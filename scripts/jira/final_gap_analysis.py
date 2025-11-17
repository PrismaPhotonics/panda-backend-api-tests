"""
Final Gap Analysis - Comprehensive Check
========================================

This script does a comprehensive analysis:
1. Checks if tests from CSV are implemented in code
2. Checks if tests have corresponding tasks in Epic PZ-14221
3. Identifies gaps
"""

import sys
import csv
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Set
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from external.jira import JiraClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_test_files_for_xray_test(xray_test_key: str, tests_dir: Path) -> List[str]:
    """Find test files with Xray marker for test key."""
    test_files = []
    
    for test_file in tests_dir.rglob('test_*.py'):
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for Xray marker - handle both single and multiple test keys
                # Pattern: @pytest.mark.xray("PZ-14101") or @pytest.mark.xray("PZ-14101", "PZ-13865")
                pattern = rf'@pytest\.mark\.xray\([^)]*["\']?{re.escape(xray_test_key)}["\']?[^)]*\)'
                if re.search(pattern, content):
                    rel_path = str(test_file.relative_to(tests_dir.parent))
                    test_files.append(rel_path)
        except:
            pass
    
    return test_files


def find_matching_epic_ticket(test_summary: str, epic_tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find matching Epic ticket by summary/keywords."""
    test_lower = test_summary.lower()
    test_keywords = set([w for w in test_lower.split() if len(w) > 3])
    
    if not test_keywords:
        return None
    
    best_match = None
    best_score = 0
    
    for ticket in epic_tickets:
        ticket_summary = ticket.get('summary', '').lower()
        ticket_keywords = set([w for w in ticket_summary.split() if len(w) > 3])
        
        if ticket_keywords:
            overlap = test_keywords.intersection(ticket_keywords)
            score = len(overlap)
            
            # Bonus for multiple matches
            if score >= 3:
                score += 5
            elif score >= 2:
                score += 2
            
            if score > best_score:
                best_score = score
                best_match = ticket
    
    return best_match if best_score >= 3 else None


def main():
    """Main analysis."""
    epic_key = "PZ-14221"
    csv_file = r"C:\Users\roy.avrahami\Downloads\Test plan (TS_Focus_Server_PZ-14024) by Roy Avrahami (Jira) (3).csv"
    
    client = JiraClient()
    tests_dir = Path(__file__).parent.parent.parent / 'tests'
    
    print("=" * 100)
    print("COMPREHENSIVE GAP ANALYSIS - Epic PZ-14221")
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
    
    epic_ticket_keys = {t['key'] for t in unique_epic_tickets}
    
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
    
    # Analyze each test
    results = {
        'implemented_with_task': [],
        'implemented_no_task': [],
        'not_implemented_with_task': [],
        'not_implemented_no_task': []
    }
    
    print("\nAnalyzing tests...")
    
    for test in csv_tests:
        test_key = test['key']
        test_summary = test['summary']
        
        # Check if implemented
        test_files = find_test_files_for_xray_test(test_key, tests_dir)
        implemented = len(test_files) > 0
        
        # Check if in Epic
        in_epic = test_key in epic_ticket_keys
        
        # Find matching ticket
        matching_ticket = None
        if not in_epic:
            matching_ticket = find_matching_epic_ticket(test_summary, unique_epic_tickets)
        
        has_task = in_epic or matching_ticket is not None
        
        # Categorize
        if implemented and has_task:
            results['implemented_with_task'].append({
                'test': test,
                'test_files': test_files,
                'ticket': matching_ticket or next(t for t in unique_epic_tickets if t['key'] == test_key)
            })
        elif implemented and not has_task:
            results['implemented_no_task'].append({
                'test': test,
                'test_files': test_files
            })
        elif not implemented and has_task:
            results['not_implemented_with_task'].append({
                'test': test,
                'ticket': matching_ticket or next(t for t in unique_epic_tickets if t['key'] == test_key)
            })
        else:
            results['not_implemented_no_task'].append({
                'test': test
            })
    
    # Print summary
    print("\n" + "=" * 100)
    print("ANALYSIS SUMMARY")
    print("=" * 100)
    print(f"\n✅ Implemented + Has Task: {len(results['implemented_with_task'])}")
    print(f"⚠️  Implemented + NO Task: {len(results['implemented_no_task'])}")
    print(f"📋 Not Implemented + Has Task: {len(results['not_implemented_with_task'])}")
    print(f"❌ Not Implemented + NO Task: {len(results['not_implemented_no_task'])}")
    
    # Show missing tasks (implemented but no task)
    if results['implemented_no_task']:
        print("\n" + "=" * 100)
        print("MISSING AUTOMATION TASKS (Tests Already Implemented!)")
        print("=" * 100)
        print(f"\n{len(results['implemented_no_task'])} tests are ALREADY IMPLEMENTED in code")
        print("but don't have corresponding automation tasks in Epic PZ-14221:")
        
        for i, item in enumerate(results['implemented_no_task'], 1):
            test = item['test']
            test_files = item['test_files']
            print(f"\n{i}. {test['key']}: {test['summary']}")
            print(f"   ✅ Implemented in: {', '.join(test_files)}")
            print(f"   ❌ Missing task in Epic PZ-14221")
            print(f"   URL: https://prismaphotonics.atlassian.net/browse/{test['key']}")
    
    # Show tests not implemented and no task
    if results['not_implemented_no_task']:
        print("\n" + "=" * 100)
        print("TESTS NOT IMPLEMENTED AND NO TASK")
        print("=" * 100)
        print(f"\n{len(results['not_implemented_no_task'])} tests are NOT implemented and have NO task:")
        
        for i, item in enumerate(results['not_implemented_no_task'], 1):
            test = item['test']
            print(f"\n{i}. {test['key']}: {test['summary']}")
            print(f"   URL: https://prismaphotonics.atlassian.net/browse/{test['key']}")
            print(f"   Status: NEEDS AUTOMATION TASK + IMPLEMENTATION")
    
    print("\n" + "=" * 100)
    print("TOTAL GAPS")
    print("=" * 100)
    total_gaps = len(results['implemented_no_task']) + len(results['not_implemented_no_task'])
    print(f"\nTotal missing automation tasks: {total_gaps}")
    print(f"  - Tests already implemented: {len(results['implemented_no_task'])}")
    print(f"  - Tests not yet implemented: {len(results['not_implemented_no_task'])}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

