"""
Integration Tests - Data Quality: Negative Amplitude Values Detection
=====================================================================

Test to detect negative amplitude values in waterfall/spectrogram data
that come from the Backend, which cause black spectrograms.

This test addresses the issue reported by Tomer:
- Some investigations open correctly
- Same investigations in another tab open with negative frequency
- Spectrogram appears black
- Values like -6.91 are seen in Dynamic Range Min

Tests Covered:
    - Detection of negative amplitude values in waterfall data
    - Validation of current_min_amp and current_max_amp values
    - Detection of negative Dynamic Range values

Author: QA Automation
Date: 2025-11-09
"""

import pytest
import logging
import time
from typing import Dict, Any, List

from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError
from src.models.focus_server_models import ConfigureRequest, ViewType
from src.utils.validators import validate_waterfall_response

logger = logging.getLogger(__name__)


@pytest.mark.critical
@pytest.mark.high
@pytest.mark.regression
class TestNegativeAmplitudeValues:
    """
    Test suite for detecting negative amplitude values in waterfall data.
    
    This test checks for the issue where negative amplitude values cause
    black spectrograms in the Panda App.
    """
    
    @pytest.mark.skip(reason="GET /waterfall/{task_id}/{row_count} endpoint not yet implemented in backend")

    
    @pytest.mark.regression
    def test_detect_negative_amplitude_values(self, focus_server_api: FocusServerAPI):
        """
        Test: Detect negative amplitude values in waterfall data.
        
        Objective:
            Verify that waterfall data does not contain negative amplitude values
            (current_min_amp, current_max_amp) that cause black spectrograms.
        
        Steps:
            1. Configure a job
            2. Get waterfall data
            3. Check for negative amplitude values
            4. Validate Dynamic Range values
        
        Expected:
            No negative amplitude values in waterfall data.
            Dynamic Range Min should be >= 0 (or acceptable range).
        """
        logger.info("=" * 80)
        logger.info("TEST: Detect Negative Amplitude Values in Waterfall Data")
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
        
        try:
            # Step 1: Configure job
            logger.info("Step 1: Configuring job...")
            response = focus_server_api.configure_streaming_job(config_request)
            job_id = response.job_id
            
            assert job_id, "Job ID must be returned from configure_streaming_job"
            
            logger.info(f"Job configured: {job_id}")
            
            # Step 2: Wait for job to be ready and get waterfall data
            logger.info("Step 2: Waiting for job to be ready...")
            max_wait = 30  # 30 seconds
            wait_start = time.time()
            
            waterfall_data = None
            while time.time() - wait_start < max_wait:
                try:
                    # Use job_id as task_id for get_waterfall
                    waterfall_data = focus_server_api.get_waterfall(job_id, row_count=100)
                    if waterfall_data:
                        if waterfall_data.status_code == 201:
                            # Data available
                            if waterfall_data.data and len(waterfall_data.data) > 0:
                                logger.info("✅ Waterfall data received")
                                break
                        elif waterfall_data.status_code == 200:
                            # No data yet, but consumer exists - keep waiting
                            logger.debug(f"Consumer exists but no data yet (status 200)")
                            time.sleep(1)
                            continue
                        elif waterfall_data.status_code == 404:
                            # Consumer not found yet - keep waiting
                            logger.debug(f"Consumer not found yet (status 404)")
                            time.sleep(1)
                            continue
                        else:
                            # Other status code
                            logger.warning(f"Unexpected status code: {waterfall_data.status_code}")
                            time.sleep(1)
                    else:
                        time.sleep(1)
                except APIError as e:
                    logger.warning(f"APIError during polling: {e}")
                    time.sleep(1)
            
            if not waterfall_data or waterfall_data.status_code != 201:
                status_msg = f"status {waterfall_data.status_code}" if waterfall_data else "no response"
                pytest.skip(f"Could not get waterfall data within timeout ({status_msg})")
            
            # Step 3: Check for negative amplitude values
            logger.info("Step 3: Checking for negative amplitude values...")
            
            negative_amplitudes_found = []
            negative_dynamic_ranges_found = []
            
            if waterfall_data.data:
                for block_idx, block in enumerate(waterfall_data.data):
                    # Check current_min_amp and current_max_amp
                    if hasattr(block, 'current_min_amp'):
                        if block.current_min_amp < 0:
                            negative_amplitudes_found.append({
                                'block': block_idx,
                                'field': 'current_min_amp',
                                'value': block.current_min_amp
                            })
                            logger.warning(
                                f"⚠️  Block {block_idx}: Negative current_min_amp = {block.current_min_amp}"
                            )
                    
                    if hasattr(block, 'current_max_amp'):
                        if block.current_max_amp < 0:
                            negative_amplitudes_found.append({
                                'block': block_idx,
                                'field': 'current_max_amp',
                                'value': block.current_max_amp
                            })
                            logger.warning(
                                f"⚠️  Block {block_idx}: Negative current_max_amp = {block.current_max_amp}"
                            )
                    
                    # Log amplitude ranges for debugging
                    if hasattr(block, 'current_min_amp') and hasattr(block, 'current_max_amp'):
                        logger.info(
                            f"Block {block_idx}: Amplitude Range: "
                            f"Min={block.current_min_amp:.4f}, Max={block.current_max_amp:.4f}"
                        )
                        
                        # Check if Dynamic Range Min is negative (like -6.91)
                        if block.current_min_amp < 0:
                            negative_dynamic_ranges_found.append({
                                'block': block_idx,
                                'dynamic_range_min': block.current_min_amp,
                                'dynamic_range_max': block.current_max_amp
                            })
            
            # Step 4: Report findings
            logger.info("\n" + "=" * 80)
            logger.info("RESULTS: Negative Amplitude Values Detection")
            logger.info("=" * 80)
            
            if negative_amplitudes_found:
                logger.error(f"❌ Found {len(negative_amplitudes_found)} negative amplitude values:")
                for item in negative_amplitudes_found:
                    logger.error(
                        f"   Block {item['block']}: {item['field']} = {item['value']}"
                    )
                
                # This is the bug - fail the test
                pytest.fail(
                    f"Negative amplitude values detected! "
                    f"This causes black spectrograms. "
                    f"Found {len(negative_amplitudes_found)} negative values."
                )
            else:
                logger.info("✅ No negative amplitude values found")
            
            if negative_dynamic_ranges_found:
                logger.error(f"❌ Found {len(negative_dynamic_ranges_found)} negative Dynamic Range values:")
                for item in negative_dynamic_ranges_found:
                    logger.error(
                        f"   Block {item['block']}: "
                        f"Dynamic Range Min={item['dynamic_range_min']:.4f}, "
                        f"Max={item['dynamic_range_max']:.4f}"
                    )
                
                pytest.fail(
                    f"Negative Dynamic Range values detected! "
                    f"This matches the issue reported by Tomer. "
                    f"Found {len(negative_dynamic_ranges_found)} negative Dynamic Range values."
                )
            else:
                logger.info("✅ No negative Dynamic Range values found")
            
            # Cleanup
            try:
                focus_server_api.cancel_job(job_id)
            except Exception as e:
                logger.warning(f"Could not cancel job: {e}")
            
            logger.info("✅ Test completed successfully")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            pytest.fail(f"Test failed: {e}")
        
        logger.info("=" * 80)
    
    @pytest.mark.skip(reason="GET /waterfall/{task_id}/{row_count} endpoint not yet implemented in backend")

    
    @pytest.mark.regression
    def test_validate_waterfall_response_amplitude_ranges(self, focus_server_api: FocusServerAPI):
        """
        Test: Validate waterfall response amplitude ranges.
        
        Objective:
            Use the validate_waterfall_response function to check for
            negative amplitude values and other data quality issues.
        
        Steps:
            1. Configure a job
            2. Get waterfall data
            3. Validate using validate_waterfall_response
            4. Check validation results for negative values
        
        Expected:
            Validation passes without negative amplitude warnings.
        """
        logger.info("=" * 80)
        logger.info("TEST: Validate Waterfall Response Amplitude Ranges")
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
        
        try:
            # Configure job
            response = focus_server_api.configure_streaming_job(config_request)
            job_id = response.job_id
            
            assert job_id, "Job ID must be returned from configure_streaming_job"
            
            logger.info(f"Job configured: {job_id}")
            
            # Wait for job to be ready
            logger.info("Waiting for job to be ready...")
            max_wait = 30
            wait_start = time.time()
            
            waterfall_data = None
            while time.time() - wait_start < max_wait:
                try:
                    # Use job_id as task_id for get_waterfall
                    waterfall_data = focus_server_api.get_waterfall(job_id, row_count=100)
                    if waterfall_data:
                        if waterfall_data.status_code == 201:
                            # Data available
                            if waterfall_data.data and len(waterfall_data.data) > 0:
                                break
                        elif waterfall_data.status_code == 200:
                            # No data yet, but consumer exists - keep waiting
                            time.sleep(1)
                            continue
                        elif waterfall_data.status_code == 404:
                            # Consumer not found yet - keep waiting
                            time.sleep(1)
                            continue
                        else:
                            # Other status code
                            time.sleep(1)
                    else:
                        time.sleep(1)
                except APIError as e:
                    logger.warning(f"APIError during polling: {e}")
                    time.sleep(1)
            
            if not waterfall_data or waterfall_data.status_code != 201:
                status_msg = f"status {waterfall_data.status_code}" if waterfall_data else "no response"
                pytest.skip(f"Could not get waterfall data within timeout ({status_msg})")
            
            # Validate waterfall response
            logger.info("Validating waterfall response...")
            validation_result = validate_waterfall_response(waterfall_data)
            
            logger.info(f"Validation result: {validation_result}")
            
            # Check for negative amplitude values in validation warnings
            if 'warnings' in validation_result:
                for warning in validation_result['warnings']:
                    logger.warning(f"⚠️  Validation warning: {warning}")
            
            # Additional check: manually verify amplitude ranges
            if waterfall_data.data:
                for block_idx, block in enumerate(waterfall_data.data):
                    if hasattr(block, 'current_min_amp') and block.current_min_amp < 0:
                        logger.error(
                            f"❌ Block {block_idx}: Negative current_min_amp = {block.current_min_amp}"
                        )
                        pytest.fail(
                            f"Negative amplitude detected: Block {block_idx}, "
                            f"current_min_amp = {block.current_min_amp}"
                        )
            
            logger.info("✅ Validation passed - no negative amplitude values")
            
            # Cleanup
            try:
                focus_server_api.cancel_job(job_id)
            except Exception as e:
                logger.warning(f"Could not cancel job: {e}")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            pytest.fail(f"Test failed: {e}")
        
        logger.info("=" * 80)

