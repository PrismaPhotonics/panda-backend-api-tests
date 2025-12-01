"""Check recording_indexer.py implementation."""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

cm = ConfigManager()
ssh = SSHManager(cm)
ssh.connect()

pod = 'panda-panda-focus-server-7c767d7688-z6n5p'
pzpy_path = '/home/prisma/.local/lib/python3.10/site-packages/pzpy'

# 1. Get recording_indexer.py content
print('='*70)
print('1. RECORDING_INDEXER.PY CONTENT')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- cat {pzpy_path}/recording/recording_indexer.py 2>/dev/null')
print(result.get('stdout', '') or 'File not found')

# 2. Check focus_server.py - recordings_in_time_range handler
print('\n' + '='*70)
print('2. FOCUS_SERVER.PY - RECORDINGS HANDLER')
print('='*70)
fs_path = '/home/prisma/.local/lib/python3.10/site-packages/focus_server'
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -B 5 -A 40 "recordings_in_time" {fs_path}/focus_server.py 2>/dev/null')
print(result.get('stdout', '') or 'Not found')

# 3. Check base_path configuration
print('\n' + '='*70)
print('3. CONFIG - BASE_PATH')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -r "base_path\\|BASE_PATH" /home/prisma/pz/config/ 2>/dev/null')
print(result.get('stdout', '') or 'Not found')

ssh.disconnect()


