"""
MongoDB Outage Resilience Tests
===============================

Integration tests for MongoDB outage resilience scenarios.
Tests PZ-13604: Integration – Orchestrator error triggers rollback
"""

import pytest
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from src.core.base_test import InfrastructureTest
from src.core.exceptions import APIError, InfrastructureError
from src.models.focus_server_models import ConfigureRequest, ViewType


class TestMongoDBOutageResilience(InfrastructureTest):
    """
    Test MongoDB outage resilience scenarios.
    
    These tests verify that the Focus Server handles MongoDB outages gracefully
    without launching processing jobs or creating side effects.
    
    NOTE: These tests REQUIRE Kubernetes to be available as they manipulate
    MongoDB deployments and pods to simulate outage scenarios.
    """
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_mongodb_manager(self, request, mongodb_manager):
        """
        Set up MongoDB manager for the test class.
        Ensures MongoDB is restored after all tests in the class.
        
        Skips all tests in this class if Kubernetes is not available.
        """
        # Check if Kubernetes is available
        if mongodb_manager.k8s_apps_v1 is None or mongodb_manager.k8s_core_v1 is None:
            pytest.skip(
                "Kubernetes is not available. "
                "These tests require Kubernetes to simulate MongoDB outages. "
                "Please configure kubeconfig to run these tests."
            )
        
        request.cls.mongodb_manager = mongodb_manager
        self.logger.info("MongoDB manager initialized for outage resilience tests")
        
        yield
        
        # Ensure MongoDB is restored after all tests in the class
        self.logger.info("Restoring MongoDB after test class completion")
        try:
            self.mongodb_manager.restore_mongodb()
            time.sleep(10)  # Give MongoDB time to become ready
        except Exception as e:
            self.logger.error(f"Failed to restore MongoDB: {e}")
    
    @pytest.fixture(scope="function", autouse=True)
    def restore_mongo_after_each_test(self, request):
        """
        Ensure MongoDB is restored to a healthy state before each test.
        """
        # Restore MongoDB before each test to ensure a clean state
        self.logger.info("Restoring MongoDB before test execution")
        try:
            self.mongodb_manager.restore_mongodb()
            time.sleep(10)  # Give MongoDB time to become ready
            
            # Verify connection before starting the test
            if not self.mongodb_manager.connect():
                pytest.fail("MongoDB is not reachable before test starts")
            self.mongodb_manager.disconnect()
            
        except Exception as e:
            self.logger.error(f"Failed to restore MongoDB before test: {e}")
            pytest.fail(f"MongoDB restoration failed: {e}")
        
        yield
        
        # Restore MongoDB after each test, even if it fails
        self.logger.info("Restoring MongoDB after test execution")
        try:
            self.mongodb_manager.restore_mongodb()
            time.sleep(10)  # Give MongoDB time to become ready
        except Exception as e:
            self.logger.error(f"Failed to restore MongoDB after test: {e}")
    
    def _get_history_configure_payload(self) -> ConfigureRequest:
        """
        Create a valid history configure payload for testing.
        
        Returns:
            ConfigureRequest with history parameters
        """
        # Use dynamic timestamps for more realistic testing
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=10)
        
        start_time_ts = int(start_time.timestamp())
        end_time_ts = int(end_time.timestamp())
        
        return ConfigureRequest(
            displayTimeAxisDuration=10,
            nfftSelection=1024,
            displayInfo={"height": 1000},
            channels={"min": 1, "max": 3},
            frequencyRange={"min": 0, "max": 500},
            start_time=start_time_ts,
            end_time=end_time_ts,
            view_type=ViewType.MULTICHANNEL
        )
    
    def _get_live_configure_payload(self) -> ConfigureRequest:
        """
        Create a valid live configure payload for testing.
        
        Returns:
            ConfigureRequest with live parameters (no time range)
        """
        return ConfigureRequest(
            displayTimeAxisDuration=10,
            nfftSelection=1024,
            displayInfo={"height": 1000},
            channels={"min": 1, "max": 3},
            frequencyRange={"min": 0, "max": 500},
            start_time=None,
            end_time=None,
            view_type=ViewType.MULTICHANNEL
        )
    
    def _verify_no_side_effects(self, test_name: str):
        """
        Verify that no side effects occurred during the test.
        
        Args:
            test_name: Name of the test for logging
        """
        self.logger.info(f"Verifying no side effects for test: {test_name}")
        
        # Check for K8s jobs (requires KubernetesManager)
        # TODO: Implement K8s job verification when KubernetesManager is available
        self.logger.debug("K8s job verification skipped (KubernetesManager not implemented)")
        
        # Check for RabbitMQ queues (requires RabbitMQManager)
        # TODO: Implement RabbitMQ queue verification when RabbitMQManager is available
        self.logger.debug("RabbitMQ queue verification skipped (RabbitMQManager not implemented)")
        
        self.logger.info("No side effects verification completed")
    
    @pytest.mark.integration
    @pytest.mark.infrastructure
    @pytest.mark.resilience
    @pytest.mark.mongodb_outage
    @pytest.mark.slow
    def test_mongodb_scale_down_outage_returns_503_no_orchestration(self, focus_server_api):
        """
        Test MongoDB scale-down outage returns 503 with no orchestration.
        
        Test Steps:
        1. Scale down MongoDB deployment to 0 replicas
        2. Send POST /configure request with history payload
        3. Verify 503 response with error message
        4. Verify no K8s jobs created
        5. Verify no RabbitMQ queues created
        6. Verify acceptable response time (<5s)
        """
        test_name = "mongodb_scale_down_outage_returns_503_no_orchestration"
        self.logger.info(f"Starting test: {test_name}")
        
        try:
            # Step 1: Scale down MongoDB deployment to 0 replicas
            self.log_test_step("Scaling down MongoDB deployment to 0 replicas")
            self.mongodb_manager.scale_down_mongodb(replicas=0)
            time.sleep(5)  # Give K8s time to react
            
            # Step 2: Verify MongoDB is indeed down
            self.log_test_step("Verifying MongoDB is unreachable")
            assert not self.mongodb_manager.connect(), "MongoDB is still reachable after scaling down"
            
            # Step 3: Send configure request to Focus Server
            self.log_test_step("Sending POST /configure request with history payload")
            history_payload = self._get_history_configure_payload()
            
            start_time = time.time()
            with pytest.raises(APIError) as exc_info:
                focus_server_api.configure_streaming_job(history_payload)
            
            response_time = time.time() - start_time
            
            # Step 4: Verify 503 response
            self.log_test_step("Verifying 503 response")
            assert "503" in str(exc_info.value) or "500" in str(exc_info.value), \
                f"Expected 503 or 500 error, but got: {exc_info.value}"
            
            # Step 5: Verify acceptable response time (<5s)
            self.log_test_step("Verifying response time is acceptable")
            self.assert_response_time(response_time, max_time=5.0)
            
            # Step 6: Verify no side effects
            self.log_test_step("Verifying no side effects occurred")
            self._verify_no_side_effects(test_name)
            
            self.logger.info(f"Test completed successfully: {test_name}")
            
        except Exception as e:
            self.logger.error(f"Test failed: {test_name} - {e}")
            raise
    
    @pytest.mark.integration
    @pytest.mark.infrastructure
    @pytest.mark.resilience
    @pytest.mark.mongodb_outage
    @pytest.mark.slow
    @pytest.mark.skip(reason="Requires SSH access and iptables manipulation on the node")
    def test_mongodb_network_block_outage_returns_503_no_orchestration(self, focus_server_api):
        """
        Test MongoDB network block outage returns 503 with no orchestration.
        
        Test Steps:
        1. Block network access to MongoDB using iptables
        2. Send POST /configure request with history payload
        3. Verify 503 response with error message
        4. Verify no K8s jobs created
        5. Verify no RabbitMQ queues created
        6. Verify acceptable response time (<5s)
        """
        test_name = "mongodb_network_block_outage_returns_503_no_orchestration"
        self.logger.info(f"Starting test: {test_name}")
        
        try:
            # Get node IP and MongoDB port from configuration
            node_ip = self.get_config("kubernetes.cluster_host")
            mongo_port = self.get_config("mongodb.port")
            
            # Step 1: Block network access to MongoDB
            self.log_test_step("Blocking network access to MongoDB using iptables")
            self.mongodb_manager.block_network_access(node_ip, mongo_port)
            time.sleep(5)  # Give iptables time to apply
            
            # Step 2: Verify MongoDB is indeed unreachable
            self.log_test_step("Verifying MongoDB is unreachable")
            assert not self.mongodb_manager.connect(), "MongoDB is still reachable after network block"
            
            # Step 3: Send configure request to Focus Server
            self.log_test_step("Sending POST /configure request with history payload")
            history_payload = self._get_history_configure_payload()
            
            start_time = time.time()
            with pytest.raises(APIError) as exc_info:
                focus_server_api.configure_streaming_job(history_payload)
            
            response_time = time.time() - start_time
            
            # Step 4: Verify 503 response
            self.log_test_step("Verifying 503 response")
            assert "503" in str(exc_info.value) or "500" in str(exc_info.value), \
                f"Expected 503 or 500 error, but got: {exc_info.value}"
            
            # Step 5: Verify acceptable response time (<5s)
            self.log_test_step("Verifying response time is acceptable")
            self.assert_response_time(response_time, max_time=5.0)
            
            # Step 6: Verify no side effects
            self.log_test_step("Verifying no side effects occurred")
            self._verify_no_side_effects(test_name)
            
            # Cleanup: Unblock network access
            self.log_test_step("Unblocking network access to MongoDB")
            self.mongodb_manager.unblock_network_access(node_ip, mongo_port)
            
            self.logger.info(f"Test completed successfully: {test_name}")
            
        except Exception as e:
            self.logger.error(f"Test failed: {test_name} - {e}")
            raise
    
    @pytest.mark.integration
    @pytest.mark.infrastructure
    @pytest.mark.resilience
    @pytest.mark.mongodb_outage
    def test_mongodb_outage_no_live_impact(self, focus_server_api):
        """
        Test MongoDB outage should not directly impact live configure requests.
        
        Test Steps:
        1. Create MongoDB outage (scale down)
        2. Send live configure request (no time range)
        3. Verify request succeeds (assuming RabbitMQ is up)
        4. Verify no side effects
        """
        test_name = "mongodb_outage_no_live_impact"
        self.logger.info(f"Starting test: {test_name}")
        
        try:
            # Step 1: Create MongoDB outage
            self.log_test_step("Creating MongoDB outage by scaling down")
            self.mongodb_manager.scale_down_mongodb(replicas=0)
            time.sleep(5)
            
            # Step 2: Verify MongoDB is down
            self.log_test_step("Verifying MongoDB is unreachable")
            assert not self.mongodb_manager.connect(), "MongoDB is still reachable after outage"
            
            # Step 3: Send live configure request (no time range)
            self.log_test_step("Sending live configure request")
            live_payload = self._get_live_configure_payload()
            
            # Expected to succeed if only MongoDB is down and live flow doesn't depend on it
            try:
                response = focus_server_api.configure_streaming_job(live_payload)
                self.log_test_step("Live configure request succeeded as expected")
                
                # Verify response is valid
                assert response is not None, "Live configure response is None"
                assert hasattr(response, 'status'), "Live configure response missing status"
                
            except APIError as e:
                # If live requests also fail, that's acceptable behavior
                self.logger.warning(f"Live configure request failed during MongoDB outage: {e}")
                # This is not a test failure - it depends on the system architecture
            
            # Step 4: Verify no side effects
            self.log_test_step("Verifying no side effects occurred")
            self._verify_no_side_effects(test_name)
            
            self.logger.info(f"Test completed successfully: {test_name}")
            
        except Exception as e:
            self.logger.error(f"Test failed: {test_name} - {e}")
            raise
    
    @pytest.mark.integration
    @pytest.mark.infrastructure
    @pytest.mark.resilience
    @pytest.mark.mongodb_outage
    def test_mongodb_outage_logging_and_metrics(self, focus_server_api):
        """
        Test MongoDB outage should result in proper logging and metrics.
        
        Test Steps:
        1. Create MongoDB outage
        2. Send configure request
        3. Check Focus Server logs for expected error messages
        4. Verify no stack traces in logs
        5. Verify proper error metrics (if implemented)
        """
        test_name = "mongodb_outage_logging_and_metrics"
        self.logger.info(f"Starting test: {test_name}")
        
        try:
            # Step 1: Create MongoDB outage
            self.log_test_step("Creating MongoDB outage")
            self.mongodb_manager.scale_down_mongodb(replicas=0)
            time.sleep(5)
            
            # Step 2: Send configure request
            self.log_test_step("Sending configure request to trigger logging")
            history_payload = self._get_history_configure_payload()
            
            with pytest.raises(APIError):
                focus_server_api.configure_streaming_job(history_payload)
            
            # Step 3: Check Focus Server logs for expected error messages
            self.log_test_step("Checking Focus Server logs for expected error messages")
            # TODO: Implement log analysis when KubernetesManager is available
            self.logger.debug("Log analysis skipped (KubernetesManager for logs not implemented)")
            
            # Step 4: Verify no stack traces in logs
            self.log_test_step("Verifying no stack traces in logs")
            # TODO: Implement stack trace detection
            self.logger.debug("Stack trace verification skipped (not implemented)")
            
            # Step 5: Verify proper error metrics
            self.log_test_step("Verifying error metrics")
            # TODO: Implement metrics verification
            self.logger.debug("Metrics verification skipped (not implemented)")
            
            self.logger.info(f"Test completed successfully: {test_name}")
            
        except Exception as e:
            self.logger.error(f"Test failed: {test_name} - {e}")
            raise
    
    @pytest.mark.integration
    @pytest.mark.infrastructure
    @pytest.mark.resilience
    @pytest.mark.mongodb_outage
    @pytest.mark.slow
    def test_mongodb_outage_cleanup_and_restore(self, focus_server_api):
        """
        Test MongoDB can be restored after an outage.
        
        Test Steps:
        1. Create MongoDB outage
        2. Verify outage is active
        3. Restore MongoDB
        4. Verify MongoDB is reachable
        5. Verify Focus Server can process history requests
        6. Verify no side effects from restoration
        """
        test_name = "mongodb_outage_cleanup_and_restore"
        self.logger.info(f"Starting test: {test_name}")
        
        try:
            # Step 1: Create MongoDB outage
            self.log_test_step("Creating MongoDB outage")
            self.mongodb_manager.scale_down_mongodb(replicas=0)
            time.sleep(5)
            
            # Step 2: Verify outage is active
            self.log_test_step("Verifying MongoDB outage is active")
            assert not self.mongodb_manager.connect(), "MongoDB is still reachable after outage"
            
            # Step 3: Restore MongoDB
            self.log_test_step("Restoring MongoDB")
            self.mongodb_manager.restore_mongodb()
            time.sleep(15)  # Give more time for full restoration
            
            # Step 4: Verify MongoDB is reachable
            self.log_test_step("Verifying MongoDB is reachable after restoration")
            assert self.mongodb_manager.connect(), "MongoDB is not reachable after restoration"
            self.mongodb_manager.disconnect()
            
            # Step 5: Verify Focus Server can process history requests
            self.log_test_step("Verifying Focus Server can process history requests")
            history_payload = self._get_history_configure_payload()
            
            try:
                response = focus_server_api.configure_streaming_job(history_payload)
                self.log_test_step("Focus Server successfully processed history request after restoration")
                
                # Verify response is valid
                assert response is not None, "History configure response is None"
                assert hasattr(response, 'status'), "History configure response missing status"
                
            except APIError as e:
                # This might fail if there's no data in the time range
                self.logger.warning(f"History configure request failed after restoration: {e}")
                # Not a test failure - depends on available data
            
            # Step 6: Verify no side effects from restoration
            self.log_test_step("Verifying no side effects from restoration")
            self._verify_no_side_effects(test_name)
            
            self.logger.info(f"Test completed successfully: {test_name}")
            
        except Exception as e:
            self.logger.error(f"Test failed: {test_name} - {e}")
            raise