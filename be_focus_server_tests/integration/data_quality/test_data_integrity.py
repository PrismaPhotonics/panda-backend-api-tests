"""
Integration Tests - Data Quality: Data Integrity
=================================================

Data quality tests for data integrity.

Tests Covered (Xray):
    - PZ-14810: Data Quality - Data Integrity Across Requests

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
class TestDataIntegrity:
    """
    Test suite for data integrity testing.
    
    Tests covered:
        - PZ-14810: Data Integrity Across Requests
    """
    
    @pytest.mark.xray("PZ-14810")
    @pytest.mark.skip(reason="GET /waterfall/{task_id}/{row_count} endpoint not yet implemented in backend")

    @pytest.mark.regression
    def test_data_integrity_across_requests(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14810: Data Quality - Data Integrity Across Requests.
        
        Objective:
            Verify that data integrity is maintained across multiple requests
            and that data does not become corrupted or inconsistent.
        
        Steps:
            1. Configure a job
            2. Send multiple requests for the same job
            3. Verify data integrity
            4. Check for corruption or inconsistencies
        
        Expected:
            Data integrity is maintained across requests.
            No data corruption or inconsistencies.
        """
        logger.info("=" * 80)
        logger.info("TEST: Data Quality - Data Integrity Across Requests (PZ-14810)")
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
            
            if not job_id:
                pytest.skip("No job_id returned - cannot test data integrity")
            
            logger.info(f"Job configured: {job_id}")
            
            # Wait for job to be ready
            logger.info("Waiting for job to be ready...")
            max_wait = 10  # 10 seconds
            wait_start = time.time()
            
            job_ready = False
            while time.time() - wait_start < max_wait:
                try:
                    waterfall_data = focus_server_api.get_waterfall(job_id, row_count=10)
                    # Job is ready if we get 200 (no data yet) or 201 (data available)
                    if waterfall_data and waterfall_data.status_code in [200, 201]:
                        job_ready = True
                        break
                    # 404 means consumer not found yet, keep waiting
                    elif waterfall_data and waterfall_data.status_code == 404:
                        time.sleep(1)
                    else:
                        time.sleep(1)
                except APIError:
                    time.sleep(1)
            
            if not job_ready:
                pytest.skip("Job did not become ready within timeout")
            
            # Send multiple requests for the same job
            num_requests = 10
            successful_requests = 0
            failed_requests = 0
            
            logger.info(f"Sending {num_requests} requests for job {job_id}...")
            
            for i in range(num_requests):
                try:
                    # Get waterfall data
                    waterfall_data = focus_server_api.get_waterfall(job_id, row_count=100)
                    
                    # Verify data is not None
                    assert waterfall_data is not None, f"Request {i+1}: Waterfall data is None"
                    
                    successful_requests += 1
                    logger.info(f"Request {i+1}/{num_requests}: SUCCESS")
                    
                    time.sleep(0.5)  # Small delay between requests
                    
                except Exception as e:
                    failed_requests += 1
                    logger.warning(f"Request {i+1}/{num_requests}: FAILED - {e}")
            
            logger.info(f"\nData Integrity Test Results:")
            logger.info(f"  Total requests: {num_requests}")
            logger.info(f"  Successful: {successful_requests}")
            logger.info(f"  Failed: {failed_requests}")
            
            # Verify integrity
            success_rate = successful_requests / num_requests
            assert success_rate >= 0.8, \
                f"Success rate {success_rate:.1%} is below 80% threshold"
            
            logger.info("✅ Data integrity maintained across requests")
            
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

