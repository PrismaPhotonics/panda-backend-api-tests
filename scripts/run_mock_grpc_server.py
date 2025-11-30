"""
Run Mock gRPC Server for Testing

This script starts a mock gRPC server in the Kubernetes cluster
that generates synthetic spectrogram data for testing.

Usage:
    python scripts/run_mock_grpc_server.py

What it does:
1. Connects to the K8s cluster via SSH
2. Finds the focus-server pod
3. Starts the mock gRPC server on a specific port
4. Returns connection details for testing
"""

import sys
import os
import time

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
    print("🧪 Mock gRPC Server Launcher")
    print("=" * 70)
    print("""
מה הסקריפט הזה עושה:
1. מתחבר ל-Kubernetes cluster
2. מוצא את ה-focus-server pod
3. מפעיל Mock gRPC Server שמייצר דאטה סינתטית
4. מחזיר פרטי התחברות לבדיקות
""")
    
    try:
        print("🔌 Connecting to cluster...")
        ssh.connect()
        print("✅ Connected to cluster!")
        
        # Step 1: Find focus-server pod
        print("\n📦 Finding focus-server pod...")
        result = ssh.execute_command(
            """kubectl get pods -n panda | grep focus-server | grep Running | awk '{print $1}' | head -1""",
            timeout=30
        )
        focus_pod = get_output(result).strip()
        
        if not focus_pod:
            print("❌ Error: Focus server pod not found or not running")
            return
        
        print(f"✅ Found pod: {focus_pod}")
        
        # Step 2: Get pod IP
        print("\n📡 Getting pod IP address...")
        result = ssh.execute_command(
            f"""kubectl get pod -n panda {focus_pod} -o jsonpath='{{.status.podIP}}'""",
            timeout=30
        )
        pod_ip = get_output(result).strip()
        print(f"✅ Pod IP: {pod_ip}")
        
        # Step 3: Check if mock server exists
        print("\n📁 Verifying mock server script exists...")
        result = ssh.execute_command(
            f"""kubectl exec -n panda {focus_pod} -- test -f /home/prisma/debug-codebase/pz/microservices/focus_server/tests/grpc_mock_server.py && echo "EXISTS" || echo "NOT_FOUND" """,
            timeout=30
        )
        
        if "NOT_FOUND" in get_output(result):
            print("❌ Mock server script not found!")
            return
        
        print("✅ Mock server script found")
        
        # Step 4: Start mock server
        MOCK_PORT = 15555  # Use a high port that's unlikely to conflict
        
        print(f"\n🚀 Starting mock gRPC server on port {MOCK_PORT}...")
        
        # Kill any existing mock server
        ssh.execute_command(
            f"""kubectl exec -n panda {focus_pod} -- pkill -f "grpc_mock_server" 2>/dev/null || true""",
            timeout=10
        )
        
        # Start the mock server
        start_cmd = f'''
kubectl exec -n panda {focus_pod} -- bash -c '
cd /home/prisma/debug-codebase/pz/microservices
export PRISMA_CONFIG=/home/prisma/debug-codebase/pz/config
export PRISMA_LOGS=/tmp
nohup python3 -c "
import sys
sys.path.insert(0, \\"/home/prisma/debug-codebase/pz/microservices\\")
from focus_server.tests.grpc_mock_server import serve

config = {{
    \\"sg_n_fft\\": 2048,
    \\"sg_overlap\\": 0.5,
    \\"roi\\": [0, 750],
    \\"frequencies_amount\\": 500,
    \\"time_range\\": [None, None]
}}
print(\\"Mock gRPC Server starting on port {MOCK_PORT}...\\")
serve(config, {MOCK_PORT}, True)
" > /tmp/mock_grpc.log 2>&1 &
echo $!
'
'''
        
        result = ssh.execute_command(start_cmd, timeout=15)
        pid = get_output(result).strip()
        print(f"   Started with PID: {pid}")
        
        # Wait for server to start
        print("   Waiting for server to initialize...")
        time.sleep(3)
        
        # Step 5: Verify server is running
        print("\n🔍 Verifying server is running...")
        result = ssh.execute_command(
            f"""kubectl exec -n panda {focus_pod} -- netstat -tlnp 2>/dev/null | grep {MOCK_PORT} || echo "NOT_LISTENING" """,
            timeout=30
        )
        status = get_output(result)
        
        if "NOT_LISTENING" in status or not status.strip():
            print("⚠️ Server may not be listening yet. Checking logs...")
            result = ssh.execute_command(
                f"""kubectl exec -n panda {focus_pod} -- cat /tmp/mock_grpc.log 2>&1 | tail -20""",
                timeout=30
            )
            print(get_output(result))
            
            # Try alternative check
            result = ssh.execute_command(
                f"""kubectl exec -n panda {focus_pod} -- ps aux | grep -i mock | grep -v grep""",
                timeout=30
            )
            ps_output = get_output(result)
            if ps_output:
                print(f"\n✅ Process is running:\n{ps_output}")
        else:
            print(f"✅ Server is listening:\n   {status.strip()}")
        
        # Step 6: Print connection info
        print("\n" + "=" * 70)
        print("📋 CONNECTION DETAILS")
        print("=" * 70)
        print(f"""
Mock gRPC Server is running!

Connection Details:
  • Host: {pod_ip}
  • Port: {MOCK_PORT}
  • Pod:  {focus_pod}

⚠️ Note: This IP is internal to the K8s cluster.
   To connect from outside, you need port-forwarding:
   
   kubectl port-forward -n panda {focus_pod} {MOCK_PORT}:{MOCK_PORT}
   
   Then connect to: localhost:{MOCK_PORT}
""")
        
        print("\n" + "=" * 70)
        print("🧪 TEST CODE")
        print("=" * 70)
        print(f'''
# After port-forwarding, run this Python code:

from src.apis.grpc_client import GrpcStreamClient

client = GrpcStreamClient()
client.connect("localhost", {MOCK_PORT})

print("Streaming data from mock server...")
for i, frame in enumerate(client.stream_data(stream_id=0, max_frames=5)):
    print(f"Frame {{i+1}}: shape={{frame.data_shape_x}}x{{frame.data_shape_y}}")
    print(f"         amplitude: {{frame.global_minimum:.2f}} - {{frame.global_maximum:.2f}}")

client.disconnect()
print("✅ Test completed!")
''')
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            ssh.disconnect()
            print("\n🔌 Disconnected from cluster")
        except:
            pass


if __name__ == "__main__":
    main()

