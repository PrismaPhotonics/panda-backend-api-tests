"""
Integration Tests - Security: Data Exposure Prevention
======================================================

Security tests for preventing sensitive data exposure.

Tests Covered (Xray):
    - PZ-14779: Security - Data Exposure Prevention
    - PZ-14780: Security - Error Message Security

Author: QA Automation Architect
Date: 2025-11-09
"""

import pytest
import logging
from typing import Dict, Any

from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError, ValidationError
from src.models.focus_server_models import ConfigureRequest, ViewType

logger = logging.getLogger(__name__)


@pytest.mark.critical



@pytest.mark.regression
class TestDataExposure:
    """
    Test suite for data exposure prevention security.
    
    Tests covered:
        - PZ-14779: Data Exposure Prevention
        - PZ-14780: Error Message Security
    """
    
    @pytest.mark.xray("PZ-14779")
    @pytest.mark.xray("PZ-13572")
    @pytest.mark.xray("PZ-13572")

    @pytest.mark.regression
    def test_data_exposure_prevention(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14779: Security - Data Exposure Prevention.
        
        Objective:
            Verify that API responses do not expose sensitive information
            such as database credentials, internal paths, or system details.
        
        Steps:
            1. Send valid request and verify response
            2. Send invalid request and verify error response
            3. Check for sensitive data in responses
        
        Expected:
            API responses do not contain sensitive information.
        """
        logger.info("=" * 80)
        logger.info("TEST: Security - Data Exposure Prevention (PZ-14779)")
        logger.info("=" * 80)
        
        sensitive_patterns = [
            "password",
            "secret",
            "api_key",
            "token",
            "/etc/passwd",
            "c:\\windows\\system32",
            "mongodb://",
            "postgresql://",
            "mysql://",
            "redis://",
            "private_key",
            "ssh-rsa"
        ]
        
        # Test 1: Valid request
        logger.info("Testing valid request...")
        payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request = ConfigureRequest(**payload)
        
        try:
            response = focus_server_api.configure_streaming_job(config_request)
            response_str = str(response).lower()
            
            # Check for sensitive data
            for pattern in sensitive_patterns:
                assert pattern not in response_str, \
                    f"Response should not contain sensitive pattern: {pattern}"
            
            logger.info("✅ Valid request response is safe")
            
            # Cleanup
            if response.job_id:
                try:
                    focus_server_api.cancel_job(response.job_id)
                except Exception:
                    pass
                    
        except Exception as e:
            logger.error(f"Error in valid request test: {e}")
            pytest.fail(f"Test failed: {e}")
        
        # Test 2: Invalid request
        logger.info("Testing invalid request...")
        invalid_payload = {
            "displayTimeAxisDuration": -1,  # Invalid value
            "nfftSelection": 0,  # Invalid value
            "channels": {"min": 100, "max": 1},  # Invalid range
        }
        
        try:
            # This should fail validation
            config_request = ConfigureRequest(**invalid_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            response_str = str(response).lower()
            
            # Check for sensitive data
            for pattern in sensitive_patterns:
                assert pattern not in response_str, \
                    f"Error response should not contain sensitive pattern: {pattern}"
            
            logger.info("✅ Invalid request error response is safe")
            
        except ValidationError as e:
            error_str = str(e).lower()
            
            # Check for sensitive data in error message
            for pattern in sensitive_patterns:
                assert pattern not in error_str, \
                    f"Error message should not contain sensitive pattern: {pattern}"
            
            logger.info("✅ Validation error message is safe")
            
        except APIError as e:
            error_str = str(e).lower()
            
            # Check for sensitive data in error message
            for pattern in sensitive_patterns:
                assert pattern not in error_str, \
                    f"API error message should not contain sensitive pattern: {pattern}"
            
            logger.info("✅ API error message is safe")
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check for sensitive data in error message
            for pattern in sensitive_patterns:
                assert pattern not in error_str, \
                    f"Error message should not contain sensitive pattern: {pattern}"
            
            logger.info("✅ Exception message is safe")
        
        logger.info("✅ All data exposure prevention checks passed")
        logger.info("=" * 80)
    
    @pytest.mark.regression
    def test_error_message_security(self, focus_server_api: FocusServerAPI):
        """
        Test: Security - Error Message Security.
        
        Note: This test verifies error message security as part of data exposure prevention.
        The main error message format test is PZ-14787 in Error Handling tests.
        
        Objective:
            Verify that error messages do not expose sensitive information
            such as stack traces, internal paths, or system details.
        
        Steps:
            1. Send request that triggers various error types
            2. Verify error messages are safe and informative
            3. Check for sensitive data in error messages
        
        Expected:
            Error messages are safe, informative, and do not expose sensitive data.
        """
        logger.info("=" * 80)
        logger.info("TEST: Security - Error Message Security (PZ-14780)")
        logger.info("=" * 80)
        
        sensitive_patterns = [
            "traceback",
            "file \"/",
            "line ",
            "c:\\",
            "/home/",
            "/root/",
            "stack trace",
            "exception:",
            "at 0x",
            "mongodb://",
            "postgresql://",
            "mysql://",
            "redis://"
        ]
        
        # Test various error scenarios
        error_scenarios = [
            {
                "name": "Invalid payload type",
                "payload": "not a dict",
                "expected_error": (TypeError, ValidationError)
            },
            {
                "name": "Missing required fields",
                "payload": {},
                "expected_error": (ValidationError,)
            },
            {
                "name": "Invalid value type",
                "payload": {
                    "displayTimeAxisDuration": "not a number",
                    "nfftSelection": "not a number"
                },
                "expected_error": (ValidationError,)
            }
        ]
        
        for scenario in error_scenarios:
            logger.info(f"\nTesting scenario: {scenario['name']}")
            
            try:
                if isinstance(scenario['payload'], dict):
                    config_request = ConfigureRequest(**scenario['payload'])
                    response = focus_server_api.configure_streaming_job(config_request)
                    response_str = str(response).lower()
                else:
                    # Invalid type - should fail before API call
                    raise TypeError(f"Invalid payload type: {type(scenario['payload'])}")
                
                # Check for sensitive data
                for pattern in sensitive_patterns:
                    assert pattern not in response_str, \
                        f"Response should not contain sensitive pattern: {pattern}"
                
                logger.info(f"  ✅ Error response is safe: {scenario['name']}")
                
            except scenario['expected_error'] as e:
                error_str = str(e).lower()
                
                # Check for sensitive data in error message
                for pattern in sensitive_patterns:
                    assert pattern not in error_str, \
                        f"Error message should not contain sensitive pattern: {pattern}"
                
                logger.info(f"  ✅ Error message is safe: {scenario['name']}")
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check for sensitive data in error message
                for pattern in sensitive_patterns:
                    assert pattern not in error_str, \
                        f"Error message should not contain sensitive pattern: {pattern}"
                
                logger.info(f"  ✅ Exception message is safe: {scenario['name']}")
        
        logger.info("\n✅ All error message security checks passed")
        logger.info("=" * 80)

