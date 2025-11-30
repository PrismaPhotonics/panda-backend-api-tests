"""
Setup port forward to mock gRPC server.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager


def get_output(result):
    if isinstance(result, dict):
        return result.get('stdout', '') or result.get('output', '')
    return str(result) if result else ''


def main():
    config_manager = ConfigManager()
    ssh = SSHManager(config_manager)
    
    print("=" * 70)
    print("🔗 Setting up Port Forward to Mock gRPC Server")
    print("=" * 70)
    
    try:
        print("\n🔌 Connecting...")
        ssh.connect()
        print("✅ Connected!")
        
        POD = "panda-panda-focus-server-78dbcfd9d9-xbcjk"
        
        # Start port forward in background
        print("\n🚀 Starting port-forward...")
        print("   This will forward localhost:15555 -> pod:15555")
        
        result = ssh.execute_command(
            f"nohup kubectl port-forward -n panda {POD} 15555:15555 --address 0.0.0.0 > /tmp/port-forward.log 2>&1 &",
            timeout=10
        )
        
        import time
        time.sleep(2)
        
        # Check if it's running
        result = ssh.execute_command(
            "ps aux | grep 'port-forward' | grep -v grep | head -1",
            timeout=10
        )
        pf_status = get_output(result)
        
        if "port-forward" in pf_status:
            print("✅ Port forward is running!")
            print(f"   {pf_status.strip()[:80]}...")
            
            print("\n" + "=" * 70)
            print("📋 CONNECTION INFO")
            print("=" * 70)
            print(f"""
Port forward is active on the K8s worker node (10.10.10.150)

To connect from your machine, you have two options:

Option 1: SSH tunnel from your machine
  ssh -L 15555:localhost:15555 prisma@10.10.10.150

Option 2: Direct connection (if network allows)
  Connect to: 10.10.10.150:15555

Then test with:
  python -c "
  from src.apis.grpc_client import GrpcStreamClient
  client = GrpcStreamClient()
  client.connect('localhost', 15555)
  for frame in client.stream_data(max_frames=3):
      print(f'Frame: {{frame.data_shape_x}}x{{frame.data_shape_y}}')
  client.disconnect()
  "
""")
        else:
            print("⚠️ Port forward may not have started. Check logs:")
            result = ssh.execute_command("cat /tmp/port-forward.log 2>&1 | tail -10", timeout=10)
            print(get_output(result))
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        try:
            ssh.disconnect()
        except:
            pass


if __name__ == "__main__":
    main()

