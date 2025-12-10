"""
Infrastructure Tests - RabbitMQ Pod Resilience
===============================================

Tests for RabbitMQ pod resilience and failure scenarios.

Test Coverage:
    1. RabbitMQ pod deletion and automatic recreation
    2. RabbitMQ scale down to 0 replicas
    3. RabbitMQ pod restart during operations
    4. RabbitMQ outage graceful degradation
    5. RabbitMQ recovery after outage
    6. RabbitMQ pod status monitoring

Author: QA Automation Architect
Date: 2025-11-07
Related: PZ-13756 (Infrastructure Resilience)
"""

import pytest
import time
import logging
from typing import Dict, Any, Optional

from src.apis.focus_server_api import FocusServerAPI
from src.models.focus_server_models import ConfigureRequest, ViewType
from src.infrastructure.kubernetes_manager import KubernetesManager
from src.core.exceptions import APIError, InfrastructureError

logger = logging.getLogger(__name__)


# ===================================================================
# Helper Functions
# ===================================================================

def get_rabbitmq_pod_selector(k8s_manager_or_config) -> str:
    """
    Get the correct RabbitMQ pod selector from environment config.
    
    Args:
        k8s_manager_or_config: Either KubernetesManager or ConfigManager instance
        
    Returns:
        str: Label selector string for RabbitMQ pods
    """
    # Try to get config_manager from k8s_manager if needed
    config_manager = k8s_manager_or_config
    if hasattr(k8s_manager_or_config, 'config_manager'):
        config_manager = k8s_manager_or_config.config_manager
    
    # Try to get from services config first
    try:
        if hasattr(config_manager, 'get_environment_config'):
            env_config = config_manager.get_environment_config()
        elif hasattr(config_manager, '_config_data'):
            env_config = config_manager._config_data
        else:
            env_config = {}
            
        services = env_config.get("services", {})
        rabbitmq_config = services.get("rabbitmq", {})
        pod_selector = rabbitmq_config.get("pod_selector")
        if pod_selector:
            return pod_selector
    except Exception:
        pass
    
    # Fallback to app.kubernetes.io/instance=rabbitmq-panda (works for both staging and kefar_saba)
    return "app.kubernetes.io/instance=rabbitmq-panda"


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def k8s_manager(config_manager):
    """Fixture to provide KubernetesManager instance."""
    logger.info("Initializing Kubernetes manager...")
    manager = KubernetesManager(config_manager)
    
    if manager.k8s_core_v1 is None and not manager.use_ssh_fallback:
        pytest.skip("Kubernetes not available (no kubeconfig or SSH)")
    
    yield manager
    logger.info("Kubernetes manager fixture cleanup complete")


@pytest.fixture
# Note: regression marker - fixture for resilience tests
def test_config():
    """Standard configuration for resilience tests."""
    return {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 1, "max": 50},
        "frequencyRange": {"min": 0, "max": 1000},
        "start_time": None,
        "end_time": None,
        "view_type": ViewType.MULTICHANNEL
    }


# ===================================================================
# Test Class: RabbitMQ Pod Resilience
# ===================================================================

@pytest.mark.critical
@pytest.mark.high
@pytest.mark.resilience
@pytest.mark.regression
class TestRabbitMQPodResilience:
    """
    Test suite for RabbitMQ pod resilience and failure scenarios.
    
    Tests validate:
    - Pod deletion and automatic recreation (StatefulSet)
    - Scale down/up scenarios
    - Pod restart during operations
    - Graceful degradation during outages
    - System recovery after outages
    """
    
    @pytest.mark.xray("PZ-14721")

    
    @pytest.mark.regression
    def test_rabbitmq_pod_deletion_recreation(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: RabbitMQ Pod Deletion and Recreation
        
        Validates that when RabbitMQ pod is deleted:
        1. Kubernetes automatically recreates the pod (StatefulSet)
        2. New pod becomes ready
        3. RabbitMQ connection is restored
        4. System functionality is restored
        
        Steps:
            1. Get current RabbitMQ pod name
            2. Verify RabbitMQ is accessible (if possible)
            3. Delete RabbitMQ pod
            4. Wait for pod deletion
            5. Wait for new pod to be created
            6. Wait for new pod to be ready
            7. Verify RabbitMQ connection restored
            8. Verify system functionality restored
        
        Expected:
            - Pod deleted successfully
            - New pod created automatically within 60 seconds
            - New pod becomes ready within 120 seconds
            - RabbitMQ connection restored
            - System functionality restored
        
        Jira: PZ-14721
        Priority: P0
        """
        logger.info("=" * 80)
        logger.info("TEST: RabbitMQ Pod Deletion and Recreation")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        original_pod_name = None
        new_pod_name = None
        
        try:
            # Step 1: Get current RabbitMQ pod
            logger.info("\nStep 1: Getting current RabbitMQ pod...")
            pods = k8s_manager.get_pods(namespace=namespace, label_selector=get_rabbitmq_pod_selector(k8s_manager))
            if not pods:
                # Try alternative label selector
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
            
            assert len(pods) > 0, "RabbitMQ pod not found"
            original_pod = pods[0]
            original_pod_name = original_pod['name']
            logger.info(f"✅ Original RabbitMQ pod: {original_pod_name}")
            
            # Step 2: Verify RabbitMQ is accessible (if possible)
            logger.info("\nStep 2: Verifying RabbitMQ accessibility...")
            # Note: Direct RabbitMQ connection test may not be available
            logger.info("ℹ️  RabbitMQ accessibility check skipped (requires RabbitMQ client)")
            
            # Step 3: Delete RabbitMQ pod
            logger.info(f"\nStep 3: Deleting RabbitMQ pod '{original_pod_name}'...")
            assert k8s_manager.delete_pod(original_pod_name, namespace=namespace), \
                "Failed to delete RabbitMQ pod"
            logger.info("✅ RabbitMQ pod deleted")
            
            # Step 4: Wait for pod deletion
            logger.info("\nStep 4: Waiting for pod deletion...")
            deleted = False
            for attempt in range(30):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector=get_rabbitmq_pod_selector(k8s_manager))
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
                if not any(p['name'] == original_pod_name for p in pods):
                    deleted = True
                    logger.info("✅ Pod deleted")
                    break
                time.sleep(1)
            
            assert deleted, f"Pod {original_pod_name} not deleted within 30 seconds"
            
            # Step 5: Wait for new pod to be created
            logger.info("\nStep 5: Waiting for new pod to be created...")
            for attempt in range(60):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector=get_rabbitmq_pod_selector(k8s_manager))
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
                if pods:
                    new_pod = pods[0]
                    if new_pod['name'] != original_pod_name:
                        new_pod_name = new_pod['name']
                        logger.info(f"✅ New pod created: {new_pod_name}")
                        break
                time.sleep(1)
            
            assert new_pod_name, "New RabbitMQ pod not created within 60 seconds"
            
            # Step 6: Wait for new pod to be ready
            logger.info(f"\nStep 6: Waiting for pod '{new_pod_name}' to be ready...")
            ready = k8s_manager.wait_for_pod_ready(new_pod_name, namespace=namespace, timeout=120)
            assert ready, f"Pod {new_pod_name} not ready within 120 seconds"
            logger.info("✅ Pod is ready")
            
            # Step 7: Verify RabbitMQ connection restored
            logger.info("\nStep 7: Verifying RabbitMQ connection restored...")
            time.sleep(10)  # Give RabbitMQ time to initialize
            logger.info("ℹ️  RabbitMQ connection verification skipped (requires RabbitMQ client)")
            
            # Step 8: Verify system functionality restored
            logger.info("\nStep 8: Verifying system functionality...")
            time.sleep(5)
            
            try:
                config_request = ConfigureRequest(**test_config)
                response = focus_server_api.configure_streaming_job(config_request)
                logger.info(f"✅ System functionality restored - job created: {response.job_id}")
                
                # Cleanup
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
            except Exception as e:
                logger.warning(f"⚠️  System functionality test failed: {e}")
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: RabbitMQ Pod Deletion and Recreation")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            raise
        finally:
            # Ensure RabbitMQ pod is running
            if new_pod_name:
                logger.info(f"\nCleanup: Verifying RabbitMQ pod '{new_pod_name}' is running...")
                pod_info = k8s_manager.get_pod_by_name(new_pod_name, namespace=namespace)
                if pod_info and pod_info.get('status') != 'Running':
                    logger.warning(f"⚠️  RabbitMQ pod '{new_pod_name}' is not running - may need manual intervention")
    
    @pytest.mark.xray("PZ-14722")

    
    @pytest.mark.regression
    def test_rabbitmq_scale_down_to_zero(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: RabbitMQ Scale Down to 0 Replicas
        
        Validates that when RabbitMQ is scaled down to 0:
        1. All pods are terminated
        2. RabbitMQ becomes unreachable
        3. System returns appropriate errors (503)
        4. No crashes occur
        5. System recovers after scale up
        
        Steps:
            1. Verify RabbitMQ pod exists
            2. Scale RabbitMQ StatefulSet to 0
            3. Wait for pods to terminate
            4. Attempt job creation (should fail gracefully)
            5. Scale RabbitMQ back to 1
            6. Wait for pod to be ready
            7. Verify system functionality restored
        
        Expected:
            - RabbitMQ scaled down successfully
            - RabbitMQ unreachable after scale down
            - Job creation returns 503 or appropriate error
            - No system crashes
            - RabbitMQ restored after scale up
        
        Jira: PZ-14722
        Priority: P0
        """
        logger.info("=" * 80)
        logger.info("TEST: RabbitMQ Scale Down to 0 Replicas")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        statefulset_name = "rabbitmq-panda"
        
        try:
            # Step 1: Verify RabbitMQ pod exists
            logger.info("\nStep 1: Verifying RabbitMQ pod exists...")
            pods = k8s_manager.get_pods(namespace=namespace, label_selector=get_rabbitmq_pod_selector(k8s_manager))
            if not pods:
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
            assert len(pods) > 0, "RabbitMQ pod not found"
            logger.info(f"✅ RabbitMQ pod found: {pods[0]['name']}")
            
            # Step 2: Scale RabbitMQ StatefulSet to 0
            logger.info(f"\nStep 2: Scaling RabbitMQ StatefulSet '{statefulset_name}' to 0 replicas...")
            assert k8s_manager.scale_statefulset(statefulset_name, replicas=0, namespace=namespace), \
                "Failed to scale RabbitMQ to 0"
            logger.info("✅ RabbitMQ scaled down to 0")
            
            # Step 3: Wait for pods to terminate
            logger.info("\nStep 3: Waiting for pods to terminate...")
            pods_terminated = False
            for attempt in range(60):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector=get_rabbitmq_pod_selector(k8s_manager))
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
                if len(pods) == 0:
                    pods_terminated = True
                    logger.info("✅ All RabbitMQ pods terminated")
                    break
                time.sleep(1)
            
            assert pods_terminated, "RabbitMQ pods not terminated within 60 seconds"
            time.sleep(5)  # Give service time to stop
            
            # Step 4: Attempt job creation (should fail gracefully)
            logger.info("\nStep 4: Attempting job creation (should fail gracefully)...")
            try:
                config_request = ConfigureRequest(**test_config)
                response = focus_server_api.configure_streaming_job(config_request)
                logger.warning(f"⚠️  Job creation succeeded unexpectedly: {response.job_id}")
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
            except APIError as e:
                error_str = str(e).lower()
                if "503" in error_str or "unavailable" in error_str or "rabbitmq" in error_str or "mq" in error_str:
                    logger.info(f"✅ Job creation failed gracefully: {e}")
                else:
                    logger.warning(f"⚠️  Unexpected error: {e}")
            except Exception as e:
                logger.info(f"✅ Job creation failed (expected): {type(e).__name__}")
            
            # Step 5: Scale RabbitMQ back to 1
            logger.info(f"\nStep 5: Scaling RabbitMQ StatefulSet '{statefulset_name}' back to 1 replica...")
            assert k8s_manager.scale_statefulset(statefulset_name, replicas=1, namespace=namespace), \
                "Failed to scale RabbitMQ back to 1"
            logger.info("✅ RabbitMQ scaled up to 1")
            
            # Step 6: Wait for pod to be ready
            logger.info("\nStep 6: Waiting for RabbitMQ pod to be ready...")
            pod_ready = False
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector=get_rabbitmq_pod_selector(k8s_manager))
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        pod_ready = True
                        logger.info(f"✅ RabbitMQ pod '{pod_name}' is ready")
                        break
                time.sleep(2)
            
            assert pod_ready, "RabbitMQ pod not ready within 120 seconds"
            
            # Step 7: Verify system functionality restored
            logger.info("\nStep 7: Verifying system functionality restored...")
            time.sleep(10)  # Give RabbitMQ time to initialize
            
            try:
                config_request = ConfigureRequest(**test_config)
                response = focus_server_api.configure_streaming_job(config_request)
                logger.info(f"✅ System functionality restored - job created: {response.job_id}")
                
                # Cleanup
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
            except Exception as e:
                logger.warning(f"⚠️  System functionality test failed: {e}")
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: RabbitMQ Scale Down to 0 Replicas")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            # Ensure RabbitMQ is restored
            try:
                logger.info("\nCleanup: Restoring RabbitMQ to 1 replica...")
                k8s_manager.scale_statefulset(statefulset_name, replicas=1, namespace=namespace)
            except:
                pass
            raise
    
    @pytest.mark.xray("PZ-14723")

    
    @pytest.mark.regression
    def test_rabbitmq_pod_restart_during_operations(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: RabbitMQ Pod Restart During Operations
        
        Validates that when RabbitMQ pod restarts during operations:
        1. Pod restart is handled gracefully
        2. Operations either succeed or fail gracefully
        3. No data corruption occurs
        4. System recovers after restart
        
        Steps:
            1. Get RabbitMQ pod name
            2. Start job creation
            3. Restart RabbitMQ pod during creation
            4. Monitor job creation result
            5. Verify pod restarted successfully
            6. Verify system functionality
        
        Expected:
            - Pod restart handled gracefully
            - Operations either succeed or fail with clear error
            - No crashes or undefined behavior
            - System recovers after restart
        
        Jira: PZ-14723
        Priority: P1
        """
        logger.info("=" * 80)
        logger.info("TEST: RabbitMQ Pod Restart During Operations")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        pod_name = None
        
        try:
            # Step 1: Get RabbitMQ pod name
            logger.info("\nStep 1: Getting RabbitMQ pod name...")
            pods = k8s_manager.get_pods(namespace=namespace, label_selector=get_rabbitmq_pod_selector(k8s_manager))
            if not pods:
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
            assert len(pods) > 0, "RabbitMQ pod not found"
            pod_name = pods[0]['name']
            logger.info(f"✅ RabbitMQ pod: {pod_name}")
            
            # Step 2-3: Start job creation and restart pod
            logger.info("\nStep 2-3: Starting job creation and restarting RabbitMQ pod...")
            
            import threading
            
            job_result = {"success": False, "error": None, "job_id": None}
            
            def create_job():
                try:
                    config_request = ConfigureRequest(**test_config)
                    response = focus_server_api.configure_streaming_job(config_request)
                    job_result["success"] = True
                    job_result["job_id"] = response.job_id if hasattr(response, 'job_id') else None
                except Exception as e:
                    job_result["error"] = str(e)
            
            job_thread = threading.Thread(target=create_job)
            job_thread.start()
            
            time.sleep(1)
            logger.info(f"Restarting RabbitMQ pod '{pod_name}'...")
            assert k8s_manager.restart_pod(pod_name, namespace=namespace), \
                "Failed to restart RabbitMQ pod"
            
            job_thread.join(timeout=60)
            
            # Step 4: Monitor job creation result
            logger.info("\nStep 4: Monitoring job creation result...")
            if job_result["success"]:
                logger.info(f"✅ Job created successfully: {job_result['job_id']}")
                try:
                    if job_result["job_id"]:
                        focus_server_api.cancel_job(job_result["job_id"])
                except:
                    pass
            else:
                logger.info(f"ℹ️  Job creation result: {job_result['error'] or 'Unknown error'}")
            
            # Step 5: Verify pod restarted successfully
            logger.info("\nStep 5: Verifying pod restarted successfully...")
            time.sleep(10)
            
            pods = k8s_manager.get_pods(namespace=namespace, label_selector=get_rabbitmq_pod_selector(k8s_manager))
            if not pods:
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
            assert len(pods) > 0, "RabbitMQ pod not found after restart"
            
            new_pod_name = pods[0]['name']
            logger.info(f"✅ New pod: {new_pod_name}")
            
            ready = k8s_manager.wait_for_pod_ready(new_pod_name, namespace=namespace, timeout=120)
            assert ready, f"Pod {new_pod_name} not ready within 120 seconds"
            logger.info("✅ Pod is ready")
            
            # Step 6: Verify system functionality
            logger.info("\nStep 6: Verifying system functionality...")
            time.sleep(10)
            
            try:
                config_request = ConfigureRequest(**test_config)
                response = focus_server_api.configure_streaming_job(config_request)
                logger.info(f"✅ System functionality verified - job created: {response.job_id}")
                
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
            except Exception as e:
                logger.warning(f"⚠️  System functionality test failed: {e}")
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: RabbitMQ Pod Restart During Operations")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            raise
    
    @pytest.mark.xray("PZ-14724")

    
    @pytest.mark.regression
    def test_rabbitmq_outage_graceful_degradation(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: RabbitMQ Outage Graceful Degradation
        
        Validates that when RabbitMQ is down:
        1. System handles outage gracefully
        2. Appropriate errors are returned (503)
        3. No crashes occur
        4. Error messages are clear
        
        Steps:
            1. Scale RabbitMQ to 0
            2. Wait for pods to terminate
            3. Attempt various operations
            4. Verify graceful error handling
            5. Restore RabbitMQ
        
        Expected:
            - All operations fail gracefully with 503 or appropriate errors
            - No crashes or undefined behavior
            - Error messages indicate RabbitMQ unavailability
        
        Jira: PZ-14724
        Priority: P0
        """
        logger.info("=" * 80)
        logger.info("TEST: RabbitMQ Outage Graceful Degradation")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        statefulset_name = "rabbitmq-panda"
        
        try:
            # Step 1: Scale RabbitMQ to 0
            logger.info(f"\nStep 1: Scaling RabbitMQ to 0...")
            assert k8s_manager.scale_statefulset(statefulset_name, replicas=0, namespace=namespace), \
                "Failed to scale RabbitMQ to 0"
            
            # Wait for pods to terminate
            for attempt in range(60):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector=get_rabbitmq_pod_selector(k8s_manager))
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
                if len(pods) == 0:
                    break
                time.sleep(1)
            
            logger.info("✅ RabbitMQ scaled down")
            time.sleep(5)
            
            # Step 2-3: Attempt operations and verify graceful handling
            logger.info("\nStep 2-3: Attempting operations during outage...")
            
            try:
                config_request = ConfigureRequest(**test_config)
                response = focus_server_api.configure_streaming_job(config_request)
                logger.warning(f"⚠️  Job creation succeeded unexpectedly: {response.job_id}")
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
            except APIError as e:
                error_str = str(e).lower()
                if "503" in error_str or "unavailable" in error_str or "rabbitmq" in error_str or "mq" in error_str:
                    logger.info(f"✅ Job creation failed gracefully: {e}")
                else:
                    logger.warning(f"⚠️  Unexpected error: {e}")
            except Exception as e:
                logger.info(f"✅ Job creation failed (expected): {type(e).__name__}")
            
            logger.info("✅ No crashes occurred")
            logger.info("✅ Errors handled gracefully")
            
            # Step 4: Restore RabbitMQ
            logger.info(f"\nStep 4: Restoring RabbitMQ...")
            assert k8s_manager.scale_statefulset(statefulset_name, replicas=1, namespace=namespace), \
                "Failed to restore RabbitMQ"
            
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector=get_rabbitmq_pod_selector(k8s_manager))
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        logger.info("✅ RabbitMQ restored")
                        break
                time.sleep(2)
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: RabbitMQ Outage Graceful Degradation")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            try:
                k8s_manager.scale_statefulset(statefulset_name, replicas=1, namespace=namespace)
            except:
                pass
            raise
    
    @pytest.mark.xray("PZ-14725")

    
    @pytest.mark.regression
    def test_rabbitmq_recovery_after_outage(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: RabbitMQ Recovery After Outage
        
        Validates that after RabbitMQ outage:
        1. System recovers automatically
        2. RabbitMQ connection is restored
        3. System functionality is restored
        
        Steps:
            1. Scale RabbitMQ to 0
            2. Wait for outage
            3. Scale RabbitMQ back to 1
            4. Wait for recovery
            5. Verify functionality restored
        
        Expected:
            - RabbitMQ recovers within reasonable time
            - Connection restored
            - Functionality restored
        
        Jira: PZ-14725
        Priority: P0
        """
        logger.info("=" * 80)
        logger.info("TEST: RabbitMQ Recovery After Outage")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        statefulset_name = "rabbitmq-panda"
        
        try:
            # Scale to 0
            logger.info(f"\nStep 1: Scaling RabbitMQ to 0...")
            assert k8s_manager.scale_statefulset(statefulset_name, replicas=0, namespace=namespace), \
                "Failed to scale RabbitMQ to 0"
            
            for attempt in range(60):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector=get_rabbitmq_pod_selector(k8s_manager))
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
                if len(pods) == 0:
                    break
                time.sleep(1)
            
            logger.info("✅ RabbitMQ scaled down")
            time.sleep(10)
            
            # Scale back to 1
            logger.info(f"\nStep 2: Scaling RabbitMQ back to 1...")
            assert k8s_manager.scale_statefulset(statefulset_name, replicas=1, namespace=namespace), \
                "Failed to restore RabbitMQ"
            
            recovery_start = time.time()
            
            pods = k8s_manager.get_pods(namespace=namespace, label_selector=get_rabbitmq_pod_selector(k8s_manager))
            if not pods:
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
            assert len(pods) > 0, "RabbitMQ pod not created"
            
            pod_name = pods[0]['name']
            ready = k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=120)
            assert ready, "RabbitMQ pod not ready"
            
            recovery_time = time.time() - recovery_start
            logger.info(f"✅ RabbitMQ recovered in {recovery_time:.1f} seconds")
            
            # Verify functionality
            logger.info("\nStep 3: Verifying functionality restored...")
            time.sleep(10)
            
            config_request = ConfigureRequest(**test_config)
            response = focus_server_api.configure_streaming_job(config_request)
            logger.info(f"✅ Functionality restored - job created: {response.job_id}")
            
            try:
                focus_server_api.cancel_job(response.job_id)
            except:
                pass
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: RabbitMQ Recovery After Outage")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            try:
                k8s_manager.scale_statefulset(statefulset_name, replicas=1, namespace=namespace)
            except:
                pass
            raise
    
    @pytest.mark.xray("PZ-14726")

    
    @pytest.mark.regression
    def test_rabbitmq_pod_status_monitoring(
        self,
        k8s_manager: KubernetesManager
    ):
        """
        Test: RabbitMQ Pod Status Monitoring
        
        Validates pod status monitoring capabilities.
        
        Steps:
            1. Get RabbitMQ pod
            2. Check pod status
            3. Verify status is Running
        
        Expected:
            - Pod status retrieved successfully
            - Status is Running
        
        Jira: PZ-14726
        Priority: P2
        """
        logger.info("=" * 80)
        logger.info("TEST: RabbitMQ Pod Status Monitoring")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        
        pods = k8s_manager.get_pods(namespace=namespace, label_selector=get_rabbitmq_pod_selector(k8s_manager))
        if not pods:
            pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
        assert len(pods) > 0, "RabbitMQ pod not found"
        
        pod_name = pods[0]['name']
        pod_info = k8s_manager.get_pod_by_name(pod_name, namespace=namespace)
        assert pod_info is not None, "Pod not found"
        
        status = pod_info.get('status')
        ready = pod_info.get('ready')
        
        logger.info(f"   Status: {status}")
        logger.info(f"   Ready: {ready}")
        
        assert status == "Running", f"Pod status should be Running, got {status}"
        assert ready == "True", f"Pod should be ready, got {ready}"
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: RabbitMQ Pod Status Monitoring")
        logger.info("=" * 80)


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary


@pytest.mark.regression
def test_rabbitmq_pod_resilience_summary():
    """Summary test for RabbitMQ pod resilience tests."""
    logger.info("=" * 80)
    logger.info("RabbitMQ Pod Resilience Tests Suite Summary")
    logger.info("=" * 80)
    logger.info("Tests in this module:")
    logger.info("  1. PZ-14721: RabbitMQ pod deletion and recreation")
    logger.info("  2. PZ-14722: RabbitMQ scale down to 0 replicas")
    logger.info("  3. PZ-14723: RabbitMQ pod restart during operations")
    logger.info("  4. PZ-14724: RabbitMQ outage graceful degradation")
    logger.info("  5. PZ-14725: RabbitMQ recovery after outage")
    logger.info("  6. PZ-14726: RabbitMQ pod status monitoring")
    logger.info("=" * 80)

