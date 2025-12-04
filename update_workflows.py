import requests
import os
import base64
import re

# GitHub API configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
REPO_OWNER = 'PrismaPhotonics'
REPO_NAME = 'panda-backend-api-tests'
BRANCH = 'chore/add-roy-tests'

# Files to update
workflow_files = [
    '.github/workflows/load-quick.yml',
    '.github/workflows/load-live-job.yml',
    '.github/workflows/load-performance.yml',
    '.github/workflows/panda-tests.yml',
    '.github/workflows/smoke-tests.yml',
    '.github/workflows/load-job-tests.yml',
]

headers = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

def get_file(path):
    """Get file content and SHA from GitHub."""
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}?ref={BRANCH}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        return content, data['sha']
    else:
        print(f'Error getting {path}: {response.status_code}')
        print(response.text)
        return None, None

def update_file(path, content, sha, message):
    """Update file content on GitHub."""
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}'
    data = {
        'message': message,
        'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
        'sha': sha,
        'branch': BRANCH,
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        return True
    else:
        print(f'Error updating {path}: {response.status_code}')
        print(response.text)
        return False

def replace_production_with_kefar_saba(content):
    """Replace all production references with kefar_saba."""
    # Replace various patterns
    replacements = [
        # Default values in inputs
        ('default: "production"', 'default: "kefar_saba"'),
        ("default: 'production'", "default: 'kefar_saba'"),
        
        # Fallback values with ||
        ("|| 'production'", "|| 'kefar_saba'"),
        ('|| "production"', '|| "kefar_saba"'),
        
        # PowerShell variable assignments
        ('$targetEnv = "production"', '$targetEnv = "kefar_saba"'),
        ("$targetEnv = 'production'", "$targetEnv = 'kefar_saba'"),
        
        # TARGET_ENVIRONMENT fallbacks
        ("TARGET_ENVIRONMENT: ${{ inputs.environment || 'production' }}", "TARGET_ENVIRONMENT: ${{ inputs.environment || 'kefar_saba' }}"),
    ]
    
    new_content = content
    changes = []
    
    for old, new in replacements:
        if old in new_content:
            new_content = new_content.replace(old, new)
            changes.append(f'  - {old} → {new}')
    
    return new_content, changes

if not GITHUB_TOKEN:
    print('ERROR: GITHUB_TOKEN not found in environment')
    exit(1)

print(f'Updating workflows in {REPO_OWNER}/{REPO_NAME} (branch: {BRANCH})')
print('=' * 60)

for path in workflow_files:
    print(f'\n📄 Processing: {path}')
    
    # Get current content
    content, sha = get_file(path)
    if content is None:
        print(f'   ❌ Failed to get file')
        continue
    
    # Replace production with kefar_saba
    new_content, changes = replace_production_with_kefar_saba(content)
    
    if not changes:
        print(f'   ⏭️  No production references found')
        continue
    
    print(f'   Found {len(changes)} replacement(s):')
    for change in changes:
        print(change)
    
    # Update file
    success = update_file(path, new_content, sha, f'chore: update environment from production to kefar_saba')
    if success:
        print(f'   ✅ Updated successfully')
    else:
        print(f'   ❌ Update failed')

print('\n' + '=' * 60)
print('Done!')

