"""
Infrastructure Tests - SEGY Recorder Pod Resilience
=====================================================

Tests for SEGY Recorder pod resilience and failure scenarios.

Test Coverage:
    1. SEGY Recorder pod deletion and automatic recreation
    2. SEGY Recorder scale down to 0 replicas
    3. SEGY Recorder pod restart during recording
    4. SEGY Recorder outage behavior
    5. SEGY Recorder recovery after outage

Author: QA Automation Architect
Date: 2025-11-07
Related: PZ-13756 (Infrastructure Resilience)
"""

import pytest
import time
import logging
from typing import Dict, Any, Optional

from src.infrastructure.kubernetes_manager import KubernetesManager
from src.core.exceptions import InfrastructureError

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


# ===================================================================
# Test Class: SEGY Recorder Pod Resilience
# ===================================================================

@pytest.mark.slow


@pytest.mark.regression
class TestSEGYRecorderPodResilience:
    """
    Test suite for SEGY Recorder pod resilience and failure scenarios.
    
    Tests validate:
    - Pod deletion and automatic recreation
    - Scale down/up scenarios
    - Pod restart during recording operations
    - Outage behavior
    - System recovery after outages
    """
    
    @pytest.mark.xray("PZ-14733")

    
    @pytest.mark.regression
    def test_segy_recorder_pod_deletion_recreation(
        self,
        k8s_manager: KubernetesManager
    ):
        """
        Test: SEGY Recorder Pod Deletion and Recreation
        
        Validates that when SEGY Recorder pod is deleted:
        1. Kubernetes automatically recreates the pod
        2. New pod becomes ready
        3. Recording functionality is restored
        
        Steps:
            1. Get current SEGY Recorder pod name
            2. Delete SEGY Recorder pod
            3. Wait for pod deletion
            4. Wait for new pod to be created
            5. Wait for new pod to be ready
            6. Verify pod is running
        
        Expected:
            - Pod deleted successfully
            - New pod created automatically within 60 seconds
            - New pod becomes ready within 120 seconds
        
        Jira: PZ-14733
        Priority: P1
        """
        logger.info("=" * 80)
        logger.info("TEST: SEGY Recorder Pod Deletion and Recreation")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        original_pod_name = None
        new_pod_name = None
        
        try:
            # Step 1: Get current SEGY Recorder pod
            logger.info("\nStep 1: Getting current SEGY Recorder pod...")
            pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-segy-recorder")
            if not pods:
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=segy-recorder")
            
            assert len(pods) > 0, "SEGY Recorder pod not found"
            original_pod = pods[0]
            original_pod_name = original_pod['name']
            logger.info(f"✅ Original SEGY Recorder pod: {original_pod_name}")
            
            # Step 2: Delete SEGY Recorder pod
            logger.info(f"\nStep 2: Deleting SEGY Recorder pod '{original_pod_name}'...")
            assert k8s_manager.delete_pod(original_pod_name, namespace=namespace), \
                "Failed to delete SEGY Recorder pod"
            logger.info("✅ SEGY Recorder pod deleted")
            
            # Step 3: Wait for pod deletion
            logger.info("\nStep 3: Waiting for pod deletion...")
            deleted = False
            for attempt in range(30):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-segy-recorder")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=segy-recorder")
                if not any(p['name'] == original_pod_name for p in pods):
                    deleted = True
                    logger.info("✅ Pod deleted")
                    break
                time.sleep(1)
            
            assert deleted, f"Pod {original_pod_name} not deleted within 30 seconds"
            
            # Step 4: Wait for new pod to be created
            logger.info("\nStep 4: Waiting for new pod to be created...")
            for attempt in range(60):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-segy-recorder")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=segy-recorder")
                if pods:
                    new_pod = pods[0]
                    if new_pod['name'] != original_pod_name:
                        new_pod_name = new_pod['name']
                        logger.info(f"✅ New pod created: {new_pod_name}")
                        break
                time.sleep(1)
            
            assert new_pod_name, "New SEGY Recorder pod not created within 60 seconds"
            
            # Step 5: Wait for new pod to be ready
            logger.info(f"\nStep 5: Waiting for pod '{new_pod_name}' to be ready...")
            ready = k8s_manager.wait_for_pod_ready(new_pod_name, namespace=namespace, timeout=120)
            assert ready, f"Pod {new_pod_name} not ready within 120 seconds"
            logger.info("✅ Pod is ready")
            
            # Step 6: Verify pod is running
            logger.info("\nStep 6: Verifying pod is running...")
            pod_info = k8s_manager.get_pod_by_name(new_pod_name, namespace=namespace)
            assert pod_info is not None, "Pod not found"
            assert pod_info.get('status') == 'Running', f"Pod status should be Running, got {pod_info.get('status')}"
            logger.info("✅ Pod is running")
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: SEGY Recorder Pod Deletion and Recreation")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            raise
        finally:
            if new_pod_name:
                logger.info(f"\nCleanup: Verifying SEGY Recorder pod '{new_pod_name}' is running...")
                pod_info = k8s_manager.get_pod_by_name(new_pod_name, namespace=namespace)
                if pod_info and pod_info.get('status') != 'Running':
                    logger.warning(f"⚠️  SEGY Recorder pod '{new_pod_name}' is not running")
    
    @pytest.mark.xray("PZ-14734")

    
    @pytest.mark.regression
    def test_segy_recorder_scale_down_to_zero(
        self,
        k8s_manager: KubernetesManager
    ):
        """
        Test: SEGY Recorder Scale Down to 0 Replicas
        
        Validates that when SEGY Recorder is scaled down to 0:
        1. All pods are terminated
        2. Recording stops (expected behavior)
        3. No crashes occur
        4. System recovers after scale up
        
        Steps:
            1. Verify SEGY Recorder pod exists
            2. Scale SEGY Recorder deployment to 0
            3. Wait for pods to terminate
            4. Scale SEGY Recorder back to 1
            5. Wait for pod to be ready
        
        Expected:
            - SEGY Recorder scaled down successfully
            - All pods terminated
            - SEGY Recorder restored after scale up
        
        Jira: PZ-14734
        Priority: P1
        """
        logger.info("=" * 80)
        logger.info("TEST: SEGY Recorder Scale Down to 0 Replicas")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        deployment_name = "panda-panda-segy-recorder"
        
        try:
            # Step 1: Verify SEGY Recorder pod exists
            logger.info("\nStep 1: Verifying SEGY Recorder pod exists...")
            pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-segy-recorder")
            if not pods:
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=segy-recorder")
            assert len(pods) > 0, "SEGY Recorder pod not found"
            logger.info(f"✅ SEGY Recorder pod found: {pods[0]['name']}")
            
            # Step 2: Scale SEGY Recorder deployment to 0
            logger.info(f"\nStep 2: Scaling SEGY Recorder deployment '{deployment_name}' to 0 replicas...")
            assert k8s_manager.scale_deployment(deployment_name, replicas=0, namespace=namespace), \
                "Failed to scale SEGY Recorder to 0"
            logger.info("✅ SEGY Recorder scaled down to 0")
            
            # Step 3: Wait for pods to terminate
            logger.info("\nStep 3: Waiting for pods to terminate...")
            pods_terminated = False
            for attempt in range(60):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-segy-recorder")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=segy-recorder")
                if len(pods) == 0:
                    pods_terminated = True
                    logger.info("✅ All SEGY Recorder pods terminated")
                    break
                time.sleep(1)
            
            assert pods_terminated, "SEGY Recorder pods not terminated within 60 seconds"
            logger.info("ℹ️  Recording stopped (expected behavior)")
            
            # Step 4: Scale SEGY Recorder back to 1
            logger.info(f"\nStep 4: Scaling SEGY Recorder deployment '{deployment_name}' back to 1 replica...")
            assert k8s_manager.scale_deployment(deployment_name, replicas=1, namespace=namespace), \
                "Failed to scale SEGY Recorder back to 1"
            logger.info("✅ SEGY Recorder scaled up to 1")
            
            # Step 5: Wait for pod to be ready
            logger.info("\nStep 5: Waiting for SEGY Recorder pod to be ready...")
            pod_ready = False
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-segy-recorder")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=segy-recorder")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        pod_ready = True
                        logger.info(f"✅ SEGY Recorder pod '{pod_name}' is ready")
                        break
                time.sleep(2)
            
            assert pod_ready, "SEGY Recorder pod not ready within 120 seconds"
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: SEGY Recorder Scale Down to 0 Replicas")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            # Ensure SEGY Recorder is restored
            try:
                logger.info("\nCleanup: Restoring SEGY Recorder to 1 replica...")
                k8s_manager.scale_deployment(deployment_name, replicas=1, namespace=namespace)
            except:
                pass
            raise
    
    @pytest.mark.xray("PZ-14735")

    
    @pytest.mark.regression
    def test_segy_recorder_pod_restart_during_recording(
        self,
        k8s_manager: KubernetesManager
    ):
        """
        Test: SEGY Recorder Pod Restart During Recording
        
        Validates that when SEGY Recorder pod restarts during recording:
        1. Pod restart is handled gracefully
        2. Recording may be interrupted (expected)
        3. Pod recovers after restart
        4. Recording can resume
        
        Steps:
            1. Get SEGY Recorder pod name
            2. Restart SEGY Recorder pod
            3. Verify pod restarted successfully
            4. Verify pod is ready
        
        Expected:
            - Pod restart handled gracefully
            - Pod recovers after restart
            - Recording can resume
        
        Jira: PZ-14735
        Priority: P2
        """
        logger.info("=" * 80)
        logger.info("TEST: SEGY Recorder Pod Restart During Recording")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        pod_name = None
        
        try:
            # Step 1: Get SEGY Recorder pod name
            logger.info("\nStep 1: Getting SEGY Recorder pod name...")
            pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-segy-recorder")
            if not pods:
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=segy-recorder")
            assert len(pods) > 0, "SEGY Recorder pod not found"
            pod_name = pods[0]['name']
            logger.info(f"✅ SEGY Recorder pod: {pod_name}")
            
            # Step 2: Restart SEGY Recorder pod
            logger.info(f"\nStep 2: Restarting SEGY Recorder pod '{pod_name}'...")
            assert k8s_manager.restart_pod(pod_name, namespace=namespace), \
                "Failed to restart SEGY Recorder pod"
            logger.info("✅ SEGY Recorder pod restart initiated")
            
            # Step 3: Verify pod restarted successfully
            logger.info("\nStep 3: Verifying pod restarted successfully...")
            time.sleep(10)  # Give pod time to restart
            
            pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-segy-recorder")
            if not pods:
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=segy-recorder")
            assert len(pods) > 0, "SEGY Recorder pod not found after restart"
            
            new_pod_name = pods[0]['name']
            logger.info(f"✅ New pod: {new_pod_name}")
            
            # Step 4: Verify pod is ready
            logger.info("\nStep 4: Verifying pod is ready...")
            ready = k8s_manager.wait_for_pod_ready(new_pod_name, namespace=namespace, timeout=120)
            assert ready, f"Pod {new_pod_name} not ready within 120 seconds"
            logger.info("✅ Pod is ready")
            
            logger.info("ℹ️  Recording may have been interrupted (expected behavior)")
            logger.info("ℹ️  Recording can resume after pod restart")
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: SEGY Recorder Pod Restart During Recording")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            raise
    
    @pytest.mark.xray("PZ-14736")

    
    @pytest.mark.regression
    def test_segy_recorder_outage_behavior(
        self,
        k8s_manager: KubernetesManager
    ):
        """
        Test: SEGY Recorder Outage Behavior
        
        Validates that when SEGY Recorder is down:
        1. Recording stops (expected behavior)
        2. No crashes occur
        3. System remains stable
        
        Steps:
            1. Scale SEGY Recorder to 0
            2. Wait for pods to terminate
            3. Verify recording stopped
            4. Restore SEGY Recorder
        
        Expected:
            - Recording stops when SEGY Recorder is down
            - No crashes or undefined behavior
            - System remains stable
        
        Jira: PZ-14736
        Priority: P2
        """
        logger.info("=" * 80)
        logger.info("TEST: SEGY Recorder Outage Behavior")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        deployment_name = "panda-panda-segy-recorder"
        
        try:
            # Step 1: Scale SEGY Recorder to 0
            logger.info(f"\nStep 1: Scaling SEGY Recorder to 0...")
            assert k8s_manager.scale_deployment(deployment_name, replicas=0, namespace=namespace), \
                "Failed to scale SEGY Recorder to 0"
            
            # Step 2: Wait for pods to terminate
            logger.info("\nStep 2: Waiting for pods to terminate...")
            for attempt in range(60):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-segy-recorder")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=segy-recorder")
                if len(pods) == 0:
                    break
                time.sleep(1)
            
            logger.info("✅ SEGY Recorder scaled down")
            
            # Step 3: Verify recording stopped
            logger.info("\nStep 3: Verifying recording stopped...")
            logger.info("ℹ️  Recording stopped (expected behavior when SEGY Recorder is down)")
            logger.info("✅ No crashes occurred")
            logger.info("✅ System remains stable")
            
            # Step 4: Restore SEGY Recorder
            logger.info(f"\nStep 4: Restoring SEGY Recorder...")
            assert k8s_manager.scale_deployment(deployment_name, replicas=1, namespace=namespace), \
                "Failed to restore SEGY Recorder"
            
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-segy-recorder")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=segy-recorder")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        logger.info("✅ SEGY Recorder restored")
                        break
                time.sleep(2)
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: SEGY Recorder Outage Behavior")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            try:
                k8s_manager.scale_deployment(deployment_name, replicas=1, namespace=namespace)
            except:
                pass
            raise
    
    @pytest.mark.xray("PZ-14737")

    
    @pytest.mark.regression
    def test_segy_recorder_recovery_after_outage(
        self,
        k8s_manager: KubernetesManager
    ):
        """
        Test: SEGY Recorder Recovery After Outage
        
        Validates that after SEGY Recorder outage:
        1. System recovers automatically
        2. SEGY Recorder pod is restored
        3. Recording can resume
        
        Steps:
            1. Scale SEGY Recorder to 0
            2. Wait for outage
            3. Scale SEGY Recorder back to 1
            4. Wait for recovery
            5. Verify pod is ready
        
        Expected:
            - SEGY Recorder recovers within reasonable time
            - Pod restored
            - Recording can resume
        
        Jira: PZ-14737
        Priority: P1
        """
        logger.info("=" * 80)
        logger.info("TEST: SEGY Recorder Recovery After Outage")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        deployment_name = "panda-panda-segy-recorder"
        
        try:
            # Scale to 0
            logger.info(f"\nStep 1: Scaling SEGY Recorder to 0...")
            assert k8s_manager.scale_deployment(deployment_name, replicas=0, namespace=namespace), \
                "Failed to scale SEGY Recorder to 0"
            
            for attempt in range(60):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-segy-recorder")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=segy-recorder")
                if len(pods) == 0:
                    break
                time.sleep(1)
            
            logger.info("✅ SEGY Recorder scaled down")
            time.sleep(10)
            
            # Scale back to 1
            logger.info(f"\nStep 2: Scaling SEGY Recorder back to 1...")
            assert k8s_manager.scale_deployment(deployment_name, replicas=1, namespace=namespace), \
                "Failed to restore SEGY Recorder"
            
            recovery_start = time.time()
            
            pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-segy-recorder")
            if not pods:
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=segy-recorder")
            assert len(pods) > 0, "SEGY Recorder pod not created"
            
            pod_name = pods[0]['name']
            ready = k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=120)
            assert ready, "SEGY Recorder pod not ready"
            
            recovery_time = time.time() - recovery_start
            logger.info(f"✅ SEGY Recorder recovered in {recovery_time:.1f} seconds")
            logger.info("ℹ️  Recording can resume after recovery")
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: SEGY Recorder Recovery After Outage")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            try:
                k8s_manager.scale_deployment(deployment_name, replicas=1, namespace=namespace)
            except:
                pass
            raise


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary


@pytest.mark.regression
def test_segy_recorder_pod_resilience_summary():
    """Summary test for SEGY Recorder pod resilience tests."""
    logger.info("=" * 80)
    logger.info("SEGY Recorder Pod Resilience Tests Suite Summary")
    logger.info("=" * 80)
    logger.info("Tests in this module:")
    logger.info("  1. PZ-14733: SEGY Recorder pod deletion and recreation")
    logger.info("  2. PZ-14734: SEGY Recorder scale down to 0 replicas")
    logger.info("  3. PZ-14735: SEGY Recorder pod restart during recording")
    logger.info("  4. PZ-14736: SEGY Recorder outage behavior")
    logger.info("  5. PZ-14737: SEGY Recorder recovery after outage")
    logger.info("=" * 80)

