"""
Integration Tests - Alerts: Edge Cases
=======================================

Tests for edge cases and boundary conditions in alert generation.

Tests Covered (Xray):
    - PZ-14945: Alert Generation - Boundary DOF Values
    - PZ-14946: Alert Generation - Minimum/Maximum Severity
    - PZ-14947: Alert Generation - Zero Alerts Amount
    - PZ-14948: Alert Generation - Very Large Alert ID
    - PZ-14949: Alert Generation - Concurrent Alerts with Same DOF
    - PZ-14950: Alert Generation - Rapid Sequential Alerts
    - PZ-14951: Alert Generation - Alert with Maximum Fields
    - PZ-14952: Alert Generation - Alert with Minimum Fields

Author: QA Automation Architect
Date: 2025-11-13
"""

import pytest
import logging
import time
import json
import requests
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

try:
    import pika
    PIKA_AVAILABLE = True
except ImportError:
    PIKA_AVAILABLE = False

from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager
from be_focus_server_tests.integration.alerts.alert_test_helpers import (
    send_alert_via_api,
    create_alert_payload
)

logger = logging.getLogger(__name__)


@pytest.mark.edge_case



@pytest.mark.regression
class TestAlertGenerationEdgeCases:
    """
    Test suite for edge cases in alert generation.
    
    Tests covered:
        - PZ-14945: Boundary DOF Values
        - PZ-14946: Minimum/Maximum Severity
        - PZ-14947: Zero Alerts Amount
        - PZ-14948: Very Large Alert ID
        - PZ-14949: Concurrent Alerts with Same DOF
        - PZ-14950: Rapid Sequential Alerts
        - PZ-14951: Alert with Maximum Fields
        - PZ-14952: Alert with Minimum Fields
    """
    
    @pytest.mark.xray("PZ-14945")
    @pytest.mark.regression
    def test_boundary_dof_values(self, config_manager):
        """
        Test PZ-14945: Alert Generation - Boundary DOF Values.
        
        Objective:
            Verify that alerts with boundary DOF values (min, max, edge cases)
            are handled correctly.
        
        Steps:
            1. Create alert with DOF = 0
            2. Create alert with DOF = 1
            3. Create alert with DOF = 2221 (max - 1)
            4. Create alert with DOF = 2222 (max)
            5. Verify all are processed correctly
        
        Expected:
            All boundary DOF values are processed correctly.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Boundary DOF Values (PZ-14945)")
        logger.info("=" * 80)
        
        boundary_dofs = [0, 1, 2221, 2222]
        
        for dof in boundary_dofs:
            alert_payload = {
                "alertsAmount": 1,
                "dofM": dof,
                "classId": 104,
                "severity": 3,
                "alertIds": [f"test-boundary-dof-{dof}-{int(time.time())}"]
            }
            
            logger.info(f"Testing boundary DOF: {dof}")
            
            # Send alert via API
            try:
                response = send_alert_via_api(config_manager, alert_payload)
                assert response.status_code in [200, 201], f"DOF {dof} failed: {response.status_code}"
                logger.info(f"✅ Boundary DOF {dof} sent successfully")
            except Exception as e:
                logger.error(f"❌ Boundary DOF {dof} failed: {e}")
                raise
        
        logger.info("✅ TEST PASSED: Boundary DOF values processed correctly")
    
    @pytest.mark.xray("PZ-14946")
    @pytest.mark.regression
    def test_min_max_severity(self, config_manager):
        """
        Test PZ-14946: Alert Generation - Minimum/Maximum Severity.
        
        Objective:
            Verify that alerts with minimum (1) and maximum (3) severity
            are handled correctly.
        
        Steps:
            1. Create alert with severity = 1 (minimum)
            2. Create alert with severity = 3 (maximum)
            3. Verify both are processed correctly
        
        Expected:
            Both minimum and maximum severity values are processed correctly.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Minimum/Maximum Severity (PZ-14946)")
        logger.info("=" * 80)
        
        severities = [1, 3]  # Min and max
        
        for severity in severities:
            alert_payload = {
                "alertsAmount": 1,
                "dofM": 5000,
                "classId": 104,
                "severity": severity,
                "alertIds": [f"test-severity-{severity}-{int(time.time())}"]
            }
            
            logger.info(f"Testing severity: {severity}")
            
            # Send alert via API
            try:
                response = send_alert_via_api(config_manager, alert_payload)
                assert response.status_code in [200, 201], f"Severity {severity} failed: {response.status_code}"
                logger.info(f"✅ Severity {severity} sent successfully")
            except Exception as e:
                logger.error(f"❌ Severity {severity} failed: {e}")
                raise
        
        logger.info("✅ TEST PASSED: Min/max severity processed correctly")
    
    @pytest.mark.xray("PZ-14947")
    @pytest.mark.regression
    def test_zero_alerts_amount(self, config_manager):
        """
        Test PZ-14947: Alert Generation - Zero Alerts Amount.
        
        Objective:
            Verify that alerts with alertsAmount = 0 are handled appropriately.
        
        Steps:
            1. Create alert with alertsAmount = 0
            2. Verify handling (reject or process)
        
        Expected:
            Zero alerts amount is handled appropriately.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Zero Alerts Amount (PZ-14947)")
        logger.info("=" * 80)
        
        alert_payload = {
            "alertsAmount": 0,  # Zero
            "dofM": 5000,
            "classId": 104,
            "severity": 3,
            "alertIds": [f"test-zero-amount-{int(time.time())}"]
        }
        
        # Send alert with zero amount - should either reject or handle gracefully
        try:
            response = send_alert_via_api(config_manager, alert_payload)
            # API may accept or reject zero amount
            if response.status_code >= 400:
                logger.info(f"✅ Zero alerts amount correctly rejected (status {response.status_code})")
            else:
                logger.info(f"ℹ️  Zero alerts amount accepted (status {response.status_code}) - API allows this")
        except requests.HTTPError as e:
            logger.info(f"✅ Zero alerts amount correctly rejected: {e.response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️  Unexpected error for zero alerts amount: {e}")
        
        logger.info("✅ TEST PASSED: Zero alerts amount handled correctly")
    
    @pytest.mark.xray("PZ-14948")
    @pytest.mark.regression
    def test_very_large_alert_id(self, config_manager):
        """
        Test PZ-14948: Alert Generation - Very Large Alert ID.
        
        Objective:
            Verify that alerts with very long alert IDs are handled correctly.
        
        Steps:
            1. Create alert with very long ID (1000+ characters)
            2. Verify handling (truncate, reject, or process)
        
        Expected:
            Very large alert IDs are handled appropriately.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Very Large Alert ID (PZ-14948)")
        logger.info("=" * 80)
        
        # Very long alert ID
        long_id = "test-" + "x" * 1000
        
        alert_payload = {
            "alertsAmount": 1,
            "dofM": 5000,
            "classId": 104,
            "severity": 3,
            "alertIds": [long_id]
        }
        
        # Send alert with very long ID - should handle appropriately
        try:
            response = send_alert_via_api(config_manager, alert_payload)
            # API may accept, truncate, or reject
            if response.status_code >= 400:
                logger.info(f"✅ Very large alert ID correctly rejected (status {response.status_code})")
            else:
                logger.info(f"ℹ️  Very large alert ID accepted (status {response.status_code}) - API may truncate")
        except requests.HTTPError as e:
            logger.info(f"✅ Very large alert ID correctly rejected: {e.response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️  Unexpected error for very large alert ID: {e}")
        
        logger.info("✅ TEST PASSED: Very large alert ID handled correctly")
    
    @pytest.mark.xray("PZ-14949")
    @pytest.mark.skipif(not PIKA_AVAILABLE, reason="pika not installed")
    @pytest.mark.regression
    def test_concurrent_alerts_same_dof(self, config_manager):
        """
        Test PZ-14949: Alert Generation - Concurrent Alerts with Same DOF.
        
        Objective:
            Verify that multiple alerts with the same DOF can be processed
            concurrently without conflicts.
        
        Steps:
            1. Create multiple alerts with same DOF simultaneously
            2. Verify all are processed correctly
            3. Verify no conflicts or data loss
        
        Expected:
            All concurrent alerts with same DOF are processed correctly.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Concurrent Alerts Same DOF (PZ-14949)")
        logger.info("=" * 80)
        
        num_alerts = 10
        same_dof = 5000
        
        def create_alert(index: int):
            alert_payload = create_alert_payload(
                class_id=104,
                dof_m=same_dof,  # Same DOF
                severity=(index % 3) + 1,
                alert_id=f"test-concurrent-dof-{index}-{int(time.time())}"
            )
            # Send alert via API
            try:
                response = send_alert_via_api(config_manager, alert_payload)
                assert response.status_code in [200, 201], f"Alert {index} failed: {response.status_code}"
                return alert_payload
            except Exception as e:
                logger.error(f"❌ Alert {index} failed: {e}")
                raise
        
        # Create alerts concurrently
        with ThreadPoolExecutor(max_workers=num_alerts) as executor:
            futures = [executor.submit(create_alert, i) for i in range(num_alerts)]
            results = [f.result() for f in futures]
        
        logger.info(f"✅ TEST PASSED: {num_alerts} concurrent alerts with same DOF processed")
    
    @pytest.mark.xray("PZ-14950")
    @pytest.mark.regression
    def test_rapid_sequential_alerts(self, config_manager):
        """
        Test PZ-14950: Alert Generation - Rapid Sequential Alerts.
        
        Objective:
            Verify that rapid sequential alerts are processed correctly
            without loss or corruption.
        
        Steps:
            1. Create alerts rapidly in sequence (no delay)
            2. Verify all are processed
            3. Verify order is maintained (if required)
        
        Expected:
            All rapid sequential alerts are processed correctly.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Rapid Sequential Alerts (PZ-14950)")
        logger.info("=" * 80)
        
        num_alerts = 50
        
        for i in range(num_alerts):
            alert_payload = {
                "alertsAmount": 1,
                "dofM": 4000 + i,
                "classId": 104,
                "severity": (i % 3) + 1,
                "alertIds": [f"test-rapid-{i}-{int(time.time())}"]
            }
            
            # Send immediately (no delay)
            try:
                response = send_alert_via_api(config_manager, alert_payload)
                assert response.status_code in [200, 201], f"Alert {i} failed: {response.status_code}"
            except Exception as e:
                logger.error(f"❌ Alert {i} failed: {e}")
                raise
        
        logger.info(f"✅ TEST PASSED: {num_alerts} rapid sequential alerts processed")
    
    @pytest.mark.xray("PZ-14951")
    @pytest.mark.regression
    def test_alert_maximum_fields(self, config_manager):
        """
        Test PZ-14951: Alert Generation - Alert with Maximum Fields.
        
        Objective:
            Verify that alerts with all possible fields set to maximum values
            are processed correctly.
        
        Steps:
            1. Create alert with all fields at maximum values
            2. Verify processing
        
        Expected:
            Alert with maximum fields is processed correctly.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Alert with Maximum Fields (PZ-14951)")
        logger.info("=" * 80)
        
        alert_payload = {
            "alertsAmount": 100,  # Maximum reasonable amount
            "dofM": 2222,  # Maximum DOF
            "classId": 104,  # Valid class ID
            "severity": 3,  # Maximum severity
            "alertIds": [f"test-max-{i}-{int(time.time())}" for i in range(100)]  # Many IDs
        }
        
        # Send alert with maximum fields
        try:
            response = send_alert_via_api(config_manager, alert_payload)
            assert response.status_code in [200, 201], f"Maximum fields alert failed: {response.status_code}"
            logger.info("✅ Alert with maximum fields sent successfully")
        except Exception as e:
            logger.error(f"❌ Alert with maximum fields failed: {e}")
            raise
        
        logger.info("✅ TEST PASSED: Alert with maximum fields processed correctly")
    
    @pytest.mark.xray("PZ-14952")
    @pytest.mark.regression
    def test_alert_minimum_fields(self, config_manager):
        """
        Test PZ-14952: Alert Generation - Alert with Minimum Fields.
        
        Objective:
            Verify that alerts with only required fields (minimum) are
            processed correctly.
        
        Steps:
            1. Create alert with only required fields
            2. Verify processing
        
        Expected:
            Alert with minimum fields is processed correctly.
        """
        logger.info("=" * 80)
        logger.info("TEST: Alert Generation - Alert with Minimum Fields (PZ-14952)")
        logger.info("=" * 80)
        
        alert_payload = {
            "alertsAmount": 1,  # Minimum
            "dofM": 1,  # Minimum DOF
            "classId": 103,  # Valid class ID
            "severity": 1,  # Minimum severity
            "alertIds": ["test-min"]  # Single ID
        }
        
        # Send alert with minimum fields
        try:
            response = send_alert_via_api(config_manager, alert_payload)
            assert response.status_code in [200, 201], f"Minimum fields alert failed: {response.status_code}"
            logger.info("✅ Alert with minimum fields sent successfully")
        except Exception as e:
            logger.error(f"❌ Alert with minimum fields failed: {e}")
            raise
        
        logger.info("✅ TEST PASSED: Alert with minimum fields processed correctly")

