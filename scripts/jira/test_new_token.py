#!/usr/bin/env python3
"""
Test new Jira API token
"""

import requests
import yaml
from pathlib import Path

# Load config
config_path = Path(__file__).parent.parent.parent / "config" / "jira_config.yaml"
config = yaml.safe_load(open(config_path))

base_url = config['jira']['base_url']
email = config['jira']['email']

# New token provided by user
new_token = "${ATLASSIAN_API_TOKEN}"

print("Testing new Jira API token...")
print("=" * 80)

# Test with new token
auth = (email, new_token)

# Test 1: Basic project access
print("\n1. Testing basic project access...")
try:
    url = f"{base_url}/rest/api/3/project/PZ"
    r = requests.get(url, auth=auth, timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        project_data = r.json()
        print(f"   SUCCESS! Project: {project_data.get('name')}")
    else:
        print(f"   Error: {r.text[:200]}")
except Exception as e:
    print(f"   Exception: {e}")

# Test 2: Try Xray endpoints
print("\n2. Testing Xray API endpoints...")
endpoints = [
    f"{base_url}/rest/raven/1.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/raven/2.0/api/testrepository/PZ/folders",
]

for endpoint in endpoints:
    try:
        r = requests.get(endpoint, auth=auth, timeout=10)
        print(f"   {endpoint}")
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   SUCCESS! Found folders!")
            print(f"   Response type: {type(data)}")
            if isinstance(data, list):
                print(f"   Found {len(data)} folders")
                if data:
                    print(f"   First folder: {str(data[0])[:200]}")
            elif isinstance(data, dict):
                print(f"   Keys: {list(data.keys())}")
                print(f"   Data: {str(data)[:300]}")
            break
        elif r.status_code == 401:
            print(f"   Authentication failed")
        elif r.status_code == 403:
            print(f"   Permission denied")
        elif r.status_code == 404:
            print(f"   Not found")
        else:
            print(f"   Error: {r.text[:100]}")
    except Exception as e:
        print(f"   Exception: {e}")

print("\n" + "=" * 80)

