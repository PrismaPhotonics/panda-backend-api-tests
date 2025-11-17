"""Check what Jira API actually returns for total count"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print("Checking Jira API response details")
print("="*80)
print()

# Query: Text search
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Get first page
results = client.jira.search_issues(jql, startAt=0, maxResults=50)

print("API Response Details:")
print(f"  Type: {type(results)}")
print(f"  Total: {results.total}")
print(f"  Max Results: {results.maxResults}")
print(f"  Start At: {results.startAt}")
print(f"  Is Last: {results.isLast}")
print(f"  Length: {len(results)}")
print()

# Check if there are more results
if not results.isLast:
    print(f"[INFO] There are more results! Total: {results.total}")
    print(f"[INFO] Got {len(results)} out of {results.total} results")
    print()
    print("Fetching all pages...")
    
    all_tests = list(results)
    start_at = 50
    
    while not results.isLast and start_at < results.total:
        print(f"Fetching page starting at {start_at}...")
        results = client.jira.search_issues(jql, startAt=start_at, maxResults=50)
        all_tests.extend(results)
        print(f"  Got {len(results)} tests (total so far: {len(all_tests)})")
        start_at += 50
        
        if results.isLast:
            break
    
    print()
    print(f"Total tests retrieved: {len(all_tests)}")
    print(f"Total from API: {results.total}")
    
    if len(all_tests) != results.total:
        print(f"[WARNING] Mismatch! Got {len(all_tests)} but API says {results.total}")
    else:
        print(f"[SUCCESS] Got all {len(all_tests)} tests!")
else:
    print(f"[INFO] All results retrieved in first page: {len(results)} tests")

client.close()

