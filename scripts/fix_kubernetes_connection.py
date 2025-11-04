#!/usr/bin/env python3
"""Fix Kubernetes connection issues."""

import os
import sys
import json
import subprocess
import socket
import time
from pathlib import Path

def test_network_connectivity():
    """Test basic network connectivity to Kubernetes API."""
    print("=" * 80)
    print("Testing Network Connectivity to Kubernetes API")
    print("=" * 80)
    
    host = "10.10.100.102"
    port = 6443
    
    print(f"\n1. Testing TCP connection to {host}:{port}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"[OK] Port {port} is open on {host}")
            return True
        else:
            print(f"[ERROR] Cannot connect to {host}:{port} - Error code: {result}")
            return False
    except socket.error as e:
        print(f"[ERROR] Socket error: {e}")
        return False
    finally:
        sock.close()

def create_ssh_tunnel():
    """Create SSH tunnel to Kubernetes API."""
    print("\n" + "=" * 80)
    print("Creating SSH Tunnel to Kubernetes API")
    print("=" * 80)
    
    print("\nTo access Kubernetes API from your local machine, you need an SSH tunnel.")
    print("\nOption 1: Manual SSH Tunnel (recommended)")
    print("-" * 40)
    print("Run this command in a separate PowerShell window:")
    print("\nssh -L 6443:10.10.100.102:6443 root@10.10.100.3")
    print("\nPassword: PASSW0RD")
    print("\nKeep this window open while running tests!")
    
    print("\n" + "-" * 40)
    print("\nOption 2: Direct Access via SSH")
    print("-" * 40)
    print("Connect to the cluster directly:")
    print("\nssh root@10.10.100.3")
    print("ssh prisma@10.10.100.113")
    print("k9s  # or kubectl commands")
    
    return False

def update_kubeconfig_for_tunnel():
    """Update kubeconfig to use localhost when tunnel is active."""
    print("\n" + "=" * 80)
    print("Updating kubeconfig for SSH Tunnel")
    print("=" * 80)
    
    kubeconfig_path = Path.home() / ".kube" / "config"
    
    if not kubeconfig_path.exists():
        print(f"[ERROR] Kubeconfig not found at {kubeconfig_path}")
        return False
    
    # Read current config
    with open(kubeconfig_path, 'r') as f:
        content = f.read()
    
    if "https://localhost:6443" in content:
        print("[INFO] Kubeconfig already configured for localhost tunnel")
        return True
    
    # Create backup
    backup_path = kubeconfig_path.with_suffix('.config.backup')
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"[OK] Backup created: {backup_path}")
    
    # Update to localhost
    new_content = content.replace(
        "server: https://10.10.100.102:6443",
        "server: https://localhost:6443"
    )
    
    with open(kubeconfig_path, 'w') as f:
        f.write(new_content)
    
    print("[OK] Updated kubeconfig to use localhost:6443")
    print("[INFO] Remember to start the SSH tunnel first!")
    
    return True

def test_kubectl():
    """Test kubectl connectivity."""
    print("\n" + "=" * 80)
    print("Testing kubectl")
    print("=" * 80)
    
    try:
        # Test kubectl version
        result = subprocess.run(
            ["kubectl", "version", "--client", "--short"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"[OK] kubectl client: {result.stdout.strip()}")
        else:
            print(f"[ERROR] kubectl client error: {result.stderr}")
            return False
        
        # Test cluster connection
        print("\nTesting cluster connection...")
        result = subprocess.run(
            ["kubectl", "get", "nodes", "--request-timeout=5s"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("[OK] Connected to cluster!")
            print(f"Nodes:\n{result.stdout}")
            return True
        else:
            print(f"[ERROR] Cannot connect to cluster: {result.stderr}")
            
            if "connection refused" in result.stderr.lower():
                print("\n[HINT] Connection refused - SSH tunnel might not be running")
                print("Start the tunnel: ssh -L 6443:10.10.100.102:6443 root@10.10.100.3")
            elif "timeout" in result.stderr.lower():
                print("\n[HINT] Connection timeout - Check network connectivity")
            
            return False
            
    except FileNotFoundError:
        print("[ERROR] kubectl not found. Please install kubectl.")
        return False
    except subprocess.TimeoutExpired:
        print("[ERROR] kubectl command timed out")
        return False

def test_with_python_client():
    """Test connection with Python Kubernetes client."""
    print("\n" + "=" * 80)
    print("Testing with Python Kubernetes Client")
    print("=" * 80)
    
    try:
        from kubernetes import client, config
        
        # Try loading config
        try:
            config.load_kube_config()
            print("[OK] Kubeconfig loaded")
        except Exception as e:
            print(f"[ERROR] Failed to load kubeconfig: {e}")
            return False
        
        # Get configuration
        configuration = client.Configuration.get_default_copy()
        print(f"Host: {configuration.host}")
        
        # Disable SSL verification for self-signed cert
        configuration.verify_ssl = False
        configuration.debug = False
        client.Configuration.set_default(configuration)
        
        # Try to connect
        v1 = client.CoreV1Api()
        
        print("Getting cluster nodes...")
        nodes = v1.list_node(timeout_seconds=5)
        
        print(f"[OK] Connected! Found {len(nodes.items)} nodes:")
        for node in nodes.items:
            print(f"  - {node.metadata.name}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        
        if "connection refused" in str(e).lower():
            print("\n[HINT] Start SSH tunnel first!")
        elif "timeout" in str(e).lower():
            print("\n[HINT] Network timeout - check connectivity")
        
        return False

def main():
    """Main function to diagnose and fix Kubernetes connection."""
    print("\n" + "=" * 80)
    print("KUBERNETES CONNECTION DIAGNOSTIC & FIX")
    print("=" * 80)
    
    # Step 1: Test direct connectivity
    print("\nStep 1: Testing direct network connectivity")
    direct_connection = test_network_connectivity()
    
    if not direct_connection:
        print("\n[WARNING] Cannot connect directly to Kubernetes API")
        print("This is expected if you're outside the cluster network")
        
        # Step 2: Suggest SSH tunnel
        print("\nStep 2: Setting up SSH Tunnel")
        create_ssh_tunnel()
        
        # Step 3: Update kubeconfig for tunnel
        print("\nStep 3: Configure kubeconfig for tunnel")
        
        response = input("\nDo you want to update kubeconfig for localhost tunnel? (y/n): ")
        if response.lower() == 'y':
            if update_kubeconfig_for_tunnel():
                print("\n[ACTION REQUIRED] Start the SSH tunnel in another window:")
                print("ssh -L 6443:10.10.100.102:6443 root@10.10.100.3")
                input("\nPress Enter after starting the tunnel...")
                
                # Test connection through tunnel
                print("\nTesting connection through tunnel...")
                test_kubectl()
                test_with_python_client()
    else:
        print("\n[OK] Direct connection available!")
        
        # Test kubectl
        test_kubectl()
        test_with_python_client()
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    
    print("\nSummary:")
    print("1. Direct connection: " + ("[OK]" if direct_connection else "[FAILED - Use SSH tunnel]"))
    print("2. For tests to work, either:")
    print("   a) Run from within the cluster network, OR")
    print("   b) Use SSH tunnel: ssh -L 6443:10.10.100.102:6443 root@10.10.100.3")
    print("3. Alternative: Connect via SSH and run k9s directly")

if __name__ == "__main__":
    main()
