"""
Smart Load Tester - Gradual load testing with breakpoint detection.

This module provides intelligent load testing capabilities:
- Gradual load increase (step-by-step)
- Automatic breakpoint detection
- Smart stopping after consecutive failures
- Detailed logging and reporting

Author: QA Automation Architect
Date: 2025-11-29
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


class FailureType(Enum):
    """Types of failures detected during load testing."""
    RATE_LIMITED = "429_rate_limited"
    UNAUTHORIZED = "401_unauthorized"  # Auth failure - stop immediately
    CONNECTION_POOL_FULL = "connection_pool_full"
    TIMEOUT = "timeout"
    SERVER_ERROR = "5xx_server_error"
    CONNECTION_ERROR = "connection_error"
    UNKNOWN = "unknown"


@dataclass
class LoadTestResult:
    """Result of a single load test step."""
    step: int
    concurrent_requests: int
    requests_sent: int
    successful: int
    failed: int
    success_rate: float
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    failures_by_type: Dict[FailureType, int]
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_healthy(self) -> bool:
        """Check if this step's success rate is acceptable."""
        return self.success_rate >= 0.9  # 90% success rate threshold


@dataclass
class BreakpointReport:
    """Report of system breakpoint detection."""
    detected: bool
    breakpoint_step: Optional[int]
    max_healthy_load: int
    failure_type: Optional[FailureType]
    failure_count: int
    total_requests_sent: int
    total_successful: int
    total_failed: int
    timestamp: datetime
    duration_seconds: float
    steps_completed: int
    detailed_message: str
    all_step_results: List[LoadTestResult]
    request_type: str = "Unknown"  # Type of requests being tested (e.g., "Alert API", "Focus Server API")
    
    def to_log_message(self) -> str:
        """Generate detailed log message for breakpoint report."""
        lines = [
            "",
            "=" * 80,
            f"🔴 SMART LOAD TEST - BREAKPOINT REPORT [{self.request_type}]",
            "=" * 80,
            "",
            f"📊 Test Summary:",
            f"   • Request Type: {self.request_type}",
            f"   • Breakpoint Detected: {'YES ⚠️' if self.detected else 'NO ✅'}",
            f"   • Steps Completed: {self.steps_completed}",
            f"   • Total Duration: {self.duration_seconds:.2f} seconds",
            f"   • Timestamp: {self.timestamp.isoformat()}",
            "",
            f"📈 Load Statistics [{self.request_type}]:",
            f"   • Maximum Healthy Load: {self.max_healthy_load} concurrent requests",
            f"   • Total Requests Sent: {self.total_requests_sent}",
            f"   • Successful Requests: {self.total_successful}",
            f"   • Failed Requests: {self.total_failed}",
            f"   • Overall Success Rate: {(self.total_successful / max(self.total_requests_sent, 1)) * 100:.1f}%",
            "",
        ]
        
        if self.detected:
            lines.extend([
                f"⚠️  Breakpoint Details:",
                f"   • Breakpoint at Step: {self.breakpoint_step}",
                f"   • Primary Failure Type: {self.failure_type.value if self.failure_type else 'N/A'}",
                f"   • Consecutive Failures: {self.failure_count}",
                f"   • Message: {self.detailed_message}",
                "",
            ])
        
        # Add step-by-step breakdown
        lines.extend([
            "📋 Step-by-Step Results:",
            "-" * 60,
        ])
        
        for result in self.all_step_results:
            status = "✅" if result.is_healthy else "❌"
            lines.append(
                f"   Step {result.step}: {result.concurrent_requests} concurrent | "
                f"{result.success_rate * 100:.1f}% success | "
                f"Avg: {result.avg_response_time_ms:.0f}ms {status}"
            )
            if result.failures_by_type:
                failure_summary = ", ".join(
                    f"{ft.value}: {count}" 
                    for ft, count in result.failures_by_type.items() if count > 0
                )
                if failure_summary:
                    lines.append(f"            Failures: {failure_summary}")
        
        lines.extend([
            "-" * 60,
            "",
            "=" * 80,
        ])
        
        return "\n".join(lines)


class SmartLoadTester:
    """
    Smart Load Tester with gradual load increase and breakpoint detection.
    
    Features:
    - Starts with low load and gradually increases
    - Detects system breakpoints automatically
    - Stops after N consecutive failures (configurable)
    - Provides detailed breakpoint reports
    - Classifies failure types (429, connection pool, timeout, etc.)
    
    Usage:
        tester = SmartLoadTester(
            request_func=my_request_function,
            initial_concurrent=5,
            step_increment=5,
            max_concurrent=100,
            requests_per_step=20,
            max_consecutive_failures=5
        )
        
        report = tester.run()
        logger.info(report.to_log_message())
    """
    
    def __init__(
        self,
        request_func: Callable[[], bool],
        initial_concurrent: int = 5,
        step_increment: int = 5,
        max_concurrent: int = 100,
        requests_per_step: int = 20,
        max_consecutive_failures: int = 5,
        step_cooldown_seconds: float = 2.0,
        request_timeout_seconds: float = 30.0,
        request_type: str = "Unknown API"
    ):
        """
        Initialize Smart Load Tester.
        
        Args:
            request_func: Function that sends a single request. 
                         Returns True on success, raises exception on failure.
            initial_concurrent: Starting number of concurrent requests
            step_increment: How many to add each step
            max_concurrent: Maximum concurrent requests to test
            requests_per_step: How many total requests per step
            max_consecutive_failures: Stop after this many consecutive failures
            step_cooldown_seconds: Pause between steps
            request_timeout_seconds: Timeout for individual requests
            request_type: Human-readable name for the API being tested (e.g., "Alert API", "Focus Server API")
        """
        self.request_func = request_func
        self.initial_concurrent = initial_concurrent
        self.step_increment = step_increment
        self.max_concurrent = max_concurrent
        self.requests_per_step = requests_per_step
        self.max_consecutive_failures = max_consecutive_failures
        self.step_cooldown_seconds = step_cooldown_seconds
        self.request_timeout_seconds = request_timeout_seconds
        self.request_type = request_type
        
        # Tracking
        self._results: List[LoadTestResult] = []
        self._consecutive_failures: Dict[FailureType, int] = {}
        self._lock = threading.Lock()
        self._stop_requested = False
        
    def _classify_failure(self, exception: Exception) -> FailureType:
        """Classify the type of failure from exception."""
        error_str = str(exception).lower()
        
        # Auth failures should stop immediately - usually indicates wrong URL/config
        if "401" in error_str or "unauthorized" in error_str:
            return FailureType.UNAUTHORIZED
        elif "429" in error_str or "too many requests" in error_str or "rate limit" in error_str:
            return FailureType.RATE_LIMITED
        elif "connection pool" in error_str or "pool is full" in error_str:
            return FailureType.CONNECTION_POOL_FULL
        elif "timeout" in error_str or "timed out" in error_str:
            return FailureType.TIMEOUT
        elif "500" in error_str or "502" in error_str or "503" in error_str or "504" in error_str:
            return FailureType.SERVER_ERROR
        elif "connection" in error_str or "refused" in error_str:
            return FailureType.CONNECTION_ERROR
        else:
            return FailureType.UNKNOWN
    
    def _execute_single_request(self) -> tuple[bool, float, Optional[FailureType]]:
        """
        Execute a single request and measure response time.
        
        Returns:
            Tuple of (success, response_time_ms, failure_type)
        """
        start_time = time.time()
        try:
            result = self.request_func()
            response_time = (time.time() - start_time) * 1000
            return (True, response_time, None)
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            failure_type = self._classify_failure(e)
            return (False, response_time, failure_type)
    
    def _run_step(self, step: int, concurrent: int) -> LoadTestResult:
        """Run a single load test step with circuit breaker protection."""
        logger.info(f"📈 [{self.request_type}] Step {step}: Testing with {concurrent} concurrent requests...")
        
        successes = 0
        failures = 0
        response_times: List[float] = []
        failures_by_type: Dict[FailureType, int] = {ft: 0 for ft in FailureType}
        
        # Circuit breaker: Track consecutive failures within this step
        consecutive_failures_in_batch = 0
        circuit_breaker_threshold = 10  # Stop batch after 10 consecutive failures
        
        # Calculate batches
        num_batches = (self.requests_per_step + concurrent - 1) // concurrent
        
        for batch_num in range(num_batches):
            if self._stop_requested:
                break
            
            # Circuit breaker: If too many consecutive failures in this step, abort early
            if consecutive_failures_in_batch >= circuit_breaker_threshold:
                logger.warning(f"⚡ [{self.request_type}] Circuit breaker triggered: {consecutive_failures_in_batch} consecutive failures in batch")
                # Mark remaining requests as failures of the most common type
                remaining_requests = self.requests_per_step - (successes + failures)
                if remaining_requests > 0:
                    most_common_failure = max(failures_by_type.items(), key=lambda x: x[1], default=(FailureType.UNKNOWN, 0))[0]
                    failures += remaining_requests
                    failures_by_type[most_common_failure] += remaining_requests
                break
                
            batch_size = min(concurrent, self.requests_per_step - batch_num * concurrent)
            if batch_size <= 0:
                break
            
            # Execute batch concurrently
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = [
                    executor.submit(self._execute_single_request) 
                    for _ in range(batch_size)
                ]
                
                # Use try/except to handle TimeoutError from as_completed
                # This ensures all futures are processed even if some timeout
                try:
                    for future in as_completed(futures, timeout=self.request_timeout_seconds * 2):
                        try:
                            success, response_time, failure_type = future.result(timeout=self.request_timeout_seconds)
                            response_times.append(response_time)
                            
                            if success:
                                successes += 1
                                consecutive_failures_in_batch = 0  # Reset on success
                            else:
                                failures += 1
                                consecutive_failures_in_batch += 1
                                if failure_type:
                                    failures_by_type[failure_type] += 1
                        except TimeoutError:
                            # Individual request timed out
                            failures += 1
                            consecutive_failures_in_batch += 1
                            failures_by_type[FailureType.TIMEOUT] += 1
                        except Exception as e:
                            failures += 1
                            consecutive_failures_in_batch += 1
                            failure_type = self._classify_failure(e)
                            failures_by_type[failure_type] += 1
                except TimeoutError:
                    # Batch iteration timed out - count remaining futures as failures
                    remaining = sum(1 for f in futures if not f.done())
                    failures += remaining
                    consecutive_failures_in_batch += remaining
                    failures_by_type[FailureType.TIMEOUT] += remaining
                    logger.warning(f"Batch timeout: {remaining} requests did not complete")
        
        # Calculate statistics
        total_requests = successes + failures
        success_rate = successes / max(total_requests, 1)
        
        avg_response = mean(response_times) if response_times else 0
        min_response = min(response_times) if response_times else 0
        max_response = max(response_times) if response_times else 0
        
        result = LoadTestResult(
            step=step,
            concurrent_requests=concurrent,
            requests_sent=total_requests,
            successful=successes,
            failed=failures,
            success_rate=success_rate,
            avg_response_time_ms=avg_response,
            min_response_time_ms=min_response,
            max_response_time_ms=max_response,
            failures_by_type={k: v for k, v in failures_by_type.items() if v > 0}
        )
        
        # Log step result
        status = "✅" if result.is_healthy else "⚠️"
        logger.info(
            f"   {status} [{self.request_type}] Step {step} complete: {successes}/{total_requests} successful "
            f"({success_rate * 100:.1f}%), Avg: {avg_response:.0f}ms"
        )
        
        if result.failures_by_type:
            logger.info(f"      [{self.request_type}] Failures: {dict(result.failures_by_type)}")
        
        return result
    
    def _check_breakpoint(self, result: LoadTestResult) -> tuple[bool, Optional[FailureType], str]:
        """
        Check if we've hit a breakpoint based on consecutive failures.
        
        Special handling:
        - 401 Unauthorized: Immediate breakpoint (configuration error)
        - 429 Rate Limited: After max_consecutive_failures steps
        - Other errors: After max_consecutive_failures steps
        
        Returns:
            Tuple of (is_breakpoint, failure_type, message)
        """
        # Update consecutive failure counts
        for failure_type, count in result.failures_by_type.items():
            if count > 0:
                self._consecutive_failures[failure_type] = \
                    self._consecutive_failures.get(failure_type, 0) + 1
            else:
                self._consecutive_failures[failure_type] = 0
        
        # IMMEDIATE BREAKPOINT: 401 Unauthorized errors indicate config problem
        # No point in retrying - stop immediately
        if FailureType.UNAUTHORIZED in result.failures_by_type:
            auth_failures = result.failures_by_type.get(FailureType.UNAUTHORIZED, 0)
            if auth_failures > 0:
                message = (
                    f"⛔ IMMEDIATE BREAKPOINT: {auth_failures} Unauthorized (401) errors detected! "
                    f"This usually means wrong URL or authentication issue. "
                    f"Check frontend_url configuration."
                )
                return (True, FailureType.UNAUTHORIZED, message)
        
        # Reset counts for successful step
        if result.is_healthy:
            self._consecutive_failures = {}
            return (False, None, "")
        
        # Check if any failure type exceeded threshold
        for failure_type, consecutive in self._consecutive_failures.items():
            if consecutive >= self.max_consecutive_failures:
                message = (
                    f"Breakpoint detected! {consecutive} consecutive steps with "
                    f"{failure_type.value} failures. System capacity reached at "
                    f"{result.concurrent_requests} concurrent requests."
                )
                return (True, failure_type, message)
        
        return (False, None, "")
    
    def run(self) -> BreakpointReport:
        """
        Run the smart load test.
        
        Returns:
            BreakpointReport with full details of the test
        """
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"🚀 SMART LOAD TEST [{self.request_type}] - Starting gradual load test...")
        logger.info("=" * 80)
        logger.info(f"   Request Type: {self.request_type}")
        logger.info(f"   Initial concurrent: {self.initial_concurrent}")
        logger.info(f"   Step increment: {self.step_increment}")
        logger.info(f"   Max concurrent: {self.max_concurrent}")
        logger.info(f"   Requests per step: {self.requests_per_step}")
        logger.info(f"   Max consecutive failures: {self.max_consecutive_failures}")
        logger.info("=" * 80)
        logger.info("")
        
        start_time = datetime.now()
        start_timestamp = time.time()
        
        step = 0
        current_concurrent = self.initial_concurrent
        max_healthy_load = 0
        breakpoint_detected = False
        breakpoint_failure_type = None
        breakpoint_message = ""
        
        self._results = []
        self._consecutive_failures = {}
        self._stop_requested = False
        
        while current_concurrent <= self.max_concurrent and not self._stop_requested:
            step += 1
            
            # Run the step
            result = self._run_step(step, current_concurrent)
            self._results.append(result)
            
            # Track max healthy load
            if result.is_healthy:
                max_healthy_load = current_concurrent
            
            # Check for breakpoint
            is_breakpoint, failure_type, message = self._check_breakpoint(result)
            
            if is_breakpoint:
                breakpoint_detected = True
                breakpoint_failure_type = failure_type
                breakpoint_message = message
                logger.warning(f"🔴 {message}")
                logger.info("   Stopping load test - breakpoint reached")
                break
            
            # Prepare for next step
            current_concurrent += self.step_increment
            
            # Cooldown between steps
            if current_concurrent <= self.max_concurrent:
                logger.info(f"   💤 Cooling down for {self.step_cooldown_seconds}s...")
                time.sleep(self.step_cooldown_seconds)
        
        # Calculate totals
        total_requests = sum(r.requests_sent for r in self._results)
        total_successful = sum(r.successful for r in self._results)
        total_failed = sum(r.failed for r in self._results)
        duration = time.time() - start_timestamp
        
        # Determine overall failure type count
        total_failures_count = 0
        if breakpoint_failure_type:
            total_failures_count = self._consecutive_failures.get(breakpoint_failure_type, 0)
        
        # Create report
        report = BreakpointReport(
            detected=breakpoint_detected,
            breakpoint_step=step if breakpoint_detected else None,
            max_healthy_load=max_healthy_load,
            failure_type=breakpoint_failure_type,
            failure_count=total_failures_count,
            total_requests_sent=total_requests,
            total_successful=total_successful,
            total_failed=total_failed,
            timestamp=start_time,
            duration_seconds=duration,
            steps_completed=step,
            detailed_message=breakpoint_message if breakpoint_detected else "Load test completed successfully",
            all_step_results=self._results,
            request_type=self.request_type
        )
        
        # Log the full report
        logger.info(report.to_log_message())
        
        return report
    
    def stop(self):
        """Request the load test to stop gracefully."""
        self._stop_requested = True


class AlertLoadTester(SmartLoadTester):
    """
    Specialized Smart Load Tester for Alert API testing.
    
    Usage:
        tester = AlertLoadTester(
            config_manager=config_manager,
            session=authenticated_session,
            initial_concurrent=5,
            max_concurrent=100
        )
        
        report = tester.run()
    """
    
    def __init__(
        self,
        config_manager,
        session,
        initial_concurrent: int = 5,
        step_increment: int = 5,
        max_concurrent: int = 100,
        requests_per_step: int = 20,
        max_consecutive_failures: int = 3,  # Reduced from 5 - fail faster
        alert_class_id: int = 104,
        alert_severity: int = 2
    ):
        """
        Initialize Alert Load Tester.
        
        Args:
            config_manager: Configuration manager instance
            session: Authenticated requests session
            initial_concurrent: Starting concurrent requests
            step_increment: Increment per step
            max_concurrent: Maximum concurrent to test
            requests_per_step: Requests per step
            max_consecutive_failures: Stop threshold (default: 3 for faster detection)
            alert_class_id: Alert class ID (103=SC, 104=SD)
            alert_severity: Alert severity (1, 2, 3)
        """
        self.config_manager = config_manager
        self.session = session
        self.alert_class_id = alert_class_id
        self.alert_severity = alert_severity
        self._alert_counter = 0
        self._counter_lock = threading.Lock()
        
        # Build correct API URL for alerts
        # Use frontend_url (via ingress) NOT frontend_api_url (NodePort - may not be accessible)
        api_config = config_manager.get("focus_server", {})
        site_id = api_config.get("site_id", "prisma-210-1000")
        
        # Try frontend_url first (accessible via ingress), then fallback
        base_url = api_config.get("frontend_url", "https://10.10.10.100/liveView")
        
        # Convert frontend URL to API URL
        # https://10.10.10.100/liveView -> https://10.10.10.100/prisma/api/{site_id}/api/push-to-rabbit
        if "/liveView" in base_url:
            base_url = base_url.replace("/liveView", "")
        base_url = base_url.rstrip("/")
        
        self.alert_url = f"{base_url}/prisma/api/{site_id}/api/push-to-rabbit"
        logger.debug(f"AlertLoadTester initialized with URL: {self.alert_url}")
        
        # Initialize parent with our request function
        super().__init__(
            request_func=self._send_alert,
            initial_concurrent=initial_concurrent,
            step_increment=step_increment,
            max_concurrent=max_concurrent,
            requests_per_step=requests_per_step,
            max_consecutive_failures=max_consecutive_failures,
            request_type="Alert API (push-to-rabbit)"  # Clear identification of request type
        )
    
    def _send_alert(self) -> bool:
        """Send a single alert request."""
        with self._counter_lock:
            self._alert_counter += 1
            counter = self._alert_counter
        
        alert_payload = {
            "alertsAmount": 1,
            "dofM": 1000 + (counter % 2000),
            "classId": self.alert_class_id,
            "severity": self.alert_severity,
            "alertIds": [f"smart-load-{counter}-{int(time.time() * 1000)}"]
        }
        
        response = self.session.post(
            self.alert_url, 
            json=alert_payload, 
            timeout=15
        )
        response.raise_for_status()
        return True

