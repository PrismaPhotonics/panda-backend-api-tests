#!/usr/bin/env python3
"""
Cleanup All Jobs Script
========================

Script to cleanup all jobs created during test execution.

This script:
1. Lists all active jobs (if API supports it)
2. Cancels all jobs via API
3. Optionally cleans up Kubernetes pods

Usage:
    python scripts/cleanup_all_jobs.py
    python scripts/cleanup_all_jobs.py --k8s  # Also cleanup K8s pods
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def cleanup_jobs_via_api(api: FocusServerAPI, job_ids: list = None):
    """
    Cleanup jobs via Focus Server API.
    
    Args:
        api: Focus Server API client
        job_ids: List of job IDs to cancel (if None, will try to get all)
    """
    logger.info("=" * 80)
    logger.info("Cleaning up jobs via Focus Server API")
    logger.info("=" * 80)
    
    if job_ids:
        logger.info(f"Cleaning up {len(job_ids)} specified jobs...")
    else:
        logger.info("Note: API doesn't support listing all jobs")
        logger.info("Please provide job IDs or use Kubernetes cleanup")
        return
    
    cleaned = 0
    failed = 0
    
    for job_id in job_ids:
        try:
            success = api.cancel_job(job_id)
            if success:
                cleaned += 1
                logger.info(f"✅ Canceled job: {job_id}")
            else:
                failed += 1
                logger.warning(f"⚠️  Failed to cancel job: {job_id}")
        except APIError as e:
            failed += 1
            logger.error(f"❌ API error canceling job {job_id}: {e}")
        except Exception as e:
            failed += 1
            logger.error(f"❌ Unexpected error canceling job {job_id}: {e}")
    
    logger.info("=" * 80)
    logger.info(f"Cleanup complete: {cleaned} canceled, {failed} failed")
    logger.info("=" * 80)


def cleanup_k8s_pods(namespace: str = "panda", label_selector: str = "app=grpc-job"):
    """
    Cleanup Kubernetes pods (gRPC jobs).
    
    Args:
        namespace: Kubernetes namespace
        label_selector: Label selector for pods to delete
    """
    import subprocess
    
    logger.info("=" * 80)
    logger.info("Cleaning up Kubernetes pods")
    logger.info("=" * 80)
    
    try:
        # Get pods
        logger.info(f"Getting pods in namespace '{namespace}' with label '{label_selector}'...")
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", namespace, "-l", label_selector, "-o", "jsonpath={.items[*].metadata.name}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        pod_names = result.stdout.strip().split()
        
        if not pod_names or pod_names == ['']:
            logger.info("No pods found to cleanup")
            return
        
        logger.info(f"Found {len(pod_names)} pods to cleanup")
        
        # Delete pods
        cleaned = 0
        failed = 0
        
        for pod_name in pod_names:
            try:
                logger.info(f"Deleting pod: {pod_name}")
                subprocess.run(
                    ["kubectl", "delete", "pod", pod_name, "-n", namespace],
                    capture_output=True,
                    check=True
                )
                cleaned += 1
                logger.info(f"✅ Deleted pod: {pod_name}")
            except subprocess.CalledProcessError as e:
                failed += 1
                logger.error(f"❌ Failed to delete pod {pod_name}: {e}")
            except Exception as e:
                failed += 1
                logger.error(f"❌ Unexpected error deleting pod {pod_name}: {e}")
        
        logger.info("=" * 80)
        logger.info(f"K8s cleanup complete: {cleaned} deleted, {failed} failed")
        logger.info("=" * 80)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get pods: {e}")
        logger.error("Make sure kubectl is configured and accessible")
    except FileNotFoundError:
        logger.error("kubectl not found. Please install kubectl to cleanup K8s pods")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Cleanup all jobs created during tests")
    parser.add_argument(
        "--k8s",
        action="store_true",
        help="Also cleanup Kubernetes pods (gRPC jobs)"
    )
    parser.add_argument(
        "--namespace",
        default="panda",
        help="Kubernetes namespace (default: panda)"
    )
    parser.add_argument(
        "--label-selector",
        default="app=grpc-job",
        help="Kubernetes label selector (default: app=grpc-job)"
    )
    parser.add_argument(
        "--job-ids",
        nargs="+",
        help="Specific job IDs to cancel (space-separated)"
    )
    parser.add_argument(
        "--env",
        default="staging",
        help="Environment (default: staging)"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("Job Cleanup Script")
    logger.info("=" * 80)
    
    # Initialize API client
    try:
        # Set environment via environment variable or config
        import os
        os.environ['ENV'] = args.env
        
        config_manager = ConfigManager()
        api = FocusServerAPI(config_manager)
        logger.info(f"Initialized API client for environment: {args.env}")
    except Exception as e:
        logger.error(f"Failed to initialize API client: {e}")
        return 1
    
    # Cleanup via API (if job IDs provided)
    if args.job_ids:
        cleanup_jobs_via_api(api, args.job_ids)
    
    # Cleanup K8s pods
    if args.k8s:
        cleanup_k8s_pods(args.namespace, args.label_selector)
    
    if not args.job_ids and not args.k8s:
        logger.warning("No cleanup action specified. Use --job-ids or --k8s")
        logger.info("")
        logger.info("Usage examples:")
        logger.info("  # Cleanup specific jobs:")
        logger.info("  python scripts/cleanup_all_jobs.py --job-ids job1 job2 job3")
        logger.info("")
        logger.info("  # Cleanup K8s pods (gRPC jobs):")
        logger.info("  python scripts/cleanup_all_jobs.py --k8s")
        logger.info("")
        logger.info("  # Cleanup both:")
        logger.info("  python scripts/cleanup_all_jobs.py --job-ids job1 job2 --k8s")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

