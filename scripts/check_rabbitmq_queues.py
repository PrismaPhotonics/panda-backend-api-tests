"""Check RabbitMQ queues for gRPC jobs."""
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
        rabbitmq_host = "10.10.10.107:15672"
        
        print(f"=== RabbitMQ Queues ({rabbitmq_host}) ===\n")
        
        cmd = f'''curl -s -u prisma:prismapanda "http://{rabbitmq_host}/api/queues" 2>/dev/null | python3 << 'EOF'
import json, sys
data = json.load(sys.stdin)
print(f"Total queues: {{len(data)}}")

# Find grpc-job queues
grpc_queues = [q for q in data if 'grpc-job' in q.get('name', '')]
print(f"grpc-job queues: {{len(grpc_queues)}}")

print("\\n--- gRPC Queues with most messages ---")
grpc_queues.sort(key=lambda x: x.get('messages', 0), reverse=True)
for q in grpc_queues[:15]:
    qname = q.get('name', 'unknown')
    msgs = q.get('messages', 0)
    consumers = q.get('consumers', 0)
    state = q.get('state', 'unknown')
    print(f"  {{qname[:50]}}: {{msgs}} msgs, {{consumers}} consumers")

# Find queues with messages
with_msgs = [q for q in data if q.get('messages', 0) > 0]
print(f"\\n--- All queues with messages > 0: {{len(with_msgs)}} ---")
for q in sorted(with_msgs, key=lambda x: x.get('messages', 0), reverse=True)[:10]:
    print(f"  {{q.get('name', 'unknown')[:60]}}: {{q.get('messages', 0)}} msgs")

# Check for data source queues (live data, recordings, etc)
print("\\n--- Data source queues ---")
for q in data:
    qname = q.get('name', '').lower()
    if any(k in qname for k in ['live', 'unwrap', 'prp', 'recording', 'fiber', 'interrogator']):
        print(f"  {{q.get('name')}}: {{q.get('messages', 0)}} msgs, {{q.get('consumers', 0)}} consumers")
EOF'''
        
        result = ssh.execute_command(cmd, timeout=30)
        print(result.get('stdout', ''))
        if result.get('stderr'):
            print('STDERR:', result.get('stderr'))
            
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

