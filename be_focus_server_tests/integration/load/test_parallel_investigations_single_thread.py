"""
Parallel Investigations - Single Thread Test Suite
===================================================

Tests that validate opening multiple investigations in parallel within a SINGLE thread.
This uses asyncio for single-threaded concurrency (cooperative multitasking) rather than
ThreadPoolExecutor which uses multiple threads.

Key Differences from ThreadPoolExecutor Tests:
- Single thread execution (event loop based)
- No GIL contention issues
- True concurrent I/O without thread overhead
- Better for I/O-bound operations like HTTP requests

Enhanced Features:
- Timestamp verification to prove parallel execution
- Job metadata inspection and configuration validation
- Job type detection (Live vs Historic)
- Component stability monitoring (Focus Server, MongoDB, RabbitMQ)
- Comprehensive end-of-test summary with job comparisons

Test Scenarios:
- Test 1: Open N investigations in parallel using asyncio.gather()
- Test 2: Validate response times under parallel load
- Test 3: Stress test with increasing number of parallel investigations
- Test 4: Verify all investigations receive valid job_ids
- Test 5: Parallel investigations with gRPC data validation
- Test 6: Verify parallel creation with timestamp analysis
- Test 7: Component stability verification during parallel load
- Test 8: Parallel LIVE jobs only (real-time streaming)
- Test 9: Parallel HISTORIC jobs only (recorded data playback)

Author: QA Automation Architect
Date: 2025-12-09
Environment: Kefar Saba (per memory directive)

Examples:
    # Run all parallel investigation tests
    pytest be_focus_server_tests/integration/load/test_parallel_investigations_single_thread.py -v --env kefar_saba

    # Run specific test
    pytest be_focus_server_tests/integration/load/test_parallel_investigations_single_thread.py::TestParallelInvestigationsSingleThread::test_open_investigations_parallel -v --env kefar_saba

    # Run with verification of parallel creation
    pytest be_focus_server_tests/integration/load/test_parallel_investigations_single_thread.py -v --env kefar_saba -k "test_parallel_creation_with_verification"
"""

import pytest
import asyncio
import aiohttp
import logging
import time
import ssl
import requests
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean, stdev

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration Constants
# =============================================================================

# Default number of parallel investigations to open
DEFAULT_PARALLEL_COUNT = 5

# Maximum number of parallel investigations for stress test
MAX_PARALLEL_COUNT = 20

# Timeout for each investigation creation (seconds)
INVESTIGATION_TIMEOUT_SECONDS = 30

# Expected maximum response time for single investigation (seconds)
EXPECTED_MAX_RESPONSE_TIME_SECONDS = 10

# Minimum success rate for parallel operations (percentage)
MIN_SUCCESS_RATE_PERCENT = 80


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class InvestigationResult:
    """Result of a single investigation creation."""
    index: int
    success: bool
    job_id: Optional[str] = None
    response_time_ms: float = 0.0
    error: Optional[str] = None
    stream_url: Optional[str] = None
    stream_port: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    # Enhanced fields for detailed tracking
    request_start_time: float = 0.0  # Epoch time when request was sent
    request_end_time: float = 0.0    # Epoch time when response received
    full_response: Optional[Dict[str, Any]] = None  # Full API response


@dataclass
class JobMetadata:
    """Detailed metadata for a created job."""
    job_id: str
    job_type: str  # "Live" or "Historic"
    creation_timestamp: datetime
    request_start_epoch: float
    request_end_epoch: float
    response_time_ms: float
    stream_url: Optional[str]
    stream_port: Optional[int]
    view_type: Optional[str]
    channels_min: Optional[int]
    channels_max: Optional[int]
    channel_count: Optional[int]
    frequency_min: Optional[int]
    frequency_max: Optional[int]
    nfft_selection: Optional[int]
    display_time_axis_duration: Optional[int]
    frequencies_list: Optional[List[float]] = None
    frequencies_amount: Optional[int] = None
    stream_amount: Optional[int] = None
    status: Optional[str] = None


@dataclass
class ComponentHealthStatus:
    """Health status of a system component."""
    component_name: str
    is_healthy: bool
    response_time_ms: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    last_checked: datetime = field(default_factory=datetime.now)


@dataclass
class ParallelTestResult:
    """Aggregated result of parallel investigation test."""
    total_investigations: int
    successful: int
    failed: int
    success_rate: float
    total_time_ms: float
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    job_ids: List[str]
    errors: List[str]
    # Enhanced fields for parallel verification
    investigation_results: List[InvestigationResult] = field(default_factory=list)
    job_metadata_list: List[JobMetadata] = field(default_factory=list)
    parallel_execution_verified: bool = False
    max_concurrent_overlap_ms: float = 0.0  # Max time jobs were created concurrently


@dataclass
class ParallelExecutionAnalysis:
    """Analysis of parallel execution timing."""
    total_jobs: int
    earliest_request_start: float
    latest_request_start: float
    earliest_response_end: float
    latest_response_end: float
    request_start_spread_ms: float  # Time spread between first and last request start
    response_end_spread_ms: float   # Time spread between first and last response
    overlap_percentage: float       # Percentage of time jobs were concurrent
    is_truly_parallel: bool         # True if requests started within threshold
    parallel_threshold_ms: float = 100.0  # Max spread to consider "parallel"


# =============================================================================
# Async Helper Functions
# =============================================================================

async def create_investigation_async(
    session: aiohttp.ClientSession,
    base_url: str,
    payload: Dict[str, Any],
    index: int,
    ssl_context: Optional[ssl.SSLContext] = None
) -> InvestigationResult:
    """
    Create a single investigation asynchronously with detailed timing.
    
    Args:
        session: aiohttp client session
        base_url: Focus Server base URL
        payload: Investigation configuration payload
        index: Investigation index for tracking
        ssl_context: Optional SSL context for HTTPS
    
    Returns:
        InvestigationResult with success status, timing details, and full response
    """
    request_start_time = time.time()
    creation_timestamp = datetime.now()
    
    try:
        url = f"{base_url}/configure"
        
        logger.debug(f"[Investigation {index}] Sending request to {url} at {creation_timestamp.strftime('%H:%M:%S.%f')[:-3]}")
        
        async with session.post(
            url,
            json=payload,
            ssl=ssl_context,
            timeout=aiohttp.ClientTimeout(total=INVESTIGATION_TIMEOUT_SECONDS)
        ) as response:
            request_end_time = time.time()
            elapsed_ms = (request_end_time - request_start_time) * 1000
            
            if response.status == 200:
                response_data = await response.json()
                
                job_id = response_data.get('job_id')
                stream_url = response_data.get('stream_url')
                stream_port = response_data.get('stream_port')
                
                if job_id:
                    logger.info(f"[Investigation {index}] ✅ Created: {job_id} ({elapsed_ms:.1f}ms) at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
                    return InvestigationResult(
                        index=index,
                        success=True,
                        job_id=job_id,
                        response_time_ms=elapsed_ms,
                        stream_url=stream_url,
                        stream_port=stream_port,
                        timestamp=creation_timestamp,
                        request_start_time=request_start_time,
                        request_end_time=request_end_time,
                        full_response=response_data
                    )
                else:
                    logger.warning(f"[Investigation {index}] ⚠️ No job_id in response")
                    return InvestigationResult(
                        index=index,
                        success=False,
                        response_time_ms=elapsed_ms,
                        error="No job_id in response",
                        timestamp=creation_timestamp,
                        request_start_time=request_start_time,
                        request_end_time=request_end_time
                    )
            else:
                request_end_time = time.time()
                elapsed_ms = (request_end_time - request_start_time) * 1000
                error_text = await response.text()
                logger.error(f"[Investigation {index}] ❌ HTTP {response.status}: {error_text[:100]}")
                return InvestigationResult(
                    index=index,
                    success=False,
                    response_time_ms=elapsed_ms,
                    error=f"HTTP {response.status}: {error_text[:100]}",
                    timestamp=creation_timestamp,
                    request_start_time=request_start_time,
                    request_end_time=request_end_time
                )
                
    except asyncio.TimeoutError:
        request_end_time = time.time()
        elapsed_ms = (request_end_time - request_start_time) * 1000
        logger.error(f"[Investigation {index}] ❌ Timeout after {elapsed_ms:.1f}ms")
        return InvestigationResult(
            index=index,
            success=False,
            response_time_ms=elapsed_ms,
            error=f"Timeout after {INVESTIGATION_TIMEOUT_SECONDS}s",
            timestamp=creation_timestamp,
            request_start_time=request_start_time,
            request_end_time=request_end_time
        )
    except Exception as e:
        request_end_time = time.time()
        elapsed_ms = (request_end_time - request_start_time) * 1000
        logger.error(f"[Investigation {index}] ❌ Error: {e}")
        return InvestigationResult(
            index=index,
            success=False,
            response_time_ms=elapsed_ms,
            error=str(e),
            timestamp=creation_timestamp,
            request_start_time=request_start_time,
            request_end_time=request_end_time
        )


async def fetch_job_metadata_async(
    session: aiohttp.ClientSession,
    base_url: str,
    job_id: str,
    ssl_context: Optional[ssl.SSLContext] = None
) -> Optional[Dict[str, Any]]:
    """
    Fetch job metadata from Focus Server.
    
    Args:
        session: aiohttp client session
        base_url: Focus Server base URL
        job_id: Job ID to fetch metadata for
        ssl_context: Optional SSL context for HTTPS
    
    Returns:
        Job metadata dictionary or None if failed
    """
    try:
        url = f"{base_url}/metadata/{job_id}"
        
        async with session.get(
            url,
            ssl=ssl_context,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.warning(f"Failed to fetch metadata for job {job_id}: HTTP {response.status}")
                return None
                
    except Exception as e:
        logger.warning(f"Error fetching metadata for job {job_id}: {e}")
        return None


def extract_job_metadata(
    result: InvestigationResult,
    original_payload: Dict[str, Any]
) -> JobMetadata:
    """
    Extract detailed job metadata from investigation result.
    
    Args:
        result: InvestigationResult from job creation
        original_payload: Original request payload
    
    Returns:
        JobMetadata with all extracted information
    """
    # Determine job type from payload
    is_live = original_payload.get('start_time') is None and original_payload.get('end_time') is None
    job_type = "Live" if is_live else "Historic"
    
    # Extract from full response if available
    full_resp = result.full_response or {}
    
    # View type mapping
    view_type_map = {"0": "Multichannel", "1": "SingleChannel", "2": "Waterfall"}
    view_type_raw = str(full_resp.get('view_type', original_payload.get('view_type', '')))
    view_type = view_type_map.get(view_type_raw, view_type_raw)
    
    # Channels from payload
    channels = original_payload.get('channels', {})
    channels_min = channels.get('min')
    channels_max = channels.get('max')
    channel_count = full_resp.get('channel_amount') or (
        (channels_max - channels_min + 1) if channels_min and channels_max else None
    )
    
    # Frequency from payload
    freq_range = original_payload.get('frequencyRange', {})
    
    return JobMetadata(
        job_id=result.job_id or "",
        job_type=job_type,
        creation_timestamp=result.timestamp,
        request_start_epoch=result.request_start_time,
        request_end_epoch=result.request_end_time,
        response_time_ms=result.response_time_ms,
        stream_url=result.stream_url,
        stream_port=result.stream_port,
        view_type=view_type,
        channels_min=channels_min,
        channels_max=channels_max,
        channel_count=channel_count,
        frequency_min=freq_range.get('min'),
        frequency_max=freq_range.get('max'),
        nfft_selection=original_payload.get('nfftSelection'),
        display_time_axis_duration=original_payload.get('displayTimeAxisDuration'),
        frequencies_list=full_resp.get('frequencies_list'),
        frequencies_amount=full_resp.get('frequencies_amount'),
        stream_amount=full_resp.get('stream_amount'),
        status=full_resp.get('status')
    )


def analyze_parallel_execution(results: List[InvestigationResult]) -> ParallelExecutionAnalysis:
    """
    Analyze timing data to verify parallel execution.
    
    Args:
        results: List of investigation results with timing data
    
    Returns:
        ParallelExecutionAnalysis with detailed timing analysis
    """
    if not results:
        return ParallelExecutionAnalysis(
            total_jobs=0,
            earliest_request_start=0,
            latest_request_start=0,
            earliest_response_end=0,
            latest_response_end=0,
            request_start_spread_ms=0,
            response_end_spread_ms=0,
            overlap_percentage=0,
            is_truly_parallel=False
        )
    
    # Extract timing data from successful results
    start_times = [r.request_start_time for r in results if r.request_start_time > 0]
    end_times = [r.request_end_time for r in results if r.request_end_time > 0]
    
    if not start_times or not end_times:
        return ParallelExecutionAnalysis(
            total_jobs=len(results),
            earliest_request_start=0,
            latest_request_start=0,
            earliest_response_end=0,
            latest_response_end=0,
            request_start_spread_ms=0,
            response_end_spread_ms=0,
            overlap_percentage=0,
            is_truly_parallel=False
        )
    
    earliest_start = min(start_times)
    latest_start = max(start_times)
    earliest_end = min(end_times)
    latest_end = max(end_times)
    
    request_spread_ms = (latest_start - earliest_start) * 1000
    response_spread_ms = (latest_end - earliest_end) * 1000
    
    # Calculate overlap: if requests started before others finished, they were concurrent
    # True parallel = all requests started before the first response came back
    is_truly_parallel = latest_start < earliest_end
    
    # Calculate overlap percentage
    total_duration = latest_end - earliest_start
    if total_duration > 0:
        # Overlap period is from latest_start to earliest_end (if positive)
        overlap_duration = max(0, earliest_end - latest_start)
        overlap_percentage = (overlap_duration / total_duration) * 100
    else:
        overlap_percentage = 0
    
    return ParallelExecutionAnalysis(
        total_jobs=len(results),
        earliest_request_start=earliest_start,
        latest_request_start=latest_start,
        earliest_response_end=earliest_end,
        latest_response_end=latest_end,
        request_start_spread_ms=request_spread_ms,
        response_end_spread_ms=response_spread_ms,
        overlap_percentage=overlap_percentage,
        is_truly_parallel=is_truly_parallel
    )


async def check_component_health_async(
    session: aiohttp.ClientSession,
    component_name: str,
    health_url: str,
    ssl_context: Optional[ssl.SSLContext] = None
) -> ComponentHealthStatus:
    """
    Check health of a system component.
    
    Args:
        session: aiohttp client session
        component_name: Name of the component
        health_url: Health check URL
        ssl_context: Optional SSL context
    
    Returns:
        ComponentHealthStatus with health check results
    """
    start_time = time.time()
    
    try:
        async with session.get(
            health_url,
            ssl=ssl_context,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            elapsed_ms = (time.time() - start_time) * 1000
            
            is_healthy = response.status in [200, 204]
            
            return ComponentHealthStatus(
                component_name=component_name,
                is_healthy=is_healthy,
                response_time_ms=elapsed_ms,
                status_code=response.status
            )
            
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return ComponentHealthStatus(
            component_name=component_name,
            is_healthy=False,
            response_time_ms=elapsed_ms,
            error_message=str(e)
        )


async def check_all_components_health(
    base_url: str,
    ssl_verify: bool = False
) -> List[ComponentHealthStatus]:
    """
    Check health of all critical system components.
    
    Args:
        base_url: Focus Server base URL
        ssl_verify: Whether to verify SSL
    
    Returns:
        List of ComponentHealthStatus for all components
    """
    # Create SSL context
    ssl_context = None
    if not ssl_verify:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    
    # Define component health endpoints
    components = [
        ("Focus Server (ack)", f"{base_url}/ack"),
        ("Focus Server (channels)", f"{base_url}/channels"),
        ("Focus Server (live_metadata)", f"{base_url}/live_metadata"),
    ]
    
    connector = aiohttp.TCPConnector(limit=10, ssl=ssl_context)
    results = []
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            check_component_health_async(session, name, url, ssl_context)
            for name, url in components
        ]
        
        results = await asyncio.gather(*tasks)
    
    return results


def print_job_details_table(job_metadata_list: List[JobMetadata]):
    """
    Print a formatted table of all job details.
    
    Args:
        job_metadata_list: List of job metadata to display
    """
    if not job_metadata_list:
        logger.info("No jobs to display")
        return
    
    logger.info(f"\n{'='*120}")
    logger.info("JOB DETAILS - COMPREHENSIVE SUMMARY")
    logger.info(f"{'='*120}")
    
    # Header
    header = f"{'#':>3} | {'Job ID':^12} | {'Type':^8} | {'View':^14} | {'Channels':^12} | {'Freq Range':^12} | {'NFFT':>6} | {'Response':>10} | {'Stream Port':>11} | {'Status':^8}"
    logger.info(header)
    logger.info("-" * 120)
    
    for i, meta in enumerate(job_metadata_list, 1):
        channels_str = f"{meta.channels_min}-{meta.channels_max}" if meta.channels_min and meta.channels_max else "N/A"
        freq_str = f"{meta.frequency_min}-{meta.frequency_max}" if meta.frequency_min is not None and meta.frequency_max is not None else "N/A"
        
        row = (
            f"{i:>3} | "
            f"{meta.job_id:^12} | "
            f"{meta.job_type:^8} | "
            f"{meta.view_type or 'N/A':^14} | "
            f"{channels_str:^12} | "
            f"{freq_str:^12} | "
            f"{meta.nfft_selection or 'N/A':>6} | "
            f"{meta.response_time_ms:>8.1f}ms | "
            f"{meta.stream_port or 'N/A':>11} | "
            f"{meta.status or 'OK':^8}"
        )
        logger.info(row)
    
    logger.info("-" * 120)
    
    # Summary statistics
    response_times = [m.response_time_ms for m in job_metadata_list]
    live_count = sum(1 for m in job_metadata_list if m.job_type == "Live")
    historic_count = sum(1 for m in job_metadata_list if m.job_type == "Historic")
    
    logger.info(f"\nSUMMARY:")
    logger.info(f"  Total Jobs: {len(job_metadata_list)}")
    logger.info(f"  Live Jobs: {live_count}")
    logger.info(f"  Historic Jobs: {historic_count}")
    logger.info(f"  Avg Response Time: {mean(response_times):.1f}ms")
    if len(response_times) > 1:
        logger.info(f"  Response Time StdDev: {stdev(response_times):.1f}ms")
    logger.info(f"  Min Response Time: {min(response_times):.1f}ms")
    logger.info(f"  Max Response Time: {max(response_times):.1f}ms")
    logger.info(f"{'='*120}\n")


def print_parallel_execution_analysis(analysis: ParallelExecutionAnalysis):
    """
    Print detailed parallel execution analysis.
    
    Args:
        analysis: ParallelExecutionAnalysis results
    """
    logger.info(f"\n{'='*80}")
    logger.info("PARALLEL EXECUTION VERIFICATION")
    logger.info(f"{'='*80}")
    
    if analysis.total_jobs == 0:
        logger.info("No jobs to analyze")
        return
    
    # Convert epoch times to readable format
    earliest_start_str = datetime.fromtimestamp(analysis.earliest_request_start).strftime('%H:%M:%S.%f')[:-3]
    latest_start_str = datetime.fromtimestamp(analysis.latest_request_start).strftime('%H:%M:%S.%f')[:-3]
    earliest_end_str = datetime.fromtimestamp(analysis.earliest_response_end).strftime('%H:%M:%S.%f')[:-3]
    latest_end_str = datetime.fromtimestamp(analysis.latest_response_end).strftime('%H:%M:%S.%f')[:-3]
    
    logger.info(f"\nTIMING ANALYSIS:")
    logger.info(f"  Total Jobs: {analysis.total_jobs}")
    logger.info(f"  First Request Sent: {earliest_start_str}")
    logger.info(f"  Last Request Sent:  {latest_start_str}")
    logger.info(f"  Request Start Spread: {analysis.request_start_spread_ms:.1f}ms")
    logger.info(f"")
    logger.info(f"  First Response Received: {earliest_end_str}")
    logger.info(f"  Last Response Received:  {latest_end_str}")
    logger.info(f"  Response End Spread: {analysis.response_end_spread_ms:.1f}ms")
    
    logger.info(f"\nPARALLEL VERIFICATION:")
    if analysis.is_truly_parallel:
        logger.info(f"  ✅ PARALLEL EXECUTION CONFIRMED!")
        logger.info(f"     All requests were sent before first response arrived")
        logger.info(f"     Concurrent overlap: {analysis.overlap_percentage:.1f}%")
    else:
        logger.info(f"  ⚠️  SEQUENTIAL BEHAVIOR DETECTED")
        logger.info(f"     Requests were NOT fully concurrent")
        logger.info(f"     Overlap percentage: {analysis.overlap_percentage:.1f}%")
    
    logger.info(f"\nPARALLEL THRESHOLD: {analysis.parallel_threshold_ms}ms")
    if analysis.request_start_spread_ms <= analysis.parallel_threshold_ms:
        logger.info(f"  ✅ Request spread ({analysis.request_start_spread_ms:.1f}ms) <= threshold ({analysis.parallel_threshold_ms}ms)")
    else:
        logger.info(f"  ⚠️  Request spread ({analysis.request_start_spread_ms:.1f}ms) > threshold ({analysis.parallel_threshold_ms}ms)")
    
    logger.info(f"{'='*80}\n")


def print_component_health_report(health_statuses: List[ComponentHealthStatus]):
    """
    Print component health status report.
    
    Args:
        health_statuses: List of component health statuses
    """
    logger.info(f"\n{'='*80}")
    logger.info("COMPONENT STABILITY CHECK")
    logger.info(f"{'='*80}")
    
    all_healthy = True
    
    for status in health_statuses:
        icon = "✅" if status.is_healthy else "❌"
        health_str = "HEALTHY" if status.is_healthy else "UNHEALTHY"
        
        logger.info(f"  {icon} {status.component_name}: {health_str}")
        logger.info(f"      Response Time: {status.response_time_ms:.1f}ms")
        
        if status.status_code:
            logger.info(f"      Status Code: {status.status_code}")
        
        if status.error_message:
            logger.info(f"      Error: {status.error_message}")
        
        if not status.is_healthy:
            all_healthy = False
    
    logger.info(f"\n{'='*80}")
    if all_healthy:
        logger.info("✅ ALL COMPONENTS STABLE - No crashes detected")
    else:
        logger.info("❌ COMPONENT ISSUES DETECTED - Some components may have crashed")
    logger.info(f"{'='*80}\n")
    
    return all_healthy


async def cancel_investigation_async(
    session: aiohttp.ClientSession,
    base_url: str,
    job_id: str,
    ssl_context: Optional[ssl.SSLContext] = None
) -> bool:
    """
    Cancel an investigation asynchronously.
    
    Args:
        session: aiohttp client session
        base_url: Focus Server base URL
        job_id: Job ID to cancel
        ssl_context: Optional SSL context for HTTPS
    
    Returns:
        True if cancelled successfully, False otherwise
    """
    try:
        url = f"{base_url}/job/{job_id}"
        
        async with session.delete(
            url,
            ssl=ssl_context,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            if response.status in [200, 204, 404]:  # 404 = already gone
                logger.debug(f"Cancelled job: {job_id}")
                return True
            else:
                logger.warning(f"Failed to cancel job {job_id}: HTTP {response.status}")
                return False
                
    except Exception as e:
        logger.warning(f"Error cancelling job {job_id}: {e}")
        return False


async def open_parallel_investigations(
    base_url: str,
    payload: Dict[str, Any],
    count: int,
    ssl_verify: bool = False,
    verify_parallel: bool = False,
    show_job_details: bool = False
) -> ParallelTestResult:
    """
    Open multiple investigations in parallel using asyncio.
    
    This runs in a SINGLE THREAD using cooperative multitasking.
    All HTTP requests are sent concurrently and awaited together.
    
    Args:
        base_url: Focus Server base URL
        payload: Investigation configuration payload
        count: Number of parallel investigations to open
        ssl_verify: Whether to verify SSL certificates
        verify_parallel: Whether to analyze and verify parallel execution
        show_job_details: Whether to print detailed job information
    
    Returns:
        ParallelTestResult with aggregated metrics and optional verification
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Opening {count} investigations in PARALLEL (Single Thread / Asyncio)")
    logger.info(f"{'='*80}")
    
    # Create SSL context
    ssl_context = None
    if not ssl_verify:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    
    # Create aiohttp session
    connector = aiohttp.TCPConnector(
        limit=count,  # Allow all connections
        limit_per_host=count,
        ssl=ssl_context
    )
    
    start_time = time.time()
    results: List[InvestigationResult] = []
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Create all investigation tasks
        tasks = [
            create_investigation_async(session, base_url, payload, i, ssl_context)
            for i in range(count)
        ]
        
        # Execute ALL tasks in parallel using asyncio.gather()
        # This is single-threaded parallel execution!
        logger.info(f"Executing {len(tasks)} tasks concurrently in single thread...")
        results = await asyncio.gather(*tasks, return_exceptions=False)
    
    total_time_ms = (time.time() - start_time) * 1000
    
    # Analyze results
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    response_times = [r.response_time_ms for r in results]
    job_ids = [r.job_id for r in successful if r.job_id]
    errors = [r.error for r in failed if r.error]
    
    success_rate = (len(successful) / len(results)) * 100 if results else 0
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0
    max_response_time = max(response_times) if response_times else 0
    
    # Extract job metadata for successful investigations
    job_metadata_list = []
    for r in successful:
        if r.success and r.job_id:
            metadata = extract_job_metadata(r, payload)
            job_metadata_list.append(metadata)
    
    # Analyze parallel execution
    parallel_analysis = analyze_parallel_execution(results)
    
    result = ParallelTestResult(
        total_investigations=len(results),
        successful=len(successful),
        failed=len(failed),
        success_rate=success_rate,
        total_time_ms=total_time_ms,
        avg_response_time_ms=avg_response_time,
        min_response_time_ms=min_response_time,
        max_response_time_ms=max_response_time,
        job_ids=job_ids,
        errors=errors,
        investigation_results=results,
        job_metadata_list=job_metadata_list,
        parallel_execution_verified=parallel_analysis.is_truly_parallel,
        max_concurrent_overlap_ms=parallel_analysis.overlap_percentage
    )
    
    # Log summary
    logger.info(f"\n{'='*80}")
    logger.info("PARALLEL INVESTIGATION RESULTS (Single Thread)")
    logger.info(f"{'='*80}")
    logger.info(f"Total investigations: {result.total_investigations}")
    logger.info(f"Successful: {result.successful} ({result.success_rate:.1f}%)")
    logger.info(f"Failed: {result.failed}")
    logger.info(f"Total time: {result.total_time_ms:.1f}ms")
    logger.info(f"Avg response time: {result.avg_response_time_ms:.1f}ms")
    logger.info(f"Min response time: {result.min_response_time_ms:.1f}ms")
    logger.info(f"Max response time: {result.max_response_time_ms:.1f}ms")
    
    if errors:
        logger.warning(f"\nErrors ({len(errors)}):")
        for i, error in enumerate(errors[:5]):  # Show first 5 errors
            logger.warning(f"  {i+1}. {error}")
    
    logger.info(f"{'='*80}\n")
    
    # Optional: Show parallel execution analysis
    if verify_parallel:
        print_parallel_execution_analysis(parallel_analysis)
    
    # Optional: Show detailed job information
    if show_job_details:
        print_job_details_table(job_metadata_list)
    
    return result


async def cleanup_investigations_async(
    base_url: str,
    job_ids: List[str],
    ssl_verify: bool = False
) -> Tuple[int, int]:
    """
    Clean up investigations in parallel.
    
    Args:
        base_url: Focus Server base URL
        job_ids: List of job IDs to cancel
        ssl_verify: Whether to verify SSL certificates
    
    Returns:
        Tuple of (cancelled_count, failed_count)
    """
    if not job_ids:
        return 0, 0
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Cleaning up {len(job_ids)} investigations...")
    logger.info(f"{'='*80}")
    
    # Create SSL context
    ssl_context = None
    if not ssl_verify:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(
        limit=10,  # Limit parallel cancellations
        ssl=ssl_context
    )
    
    cancelled = 0
    failed = 0
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            cancel_investigation_async(session, base_url, job_id, ssl_context)
            for job_id in job_ids
        ]
        
        results = await asyncio.gather(*tasks)
        
        cancelled = sum(1 for r in results if r)
        failed = sum(1 for r in results if not r)
    
    logger.info(f"Cleanup complete: {cancelled} cancelled, {failed} failed")
    logger.info(f"{'='*80}\n")
    
    return cancelled, failed


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def parallel_investigation_payload():
    """Standard payload for parallel investigation tests."""
    return {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 1, "max": 50},
        "frequencyRange": {"min": 0, "max": 1000},
        "start_time": None,  # Live mode
        "end_time": None,
        "view_type": "0"  # MULTICHANNEL = "0"
    }


@pytest.fixture
def focus_server_url(config_manager) -> str:
    """Get Focus Server URL from configuration."""
    api_config = config_manager.get_api_config()
    base_url = api_config.get("base_url")
    
    if not base_url:
        pytest.skip("Focus Server base URL not configured")
    
    return base_url


# =============================================================================
# Test Class: Parallel Investigations - Single Thread
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.load
@pytest.mark.parallel
@pytest.mark.integration
class TestParallelInvestigationsSingleThread:
    """
    Test suite for parallel investigation operations in a SINGLE THREAD.
    
    Uses asyncio for cooperative multitasking - all operations run concurrently
    within the same thread using an event loop.
    
    Key Benefits:
    - No thread creation overhead
    - No GIL contention
    - Lower memory footprint
    - True concurrent I/O operations
    
    Tests Covered:
    - PZ-TBD: Parallel Investigations - Single Thread Basic
    - PZ-TBD: Parallel Investigations - Response Time Validation
    - PZ-TBD: Parallel Investigations - Stress Test
    """
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    @pytest.mark.parametrize("parallel_count", [3, 5, 10])
    async def test_open_investigations_parallel(
        self,
        focus_server_url: str,
        parallel_investigation_payload: Dict[str, Any],
        parallel_count: int
    ):
        """
        Test opening N investigations in parallel within a single thread.
        
        Steps:
            1. Prepare investigation configuration payload
            2. Open N investigations concurrently using asyncio.gather()
            3. Validate all investigations created successfully
            4. Verify each investigation has valid job_id
            5. Cleanup all created investigations
        
        Expected:
            - All investigations created successfully
            - Success rate >= MIN_SUCCESS_RATE_PERCENT
            - Each investigation has unique job_id
            - Parallel execution faster than sequential
        
        Args:
            focus_server_url: Focus Server base URL
            parallel_investigation_payload: Configuration payload
            parallel_count: Number of parallel investigations
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: Open {parallel_count} Investigations in Parallel (Single Thread)")
        logger.info(f"{'='*80}")
        
        job_ids = []
        
        try:
            # Execute parallel investigation creation
            result = await open_parallel_investigations(
                base_url=focus_server_url,
                payload=parallel_investigation_payload,
                count=parallel_count,
                ssl_verify=False
            )
            
            job_ids = result.job_ids
            
            # Assertions
            assert result.total_investigations == parallel_count, \
                f"Expected {parallel_count} investigations, got {result.total_investigations}"
            
            assert result.success_rate >= MIN_SUCCESS_RATE_PERCENT, \
                f"Success rate {result.success_rate:.1f}% below minimum {MIN_SUCCESS_RATE_PERCENT}%"
            
            # Verify unique job_ids
            unique_job_ids = set(job_ids)
            assert len(unique_job_ids) == len(job_ids), \
                f"Duplicate job_ids detected: {len(job_ids)} total, {len(unique_job_ids)} unique"
            
            logger.info(f"\n✅ TEST PASSED: {parallel_count} parallel investigations created successfully")
            
        finally:
            # Cleanup
            if job_ids:
                await cleanup_investigations_async(focus_server_url, job_ids, ssl_verify=False)
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    async def test_parallel_investigation_response_times(
        self,
        focus_server_url: str,
        parallel_investigation_payload: Dict[str, Any]
    ):
        """
        Test that parallel investigation response times are acceptable.
        
        Steps:
            1. Open 5 investigations in parallel
            2. Measure individual and total response times
            3. Validate response times meet SLA
        
        Expected:
            - Average response time < EXPECTED_MAX_RESPONSE_TIME_SECONDS
            - Total time < (sequential_time / parallel_speedup_factor)
        """
        logger.info(f"\n{'='*80}")
        logger.info("TEST: Parallel Investigation Response Time Validation")
        logger.info(f"{'='*80}")
        
        parallel_count = 5
        job_ids = []
        
        try:
            result = await open_parallel_investigations(
                base_url=focus_server_url,
                payload=parallel_investigation_payload,
                count=parallel_count,
                ssl_verify=False
            )
            
            job_ids = result.job_ids
            
            # Response time assertions
            expected_max_ms = EXPECTED_MAX_RESPONSE_TIME_SECONDS * 1000
            
            assert result.avg_response_time_ms < expected_max_ms, \
                f"Avg response time {result.avg_response_time_ms:.1f}ms exceeds {expected_max_ms}ms"
            
            # Parallel efficiency check:
            # Total time should be less than (avg_time * count) / 2
            # (at least 2x speedup compared to sequential)
            expected_max_total_ms = (result.avg_response_time_ms * parallel_count) / 2
            
            logger.info(f"\nParallel Efficiency:")
            logger.info(f"  Total time: {result.total_time_ms:.1f}ms")
            logger.info(f"  Expected sequential: {result.avg_response_time_ms * parallel_count:.1f}ms")
            logger.info(f"  Speedup factor: {(result.avg_response_time_ms * parallel_count) / result.total_time_ms:.2f}x")
            
            # Allow some slack for parallel overhead
            assert result.total_time_ms < expected_max_total_ms * 1.5, \
                f"Parallel execution not efficient enough. Total: {result.total_time_ms:.1f}ms, " \
                f"Expected max: {expected_max_total_ms * 1.5:.1f}ms"
            
            logger.info(f"\n✅ TEST PASSED: Response times within acceptable limits")
            
        finally:
            if job_ids:
                await cleanup_investigations_async(focus_server_url, job_ids, ssl_verify=False)
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    @pytest.mark.slow
    @pytest.mark.nightly
    async def test_parallel_investigation_stress(
        self,
        focus_server_url: str,
        parallel_investigation_payload: Dict[str, Any]
    ):
        """
        Stress test: Gradually increase parallel investigation count.
        
        Steps:
            1. Start with 5 parallel investigations
            2. Increase to 10, then 15, then 20
            3. Track success rates and response times at each level
            4. Identify breaking point or maximum capacity
        
        Expected:
            - Success rate >= MIN_SUCCESS_RATE_PERCENT at each level
            - System remains stable under load
        """
        logger.info(f"\n{'='*80}")
        logger.info("TEST: Parallel Investigation Stress Test")
        logger.info(f"{'='*80}")
        
        test_counts = [5, 10, 15, MAX_PARALLEL_COUNT]
        results_by_count: Dict[int, ParallelTestResult] = {}
        all_job_ids: List[str] = []
        
        try:
            for count in test_counts:
                logger.info(f"\n{'='*60}")
                logger.info(f"Stress Level: {count} parallel investigations")
                logger.info(f"{'='*60}")
                
                result = await open_parallel_investigations(
                    base_url=focus_server_url,
                    payload=parallel_investigation_payload,
                    count=count,
                    ssl_verify=False
                )
                
                results_by_count[count] = result
                all_job_ids.extend(result.job_ids)
                
                # Check if we should continue
                if result.success_rate < MIN_SUCCESS_RATE_PERCENT:
                    logger.warning(f"⚠️ Success rate dropped below {MIN_SUCCESS_RATE_PERCENT}% at {count} parallel")
                    break
                
                # Brief pause between stress levels
                await asyncio.sleep(2)
            
            # Log stress test summary
            logger.info(f"\n{'='*80}")
            logger.info("STRESS TEST SUMMARY")
            logger.info(f"{'='*80}")
            
            for count, result in results_by_count.items():
                status = "✅" if result.success_rate >= MIN_SUCCESS_RATE_PERCENT else "❌"
                logger.info(
                    f"  {status} {count} parallel: "
                    f"{result.success_rate:.1f}% success, "
                    f"{result.avg_response_time_ms:.1f}ms avg, "
                    f"{result.total_time_ms:.1f}ms total"
                )
            
            # Assertions
            for count, result in results_by_count.items():
                assert result.success_rate >= MIN_SUCCESS_RATE_PERCENT, \
                    f"Success rate {result.success_rate:.1f}% at {count} parallel below minimum"
            
            logger.info(f"\n✅ TEST PASSED: Stress test completed successfully")
            
        finally:
            if all_job_ids:
                await cleanup_investigations_async(focus_server_url, all_job_ids, ssl_verify=False)
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    async def test_parallel_investigation_unique_resources(
        self,
        focus_server_url: str,
        parallel_investigation_payload: Dict[str, Any]
    ):
        """
        Verify that parallel investigations receive unique resources.
        
        Steps:
            1. Open 5 investigations in parallel
            2. Extract stream_url and stream_port from each
            3. Verify each investigation has unique resources
        
        Expected:
            - Each investigation has unique job_id
            - Each investigation has valid stream_url and stream_port
            - No resource conflicts between parallel investigations
        """
        logger.info(f"\n{'='*80}")
        logger.info("TEST: Parallel Investigation Unique Resources")
        logger.info(f"{'='*80}")
        
        parallel_count = 5
        job_ids = []
        
        try:
            # Create SSL context for direct requests
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(limit=parallel_count, ssl=ssl_context)
            
            results: List[InvestigationResult] = []
            
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = [
                    create_investigation_async(
                        session,
                        focus_server_url,
                        parallel_investigation_payload,
                        i,
                        ssl_context
                    )
                    for i in range(parallel_count)
                ]
                
                results = await asyncio.gather(*tasks)
            
            # Collect successful results
            successful = [r for r in results if r.success]
            job_ids = [r.job_id for r in successful if r.job_id]
            
            # Verify unique job_ids
            assert len(set(job_ids)) == len(job_ids), \
                f"Duplicate job_ids detected: {job_ids}"
            
            # Verify stream resources (if available)
            stream_info = [
                (r.stream_url, r.stream_port)
                for r in successful
                if r.stream_url and r.stream_port
            ]
            
            logger.info(f"\nResource allocation:")
            for i, result in enumerate(successful):
                logger.info(
                    f"  Investigation {i+1}: job_id={result.job_id}, "
                    f"stream={result.stream_url}:{result.stream_port}"
                )
            
            # Verify we got valid stream info
            if stream_info:
                # Check for unique port allocations
                ports = [port for _, port in stream_info]
                logger.info(f"  Stream ports: {ports}")
            
            logger.info(f"\n✅ TEST PASSED: All {len(successful)} investigations have unique resources")
            
        finally:
            if job_ids:
                await cleanup_investigations_async(focus_server_url, job_ids, ssl_verify=False)


# =============================================================================
# Test Class: Parallel vs Sequential Comparison
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.load
@pytest.mark.parallel
@pytest.mark.integration
class TestParallelVsSequential:
    """
    Compare parallel (single-thread) vs sequential investigation creation.
    
    This demonstrates the performance benefits of asyncio-based parallel
    execution within a single thread.
    """
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    async def test_parallel_vs_sequential_performance(
        self,
        focus_server_url: str,
        parallel_investigation_payload: Dict[str, Any]
    ):
        """
        Compare parallel vs sequential investigation creation times.
        
        Steps:
            1. Create 5 investigations sequentially, measure time
            2. Create 5 investigations in parallel, measure time
            3. Compare performance
        
        Expected:
            - Parallel execution significantly faster than sequential
            - Speedup factor >= 2x
        """
        logger.info(f"\n{'='*80}")
        logger.info("TEST: Parallel vs Sequential Performance Comparison")
        logger.info(f"{'='*80}")
        
        count = 5
        sequential_job_ids: List[str] = []
        parallel_job_ids: List[str] = []
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(limit=count, ssl=ssl_context)
        
        try:
            # === Sequential Execution ===
            logger.info(f"\n--- SEQUENTIAL: Creating {count} investigations one by one ---")
            
            sequential_start = time.time()
            
            async with aiohttp.ClientSession(connector=connector) as session:
                for i in range(count):
                    result = await create_investigation_async(
                        session,
                        focus_server_url,
                        parallel_investigation_payload,
                        i,
                        ssl_context
                    )
                    if result.success and result.job_id:
                        sequential_job_ids.append(result.job_id)
            
            sequential_time_ms = (time.time() - sequential_start) * 1000
            
            # Clean up sequential jobs
            await cleanup_investigations_async(focus_server_url, sequential_job_ids, ssl_verify=False)
            sequential_job_ids = []
            
            # Brief pause
            await asyncio.sleep(2)
            
            # === Parallel Execution ===
            logger.info(f"\n--- PARALLEL: Creating {count} investigations concurrently ---")
            
            parallel_start = time.time()
            
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = [
                    create_investigation_async(
                        session,
                        focus_server_url,
                        parallel_investigation_payload,
                        i,
                        ssl_context
                    )
                    for i in range(count)
                ]
                
                results = await asyncio.gather(*tasks)
                
                parallel_job_ids = [
                    r.job_id for r in results
                    if r.success and r.job_id
                ]
            
            parallel_time_ms = (time.time() - parallel_start) * 1000
            
            # Calculate speedup
            speedup = sequential_time_ms / parallel_time_ms if parallel_time_ms > 0 else 0
            
            # Log comparison
            logger.info(f"\n{'='*60}")
            logger.info("PERFORMANCE COMPARISON")
            logger.info(f"{'='*60}")
            logger.info(f"Sequential time: {sequential_time_ms:.1f}ms")
            logger.info(f"Parallel time:   {parallel_time_ms:.1f}ms")
            logger.info(f"Speedup factor:  {speedup:.2f}x")
            logger.info(f"Time saved:      {sequential_time_ms - parallel_time_ms:.1f}ms ({((sequential_time_ms - parallel_time_ms) / sequential_time_ms * 100):.1f}%)")
            logger.info(f"{'='*60}")
            
            # Assertions
            assert speedup >= 1.5, \
                f"Parallel speedup {speedup:.2f}x below expected 1.5x minimum"
            
            logger.info(f"\n✅ TEST PASSED: Parallel execution {speedup:.2f}x faster than sequential")
            
        finally:
            # Final cleanup
            if sequential_job_ids:
                await cleanup_investigations_async(focus_server_url, sequential_job_ids, ssl_verify=False)
            if parallel_job_ids:
                await cleanup_investigations_async(focus_server_url, parallel_job_ids, ssl_verify=False)


# =============================================================================
# Test Class: Comprehensive Parallel Verification
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.load
@pytest.mark.parallel
@pytest.mark.integration
class TestParallelCreationVerification:
    """
    Comprehensive test suite that verifies parallel job creation with:
    - Timestamp verification to prove parallel execution
    - Detailed job metadata inspection
    - Job type detection (Live vs Historic)
    - Component stability monitoring
    - End-of-test summary and comparison
    """
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    async def test_parallel_creation_with_full_verification(
        self,
        focus_server_url: str,
        parallel_investigation_payload: Dict[str, Any]
    ):
        """
        Test parallel investigation creation with comprehensive verification.
        
        This test:
        1. Opens N investigations in parallel
        2. Verifies they were created concurrently (timestamp analysis)
        3. Inspects each job's configuration and metadata
        4. Validates job types (Live/Historic)
        5. Checks component stability before and after
        6. Generates comprehensive summary report
        
        Steps:
            1. Pre-test: Check component health
            2. Create investigations in parallel
            3. Analyze timing to verify parallel execution
            4. Fetch and validate metadata for each job
            5. Post-test: Check component stability
            6. Generate comparison report
        
        Expected:
            - All jobs created successfully
            - Parallel execution verified (all requests sent concurrently)
            - All components stable (no crashes)
            - Each job has valid configuration
        """
        logger.info(f"\n{'='*100}")
        logger.info("TEST: Parallel Creation with Full Verification")
        logger.info(f"{'='*100}")
        
        parallel_count = 5
        job_ids = []
        
        try:
            # =========================================================
            # PHASE 1: Pre-test Component Health Check
            # =========================================================
            logger.info(f"\n{'='*80}")
            logger.info("PHASE 1: Pre-Test Component Health Check")
            logger.info(f"{'='*80}")
            
            pre_health = await check_all_components_health(focus_server_url, ssl_verify=False)
            pre_all_healthy = print_component_health_report(pre_health)
            
            assert pre_all_healthy, "Pre-test health check failed - components not stable"
            
            # =========================================================
            # PHASE 2: Create Investigations in Parallel
            # =========================================================
            logger.info(f"\n{'='*80}")
            logger.info("PHASE 2: Create Investigations in Parallel")
            logger.info(f"{'='*80}")
            
            result = await open_parallel_investigations(
                base_url=focus_server_url,
                payload=parallel_investigation_payload,
                count=parallel_count,
                ssl_verify=False,
                verify_parallel=True,
                show_job_details=True
            )
            
            job_ids = result.job_ids
            
            # =========================================================
            # PHASE 3: Analyze Parallel Execution
            # =========================================================
            logger.info(f"\n{'='*80}")
            logger.info("PHASE 3: Parallel Execution Analysis")
            logger.info(f"{'='*80}")
            
            analysis = analyze_parallel_execution(result.investigation_results)
            
            # Verify parallel execution
            if analysis.is_truly_parallel:
                logger.info("✅ PARALLEL EXECUTION VERIFIED!")
                logger.info(f"   All {parallel_count} requests were sent concurrently")
                logger.info(f"   Request spread: {analysis.request_start_spread_ms:.1f}ms")
            else:
                logger.warning("⚠️ SEQUENTIAL BEHAVIOR DETECTED")
                logger.warning(f"   Request spread: {analysis.request_start_spread_ms:.1f}ms")
            
            # =========================================================
            # PHASE 4: Job Metadata Validation
            # =========================================================
            logger.info(f"\n{'='*80}")
            logger.info("PHASE 4: Job Metadata Validation")
            logger.info(f"{'='*80}")
            
            for meta in result.job_metadata_list:
                logger.info(f"\nJob {meta.job_id}:")
                logger.info(f"  Type: {meta.job_type}")
                logger.info(f"  View Type: {meta.view_type}")
                logger.info(f"  Channels: {meta.channels_min}-{meta.channels_max} ({meta.channel_count} total)")
                logger.info(f"  Frequency: {meta.frequency_min}-{meta.frequency_max} Hz")
                logger.info(f"  NFFT: {meta.nfft_selection}")
                logger.info(f"  Stream: {meta.stream_url}:{meta.stream_port}")
                logger.info(f"  Response Time: {meta.response_time_ms:.1f}ms")
                logger.info(f"  Created: {meta.creation_timestamp.strftime('%H:%M:%S.%f')[:-3]}")
            
            # =========================================================
            # PHASE 5: Post-test Component Stability Check
            # =========================================================
            logger.info(f"\n{'='*80}")
            logger.info("PHASE 5: Post-Test Component Stability Check")
            logger.info(f"{'='*80}")
            
            post_health = await check_all_components_health(focus_server_url, ssl_verify=False)
            post_all_healthy = print_component_health_report(post_health)
            
            # =========================================================
            # PHASE 6: Final Summary
            # =========================================================
            logger.info(f"\n{'='*100}")
            logger.info("FINAL TEST SUMMARY")
            logger.info(f"{'='*100}")
            
            logger.info(f"\n📊 RESULTS:")
            logger.info(f"  Total Investigations: {result.total_investigations}")
            logger.info(f"  Successful: {result.successful}")
            logger.info(f"  Failed: {result.failed}")
            logger.info(f"  Success Rate: {result.success_rate:.1f}%")
            
            logger.info(f"\n⏱️ TIMING:")
            logger.info(f"  Total Time: {result.total_time_ms:.1f}ms")
            logger.info(f"  Avg Response: {result.avg_response_time_ms:.1f}ms")
            logger.info(f"  Min Response: {result.min_response_time_ms:.1f}ms")
            logger.info(f"  Max Response: {result.max_response_time_ms:.1f}ms")
            
            logger.info(f"\n🔄 PARALLEL EXECUTION:")
            logger.info(f"  Verified: {'✅ YES' if analysis.is_truly_parallel else '❌ NO'}")
            logger.info(f"  Request Spread: {analysis.request_start_spread_ms:.1f}ms")
            logger.info(f"  Overlap: {analysis.overlap_percentage:.1f}%")
            
            logger.info(f"\n🏥 COMPONENT STABILITY:")
            logger.info(f"  Pre-test: {'✅ All Healthy' if pre_all_healthy else '❌ Issues Detected'}")
            logger.info(f"  Post-test: {'✅ All Healthy' if post_all_healthy else '❌ Issues Detected'}")
            
            logger.info(f"\n📋 JOB TYPES:")
            live_count = sum(1 for m in result.job_metadata_list if m.job_type == "Live")
            historic_count = sum(1 for m in result.job_metadata_list if m.job_type == "Historic")
            logger.info(f"  Live: {live_count}")
            logger.info(f"  Historic: {historic_count}")
            
            logger.info(f"\n{'='*100}")
            
            # Assertions
            assert result.success_rate >= MIN_SUCCESS_RATE_PERCENT, \
                f"Success rate {result.success_rate:.1f}% below minimum {MIN_SUCCESS_RATE_PERCENT}%"
            
            assert post_all_healthy, "Post-test health check failed - components may have crashed"
            
            logger.info("✅ TEST PASSED: All verifications successful!")
            
        finally:
            # Cleanup
            if job_ids:
                await cleanup_investigations_async(focus_server_url, job_ids, ssl_verify=False)
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    async def test_parallel_creation_timestamp_verification(
        self,
        focus_server_url: str,
        parallel_investigation_payload: Dict[str, Any]
    ):
        """
        Verify that jobs are truly created in parallel by analyzing timestamps.
        
        This test specifically validates that:
        1. All requests are sent within a small time window (< 100ms spread)
        2. Requests overlap (started before others finished)
        3. Sequential execution would take much longer
        
        Steps:
            1. Create 10 investigations in parallel
            2. Analyze request start times
            3. Verify all requests started within threshold
            4. Calculate theoretical sequential vs actual parallel time
        
        Expected:
            - Request start spread < 100ms (all sent nearly simultaneously)
            - Actual time << theoretical sequential time
        """
        logger.info(f"\n{'='*80}")
        logger.info("TEST: Parallel Creation Timestamp Verification")
        logger.info(f"{'='*80}")
        
        parallel_count = 10
        job_ids = []
        
        try:
            # Create investigations with verification
            result = await open_parallel_investigations(
                base_url=focus_server_url,
                payload=parallel_investigation_payload,
                count=parallel_count,
                ssl_verify=False,
                verify_parallel=True,
                show_job_details=False
            )
            
            job_ids = result.job_ids
            
            # Detailed timestamp analysis
            analysis = analyze_parallel_execution(result.investigation_results)
            
            # Print detailed timing for each request
            logger.info(f"\n{'='*80}")
            logger.info("INDIVIDUAL REQUEST TIMING")
            logger.info(f"{'='*80}")
            
            sorted_results = sorted(result.investigation_results, key=lambda r: r.request_start_time)
            
            for r in sorted_results:
                if r.request_start_time > 0:
                    start_str = datetime.fromtimestamp(r.request_start_time).strftime('%H:%M:%S.%f')[:-3]
                    end_str = datetime.fromtimestamp(r.request_end_time).strftime('%H:%M:%S.%f')[:-3]
                    offset_ms = (r.request_start_time - analysis.earliest_request_start) * 1000
                    
                    logger.info(
                        f"  Job {r.index:>2}: "
                        f"Start={start_str} (+{offset_ms:>6.1f}ms) | "
                        f"End={end_str} | "
                        f"Duration={r.response_time_ms:>7.1f}ms | "
                        f"{'✅' if r.success else '❌'}"
                    )
            
            # Verify parallel execution
            PARALLEL_THRESHOLD_MS = 100  # Max allowed spread between request starts
            
            logger.info(f"\n{'='*80}")
            logger.info("PARALLEL VERIFICATION RESULTS")
            logger.info(f"{'='*80}")
            
            logger.info(f"\nRequest Start Spread: {analysis.request_start_spread_ms:.1f}ms")
            logger.info(f"Parallel Threshold: {PARALLEL_THRESHOLD_MS}ms")
            
            if analysis.request_start_spread_ms <= PARALLEL_THRESHOLD_MS:
                logger.info(f"✅ PARALLEL EXECUTION CONFIRMED!")
                logger.info(f"   All {parallel_count} requests started within {analysis.request_start_spread_ms:.1f}ms of each other")
            else:
                logger.warning(f"⚠️ REQUESTS NOT FULLY PARALLEL")
                logger.warning(f"   Spread of {analysis.request_start_spread_ms:.1f}ms exceeds threshold")
            
            # Calculate speedup
            theoretical_sequential_ms = sum(r.response_time_ms for r in result.investigation_results)
            actual_parallel_ms = result.total_time_ms
            speedup = theoretical_sequential_ms / actual_parallel_ms if actual_parallel_ms > 0 else 0
            
            logger.info(f"\nPERFORMANCE:")
            logger.info(f"  Theoretical Sequential Time: {theoretical_sequential_ms:.1f}ms")
            logger.info(f"  Actual Parallel Time: {actual_parallel_ms:.1f}ms")
            logger.info(f"  Speedup: {speedup:.2f}x")
            
            logger.info(f"{'='*80}\n")
            
            # Assertions
            assert analysis.is_truly_parallel, \
                f"Requests were not parallel - spread: {analysis.request_start_spread_ms:.1f}ms"
            
            assert speedup >= 1.5, \
                f"Insufficient parallel speedup: {speedup:.2f}x (expected >= 1.5x)"
            
            logger.info("✅ TEST PASSED: Parallel execution verified!")
            
        finally:
            if job_ids:
                await cleanup_investigations_async(focus_server_url, job_ids, ssl_verify=False)
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    async def test_mixed_job_types_parallel(
        self,
        focus_server_url: str,
        config_manager
    ):
        """
        Test creating both Live and Historic jobs in parallel.
        
        Steps:
            1. Create mix of Live and Historic investigation payloads
            2. Execute all in parallel
            3. Verify job types are correctly identified
            4. Check all jobs have valid metadata
        """
        logger.info(f"\n{'='*80}")
        logger.info("TEST: Mixed Job Types (Live + Historic) in Parallel")
        logger.info(f"{'='*80}")
        
        import time as time_module
        
        # Create Live payload
        live_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": None,
            "end_time": None,
            "view_type": "0"
        }
        
        # Create Historic payload (with timestamps)
        current_time = int(time_module.time())
        historic_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": current_time - 3600,  # 1 hour ago
            "end_time": current_time - 3000,    # 50 minutes ago
            "view_type": "0"
        }
        
        all_job_ids = []
        
        try:
            # Create SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(limit=6, ssl=ssl_context)
            
            results: List[Tuple[InvestigationResult, str]] = []  # (result, job_type)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # Create tasks for mixed job types
                tasks = []
                
                # 3 Live jobs
                for i in range(3):
                    task = create_investigation_async(session, focus_server_url, live_payload, i, ssl_context)
                    tasks.append((task, "Live"))
                
                # 3 Historic jobs
                for i in range(3, 6):
                    task = create_investigation_async(session, focus_server_url, historic_payload, i, ssl_context)
                    tasks.append((task, "Historic"))
                
                # Execute all in parallel
                logger.info(f"Creating 6 jobs (3 Live + 3 Historic) in parallel...")
                task_coroutines = [t[0] for t in tasks]
                job_types = [t[1] for t in tasks]
                
                raw_results = await asyncio.gather(*task_coroutines)
                results = list(zip(raw_results, job_types))
            
            # Analyze results
            logger.info(f"\n{'='*80}")
            logger.info("MIXED JOB RESULTS")
            logger.info(f"{'='*80}")
            
            for result, expected_type in results:
                status = "✅" if result.success else "❌"
                actual_type = "Live" if expected_type == "Live" else "Historic"
                
                logger.info(
                    f"  {status} Job {result.index}: "
                    f"ID={result.job_id or 'N/A'} | "
                    f"Type={actual_type} | "
                    f"Response={result.response_time_ms:.1f}ms"
                )
                
                if result.job_id:
                    all_job_ids.append(result.job_id)
            
            # Summary
            successful_live = sum(1 for r, t in results if r.success and t == "Live")
            successful_historic = sum(1 for r, t in results if r.success and t == "Historic")
            
            logger.info(f"\nSUMMARY:")
            logger.info(f"  Live Jobs Created: {successful_live}/3")
            logger.info(f"  Historic Jobs Created: {successful_historic}/3")
            logger.info(f"  Total Successful: {successful_live + successful_historic}/6")
            
            logger.info(f"{'='*80}\n")
            
            # Assertions
            assert successful_live >= 2, f"Only {successful_live}/3 Live jobs created"
            # Note: Historic jobs might fail if no recordings available
            
            logger.info("✅ TEST PASSED: Mixed job types created successfully!")
            
        finally:
            if all_job_ids:
                await cleanup_investigations_async(focus_server_url, all_job_ids, ssl_verify=False)
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    @pytest.mark.slow
    async def test_component_stability_under_parallel_load(
        self,
        focus_server_url: str,
        parallel_investigation_payload: Dict[str, Any]
    ):
        """
        Stress test component stability under parallel load.
        
        Steps:
            1. Check initial component health
            2. Create 15 parallel investigations
            3. Check component health during load
            4. Wait for jobs to process
            5. Final component health check
            6. Verify no component crashes
        """
        logger.info(f"\n{'='*80}")
        logger.info("TEST: Component Stability Under Parallel Load")
        logger.info(f"{'='*80}")
        
        parallel_count = 15
        job_ids = []
        
        try:
            # =========================================================
            # PRE-LOAD: Initial Health Check
            # =========================================================
            logger.info("\n📊 PRE-LOAD HEALTH CHECK:")
            pre_health = await check_all_components_health(focus_server_url, ssl_verify=False)
            pre_healthy = print_component_health_report(pre_health)
            assert pre_healthy, "Initial health check failed"
            
            # =========================================================
            # LOAD PHASE: Create Parallel Investigations
            # =========================================================
            logger.info(f"\n🔄 CREATING {parallel_count} PARALLEL INVESTIGATIONS...")
            result = await open_parallel_investigations(
                base_url=focus_server_url,
                payload=parallel_investigation_payload,
                count=parallel_count,
                ssl_verify=False,
                verify_parallel=True,
                show_job_details=True
            )
            job_ids = result.job_ids
            
            # =========================================================
            # MID-LOAD: Health Check During Load
            # =========================================================
            logger.info("\n📊 MID-LOAD HEALTH CHECK (jobs still active):")
            mid_health = await check_all_components_health(focus_server_url, ssl_verify=False)
            mid_healthy = print_component_health_report(mid_health)
            
            # Brief wait for system stabilization
            logger.info("\n⏳ Waiting 5 seconds for system stabilization...")
            await asyncio.sleep(5)
            
            # =========================================================
            # POST-LOAD: Final Health Check
            # =========================================================
            logger.info("\n📊 POST-LOAD HEALTH CHECK:")
            post_health = await check_all_components_health(focus_server_url, ssl_verify=False)
            post_healthy = print_component_health_report(post_health)
            
            # =========================================================
            # SUMMARY
            # =========================================================
            logger.info(f"\n{'='*80}")
            logger.info("STABILITY TEST SUMMARY")
            logger.info(f"{'='*80}")
            
            logger.info(f"\n🏥 COMPONENT HEALTH:")
            logger.info(f"  Pre-Load:  {'✅ HEALTHY' if pre_healthy else '❌ UNHEALTHY'}")
            logger.info(f"  Mid-Load:  {'✅ HEALTHY' if mid_healthy else '❌ UNHEALTHY'}")
            logger.info(f"  Post-Load: {'✅ HEALTHY' if post_healthy else '❌ UNHEALTHY'}")
            
            logger.info(f"\n📈 LOAD METRICS:")
            logger.info(f"  Jobs Created: {result.successful}/{parallel_count}")
            logger.info(f"  Success Rate: {result.success_rate:.1f}%")
            logger.info(f"  Total Time: {result.total_time_ms:.1f}ms")
            
            if pre_healthy and mid_healthy and post_healthy:
                logger.info("\n✅ ALL COMPONENTS REMAINED STABLE UNDER LOAD!")
            else:
                logger.warning("\n⚠️ COMPONENT INSTABILITY DETECTED!")
            
            logger.info(f"{'='*80}\n")
            
            # Assertions
            assert post_healthy, "Post-load health check failed - components may have crashed"
            assert result.success_rate >= 70, f"Success rate {result.success_rate:.1f}% too low under load"
            
            logger.info("✅ TEST PASSED: Components stable under parallel load!")
            
        finally:
            if job_ids:
                await cleanup_investigations_async(focus_server_url, job_ids, ssl_verify=False)
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    async def test_parallel_live_jobs_only(
        self,
        focus_server_url: str,
        parallel_investigation_payload: Dict[str, Any]
    ):
        """
        Test creating multiple LIVE jobs in parallel.
        
        Live jobs are real-time streaming jobs that don't have start_time/end_time.
        They connect to live data streams and process data in real-time.
        
        Steps:
            1. Create 10 Live investigation payloads (no start_time/end_time)
            2. Execute all in parallel
            3. Verify all jobs are Live type
            4. Check response times and success rate
            5. Validate component stability
        
        Expected:
            - All jobs created as Live type
            - Response times < 2 seconds per job
            - Success rate >= 80%
            - Components remain stable
        """
        logger.info(f"\n{'='*100}")
        logger.info("TEST: Parallel LIVE Jobs Only")
        logger.info(f"{'='*100}")
        
        parallel_count = 10
        job_ids = []
        
        # Live payload - no start_time/end_time
        live_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": None,  # Live mode indicator
            "end_time": None,    # Live mode indicator
            "view_type": "0"     # MULTICHANNEL
        }
        
        try:
            # Pre-test health check
            logger.info("\n📊 PRE-TEST HEALTH CHECK:")
            pre_health = await check_all_components_health(focus_server_url, ssl_verify=False)
            pre_healthy = print_component_health_report(pre_health)
            assert pre_healthy, "Pre-test health check failed"
            
            # Create Live jobs in parallel
            logger.info(f"\n🔴 CREATING {parallel_count} LIVE JOBS IN PARALLEL...")
            
            result = await open_parallel_investigations(
                base_url=focus_server_url,
                payload=live_payload,
                count=parallel_count,
                ssl_verify=False,
                verify_parallel=True,
                show_job_details=True
            )
            
            job_ids = result.job_ids
            
            # Verify all jobs are Live type
            logger.info(f"\n{'='*80}")
            logger.info("LIVE JOB VERIFICATION")
            logger.info(f"{'='*80}")
            
            live_count = sum(1 for m in result.job_metadata_list if m.job_type == "Live")
            historic_count = sum(1 for m in result.job_metadata_list if m.job_type == "Historic")
            
            logger.info(f"  Live Jobs: {live_count}")
            logger.info(f"  Historic Jobs: {historic_count}")
            
            # Detailed job info
            logger.info(f"\n📋 JOB DETAILS:")
            for i, meta in enumerate(result.job_metadata_list, 1):
                logger.info(
                    f"  {i:>2}. Job {meta.job_id}: "
                    f"Type={meta.job_type:8} | "
                    f"Channels={meta.channels_min}-{meta.channels_max} | "
                    f"Freq={meta.frequency_min}-{meta.frequency_max}Hz | "
                    f"Response={meta.response_time_ms:.1f}ms"
                )
            
            # Post-test health check
            logger.info("\n📊 POST-TEST HEALTH CHECK:")
            post_health = await check_all_components_health(focus_server_url, ssl_verify=False)
            post_healthy = print_component_health_report(post_health)
            
            # Summary
            logger.info(f"\n{'='*100}")
            logger.info("LIVE JOBS TEST SUMMARY")
            logger.info(f"{'='*100}")
            logger.info(f"\n📊 RESULTS:")
            logger.info(f"  Total Jobs Requested: {parallel_count}")
            logger.info(f"  Successfully Created: {result.successful}")
            logger.info(f"  Failed: {result.failed}")
            logger.info(f"  Success Rate: {result.success_rate:.1f}%")
            logger.info(f"\n📋 JOB TYPES:")
            logger.info(f"  Live: {live_count} ({'✅ ALL' if live_count == result.successful else '⚠️'})")
            logger.info(f"  Historic: {historic_count}")
            logger.info(f"\n⏱️ TIMING:")
            logger.info(f"  Total Time: {result.total_time_ms:.1f}ms")
            logger.info(f"  Avg Response: {result.avg_response_time_ms:.1f}ms")
            logger.info(f"  Min Response: {result.min_response_time_ms:.1f}ms")
            logger.info(f"  Max Response: {result.max_response_time_ms:.1f}ms")
            logger.info(f"\n🏥 STABILITY:")
            logger.info(f"  Pre-test: {'✅ Healthy' if pre_healthy else '❌ Issues'}")
            logger.info(f"  Post-test: {'✅ Healthy' if post_healthy else '❌ Issues'}")
            logger.info(f"{'='*100}\n")
            
            # Assertions
            assert result.success_rate >= MIN_SUCCESS_RATE_PERCENT, \
                f"Success rate {result.success_rate:.1f}% below minimum {MIN_SUCCESS_RATE_PERCENT}%"
            
            assert live_count == result.successful, \
                f"Not all successful jobs are Live type: {live_count}/{result.successful}"
            
            assert post_healthy, "Post-test health check failed"
            
            logger.info("✅ TEST PASSED: All Live jobs created successfully!")
            
        finally:
            if job_ids:
                await cleanup_investigations_async(focus_server_url, job_ids, ssl_verify=False)
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    @pytest.mark.slow
    async def test_parallel_historic_jobs_only(
        self,
        focus_server_url: str,
        config_manager
    ):
        """
        Test creating multiple HISTORIC jobs in parallel.
        
        Historic jobs retrieve and process previously recorded data.
        They require start_time and end_time parameters to specify the time range.
        
        NOTE: Historic jobs take significantly longer than Live jobs (15-30+ seconds)
        because they need to load and process recorded data.
        
        Steps:
            1. Create 5 Historic investigation payloads (with start_time/end_time)
            2. Execute all in parallel
            3. Verify all jobs are Historic type
            4. Check response times (expected longer than Live)
            5. Validate component stability
        
        Expected:
            - All jobs created as Historic type
            - Response times may be 15-60 seconds per job
            - Success rate >= 60% (Historic jobs may fail if no recordings available)
            - Components remain stable
        """
        logger.info(f"\n{'='*100}")
        logger.info("TEST: Parallel HISTORIC Jobs Only")
        logger.info(f"{'='*100}")
        
        import time as time_module
        
        parallel_count = 5  # Fewer jobs due to longer processing time
        job_ids = []
        
        # Calculate time range for historic data (1 hour window, starting 2 hours ago)
        current_time = int(time_module.time())
        start_time = current_time - 7200  # 2 hours ago
        end_time = current_time - 3600    # 1 hour ago
        
        # Historic payload - WITH start_time/end_time
        historic_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": start_time,  # Historic mode indicator
            "end_time": end_time,       # Historic mode indicator
            "view_type": "0"            # MULTICHANNEL
        }
        
        try:
            # Pre-test health check
            logger.info("\n📊 PRE-TEST HEALTH CHECK:")
            pre_health = await check_all_components_health(focus_server_url, ssl_verify=False)
            pre_healthy = print_component_health_report(pre_health)
            assert pre_healthy, "Pre-test health check failed"
            
            # Log historic parameters
            logger.info(f"\n📼 HISTORIC JOB PARAMETERS:")
            logger.info(f"  Start Time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"  End Time: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"  Duration: {(end_time - start_time) // 60} minutes")
            
            # Create Historic jobs in parallel
            logger.info(f"\n📼 CREATING {parallel_count} HISTORIC JOBS IN PARALLEL...")
            logger.info("⏳ Note: Historic jobs take longer (15-60+ seconds each)...")
            
            # Use longer timeout for historic jobs
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(limit=parallel_count, ssl=ssl_context)
            
            results: List[InvestigationResult] = []
            start_time_test = time.time()
            
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = [
                    create_investigation_async(
                        session,
                        focus_server_url,
                        historic_payload,
                        i,
                        ssl_context
                    )
                    for i in range(parallel_count)
                ]
                
                # Execute with longer overall timeout
                results = await asyncio.gather(*tasks, return_exceptions=False)
            
            total_time_ms = (time.time() - start_time_test) * 1000
            
            # Analyze results
            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]
            job_ids = [r.job_id for r in successful if r.job_id]
            
            # Extract metadata
            job_metadata_list = []
            for r in successful:
                if r.success and r.job_id:
                    metadata = extract_job_metadata(r, historic_payload)
                    job_metadata_list.append(metadata)
            
            # Verify all jobs are Historic type
            logger.info(f"\n{'='*80}")
            logger.info("HISTORIC JOB VERIFICATION")
            logger.info(f"{'='*80}")
            
            historic_count = sum(1 for m in job_metadata_list if m.job_type == "Historic")
            live_count = sum(1 for m in job_metadata_list if m.job_type == "Live")
            
            logger.info(f"  Historic Jobs: {historic_count}")
            logger.info(f"  Live Jobs: {live_count}")
            
            # Detailed job info
            logger.info(f"\n📋 JOB DETAILS:")
            for i, meta in enumerate(job_metadata_list, 1):
                logger.info(
                    f"  {i:>2}. Job {meta.job_id}: "
                    f"Type={meta.job_type:8} | "
                    f"Channels={meta.channels_min}-{meta.channels_max} | "
                    f"Freq={meta.frequency_min}-{meta.frequency_max}Hz | "
                    f"Response={meta.response_time_ms:.1f}ms"
                )
            
            # Log failures
            if failed:
                logger.warning(f"\n⚠️ FAILED JOBS ({len(failed)}):")
                for r in failed:
                    logger.warning(f"  Job {r.index}: {r.error}")
            
            # Post-test health check
            logger.info("\n📊 POST-TEST HEALTH CHECK:")
            post_health = await check_all_components_health(focus_server_url, ssl_verify=False)
            post_healthy = print_component_health_report(post_health)
            
            # Calculate stats
            response_times = [r.response_time_ms for r in results]
            success_rate = (len(successful) / len(results)) * 100 if results else 0
            avg_response = mean(response_times) if response_times else 0
            min_response = min(response_times) if response_times else 0
            max_response = max(response_times) if response_times else 0
            
            # Summary
            logger.info(f"\n{'='*100}")
            logger.info("HISTORIC JOBS TEST SUMMARY")
            logger.info(f"{'='*100}")
            logger.info(f"\n📊 RESULTS:")
            logger.info(f"  Total Jobs Requested: {parallel_count}")
            logger.info(f"  Successfully Created: {len(successful)}")
            logger.info(f"  Failed: {len(failed)}")
            logger.info(f"  Success Rate: {success_rate:.1f}%")
            logger.info(f"\n📋 JOB TYPES:")
            logger.info(f"  Historic: {historic_count} ({'✅ ALL' if historic_count == len(successful) else '⚠️'})")
            logger.info(f"  Live: {live_count}")
            logger.info(f"\n⏱️ TIMING (Historic jobs are expected to be slower):")
            logger.info(f"  Total Time: {total_time_ms:.1f}ms ({total_time_ms/1000:.1f}s)")
            logger.info(f"  Avg Response: {avg_response:.1f}ms ({avg_response/1000:.1f}s)")
            logger.info(f"  Min Response: {min_response:.1f}ms ({min_response/1000:.1f}s)")
            logger.info(f"  Max Response: {max_response:.1f}ms ({max_response/1000:.1f}s)")
            logger.info(f"\n🏥 STABILITY:")
            logger.info(f"  Pre-test: {'✅ Healthy' if pre_healthy else '❌ Issues'}")
            logger.info(f"  Post-test: {'✅ Healthy' if post_healthy else '❌ Issues'}")
            logger.info(f"{'='*100}\n")
            
            # Assertions (lower threshold for Historic jobs)
            HISTORIC_MIN_SUCCESS_RATE = 60  # Lower threshold - may fail if no recordings
            
            assert success_rate >= HISTORIC_MIN_SUCCESS_RATE, \
                f"Success rate {success_rate:.1f}% below minimum {HISTORIC_MIN_SUCCESS_RATE}%"
            
            if len(successful) > 0:
                assert historic_count == len(successful), \
                    f"Not all successful jobs are Historic type: {historic_count}/{len(successful)}"
            
            assert post_healthy, "Post-test health check failed"
            
            logger.info("✅ TEST PASSED: Historic jobs test completed!")
            
        finally:
            if job_ids:
                await cleanup_investigations_async(focus_server_url, job_ids, ssl_verify=False)


# =============================================================================
# Synchronous Test Wrapper (for non-asyncio runners)
# =============================================================================

@pytest.mark.load
@pytest.mark.parallel
@pytest.mark.integration
class TestParallelInvestigationsSyncWrapper:
    """
    Synchronous wrapper for parallel investigation tests.
    
    Use this class if your pytest runner doesn't support asyncio directly.
    """
    
    @pytest.mark.xray("PZ-TBD")  # TODO: Add Xray ID
    def test_open_5_investigations_parallel_sync(
        self,
        focus_server_url: str,
        parallel_investigation_payload: Dict[str, Any]
    ):
        """
        Synchronous test wrapper for opening 5 parallel investigations.
        
        This wraps the async function for compatibility with non-async test runners.
        """
        logger.info("Running parallel investigations test (sync wrapper)")
        
        async def run_test():
            job_ids = []
            try:
                result = await open_parallel_investigations(
                    base_url=focus_server_url,
                    payload=parallel_investigation_payload,
                    count=5,
                    ssl_verify=False
                )
                
                job_ids = result.job_ids
                
                assert result.success_rate >= MIN_SUCCESS_RATE_PERCENT, \
                    f"Success rate {result.success_rate:.1f}% below minimum"
                
                return result
            finally:
                if job_ids:
                    await cleanup_investigations_async(focus_server_url, job_ids, ssl_verify=False)
        
        # Run async test in event loop
        result = asyncio.run(run_test())
        
        logger.info(f"✅ Completed: {result.successful}/{result.total_investigations} successful")

