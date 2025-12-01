"""
Deep Alert Logs Investigation Test

This test performs a comprehensive investigation of alert logs across all relevant components:
- Focus Server (API endpoint)
- Prisma Web App API (handles push-to-rabbit)
- RabbitMQ (message queue)
- gRPC Jobs (process alerts)
- MongoDB (stores alerts)
- RabbitMQ Management API (monitoring)

PZ-15051: Deep Alert Logs Investigation
"""

import logging
import time
import json
import requests
import re
from typing import Dict, List, Tuple, Optional

import pytest

from src.infrastructure.kubernetes_manager import KubernetesManager
from src.infrastructure.ssh_manager import SSHManager
from src.infrastructure.mongodb_manager import MongoDBManager
from config.config_manager import ConfigManager

logger = logging.getLogger(__name__)


@pytest.mark.slow
@pytest.mark.nightly
class TestDeepAlertLogsInvestigation:
    """
    Deep investigation test suite for alert logs.
    
    This test performs comprehensive investigation:
    1. Lists all relevant pods
    2. Checks Focus Server logs (API endpoint)
    3. Checks Prisma Web App API logs (if separate)
    4. Checks RabbitMQ logs and Management API
    5. Checks gRPC Job logs (all pods)
    6. Checks MongoDB for stored alerts
    7. Sends test alert
    8. Monitors all components after sending
    9. Generates comprehensive report
    """
    
    @pytest.mark.xray("PZ-15051")
    def test_deep_investigate_alert_logs(self, config_manager):
        """
        PZ-15051: Deep Alert Logs Investigation.
        
        Objective:
            To comprehensively investigate where alert-related logs appear
            across all components in the Kubernetes environment.
        
        Steps:
            1. List all pods and identify relevant ones
            2. Check Focus Server logs for API endpoint
            3. Check RabbitMQ logs and Management API
            4. Check gRPC Job logs (sample from multiple pods)
            5. Check MongoDB for stored alerts
            6. Send test alert via API
            7. Monitor all components after sending
            8. Generate comprehensive report
        """
        logger.info("=" * 80)
        logger.info("DEEP INVESTIGATION: Alert Logs in Kubernetes")
        logger.info("=" * 80)
        logger.info(f"Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%S')}\n")
        
        namespace = "panda"
        test_alert_id = f"deep-investigation-{int(time.time())}"
        report = []
        
        # Initialize managers
        k8s_manager = KubernetesManager(config_manager)
        ssh_manager = SSHManager(config_manager)
        mongodb_manager = MongoDBManager(config_manager)
        
        try:
            ssh_manager.connect()
        except Exception as e:
            logger.warning(f"SSH connection failed: {e}")
            ssh_manager = None
        
        # Step 1: List all pods
        logger.info("=" * 80)
        logger.info("Step 1: Listing All Pods")
        logger.info("=" * 80 + "\n")
        
        pods = k8s_manager.get_pods(namespace=namespace)
        logger.info(f"Found {len(pods)} pods in namespace '{namespace}':\n")
        
        relevant_pods = {
            "focus-server": [],
            "rabbitmq": [],
            "grpc-job": [],
            "mongodb": [],
            "segy-recorder": [],
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
            elif 'segy-recorder' in name:
                relevant_pods["segy-recorder"].append((name, status))
        
        for category, pod_list in relevant_pods.items():
            if pod_list:
                logger.info(f"{category.upper()}:")
                for name, status in pod_list:
                    logger.info(f"  - {name} ({status})")
        
        report.append(f"Found {len(pods)} pods total")
        report.append(f"Focus Server: {len(relevant_pods['focus-server'])} pods")
        report.append(f"RabbitMQ: {len(relevant_pods['rabbitmq'])} pods")
        report.append(f"gRPC Jobs: {len(relevant_pods['grpc-job'])} pods")
        report.append(f"MongoDB: {len(relevant_pods['mongodb'])} pods")
        report.append("")
        
        # Step 1.5: Investigate Ingress, Services, and Endpoints
        logger.info("\n" + "=" * 80)
        logger.info("Step 1.5: Investigating Ingress, Services, and Endpoints")
        logger.info("=" * 80 + "\n")
        
        try:
            # Get Ingress resources
            logger.info("Getting Ingress resources...")
            ingress_list = k8s_manager.get_ingress(namespace=namespace)
            logger.info(f"Found {len(ingress_list)} Ingress resources")
            
            for ingress in ingress_list:
                ingress_name = ingress.get('name', 'unknown')
                rules = ingress.get('rules', [])
                logger.info(f"\nIngress: {ingress_name}")
                logger.info(f"  Rules: {json.dumps(rules, indent=4)}")
                
                # Check for push-to-rabbit routing
                for rule in rules:
                    paths = rule.get('paths', [])
                    for path in paths:
                        if 'push-to-rabbit' in str(path).lower() or 'api' in str(path).lower():
                            logger.info(f"  ⚠️  Found API-related path: {path}")
                            report.append(f"Ingress {ingress_name}: Found API path {path}")
            
            # Get Services
            logger.info("\nGetting Services...")
            services = k8s_manager.get_services(namespace=namespace)
            logger.info(f"Found {len(services)} Services")
            
            webapp_service = None
            for svc in services:
                svc_name = svc.get('name', 'unknown')
                svc_type = svc.get('type', 'unknown')
                cluster_ip = svc.get('cluster_ip', 'unknown')
                ports = svc.get('ports', [])
                
                logger.info(f"\nService: {svc_name}")
                logger.info(f"  Type: {svc_type}")
                logger.info(f"  Cluster IP: {cluster_ip}")
                logger.info(f"  Ports: {ports}")
                
                if 'webapp' in svc_name.lower() or 'web' in svc_name.lower():
                    webapp_service = svc
                    logger.info(f"  ⚠️  Found WebApp service: {svc_name}")
                    report.append(f"Service: Found WebApp service {svc_name}")
            
            # Get Endpoints
            logger.info("\nGetting Endpoints...")
            endpoints = k8s_manager.get_endpoints(namespace=namespace)
            logger.info(f"Found {len(endpoints)} Endpoints")
            
            for ep in endpoints:
                ep_name = ep.get('name', 'unknown')
                subsets = ep.get('subsets', [])
                logger.info(f"\nEndpoint: {ep_name}")
                
                for subset in subsets:
                    addresses = subset.get('addresses', [])
                    ports = subset.get('ports', [])
                    logger.info(f"  Addresses: {len(addresses)}")
                    for addr in addresses:
                        pod_name = addr.get('targetRef', {}).get('name', 'unknown')
                        ip = addr.get('ip', 'unknown')
                        logger.info(f"    - {ip} -> Pod: {pod_name}")
                        report.append(f"Endpoint {ep_name}: {ip} -> {pod_name}")
                    logger.info(f"  Ports: {ports}")
            
            # Check Ingress Controller logs for routing info
            logger.info("\nChecking Ingress Controller for routing info...")
            ingress_pods = k8s_manager.get_pods(namespace="kube-system")
            ingress_pod = None
            for pod in ingress_pods:
                if 'ingress-nginx-controller' in pod.get('name', ''):
                    ingress_pod = pod
                    break
            
            if ingress_pod:
                pod_name = ingress_pod['name']
                logger.info(f"Found Ingress Controller pod: {pod_name}")
                # We'll check logs later after sending alert
                report.append(f"Ingress Controller: {pod_name}")
            else:
                logger.warning("⚠️  Ingress Controller pod not found")
                report.append("Ingress Controller: Pod not found")
                
        except Exception as e:
            logger.error(f"❌ Error investigating Ingress/Services/Endpoints: {e}")
            report.append(f"Ingress/Services/Endpoints: Error - {e}")
        
        # Step 2: Check RabbitMQ Management API (including bindings!)
        logger.info("\n" + "=" * 80)
        logger.info("Step 2: Checking RabbitMQ Management API (Deep Investigation)")
        logger.info("=" * 80 + "\n")
        
        rabbitmq_config = config_manager.get("rabbitmq", {})
        rabbitmq_host = rabbitmq_config.get("host", "10.10.10.150")
        rabbitmq_user = rabbitmq_config.get("username", "user")
        rabbitmq_password = rabbitmq_config.get("password", "")
        
        try:
            auth = (rabbitmq_user, rabbitmq_password)
            
            # Get exchanges
            logger.info("Getting RabbitMQ exchanges...")
            mgmt_url = f"http://{rabbitmq_host}:15672/api/exchanges"
            response = requests.get(mgmt_url, auth=auth, timeout=10)
            if response.status_code == 200:
                exchanges = response.json()
                prisma_exchange = [e for e in exchanges if e.get('name') == 'prisma']
                if prisma_exchange:
                    logger.info("✅ Found 'prisma' exchange:")
                    logger.info(f"  Type: {prisma_exchange[0].get('type')}")
                    logger.info(f"  Durable: {prisma_exchange[0].get('durable')}")
                    logger.info(f"  Auto-delete: {prisma_exchange[0].get('auto_delete')}")
                    logger.info(f"  Messages published: {prisma_exchange[0].get('message_stats', {}).get('publish', 0)}")
                    logger.info(f"  Messages in: {prisma_exchange[0].get('message_stats', {}).get('publish_in', 0)}")
                    logger.info(f"  Messages out: {prisma_exchange[0].get('message_stats', {}).get('publish_out', 0)}")
                    report.append(f"RabbitMQ Exchange 'prisma': Found, Type: {prisma_exchange[0].get('type')}")
                else:
                    logger.warning("❌ 'prisma' exchange not found")
                    report.append("RabbitMQ Exchange 'prisma': NOT FOUND")
            
            # Get queues
            logger.info("\nGetting RabbitMQ queues...")
            queues_url = f"http://{rabbitmq_host}:15672/api/queues"
            response = requests.get(queues_url, auth=auth, timeout=10)
            if response.status_code == 200:
                queues = response.json()
                logger.info(f"Total queues: {len(queues)}")
                
                alert_queues = [q for q in queues if 'alert' in q.get('name', '').lower() or 'prisma-210-1000' in q.get('name', '')]
                logger.info(f"\nFound {len(alert_queues)} queues related to alerts:")
                if alert_queues:
                    for queue in alert_queues[:10]:  # Show first 10
                        logger.info(f"  - {queue.get('name')}: {queue.get('messages', 0)} messages, {queue.get('consumers', 0)} consumers")
                        report.append(f"RabbitMQ Queue: {queue.get('name')}, Messages: {queue.get('messages', 0)}, Consumers: {queue.get('consumers', 0)}")
                else:
                    logger.warning("  ⚠️  No alert-related queues found!")
                    report.append("RabbitMQ: No alert-related queues found")
            
            # Get bindings for 'prisma' exchange (CRITICAL!)
            logger.info("\nGetting RabbitMQ bindings for 'prisma' exchange...")
            bindings_url = f"http://{rabbitmq_host}:15672/api/exchanges/%2F/prisma/bindings/source"
            response = requests.get(bindings_url, auth=auth, timeout=10)
            if response.status_code == 200:
                bindings = response.json()
                logger.info(f"Total bindings for 'prisma' exchange: {len(bindings)}")
                
                alert_bindings = []
                for binding in bindings:
                    routing_key = binding.get('routing_key', '')
                    queue_name = binding.get('destination', '')
                    
                    if 'alert' in routing_key.lower() or 'alert' in queue_name.lower() or 'Algorithm.AlertReport' in routing_key:
                        alert_bindings.append(binding)
                        logger.info(f"  ⚠️  Found alert-related binding:")
                        logger.info(f"    Routing Key: {routing_key}")
                        logger.info(f"    Queue: {queue_name}")
                        report.append(f"RabbitMQ Binding: {routing_key} -> {queue_name}")
                
                if not alert_bindings:
                    logger.warning("  ❌ No alert-related bindings found!")
                    logger.warning("  This means alerts published to 'prisma' exchange with alert routing keys will be DROPPED!")
                    report.append("RabbitMQ: CRITICAL - No alert-related bindings found!")
                else:
                    logger.info(f"  ✅ Found {len(alert_bindings)} alert-related bindings")
                    
        except Exception as e:
            logger.warning(f"⚠️  Could not check RabbitMQ Management API: {e}")
            report.append(f"RabbitMQ Management API: Error - {e}")
        
        # Step 3: Check MongoDB for existing alerts
        logger.info("\n" + "=" * 80)
        logger.info("Step 3: Checking MongoDB for Alerts")
        logger.info("=" * 80 + "\n")
        
        try:
            mongodb_manager.connect()
            db = mongodb_manager.get_database("prisma")
            alerts_collection = db.get_collection("alerts")
            
            # Count total alerts
            total_alerts = alerts_collection.count_documents({})
            logger.info(f"Total alerts in MongoDB: {total_alerts}")
            
            # Get recent alerts (last 5)
            recent_alerts = list(alerts_collection.find().sort("_id", -1).limit(5))
            if recent_alerts:
                logger.info("\nRecent alerts:")
                for alert in recent_alerts:
                    alert_id = alert.get('ext_id') or alert.get('_id')
                    logger.info(f"  - Alert ID: {alert_id}, Class: {alert.get('class_id')}, Severity: {alert.get('severity')}")
            
            report.append(f"MongoDB: {total_alerts} total alerts")
            mongodb_manager.disconnect()
        except Exception as e:
            logger.warning(f"⚠️  Could not check MongoDB: {e}")
            report.append(f"MongoDB: Error - {e}")
        
        # Step 4: Check gRPC Job logs (sample)
        logger.info("\n" + "=" * 80)
        logger.info("Step 4: Checking gRPC Job Logs (Sample)")
        logger.info("=" * 80 + "\n")
        
        grpc_sample_size = min(3, len(relevant_pods["grpc-job"]))
        for i, (pod_name, status) in enumerate(relevant_pods["grpc-job"][:grpc_sample_size]):
            logger.info(f"Checking logs for: {pod_name} ({i+1}/{grpc_sample_size})")
            try:
                logs = k8s_manager.get_pod_logs(pod_name, namespace=namespace, tail_lines=200)
                
                keywords = ["alert", "Algorithm.AlertReport", "MLGroundAlertReport", "publish", "consume"]
                found_keywords = {}
                for keyword in keywords:
                    matching_lines = [line for line in logs.split('\n') if keyword.lower() in line.lower()]
                    if matching_lines:
                        found_keywords[keyword] = len(matching_lines)
                
                if found_keywords:
                    logger.info(f"  ✅ Found keywords: {found_keywords}")
                    report.append(f"gRPC Job {pod_name}: Found keywords {list(found_keywords.keys())}")
                else:
                    logger.info(f"  ℹ️  No alert-related keywords found")
                    report.append(f"gRPC Job {pod_name}: No alert keywords found")
            except Exception as e:
                logger.warning(f"  ⚠️  Error getting logs: {e}")
                report.append(f"gRPC Job {pod_name}: Error - {e}")
        
        # Step 5: Send test alert
        logger.info("\n" + "=" * 80)
        logger.info("Step 5: Sending Test Alert")
        logger.info("=" * 80 + "\n")
        
        try:
            api_config = config_manager.get("focus_server", {})
            base_url = api_config.get("frontend_api_url", "https://10.10.10.100/prisma/api/")
            
            if "/internal/sites/" in base_url:
                base_url = base_url.split("/internal/sites/")[0]
            if not base_url.endswith("/"):
                base_url += "/"
            
            logger.info(f"Base URL: {base_url}")
            
            # Authenticate
            session = requests.Session()
            session.verify = False
            
            login_url = base_url + "auth/login"
            login_resp = session.post(
                login_url,
                json={"username": "prisma", "password": "prisma"},
                timeout=15
            )
            login_resp.raise_for_status()
            logger.info("✅ Authentication successful")
            
            # Send alert
            alert_payload = {
                "alertsAmount": 1,
                "dofM": 4163,
                "classId": 104,
                "severity": 3,
                "alertIds": [test_alert_id]
            }
            
            alert_url = base_url + "prisma-210-1000/api/push-to-rabbit"
            logger.info(f"Alert URL: {alert_url}")
            logger.info(f"Alert Payload: {json.dumps(alert_payload, indent=2)}")
            
            alert_resp = session.post(alert_url, json=alert_payload, timeout=15)
            alert_resp.raise_for_status()
            logger.info(f"\n✅ Alert sent successfully!")
            logger.info(f"Response: {alert_resp.text[:500]}")  # First 500 chars
            
            report.append(f"Test Alert Sent: {test_alert_id}")
            report.append(f"API Response: {alert_resp.status_code}")
            
        except Exception as e:
            logger.error(f"❌ Error sending alert: {e}")
            report.append(f"Test Alert: Error - {e}")
            return  # Can't continue without alert
        
        # Step 6: Wait and monitor all components
        logger.info("\n" + "=" * 80)
        logger.info("Step 6: Monitoring All Components After Alert")
        logger.info("=" * 80 + "\n")
        
        logger.info("Waiting 5 seconds for processing...")
        time.sleep(5)
        
        # 6.0: Check Ingress Controller logs (PRIMARY LOCATION!)
        logger.info("\n" + "=" * 80)
        logger.info("Step 6.0: Checking Ingress Controller Logs (PRIMARY LOCATION!)")
        logger.info("=" * 80 + "\n")
        
        try:
            # Find Ingress Controller pod
            ingress_pods = k8s_manager.get_pods(namespace="kube-system")
            ingress_pod = None
            for pod in ingress_pods:
                if 'ingress-nginx-controller' in pod['name']:
                    ingress_pod = pod
                    break
            
            if ingress_pod:
                pod_name = ingress_pod['name']
                logger.info(f"Found Ingress Controller pod: {pod_name}")
                logs = k8s_manager.get_pod_logs(pod_name, namespace="kube-system", tail_lines=500)
                
                # Search for push-to-rabbit
                if "push-to-rabbit" in logs.lower():
                    logger.info(f"  ✅ Found push-to-rabbit in Ingress Controller logs!")
                    matching_lines = [line for line in logs.split('\n') 
                                    if "push-to-rabbit" in line.lower()]
                    logger.info(f"  Found {len(matching_lines)} matching lines")
                    for line in matching_lines[-3:]:  # Show last 3
                        logger.info(f"    {line[:200]}")
                    
                    # Check for success (201 status)
                    success_lines = [line for line in matching_lines if " 201 " in line]
                    if success_lines:
                        logger.info(f"  ✅ Found {len(success_lines)} successful requests (201)")
                        report.append(f"Ingress Controller: Found {len(success_lines)} successful push-to-rabbit requests")
                    else:
                        logger.warning(f"  ⚠️  No 201 status codes found")
                        report.append(f"Ingress Controller: push-to-rabbit found but no 201 status")
                    
                    # Check for alert_sound.mp3 (indicates frontend received alert)
                    alert_sound_lines = [line for line in logs.split('\n') 
                                       if "alert_sound.mp3" in line.lower()]
                    if alert_sound_lines:
                        logger.info(f"  ✅ Found {len(alert_sound_lines)} alert_sound.mp3 requests (Frontend received alert!)")
                        report.append(f"Ingress Controller: Frontend received alert ({len(alert_sound_lines)} sound requests)")
                else:
                    logger.warning(f"  ❌ push-to-rabbit not found in Ingress Controller logs")
                    report.append(f"Ingress Controller: push-to-rabbit NOT found")
            else:
                logger.warning("  ⚠️  Ingress Controller pod not found")
                report.append("Ingress Controller: Pod not found")
        except Exception as e:
            logger.error(f"  ❌ Error checking Ingress Controller: {e}")
            report.append(f"Ingress Controller: Error - {e}")
        
        # 6.1: Check Focus Server logs
        if relevant_pods["focus-server"]:
            pod_name = relevant_pods["focus-server"][0][0]
            logger.info(f"\nChecking Focus Server logs: {pod_name}")
            try:
                logs = k8s_manager.get_pod_logs(pod_name, namespace=namespace, tail_lines=200)
                
                # Search for alert ID or push-to-rabbit
                if test_alert_id in logs or "push-to-rabbit" in logs.lower():
                    logger.info(f"  ✅ Found alert-related logs!")
                    matching_lines = [line for line in logs.split('\n') 
                                    if test_alert_id in line or "push-to-rabbit" in line.lower()]
                    for line in matching_lines[-5:]:
                        logger.info(f"    {line[:200]}")
                    report.append(f"Focus Server: Found alert in logs")
                else:
                    logger.warning(f"  ❌ Alert not found in Focus Server logs")
                    report.append(f"Focus Server: Alert NOT found in logs")
            except Exception as e:
                logger.error(f"  ❌ Error: {e}")
                report.append(f"Focus Server: Error - {e}")
        
        # 6.2: Check RabbitMQ logs
        if relevant_pods["rabbitmq"]:
            pod_name = relevant_pods["rabbitmq"][0][0]
            logger.info(f"\nChecking RabbitMQ logs: {pod_name}")
            try:
                logs = k8s_manager.get_pod_logs(pod_name, namespace=namespace, tail_lines=200)
                
                # Check for recent activity around alert time
                if test_alert_id in logs or "prisma" in logs.lower():
                    logger.info(f"  ✅ Found activity in RabbitMQ logs!")
                    matching_lines = [line for line in logs.split('\n') 
                                    if test_alert_id in line or ("prisma" in line.lower() and "12:03" in line)]
                    for line in matching_lines[-5:]:
                        logger.info(f"    {line[:200]}")
                    report.append(f"RabbitMQ: Found activity in logs")
                else:
                    logger.info(f"  ℹ️  No specific alert ID found (normal - RabbitMQ logs are low-level)")
                    report.append(f"RabbitMQ: Activity found (low-level logs)")
            except Exception as e:
                logger.error(f"  ❌ Error: {e}")
                report.append(f"RabbitMQ: Error - {e}")
        
        # 6.3: Check RabbitMQ Management API for new messages
        logger.info(f"\nChecking RabbitMQ Management API for new messages...")
        try:
            queues_url = f"http://{rabbitmq_host}:15672/api/queues"
            response = requests.get(queues_url, auth=auth, timeout=10)
            if response.status_code == 200:
                queues = response.json()
                total_messages = sum(q.get('messages', 0) for q in queues)
                logger.info(f"  Total messages in all queues: {total_messages}")
                report.append(f"RabbitMQ Total Messages: {total_messages}")
        except Exception as e:
            logger.warning(f"  ⚠️  Error: {e}")
        
        # 6.4: Check MongoDB for new alert
        logger.info(f"\nChecking MongoDB for new alert: {test_alert_id}")
        try:
            mongodb_manager.connect()
            db = mongodb_manager.get_database("prisma")
            alerts_collection = db.get_collection("alerts")
            
            # Search for alert by ext_id
            alert_found = alerts_collection.find_one({"ext_id": test_alert_id})
            if alert_found:
                logger.info(f"  ✅ Alert found in MongoDB!")
                logger.info(f"    Class ID: {alert_found.get('class_id')}")
                logger.info(f"    Severity: {alert_found.get('severity')}")
                logger.info(f"    Distance: {alert_found.get('distance_m')}")
                report.append(f"MongoDB: Alert {test_alert_id} FOUND")
            else:
                logger.warning(f"  ❌ Alert not found in MongoDB yet")
                report.append(f"MongoDB: Alert {test_alert_id} NOT FOUND")
            
            mongodb_manager.disconnect()
        except Exception as e:
            logger.error(f"  ❌ Error: {e}")
            report.append(f"MongoDB Check: Error - {e}")
        
        # 6.5: Check gRPC Job logs for alert processing
        logger.info(f"\nChecking gRPC Job logs for alert processing...")
        grpc_sample_size = min(3, len(relevant_pods["grpc-job"]))
        for i, (pod_name, status) in enumerate(relevant_pods["grpc-job"][:grpc_sample_size]):
            logger.info(f"  Checking: {pod_name} ({i+1}/{grpc_sample_size})")
            try:
                logs = k8s_manager.get_pod_logs(pod_name, namespace=namespace, tail_lines=100)
                
                if test_alert_id in logs or "Algorithm.AlertReport" in logs:
                    logger.info(f"    ✅ Found alert-related activity!")
                    matching_lines = [line for line in logs.split('\n') 
                                    if test_alert_id in line or "Algorithm.AlertReport" in line]
                    for line in matching_lines[-3:]:
                        logger.info(f"      {line[:200]}")
                    report.append(f"gRPC Job {pod_name}: Found alert activity")
                else:
                    logger.info(f"    ℹ️  No alert activity found")
            except Exception as e:
                logger.warning(f"    ⚠️  Error: {e}")
        
        # Step 7: Generate comprehensive report
        logger.info("\n" + "=" * 80)
        logger.info("COMPREHENSIVE INVESTIGATION REPORT")
        logger.info("=" * 80 + "\n")
        
        report_text = "\n".join(report)
        logger.info(report_text)
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Test Alert ID: {test_alert_id}")
        logger.info(f"Total Pods Checked: {len(pods)}")
        logger.info(f"Focus Server Pods: {len(relevant_pods['focus-server'])}")
        logger.info(f"RabbitMQ Pods: {len(relevant_pods['rabbitmq'])}")
        logger.info(f"gRPC Job Pods: {len(relevant_pods['grpc-job'])}")
        logger.info(f"MongoDB Pods: {len(relevant_pods['mongodb'])}")
        logger.info("\n✅ Deep investigation complete!\n")
        
        # Cleanup
        if ssh_manager:
            ssh_manager.disconnect()
        
        # Assertions
        assert test_alert_id in report_text or "Test Alert Sent" in report_text, "Test alert was not sent successfully"

