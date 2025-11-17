"""Get ALL 237 tests using REST API v3 with cursor pagination"""
import sys
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print("Getting ALL 237 tests using REST API v3")
print("="*80)
print()

# Query: Text search
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Get credentials and base URL
auth = client.jira._session.auth
base_url = client.jira._options['server']

# Use REST API v3 with JQL endpoint
api_url = f"{base_url}/rest/api/3/search/jql"

print("Using REST API v3 with pagination")
print()

# Try pagination with startAt
all_tests = []
all_test_ids = set()
start_at = 0
max_results = 100
page = 1

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

while True:
    print(f"Page {page}: Fetching results {start_at} to {start_at + max_results}...")
    
    try:
        payload = {
            'jql': jql,
            'startAt': start_at,
            'maxResults': max_results,
            'fields': ['key', 'summary', 'status', 'description']
        }
        
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            auth=auth
        )
        
        if response.status_code != 200:
            print(f"  [ERROR] Status {response.status_code}: {response.text[:500]}")
            break
        
        data = response.json()
        
        total = data.get('total', 0)
        issues = data.get('issues', [])
        start_at_response = data.get('startAt', 0)
        max_results_response = data.get('maxResults', 0)
        is_last = start_at_response + len(issues) >= total
        
        print(f"  Got {len(issues)} tests")
        print(f"  API says total: {total}")
        print(f"  Start at: {start_at_response}")
        print(f"  Max results: {max_results_response}")
        print(f"  Is last: {is_last}")
        print()
        
        # Add tests
        for issue in issues:
            test_key = issue.get('key')
            if test_key and test_key not in all_test_ids:
                all_tests.append(issue)
                all_test_ids.add(test_key)
        
        print(f"  Total unique tests so far: {len(all_test_ids)}")
        print()
        
        # Check if we got all results
        if len(issues) == 0:
            print(f"  [STOP] No more results")
            break
        
        if is_last or len(all_test_ids) >= total:
            print(f"  [STOP] Got all {total} tests")
            break
        
        # Continue to next page
        start_at = start_at_response + len(issues)
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
print("FINAL SUMMARY")
print("="*80)
print(f"Total unique tests found: {len(all_test_ids)}")
print()

if len(all_test_ids) < 237:
    print(f"[WARNING] Got {len(all_test_ids)} tests but expected 237!")
    print()
    print("Possible reasons:")
    print("  1. API is limited to 100 results per page")
    print("  2. Pagination is not working correctly")
    print("  3. Query is different in Jira UI")
    print("  4. There are permissions issues")
    print("  5. API has a maximum limit")
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

# Show first 10 test details
print()
print("="*80)
print("FIRST 10 TEST DETAILS:")
print("="*80)
for i, test in enumerate(all_tests[:10], 1):
    test_key = test.get('key')
    fields = test.get('fields', {})
    summary = fields.get('summary', 'N/A')
    print(f"{i:3}. {test_key}: {summary}")

client.close()

