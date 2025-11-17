"""
Integration Test - Alert Logs Investigation
============================================

This test investigates where and how to see alert logs in Kubernetes.

It:
1. Lists all pods
2. Checks Focus Server logs
3. Checks RabbitMQ logs
4. Sends a test alert
5. Monitors logs after sending
6. Creates a detailed report

Run with:
    pytest be_focus_server_tests/integration/alerts/test_alert_logs_investigation.py -v -s

Author: QA Automation Architect
Date: 2025-11-13
"""

import pytest
import logging
import time
import json
from datetime import datetime

from src.infrastructure.kubernetes_manager import KubernetesManager
from src.infrastructure.ssh_manager import SSHManager
from config.config_manager import ConfigManager
import requests

logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.alerts
@pytest.mark.api
@pytest.mark.investigation
class TestAlertLogsInvestigation:
    """
    Investigation test for alert logs in Kubernetes.
    
    This test helps understand where and how to see alert logs.
    """
    
    def test_investigate_alert_logs(self, config_manager):
        """
        Investigate alert logs in Kubernetes.
        
        This test:
        1. Lists all pods
        2. Checks Focus Server logs
        3. Checks RabbitMQ logs
        4. Sends a test alert
        5. Monitors logs after sending
        """
        logger.info("=" * 80)
        logger.info("INVESTIGATION: Alert Logs in Kubernetes")
        logger.info("=" * 80)
        logger.info(f"Timestamp: {datetime.now().isoformat()}\n")
        
        # Initialize managers
        k8s_manager = KubernetesManager(config_manager)
        
        # Step 1: List all pods
        logger.info("\n" + "=" * 80)
        logger.info("Step 1: Listing All Pods")
        logger.info("=" * 80 + "\n")
        
        pods = k8s_manager.get_pods(namespace="panda")
        logger.info(f"Found {len(pods)} pods in namespace 'panda':\n")
        
        relevant_pods = {
            "focus-server": [],
            "rabbitmq": [],
            "grpc-job": [],
            "mongodb": [],
        }
        
        for pod in pods:
            name = pod['name']
            status = pod['status']
            
            if 'focus-server' in name:
                relevant_pods["focus-server"].append((name, status))
            elif 'rabbitmq' in name:
                relevant_pods["rabbitmq"].append((name, status))
            elif 'grpc-job' in name:
                relevant_pods["grpc-job"].append((name, status))
            elif 'mongodb' in name:
                relevant_pods["mongodb"].append((name, status))
        
        for category, pod_list in relevant_pods.items():
            if pod_list:
                logger.info(f"{category.upper()}:")
                for name, status in pod_list:
                    logger.info(f"  - {name} ({status})")
        
        # Step 2: Check Focus Server logs
        logger.info("\n" + "=" * 80)
        logger.info("Step 2: Checking Focus Server Logs")
        logger.info("=" * 80 + "\n")
        
        if relevant_pods["focus-server"]:
            pod_name = relevant_pods["focus-server"][0][0]
            logger.info(f"Checking logs for: {pod_name}\n")
            
            try:
                logs = k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=500)
                
                keywords = [
                    "push-to-rabbit",
                    "alert",
                    "rabbit",
                    "queue",
                    "api",
                    "POST",
                    "prisma-210-1000"
                ]
                
                logger.info("Searching for keywords in logs:")
                found_keywords = {}
                for keyword in keywords:
                    matching_lines = [line for line in logs.split('\n') if keyword.lower() in line.lower()]
                    if matching_lines:
                        found_keywords[keyword] = matching_lines[-10:]
                        logger.info(f"  ✅ '{keyword}': Found {len(matching_lines)} lines")
                    else:
                        logger.info(f"  ❌ '{keyword}': Not found")
                
                if found_keywords:
                    logger.info("\nSample log lines:")
                    for keyword, lines in found_keywords.items():
                        logger.info(f"\n  {keyword}:")
                        for line in lines[-3:]:
                            logger.info(f"    {line[:150]}")
                else:
                    logger.warning("\n⚠️  No alert-related keywords found in Focus Server logs")
                    logger.info("\nLast 20 lines of logs:")
                    for line in logs.split('\n')[-20:]:
                        logger.info(f"  {line}")
                        
            except Exception as e:
                logger.error(f"❌ Error getting Focus Server logs: {e}")
        
        # Step 3: Check RabbitMQ logs
        logger.info("\n" + "=" * 80)
        logger.info("Step 3: Checking RabbitMQ Logs")
        logger.info("=" * 80 + "\n")
        
        if relevant_pods["rabbitmq"]:
            pod_name = relevant_pods["rabbitmq"][0][0]
            logger.info(f"Checking logs for: {pod_name}\n")
            
            try:
                logs = k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=500)
                
                keywords = [
                    "publish",
                    "consume",
                    "exchange",
                    "routing",
                    "prisma",
                    "Algorithm.AlertReport"
                ]
                
                logger.info("Searching for keywords in logs:")
                found_keywords = {}
                for keyword in keywords:
                    matching_lines = [line for line in logs.split('\n') if keyword.lower() in line.lower()]
                    if matching_lines:
                        found_keywords[keyword] = matching_lines[-10:]
                        logger.info(f"  ✅ '{keyword}': Found {len(matching_lines)} lines")
                    else:
                        logger.info(f"  ❌ '{keyword}': Not found")
                
                if found_keywords:
                    logger.info("\nSample log lines:")
                    for keyword, lines in found_keywords.items():
                        logger.info(f"\n  {keyword}:")
                        for line in lines[-3:]:
                            logger.info(f"    {line[:150]}")
                else:
                    logger.warning("\n⚠️  No alert-related keywords found in RabbitMQ logs")
                    logger.info("\nLast 20 lines of logs:")
                    for line in logs.split('\n')[-20:]:
                        logger.info(f"  {line}")
                        
            except Exception as e:
                logger.error(f"❌ Error getting RabbitMQ logs: {e}")
        
        # Step 4: Check RabbitMQ queues/exchanges
        logger.info("\n" + "=" * 80)
        logger.info("Step 4: Checking RabbitMQ Queues and Exchanges")
        logger.info("=" * 80 + "\n")
        
        if relevant_pods["rabbitmq"]:
            pod_name = relevant_pods["rabbitmq"][0][0]
            logger.info(f"Checking RabbitMQ queues/exchanges in: {pod_name}\n")
            
            try:
                ssh_manager = SSHManager(config_manager)
                ssh_manager.connect()
                
                # Check exchanges
                cmd = f"kubectl exec -n panda {pod_name} -- rabbitmqctl list_exchanges name type"
                result = ssh_manager.execute_command(cmd, timeout=30)
                if result["success"]:
                    logger.info("Exchanges:")
                    logger.info(result["stdout"])
                else:
                    logger.warning(f"⚠️  Could not list exchanges: {result['stderr']}")
                
                # Check queues
                cmd = f"kubectl exec -n panda {pod_name} -- rabbitmqctl list_queues name messages"
                result = ssh_manager.execute_command(cmd, timeout=30)
                if result["success"]:
                    logger.info("\nQueues:")
                    logger.info(result["stdout"])
                else:
                    logger.warning(f"⚠️  Could not list queues: {result['stderr']}")
                
                # Check bindings
                cmd = f"kubectl exec -n panda {pod_name} -- rabbitmqctl list_bindings exchange_name routing_key queue_name"
                result = ssh_manager.execute_command(cmd, timeout=30)
                if result["success"]:
                    logger.info("\nBindings:")
                    logger.info(result["stdout"])
                else:
                    logger.warning(f"⚠️  Could not list bindings: {result['stderr']}")
                
                ssh_manager.disconnect()
                
            except Exception as e:
                logger.error(f"❌ Error checking RabbitMQ: {e}")
        
        # Step 5: Send test alert and monitor logs
        logger.info("\n" + "=" * 80)
        logger.info("Step 5: Sending Test Alert and Monitoring Logs")
        logger.info("=" * 80 + "\n")
        
        try:
            # Get API configuration
            api_config = config_manager.get("focus_server", {})
            base_url = api_config.get("frontend_api_url", "https://10.10.10.100/prisma/api/")
            
            # Fix base URL (remove /internal/sites/prisma-210-1000)
            if "/internal/sites/" in base_url:
                base_url = base_url.split("/internal/sites/")[0]
            if not base_url.endswith("/"):
                base_url += "/"
            
            logger.info(f"Base URL: {base_url}")
            logger.info("Sending test alert...\n")
            
            # Authenticate
            session = requests.Session()
            session.verify = False
            
            login_url = base_url + "auth/login"
            logger.info(f"Login URL: {login_url}")
            
            login_resp = session.post(
                login_url,
                json={"username": "prisma", "password": "prisma"},
                timeout=15
            )
            login_resp.raise_for_status()
            logger.info("✅ Authentication successful")
            
            # Send alert
            alert_id = f"investigation-test-{int(time.time())}"
            alert_payload = {
                "alertsAmount": 1,
                "dofM": 4163,
                "classId": 104,
                "severity": 3,
                "alertIds": [alert_id]
            }
            
            alert_url = base_url + "prisma-210-1000/api/push-to-rabbit"
            logger.info(f"\nAlert URL: {alert_url}")
            logger.info(f"Alert Payload: {json.dumps(alert_payload, indent=2)}")
            
            alert_resp = session.post(alert_url, json=alert_payload, timeout=15)
            alert_resp.raise_for_status()
            logger.info(f"\n✅ Alert sent successfully!")
            logger.info(f"Response: {alert_resp.text}")
            
            # Wait for processing
            logger.info("\nWaiting 3 seconds for processing...")
            time.sleep(3)
            
            # Check logs again
            logger.info("\nChecking logs after sending alert...")
            
            if relevant_pods["focus-server"]:
                pod_name = relevant_pods["focus-server"][0][0]
                logs = k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=100)
                
                if alert_id in logs or "push-to-rabbit" in logs.lower():
                    logger.info(f"✅ Found alert-related logs in Focus Server!")
                    matching_lines = [line for line in logs.split('\n') 
                                    if alert_id in line or "push-to-rabbit" in line.lower()]
                    for line in matching_lines[-5:]:
                        logger.info(f"  {line}")
                else:
                    logger.warning("❌ Alert not found in Focus Server logs")
                    logger.info("\nLast 30 lines of logs:")
                    for line in logs.split('\n')[-30:]:
                        logger.info(f"  {line}")
            
            if relevant_pods["rabbitmq"]:
                pod_name = relevant_pods["rabbitmq"][0][0]
                logs = k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=100)
                
                if "prisma" in logs.lower() or "exchange" in logs.lower():
                    logger.info(f"✅ Found activity in RabbitMQ logs!")
                    matching_lines = [line for line in logs.split('\n') 
                                    if "prisma" in line.lower() or "exchange" in line.lower()]
                    for line in matching_lines[-5:]:
                        logger.info(f"  {line}")
                else:
                    logger.warning("❌ No activity found in RabbitMQ logs")
                    logger.info("\nLast 30 lines of logs:")
                    for line in logs.split('\n')[-30:]:
                        logger.info(f"  {line}")
        
        except Exception as e:
            logger.error(f"❌ Error sending test alert: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Step 6: Summary
        logger.info("\n" + "=" * 80)
        logger.info("Step 6: Summary and Recommendations")
        logger.info("=" * 80 + "\n")
        
        focus_server_pod = relevant_pods["focus-server"][0][0] if relevant_pods["focus-server"] else "N/A"
        rabbitmq_pod = relevant_pods["rabbitmq"][0][0] if relevant_pods["rabbitmq"] else "N/A"
        
        summary_text = f"""
📋 Summary:

1. Focus Server Pod: {focus_server_pod}
   - Check logs: kubectl logs -n panda {focus_server_pod} --tail=500 | grep -i "push-to-rabbit"
   - Follow: kubectl logs -n panda {focus_server_pod} -f

2. RabbitMQ Pod: {rabbitmq_pod}
   - Check logs: kubectl logs -n panda {rabbitmq_pod} --tail=500 | grep -i "publish|exchange"
   - Check queues: kubectl exec -n panda {rabbitmq_pod} -- rabbitmqctl list_queues

3. For real-time monitoring:
   - Terminal 1: kubectl logs -n panda {focus_server_pod} -f
   - Terminal 2: Send alert via API
   - Watch Terminal 1 for new logs

4. RabbitMQ Management UI:
   - URL: http://10.10.10.100:15672
   - Check Exchanges → prisma
   - Check Queues → Look for queues with "prisma-210-1000"
        """
        logger.info(summary_text)
        
        logger.info("\n✅ Investigation complete!\n")

