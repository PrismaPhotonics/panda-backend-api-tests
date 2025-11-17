#!/usr/bin/env python3
"""Script to get Jira field options for custom fields."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient
import json

def main():
    """Get field options for custom fields."""
    client = JiraClient()
    
    # Get all fields
    print("Getting all Jira fields...")
    fields = client.jira.fields()
    
    # Find custom field 10038 (Found by)
    print("\n" + "=" * 80)
    print("Custom Field 10038 (Found by):")
    print("=" * 80)
    
    for field in fields:
        if field['id'] == 'customfield_10038':
            print(f"Name: {field.get('name', 'N/A')}")
            print(f"Type: {field.get('type', 'N/A')}")
            print(f"Schema: {json.dumps(field.get('schema', {}), indent=2)}")
            
            # Try to get options if it's a select field
            if 'options' in field:
                print(f"\nOptions:")
                for option in field['options']:
                    print(f"  - {option}")
            break
    
    # Try to get field options via API
    print("\n" + "=" * 80)
    print("Trying to get field options via API...")
    print("=" * 80)
    
    try:
        # Get field options
        field_options = client.jira.field('customfield_10038')
        print(f"Field: {field_options}")
    except Exception as e:
        print(f"Error getting field options: {e}")
    
    # Try to get issue metadata to see field structure
    print("\n" + "=" * 80)
    print("Getting issue metadata...")
    print("=" * 80)
    
    try:
        # Get issue metadata
        metadata = client.jira.createmeta(
            projectKeys=client.project_key,
            issuetypeNames=['Bug']
        )
        
        if metadata and 'projects' in metadata:
            for project in metadata['projects']:
                if project['key'] == client.project_key:
                    for issue_type in project.get('issuetypes', []):
                        if issue_type['name'] == 'Bug':
                            print(f"\nBug issue type fields:")
                            for field in issue_type.get('fields', {}).values():
                                if field.get('key') == 'customfield_10038':
                                    print(f"Field: {field.get('name')}")
                                    print(f"Allowed Values:")
                                    for value in field.get('allowedValues', []):
                                        print(f"  - {value.get('value', value)}")
                                    break
    except Exception as e:
        print(f"Error getting metadata: {e}")
    
    client.close()

if __name__ == "__main__":
    main()

