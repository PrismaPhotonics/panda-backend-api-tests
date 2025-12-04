"""Check mongo_mapper.py implementation."""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

cm = ConfigManager()
ssh = SSHManager(cm)
ssh.connect()

pod = 'panda-panda-focus-server-7c767d7688-z6n5p'
pzpy_path = '/home/prisma/.local/lib/python3.10/site-packages/pzpy'

# 1. Get full mongo_mapper.py content
print('='*70)
print('1. MONGO_MAPPER.PY CONTENT')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- cat {pzpy_path}/recording/mongo_mapper/mongo_mapper.py 2>/dev/null')
print(result.get('stdout', '') or 'File not found')

# 2. Check how recordings_in_time_range endpoint works
print('\n' + '='*70)
print('2. SEARCH FOR recordings_in_time IN ALL PZPY')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -rn "recordings_in_time" {pzpy_path}/ 2>/dev/null')
print(result.get('stdout', '') or 'Not found')

# 3. Check focus_server module location
print('\n' + '='*70)
print('3. FIND FOCUS_SERVER MODULE')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- find /home/prisma -name "focus_server*" -type f 2>/dev/null | head -20')
print(result.get('stdout', '') or 'Not found')

# 4. Check debug-codebase for focus_server
print('\n' + '='*70)
print('4. DEBUG-CODEBASE FOCUS_SERVER')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- ls -la /home/prisma/debug-codebase/pz/microservices/pzpy/focus_server/ 2>/dev/null')
print(result.get('stdout', '') or 'Not found')

ssh.disconnect()


