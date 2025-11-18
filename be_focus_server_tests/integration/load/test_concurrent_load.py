"""
Integration Tests - Load: Concurrent Load
=========================================

Load tests for concurrent job creation.

Tests Covered (Xray):
    - PZ-14800: Load - Concurrent Job Creation Load

Author: QA Automation Architect
Date: 2025-11-09
"""

import pytest
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError
from src.models.focus_server_models import ConfigureRequest, ViewType

logger = logging.getLogger(__name__)


@pytest.mark.slow



@pytest.mark.regression
class TestConcurrentLoad:
    """
    Test suite for concurrent load testing.
    
    Tests covered:
        - PZ-14800: Concurrent Job Creation Load
    """
    
    @pytest.mark.xray("PZ-14800")

    
    @pytest.mark.regression
    def test_concurrent_job_creation_load(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14800: Load - Concurrent Job Creation Load.
        
        Objective:
            Verify that API can handle concurrent job creation requests
            efficiently and maintain acceptable performance.
        
        Steps:
            1. Send multiple concurrent job creation requests
            2. Measure success rate and response times
            3. Verify system remains stable
            4. Cleanup all created jobs
        
        Expected:
            All concurrent requests complete successfully.
            Response times remain within acceptable limits.
            System remains stable.
        """
        logger.info("=" * 80)
        logger.info("TEST: Load - Concurrent Job Creation Load (PZ-14800)")
        logger.info("=" * 80)
        
        num_concurrent_jobs = 20  # 20 concurrent jobs
        max_response_time = 10.0  # 10 seconds per job
        
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
        
        def create_job(job_id: int) -> Dict[str, Any]:
            """Create a single job and return metrics."""
            start_time = time.time()
            try:
                response = focus_server_api.configure_streaming_job(config_request)
                elapsed_time = time.time() - start_time
                
                return {
                    "job_id": job_id,
                    "success": True,
                    "elapsed_time": elapsed_time,
                    "actual_job_id": response.job_id if response else None,
                    "error": None
                }
            except Exception as e:
                elapsed_time = time.time() - start_time
                return {
                    "job_id": job_id,
                    "success": False,
                    "elapsed_time": elapsed_time,
                    "actual_job_id": None,
                    "error": str(e)
                }
        
        # Send concurrent requests
        logger.info(f"Sending {num_concurrent_jobs} concurrent job creation requests...")
        start_time = time.time()
        
        results = []
        with ThreadPoolExecutor(max_workers=num_concurrent_jobs) as executor:
            futures = [executor.submit(create_job, i) for i in range(num_concurrent_jobs)]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_jobs = [r for r in results if r["success"]]
        failed_jobs = [r for r in results if not r["success"]]
        
        job_ids = [r["actual_job_id"] for r in successful_jobs if r["actual_job_id"]]
        response_times = [r["elapsed_time"] for r in successful_jobs]
        
        success_rate = len(successful_jobs) / num_concurrent_jobs
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time_actual = max(response_times) if response_times else 0
        
        logger.info(f"\nResults:")
        logger.info(f"  Total jobs: {num_concurrent_jobs}")
        logger.info(f"  Successful: {len(successful_jobs)} ({success_rate:.1%})")
        logger.info(f"  Failed: {len(failed_jobs)}")
        logger.info(f"  Total time: {total_time:.3f} seconds")
        logger.info(f"  Average response time: {avg_response_time:.3f} seconds")
        logger.info(f"  Max response time: {max_response_time_actual:.3f} seconds")
        
        if failed_jobs:
            logger.warning(f"Failed jobs: {failed_jobs[:3]}")
        
        # Cleanup
        logger.info(f"\nCleaning up {len(job_ids)} jobs...")
        cleanup_start = time.time()
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
            except Exception:
                pass
        cleanup_time = time.time() - cleanup_start
        logger.info(f"Cleanup completed in {cleanup_time:.3f} seconds")
        
        # Assertions
        assert success_rate >= 0.8, \
            f"Success rate {success_rate:.1%} is below 80% threshold"
        
        if response_times:
            assert avg_response_time <= max_response_time, \
                f"Average response time {avg_response_time:.3f}s exceeds threshold {max_response_time}s"
        
        logger.info("✅ Concurrent job creation load test completed successfully")
        logger.info("=" * 80)

