"""
Check how Focus Server's RecordingMongoMapper uses base_paths and GUID
"""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

cm = ConfigManager()
ssh = SSHManager(cm)
ssh.connect()

print('='*70)
print('בודק איך Focus Server משתמש ב-base_paths ו-GUID')
print('='*70)
print()

# Check RecordingMongoMapper initialization
cmd = """python3 -c "
import sys
sys.path.insert(0, '/home/prisma/.local/lib/python3.10/site-packages')
try:
    from pzpy.focus_server.recording_mongo_mapper import RecordingMongoMapper
    import inspect
    print('=== RecordingMongoMapper.__init__ ===')
    source = inspect.getsource(RecordingMongoMapper.__init__)
    print(source)
    print()
    print('=== RecordingMongoMapper class methods ===')
    for name, method in inspect.getmembers(RecordingMongoMapper, predicate=inspect.isfunction):
        if not name.startswith('_'):
            print(f'{name}:')
            print(inspect.getsource(method))
            print()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
" """

result = ssh.execute_command(f'kubectl exec -n panda deployment/panda-panda-focus-server -- bash -c {cmd}')
print(result.get('stdout', '') or 'No output')
print(result.get('stderr', '') or '')

ssh.disconnect()

