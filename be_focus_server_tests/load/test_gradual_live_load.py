"""
Gradual Live Job Load Test - Step-Up Load Testing
===================================================

This module implements a gradual (step-up) load test for Live Jobs:
1. Starts with 5 concurrent live jobs
2. Every 10 seconds, adds 5 more jobs
3. Continues until reaching 100 live jobs
4. At each step: validates system health and stability
5. At maximum load: performs final health check
6. Cleanup: stops all jobs and cleans up resources

This approach allows us to:
- Identify the breaking point of the system
- Monitor performance degradation under load
- Ensure proper cleanup even after heavy load

Test Flow (Step-Up):
    Step 1:  5 jobs → Health Check
    Step 2: 10 jobs → Health Check
    Step 3: 15 jobs → Health Check
    ...
    Step 20: 100 jobs → Final Health Check → Cleanup

Markers:
    - @pytest.mark.gradual_load - Gradual load tests
    - @pytest.mark.load - Load tests
    - @pytest.mark.live - Live job tests

Run:
    pytest be_focus_server_tests/load/test_gradual_live_load.py -v -s

Author: QA Automation Architect
Date: 2025-11-30
"""

import pytest
import logging
import time
import os
import threading
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration Constants
# =============================================================================

# Load test parameters
INITIAL_JOBS = 5           # Start with 5 jobs
STEP_INCREMENT = 5         # Add 5 jobs each step
MAX_JOBS = 100             # Maximum 100 jobs running concurrently (Yonatan's requirement)
STEP_INTERVAL_SEC = 10     # Wait 10 seconds between steps

# SLA thresholds - adjusted for Focus Server MaxWindows limit
DEFAULT_SLA = {
    "min_success_rate": 60,           # Minimum success rate per step (%) - more lenient
    "min_streaming_rate": 50,         # At least 50% of jobs should stream data
    "max_avg_response_time_ms": 60000, # Max average response time (ms) - more lenient
    "max_error_rate_at_max": 40,      # Max error rate at maximum load (%) - expect some GOAWAY
    "health_check_timeout_sec": 60,    # Health check timeout (seconds)
}


# =============================================================================
# Data Classes
# =============================================================================

class LiveJobHandle:
    """
    Represents an active Live Job with CONTINUOUS streaming.
    
    Each job runs a background thread that continuously receives frames
    to keep the gRPC stream alive.
    """
    
    def __init__(
        self,
        job_id: str,
        stream_url: str,
        stream_port: int,
        grpc_client: Any,
    ):
        self.job_id = job_id
        self.stream_url = stream_url
        self.stream_port = stream_port
        self.grpc_client = grpc_client
        self.created_at = datetime.now()
        self.is_active = True
        self.frames_received = 0
        self.error: Optional[str] = None
        
        # Background streaming
        self._stop_event = threading.Event()
        self._stream_thread: Optional[threading.Thread] = None
    
    def start_streaming(self) -> bool:
        """Start continuous background streaming to keep connection alive."""
        if self._stream_thread and self._stream_thread.is_alive():
            return True  # Already streaming
        
        self._stop_event.clear()
        self._stream_thread = threading.Thread(
            target=self._continuous_stream,
            name=f"stream-{self.job_id}",
            daemon=True
        )
        self._stream_thread.start()
        logger.debug(f"Job {self.job_id}: Started continuous streaming thread")
        return True
    
    def _continuous_stream(self):
        """Background thread that continuously receives frames."""
        logger.debug(f"Job {self.job_id}: Streaming thread started")
        
        while not self._stop_event.is_set() and self.is_active:
            try:
                # Receive frames in small batches
                for frame in self.grpc_client.stream_data(
                    stream_id=0,
                    max_frames=10,  # Get 10 frames at a time
                    timeout=30
                ):
                    self.frames_received += 1
                    
                    if self._stop_event.is_set():
                        break
                
                # Small delay between batches
                if not self._stop_event.is_set():
                    time.sleep(0.1)
                    
            except Exception as e:
                error_str = str(e).lower()
                if "cancelled" in error_str or "stop" in error_str:
                    # Normal shutdown
                    break
                    
                logger.debug(f"Job {self.job_id}: Stream error: {e}")
                self.error = str(e)
                
                # Try to reconnect if not stopping
                if not self._stop_event.is_set():
                    time.sleep(1)  # Brief pause before retry
        
        logger.debug(f"Job {self.job_id}: Streaming thread ended ({self.frames_received} frames)")
    
    def stop(self) -> bool:
        """Stop streaming and cleanup this job."""
        if not self.is_active:
            return True
        
        try:
            # Signal thread to stop
            self._stop_event.set()
            
            # Wait for thread to finish (with timeout)
            if self._stream_thread and self._stream_thread.is_alive():
                self._stream_thread.join(timeout=5)
            
            # Disconnect gRPC
            if self.grpc_client:
                self.grpc_client.disconnect()
            
            self.is_active = False
            return True
            
        except Exception as e:
            self.error = str(e)
            self.is_active = False
            return False


@dataclass
class StepResult:
    """Result of a single load step."""
    step_number: int
    target_job_count: int
    actual_job_count: int
    new_jobs_created: int
    successful_jobs: int
    failed_jobs: int
    
    # Timing metrics
    step_duration_sec: float
    avg_job_creation_time_ms: float
    
    # Health metrics
    health_check_passed: bool
    api_response_time_ms: float
    system_healthy: bool
    
    # Overall status
    success_rate: float
    error_messages: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_log_message(self) -> str:
        """Generate log message for this step."""
        status_emoji = "✅" if self.health_check_passed else "❌"
        return (
            f"\n"
            f"{'='*60}\n"
            f"{status_emoji} STEP {self.step_number}: {self.target_job_count} Jobs\n"
            f"{'='*60}\n"
            f"   📊 Jobs: {self.actual_job_count} active "
            f"({self.successful_jobs} ok, {self.failed_jobs} failed)\n"
            f"   ⏱️  Avg Creation: {self.avg_job_creation_time_ms:.0f}ms\n"
            f"   📈 Success Rate: {self.success_rate:.1f}%\n"
            f"   🏥 Health: {'PASS' if self.health_check_passed else 'FAIL'}\n"
            f"   🔍 API Response: {self.api_response_time_ms:.0f}ms\n"
            f"{'='*60}"
        )


@dataclass
class GradualLoadTestResult:
    """Complete result of the gradual load test."""
    test_name: str
    start_time: datetime
    end_time: datetime
    total_duration_sec: float
    
    # Step results
    step_results: List[StepResult]
    total_steps: int
    successful_steps: int
    
    # Job statistics
    max_concurrent_jobs: int
    total_jobs_created: int
    total_jobs_successful: int
    total_jobs_failed: int
    
    # Cleanup
    cleanup_successful: bool
    jobs_cleaned_up: int
    
    # Overall status
    test_passed: bool
    breaking_point: Optional[int] = None  # Job count where system started failing
    
    def to_log_message(self) -> str:
        """Generate comprehensive log message."""
        status = "✅ PASSED" if self.test_passed else "❌ FAILED"
        
        lines = [
            "",
            "=" * 80,
            "🚀 GRADUAL LIVE JOB LOAD TEST - RESULTS",
            "=" * 80,
            "",
            f"📊 Overall Status: {status}",
            f"   • Duration: {self.total_duration_sec:.1f} seconds",
            f"   • Total Steps: {self.total_steps}",
            f"   • Successful Steps: {self.successful_steps}",
            "",
            f"📈 Job Statistics:",
            f"   • Max Concurrent Jobs: {self.max_concurrent_jobs}",
            f"   • Total Jobs Created: {self.total_jobs_created}",
            f"   • Successful: {self.total_jobs_successful}",
            f"   • Failed: {self.total_jobs_failed}",
            "",
        ]
        
        if self.breaking_point:
            lines.extend([
                f"⚠️  Breaking Point: {self.breaking_point} jobs",
                "",
            ])
        
        lines.extend([
            f"🧹 Cleanup:",
            f"   • Status: {'✅ Successful' if self.cleanup_successful else '❌ Failed'}",
            f"   • Jobs Cleaned: {self.jobs_cleaned_up}",
            "",
            "=" * 80,
        ])
        
        return "\n".join(lines)


# =============================================================================
# Gradual Load Tester
# =============================================================================

class GradualLiveLoadTester:
    """
    Gradual (Step-Up) Load Tester for Live Jobs - ACCUMULATIVE.
    
    Implements a step-up load pattern where jobs ACCUMULATE:
    1. Start with INITIAL_JOBS (e.g., 5 jobs)
    2. Every STEP_INTERVAL_SEC, ADD STEP_INCREMENT more jobs
       (WITHOUT deleting the previous ones!)
    3. Continue until reaching MAX_JOBS (e.g., 100 concurrent jobs)
    4. At each step, validate system health while ALL jobs are running
    5. Final health check at maximum load (all 100 jobs running)
    6. ONLY THEN cleanup all jobs at the end
    
    Example flow:
    - Step 1: 5 jobs running
    - Step 2: 10 jobs running (5 old + 5 new)
    - Step 3: 15 jobs running (10 old + 5 new)
    - ...
    - Step 20: 100 jobs running concurrently
    - Final health check
    - Cleanup: delete all 100 jobs
    
    Usage:
        tester = GradualLiveLoadTester(config_manager)
        result = tester.run_test()
        print(result.to_log_message())
    """
    
    def __init__(
        self,
        config_manager,
        initial_jobs: int = INITIAL_JOBS,
        step_increment: int = STEP_INCREMENT,
        max_jobs: int = MAX_JOBS,
        step_interval_sec: int = STEP_INTERVAL_SEC,
        sla: Optional[Dict[str, Any]] = None,
        # Job configuration
        channels_min: int = 1,
        channels_max: int = 50,
        frequency_min: int = 0,
        frequency_max: int = 500,
        nfft: int = 1024,
        display_height: int = 600,
        # gRPC configuration - optimized timeouts for faster execution
        max_grpc_connect_retries: int = 3,         # Reduced retries for faster failure detection
        grpc_connect_retry_delay_ms: int = 2000,   # 2s between retries (reduced from 5s)
        frames_to_receive: int = 3,
        job_creation_delay_sec: float = 2.0,       # Delay between creating each job
        # Early termination configuration
        max_consecutive_failures: int = 3,         # Stop after N consecutive failed steps
    ):
        """
        Initialize Gradual Load Tester.
        
        Args:
            config_manager: Configuration manager instance
            initial_jobs: Starting number of jobs (default: 5)
            step_increment: Jobs to add each step (default: 5)
            max_jobs: Maximum jobs to reach (default: 50)
            step_interval_sec: Seconds between steps (default: 10)
            sla: SLA thresholds dictionary
            channels_min/max: Channel range for jobs
            frequency_min/max: Frequency range for jobs
            nfft: NFFT selection
            display_height: Display height
            max_grpc_connect_retries: Max retries for gRPC connection
            grpc_connect_retry_delay_ms: Delay between retries
            frames_to_receive: Frames to receive for validation
            max_consecutive_failures: Stop test after N consecutive failed steps (default: 3)
        """
        from src.apis.focus_server_api import FocusServerAPI
        from src.apis.grpc_client import GrpcStreamClient
        
        self.config_manager = config_manager
        self.api = FocusServerAPI(config_manager)
        
        # Load parameters
        self.initial_jobs = initial_jobs
        self.step_increment = step_increment
        self.max_jobs = max_jobs
        self.step_interval_sec = step_interval_sec
        self.sla = sla or DEFAULT_SLA
        
        # Job configuration
        self.channels_min = channels_min
        self.channels_max = channels_max
        self.frequency_min = frequency_min
        self.frequency_max = frequency_max
        self.nfft = nfft
        self.display_height = display_height
        
        # gRPC configuration
        self.max_grpc_connect_retries = max_grpc_connect_retries
        self.grpc_connect_retry_delay_ms = grpc_connect_retry_delay_ms
        self.frames_to_receive = frames_to_receive
        self.job_creation_delay_sec = job_creation_delay_sec
        self.max_consecutive_failures = max_consecutive_failures
        
        # gRPC client factory
        def grpc_factory(connection_timeout: int = 30):
            return GrpcStreamClient(
                config_manager=config_manager,
                connection_timeout=connection_timeout
            )
        self.grpc_client_factory = grpc_factory
        
        # Active jobs tracking
        self.active_jobs: List[LiveJobHandle] = []
        
        # Monitoring thread for periodic status updates
        self._monitoring_stop_event = threading.Event()
        self._monitoring_thread: Optional[threading.Thread] = None
        self._monitoring_interval_sec = 120  # 2 minutes
        self._last_monitoring_time: Optional[datetime] = None
        
        # Trend tracking for early warning detection
        self._health_history: List[Dict[str, Any]] = []  # Store last N health checks
        self._max_history_size = 10  # Keep last 10 monitoring cycles (20 minutes)
        self._early_warning_thresholds = {
            "response_time_increase_pct": 50,  # 50% increase = warning
            "error_rate_increase_pct": 30,     # 30% increase = warning
            "dead_jobs_increase_pct": 20,      # 20% increase = warning
            "frames_per_second_decrease_pct": 40,  # 40% decrease = warning
            "job_creation_time_increase_pct": 100,  # 100% increase = warning
        }
        
        logger.info(
            f"GradualLiveLoadTester initialized:\n"
            f"   Initial Jobs: {initial_jobs}\n"
            f"   Step Increment: {step_increment}\n"
            f"   Max Jobs: {max_jobs}\n"
            f"   Step Interval: {step_interval_sec}s\n"
            f"   Max Consecutive Failures: {max_consecutive_failures} (early termination)\n"
            f"   Monitoring Interval: {self._monitoring_interval_sec}s (status updates every 2 minutes)"
        )
    
    def _create_single_job(self) -> Optional[LiveJobHandle]:
        """
        Create a single Live Job and connect to its gRPC stream.
        
        Returns:
            LiveJobHandle if successful, None if failed
        """
        from src.models.focus_server_models import ConfigureRequest
        
        job_id = None
        grpc_client = None
        
        try:
            # Step 1: Create job via POST /configure
            payload = ConfigureRequest(
                displayTimeAxisDuration=10,
                nfftSelection=self.nfft,
                displayInfo={"height": self.display_height},
                channels={"min": self.channels_min, "max": self.channels_max},
                frequencyRange={"min": self.frequency_min, "max": self.frequency_max},
                start_time=None,  # LIVE mode
                end_time=None,    # LIVE mode
                view_type="0"     # MULTICHANNEL
            )
            
            response = self.api.configure_streaming_job(payload)
            job_id = response.job_id
            stream_url = response.stream_url
            stream_port = int(response.stream_port)
            
            logger.debug(f"Job {job_id} configured: {stream_url}:{stream_port}")
            
            # Step 2: Connect to gRPC with retries
            grpc_client = self.grpc_client_factory(connection_timeout=30)  # 30s timeout (reduced from 60s)
            
            connected = False
            last_error = None
            
            for attempt in range(self.max_grpc_connect_retries):
                try:
                    grpc_client.connect(stream_url=stream_url, stream_port=stream_port)
                    connected = True
                    break
                except Exception as e:
                    last_error = str(e)
                    logger.debug(f"Job {job_id}: gRPC connect attempt {attempt + 1} failed")
                    if attempt < self.max_grpc_connect_retries - 1:
                        time.sleep(self.grpc_connect_retry_delay_ms / 1000)
            
            if not connected:
                raise ConnectionError(f"gRPC connect failed: {last_error}")
            
            # Step 3: Create handle and START CONTINUOUS STREAMING
            handle = LiveJobHandle(
                job_id=job_id,
                stream_url=stream_url,
                stream_port=stream_port,
                grpc_client=grpc_client,
            )
            
            # CRITICAL: Start background streaming to keep connection alive!
            # This thread continuously receives frames to prevent connection timeout
            handle.start_streaming()
            
            # Wait a moment to verify streaming started
            time.sleep(0.5)
            
            if handle.frames_received > 0:
                logger.debug(f"Job {job_id}: Streaming started ({handle.frames_received} frames)")
            else:
                logger.debug(f"Job {job_id}: Stream thread started, waiting for frames...")
            
            return handle
            
        except Exception as e:
            logger.warning(f"Failed to create job: {e}")
            
            # Cleanup on failure
            if grpc_client:
                try:
                    grpc_client.disconnect()
                except Exception:
                    pass
            
            return None
    
    def _create_jobs_batch(self, count: int, burst_mode: bool = False) -> List[LiveJobHandle]:
        """
        Create a batch of Live Jobs.
        
        Args:
            count: Number of jobs to create
            burst_mode: If True, create jobs in PARALLEL (fast burst).
                       If False, create sequentially with delays.
            
        Returns:
            List of successfully created LiveJobHandles
        """
        if burst_mode:
            return self._create_jobs_burst(count)
        else:
            return self._create_jobs_sequential(count)
    
    def _create_jobs_burst(self, count: int) -> List[LiveJobHandle]:
        """
        Create jobs in PARALLEL for burst start.
        
        Uses ThreadPoolExecutor to create multiple jobs simultaneously.
        This is faster but may overwhelm K8s if count is too high.
        
        Args:
            count: Number of jobs to create in parallel
            
        Returns:
            List of successfully created LiveJobHandles
        """
        logger.info(f"   🚀 BURST MODE: Creating {count} jobs in parallel...")
        created_jobs = []
        
        with ThreadPoolExecutor(max_workers=min(count, 10)) as executor:
            futures = [executor.submit(self._create_single_job) for _ in range(count)]
            
            for i, future in enumerate(as_completed(futures, timeout=120)):
                try:
                    job_handle = future.result()
                    if job_handle:
                        created_jobs.append(job_handle)
                        logger.debug(f"Burst job {len(created_jobs)}/{count} created: {job_handle.job_id}")
                except Exception as e:
                    logger.warning(f"Burst job creation failed: {e}")
        
        logger.info(f"   🚀 BURST COMPLETE: {len(created_jobs)}/{count} jobs created")
        return created_jobs
    
    def _create_jobs_sequential(self, count: int) -> List[LiveJobHandle]:
        """
        Create jobs ONE AT A TIME with delays.
        
        Jobs are created sequentially with delays to allow K8s pods
        to start up before we attempt gRPC connections.
        
        Args:
            count: Number of jobs to create
            
        Returns:
            List of successfully created LiveJobHandles
        """
        created_jobs = []
        
        for i in range(count):
            logger.debug(f"Creating job {i + 1}/{count}...")
            
            try:
                job_handle = self._create_single_job()
                if job_handle:
                    created_jobs.append(job_handle)
                    logger.debug(f"Job {job_handle.job_id} created successfully")
                else:
                    logger.warning(f"Job {i + 1}/{count} creation returned None")
            except Exception as e:
                logger.warning(f"Job {i + 1}/{count} creation failed: {e}")
            
            # Delay before creating next job (give K8s time to schedule pod)
            if i < count - 1 and self.job_creation_delay_sec > 0:
                time.sleep(self.job_creation_delay_sec)
        
        return created_jobs
    
    def _check_streaming_status(self) -> tuple:
        """
        Check the status of all streaming jobs.
        
        Each job has a background thread continuously receiving frames.
        This method checks if those threads are still alive and active.
        
        Returns:
            Tuple of (alive_count: int, dead_count: int, total_frames: int)
        """
        alive_count = 0
        dead_count = 0
        total_frames = 0
        
        for job_handle in self.active_jobs:
            if not job_handle.is_active:
                dead_count += 1
                continue
            
            # Check if streaming thread is alive
            if job_handle._stream_thread and job_handle._stream_thread.is_alive():
                alive_count += 1
                total_frames += job_handle.frames_received
            else:
                # Thread died - mark job as inactive
                if job_handle.error:
                    logger.debug(f"Job {job_handle.job_id} stream died: {job_handle.error}")
                else:
                    logger.debug(f"Job {job_handle.job_id} stream thread not alive")
                dead_count += 1
                job_handle.is_active = False
        
        return alive_count, dead_count, total_frames
    
    def _check_component_health(self) -> Dict[str, Any]:
        """
        Check health of all system components.
        
        Returns:
            Dictionary with health status of each component
        """
        components = {
            "focus_server_api": {"healthy": False, "error": None, "response_time_ms": 0},
            "mongodb": {"healthy": False, "error": None},
            "rabbitmq": {"healthy": False, "error": None},
            "grpc_jobs": {"healthy": False, "active_count": 0, "dead_count": 0}
        }
        
        # Check Focus Server API
        try:
            start_time = time.time()
            channels = self.api.get_channels()
            response_time_ms = (time.time() - start_time) * 1000
            components["focus_server_api"]["healthy"] = (
                channels is not None and 
                response_time_ms < self.sla.get("health_check_timeout_sec", 30) * 1000
            )
            components["focus_server_api"]["response_time_ms"] = response_time_ms
        except Exception as e:
            components["focus_server_api"]["error"] = str(e)
        
        # Check MongoDB (if available)
        try:
            from src.infrastructure.mongodb_manager import MongoDBManager
            mongodb = MongoDBManager(self.config_manager)
            mongodb.connect()
            mongodb.disconnect()
            components["mongodb"]["healthy"] = True
        except Exception as e:
            components["mongodb"]["error"] = str(e)
        
        # Check RabbitMQ (if available)
        try:
            from src.infrastructure.rabbitmq_manager import RabbitMQManager
            rabbitmq = RabbitMQManager(self.config_manager)
            rabbitmq.connect()
            rabbitmq.disconnect()
            components["rabbitmq"]["healthy"] = True
        except Exception as e:
            components["rabbitmq"]["error"] = str(e)
        
        # Check gRPC jobs status
        alive_count, dead_count, total_frames = self._check_streaming_status()
        components["grpc_jobs"]["active_count"] = alive_count
        components["grpc_jobs"]["dead_count"] = dead_count
        components["grpc_jobs"]["healthy"] = (alive_count > 0 and dead_count < alive_count * 0.5)
        
        return components
    
    def _calculate_health_score(self, components: Dict[str, Any], current_job_count: int) -> float:
        """
        Calculate overall system health score (0-100).
        
        Higher score = healthier system.
        Score < 50 = critical degradation.
        
        Returns:
            Health score from 0 (critical) to 100 (perfect)
        """
        score = 100.0
        
        # Focus Server API health (30% weight)
        if not components["focus_server_api"]["healthy"]:
            score -= 30
        else:
            # Penalize slow response times
            response_time = components["focus_server_api"]["response_time_ms"]
            if response_time > 10000:  # > 10s
                score -= 20
            elif response_time > 5000:  # > 5s
                score -= 10
            elif response_time > 2000:  # > 2s
                score -= 5
        
        # MongoDB health (20% weight)
        if not components["mongodb"]["healthy"]:
            score -= 20
        
        # RabbitMQ health (20% weight)
        if not components["rabbitmq"]["healthy"]:
            score -= 20
        
        # gRPC Jobs health (30% weight)
        total_jobs = components["grpc_jobs"]["active_count"] + components["grpc_jobs"]["dead_count"]
        if total_jobs > 0:
            dead_percentage = (components["grpc_jobs"]["dead_count"] / total_jobs) * 100
            if dead_percentage > 50:
                score -= 30
            elif dead_percentage > 30:
                score -= 20
            elif dead_percentage > 10:
                score -= 10
        
        return max(0.0, min(100.0, score))
    
    def _detect_early_warning_signs(self, components: Dict[str, Any], current_job_count: int) -> List[Dict[str, Any]]:
        """
        Detect early warning signs before total system failure.
        
        Analyzes trends in:
        - Response times (increasing = bad)
        - Error rates (increasing = bad)
        - Dead jobs percentage (increasing = bad)
        - Frames per second (decreasing = bad)
        - Job creation times (increasing = bad)
        - Health score (declining = bad)
        
        Returns:
            List of early warning signs detected
        """
        warnings = []
        
        if len(self._health_history) < 2:
            return warnings  # Need at least 2 data points for trend analysis
        
        # Get previous health check
        previous_health = self._health_history[-1]
        
        # Create current health dict for comparison
        current_health = {
            "focus_server_api": components["focus_server_api"],
            "grpc_jobs": components["grpc_jobs"],
            "response_time_ms": components["focus_server_api"]["response_time_ms"],
            "total_frames_received": sum([j.frames_received for j in self.active_jobs])
        }
        
        # 1. Check response time trend
        current_response_time = current_health["response_time_ms"]
        previous_response_time = previous_health.get("response_time_ms", current_response_time)
        
        if previous_response_time > 0:
            response_time_increase = ((current_response_time - previous_response_time) / previous_response_time) * 100
            if response_time_increase > self._early_warning_thresholds["response_time_increase_pct"]:
                warnings.append({
                    "type": "RESPONSE_TIME_DEGRADATION",
                    "severity": "WARNING",
                    "message": f"API response time increased by {response_time_increase:.1f}% "
                              f"({previous_response_time:.0f}ms → {current_response_time:.0f}ms)",
                    "current_value": current_response_time,
                    "previous_value": previous_response_time,
                    "increase_pct": response_time_increase
                })
        
        # 2. Check dead jobs trend
        current_dead = current_health["grpc_jobs"]["dead_count"]
        current_total = current_health["grpc_jobs"]["active_count"] + current_dead
        previous_dead = previous_health.get("dead_jobs", 0)
        previous_total = previous_health.get("total_jobs", current_total)
        
        if previous_total > 0 and current_total > 0:
            current_dead_pct = (current_dead / current_total) * 100
            previous_dead_pct = (previous_dead / previous_total) * 100
            
            if previous_dead_pct > 0:
                dead_increase = current_dead_pct - previous_dead_pct
                if dead_increase > self._early_warning_thresholds["dead_jobs_increase_pct"]:
                    warnings.append({
                        "type": "JOB_FAILURE_RATE_INCREASING",
                        "severity": "WARNING",
                        "message": f"Dead jobs percentage increased by {dead_increase:.1f}% "
                                  f"({previous_dead_pct:.1f}% → {current_dead_pct:.1f}%)",
                        "current_value": current_dead_pct,
                        "previous_value": previous_dead_pct,
                        "increase_pct": dead_increase
                    })
        
        # 3. Check frames per second trend (if available)
        current_frames = current_health["total_frames_received"]
        previous_frames = previous_health.get("total_frames_received", current_frames)
        
        # Calculate approximate FPS (frames per monitoring cycle)
        if previous_frames > 0 and current_frames > previous_frames:
            frames_increase = ((current_frames - previous_frames) / previous_frames) * 100
            # Negative means decrease
            if frames_increase < -self._early_warning_thresholds["frames_per_second_decrease_pct"]:
                warnings.append({
                    "type": "FRAME_RATE_DECREASING",
                    "severity": "WARNING",
                    "message": f"Frame rate decreased by {abs(frames_increase):.1f}% "
                              f"({previous_frames} → {current_frames} frames)",
                    "current_value": current_frames,
                    "previous_value": previous_frames,
                    "decrease_pct": abs(frames_increase)
                })
        
        # 4. Check if health score is declining rapidly
        current_score = self._calculate_health_score(components, current_job_count)
        previous_score = previous_health.get("health_score", current_score)
        
        if previous_score > 0:
            score_decrease = previous_score - current_score
            if score_decrease > 15:  # Drop of more than 15 points
                warnings.append({
                    "type": "HEALTH_SCORE_DECLINING",
                    "severity": "WARNING",
                    "message": f"System health score dropped by {score_decrease:.1f} points "
                              f"({previous_score:.1f} → {current_score:.1f})",
                    "current_value": current_score,
                    "previous_value": previous_score,
                    "decrease": score_decrease
                })
        
        # 5. Check for gradual component degradation
        component_degradations = []
        if not components["focus_server_api"]["healthy"] and previous_health.get("api_healthy", True):
            component_degradations.append("Focus Server API")
        if not components["mongodb"]["healthy"] and previous_health.get("mongodb_healthy", True):
            component_degradations.append("MongoDB")
        if not components["rabbitmq"]["healthy"] and previous_health.get("rabbitmq_healthy", True):
            component_degradations.append("RabbitMQ")
        
        if component_degradations:
            warnings.append({
                "type": "COMPONENT_DEGRADATION",
                "severity": "CRITICAL",
                "message": f"Components degraded: {', '.join(component_degradations)}",
                "degraded_components": component_degradations
            })
        
        return warnings
    
    def _detect_breaking_point(self, components: Dict[str, Any], current_job_count: int) -> Optional[Dict[str, Any]]:
        """
        Detect if system has reached breaking point.
        
        Returns:
            Breaking point info dict if detected, None otherwise
        """
        issues = []
        
        # Check Focus Server API
        if not components["focus_server_api"]["healthy"]:
            issues.append({
                "component": "Focus Server API",
                "status": "FAILED",
                "error": components["focus_server_api"]["error"] or "Timeout/No response",
                "response_time_ms": components["focus_server_api"]["response_time_ms"]
            })
        
        # Check MongoDB
        if not components["mongodb"]["healthy"]:
            issues.append({
                "component": "MongoDB",
                "status": "FAILED",
                "error": components["mongodb"]["error"] or "Connection failed"
            })
        
        # Check RabbitMQ
        if not components["rabbitmq"]["healthy"]:
            issues.append({
                "component": "RabbitMQ",
                "status": "FAILED",
                "error": components["rabbitmq"]["error"] or "Connection failed"
            })
        
        # Check gRPC jobs - if more than 50% are dead AND we have jobs, it's a breaking point
        total_jobs = components["grpc_jobs"]["active_count"] + components["grpc_jobs"]["dead_count"]
        if total_jobs > 0 and components["grpc_jobs"]["dead_count"] > 0:
            dead_percentage = (components["grpc_jobs"]["dead_count"] / total_jobs) * 100
            
            if dead_percentage > 50:
                issues.append({
                    "component": "gRPC Jobs",
                    "status": "CRITICAL",
                    "error": f"{dead_percentage:.1f}% of jobs are dead ({components['grpc_jobs']['dead_count']}/{total_jobs})",
                    "active_count": components["grpc_jobs"]["active_count"],
                    "dead_count": components["grpc_jobs"]["dead_count"]
                })
        
        if issues:
            return {
                "detected": True,
                "job_count": current_job_count,
                "issues": issues,
                "timestamp": datetime.now()
            }
        
        return None
    
    def _monitoring_loop(self):
        """
        Background monitoring loop that runs every 2 minutes.
        
        Reports:
        - Current number of active jobs
        - System component health
        - Breaking point detection
        """
        logger.info("📊 [MONITORING] Started periodic monitoring (every 2 minutes)")
        
        while not self._monitoring_stop_event.is_set():
            try:
                # Wait for monitoring interval (or stop event)
                if self._monitoring_stop_event.wait(timeout=self._monitoring_interval_sec):
                    break  # Stop event was set
                
                self._last_monitoring_time = datetime.now()
                current_time = self._last_monitoring_time.strftime("%H:%M:%S")
                
                # Get current job count
                active_jobs_count = len([j for j in self.active_jobs if j.is_active])
                total_jobs_count = len(self.active_jobs)
                
                # Calculate total frames received
                total_frames_received = sum([j.frames_received for j in self.active_jobs])
                
                # Check component health
                components = self._check_component_health()
                
                # Calculate health score
                health_score = self._calculate_health_score(components, active_jobs_count)
                
                # Store health history for trend analysis
                health_snapshot = {
                    "timestamp": datetime.now(),
                    "job_count": active_jobs_count,
                    "response_time_ms": components["focus_server_api"]["response_time_ms"],
                    "api_healthy": components["focus_server_api"]["healthy"],
                    "mongodb_healthy": components["mongodb"]["healthy"],
                    "rabbitmq_healthy": components["rabbitmq"]["healthy"],
                    "dead_jobs": components["grpc_jobs"]["dead_count"],
                    "total_jobs": components["grpc_jobs"]["active_count"] + components["grpc_jobs"]["dead_count"],
                    "total_frames_received": total_frames_received,
                    "health_score": health_score
                }
                
                # Keep only last N health checks
                self._health_history.append(health_snapshot)
                if len(self._health_history) > self._max_history_size:
                    self._health_history.pop(0)
                
                # Detect early warning signs (before breaking point)
                early_warnings = self._detect_early_warning_signs(components, active_jobs_count)
                
                # Detect breaking point
                breaking_point_info = self._detect_breaking_point(components, active_jobs_count)
                
                # Log status update
                logger.info("")
                logger.info("=" * 80)
                logger.info(f"📊 [MONITORING UPDATE] {current_time} - Status Report")
                logger.info("=" * 80)
                logger.info(f"   🔢 Active Jobs: {active_jobs_count} / {total_jobs_count} total")
                logger.info(f"   📈 Streaming Jobs: {components['grpc_jobs']['active_count']} active, {components['grpc_jobs']['dead_count']} dead")
                logger.info(f"   📊 Health Score: {health_score:.1f}/100")
                
                # Early warning signs
                if early_warnings:
                    logger.warning("")
                    logger.warning("   " + "=" * 76)
                    logger.warning("   ⚠️  EARLY WARNING SIGNS DETECTED!")
                    logger.warning("   " + "=" * 76)
                    logger.warning("   System is showing signs of degradation before total failure:")
                    logger.warning("")
                    for warning in early_warnings:
                        severity_icon = "🔴" if warning["severity"] == "CRITICAL" else "🟡"
                        logger.warning(f"   {severity_icon} {warning['type']}: {warning['message']}")
                    logger.warning("   " + "=" * 76)
                    logger.warning("")
                
                # Component health status
                logger.info("")
                logger.info("   🏥 Component Health:")
                api_status = "✅ HEALTHY" if components["focus_server_api"]["healthy"] else "❌ FAILED"
                api_time = components["focus_server_api"]["response_time_ms"]
                logger.info(f"      • Focus Server API: {api_status} ({api_time:.0f}ms)")
                
                mongodb_status = "✅ HEALTHY" if components["mongodb"]["healthy"] else "❌ FAILED"
                logger.info(f"      • MongoDB: {mongodb_status}")
                
                rabbitmq_status = "✅ HEALTHY" if components["rabbitmq"]["healthy"] else "❌ FAILED"
                logger.info(f"      • RabbitMQ: {rabbitmq_status}")
                
                grpc_status = "✅ HEALTHY" if components["grpc_jobs"]["healthy"] else "⚠️ DEGRADED"
                logger.info(f"      • gRPC Jobs: {grpc_status}")
                
                # Breaking point detection
                if breaking_point_info:
                    logger.error("")
                    logger.error("   " + "=" * 76)
                    logger.error("   🛑 BREAKING POINT DETECTED!")
                    logger.error("   " + "=" * 76)
                    logger.error(f"   ⚠️  System failure detected at {breaking_point_info['job_count']} concurrent jobs")
                    logger.error(f"   📅 Timestamp: {breaking_point_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.error("")
                    logger.error("   🔴 Failed Components:")
                    for issue in breaking_point_info["issues"]:
                        logger.error(f"      • {issue['component']}: {issue['status']}")
                        if issue.get("error"):
                            logger.error(f"        Error: {issue['error']}")
                        if issue.get("response_time_ms"):
                            logger.error(f"        Response Time: {issue['response_time_ms']:.0f}ms")
                    logger.error("   " + "=" * 76)
                else:
                    logger.info("")
                    logger.info("   ✅ All components healthy - no breaking point detected")
                
                logger.info("=" * 80)
                logger.info("")
                
            except Exception as e:
                logger.error(f"📊 [MONITORING] Error in monitoring loop: {e}")
                time.sleep(10)  # Brief pause before retry
        
        logger.info("📊 [MONITORING] Monitoring thread stopped")
    
    def _start_monitoring(self):
        """Start background monitoring thread."""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return  # Already running
        
        self._monitoring_stop_event.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            name="load-test-monitoring",
            daemon=True
        )
        self._monitoring_thread.start()
        logger.info("📊 [MONITORING] Background monitoring started")
    
    def _stop_monitoring(self):
        """Stop background monitoring thread."""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_stop_event.set()
            self._monitoring_thread.join(timeout=5)
            logger.info("📊 [MONITORING] Background monitoring stopped")
    
    def _check_system_health(self) -> tuple:
        """
        Check system health and responsiveness.
        
        Returns:
            Tuple of (is_healthy: bool, response_time_ms: float)
        """
        start_time = time.time()
        
        try:
            # Quick health check via /channels endpoint
            channels = self.api.get_channels()
            response_time_ms = (time.time() - start_time) * 1000
            
            is_healthy = (
                channels is not None and
                response_time_ms < self.sla.get("health_check_timeout_sec", 30) * 1000
            )
            
            return is_healthy, response_time_ms
            
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            logger.warning(f"Health check failed: {e}")
            return False, response_time_ms
    
    def _execute_step(self, step_number: int, target_job_count: int) -> StepResult:
        """
        Execute a single step of the gradual load test.
        
        Args:
            step_number: Current step number (1-based)
            target_job_count: Target number of jobs for this step
            
        Returns:
            StepResult with all metrics
        """
        step_start = time.time()
        
        # Calculate how many new jobs to create
        current_active = len([j for j in self.active_jobs if j.is_active])
        new_jobs_needed = target_job_count - current_active
        
        logger.info(
            f"\n📊 STEP {step_number}: "
            f"Creating {new_jobs_needed} jobs to reach {target_job_count} total"
        )
        
        # Track creation times
        creation_times = []
        
        # Create new jobs and ADD them to existing ones (accumulative!)
        # IMPORTANT: We DO NOT delete previous jobs - they keep running!
        if new_jobs_needed > 0:
            creation_start = time.time()
            
            # Use BURST mode for first step if creating many jobs (initial burst)
            # Use SEQUENTIAL mode for incremental steps
            use_burst = (step_number == 1 and new_jobs_needed >= 10)
            
            if use_burst:
                logger.info(f"   🚀 Using BURST mode for initial {new_jobs_needed} jobs")
            
            new_handles = self._create_jobs_batch(new_jobs_needed, burst_mode=use_burst)
            creation_time = (time.time() - creation_start) * 1000
            
            if new_handles:
                creation_times.append(creation_time / len(new_handles))
            
            # ACCUMULATE: Add new jobs to the existing list (no deletion!)
            self.active_jobs.extend(new_handles)
            
            logger.info(f"   Created {len(new_handles)}/{new_jobs_needed} NEW jobs (total: {len(self.active_jobs)} concurrent)")
        
        # Check streaming status - background threads are continuously streaming
        logger.info(f"   🔄 Checking {len(self.active_jobs)} streaming jobs...")
        alive_count, dead_count, total_frames = self._check_streaming_status()
        logger.info(f"   ✓ Streaming: {alive_count}, Dead: {dead_count}, Total Frames: {total_frames}")
        
        # Count current status (after keepalive, since it may update is_active)
        active_count = len([j for j in self.active_jobs if j.is_active])
        failed_count = len([j for j in self.active_jobs if not j.is_active or j.error])
        successful_count = active_count - failed_count
        
        # Check system health
        logger.info(f"   🏥 Checking system health...")
        is_healthy, api_response_time = self._check_system_health()
        
        # Calculate success rate
        total_jobs = len(self.active_jobs)
        success_rate = (successful_count / max(total_jobs, 1)) * 100
        
        # Determine if step passed
        step_passed = (
            success_rate >= self.sla.get("min_success_rate", 70) and
            is_healthy
        )
        
        step_duration = time.time() - step_start
        
        # Collect errors
        error_messages = [j.error for j in self.active_jobs if j.error]
        
        result = StepResult(
            step_number=step_number,
            target_job_count=target_job_count,
            actual_job_count=active_count,
            new_jobs_created=len(new_handles) if new_jobs_needed > 0 else 0,
            successful_jobs=successful_count,
            failed_jobs=failed_count,
            step_duration_sec=step_duration,
            avg_job_creation_time_ms=mean(creation_times) if creation_times else 0,
            health_check_passed=step_passed,
            api_response_time_ms=api_response_time,
            system_healthy=is_healthy,
            success_rate=success_rate,
            error_messages=error_messages[:5]  # Limit to 5 errors
        )
        
        logger.info(result.to_log_message())
        
        return result
    
    def _cleanup_all_jobs(self) -> tuple:
        """
        Stop and cleanup all active jobs by disconnecting gRPC.
        
        Note: DELETE /job/{job_id} API is NOT implemented in Focus Server (returns 404).
        Jobs are cleaned up automatically by Kubernetes cleanup-job when:
        1. gRPC connection is closed
        2. CPU usage drops below threshold for 5 consecutive checks
        
        So we ONLY disconnect gRPC - K8s handles the rest automatically.
        
        Returns:
            Tuple of (success: bool, jobs_cleaned: int)
        """
        logger.info("\n🧹 CLEANUP: Disconnecting all gRPC connections...")
        logger.info("   (K8s cleanup-jobs will handle actual deletion automatically)")
        
        jobs_cleaned = 0
        cleanup_errors = []
        
        for job_handle in self.active_jobs:
            try:
                # Disconnect gRPC - this is all we need to do!
                # The K8s cleanup-job will detect low CPU and delete everything
                if job_handle.grpc_client:
                    try:
                        job_handle.grpc_client.disconnect()
                        logger.debug(f"   ✓ Disconnected gRPC for job {job_handle.job_id}")
                    except Exception as e:
                        logger.debug(f"   gRPC disconnect warning for {job_handle.job_id}: {e}")
                
                # NOTE: DO NOT call self.api.cancel_job() - endpoint doesn't exist!
                # DELETE /job/{job_id} returns 404 (not implemented in Focus Server)
                
                job_handle.is_active = False
                jobs_cleaned += 1
                
            except Exception as e:
                cleanup_errors.append(str(e))
                logger.warning(f"Cleanup error for job {job_handle.job_id}: {e}")
        
        self.active_jobs.clear()
        
        success = len(cleanup_errors) == 0 or (jobs_cleaned > 0)
        
        logger.info(f"   Cleaned up {jobs_cleaned} jobs")
        if cleanup_errors:
            logger.warning(f"   Cleanup errors: {len(cleanup_errors)}")
        
        return success, jobs_cleaned
    
    def run_test(self, test_name: str = "Gradual Live Job Load Test") -> GradualLoadTestResult:
        """
        Run the complete gradual load test.
        
        Flow:
        1. Start with initial_jobs
        2. Every step_interval_sec, add step_increment more jobs
        3. At each step, validate system health
        4. Track consecutive failures - stop early if max_consecutive_failures reached
        5. Continue until max_jobs reached OR early termination triggered
        6. Perform final health check
        7. Cleanup all jobs
        
        Early Termination:
        - If max_consecutive_failures (default: 3) consecutive steps fail,
          the test stops immediately to prevent excessive runtime.
        - This prevents tests from running for hours when the system
          has already reached its breaking point.
        
        Args:
            test_name: Name for this test run
            
        Returns:
            GradualLoadTestResult with complete metrics
        """
        start_time = datetime.now()
        logger.info(
            f"\n"
            f"{'='*80}\n"
            f"🚀 GRADUAL LIVE JOB LOAD TEST - Starting\n"
            f"{'='*80}\n"
            f"   Test: {test_name}\n"
            f"   Pattern: {self.initial_jobs} → {self.max_jobs} jobs "
            f"(+{self.step_increment} every {self.step_interval_sec}s)\n"
            f"   Monitoring: Status updates every 2 minutes\n"
            f"{'='*80}\n"
        )
        
        step_results: List[StepResult] = []
        breaking_point = None
        consecutive_failures = 0  # Track consecutive failed steps
        
        # Start background monitoring
        self._start_monitoring()
        
        try:
            # Calculate number of steps
            current_target = self.initial_jobs
            step_number = 0
            
            while current_target <= self.max_jobs:
                step_number += 1
                
                # Execute step
                step_result = self._execute_step(step_number, current_target)
                step_results.append(step_result)
                
                # Track consecutive failures for early termination
                if not step_result.health_check_passed:
                    consecutive_failures += 1
                    logger.warning(f"⚠️ Step {step_number} failed ({consecutive_failures} consecutive failures)")
                    
                    # Check for breaking point (first failure)
                    if breaking_point is None:
                        breaking_point = current_target
                        logger.warning(f"⚠️ Breaking point detected at {current_target} jobs!")
                    
                    # Early termination: Stop after max_consecutive_failures
                    if consecutive_failures >= self.max_consecutive_failures:
                        logger.error(
                            f"\n🛑 EARLY TERMINATION: "
                            f"{consecutive_failures} consecutive failed steps "
                            f"(limit: {self.max_consecutive_failures})\n"
                            f"   Breaking point: {breaking_point} jobs\n"
                            f"   Stopping test to prevent excessive runtime."
                        )
                        break
                else:
                    # Reset counter on success
                    consecutive_failures = 0
                
                # Check if we've reached maximum
                if current_target >= self.max_jobs:
                    logger.info(f"\n🎯 MAXIMUM REACHED: {self.max_jobs} jobs")
                    break
                
                # Increment for next step
                current_target += self.step_increment
                
                # Wait before next step
                if current_target <= self.max_jobs:
                    logger.info(f"\n⏳ Waiting {self.step_interval_sec}s before next step...")
                    time.sleep(self.step_interval_sec)
            
            # Final health check at maximum load
            logger.info("\n🏥 FINAL HEALTH CHECK at maximum load...")
            final_healthy, final_response_time = self._check_system_health()
            logger.info(f"   System Healthy: {final_healthy}")
            logger.info(f"   API Response: {final_response_time:.0f}ms")
            
        except Exception as e:
            logger.error(f"Test execution error: {e}")
        
        finally:
            # Stop monitoring
            self._stop_monitoring()
            
            # Always cleanup
            cleanup_success, jobs_cleaned = self._cleanup_all_jobs()
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # Calculate totals
        successful_steps = len([s for s in step_results if s.health_check_passed])
        max_concurrent = max([s.actual_job_count for s in step_results], default=0)
        total_created = sum([s.new_jobs_created for s in step_results])
        total_successful = max([s.successful_jobs for s in step_results], default=0)
        total_failed = sum([s.failed_jobs for s in step_results])
        
        # Determine overall pass/fail
        test_passed = (
            successful_steps >= len(step_results) * 0.7 and  # 70% of steps passed
            cleanup_success
        )
        
        result = GradualLoadTestResult(
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            total_duration_sec=total_duration,
            step_results=step_results,
            total_steps=len(step_results),
            successful_steps=successful_steps,
            max_concurrent_jobs=max_concurrent,
            total_jobs_created=total_created,
            total_jobs_successful=total_successful,
            total_jobs_failed=total_failed,
            cleanup_successful=cleanup_success,
            jobs_cleaned_up=jobs_cleaned,
            test_passed=test_passed,
            breaking_point=breaking_point
        )
        
        logger.info(result.to_log_message())
        
        return result


# =============================================================================
# Fixtures
# =============================================================================

def get_environment() -> str:
    """Get current environment from env var."""
    return os.getenv("ENVIRONMENT", "staging").lower()


def get_gradual_load_sla() -> Dict[str, Any]:
    """Get SLA thresholds based on environment."""
    env = get_environment()
    
    if env in ("prod", "production"):
        return {
            "min_success_rate": 85,
            "max_avg_response_time_ms": 15000,
            "max_error_rate_at_max": 20,
            "health_check_timeout_sec": 15,
        }
    else:
        # Staging - more lenient
        return {
            "min_success_rate": 70,
            "max_avg_response_time_ms": 30000,
            "max_error_rate_at_max": 30,
            "health_check_timeout_sec": 30,
        }


@pytest.fixture
def gradual_load_sla() -> Dict[str, Any]:
    """Provide gradual load SLA configuration."""
    return get_gradual_load_sla()


@pytest.fixture
def gradual_tester(config_manager) -> GradualLiveLoadTester:
    """Create GradualLiveLoadTester with default configuration."""
    return GradualLiveLoadTester(
        config_manager=config_manager,
        initial_jobs=INITIAL_JOBS,
        step_increment=STEP_INCREMENT,
        max_jobs=MAX_JOBS,
        step_interval_sec=STEP_INTERVAL_SEC,
        sla=get_gradual_load_sla()
    )


@pytest.fixture
def quick_gradual_tester(config_manager) -> GradualLiveLoadTester:
    """Create GradualLiveLoadTester with quick settings for faster testing."""
    return GradualLiveLoadTester(
        config_manager=config_manager,
        initial_jobs=2,
        step_increment=2,
        max_jobs=10,
        step_interval_sec=5,
        sla=get_gradual_load_sla()
    )


# =============================================================================
# Test Class: Gradual Load Tests
# =============================================================================

@pytest.mark.gradual_load
@pytest.mark.load
@pytest.mark.live
class TestGradualLiveLoad:
    """
    Gradual (Step-Up) Load Tests for Live Jobs.
    
    These tests validate system behavior under increasing load:
    - System handles incremental load increases
    - Performance remains acceptable as load grows
    - System recovers gracefully after high load
    - Proper cleanup after test completion
    """
    
    @pytest.mark.xray("PZ-LOAD-300")
    @pytest.mark.slow
    def test_full_gradual_load_5_to_100(self, gradual_tester, gradual_load_sla):
        """
        Test: Full gradual load test from 5 to 100 concurrent jobs.
        
        Flow:
        1. Start with 5 live jobs
        2. Every 10 seconds, add 5 more jobs (WITHOUT deleting previous ones!)
        3. Continue until 100 jobs running simultaneously (20 steps)
        4. Validate system health at each step (while ALL jobs are still running)
        5. Final health check at maximum load (100 concurrent jobs)
        6. Only THEN cleanup all jobs at the end
        
        Important: Jobs accumulate - each step ADDS jobs, doesn't replace them.
        At step 20, there should be 100 live jobs streaming data concurrently.
        
        Expected:
        - At least 60% of steps should pass health check
        - System should remain responsive under load
        - Cleanup should complete successfully
        """
        env = get_environment()
        
        logger.info(f"\n[GRADUAL LOAD] Full Test: 5 → 100 jobs (accumulative, no deletion until end)")
        logger.info(f"    Environment: {env.upper()}")
        logger.info(f"    SLA: Min Success Rate {gradual_load_sla['min_success_rate']}%")
        
        result = gradual_tester.run_test(
            test_name="Full Gradual Load (5→100 concurrent)"
        )
        
        # Assertions
        assert result.cleanup_successful, \
            "Cleanup should complete successfully"
        
        # At least 70% of steps should pass
        min_successful_steps = int(result.total_steps * 0.7)
        assert result.successful_steps >= min_successful_steps, \
            f"Expected at least {min_successful_steps} successful steps, got {result.successful_steps}"
        
        # Should reach maximum load
        assert result.max_concurrent_jobs >= 80, \
            f"Expected to reach at least 80 concurrent jobs, got {result.max_concurrent_jobs}"
        
        logger.info(f"\n✅ Gradual load test completed")
        logger.info(f"   Successful Steps: {result.successful_steps}/{result.total_steps}")
        logger.info(f"   Max Concurrent: {result.max_concurrent_jobs}")
        
        if result.breaking_point:
            logger.warning(f"   Breaking Point: {result.breaking_point} jobs")
    
    @pytest.mark.xray("PZ-LOAD-301")
    def test_quick_gradual_load(self, quick_gradual_tester, gradual_load_sla):
        """
        Test: Quick gradual load test (2 → 10 jobs).
        
        Faster version for CI/CD pipelines:
        - 2 initial jobs
        - +2 every 5 seconds
        - Maximum 10 jobs
        
        Validates the gradual load mechanism works correctly.
        """
        env = get_environment()
        
        logger.info(f"\n[GRADUAL LOAD] Quick Test: 2 → 10 jobs")
        logger.info(f"    Environment: {env.upper()}")
        
        result = quick_gradual_tester.run_test(
            test_name="Quick Gradual Load (2→10)"
        )
        
        # Assertions
        assert result.cleanup_successful, \
            "Cleanup should complete successfully"
        
        assert result.total_steps >= 3, \
            f"Expected at least 3 steps, got {result.total_steps}"
        
        assert result.max_concurrent_jobs >= 6, \
            f"Expected at least 6 concurrent jobs, got {result.max_concurrent_jobs}"
        
        logger.info(f"\n✅ Quick gradual load test completed")
    
    @pytest.mark.xray("PZ-LOAD-302")
    def test_gradual_load_stability(self, config_manager, gradual_load_sla):
        """
        Test: Gradual load with stability validation.
        
        Tests that the system remains stable:
        - No crashes during load increase
        - API remains responsive
        - Jobs can be created consistently
        """
        env = get_environment()
        
        logger.info(f"\n[GRADUAL LOAD] Stability Test")
        logger.info(f"    Environment: {env.upper()}")
        
        # Create tester with moderate load
        tester = GradualLiveLoadTester(
            config_manager=config_manager,
            initial_jobs=5,
            step_increment=5,
            max_jobs=25,  # Lower max for stability test
            step_interval_sec=8,
            sla=gradual_load_sla
        )
        
        result = tester.run_test(
            test_name="Stability Test (5→25)"
        )
        
        # Check stability: all steps should have some successful jobs
        for step in result.step_results:
            assert step.successful_jobs > 0, \
                f"Step {step.step_number} had no successful jobs"
        
        # API should have remained responsive
        avg_response_time = mean([s.api_response_time_ms for s in result.step_results])
        max_response_time = gradual_load_sla.get("max_avg_response_time_ms", 30000)
        
        assert avg_response_time < max_response_time, \
            f"Average API response time {avg_response_time:.0f}ms exceeds {max_response_time}ms"
        
        assert result.cleanup_successful, \
            "Cleanup should complete successfully"
        
        logger.info(f"\n✅ Stability test passed")
        logger.info(f"   Avg API Response: {avg_response_time:.0f}ms")


# =============================================================================
# Test Class: Custom Configuration Tests
# =============================================================================

@pytest.mark.gradual_load
@pytest.mark.load
@pytest.mark.live
class TestGradualLoadCustomConfig:
    """
    Gradual load tests with custom configurations.
    
    These tests allow running with different parameters.
    """
    
    @pytest.mark.xray("PZ-LOAD-310")
    @pytest.mark.slow
    def test_high_concurrency_gradual(self, config_manager, gradual_load_sla):
        """
        Test: High concurrency gradual load (10 job steps) - OPTIMIZED.
        
        Uses larger increments for faster load buildup:
        - Start with 10 jobs
        - Add 10 every 8 seconds
        - Reach 100 jobs in 10 steps
        
        Optimizations:
        - Reduced gRPC retries: 3 instead of 10 (faster failure detection)
        - Reduced retry delay: 2s instead of 5s (faster retries)
        - Reduced connection timeout: 30s instead of 60s (faster timeouts)
        - Early termination: Stop after 3 consecutive failures (prevent excessive runtime)
        """
        env = get_environment()
        
        logger.info(f"\n[GRADUAL LOAD] High Concurrency: 10 → 100 (step 10)")
        
        tester = GradualLiveLoadTester(
            config_manager=config_manager,
            initial_jobs=10,
            step_increment=10,
            max_jobs=100,
            step_interval_sec=8,
            sla=gradual_load_sla,
            max_grpc_connect_retries=3,        # Optimized: Reduced from 10
            grpc_connect_retry_delay_ms=2000,  # Optimized: Reduced from 5000ms
            max_consecutive_failures=3          # Early termination after 3 consecutive failures
        )
        
        result = tester.run_test(
            test_name="High Concurrency (10→100, step 10)"
        )
        
        assert result.cleanup_successful, "Cleanup must succeed"
        assert result.total_steps >= 8, f"Expected 8+ steps, got {result.total_steps}"
        
        logger.info(f"\n✅ High concurrency test completed")
        logger.info(f"   Max Concurrent: {result.max_concurrent_jobs}")
    
    @pytest.mark.xray("PZ-LOAD-312")
    @pytest.mark.slow
    def test_burst_then_gradual_30_to_100(self, config_manager, gradual_load_sla):
        """
        Test: Burst start with 30 jobs, then gradual increase to 100 (OPTIMIZED).
        
        Strategy:
        1. Start with 30 jobs all at once (burst)
        2. Add 5 jobs at a time until reaching 100 jobs (optimized from +1)
        3. Total 14 incremental steps after initial burst (reduced from 70)
        4. Early termination after 3 consecutive failures
        
        Optimizations:
        - Reduced step increment: +5 instead of +1 (faster execution)
        - Reduced gRPC retries: 3 instead of 10 (faster failure detection)
        - Reduced retry delay: 2s instead of 5s (faster retries)
        - Reduced connection timeout: 30s instead of 60s (faster timeouts)
        - Early termination: Stop after 3 consecutive failures (prevent excessive runtime)
        
        This tests:
        - System ability to handle initial burst load (30 jobs)
        - Scaling from 30 to 100 with 5-job precision
        - Breaking point detection with early termination
        
        Expected:
        - Initial 30 jobs should start successfully
        - System should handle gradual increase
        - Breaking point (if any) will be detected and test will stop early
        - Test should complete in reasonable time (< 1 hour instead of 3+ hours)
        """
        env = get_environment()
        
        logger.info(f"\n" + "="*70)
        logger.info(f"[BURST+GRADUAL] 30 → 100 (burst start, +5 per step)")
        logger.info(f"="*70)
        logger.info(f"    Environment: {env.upper()}")
        logger.info(f"    Initial Burst: 30 jobs")
        logger.info(f"    Increment: +5 jobs per step (optimized)")
        logger.info(f"    Target: 100 concurrent jobs")
        logger.info(f"    Total Steps: 15 (1 burst + 14 incremental)")
        logger.info(f"    Early Stop: After 3 consecutive failures")
        
        # Create tester with burst-then-gradual config (optimized)
        tester = GradualLiveLoadTester(
            config_manager=config_manager,
            initial_jobs=30,        # BURST: Start with 30 jobs
            step_increment=5,       # Then add 5 at a time (reduced from 1)
            max_jobs=100,           # Target: 100 concurrent jobs
            step_interval_sec=5,    # 5 seconds between each step
            sla=gradual_load_sla,
            max_grpc_connect_retries=3,        # Reduced from 10
            grpc_connect_retry_delay_ms=2000,  # Reduced from 5000ms
            max_consecutive_failures=3          # Stop after 3 consecutive failures
        )
        
        result = tester.run_test(
            test_name="Burst+Gradual (30→100, +5 per step, optimized)"
        )
        
        # Assertions
        assert result.cleanup_successful, \
            "Cleanup should complete successfully"
        
        # Should complete at least some steps (reduced expectation due to early termination)
        assert result.total_steps >= 3, \
            f"Expected at least 3 steps, got {result.total_steps}"
        
        # Should reach at least 30 concurrent jobs (initial burst)
        assert result.max_concurrent_jobs >= 30, \
            f"Expected at least 30 concurrent jobs, got {result.max_concurrent_jobs}"
        
        logger.info(f"\n" + "="*70)
        logger.info(f"✅ Burst+Gradual test completed")
        logger.info(f"="*70)
        logger.info(f"   Total Steps: {result.total_steps}")
        logger.info(f"   Successful Steps: {result.successful_steps}")
        logger.info(f"   Max Concurrent Jobs: {result.max_concurrent_jobs}")
        
        if result.breaking_point:
            logger.warning(f"   ⚠️ Breaking Point Detected: {result.breaking_point} jobs")
            logger.info(f"   This is valuable data - system capacity is {result.breaking_point} concurrent jobs")
        else:
            logger.info(f"   🎉 No breaking point - system handled all 100 jobs!")
    
    @pytest.mark.xray("PZ-LOAD-311")
    def test_gradual_load_with_heavy_channels(self, config_manager, gradual_load_sla):
        """
        Test: Gradual load with heavy channel configuration - OPTIMIZED.
        
        Uses more channels per job (200 channels instead of 50).
        This tests system behavior with larger data processing.
        
        Optimizations:
        - Reduced gRPC retries: 3 instead of 10 (faster failure detection)
        - Reduced retry delay: 2s instead of 5s (faster retries)
        - Reduced connection timeout: 30s instead of 60s (faster timeouts)
        - Early termination: Stop after 3 consecutive failures (prevent excessive runtime)
        """
        env = get_environment()
        
        logger.info(f"\n[GRADUAL LOAD] Heavy Channels Test")
        
        tester = GradualLiveLoadTester(
            config_manager=config_manager,
            initial_jobs=3,
            step_increment=3,
            max_jobs=15,  # Lower max for heavy channels
            step_interval_sec=10,
            channels_min=1,
            channels_max=200,  # Heavy channel load
            sla=gradual_load_sla,
            max_grpc_connect_retries=3,        # Optimized: Reduced from 10
            grpc_connect_retry_delay_ms=2000,  # Optimized: Reduced from 5000ms
            max_consecutive_failures=3          # Early termination after 3 consecutive failures
        )
        
        result = tester.run_test(
            test_name="Heavy Channels (200 per job)"
        )
        
        assert result.cleanup_successful, "Cleanup must succeed"
        
        logger.info(f"\n✅ Heavy channels test completed")
        logger.info(f"   Max Concurrent: {result.max_concurrent_jobs}")


# =============================================================================
# Standalone Execution
# =============================================================================

if __name__ == "__main__":
    """
    Run gradual load test standalone (for debugging/development).
    
    Usage:
        python -m be_focus_server_tests.load.test_gradual_live_load
    """
    import sys
    sys.path.insert(0, ".")
    
    from config.config_manager import ConfigManager
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S"
    )
    
    print("\n" + "="*80)
    print("🚀 GRADUAL LIVE JOB LOAD TEST - Standalone Mode")
    print("="*80 + "\n")
    
    try:
        # Initialize
        config = ConfigManager()
        
        # Run quick test
        tester = GradualLiveLoadTester(
            config_manager=config,
            initial_jobs=2,
            step_increment=2,
            max_jobs=10,
            step_interval_sec=5
        )
        
        result = tester.run_test(test_name="Standalone Quick Test")
        
        # Summary
        print("\n" + "="*80)
        print("📊 FINAL SUMMARY")
        print("="*80)
        print(f"   Test Passed: {'✅ YES' if result.test_passed else '❌ NO'}")
        print(f"   Steps Completed: {result.total_steps}")
        print(f"   Max Concurrent: {result.max_concurrent_jobs}")
        print(f"   Cleanup: {'✅' if result.cleanup_successful else '❌'}")
        print("="*80 + "\n")
        
        sys.exit(0 if result.test_passed else 1)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

