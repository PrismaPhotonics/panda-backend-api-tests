#!/usr/bin/env python3
"""
Kubernetes Agent - Interactive K8s Management Tool
==================================================

Interactive agent for managing Kubernetes environments (staging and production/kefar saba).

Features:
- Connect to both staging and production K8s environments
- Monitor pods, jobs, services, deployments
- Delete gRPC jobs and pods (with confirmation)
- Execute various K8s operations
- Safe operations with confirmation prompts

Usage:
    python scripts/k8s_agent.py
    python scripts/k8s_agent.py --env staging
    python scripts/k8s_agent.py --env production
"""

import sys
import os
import json
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.infrastructure.kubernetes_manager import KubernetesManager
from src.core.exceptions import InfrastructureError


def log_step(message: str, level: str = "INFO"):
    """
    Log a step with timestamp.
    
    Args:
        message: Message to log
        level: Log level (INFO, DEBUG, WARNING, ERROR)
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {
        "INFO": "ℹ️",
        "DEBUG": "🔍",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "SUCCESS": "✅"
    }.get(level, "•")
    
    print(f"[{timestamp}] {prefix} {message}")


def log_progress(message: str):
    """Log progress message."""
    log_step(message, "DEBUG")


def log_success(message: str):
    """Log success message."""
    log_step(message, "SUCCESS")


class K8sAgent:
    """
    Interactive Kubernetes management agent.
    
    Provides interactive CLI for managing K8s environments with:
    - Environment selection (staging/production)
    - Monitoring capabilities
    - Safe deletion operations (with confirmation)
    - Configuration management
    """
    
    def __init__(self, environment: str = "staging"):
        """
        Initialize K8s Agent.
        
        Args:
            environment: Environment name (staging or production)
        """
        self.environment = environment
        self.config_manager = ConfigManager(env=environment)
        self.k8s_manager: Optional[KubernetesManager] = None
        self.connected = False
        
        # Environment display names
        self.env_display_names = {
            "staging": "Staging (10.10.10.100)",
            "production": "Production - Kefar Saba (10.10.100.100)"
        }
        
    def connect(self) -> bool:
        """
        Connect to Kubernetes cluster.
        
        Returns:
            True if connection successful
        """
        start_time = time.time()
        env_name = self.env_display_names.get(self.environment, self.environment)
        
        try:
            print(f"\n🔌 Connecting to {env_name}...")
            log_progress("Initializing Kubernetes Manager...")
            
            self.k8s_manager = KubernetesManager(self.config_manager)
            self.connected = True
            log_success("Kubernetes Manager initialized")
            
            # Test connection by getting cluster info
            try:
                log_progress("Testing connection by retrieving cluster info...")
                cluster_info = self.k8s_manager.get_cluster_info()
                
                elapsed = time.time() - start_time
                print(f"✅ Connected successfully! (took {elapsed:.2f}s)")
                print(f"   Cluster Version: {cluster_info.get('version', 'unknown')}")
                print(f"   Nodes: {cluster_info.get('node_count', 0)}")
                return True
            except Exception as e:
                elapsed = time.time() - start_time
                log_step(f"Connection established but cluster info unavailable: {e}", "WARNING")
                print(f"⚠️  Connection established (took {elapsed:.2f}s) but cluster info unavailable")
                return True  # Still consider connected if manager initialized
                
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Failed to connect (took {elapsed:.2f}s): {e}")
            self.connected = False
            return False
    
    def _confirm_action(self, action: str, resource: str, resource_name: str = "") -> bool:
        """
        Confirm destructive action with user.
        
        Args:
            action: Action description (e.g., "delete", "restart")
            resource: Resource type (e.g., "pod", "job")
            resource_name: Name of the resource
            
        Returns:
            True if user confirmed, False otherwise
        """
        resource_display = f" {resource_name}" if resource_name else ""
        prompt = f"\n⚠️  Are you sure you want to {action} {resource}{resource_display}? (yes/no): "
        
        response = input(prompt).strip().lower()
        return response in ["yes", "y"]
    
    def _confirm_multiple(self, action: str, resource: str, count: int) -> bool:
        """
        Confirm multiple resource deletion.
        
        Args:
            action: Action description
            resource: Resource type
            count: Number of resources
            
        Returns:
            True if user confirmed, False otherwise
        """
        prompt = f"\n⚠️  Are you sure you want to {action} {count} {resource}(s)? (yes/no): "
        response = input(prompt).strip().lower()
        return response in ["yes", "y"]
    
    def list_pods(self, label_selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List pods in the cluster.
        
        Args:
            label_selector: Optional label selector for filtering
            
        Returns:
            List of pod information dictionaries
        """
        if not self.connected:
            print("❌ Not connected to cluster. Use 'connect' first.")
            return []
        
        start_time = time.time()
        filter_msg = f" with label '{label_selector}'" if label_selector else ""
        
        try:
            log_progress(f"Retrieving pods{filter_msg}...")
            pods = self.k8s_manager.get_pods(label_selector=label_selector)
            
            elapsed = time.time() - start_time
            
            if not pods:
                print(f"\n📦 No pods found{filter_msg} (took {elapsed:.2f}s)")
                return []
            
            log_success(f"Retrieved {len(pods)} pod(s) in {elapsed:.2f}s")
            print(f"\n📦 Found {len(pods)} pod(s):")
            print("-" * 100)
            print(f"{'NAME':<50} {'STATUS':<15} {'READY':<10} {'RESTARTS':<10} {'NODE':<20}")
            print("-" * 100)
            
            for pod in pods:
                name = pod.get("name", "unknown")[:48]
                status = pod.get("status", "Unknown")[:13]
                ready = pod.get("ready", "Unknown")[:8]
                restarts = str(pod.get("restart_count", 0))[:8]
                node = pod.get("node_name", "unknown")[:18]
                
                print(f"{name:<50} {status:<15} {ready:<10} {restarts:<10} {node:<20}")
            
            return pods
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Failed to list pods (took {elapsed:.2f}s): {e}")
            return []
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """
        List jobs in the cluster.
        
        Returns:
            List of job information dictionaries
        """
        if not self.connected:
            print("❌ Not connected to cluster. Use 'connect' first.")
            return []
        
        start_time = time.time()
        
        try:
            log_progress("Retrieving jobs...")
            jobs = self.k8s_manager.get_jobs()
            
            elapsed = time.time() - start_time
            
            if not jobs:
                print(f"\n📋 No jobs found (took {elapsed:.2f}s)")
                return []
            
            log_success(f"Retrieved {len(jobs)} job(s) in {elapsed:.2f}s")
            print(f"\n📋 Found {len(jobs)} job(s):")
            print("-" * 100)
            print(f"{'NAME':<50} {'STATUS':<15} {'SUCCEEDED':<12} {'FAILED':<12}")
            print("-" * 100)
            
            for job in jobs:
                name = job.get("name", "unknown")[:48]
                status = job.get("status", "Unknown")[:13]
                succeeded = str(job.get("succeeded", 0))[:10]
                failed = str(job.get("failed", 0))[:10]
                
                print(f"{name:<50} {status:<15} {succeeded:<12} {failed:<12}")
            
            return jobs
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Failed to list jobs (took {elapsed:.2f}s): {e}")
            return []
    
    def list_deployments(self) -> List[Dict[str, Any]]:
        """
        List deployments in the cluster.
        
        Returns:
            List of deployment information dictionaries
        """
        if not self.connected:
            print("❌ Not connected to cluster. Use 'connect' first.")
            return []
        
        start_time = time.time()
        
        try:
            log_progress("Retrieving deployments...")
            deployments = self.k8s_manager.get_deployments()
            
            elapsed = time.time() - start_time
            
            if not deployments:
                print(f"\n🚀 No deployments found (took {elapsed:.2f}s)")
                return []
            
            log_success(f"Retrieved {len(deployments)} deployment(s) in {elapsed:.2f}s")
            print(f"\n🚀 Found {len(deployments)} deployment(s):")
            print("-" * 100)
            print(f"{'NAME':<50} {'REPLICAS':<15} {'READY':<15} {'AVAILABLE':<15}")
            print("-" * 100)
            
            for deployment in deployments:
                name = deployment.get("name", "unknown")[:48]
                replicas = str(deployment.get("replicas", 0))[:13]
                ready = str(deployment.get("ready_replicas", 0))[:13]
                available = str(deployment.get("available_replicas", 0))[:13]
                
                print(f"{name:<50} {replicas:<15} {ready:<15} {available:<15}")
            
            return deployments
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Failed to list deployments (took {elapsed:.2f}s): {e}")
            return []
    
    def list_grpc_jobs(self) -> List[Dict[str, Any]]:
        """
        List gRPC job pods specifically.
        
        Returns:
            List of gRPC job pod information dictionaries
        """
        log_progress("Retrieving gRPC job pods (label: app=grpc-service)...")
        return self.list_pods(label_selector="app=grpc-service")
    
    def delete_pod(self, pod_name: str) -> bool:
        """
        Delete a pod (with confirmation).
        
        Args:
            pod_name: Name of the pod to delete
            
        Returns:
            True if deletion successful
        """
        if not self.connected:
            print("❌ Not connected to cluster. Use 'connect' first.")
            return False
        
        start_time = time.time()
        
        # Get pod info first
        try:
            log_progress(f"Retrieving pod information for '{pod_name}'...")
            pod_info = self.k8s_manager.get_pod_by_name(pod_name)
            if not pod_info:
                print(f"❌ Pod '{pod_name}' not found")
                return False
            
            log_success("Pod information retrieved")
            print(f"\n📦 Pod Information:")
            print(f"   Name: {pod_info.get('name')}")
            print(f"   Status: {pod_info.get('status')}")
            print(f"   Ready: {pod_info.get('ready')}")
            print(f"   Node: {pod_info.get('node_name')}")
            
        except Exception as e:
            log_step(f"Could not retrieve pod info: {e}", "WARNING")
            print(f"⚠️  Could not retrieve pod info: {e}")
        
        # Confirm deletion
        if not self._confirm_action("delete", "pod", pod_name):
            print("❌ Deletion cancelled by user")
            return False
        
        try:
            log_progress(f"Deleting pod '{pod_name}'...")
            success = self.k8s_manager.delete_pod(pod_name)
            
            elapsed = time.time() - start_time
            
            if success:
                print(f"✅ Pod '{pod_name}' deleted successfully (took {elapsed:.2f}s)")
            else:
                print(f"❌ Failed to delete pod '{pod_name}' (took {elapsed:.2f}s)")
            return success
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Error deleting pod (took {elapsed:.2f}s): {e}")
            return False
    
    def delete_grpc_jobs(self, pattern: Optional[str] = None) -> int:
        """
        Delete gRPC job pods (with confirmation).
        
        Args:
            pattern: Optional pattern to filter pod names
            
        Returns:
            Number of pods deleted
        """
        if not self.connected:
            print("❌ Not connected to cluster. Use 'connect' first.")
            return 0
        
        start_time = time.time()
        
        # Get gRPC job pods
        log_progress("Retrieving gRPC job pods...")
        pods = self.list_grpc_jobs()
        
        if not pods:
            print("📦 No gRPC job pods found")
            return 0
        
        # Filter by pattern if provided
        if pattern:
            log_progress(f"Filtering pods by pattern '{pattern}'...")
            pods = [p for p in pods if pattern in p.get("name", "")]
            if not pods:
                print(f"📦 No gRPC job pods found matching pattern '{pattern}'")
                return 0
            log_success(f"Found {len(pods)} pod(s) matching pattern")
        
        # Show pods to be deleted
        print(f"\n📦 Pods to be deleted ({len(pods)}):")
        for pod in pods:
            print(f"   - {pod.get('name')} (Status: {pod.get('status')})")
        
        # Confirm deletion
        if not self._confirm_multiple("delete", "gRPC job pod", len(pods)):
            print("❌ Deletion cancelled by user")
            return 0
        
        # Delete pods
        log_progress(f"Starting deletion of {len(pods)} pod(s)...")
        deleted = 0
        failed = 0
        
        for idx, pod in enumerate(pods, 1):
            pod_name = pod.get("name")
            log_progress(f"Deleting pod {idx}/{len(pods)}: {pod_name}...")
            try:
                if self.k8s_manager.delete_pod(pod_name):
                    print(f"✅ Deleted pod: {pod_name}")
                    deleted += 1
                else:
                    print(f"❌ Failed to delete pod: {pod_name}")
                    failed += 1
            except Exception as e:
                print(f"❌ Error deleting pod {pod_name}: {e}")
                failed += 1
        
        elapsed = time.time() - start_time
        print(f"\n📊 Summary: {deleted} deleted, {failed} failed (total time: {elapsed:.2f}s)")
        return deleted
    
    def delete_pods_by_status(self, status: str) -> int:
        """
        Delete pods by status (with confirmation).
        
        Args:
            status: Pod status to filter by (Running, Pending, Failed, Succeeded, etc.)
            
        Returns:
            Number of pods deleted
        """
        if not self.connected:
            print("❌ Not connected to cluster. Use 'connect' first.")
            return 0
        
        start_time = time.time()
        
        # Get all pods
        log_progress(f"Retrieving pods with status '{status}'...")
        all_pods = self.list_pods()
        
        if not all_pods:
            print("📦 No pods found")
            return 0
        
        # Filter by status
        matching_pods = [p for p in all_pods if p.get("status", "").lower() == status.lower()]
        
        if not matching_pods:
            elapsed = time.time() - start_time
            print(f"📦 No pods found with status '{status}' (took {elapsed:.2f}s)")
            return 0
        
        log_success(f"Found {len(matching_pods)} pod(s) with status '{status}'")
        
        # Show pods to be deleted
        print(f"\n📦 Pods to be deleted ({len(matching_pods)}):")
        for pod in matching_pods:
            print(f"   - {pod.get('name')} (Status: {pod.get('status')}, Node: {pod.get('node_name')})")
        
        # Confirm deletion
        if not self._confirm_multiple("delete", f"pod with status '{status}'", len(matching_pods)):
            print("❌ Deletion cancelled by user")
            return 0
        
        # Delete pods
        log_progress(f"Starting deletion of {len(matching_pods)} pod(s) with status '{status}'...")
        deleted = 0
        failed = 0
        
        for idx, pod in enumerate(matching_pods, 1):
            pod_name = pod.get("name")
            log_progress(f"Deleting pod {idx}/{len(matching_pods)}: {pod_name}...")
            try:
                if self.k8s_manager.delete_pod(pod_name):
                    print(f"✅ Deleted pod: {pod_name}")
                    deleted += 1
                else:
                    print(f"❌ Failed to delete pod: {pod_name}")
                    failed += 1
            except Exception as e:
                print(f"❌ Error deleting pod {pod_name}: {e}")
                failed += 1
        
        elapsed = time.time() - start_time
        print(f"\n📊 Summary: {deleted} deleted, {failed} failed (total time: {elapsed:.2f}s)")
        return deleted
    
    def quick_cleanup_via_kubectl(self) -> bool:
        """
        Run the quick cleanup kubectl command directly via SSH.
        
        This executes the recommended command:
        kubectl get jobs -n panda -o name | grep -E "(grpc-job|cleanup-job)" | xargs -I {} kubectl delete {} -n panda
        
        Returns:
            True if command executed successfully
        """
        if not self.connected:
            print("❌ Not connected to cluster. Use 'connect' first.")
            return False
        
        if not self.k8s_manager:
            print("❌ Kubernetes manager not initialized")
            return False
        
        # Ensure SSH is available
        if not self.k8s_manager.use_ssh_fallback:
            print("⚠️  This command requires SSH access. Trying to initialize SSH fallback...")
            if not self.k8s_manager._init_ssh_fallback():
                print("❌ SSH fallback not available. Cannot execute kubectl command directly.")
                print("\n💡 Alternative: Use command 18 (Delete all gRPC jobs) instead.")
                return False
        
        start_time = time.time()
        
        # The magic command!
        command = "kubectl get jobs -n panda -o name | grep -E '(grpc-job|cleanup-job)' | xargs -I {} kubectl delete {} -n panda"
        
        print(f"\n🚀 Executing quick cleanup command via SSH...")
        print(f"Command: {command}")
        print("")
        
        # Confirm execution
        confirm = input("⚠️  This will delete all gRPC and cleanup jobs. Continue? (yes/no): ").strip().lower()
        if confirm not in ["yes", "y"]:
            print("❌ Command cancelled")
            return False
        
        try:
            # Execute via SSH
            namespace = self.k8s_manager.k8s_config.get("namespace", "panda")
            # Note: This is a shell command, not a kubectl command, so we use SSH directly
            full_command = f"kubectl get jobs -n {namespace} -o name | grep -E '(grpc-job|cleanup-job)' | xargs -I {{}} kubectl delete {{}} -n {namespace}"
            
            log_progress("Executing cleanup command via SSH...")
            
            # Use SSH manager directly for shell commands
            if not self.k8s_manager.ssh_manager:
                if not self.k8s_manager._init_ssh_fallback():
                    print("❌ Failed to initialize SSH connection")
                    return False
            
            if not self.k8s_manager.ssh_manager.connected:
                if not self.k8s_manager.ssh_manager.connect():
                    print("❌ Failed to connect via SSH")
                    return False
            
            result = self.k8s_manager.ssh_manager.execute_command(full_command, timeout=120)
            
            elapsed = time.time() - start_time
            
            if result["success"]:
                print(f"\n✅ Command executed successfully (took {elapsed:.2f}s)")
                if result.get("stdout"):
                    print(f"Output:\n{result['stdout']}")
                return True
            else:
                print(f"\n❌ Command failed (took {elapsed:.2f}s)")
                if result.get("stderr"):
                    print(f"Error:\n{result['stderr']}")
                return False
                
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"\n❌ Error executing command (took {elapsed:.2f}s): {e}")
            return False
    
    def delete_all_grpc_jobs(self, include_cleanup: bool = True) -> int:
        """
        Delete all gRPC Kubernetes jobs (this will stop pods from recreating).
        
        Args:
            include_cleanup: If True, also delete cleanup jobs
            
        Returns:
            Number of jobs deleted
        """
        if not self.connected:
            print("❌ Not connected to cluster. Use 'connect' first.")
            return 0
        
        start_time = time.time()
        
        # Get all jobs
        log_progress("Retrieving all jobs...")
        all_jobs = self.list_jobs()
        
        if not all_jobs:
            print("📋 No jobs found")
            return 0
        
        # Filter gRPC jobs (usually start with "grpc-job-")
        grpc_jobs = [j for j in all_jobs if j.get("name", "").startswith("grpc-job-")]
        
        # Filter cleanup jobs if requested
        cleanup_jobs = []
        if include_cleanup:
            cleanup_jobs = [j for j in all_jobs if j.get("name", "").startswith("cleanup-job-")]
        
        all_jobs_to_delete = grpc_jobs + cleanup_jobs
        
        if not all_jobs_to_delete:
            elapsed = time.time() - start_time
            print(f"📋 No gRPC or cleanup jobs found (took {elapsed:.2f}s)")
            return 0
        
        log_success(f"Found {len(grpc_jobs)} gRPC job(s) and {len(cleanup_jobs)} cleanup job(s)")
        
        # Show jobs to be deleted
        print(f"\n📋 Jobs to be deleted ({len(all_jobs_to_delete)}):")
        if grpc_jobs:
            print(f"\n  gRPC Jobs ({len(grpc_jobs)}):")
            for job in grpc_jobs[:10]:  # Show first 10
                print(f"   - {job.get('name')} (Status: {job.get('status')})")
            if len(grpc_jobs) > 10:
                print(f"   ... and {len(grpc_jobs) - 10} more")
        
        if cleanup_jobs:
            print(f"\n  Cleanup Jobs ({len(cleanup_jobs)}):")
            for job in cleanup_jobs[:10]:  # Show first 10
                print(f"   - {job.get('name')} (Status: {job.get('status')})")
            if len(cleanup_jobs) > 10:
                print(f"   ... and {len(cleanup_jobs) - 10} more")
        
        print("\n⚠️  IMPORTANT: Deleting jobs will also delete their associated pods.")
        print("   This will prevent pods from being recreated automatically.")
        
        # Confirm deletion
        if not self._confirm_multiple("delete", "job", len(all_jobs_to_delete)):
            print("❌ Deletion cancelled by user")
            return 0
        
        # Delete jobs
        log_progress(f"Starting deletion of {len(all_jobs_to_delete)} job(s)...")
        deleted = 0
        failed = 0
        
        for idx, job in enumerate(all_jobs_to_delete, 1):
            job_name = job.get("name")
            log_progress(f"Deleting job {idx}/{len(all_jobs_to_delete)}: {job_name}...")
            try:
                if self.k8s_manager.delete_job(job_name):
                    print(f"✅ Deleted job: {job_name}")
                    deleted += 1
                else:
                    print(f"❌ Failed to delete job: {job_name}")
                    failed += 1
            except Exception as e:
                print(f"❌ Error deleting job {job_name}: {e}")
                failed += 1
        
        elapsed = time.time() - start_time
        print(f"\n📊 Summary: {deleted} jobs deleted, {failed} failed (total time: {elapsed:.2f}s)")
        print("ℹ️  Note: Associated pods will be deleted automatically by Kubernetes.")
        return deleted
    
    def delete_job(self, job_name: str) -> bool:
        """
        Delete a Kubernetes job (with confirmation).
        
        Args:
            job_name: Name of the job to delete
            
        Returns:
            True if deletion successful
        """
        if not self.connected:
            print("❌ Not connected to cluster. Use 'connect' first.")
            return False
        
        start_time = time.time()
        
        # Confirm deletion
        if not self._confirm_action("delete", "job", job_name):
            print("❌ Deletion cancelled by user")
            return False
        
        try:
            log_progress(f"Deleting job '{job_name}'...")
            success = self.k8s_manager.delete_job(job_name)
            
            elapsed = time.time() - start_time
            
            if success:
                print(f"✅ Job '{job_name}' deleted successfully (took {elapsed:.2f}s)")
            else:
                print(f"❌ Failed to delete job '{job_name}' (took {elapsed:.2f}s)")
            return success
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Error deleting job (took {elapsed:.2f}s): {e}")
            return False
    
    def get_pod_logs(self, pod_name: str, tail_lines: int = 100) -> Optional[str]:
        """
        Get logs from a pod.
        
        Args:
            pod_name: Name of the pod
            tail_lines: Number of lines to retrieve
            
        Returns:
            Logs as string or None if failed
        """
        if not self.connected:
            print("❌ Not connected to cluster. Use 'connect' first.")
            return None
        
        start_time = time.time()
        
        try:
            log_progress(f"Retrieving logs from pod '{pod_name}' (last {tail_lines} lines)...")
            logs = self.k8s_manager.get_pod_logs(pod_name, tail_lines=tail_lines)
            
            elapsed = time.time() - start_time
            log_success(f"Retrieved logs in {elapsed:.2f}s")
            return logs
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Failed to get logs (took {elapsed:.2f}s): {e}")
            return None
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get cluster information.
        
        Returns:
            Dictionary with cluster information
        """
        if not self.connected:
            print("❌ Not connected to cluster. Use 'connect' first.")
            return {}
        
        start_time = time.time()
        
        try:
            log_progress("Retrieving cluster information...")
            info = self.k8s_manager.get_cluster_info()
            
            elapsed = time.time() - start_time
            log_success(f"Retrieved cluster info in {elapsed:.2f}s")
            return info
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Failed to get cluster info (took {elapsed:.2f}s): {e}")
            return {}
    
    def show_cluster_info(self):
        """Display cluster information in a formatted way."""
        info = self.get_cluster_info()
        
        if not info:
            return
        
        print(f"\n📊 Cluster Information:")
        print("-" * 60)
        print(f"Version: {info.get('version', 'unknown')}")
        print(f"Node Count: {info.get('node_count', 0)}")
        
        nodes = info.get('nodes', [])
        if nodes:
            print(f"\nNodes:")
            for node in nodes:
                name = node.get('name', 'unknown')
                status = node.get('status', 'unknown')
                roles = ', '.join(node.get('roles', [])) or 'worker'
                print(f"  - {name}: {status} ({roles})")
    
    def show_menu(self):
        """Display interactive menu."""
        print("\n" + "=" * 80)
        print(f"  Kubernetes Agent - {self.env_display_names.get(self.environment, self.environment)}")
        print("=" * 80)
        print("\n📊 Monitoring Commands:")
        print("  1.  List all pods")
        print("  2.  List gRPC job pods")
        print("  3.  List all jobs")
        print("  4.  List deployments")
        print("  5.  Show cluster info")
        print("  6.  Get pod logs")
        print("  7.  Get pod details")
        print("\n🗑️  Deletion Commands (with confirmation):")
        print("  8.  Delete pod (by name)")
        print("  9.  Delete gRPC job pods (all)")
        print("  10. Delete gRPC job pods (by pattern)")
        print("  11. Delete job (by name)")
        print("  12. Delete multiple pods (by pattern)")
        print("  13. Delete pods (by status)")
        print("  18. Delete all gRPC jobs (stops pods from recreating)")
        print("  19. Quick cleanup (run kubectl command directly)")
        print("\n⚙️  Management Commands:")
        print("  14. Restart pod (delete and recreate)")
        print("  15. Scale deployment")
        print("  16. Switch environment")
        print("  17. Reconnect")
        print("\n  0.  Exit")
        print("-" * 80)
    
    def run_interactive(self):
        """Run interactive CLI loop."""
        print("\n🚀 Kubernetes Agent Starting...")
        print(f"Environment: {self.env_display_names.get(self.environment, self.environment)}")
        
        if not self.connect():
            print("❌ Failed to connect. Exiting.")
            return
        
        while True:
            self.show_menu()
            
            try:
                choice = input("\nEnter command number: ").strip()
                
                if choice == "0":
                    print("\n👋 Goodbye!")
                    break
                
                elif choice == "1":
                    self.list_pods()
                
                elif choice == "2":
                    self.list_grpc_jobs()
                
                elif choice == "3":
                    self.list_jobs()
                
                elif choice == "4":
                    self.list_deployments()
                
                elif choice == "5":
                    self.show_cluster_info()
                
                elif choice == "6":
                    pod_name = input("Enter pod name: ").strip()
                    if pod_name:
                        tail = input("Number of lines (default 100): ").strip()
                        tail_lines = int(tail) if tail.isdigit() else 100
                        logs = self.get_pod_logs(pod_name, tail_lines)
                        if logs:
                            print(f"\n📄 Logs from pod '{pod_name}':")
                            print("-" * 80)
                            print(logs)
                
                elif choice == "7":
                    pod_name = input("Enter pod name: ").strip()
                    if pod_name:
                        start_time = time.time()
                        log_progress(f"Retrieving details for pod '{pod_name}'...")
                        pod_info = self.k8s_manager.get_pod_by_name(pod_name)
                        elapsed = time.time() - start_time
                        
                        if pod_info:
                            log_success(f"Retrieved pod details in {elapsed:.2f}s")
                            print(f"\n📦 Pod Details:")
                            print("-" * 60)
                            for key, value in pod_info.items():
                                if key != "labels":
                                    print(f"  {key}: {value}")
                            if pod_info.get("labels"):
                                print(f"  labels: {json.dumps(pod_info['labels'], indent=2)}")
                        else:
                            print(f"❌ Pod '{pod_name}' not found (took {elapsed:.2f}s)")
                
                elif choice == "8":
                    pod_name = input("Enter pod name to delete: ").strip()
                    if pod_name:
                        self.delete_pod(pod_name)
                
                elif choice == "9":
                    self.delete_grpc_jobs()
                
                elif choice == "10":
                    pattern = input("Enter pattern to filter pod names: ").strip()
                    if pattern:
                        self.delete_grpc_jobs(pattern=pattern)
                    else:
                        print("❌ Pattern cannot be empty")
                
                elif choice == "11":
                    job_name = input("Enter job name to delete: ").strip()
                    if job_name:
                        self.delete_job(job_name)
                
                elif choice == "12":
                    pattern = input("Enter pattern to filter pod names: ").strip()
                    if pattern:
                        pods = self.list_pods()
                        matching_pods = [p for p in pods if pattern in p.get("name", "")]
                        if not matching_pods:
                            print(f"❌ No pods found matching pattern '{pattern}'")
                        else:
                            print(f"\n📦 Found {len(matching_pods)} pod(s) matching pattern:")
                            for pod in matching_pods:
                                print(f"   - {pod.get('name')} (Status: {pod.get('status')})")
                            
                            if self._confirm_multiple("delete", "pod", len(matching_pods)):
                                deleted = 0
                                for pod in matching_pods:
                                    if self.k8s_manager.delete_pod(pod.get("name")):
                                        deleted += 1
                                print(f"✅ Deleted {deleted} pod(s)")
                            else:
                                print("❌ Deletion cancelled")
                    else:
                        print("❌ Pattern cannot be empty")
                
                elif choice == "13":
                    print("\nAvailable pod statuses:")
                    print("  - Running")
                    print("  - Pending")
                    print("  - Failed")
                    print("  - Succeeded")
                    print("  - Unknown")
                    status = input("Enter status to filter pods: ").strip()
                    if status:
                        self.delete_pods_by_status(status)
                    else:
                        print("❌ Status cannot be empty")
                
                elif choice == "14":
                    pod_name = input("Enter pod name to restart: ").strip()
                    if pod_name:
                        if self._confirm_action("restart", "pod", pod_name):
                            start_time = time.time()
                            log_progress(f"Restarting pod '{pod_name}'...")
                            if self.k8s_manager.restart_pod(pod_name):
                                elapsed = time.time() - start_time
                                print(f"✅ Pod '{pod_name}' restarted successfully (took {elapsed:.2f}s)")
                            else:
                                elapsed = time.time() - start_time
                                print(f"❌ Failed to restart pod '{pod_name}' (took {elapsed:.2f}s)")
                        else:
                            print("❌ Restart cancelled")
                
                elif choice == "15":
                    deployment_name = input("Enter deployment name: ").strip()
                    if deployment_name:
                        replicas_str = input("Enter number of replicas: ").strip()
                        if replicas_str.isdigit():
                            replicas = int(replicas_str)
                            if self._confirm_action("scale", f"deployment '{deployment_name}' to {replicas} replicas", ""):
                                start_time = time.time()
                                log_progress(f"Scaling deployment '{deployment_name}' to {replicas} replicas...")
                                if self.k8s_manager.scale_deployment(deployment_name, replicas):
                                    elapsed = time.time() - start_time
                                    print(f"✅ Deployment '{deployment_name}' scaled to {replicas} replicas (took {elapsed:.2f}s)")
                                else:
                                    elapsed = time.time() - start_time
                                    print(f"❌ Failed to scale deployment '{deployment_name}' (took {elapsed:.2f}s)")
                            else:
                                print("❌ Scaling cancelled")
                        else:
                            print("❌ Invalid number of replicas")
                
                elif choice == "16":
                    print("\nAvailable environments:")
                    print("  1. staging")
                    print("  2. production")
                    env_choice = input("Select environment (1 or 2): ").strip()
                    if env_choice == "1":
                        self.environment = "staging"
                    elif env_choice == "2":
                        self.environment = "production"
                    else:
                        print("❌ Invalid choice")
                        continue
                    
                    # Reinitialize with new environment
                    log_progress(f"Switching to environment: {self.environment}")
                    self.config_manager = ConfigManager(env=self.environment)
                    self.k8s_manager = None
                    self.connected = False
                    if not self.connect():
                        print("❌ Failed to connect to new environment")
                
                elif choice == "17":
                    self.connected = False
                    self.k8s_manager = None
                    if not self.connect():
                        print("❌ Failed to reconnect")
                
                elif choice == "18":
                    print("\nOptions:")
                    print("  1. Delete gRPC jobs only")
                    print("  2. Delete gRPC + cleanup jobs")
                    option = input("Select option (1 or 2, default 2): ").strip()
                    include_cleanup = option != "1"
                    self.delete_all_grpc_jobs(include_cleanup=include_cleanup)
                
                elif choice == "19":
                    print("\n" + "=" * 80)
                    print("  Quick Cleanup - Run kubectl command directly")
                    print("=" * 80)
                    print("\nThis will execute the recommended cleanup command:")
                    print("  kubectl get jobs -n panda -o name | grep -E '(grpc-job|cleanup-job)' | xargs -I {} kubectl delete {} -n panda")
                    print("\nOptions:")
                    print("  1. Execute command via SSH (requires SSH connection)")
                    print("  2. Show command to copy/paste manually")
                    print("  3. Cancel")
                    option = input("\nSelect option (1, 2, or 3): ").strip()
                    
                    if option == "1":
                        self.quick_cleanup_via_kubectl()
                    elif option == "2":
                        namespace = self.k8s_manager.k8s_config.get("namespace", "panda") if self.k8s_manager else "panda"
                        command = f"kubectl get jobs -n {namespace} -o name | grep -E '(grpc-job|cleanup-job)' | xargs -I {{}} kubectl delete {{}} -n {namespace}"
                        print(f"\n📋 Command to copy:")
                        print("-" * 80)
                        print(command)
                        print("-" * 80)
                        print("\n💡 Copy this command and run it on the server:")
                        print("   ssh root@10.10.10.10")
                        print("   ssh prisma@10.10.10.150")
                        print(f"   {command}")
                    else:
                        print("❌ Cancelled")
                
                else:
                    print("❌ Invalid command. Please try again.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                input("\nPress Enter to continue...")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Interactive Kubernetes Agent for managing K8s environments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/k8s_agent.py
  python scripts/k8s_agent.py --env staging
  python scripts/k8s_agent.py --env production
        """
    )
    
    parser.add_argument(
        "--env",
        "--environment",
        dest="environment",
        choices=["staging", "production"],
        default="staging",
        help="Kubernetes environment to connect to (default: staging)"
    )
    
    args = parser.parse_args()
    
    # Create and run agent
    agent = K8sAgent(environment=args.environment)
    agent.run_interactive()


if __name__ == "__main__":
    main()

