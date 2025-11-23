"""
Integration Tests - Performance Latency Requirements
=====================================================

Tests for performance and latency requirements based on Xray specifications.

Validates that Focus Server meets performance SLA requirements:
- Configuration endpoint latency
- Job creation time
- Response time consistency

Xray Tests Covered:
    - PZ-13920: Performance - Configuration Endpoint P95 < 500ms
    - PZ-13921: Performance - Configuration Endpoint P99 < 1000ms
    - PZ-13922: Performance - Job Creation Time < 2 seconds

Author: QA Automation Architect  
Date: 2025-10-27
"""

import pytest
import logging
import time
import statistics
from typing import List, Dict

from src.models.focus_server_models import ConfigureRequest, ViewType
from src.apis.focus_server_api import FocusServerAPI

logger = logging.getLogger(__name__)


# ===================================================================
# Test Class: Configuration Endpoint Latency
# ===================================================================

@pytest.mark.critical
@pytest.mark.high
@pytest.mark.regression
class TestConfigurationEndpointLatency:
    """
    Test suite for configuration endpoint latency requirements.
    
    Tests covered:
        - PZ-13920: P95 latency < 500ms
        - PZ-13921: P99 latency < 1000ms
        - PZ-13922: Job creation < 2 seconds
    
    Priority: HIGH
    """
    
    def _measure_latency(self, focus_server_api: FocusServerAPI, num_samples: int = 20) -> List[float]:
        """
        Measure latency for multiple configuration requests.
        
        Args:
            focus_server_api: Focus Server API client
            num_samples: Number of measurements to take
            
        Returns:
            List of latency measurements in milliseconds
        """
        latencies = []
        
        for i in range(num_samples):
            config = {
                "displayTimeAxisDuration": 10,
                "nfftSelection": 1024,
                "displayInfo": {"height": 1000},
                "channels": {"min": 1, "max": 50},
                "frequencyRange": {"min": 0, "max": 500},
                "start_time": None,
                "end_time": None,
                "view_type": ViewType.MULTICHANNEL
            }
            
            start_time = time.time()
            config_request = ConfigureRequest(**config)
            response = focus_server_api.configure_streaming_job(config_request)
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
            
            logger.info(f"Sample {i+1}/{num_samples}: {latency_ms:.2f}ms")
            
            # Clean up
            if hasattr(response, 'job_id') and response.job_id:
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
            
            # Small delay between requests
            time.sleep(0.1)
        
        return latencies
    
    @pytest.mark.xray("PZ-14092")

    
    @pytest.mark.regression
    def test_config_endpoint_p95_latency(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-13920: Configuration endpoint P95 latency < 500ms.
        
        Steps:
            1. Send 20 configuration requests
            2. Measure response time for each
            3. Calculate P95 (95th percentile)
            4. Verify P95 < 500ms
        
        Expected:
            - P95 latency < 500ms
            - All requests succeed
        
        Jira: PZ-13920
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: Configuration Endpoint P95 Latency (PZ-13920)")
        logger.info("=" * 80)
        
        num_samples = 20
        p95_threshold_ms = 500
        
        logger.info(f"Measuring latency for {num_samples} requests...")
        latencies = self._measure_latency(focus_server_api, num_samples)
        
        # Calculate statistics
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        mean_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        
        logger.info("")
        logger.info("Latency Statistics:")
        logger.info(f"  Mean:   {mean_latency:.2f}ms")
        logger.info(f"  Median: {median_latency:.2f}ms")
        logger.info(f"  P95:    {p95_latency:.2f}ms")
        logger.info(f"  Min:    {min_latency:.2f}ms")
        logger.info(f"  Max:    {max_latency:.2f}ms")
        logger.info("")
        
        # Verify P95 requirement
        assert p95_latency < p95_threshold_ms, \
            f"P95 latency {p95_latency:.2f}ms exceeds threshold {p95_threshold_ms}ms"
        
        logger.info(f"✅ P95 latency {p95_latency:.2f}ms meets requirement (< {p95_threshold_ms}ms)")
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: P95 Latency Requirement Met")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14091")

    
    @pytest.mark.regression
    def test_config_endpoint_p99_latency(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-13921: Configuration endpoint P99 latency < 1000ms.
        
        Steps:
            1. Send 100 configuration requests
            2. Measure response time for each
            3. Calculate P99 (99th percentile)
            4. Verify P99 < 1000ms
        
        Expected:
            - P99 latency < 1000ms
            - At least 99% of requests complete within threshold
        
        Jira: PZ-13921
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: Configuration Endpoint P99 Latency (PZ-13921)")
        logger.info("=" * 80)
        
        num_samples = 100
        p99_threshold_ms = 1000
        
        logger.info(f"Measuring latency for {num_samples} requests...")
        logger.info("(This may take a few minutes...)")
        
        latencies = self._measure_latency(focus_server_api, num_samples)
        
        # Calculate statistics
        p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
        mean_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]
        
        logger.info("")
        logger.info("Latency Statistics:")
        logger.info(f"  Mean:   {mean_latency:.2f}ms")
        logger.info(f"  P95:    {p95_latency:.2f}ms")
        logger.info(f"  P99:    {p99_latency:.2f}ms")
        logger.info(f"  Samples: {num_samples}")
        logger.info("")
        
        # Verify P99 requirement
        assert p99_latency < p99_threshold_ms, \
            f"P99 latency {p99_latency:.2f}ms exceeds threshold {p99_threshold_ms}ms"
        
        logger.info(f"✅ P99 latency {p99_latency:.2f}ms meets requirement (< {p99_threshold_ms}ms)")
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: P99 Latency Requirement Met")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14090")

    
    @pytest.mark.regression
    def test_job_creation_time(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-13922: Job creation time < 2 seconds.
        
        Steps:
            1. Send configuration request
            2. Measure time from request to job_id return
            3. Verify time < 2 seconds
        
        Expected:
            - Job creation completes within 2 seconds
            - job_id returned successfully
        
        Jira: PZ-13922
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: Job Creation Time (PZ-13922)")
        logger.info("=" * 80)
        
        threshold_seconds = 2.0
        num_tests = 10
        
        creation_times = []
        
        for i in range(num_tests):
            logger.info(f"\nTest {i+1}/{num_tests}:")
            
            config = {
                "displayTimeAxisDuration": 10,
                "nfftSelection": 1024,
                "displayInfo": {"height": 1000},
                "channels": {"min": 1, "max": 50},
                "frequencyRange": {"min": 0, "max": 500},
                "start_time": None,
                "end_time": None,
                "view_type": ViewType.MULTICHANNEL
            }
            
            start_time = time.time()
            config_request = ConfigureRequest(**config)
            response = focus_server_api.configure_streaming_job(config_request)
            end_time = time.time()
            
            creation_time = end_time - start_time
            creation_times.append(creation_time)
            
            assert hasattr(response, 'job_id') and response.job_id, \
                "Job creation should return job_id"
            
            logger.info(f"  Job {response.job_id} created in {creation_time:.3f}s")
            
            # Verify threshold
            assert creation_time < threshold_seconds, \
                f"Job creation took {creation_time:.3f}s, exceeds threshold {threshold_seconds}s"
            
            # Clean up
            try:
                focus_server_api.cancel_job(response.job_id)
            except:
                pass
        
        # Statistics
        mean_time = statistics.mean(creation_times)
        max_time = max(creation_times)
        min_time = min(creation_times)
        
        logger.info("")
        logger.info("Job Creation Statistics:")
        logger.info(f"  Mean: {mean_time:.3f}s")
        logger.info(f"  Min:  {min_time:.3f}s")
        logger.info(f"  Max:  {max_time:.3f}s")
        logger.info(f"  All:  {' '.join([f'{t:.3f}s' for t in creation_times])}")
        logger.info("")
        
        logger.info(f"✅ All jobs created within {threshold_seconds}s threshold")
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Job Creation Time Requirement Met")
        logger.info("=" * 80)


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary


@pytest.mark.regression
def test_latency_requirements_summary():
    """
    Summary test for performance latency requirements.
    
    Xray Tests Covered:
        - PZ-13920: Configuration Endpoint P95 < 500ms
        - PZ-13921: Configuration Endpoint P99 < 1000ms
        - PZ-13922: Job Creation Time < 2 seconds
    
    This test always passes and serves as documentation.
    """
    logger.info("=" * 80)
    logger.info("Performance Latency Requirements Test Suite Summary")
    logger.info("=" * 80)
    logger.info("Tests in this module:")
    logger.info("  1. PZ-13920: P95 latency < 500ms")
    logger.info("  2. PZ-13921: P99 latency < 1000ms")
    logger.info("  3. PZ-13922: Job creation < 2 seconds")
    logger.info("=" * 80)

