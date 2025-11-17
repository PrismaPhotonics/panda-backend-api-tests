#!/usr/bin/env python3
"""
Script to investigate alert logs in Kubernetes.

This script:
1. Connects to Kubernetes
2. Lists relevant pods
3. Checks logs for alert-related content
4. Sends a test alert
5. Monitors logs after sending
6. Creates a report

Usage:
    python scripts/investigate_alert_logs.py
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.infrastructure.kubernetes_manager import KubernetesManager
from src.infrastructure.ssh_manager import SSHManager
import requests


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def investigate_alert_logs():
    """Main investigation function."""
    
    print_section("🔍 Alert Logs Investigation - Kubernetes")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Initialize managers
    config_manager = ConfigManager()
    k8s_manager = KubernetesManager(config_manager)
    
    # Step 1: List all pods
    print_section("Step 1: Listing All Pods")
    try:
        pods = k8s_manager.get_pods(namespace="panda")
        print(f"Found {len(pods)} pods in namespace 'panda':\n")
        
        relevant_pods = {
            "focus-server": [],
            "rabbitmq": [],
            "grpc-job": [],
            "mongodb": [],
            "other": []
        }
        
        for pod in pods:
            name = pod['metadata']['name']
            status = pod['status']['phase']
            
            if 'focus-server' in name:
                relevant_pods["focus-server"].append((name, status))
            elif 'rabbitmq' in name:
                relevant_pods["rabbitmq"].append((name, status))
            elif 'grpc-job' in name:
                relevant_pods["grpc-job"].append((name, status))
            elif 'mongodb' in name:
                relevant_pods["mongodb"].append((name, status))
            else:
                relevant_pods["other"].append((name, status))
        
        for category, pod_list in relevant_pods.items():
            if pod_list:
                print(f"\n{category.upper()}:")
                for name, status in pod_list:
                    print(f"  - {name} ({status})")
        
    except Exception as e:
        print(f"❌ Error listing pods: {e}")
        return
    
    # Step 2: Check Focus Server logs
    print_section("Step 2: Checking Focus Server Logs")
    if relevant_pods["focus-server"]:
        pod_name = relevant_pods["focus-server"][0][0]
        print(f"Checking logs for: {pod_name}\n")
        
        try:
            logs = k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=500)
            
            # Search for alert-related keywords
            keywords = [
                "push-to-rabbit",
                "alert",
                "rabbit",
                "queue",
                "api",
                "POST",
                "prisma-210-1000"
            ]
            
            print("Searching for keywords in logs:")
            found_keywords = {}
            for keyword in keywords:
                matching_lines = [line for line in logs.split('\n') if keyword.lower() in line.lower()]
                if matching_lines:
                    found_keywords[keyword] = matching_lines[-10:]  # Last 10 matches
                    print(f"  ✅ '{keyword}': Found {len(matching_lines)} lines")
                else:
                    print(f"  ❌ '{keyword}': Not found")
            
            if found_keywords:
                print("\nSample log lines:")
                for keyword, lines in found_keywords.items():
                    print(f"\n  {keyword}:")
                    for line in lines[-3:]:  # Show last 3
                        print(f"    {line[:150]}...")  # Truncate long lines
            else:
                print("\n⚠️  No alert-related keywords found in Focus Server logs")
                print("\nLast 20 lines of logs:")
                for line in logs.split('\n')[-20:]:
                    print(f"  {line}")
                    
        except Exception as e:
            print(f"❌ Error getting Focus Server logs: {e}")
    
    # Step 3: Check RabbitMQ logs
    print_section("Step 3: Checking RabbitMQ Logs")
    if relevant_pods["rabbitmq"]:
        pod_name = relevant_pods["rabbitmq"][0][0]
        print(f"Checking logs for: {pod_name}\n")
        
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
            
            print("Searching for keywords in logs:")
            found_keywords = {}
            for keyword in keywords:
                matching_lines = [line for line in logs.split('\n') if keyword.lower() in line.lower()]
                if matching_lines:
                    found_keywords[keyword] = matching_lines[-10:]
                    print(f"  ✅ '{keyword}': Found {len(matching_lines)} lines")
                else:
                    print(f"  ❌ '{keyword}': Not found")
            
            if found_keywords:
                print("\nSample log lines:")
                for keyword, lines in found_keywords.items():
                    print(f"\n  {keyword}:")
                    for line in lines[-3:]:
                        print(f"    {line[:150]}...")
            else:
                print("\n⚠️  No alert-related keywords found in RabbitMQ logs")
                print("\nLast 20 lines of logs:")
                for line in logs.split('\n')[-20:]:
                    print(f"  {line}")
                    
        except Exception as e:
            print(f"❌ Error getting RabbitMQ logs: {e}")
    
    # Step 4: Check RabbitMQ queues/exchanges via kubectl exec
    print_section("Step 4: Checking RabbitMQ Queues and Exchanges")
    if relevant_pods["rabbitmq"]:
        pod_name = relevant_pods["rabbitmq"][0][0]
        print(f"Checking RabbitMQ queues/exchanges in: {pod_name}\n")
        
        try:
            ssh_manager = SSHManager(config_manager)
            ssh_manager.connect()
            
            # Check exchanges
            cmd = f"kubectl exec -n panda {pod_name} -- rabbitmqctl list_exchanges name type"
            result = ssh_manager.execute_command(cmd, timeout=30)
            if result["success"]:
                print("Exchanges:")
                print(result["stdout"])
            else:
                print(f"⚠️  Could not list exchanges: {result['stderr']}")
            
            # Check queues
            cmd = f"kubectl exec -n panda {pod_name} -- rabbitmqctl list_queues name messages"
            result = ssh_manager.execute_command(cmd, timeout=30)
            if result["success"]:
                print("\nQueues:")
                print(result["stdout"])
            else:
                print(f"⚠️  Could not list queues: {result['stderr']}")
            
            # Check bindings
            cmd = f"kubectl exec -n panda {pod_name} -- rabbitmqctl list_bindings exchange_name routing_key queue_name"
            result = ssh_manager.execute_command(cmd, timeout=30)
            if result["success"]:
                print("\nBindings:")
                print(result["stdout"])
            else:
                print(f"⚠️  Could not list bindings: {result['stderr']}")
            
            ssh_manager.disconnect()
            
        except Exception as e:
            print(f"❌ Error checking RabbitMQ: {e}")
    
    # Step 5: Send a test alert and monitor logs
    print_section("Step 5: Sending Test Alert and Monitoring Logs")
    
    try:
        # Get API configuration
        api_config = config_manager.get("focus_server", {})
        base_url = api_config.get("frontend_api_url", "https://10.10.10.100/prisma/api/")
        
        print(f"Base URL: {base_url}")
        print("Sending test alert...\n")
        
        # Authenticate
        session = requests.Session()
        session.verify = False
        
        login_url = base_url.replace("/internal/sites/prisma-210-1000", "") + "auth/login"
        print(f"Login URL: {login_url}")
        
        login_resp = session.post(
            login_url,
            json={"username": "prisma", "password": "prisma"},
            timeout=15
        )
        login_resp.raise_for_status()
        print("✅ Authentication successful")
        
        # Send alert
        alert_id = f"investigation-test-{int(time.time())}"
        alert_payload = {
            "alertsAmount": 1,
            "dofM": 4163,
            "classId": 104,
            "severity": 3,
            "alertIds": [alert_id]
        }
        
        alert_url = base_url.replace("/internal/sites/prisma-210-1000", "") + "prisma-210-1000/api/push-to-rabbit"
        print(f"\nAlert URL: {alert_url}")
        print(f"Alert Payload: {json.dumps(alert_payload, indent=2)}")
        
        alert_resp = session.post(alert_url, json=alert_payload, timeout=15)
        alert_resp.raise_for_status()
        print(f"\n✅ Alert sent successfully!")
        print(f"Response: {alert_resp.text}")
        
        # Wait a bit for processing
        print("\nWaiting 3 seconds for processing...")
        time.sleep(3)
        
        # Check logs again
        print("\nChecking logs after sending alert...")
        
        if relevant_pods["focus-server"]:
            pod_name = relevant_pods["focus-server"][0][0]
            logs = k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=100)
            
            if alert_id in logs or "push-to-rabbit" in logs.lower():
                print(f"✅ Found alert-related logs in Focus Server!")
                matching_lines = [line for line in logs.split('\n') 
                                if alert_id in line or "push-to-rabbit" in line.lower()]
                for line in matching_lines[-5:]:
                    print(f"  {line}")
            else:
                print("❌ Alert not found in Focus Server logs")
        
        if relevant_pods["rabbitmq"]:
            pod_name = relevant_pods["rabbitmq"][0][0]
            logs = k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=100)
            
            if "prisma" in logs.lower() or "exchange" in logs.lower():
                print(f"✅ Found activity in RabbitMQ logs!")
                matching_lines = [line for line in logs.split('\n') 
                                if "prisma" in line.lower() or "exchange" in line.lower()]
                for line in matching_lines[-5:]:
                    print(f"  {line}")
            else:
                print("❌ No activity found in RabbitMQ logs")
        
    except Exception as e:
        print(f"❌ Error sending test alert: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 6: Summary and recommendations
    print_section("Step 6: Summary and Recommendations")
    
    print("""
📋 Summary:

1. Focus Server Pod: {focus_server_pod}
   - Check logs for: "push-to-rabbit", "POST", "api"
   - Command: kubectl logs -n panda {focus_server_pod} --tail=500 | grep -i "push-to-rabbit\|alert"

2. RabbitMQ Pod: {rabbitmq_pod}
   - Check logs for: "publish", "exchange", "prisma"
   - Command: kubectl logs -n panda {rabbitmq_pod} --tail=500 | grep -i "publish\|exchange\|prisma"
   - Check queues: kubectl exec -n panda {rabbitmq_pod} -- rabbitmqctl list_queues

3. For real-time monitoring:
   - Terminal 1: kubectl logs -n panda {focus_server_pod} -f
   - Terminal 2: Send alert via API
   - Watch Terminal 1 for new logs

4. Check RabbitMQ Management UI:
   - URL: http://10.10.10.100:15672 (or your RabbitMQ management URL)
   - Check Exchanges → prisma
   - Check Queues → Look for queues with "prisma-210-1000" or "alert"
   - Check Messages → See if messages are being published/consumed
    """.format(
        focus_server_pod=relevant_pods["focus-server"][0][0] if relevant_pods["focus-server"] else "N/A",
        rabbitmq_pod=relevant_pods["rabbitmq"][0][0] if relevant_pods["rabbitmq"] else "N/A"
    ))
    
    print("\n✅ Investigation complete!\n")


if __name__ == "__main__":
    try:
        investigate_alert_logs()
    except KeyboardInterrupt:
        print("\n\n⚠️  Investigation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

