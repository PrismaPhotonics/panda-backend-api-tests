"""
Live Job Load Tester - End-to-End Live Streaming Job Load Testing
=================================================================

This module provides comprehensive load testing for the complete Live Job flow:
1. POST /configure → Create job
2. Wait for job ready (with retries - as Yonatan noted!)
3. Connect to gRPC stream
4. Receive and validate frames
5. Cleanup and disconnect

Implements the FULL Live Job lifecycle for performance measurement.

Author: QA Automation Architect
Date: 2025-11-30
"""

import logging
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
from statistics import mean, median, stdev
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

class LiveJobPhase(Enum):
    """Phases of Live Job lifecycle."""
    CONFIGURE = "configure"
    WAIT_FOR_READY = "wait_for_ready"
    GRPC_CONNECT = "grpc_connect"
    STREAM_DATA = "stream_data"
    DISCONNECT = "disconnect"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class PhaseMetrics:
    """Metrics for a single phase of the job lifecycle."""
    phase: LiveJobPhase
    duration_ms: float
    success: bool
    retries: int = 0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase.value,
            "duration_ms": round(self.duration_ms, 2),
            "success": self.success,
            "retries": self.retries,
            "error": self.error
        }


@dataclass
class LiveJobResult:
    """Complete result of a single Live Job execution."""
    job_id: Optional[str]
    success: bool
    total_duration_ms: float
    phases: List[PhaseMetrics]
    frames_received: int = 0
    stream_url: Optional[str] = None
    stream_port: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def configure_time_ms(self) -> float:
        """Time spent in configure phase."""
        for p in self.phases:
            if p.phase == LiveJobPhase.CONFIGURE:
                return p.duration_ms
        return 0.0
    
    @property
    def grpc_connect_time_ms(self) -> float:
        """Time spent connecting to gRPC (includes retries)."""
        total = 0.0
        for p in self.phases:
            if p.phase in (LiveJobPhase.WAIT_FOR_READY, LiveJobPhase.GRPC_CONNECT):
                total += p.duration_ms
        return total
    
    @property
    def total_retries(self) -> int:
        """Total retries across all phases."""
        return sum(p.retries for p in self.phases)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "success": self.success,
            "total_duration_ms": round(self.total_duration_ms, 2),
            "configure_time_ms": round(self.configure_time_ms, 2),
            "grpc_connect_time_ms": round(self.grpc_connect_time_ms, 2),
            "frames_received": self.frames_received,
            "total_retries": self.total_retries,
            "stream_url": self.stream_url,
            "stream_port": self.stream_port,
            "error": self.error,
            "phases": [p.to_dict() for p in self.phases]
        }


@dataclass
class LiveJobLoadTestResult:
    """Complete result of a Live Job load test."""
    test_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    
    # Job counts
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    
    # Timing metrics (in ms)
    avg_total_time_ms: float
    min_total_time_ms: float
    max_total_time_ms: float
    p50_total_time_ms: float
    p95_total_time_ms: float
    p99_total_time_ms: float
    
    # Phase-specific metrics
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
    all_job_results: List[LiveJobResult] = field(default_factory=list)
    
    def to_log_message(self) -> str:
        """Generate detailed log message."""
        lines = [
            "",
            "=" * 80,
            "🚀 LIVE JOB LOAD TEST - RESULTS",
            "=" * 80,
            "",
            f"📊 Test Summary:",
            f"   • Test Name: {self.test_name}",
            f"   • Duration: {self.duration_seconds:.2f} seconds",
            f"   • Total Jobs: {self.total_jobs}",
            f"   • Successful: {self.successful_jobs} ({100 * self.successful_jobs / max(self.total_jobs, 1):.1f}%)",
            f"   • Failed: {self.failed_jobs} ({self.error_rate:.1f}%)",
            "",
            f"⏱️  Timing Metrics (Total Job Time):",
            f"   • Average: {self.avg_total_time_ms:.0f}ms",
            f"   • Min: {self.min_total_time_ms:.0f}ms",
            f"   • Max: {self.max_total_time_ms:.0f}ms",
            f"   • P50: {self.p50_total_time_ms:.0f}ms",
            f"   • P95: {self.p95_total_time_ms:.0f}ms",
            f"   • P99: {self.p99_total_time_ms:.0f}ms",
            "",
            f"📡 Phase Breakdown:",
            f"   • Avg Configure Time: {self.avg_configure_time_ms:.0f}ms",
            f"   • Avg gRPC Connect Time: {self.avg_grpc_connect_time_ms:.0f}ms (includes retries)",
            "",
            f"📦 gRPC Streaming:",
            f"   • Total Frames Received: {self.total_frames_received}",
            f"   • Avg Frames per Job: {self.avg_frames_received:.1f}",
            "",
            f"🔄 Retry Statistics:",
            f"   • Total Retries: {self.total_retries}",
            f"   • Jobs with Retries: {self.jobs_with_retries}",
            f"   • Avg Retries per Job: {self.avg_retries_per_job:.2f}",
            "",
        ]
        
        if self.errors_by_type:
            lines.extend([
                f"❌ Errors by Type:",
            ])
            for error_type, count in self.errors_by_type.items():
                lines.append(f"   • {error_type}: {count}")
            lines.append("")
        
        lines.extend([
            "=" * 80,
        ])
        
        return "\n".join(lines)


# =============================================================================
# Live Job Load Tester
# =============================================================================

class LiveJobLoadTester:
    """
    Live Job Load Tester - Tests complete Live Job lifecycle.
    
    Implements the FULL flow as described by Yonatan:
    1. POST /configure → Create job, get job_id, stream_url, stream_port
    2. Wait for job ready (with RETRIES - key insight from Yonatan!)
    3. Connect to gRPC stream
    4. Receive frames
    5. Disconnect and cleanup
    
    Usage:
        tester = LiveJobLoadTester(
            focus_server_api=api,
            grpc_client_factory=create_grpc_client,
            config_payload=payload
        )
        
        result = tester.run_load_test(
            num_jobs=10,
            concurrent_jobs=3
        )
        
        logger.info(result.to_log_message())
    """
    
    def __init__(
        self,
        focus_server_api,
        grpc_client_factory: Callable,
        config_payload: Dict[str, Any],
        # Retry configuration - KEY FEATURE as Yonatan mentioned!
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
        Initialize Live Job Load Tester.
        
        Args:
            focus_server_api: FocusServerAPI instance
            grpc_client_factory: Factory function to create GrpcStreamClient
            config_payload: ConfigureRequest payload (dict)
            max_grpc_connect_retries: Max retries for gRPC connection (Yonatan's insight!)
            grpc_connect_retry_delay_ms: Delay between retries
            configure_timeout_seconds: Timeout for POST /configure
            grpc_connect_timeout_seconds: Total timeout for gRPC connection
            stream_timeout_seconds: Timeout for streaming data
            frames_to_receive: Number of frames to receive before stopping
        """
        self.focus_server_api = focus_server_api
        self.grpc_client_factory = grpc_client_factory
        self.config_payload = config_payload
        
        # Retry config - critical for reliability
        self.max_grpc_connect_retries = max_grpc_connect_retries
        self.grpc_connect_retry_delay_ms = grpc_connect_retry_delay_ms
        
        # Timeouts
        self.configure_timeout = configure_timeout_seconds
        self.grpc_connect_timeout = grpc_connect_timeout_seconds
        self.stream_timeout = stream_timeout_seconds
        
        # Stream config
        self.frames_to_receive = frames_to_receive
        
        # Thread safety
        self._lock = threading.Lock()
        self._job_counter = 0
    
    def _execute_single_job(self) -> LiveJobResult:
        """
        Execute a single Live Job from start to finish.
        
        Flow:
        1. POST /configure
        2. Wait for ready (with retries!)
        3. Connect to gRPC
        4. Stream data
        5. Disconnect
        
        Returns:
            LiveJobResult with all metrics
        """
        start_time = time.time()
        phases: List[PhaseMetrics] = []
        job_id = None
        stream_url = None
        stream_port = None
        frames_received = 0
        grpc_client = None
        
        try:
            # ============================================================
            # PHASE 1: POST /configure
            # ============================================================
            phase_start = time.time()
            try:
                from src.models.focus_server_models import ConfigureRequest
                
                # Create request from payload
                config_request = ConfigureRequest(**self.config_payload)
                
                # Send configure request
                response = self.focus_server_api.configure_streaming_job(config_request)
                
                job_id = response.job_id
                stream_url = response.stream_url
                stream_port = int(response.stream_port)
                
                phases.append(PhaseMetrics(
                    phase=LiveJobPhase.CONFIGURE,
                    duration_ms=(time.time() - phase_start) * 1000,
                    success=True
                ))
                
                logger.debug(f"Job {job_id} configured: {stream_url}:{stream_port}")
                
            except Exception as e:
                phases.append(PhaseMetrics(
                    phase=LiveJobPhase.CONFIGURE,
                    duration_ms=(time.time() - phase_start) * 1000,
                    success=False,
                    error=str(e)
                ))
                raise RuntimeError(f"Configure failed: {e}")
            
            # ============================================================
            # PHASE 2: Wait for Ready + Connect to gRPC (WITH RETRIES!)
            # This is the KEY insight from Yonatan - need retries here!
            # ============================================================
            phase_start = time.time()
            connect_retries = 0
            connected = False
            last_error = None
            
            # Create gRPC client
            grpc_client = self.grpc_client_factory(
                connection_timeout=int(self.grpc_connect_timeout)
            )
            
            # Retry loop - critical for reliability!
            for attempt in range(self.max_grpc_connect_retries):
                try:
                    logger.debug(
                        f"Job {job_id}: gRPC connect attempt {attempt + 1}/{self.max_grpc_connect_retries}"
                    )
                    
                    # Try to connect
                    grpc_client.connect(stream_url=stream_url, stream_port=stream_port)
                    connected = True
                    break
                    
                except Exception as e:
                    last_error = str(e)
                    connect_retries = attempt + 1
                    
                    logger.debug(
                        f"Job {job_id}: gRPC connect attempt {attempt + 1} failed: {e}"
                    )
                    
                    # Wait before retry (except on last attempt)
                    if attempt < self.max_grpc_connect_retries - 1:
                        time.sleep(self.grpc_connect_retry_delay_ms / 1000)
            
            phases.append(PhaseMetrics(
                phase=LiveJobPhase.GRPC_CONNECT,
                duration_ms=(time.time() - phase_start) * 1000,
                success=connected,
                retries=connect_retries,
                error=None if connected else last_error
            ))
            
            if not connected:
                raise RuntimeError(
                    f"gRPC connect failed after {connect_retries} retries: {last_error}"
                )
            
            logger.debug(f"Job {job_id}: Connected to gRPC after {connect_retries} retries")
            
            # ============================================================
            # PHASE 3: Stream Data
            # ============================================================
            phase_start = time.time()
            try:
                # Stream frames
                for frame in grpc_client.stream_data(
                    stream_id=0, 
                    max_frames=self.frames_to_receive,
                    timeout=self.stream_timeout
                ):
                    frames_received += 1
                    logger.debug(
                        f"Job {job_id}: Received frame {frames_received}/{self.frames_to_receive}"
                    )
                
                phases.append(PhaseMetrics(
                    phase=LiveJobPhase.STREAM_DATA,
                    duration_ms=(time.time() - phase_start) * 1000,
                    success=True
                ))
                
            except Exception as e:
                phases.append(PhaseMetrics(
                    phase=LiveJobPhase.STREAM_DATA,
                    duration_ms=(time.time() - phase_start) * 1000,
                    success=frames_received > 0,  # Partial success if got some frames
                    error=str(e)
                ))
                
                if frames_received == 0:
                    raise RuntimeError(f"Stream failed: {e}")
            
            # ============================================================
            # PHASE 4: Disconnect
            # ============================================================
            phase_start = time.time()
            try:
                if grpc_client:
                    grpc_client.disconnect()
                
                phases.append(PhaseMetrics(
                    phase=LiveJobPhase.DISCONNECT,
                    duration_ms=(time.time() - phase_start) * 1000,
                    success=True
                ))
            except Exception as e:
                phases.append(PhaseMetrics(
                    phase=LiveJobPhase.DISCONNECT,
                    duration_ms=(time.time() - phase_start) * 1000,
                    success=False,
                    error=str(e)
                ))
            
            # Success!
            return LiveJobResult(
                job_id=job_id,
                success=True,
                total_duration_ms=(time.time() - start_time) * 1000,
                phases=phases,
                frames_received=frames_received,
                stream_url=stream_url,
                stream_port=stream_port
            )
            
        except Exception as e:
            # Cleanup on error
            if grpc_client:
                try:
                    grpc_client.disconnect()
                except Exception:
                    pass
            
            return LiveJobResult(
                job_id=job_id,
                success=False,
                total_duration_ms=(time.time() - start_time) * 1000,
                phases=phases,
                frames_received=frames_received,
                stream_url=stream_url,
                stream_port=stream_port,
                error=str(e)
            )
    
    def run_load_test(
        self,
        num_jobs: int = 10,
        concurrent_jobs: int = 3,
        test_name: str = "Live Job Load Test"
    ) -> LiveJobLoadTestResult:
        """
        Run a complete load test with multiple Live Jobs.
        
        Args:
            num_jobs: Total number of jobs to execute
            concurrent_jobs: Number of concurrent jobs
            test_name: Name for the test
            
        Returns:
            LiveJobLoadTestResult with all metrics
        """
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"🚀 LIVE JOB LOAD TEST - Starting...")
        logger.info("=" * 80)
        logger.info(f"   Total Jobs: {num_jobs}")
        logger.info(f"   Concurrent: {concurrent_jobs}")
        logger.info(f"   Frames per Job: {self.frames_to_receive}")
        logger.info(f"   Max gRPC Retries: {self.max_grpc_connect_retries}")
        logger.info("=" * 80)
        logger.info("")
        
        start_time = datetime.now()
        start_timestamp = time.time()
        
        all_results: List[LiveJobResult] = []
        
        # Execute jobs with concurrency
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
                        f"{status} Job {completed}/{num_jobs}: {result.job_id} "
                        f"({result.total_duration_ms:.0f}ms, {result.frames_received} frames)"
                    )
                    
                except Exception as e:
                    completed += 1
                    logger.warning(f"❌ Job {completed}/{num_jobs} failed: {e}")
                    all_results.append(LiveJobResult(
                        job_id=None,
                        success=False,
                        total_duration_ms=0,
                        phases=[],
                        error=str(e)
                    ))
        
        end_time = datetime.now()
        duration_seconds = time.time() - start_timestamp
        
        # Calculate metrics
        return self._calculate_results(
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            all_results=all_results
        )
    
    def _calculate_results(
        self,
        test_name: str,
        start_time: datetime,
        end_time: datetime,
        duration_seconds: float,
        all_results: List[LiveJobResult]
    ) -> LiveJobLoadTestResult:
        """Calculate aggregate metrics from all job results."""
        
        successful = [r for r in all_results if r.success]
        failed = [r for r in all_results if not r.success]
        
        # Timing metrics from successful jobs
        total_times = [r.total_duration_ms for r in successful] if successful else [0]
        configure_times = [r.configure_time_ms for r in successful] if successful else [0]
        grpc_connect_times = [r.grpc_connect_time_ms for r in successful] if successful else [0]
        
        # Sort for percentiles
        sorted_times = sorted(total_times)
        
        def percentile(data: List[float], p: float) -> float:
            if not data:
                return 0.0
            index = int(len(data) * p / 100)
            return data[min(index, len(data) - 1)]
        
        # Frame metrics
        total_frames = sum(r.frames_received for r in all_results)
        avg_frames = mean([r.frames_received for r in successful]) if successful else 0
        
        # Retry metrics
        total_retries = sum(r.total_retries for r in all_results)
        jobs_with_retries = sum(1 for r in all_results if r.total_retries > 0)
        avg_retries = mean([r.total_retries for r in all_results]) if all_results else 0
        
        # Error analysis
        errors_by_type: Dict[str, int] = {}
        for r in failed:
            if r.error:
                error_type = r.error.split(":")[0][:30]
                errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
        
        result = LiveJobLoadTestResult(
            test_name=test_name,
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
            avg_grpc_connect_time_ms=mean(grpc_connect_times) if grpc_connect_times else 0,
            avg_frames_received=avg_frames,
            total_frames_received=total_frames,
            total_retries=total_retries,
            jobs_with_retries=jobs_with_retries,
            avg_retries_per_job=avg_retries,
            error_rate=len(failed) / len(all_results) * 100 if all_results else 0,
            errors_by_type=errors_by_type,
            all_job_results=all_results
        )
        
        # Log results
        logger.info(result.to_log_message())
        
        return result


# =============================================================================
# Factory Function
# =============================================================================

def create_live_job_load_tester(
    config_manager,
    channels_min: int = 1,
    channels_max: int = 50,
    frequency_min: int = 0,
    frequency_max: int = 500,
    nfft: int = 1024,
    display_height: int = 600,
    **kwargs
) -> LiveJobLoadTester:
    """
    Factory function to create LiveJobLoadTester with sensible defaults.
    
    Args:
        config_manager: Configuration manager instance
        channels_min: Min channel (default: 1)
        channels_max: Max channel (default: 50)
        frequency_min: Min frequency Hz (default: 0)
        frequency_max: Max frequency Hz (default: 500)
        nfft: NFFT selection (default: 1024)
        display_height: Display height (default: 600)
        **kwargs: Additional args for LiveJobLoadTester
        
    Returns:
        Configured LiveJobLoadTester instance
    """
    from src.apis.focus_server_api import FocusServerAPI
    from src.apis.grpc_client import GrpcStreamClient
    
    # Create API client
    api = FocusServerAPI(config_manager)
    
    # Create gRPC client factory
    def grpc_factory(connection_timeout: int = 30):
        return GrpcStreamClient(
            config_manager=config_manager,
            connection_timeout=connection_timeout
        )
    
    # Create config payload
    config_payload = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": nfft,
        "displayInfo": {"height": display_height},
        "channels": {"min": channels_min, "max": channels_max},
        "frequencyRange": {"min": frequency_min, "max": frequency_max},
        "view_type": 0  # MULTICHANNEL
    }
    
    return LiveJobLoadTester(
        focus_server_api=api,
        grpc_client_factory=grpc_factory,
        config_payload=config_payload,
        **kwargs
    )

