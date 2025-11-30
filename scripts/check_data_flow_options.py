"""
Check options to enable data flow to gRPC jobs.
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
        
        # 1. Check focus_server.yaml for livefs_forwarder
        print("=== focus_server.yaml livefs_forwarder config ===")
        result = ssh.execute_command(
            """grep -A 10 "livefs_forwarder" /home/prisma/debug-codebase/pz/config/autocfg/parameters/components/focus_server.yaml 2>&1"""
        )
        print(get_output(result))
        
        # 2. Check Player.py for usage
        print("\n=== Player.py usage ===")
        result = ssh.execute_command(
            """head -100 /home/prisma/debug-codebase/pz/microservices/player/Player.py 2>&1"""
        )
        print(get_output(result))
        
        # 3. Check if we can publish to grpc-job queue directly
        print("\n=== Check grpc-job queue details ===")
        result = ssh.execute_command(
            """curl -s -u prisma:prismapanda 'http://10.10.10.107:15672/api/queues/%2F/grpc-job-4-1352-1764438737.153977' 2>&1 | python3 -c "import json,sys; q=json.load(sys.stdin); print(f'Queue: {q.get(\"name\")}'); print(f'Messages: {q.get(\"messages\", 0)}'); print(f'Consumers: {q.get(\"consumers\", 0)}')" 2>&1"""
        )
        print(get_output(result))
        
        # 4. Check how to send test data to RabbitMQ
        print("\n=== Check baby_analyzer can send test data ===")
        result = ssh.execute_command(
            """cd /home/prisma/debug-codebase/pz/microservices && PRISMA_CONFIG=/home/prisma/debug-codebase/pz/config PRISMA_LOGS=/tmp /home/prisma/debug-codebase/venv/bin/python -c "
from pzpy.msgbus import RabbitMQPublisher
print('RabbitMQPublisher imported successfully')
" 2>&1"""
        )
        print(get_output(result))
        
        # 5. Check what PrpInfoMessage looks like
        print("\n=== Check PrpInfoMessage structure ===")
        result = ssh.execute_command(
            """grep -r "PrpInfoMessage" /home/prisma/debug-codebase/pz/microservices/pzpy/ 2>/dev/null | head -10"""
        )
        print(get_output(result))
        
        # 6. Check if there's a mock/test data sender
        print("\n=== Check for test data senders ===")
        result = ssh.execute_command(
            """find /home/prisma/debug-codebase/pz -name "*mock*" -o -name "*test*sender*" -o -name "*simulator*" 2>/dev/null | grep -v __pycache__ | head -15"""
        )
        print(get_output(result))
        
        # 7. Check if we can replay a recording to RabbitMQ
        print("\n=== Check recording replay options ===")
        result = ssh.execute_command(
            """grep -r "replay" /home/prisma/debug-codebase/pz/microservices/ 2>/dev/null | grep -v __pycache__ | head -10"""
        )
        print(get_output(result))
        
        # 8. Check the forwarder config 
        print("\n=== Check forwarder config ===")
        result = ssh.execute_command(
            """grep -A 5 "interrogator_forwarder" /home/prisma/debug-codebase/pz/config/autocfg/parameters/components/focus_server.yaml 2>&1"""
        )
        print(get_output(result))
        
    finally:
        ssh.disconnect()


if __name__ == "__main__":
    main()

