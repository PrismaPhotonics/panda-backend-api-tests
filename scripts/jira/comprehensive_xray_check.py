#!/usr/bin/env python3
"""
Comprehensive check for Xray Test Repository API access
"""

import requests
import yaml
import json
from pathlib import Path

# Load config
config_path = Path(__file__).parent.parent.parent / "config" / "jira_config.yaml"
config = yaml.safe_load(open(config_path))

base_url = config['jira']['base_url']
email = config['jira']['email']
api_token = config['jira']['api_token']
auth = (email, api_token)

print("=" * 80)
print("COMPREHENSIVE XRAY TEST REPOSITORY API CHECK")
print("=" * 80)

# 1. Check project capabilities
print("\n1. Checking project capabilities...")
try:
    url = f"{base_url}/rest/api/3/project/PZ"
    r = requests.get(url, auth=auth, timeout=10)
    if r.status_code == 200:
        project = r.json()
        print(f"   Project: {project.get('name')}")
        print(f"   Key: {project.get('key')}")
        # Check for Xray-related capabilities
        if 'properties' in project:
            print(f"   Properties: {project.get('properties')}")
except Exception as e:
    print(f"   Error: {e}")

# 2. Check available REST API endpoints
print("\n2. Checking available REST API endpoints...")
try:
    url = f"{base_url}/rest/api/3/application-properties"
    r = requests.get(url, auth=auth, timeout=10)
    if r.status_code == 200:
        props = r.json()
        xray_props = [p for p in props if 'xray' in str(p).lower() or 'test' in str(p).lower()]
        if xray_props:
            print(f"   Found Xray-related properties: {len(xray_props)}")
            for prop in xray_props[:5]:
                print(f"     {prop.get('key')}: {prop.get('value')}")
except Exception as e:
    print(f"   Error: {e}")

# 3. Try to get test issue with all fields
print("\n3. Checking test issue fields...")
try:
    url = f"{base_url}/rest/api/3/search"
    jql = "project = PZ AND type = Test AND key = PZ-14933"
    params = {
        'jql': jql,
        'fields': '*all',
        'expand': 'renderedFields,names,schema'
    }
    r = requests.get(url, auth=auth, params=params, timeout=10)
    if r.status_code == 200:
        data = r.json()
        issues = data.get('issues', [])
        if issues:
            issue = issues[0]
            fields = issue.get('fields', {})
            print(f"   Found test: {issue.get('key')}")
            # Look for folder-related fields
            folder_fields = {k: v for k, v in fields.items() if 'folder' in k.lower() or 'testrepository' in k.lower() or 'xray' in k.lower()}
            if folder_fields:
                print(f"   Found folder-related fields:")
                for k, v in folder_fields.items():
                    print(f"     {k}: {v}")
            else:
                print(f"   No folder-related fields found")
                print(f"   All field keys: {list(fields.keys())[:20]}")
except Exception as e:
    print(f"   Error: {e}")

# 4. Try all possible Xray endpoints
print("\n4. Trying all possible Xray endpoints...")
endpoints_to_try = [
    # Raven API (Xray Server/DC)
    f"{base_url}/rest/raven/1.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/raven/2.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/raven/1.0/api/testrepository/PZ",
    f"{base_url}/rest/raven/2.0/api/testrepository/PZ",
    
    # Alternative Raven paths
    f"{base_url}/rest/raven/1.0/api/testrepository/folders",
    f"{base_url}/rest/raven/2.0/api/testrepository/folders",
    
    # Jira API with testrepository
    f"{base_url}/rest/api/3/project/PZ/testrepository/folders",
    f"{base_url}/rest/api/2/project/PZ/testrepository/folders",
    f"{base_url}/rest/api/3/project/PZ/testrepository",
    f"{base_url}/rest/api/2/project/PZ/testrepository",
    
    # Xray plugin paths
    f"{base_url}/rest/xray/1.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/xray/2.0/api/testrepository/PZ/folders",
    
    # Direct folder access with base folder ID
    f"{base_url}/rest/raven/1.0/api/testrepository/PZ/folders/68d91b9f681e183ea2e83e16",
    f"{base_url}/rest/raven/2.0/api/testrepository/PZ/folders/68d91b9f681e183ea2e83e16",
]

success_endpoints = []
for endpoint in endpoints_to_try:
    try:
        r = requests.get(endpoint, auth=auth, timeout=10)
        if r.status_code == 200:
            print(f"   SUCCESS: {endpoint}")
            try:
                data = r.json()
                print(f"     Response: {json.dumps(data, indent=2)[:300]}")
            except:
                print(f"     Response (text): {r.text[:300]}")
            success_endpoints.append(endpoint)
        elif r.status_code not in [404, 401, 403]:
            print(f"   {endpoint}: {r.status_code}")
    except Exception as e:
        pass

if not success_endpoints:
    print("   No working endpoints found")

# 5. Try to find folder info via issue links or custom fields
print("\n5. Checking for folder info in custom fields...")
try:
    # Get all custom fields
    url = f"{base_url}/rest/api/3/field"
    r = requests.get(url, auth=auth, timeout=10)
    if r.status_code == 200:
        fields = r.json()
        folder_fields = [f for f in fields if 'folder' in str(f).lower() or 'testrepository' in str(f).lower() or 'xray' in str(f).lower()]
        if folder_fields:
            print(f"   Found folder-related custom fields:")
            for field in folder_fields[:10]:
                print(f"     {field.get('id')}: {field.get('name')}")
        else:
            print(f"   No folder-related custom fields found")
except Exception as e:
    print(f"   Error: {e}")

# 6. Try GraphQL API
print("\n6. Trying Jira GraphQL API...")
try:
    url = f"{base_url}/gateway/api/graphql"
    query = """
    query {
        __schema {
            types {
                name
            }
        }
    }
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    r = requests.post(url, json={"query": query}, headers=headers, auth=auth, timeout=10)
    if r.status_code == 200:
        data = r.json()
        if 'data' in data:
            types = data['data'].get('__schema', {}).get('types', [])
            xray_types = [t for t in types if 'xray' in str(t).lower() or 'test' in str(t).lower() or 'folder' in str(t).lower()]
            if xray_types:
                print(f"   Found Xray-related types:")
                for t in xray_types[:10]:
                    print(f"     {t.get('name')}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 80)
if success_endpoints:
    print(f"FOUND {len(success_endpoints)} WORKING ENDPOINT(S)!")
    for ep in success_endpoints:
        print(f"  - {ep}")
else:
    print("NO WORKING ENDPOINTS FOUND")
    print("Xray Test Repository API is not available via REST API")
    print("You need to find folder IDs manually via UI")
print("=" * 80)

