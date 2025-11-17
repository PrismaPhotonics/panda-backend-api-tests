"""Get ALL 237 tests - FORCE pagination even if API says total=100"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print("Getting ALL 237 tests - FORCE pagination")
print("="*80)
print()

# Query: Text search
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Force pagination - keep going until no more results
all_tests = []
all_test_ids = set()
start_at = 0
max_results = 50  # Use smaller page size
page = 1

print("="*80)
print("FORCED PAGINATION - Getting all pages")
print("="*80)
print()

while True:
    print(f"Page {page}: Fetching results {start_at} to {start_at + max_results}...")
    
    try:
        # Use enhanced_search_issues with maxResults
        # But we'll manually paginate by getting all tests and filtering
        # Actually, let's try to use the Jira Python library's search_issues
        # which might support pagination better
        
        # Try to use the underlying Jira client directly
        # Check if we can use search_issues with startAt
        try:
            # Try to use search_issues (deprecated but might work)
            results = client.jira.search_issues(
                jql,
                startAt=start_at,
                maxResults=max_results
            )
            
            batch = list(results)
            
            print(f"  Got {len(batch)} tests")
            print(f"  API says total: {results.total}")
            print(f"  Is Last: {results.isLast}")
            print()
            
            # Add tests
            for test in batch:
                if test.key not in all_test_ids:
                    all_tests.append(test)
                    all_test_ids.add(test.key)
            
            print(f"  Total unique tests so far: {len(all_test_ids)}")
            print()
            
            # Check if we got all results
            if len(batch) == 0:
                print(f"  [STOP] No more results")
                break
            
            # Continue to next page even if API says total=100
            # We'll keep going until we get no more results
            start_at += len(batch)
            page += 1
            
            # Safety check - but allow more pages for 237 results
            if page > 10:
                print(f"  [WARNING] Stopped after 10 pages (safety limit)")
                print(f"  [INFO] Got {len(all_test_ids)} tests so far")
                break
                
        except Exception as e:
            # If search_issues is deprecated, try enhanced_search_issues
            if "deprecated" in str(e).lower() or "enhanced" in str(e).lower():
                print(f"  [INFO] search_issues is deprecated, trying alternative...")
                
                # Try to get all tests in project and filter
                print(f"  [INFO] Getting all tests in project and filtering...")
                
                # Get all tests in project
                all_project_tests = []
                project_jql = 'project = PZ AND issuetype = Test'
                
                # Try enhanced_search_issues
                try:
                    results = client.jira.enhanced_search_issues(project_jql, maxResults=1000)
                    
                    if hasattr(results, '__iter__'):
                        all_project_tests = list(results)
                    elif hasattr(results, 'issues'):
                        all_project_tests = list(results.issues)
                    elif hasattr(results, 'values'):
                        all_project_tests = list(results.values)
                    else:
                        all_project_tests = [results]
                    
                    print(f"  Got {len(all_project_tests)} tests from project")
                    
                    # Filter tests that mention PZ-14024
                    filtered_tests = []
                    for test in all_project_tests:
                        test_key = None
                        if hasattr(test, 'key'):
                            test_key = test.key
                        elif isinstance(test, dict):
                            test_key = test.get('key')
                        
                        if not test_key:
                            continue
                        
                        # Check summary and description
                        summary = ""
                        description = ""
                        
                        if hasattr(test, 'fields'):
                            if hasattr(test.fields, 'summary'):
                                summary = test.fields.summary or ""
                            if hasattr(test.fields, 'description'):
                                desc = test.fields.description
                                description = str(desc) if desc else ""
                        elif isinstance(test, dict):
                            fields = test.get('fields', {})
                            summary = fields.get('summary', '') or ""
                            description = str(fields.get('description', '')) or ""
                        
                        # Check if test mentions PZ-14024
                        if test_plan_key in summary or test_plan_key in description:
                            if test_key not in all_test_ids:
                                filtered_tests.append(test)
                                all_test_ids.add(test_key)
                                all_tests.append(test)
                    
                    print(f"  Filtered {len(filtered_tests)} tests that mention {test_plan_key}")
                    print(f"  Total unique tests: {len(all_test_ids)}")
                    
                except Exception as e2:
                    print(f"  [ERROR] {e2}")
                    break
                
                break
            else:
                print(f"  [ERROR] {e}")
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
    print("The API is still limited to 100 results per query.")
    print("This is a known limitation of Jira Cloud API.")
    print()
    print("Possible solutions:")
    print("  1. Export test plan from Jira UI")
    print("  2. Use Jira export feature")
    print("  3. Contact Jira support about API limits")
    print("  4. Use multiple queries with different filters")
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
output_file = Path("docs/04_testing/xray_mapping/TEST_PLAN_PZ14024_FORCED_PAGINATION.txt")
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"Test Plan: PZ-14024\n")
    f.write(f"Total Tests: {len(test_ids)}\n")
    f.write(f"Query: {jql}\n")
    f.write(f"Source: Forced pagination\n")
    f.write(f"\n")
    f.write(f"All Test IDs:\n")
    for test_id in test_ids:
        f.write(f"{test_id}\n")

print(f"Results saved to: {output_file}")

client.close()

