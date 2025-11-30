"""Script to get proto file content from Kubernetes pod."""
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
        # Find a running pod
        result = ssh.execute_command('kubectl get pods -n panda | grep grpc-job | grep Running | head -1')
        lines = result.get('stdout', '').strip().split()
        if not lines:
            print('No running pods found')
            return
            
        pod_name = lines[0]
        print(f'Using pod: {pod_name}')
        
        # Get the main pandadatastream.proto content
        print('\n' + '='*80)
        print('=== pandadatastream.proto ===')
        print('='*80)
        proto_path = '/home/prisma/debug-codebase/pz/microservices/pzpy/recording/backends/protocols/panda_datastream/pandadatastream.proto'
        cmd = f'kubectl exec -n panda {pod_name} -- cat {proto_path}'
        result = ssh.execute_command(cmd, timeout=60)
        print(result.get('stdout', '') or f'Error: {result.get("stderr", "")}')
        
        # Also check streaming_service_test.proto for reference
        print('\n' + '='*80)
        print('=== streaming_service_test.proto (for reference) ===')
        print('='*80)
        proto_path2 = '/home/prisma/debug-codebase/pz/microservices/pzpy/recording/backends/performance_tests/protobuf/streaming_service_test.proto'
        cmd = f'kubectl exec -n panda {pod_name} -- cat {proto_path2}'
        result = ssh.execute_command(cmd, timeout=60)
        print(result.get('stdout', '') or f'Error: {result.get("stderr", "")}')
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

