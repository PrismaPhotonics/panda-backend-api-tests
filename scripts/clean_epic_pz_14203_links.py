"""
Clean Epic PZ-14203 Links
==========================

Remove all child work items from Epic PZ-14203 except BE and FE automation epics.
"""

import sys
from pathlib import Path

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
be_epic_key = "PZ-14221"
fe_epic_key = "PZ-14220"

print("=" * 80)
print(f"Cleaning Epic {epic_key} Links")
print("=" * 80)
print(f"Keeping only: {be_epic_key} and {fe_epic_key}")
print()

# Get all issues linked to this epic
jql = f'"Epic Link" = {epic_key}'
linked_issues = jira_agent.search(jql=jql, max_results=500)

print(f"Found {len(linked_issues)} issues linked to {epic_key}\n")

# Find Epic Link field
epic_link_field = None
try:
    fields = jira_agent.client.jira.fields()
    for field in fields:
        if field['name'].lower() == 'epic link' or field['id'] == 'customfield_10014':
            epic_link_field = field['id']
            print(f"Found Epic Link field: {epic_link_field}")
            break
except:
    epic_link_field = 'customfield_10014'  # Fallback

if not epic_link_field:
    epic_link_field = 'customfield_10014'

# Separate issues to keep and remove
to_remove = []
to_keep = []

for issue in linked_issues:
    issue_key = issue.get('key', '')
    issue_type = issue.get('issue_type', '').lower()
    summary = issue.get('summary', '')
    
    # Keep only BE and FE epics
    if issue_key == be_epic_key or issue_key == fe_epic_key:
        to_keep.append(issue)
        print(f"[KEEP] {issue_key} - {summary}")
    else:
        to_remove.append(issue)
        print(f"[REMOVE] {issue_key} ({issue_type}) - {summary}")

print(f"\nSummary:")
print(f"  To keep: {len(to_keep)}")
print(f"  To remove: {len(to_remove)}")

# Remove Epic Link from issues that should not be linked
removed_count = 0
failed_count = 0

if to_remove:
    print(f"\nRemoving Epic Link from {len(to_remove)} issues...")
    
    for issue in to_remove:
        issue_key = issue.get('key', '')
        try:
            # Unlink by setting Epic Link to None
            jira_agent.client.update_issue(
                issue_key=issue_key,
                **{epic_link_field: None}
            )
            removed_count += 1
            print(f"  [OK] Removed Epic Link from {issue_key}")
        except Exception as e:
            failed_count += 1
            print(f"  [FAILED] Could not remove Epic Link from {issue_key}: {e}")
            # Try alternative method
            try:
                issue_obj = jira_agent.client.jira.issue(issue_key)
                for field_id in ['customfield_10014', 'customfield_10011']:
                    try:
                        issue_obj.update(fields={field_id: None})
                        removed_count += 1
                        failed_count -= 1
                        print(f"  [OK] Removed Epic Link from {issue_key} (alternative method)")
                        break
                    except:
                        continue
            except:
                pass

print(f"\n{'=' * 80}")
print(f"Summary:")
print(f"  Removed: {removed_count}")
print(f"  Failed: {failed_count}")
print(f"  Kept: {len(to_keep)}")
print(f"{'=' * 80}")

