#!/usr/bin/env python3
"""
Deep check for Xray Test Repository API - trying all possible approaches
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
print("DEEP XRAY API CHECK - ALL POSSIBLE APPROACHES")
print("=" * 80)

success_endpoints = []

# 1. Try Atlassian Connect API with Xray addon
print("\n1. Trying Atlassian Connect API with Xray addon...")
try:
    # Get addon info
    url = f"{base_url}/rest/atlassian-connect/1/addons/com.xpandit.plugins.xray"
    r = requests.get(url, auth=auth, timeout=10)
    if r.status_code == 200:
        addon = r.json()
        print(f"   Xray addon found: {addon.get('name')} v{addon.get('version')}")
        
        # Try to access addon modules
        modules_url = f"{base_url}/rest/atlassian-connect/1/addons/com.xpandit.plugins.xray/modules"
        r_modules = requests.get(modules_url, auth=auth, timeout=10)
        if r_modules.status_code == 200:
            modules = r_modules.json()
            print(f"   Found modules: {list(modules.keys())[:10]}")
except Exception as e:
    print(f"   Error: {e}")

# 2. Try Xray-specific REST endpoints with different versions
print("\n2. Trying Xray REST endpoints with different versions...")
xray_endpoints = [
    # Raven API v1
    f"{base_url}/rest/raven/1.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/raven/1.0/api/testrepository/PZ/folders/68d91b9f681e183ea2e83e16",
    f"{base_url}/rest/raven/1.0/api/testrepository/PZ/folders/68d91b9f681e183ea2e83e16/children",
    f"{base_url}/rest/raven/1.0/api/testrepository/PZ/folders/68d91b9f681e183ea2e83e16/tests",
    
    # Raven API v2
    f"{base_url}/rest/raven/2.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/raven/2.0/api/testrepository/PZ/folders/68d91b9f681e183ea2e83e16",
    f"{base_url}/rest/raven/2.0/api/testrepository/PZ/folders/68d91b9f681e183ea2e83e16/children",
    f"{base_url}/rest/raven/2.0/api/testrepository/PZ/folders/68d91b9f681e183ea2e83e16/tests",
    
    # Alternative paths
    f"{base_url}/rest/api/raven/1.0/testrepository/PZ/folders",
    f"{base_url}/rest/api/raven/2.0/testrepository/PZ/folders",
]

for endpoint in xray_endpoints:
    try:
        r = requests.get(endpoint, auth=auth, timeout=10)
        if r.status_code == 200:
            print(f"   SUCCESS: {endpoint}")
            try:
                data = r.json()
                print(f"     Response: {json.dumps(data, indent=2)[:400]}")
            except:
                print(f"     Response (text): {r.text[:400]}")
            success_endpoints.append(endpoint)
        elif r.status_code == 401:
            print(f"   AUTH: {endpoint}")
        elif r.status_code == 403:
            print(f"   PERM: {endpoint}")
    except:
        pass

# 3. Try Jira API v3 with testrepository
print("\n3. Trying Jira API v3 with testrepository...")
jira_endpoints = [
    f"{base_url}/rest/api/3/project/PZ/testrepository",
    f"{base_url}/rest/api/3/project/PZ/testrepository/folders",
    f"{base_url}/rest/api/3/project/PZ/testrepository/folders/68d91b9f681e183ea2e83e16",
    f"{base_url}/rest/api/3/testrepository/PZ/folders",
]

for endpoint in jira_endpoints:
    try:
        r = requests.get(endpoint, auth=auth, timeout=10)
        if r.status_code == 200:
            print(f"   SUCCESS: {endpoint}")
            try:
                data = r.json()
                print(f"     Response: {json.dumps(data, indent=2)[:400]}")
            except:
                print(f"     Response (text): {r.text[:400]}")
            success_endpoints.append(endpoint)
    except:
        pass

# 4. Try GraphQL with Xray-specific queries
print("\n4. Trying GraphQL API with Xray queries...")
try:
    url = f"{base_url}/gateway/api/graphql"
    
    # Try different GraphQL queries
    queries = [
        # Query 1: Try to find Xray types
        """
        query {
            __type(name: "XrayTestRepository") {
                name
                fields {
                    name
                    type {
                        name
                    }
                }
            }
        }
        """,
        # Query 2: Try to query project with Xray
        """
        query {
            project(key: "PZ") {
                id
                key
                name
            }
        }
        """,
    ]
    
    for query in queries:
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            r = requests.post(url, json={"query": query}, headers=headers, auth=auth, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if 'data' in data and data['data']:
                    print(f"   GraphQL SUCCESS")
                    print(f"     Response: {json.dumps(data, indent=2)[:400]}")
                    success_endpoints.append(f"{url} (GraphQL)")
        except:
            pass
except Exception as e:
    print(f"   Error: {e}")

# 5. Try to assign test to folder directly
print("\n5. Trying to assign test to folder directly...")
try:
    # Try PUT request to assign test to folder
    test_key = "PZ-14933"
    folder_id = "68d91b9f681e183ea2e83e16"
    
    assign_endpoints = [
        f"{base_url}/rest/raven/1.0/api/testrepository/PZ/folders/{folder_id}/tests/{test_key}",
        f"{base_url}/rest/raven/2.0/api/testrepository/PZ/folders/{folder_id}/tests/{test_key}",
        f"{base_url}/rest/api/3/project/PZ/testrepository/folders/{folder_id}/tests/{test_key}",
    ]
    
    for endpoint in assign_endpoints:
        try:
            # Try GET first to see if it exists
            r = requests.get(endpoint, auth=auth, timeout=10)
            if r.status_code == 200:
                print(f"   SUCCESS (GET): {endpoint}")
                success_endpoints.append(endpoint)
            elif r.status_code == 404:
                # Try PUT to assign
                r_put = requests.put(endpoint, auth=auth, timeout=10)
                if r_put.status_code in [200, 201, 204]:
                    print(f"   SUCCESS (PUT): {endpoint}")
                    success_endpoints.append(endpoint)
        except:
            pass
except Exception as e:
    print(f"   Error: {e}")

# 6. Try to get folder structure via issue search
print("\n6. Trying to get folder info via issue search...")
try:
    url = f"{base_url}/rest/api/3/search"
    jql = "project = PZ AND type = Test AND key = PZ-14933"
    params = {
        'jql': jql,
        'fields': '*all',
        'expand': 'renderedFields,names,schema,operations'
    }
    r = requests.get(url, auth=auth, params=params, timeout=10)
    if r.status_code == 200:
        data = r.json()
        issues = data.get('issues', [])
        if issues:
            issue = issues[0]
            # Look for any folder-related information
            all_data = json.dumps(issue, indent=2)
            if 'folder' in all_data.lower() or 'testrepository' in all_data.lower():
                print(f"   Found folder-related info in issue")
                print(f"     {all_data[:500]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 80)
if success_endpoints:
    print(f"FOUND {len(success_endpoints)} WORKING ENDPOINT(S)!")
    for ep in success_endpoints:
        print(f"  [OK] {ep}")
else:
    print("NO WORKING ENDPOINTS FOUND")
    print("\nFINAL CONCLUSION:")
    print("Xray Test Repository API is NOT available via REST API")
    print("This is a limitation of Xray Cloud - folders can only be managed via UI")
    print("\nSOLUTION:")
    print("1. Find folder IDs manually via browser DevTools")
    print("2. Use the script: py scripts/jira/assign_alerts_via_jira_api.py --folder-ids <ids>")
    print("3. Or add tests manually via UI")
print("=" * 80)

