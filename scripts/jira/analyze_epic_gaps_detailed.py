"""
Detailed Epic Gap Analysis
==========================

Analyze gaps between Xray Test Plan tests and Epic PZ-14221 automation tasks.
"""

import sys
import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Set
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from external.jira import JiraClient, JiraAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Generate detailed gap analysis."""
    epic_key = "PZ-14221"
    csv_file = r"C:\Users\roy.avrahami\Downloads\Test plan (TS_Focus_Server_PZ-14024) by Roy Avrahami (Jira) (3).csv"
    
    client = JiraClient()
    
    print("=" * 100)
    print("EPIC PZ-14221 - DETAILED GAP ANALYSIS")
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
    
    print(f"\nTotal tickets in Epic PZ-14221: {len(unique_epic_tickets)}")
    
    # Parse CSV
    print(f"\nParsing CSV file...")
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
                    'issue_key': issue_key,
                    'summary': summary,
                    'status': row.get('Status', '').strip(),
                    'type': row.get('Issue Type', '').strip(),
                    'description': row.get('Description', '').strip()
                })
    
    print(f"Total tests in CSV: {len(csv_tests)}")
    
    # Get details of CSV tests
    print("\nAnalyzing CSV tests...")
    csv_test_details = []
    for test in csv_tests:
        issue_key = test['issue_key']
        if issue_key:
            try:
                test_details = client.get_issue(issue_key)
                csv_test_details.append({
                    'key': issue_key,
                    'summary': test_details.get('summary', test['summary']),
                    'status': test_details.get('status', test['status']),
                    'type': test_details.get('issue_type', test['type']),
                    'description': test_details.get('description', test['description']),
                    'url': test_details.get('url', '')
                })
            except Exception as e:
                logger.warning(f"Could not get details for {issue_key}: {e}")
                csv_test_details.append({
                    'key': issue_key,
                    'summary': test['summary'],
                    'status': test['status'],
                    'type': test['type'],
                    'description': test['description'],
                    'url': f"https://prismaphotonics.atlassian.net/browse/{issue_key}"
                })
    
    # Create mapping: Epic tickets by summary/keywords
    epic_ticket_keys = {t['key'] for t in unique_epic_tickets}
    epic_ticket_summaries = {t.get('summary', '').lower(): t for t in unique_epic_tickets}
    
    # Find matches
    matched_tests = []
    unmatched_tests = []
    
    for test in csv_test_details:
        test_key = test['key']
        test_summary = test.get('summary', '').lower()
        
        # Check if test key exists in Epic
        if test_key in epic_ticket_keys:
            matched_tests.append({
                'test': test,
                'ticket': next(t for t in unique_epic_tickets if t['key'] == test_key)
            })
            continue
        
        # Try to find by summary match
        found_match = False
        for epic_ticket in unique_epic_tickets:
            epic_summary = epic_ticket.get('summary', '').lower()
            
            # Extract keywords from test summary
            test_keywords = set([w for w in test_summary.split() if len(w) > 3])
            epic_keywords = set([w for w in epic_summary.split() if len(w) > 3])
            
            # Check for significant overlap
            if test_keywords and epic_keywords:
                overlap = test_keywords.intersection(epic_keywords)
                if len(overlap) >= 2:  # At least 2 keywords match
                    matched_tests.append({
                        'test': test,
                        'ticket': epic_ticket,
                        'match_type': 'keyword'
                    })
                    found_match = True
                    break
        
        if not found_match:
            unmatched_tests.append(test)
    
    # Print results
    print("\n" + "=" * 100)
    print("ANALYSIS RESULTS")
    print("=" * 100)
    print(f"\nEpic PZ-14221 tickets: {len(unique_epic_tickets)}")
    print(f"CSV tests: {len(csv_test_details)}")
    print(f"Matched tests: {len(matched_tests)}")
    print(f"Unmatched tests (missing automation tasks): {len(unmatched_tests)}")
    
    # Show unmatched tests (missing automation tasks)
    if unmatched_tests:
        print("\n" + "=" * 100)
        print("MISSING AUTOMATION TASKS")
        print("=" * 100)
        print(f"\nFound {len(unmatched_tests)} tests from CSV that don't have corresponding automation tasks in Epic PZ-14221:")
        print("\nThese tests need automation development tasks created:")
        
        for i, test in enumerate(unmatched_tests, 1):
            print(f"\n{i}. {test['key']}: {test['summary']}")
            print(f"   Status: {test['status']}, Type: {test['type']}")
            print(f"   URL: {test['url']}")
            
            # Show description preview
            desc = test.get('description', '')
            if desc:
                desc_preview = desc[:150] + "..." if len(desc) > 150 else desc
                print(f"   Description: {desc_preview}")
    
    # Show Epic tickets without tests
    matched_ticket_keys = {m['ticket']['key'] for m in matched_tests}
    unmatched_tickets = [t for t in unique_epic_tickets if t['key'] not in matched_ticket_keys]
    
    if unmatched_tickets:
        print("\n" + "=" * 100)
        print("EPIC TICKETS WITHOUT TESTS IN CSV")
        print("=" * 100)
        print(f"\nFound {len(unmatched_tickets)} tickets in Epic that don't have tests in CSV:")
        
        # Group by type
        tasks = [t for t in unmatched_tickets if t.get('issue_type', '').lower() == 'task']
        subtasks = [t for t in unmatched_tickets if t.get('issue_type', '').lower() == 'sub-task']
        stories = [t for t in unmatched_tickets if t.get('issue_type', '').lower() == 'story']
        
        print(f"\n  Tasks: {len(tasks)}")
        print(f"  Sub-tasks: {len(subtasks)}")
        print(f"  Stories: {len(stories)}")
        
        # Show first 20 unmatched tickets
        print("\nSample unmatched tickets:")
        for i, ticket in enumerate(unmatched_tickets[:20], 1):
            print(f"\n{i}. {ticket['key']}: {ticket.get('summary', 'N/A')}")
            print(f"   Type: {ticket.get('issue_type', 'N/A')}, Status: {ticket.get('status', 'N/A')}")
            print(f"   URL: {ticket.get('url', 'N/A')}")
    
    # Generate report file
    report_file = Path(__file__).parent.parent.parent / "docs" / "06_project_management" / "jira" / "EPIC_PZ-14221_GAP_ANALYSIS_DETAILED.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Gap Analysis Report - Epic PZ-14221\n\n")
        f.write(f"**Date:** 2025-11-04\n")
        f.write(f"**Epic:** PZ-14221 - Backend Automation - Focus Server API Tests - Drop 3\n\n")
        f.write("## Executive Summary\n\n")
        f.write(f"- **Epic tickets:** {len(unique_epic_tickets)}\n")
        f.write(f"- **CSV tests (Xray):** {len(csv_test_details)}\n")
        f.write(f"- **Matched:** {len(matched_tests)}\n")
        f.write(f"- **Missing automation tasks:** {len(unmatched_tests)}\n")
        f.write(f"- **Epic tickets without tests:** {len(unmatched_tickets)}\n\n")
        
        if unmatched_tests:
            f.write("## Missing Automation Tasks\n\n")
            f.write(f"These {len(unmatched_tests)} Xray tests need automation development tasks in Epic PZ-14221:\n\n")
            for test in unmatched_tests:
                f.write(f"### {test['key']}: {test['summary']}\n\n")
                f.write(f"- **Status:** {test['status']}\n")
                f.write(f"- **Type:** {test['type']}\n")
                f.write(f"- **URL:** {test['url']}\n")
                f.write(f"- **Suggested Task:** Automate: {test['summary']}\n\n")
                if test.get('description'):
                    desc = test['description'][:300] + "..." if len(test['description']) > 300 else test['description']
                    f.write(f"**Description:**\n{desc}\n\n")
                f.write("---\n\n")
    
    print(f"\n\nDetailed report saved to: {report_file}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

