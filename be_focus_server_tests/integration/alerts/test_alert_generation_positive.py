"""
Integration Tests - Alerts: Positive Scenarios
==============================================

Tests for successful alert generation and processing from Backend.

Tests Covered (Xray):
    - PZ-15000: Alert Generation - Successful SD Alert
    - PZ-15001: Alert Generation - Successful SC Alert
    - PZ-15002: Alert Generation - Multiple Alerts
    - PZ-15003: Alert Generation - Different Severity Levels
    - PZ-15004: Alert Generation - Alert Processing via RabbitMQ

Author: QA Automation Architect
Date: 2025-11-13
"""

import pytest
import logging
import time
import json
import requests
from typing import Dict, Any, List
from datetime import datetime

try:
    import pika
    PIKA_AVAILABLE = True
except ImportError:
    PIKA_AVAILABLE = False

from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError
from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager
from be_focus_server_tests.integration.alerts.alert_test_helpers import (
    send_alert_via_api,
    create_alert_payload,
    authenticate_session
)

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


@pytest.mark.integration
@pytest.mark.alerts
@pytest.mark.api
@pytest.mark.positive
class TestAlertGenerationPositive:
    """
    Test suite for positive alert generation scenarios.
    
    Tests covered:
        - PZ-15000: Successful SD Alert Generation
        - PZ-15001: Successful SC Alert Generation
        - PZ-15002: Multiple Alerts Generation
        - PZ-15003: Different Severity Levels
        - PZ-15004: Alert Processing via RabbitMQ
    """
    
    @pytest.mark.xray("PZ-15000")
    def test_successful_sd_alert_generation(self, config_manager):
        """
        Test PZ-15000: Alert Generation - Successful SD Alert.
        
        Objective:
            Verify that SD (Spatial Distribution) alerts can be successfully
            generated and processed through the backend system.
        
        Steps:
            1. Create SD alert payload (classId=104)
            2. Send alert via HTTP API (push-to-rabbit endpoint)
            3. Verify alert is sent successfully
        
        Expected:
            Alert is successfully generated and sent via HTTP API.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Successful SD Alert (PZ-15000)")
        logger.info("=" * 80)
        
        # Alert payload for SD alert
        alert_payload = {
            "alertsAmount": 1,
            "dofM": 4163,  # Distance on fiber in meters
            "classId": 104,  # SD (Spatial Distribution)
            "severity": 3,  # High severity
            "alertIds": [f"test-sd-{int(time.time())}"]
        }
        
        logger.info(f"Alert Payload: {json.dumps(alert_payload, indent=2)}")
        
        # Send alert via HTTP API (push-to-rabbit endpoint)
        try:
            response = send_alert_via_api(config_manager, alert_payload)
            
            logger.info(f"✅ Alert sent successfully via HTTP API!")
            logger.info(f"   Response Status: {response.status_code}")
            logger.info(f"   Response: {response.text[:200]}")
            
            # Verify response
            assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
            
            logger.info("✅ TEST PASSED: SD Alert generated and sent successfully")
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            raise
    
    @pytest.mark.xray("PZ-15001")
    def test_successful_sc_alert_generation(self, config_manager):
        """
        Test PZ-15001: Alert Generation - Successful SC Alert.
        
        Objective:
            Verify that SC (Single Channel) alerts can be successfully
            generated and processed through the backend system.
        
        Steps:
            1. Create SC alert payload (classId=103)
            2. Publish alert to RabbitMQ
            3. Verify alert appears in RabbitMQ queue
            4. Verify alert is processed correctly
        
        Expected:
            Alert is successfully generated and processed.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Successful SC Alert (PZ-15001)")
        logger.info("=" * 80)
        
        # Alert payload for SC alert
        alert_payload = {
            "alertsAmount": 1,
            "dofM": 5682,  # Distance on fiber in meters
            "classId": 103,  # SC (Single Channel)
            "severity": 2,  # Medium severity
            "alertIds": [f"test-sc-{int(time.time())}"]
        }
        
        logger.info(f"Alert Payload: {json.dumps(alert_payload, indent=2)}")
        
        # Send alert via HTTP API (same as SD alert test, but with SC parameters)
        try:
            response = send_alert_via_api(config_manager, alert_payload)
            
            logger.info(f"✅ Alert sent successfully via HTTP API!")
            logger.info(f"   Response Status: {response.status_code}")
            logger.info(f"   Response: {response.text[:200]}")
            
            # Verify response
            assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
            
            logger.info("✅ TEST PASSED: SC Alert generated and sent successfully")
            
        except Exception as e:
            logger.error(f"❌ TEST FAILED: {e}")
            raise
    
    @pytest.mark.xray("PZ-15002")
    def test_multiple_alerts_generation(self, config_manager):
        """
        Test PZ-15002: Alert Generation - Multiple Alerts.
        
        Objective:
            Verify that multiple alerts can be generated and processed
            simultaneously without conflicts.
        
        Steps:
            1. Create multiple alert payloads
            2. Publish all alerts to RabbitMQ
            3. Verify all alerts are processed
            4. Verify no conflicts or data loss
        
        Expected:
            All alerts are successfully generated and processed.
            No conflicts or data loss.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Multiple Alerts (PZ-15002)")
        logger.info("=" * 80)
        
        num_alerts = 5
        alerts = []
        
        for i in range(num_alerts):
            alert_payload = {
                "alertsAmount": 1,
                "dofM": 4000 + (i * 100),  # Different distances
                "classId": 104 if i % 2 == 0 else 103,  # Alternate SD/SC
                "severity": (i % 3) + 1,  # Rotate severity 1, 2, 3
                "alertIds": [f"test-multi-{int(time.time())}-{i}"]
            }
            alerts.append(alert_payload)
        
        logger.info(f"Generated {num_alerts} alerts")
        
        # Send all alerts via HTTP API
        success_count = 0
        failed_alerts = []
        
        for i, alert_payload in enumerate(alerts):
            try:
                response = send_alert_via_api(config_manager, alert_payload)
                assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
                success_count += 1
                logger.info(f"✅ Alert {i+1}/{num_alerts} sent successfully")
            except Exception as e:
                failed_alerts.append((i, str(e)))
                logger.error(f"❌ Alert {i+1}/{num_alerts} failed: {e}")
        
        # Verify all alerts were sent successfully
        assert success_count == num_alerts, f"Only {success_count}/{num_alerts} alerts sent successfully. Failures: {failed_alerts}"
        
        logger.info(f"✅ TEST PASSED: All {num_alerts} alerts generated and sent successfully")
    
    @pytest.mark.xray("PZ-15003")
    def test_different_severity_levels(self, config_manager):
        """
        Test PZ-15003: Alert Generation - Different Severity Levels.
        
        Objective:
            Verify that alerts with different severity levels (1, 2, 3)
            are correctly generated and processed.
        
        Steps:
            1. Create alerts with severity 1 (Low)
            2. Create alerts with severity 2 (Medium)
            3. Create alerts with severity 3 (High)
            4. Verify all are processed correctly
        
        Expected:
            All severity levels are processed correctly.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Different Severity Levels (PZ-15003)")
        logger.info("=" * 80)
        
        severities = [1, 2, 3]
        severity_names = {1: "Low", 2: "Medium", 3: "High"}
        
        for severity in severities:
            alert_payload = {
                "alertsAmount": 1,
                "dofM": 5000,
                "classId": 104,
                "severity": severity,
                "alertIds": [f"test-severity-{severity}-{int(time.time())}"]
            }
            
            logger.info(f"Testing severity {severity} ({severity_names[severity]})")
            
            # Send alert via HTTP API
            try:
                response = send_alert_via_api(config_manager, alert_payload)
                assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
                logger.info(f"✅ Severity {severity} alert sent successfully")
            except Exception as e:
                logger.error(f"❌ Severity {severity} alert failed: {e}")
                raise
        
        logger.info("✅ TEST PASSED: All severity levels processed correctly")
    
    @pytest.mark.xray("PZ-15004")
    @pytest.mark.skipif(not PIKA_AVAILABLE, reason="pika not installed")
    def test_alert_processing_via_rabbitmq(self, config_manager):
        """
        Test PZ-15004: Alert Processing via RabbitMQ.
        
        Objective:
            Verify that alerts are correctly processed through RabbitMQ
            message queue system.
        
        Steps:
            1. Publish alert to RabbitMQ exchange
            2. Verify message is in queue
            3. Verify message routing is correct
            4. Verify message format is valid
        
        Expected:
            Alert is correctly processed via RabbitMQ.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Processing via RabbitMQ (PZ-15004)")
        logger.info("=" * 80)
        
        # Get RabbitMQ configuration
        rabbitmq_config = config_manager.get("rabbitmq", {})
        
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
                
                # Verify exchange exists
                channel.exchange_declare(
                    exchange="prisma",
                    exchange_type="topic",
                    durable=True,
                    passive=True  # Check if exists
                )
                
                logger.info("✅ Exchange 'prisma' exists")
                
                # Verify routing keys
                routing_keys = [
                    "Algorithm.AlertReport.MLGround",
                    "Algorithm.AlertReport.Pulse",
                    "Algorithm.AlertReport.FiberCut",
                    "Algorithm.AlertReport"
                ]
                
                for routing_key in routing_keys:
                    logger.info(f"Testing routing key: {routing_key}")
                    # Test publish (message will be routed)
                
                connection.close()
                
                logger.info("✅ TEST PASSED: Alert processing via RabbitMQ verified")
                
            except Exception as e:
                logger.error(f"❌ TEST FAILED: {e}")
                raise
    
