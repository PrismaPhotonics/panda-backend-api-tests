"""Check Focus Server API for active investigations."""
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
        focus_server_url = "https://10.10.10.100/focus-server"
        
        print("=== Focus Server Health Check ===")
        result = ssh.execute_command(f'curl -sk "{focus_server_url}/ack" 2>&1')
        print(f"Health: {result.get('stdout', '')[:200]}")
        
        print("\n=== Focus Server Live Metadata ===")
        result = ssh.execute_command(f'curl -sk "{focus_server_url}/live_metadata" 2>&1 | head -c 500')
        print(result.get('stdout', '')[:500])
        
        print("\n=== Focus Server Channels ===")
        result = ssh.execute_command(f'curl -sk "{focus_server_url}/channels" 2>&1 | head -c 200')
        print(result.get('stdout', '')[:200])
        
        print("\n=== Check for data source (interrogator/forwarder) ===")
        result = ssh.execute_command('kubectl get pods -n panda | grep -i "forwarder\\|interrogator\\|unwrap\\|live" | head -10')
        print(result.get('stdout', '') or 'No data source pods found')
        
        print("\n=== Check smart_recorder queue ===")
        result = ssh.execute_command('curl -s -u prisma:prismapanda "http://10.10.10.107:15672/api/queues/%2F/smart_recorder" 2>&1 | grep -oP \'"messages":[0-9]+|"consumers":[0-9]+\'')
        print(result.get('stdout', '') or 'Queue info not available')
        
        print("\n=== Data flow pods in panda namespace ===")
        result = ssh.execute_command('kubectl get pods -n panda 2>&1 | grep -v "grpc-job\\|cleanup-job" | head -20')
        print(result.get('stdout', ''))
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

