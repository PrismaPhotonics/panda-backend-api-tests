"""
Copy kubeconfig from remote K8s host using SSH
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.ssh_manager import SSHManager
from config.config_manager import ConfigManager

def main():
    print("Copying kubeconfig from remote host...")
    
    # Get config
    config = ConfigManager(env="staging")
    ssh_config = config.get("ssh")
    
    # Connect to remote host
    ssh_manager = SSHManager(config)
    
    try:
        print(f"Connecting to {ssh_config['host']}...")
        ssh_manager.connect()
        print("Connected!")
        
        # Read remote kubeconfig
        print("Reading remote kubeconfig...")
        result = ssh_manager.execute_command("cat ~/.kube/config")
        
        if result["exit_code"] != 0:
            print(f"Failed to read remote kubeconfig: {result['stderr']}")
            return 1
        
        kubeconfig_content = result["stdout"]
        
        # Write to local file
        local_kubeconfig = Path.home() / ".kube" / "config"
        local_kubeconfig.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Writing to {local_kubeconfig}...")
        local_kubeconfig.write_text(kubeconfig_content)
        
        print("SUCCESS: Kubeconfig copied successfully!")
        print(f"Location: {local_kubeconfig}")
        
        # Verify
        if local_kubeconfig.exists():
            size = local_kubeconfig.stat().st_size
            print(f"File size: {size} bytes")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh_manager.disconnect()

if __name__ == "__main__":
    sys.exit(main())

