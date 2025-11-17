"""
Analyze Epic Stories Status
============================

Analyzes all Stories in Epic PZ-14221 and determines which can be marked as "Closed"
(fully implemented) and which should be "Working" (partially implemented).

Author: QA Automation Architect
Date: 2025-11-04
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Set

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


def find_test_files_for_xray_test(xray_test_key: str, tests_dir: Path) -> List[str]:
    """Find test files with Xray marker for test key."""
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
        xray_tests.add(f"PZ-{match}")
    
    return xray_tests


def get_all_epic_stories():
    """Get all Stories linked to Epic."""
    jql = f'"Epic Link" = {EPIC_KEY} AND type = Story'
    stories = client.search_issues(jql, max_results=500)
    
    # Also get Stories that might be linked differently
    jql2 = f'project = PZ AND "Epic Link" = {EPIC_KEY}'
    stories2 = client.search_issues(jql2, max_results=500)
    
    # Combine and remove duplicates
    all_stories = {}
    for story in stories + stories2:
        if story['key'] not in all_stories:
            all_stories[story['key']] = story
    
    return list(all_stories.values())


def get_story_tasks(story_key: str) -> List[Dict[str, Any]]:
    """Get all Tasks/Sub-tasks for a Story."""
    jql = f"parent = {story_key}"
    tasks = client.search_issues(jql, max_results=100)
    return tasks


def analyze_story_implementation(story: Dict[str, Any], tests_dir: Path) -> Dict[str, Any]:
    """Analyze Story implementation status."""
    story_key = story['key']
    story_summary = story.get('summary', '')
    story_description = story.get('description', '')
    
    # Get all Xray tests mentioned in Story description
    story_xray_tests = extract_xray_tests_from_description(story_description)
    
    # Get all Tasks
    tasks = get_story_tasks(story_key)
    
    # Analyze each Task
    task_analysis = []
    total_xray_tests = set()
    implemented_xray_tests = set()
    
    for task in tasks:
        task_key = task['key']
        task_summary = task.get('summary', '')
        task_description = task.get('description', '')
        
        # Get Xray tests from Task description
        task_xray_tests = extract_xray_tests_from_description(task_description)
        total_xray_tests.update(task_xray_tests)
        
        # Check implementation for each Xray test
        task_implemented_tests = set()
        task_not_implemented_tests = set()
        
        for xray_test in task_xray_tests:
            test_files = find_test_files_for_xray_test(xray_test, tests_dir)
            if test_files:
                implemented_xray_tests.add(xray_test)
                task_implemented_tests.add(xray_test)
            else:
                task_not_implemented_tests.add(xray_test)
        
        task_analysis.append({
            'key': task_key,
            'summary': task_summary,
            'total_tests': len(task_xray_tests),
            'implemented_tests': len(task_implemented_tests),
            'not_implemented_tests': len(task_not_implemented_tests),
            'implemented_test_keys': list(task_implemented_tests),
            'not_implemented_test_keys': list(task_not_implemented_tests)
        })
    
    # Also check Story-level Xray tests
    story_implemented_tests = set()
    story_not_implemented_tests = set()
    
    for xray_test in story_xray_tests:
        test_files = find_test_files_for_xray_test(xray_test, tests_dir)
        if test_files:
            implemented_xray_tests.add(xray_test)
            story_implemented_tests.add(xray_test)
        else:
            story_not_implemented_tests.add(xray_test)
    
    total_xray_tests.update(story_xray_tests)
    
    # Calculate overall status
    total_tests_count = len(total_xray_tests)
    implemented_tests_count = len(implemented_xray_tests)
    implementation_percentage = (implemented_tests_count / total_tests_count * 100) if total_tests_count > 0 else 0
    
    # Determine status
    if total_tests_count == 0:
        status = "UNKNOWN"  # No Xray tests found in description
    elif implemented_tests_count == total_tests_count:
        status = "CLOSED"  # All tests implemented
    elif implemented_tests_count > 0:
        status = "WORKING"  # Partially implemented
    else:
        status = "TO_DO"  # Not implemented
    
    return {
        'story_key': story_key,
        'story_summary': story_summary,
        'story_status': story.get('status', 'Unknown'),
        'total_tests': total_tests_count,
        'implemented_tests': implemented_tests_count,
        'not_implemented_tests': total_tests_count - implemented_tests_count,
        'implementation_percentage': implementation_percentage,
        'status': status,
        'tasks': task_analysis,
        'story_xray_tests': list(story_xray_tests),
        'all_xray_tests': list(total_xray_tests),
        'implemented_xray_tests': list(implemented_xray_tests),
        'not_implemented_xray_tests': list(total_xray_tests - implemented_xray_tests)
    }


def main():
    """Main execution."""
    print("=" * 100)
    print("ANALYZING EPIC STORIES STATUS - PZ-14221")
    print("=" * 100)
    print()
    
    # Get all Stories
    print("Fetching Stories from Epic...")
    stories = get_all_epic_stories()
    print(f"Found {len(stories)} Stories\n")
    
    # Analyze each Story
    tests_dir = Path(__file__).parent.parent.parent / 'tests'
    
    analysis_results = []
    
    for story in stories:
        print(f"Analyzing: {story['key']} - {story.get('summary', 'N/A')}")
        analysis = analyze_story_implementation(story, tests_dir)
        analysis_results.append(analysis)
        print(f"  Status: {analysis['status']} ({analysis['implementation_percentage']:.1f}% implemented)")
        print()
    
    # Group by status
    stories_to_close = [a for a in analysis_results if a['status'] == 'CLOSED']
    stories_to_working = [a for a in analysis_results if a['status'] == 'WORKING']
    stories_to_do = [a for a in analysis_results if a['status'] == 'TO_DO']
    stories_unknown = [a for a in analysis_results if a['status'] == 'UNKNOWN']
    
    # Print summary
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print()
    print(f"Total Stories: {len(analysis_results)}")
    print(f"  ✅ Can be CLOSED: {len(stories_to_close)}")
    print(f"  🔄 Should be WORKING: {len(stories_to_working)}")
    print(f"  📋 Should be TO DO: {len(stories_to_do)}")
    print(f"  ❓ UNKNOWN (no Xray tests found): {len(stories_unknown)}")
    print()
    
    # Print Stories to Close
    if stories_to_close:
        print("=" * 100)
        print("STORIES TO CLOSE (All tests implemented)")
        print("=" * 100)
        print()
        for story in stories_to_close:
            print(f"✅ {story['story_key']}: {story['story_summary']}")
            print(f"   Current Status: {story['story_status']}")
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
            print(f"   Current Status: {story['story_status']}")
            print(f"   Tests: {story['implemented_tests']}/{story['total_tests']} implemented ({story['implementation_percentage']:.1f}%)")
            if story['not_implemented_xray_tests']:
                print(f"   Missing Tests: {', '.join(story['not_implemented_xray_tests'][:10])}")
                if len(story['not_implemented_xray_tests']) > 10:
                    print(f"   ... and {len(story['not_implemented_xray_tests']) - 10} more")
            print(f"   URL: https://prismaphotonics.atlassian.net/browse/{story['story_key']}")
            print()
    
    # Print Stories to DO
    if stories_to_do:
        print("=" * 100)
        print("STORIES TO DO (Not implemented)")
        print("=" * 100)
        print()
        for story in stories_to_do:
            print(f"📋 {story['story_key']}: {story['story_summary']}")
            print(f"   Current Status: {story['story_status']}")
            print(f"   Tests: 0/{story['total_tests']} implemented")
            print(f"   URL: https://prismaphotonics.atlassian.net/browse/{story['story_key']}")
            print()
    
    # Print Unknown Stories
    if stories_unknown:
        print("=" * 100)
        print("STORIES WITH UNKNOWN STATUS (No Xray tests found in description)")
        print("=" * 100)
        print()
        for story in stories_unknown:
            print(f"❓ {story['story_key']}: {story['story_summary']}")
            print(f"   Current Status: {story['story_status']}")
            print(f"   Note: No Xray test keys found in Story/Task descriptions")
            print(f"   URL: https://prismaphotonics.atlassian.net/browse/{story['story_key']}")
            print()
    
    # Create detailed report
    report_lines = []
    report_lines.append("# Epic Stories Status Analysis - PZ-14221")
    report_lines.append(f"**Date:** 2025-11-04\n")
    report_lines.append(f"## Summary\n")
    report_lines.append(f"- Total Stories: {len(analysis_results)}")
    report_lines.append(f"- ✅ Can be CLOSED: {len(stories_to_close)}")
    report_lines.append(f"- 🔄 Should be WORKING: {len(stories_to_working)}")
    report_lines.append(f"- 📋 Should be TO DO: {len(stories_to_do)}")
    report_lines.append(f"- ❓ UNKNOWN: {len(stories_unknown)}\n")
    
    if stories_to_close:
        report_lines.append("## Stories to CLOSE\n")
        for story in stories_to_close:
            report_lines.append(f"### {story['story_key']}: {story['story_summary']}")
            report_lines.append(f"- **Current Status:** {story['story_status']}")
            report_lines.append(f"- **Tests:** {story['implemented_tests']}/{story['total_tests']} implemented (100%)")
            report_lines.append(f"- **URL:** https://prismaphotonics.atlassian.net/browse/{story['story_key']}\n")
    
    if stories_to_working:
        report_lines.append("## Stories to WORKING\n")
        for story in stories_to_working:
            report_lines.append(f"### {story['story_key']}: {story['story_summary']}")
            report_lines.append(f"- **Current Status:** {story['story_status']}")
            report_lines.append(f"- **Tests:** {story['implemented_tests']}/{story['total_tests']} implemented ({story['implementation_percentage']:.1f}%)")
            if story['not_implemented_xray_tests']:
                report_lines.append(f"- **Missing Tests:** {', '.join(story['not_implemented_xray_tests'])}")
            report_lines.append(f"- **URL:** https://prismaphotonics.atlassian.net/browse/{story['story_key']}\n")
    
    # Save report
    report_path = project_root / 'docs' / '06_project_management' / 'jira' / 'EPIC_STORIES_STATUS_ANALYSIS.md'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"\n✅ Detailed report saved to: {report_path}")
    print("\n✅ Done!")


if __name__ == '__main__':
    main()

