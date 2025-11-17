#!/usr/bin/env python3
"""
Check Staging K9s/Kubernetes Status Script
==========================================

Comprehensive script to check the status of k9s and Kubernetes cluster in staging environment.

This script:
1. Tests SSH connectivity to staging server
2. Checks availability of kubectl and k9s
3. Checks cluster status (nodes, pods, services, deployments)
4. Displays comprehensive status report

Usage:
    python scripts/check_staging_k9s_status.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.infrastructure.kubernetes_manager import KubernetesManager


class StagingK9sStatusChecker:
    """Comprehensive status checker for staging Kubernetes/k9s environment."""
    
    def __init__(self):
        """Initialize the status checker."""
        self.config_manager = ConfigManager(env="staging")
        self.k8s_config = self.config_manager.get_kubernetes_config()
        self.ssh_config = self.config_manager.get("ssh", {})
        self.namespace = self.k8s_config.get("namespace", "panda")
        self.k8s_manager = None
        self.status_report = {
            "timestamp": datetime.now().isoformat(),
            "environment": "staging",
            "ssh_connection": {},
            "tools_availability": {},
            "cluster_status": {},
            "resources": {}
        }
    
    def check_ssh_connection(self) -> bool:
        """Check SSH connection to staging server."""
        print("\n" + "=" * 80)
        print("1. Checking SSH Connection")
        print("=" * 80)
        
        try:
            self.k8s_manager = KubernetesManager(self.config_manager)
            
            # Check if SSH manager is available
            if hasattr(self.k8s_manager, 'ssh_manager') and self.k8s_manager.ssh_manager:
                ssh_manager = self.k8s_manager.ssh_manager
                
                if ssh_manager.connected:
                    print("[OK] SSH connection is active")
                    self.status_report["ssh_connection"]["status"] = "connected"
                    
                    # Get hostname
                    result = ssh_manager.execute_command("hostname")
                    if result.get("success"):
                        hostname = result.get("stdout", "").strip()
                        print(f"    Hostname: {hostname}")
                        self.status_report["ssh_connection"]["hostname"] = hostname
                    
                    # Get connection details
                    jump_host = self.ssh_config.get("jump_host", {})
                    target_host = self.ssh_config.get("target_host", {})
                    
                    self.status_report["ssh_connection"]["jump_host"] = jump_host.get("host", "N/A")
                    self.status_report["ssh_connection"]["target_host"] = target_host.get("host", "N/A")
                    
                    return True
                else:
                    print("[WARNING] SSH manager exists but not connected")
                    print("    Attempting to connect...")
                    if ssh_manager.connect():
                        print("[OK] SSH connection established")
                        self.status_report["ssh_connection"]["status"] = "connected"
                        return True
                    else:
                        print("[ERROR] Failed to establish SSH connection")
                        self.status_report["ssh_connection"]["status"] = "failed"
                        return False
            else:
                print("[WARNING] SSH manager not initialized")
                print("    Attempting to initialize...")
                if self.k8s_manager._init_ssh_fallback():
                    print("[OK] SSH fallback initialized")
                    self.status_report["ssh_connection"]["status"] = "connected"
                    return True
                else:
                    print("[ERROR] Failed to initialize SSH fallback")
                    self.status_report["ssh_connection"]["status"] = "failed"
                    return False
                    
        except Exception as e:
            print(f"[ERROR] SSH connection check failed: {e}")
            self.status_report["ssh_connection"]["status"] = "error"
            self.status_report["ssh_connection"]["error"] = str(e)
            return False
    
    def check_tools_availability(self) -> bool:
        """Check availability of kubectl and k9s."""
        print("\n" + "=" * 80)
        print("2. Checking Tools Availability")
        print("=" * 80)
        
        if not self.k8s_manager or not hasattr(self.k8s_manager, 'ssh_manager'):
            print("[SKIP] SSH manager not available")
            return False
        
        ssh_manager = self.k8s_manager.ssh_manager
        if not ssh_manager or not ssh_manager.connected:
            print("[SKIP] SSH connection not available")
            return False
        
        tools_ok = True
        
        # Check kubectl
        print("\nChecking kubectl...")
        result = ssh_manager.execute_command("which kubectl")
        if result.get("success") and result.get("stdout", "").strip():
            kubectl_path = result.get("stdout", "").strip()
            print(f"  [OK] kubectl found at: {kubectl_path}")
            self.status_report["tools_availability"]["kubectl"] = {
                "available": True,
                "path": kubectl_path
            }
            
            # Get kubectl version
            version_result = ssh_manager.execute_command("kubectl version --client --short")
            if version_result.get("success"):
                version = version_result.get("stdout", "").strip()
                print(f"    Version: {version}")
                self.status_report["tools_availability"]["kubectl"]["version"] = version
        else:
            print("  [ERROR] kubectl not found")
            self.status_report["tools_availability"]["kubectl"] = {"available": False}
            tools_ok = False
        
        # Check k9s
        print("\nChecking k9s...")
        result = ssh_manager.execute_command("which k9s")
        if result.get("success") and result.get("stdout", "").strip():
            k9s_path = result.get("stdout", "").strip()
            print(f"  [OK] k9s found at: {k9s_path}")
            self.status_report["tools_availability"]["k9s"] = {
                "available": True,
                "path": k9s_path
            }
            
            # Get k9s version
            version_result = ssh_manager.execute_command("k9s version")
            if version_result.get("success"):
                version = version_result.get("stdout", "").strip()
                print(f"    Version: {version}")
                self.status_report["tools_availability"]["k9s"]["version"] = version
        else:
            print("  [WARNING] k9s not found (may need to be installed)")
            self.status_report["tools_availability"]["k9s"] = {"available": False}
        
        return tools_ok
    
    def check_cluster_status(self) -> bool:
        """Check Kubernetes cluster status."""
        print("\n" + "=" * 80)
        print("3. Checking Cluster Status")
        print("=" * 80)
        
        if not self.k8s_manager:
            print("[SKIP] Kubernetes manager not available")
            return False
        
        try:
            # Check cluster connectivity
            print("\nChecking cluster connectivity...")
            result = self.k8s_manager._execute_kubectl_via_ssh("cluster-info")
            if result.get("success"):
                print("  [OK] Cluster is accessible")
                self.status_report["cluster_status"]["accessible"] = True
                
                # Extract cluster info
                cluster_info = result.get("stdout", "")
                if cluster_info:
                    # Extract Kubernetes master URL
                    for line in cluster_info.split("\n"):
                        if "Kubernetes control plane" in line or "master" in line.lower():
                            print(f"    {line.strip()}")
            else:
                print("  [ERROR] Cannot access cluster")
                print(f"    Error: {result.get('stderr', 'Unknown error')}")
                self.status_report["cluster_status"]["accessible"] = False
                return False
            
            # Check nodes
            print("\nChecking nodes...")
            result = self.k8s_manager._execute_kubectl_via_ssh("get nodes -o wide")
            if result.get("success"):
                nodes_output = result.get("stdout", "")
                if nodes_output:
                    print("  [OK] Nodes:")
                    print(nodes_output)
                    # Count nodes
                    node_lines = [line for line in nodes_output.split("\n") if line.strip() and not line.startswith("NAME")]
                    node_count = len(node_lines)
                    self.status_report["cluster_status"]["nodes"] = {
                        "count": node_count,
                        "details": nodes_output
                    }
                    print(f"    Total nodes: {node_count}")
            else:
                print("  [WARNING] Cannot retrieve nodes")
                self.status_report["cluster_status"]["nodes"] = {"error": result.get("stderr", "")}
            
            # Check namespace
            print(f"\nChecking namespace '{self.namespace}'...")
            result = self.k8s_manager._execute_kubectl_via_ssh(f"get namespace {self.namespace}")
            if result.get("success"):
                print(f"  [OK] Namespace '{self.namespace}' exists")
                self.status_report["cluster_status"]["namespace"] = {
                    "exists": True,
                    "name": self.namespace
                }
            else:
                print(f"  [WARNING] Namespace '{self.namespace}' may not exist")
                self.status_report["cluster_status"]["namespace"] = {
                    "exists": False,
                    "name": self.namespace
                }
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Cluster status check failed: {e}")
            self.status_report["cluster_status"]["error"] = str(e)
            return False
    
    def check_resources(self) -> bool:
        """Check Kubernetes resources (pods, services, deployments)."""
        print("\n" + "=" * 80)
        print("4. Checking Resources")
        print("=" * 80)
        
        if not self.k8s_manager:
            print("[SKIP] Kubernetes manager not available")
            return False
        
        try:
            # Check pods
            print("\nChecking pods...")
            result = self.k8s_manager._execute_kubectl_via_ssh("get pods -o wide")
            if result.get("success"):
                pods_output = result.get("stdout", "")
                if pods_output:
                    print("  [OK] Pods:")
                    print(pods_output)
                    
                    # Parse pod status
                    pod_lines = [line for line in pods_output.split("\n") if line.strip() and not line.startswith("NAME")]
                    total_pods = len(pod_lines)
                    running_pods = sum(1 for line in pod_lines if "Running" in line)
                    pending_pods = sum(1 for line in pod_lines if "Pending" in line)
                    failed_pods = sum(1 for line in pod_lines if "Error" in line or "CrashLoopBackOff" in line)
                    
                    self.status_report["resources"]["pods"] = {
                        "total": total_pods,
                        "running": running_pods,
                        "pending": pending_pods,
                        "failed": failed_pods,
                        "details": pods_output
                    }
                    
                    print(f"    Total: {total_pods}, Running: {running_pods}, Pending: {pending_pods}, Failed: {failed_pods}")
                    
                    if failed_pods > 0:
                        print("    [WARNING] Some pods are in failed state!")
                else:
                    print("  [INFO] No pods found")
                    self.status_report["resources"]["pods"] = {"total": 0}
            else:
                print("  [WARNING] Cannot retrieve pods")
                self.status_report["resources"]["pods"] = {"error": result.get("stderr", "")}
            
            # Check services
            print("\nChecking services...")
            result = self.k8s_manager._execute_kubectl_via_ssh("get svc")
            if result.get("success"):
                svc_output = result.get("stdout", "")
                if svc_output:
                    print("  [OK] Services:")
                    print(svc_output)
                    
                    svc_lines = [line for line in svc_output.split("\n") if line.strip() and not line.startswith("NAME")]
                    svc_count = len(svc_lines)
                    self.status_report["resources"]["services"] = {
                        "count": svc_count,
                        "details": svc_output
                    }
                    print(f"    Total services: {svc_count}")
                else:
                    print("  [INFO] No services found")
                    self.status_report["resources"]["services"] = {"count": 0}
            else:
                print("  [WARNING] Cannot retrieve services")
                self.status_report["resources"]["services"] = {"error": result.get("stderr", "")}
            
            # Check deployments
            print("\nChecking deployments...")
            result = self.k8s_manager._execute_kubectl_via_ssh("get deployments")
            if result.get("success"):
                deploy_output = result.get("stdout", "")
                if deploy_output:
                    print("  [OK] Deployments:")
                    print(deploy_output)
                    
                    deploy_lines = [line for line in deploy_output.split("\n") if line.strip() and not line.startswith("NAME")]
                    deploy_count = len(deploy_lines)
                    self.status_report["resources"]["deployments"] = {
                        "count": deploy_count,
                        "details": deploy_output
                    }
                    print(f"    Total deployments: {deploy_count}")
                else:
                    print("  [INFO] No deployments found")
                    self.status_report["resources"]["deployments"] = {"count": 0}
            else:
                print("  [WARNING] Cannot retrieve deployments")
                self.status_report["resources"]["deployments"] = {"error": result.get("stderr", "")}
            
            # Check jobs
            print("\nChecking jobs...")
            result = self.k8s_manager._execute_kubectl_via_ssh("get jobs")
            if result.get("success"):
                jobs_output = result.get("stdout", "")
                if jobs_output:
                    print("  [OK] Jobs:")
                    print(jobs_output)
                    
                    jobs_lines = [line for line in jobs_output.split("\n") if line.strip() and not line.startswith("NAME")]
                    jobs_count = len(jobs_lines)
                    self.status_report["resources"]["jobs"] = {
                        "count": jobs_count,
                        "details": jobs_output
                    }
                    print(f"    Total jobs: {jobs_count}")
                else:
                    print("  [INFO] No jobs found")
                    self.status_report["resources"]["jobs"] = {"count": 0}
            else:
                print("  [WARNING] Cannot retrieve jobs")
                self.status_report["resources"]["jobs"] = {"error": result.get("stderr", "")}
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Resources check failed: {e}")
            self.status_report["resources"]["error"] = str(e)
            return False
    
    def print_summary(self):
        """Print summary report."""
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        # SSH Connection
        ssh_status = self.status_report.get("ssh_connection", {}).get("status", "unknown")
        print(f"\nSSH Connection: {ssh_status.upper()}")
        if ssh_status == "connected":
            target = self.status_report.get("ssh_connection", {}).get("target_host", "N/A")
            hostname = self.status_report.get("ssh_connection", {}).get("hostname", "N/A")
            print(f"  Target: {target}")
            print(f"  Hostname: {hostname}")
        
        # Tools
        print("\nTools Availability:")
        kubectl = self.status_report.get("tools_availability", {}).get("kubectl", {})
        k9s = self.status_report.get("tools_availability", {}).get("k9s", {})
        kubectl_status = "OK" if kubectl.get('available') else "NOT FOUND"
        k9s_status = "OK" if k9s.get('available') else "NOT FOUND"
        print(f"  kubectl: {kubectl_status}")
        print(f"  k9s: {k9s_status}")
        
        # Cluster
        cluster_accessible = self.status_report.get("cluster_status", {}).get("accessible", False)
        cluster_status = "Accessible" if cluster_accessible else "Not Accessible"
        print(f"\nCluster Status: {cluster_status}")
        
        nodes = self.status_report.get("cluster_status", {}).get("nodes", {})
        if "count" in nodes:
            print(f"  Nodes: {nodes['count']}")
        
        # Resources
        print("\nResources:")
        pods = self.status_report.get("resources", {}).get("pods", {})
        if "total" in pods:
            print(f"  Pods: {pods.get('total', 0)} total, {pods.get('running', 0)} running, {pods.get('failed', 0)} failed")
        
        services = self.status_report.get("resources", {}).get("services", {})
        if "count" in services:
            print(f"  Services: {services.get('count', 0)}")
        
        deployments = self.status_report.get("resources", {}).get("deployments", {})
        if "count" in deployments:
            print(f"  Deployments: {deployments.get('count', 0)}")
        
        jobs = self.status_report.get("resources", {}).get("jobs", {})
        if "count" in jobs:
            print(f"  Jobs: {jobs.get('count', 0)}")
        
        print("\n" + "=" * 80)
        print("Status check complete!")
        print("=" * 80)
    
    def run(self) -> int:
        """Run all checks."""
        print("=" * 80)
        print("Staging K9s/Kubernetes Status Check")
        print("=" * 80)
        print(f"Environment: staging")
        print(f"Namespace: {self.namespace}")
        print(f"Timestamp: {self.status_report['timestamp']}")
        
        # Run checks
        ssh_ok = self.check_ssh_connection()
        if not ssh_ok:
            print("\n[ERROR] Cannot proceed without SSH connection")
            return 1
        
        self.check_tools_availability()
        self.check_cluster_status()
        self.check_resources()
        
        # Print summary
        self.print_summary()
        
        return 0


def main():
    """Main entry point."""
    checker = StagingK9sStatusChecker()
    return checker.run()


if __name__ == "__main__":
    sys.exit(main())

