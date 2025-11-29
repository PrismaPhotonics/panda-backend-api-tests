"""Create investigation with correct endpoint and payload."""
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
        
        # Correct payload structure based on documentation
        print("=== Creating LIVE investigation (correct API) ===\n")
        configure_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {
                "height": 500
            },
            "channels": {
                "min": 1,
                "max": 100
            },
            "frequencyRange": {
                "min": 0,
                "max": 500
            },
            "start_time": None,
            "end_time": None,
            "view_type": 0  # MULTICHANNEL
        }
        config_json = json.dumps(configure_payload)
        print(f"Payload: {config_json}\n")
        
        result = ssh.execute_command(f'''
            curl -sk -X POST "{focus_server_url}/configure" \
            -H "Content-Type: application/json" \
            -d '{config_json}' 2>&1
        ''')
        response = result.get('stdout', '')
        print(f"Response: {response[:1000]}")
        
        # Parse response to get job_id and stream info
        try:
            resp_data = json.loads(response)
            job_id = resp_data.get('job_id', 'unknown')
            stream_url = resp_data.get('stream_url', 'unknown')
            stream_port = resp_data.get('stream_port', 'unknown')
            
            print(f"\n✅ Job Created!")
            print(f"   Job ID: {job_id}")
            print(f"   Stream URL: {stream_url}")
            print(f"   Stream Port: {stream_port}")
            
            # Check if job is running
            print(f"\n=== Checking job pod ===")
            result = ssh.execute_command(f'kubectl get pods -n panda | grep grpc-job | grep Running | tail -5')
            print(result.get('stdout', ''))
            
            # Check port in pod
            print(f"\n=== Checking if gRPC port is listening ===")
            result = ssh.execute_command(f'kubectl get pods -n panda | grep grpc-job | grep Running | head -1')
            pod_line = result.get('stdout', '').strip().split()
            if pod_line:
                newest_pod = pod_line[0]
                result = ssh.execute_command(f'kubectl exec -n panda {newest_pod} -- ss -tlnp 2>/dev/null || kubectl exec -n panda {newest_pod} -- netstat -tlnp 2>/dev/null | head -5')
                print(f"Pod {newest_pod}:")
                print(result.get('stdout', '') or 'No listening ports')
            
        except json.JSONDecodeError:
            print("Could not parse response as JSON")
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

