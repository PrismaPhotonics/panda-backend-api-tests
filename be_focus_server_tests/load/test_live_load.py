"""
Live Job Load Tests - Real-Time Streaming Performance
======================================================

Tests for LIVE streaming jobs:
- Real-time data from the fiber
- No start_time/end_time (continuous stream)

Markers:
- @pytest.mark.live - Live job tests
- @pytest.mark.load - Load tests
- @pytest.mark.job_load - Job-based load tests

Run:
    pytest be_focus_server_tests/load/test_live_load.py -v -m live

Author: QA Automation Architect
Date: 2025-11-30
"""

import pytest
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)


# =============================================================================
# SLA Configuration
# =============================================================================

def get_environment() -> str:
    return os.getenv("ENVIRONMENT", "staging").lower()


def get_live_sla() -> Dict[str, Any]:
    """Get SLA for Live jobs."""
    env = get_environment()
    
    if env in ("prod", "production"):
        return {
            "description": "Production - Live Jobs",
            "configure_p95_ms": 2000,
            "grpc_connect_p95_ms": 15000,
            "total_p95_ms": 20000,
            "total_p99_ms": 45000,
            "min_success_rate": 95,
            "max_avg_retries": 2.0,
        }
    else:
        return {
            "description": f"Staging - Live Jobs ({env})",
            "configure_p95_ms": 5000,
            "grpc_connect_p95_ms": 30000,
            "total_p95_ms": 45000,
            "total_p99_ms": 90000,
            "min_success_rate": 80,
            "max_avg_retries": 3.0,
        }


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def live_sla() -> Dict[str, Any]:
    return get_live_sla()


@pytest.fixture
def live_tester(config_manager):
    """Create Live Job Load Tester."""
    from be_focus_server_tests.load.job_load_tester import create_live_job_tester
    
    return create_live_job_tester(
        config_manager=config_manager,
        channels_min=1,
        channels_max=50,
        frequency_min=0,
        frequency_max=500,
        nfft=1024,
        max_grpc_connect_retries=5,
        grpc_connect_retry_delay_ms=2000,
        frames_to_receive=5,
    )


@pytest.fixture
def heavy_live_tester(config_manager):
    """Create heavy Live Job Load Tester."""
    from be_focus_server_tests.load.job_load_tester import create_live_job_tester
    
    return create_live_job_tester(
        config_manager=config_manager,
        channels_min=1,
        channels_max=500,
        frequency_min=0,
        frequency_max=1000,
        nfft=2048,
        max_grpc_connect_retries=5,
        frames_to_receive=3,
    )


# =============================================================================
# Test Class: Live Job Load Tests
# =============================================================================

@pytest.mark.live
@pytest.mark.load
@pytest.mark.job_load
class TestLiveJobLoad:
    """
    Live Job load tests.
    
    Tests real-time streaming from the fiber.
    """
    
    @pytest.mark.xray("PZ-15234")  # Load - Live - Single Live Job Complete Flow
    @pytest.mark.jira("PZ-15234")
    def test_single_live_job(self, live_tester, live_sla):
        """Test: Single Live job complete flow."""
        env = get_environment()
        
        logger.info(f"\n[LIVE] Single Job Flow")
        logger.info(f"    Environment: {env.upper()}")
        
        result = live_tester.run_load_test(
            num_jobs=1,
            concurrent_jobs=1,
            test_name="Single Live Job"
        )
        
        assert result.successful_jobs >= 1, "Single job should succeed"
        assert result.total_frames_received > 0, "Should receive frames"
        
        logger.info(f"✅ Live job completed in {result.avg_total_time_ms:.0f}ms")
    
    @pytest.mark.xray("PZ-15235")  # Load - Live - Job Timing Meets SLA
    @pytest.mark.jira("PZ-15235")
    def test_live_job_timing(self, live_tester, live_sla):
        """Test: Live job timing meets SLA."""
        env = get_environment()
        
        logger.info(f"\n[LIVE] Timing SLA Test")
        
        result = live_tester.run_load_test(
            num_jobs=5,
            concurrent_jobs=2,
            test_name="Live Job Timing"
        )
        
        assert result.error_rate < (100 - live_sla['min_success_rate']), \
            f"Error rate {result.error_rate:.1f}% too high ({env})"
        
        assert result.p95_total_time_ms < live_sla['total_p95_ms'], \
            f"P95 {result.p95_total_time_ms:.0f}ms exceeds {live_sla['total_p95_ms']}ms ({env})"
    
    @pytest.mark.xray("PZ-15236")  # Load - Live - Multiple Concurrent Jobs
    @pytest.mark.jira("PZ-15236")
    def test_concurrent_live_jobs(self, live_tester, live_sla):
        """Test: Multiple concurrent Live jobs."""
        env = get_environment()
        concurrent = 3
        
        logger.info(f"\n[LIVE] Concurrent Jobs Test ({concurrent})")
        
        result = live_tester.run_load_test(
            num_jobs=6,
            concurrent_jobs=concurrent,
            test_name="Concurrent Live Jobs"
        )
        
        success_rate = 100 - result.error_rate
        assert success_rate >= live_sla['min_success_rate'], \
            f"Success rate {success_rate:.1f}% below threshold ({env})"
    
    @pytest.mark.xray("PZ-15237")  # Load - Live - Retry Behavior (gRPC Connection)
    @pytest.mark.jira("PZ-15237")
    def test_live_retry_behavior(self, live_tester, live_sla):
        """Test: Live job retry behavior (Yonatan's feedback)."""
        env = get_environment()
        
        logger.info(f"\n[LIVE] Retry Behavior Test")
        
        result = live_tester.run_load_test(
            num_jobs=5,
            concurrent_jobs=2,
            test_name="Live Retry Behavior"
        )
        
        # Jobs should succeed even with retries
        success_rate = 100 - result.error_rate
        assert success_rate >= live_sla['min_success_rate'], \
            f"Success rate {success_rate:.1f}% too low despite retries ({env})"
        
        assert result.avg_retries_per_job <= live_sla['max_avg_retries'], \
            f"Avg retries {result.avg_retries_per_job:.2f} too high ({env})"


# =============================================================================
# Test Class: Live Heavy Load
# =============================================================================

@pytest.mark.live
@pytest.mark.load
@pytest.mark.job_load
@pytest.mark.heavy
class TestLiveHeavyLoad:
    """Heavy load tests for Live jobs."""
    
    @pytest.mark.xray("PZ-15238")  # Load - Live - Heavy Channel Load (500 Channels)
    @pytest.mark.jira("PZ-15238")
    @pytest.mark.slow
    def test_heavy_channel_live(self, heavy_live_tester, live_sla):
        """Test: Live job with 500 channels."""
        env = get_environment()
        
        logger.info(f"\n[LIVE] Heavy Channel Load (500)")
        
        result = heavy_live_tester.run_load_test(
            num_jobs=3,
            concurrent_jobs=1,
            test_name="Heavy Live (500 channels)"
        )
        
        success_rate = 100 - result.error_rate
        min_required = live_sla['min_success_rate'] - 10
        
        assert success_rate >= min_required, \
            f"Heavy load success rate {success_rate:.1f}% below {min_required}% ({env})"
    
    @pytest.mark.xray("PZ-15239")  # Load - Live - Sustained Load Test
    @pytest.mark.jira("PZ-15239")
    @pytest.mark.slow
    def test_sustained_live_load(self, live_tester, live_sla):
        """Test: Sustained Live job load."""
        env = get_environment()
        
        logger.info(f"\n[LIVE] Sustained Load Test")
        
        result = live_tester.run_load_test(
            num_jobs=10,
            concurrent_jobs=2,
            test_name="Sustained Live Load"
        )
        
        success_rate = 100 - result.error_rate
        assert success_rate >= live_sla['min_success_rate'], \
            f"Sustained success rate {success_rate:.1f}% below threshold ({env})"


# =============================================================================
# Test Class: Live Stress Tests
# =============================================================================

@pytest.mark.live
@pytest.mark.load
@pytest.mark.job_load
@pytest.mark.stress
class TestLiveStress:
    """Stress tests for Live jobs."""
    
    @pytest.mark.xray("PZ-15240")  # Load - Live - Maximum Concurrent Jobs Stress
    @pytest.mark.jira("PZ-15240")
    @pytest.mark.slow
    def test_max_concurrent_live(self, live_tester, live_sla):
        """Test: Maximum concurrent Live jobs."""
        env = get_environment()
        max_concurrent = 5
        
        logger.info(f"\n[LIVE] Max Concurrent Stress ({max_concurrent})")
        
        result = live_tester.run_load_test(
            num_jobs=max_concurrent,
            concurrent_jobs=max_concurrent,
            test_name="Max Concurrent Live"
        )
        
        success_rate = 100 - result.error_rate
        min_required = live_sla['min_success_rate'] - 15
        
        assert success_rate >= min_required, \
            f"Stress success rate {success_rate:.1f}% below {min_required}% ({env})"

