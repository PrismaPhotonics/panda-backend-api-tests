import requests
import os

# GitHub API configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
REPO_OWNER = 'PrismaPhotonics'
REPO_NAME = 'panda-backend-api-tests'
ENVIRONMENT_NAME = 'kefar_saba'

# Variables to add
variables = [
    ('ENVIRONMENT_NAME', 'kefar_saba'),
    ('FOCUS_API_PREFIX', '/focus-server'),
    ('FOCUS_SERVER_HOST', '10.10.100.100'),
    ('K8S_NAMESPACE', 'panda'),
    ('MONGODB_HOST', '10.10.100.108'),
    ('MONGODB_PORT', '27017'),
    ('MONGODB_USERNAME', 'prisma'),
    ('RABBITMQ_HOST', '10.10.100.107'),
    ('RABBITMQ_PORT', '5672'),
    ('RABBITMQ_USERNAME', 'prisma'),
    ('SITE_ID', 'prisma-210-1000'),
    ('SSH_JUMP_HOST', '10.10.100.3'),
    ('SSH_JUMP_USER', 'root'),
    ('SSH_TARGET_HOST', '10.10.100.113'),
    ('SSH_TARGET_USER', 'prisma'),
]

if not GITHUB_TOKEN:
    print('ERROR: GITHUB_TOKEN not found in environment')
    print('Please set GITHUB_TOKEN environment variable')
    exit(1)

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

base_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/environments/{ENVIRONMENT_NAME}/variables'

print(f'Adding variables to environment: {ENVIRONMENT_NAME}')
print('=' * 50)

success_count = 0
for name, value in variables:
    data = {'name': name, 'value': value}
    response = requests.post(base_url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f'✓ Added: {name} = {value}')
        success_count += 1
    elif response.status_code == 409:
        # Variable already exists, try to update it
        update_url = f'{base_url}/{name}'
        response = requests.patch(update_url, headers=headers, json={'value': value})
        if response.status_code == 204:
            print(f'✓ Updated: {name} = {value}')
            success_count += 1
        else:
            print(f'✗ Failed to update {name}: {response.status_code} - {response.text}')
    else:
        print(f'✗ Failed: {name} - {response.status_code} - {response.text}')

print('=' * 50)
print(f'Done! {success_count}/{len(variables)} variables added successfully.')

