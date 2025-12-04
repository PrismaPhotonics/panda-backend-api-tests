"""Check what data source is needed to start data flow."""
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
        print("=== Check prisma-config for data source settings ===\n")
        result = ssh.execute_command('kubectl get configmap -n panda prisma-config -o yaml 2>&1 | grep -A 50 "data:" | head -100')
        print(result.get('stdout', ''))
        
        print("\n=== Check livefs-index.txt (live data source info) ===")
        result = ssh.execute_command('''
            kubectl exec -n panda panda-panda-segy-recorder-788f56f69-l89v7 -- \
            cat /prisma/root/recordings/livefs-index.txt 2>/dev/null
        ''')
        print(result.get('stdout', '') or 'File not found')
        
        print("\n=== Check focus-server logs for data source ===")
        result = ssh.execute_command('kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-xbcjk --tail=30 2>&1 | grep -i "data\\|source\\|rabbit\\|amqp\\|forwarder"')
        print(result.get('stdout', '') or 'No relevant logs')
        
        print("\n=== All pods in ALL namespaces (looking for forwarder/simulator) ===")
        result = ssh.execute_command('kubectl get pods -A 2>&1 | grep -i "forward\\|live\\|simul\\|unwrap\\|interrogator" | head -15')
        print(result.get('stdout', '') or 'No forwarder/simulator pods found')
        
        print("\n=== Check if there's a livefs forwarder deployment ===")
        result = ssh.execute_command('kubectl get deploy -A 2>&1 | grep -i "forwarder\\|live"')
        print(result.get('stdout', '') or 'No forwarder deployment found')
        
        print("\n=== Check RabbitMQ exchanges (data might flow through exchanges) ===")
        result = ssh.execute_command('curl -s -u prisma:prismapanda "http://10.10.10.107:15672/api/exchanges" 2>&1 | grep -o \'"name":"[^"]*"\' | head -20')
        print(result.get('stdout', ''))
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

