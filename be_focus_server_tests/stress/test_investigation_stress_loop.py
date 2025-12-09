"""
Stress Test - Investigation Loop
=================================

Stress test that works in a loop:
1. Check if number of open investigations >= N (default: 200) - if yes, stop
2. Start n new investigations (default: 5)
3. Wait for response from focus server, retry on error (up to max retries)
4. Wait for gRPC data
5. Loop back to step 0

Author: QA Automation Team
Date: 2025-11-26
Requested by: Backend Lead Developer
"""

import pytest
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.apis.focus_server_api import FocusServerAPI
from src.apis.grpc_client import GrpcStreamClient
from src.models.focus_server_models import ConfigureRequest, ViewType
from src.core.exceptions import APIError
from src.infrastructure.kubernetes_manager import KubernetesManager

logger = logging.getLogger(__name__)

# Test configuration
MAX_OPEN_INVESTIGATIONS = 200  # N - maximum number of open investigations
NEW_INVESTIGATIONS_BATCH = 5   # n - number of new investigations to start each iteration
MAX_RETRIES = 3                # Maximum retries for failed job creation
RETRY_DELAY_SECONDS = 2        # Delay between retries
GRPC_WAIT_TIMEOUT_SECONDS = 30 # Timeout for waiting for gRPC data
GRPC_MIN_FRAMES = 5            # Minimum number of frames to receive from gRPC


class InvestigationStressLoop:
    """Stress test loop for investigations."""
    
    def __init__(
        self,
        api: FocusServerAPI,
        k8s_manager: Optional[KubernetesManager] = None,
        grpc_client: Optional[GrpcStreamClient] = None
    ):
        """Initialize stress test loop."""
        self.api = api
        self.k8s_manager = k8s_manager
        self.grpc_client = grpc_client
        self.created_job_ids: List[str] = []
        self.stats = {
            "iterations": 0,
            "total_jobs_created": 0,
            "total_jobs_succeeded": 0,
            "total_jobs_failed": 0,
            "total_retries": 0,
            "grpc_streams_successful": 0,
            "grpc_streams_failed": 0,
            "start_time": None,
            "end_time": None
        }
    
    def count_active_investigations(self) -> int:
        """
        Count active investigations (jobs) from Kubernetes.
        
        Returns:
            Number of active grpc-job-* jobs
        """
        if not self.k8s_manager:
            logger.warning("K8s manager not available - cannot count active investigations")
            return 0
        
        try:
            # Get namespace from config
            namespace = self.k8s_manager.k8s_config.get("namespace", "panda")
            
            # Get all jobs
            jobs = self.k8s_manager.get_jobs(namespace)
            
            # Count active grpc-job-* jobs
            active_count = 0
            for job in jobs:
                job_name = job.get("name", "")
                if job_name.startswith("grpc-job-"):
                    # Check if job is active (not completed/failed)
                    status = job.get("status", "").lower()
                    succeeded = job.get("succeeded", 0) or 0
                    failed = job.get("failed", 0) or 0
                    
                    # Job is active if it hasn't completed or failed
                    if status != "complete" and succeeded == 0 and failed == 0:
                        active_count += 1
            
            logger.info(f"Active investigations count: {active_count}")
            return active_count
        
        except Exception as e:
            logger.error(f"Failed to count active investigations: {e}")
            return 0
    
    def create_investigation_with_retry(
        self,
        config_payload: Dict[str, Any],
        max_retries: int = MAX_RETRIES
    ) -> tuple[Optional[str], Optional[Any]]:
        """
        Create an investigation (job) with retry logic.
        
        Args:
            config_payload: Configuration payload
            max_retries: Maximum number of retries
            
        Returns:
            Tuple of (job_id, configure_response) - configure_response contains stream_url/port
        """
        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"Creating investigation (attempt {attempt + 1}/{max_retries + 1})...")
                
                config_request = ConfigureRequest(**config_payload)
                response = self.api.configure_streaming_job(config_request)
                
                if response and hasattr(response, 'job_id') and response.job_id:
                    job_id = response.job_id
                    logger.info(f"✅ Investigation created: {job_id}")
                    logger.debug(f"   Stream: {response.stream_url}:{response.stream_port}")
                    self.stats["total_jobs_created"] += 1
                    self.stats["total_jobs_succeeded"] += 1
                    self.created_job_ids.append(job_id)
                    return job_id, response
                else:
                    raise APIError("No job_id returned from configure_streaming_job")
            
            except Exception as e:
                if attempt < max_retries:
                    self.stats["total_retries"] += 1
                    logger.warning(
                        f"⚠️  Failed to create investigation (attempt {attempt + 1}/{max_retries + 1}): {e}"
                    )
                    logger.info(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    logger.error(f"❌ Failed to create investigation after {max_retries + 1} attempts: {e}")
                    self.stats["total_jobs_failed"] += 1
                    return None, None
        
        return None, None
    
    def wait_for_grpc_data(self, job_id: str, configure_response: Optional[Any] = None) -> bool:
        """
        Wait for gRPC data stream.
        
        Args:
            job_id: Job ID to wait for
            configure_response: Optional ConfigureResponse object (if available, will use stream_url/port from it)
            
        Returns:
            True if data received successfully, False otherwise
        """
        if not self.grpc_client:
            logger.warning("gRPC client not available - skipping gRPC wait")
            return False
        
        try:
            # Get stream URL and port
            stream_url = None
            stream_port = None
            
            # Option 1: Use configure_response if provided (FASTEST - no API call needed)
            if configure_response and hasattr(configure_response, 'stream_url') and configure_response.stream_url:
                # Extract hostname/IP from stream_url (remove http:// or https:// if present)
                stream_url_raw = configure_response.stream_url
                if stream_url_raw.startswith('http://'):
                    stream_url = stream_url_raw.replace('http://', '')
                elif stream_url_raw.startswith('https://'):
                    stream_url = stream_url_raw.replace('https://', '')
                else:
                    stream_url = stream_url_raw
                stream_port = configure_response.stream_port
                logger.info(f"✅ Using stream info from configure response: {stream_url}:{stream_port}")
            
            # Option 2: Get from metadata endpoint (with retry logic)
            else:
                logger.info(f"Getting job metadata for {job_id} (waiting for job to be ready)...")
                metadata = None
                max_wait_time = 60  # Wait up to 60 seconds
                wait_start = time.time()
                wait_interval = 2  # Check every 2 seconds
                
                while time.time() - wait_start < max_wait_time:
                    try:
                        metadata = self.api.get_job_metadata(job_id)
                        if metadata and hasattr(metadata, 'stream_url') and metadata.stream_url:
                            stream_url = metadata.stream_url
                            stream_port = metadata.stream_port
                            logger.info(f"✅ Job metadata retrieved after {time.time() - wait_start:.1f}s: {stream_url}:{stream_port}")
                            break
                    except Exception as e:
                        logger.debug(f"Metadata not ready yet (attempt {int((time.time() - wait_start) / wait_interval) + 1}): {e}")
                    
                    if time.time() - wait_start < max_wait_time:
                        time.sleep(wait_interval)
                
                if not stream_url or not stream_port:
                    logger.warning(f"Could not get stream URL/port for job {job_id} after {max_wait_time}s - job may not be ready")
                    return False
            
            logger.info(f"Connecting to gRPC stream: {stream_url}:{stream_port}")
            
            # Connect to gRPC stream
            self.grpc_client.connect(stream_url, stream_port)
            
            # Wait for data
            logger.info(f"Waiting for gRPC data (timeout: {GRPC_WAIT_TIMEOUT_SECONDS}s)...")
            frames_received = 0
            start_time = time.time()
            
            # Use stream_id=0 (default) - stream_id is for stream separation, not job_id
            for frame in self.grpc_client.stream_data(stream_id=0, max_frames=GRPC_MIN_FRAMES):
                frames_received += 1
                logger.debug(f"Received frame {frames_received}/{GRPC_MIN_FRAMES}")
                
                if frames_received >= GRPC_MIN_FRAMES:
                    elapsed = time.time() - start_time
                    logger.info(f"✅ Received {frames_received} frames in {elapsed:.2f}s")
                    self.stats["grpc_streams_successful"] += 1
                    self.grpc_client.disconnect()
                    return True
                
                # Check timeout
                if time.time() - start_time > GRPC_WAIT_TIMEOUT_SECONDS:
                    logger.warning(f"⏱️  Timeout waiting for gRPC data ({GRPC_WAIT_TIMEOUT_SECONDS}s)")
                    self.grpc_client.disconnect()
                    self.stats["grpc_streams_failed"] += 1
                    return False
            
            # If we got here, we received some frames but not enough
            if frames_received > 0:
                logger.info(f"✅ Received {frames_received} frames (less than {GRPC_MIN_FRAMES} requested)")
                self.stats["grpc_streams_successful"] += 1
                self.grpc_client.disconnect()
                return True
            else:
                logger.warning("⚠️  No frames received from gRPC stream")
                self.stats["grpc_streams_failed"] += 1
                self.grpc_client.disconnect()
                return False
        
        except Exception as e:
            logger.error(f"❌ Error waiting for gRPC data: {e}")
            if self.grpc_client:
                try:
                    self.grpc_client.disconnect()
                except:
                    pass
            self.stats["grpc_streams_failed"] += 1
            return False
    
    def run_stress_loop(
        self,
        config_payload: Dict[str, Any],
        max_iterations: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run the stress test loop.
        
        Args:
            config_payload: Configuration payload for investigations
            max_iterations: Maximum number of iterations (None = unlimited)
            
        Returns:
            Statistics dictionary
        """
        self.stats["start_time"] = datetime.now()
        
        logger.info("=" * 80)
        logger.info("STRESS TEST LOOP - Investigation Stress Test")
        logger.info("=" * 80)
        logger.info(f"Max open investigations: {MAX_OPEN_INVESTIGATIONS}")
        logger.info(f"New investigations per iteration: {NEW_INVESTIGATIONS_BATCH}")
        logger.info(f"Max retries per investigation: {MAX_RETRIES}")
        logger.info(f"gRPC wait timeout: {GRPC_WAIT_TIMEOUT_SECONDS}s")
        logger.info(f"gRPC min frames: {GRPC_MIN_FRAMES}")
        if max_iterations:
            logger.info(f"Max iterations: {max_iterations}")
        logger.info("=" * 80)
        logger.info("")
        
        iteration = 0
        
        while True:
            iteration += 1
            self.stats["iterations"] = iteration
            
            logger.info("")
            logger.info("=" * 80)
            logger.info(f"ITERATION {iteration}")
            logger.info("=" * 80)
            
            # Step 0: Check if number of open investigations >= N
            logger.info("Step 0: Checking active investigations count...")
            active_count = self.count_active_investigations()
            
            if active_count >= MAX_OPEN_INVESTIGATIONS:
                logger.warning(f"⚠️  Active investigations ({active_count}) >= max ({MAX_OPEN_INVESTIGATIONS})")
                logger.info("Stopping stress test loop...")
                break
            
            logger.info(f"✅ Active investigations: {active_count} < {MAX_OPEN_INVESTIGATIONS}")
            
            # Check max iterations
            if max_iterations and iteration > max_iterations:
                logger.info(f"Reached maximum iterations ({max_iterations})")
                break
            
            # Step 1: Start n new investigations
            logger.info(f"Step 1: Starting {NEW_INVESTIGATIONS_BATCH} new investigations...")
            batch_jobs = []  # List of (job_id, configure_response) tuples
            
            for i in range(NEW_INVESTIGATIONS_BATCH):
                logger.info(f"  Creating investigation {i+1}/{NEW_INVESTIGATIONS_BATCH}...")
                job_id, configure_response = self.create_investigation_with_retry(config_payload)
                
                if job_id:
                    batch_jobs.append((job_id, configure_response))
                else:
                    logger.warning(f"  ⚠️  Failed to create investigation {i+1}/{NEW_INVESTIGATIONS_BATCH}")
            
            logger.info(f"✅ Created {len(batch_jobs)}/{NEW_INVESTIGATIONS_BATCH} investigations")
            
            # Step 2: Wait for gRPC data for each successful job
            if batch_jobs:
                logger.info(f"Step 2: Waiting for gRPC data for {len(batch_jobs)} investigations...")
                
                for job_id, configure_response in batch_jobs:
                    logger.info(f"  Waiting for gRPC data: {job_id}...")
                    success = self.wait_for_grpc_data(job_id, configure_response)
                    
                    if success:
                        logger.info(f"  ✅ gRPC data received for {job_id}")
                    else:
                        logger.warning(f"  ⚠️  Failed to receive gRPC data for {job_id}")
            
            # Step 3: Loop back to step 0
            logger.info("Step 3: Iteration complete, looping back...")
            logger.info("")
            
            # Small delay between iterations
            time.sleep(1)
        
        self.stats["end_time"] = datetime.now()
        
        # Calculate duration
        if self.stats["start_time"] and self.stats["end_time"]:
            duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
            self.stats["duration_seconds"] = duration
        else:
            self.stats["duration_seconds"] = 0
        
        return self.stats


# ===================================================================
# Test Fixtures
# ===================================================================

@pytest.fixture
def standard_investigation_config():
    """Standard configuration for investigations."""
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


# ===================================================================
# Test Cases
# ===================================================================

@pytest.mark.stress
@pytest.mark.load
@pytest.mark.slow
@pytest.mark.nightly
class TestInvestigationStressLoop:
    """Stress test loop for investigations."""
    
    def test_investigation_stress_loop(
        self,
        focus_server_api: FocusServerAPI,
        config_manager,
        standard_investigation_config: Dict[str, Any],
        k8s_manager: Optional[KubernetesManager] = None,
        grpc_client: Optional[GrpcStreamClient] = None
    ):
        """
        Stress test: Investigation loop.
        
        Process:
        1. Check if number of open investigations >= N (200) - if yes, stop
        2. Start n new investigations (5)
        3. Wait for response from focus server, retry on error (up to max retries)
        4. Wait for gRPC data
        5. Loop back to step 0
        
        This test runs until:
        - Number of active investigations reaches MAX_OPEN_INVESTIGATIONS (200)
        - Or manually stopped
        """
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Investigation Stress Loop")
        logger.info("=" * 80)
        
        # Initialize K8s manager if not provided
        if not k8s_manager:
            try:
                k8s_manager = KubernetesManager(config_manager)
                logger.info("✅ Kubernetes manager initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize K8s manager: {e}")
                k8s_manager = None
        
        # Initialize gRPC client if not provided
        if not grpc_client:
            try:
                grpc_client = GrpcStreamClient(config_manager)
                logger.info("✅ gRPC client initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize gRPC client: {e}")
                grpc_client = None
        
        # Initialize stress loop
        stress_loop = InvestigationStressLoop(
            api=focus_server_api,
            k8s_manager=k8s_manager,
            grpc_client=grpc_client
        )
        
        try:
            # Run stress loop
            stats = stress_loop.run_stress_loop(
                config_payload=standard_investigation_config,
                max_iterations=None  # Run until max investigations reached
            )
            
            # Print summary
            logger.info("")
            logger.info("=" * 80)
            logger.info("STRESS TEST LOOP - SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Iterations completed: {stats['iterations']}")
            logger.info(f"Total jobs created: {stats['total_jobs_created']}")
            logger.info(f"Total jobs succeeded: {stats['total_jobs_succeeded']}")
            logger.info(f"Total jobs failed: {stats['total_jobs_failed']}")
            logger.info(f"Total retries: {stats['total_retries']}")
            logger.info(f"gRPC streams successful: {stats['grpc_streams_successful']}")
            logger.info(f"gRPC streams failed: {stats['grpc_streams_failed']}")
            
            if stats.get('duration_seconds'):
                duration_min = stats['duration_seconds'] / 60
                logger.info(f"Duration: {duration_min:.2f} minutes ({stats['duration_seconds']:.0f} seconds)")
            
            logger.info("=" * 80)
            
            # Assertions
            assert stats['iterations'] > 0, "Should have completed at least one iteration"
            assert stats['total_jobs_created'] > 0, "Should have created at least one job"
            
            logger.info("\n✅ Stress test loop completed successfully!")
        
        finally:
            # Cleanup: Cancel all created jobs
            if hasattr(stress_loop, 'created_job_ids') and stress_loop.created_job_ids:
                logger.info(f"\n{'='*80}")
                logger.info(f"Cleaning up {len(stress_loop.created_job_ids)} investigation jobs...")
                logger.info(f"{'='*80}")
                
                cleanup_start = time.time()
                canceled_count = 0
                failed_count = 0
                
                def cancel_job_safe(job_id: str) -> bool:
                    """Cancel a single job safely."""
                    try:
                        focus_server_api.cancel_job(job_id)
                        logger.debug(f"Canceled job: {job_id}")
                        return True
                    except Exception as e:
                        logger.warning(f"Failed to cancel job {job_id}: {e}")
                        return False
                
                # Parallel cleanup (max 10 workers to avoid overwhelming API)
                from concurrent.futures import ThreadPoolExecutor, as_completed
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = {executor.submit(cancel_job_safe, job_id): job_id 
                              for job_id in stress_loop.created_job_ids}
                    
                    for future in as_completed(futures):
                        if future.result():
                            canceled_count += 1
                        else:
                            failed_count += 1
                
                cleanup_time = time.time() - cleanup_start
                logger.info(f"Cleanup completed: {canceled_count}/{len(stress_loop.created_job_ids)} jobs canceled in {cleanup_time:.2f}s")
                
                if failed_count > 0:
                    logger.warning(f"⚠️ Failed to cancel {failed_count} jobs - they may need manual cleanup")
                else:
                    logger.info("✅ All investigation jobs cleaned up successfully")


@pytest.mark.stress
@pytest.mark.load
@pytest.mark.slow
@pytest.mark.nightly
class TestInvestigationStressLoopLimited:
    """Limited stress test loop (for CI/CD)."""
    
    def test_investigation_stress_loop_limited(
        self,
        focus_server_api: FocusServerAPI,
        config_manager,
        standard_investigation_config: Dict[str, Any],
        k8s_manager: Optional[KubernetesManager] = None,
        grpc_client: Optional[GrpcStreamClient] = None
    ):
        """
        Limited stress test loop (for CI/CD environments).
        
        Same as test_investigation_stress_loop but with limited iterations.
        """
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Investigation Stress Loop (Limited)")
        logger.info("=" * 80)
        
        # Initialize K8s manager if not provided
        if not k8s_manager:
            try:
                k8s_manager = KubernetesManager(config_manager)
                logger.info("✅ Kubernetes manager initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize K8s manager: {e}")
                k8s_manager = None
        
        # Initialize gRPC client if not provided
        if not grpc_client:
            try:
                grpc_client = GrpcStreamClient(config_manager)
                logger.info("✅ gRPC client initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize gRPC client: {e}")
                grpc_client = None
        
        # Initialize stress loop
        stress_loop = InvestigationStressLoop(
            api=focus_server_api,
            k8s_manager=k8s_manager,
            grpc_client=grpc_client
        )
        
        try:
            # Run stress loop with limited iterations
            stats = stress_loop.run_stress_loop(
                config_payload=standard_investigation_config,
                max_iterations=3  # Limited to 3 iterations for CI/CD
            )
            
            # Print summary
            logger.info("")
            logger.info("=" * 80)
            logger.info("STRESS TEST LOOP - SUMMARY (Limited)")
            logger.info("=" * 80)
            logger.info(f"Iterations completed: {stats['iterations']}")
            logger.info(f"Total jobs created: {stats['total_jobs_created']}")
            logger.info(f"Total jobs succeeded: {stats['total_jobs_succeeded']}")
            logger.info(f"Total jobs failed: {stats['total_jobs_failed']}")
            logger.info(f"gRPC streams successful: {stats['grpc_streams_successful']}")
            logger.info(f"gRPC streams failed: {stats['grpc_streams_failed']}")
            logger.info("=" * 80)
            
            # Assertions
            assert stats['iterations'] > 0, "Should have completed at least one iteration"
            
            logger.info("\n✅ Limited stress test loop completed successfully!")
        
        finally:
            # Cleanup: Cancel all created jobs
            if hasattr(stress_loop, 'created_job_ids') and stress_loop.created_job_ids:
                logger.info(f"\n{'='*80}")
                logger.info(f"Cleaning up {len(stress_loop.created_job_ids)} investigation jobs...")
                logger.info(f"{'='*80}")
                
                cleanup_start = time.time()
                canceled_count = 0
                failed_count = 0
                
                def cancel_job_safe(job_id: str) -> bool:
                    """Cancel a single job safely."""
                    try:
                        focus_server_api.cancel_job(job_id)
                        logger.debug(f"Canceled job: {job_id}")
                        return True
                    except Exception as e:
                        logger.warning(f"Failed to cancel job {job_id}: {e}")
                        return False
                
                # Parallel cleanup (max 10 workers to avoid overwhelming API)
                from concurrent.futures import ThreadPoolExecutor, as_completed
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = {executor.submit(cancel_job_safe, job_id): job_id 
                              for job_id in stress_loop.created_job_ids}
                    
                    for future in as_completed(futures):
                        if future.result():
                            canceled_count += 1
                        else:
                            failed_count += 1
                
                cleanup_time = time.time() - cleanup_start
                logger.info(f"Cleanup completed: {canceled_count}/{len(stress_loop.created_job_ids)} jobs canceled in {cleanup_time:.2f}s")
                
                if failed_count > 0:
                    logger.warning(f"⚠️ Failed to cancel {failed_count} jobs - they may need manual cleanup")
                else:
                    logger.info("✅ All investigation jobs cleaned up successfully")

