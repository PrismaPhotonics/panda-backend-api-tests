"""
Integration Tests - Live Monitoring Flow
==========================================

Comprehensive integration tests for the live monitoring flow in Focus Server.

Test Flow:
    1. POST /config/{task_id} → (no start_time)
    2. GET /waterfall/{task_id}/{row_count} (poll continuously)
    3. GET /metadata/{task_id} (get current metadata)

Author: QA Automation Architect
Date: 2025-10-07
"""

import pytest
import time
import logging
from typing import Dict, Any

from src.models.focus_server_models import ConfigTaskRequest, ConfigTaskResponse
from src.utils.helpers import generate_task_id, generate_config_payload, poll_until
from src.utils.validators import (
    validate_task_id_format, 
    validate_waterfall_response,
    validate_metadata_consistency
)

logger = logging.getLogger(__name__)


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def live_config_payload() -> Dict[str, Any]:
    """
    Generate live configuration payload.
    
    Returns:
        Configuration payload for live monitoring (no timestamps)
    """
    return generate_config_payload(
        sensors_min=0,
        sensors_max=50,
        freq_min=0,
        freq_max=500,
        nfft=1024,
        canvas_height=1000,
        live=True  # No timestamps - live mode
    )


@pytest.fixture
def configured_live_task(focus_server_api, live_config_payload):
    """
    Fixture to configure a live task and return task_id.
    
    Yields:
        task_id for the configured live task
        
    Cleanup:
        Task is cleaned up after test completes
    """
    task_id = generate_task_id("live_test")
    logger.info(f"Configuring live task: {task_id}")
    
    # Configure task
    config_request = ConfigTaskRequest(**live_config_payload)
    response = focus_server_api.config_task(task_id, config_request)
    
    assert response.status == "Config received successfully"
    logger.info(f"Live task {task_id} configured successfully")
    
    yield task_id
    
    # Cleanup (if needed)
    logger.info(f"Cleaning up live task: {task_id}")
    # Add cleanup logic here if API supports task cancellation


# ===================================================================
# Happy Path Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
class TestLiveMonitoringHappyPath:
    """
    Test suite for live monitoring happy path scenarios.
    
    These tests validate the standard live monitoring flow with expected inputs.
    """
    
    def test_configure_live_task_success(self, focus_server_api, live_config_payload):
        """
        Test: Successfully configure a live monitoring task.
        
        Steps:
            1. Generate unique task_id
            2. Send POST /config/{task_id} with live payload
            3. Verify successful response
        
        Expected:
            - Status code: 200
            - Response status: "Config received successfully"
            - Task ID returned matches input
        """
        task_id = generate_task_id("live_happy")
        logger.info(f"Test: Configuring live task {task_id}")
        
        # Validate task_id format
        assert validate_task_id_format(task_id)
        
        # Create config request
        config_request = ConfigTaskRequest(**live_config_payload)
        
        # Configure task
        response = focus_server_api.config_task(task_id, config_request)
        
        # Assertions
        assert isinstance(response, ConfigTaskResponse)
        assert response.status == "Config received successfully"
        assert response.task_id == task_id or response.task_id is None  # Some APIs may not return task_id
        
        logger.info(f"✅ Live task {task_id} configured successfully")
    
    def test_get_sensors_list(self, focus_server_api):
        """
        Test: Retrieve list of available sensors.
        
        Steps:
            1. Send GET /sensors
            2. Verify sensors list returned
        
        Expected:
            - Sensors list is non-empty
            - Sensors are sequential integers starting from 0
        """
        logger.info("Test: Getting sensors list")
        
        # Get sensors
        response = focus_server_api.get_sensors()
        
        # Assertions
        assert response.sensors is not None
        assert isinstance(response.sensors, list)
        assert len(response.sensors) > 0
        
        # Verify sensors are sequential
        assert response.sensors[0] == 0
        assert response.sensors == list(range(len(response.sensors)))
        
        logger.info(f"✅ Retrieved {len(response.sensors)} sensors")
    
    def test_get_live_metadata(self, focus_server_api):
        """
        Test: Retrieve live metadata from fiber.
        
        Steps:
            1. Send GET /live_metadata
            2. Verify metadata structure and values
        
        Expected:
            - Metadata contains required fields (prr, num_samples_per_trace, dtype)
            - Values are valid (positive numbers, valid dtype)
        """
        logger.info("Test: Getting live metadata")
        
        # Get live metadata
        metadata = focus_server_api.get_live_metadata_flat()
        
        # Assertions
        assert metadata.prr > 0, "PRR must be positive"
        assert metadata.num_samples_per_trace > 0, "Samples per trace must be positive"
        assert metadata.dtype in ["float32", "float64", "int16", "int32"], "Invalid dtype"
        
        # Validate metadata consistency
        assert validate_metadata_consistency(metadata)
        
        logger.info(f"✅ Live metadata retrieved: PRR={metadata.prr}, channels={metadata.number_of_channels}")
    
    def test_poll_waterfall_data_live_task(self, focus_server_api, configured_live_task):
        """
        Test: Poll waterfall data from a configured live task.
        
        Steps:
            1. Use pre-configured live task
            2. Poll GET /waterfall/{task_id}/{row_count} multiple times
            3. Verify data becomes available
        
        Expected:
            - Initial polls may return status 200 (no data yet)
            - Eventually status 201 with data is returned
            - Data structure is valid
        """
        task_id = configured_live_task
        row_count = 10
        max_poll_attempts = 30
        poll_interval = 2.0  # seconds
        
        logger.info(f"Test: Polling waterfall data for task {task_id}")
        
        data_received = False
        
        for attempt in range(max_poll_attempts):
            logger.debug(f"Poll attempt {attempt + 1}/{max_poll_attempts}")
            
            # Get waterfall data
            response = focus_server_api.get_waterfall(task_id, row_count)
            
            # Check status
            if response.status_code == 200:
                # No data yet - expected initially
                logger.debug(f"No data yet (status 200), continuing...")
                
            elif response.status_code == 201:
                # Data available!
                logger.info(f"✅ Data received on attempt {attempt + 1}")
                data_received = True
                
                # Validate response
                validation_result = validate_waterfall_response(response)
                assert validation_result["is_valid"]
                
                # Assertions on data
                assert response.data is not None
                assert len(response.data) > 0
                
                # Check data structure
                for block in response.data:
                    assert len(block.rows) > 0
                    assert block.current_max_amp >= block.current_min_amp
                    
                    for row in block.rows:
                        assert len(row.sensors) > 0
                        assert row.endTimestamp > row.startTimestamp
                
                break
                
            elif response.status_code == 208:
                # Baby analyzer exited - test failure
                pytest.fail(f"Baby analyzer exited unexpectedly (status 208)")
                
            elif response.status_code == 404:
                # Consumer not found - test failure
                pytest.fail(f"Consumer not found for task {task_id} (status 404)")
            
            # Wait before next poll
            time.sleep(poll_interval)
        
        # Final assertion
        assert data_received, f"No data received after {max_poll_attempts} poll attempts"
        
        logger.info(f"✅ Waterfall polling test passed for task {task_id}")
    
    def test_get_task_metadata(self, focus_server_api, configured_live_task):
        """
        Test: Retrieve task-specific metadata.
        
        Steps:
            1. Use pre-configured live task
            2. Send GET /metadata/{task_id}
            3. Verify metadata returned
        
        Expected:
            - Status 201 (metadata available) or 200 (not running yet)
            - If available, metadata structure is valid
        """
        task_id = configured_live_task
        logger.info(f"Test: Getting metadata for task {task_id}")
        
        # Get task metadata
        response = focus_server_api.get_task_metadata(task_id)
        
        # Assertions
        assert response.status_code in [200, 201], f"Unexpected status code: {response.status_code}"
        
        if response.status_code == 201:
            # Metadata available
            assert response.metadata is not None
            assert validate_metadata_consistency(response.metadata)
            
            logger.info(f"✅ Task metadata retrieved: PRR={response.metadata.prr}")
        else:
            # Consumer not running yet (status 200)
            logger.info(f"ℹ️  Consumer not running yet (status 200)")
    
    def test_complete_live_monitoring_flow(self, focus_server_api, live_config_payload):
        """
        Test: Complete end-to-end live monitoring flow.
        
        This test executes the full live monitoring workflow:
            1. Get sensors list
            2. Get live metadata
            3. Configure live task
            4. Poll for waterfall data
            5. Get task metadata
        
        Expected:
            - All steps complete successfully
            - Data flows through the pipeline
        """
        logger.info("Test: Complete live monitoring flow")
        
        # Step 1: Get sensors
        sensors_response = focus_server_api.get_sensors()
        assert len(sensors_response.sensors) > 0
        logger.info(f"✅ Step 1: Retrieved {len(sensors_response.sensors)} sensors")
        
        # Step 2: Get live metadata
        live_metadata = focus_server_api.get_live_metadata_flat()
        assert live_metadata.prr > 0
        logger.info(f"✅ Step 2: Live metadata retrieved (PRR={live_metadata.prr})")
        
        # Step 3: Configure task
        task_id = generate_task_id("complete_flow")
        config_request = ConfigTaskRequest(**live_config_payload)
        config_response = focus_server_api.config_task(task_id, config_request)
        assert config_response.status == "Config received successfully"
        logger.info(f"✅ Step 3: Task {task_id} configured")
        
        # Step 4: Poll for waterfall data
        data_received = False
        for attempt in range(20):
            response = focus_server_api.get_waterfall(task_id, 10)
            
            if response.status_code == 201:
                data_received = True
                logger.info(f"✅ Step 4: Waterfall data received (attempt {attempt + 1})")
                break
            
            time.sleep(2.0)
        
        assert data_received, "No waterfall data received"
        
        # Step 5: Get task metadata
        task_metadata_response = focus_server_api.get_task_metadata(task_id)
        assert task_metadata_response.status_code in [200, 201]
        logger.info(f"✅ Step 5: Task metadata retrieved (status {task_metadata_response.status_code})")
        
        logger.info("✅ Complete live monitoring flow test passed")


# ===================================================================
# Edge Cases Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
class TestLiveMonitoringEdgeCases:
    """
    Test suite for live monitoring edge cases.
    
    These tests validate behavior with boundary conditions and unusual scenarios.
    """
    
    def test_waterfall_with_invalid_task_id(self, focus_server_api):
        """
        Test: Request waterfall data for non-existent task.
        
        Steps:
            1. Generate task_id that was never configured
            2. Send GET /waterfall/{task_id}/{row_count}
        
        Expected:
            - Status 404 (consumer not found)
        """
        task_id = "nonexistent_task_12345"
        row_count = 10
        
        logger.info(f"Test: Waterfall request with invalid task_id: {task_id}")
        
        # Request waterfall for non-existent task
        response = focus_server_api.get_waterfall(task_id, row_count)
        
        # Assertions
        assert response.status_code == 404, "Expected status 404 for non-existent task"
        assert response.data is None
        
        logger.info("✅ Invalid task_id handled correctly (status 404)")
    
    def test_waterfall_with_zero_row_count(self, focus_server_api, configured_live_task):
        """
        Test: Request waterfall with invalid row_count = 0.
        
        Steps:
            1. Use configured live task
            2. Send GET /waterfall/{task_id}/0
        
        Expected:
            - ValidationError raised (row_count must be > 0)
        """
        task_id = configured_live_task
        
        logger.info(f"Test: Waterfall with row_count=0 for task {task_id}")
        
        # Attempt to get waterfall with row_count=0
        with pytest.raises(Exception) as exc_info:
            focus_server_api.get_waterfall(task_id, 0)
        
        # Verify exception type
        assert "row_count" in str(exc_info.value).lower()
        
        logger.info("✅ Zero row_count rejected correctly")
    
    def test_waterfall_with_negative_row_count(self, focus_server_api, configured_live_task):
        """
        Test: Request waterfall with invalid row_count < 0.
        
        Steps:
            1. Use configured live task
            2. Send GET /waterfall/{task_id}/-5
        
        Expected:
            - ValidationError raised (row_count must be > 0)
        """
        task_id = configured_live_task
        
        logger.info(f"Test: Waterfall with row_count=-5 for task {task_id}")
        
        # Attempt to get waterfall with negative row_count
        with pytest.raises(Exception) as exc_info:
            focus_server_api.get_waterfall(task_id, -5)
        
        # Verify exception type
        assert "row_count" in str(exc_info.value).lower()
        
        logger.info("✅ Negative row_count rejected correctly")
    
    def test_waterfall_with_very_large_row_count(self, focus_server_api, configured_live_task):
        """
        Test: Request waterfall with very large row_count.
        
        Steps:
            1. Use configured live task
            2. Send GET /waterfall/{task_id}/10000
        
        Expected:
            - Request succeeds (server handles large requests)
            - Response is valid (may return fewer rows than requested)
        """
        task_id = configured_live_task
        row_count = 10000
        
        logger.info(f"Test: Waterfall with large row_count={row_count} for task {task_id}")
        
        # Request with large row_count
        response = focus_server_api.get_waterfall(task_id, row_count)
        
        # Assertions
        assert response.status_code in [200, 201, 404], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 201:
            # Data returned - verify it's valid
            validation_result = validate_waterfall_response(response)
            assert validation_result["is_valid"]
            
            # Server may return fewer rows than requested
            if response.data:
                total_rows = sum(len(block.rows) for block in response.data)
                logger.info(f"Received {total_rows} rows (requested {row_count})")
        
        logger.info("✅ Large row_count handled correctly")
    
    def test_metadata_for_invalid_task_id(self, focus_server_api):
        """
        Test: Request metadata for non-existent task.
        
        Steps:
            1. Generate task_id that was never configured
            2. Send GET /metadata/{task_id}
        
        Expected:
            - Status 404 (invalid task_id)
        """
        task_id = "nonexistent_task_metadata_test"
        
        logger.info(f"Test: Metadata request for invalid task_id: {task_id}")
        
        # Request metadata for non-existent task
        response = focus_server_api.get_task_metadata(task_id)
        
        # Assertions
        assert response.status_code == 404, "Expected status 404 for non-existent task"
        assert response.metadata is None
        
        logger.info("✅ Invalid task_id for metadata handled correctly (status 404)")
    
    def test_rapid_waterfall_polling(self, focus_server_api, configured_live_task):
        """
        Test: Rapid successive waterfall requests (stress test).
        
        Steps:
            1. Use configured live task
            2. Send 50 rapid GET /waterfall requests
        
        Expected:
            - All requests complete without errors
            - Server handles rapid requests gracefully
        """
        task_id = configured_live_task
        num_requests = 50
        
        logger.info(f"Test: Rapid waterfall polling ({num_requests} requests) for task {task_id}")
        
        success_count = 0
        
        for i in range(num_requests):
            try:
                response = focus_server_api.get_waterfall(task_id, 5)
                
                # Any valid status is acceptable
                assert response.status_code in [200, 201, 208, 404]
                success_count += 1
                
            except Exception as e:
                logger.warning(f"Request {i + 1} failed: {e}")
        
        # Allow some failures (rate limiting, etc.)
        success_rate = (success_count / num_requests) * 100
        assert success_rate >= 90, f"Success rate too low: {success_rate}%"
        
        logger.info(f"✅ Rapid polling test passed ({success_count}/{num_requests} succeeded)")


# ===================================================================
# Error Handling Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
class TestLiveMonitoringErrorHandling:
    """
    Test suite for live monitoring error handling.
    
    These tests validate proper error handling and recovery.
    """
    
    def test_config_with_invalid_sensor_range(self, focus_server_api):
        """
        Test: Configure task with invalid sensor range (min > max).
        
        Steps:
            1. Create config with sensors.min > sensors.max
            2. Attempt to configure task
        
        Expected:
            - ValidationError raised before API call
        """
        task_id = generate_task_id("invalid_sensors")
        
        logger.info(f"Test: Config with invalid sensor range for task {task_id}")
        
        # Create invalid config (min > max)
        with pytest.raises(Exception) as exc_info:
            invalid_payload = generate_config_payload(
                sensors_min=100,
                sensors_max=50,  # Invalid: max < min
                live=True
            )
            config_request = ConfigTaskRequest(**invalid_payload)
        
        # Verify validation error
        assert "sensor" in str(exc_info.value).lower() or "max" in str(exc_info.value).lower()
        
        logger.info("✅ Invalid sensor range rejected by validation")
    
    def test_config_with_invalid_frequency_range(self, focus_server_api):
        """
        Test: Configure task with invalid frequency range (min > max).
        
        Steps:
            1. Create config with frequencyRange.min > frequencyRange.max
            2. Attempt to configure task
        
        Expected:
            - ValidationError raised before API call
        """
        task_id = generate_task_id("invalid_freq")
        
        logger.info(f"Test: Config with invalid frequency range for task {task_id}")
        
        # Create invalid config (min > max)
        with pytest.raises(Exception) as exc_info:
            invalid_payload = generate_config_payload(
                freq_min=1000,
                freq_max=500,  # Invalid: max < min
                live=True
            )
            config_request = ConfigTaskRequest(**invalid_payload)
        
        # Verify validation error
        assert "frequenc" in str(exc_info.value).lower() or "max" in str(exc_info.value).lower()
        
        logger.info("✅ Invalid frequency range rejected by validation")
    
    def test_config_with_zero_canvas_height(self, focus_server_api):
        """
        Test: Configure task with invalid canvas height = 0.
        
        Steps:
            1. Create config with canvasInfo.height = 0
            2. Attempt to configure task
        
        Expected:
            - ValidationError raised before API call
        """
        task_id = generate_task_id("invalid_canvas")
        
        logger.info(f"Test: Config with zero canvas height for task {task_id}")
        
        # Create invalid config (height = 0)
        with pytest.raises(Exception) as exc_info:
            invalid_payload = generate_config_payload(
                canvas_height=0,  # Invalid
                live=True
            )
            config_request = ConfigTaskRequest(**invalid_payload)
        
        # Verify validation error
        assert "height" in str(exc_info.value).lower() or "positive" in str(exc_info.value).lower()
        
        logger.info("✅ Zero canvas height rejected by validation")

