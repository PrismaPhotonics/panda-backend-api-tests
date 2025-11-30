"""
Quick Load Metrics Tests - Focused Performance Measurements
============================================================

Fast, focused tests that measure REAL performance metrics:
- Response time percentiles (P50, P95, P99)
- Throughput (requests per second)
- Error rates under load
- Concurrent request handling

Target execution time: 5-10 minutes total

NOTE: SLA thresholds are environment-dependent.
- Production: Strict SLAs (fast response required)
- Staging: Lenient SLAs (accounts for weaker infrastructure)

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
# Environment-based SLA Configuration
# =============================================================================

def get_environment() -> str:
    """Get current environment from env var."""
    return os.getenv("ENVIRONMENT", "staging").lower()


def get_sla_config() -> Dict[str, Any]:
    """
    Get SLA thresholds based on environment.
    
    Production: Strict SLAs - system must perform well
    Staging: Lenient SLAs - weaker infrastructure, VPN latency, etc.
    """
    env = get_environment()
    
    if env in ("prod", "production"):
        return {
            "description": "Production SLA - Strict",
            # /channels endpoint (returns ~2300 channels, heavy)
            "channels_p50": 500,
            "channels_p95": 1000,
            "channels_p99": 1500,
            "channels_error_rate": 1,
            # /ack endpoint (lightweight health check)
            "ack_p50": 200,
            "ack_p95": 500,
            "ack_p99": 800,
            "ack_error_rate": 0.5,
            # General API
            "api_p50": 500,
            "api_p95": 1000,
            "api_p99": 1500,
            "api_error_rate": 1,
            # Load test thresholds
            "error_rate_threshold": 1,
            "burst_error_rate": 5,
            "min_throughput": 20,
        }
    else:
        # Staging - more lenient
        return {
            "description": f"Staging SLA - Lenient ({env})",
            # /channels endpoint
            "channels_p50": 3000,
            "channels_p95": 5000,
            "channels_p99": 8000,
            "channels_error_rate": 15,
            # /ack endpoint
            "ack_p50": 1000,
            "ack_p95": 3000,
            "ack_p99": 5000,
            "ack_error_rate": 5,
            # General API
            "api_p50": 2000,
            "api_p95": 4000,
            "api_p99": 6000,
            "api_error_rate": 10,
            # Load test thresholds
            "error_rate_threshold": 5,
            "burst_error_rate": 15,
            "min_throughput": 5,
        }


# =============================================================================
# Test Configuration
# =============================================================================

def get_config() -> Dict[str, Any]:
    """Get test configuration from environment or defaults."""
    return {
        "concurrent_requests": int(os.getenv("LOAD_TEST_CONCURRENT_REQUESTS", "50")),
        "duration_seconds": int(os.getenv("LOAD_TEST_DURATION_SECONDS", "60")),
        "quick_mode": os.getenv("QUICK_LOAD_MODE", "false").lower() == "true",
        "request_timeout": 10,  # 10 seconds max per request
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
    sla = get_sla_config()
    env = get_environment()
    
    logger.info("\n" + "=" * 60)
    logger.info(f"LOAD TEST RESULTS: {result.test_name}")
    logger.info(f"Environment: {env.upper()} ({sla['description']})")
    logger.info("=" * 60)
    logger.info(f"Duration: {result.duration_seconds:.1f}s")
    logger.info(f"Total Requests: {result.total_requests}")
    logger.info(f"Successful: {result.successful_requests} ({100 - result.error_rate:.1f}%)")
    logger.info(f"Failed: {result.failed_requests} ({result.error_rate:.1f}%)")
    logger.info("-" * 60)
    logger.info("LATENCY (ms):")
    logger.info(f"  Min:    {result.latency_min:.1f}")
    logger.info(f"  Avg:    {result.latency_avg:.1f}")
    logger.info(f"  P50:    {result.latency_p50:.1f}")
    logger.info(f"  P95:    {result.latency_p95:.1f}")
    logger.info(f"  P99:    {result.latency_p99:.1f}")
    logger.info(f"  Max:    {result.latency_max:.1f}")
    logger.info("-" * 60)
    logger.info(f"THROUGHPUT: {result.requests_per_second:.1f} req/s")
    if result.errors_by_type:
        logger.info("-" * 60)
        logger.info("ERRORS BY TYPE:")
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
def sla_config() -> Dict[str, Any]:
    """Provide SLA configuration based on environment."""
    return get_sla_config()


@pytest.fixture
def focus_server_url(config_manager) -> str:
    """
    Get Focus Server base URL from configuration.
    
    NOTE: Named 'focus_server_url' to avoid conflict with pytest-base-url plugin's
    'base_url' fixture which has session scope.
    """
    focus_config = config_manager.get_section("focus_server")
    base = focus_config.get("base_url", "https://10.10.10.100/focus-server")
    return base.rstrip("/")


# =============================================================================
# Test Class: Quick Load Metrics
# =============================================================================

@pytest.mark.quick_load
@pytest.mark.load
class TestQuickLoadMetrics:
    """
    Quick load tests that measure real performance metrics.
    
    SLA thresholds are environment-dependent:
    - Production: Strict (system must be fast)
    - Staging: Lenient (accounts for weak infrastructure)
    """
    
    @pytest.mark.xray("PZ-LOAD-000")
    def test_server_connectivity(self, focus_server_url: str, sla_config: Dict[str, Any]):
        """
        Test: Verify server is reachable before running load tests.
        """
        url = f"{focus_server_url}/ack"
        env = get_environment()
        
        logger.info(f"\n[*] Verifying server connectivity...")
        logger.info(f"    Environment: {env.upper()}")
        logger.info(f"    Base URL: {focus_server_url}")
        logger.info(f"    Health check URL: {url}")
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            logger.info(f"    Status: {response.status_code}")
            logger.info(f"    Response time: {response.elapsed.total_seconds() * 1000:.1f}ms")
            
            assert response.status_code == 200, \
                f"Server returned HTTP {response.status_code}, expected 200"
            
            logger.info("    [+] Server is reachable and healthy")
            
        except requests.exceptions.ConnectionError as e:
            pytest.fail(f"Cannot connect to server at {url}: {e}")
        except requests.exceptions.Timeout:
            pytest.fail(f"Server timeout at {url} (>10s)")
        except Exception as e:
            pytest.fail(f"Unexpected error connecting to {url}: {e}")
    
    @pytest.mark.xray("PZ-LOAD-001")
    def test_api_latency_percentiles(self, focus_server_url: str, load_config: Dict[str, Any], 
                                     sla_config: Dict[str, Any]):
        """
        Test: Measure API latency percentiles under load.
        
        SLA Targets (environment-dependent):
        - Production: P50<500ms, P95<1000ms, P99<1500ms
        - Staging: P50<2000ms, P95<4000ms, P99<6000ms
        """
        url = f"{focus_server_url}/channels"
        workers = load_config["concurrent_requests"]
        timeout = load_config["request_timeout"]
        env = get_environment()
        
        logger.info(f"\n[*] Testing API Latency with {workers} concurrent requests...")
        logger.info(f"    Environment: {env.upper()} - {sla_config['description']}")
        logger.info(f"    Base URL: {focus_server_url}")
        logger.info(f"    Test URL: {url}")
        
        # Warmup
        logger.info(f"    Warming up with {load_config['warmup_requests']} requests...")
        for _ in range(load_config["warmup_requests"]):
            make_request(url, timeout=timeout)
        
        # Actual test
        metrics: List[RequestMetric] = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            total_requests = 200
            futures = [executor.submit(make_request, url, timeout) 
                      for _ in range(total_requests)]
            
            for future in as_completed(futures, timeout=120):
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
        
        # Environment-specific SLA assertions
        assert result.error_rate < sla_config['api_error_rate'], \
            f"Error rate {result.error_rate:.1f}% exceeds {sla_config['api_error_rate']}% threshold ({env})"
        assert result.latency_p50 < sla_config['api_p50'], \
            f"P50 latency {result.latency_p50:.1f}ms exceeds {sla_config['api_p50']}ms SLA ({env})"
        assert result.latency_p95 < sla_config['api_p95'], \
            f"P95 latency {result.latency_p95:.1f}ms exceeds {sla_config['api_p95']}ms SLA ({env})"
        assert result.latency_p99 < sla_config['api_p99'], \
            f"P99 latency {result.latency_p99:.1f}ms exceeds {sla_config['api_p99']}ms SLA ({env})"
    
    @pytest.mark.xray("PZ-LOAD-002")
    def test_sustained_throughput(self, focus_server_url: str, load_config: Dict[str, Any],
                                  sla_config: Dict[str, Any]):
        """
        Test: Measure sustained throughput over time.
        """
        url = f"{focus_server_url}/ack"
        duration = min(load_config["duration_seconds"], 60)
        workers = 10
        timeout = load_config["request_timeout"]
        env = get_environment()
        
        logger.info(f"\n[*] Testing Sustained Throughput for {duration}s...")
        logger.info(f"    Environment: {env.upper()}")
        
        metrics: List[RequestMetric] = []
        start_time = time.time()
        
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
        assert result.error_rate < sla_config['error_rate_threshold'], \
            f"Error rate {result.error_rate:.1f}% exceeds {sla_config['error_rate_threshold']}% ({env})"
        assert result.requests_per_second > sla_config['min_throughput'], \
            f"Throughput {result.requests_per_second:.1f} req/s below {sla_config['min_throughput']} ({env})"
    
    @pytest.mark.xray("PZ-LOAD-003")
    def test_concurrent_request_handling(self, focus_server_url: str, load_config: Dict[str, Any],
                                         sla_config: Dict[str, Any]):
        """
        Test: Verify system handles high concurrency gracefully.
        """
        url = f"{focus_server_url}/channels"
        workers = min(load_config["concurrent_requests"], 100)
        timeout = load_config["request_timeout"]
        env = get_environment()
        
        logger.info(f"\n[*] Testing Concurrent Request Handling with {workers} workers...")
        logger.info(f"    Environment: {env.upper()}")
        
        metrics: List[RequestMetric] = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(make_request, url, timeout) 
                      for _ in range(workers)]
            
            completed = 0
            for future in as_completed(futures, timeout=60):
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
        assert result.error_rate < sla_config['burst_error_rate'], \
            f"Error rate {result.error_rate:.1f}% exceeds {sla_config['burst_error_rate']}% under burst ({env})"
        assert result.latency_p99 < sla_config['api_p99'], \
            f"P99 latency {result.latency_p99:.1f}ms exceeds {sla_config['api_p99']}ms under burst ({env})"
    
    @pytest.mark.xray("PZ-LOAD-004")
    def test_error_rate_under_load(self, focus_server_url: str, load_config: Dict[str, Any],
                                   sla_config: Dict[str, Any]):
        """
        Test: Measure error rate under sustained load.
        """
        url = f"{focus_server_url}/ack"
        workers = 20
        total_requests = 500
        timeout = load_config["request_timeout"]
        env = get_environment()
        
        logger.info(f"\n[*] Testing Error Rate with {total_requests} requests...")
        logger.info(f"    Environment: {env.upper()}")
        
        metrics: List[RequestMetric] = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(make_request, url, timeout) 
                      for _ in range(total_requests)]
            
            for future in as_completed(futures, timeout=180):
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
        
        # Environment-specific error rate threshold
        assert result.error_rate < sla_config['ack_error_rate'], \
            f"Error rate {result.error_rate:.1f}% exceeds {sla_config['ack_error_rate']}% threshold ({env})"


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
    def test_channels_endpoint_performance(self, focus_server_url: str, load_config: Dict[str, Any],
                                           sla_config: Dict[str, Any]):
        """
        Test: /channels endpoint performance.
        
        This is a heavy endpoint that returns channel metadata (~2300 channels).
        """
        url = f"{focus_server_url}/channels"
        workers = 20
        timeout = load_config["request_timeout"]
        env = get_environment()
        
        logger.info(f"\n[*] Testing /channels endpoint performance...")
        logger.info(f"    Environment: {env.upper()}")
        logger.info(f"    URL: {url}")
        
        metrics: List[RequestMetric] = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(make_request, url, timeout) 
                      for _ in range(100)]
            
            for future in as_completed(futures, timeout=120):
                try:
                    metrics.append(future.result(timeout=timeout))
                except Exception:
                    pass
        
        duration = time.time() - start_time
        result = analyze_metrics(metrics, "/channels Endpoint", duration, workers)
        log_result_summary(result)
        
        # Environment-specific SLA
        assert result.latency_p95 < sla_config['channels_p95'], \
            f"/channels P95 latency {result.latency_p95:.1f}ms exceeds {sla_config['channels_p95']}ms SLA ({env})"
        assert result.error_rate < sla_config['channels_error_rate'], \
            f"/channels error rate {result.error_rate:.1f}% exceeds {sla_config['channels_error_rate']}% ({env})"
    
    @pytest.mark.xray("PZ-LOAD-011")
    def test_ack_endpoint_performance(self, focus_server_url: str, load_config: Dict[str, Any],
                                      sla_config: Dict[str, Any]):
        """
        Test: /ack (health check) endpoint performance.
        """
        url = f"{focus_server_url}/ack"
        workers = 50
        timeout = 5
        env = get_environment()
        
        logger.info(f"\n[*] Testing /ack endpoint performance...")
        logger.info(f"    Environment: {env.upper()}")
        logger.info(f"    URL: {url}")
        
        metrics: List[RequestMetric] = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(make_request, url, timeout) 
                      for _ in range(200)]
            
            for future in as_completed(futures, timeout=60):
                try:
                    metrics.append(future.result(timeout=timeout))
                except Exception:
                    pass
        
        duration = time.time() - start_time
        result = analyze_metrics(metrics, "/ack Endpoint", duration, workers)
        log_result_summary(result)
        
        # Environment-specific SLA
        assert result.latency_p50 < sla_config['ack_p50'], \
            f"/ack P50 latency {result.latency_p50:.1f}ms exceeds {sla_config['ack_p50']}ms SLA ({env})"
        assert result.latency_p95 < sla_config['ack_p95'], \
            f"/ack P95 latency {result.latency_p95:.1f}ms exceeds {sla_config['ack_p95']}ms SLA ({env})"
        assert result.latency_p99 < sla_config['ack_p99'], \
            f"/ack P99 latency {result.latency_p99:.1f}ms exceeds {sla_config['ack_p99']}ms SLA ({env})"
        assert result.error_rate < sla_config['ack_error_rate'], \
            f"/ack error rate {result.error_rate:.1f}% exceeds {sla_config['ack_error_rate']}% ({env})"
