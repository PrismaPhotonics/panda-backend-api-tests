"""
Count Open Bugs in PZ Project
=============================

Simple script to count open bugs in Jira PZ project.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

def main():
    """Count open bugs."""
    try:
        client = JiraClient()
        
        # Search for open bugs
        jql = "project = PZ AND issuetype = Bug AND status != Done AND status != Closed AND status != Resolved"
        bugs = client.search_issues(jql, max_results=1000)
        
        print(f"Total open bugs: {len(bugs)}")
        
        # Count by status
        status_count = {}
        for bug in bugs:
            status = bug['status']
            status_count[status] = status_count.get(status, 0) + 1
        
        print("\nBugs by status:")
        for status, count in sorted(status_count.items()):
            print(f"  {status}: {count}")
        
        # Count by priority
        priority_count = {}
        for bug in bugs:
            priority = bug['priority'] or 'Unassigned'
            priority_count[priority] = priority_count.get(priority, 0) + 1
        
        print("\nBugs by priority:")
        for priority, count in sorted(priority_count.items()):
            print(f"  {priority}: {count}")
        
        client.close()
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())

