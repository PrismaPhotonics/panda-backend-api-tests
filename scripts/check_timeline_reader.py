"""Check timeline_reader and recordings query logic."""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

cm = ConfigManager()
ssh = SSHManager(cm)
ssh.connect()

pod = 'panda-panda-focus-server-7c767d7688-z6n5p'
pzpy_path = '/home/prisma/.local/lib/python3.10/site-packages/pzpy'

# 1. Find timeline_reader
print('='*70)
print('1. FIND TIMELINE_READER')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- find {pzpy_path} -name "*timeline*" -type f 2>/dev/null')
print(result.get('stdout', '') or 'Not found')

# 2. Find focus_server modules
print('\n' + '='*70)
print('2. FOCUS SERVER MODULE FILES')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- ls -la {pzpy_path}/focus_server/ 2>/dev/null')
print(result.get('stdout', '') or 'No focus_server dir')

# 3. Check recordings_in_time_range implementation
print('\n' + '='*70)
print('3. RECORDINGS_IN_TIME_RANGE IN FOCUS SERVER')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -rn "recordings_in_time" {pzpy_path}/focus_server/ 2>/dev/null')
print(result.get('stdout', '') or 'Not found in focus_server')

# 4. Check recording module
print('\n' + '='*70)
print('4. RECORDING MODULE')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- ls -la {pzpy_path}/recording/ 2>/dev/null')
print(result.get('stdout', '') or 'No recording module')

# 5. Check timeline_reader.py content (get_recordings method)
print('\n' + '='*70)
print('5. TIMELINE_READER - GET_RECORDINGS METHOD')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -A 50 "def get_recordings" {pzpy_path}/recording/timeline_reader.py 2>/dev/null | head -60')
print(result.get('stdout', '') or 'Method not found')

# 6. Check how recordings_in_time_range is handled in routes
print('\n' + '='*70)
print('6. FOCUS SERVER ROUTES')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -B 5 -A 30 "recordings_in_time" {pzpy_path}/focus_server/focus_server_routes.py 2>/dev/null')
print(result.get('stdout', '') or 'Not found')

# 7. Check MongoClient usage
print('\n' + '='*70)
print('7. MONGODB CLIENT IN RECORDING MODULE')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -rn "MongoClient\\|pymongo" {pzpy_path}/recording/ 2>/dev/null | head -20')
print(result.get('stdout', '') or 'No MongoDB usage')

ssh.disconnect()


