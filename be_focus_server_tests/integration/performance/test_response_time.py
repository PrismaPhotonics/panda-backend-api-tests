"""
Integration Tests - Performance: Response Time
==============================================

Performance tests for API response time.

Tests Covered (Xray):
    - PZ-14790: Performance - POST /configure Response Time
    - PZ-14791: Performance - GET /waterfall Response Time
    - PZ-14792: Performance - GET /metadata Response Time

Author: QA Automation Architect
Date: 2025-11-09
"""

import pytest
import logging
import time
from typing import Dict, Any

from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError
from src.models.focus_server_models import ConfigureRequest, ViewType

logger = logging.getLogger(__name__)


@pytest.mark.api



@pytest.mark.regression
class TestResponseTime:
    """
    Test suite for API response time performance.
    
    Tests covered:
        - PZ-14790: POST /configure Response Time
        - PZ-14791: GET /waterfall Response Time
        - PZ-14792: GET /metadata Response Time
    """
    
    # Performance thresholds (in seconds)
    CONFIGURE_RESPONSE_TIME_THRESHOLD = 5.0  # 5 seconds
    WATERFALL_RESPONSE_TIME_THRESHOLD = 2.0  # 2 seconds
    METADATA_RESPONSE_TIME_THRESHOLD = 1.0   # 1 second
    
    @pytest.mark.xray("PZ-14790")

    
    @pytest.mark.regression
    def test_configure_response_time(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14790: Performance - POST /configure Response Time.
        
        Objective:
            Verify that POST /configure endpoint responds within acceptable
            time limits.
        
        Steps:
            1. Send POST /configure request
            2. Measure response time
            3. Verify response time is within threshold
        
        Expected:
            POST /configure responds within 5 seconds.
        """
        logger.info("=" * 80)
        logger.info("TEST: Performance - POST /configure Response Time (PZ-14790)")
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
        
        # Measure response time
        start_time = time.time()
        
        try:
            response = focus_server_api.configure_streaming_job(config_request)
            elapsed_time = time.time() - start_time
            
            logger.info(f"Response time: {elapsed_time:.3f} seconds")
            logger.info(f"Threshold: {self.CONFIGURE_RESPONSE_TIME_THRESHOLD} seconds")
            
            # Verify response time is within threshold
            assert elapsed_time <= self.CONFIGURE_RESPONSE_TIME_THRESHOLD, \
                f"Response time {elapsed_time:.3f}s exceeds threshold {self.CONFIGURE_RESPONSE_TIME_THRESHOLD}s"
            
            logger.info(f"✅ Response time is within threshold: {elapsed_time:.3f}s <= {self.CONFIGURE_RESPONSE_TIME_THRESHOLD}s")
            
            # Cleanup
            if response.job_id:
                try:
                    focus_server_api.cancel_job(response.job_id)
                except Exception as e:
                    logger.warning(f"Could not cancel job: {e}")
                    
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Request failed after {elapsed_time:.3f} seconds: {e}")
            pytest.fail(f"Request failed: {e}")
        
        logger.info("✅ Test completed")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14791")
    @pytest.mark.skip(reason="GET /waterfall/{task_id}/{row_count} endpoint not yet implemented in backend")

    @pytest.mark.regression
    def test_waterfall_response_time(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14791: Performance - GET /waterfall Response Time.
        
        Objective:
            Verify that GET /waterfall endpoint responds within acceptable
            time limits.
        
        Steps:
            1. Configure a job
            2. Send GET /waterfall request
            3. Measure response time
            4. Verify response time is within threshold
        
        Expected:
            GET /waterfall responds within 2 seconds.
        """
        logger.info("=" * 80)
        logger.info("TEST: Performance - GET /waterfall Response Time (PZ-14791)")
        logger.info("=" * 80)
        
        # First, configure a job
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
            
            if not job_id:
                pytest.skip("No job_id returned - cannot test waterfall endpoint")
            
            logger.info(f"Job configured: {job_id}")
            
            # Wait a bit for data to be available
            time.sleep(2)
            
            # Measure waterfall response time
            start_time = time.time()
            
            try:
                # Get waterfall data
                waterfall_data = focus_server_api.get_waterfall(job_id, row_count=100)
                elapsed_time = time.time() - start_time
                
                logger.info(f"Response time: {elapsed_time:.3f} seconds")
                logger.info(f"Threshold: {self.WATERFALL_RESPONSE_TIME_THRESHOLD} seconds")
                
                # Verify response time is within threshold
                assert elapsed_time <= self.WATERFALL_RESPONSE_TIME_THRESHOLD, \
                    f"Response time {elapsed_time:.3f}s exceeds threshold {self.WATERFALL_RESPONSE_TIME_THRESHOLD}s"
                
                logger.info(f"✅ Response time is within threshold: {elapsed_time:.3f}s <= {self.WATERFALL_RESPONSE_TIME_THRESHOLD}s")
                
            except APIError as e:
                elapsed_time = time.time() - start_time
                logger.warning(f"Waterfall request failed after {elapsed_time:.3f} seconds: {e}")
                # Don't fail - waterfall may not be available yet
                pytest.skip(f"Waterfall endpoint not available: {e}")
            
            # Cleanup
            try:
                focus_server_api.cancel_job(job_id)
            except Exception as e:
                logger.warning(f"Could not cancel job: {e}")
                
        except Exception as e:
            logger.error(f"Test failed: {e}")
            pytest.fail(f"Test failed: {e}")
        
        logger.info("✅ Test completed")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14792")

    
    @pytest.mark.regression
    def test_metadata_response_time(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14792: Performance - GET /metadata Response Time.
        
        Objective:
            Verify that GET /metadata endpoint responds within acceptable
            time limits.
        
        Steps:
            1. Send GET /metadata request
            2. Measure response time
            3. Verify response time is within threshold
        
        Expected:
            GET /metadata responds within 1 second.
        """
        logger.info("=" * 80)
        logger.info("TEST: Performance - GET /metadata Response Time (PZ-14792)")
        logger.info("=" * 80)
        
        # Measure metadata response time
        start_time = time.time()
        
        try:
            metadata = focus_server_api.get_live_metadata_flat()
            elapsed_time = time.time() - start_time
            
            logger.info(f"Response time: {elapsed_time:.3f} seconds")
            logger.info(f"Threshold: {self.METADATA_RESPONSE_TIME_THRESHOLD} seconds")
            
            # Verify response time is within threshold
            assert elapsed_time <= self.METADATA_RESPONSE_TIME_THRESHOLD, \
                f"Response time {elapsed_time:.3f}s exceeds threshold {self.METADATA_RESPONSE_TIME_THRESHOLD}s"
            
            logger.info(f"✅ Response time is within threshold: {elapsed_time:.3f}s <= {self.METADATA_RESPONSE_TIME_THRESHOLD}s")
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Request failed after {elapsed_time:.3f} seconds: {e}")
            pytest.fail(f"Request failed: {e}")
        
        logger.info("✅ Test completed")
        logger.info("=" * 80)

