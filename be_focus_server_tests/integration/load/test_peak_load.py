"""
Integration Tests - Load: Peak Load
====================================

Load tests for peak load scenarios.

Tests Covered (Xray):
    - PZ-14802: Load - Peak Load - High RPS

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
@pytest.mark.nightly
@pytest.mark.load
@pytest.mark.regression
class TestPeakLoad:
    """
    Test suite for peak load testing.
    
    Tests covered:
        - PZ-14802: Peak Load - High RPS
    """
    
    @pytest.mark.xray("PZ-14802")
    @pytest.mark.xray("PZ-14800")

    @pytest.mark.regression
    def test_peak_load_high_rps(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14802: Load - Peak Load - High RPS.
        
        Objective:
            Verify that API can handle peak load with high requests per second
            (RPS) without failures or significant degradation.
        
        Steps:
            1. Send requests at high RPS for a short period
            2. Measure success rate and response times
            3. Verify system remains stable
            4. Cleanup all created jobs
        
        Expected:
            API handles peak load successfully.
            Success rate remains high.
            Response times remain acceptable.
        """
        logger.info("=" * 80)
        logger.info("TEST: Load - Peak Load - High RPS (PZ-14802)")
        logger.info("=" * 80)
        
        peak_duration = 60  # 60 seconds
        target_rps = 10  # 10 requests per second
        total_requests = peak_duration * target_rps  # 600 requests
        
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
        
        def send_request(request_id: int) -> Dict[str, Any]:
            """Send a single request."""
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
        
        # Send requests at high RPS
        logger.info(f"Sending {total_requests} requests at {target_rps} RPS for {peak_duration} seconds...")
        start_time = time.time()
        
        results = []
        request_id = 0
        
        # Use thread pool to send concurrent requests
        with ThreadPoolExecutor(max_workers=target_rps * 2) as executor:
            futures = []
            
            # Submit requests continuously
            while time.time() - start_time < peak_duration:
                if len(futures) < target_rps * 2:  # Keep pool filled
                    request_id += 1
                    future = executor.submit(send_request, request_id)
                    futures.append(future)
                
                # Collect completed requests
                for future in list(futures):
                    if future.done():
                        results.append(future.result())
                        futures.remove(future)
                
                # Maintain RPS
                time.sleep(1.0 / target_rps)
            
            # Wait for remaining requests
            for future in as_completed(futures):
                results.append(future.result())
        
        total_time = time.time() - start_time
        actual_rps = len(results) / total_time if total_time > 0 else 0
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        job_ids = [r["job_id"] for r in successful_requests if r["job_id"]]
        response_times = [r["elapsed_time"] for r in successful_requests]
        
        success_rate = len(successful_requests) / len(results) if results else 0
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        logger.info(f"\nPeak Load Test Results:")
        logger.info(f"  Duration: {total_time:.1f} seconds")
        logger.info(f"  Total requests: {len(results)}")
        logger.info(f"  Actual RPS: {actual_rps:.2f}")
        logger.info(f"  Target RPS: {target_rps}")
        logger.info(f"  Successful: {len(successful_requests)} ({success_rate:.1%})")
        logger.info(f"  Failed: {len(failed_requests)}")
        logger.info(f"  Average response time: {avg_response_time:.3f} seconds")
        logger.info(f"  Max response time: {max_response_time:.3f} seconds")
        
        # Cleanup
        logger.info(f"\nCleaning up {len(job_ids)} jobs...")
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
            except Exception:
                pass
        
        # Assertions
        assert success_rate >= 0.85, \
            f"Success rate {success_rate:.1%} is below 85% threshold"
        
        assert actual_rps >= target_rps * 0.8, \
            f"Actual RPS {actual_rps:.2f} is below 80% of target {target_rps}"
        
        logger.info("✅ Peak load test completed successfully")
        logger.info("=" * 80)

