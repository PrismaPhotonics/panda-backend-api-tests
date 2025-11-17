"""Get ALL 150 tests from Test Plan with proper pagination"""
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

# Query: Text search
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Get all results with pagination
all_tests = []
start_at = 0
max_results = 100  # Use 100 to get more results per page
page = 1

while True:
    print(f"Page {page}: Fetching results {start_at} to {start_at + max_results}...")
    
    try:
        results = client.jira.search_issues(
            jql, 
            startAt=start_at, 
            maxResults=max_results
        )
        
        batch = list(results)
        all_tests.extend(batch)
        
        print(f"  Got {len(batch)} tests (total so far: {len(all_tests)})")
        print(f"  API says total: {results.total}")
        print(f"  Is Last: {results.isLast}")
        print()
        
        # Check if we got all results
        if len(batch) == 0 or results.isLast or len(all_tests) >= results.total:
            print(f"[DONE] Retrieved all {len(all_tests)} tests")
            print(f"[INFO] API says total: {results.total}")
            break
        
        # Check if we need to fetch more
        if len(all_tests) < results.total:
            start_at += len(batch)
            page += 1
        else:
            break
            
        # Safety check
        if page > 10:
            print(f"[WARNING] Stopped after 10 pages (safety limit)")
            break
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        break

print()
print("="*80)
print("FINAL SUMMARY")
print("="*80)
print(f"Total tests found: {len(all_tests)}")
print()

# Get all test IDs
test_ids = sorted([t.key for t in all_tests])

print(f"Total unique test IDs: {len(test_ids)}")
print()
print("="*80)
print("ALL TEST IDs (sorted):")
print("="*80)
for i, test_id in enumerate(test_ids, 1):
    print(f"{i:3}. {test_id}")

print()
print("="*80)
print("TEST DETAILS:")
print("="*80)
for i, test in enumerate(all_tests, 1):
    print(f"{i:3}. {test.key}: {test.fields.summary}")

client.close()

