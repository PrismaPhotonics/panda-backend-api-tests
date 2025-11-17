"""Analyze Test Plan structure to understand how tests are linked"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

client = JiraClient()

test_plan_key = "PZ-14024"

print("="*80)
print(f"Analyzing Test Plan: {test_plan_key}")
print("="*80)
print()

# Get Test Plan issue
test_plan = client.jira.issue(test_plan_key, expand='renderedFields')

print(f"Test Plan: {test_plan.key}")
print(f"Summary: {test_plan.fields.summary}")
print(f"Status: {test_plan.fields.status.name}")
print()

# Check all fields
print("="*80)
print("ALL FIELDS IN TEST PLAN:")
print("="*80)

for field_name in sorted(dir(test_plan.fields)):
    if not field_name.startswith('_') and not callable(getattr(test_plan.fields, field_name, None)):
        try:
            field_value = getattr(test_plan.fields, field_name)
            if field_value:
                value_str = str(field_value)
                if len(value_str) > 200:
                    value_str = value_str[:200] + "..."
                print(f"  {field_name}: {value_str}")
        except:
            pass

print()
print("="*80)
print("CHECKING TEST PLAN LINKS:")
print("="*80)

# Check issue links
if hasattr(test_plan.fields, 'issuelinks'):
    links = test_plan.fields.issuelinks
    print(f"Issue Links: {len(links)}")
    for link in links[:10]:
        if hasattr(link, 'outwardIssue'):
            print(f"  Outward: {link.outwardIssue.key} - {link.outwardIssue.fields.summary[:50]}")
        if hasattr(link, 'inwardIssue'):
            print(f"  Inward: {link.inwardIssue.key} - {link.inwardIssue.fields.summary[:50]}")
else:
    print("No issue links found")

print()
print("="*80)
print("CHECKING TESTS WITH 'Test Plan' FIELD:")
print("="*80)

# Get tests with Test Plan field
jql = 'project = PZ AND issuetype = Test AND "Test Plan" = PZ-14024'
tests = client.jira.search_issues(jql, maxResults=1000)

print(f"Found {len(tests)} tests with 'Test Plan' field = PZ-14024")
print()

# Check a few tests to see how they're linked
print("Checking first 5 tests to see Test Plan field:")
for test in tests[:5]:
    print(f"\n  {test.key}: {test.fields.summary[:50]}")
    # Try to find Test Plan field
    for field_name in dir(test.fields):
        if 'test' in field_name.lower() and 'plan' in field_name.lower():
            try:
                field_value = getattr(test.fields, field_name)
                if field_value:
                    print(f"    {field_name}: {field_value}")
            except:
                pass

print()
print("="*80)
print("SUMMARY")
print("="*80)
print(f"Test Plan: {test_plan.key}")
print(f"Tests with 'Test Plan' field = PZ-14024: {len(tests)}")
print("="*80)

client.close()

