"""
Live Job Load Tests - End-to-End Performance Testing
=====================================================

Tests the complete Live Job flow:
1. Create job via POST /configure
2. Wait for gRPC ready (with retries!)
3. Connect and stream data
4. Measure performance metrics

Based on Yonatan's feedback:
- Added retry logic between step 4 (configure) and step 5 (gRPC connect)
- Proper cleanup and resource management

Author: QA Automation Architect
Date: 2025-11-30
"""

import pytest
import logging
import os
from typing import Dict, Any, List

# Import K8s verification module
from be_focus_server_tests.load.k8s_job_verification import (
    verify_job_from_k8s,
    verify_jobs_batch_from_k8s,
    log_k8s_verification_summary,
    assert_all_jobs_are_live,
    K8sJobVerification,
    JobType
)

logger = logging.getLogger(__name__)


# =============================================================================
# Environment-based SLA Configuration
# =============================================================================

def get_environment() -> str:
    """Get current environment from env var."""
    return os.getenv("ENVIRONMENT", "staging").lower()


def get_live_job_sla() -> Dict[str, Any]:
    """
    Get SLA thresholds for Live Job tests.
    
    Production: Strict SLAs
    Staging: Lenient SLAs (weaker infrastructure)
    """
    env = get_environment()
    
    if env in ("prod", "production"):
        return {
            "description": "Production - Strict SLAs",
            # Job creation (POST /configure)
            "configure_p95_ms": 2000,
            "configure_p99_ms": 5000,
            # gRPC connection (including retries)
            "grpc_connect_p95_ms": 15000,
            "grpc_connect_p99_ms": 30000,
            # Total job time (create + connect + stream)
            "total_p95_ms": 20000,
            "total_p99_ms": 45000,
            # Success rate
            "min_success_rate": 95,
            # Retry thresholds
            "max_avg_retries": 2.0,
            "max_jobs_with_retries_pct": 30,
        }
    else:
        # Staging - more lenient
        return {
            "description": f"Staging - Lenient SLAs ({env})",
            # Job creation
            "configure_p95_ms": 5000,
            "configure_p99_ms": 10000,
            # gRPC connection
            "grpc_connect_p95_ms": 30000,
            "grpc_connect_p99_ms": 60000,
            # Total job time
            "total_p95_ms": 45000,
            "total_p99_ms": 90000,
            # Success rate
            "min_success_rate": 80,
            # Retry thresholds (staging may need more retries)
            "max_avg_retries": 3.0,
            "max_jobs_with_retries_pct": 50,
        }


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def live_job_sla() -> Dict[str, Any]:
    """Provide Live Job SLA configuration."""
    return get_live_job_sla()


@pytest.fixture
def live_job_tester(config_manager, kubernetes_manager):
    """
    Create LiveJobLoadTester instance with K8s verification.
    
    Configured with:
    - 50 channels (small load)
    - 500 Hz frequency range
    - 5 retries for gRPC connection (Yonatan's feedback!)
    - K8s job verification enabled
    """
    from be_focus_server_tests.load.live_job_load_tester import create_live_job_load_tester
    
    tester = create_live_job_load_tester(
        config_manager=config_manager,
        channels_min=1,
        channels_max=50,
        frequency_min=0,
        frequency_max=500,
        nfft=1024,
        display_height=600,
        # Retry config - KEY for reliability!
        max_grpc_connect_retries=5,
        grpc_connect_retry_delay_ms=2000,
        # Stream config
        frames_to_receive=5,
    )
    # Attach kubernetes_manager for K8s verification
    tester.k8s_manager = kubernetes_manager
    return tester


@pytest.fixture
def heavy_load_tester(config_manager, kubernetes_manager):
    """
    Create LiveJobLoadTester for heavy load testing with K8s verification.
    
    Configured with:
    - 500 channels (heavy load)
    - Full frequency range
    - K8s job verification enabled
    """
    from be_focus_server_tests.load.live_job_load_tester import create_live_job_load_tester
    
    tester = create_live_job_load_tester(
        config_manager=config_manager,
        channels_min=1,
        channels_max=500,
        frequency_min=0,
        frequency_max=1000,
        nfft=2048,
        display_height=800,
        max_grpc_connect_retries=5,
        grpc_connect_retry_delay_ms=3000,
        frames_to_receive=3,
    )
    # Attach kubernetes_manager for K8s verification
    tester.k8s_manager = kubernetes_manager
    return tester


# =============================================================================
# Test Class: Live Job Load Tests
# =============================================================================

@pytest.mark.live_job_load
@pytest.mark.load
class TestLiveJobLoad:
    """
    Live Job load tests - tests complete job lifecycle.
    
    Flow tested:
    1. POST /configure → Create job
    2. Wait + Retry → gRPC ready (Yonatan's insight!)
    3. Connect → gRPC stream
    4. Receive → Spectrogram frames
    5. Disconnect → Cleanup
    """
    
    @pytest.mark.xray("PZ-LOAD-100")
    def test_single_live_job_flow(self, live_job_tester, live_job_sla):
        """
        Test: Single Live Job complete flow.
        
        Validates:
        - Job creation succeeds
        - gRPC connection works (with retries if needed)
        - Frames are received
        - Proper cleanup
        """
        env = get_environment()
        
        logger.info(f"\n[*] Testing Single Live Job Flow")
        logger.info(f"    Environment: {env.upper()}")
        logger.info(f"    SLA: {live_job_sla['description']}")
        
        result = live_job_tester.run_load_test(
            num_jobs=1,
            concurrent_jobs=1,
            test_name="Single Live Job Flow"
        )
        
        # Assertions
        assert result.successful_jobs >= 1, \
            f"Single job should succeed, got {result.successful_jobs} successful"
        
        assert result.total_frames_received > 0, \
            "Should receive at least one frame"
        
        logger.info(f"[+] Single Live Job completed in {result.avg_total_time_ms:.0f}ms")
        logger.info(f"    Retries: {result.total_retries}")
        logger.info(f"    Frames: {result.total_frames_received}")
    
    @pytest.mark.xray("PZ-LOAD-101")
    def test_live_job_timing_sla(self, live_job_tester, live_job_sla):
        """
        Test: Live Job timing meets SLA.
        
        Measures:
        - Configure time (POST /configure)
        - gRPC connect time (including retries)
        - Total job time
        """
        env = get_environment()
        
        logger.info(f"\n[*] Testing Live Job Timing SLA")
        logger.info(f"    Environment: {env.upper()}")
        
        result = live_job_tester.run_load_test(
            num_jobs=5,
            concurrent_jobs=2,
            test_name="Live Job Timing SLA"
        )
        
        # Calculate P95 from results
        successful_results = [r for r in result.all_job_results if r.success]
        if not successful_results:
            pytest.fail("No successful jobs to measure timing")
        
        total_times = sorted([r.total_duration_ms for r in successful_results])
        p95_idx = int(len(total_times) * 0.95)
        actual_p95 = total_times[min(p95_idx, len(total_times) - 1)]
        
        # Assertions
        assert result.error_rate < (100 - live_job_sla['min_success_rate']), \
            f"Error rate {result.error_rate:.1f}% exceeds threshold ({env})"
        
        assert actual_p95 < live_job_sla['total_p95_ms'], \
            f"P95 total time {actual_p95:.0f}ms exceeds {live_job_sla['total_p95_ms']}ms SLA ({env})"
        
        logger.info(f"[+] Timing SLA passed:")
        logger.info(f"    P95 Total Time: {actual_p95:.0f}ms (limit: {live_job_sla['total_p95_ms']}ms)")
        logger.info(f"    Success Rate: {100 - result.error_rate:.1f}%")
    
    @pytest.mark.xray("PZ-LOAD-102")
    def test_concurrent_live_jobs(self, live_job_tester, live_job_sla):
        """
        Test: Multiple concurrent Live Jobs.
        
        Validates system handles concurrent job creation and streaming.
        """
        env = get_environment()
        concurrent = 3  # Start with 3 concurrent
        
        logger.info(f"\n[*] Testing Concurrent Live Jobs")
        logger.info(f"    Environment: {env.upper()}")
        logger.info(f"    Concurrent Jobs: {concurrent}")
        
        result = live_job_tester.run_load_test(
            num_jobs=6,
            concurrent_jobs=concurrent,
            test_name="Concurrent Live Jobs"
        )
        
        # Assertions
        success_rate = 100 - result.error_rate
        assert success_rate >= live_job_sla['min_success_rate'], \
            f"Success rate {success_rate:.1f}% below {live_job_sla['min_success_rate']}% ({env})"
        
        logger.info(f"[+] Concurrent test passed:")
        logger.info(f"    Success Rate: {success_rate:.1f}%")
        logger.info(f"    Avg Time: {result.avg_total_time_ms:.0f}ms")
        logger.info(f"    Total Retries: {result.total_retries}")
    
    @pytest.mark.xray("PZ-LOAD-103")
    def test_grpc_retry_behavior(self, live_job_tester, live_job_sla):
        """
        Test: gRPC connection retry behavior.
        
        Validates:
        - Retries happen when needed
        - Retry count is reasonable
        - Jobs succeed despite initial failures
        
        This is the KEY test based on Yonatan's feedback about
        needing retries between configure and gRPC connect.
        """
        env = get_environment()
        
        logger.info(f"\n[*] Testing gRPC Retry Behavior (Yonatan's feedback)")
        logger.info(f"    Environment: {env.upper()}")
        logger.info(f"    Max retries configured: 5")
        
        result = live_job_tester.run_load_test(
            num_jobs=5,
            concurrent_jobs=2,
            test_name="gRPC Retry Behavior"
        )
        
        # Analyze retry behavior
        logger.info(f"\n    Retry Analysis:")
        logger.info(f"    Total Retries: {result.total_retries}")
        logger.info(f"    Jobs with Retries: {result.jobs_with_retries}/{result.total_jobs}")
        logger.info(f"    Avg Retries per Job: {result.avg_retries_per_job:.2f}")
        
        # Assertions
        assert result.avg_retries_per_job <= live_job_sla['max_avg_retries'], \
            f"Avg retries {result.avg_retries_per_job:.2f} exceeds {live_job_sla['max_avg_retries']} ({env})"
        
        retry_pct = result.jobs_with_retries / max(result.total_jobs, 1) * 100
        assert retry_pct <= live_job_sla['max_jobs_with_retries_pct'], \
            f"Jobs with retries {retry_pct:.1f}% exceeds {live_job_sla['max_jobs_with_retries_pct']}% ({env})"
        
        # Key insight: Jobs should SUCCEED even if they needed retries
        success_rate = 100 - result.error_rate
        assert success_rate >= live_job_sla['min_success_rate'], \
            f"Success rate {success_rate:.1f}% too low despite retries ({env})"
        
        logger.info(f"[+] Retry behavior is within acceptable limits")


# =============================================================================
# Test Class: Heavy Load Tests
# =============================================================================

@pytest.mark.live_job_load
@pytest.mark.load
@pytest.mark.heavy
class TestLiveJobHeavyLoad:
    """
    Heavy load tests for Live Jobs.
    
    Uses larger channel ranges and more concurrent jobs.
    """
    
    @pytest.mark.xray("PZ-LOAD-110")
    @pytest.mark.slow
    def test_heavy_channel_load(self, heavy_load_tester, live_job_sla):
        """
        Test: Live Job with heavy channel load (500 channels).
        
        Validates system handles large channel requests.
        """
        env = get_environment()
        
        logger.info(f"\n[*] Testing Heavy Channel Load (500 channels)")
        logger.info(f"    Environment: {env.upper()}")
        
        result = heavy_load_tester.run_load_test(
            num_jobs=3,
            concurrent_jobs=1,  # Sequential for heavy load
            test_name="Heavy Channel Load"
        )
        
        # More lenient assertions for heavy load
        success_rate = 100 - result.error_rate
        min_required = live_job_sla['min_success_rate'] - 10  # 10% more lenient
        
        assert success_rate >= min_required, \
            f"Heavy load success rate {success_rate:.1f}% below {min_required}% ({env})"
        
        logger.info(f"[+] Heavy load test completed:")
        logger.info(f"    Success Rate: {success_rate:.1f}%")
        logger.info(f"    Avg Time: {result.avg_total_time_ms:.0f}ms")
    
    @pytest.mark.xray("PZ-LOAD-111")
    @pytest.mark.slow
    def test_sustained_live_job_load(self, live_job_tester, live_job_sla):
        """
        Test: Sustained Live Job load over time.
        
        Creates multiple jobs sequentially to test sustained performance.
        """
        env = get_environment()
        
        logger.info(f"\n[*] Testing Sustained Live Job Load")
        logger.info(f"    Environment: {env.upper()}")
        
        result = live_job_tester.run_load_test(
            num_jobs=10,
            concurrent_jobs=2,
            test_name="Sustained Live Job Load"
        )
        
        success_rate = 100 - result.error_rate
        
        assert success_rate >= live_job_sla['min_success_rate'], \
            f"Sustained load success rate {success_rate:.1f}% below threshold ({env})"
        
        # Check for performance degradation over time
        if len(result.all_job_results) >= 6:
            first_half = result.all_job_results[:len(result.all_job_results)//2]
            second_half = result.all_job_results[len(result.all_job_results)//2:]
            
            first_avg = sum(r.total_duration_ms for r in first_half if r.success) / max(len([r for r in first_half if r.success]), 1)
            second_avg = sum(r.total_duration_ms for r in second_half if r.success) / max(len([r for r in second_half if r.success]), 1)
            
            degradation = (second_avg - first_avg) / max(first_avg, 1) * 100
            
            logger.info(f"    Performance Degradation: {degradation:.1f}%")
            
            # Allow up to 50% degradation
            assert degradation < 50, \
                f"Performance degraded by {degradation:.1f}% over sustained load"
        
        logger.info(f"[+] Sustained load test passed:")
        logger.info(f"    Success Rate: {success_rate:.1f}%")
        logger.info(f"    Total Jobs: {result.total_jobs}")


# =============================================================================
# Test Class: Stress Tests
# =============================================================================

@pytest.mark.live_job_load
@pytest.mark.load
@pytest.mark.stress
class TestLiveJobStress:
    """
    Stress tests for Live Jobs - push the system to limits.
    """
    
    @pytest.mark.xray("PZ-LOAD-120")
    @pytest.mark.slow
    def test_max_concurrent_jobs(self, live_job_tester, live_job_sla):
        """
        Test: Maximum concurrent Live Jobs.
        
        Tests system behavior at high concurrency.
        Note: Focus Server has MaxWindows=30 limit.
        """
        env = get_environment()
        max_concurrent = 5  # Conservative for stress test
        
        logger.info(f"\n[*] Testing Max Concurrent Jobs")
        logger.info(f"    Environment: {env.upper()}")
        logger.info(f"    Concurrent Jobs: {max_concurrent}")
        
        result = live_job_tester.run_load_test(
            num_jobs=max_concurrent,
            concurrent_jobs=max_concurrent,
            test_name="Max Concurrent Jobs Stress"
        )
        
        # Stress test - more lenient
        success_rate = 100 - result.error_rate
        min_required = live_job_sla['min_success_rate'] - 15  # 15% more lenient
        
        logger.info(f"    Results:")
        logger.info(f"    Success Rate: {success_rate:.1f}%")
        logger.info(f"    P95 Time: {result.p95_total_time_ms:.0f}ms")
        logger.info(f"    Total Retries: {result.total_retries}")
        
        # Log errors for analysis
        if result.errors_by_type:
            logger.info(f"    Errors: {result.errors_by_type}")
        
        assert success_rate >= min_required, \
            f"Stress test success rate {success_rate:.1f}% below {min_required}% ({env})"

