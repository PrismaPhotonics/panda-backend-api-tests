"""Check different JQL queries for Test Plan PZ-14024"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

# Query 1: Test Plan field
jql1 = 'project = PZ AND issuetype = Test AND "Test Plan" = PZ-14024'
print(f"Query 1: {jql1}")
tests1 = client.jira.search_issues(jql1, maxResults=1000)
print(f"Results: {len(tests1)} tests\n")

# Query 2: Text search
jql2 = 'project = PZ AND issuetype = Test AND text ~ "PZ-14024"'
print(f"Query 2: {jql2}")
tests2 = client.jira.search_issues(jql2, maxResults=1000)
print(f"Results: {len(tests2)} tests\n")

# Compare
print("="*80)
print("COMPARISON")
print("="*80)
print(f"Query 1 (Test Plan field): {len(tests1)} tests")
print(f"Query 2 (text search): {len(tests2)} tests")

if len(tests1) != len(tests2):
    print(f"\n⚠️ DIFFERENCE: {abs(len(tests1) - len(tests2))} tests")
    
    # Find differences
    keys1 = {t.key for t in tests1}
    keys2 = {t.key for t in tests2}
    
    only_in_1 = keys1 - keys2
    only_in_2 = keys2 - keys1
    
    if only_in_1:
        print(f"\nTests only in Query 1 ({len(only_in_1)}):")
        for key in sorted(list(only_in_1))[:10]:
            print(f"  - {key}")
        if len(only_in_1) > 10:
            print(f"  ... and {len(only_in_1) - 10} more")
    
    if only_in_2:
        print(f"\nTests only in Query 2 ({len(only_in_2)}):")
        for key in sorted(list(only_in_2))[:10]:
            print(f"  - {key}")
        if len(only_in_2) > 10:
            print(f"  ... and {len(only_in_2) - 10} more")

print("\nFirst 10 tests from Query 1:")
for t in tests1[:10]:
    print(f"  {t.key}: {t.fields.summary[:60]}")

print("\nFirst 10 tests from Query 2:")
for t in tests2[:10]:
    print(f"  {t.key}: {t.fields.summary[:60]}")

client.close()

