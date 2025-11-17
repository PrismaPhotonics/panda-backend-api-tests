"""Get ALL tests from Test Plan - no limits"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print(f"Getting ALL tests from Test Plan: {test_plan_key}")
print("="*80)
print()

# Query 1: Test Plan field (exact match)
jql1 = f'project = PZ AND issuetype = Test AND "Test Plan" = {test_plan_key}'
print(f"Query 1: {jql1}")
tests1 = client.jira.search_issues(jql1, maxResults=None)  # No limit
print(f"Results: {len(tests1)} tests")
print()

# Query 2: Text search (contains PZ-14024 anywhere)
jql2 = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_key}"'
print(f"Query 2: {jql2}")
tests2 = client.jira.search_issues(jql2, maxResults=None)  # No limit
print(f"Results: {len(tests2)} tests")
print()

print("="*80)
print("COMPARISON")
print("="*80)
print(f"Query 1 (Test Plan field): {len(tests1)} tests")
print(f"Query 2 (text search): {len(tests2)} tests")
print()

# Get all test IDs
keys1 = {t.key for t in tests1}
keys2 = {t.key for t in tests2}

print(f"Tests in Query 1: {len(keys1)}")
print(f"Tests in Query 2: {len(keys2)}")
print()

# Differences
only_in_1 = keys1 - keys2
only_in_2 = keys2 - keys1

if only_in_1:
    print(f"Tests only in Query 1 ({len(only_in_1)}):")
    for key in sorted(list(only_in_1))[:20]:
        print(f"  - {key}")
    if len(only_in_1) > 20:
        print(f"  ... and {len(only_in_1) - 20} more")

if only_in_2:
    print(f"\nTests only in Query 2 ({len(only_in_2)}):")
    for key in sorted(list(only_in_2))[:20]:
        print(f"  - {key}")
    if len(only_in_2) > 20:
        print(f"  ... and {len(only_in_2) - 20} more")

print()
print("="*80)
print("FIRST 20 TESTS FROM QUERY 2 (text search):")
print("="*80)
for i, test in enumerate(tests2[:20], 1):
    print(f"{i:3}. {test.key}: {test.fields.summary[:70]}")

print()
print("="*80)
print("LAST 20 TESTS FROM QUERY 2 (text search):")
print("="*80)
for i, test in enumerate(tests2[-20:], len(tests2)-19):
    print(f"{i:3}. {test.key}: {test.fields.summary[:70]}")

client.close()

