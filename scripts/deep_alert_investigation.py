#!/usr/bin/env python3
"""
Deep Alert Investigation Script
חקירה מעמיקה של תהליך ה-alerts במערכת
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

try:
    from src.infrastructure.kubernetes_manager import KubernetesManager
    from src.infrastructure.ssh_manager import SSHManager
    from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager
    from src.infrastructure.mongodb_manager import MongoDBManager
    from src.config.config_manager import ConfigManager
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure you're running from the project root directory")
    exit(1)


class DeepAlertInvestigation:
    """Deep investigation of alert processing flow"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.k8s_manager = None
        self.ssh_manager = None
        self.rabbitmq_manager = None
        self.mongodb_manager = None
        self.report = []
        
    def setup(self):
        """Setup all managers"""
        logger.info("=" * 80)
        logger.info("Setting up investigation infrastructure...")
        logger.info("=" * 80)
        
        try:
            # Kubernetes Manager
            logger.info("Initializing Kubernetes Manager...")
            self.k8s_manager = KubernetesManager(config_manager=self.config_manager)
            logger.info("✅ Kubernetes Manager initialized")
            
            # SSH Manager
            logger.info("Initializing SSH Manager...")
            self.ssh_manager = SSHManager(config_manager=self.config_manager)
            logger.info("✅ SSH Manager initialized")
            
            # RabbitMQ Manager
            logger.info("Initializing RabbitMQ Manager...")
            ssh_config = self.config_manager.get("ssh", {})
            rabbitmq_config = self.config_manager.get("rabbitmq", {})
            self.rabbitmq_manager = RabbitMQConnectionManager(
                host=rabbitmq_config.get("host", "10.10.10.107"),
                port=rabbitmq_config.get("port", 5672),
                username=rabbitmq_config.get("username", "prisma"),
                password=rabbitmq_config.get("password", "prismapanda"),
                ssh_host=ssh_config.get("host"),
                ssh_user=ssh_config.get("user"),
                ssh_password=ssh_config.get("password"),
                ssh_key_file=ssh_config.get("key_file")
            )
            logger.info("✅ RabbitMQ Manager initialized")
            
            # MongoDB Manager
            logger.info("Initializing MongoDB Manager...")
            self.mongodb_manager = MongoDBManager(config_manager=self.config_manager)
            self.mongodb_manager.connect()
            logger.info("✅ MongoDB Manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Error setting up infrastructure: {e}")
            raise
    
    def investigate_ingress_configuration(self) -> Dict[str, Any]:
        """Investigate Ingress configuration"""
        logger.info("\n" + "=" * 80)
        logger.info("STEP 1: Investigating Ingress Configuration")
        logger.info("=" * 80)
        
        findings = {
            "ingress_rules": [],
            "services": [],
            "endpoints": []
        }
        
        try:
            # Get all Ingress resources
            logger.info("Getting Ingress resources...")
            ingress_list = self.k8s_manager.get_ingress(namespace="panda")
            logger.info(f"Found {len(ingress_list)} Ingress resources")
            
            for ingress in ingress_list:
                ingress_name = ingress.get('name', 'unknown')
                logger.info(f"\nIngress: {ingress_name}")
                logger.info(f"  Rules: {json.dumps(ingress.get('rules', []), indent=2)}")
                findings["ingress_rules"].append(ingress)
            
            # Get all Services
            logger.info("\nGetting Services...")
            services = self.k8s_manager.get_services(namespace="panda")
            logger.info(f"Found {len(services)} Services")
            
            for svc in services:
                svc_name = svc.get('name', 'unknown')
                svc_type = svc.get('type', 'unknown')
                cluster_ip = svc.get('cluster_ip', 'unknown')
                ports = svc.get('ports', [])
                logger.info(f"\nService: {svc_name}")
                logger.info(f"  Type: {svc_type}")
                logger.info(f"  Cluster IP: {cluster_ip}")
                logger.info(f"  Ports: {ports}")
                findings["services"].append(svc)
            
            # Get Endpoints
            logger.info("\nGetting Endpoints...")
            endpoints = self.k8s_manager.get_endpoints(namespace="panda")
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
                        logger.info(f"    - {addr.get('ip', 'unknown')} -> {addr.get('targetRef', {}).get('name', 'unknown')}")
                    logger.info(f"  Ports: {ports}")
                findings["endpoints"].append(ep)
            
            # Check Ingress Controller logs for routing info
            logger.info("\nChecking Ingress Controller logs for routing...")
            ingress_pods = self.k8s_manager.get_pods(namespace="kube-system")
            ingress_pod = None
            for pod in ingress_pods:
                if 'ingress-nginx-controller' in pod.get('name', ''):
                    ingress_pod = pod
                    break
            
            if ingress_pod:
                pod_name = ingress_pod['name']
                logger.info(f"Found Ingress Controller pod: {pod_name}")
                logs = self.k8s_manager.get_pod_logs(pod_name, namespace="kube-system", tail_lines=100)
                
                # Look for push-to-rabbit routing
                if "push-to-rabbit" in logs.lower():
                    logger.info("✅ Found push-to-rabbit in Ingress logs")
                    lines = [line for line in logs.split('\n') if "push-to-rabbit" in line.lower()]
                    logger.info(f"Found {len(lines)} matching lines")
                    for line in lines[-3:]:  # Show last 3
                        logger.info(f"  {line[:200]}")
                else:
                    logger.warning("⚠️  push-to-rabbit not found in Ingress logs")
            
        except Exception as e:
            logger.error(f"❌ Error investigating Ingress: {e}")
            findings["error"] = str(e)
        
        return findings
    
    def investigate_rabbitmq_state(self) -> Dict[str, Any]:
        """Investigate RabbitMQ state"""
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2: Investigating RabbitMQ State")
        logger.info("=" * 80)
        
        findings = {
            "exchanges": [],
            "queues": [],
            "bindings": [],
            "connections": []
        }
        
        try:
            # Get exchanges
            logger.info("Getting RabbitMQ exchanges...")
            exchanges = self.rabbitmq_manager.list_exchanges()
            logger.info(f"Found {len(exchanges)} exchanges")
            for exchange in exchanges:
                if exchange.get('name') == 'prisma':
                    logger.info(f"\n✅ Found 'prisma' exchange:")
                    logger.info(f"  Type: {exchange.get('type')}")
                    logger.info(f"  Durable: {exchange.get('durable')}")
                    logger.info(f"  Auto-delete: {exchange.get('auto_delete')}")
                findings["exchanges"].append(exchange)
            
            # Get queues
            logger.info("\nGetting RabbitMQ queues...")
            queues = self.rabbitmq_manager.list_queues()
            logger.info(f"Found {len(queues)} queues")
            
            alert_queues = []
            for queue in queues:
                queue_name = queue.get('name', '')
                messages = queue.get('messages', 0)
                consumers = queue.get('consumers', 0)
                
                if 'alert' in queue_name.lower():
                    alert_queues.append(queue)
                    logger.info(f"\n⚠️  Found alert-related queue: {queue_name}")
                    logger.info(f"  Messages: {messages}")
                    logger.info(f"  Consumers: {consumers}")
                
                findings["queues"].append(queue)
            
            if not alert_queues:
                logger.warning("⚠️  No alert-related queues found!")
            
            # Get bindings for 'prisma' exchange
            logger.info("\nGetting bindings for 'prisma' exchange...")
            bindings = self.rabbitmq_manager.list_bindings(exchange_name='prisma')
            logger.info(f"Found {len(bindings)} bindings for 'prisma' exchange")
            
            alert_bindings = []
            for binding in bindings:
                routing_key = binding.get('routing_key', '')
                queue_name = binding.get('queue', '')
                
                if 'alert' in routing_key.lower() or 'alert' in queue_name.lower():
                    alert_bindings.append(binding)
                    logger.info(f"\n⚠️  Found alert-related binding:")
                    logger.info(f"  Exchange: prisma")
                    logger.info(f"  Routing Key: {routing_key}")
                    logger.info(f"  Queue: {queue_name}")
                
                findings["bindings"].append(binding)
            
            if not alert_bindings:
                logger.warning("⚠️  No alert-related bindings found!")
                logger.info("This means alerts published to 'prisma' exchange with alert routing keys will be dropped!")
            
            # Get connections
            logger.info("\nGetting RabbitMQ connections...")
            connections = self.rabbitmq_manager.list_connections()
            logger.info(f"Found {len(connections)} connections")
            findings["connections"] = connections
            
        except Exception as e:
            logger.error(f"❌ Error investigating RabbitMQ: {e}")
            findings["error"] = str(e)
        
        return findings
    
    def investigate_pods(self) -> Dict[str, Any]:
        """Investigate pods that might handle alerts"""
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3: Investigating Pods")
        logger.info("=" * 80)
        
        findings = {
            "pods": [],
            "focus_server_logs": {},
            "webapp_logs": {}
        }
        
        try:
            # Get all pods
            logger.info("Getting all pods in 'panda' namespace...")
            pods = self.k8s_manager.get_pods(namespace="panda")
            logger.info(f"Found {len(pods)} pods")
            
            focus_server_pods = []
            webapp_pods = []
            
            for pod in pods:
                pod_name = pod.get('name', '')
                status = pod.get('status', '')
                
                if 'focus-server' in pod_name:
                    focus_server_pods.append(pod)
                    logger.info(f"\n✅ Found Focus Server pod: {pod_name} ({status})")
                elif 'webapp' in pod_name.lower():
                    webapp_pods.append(pod)
                    logger.info(f"\n✅ Found WebApp pod: {pod_name} ({status})")
                
                findings["pods"].append(pod)
            
            # Check Focus Server logs
            if focus_server_pods:
                pod_name = focus_server_pods[0]['name']
                logger.info(f"\nChecking Focus Server logs: {pod_name}")
                logs = self.k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=500)
                
                # Search for alert-related keywords
                keywords = ['push-to-rabbit', 'alert', 'api', 'http', 'post']
                found_keywords = {}
                for keyword in keywords:
                    if keyword.lower() in logs.lower():
                        lines = [line for line in logs.split('\n') if keyword.lower() in line.lower()]
                        found_keywords[keyword] = len(lines)
                        logger.info(f"  Found '{keyword}': {len(lines)} occurrences")
                        if len(lines) > 0:
                            logger.info(f"    Last occurrence: {lines[-1][:150]}")
                    else:
                        logger.info(f"  '{keyword}': Not found")
                
                findings["focus_server_logs"] = {
                    "pod": pod_name,
                    "keywords_found": found_keywords,
                    "log_sample": logs[-1000:] if len(logs) > 1000 else logs
                }
            else:
                logger.warning("⚠️  No Focus Server pods found!")
            
            # Check WebApp pods if any
            if webapp_pods:
                for pod in webapp_pods:
                    pod_name = pod['name']
                    logger.info(f"\nChecking WebApp logs: {pod_name}")
                    logs = self.k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=500)
                    
                    if "push-to-rabbit" in logs.lower():
                        logger.info(f"  ✅ Found push-to-rabbit in {pod_name}")
                        lines = [line for line in logs.split('\n') if "push-to-rabbit" in line.lower()]
                        logger.info(f"  Found {len(lines)} matching lines")
                        for line in lines[-3:]:
                            logger.info(f"    {line[:150]}")
                    
                    findings["webapp_logs"][pod_name] = {
                        "log_sample": logs[-1000:] if len(logs) > 1000 else logs
                    }
            else:
                logger.info("No WebApp pods found (might be part of Focus Server)")
            
        except Exception as e:
            logger.error(f"❌ Error investigating pods: {e}")
            findings["error"] = str(e)
        
        return findings
    
    def investigate_mongodb(self, alert_id: Optional[str] = None) -> Dict[str, Any]:
        """Investigate MongoDB for alerts"""
        logger.info("\n" + "=" * 80)
        logger.info("STEP 4: Investigating MongoDB")
        logger.info("=" * 80)
        
        findings = {
            "collections": [],
            "recent_alerts": [],
            "alert_found": False
        }
        
        try:
            db = self.mongodb_manager.get_database("prisma")
            
            # List collections
            logger.info("Listing collections...")
            collections = db.list_collection_names()
            logger.info(f"Found {len(collections)} collections")
            for coll_name in collections:
                if 'alert' in coll_name.lower():
                    logger.info(f"  ⚠️  Alert-related collection: {coll_name}")
                findings["collections"].append(coll_name)
            
            # Check alerts collection
            if 'alerts' in collections:
                logger.info("\nChecking 'alerts' collection...")
                alerts_collection = db.get_collection("alerts")
                
                # Count total alerts
                total_count = alerts_collection.count_documents({})
                logger.info(f"Total alerts in collection: {total_count}")
                
                # Get recent alerts
                recent_alerts = list(alerts_collection.find().sort("_id", -1).limit(10))
                logger.info(f"Recent alerts: {len(recent_alerts)}")
                
                for alert in recent_alerts[:5]:
                    ext_id = alert.get('ext_id', 'N/A')
                    class_id = alert.get('class_id', 'N/A')
                    severity = alert.get('severity', 'N/A')
                    logger.info(f"  Alert: ext_id={ext_id}, class_id={class_id}, severity={severity}")
                
                findings["recent_alerts"] = recent_alerts
                
                # Check for specific alert if provided
                if alert_id:
                    logger.info(f"\nSearching for alert: {alert_id}")
                    alert_doc = alerts_collection.find_one({"ext_id": alert_id})
                    if alert_doc:
                        logger.info(f"✅ Alert found in MongoDB!")
                        logger.info(f"  Class ID: {alert_doc.get('class_id')}")
                        logger.info(f"  Severity: {alert_doc.get('severity')}")
                        logger.info(f"  Distance: {alert_doc.get('distance_m')}")
                        findings["alert_found"] = True
                        findings["alert_document"] = alert_doc
                    else:
                        logger.warning(f"⚠️  Alert {alert_id} NOT found in MongoDB")
            else:
                logger.warning("⚠️  'alerts' collection not found!")
            
        except Exception as e:
            logger.error(f"❌ Error investigating MongoDB: {e}")
            findings["error"] = str(e)
        
        return findings
    
    def send_test_alert(self) -> Dict[str, Any]:
        """Send a test alert and monitor the flow"""
        logger.info("\n" + "=" * 80)
        logger.info("STEP 5: Sending Test Alert and Monitoring")
        logger.info("=" * 80)
        
        import requests
        
        test_alert_id = f"deep-investigation-{int(time.time())}"
        findings = {
            "alert_id": test_alert_id,
            "sent": False,
            "response_status": None,
            "response_body": None
        }
        
        try:
            # Get API configuration
            api_config = self.config_manager.get("focus_server", {})
            base_url = api_config.get("frontend_api_url", "https://10.10.10.100/prisma/api/")
            site_id = self.config_manager.get("site_id", "prisma-210-1000")
            
            if "/internal/sites/" in base_url:
                base_url = base_url.split("/internal/sites/")[0]
            if not base_url.endswith("/"):
                base_url += "/"
            
            logger.info(f"API Base URL: {base_url}")
            logger.info(f"Site ID: {site_id}")
            logger.info(f"Test Alert ID: {test_alert_id}")
            
            # Authenticate
            session = requests.Session()
            session.verify = False
            
            login_url = base_url + "auth/login"
            logger.info(f"\nAuthenticating at: {login_url}")
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
            
            alert_url = base_url + f"{site_id}/api/push-to-rabbit"
            logger.info(f"\nSending alert to: {alert_url}")
            logger.info(f"Payload: {json.dumps(alert_payload, indent=2)}")
            
            alert_resp = session.post(alert_url, json=alert_payload, timeout=15)
            alert_resp.raise_for_status()
            
            logger.info(f"✅ Alert sent successfully!")
            logger.info(f"   Status: {alert_resp.status_code}")
            logger.info(f"   Response: {alert_resp.text[:500]}")
            
            findings["sent"] = True
            findings["response_status"] = alert_resp.status_code
            findings["response_body"] = alert_resp.text
            
            # Wait a bit for processing
            logger.info("\nWaiting 5 seconds for processing...")
            time.sleep(5)
            
            # Check MongoDB
            logger.info("Checking MongoDB for alert...")
            mongo_findings = self.investigate_mongodb(alert_id=test_alert_id)
            findings["mongodb_check"] = mongo_findings
            
            # Check RabbitMQ queues
            logger.info("Checking RabbitMQ queues after alert...")
            queues = self.rabbitmq_manager.list_queues()
            alert_queues = [q for q in queues if 'alert' in q.get('name', '').lower()]
            findings["rabbitmq_queues_after"] = alert_queues
            
            if alert_queues:
                logger.info(f"Found {len(alert_queues)} alert-related queues")
            else:
                logger.warning("No alert-related queues found after sending alert")
            
        except Exception as e:
            logger.error(f"❌ Error sending test alert: {e}")
            findings["error"] = str(e)
        
        return findings
    
    def generate_report(self, findings: Dict[str, Any]):
        """Generate comprehensive report"""
        logger.info("\n" + "=" * 80)
        logger.info("GENERATING COMPREHENSIVE REPORT")
        logger.info("=" * 80)
        
        report_file = f"docs/04_testing/analysis/deep_alert_investigation_{int(time.time())}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(findings, f, indent=2, default=str)
        
        logger.info(f"✅ Report saved to: {report_file}")
        
        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        
        logger.info("\n1. Ingress Configuration:")
        if findings.get("ingress"):
            logger.info(f"   Found {len(findings['ingress'].get('ingress_rules', []))} Ingress rules")
            logger.info(f"   Found {len(findings['ingress'].get('services', []))} Services")
        
        logger.info("\n2. RabbitMQ State:")
        if findings.get("rabbitmq"):
            rabbitmq = findings['rabbitmq']
            logger.info(f"   Exchanges: {len(rabbitmq.get('exchanges', []))}")
            logger.info(f"   Queues: {len(rabbitmq.get('queues', []))}")
            logger.info(f"   Bindings: {len(rabbitmq.get('bindings', []))}")
            
            alert_queues = [q for q in rabbitmq.get('queues', []) if 'alert' in q.get('name', '').lower()]
            alert_bindings = [b for b in rabbitmq.get('bindings', []) if 'alert' in b.get('routing_key', '').lower() or 'alert' in b.get('queue', '').lower()]
            
            if alert_queues:
                logger.info(f"   ⚠️  Alert queues: {len(alert_queues)}")
            else:
                logger.warning("   ❌ No alert queues found!")
            
            if alert_bindings:
                logger.info(f"   ⚠️  Alert bindings: {len(alert_bindings)}")
            else:
                logger.warning("   ❌ No alert bindings found!")
        
        logger.info("\n3. Pods:")
        if findings.get("pods"):
            pods = findings['pods']
            logger.info(f"   Total pods: {len(pods.get('pods', []))}")
            logger.info(f"   Focus Server logs checked: {len(pods.get('focus_server_logs', {}))}")
        
        logger.info("\n4. MongoDB:")
        if findings.get("mongodb"):
            mongodb = findings['mongodb']
            logger.info(f"   Collections: {len(mongodb.get('collections', []))}")
            logger.info(f"   Recent alerts: {len(mongodb.get('recent_alerts', []))}")
            logger.info(f"   Alert found: {mongodb.get('alert_found', False)}")
        
        logger.info("\n5. Test Alert:")
        if findings.get("test_alert"):
            test_alert = findings['test_alert']
            logger.info(f"   Alert ID: {test_alert.get('alert_id')}")
            logger.info(f"   Sent: {test_alert.get('sent', False)}")
            logger.info(f"   Response Status: {test_alert.get('response_status')}")
            if test_alert.get('mongodb_check', {}).get('alert_found'):
                logger.info("   ✅ Alert found in MongoDB")
            else:
                logger.warning("   ❌ Alert NOT found in MongoDB")
    
    def run(self):
        """Run complete investigation"""
        try:
            self.setup()
            
            findings = {}
            
            # Step 1: Ingress Configuration
            findings["ingress"] = self.investigate_ingress_configuration()
            
            # Step 2: RabbitMQ State
            findings["rabbitmq"] = self.investigate_rabbitmq_state()
            
            # Step 3: Pods
            findings["pods"] = self.investigate_pods()
            
            # Step 4: MongoDB (before test alert)
            findings["mongodb_before"] = self.investigate_mongodb()
            
            # Step 5: Send test alert and monitor
            findings["test_alert"] = self.send_test_alert()
            
            # Step 6: MongoDB (after test alert)
            if findings.get("test_alert", {}).get("alert_id"):
                findings["mongodb_after"] = self.investigate_mongodb(
                    alert_id=findings["test_alert"]["alert_id"]
                )
            
            # Generate report
            self.generate_report(findings)
            
        except Exception as e:
            logger.error(f"❌ Investigation failed: {e}")
            raise
        finally:
            if self.mongodb_manager:
                self.mongodb_manager.disconnect()


if __name__ == "__main__":
    config_manager = ConfigManager()
    investigation = DeepAlertInvestigation(config_manager)
    investigation.run()

