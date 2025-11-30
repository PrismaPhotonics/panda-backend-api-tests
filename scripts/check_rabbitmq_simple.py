"""Simple RabbitMQ check."""
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
        # Step 1: Test connectivity
        print("=== Step 1: Test RabbitMQ Connectivity ===")
        result = ssh.execute_command('curl -s -u prisma:prismapanda "http://10.10.10.107:15672/api/overview" | head -c 200')
        print(result.get('stdout', '')[:200])
        
        # Step 2: Get queue list as raw JSON
        print("\n=== Step 2: Get Queue Names ===")
        result = ssh.execute_command('curl -s -u prisma:prismapanda "http://10.10.10.107:15672/api/queues" | grep -o \'"name":"[^"]*"\' | head -30')
        print(result.get('stdout', ''))
        
        # Step 3: Count queues with grpc in name
        print("\n=== Step 3: gRPC Queue Count ===")
        result = ssh.execute_command('curl -s -u prisma:prismapanda "http://10.10.10.107:15672/api/queues" | grep -o \'"name":"grpc-job[^"]*"\' | wc -l')
        print(f"gRPC queues: {result.get('stdout', '').strip()}")
        
        # Step 4: Check for messages in queues
        print("\n=== Step 4: Queues with Messages ===")
        result = ssh.execute_command('curl -s -u prisma:prismapanda "http://10.10.10.107:15672/api/queues" | grep -oP \'"name":"[^"]*","vhost"[^}]*"messages":[0-9]+\' | grep -v \'"messages":0\' | head -10')
        print(result.get('stdout', '') or 'No queues with messages found')
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

