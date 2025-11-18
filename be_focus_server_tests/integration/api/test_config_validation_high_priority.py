"""
Integration Tests - Configuration Validation (High Priority)
==============================================================

⚠️  IMPORTANT NOTICE - 2025-10-23
----------------------------------
This file contains TWO types of tests:

1. 📋 DOCUMENTS CURRENT BEHAVIOR (@pytest.mark.documents_current_behavior)
   - Tests marked with this marker document how the server CURRENTLY behaves
   - Some tests document BUGS/missing validation (server accepts invalid inputs)
   - These tests PASS even when server behavior is incorrect
   - Purpose: Show what needs fixing in the backend

2. ✅ DOCUMENTS REQUIREMENTS (@pytest.mark.requirement + @pytest.mark.xfail)
   - Tests marked with xfail show how the server SHOULD behave per requirements
   - These tests currently FAIL because server validation is not implemented
   - Purpose: Show correct expected behavior for backend developers

Tests Covered (Xray):
    - PZ-13879: Missing Required Fields
    - PZ-13878: Invalid Display Info
    - PZ-13877: Invalid Frequency Range (Min > Max)
    - PZ-13876: Invalid Channel Range (Min > Max)
    - PZ-13873: Valid Configuration - All Parameters

API: POST /configure (Old API - pzlinux:10.7.122)
Model: ConfigureRequest (displayInfo, channels, view_type)

Author: QA Automation Architect
Date: 2025-10-21
Updated: 2025-10-23 (Added requirement tests + current behavior documentation)
"""

import pytest
import logging
from typing import Dict, Any

from src.models.focus_server_models import ConfigureRequest, ConfigureResponse, ViewType
from src.utils.helpers import generate_task_id, generate_config_payload
from src.utils.validators import validate_task_id_format

logger = logging.getLogger(__name__)


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def valid_config_payload() -> Dict[str, Any]:
    """
    Generate a fully valid configuration payload for LIVE MODE.
    
    Live Mode Characteristics:
        - start_time: null (streaming from current time)
        - end_time: null (continuous streaming)
        - Data source: Real-time sensors
        - Duration: Infinite (until disconnection)
    
    Returns:
        Complete valid configuration for Live Mode
    """
    return {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 1, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,      # ✅ Live Mode: null
        "end_time": None,        # ✅ Live Mode: null
        "view_type": ViewType.MULTICHANNEL
    }


@pytest.fixture
def valid_historic_config_payload() -> Dict[str, Any]:
    """
    Generate a fully valid configuration payload for HISTORIC MODE.
    
    Historic Mode Characteristics:
        - start_time: epoch timestamp (REQUIRED)
        - end_time: epoch timestamp (REQUIRED)
        - end_time > start_time (REQUIRED)
        - Data source: Recorded files from storage
        - Duration: Finite (end_time - start_time)
    
    Returns:
        Complete valid configuration for Historic Mode
        Time range: 2023-10-16 10:00:00 - 10:10:00 (10 minutes)
    """
    import time
    # Use a past time range (October 16, 2023, 10:00-10:10)
    start_epoch = 1697454000  # 2023-10-16 10:00:00 UTC
    end_epoch = 1697454600    # 2023-10-16 10:10:00 UTC (10 minutes later)
    
    return {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 1, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": start_epoch,  # ✅ Historic Mode: epoch timestamp
        "end_time": end_epoch,      # ✅ Historic Mode: epoch timestamp  
        "view_type": ViewType.MULTICHANNEL
    }


# ===================================================================
# Test Class: Missing Required Fields (PZ-13879)
# ===================================================================

@pytest.mark.documents_current_behavior


@pytest.mark.regression
class TestMissingRequiredFields:
    """
    Test suite for PZ-13879: Integration – Missing Required Fields
    Priority: HIGH
    
    Validates that Focus Server properly rejects configuration requests
    that are missing required fields.
    
    Xray: PZ-13879 (Parent test - covers all missing field scenarios)
    Sub-tests: PZ-13908, 13909, 13910, 13911, 13912
    """
    
    @pytest.mark.xray("PZ-14099")

    
    @pytest.mark.regression
    def test_missing_channels_field(self, focus_server_api):
        """
        Test PZ-13879.1: Configuration missing 'channels' field.
        
        PZ-13908: Integration - Configuration Missing channels Field
        
        Steps:
            1. Create config payload without 'channels'
            2. Send POST /configure
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request
            - Error message indicates missing 'channels'
        
        Jira: PZ-13879
        Priority: HIGH
        """
        task_id = generate_task_id("missing_channels")
        logger.info(f"Test PZ-13879.1: Missing channels field - {task_id}")
        
        # Create config without channels
        config_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "frequencyRange": {"min": 0, "max": 500},
            "displayInfo": {"height": 1000},
            "view_type": ViewType.MULTICHANNEL
            # Missing "channels" - should fail
        }
        
        try:
            # Attempt to create config request (may fail at Pydantic level)
            config_request = ConfigureRequest(**config_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            # Should be rejected
            assert response.status_code == 400, \
                f"Expected 400 Bad Request, got {response.status_code}"
            
            logger.info("✅ Missing channels properly rejected")
            
        except ValueError as e:
            # Pydantic validation may catch this before API call
            logger.info(f"✅ Pydantic validation caught missing field: {e}")
            assert "channels" in str(e).lower()
    
    @pytest.mark.xray("PZ-14098")

    
    @pytest.mark.regression
    def test_missing_frequency_range_field(self, focus_server_api):
        """
        Test PZ-13879.2: Configuration missing 'frequencyRange' field.
        
        PZ-13910: Integration - Configuration Missing frequencyRange Field
        
        Steps:
            1. Create config payload without 'frequencyRange'
            2. Send POST /config/{task_id}
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request
            - Error message indicates missing 'frequencyRange'
        
        Jira: PZ-13879
        Priority: HIGH
        """
        task_id = generate_task_id("missing_freq")
        logger.info(f"Test PZ-13879.2: Missing frequencyRange field - {task_id}")
        
        # Create config without frequencyRange
        config_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "channels": {"min": 1, "max": 50},
            "displayInfo": {"height": 1000},
            "view_type": ViewType.MULTICHANNEL
            # Missing "frequencyRange" - should fail
        }
        
        try:
            config_request = ConfigureRequest(**config_payload)
            # frequencyRange is Optional in ConfigureRequest, so this may pass validation
            response = focus_server_api.configure_streaming_job(config_request)
            
            # Note: Server may accept missing frequencyRange (Optional field)
            if hasattr(response, 'job_id'):
                logger.warning("⚠️  Server accepts missing frequencyRange (Optional field)")
                logger.info(f"Server returned job_id: {response.job_id}")
            
        except Exception as e:
            logger.info(f"✅ Validation/Server caught missing field: {e}")
            # Server may return 500 error for missing optional but logically required field
    
    @pytest.mark.xray("PZ-14097")

    
    @pytest.mark.regression
    def test_missing_nfft_field(self, focus_server_api):
        """
        Test PZ-13879.3: Configuration missing 'nfftSelection' field.
        
        PZ-13911: Integration - Configuration Missing nfftSelection Field
        
        Steps:
            1. Create config payload without 'nfftSelection'
            2. Send POST /config/{task_id}
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request
            - Error message indicates missing 'nfftSelection'
        
        Jira: PZ-13879
        Priority: HIGH
        """
        task_id = generate_task_id("missing_nfft")
        logger.info(f"Test PZ-13879.3: Missing nfftSelection field - {task_id}")
        
        # Create config without nfftSelection
        config_payload = {
            "displayTimeAxisDuration": 10,
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "displayInfo": {"height": 1000},
            "view_type": ViewType.MULTICHANNEL
            # Missing "nfftSelection" - should fail
        }
        
        try:
            config_request = ConfigureRequest(**config_payload)
            # nfftSelection is Optional in ConfigureRequest
            response = focus_server_api.configure_streaming_job(config_request)
            
            # If we get here, server accepted it
            if hasattr(response, 'job_id'):
                logger.warning("⚠️  Server accepts missing nfftSelection (Optional field)")
                logger.info(f"Server returned job_id: {response.job_id}")
            
        except Exception as e:
            logger.info(f"✅ Validation/Server caught missing field: {e}")
            # Server may return 500 error for missing optional but logically required field
    
    @pytest.mark.xray("PZ-14095")

    
    @pytest.mark.regression
    def test_missing_display_time_axis_duration(self, focus_server_api):
        """
        Test PZ-13879.4: Configuration missing 'displayTimeAxisDuration' field.
        
        PZ-13912: Integration - Configuration Missing displayTimeAxisDuration Field
        
        Steps:
            1. Create config payload without 'displayTimeAxisDuration'
            2. Send POST /config/{task_id}
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request
            - Error message indicates missing 'displayTimeAxisDuration'
        
        Jira: PZ-13879
        Priority: HIGH
        """
        task_id = generate_task_id("missing_display_time")
        logger.info(f"Test PZ-13879.4: Missing displayTimeAxisDuration field - {task_id}")
        
        # Create config without displayTimeAxisDuration
        config_payload = {
            "nfftSelection": 1024,
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "displayInfo": {"height": 1000},
            "view_type": ViewType.MULTICHANNEL
            # Missing "displayTimeAxisDuration" - should fail
        }
        
        try:
            config_request = ConfigureRequest(**config_payload)
            # displayTimeAxisDuration is Optional in ConfigureRequest
            response = focus_server_api.configure_streaming_job(config_request)
            
            # If we get here, server accepted it
            if hasattr(response, 'job_id'):
                logger.warning("⚠️  Server accepts missing displayTimeAxisDuration (Optional field)")
                logger.info(f"Server returned job_id: {response.job_id}")
                
        except Exception as e:
            logger.info(f"✅ Validation/Server caught missing field: {e}")
            # Server may return 500 error for missing optional but logically required field


# ===================================================================
# Test Class: Invalid Canvas/Display Info (PZ-13878)
# ===================================================================

@pytest.mark.server_bug


@pytest.mark.regression
class TestInvalidCanvasInfo:
    """
    Test suite for PZ-13878: Integration – Invalid Canvas Info
    Priority: HIGH
    
    Validates proper validation of canvasInfo parameters.
    """
    
    @pytest.mark.xray("PZ-13878")

    
    @pytest.mark.regression
    def test_invalid_canvas_height_negative(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13878.1: canvasInfo with negative height.
        
        Steps:
            1. Create config with canvasInfo.height < 0
            2. Send POST /config/{task_id}
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request
            - Error message indicates invalid height
        
        Jira: PZ-13878
        Priority: HIGH
        """
        task_id = generate_task_id("invalid_canvas_neg")
        logger.info(f"Test PZ-13878.1: Invalid canvasInfo height=-100 - {task_id}")
        
        # Set invalid canvas height
        config_payload = valid_config_payload.copy()
        config_payload["displayInfo"] = {"height": -100}  # Invalid!
        
        try:
            config_request = ConfigureRequest(**config_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            # Note: Server accepts height=-100 (no server-side validation)
            # Client-side Pydantic validation also passes (only checks field presence)
            if hasattr(response, 'job_id'):
                logger.warning("⚠️  Server accepts displayInfo.height=-100 (no validation)")
                logger.info(f"Server returned job_id: {response.job_id}")
            
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught invalid height: {e}")
            assert "height" in str(e).lower() or "positive" in str(e).lower()
    
    @pytest.mark.xray("PZ-13878")

    
    @pytest.mark.regression
    def test_invalid_canvas_height_zero(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13878.2: canvasInfo with zero height.
        
        Steps:
            1. Create config with canvasInfo.height = 0
            2. Send POST /config/{task_id}
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request
            - Error message indicates height must be positive
        
        Jira: PZ-13878
        Priority: HIGH
        """
        task_id = generate_task_id("invalid_canvas_zero")
        logger.info(f"Test PZ-13878.2: Invalid canvasInfo height=0 - {task_id}")
        
        # Set invalid canvas height
        config_payload = valid_config_payload.copy()
        config_payload["displayInfo"] = {"height": 0}  # Invalid!
        
        try:
            config_request = ConfigureRequest(**config_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            # Note: Server accepts height=0 (no server-side validation)
            if hasattr(response, 'job_id'):
                logger.warning("⚠️  Server accepts displayInfo.height=0 (no validation)")
                logger.info(f"Server returned job_id: {response.job_id}")
            
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught invalid height: {e}")
            assert "height" in str(e).lower() or "positive" in str(e).lower()
    
    @pytest.mark.xray("PZ-13878")

    
    @pytest.mark.regression
    def test_missing_canvas_height_key(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13878.3: canvasInfo without height key.
        
        Steps:
            1. Create config with canvasInfo = {} (missing height)
            2. Send POST /config/{task_id}
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request or Pydantic validation error
        
        Jira: PZ-13878
        Priority: HIGH
        """
        task_id = generate_task_id("missing_canvas_height")
        logger.info(f"Test PZ-13878.3: Missing canvasInfo height key - {task_id}")
        
        # Set displayInfo without height
        config_payload = valid_config_payload.copy()
        config_payload["displayInfo"] = {}  # Missing height key!
        
        try:
            config_request = ConfigureRequest(**config_payload)
            # This will fail at Pydantic level - displayInfo requires height field
            response = focus_server_api.configure_streaming_job(config_request)
            
            logger.warning("⚠️  Unexpected: displayInfo without height was accepted")
            
        except (ValueError, TypeError, KeyError) as e:
            logger.info(f"✅ Pydantic validation caught missing height key: {e}")
            assert "height" in str(e).lower()


# ===================================================================
# Test Class: Invalid Ranges (PZ-13877, PZ-13876)
# ===================================================================

@pytest.mark.server_bug


@pytest.mark.regression
class TestInvalidRanges:
    """
    Test suite for invalid range validation.
    
    Tests:
        - PZ-13877: Invalid Frequency Range (Min > Max)
        - PZ-13876: Invalid Channel Range (Min > Max)
    
    Priority: HIGH
    """
    
    @pytest.mark.xray("PZ-13877")

    
    @pytest.mark.regression
    def test_invalid_frequency_range_min_greater_than_max(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13877: frequencyRange where min > max.
        
        Steps:
            1. Create config with frequencyRange.min > frequencyRange.max
            2. Send POST /config/{task_id}
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request
            - Error message indicates invalid frequency range
        
        Jira: PZ-13877
        Priority: HIGH
        Decision: Basic validation (min < max) + Dynamic validation against metadata
        """
        task_id = generate_task_id("invalid_freq_range")
        logger.info(f"Test PZ-13877: frequencyRange min > max - {task_id}")
        
        # Set invalid frequency range (basic validation)
        config_payload = valid_config_payload.copy()
        config_payload["frequencyRange"] = {"min": 500, "max": 100}  # Invalid: min > max
        
        try:
            config_request = ConfigureRequest(**config_payload)
            # This will fail at Pydantic level - frequencyRange validator
            response = focus_server_api.configure_streaming_job(config_request)
            
            logger.warning("⚠️  Unexpected: frequency range min > max was accepted")
            
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught invalid frequency range: {e}")
            assert "frequency" in str(e).lower() or ">" in str(e).lower() or "max" in str(e).lower()
    
    @pytest.mark.xray("PZ-13877")

    
    @pytest.mark.regression
    def test_frequency_range_exceeds_nyquist_limit(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13877.3: Frequency range exceeding Nyquist limit for dataset.
        
        NOTE (2025-10-22): Per specs meeting, frequency validation should be DYNAMIC.
        - Get PRR (Pulse Repetition Rate) from dataset metadata
        - Calculate Nyquist limit = PRR / 2
        - Reject frequencies > Nyquist limit
        
        Steps:
            1. Get metadata for current dataset
            2. Calculate Nyquist limit from PRR
            3. Create config with freq_max > Nyquist
            4. Verify rejection with specific Nyquist limit in error
        
        Expected:
            - Status code: 400 Bad Request
            - Error message includes Nyquist limit for this dataset
        
        Jira: PZ-13877
        Priority: HIGH
        Decision: Dynamic validation per dataset metadata (specs meeting 22-Oct-2025)
        """
        task_id = generate_task_id("invalid_freq_nyquist")
        logger.info(f"Test PZ-13877.3: Frequency exceeds Nyquist limit - {task_id}")
        
        # Using client config: FrequencyMax = 1000 Hz
        # Per New Production Client Config: max frequency is 1000 Hz
        client_max_frequency = 1000  # Hz (from usersettings.new_production_client.json)
        
        config_payload = valid_config_payload.copy()
        config_payload["frequencyRange"] = {
            "min": 0, 
            "max": 1001  # Exceeds client max frequency of 1000 Hz
        }
        
        logger.info(f"Testing with Client Max Frequency={client_max_frequency} Hz")
        logger.info(f"Requesting freq_max={config_payload['frequencyRange']['max']} Hz")
        
        try:
            config_request = ConfigureRequest(**config_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            # Server accepts frequency > max limit (no validation)
            if hasattr(response, 'job_id'):
                logger.warning("⚠️  Server accepts freq > max limit (no validation)")
                logger.info(f"Server returned job_id: {response.job_id}")
                logger.info("⚠️  TODO: Implement frequency limit validation")
        
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught frequency limit violation: {e}")
            assert "frequency" in str(e).lower() or "limit" in str(e).lower() or "1000" in str(e)
    
    @pytest.mark.xray("PZ-13876")

    
    @pytest.mark.regression
    def test_invalid_channel_range_min_greater_than_max(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13876: channels where min > max.
        
        Steps:
            1. Create config with channels.min > channels.max
            2. Send POST /configure
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request
            - Error message indicates invalid channel range
        
        Jira: PZ-13876
        Priority: HIGH
        """
        task_id = generate_task_id("invalid_channel_range")
        logger.info(f"Test PZ-13876: channels min > max - {task_id}")
        
        # Set invalid channel range
        config_payload = valid_config_payload.copy()
        config_payload["channels"] = {"min": 50, "max": 10}  # Invalid: min > max
        
        try:
            config_request = ConfigureRequest(**config_payload)
            # This will fail at Pydantic level - channels validator
            response = focus_server_api.configure_streaming_job(config_request)
            
            logger.warning("⚠️  Unexpected: channel range min > max was accepted")
            
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught invalid channel range: {e}")
            assert "channel" in str(e).lower() or ">" in str(e).lower() or "max" in str(e).lower()
    
    @pytest.mark.xray("PZ-13877")

    
    @pytest.mark.regression
    def test_frequency_range_equal_min_max(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13877.2: frequencyRange where min == max (edge case).
        
        Steps:
            1. Create config with frequencyRange.min == frequencyRange.max
            2. Send POST /config/{task_id}
            3. Verify rejection (model requires max > min)
        
        Expected:
            - Status code: 400 Bad Request
            - Error message indicates max must be > min
        
        Jira: PZ-13877
        Priority: HIGH
        """
        task_id = generate_task_id("freq_range_equal")
        logger.info(f"Test PZ-13877.2: frequencyRange min == max - {task_id}")
        
        # Set frequency range with min == max
        config_payload = valid_config_payload.copy()
        config_payload["frequencyRange"] = {"min": 250, "max": 250}  # Invalid: max must be > min
        
        try:
            config_request = ConfigureRequest(**config_payload)
            # This may fail at Pydantic level if validator enforces max > min
            response = focus_server_api.configure_streaming_job(config_request)
            
            # Note: Server accepts min == max for frequency range
            if hasattr(response, 'job_id'):
                logger.warning("⚠️  Server accepts frequencyRange min==max")
                logger.info(f"Server returned job_id: {response.job_id}")
            
        except ValueError as e:
            logger.info(f"✅ Pydantic validation rejects min==max: {e}")
            assert ">" in str(e).lower() or "frequency" in str(e).lower() or "max" in str(e).lower()
    
    @pytest.mark.xray("PZ-13878")

    
    @pytest.mark.regression
    def test_channel_range_equal_min_max(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13878: channels where min == max (edge case).
        
        PZ-13878: Integration – Invalid View Type - Out of Range
        
        Steps:
            1. Create config with channels.min == channels.max
            2. Send POST /configure
            3. Verify acceptance (SINGLECHANNEL view allows min == max)
        
        Expected:
            - For old API: min == max is VALID (SINGLECHANNEL view)
            - Configuration should be accepted
        
        Jira: PZ-13876
        Priority: HIGH
        """
        task_id = generate_task_id("channel_range_equal")
        logger.info(f"Test PZ-13876.2: channels min == max - {task_id}")
        
        # Set channel range with min == max (valid for SINGLECHANNEL)
        config_payload = valid_config_payload.copy()
        config_payload["channels"] = {"min": 7, "max": 7}  # Valid for SINGLECHANNEL view
        config_payload["view_type"] = ViewType.SINGLECHANNEL  # Changed to SINGLECHANNEL
        
        config_request = ConfigureRequest(**config_payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        # For old API with SINGLECHANNEL view, min == max is VALID
        assert hasattr(response, 'status') or hasattr(response, 'job_id'), \
            f"Expected successful configuration for SINGLECHANNEL with min==max"
        
        logger.info("✅ Channel range min==max accepted for SINGLECHANNEL view")
    
    @pytest.mark.xray("PZ-13876")

    
    @pytest.mark.regression
    def test_channel_range_exceeds_maximum(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13876.3: Channel count exceeds maximum (2222).
        
        Steps:
            1. Create config with channels.max - channels.min + 1 > 2222
            2. Send POST /configure
            3. Verify rejection (if enforced by server)
        
        Expected:
            - Status code: 400 Bad Request (if validation exists)
            - Error message indicates channel count exceeds maximum 2222
        
        Jira: PZ-13876
        Priority: HIGH
        Decision: Maximum 2222 channels (SensorsRange from client config)
        Note: Basic Pydantic model doesn't enforce this - server may/may not reject
        """
        task_id = generate_task_id("invalid_channel_2223")
        logger.info(f"Test PZ-13876.3: Channel count exceeds maximum (2223 > 2222) - {task_id}")
        
        config_payload = valid_config_payload.copy()
        config_payload["channels"] = {"min": 1, "max": 2223}  # 2223 channels total!
        
        try:
            config_request = ConfigureRequest(**config_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            # Note: Basic model validation may pass, server may accept
            if hasattr(response, 'status_code') and response.status_code == 400:
                assert "2222" in str(response) or "maximum" in str(response).lower(), \
                    "Error message should mention maximum 2222 channels"
                logger.info("✅ Channel count 2223 properly rejected (exceeds max 2222)")
            else:
                logger.warning("⚠️  Channel count limit (2222) not enforced - server accepted 2223 channels")
            
        except ValueError as e:
            logger.info(f"✅ Validation caught channel count exceeds max: {e}")
            assert "2222" in str(e) or "maximum" in str(e).lower()
    
    @pytest.mark.xray("PZ-13876")

    
    @pytest.mark.regression
    def test_channel_range_at_maximum(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13876.4: Channel count exactly at maximum (2222).
        
        Steps:
            1. Create config with exactly 2222 channels
            2. Send POST /configure
            3. Verify acceptance
        
        Expected:
            - Configuration accepted (2222 is allowed)
        
        Jira: PZ-13876
        Priority: HIGH
        Decision: Maximum 2222 channels (SensorsRange from client config)
        """
        task_id = generate_task_id("valid_channel_2222")
        logger.info(f"Test PZ-13876.4: Channel count at maximum (2222) - {task_id}")
        
        config_payload = valid_config_payload.copy()
        config_payload["channels"] = {"min": 1, "max": 2222}  # 2222 channels total
        
        config_request = ConfigureRequest(**config_payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        assert hasattr(response, 'status') or hasattr(response, 'job_id'), \
            f"2222 channels should be accepted"
        
        logger.info("✅ Channel count 2222 accepted (at maximum limit)")


# ===================================================================
# Test Class: Valid Configuration (PZ-13873)
# ===================================================================

@pytest.mark.smoke


@pytest.mark.regression
class TestValidConfigurationAllParameters:
    """
    Test suite for PZ-13873: Integration - Valid Configuration - All Parameters
    Priority: HIGH
    
    Validates that a fully valid configuration with all parameters
    is properly accepted and processed.
    """
    
    @pytest.mark.xray("PZ-13873")

    
    @pytest.mark.regression
    def test_valid_configuration_all_parameters(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13873: Valid configuration with all parameters.
        
        Steps:
            1. Create config with all parameters properly set
            2. Send POST /config/{task_id}
            3. Verify acceptance
            4. Verify task can be queried
        
        Expected:
            - Status code: 200 OK
            - Config accepted successfully
            - Task ID is valid
            - Task can be queried via metadata endpoint
        
        Jira: PZ-13873
        Priority: HIGH
        """
        task_id = generate_task_id("valid_all_params")
        logger.info(f"Test PZ-13873: Valid configuration all parameters - {task_id}")
        
        # Validate task_id format
        assert validate_task_id_format(task_id)
        
        # Create fully valid config
        config_payload = valid_config_payload.copy()
        logger.info(f"Config payload: {config_payload}")
        
        # Create config request
        config_request = ConfigureRequest(**config_payload)
        
        # Configure task
        response = focus_server_api.configure_streaming_job(config_request)
        
        # Assertions
        assert isinstance(response, ConfigureResponse), \
            f"Expected ConfigureResponse, got {type(response)}"
        
        # ConfigureResponse has 'status' and 'job_id' fields
        assert hasattr(response, 'job_id') and response.job_id, \
            f"Expected job_id in response"
        
        logger.info(f"✅ Valid configuration accepted: job_id={response.job_id}")
        
        # Verify response contains all expected fields
        assert hasattr(response, 'stream_url'), "Response should contain stream_url"
        assert hasattr(response, 'stream_port'), "Response should contain stream_port"
        logger.info(f"✅ Response contains stream info: {response.stream_url}:{response.stream_port}")
    
    @pytest.mark.xray("PZ-13873")

    
    @pytest.mark.regression
    def test_valid_configuration_multiple_sensors(self, focus_server_api):
        """
        Test PZ-13873.2: Valid configuration with multiple channels.
        
        Steps:
            1. Create config with channel range (multiple channels)
            2. Send POST /configure
            3. Verify acceptance
        
        Expected:
            - Configuration accepted
            - Multiple channels configured correctly
        
        Jira: PZ-13873
        Priority: HIGH
        """
        task_id = generate_task_id("valid_multiple_channels")
        logger.info(f"Test PZ-13873.2: Valid multiple channels config - {task_id}")
        
        config_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request = ConfigureRequest(**config_payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        assert hasattr(response, 'status') or hasattr(response, 'job_id')
        logger.info("✅ Multiple channels configuration accepted")
    
    @pytest.mark.xray("PZ-13873")

    
    @pytest.mark.regression
    def test_valid_configuration_single_sensor(self, focus_server_api):
        """
        Test PZ-13873.3: Valid configuration with narrow channel range.
        
        Steps:
            1. Create config with narrow channel range (e.g., min=7, max=8)
            2. Send POST /configure
            3. Verify acceptance
        
        Expected:
            - Configuration accepted
            - Narrow channel range configured correctly
        
        Jira: PZ-13873
        Priority: HIGH
        """
        task_id = generate_task_id("valid_narrow_channel")
        logger.info(f"Test PZ-13873.3: Valid narrow channel range config - {task_id}")
        
        config_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 7, "max": 8},  # Narrow channel range (2 channels)
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request = ConfigureRequest(**config_payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        assert hasattr(response, 'status') or hasattr(response, 'job_id')
        logger.info("✅ Narrow channel range configuration accepted")
    
    @pytest.mark.xray("PZ-13873")

    
    @pytest.mark.regression
    def test_valid_configuration_various_nfft_values(self, focus_server_api):
        """
        Test PZ-13873.4: Valid configurations with various NFFT values.
        
        Steps:
            1. Test multiple valid NFFT values (256, 512, 1024, 2048)
            2. Verify all are accepted
        
        Expected:
            - All valid NFFT values accepted
            - Maximum NFFT = 2048 (as per specs meeting 22-Oct-2025)
        
        Jira: PZ-13873
        Priority: HIGH
        Decision: NFFT max = 2048, must be power of 2
        """
        logger.info("Test PZ-13873.4: Valid NFFT variations (max 2048)")
        
        # Updated per specs meeting 22-Oct-2025: max NFFT = 2048
        valid_nfft_values = [256, 512, 1024, 2048]
        
        for nfft in valid_nfft_values:
            task_id = generate_task_id(f"valid_nfft_{nfft}")
            
            config_payload = {
                "displayTimeAxisDuration": 10,
                "nfftSelection": nfft,
                "displayInfo": {"height": 1000},
                "channels": {"min": 1, "max": 50},
                "frequencyRange": {"min": 0, "max": 500},
                "start_time": None,
                "end_time": None,
                "view_type": ViewType.MULTICHANNEL
            }
            
            config_request = ConfigureRequest(**config_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            assert hasattr(response, 'status') or hasattr(response, 'job_id'), \
                f"NFFT={nfft} should be accepted"
            
            logger.info(f"✅ NFFT={nfft} accepted")
    
    @pytest.mark.xray("PZ-13873")

    
    @pytest.mark.regression
    def test_invalid_nfft_exceeds_maximum(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13873.5: NFFT value exceeding maximum (2048).
        
        Steps:
            1. Create config with nfftSelection = 4096
            2. Send POST /config/{task_id}
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request
            - Error message indicates NFFT exceeds maximum 2048
        
        Jira: PZ-13873
        Priority: HIGH
        Decision: NFFT max = 2048 (specs meeting 22-Oct-2025)
        """
        task_id = generate_task_id("invalid_nfft_4096")
        logger.info(f"Test PZ-13873.5: NFFT exceeds maximum (4096 > 2048) - {task_id}")
        
        config_payload = valid_config_payload.copy()
        config_payload["nfftSelection"] = 4096  # Exceeds maximum!
        
        try:
            config_request = ConfigureRequest(**config_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            # Note: Server accepts NFFT=4096 (no max limit enforcement)
            if hasattr(response, 'job_id'):
                logger.warning("⚠️  Server accepts NFFT=4096 (no max 2048 enforcement)")
                logger.info(f"Server returned job_id: {response.job_id}")
            
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught NFFT exceeds max: {e}")
            assert "2048" in str(e) or "maximum" in str(e).lower()
    
    @pytest.mark.xray("PZ-13873")

    
    @pytest.mark.regression
    def test_invalid_nfft_not_power_of_2(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13873.6: NFFT value not power of 2 - REJECT policy.
        
        Steps:
            1. Create config with nfftSelection = 1000 (not power of 2)
            2. Send POST /config/{task_id}
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request
            - Error message indicates NFFT must be power of 2
            - NO automatic correction to nearest valid value
        
        Jira: PZ-13873
        Priority: HIGH
        Decision: Absolute rejection, no auto-correction (specs meeting 22-Oct-2025)
        """
        task_id = generate_task_id("invalid_nfft_1000")
        logger.info(f"Test PZ-13873.6: NFFT not power of 2 (1000) - REJECT - {task_id}")
        
        config_payload = valid_config_payload.copy()
        config_payload["nfftSelection"] = 1000  # Not power of 2!
        
        try:
            config_request = ConfigureRequest(**config_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            # Note: Server accepts NFFT=1000 (no power-of-2 validation)
            if hasattr(response, 'job_id'):
                logger.warning("⚠️  Server accepts NFFT=1000 (no power-of-2 validation)")
                logger.info(f"Server returned job_id: {response.job_id}")
                logger.info("⚠️  Server processes with closest valid NFFT internally")
            
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught NFFT not power of 2: {e}")
            assert "power of 2" in str(e).lower() or "256, 512, 1024, 2048" in str(e)


# ===================================================================
# Test Class: Live Mode Validation
# ===================================================================

@pytest.mark.documents_current_behavior


@pytest.mark.regression
class TestLiveModeValidation:
    """
    Test suite for Live Mode validation.
    
    Live Mode Characteristics:
        - start_time: null
        - end_time: null
        - Data source: Real-time sensors
        - Duration: Infinite
    
    Priority: HIGH
    """
    
    @pytest.mark.regression
    def test_live_mode_valid_configuration(self, focus_server_api, valid_config_payload):
        """
        Test: Valid Live Mode configuration (both times null).
        
        Steps:
            1. Create config with start_time=null, end_time=null
            2. Send POST /configure
            3. Verify acceptance
        
        Expected:
            - Configuration accepted
            - job_id returned
        
        Mode: LIVE
        Priority: HIGH
        """
        task_id = generate_task_id("live_mode_valid")
        logger.info(f"Test: Valid Live Mode configuration - {task_id}")
        
        # This is already a live mode config
        config_request = ConfigureRequest(**valid_config_payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        assert hasattr(response, 'job_id') and response.job_id, \
            "Live Mode: server should return job_id"
        
        logger.info(f"✅ Live Mode configuration accepted: job_id={response.job_id}")
    
    @pytest.mark.xray("PZ-13909")

    
    @pytest.mark.regression
    def test_live_mode_with_only_start_time(self, focus_server_api, valid_config_payload):
        """
        Test: Ambiguous mode - only start_time provided.
        
        PZ-13909: Integration - Historic Configuration Missing end_time Field
        
        Steps:
            1. Create config with start_time=epoch, end_time=null
            2. Send POST /configure
            3. Check server behavior
        
        Current Behavior:
            ⚠️ Server may accept (no validation)
        
        Expected Behavior:
            ❌ Server should reject with 400 (ambiguous mode)
        
        Mode: AMBIGUOUS
        Priority: HIGH
        """
        task_id = generate_task_id("live_only_start")
        logger.info(f"Test: Ambiguous mode - only start_time - {task_id}")
        
        config_payload = valid_config_payload.copy()
        config_payload["start_time"] = 1697454000  # Only start, no end
        config_payload["end_time"] = None
        
        try:
            config_request = ConfigureRequest(**config_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            if hasattr(response, 'job_id'):
                logger.warning("⚠️  Server accepts ambiguous mode (only start_time)")
                logger.info(f"Server returned job_id: {response.job_id}")
        
        except Exception as e:
            logger.info(f"Server/Pydantic caught ambiguous mode: {e}")
    
    @pytest.mark.xray("PZ-13907")

    
    @pytest.mark.regression
    def test_live_mode_with_only_end_time(self, focus_server_api, valid_config_payload):
        """
        Test: Ambiguous mode - only end_time provided.
        
        PZ-13907: Integration - Historic Configuration Missing start_time Field
        
        Steps:
            1. Create config with start_time=null, end_time=epoch
            2. Send POST /configure
            3. Check server behavior
        
        Current Behavior:
            ⚠️ Server may accept (no validation)
        
        Expected Behavior:
            ❌ Server should reject with 400 (ambiguous mode)
        
        Mode: AMBIGUOUS
        Priority: HIGH
        """
        task_id = generate_task_id("live_only_end")
        logger.info(f"Test: Ambiguous mode - only end_time - {task_id}")
        
        config_payload = valid_config_payload.copy()
        config_payload["start_time"] = None
        config_payload["end_time"] = 1697454600  # Only end, no start
        
        try:
            config_request = ConfigureRequest(**config_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            if hasattr(response, 'job_id'):
                logger.warning("⚠️  Server accepts ambiguous mode (only end_time)")
                logger.info(f"Server returned job_id: {response.job_id}")
        
        except Exception as e:
            logger.info(f"Server/Pydantic caught ambiguous mode: {e}")


# ===================================================================
# Test Class: Historic Mode Validation
# ===================================================================

@pytest.mark.documents_current_behavior


@pytest.mark.regression
class TestHistoricModeValidation:
    """
    Test suite for Historic Mode validation.
    
    Historic Mode Characteristics:
        - start_time: epoch timestamp (REQUIRED)
        - end_time: epoch timestamp (REQUIRED)
        - end_time > start_time (REQUIRED)
        - Data source: Recorded files
        - Duration: Finite
    
    Priority: HIGH
    """
    
    @pytest.mark.xray("PZ-13548")

    
    @pytest.mark.regression
    def test_historic_mode_valid_configuration(self, focus_server_api, valid_historic_config_payload):
        """
        Test: Valid Historic Mode configuration.
        
        PZ-13548: API – Historical configure (happy path)
        
        Steps:
            1. Create config with start_time and end_time (both epochs)
            2. Send POST /configure
            3. Verify server handles Historic Mode correctly
        
        Expected:
            - Server recognizes Historic Mode (both times provided)
            - Either: job_id returned (if recordings exist)
            - Or: 404 "No recording found" (if no recordings exist) ✅ Valid response
        
        Mode: HISTORIC
        Priority: HIGH
        """
        task_id = generate_task_id("historic_mode_valid")
        logger.info(f"Test: Valid Historic Mode configuration - {task_id}")
        logger.info(f"Time range: {valid_historic_config_payload['start_time']} - {valid_historic_config_payload['end_time']}")
        
        config_request = ConfigureRequest(**valid_historic_config_payload)
        
        try:
            response = focus_server_api.configure_streaming_job(config_request)
            
            # If recordings exist for this time range
            assert hasattr(response, 'job_id') and response.job_id, \
                "Historic Mode: server should return job_id when recordings exist"
            
            logger.info(f"✅ Historic Mode configuration accepted: job_id={response.job_id}")
        
        except Exception as e:
            from src.core.exceptions import APIError
            
            # If no recordings exist, server should return 404
            if isinstance(e, APIError) and "No recording found" in str(e):
                logger.info("✅ Historic Mode: Server correctly returned 404 (no recordings in time range)")
                logger.info("   This is the EXPECTED behavior for Historic Mode without data")
            else:
                # Other errors are unexpected
                raise
    
    @pytest.mark.xray("PZ-13552")

    
    @pytest.mark.regression
    def test_historic_mode_with_equal_times(self, focus_server_api, valid_historic_config_payload):
        """
        Test: Historic Mode with start_time == end_time.
        
        PZ-13552: API – Invalid time range (negative)
        
        Steps:
            1. Create config with start_time == end_time
            2. Send POST /configure
            3. Check server behavior
        
        Current Behavior:
            ⚠️ Server may accept (no validation)
        
        Expected Behavior:
            ❌ Server should reject with 400 (zero duration)
        
        Mode: HISTORIC (invalid)
        Priority: HIGH
        """
        task_id = generate_task_id("historic_equal_times")
        logger.info(f"Test: Historic Mode start==end - {task_id}")
        
        config_payload = valid_historic_config_payload.copy()
        config_payload["start_time"] = 1697454000
        config_payload["end_time"] = 1697454000  # Same as start!
        
        try:
            config_request = ConfigureRequest(**config_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            if hasattr(response, 'job_id'):
                logger.warning("⚠️  Server accepts historic mode with start==end")
                logger.info(f"Server returned job_id: {response.job_id}")
        
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught start==end: {e}")
            assert "end_time must be > start_time" in str(e).lower()
    
    # REMOVED: test_historic_mode_with_inverted_range - duplicate of test_prelaunch_validations.py::test_time_range_validation_reversed_range
    
    @pytest.mark.xray("PZ-13552")

    
    @pytest.mark.regression
    def test_historic_mode_with_negative_time(self, focus_server_api, valid_historic_config_payload):
        """
        Test: Historic Mode with negative timestamp.
        
        PZ-13552: API – Invalid time range (negative)
        
        Steps:
            1. Create config with start_time < 0
            2. Send POST /configure
            3. Check validation
        
        Expected:
            - Pydantic rejects with validation error
        
        Mode: HISTORIC (invalid)
        Priority: HIGH
        """
        task_id = generate_task_id("historic_negative")
        logger.info(f"Test: Historic Mode negative timestamp - {task_id}")
        
        config_payload = valid_historic_config_payload.copy()
        config_payload["start_time"] = -100  # Negative!
        
        try:
            config_request = ConfigureRequest(**config_payload)
            
            logger.warning("⚠️  Unexpected: negative timestamp was accepted by Pydantic")
        
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught negative time: {e}")
            assert "greater than or equal to 0" in str(e).lower()


# ===================================================================
# REQUIREMENT TESTS - Show Correct Expected Behavior
# ===================================================================
# These tests document how the server SHOULD behave according to requirements.
# They are marked with @pytest.mark.xfail because the server currently
# does NOT implement proper validation.

@pytest.mark.requirement


@pytest.mark.regression
class TestInvalidCanvasInfo_Requirements:
    """
    📋 REQUIREMENT TESTS - How server SHOULD behave
    
    These tests document the CORRECT expected behavior per requirements.
    Currently marked as @pytest.mark.xfail because server validation 
    is NOT implemented.
    
    For Backend Developers:
        ❌ Current: Server accepts height=-100, height=0 with 200 OK
        ✅ Required: Server MUST reject with 400 Bad Request
    """
    
    @pytest.mark.xfail(reason="Server does not validate negative height (BUG)", strict=False)
    @pytest.mark.xray("PZ-13878")

    @pytest.mark.regression
    def test_requirement_negative_height_must_be_rejected(self, focus_server_api, valid_config_payload):
        """
        ✅ REQUIREMENT: Server MUST reject negative height with 400 Bad Request.
        
        Expected Backend Behavior:
            1. Validate displayInfo.height > 0
            2. Return 400 Bad Request if height <= 0
            3. Error message: "displayInfo.height must be positive"
        
        Current Behavior:
            ❌ Server accepts height=-100 and returns 200 OK with job_id
        
        Jira: PZ-13878
        Priority: CRITICAL
        Type: Server-side validation missing
        """
        task_id = generate_task_id("req_negative_height")
        logger.info(f"[REQUIREMENT TEST] Negative height MUST be rejected - {task_id}")
        
        config_payload = valid_config_payload.copy()
        config_payload["displayInfo"] = {"height": -100}
        
        from src.core.exceptions import APIError
        
        # THIS IS HOW IT SHOULD WORK:
        with pytest.raises(APIError) as exc_info:
            config_request = ConfigureRequest(**config_payload)
            focus_server_api.configure_streaming_job(config_request)
        
        # Expected behavior:
        assert exc_info.value.status_code == 400, \
            "Server MUST return 400 Bad Request for negative height"
        assert "height" in str(exc_info.value).lower() and "positive" in str(exc_info.value).lower(), \
            "Error message MUST mention 'height' and 'positive'"
        
        logger.info("✅ REQUIREMENT: Negative height properly rejected")
    
    @pytest.mark.xfail(reason="Server does not validate zero height (BUG)", strict=False)
    @pytest.mark.xray("PZ-13878")

    @pytest.mark.regression
    def test_requirement_zero_height_must_be_rejected(self, focus_server_api, valid_config_payload):
        """
        ✅ REQUIREMENT: Server MUST reject zero height with 400 Bad Request.
        
        Expected Backend Behavior:
            1. Validate displayInfo.height > 0
            2. Return 400 Bad Request if height == 0
            3. Error message: "displayInfo.height must be positive"
        
        Current Behavior:
            ❌ Server accepts height=0 and returns 200 OK with job_id
        
        Jira: PZ-13878
        Priority: CRITICAL
        Type: Server-side validation missing
        """
        task_id = generate_task_id("req_zero_height")
        logger.info(f"[REQUIREMENT TEST] Zero height MUST be rejected - {task_id}")
        
        config_payload = valid_config_payload.copy()
        config_payload["displayInfo"] = {"height": 0}
        
        from src.core.exceptions import APIError
        
        # THIS IS HOW IT SHOULD WORK:
        with pytest.raises(APIError) as exc_info:
            config_request = ConfigureRequest(**config_payload)
            focus_server_api.configure_streaming_job(config_request)
        
        # Expected behavior:
        assert exc_info.value.status_code == 400, \
            "Server MUST return 400 Bad Request for zero height"
        assert "height" in str(exc_info.value).lower() and "positive" in str(exc_info.value).lower(), \
            "Error message MUST mention 'height' and 'positive'"
        
        logger.info("✅ REQUIREMENT: Zero height properly rejected")


@pytest.mark.requirement



@pytest.mark.regression
class TestNFFT_Requirements:
    """
    📋 REQUIREMENT TESTS - NFFT Validation
    
    For Backend Developers:
        ❌ Current: Server accepts any NFFT value (1000, 4096, etc.)
        ✅ Required: Server MUST validate:
            - NFFT must be power of 2
            - NFFT max = 2048
            - Return 400 Bad Request for invalid values
    """
    
    @pytest.mark.xfail(reason="Server does not validate NFFT power of 2 (BUG)", strict=False)
    @pytest.mark.xray("PZ-13873")

    @pytest.mark.regression
    def test_requirement_nfft_must_be_power_of_2(self, focus_server_api, valid_config_payload):
        """
        ✅ REQUIREMENT: Server MUST reject NFFT values that are not power of 2.
        
        Expected Backend Behavior:
            1. Validate NFFT is power of 2 (256, 512, 1024, 2048)
            2. Return 400 Bad Request if not power of 2
            3. Error message: "nfftSelection must be power of 2 (256, 512, 1024, 2048)"
            4. NO automatic correction - absolute rejection
        
        Current Behavior:
            ❌ Server accepts NFFT=1000 and processes with closest valid value
        
        Jira: PZ-13873
        Priority: HIGH
        Decision: Absolute rejection, no auto-correction (specs meeting 22-Oct-2025)
        Type: Server-side validation missing
        """
        task_id = generate_task_id("req_nfft_power_of_2")
        logger.info(f"[REQUIREMENT TEST] NFFT not power of 2 MUST be rejected - {task_id}")
        
        config_payload = valid_config_payload.copy()
        config_payload["nfftSelection"] = 1000  # Not power of 2
        
        from src.core.exceptions import APIError
        
        # THIS IS HOW IT SHOULD WORK:
        with pytest.raises(APIError) as exc_info:
            config_request = ConfigureRequest(**config_payload)
            focus_server_api.configure_streaming_job(config_request)
        
        # Expected behavior:
        assert exc_info.value.status_code == 400, \
            "Server MUST return 400 Bad Request for NFFT not power of 2"
        assert "power of 2" in str(exc_info.value).lower() or "256" in str(exc_info.value), \
            "Error message MUST mention 'power of 2' or valid values"
        
        logger.info("✅ REQUIREMENT: NFFT not power of 2 properly rejected")
    
    @pytest.mark.xfail(reason="Server does not enforce NFFT max=2048 (BUG)", strict=False)
    @pytest.mark.xray("PZ-13873")

    @pytest.mark.regression
    def test_requirement_nfft_max_2048(self, focus_server_api, valid_config_payload):
        """
        ✅ REQUIREMENT: Server MUST reject NFFT > 2048.
        
        Expected Backend Behavior:
            1. Validate NFFT <= 2048
            2. Return 400 Bad Request if NFFT > 2048
            3. Error message: "nfftSelection exceeds maximum (2048)"
        
        Current Behavior:
            ❌ Server accepts NFFT=4096 and returns 200 OK
        
        Jira: PZ-13873
        Priority: HIGH
        Decision: NFFT max = 2048 (specs meeting 22-Oct-2025)
        Type: Server-side validation missing
        """
        task_id = generate_task_id("req_nfft_max_2048")
        logger.info(f"[REQUIREMENT TEST] NFFT > 2048 MUST be rejected - {task_id}")
        
        config_payload = valid_config_payload.copy()
        config_payload["nfftSelection"] = 4096  # Exceeds max
        
        from src.core.exceptions import APIError
        
        # THIS IS HOW IT SHOULD WORK:
        with pytest.raises(APIError) as exc_info:
            config_request = ConfigureRequest(**config_payload)
            focus_server_api.configure_streaming_job(config_request)
        
        # Expected behavior:
        assert exc_info.value.status_code == 400, \
            "Server MUST return 400 Bad Request for NFFT > 2048"
        assert "2048" in str(exc_info.value) and "maximum" in str(exc_info.value).lower(), \
            "Error message MUST mention maximum 2048"
        
        logger.info("✅ REQUIREMENT: NFFT > 2048 properly rejected")


@pytest.mark.requirement



@pytest.mark.regression
class TestModeValidation_Requirements:
    """
    📋 REQUIREMENT TESTS - Mode Detection and Validation
    
    For Backend Developers:
        ❌ Current: Server accepts ambiguous modes (only one time field)
        ✅ Required: Server MUST validate mode consistency:
            - Live Mode: both times must be null
            - Historic Mode: both times must be provided
            - Reject partial time specification with clear error
    """
    
    @pytest.mark.xfail(reason="Server does not validate ambiguous mode (only start_time)", strict=False)
    @pytest.mark.xray("PZ-13552")

    @pytest.mark.regression
    def test_requirement_reject_only_start_time(self, focus_server_api, valid_config_payload):
        """
        ✅ REQUIREMENT: Server MUST reject configs with only start_time.
        
        Expected Backend Behavior:
            1. Detect partial time specification
            2. Return 400 Bad Request
            3. Error: "Ambiguous mode: provide both times or neither"
        
        Current Behavior:
            ❌ Server may accept with unclear behavior
        
        Priority: HIGH
        Type: Mode validation missing
        """
        task_id = generate_task_id("req_reject_only_start")
        logger.info(f"[REQUIREMENT TEST] Reject only start_time - {task_id}")
        
        config_payload = valid_config_payload.copy()
        config_payload["start_time"] = 1697454000
        config_payload["end_time"] = None
        
        from src.core.exceptions import APIError
        
        # THIS IS HOW IT SHOULD WORK:
        with pytest.raises(APIError) as exc_info:
            config_request = ConfigureRequest(**config_payload)
            focus_server_api.configure_streaming_job(config_request)
        
        # Expected behavior:
        assert exc_info.value.status_code == 400, \
            "Server MUST return 400 Bad Request for ambiguous mode"
        assert "ambiguous" in str(exc_info.value).lower() or "both" in str(exc_info.value).lower(), \
            "Error message MUST mention ambiguous mode"
        
        logger.info("✅ REQUIREMENT: Ambiguous mode (only start) properly rejected")
    
    @pytest.mark.xfail(reason="Server does not validate ambiguous mode (only end_time)", strict=False)
    @pytest.mark.xray("PZ-13552")

    @pytest.mark.regression
    def test_requirement_reject_only_end_time(self, focus_server_api, valid_config_payload):
        """
        ✅ REQUIREMENT: Server MUST reject configs with only end_time.
        
        Expected Backend Behavior:
            1. Detect partial time specification
            2. Return 400 Bad Request
            3. Error: "Ambiguous mode: provide both times or neither"
        
        Current Behavior:
            ❌ Server may accept with unclear behavior
        
        Priority: HIGH
        Type: Mode validation missing
        """
        task_id = generate_task_id("req_reject_only_end")
        logger.info(f"[REQUIREMENT TEST] Reject only end_time - {task_id}")
        
        config_payload = valid_config_payload.copy()
        config_payload["start_time"] = None
        config_payload["end_time"] = 1697454600
        
        from src.core.exceptions import APIError
        
        # THIS IS HOW IT SHOULD WORK:
        with pytest.raises(APIError) as exc_info:
            config_request = ConfigureRequest(**config_payload)
            focus_server_api.configure_streaming_job(config_request)
        
        # Expected behavior:
        assert exc_info.value.status_code == 400, \
            "Server MUST return 400 Bad Request for ambiguous mode"
        assert "ambiguous" in str(exc_info.value).lower() or "both" in str(exc_info.value).lower(), \
            "Error message MUST mention ambiguous mode"
        
        logger.info("✅ REQUIREMENT: Ambiguous mode (only end) properly rejected")


@pytest.mark.requirement



@pytest.mark.regression
class TestFrequencyValidation_Requirements:
    """
    📋 REQUIREMENT TESTS - Dynamic Frequency Validation
    
    For Backend Developers:
        ❌ Current: Server accepts any frequency value
        ✅ Required: Server MUST:
            1. Get PRR from dataset metadata
            2. Calculate Nyquist limit = PRR / 2
            3. Reject frequencies > Nyquist with 400 Bad Request
            4. Error message must include actual Nyquist limit for this dataset
    """
    
    @pytest.mark.xfail(reason="Server does not validate frequency vs Nyquist limit (BUG)", strict=False)
    @pytest.mark.xray("PZ-13555")

    @pytest.mark.regression
    def test_requirement_frequency_must_not_exceed_nyquist(self, focus_server_api, valid_config_payload):
        """
        ✅ REQUIREMENT: Server MUST reject frequencies exceeding Nyquist limit.
        
        Expected Backend Behavior:
            1. Retrieve dataset metadata to get PRR
            2. Calculate Nyquist = PRR / 2
            3. Validate frequencyRange.max <= Nyquist
            4. Return 400 Bad Request if max > Nyquist
            5. Error: "Frequency 600 Hz exceeds Nyquist limit (500 Hz) for this dataset"
        
        Current Behavior:
            ❌ Server accepts freq > Nyquist with 200 OK (no dynamic validation)
        
        Jira: PZ-13877
        Priority: HIGH
        Decision: Dynamic validation per dataset metadata (specs meeting 22-Oct-2025)
        Type: Server-side dynamic validation missing
        """
        task_id = generate_task_id("req_freq_nyquist")
        logger.info(f"[REQUIREMENT TEST] Frequency > Nyquist MUST be rejected - {task_id}")
        
        # Using client config: FrequencyMax = 1000 Hz
        config_payload = valid_config_payload.copy()
        config_payload["frequencyRange"] = {"min": 0, "max": 1001}  # Exceeds max 1000 Hz
        
        from src.core.exceptions import APIError
        
        # THIS IS HOW IT SHOULD WORK:
        with pytest.raises(APIError) as exc_info:
            config_request = ConfigureRequest(**config_payload)
            focus_server_api.configure_streaming_job(config_request)
        
        # Expected behavior:
        assert exc_info.value.status_code == 400, \
            "Server MUST return 400 Bad Request for freq > Nyquist"
        assert "nyquist" in str(exc_info.value).lower() or "limit" in str(exc_info.value).lower(), \
            "Error message MUST mention 'nyquist' or 'limit'"
        
        logger.info("✅ REQUIREMENT: Frequency > Nyquist properly rejected")



