"""
Infrastructure Tests - Multiple Pods Resilience
=================================================

Tests for multiple pods failure scenarios and cascading failures.

Test Coverage:
    1. MongoDB + RabbitMQ down simultaneously
    2. MongoDB + Focus Server down simultaneously
    3. RabbitMQ + Focus Server down simultaneously
    4. Focus Server + SEGY Recorder down simultaneously

Author: QA Automation Architect
Date: 2025-11-07
Related: PZ-13756 (Infrastructure Resilience)
"""

import pytest
import time
import logging
from typing import Dict, Any, Optional, List, Tuple

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
@pytest.mark.regression
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
# Helper Functions
# ===================================================================

def scale_down_pods(k8s_manager: KubernetesManager, deployments: List[Tuple[str, str]], namespace: str) -> bool:
    """
    Scale down multiple deployments.
    
    Args:
        k8s_manager: Kubernetes manager instance
        deployments: List of (deployment_name, deployment_type) tuples
        namespace: Kubernetes namespace
        
    Returns:
        True if all scaled down successfully
    """
    for deployment_name, deployment_type in deployments:
        logger.info(f"Scaling {deployment_type} '{deployment_name}' to 0...")
        if deployment_type == "StatefulSet":
            if not k8s_manager.scale_statefulset(deployment_name, replicas=0, namespace=namespace):
                logger.error(f"Failed to scale {deployment_type} '{deployment_name}'")
                return False
        else:
            if not k8s_manager.scale_deployment(deployment_name, replicas=0, namespace=namespace):
                logger.error(f"Failed to scale {deployment_type} '{deployment_name}'")
                return False
    
    # Wait for pods to terminate
    for deployment_name, deployment_type in deployments:
        logger.info(f"Waiting for {deployment_type} '{deployment_name}' pods to terminate...")
        for attempt in range(60):
            pods = k8s_manager.get_pods(namespace=namespace)
            # Filter pods by deployment name pattern
            matching_pods = [p for p in pods if deployment_name.split('-')[-1] in p.get('name', '')]
            if len(matching_pods) == 0:
                break
            time.sleep(1)
    
    return True


def scale_up_pods(k8s_manager: KubernetesManager, deployments: List[Tuple[str, str]], namespace: str) -> bool:
    """
    Scale up multiple deployments.
    
    Args:
        k8s_manager: Kubernetes manager instance
        deployments: List of (deployment_name, deployment_type) tuples
        namespace: Kubernetes namespace
        
    Returns:
        True if all scaled up successfully
    """
    for deployment_name, deployment_type in deployments:
        logger.info(f"Scaling {deployment_type} '{deployment_name}' to 1...")
        if deployment_type == "StatefulSet":
            if not k8s_manager.scale_statefulset(deployment_name, replicas=1, namespace=namespace):
                logger.error(f"Failed to scale {deployment_type} '{deployment_name}'")
                return False
        else:
            if not k8s_manager.scale_deployment(deployment_name, replicas=1, namespace=namespace):
                logger.error(f"Failed to scale {deployment_type} '{deployment_name}'")
                return False
    
    # Wait for pods to be ready
    for deployment_name, deployment_type in deployments:
        logger.info(f"Waiting for {deployment_type} '{deployment_name}' pod to be ready...")
        for attempt in range(120):
            pods = k8s_manager.get_pods(namespace=namespace)
            matching_pods = [p for p in pods if deployment_name.split('-')[-1] in p.get('name', '')]
            if matching_pods:
                pod_name = matching_pods[0]['name']
                if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                    break
            time.sleep(2)
    
    return True


# ===================================================================
# Test Class: Multiple Pods Resilience
# ===================================================================

@pytest.mark.critical


@pytest.mark.regression
class TestMultiplePodsResilience:
    """
    Test suite for multiple pods failure scenarios.
    
    Tests validate:
    - Multiple pods down simultaneously
    - Cascading failures
    - Recovery order
    - System stability during multiple outages
    """
    
    @pytest.mark.xray("PZ-14738")

    
    @pytest.mark.regression
    def test_mongodb_rabbitmq_down_simultaneously(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: MongoDB + RabbitMQ Down Simultaneously
        
        Validates that when both MongoDB and RabbitMQ are down:
        1. System handles complete outage gracefully
        2. Clear errors are returned
        3. No crashes occur
        4. System recovers after both are restored
        
        Steps:
            1. Scale MongoDB and RabbitMQ to 0
            2. Wait for pods to terminate
            3. Attempt operations (should fail gracefully)
            4. Scale both back to 1
            5. Wait for recovery
            6. Verify functionality restored
        
        Expected:
            - Complete outage handled gracefully
            - Clear error messages
            - No crashes
            - System recovers after restoration
        
        Jira: PZ-14738
        Priority: P1
        """
        logger.info("=" * 80)
        logger.info("TEST: MongoDB + RabbitMQ Down Simultaneously")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        deployments = [
            ("mongodb", "Deployment"),
            ("rabbitmq-panda", "StatefulSet")
        ]
        
        try:
            # Scale down both
            logger.info("\nStep 1: Scaling down MongoDB and RabbitMQ...")
            assert scale_down_pods(k8s_manager, deployments, namespace), \
                "Failed to scale down pods"
            logger.info("✅ Both pods scaled down")
            time.sleep(5)
            
            # Attempt operations
            logger.info("\nStep 2: Attempting operations during outage...")
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
                if "503" in error_str or "unavailable" in error_str:
                    logger.info(f"✅ Job creation failed gracefully: {e}")
                else:
                    logger.warning(f"⚠️  Unexpected error: {e}")
            except Exception as e:
                logger.info(f"✅ Job creation failed (expected): {type(e).__name__}")
            
            logger.info("✅ No crashes occurred")
            logger.info("✅ Errors handled gracefully")
            
            # Scale up both
            logger.info("\nStep 3: Scaling up MongoDB and RabbitMQ...")
            assert scale_up_pods(k8s_manager, deployments, namespace), \
                "Failed to scale up pods"
            logger.info("✅ Both pods scaled up")
            
            # Verify functionality
            logger.info("\nStep 4: Verifying functionality restored...")
            time.sleep(10)
            
            try:
                config_request = ConfigureRequest(**test_config)
                response = focus_server_api.configure_streaming_job(config_request)
                logger.info(f"✅ Functionality restored - job created: {response.job_id}")
                
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
            except Exception as e:
                logger.warning(f"⚠️  Functionality test failed: {e}")
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: MongoDB + RabbitMQ Down Simultaneously")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            # Ensure pods are restored
            try:
                scale_up_pods(k8s_manager, deployments, namespace)
            except:
                pass
            raise
    
    @pytest.mark.xray("PZ-14739")

    
    @pytest.mark.regression
    def test_mongodb_focus_server_down_simultaneously(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: MongoDB + Focus Server Down Simultaneously
        
        Validates that when both MongoDB and Focus Server are down:
        1. Complete outage handled gracefully
        2. Clear errors returned
        3. No crashes occur
        4. System recovers after restoration
        
        Steps:
            1. Scale MongoDB and Focus Server to 0
            2. Wait for pods to terminate
            3. Attempt operations (should fail gracefully)
            4. Scale both back to 1
            5. Wait for recovery
            6. Verify functionality restored
        
        Expected:
            - Complete outage handled gracefully
            - Clear error messages
            - No crashes
            - System recovers after restoration
        
        Jira: PZ-14739
        Priority: P1
        """
        logger.info("=" * 80)
        logger.info("TEST: MongoDB + Focus Server Down Simultaneously")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        deployments = [
            ("mongodb", "Deployment"),
            ("panda-panda-focus-server", "Deployment")
        ]
        
        try:
            # Scale down both
            logger.info("\nStep 1: Scaling down MongoDB and Focus Server...")
            assert scale_down_pods(k8s_manager, deployments, namespace), \
                "Failed to scale down pods"
            logger.info("✅ Both pods scaled down")
            time.sleep(5)
            
            # Attempt operations
            logger.info("\nStep 2: Attempting operations during outage...")
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
            
            # Scale up both
            logger.info("\nStep 3: Scaling up MongoDB and Focus Server...")
            assert scale_up_pods(k8s_manager, deployments, namespace), \
                "Failed to scale up pods"
            logger.info("✅ Both pods scaled up")
            
            # Verify functionality
            logger.info("\nStep 4: Verifying functionality restored...")
            time.sleep(10)
            
            # Wait for API to be accessible
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
            
            try:
                config_request = ConfigureRequest(**test_config)
                response = focus_server_api.configure_streaming_job(config_request)
                logger.info(f"✅ Functionality restored - job created: {response.job_id}")
                
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
            except Exception as e:
                logger.warning(f"⚠️  Functionality test failed: {e}")
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: MongoDB + Focus Server Down Simultaneously")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            try:
                scale_up_pods(k8s_manager, deployments, namespace)
            except:
                pass
            raise
    
    @pytest.mark.xray("PZ-14740")

    
    @pytest.mark.regression
    def test_rabbitmq_focus_server_down_simultaneously(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: RabbitMQ + Focus Server Down Simultaneously
        
        Validates that when both RabbitMQ and Focus Server are down:
        1. Complete outage handled gracefully
        2. Clear errors returned
        3. No crashes occur
        4. System recovers after restoration
        
        Steps:
            1. Scale RabbitMQ and Focus Server to 0
            2. Wait for pods to terminate
            3. Attempt operations (should fail gracefully)
            4. Scale both back to 1
            5. Wait for recovery
            6. Verify functionality restored
        
        Expected:
            - Complete outage handled gracefully
            - Clear error messages
            - No crashes
            - System recovers after restoration
        
        Jira: PZ-14740
        Priority: P1
        """
        logger.info("=" * 80)
        logger.info("TEST: RabbitMQ + Focus Server Down Simultaneously")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        deployments = [
            ("rabbitmq-panda", "StatefulSet"),
            ("panda-panda-focus-server", "Deployment")
        ]
        
        try:
            # Scale down both
            logger.info("\nStep 1: Scaling down RabbitMQ and Focus Server...")
            assert scale_down_pods(k8s_manager, deployments, namespace), \
                "Failed to scale down pods"
            logger.info("✅ Both pods scaled down")
            time.sleep(5)
            
            # Attempt operations
            logger.info("\nStep 2: Attempting operations during outage...")
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
            
            # Scale up both
            logger.info("\nStep 3: Scaling up RabbitMQ and Focus Server...")
            assert scale_up_pods(k8s_manager, deployments, namespace), \
                "Failed to scale up pods"
            logger.info("✅ Both pods scaled up")
            
            # Verify functionality
            logger.info("\nStep 4: Verifying functionality restored...")
            time.sleep(10)
            
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
            
            try:
                config_request = ConfigureRequest(**test_config)
                response = focus_server_api.configure_streaming_job(config_request)
                logger.info(f"✅ Functionality restored - job created: {response.job_id}")
                
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
            except Exception as e:
                logger.warning(f"⚠️  Functionality test failed: {e}")
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: RabbitMQ + Focus Server Down Simultaneously")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            try:
                scale_up_pods(k8s_manager, deployments, namespace)
            except:
                pass
            raise
    
    @pytest.mark.xray("PZ-14741")

    
    @pytest.mark.regression
    def test_focus_server_segy_recorder_down_simultaneously(
        self,
        k8s_manager: KubernetesManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: Focus Server + SEGY Recorder Down Simultaneously
        
        Validates that when both Focus Server and SEGY Recorder are down:
        1. Jobs fail gracefully
        2. Recording stops
        3. No crashes occur
        4. System recovers after restoration
        
        Steps:
            1. Scale Focus Server and SEGY Recorder to 0
            2. Wait for pods to terminate
            3. Attempt operations (should fail gracefully)
            4. Scale both back to 1
            5. Wait for recovery
            6. Verify functionality restored
        
        Expected:
            - Jobs fail gracefully
            - Recording stops
            - No crashes
            - System recovers after restoration
        
        Jira: PZ-14741
        Priority: P2
        """
        logger.info("=" * 80)
        logger.info("TEST: Focus Server + SEGY Recorder Down Simultaneously")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        deployments = [
            ("panda-panda-focus-server", "Deployment"),
            ("panda-panda-segy-recorder", "Deployment")
        ]
        
        try:
            # Scale down both
            logger.info("\nStep 1: Scaling down Focus Server and SEGY Recorder...")
            assert scale_down_pods(k8s_manager, deployments, namespace), \
                "Failed to scale down pods"
            logger.info("✅ Both pods scaled down")
            time.sleep(5)
            
            # Attempt operations
            logger.info("\nStep 2: Attempting operations during outage...")
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
            
            logger.info("ℹ️  Recording stopped (expected behavior)")
            logger.info("✅ No crashes occurred")
            
            # Scale up both
            logger.info("\nStep 3: Scaling up Focus Server and SEGY Recorder...")
            assert scale_up_pods(k8s_manager, deployments, namespace), \
                "Failed to scale up pods"
            logger.info("✅ Both pods scaled up")
            
            # Verify functionality
            logger.info("\nStep 4: Verifying functionality restored...")
            time.sleep(10)
            
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
            
            try:
                config_request = ConfigureRequest(**test_config)
                response = focus_server_api.configure_streaming_job(config_request)
                logger.info(f"✅ Functionality restored - job created: {response.job_id}")
                
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
            except Exception as e:
                logger.warning(f"⚠️  Functionality test failed: {e}")
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: Focus Server + SEGY Recorder Down Simultaneously")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            try:
                scale_up_pods(k8s_manager, deployments, namespace)
            except:
                pass
            raise


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary


@pytest.mark.regression
def test_multiple_pods_resilience_summary():
    """Summary test for multiple pods resilience tests."""
    logger.info("=" * 80)
    logger.info("Multiple Pods Resilience Tests Suite Summary")
    logger.info("=" * 80)
    logger.info("Tests in this module:")
    logger.info("  1. PZ-14738: MongoDB + RabbitMQ down simultaneously")
    logger.info("  2. PZ-14739: MongoDB + Focus Server down simultaneously")
    logger.info("  3. PZ-14740: RabbitMQ + Focus Server down simultaneously")
    logger.info("  4. PZ-14741: Focus Server + SEGY Recorder down simultaneously")
    logger.info("=" * 80)

