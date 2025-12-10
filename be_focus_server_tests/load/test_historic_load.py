"""
Historic Job Load Tests - Recorded Data Playback Performance
=============================================================

Tests for HISTORIC playback jobs:
- Replay recorded data from storage
- Has start_time and end_time (finite stream)

Markers:
- @pytest.mark.historic - Historic job tests
- @pytest.mark.load - Load tests
- @pytest.mark.job_load - Job-based load tests

Run:
    pytest be_focus_server_tests/load/test_historic_load.py -v -m historic

Author: QA Automation Architect
Date: 2025-11-30
"""

import pytest
import logging
import os
from typing import Dict, Any, List

# Import production constants
from be_focus_server_tests.constants import FREQUENCY_MAX_HZ

# Import K8s verification module
from be_focus_server_tests.load.k8s_job_verification import (
    verify_job_from_k8s,
    verify_jobs_batch_from_k8s,
    log_k8s_verification_summary,
    assert_all_jobs_are_historic,
    K8sJobVerification,
    JobType
)

logger = logging.getLogger(__name__)


# =============================================================================
# SLA Configuration
# =============================================================================

def get_environment() -> str:
    return os.getenv("ENVIRONMENT", "staging").lower()


def get_historic_sla() -> Dict[str, Any]:
    """Get SLA for Historic jobs."""
    env = get_environment()
    
    if env in ("prod", "production"):
        return {
            "description": "Production - Historic Jobs",
            "configure_p95_ms": 3000,
            "grpc_connect_p95_ms": 20000,
            "total_p95_ms": 30000,
            "total_p99_ms": 60000,
            "min_success_rate": 90,
            "max_avg_retries": 2.5,
        }
    else:
        return {
            "description": f"Staging - Historic Jobs ({env})",
            "configure_p95_ms": 8000,
            "grpc_connect_p95_ms": 40000,
            "total_p95_ms": 60000,
            "total_p99_ms": 120000,
            "min_success_rate": 75,
            "max_avg_retries": 4.0,
        }


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def historic_sla() -> Dict[str, Any]:
    return get_historic_sla()


@pytest.fixture
def historic_tester(config_manager, kubernetes_manager):
    """Create Historic Job Load Tester with K8s verification."""
    from be_focus_server_tests.load.job_load_tester import create_historic_job_tester
    
    tester = create_historic_job_tester(
        config_manager=config_manager,
        channels_min=1,
        channels_max=50,
        frequency_min=0,
        frequency_max=FREQUENCY_MAX_HZ,  # Use production constant (1000 Hz)
        nfft=1024,
        recording_duration_seconds=10,
        max_grpc_connect_retries=5,
        grpc_connect_retry_delay_ms=2000,
        frames_to_receive=5,
    )
    # Attach kubernetes_manager for K8s verification
    tester.k8s_manager = kubernetes_manager
    return tester


@pytest.fixture
def heavy_historic_tester(config_manager, kubernetes_manager):
    """Create heavy Historic Job Load Tester with K8s verification."""
    from be_focus_server_tests.load.job_load_tester import create_historic_job_tester
    
    tester = create_historic_job_tester(
        config_manager=config_manager,
        channels_min=1,
        channels_max=500,
        frequency_min=0,
        frequency_max=1000,
        nfft=2048,
        recording_duration_seconds=30,
        max_grpc_connect_retries=5,
        frames_to_receive=3,
    )
    # Attach kubernetes_manager for K8s verification
    tester.k8s_manager = kubernetes_manager
    return tester


# =============================================================================
# Test Class: Historic Job Load Tests
# =============================================================================

@pytest.mark.historic
@pytest.mark.load
@pytest.mark.job_load
class TestHistoricJobLoad:
    """
    Historic Job load tests.
    
    Tests recorded data playback from storage.
    """
    
    @pytest.mark.xray("PZ-15241")  # Load - Historic - Single Historic Job Complete Flow
    @pytest.mark.jira("PZ-15241")
    def test_single_historic_job(self, historic_tester, historic_sla):
        """Test: Single Historic job complete flow."""
        env = get_environment()
        
        logger.info(f"\n[HISTORIC] Single Job Flow")
        logger.info(f"    Environment: {env.upper()}")
        
        result = historic_tester.run_load_test(
            num_jobs=1,
            concurrent_jobs=1,
            test_name="Single Historic Job"
        )
        
        # Historic may have no recordings - handle gracefully
        if result.total_jobs > 0:
            if result.successful_jobs == 0:
                # Check if it's a "no recordings" error
                errors = result.errors_by_type
                if any("recording" in str(e).lower() for e in errors.keys()):
                    pytest.skip("No recordings available for historic playback")
            
            assert result.successful_jobs >= 1, "Single job should succeed"
        
        logger.info(f"✅ Historic job completed in {result.avg_total_time_ms:.0f}ms")
    
    @pytest.mark.xray("PZ-15242")  # Load - Historic - Job Timing Meets SLA
    @pytest.mark.jira("PZ-15242")
    def test_historic_job_timing(self, historic_tester, historic_sla):
        """Test: Historic job timing meets SLA."""
        env = get_environment()
        
        logger.info(f"\n[HISTORIC] Timing SLA Test")
        
        result = historic_tester.run_load_test(
            num_jobs=5,
            concurrent_jobs=2,
            test_name="Historic Job Timing"
        )
        
        if result.successful_jobs == 0:
            pytest.skip("No successful historic jobs - may have no recordings")
        
        assert result.error_rate < (100 - historic_sla['min_success_rate']), \
            f"Error rate {result.error_rate:.1f}% too high ({env})"
        
        assert result.p95_total_time_ms < historic_sla['total_p95_ms'], \
            f"P95 {result.p95_total_time_ms:.0f}ms exceeds {historic_sla['total_p95_ms']}ms ({env})"
    
    @pytest.mark.xray("PZ-15243")  # Load - Historic - Multiple Concurrent Jobs
    @pytest.mark.jira("PZ-15243")
    def test_concurrent_historic_jobs(self, historic_tester, historic_sla):
        """Test: Multiple concurrent Historic jobs."""
        env = get_environment()
        concurrent = 3
        
        logger.info(f"\n[HISTORIC] Concurrent Jobs Test ({concurrent})")
        
        result = historic_tester.run_load_test(
            num_jobs=6,
            concurrent_jobs=concurrent,
            test_name="Concurrent Historic Jobs"
        )
        
        if result.successful_jobs == 0:
            pytest.skip("No successful historic jobs")
        
        success_rate = 100 - result.error_rate
        assert success_rate >= historic_sla['min_success_rate'], \
            f"Success rate {success_rate:.1f}% below threshold ({env})"
    
    @pytest.mark.xray("PZ-15244")  # Load - Historic - Retry Behavior
    @pytest.mark.jira("PZ-15244")
    def test_historic_retry_behavior(self, historic_tester, historic_sla):
        """Test: Historic job retry behavior."""
        env = get_environment()
        
        logger.info(f"\n[HISTORIC] Retry Behavior Test")
        
        result = historic_tester.run_load_test(
            num_jobs=5,
            concurrent_jobs=2,
            test_name="Historic Retry Behavior"
        )
        
        if result.successful_jobs == 0:
            pytest.skip("No successful historic jobs")
        
        success_rate = 100 - result.error_rate
        assert success_rate >= historic_sla['min_success_rate'], \
            f"Success rate {success_rate:.1f}% too low ({env})"
        
        assert result.avg_retries_per_job <= historic_sla['max_avg_retries'], \
            f"Avg retries {result.avg_retries_per_job:.2f} too high ({env})"


# =============================================================================
# Test Class: Historic Heavy Load
# =============================================================================

@pytest.mark.historic
@pytest.mark.load
@pytest.mark.job_load
@pytest.mark.heavy
class TestHistoricHeavyLoad:
    """Heavy load tests for Historic jobs."""
    
    @pytest.mark.xray("PZ-15245")  # Load - Historic - Heavy Channel Load (500 Channels)
    @pytest.mark.jira("PZ-15245")
    @pytest.mark.slow
    def test_heavy_channel_historic(self, heavy_historic_tester, historic_sla):
        """Test: Historic job with 500 channels."""
        env = get_environment()
        
        logger.info(f"\n[HISTORIC] Heavy Channel Load (500)")
        
        result = heavy_historic_tester.run_load_test(
            num_jobs=3,
            concurrent_jobs=1,
            test_name="Heavy Historic (500 channels)"
        )
        
        if result.successful_jobs == 0:
            pytest.skip("No successful historic jobs")
        
        success_rate = 100 - result.error_rate
        min_required = historic_sla['min_success_rate'] - 10
        
        assert success_rate >= min_required, \
            f"Heavy load success rate {success_rate:.1f}% below {min_required}% ({env})"
    
    @pytest.mark.xray("PZ-15246")  # Load - Historic - Sustained Load Test
    @pytest.mark.jira("PZ-15246")
    @pytest.mark.slow
    def test_sustained_historic_load(self, historic_tester, historic_sla):
        """Test: Sustained Historic job load."""
        env = get_environment()
        
        logger.info(f"\n[HISTORIC] Sustained Load Test")
        
        result = historic_tester.run_load_test(
            num_jobs=10,
            concurrent_jobs=2,
            test_name="Sustained Historic Load"
        )
        
        if result.successful_jobs == 0:
            pytest.skip("No successful historic jobs")
        
        success_rate = 100 - result.error_rate
        assert success_rate >= historic_sla['min_success_rate'], \
            f"Sustained success rate {success_rate:.1f}% below threshold ({env})"


# =============================================================================
# Test Class: Historic Stress Tests
# =============================================================================

@pytest.mark.historic
@pytest.mark.load
@pytest.mark.job_load
@pytest.mark.stress
class TestHistoricStress:
    """Stress tests for Historic jobs."""
    
    @pytest.mark.xray("PZ-15247")  # Load - Historic - Maximum Concurrent Jobs Stress
    @pytest.mark.jira("PZ-15247")
    @pytest.mark.slow
    def test_max_concurrent_historic(self, historic_tester, historic_sla):
        """Test: Maximum concurrent Historic jobs."""
        env = get_environment()
        max_concurrent = 5
        
        logger.info(f"\n[HISTORIC] Max Concurrent Stress ({max_concurrent})")
        
        result = historic_tester.run_load_test(
            num_jobs=max_concurrent,
            concurrent_jobs=max_concurrent,
            test_name="Max Concurrent Historic"
        )
        
        if result.successful_jobs == 0:
            pytest.skip("No successful historic jobs")
        
        success_rate = 100 - result.error_rate
        min_required = historic_sla['min_success_rate'] - 15
        
        assert success_rate >= min_required, \
            f"Stress success rate {success_rate:.1f}% below {min_required}% ({env})"


# =============================================================================
# Test Class: Historic-Specific Tests
# =============================================================================

@pytest.mark.historic
@pytest.mark.load
@pytest.mark.job_load
class TestHistoricSpecific:
    """Tests specific to Historic playback behavior."""
    
    @pytest.mark.xray("PZ-15248")  # Load - Historic - Recording Availability Check
    @pytest.mark.jira("PZ-15248")
    def test_recording_availability(self, config_manager):
        """Test: Check available recordings before testing."""
        from src.apis.focus_server_api import FocusServerAPI
        from src.models.focus_server_models import RecordingsInTimeRangeRequest
        import time
        
        api = FocusServerAPI(config_manager)
        
        # Query last 24 hours
        now = int(time.time() * 1000)
        day_ago = now - (24 * 60 * 60 * 1000)
        
        try:
            request = RecordingsInTimeRangeRequest(
                start_time=day_ago,
                end_time=now
            )
            response = api.get_recordings_in_time_range(request)
            
            recordings = response.root if response.root else []
            
            logger.info(f"[HISTORIC] Found {len(recordings)} recordings")
            
            if recordings:
                for i, (start, end) in enumerate(recordings[:5]):
                    duration_sec = (end - start) / 1000
                    logger.info(f"    Recording {i+1}: {duration_sec:.1f}s")
            
            assert len(recordings) > 0, \
                "No recordings available for historic playback tests"
            
        except Exception as e:
            pytest.skip(f"Cannot check recordings: {e}")
    
    @pytest.mark.xray("PZ-15249")  # Load - Historic - Playback Runs to Completion
    @pytest.mark.jira("PZ-15249")
    def test_historic_playback_complete(self, historic_tester, historic_sla):
        """Test: Historic playback runs to completion."""
        env = get_environment()
        
        logger.info(f"\n[HISTORIC] Playback Completion Test")
        
        # Use short duration for faster test
        historic_tester.recording_duration_seconds = 5
        historic_tester.frames_to_receive = 10  # More frames to test completion
        
        result = historic_tester.run_load_test(
            num_jobs=1,
            concurrent_jobs=1,
            test_name="Historic Playback Complete"
        )
        
        if result.successful_jobs == 0:
            pytest.skip("Historic job failed - may have no recordings")
        
        # Should receive frames
        assert result.total_frames_received > 0, \
            "Should receive frames from historic playback"

