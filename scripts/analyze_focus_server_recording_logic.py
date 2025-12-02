"""
Analyze Focus Server logic for finding recordings in MongoDB.

This script checks:
1. How Focus Server finds GUID from base_paths
2. What storage_mount_path is configured
3. How RecordingMongoMapper queries MongoDB
4. The actual code that searches for recordings
"""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager
import pymongo
from datetime import datetime

cm = ConfigManager()
ssh = SSHManager(cm)
ssh.connect()

print('='*80)
print('ANALYZING FOCUS SERVER RECORDING LOGIC')
print('='*80)
print()

# Get pod name
print('1. Finding Focus Server pod...')
print('-'*80)
result = ssh.execute_command('kubectl get pods -n panda -l app=panda-panda-focus-server -o jsonpath="{.items[0].metadata.name}"')
pod_name = result.get('stdout', '').strip()
if not pod_name:
    print('❌ Could not find Focus Server pod')
    sys.exit(1)
print(f'✅ Found pod: {pod_name}')
print()

# Check storage_mount_path configuration
print('2. Checking storage_mount_path configuration...')
print('-'*80)
cmd1 = """python3 -c "
import sys
sys.path.insert(0, '/home/prisma/.local/lib/python3.10/site-packages')
try:
    from pzpy.focus_server.default_config import Config
    print(f'storage_mount_path = {Config.Focus.storage_mount_path}')
except Exception as e:
    print(f'Error loading config: {e}')
" """
result1 = ssh.execute_command(f'kubectl exec -n panda {pod_name} -- bash -c "{cmd1}"')
storage_mount_path = result1.get('stdout', '').strip()
print(f'✅ {storage_mount_path}')
print()

# Check MongoDB base_paths
print('3. Checking MongoDB base_paths...')
print('-'*80)
mongo_config = cm.get_database_config()
try:
    client = pymongo.MongoClient(
        host=mongo_config['host'],
        port=mongo_config['port'],
        username=mongo_config['username'],
        password=mongo_config['password'],
        authSource=mongo_config.get('auth_source', 'prisma'),
        serverSelectionTimeoutMS=5000
    )
    db = client[mongo_config.get('database', 'prisma')]
    base_paths = db['base_paths']
    
    print('base_paths in MongoDB:')
    for doc in base_paths.find():
        base_path_val = doc.get('base_path', 'N/A')
        guid_val = doc.get('guid', 'N/A')
        is_archive = doc.get('is_archive', False)
        print(f'  - base_path: {base_path_val}')
        print(f'    guid: {guid_val}')
        print(f'    is_archive: {is_archive}')
        print()
    
    client.close()
except Exception as e:
    print(f'❌ Error connecting to MongoDB: {e}')
print()

# Check RecordingMongoMapper source code
print('4. Analyzing RecordingMongoMapper source code...')
print('-'*80)
cmd2 = """python3 -c "
import sys
sys.path.insert(0, '/home/prisma/.local/lib/python3.10/site-packages')
import inspect
import os

try:
    # Try to import RecordingMongoMapper
    from pzpy.focus_server.recording_mongo_mapper import RecordingMongoMapper
    
    print('=== RecordingMongoMapper.__init__ ===')
    try:
        init_source = inspect.getsource(RecordingMongoMapper.__init__)
        print(init_source)
    except Exception as e:
        print(f'Could not get __init__ source: {e}')
    
    print()
    print('=== All methods in RecordingMongoMapper ===')
    for name, method in inspect.getmembers(RecordingMongoMapper, predicate=inspect.ismethod):
        if not name.startswith('_'):
            print(f'  - {name}')
    
    # Try to find methods that query base_paths
    print()
    print('=== Methods that might query base_paths ===')
    for name, method in inspect.getmembers(RecordingMongoMapper, predicate=inspect.ismethod):
        if 'base_path' in name.lower() or 'guid' in name.lower() or 'collection' in name.lower():
            print(f'=== {name} ===')
            try:
                print(inspect.getsource(method))
            except Exception as e:
                print(f'Could not get source: {e}')
            print()
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
" """
result2 = ssh.execute_command(f'kubectl exec -n panda {pod_name} -- bash -c "{cmd2}"')
print(result2.get('stdout', '') or 'No output')
if result2.get('stderr'):
    print('STDERR:', result2.get('stderr'))
print()

# Check focus_manager.py for how it uses RecordingMongoMapper
print('5. Checking focus_manager.py for recording search logic...')
print('-'*80)
fs_path = '/home/prisma/.local/lib/python3.10/site-packages/focus_server'
cmd3 = f'kubectl exec -n panda {pod_name} -- grep -B 5 -A 30 "def.*recording.*time.*range\\|def.*find.*recording\\|def.*get.*recording" {fs_path}/focus_manager.py 2>/dev/null | head -100'
result3 = ssh.execute_command(cmd3)
print(result3.get('stdout', '') or 'Not found')
print()

# Check how configure endpoint uses recordings
print('6. Checking configure endpoint logic...')
print('-'*80)
cmd4 = f'kubectl exec -n panda {pod_name} -- grep -B 10 -A 50 "def configure\\|No recording found" {fs_path}/focus_manager.py 2>/dev/null | head -150'
result4 = ssh.execute_command(cmd4)
print(result4.get('stdout', '') or 'Not found')
print()

# Summary
print('='*80)
print('SUMMARY')
print('='*80)
print(f'1. storage_mount_path configured: {storage_mount_path}')
print('2. MongoDB base_paths:')
print('   - /prisma/root/recordings → GUID: 25b4875f-5785-4b24-8895-121039474bcd (✅ Has recordings)')
print('   - /prisma/root/recordings/segy → GUID: 873ea296-a3a3-4c22-a880-608766f004cd (❌ Empty)')
print()
if storage_mount_path and '/segy' in storage_mount_path:
    print('❌ PROBLEM IDENTIFIED:')
    print(f'   Focus Server is configured with storage_mount_path = {storage_mount_path}')
    print('   This likely causes it to search for base_path = "/prisma/root/recordings/segy"')
    print('   But recordings are in base_path = "/prisma/root/recordings"')
    print()
    print('✅ SOLUTION:')
    print('   Focus Server should search for base_path = "/prisma/root/recordings"')
    print('   regardless of storage_mount_path value')
else:
    print('✅ Configuration looks correct')
print()

ssh.disconnect()

