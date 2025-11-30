"""
Check where livefs_forwarder setting is and how to enable it.
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
        
        # 1. Check where livefs_forwarder is configured
        print("=== 1. Where is livefs_forwarder configured? ===\n")
        
        # Check in ConfigMaps
        print("📁 Checking Kubernetes ConfigMaps...")
        result = ssh.execute_command(
            """kubectl get configmap -n panda -o yaml 2>&1 | grep -A5 -B5 "livefs_forwarder" | head -30"""
        )
        print(get_output(result) or "Not found in ConfigMaps")
        
        # 2. Check Helm values
        print("\n📁 Checking Helm release values...")
        result = ssh.execute_command(
            """helm get values panda -n panda 2>&1 | grep -A5 -B5 "livefs" | head -20"""
        )
        print(get_output(result) or "Not found in Helm values")
        
        # 3. Check the actual config file on disk
        print("\n📁 Checking config file on disk...")
        result = ssh.execute_command(
            """cat /home/prisma/debug-codebase/pz/config/autocfg/parameters/components/focus_server.yaml 2>&1 | grep -A20 "livefs_forwarder"  | head -30"""
        )
        print(get_output(result))
        
        # 4. Check if there's an API to enable it
        print("\n📁 Checking Focus Server API for config endpoints...")
        result = ssh.execute_command(
            """curl -s -k 'https://10.10.10.100/focus-server/docs' 2>&1 | head -50"""
        )
        api_docs = get_output(result)
        print(api_docs[:500] if api_docs else "No API docs found")
        
        # 5. Check if there's an environment variable
        print("\n📁 Checking Focus Server pod environment...")
        result = ssh.execute_command(
            """kubectl get pods -n panda | grep focus-server | awk '{print $1}' | head -1"""
        )
        focus_pod = get_output(result).strip()
        
        if focus_pod:
            result = ssh.execute_command(
                f"""kubectl exec -n panda {focus_pod} -- env 2>&1 | grep -iE "livefs|forwarder" | head -10"""
            )
            print(get_output(result) or "No livefs/forwarder env vars found")
            
            # Check running processes
            print("\n📁 Checking what processes are running in focus-server pod...")
            result = ssh.execute_command(
                f"""kubectl exec -n panda {focus_pod} -- ps aux 2>&1 | head -20"""
            )
            print(get_output(result))
        
        # 6. Check if livefs_forwarder is a separate deployment
        print("\n📁 Checking for livefs_forwarder deployment...")
        result = ssh.execute_command(
            """kubectl get deploy -n panda -o name 2>&1 | grep -iE "forwarder|livefs" """
        )
        print(get_output(result) or "No livefs_forwarder deployment found")
        
        # 7. Check how to start livefs_forwarder manually
        print("\n📁 Checking how livefs_forwarder should be started...")
        result = ssh.execute_command(
            """grep -A 10 "livefs_forwarder:" /home/prisma/debug-codebase/pz/config/autocfg/parameters/components/focus_server.yaml 2>&1"""
        )
        print(get_output(result))
        
        # 8. Summary
        print("\n" + "=" * 60)
        print("📋 SUMMARY: How to enable livefs_forwarder")
        print("=" * 60)
        
    finally:
        ssh.disconnect()


if __name__ == "__main__":
    main()

