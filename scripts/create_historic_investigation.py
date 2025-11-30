"""Create a historic investigation to test gRPC data flow."""
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
        
        # First, check available recordings with time info
        print("=== Checking for recordings with time info ===")
        result = ssh.execute_command('''
            kubectl exec -n panda panda-panda-segy-recorder-788f56f69-l89v7 -- \
            find /prisma/root/recordings -name "*.segy" -o -name "*.prp" 2>/dev/null | head -5
        ''')
        print(f"Sample recording files: {result.get('stdout', '') or 'None found'}")
        
        # Check recordings time range via Focus Server API
        print("\n=== Query recordings in time range ===")
        # Try last 24 hours
        query_payload = {
            "start_time": 1732809600,  # Nov 28, 2024 12:00 UTC
            "end_time": 1732896000     # Nov 29, 2024 12:00 UTC
        }
        query_json = json.dumps(query_payload)
        
        result = ssh.execute_command(f'''
            curl -sk -X POST "{focus_server_url}/recordings_in_time_range" \
            -H "Content-Type: application/json" \
            -d '{query_json}' 2>&1 | head -c 500
        ''')
        print(f"Recordings query result: {result.get('stdout', '')[:500]}")
        
        # Try to create a historic investigation
        print("\n=== Creating historic investigation ===")
        
        # Use a recent time range (last few hours)
        import time
        current_time = int(time.time())
        # Go back 2 hours
        start_time_epoch = current_time - (2 * 60 * 60)
        end_time_epoch = current_time - (1 * 60 * 60)  # 1 hour window
        
        # Convert to the format Focus Server expects (YYMMDDHHMMSS)
        from datetime import datetime
        start_str = datetime.fromtimestamp(start_time_epoch).strftime('%y%m%d%H%M%S')
        end_str = datetime.fromtimestamp(end_time_epoch).strftime('%y%m%d%H%M%S')
        
        print(f"Time range: {start_str} to {end_str}")
        
        configure_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 500},
            "sensors": {"min": 1, "max": 100},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": start_str,
            "end_time": end_str
        }
        config_json = json.dumps(configure_payload)
        
        result = ssh.execute_command(f'''
            curl -sk -X POST "{focus_server_url}/config/test-historic-$(date +%s)" \
            -H "Content-Type: application/json" \
            -d '{config_json}' 2>&1
        ''')
        print(f"Configure response: {result.get('stdout', '')}")
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

