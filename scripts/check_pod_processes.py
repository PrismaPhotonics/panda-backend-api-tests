"""Check what's running inside a gRPC pod."""
import sys
sys.path.insert(0, 'C:\\Projects\\focus_server_automation')

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

def main():
    cm = ConfigManager()
    ssh = SSHManager(cm)
    
    if not ssh.connect():
        print("Failed to connect via SSH")
        return
    
    try:
        # Get a running pod
        result = ssh.execute_command('kubectl get pods -n panda | grep grpc-job | grep Running | head -1')
        lines = result.get('stdout', '').strip().split()
        if not lines:
            print('No running pods found')
            return
        
        pod_name = lines[0]
        print(f'Pod: {pod_name}')
        
        print("\n=== Processes in pod ===")
        result = ssh.execute_command(f'kubectl exec -n panda {pod_name} -- ps aux')
        print(result.get('stdout', ''))
        
        print("\n=== Listening ports in pod ===")
        result = ssh.execute_command(f'kubectl exec -n panda {pod_name} -- ss -tlnp 2>/dev/null || kubectl exec -n panda {pod_name} -- netstat -tlnp 2>/dev/null || echo "No ss or netstat"')
        print(result.get('stdout', ''))
        
        print("\n=== Check if gRPC port is listening ===")
        result = ssh.execute_command(f'kubectl exec -n panda {pod_name} -- bash -c "echo > /dev/tcp/localhost/5000 && echo Port 5000 is OPEN || echo Port 5000 is CLOSED" 2>&1')
        print(result.get('stdout', ''))
        
        print("\n=== Environment variables (gRPC related) ===")
        result = ssh.execute_command(f'kubectl exec -n panda {pod_name} -- env | grep -i grpc')
        print(result.get('stdout', '') or 'No GRPC env vars')
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

