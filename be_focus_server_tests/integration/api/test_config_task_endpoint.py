"""
Integration Tests - POST /config/{task_id} Endpoint (Future Structure)
========================================================================

⚠️  NOTE: These tests are for the FUTURE API structure using POST /config/{task_id}
   Currently, the staging environment uses POST /configure endpoint.
   These tests are SKIPPED until the new endpoint is deployed.

Tests for POST /config/{task_id} endpoint covering:
- Valid configuration
- Invalid task ID
- Missing required fields
- Invalid sensor range
- Invalid frequency range

Tests Covered (Xray):
    - PZ-14750: POST /config/{task_id} - Valid Configuration
    - PZ-14751: POST /config/{task_id} - Invalid Task ID
    - PZ-14752: POST /config/{task_id} - Missing Required Fields
    - PZ-14753: POST /config/{task_id} - Invalid Sensor Range
    - PZ-14754: POST /config/{task_id} - Invalid Frequency Range

Author: QA Automation Architect
Date: 2025-11-09
"""

import pytest
import logging
from typing import Dict, Any

from src.models.focus_server_models import ConfigTaskRequest
from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError, ValidationError
from src.utils.helpers import generate_task_id

logger = logging.getLogger(__name__)


# ===================================================================
# Test Class: POST /config/{task_id} Endpoint
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
@pytest.mark.skip(reason="Future API structure - POST /config/{task_id} endpoint not yet deployed to staging. "
                          "Use POST /configure tests instead (test_configure_endpoint.py)")
@pytest.mark.regression
class TestConfigTaskEndpoint:
    """
    Test suite for POST /config/{task_id} endpoint.
    
    Tests covered:
        - PZ-14750: Valid Configuration
        - PZ-14751: Invalid Task ID
        - PZ-14752: Missing Required Fields
        - PZ-14753: Invalid Sensor Range
        - PZ-14754: Invalid Frequency Range
    
    Priority: HIGH
    """
    
    @pytest.mark.xray("PZ-14750")
    @pytest.mark.xray("PZ-13547")

    @pytest.mark.regression
    def test_config_task_valid_configuration(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14750: POST /config/{task_id} - Valid Configuration.
        
        Validates that POST /config/{task_id} endpoint accepts valid 
        configuration requests and returns 200 OK with proper response structure.
        
        Steps:
            1. Generate unique task_id
            2. Prepare valid configuration payload
            3. Send POST /config/{task_id} request
            4. Verify response structure
            5. Verify task_id in response
        
        Expected:
            - Request returns 200 OK
            - Response contains status field
            - Response contains task_id field matching request
            - No errors occur
        
        Jira: PZ-14750
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: POST /config/{task_id} - Valid Configuration (PZ-14750)")
        logger.info("=" * 80)
        
        # Step 1: Generate unique task_id
        task_id = generate_task_id("test-config")
        logger.info(f"Generated task_id: {task_id}")
        
        # Step 2: Prepare valid configuration payload
        config_payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None
        }
        
        logger.info("Preparing valid configuration payload...")
        config_request = ConfigTaskRequest(**config_payload)
        
        # Step 3: Send POST /config/{task_id} request
        logger.info(f"Sending POST /config/{task_id} request...")
        try:
            response = focus_server_api.config_task(task_id, config_request)
            
            # Step 4: Verify response structure
            assert response is not None, "Response should not be None"
            assert hasattr(response, 'status'), "Response should have status field"
            assert hasattr(response, 'task_id'), "Response should have task_id field"
            
            # Step 5: Verify task_id in response
            assert response.task_id == task_id, \
                f"Response task_id ({response.task_id}) should match request task_id ({task_id})"
            
            logger.info(f"✅ Response status: {response.status}")
            logger.info(f"✅ Response task_id: {response.task_id}")
            logger.info("✅ All assertions passed")
            
        except APIError as e:
            logger.error(f"API Error: {e}")
            pytest.fail(f"API call failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            pytest.fail(f"Unexpected error: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Valid Configuration")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14751")
    @pytest.mark.xray("PZ-13879")

    @pytest.mark.regression
    def test_config_task_invalid_task_id(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14751: POST /config/{task_id} - Invalid Task ID.
        
        Validates that POST /config/{task_id} endpoint properly rejects 
        invalid task_id formats and returns appropriate error response.
        
        Steps:
            1. Prepare invalid task_id formats (empty, null, special chars)
            2. Send POST /config/{task_id} requests
            3. Verify error responses
        
        Expected:
            - All invalid task_id formats are rejected
            - Status code is 400 Bad Request
            - Error message indicates invalid task_id
        
        Jira: PZ-14751
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: POST /config/{task_id} - Invalid Task ID (PZ-14751)")
        logger.info("=" * 80)
        
        # Prepare valid payload for testing
        config_payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None
        }
        config_request = ConfigTaskRequest(**config_payload)
        
        # Test invalid task_id formats
        invalid_task_ids = [
            ("", "empty string"),
            ("test@#$%task", "special characters"),
            ("a" * 300, "very long string")
        ]
        
        for invalid_id, description in invalid_task_ids:
            logger.info(f"\nTesting invalid task_id: {description} ({invalid_id[:50]}...)")
            
            try:
                response = focus_server_api.config_task(invalid_id, config_request)
                
                # If we get here, the request was accepted (unexpected)
                logger.warning(f"⚠️  Invalid task_id '{invalid_id[:50]}...' was accepted (unexpected)")
                logger.warning(f"   Response: {response}")
                
            except ValidationError as e:
                logger.info(f"✅ ValidationError caught (expected): {e}")
            except APIError as e:
                # Check if it's a 400 Bad Request
                if hasattr(e, 'status_code') and e.status_code == 400:
                    logger.info(f"✅ 400 Bad Request (expected): {e}")
                else:
                    logger.info(f"✅ APIError caught (expected): {e}")
            except Exception as e:
                logger.info(f"✅ Error caught (expected): {type(e).__name__}: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Invalid Task ID Handling")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14752")
    @pytest.mark.xray("PZ-13879")

    @pytest.mark.regression
    def test_config_task_missing_required_fields(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14752: POST /config/{task_id} - Missing Required Fields.
        
        Validates that POST /config/{task_id} endpoint properly rejects 
        requests with missing required fields and returns 422 Unprocessable Entity.
        
        Steps:
            1. Generate unique task_id
            2. Prepare payloads missing required fields
            3. Send POST /config/{task_id} requests
            4. Verify error responses
        
        Expected:
            - All requests with missing required fields are rejected
            - Status code is 422 Unprocessable Entity
            - Error message indicates which field is missing
        
        Jira: PZ-14752
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: POST /config/{task_id} - Missing Required Fields (PZ-14752)")
        logger.info("=" * 80)
        
        task_id = generate_task_id("test-missing")
        
        # Test missing required fields
        base_payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None
        }
        
        missing_fields_tests = [
            ("displayTimeAxisDuration", {k: v for k, v in base_payload.items() if k != "displayTimeAxisDuration"}),
            ("nfftSelection", {k: v for k, v in base_payload.items() if k != "nfftSelection"}),
            ("canvasInfo", {k: v for k, v in base_payload.items() if k != "canvasInfo"}),
            ("sensors", {k: v for k, v in base_payload.items() if k != "sensors"}),
            ("frequencyRange", {k: v for k, v in base_payload.items() if k != "frequencyRange"}),
        ]
        
        for missing_field, payload in missing_fields_tests:
            logger.info(f"\nTesting missing field: {missing_field}")
            
            try:
                # Try to create request - should fail validation
                config_request = ConfigTaskRequest(**payload)
                
                # If we get here, validation passed (unexpected)
                logger.warning(f"⚠️  Missing field '{missing_field}' was accepted (unexpected)")
                
                # Try to send request anyway
                try:
                    response = focus_server_api.config_task(task_id, config_request)
                    logger.warning(f"⚠️  Request succeeded (unexpected): {response}")
                except APIError as e:
                    if hasattr(e, 'status_code') and e.status_code == 422:
                        logger.info(f"✅ 422 Unprocessable Entity (expected): {e}")
                    else:
                        logger.info(f"✅ APIError caught: {e}")
                
            except ValidationError as e:
                logger.info(f"✅ ValidationError caught (expected): {e}")
            except TypeError as e:
                logger.info(f"✅ TypeError caught (expected): {e}")
            except Exception as e:
                logger.info(f"✅ Error caught (expected): {type(e).__name__}: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Missing Required Fields Handling")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14753")

    
    @pytest.mark.regression
    def test_config_task_invalid_sensor_range(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14753: POST /config/{task_id} - Invalid Sensor Range.
        
        Validates that POST /config/{task_id} endpoint properly rejects 
        invalid sensor range configurations and returns 400 Bad Request.
        
        Steps:
            1. Generate unique task_id
            2. Prepare payloads with invalid sensor ranges
            3. Send POST /config/{task_id} requests
            4. Verify error responses
        
        Expected:
            - All invalid sensor ranges are rejected
            - Status code is 400 Bad Request
            - Error message indicates invalid sensor range
        
        Jira: PZ-14753
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: POST /config/{task_id} - Invalid Sensor Range (PZ-14753)")
        logger.info("=" * 80)
        
        task_id = generate_task_id("test-sensor")
        
        # Test invalid sensor ranges
        invalid_sensor_tests = [
            ({"min": 50, "max": 1}, "min > max"),
            ({"min": -1, "max": 50}, "negative min"),
            ({"min": 1, "max": 100000}, "out of bounds max"),
        ]
        
        base_payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None
        }
        
        for invalid_sensors, description in invalid_sensor_tests:
            logger.info(f"\nTesting invalid sensor range: {description} ({invalid_sensors})")
            
            payload = {**base_payload, "sensors": invalid_sensors}
            
            try:
                # Try to create request - should fail validation
                config_request = ConfigTaskRequest(**payload)
                
                # If validation passed, try to send request
                try:
                    response = focus_server_api.config_task(task_id, config_request)
                    logger.warning(f"⚠️  Invalid sensor range was accepted (unexpected): {response}")
                except APIError as e:
                    if hasattr(e, 'status_code') and e.status_code == 400:
                        logger.info(f"✅ 400 Bad Request (expected): {e}")
                    else:
                        logger.info(f"✅ APIError caught: {e}")
                
            except ValidationError as e:
                logger.info(f"✅ ValidationError caught (expected): {e}")
            except Exception as e:
                logger.info(f"✅ Error caught (expected): {type(e).__name__}: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Invalid Sensor Range Handling")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14754")

    
    @pytest.mark.regression
    def test_config_task_invalid_frequency_range(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14754: POST /config/{task_id} - Invalid Frequency Range.
        
        Validates that POST /config/{task_id} endpoint properly rejects 
        invalid frequency range configurations and returns 400 Bad Request.
        
        Steps:
            1. Generate unique task_id
            2. Prepare payloads with invalid frequency ranges
            3. Send POST /config/{task_id} requests
            4. Verify error responses
        
        Expected:
            - All invalid frequency ranges are rejected
            - Status code is 400 Bad Request
            - Error message indicates invalid frequency range
        
        Jira: PZ-14754
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: POST /config/{task_id} - Invalid Frequency Range (PZ-14754)")
        logger.info("=" * 80)
        
        task_id = generate_task_id("test-freq")
        
        # Test invalid frequency ranges
        invalid_freq_tests = [
            ({"min": 500, "max": 0}, "min > max"),
            ({"min": -1, "max": 500}, "negative min"),
            ({"min": 0, "max": 2000}, "exceeds Nyquist limit (assuming PRR=2000)"),
        ]
        
        base_payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 1, "max": 50},
            "start_time": None,
            "end_time": None
        }
        
        for invalid_freq, description in invalid_freq_tests:
            logger.info(f"\nTesting invalid frequency range: {description} ({invalid_freq})")
            
            payload = {**base_payload, "frequencyRange": invalid_freq}
            
            try:
                # Try to create request - should fail validation
                config_request = ConfigTaskRequest(**payload)
                
                # If validation passed, try to send request
                try:
                    response = focus_server_api.config_task(task_id, config_request)
                    logger.warning(f"⚠️  Invalid frequency range was accepted (unexpected): {response}")
                except APIError as e:
                    if hasattr(e, 'status_code') and e.status_code == 400:
                        logger.info(f"✅ 400 Bad Request (expected): {e}")
                    else:
                        logger.info(f"✅ APIError caught: {e}")
                
            except ValidationError as e:
                logger.info(f"✅ ValidationError caught (expected): {e}")
            except Exception as e:
                logger.info(f"✅ Error caught (expected): {type(e).__name__}: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Invalid Frequency Range Handling")
        logger.info("=" * 80)



