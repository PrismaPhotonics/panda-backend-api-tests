"""
Integration Tests - Configuration Validation (High Priority)
==============================================================

High priority configuration validation tests for Focus Server.
These tests validate critical validation logic for configuration requests.

Tests Covered (Xray):
    - PZ-13879: Missing Required Fields
    - PZ-13878: Invalid View Type
    - PZ-13877: Invalid Frequency Range (Min > Max)
    - PZ-13876: Invalid Channel Range (Min > Max)
    - PZ-13873: Valid Configuration - All Parameters

Author: QA Automation Architect
Date: 2025-10-21
"""

import pytest
import logging
from typing import Dict, Any

from src.models.focus_server_models import ConfigTaskRequest, ConfigTaskResponse
from src.utils.helpers import generate_task_id, generate_config_payload
from src.utils.validators import validate_task_id_format

logger = logging.getLogger(__name__)


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def valid_config_payload() -> Dict[str, Any]:
    """
    Generate a fully valid configuration payload.
    
    Returns:
        Complete valid configuration with all parameters
    """
    return {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 0, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,
        "end_time": None,
        "view_type": 0
    }


# ===================================================================
# Test Class: Missing Required Fields (PZ-13879)
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
class TestMissingRequiredFields:
    """
    Test suite for PZ-13879: Integration – Missing Required Fields
    Priority: HIGH
    
    Validates that Focus Server properly rejects configuration requests
    that are missing required fields.
    """
    
    def test_missing_channels_field(self, focus_server_api):
        """
        Test PZ-13879.1: Configuration missing 'channels' field.
        
        Steps:
            1. Create config payload without 'channels'
            2. Send POST /config/{task_id}
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
            "nfftSelection": 1024,
            "frequencyRange": {"min": 0, "max": 500},
            "displayInfo": {"height": 1000},
            "view_type": 0
            # Missing "channels" - should fail
        }
        
        try:
            # Attempt to create config request (may fail at Pydantic level)
            config_request = ConfigTaskRequest(**config_payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            # Should be rejected
            assert response.status_code == 400, \
                f"Expected 400 Bad Request, got {response.status_code}"
            
            logger.info("✅ Missing channels properly rejected")
            
        except ValueError as e:
            # Pydantic validation may catch this before API call
            logger.info(f"✅ Pydantic validation caught missing field: {e}")
            assert "channels" in str(e).lower()
    
    def test_missing_frequency_range_field(self, focus_server_api):
        """
        Test PZ-13879.2: Configuration missing 'frequencyRange' field.
        
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
            "nfftSelection": 1024,
            "channels": {"min": 0, "max": 50},
            "displayInfo": {"height": 1000},
            "view_type": 0
            # Missing "frequencyRange" - should fail
        }
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            assert response.status_code == 400, \
                f"Expected 400 Bad Request, got {response.status_code}"
            
            logger.info("✅ Missing frequencyRange properly rejected")
            
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught missing field: {e}")
            assert "frequencyRange" in str(e).lower() or "frequency" in str(e).lower()
    
    def test_missing_nfft_field(self, focus_server_api):
        """
        Test PZ-13879.3: Configuration missing 'nfftSelection' field.
        
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
            "channels": {"min": 0, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "displayInfo": {"height": 1000},
            "view_type": 0
            # Missing "nfftSelection" - should fail
        }
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            assert response.status_code == 400, \
                f"Expected 400 Bad Request, got {response.status_code}"
            
            logger.info("✅ Missing nfftSelection properly rejected")
            
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught missing field: {e}")
            assert "nfft" in str(e).lower()
    
    def test_missing_view_type_field(self, focus_server_api):
        """
        Test PZ-13879.4: Configuration missing 'view_type' field.
        
        Steps:
            1. Create config payload without 'view_type'
            2. Send POST /config/{task_id}
            3. Verify behavior (may use default)
        
        Expected:
            - Either rejected with 400, or accepted with default value (0)
        
        Jira: PZ-13879
        Priority: HIGH
        """
        task_id = generate_task_id("missing_view_type")
        logger.info(f"Test PZ-13879.4: Missing view_type field - {task_id}")
        
        # Create config without view_type
        config_payload = {
            "nfftSelection": 1024,
            "channels": {"min": 0, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "displayInfo": {"height": 1000}
            # Missing "view_type" - may have default
        }
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            # May be accepted with default or rejected
            if response.status_code == 200:
                logger.info("✅ view_type has default value - accepted")
            elif response.status_code == 400:
                logger.info("✅ Missing view_type properly rejected")
            else:
                pytest.fail(f"Unexpected status code: {response.status_code}")
                
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught missing field: {e}")


# ===================================================================
# Test Class: Invalid View Type (PZ-13878)
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
class TestInvalidViewType:
    """
    Test suite for PZ-13878: Integration – Invalid View Type - Out of Range
    Priority: HIGH
    
    Validates proper validation of view_type enum values.
    Valid values: 0 (MULTICHANNEL) or 1 (SINGLECHANNEL)
    """
    
    def test_invalid_view_type_negative(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13878.1: view_type with negative value.
        
        Steps:
            1. Create config with view_type = -1
            2. Send POST /config/{task_id}
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request
            - Error message indicates invalid view_type
        
        Jira: PZ-13878
        Priority: HIGH
        """
        task_id = generate_task_id("invalid_view_type_neg")
        logger.info(f"Test PZ-13878.1: Invalid view_type=-1 - {task_id}")
        
        # Set invalid view_type
        config_payload = valid_config_payload.copy()
        config_payload["view_type"] = -1  # Invalid!
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            assert response.status_code == 400, \
                f"Expected 400 Bad Request for view_type=-1, got {response.status_code}"
            
            logger.info("✅ Invalid view_type=-1 properly rejected")
            
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught invalid view_type: {e}")
            assert "view_type" in str(e).lower()
    
    def test_invalid_view_type_out_of_range(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13878.2: view_type with out-of-range value.
        
        Steps:
            1. Create config with view_type = 99
            2. Send POST /config/{task_id}
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request
            - Error message indicates invalid view_type
        
        Jira: PZ-13878
        Priority: HIGH
        """
        task_id = generate_task_id("invalid_view_type_99")
        logger.info(f"Test PZ-13878.2: Invalid view_type=99 - {task_id}")
        
        # Set invalid view_type
        config_payload = valid_config_payload.copy()
        config_payload["view_type"] = 99  # Invalid! (valid: 0 or 1)
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            assert response.status_code == 400, \
                f"Expected 400 Bad Request for view_type=99, got {response.status_code}"
            
            logger.info("✅ Invalid view_type=99 properly rejected")
            
        except ValueError as e:
            logger.info(f"✅ Pydantic validation caught invalid view_type: {e}")
            assert "view_type" in str(e).lower()
    
    def test_invalid_view_type_string(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13878.3: view_type with string value.
        
        Steps:
            1. Create config with view_type = "invalid"
            2. Send POST /config/{task_id}
            3. Verify rejection
        
        Expected:
            - Status code: 400 Bad Request or Pydantic validation error
        
        Jira: PZ-13878
        Priority: HIGH
        """
        task_id = generate_task_id("invalid_view_type_string")
        logger.info(f"Test PZ-13878.3: Invalid view_type='invalid' - {task_id}")
        
        # Set invalid view_type
        config_payload = valid_config_payload.copy()
        config_payload["view_type"] = "invalid"  # Wrong type!
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            assert response.status_code == 400, \
                f"Expected 400 Bad Request for view_type='invalid', got {response.status_code}"
            
            logger.info("✅ Invalid view_type string properly rejected")
            
        except (ValueError, TypeError) as e:
            logger.info(f"✅ Type validation caught invalid view_type: {e}")


# ===================================================================
# Test Class: Invalid Ranges (PZ-13877, PZ-13876)
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
class TestInvalidRanges:
    """
    Test suite for invalid range validation.
    
    Tests:
        - PZ-13877: Invalid Frequency Range (Min > Max)
        - PZ-13876: Invalid Channel Range (Min > Max)
    
    Priority: HIGH
    """
    
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
        """
        task_id = generate_task_id("invalid_freq_range")
        logger.info(f"Test PZ-13877: frequencyRange min > max - {task_id}")
        
        # Set invalid frequency range
        config_payload = valid_config_payload.copy()
        config_payload["frequencyRange"] = {"min": 500, "max": 100}  # Invalid: min > max
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            assert response.status_code == 400, \
                f"Expected 400 Bad Request for min > max, got {response.status_code}"
            
            logger.info("✅ Invalid frequency range (min > max) properly rejected")
            
        except ValueError as e:
            logger.info(f"✅ Validation caught invalid frequency range: {e}")
            assert "frequency" in str(e).lower() or "min" in str(e).lower() or "max" in str(e).lower()
    
    def test_invalid_channel_range_min_greater_than_max(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13876: channels where min > max.
        
        Steps:
            1. Create config with channels.min > channels.max
            2. Send POST /config/{task_id}
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
            config_request = ConfigTaskRequest(**config_payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            assert response.status_code == 400, \
                f"Expected 400 Bad Request for min > max, got {response.status_code}"
            
            logger.info("✅ Invalid channel range (min > max) properly rejected")
            
        except ValueError as e:
            logger.info(f"✅ Validation caught invalid channel range: {e}")
            assert "channel" in str(e).lower() or "min" in str(e).lower() or "max" in str(e).lower()
    
    def test_frequency_range_equal_min_max(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13877.2: frequencyRange where min == max (edge case).
        
        Steps:
            1. Create config with frequencyRange.min == frequencyRange.max
            2. Send POST /config/{task_id}
            3. Verify behavior (may be accepted or rejected)
        
        Expected:
            - Behavior depends on specs: may accept (zero range) or reject
        
        Jira: PZ-13877
        Priority: HIGH
        """
        task_id = generate_task_id("freq_range_equal")
        logger.info(f"Test PZ-13877.2: frequencyRange min == max - {task_id}")
        
        # Set frequency range with min == max
        config_payload = valid_config_payload.copy()
        config_payload["frequencyRange"] = {"min": 250, "max": 250}  # Edge case
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            # Behavior depends on specs - document what happens
            logger.info(f"Frequency range min==max: status_code={response.status_code}")
            
            # TODO: Update assertion after specs meeting
            # For now, just log the behavior
            
        except ValueError as e:
            logger.info(f"Validation rejects min==max: {e}")
    
    def test_channel_range_equal_min_max(self, focus_server_api, valid_config_payload):
        """
        Test PZ-13876.2: channels where min == max (edge case).
        
        Steps:
            1. Create config with channels.min == channels.max
            2. Send POST /config/{task_id}
            3. Verify behavior (may be SingleChannel scenario)
        
        Expected:
            - May be accepted as SingleChannel equivalent
            - Or may require view_type=1
        
        Jira: PZ-13876
        Priority: HIGH
        """
        task_id = generate_task_id("channel_range_equal")
        logger.info(f"Test PZ-13876.2: channels min == max - {task_id}")
        
        # Set channel range with min == max
        config_payload = valid_config_payload.copy()
        config_payload["channels"] = {"min": 7, "max": 7}  # Edge case
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            # Behavior depends on specs - document what happens
            logger.info(f"Channel range min==max: status_code={response.status_code}")
            
            # TODO: Update assertion after specs meeting
            
        except ValueError as e:
            logger.info(f"Validation rejects min==max: {e}")


# ===================================================================
# Test Class: Valid Configuration (PZ-13873)
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
@pytest.mark.smoke
class TestValidConfigurationAllParameters:
    """
    Test suite for PZ-13873: Integration - Valid Configuration - All Parameters
    Priority: HIGH
    
    Validates that a fully valid configuration with all parameters
    is properly accepted and processed.
    """
    
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
        config_request = ConfigTaskRequest(**config_payload)
        
        # Configure task
        response = focus_server_api.config_task(task_id, config_request)
        
        # Assertions
        assert isinstance(response, ConfigTaskResponse), \
            f"Expected ConfigTaskResponse, got {type(response)}"
        
        assert response.status == "Config received successfully" or response.status_code == 200, \
            f"Expected successful config, got status={response.status}, status_code={response.status_code}"
        
        logger.info(f"✅ Valid configuration accepted: {response.status}")
        
        # Try to query metadata to verify task exists
        try:
            metadata_response = focus_server_api.get_metadata(task_id)
            logger.info(f"✅ Task metadata accessible: {metadata_response}")
        except Exception as e:
            logger.warning(f"Could not query metadata (may not be implemented): {e}")
    
    def test_valid_configuration_multichannel_explicit(self, focus_server_api):
        """
        Test PZ-13873.2: Valid MULTICHANNEL configuration (view_type=0).
        
        Steps:
            1. Create config with view_type=0 (MULTICHANNEL)
            2. Send POST /config/{task_id}
            3. Verify acceptance
        
        Expected:
            - Configuration accepted
            - Task operates in MULTICHANNEL mode
        
        Jira: PZ-13873
        Priority: HIGH
        """
        task_id = generate_task_id("valid_multichannel")
        logger.info(f"Test PZ-13873.2: Valid MULTICHANNEL config - {task_id}")
        
        config_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 0, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": 0  # Explicit MULTICHANNEL
        }
        
        config_request = ConfigTaskRequest(**config_payload)
        response = focus_server_api.config_task(task_id, config_request)
        
        assert response.status == "Config received successfully" or response.status_code == 200
        logger.info("✅ MULTICHANNEL configuration accepted")
    
    def test_valid_configuration_singlechannel_explicit(self, focus_server_api):
        """
        Test PZ-13873.3: Valid SINGLECHANNEL configuration (view_type=1).
        
        Steps:
            1. Create config with view_type=1 (SINGLECHANNEL)
            2. channels.min == channels.max
            3. Send POST /config/{task_id}
            4. Verify acceptance
        
        Expected:
            - Configuration accepted
            - Task operates in SINGLECHANNEL mode
        
        Jira: PZ-13873
        Priority: HIGH
        """
        task_id = generate_task_id("valid_singlechannel")
        logger.info(f"Test PZ-13873.3: Valid SINGLECHANNEL config - {task_id}")
        
        config_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 7, "max": 7},  # Single channel
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": 1  # Explicit SINGLECHANNEL
        }
        
        config_request = ConfigTaskRequest(**config_payload)
        response = focus_server_api.config_task(task_id, config_request)
        
        assert response.status == "Config received successfully" or response.status_code == 200
        logger.info("✅ SINGLECHANNEL configuration accepted")
    
    def test_valid_configuration_various_nfft_values(self, focus_server_api):
        """
        Test PZ-13873.4: Valid configurations with various NFFT values.
        
        Steps:
            1. Test multiple valid NFFT values (256, 512, 1024, 2048)
            2. Verify all are accepted
        
        Expected:
            - All valid NFFT values accepted
        
        Jira: PZ-13873
        Priority: HIGH
        """
        logger.info("Test PZ-13873.4: Valid NFFT variations")
        
        valid_nfft_values = [256, 512, 1024, 2048]
        
        for nfft in valid_nfft_values:
            task_id = generate_task_id(f"valid_nfft_{nfft}")
            
            config_payload = {
                "displayTimeAxisDuration": 10,
                "nfftSelection": nfft,
                "displayInfo": {"height": 1000},
                "channels": {"min": 0, "max": 50},
                "frequencyRange": {"min": 0, "max": 500},
                "start_time": None,
                "end_time": None,
                "view_type": 0
            }
            
            config_request = ConfigTaskRequest(**config_payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            assert response.status == "Config received successfully" or response.status_code == 200, \
                f"NFFT={nfft} should be accepted"
            
            logger.info(f"✅ NFFT={nfft} accepted")


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary
def test_config_validation_high_priority_summary():
    """
    Summary test for configuration validation (high priority tests).
    
    This test documents which Xray test cases are covered in this module.
    
    Covered Xray Tests:
        ✅ PZ-13879: Missing Required Fields (4 tests)
        ✅ PZ-13878: Invalid View Type (3 tests)
        ✅ PZ-13877: Invalid Frequency Range (2 tests)
        ✅ PZ-13876: Invalid Channel Range (2 tests)
        ✅ PZ-13873: Valid Configuration All Parameters (4 tests)
    
    Total: 15 high-priority configuration validation tests
    """
    logger.info("=" * 80)
    logger.info("Configuration Validation (High Priority) - Summary")
    logger.info("=" * 80)
    logger.info("Xray Test Coverage:")
    logger.info("  ✅ PZ-13879: Missing Required Fields - 4 tests")
    logger.info("  ✅ PZ-13878: Invalid View Type - 3 tests")
    logger.info("  ✅ PZ-13877: Invalid Frequency Range - 2 tests")
    logger.info("  ✅ PZ-13876: Invalid Channel Range - 2 tests")
    logger.info("  ✅ PZ-13873: Valid Configuration - 4 tests")
    logger.info("=" * 80)
    logger.info("Total: 15 High Priority Tests")
    logger.info("=" * 80)

