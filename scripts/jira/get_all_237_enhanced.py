"""Get ALL 237 tests using enhanced_search_issues with proper pagination"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print("Getting ALL 237 tests using enhanced_search_issues")
print("="*80)
print()

# Query: Text search
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Check if enhanced_search_issues exists
if not hasattr(client.jira, 'enhanced_search_issues'):
    print("[ERROR] enhanced_search_issues method not found!")
    print("Available methods:")
    methods = [m for m in dir(client.jira) if 'search' in m.lower()]
    for method in methods:
        print(f"  - {method}")
    client.close()
    sys.exit(1)

print("Using enhanced_search_issues method")
print()

# Try enhanced_search_issues with different maxResults
all_tests = []
all_test_ids = set()
start_at = 0
max_results = 100
page = 1

print("="*80)
print("PAGINATION WITH enhanced_search_issues")
print("="*80)
print()

while True:
    print(f"Page {page}: Fetching results {start_at} to {start_at + max_results}...")
    
    try:
        # Try enhanced_search_issues
        results = client.jira.enhanced_search_issues(
            jql, 
            startAt=start_at, 
            maxResults=max_results
        )
        
        # Check what type of result we got
        print(f"  Result type: {type(results)}")
        
        # Try to get batch
        if hasattr(results, '__iter__'):
            batch = list(results)
        elif hasattr(results, 'issues'):
            batch = list(results.issues)
        elif hasattr(results, 'values'):
            batch = list(results.values)
        else:
            batch = [results]
        
        print(f"  Got {len(batch)} tests")
        
        # Check total
        if hasattr(results, 'total'):
            print(f"  API says total: {results.total}")
        if hasattr(results, 'maxResults'):
            print(f"  Max results: {results.maxResults}")
        if hasattr(results, 'startAt'):
            print(f"  Start at: {results.startAt}")
        if hasattr(results, 'isLast'):
            print(f"  Is Last: {results.isLast}")
        
        # Add tests
        for test in batch:
            if hasattr(test, 'key'):
                if test.key not in all_test_ids:
                    all_tests.append(test)
                    all_test_ids.add(test.key)
        
        print(f"  Total unique tests so far: {len(all_test_ids)}")
        print()
        
        # Check if we got all results
        if len(batch) == 0:
            print(f"  [STOP] No more results")
            break
        
        # Check if this is the last page
        if hasattr(results, 'isLast') and results.isLast:
            print(f"  [STOP] API says this is the last page")
            break
        
        # Check if we got all results
        if hasattr(results, 'total'):
            if len(all_test_ids) >= results.total:
                print(f"  [STOP] Got all {results.total} tests from API")
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
print("FINAL SUMMARY")
print("="*80)
print(f"Total unique tests found: {len(all_test_ids)}")
print()

if len(all_test_ids) < 237:
    print(f"[WARNING] Got {len(all_test_ids)} tests but expected 237!")
    print()
    print("Trying alternative: Direct API call...")
    print()
    
    # Try direct API call
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        # Get credentials from client
        auth = client.jira._session.auth
        base_url = client.jira._options['server']
        
        # Build API URL
        api_url = f"{base_url}/rest/api/3/search"
        
        # Build request
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Try pagination
        all_direct_tests = []
        start_at = 0
        max_results = 100
        page = 1
        
        while True:
            print(f"Direct API call - Page {page}: {start_at} to {start_at + max_results}...")
            
            payload = {
                'jql': jql,
                'startAt': start_at,
                'maxResults': max_results,
                'fields': ['key', 'summary', 'status']
            }
            
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                auth=auth
            )
            
            if response.status_code != 200:
                print(f"  [ERROR] Status {response.status_code}: {response.text[:200]}")
                break
            
            data = response.json()
            
            total = data.get('total', 0)
            issues = data.get('issues', [])
            
            print(f"  Got {len(issues)} tests")
            print(f"  API says total: {total}")
            print(f"  Start at: {data.get('startAt', 0)}")
            print(f"  Max results: {data.get('maxResults', 0)}")
            print()
            
            # Add tests
            for issue in issues:
                test_key = issue.get('key')
                if test_key and test_key not in all_test_ids:
                    all_direct_tests.append(issue)
                    all_test_ids.add(test_key)
            
            print(f"  Total unique tests so far: {len(all_test_ids)}")
            print()
            
            # Check if we got all results
            if len(issues) == 0:
                print(f"  [STOP] No more results")
                break
            
            if len(all_test_ids) >= total:
                print(f"  [STOP] Got all {total} tests")
                break
            
            # Continue to next page
            start_at += len(issues)
            page += 1
            
            if page > 10:
                print(f"  [WARNING] Stopped after 10 pages")
                break
        
        print(f"Direct API call found: {len(all_direct_tests)} tests")
        print(f"Total unique tests: {len(all_test_ids)}")
        
    except Exception as e:
        print(f"[ERROR] Direct API call failed: {e}")
        import traceback
        traceback.print_exc()
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

client.close()

