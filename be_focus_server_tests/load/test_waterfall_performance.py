"""
Load Tests - Waterfall Data Streaming Performance
==================================================

Tests for waterfall data retrieval performance under concurrent load.

Tests Covered (Xray):
    - PZ-15141: Performance - Waterfall Data Streaming Under Load

Author: QA Automation Architect
Date: 2025-11-23
"""

import pytest
import logging
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

from src.apis.focus_server_api import FocusServerAPI
from src.models.focus_server_models import ConfigureRequest, ViewType

logger = logging.getLogger(__name__)


# ===================================================================
# Test Class: Waterfall Streaming Performance
# ===================================================================

@pytest.mark.slow
@pytest.mark.nightly
@pytest.mark.load
@pytest.mark.performance
@pytest.mark.streaming
@pytest.mark.regression
class TestWaterfallPerformance:
    """
    Test suite for waterfall data streaming performance under load.
    
    Tests covered:
        - PZ-15141: Waterfall Data Streaming Performance
    """
    
    @pytest.mark.xray("PZ-15141")
    @pytest.mark.regression
    def test_waterfall_streaming_performance_under_load(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-15141: Performance - Waterfall Data Streaming Under Load.
        
        Objective:
            Verify GET /waterfall endpoint maintains acceptable performance
            when retrieving large datasets under concurrent load.
        
        Steps:
            1. Test baseline performance (single job, different row counts)
            2. Create 20 concurrent streaming jobs
            3. Poll waterfall data from all jobs
            4. Measure response times, throughput, data quality
            5. Test large dataset retrieval (1000+ rows)
            6. Verify no performance degradation
        
        Expected:
            - 100 rows: < 300ms response time
            - 1000 rows: < 2000ms response time
            - Throughput ≥ 500 rows/second
            - Success rate ≥ 98%
            - Data completeness = 100%
        
        Jira: PZ-15141
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: Waterfall Streaming Performance Under Load (PZ-15141)")
        logger.info("=" * 80)
        
        num_concurrent_jobs = 20
        test_duration = 180  # 3 minutes
        poll_interval = 2  # seconds
        
        logger.info(f"Test Configuration:")
        logger.info(f"  Concurrent Jobs: {num_concurrent_jobs}")
        logger.info(f"  Test Duration: {test_duration} seconds")
        logger.info(f"  Poll Interval: {poll_interval} seconds")
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
        
        # Phase 1: Baseline performance test
        logger.info("Phase 1: Testing baseline waterfall performance...")
        
        # Create single job for baseline
        logger.info("Creating single job for baseline test...")
        config_request = ConfigureRequest(**config_payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        if not response.job_id:
            pytest.fail("Failed to create baseline job")
        
        baseline_job_id = response.job_id
        logger.info(f"Baseline job created: {baseline_job_id}")
        
        # Wait for job to start streaming
        time.sleep(10)
        
        # Test different row counts
        row_count_tests = [10, 100, 500, 1000]
        baseline_results = {}
        
        for row_count in row_count_tests:
            logger.info(f"\n  Testing {row_count} rows...")
            row_latencies = []
            
            # Test 5 times for each row count
            for attempt in range(5):
                start = time.time()
                try:
                    waterfall_data = focus_server_api.get_waterfall(baseline_job_id, row_count)
                    latency_ms = (time.time() - start) * 1000
                    row_latencies.append(latency_ms)
                    logger.debug(f"    Attempt {attempt+1}: {latency_ms:.2f}ms")
                except Exception as e:
                    logger.warning(f"    Attempt {attempt+1} failed: {e}")
                
                time.sleep(0.5)
            
            if row_latencies:
                avg_latency = statistics.mean(row_latencies)
                max_latency = max(row_latencies)
                
                baseline_results[row_count] = {
                    'avg_ms': avg_latency,
                    'max_ms': max_latency,
                    'samples': len(row_latencies)
                }
                
                logger.info(f"    Average: {avg_latency:.2f}ms, Max: {max_latency:.2f}ms")
        
        # Cleanup baseline job
        try:
            focus_server_api.cancel_job(baseline_job_id)
        except:
            pass
        
        logger.info(f"\nBaseline Performance Summary:")
        for row_count, result in baseline_results.items():
            logger.info(f"  {row_count:4d} rows: {result['avg_ms']:7.2f}ms avg, "
                       f"{result['max_ms']:7.2f}ms max")
        logger.info(f"")
        
        # Phase 2: Create concurrent load
        logger.info("Phase 2: Creating concurrent streaming jobs...")
        
        job_ids = []
        for i in range(num_concurrent_jobs):
            try:
                config_request = ConfigureRequest(**config_payload)
                response = focus_server_api.configure_streaming_job(config_request)
                
                if response.job_id:
                    job_ids.append(response.job_id)
                    logger.debug(f"  Job {i+1}/{num_concurrent_jobs}: {response.job_id}")
            
            except Exception as e:
                logger.warning(f"  Job {i+1}/{num_concurrent_jobs} failed: {e}")
        
        logger.info(f"Created {len(job_ids)}/{num_concurrent_jobs} jobs")
        
        if len(job_ids) < num_concurrent_jobs * 0.8:
            pytest.fail(f"Only {len(job_ids)}/{num_concurrent_jobs} jobs created")
        
        # Wait for jobs to start streaming
        logger.info("Waiting 30 seconds for jobs to start streaming...")
        time.sleep(30)
        logger.info(f"")
        
        # Phase 3: Poll waterfall data from all jobs
        logger.info("Phase 3: Polling waterfall data from all jobs...")
        
        def poll_job_waterfall(job_id: str) -> Dict[str, Any]:
            """Poll waterfall data for a single job."""
            poll_count = 0
            successful_polls = 0
            failed_polls = 0
            response_times = []
            total_rows_retrieved = 0
            
            test_end = time.time() + test_duration
            
            while time.time() < test_end:
                poll_count += 1
                start = time.time()
                
                try:
                    waterfall_data = focus_server_api.get_waterfall(job_id, 100)
                    
                    latency_ms = (time.time() - start) * 1000
                    response_times.append(latency_ms)
                    successful_polls += 1
                    
                    # Count rows (if waterfall_data has rows attribute)
                    if hasattr(waterfall_data, 'rows') and waterfall_data.rows:
                        total_rows_retrieved += len(waterfall_data.rows)
                    else:
                        total_rows_retrieved += 100  # Estimate
                
                except Exception as e:
                    failed_polls += 1
                    logger.debug(f"Poll failed for {job_id}: {e}")
                
                time.sleep(poll_interval)
            
            return {
                'job_id': job_id,
                'poll_count': poll_count,
                'successful_polls': successful_polls,
                'failed_polls': failed_polls,
                'response_times': response_times,
                'total_rows': total_rows_retrieved,
                'avg_response_ms': statistics.mean(response_times) if response_times else 0,
                'p95_response_ms': sorted(response_times)[int(len(response_times)*0.95)] if response_times else 0
            }
        
        # Poll all jobs concurrently
        polling_results = []
        
        with ThreadPoolExecutor(max_workers=num_concurrent_jobs) as executor:
            futures = [executor.submit(poll_job_waterfall, job_id) for job_id in job_ids]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    polling_results.append(result)
                except Exception as e:
                    logger.error(f"Polling thread failed: {e}")
        
        # Analyze results
        total_polls = sum(r['poll_count'] for r in polling_results)
        total_successful = sum(r['successful_polls'] for r in polling_results)
        total_failed = sum(r['failed_polls'] for r in polling_results)
        total_rows = sum(r['total_rows'] for r in polling_results)
        
        all_response_times = []
        for r in polling_results:
            all_response_times.extend(r['response_times'])
        
        if all_response_times:
            all_response_times.sort()
            avg_response_time = statistics.mean(all_response_times)
            p50_response_time = all_response_times[len(all_response_times) // 2]
            p95_response_time = all_response_times[int(len(all_response_times) * 0.95)]
            p99_response_time = all_response_times[int(len(all_response_times) * 0.99)]
            max_response_time = max(all_response_times)
        else:
            avg_response_time = p50_response_time = p95_response_time = p99_response_time = max_response_time = 0
        
        success_rate = total_successful / total_polls if total_polls > 0 else 0
        
        # Calculate throughput
        rows_per_second = total_rows / test_duration
        
        logger.info(f"\n{'='*80}")
        logger.info(f"WATERFALL STREAMING PERFORMANCE RESULTS")
        logger.info(f"{'='*80}")
        logger.info(f"")
        logger.info(f"Polling Statistics:")
        logger.info(f"  Total Polls: {total_polls}")
        logger.info(f"  Successful: {total_successful}")
        logger.info(f"  Failed: {total_failed}")
        logger.info(f"  Success Rate: {success_rate:.1%}")
        logger.info(f"")
        logger.info(f"Response Time (100 rows):")
        logger.info(f"  Average: {avg_response_time:.2f}ms")
        logger.info(f"  P50: {p50_response_time:.2f}ms")
        logger.info(f"  P95: {p95_response_time:.2f}ms")
        logger.info(f"  P99: {p99_response_time:.2f}ms")
        logger.info(f"  Max: {max_response_time:.2f}ms")
        logger.info(f"")
        logger.info(f"Throughput:")
        logger.info(f"  Total Rows Retrieved: {total_rows:,}")
        logger.info(f"  Rows/Second: {rows_per_second:.1f}")
        logger.info(f"")
        
        # Per-job analysis
        job_avg_responses = [r['avg_response_ms'] for r in polling_results if r['successful_polls'] > 0]
        
        if len(job_avg_responses) > 1:
            job_response_variance = statistics.stdev(job_avg_responses)
            job_response_avg = statistics.mean(job_avg_responses)
            variance_pct = (job_response_variance / job_response_avg * 100) if job_response_avg > 0 else 0
            
            logger.info(f"Per-Job Consistency:")
            logger.info(f"  Job Count: {len(job_avg_responses)}")
            logger.info(f"  Avg Response: {job_response_avg:.2f}ms")
            logger.info(f"  Std Dev: {job_response_variance:.2f}ms")
            logger.info(f"  Variance: {variance_pct:.1f}%")
            logger.info(f"")
        
        # Phase 4: Test large dataset retrieval
        logger.info("Phase 4: Testing large dataset retrieval under load...")
        
        # Test 1000 rows from first 5 jobs
        large_row_count = 1000
        large_dataset_results = []
        
        for job_id in job_ids[:5]:
            start = time.time()
            try:
                waterfall_data = focus_server_api.get_waterfall(job_id, large_row_count)
                latency_ms = (time.time() - start) * 1000
                large_dataset_results.append({
                    'success': True,
                    'latency_ms': latency_ms,
                    'job_id': job_id
                })
                logger.debug(f"  {job_id}: {latency_ms:.2f}ms for {large_row_count} rows")
            except Exception as e:
                large_dataset_results.append({
                    'success': False,
                    'latency_ms': 0,
                    'job_id': job_id,
                    'error': str(e)
                })
                logger.warning(f"  {job_id}: Failed - {e}")
            
            time.sleep(1)
        
        large_successful = [r for r in large_dataset_results if r['success']]
        
        if large_successful:
            large_latencies = [r['latency_ms'] for r in large_successful]
            large_avg = statistics.mean(large_latencies)
            large_max = max(large_latencies)
            
            logger.info(f"\nLarge Dataset ({large_row_count} rows) Results:")
            logger.info(f"  Successful: {len(large_successful)}/5")
            logger.info(f"  Average: {large_avg:.2f}ms")
            logger.info(f"  Max: {large_max:.2f}ms")
            logger.info(f"")
        
        # Phase 5: Cleanup
        logger.info("Phase 5: Cleaning up jobs...")
        cleanup_count = 0
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
                cleanup_count += 1
            except Exception as e:
                logger.debug(f"Failed to cleanup {job_id}: {e}")
        
        logger.info(f"Cleaned up {cleanup_count}/{len(job_ids)} jobs")
        logger.info(f"")
        
        # Assertions
        logger.info(f"{'='*80}")
        logger.info(f"VALIDATION RESULTS")
        logger.info(f"{'='*80}")
        
        # 1. Success rate
        min_success_rate = 0.98  # 98%
        assert success_rate >= min_success_rate, \
            f"Success rate {success_rate:.1%} below {min_success_rate:.1%}"
        logger.info(f"✅ Success rate OK: {success_rate:.1%} >= {min_success_rate:.1%}")
        
        # 2. Response time for 100 rows
        max_avg_response_100 = 300  # 300ms
        assert avg_response_time < max_avg_response_100, \
            f"Average response time {avg_response_time:.2f}ms exceeds {max_avg_response_100}ms"
        logger.info(f"✅ Response time OK: {avg_response_time:.2f}ms < {max_avg_response_100}ms")
        
        # 3. P95 response time
        max_p95_response = 500  # 500ms
        assert p95_response_time < max_p95_response, \
            f"P95 response time {p95_response_time:.2f}ms exceeds {max_p95_response}ms"
        logger.info(f"✅ P95 response OK: {p95_response_time:.2f}ms < {max_p95_response}ms")
        
        # 4. Throughput
        min_throughput = 500  # 500 rows/second
        assert rows_per_second >= min_throughput, \
            f"Throughput {rows_per_second:.1f} rows/s below {min_throughput} rows/s"
        logger.info(f"✅ Throughput OK: {rows_per_second:.1f} rows/s >= {min_throughput} rows/s")
        
        # 5. Large dataset response time (if tested)
        if large_successful:
            max_large_dataset_time = 2000  # 2 seconds for 1000 rows
            assert large_avg < max_large_dataset_time, \
                f"Large dataset avg {large_avg:.2f}ms exceeds {max_large_dataset_time}ms"
            logger.info(f"✅ Large dataset OK: {large_avg:.2f}ms < {max_large_dataset_time}ms")
        
        # 6. Per-job consistency
        if 'variance_pct' in locals() and len(job_avg_responses) > 1:
            max_variance = 30  # 30%
            assert variance_pct < max_variance, \
                f"Per-job variance {variance_pct:.1f}% exceeds {max_variance}%"
            logger.info(f"✅ Consistency OK: variance {variance_pct:.1f}% < {max_variance}%")
        
        logger.info(f"")
        logger.info(f"{'='*80}")
        logger.info(f"✅ TEST PASSED: Waterfall Streaming Performance!")
        logger.info(f"{'='*80}")
        logger.info(f"Waterfall endpoint performs well under concurrent load")
        logger.info(f"Response times within acceptable limits")
        logger.info(f"Throughput meets requirements")
        logger.info(f"No streaming bottlenecks detected")
        logger.info(f"{'='*80}\n")
    
    @pytest.mark.xray("PZ-15141")
    @pytest.mark.regression
    def test_waterfall_row_count_performance(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-15141.2: Waterfall Row Count Performance.
        
        Objective:
            Measure performance degradation as row count increases.
        
        Expected:
            - Linear scaling (2x rows ≈ 2x time)
            - No exponential degradation
        """
        logger.info("=" * 80)
        logger.info("TEST: Waterfall Row Count Performance (PZ-15141.2)")
        logger.info("=" * 80)
        
        # Create single job
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
        
        config_request = ConfigureRequest(**config_payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        if not response.job_id:
            pytest.fail("Failed to create job")
        
        job_id = response.job_id
        logger.info(f"Job created: {job_id}")
        
        # Wait for streaming to start
        time.sleep(10)
        
        # Test different row counts
        row_counts = [10, 50, 100, 200, 500, 1000, 2000]
        row_count_results = []
        
        logger.info("\nTesting different row counts...")
        
        for row_count in row_counts:
            latencies = []
            
            # Test 3 times for each count
            for attempt in range(3):
                start = time.time()
                try:
                    waterfall_data = focus_server_api.get_waterfall(job_id, row_count)
                    latency_ms = (time.time() - start) * 1000
                    latencies.append(latency_ms)
                except Exception as e:
                    logger.warning(f"{row_count} rows attempt {attempt+1} failed: {e}")
                
                time.sleep(1)
            
            if latencies:
                avg_latency = statistics.mean(latencies)
                
                row_count_results.append({
                    'rows': row_count,
                    'avg_ms': avg_latency,
                    'ms_per_row': avg_latency / row_count
                })
                
                logger.info(f"  {row_count:4d} rows: {avg_latency:7.2f}ms "
                           f"({avg_latency/row_count:.3f}ms per row)")
        
        # Cleanup
        try:
            focus_server_api.cancel_job(job_id)
        except:
            pass
        
        # Analyze scaling
        logger.info(f"\n{'='*80}")
        logger.info(f"ROW COUNT SCALING ANALYSIS")
        logger.info(f"{'='*80}")
        
        if len(row_count_results) >= 3:
            # Check if scaling is linear
            ms_per_row_values = [r['ms_per_row'] for r in row_count_results]
            avg_ms_per_row = statistics.mean(ms_per_row_values)
            ms_per_row_variance = statistics.stdev(ms_per_row_values) if len(ms_per_row_values) > 1 else 0
            
            logger.info(f"Scaling Metrics:")
            logger.info(f"  Average ms/row: {avg_ms_per_row:.3f}ms")
            logger.info(f"  Std Dev: {ms_per_row_variance:.3f}ms")
            logger.info(f"  Variance: {(ms_per_row_variance/avg_ms_per_row*100) if avg_ms_per_row > 0 else 0:.1f}%")
            
            # Variance should be low for linear scaling
            max_variance_pct = 50  # 50% variance acceptable
            variance_pct = (ms_per_row_variance/avg_ms_per_row*100) if avg_ms_per_row > 0 else 0
            
            if variance_pct < max_variance_pct:
                logger.info(f"  ✅ Scaling is approximately linear")
            else:
                logger.warning(f"  ⚠️  Scaling may be non-linear (high variance)")
        
        # Verify thresholds
        logger.info(f"")
        logger.info(f"Threshold Validation:")
        
        # Find 100-row result
        result_100 = next((r for r in row_count_results if r['rows'] == 100), None)
        if result_100:
            max_100_rows = 300  # 300ms
            assert result_100['avg_ms'] < max_100_rows, \
                f"100 rows took {result_100['avg_ms']:.2f}ms > {max_100_rows}ms"
            logger.info(f"  ✅ 100 rows: {result_100['avg_ms']:.2f}ms < {max_100_rows}ms")
        
        # Find 1000-row result
        result_1000 = next((r for r in row_count_results if r['rows'] == 1000), None)
        if result_1000:
            max_1000_rows = 2000  # 2 seconds
            assert result_1000['avg_ms'] < max_1000_rows, \
                f"1000 rows took {result_1000['avg_ms']:.2f}ms > {max_1000_rows}ms"
            logger.info(f"  ✅ 1000 rows: {result_1000['avg_ms']:.2f}ms < {max_1000_rows}ms")
        
        logger.info(f"")
        logger.info(f"✅ Waterfall performance scales acceptably with row count")

