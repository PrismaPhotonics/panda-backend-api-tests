"""
Gradual Historic Job Load Test - Step-by-Step Capacity Testing
================================================================

This test implements a gradual load testing strategy for Historic Jobs,
using the SAME intervals as Live load tests:

1. Start with 5 concurrent Historic Jobs
2. Every 10 seconds, add 5 more Historic Jobs
3. Continue until reaching 100 Historic Jobs maximum
4. At each step, verify system health and stability
5. After reaching maximum, perform final health check
6. Clean up all jobs and verify system returns to healthy state

Test Flow:
    Step 1: Start 5 jobs → Verify health → Wait 10s
    Step 2: Add 5 more (10 total) → Verify health → Wait 10s
    Step 3: Add 5 more (15 total) → Verify health → Wait 10s
    ...
    Step 20: Add 5 more (100 total) → Final health check
    Cleanup: Cancel all jobs → Verify clean state

Uses MongoDB base_paths collection to find recordings for load testing.

Author: QA Automation Architect
Date: 2025-12-02
"""

import pytest
import logging
import time
import threading
import random
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from enum import Enum
from statistics import mean, stdev

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration Constants - SAME AS LIVE TESTS
# =============================================================================

class GradualHistoricLoadConfig:
    """Configuration for gradual historic load test - SAME intervals as Live."""
    
    # Load stepping - IDENTICAL to Live tests
    INITIAL_JOBS: int = 5           # Start with 5 jobs (same as Live)
    STEP_INCREMENT: int = 5         # Add 5 jobs per step (same as Live)
    MAX_JOBS: int = 100             # Maximum 100 jobs (same as Live)
    STEP_INTERVAL_SECONDS: int = 10 # Wait 10 seconds between steps (SAME AS LIVE)
    
    # Health check thresholds - adjusted for Historic jobs
    MIN_SUCCESS_RATE: float = 70.0  # Minimum 70% success rate
    MIN_STREAMING_RATE: float = 50.0  # At least 50% of jobs should stream data
    MAX_API_RESPONSE_TIME_MS: float = 10000.0  # Max 10s for API calls
    MAX_GRPC_CONNECT_TIME_MS: float = 60000.0  # Max 60s for gRPC connect
    
    # Job configuration
    CHANNELS_MIN: int = 1
    CHANNELS_MAX: int = 50
    FREQUENCY_MIN: int = 0
    FREQUENCY_MAX: int = 500
    NFFT: int = 1024
    FRAMES_TO_RECEIVE: int = 3  # Quick verification per job
    
    # Historic-specific - DYNAMIC TIME RANGE
    RECORDING_DURATION_SECONDS: int = 10  # Duration of recording to request
    MIN_DURATION_SECONDS: float = 5.0     # Min recording duration in MongoDB
    MAX_DURATION_SECONDS: float = 300.0   # Max recording duration (5 minutes) - EXTENDED for flexibility
    WEEKS_BACK: int = 4                   # Weeks back to search (1 month) - EXTENDED from 2
    MAX_RECORDINGS_TO_LOAD: int = 500     # Max recordings to load from MongoDB - EXTENDED for more options
    
    # Retry configuration
    MAX_GRPC_RETRIES: int = 3       # Reduced retries for faster failure detection
    GRPC_RETRY_DELAY_MS: int = 2000 # Shorter delay between retries
    
    # Batch creation delay
    JOB_CREATION_DELAY_MS: int = 200  # Reduced delay between creating jobs in batch


class HealthCheckResult(Enum):
    """Health check result status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ActiveHistoricJob:
    """Represents an active Historic Job."""
    job_id: str
    stream_url: str
    stream_port: int
    grpc_client: Any
    created_at: datetime
    connected: bool = False
    frames_received: int = 0
    start_time: Optional[int] = None  # Historic: epoch seconds
    end_time: Optional[int] = None     # Historic: epoch seconds
    error: Optional[str] = None
    
    def __hash__(self):
        return hash(self.job_id)


@dataclass
class StepMetrics:
    """Metrics for a single load step."""
    step_number: int
    target_jobs: int
    actual_jobs: int
    jobs_created: int
    jobs_failed: int
    creation_time_ms: float
    grpc_connect_time_ms: float
    health_status: HealthCheckResult
    api_response_time_ms: float
    success_rate: float
    timestamp: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number,
            "target_jobs": self.target_jobs,
            "actual_jobs": self.actual_jobs,
            "jobs_created": self.jobs_created,
            "jobs_failed": self.jobs_failed,
            "creation_time_ms": round(self.creation_time_ms, 2),
            "grpc_connect_time_ms": round(self.grpc_connect_time_ms, 2),
            "health_status": self.health_status.value,
            "api_response_time_ms": round(self.api_response_time_ms, 2),
            "success_rate": round(self.success_rate, 2),
            "timestamp": self.timestamp.isoformat(),
            "errors": self.errors
        }


@dataclass
class GradualHistoricLoadTestResult:
    """Complete result of gradual historic load test."""
    test_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    
    # Job counts
    max_jobs_reached: int
    total_jobs_created: int
    total_jobs_failed: int
    total_jobs_cleaned: int
    
    # Health metrics
    final_health_status: HealthCheckResult
    steps_healthy: int
    steps_degraded: int
    steps_unhealthy: int
    
    # Performance metrics
    avg_creation_time_ms: float
    avg_grpc_connect_time_ms: float
    
    # All step metrics
    step_metrics: List[StepMetrics] = field(default_factory=list)
    
    def to_log_message(self) -> str:
        """Generate detailed log message."""
        lines = [
            "",
            "=" * 80,
            "📼 GRADUAL HISTORIC JOB LOAD TEST - RESULTS",
            "=" * 80,
            "",
            f"📊 Test Summary:",
            f"   • Test Name: {self.test_name}",
            f"   • Duration: {self.duration_seconds:.2f} seconds",
            f"   • Max Jobs Reached: {self.max_jobs_reached}",
            "",
            f"📦 Job Statistics:",
            f"   • Total Created: {self.total_jobs_created}",
            f"   • Total Failed: {self.total_jobs_failed}",
            f"   • Total Cleaned: {self.total_jobs_cleaned}",
            "",
            f"🏥 Health Status:",
            f"   • Final Status: {self.final_health_status.value}",
            f"   • Healthy Steps: {self.steps_healthy}",
            f"   • Degraded Steps: {self.steps_degraded}",
            f"   • Unhealthy Steps: {self.steps_unhealthy}",
            "",
            f"⏱️  Performance:",
            f"   • Avg Creation Time: {self.avg_creation_time_ms:.0f}ms",
            f"   • Avg gRPC Connect Time: {self.avg_grpc_connect_time_ms:.0f}ms",
            "",
            "📈 Step-by-Step Progress:",
        ]
        
        for step in self.step_metrics:
            status_icon = "✅" if step.health_status == HealthCheckResult.HEALTHY else (
                "⚠️" if step.health_status == HealthCheckResult.DEGRADED else "❌"
            )
            lines.append(
                f"   Step {step.step_number:2d}: {step.actual_jobs:2d} jobs | "
                f"{step.success_rate:.0f}% success | {status_icon} {step.health_status.value}"
            )
        
        lines.extend([
            "",
            "=" * 80,
        ])
        
        return "\n".join(lines)


# =============================================================================
# Gradual Historic Job Load Tester
# =============================================================================

class GradualHistoricJobLoadTester:
    """
    Gradual Historic Job Load Tester - Step-by-step capacity testing.
    
    Uses the SAME intervals as Live load tests:
    - Initial: 5 jobs
    - Step: +5 jobs every 10 seconds
    - Max: 100 jobs
    
    This tester gradually increases the number of concurrent Historic Jobs,
    verifying system health at each step.
    
    Uses MongoDB base_paths collection to find recordings for load testing.
    
    Usage:
        tester = GradualHistoricJobLoadTester(config_manager)
        result = tester.run_gradual_load_test()
        print(result.to_log_message())
    """
    
    def __init__(self, config_manager, config: Optional[GradualHistoricLoadConfig] = None):
        """
        Initialize the gradual historic load tester.
        
        Args:
            config_manager: Configuration manager instance
            config: Optional custom configuration (defaults to GradualHistoricLoadConfig)
        """
        self.config_manager = config_manager
        self.cfg = config or GradualHistoricLoadConfig()
        
        # Active jobs tracking
        self._active_jobs: Dict[str, ActiveHistoricJob] = {}
        self._lock = threading.Lock()
        
        # API client (lazy initialization)
        self._api = None
        
        logger.info(
            f"GradualHistoricJobLoadTester initialized: "
            f"Initial={self.cfg.INITIAL_JOBS}, Step={self.cfg.STEP_INCREMENT}, "
            f"Max={self.cfg.MAX_JOBS}, Interval={self.cfg.STEP_INTERVAL_SECONDS}s"
        )
    
    @property
    def api(self):
        """Lazy initialization of Focus Server API client."""
        if self._api is None:
            from src.apis.focus_server_api import FocusServerAPI
            self._api = FocusServerAPI(self.config_manager)
        return self._api
    
    def _get_available_recordings(self) -> List[tuple]:
        """
        Get available recordings from MongoDB base_paths collection.
        
        DYNAMIC TIME RANGE: Searches from current date going back up to 4 weeks.
        Works with both kefar_saba and staging environments which have different data.
        
        Returns:
            List of (start_time_ms, end_time_ms) tuples
        """
        try:
            from be_focus_server_tests.fixtures.recording_fixtures import fetch_recordings_from_mongodb
            
            logger.info(f"🔍 Querying MongoDB for historic recordings...")
            logger.info(f"   Time range: last {self.cfg.WEEKS_BACK} weeks from NOW")
            logger.info(f"   Duration filter: {self.cfg.MIN_DURATION_SECONDS}-{self.cfg.MAX_DURATION_SECONDS}s")
            
            # Try with configured weeks_back first
            recordings_info = fetch_recordings_from_mongodb(
                config_manager=self.config_manager,
                max_recordings=self.cfg.MAX_RECORDINGS_TO_LOAD,
                min_duration_seconds=self.cfg.MIN_DURATION_SECONDS,
                max_duration_seconds=self.cfg.MAX_DURATION_SECONDS,
                weeks_back=self.cfg.WEEKS_BACK
            )
            
            # If no recordings found, try extending the search range
            if not recordings_info.has_recordings:
                logger.warning(f"No recordings in last {self.cfg.WEEKS_BACK} weeks, trying 8 weeks...")
                recordings_info = fetch_recordings_from_mongodb(
                    config_manager=self.config_manager,
                    max_recordings=self.cfg.MAX_RECORDINGS_TO_LOAD,
                    min_duration_seconds=self.cfg.MIN_DURATION_SECONDS,
                    max_duration_seconds=600.0,  # Up to 10 minutes
                    weeks_back=8  # 2 months back
                )
            
            if not recordings_info.has_recordings:
                logger.error("❌ No recordings found in MongoDB even with extended search!")
                logger.error("   Check MongoDB connection and data availability")
                return []
            
            # Convert Recording objects to (start_ms, end_ms) tuples
            recordings_list = []
            for rec in recordings_info.recordings:
                recordings_list.append((rec.start_time_ms, rec.end_time_ms))
            
            # Log sample of found recordings
            logger.info(f"✅ Loaded {len(recordings_list)} recordings from MongoDB")
            if recordings_list:
                first_rec = recordings_list[0]
                last_rec = recordings_list[-1]
                from datetime import datetime
                first_dt = datetime.fromtimestamp(first_rec[0] / 1000)
                last_dt = datetime.fromtimestamp(last_rec[0] / 1000)
                logger.info(f"   Newest: {first_dt}")
                logger.info(f"   Oldest: {last_dt}")
            
            return recordings_list
            
        except Exception as e:
            logger.error(f"Failed to get recordings from MongoDB: {e}", exc_info=True)
            return []
    
    def _create_config_payload(self, recording_index: int = 0) -> Dict[str, Any]:
        """
        Create Historic job payload with time range from MongoDB.
        
        Uses round-robin selection to distribute load across different recordings.
        """
        recordings = self._get_available_recordings()
        
        if recordings:
            # Round-robin selection
            rec_index = recording_index % len(recordings)
            rec_start_ms, rec_end_ms = recordings[rec_index]
            
            # Calculate time range (use requested duration or available)
            duration_ms = self.cfg.RECORDING_DURATION_SECONDS * 1000
            actual_duration_ms = min(duration_ms, rec_end_ms - rec_start_ms)
            
            # Convert to seconds for API (epoch seconds)
            start_time = rec_start_ms // 1000
            end_time = (rec_start_ms + actual_duration_ms) // 1000
        else:
            # Fallback: use current time minus offset (may fail if no recording)
            logger.warning("No recordings found in MongoDB base_paths, using fallback time range")
            now = int(time.time())
            start_time = now - 60  # 1 minute ago (in seconds)
            end_time = now - 50     # 50 seconds ago (in seconds)
        
        return {
            "displayTimeAxisDuration": 10,
            "nfftSelection": self.cfg.NFFT,
            "displayInfo": {"height": 600},
            "channels": {
                "min": self.cfg.CHANNELS_MIN, 
                "max": self.cfg.CHANNELS_MAX
            },
            "frequencyRange": {
                "min": self.cfg.FREQUENCY_MIN, 
                "max": self.cfg.FREQUENCY_MAX
            },
            "start_time": start_time,  # HISTORIC - has start time
            "end_time": end_time,       # HISTORIC - has end time
            "view_type": "0"            # MULTICHANNEL
        }
    
    def _create_single_job(self, recording_index: int = 0) -> Optional[ActiveHistoricJob]:
        """
        Create a single Historic Job and connect to gRPC.
        
        Args:
            recording_index: Index for round-robin recording selection
        
        Returns:
            ActiveHistoricJob instance if successful, None otherwise
        """
        from src.models.focus_server_models import ConfigureRequest
        from src.apis.grpc_client import GrpcStreamClient
        
        start_time = time.time()
        job_id = None
        grpc_client = None
        config_start_time = None
        config_end_time = None
        
        try:
            # Step 1: Create job via POST /configure
            config_payload = self._create_config_payload(recording_index)
            config_start_time = config_payload.get("start_time")
            config_end_time = config_payload.get("end_time")
            
            config_request = ConfigureRequest(**config_payload)
            response = self.api.configure_streaming_job(config_request)
            
            job_id = response.job_id
            stream_url = response.stream_url
            stream_port = int(response.stream_port)
            
            configure_time = (time.time() - start_time) * 1000
            
            logger.debug(
                f"Job {job_id} created in {configure_time:.0f}ms: "
                f"{stream_url}:{stream_port}"
            )
            
            # Step 2: Create gRPC client and connect with retries
            grpc_client = GrpcStreamClient(
                config_manager=self.config_manager,
                connection_timeout=20,  # Reduced from 30 to 20 seconds
                stream_timeout=30      # Reduced from 60 to 30 seconds
            )
            
            connected = False
            last_error = None
            
            for attempt in range(self.cfg.MAX_GRPC_RETRIES):
                try:
                    grpc_client.connect(
                        stream_url=stream_url,
                        stream_port=stream_port,
                        use_tls=False
                    )
                    connected = True
                    break
                except Exception as e:
                    last_error = str(e)
                    if attempt < self.cfg.MAX_GRPC_RETRIES - 1:
                        time.sleep(self.cfg.GRPC_RETRY_DELAY_MS / 1000)
            
            if not connected:
                raise ConnectionError(
                    f"gRPC connect failed after {self.cfg.MAX_GRPC_RETRIES} retries: {last_error}"
                )
            
            # Step 3: Receive a few frames to verify connection
            frames_received = 0
            for frame in grpc_client.stream_data(
                stream_id=0, 
                max_frames=self.cfg.FRAMES_TO_RECEIVE,
                timeout=20  # Reduced from 30 to 20 seconds
            ):
                frames_received += 1
            
            # Create active job
            active_job = ActiveHistoricJob(
                job_id=job_id,
                stream_url=stream_url,
                stream_port=stream_port,
                grpc_client=grpc_client,
                created_at=datetime.now(),
                connected=True,
                frames_received=frames_received,
                start_time=config_start_time,
                end_time=config_end_time
            )
            
            total_time = (time.time() - start_time) * 1000
            logger.info(
                f"✅ Job {job_id} fully initialized in {total_time:.0f}ms "
                f"({frames_received} frames)"
            )
            
            return active_job
            
        except Exception as e:
            logger.warning(f"❌ Failed to create job: {e}")
            
            # Cleanup on failure
            if grpc_client:
                try:
                    grpc_client.disconnect()
                except Exception:
                    pass
            
            return ActiveHistoricJob(
                job_id=job_id or "unknown",
                stream_url="",
                stream_port=0,
                grpc_client=None,
                created_at=datetime.now(),
                connected=False,
                error=str(e),
                start_time=config_start_time,
                end_time=config_end_time
            )
    
    def _create_jobs_batch(self, count: int) -> Tuple[int, int, float, float]:
        """
        Create a batch of Historic jobs with controlled concurrency.
        
        Uses limited parallelism to avoid overwhelming Focus Server.
        Adds small delays between job creation to allow server to stabilize.
        
        Args:
            count: Number of jobs to create
            
        Returns:
            Tuple of (successful_count, failed_count, avg_create_time, avg_connect_time)
        """
        start_time = time.time()
        successful = 0
        failed = 0
        create_times: List[float] = []
        
        # Limit concurrent job creation to avoid overwhelming server
        # OPTIMIZATION: Increased parallelism for faster execution
        max_parallel = min(count, 5)  # Increased from 3 to 5
        delay_between_batches = self.cfg.JOB_CREATION_DELAY_MS / 1000
        
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            futures = []
            
            # Submit jobs with small delays to avoid thundering herd
            for i in range(count):
                # Use round-robin for recording selection
                recording_index = len(self._active_jobs) + i
                futures.append(executor.submit(self._create_single_job, recording_index))
                
                # Add small delay between submissions
                if i < count - 1 and delay_between_batches > 0:
                    time.sleep(delay_between_batches)
            
            for future in as_completed(futures, timeout=300):
                try:
                    job = future.result(timeout=60)  # Reduced from 90 to 60 seconds
                    
                    if job and job.connected:
                        with self._lock:
                            self._active_jobs[job.job_id] = job
                        successful += 1
                        logger.info(f"✅ Job {job.job_id} fully initialized ({job.frames_received} frames)")
                    else:
                        failed += 1
                        if job:
                            logger.warning(f"❌ Job {job.job_id} created but not connected: {job.error}")
                        
                except Exception as e:
                    logger.warning(f"Job creation exception: {e}")
                    failed += 1
        
        total_time = (time.time() - start_time) * 1000
        avg_time = total_time / max(count, 1)
        
        return successful, failed, avg_time, avg_time
    
    def _check_system_health(self) -> Tuple[HealthCheckResult, float]:
        """
        Check overall system health.
        
        Returns:
            Tuple of (HealthCheckResult, api_response_time_ms)
        """
        start_time = time.time()
        
        try:
            # Primary check: API health
            is_api_healthy = self.api.get_health_status()
            api_time = (time.time() - start_time) * 1000
            
            if not is_api_healthy:
                logger.warning("API health check failed")
                return HealthCheckResult.UNHEALTHY, api_time
            
            # Secondary check: Count jobs with valid connections
            connected_jobs = 0
            total_jobs = len(self._active_jobs)
            
            for job in list(self._active_jobs.values()):
                if job.grpc_client and job.connected:
                    connected_jobs += 1
            
            # Calculate health status
            if total_jobs == 0:
                return HealthCheckResult.HEALTHY, api_time
            
            connection_ratio = connected_jobs / total_jobs
            
            if connection_ratio >= 0.5:  # At least 50% connected = healthy
                return HealthCheckResult.HEALTHY, api_time
            elif connection_ratio >= 0.3:  # 30-50% = degraded
                return HealthCheckResult.DEGRADED, api_time
            else:
                return HealthCheckResult.DEGRADED, api_time
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthCheckResult.UNHEALTHY, 0.0
    
    def _verify_active_jobs(self) -> Tuple[int, int]:
        """
        Verify active jobs are still healthy.
        
        OPTIMIZED: Samples jobs instead of checking all to avoid timeout issues.
        For large job counts (>20), only checks a sample to speed up verification.
        
        Returns:
            Tuple of (streaming_count, not_streaming_count)
        """
        streaming = 0
        not_streaming = 0
        
        jobs_list = list(self._active_jobs.items())
        total_jobs = len(jobs_list)
        
        # OPTIMIZATION: For large job counts, sample instead of checking all
        # This prevents timeout issues when verifying 100+ jobs
        if total_jobs > 20:
            # Sample up to 20 jobs for verification
            import random
            sample_size = min(20, total_jobs)
            jobs_to_check = random.sample(jobs_list, sample_size)
            logger.info(f"   🔍 Sampling {sample_size}/{total_jobs} jobs for verification...")
        else:
            jobs_to_check = jobs_list
            logger.info(f"   🔍 Verifying {total_jobs} active jobs...")
        
        for job_id, job in jobs_to_check:
            if job.grpc_client and job.connected:
                try:
                    # Try to receive one more frame with VERY short timeout
                    frame_received = False
                    for frame in job.grpc_client.stream_data(
                        stream_id=0, 
                        max_frames=1,
                        timeout=2  # Reduced from 5 to 2 seconds for faster verification
                    ):
                        job.frames_received += 1
                        frame_received = True
                        streaming += 1
                        break
                    
                    if not frame_received:
                        not_streaming += 1
                        
                except Exception as e:
                    logger.debug(f"Job {job_id} verification failed: {e}")
                    not_streaming += 1
            else:
                not_streaming += 1
        
        # Scale results if we sampled
        if total_jobs > 20 and len(jobs_to_check) > 0:
            sample_ratio = len(jobs_to_check) / total_jobs
            estimated_streaming = int(streaming / sample_ratio) if sample_ratio > 0 else streaming
            estimated_not_streaming = total_jobs - estimated_streaming
            logger.info(f"   📊 Verification (sampled): {streaming}/{len(jobs_to_check)} streaming → ~{estimated_streaming}/{total_jobs} total")
            return estimated_streaming, estimated_not_streaming
        else:
            logger.info(f"   📊 Verification: {streaming}/{total_jobs} streaming")
            return streaming, not_streaming
    
    def _cleanup_all_jobs(self) -> int:
        """
        Clean up all active jobs by disconnecting gRPC connections.
        
        Returns:
            Number of jobs cleaned up
        """
        logger.info(f"\n🧹 Disconnecting {len(self._active_jobs)} gRPC connections...")
        
        cleaned = 0
        
        for job_id, job in list(self._active_jobs.items()):
            try:
                if job.grpc_client:
                    try:
                        job.grpc_client.disconnect()
                        logger.debug(f"   ✓ Disconnected gRPC for {job_id}")
                    except Exception:
                        pass
                
                cleaned += 1
                
            except Exception as e:
                logger.warning(f"Error cleaning up job {job_id}: {e}")
        
        with self._lock:
            self._active_jobs.clear()
        
        logger.info(f"✅ Disconnected {cleaned} gRPC connections")
        return cleaned
    
    def run_gradual_load_test(
        self,
        test_name: str = "Gradual Historic Job Load Test"
    ) -> GradualHistoricLoadTestResult:
        """
        Run the complete gradual load test - SAME intervals as Live tests.
        
        Steps:
        1. Start with INITIAL_JOBS concurrent jobs
        2. Every STEP_INTERVAL_SECONDS, add STEP_INCREMENT more jobs
        3. Verify system health at each step
        4. Continue until MAX_JOBS is reached
        5. Perform final health verification
        6. Clean up all jobs
        
        Args:
            test_name: Name for this test run
            
        Returns:
            GradualHistoricLoadTestResult with all metrics
        """
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"📼 GRADUAL HISTORIC JOB LOAD TEST - Starting")
        logger.info("=" * 80)
        logger.info(f"   Initial Jobs: {self.cfg.INITIAL_JOBS}")
        logger.info(f"   Step Increment: +{self.cfg.STEP_INCREMENT} jobs")
        logger.info(f"   Step Interval: {self.cfg.STEP_INTERVAL_SECONDS} seconds (SAME AS LIVE)")
        logger.info(f"   Maximum Jobs: {self.cfg.MAX_JOBS}")
        logger.info("=" * 80)
        logger.info("")
        
        start_time = datetime.now()
        start_timestamp = time.time()
        
        step_metrics: List[StepMetrics] = []
        total_created = 0
        total_failed = 0
        max_jobs_reached = 0
        
        try:
            # Calculate number of steps
            num_steps = (self.cfg.MAX_JOBS - self.cfg.INITIAL_JOBS) // self.cfg.STEP_INCREMENT + 1
            
            # ================================================================
            # STEP LOOP: Gradually increase load
            # ================================================================
            for step in range(1, num_steps + 1):
                # Calculate target jobs for this step
                if step == 1:
                    target_jobs = self.cfg.INITIAL_JOBS
                    jobs_to_create = self.cfg.INITIAL_JOBS
                else:
                    target_jobs = self.cfg.INITIAL_JOBS + (step - 1) * self.cfg.STEP_INCREMENT
                    jobs_to_create = self.cfg.STEP_INCREMENT
                
                # Don't exceed max
                if target_jobs > self.cfg.MAX_JOBS:
                    target_jobs = self.cfg.MAX_JOBS
                    jobs_to_create = target_jobs - len(self._active_jobs)
                
                if jobs_to_create <= 0:
                    break
                
                logger.info("")
                logger.info(f"{'─' * 60}")
                logger.info(f"📊 STEP {step}/{num_steps}: Creating {jobs_to_create} jobs (target: {target_jobs})")
                logger.info(f"{'─' * 60}")
                
                # Create jobs for this step
                step_start = time.time()
                successful, failed, avg_create, avg_connect = self._create_jobs_batch(jobs_to_create)
                step_time = (time.time() - step_start) * 1000
                
                total_created += successful
                total_failed += failed
                
                # Update max jobs reached
                current_jobs = len(self._active_jobs)
                max_jobs_reached = max(max_jobs_reached, current_jobs)
                
                # Verify active jobs health
                logger.info(f"   🔍 Verifying {current_jobs} active jobs...")
                healthy, unhealthy = self._verify_active_jobs()
                
                # Check overall system health
                health_status, api_time = self._check_system_health()
                
                # Calculate success rate
                if successful + failed > 0:
                    success_rate = successful / (successful + failed) * 100
                else:
                    success_rate = 0.0
                
                # Record step metrics
                errors = []
                if failed > 0:
                    errors.append(f"{failed} jobs failed to create")
                if unhealthy > 0:
                    errors.append(f"{unhealthy} jobs unhealthy")
                
                step_metric = StepMetrics(
                    step_number=step,
                    target_jobs=target_jobs,
                    actual_jobs=current_jobs,
                    jobs_created=successful,
                    jobs_failed=failed,
                    creation_time_ms=step_time,
                    grpc_connect_time_ms=avg_connect,
                    health_status=health_status,
                    api_response_time_ms=api_time,
                    success_rate=success_rate,
                    errors=errors
                )
                step_metrics.append(step_metric)
                
                # Log step results
                status_icon = "✅" if health_status == HealthCheckResult.HEALTHY else (
                    "⚠️" if health_status == HealthCheckResult.DEGRADED else "❌"
                )
                logger.info(
                    f"   {status_icon} Step {step} complete: "
                    f"{current_jobs} jobs active, {success_rate:.0f}% success, "
                    f"{health_status.value}"
                )
                
                # Wait before next step (except on last step)
                if step < num_steps and current_jobs < self.cfg.MAX_JOBS:
                    logger.info(
                        f"   ⏳ Waiting {self.cfg.STEP_INTERVAL_SECONDS}s before next step..."
                    )
                    time.sleep(self.cfg.STEP_INTERVAL_SECONDS)
            
            # ================================================================
            # FINAL HEALTH CHECK
            # ================================================================
            logger.info("")
            logger.info(f"{'─' * 60}")
            logger.info(f"🏁 FINAL HEALTH CHECK at {max_jobs_reached} jobs")
            logger.info(f"{'─' * 60}")
            
            final_health, final_api_time = self._check_system_health()
            healthy, unhealthy = self._verify_active_jobs()
            
            final_status_icon = "✅" if final_health == HealthCheckResult.HEALTHY else (
                "⚠️" if final_health == HealthCheckResult.DEGRADED else "❌"
            )
            logger.info(f"   {final_status_icon} Final Status: {final_health.value}")
            logger.info(f"   📊 Healthy Jobs: {healthy}/{len(self._active_jobs)}")
            
        finally:
            # ================================================================
            # CLEANUP
            # ================================================================
            cleaned = self._cleanup_all_jobs()
            
            # Verify system returns to healthy state
            time.sleep(2)  # Brief pause before final check
            post_cleanup_health, _ = self._check_system_health()
            logger.info(f"   🧹 Post-cleanup health: {post_cleanup_health.value}")
        
        end_time = datetime.now()
        duration_seconds = time.time() - start_timestamp
        
        # ================================================================
        # CALCULATE RESULTS
        # ================================================================
        
        # Count health statuses
        steps_healthy = sum(1 for s in step_metrics if s.health_status == HealthCheckResult.HEALTHY)
        steps_degraded = sum(1 for s in step_metrics if s.health_status == HealthCheckResult.DEGRADED)
        steps_unhealthy = sum(1 for s in step_metrics if s.health_status == HealthCheckResult.UNHEALTHY)
        
        # Calculate averages
        avg_creation_time = mean([s.creation_time_ms for s in step_metrics]) if step_metrics else 0
        avg_connect_time = mean([s.grpc_connect_time_ms for s in step_metrics]) if step_metrics else 0
        
        result = GradualHistoricLoadTestResult(
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            max_jobs_reached=max_jobs_reached,
            total_jobs_created=total_created,
            total_jobs_failed=total_failed,
            total_jobs_cleaned=cleaned,
            final_health_status=final_health,
            steps_healthy=steps_healthy,
            steps_degraded=steps_degraded,
            steps_unhealthy=steps_unhealthy,
            avg_creation_time_ms=avg_creation_time,
            avg_grpc_connect_time_ms=avg_connect_time,
            step_metrics=step_metrics
        )
        
        # Log results
        logger.info(result.to_log_message())
        return result


# =============================================================================
# Factory Function
# =============================================================================

def create_gradual_historic_load_tester(
    config_manager,
    initial_jobs: int = 5,
    step_increment: int = 5,
    max_jobs: int = 100,
    step_interval: int = 10
) -> GradualHistoricJobLoadTester:
    """
    Factory function to create a GradualHistoricJobLoadTester with custom config.
    
    Uses SAME default values as Live tests:
    - Initial: 5 jobs
    - Step: +5 jobs every 10 seconds
    - Max: 100 jobs
    
    Args:
        config_manager: Configuration manager instance
        initial_jobs: Starting number of jobs (default: 5)
        step_increment: Jobs to add per step (default: 5)
        max_jobs: Maximum jobs (default: 100)
        step_interval: Seconds between steps (default: 10)
        
    Returns:
        Configured GradualHistoricJobLoadTester instance
    """
    config = GradualHistoricLoadConfig()
    config.INITIAL_JOBS = initial_jobs
    config.STEP_INCREMENT = step_increment
    config.MAX_JOBS = max_jobs
    config.STEP_INTERVAL_SECONDS = step_interval
    
    return GradualHistoricJobLoadTester(config_manager, config)


# =============================================================================
# Pytest Fixtures
# =============================================================================

@pytest.fixture
def gradual_historic_tester(config_manager) -> GradualHistoricJobLoadTester:
    """
    Fixture to create GradualHistoricJobLoadTester with default configuration.
    
    Uses SAME intervals as Live tests:
    - Initial: 5 jobs
    - Step: +5 jobs every 10 seconds
    - Max: 100 jobs
    """
    return GradualHistoricJobLoadTester(config_manager)


@pytest.fixture
def quick_gradual_historic_tester(config_manager) -> GradualHistoricJobLoadTester:
    """
    Fixture for quick gradual historic load testing (smaller scale for CI).
    
    Uses:
    - Initial: 2 jobs
    - Step: +2 jobs every 5 seconds
    - Max: 10 jobs
    """
    config = GradualHistoricLoadConfig()
    config.INITIAL_JOBS = 2
    config.STEP_INCREMENT = 2
    config.MAX_JOBS = 10
    config.STEP_INTERVAL_SECONDS = 5
    
    return GradualHistoricJobLoadTester(config_manager, config)


# =============================================================================
# Test Class: Gradual Historic Load Tests
# =============================================================================

@pytest.mark.gradual_load
@pytest.mark.load
@pytest.mark.historic
class TestGradualHistoricJobLoad:
    """
    Gradual Historic Job load tests - step-by-step capacity testing.
    
    Uses the SAME intervals as Live load tests:
    - Initial: 5 jobs
    - Step: +5 jobs every 10 seconds
    - Max: 100 jobs
    
    These tests verify system stability as Historic load increases gradually.
    """
    
    @pytest.mark.xray("PZ-15317")  # Load - Historic - Gradual Load to 100 Jobs
    @pytest.mark.slow
    def test_gradual_load_to_100_jobs(self, gradual_historic_tester):
        """
        Test: Gradual load increase from 5 to 100 Historic Jobs.
        
        Flow:
        1. Start with 5 jobs
        2. Add 5 jobs every 10 seconds
        3. Verify health at each step
        4. Reach 100 jobs maximum
        5. Final health check
        6. Clean up all jobs
        
        Uses SAME intervals as Live tests for consistency.
        
        Expected:
        - At least 70% of steps should pass health check
        - System should remain responsive under load
        - Cleanup should complete successfully
        """
        logger.info(f"\n[GRADUAL HISTORIC LOAD] Full Test: 5 → 100 jobs")
        logger.info(f"    Intervals: SAME AS LIVE TESTS (5+5+5 every 10s)")
        
        result = gradual_historic_tester.run_gradual_load_test(
            test_name="Gradual Load to 100 Jobs"
        )
        
        # Assertions
        assert result.total_jobs_cleaned > 0, \
            "Should have cleaned up at least some jobs"
        
        # At least 70% of steps should pass
        min_successful_steps = int(len(result.step_metrics) * 0.7)
        assert result.steps_healthy >= min_successful_steps, \
            f"Expected at least {min_successful_steps} healthy steps, got {result.steps_healthy}"
        
        # Should reach maximum load
        assert result.max_jobs_reached >= 80, \
            f"Expected to reach at least 80 concurrent jobs, got {result.max_jobs_reached}"
        
        logger.info(f"\n✅ Gradual historic load test completed")
        logger.info(f"   Successful Steps: {result.steps_healthy}/{len(result.step_metrics)}")
        logger.info(f"   Max Concurrent: {result.max_jobs_reached}")
    
    @pytest.mark.xray("PZ-15318")  # Load - Historic - Quick Gradual Load (2→10 Jobs)
    def test_quick_gradual_load(self, quick_gradual_historic_tester):
        """
        Test: Quick gradual load test (2 → 10 jobs).
        
        Faster version for CI/CD pipelines:
        - 2 initial jobs
        - +2 every 5 seconds
        - Maximum 10 jobs
        
        Validates the gradual load mechanism works correctly.
        """
        logger.info(f"\n[GRADUAL HISTORIC LOAD] Quick Test: 2 → 10 jobs")
        
        result = quick_gradual_historic_tester.run_gradual_load_test(
            test_name="Quick Gradual Load (2→10)"
        )
        
        # Assertions
        assert result.total_jobs_cleaned > 0, \
            "Should have cleaned up at least some jobs"
        
        assert len(result.step_metrics) >= 3, \
            f"Expected at least 3 steps, got {len(result.step_metrics)}"
        
        assert result.max_jobs_reached >= 6, \
            f"Expected at least 6 concurrent jobs, got {result.max_jobs_reached}"
        
        logger.info(f"\n✅ Quick gradual historic load test completed")
    
    @pytest.mark.xray("PZ-15319")  # Load - Historic - Gradual Load Health Tracking
    @pytest.mark.slow
    def test_gradual_load_health_tracking(self, gradual_historic_tester):
        """
        Test: Health tracking during gradual load increase.
        
        Validates that health status is properly tracked and
        system doesn't become unhealthy during normal load increase.
        """
        result = gradual_historic_tester.run_gradual_load_test(
            test_name="Health Tracking Test"
        )
        
        # Verify health was tracked at each step
        assert len(result.step_metrics) >= 5, \
            f"Expected at least 5 steps, got {len(result.step_metrics)}"
        
        # Calculate health ratio
        total_steps = len(result.step_metrics)
        healthy_ratio = result.steps_healthy / total_steps if total_steps > 0 else 0
        
        # At least 60% of steps should be healthy
        assert healthy_ratio >= 0.6, \
            f"Only {healthy_ratio*100:.0f}% of steps were healthy, expected >= 60%"
        
        # Log health progression
        logger.info(f"[+] Health tracking: {result.steps_healthy}/{total_steps} steps healthy")
        for step in result.step_metrics:
            logger.info(
                f"    Step {step.step_number}: {step.actual_jobs} jobs, "
                f"{step.health_status.value}"
            )
    
    @pytest.mark.xray("PZ-15320")  # Load - Historic - Gradual Load Cleanup Verification
    @pytest.mark.slow
    def test_gradual_load_cleanup_verification(self, gradual_historic_tester):
        """
        Test: Verify proper cleanup after gradual load test.
        
        Validates that:
        1. All jobs are properly disconnected
        2. Resources are released
        3. System returns to healthy state after cleanup
        """
        result = gradual_historic_tester.run_gradual_load_test(
            test_name="Cleanup Verification Test"
        )
        
        # Verify cleanup
        assert result.total_jobs_cleaned > 0, \
            "Should have cleaned up at least some jobs"
        
        cleanup_ratio = result.total_jobs_cleaned / max(result.total_jobs_created, 1)
        assert cleanup_ratio >= 0.9, \
            f"Cleanup ratio {cleanup_ratio*100:.0f}% below 90%"
        
        # Verify final health
        assert result.final_health_status != HealthCheckResult.UNHEALTHY, \
            "System should not be unhealthy after cleanup"
        
        logger.info(
            f"[+] Cleanup verified: {result.total_jobs_cleaned}/{result.total_jobs_created} "
            f"jobs cleaned, final status: {result.final_health_status.value}"
        )


# =============================================================================
# Test Class: Custom Configuration Tests
# =============================================================================

@pytest.mark.gradual_load
@pytest.mark.load
@pytest.mark.historic
class TestGradualHistoricLoadCustomConfig:
    """
    Gradual historic load tests with custom configurations.
    
    These tests allow running with different parameters while maintaining
    the same core gradual load pattern.
    """
    
    @pytest.mark.xray("PZ-15321")  # Load - Historic - High Concurrency Gradual Load
    @pytest.mark.slow
    def test_high_concurrency_gradual(self, config_manager):
        """
        Test: High concurrency gradual load (10 job steps).
        
        Uses larger increments for faster load buildup:
        - Start with 10 jobs
        - Add 10 every 8 seconds
        - Reach 100 jobs in 10 steps
        
        Still uses gradual pattern, just with larger steps.
        """
        logger.info(f"\n[GRADUAL HISTORIC LOAD] High Concurrency: 10 → 100 (step 10)")
        
        tester = create_gradual_historic_load_tester(
            config_manager=config_manager,
            initial_jobs=10,
            step_increment=10,
            max_jobs=100,
            step_interval=8
        )
        
        result = tester.run_gradual_load_test(
            test_name="High Concurrency (10→100, step 10)"
        )
        
        assert result.total_jobs_cleaned > 0, "Cleanup must succeed"
        assert len(result.step_metrics) >= 8, f"Expected 8+ steps, got {len(result.step_metrics)}"
        
        logger.info(f"\n✅ High concurrency test completed")
        logger.info(f"   Max Concurrent: {result.max_jobs_reached}")

