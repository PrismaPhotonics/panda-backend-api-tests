"""
Delete Recent Tasks for Epic PZ-14220
======================================

Delete all Sub-tasks that were just created under Stories in Epic PZ-14220.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

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

epic_key = "PZ-14220"

print("=" * 80)
print(f"Deleting Recent Tasks for Epic {epic_key}")
print("=" * 80)

# Get all stories in epic
jql = f'"Epic Link" = {epic_key} AND issuetype = Story'
stories = jira_agent.search(jql=jql, max_results=500)

print(f"Found {len(stories)} stories\n")

# Get current time (5 minutes ago to catch recent tasks)
cutoff_time = datetime.now() - timedelta(minutes=10)

deleted_count = 0
failed_count = 0

for story in stories:
    story_key = story.get('key')
    print(f"Checking Story: {story_key}")
    
    # Get all subtasks
    jql_subtasks = f"parent = {story_key}"
    subtasks = jira_agent.search(jql=jql_subtasks, max_results=100)
    
    print(f"  Found {len(subtasks)} subtasks")
    
    for subtask in subtasks:
        subtask_key = subtask.get('key')
        subtask_created = subtask.get('created', '')
        subtask_summary = subtask.get('summary', '')
        
        # Check if created recently (within last 10 minutes)
        try:
            if subtask_created:
                # Parse created time
                created_dt = datetime.fromisoformat(subtask_created.replace('Z', '+00:00'))
                if created_dt.tzinfo:
                    created_dt = created_dt.astimezone()
                    created_dt = created_dt.replace(tzinfo=None)
                
                # Check if recent (within last 10 minutes)
                if created_dt >= cutoff_time:
                    print(f"    [DELETE] {subtask_key} - {subtask_summary}")
                    try:
                        # Delete the issue
                        issue = jira_agent.client.jira.issue(subtask_key)
                        issue.delete()
                        deleted_count += 1
                        print(f"      [OK] Deleted {subtask_key}")
                    except Exception as e:
                        failed_count += 1
                        print(f"      [FAILED] Could not delete {subtask_key}: {e}")
                else:
                    print(f"    [SKIP] {subtask_key} - Not recent (created: {subtask_created})")
            else:
                # If no created time, check by description or summary pattern
                # Delete if it matches the pattern of tasks we created
                if any(keyword in subtask_summary.lower() for keyword in [
                    'setup test environment', 'implement test cases', 'add test data',
                    'execute and validate', 'identify error scenarios', 'validate',
                    'analyze requirements', 'implement test'
                ]):
                    print(f"    [DELETE] {subtask_key} - {subtask_summary} (matches pattern)")
                    try:
                        issue = jira_agent.client.jira.issue(subtask_key)
                        issue.delete()
                        deleted_count += 1
                        print(f"      [OK] Deleted {subtask_key}")
                    except Exception as e:
                        failed_count += 1
                        print(f"      [FAILED] Could not delete {subtask_key}: {e}")
                else:
                    print(f"    [SKIP] {subtask_key} - Doesn't match pattern")
        
        except Exception as e:
            print(f"    [ERROR] Could not process {subtask_key}: {e}")

print(f"\n{'=' * 80}")
print(f"Summary:")
print(f"  Deleted: {deleted_count}")
print(f"  Failed: {failed_count}")
print(f"{'=' * 80}")

