"""
Cleanup pending gRPC job pods before running load tests.

This script deletes all pending gRPC job pods to ensure a clean state
before running gradual load tests.

Usage:
    python scripts/cleanup_pending_jobs.py
"""
import sys
sys.path.insert(0, 'C:\\Projects\\focus_server_automation')

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager


def main():
    """Clean up all pending gRPC job pods."""
    cm = ConfigManager()
    ssh = SSHManager(cm)
    
    if not ssh.connect():
        print("Failed to connect via SSH")
        return
    
    try:
        # Count current pods
        print("\n=== Current Pod Status ===")
        result = ssh.execute_command('kubectl get pods -n panda | grep grpc-job | wc -l')
        total_jobs = int(result.get('stdout', '0').strip() or '0')
        
        result = ssh.execute_command('kubectl get pods -n panda | grep grpc-job | grep Running | wc -l')
        running_jobs = int(result.get('stdout', '0').strip() or '0')
        
        result = ssh.execute_command('kubectl get pods -n panda | grep grpc-job | grep Pending | wc -l')
        pending_jobs = int(result.get('stdout', '0').strip() or '0')
        
        print(f"Total gRPC jobs: {total_jobs}")
        print(f"Running: {running_jobs}")
        print(f"Pending: {pending_jobs}")
        
        if pending_jobs == 0:
            print("\n✅ No pending jobs to clean up!")
            return
        
        # Delete pending pods
        print(f"\n⚠️  Deleting {pending_jobs} pending gRPC job pods...")
        result = ssh.execute_command(
            'kubectl get pods -n panda | grep grpc-job | grep Pending | '
            "awk '{print $1}' | xargs -r kubectl delete pod -n panda --force --grace-period=0"
        )
        print(result.get('stdout', ''))
        
        # Delete associated services
        print("\n🧹 Cleaning up orphaned services...")
        result = ssh.execute_command(
            'kubectl get svc -n panda | grep grpc-service | '
            "awk '{print $1}' | while read svc; do "
            'pod_name=$(echo $svc | sed "s/grpc-service/grpc-job/"); '
            'if ! kubectl get pod -n panda $pod_name-* >/dev/null 2>&1; then '
            'echo "Deleting orphan service: $svc"; '
            'kubectl delete svc -n panda $svc; '
            'fi; done 2>/dev/null'
        )
        print(result.get('stdout', '') or 'Done')
        
        # Delete cleanup jobs
        print("\n🗑️  Cleaning up old cleanup jobs...")
        result = ssh.execute_command(
            'kubectl get pods -n panda | grep cleanup-job | '
            "awk '{print $1}' | xargs -r kubectl delete pod -n panda --force --grace-period=0 2>/dev/null"
        )
        
        # Verify cleanup
        print("\n=== After Cleanup ===")
        result = ssh.execute_command('kubectl get pods -n panda | grep grpc-job | wc -l')
        total_after = int(result.get('stdout', '0').strip() or '0')
        
        result = ssh.execute_command('kubectl get pods -n panda | grep grpc-job | grep Running | wc -l')
        running_after = int(result.get('stdout', '0').strip() or '0')
        
        result = ssh.execute_command('kubectl get pods -n panda | grep grpc-job | grep Pending | wc -l')
        pending_after = int(result.get('stdout', '0').strip() or '0')
        
        print(f"Total gRPC jobs: {total_after}")
        print(f"Running: {running_after}")
        print(f"Pending: {pending_after}")
        
        if pending_after == 0:
            print("\n✅ Cleanup completed successfully!")
        else:
            print(f"\n⚠️  Still {pending_after} pending pods remaining")
        
    finally:
        ssh.disconnect()


if __name__ == '__main__':
    main()

