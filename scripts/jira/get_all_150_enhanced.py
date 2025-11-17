"""Get ALL 150 tests using enhanced_search_issues"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print("Getting ALL 150 tests using enhanced_search_issues")
print("="*80)
print()

# Query: Text search
jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query: {jql}")
print()

# Try enhanced_search_issues
print("Trying enhanced_search_issues...")
try:
    # Check if method exists
    if hasattr(client.jira, 'enhanced_search_issues'):
        print("  Method exists!")
        results = client.jira.enhanced_search_issues(jql, maxResults=200)
        print(f"  Got {len(results)} tests")
        print(f"  Total: {results.total if hasattr(results, 'total') else 'N/A'}")
    else:
        print("  Method does not exist, trying regular search_issues with maxResults=200...")
        results = client.jira.search_issues(jql, maxResults=200)
        print(f"  Got {len(results)} tests")
        print(f"  Total: {results.total}")
        
        # Try pagination
        all_tests = list(results)
        start_at = len(all_tests)
        
        while start_at < results.total and len(all_tests) < 200:
            print(f"  Fetching page starting at {start_at}...")
            page_results = client.jira.search_issues(jql, startAt=start_at, maxResults=200)
            page_tests = list(page_results)
            all_tests.extend(page_tests)
            print(f"    Got {len(page_tests)} tests (total so far: {len(all_tests)})")
            
            if len(page_tests) == 0:
                break
                
            start_at += len(page_tests)
        
        print(f"  [FINAL] Total tests: {len(all_tests)}")
        
        # Get all test IDs
        test_ids = sorted([t.key for t in all_tests])
        print()
        print("All test IDs (sorted):")
        for i, test_id in enumerate(test_ids, 1):
            print(f"{i:3}. {test_id}")
            
except Exception as e:
    print(f"  [ERROR] {e}")
    import traceback
    traceback.print_exc()

client.close()

