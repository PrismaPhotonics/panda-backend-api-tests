"""
Integration Tests - Performance: Concurrent Requests
====================================================

Performance tests for concurrent requests handling.

Tests Covered (Xray):
    - PZ-14793: Performance - Concurrent Requests Performance

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


@pytest.mark.api



@pytest.mark.regression
class TestConcurrentPerformance:
    """
    Test suite for concurrent requests performance.
    
    Tests covered:
        - PZ-14793: Concurrent Requests Performance
    """
    
    @pytest.mark.xray("PZ-14793")

    
    @pytest.mark.regression
    def test_concurrent_requests_performance(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14793: Performance - Concurrent Requests Performance.
        
        Objective:
            Verify that API handles concurrent requests efficiently and
            maintains acceptable response times under concurrent load.
        
        Steps:
            1. Send multiple concurrent requests
            2. Measure response times
            3. Verify all requests complete successfully
            4. Verify response times are within acceptable limits
        
        Expected:
            All concurrent requests complete successfully.
            Average response time is within acceptable limits.
        """
        logger.info("=" * 80)
        logger.info("TEST: Performance - Concurrent Requests Performance (PZ-14793)")
        logger.info("=" * 80)
        
        num_concurrent_requests = 10
        max_response_time = 10.0  # 10 seconds per request
        
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
        
        def send_request(request_id: int) -> Dict[str, Any]:
            """Send a single request and return metrics."""
            start_time = time.time()
            try:
                response = focus_server_api.configure_streaming_job(config_request)
                elapsed_time = time.time() - start_time
                
                return {
                    "request_id": request_id,
                    "success": True,
                    "elapsed_time": elapsed_time,
                    "job_id": response.job_id if response else None,
                    "error": None
                }
            except Exception as e:
                elapsed_time = time.time() - start_time
                return {
                    "request_id": request_id,
                    "success": False,
                    "elapsed_time": elapsed_time,
                    "job_id": None,
                    "error": str(e)
                }
        
        # Send concurrent requests
        logger.info(f"Sending {num_concurrent_requests} concurrent requests...")
        start_time = time.time()
        
        results = []
        with ThreadPoolExecutor(max_workers=num_concurrent_requests) as executor:
            futures = [executor.submit(send_request, i) for i in range(num_concurrent_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        job_ids = [r["job_id"] for r in successful_requests if r["job_id"]]
        response_times = [r["elapsed_time"] for r in successful_requests]
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time_actual = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        logger.info(f"\nResults:")
        logger.info(f"  Total requests: {num_concurrent_requests}")
        logger.info(f"  Successful: {len(successful_requests)}")
        logger.info(f"  Failed: {len(failed_requests)}")
        logger.info(f"  Total time: {total_time:.3f} seconds")
        logger.info(f"  Average response time: {avg_response_time:.3f} seconds")
        logger.info(f"  Min response time: {min_response_time:.3f} seconds")
        logger.info(f"  Max response time: {max_response_time_actual:.3f} seconds")
        
        if failed_requests:
            logger.warning(f"Failed requests: {failed_requests[:3]}")
        
        # Cleanup
        logger.info(f"\nCleaning up {len(job_ids)} jobs...")
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
            except Exception:
                pass
        
        # Assertions
        success_rate = len(successful_requests) / num_concurrent_requests
        assert success_rate >= 0.8, \
            f"Success rate {success_rate:.1%} is below 80% threshold"
        
        if response_times:
            assert avg_response_time <= max_response_time, \
                f"Average response time {avg_response_time:.3f}s exceeds threshold {max_response_time}s"
            
            assert max_response_time_actual <= max_response_time * 2, \
                f"Max response time {max_response_time_actual:.3f}s exceeds threshold {max_response_time * 2}s"
        
        logger.info("✅ All concurrent requests completed successfully")
        logger.info("=" * 80)

