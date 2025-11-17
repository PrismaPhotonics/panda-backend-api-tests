"""Get ALL 237 tests from Test Plan - comprehensive check"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print("Getting ALL 237 tests from Test Plan PZ-14024")
print("="*80)
print()

# Query: Text search
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Method 1: Try with different maxResults values
print("="*80)
print("METHOD 1: Different maxResults values")
print("="*80)
print()

max_results_options = [50, 100, 200, 500, 1000]

for max_results in max_results_options:
    print(f"Trying maxResults={max_results}...")
    try:
        results = client.jira.search_issues(jql, startAt=0, maxResults=max_results)
        print(f"  Total from API: {results.total}")
        print(f"  Got: {len(results)} tests")
        print(f"  Is Last: {results.isLast}")
        print()
        
        if results.total > len(results):
            print(f"  [INFO] There are more results! Total: {results.total}, Got: {len(results)}")
            break
    except Exception as e:
        print(f"  [ERROR] {e}")
        print()
        continue

# Method 2: Try pagination with proper handling
print("="*80)
print("METHOD 2: Pagination with proper handling")
print("="*80)
print()

all_tests = []
start_at = 0
max_results = 100
page = 1
total_from_api = None

while True:
    print(f"Page {page}: Fetching results {start_at} to {start_at + max_results}...")
    
    try:
        results = client.jira.search_issues(
            jql, 
            startAt=start_at, 
            maxResults=max_results
        )
        
        if total_from_api is None:
            total_from_api = results.total
            print(f"  API says total: {total_from_api}")
        
        batch = list(results)
        all_tests.extend(batch)
        
        print(f"  Got {len(batch)} tests (total so far: {len(all_tests)})")
        print(f"  Is Last: {results.isLast}")
        print()
        
        # Check if we got all results
        if len(batch) == 0:
            print(f"  [STOP] No more results")
            break
        
        if results.isLast:
            print(f"  [STOP] API says this is the last page")
            break
        
        if len(all_tests) >= total_from_api:
            print(f"  [STOP] Got all {total_from_api} tests from API")
            break
        
        # Continue to next page
        start_at += len(batch)
        page += 1
        
        # Safety check
        if page > 10:
            print(f"  [WARNING] Stopped after 10 pages (safety limit)")
            break
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        break

print()
print("="*80)
print("METHOD 3: Check if there are more results with different queries")
print("="*80)
print()

# Try different queries
queries = [
    ('Text search', f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'),
    ('Test Plan field', f'project = PZ AND issuetype = Test AND "Test Plan" = {test_plan_key}'),
    ('All tests in project', 'project = PZ AND issuetype = Test'),
]

all_unique_tests = set()
query_results = {}

for query_name, query_jql in queries:
    print(f"Query: {query_name}")
    print(f"JQL: {query_jql}")
    
    query_tests = []
    start_at = 0
    max_results = 100
    page = 1
    
    while True:
        try:
            results = client.jira.search_issues(
                query_jql, 
                startAt=start_at, 
                maxResults=max_results
            )
            
            batch = list(results)
            query_tests.extend(batch)
            
            print(f"  Page {page}: Got {len(batch)} tests (total: {len(query_tests)}, API says: {results.total})")
            
            if len(batch) == 0 or results.isLast or len(query_tests) >= results.total:
                break
            
            start_at += len(batch)
            page += 1
            
            if page > 10:
                print(f"  [WARNING] Stopped after 10 pages")
                break
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            break
    
    query_results[query_name] = query_tests
    for test in query_tests:
        all_unique_tests.add(test.key)
    
    print(f"  Total: {len(query_tests)} tests")
    print()

print()
print("="*80)
print("FINAL SUMMARY")
print("="*80)
print()

print(f"Method 2 (Pagination): {len(all_tests)} tests")
print(f"Method 3 (All queries): {len(all_unique_tests)} unique tests")
print()

print("Results by query:")
for query_name, tests in query_results.items():
    print(f"  {query_name}: {len(tests)} tests")

print()
print("="*80)
print("ANALYSIS")
print("="*80)
print()

if len(all_tests) < 237:
    print(f"[WARNING] Got {len(all_tests)} tests but expected 237!")
    print("Possible reasons:")
    print("  1. API is limited to 100 results per page")
    print("  2. Pagination is not working correctly")
    print("  3. Query is different in Jira UI")
    print("  4. There are permissions issues")
    print("  5. API has a maximum limit")
else:
    print(f"[SUCCESS] Got {len(all_tests)} tests!")

print()
print("="*80)
print("ALL TEST IDs (sorted):")
print("="*80)

test_ids = sorted([t.key for t in all_tests])
for i, test_id in enumerate(test_ids, 1):
    print(f"{i:3}. {test_id}")

print()
print(f"Total: {len(test_ids)} tests")

client.close()

