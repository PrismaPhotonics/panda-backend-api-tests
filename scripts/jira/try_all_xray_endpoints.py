#!/usr/bin/env python3
"""
Try all possible Xray API endpoints
"""

import requests
import yaml
from pathlib import Path

# Load config
config_path = Path(__file__).parent.parent.parent / "config" / "jira_config.yaml"
config = yaml.safe_load(open(config_path))

base_url = config['jira']['base_url']
email = config['jira']['email']
api_token = config['jira']['api_token']
auth = (email, api_token)

print("=" * 80)
print("TRYING ALL POSSIBLE XRAY API ENDPOINTS")
print("=" * 80)

# All possible endpoints to try
endpoints = [
    # Raven API (Xray Server/DC)
    f"{base_url}/rest/raven/1.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/raven/2.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/raven/1.0/api/testrepository/PZ",
    f"{base_url}/rest/raven/2.0/api/testrepository/PZ",
    
    # Jira API
    f"{base_url}/rest/api/3/project/PZ/testrepository/folders",
    f"{base_url}/rest/api/2/project/PZ/testrepository/folders",
    f"{base_url}/rest/api/3/project/PZ/testrepository",
    f"{base_url}/rest/api/2/project/PZ/testrepository",
    
    # Alternative paths
    f"{base_url}/rest/api/3/testrepository/PZ/folders",
    f"{base_url}/rest/api/2/testrepository/PZ/folders",
    
    # Xray Cloud API (if applicable)
    f"{base_url}/rest/xray/1.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/xray/2.0/api/testrepository/PZ/folders",
]

success_count = 0
for endpoint in endpoints:
    try:
        r = requests.get(endpoint, auth=auth, timeout=10)
        if r.status_code == 200:
            print(f"\nSUCCESS! {endpoint}")
            print(f"Status: {r.status_code}")
            data = r.json()
            print(f"Response type: {type(data)}")
            if isinstance(data, list):
                print(f"Found {len(data)} items")
                if data:
                    print(f"First item: {str(data[0])[:300]}")
            elif isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                print(f"Data: {str(data)[:500]}")
            success_count += 1
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

print("\n" + "=" * 80)
if success_count == 0:
    print("No working endpoints found.")
    print("Xray Test Repository API is not available via REST API.")
    print("You need to use the UI to find folder IDs or assign tests manually.")
else:
    print(f"Found {success_count} working endpoint(s)!")
print("=" * 80)

