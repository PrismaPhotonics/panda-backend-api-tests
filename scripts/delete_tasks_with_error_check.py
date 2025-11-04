"""
Delete Tasks with Error Checking
=================================

Delete tasks and show detailed errors.
"""

import sys
from pathlib import Path
from datetime import datetime

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
today = datetime.now().strftime('%Y-%m-%d')

print("=" * 80)
print("DELETING TASKS CREATED TODAY")
print("=" * 80)

# Get all stories in epic
jql = f'"Epic Link" = {epic_key} AND issuetype = Story'
stories = jira_agent.search(jql=jql, max_results=500)

tasks_to_delete = []

# Collect all subtasks created today
for story in stories:
    story_key = story.get('key')
    
    # Get all subtasks for this story
    subtasks_jql = f"parent = {story_key}"
    subtasks = jira_agent.search(jql=subtasks_jql, max_results=100)
    
    for subtask in subtasks:
        subtask_key = subtask.get('key')
        created = subtask.get('created', '')
        
        # Check if created today
        if created and today in created:
            tasks_to_delete.append(subtask_key)

print(f"Found {len(tasks_to_delete)} tasks to delete\n")

deleted_count = 0
failed_count = 0

# Delete all found tasks
for task_key in tasks_to_delete:
    try:
        # Try to delete
        issue = jira_agent.client.jira.issue(task_key)
        issue.delete()
        deleted_count += 1
        print(f"[OK] Deleted {task_key}")
    except Exception as e:
        failed_count += 1
        error_msg = str(e)
        print(f"[FAILED] {task_key}: {error_msg[:100]}")

print(f"\n{'=' * 80}")
print("Summary:")
print(f"  Tasks found: {len(tasks_to_delete)}")
print(f"  Deleted: {deleted_count}")
print(f"  Failed: {failed_count}")
print(f"{'=' * 80}")

