"""
Environment Cleanup - Clean up all resources created during test execution

This module provides comprehensive cleanup functionality to attend:
- Delete all Kubernetes jobs created during tests
- Delete all gRPC services
- Cancel all active jobs via Focus Server API
- Clean up orphaned pods and services

Author: QA Automation Team
Date: 2025-10-29
"""

import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.apis.focus_server_api import FocusServerAPI
from src.infrastructure.kubernetes_manager import KubernetesManager
from src.core.exceptions import InfrastructureError


class EnvironmentCleanup:
    """
    Comprehensive environment cleanup after test execution.
    
    Cleans up:
    - All Kubernetes jobs (grpc-job-*, cleanup-job-*)
    - All gRPC services (grpc-service-*)
    - All active jobs via Focus Server API
    - Orphaned pods and resources
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize environment cleanup.
        
        Args:
            config_manager: Optional config manager (creates new if not provided)
        """
        self.logger = logging.getLogger(__name__)
        
        if config_manager is None:
            config_manager = ConfigManager()
        
        self.config_manager = config_manager
        
        # Initialize clients
        try:
            self.focus_server_api = FocusServerAPI(config_manager)
            self.logger.info("Focus Server API initialized for cleanup")
        except Exception as e:
            self.logger.warning(f"Focus Server API not available: {e}")
            self.focus_server_api = None
        
        try:
            self.k8s_manager = KubernetesManager(config_manager)
            self.logger.info("Kubernetes Manager initialized for cleanup")
        except Exception as e:
            self.logger.warning(f"Kubernetes Manager not available: {e}")
            self.k8s_manager = None
        
        # Get namespace
        k8s_config = config_manager.get_kubernetes_config()
        self.namespace = k8s_config.get("namespace", "panda")
        
        # Statistics
        self.stats = {
            "jobs_cancelled": 0,
            "jobs_deleted": 0,
            "services_deleted": 0,
            "pods_deleted": 0,
            "errors": 0
        }
    
    def cleanup_all(self) -> Dict[str, Any]:
        """
        Perform comprehensive cleanup of all test resources.
        
        Returns:
            Dictionary with cleanup statistics
        """
        self.logger.info("\n" + "="*80)
        self.logger.info("ENVIRONMENT CLEANUP: Starting comprehensive cleanup...")
        self.logger.info("="*80 + "\n")
        
        # Reset statistics
        self.stats = {
            "jobs_cancelled": 0,
            "jobs_deleted": 0,
            "services_deleted": 0,
            "pods_deleted": 0,
            "errors": 0
        }
        
        try:
            # Step 1: Cancel all active jobs via Focus Server API
            self._cancel_active_jobs()
            
            # Step 2: Delete all Kubernetes jobs
            self._cleanup_kubernetes_jobs()
            
            # Step 3: Delete all gRPC services
            self._cleanup_grpc_services()
            
            # Step 4: Cleanup orphaned pods
            self._cleanup_orphaned_pods()
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            self.stats["errors"] += 1
        
        # Summary
        self.logger.info("\n" + "="*80)
        self.logger.info("CLEANUP SUMMARY")
        self.logger.info("="*80)
        self.logger.info(f"Jobs cancelled (via API):     {self.stats['jobs_cancelled']}")
        self.logger.info(f"Jobs deleted (K8s):           {self.stats['jobs_deleted']}")
        self.logger.info(f"Services deleted:             {self.stats['services_deleted']}")
        self.logger.info(f"Orphaned pods deleted:        {self.stats['pods_deleted']}")
        self.logger.info(f"Errors:                       {self.stats['errors']}")
        self.logger.info("="*80 + "\n")
        
        return self.stats
    
    def _cancel_active_jobs(self):
        """Cancel all active jobs via Focus Server API."""
        if not self.focus_server_api:
            self.logger.info("Skipping API job cancellation (API not available)")
            return
        
        self.logger.info("Step 1: Cancelling active jobs via Focus Server API...")
        
        try:
            # Get all active jobs - we need to find jobs first
            # Since we don't have a direct "list jobs" endpoint, we'll rely on K8s
            # But we can try to cancel jobs we find in K8s
            
            # Get all grpc jobs from K8s
            if self.k8s_manager:
                jobs = self.k8s_manager.get_jobs(self.namespace)
                grpc_jobs = [j for j in jobs if j.get("name", "").startswith("grpc-job-")]
                
                for job in grpc_jobs:
                    job_name = job.get("name", "")
                    # Extract job_id from job name (format: grpc-job-{job_id})
                    if job_name.startswith("grpc-job-"):
                        job_id = job_name.replace("grpc-job-", "")
                        
                        try:
                            if self.focus_server_api.cancel_job(job_id):
                                self.stats["jobs_cancelled"] += 1
                                self.logger.debug(f"  ✓ Cancelled job: {job_id}")
                            time.sleep(0.5)  # Small delay to avoid rate limiting
                        except Exception as e:
                            self.logger.debug(f"  ✗ Failed to cancel job {job_id}: {e}")
                            self.stats["errors"] += 1
            
            self.logger.info(f"  ✓ Cancelled {self.stats['jobs_cancelled']} jobs via API")
            
        except Exception as e:
            self.logger.warning(f"  ✗ Error cancelling jobs via API: {e}")
            self.stats["errors"] += 1
    
    def _cleanup_kubernetes_jobs(self):
        """Delete all Kubernetes jobs related to test execution."""
        if not self.k8s_manager:
            self.logger.info("Skipping Kubernetes job cleanup (K8s not available)")
            return
        
        self.logger.info("Step 2: Deleting Kubernetes jobs...")
        
        try:
            # Get all jobs
            jobs = self.k8s_manager.get_jobs(self.namespace)
            
            # Filter test-related jobs
            test_jobs = [
                j for j in jobs 
                if j.get("name", "").startswith(("grpc-job-", "cleanup-job-"))
            ]
            
            self.logger.info(f"  Found {len(test_jobs)} test-related jobs")
            
            # Delete each job
            for job in test_jobs:
                job_name = job.get("name", "")
                try:
                    if self.k8s_manager.delete_job(job_name, self.namespace):
                        self.stats["jobs_deleted"] += 1
                        self.logger.debug(f"  ✓ Deleted job: {job_name}")
                    time.sleep(0.3)  # Small delay
                except Exception as e:
                    self.logger.debug(f"  ✗ Failed to delete job {job_name}: {e}")
                    self.stats["errors"] += 1
            
            self.logger.info(f"  ✓ Deleted {self.stats['jobs_deleted']} Kubernetes jobs")
            
        except Exception as e:
            self.logger.warning(f"  ✗ Error deleting Kubernetes jobs: {e}")
            self.stats["errors"] += 1
    
    def _cleanup_grpc_services(self):
        """Delete all gRPC services."""
        if not self.k8s_manager:
            self.logger.info("Skipping service cleanup (K8s not available)")
            return
        
        self.logger.info("Step 3: Deleting gRPC services...")
        
        try:
            # Get all services directly from K8s API
            from kubernetes import client
            from kubernetes.client.rest import ApiException
            
            if self.k8s_manager.k8s_core_v1 is None:
                self.logger.info("  Kubernetes API not available")
                return
            
            services = self.k8s_manager.k8s_core_v1.list_namespaced_service(
                namespace=self.namespace
            )
            
            # Filter test-related services
            grpc_services = [
                s for s in services.items
                if s.metadata.name.startswith("grpc-service-")
            ]
            
            self.logger.info(f"  Found {len(grpc_services)} gRPC services")
            
            # Delete each service
            for service in grpc_services:
                service_name = service.metadata.name
                try:
                    self.k8s_manager.k8s_core_v1.delete_namespaced_service(
                        name=service_name,
                        namespace=self.namespace
                    )
                    self.stats["services_deleted"] += 1
                    self.logger.debug(f"  ✓ Deleted service: {service_name}")
                    time.sleep(0.2)
                except ApiException as e:
                    if e.status == 404:
                        # Service already deleted, that's OK
                        pass
                    else:
                        self.logger.debug(f"  ✗ Failed to delete service {service_name}: {e}")
                        self.stats["errors"] += 1
                except Exception as e:
                    self.logger.debug(f"  ✗ Failed to delete service {service_name}: {e}")
                    self.stats["errors"] += 1
            
            self.logger.info(f"  ✓ Deleted {self.stats['services_deleted']} gRPC services")
            
        except Exception as e:
            self.logger.warning(f"  ✗ Error deleting services: {e}")
            self.stats["errors"] += 1
    
    def _cleanup_orphaned_pods(self):
        """Clean up orphaned pods from failed jobs."""
        if not self.k8s_manager:
            self.logger.info("Skipping pod cleanup (K8s not available)")
            return
        
        self.logger.info("Step 4: Cleaning up orphaned pods...")
        
        try:
            # Get all pods
            pods = self.k8s_manager.get_pods(self.namespace)
            
            # Filter test-related pods in failed/error states
            orphaned_pods = [
                p for p in pods
                if (p.get("name", "").startswith(("grpc-job-", "cleanup-job-")) and
                    p.get("status") in ("Failed", "Error", "Unknown"))
            ]
            
            if orphaned_pods:
                self.logger.info(f"  Found {len(orphaned_pods)} orphaned pods")
                
                for pod in orphaned_pods:
                    pod_name = pod.get("name", "")
                    try:
                        if self.k8s_manager.delete_pod(pod_name, self.namespace):
                            self.stats["pods_deleted"] += 1
                            self.logger.debug(f"  ✓ Deleted pod: {pod_name}")
                        time.sleep(0.2)
                    except Exception as e:
                        self.logger.debug(f"  ✗ Failed to delete pod {pod_name}: {e}")
                        self.stats["errors"] += 1
            else:
                self.logger.info("  No orphaned pods found")
            
            self.logger.info(f"  ✓ Deleted {self.stats['pods_deleted']} orphaned pods")
            
        except Exception as e:
            self.logger.warning(f"  ✗ Error cleaning up pods: {e}")
            self.stats["errors"] += 1


def main():
    """Main entry point for standalone cleanup execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean up all test resources from environment"
    )
    
    parser.add_argument(
        "--env",
        default="new_production",
        help="Environment to clean (default: new_production)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Initialize cleanup
    config_manager = ConfigManager(args.env)
    cleanup = EnvironmentCleanup(config_manager)
    
    # Execute cleanup
    stats = cleanup.cleanup_all()
    
    # Exit with error code if errors occurred
    sys.exit(1 if stats["errors"] > 0 else 0)


if __name__ == "__main__":
    main()

