#!/usr/bin/env python3
"""
Try Xray via GraphQL API with proper operation names
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
print("TRYING XRAY VIA GRAPHQL API")
print("=" * 80)

url = f"{base_url}/gateway/api/graphql"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Try different GraphQL queries with operation names
queries = [
    {
        "operationName": "GetProject",
        "query": """
        query GetProject {
            project(key: "PZ") {
                id
                key
                name
            }
        }
        """
    },
    {
        "operationName": "GetIssue",
        "query": """
        query GetIssue {
            issue(key: "PZ-14933") {
                id
                key
                summary
            }
        }
        """
    },
    {
        "operationName": "GetSchema",
        "query": """
        query GetSchema {
            __schema {
                queryType {
                    name
                    fields {
                        name
                        type {
                            name
                        }
                    }
                }
            }
        }
        """
    },
]

for query_data in queries:
    try:
        print(f"\nTrying: {query_data['operationName']}")
        r = requests.post(url, json=query_data, headers=headers, auth=auth, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if 'errors' in data:
                print(f"  Errors: {json.dumps(data['errors'], indent=2)[:300]}")
            if 'data' in data and data['data']:
                print(f"  SUCCESS!")
                print(f"  Response: {json.dumps(data['data'], indent=2)[:500]}")
        else:
            print(f"  Status: {r.status_code}")
            print(f"  Response: {r.text[:300]}")
    except Exception as e:
        print(f"  Error: {e}")

# Try to find Xray-related types in schema
print("\n" + "=" * 80)
print("SEARCHING FOR XRAY TYPES IN SCHEMA")
print("=" * 80)

try:
    query = {
        "operationName": "GetAllTypes",
        "query": """
        query GetAllTypes {
            __schema {
                types {
                    name
                }
            }
        }
        """
    }
    r = requests.post(url, json=query, headers=headers, auth=auth, timeout=10)
    if r.status_code == 200:
        data = r.json()
        if 'data' in data:
            types = data['data'].get('__schema', {}).get('types', [])
            xray_types = [t for t in types if t.get('name') and ('xray' in t['name'].lower() or 'test' in t['name'].lower() or 'folder' in t['name'].lower() or 'repository' in t['name'].lower())]
            if xray_types:
                print(f"Found {len(xray_types)} Xray-related types:")
                for t in xray_types[:20]:
                    print(f"  - {t['name']}")
            else:
                print("No Xray-related types found in schema")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
