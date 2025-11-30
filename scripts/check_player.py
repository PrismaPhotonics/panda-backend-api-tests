"""
Check player module and how to use it.
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
        
        # 1. Check player module structure
        print("=== Player module structure ===")
        result = ssh.execute_command(
            """ls -la /home/prisma/debug-codebase/pz/microservices/player/ 2>&1"""
        )
        print(get_output(result))
        
        # 2. Check player __main__.py
        print("\n=== Player __main__.py ===")
        result = ssh.execute_command(
            """cat /home/prisma/debug-codebase/pz/microservices/player/__main__.py 2>&1 | head -50"""
        )
        print(get_output(result))
        
        # 3. Check if player can be run
        print("\n=== Try player help ===")
        result = ssh.execute_command(
            """cd /home/prisma/debug-codebase/pz/microservices && PRISMA_CONFIG=/home/prisma/debug-codebase/pz/config /home/prisma/debug-codebase/venv/bin/python -m player --help 2>&1 | head -50"""
        )
        print(get_output(result))
        
        # 4. Check recent recording info
        print("\n=== Recent recording info ===")
        result = ssh.execute_command(
            """cat /prisma/root/recordings/4f7545a5-c667-460f-9d09-65f6f7653ba4/*-info.json 2>&1"""
        )
        print(get_output(result))
        
        # 5. Check livefs path
        print("\n=== Check livefs ===")
        result = ssh.execute_command(
            """ls -la /prisma/liveprp/ 2>&1 | head -20"""
        )
        print(get_output(result))
        
        # 6. Check if there's current live data
        print("\n=== Check current live data (if exists) ===")
        result = ssh.execute_command(
            """ls -lat /prisma/root/recordings/ 2>&1 | head -5"""
        )
        print(get_output(result))
        
        # 7. See grpc-job pod logs
        print("\n=== Check latest grpc-job pod logs ===")
        result = ssh.execute_command(
            """kubectl logs -n panda $(kubectl get pods -n panda | grep grpc-job | head -1 | awk '{print $1}') --tail=30 2>&1"""
        )
        print(get_output(result))
        
    finally:
        ssh.disconnect()


if __name__ == "__main__":
    main()

