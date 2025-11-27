"""
Pytest Configuration for Performance Tests
===========================================

Fixtures and configuration specific to performance testing,
including automatic job cleanup with system cleanup verification.
"""

import pytest
import logging
import time
from typing import List, Set, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# Module-level set to track job IDs created during test execution
_job_ids_created: Set[str] = set()

# Cleanup configuration
AUTO_CLEANUP_WAIT_TIME = 180  # Wait 3 minutes for system cleanup (max time from docs)
AUTO_CLEANUP_CHECK_INTERVAL = 10  # Check every 10 seconds


@pytest.fixture(scope="function", autouse=True)
def auto_cleanup_jobs(focus_server_api, request):
    """
    Automatic cleanup fixture for performance tests with system cleanup verification.
    
    This fixture:
    1. Tracks all job IDs created during test execution
    2. Attempts API cancellation (if available)
    3. Waits for system automatic cleanup (up to 3 minutes)
    4. Verifies jobs are cleaned up by the system
    5. Only performs aggressive K8s deletion if system cleanup failed
    6. Logs cleanup status for test results
    
    Args:
        focus_server_api: Focus Server API instance
        request: Pytest request object (for accessing fixtures)
        
    Usage:
        No need to use this fixture explicitly - it runs automatically.
        Just create jobs normally and they will be cleaned up automatically.
    """
    global _job_ids_created
    
    # Clear job IDs for this test
    test_job_ids: List[str] = []
    
    # Monkey patch configure_streaming_job to track job IDs
    original_configure = focus_server_api.configure_streaming_job
    
    def tracked_configure(*args, **kwargs):
        """Track job creation and return response."""
        response = original_configure(*args, **kwargs)
        if response and hasattr(response, 'job_id') and response.job_id:
            job_id = response.job_id
            test_job_ids.append(job_id)
            _job_ids_created.add(job_id)
            logger.debug(f"Auto-tracked job: {job_id}")
        return response
    
    # Replace method temporarily
    focus_server_api.configure_streaming_job = tracked_configure
    
    # Yield control to test
    yield
    
    # Restore original method
    focus_server_api.configure_streaming_job = original_configure
    
    # Cleanup all tracked jobs with system cleanup verification
    if test_job_ids:
        logger.info(f"\n{'='*80}")
        logger.info(f"Auto-cleanup: Starting cleanup for {len(test_job_ids)} jobs...")
        logger.info(f"{'='*80}")
        
        cleanup_start = time.time()
        
        # Step 1: Try API cancellation (if available)
        logger.info("Step 1: Attempting API cancellation...")
        api_canceled_count = 0
        api_failed_count = 0
        
        def cancel_job_safe(job_id: str) -> tuple[bool, bool]:
            """Cancel a single job safely via API."""
            try:
                focus_server_api.cancel_job(job_id)
                logger.debug(f"API canceled job: {job_id}")
                return True, True  # (success, api_worked)
            except Exception as e:
                if "404" in str(e):
                    logger.debug(f"API cancellation not available for job {job_id} (404)")
                    return False, False  # (success=False, api_worked=False - expected)
                else:
                    logger.warning(f"API cancellation failed for job {job_id}: {e}")
                    return False, True  # (success=False, api_worked=True - unexpected error)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(cancel_job_safe, job_id): job_id 
                      for job_id in test_job_ids}
            
            for future in as_completed(futures):
                success, api_worked = future.result()
                if success:
                    api_canceled_count += 1
                elif api_worked:
                    api_failed_count += 1
        
        logger.info(f"  API cancellation: {api_canceled_count} succeeded, {api_failed_count} failed, "
                   f"{len(test_job_ids) - api_canceled_count - api_failed_count} not supported")
        
        # Step 2: Wait for system automatic cleanup
        logger.info(f"\nStep 2: Waiting for system automatic cleanup (up to {AUTO_CLEANUP_WAIT_TIME}s)...")
        logger.info("  This verifies that the system's cleanup mechanism works correctly.")
        
        # Try to get k8s_manager if available (optional)
        k8s_manager = None
        try:
            k8s_manager = request.getfixturevalue("k8s_manager")
        except:
            try:
                # Try to create k8s_manager if config_manager is available
                config_manager = request.getfixturevalue("config_manager")
                from src.infrastructure.kubernetes_manager import KubernetesManager
                k8s_manager = KubernetesManager(config_manager)
            except:
                logger.debug("K8s manager not available - will skip K8s verification")
        
        # Wait and check if jobs are cleaned up
        wait_start = time.time()
        remaining_jobs = set(test_job_ids)
        checks_performed = 0
        
        while time.time() - wait_start < AUTO_CLEANUP_WAIT_TIME and remaining_jobs:
            time.sleep(AUTO_CLEANUP_CHECK_INTERVAL)
            checks_performed += 1
            
            # Check which jobs still exist in K8s (if k8s_manager available)
            if k8s_manager:
                still_existing = []
                for job_id in list(remaining_jobs):
                    try:
                        # Check if grpc-job exists (job name format: grpc-job-{job_id})
                        jobs = k8s_manager.get_jobs()
                        job_name_prefix = f"grpc-job-{job_id}"
                        # Job name might have suffix, so check if it starts with prefix
                        if any(j.get("name", "").startswith(job_name_prefix) for j in jobs):
                            still_existing.append(job_id)
                    except Exception as e:
                        # If we can't check, assume it still exists
                        logger.debug(f"Could not check job {job_id} existence: {e}")
                        still_existing.append(job_id)
                
                remaining_jobs = set(still_existing)
                
                if remaining_jobs:
                    logger.debug(f"  Check {checks_performed}: {len(remaining_jobs)} jobs still exist")
                else:
                    logger.info(f"  ✅ All jobs cleaned up by system after {time.time() - wait_start:.1f}s")
                    break
            else:
                # Without K8s manager, we can't verify - just wait
                elapsed = time.time() - wait_start
                logger.debug(f"  Check {checks_performed}: Waiting... ({elapsed:.1f}s elapsed)")
        
        wait_time = time.time() - wait_start
        
        # Step 3: Aggressive cleanup if jobs still exist
        if remaining_jobs:
            logger.warning(f"\n⚠️  Step 3: System cleanup FAILED - {len(remaining_jobs)} jobs still exist after {wait_time:.1f}s")
            logger.warning("  This indicates a problem with the system's automatic cleanup mechanism!")
            logger.warning("  Performing aggressive cleanup via Kubernetes...")
            
            if k8s_manager:
                aggressive_cleanup_count = 0
                aggressive_failed_count = 0
                
                for job_id in remaining_jobs:
                    try:
                        # Delete grpc-job
                        if k8s_manager.delete_job(f"grpc-job-{job_id}"):
                            aggressive_cleanup_count += 1
                            logger.debug(f"  Deleted grpc-job-{job_id}")
                        
                        # Delete cleanup-job
                        try:
                            k8s_manager.delete_job(f"cleanup-job-{job_id}")
                        except:
                            pass  # cleanup-job might not exist
                        
                    except Exception as e:
                        aggressive_failed_count += 1
                        logger.error(f"  Failed to delete job {job_id} via K8s: {e}")
                
                logger.warning(f"  Aggressive cleanup: {aggressive_cleanup_count} deleted, {aggressive_failed_count} failed")
            else:
                logger.error("  Cannot perform aggressive cleanup - K8s manager not available")
                logger.error(f"  Manual cleanup required for {len(remaining_jobs)} jobs: {list(remaining_jobs)}")
        else:
            logger.info(f"\n✅ Step 3: System cleanup SUCCESSFUL - all jobs cleaned up automatically")
        
        cleanup_time = time.time() - cleanup_start
        
        # Summary
        logger.info(f"\n{'='*80}")
        logger.info(f"Cleanup Summary:")
        logger.info(f"  Total jobs: {len(test_job_ids)}")
        logger.info(f"  API canceled: {api_canceled_count}")
        logger.info(f"  System cleaned up: {len(test_job_ids) - len(remaining_jobs)}")
        if remaining_jobs:
            logger.warning(f"  ⚠️  System cleanup FAILED: {len(remaining_jobs)} jobs required aggressive cleanup")
            logger.warning(f"  This is a test failure - system cleanup mechanism is not working correctly!")
        logger.info(f"  Total cleanup time: {cleanup_time:.2f}s")
        logger.info(f"{'='*80}\n")
        
        # Remove from global set
        for job_id in test_job_ids:
            _job_ids_created.discard(job_id)
    else:
        logger.debug("No jobs to cleanup")


@pytest.fixture(scope="session", autouse=True)
def session_job_cleanup(request):
    """
    Session-level cleanup fixture.
    
    Cleans up any remaining jobs at the end of the test session.
    This is a safety net in case some jobs weren't cleaned up properly.
    """
    yield
    
    # Final cleanup at session end
    if _job_ids_created:
        logger.warning(f"Session cleanup: Found {len(_job_ids_created)} remaining jobs")
        logger.warning("These jobs should have been cleaned up by test fixtures")
        logger.warning("Manual cleanup may be required")

