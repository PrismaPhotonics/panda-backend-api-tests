"""
Load Tests - Soak Test for Memory Leak Detection
=================================================

24-hour soak test to detect memory leaks and resource degradation.

Tests Covered (Xray):
    - PZ-15138: Load - Soak Test - 24 Hour Memory Leak Detection

Author: QA Automation Architect
Date: 2025-11-23
"""

import pytest
import logging
import time
import psutil
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.apis.focus_server_api import FocusServerAPI
from src.models.focus_server_models import ConfigureRequest, ViewType

logger = logging.getLogger(__name__)


# ===================================================================
# Test Class: Soak Test - Memory Leak Detection
# ===================================================================

@pytest.mark.slow
@pytest.mark.nightly
@pytest.mark.load
@pytest.mark.soak
@pytest.mark.regression
@pytest.mark.skip(reason="24-hour test - run manually weekly with: pytest -v --no-skip")
class TestSoakMemoryLeak:
    """
    Test suite for 24-hour soak testing and memory leak detection.
    
    Tests covered:
        - PZ-15138: 24-Hour Soak Test
    """
    
    @pytest.mark.xray("PZ-15138")
    @pytest.mark.regression
    def test_memory_leak_soak_24_hours(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-15138: Load - Soak Test - 24 Hour Memory Leak Detection.
        
        Objective:
            Verify system can run continuously for 24 hours without:
            - Memory leaks
            - Performance degradation
            - Resource exhaustion
            - Crashes or failures
        
        Steps:
            1. Record baseline metrics
            2. Run continuous job creation for 24 hours
            3. Create 5 jobs every 5 minutes
            4. Monitor memory, CPU, success rate
            5. Log hourly summaries
            6. Analyze trends and detect leaks
        
        Expected:
            - Memory growth < 15% over 24 hours
            - No memory leak detected (< 50 MB/hour)
            - CPU stable (no upward trend)
            - Success rate ≥ 95% throughout
            - Response time stable (< 20% increase)
            - No crashes or OOM kills
        
        Jira: PZ-15138
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: 24-Hour Soak Test - Memory Leak Detection (PZ-15138)")
        logger.info("=" * 80)
        logger.warning("⚠️  This test will run for 24 HOURS!")
        logger.warning("⚠️  Do not interrupt unless absolutely necessary")
        logger.info("=" * 80)
        
        # Configuration
        duration_hours = 24
        jobs_per_interval = 5
        interval_minutes = 5
        
        # Calculate total iterations
        iterations_per_hour = 60 // interval_minutes  # 12
        total_iterations = duration_hours * iterations_per_hour  # 288
        
        logger.info(f"Test Configuration:")
        logger.info(f"  Duration: {duration_hours} hours")
        logger.info(f"  Jobs per interval: {jobs_per_interval}")
        logger.info(f"  Interval: {interval_minutes} minutes")
        logger.info(f"  Total iterations: {total_iterations}")
        logger.info(f"  Total jobs: ~{total_iterations * jobs_per_interval}")
        
        # Standard configuration payload
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
        
        # Record baseline metrics
        logger.info("\nRecording baseline metrics...")
        process = psutil.Process()
        
        memory_baseline = psutil.virtual_memory().percent
        memory_baseline_mb = process.memory_info().rss / 1024 / 1024
        cpu_baseline = psutil.cpu_percent(interval=1)
        
        logger.info(f"Baseline Metrics:")
        logger.info(f"  System Memory: {memory_baseline:.1f}%")
        logger.info(f"  Process Memory: {memory_baseline_mb:.1f} MB")
        logger.info(f"  CPU: {cpu_baseline:.1f}%")
        
        # Initialize tracking
        memory_samples = [memory_baseline]
        cpu_samples = [cpu_baseline]
        process_memory_samples = [memory_baseline_mb]
        success_counts = []
        failure_counts = []
        response_times = []
        hourly_reports = []
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        iteration = 0
        total_jobs_created = 0
        total_jobs_failed = 0
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 Starting 24-hour soak test at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   Expected completion: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*80}\n")
        
        # Main soak test loop
        while datetime.now() < end_time:
            iteration += 1
            iteration_start = time.time()
            
            hours_elapsed = (datetime.now() - start_time).total_seconds() / 3600
            
            logger.info(f"\n--- Iteration {iteration}/{total_iterations} "
                       f"(Hour {hours_elapsed:.1f}/{duration_hours}) ---")
            
            # Create jobs for this interval
            interval_success = 0
            interval_failure = 0
            interval_response_times = []
            job_ids_to_cleanup = []
            
            for job_num in range(jobs_per_interval):
                job_start = time.time()
                
                try:
                    config_request = ConfigureRequest(**config_payload)
                    response = focus_server_api.configure_streaming_job(config_request)
                    
                    job_elapsed = time.time() - job_start
                    interval_response_times.append(job_elapsed)
                    
                    if response.job_id:
                        interval_success += 1
                        total_jobs_created += 1
                        job_ids_to_cleanup.append(response.job_id)
                        logger.debug(f"  Job {job_num+1}/{jobs_per_interval}: "
                                   f"Success ({job_elapsed:.3f}s) - {response.job_id}")
                    else:
                        interval_failure += 1
                        total_jobs_failed += 1
                        logger.warning(f"  Job {job_num+1}/{jobs_per_interval}: "
                                     f"No job_id returned")
                
                except Exception as e:
                    job_elapsed = time.time() - job_start
                    interval_failure += 1
                    total_jobs_failed += 1
                    logger.error(f"  Job {job_num+1}/{jobs_per_interval}: "
                               f"Failed ({job_elapsed:.3f}s) - {e}")
            
            # Cleanup jobs immediately to avoid resource buildup
            for job_id in job_ids_to_cleanup:
                try:
                    focus_server_api.cancel_job(job_id)
                except Exception:
                    pass  # Continue even if cleanup fails
            
            # Record results
            success_counts.append(interval_success)
            failure_counts.append(interval_failure)
            if interval_response_times:
                response_times.extend(interval_response_times)
            
            # Sample system metrics
            current_memory = psutil.virtual_memory().percent
            current_cpu = psutil.cpu_percent(interval=1)
            current_process_memory = process.memory_info().rss / 1024 / 1024
            
            memory_samples.append(current_memory)
            cpu_samples.append(current_cpu)
            process_memory_samples.append(current_process_memory)
            
            # Calculate current stats
            memory_growth = current_memory - memory_baseline
            process_memory_growth = current_process_memory - memory_baseline_mb
            avg_response_time = statistics.mean(interval_response_times) if interval_response_times else 0
            
            logger.info(f"Iteration Results:")
            logger.info(f"  Success: {interval_success}/{jobs_per_interval}")
            logger.info(f"  Memory: {current_memory:.1f}% (+{memory_growth:.1f}%)")
            logger.info(f"  Process Memory: {current_process_memory:.1f} MB (+{process_memory_growth:.1f} MB)")
            logger.info(f"  CPU: {current_cpu:.1f}%")
            logger.info(f"  Avg Response: {avg_response_time:.3f}s")
            
            # Hourly reporting
            if iteration % iterations_per_hour == 0:
                hours_completed = iteration // iterations_per_hour
                
                # Calculate hourly stats
                hour_start_idx = (hours_completed - 1) * iterations_per_hour
                hour_success = sum(success_counts[hour_start_idx:iteration])
                hour_failure = sum(failure_counts[hour_start_idx:iteration])
                hour_total = hour_success + hour_failure
                hour_success_rate = hour_success / hour_total if hour_total > 0 else 0
                
                hour_memory_growth = memory_samples[-1] - memory_samples[hour_start_idx]
                hour_cpu_avg = statistics.mean(cpu_samples[hour_start_idx:iteration])
                
                hourly_report = {
                    'hour': hours_completed,
                    'success_rate': hour_success_rate,
                    'memory_growth_pct': memory_growth,
                    'memory_growth_mb': process_memory_growth,
                    'cpu_avg': hour_cpu_avg,
                    'total_jobs_created': total_jobs_created,
                    'total_jobs_failed': total_jobs_failed
                }
                hourly_reports.append(hourly_report)
                
                logger.info(f"\n{'='*80}")
                logger.info(f"📊 HOURLY REPORT - Hour {hours_completed}/{duration_hours}")
                logger.info(f"{'='*80}")
                logger.info(f"Time Elapsed: {hours_completed} hours")
                logger.info(f"Progress: {(hours_completed/duration_hours)*100:.1f}%")
                logger.info(f"")
                logger.info(f"Hour {hours_completed} Stats:")
                logger.info(f"  Success Rate: {hour_success_rate:.1%} ({hour_success}/{hour_total})")
                logger.info(f"")
                logger.info(f"Cumulative Stats:")
                logger.info(f"  Total Jobs Created: {total_jobs_created}")
                logger.info(f"  Total Jobs Failed: {total_jobs_failed}")
                logger.info(f"  Overall Success Rate: {total_jobs_created/(total_jobs_created+total_jobs_failed):.1%}")
                logger.info(f"")
                logger.info(f"System Metrics:")
                logger.info(f"  Memory: {current_memory:.1f}% (baseline: {memory_baseline:.1f}%)")
                logger.info(f"  Memory Growth: +{memory_growth:.1f}%")
                logger.info(f"  Process Memory: {current_process_memory:.1f} MB")
                logger.info(f"  Process Growth: +{process_memory_growth:.1f} MB")
                logger.info(f"  CPU Average (last hour): {hour_cpu_avg:.1f}%")
                logger.info(f"")
                
                # Memory leak detection
                memory_growth_rate_mb_per_hour = process_memory_growth / hours_completed
                logger.info(f"Memory Leak Analysis:")
                logger.info(f"  Growth Rate: {memory_growth_rate_mb_per_hour:.2f} MB/hour")
                
                if memory_growth_rate_mb_per_hour > 100:
                    logger.error(f"  ❌ CRITICAL: Severe memory leak detected!")
                    logger.error(f"     Projected 24h growth: {memory_growth_rate_mb_per_hour * 24:.0f} MB")
                elif memory_growth_rate_mb_per_hour > 50:
                    logger.warning(f"  ⚠️  WARNING: Possible memory leak detected")
                    logger.warning(f"     Projected 24h growth: {memory_growth_rate_mb_per_hour * 24:.0f} MB")
                else:
                    logger.info(f"  ✅ OK: Memory growth within acceptable range")
                    logger.info(f"     Projected 24h growth: {memory_growth_rate_mb_per_hour * 24:.0f} MB")
                
                logger.info(f"{'='*80}\n")
            
            # Calculate sleep time to maintain interval
            iteration_elapsed = time.time() - iteration_start
            sleep_time = (interval_minutes * 60) - iteration_elapsed
            
            if sleep_time > 0:
                next_iteration = datetime.now() + timedelta(seconds=sleep_time)
                logger.debug(f"Next iteration at: {next_iteration.strftime('%H:%M:%S')} "
                           f"(sleeping {sleep_time:.1f}s)")
                time.sleep(sleep_time)
            else:
                logger.warning(f"⚠️  Iteration took longer than interval! "
                             f"({iteration_elapsed:.1f}s > {interval_minutes*60}s)")
        
        # Final analysis
        total_duration = (datetime.now() - start_time).total_seconds() / 3600
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🎉 24-HOUR SOAK TEST COMPLETED!")
        logger.info(f"{'='*80}")
        logger.info(f"Test Duration: {total_duration:.2f} hours")
        logger.info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"")
        
        # Job statistics
        total_jobs = total_jobs_created + total_jobs_failed
        overall_success_rate = total_jobs_created / total_jobs if total_jobs > 0 else 0
        
        logger.info(f"Job Statistics:")
        logger.info(f"  Total Jobs Attempted: {total_jobs}")
        logger.info(f"  Successful: {total_jobs_created}")
        logger.info(f"  Failed: {total_jobs_failed}")
        logger.info(f"  Success Rate: {overall_success_rate:.1%}")
        logger.info(f"")
        
        # Memory analysis
        memory_final = memory_samples[-1]
        memory_total_growth = memory_final - memory_baseline
        process_memory_final = process_memory_samples[-1]
        process_memory_total_growth = process_memory_final - memory_baseline_mb
        
        memory_leak_rate = process_memory_total_growth / total_duration
        
        logger.info(f"Memory Analysis:")
        logger.info(f"  Baseline: {memory_baseline:.1f}% ({memory_baseline_mb:.1f} MB)")
        logger.info(f"  Final: {memory_final:.1f}% ({process_memory_final:.1f} MB)")
        logger.info(f"  Growth: +{memory_total_growth:.1f}% (+{process_memory_total_growth:.1f} MB)")
        logger.info(f"  Growth Rate: {memory_leak_rate:.2f} MB/hour")
        logger.info(f"")
        
        # CPU analysis
        cpu_avg = statistics.mean(cpu_samples)
        cpu_max = max(cpu_samples)
        cpu_min = min(cpu_samples)
        cpu_stdev = statistics.stdev(cpu_samples) if len(cpu_samples) > 1 else 0
        
        logger.info(f"CPU Analysis:")
        logger.info(f"  Average: {cpu_avg:.1f}%")
        logger.info(f"  Min: {cpu_min:.1f}%")
        logger.info(f"  Max: {cpu_max:.1f}%")
        logger.info(f"  Std Dev: {cpu_stdev:.1f}%")
        logger.info(f"")
        
        # Response time analysis
        if response_times:
            response_avg = statistics.mean(response_times)
            response_p95 = sorted(response_times)[int(len(response_times) * 0.95)]
            response_max = max(response_times)
            
            logger.info(f"Response Time Analysis:")
            logger.info(f"  Average: {response_avg:.3f}s")
            logger.info(f"  P95: {response_p95:.3f}s")
            logger.info(f"  Max: {response_max:.3f}s")
            logger.info(f"")
        
        # Success rate trend analysis
        if len(success_counts) >= iterations_per_hour * 2:  # At least 2 hours
            first_hour_success = sum(success_counts[:iterations_per_hour])
            first_hour_total = jobs_per_interval * iterations_per_hour
            first_hour_rate = first_hour_success / first_hour_total
            
            last_hour_success = sum(success_counts[-iterations_per_hour:])
            last_hour_total = jobs_per_interval * iterations_per_hour
            last_hour_rate = last_hour_success / last_hour_total
            
            success_rate_change = last_hour_rate - first_hour_rate
            
            logger.info(f"Success Rate Trend:")
            logger.info(f"  First Hour: {first_hour_rate:.1%}")
            logger.info(f"  Last Hour: {last_hour_rate:.1%}")
            logger.info(f"  Change: {success_rate_change:+.1%}")
            
            if success_rate_change < -0.05:  # Dropped more than 5%
                logger.warning(f"  ⚠️  Success rate degraded over time!")
            else:
                logger.info(f"  ✅ Success rate remained stable")
            logger.info(f"")
        
        # Memory leak detection
        logger.info(f"{'='*80}")
        logger.info(f"🔍 MEMORY LEAK DETECTION RESULTS")
        logger.info(f"{'='*80}")
        
        memory_leak_detected = False
        
        if memory_total_growth >= 20:
            logger.error(f"❌ SEVERE MEMORY LEAK DETECTED!")
            logger.error(f"   System memory grew by {memory_total_growth:.1f}%")
            memory_leak_detected = True
        elif memory_total_growth >= 15:
            logger.warning(f"⚠️  MEMORY LEAK WARNING!")
            logger.warning(f"   System memory grew by {memory_total_growth:.1f}%")
            memory_leak_detected = True
        else:
            logger.info(f"✅ NO MEMORY LEAK: Growth of {memory_total_growth:.1f}% is acceptable")
        
        if memory_leak_rate >= 100:
            logger.error(f"❌ SEVERE MEMORY LEAK: {memory_leak_rate:.2f} MB/hour")
            memory_leak_detected = True
        elif memory_leak_rate >= 50:
            logger.warning(f"⚠️  POSSIBLE MEMORY LEAK: {memory_leak_rate:.2f} MB/hour")
            memory_leak_detected = True
        else:
            logger.info(f"✅ Memory leak rate OK: {memory_leak_rate:.2f} MB/hour")
        
        logger.info(f"{'='*80}\n")
        
        # Assertions
        logger.info(f"Validating Results Against Thresholds...")
        logger.info(f"")
        
        # 1. Success rate
        assert overall_success_rate >= 0.95, \
            f"Success rate {overall_success_rate:.1%} below 95% threshold"
        logger.info(f"✅ Success rate OK: {overall_success_rate:.1%} >= 95%")
        
        # 2. Memory growth
        assert memory_total_growth < 15, \
            f"Memory growth {memory_total_growth:.1f}% exceeds 15% threshold"
        logger.info(f"✅ Memory growth OK: {memory_total_growth:.1f}% < 15%")
        
        # 3. Memory leak rate
        assert memory_leak_rate < 50, \
            f"Memory leak rate {memory_leak_rate:.2f} MB/hour exceeds 50 MB/hour threshold"
        logger.info(f"✅ Memory leak rate OK: {memory_leak_rate:.2f} MB/hour < 50 MB/hour")
        
        # 4. Response time stability
        if len(response_times) >= 100:
            response_first_100 = statistics.mean(response_times[:100])
            response_last_100 = statistics.mean(response_times[-100:])
            response_degradation = (response_last_100 - response_first_100) / response_first_100
            
            assert response_degradation < 0.20, \
                f"Response time degraded by {response_degradation:.1%} (threshold: 20%)"
            logger.info(f"✅ Response time stable: degradation {response_degradation:.1%} < 20%")
        
        logger.info(f"")
        logger.info(f"{'='*80}")
        logger.info(f"✅ TEST PASSED: 24-Hour Soak Test Successful!")
        logger.info(f"{'='*80}")
        logger.info(f"No memory leaks detected")
        logger.info(f"System remained stable for 24 hours")
        logger.info(f"Performance remained consistent")
        logger.info(f"{'='*80}\n")


# ===================================================================
# Shorter Soak Test (4 hours) - For CI/Nightly
# ===================================================================

@pytest.mark.slow
@pytest.mark.nightly
@pytest.mark.load
@pytest.mark.soak
@pytest.mark.regression
class TestSoakMemoryLeakShort:
    """Shorter 4-hour soak test for nightly runs."""
    
    @pytest.mark.xray("PZ-15138")
    @pytest.mark.regression
    def test_memory_leak_soak_4_hours(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-15138 (Short Version): 4-Hour Soak Test.
        
        Shorter version of the 24-hour soak test for nightly CI runs.
        
        Expected:
            - Memory growth < 5% over 4 hours
            - Success rate ≥ 95%
            - No crashes
        """
        logger.info("=" * 80)
        logger.info("TEST: 4-Hour Soak Test - Memory Leak Detection (PZ-15138 Short)")
        logger.info("=" * 80)
        
        duration_hours = 4
        jobs_per_interval = 5
        interval_minutes = 5
        
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
        
        # Record baseline
        memory_baseline = psutil.virtual_memory().percent
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        total_success = 0
        total_failure = 0
        memory_samples = [memory_baseline]
        
        logger.info(f"Running {duration_hours}-hour soak test...")
        logger.info(f"Creating {jobs_per_interval} jobs every {interval_minutes} minutes")
        
        while datetime.now() < end_time:
            # Create jobs
            for _ in range(jobs_per_interval):
                try:
                    config_request = ConfigureRequest(**config_payload)
                    response = focus_server_api.configure_streaming_job(config_request)
                    
                    if response.job_id:
                        total_success += 1
                        # Cleanup immediately
                        try:
                            focus_server_api.cancel_job(response.job_id)
                        except:
                            pass
                    else:
                        total_failure += 1
                
                except Exception as e:
                    total_failure += 1
                    logger.debug(f"Job failed: {e}")
            
            # Sample memory
            current_memory = psutil.virtual_memory().percent
            memory_samples.append(current_memory)
            
            # Wait
            time.sleep(interval_minutes * 60)
        
        # Analysis
        memory_growth = memory_samples[-1] - memory_baseline
        success_rate = total_success / (total_success + total_failure)
        
        logger.info(f"\n4-Hour Soak Test Results:")
        logger.info(f"  Success Rate: {success_rate:.1%}")
        logger.info(f"  Memory Growth: +{memory_growth:.1f}%")
        
        # Assertions
        assert success_rate >= 0.95, \
            f"Success rate {success_rate:.1%} below 95%"
        
        assert memory_growth < 5, \
            f"Memory growth {memory_growth:.1f}% exceeds 5% (4-hour threshold)"
        
        logger.info(f"✅ 4-hour soak test passed!")

