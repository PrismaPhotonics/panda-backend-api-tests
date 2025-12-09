"""
Integration Tests - NFFT Value Validation
==========================================

Comprehensive tests for all valid and invalid NFFT values.

These tests ensure that:
1. All 10 valid NFFT values (powers of 2) are accepted
2. Invalid NFFT values are rejected with appropriate errors

Tests Covered (Xray):
    - PZ-XXXX: NFFT Valid Values Coverage
    - PZ-XXXX: NFFT Invalid Values Rejection

Author: QA Automation
Date: 2025-12-09
"""

import pytest
import logging
from typing import List

from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError, ValidationError
from src.models.focus_server_models import ConfigureRequest, ViewType

# Import production constants
from be_focus_server_tests.constants import (
    NFFT_OPTIONS,
    INVALID_NFFT_VALUES,
    DEFAULT_NFFT,
    FREQUENCY_MAX_HZ,
    FREQUENCY_MIN_HZ,
    DEFAULT_START_CHANNEL,
    DEFAULT_END_CHANNEL,
    DEFAULT_DISPLAY_TIME_AXIS_DURATION,
    DEFAULT_DISPLAY_INFO_HEIGHT,
)

logger = logging.getLogger(__name__)


@pytest.mark.regression
class TestNFFTAllValues:
    """
    Comprehensive NFFT validation tests.
    
    Tests all 10 valid NFFT values (powers of 2 from 128 to 65536)
    and verifies that invalid values are properly rejected.
    """
    
    def get_base_payload(self, nfft: int) -> dict:
        """Get a base payload with specified NFFT value."""
        return {
            "displayTimeAxisDuration": DEFAULT_DISPLAY_TIME_AXIS_DURATION,
            "nfftSelection": nfft,
            "displayInfo": {"height": DEFAULT_DISPLAY_INFO_HEIGHT},
            "channels": {"min": DEFAULT_START_CHANNEL, "max": DEFAULT_END_CHANNEL},
            "frequencyRange": {"min": FREQUENCY_MIN_HZ, "max": FREQUENCY_MAX_HZ},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
    
    @pytest.mark.parametrize("nfft", NFFT_OPTIONS)
    def test_valid_nfft_values_accepted(self, focus_server_api: FocusServerAPI, nfft: int):
        """
        Test that all valid NFFT values (powers of 2) are accepted.
        
        Valid NFFT values: 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536
        
        Steps:
            1. Create ConfigureRequest with specified NFFT value
            2. Send configure request to API
            3. Verify job is created successfully
            4. Clean up job
        
        Expected:
            All 10 valid NFFT values should create jobs successfully.
        """
        logger.info(f"Testing valid NFFT value: {nfft}")
        
        payload = self.get_base_payload(nfft)
        
        try:
            config_request = ConfigureRequest(**payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            # Verify job was created
            assert response.job_id is not None, \
                f"Job should be created for valid NFFT={nfft}"
            assert len(response.job_id) > 0, \
                f"Job ID should not be empty for NFFT={nfft}"
            
            logger.info(f"  Job created: {response.job_id}")
            
            # Cleanup
            try:
                focus_server_api.cancel_job(response.job_id)
                logger.info(f"  Job cancelled successfully")
            except Exception as cleanup_error:
                logger.warning(f"  Cleanup warning: {cleanup_error}")
            
        except (ValidationError, APIError) as e:
            pytest.fail(
                f"Valid NFFT value {nfft} was rejected. "
                f"Expected: Job created. "
                f"Actual: Error - {e}"
            )
    
    @pytest.mark.parametrize("invalid_nfft", INVALID_NFFT_VALUES)
    def test_invalid_nfft_values_rejected(self, focus_server_api: FocusServerAPI, invalid_nfft: int):
        """
        Test that invalid NFFT values are rejected.
        
        Invalid values include:
            - 0 (zero)
            - -1 (negative)
            - 100 (not power of 2)
            - 127 (one less than valid)
            - 129 (one more than valid)
            - 500 (not power of 2)
            - 1000 (not power of 2, common mistake)
            - 65537 (one more than max)
            - 131072 (too large)
        
        Steps:
            1. Attempt to create ConfigureRequest with invalid NFFT
            2. Verify either Pydantic or API rejects the value
        
        Expected:
            All invalid NFFT values should be rejected with ValidationError or APIError.
        """
        logger.info(f"Testing invalid NFFT value: {invalid_nfft}")
        
        payload = self.get_base_payload(invalid_nfft)
        
        try:
            config_request = ConfigureRequest(**payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            # If we get here, the invalid NFFT was accepted - this is a BUG
            if response.job_id:
                # Cleanup first
                try:
                    focus_server_api.cancel_job(response.job_id)
                except Exception:
                    pass
            
            pytest.fail(
                f"BUG: Invalid NFFT value {invalid_nfft} was accepted. "
                f"Expected: ValidationError or 400 Bad Request. "
                f"Actual: Job created with id={response.job_id}"
            )
            
        except (ValidationError, ValueError, TypeError) as e:
            # Expected - Pydantic caught the invalid value
            logger.info(f"  Pydantic rejected: {type(e).__name__}")
            assert True, f"Invalid NFFT {invalid_nfft} correctly rejected by validation"
            
        except APIError as e:
            # Expected - API caught the invalid value
            logger.info(f"  API rejected: {e}")
            # Verify error mentions NFFT or validation
            error_str = str(e).lower()
            assert "nfft" in error_str or "validation" in error_str or "invalid" in error_str or "400" in str(e), \
                f"Error should mention NFFT or validation issue: {e}"
    
    def test_nfft_boundary_values(self, focus_server_api: FocusServerAPI):
        """
        Test boundary values for NFFT.
        
        Steps:
            1. Test minimum valid (128) - should pass
            2. Test maximum valid (65536) - should pass
            3. Test below minimum (64) - should fail
            4. Test above maximum (131072) - should fail
        
        Expected:
            Boundary values within range pass, outside range fail.
        """
        logger.info("Testing NFFT boundary values")
        
        # Test minimum valid
        min_payload = self.get_base_payload(128)
        config_request = ConfigureRequest(**min_payload)
        response = focus_server_api.configure_streaming_job(config_request)
        assert response.job_id is not None, "Minimum NFFT (128) should be accepted"
        focus_server_api.cancel_job(response.job_id)
        logger.info("  Minimum NFFT (128): PASSED")
        
        # Test maximum valid
        max_payload = self.get_base_payload(65536)
        config_request = ConfigureRequest(**max_payload)
        response = focus_server_api.configure_streaming_job(config_request)
        assert response.job_id is not None, "Maximum NFFT (65536) should be accepted"
        focus_server_api.cancel_job(response.job_id)
        logger.info("  Maximum NFFT (65536): PASSED")
        
        # Test below minimum (64 is power of 2 but not in valid range)
        below_min_payload = self.get_base_payload(64)
        try:
            config_request = ConfigureRequest(**below_min_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            if response.job_id:
                focus_server_api.cancel_job(response.job_id)
            pytest.fail("NFFT 64 should be rejected (below minimum)")
        except (ValidationError, APIError, ValueError):
            logger.info("  Below minimum NFFT (64): Correctly rejected")
        
        # Test above maximum (131072)
        above_max_payload = self.get_base_payload(131072)
        try:
            config_request = ConfigureRequest(**above_max_payload)
            response = focus_server_api.configure_streaming_job(config_request)
            if response.job_id:
                focus_server_api.cancel_job(response.job_id)
            pytest.fail("NFFT 131072 should be rejected (above maximum)")
        except (ValidationError, APIError, ValueError):
            logger.info("  Above maximum NFFT (131072): Correctly rejected")
    
    def test_nfft_default_value(self, focus_server_api: FocusServerAPI):
        """
        Test that the default NFFT value (1024) works correctly.
        
        This is the most commonly used value and should always work.
        """
        logger.info(f"Testing default NFFT value: {DEFAULT_NFFT}")
        
        payload = self.get_base_payload(DEFAULT_NFFT)
        config_request = ConfigureRequest(**payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        assert response.job_id is not None, \
            f"Default NFFT ({DEFAULT_NFFT}) should always work"
        
        logger.info(f"  Default NFFT job created: {response.job_id}")
        
        # Cleanup
        focus_server_api.cancel_job(response.job_id)
        logger.info(f"  Job cancelled successfully")
    
    def test_all_valid_nfft_values_comprehensive(self, focus_server_api: FocusServerAPI):
        """
        Comprehensive test that validates ALL valid NFFT values in sequence.
        
        This test creates and cancels jobs for all 10 valid values,
        tracking success/failure for each.
        
        Expected:
            All 10 values should succeed.
        """
        logger.info("=" * 80)
        logger.info("Comprehensive NFFT Values Test")
        logger.info("=" * 80)
        
        results = []
        
        for nfft in NFFT_OPTIONS:
            logger.info(f"\nTesting NFFT={nfft}")
            
            try:
                payload = self.get_base_payload(nfft)
                config_request = ConfigureRequest(**payload)
                response = focus_server_api.configure_streaming_job(config_request)
                
                if response.job_id:
                    results.append({"nfft": nfft, "status": "PASS", "job_id": response.job_id})
                    logger.info(f"  PASS - job_id: {response.job_id}")
                    
                    # Cleanup
                    try:
                        focus_server_api.cancel_job(response.job_id)
                    except Exception:
                        pass
                else:
                    results.append({"nfft": nfft, "status": "FAIL", "reason": "No job_id"})
                    logger.error(f"  FAIL - No job_id returned")
                    
            except Exception as e:
                results.append({"nfft": nfft, "status": "FAIL", "reason": str(e)})
                logger.error(f"  FAIL - {e}")
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("Results Summary:")
        passed = [r for r in results if r["status"] == "PASS"]
        failed = [r for r in results if r["status"] == "FAIL"]
        
        logger.info(f"  PASSED: {len(passed)}/{len(NFFT_OPTIONS)}")
        logger.info(f"  FAILED: {len(failed)}/{len(NFFT_OPTIONS)}")
        
        if failed:
            for f in failed:
                logger.error(f"  - NFFT {f['nfft']}: {f.get('reason', 'Unknown')}")
        
        logger.info("=" * 80)
        
        # Final assertion
        assert len(failed) == 0, \
            f"{len(failed)} NFFT values failed: {[f['nfft'] for f in failed]}"

