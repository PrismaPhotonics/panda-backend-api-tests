"""Get ALL 237 tests with proper pagination - force pagination"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print("Getting ALL 237 tests with FORCED pagination")
print("="*80)
print()

# Query: Text search
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Force pagination - try to get all pages even if API says total=100
all_tests = []
all_test_ids = set()
start_at = 0
max_results = 50  # Use smaller page size to force pagination
page = 1
last_total = None

print("="*80)
print("FORCED PAGINATION - Getting all pages")
print("="*80)
print()

while True:
    print(f"Page {page}: Fetching results {start_at} to {start_at + max_results}...")
    
    try:
        results = client.jira.search_issues(
            jql, 
            startAt=start_at, 
            maxResults=max_results
        )
        
        batch = list(results)
        
        print(f"  Got {len(batch)} tests")
        print(f"  API says total: {results.total}")
        print(f"  Is Last: {results.isLast}")
        
        # Check if total changed
        if last_total is not None and results.total != last_total:
            print(f"  [INFO] Total changed from {last_total} to {results.total}!")
        last_total = results.total
        
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
        
        # Safety check - but allow more pages
        if page > 20:
            print(f"  [WARNING] Stopped after 20 pages (safety limit)")
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
print(f"Total tests in list: {len(all_tests)}")
print()

if len(all_test_ids) < 237:
    print(f"[WARNING] Got {len(all_test_ids)} tests but expected 237!")
    print()
    print("Trying alternative approach: Get all tests and filter...")
    print()
    
    # Alternative: Get ALL tests in project and filter
    print("Getting ALL tests in project PZ...")
    all_project_tests = []
    start_at = 0
    max_results = 100
    page = 1
    
    while True:
        print(f"Page {page}: Fetching all tests {start_at} to {start_at + max_results}...")
        try:
            results = client.jira.search_issues(
                'project = PZ AND issuetype = Test',
                startAt=start_at,
                maxResults=max_results
            )
            
            batch = list(results)
            all_project_tests.extend(batch)
            
            print(f"  Got {len(batch)} tests (total: {len(all_project_tests)}, API says: {results.total})")
            
            if len(batch) == 0 or results.isLast or len(all_project_tests) >= results.total:
                break
            
            start_at += len(batch)
            page += 1
            
            if page > 10:
                print(f"  [WARNING] Stopped after 10 pages")
                break
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            break
    
    print()
    print(f"Total tests in project: {len(all_project_tests)}")
    print()
    
    # Filter tests that mention PZ-14024
    print("Filtering tests that mention PZ-14024...")
    filtered_tests = []
    for test in all_project_tests:
        # Check all text fields
        summary = test.fields.summary or ""
        description = getattr(test.fields, 'description', None) or ""
        description_str = str(description) if description else ""
        
        # Check if test mentions PZ-14024
        if test_plan_key in summary or test_plan_key in description_str:
            filtered_tests.append(test)
        
        # Also check custom fields
        for field_name in dir(test.fields):
            if not field_name.startswith('_') and 'test' in field_name.lower() and 'plan' in field_name.lower():
                try:
                    field_value = getattr(test.fields, field_name)
                    if field_value and test_plan_key in str(field_value):
                        if test not in filtered_tests:
                            filtered_tests.append(test)
                except:
                    pass
    
    print(f"Filtered tests: {len(filtered_tests)}")
    print()
    
    # Add to all_tests
    for test in filtered_tests:
        if test.key not in all_test_ids:
            all_tests.append(test)
            all_test_ids.add(test.key)
    
    print(f"Total unique tests after filtering: {len(all_test_ids)}")
else:
    print(f"[SUCCESS] Got all {len(all_test_ids)} tests!")

print()
print("="*80)
print("ALL TEST IDs (sorted):")
print("="*80)

test_ids = sorted([t.key for t in all_tests])
for i, test_id in enumerate(test_ids, 1):
    print(f"{i:3}. {test_id}")

print()
print(f"Total: {len(test_ids)} tests")

client.close()

