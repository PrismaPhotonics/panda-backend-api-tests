"""
Simple check for livefs_forwarder.
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
        print("Connecting to SSH...")
        ssh.connect()
        print("Connected!")
        
        # Simple check for livefs_forwarder config
        print("\n=== livefs_forwarder configuration ===\n")
        result = ssh.execute_command(
            """grep -B2 -A10 "livefs_forwarder" /home/prisma/debug-codebase/pz/config/autocfg/parameters/components/focus_server.yaml 2>&1""",
            timeout=30
        )
        print(get_output(result))
        
        # Check if it's a Helm value
        print("\n=== Checking Helm values ===")
        result = ssh.execute_command(
            """helm get values panda -n panda 2>&1 | head -30""",
            timeout=30
        )
        print(get_output(result))
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            ssh.disconnect()
        except:
            pass


if __name__ == "__main__":
    main()

