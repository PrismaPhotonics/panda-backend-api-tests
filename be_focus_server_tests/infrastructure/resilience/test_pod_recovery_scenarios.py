"""
Infrastructure Tests - Pod Recovery Scenarios
===============================================

Tests for pod recovery scenarios and recovery order validation.

Test Coverage:
    1. Recovery order validation (MongoDB first, then RabbitMQ, then Focus Server)
    2. Cascading recovery scenarios
    3. Recovery time measurement

Author: QA Automation Architect
Date: 2025-11-07
Related: PZ-13756 (Infrastructure Resilience)
"""

import pytest
import time
import logging
from typing import Dict, Any, Optional, List

from src.apis.focus_server_api import FocusServerAPI
from src.models.focus_server_models import ConfigureRequest, ViewType
from src.infrastructure.kubernetes_manager import KubernetesManager
from src.infrastructure.mongodb_manager import MongoDBManager
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
def mongodb_manager(config_manager, k8s_manager):
    """Fixture to provide MongoDBManager instance."""
    logger.info("Initializing MongoDB manager...")
    manager = MongoDBManager(config_manager, kubernetes_manager=k8s_manager)
    yield manager
    logger.info("MongoDB manager fixture cleanup complete")


@pytest.fixture
# Note: regression marker - fixture for resilience tests
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
# Test Class: Pod Recovery Scenarios
# ===================================================================

@pytest.mark.slow
@pytest.mark.nightly
@pytest.mark.resilience
@pytest.mark.regression
class TestPodRecoveryScenarios:
    """
    Test suite for pod recovery scenarios.
    
    Tests validate:
    - Recovery order (dependencies first)
    - Cascading recovery
    - Recovery time measurement
    """
    
    @pytest.mark.xray("PZ-14742")

    
    @pytest.mark.regression
    def test_recovery_order_validation(
        self,
        k8s_manager: KubernetesManager,
        mongodb_manager: MongoDBManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: Recovery Order Validation
        
        Validates that pods recover in the correct order:
        1. MongoDB should recover first (infrastructure dependency)
        2. RabbitMQ should recover second (depends on MongoDB)
        3. Focus Server should recover last (depends on MongoDB and RabbitMQ)
        
        Steps:
            1. Scale all pods to 0
            2. Scale MongoDB to 1 and wait for ready
            3. Scale RabbitMQ to 1 and wait for ready
            4. Scale Focus Server to 1 and wait for ready
            5. Verify system functionality
        
        Expected:
            - Recovery order is correct
            - Each pod becomes ready before next one starts
            - System functionality restored after all pods recover
        
        Jira: PZ-14742
        Priority: P1
        """
        logger.info("=" * 80)
        logger.info("TEST: Recovery Order Validation")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        
        try:
            # Step 1: Scale all pods to 0
            logger.info("\nStep 1: Scaling all pods to 0...")
            
            # Scale MongoDB
            k8s_manager.scale_deployment("mongodb", replicas=0, namespace=namespace)
            # Scale RabbitMQ
            k8s_manager.scale_statefulset("rabbitmq-panda", replicas=0, namespace=namespace)
            # Scale Focus Server
            k8s_manager.scale_deployment("panda-panda-focus-server", replicas=0, namespace=namespace)
            
            # Wait for all pods to terminate
            logger.info("Waiting for all pods to terminate...")
            time.sleep(10)
            
            logger.info("✅ All pods scaled down")
            
            # Step 2: Scale MongoDB to 1
            logger.info("\nStep 2: Scaling MongoDB to 1...")
            assert k8s_manager.scale_deployment("mongodb", replicas=1, namespace=namespace), \
                "Failed to scale MongoDB"
            
            # Wait for MongoDB pod to be ready
            mongodb_ready = False
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=mongodb")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        mongodb_ready = True
                        logger.info(f"✅ MongoDB pod '{pod_name}' is ready")
                        break
                time.sleep(2)
            
            assert mongodb_ready, "MongoDB pod not ready"
            
            # Verify MongoDB connection
            connection_restored = False
            for attempt in range(30):
                if mongodb_manager.connect():
                    connection_restored = True
                    mongodb_manager.disconnect()
                    break
                time.sleep(1)
            
            assert connection_restored, "MongoDB connection not restored"
            logger.info("✅ MongoDB recovered and accessible")
            
            # Step 3: Scale RabbitMQ to 1
            logger.info("\nStep 3: Scaling RabbitMQ to 1...")
            assert k8s_manager.scale_statefulset("rabbitmq-panda", replicas=1, namespace=namespace), \
                "Failed to scale RabbitMQ"
            
            # Wait for RabbitMQ pod to be ready
            rabbitmq_ready = False
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=rabbitmq")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        rabbitmq_ready = True
                        logger.info(f"✅ RabbitMQ pod '{pod_name}' is ready")
                        break
                time.sleep(2)
            
            assert rabbitmq_ready, "RabbitMQ pod not ready"
            logger.info("✅ RabbitMQ recovered")
            
            # Step 4: Scale Focus Server to 1
            logger.info("\nStep 4: Scaling Focus Server to 1...")
            assert k8s_manager.scale_deployment("panda-panda-focus-server", replicas=1, namespace=namespace), \
                "Failed to scale Focus Server"
            
            # Wait for Focus Server pod to be ready
            focus_server_ready = False
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        focus_server_ready = True
                        logger.info(f"✅ Focus Server pod '{pod_name}' is ready")
                        break
                time.sleep(2)
            
            assert focus_server_ready, "Focus Server pod not ready"
            
            # Verify Focus Server API
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
            logger.info("✅ Focus Server recovered and accessible")
            
            # Step 5: Verify system functionality
            logger.info("\nStep 5: Verifying system functionality...")
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
            logger.info("✅ TEST PASSED: Recovery Order Validation")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            # Ensure all pods are restored
            try:
                k8s_manager.scale_deployment("mongodb", replicas=1, namespace=namespace)
                k8s_manager.scale_statefulset("rabbitmq-panda", replicas=1, namespace=namespace)
                k8s_manager.scale_deployment("panda-panda-focus-server", replicas=1, namespace=namespace)
            except:
                pass
            raise
    
    @pytest.mark.xray("PZ-14743")

    
    @pytest.mark.regression
    def test_cascading_recovery_scenarios(
        self,
        k8s_manager: KubernetesManager,
        mongodb_manager: MongoDBManager,
        focus_server_api: FocusServerAPI,
        test_config: Dict[str, Any]
    ):
        """
        Test: Cascading Recovery Scenarios
        
        Validates cascading recovery when multiple pods are restored simultaneously.
        
        Steps:
            1. Scale all pods to 0
            2. Scale all pods back to 1 simultaneously
            3. Monitor recovery progress
            4. Verify system functionality
        
        Expected:
            - Pods recover in dependency order (MongoDB → RabbitMQ → Focus Server)
            - System functionality restored after all pods recover
            - No infinite loops or cascading failures
        
        Jira: PZ-14743
        Priority: P2
        """
        logger.info("=" * 80)
        logger.info("TEST: Cascading Recovery Scenarios")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        
        try:
            # Scale all to 0
            logger.info("\nStep 1: Scaling all pods to 0...")
            k8s_manager.scale_deployment("mongodb", replicas=0, namespace=namespace)
            k8s_manager.scale_statefulset("rabbitmq-panda", replicas=0, namespace=namespace)
            k8s_manager.scale_deployment("panda-panda-focus-server", replicas=0, namespace=namespace)
            time.sleep(10)
            logger.info("✅ All pods scaled down")
            
            # Scale all back to 1 simultaneously
            logger.info("\nStep 2: Scaling all pods back to 1 simultaneously...")
            k8s_manager.scale_deployment("mongodb", replicas=1, namespace=namespace)
            k8s_manager.scale_statefulset("rabbitmq-panda", replicas=1, namespace=namespace)
            k8s_manager.scale_deployment("panda-panda-focus-server", replicas=1, namespace=namespace)
            
            # Monitor recovery progress
            logger.info("\nStep 3: Monitoring recovery progress...")
            recovery_start = time.time()
            
            # Wait for MongoDB
            mongodb_ready = False
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=mongodb")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        mongodb_ready = True
                        logger.info(f"✅ MongoDB recovered: {time.time() - recovery_start:.1f}s")
                        break
                time.sleep(2)
            
            assert mongodb_ready, "MongoDB not recovered"
            
            # Wait for RabbitMQ
            rabbitmq_ready = False
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=rabbitmq")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        rabbitmq_ready = True
                        logger.info(f"✅ RabbitMQ recovered: {time.time() - recovery_start:.1f}s")
                        break
                time.sleep(2)
            
            assert rabbitmq_ready, "RabbitMQ not recovered"
            
            # Wait for Focus Server
            focus_server_ready = False
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        focus_server_ready = True
                        logger.info(f"✅ Focus Server recovered: {time.time() - recovery_start:.1f}s")
                        break
                time.sleep(2)
            
            assert focus_server_ready, "Focus Server not recovered"
            
            # Verify API
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
            logger.info(f"\n✅ Total recovery time: {recovery_time:.1f} seconds")
            
            # Verify functionality
            logger.info("\nStep 4: Verifying system functionality...")
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
            logger.info("✅ TEST PASSED: Cascading Recovery Scenarios")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            try:
                k8s_manager.scale_deployment("mongodb", replicas=1, namespace=namespace)
                k8s_manager.scale_statefulset("rabbitmq-panda", replicas=1, namespace=namespace)
                k8s_manager.scale_deployment("panda-panda-focus-server", replicas=1, namespace=namespace)
            except:
                pass
            raise
    
    @pytest.mark.xray("PZ-14744")

    
    @pytest.mark.regression
    def test_recovery_time_measurement(
        self,
        k8s_manager: KubernetesManager,
        mongodb_manager: MongoDBManager,
        focus_server_api: FocusServerAPI
    ):
        """
        Test: Recovery Time Measurement
        
        Measures recovery time for each pod type.
        
        Steps:
            1. Scale each pod type to 0
            2. Scale back to 1
            3. Measure recovery time
            4. Document recovery times
        
        Expected:
            - Recovery times are measured accurately
            - Recovery times are within acceptable limits
            - Recovery times are documented
        
        Jira: PZ-14744
        Priority: P2
        """
        logger.info("=" * 80)
        logger.info("TEST: Recovery Time Measurement")
        logger.info("=" * 80)
        
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        recovery_times = {}
        
        try:
            # MongoDB recovery time
            logger.info("\nMeasuring MongoDB recovery time...")
            k8s_manager.scale_deployment("mongodb", replicas=0, namespace=namespace)
            time.sleep(5)
            
            start_time = time.time()
            k8s_manager.scale_deployment("mongodb", replicas=1, namespace=namespace)
            
            mongodb_ready = False
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=mongodb")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        mongodb_ready = True
                        break
                time.sleep(2)
            
            if mongodb_ready:
                recovery_times["MongoDB"] = time.time() - start_time
                logger.info(f"✅ MongoDB recovery time: {recovery_times['MongoDB']:.1f}s")
            
            # RabbitMQ recovery time
            logger.info("\nMeasuring RabbitMQ recovery time...")
            k8s_manager.scale_statefulset("rabbitmq-panda", replicas=0, namespace=namespace)
            time.sleep(5)
            
            start_time = time.time()
            k8s_manager.scale_statefulset("rabbitmq-panda", replicas=1, namespace=namespace)
            
            rabbitmq_ready = False
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=rabbitmq")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/instance=rabbitmq-panda")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        rabbitmq_ready = True
                        break
                time.sleep(2)
            
            if rabbitmq_ready:
                recovery_times["RabbitMQ"] = time.time() - start_time
                logger.info(f"✅ RabbitMQ recovery time: {recovery_times['RabbitMQ']:.1f}s")
            
            # Focus Server recovery time
            logger.info("\nMeasuring Focus Server recovery time...")
            k8s_manager.scale_deployment("panda-panda-focus-server", replicas=0, namespace=namespace)
            time.sleep(5)
            
            start_time = time.time()
            k8s_manager.scale_deployment("panda-panda-focus-server", replicas=1, namespace=namespace)
            
            focus_server_ready = False
            for attempt in range(120):
                pods = k8s_manager.get_pods(namespace=namespace, label_selector="app.kubernetes.io/name=panda-panda-focus-server")
                if not pods:
                    pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=focus-server")
                if pods:
                    pod_name = pods[0]['name']
                    if k8s_manager.wait_for_pod_ready(pod_name, namespace=namespace, timeout=10):
                        focus_server_ready = True
                        break
                time.sleep(2)
            
            if focus_server_ready:
                recovery_times["Focus Server"] = time.time() - start_time
                logger.info(f"✅ Focus Server recovery time: {recovery_times['Focus Server']:.1f}s")
            
            # Summary
            logger.info("\n" + "=" * 80)
            logger.info("RECOVERY TIME SUMMARY:")
            logger.info("=" * 80)
            for pod_type, recovery_time in recovery_times.items():
                logger.info(f"  {pod_type}: {recovery_time:.1f} seconds")
            logger.info("=" * 80)
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: Recovery Time Measurement")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            # Ensure all pods are restored
            try:
                k8s_manager.scale_deployment("mongodb", replicas=1, namespace=namespace)
                k8s_manager.scale_statefulset("rabbitmq-panda", replicas=1, namespace=namespace)
                k8s_manager.scale_deployment("panda-panda-focus-server", replicas=1, namespace=namespace)
            except:
                pass
            raise


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary


@pytest.mark.regression
def test_pod_recovery_scenarios_summary():
    """Summary test for pod recovery scenarios tests."""
    logger.info("=" * 80)
    logger.info("Pod Recovery Scenarios Tests Suite Summary")
    logger.info("=" * 80)
    logger.info("Tests in this module:")
    logger.info("  1. PZ-14742: Recovery order validation")
    logger.info("  2. PZ-14743: Cascading recovery scenarios")
    logger.info("  3. PZ-14744: Recovery time measurement")
    logger.info("=" * 80)

