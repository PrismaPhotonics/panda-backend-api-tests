"""Simple gRPC test - run from inside the cluster."""
import sys
sys.path.insert(0, 'C:\\Projects\\focus_server_automation')

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

def main():
    cm = ConfigManager()
    ssh = SSHManager(cm)
    
    if not ssh.connect():
        print("Failed to connect via SSH")
        return
    
    try:
        # Get a running pod
        result = ssh.execute_command('kubectl get pods -n panda | grep grpc-job | grep Running | head -1')
        lines = result.get('stdout', '').strip().split()
        if not lines:
            print('No running pods found')
            return
        
        pod_name = lines[0]
        parts = pod_name.split('-')
        job_id = f"{parts[2]}-{parts[3]}" if len(parts) >= 4 else "unknown"
        
        # Get NodePort
        service_name = f"grpc-service-{job_id}"
        result = ssh.execute_command(f'kubectl get svc -n panda {service_name} -o jsonpath="{{.spec.ports[0].nodePort}}"')
        node_port = result.get('stdout', '').strip()
        
        print(f'Pod: {pod_name}')
        print(f'Job ID: {job_id}')
        print(f'Service: {service_name}')
        print(f'NodePort: {node_port}')
        
        # Test local connection first (same pod, localhost:5000)
        print("\n=== Test 1: Connection to localhost:5000 (same pod) ===")
        simple_script = '''
import grpc
try:
    channel = grpc.insecure_channel("localhost:5000")
    grpc.channel_ready_future(channel).result(timeout=5)
    print("localhost:5000 - OK")
    channel.close()
except Exception as e:
    print(f"localhost:5000 - FAILED: {e}")
'''
        import base64
        script_b64 = base64.b64encode(simple_script.encode()).decode()
        cmd = f'kubectl exec -n panda {pod_name} -- bash -c "echo {script_b64} | base64 -d | python3"'
        result = ssh.execute_command(cmd, timeout=30)
        print(result.get('stdout', ''))
        if result.get('stderr'):
            print('STDERR:', result.get('stderr'))
        
        # Test connection to NodePort
        print(f"\n=== Test 2: Connection to 10.10.10.151:{node_port} (NodePort) ===")
        simple_script2 = f'''
import grpc
try:
    channel = grpc.insecure_channel("10.10.10.151:{node_port}")
    grpc.channel_ready_future(channel).result(timeout=5)
    print("NodePort - OK")
    channel.close()
except Exception as e:
    print(f"NodePort - FAILED: {{e}}")
'''
        script_b64 = base64.b64encode(simple_script2.encode()).decode()
        cmd = f'kubectl exec -n panda {pod_name} -- bash -c "echo {script_b64} | base64 -d | python3"'
        result = ssh.execute_command(cmd, timeout=30)
        print(result.get('stdout', ''))
        if result.get('stderr'):
            print('STDERR:', result.get('stderr'))
        
        # Now test streaming
        print(f"\n=== Test 3: Streaming from localhost:5000 ===")
        stream_script = '''
import sys
sys.path.insert(0, '/home/prisma/debug-codebase/pz/microservices')
import grpc
from pzpy.recording.backends.protocols.panda_datastream import pandadatastream_pb2, pandadatastream_pb2_grpc

try:
    channel = grpc.insecure_channel("localhost:5000")
    grpc.channel_ready_future(channel).result(timeout=5)
    print("Channel ready")
    
    stub = pandadatastream_pb2_grpc.DataStreamServiceStub(channel)
    request = pandadatastream_pb2.StreamDataRequest(stream_id=0)
    
    print("Starting stream...")
    count = 0
    for frame in stub.StreamData(request, timeout=10):
        count += 1
        print(f"Frame {count}: {frame.data_shape_x}x{frame.data_shape_y}, amp=[{frame.global_minimum:.2f}, {frame.global_maximum:.2f}]")
        if count >= 3:
            break
    
    print(f"SUCCESS! {count} frames")
    channel.close()
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()
'''
        script_b64 = base64.b64encode(stream_script.encode()).decode()
        cmd = f'kubectl exec -n panda {pod_name} -- bash -c "echo {script_b64} | base64 -d | python3"'
        result = ssh.execute_command(cmd, timeout=60)
        print(result.get('stdout', ''))
        if result.get('stderr'):
            print('STDERR:', result.get('stderr'))
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

