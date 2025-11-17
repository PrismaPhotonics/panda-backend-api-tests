#!/usr/bin/env python3
"""
Test Xray API endpoints to find folder IDs
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

# Test endpoints
endpoints = [
    f"{base_url}/rest/raven/1.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/raven/2.0/api/testrepository/PZ/folders",
    f"{base_url}/rest/api/3/project/PZ/testrepository/folders",
    f"{base_url}/rest/api/2/project/PZ/testrepository/folders",
]

print("Testing Xray API endpoints...")
for endpoint in endpoints:
    try:
        r = requests.get(endpoint, auth=auth, timeout=10)
        print(f"\n{endpoint}")
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"  Response type: {type(data)}")
            if isinstance(data, list):
                print(f"  Found {len(data)} folders")
                if data:
                    print(f"  First folder: {data[0]}")
            elif isinstance(data, dict):
                print(f"  Keys: {list(data.keys())}")
                print(f"  Data: {str(data)[:200]}")
        else:
            print(f"  Error: {r.text[:200]}")
    except Exception as e:
        print(f"\n{endpoint}")
        print(f"  Exception: {e}")

