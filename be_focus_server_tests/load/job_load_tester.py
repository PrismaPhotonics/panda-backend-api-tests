"""
Job Load Tester - Base Class for Live and Historic Load Testing
================================================================

This module provides:
- BaseJobLoadTester: Common functionality for all job types
- LiveJobLoadTester: Live streaming job testing
- HistoricJobLoadTester: Historic playback job testing

Both Live and Historic share the same flow:
1. POST /configure → Create job
2. Wait for gRPC ready (with retries!)
3. Connect to gRPC stream
4. Receive frames
5. Disconnect and cleanup

The difference is in the payload:
- Live: start_time=None, end_time=None
- Historic: start_time and end_time from available recordings

Author: QA Automation Architect
Date: 2025-11-30
"""

import logging
import time
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
from statistics import mean

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Data Classes
# =============================================================================

class JobType(Enum):
    """Type of job being tested."""
    LIVE = "live"
    HISTORIC = "historic"


class JobPhase(Enum):
    """Phases of job lifecycle."""
    CONFIGURE = "configure"
    WAIT_FOR_READY = "wait_for_ready"
    GRPC_CONNECT = "grpc_connect"
    STREAM_DATA = "stream_data"
    DISCONNECT = "disconnect"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class PhaseMetrics:
    """Metrics for a single phase."""
    phase: JobPhase
    duration_ms: float
    success: bool
    retries: int = 0
    error: Optional[str] = None


@dataclass
class JobResult:
    """Complete result of a single job execution."""
    job_type: JobType
    job_id: Optional[str]
    success: bool
    total_duration_ms: float
    phases: List[PhaseMetrics]
    frames_received: int = 0
    stream_url: Optional[str] = None
    stream_port: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    # Historic-specific
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    
    @property
    def configure_time_ms(self) -> float:
        for p in self.phases:
            if p.phase == JobPhase.CONFIGURE:
                return p.duration_ms
        return 0.0
    
    @property
    def grpc_connect_time_ms(self) -> float:
        total = 0.0
        for p in self.phases:
            if p.phase in (JobPhase.WAIT_FOR_READY, JobPhase.GRPC_CONNECT):
                total += p.duration_ms
        return total
    
    @property
    def total_retries(self) -> int:
        return sum(p.retries for p in self.phases)


@dataclass
class LoadTestResult:
    """Complete result of a load test."""
    test_name: str
    job_type: JobType
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    
    # Job counts
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    
    # Timing metrics (ms)
    avg_total_time_ms: float
    min_total_time_ms: float
    max_total_time_ms: float
    p50_total_time_ms: float
    p95_total_time_ms: float
    p99_total_time_ms: float
    
    # Phase metrics
    avg_configure_time_ms: float
    avg_grpc_connect_time_ms: float
    
    # gRPC metrics
    avg_frames_received: float
    total_frames_received: int
    
    # Retry metrics
    total_retries: int
    jobs_with_retries: int
    avg_retries_per_job: float
    
    # Error analysis
    error_rate: float
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    
    # All results
    all_job_results: List[JobResult] = field(default_factory=list)
    
    def to_log_message(self) -> str:
        """Generate detailed log message."""
        job_type_emoji = "🔴" if self.job_type == JobType.LIVE else "📼"
        
        lines = [
            "",
            "=" * 80,
            f"{job_type_emoji} {self.job_type.value.upper()} JOB LOAD TEST - RESULTS",
            "=" * 80,
            "",
            f"📊 Test Summary:",
            f"   • Test Name: {self.test_name}",
            f"   • Job Type: {self.job_type.value}",
            f"   • Duration: {self.duration_seconds:.2f}s",
            f"   • Total Jobs: {self.total_jobs}",
            f"   • Successful: {self.successful_jobs} ({100 * self.successful_jobs / max(self.total_jobs, 1):.1f}%)",
            f"   • Failed: {self.failed_jobs} ({self.error_rate:.1f}%)",
            "",
            f"⏱️  Timing Metrics:",
            f"   • Average: {self.avg_total_time_ms:.0f}ms",
            f"   • Min: {self.min_total_time_ms:.0f}ms",
            f"   • Max: {self.max_total_time_ms:.0f}ms",
            f"   • P50: {self.p50_total_time_ms:.0f}ms",
            f"   • P95: {self.p95_total_time_ms:.0f}ms",
            f"   • P99: {self.p99_total_time_ms:.0f}ms",
            "",
            f"📡 Phase Breakdown:",
            f"   • Avg Configure: {self.avg_configure_time_ms:.0f}ms",
            f"   • Avg gRPC Connect: {self.avg_grpc_connect_time_ms:.0f}ms",
            "",
            f"📦 Streaming:",
            f"   • Total Frames: {self.total_frames_received}",
            f"   • Avg per Job: {self.avg_frames_received:.1f}",
            "",
            f"🔄 Retries:",
            f"   • Total: {self.total_retries}",
            f"   • Jobs with Retries: {self.jobs_with_retries}",
            f"   • Avg per Job: {self.avg_retries_per_job:.2f}",
            "",
        ]
        
        if self.errors_by_type:
            lines.append(f"❌ Errors:")
            for error_type, count in self.errors_by_type.items():
                lines.append(f"   • {error_type}: {count}")
            lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)


# =============================================================================
# Base Job Load Tester
# =============================================================================

class BaseJobLoadTester(ABC):
    """
    Base class for job load testing.
    
    Provides common functionality for both Live and Historic jobs.
    Subclasses implement job-specific payload creation.
    """
    
    def __init__(
        self,
        focus_server_api,
        grpc_client_factory: Callable,
        # Retry configuration
        max_grpc_connect_retries: int = 5,
        grpc_connect_retry_delay_ms: int = 2000,
        # Timeouts
        configure_timeout_seconds: float = 30.0,
        grpc_connect_timeout_seconds: float = 60.0,
        stream_timeout_seconds: float = 30.0,
        # Stream configuration
        frames_to_receive: int = 5,
    ):
        """
        Initialize base job load tester.
        
        Args:
            focus_server_api: FocusServerAPI instance
            grpc_client_factory: Factory to create GrpcStreamClient
            max_grpc_connect_retries: Max retries for gRPC connection
            grpc_connect_retry_delay_ms: Delay between retries
            configure_timeout_seconds: Timeout for configure
            grpc_connect_timeout_seconds: Timeout for gRPC connect
            stream_timeout_seconds: Timeout for streaming
            frames_to_receive: Frames to receive per job
        """
        self.focus_server_api = focus_server_api
        self.grpc_client_factory = grpc_client_factory
        
        self.max_grpc_connect_retries = max_grpc_connect_retries
        self.grpc_connect_retry_delay_ms = grpc_connect_retry_delay_ms
        
        self.configure_timeout = configure_timeout_seconds
        self.grpc_connect_timeout = grpc_connect_timeout_seconds
        self.stream_timeout = stream_timeout_seconds
        
        self.frames_to_receive = frames_to_receive
        
        self._lock = threading.Lock()
    
    @property
    @abstractmethod
    def job_type(self) -> JobType:
        """Return the type of job this tester handles."""
        pass
    
    @abstractmethod
    def _create_config_payload(self) -> Dict[str, Any]:
        """
        Create the configuration payload for POST /configure.
        
        Subclasses implement this to provide Live or Historic specific payload.
        
        Returns:
            Dictionary to pass to ConfigureRequest
        """
        pass
    
    def _execute_single_job(self) -> JobResult:
        """Execute a single job from start to finish."""
        start_time = time.time()
        phases: List[PhaseMetrics] = []
        job_id = None
        stream_url = None
        stream_port = None
        frames_received = 0
        grpc_client = None
        config_start_time = None
        config_end_time = None
        
        try:
            # PHASE 1: Configure
            phase_start = time.time()
            try:
                from src.models.focus_server_models import ConfigureRequest
                
                payload = self._create_config_payload()
                config_request = ConfigureRequest(**payload)
                
                # Store time range for Historic jobs
                config_start_time = payload.get("start_time")
                config_end_time = payload.get("end_time")
                
                response = self.focus_server_api.configure_streaming_job(config_request)
                
                job_id = response.job_id
                stream_url = response.stream_url
                stream_port = int(response.stream_port)
                
                phases.append(PhaseMetrics(
                    phase=JobPhase.CONFIGURE,
                    duration_ms=(time.time() - phase_start) * 1000,
                    success=True
                ))
                
                logger.debug(f"[{self.job_type.value}] Job {job_id} configured")
                
            except Exception as e:
                phases.append(PhaseMetrics(
                    phase=JobPhase.CONFIGURE,
                    duration_ms=(time.time() - phase_start) * 1000,
                    success=False,
                    error=str(e)
                ))
                raise RuntimeError(f"Configure failed: {e}")
            
            # PHASE 2: gRPC Connect with Retries
            phase_start = time.time()
            connect_retries = 0
            connected = False
            last_error = None
            
            grpc_client = self.grpc_client_factory(
                connection_timeout=int(self.grpc_connect_timeout)
            )
            
            for attempt in range(self.max_grpc_connect_retries):
                try:
                    grpc_client.connect(stream_url=stream_url, stream_port=stream_port)
                    connected = True
                    break
                except Exception as e:
                    last_error = str(e)
                    connect_retries = attempt + 1
                    if attempt < self.max_grpc_connect_retries - 1:
                        time.sleep(self.grpc_connect_retry_delay_ms / 1000)
            
            phases.append(PhaseMetrics(
                phase=JobPhase.GRPC_CONNECT,
                duration_ms=(time.time() - phase_start) * 1000,
                success=connected,
                retries=connect_retries,
                error=None if connected else last_error
            ))
            
            if not connected:
                raise RuntimeError(f"gRPC connect failed after {connect_retries} retries")
            
            # PHASE 3: Stream Data
            phase_start = time.time()
            try:
                for frame in grpc_client.stream_data(
                    stream_id=0,
                    max_frames=self.frames_to_receive,
                    timeout=self.stream_timeout
                ):
                    frames_received += 1
                
                phases.append(PhaseMetrics(
                    phase=JobPhase.STREAM_DATA,
                    duration_ms=(time.time() - phase_start) * 1000,
                    success=True
                ))
                
            except Exception as e:
                phases.append(PhaseMetrics(
                    phase=JobPhase.STREAM_DATA,
                    duration_ms=(time.time() - phase_start) * 1000,
                    success=frames_received > 0,
                    error=str(e)
                ))
                if frames_received == 0:
                    raise RuntimeError(f"Stream failed: {e}")
            
            # PHASE 4: Disconnect
            phase_start = time.time()
            try:
                if grpc_client:
                    grpc_client.disconnect()
                phases.append(PhaseMetrics(
                    phase=JobPhase.DISCONNECT,
                    duration_ms=(time.time() - phase_start) * 1000,
                    success=True
                ))
            except Exception as e:
                phases.append(PhaseMetrics(
                    phase=JobPhase.DISCONNECT,
                    duration_ms=(time.time() - phase_start) * 1000,
                    success=False,
                    error=str(e)
                ))
            
            return JobResult(
                job_type=self.job_type,
                job_id=job_id,
                success=True,
                total_duration_ms=(time.time() - start_time) * 1000,
                phases=phases,
                frames_received=frames_received,
                stream_url=stream_url,
                stream_port=stream_port,
                start_time=config_start_time,
                end_time=config_end_time
            )
            
        except Exception as e:
            if grpc_client:
                try:
                    grpc_client.disconnect()
                except Exception:
                    pass
            
            return JobResult(
                job_type=self.job_type,
                job_id=job_id,
                success=False,
                total_duration_ms=(time.time() - start_time) * 1000,
                phases=phases,
                frames_received=frames_received,
                stream_url=stream_url,
                stream_port=stream_port,
                error=str(e),
                start_time=config_start_time,
                end_time=config_end_time
            )
    
    def run_load_test(
        self,
        num_jobs: int = 10,
        concurrent_jobs: int = 3,
        test_name: Optional[str] = None
    ) -> LoadTestResult:
        """
        Run load test with multiple jobs.
        
        Args:
            num_jobs: Total jobs to execute
            concurrent_jobs: Concurrent job count
            test_name: Test name (auto-generated if None)
            
        Returns:
            LoadTestResult with all metrics
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        if test_name is None:
            test_name = f"{self.job_type.value.title()} Job Load Test"
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"🚀 {self.job_type.value.upper()} JOB LOAD TEST - Starting...")
        logger.info("=" * 80)
        logger.info(f"   Type: {self.job_type.value}")
        logger.info(f"   Total Jobs: {num_jobs}")
        logger.info(f"   Concurrent: {concurrent_jobs}")
        logger.info(f"   Frames per Job: {self.frames_to_receive}")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        start_timestamp = time.time()
        
        all_results: List[JobResult] = []
        
        with ThreadPoolExecutor(max_workers=concurrent_jobs) as executor:
            futures = [
                executor.submit(self._execute_single_job)
                for _ in range(num_jobs)
            ]
            
            completed = 0
            for future in as_completed(futures, timeout=300):
                try:
                    result = future.result(timeout=120)
                    all_results.append(result)
                    completed += 1
                    
                    status = "✅" if result.success else "❌"
                    logger.info(
                        f"{status} [{self.job_type.value}] Job {completed}/{num_jobs}: "
                        f"{result.job_id} ({result.total_duration_ms:.0f}ms)"
                    )
                except Exception as e:
                    completed += 1
                    logger.warning(f"❌ Job {completed}/{num_jobs} failed: {e}")
                    all_results.append(JobResult(
                        job_type=self.job_type,
                        job_id=None,
                        success=False,
                        total_duration_ms=0,
                        phases=[],
                        error=str(e)
                    ))
        
        end_time = datetime.now()
        duration_seconds = time.time() - start_timestamp
        
        return self._calculate_results(
            test_name, start_time, end_time, duration_seconds, all_results
        )
    
    def _calculate_results(
        self,
        test_name: str,
        start_time: datetime,
        end_time: datetime,
        duration_seconds: float,
        all_results: List[JobResult]
    ) -> LoadTestResult:
        """Calculate aggregate metrics."""
        successful = [r for r in all_results if r.success]
        failed = [r for r in all_results if not r.success]
        
        total_times = [r.total_duration_ms for r in successful] if successful else [0]
        configure_times = [r.configure_time_ms for r in successful] if successful else [0]
        grpc_times = [r.grpc_connect_time_ms for r in successful] if successful else [0]
        
        sorted_times = sorted(total_times)
        
        def percentile(data: List[float], p: float) -> float:
            if not data:
                return 0.0
            idx = int(len(data) * p / 100)
            return data[min(idx, len(data) - 1)]
        
        total_frames = sum(r.frames_received for r in all_results)
        avg_frames = mean([r.frames_received for r in successful]) if successful else 0
        
        total_retries = sum(r.total_retries for r in all_results)
        jobs_with_retries = sum(1 for r in all_results if r.total_retries > 0)
        avg_retries = mean([r.total_retries for r in all_results]) if all_results else 0
        
        errors_by_type: Dict[str, int] = {}
        for r in failed:
            if r.error:
                error_type = r.error.split(":")[0][:30]
                errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
        
        result = LoadTestResult(
            test_name=test_name,
            job_type=self.job_type,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            total_jobs=len(all_results),
            successful_jobs=len(successful),
            failed_jobs=len(failed),
            avg_total_time_ms=mean(total_times) if total_times else 0,
            min_total_time_ms=min(total_times) if total_times else 0,
            max_total_time_ms=max(total_times) if total_times else 0,
            p50_total_time_ms=percentile(sorted_times, 50),
            p95_total_time_ms=percentile(sorted_times, 95),
            p99_total_time_ms=percentile(sorted_times, 99),
            avg_configure_time_ms=mean(configure_times) if configure_times else 0,
            avg_grpc_connect_time_ms=mean(grpc_times) if grpc_times else 0,
            avg_frames_received=avg_frames,
            total_frames_received=total_frames,
            total_retries=total_retries,
            jobs_with_retries=jobs_with_retries,
            avg_retries_per_job=avg_retries,
            error_rate=len(failed) / len(all_results) * 100 if all_results else 0,
            errors_by_type=errors_by_type,
            all_job_results=all_results
        )
        
        logger.info(result.to_log_message())
        return result


# =============================================================================
# Live Job Load Tester
# =============================================================================

class LiveJobLoadTester(BaseJobLoadTester):
    """
    Load tester for Live streaming jobs.
    
    Live jobs stream real-time data from the fiber.
    - start_time = None
    - end_time = None
    """
    
    def __init__(
        self,
        focus_server_api,
        grpc_client_factory: Callable,
        # Job configuration
        channels_min: int = 1,
        channels_max: int = 50,
        frequency_min: int = 0,
        frequency_max: int = 500,
        nfft: int = 1024,
        display_height: int = 600,
        view_type: int = 0,  # MULTICHANNEL
        **kwargs
    ):
        """
        Initialize Live Job Load Tester.
        
        Args:
            channels_min: Min channel
            channels_max: Max channel
            frequency_min: Min frequency Hz
            frequency_max: Max frequency Hz
            nfft: NFFT selection
            display_height: Display height
            view_type: View type (0=Multi, 1=Single, 2=Waterfall)
            **kwargs: Base class arguments
        """
        super().__init__(focus_server_api, grpc_client_factory, **kwargs)
        
        self.channels_min = channels_min
        self.channels_max = channels_max
        self.frequency_min = frequency_min
        self.frequency_max = frequency_max
        self.nfft = nfft
        self.display_height = display_height
        self.view_type = view_type
    
    @property
    def job_type(self) -> JobType:
        return JobType.LIVE
    
    def _create_config_payload(self) -> Dict[str, Any]:
        """Create Live job payload (no start_time/end_time)."""
        return {
            "displayTimeAxisDuration": 10,
            "nfftSelection": self.nfft,
            "displayInfo": {"height": self.display_height},
            "channels": {"min": self.channels_min, "max": self.channels_max},
            "frequencyRange": {"min": self.frequency_min, "max": self.frequency_max},
            "start_time": None,  # LIVE - no start time
            "end_time": None,    # LIVE - no end time
            "view_type": str(self.view_type)
        }


# =============================================================================
# Historic Job Load Tester
# =============================================================================

class HistoricJobLoadTester(BaseJobLoadTester):
    """
    Load tester for Historic playback jobs.
    
    Historic jobs replay recorded data from storage.
    - start_time = epoch timestamp
    - end_time = epoch timestamp
    
    Uses MongoDB base_paths collection directly to find recordings for load testing.
    """
    
    def __init__(
        self,
        focus_server_api,
        grpc_client_factory: Callable,
        config_manager=None,
        # Job configuration
        channels_min: int = 1,
        channels_max: int = 50,
        frequency_min: int = 0,
        frequency_max: int = 500,
        nfft: int = 1024,
        display_height: int = 600,
        view_type: int = 0,
        # Historic-specific
        recording_duration_seconds: int = 10,
        # MongoDB query parameters
        min_duration_seconds: float = 5.0,
        max_duration_seconds: float = 10.0,
        weeks_back: int = 2,
        max_recordings_to_load: int = 100,
        **kwargs
    ):
        """
        Initialize Historic Job Load Tester.
        
        Args:
            config_manager: ConfigManager instance (required for MongoDB access)
            recording_duration_seconds: Duration of recording to request
            min_duration_seconds: Minimum recording duration to search for
            max_duration_seconds: Maximum recording duration to search for
            weeks_back: Number of weeks back to search in MongoDB
            max_recordings_to_load: Maximum recordings to load from MongoDB
            **kwargs: Base class and common arguments
        """
        super().__init__(focus_server_api, grpc_client_factory, **kwargs)
        
        self.config_manager = config_manager
        self.channels_min = channels_min
        self.channels_max = channels_max
        self.frequency_min = frequency_min
        self.frequency_max = frequency_max
        self.nfft = nfft
        self.display_height = display_height
        self.view_type = view_type
        self.recording_duration_seconds = recording_duration_seconds
        
        # MongoDB query parameters
        self.min_duration_seconds = min_duration_seconds
        self.max_duration_seconds = max_duration_seconds
        self.weeks_back = weeks_back
        self.max_recordings_to_load = max_recordings_to_load
        
        # Cache available recordings from MongoDB
        self._available_recordings: Optional[List[tuple]] = None
        self._recording_index = 0  # For round-robin selection
    
    @property
    def job_type(self) -> JobType:
        return JobType.HISTORIC
    
    def _get_available_recordings_from_mongodb(self) -> List[tuple]:
        """
        Get available recordings DIRECTLY from MongoDB using base_paths collection.
        
        Query flow:
        1. Connect to MongoDB
        2. Query base_paths collection for base_path="/prisma/root/recordings", is_archive=False
        3. Get guid from the document
        4. Query collection named {guid} for recordings
        5. Filter by deleted=False, duration, and time range
        
        Returns:
            List of (start_time_ms, end_time_ms) tuples
        """
        if self._available_recordings is not None:
            return self._available_recordings
        
        if not self.config_manager:
            logger.warning("No config_manager provided, cannot query MongoDB")
            return []
        
        try:
            from be_focus_server_tests.fixtures.recording_fixtures import fetch_recordings_from_mongodb
            
            logger.info(f"Querying MongoDB for historic recordings...")
            logger.info(f"  - Duration: {self.min_duration_seconds}-{self.max_duration_seconds}s")
            logger.info(f"  - Time range: last {self.weeks_back} weeks")
            logger.info(f"  - Max recordings: {self.max_recordings_to_load}")
            
            # Query MongoDB directly using base_paths collection
            recordings_info = fetch_recordings_from_mongodb(
                config_manager=self.config_manager,
                max_recordings=self.max_recordings_to_load,
                min_duration_seconds=self.min_duration_seconds,
                max_duration_seconds=self.max_duration_seconds,
                weeks_back=self.weeks_back
            )
            
            if not recordings_info.has_recordings:
                logger.warning("No recordings found in MongoDB")
                self._available_recordings = []
                return []
            
            # Convert Recording objects to (start_ms, end_ms) tuples
            recordings_list = []
            for rec in recordings_info.recordings:
                # Use start_time_ms and end_time_ms (in milliseconds) for API calls
                recordings_list.append((rec.start_time_ms, rec.end_time_ms))
            
            self._available_recordings = recordings_list
            logger.info(f"✅ Loaded {len(self._available_recordings)} recordings from MongoDB base_paths collection")
            
            # Log first few recordings for debugging
            for i, (start_ms, end_ms) in enumerate(recordings_list[:3]):
                duration_sec = (end_ms - start_ms) / 1000
                logger.debug(f"  Recording {i+1}: {duration_sec:.1f}s duration")
            
            return self._available_recordings
            
        except Exception as e:
            logger.error(f"Failed to get recordings from MongoDB: {e}", exc_info=True)
            self._available_recordings = []
            return []
    
    def _get_available_recordings(self) -> List[tuple]:
        """
        Get available recordings - tries MongoDB first, falls back to API.
        
        For load testing, we prefer MongoDB direct access via base_paths collection.
        """
        # Try MongoDB first (preferred method)
        recordings = self._get_available_recordings_from_mongodb()
        
        if recordings:
            return recordings
        
        # Fallback to API (may not work, but try anyway)
        logger.warning("MongoDB query failed, falling back to Focus Server API")
        try:
            from src.models.focus_server_models import RecordingsInTimeRangeRequest
            
            # Query last 24 hours
            now = int(time.time() * 1000)  # epoch ms
            day_ago = now - (24 * 60 * 60 * 1000)
            
            request = RecordingsInTimeRangeRequest(
                start_time=day_ago,
                end_time=now
            )
            
            response = self.focus_server_api.get_recordings_in_time_range(request)
            api_recordings = response.root if response.root else []
            
            if api_recordings:
                logger.info(f"Found {len(api_recordings)} recordings via API")
                return api_recordings
            
        except Exception as e:
            logger.warning(f"API fallback also failed: {e}")
        
        return []
    
    def _create_config_payload(self) -> Dict[str, Any]:
        """
        Create Historic job payload with time range from MongoDB base_paths collection.
        
        Uses round-robin selection to distribute load across different recordings.
        """
        recordings = self._get_available_recordings()
        
        if recordings:
            # Round-robin selection for load distribution
            with self._lock:
                recording_index = self._recording_index % len(recordings)
                self._recording_index += 1
            
            rec_start_ms, rec_end_ms = recordings[recording_index]
            
            # Calculate time range (use requested duration or available)
            # recordings are in milliseconds, but API expects seconds
            duration_ms = self.recording_duration_seconds * 1000
            actual_duration_ms = min(duration_ms, rec_end_ms - rec_start_ms)
            
            # Convert to seconds for API (epoch seconds)
            start_time = rec_start_ms // 1000
            end_time = (rec_start_ms + actual_duration_ms) // 1000
            
            duration_sec = actual_duration_ms / 1000
            logger.debug(f"Using recording {recording_index + 1}/{len(recordings)}: "
                        f"duration={duration_sec:.1f}s")
        else:
            # Fallback: use current time minus offset (may fail if no recording)
            logger.warning("No recordings found in MongoDB base_paths, using fallback time range")
            # API expects epoch seconds, not milliseconds
            now = int(time.time())
            start_time = now - 60  # 1 minute ago (in seconds)
            end_time = now - 50     # 50 seconds ago (in seconds)
        
        return {
            "displayTimeAxisDuration": 10,
            "nfftSelection": self.nfft,
            "displayInfo": {"height": self.display_height},
            "channels": {"min": self.channels_min, "max": self.channels_max},
            "frequencyRange": {"min": self.frequency_min, "max": self.frequency_max},
            "start_time": start_time,  # HISTORIC - has start time
            "end_time": end_time,       # HISTORIC - has end time
            "view_type": str(self.view_type)
        }


# =============================================================================
# Factory Functions
# =============================================================================

def create_live_job_tester(
    config_manager,
    channels_min: int = 1,
    channels_max: int = 50,
    frequency_min: int = 0,
    frequency_max: int = 500,
    nfft: int = 1024,
    **kwargs
) -> LiveJobLoadTester:
    """Factory to create LiveJobLoadTester."""
    from src.apis.focus_server_api import FocusServerAPI
    from src.apis.grpc_client import GrpcStreamClient
    
    api = FocusServerAPI(config_manager)
    
    def grpc_factory(connection_timeout: int = 30):
        return GrpcStreamClient(
            config_manager=config_manager,
            connection_timeout=connection_timeout
        )
    
    return LiveJobLoadTester(
        focus_server_api=api,
        grpc_client_factory=grpc_factory,
        channels_min=channels_min,
        channels_max=channels_max,
        frequency_min=frequency_min,
        frequency_max=frequency_max,
        nfft=nfft,
        **kwargs
    )


def create_historic_job_tester(
    config_manager,
    channels_min: int = 1,
    channels_max: int = 50,
    frequency_min: int = 0,
    frequency_max: int = 500,
    nfft: int = 1024,
    recording_duration_seconds: int = 10,
    # MongoDB query parameters
    min_duration_seconds: float = 5.0,
    max_duration_seconds: float = 10.0,
    weeks_back: int = 2,
    max_recordings_to_load: int = 100,
    **kwargs
) -> HistoricJobLoadTester:
    """
    Factory to create HistoricJobLoadTester.
    
    Uses MongoDB base_paths collection to find recordings for load testing.
    
    Args:
        config_manager: ConfigManager instance (required for MongoDB access)
        channels_min: Min channel
        channels_max: Max channel
        frequency_min: Min frequency Hz
        frequency_max: Max frequency Hz
        nfft: NFFT selection
        recording_duration_seconds: Duration of recording to request
        min_duration_seconds: Minimum recording duration to search for in MongoDB
        max_duration_seconds: Maximum recording duration to search for in MongoDB
        weeks_back: Number of weeks back to search in MongoDB
        max_recordings_to_load: Maximum recordings to load from MongoDB for load testing
        **kwargs: Other arguments passed to HistoricJobLoadTester
    """
    from src.apis.focus_server_api import FocusServerAPI
    from src.apis.grpc_client import GrpcStreamClient
    
    api = FocusServerAPI(config_manager)
    
    def grpc_factory(connection_timeout: int = 30):
        return GrpcStreamClient(
            config_manager=config_manager,
            connection_timeout=connection_timeout
        )
    
    return HistoricJobLoadTester(
        focus_server_api=api,
        grpc_client_factory=grpc_factory,
        config_manager=config_manager,  # Pass config_manager for MongoDB access
        channels_min=channels_min,
        channels_max=channels_max,
        frequency_min=frequency_min,
        frequency_max=frequency_max,
        nfft=nfft,
        recording_duration_seconds=recording_duration_seconds,
        min_duration_seconds=min_duration_seconds,
        max_duration_seconds=max_duration_seconds,
        weeks_back=weeks_back,
        max_recordings_to_load=max_recordings_to_load,
        **kwargs
    )

