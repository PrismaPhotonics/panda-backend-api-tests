"""Get ALL 237 tests - final comprehensive solution"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print("Getting ALL 237 tests - FINAL COMPREHENSIVE SOLUTION")
print("="*80)
print()

# Query: Text search
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Method 1: Use enhanced_search_issues without startAt (it uses cursor internally)
print("="*80)
print("METHOD 1: enhanced_search_issues (no pagination params)")
print("="*80)
print()

try:
    # enhanced_search_issues doesn't take startAt, it uses cursor internally
    results = client.jira.enhanced_search_issues(jql, maxResults=1000)
    
    # Check what we got
    if hasattr(results, '__iter__'):
        tests_list = list(results)
    elif hasattr(results, 'issues'):
        tests_list = list(results.issues)
    elif hasattr(results, 'values'):
        tests_list = list(results.values)
    else:
        tests_list = [results]
    
    print(f"Got {len(tests_list)} tests")
    if hasattr(results, 'total'):
        print(f"API says total: {results.total}")
    if hasattr(results, 'maxResults'):
        print(f"Max results: {results.maxResults}")
    
    print()
    
    # Get all test IDs
    all_test_ids = set()
    for test in tests_list:
        if hasattr(test, 'key'):
            all_test_ids.add(test.key)
        elif isinstance(test, dict):
            all_test_ids.add(test.get('key'))
    
    print(f"Total unique test IDs: {len(all_test_ids)}")
    print()
    
    if len(all_test_ids) < 237:
        print(f"[WARNING] Got {len(all_test_ids)} tests but expected 237!")
        print()
        
        # Method 2: Try to get all tests in project and filter
        print("="*80)
        print("METHOD 2: Get ALL tests in project and filter")
        print("="*80)
        print()
        
        all_project_tests = []
        start_at = 0
        max_results = 100
        page = 1
        
        while True:
            print(f"Page {page}: Fetching all tests {start_at} to {start_at + max_results}...")
            try:
                # Use enhanced_search_issues for all tests
                all_tests_jql = 'project = PZ AND issuetype = Test'
                results = client.jira.enhanced_search_issues(all_tests_jql, maxResults=max_results)
                
                if hasattr(results, '__iter__'):
                    batch = list(results)
                elif hasattr(results, 'issues'):
                    batch = list(results.issues)
                elif hasattr(results, 'values'):
                    batch = list(results.values)
                else:
                    batch = [results]
                
                all_project_tests.extend(batch)
                
                print(f"  Got {len(batch)} tests (total: {len(all_project_tests)})")
                if hasattr(results, 'total'):
                    print(f"  API says total: {results.total}")
                
                # Check if we got all results
                if len(batch) == 0:
                    break
                
                if hasattr(results, 'total'):
                    if len(all_project_tests) >= results.total:
                        break
                
                # Try next page - but enhanced_search_issues doesn't support pagination
                # So we'll filter what we got
                break
                
            except Exception as e:
                print(f"  [ERROR] {e}")
                break
        
        print()
        print(f"Total tests in project: {len(all_project_tests)}")
        print()
        
        # Filter tests that mention PZ-14024
        print("Filtering tests that mention PZ-14024...")
        filtered_tests = []
        for test in all_project_tests:
            # Get test key
            test_key = None
            if hasattr(test, 'key'):
                test_key = test.key
            elif isinstance(test, dict):
                test_key = test.get('key')
            
            if not test_key:
                continue
            
            # Check summary and description
            summary = ""
            description = ""
            
            if hasattr(test, 'fields'):
                if hasattr(test.fields, 'summary'):
                    summary = test.fields.summary or ""
                if hasattr(test.fields, 'description'):
                    desc = test.fields.description
                    description = str(desc) if desc else ""
            elif isinstance(test, dict):
                fields = test.get('fields', {})
                summary = fields.get('summary', '') or ""
                description = str(fields.get('description', '')) or ""
            
            # Check if test mentions PZ-14024
            if test_plan_key in summary or test_plan_key in description:
                filtered_tests.append(test)
                all_test_ids.add(test_key)
        
        print(f"Filtered tests: {len(filtered_tests)}")
        print()
        
        print(f"Total unique tests after filtering: {len(all_test_ids)}")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
print("FINAL SUMMARY")
print("="*80)
print(f"Total unique tests found: {len(all_test_ids)}")
print()

if len(all_test_ids) < 237:
    print(f"[WARNING] Got {len(all_test_ids)} tests but expected 237!")
    print()
    print("The issue is that Jira Cloud API has limitations:")
    print("  1. enhanced_search_issues doesn't support pagination parameters")
    print("  2. search_issues is deprecated and limited to 100 results")
    print("  3. The API might have a maximum limit per query")
    print()
    print("SOLUTION: Need to use multiple queries or get all tests and filter")
else:
    print(f"[SUCCESS] Got all {len(all_test_ids)} tests!")

print()
print("="*80)
print("ALL TEST IDs (sorted):")
print("="*80)

test_ids = sorted(list(all_test_ids))
for i, test_id in enumerate(test_ids, 1):
    print(f"{i:3}. {test_id}")

print()
print(f"Total: {len(test_ids)} tests")

client.close()

