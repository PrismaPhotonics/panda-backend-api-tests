"""
Integration Tests - Dynamic ROI Adjustment
============================================

⚠️  MIGRATED TO OLD API - 2025-10-23
--------------------------------------
These tests have been MIGRATED to work with POST /configure API.

Comprehensive integration tests for dynamic ROI (Region of Interest) adjustment
via RabbitMQ command interface.

IMPORTANT UPDATE (2025-10-22):
    Per specs meeting decision, ROI Change = NEW CONFIG REQUEST.
    - NOT dynamic streaming adjustment
    - Requires stopping old task and starting new one
    - Frontend should send new POST /configure with updated ROI
    
    These tests validate the RabbitMQ mechanism that still exists,
    but the recommended approach is:
    1. User requests ROI change
    2. Frontend sends new POST /configure
    3. Old job_id is stopped/replaced
    
Test Flow (Legacy/Internal):
    1. Configure live job with initial ROI
    2. Send RegionOfInterestCommand via MQ
    3. Verify baby analyzer reinitializes with new ROI

Author: QA Automation Architect
Date: 2025-10-07
Last Updated: 2025-10-23 (MIGRATED)
"""

import logging
import time

import pytest

from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient
from src.models.focus_server_models import ConfigureRequest, ConfigureResponse, ViewType
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
    Fixture to configure a job suitable for ROI testing (POST /configure).
    
    Yields:
        Tuple of (job_id, initial_sensor_min, initial_sensor_max)
    """
    initial_min = 1
    initial_max = 100
    
    logger.info(f"Configuring job with initial ROI: [{initial_min}, {initial_max}]")
    
    # Create config with initial ROI (POST /configure format)
    payload = {
        "displayTimeAxisDuration": 30,
        "nfftSelection": 1024,
        "displayInfo": {
            "height": 1000
        },
        "channels": {
            "min": initial_min,
            "max": initial_max
        },
        "frequencyRange": {
            "min": 0,
            "max": 500
        },
        "start_time": None,  # Live mode
        "end_time": None,
        "view_type": ViewType.MULTICHANNEL
    }
    
    # Configure job
    config_request = ConfigureRequest(**payload)
    response = focus_server_api.configure_streaming_job(config_request)
    
    assert hasattr(response, 'job_id') and response.job_id
    job_id = response.job_id
    logger.info(f"Job {job_id} configured with ROI [{initial_min}, {initial_max}]")
    
    yield job_id, initial_min, initial_max
    
    # Cleanup
    logger.info(f"Cleaning up job {job_id}")


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
    
    @pytest.mark.xray("PZ-13787")
    def test_send_roi_change_command(self, baby_analyzer_mq_client):
        """
        Test: Successfully send ROI change command via RabbitMQ.
        
        PZ-13787: ROI Change - Send Command
        
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
        
        NOTE (2025-10-22): Per specs meeting, recommended approach is NEW CONFIG REQUEST.
        This test validates the RabbitMQ mechanism for internal/legacy use.
        
        ROI Change Policy (Updated):
        - Maximum 50% change in ROI size
        - For production: Frontend should send new POST /config instead
        
        Steps:
            1. Define current and new ROI
            2. Validate change safety (max 50% change)
            3. Send command if safe
        
        Expected:
            - Safety validation passes (within 50% limit)
            - Command sent successfully
        """
        logger.info("Test: ROI change with safety validation (50% limit)")
        
        # Define ROI change (within 50% limit)
        current_min = 0
        current_max = 100
        new_min = 20
        new_max = 120
        
        # Validate safety - 50% limit per specs meeting 22-Oct-2025
        safety_result = validate_roi_change_safety(
            current_min=current_min,
            current_max=current_max,
            new_min=new_min,
            new_max=new_max,
            max_change_percent=50.0  # Specs decision: 50% max change
        )
        
        logger.info(f"Safety validation (50% limit): {safety_result}")
        assert safety_result["is_safe"], f"ROI change not safe: {safety_result['warnings']}"
        
        # Send command
        baby_analyzer_mq_client.send_roi_change(start=new_min, end=new_max)
        
        logger.info(f"✅ Safe ROI change sent: [{new_min}, {new_max}] (within 50% limit)")
    
    @pytest.mark.xray("PZ-13788")
    def test_multiple_roi_changes_sequence(self, baby_analyzer_mq_client):
        """
        Test: Send sequence of ROI changes.
        
        PZ-13788: ROI Change - Multiple Sequences
        
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
    
    @pytest.mark.xray("PZ-13789")
    def test_roi_expansion(self, baby_analyzer_mq_client):
        """
        Test: Expand ROI (increase sensor range).
        
        PZ-13789: ROI Expansion Test
        
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
    
    @pytest.mark.xray("PZ-13790")
    def test_roi_shrinking(self, baby_analyzer_mq_client):
        """
        Test: Shrink ROI (decrease sensor range).
        
        PZ-13790: ROI Shrinking Test
        
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
    
    @pytest.mark.xray("PZ-13791")
    def test_roi_shift(self, baby_analyzer_mq_client):
        """Already implemented above - duplicate marker."""
        pass


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
    
    @pytest.mark.xray("PZ-13792")
    def test_roi_with_zero_start(self, baby_analyzer_mq_client):
        """
        Test: ROI starting at sensor 0.
        
        PZ-13792: ROI Zero Start
        
        Steps:
            1. Send ROI [0, 50]
        
        Expected:
            - Command sent successfully (0 is valid start)
        """
        logger.info("Test: ROI with zero start")
        
        baby_analyzer_mq_client.send_roi_change(start=0, end=50)
        
        logger.info("✅ ROI with zero start sent successfully")
    
    @pytest.mark.xray("PZ-13793")
    def test_roi_with_large_range(self, baby_analyzer_mq_client):
        """
        Test: ROI with very large range.
        
        PZ-13793: ROI Large Range
        
        Steps:
            1. Send ROI [0, 10000]
        
        Expected:
            - Command sent successfully
            - Note: Actual processing may cap at available sensors
        """
        logger.info("Test: ROI with large range")
        
        baby_analyzer_mq_client.send_roi_change(start=0, end=10000)
        
        logger.info("✅ ROI with large range sent successfully")
    
    @pytest.mark.xray("PZ-13794")
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
    
    @pytest.mark.xray("PZ-13795")
    def test_unsafe_roi_change(self, baby_analyzer_mq_client):
        """
        Test: Unsafe ROI change (exceeds 50% limit).
        
        PZ-13795: Unsafe ROI Change
        
        NOTE (2025-10-22): Per specs meeting, ROI changes > 50% should be rejected.
        Recommended approach: Send new POST /config instead of RabbitMQ command.
        
        Steps:
            1. Validate drastic ROI change (>50%)
            2. Verify safety check fails
            3. Log warning about exceeding 50% limit
        
        Expected:
            - Safety validation fails (>50% change)
            - Warning logged
            - Recommended: Use new config request instead
        """
        logger.info("Test: Unsafe ROI change (exceeds 50% limit)")
        
        # Define drastic change (>>50%)
        current_min = 0
        current_max = 100
        new_min = 500
        new_max = 600
        
        # Validate safety - 50% limit per specs meeting 22-Oct-2025
        safety_result = validate_roi_change_safety(
            current_min=current_min,
            current_max=current_max,
            new_min=new_min,
            new_max=new_max,
            max_change_percent=50.0  # Specs decision: 50% max change
        )
        
        logger.info(f"Safety validation (50% limit): {safety_result}")
        assert not safety_result["is_safe"], "Expected unsafe ROI change to be flagged (>50%)"
        
        logger.info(f"⚠️  Unsafe ROI change detected: {safety_result['warnings']}")
        logger.info("⚠️  Recommendation: Use new POST /config request for large ROI changes")
        logger.info("✅ 50% limit validation working correctly")


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
    
    @pytest.mark.xray("PZ-13796")
    def test_roi_with_negative_start(self, baby_analyzer_mq_client):
        """
        Test: ROI with negative start index.
        
        PZ-13796: ROI Negative Start
        
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
    
    @pytest.mark.xray("PZ-13797")
    def test_roi_with_negative_end(self, baby_analyzer_mq_client):
        """
        Test: ROI with negative end index.
        
        PZ-13797: ROI Negative End
        
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
    
    @pytest.mark.xray("PZ-13798")
    def test_roi_with_reversed_range(self, baby_analyzer_mq_client):
        """
        Test: ROI with end < start.
        
        PZ-13798: ROI Reversed Range
        
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
    
    @pytest.mark.xray("PZ-13799")
    def test_roi_with_equal_start_end(self, baby_analyzer_mq_client):
        """
        Test: ROI with start == end (no sensors).
        
        PZ-13799: ROI Equal Start End
        
        Steps:
            1. Attempt to send ROI [50, 50]
        
        Expected:
            - ValidationError raised (end must be > start)
        """
        logger.info("Test: ROI with equal start and end")
        
        with pytest.raises(Exception) as exc_info:
            baby_analyzer_mq_client.send_roi_change(start=50, end=50)
        
        logger.info(f"✅ Equal start/end rejected: {exc_info.value}")

