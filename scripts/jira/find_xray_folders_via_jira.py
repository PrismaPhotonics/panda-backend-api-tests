#!/usr/bin/env python3
"""
Find Xray folders via Jira API
Tries multiple approaches to find folder IDs
"""

import requests
import yaml
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load config
config_path = project_root / "config" / "jira_config.yaml"
config = yaml.safe_load(open(config_path))

base_url = config['jira']['base_url']
email = config['jira']['email']
api_token = config['jira']['api_token']
auth = (email, api_token)

print("=" * 80)
print("SEARCHING FOR XRAY FOLDERS VIA JIRA API")
print("=" * 80)

# Try to get project metadata
print("\n1. Trying to get project metadata...")
try:
    url = f"{base_url}/rest/api/3/project/PZ"
    r = requests.get(url, auth=auth, timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        project_data = r.json()
        print(f"   Project: {project_data.get('name')}")
        print(f"   Key: {project_data.get('key')}")
except Exception as e:
    print(f"   Error: {e}")

# Try to search for tests and see if they have folder information
print("\n2. Trying to get test issues...")
try:
    url = f"{base_url}/rest/api/3/search"
    jql = "project = PZ AND type = Test AND key IN (PZ-14933, PZ-14934)"
    params = {
        'jql': jql,
        'fields': 'id,key,summary,status,customfield_*',
        'expand': 'renderedFields,names,schema'
    }
    r = requests.get(url, auth=auth, params=params, timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        issues = data.get('issues', [])
        print(f"   Found {len(issues)} tests")
        if issues:
            # Check for custom fields that might contain folder info
            issue = issues[0]
            fields = issue.get('fields', {})
            print(f"   Fields: {list(fields.keys())[:10]}...")
            # Look for folder-related fields
            for key, value in fields.items():
                if 'folder' in key.lower() or 'testrepository' in key.lower():
                    print(f"   Found folder-related field: {key} = {value}")
except Exception as e:
    print(f"   Error: {e}")

# Try GraphQL API
print("\n3. Trying Jira GraphQL API...")
try:
    url = f"{base_url}/gateway/api/graphql"
    query = """
    query {
        project(key: "PZ") {
            id
            key
            name
        }
    }
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {requests.auth._basic_auth_str(email, api_token)}"
    }
    r = requests.post(url, json={"query": query}, headers=headers, auth=auth, timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Response: {json.dumps(data, indent=2)[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Try Xray-specific endpoints
print("\n4. Trying Xray-specific endpoints...")
endpoints = [
    f"{base_url}/rest/raven/1.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/raven/2.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/api/3/project/PZ/testrepository/folders",
    f"{base_url}/rest/api/2/project/PZ/testrepository/folders",
]

for endpoint in endpoints:
    try:
        r = requests.get(endpoint, auth=auth, timeout=10)
        print(f"   {endpoint}")
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   SUCCESS! Found data: {str(data)[:200]}")
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
print("SUMMARY")
print("=" * 80)
print("If no folders were found via API, you need to:")
print("1. Open Xray Test Repository in browser")
print("2. Use DevTools (F12) > Network tab")
print("3. Click on each folder")
print("4. Find folder ID in API response or URL")
print("5. Run: py scripts/jira/assign_alerts_via_jira_api.py --folder-ids <ids>")
print("=" * 80)

