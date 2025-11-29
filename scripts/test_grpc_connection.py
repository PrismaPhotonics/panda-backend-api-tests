"""Test gRPC connection with the new pandadatastream proto."""
import sys
sys.path.insert(0, 'C:\\Projects\\focus_server_automation')

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager
from src.apis.grpc_client import GrpcStreamClient

def main():
    cm = ConfigManager()
    ssh = SSHManager(cm)
    
    if not ssh.connect():
        print("Failed to connect via SSH")
        return
    
    try:
        # Get a running pod and its service info
        print("=== Finding running gRPC job ===")
        result = ssh.execute_command('kubectl get pods -n panda | grep grpc-job | grep Running | head -1')
        lines = result.get('stdout', '').strip().split()
        if not lines:
            print('No running pods found')
            return
        
        pod_name = lines[0]
        print(f'Pod: {pod_name}')
        
        # Extract job ID from pod name (e.g., grpc-job-21-1097-wbkwn -> 21-1097)
        parts = pod_name.split('-')
        if len(parts) >= 4:
            job_id = f"{parts[2]}-{parts[3]}"
            print(f'Job ID: {job_id}')
        
        # Get the service for this job
        service_name = f"grpc-service-{job_id}"
        result = ssh.execute_command(f'kubectl get svc -n panda {service_name} -o jsonpath="{{.spec.ports[0].nodePort}}"')
        node_port = result.get('stdout', '').strip()
        
        if not node_port:
            print(f"Could not find NodePort for service {service_name}")
            # Try listing all grpc services
            result = ssh.execute_command('kubectl get svc -n panda | grep grpc-service | head -5')
            print(f"Available services:\n{result.get('stdout', '')}")
            return
        
        print(f'NodePort: {node_port}')
        
        # Get node IP
        result = ssh.execute_command('kubectl get nodes -o jsonpath="{.items[0].status.addresses[?(@.type==\\"InternalIP\\")].address}"')
        node_ip = result.get('stdout', '').strip()
        print(f'Node IP: {node_ip}')
        
        # Now try to connect from SSH host
        print(f"\n=== Testing gRPC connection to {node_ip}:{node_port} ===")
        
        # We need to test from inside the cluster or via port-forward
        # Let's set up a port-forward and then connect locally
        print("\nNote: gRPC service is on internal network.")
        print("To test from this machine, you would need:")
        print(f"  kubectl port-forward -n panda svc/{service_name} {node_port}:5000")
        print(f"  Then connect to localhost:{node_port}")
        
        # Let's try to ping the service from inside the cluster
        print(f"\n=== Testing connectivity from inside cluster ===")
        result = ssh.execute_command(f'kubectl exec -n panda {pod_name} -- curl -s -o /dev/null -w "%{{http_code}}" http://localhost:5000 2>&1 || echo "Connection test"')
        print(f'Internal test result: {result.get("stdout", "")}')
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

