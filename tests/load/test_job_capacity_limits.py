"""
Job Capacity Limits Testing
============================

Comprehensive tests to find system capacity limits in terms of concurrent jobs.

Test Categories:
1. Baseline Performance
2. Linear Load Test
3. Stress Test
4. Recovery Test
5. Resource Monitoring

Author: QA Automation Team
Date: October 26, 2025
"""

import pytest
import logging
import time
import statistics
import psutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Tuple
import json

from src.apis.focus_server_api import FocusServerAPI
from src.models.focus_server_models import ConfigureRequest
from src.core.exceptions import APIError

logger = logging.getLogger(__name__)


# ===================================================================
# Test Configuration
# ===================================================================

# Load test parameters (adjust according to your system capacity)
BASELINE_JOBS = 1          # Single job baseline
LIGHT_LOAD_JOBS = 5        # Light load
MEDIUM_LOAD_JOBS = 10      # Medium load
HEAVY_LOAD_JOBS = 20       # Heavy load
EXTREME_LOAD_JOBS = 50     # Extreme load
STRESS_LOAD_JOBS = 100     # Stress test
TARGET_CAPACITY_JOBS = 200 # Target capacity - meeting requirement (PZ-13756)

# Success rate thresholds
SUCCESS_RATE_EXCELLENT = 0.95  # 95%+ = Excellent
SUCCESS_RATE_GOOD = 0.90       # 90%+ = Good
SUCCESS_RATE_ACCEPTABLE = 0.80 # 80%+ = Acceptable
SUCCESS_RATE_POOR = 0.50       # 50%+ = Poor

# Performance thresholds
LATENCY_EXCELLENT_MS = 200     # < 200ms = Excellent
LATENCY_GOOD_MS = 500          # < 500ms = Good
LATENCY_ACCEPTABLE_MS = 1000   # < 1s = Acceptable

# Resource thresholds
CPU_THRESHOLD_WARNING = 70     # 70% CPU = Warning
CPU_THRESHOLD_CRITICAL = 85    # 85% CPU = Critical
MEM_THRESHOLD_WARNING = 75     # 75% RAM = Warning
MEM_THRESHOLD_CRITICAL = 90    # 90% RAM = Critical


# ===================================================================
# Helper Classes
# ===================================================================

class SystemMetrics:
    """Class for collecting system metrics."""
    
    def __init__(self):
        self.cpu_samples = []
        self.memory_samples = []
        self.network_samples = []
        self.disk_samples = []
        
    def sample(self):
        """Collect a single sample of metrics."""
        self.cpu_samples.append(psutil.cpu_percent(interval=0.1))
        self.memory_samples.append(psutil.virtual_memory().percent)
        
        # Network I/O
        net_io = psutil.net_io_counters()
        self.network_samples.append({
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv
        })
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        self.disk_samples.append({
            'read_bytes': disk_io.read_bytes,
            'write_bytes': disk_io.write_bytes
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get statistical summary."""
        if not self.cpu_samples:
            return {}
        
        return {
            'cpu': {
                'mean': statistics.mean(self.cpu_samples),
                'max': max(self.cpu_samples),
                'min': min(self.cpu_samples),
                'stdev': statistics.stdev(self.cpu_samples) if len(self.cpu_samples) > 1 else 0
            },
            'memory': {
                'mean': statistics.mean(self.memory_samples),
                'max': max(self.memory_samples),
                'min': min(self.memory_samples)
            },
            'samples_count': len(self.cpu_samples)
        }
    
    def is_system_healthy(self) -> Tuple[bool, str]:
        """Check if system is healthy."""
        if not self.cpu_samples:
            return True, "No samples yet"
        
        current_cpu = self.cpu_samples[-1]
        current_mem = self.memory_samples[-1]
        
        if current_cpu > CPU_THRESHOLD_CRITICAL:
            return False, f"CPU critical: {current_cpu:.1f}%"
        
        if current_mem > MEM_THRESHOLD_CRITICAL:
            return False, f"Memory critical: {current_mem:.1f}%"
        
        if current_cpu > CPU_THRESHOLD_WARNING:
            return True, f"CPU warning: {current_cpu:.1f}%"
        
        if current_mem > MEM_THRESHOLD_WARNING:
            return True, f"Memory warning: {current_mem:.1f}%"
        
        return True, "System healthy"


class JobMetrics:
    """Class for collecting job metrics."""
    
    def __init__(self):
        self.job_results = []
        self.creation_latencies = []
        self.start_time = None
        self.end_time = None
    
    def add_result(self, job_result: Dict[str, Any]):
        """Add a job result."""
        self.job_results.append(job_result)
        
        if job_result.get('success') and 'latency_ms' in job_result:
            self.creation_latencies.append(job_result['latency_ms'])
    
    def get_success_rate(self) -> float:
        """Get success rate."""
        if not self.job_results:
            return 0.0
        
        successes = sum(1 for r in self.job_results if r.get('success'))
        return successes / len(self.job_results)
    
    def get_latency_stats(self) -> Dict[str, float]:
        """Get latency statistics."""
        if not self.creation_latencies:
            return {}
        
        sorted_latencies = sorted(self.creation_latencies)
        
        return {
            'mean': statistics.mean(self.creation_latencies),
            'median': statistics.median(self.creation_latencies),
            'p95': sorted_latencies[int(len(sorted_latencies) * 0.95)],
            'p99': sorted_latencies[int(len(sorted_latencies) * 0.99)],
            'min': min(self.creation_latencies),
            'max': max(self.creation_latencies)
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get full summary."""
        duration_seconds = 0
        if self.start_time and self.end_time:
            duration_seconds = (self.end_time - self.start_time).total_seconds()
        
        return {
            'total_jobs': len(self.job_results),
            'successful_jobs': sum(1 for r in self.job_results if r.get('success')),
            'failed_jobs': sum(1 for r in self.job_results if not r.get('success')),
            'success_rate': self.get_success_rate(),
            'latency_stats': self.get_latency_stats(),
            'duration_seconds': duration_seconds,
            'jobs_per_second': len(self.job_results) / duration_seconds if duration_seconds > 0 else 0
        }


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def standard_config_payload():
    """Standard configuration for load tests."""
    return {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 1, "max": 50},  # 50 channels - medium load
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,  # Live mode
        "end_time": None,
        "view_type": 0  # MultiChannel
    }


@pytest.fixture
def lightweight_config_payload():
    """Lightweight configuration for high load tests."""
    return {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 512,  # Lower NFFT
        "displayInfo": {"height": 800},
        "channels": {"min": 1, "max": 10},  # Only 10 channels
        "frequencyRange": {"min": 0, "max": 250},
        "start_time": None,
        "end_time": None,
        "view_type": 0
    }


@pytest.fixture
def heavy_config_payload():
    """Heavy configuration for boundary testing."""
    return {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 2048,  # High NFFT
        "displayInfo": {"height": 1200},
        "channels": {"min": 1, "max": 200},  # 200 channels
        "frequencyRange": {"min": 0, "max": 1000},
        "start_time": None,
        "end_time": None,
        "view_type": 0  # MultiChannel = heaviest load
    }


# ===================================================================
# Helper Functions
# ===================================================================

def create_single_job(api: FocusServerAPI, config_payload: Dict[str, Any], 
                     job_num: int) -> Dict[str, Any]:
    """
    Create a single job and measure performance.
    
    Returns:
        Dict with results: success, latency_ms, job_id, error_message
    """
    result = {
        'job_num': job_num,
        'success': False,
        'latency_ms': 0,
        'job_id': None,
        'error_message': None
    }
    
    try:
        start_time = time.time()
        
        config_request = ConfigureRequest(**config_payload)
        response = api.configure_streaming_job(config_request)
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        result['success'] = True
        result['latency_ms'] = latency_ms
        result['job_id'] = response.job_id if hasattr(response, 'job_id') else None
        
        logger.debug(f"Job #{job_num} created successfully: {result['job_id']} ({latency_ms:.0f}ms)")
        
    except Exception as e:
        result['error_message'] = str(e)
        logger.warning(f"Job #{job_num} failed: {e}")
    
    return result


def create_concurrent_jobs(api: FocusServerAPI, config_payload: Dict[str, Any],
                          num_jobs: int, max_workers: int = 20) -> Tuple[JobMetrics, SystemMetrics]:
    """
    Create concurrent jobs and measure performance.
    
    Args:
        api: FocusServerAPI instance
        config_payload: Configuration for jobs
        num_jobs: Number of jobs to create
        max_workers: Maximum number of concurrent threads
    
    Returns:
        Tuple of (JobMetrics, SystemMetrics)
    """
    job_metrics = JobMetrics()
    system_metrics = SystemMetrics()
    
    logger.info(f"\n{'='*70}")
    logger.info(f"Creating {num_jobs} concurrent jobs with {max_workers} workers")
    logger.info(f"{'='*70}")
    
    job_metrics.start_time = datetime.now()
    
    # Sample system metrics before
    system_metrics.sample()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        futures = [
            executor.submit(create_single_job, api, config_payload, i)
            for i in range(num_jobs)
        ]
        
        # Collect results as they complete
        for future in as_completed(futures):
            result = future.result()
            job_metrics.add_result(result)
            
            # Sample system every 10 jobs
            if len(job_metrics.job_results) % 10 == 0:
                system_metrics.sample()
    
    job_metrics.end_time = datetime.now()
    
    # Sample system metrics after
    system_metrics.sample()
    
    # Print summary
    summary = job_metrics.get_summary()
    logger.info(f"\nResults for {num_jobs} jobs:")
    logger.info(f"  ✓ Success Rate: {summary['success_rate']:.1%}")
    logger.info(f"  ✓ Successful: {summary['successful_jobs']}/{summary['total_jobs']}")
    logger.info(f"  ✓ Failed: {summary['failed_jobs']}/{summary['total_jobs']}")
    
    if summary['latency_stats']:
        stats = summary['latency_stats']
        logger.info(f"  ⏱ Latency - Mean: {stats['mean']:.0f}ms, "
                   f"P95: {stats['p95']:.0f}ms, P99: {stats['p99']:.0f}ms")
    
    system_summary = system_metrics.get_summary()
    if system_summary:
        logger.info(f"  💻 CPU - Mean: {system_summary['cpu']['mean']:.1f}%, "
                   f"Max: {system_summary['cpu']['max']:.1f}%")
        logger.info(f"  🧠 Memory - Mean: {system_summary['memory']['mean']:.1f}%, "
                   f"Max: {system_summary['memory']['max']:.1f}%")
    
    return job_metrics, system_metrics


def cleanup_jobs(api: FocusServerAPI, job_ids: List[str]):
    """Clean up created jobs."""
    logger.info(f"Cleaning up {len(job_ids)} jobs...")
    
    cleaned = 0
    for job_id in job_ids:
        try:
            api.cancel_job(job_id)
            cleaned += 1
        except Exception as e:
            logger.debug(f"Failed to clean job {job_id}: {e}")
    
    logger.info(f"Cleaned {cleaned}/{len(job_ids)} jobs")


# ===================================================================
# Test 1: Baseline Performance
# ===================================================================

@pytest.mark.load
@pytest.mark.baseline
@pytest.mark.jira("PZ-13986", "PZ-13268")  # Bugs: 200 Jobs Capacity Issue, CNI IP Exhaustion
class TestBaselinePerformance:
    """Baseline performance test - single job."""
    
    def test_single_job_baseline(self, focus_server_api, standard_config_payload):
        """
        Baseline performance test for a single job.
        
        Measures:
        - Latency for job creation
        - System resources
        - Job health
        """
        logger.info("\n" + "="*70)
        logger.info("TEST: Baseline Performance - Single Job")
        logger.info("="*70)
        
        # Create single job
        job_metrics, system_metrics = create_concurrent_jobs(
            focus_server_api, 
            standard_config_payload, 
            num_jobs=BASELINE_JOBS,
            max_workers=1
        )
        
        # Get results
        summary = job_metrics.get_summary()
        system_summary = system_metrics.get_summary()
        
        # Assertions
        assert summary['success_rate'] == 1.0, \
            f"Baseline job should succeed (got {summary['success_rate']:.1%})"
        
        latency_stats = summary['latency_stats']
        assert latency_stats['mean'] < LATENCY_ACCEPTABLE_MS, \
            f"Baseline latency too high: {latency_stats['mean']:.0f}ms"
        
        logger.info(f"\n✅ Baseline established:")
        logger.info(f"   Latency: {latency_stats['mean']:.0f}ms")
        logger.info(f"   CPU: {system_summary['cpu']['mean']:.1f}%")
        logger.info(f"   Memory: {system_summary['memory']['mean']:.1f}%")


# ===================================================================
# Test 2: Linear Load Test
# ===================================================================

@pytest.mark.load
@pytest.mark.linear
@pytest.mark.jira("PZ-13986", "PZ-13268")  # Bugs: 200 Jobs Capacity Issue, CNI IP Exhaustion
class TestLinearLoad:
    """Linear load test - finding breaking point."""
    
    def test_linear_load_progression(self, focus_server_api, lightweight_config_payload):
        """
        Linear load test: 5 → 10 → 20 → 50 jobs.
        
        Goal: Find the point where success rate drops below 90%.
        """
        logger.info("\n" + "="*70)
        logger.info("TEST: Linear Load Progression")
        logger.info("="*70)
        
        test_levels = [
            LIGHT_LOAD_JOBS,    # 5
            MEDIUM_LOAD_JOBS,   # 10
            HEAVY_LOAD_JOBS,    # 20
            EXTREME_LOAD_JOBS   # 50
        ]
        
        results = {}
        
        for num_jobs in test_levels:
            logger.info(f"\n{'='*70}")
            logger.info(f"Testing {num_jobs} concurrent jobs...")
            logger.info(f"{'='*70}")
            
            # Create jobs
            job_metrics, system_metrics = create_concurrent_jobs(
                focus_server_api,
                lightweight_config_payload,
                num_jobs=num_jobs,
                max_workers=min(num_jobs, 20)
            )
            
            summary = job_metrics.get_summary()
            system_summary = system_metrics.get_summary()
            
            results[num_jobs] = {
                'job_metrics': summary,
                'system_metrics': system_summary
            }
            
            # Check if we hit capacity
            if summary['success_rate'] < SUCCESS_RATE_GOOD:
                logger.warning(f"⚠️ Success rate dropped to {summary['success_rate']:.1%} at {num_jobs} jobs")
                logger.warning(f"   Possible capacity limit reached!")
                break
            
            # Give system time to recover
            logger.info("Waiting 5 seconds for system recovery...")
            time.sleep(5)
        
        # Print summary table
        logger.info("\n" + "="*70)
        logger.info("LINEAR LOAD TEST - SUMMARY")
        logger.info("="*70)
        logger.info(f"{'Jobs':<10} {'Success Rate':<15} {'Latency (ms)':<15} {'CPU %':<10} {'Memory %':<10}")
        logger.info("-" * 70)
        
        for num_jobs, result in results.items():
            job_sum = result['job_metrics']
            sys_sum = result['system_metrics']
            latency = job_sum['latency_stats'].get('mean', 0)
            cpu = sys_sum['cpu']['mean']
            mem = sys_sum['memory']['mean']
            
            logger.info(f"{num_jobs:<10} {job_sum['success_rate']:<15.1%} {latency:<15.0f} {cpu:<10.1f} {mem:<10.1f}")
        
        logger.info("="*70)
        
        # Find maximum capacity with good success rate
        max_capacity = 0
        for num_jobs, result in results.items():
            if result['job_metrics']['success_rate'] >= SUCCESS_RATE_GOOD:
                max_capacity = num_jobs
        
        logger.info(f"\n📊 Maximum Capacity (90%+ success): {max_capacity} concurrent jobs")
        
        # Assertion: we should handle at least MEDIUM_LOAD_JOBS
        assert MEDIUM_LOAD_JOBS in results, \
            f"Should have tested at least {MEDIUM_LOAD_JOBS} jobs"
        
        assert results[LIGHT_LOAD_JOBS]['job_metrics']['success_rate'] >= SUCCESS_RATE_GOOD, \
            f"System should handle {LIGHT_LOAD_JOBS} jobs with 90%+ success"


# ===================================================================
# Test 3: Stress Test
# ===================================================================

@pytest.mark.load
@pytest.mark.stress
@pytest.mark.slow
@pytest.mark.jira("PZ-13986", "PZ-13268")  # Bugs: 200 Jobs Capacity Issue, CNI IP Exhaustion
class TestStressLoad:
    """Stress test - pushing system to the limit."""
    
    def test_extreme_concurrent_load(self, focus_server_api, lightweight_config_payload):
        """
        Extreme load test: 100 concurrent jobs.
        
        Goal: Check how system behaves under overload.
        """
        logger.info("\n" + "="*70)
        logger.info("TEST: Stress Test - Extreme Load")
        logger.info("="*70)
        logger.warning("⚠️ This test may cause temporary system overload!")
        
        # Create extreme load
        job_metrics, system_metrics = create_concurrent_jobs(
            focus_server_api,
            lightweight_config_payload,
            num_jobs=STRESS_LOAD_JOBS,
            max_workers=30
        )
        
        summary = job_metrics.get_summary()
        system_summary = system_metrics.get_summary()
        
        # Log results
        logger.info(f"\n📊 Stress Test Results ({STRESS_LOAD_JOBS} jobs):")
        logger.info(f"   Success Rate: {summary['success_rate']:.1%}")
        logger.info(f"   Successful: {summary['successful_jobs']}/{summary['total_jobs']}")
        logger.info(f"   Failed: {summary['failed_jobs']}/{summary['total_jobs']}")
        
        if summary['latency_stats']:
            stats = summary['latency_stats']
            logger.info(f"   Latency P95: {stats['p95']:.0f}ms, P99: {stats['p99']:.0f}ms")
        
        logger.info(f"   CPU Max: {system_summary['cpu']['max']:.1f}%")
        logger.info(f"   Memory Max: {system_summary['memory']['max']:.1f}%")
        
        # Check system health
        is_healthy, health_msg = system_metrics.is_system_healthy()
        logger.info(f"   System Health: {health_msg}")
        
        # We expect some failures at this load
        # But the system should not crash completely
        assert summary['success_rate'] > SUCCESS_RATE_POOR, \
            f"Even under stress, system should maintain {SUCCESS_RATE_POOR:.0%}+ success rate"
        
        logger.info("\n✅ Stress test completed - system survived!")


# ===================================================================
# Test 4: Heavy Configuration Stress Test
# ===================================================================

@pytest.mark.load
@pytest.mark.stress
@pytest.mark.slow
@pytest.mark.jira("PZ-13986")  # Bug: 200 Jobs Capacity Issue
class TestHeavyConfigurationStress:
    """Stress test with heavy configuration."""
    
    def test_heavy_config_concurrent(self, focus_server_api, heavy_config_payload):
        """
        Heavy configuration test (200 channels, NFFT 2048) with concurrent jobs.
        
        This is the most demanding test - system is expected to struggle.
        """
        logger.info("\n" + "="*70)
        logger.info("TEST: Heavy Configuration Stress")
        logger.info("="*70)
        logger.info("Config: 200 channels, NFFT 2048, Full frequency range")
        logger.warning("⚠️ This is the most demanding test!")
        
        # Test with fewer jobs due to heavy config
        num_jobs = MEDIUM_LOAD_JOBS  # 10 jobs only
        
        job_metrics, system_metrics = create_concurrent_jobs(
            focus_server_api,
            heavy_config_payload,
            num_jobs=num_jobs,
            max_workers=5  # Fewer workers due to heavy load
        )
        
        summary = job_metrics.get_summary()
        system_summary = system_metrics.get_summary()
        
        logger.info(f"\n📊 Heavy Config Results ({num_jobs} jobs):")
        logger.info(f"   Success Rate: {summary['success_rate']:.1%}")
        logger.info(f"   CPU Max: {system_summary['cpu']['max']:.1f}%")
        logger.info(f"   Memory Max: {system_summary['memory']['max']:.1f}%")
        
        if summary['latency_stats']:
            stats = summary['latency_stats']
            logger.info(f"   Latency P95: {stats['p95']:.0f}ms")
        
        # With heavy config, we expect lower success rate
        # But it should still work to some extent
        assert summary['success_rate'] >= SUCCESS_RATE_ACCEPTABLE, \
            f"Heavy config should maintain {SUCCESS_RATE_ACCEPTABLE:.0%}+ success"


# ===================================================================
# Test 5: Recovery Test
# ===================================================================

@pytest.mark.load
@pytest.mark.recovery
@pytest.mark.jira("PZ-13986")  # Bug: 200 Jobs Capacity Issue
class TestSystemRecovery:
    """System recovery test after load."""
    
    def test_recovery_after_stress(self, focus_server_api, standard_config_payload):
        """
        Check that system recovers after heavy load.
        
        Process:
        1. Create heavy load
        2. Wait 30 seconds
        3. Try single job
        4. Verify it succeeds
        """
        logger.info("\n" + "="*70)
        logger.info("TEST: System Recovery After Stress")
        logger.info("="*70)
        
        # Step 1: Create stress load
        logger.info("Step 1: Creating stress load...")
        stress_metrics, _ = create_concurrent_jobs(
            focus_server_api,
            standard_config_payload,
            num_jobs=HEAVY_LOAD_JOBS,
            max_workers=20
        )
        
        stress_success = stress_metrics.get_summary()['success_rate']
        logger.info(f"Stress load success rate: {stress_success:.1%}")
        
        # Step 2: Wait for recovery
        recovery_time = 30
        logger.info(f"\nStep 2: Waiting {recovery_time} seconds for recovery...")
        time.sleep(recovery_time)
        
        # Step 3: Test single job
        logger.info("\nStep 3: Testing single job after recovery...")
        recovery_metrics, recovery_system = create_concurrent_jobs(
            focus_server_api,
            standard_config_payload,
            num_jobs=1,
            max_workers=1
        )
        
        recovery_summary = recovery_metrics.get_summary()
        recovery_sys_summary = recovery_system.get_summary()
        
        # Step 4: Verify recovery
        logger.info(f"\n📊 Recovery Test Results:")
        logger.info(f"   Success: {recovery_summary['success_rate']:.1%}")
        logger.info(f"   Latency: {recovery_summary['latency_stats']['mean']:.0f}ms")
        logger.info(f"   CPU: {recovery_sys_summary['cpu']['mean']:.1f}%")
        logger.info(f"   Memory: {recovery_sys_summary['memory']['mean']:.1f}%")
        
        assert recovery_summary['success_rate'] == 1.0, \
            "System should fully recover after stress"
        
        assert recovery_summary['latency_stats']['mean'] < LATENCY_ACCEPTABLE_MS, \
            "Latency should return to normal after recovery"
        
        logger.info("\n✅ System recovered successfully!")


# ===================================================================
# Test 6: Sustained Load Test (Soak Test)
# ===================================================================

@pytest.mark.load
@pytest.mark.soak
@pytest.mark.slow
@pytest.mark.skip(reason="Very long test - run manually")
class TestSustainedLoad:
    """Sustained load test - soak test."""
    
    def test_sustained_load_1_hour(self, focus_server_api, standard_config_payload):
        """
        Sustained load test: 10 jobs for 1 hour.
        
        Goal: Detect memory leaks or resource leaks.
        """
        logger.info("\n" + "="*70)
        logger.info("TEST: Sustained Load - 1 Hour Soak Test")
        logger.info("="*70)
        logger.warning("⚠️ This test will run for approximately 1 hour!")
        
        duration_seconds = 3600  # 1 hour
        num_jobs = MEDIUM_LOAD_JOBS
        interval_seconds = 60  # Create jobs every 60 seconds
        
        start_time = datetime.now()
        iteration = 0
        all_results = []
        
        while (datetime.now() - start_time).total_seconds() < duration_seconds:
            iteration += 1
            logger.info(f"\n--- Iteration {iteration} ---")
            
            job_metrics, system_metrics = create_concurrent_jobs(
                focus_server_api,
                standard_config_payload,
                num_jobs=num_jobs,
                max_workers=10
            )
            
            summary = job_metrics.get_summary()
            system_summary = system_metrics.get_summary()
            
            all_results.append({
                'iteration': iteration,
                'timestamp': datetime.now(),
                'success_rate': summary['success_rate'],
                'cpu_max': system_summary['cpu']['max'],
                'memory_max': system_summary['memory']['max']
            })
            
            logger.info(f"Iteration {iteration}: "
                       f"Success {summary['success_rate']:.1%}, "
                       f"CPU {system_summary['cpu']['max']:.1f}%, "
                       f"Memory {system_summary['memory']['max']:.1f}%")
            
            # Check for degradation
            if summary['success_rate'] < SUCCESS_RATE_ACCEPTABLE:
                logger.error(f"❌ Success rate dropped below acceptable level!")
                break
            
            # Wait before next iteration
            time.sleep(interval_seconds)
        
        # Analyze results
        logger.info("\n" + "="*70)
        logger.info("SOAK TEST - SUMMARY")
        logger.info("="*70)
        
        memory_trend = [r['memory_max'] for r in all_results]
        cpu_trend = [r['cpu_max'] for r in all_results]
        success_trend = [r['success_rate'] for r in all_results]
        
        logger.info(f"Total iterations: {len(all_results)}")
        logger.info(f"Average success rate: {statistics.mean(success_trend):.1%}")
        logger.info(f"Memory trend: {memory_trend[0]:.1f}% → {memory_trend[-1]:.1f}%")
        logger.info(f"CPU trend: {cpu_trend[0]:.1f}% → {cpu_trend[-1]:.1f}%")
        
        # Check for memory leak
        memory_increase = memory_trend[-1] - memory_trend[0]
        if memory_increase > 10:
            logger.warning(f"⚠️ Possible memory leak detected: +{memory_increase:.1f}%")
        
        assert statistics.mean(success_trend) >= SUCCESS_RATE_GOOD, \
            "Sustained load should maintain 90%+ success rate"


# ===================================================================
# Test 7: 200 Concurrent Jobs - Target Capacity (NEW - PZ-13756)
# ===================================================================

@pytest.mark.load
@pytest.mark.capacity
@pytest.mark.critical
@pytest.mark.xray("PZ-14088")
class Test200ConcurrentJobsCapacity:
    """
    Target capacity test - 200 concurrent jobs.
    
    PZ-13986: 200 Jobs Capacity Issue (Infrastructure Gap)
    
    Meeting requirement (PZ-13756):
    - System must support 200 concurrent jobs
    - Target environments (DEV/Staging) must succeed
    - Non-target environments: Infra Gap report
    
    Found bug: System handles only 40/200 concurrent jobs (20% success rate).
    """
    
    @pytest.mark.xray("PZ-14088")
    def test_200_concurrent_jobs_target_capacity(
        self, 
        focus_server_api, 
        lightweight_config_payload,
        config_manager
    ):
        """
        Test: 200 Concurrent Jobs - Target Capacity Validation
        
        PZ-13986: 200 Jobs Capacity Issue
        
        Validates that environment supports 200 concurrent jobs.
        If target not met, generates Infrastructure Gap Report.
        
        Found bug: Only 40/200 jobs succeed (80% failure rate).
        This is an infrastructure capacity gap requiring DevOps attention.
        
        Success Criteria:
        - DEV/Staging: Must support 200 jobs (>= 95% success rate)
        - Other envs: Report actual capacity + gap analysis
        
        Related: Meeting decision (PZ-13756) - Support 200 concurrent Jobs
        
        Args:
            focus_server_api: FocusServerAPI fixture
            lightweight_config_payload: Lightweight config for capacity testing
            config_manager: ConfigManager fixture for environment detection
        """
        logger.info("\n" + "="*80)
        logger.info("TEST: 200 CONCURRENT JOBS - TARGET CAPACITY VALIDATION")
        logger.info("="*80)
        logger.info("This is a CRITICAL test per meeting decision (PZ-13756)")
        logger.info("="*80 + "\n")
        
        # Get environment info
        env = config_manager.environment
        logger.info(f"🌍 Testing environment: {env}")
        
        # Determine if this is a target environment
        target_environments = ["dev", "staging"]
        is_target_env = env.lower() in target_environments
        
        if is_target_env:
            logger.info(f"✅ This is a TARGET environment - must meet 200 jobs requirement")
        else:
            logger.info(f"ℹ️  This is a non-target environment - will report actual capacity")
        
        # Create 200 concurrent jobs
        logger.info(f"\n🚀 Creating {TARGET_CAPACITY_JOBS} concurrent jobs...")
        logger.info(f"Using lightweight configuration to maximize capacity")
        
        job_metrics, system_metrics = create_concurrent_jobs(
            api=focus_server_api,
            config_payload=lightweight_config_payload,
            num_jobs=TARGET_CAPACITY_JOBS,
            max_workers=50  # High worker count for true concurrency
        )
        
        # Analyze results
        summary = job_metrics.get_summary()
        system_summary = system_metrics.get_summary()
        
        success_count = summary['successful_jobs']
        failed_count = summary['failed_jobs']
        success_rate = summary['success_rate']
        
        # Log detailed results
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 200 CONCURRENT JOBS - TEST RESULTS")
        logger.info(f"{'='*80}")
        logger.info(f"Environment:        {env}")
        logger.info(f"Target Capacity:    {TARGET_CAPACITY_JOBS} concurrent jobs")
        logger.info(f"Actual Capacity:    {success_count} jobs succeeded")
        logger.info(f"Failed Jobs:        {failed_count}")
        logger.info(f"Success Rate:       {success_rate:.1%}")
        logger.info(f"")
        
        if summary['latency_stats']:
            stats = summary['latency_stats']
            logger.info(f"Performance Metrics:")
            logger.info(f"  ⏱️  Average Latency:  {stats['mean']:.0f}ms")
            logger.info(f"  ⏱️  P95 Latency:      {stats['p95']:.0f}ms")
            logger.info(f"  ⏱️  P99 Latency:      {stats['p99']:.0f}ms")
            logger.info(f"  ⏱️  Max Latency:      {stats['max']:.0f}ms")
        
        logger.info(f"")
        logger.info(f"System Resources:")
        logger.info(f"  💻 CPU - Mean:       {system_summary['cpu']['mean']:.1f}%")
        logger.info(f"  💻 CPU - Max:        {system_summary['cpu']['max']:.1f}%")
        logger.info(f"  🧠 Memory - Mean:    {system_summary['memory']['mean']:.1f}%")
        logger.info(f"  🧠 Memory - Max:     {system_summary['memory']['max']:.1f}%")
        logger.info(f"{'='*80}\n")
        
        # Generate Infra Gap Report if capacity not fully met
        gap = TARGET_CAPACITY_JOBS - success_count
        
        if gap > 0:
            logger.warning(f"⚠️  Capacity gap detected: {gap} jobs short of target")
            
            report_path = generate_infra_gap_report(
                environment=env,
                target_capacity=TARGET_CAPACITY_JOBS,
                actual_capacity=success_count,
                success_rate=success_rate,
                job_metrics=summary,
                system_metrics=system_summary,
                recommendations=[
                    "Scale Kubernetes cluster - add more nodes",
                    "Increase resource limits for Focus Server pods",
                    "Optimize Focus Server startup time and resource usage",
                    "Consider implementing job queue mechanism for burst capacity",
                    "Review network bandwidth and latency between components",
                    "Consult with DevOps team for infrastructure capacity planning"
                ]
            )
            
            logger.warning(f"📄 Infrastructure Gap Report generated: {report_path}")
            logger.warning(f"   Review this report for capacity improvement recommendations")
        
        # Assertions based on environment type
        if is_target_env:
            # Target environments MUST meet the requirement
            assert success_rate >= SUCCESS_RATE_EXCELLENT, (
                f"\n{'='*80}\n"
                f"❌ CAPACITY REQUIREMENT NOT MET\n"
                f"{'='*80}\n"
                f"Environment:        {env} (TARGET ENVIRONMENT)\n"
                f"Required:           200 concurrent jobs (95%+ success rate)\n"
                f"Achieved:           {success_count}/{TARGET_CAPACITY_JOBS} jobs ({success_rate:.1%})\n"
                f"Gap:                {gap} jobs\n"
                f"\n"
                f"Target environments (dev/staging) MUST support 200 concurrent jobs.\n"
                f"See Infrastructure Gap Report for recommendations: {report_path if gap > 0 else 'N/A'}\n"
                f"{'='*80}\n"
            )
            
            logger.info(f"\n{'='*80}")
            logger.info(f"✅ CAPACITY REQUIREMENT MET")
            logger.info(f"{'='*80}")
            logger.info(f"Environment '{env}' successfully supports 200 concurrent jobs!")
            logger.info(f"Success Rate: {success_rate:.1%} (>= {SUCCESS_RATE_EXCELLENT:.0%} required)")
            logger.info(f"{'='*80}\n")
        
        else:
            # Non-target environments: just report capacity (informational)
            logger.info(f"\n{'='*80}")
            logger.info(f"ℹ️  CAPACITY REPORT (Informational)")
            logger.info(f"{'='*80}")
            logger.info(f"Environment:        {env} (non-target)")
            logger.info(f"Achieved Capacity:  {success_count}/{TARGET_CAPACITY_JOBS} jobs")
            logger.info(f"Success Rate:       {success_rate:.1%}")
            logger.info(f"")
            logger.info(f"This environment is not required to meet the 200 jobs target.")
            logger.info(f"Results are informational for capacity planning purposes.")
            
            if gap > 0:
                logger.info(f"")
                logger.info(f"If you need to improve capacity, see Infrastructure Gap Report:")
                logger.info(f"  {report_path}")
            
            logger.info(f"{'='*80}\n")


# ===================================================================
# Infrastructure Gap Report Generation
# ===================================================================

def generate_infra_gap_report(
    environment: str,
    target_capacity: int,
    actual_capacity: int,
    success_rate: float,
    job_metrics: Dict[str, Any],
    system_metrics: Dict[str, Any],
    recommendations: List[str]
) -> str:
    """
    Generate Infrastructure Gap Report when capacity target not met.
    
    This report provides:
    - Detailed capacity gap analysis
    - Performance metrics
    - System resource utilization
    - Bottleneck identification
    - Actionable recommendations
    - Next steps for infrastructure team
    
    Args:
        environment: Environment name (dev/staging/production)
        target_capacity: Target number of concurrent jobs (200)
        actual_capacity: Actual number of jobs achieved
        success_rate: Success rate (0.0-1.0)
        job_metrics: Job creation metrics (from JobMetrics.get_summary())
        system_metrics: System resource metrics (from SystemMetrics.get_summary())
        recommendations: List of specific recommendations
    
    Returns:
        str: Path to generated report file
    
    Example:
        >>> report_path = generate_infra_gap_report(
        ...     environment="dev",
        ...     target_capacity=200,
        ...     actual_capacity=150,
        ...     success_rate=0.75,
        ...     job_metrics=metrics_summary,
        ...     system_metrics=system_summary,
        ...     recommendations=["Scale K8s cluster", "Increase pod resources"]
        ... )
        >>> print(f"Report saved to: {report_path}")
    """
    import os
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"infra_gap_report_{environment}_{timestamp}.json"
    
    # Create reports directory if it doesn't exist
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, report_filename)
    
    # Calculate gap metrics
    gap = target_capacity - actual_capacity
    gap_percentage = (gap / target_capacity) * 100
    
    # Extract latency stats
    latency_stats = job_metrics.get('latency_stats', {})
    avg_creation_latency_ms = latency_stats.get('mean', 0)
    p95_latency_ms = latency_stats.get('p95', 0)
    p99_latency_ms = latency_stats.get('p99', 0)
    max_latency_ms = latency_stats.get('max', 0)
    
    # Extract system metrics
    cpu_metrics = system_metrics.get('cpu', {})
    memory_metrics = system_metrics.get('memory', {})
    
    cpu_mean = cpu_metrics.get('mean', 0)
    cpu_max = cpu_metrics.get('max', 0)
    memory_mean = memory_metrics.get('mean', 0)
    memory_max = memory_metrics.get('max', 0)
    
    # Identify bottlenecks
    bottlenecks = []
    bottleneck_analysis = {
        "cpu_bottleneck": cpu_max > CPU_THRESHOLD_CRITICAL,
        "memory_bottleneck": memory_max > MEM_THRESHOLD_CRITICAL,
        "latency_bottleneck": avg_creation_latency_ms > LATENCY_ACCEPTABLE_MS,
        "severe_failures": success_rate < SUCCESS_RATE_ACCEPTABLE
    }
    
    if bottleneck_analysis["cpu_bottleneck"]:
        bottlenecks.append(f"CPU usage exceeded {CPU_THRESHOLD_CRITICAL}% (peak: {cpu_max:.1f}%) - likely CPU bottleneck")
    
    if bottleneck_analysis["memory_bottleneck"]:
        bottlenecks.append(f"Memory usage exceeded {MEM_THRESHOLD_CRITICAL}% (peak: {memory_max:.1f}%) - likely memory bottleneck")
    
    if bottleneck_analysis["latency_bottleneck"]:
        bottlenecks.append(f"Average job creation took {avg_creation_latency_ms:.0f}ms (threshold: {LATENCY_ACCEPTABLE_MS}ms) - slow provisioning")
    
    if bottleneck_analysis["severe_failures"]:
        bottlenecks.append(f"High failure rate ({(1-success_rate)*100:.1f}%) indicates system overload or misconfiguration")
    
    if not bottlenecks:
        bottlenecks.append("No obvious bottlenecks detected - may need deeper analysis")
    
    # Build comprehensive report
    report = {
        "report_metadata": {
            "report_type": "Infrastructure Capacity Gap Analysis",
            "generated_at": datetime.now().isoformat(),
            "generated_by": "Focus Server Automation Test Suite",
            "jira_reference": "PZ-13756",
            "meeting_decision": "Support 200 concurrent jobs"
        },
        
        "environment": {
            "name": environment,
            "is_target_environment": environment.lower() in ["dev", "staging"],
            "requirement": "Must support 200 concurrent jobs" if environment.lower() in ["dev", "staging"] else "Informational only"
        },
        
        "capacity_analysis": {
            "target_capacity": target_capacity,
            "actual_capacity": actual_capacity,
            "gap": gap,
            "gap_percentage": f"{gap_percentage:.2f}%",
            "success_rate": f"{success_rate*100:.2f}%",
            "success_rate_raw": success_rate,
            "capacity_met": actual_capacity >= target_capacity,
            "success_threshold_met": success_rate >= SUCCESS_RATE_EXCELLENT
        },
        
        "performance_metrics": {
            "job_creation": {
                "total_jobs_attempted": job_metrics.get('total_jobs', 0),
                "successful_jobs": job_metrics.get('successful_jobs', 0),
                "failed_jobs": job_metrics.get('failed_jobs', 0),
                "average_latency_ms": f"{avg_creation_latency_ms:.2f}",
                "p95_latency_ms": f"{p95_latency_ms:.2f}",
                "p99_latency_ms": f"{p99_latency_ms:.2f}",
                "max_latency_ms": f"{max_latency_ms:.2f}",
                "duration_seconds": job_metrics.get('duration_seconds', 0),
                "jobs_per_second": f"{job_metrics.get('jobs_per_second', 0):.2f}"
            }
        },
        
        "system_resources": {
            "cpu": {
                "mean_percent": f"{cpu_mean:.2f}",
                "max_percent": f"{cpu_max:.2f}",
                "samples_collected": system_metrics.get('samples_count', 0),
                "threshold_warning": CPU_THRESHOLD_WARNING,
                "threshold_critical": CPU_THRESHOLD_CRITICAL,
                "exceeded_critical": cpu_max > CPU_THRESHOLD_CRITICAL
            },
            "memory": {
                "mean_percent": f"{memory_mean:.2f}",
                "max_percent": f"{memory_max:.2f}",
                "threshold_warning": MEM_THRESHOLD_WARNING,
                "threshold_critical": MEM_THRESHOLD_CRITICAL,
                "exceeded_critical": memory_max > MEM_THRESHOLD_CRITICAL
            }
        },
        
        "bottleneck_analysis": {
            "identified_bottlenecks": bottlenecks,
            "cpu_constrained": bottleneck_analysis["cpu_bottleneck"],
            "memory_constrained": bottleneck_analysis["memory_bottleneck"],
            "latency_issues": bottleneck_analysis["latency_bottleneck"],
            "high_failure_rate": bottleneck_analysis["severe_failures"]
        },
        
        "recommendations": {
            "immediate_actions": recommendations,
            "investigation_areas": [
                "Review Kubernetes cluster node capacity and utilization",
                "Analyze Focus Server pod resource requests and limits",
                "Check network bandwidth and latency metrics",
                "Review database (MongoDB) connection pool settings",
                "Verify RabbitMQ capacity and message throughput",
                "Check for any resource contention or throttling"
            ],
            "next_steps": [
                "Share this report with DevOps/Infrastructure team",
                "Schedule capacity planning meeting",
                "Plan infrastructure scaling strategy",
                "Consider implementing horizontal pod autoscaling (HPA)",
                "Set up monitoring alerts for capacity thresholds",
                "Re-run test after infrastructure improvements"
            ]
        },
        
        "additional_context": {
            "test_configuration": "Lightweight config (10 channels, NFFT 512)",
            "concurrency_workers": 50,
            "notes": [
                "Test used lightweight configuration to maximize job count",
                "Actual production workloads may have different resource profiles",
                "Results may vary based on time of day and system load",
                "Consider running test multiple times for consistent baseline"
            ]
        }
    }
    
    # Write report to JSON file
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"📊 INFRASTRUCTURE GAP REPORT GENERATED")
    logger.info(f"{'='*80}")
    logger.info(f"Report saved to: {report_path}")
    logger.info(f"{'='*80}\n")
    
    # Also log a summary to console for immediate visibility
    logger.warning(f"\n{'='*80}")
    logger.warning(f"║ INFRASTRUCTURE CAPACITY GAP REPORT")
    logger.warning(f"╠{'='*78}╣")
    logger.warning(f"║ Environment:        {environment:<58} ║")
    logger.warning(f"║ Target Capacity:    {target_capacity} concurrent jobs{' '*(44)} ║")
    logger.warning(f"║ Actual Capacity:    {actual_capacity} concurrent jobs{' '*(44 - len(str(actual_capacity)))} ║")
    logger.warning(f"║ Success Rate:       {success_rate*100:.1f}%{' '*(54)} ║")
    logger.warning(f"║ Gap:                {gap} jobs{' '*(53 - len(str(gap)))} ║")
    logger.warning(f"╠{'='*78}╣")
    logger.warning(f"║ TOP RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations[:3], 1):  # Show first 3
        logger.warning(f"║ {i}. {rec:<73} ║")
    logger.warning(f"╠{'='*78}╣")
    logger.warning(f"║ Full report: {report_path:<56} ║")
    logger.warning(f"{'='*80}\n")
    
    return report_path


# ===================================================================
# Test Report Generation
# ===================================================================

def generate_load_test_report(output_file: str = "load_test_report.json"):
    """
    Generate summary report of all load tests.
    
    Run all tests and save results to JSON file.
    """
    logger.info("\n" + "="*70)
    logger.info("GENERATING LOAD TEST REPORT")
    logger.info("="*70)
    
    # This would be called after running all tests
    # For now, it's a placeholder
    
    report = {
        'test_date': datetime.now().isoformat(),
        'system_info': {
            'cpu_count': psutil.cpu_count(),
            'total_memory_gb': psutil.virtual_memory().total / (1024**3),
            'python_version': pytest.__version__
        },
        'test_results': {
            # Would be populated with actual test results
        },
        'recommendations': []
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"✅ Report saved to: {output_file}")


if __name__ == "__main__":
    # Run load tests
    pytest.main([
        __file__,
        "-v",
        "-m", "load",
        "--tb=short",
        "--log-cli-level=INFO"
    ])

