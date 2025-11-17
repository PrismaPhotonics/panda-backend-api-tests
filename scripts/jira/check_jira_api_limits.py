"""Check Jira API limits and pagination"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print("Checking Jira API limits and pagination")
print("="*80)
print()

# Query: Text search
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Try different maxResults values
max_results_options = [50, 100, 200, 500, 1000]

for max_results in max_results_options:
    print(f"Trying maxResults={max_results}...")
    try:
        results = client.jira.search_issues(jql, startAt=0, maxResults=max_results)
        print(f"  Total from API: {results.total}")
        print(f"  Got: {len(results)} tests")
        print(f"  Is Last: {results.isLast}")
        print(f"  Max Results: {results.maxResults}")
        print()
        
        if results.total > len(results):
            print(f"  [INFO] There are more results! Total: {results.total}, Got: {len(results)}")
            print(f"  [INFO] Need to fetch more pages...")
            print()
            
            # Try to get all pages
            all_tests = list(results)
            start_at = len(results)
            
            while start_at < results.total:
                print(f"  Fetching page starting at {start_at}...")
                page_results = client.jira.search_issues(jql, startAt=start_at, maxResults=max_results)
                page_tests = list(page_results)
                all_tests.extend(page_tests)
                print(f"    Got {len(page_tests)} tests (total so far: {len(all_tests)})")
                
                if len(page_tests) == 0 or page_results.isLast:
                    break
                
                start_at += len(page_tests)
            
            print(f"  [FINAL] Total tests retrieved: {len(all_tests)}")
            print(f"  [FINAL] Total from API: {results.total}")
            print()
            
            if len(all_tests) == results.total:
                print(f"  [SUCCESS] Got all {len(all_tests)} tests!")
            else:
                print(f"  [WARNING] Got {len(all_tests)} tests but API says {results.total} available!")
            
            break
        else:
            print(f"  [OK] Got all {len(results)} tests in first page")
            print()
    except Exception as e:
        print(f"  [ERROR] {e}")
        print()
        continue

print("="*80)
print("Checking if there are more results with different queries")
print("="*80)
print()

# Try without text search - just all tests
jql_all = 'project = PZ AND issuetype = Test'
print(f"Query: {jql_all}")
print()

try:
    results = client.jira.search_issues(jql_all, startAt=0, maxResults=1000)
    print(f"Total tests in project: {results.total}")
    print(f"Got: {len(results)} tests")
    print()
    
    # Check how many mention PZ-14024
    tests_with_plan = []
    for test in results:
        # Check if test mentions PZ-14024 in any field
        summary = test.fields.summary or ""
        description = getattr(test.fields, 'description', None) or ""
        description_str = str(description) if description else ""
        
        if test_plan_key in summary or test_plan_key in description_str:
            tests_with_plan.append(test.key)
    
    print(f"Tests that mention '{test_plan_key}' in summary/description: {len(tests_with_plan)}")
    if len(tests_with_plan) > 0:
        print("First 20:")
        for tid in tests_with_plan[:20]:
            print(f"  - {tid}")
        if len(tests_with_plan) > 20:
            print(f"  ... and {len(tests_with_plan) - 20} more")
    
except Exception as e:
    print(f"[ERROR] {e}")

client.close()

