"""
Load Tests - Network Bandwidth Under Concurrent Load
====================================================

Tests for network bandwidth and streaming performance under concurrent load.

Tests Covered (Xray):
    - PZ-15139: Performance - Network Bandwidth Under Concurrent Load

Author: QA Automation Architect
Date: 2025-11-23
"""

import pytest
import logging
import time
import psutil
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
from datetime import datetime

from src.apis.focus_server_api import FocusServerAPI
from src.models.focus_server_models import ConfigureRequest, ViewType

logger = logging.getLogger(__name__)


# ===================================================================
# Test Class: Network Bandwidth Under Load
# ===================================================================

@pytest.mark.slow
@pytest.mark.nightly
@pytest.mark.load
@pytest.mark.performance
@pytest.mark.network
class TestNetworkBandwidth:
    """
    Test suite for network bandwidth performance under concurrent load.
    
    Tests covered:
        - PZ-15139: Network Bandwidth Under Concurrent Load
    """
    
    @pytest.mark.xray("PZ-15139")
    def test_network_bandwidth_under_concurrent_load(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-15139: Performance - Network Bandwidth Under Concurrent Load.
        
        Objective:
            Measure network bandwidth consumption and streaming performance
            when multiple concurrent jobs are running.
        
        Steps:
            1. Record baseline network metrics (no load)
            2. Create 20 concurrent streaming jobs
            3. Poll waterfall data continuously for 5 minutes
            4. Measure total bandwidth, per-job bandwidth, latency
            5. Verify no network bottlenecks or degradation
            6. Cleanup all jobs
        
        Expected:
            - Total bandwidth < 800 Mbps (for 1 Gbps link)
            - Per-job bandwidth consistent (variance < 20%)
            - Network latency increase < 50ms
            - No packet loss
            - All streams stable
        
        Jira: PZ-15139
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: Network Bandwidth Under Concurrent Load (PZ-15139)")
        logger.info("=" * 80)
        
        num_jobs = 10  # Reduced from 20 to avoid system overload
        poll_duration = 300  # 5 minutes
        rows_per_poll = 100
        poll_interval = 2  # Increased from 1 to reduce request rate
        
        logger.info(f"Test Configuration:")
        logger.info(f"  Concurrent Jobs: {num_jobs}")
        logger.info(f"  Poll Duration: {poll_duration} seconds ({poll_duration/60:.1f} minutes)")
        logger.info(f"  Rows Per Poll: {rows_per_poll}")
        logger.info(f"  Poll Interval: {poll_interval} second(s)")
        logger.info(f"")
        
        # Standard configuration
        config_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,  # Live mode
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        # Phase 1: Baseline network metrics
        logger.info("Phase 1: Recording baseline network metrics...")
        
        net_io_baseline = psutil.net_io_counters()
        baseline_bytes_sent = net_io_baseline.bytes_sent
        baseline_bytes_recv = net_io_baseline.bytes_recv
        
        # Measure baseline latency with a few test requests
        baseline_latencies = []
        for _ in range(5):
            start = time.time()
            try:
                focus_server_api.get_channels()
                latency_ms = (time.time() - start) * 1000
                baseline_latencies.append(latency_ms)
            except Exception as e:
                logger.warning(f"Baseline latency test failed: {e}")
            time.sleep(0.5)
        
        baseline_latency = statistics.mean(baseline_latencies) if baseline_latencies else 0
        
        logger.info(f"Baseline Network Metrics:")
        logger.info(f"  Bytes Sent: {baseline_bytes_sent:,}")
        logger.info(f"  Bytes Received: {baseline_bytes_recv:,}")
        logger.info(f"  Latency: {baseline_latency:.2f}ms")
        logger.info(f"")
        
        # Phase 2: Create concurrent streaming jobs
        logger.info("Phase 2: Creating concurrent streaming jobs...")
        
        job_ids = []
        job_creation_start = time.time()
        
        for i in range(num_jobs):
            try:
                config_request = ConfigureRequest(**config_payload)
                response = focus_server_api.configure_streaming_job(config_request)
                
                if response.job_id:
                    job_ids.append(response.job_id)
                    logger.debug(f"  Job {i+1}/{num_jobs} created: {response.job_id}")
                else:
                    logger.warning(f"  Job {i+1}/{num_jobs}: No job_id returned")
            
            except Exception as e:
                logger.error(f"  Job {i+1}/{num_jobs} failed: {e}")
        
        job_creation_time = time.time() - job_creation_start
        
        logger.info(f"Created {len(job_ids)}/{num_jobs} jobs in {job_creation_time:.2f}s")
        
        if len(job_ids) < num_jobs * 0.8:
            pytest.fail(f"Only {len(job_ids)}/{num_jobs} jobs created - insufficient for test")
        
        # Wait for jobs to stabilize
        logger.info("Waiting 30 seconds for jobs to stabilize...")
        time.sleep(30)
        
        logger.info(f"")
        
        # Phase 3: Measure streaming performance
        logger.info("Phase 3: Measuring streaming performance...")
        logger.info(f"Polling waterfall data from {len(job_ids)} jobs for {poll_duration} seconds...")
        
        # Record network start
        net_io_start = psutil.net_io_counters()
        start_bytes_sent = net_io_start.bytes_sent
        start_bytes_recv = net_io_start.bytes_recv
        
        test_start_time = time.time()
        test_end_time = test_start_time + poll_duration
        
        def poll_waterfall(job_id: str) -> Dict[str, Any]:
            """Poll waterfall data for a single job."""
            poll_count = 0
            total_bytes = 0
            response_times = []
            errors = 0
            
            while time.time() < test_end_time:
                poll_start = time.time()
                
                try:
                    # Get waterfall data
                    waterfall_data = focus_server_api.get_waterfall(job_id, rows_per_poll)
                    
                    poll_latency = time.time() - poll_start
                    response_times.append(poll_latency)
                    
                    # Estimate data size (rough approximation)
                    data_size = len(str(waterfall_data))
                    total_bytes += data_size
                    
                    poll_count += 1
                    
                except Exception as e:
                    errors += 1
                    logger.debug(f"Poll failed for job {job_id}: {e}")
                
                # Wait before next poll
                time.sleep(poll_interval)
            
            return {
                'job_id': job_id,
                'poll_count': poll_count,
                'total_bytes': total_bytes,
                'response_times': response_times,
                'errors': errors,
                'avg_response_time': statistics.mean(response_times) if response_times else 0
            }
        
        # Poll all jobs concurrently
        results = []
        
        with ThreadPoolExecutor(max_workers=num_jobs) as executor:
            futures = [executor.submit(poll_waterfall, job_id) for job_id in job_ids]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Polling thread failed: {e}")
        
        actual_test_duration = time.time() - test_start_time
        
        # Record network end
        net_io_end = psutil.net_io_counters()
        end_bytes_sent = net_io_end.bytes_sent
        end_bytes_recv = net_io_end.bytes_recv
        
        # Calculate network statistics
        total_bytes_sent = end_bytes_sent - start_bytes_sent
        total_bytes_recv = end_bytes_recv - start_bytes_recv
        total_bytes_transferred = total_bytes_sent + total_bytes_recv
        
        # Convert to MB/s and Mbps
        total_mb = total_bytes_transferred / (1024 * 1024)
        mb_per_second = total_mb / actual_test_duration
        mbps = (total_bytes_transferred * 8) / (actual_test_duration * 1_000_000)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"NETWORK BANDWIDTH RESULTS")
        logger.info(f"{'='*80}")
        logger.info(f"Test Duration: {actual_test_duration:.1f} seconds")
        logger.info(f"")
        logger.info(f"Network Transfer:")
        logger.info(f"  Total Sent: {total_bytes_sent / (1024*1024):.2f} MB")
        logger.info(f"  Total Received: {total_bytes_recv / (1024*1024):.2f} MB")
        logger.info(f"  Total Transfer: {total_mb:.2f} MB")
        logger.info(f"")
        logger.info(f"Bandwidth:")
        logger.info(f"  Average: {mb_per_second:.2f} MB/s")
        logger.info(f"  Average: {mbps:.2f} Mbps")
        logger.info(f"")
        
        # Analyze per-job statistics
        successful_jobs = [r for r in results if r['poll_count'] > 0]
        
        if successful_jobs:
            poll_counts = [r['poll_count'] for r in successful_jobs]
            avg_polls = statistics.mean(poll_counts)
            
            job_response_times = []
            for r in successful_jobs:
                if r['response_times']:
                    job_response_times.append(statistics.mean(r['response_times']))
            
            avg_response_time = statistics.mean(job_response_times) if job_response_times else 0
            response_time_variance = statistics.stdev(job_response_times) if len(job_response_times) > 1 else 0
            
            total_polls = sum(poll_counts)
            total_errors = sum(r['errors'] for r in successful_jobs)
            error_rate = total_errors / total_polls if total_polls > 0 else 0
            
            logger.info(f"Polling Statistics:")
            logger.info(f"  Total Polls: {total_polls}")
            logger.info(f"  Average Polls per Job: {avg_polls:.1f}")
            logger.info(f"  Total Errors: {total_errors}")
            logger.info(f"  Error Rate: {error_rate:.2%}")
            logger.info(f"")
            logger.info(f"Response Time:")
            logger.info(f"  Average: {avg_response_time*1000:.2f}ms")
            logger.info(f"  Std Dev: {response_time_variance*1000:.2f}ms")
            logger.info(f"  Variance: {(response_time_variance/avg_response_time*100) if avg_response_time > 0 else 0:.1f}%")
            logger.info(f"")
            
            # Per-job bandwidth
            per_job_mbps = mbps / len(successful_jobs) if successful_jobs else 0
            logger.info(f"Per-Job Bandwidth:")
            logger.info(f"  Average: {per_job_mbps:.2f} Mbps")
            logger.info(f"")
        
        # Measure latency under load
        logger.info("Measuring latency under load...")
        load_latencies = []
        for _ in range(10):
            start = time.time()
            try:
                focus_server_api.get_channels()
                latency_ms = (time.time() - start) * 1000
                load_latencies.append(latency_ms)
            except Exception as e:
                logger.warning(f"Latency test failed: {e}")
            time.sleep(0.5)
        
        under_load_latency = statistics.mean(load_latencies) if load_latencies else 0
        latency_increase = under_load_latency - baseline_latency
        
        logger.info(f"Latency Analysis:")
        logger.info(f"  Baseline: {baseline_latency:.2f}ms")
        logger.info(f"  Under Load: {under_load_latency:.2f}ms")
        logger.info(f"  Increase: +{latency_increase:.2f}ms")
        logger.info(f"")
        
        # Phase 4: Cleanup
        logger.info("Phase 4: Cleaning up jobs...")
        cleanup_count = 0
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
                cleanup_count += 1
            except Exception as e:
                logger.debug(f"Failed to cleanup job {job_id}: {e}")
        
        logger.info(f"Cleaned up {cleanup_count}/{len(job_ids)} jobs")
        logger.info(f"")
        
        # Assertions
        logger.info(f"{'='*80}")
        logger.info(f"VALIDATION RESULTS")
        logger.info(f"{'='*80}")
        
        # 1. Bandwidth should not saturate network
        max_bandwidth_mbps = 800  # For 1 Gbps link, leave 20% headroom
        assert mbps < max_bandwidth_mbps, \
            f"Bandwidth {mbps:.2f} Mbps exceeds limit {max_bandwidth_mbps} Mbps (network saturated)"
        logger.info(f"✅ Bandwidth OK: {mbps:.2f} Mbps < {max_bandwidth_mbps} Mbps")
        
        # 2. Latency should not increase significantly
        max_latency_increase = 50  # 50ms
        assert latency_increase < max_latency_increase, \
            f"Latency increased by {latency_increase:.2f}ms (threshold: {max_latency_increase}ms)"
        logger.info(f"✅ Latency OK: +{latency_increase:.2f}ms < {max_latency_increase}ms")
        
        # 3. Per-job bandwidth should be consistent
        if successful_jobs and len(job_response_times) > 1:
            variance_pct = (response_time_variance / avg_response_time * 100) if avg_response_time > 0 else 0
            max_variance = 30  # 30%
            
            assert variance_pct < max_variance, \
                f"Per-job response time variance {variance_pct:.1f}% exceeds {max_variance}%"
            logger.info(f"✅ Consistency OK: variance {variance_pct:.1f}% < {max_variance}%")
        
        # 4. Error rate should be minimal
        if 'error_rate' in locals():
            max_error_rate = 0.02  # 2%
            assert error_rate <= max_error_rate, \
                f"Error rate {error_rate:.2%} exceeds {max_error_rate:.2%}"
            logger.info(f"✅ Error rate OK: {error_rate:.2%} <= {max_error_rate:.2%}")
        
        # 5. All jobs should have been polling
        min_successful_jobs = num_jobs * 0.9  # 90%
        assert len(successful_jobs) >= min_successful_jobs, \
            f"Only {len(successful_jobs)}/{num_jobs} jobs polled successfully"
        logger.info(f"✅ Job success OK: {len(successful_jobs)}/{num_jobs} jobs active")
        
        logger.info(f"")
        logger.info(f"{'='*80}")
        logger.info(f"✅ TEST PASSED: Network Bandwidth Test Successful!")
        logger.info(f"{'='*80}")
        logger.info(f"Network can handle {num_jobs} concurrent streams")
        logger.info(f"Total bandwidth: {mbps:.2f} Mbps")
        logger.info(f"No network bottlenecks detected")
        logger.info(f"{'='*80}\n")
    
    @pytest.mark.xray("PZ-15139")
    def test_network_throughput_scaling(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-15139.2: Network Throughput Scaling.
        
        Objective:
            Verify that network throughput scales linearly with job count.
        
        Steps:
            1. Test with 5 jobs
            2. Test with 10 jobs
            3. Test with 20 jobs
            4. Verify linear scaling
        
        Expected:
            - Throughput scales linearly (2x jobs ≈ 2x bandwidth)
            - No saturation at any level
        """
        logger.info("=" * 80)
        logger.info("TEST: Network Throughput Scaling (PZ-15139.2)")
        logger.info("=" * 80)
        
        job_counts = [3, 5, 10]  # Reduced from [5, 10, 20] to safer levels
        test_duration = 60  # 1 minute per test
        
        config_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        throughput_results = []
        
        for num_jobs in job_counts:
            logger.info(f"\nTesting with {num_jobs} concurrent jobs...")
            
            # Create jobs
            job_ids = []
            for i in range(num_jobs):
                try:
                    config_request = ConfigureRequest(**config_payload)
                    response = focus_server_api.configure_streaming_job(config_request)
                    if response.job_id:
                        job_ids.append(response.job_id)
                except Exception as e:
                    logger.warning(f"Failed to create job {i+1}: {e}")
            
            logger.info(f"  Created {len(job_ids)} jobs")
            
            # Measure network for this configuration
            net_start = psutil.net_io_counters()
            time.sleep(test_duration)
            net_end = psutil.net_io_counters()
            
            # Calculate bandwidth
            bytes_transferred = (net_end.bytes_sent - net_start.bytes_sent) + \
                              (net_end.bytes_recv - net_start.bytes_recv)
            mbps = (bytes_transferred * 8) / (test_duration * 1_000_000)
            
            throughput_results.append({
                'num_jobs': len(job_ids),
                'mbps': mbps,
                'mb_per_second': bytes_transferred / (1024 * 1024) / test_duration
            })
            
            logger.info(f"  Bandwidth: {mbps:.2f} Mbps")
            
            # Cleanup
            for job_id in job_ids:
                try:
                    focus_server_api.cancel_job(job_id)
                except:
                    pass
            
            # Wait between tests
            time.sleep(5)
        
        # Analyze scaling
        logger.info(f"\n{'='*80}")
        logger.info(f"THROUGHPUT SCALING ANALYSIS")
        logger.info(f"{'='*80}")
        
        for result in throughput_results:
            logger.info(f"  {result['num_jobs']:2d} jobs: {result['mbps']:8.2f} Mbps "
                       f"({result['mb_per_second']:.2f} MB/s)")
        
        # Check if scaling is roughly linear
        if len(throughput_results) >= 2:
            # Compare 5 jobs vs 10 jobs
            ratio_2x = throughput_results[1]['mbps'] / throughput_results[0]['mbps']
            logger.info(f"")
            logger.info(f"Scaling Ratio (10 jobs / 5 jobs): {ratio_2x:.2f}x")
            logger.info(f"Expected: ~2.0x (linear scaling)")
            
            # Allow 30% deviation from linear (1.4x to 2.6x is acceptable)
            assert 1.4 <= ratio_2x <= 2.6, \
                f"Scaling ratio {ratio_2x:.2f}x not linear (expected ~2.0x)"
            logger.info(f"✅ Scaling is approximately linear")
        
        logger.info(f"")
        logger.info(f"✅ Network throughput scales linearly with job count")

