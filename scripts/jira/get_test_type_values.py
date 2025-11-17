#!/usr/bin/env python3
"""Get Test Type field allowed values."""

import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

def main():
    client = JiraClient()
    
    print("Getting Test Type field allowed values...")
    print("=" * 80)
    
    try:
        metadata = client.jira.createmeta(
            projectKeys='PZ',
            issuetypeNames=['Test']
        )
        
        if metadata and 'projects' in metadata and len(metadata['projects']) > 0:
            project = metadata['projects'][0]
            if 'issuetypes' in project and len(project['issuetypes']) > 0:
                test_type = project['issuetypes'][0]
                fields = test_type.get('fields', {})
                
                test_type_field = fields.get('customfield_10951', {})
                
                print(f"\nField Name: {test_type_field.get('name', 'N/A')}")
                print(f"Field Type: {test_type_field.get('schema', {}).get('type', 'N/A')}")
                
                print("\nAllowed Values:")
                allowed_values = test_type_field.get('allowedValues', [])
                if allowed_values:
                    for val in allowed_values:
                        if isinstance(val, dict):
                            print(f"  - {val.get('value', val)}")
                        else:
                            print(f"  - {val}")
                else:
                    print("  (No allowed values found)")
                    
                print("\nFull Field Info:")
                print(json.dumps(test_type_field, indent=2, default=str))
        else:
            print("No metadata found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    client.close()

if __name__ == '__main__':
    main()

