#!/usr/bin/env python3
"""
Check folder custom field and try to use it
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
print("CHECKING FOLDER CUSTOM FIELD")
print("=" * 80)

# Get custom field details
print("\n1. Getting custom field details...")
try:
    url = f"{base_url}/rest/api/3/field/customfield_10195"
    r = requests.get(url, auth=auth, timeout=10)
    if r.status_code == 200:
        field = r.json()
        print(f"   Field ID: {field.get('id')}")
        print(f"   Field Name: {field.get('name')}")
        print(f"   Field Type: {field.get('type')}")
        print(f"   Schema: {field.get('schema')}")
    else:
        print(f"   Status: {r.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Check if test issues have this field populated
print("\n2. Checking test issues for folder field...")
try:
    url = f"{base_url}/rest/api/3/search"
    jql = "project = PZ AND type = Test AND key IN (PZ-14933, PZ-14934, PZ-14935)"
    params = {
        'jql': jql,
        'fields': 'id,key,summary,customfield_10195',
        'expand': 'renderedFields,names,schema'
    }
    r = requests.get(url, auth=auth, params=params, timeout=10)
    if r.status_code == 200:
        data = r.json()
        issues = data.get('issues', [])
        print(f"   Found {len(issues)} tests")
        for issue in issues:
            key = issue.get('key')
            fields = issue.get('fields', {})
            folder_value = fields.get('customfield_10195')
            print(f"   {key}: folder field = {folder_value}")
except Exception as e:
    print(f"   Error: {e}")

# Try to update a test with folder field
print("\n3. Testing if we can update folder field...")
try:
    # First, get a test issue
    url = f"{base_url}/rest/api/3/search"
    jql = "project = PZ AND type = Test AND key = PZ-14933"
    params = {
        'jql': jql,
        'fields': 'id,key',
    }
    r = requests.get(url, auth=auth, params=params, timeout=10)
    if r.status_code == 200:
        data = r.json()
        issues = data.get('issues', [])
        if issues:
            issue = issues[0]
            issue_id = issue.get('id')
            issue_key = issue.get('key')
            
            # Try to get current value first
            url_get = f"{base_url}/rest/api/3/issue/{issue_key}"
            r_get = requests.get(url_get, auth=auth, params={'fields': 'customfield_10195'}, timeout=10)
            if r_get.status_code == 200:
                current_data = r_get.json()
                current_folder = current_data.get('fields', {}).get('customfield_10195')
                print(f"   Current folder value for {issue_key}: {current_folder}")
                
                # Try to see what values are possible
                # This is a dry run - we won't actually update
                print(f"   (Dry run - not updating)")
except Exception as e:
    print(f"   Error: {e}")

# Try to find folder options/values
print("\n4. Checking for folder options...")
try:
    # Try to get field options if it's a select field
    url = f"{base_url}/rest/api/3/field/customfield_10195/option"
    r = requests.get(url, auth=auth, timeout=10)
    if r.status_code == 200:
        options = r.json()
        print(f"   Found {len(options)} folder options:")
        for opt in options[:10]:
            print(f"     {opt.get('id')}: {opt.get('value')}")
    else:
        print(f"   Status: {r.status_code} - {r.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 80)

