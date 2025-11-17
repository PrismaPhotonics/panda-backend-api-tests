"""Get ALL tests from Test Plan - complete check with all methods"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print(f"Getting ALL tests from Test Plan: {test_plan_key}")
print("="*80)
print()

# Try different queries
queries = [
    ('Text search', f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'),
    ('Test Plan field', f'project = PZ AND issuetype = Test AND "Test Plan" = {test_plan_key}'),
    ('Summary contains', f'project = PZ AND issuetype = Test AND summary ~ "{test_plan_key}"'),
    ('Description contains', f'project = PZ AND issuetype = Test AND description ~ "{test_plan_key}"'),
]

all_results = {}

for query_name, jql in queries:
    print(f"Query: {query_name}")
    print(f"JQL: {jql}")
    print()
    
    all_tests = []
    start_at = 0
    max_results = 50
    page = 1
    
    while True:
        try:
            print(f"  Page {page}: Fetching {start_at} to {start_at + max_results}...", end=" ")
            results = client.jira.search_issues(
                jql, 
                startAt=start_at, 
                maxResults=max_results
            )
            
            batch = list(results)
            all_tests.extend(batch)
            
            print(f"Got {len(batch)} tests (total: {len(all_tests)}, API says: {results.total})")
            
            # Check if we got all results
            if len(batch) == 0 or len(all_tests) >= results.total or results.isLast:
                print(f"  [DONE] Retrieved all {len(all_tests)} tests")
                break
            
            start_at += max_results
            page += 1
            
            # Safety check
            if page > 10:
                print(f"  [WARNING] Stopped after 10 pages (safety limit)")
                break
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            break
    
    all_results[query_name] = {
        'jql': jql,
        'tests': all_tests,
        'count': len(all_tests)
    }
    
    print()

print("="*80)
print("SUMMARY")
print("="*80)
print()

for query_name, result in all_results.items():
    print(f"{query_name}:")
    print(f"  JQL: {result['jql']}")
    print(f"  Total tests: {result['count']}")
    print()

# Compare results
print("="*80)
print("COMPARISON")
print("="*80)
print()

# Get all unique test IDs from all queries
all_test_ids = set()
for result in all_results.values():
    for test in result['tests']:
        all_test_ids.add(test.key)

print(f"Total unique test IDs across all queries: {len(all_test_ids)}")
print()

# Show which tests are in which query
print("Test IDs by query:")
for query_name, result in all_results.items():
    test_ids = {t.key for t in result['tests']}
    print(f"  {query_name}: {len(test_ids)} tests")
    if len(test_ids) <= 20:
        for tid in sorted(test_ids):
            print(f"    - {tid}")
    else:
        for tid in sorted(list(test_ids))[:10]:
            print(f"    - {tid}")
        print(f"    ... and {len(test_ids) - 10} more")

print()
print("="*80)
print("ALL UNIQUE TEST IDs (sorted):")
print("="*80)
for i, test_id in enumerate(sorted(all_test_ids), 1):
    print(f"{i:3}. {test_id}")

print()
print("="*80)
print("TEST DETAILS:")
print("="*80)

# Get details for all unique tests
test_details = {}
for result in all_results.values():
    for test in result['tests']:
        if test.key not in test_details:
            test_details[test.key] = test

for i, (test_id, test) in enumerate(sorted(test_details.items()), 1):
    print(f"{i:3}. {test_id}: {test.fields.summary}")

client.close()

