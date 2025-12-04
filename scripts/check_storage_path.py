"""Check the actual storage_path being used by Focus Server."""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

cm = ConfigManager()
ssh = SSHManager(cm)
ssh.connect()

pod = 'panda-panda-focus-server-7c767d7688-z6n5p'

# 1. Check Config.Focus settings
print('='*70)
print('1. CONFIG.FOCUS SETTINGS')
print('='*70)
pzpy_path = '/home/prisma/.local/lib/python3.10/site-packages/pzpy'
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -B 2 -A 30 "class Focus" {pzpy_path}/configuration.py 2>/dev/null')
print(result.get('stdout', '') or 'Not found')

# 2. Check storage_mount_path specifically
print('\n' + '='*70)
print('2. STORAGE_MOUNT_PATH')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -r "storage_mount_path" {pzpy_path}/ 2>/dev/null | head -10')
print(result.get('stdout', '') or 'Not found')

# 3. Check actual default_config for Focus settings
print('\n' + '='*70)
print('3. DEFAULT_CONFIG - FOCUS SETTINGS')
print('='*70)
config_path = '/home/prisma/pz/config/py/..2025_12_01_13_02_15.3195021161/default_config.py'
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- grep -A 30 "class Focus" {config_path} 2>/dev/null')
print(result.get('stdout', '') or 'Not found')

# 4. Get the full configuration.py file (Focus section)
print('\n' + '='*70)
print('4. FULL CONFIGURATION.PY')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- cat {pzpy_path}/configuration.py 2>/dev/null | head -200')
print(result.get('stdout', '') or 'Not found')

# 5. Check what MongoDB has for base_paths (we know from screenshots)
print('\n' + '='*70)
print('5. MONGODB BASE_PATHS (from screenshots)')
print('='*70)
print('GUID: 0d751218-ffd1-42cd-9281-42ee23ecab7a')
print('base_path: /prisma/root/recordings')
print('is_archive: false')
print('')
print('GUID: bf1a36b5-bbaa-469b-bb36-e890e4078fd7')
print('base_path: /prisma/root/recordings')
print('is_archive: false')
print('')
print('GUID: a2d8ae0b-e7a9-4f0a-8411-151456602836')
print('base_path: /prisma/root/recordings/segy')
print('is_archive: false')

ssh.disconnect()


