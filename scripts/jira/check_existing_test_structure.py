#!/usr/bin/env python3
"""Check existing test structure in Xray."""

import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

def main():
    client = JiraClient()
    
    # Try to find an existing test with Test Type set
    print("Searching for existing tests with Test Type...")
    print("=" * 80)
    
    try:
        # Search for tests
        jql = 'project = PZ AND issuetype = Test ORDER BY created DESC'
        tests = client.jira.search_issues(jql, maxResults=10)
        
        print(f"\nFound {len(tests)} recent tests\n")
        
        for test in tests:
            print(f"Test: {test.key} - {test.fields.summary}")
            
            # Check Test Type field
            test_type_value = None
            if hasattr(test.fields, 'customfield_10951'):
                test_type_value = test.fields.customfield_10951
            elif 'customfield_10951' in test.raw['fields']:
                test_type_value = test.raw['fields']['customfield_10951']
            
            if test_type_value:
                print(f"  [OK] Test Type: {test_type_value}")
                if isinstance(test_type_value, dict):
                    print(f"     Value: {test_type_value.get('value', test_type_value)}")
            else:
                print(f"  [NOT SET] Test Type: Not set")
            
            # Check description format
            if test.fields.description:
                try:
                    desc_preview = test.fields.description[:200].replace('\n', ' ')
                    print(f"  Description preview: {desc_preview}...")
                except UnicodeEncodeError:
                    print(f"  Description: (contains special characters)")
            
            print("-" * 80)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    client.close()

if __name__ == '__main__':
    main()

