"""
Find forwarder/player in pz codebase.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

def main():
    config_manager = ConfigManager()
    ssh = SSHManager(config_manager)
    
    def get_output(result):
        if isinstance(result, dict):
            return result.get('stdout', '') or result.get('output', '')
        return str(result) if result else ''
    
    try:
        ssh.connect()
        
        # 1. Find forwarder in microservices
        print("=== Find forwarder in pz/microservices ===")
        result = ssh.execute_command(
            """ls -la /home/prisma/debug-codebase/pz/microservices/ 2>&1 | head -30"""
        )
        print(get_output(result))
        
        # 2. Find forwarder module
        print("\n=== Find forwarder module ===")
        result = ssh.execute_command(
            """find /home/prisma/debug-codebase/pz/microservices -name "*forwarder*" -type d 2>/dev/null | head -10"""
        )
        print(get_output(result) or "No forwarder directories found")
        
        # 3. Check if forwarder can be run
        print("\n=== Check forwarder module ===")
        result = ssh.execute_command(
            """ls -la /home/prisma/debug-codebase/pz/microservices/forwarder/ 2>&1 | head -10"""
        )
        print(get_output(result))
        
        # 4. Check baby_analyzer usage
        print("\n=== Check baby_analyzer usage/help ===")
        result = ssh.execute_command(
            """/home/prisma/debug-codebase/venv/bin/python -m baby_analyzer --help 2>&1 | head -50"""
        )
        print(get_output(result))
        
        # 5. Check for player module
        print("\n=== Find player module ===")
        result = ssh.execute_command(
            """find /home/prisma/debug-codebase/pz/microservices -name "*player*" -type d 2>/dev/null | head -10"""
        )
        print(get_output(result) or "No player directories found")
        
        # 6. Check livefs_forwarder
        print("\n=== Check livefs_forwarder in config ===")
        result = ssh.execute_command(
            """grep -r "livefs_forwarder" /home/prisma/debug-codebase/pz/config/ 2>/dev/null | head -10"""
        )
        print(get_output(result) or "No livefs_forwarder config found")
        
        # 7. Check if there's a way to run forwarder directly
        print("\n=== Check forwarder entry point ===")
        result = ssh.execute_command(
            """/home/prisma/debug-codebase/venv/bin/python -m forwarder --help 2>&1 | head -30"""
        )
        print(get_output(result))
        
        # 8. Check RabbitMQ for any messages at all
        print("\n=== Check RabbitMQ queues with messages ===")
        result = ssh.execute_command(
            """curl -s -u prisma:prismapanda 'http://10.10.10.107:15672/api/queues' 2>&1 | python3 -c "import json,sys; data=json.load(sys.stdin); [print(f'{q[\"name\"]}: {q[\"messages\"]} msgs') for q in data if q.get('messages',0) > 0]" 2>&1"""
        )
        print(get_output(result) or "No queues with messages")
        
        # 9. Check if there's an active investigation producing data
        print("\n=== Check active grpc-jobs ===")
        result = ssh.execute_command(
            """kubectl get jobs -n panda | grep grpc-job | head -10"""
        )
        print(get_output(result) or "No grpc-jobs found")
        
        # 10. Check one recording folder structure
        print("\n=== Check recording folder structure ===")
        result = ssh.execute_command(
            """ls -la /prisma/root/recordings/4f7545a5-c667-460f-9d09-65f6f7653ba4/ 2>&1 | head -20"""
        )
        print(get_output(result))
        
    finally:
        ssh.disconnect()


if __name__ == "__main__":
    main()

