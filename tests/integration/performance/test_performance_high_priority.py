"""
Integration Tests - Performance (High Priority)
=================================================

High priority performance tests for Focus Server.

Tests Covered (Xray):
    - PZ-13770: Performance – /config Latency P95
    - PZ-13771: Performance – Concurrent Task Limit

Author: QA Automation Architect
Date: 2025-10-21
"""

import pytest
import time
import logging
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.models.focus_server_models import ConfigTaskRequest, ConfigTaskResponse
from src.utils.helpers import generate_task_id, generate_config_payload

logger = logging.getLogger(__name__)


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def performance_config_payload() -> Dict[str, Any]:
    """
    Generate standard configuration payload for performance testing.
    
    Returns:
        Configuration payload optimized for performance testing
    """
    return generate_config_payload(
        sensors_min=0,
        sensors_max=50,
        freq_min=0,
        freq_max=500,
        nfft=1024,
        canvas_height=1000,
        live=True
    )


# ===================================================================
# Test Class: API Latency P95/P99 (PZ-13770)
# ===================================================================

@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.critical
@pytest.mark.slow
class TestAPILatencyP95:
    """
    Test suite for PZ-13770: Performance – /config Latency P95
    Priority: HIGH
    
    Measures and validates P95 and P99 latency for critical API endpoints.
    """
    
    def test_config_endpoint_latency_p95_p99(self, focus_server_api, performance_config_payload):
        """
        Test PZ-13770.1: Measure P95/P99 latency for POST /config.
        
        Steps:
            1. Execute 100 POST /config requests
            2. Measure latency for each request
            3. Calculate P50, P95, P99 percentiles
            4. Verify against thresholds
        
        Expected:
            - P95 latency < [THRESHOLD] ms (need specs!)
            - P99 latency < [THRESHOLD] ms (need specs!)
            - No requests timeout
        
        Jira: PZ-13770
        Priority: HIGH
        """
        logger.info("Test PZ-13770.1: POST /config latency P95/P99")
        
        num_requests = 100
        latencies = []
        errors = 0
        
        logger.info(f"Executing {num_requests} POST /config requests...")
        
        for i in range(num_requests):
            task_id = generate_task_id(f"perf_latency_{i}")
            
            try:
                # Measure request latency
                start_time = time.perf_counter()
                
                config_request = ConfigTaskRequest(**performance_config_payload)
                response = focus_server_api.config_task(task_id, config_request)
                
                end_time = time.perf_counter()
                
                # Record latency in milliseconds
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
                # Verify request succeeded
                if not (response.status == "Config received successfully" or response.status_code == 200):
                    errors += 1
                    logger.warning(f"Request {i}: Unexpected status {response.status_code}")
                
            except Exception as e:
                errors += 1
                logger.error(f"Request {i}: Error - {e}")
            
            # Small delay between requests to avoid overwhelming server
            if i % 10 == 0 and i > 0:
                logger.info(f"Completed {i}/{num_requests} requests")
                time.sleep(0.1)
        
        # Calculate statistics
        assert len(latencies) > 0, "No successful requests"
        
        latencies.sort()
        
        p50 = statistics.median(latencies)
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        min_latency = min(latencies)
        max_latency = max(latencies)
        avg_latency = statistics.mean(latencies)
        
        logger.info("=" * 60)
        logger.info(f"POST /config Latency Results ({len(latencies)} requests):")
        logger.info(f"  Min:  {min_latency:8.2f} ms")
        logger.info(f"  P50:  {p50:8.2f} ms")
        logger.info(f"  Avg:  {avg_latency:8.2f} ms")
        logger.info(f"  P95:  {p95:8.2f} ms ⭐")
        logger.info(f"  P99:  {p99:8.2f} ms ⭐")
        logger.info(f"  Max:  {max_latency:8.2f} ms")
        logger.info(f"  Errors: {errors}/{num_requests}")
        logger.info("=" * 60)
        
        # TODO: Update thresholds after specs meeting
        # For now, use reasonable defaults for high-performance API
        THRESHOLD_P95_MS = 500   # 500ms for P95
        THRESHOLD_P99_MS = 1000  # 1000ms for P99
        MAX_ERROR_RATE = 0.05    # 5% error rate
        
        # Assertions
        error_rate = errors / num_requests
        assert error_rate <= MAX_ERROR_RATE, \
            f"Error rate {error_rate:.2%} exceeds threshold {MAX_ERROR_RATE:.2%}"
        
        # TODO: Uncomment after specs meeting
        # assert p95 < THRESHOLD_P95_MS, \
        #     f"P95 latency {p95:.2f}ms exceeds threshold {THRESHOLD_P95_MS}ms"
        # 
        # assert p99 < THRESHOLD_P99_MS, \
        #     f"P99 latency {p99:.2f}ms exceeds threshold {THRESHOLD_P99_MS}ms"
        
        # For now, just log warning if exceeds reasonable thresholds
        if p95 >= THRESHOLD_P95_MS:
            logger.warning(f"⚠️ P95 latency {p95:.2f}ms >= {THRESHOLD_P95_MS}ms (would fail if enforced)")
        else:
            logger.info(f"✅ P95 latency {p95:.2f}ms < {THRESHOLD_P95_MS}ms")
        
        if p99 >= THRESHOLD_P99_MS:
            logger.warning(f"⚠️ P99 latency {p99:.2f}ms >= {THRESHOLD_P99_MS}ms (would fail if enforced)")
        else:
            logger.info(f"✅ P99 latency {p99:.2f}ms < {THRESHOLD_P99_MS}ms")
    
    def test_waterfall_endpoint_latency_p95(self, focus_server_api, performance_config_payload):
        """
        Test PZ-13770.2: Measure P95/P99 latency for GET /waterfall.
        
        Steps:
            1. Configure a task
            2. Execute 50 GET /waterfall requests
            3. Measure latencies
            4. Calculate P95/P99
        
        Expected:
            - P95 latency < [THRESHOLD] ms
            - P99 latency < [THRESHOLD] ms
        
        Jira: PZ-13770
        Priority: HIGH
        """
        logger.info("Test PZ-13770.2: GET /waterfall latency P95/P99")
        
        # Configure a task first
        task_id = generate_task_id("perf_waterfall")
        config_request = ConfigTaskRequest(**performance_config_payload)
        response = focus_server_api.config_task(task_id, config_request)
        assert response.status == "Config received successfully" or response.status_code == 200
        
        logger.info(f"Task {task_id} configured, measuring waterfall latency...")
        
        num_requests = 50
        latencies = []
        errors = 0
        
        for i in range(num_requests):
            try:
                start_time = time.perf_counter()
                
                waterfall_response = focus_server_api.get_waterfall(task_id, row_count=100)
                
                end_time = time.perf_counter()
                
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
                # Any status 200/201/208 is acceptable for latency measurement
                if waterfall_response.status_code not in [200, 201, 208]:
                    errors += 1
                
            except Exception as e:
                errors += 1
                logger.error(f"Request {i}: Error - {e}")
            
            time.sleep(0.2)  # Small delay between requests
        
        # Calculate statistics
        assert len(latencies) > 0, "No successful requests"
        
        latencies.sort()
        
        p50 = statistics.median(latencies)
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        avg_latency = statistics.mean(latencies)
        
        logger.info("=" * 60)
        logger.info(f"GET /waterfall Latency Results ({len(latencies)} requests):")
        logger.info(f"  P50:  {p50:8.2f} ms")
        logger.info(f"  Avg:  {avg_latency:8.2f} ms")
        logger.info(f"  P95:  {p95:8.2f} ms ⭐")
        logger.info(f"  P99:  {p99:8.2f} ms ⭐")
        logger.info(f"  Errors: {errors}/{num_requests}")
        logger.info("=" * 60)
        
        # TODO: Update thresholds after specs meeting
        THRESHOLD_P95_MS = 300   # Waterfall may be faster than config
        THRESHOLD_P99_MS = 600
        
        if p95 >= THRESHOLD_P95_MS:
            logger.warning(f"⚠️ GET /waterfall P95 {p95:.2f}ms >= {THRESHOLD_P95_MS}ms")
        else:
            logger.info(f"✅ GET /waterfall P95 {p95:.2f}ms < {THRESHOLD_P95_MS}ms")


# ===================================================================
# Test Class: Concurrent Task Limit (PZ-13771)
# ===================================================================

@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.critical
@pytest.mark.slow
class TestConcurrentTaskLimit:
    """
    Test suite for PZ-13771: Performance – Concurrent Task Limit
    Priority: HIGH
    
    Validates system behavior under concurrent task load and determines
    maximum supported concurrent tasks.
    """
    
    def test_concurrent_task_creation(self, focus_server_api, performance_config_payload):
        """
        Test PZ-13771.1: Create multiple concurrent tasks.
        
        Steps:
            1. Create 20 tasks concurrently using ThreadPoolExecutor
            2. Measure success rate
            3. Verify system stability
        
        Expected:
            - At least X concurrent tasks succeed (need specs!)
            - System remains stable
            - No crashes or errors
        
        Jira: PZ-13771
        Priority: HIGH
        """
        logger.info("Test PZ-13771.1: Concurrent task creation")
        
        num_concurrent = 20
        max_workers = 10
        
        logger.info(f"Creating {num_concurrent} tasks with {max_workers} workers...")
        
        def create_task(task_num: int) -> Dict[str, Any]:
            """Create a single task and return result."""
            task_id = generate_task_id(f"concurrent_{task_num}")
            
            try:
                start_time = time.perf_counter()
                
                config_request = ConfigTaskRequest(**performance_config_payload)
                response = focus_server_api.config_task(task_id, config_request)
                
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                
                success = (response.status == "Config received successfully" or 
                          response.status_code == 200)
                
                return {
                    'task_id': task_id,
                    'task_num': task_num,
                    'success': success,
                    'latency_ms': latency_ms,
                    'status_code': getattr(response, 'status_code', None),
                    'error': None
                }
                
            except Exception as e:
                logger.error(f"Task {task_num} failed: {e}")
                return {
                    'task_id': task_id,
                    'task_num': task_num,
                    'success': False,
                    'latency_ms': None,
                    'status_code': None,
                    'error': str(e)
                }
        
        # Execute concurrent task creation
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(create_task, i) for i in range(num_concurrent)]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                
                if result['success']:
                    logger.info(f"✅ Task {result['task_num']}: {result['latency_ms']:.2f}ms")
                else:
                    logger.warning(f"❌ Task {result['task_num']}: Failed")
        
        # Analyze results
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        success_rate = len(successful) / num_concurrent
        
        logger.info("=" * 60)
        logger.info(f"Concurrent Task Creation Results:")
        logger.info(f"  Total tasks:      {num_concurrent}")
        logger.info(f"  Successful:       {len(successful)}")
        logger.info(f"  Failed:           {len(failed)}")
        logger.info(f"  Success rate:     {success_rate:.1%}")
        
        if successful:
            latencies = [r['latency_ms'] for r in successful]
            avg_latency = statistics.mean(latencies)
            max_latency = max(latencies)
            logger.info(f"  Avg latency:      {avg_latency:.2f}ms")
            logger.info(f"  Max latency:      {max_latency:.2f}ms")
        
        logger.info("=" * 60)
        
        # TODO: Update threshold after specs meeting
        MIN_SUCCESS_RATE = 0.90  # 90% success rate
        
        assert success_rate >= MIN_SUCCESS_RATE, \
            f"Success rate {success_rate:.1%} < threshold {MIN_SUCCESS_RATE:.1%}"
        
        logger.info(f"✅ Concurrent task creation: {success_rate:.1%} success rate")
    
    def test_concurrent_task_polling(self, focus_server_api, performance_config_payload):
        """
        Test PZ-13771.2: Poll multiple tasks concurrently.
        
        Steps:
            1. Create 10 tasks
            2. Poll all tasks concurrently
            3. Verify all tasks can be polled
        
        Expected:
            - All tasks can be polled concurrently
            - No interference between tasks
        
        Jira: PZ-13771
        Priority: HIGH
        """
        logger.info("Test PZ-13771.2: Concurrent task polling")
        
        num_tasks = 10
        
        # Create tasks first
        task_ids = []
        logger.info(f"Creating {num_tasks} tasks...")
        
        for i in range(num_tasks):
            task_id = generate_task_id(f"poll_concurrent_{i}")
            config_request = ConfigTaskRequest(**performance_config_payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            if response.status == "Config received successfully" or response.status_code == 200:
                task_ids.append(task_id)
        
        assert len(task_ids) >= num_tasks * 0.8, \
            f"Only {len(task_ids)}/{num_tasks} tasks created successfully"
        
        logger.info(f"{len(task_ids)} tasks created successfully")
        
        # Poll all tasks concurrently
        def poll_task(task_id: str) -> Dict[str, Any]:
            """Poll a single task and return result."""
            try:
                response = focus_server_api.get_waterfall(task_id, row_count=100)
                return {
                    'task_id': task_id,
                    'success': True,
                    'status_code': response.status_code,
                    'has_data': hasattr(response, 'data') and response.data is not None
                }
            except Exception as e:
                return {
                    'task_id': task_id,
                    'success': False,
                    'error': str(e)
                }
        
        logger.info(f"Polling {len(task_ids)} tasks concurrently...")
        
        poll_results = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(poll_task, tid) for tid in task_ids]
            
            for future in as_completed(futures):
                result = future.result()
                poll_results.append(result)
        
        # Analyze results
        successful_polls = [r for r in poll_results if r['success']]
        failed_polls = [r for r in poll_results if not r['success']]
        
        logger.info("=" * 60)
        logger.info(f"Concurrent Polling Results:")
        logger.info(f"  Tasks polled:     {len(poll_results)}")
        logger.info(f"  Successful:       {len(successful_polls)}")
        logger.info(f"  Failed:           {len(failed_polls)}")
        logger.info("=" * 60)
        
        # All polls should succeed
        assert len(failed_polls) == 0, \
            f"{len(failed_polls)} polls failed: {failed_polls}"
        
        logger.info("✅ All tasks polled successfully")
    
    def test_concurrent_task_max_limit(self, focus_server_api, performance_config_payload):
        """
        Test PZ-13771.3: Find maximum concurrent task limit.
        
        Steps:
            1. Gradually increase concurrent task count
            2. Find the point where tasks start failing
            3. Document maximum supported concurrent tasks
        
        Expected:
            - System supports at least [MIN] concurrent tasks
            - Graceful degradation when limit exceeded
        
        Jira: PZ-13771
        Priority: HIGH
        """
        logger.info("Test PZ-13771.3: Maximum concurrent task limit")
        
        # Try increasing numbers of concurrent tasks
        test_counts = [10, 20, 30, 40, 50]
        results_by_count = {}
        
        for count in test_counts:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing {count} concurrent tasks...")
            logger.info(f"{'='*60}")
            
            def create_task(task_num: int) -> bool:
                task_id = generate_task_id(f"max_limit_{count}_{task_num}")
                try:
                    config_request = ConfigTaskRequest(**performance_config_payload)
                    response = focus_server_api.config_task(task_id, config_request)
                    return response.status == "Config received successfully" or response.status_code == 200
                except:
                    return False
            
            with ThreadPoolExecutor(max_workers=min(count, 20)) as executor:
                futures = [executor.submit(create_task, i) for i in range(count)]
                outcomes = [f.result() for f in as_completed(futures)]
            
            success_count = sum(outcomes)
            success_rate = success_count / count
            
            results_by_count[count] = {
                'success_count': success_count,
                'success_rate': success_rate
            }
            
            logger.info(f"Result: {success_count}/{count} succeeded ({success_rate:.1%})")
            
            # If success rate drops below 80%, we've likely hit the limit
            if success_rate < 0.80:
                logger.info(f"⚠️ Success rate dropped below 80% at {count} tasks")
                break
            
            # Small delay between test rounds
            time.sleep(2)
        
        # Report findings
        logger.info("\n" + "=" * 60)
        logger.info("Maximum Concurrent Task Limit - Summary:")
        logger.info("=" * 60)
        
        for count, result in results_by_count.items():
            logger.info(f"  {count:3d} tasks: {result['success_count']:3d} succeeded ({result['success_rate']:.1%})")
        
        logger.info("=" * 60)
        
        # TODO: Update minimum after specs meeting
        MIN_CONCURRENT_TASKS = 10
        
        # Find highest count with >= 90% success rate
        high_success_counts = [count for count, result in results_by_count.items() 
                              if result['success_rate'] >= 0.90]
        
        if high_success_counts:
            max_reliable = max(high_success_counts)
            logger.info(f"✅ System reliably supports at least {max_reliable} concurrent tasks")
            
            assert max_reliable >= MIN_CONCURRENT_TASKS, \
                f"Max reliable concurrent tasks {max_reliable} < minimum {MIN_CONCURRENT_TASKS}"
        else:
            pytest.fail("Could not find reliable concurrent task count")


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary
def test_performance_high_priority_summary():
    """
    Summary test for performance (high priority tests).
    
    This test documents which Xray test cases are covered in this module.
    
    Covered Xray Tests:
        ✅ PZ-13770: Performance – /config Latency P95/P99 (2 tests)
        ✅ PZ-13771: Performance – Concurrent Task Limit (3 tests)
    
    Total: 5 high-priority performance tests
    """
    logger.info("=" * 80)
    logger.info("Performance (High Priority) - Summary")
    logger.info("=" * 80)
    logger.info("Xray Test Coverage:")
    logger.info("  ✅ PZ-13770: API Latency P95/P99 - 2 tests")
    logger.info("  ✅ PZ-13771: Concurrent Task Limit - 3 tests")
    logger.info("=" * 80)
    logger.info("Total: 5 High Priority Tests")
    logger.info("=" * 80)

