#!/usr/bin/env python3
"""
Try Xray UI API endpoints
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
print("TRYING XRAY UI API ENDPOINTS")
print("=" * 80)

# Try Xray UI/Connect API endpoints
endpoints_to_try = [
    # Xray Connect API (for apps)
    f"{base_url}/rest/atlassian-connect/1/app/xray",
    
    # Try to access test repository via UI API
    f"{base_url}/rest/api/3/project/PZ/components",
    
    # Try Xray-specific UI endpoints
    f"{base_url}/plugins/servlet/xray/testrepository/PZ/folders",
    f"{base_url}/plugins/servlet/xray/testrepository/folders",
    
    # Try with base folder ID
    f"{base_url}/plugins/servlet/xray/testrepository/PZ/folders/68d91b9f681e183ea2e83e16",
    
    # Try different plugin paths
    f"{base_url}/rest/xpandit/xray/1.0/testrepository/PZ/folders",
    f"{base_url}/rest/xpandit/xray/2.0/testrepository/PZ/folders",
    
    # Try Atlassian Connect endpoints
    f"{base_url}/rest/atlassian-connect/1/addons/com.xpandit.plugins.xray",
]

success_endpoints = []
for endpoint in endpoints_to_try:
    try:
        r = requests.get(endpoint, auth=auth, timeout=10)
        if r.status_code == 200:
            print(f"\nSUCCESS: {endpoint}")
            try:
                data = r.json()
                print(f"Response: {json.dumps(data, indent=2)[:500]}")
            except:
                print(f"Response (text): {r.text[:500]}")
            success_endpoints.append(endpoint)
        elif r.status_code == 401:
            print(f"AUTH FAILED: {endpoint}")
        elif r.status_code == 403:
            print(f"PERMISSION DENIED: {endpoint}")
        elif r.status_code == 404:
            pass  # Silent for 404
        else:
            print(f"OTHER ({r.status_code}): {endpoint}")
    except Exception as e:
        pass  # Silent for exceptions

# Try POST requests to see if we need to create folders
print("\n" + "=" * 80)
print("TRYING TO CREATE/ACCESS FOLDERS VIA POST")
print("=" * 80)

post_endpoints = [
    f"{base_url}/rest/raven/1.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/api/3/project/PZ/testrepository/folders",
]

for endpoint in post_endpoints:
    try:
        # Try to get folder info via POST
        payload = {"folderId": "68d91b9f681e183ea2e83e16"}
        r = requests.post(endpoint, json=payload, auth=auth, timeout=10)
        if r.status_code in [200, 201]:
            print(f"\nSUCCESS (POST): {endpoint}")
            try:
                data = r.json()
                print(f"Response: {json.dumps(data, indent=2)[:500]}")
            except:
                print(f"Response (text): {r.text[:500]}")
            success_endpoints.append(endpoint)
    except Exception as e:
        pass

print("\n" + "=" * 80)
if success_endpoints:
    print(f"FOUND {len(success_endpoints)} WORKING ENDPOINT(S)!")
    for ep in success_endpoints:
        print(f"  - {ep}")
else:
    print("NO WORKING ENDPOINTS FOUND")
    print("\nCONCLUSION:")
    print("Xray Test Repository API is not available via REST API")
    print("You need to:")
    print("1. Open Xray Test Repository in browser")
    print("2. Use DevTools (F12) > Network tab")
    print("3. Click on folders to find folder IDs")
    print("4. Use the script with --folder-ids parameter")
print("=" * 80)

