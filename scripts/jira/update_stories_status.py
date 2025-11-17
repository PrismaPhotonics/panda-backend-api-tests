"""
Update Stories Status Based on Analysis Results
================================================

Updates Stories status to "WORKING" or "TO DO" based on manual analysis results.
Supports both automatic analysis and manual status updates from analysis reports.

Author: QA Automation Architect
Date: 2025-11-04
Updated: 2025-11-05
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Set, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

# Configure UTF-8 for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

# Initialize client
client = JiraClient()
EPIC_KEY = "PZ-14221"

# Ignore these keys (they are Epic/Test Plan IDs, not test IDs)
IGNORE_KEYS = {"PZ-14221", "PZ-14024"}


def get_story_tasks(story_key: str) -> List[Dict[str, Any]]:
    """Get all Tasks/Sub-tasks for a Story.
    
    Args:
        story_key: Story key (e.g., "PZ-12345")
    
    Returns:
        List of Task dictionaries
    """
    try:
        jql = f"parent = {story_key}"
        tasks = client.search_issues(jql, max_results=100)
        return tasks
    except Exception as e:
        print(f"  ⚠️  Failed to get tasks for {story_key}: {e}")
        return []


def update_task_status(task_key: str, target_status: str, task_summary: str = "") -> bool:
    """Update task status with fallback to alternative status names.
    
    Args:
        task_key: Task key (e.g., "PZ-12345")
        target_status: Target status name
        task_summary: Task summary for logging
    
    Returns:
        True if successful, False otherwise
    """
    # Map target status to possible status names
    status_options = {
        "WORKING": ["In Progress", "WORKING", "Working", "In Development"],
        "TO DO": ["To Do", "TO DO", "ToDo", "Open", "Backlog"],
        "CLOSED": ["Done", "CLOSED", "Closed", "Resolved"]
    }
    
    # Get status options for target
    status_list = status_options.get(target_status, [target_status])
    
    for status_name in status_list:
        try:
            client.transition_issue(task_key, status_name)
            if task_summary:
                print(f"    ✅ Updated Task {task_key} ({task_summary[:40]}...) to {status_name}")
            else:
                print(f"    ✅ Updated Task {task_key} to {status_name}")
            return True
        except:
            continue
    
    # If all failed, return False
    if task_summary:
        print(f"    ❌ Failed to update Task {task_key} ({task_summary[:40]}...) to {target_status}")
    else:
        print(f"    ❌ Failed to update Task {task_key} to {target_status}")
    return False


def sync_story_status_with_tasks(story_key: str, tasks: List[Dict[str, Any]]) -> Optional[str]:
    """Determine Story status based on Tasks status.
    
    Logic:
    - If all tasks are CLOSED -> Story should be CLOSED
    - If some tasks are WORKING/CLOSED -> Story should be WORKING
    - If all tasks are TO DO -> Story should be TO DO
    
    Args:
        story_key: Story key
        tasks: List of Task dictionaries
    
    Returns:
        Recommended status for Story, or None if unclear
    """
    if not tasks:
        return None
    
    status_counts = {
        'CLOSED': 0,
        'WORKING': 0,
        'TO DO': 0
    }
    
    for task in tasks:
        task_status = task.get('status', 'Unknown')
        
        # Categorize task status
        if task_status in ["CLOSED", "Done", "Closed", "Resolved"]:
            status_counts['CLOSED'] += 1
        elif task_status in ["In Progress", "WORKING", "Working", "In Development"]:
            status_counts['WORKING'] += 1
        elif task_status in ["TO DO", "To Do", "ToDo", "Open", "Backlog"]:
            status_counts['TO DO'] += 1
    
    total = len(tasks)
    
    # If all tasks are CLOSED
    if status_counts['CLOSED'] == total:
        return "CLOSED"
    
    # If all tasks are TO DO
    if status_counts['TO DO'] == total:
        return "TO DO"
    
    # If there are any WORKING or CLOSED tasks
    if status_counts['WORKING'] > 0 or status_counts['CLOSED'] > 0:
        return "WORKING"
    
    return None


def update_story_tasks(story_key: str, story_target_status: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Update all Tasks/Sub-tasks for a Story based on Story target status.
    
    Args:
        story_key: Story key
        story_target_status: Target status for Story (WORKING or TO DO)
        tasks: List of Task dictionaries
    
    Returns:
        Dictionary with update results
    """
    if not tasks:
        return {
            'total': 0,
            'updated': 0,
            'skipped': 0,
            'errors': []
        }
    
    results = {
        'total': len(tasks),
        'updated': 0,
        'skipped': 0,
        'errors': []
    }
    
    print(f"  📋 Found {len(tasks)} Tasks/Sub-tasks for {story_key}")
    
    for task in tasks:
        task_key = task.get('key', '')
        task_status = task.get('status', 'Unknown')
        task_summary = task.get('summary', '')
        
        # Determine target status for task based on story target status
        if story_target_status == "WORKING":
            # If story is WORKING, move tasks from TO DO to WORKING
            # Keep tasks that are already WORKING or CLOSED
            if task_status in ["TO DO", "To Do", "ToDo", "Open", "Backlog"]:
                if update_task_status(task_key, "WORKING", task_summary):
                    results['updated'] += 1
                else:
                    results['errors'].append(f"Failed to update {task_key} to WORKING")
            elif task_status in ["CLOSED", "Done", "Closed", "Resolved"]:
                # Don't move CLOSED tasks back
                print(f"    ⏭️  Skipping Task {task_key} - already CLOSED")
                results['skipped'] += 1
            else:
                # Already in WORKING/In Progress
                print(f"    ✓ Task {task_key} already in {task_status}")
                results['skipped'] += 1
        
        elif story_target_status == "TO DO":
            # If story is TO DO, move tasks from WORKING/CLOSED to TO DO
            # But keep CLOSED tasks if they're truly done
            if task_status in ["CLOSED", "Done", "Closed", "Resolved"]:
                # Ask: should we move CLOSED tasks back to TO DO?
                # For now, we'll skip CLOSED tasks
                print(f"    ⏭️  Skipping Task {task_key} - already CLOSED (won't move back)")
                results['skipped'] += 1
            elif task_status not in ["TO DO", "To Do", "ToDo", "Open", "Backlog"]:
                # Move from WORKING/In Progress to TO DO
                if update_task_status(task_key, "TO DO", task_summary):
                    results['updated'] += 1
                else:
                    results['errors'].append(f"Failed to update {task_key} to TO DO")
            else:
                # Already in TO DO
                print(f"    ✓ Task {task_key} already in TO DO")
                results['skipped'] += 1
    
    return results

# Manual status updates based on analysis results (2025-11-05)
# Stories to change to WORKING (12 Stories)
STORIES_TO_WORKING = [
    "PZ-14595",  # API Endpoints Testing Framework (33/35 - 94.3%)
    "PZ-14589",  # API Endpoints Testing Framework (33/35 - 94.3%) - duplicate
    "PZ-14625",  # Calculations and E2E (15/17 - 88.2%)
    "PZ-14607",  # SingleChannel View (14/16 - 87.5%)
    "PZ-14609",  # Dynamic ROI Adjustment (13/15 - 86.7%)
    "PZ-14611",  # Data Quality Tests (10/12 - 83.3%)
    "PZ-14601",  # Historic Playback (8/10 - 80.0%)
    "PZ-14620",  # Infrastructure Tests (6/8 - 75.0%)
    "PZ-14604",  # Live Monitoring (4/6 - 66.7%)
    "PZ-14488",  # API Endpoint Tests (6/9 - 66.7%) - currently CLOSED
    "PZ-14616",  # Performance and Load Tests (4/7 - 57.1%)
    "PZ-14628",  # Stress and Edge Case Tests (1/3 - 33.3%)
]

# Stories to change to TO DO (3 Stories)
STORIES_TO_TODO = [
    "PZ-14504",  # Kubernetes Orchestration Tests (0/1 - 0%) - currently CLOSED
    "PZ-14280",  # Test Plan and Documentation (0/2 - 0%) - currently CLOSED
    "PZ-14274",  # gRPC Stream Validation Framework (0/2 - 0%) - currently CLOSED
]


def find_test_files_for_xray_test(xray_test_key: str, tests_dir: Path) -> List[str]:
    """Find test files with Xray marker for test key."""
    if xray_test_key in IGNORE_KEYS:
        return []  # Don't check Epic/Test Plan IDs
    
    test_files = []
    
    for test_file in tests_dir.rglob('test_*.py'):
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for Xray marker - handle both single and multiple test keys
                pattern = rf'@pytest\.mark\.xray\([^)]*["\']?{re.escape(xray_test_key)}["\']?[^)]*\)'
                if re.search(pattern, content):
                    rel_path = str(test_file.relative_to(tests_dir.parent))
                    test_files.append(rel_path)
        except:
            pass
    
    return test_files


def extract_xray_tests_from_description(description: str) -> Set[str]:
    """Extract Xray test keys from Story/Task description."""
    xray_tests = set()
    
    if not description:
        return xray_tests
    
    # Pattern: PZ-XXXXX (Xray test keys)
    pattern = r'PZ-(\d{5})'
    matches = re.findall(pattern, description)
    
    for match in matches:
        test_key = f"PZ-{match}"
        if test_key not in IGNORE_KEYS:  # Filter out Epic/Test Plan IDs
            xray_tests.add(test_key)
    
    return xray_tests


def analyze_story_implementation(story: Dict[str, Any], tests_dir: Path) -> Dict[str, Any]:
    """Analyze Story implementation status."""
    story_key = story['key']
    story_summary = story.get('summary', '')
    story_description = story.get('description', '')
    
    # Get all Xray tests mentioned in Story description
    story_xray_tests = extract_xray_tests_from_description(story_description)
    
    # Get all Tasks
    jql = f"parent = {story_key}"
    tasks = client.search_issues(jql, max_results=100)
    
    # Analyze each Task
    total_xray_tests = set()
    implemented_xray_tests = set()
    
    for task in tasks:
        task_description = task.get('description', '')
        task_xray_tests = extract_xray_tests_from_description(task_description)
        total_xray_tests.update(task_xray_tests)
        
        # Check implementation for each Xray test
        for xray_test in task_xray_tests:
            test_files = find_test_files_for_xray_test(xray_test, tests_dir)
            if test_files:
                implemented_xray_tests.add(xray_test)
    
    # Also check Story-level Xray tests
    for xray_test in story_xray_tests:
        test_files = find_test_files_for_xray_test(xray_test, tests_dir)
        if test_files:
            implemented_xray_tests.add(xray_test)
    
    total_xray_tests.update(story_xray_tests)
    
    # Calculate overall status
    total_tests_count = len(total_xray_tests)
    implemented_tests_count = len(implemented_xray_tests)
    implementation_percentage = (implemented_tests_count / total_tests_count * 100) if total_tests_count > 0 else 0
    
    # Determine status
    if total_tests_count == 0:
        status = "UNKNOWN"  # No Xray tests found in description
    elif implemented_tests_count == total_tests_count and total_tests_count > 0:
        status = "CLOSED"  # All tests implemented
    elif implemented_tests_count > 0:
        status = "WORKING"  # Partially implemented
    else:
        status = "TO_DO"  # Not implemented
    
    return {
        'story_key': story_key,
        'story_summary': story_summary,
        'current_status': story.get('status', 'Unknown'),
        'total_tests': total_tests_count,
        'implemented_tests': implemented_tests_count,
        'implementation_percentage': implementation_percentage,
        'recommended_status': status
    }


def update_stories_manual(auto_confirm: bool = False):
    """Update Stories status based on manual analysis results.
    
    Args:
        auto_confirm: If True, skip confirmation prompt and proceed automatically
    """
    print("=" * 100)
    print("MANUAL STATUS UPDATE - PZ-14221")
    print("=" * 100)
    print()
    
    print("Updating Stories based on manual analysis results...")
    print()
    
    stories_to_working_info = []
    stories_to_todo_info = []
    errors = []
    
    # Fetch Stories info for WORKING
    print("Fetching Stories to update to WORKING...")
    for story_key in STORIES_TO_WORKING:
        try:
            story = client.get_issue(story_key)
            current_status = story.get('status', 'Unknown')
            # Get tasks for this story
            tasks = get_story_tasks(story_key)
            stories_to_working_info.append({
                'story_key': story_key,
                'story_summary': story.get('summary', ''),
                'current_status': current_status,
                'tasks': tasks
            })
            print(f"  ✓ {story_key}: {story.get('summary', '')[:60]}... (Current: {current_status}, Tasks: {len(tasks)})")
        except Exception as e:
            print(f"  ✗ {story_key}: Failed to fetch - {e}")
            errors.append(f"Failed to fetch {story_key}: {e}")
    
    print()
    
    # Fetch Stories info for TO DO
    print("Fetching Stories to update to TO DO...")
    for story_key in STORIES_TO_TODO:
        try:
            story = client.get_issue(story_key)
            current_status = story.get('status', 'Unknown')
            # Get tasks for this story
            tasks = get_story_tasks(story_key)
            stories_to_todo_info.append({
                'story_key': story_key,
                'story_summary': story.get('summary', ''),
                'current_status': current_status,
                'tasks': tasks
            })
            print(f"  ✓ {story_key}: {story.get('summary', '')[:60]}... (Current: {current_status}, Tasks: {len(tasks)})")
        except Exception as e:
            print(f"  ✗ {story_key}: Failed to fetch - {e}")
            errors.append(f"Failed to fetch {story_key}: {e}")
    
    print()
    
    # Print summary
    print("=" * 100)
    print("STATUS UPDATE SUMMARY")
    print("=" * 100)
    print()
    print(f"Stories to update to WORKING: {len(stories_to_working_info)}")
    print(f"Stories to update to TO DO: {len(stories_to_todo_info)}")
    print()
    
    # Print Stories to WORKING
    if stories_to_working_info:
        print("=" * 100)
        print("STORIES TO UPDATE TO WORKING")
        print("=" * 100)
        print()
        for story in stories_to_working_info:
            print(f"🔄 {story['story_key']}: {story['story_summary']}")
            print(f"   Current: {story['current_status']} → Target: WORKING")
            print(f"   URL: https://prismaphotonics.atlassian.net/browse/{story['story_key']}")
            print()
    
    # Print Stories to TO DO
    if stories_to_todo_info:
        print("=" * 100)
        print("STORIES TO UPDATE TO TO DO")
        print("=" * 100)
        print()
        for story in stories_to_todo_info:
            print(f"📋 {story['story_key']}: {story['story_summary']}")
            print(f"   Current: {story['current_status']} → Target: TO DO")
            print(f"   URL: https://prismaphotonics.atlassian.net/browse/{story['story_key']}")
            print()
    
    # Ask for confirmation
    print("=" * 100)
    print("CONFIRMATION REQUIRED")
    print("=" * 100)
    print()
    print("⚠️  This script will update Story statuses in Jira.")
    print("   Please review the analysis above before proceeding.")
    print()
    print(f"   Stories to WORKING: {len(stories_to_working_info)}")
    print(f"   Stories to TO DO: {len(stories_to_todo_info)}")
    print()
    
    if not auto_confirm:
        response = input("Do you want to proceed with status updates? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("\n❌ Status update cancelled.")
            return
    else:
        print("⚠️  Auto-confirm mode: Proceeding with status updates...")
        print()
    
    # Update Stories and their Tasks
    print("\nUpdating Stories and their Tasks...\n")
    
    updated_working = 0
    updated_todo = 0
    tasks_updated_working = 0
    tasks_updated_todo = 0
    
    # Update to WORKING
    print("=" * 100)
    print("UPDATING STORIES TO WORKING")
    print("=" * 100)
    print()
    for story in stories_to_working_info:
        story_key = story['story_key']
        story_summary = story['story_summary']
        tasks = story.get('tasks', [])
        
        print(f"📝 Story: {story_key} - {story_summary[:60]}...")
        
        # First, update Tasks to WORKING
        if tasks:
            task_results = update_story_tasks(story_key, "WORKING", tasks)
            tasks_updated_working += task_results['updated']
            if task_results['errors']:
                errors.extend(task_results['errors'])
            
            # Verify Story status is synced with Tasks after update
            # (Tasks are updated first, so Story should reflect their state)
            recommended_status = sync_story_status_with_tasks(story_key, tasks)
            if recommended_status and recommended_status != "WORKING":
                print(f"  ⚠️  Note: Tasks suggest Story should be {recommended_status}, but updating to WORKING as requested")
        
        # Then, update Story status
        try:
            # Try different status names for WORKING
            status_updated = False
            status_used = None
            for status_name in ["In Progress", "WORKING", "Working", "In Development"]:
                try:
                    client.transition_issue(story_key, status_name)
                    status_used = status_name
                    status_updated = True
                    break
                except:
                    continue
            
            if status_updated:
                print(f"  ✅ Updated Story {story_key} to {status_used}")
                updated_working += 1
            else:
                raise Exception(f"Could not transition to any WORKING status")
        except Exception as e:
            error_msg = f"Failed to update {story_key}: {e}"
            print(f"  ❌ {error_msg}")
            errors.append(error_msg)
        
        print()
    
    # Update to TO DO
    print("=" * 100)
    print("UPDATING STORIES TO TO DO")
    print("=" * 100)
    print()
    for story in stories_to_todo_info:
        story_key = story['story_key']
        story_summary = story['story_summary']
        tasks = story.get('tasks', [])
        
        print(f"📝 Story: {story_key} - {story_summary[:60]}...")
        
        # First, update Tasks to TO DO
        if tasks:
            task_results = update_story_tasks(story_key, "TO DO", tasks)
            tasks_updated_todo += task_results['updated']
            if task_results['errors']:
                errors.extend(task_results['errors'])
            
            # Verify Story status is synced with Tasks after update
            # (Tasks are updated first, so Story should reflect their state)
            recommended_status = sync_story_status_with_tasks(story_key, tasks)
            if recommended_status and recommended_status != "TO DO":
                print(f"  ⚠️  Note: Tasks suggest Story should be {recommended_status}, but updating to TO DO as requested")
        
        # Then, update Story status
        try:
            # Try different status names for TO DO
            status_updated = False
            status_used = None
            for status_name in ["To Do", "TO DO", "ToDo", "Open", "Backlog"]:
                try:
                    client.transition_issue(story_key, status_name)
                    status_used = status_name
                    status_updated = True
                    break
                except:
                    continue
            
            if status_updated:
                print(f"  ✅ Updated Story {story_key} to {status_used}")
                updated_todo += 1
            else:
                raise Exception(f"Could not transition to any TO DO status")
        except Exception as e:
            error_msg = f"Failed to update {story_key}: {e}"
            print(f"  ❌ {error_msg}")
            errors.append(error_msg)
        
        print()
    
    # Final summary
    print("\n" + "=" * 100)
    print("UPDATE SUMMARY")
    print("=" * 100)
    print(f"\n📊 Stories:")
    print(f"  ✅ Successfully updated to WORKING: {updated_working}/{len(stories_to_working_info)}")
    print(f"  ✅ Successfully updated to TO DO: {updated_todo}/{len(stories_to_todo_info)}")
    print(f"\n📋 Tasks:")
    print(f"  ✅ Tasks updated to WORKING: {tasks_updated_working}")
    print(f"  ✅ Tasks updated to TO DO: {tasks_updated_todo}")
    
    if errors:
        print(f"\n❌ Errors: {len(errors)}")
        for error in errors:
            print(f"   - {error}")
    
    print("\n✅ Done!")


def main():
    """Main execution - supports both manual and automatic updates."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Update Stories status in Jira based on analysis results'
    )
    parser.add_argument(
        '--manual',
        action='store_true',
        help='Use manual status updates from predefined lists (STORIES_TO_WORKING, STORIES_TO_TODO)'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Use automatic analysis based on test implementation status'
    )
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Auto-confirm: Skip confirmation prompt and proceed with updates'
    )
    
    args = parser.parse_args()
    
    # Default to manual if no flag specified
    if not args.manual and not args.auto:
        args.manual = True
    
    if args.manual:
        update_stories_manual(auto_confirm=args.yes)
    elif args.auto:
        update_stories_automatic()


def update_stories_automatic():
    """Update Stories status based on automatic implementation analysis."""
    print("=" * 100)
    print("ANALYZING STORIES FOR STATUS UPDATE - PZ-14221")
    print("=" * 100)
    print()
    
    # Get all Stories
    print("Fetching Stories from Epic...")
    jql = f'"Epic Link" = {EPIC_KEY} AND type = Story'
    stories = client.search_issues(jql, max_results=500)
    print(f"Found {len(stories)} Stories\n")
    
    # Analyze each Story
    tests_dir = Path(__file__).parent.parent.parent / 'tests'
    
    stories_to_close = []
    stories_to_working = []
    stories_no_change = []
    
    print("Analyzing Stories...\n")
    
    for story in stories:
        analysis = analyze_story_implementation(story, tests_dir)
        
        story_key = analysis['story_key']
        current_status = analysis['current_status']
        recommended_status = analysis['recommended_status']
        
        print(f"{story_key}: {analysis['story_summary'][:60]}...")
        print(f"  Current: {current_status} | Recommended: {recommended_status}")
        print(f"  Tests: {analysis['implemented_tests']}/{analysis['total_tests']} ({analysis['implementation_percentage']:.1f}%)")
        
        # Determine action
        if recommended_status == "CLOSED" and current_status != "CLOSED":
            stories_to_close.append(analysis)
            print(f"  ✅ Action: Change to CLOSED")
        elif recommended_status == "WORKING" and current_status not in ["WORKING", "IN PROGRESS", "In Progress"]:
            stories_to_working.append(analysis)
            print(f"  🔄 Action: Change to WORKING")
        else:
            stories_no_change.append(analysis)
            print(f"  ⏭️  Action: No change needed")
        
        print()
    
    # Print summary
    print("=" * 100)
    print("STATUS UPDATE SUMMARY")
    print("=" * 100)
    print()
    print(f"Total Stories Analyzed: {len(stories)}")
    print(f"  ✅ Stories to CLOSE: {len(stories_to_close)}")
    print(f"  🔄 Stories to WORKING: {len(stories_to_working)}")
    print(f"  ⏭️  Stories - No change: {len(stories_no_change)}")
    print()
    
    # Print Stories to Close
    if stories_to_close:
        print("=" * 100)
        print("STORIES TO CLOSE (All tests implemented)")
        print("=" * 100)
        print()
        for story in stories_to_close:
            print(f"✅ {story['story_key']}: {story['story_summary']}")
            print(f"   Current: {story['current_status']} → Recommended: CLOSED")
            print(f"   Tests: {story['implemented_tests']}/{story['total_tests']} implemented (100%)")
            print(f"   URL: https://prismaphotonics.atlassian.net/browse/{story['story_key']}")
            print()
    
    # Print Stories to Working
    if stories_to_working:
        print("=" * 100)
        print("STORIES TO WORKING (Partially implemented)")
        print("=" * 100)
        print()
        for story in stories_to_working:
            print(f"🔄 {story['story_key']}: {story['story_summary']}")
            print(f"   Current: {story['current_status']} → Recommended: WORKING")
            print(f"   Tests: {story['implemented_tests']}/{story['total_tests']} implemented ({story['implementation_percentage']:.1f}%)")
            print(f"   URL: https://prismaphotonics.atlassian.net/browse/{story['story_key']}")
            print()
    
    # Ask for confirmation
    print("=" * 100)
    print("CONFIRMATION REQUIRED")
    print("=" * 100)
    print()
    print("⚠️  This script will update Story statuses in Jira.")
    print("   Please review the analysis above before proceeding.")
    print()
    print(f"   Stories to CLOSE: {len(stories_to_close)}")
    print(f"   Stories to WORKING: {len(stories_to_working)}")
    print()
    
    response = input("Do you want to proceed with status updates? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Status update cancelled.")
        return
    
    # Update Stories
    print("\nUpdating Stories...\n")
    
    updated_close = 0
    updated_working = 0
    errors = []
    
    for story in stories_to_close:
        try:
            # Try different status names for CLOSED
            status_updated = False
            for status_name in ["Done", "CLOSED", "Closed", "Resolved"]:
                try:
                    client.transition_issue(story['story_key'], status_name)
                    print(f"✅ Updated {story['story_key']} to {status_name}")
                    updated_close += 1
                    status_updated = True
                    break
                except:
                    continue
            
            if not status_updated:
                raise Exception(f"Could not transition to any CLOSED status")
        except Exception as e:
            error_msg = f"Failed to update {story['story_key']}: {e}"
            print(f"❌ {error_msg}")
            errors.append(error_msg)
    
    for story in stories_to_working:
        try:
            # Try different status names for WORKING
            status_updated = False
            for status_name in ["In Progress", "WORKING", "Working", "In Development"]:
                try:
                    client.transition_issue(story['story_key'], status_name)
                    print(f"✅ Updated {story['story_key']} to {status_name}")
                    updated_working += 1
                    status_updated = True
                    break
                except:
                    continue
            
            if not status_updated:
                raise Exception(f"Could not transition to any WORKING status")
        except Exception as e:
            error_msg = f"Failed to update {story['story_key']}: {e}"
            print(f"❌ {error_msg}")
            errors.append(error_msg)
    
    # Final summary
    print("\n" + "=" * 100)
    print("UPDATE SUMMARY")
    print("=" * 100)
    print(f"\n✅ Successfully updated to CLOSED: {updated_close}/{len(stories_to_close)}")
    print(f"✅ Successfully updated to WORKING: {updated_working}/{len(stories_to_working)}")
    
    if errors:
        print(f"\n❌ Errors: {len(errors)}")
        for error in errors:
            print(f"   - {error}")
    
    print("\n✅ Done!")


if __name__ == '__main__':
    main()

