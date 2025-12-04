"""Check focus_manager configuration and base_path."""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

cm = ConfigManager()
ssh = SSHManager(cm)
ssh.connect()

pod = 'panda-panda-focus-server-7c767d7688-z6n5p'
fs_path = '/home/prisma/.local/lib/python3.10/site-packages/focus_server'

# 1. Check focus_manager initialization
print('='*70)
print('1. FOCUS_MANAGER INITIALIZATION')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -B 5 -A 50 "class FocusManager" {fs_path}/focus_manager.py 2>/dev/null | head -80')
print(result.get('stdout', '') or 'Not found')

# 2. Check get_recordings_in_time_range method
print('\n' + '='*70)
print('2. GET_RECORDINGS_IN_TIME_RANGE METHOD')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -B 3 -A 30 "def get_recordings_in_time_range" {fs_path}/focus_manager.py 2>/dev/null')
print(result.get('stdout', '') or 'Not found')

# 3. Check Config.Recording configuration
print('\n' + '='*70)
print('3. CONFIG RECORDING SETTINGS')
print('='*70)
pzpy_path = '/home/prisma/.local/lib/python3.10/site-packages/pzpy'
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -B 5 -A 20 "class Recording" {pzpy_path}/configuration.py 2>/dev/null')
print(result.get('stdout', '') or 'Not found')

# 4. Check actual configured base_path
print('\n' + '='*70)
print('4. CONFIGURED BASE_PATH IN CONFIG')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -r "recording_path\\|base_path\\|storage_path" {pzpy_path}/configuration.py 2>/dev/null')
print(result.get('stdout', '') or 'Not found')

# 5. Check default_config.py
print('\n' + '='*70)
print('5. DEFAULT_CONFIG.PY - RECORDING SETTINGS')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- cat /home/prisma/pz/config/py/..2025_12_01_13_02_15.3195021161/default_config.py 2>/dev/null | head -100')
print(result.get('stdout', '') or 'Not found')

# 6. Check environment variables for storage path
print('\n' + '='*70)
print('6. STORAGE RELATED ENV VARS')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- printenv | grep -i "storage\\|path\\|recording"')
print(result.get('stdout', '') or 'No matches')

ssh.disconnect()


