#!/usr/bin/env python3
"""
Find Xray Test Type Custom Field ID
====================================

This script finds the custom field ID for Xray Test Type field.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient
import json

def main():
    """Find Test Type custom field."""
    client = JiraClient()
    
    print("Searching for Xray Test Type custom field...")
    print("=" * 80)
    
    # Get all fields
    fields = client.jira.fields()
    
    # Search for Test Type field
    test_type_fields = []
    for field in fields:
        field_name = field.get('name', '').lower()
        field_id = field.get('id', '')
        
        if 'test type' in field_name or 'testtype' in field_name:
            test_type_fields.append({
                'id': field_id,
                'name': field.get('name'),
                'type': field.get('type'),
                'schema': field.get('schema', {})
            })
    
    if test_type_fields:
        print(f"\nFound {len(test_type_fields)} Test Type field(s):\n")
        for field in test_type_fields:
            print(f"Field ID: {field['id']}")
            print(f"Name: {field['name']}")
            print(f"Type: {field['type']}")
            print(f"Schema: {json.dumps(field['schema'], indent=2)}")
            print("-" * 80)
    else:
        print("\n⚠️  Test Type field not found by name search.")
        print("\nTrying to find by checking Test issue metadata...")
        
        # Try to get Test issue metadata
        try:
            metadata = client.jira.createmeta(
                projectKeys="PZ",
                issuetypeNames=['Test']
            )
            
            if metadata and 'projects' in metadata:
                for project in metadata['projects']:
                    if project['key'] == 'PZ':
                        for issue_type in project.get('issuetypes', []):
                            if issue_type['name'] == 'Test':
                                print(f"\nTest issue type fields:")
                                for field_id, field_info in issue_type.get('fields', {}).items():
                                    field_name = field_info.get('name', '')
                                    if 'test type' in field_name.lower() or 'testtype' in field_name.lower():
                                        print(f"\n✅ Found Test Type field:")
                                        print(f"   Field ID: {field_id}")
                                        print(f"   Name: {field_name}")
                                        print(f"   Type: {field_info.get('schema', {}).get('type', 'N/A')}")
                                        
                                        # Try to get allowed values
                                        if 'allowedValues' in field_info:
                                            print(f"   Allowed Values:")
                                            for value in field_info['allowedValues']:
                                                print(f"     - {value.get('value', value)}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Also check an existing test issue
    print("\n" + "=" * 80)
    print("Checking existing test issue for Test Type field...")
    print("=" * 80)
    
    try:
        # Get a test issue (try PZ-14715 which we just created)
        test_issue = client.jira.issue('PZ-14715', expand='names')
        
        print(f"\nTest Issue: {test_issue.key}")
        print(f"Fields in issue:")
        
        # Check all custom fields
        for field_name, field_value in test_issue.raw['fields'].items():
            if field_name.startswith('customfield_'):
                field_info = None
                # Try to get field name from names
                if 'names' in test_issue.raw:
                    field_id_num = field_name.replace('customfield_', '')
                    if field_id_num in test_issue.raw['names']:
                        field_info = test_issue.raw['names'][field_id_num]
                
                if field_info and ('test type' in field_info.lower() or 'testtype' in field_info.lower()):
                    print(f"\n✅ Found Test Type field:")
                    print(f"   Field ID: {field_name}")
                    print(f"   Name: {field_info}")
                    print(f"   Value: {field_value}")
                elif field_value:
                    # Print all custom fields for reference
                    print(f"   {field_name}: {field_value}")
    except Exception as e:
        print(f"Could not check test issue: {e}")
    
    client.close()

if __name__ == "__main__":
    main()

