"""Create investigation with correct time range and endpoint."""
import sys
sys.path.insert(0, 'C:\\Projects\\focus_server_automation')

import json
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
        
        # Check the actual recordings dates
        print("=== Recent recordings ===")
        result = ssh.execute_command('''
            kubectl exec -n panda panda-panda-segy-recorder-788f56f69-l89v7 -- \
            ls -lt /prisma/root/recordings 2>/dev/null | head -10
        ''')
        print(result.get('stdout', ''))
        
        # Get a recent recording's files
        print("\n=== Most recent recording folder ===")
        result = ssh.execute_command('''
            kubectl exec -n panda panda-panda-segy-recorder-788f56f69-l89v7 -- bash -c '
                latest=$(ls -t /prisma/root/recordings | head -1)
                echo "Latest folder: $latest"
                ls -la "/prisma/root/recordings/$latest" | head -5
            '
        ''')
        print(result.get('stdout', ''))
        
        # Try creating a LIVE investigation (no time range = live mode)
        print("\n=== Creating LIVE investigation ===")
        configure_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 500},
            "sensors": {"min": 1, "max": 100},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None
        }
        config_json = json.dumps(configure_payload)
        
        import time
        task_id = f"live-test-{int(time.time())}"
        
        result = ssh.execute_command(f'''
            curl -sk -X POST "{focus_server_url}/config/{task_id}" \
            -H "Content-Type: application/json" \
            -d '{config_json}' 2>&1
        ''')
        print(f"Task ID: {task_id}")
        print(f"Response: {result.get('stdout', '')}")
        
        # Check if job was created
        print("\n=== Check if gRPC job was created ===")
        result = ssh.execute_command(f'kubectl get pods -n panda | grep grpc-job | grep -i running | tail -5')
        print(result.get('stdout', ''))
        
        # Check RabbitMQ for new queue
        print("\n=== Check new queue in RabbitMQ ===")
        result = ssh.execute_command(f'''
            curl -s -u prisma:prismapanda "http://10.10.10.107:15672/api/queues" | \
            grep -o '"name":"[^"]*{task_id}[^"]*"' || echo "Queue not found"
        ''')
        print(result.get('stdout', ''))
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

