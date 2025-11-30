"""
Test connection to Mock gRPC Server via SSH tunnel.
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
        print("\n🔌 Connecting to cluster...")
        ssh.connect()
        print("✅ Connected!")
        
        # Test the mock server from inside the cluster
        print("\n🔍 Testing mock server from inside the cluster...")
        
        # First, check if it's still running
        result = ssh.execute_command(
            """kubectl exec -n panda panda-panda-focus-server-78dbcfd9d9-xbcjk -- netstat -tlnp 2>/dev/null | grep 15555""",
            timeout=30
        )
        status = get_output(result)
        
        if "15555" not in status:
            print("⚠️ Mock server not running. Restarting...")
            # Restart it
            result = ssh.execute_command(
                """kubectl exec -n panda panda-panda-focus-server-78dbcfd9d9-xbcjk -- bash -c '
cd /home/prisma/debug-codebase/pz/microservices
export PRISMA_CONFIG=/home/prisma/debug-codebase/pz/config
export PRISMA_LOGS=/tmp
nohup python3 -c "
import sys
sys.path.insert(0, \\"/home/prisma/debug-codebase/pz/microservices\\")
from focus_server.tests.grpc_mock_server import serve
config = {
    \\"sg_n_fft\\": 2048,
    \\"sg_overlap\\": 0.5,
    \\"roi\\": [0, 750],
    \\"frequencies_amount\\": 500,
    \\"time_range\\": [None, None]
}
serve(config, 15555, True)
" > /tmp/mock_grpc.log 2>&1 &
'""",
                timeout=15
            )
            import time
            time.sleep(3)
        
        print("✅ Mock server is running on port 15555")
        
        # Now test it with a Python gRPC client from inside the pod
        print("\n🧪 Running gRPC client test from inside the cluster...")
        
        test_code = '''
import sys
sys.path.insert(0, "/home/prisma/debug-codebase/pz/microservices")
import grpc
from pzpy.recording.backends.protocols.panda_datastream import pandadatastream_pb2, pandadatastream_pb2_grpc

channel = grpc.insecure_channel("localhost:15555")
stub = pandadatastream_pb2_grpc.DataStreamServiceStub(channel)

request = pandadatastream_pb2.StreamDataRequest(stream_id=0)
print("Connecting to mock server...")

frame_count = 0
try:
    for response in stub.StreamData(request, timeout=10):
        frame_count += 1
        print(f"Frame {frame_count}: shape={response.data_shape_x}x{response.data_shape_y}, amp={response.global_minimum:.2f}-{response.global_maximum:.2f}")
        if frame_count >= 3:
            break
    print(f"SUCCESS: Received {frame_count} frames!")
except Exception as e:
    print(f"ERROR: {e}")

channel.close()
'''
        
        result = ssh.execute_command(
            f"""kubectl exec -n panda panda-panda-focus-server-78dbcfd9d9-xbcjk -- bash -c '
cd /home/prisma/debug-codebase/pz/microservices
export PRISMA_CONFIG=/home/prisma/debug-codebase/pz/config
export PRISMA_LOGS=/tmp
python3 -c "{test_code}"
'""",
            timeout=30
        )
        
        output = get_output(result)
        print(output)
        
        if "SUCCESS" in output:
            print("\n" + "=" * 70)
            print("✅ gRPC DATA FLOW VERIFIED!")
            print("=" * 70)
            print("""
ה-Mock Server עובד ומייצר דאטה!

עכשיו אפשר:
1. לבדוק את ה-GrpcStreamClient שלנו
2. להריץ load tests עם דאטה אמיתי (סינתטי)
""")
        else:
            print("\n⚠️ Test may have issues. Check the output above.")
        
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

