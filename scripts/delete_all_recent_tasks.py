"""
Delete All Recent Tasks Created in Last 10 Minutes
===================================================

Delete all tasks created in the last 10 minutes under Epic PZ-14220 stories.
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
cutoff_time = datetime.now() - timedelta(minutes=10)

print("=" * 80)
print("DELETING ALL TASKS CREATED IN LAST 10 MINUTES")
print("=" * 80)
print(f"Epic: {epic_key}")
print(f"Cutoff time: {cutoff_time}")
print()

# Get all stories in epic
jql = f'"Epic Link" = {epic_key} AND issuetype = Story'
stories = jira_agent.search(jql=jql, max_results=500)

print(f"Found {len(stories)} stories\n")

deleted_count = 0
failed_count = 0
tasks_to_delete = []

# Collect all subtasks created in last 10 minutes
for story in stories:
    story_key = story.get('key')
    
    # Get all subtasks for this story
    subtasks_jql = f"parent = {story_key}"
    subtasks = jira_agent.search(jql=subtasks_jql, max_results=100)
    
    for subtask in subtasks:
        subtask_key = subtask.get('key')
        created = subtask.get('created', '')
        
        # Check if created in last 10 minutes
        if created:
            try:
                # Parse ISO format datetime
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00').replace('+00:00', ''))
                if created_dt.replace(tzinfo=None) > cutoff_time:
                    tasks_to_delete.append({
                        'key': subtask_key,
                        'summary': subtask.get('summary', 'N/A'),
                        'story': story_key,
                        'created': created
                    })
            except:
                pass

print(f"Found {len(tasks_to_delete)} tasks created in last 10 minutes\n")

# Delete all found tasks
for task in tasks_to_delete:
    print(f"[DELETE] {task['key']} - Story: {task['story']}")
    try:
        # Get the issue object and delete it
        issue = jira_agent.client.jira.issue(task['key'])
        issue.delete()
        deleted_count += 1
        print(f"  [OK] Deleted {task['key']}")
    except Exception as e:
        failed_count += 1
        print(f"  [FAILED] Could not delete {task['key']}: {str(e)[:100]}")

print(f"\n{'=' * 80}")
print("Summary:")
print(f"  Tasks found: {len(tasks_to_delete)}")
print(f"  Deleted: {deleted_count}")
print(f"  Failed: {failed_count}")
print(f"{'=' * 80}")

