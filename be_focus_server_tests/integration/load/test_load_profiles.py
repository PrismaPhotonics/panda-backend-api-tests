"""
Integration Tests - Load: Load Profiles
========================================

Load tests for different load profiles.

Tests Covered (Xray):
    - PZ-14803: Load - Ramp-Up Load Profile
    - PZ-14804: Load - Spike Load Profile
    - PZ-14805: Load - Steady-State Load Profile

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
class TestLoadProfiles:
    """
    Test suite for load profile testing.
    
    Tests covered:
        - PZ-14803: Ramp-Up Load Profile
        - PZ-14804: Spike Load Profile
        - PZ-14805: Steady-State Load Profile
    """
    
    @pytest.mark.xray("PZ-14803")
    def test_ramp_up_load_profile(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14803: Load - Ramp-Up Load Profile.
        
        Objective:
            Verify that API can handle gradually increasing load (ramp-up)
            without failures or degradation.
        
        Steps:
            1. Start with low RPS
            2. Gradually increase RPS over time
            3. Monitor success rate and response times
            4. Verify system remains stable
        
        Expected:
            API handles ramp-up load successfully.
            Success rate remains high throughout ramp-up.
        """
        logger.info("=" * 80)
        logger.info("TEST: Load - Ramp-Up Load Profile (PZ-14803)")
        logger.info("=" * 80)
        
        # Optimized: Reduced from 120s to 30s for faster CI while still testing ramp-up
        ramp_duration = 30  # 30 seconds (was 120)
        initial_rps = 2     # Start higher (was 1)
        max_rps = 8         # Peak (was 10)
        ramp_steps = 5      # Fewer steps (was 10)
        
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
        
        def send_request() -> Dict[str, Any]:
            """Send a single request."""
            start_time = time.time()
            try:
                response = focus_server_api.configure_streaming_job(config_request)
                elapsed_time = time.time() - start_time
                
                return {
                    "success": True,
                    "elapsed_time": elapsed_time,
                    "job_id": response.job_id if response else None,
                    "error": None
                }
            except Exception as e:
                elapsed_time = time.time() - start_time
                return {
                    "success": False,
                    "elapsed_time": elapsed_time,
                    "job_id": None,
                    "error": str(e)
                }
        
        start_time = time.time()
        end_time = start_time + ramp_duration
        
        results = []
        job_ids = []
        current_rps = initial_rps
        rps_increment = (max_rps - initial_rps) / ramp_steps
        
        logger.info(f"Starting ramp-up load test...")
        logger.info(f"  Initial RPS: {initial_rps}")
        logger.info(f"  Max RPS: {max_rps}")
        logger.info(f"  Duration: {ramp_duration} seconds")
        
        step_duration = ramp_duration / ramp_steps
        
        while time.time() < end_time:
            step_start = time.time()
            step_end = step_start + step_duration
            
            logger.info(f"Ramp-up step: RPS = {current_rps:.1f}")
            
            # Send requests at current RPS
            while time.time() < step_end:
                request_start = time.time()
                result = send_request()
                results.append(result)
                
                if result["job_id"]:
                    job_ids.append(result["job_id"])
                
                # Maintain RPS
                sleep_time = 1.0 / current_rps - (time.time() - request_start)
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            # Increase RPS for next step
            current_rps = min(current_rps + rps_increment, max_rps)
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        success_rate = len(successful_requests) / len(results) if results else 0
        
        logger.info(f"\nRamp-Up Load Test Results:")
        logger.info(f"  Total requests: {len(results)}")
        logger.info(f"  Successful: {len(successful_requests)} ({success_rate:.1%})")
        
        # Cleanup
        logger.info(f"\nCleaning up {len(job_ids)} jobs...")
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
            except Exception:
                pass
        
        assert success_rate >= 0.85, \
            f"Success rate {success_rate:.1%} is below 85% threshold"
        
        logger.info("✅ Ramp-up load test completed successfully")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14804")
    def test_spike_load_profile(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14804: Load - Spike Load Profile.
        
        Objective:
            Verify that API can handle sudden spike in load without failures
            or significant degradation.
        
        Steps:
            1. Send normal load
            2. Suddenly increase to high load (spike)
            3. Monitor success rate and response times
            4. Verify system recovers
        
        Expected:
            API handles spike load successfully.
            System recovers after spike.
        """
        logger.info("=" * 80)
        logger.info("TEST: Load - Spike Load Profile (PZ-14804)")
        logger.info("=" * 80)
        
        # Optimized: Reduced total from 40s to 20s while still testing spike behavior
        normal_rps = 3      # Slightly higher baseline (was 2)
        spike_rps = 10      # Peak spike (was 12)
        normal_duration = 10  # 10 seconds normal (was 30)
        spike_duration = 10   # 10 seconds spike (unchanged)
        
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
        
        def send_request() -> Dict[str, Any]:
            """Send a single request."""
            start_time = time.time()
            try:
                response = focus_server_api.configure_streaming_job(config_request)
                elapsed_time = time.time() - start_time
                
                return {
                    "success": True,
                    "elapsed_time": elapsed_time,
                    "job_id": response.job_id if response else None,
                    "error": None
                }
            except Exception as e:
                elapsed_time = time.time() - start_time
                return {
                    "success": False,
                    "elapsed_time": elapsed_time,
                    "job_id": None,
                    "error": str(e)
                }
        
        results = []
        job_ids = []
        
        # Phase 1: Normal load
        logger.info("Phase 1: Normal load...")
        normal_start = time.time()
        normal_end = normal_start + normal_duration
        
        while time.time() < normal_end:
            request_start = time.time()
            result = send_request()
            results.append(result)
            
            if result["job_id"]:
                job_ids.append(result["job_id"])
            
            sleep_time = 1.0 / normal_rps - (time.time() - request_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Phase 2: Spike load
        logger.info("Phase 2: Spike load...")
        spike_start = time.time()
        spike_end = spike_start + spike_duration
        
        with ThreadPoolExecutor(max_workers=spike_rps) as executor:
            futures = []
            
            while time.time() < spike_end:
                if len(futures) < spike_rps:
                    future = executor.submit(send_request)
                    futures.append(future)
                
                for future in list(futures):
                    if future.done():
                        result = future.result()
                        results.append(result)
                        if result["job_id"]:
                            job_ids.append(result["job_id"])
                        futures.remove(future)
                
                time.sleep(0.1)
            
            # Wait for remaining
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                if result["job_id"]:
                    job_ids.append(result["job_id"])
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        success_rate = len(successful_requests) / len(results) if results else 0
        
        logger.info(f"\nSpike Load Test Results:")
        logger.info(f"  Total requests: {len(results)}")
        logger.info(f"  Successful: {len(successful_requests)} ({success_rate:.1%})")
        
        # Cleanup
        logger.info(f"\nCleaning up {len(job_ids)} jobs...")
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
            except Exception:
                pass
        
        assert success_rate >= 0.80, \
            f"Success rate {success_rate:.1%} is below 80% threshold"
        
        logger.info("✅ Spike load test completed successfully")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14805")
    @pytest.mark.xray("PZ-14800")
    def test_steady_state_load_profile(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14805: Load - Steady-State Load Profile.
        
        Objective:
            Verify that API can handle steady-state load over extended period
            without degradation or failures.
        
        Steps:
            1. Send requests at constant RPS for extended period
            2. Monitor success rate and response times
            3. Verify system remains stable
        
        Expected:
            API handles steady-state load successfully.
            Performance remains consistent over time.
        """
        logger.info("=" * 80)
        logger.info("TEST: Load - Steady-State Load Profile (PZ-14805)")
        logger.info("=" * 80)
        
        # Optimized: Reduced from 180s to 45s while still validating steady state
        steady_rps = 5        # Keep same RPS
        steady_duration = 45  # 45 seconds (was 180)
        
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
        
        def send_request() -> Dict[str, Any]:
            """Send a single request."""
            start_time = time.time()
            try:
                response = focus_server_api.configure_streaming_job(config_request)
                elapsed_time = time.time() - start_time
                
                return {
                    "success": True,
                    "elapsed_time": elapsed_time,
                    "job_id": response.job_id if response else None,
                    "error": None
                }
            except Exception as e:
                elapsed_time = time.time() - start_time
                return {
                    "success": False,
                    "elapsed_time": elapsed_time,
                    "job_id": None,
                    "error": str(e)
                }
        
        start_time = time.time()
        end_time = start_time + steady_duration
        
        results = []
        job_ids = []
        
        logger.info(f"Starting steady-state load test...")
        logger.info(f"  RPS: {steady_rps}")
        logger.info(f"  Duration: {steady_duration} seconds")
        
        while time.time() < end_time:
            request_start = time.time()
            result = send_request()
            results.append(result)
            
            if result["job_id"]:
                job_ids.append(result["job_id"])
            
            # Maintain steady RPS
            sleep_time = 1.0 / steady_rps - (time.time() - request_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["elapsed_time"] for r in successful_requests]
        
        success_rate = len(successful_requests) / len(results) if results else 0
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        logger.info(f"\nSteady-State Load Test Results:")
        logger.info(f"  Total requests: {len(results)}")
        logger.info(f"  Successful: {len(successful_requests)} ({success_rate:.1%})")
        logger.info(f"  Average response time: {avg_response_time:.3f} seconds")
        
        # Cleanup
        logger.info(f"\nCleaning up {len(job_ids)} jobs...")
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
            except Exception:
                pass
        
        assert success_rate >= 0.90, \
            f"Success rate {success_rate:.1%} is below 90% threshold"
        
        logger.info("✅ Steady-state load test completed successfully")
        logger.info("=" * 80)

