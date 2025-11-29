"""Check RabbitMQ for grpc-job queues and their message counts."""
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
        # Check RabbitMQ queues via API
        print("=== RabbitMQ grpc-job Queues ===\n")
        
        # Get queues with grpc-job in name
        cmd = '''curl -s -u prisma:prismapanda "http://rabbitmq-panda:15672/api/queues/%2F" | python3 -c "
import json, sys
data = json.load(sys.stdin)
grpc_queues = [q for q in data if 'grpc-job' in q.get('name', '')]
print(f'Total grpc-job queues: {len(grpc_queues)}')
print()
# Sort by message count
grpc_queues.sort(key=lambda x: x.get('messages', 0), reverse=True)
for q in grpc_queues[:20]:
    name = q.get('name', 'unknown')
    messages = q.get('messages', 0)
    consumers = q.get('consumers', 0)
    state = q.get('state', 'unknown')
    print(f'{name}')
    print(f'  Messages: {messages}, Consumers: {consumers}, State: {state}')
"'''
        result = ssh.execute_command(cmd, timeout=30)
        print(result.get('stdout', ''))
        if result.get('stderr'):
            print('STDERR:', result.get('stderr'))
        
        # Check for any queues with messages
        print("\n=== Queues with Messages > 0 ===\n")
        cmd = '''curl -s -u prisma:prismapanda "http://rabbitmq-panda:15672/api/queues/%2F" | python3 -c "
import json, sys
data = json.load(sys.stdin)
with_messages = [q for q in data if q.get('messages', 0) > 0]
print(f'Queues with messages: {len(with_messages)}')
for q in with_messages[:10]:
    print(f'  {q.get(\"name\")}: {q.get(\"messages\")} messages')
"'''
        result = ssh.execute_command(cmd, timeout=30)
        print(result.get('stdout', ''))
        
        # Check Focus Server related queues
        print("\n=== Focus-related Queues ===\n")
        cmd = '''curl -s -u prisma:prismapanda "http://rabbitmq-panda:15672/api/queues/%2F" | python3 -c "
import json, sys
data = json.load(sys.stdin)
focus_queues = [q for q in data if 'focus' in q.get('name', '').lower() or 'baby' in q.get('name', '').lower()]
print(f'Focus/Baby queues: {len(focus_queues)}')
for q in focus_queues[:15]:
    print(f'  {q.get(\"name\")}: {q.get(\"messages\", 0)} messages, {q.get(\"consumers\", 0)} consumers')
"'''
        result = ssh.execute_command(cmd, timeout=30)
        print(result.get('stdout', ''))
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

