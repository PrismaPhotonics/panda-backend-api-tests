"""Check pagination to get all 150 tests"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print("Checking pagination to get all 150 tests")
print("="*80)
print()

# Query: Text search
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Try different startAt values
start_at_values = [0, 50, 100, 150, 200]

all_tests = []
all_test_ids = set()

for start_at in start_at_values:
    print(f"Fetching with startAt={start_at}, maxResults=100...")
    try:
        results = client.jira.search_issues(jql, startAt=start_at, maxResults=100)
        batch = list(results)
        print(f"  Got {len(batch)} tests")
        print(f"  API says total: {results.total}")
        print(f"  Is Last: {results.isLast}")
        
        for test in batch:
            all_tests.append(test)
            all_test_ids.add(test.key)
        
        print(f"  Total unique tests so far: {len(all_test_ids)}")
        print()
        
        if len(batch) == 0:
            print("  [STOP] No more results")
            break
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        print()
        break

print("="*80)
print("FINAL SUMMARY")
print("="*80)
print(f"Total unique tests found: {len(all_test_ids)}")
print()

if len(all_test_ids) < 150:
    print(f"[WARNING] Got {len(all_test_ids)} tests but expected 150!")
    print("This might mean:")
    print("  1. API is limited to 100 results")
    print("  2. Query is different in Jira UI")
    print("  3. There are permissions issues")
else:
    print(f"[SUCCESS] Got all {len(all_test_ids)} tests!")

print()
print("All test IDs (sorted):")
for i, test_id in enumerate(sorted(all_test_ids), 1):
    print(f"{i:3}. {test_id}")

client.close()

