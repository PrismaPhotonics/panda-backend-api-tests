"""
Start gRPC Mock Server and test data flow.

This script:
1. Starts the mock gRPC server in the focus-server pod
2. Tests connecting to it with our GrpcStreamClient

This bypasses the need for livefs_forwarder or RabbitMQ data flow.
"""

import sys
import os
import time
import threading

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
    print("gRPC Mock Server Test")
    print("=" * 70)
    
    try:
        print("\n🔌 Connecting to cluster via SSH...")
        ssh.connect()
        print("✅ Connected!")
        
        # Step 1: Get focus-server pod name
        print("\n📦 Getting focus-server pod...")
        result = ssh.execute_command(
            """kubectl get pods -n panda | grep focus-server | awk '{print $1}' | head -1""",
            timeout=30
        )
        focus_pod = get_output(result).strip()
        
        if not focus_pod:
            print("❌ Focus server pod not found!")
            return
        
        print(f"✅ Focus server pod: {focus_pod}")
        
        # Step 2: Check if mock server script exists
        print("\n📁 Checking mock server script...")
        result = ssh.execute_command(
            f"""kubectl exec -n panda {focus_pod} -- ls -la /home/prisma/debug-codebase/pz/microservices/focus_server/tests/grpc_mock_server.py 2>&1""",
            timeout=30
        )
        print(get_output(result))
        
        # Step 3: Start mock server in background
        print("\n🚀 Starting mock gRPC server on port 5555...")
        print("   (This will run in background)")
        
        # Create a modified mock server that listens on a specific port
        mock_command = '''
cd /home/prisma/debug-codebase/pz/microservices && \\
PRISMA_CONFIG=/home/prisma/debug-codebase/pz/config \\
PRISMA_LOGS=/tmp \\
python3 -c "
from focus_server.tests.grpc_mock_server import serve
config = {
    'sg_n_fft': 2048,
    'sg_overlap': 0.5,
    'roi': [0, 750],
    'frequencies_amount': 500,
    'time_range': [None, None]
}
print('Starting mock gRPC server on port 5555...')
serve(config, 5555, True)
" &
'''
        
        result = ssh.execute_command(
            f"""kubectl exec -n panda {focus_pod} -- bash -c '{mock_command}' 2>&1""",
            timeout=10
        )
        print(get_output(result))
        
        print("\n⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Step 4: Check if it's running
        print("\n🔍 Checking if mock server is running...")
        result = ssh.execute_command(
            f"""kubectl exec -n panda {focus_pod} -- netstat -tlnp 2>/dev/null | grep 5555""",
            timeout=30
        )
        server_status = get_output(result)
        
        if "5555" in server_status:
            print(f"✅ Mock server is running!")
            print(f"   {server_status.strip()}")
            
            # Get the NodePort or ClusterIP
            print("\n📡 Getting connection details...")
            result = ssh.execute_command(
                f"""kubectl get pod -n panda {focus_pod} -o jsonpath='{{.status.podIP}}'""",
                timeout=30
            )
            pod_ip = get_output(result).strip()
            print(f"   Pod IP: {pod_ip}")
            print(f"   Port: 5555")
            
            print("\n✅ You can now test with:")
            print(f"   python -c \"")
            print(f"   from src.apis.grpc_client import GrpcStreamClient")
            print(f"   client = GrpcStreamClient()")
            print(f"   client.connect('{pod_ip}', 5555)")
            print(f"   for frame in client.stream_data(max_frames=3):")
            print(f"       print(f'Got frame: {{frame.data_shape_x}}x{{frame.data_shape_y}}')")
            print(f"   \"")
        else:
            print("❌ Mock server did not start")
            print("   Checking logs...")
            result = ssh.execute_command(
                f"""kubectl logs -n panda {focus_pod} --tail=10 2>&1""",
                timeout=30
            )
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

