#!/usr/bin/env python3
"""Find Test Type field values from existing tests."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

def main():
    client = JiraClient()
    
    print("Searching for tests with Test Type set...")
    print("=" * 80)
    
    try:
        # Search for tests that have Test Type set
        jql = 'project = PZ AND issuetype = Test ORDER BY created DESC'
        tests = client.jira.search_issues(jql, maxResults=50)
        
        print(f"\nFound {len(tests)} recent tests\n")
        
        test_types_found = set()
        
        for test in tests:
            # Check Test Type field
            test_type_value = None
            if hasattr(test.fields, 'customfield_10951') and test.fields.customfield_10951:
                test_type_value = test.fields.customfield_10951
            elif 'customfield_10951' in test.raw['fields'] and test.raw['fields']['customfield_10951']:
                test_type_value = test.raw['fields']['customfield_10951']
            
            if test_type_value:
                if isinstance(test_type_value, dict):
                    value = test_type_value.get('value', str(test_type_value))
                else:
                    value = str(test_type_value)
                
                test_types_found.add(value)
                print(f"[OK] {test.key}: Test Type = '{value}'")
        
        print("\n" + "=" * 80)
        print("Summary of Test Type values found:")
        print("=" * 80)
        
        if test_types_found:
            for value in sorted(test_types_found):
                print(f"  - {value}")
        else:
            print("  [ERROR] No tests with Test Type set found")
            print("\n  Trying to find any test with customfield_10951...")
            
            # Check our newly created tests
            for test in tests[:10]:
                if 'customfield_10951' in test.raw['fields']:
                    val = test.raw['fields']['customfield_10951']
                    print(f"  {test.key}: customfield_10951 = {val} (type: {type(val).__name__})")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    client.close()

if __name__ == '__main__':
    main()

