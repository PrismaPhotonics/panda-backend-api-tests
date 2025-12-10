#!/usr/bin/env python3
"""Check staging K8s cluster status for leftover jobs and errors."""

import sys
sys.path.insert(0, '.')

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

def main():
    print("Connecting to staging K8s cluster...")
    
    # Initialize config for staging environment
    config = ConfigManager(env='staging')
    
    # Connect to staging via jump host
    ssh = SSHManager(config)
    ssh.connect()
    
    print("=" * 80)
    print("1. CHECKING GRPC-SERVICE PODS (Active Jobs)")
    print("=" * 80)
    result = ssh.execute_command('kubectl get pods -n panda 2>&1 | grep grpc-service || echo "No grpc-service pods found"')
    print(result)
    
    print("\n" + "=" * 80)
    print("2. CHECKING FOCUS-SERVER POD STATUS")
    print("=" * 80)
    result = ssh.execute_command('kubectl get pods -n panda 2>&1 | grep focus-server')
    print(result)
    
    print("\n" + "=" * 80)
    print("3. CHECKING ALL PANDA PODS STATUS")
    print("=" * 80)
    result = ssh.execute_command('kubectl get pods -n panda -o wide 2>&1')
    print(result)
    
    print("\n" + "=" * 80)
    print("4. CHECKING FOCUS-SERVER RECENT LOGS (last 30 lines)")
    print("=" * 80)
    result = ssh.execute_command('kubectl logs -n panda -l app.kubernetes.io/name=panda-panda-focus-server --tail=30 2>&1')
    print(result)
    
    print("\n" + "=" * 80)
    print("5. CHECKING FOR ERROR LOGS IN FOCUS-SERVER")
    print("=" * 80)
    result = ssh.execute_command('kubectl logs -n panda -l app.kubernetes.io/name=panda-panda-focus-server --tail=200 2>&1 | grep -i error || echo "No errors found"')
    print(result)
    
    print("\n" + "=" * 80)
    print("6. CHECKING POD EVENTS (for crashes/restarts)")
    print("=" * 80)
    result = ssh.execute_command('kubectl get events -n panda --sort-by=.lastTimestamp 2>&1 | tail -20')
    print(result)
    
    print("\n" + "=" * 80)
    print("7. CHECKING FOCUS-SERVER POD DETAILS")
    print("=" * 80)
    result = ssh.execute_command('kubectl describe pod -n panda -l app.kubernetes.io/name=panda-panda-focus-server 2>&1 | grep -A5 "State:" | head -20')
    print(result)
    
    ssh.disconnect()
    print("\n✅ Check complete!")

if __name__ == "__main__":
    main()

