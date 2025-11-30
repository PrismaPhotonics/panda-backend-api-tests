"""Check logs of a gRPC pod to understand why port 5000 is closed."""
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
        
        print("\n=== Last 50 lines of pod logs ===")
        result = ssh.execute_command(f'kubectl logs -n panda {pod_name} --tail=50')
        print(result.get('stdout', '') or 'No logs')
        
        print("\n=== Grep for errors/warnings ===")
        result = ssh.execute_command(f'kubectl logs -n panda {pod_name} 2>&1 | grep -i "error\\|warning\\|failed\\|exception\\|grpc" | tail -30')
        print(result.get('stdout', '') or 'No error messages found')
        
        print("\n=== Check if gRPC backend is starting ===")
        result = ssh.execute_command(f'kubectl logs -n panda {pod_name} 2>&1 | grep -i "grpc\\|server\\|listen\\|bind\\|port" | head -20')
        print(result.get('stdout', '') or 'No gRPC/server messages found')
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

