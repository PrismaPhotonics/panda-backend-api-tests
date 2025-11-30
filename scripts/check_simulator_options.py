"""
Check simulator options and how to start data flow.

This script searches for:
1. Simulator configurations
2. Player/forwarder settings  
3. Ways to push mock data to RabbitMQ
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

def main():
    config_manager = ConfigManager()
    ssh = SSHManager(config_manager)
    
    try:
        ssh.connect()
        
        def get_output(result):
            """Extract stdout from result dict."""
            if isinstance(result, dict):
                return result.get('stdout', '') or result.get('output', '')
            return str(result) if result else ''
        
        # 1. Check for simulator in deployments
        print("=== Check for simulator deployments ===")
        result = ssh.execute_command(
            "kubectl get deploy -n panda -o name 2>&1 | head -20"
        )
        print(get_output(result) or "No deployments found")
        
        # 2. Check configmaps for simulator settings
        print("\n=== Check configmaps for player/simulator ===")
        result = ssh.execute_command(
            "kubectl get configmap -n panda -o name 2>&1"
        )
        print(get_output(result) or "No configmaps found")
        
        # 3. Check for player processes
        print("\n=== Check for player/forwarder processes in pods ===")
        result = ssh.execute_command(
            """kubectl get pods -n panda -o jsonpath='{.items[*].metadata.name}' 2>&1 | tr ' ' '\n' | head -10"""
        )
        output = get_output(result)
        pods = output.strip().split('\n') if output else []
        print(f"Pods found: {pods}")
        
        # 4. Check focus-server pod for available commands
        print("\n=== Check focus-server pod environment ===")
        result = ssh.execute_command(
            """kubectl get pods -n panda | grep focus-server | awk '{print $1}' | head -1"""
        )
        focus_pod = get_output(result).strip()
        
        if focus_pod:
            print(f"Focus Server pod: {focus_pod}")
            
            # Check what's available
            result = ssh.execute_command(
                f"""kubectl exec -n panda {focus_pod} -- ls -la /home/prisma/debug-codebase/venv/bin/ 2>&1 | grep -E "player|forwarder|simulator" | head -10"""
            )
            print("Player/forwarder binaries:")
            print(get_output(result) or "  None found")
            
            # Check Python modules available
            result = ssh.execute_command(
                f"""kubectl exec -n panda {focus_pod} -- /home/prisma/debug-codebase/venv/bin/python -c "import baby_analyzer; print(dir(baby_analyzer))" 2>&1 | head -5"""
            )
            print("\nbaby_analyzer module:")
            print(get_output(result) or "  Not accessible")
        
        # 5. Check for recordings directory
        print("\n=== Check recordings directory structure ===")
        result = ssh.execute_command(
            """ls -la /prisma/root/recordings/ 2>&1 | head -15"""
        )
        print(get_output(result) or "No recordings found")
        
        # 6. Check if there's a way to replay recordings
        print("\n=== Check for replay/player options ===")
        result = ssh.execute_command(
            """find /home/prisma -name "*player*" -o -name "*forwarder*" 2>/dev/null | head -10"""
        )
        print(get_output(result) or "No player/forwarder scripts found")
        
        # 7. Check focus-server API for endpoints
        print("\n=== Check Focus Server API endpoints ===")
        result = ssh.execute_command(
            """curl -s -k https://10.10.10.100/focus-server/ 2>&1 | head -20"""
        )
        print(get_output(result) or "No response")
        
        # 8. Check if there's a debug_player or simulator in the codebase
        print("\n=== Check debug-codebase for player ===")
        result = ssh.execute_command(
            """ls -la /home/prisma/debug-codebase/ 2>&1 | head -15"""
        )
        print(get_output(result) or "Directory not found")
        
        # 9. Check microservices directory
        print("\n=== Check microservices for player/simulator ===")
        result = ssh.execute_command(
            """ls -la /home/prisma/debug-codebase/microservices/ 2>&1 | grep -E "player|forwarder|simulator" | head -10"""
        )
        print(get_output(result) or "No matching directories found")
        
    finally:
        ssh.disconnect()


if __name__ == "__main__":
    main()

