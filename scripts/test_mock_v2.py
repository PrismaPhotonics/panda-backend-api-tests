"""
Test Mock gRPC Server - Version 2.
Creates a test script on the server and runs it.
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
    print("🧪 Testing Mock gRPC Server")
    print("=" * 70)
    
    try:
        print("\n🔌 Connecting...")
        ssh.connect()
        print("✅ Connected!")
        
        POD = "panda-panda-focus-server-78dbcfd9d9-xbcjk"
        
        # 1. Check if mock server is running
        print("\n🔍 Step 1: Checking mock server...")
        result = ssh.execute_command(
            f"kubectl exec -n panda {POD} -- netstat -tlnp 2>/dev/null | grep 15555",
            timeout=30
        )
        status = get_output(result)
        
        if "15555" in status and "LISTEN" in status:
            print("✅ Mock server is LISTENING on port 15555")
        else:
            print("❌ Mock server not running!")
            return
        
        # 2. Create test script on server
        print("\n📝 Step 2: Creating test script on server...")
        
        test_script = '''#!/usr/bin/env python3
import sys
sys.path.insert(0, "/home/prisma/debug-codebase/pz/microservices")
import grpc
from pzpy.recording.backends.protocols.panda_datastream import pandadatastream_pb2, pandadatastream_pb2_grpc

print("Connecting to mock gRPC server on localhost:15555...")
channel = grpc.insecure_channel("localhost:15555")
stub = pandadatastream_pb2_grpc.DataStreamServiceStub(channel)
request = pandadatastream_pb2.StreamDataRequest(stream_id=0)

count = 0
try:
    for resp in stub.StreamData(request, timeout=5):
        count += 1
        print(f"Frame {count}: shape={resp.data_shape_x}x{resp.data_shape_y}, amp={resp.global_minimum:.3f}-{resp.global_maximum:.3f}")
        if count >= 3:
            break
    print(f"SUCCESS: Received {count} frames from mock server!")
except grpc.RpcError as e:
    print(f"gRPC Error: {e.code()} - {e.details()}")
except Exception as e:
    print(f"Error: {e}")
finally:
    channel.close()
'''
        
        # Write the script to the pod
        result = ssh.execute_command(
            f"kubectl exec -n panda {POD} -- bash -c 'cat > /tmp/test_grpc.py << ENDOFSCRIPT\n{test_script}\nENDOFSCRIPT'",
            timeout=30
        )
        print("✅ Test script created")
        
        # 3. Run the test script
        print("\n🚀 Step 3: Running test...")
        result = ssh.execute_command(
            f"kubectl exec -n panda {POD} -- bash -c 'cd /home/prisma/debug-codebase/pz/microservices && PRISMA_CONFIG=/home/prisma/debug-codebase/pz/config PRISMA_LOGS=/tmp python3 /tmp/test_grpc.py'",
            timeout=30
        )
        
        output = get_output(result)
        print("\n" + "-" * 50)
        print(output)
        print("-" * 50)
        
        if "SUCCESS" in output:
            print("\n" + "=" * 70)
            print("🎉 gRPC DATA STREAMING WORKS!")
            print("=" * 70)
            print("""
✅ ה-Mock Server מייצר דאטה בהצלחה!
✅ ה-gRPC client מקבל frames!

עכשיו אפשר לבדוק את ה-GrpcStreamClient שלנו
עם port-forward לשרת המקומי.
""")
        elif "Error" in output or "error" in output.lower():
            print("\n⚠️ There was an error. See output above.")
        else:
            print("\n⚠️ Unexpected output. Check above.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            ssh.disconnect()
        except:
            pass


if __name__ == "__main__":
    main()

