"""
Script to find where push-to-rabbit endpoint logs appear.

This script:
1. Lists all pods in the namespace
2. Checks all containers in Focus Server pod
3. Checks for Prisma Web App API pod (separate)
4. Checks RabbitMQ Management API for message activity
5. Checks MongoDB for stored alerts
6. Provides recommendations
"""

import logging
import sys
import time
import requests
from typing import List, Dict, Optional

# Add project root to path
sys.path.insert(0, '.')

from src.infrastructure.kubernetes_manager import KubernetesManager
from src.infrastructure.ssh_manager import SSHManager
from src.infrastructure.mongodb_manager import MongoDBManager
from config.config_manager import ConfigManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def find_push_to_rabbit_logs():
    """Find where push-to-rabbit endpoint logs appear."""
    
    logger.info("=" * 80)
    logger.info("Finding push-to-rabbit Endpoint Logs")
    logger.info("=" * 80 + "\n")
    
    config_manager = ConfigManager()
    namespace = "panda"
    
    # Initialize managers
    k8s_manager = KubernetesManager(config_manager)
    ssh_manager = SSHManager(config_manager)
    
    try:
        ssh_manager.connect()
    except Exception as e:
        logger.warning(f"SSH connection failed: {e}")
        ssh_manager = None
    
    # Step 1: List all pods
    logger.info("Step 1: Listing all pods...\n")
    pods = k8s_manager.get_pods(namespace=namespace)
    
    # Find relevant pods
    focus_server_pods = [p for p in pods if 'focus-server' in p['name']]
    prisma_pods = [p for p in pods if 'prisma' in p['name'].lower() and 'focus-server' not in p['name']]
    web_app_pods = [p for p in pods if 'web' in p['name'].lower() or 'app' in p['name'].lower()]
    
    logger.info(f"Found {len(focus_server_pods)} Focus Server pods:")
    for pod in focus_server_pods:
        logger.info(f"  - {pod['name']} ({pod['status']})")
    
    if prisma_pods:
        logger.info(f"\nFound {len(prisma_pods)} Prisma pods:")
        for pod in prisma_pods:
            logger.info(f"  - {pod['name']} ({pod['status']})")
    
    if web_app_pods:
        logger.info(f"\nFound {len(web_app_pods)} Web App pods:")
        for pod in web_app_pods:
            logger.info(f"  - {pod['name']} ({pod['status']})")
    
    # Step 2: Check all containers in Focus Server pod
    if focus_server_pods:
        pod_name = focus_server_pods[0]['name']
        logger.info(f"\n" + "=" * 80)
        logger.info(f"Step 2: Checking all containers in {pod_name}")
        logger.info("=" * 80 + "\n")
        
        try:
            # Get pod details to see all containers
            if ssh_manager:
                cmd = f"kubectl get pod {pod_name} -n {namespace} -o json"
                result = ssh_manager.execute_command(cmd, timeout=30)
                if result["success"]:
                    import json
                    pod_details = json.loads(result["stdout"])
                    containers = pod_details.get('spec', {}).get('containers', [])
                    logger.info(f"Found {len(containers)} containers:")
                    for container in containers:
                        logger.info(f"  - {container['name']}")
                    
                    # Check logs from each container
                    for container in containers:
                        container_name = container['name']
                        logger.info(f"\nChecking logs from container: {container_name}")
                        try:
                            logs = k8s_manager.get_pod_logs(
                                pod_name, 
                                namespace=namespace, 
                                tail_lines=200,
                                container=container_name
                            )
                            
                            # Search for push-to-rabbit
                            keywords = ["push-to-rabbit", "pushToRabbit", "push_to_rabbit", "prisma-210-1000/api"]
                            found = False
                            for keyword in keywords:
                                if keyword.lower() in logs.lower():
                                    logger.info(f"  ✅ Found '{keyword}' in logs!")
                                    matching_lines = [line for line in logs.split('\n') if keyword.lower() in line.lower()]
                                    for line in matching_lines[-5:]:
                                        logger.info(f"    {line[:200]}")
                                    found = True
                            
                            if not found:
                                logger.info(f"  ❌ No push-to-rabbit keywords found")
                                
                        except Exception as e:
                            logger.warning(f"  ⚠️  Error getting logs from {container_name}: {e}")
                else:
                    logger.warning(f"Could not get pod details: {result['stderr']}")
        except Exception as e:
            logger.error(f"Error checking containers: {e}")
    
    # Step 3: Check all pods for push-to-rabbit logs
    logger.info(f"\n" + "=" * 80)
    logger.info("Step 3: Checking all pods for push-to-rabbit logs")
    logger.info("=" * 80 + "\n")
    
    all_pods_to_check = focus_server_pods + prisma_pods + web_app_pods
    
    for pod in all_pods_to_check[:5]:  # Check first 5 pods
        pod_name = pod['name']
        logger.info(f"Checking: {pod_name}")
        try:
            logs = k8s_manager.get_pod_logs(pod_name, namespace=namespace, tail_lines=500)
            
            keywords = ["push-to-rabbit", "pushToRabbit", "push_to_rabbit", "prisma-210-1000/api", "POST.*api"]
            found_keywords = []
            for keyword in keywords:
                if keyword.lower() in logs.lower():
                    found_keywords.append(keyword)
            
            if found_keywords:
                logger.info(f"  ✅ Found keywords: {found_keywords}")
                # Show sample lines
                for keyword in found_keywords[:2]:  # Show first 2
                    matching_lines = [line for line in logs.split('\n') if keyword.lower() in line.lower()]
                    for line in matching_lines[-3:]:
                        logger.info(f"    {line[:200]}")
            else:
                logger.info(f"  ❌ No push-to-rabbit keywords found")
        except Exception as e:
            logger.warning(f"  ⚠️  Error: {e}")
    
    # Step 4: Check RabbitMQ Management API
    logger.info(f"\n" + "=" * 80)
    logger.info("Step 4: Checking RabbitMQ Management API")
    logger.info("=" * 80 + "\n")
    
    rabbitmq_config = config_manager.get("rabbitmq", {})
    rabbitmq_host = rabbitmq_config.get("host", "10.10.10.150")
    rabbitmq_user = rabbitmq_config.get("username", "user")
    rabbitmq_password = rabbitmq_config.get("password", "")
    
    try:
        auth = (rabbitmq_user, rabbitmq_password)
        
        # Check exchanges
        response = requests.get(f"http://{rabbitmq_host}:15672/api/exchanges", auth=auth, timeout=10)
        if response.status_code == 200:
            exchanges = response.json()
            prisma_exchange = [e for e in exchanges if e.get('name') == 'prisma']
            if prisma_exchange:
                ex = prisma_exchange[0]
                stats = ex.get('message_stats', {})
                logger.info("✅ Found 'prisma' exchange:")
                logger.info(f"  Messages published: {stats.get('publish', 0)}")
                logger.info(f"  Messages published (rate): {stats.get('publish_details', {}).get('rate', 0)}")
                logger.info(f"  Messages in: {stats.get('publish_in', 0)}")
                logger.info(f"  Messages out: {stats.get('publish_out', 0)}")
        
        # Check queues
        response = requests.get(f"http://{rabbitmq_host}:15672/api/queues", auth=auth, timeout=10)
        if response.status_code == 200:
            queues = response.json()
            queues_with_messages = [q for q in queues if q.get('messages', 0) > 0]
            logger.info(f"\nFound {len(queues_with_messages)} queues with messages:")
            for queue in queues_with_messages[:10]:
                logger.info(f"  - {queue.get('name')}: {queue.get('messages', 0)} messages")
    except Exception as e:
        logger.warning(f"⚠️  Error checking RabbitMQ Management API: {e}")
    
    # Step 5: Check MongoDB
    logger.info(f"\n" + "=" * 80)
    logger.info("Step 5: Checking MongoDB for recent alerts")
    logger.info("=" * 80 + "\n")
    
    try:
        mongodb_manager = MongoDBManager(config_manager)
        mongodb_manager.connect()
        db = mongodb_manager.get_database("prisma")
        alerts_collection = db.get_collection("alerts")
        
        # Get recent alerts (last 10 minutes)
        from datetime import datetime, timedelta
        recent_time = datetime.utcnow() - timedelta(minutes=10)
        
        recent_alerts = list(alerts_collection.find({
            "start_time": {"$gte": recent_time.isoformat()}
        }).sort("start_time", -1).limit(10))
        
        if recent_alerts:
            logger.info(f"✅ Found {len(recent_alerts)} recent alerts:")
            for alert in recent_alerts[:5]:
                alert_id = alert.get('ext_id') or alert.get('_id')
                logger.info(f"  - Alert ID: {alert_id}")
                logger.info(f"    Class: {alert.get('class_id')}, Severity: {alert.get('severity')}")
                logger.info(f"    Start Time: {alert.get('start_time')}")
        else:
            logger.info("❌ No recent alerts found in MongoDB")
        
        mongodb_manager.disconnect()
    except Exception as e:
        logger.warning(f"⚠️  Error checking MongoDB: {e}")
    
    # Step 6: Recommendations
    logger.info(f"\n" + "=" * 80)
    logger.info("RECOMMENDATIONS")
    logger.info("=" * 80 + "\n")
    
    logger.info("1. Check if push-to-rabbit endpoint is in a separate service:")
    logger.info("   - Look for Prisma Web App API pod")
    logger.info("   - Check ingress/load balancer configuration")
    logger.info("")
    
    logger.info("2. Check Focus Server logs with more detail:")
    logger.info("   kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=1000 --all-containers=true")
    logger.info("")
    
    logger.info("3. Check logs in real-time while sending alert:")
    logger.info("   Terminal 1: kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -f")
    logger.info("   Terminal 2: Send alert via API")
    logger.info("")
    
    logger.info("4. Check RabbitMQ Management UI:")
    logger.info(f"   URL: http://{rabbitmq_host}:15672")
    logger.info("   - Go to Exchanges → prisma")
    logger.info("   - Check message stats and recent messages")
    logger.info("")
    
    logger.info("5. Check if endpoint logs are at DEBUG level:")
    logger.info("   - May need to enable DEBUG logging")
    logger.info("   - Or check application logs separately")
    
    logger.info("\n✅ Investigation complete!\n")
    
    if ssh_manager:
        ssh_manager.disconnect()


if __name__ == "__main__":
    find_push_to_rabbit_logs()

