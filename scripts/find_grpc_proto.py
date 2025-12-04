"""Script to find gRPC proto files on running Kubernetes pod."""
import sys
sys.path.insert(0, 'C:\\Projects\\focus_server_automation')

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

def main():
    cm = ConfigManager()
    ssh = SSHManager(cm)

    if not ssh.connect():
        print("Failed to connect via SSH")
        return

    try:
        # Find a running pod first
        result = ssh.execute_command('kubectl get pods -n panda | grep grpc-job | grep Running | head -1')
        lines = result.get('stdout', '').strip().split()
        if not lines:
            print('No running pods found')
            return
            
        pod_name = lines[0]
        print(f'Using pod: {pod_name}')
        
        print('\n=== Search for proto files ===')
        cmd = f'kubectl exec -n panda {pod_name} -- find /home/prisma -name "*.proto" 2>/dev/null | head -10'
        result = ssh.execute_command(cmd)
        print('Proto files:', result.get('stdout', '') or 'None found')
        
        print('\n=== Search for _pb2.py files ===')
        cmd = f'kubectl exec -n panda {pod_name} -- find /home/prisma -name "*_pb2.py" 2>/dev/null | head -10'
        result = ssh.execute_command(cmd)
        print('pb2 files:', result.get('stdout', '') or 'None found')
        
        print('\n=== Search for grpc in site-packages ===')
        cmd = f'kubectl exec -n panda {pod_name} -- find /home/prisma -path "*/site-packages/*" -name "*grpc*" 2>/dev/null | head -10'
        result = ssh.execute_command(cmd)
        print('grpc packages:', result.get('stdout', '') or 'None found')
        
        print('\n=== Try grpcurl list ===')
        cmd = f'kubectl exec -n panda {pod_name} -- grpcurl -plaintext localhost:5000 list 2>&1'
        result = ssh.execute_command(cmd)
        print('grpcurl result:', result.get('stdout', ''), result.get('stderr', ''))
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

