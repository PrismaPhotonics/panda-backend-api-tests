#!/usr/bin/env python3
"""Test the fixed Kubernetes manager."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_manager import ConfigManager
from src.infrastructure.kubernetes_manager_fixed import KubernetesManagerFixed

def test_kubernetes_connection():
    """Test Kubernetes connection with the fixed manager."""
    print("=" * 80)
    print("Testing Kubernetes Connection with Fixed Manager")
    print("=" * 80)
    
    # Initialize config manager
    config_manager = ConfigManager("new_production")
    
    # Create fixed Kubernetes manager
    print("\nInitializing Kubernetes manager...")
    k8s_manager = KubernetesManagerFixed(config_manager)
    
    # Get connection status
    print("\nConnection Status:")
    status = k8s_manager.get_connection_status()
    
    print(f"  Connected: {status['connected']}")
    print(f"  API Available: {status['api_available']}")
    print(f"  Test Connection: {status['test_connection']}")
    
    if status['error']:
        print(f"  Error: {status['error']}")
    
    if status['hints']:
        print("\n  Hints to fix connection:")
        for hint in status['hints']:
            print(f"    - {hint}")
    
    # Try to get cluster info
    print("\nCluster Information:")
    cluster_info = k8s_manager.get_cluster_info()
    
    if cluster_info.get('connected'):
        print(f"  [OK] Connected to cluster")
        print(f"  Version: {cluster_info.get('version', 'Unknown')}")
        print(f"  Nodes: {cluster_info.get('node_count', 0)}")
        
        for node in cluster_info.get('nodes', []):
            print(f"    - {node['name']}: {node['status']}")
    else:
        print(f"  [ERROR] Not connected")
        print(f"  Error: {cluster_info.get('error')}")
        
        if cluster_info.get('hint'):
            print(f"  Hint: {cluster_info['hint']}")
    
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    
    if k8s_manager.connected:
        print("[SUCCESS] Kubernetes connection is working!")
    else:
        print("[INFO] Kubernetes connection not available")
        print("\nTo fix this, choose one option:")
        print("\n1. Create SSH Tunnel (for local testing):")
        print("   ssh -L 6443:10.10.100.102:6443 root@10.10.100.3")
        print("   Password: PASSW0RD")
        print("\n2. Direct SSH Access (for manual operations):")
        print("   ssh root@10.10.100.3")
        print("   ssh prisma@10.10.100.113")
        print("   k9s")
        print("\n3. Run tests from within the cluster network")

if __name__ == "__main__":
    test_kubernetes_connection()
