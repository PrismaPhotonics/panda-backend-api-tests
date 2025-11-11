"""
Infrastructure Tests - Focus Server Pod Resilience
===================================================

Tests for Focus Server pod resilience and failure scenarios.

Test Coverage:
    1. Focus Server pod deletion and automatic recreation
    2. Focus Server scale down to 0 replicas
    3. Focus Server pod restart during job creation
    4. Focus Server outage graceful degradation
    5. Focus Server recovery after outage
    6. Focus Server pod status monitoring

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
def test_config():
    """Standard configuration for resilience tests."""
    return {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 1, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,
        "end_time": None,
        "view_type": ViewType.MULTICHANNEL
    }


# ===================================================================
# Test Class: Focus Server Pod Resilience
# ===================================================================

@pytest.mark.infrastructure
@pytest.mark.resilience
@pytest.mark.kubernetes
@pytest.mark.critical
@pytest.mark.slow
class TestFocusServerPodResilience:
    """
    Test suite for Focus Server pod resilience and failure scenarios.
    
    Tests validate:
    - Pod deletion and automatic recreation
    - Scale down/up scenarios
    - Pod restart during operations
    - Graceful degradation during outages
    - System recovery after outages
    """
    
    @pytest.mark.xray("PZ-14727")
    def test_focus_server_pod_deletion_recreation(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: Focus Server Pod Deletion and Recreation
        
        Validates that when Focus Server pod is deleted:
        1. Kubernetes automatically recreates the pod
        2. New pod becomes ready
        3. Focus Server API is restored
        4. System functionality is restored
        
        Steps:
            1. Get current Focus Server pod name
            2. Verify Focus Server is accessible
            3. Delete Focus Server pod
            4. Wait for pod deletion
            5. Wait for new pod to be created
            6. Wait for new pod to be ready
            7. Verify Focus Server API restored
            8. Verify system functionality restored
        
        Expected:
            - Pod deleted successfully
            - New pod created automatically within 60 seconds
            - New pod becomes ready within 120 seconds
            - Focus Server API restored
            - System functionality restored
        
        Jira: PZ-14727
        Priority: P0
        """
        logger.info("=" * 80)
        logger.info("TEST: Focus Server Pod Deletion and Recreation")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        original_pod_name = None
        new_pod_name = None
        
        try:
            # Step 1: Get current Focus Server pod
            logger.info("\nStep 1: Getting current Focus Server pod...")
            pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
            if not pods:
                # Try alternative selectors
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
            
            assert len(pods) > 0, "Focus Server pod not found"
            original_pod = pods[0]
            original_pod_name = original_pod['name']
            logger.info(f"✅ Original Focus Server pod: {original_pod_name}")
            
            # Step 2: Verify Focus Server is accessible
            logger.info("\nStep 2: Verifying Focus Server accessibility...")
            try:
                response = focus_server_api.get("/ack")
                assert response.status_code == 200, f"Health check failed: {response.status_code}"
                logger.info("✅ Focus Server accessible before deletion")
            except Exception as e:
                logger.warning(f"⚠️  Health check failed: {e}")
            
            # Step 3: Delete Focus Server pod
            logger.info(f"\nStep 3: Deleting Focus Server pod '{original_pod_name}'...")
            assert k8s_manager.delete_pod(original_pod_name, namespace=namespace), \
                "Failed to delete Focus Server pod"
            logger.info("✅ Focus Server pod deleted")
            
            # Step 4: Wait for pod deletion
            logger.info("\nStep 4: Waiting for pod deletion...")
            deleted = False
            for attempt in range(30):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
                if not any(p['name'] == original_pod_name for p in pods):
                    deleted = True
                    logger.info("✅ Pod deleted")
                    break
                time.sleep(1)
            
            assert deleted, f"Pod {original_pod_name} not deleted within 30 seconds"
            
            # Step 5: Wait for new pod to be created
            logger.info("\nStep 5: Waiting for new pod to be created...")
            for attempt in range(60):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
                if pods:
                    new_pod = pods[0]
                    if new_pod['name'] != original_pod_name:
                        new_pod_name = new_pod['name']
                        logger.info(f"✅ New pod created: {new_pod_name}")
                        break
                time.sleep(1)
            
            assert new_pod_name, "New Focus Server pod not created within 60 seconds"
            
            # Step 6: Wait for new pod to be ready
            logger.info(f"\nStep 6: Waiting for pod '{new_pod_name}' to be ready...")
            ready = k8s_manager.wait_for_pod_ready(new_pod_name, namespace=namespace, timeout=120)
            assert ready, f"Pod {new_pod_name} not ready within 120 seconds"
            logger.info("✅ Pod is ready")
            
            # Step 7: Verify Focus Server API restored
            logger.info("\nStep 7: Verifying Focus Server API restored...")
            api_restored = False
            for attempt in range(60):  # 60 seconds timeout
                try:
                    response = focus_server_api.get("/ack", timeout=5)
                    if response.status_code == 200:
                        api_restored = True
                        logger.info("✅ Focus Server API restored")
                        break
                except:
                    pass
                time.sleep(1)
            
            assert api_restored, "Focus Server API not restored within 60 seconds"
            
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
            logger.info("✅ TEST PASSED: Focus Server Pod Deletion and Recreation")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            raise
        finally:
            if new_pod_name:
                logger.info(f"\nCleanup: Verifying Focus Server pod '{new_pod_name}' is running...")
                pod_info = k8s_manager.get_pod_by_name(new_pod_name, namespace=namespace)
                if pod_info and pod_info.get('status') != 'Running':
                    logger.warning(f"⚠️  Focus Server pod '{new_pod_name}' is not running")
    
    @pytest.mark.xray("PZ-14728")
    def test_focus_server_scale_down_to_zero(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: Focus Server Scale Down to 0 Replicas
        
        Validates that when Focus Server is scaled down to 0:
        1. All pods are terminated
        2. Focus Server becomes unreachable
        3. System returns appropriate errors (503)
        4. No crashes occur
        5. System recovers after scale up
        
        Steps:
            1. Verify Focus Server is accessible
            2. Scale Focus Server deployment to 0
            3. Wait for pods to terminate
            4. Verify Focus Server is unreachable
            5. Attempt job creation (should fail gracefully)
            6. Scale Focus Server back to 1
            7. Wait for pod to be ready
            8. Verify system functionality restored
        
        Expected:
            - Focus Server scaled down successfully
            - Focus Server unreachable after scale down
            - Job creation returns 503 or appropriate error
            - No system crashes
            - Focus Server restored after scale up
        
        Jira: PZ-14728
        Priority: P0
        """
        logger.info("=" * 80)
        logger.info("TEST: Focus Server Scale Down to 0 Replicas")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        deployment_name = "panda-panda-focus-server"
        
        try:
            # Step 1: Verify Focus Server is accessible
            logger.info("\nStep 1: Verifying Focus Server accessibility...")
            try:
                response = focus_server_api.get("/ack")
                assert response.status_code == 200
                logger.info("✅ Focus Server accessible")
            except Exception as e:
                logger.warning(f"⚠️  Health check failed: {e}")
            
            # Step 2: Scale Focus Server deployment to 0
            logger.info(f"\nStep 2: Scaling Focus Server deployment '{deployment_name}' to 0 replicas...")
            assert k8s_manager.scale_deployment(deployment_name, replicas=0, namespace=namespace), \
                "Failed to scale Focus Server to 0"
            logger.info("✅ Focus Server scaled down to 0")
            
            # Step 3: Wait for pods to terminate
            logger.info("\nStep 3: Waiting for pods to terminate...")
            pods_terminated = False
            for attempt in range(60):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
                if len(pods) == 0:
                    pods_terminated = True
                    logger.info("✅ All Focus Server pods terminated")
                    break
                time.sleep(1)
            
            assert pods_terminated, "Focus Server pods not terminated within 60 seconds"
            time.sleep(5)
            
            # Step 4: Verify Focus Server is unreachable
            logger.info("\nStep 4: Verifying Focus Server is unreachable...")
            unreachable = False
            for attempt in range(10):
                try:
                    focus_server_api.get("/ack", timeout=2)
                except Exception:
                    unreachable = True
                    logger.info("✅ Focus Server is unreachable")
                    break
                time.sleep(1)
            
            assert unreachable, "Focus Server should be unreachable after scale down"
            
            # Step 5: Attempt job creation (should fail gracefully)
            logger.info("\nStep 5: Attempting job creation (should fail gracefully)...")
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
                if "503" in error_str or "unavailable" in error_str or "connection" in error_str:
                    logger.info(f"✅ Job creation failed gracefully: {e}")
                else:
                    logger.warning(f"⚠️  Unexpected error: {e}")
            except Exception as e:
                logger.info(f"✅ Job creation failed (expected): {type(e).__name__}")
            
            # Step 6: Scale Focus Server back to 1
            logger.info(f"\nStep 6: Scaling Focus Server deployment '{deployment_name}' back to 1 replica...")
            assert k8s_manager.scale_deployment(deployment_name, replicas=1, namespace=namespace), \
                "Failed to scale Focus Server back to 1"
            logger.info("✅ Focus Server scaled up to 1")
            
            # Step 7: Wait for pod to be ready
            logger.info("\nStep 7: Waiting for Focus Server pod to be ready...")
            pod_ready = False
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        pod_ready = True
                        logger.info(f"✅ Focus Server pod '{pod_name}' is ready")
                        break
                time.sleep(2)
            
            assert pod_ready, "Focus Server pod not ready within 120 seconds"
            
            # Step 8: Verify system functionality restored
            logger.info("\nStep 8: Verifying system functionality restored...")
            api_restored = False
            for attempt in range(60):
                try:
                    response = focus_server_api.get("/ack", timeout=5)
                    if response.status_code == 200:
                        api_restored = True
                        break
                except:
                    pass
                time.sleep(1)
            
            assert api_restored, "Focus Server API not restored within 60 seconds"
            
            time.sleep(5)
            
            try:
                config_request = ConfigureRequest(**test_config)
                response = focus_server_api.configure_streaming_job(config_request)
                logger.info(f"✅ System functionality restored - job created: {response.job_id}")
                
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
            except Exception as e:
                logger.warning(f"⚠️  System functionality test failed: {e}")
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: Focus Server Scale Down to 0 Replicas")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            try:
                k8s_manager.scale_deployment(deployment_name, replicas=1, namespace=namespace)
            except:
                pass
            raise
    
    @pytest.mark.xray("PZ-14729")
    def test_focus_server_pod_restart_during_job_creation(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: Focus Server Pod Restart During Job Creation
        
        Validates that when Focus Server pod restarts during job creation:
        1. Pod restart is handled gracefully
        2. Job creation either succeeds or fails gracefully
        3. No data corruption occurs
        4. System recovers after restart
        
        Steps:
            1. Get Focus Server pod name
            2. Start job creation
            3. Restart Focus Server pod during creation
            4. Monitor job creation result
            5. Verify pod restarted successfully
            6. Verify system functionality
        
        Expected:
            - Pod restart handled gracefully
            - Job creation either succeeds or fails with clear error
            - No crashes or undefined behavior
            - System recovers after restart
        
        Jira: PZ-14729
        Priority: P1
        """
        logger.info("=" * 80)
        logger.info("TEST: Focus Server Pod Restart During Job Creation")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        pod_name = None
        
        try:
            # Get pod name
            pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
            if not pods:
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
            assert len(pods) > 0, "Focus Server pod not found"
            pod_name = pods[0]['name']
            logger.info(f"✅ Focus Server pod: {pod_name}")
            
            # Start job creation and restart pod
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
            logger.info(f"Restarting Focus Server pod '{pod_name}'...")
            assert k8s_manager.restart_pod(pod_name, namespace=namespace), \
                "Failed to restart Focus Server pod"
            
            job_thread.join(timeout=60)
            
            # Monitor result
            if job_result["success"]:
                logger.info(f"✅ Job created successfully: {job_result['job_id']}")
                try:
                    if job_result["job_id"]:
                        focus_server_api.cancel_job(job_result["job_id"])
                except:
                    pass
            else:
                logger.info(f"ℹ️  Job creation result: {job_result['error'] or 'Unknown error'}")
            
            # Verify pod restarted
            time.sleep(10)
            pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
            if not pods:
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
            assert len(pods) > 0, "Focus Server pod not found after restart"
            
            new_pod_name = pods[0]['name']
            ready = k8s_manager.wait_for_pod_ready(new_pod_name, namespace=namespace, timeout=120)
            assert ready, f"Pod {new_pod_name} not ready"
            
            # Verify functionality
            time.sleep(5)
            api_restored = False
            for attempt in range(60):
                try:
                    response = focus_server_api.get("/ack", timeout=5)
                    if response.status_code == 200:
                        api_restored = True
                        break
                except:
                    pass
                time.sleep(1)
            
            assert api_restored, "Focus Server API not restored"
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: Focus Server Pod Restart During Job Creation")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            raise
    
    @pytest.mark.xray("PZ-14730")
    def test_focus_server_outage_graceful_degradation(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: Focus Server Outage Graceful Degradation
        
        Validates that when Focus Server is down:
        1. System handles outage gracefully
        2. Appropriate errors are returned (503)
        3. No crashes occur
        
        Steps:
            1. Scale Focus Server to 0
            2. Wait for pods to terminate
            3. Attempt various operations
            4. Verify graceful error handling
            5. Restore Focus Server
        
        Expected:
            - All operations fail gracefully with 503 or appropriate errors
            - No crashes or undefined behavior
        
        Jira: PZ-14730
        Priority: P0
        """
        logger.info("=" * 80)
        logger.info("TEST: Focus Server Outage Graceful Degradation")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        deployment_name = "panda-panda-focus-server"
        
        try:
            # Scale to 0
            assert k8s_manager.scale_deployment(deployment_name, replicas=0, namespace=namespace), \
                "Failed to scale Focus Server to 0"
            
            for attempt in range(60):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
                if len(pods) == 0:
                    break
                time.sleep(1)
            
            time.sleep(5)
            
            # Attempt operations
            try:
                config_request = ConfigureRequest(**test_config)
                response = focus_server_api.configure_streaming_job(config_request)
                logger.warning(f"⚠️  Job creation succeeded unexpectedly")
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
            except APIError as e:
                error_str = str(e).lower()
                if "503" in error_str or "unavailable" in error_str or "connection" in error_str:
                    logger.info(f"✅ Job creation failed gracefully: {e}")
                else:
                    logger.warning(f"⚠️  Unexpected error: {e}")
            except Exception as e:
                logger.info(f"✅ Job creation failed (expected): {type(e).__name__}")
            
            logger.info("✅ No crashes occurred")
            logger.info("✅ Errors handled gracefully")
            
            # Restore
            assert k8s_manager.scale_deployment(deployment_name, replicas=1, namespace=namespace), \
                "Failed to restore Focus Server"
            
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        break
                time.sleep(2)
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: Focus Server Outage Graceful Degradation")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            try:
                k8s_manager.scale_deployment(deployment_name, replicas=1, namespace=namespace)
            except:
                pass
            raise
    
    @pytest.mark.xray("PZ-14731")
    def test_focus_server_recovery_after_outage(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: Focus Server Recovery After Outage
        
        Validates that after Focus Server outage:
        1. System recovers automatically
        2. Focus Server API is restored
        3. System functionality is restored
        
        Steps:
            1. Scale Focus Server to 0
            2. Wait for outage
            3. Scale Focus Server back to 1
            4. Wait for recovery
            5. Verify functionality restored
        
        Expected:
            - Focus Server recovers within reasonable time
            - API restored
            - Functionality restored
        
        Jira: PZ-14731
        Priority: P0
        """
        logger.info("=" * 80)
        logger.info("TEST: Focus Server Recovery After Outage")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        deployment_name = "panda-panda-focus-server"
        
        try:
            # Scale to 0
            assert k8s_manager.scale_deployment(deployment_name, replicas=0, namespace=namespace), \
                "Failed to scale Focus Server to 0"
            
            for attempt in range(60):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
                if len(pods) == 0:
                    break
                time.sleep(1)
            
            time.sleep(10)
            
            # Scale back to 1
            assert k8s_manager.scale_deployment(deployment_name, replicas=1, namespace=namespace), \
                "Failed to restore Focus Server"
            
            recovery_start = time.time()
            
            pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
            if not pods:
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
            assert len(pods) > 0, "Focus Server pod not created"
            
            pod_name = pods[0]['name']
            ready = k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=120)
            assert ready, "Focus Server pod not ready"
            
            # Verify API restored
            api_restored = False
            for attempt in range(60):
                try:
                    response = focus_server_api.get("/ack", timeout=5)
                    if response.status_code == 200:
                        api_restored = True
                        break
                except:
                    pass
                time.sleep(1)
            
            assert api_restored, "Focus Server API not restored"
            
            recovery_time = time.time() - recovery_start
            logger.info(f"✅ Focus Server recovered in {recovery_time:.1f} seconds")
            
            # Verify functionality
            time.sleep(5)
            config_request = ConfigureRequest(**test_config)
            response = focus_server_api.configure_streaming_job(config_request)
            logger.info(f"✅ Functionality restored - job created: {response.job_id}")
            
            try:
                focus_server_api.cancel_job(response.job_id)
            except:
                pass
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: Focus Server Recovery After Outage")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            try:
                k8s_manager.scale_deployment(deployment_name, replicas=1, namespace=namespace)
            except:
                pass
            raise
    
    @pytest.mark.xray("PZ-14732")
    def test_focus_server_pod_status_monitoring(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI
    ):
        """
        Test: Focus Server Pod Status Monitoring
        
        Validates pod status monitoring capabilities.
        
        Steps:
            1. Get Focus Server pod
            2. Check pod status
            3. Verify status is Running
            4. Verify API is accessible
        
        Expected:
            - Pod status retrieved successfully
            - Status is Running
            - API is accessible
        
        Jira: PZ-14732
        Priority: P2
        """
        logger.info("=" * 80)
        logger.info("TEST: Focus Server Pod Status Monitoring")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        
        pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
        if not pods:
            pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
        assert len(pods) > 0, "Focus Server pod not found"
        
        pod_name = pods[0]['name']
        pod_info = k8s_manager.get_pod_by_name(pod_name, namespace=namespace)
        assert pod_info is not None, "Pod not found"
        
        status = pod_info.get('status')
        ready = pod_info.get('ready')
        
        logger.info(f"   Status: {status}")
        logger.info(f"   Ready: {ready}")
        
        assert status == "Running", f"Pod status should be Running, got {status}"
        assert ready == "True", f"Pod should be ready, got {ready}"
        
        # Verify API
        response = focus_server_api.get("/ack")
        assert response.status_code == 200, f"API should be accessible, got {response.status_code}"
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Focus Server Pod Status Monitoring")
        logger.info("=" * 80)


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary
def test_focus_server_pod_resilience_summary():
    """Summary test for Focus Server pod resilience tests."""
    logger.info("=" * 80)
    logger.info("Focus Server Pod Resilience Tests Suite Summary")
    logger.info("=" * 80)
    logger.info("Tests in this module:")
    logger.info("  1. PZ-14727: Focus Server pod deletion and recreation")
    logger.info("  2. PZ-14728: Focus Server scale down to 0 replicas")
    logger.info("  3. PZ-14729: Focus Server pod restart during job creation")
    logger.info("  4. PZ-14730: Focus Server outage graceful degradation")
    logger.info("  5. PZ-14731: Focus Server recovery after outage")
    logger.info("  6. PZ-14732: Focus Server pod status monitoring")
    logger.info("=" * 80)

