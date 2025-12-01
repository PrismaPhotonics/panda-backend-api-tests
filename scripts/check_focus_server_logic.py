"""
Check how Focus Server should find the GUID from base_paths
"""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

cm = ConfigManager()
ssh = SSHManager(cm)
ssh.connect()

print('='*70)
print('בודק איך Focus Server אמור למצוא GUID מ-base_paths')
print('='*70)
print()

# Check what storage_mount_path is configured
print('1. מה ה-storage_mount_path מוגדר ב-Focus Server?')
print('-'*70)
cmd = """python3 -c "
import sys
sys.path.insert(0, '/home/prisma/.local/lib/python3.10/site-packages')
try:
    from pzpy.focus_server.default_config import Config
    print(f'storage_mount_path = {Config.Focus.storage_mount_path}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
" """
result = ssh.execute_command(f'kubectl exec -n panda deployment/panda-panda-focus-server -- bash -c "{cmd}"')
print(result.get('stdout', '') or 'No output')
print()

# Check how RecordingMongoMapper uses base_paths
print('2. איך RecordingMongoMapper משתמש ב-base_paths?')
print('-'*70)
cmd2 = """python3 -c "
import sys
sys.path.insert(0, '/home/prisma/.local/lib/python3.10/site-packages')
try:
    from pzpy.focus_server.recording_mongo_mapper import RecordingMongoMapper
    import inspect
    
    # Get the source code of key methods
    print('=== __init__ ===')
    print(inspect.getsource(RecordingMongoMapper.__init__))
    print()
    
    # Try to find methods that query base_paths
    for name, method in inspect.getmembers(RecordingMongoMapper, predicate=inspect.isfunction):
        if 'base_path' in name.lower() or 'guid' in name.lower() or 'collection' in name.lower():
            print(f'=== {name} ===')
            print(inspect.getsource(method))
            print()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
" """
result2 = ssh.execute_command(f'kubectl exec -n panda deployment/panda-panda-focus-server -- bash -c "{cmd2}"')
print(result2.get('stdout', '') or 'No output')
print(result2.get('stderr', '') or '')

ssh.disconnect()

