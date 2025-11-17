"""Get ALL 237 tests using Xray GraphQL API"""
import sys
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print("Getting ALL 237 tests using Xray GraphQL API")
print("="*80)
print()

# Get credentials and base URL
auth = client.jira._session.auth
base_url = client.jira._options['server']

print(f"Base URL: {base_url}")
print(f"Test Plan: {test_plan_key}")
print()

# Try Xray GraphQL API endpoints
graphql_endpoints = [
    f"{base_url}/rest/api/2/graphql",
    f"{base_url}/rest/api/3/graphql",
    f"{base_url}/rest/xray/1.0/graphql",
    f"{base_url}/rest/xray/2.0/graphql",
    f"{base_url}/rest/raven/1.0/graphql",
    f"{base_url}/rest/raven/2.0/graphql",
]

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

all_tests = []
all_test_ids = set()

print("="*80)
print("Trying Xray GraphQL API endpoints")
print("="*80)
print()

# GraphQL query to get test plan tests
graphql_queries = [
    # Query 1: Get test plan with tests
    """
    {
      getTestPlan(jira: {id: "%s"}) {
        jira(fields: ["key", "summary"])
        tests {
          jira(fields: ["key", "summary", "status"])
        }
      }
    }
    """ % test_plan_key,
    
    # Query 2: Get test plan with tests (alternative)
    """
    query {
      getTestPlan(jira: {id: "%s"}) {
        jira(fields: ["key", "summary"])
        tests {
          jira(fields: ["key", "summary", "status"])
        }
      }
    }
    """ % test_plan_key,
    
    # Query 3: Get tests by test plan
    """
    {
      getTests(jql: "Test Plan = %s") {
        results {
          jira(fields: ["key", "summary", "status"])
        }
      }
    }
    """ % test_plan_key,
]

for endpoint in graphql_endpoints:
    print(f"Trying GraphQL endpoint: {endpoint}")
    
    for i, query in enumerate(graphql_queries, 1):
        print(f"  Query {i}...")
        
        try:
            payload = {
                'query': query
            }
            
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                auth=auth
            )
            
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"    [SUCCESS] Got response!")
                
                try:
                    data = response.json()
                    print(f"    Response type: {type(data)}")
                    
                    # Parse GraphQL response
                    if 'data' in data:
                        data_content = data['data']
                        
                        # Try to find test plan
                        if 'getTestPlan' in data_content:
                            test_plan = data_content['getTestPlan']
                            if 'tests' in test_plan:
                                tests = test_plan['tests']
                                print(f"    Found {len(tests)} tests in test plan")
                                
                                for test in tests:
                                    if 'jira' in test:
                                        test_jira = test['jira']
                                        test_key = test_jira.get('key')
                                        if test_key and test_key not in all_test_ids:
                                            all_test_ids.add(test_key)
                                            all_tests.append(test)
                                
                                print(f"    Extracted {len(all_test_ids)} unique test IDs")
                                
                                if len(all_test_ids) > 0:
                                    print(f"    [SUCCESS] Found {len(all_test_ids)} tests via GraphQL!")
                                    break
                        
                        # Try to find tests
                        if 'getTests' in data_content:
                            tests_data = data_content['getTests']
                            if 'results' in tests_data:
                                tests = tests_data['results']
                                print(f"    Found {len(tests)} tests")
                                
                                for test in tests:
                                    if 'jira' in test:
                                        test_jira = test['jira']
                                        test_key = test_jira.get('key')
                                        if test_key and test_key not in all_test_ids:
                                            all_test_ids.add(test_key)
                                            all_tests.append(test)
                                
                                print(f"    Extracted {len(all_test_ids)} unique test IDs")
                                
                                if len(all_test_ids) > 0:
                                    print(f"    [SUCCESS] Found {len(all_test_ids)} tests via GraphQL!")
                                    break
                    
                    # Print response for debugging
                    print(f"    Response: {json.dumps(data, indent=2)[:500]}")
                    
                except Exception as e:
                    print(f"    [ERROR] Failed to parse JSON: {e}")
                    print(f"    Response text: {response.text[:500]}")
            elif response.status_code == 404:
                print(f"    [NOT FOUND] Endpoint not available")
            elif response.status_code == 400:
                print(f"    [BAD REQUEST] Query might be invalid")
                print(f"    Response: {response.text[:500]}")
            else:
                print(f"    [ERROR] Status {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            print(f"    [ERROR] {e}")
    
    print()
    
    if len(all_test_ids) > 0:
        print(f"[SUCCESS] Found {len(all_test_ids)} tests via GraphQL!")
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
    print("Trying alternative: Use JQL with pagination workaround...")
    print()
    
    # Alternative: Use multiple JQL queries with different filters
    # Split by test ID ranges or other criteria
    print("Trying multiple JQL queries with different filters...")
    print()
    
    # Try different JQL patterns
    jql_patterns = [
        f'project = PZ AND issuetype = Test AND "Test Plan" = {test_plan_key}',
        f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"',
        f'project = PZ AND issuetype = Test AND summary ~ "{test_plan_key}"',
        f'project = PZ AND issuetype = Test AND description ~ "{test_plan_key}"',
    ]
    
    for jql in jql_patterns:
        print(f"Query: {jql}")
        try:
            # Use enhanced_search_issues
            results = client.jira.enhanced_search_issues(jql, maxResults=1000)
            
            if hasattr(results, '__iter__'):
                tests_list = list(results)
            elif hasattr(results, 'issues'):
                tests_list = list(results.issues)
            elif hasattr(results, 'values'):
                tests_list = list(results.values)
            else:
                tests_list = [results]
            
            print(f"  Got {len(tests_list)} tests")
            
            for test in tests_list:
                test_key = None
                if hasattr(test, 'key'):
                    test_key = test.key
                elif isinstance(test, dict):
                    test_key = test.get('key')
                
                if test_key and test_key not in all_test_ids:
                    all_test_ids.add(test_key)
                    all_tests.append(test)
            
            print(f"  Total unique tests: {len(all_test_ids)}")
            print()
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            print()
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
output_file = Path("docs/04_testing/xray_mapping/TEST_PLAN_PZ14024_XRAY_GRAPHQL_TESTS.txt")
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"Test Plan: PZ-14024\n")
    f.write(f"Total Tests: {len(test_ids)}\n")
    f.write(f"Source: Xray GraphQL API + JQL fallback\n")
    f.write(f"\n")
    f.write(f"All Test IDs:\n")
    for test_id in test_ids:
        f.write(f"{test_id}\n")

print(f"Results saved to: {output_file}")

client.close()

