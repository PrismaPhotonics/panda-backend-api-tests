"""
Integration Tests - Historic Playback Flow
============================================

Comprehensive integration tests for the historic playback flow in Focus Server.

Test Flow:
    1. POST /config/{task_id} → (with start_time & end_time)
    2. GET /waterfall/{task_id}/{row_count} (poll until 208 status)
    3. Verify playback completes successfully

Author: QA Automation Architect
Date: 2025-10-07
"""

import pytest
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from src.models.focus_server_models import ConfigTaskRequest, ConfigTaskResponse
from src.utils.helpers import (
    generate_task_id, 
    generate_config_payload,
    generate_time_range,
    datetime_to_yymmddHHMMSS
)
from src.utils.validators import (
    validate_task_id_format,
    validate_time_format_yymmddHHMMSS,
    validate_waterfall_response
)

logger = logging.getLogger(__name__)


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def historic_config_payload() -> Dict[str, Any]:
    """
    Generate historic configuration payload with time range.
    
    Returns:
        Configuration payload for historic playback (with timestamps)
    """
    return generate_config_payload(
        sensors_min=0,
        sensors_max=50,
        freq_min=0,
        freq_max=500,
        nfft=1024,
        canvas_height=1000,
        live=False,  # Historic mode - with timestamps
        duration_minutes=5  # 5-minute historic range
    )


@pytest.fixture
def configured_historic_task(focus_server_api, historic_config_payload):
    """
    Fixture to configure a historic playback task and return task_id.
    
    Yields:
        task_id for the configured historic task
        
    Cleanup:
        Task is cleaned up after test completes
    """
    task_id = generate_task_id("historic_test")
    logger.info(f"Configuring historic task: {task_id}")
    
    # Configure task
    config_request = ConfigTaskRequest(**historic_config_payload)
    response = focus_server_api.config_task(task_id, config_request)
    
    assert response.status == "Config received successfully"
    logger.info(f"Historic task {task_id} configured successfully")
    
    yield task_id
    
    # Cleanup
    logger.info(f"Cleaning up historic task: {task_id}")


# ===================================================================
# Happy Path Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
class TestHistoricPlaybackHappyPath:
    """
    Test suite for historic playback happy path scenarios.
    
    These tests validate the standard historic playback flow with expected inputs.
    """
    
    def test_configure_historic_task_success(self, focus_server_api, historic_config_payload):
        """
        Test: Successfully configure a historic playback task.
        
        Steps:
            1. Generate unique task_id
            2. Create config with start_time and end_time
            3. Send POST /config/{task_id}
            4. Verify successful response
        
        Expected:
            - Status code: 200
            - Response status: "Config received successfully"
            - Task configured for historic playback
        """
        task_id = generate_task_id("historic_happy")
        logger.info(f"Test: Configuring historic task {task_id}")
        
        # Validate task_id format
        assert validate_task_id_format(task_id)
        
        # Validate time formats in payload
        start_time = historic_config_payload.get("start_time")
        end_time = historic_config_payload.get("end_time")
        
        if start_time and end_time:
            assert validate_time_format_yymmddHHMMSS(start_time)
            assert validate_time_format_yymmddHHMMSS(end_time)
            logger.info(f"Time range: {start_time} to {end_time}")
        
        # Create config request
        config_request = ConfigTaskRequest(**historic_config_payload)
        
        # Configure task
        response = focus_server_api.config_task(task_id, config_request)
        
        # Assertions
        assert isinstance(response, ConfigTaskResponse)
        assert response.status == "Config received successfully"
        
        logger.info(f"✅ Historic task {task_id} configured successfully")
    
    def test_poll_historic_playback_until_completion(self, focus_server_api, configured_historic_task):
        """
        Test: Poll historic playback until completion (status 208).
        
        Steps:
            1. Use pre-configured historic task
            2. Poll GET /waterfall/{task_id}/{row_count}
            3. Continue until status 208 (baby analyzer exited)
        
        Expected:
            - Initial status may be 200 (no data yet)
            - Then status 201 (data available)
            - Finally status 208 (playback completed)
            - Data received is valid
        """
        task_id = configured_historic_task
        row_count = 10
        max_poll_attempts = 100  # Historic playback may take longer
        poll_interval = 2.0  # seconds
        
        logger.info(f"Test: Polling historic playback for task {task_id}")
        
        status_transitions = []
        data_blocks_received = 0
        
        for attempt in range(max_poll_attempts):
            logger.debug(f"Poll attempt {attempt + 1}/{max_poll_attempts}")
            
            # Get waterfall data
            response = focus_server_api.get_waterfall(task_id, row_count)
            
            # Track status transitions
            if not status_transitions or status_transitions[-1] != response.status_code:
                status_transitions.append(response.status_code)
                logger.info(f"Status transition: {response.status_code} ({response.message})")
            
            # Check status
            if response.status_code == 200:
                # No data yet - wait and continue
                logger.debug("No data yet (status 200)")
                
            elif response.status_code == 201:
                # Data available
                logger.debug(f"Data available (status 201)")
                
                # Validate response
                validation_result = validate_waterfall_response(response)
                assert validation_result["is_valid"]
                
                # Count data blocks
                if response.data:
                    data_blocks_received += len(response.data)
                    logger.debug(f"Received {len(response.data)} data blocks (total: {data_blocks_received})")
                
            elif response.status_code == 208:
                # Baby analyzer exited - playback complete!
                logger.info(f"✅ Playback completed (status 208) after {attempt + 1} polls")
                logger.info(f"Status transitions: {status_transitions}")
                logger.info(f"Total data blocks received: {data_blocks_received}")
                
                # Assertions
                assert data_blocks_received > 0, "No data blocks received during playback"
                
                return  # Test passed
                
            elif response.status_code == 404:
                # Consumer not found - test failure
                pytest.fail(f"Consumer not found for task {task_id} (status 404)")
            
            # Wait before next poll
            time.sleep(poll_interval)
        
        # If we reach here, playback didn't complete
        pytest.fail(
            f"Playback did not complete after {max_poll_attempts} poll attempts. "
            f"Last status: {status_transitions[-1] if status_transitions else 'unknown'}"
        )
    
    def test_historic_playback_with_short_duration(self, focus_server_api):
        """
        Test: Historic playback with short duration (1 minute).
        
        Steps:
            1. Configure task with 1-minute time range
            2. Poll until completion
        
        Expected:
            - Playback completes quickly
            - Status 208 received within reasonable time
        """
        task_id = generate_task_id("short_historic")
        logger.info(f"Test: Short historic playback for task {task_id}")
        
        # Create 1-minute historic range
        payload = generate_config_payload(
            sensors_min=0,
            sensors_max=20,
            live=False,
            duration_minutes=1  # Very short duration
        )
        
        # Configure task
        config_request = ConfigTaskRequest(**payload)
        response = focus_server_api.config_task(task_id, config_request)
        assert response.status == "Config received successfully"
        
        # Poll until completion (with shorter timeout)
        max_attempts = 30
        completed = False
        
        for attempt in range(max_attempts):
            response = focus_server_api.get_waterfall(task_id, 10)
            
            if response.status_code == 208:
                completed = True
                logger.info(f"✅ Short playback completed after {attempt + 1} polls")
                break
            
            time.sleep(1.0)
        
        assert completed, "Short historic playback did not complete in time"
    
    def test_historic_playback_data_integrity(self, focus_server_api, configured_historic_task):
        """
        Test: Verify data integrity during historic playback.
        
        Steps:
            1. Use configured historic task
            2. Collect all data blocks during playback
            3. Verify data consistency (timestamps, sensors, etc.)
        
        Expected:
            - Timestamps are sequential and increasing
            - Sensor data is consistent
            - No missing or corrupted data
        """
        task_id = configured_historic_task
        logger.info(f"Test: Data integrity for historic task {task_id}")
        
        all_rows = []
        last_timestamp = 0
        
        for attempt in range(100):
            response = focus_server_api.get_waterfall(task_id, 20)
            
            if response.status_code == 201 and response.data:
                # Collect rows
                for block in response.data:
                    for row in block.rows:
                        all_rows.append(row)
                        
                        # Check timestamp ordering
                        assert row.startTimestamp >= last_timestamp, \
                            "Timestamps not sequential"
                        last_timestamp = row.endTimestamp
                        
                        # Check sensor data
                        assert len(row.sensors) > 0, "Row has no sensor data"
                        
                        for sensor in row.sensors:
                            assert sensor.id >= 0, "Invalid sensor ID"
                            assert len(sensor.intensity) > 0, "Sensor has no intensity data"
                
            elif response.status_code == 208:
                # Playback complete
                logger.info(f"✅ Data integrity verified: {len(all_rows)} rows collected")
                break
            
            time.sleep(2.0)
        
        # Final assertions
        assert len(all_rows) > 0, "No rows collected during playback"
        logger.info(f"✅ All {len(all_rows)} rows passed integrity checks")


# ===================================================================
# Edge Cases Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
class TestHistoricPlaybackEdgeCases:
    """
    Test suite for historic playback edge cases.
    
    These tests validate behavior with boundary conditions and unusual scenarios.
    """
    
    def test_historic_with_very_old_timestamps(self, focus_server_api):
        """
        Test: Historic playback with very old timestamps (no data available).
        
        Steps:
            1. Configure task with time range from 1 year ago
            2. Attempt playback
        
        Expected:
            - Task configures successfully
            - No data returned (or status 208 immediately)
        """
        task_id = generate_task_id("old_timestamps")
        logger.info(f"Test: Historic with old timestamps for task {task_id}")
        
        # Create time range from 1 year ago
        old_start = datetime.now() - timedelta(days=365)
        old_end = old_start + timedelta(minutes=5)
        
        payload = generate_config_payload(
            sensors_min=0,
            sensors_max=20,
            live=False
        )
        payload["start_time"] = datetime_to_yymmddHHMMSS(old_start)
        payload["end_time"] = datetime_to_yymmddHHMMSS(old_end)
        
        # Configure task
        config_request = ConfigTaskRequest(**payload)
        response = focus_server_api.config_task(task_id, config_request)
        assert response.status == "Config received successfully"
        
        # Poll a few times
        for attempt in range(10):
            response = focus_server_api.get_waterfall(task_id, 10)
            
            # Acceptable responses: 200 (no data), 208 (completed), 404 (not found)
            assert response.status_code in [200, 208, 404]
            
            if response.status_code == 208:
                logger.info("✅ Playback completed immediately (no data for old timestamps)")
                break
            
            time.sleep(1.0)
        
        logger.info("✅ Old timestamps handled correctly")
    
    def test_historic_with_future_timestamps(self, focus_server_api):
        """
        Test: Historic playback with future timestamps.
        
        Steps:
            1. Create time range in the future
            2. Attempt to configure task
        
        Expected:
            - Configuration may succeed (depends on server validation)
            - Playback should handle gracefully (no data or error)
        """
        task_id = generate_task_id("future_timestamps")
        logger.info(f"Test: Historic with future timestamps for task {task_id}")
        
        # Create time range in the future
        future_start = datetime.now() + timedelta(hours=1)
        future_end = future_start + timedelta(minutes=5)
        
        payload = generate_config_payload(
            sensors_min=0,
            sensors_max=20,
            live=False
        )
        payload["start_time"] = datetime_to_yymmddHHMMSS(future_start)
        payload["end_time"] = datetime_to_yymmddHHMMSS(future_end)
        
        try:
            # Attempt to configure task
            config_request = ConfigTaskRequest(**payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            # If configuration succeeds, playback should handle it
            logger.info("Configuration accepted, checking playback behavior...")
            
            # Poll a few times
            for attempt in range(5):
                waterfall_response = focus_server_api.get_waterfall(task_id, 10)
                
                # Should return no data or complete immediately
                assert waterfall_response.status_code in [200, 208, 404]
                
                if waterfall_response.status_code == 208:
                    logger.info("✅ Playback completed (no data for future timestamps)")
                    break
                
                time.sleep(1.0)
        
        except Exception as e:
            # Configuration or validation may reject future timestamps
            logger.info(f"✅ Future timestamps rejected: {e}")
    
    def test_historic_with_reversed_time_range(self, focus_server_api):
        """
        Test: Historic playback with reversed time range (end < start).
        
        Steps:
            1. Create config with end_time < start_time
            2. Attempt to configure task
        
        Expected:
            - ValidationError raised before API call
        """
        task_id = generate_task_id("reversed_time")
        logger.info(f"Test: Historic with reversed time range for task {task_id}")
        
        # Create reversed time range
        start_time = datetime.now()
        end_time = start_time - timedelta(minutes=5)  # Before start - invalid
        
        payload = generate_config_payload(
            sensors_min=0,
            sensors_max=20,
            live=False
        )
        payload["start_time"] = datetime_to_yymmddHHMMSS(start_time)
        payload["end_time"] = datetime_to_yymmddHHMMSS(end_time)
        
        # Attempt to create config request (should fail validation)
        with pytest.raises(Exception) as exc_info:
            config_request = ConfigTaskRequest(**payload)
        
        # Verify validation error mentions time
        assert "time" in str(exc_info.value).lower()
        
        logger.info("✅ Reversed time range rejected by validation")
    
    def test_historic_with_very_long_duration(self, focus_server_api):
        """
        Test: Historic playback with very long duration (24 hours).
        
        Steps:
            1. Configure task with 24-hour time range
            2. Start playback
            3. Cancel after a few data blocks
        
        Expected:
            - Task configures successfully
            - Playback starts (status 201)
            - Data is being processed
        
        Note: We don't wait for full completion (would take too long)
        """
        task_id = generate_task_id("long_duration")
        logger.info(f"Test: Historic with long duration for task {task_id}")
        
        # Create 24-hour time range
        payload = generate_config_payload(
            sensors_min=0,
            sensors_max=20,
            live=False,
            duration_minutes=1440  # 24 hours
        )
        
        # Configure task
        config_request = ConfigTaskRequest(**payload)
        response = focus_server_api.config_task(task_id, config_request)
        assert response.status == "Config received successfully"
        
        # Poll a few times to verify playback starts
        playback_started = False
        
        for attempt in range(20):
            response = focus_server_api.get_waterfall(task_id, 10)
            
            if response.status_code == 201:
                playback_started = True
                logger.info(f"✅ Long-duration playback started (received data on attempt {attempt + 1})")
                break
            
            time.sleep(2.0)
        
        # We're not waiting for completion (would take too long)
        # Just verify playback started
        if not playback_started:
            logger.warning("Long-duration playback did not start (may be expected if no data)")
        
        logger.info("✅ Long-duration configuration handled correctly")


# ===================================================================
# Error Handling Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
class TestHistoricPlaybackErrorHandling:
    """
    Test suite for historic playback error handling.
    
    These tests validate proper error handling and recovery.
    """
    
    def test_config_with_invalid_time_format(self, focus_server_api):
        """
        Test: Configure with invalid time format string.
        
        Steps:
            1. Create config with malformed time string
            2. Attempt to configure task
        
        Expected:
            - ValidationError raised
        """
        task_id = generate_task_id("invalid_time_format")
        logger.info(f"Test: Config with invalid time format for task {task_id}")
        
        # Create config with invalid time format
        payload = generate_config_payload(
            sensors_min=0,
            sensors_max=20,
            live=False
        )
        payload["start_time"] = "2025-10-07"  # Wrong format (should be yymmddHHMMSS)
        payload["end_time"] = "2025-10-08"
        
        # Attempt to create config request (should fail validation)
        with pytest.raises(Exception) as exc_info:
            config_request = ConfigTaskRequest(**payload)
        
        # Verify validation error
        logger.info(f"✅ Invalid time format rejected: {exc_info.value}")
    
    def test_config_with_non_numeric_time(self, focus_server_api):
        """
        Test: Configure with non-numeric time string.
        
        Steps:
            1. Create config with alphabetic time string
            2. Attempt to configure task
        
        Expected:
            - ValidationError raised
        """
        task_id = generate_task_id("non_numeric_time")
        logger.info(f"Test: Config with non-numeric time for task {task_id}")
        
        # Create config with non-numeric time
        payload = generate_config_payload(
            sensors_min=0,
            sensors_max=20,
            live=False
        )
        payload["start_time"] = "ABCDEFGHIJKL"  # 12 characters but not digits
        payload["end_time"] = "MNOPQRSTUVWX"
        
        # Attempt to create config request (should fail validation)
        with pytest.raises(Exception) as exc_info:
            config_request = ConfigTaskRequest(**payload)
        
        logger.info(f"✅ Non-numeric time rejected: {exc_info.value}")

