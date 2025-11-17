"""
Generate Detailed Gap Report
============================

Generate a detailed report comparing test plan CSV with Epic PZ-14221 tickets.
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
    """Generate gap report."""
    epic_key = "PZ-14221"
    csv_file = r"C:\Users\roy.avrahami\Downloads\Test plan (TS_Focus_Server_PZ-14024) by Roy Avrahami (Jira) (3).csv"
    
    client = JiraClient()
    agent = JiraAgent()
    
    # Get all tickets in Epic
    print("=" * 100)
    print("EPIC PZ-14221 - GAP ANALYSIS REPORT")
    print("=" * 100)
    
    # Get Epic tickets
    jql = f'"Epic Link" = {epic_key}'
    epic_tickets = client.search_issues(jql, max_results=500)
    
    # Get all subtasks
    all_tickets = []
    for ticket in epic_tickets:
        all_tickets.append(ticket)
        try:
            subtasks_jql = f"parent = {ticket['key']}"
            subtasks = client.search_issues(subtasks_jql, max_results=100)
            all_tickets.extend(subtasks)
        except:
            pass
    
    # Remove duplicates
    seen_keys = set()
    unique_tickets = []
    for ticket in all_tickets:
        if ticket['key'] not in seen_keys:
            seen_keys.add(ticket['key'])
            unique_tickets.append(ticket)
    
    print(f"\nTotal tickets in Epic: {len(unique_tickets)}")
    
    # Parse CSV
    print(f"\nParsing CSV file: {csv_file}")
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
            
            if issue_key or summary:
                csv_tests.append({
                    'issue_key': issue_key,
                    'summary': summary,
                    'row': row
                })
    
    print(f"Total tests in CSV: {len(csv_tests)}")
    
    # Create mapping
    epic_ticket_keys = {t['key'] for t in unique_tickets}
    csv_test_keys = {t['issue_key'] for t in csv_tests if t['issue_key']}
    
    # Find matches
    matched_by_key = csv_test_keys.intersection(epic_ticket_keys)
    unmatched_csv_tests = [t for t in csv_tests if t['issue_key'] and t['issue_key'] not in epic_ticket_keys]
    unmatched_tickets = [t for t in unique_tickets if t['key'] not in csv_test_keys]
    
    # Print report
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"Epic tickets: {len(unique_tickets)}")
    print(f"CSV tests: {len(csv_tests)}")
    print(f"Matched by key: {len(matched_by_key)}")
    print(f"Unmatched CSV tests (missing tasks): {len(unmatched_csv_tests)}")
    print(f"Unmatched tickets (no test in CSV): {len(unmatched_tickets)}")
    
    # Show unmatched CSV tests (missing automation tasks)
    if unmatched_csv_tests:
        print("\n" + "=" * 100)
        print("MISSING AUTOMATION TASKS")
        print("=" * 100)
        print(f"\nFound {len(unmatched_csv_tests)} tests from CSV that don't have corresponding tasks in Epic:")
        print("\nThese tests need automation development tasks created:")
        
        for i, test in enumerate(unmatched_csv_tests[:50], 1):  # Show first 50
            issue_key = test['issue_key']
            summary = test['summary']
            print(f"\n{i}. {issue_key}: {summary}")
            
            # Try to get ticket details
            if issue_key:
                try:
                    ticket = client.get_issue(issue_key)
                    status = ticket.get('status', 'N/A')
                    issue_type = ticket.get('issue_type', 'N/A')
                    print(f"   Status: {status}, Type: {issue_type}")
                    print(f"   URL: {ticket.get('url', 'N/A')}")
                except:
                    print(f"   [Ticket not found or not accessible]")
    
    # Show unmatched tickets
    if unmatched_tickets:
        print("\n" + "=" * 100)
        print("TICKETS IN EPIC WITHOUT TESTS IN CSV")
        print("=" * 100)
        print(f"\nFound {len(unmatched_tickets)} tickets in Epic that don't have tests in CSV:")
        
        for i, ticket in enumerate(unmatched_tickets[:30], 1):  # Show first 30
            print(f"\n{i}. {ticket['key']}: {ticket.get('summary', 'N/A')}")
            print(f"   Type: {ticket.get('issue_type', 'N/A')}, Status: {ticket.get('status', 'N/A')}")
            print(f"   URL: {ticket.get('url', 'N/A')}")
    
    # Generate detailed report file
    report_file = Path(__file__).parent.parent.parent / "docs" / "06_project_management" / "jira" / "GAP_ANALYSIS_REPORT_PZ-14221.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Gap Analysis Report - Epic PZ-14221\n\n")
        f.write(f"**Date:** 2025-11-04\n")
        f.write(f"**Epic:** PZ-14221 - Backend Automation - Focus Server API Tests - Drop 3\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Epic tickets: {len(unique_tickets)}\n")
        f.write(f"- CSV tests: {len(csv_tests)}\n")
        f.write(f"- Matched by key: {len(matched_by_key)}\n")
        f.write(f"- Unmatched CSV tests (missing tasks): {len(unmatched_csv_tests)}\n")
        f.write(f"- Unmatched tickets (no test in CSV): {len(unmatched_tickets)}\n\n")
        
        if unmatched_csv_tests:
            f.write("## Missing Automation Tasks\n\n")
            f.write(f"These {len(unmatched_csv_tests)} tests from CSV need automation development tasks:\n\n")
            for test in unmatched_csv_tests:
                f.write(f"### {test['issue_key']}: {test['summary']}\n\n")
                f.write(f"- **Issue Key:** {test['issue_key']}\n")
                f.write(f"- **Summary:** {test['summary']}\n")
                f.write(f"- **Suggested Task:** Automate: {test['summary']}\n\n")
    
    print(f"\n\nDetailed report saved to: {report_file}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

