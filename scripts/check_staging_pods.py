#!/usr/bin/env python3
"""
Check Staging Pods Script
==========================

Script to check pods in staging Kubernetes cluster via SSH.

This script:
1. Connects to staging server via SSH
2. Runs kubectl commands to check pods
3. Displays results

Usage:
    python scripts/check_staging_pods.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.infrastructure.kubernetes_manager import KubernetesManager

def check_pods_via_ssh():
    """Check pods via SSH connection to staging server."""
    print("=" * 80)
    print("Checking Staging Pods via SSH")
    print("=" * 80)
    
    # Load config
    config_manager = ConfigManager()
    k8s_config = config_manager.get_kubernetes_config()
    namespace = k8s_config.get("namespace", "panda")
    
    print(f"\nConnecting to staging Kubernetes...")
    print(f"  Namespace: {namespace}\n")
    
    try:
        # Initialize Kubernetes manager (uses SSH fallback)
        k8s_manager = KubernetesManager(config_manager)
        
        # Run kubectl commands via SSH
        commands = [
            f"get pods",
            f"get pods -l app=grpc-job",
            f"get jobs -l app=grpc-job",
        ]
        
        for cmd in commands:
            print(f"Running: kubectl -n {namespace} {cmd}")
            print("-" * 80)
            try:
                result = k8s_manager._execute_kubectl_via_ssh(cmd)
                if result.get("success"):
                    stdout = result.get("stdout", "")
                    if stdout:
                        print(stdout)
                    else:
                        print("(No output)")
                else:
                    stderr = result.get("stderr", "")
                    if stderr:
                        print(f"Error: {stderr}")
                    else:
                        print("(Command failed)")
            except Exception as e:
                print(f"Error: {e}")
            print()
        
        print("=" * 80)
        print("Check complete")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(check_pods_via_ssh())

