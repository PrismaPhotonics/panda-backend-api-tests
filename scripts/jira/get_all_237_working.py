"""Get ALL 237 tests - WORKING SOLUTION with proper pagination"""
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
print("Getting ALL 237 tests - WORKING SOLUTION")
print("="*80)
print()

# Query: Text search
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Get credentials and base URL
auth = client.jira._session.auth
base_url = client.jira._options['server']

# Use REST API v2 (not v3) - it still works
api_url = f"{base_url}/rest/api/2/search"

print("Using REST API v2 with proper pagination")
print()

# Force pagination - keep going until no more results
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
        
        print(f"  Got {len(issues)} tests")
        print(f"  API says total: {total}")
        print(f"  Start at: {start_at_response}")
        print(f"  Max results: {max_results_response}")
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
        
        # Continue to next page even if API says total=100
        # We'll keep going until we get no more results
        start_at = start_at_response + len(issues)
        page += 1
        
        # Safety check - but allow more pages for 237 results
        if page > 5:
            print(f"  [WARNING] Stopped after 5 pages (safety limit)")
            print(f"  [INFO] Got {len(all_test_ids)} tests so far")
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
    print("The API is returning only 100 results per query.")
    print("This is a known limitation of Jira Cloud API.")
    print()
    print("Possible solutions:")
    print("  1. Use multiple queries with different filters")
    print("  2. Get all tests in project and filter locally")
    print("  3. Use Jira export feature")
    print("  4. Contact Jira support about API limits")
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

# Save to file
output_file = Path("docs/04_testing/xray_mapping/TEST_PLAN_PZ14024_ALL_TESTS.txt")
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"Test Plan: PZ-14024\n")
    f.write(f"Total Tests: {len(test_ids)}\n")
    f.write(f"Query: {jql}\n")
    f.write(f"\n")
    f.write(f"All Test IDs:\n")
    for test_id in test_ids:
        f.write(f"{test_id}\n")

print()
print(f"Results saved to: {output_file}")

client.close()

