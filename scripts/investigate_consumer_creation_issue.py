#!/usr/bin/env python3
"""
Investigate Consumer Creation Issue
===================================

This script performs comprehensive investigation of consumer creation issues:
1. Check Backend Logs for GET /metadata/{job_id} requests
2. Check MongoDB for job registration
3. Check Consumer Service status and logs
4. Check K8s Pod Labels

Usage:
    python scripts/investigate_consumer_creation_issue.py --job-id 19-7
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List

# Add project root to path
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.config_manager import ConfigManager
from src.infrastructure.kubernetes_manager import KubernetesManager
from src.infrastructure.mongodb_manager import MongoDBManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConsumerCreationInvestigator:
    """Investigate consumer creation issues."""
    
    def __init__(self, environment: str = "staging"):
        """Initialize investigator."""
        self.environment = environment
        self.config_manager = ConfigManager(environment)
        self.k8s_manager = KubernetesManager(self.config_manager)
        # MongoDBManager can take optional kubernetes_manager for SSH fallback
        self.mongo_manager = MongoDBManager(self.config_manager, kubernetes_manager=self.k8s_manager)
        
        logger.info(f"Initialized investigator for environment: {environment}")
    
    def investigate(self, job_id: str):
        """Run full investigation."""
        logger.info("=" * 80)
        logger.info(f"INVESTIGATING CONSUMER CREATION ISSUE FOR JOB_ID: {job_id}")
        logger.info("=" * 80)
        
        results = {
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "backend_logs": {},
            "mongodb": {},
            "consumer_service": {},
            "k8s_pods": {},
            "k8s_labels": {}
        }
        
        # 1. Check Backend Logs
        logger.info("\n" + "=" * 80)
        logger.info("1. CHECKING BACKEND LOGS")
        logger.info("=" * 80)
        results["backend_logs"] = self.check_backend_logs(job_id)
        
        # 2. Check MongoDB
        logger.info("\n" + "=" * 80)
        logger.info("2. CHECKING MONGODB")
        logger.info("=" * 80)
        results["mongodb"] = self.check_mongodb(job_id)
        
        # 3. Check Consumer Service
        logger.info("\n" + "=" * 80)
        logger.info("3. CHECKING CONSUMER SERVICE")
        logger.info("=" * 80)
        results["consumer_service"] = self.check_consumer_service(job_id)
        
        # 4. Check K8s Pods and Labels
        logger.info("\n" + "=" * 80)
        logger.info("4. CHECKING K8S PODS AND LABELS")
        logger.info("=" * 80)
        results["k8s_pods"], results["k8s_labels"] = self.check_k8s_pods_and_labels(job_id)
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        self.print_summary(results)
        
        return results
    
    def check_backend_logs(self, job_id: str) -> Dict[str, Any]:
        """Check Backend logs for metadata requests."""
        results = {
            "status": "unknown",
            "logs_found": False,
            "error": None,
            "log_entries": []
        }
        
        try:
            # Find Backend pod
            namespace = self.k8s_manager.k8s_config.get("namespace", "panda")
            backend_selector = "app.kubernetes.io/name=panda-panda-focus-server"
            
            pods = self.k8s_manager.get_pods(
                namespace=namespace,
                label_selector=backend_selector
            )
            
            if not pods:
                results["status"] = "error"
                results["error"] = "No Backend pods found"
                logger.error("❌ No Backend pods found")
                return results
            
            backend_pod = pods[0]
            pod_name = backend_pod.get("name")
            logger.info(f"✅ Found Backend pod: {pod_name}")
            
            # Get logs
            logger.info(f"Fetching logs from {pod_name}...")
            logs = self.k8s_manager.get_pod_logs(
                pod_name=pod_name,
                namespace=namespace,
                tail_lines=1000
            )
            
            # Search for job_id in logs
            log_lines = logs.split('\n')
            matching_lines = [
                line for line in log_lines
                if job_id in line.lower() or f"/metadata/{job_id}" in line.lower()
            ]
            
            if matching_lines:
                results["status"] = "found"
                results["logs_found"] = True
                results["log_entries"] = matching_lines[-20:]  # Last 20 matching lines
                logger.info(f"✅ Found {len(matching_lines)} log entries mentioning {job_id}")
                for line in matching_lines[-10:]:  # Show last 10
                    logger.info(f"  {line}")
            else:
                results["status"] = "not_found"
                results["logs_found"] = False
                logger.warning(f"⚠️  No log entries found mentioning {job_id}")
                logger.info("Showing last 20 log lines:")
                for line in log_lines[-20:]:
                    logger.info(f"  {line}")
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            logger.error(f"❌ Error checking Backend logs: {e}")
        
        return results
    
    def check_mongodb(self, job_id: str) -> Dict[str, Any]:
        """Check MongoDB for job registration."""
        results = {
            "status": "unknown",
            "connected": False,
            "job_found": False,
            "consumer_found": False,
            "error": None,
            "job_data": None,
            "consumer_data": None
        }
        
        try:
            # Connect to MongoDB
            logger.info("Connecting to MongoDB...")
            if not self.mongo_manager.connect():
                results["status"] = "error"
                results["error"] = "Failed to connect to MongoDB"
                logger.error("❌ Failed to connect to MongoDB")
                return results
            
            results["connected"] = True
            logger.info("✅ Connected to MongoDB")
            
            # Get database
            db_name = self.mongo_manager.mongo_config.get("database", "prisma")
            db = self.mongo_manager.get_database(db_name)
            
            # Check for job
            logger.info(f"Searching for job_id: {job_id}...")
            
            # List all collections first
            logger.info("Listing all collections in database...")
            all_collections = db.list_collection_names()
            logger.info(f"Found {len(all_collections)} collections: {', '.join(all_collections[:10])}...")
            
            # Try common collection names
            collections_to_check = ["jobs", "job", "configurations", "configs", "configurations_history", "job_configurations"]
            
            # Also check all collections that might contain job data
            for coll_name in all_collections:
                if any(keyword in coll_name.lower() for keyword in ["job", "config", "task", "consumer"]):
                    if coll_name not in collections_to_check:
                        collections_to_check.append(coll_name)
            
            logger.info(f"Checking {len(collections_to_check)} collections...")
            
            for collection_name in collections_to_check:
                try:
                    collection = db[collection_name]
                    # Try multiple search patterns
                    search_patterns = [
                        {"job_id": job_id},
                        {"_id": job_id},
                        {"jobId": job_id},
                        {"job-id": job_id},
                        {"id": job_id}
                    ]
                    
                    job = None
                    used_pattern = None
                    for pattern in search_patterns:
                        job = collection.find_one(pattern)
                        if job:
                            used_pattern = pattern
                            break
                    
                    if job:
                        results["job_found"] = True
                        results["job_data"] = dict(job)
                        logger.info(f"✅ Found job in collection '{collection_name}' with pattern: {used_pattern}")
                        logger.info(f"  Job data keys: {list(job.keys())}")
                        # Show first few fields
                        for key, value in list(job.items())[:5]:
                            logger.info(f"    {key}: {value}")
                        break
                except Exception as e:
                    logger.debug(f"Collection '{collection_name}' not found or error: {e}")
                    continue
            
            if not results["job_found"]:
                # Try searching by partial match in all collections
                logger.info("Job not found by exact job_id, searching by partial match in all collections...")
                for collection_name in all_collections[:20]:  # Check first 20 collections
                    try:
                        collection = db[collection_name]
                        # Try searching for job_id as substring
                        jobs = list(collection.find({"$or": [
                            {"job_id": {"$regex": job_id, "$options": "i"}},
                            {"_id": {"$regex": job_id, "$options": "i"}},
                            {"jobId": {"$regex": job_id, "$options": "i"}},
                            {"id": {"$regex": job_id, "$options": "i"}}
                        ]}).limit(5))
                        if jobs:
                            logger.info(f"Found {len(jobs)} potential matches in '{collection_name}':")
                            for job in jobs[:2]:  # Show first 2
                                logger.info(f"  Keys: {list(job.keys())}")
                    except Exception:
                        continue
            
            # Check for consumer
            logger.info(f"Searching for consumer with job_id: {job_id}...")
            consumer_collections = ["consumers", "consumer", "consumer_status"]
            
            for collection_name in consumer_collections:
                try:
                    collection = db[collection_name]
                    consumer = collection.find_one({"job_id": job_id})
                    if consumer:
                        results["consumer_found"] = True
                        results["consumer_data"] = dict(consumer)
                        logger.info(f"✅ Found consumer in collection '{collection_name}':")
                        logger.info(f"  {consumer}")
                        break
                except Exception:
                    continue
            
            if not results["job_found"]:
                results["status"] = "job_not_found"
                logger.warning(f"⚠️  Job {job_id} not found in MongoDB")
            elif not results["consumer_found"]:
                results["status"] = "consumer_not_found"
                logger.warning(f"⚠️  Consumer for job {job_id} not found in MongoDB")
            else:
                results["status"] = "found"
                logger.info("✅ Both job and consumer found in MongoDB")
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            logger.error(f"❌ Error checking MongoDB: {e}")
        finally:
            self.mongo_manager.disconnect()
        
        return results
    
    def check_consumer_service(self, job_id: str) -> Dict[str, Any]:
        """Check Consumer Service status and logs."""
        results = {
            "status": "unknown",
            "pods_found": False,
            "pods": [],
            "logs": [],
            "error": None
        }
        
        try:
            namespace = self.k8s_manager.k8s_config.get("namespace", "panda")
            
            # Try to find consumer service pods
            # Common selectors for consumer service
            selectors = [
                "app=consumer",
                "app=consumer-service",
                "component=consumer",
                "name=consumer"
            ]
            
            pods_found = []
            for selector in selectors:
                pods = self.k8s_manager.get_pods(
                    namespace=namespace,
                    label_selector=selector
                )
                if pods:
                    pods_found.extend(pods)
                    logger.info(f"✅ Found {len(pods)} pods with selector '{selector}'")
            
            if not pods_found:
                # Try searching by name pattern
                all_pods = self.k8s_manager.get_pods(namespace=namespace)
                pods_found = [
                    pod for pod in all_pods
                    if "consumer" in pod.get("name", "").lower()
                ]
                if pods_found:
                    logger.info(f"✅ Found {len(pods_found)} pods with 'consumer' in name")
            
            if pods_found:
                results["pods_found"] = True
                results["status"] = "found"
                for pod in pods_found:
                    pod_info = {
                        "name": pod.get("name"),
                        "status": pod.get("status"),
                        "ready": pod.get("ready")
                    }
                    results["pods"].append(pod_info)
                    logger.info(f"  Pod: {pod_info['name']} | Status: {pod_info['status']} | Ready: {pod_info['ready']}")
                    
                    # Get logs
                    try:
                        logs = self.k8s_manager.get_pod_logs(
                            pod_name=pod_info["name"],
                            namespace=namespace,
                            tail_lines=100
                        )
                        log_lines = logs.split('\n')
                        matching_lines = [
                            line for line in log_lines
                            if job_id in line.lower()
                        ]
                        if matching_lines:
                            results["logs"].extend(matching_lines[-10:])
                            logger.info(f"  Found {len(matching_lines)} log entries mentioning {job_id}")
                    except Exception as e:
                        logger.debug(f"Could not get logs from {pod_info['name']}: {e}")
            else:
                results["status"] = "not_found"
                logger.warning("⚠️  No Consumer Service pods found")
                logger.info("Listing all pods in namespace:")
                all_pods = self.k8s_manager.get_pods(namespace=namespace)
                for pod in all_pods[:20]:  # Show first 20
                    logger.info(f"  {pod.get('name')} | {pod.get('status')}")
        
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            logger.error(f"❌ Error checking Consumer Service: {e}")
        
        return results
    
    def check_k8s_pods_and_labels(self, job_id: str):
        """Check K8s pods and labels."""
        pods_results = {
            "status": "unknown",
            "pods_found": False,
            "pods": [],
            "error": None
        }
        
        labels_results = {
            "status": "unknown",
            "labels_analysis": {},
            "error": None
        }
        
        try:
            namespace = self.k8s_manager.k8s_config.get("namespace", "panda")
            
            # Get all pods
            all_pods = self.k8s_manager.get_pods(namespace=namespace)
            
            # Find pods matching job_id
            matching_pods = [
                pod for pod in all_pods
                if job_id in pod.get("name", "")
            ]
            
            if matching_pods:
                pods_results["pods_found"] = True
                pods_results["status"] = "found"
                logger.info(f"✅ Found {len(matching_pods)} pods matching job_id {job_id}")
                
                for pod in matching_pods:
                    pod_name = pod.get("name")
                    labels = pod.get("labels", {})
                    
                    pod_info = {
                        "name": pod_name,
                        "status": pod.get("status"),
                        "ready": pod.get("ready"),
                        "labels": labels
                    }
                    pods_results["pods"].append(pod_info)
                    
                    logger.info(f"\n  Pod: {pod_name}")
                    logger.info(f"    Status: {pod.get('status')}")
                    logger.info(f"    Ready: {pod.get('ready')}")
                    logger.info(f"    Labels:")
                    for key, value in labels.items():
                        logger.info(f"      {key}: {value}")
                    
                    # Check for job_id label
                    if "job_id" in labels:
                        if labels["job_id"] == job_id:
                            logger.info(f"    ✅ job_id label matches: {labels['job_id']}")
                        else:
                            logger.warning(f"    ⚠️  job_id label mismatch: expected {job_id}, got {labels['job_id']}")
                    else:
                        logger.warning(f"    ⚠️  No job_id label found")
                        logger.info(f"    Available labels: {list(labels.keys())}")
                
                # Analyze labels
                labels_results["status"] = "analyzed"
                labels_analysis = {
                    "pods_with_job_id_label": sum(1 for p in matching_pods if "job_id" in p.get("labels", {})),
                    "pods_without_job_id_label": sum(1 for p in matching_pods if "job_id" not in p.get("labels", {})),
                    "common_labels": {}
                }
                
                # Find common labels
                all_labels = {}
                for pod in matching_pods:
                    for key, value in pod.get("labels", {}).items():
                        if key not in all_labels:
                            all_labels[key] = []
                        all_labels[key].append(value)
                
                labels_results["labels_analysis"] = labels_analysis
                logger.info(f"\n  Labels Analysis:")
                logger.info(f"    Pods with job_id label: {labels_analysis['pods_with_job_id_label']}")
                logger.info(f"    Pods without job_id label: {labels_analysis['pods_without_job_id_label']}")
            else:
                pods_results["status"] = "not_found"
                logger.warning(f"⚠️  No pods found matching job_id {job_id}")
        
        except Exception as e:
            pods_results["status"] = "error"
            pods_results["error"] = str(e)
            labels_results["status"] = "error"
            labels_results["error"] = str(e)
            logger.error(f"❌ Error checking K8s pods: {e}")
        
        return pods_results, labels_results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print investigation summary."""
        job_id = results["job_id"]
        
        logger.info(f"\nJob ID: {job_id}")
        logger.info(f"Timestamp: {results['timestamp']}")
        
        # Backend Logs
        logger.info(f"\n📋 Backend Logs:")
        backend = results["backend_logs"]
        if backend["status"] == "found":
            logger.info(f"  ✅ Found logs mentioning {job_id}")
        elif backend["status"] == "not_found":
            logger.warning(f"  ⚠️  No logs found mentioning {job_id}")
        else:
            logger.error(f"  ❌ Error: {backend.get('error')}")
        
        # MongoDB
        logger.info(f"\n📋 MongoDB:")
        mongo = results["mongodb"]
        if mongo.get("connected"):
            if mongo.get("job_found"):
                logger.info(f"  ✅ Job found in MongoDB")
            else:
                logger.warning(f"  ⚠️  Job NOT found in MongoDB")
            
            if mongo.get("consumer_found"):
                logger.info(f"  ✅ Consumer found in MongoDB")
            else:
                logger.warning(f"  ⚠️  Consumer NOT found in MongoDB")
        else:
            logger.error(f"  ❌ Could not connect to MongoDB: {mongo.get('error')}")
        
        # Consumer Service
        logger.info(f"\n📋 Consumer Service:")
        consumer = results["consumer_service"]
        if consumer["pods_found"]:
            logger.info(f"  ✅ Found {len(consumer['pods'])} Consumer Service pod(s)")
        else:
            logger.warning(f"  ⚠️  No Consumer Service pods found")
        
        # K8s Pods
        logger.info(f"\n📋 K8s Pods:")
        pods = results["k8s_pods"]
        if pods["pods_found"]:
            logger.info(f"  ✅ Found {len(pods['pods'])} pod(s) matching {job_id}")
            for pod in pods["pods"]:
                has_job_id_label = "job_id" in pod.get("labels", {})
                if has_job_id_label:
                    logger.info(f"    ✅ {pod['name']} has job_id label")
                else:
                    logger.warning(f"    ⚠️  {pod['name']} missing job_id label")
        else:
            logger.warning(f"  ⚠️  No pods found matching {job_id}")
        
        # Recommendations
        logger.info(f"\n💡 RECOMMENDATIONS:")
        
        if not mongo.get("job_found"):
            logger.info("  1. ⚠️  Job not found in MongoDB - Backend may not have saved the job")
        
        if not mongo.get("consumer_found"):
            logger.info("  2. ⚠️  Consumer not found in MongoDB - Consumer Service may not have created it")
        
        if pods["pods_found"]:
            pods_without_label = [
                p for p in pods["pods"]
                if "job_id" not in p.get("labels", {})
            ]
            if pods_without_label:
                logger.info(f"  3. ⚠️  {len(pods_without_label)} pod(s) missing job_id label - Backend may not find them")
                logger.info("     → Consider adding job_id label to Pods during creation")
        
        if not consumer["pods_found"]:
            logger.info("  4. ⚠️  Consumer Service not found - may not be running or named differently")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Investigate consumer creation issues"
    )
    parser.add_argument(
        "--job-id",
        required=True,
        help="Job ID to investigate (e.g., '19-7')"
    )
    parser.add_argument(
        "--environment",
        default="staging",
        choices=["staging", "production", "local"],
        help="Environment to investigate"
    )
    
    args = parser.parse_args()
    
    investigator = ConsumerCreationInvestigator(environment=args.environment)
    results = investigator.investigate(args.job_id)
    
    # Exit with error code if issues found
    if results["mongodb"].get("status") == "error" or not results["mongodb"].get("job_found"):
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()

