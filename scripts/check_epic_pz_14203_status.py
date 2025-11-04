"""
Check Epic PZ-14203 Status
===========================

Check which epics are currently linked to PZ-14203.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Remove scripts directory from path to avoid conflicts
scripts_dir = str(project_root / "scripts")
if scripts_dir in sys.path:
    sys.path.remove(scripts_dir)

from external.jira.jira_agent import JiraAgent

# Initialize agent
jira_agent = JiraAgent()

epic_key = "PZ-14203"

print("=" * 80)
print(f"Checking Epic {epic_key} Links")
print("=" * 80)

# Get all issues linked to this epic
jql = f'"Epic Link" = {epic_key}'
linked_issues = jira_agent.search(jql=jql, max_results=500)

print(f"\nFound {len(linked_issues)} issues linked to {epic_key}\n")

epics = []
stories = []
other = []

for issue in linked_issues:
    issue_type = issue.get('issue_type', '').lower()
    key = issue.get('key', '')
    summary = issue.get('summary', '')
    
    if issue_type == 'epic':
        epics.append(issue)
        print(f"  Epic: {key} - {summary}")
    elif issue_type == 'story':
        stories.append(issue)
    else:
        other.append(issue)

print(f"\nSummary:")
print(f"  Epics: {len(epics)}")
print(f"  Stories: {len(stories)}")
print(f"  Other: {len(other)}")

if epics:
    print("\nEpics linked:")
    for epic in epics:
        print(f"  - {epic['key']}: {epic['summary']}")

print("\n" + "=" * 80)

