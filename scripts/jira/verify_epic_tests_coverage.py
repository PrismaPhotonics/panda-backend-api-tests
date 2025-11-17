"""
Verify Epic Tests Coverage
==========================

Check if tests in CSV are already covered by Epic tickets or if they're already implemented.
"""

import sys
import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Set
import logging
import re

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from external.jira import JiraClient, JiraAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_test_files_for_xray_test(xray_test_key: str) -> List[str]:
    """
    Find test files that contain Xray markers for a specific test.
    
    Args:
        xray_test_key: Xray test key (e.g., "PZ-14101")
    
    Returns:
        List of test file paths
    """
    test_files = []
    tests_dir = Path(__file__).parent.parent.parent / 'tests'
    
    # Search for Xray markers
    for test_file in tests_dir.rglob('test_*.py'):
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for Xray marker
                pattern = rf'@pytest\.mark\.xray\(["\']?{re.escape(xray_test_key)}["\']?\)'
                if re.search(pattern, content):
                    rel_path = str(test_file.relative_to(tests_dir.parent))
                    test_files.append(rel_path)
        except Exception as e:
            logger.debug(f"Error reading {test_file}: {e}")
    
    return test_files


def main():
    """Verify coverage."""
    epic_key = "PZ-14221"
    csv_file = r"C:\Users\roy.avrahami\Downloads\Test plan (TS_Focus_Server_PZ-14024) by Roy Avrahami (Jira) (3).csv"
    
    client = JiraClient()
    
    print("=" * 100)
    print("VERIFICATION: Epic PZ-14221 vs Test Plan CSV")
    print("=" * 100)
    
    # Get Epic tickets
    jql_epic = f'"Epic Link" = {epic_key}'
    epic_tickets = client.search_issues(jql_epic, max_results=500)
    
    # Get all subtasks
    all_epic_tickets = []
    for ticket in epic_tickets:
        all_epic_tickets.append(ticket)
        try:
            subtasks_jql = f"parent = {ticket['key']}"
            subtasks = client.search_issues(subtasks_jql, max_results=100)
            all_epic_tickets.extend(subtasks)
        except:
            pass
    
    # Remove duplicates
    seen_keys = set()
    unique_epic_tickets = []
    for ticket in all_epic_tickets:
        if ticket['key'] not in seen_keys:
            seen_keys.add(ticket['key'])
            unique_epic_tickets.append(ticket)
    
    print(f"\nEpic tickets: {len(unique_epic_tickets)}")
    
    # Parse CSV
    csv_tests = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        sample = f.read(1024)
        f.seek(0)
        delimiter = ',' if ',' in sample and sample.count(',') > sample.count(';') else ';'
        reader = csv.DictReader(f, delimiter=delimiter)
        
        for row in reader:
            if not any(row.values()):
                continue
            issue_key = row.get('Issue key', '').strip()
            summary = row.get('Summary', '').strip()
            if issue_key:
                csv_tests.append({
                    'key': issue_key,
                    'summary': summary
                })
    
    print(f"CSV tests: {len(csv_tests)}")
    
    # Check each test
    print("\n" + "=" * 100)
    print("VERIFICATION RESULTS")
    print("=" * 100)
    
    results = {
        'tests_in_epic': [],
        'tests_implemented_no_task': [],
        'tests_not_implemented': [],
        'tests_with_task': []
    }
    
    for test in csv_tests:
        test_key = test['key']
        test_summary = test['summary']
        
        # Check if test is in Epic
        in_epic = test_key in {t['key'] for t in unique_epic_tickets}
        
        # Check if test is implemented in code
        test_files = find_test_files_for_xray_test(test_key)
        implemented = len(test_files) > 0
        
        # Find matching Epic ticket by summary/keywords
        matching_ticket = None
        test_keywords = set([w.lower() for w in test_summary.split() if len(w) > 3])
        
        for ticket in unique_epic_tickets:
            ticket_summary = ticket.get('summary', '').lower()
            ticket_keywords = set([w.lower() for w in ticket_summary.split() if len(w) > 3])
            
            if test_keywords and ticket_keywords:
                overlap = test_keywords.intersection(ticket_keywords)
                if len(overlap) >= 3:  # At least 3 keywords match
                    matching_ticket = ticket
                    break
        
        # Categorize
        if in_epic:
            results['tests_in_epic'].append({
                'test': test,
                'ticket': next(t for t in unique_epic_tickets if t['key'] == test_key)
            })
        elif matching_ticket:
            results['tests_with_task'].append({
                'test': test,
                'ticket': matching_ticket,
                'test_files': test_files
            })
        elif implemented:
            results['tests_implemented_no_task'].append({
                'test': test,
                'test_files': test_files
            })
        else:
            results['tests_not_implemented'].append({
                'test': test
            })
    
    # Print results
    print(f"\n✅ Tests in Epic: {len(results['tests_in_epic'])}")
    print(f"✅ Tests with matching task: {len(results['tests_with_task'])}")
    print(f"⚠️  Tests implemented but no task: {len(results['tests_implemented_no_task'])}")
    print(f"❌ Tests not implemented: {len(results['tests_not_implemented'])}")
    
    # Show tests implemented but no task
    if results['tests_implemented_no_task']:
        print("\n" + "=" * 100)
        print("TESTS IMPLEMENTED BUT NO TASK IN EPIC")
        print("=" * 100)
        print(f"\nFound {len(results['tests_implemented_no_task'])} tests that are already implemented in code")
        print("but don't have corresponding automation tasks in Epic PZ-14221:")
        
        for i, item in enumerate(results['tests_implemented_no_task'][:30], 1):
            test = item['test']
            test_files = item['test_files']
            print(f"\n{i}. {test['key']}: {test['summary']}")
            print(f"   Test files: {', '.join(test_files)}")
            print(f"   URL: https://prismaphotonics.atlassian.net/browse/{test['key']}")
    
    # Show tests not implemented
    if results['tests_not_implemented']:
        print("\n" + "=" * 100)
        print("TESTS NOT IMPLEMENTED")
        print("=" * 100)
        print(f"\nFound {len(results['tests_not_implemented'])} tests that are NOT yet implemented:")
        
        for i, item in enumerate(results['tests_not_implemented'][:30], 1):
            test = item['test']
            print(f"\n{i}. {test['key']}: {test['summary']}")
            print(f"   URL: https://prismaphotonics.atlassian.net/browse/{test['key']}")
            print(f"   Status: NEEDS AUTOMATION TASK")
    
    # Show tests with matching tasks
    if results['tests_with_task']:
        print("\n" + "=" * 100)
        print("TESTS WITH MATCHING TASKS (GOOD!)")
        print("=" * 100)
        print(f"\nFound {len(results['tests_with_task'])} tests that have matching tasks in Epic:")
        
        for i, item in enumerate(results['tests_with_task'][:20], 1):
            test = item['test']
            ticket = item['ticket']
            test_files = item.get('test_files', [])
            print(f"\n{i}. Test: {test['key']}: {test['summary']}")
            print(f"   Task: {ticket['key']}: {ticket.get('summary', 'N/A')}")
            if test_files:
                print(f"   ✅ Implemented in: {', '.join(test_files)}")
            else:
                print(f"   ⚠️  Not yet implemented in code")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

