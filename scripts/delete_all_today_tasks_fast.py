"""
Delete All Tasks Created Today - Fast Version
=============================================

Delete all tasks created today under Epic PZ-14220 stories.
No printing to avoid encoding issues.
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
print("DELETING ALL TASKS CREATED TODAY")
print("=" * 80)
print(f"Epic: {epic_key}")
print(f"Date: {today}")
print()

# Get all stories in epic
jql = f'"Epic Link" = {epic_key} AND issuetype = Story'
stories = jira_agent.search(jql=jql, max_results=500)

print(f"Found {len(stories)} stories")

deleted_count = 0
failed_count = 0
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

print(f"Found {len(tasks_to_delete)} tasks created today\n")

# Delete all found tasks
for task_key in tasks_to_delete:
    try:
        jira_agent.client.jira.delete_issue(task_key)
        deleted_count += 1
        if deleted_count % 10 == 0:
            print(f"Deleted {deleted_count} tasks...")
    except Exception as e:
        failed_count += 1

print(f"\n{'=' * 80}")
print("Summary:")
print(f"  Tasks found: {len(tasks_to_delete)}")
print(f"  Deleted: {deleted_count}")
print(f"  Failed: {failed_count}")
print(f"{'=' * 80}")

