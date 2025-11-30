"""Check RabbitMQ queues - try different hostnames."""
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
        # Try different RabbitMQ hostnames
        hostnames = [
            "data-rabbitmq.prismaphotonics.net:15672",
            "rabbitmq-panda:15672",
            "10.10.10.107:15672",
            "localhost:15672"
        ]
        
        for host in hostnames:
            print(f"\n=== Trying RabbitMQ at {host} ===")
            cmd = f'curl -s --connect-timeout 5 -u prisma:prismapanda "http://{host}/api/overview" 2>&1 | head -5'
            result = ssh.execute_command(cmd, timeout=15)
            output = result.get('stdout', '')
            if 'cluster_name' in output or 'rabbitmq' in output.lower():
                print(f"✅ Connected to {host}!")
                
                # Get queue list
                print(f"\n=== Queues from {host} ===")
                cmd = f'''curl -s -u prisma:prismapanda "http://{host}/api/queues" 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'Total queues: {{len(data)}}')
    grpc = [q for q in data if 'grpc' in q.get('name', '').lower()]
    print(f'gRPC-related queues: {{len(grpc)}}')
    for q in grpc[:10]:
        print(f'  {{q.get(\"name\")}}: {{q.get(\"messages\", 0)}} msgs, {{q.get(\"consumers\", 0)}} consumers')
except Exception as e:
    print(f'Error: {{e}}')
" 2>&1'''
                result = ssh.execute_command(cmd, timeout=30)
                print(result.get('stdout', ''))
                break
            else:
                print(f"❌ {host}: {output[:100] if output else 'No response'}")
        
        # Also check from inside a pod (they might use internal service name)
        print("\n=== Check RabbitMQ from inside a pod ===")
        result = ssh.execute_command('kubectl get pods -n panda | grep grpc-job | grep Running | head -1')
        lines = result.get('stdout', '').strip().split()
        if lines:
            pod_name = lines[0]
            cmd = f'kubectl exec -n panda {pod_name} -- curl -s --connect-timeout 5 -u prisma:prismapanda "http://rabbitmq-panda:15672/api/overview" 2>&1 | head -3'
            result = ssh.execute_command(cmd, timeout=20)
            print(f"From pod {pod_name}:")
            print(result.get('stdout', '')[:200])
            
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

