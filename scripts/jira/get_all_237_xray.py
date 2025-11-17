"""Get ALL 237 tests using Xray API"""
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
print("Getting ALL 237 tests using Xray API")
print("="*80)
print()

# Get credentials and base URL
auth = client.jira._session.auth
base_url = client.jira._options['server']

print(f"Base URL: {base_url}")
print(f"Test Plan: {test_plan_key}")
print()

# Try different Xray API endpoints
xray_endpoints = [
    # Xray v1 (Raven)
    f"/rest/raven/1.0/api/testplan/{test_plan_key}/test",
    f"/rest/raven/1.0/api/testplan/{test_plan_key}/test?limit=1000",
    f"/rest/raven/1.0/api/testplan/{test_plan_key}/test?limit=1000&offset=0",
    
    # Xray v2 (Raven)
    f"/rest/raven/2.0/api/testplan/{test_plan_key}/test",
    f"/rest/raven/2.0/api/testplan/{test_plan_key}/test?limit=1000",
    f"/rest/raven/2.0/api/testplan/{test_plan_key}/test?limit=1000&offset=0",
    
    # Xray v1 (Xray)
    f"/rest/xray/1.0/testplan/{test_plan_key}/test",
    f"/rest/xray/1.0/testplan/{test_plan_key}/test?limit=1000",
    f"/rest/xray/1.0/testplan/{test_plan_key}/test?limit=1000&offset=0",
    
    # Xray v2 (Xray)
    f"/rest/xray/2.0/testplan/{test_plan_key}/test",
    f"/rest/xray/2.0/testplan/{test_plan_key}/test?limit=1000",
    f"/rest/xray/2.0/testplan/{test_plan_key}/test?limit=1000&offset=0",
]

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

all_tests = []
all_test_ids = set()

print("="*80)
print("Trying Xray API endpoints")
print("="*80)
print()

for endpoint in xray_endpoints:
    full_url = f"{base_url}{endpoint}"
    print(f"Trying: {endpoint}")
    
    try:
        # Try GET request
        response = requests.get(
            full_url,
            headers=headers,
            auth=auth
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  [SUCCESS] Got response!")
            
            try:
                data = response.json()
                print(f"  Response type: {type(data)}")
                
                # Parse response
                tests = []
                
                if isinstance(data, list):
                    tests = data
                elif isinstance(data, dict):
                    if 'data' in data:
                        tests = data['data']
                    elif 'tests' in data:
                        tests = data['tests']
                    elif 'results' in data:
                        tests = data['results']
                    elif 'issues' in data:
                        tests = data['issues']
                    elif 'values' in data:
                        tests = data['values']
                    else:
                        # Try to find test keys in the response
                        for key, value in data.items():
                            if isinstance(value, list):
                                tests.extend(value)
                
                print(f"  Found {len(tests)} tests")
                
                # Extract test IDs
                for test in tests:
                    test_key = None
                    
                    if isinstance(test, str):
                        test_key = test
                    elif isinstance(test, dict):
                        test_key = test.get('key') or test.get('id') or test.get('testKey') or test.get('issueKey')
                    elif hasattr(test, 'key'):
                        test_key = test.key
                    
                    if test_key and test_key not in all_test_ids:
                        all_test_ids.add(test_key)
                        all_tests.append(test)
                
                print(f"  Extracted {len(all_test_ids)} unique test IDs")
                print()
                
                if len(tests) > 0:
                    print(f"  [SUCCESS] Found {len(tests)} tests via this endpoint!")
                    print()
                    break  # Success, stop trying other endpoints
                    
            except Exception as e:
                print(f"  [ERROR] Failed to parse JSON: {e}")
                print(f"  Response text: {response.text[:500]}")
        elif response.status_code == 404:
            print(f"  [NOT FOUND] Endpoint not available")
        elif response.status_code == 401:
            print(f"  [UNAUTHORIZED] Authentication failed")
        elif response.status_code == 403:
            print(f"  [FORBIDDEN] No permission")
        else:
            print(f"  [ERROR] Status {response.status_code}: {response.text[:200]}")
            
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    print()

print()
print("="*80)
print("FINAL SUMMARY")
print("="*80)
print(f"Total unique tests found: {len(all_test_ids)}")
print()

if len(all_test_ids) < 237:
    print(f"[WARNING] Got {len(all_test_ids)} tests but expected 237!")
    print()
    print("Trying alternative: Get test plan details and extract test IDs...")
    print()
    
    # Alternative: Get test plan issue and check for test references
    try:
        test_plan_issue = client.jira.issue(test_plan_key, expand='renderedFields')
        
        print(f"Test Plan: {test_plan_issue.key}")
        print(f"Summary: {test_plan_issue.fields.summary}")
        print()
        
        # Check all fields for test references
        print("Checking all fields for test references...")
        for field_name in dir(test_plan_issue.fields):
            if not field_name.startswith('_') and not callable(getattr(test_plan_issue.fields, field_name, None)):
                try:
                    field_value = getattr(test_plan_issue.fields, field_name)
                    if field_value:
                        value_str = str(field_value)
                        # Check if it contains test IDs
                        if 'PZ-' in value_str:
                            # Try to extract test IDs
                            import re
                            test_ids_found = re.findall(r'PZ-\d+', value_str)
                            for tid in test_ids_found:
                                if tid not in all_test_ids:
                                    all_test_ids.add(tid)
                                    print(f"  Found test ID in {field_name}: {tid}")
                except:
                    pass
        
        print(f"Total unique tests after checking fields: {len(all_test_ids)}")
        
    except Exception as e:
        print(f"[ERROR] Failed to get test plan: {e}")
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

# Get details for each test
print()
print("="*80)
print("Getting test details...")
print("="*80)
print()

test_details = []
for test_id in test_ids[:50]:  # Get first 50 to avoid too many requests
    try:
        test_issue = client.jira.issue(test_id)
        test_details.append({
            'key': test_issue.key,
            'summary': test_issue.fields.summary,
            'status': test_issue.fields.status.name
        })
    except Exception as e:
        print(f"  [ERROR] Failed to get {test_id}: {e}")

print(f"Got details for {len(test_details)} tests")
print()

# Save to file
output_file = Path("docs/04_testing/xray_mapping/TEST_PLAN_PZ14024_XRAY_TESTS.txt")
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"Test Plan: PZ-14024\n")
    f.write(f"Total Tests: {len(test_ids)}\n")
    f.write(f"Source: Xray API\n")
    f.write(f"\n")
    f.write(f"All Test IDs:\n")
    for test_id in test_ids:
        f.write(f"{test_id}\n")
    
    if test_details:
        f.write(f"\n")
        f.write(f"Test Details (first 50):\n")
        for test in test_details:
            f.write(f"{test['key']}: {test['summary']} ({test['status']})\n")

print(f"Results saved to: {output_file}")

client.close()

