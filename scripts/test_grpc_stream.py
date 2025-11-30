"""Test actual gRPC streaming with the new pandadatastream proto."""
import sys
sys.path.insert(0, 'C:\\Projects\\focus_server_automation')

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

def main():
    cm = ConfigManager()
    ssh = SSHManager(cm)
    
    if not ssh.connect():
        print("Failed to connect via SSH")
        return
    
    try:
        # Get a running pod and its service info
        print("=== Finding running gRPC job ===")
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
        
        # Get node IP
        result = ssh.execute_command('kubectl get nodes -o jsonpath="{.items[0].status.addresses[?(@.type==\\"InternalIP\\")].address}"')
        node_ip = result.get('stdout', '').strip()
        
        print(f'Pod: {pod_name}')
        print(f'Job ID: {job_id}')
        print(f'Target: {node_ip}:{node_port}')
        
        # Create a Python script to run on the remote server
        test_script = '''
import sys
import grpc

# Add the paths
sys.path.insert(0, '/home/prisma/debug-codebase/pz/microservices')

# Import the proto
from pzpy.recording.backends.protocols.panda_datastream import pandadatastream_pb2, pandadatastream_pb2_grpc

target = "{target}"
print(f"Connecting to gRPC at {{target}}...")

try:
    channel = grpc.insecure_channel(target)
    grpc.channel_ready_future(channel).result(timeout=10)
    print("Channel ready!")
    
    stub = pandadatastream_pb2_grpc.DataStreamServiceStub(channel)
    request = pandadatastream_pb2.StreamDataRequest(stream_id=0)
    
    print("Starting stream...")
    count = 0
    for frame in stub.StreamData(request, timeout=30):
        count += 1
        print(f"Frame {{count}}: shape={{frame.data_shape_x}}x{{frame.data_shape_y}}, amp=[{{frame.global_minimum:.2f}}, {{frame.global_maximum:.2f}}]")
        if count >= 5:
            break
    
    print(f"SUCCESS! Received {{count}} frames")
    channel.close()
except Exception as e:
    print(f"ERROR: {{e}}")
'''.format(target=f"{node_ip}:{node_port}")
        
        # Run the script on the remote pod
        print(f"\n=== Running gRPC test from inside cluster ===")
        
        # We need to exec into a pod that has Python with grpc and the proto
        # The grpc-job pod itself should have these
        cmd = f'kubectl exec -n panda {pod_name} -- python3 -c "{test_script}"'
        
        # Escape the script properly for shell
        import base64
        script_b64 = base64.b64encode(test_script.encode()).decode()
        cmd = f'kubectl exec -n panda {pod_name} -- bash -c "echo {script_b64} | base64 -d | python3"'
        
        result = ssh.execute_command(cmd, timeout=60)
        print("STDOUT:", result.get('stdout', ''))
        print("STDERR:", result.get('stderr', ''))
        
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()

