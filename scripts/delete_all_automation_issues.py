"""
Delete All Automation-Created Issues
=====================================

This script finds and deletes all Jira issues created by automation:
1. Tests with "Infrastructure -" prefix in summary
2. Tests with Test Type = "Automation" (customfield_10951)
3. Stories with labels "backend", "automation", "focus-server"
4. Any issues with summary starting with "Infrastructure -"

Requirements:
- ATLASSIAN_API_TOKEN environment variable must be set
"""

import sys
import os
from pathlib import Path

# Check for API token
if not os.environ.get('ATLASSIAN_API_TOKEN'):
    print("=" * 80)
    print("ERROR: ATLASSIAN_API_TOKEN environment variable is not set!")
    print("=" * 80)
    print("\nPlease set the API token before running this script:")
    print("\nWindows PowerShell:")
    print('  $env:ATLASSIAN_API_TOKEN = "your-api-token-here"')
    print("\nLinux/Mac:")
    print('  export ATLASSIAN_API_TOKEN="your-api-token-here"')
    print("\nThen run the script again.")
    sys.exit(1)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Remove scripts directory from path to avoid conflicts
scripts_dir = str(project_root / "scripts")
if scripts_dir in sys.path:
    sys.path.remove(scripts_dir)

from external.jira.jira_agent import JiraAgent

# Initialize agent
try:
    jira_agent = JiraAgent()
except Exception as e:
    print("=" * 80)
    print("ERROR: Failed to connect to Jira!")
    print("=" * 80)
    print(f"\nError: {e}")
    print("\nPlease check:")
    print("1. ATLASSIAN_API_TOKEN environment variable is set correctly")
    print("2. The API token is valid and has permissions to access Jira")
    print("3. Your network connection is working")
    sys.exit(1)

print("=" * 80)
print("DELETING ALL AUTOMATION-CREATED ISSUES")
print("=" * 80)
print()

all_issues_to_delete = []
deleted_count = 0
failed_count = 0

# 1. Find Tests with "Infrastructure -" prefix
print("Searching for Tests with 'Infrastructure -' prefix...")
jql1 = 'project = PZ AND summary ~ "Infrastructure -" AND issuetype = Test'
issues1 = jira_agent.search(jql=jql1, max_results=1000)
print(f"Found {len(issues1)} tests with 'Infrastructure -' prefix")
all_issues_to_delete.extend(issues1)

# 2. Find Tests with Test Type = "Automation"
print("\nSearching for Tests with Test Type = 'Automation'...")
jql2 = 'project = PZ AND issuetype = Test AND "Test Type" = Automation'
try:
    issues2 = jira_agent.search(jql=jql2, max_results=1000)
    print(f"Found {len(issues2)} tests with Test Type = 'Automation'")
    all_issues_to_delete.extend(issues2)
except Exception as e:
    print(f"Could not search by Test Type (may need different field name): {e}")
    # Try alternative: search by custom field ID
    try:
        jql2_alt = 'project = PZ AND issuetype = Test AND customfield_10951 = Automation'
        issues2 = jira_agent.search(jql=jql2_alt, max_results=1000)
        print(f"Found {len(issues2)} tests with Test Type = 'Automation' (alternative query)")
        all_issues_to_delete.extend(issues2)
    except Exception as e2:
        print(f"Alternative query also failed: {e2}")

# 3. Find Stories with automation labels
print("\nSearching for Stories with automation labels...")
jql3 = 'project = PZ AND issuetype = Story AND labels in (automation, backend, "focus-server")'
issues3 = jira_agent.search(jql=jql3, max_results=1000)
print(f"Found {len(issues3)} stories with automation labels")
all_issues_to_delete.extend(issues3)

# 4. Find any issues with "Infrastructure -" prefix (catch-all)
print("\nSearching for any issues with 'Infrastructure -' prefix...")
jql4 = 'project = PZ AND summary ~ "Infrastructure -"'
issues4 = jira_agent.search(jql=jql4, max_results=1000)
print(f"Found {len(issues4)} issues with 'Infrastructure -' prefix")
all_issues_to_delete.extend(issues4)

# Remove duplicates (based on issue key)
unique_issues = {}
for issue in all_issues_to_delete:
    key = issue.get('key')
    if key:
        unique_issues[key] = issue

issues_to_delete = list(unique_issues.values())

print(f"\n{'=' * 80}")
print(f"Total unique issues to delete: {len(issues_to_delete)}")
print(f"{'=' * 80}\n")

# Show list of issues to delete
if issues_to_delete:
    print("Issues to delete:")
    for issue in issues_to_delete[:20]:  # Show first 20
        print(f"  - {issue.get('key')}: {issue.get('summary', 'N/A')[:60]}")
    if len(issues_to_delete) > 20:
        print(f"  ... and {len(issues_to_delete) - 20} more issues")
    print()

# Confirm deletion
response = input("Do you want to proceed with deletion? (yes/no): ")
if response.lower() != 'yes':
    print("Deletion cancelled.")
    sys.exit(0)

print("\nStarting deletion...")
print()

# Delete all issues
for issue in issues_to_delete:
    issue_key = issue.get('key')
    summary = issue.get('summary', 'N/A')
    
    try:
        # Delete the issue
        jira_agent.client.jira.delete_issue(issue_key)
        deleted_count += 1
        if deleted_count % 10 == 0:
            print(f"Deleted {deleted_count}/{len(issues_to_delete)} issues...")
    except Exception as e:
        failed_count += 1
        error_msg = str(e)
        print(f"[FAILED] {issue_key}: {error_msg[:100]}")

print(f"\n{'=' * 80}")
print("Summary:")
print(f"  Total issues found: {len(issues_to_delete)}")
print(f"  Successfully deleted: {deleted_count}")
print(f"  Failed: {failed_count}")
print(f"{'=' * 80}")

