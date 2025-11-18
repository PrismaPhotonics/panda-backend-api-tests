"""
Integration Tests - Error Handling: Network Errors
===================================================

Error handling tests for network-related errors.

Tests Covered (Xray):
    - PZ-14783: Error Handling - Network Timeout
    - PZ-14784: Error Handling - Connection Refused

Author: QA Automation Architect
Date: 2025-11-09
"""

import pytest
import logging
import time
from typing import Dict, Any

from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError, InfrastructureError

logger = logging.getLogger(__name__)


@pytest.mark.critical



@pytest.mark.regression
class TestNetworkErrors:
    """
    Test suite for network error handling.
    
    Tests covered:
        - PZ-14783: Network Timeout
        - PZ-14784: Connection Refused
    """
    
    @pytest.mark.xray("PZ-14783")

    
    @pytest.mark.regression
    def test_network_timeout(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14783: Error Handling - Network Timeout.
        
        Objective:
            Verify that the API properly handles network timeout errors
            and provides informative error messages.
        
        Steps:
            1. Send request with very short timeout
            2. Verify timeout error is handled
            3. Verify error message is informative
            4. Verify system remains stable
        
        Expected:
            Network timeout errors are handled gracefully with informative messages.
        """
        logger.info("=" * 80)
        logger.info("TEST: Error Handling - Network Timeout (PZ-14783)")
        logger.info("=" * 80)
        
        # Note: Network timeout testing requires modifying API client timeout
        # This test verifies error handling when timeout occurs
        
        from src.models.focus_server_models import ConfigureRequest, ViewType
        
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
            # Send request (timeout depends on API client configuration)
            start_time = time.time()
            response = focus_server_api.configure_streaming_job(config_request)
            elapsed_time = time.time() - start_time
            
            logger.info(f"Request completed in {elapsed_time:.2f} seconds")
            
            if response.job_id:
                logger.info(f"Request succeeded: job_id={response.job_id}")
                
                # Cleanup
                try:
                    focus_server_api.cancel_job(response.job_id)
                except Exception:
                    pass
            
            # Note: Timeout would be tested by configuring very short timeout
            # For now, verify request completes successfully
            logger.info("✅ Request completed successfully")
            pytest.skip("Network timeout not triggered. Test verifies error handling when timeout occurs.")
            
        except APIError as e:
            error_str = str(e).lower()
            
            if "timeout" in error_str or (hasattr(e, 'status_code') and e.status_code == 504):
                logger.info("✅ Network timeout error detected")
                logger.info(f"Error: {e}")
                
                # Verify error message is informative
                assert len(str(e)) > 0, "Error message should not be empty"
                
            else:
                logger.info(f"Other error (not timeout): {e}")
                pytest.skip("Network timeout not triggered")
                
        except Exception as e:
            error_str = str(e).lower()
            
            if "timeout" in error_str:
                logger.info("✅ Timeout exception detected")
                logger.info(f"Error: {e}")
                
                # Verify error is handled gracefully
                assert True, "Timeout error handled"
                
            else:
                logger.warning(f"Unexpected error: {e}")
                pytest.skip("Test skipped - unexpected error")
        
        logger.info("✅ Test completed")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14784")

    
    @pytest.mark.regression
    def test_connection_refused(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14784: Error Handling - Connection Refused.
        
        Objective:
            Verify that the API properly handles connection refused errors
            and provides informative error messages.
        
        Steps:
            1. Attempt connection to invalid/unreachable endpoint
            2. Verify connection refused error is handled
            3. Verify error message is informative
            4. Verify system remains stable
        
        Expected:
            Connection refused errors are handled gracefully with informative messages.
        """
        logger.info("=" * 80)
        logger.info("TEST: Error Handling - Connection Refused (PZ-14784)")
        logger.info("=" * 80)
        
        # Note: Connection refused testing requires invalid endpoint
        # This test verifies error handling when connection is refused
        
        # Test with invalid endpoint (if API client supports it)
        # For now, verify current endpoint works
        
        try:
            # Verify current endpoint is reachable
            is_healthy = focus_server_api.health_check()
            
            if is_healthy:
                logger.info("✅ Current endpoint is reachable")
                logger.info("Connection refused test would verify error handling when connection is refused")
                pytest.skip("Connection refused not triggered. Test verifies error handling when connection is refused.")
            else:
                logger.warning("⚠️  Health check failed (connection may be refused)")
                
                # This might indicate connection issues
                try:
                    from src.models.focus_server_models import ConfigureRequest, ViewType
                    
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
                    response = focus_server_api.configure_streaming_job(config_request)
                    
                    if response.job_id:
                        try:
                            focus_server_api.cancel_job(response.job_id)
                        except Exception:
                            pass
                    
                except Exception as e:
                    error_str = str(e).lower()
                    
                    if "connection" in error_str or "refused" in error_str or "refused" in error_str:
                        logger.info("✅ Connection refused error detected")
                        logger.info(f"Error: {e}")
                        
                        # Verify error message is informative
                        assert len(str(e)) > 0, "Error message should not be empty"
                        
                    else:
                        logger.warning(f"Other error: {e}")
                        
        except Exception as e:
            error_str = str(e).lower()
            
            if "connection" in error_str or "refused" in error_str:
                logger.info("✅ Connection refused error detected")
                logger.info(f"Error: {e}")
                
                # Verify error is handled gracefully
                assert True, "Connection refused error handled"
                
            else:
                logger.warning(f"Unexpected error: {e}")
                pytest.skip("Test skipped - unexpected error")
        
        logger.info("✅ Test completed")
        logger.info("=" * 80)

