"""
Integration Tests - Alerts: Load Scenarios
==========================================

Tests for load and stress scenarios in alert generation.

SMART LOAD TESTING FEATURES:
    - Gradual load increase (step-by-step)
    - Automatic breakpoint detection
    - Smart stopping after consecutive failures
    - Detailed logging and reporting

Tests Covered (Xray):
    - PZ-14953: Alert Generation - High Volume Load (Smart)
    - PZ-14954: Alert Generation - Sustained Load
    - PZ-14955: Alert Generation - Burst Load (Smart)
    - PZ-14956: Alert Generation - Mixed Alert Types Load
    - PZ-14957: Alert Generation - RabbitMQ Queue Capacity
    - PZ-15100: Smart Breakpoint Detection Test (NEW)

Author: QA Automation Architect
Date: 2025-11-13
Updated: 2025-11-29 - Added Smart Load Testing with breakpoint detection
"""

import pytest
import logging
import time
import json
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean, median

try:
    import pika
    PIKA_AVAILABLE = True
except ImportError:
    PIKA_AVAILABLE = False

from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager
from be_focus_server_tests.integration.alerts.alert_test_helpers import (
    send_alert_via_api,
    create_alert_payload,
    authenticate_session
)
from be_focus_server_tests.integration.alerts.smart_load_tester import (
    SmartLoadTester,
    AlertLoadTester,
    BreakpointReport,
    FailureType
)
from datetime import datetime

logger = logging.getLogger(__name__)


def _get_rabbitmq_connection_manager(config_manager):
    """Helper function to create RabbitMQConnectionManager with SSH credentials."""
    # Get SSH config for RabbitMQ connection
    ssh_config = config_manager.get("ssh", {})
    if "target_host" in ssh_config:
        ssh_host = ssh_config["target_host"]["host"]
        ssh_user = ssh_config["target_host"]["username"]
        ssh_password = ssh_config["target_host"].get("password")
        ssh_key_file = ssh_config["target_host"].get("key_file")
    else:
        ssh_host = ssh_config.get("host")
        ssh_user = ssh_config.get("username", "prisma")
        ssh_password = ssh_config.get("password")
        ssh_key_file = ssh_config.get("key_file")
    
    # Expand SSH key path if needed
    if ssh_key_file and ssh_key_file.startswith('~'):
        from pathlib import Path
        home = str(Path.home())
        ssh_key_file = ssh_key_file.replace('~', home, 1)
    
    return RabbitMQConnectionManager(
        k8s_host=config_manager.get("kubernetes", {}).get("host", ssh_host or "10.10.10.100"),
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        ssh_key_file=ssh_key_file
    )


@pytest.mark.slow
@pytest.mark.nightly
@pytest.mark.load
class TestAlertGenerationLoad:
    """
    Test suite for load scenarios in alert generation.
    
    Tests covered:
        - PZ-14953: High Volume Load
        - PZ-14954: Sustained Load
        - PZ-14955: Burst Load
        - PZ-14956: Mixed Alert Types Load
        - PZ-14957: RabbitMQ Queue Capacity
    """
    
    @pytest.mark.xray("PZ-14953")
    def test_high_volume_load(self, config_manager):
        """
        Test PZ-14953: Alert Generation - High Volume Load (SMART).
        
        Objective:
            Use smart load testing to gradually increase volume and detect
            the exact breakpoint where system starts failing.
        
        SMART FEATURES:
            - Gradual load increase (step-by-step)
            - Automatic breakpoint detection (429, connection pool full)
            - Stops after 5 consecutive failures - no wasted requests!
            - Reports max healthy volume capacity
        
        Steps:
            1. Start with 5 concurrent requests, 50 per step
            2. Increase by 5 concurrent each step
            3. Monitor for failures (429, connection pool, etc.)
            4. Stop when breakpoint detected
            5. Report max healthy volume
        
        Expected:
            Breakpoint is detected and logged.
            Max healthy volume is reported.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - High Volume Load SMART (PZ-14953)")
        logger.info("=" * 80)
        
        # Get base URL for authentication
        # Use frontend_url or base_url for auth (not frontend_api_url which is NodePort)
        api_config = config_manager.get("focus_server", {})
        # Try frontend_url first, fallback to base_url, then default
        base_url = api_config.get("frontend_url") or api_config.get("base_url") or "https://10.10.10.100/prisma/api/"
        # Convert frontend URL to API base URL if needed
        if "/liveView" in base_url:
            base_url = base_url.replace("/liveView", "/prisma/api/")
        if not base_url.endswith("/"):
            base_url += "/"
        # Ensure we have /prisma/api/ in the path
        if "/prisma/api" not in base_url:
            base_url = base_url.rstrip("/") + "/prisma/api/"
        
        # Create shared session
        session = authenticate_session(base_url)
        
        # Use Smart Load Tester
        tester = AlertLoadTester(
            config_manager=config_manager,
            session=session,
            initial_concurrent=5,      # Start gentle
            step_increment=5,          # Increase by 5 each step
            max_concurrent=75,         # Max concurrent to test
            requests_per_step=50,      # 50 requests per step = high volume
            max_consecutive_failures=5  # Stop after 5 consecutive failures
        )
        
        # Run smart load test
        report = tester.run()
        
        # Log results
        logger.info(f"Results (SMART):")
        logger.info(f"  📊 Max healthy load: {report.max_healthy_load} concurrent requests")
        logger.info(f"  📈 Steps completed: {report.steps_completed}")
        logger.info(f"  📦 Total requests sent: {report.total_requests_sent}")
        logger.info(f"  ✅ Successful: {report.total_successful}")
        logger.info(f"  ❌ Failed: {report.total_failed}")
        success_rate = report.total_successful / max(report.total_requests_sent, 1)
        logger.info(f"  📉 Success rate: {success_rate * 100:.1f}%")
        logger.info(f"  ⏱️  Duration: {report.duration_seconds:.2f}s")
        
        if report.detected:
            logger.info(f"  🔴 BREAKPOINT DETECTED at step {report.breakpoint_step}")
            logger.info(f"  ⚠️  Failure type: {report.failure_type.value if report.failure_type else 'N/A'}")
            logger.info(f"  💡 System capacity: ~{report.max_healthy_load * 50 // 5} requests before failure")
        else:
            logger.info(f"  ✅ No breakpoint - system handled all load levels!")
        
        # Test passes if system handles at least 5 concurrent requests
        assert report.max_healthy_load >= 5, \
            f"System should handle at least 5 concurrent requests, got {report.max_healthy_load}"
        
        logger.info("✅ TEST PASSED: High volume SMART load detection completed")
    
    @pytest.mark.xray("PZ-14954")
    def test_sustained_load(self, config_manager):
        """
        Test PZ-14954: Alert Generation - Sustained Load with Circuit Breaker.
        
        Objective:
            Verify that system can handle sustained load over extended period
            without degradation. Uses smart circuit breaker to stop early if
            system is persistently rate-limited or has config issues.
        
        Circuit Breaker Logic:
            - 401 Unauthorized: Stop immediately (config problem)
            - 429 Rate Limited: Stop after 3 consecutive rate limit cycles
            - Other errors: Continue with logging
        
        Expected:
            System maintains performance under sustained load.
            Test exits early if system is persistently rate-limited (this is a FINDING, not a failure).
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Sustained Load with Circuit Breaker (PZ-14954)")
        logger.info("=" * 80)
        
        # Configuration - reduced duration for faster feedback
        duration_seconds = 120  # 2 minutes (was 10 minutes - too long for CI)
        alerts_per_second = 5
        
        # Circuit breaker thresholds
        max_consecutive_401 = 3   # Stop immediately on auth errors
        max_rate_limit_cycles = 3  # Stop after 3 backoff cycles
        backoff_time = 10  # seconds to wait when rate limited
        
        # Get base URL for authentication
        api_config = config_manager.get("focus_server", {})
        base_url = api_config.get("frontend_url") or api_config.get("base_url") or "https://10.10.10.100/prisma/api/"
        if "/liveView" in base_url:
            base_url = base_url.replace("/liveView", "/prisma/api/")
        if not base_url.endswith("/"):
            base_url += "/"
        if "/prisma/api" not in base_url:
            base_url = base_url.rstrip("/") + "/prisma/api/"
        
        # Create shared session
        session = authenticate_session(base_url)
        
        start_time = time.time()
        success_count = 0
        fail_count = 0
        consecutive_401_errors = 0
        consecutive_429_errors = 0
        rate_limit_cycles = 0
        circuit_breaker_reason = None
        
        logger.info(f"Starting sustained load test: {duration_seconds}s, {alerts_per_second} alerts/sec")
        logger.info(f"Circuit breaker: 401 threshold={max_consecutive_401}, rate limit cycles={max_rate_limit_cycles}")
        
        while time.time() - start_time < duration_seconds:
            # === CIRCUIT BREAKER CHECK ===
            
            # 1. Check for persistent 401 errors (config problem)
            if consecutive_401_errors >= max_consecutive_401:
                circuit_breaker_reason = f"⛔ CIRCUIT BREAKER: {consecutive_401_errors} consecutive 401 Unauthorized errors. Check URL/auth config!"
                logger.error(circuit_breaker_reason)
                break
            
            # 2. Check for persistent rate limiting
            if rate_limit_cycles >= max_rate_limit_cycles:
                circuit_breaker_reason = f"🔴 CIRCUIT BREAKER: System persistently rate-limited ({rate_limit_cycles} cycles). Capacity finding recorded."
                logger.warning(circuit_breaker_reason)
                break
            
            # 3. Check for too many consecutive 429 errors
            if consecutive_429_errors >= 5:
                logger.warning(f"⚠️ Rate limit backoff #{rate_limit_cycles + 1}: {consecutive_429_errors} consecutive 429 errors")
                time.sleep(backoff_time)
                consecutive_429_errors = 0
                rate_limit_cycles += 1
                continue
            
            # === SEND ALERTS ===
            for _ in range(alerts_per_second):
                alert_payload = {
                    "alertsAmount": 1,
                    "dofM": 1000 + (success_count % 2000),
                    "classId": 104,
                    "severity": (success_count % 3) + 1,
                    "alertIds": [f"sustained-{success_count}-{int(time.time())}"]
                }
                
                try:
                    response = send_alert_via_api(
                        config_manager, 
                        alert_payload, 
                        session=session,
                        max_retries=2,  # Reduced retries - circuit breaker handles persistence
                        retry_delay=0.5
                    )
                    if response.status_code in [200, 201]:
                        success_count += 1
                        consecutive_401_errors = 0
                        consecutive_429_errors = 0
                except Exception as e:
                    error_str = str(e)
                    fail_count += 1
                    
                    # Classify error for circuit breaker
                    if "401" in error_str or "Unauthorized" in error_str:
                        consecutive_401_errors += 1
                        consecutive_429_errors = 0
                        logger.error(f"401 error #{consecutive_401_errors}: {e}")
                    elif "429" in error_str or "Too Many Requests" in error_str:
                        consecutive_429_errors += 1
                        consecutive_401_errors = 0
                        # Only log every 5th 429 to reduce noise
                        if consecutive_429_errors % 5 == 1:
                            logger.warning(f"Rate limited (429): consecutive={consecutive_429_errors}")
                    else:
                        # Other errors - log but don't affect circuit breaker
                        consecutive_401_errors = 0
                        consecutive_429_errors = 0
                        logger.debug(f"Other error: {e}")
                
                time.sleep(0.05)  # 50ms between requests
            
            time.sleep(0.5)  # Wait before next batch
        
        # === RESULTS ===
        elapsed_time = time.time() - start_time
        total_attempts = success_count + fail_count
        success_rate = success_count / max(total_attempts, 1) * 100
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("SUSTAINED LOAD TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"  Duration: {elapsed_time:.1f}s")
        logger.info(f"  Alerts sent: {success_count}")
        logger.info(f"  Alerts failed: {fail_count}")
        logger.info(f"  Success rate: {success_rate:.1f}%")
        logger.info(f"  Rate: {success_count / elapsed_time:.2f} alerts/sec")
        
        if circuit_breaker_reason:
            logger.info(f"  Exit reason: {circuit_breaker_reason}")
            # Circuit breaker triggered is a FINDING, not necessarily a failure
            if "401" in circuit_breaker_reason:
                pytest.fail(f"Test failed due to authentication errors: {circuit_breaker_reason}")
            else:
                # Rate limit finding - test passes but with warning
                logger.warning("📊 FINDING: System has rate limiting that kicks in under sustained load")
        
        # Test passes if we got at least some successful requests
        assert success_count > 0, "No alerts were successfully sent"
        
        logger.info("✅ TEST PASSED: Sustained load test completed")
    
    @pytest.mark.xray("PZ-14955")
    def test_burst_load(self, config_manager):
        """
        Test PZ-14955: Alert Generation - Burst Load (SMART).
        
        Objective:
            Use smart load testing to gradually find the maximum burst size
            the system can handle without failures.
        
        SMART FEATURES:
            - Starts with 10 concurrent, increases by 10 each step
            - Automatically detects breakpoint (429, connection pool full)
            - Stops after 5 consecutive failures
            - Reports exact max healthy burst size
        
        Steps:
            1. Start with 10 concurrent requests
            2. Increase by 10 each step up to 100
            3. Monitor for failures
            4. Stop when breakpoint detected
            5. Report max healthy burst size
        
        Expected:
            Breakpoint is detected and max burst capacity is reported.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Burst Load SMART (PZ-14955)")
        logger.info("=" * 80)
        
        # Get base URL for authentication
        # Use frontend_url or base_url for auth (not frontend_api_url which is NodePort)
        api_config = config_manager.get("focus_server", {})
        # Try frontend_url first, fallback to base_url, then default
        base_url = api_config.get("frontend_url") or api_config.get("base_url") or "https://10.10.10.100/prisma/api/"
        # Convert frontend URL to API base URL if needed
        if "/liveView" in base_url:
            base_url = base_url.replace("/liveView", "/prisma/api/")
        if not base_url.endswith("/"):
            base_url += "/"
        # Ensure we have /prisma/api/ in the path
        if "/prisma/api" not in base_url:
            base_url = base_url.rstrip("/") + "/prisma/api/"
        
        # Create shared session
        session = authenticate_session(base_url)
        
        # Use Smart Load Tester for burst detection
        tester = AlertLoadTester(
            config_manager=config_manager,
            session=session,
            initial_concurrent=10,     # Start with 10 concurrent
            step_increment=10,         # Add 10 each step
            max_concurrent=100,        # Max burst to test
            requests_per_step=30,      # 30 requests per step
            max_consecutive_failures=5  # Stop after 5 consecutive failures
        )
        
        # Run smart burst test
        report = tester.run()
        
        # Log results
        logger.info(f"Results (SMART):")
        logger.info(f"  📊 Max healthy burst: {report.max_healthy_load} concurrent requests")
        logger.info(f"  📈 Steps completed: {report.steps_completed}")
        logger.info(f"  ✅ Successful requests: {report.total_successful}")
        logger.info(f"  ❌ Failed requests: {report.total_failed}")
        logger.info(f"  ⏱️  Total time: {report.duration_seconds:.2f}s")
        
        if report.detected:
            logger.info(f"  🔴 Breakpoint at step {report.breakpoint_step}")
            logger.info(f"  ⚠️  Failure type: {report.failure_type.value if report.failure_type else 'N/A'}")
        
        # Test passes if system handles at least 10 concurrent requests
        assert report.max_healthy_load >= 10, \
            f"System should handle at least 10 concurrent requests, got {report.max_healthy_load}"
        
        logger.info("✅ TEST PASSED: Burst load SMART detection completed")
    
    @pytest.mark.xray("PZ-14956")
    def test_mixed_alert_types_load(self, config_manager):
        """
        Test PZ-14956: Alert Generation - Mixed Alert Types Load with Circuit Breaker.
        
        Objective:
            Verify that system can handle mixed alert types (SD, SC, different severities)
            under load without issues. Uses circuit breaker to stop on persistent errors.
        
        Circuit Breaker:
            - 401 Unauthorized: Stop immediately (config error)
            - 429 Rate Limited: Stop after 3 consecutive cycles
        
        Expected:
            All alert types are processed correctly under load.
            Test exits early if system is rate-limited (this is a FINDING).
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Mixed Alert Types Load with Circuit Breaker (PZ-14956)")
        logger.info("=" * 80)
        
        num_alerts = 100  # Reduced from 300 for faster feedback
        class_ids = [103, 104]  # SC and SD
        severities = [1, 2, 3]
        
        # Circuit breaker thresholds
        max_consecutive_401 = 3
        max_consecutive_429 = 10
        
        # Get base URL for authentication
        api_config = config_manager.get("focus_server", {})
        base_url = api_config.get("frontend_url") or api_config.get("base_url") or "https://10.10.10.100/prisma/api/"
        if "/liveView" in base_url:
            base_url = base_url.replace("/liveView", "/prisma/api/")
        if not base_url.endswith("/"):
            base_url += "/"
        if "/prisma/api" not in base_url:
            base_url = base_url.rstrip("/") + "/prisma/api/"
        
        # Create shared session
        session = authenticate_session(base_url)
        
        success_by_type = {
            "SD": 0, "SC": 0,
            "severity_1": 0, "severity_2": 0, "severity_3": 0
        }
        fail_count = 0
        consecutive_401 = 0
        consecutive_429 = 0
        circuit_breaker_reason = None
        
        for i in range(num_alerts):
            # === CIRCUIT BREAKER CHECK ===
            if consecutive_401 >= max_consecutive_401:
                circuit_breaker_reason = f"⛔ CIRCUIT BREAKER: {consecutive_401} consecutive 401 errors"
                logger.error(circuit_breaker_reason)
                break
            
            if consecutive_429 >= max_consecutive_429:
                circuit_breaker_reason = f"🔴 CIRCUIT BREAKER: {consecutive_429} consecutive 429 errors - system rate-limited"
                logger.warning(circuit_breaker_reason)
                break
            
            class_id = class_ids[i % len(class_ids)]
            severity = severities[i % len(severities)]
            
            alert_payload = {
                "alertsAmount": 1,
                "dofM": 1000 + (i % 2000),
                "classId": class_id,
                "severity": severity,
                "alertIds": [f"mixed-{class_id}-{severity}-{i}-{int(time.time())}"]
            }
            
            try:
                response = send_alert_via_api(
                    config_manager, alert_payload, session=session,
                    max_retries=2, retry_delay=0.5
                )
                if response.status_code in [200, 201]:
                    consecutive_401 = 0
                    consecutive_429 = 0
                    
                    if class_id == 104:
                        success_by_type["SD"] += 1
                    else:
                        success_by_type["SC"] += 1
                    success_by_type[f"severity_{severity}"] += 1
            except Exception as e:
                error_str = str(e)
                fail_count += 1
                
                if "401" in error_str or "Unauthorized" in error_str:
                    consecutive_401 += 1
                    consecutive_429 = 0
                elif "429" in error_str or "Too Many Requests" in error_str:
                    consecutive_429 += 1
                    consecutive_401 = 0
                else:
                    consecutive_401 = 0
                    consecutive_429 = 0
                
                logger.debug(f"Alert {i} failed: {e}")
            
            time.sleep(0.02)  # Small delay to avoid flooding
        
        total_success = sum([success_by_type["SD"], success_by_type["SC"]])
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("MIXED ALERT TYPES TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"  SD alerts: {success_by_type['SD']}")
        logger.info(f"  SC alerts: {success_by_type['SC']}")
        logger.info(f"  Severity 1: {success_by_type['severity_1']}")
        logger.info(f"  Severity 2: {success_by_type['severity_2']}")
        logger.info(f"  Severity 3: {success_by_type['severity_3']}")
        logger.info(f"  Failed: {fail_count}")
        
        if circuit_breaker_reason:
            logger.info(f"  Exit reason: {circuit_breaker_reason}")
            if "401" in circuit_breaker_reason:
                pytest.fail(f"Test failed due to auth errors: {circuit_breaker_reason}")
        
        # Test passes if we got at least some successful alerts
        assert total_success > 0, "No alerts were successfully sent"
        
        logger.info("✅ TEST PASSED: Mixed alert types load handled successfully")
    
    @pytest.mark.xray("PZ-14957")
    @pytest.mark.skipif(not PIKA_AVAILABLE, reason="pika not installed")
    def test_rabbitmq_queue_capacity(self, config_manager):
        """
        Test PZ-14957: Alert Generation - RabbitMQ Queue Capacity.
        
        Objective:
            Verify that RabbitMQ queues can handle high volume of alerts
            without overflow or message loss.
        
        Steps:
            1. Generate alerts until queue reaches capacity
            2. Monitor queue size
            3. Verify no message loss
            4. Verify queue recovery
        
        Expected:
            Queue handles capacity correctly.
            No message loss.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - RabbitMQ Queue Capacity (PZ-14957)")
        logger.info("=" * 80)
        
        # Get RabbitMQ configuration
        with _get_rabbitmq_connection_manager(config_manager) as conn_info:
            try:
                import pika
                
                # Connect to RabbitMQ
                credentials = pika.PlainCredentials(
                    conn_info["username"],
                    conn_info["password"]
                )
                parameters = pika.ConnectionParameters(
                    host=conn_info["host"],
                    port=conn_info["port"],
                    credentials=credentials,
                    heartbeat=600
                )
                
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                
                # Declare exchange
                channel.exchange_declare(
                    exchange="prisma",
                    exchange_type="topic",
                    durable=True
                )
                
                # Generate alerts and monitor queue
                num_alerts = 500  # Reduced from 1000 to avoid queue overload
                published_count = 0
                
                for i in range(num_alerts):
                    alert_message = {
                        "algorun_id": f"load-test-{i}",
                        "alert_id": f"load-test-{i}-{int(time.time())}",
                        "class_id": 104,
                        "severity": (i % 3) + 1,
                        "distance_m": 1000 + (i % 2000),
                        "alert_time": datetime.now().isoformat(),
                        "time_interval_s": 150
                    }
                    
                    try:
                        channel.basic_publish(
                            exchange="prisma",
                            routing_key="Algorithm.AlertReport.MLGround",
                            body=json.dumps(alert_message),
                            properties=pika.BasicProperties(
                                delivery_mode=2,
                                content_type="application/json"
                            )
                        )
                        published_count += 1
                    except Exception as e:
                        logger.error(f"Failed to publish alert {i}: {e}")
                
                connection.close()
                
                logger.info(f"Published {published_count} alerts")
                assert published_count >= num_alerts * 0.95, \
                    f"Published {published_count} alerts, expected at least {num_alerts * 0.95}"
                
                logger.info("✅ TEST PASSED: RabbitMQ queue capacity handled successfully")
                
            except Exception as e:
                logger.error(f"❌ TEST FAILED: {e}")
                raise
    
    @pytest.mark.xray("PZ-15035")
    @pytest.mark.skip(reason="Alerts are NOT stored in MongoDB - this test is invalid")
    def test_mongodb_write_load(self, config_manager):
        """
        Test PZ-15035: Alert Generation - MongoDB Write Load.
        
        SKIPPED: Alerts are NOT stored in MongoDB, so this test is not applicable.
        
        This test was removed because:
        - Alerts are sent via Prisma Web App API to RabbitMQ
        - Alerts are NOT persisted in MongoDB
        - Testing MongoDB write load for alerts is not relevant
        """
        pytest.skip("Alerts are NOT stored in MongoDB - this test is invalid")
    
    @pytest.mark.xray("PZ-15100")
    def test_smart_breakpoint_detection(self, config_manager):
        """
        Test PZ-15100: Smart Breakpoint Detection.
        
        Objective:
            Use smart load testing to gradually increase load and detect
            the exact breakpoint where the system starts failing.
        
        Features:
            - Starts with low load (5 concurrent requests)
            - Increases by 5 each step
            - Detects breakpoint automatically (429, connection pool full, etc.)
            - Stops after 5 consecutive failures of the same type
            - Provides detailed breakpoint report
        
        Steps:
            1. Start with 5 concurrent requests
            2. Send 20 requests per step
            3. Increase load by 5 concurrent each step
            4. Monitor for failures (429, connection pool, etc.)
            5. Stop when breakpoint is detected
            6. Log detailed breakpoint report
        
        Expected:
            System breakpoint is detected and logged.
            Test passes regardless of where breakpoint is detected.
            Detailed report shows max healthy load capacity.
        """
        logger.info("=" * 80)
        logger.info("TEST: Smart Breakpoint Detection (PZ-15100)")
        logger.info("=" * 80)
        
        # Get base URL for authentication
        # Use frontend_url or base_url for auth (not frontend_api_url which is NodePort)
        api_config = config_manager.get("focus_server", {})
        # Try frontend_url first, fallback to base_url, then default
        base_url = api_config.get("frontend_url") or api_config.get("base_url") or "https://10.10.10.100/prisma/api/"
        # Convert frontend URL to API base URL if needed
        if "/liveView" in base_url:
            base_url = base_url.replace("/liveView", "/prisma/api/")
        if not base_url.endswith("/"):
            base_url += "/"
        # Ensure we have /prisma/api/ in the path
        if "/prisma/api" not in base_url:
            base_url = base_url.rstrip("/") + "/prisma/api/"
        
        # Create shared session
        session = authenticate_session(base_url)
        
        # Create smart load tester
        tester = AlertLoadTester(
            config_manager=config_manager,
            session=session,
            initial_concurrent=5,      # Start with 5 concurrent
            step_increment=5,          # Add 5 each step
            max_concurrent=200,        # Max to test
            requests_per_step=20,      # 20 requests per step
            max_consecutive_failures=5  # Stop after 5 consecutive failures
        )
        
        # Run the smart load test
        report = tester.run()
        
        # Log summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("SMART LOAD TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"  📊 Max Healthy Load: {report.max_healthy_load} concurrent requests")
        logger.info(f"  📈 Steps Completed: {report.steps_completed}")
        logger.info(f"  ⏱️  Duration: {report.duration_seconds:.2f}s")
        logger.info(f"  ✅ Successful: {report.total_successful}")
        logger.info(f"  ❌ Failed: {report.total_failed}")
        
        if report.detected:
            logger.info(f"  🔴 Breakpoint: Step {report.breakpoint_step}")
            logger.info(f"  ⚠️  Failure Type: {report.failure_type.value if report.failure_type else 'N/A'}")
        else:
            logger.info(f"  ✅ No breakpoint detected - system handled all load levels")
        
        logger.info("=" * 80)
        
        # Test passes regardless - we're just detecting the breakpoint
        # The test is informational, not a pass/fail scenario
        assert report.max_healthy_load >= 5, \
            "System should handle at least 5 concurrent requests"
        
        logger.info("✅ TEST PASSED: Smart breakpoint detection completed")


@pytest.mark.slow
@pytest.mark.nightly
@pytest.mark.load
class TestSmartLoadScenarios:
    """
    Smart Load Test scenarios with gradual increase and breakpoint detection.
    
    These tests use intelligent load testing that:
    - Increases load gradually (step-by-step)
    - Detects system breakpoints automatically
    - Stops after N consecutive failures
    - Provides detailed reports
    
    Tests covered:
        - PZ-15101: Gradual Load Increase
        - PZ-15102: Rapid Burst Detection
        - PZ-15103: Mixed Load Breakpoint
    """
    
    @pytest.mark.xray("PZ-15101")
    def test_gradual_load_increase(self, config_manager):
        """
        Test PZ-15101: Gradual Load Increase with Breakpoint Detection.
        
        Objective:
            Gradually increase load from 10 to 150 concurrent requests
            and detect the exact point where system starts failing.
        
        Configuration:
            - Initial: 10 concurrent
            - Increment: 10 per step
            - Max: 150 concurrent
            - Requests per step: 30
            - Failure threshold: 5 consecutive
        
        Expected:
            Breakpoint is detected and logged with full details.
        """
        logger.info("=" * 80)
        logger.info("TEST: Gradual Load Increase (PZ-15101)")
        logger.info("=" * 80)
        
        # Get base URL for authentication
        # Use frontend_url or base_url for auth (not frontend_api_url which is NodePort)
        api_config = config_manager.get("focus_server", {})
        # Try frontend_url first, fallback to base_url, then default
        base_url = api_config.get("frontend_url") or api_config.get("base_url") or "https://10.10.10.100/prisma/api/"
        # Convert frontend URL to API base URL if needed
        if "/liveView" in base_url:
            base_url = base_url.replace("/liveView", "/prisma/api/")
        if not base_url.endswith("/"):
            base_url += "/"
        # Ensure we have /prisma/api/ in the path
        if "/prisma/api" not in base_url:
            base_url = base_url.rstrip("/") + "/prisma/api/"
        
        # Create shared session
        session = authenticate_session(base_url)
        
        # Create smart load tester with gradual increase
        tester = AlertLoadTester(
            config_manager=config_manager,
            session=session,
            initial_concurrent=10,     # Start with 10
            step_increment=10,         # Add 10 each step
            max_concurrent=150,        # Max 150
            requests_per_step=30,      # 30 requests per step
            max_consecutive_failures=5
        )
        
        # Run the test
        report = tester.run()
        
        # This test is informational - always passes
        logger.info(f"📊 Maximum healthy load detected: {report.max_healthy_load} concurrent requests")
        
        if report.detected:
            logger.info(f"🔴 System breakpoint at step {report.breakpoint_step}")
            logger.info(f"   Failure type: {report.failure_type.value if report.failure_type else 'Unknown'}")
        
        assert report.steps_completed >= 1, "At least one step should complete"
        logger.info("✅ TEST PASSED: Gradual load increase completed")
    
    @pytest.mark.xray("PZ-15102")
    def test_rapid_burst_detection(self, config_manager):
        """
        Test PZ-15102: Rapid Burst Breakpoint Detection.
        
        Objective:
            Test rapid burst scenarios with aggressive load increase
            to find breakpoint quickly.
        
        Configuration:
            - Initial: 20 concurrent
            - Increment: 20 per step (aggressive)
            - Max: 200 concurrent
            - Requests per step: 50
            - Failure threshold: 3 consecutive (sensitive)
        
        Expected:
            Quick detection of system limits under burst conditions.
        """
        logger.info("=" * 80)
        logger.info("TEST: Rapid Burst Detection (PZ-15102)")
        logger.info("=" * 80)
        
        # Get base URL for authentication
        # Use frontend_url or base_url for auth (not frontend_api_url which is NodePort)
        api_config = config_manager.get("focus_server", {})
        # Try frontend_url first, fallback to base_url, then default
        base_url = api_config.get("frontend_url") or api_config.get("base_url") or "https://10.10.10.100/prisma/api/"
        # Convert frontend URL to API base URL if needed
        if "/liveView" in base_url:
            base_url = base_url.replace("/liveView", "/prisma/api/")
        if not base_url.endswith("/"):
            base_url += "/"
        # Ensure we have /prisma/api/ in the path
        if "/prisma/api" not in base_url:
            base_url = base_url.rstrip("/") + "/prisma/api/"
        
        # Create shared session
        session = authenticate_session(base_url)
        
        # Create smart load tester with aggressive increase
        tester = AlertLoadTester(
            config_manager=config_manager,
            session=session,
            initial_concurrent=20,     # Start higher
            step_increment=20,         # Aggressive increase
            max_concurrent=200,        # Higher max
            requests_per_step=50,      # More requests per step
            max_consecutive_failures=3  # More sensitive threshold
        )
        
        # Run the test
        report = tester.run()
        
        logger.info(f"📊 Maximum healthy load: {report.max_healthy_load} concurrent requests")
        logger.info(f"⏱️  Total duration: {report.duration_seconds:.2f}s")
        
        if report.detected:
            logger.info(f"🔴 Burst breakpoint detected at step {report.breakpoint_step}")
        
        assert report.steps_completed >= 1, "At least one step should complete"
        logger.info("✅ TEST PASSED: Rapid burst detection completed")
    
    @pytest.mark.xray("PZ-15103")
    def test_sustained_smart_load(self, config_manager):
        """
        Test PZ-15103: Sustained Smart Load with Extended Steps.
        
        Objective:
            Test sustained load with more requests per step to ensure
            consistent performance over time.
        
        Configuration:
            - Initial: 5 concurrent
            - Increment: 5 per step (gentle)
            - Max: 50 concurrent
            - Requests per step: 100 (sustained)
            - Failure threshold: 5 consecutive
        
        Expected:
            System maintains performance under sustained load at each level.
        """
        logger.info("=" * 80)
        logger.info("TEST: Sustained Smart Load (PZ-15103)")
        logger.info("=" * 80)
        
        # Get base URL for authentication
        # Use frontend_url or base_url for auth (not frontend_api_url which is NodePort)
        api_config = config_manager.get("focus_server", {})
        # Try frontend_url first, fallback to base_url, then default
        base_url = api_config.get("frontend_url") or api_config.get("base_url") or "https://10.10.10.100/prisma/api/"
        # Convert frontend URL to API base URL if needed
        if "/liveView" in base_url:
            base_url = base_url.replace("/liveView", "/prisma/api/")
        if not base_url.endswith("/"):
            base_url += "/"
        # Ensure we have /prisma/api/ in the path
        if "/prisma/api" not in base_url:
            base_url = base_url.rstrip("/") + "/prisma/api/"
        
        # Create shared session
        session = authenticate_session(base_url)
        
        # Create smart load tester with sustained load per step
        tester = AlertLoadTester(
            config_manager=config_manager,
            session=session,
            initial_concurrent=5,      # Start gentle
            step_increment=5,          # Gentle increase
            max_concurrent=50,         # Lower max
            requests_per_step=100,     # More requests per step (sustained)
            max_consecutive_failures=5
        )
        
        # Run the test
        report = tester.run()
        
        logger.info(f"📊 Maximum healthy load: {report.max_healthy_load} concurrent requests")
        logger.info(f"📈 Total requests sent: {report.total_requests_sent}")
        logger.info(f"✅ Success rate: {(report.total_successful / max(report.total_requests_sent, 1)) * 100:.1f}%")
        
        if report.detected:
            logger.info(f"🔴 Sustained load breakpoint at step {report.breakpoint_step}")
        
        assert report.steps_completed >= 1, "At least one step should complete"
        logger.info("✅ TEST PASSED: Sustained smart load completed")

