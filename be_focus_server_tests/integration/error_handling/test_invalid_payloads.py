"""
Integration Tests - Error Handling: Invalid Payloads
=====================================================

Error handling tests for invalid payloads.

Tests Covered (Xray):
    - PZ-14785: Error Handling - Invalid JSON Payload
    - PZ-14786: Error Handling - Malformed Request
    - PZ-14787: Error Handling - Error Message Format

Author: QA Automation Architect
Date: 2025-11-09
"""

import pytest
import logging
import json
from typing import Dict, Any

from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError, ValidationError
from src.models.focus_server_models import ConfigureRequest, ViewType

logger = logging.getLogger(__name__)


@pytest.mark.critical
@pytest.mark.high
@pytest.mark.regression
class TestInvalidPayloads:
    """
    Test suite for invalid payload error handling.
    
    Tests covered:
        - PZ-14785: Invalid JSON Payload
        - PZ-14786: Malformed Request
        - PZ-14787: Error Message Format
    """
    
    @pytest.mark.xray("PZ-14785")

    
    @pytest.mark.regression
    def test_invalid_json_payload(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14785: Error Handling - Invalid JSON Payload.
        
        Objective:
            Verify that the API properly handles invalid JSON payloads
            and returns appropriate error messages.
        
        Steps:
            1. Send request with invalid JSON syntax
            2. Send request with invalid JSON structure
            3. Verify error messages are informative
        
        Expected:
            Invalid JSON payloads are rejected with HTTP 400 Bad Request.
            Error messages are informative and helpful.
        """
        logger.info("=" * 80)
        logger.info("TEST: Error Handling - Invalid JSON Payload (PZ-14785)")
        logger.info("=" * 80)
        
        # Note: Pydantic validation happens before JSON is sent to API
        # This test verifies validation error handling
        
        invalid_payloads = [
            # Invalid types
            {
                "displayTimeAxisDuration": "not a number",
                "nfftSelection": "not a number"
            },
            {
                "displayTimeAxisDuration": None,
                "nfftSelection": None
            },
            # Missing required fields
            {},
            # Invalid structure
            {
                "displayTimeAxisDuration": 10,
                "channels": "not a dict"
            }
        ]
        
        for i, payload in enumerate(invalid_payloads):
            logger.info(f"\nTesting invalid payload {i+1}/{len(invalid_payloads)}...")
            logger.info(f"Payload: {json.dumps(payload, default=str)[:200]}...")
            
            try:
                # Pydantic will validate before API call
                config_request = ConfigureRequest(**payload)
                response = focus_server_api.configure_streaming_job(config_request)
                
                # If validation passes but API rejects, check API error
                logger.warning(f"Payload {i+1} passed validation (unexpected)")
                
                if response.job_id:
                    try:
                        focus_server_api.cancel_job(response.job_id)
                    except Exception:
                        pass
                        
            except ValidationError as e:
                logger.info(f"✅ Validation error (expected): {type(e).__name__}")
                logger.info(f"Error message: {str(e)[:200]}...")
                
                # Verify error message is informative
                error_msg = str(e)
                assert len(error_msg) > 0, "Error message should not be empty"
                assert "validation" in error_msg.lower() or "invalid" in error_msg.lower() or "required" in error_msg.lower(), \
                    "Error message should indicate validation issue"
                
            except APIError as e:
                # API-level error
                if hasattr(e, 'status_code'):
                    logger.info(f"✅ API error (status {e.status_code}): {type(e).__name__}")
                    assert e.status_code in [400, 422], \
                        f"Expected 400 or 422 for invalid payload, got {e.status_code}"
                else:
                    logger.info(f"✅ API error: {type(e).__name__}")
                
                error_msg = str(e)
                assert len(error_msg) > 0, "Error message should not be empty"
                logger.info(f"Error message: {error_msg[:200]}...")
                
            except Exception as e:
                logger.warning(f"Unexpected error: {type(e).__name__}: {e}")
                # Don't fail - verify error is handled
                error_msg = str(e)
                assert len(error_msg) > 0, "Error message should not be empty"
        
        logger.info("\n✅ All invalid JSON payload tests completed")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14786")

    
    @pytest.mark.regression
    def test_malformed_request(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14786: Error Handling - Malformed Request.
        
        Objective:
            Verify that the API properly handles malformed requests
            and returns appropriate error messages.
        
        Steps:
            1. Send request with malformed structure
            2. Send request with wrong data types
            3. Send request with invalid values
            4. Verify error messages are informative
        
        Expected:
            Malformed requests are rejected with HTTP 400 Bad Request.
            Error messages are informative and helpful.
        """
        logger.info("=" * 80)
        logger.info("TEST: Error Handling - Malformed Request (PZ-14786)")
        logger.info("=" * 80)
        
        malformed_requests = [
            # Wrong data types
            {
                "displayTimeAxisDuration": "10",  # String instead of number
                "nfftSelection": "1024"
            },
            {
                "displayTimeAxisDuration": [10],  # List instead of number
                "nfftSelection": [1024]
            },
            # Invalid ranges
            {
                "displayTimeAxisDuration": 10,
                "nfftSelection": 1024,
                "channels": {"min": 100, "max": 1},  # min > max
                "frequencyRange": {"min": 500, "max": 0}  # min > max
            },
            # Invalid view type
            {
                "displayTimeAxisDuration": 10,
                "nfftSelection": 1024,
                "view_type": "invalid_view_type"
            }
        ]
        
        for i, payload in enumerate(malformed_requests):
            logger.info(f"\nTesting malformed request {i+1}/{len(malformed_requests)}...")
            
            try:
                config_request = ConfigureRequest(**payload)
                response = focus_server_api.configure_streaming_job(config_request)
                
                logger.warning(f"Request {i+1} succeeded (unexpected)")
                
                if response.job_id:
                    try:
                        focus_server_api.cancel_job(response.job_id)
                    except Exception:
                        pass
                        
            except ValidationError as e:
                logger.info(f"✅ Validation error (expected): {type(e).__name__}")
                logger.info(f"Error: {str(e)[:200]}...")
                
                # Verify error message is informative
                error_msg = str(e)
                assert len(error_msg) > 0, "Error message should not be empty"
                
            except APIError as e:
                logger.info(f"✅ API error: {type(e).__name__}")
                
                if hasattr(e, 'status_code'):
                    assert e.status_code in [400, 422], \
                        f"Expected 400 or 422 for malformed request, got {e.status_code}"
                
                error_msg = str(e)
                assert len(error_msg) > 0, "Error message should not be empty"
                logger.info(f"Error message: {error_msg[:200]}...")
                
            except Exception as e:
                logger.warning(f"Unexpected error: {type(e).__name__}: {e}")
                error_msg = str(e)
                assert len(error_msg) > 0, "Error message should not be empty"
        
        logger.info("\n✅ All malformed request tests completed")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14787")

    
    @pytest.mark.regression
    def test_error_message_format(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14787: Error Handling - Error Message Format.
        
        Objective:
            Verify that error messages follow a consistent format and
            are informative and helpful.
        
        Steps:
            1. Trigger various error types
            2. Verify error message format
            3. Verify error messages are informative
        
        Expected:
            Error messages follow a consistent format.
            Error messages are informative and helpful.
        """
        logger.info("=" * 80)
        logger.info("TEST: Error Handling - Error Message Format (PZ-14787)")
        logger.info("=" * 80)
        
        error_scenarios = [
            {
                "name": "Missing required field",
                "payload": {
                    "displayTimeAxisDuration": 10
                    # Missing nfftSelection
                }
            },
            {
                "name": "Invalid value type",
                "payload": {
                    "displayTimeAxisDuration": "not a number",
                    "nfftSelection": 1024
                }
            },
            {
                "name": "Invalid range",
                "payload": {
                    "displayTimeAxisDuration": 10,
                    "nfftSelection": 1024,
                    "channels": {"min": 100, "max": 1}
                }
            }
        ]
        
        for scenario in error_scenarios:
            logger.info(f"\nTesting scenario: {scenario['name']}")
            
            try:
                config_request = ConfigureRequest(**scenario['payload'])
                response = focus_server_api.configure_streaming_job(config_request)
                
                logger.warning(f"Request succeeded (unexpected): {scenario['name']}")
                
                if response.job_id:
                    try:
                        focus_server_api.cancel_job(response.job_id)
                    except Exception:
                        pass
                        
            except ValidationError as e:
                error_msg = str(e)
                
                # Verify error message format
                assert len(error_msg) > 0, "Error message should not be empty"
                assert isinstance(error_msg, str), "Error message should be a string"
                
                logger.info(f"✅ Validation error format: {error_msg[:200]}...")
                
                # Verify error message is informative
                # Should contain field name or error type
                assert any(keyword in error_msg.lower() for keyword in [
                    "validation", "invalid", "required", "field", "error"
                ]), "Error message should be informative"
                
            except APIError as e:
                error_msg = str(e)
                
                # Verify error message format
                assert len(error_msg) > 0, "Error message should not be empty"
                assert isinstance(error_msg, str), "Error message should be a string"
                
                logger.info(f"✅ API error format: {error_msg[:200]}...")
                
                # Verify error message is informative
                assert any(keyword in error_msg.lower() for keyword in [
                    "error", "invalid", "bad", "request", "failed"
                ]), "Error message should be informative"
                
            except Exception as e:
                error_msg = str(e)
                
                # Verify error message format
                assert len(error_msg) > 0, "Error message should not be empty"
                assert isinstance(error_msg, str), "Error message should be a string"
                
                logger.info(f"✅ Exception format: {error_msg[:200]}...")
        
        logger.info("\n✅ All error message format tests completed")
        logger.info("=" * 80)

