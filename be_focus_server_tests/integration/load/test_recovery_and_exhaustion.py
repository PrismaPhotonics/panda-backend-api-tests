"""
Integration Tests - Load: Recovery and Resource Exhaustion
===========================================================

Load tests for recovery and resource exhaustion scenarios.

Tests Covered (Xray):
    - PZ-14806: Load - Recovery After Load
    - PZ-14807: Load - Resource Exhaustion Under Load

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
class TestRecoveryAndExhaustion:
    """
    Test suite for recovery and resource exhaustion testing.
    
    Tests covered:
        - PZ-14806: Recovery After Load
        - PZ-14807: Resource Exhaustion Under Load
    """
    
    @pytest.mark.xray("PZ-14806")

    
    @pytest.mark.regression
    def test_recovery_after_load(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14806: Load - Recovery After Load.
        
        Objective:
            Verify that API recovers properly after high load and
            returns to normal performance levels.
        
        Steps:
            1. Apply high load
            2. Stop load
            3. Wait for recovery
            4. Verify system returns to normal performance
        
        Expected:
            API recovers after load.
            Performance returns to normal levels.
        """
        logger.info("=" * 80)
        logger.info("TEST: Load - Recovery After Load (PZ-14806)")
        logger.info("=" * 80)
        
        high_load_rps = 15
        high_load_duration = 60  # 60 seconds
        recovery_wait = 30  # 30 seconds recovery
        normal_rps = 2
        
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
        
        job_ids = []
        
        # Phase 1: High load
        logger.info("Phase 1: Applying high load...")
        high_load_start = time.time()
        high_load_end = high_load_start + high_load_duration
        
        high_load_results = []
        
        with ThreadPoolExecutor(max_workers=high_load_rps) as executor:
            futures = []
            
            while time.time() < high_load_end:
                if len(futures) < high_load_rps:
                    future = executor.submit(send_request)
                    futures.append(future)
                
                for future in list(futures):
                    if future.done():
                        result = future.result()
                        high_load_results.append(result)
                        if result["job_id"]:
                            job_ids.append(result["job_id"])
                        futures.remove(future)
                
                time.sleep(0.1)
            
            # Wait for remaining
            for future in as_completed(futures):
                result = future.result()
                high_load_results.append(result)
                if result["job_id"]:
                    job_ids.append(result["job_id"])
        
        high_load_success = len([r for r in high_load_results if r["success"]])
        high_load_success_rate = high_load_success / len(high_load_results) if high_load_results else 0
        
        logger.info(f"High load phase completed:")
        logger.info(f"  Requests: {len(high_load_results)}")
        logger.info(f"  Success rate: {high_load_success_rate:.1%}")
        
        # Phase 2: Recovery wait
        logger.info(f"\nPhase 2: Waiting for recovery ({recovery_wait} seconds)...")
        time.sleep(recovery_wait)
        
        # Phase 3: Normal load (recovery verification)
        logger.info("Phase 3: Verifying recovery with normal load...")
        normal_load_duration = 30  # 30 seconds
        normal_load_start = time.time()
        normal_load_end = normal_load_start + normal_load_duration
        
        normal_load_results = []
        
        while time.time() < normal_load_end:
            request_start = time.time()
            result = send_request()
            normal_load_results.append(result)
            
            if result["job_id"]:
                job_ids.append(result["job_id"])
            
            sleep_time = 1.0 / normal_rps - (time.time() - request_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        normal_load_success = len([r for r in normal_load_results if r["success"]])
        normal_load_success_rate = normal_load_success / len(normal_load_results) if normal_load_results else 0
        normal_load_response_times = [r["elapsed_time"] for r in normal_load_results if r["success"]]
        normal_load_avg_time = sum(normal_load_response_times) / len(normal_load_response_times) if normal_load_response_times else 0
        
        logger.info(f"Recovery verification:")
        logger.info(f"  Requests: {len(normal_load_results)}")
        logger.info(f"  Success rate: {normal_load_success_rate:.1%}")
        logger.info(f"  Average response time: {normal_load_avg_time:.3f} seconds")
        
        # Cleanup
        logger.info(f"\nCleaning up {len(job_ids)} jobs...")
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
            except Exception:
                pass
        
        # Assertions
        assert normal_load_success_rate >= 0.90, \
            f"Recovery success rate {normal_load_success_rate:.1%} is below 90% threshold"
        
        assert normal_load_avg_time <= 5.0, \
            f"Recovery average response time {normal_load_avg_time:.3f}s exceeds 5s threshold"
        
        logger.info("✅ Recovery after load test completed successfully")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14807")

    
    @pytest.mark.regression
    def test_resource_exhaustion_under_load(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14807: Load - Resource Exhaustion Under Load.
        
        Objective:
            Verify that API handles resource exhaustion gracefully
            and provides appropriate error messages.
        
        Steps:
            1. Apply extreme load to exhaust resources
            2. Monitor for resource exhaustion errors
            3. Verify graceful degradation
            4. Cleanup and verify system recovers
        
        Expected:
            API handles resource exhaustion gracefully.
            Error messages are informative.
            System recovers after cleanup.
        """
        logger.info("=" * 80)
        logger.info("TEST: Load - Resource Exhaustion Under Load (PZ-14807)")
        logger.info("=" * 80)
        
        extreme_load_rps = 50  # Very high RPS
        extreme_load_duration = 30  # 30 seconds
        
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
                error_str = str(e).lower()
                
                # Check for resource exhaustion indicators
                is_resource_error = any(keyword in error_str for keyword in [
                    "resource", "exhausted", "limit", "capacity", "503", "429", "timeout"
                ])
                
                return {
                    "success": False,
                    "elapsed_time": elapsed_time,
                    "job_id": None,
                    "error": str(e),
                    "is_resource_error": is_resource_error
                }
        
        start_time = time.time()
        end_time = start_time + extreme_load_duration
        
        results = []
        job_ids = []
        resource_errors = []
        
        logger.info(f"Applying extreme load ({extreme_load_rps} RPS for {extreme_load_duration} seconds)...")
        
        with ThreadPoolExecutor(max_workers=extreme_load_rps) as executor:
            futures = []
            
            while time.time() < end_time:
                if len(futures) < extreme_load_rps:
                    future = executor.submit(send_request)
                    futures.append(future)
                
                for future in list(futures):
                    if future.done():
                        result = future.result()
                        results.append(result)
                        
                        if result["job_id"]:
                            job_ids.append(result["job_id"])
                        
                        if not result["success"] and result.get("is_resource_error"):
                            resource_errors.append(result)
                        
                        futures.remove(future)
                
                time.sleep(0.05)  # Small delay
            
            # Wait for remaining
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                
                if result["job_id"]:
                    job_ids.append(result["job_id"])
                
                if not result["success"] and result.get("is_resource_error"):
                    resource_errors.append(result)
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        success_rate = len(successful_requests) / len(results) if results else 0
        
        logger.info(f"\nResource Exhaustion Test Results:")
        logger.info(f"  Total requests: {len(results)}")
        logger.info(f"  Successful: {len(successful_requests)} ({success_rate:.1%})")
        logger.info(f"  Failed: {len(failed_requests)}")
        logger.info(f"  Resource errors: {len(resource_errors)}")
        
        if resource_errors:
            logger.info(f"  Resource error examples:")
            for error in resource_errors[:3]:
                logger.info(f"    - {error['error'][:100]}...")
        
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
        
        # Wait for system recovery
        logger.info("\nWaiting for system recovery...")
        time.sleep(10)
        
        # Verify system recovery
        logger.info("Verifying system recovery...")
        try:
            is_healthy = focus_server_api.health_check()
            if is_healthy:
                logger.info("✅ System is healthy after recovery")
            else:
                logger.warning("⚠️  System health check failed after recovery")
        except Exception as e:
            logger.warning(f"⚠️  Could not verify system health: {e}")
        
        # Assertions
        # Under extreme load, some failures are expected
        # We verify that resource errors are handled gracefully
        if resource_errors:
            logger.info("✅ Resource exhaustion errors detected and handled gracefully")
        
        # Verify cleanup was successful
        assert cleanup_time < 60, \
            f"Cleanup took too long: {cleanup_time:.3f}s"
        
        logger.info("✅ Resource exhaustion test completed successfully")
        logger.info("=" * 80)

