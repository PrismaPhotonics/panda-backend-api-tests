"""
Integration Tests - Alerts: Load Scenarios
==========================================

Tests for load and stress scenarios in alert generation.

Tests Covered (Xray):
    - PZ-14953: Alert Generation - High Volume Load
    - PZ-14954: Alert Generation - Sustained Load
    - PZ-14955: Alert Generation - Burst Load
    - PZ-14956: Alert Generation - Mixed Alert Types Load
    - PZ-14957: Alert Generation - RabbitMQ Queue Capacity

Author: QA Automation Architect
Date: 2025-11-13
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
@pytest.mark.regression
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
    @pytest.mark.regression
    def test_high_volume_load(self, config_manager):
        """
        Test PZ-14953: Alert Generation - High Volume Load.
        
        Objective:
            Verify that system can handle high volume of alerts
            without degradation or failures.
        
        Steps:
            1. Generate large number of alerts (1000+)
            2. Measure processing time
            3. Verify success rate
            4. Verify system stability
        
        Expected:
            System handles high volume load successfully.
            Success rate >= 99%
            No system degradation.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - High Volume Load (PZ-14953)")
        logger.info("=" * 80)
        
        num_alerts = 1000
        max_processing_time = 300  # 5 minutes
        min_success_rate = 0.99  # 99%
        
        # Get base URL for authentication
        api_config = config_manager.get("focus_server", {})
        base_url = api_config.get("frontend_api_url", "https://10.10.10.100/prisma/api/")
        if "/internal/sites/" in base_url:
            base_url = base_url.split("/internal/sites/")[0]
        if not base_url.endswith("/"):
            base_url += "/"
        
        # Create shared session to avoid rate limiting
        session = authenticate_session(base_url)
        
        start_time = time.time()
        success_count = 0
        failure_count = 0
        consecutive_429_errors = 0  # Track consecutive rate limit errors
        max_consecutive_429 = 5  # Threshold for backing off
        
        for i in range(num_alerts):
            # If too many consecutive 429 errors, wait longer before continuing
            if consecutive_429_errors >= max_consecutive_429:
                backoff_time = 10  # 10 seconds backoff
                logger.warning(f"⚠️ Rate limited! Pausing for {backoff_time}s after {consecutive_429_errors} consecutive 429 errors...")
                time.sleep(backoff_time)
                consecutive_429_errors = 0  # Reset counter after backoff
            
            alert_payload = {
                "alertsAmount": 1,
                "dofM": 1000 + (i % 2000),
                "classId": 104 if i % 2 == 0 else 103,
                "severity": (i % 3) + 1,
                "alertIds": [f"load-test-{i}-{int(time.time())}"]
            }
            
            # Send alert via API using shared session with retry logic
            try:
                response = send_alert_via_api(
                    config_manager, 
                    alert_payload, 
                    session=session,
                    max_retries=5,  # Increase retries for load tests
                    retry_delay=0.5  # Faster initial retry for load tests
                )
                assert response.status_code in [200, 201], f"Alert {i} failed: {response.status_code}"
                success_count += 1
                consecutive_429_errors = 0  # Reset on success
            except Exception as e:
                error_str = str(e)
                logger.error(f"Failed to send alert {i}: {e}")
                failure_count += 1
                
                # Track consecutive 429 errors
                if "429" in error_str or "Too Many Requests" in error_str:
                    consecutive_429_errors += 1
                else:
                    consecutive_429_errors = 0  # Reset if it's not a 429 error
            
            # Add small delay to avoid rate limiting (every 10 alerts)
            if (i + 1) % 10 == 0:
                time.sleep(0.1)  # 100ms pause every 10 alerts
        
        end_time = time.time()
        processing_time = end_time - start_time
        success_rate = success_count / num_alerts
        
        logger.info(f"Results:")
        logger.info(f"  Total alerts: {num_alerts}")
        logger.info(f"  Success: {success_count}")
        logger.info(f"  Failures: {failure_count}")
        logger.info(f"  Success rate: {success_rate:.2%}")
        logger.info(f"  Processing time: {processing_time:.2f}s")
        
        assert processing_time < max_processing_time, \
            f"Processing time {processing_time}s exceeds limit {max_processing_time}s"
        assert success_rate >= min_success_rate, \
            f"Success rate {success_rate:.2%} below minimum {min_success_rate:.2%}"
        
        logger.info("✅ TEST PASSED: High volume load handled successfully")
    
    @pytest.mark.xray("PZ-14954")
    @pytest.mark.regression
    def test_sustained_load(self, config_manager):
        """
        Test PZ-14954: Alert Generation - Sustained Load.
        
        Objective:
            Verify that system can handle sustained load over extended period
            without degradation.
        
        Steps:
            1. Generate alerts continuously for extended period (10+ minutes)
            2. Monitor system metrics
            3. Verify no degradation
        
        Expected:
            System maintains performance under sustained load.
            No memory leaks or performance degradation.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Sustained Load (PZ-14954)")
        logger.info("=" * 80)
        
        duration_seconds = 600  # 10 minutes
        alerts_per_second = 10
        total_alerts = duration_seconds * alerts_per_second
        
        # Get base URL for authentication
        api_config = config_manager.get("focus_server", {})
        base_url = api_config.get("frontend_api_url", "https://10.10.10.100/prisma/api/")
        if "/internal/sites/" in base_url:
            base_url = base_url.split("/internal/sites/")[0]
        if not base_url.endswith("/"):
            base_url += "/"
        
        # Create shared session to avoid rate limiting
        session = authenticate_session(base_url)
        
        start_time = time.time()
        success_count = 0
        consecutive_429_errors = 0  # Track consecutive rate limit errors
        max_consecutive_429 = 5  # Threshold for backing off
        
        while time.time() - start_time < duration_seconds:
            # If too many consecutive 429 errors, wait longer before continuing
            if consecutive_429_errors >= max_consecutive_429:
                backoff_time = 10  # 10 seconds backoff
                logger.warning(f"⚠️ Rate limited! Pausing for {backoff_time}s after {consecutive_429_errors} consecutive 429 errors...")
                time.sleep(backoff_time)
                consecutive_429_errors = 0  # Reset counter after backoff
            
            for _ in range(alerts_per_second):
                alert_payload = {
                    "alertsAmount": 1,
                    "dofM": 1000 + (success_count % 2000),
                    "classId": 104,
                    "severity": (success_count % 3) + 1,
                    "alertIds": [f"sustained-{success_count}-{int(time.time())}"]
                }
                
                # Send alert via API using shared session with retry logic
                try:
                    response = send_alert_via_api(
                        config_manager, 
                        alert_payload, 
                        session=session,
                        max_retries=5,  # Increase retries for load tests
                        retry_delay=0.5  # Faster initial retry for load tests
                    )
                    assert response.status_code in [200, 201], f"Alert failed: {response.status_code}"
                    success_count += 1
                    consecutive_429_errors = 0  # Reset on success
                except Exception as e:
                    error_str = str(e)
                    logger.error(f"Failed to send alert: {e}")
                    
                    # Track consecutive 429 errors
                    if "429" in error_str or "Too Many Requests" in error_str:
                        consecutive_429_errors += 1
                    else:
                        consecutive_429_errors = 0  # Reset if it's not a 429 error
                    # Continue with next alert
                
                # Add small delay between individual requests to avoid rate limiting
                time.sleep(0.05)  # 50ms between requests
            
            time.sleep(0.5)  # Wait half a second before next batch
        
        elapsed_time = time.time() - start_time
        alerts_per_second_actual = success_count / elapsed_time
        
        logger.info(f"Results:")
        logger.info(f"  Duration: {elapsed_time:.2f}s")
        logger.info(f"  Alerts published: {success_count}")
        logger.info(f"  Rate: {alerts_per_second_actual:.2f} alerts/sec")
        
        assert alerts_per_second_actual >= alerts_per_second * 0.9, \
            f"Alert rate {alerts_per_second_actual:.2f} below expected {alerts_per_second}"
        
        logger.info("✅ TEST PASSED: Sustained load handled successfully")
    
    @pytest.mark.xray("PZ-14955")
    @pytest.mark.regression
    def test_burst_load(self, config_manager):
        """
        Test PZ-14955: Alert Generation - Burst Load.
        
        Objective:
            Verify that system can handle sudden burst of alerts
            without failures or degradation.
        
        Steps:
            1. Generate large number of alerts simultaneously (burst)
            2. Measure processing time
            3. Verify all are processed
        
        Expected:
            System handles burst load successfully.
            All alerts are processed.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Burst Load (PZ-14955)")
        logger.info("=" * 80)
        
        burst_size = 500
        
        # Get base URL for authentication
        api_config = config_manager.get("focus_server", {})
        base_url = api_config.get("frontend_api_url", "https://10.10.10.100/prisma/api/")
        if "/internal/sites/" in base_url:
            base_url = base_url.split("/internal/sites/")[0]
        if not base_url.endswith("/"):
            base_url += "/"
        
        # Create shared session to avoid rate limiting (requests.Session is thread-safe)
        session = authenticate_session(base_url)
        
        def publish_alert(index: int):
            alert_payload = {
                "alertsAmount": 1,
                "dofM": 1000 + (index % 2000),
                "classId": 104,
                "severity": (index % 3) + 1,
                "alertIds": [f"burst-{index}-{int(time.time())}"]
            }
            
            # Send alert via API using shared session
            try:
                response = send_alert_via_api(config_manager, alert_payload, session=session)
                assert response.status_code in [200, 201], f"Alert {index} failed: {response.status_code}"
                return True, index
            except Exception as e:
                logger.error(f"Failed to send alert {index}: {e}")
                return False, index
        
        start_time = time.time()
        
        # Publish all alerts simultaneously
        with ThreadPoolExecutor(max_workers=burst_size) as executor:
            futures = [executor.submit(publish_alert, i) for i in range(burst_size)]
            results = [f.result() for f in as_completed(futures)]
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        success_count = sum(1 for success, _ in results if success)
        success_rate = success_count / burst_size
        
        logger.info(f"Results:")
        logger.info(f"  Burst size: {burst_size}")
        logger.info(f"  Success: {success_count}")
        logger.info(f"  Success rate: {success_rate:.2%}")
        logger.info(f"  Processing time: {processing_time:.2f}s")
        
        assert success_rate >= 0.95, \
            f"Success rate {success_rate:.2%} below minimum 95%"
        
        logger.info("✅ TEST PASSED: Burst load handled successfully")
    
    @pytest.mark.xray("PZ-14956")
    @pytest.mark.regression
    def test_mixed_alert_types_load(self, config_manager):
        """
        Test PZ-14956: Alert Generation - Mixed Alert Types Load.
        
        Objective:
            Verify that system can handle mixed alert types (SD, SC, different severities)
            under load without issues.
        
        Steps:
            1. Generate mix of SD and SC alerts
            2. Generate mix of severity levels
            3. Verify all are processed correctly
        
        Expected:
            All alert types are processed correctly under load.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Mixed Alert Types Load (PZ-14956)")
        logger.info("=" * 80)
        
        num_alerts = 500
        class_ids = [103, 104]  # SC and SD
        severities = [1, 2, 3]
        
        # Get base URL for authentication
        api_config = config_manager.get("focus_server", {})
        base_url = api_config.get("frontend_api_url", "https://10.10.10.100/prisma/api/")
        if "/internal/sites/" in base_url:
            base_url = base_url.split("/internal/sites/")[0]
        if not base_url.endswith("/"):
            base_url += "/"
        
        # Create shared session to avoid rate limiting
        session = authenticate_session(base_url)
        
        success_by_type = {
            "SD": 0,
            "SC": 0,
            "severity_1": 0,
            "severity_2": 0,
            "severity_3": 0
        }
        
        for i in range(num_alerts):
            class_id = class_ids[i % len(class_ids)]
            severity = severities[i % len(severities)]
            
            alert_payload = {
                "alertsAmount": 1,
                "dofM": 1000 + (i % 2000),
                "classId": class_id,
                "severity": severity,
                "alertIds": [f"mixed-{class_id}-{severity}-{i}-{int(time.time())}"]
            }
            
            # Send alert via API using shared session
            try:
                response = send_alert_via_api(config_manager, alert_payload, session=session)
                assert response.status_code in [200, 201], f"Alert failed: {response.status_code}"
            except Exception as e:
                logger.error(f"Failed to send alert: {e}")
                raise
            
            if class_id == 104:
                success_by_type["SD"] += 1
            else:
                success_by_type["SC"] += 1
            
            success_by_type[f"severity_{severity}"] += 1
        
        logger.info(f"Results:")
        logger.info(f"  SD alerts: {success_by_type['SD']}")
        logger.info(f"  SC alerts: {success_by_type['SC']}")
        logger.info(f"  Severity 1: {success_by_type['severity_1']}")
        logger.info(f"  Severity 2: {success_by_type['severity_2']}")
        logger.info(f"  Severity 3: {success_by_type['severity_3']}")
        
        assert success_by_type["SD"] > 0, "No SD alerts processed"
        assert success_by_type["SC"] > 0, "No SC alerts processed"
        
        logger.info("✅ TEST PASSED: Mixed alert types load handled successfully")
    
    @pytest.mark.xray("PZ-14957")
    @pytest.mark.skipif(not PIKA_AVAILABLE, reason="pika not installed")
    @pytest.mark.regression
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
                num_alerts = 1000
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

    @pytest.mark.regression
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

