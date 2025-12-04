"""
Simple test for Mock gRPC Server.
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
    print("🧪 Testing Mock gRPC Server (Simple)")
    print("=" * 70)
    
    try:
        print("\n🔌 Connecting...")
        ssh.connect()
        print("✅ Connected!")
        
        POD = "panda-panda-focus-server-78dbcfd9d9-xbcjk"
        
        # Check if mock server is running
        print("\n🔍 Checking mock server status...")
        result = ssh.execute_command(
            f"kubectl exec -n panda {POD} -- netstat -tlnp 2>/dev/null | grep 15555",
            timeout=30
        )
        status = get_output(result)
        print(f"   {status.strip() if status.strip() else 'Not listening'}")
        
        if "15555" not in status:
            print("   ⚠️ Mock server not running!")
            return
        
        # Run the grpc_mock_client.py that already exists
        print("\n🧪 Running existing mock client test...")
        result = ssh.execute_command(
            f"""kubectl exec -n panda {POD} -- bash -c 'cd /home/prisma/debug-codebase/pz/microservices && PRISMA_CONFIG=/home/prisma/debug-codebase/pz/config PRISMA_LOGS=/tmp timeout 10 python3 -c "
import grpc
import sys
sys.path.insert(0, chr(46))
from pzpy.recording.backends.protocols.panda_datastream import pandadatastream_pb2, pandadatastream_pb2_grpc

print(chr(67)+chr(111)+chr(110)+chr(110)+chr(101)+chr(99)+chr(116)+chr(105)+chr(110)+chr(103)+chr(46)+chr(46)+chr(46))
channel = grpc.insecure_channel(chr(108)+chr(111)+chr(99)+chr(97)+chr(108)+chr(104)+chr(111)+chr(115)+chr(116)+chr(58)+chr(49)+chr(53)+chr(53)+chr(53)+chr(53))
stub = pandadatastream_pb2_grpc.DataStreamServiceStub(channel)
request = pandadatastream_pb2.StreamDataRequest(stream_id=0)

count = 0
for resp in stub.StreamData(request, timeout=5):
    count += 1
    print(f\\'Frame {{count}}: {{resp.data_shape_x}}x{{resp.data_shape_y}}\\')
    if count >= 3:
        break

print(f\\'SUCCESS: {{count}} frames\\')
channel.close()
" 2>&1'""",
            timeout=30
        )
        
        output = get_output(result)
        print(output)
        
        if "SUCCESS" in output or "Frame" in output:
            print("\n" + "=" * 70)
            print("✅ MOCK gRPC SERVER WORKS!")
            print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        try:
            ssh.disconnect()
        except:
            pass


if __name__ == "__main__":
    main()

