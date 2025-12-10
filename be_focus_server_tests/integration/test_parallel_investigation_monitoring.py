"""
Integration Tests - Parallel Investigation Monitoring
======================================================

Tests that check open investigations in parallel within one thread.

This test suite validates:
    1. Checking status of multiple investigations concurrently
    2. Monitoring investigation lifecycle in parallel
    3. Verifying investigation state transitions
    4. Retrieving metadata for multiple investigations simultaneously

Tests use ThreadPoolExecutor to perform parallel status checks within
a single thread pool, ensuring efficient monitoring of multiple investigations.

Author: QA Automation Team
Date: 2025-12-09
"""

import pytest
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime

from src.apis.focus_server_api import FocusServerAPI
from src.apis.grpc_client import GrpcStreamClient
from src.models.focus_server_models import ConfigureRequest, ViewType
from src.core.exceptions import APIError
from src.infrastructure.kubernetes_manager import KubernetesManager

logger = logging.getLogger(__name__)

# Test configuration
NUM_PARALLEL_INVESTIGATIONS = 10  # Number of investigations to create for parallel monitoring
STATUS_CHECK_INTERVAL = 2  # Seconds between status checks
MAX_MONITORING_TIME = 60  # Maximum time to monitor investigations
PARALLEL_WORKERS = 5  # Number of parallel workers for status checks


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class InvestigationStatus:
    """Status of a single investigation."""
    job_id: str
    status: str = "unknown"
    is_active: bool = False
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    check_time: float = 0.0
    k8s_status: Optional[str] = None


# =============================================================================
# Helper Functions
# =============================================================================

def check_investigation_status(
    focus_server_api: FocusServerAPI,
    job_id: str,
    k8s_manager: Optional[KubernetesManager] = None
) -> InvestigationStatus:
    """
    Check status of a single investigation.
    
    Args:
        focus_server_api: FocusServerAPI instance
        job_id: Job ID to check
        k8s_manager: Optional KubernetesManager for K8s status
        
    Returns:
        InvestigationStatus object with current status
    """
    start_time = time.time()
    status = InvestigationStatus(job_id=job_id)
    
    try:
        # Get metadata from Focus Server API
        metadata = focus_server_api.get_job_metadata(job_id)
        
        if metadata:
            status.metadata = {
                "stream_url": getattr(metadata, 'stream_url', None),
                "stream_port": getattr(metadata, 'stream_port', None),
                "job_id": getattr(metadata, 'job_id', None),
            }
            status.status = "running"
            status.is_active = True
        else:
            status.status = "not_found"
            status.is_active = False
            
    except Exception as e:
        status.error = str(e)
        status.status = "error"
        status.is_active = False
        logger.debug(f"Failed to get metadata for {job_id}: {e}")
    
    # Check K8s status if available
    if k8s_manager:
        try:
            namespace = k8s_manager.k8s_config.get("namespace", "panda")
            jobs = k8s_manager.get_jobs(namespace)
            
            # Find job in K8s
            k8s_job_name = f"grpc-job-{job_id}"
            for job in jobs:
                if job.get("name", "").startswith(k8s_job_name):
                    status.k8s_status = job.get("status", "unknown")
                    break
                    
        except Exception as e:
            logger.debug(f"Failed to get K8s status for {job_id}: {e}")
    
    status.check_time = (time.time() - start_time) * 1000  # Convert to ms
    return status


def check_multiple_investigations_parallel(
    focus_server_api: FocusServerAPI,
    job_ids: List[str],
    k8s_manager: Optional[KubernetesManager] = None,
    max_workers: int = PARALLEL_WORKERS
) -> List[InvestigationStatus]:
    """
    Check status of multiple investigations in parallel.
    
    Args:
        focus_server_api: FocusServerAPI instance
        job_ids: List of job IDs to check
        k8s_manager: Optional KubernetesManager for K8s status
        max_workers: Maximum number of parallel workers
        
    Returns:
        List of InvestigationStatus objects
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all status check tasks
        futures = {
            executor.submit(check_investigation_status, focus_server_api, job_id, k8s_manager): job_id
            for job_id in job_ids
        }
        
        # Collect results as they complete
        for future in as_completed(futures):
            job_id = futures[future]
            try:
                status = future.result()
                results.append(status)
                logger.debug(f"Status check complete for {job_id}: {status.status}")
            except Exception as e:
                logger.error(f"Status check failed for {job_id}: {e}")
                results.append(InvestigationStatus(
                    job_id=job_id,
                    status="error",
                    error=str(e),
                    is_active=False
                ))
    
    return results


def monitor_investigation_lifecycle(
    focus_server_api: FocusServerAPI,
    job_id: str,
    max_duration: int = 30,
    check_interval: int = 2
) -> List[InvestigationStatus]:
    """
    Monitor an investigation's lifecycle over time.
    
    Args:
        focus_server_api: FocusServerAPI instance
        job_id: Job ID to monitor
        max_duration: Maximum monitoring duration in seconds
        check_interval: Interval between checks in seconds
        
    Returns:
        List of InvestigationStatus snapshots over time
    """
    snapshots = []
    start_time = time.time()
    
    while time.time() - start_time < max_duration:
        status = check_investigation_status(focus_server_api, job_id)
        snapshots.append(status)
        
        logger.debug(
            f"Lifecycle snapshot for {job_id}: "
            f"status={status.status}, active={status.is_active}, "
            f"elapsed={time.time() - start_time:.1f}s"
        )
        
        # If investigation is no longer active, stop monitoring
        if not status.is_active and status.status != "running":
            logger.info(f"Investigation {job_id} is no longer active, stopping monitoring")
            break
        
        time.sleep(check_interval)
    
    return snapshots


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def live_investigation_config() -> Dict[str, Any]:
    """Standard configuration for live investigation."""
    return {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 1, "max": 50},
        "frequencyRange": {"min": 0, "max": 1000},
        "start_time": None,  # Live mode
        "end_time": None,
        "view_type": ViewType.MULTICHANNEL
    }


# =============================================================================
# Test Class: Parallel Investigation Monitoring
# =============================================================================

@pytest.mark.integration
@pytest.mark.load
@pytest.mark.parallel
class TestParallelInvestigationMonitoring:
    """
    Test suite for parallel investigation monitoring.
    
    These tests validate:
    - Checking multiple investigation statuses in parallel
    - Monitoring investigation lifecycle concurrently
    - Verifying state transitions
    - Retrieving metadata in parallel
    """
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    def test_check_open_investigations_parallel(
        self,
        focus_server_api: FocusServerAPI,
        config_manager,
        live_investigation_config: Dict[str, Any],
        auto_cleanup_jobs
    ):
        """
        Test: Check status of multiple open investigations in parallel.
        
        Objective:
            Verify that we can check the status of multiple investigations
            concurrently using ThreadPoolExecutor within one thread.
        
        Steps:
            1. Create multiple investigations
            2. Check their status in parallel
            3. Verify all status checks complete successfully
            4. Validate response times are reasonable
        
        Expected:
            - All investigations are created successfully
            - Parallel status checks complete faster than sequential
            - All status information is accurate
        """
        logger.info("=" * 80)
        logger.info("TEST: Check Open Investigations in Parallel")
        logger.info("=" * 80)
        
        num_investigations = NUM_PARALLEL_INVESTIGATIONS
        created_jobs = []
        
        try:
            # =========================================================
            # PHASE 1: Create Multiple Investigations
            # =========================================================
            logger.info(f"\nPHASE 1: Creating {num_investigations} investigations...")
            
            for i in range(num_investigations):
                try:
                    config_request = ConfigureRequest(**live_investigation_config)
                    response = focus_server_api.configure_streaming_job(config_request)
                    
                    if response and response.job_id:
                        created_jobs.append(response.job_id)
                        logger.info(f"  ✅ Created investigation {i+1}/{num_investigations}: {response.job_id}")
                    else:
                        logger.warning(f"  ⚠️  Failed to create investigation {i+1}/{num_investigations}")
                        
                except Exception as e:
                    logger.error(f"  ❌ Error creating investigation {i+1}: {e}")
            
            logger.info(f"\n✅ Created {len(created_jobs)}/{num_investigations} investigations")
            
            assert len(created_jobs) >= num_investigations * 0.7, \
                f"At least 70% of investigations should be created, got {len(created_jobs)}/{num_investigations}"
            
            # Wait for jobs to start
            logger.info("\nWaiting 5s for jobs to start...")
            time.sleep(5)
            
            # =========================================================
            # PHASE 2: Check Status in Parallel
            # =========================================================
            logger.info(f"\nPHASE 2: Checking status of {len(created_jobs)} investigations in parallel...")
            
            # Initialize K8s manager if available
            k8s_manager = None
            try:
                k8s_manager = KubernetesManager(config_manager)
                logger.info("✅ K8s manager initialized for status checks")
            except Exception as e:
                logger.warning(f"⚠️  K8s manager not available: {e}")
            
            # Parallel status check
            parallel_start = time.time()
            statuses = check_multiple_investigations_parallel(
                focus_server_api=focus_server_api,
                job_ids=created_jobs,
                k8s_manager=k8s_manager,
                max_workers=PARALLEL_WORKERS
            )
            parallel_duration = time.time() - parallel_start
            
            logger.info(f"\n✅ Parallel status check completed in {parallel_duration:.2f}s")
            
            # =========================================================
            # PHASE 3: Analyze Results
            # =========================================================
            logger.info(f"\nPHASE 3: Analyzing results...")
            
            active_count = sum(1 for s in statuses if s.is_active)
            error_count = sum(1 for s in statuses if s.error)
            avg_check_time = sum(s.check_time for s in statuses) / len(statuses) if statuses else 0
            
            logger.info(f"\nResults Summary:")
            logger.info(f"  Total investigations: {len(created_jobs)}")
            logger.info(f"  Status checks completed: {len(statuses)}")
            logger.info(f"  Active investigations: {active_count}")
            logger.info(f"  Errors: {error_count}")
            logger.info(f"  Parallel check duration: {parallel_duration:.2f}s")
            logger.info(f"  Average check time per investigation: {avg_check_time:.1f}ms")
            
            # Log status breakdown
            status_breakdown = {}
            for s in statuses:
                status_breakdown[s.status] = status_breakdown.get(s.status, 0) + 1
            
            logger.info(f"\nStatus Breakdown:")
            for status, count in status_breakdown.items():
                logger.info(f"  {status}: {count}")
            
            # =========================================================
            # PHASE 4: Verify Parallel Efficiency
            # =========================================================
            logger.info(f"\nPHASE 4: Verifying parallel efficiency...")
            
            # Estimate sequential time (sum of all check times)
            estimated_sequential_time = sum(s.check_time for s in statuses) / 1000  # Convert to seconds
            
            logger.info(f"  Estimated sequential time: {estimated_sequential_time:.2f}s")
            logger.info(f"  Actual parallel time: {parallel_duration:.2f}s")
            
            if estimated_sequential_time > 0:
                speedup = estimated_sequential_time / parallel_duration
                logger.info(f"  Speedup: {speedup:.2f}x")
                
                # Parallel should be faster than sequential
                assert parallel_duration < estimated_sequential_time, \
                    f"Parallel check ({parallel_duration:.2f}s) should be faster than sequential ({estimated_sequential_time:.2f}s)"
            
            # =========================================================
            # Assertions
            # =========================================================
            assert len(statuses) == len(created_jobs), \
                f"Should get status for all jobs, got {len(statuses)}/{len(created_jobs)}"
            
            assert active_count > 0, \
                "At least some investigations should be active"
            
            logger.info("\n✅ TEST PASSED: Parallel investigation monitoring successful!")
            
        finally:
            # Cleanup
            if created_jobs:
                logger.info(f"\nCleaning up {len(created_jobs)} investigations...")
                cleanup_start = time.time()
                
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = {
                        executor.submit(focus_server_api.cancel_job, job_id): job_id
                        for job_id in created_jobs
                    }
                    
                    canceled = 0
                    for future in as_completed(futures):
                        try:
                            future.result()
                            canceled += 1
                        except Exception as e:
                            logger.debug(f"Cleanup error: {e}")
                
                cleanup_time = time.time() - cleanup_start
                logger.info(f"✅ Cleanup completed: {canceled}/{len(created_jobs)} jobs canceled in {cleanup_time:.2f}s")
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    def test_monitor_investigation_status_changes(
        self,
        focus_server_api: FocusServerAPI,
        live_investigation_config: Dict[str, Any],
        auto_cleanup_jobs
    ):
        """
        Test: Monitor status changes of multiple investigations over time.
        
        Objective:
            Verify that we can monitor the lifecycle of multiple investigations
            in parallel, tracking their state transitions.
        
        Steps:
            1. Create multiple investigations
            2. Monitor their status changes over time in parallel
            3. Verify state transitions are captured
            4. Validate monitoring completes within expected time
        
        Expected:
            - All investigations start in "running" state
            - Status changes are captured accurately
            - Parallel monitoring is efficient
        """
        logger.info("=" * 80)
        logger.info("TEST: Monitor Investigation Status Changes")
        logger.info("=" * 80)
        
        num_investigations = 3  # Smaller number for lifecycle monitoring
        created_jobs = []
        
        try:
            # Create investigations
            logger.info(f"\nCreating {num_investigations} investigations...")
            
            for i in range(num_investigations):
                try:
                    config_request = ConfigureRequest(**live_investigation_config)
                    response = focus_server_api.configure_streaming_job(config_request)
                    
                    if response and response.job_id:
                        created_jobs.append(response.job_id)
                        logger.info(f"  ✅ Created investigation {i+1}: {response.job_id}")
                        
                except Exception as e:
                    logger.error(f"  ❌ Error creating investigation {i+1}: {e}")
            
            logger.info(f"\n✅ Created {len(created_jobs)} investigations")
            
            # Wait for jobs to start
            time.sleep(3)
            
            # Monitor lifecycle in parallel
            logger.info(f"\nMonitoring lifecycle of {len(created_jobs)} investigations...")
            
            all_snapshots = {}
            
            with ThreadPoolExecutor(max_workers=len(created_jobs)) as executor:
                futures = {
                    executor.submit(
                        monitor_investigation_lifecycle,
                        focus_server_api,
                        job_id,
                        max_duration=20,
                        check_interval=2
                    ): job_id
                    for job_id in created_jobs
                }
                
                for future in as_completed(futures):
                    job_id = futures[future]
                    try:
                        snapshots = future.result()
                        all_snapshots[job_id] = snapshots
                        logger.info(f"  ✅ Monitoring complete for {job_id}: {len(snapshots)} snapshots")
                    except Exception as e:
                        logger.error(f"  ❌ Monitoring failed for {job_id}: {e}")
            
            # Analyze snapshots
            logger.info(f"\nLifecycle Analysis:")
            
            for job_id, snapshots in all_snapshots.items():
                logger.info(f"\n  Job {job_id}:")
                logger.info(f"    Total snapshots: {len(snapshots)}")
                
                if snapshots:
                    statuses = [s.status for s in snapshots]
                    unique_statuses = set(statuses)
                    logger.info(f"    Statuses observed: {unique_statuses}")
                    logger.info(f"    Initial status: {snapshots[0].status}")
                    logger.info(f"    Final status: {snapshots[-1].status}")
                    
                    # Check for state transitions
                    transitions = []
                    for i in range(1, len(snapshots)):
                        if snapshots[i].status != snapshots[i-1].status:
                            transitions.append(
                                f"{snapshots[i-1].status} -> {snapshots[i].status}"
                            )
                    
                    if transitions:
                        logger.info(f"    State transitions: {transitions}")
                    else:
                        logger.info(f"    State transitions: None (stable)")
            
            # Assertions
            assert len(all_snapshots) > 0, "Should have monitoring data for at least one investigation"
            
            for job_id, snapshots in all_snapshots.items():
                assert len(snapshots) > 0, f"Should have at least one snapshot for {job_id}"
            
            logger.info("\n✅ TEST PASSED: Investigation lifecycle monitoring successful!")
            
        finally:
            # Cleanup
            if created_jobs:
                logger.info(f"\nCleaning up {len(created_jobs)} investigations...")
                for job_id in created_jobs:
                    try:
                        focus_server_api.cancel_job(job_id)
                    except Exception as e:
                        logger.debug(f"Cleanup error for {job_id}: {e}")
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    def test_concurrent_status_checks(
        self,
        focus_server_api: FocusServerAPI,
        live_investigation_config: Dict[str, Any],
        auto_cleanup_jobs
    ):
        """
        Test: Verify concurrent status checks don't interfere with each other.
        
        Objective:
            Ensure that checking the same investigation's status multiple times
            concurrently returns consistent results.
        
        Steps:
            1. Create a single investigation
            2. Check its status multiple times concurrently
            3. Verify all checks return consistent results
        
        Expected:
            - All concurrent checks complete successfully
            - Results are consistent across all checks
        """
        logger.info("=" * 80)
        logger.info("TEST: Concurrent Status Checks")
        logger.info("=" * 80)
        
        job_id = None
        
        try:
            # Create investigation
            logger.info("\nCreating investigation...")
            config_request = ConfigureRequest(**live_investigation_config)
            response = focus_server_api.configure_streaming_job(config_request)
            
            assert response and response.job_id, "Investigation creation failed"
            job_id = response.job_id
            logger.info(f"✅ Created investigation: {job_id}")
            
            # Wait for job to start
            time.sleep(3)
            
            # Perform concurrent status checks
            num_checks = 20
            logger.info(f"\nPerforming {num_checks} concurrent status checks...")
            
            statuses = []
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(check_investigation_status, focus_server_api, job_id)
                    for _ in range(num_checks)
                ]
                
                for future in as_completed(futures):
                    try:
                        status = future.result()
                        statuses.append(status)
                    except Exception as e:
                        logger.error(f"Status check failed: {e}")
            
            logger.info(f"✅ Completed {len(statuses)}/{num_checks} status checks")
            
            # Analyze consistency
            logger.info(f"\nConsistency Analysis:")
            
            status_values = [s.status for s in statuses]
            unique_statuses = set(status_values)
            
            logger.info(f"  Total checks: {len(statuses)}")
            logger.info(f"  Unique statuses: {unique_statuses}")
            
            for status_val in unique_statuses:
                count = status_values.count(status_val)
                percentage = (count / len(statuses)) * 100
                logger.info(f"    {status_val}: {count} ({percentage:.1f}%)")
            
            # Check times
            check_times = [s.check_time for s in statuses]
            avg_check_time = sum(check_times) / len(check_times) if check_times else 0
            min_check_time = min(check_times) if check_times else 0
            max_check_time = max(check_times) if check_times else 0
            
            logger.info(f"\nCheck Times:")
            logger.info(f"  Average: {avg_check_time:.1f}ms")
            logger.info(f"  Min: {min_check_time:.1f}ms")
            logger.info(f"  Max: {max_check_time:.1f}ms")
            
            # Assertions
            assert len(statuses) == num_checks, \
                f"All status checks should complete, got {len(statuses)}/{num_checks}"
            
            # Most checks should return the same status (allowing for some variation during transitions)
            most_common_status = max(set(status_values), key=status_values.count)
            most_common_count = status_values.count(most_common_status)
            consistency_rate = (most_common_count / len(statuses)) * 100
            
            logger.info(f"\nConsistency Rate: {consistency_rate:.1f}%")
            
            assert consistency_rate >= 80, \
                f"At least 80% of checks should return the same status, got {consistency_rate:.1f}%"
            
            logger.info("\n✅ TEST PASSED: Concurrent status checks are consistent!")
            
        finally:
            # Cleanup
            if job_id:
                try:
                    focus_server_api.cancel_job(job_id)
                    logger.info(f"\n✅ Cleaned up investigation: {job_id}")
                except Exception as e:
                    logger.debug(f"Cleanup error: {e}")


# =============================================================================
# Summary Test
# =============================================================================

@pytest.mark.summary
@pytest.mark.skip(reason="Documentation only - no executable assertions")
def test_parallel_monitoring_summary():
    """
    Summary test for parallel investigation monitoring.
    
    Tests Covered:
        - Checking multiple investigations in parallel
        - Monitoring investigation lifecycle
        - Concurrent status checks
    
    Key Validations:
        - Parallel status checks are faster than sequential
        - Investigation state transitions are captured
        - Concurrent checks return consistent results
    
    NOTE: This test is skipped - it's documentation only.
    Real tests are in the class above.
    """
    logger.info("=" * 80)
    logger.info("Parallel Investigation Monitoring Tests Suite Summary")
    logger.info("=" * 80)
    logger.info("Tests in this module:")
    logger.info("  1. Check Open Investigations in Parallel")
    logger.info("  2. Monitor Investigation Status Changes")
    logger.info("  3. Concurrent Status Checks")
    logger.info("")
    logger.info("Key Validations:")
    logger.info("  ✅ Parallel status checks are faster than sequential")
    logger.info("  ✅ Investigation state transitions are captured")
    logger.info("  ✅ Concurrent checks return consistent results")
    logger.info("=" * 80)
