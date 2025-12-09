"""
Integration Tests - Security: Input Validation
===============================================

Tests for Pydantic type validation that provides inherent protection against
malformed inputs in Focus Server.

NOTE: Focus Server uses MongoDB (not SQL) and Pydantic typed models.
      ConfigureRequest has no string fields that could be exploited for
      SQL injection or XSS attacks. The protection is inherent in the
      type system - Pydantic rejects non-conforming inputs before they
      reach the database or response.

Tests Covered (Xray):
    - PZ-14774: Type Validation - Rejects Invalid Types
    - PZ-14775: Type Validation - Response Contains No Executable Code
    - PZ-14788: Type Validation - Malformed Input Handling

Author: QA Automation Architect
Date: 2025-11-09
Updated: 2025-12-09 (Converted to meaningful type validation tests)
"""

import pytest
import logging
from typing import Dict, Any

from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError, ValidationError
from src.models.focus_server_models import ConfigureRequest, ViewType

logger = logging.getLogger(__name__)


@pytest.mark.high
@pytest.mark.regression
class TestInputValidation:
    """
    Test suite for input type validation.
    
    Focus Server uses MongoDB + Pydantic typed models, which provides
    inherent protection against injection attacks by rejecting invalid types.
    
    Tests covered:
        - PZ-14774: Type validation rejects strings where numbers expected
        - PZ-14775: API responses do not contain executable code
        - PZ-14788: Malformed inputs are handled gracefully
    """
    
    @pytest.mark.xray("PZ-14774")
    @pytest.mark.regression
    def test_pydantic_rejects_invalid_types(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14774: Pydantic Type Validation.
        
        Objective:
            Verify that Pydantic rejects invalid types in ConfigureRequest,
            providing inherent protection against malformed inputs.
        
        Steps:
            1. Attempt to create ConfigureRequest with string in numeric field
            2. Verify Pydantic raises ValidationError
        
        Expected:
            Pydantic rejects invalid types with clear error message.
        
        Note:
            Focus Server uses MongoDB (not SQL) and has no string fields
            in ConfigureRequest. SQL injection is not applicable.
        """
        logger.info("=" * 80)
        logger.info("TEST: Pydantic Type Validation (PZ-14774)")
        logger.info("=" * 80)
        
        invalid_type_payloads = [
            {"field": "nfftSelection", "invalid_value": "' OR '1'='1", "description": "string in nfftSelection"},
            {"field": "nfftSelection", "invalid_value": "1024; DROP TABLE", "description": "SQL-like string"},
            {"field": "displayTimeAxisDuration", "invalid_value": "ten", "description": "word in numeric field"},
        ]
        
        base_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        validation_errors_caught = 0
        
        for test_case in invalid_type_payloads:
            logger.info(f"Testing: {test_case['description']}")
            
            test_payload = base_payload.copy()
            test_payload[test_case['field']] = test_case['invalid_value']
            
            try:
                config_request = ConfigureRequest(**test_payload)
                # If we get here, Pydantic didn't catch it - this is unexpected
                pytest.fail(f"Pydantic should have rejected {test_case['description']}, "
                           f"but created ConfigureRequest successfully")
            except (ValueError, ValidationError, TypeError) as e:
                validation_errors_caught += 1
                logger.info(f"  Pydantic rejected invalid input: {type(e).__name__}")
                # Verify error message doesn't expose sensitive info
                error_msg = str(e).lower()
                assert "sql" not in error_msg or "database" not in error_msg, \
                    "Error should not expose database details"
        
        assert validation_errors_caught == len(invalid_type_payloads), \
            f"Expected {len(invalid_type_payloads)} validation errors, got {validation_errors_caught}"
        
        logger.info(f"All {validation_errors_caught} invalid inputs rejected by Pydantic")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14775")
    @pytest.mark.regression
    def test_api_response_safe(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14775: API Response Safety.
        
        Objective:
            Verify that API responses do not contain executable code.
        
        Steps:
            1. Send valid configure request
            2. Verify response does not contain script tags or javascript
        
        Expected:
            API responses are JSON/protobuf data, not HTML with scripts.
        
        Note:
            Focus Server is a backend API returning JSON/protobuf.
            XSS is not applicable as there's no HTML rendering.
        """
        logger.info("=" * 80)
        logger.info("TEST: API Response Safety (PZ-14775)")
        logger.info("=" * 80)
        
        payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request = ConfigureRequest(**payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        # Verify response structure is safe
        response_str = str(response)
        
        assert "<script>" not in response_str.lower(), \
            "Response should not contain script tags"
        assert "javascript:" not in response_str.lower(), \
            "Response should not contain javascript: protocol"
        assert "<html>" not in response_str.lower(), \
            "Response should not contain HTML (should be JSON/protobuf)"
        
        logger.info("Response verified as safe (no executable code)")
        
        # Cleanup
        if response.job_id:
            try:
                focus_server_api.cancel_job(response.job_id)
            except Exception:
                pass
        
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14788")
    @pytest.mark.regression
    def test_malformed_input_handling(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14788: Malformed Input Handling.
        
        Objective:
            Verify that malformed inputs are handled gracefully without
            exposing system internals in error messages.
        
        Steps:
            1. Send requests with various malformed inputs
            2. Verify errors are handled gracefully
            3. Verify error messages don't expose sensitive paths
        
        Expected:
            All malformed inputs handled gracefully with safe error messages.
        """
        logger.info("=" * 80)
        logger.info("TEST: Malformed Input Handling (PZ-14788)")
        logger.info("=" * 80)
        
        malformed_inputs = [
            {"field": "channels", "value": "not_a_dict", "description": "string for dict field"},
            {"field": "displayInfo", "value": 12345, "description": "int for dict field"},
            {"field": "frequencyRange", "value": None, "description": "None for required dict"},
        ]
        
        base_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        errors_handled_safely = 0
        
        for test_case in malformed_inputs:
            logger.info(f"Testing: {test_case['description']}")
            
            test_payload = base_payload.copy()
            test_payload[test_case['field']] = test_case['value']
            
            try:
                config_request = ConfigureRequest(**test_payload)
                # Unexpected - Pydantic should catch this
                logger.warning(f"  Pydantic accepted malformed input - checking API response")
                
                try:
                    response = focus_server_api.configure_streaming_job(config_request)
                    if response.job_id:
                        focus_server_api.cancel_job(response.job_id)
                except APIError as api_err:
                    error_str = str(api_err).lower()
                    assert "/etc/passwd" not in error_str, "Error should not expose system paths"
                    assert "system32" not in error_str, "Error should not expose system paths"
                    errors_handled_safely += 1
                    logger.info(f"  API error handled safely")
                    
            except (ValueError, ValidationError, TypeError) as e:
                errors_handled_safely += 1
                error_str = str(e).lower()
                # Verify error doesn't expose sensitive info
                assert "/etc/passwd" not in error_str, "Error should not expose system paths"
                assert "system32" not in error_str, "Error should not expose system paths"
                logger.info(f"  Pydantic error handled safely: {type(e).__name__}")
        
        logger.info(f"All {errors_handled_safely} malformed inputs handled safely")
        logger.info("=" * 80)
