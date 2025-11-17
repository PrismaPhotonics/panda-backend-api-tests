"""Get ALL tests from Test Plan with pagination"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print(f"Getting ALL tests from Test Plan: {test_plan_key} (with pagination)")
print("="*80)
print()

# Query: Text search (contains PZ-14024 anywhere)
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Get all results with pagination
all_tests = []
start_at = 0
max_results = 50
total = None

while True:
    print(f"Fetching results {start_at} to {start_at + max_results}...")
    results = client.jira.search_issues(jql, startAt=start_at, maxResults=max_results)
    
    if total is None:
        total = results.total
        print(f"Total results available: {total}")
    
    all_tests.extend(results)
    print(f"  Got {len(results)} tests (total so far: {len(all_tests)})")
    
    if len(all_tests) >= total or len(results) == 0:
        break
    
    start_at += max_results

print()
print("="*80)
print("SUMMARY")
print("="*80)
print(f"Total tests found: {len(all_tests)}")
print(f"Total available: {total}")
print()

# Get all test IDs
test_ids = [t.key for t in all_tests]
test_ids_sorted = sorted(test_ids)

print(f"First 20 test IDs:")
for i, test_id in enumerate(test_ids_sorted[:20], 1):
    print(f"  {i:3}. {test_id}")

print()
print(f"Last 20 test IDs:")
for i, test_id in enumerate(test_ids_sorted[-20:], len(test_ids_sorted)-19):
    print(f"  {i:3}. {test_id}")

print()
print("="*80)
print("ALL TEST IDs (sorted):")
print("="*80)
for i, test_id in enumerate(test_ids_sorted, 1):
    print(f"{i:3}. {test_id}")

print()
print("="*80)
print("TEST DETAILS:")
print("="*80)
for i, test in enumerate(all_tests, 1):
    print(f"{i:3}. {test.key}: {test.fields.summary}")

client.close()

