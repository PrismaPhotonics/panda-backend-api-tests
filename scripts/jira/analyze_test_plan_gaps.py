"""
Analyze Test Plan Gaps
=======================

This script analyzes a test plan CSV file and compares it with tickets in Epic PZ-14221
to identify missing automation development tasks.

Author: QA Automation Architect
Date: 2025-11-04
"""

import sys
import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Set
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from external.jira import JiraClient, JiraAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestPlanGapAnalyzer:
    """Analyze gaps between test plan and Epic tickets."""
    
    def __init__(self, epic_key: str, csv_file_path: str):
        """
        Initialize analyzer.
        
        Args:
            epic_key: Epic key (e.g., "PZ-14221")
            csv_file_path: Path to test plan CSV file
        """
        self.epic_key = epic_key
        self.csv_file_path = csv_file_path
        self.client = JiraClient()
        self.agent = JiraAgent()
        
        # Data storage
        self.test_plan_tests = []
        self.epic_tickets = []
        self.missing_tasks = []
        
    def parse_csv_file(self) -> List[Dict[str, Any]]:
        """
        Parse test plan CSV file.
        
        Returns:
            List of test dictionaries from CSV
        """
        logger.info(f"Parsing CSV file: {self.csv_file_path}")
        
        tests = []
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as f:
                # Try to detect delimiter
                sample = f.read(1024)
                f.seek(0)
                
                # Try common delimiters
                delimiter = ','
                if ';' in sample and sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif '\t' in sample:
                    delimiter = '\t'
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                    
                    # Extract test information
                    test_info = {
                        'row_number': row_num,
                        'raw_data': row
                    }
                    
                    # Try to find test name/summary
                    for key in ['Test Name', 'Test Summary', 'Summary', 'Name', 'Test', 'Title']:
                        if key in row and row[key]:
                            test_info['test_name'] = row[key].strip()
                            break
                    
                    # Try to find Issue key (most important for matching)
                    for key in ['Issue key', 'Issue Key', 'Issue ID', 'Test ID', 'ID', 'Test Key', 'Key', 'Xray ID']:
                        if key in row and row[key]:
                            test_info['test_id'] = row[key].strip()
                            test_info['issue_key'] = row[key].strip()
                            break
                    
                    # Try to find description
                    for key in ['Description', 'Test Description', 'Details', 'Test Details']:
                        if key in row and row[key]:
                            test_info['description'] = row[key].strip()
                            break
                    
                    # Try to find category/type
                    for key in ['Category', 'Type', 'Test Type', 'Category', 'Component']:
                        if key in row and row[key]:
                            test_info['category'] = row[key].strip()
                            break
                    
                    # Store all row data for reference
                    test_info['all_fields'] = {k: v for k, v in row.items() if v}
                    
                    tests.append(test_info)
            
            logger.info(f"Parsed {len(tests)} tests from CSV")
            return tests
        
        except Exception as e:
            logger.error(f"Failed to parse CSV file: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_all_epic_tickets(self) -> List[Dict[str, Any]]:
        """
        Get all tickets (stories, tasks, subtasks) in Epic.
        
        Returns:
            List of ticket dictionaries
        """
        logger.info(f"Getting all tickets in Epic {self.epic_key}")
        
        all_tickets = []
        
        try:
            # Get Epic details
            epic = self.client.get_issue(self.epic_key)
            logger.info(f"Epic: {epic.get('summary', 'N/A')} ({epic.get('status', 'N/A')})")
            
            # Get all tickets with Epic Link = PZ-14221
            jql = f'"Epic Link" = {self.epic_key}'
            epic_tickets = self.client.search_issues(jql, max_results=500)
            logger.info(f"Found {len(epic_tickets)} tickets with Epic Link")
            
            for ticket in epic_tickets:
                issue_type = ticket.get('issue_type', '').lower()
                
                # Get subtasks if it's a story or task
                if issue_type in ['story', 'task']:
                    try:
                        subtasks_jql = f"parent = {ticket['key']}"
                        subtasks = self.client.search_issues(subtasks_jql, max_results=100)
                        all_tickets.extend(subtasks)
                        logger.debug(f"Found {len(subtasks)} subtasks for {ticket['key']}")
                    except Exception as e:
                        logger.warning(f"Failed to get subtasks for {ticket['key']}: {e}")
                
                all_tickets.append(ticket)
            
            # Also get tickets linked via parent
            try:
                parent_jql = f"parent in ({','.join([t['key'] for t in epic_tickets])})"
                parent_tickets = self.client.search_issues(parent_jql, max_results=200)
                all_tickets.extend(parent_tickets)
            except Exception as e:
                logger.warning(f"Failed to get parent-linked tickets: {e}")
            
            # Remove duplicates
            seen_keys = set()
            unique_tickets = []
            for ticket in all_tickets:
                if ticket['key'] not in seen_keys:
                    seen_keys.add(ticket['key'])
                    unique_tickets.append(ticket)
            
            logger.info(f"Total unique tickets in Epic: {len(unique_tickets)}")
            return unique_tickets
        
        except Exception as e:
            logger.error(f"Failed to get epic tickets: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def extract_test_keywords(self, test_name: str) -> Set[str]:
        """
        Extract keywords from test name for matching.
        
        Args:
            test_name: Test name string
        
        Returns:
            Set of keywords
        """
        if not test_name:
            return set()
        
        # Normalize and split
        normalized = test_name.lower()
        
        # Remove common words
        stop_words = {'test', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        # Split by common separators
        words = normalized.replace('-', ' ').replace('_', ' ').split()
        
        # Filter out stop words and short words
        keywords = {w for w in words if len(w) > 2 and w not in stop_words}
        
        return keywords
    
    def find_matching_ticket(self, test_info: Dict[str, Any], epic_tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Find matching ticket for a test.
        
        Args:
            test_info: Test information from CSV
            epic_tickets: List of tickets in Epic
        
        Returns:
            Matching ticket dict or None
        """
        # First try exact match by Issue key
        issue_key = test_info.get('issue_key', '')
        if issue_key:
            for ticket in epic_tickets:
                if ticket['key'] == issue_key:
                    return ticket
        
        # Then try by test name/keywords
        test_name = test_info.get('test_name', '')
        test_keywords = self.extract_test_keywords(test_name)
        
        if not test_keywords:
            return None
        
        best_match = None
        best_score = 0
        
        for ticket in epic_tickets:
            ticket_summary = ticket.get('summary', '').lower()
            ticket_description = ticket.get('description', '').lower()
            
            # Calculate match score
            score = 0
            
            # Exact keyword matches
            ticket_text = f"{ticket_summary} {ticket_description}"
            for keyword in test_keywords:
                if keyword in ticket_text:
                    score += 1
            
            # Bonus for multiple keyword matches
            matched_keywords = sum(1 for kw in test_keywords if kw in ticket_text)
            if matched_keywords > 1:
                score += matched_keywords * 0.5
            
            # Check for test ID match in summary
            test_id = test_info.get('test_id', '')
            if test_id and test_id in ticket_summary:
                score += 10
            
            if score > best_score:
                best_score = score
                best_match = ticket
        
        # Only return match if score is significant
        if best_score >= 2:
            return best_match
        
        return None
    
    def analyze_gaps(self) -> Dict[str, Any]:
        """
        Analyze gaps between test plan and Epic tickets.
        
        Returns:
            Dictionary with analysis results
        """
        logger.info("=" * 80)
        logger.info("Starting Gap Analysis")
        logger.info("=" * 80)
        
        # Parse CSV
        self.test_plan_tests = self.parse_csv_file()
        
        # Get Epic tickets
        self.epic_tickets = self.get_all_epic_tickets()
        
        # Find matches
        matched_tests = []
        unmatched_tests = []
        
        for test in self.test_plan_tests:
            match = self.find_matching_ticket(test, self.epic_tickets)
            if match:
                matched_tests.append({
                    'test': test,
                    'ticket': match
                })
            else:
                unmatched_tests.append(test)
        
        # Find unmatched tickets (tickets without tests)
        matched_ticket_keys = {m['ticket']['key'] for m in matched_tests}
        unmatched_tickets = [t for t in self.epic_tickets if t['key'] not in matched_ticket_keys]
        
        # Prepare results
        results = {
            'epic_key': self.epic_key,
            'test_plan_total': len(self.test_plan_tests),
            'epic_tickets_total': len(self.epic_tickets),
            'matched_tests': len(matched_tests),
            'unmatched_tests': len(unmatched_tests),
            'unmatched_tickets': len(unmatched_tickets),
            'matched_tests_details': matched_tests,
            'unmatched_tests_details': unmatched_tests,
            'unmatched_tickets_details': unmatched_tickets,
            'missing_tasks': []
        }
        
        # Identify missing tasks
        for test in unmatched_tests:
            test_name = test.get('test_name', f"Row {test.get('row_number', 'N/A')}")
            results['missing_tasks'].append({
                'test_name': test_name,
                'test_id': test.get('test_id', ''),
                'description': test.get('description', ''),
                'category': test.get('category', ''),
                'row_number': test.get('row_number'),
                'suggested_task_summary': f"Automate: {test_name}",
                'all_fields': test.get('all_fields', {})
            })
        
        return results
    
    def print_report(self, results: Dict[str, Any]):
        """Print analysis report."""
        print("\n" + "=" * 80)
        print("GAP ANALYSIS REPORT")
        print("=" * 80)
        print(f"\nEpic: {results['epic_key']}")
        print(f"Test Plan Total: {results['test_plan_total']} tests")
        print(f"Epic Tickets Total: {results['epic_tickets_total']} tickets")
        print(f"\nMatched: {results['matched_tests']} tests")
        print(f"Unmatched Tests: {results['unmatched_tests']} tests (missing tasks)")
        print(f"Unmatched Tickets: {results['unmatched_tickets']} tickets (no tests)")
        
        if results['missing_tasks']:
            print("\n" + "-" * 80)
            print("MISSING AUTOMATION TASKS")
            print("-" * 80)
            for i, task in enumerate(results['missing_tasks'], 1):
                print(f"\n{i}. {task['test_name']}")
                if task.get('test_id'):
                    print(f"   Test ID: {task['test_id']}")
                if task.get('description'):
                    desc = task['description'][:100] + "..." if len(task['description']) > 100 else task['description']
                    print(f"   Description: {desc}")
                if task.get('category'):
                    print(f"   Category: {task['category']}")
                print(f"   Suggested Summary: {task['suggested_task_summary']}")
        
        if results['unmatched_tickets_details']:
            print("\n" + "-" * 80)
            print("TICKETS WITHOUT TESTS")
            print("-" * 80)
            for ticket in results['unmatched_tickets_details'][:20]:  # Show first 20
                print(f"\n- {ticket['key']}: {ticket.get('summary', 'N/A')}")
                print(f"  Type: {ticket.get('issue_type', 'N/A')}, Status: {ticket.get('status', 'N/A')}")


def main():
    """Main function."""
    epic_key = "PZ-14221"
    csv_file = r"C:\Users\roy.avrahami\Downloads\Test plan (TS_Focus_Server_PZ-14024) by Roy Avrahami (Jira) (3).csv"
    
    if not os.path.exists(csv_file):
        print(f"ERROR: CSV file not found: {csv_file}")
        return 1
    
    analyzer = TestPlanGapAnalyzer(epic_key, csv_file)
    results = analyzer.analyze_gaps()
    analyzer.print_report(results)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

