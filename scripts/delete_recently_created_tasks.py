"""
Delete Recently Created Tasks
=============================

Delete all tasks created recently under Epic PZ-14220.
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
print("DELETING RECENTLY CREATED TASKS")
print("=" * 80)
print(f"Epic: {epic_key}")
print(f"Time: {datetime.now()}")
print()

# Get all stories in epic
jql = f'"Epic Link" = {epic_key} AND issuetype = Story'
stories = jira_agent.search(jql=jql, max_results=500)

print(f"Found {len(stories)} stories\n")

# Get all subtasks created in the last hour
cutoff_time = datetime.now() - timedelta(hours=1)
deleted_count = 0
failed_count = 0

for story in stories:
    story_key = story.get('key')
    print(f"Checking subtasks for {story_key}...")
    
    # Get all subtasks for this story
    subtasks_jql = f"parent = {story_key}"
    subtasks = jira_agent.search(jql=subtasks_jql, max_results=100)
    
    for subtask in subtasks:
        subtask_key = subtask.get('key')
        created = subtask.get('created', '')
        
        # Check if created recently (last hour)
        try:
            if created:
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                if created_dt > cutoff_time:
                    print(f"  [DELETE] {subtask_key} - {subtask.get('summary', 'N/A')}")
                    try:
                        # Delete the issue
                        jira_agent.client.jira.delete_issue(subtask_key)
                        deleted_count += 1
                        print(f"    [OK] Deleted {subtask_key}")
                    except Exception as e:
                        failed_count += 1
                        print(f"    [FAILED] Could not delete {subtask_key}: {e}")
        except:
            # If we can't parse date, delete anyway if it looks like a new task
            # Check if summary contains common task patterns
            summary = subtask.get('summary', '').lower()
            if any(keyword in summary for keyword in ['setup test environment', 'implement test', 'validate', 'add test data']):
                print(f"  [DELETE] {subtask_key} - {subtask.get('summary', 'N/A')}")
                try:
                    jira_agent.client.jira.delete_issue(subtask_key)
                    deleted_count += 1
                    print(f"    [OK] Deleted {subtask_key}")
                except Exception as e:
                    failed_count += 1
                    print(f"    [FAILED] Could not delete {subtask_key}: {e}")

print(f"\n{'=' * 80}")
print("Summary:")
print(f"  Deleted: {deleted_count}")
print(f"  Failed: {failed_count}")
print(f"{'=' * 80}")

