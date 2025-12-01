"""
Script to investigate why Focus Server doesn't return recordings from MongoDB.
"""
import sys
sys.path.insert(0, '.')

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

def main():
    cm = ConfigManager()
    ssh = SSHManager(cm)

    if not ssh.connect():
        print('Failed to connect via SSH')
        return

    try:
        pod_name = 'panda-panda-focus-server-7c767d7688-z6n5p'
        
        # 1. Check py config files
        print('='*70)
        print('1. PY CONFIG FILES')
        print('='*70)
        result = ssh.execute_command(f'kubectl exec -n panda {pod_name} -- find /home/prisma/pz/config/py -type f 2>/dev/null')
        print(result.get('stdout', '') or 'No py config files')
        
        # 2. Check config.yaml
        print('\n' + '='*70)
        print('2. CONFIG.YAML CONTENT')
        print('='*70)
        result = ssh.execute_command(f'kubectl exec -n panda {pod_name} -- cat /home/prisma/pz/config/py/config.yaml 2>/dev/null')
        output = result.get('stdout', '')
        print(output[:3000] if output else 'No config.yaml')
        
        # 3. Check panda config folder
        print('\n' + '='*70)
        print('3. PANDA CONFIG FOLDER')
        print('='*70)
        result = ssh.execute_command(f'kubectl exec -n panda {pod_name} -- ls -la /home/prisma/pz/config/panda/ 2>/dev/null')
        print(result.get('stdout', '') or 'No panda config folder')
        
        # 4. Try calling recordings API from inside pod (Nov 26 timestamps from screenshot)
        print('\n' + '='*70)
        print('4. CALLING API FROM INSIDE POD')
        print('='*70)
        # Nov 26, 2025 17:16 UTC
        cmd = f'''kubectl exec -n panda {pod_name} -- curl -s -X POST http://localhost:5000/recordings_in_time_range -H "Content-Type: application/json" -d '{{"start_time": 1732641360, "end_time": 1732641600}}' '''
        result = ssh.execute_command(cmd)
        print('Query: start=1732641360 (Nov 26 17:16), end=1732641600 (Nov 26 17:20)')
        print('Response:', result.get('stdout', '') or 'empty')
        
        # 5. Check Focus Server source files
        print('\n' + '='*70)
        print('5. FOCUS SERVER SOURCE FILES')
        print('='*70)
        result = ssh.execute_command(f'kubectl exec -n panda {pod_name} -- ls -la /home/prisma/pz/microservices/pzpy/focus_server/ 2>/dev/null')
        print(result.get('stdout', '') or 'No focus_server dir')
        
        # 6. Check recordings route implementation
        print('\n' + '='*70)
        print('6. FOCUS SERVER ROUTES - RECORDINGS')
        print('='*70)
        cmd = f'kubectl exec -n panda {pod_name} -- grep -A 40 "recordings_in_time" /home/prisma/pz/microservices/pzpy/focus_server/focus_server_routes.py 2>/dev/null'
        result = ssh.execute_command(cmd)
        print(result.get('stdout', '') or 'Not found in routes')
        
        # 7. Check timeline_reader
        print('\n' + '='*70)
        print('7. TIMELINE_READER MODULE')
        print('='*70)
        result = ssh.execute_command(f'kubectl exec -n panda {pod_name} -- ls -la /home/prisma/pz/microservices/pzpy/recording/ 2>/dev/null')
        print(result.get('stdout', '') or 'No recording dir')
        
        # 8. Check timeline_reader.py content
        print('\n' + '='*70)
        print('8. TIMELINE_READER.PY - RECORDINGS QUERY')
        print('='*70)
        cmd = f'kubectl exec -n panda {pod_name} -- grep -A 30 "def get_recordings" /home/prisma/pz/microservices/pzpy/recording/timeline_reader.py 2>/dev/null'
        result = ssh.execute_command(cmd)
        print(result.get('stdout', '') or 'Not found or no get_recordings method')
        
        # 9. Check how Focus Server connects to MongoDB
        print('\n' + '='*70)
        print('9. MONGODB CONNECTION IN FOCUS SERVER')
        print('='*70)
        cmd = f'kubectl exec -n panda {pod_name} -- grep -r "MongoClient\\|pymongo" /home/prisma/pz/microservices/pzpy/focus_server/ 2>/dev/null'
        result = ssh.execute_command(cmd)
        print(result.get('stdout', '') or 'No MongoDB connection in focus_server')

    finally:
        ssh.disconnect()


if __name__ == '__main__':
    main()

