#!/usr/bin/env python3
"""Check Kubernetes configuration and fix issues."""

import os
from kubernetes import client, config

def check_k8s_config():
    """Check current Kubernetes configuration."""
    print("=" * 80)
    print("Checking Kubernetes Configuration")
    print("=" * 80)
    
    # Check KUBECONFIG environment variable
    kubeconfig_env = os.environ.get('KUBECONFIG')
    print(f"KUBECONFIG env variable: {kubeconfig_env or 'Not set'}")
    
    # Check default kubeconfig location
    default_kubeconfig = os.path.expanduser("~/.kube/config")
    print(f"Default kubeconfig path: {default_kubeconfig}")
    print(f"Default kubeconfig exists: {os.path.exists(default_kubeconfig)}")
    
    try:
        # Try to load kubeconfig
        print("\nTrying to load kubeconfig...")
        config.load_kube_config()
        
        # Get the configuration
        configuration = client.Configuration.get_default_copy()
        print(f"[OK] Kubeconfig loaded successfully")
        print(f"Host: {configuration.host}")
        
        # Try to connect
        version_api = client.VersionApi()
        version = version_api.get_code()
        print(f"[OK] Connected to cluster version: {version.git_version}")
        
    except config.ConfigException as e:
        print(f"[ERROR] Failed to load kubeconfig: {e}")
        print("\nTrying to load in-cluster config...")
        
        try:
            config.load_incluster_config()
            configuration = client.Configuration.get_default_copy()
            print(f"[OK] In-cluster config loaded")
            print(f"Host: {configuration.host}")
        except:
            print("[ERROR] Failed to load in-cluster config")
            print("\n[WARNING] No valid Kubernetes configuration found")
            print("This is expected if running outside of Kubernetes cluster")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        
        # Check if it's SSL error
        if "SSL" in str(e) or "certificate" in str(e).lower():
            print("\n[WARNING] SSL/Certificate error detected")
            print("This might be due to self-signed certificates")
            
            # Try with SSL verification disabled
            try:
                print("\nTrying with SSL verification disabled...")
                configuration = client.Configuration()
                configuration.host = "https://10.10.100.102:6443"  # Correct host
                configuration.verify_ssl = False
                configuration.debug = False
                client.Configuration.set_default(configuration)
                
                version_api = client.VersionApi()
                version = version_api.get_code()
                print(f"[OK] Connected (SSL disabled) to cluster version: {version.git_version}")
            except Exception as e2:
                print(f"[ERROR] Still failed: {e2}")

if __name__ == "__main__":
    check_k8s_config()
