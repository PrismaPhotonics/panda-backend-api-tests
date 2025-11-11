"""
Integration Tests - Performance: Network Latency Impact
=======================================================

Performance tests for network latency impact.

Tests Covered (Xray):
    - PZ-14798: Performance - Network Latency Impact
    - PZ-14799: Performance - End-to-End Latency

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


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.api
class TestNetworkLatency:
    """
    Test suite for network latency impact.
    
    Tests covered:
        - PZ-14798: Network Latency Impact
        - PZ-14799: End-to-End Latency
    """
    
    @pytest.mark.xray("PZ-14798")
    def test_network_latency_impact(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14798: Performance - Network Latency Impact.
        
        Objective:
            Verify that network latency does not significantly impact
            API performance and response times.
        
        Steps:
            1. Send multiple requests
            2. Measure response times
            3. Calculate network latency component
            4. Verify latency impact is acceptable
        
        Expected:
            Network latency impact is minimal and acceptable.
        """
        logger.info("=" * 80)
        logger.info("TEST: Performance - Network Latency Impact (PZ-14798)")
        logger.info("=" * 80)
        
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
        
        num_requests = 5
        response_times = []
        job_ids = []
        
        # Send multiple requests to measure latency
        for i in range(num_requests):
            start_time = time.time()
            
            try:
                response = focus_server_api.configure_streaming_job(config_request)
                elapsed_time = time.time() - start_time
                
                response_times.append(elapsed_time)
                
                if response.job_id:
                    job_ids.append(response.job_id)
                
                logger.info(f"Request {i+1}/{num_requests}: {elapsed_time:.3f} seconds")
                
            except Exception as e:
                logger.error(f"Request {i+1} failed: {e}")
        
        # Analyze latency
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Estimate network latency (difference between min and max)
            latency_variance = max_response_time - min_response_time
            
            logger.info(f"\nLatency Analysis:")
            logger.info(f"  Average response time: {avg_response_time:.3f} seconds")
            logger.info(f"  Min response time: {min_response_time:.3f} seconds")
            logger.info(f"  Max response time: {max_response_time:.3f} seconds")
            logger.info(f"  Latency variance: {latency_variance:.3f} seconds")
            
            # Cleanup
            logger.info(f"\nCleaning up {len(job_ids)} jobs...")
            for job_id in job_ids:
                try:
                    focus_server_api.cancel_job(job_id)
                except Exception:
                    pass
            
            # Verify latency variance is acceptable (less than 2 seconds)
            max_latency_variance = 2.0  # seconds
            assert latency_variance <= max_latency_variance, \
                f"Latency variance {latency_variance:.3f}s exceeds threshold {max_latency_variance}s"
            
            logger.info(f"✅ Network latency impact is acceptable: {latency_variance:.3f}s <= {max_latency_variance}s")
        else:
            pytest.fail("No successful requests to analyze latency")
        
        logger.info("✅ Test completed")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14799")
    @pytest.mark.xray("PZ-14090")
    def test_end_to_end_latency(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14799: Performance - End-to-End Latency.
        
        Objective:
            Verify that end-to-end latency (from request to response) is
            within acceptable limits for the complete workflow.
        
        Steps:
            1. Send POST /configure request
            2. Wait for job to be ready
            3. Send GET /waterfall request
            4. Measure total end-to-end latency
            5. Verify latency is within acceptable limits
        
        Expected:
            End-to-end latency is within acceptable limits.
        """
        logger.info("=" * 80)
        logger.info("TEST: Performance - End-to-End Latency (PZ-14799)")
        logger.info("=" * 80)
        
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
        
        max_end_to_end_latency = 10.0  # 10 seconds
        
        # Start end-to-end timing
        start_time = time.time()
        
        try:
            # Step 1: Configure job
            logger.info("Step 1: Configuring job...")
            configure_start = time.time()
            response = focus_server_api.configure_streaming_job(config_request)
            configure_time = time.time() - configure_start
            
            job_id = response.job_id
            if not job_id:
                pytest.fail("No job_id returned from configure request")
            
            logger.info(f"Job configured in {configure_time:.3f} seconds: {job_id}")
            
            # Step 2: Wait for job to be ready (polling)
            logger.info("Step 2: Waiting for job to be ready...")
            wait_start = time.time()
            max_wait_time = 5.0  # 5 seconds
            wait_timeout = time.time() + max_wait_time
            
            job_ready = False
            while time.time() < wait_timeout:
                try:
                    # Try to get waterfall data (indicates job is ready)
                    waterfall_data = focus_server_api.get_waterfall_data(job_id, row_count=10)
                    job_ready = True
                    break
                except APIError:
                    # Job not ready yet, wait a bit
                    time.sleep(0.5)
            
            wait_time = time.time() - wait_start
            
            if not job_ready:
                logger.warning("Job did not become ready within timeout")
                # Continue anyway to measure what we can
            
            logger.info(f"Job ready in {wait_time:.3f} seconds")
            
            # Step 3: Get waterfall data
            logger.info("Step 3: Getting waterfall data...")
            waterfall_start = time.time()
            waterfall_data = focus_server_api.get_waterfall_data(job_id, row_count=100)
            waterfall_time = time.time() - waterfall_start
            
            logger.info(f"Waterfall data retrieved in {waterfall_time:.3f} seconds")
            
            # Total end-to-end latency
            total_time = time.time() - start_time
            
            logger.info(f"\nEnd-to-End Latency Breakdown:")
            logger.info(f"  Configure: {configure_time:.3f} seconds")
            logger.info(f"  Wait for ready: {wait_time:.3f} seconds")
            logger.info(f"  Waterfall: {waterfall_time:.3f} seconds")
            logger.info(f"  Total: {total_time:.3f} seconds")
            logger.info(f"  Threshold: {max_end_to_end_latency} seconds")
            
            # Cleanup
            try:
                focus_server_api.cancel_job(job_id)
            except Exception as e:
                logger.warning(f"Could not cancel job: {e}")
            
            # Verify end-to-end latency
            assert total_time <= max_end_to_end_latency, \
                f"End-to-end latency {total_time:.3f}s exceeds threshold {max_end_to_end_latency}s"
            
            logger.info(f"✅ End-to-end latency is within threshold: {total_time:.3f}s <= {max_end_to_end_latency}s")
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"End-to-end test failed after {total_time:.3f} seconds: {e}")
            pytest.fail(f"End-to-end test failed: {e}")
        
        logger.info("✅ Test completed")
        logger.info("=" * 80)

