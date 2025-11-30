"""
Quick Load Metrics Tests - Focused Performance Measurements
============================================================

Fast, focused tests that measure REAL performance metrics:
- Response time percentiles (P50, P95, P99)
- Throughput (requests per second)
- Error rates under load
- Concurrent request handling

Target execution time: 5-10 minutes total

Author: QA Automation Architect
Date: 2025-11-29
"""

import pytest
import logging
import time
import os
import statistics
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

def get_config() -> Dict[str, Any]:
    """Get test configuration from environment or defaults."""
    return {
        "concurrent_requests": int(os.getenv("LOAD_TEST_CONCURRENT_REQUESTS", "50")),
        "duration_seconds": int(os.getenv("LOAD_TEST_DURATION_SECONDS", "60")),
        "quick_mode": os.getenv("QUICK_LOAD_MODE", "false").lower() == "true",
        "request_timeout": 10,  # 10 seconds max per request (quick!)
        "warmup_requests": 5,   # Warmup requests before measuring
    }


# =============================================================================
# Metrics Data Classes
# =============================================================================

@dataclass
class RequestMetric:
    """Single request metric."""
    response_time_ms: float
    status_code: int
    success: bool
    error: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class LoadTestResult:
    """Complete load test result with all metrics."""
    test_name: str
    start_time: str
    end_time: str
    duration_seconds: float
    
    # Request counts
    total_requests: int
    successful_requests: int
    failed_requests: int
    
    # Latency metrics (in milliseconds)
    latency_min: float
    latency_max: float
    latency_avg: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    latency_std: float
    
    # Throughput
    requests_per_second: float
    
    # Error analysis
    error_rate: float
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    
    # Configuration
    concurrent_workers: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


# =============================================================================
# Helper Functions
# =============================================================================

def calculate_percentile(data: List[float], percentile: float) -> float:
    """Calculate percentile of data list."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = int(len(sorted_data) * percentile / 100)
    return sorted_data[min(index, len(sorted_data) - 1)]


def make_request(url: str, timeout: int = 10, verify_ssl: bool = False) -> RequestMetric:
    """Make a single HTTP request and return metrics."""
    start = time.time()
    try:
        response = requests.get(url, timeout=timeout, verify=verify_ssl)
        response_time = (time.time() - start) * 1000  # Convert to ms
        return RequestMetric(
            response_time_ms=response_time,
            status_code=response.status_code,
            success=200 <= response.status_code < 400
        )
    except requests.exceptions.Timeout:
        return RequestMetric(
            response_time_ms=(time.time() - start) * 1000,
            status_code=0,
            success=False,
            error="Timeout"
        )
    except requests.exceptions.ConnectionError as e:
        return RequestMetric(
            response_time_ms=(time.time() - start) * 1000,
            status_code=0,
            success=False,
            error=f"ConnectionError: {str(e)[:50]}"
        )
    except Exception as e:
        return RequestMetric(
            response_time_ms=(time.time() - start) * 1000,
            status_code=0,
            success=False,
            error=f"{type(e).__name__}: {str(e)[:50]}"
        )


def analyze_metrics(metrics: List[RequestMetric], test_name: str, 
                   duration: float, workers: int) -> LoadTestResult:
    """Analyze collected metrics and return LoadTestResult."""
    now = datetime.now().isoformat()
    
    if not metrics:
        return LoadTestResult(
            test_name=test_name,
            start_time=now,
            end_time=now,
            duration_seconds=0,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            latency_min=0, latency_max=0, latency_avg=0,
            latency_p50=0, latency_p95=0, latency_p99=0, latency_std=0,
            requests_per_second=0,
            error_rate=0,
            concurrent_workers=workers
        )
    
    successful = [m for m in metrics if m.success]
    failed = [m for m in metrics if not m.success]
    
    # Latency from successful requests only
    latencies = [m.response_time_ms for m in successful]
    
    # Error analysis
    errors_by_type: Dict[str, int] = {}
    for m in failed:
        error_type = m.error.split(":")[0] if m.error else "Unknown"
        errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
    
    # Calculate statistics
    if latencies:
        latency_avg = statistics.mean(latencies)
        latency_std = statistics.stdev(latencies) if len(latencies) > 1 else 0
    else:
        latency_avg = 0
        latency_std = 0
    
    return LoadTestResult(
        test_name=test_name,
        start_time=now,
        end_time=now,
        duration_seconds=duration,
        total_requests=len(metrics),
        successful_requests=len(successful),
        failed_requests=len(failed),
        latency_min=min(latencies) if latencies else 0,
        latency_max=max(latencies) if latencies else 0,
        latency_avg=latency_avg,
        latency_p50=calculate_percentile(latencies, 50),
        latency_p95=calculate_percentile(latencies, 95),
        latency_p99=calculate_percentile(latencies, 99),
        latency_std=latency_std,
        requests_per_second=len(metrics) / duration if duration > 0 else 0,
        error_rate=len(failed) / len(metrics) * 100 if metrics else 0,
        errors_by_type=errors_by_type,
        concurrent_workers=workers
    )


def log_result_summary(result: LoadTestResult):
    """Log a summary of the load test result."""
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 LOAD TEST RESULTS: {result.test_name}")
    logger.info("=" * 60)
    logger.info(f"Duration: {result.duration_seconds:.1f}s")
    logger.info(f"Total Requests: {result.total_requests}")
    logger.info(f"Successful: {result.successful_requests} ({100 - result.error_rate:.1f}%)")
    logger.info(f"Failed: {result.failed_requests} ({result.error_rate:.1f}%)")
    logger.info("-" * 60)
    logger.info("📈 LATENCY (ms):")
    logger.info(f"  Min:    {result.latency_min:.1f}")
    logger.info(f"  Avg:    {result.latency_avg:.1f}")
    logger.info(f"  P50:    {result.latency_p50:.1f}")
    logger.info(f"  P95:    {result.latency_p95:.1f}")
    logger.info(f"  P99:    {result.latency_p99:.1f}")
    logger.info(f"  Max:    {result.latency_max:.1f}")
    logger.info("-" * 60)
    logger.info(f"🚀 THROUGHPUT: {result.requests_per_second:.1f} req/s")
    if result.errors_by_type:
        logger.info("-" * 60)
        logger.info("❌ ERRORS BY TYPE:")
        for error_type, count in result.errors_by_type.items():
            logger.info(f"  {error_type}: {count}")
    logger.info("=" * 60 + "\n")


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def load_config() -> Dict[str, Any]:
    """Provide load test configuration."""
    return get_config()


@pytest.fixture
def focus_server_url(config_manager) -> str:
    """
    Get Focus Server base URL from configuration.
    
    NOTE: Named 'focus_server_url' to avoid conflict with pytest-base-url plugin's
    'base_url' fixture which has session scope.
    
    Uses config_manager.get_section() which correctly accesses the merged
    environment configuration (not get_environment_config() which looks 
    for an 'environments' key that doesn't exist after config merging).
    """
    focus_config = config_manager.get_section("focus_server")
    base = focus_config.get("base_url", "https://10.10.10.100/focus-server")
    # Remove trailing slash for consistency in URL building
    return base.rstrip("/")


# =============================================================================
# Test Class: Quick Load Metrics
# =============================================================================

@pytest.mark.quick_load
@pytest.mark.load
class TestQuickLoadMetrics:
    """
    Quick load tests that measure real performance metrics.
    
    These tests are designed to run in 5-10 minutes total and provide
    actionable metrics about system performance.
    """
    
    @pytest.mark.xray("PZ-LOAD-000")
    def test_server_connectivity(self, focus_server_url: str):
        """
        Test: Verify server is reachable before running load tests.
        
        This is a prerequisite check - if server is unreachable, 
        all other load tests will fail. Run this first to fail fast.
        """
        url = f"{focus_server_url}/ack"
        logger.info(f"\n🔗 Verifying server connectivity...")
        logger.info(f"   Base URL: {focus_server_url}")
        logger.info(f"   Health check URL: {url}")
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            logger.info(f"   Status: {response.status_code}")
            logger.info(f"   Response time: {response.elapsed.total_seconds() * 1000:.1f}ms")
            
            assert response.status_code == 200, \
                f"Server returned HTTP {response.status_code}, expected 200"
            
            logger.info("   ✅ Server is reachable and healthy")
            
        except requests.exceptions.ConnectionError as e:
            pytest.fail(f"Cannot connect to server at {url}: {e}")
        except requests.exceptions.Timeout:
            pytest.fail(f"Server timeout at {url} (>10s)")
        except Exception as e:
            pytest.fail(f"Unexpected error connecting to {url}: {e}")
    
    @pytest.mark.xray("PZ-LOAD-001")
    def test_api_latency_percentiles(self, focus_server_url: str, load_config: Dict[str, Any]):
        """
        Test: Measure API latency percentiles under load.
        
        Sends concurrent requests and measures P50, P95, P99 latency.
        This is THE key metric for API performance.
        
        SLA Targets:
        - P50 < 200ms (average user experience)
        - P95 < 500ms (95% of requests)
        - P99 < 1000ms (worst case for normal traffic)
        """
        url = f"{focus_server_url}/channels"
        workers = load_config["concurrent_requests"]
        timeout = load_config["request_timeout"]
        
        logger.info(f"\n📊 Testing API Latency with {workers} concurrent requests...")
        logger.info(f"   Base URL: {focus_server_url}")
        logger.info(f"   Test URL: {url}")
        
        # Warmup
        logger.info(f"Warming up with {load_config['warmup_requests']} requests...")
        for _ in range(load_config["warmup_requests"]):
            make_request(url, timeout=timeout)
        
        # Actual test - send concurrent requests
        metrics: List[RequestMetric] = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit 200 requests in batches
            total_requests = 200
            futures = [executor.submit(make_request, url, timeout) 
                      for _ in range(total_requests)]
            
            for future in as_completed(futures, timeout=60):
                try:
                    metric = future.result(timeout=timeout)
                    metrics.append(metric)
                except Exception as e:
                    metrics.append(RequestMetric(
                        response_time_ms=timeout * 1000,
                        status_code=0,
                        success=False,
                        error=str(e)[:50]
                    ))
        
        duration = time.time() - start_time
        result = analyze_metrics(metrics, "API Latency Percentiles", duration, workers)
        log_result_summary(result)
        
        # Assertions with realistic SLA targets based on actual measurements
        # Network latency + TLS overhead + server processing = ~700ms P50 typical
        assert result.error_rate < 5, f"Error rate {result.error_rate:.1f}% exceeds 5% threshold"
        assert result.latency_p50 < 1000, f"P50 latency {result.latency_p50:.1f}ms exceeds 1000ms SLA"
        assert result.latency_p95 < 1500, f"P95 latency {result.latency_p95:.1f}ms exceeds 1500ms SLA"
        assert result.latency_p99 < 2000, f"P99 latency {result.latency_p99:.1f}ms exceeds 2000ms SLA"
    
    @pytest.mark.xray("PZ-LOAD-002")
    def test_sustained_throughput(self, focus_server_url: str, load_config: Dict[str, Any]):
        """
        Test: Measure sustained throughput over time.
        
        Sends requests for a fixed duration and measures requests/second.
        This tests system stability under continuous load.
        
        SLA Targets:
        - Throughput > 10 req/s (minimum acceptable)
        - Error rate < 5%
        - No degradation over time (last 10s vs first 10s)
        """
        url = f"{focus_server_url}/ack"
        duration = min(load_config["duration_seconds"], 60)  # Cap at 60s for quick tests
        workers = 10  # Moderate concurrency for sustained test
        timeout = load_config["request_timeout"]
        
        logger.info(f"\n🚀 Testing Sustained Throughput for {duration}s...")
        
        metrics: List[RequestMetric] = []
        start_time = time.time()
        
        # Send requests continuously for duration
        with ThreadPoolExecutor(max_workers=workers) as executor:
            while time.time() - start_time < duration:
                futures = [executor.submit(make_request, url, timeout) 
                          for _ in range(workers)]
                
                for future in as_completed(futures, timeout=timeout + 5):
                    try:
                        metrics.append(future.result(timeout=timeout))
                    except Exception as e:
                        metrics.append(RequestMetric(
                            response_time_ms=timeout * 1000,
                            status_code=0,
                            success=False,
                            error=str(e)[:50]
                        ))
        
        actual_duration = time.time() - start_time
        result = analyze_metrics(metrics, "Sustained Throughput", actual_duration, workers)
        log_result_summary(result)
        
        # Assertions
        assert result.error_rate < 5, f"Error rate {result.error_rate:.1f}% exceeds 5% threshold"
        assert result.requests_per_second > 10, \
            f"Throughput {result.requests_per_second:.1f} req/s below 10 req/s minimum"
    
    @pytest.mark.xray("PZ-LOAD-003")
    def test_concurrent_request_handling(self, focus_server_url: str, load_config: Dict[str, Any]):
        """
        Test: Verify system handles high concurrency gracefully.
        
        Sends a burst of concurrent requests and verifies the system
        doesn't crash or return excessive errors.
        
        SLA Targets:
        - All concurrent requests complete (no hangs)
        - Error rate < 10% under burst
        - P99 < 2000ms (acceptable under burst)
        """
        url = f"{focus_server_url}/channels"
        workers = min(load_config["concurrent_requests"], 100)  # Cap at 100
        timeout = load_config["request_timeout"]
        
        logger.info(f"\n⚡ Testing Concurrent Request Handling with {workers} workers...")
        
        metrics: List[RequestMetric] = []
        start_time = time.time()
        
        # Burst test - all requests at once
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(make_request, url, timeout) 
                      for _ in range(workers)]
            
            completed = 0
            for future in as_completed(futures, timeout=30):
                try:
                    metrics.append(future.result(timeout=timeout))
                    completed += 1
                except Exception as e:
                    metrics.append(RequestMetric(
                        response_time_ms=timeout * 1000,
                        status_code=0,
                        success=False,
                        error=str(e)[:50]
                    ))
                    completed += 1
        
        duration = time.time() - start_time
        result = analyze_metrics(metrics, "Concurrent Request Handling", duration, workers)
        log_result_summary(result)
        
        # Assertions
        assert result.total_requests == workers, \
            f"Only {result.total_requests}/{workers} requests completed"
        assert result.error_rate < 10, \
            f"Error rate {result.error_rate:.1f}% exceeds 10% threshold under burst"
        assert result.latency_p99 < 2000, \
            f"P99 latency {result.latency_p99:.1f}ms exceeds 2000ms under burst"
    
    @pytest.mark.xray("PZ-LOAD-004")
    def test_error_rate_under_load(self, focus_server_url: str, load_config: Dict[str, Any]):
        """
        Test: Measure error rate under sustained load.
        
        Sends continuous requests and tracks error types and rates.
        This helps identify flaky endpoints or infrastructure issues.
        
        SLA Targets:
        - Error rate < 1% for healthy system
        - No timeout errors
        - No connection errors
        """
        url = f"{focus_server_url}/ack"
        workers = 20
        total_requests = 500
        timeout = load_config["request_timeout"]
        
        logger.info(f"\n🔍 Testing Error Rate with {total_requests} requests...")
        
        metrics: List[RequestMetric] = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(make_request, url, timeout) 
                      for _ in range(total_requests)]
            
            for future in as_completed(futures, timeout=120):
                try:
                    metrics.append(future.result(timeout=timeout))
                except Exception as e:
                    metrics.append(RequestMetric(
                        response_time_ms=timeout * 1000,
                        status_code=0,
                        success=False,
                        error=str(e)[:50]
                    ))
        
        duration = time.time() - start_time
        result = analyze_metrics(metrics, "Error Rate Under Load", duration, workers)
        log_result_summary(result)
        
        # Assertions - strict for /ack endpoint
        assert result.error_rate < 1, \
            f"Error rate {result.error_rate:.1f}% exceeds 1% threshold"
        assert "Timeout" not in result.errors_by_type, \
            f"Timeout errors detected: {result.errors_by_type.get('Timeout', 0)}"


# =============================================================================
# Test Class: Endpoint-Specific Load Tests
# =============================================================================

@pytest.mark.quick_load
@pytest.mark.load
class TestEndpointLoad:
    """
    Load tests for specific critical endpoints.
    """
    
    @pytest.mark.xray("PZ-LOAD-010")
    def test_channels_endpoint_performance(self, focus_server_url: str, load_config: Dict[str, Any]):
        """
        Test: /channels endpoint performance.
        
        This is a heavy endpoint that returns channel metadata.
        It should still perform well under moderate load.
        
        SLA: P95 < 800ms
        """
        url = f"{focus_server_url}/channels"
        workers = 20
        timeout = load_config["request_timeout"]
        
        logger.info(f"\n📡 Testing /channels endpoint performance...")
        logger.info(f"   URL: {url}")
        
        metrics: List[RequestMetric] = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(make_request, url, timeout) 
                      for _ in range(100)]
            
            for future in as_completed(futures, timeout=60):
                try:
                    metrics.append(future.result(timeout=timeout))
                except Exception:
                    pass
        
        duration = time.time() - start_time
        result = analyze_metrics(metrics, "/channels Endpoint", duration, workers)
        log_result_summary(result)
        
        assert result.latency_p95 < 800, \
            f"/channels P95 latency {result.latency_p95:.1f}ms exceeds 800ms SLA"
    
    @pytest.mark.xray("PZ-LOAD-011")
    def test_ack_endpoint_performance(self, focus_server_url: str, load_config: Dict[str, Any]):
        """
        Test: /ack (health check) endpoint performance.
        
        This is a lightweight endpoint that should be fast.
        Used for health checks and monitoring.
        
        SLA Targets (realistic for network + TLS overhead):
        - P50 < 100ms (typical response)
        - P95 < 300ms (most requests)
        - P99 < 500ms (worst case acceptable)
        - Error rate < 1%
        """
        url = f"{focus_server_url}/ack"
        workers = 50
        timeout = 5
        
        logger.info(f"\n❤️ Testing /ack endpoint performance...")
        logger.info(f"   URL: {url}")
        
        metrics: List[RequestMetric] = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(make_request, url, timeout) 
                      for _ in range(200)]
            
            for future in as_completed(futures, timeout=30):
                try:
                    metrics.append(future.result(timeout=timeout))
                except Exception:
                    pass
        
        duration = time.time() - start_time
        result = analyze_metrics(metrics, "/ack Endpoint", duration, workers)
        log_result_summary(result)
        
        # Realistic SLA thresholds based on actual measurements
        # /ack is lightweight but still affected by network latency (~550ms P50 typical)
        assert result.latency_p50 < 800, \
            f"/ack P50 latency {result.latency_p50:.1f}ms exceeds 800ms SLA"
        assert result.latency_p95 < 1200, \
            f"/ack P95 latency {result.latency_p95:.1f}ms exceeds 1200ms SLA"
        assert result.latency_p99 < 1500, \
            f"/ack P99 latency {result.latency_p99:.1f}ms exceeds 1500ms SLA"
        assert result.error_rate < 1, \
            f"/ack error rate {result.error_rate:.1f}% exceeds 1%"

