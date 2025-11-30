"""
Check gRPC mock server and client in Focus Server tests.
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
        
        # 1. Check gRPC mock server
        print("=== gRPC mock server ===")
        result = ssh.execute_command(
            """cat /home/prisma/debug-codebase/pz/microservices/focus_server/tests/grpc_mock_server.py 2>&1 | head -100"""
        )
        print(get_output(result))
        
        # 2. Check gRPC mock client
        print("\n=== gRPC mock client ===")
        result = ssh.execute_command(
            """cat /home/prisma/debug-codebase/pz/microservices/focus_server/tests/grpc_mock_client.py 2>&1 | head -100"""
        )
        print(get_output(result))
        
        # 3. Check simulator
        print("\n=== Simulator structure ===")
        result = ssh.execute_command(
            """ls -la /home/prisma/debug-codebase/pz/microservices/pz_integrations/simulator/ 2>&1"""
        )
        print(get_output(result))
        
        # 4. Check how Focus Server starts gRPC job
        print("\n=== Focus Server gRPC job start logic ===")
        result = ssh.execute_command(
            """grep -r "grpc-job" /home/prisma/debug-codebase/pz/microservices/focus_server/*.py 2>/dev/null | head -15"""
        )
        print(get_output(result))
        
        # 5. Check Focus Server configure endpoint
        print("\n=== Focus Server configure endpoint ===")
        result = ssh.execute_command(
            """grep -A 20 "def configure" /home/prisma/debug-codebase/pz/microservices/focus_server/focus_server.py 2>/dev/null | head -30"""
        )
        print(get_output(result))
        
    finally:
        ssh.disconnect()


if __name__ == "__main__":
    main()

