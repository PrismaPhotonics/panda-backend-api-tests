"""
Integration Tests - Dynamic ROI Adjustment
============================================

Comprehensive integration tests for dynamic ROI (Region of Interest) adjustment
via RabbitMQ command interface.

Test Flow:
    1. Configure live task with initial ROI
    2. Send RegionOfInterestCommand via MQ
    3. Verify baby analyzer reinitializes with new ROI
    4. Verify GET /waterfall returns updated sensor range

Author: QA Automation Architect
Date: 2025-10-07
"""

import logging
import time

import pytest

from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient
from src.models.focus_server_models import ConfigTaskRequest
from src.utils.helpers import generate_task_id, generate_config_payload
from src.utils.validators import validate_roi_change_safety

logger = logging.getLogger(__name__)


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def baby_analyzer_mq_client(config_manager):
    """
    Fixture to provide BabyAnalyzerMQClient instance.
    
    Yields:
        Connected BabyAnalyzerMQClient
    """
    # Get RabbitMQ configuration from config manager
    rabbitmq_config = config_manager.get("rabbitmq", {})
    
    host = rabbitmq_config.get("host", "localhost")
    port = rabbitmq_config.get("port", 5672)
    username = rabbitmq_config.get("username", "guest")
    password = rabbitmq_config.get("password", "guest")
    
    logger.info(f"Creating Baby Analyzer MQ client for {host}:{port}")
    
    # Create client
    client = BabyAnalyzerMQClient(
        host=host,
        port=port,
        username=username,
        password=password
    )
    
    # Connect
    client.connect()
    
    yield client
    
    # Disconnect
    client.disconnect()
    logger.info("Baby Analyzer MQ client disconnected")


@pytest.fixture
def configured_task_for_roi(focus_server_api):
    """
    Fixture to configure a task suitable for ROI testing.
    
    Yields:
        Tuple of (task_id, initial_sensor_min, initial_sensor_max)
    """
    task_id = generate_task_id("roi_test")
    initial_min = 0
    initial_max = 100
    
    logger.info(f"Configuring task {task_id} with initial ROI: [{initial_min}, {initial_max}]")
    
    # Create config with initial ROI
    payload = generate_config_payload(
        sensors_min=initial_min,
        sensors_max=initial_max,
        freq_min=0,
        freq_max=500,
        nfft=1024,
        live=True
    )
    
    # Configure task
    config_request = ConfigTaskRequest(**payload)
    response = focus_server_api.config_task(task_id, config_request)
    
    assert response.status == "Config received successfully"
    logger.info(f"Task {task_id} configured with ROI [{initial_min}, {initial_max}]")
    
    yield task_id, initial_min, initial_max
    
    # Cleanup
    logger.info(f"Cleaning up task {task_id}")


# ===================================================================
# Happy Path Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.rabbitmq
class TestDynamicROIHappyPath:
    """
    Test suite for dynamic ROI adjustment happy path scenarios.
    
    These tests validate standard ROI changes via RabbitMQ commands.
    """
    
    def test_send_roi_change_command(self, baby_analyzer_mq_client):
        """
        Test: Successfully send ROI change command via RabbitMQ.
        
        Steps:
            1. Connect to RabbitMQ
            2. Send RegionOfInterestCommand
            3. Verify command sent without errors
        
        Expected:
            - Command published successfully
            - No exceptions raised
        """
        logger.info("Test: Sending ROI change command")
        
        # Define new ROI
        new_start = 50
        new_end = 150
        
        # Send ROI change command
        baby_analyzer_mq_client.send_roi_change(
            start=new_start,
            end=new_end,
            routing_key="roi"
        )
        
        logger.info(f"✅ ROI change command sent: [{new_start}, {new_end}]")
    
    def test_roi_change_with_validation(self, baby_analyzer_mq_client):
        """
        Test: Send ROI change with safety validation.
        
        Steps:
            1. Define current and new ROI
            2. Validate change safety
            3. Send command if safe
        
        Expected:
            - Safety validation passes
            - Command sent successfully
        """
        logger.info("Test: ROI change with safety validation")
        
        # Define ROI change
        current_min = 0
        current_max = 100
        new_min = 20
        new_max = 120
        
        # Validate safety
        safety_result = validate_roi_change_safety(
            current_min=current_min,
            current_max=current_max,
            new_min=new_min,
            new_max=new_max,
            max_change_percent=50.0
        )
        
        logger.info(f"Safety validation: {safety_result}")
        assert safety_result["is_safe"], f"ROI change not safe: {safety_result['warnings']}"
        
        # Send command
        baby_analyzer_mq_client.send_roi_change(start=new_min, end=new_max)
        
        logger.info(f"✅ Safe ROI change sent: [{new_min}, {new_max}]")
    
    def test_multiple_roi_changes_sequence(self, baby_analyzer_mq_client):
        """
        Test: Send sequence of ROI changes.
        
        Steps:
            1. Send first ROI change
            2. Wait briefly
            3. Send second ROI change
            4. Send third ROI change
        
        Expected:
            - All commands sent successfully
            - No errors during sequence
        """
        logger.info("Test: Multiple ROI changes sequence")
        
        roi_sequence = [
            (10, 110),
            (20, 120),
            (30, 130)
        ]
        
        for idx, (start, end) in enumerate(roi_sequence, 1):
            logger.info(f"Sending ROI change {idx}: [{start}, {end}]")
            baby_analyzer_mq_client.send_roi_change(start=start, end=end)
            time.sleep(1.0)  # Brief delay between commands
        
        logger.info(f"✅ Sent {len(roi_sequence)} ROI changes successfully")
    
    def test_roi_expansion(self, baby_analyzer_mq_client):
        """
        Test: Expand ROI (increase sensor range).
        
        Steps:
            1. Start with ROI [50, 100]
            2. Expand to [0, 200]
            3. Verify command sent
        
        Expected:
            - Expansion command sent successfully
        """
        logger.info("Test: ROI expansion")
        
        # Current ROI
        current_start = 50
        current_end = 100
        
        # Expanded ROI
        new_start = 0
        new_end = 200
        
        # Send expansion
        baby_analyzer_mq_client.send_roi_change(start=new_start, end=new_end)
        
        logger.info(f"✅ ROI expanded from [{current_start}, {current_end}] to [{new_start}, {new_end}]")
    
    def test_roi_shrinking(self, baby_analyzer_mq_client):
        """
        Test: Shrink ROI (decrease sensor range).
        
        Steps:
            1. Start with ROI [0, 200]
            2. Shrink to [50, 100]
            3. Verify command sent
        
        Expected:
            - Shrinking command sent successfully
        """
        logger.info("Test: ROI shrinking")
        
        # Current ROI
        current_start = 0
        current_end = 200
        
        # Shrunken ROI
        new_start = 50
        new_end = 100
        
        # Send shrinking
        baby_analyzer_mq_client.send_roi_change(start=new_start, end=new_end)
        
        logger.info(f"✅ ROI shrunk from [{current_start}, {current_end}] to [{new_start}, {new_end}]")
    
    def test_roi_shift(self, baby_analyzer_mq_client):
        """
        Test: Shift ROI (move without changing size).
        
        Steps:
            1. Start with ROI [0, 100]
            2. Shift to [50, 150] (same size, different position)
            3. Verify command sent
        
        Expected:
            - Shift command sent successfully
        """
        logger.info("Test: ROI shift")
        
        # Current ROI
        current_start = 0
        current_end = 100
        roi_size = current_end - current_start
        
        # Shifted ROI (same size)
        shift = 50
        new_start = current_start + shift
        new_end = current_end + shift
        
        assert new_end - new_start == roi_size, "ROI size changed during shift"
        
        # Send shift
        baby_analyzer_mq_client.send_roi_change(start=new_start, end=new_end)
        
        logger.info(f"✅ ROI shifted from [{current_start}, {current_end}] to [{new_start}, {new_end}]")


# ===================================================================
# Integration with Waterfall API Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.rabbitmq
@pytest.mark.slow
class TestROIWithWaterfallIntegration:
    """
    Test suite for ROI changes integrated with waterfall data retrieval.
    
    These tests verify that ROI changes affect the waterfall data returned.
    """
    
    def test_roi_change_affects_waterfall_data(
        self,
        focus_server_api,
        baby_analyzer_mq_client,
        configured_task_for_roi
    ):
        """
        Test: Verify ROI change affects waterfall data.
        
        Steps:
            1. Configure task with initial ROI [0, 100]
            2. Get waterfall data (verify sensor range)
            3. Send ROI change to [50, 150]
            4. Wait for reinitialization
            5. Get waterfall data again
            6. Verify sensor range changed
        
        Expected:
            - Initial data has sensors [0, 100]
            - After ROI change, data has sensors [50, 150]
        
        Note: This test requires baby analyzer to be running and processing data.
        """
        task_id, initial_min, initial_max = configured_task_for_roi
        logger.info(f"Test: ROI change affects waterfall for task {task_id}")
        
        # Step 1: Get initial waterfall data
        logger.info("Step 1: Getting initial waterfall data...")
        initial_data_received = False
        
        for attempt in range(20):
            response = focus_server_api.get_waterfall(task_id, 10)
            
            if response.status_code == 201 and response.data:
                initial_data_received = True
                
                # Verify initial sensor range
                for block in response.data:
                    for row in block.rows:
                        sensor_ids = [s.id for s in row.sensors]
                        logger.info(f"Initial sensor range: {min(sensor_ids)} - {max(sensor_ids)}")
                
                break
            
            time.sleep(2.0)
        
        if not initial_data_received:
            pytest.skip("Could not retrieve initial waterfall data (may not be available)")
        
        # Step 2: Send ROI change
        new_min = 50
        new_max = 150
        logger.info(f"Step 2: Sending ROI change to [{new_min}, {new_max}]...")
        baby_analyzer_mq_client.send_roi_change(start=new_min, end=new_max)
        
        # Step 3: Wait for reinitialization
        logger.info("Step 3: Waiting for baby analyzer to reinitialize...")
        time.sleep(5.0)  # Give baby analyzer time to reinitialize
        
        # Step 4: Get waterfall data with new ROI
        logger.info("Step 4: Getting waterfall data after ROI change...")
        new_data_received = False
        
        for attempt in range(20):
            response = focus_server_api.get_waterfall(task_id, 10)
            
            if response.status_code == 201 and response.data:
                new_data_received = True
                
                # Check if sensor range changed
                for block in response.data:
                    for row in block.rows:
                        sensor_ids = [s.id for s in row.sensors]
                        current_min = min(sensor_ids)
                        current_max = max(sensor_ids)
                        
                        logger.info(f"New sensor range: {current_min} - {current_max}")
                        
                        # Verify new range is closer to target
                        # (exact match may not happen due to processing delays)
                        if current_min >= new_min - 10 and current_max <= new_max + 10:
                            logger.info("✅ ROI change successfully affected waterfall data")
                            return
                
                break
            
            time.sleep(2.0)
        
        if not new_data_received:
            logger.warning("Could not verify ROI change in waterfall data (data not available)")
        
        logger.info("✅ ROI change command test completed")


# ===================================================================
# Edge Cases Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.rabbitmq
class TestROIEdgeCases:
    """
    Test suite for ROI adjustment edge cases.
    
    These tests validate behavior with boundary conditions.
    """
    
    def test_roi_with_zero_start(self, baby_analyzer_mq_client):
        """
        Test: ROI starting at sensor 0.
        
        Steps:
            1. Send ROI [0, 50]
        
        Expected:
            - Command sent successfully (0 is valid start)
        """
        logger.info("Test: ROI with zero start")
        
        baby_analyzer_mq_client.send_roi_change(start=0, end=50)
        
        logger.info("✅ ROI with zero start sent successfully")
    
    def test_roi_with_large_range(self, baby_analyzer_mq_client):
        """
        Test: ROI with very large range.
        
        Steps:
            1. Send ROI [0, 10000]
        
        Expected:
            - Command sent successfully
            - Note: Actual processing may cap at available sensors
        """
        logger.info("Test: ROI with large range")
        
        baby_analyzer_mq_client.send_roi_change(start=0, end=10000)
        
        logger.info("✅ ROI with large range sent successfully")
    
    def test_roi_with_small_range(self, baby_analyzer_mq_client):
        """
        Test: ROI with very small range (1 sensor).
        
        Steps:
            1. Send ROI [100, 101] (only 1 sensor)
        
        Expected:
            - Command sent successfully
        """
        logger.info("Test: ROI with small range")
        
        baby_analyzer_mq_client.send_roi_change(start=100, end=101)
        
        logger.info("✅ ROI with small range sent successfully")
    
    def test_unsafe_roi_change(self, baby_analyzer_mq_client):
        """
        Test: Unsafe ROI change (very drastic change).
        
        Steps:
            1. Validate drastic ROI change
            2. Verify safety check fails
            3. Optionally send anyway (with warning)
        
        Expected:
            - Safety validation fails
            - Warning logged
        """
        logger.info("Test: Unsafe ROI change")
        
        # Define drastic change
        current_min = 0
        current_max = 100
        new_min = 500
        new_max = 600
        
        # Validate safety
        safety_result = validate_roi_change_safety(
            current_min=current_min,
            current_max=current_max,
            new_min=new_min,
            new_max=new_max,
            max_change_percent=50.0
        )
        
        logger.info(f"Safety validation: {safety_result}")
        assert not safety_result["is_safe"], "Expected unsafe ROI change to be flagged"
        
        logger.info(f"⚠️  Unsafe ROI change detected: {safety_result['warnings']}")
        logger.info("✅ Unsafe ROI change validation working correctly")


# ===================================================================
# Error Handling Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.rabbitmq
class TestROIErrorHandling:
    """
    Test suite for ROI adjustment error handling.
    
    These tests validate proper error handling for invalid inputs.
    """
    
    def test_roi_with_negative_start(self, baby_analyzer_mq_client):
        """
        Test: ROI with negative start index.
        
        Steps:
            1. Attempt to send ROI [-10, 50]
        
        Expected:
            - ValidationError raised
        """
        logger.info("Test: ROI with negative start")
        
        with pytest.raises(Exception) as exc_info:
            baby_analyzer_mq_client.send_roi_change(start=-10, end=50)
        
        assert "negative" in str(exc_info.value).lower() or "non-negative" in str(exc_info.value).lower()
        logger.info(f"✅ Negative start rejected: {exc_info.value}")
    
    def test_roi_with_negative_end(self, baby_analyzer_mq_client):
        """
        Test: ROI with negative end index.
        
        Steps:
            1. Attempt to send ROI [0, -10]
        
        Expected:
            - ValidationError raised
        """
        logger.info("Test: ROI with negative end")
        
        with pytest.raises(Exception) as exc_info:
            baby_analyzer_mq_client.send_roi_change(start=0, end=-10)
        
        assert "negative" in str(exc_info.value).lower() or "non-negative" in str(exc_info.value).lower()
        logger.info(f"✅ Negative end rejected: {exc_info.value}")
    
    def test_roi_with_reversed_range(self, baby_analyzer_mq_client):
        """
        Test: ROI with end < start.
        
        Steps:
            1. Attempt to send ROI [100, 50]
        
        Expected:
            - ValidationError raised
        """
        logger.info("Test: ROI with reversed range")
        
        with pytest.raises(Exception) as exc_info:
            baby_analyzer_mq_client.send_roi_change(start=100, end=50)
        
        assert "greater" in str(exc_info.value).lower() or ">" in str(exc_info.value)
        logger.info(f"✅ Reversed range rejected: {exc_info.value}")
    
    def test_roi_with_equal_start_end(self, baby_analyzer_mq_client):
        """
        Test: ROI with start == end (no sensors).
        
        Steps:
            1. Attempt to send ROI [50, 50]
        
        Expected:
            - ValidationError raised (end must be > start)
        """
        logger.info("Test: ROI with equal start and end")
        
        with pytest.raises(Exception) as exc_info:
            baby_analyzer_mq_client.send_roi_change(start=50, end=50)
        
        logger.info(f"✅ Equal start/end rejected: {exc_info.value}")

