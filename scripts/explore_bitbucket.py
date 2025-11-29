"""
Script to explore Bitbucket repository and find proto files
"""
import requests
import os

workspace = 'prismaphotonics'
repo = 'pz'

# Get auth from environment
bb_user = os.environ.get('BITBUCKET_USERNAME', '')
bb_pass = os.environ.get('BITBUCKET_APP_PASSWORD', '')
auth = (bb_user, bb_pass) if bb_user and bb_pass else None

def list_dir(path=''):
    """List directory contents"""
    url = f'https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/src/master/{path}?pagelen=100'
    try:
        resp = requests.get(url, auth=auth, timeout=30)
        if resp.status_code == 200:
            return resp.json().get('values', [])
        else:
            print(f'  Error {resp.status_code}: {resp.text[:100]}')
            return []
    except Exception as e:
        print(f'  Exception: {e}')
        return []

def search_proto(path='', depth=0, max_depth=3):
    """Recursively search for .proto files"""
    if depth > max_depth:
        return []
    
    found = []
    items = list_dir(path)
    
    for item in items:
        item_path = item.get('path', '')
        item_type = item.get('type', '')
        
        # Check if it's a proto file
        if item_path.endswith('.proto'):
            found.append(item_path)
            print(f'  FOUND: {item_path}')
        
        # Check for grpc/proto directories
        if item_type == 'commit_directory':
            name = item_path.split('/')[-1].lower()
            if any(x in name for x in ['grpc', 'proto', 'rpc', 'service']):
                print(f'  Exploring: {item_path}/')
                found.extend(search_proto(item_path, depth + 1, max_depth))
    
    return found

print('=== Exploring Bitbucket pz repository ===')
print(f'Auth: {"configured" if auth else "not configured"}')
print()

# First list root directory
print('Root directory:')
root_items = list_dir('')
for item in root_items[:20]:
    print(f"  {item.get('type', '?')[:3]}: {item.get('path', '?')}")

# Search for common proto locations
common_paths = [
    'proto',
    'protos', 
    'api/proto',
    'grpc',
    'src/proto',
    'panda/proto',
    'pzlinux/proto',
    'services/grpc',
]

print('\nSearching common proto paths:')
for path in common_paths:
    print(f'\nChecking {path}/:')
    items = list_dir(path)
    for item in items[:10]:
        p = item.get('path', '')
        if p.endswith('.proto'):
            print(f'  PROTO: {p}')
        else:
            print(f"  {item.get('type', '?')[:3]}: {p}")

