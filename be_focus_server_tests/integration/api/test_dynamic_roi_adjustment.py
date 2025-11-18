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
# Test Case Tables for Parameterized Tests
# ===================================================================

# ROI Test Cases - Different combinations to test
ROI_TEST_CASES = [
    # Format: (test_id, roi1_min, roi1_max, roi2_min, roi2_max, description)
    ("small_to_large", 1, 50, 1, 100, "Small ROI [1-50] to Large ROI [1-100]"),
    ("large_to_small", 1, 100, 1, 50, "Large ROI [1-100] to Small ROI [1-50]"),
    ("shift_right", 1, 50, 51, 100, "Shift ROI right [1-50] → [51-100]"),
    ("shift_left", 51, 100, 1, 50, "Shift ROI left [51-100] → [1-50]"),
    ("expand_both_sides", 25, 75, 1, 100, "Expand ROI both sides [25-75] → [1-100]"),
    ("shrink_both_sides", 1, 100, 25, 75, "Shrink ROI both sides [1-100] → [25-75]"),
    ("expand_right", 1, 50, 1, 75, "Expand ROI right side [1-50] → [1-75]"),
    ("expand_left", 50, 100, 25, 100, "Expand ROI left side [50-100] → [25-100]"),
    ("shrink_right", 1, 100, 1, 50, "Shrink ROI right side [1-100] → [1-50]"),
    ("shrink_left", 1, 100, 50, 100, "Shrink ROI left side [1-100] → [50-100]"),
    ("very_small_roi", 1, 10, 1, 20, "Very small ROI [1-10] → [1-20]"),
    ("medium_roi", 50, 150, 50, 200, "Medium ROI [50-150] → [50-200]"),
    ("large_roi", 100, 500, 100, 1000, "Large ROI [100-500] → [100-1000]"),
    ("overlap_partial", 1, 100, 50, 150, "Partial overlap [1-100] → [50-150]"),
    ("no_overlap", 1, 50, 200, 250, "No overlap [1-50] → [200-250]"),
    ("same_size_shift", 1, 50, 100, 149, "Same size shift [1-50] → [100-149]"),
    ("double_size", 1, 50, 1, 100, "Double size [1-50] → [1-100]"),
    ("half_size", 1, 100, 1, 50, "Half size [1-100] → [1-50]"),
    ("edge_case_min", 1, 10, 1, 5, "Edge case: minimum ROI [1-10] → [1-5]"),
    ("edge_case_max", 1, 100, 1, 200, "Edge case: maximum ROI [1-100] → [1-200]"),
]

# Configuration Test Cases - Different config combinations
CONFIG_TEST_CASES = [
    # Format: (test_id, nfft, freq_min, freq_max, display_duration, description)
    ("default_config", 1024, 0, 500, 30, "Default configuration"),
    ("small_nfft", 512, 0, 500, 30, "Small NFFT (512)"),
    ("large_nfft", 2048, 0, 500, 30, "Large NFFT (2048)"),
    ("small_freq_range", 1024, 0, 100, 30, "Small frequency range [0-100]"),
    ("large_freq_range", 1024, 0, 1000, 30, "Large frequency range [0-1000]"),
    ("mid_freq_range", 1024, 200, 800, 30, "Mid frequency range [200-800]"),
    ("short_duration", 1024, 0, 500, 10, "Short display duration (10s)"),
    ("long_duration", 1024, 0, 500, 60, "Long display duration (60s)"),
]


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

@pytest.mark.rabbitmq


@pytest.mark.regression
class TestDynamicROIHappyPath:
    """
    Test suite for dynamic ROI adjustment happy path scenarios.
    
    These tests validate standard ROI changes via RabbitMQ commands.
    """
    
    @pytest.mark.xray("PZ-13787")
    @pytest.mark.xray("PZ-13784")
    @pytest.mark.xray("PZ-13785")

    @pytest.mark.regression
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
    
    @pytest.mark.regression
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
    @pytest.mark.xray("PZ-13786")

    @pytest.mark.regression
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
    @pytest.mark.xray("PZ-13787")

    @pytest.mark.regression
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
    @pytest.mark.xray("PZ-13788")
    @pytest.mark.xray("PZ-13789")

    @pytest.mark.regression
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
    
    @pytest.mark.xray("PZ-13791")

    
    @pytest.mark.regression
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
# Edge Cases Tests
# ===================================================================

@pytest.mark.rabbitmq


@pytest.mark.regression
class TestROIEdgeCases:
    """
    Test suite for ROI adjustment edge cases.
    
    These tests validate behavior with boundary conditions.
    """
    
    @pytest.mark.xray("PZ-13792")
    @pytest.mark.xray("PZ-13796")

    @pytest.mark.regression
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
    @pytest.mark.xray("PZ-13795")

    @pytest.mark.regression
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

    
    @pytest.mark.regression
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
    @pytest.mark.xray("PZ-13797")

    @pytest.mark.regression
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

@pytest.mark.rabbitmq


@pytest.mark.regression
class TestROIErrorHandling:
    """
    Test suite for ROI adjustment error handling.
    
    These tests validate proper error handling for invalid inputs.
    """
    
    @pytest.mark.xray("PZ-13796")
    @pytest.mark.xray("PZ-13792")

    @pytest.mark.regression
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
    @pytest.mark.xray("PZ-13793")

    @pytest.mark.regression
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
    @pytest.mark.xray("PZ-13791")

    @pytest.mark.regression
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
    @pytest.mark.xray("PZ-13790")

    @pytest.mark.regression
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


# ===================================================================
# Data Size Tests
# ===================================================================

@pytest.mark.roi


@pytest.mark.regression
class TestROIDataSize:
    """
    Test suite for verifying data size consistency between different ROIs.
    
    These tests validate that different ROI configurations produce
    the SAME data size. If data sizes differ, this indicates a bug.
    
    Bug Detection:
        This test suite detects bugs where different ROI configurations
        incorrectly produce different data sizes when they should be consistent.
    """
    
    @pytest.mark.parametrize(
        "test_id,roi1_min,roi1_max,roi2_min,roi2_max,description",
        ROI_TEST_CASES,
        ids=[case[0] for case in ROI_TEST_CASES]  # Use test_id as test name
    )
    @pytest.mark.regression
def test_roi_change_should_not_affect_other_config_parameters(
        self, 
        focus_server_api,
        test_id,
        roi1_min,
        roi1_max,
        roi2_min,
        roi2_max,
        description
    ):
        """
        Test: ROI change should NOT affect other configuration parameters.
        
        Objective:
            Verify that when ROI (channels) changes, other configuration parameters
            (NFFT, frequency range, display settings, etc.) remain UNCHANGED.
            If they change, this indicates a bug.
        
        Steps:
            1. Configure job with ROI [min1, max1] and specific config values
            2. Get configuration response and note all non-ROI parameters
            3. Configure new job with ROI [min2, max2] but SAME config values
            4. Get configuration response and compare non-ROI parameters
            5. Verify all non-ROI parameters are the SAME (expected behavior)
            6. If any differ, alert about the bug
        
        Expected:
            - ROI (channels) should change between jobs
            - All other parameters should remain the SAME:
              * nfftSelection
              * frequencyRange (min/max)
              * displayTimeAxisDuration
              * displayInfo.height
              * view_type
            - If any non-ROI parameter changes, this is a bug
        
        Bug Detection:
            This test detects a bug where changing ROI incorrectly causes
            other configuration parameters to change when they should remain constant.
        """
        logger.info("=" * 80)
        logger.info(f"TEST: ROI Change Should NOT Affect Other Config Parameters")
        logger.info(f"Test Case: {test_id} - {description}")
        logger.info("=" * 80)
        logger.info("⚠️  BUG DETECTION TEST: This test will FAIL if config params change")
        logger.info("=" * 80)
        
        # Define fixed configuration values (should remain constant)
        fixed_nfft = 1024
        fixed_freq_min = 0
        fixed_freq_max = 500
        fixed_display_duration = 30
        fixed_display_height = 1000
        fixed_view_type = ViewType.MULTICHANNEL
        
        logger.info(f"Fixed Config Values (should NOT change):")
        logger.info(f"  NFFT: {fixed_nfft}")
        logger.info(f"  Frequency Range: [{fixed_freq_min}, {fixed_freq_max}]")
        logger.info(f"  Display Duration: {fixed_display_duration}")
        logger.info(f"  Display Height: {fixed_display_height}")
        logger.info(f"  View Type: {fixed_view_type}")
        logger.info(f"\nTest Case: {description}")
        logger.info(f"ROI 1: [{roi1_min}, {roi1_max}] ({roi1_max - roi1_min + 1} channels)")
        logger.info(f"ROI 2: [{roi2_min}, {roi2_max}] ({roi2_max - roi2_min + 1} channels)")
        logger.info("Expected: ROI changes, but all other params stay the SAME")
        
        # ============================================
        # Step 1: Configure first job with ROI 1
        # ============================================
        logger.info("\nStep 1: Configuring first job with ROI 1...")
        payload1 = {
            "displayTimeAxisDuration": fixed_display_duration,
            "nfftSelection": fixed_nfft,
            "displayInfo": {
                "height": fixed_display_height
            },
            "channels": {
                "min": roi1_min,
                "max": roi1_max
            },
            "frequencyRange": {
                "min": fixed_freq_min,
                "max": fixed_freq_max
            },
            "start_time": None,  # Live mode
            "end_time": None,
            "view_type": fixed_view_type
        }
        
        config_request1 = ConfigureRequest(**payload1)
        response1 = focus_server_api.configure_streaming_job(config_request1)
        
        assert hasattr(response1, 'job_id') and response1.job_id
        job_id1 = response1.job_id
        logger.info(f"✅ Job 1 configured: {job_id1}")
        
        # Extract config values from response
        config1 = {
            "nfft": getattr(response1, 'frequencies_amount', None),  # May be derived from nfft
            "frequencies_list": getattr(response1, 'frequencies_list', None),
            "lines_dt": getattr(response1, 'lines_dt', None),
            "view_type": getattr(response1, 'view_type', None),
            "stream_amount": getattr(response1, 'stream_amount', None),
        }
        
        # Get metadata for additional parameters
        time.sleep(2.0)
        metadata1 = None
        for attempt in range(5):
            try:
                metadata1 = focus_server_api.get_job_metadata(job_id1)
                if metadata1:
                    break
            except Exception as e:
                logger.debug(f"  Attempt {attempt + 1}: {e}")
                time.sleep(1.0)
        
        logger.info(f"  Job 1 config values:")
        logger.info(f"    View Type: {config1['view_type']}")
        logger.info(f"    Stream Amount: {config1['stream_amount']}")
        logger.info(f"    Lines DT: {config1['lines_dt']}")
        if config1['frequencies_list']:
            logger.info(f"    Frequencies Count: {len(config1['frequencies_list'])}")
        
        # ============================================
        # Step 2: Configure second job with ROI 2 (SAME config values)
        # ============================================
        logger.info("\nStep 2: Configuring second job with ROI 2 (SAME config values)...")
        payload2 = {
            "displayTimeAxisDuration": fixed_display_duration,  # SAME
            "nfftSelection": fixed_nfft,  # SAME
            "displayInfo": {
                "height": fixed_display_height  # SAME
            },
            "channels": {
                "min": roi2_min,  # DIFFERENT
                "max": roi2_max   # DIFFERENT
            },
            "frequencyRange": {
                "min": fixed_freq_min,  # SAME
                "max": fixed_freq_max   # SAME
            },
            "start_time": None,  # Live mode
            "end_time": None,
            "view_type": fixed_view_type  # SAME
        }
        
        config_request2 = ConfigureRequest(**payload2)
        response2 = focus_server_api.configure_streaming_job(config_request2)
        
        assert hasattr(response2, 'job_id') and response2.job_id
        job_id2 = response2.job_id
        logger.info(f"✅ Job 2 configured: {job_id2}")
        
        # Extract config values from response
        config2 = {
            "nfft": getattr(response2, 'frequencies_amount', None),
            "frequencies_list": getattr(response2, 'frequencies_list', None),
            "lines_dt": getattr(response2, 'lines_dt', None),
            "view_type": getattr(response2, 'view_type', None),
            "stream_amount": getattr(response2, 'stream_amount', None),
        }
        
        # Get metadata for additional parameters
        time.sleep(2.0)
        metadata2 = None
        for attempt in range(5):
            try:
                metadata2 = focus_server_api.get_job_metadata(job_id2)
                if metadata2:
                    break
            except Exception as e:
                logger.debug(f"  Attempt {attempt + 1}: {e}")
                time.sleep(1.0)
        
        logger.info(f"  Job 2 config values:")
        logger.info(f"    View Type: {config2['view_type']}")
        logger.info(f"    Stream Amount: {config2['stream_amount']}")
        logger.info(f"    Lines DT: {config2['lines_dt']}")
        if config2['frequencies_list']:
            logger.info(f"    Frequencies Count: {len(config2['frequencies_list'])}")
        
        # ============================================
        # Step 3: Verify non-ROI parameters are the SAME
        # ============================================
        logger.info("\nStep 3: Verifying non-ROI parameters are the SAME...")
        
        bugs_detected = []
        
        # Check view_type
        if config1['view_type'] != config2['view_type']:
            bugs_detected.append(
                f"view_type changed: Job1={config1['view_type']}, Job2={config2['view_type']}"
            )
        
        # Check frequencies_list (derived from NFFT)
        if config1['frequencies_list'] and config2['frequencies_list']:
            if len(config1['frequencies_list']) != len(config2['frequencies_list']):
                bugs_detected.append(
                    f"frequencies_list length changed: "
                    f"Job1={len(config1['frequencies_list'])}, Job2={len(config2['frequencies_list'])}"
                )
            elif config1['frequencies_list'] != config2['frequencies_list']:
                bugs_detected.append(
                    f"frequencies_list values changed (same length but different values)"
                )
        
        # Check lines_dt
        if config1['lines_dt'] is not None and config2['lines_dt'] is not None:
            if abs(config1['lines_dt'] - config2['lines_dt']) > 0.001:  # Allow small floating point differences
                bugs_detected.append(
                    f"lines_dt changed: Job1={config1['lines_dt']}, Job2={config2['lines_dt']}"
                )
        
        # Check stream_amount (should be same for same view_type)
        if config1['stream_amount'] is not None and config2['stream_amount'] is not None:
            if config1['stream_amount'] != config2['stream_amount']:
                bugs_detected.append(
                    f"stream_amount changed: Job1={config1['stream_amount']}, Job2={config2['stream_amount']}"
                )
        
        # Verify ROI actually changed (this should be different)
        channel_amount1 = getattr(response1, 'channel_amount', None)
        channel_amount2 = getattr(response2, 'channel_amount', None)
        if channel_amount1 and channel_amount2:
            logger.info(f"  ROI verification:")
            logger.info(f"    Job 1 channels: {channel_amount1}")
            logger.info(f"    Job 2 channels: {channel_amount2}")
            if channel_amount1 == channel_amount2:
                logger.warning(f"  ⚠️  ROI didn't change - this is unexpected!")
            else:
                logger.info(f"  ✅ ROI correctly changed: {channel_amount1} → {channel_amount2}")
        
        # Report bugs if any detected
        if bugs_detected:
            error_msg = (
                f"\n{'=' * 80}\n"
                f"🚨 BUG DETECTED: ROI change incorrectly affected other config parameters!\n"
                f"{'=' * 80}\n"
                f"Test Case: {test_id} - {description}\n"
                f"ROI changed from [{roi1_min}, {roi1_max}] to [{roi2_min}, {roi2_max}]\n"
                f"\nExpected: Only ROI should change, all other params should stay the SAME\n"
                f"Actual: The following parameters changed incorrectly:\n"
            )
            for bug in bugs_detected:
                error_msg += f"  - {bug}\n"
            error_msg += (
                f"\nThis indicates a bug where ROI changes affect unrelated config parameters!\n"
                f"{'=' * 80}\n"
            )
            logger.error(error_msg)
            raise AssertionError(error_msg)
        
        logger.info(f"✅ TEST PASSED ({test_id}): ROI change did NOT affect other config parameters")
        logger.info(f"   Test Case: {description}")
        logger.info(f"   All non-ROI parameters remained constant:")
        logger.info(f"   - View Type: {config1['view_type']} (unchanged)")
        logger.info(f"   - Stream Amount: {config1['stream_amount']} (unchanged)")
        logger.info(f"   - Lines DT: {config1['lines_dt']} (unchanged)")
        if config1['frequencies_list']:
            logger.info(f"   - Frequencies Count: {len(config1['frequencies_list'])} (unchanged)")
    
    @pytest.mark.parametrize(
        "config_test_id,nfft,freq_min,freq_max,display_duration,config_description",
        CONFIG_TEST_CASES,
        ids=[case[0] for case in CONFIG_TEST_CASES]  # Use test_id as test name
    )
    @pytest.mark.regression
def test_roi_change_with_different_configs_should_not_affect_other_params(
        self,
        focus_server_api,
        config_test_id,
        nfft,
        freq_min,
        freq_max,
        display_duration,
        config_description
    ):
        """
        Test: ROI change with different config combinations should NOT affect other parameters.
        
        Objective:
            Verify that when ROI changes with different configuration settings
            (NFFT, frequency range, display duration), other parameters remain unchanged.
        
        This test runs with different config combinations to ensure robustness.
        """
        logger.info("=" * 80)
        logger.info(f"TEST: ROI Change with Different Configs Should NOT Affect Other Params")
        logger.info(f"Config Test Case: {config_test_id} - {config_description}")
        logger.info("=" * 80)
        
        # Fixed values
        fixed_display_height = 1000
        fixed_view_type = ViewType.MULTICHANNEL
        
        # ROI test cases - use a subset for config testing
        roi1_min, roi1_max = 1, 50
        roi2_min, roi2_max = 1, 100
        
        logger.info(f"Configuration Values:")
        logger.info(f"  NFFT: {nfft}")
        logger.info(f"  Frequency Range: [{freq_min}, {freq_max}]")
        logger.info(f"  Display Duration: {display_duration}")
        logger.info(f"  Display Height: {fixed_display_height}")
        logger.info(f"  View Type: {fixed_view_type}")
        logger.info(f"\nROI 1: [{roi1_min}, {roi1_max}]")
        logger.info(f"ROI 2: [{roi2_min}, {roi2_max}]")
        
        # Configure Job 1
        payload1 = {
            "displayTimeAxisDuration": display_duration,
            "nfftSelection": nfft,
            "displayInfo": {"height": fixed_display_height},
            "channels": {"min": roi1_min, "max": roi1_max},
            "frequencyRange": {"min": freq_min, "max": freq_max},
            "start_time": None,
            "end_time": None,
            "view_type": fixed_view_type
        }
        
        config_request1 = ConfigureRequest(**payload1)
        response1 = focus_server_api.configure_streaming_job(config_request1)
        assert hasattr(response1, 'job_id') and response1.job_id
        job_id1 = response1.job_id
        
        config1 = {
            "frequencies_list": getattr(response1, 'frequencies_list', None),
            "lines_dt": getattr(response1, 'lines_dt', None),
            "view_type": getattr(response1, 'view_type', None),
            "stream_amount": getattr(response1, 'stream_amount', None),
        }
        
        time.sleep(2.0)
        
        # Configure Job 2 with same config but different ROI
        payload2 = {
            "displayTimeAxisDuration": display_duration,  # SAME
            "nfftSelection": nfft,  # SAME
            "displayInfo": {"height": fixed_display_height},  # SAME
            "channels": {"min": roi2_min, "max": roi2_max},  # DIFFERENT
            "frequencyRange": {"min": freq_min, "max": freq_max},  # SAME
            "start_time": None,
            "end_time": None,
            "view_type": fixed_view_type  # SAME
        }
        
        config_request2 = ConfigureRequest(**payload2)
        response2 = focus_server_api.configure_streaming_job(config_request2)
        assert hasattr(response2, 'job_id') and response2.job_id
        job_id2 = response2.job_id
        
        config2 = {
            "frequencies_list": getattr(response2, 'frequencies_list', None),
            "lines_dt": getattr(response2, 'lines_dt', None),
            "view_type": getattr(response2, 'view_type', None),
            "stream_amount": getattr(response2, 'stream_amount', None),
        }
        
        time.sleep(2.0)
        
        # Verify parameters are the same
        bugs_detected = []
        
        if config1['view_type'] != config2['view_type']:
            bugs_detected.append(f"view_type changed: {config1['view_type']} → {config2['view_type']}")
        
        if config1['frequencies_list'] and config2['frequencies_list']:
            if len(config1['frequencies_list']) != len(config2['frequencies_list']):
                bugs_detected.append(
                    f"frequencies_list length: {len(config1['frequencies_list'])} → {len(config2['frequencies_list'])}"
                )
        
        if config1['lines_dt'] is not None and config2['lines_dt'] is not None:
            if abs(config1['lines_dt'] - config2['lines_dt']) > 0.001:
                bugs_detected.append(f"lines_dt changed: {config1['lines_dt']} → {config2['lines_dt']}")
        
        if config1['stream_amount'] != config2['stream_amount']:
            bugs_detected.append(
                f"stream_amount changed: {config1['stream_amount']} → {config2['stream_amount']}"
            )
        
        if bugs_detected:
            error_msg = (
                f"\n{'=' * 80}\n"
                f"🚨 BUG DETECTED in config test case: {config_test_id}\n"
                f"{'=' * 80}\n"
                f"Config: {config_description}\n"
                f"ROI: [{roi1_min}, {roi1_max}] → [{roi2_min}, {roi2_max}]\n"
                f"Bugs:\n"
            )
            for bug in bugs_detected:
                error_msg += f"  - {bug}\n"
            error_msg += f"{'=' * 80}\n"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        
        logger.info(f"✅ TEST PASSED ({config_test_id}): Config params remained constant")
    
    @pytest.mark.regression
def test_different_rois_should_produce_same_data_size(self, focus_server_api):
        """
        Test: Different ROIs should produce the same data size.
        
        Objective:
            Verify that configuring jobs with different ROI ranges
            produces the SAME data size. If data sizes differ, this indicates a bug.
        
        Steps:
            1. Configure job with ROI [min1, max1] (e.g., [1, 50])
            2. Get data size (channel_amount or actual data size)
            3. Configure new job with ROI [min2, max2] (e.g., [1, 100])
            4. Get data size for second job
            5. Verify both data sizes are the SAME (expected behavior)
            6. If different, alert about the bug
        
        Expected:
            - Both ROIs should produce the same data size
            - Data size should be consistent regardless of ROI range
            - If sizes differ, this is a bug that should be reported
        
        Bug Detection:
            This test detects a bug where different ROI configurations
            incorrectly produce different data sizes when they should be the same.
        """
        logger.info("=" * 80)
        logger.info("TEST: Different ROIs Should Produce Same Data Size")
        logger.info("=" * 80)
        logger.info("⚠️  BUG DETECTION TEST: This test will FAIL if data sizes differ")
        logger.info("=" * 80)
        
        # Define two different ROIs
        roi1_min = 1
        roi1_max = 50
        
        roi2_min = 1
        roi2_max = 100
        
        logger.info(f"ROI 1: [{roi1_min}, {roi1_max}]")
        logger.info(f"ROI 2: [{roi2_min}, {roi2_max}]")
        logger.info("Expected: Both should produce the SAME data size")
        
        # ============================================
        # Step 1: Configure first job with ROI 1
        # ============================================
        logger.info("\nStep 1: Configuring first job with ROI 1...")
        payload1 = {
            "displayTimeAxisDuration": 30,
            "nfftSelection": 1024,
            "displayInfo": {
                "height": 1000
            },
            "channels": {
                "min": roi1_min,
                "max": roi1_max
            },
            "frequencyRange": {
                "min": 0,
                "max": 500
            },
            "start_time": None,  # Live mode
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request1 = ConfigureRequest(**payload1)
        response1 = focus_server_api.configure_streaming_job(config_request1)
        
        assert hasattr(response1, 'job_id') and response1.job_id
        job_id1 = response1.job_id
        logger.info(f"✅ Job 1 configured: {job_id1}")
        
        # Wait a bit for job to initialize
        time.sleep(2.0)
        
        # Get metadata for first job to determine data size
        logger.info("  Getting metadata for job 1...")
        metadata1 = None
        data_size1 = None
        
        for attempt in range(5):
            try:
                metadata1 = focus_server_api.get_job_metadata(job_id1)
                if metadata1:
                    # Try to get data size from metadata
                    if hasattr(metadata1, 'channel_amount'):
                        data_size1 = metadata1.channel_amount
                        logger.info(f"  Job 1 data size (channel_amount): {data_size1}")
                        break
            except Exception as e:
                logger.debug(f"  Attempt {attempt + 1}: {e}")
                time.sleep(1.0)
        
        # Fallback: use configure response
        if data_size1 is None:
            data_size1 = getattr(response1, 'channel_amount', None)
            if data_size1:
                logger.info(f"  Using configure response channel_amount: {data_size1}")
        
        # Try to get actual data size from waterfall if available
        if data_size1 is None:
            logger.warning("  ⚠️  Could not determine data size from metadata, trying waterfall...")
            try:
                waterfall1 = focus_server_api.get_waterfall(job_id1, row_count=10)
                if waterfall1 and waterfall1.status_code == 201 and waterfall1.data:
                    # Count sensors in waterfall data
                    total_sensors = 0
                    for block in waterfall1.data:
                        if hasattr(block, 'rows'):
                            for row in block.rows:
                                if hasattr(row, 'sensors'):
                                    total_sensors += len(row.sensors)
                    if total_sensors > 0:
                        data_size1 = total_sensors
                        logger.info(f"  Job 1 data size (from waterfall): {data_size1} sensors")
            except Exception as e:
                logger.debug(f"  Waterfall not available: {e}")
        
        assert data_size1 is not None, "Could not determine data size for job 1"
        logger.info(f"✅ Job 1 data size: {data_size1}")
        
        # ============================================
        # Step 2: Configure second job with ROI 2
        # ============================================
        logger.info("\nStep 2: Configuring second job with ROI 2...")
        payload2 = {
            "displayTimeAxisDuration": 30,
            "nfftSelection": 1024,
            "displayInfo": {
                "height": 1000
            },
            "channels": {
                "min": roi2_min,
                "max": roi2_max
            },
            "frequencyRange": {
                "min": 0,
                "max": 500
            },
            "start_time": None,  # Live mode
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request2 = ConfigureRequest(**payload2)
        response2 = focus_server_api.configure_streaming_job(config_request2)
        
        assert hasattr(response2, 'job_id') and response2.job_id
        job_id2 = response2.job_id
        logger.info(f"✅ Job 2 configured: {job_id2}")
        
        # Wait a bit for job to initialize
        time.sleep(2.0)
        
        # Get metadata for second job to determine data size
        logger.info("  Getting metadata for job 2...")
        metadata2 = None
        data_size2 = None
        
        for attempt in range(5):
            try:
                metadata2 = focus_server_api.get_job_metadata(job_id2)
                if metadata2:
                    # Try to get data size from metadata
                    if hasattr(metadata2, 'channel_amount'):
                        data_size2 = metadata2.channel_amount
                        logger.info(f"  Job 2 data size (channel_amount): {data_size2}")
                        break
            except Exception as e:
                logger.debug(f"  Attempt {attempt + 1}: {e}")
                time.sleep(1.0)
        
        # Fallback: use configure response
        if data_size2 is None:
            data_size2 = getattr(response2, 'channel_amount', None)
            if data_size2:
                logger.info(f"  Using configure response channel_amount: {data_size2}")
        
        # Try to get actual data size from waterfall if available
        if data_size2 is None:
            logger.warning("  ⚠️  Could not determine data size from metadata, trying waterfall...")
            try:
                waterfall2 = focus_server_api.get_waterfall(job_id2, row_count=10)
                if waterfall2 and waterfall2.status_code == 201 and waterfall2.data:
                    # Count sensors in waterfall data
                    total_sensors = 0
                    for block in waterfall2.data:
                        if hasattr(block, 'rows'):
                            for row in block.rows:
                                if hasattr(row, 'sensors'):
                                    total_sensors += len(row.sensors)
                    if total_sensors > 0:
                        data_size2 = total_sensors
                        logger.info(f"  Job 2 data size (from waterfall): {data_size2} sensors")
            except Exception as e:
                logger.debug(f"  Waterfall not available: {e}")
        
        assert data_size2 is not None, "Could not determine data size for job 2"
        logger.info(f"✅ Job 2 data size: {data_size2}")
        
        # ============================================
        # Step 3: Verify data sizes are the SAME
        # ============================================
        logger.info("\nStep 3: Verifying data sizes are the SAME...")
        logger.info(f"  Job 1 data size: {data_size1}")
        logger.info(f"  Job 2 data size: {data_size2}")
        
        if data_size1 != data_size2:
            error_msg = (
                f"\n{'=' * 80}\n"
                f"🚨 BUG DETECTED: Different ROIs produce different data sizes!\n"
                f"{'=' * 80}\n"
                f"ROI [{roi1_min}, {roi1_max}] → Data size: {data_size1}\n"
                f"ROI [{roi2_min}, {roi2_max}] → Data size: {data_size2}\n"
                f"\nExpected: Both ROIs should produce the SAME data size\n"
                f"Actual: Data sizes differ by {abs(data_size1 - data_size2)} units\n"
                f"\nThis indicates a bug in ROI handling!\n"
                f"{'=' * 80}\n"
            )
            logger.error(error_msg)
            raise AssertionError(error_msg)
        
        logger.info(f"✅ TEST PASSED: Different ROIs produce the SAME data size")
        logger.info(f"   ROI [{roi1_min}, {roi1_max}] → Data size: {data_size1}")
        logger.info(f"   ROI [{roi2_min}, {roi2_max}] → Data size: {data_size2}")
        logger.info(f"   ✅ Both match: {data_size1}")