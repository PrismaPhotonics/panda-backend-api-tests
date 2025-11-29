"""Find how to start data source for gRPC jobs."""
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
        print("=== Looking for recordings/mock data ===\n")
        
        # Check for recordings in the storage
        print("1. Check recordings storage:")
        result = ssh.execute_command('kubectl exec -n panda panda-panda-segy-recorder-788f56f69-l89v7 -- ls -la /prisma/root/recordings 2>/dev/null | head -15')
        print(result.get('stdout', '') or 'Cannot access recordings')
        
        # Check for simulator/mock configurations
        print("\n2. Check for simulator pods or configs:")
        result = ssh.execute_command('kubectl get pods -A 2>/dev/null | grep -i "simulator\\|mock\\|test\\|player" | head -10')
        print(result.get('stdout', '') or 'No simulator pods found')
        
        # Check deployments
        print("\n3. Check panda deployments:")
        result = ssh.execute_command('kubectl get deployments -n panda 2>&1 | head -20')
        print(result.get('stdout', ''))
        
        # Check services
        print("\n4. Check panda services:")
        result = ssh.execute_command('kubectl get svc -n panda 2>&1 | grep -v "grpc-service" | head -20')
        print(result.get('stdout', ''))
        
        # Check for ConfigMaps that might have data source config
        print("\n5. Check ConfigMaps:")
        result = ssh.execute_command('kubectl get configmap -n panda 2>&1 | head -20')
        print(result.get('stdout', ''))
        
        # Check if there's a way to configure/start data flow
        print("\n6. Check for data flow scripts/jobs:")
        result = ssh.execute_command('kubectl get jobs -n panda 2>&1 | grep -v "grpc-job\\|cleanup-job" | head -10')
        print(result.get('stdout', '') or 'No additional jobs')
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

