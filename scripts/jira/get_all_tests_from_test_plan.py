"""Get ALL tests from Test Plan - proper pagination"""
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

# Query: Text search (contains PZ-14024 anywhere)
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Get all results with proper pagination
all_tests = []
start_at = 0
max_results = 50
total = None
page = 1

while True:
    print(f"Page {page}: Fetching results {start_at} to {start_at + max_results}...")
    
    try:
        results = client.jira.search_issues(
            jql, 
            startAt=start_at, 
            maxResults=max_results,
            expand='renderedFields'
        )
        
        if total is None:
            total = results.total
            print(f"  Total results available: {total}")
        
        batch = list(results)
        all_tests.extend(batch)
        print(f"  Got {len(batch)} tests (total so far: {len(all_tests)}/{total})")
        
        # Check if we got all results
        if len(all_tests) >= total or len(batch) < max_results:
            print(f"  [OK] All results retrieved!")
            break
        
        start_at += max_results
        page += 1
        
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        break

print()
print("="*80)
print("FINAL SUMMARY")
print("="*80)
print(f"Total tests found: {len(all_tests)}")
print(f"Total available (from API): {total}")
print()

if len(all_tests) != total:
    print(f"[WARNING] Got {len(all_tests)} tests but API says {total} available!")
    print("This might mean pagination didn't work correctly.")
else:
    print(f"[SUCCESS] Got all {len(all_tests)} tests!")

print()
print("="*80)
print("ALL TEST IDs (sorted):")
print("="*80)
test_ids = sorted([t.key for t in all_tests])
for i, test_id in enumerate(test_ids, 1):
    print(f"{i:3}. {test_id}")

print()
print("="*80)
print("TEST DETAILS:")
print("="*80)
for i, test in enumerate(all_tests, 1):
    print(f"{i:3}. {test.key}: {test.fields.summary}")

client.close()

