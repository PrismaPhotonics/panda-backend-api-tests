#!/usr/bin/env python3
"""Script to find valid Found by field values from existing bugs."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

def main():
    """Find valid Found by values from existing bugs."""
    client = JiraClient()
    
    # Search for recent bugs
    print("Searching for recent bugs to find Found by values...")
    jql = "project = PZ AND issuetype = Bug ORDER BY created DESC"
    issues = client.search_issues(jql, max_results=10)
    
    print(f"\nFound {len(issues)} recent bugs")
    print("=" * 80)
    
    found_by_values = set()
    
    for issue_key in [issue['key'] for issue in issues[:5]]:  # Check first 5
        try:
            issue_obj = client.jira.issue(issue_key)
            # Try to get customfield_10038
            if hasattr(issue_obj.fields, 'customfield_10038'):
                found_by = issue_obj.fields.customfield_10038
                if found_by:
                    found_by_values.add(found_by.value if hasattr(found_by, 'value') else str(found_by))
                    print(f"{issue_key}: Found by = {found_by}")
        except Exception as e:
            print(f"Error checking {issue_key}: {e}")
    
    print("\n" + "=" * 80)
    print("Valid Found by values found:")
    print("=" * 80)
    for value in sorted(found_by_values):
        print(f"  - {value}")
    
    # Try common values
    print("\n" + "=" * 80)
    print("Trying common values:")
    print("=" * 80)
    common_values = ["QA", "QA Team", "Automation", "Manual Testing", "Roy Avrahami", "roy.avrahami"]
    for value in common_values:
        print(f"  - {value}")
    
    client.close()

if __name__ == "__main__":
    main()

