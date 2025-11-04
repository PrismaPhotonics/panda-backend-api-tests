"""
Cursor Jira Agent - Interactive Jira Operations
================================================

This script provides an interactive interface for Jira operations
that can be easily called from Cursor chat or as agent commands.

Usage:
    python scripts/jira/cursor_jira_agent.py create-bug "API endpoint returns 500" "The /channels endpoint fails"
    python scripts/jira/cursor_jira_agent.py search "project = PZ AND status != Done"
    python scripts/jira/cursor_jira_agent.py get PZ-12345
    python scripts/jira/cursor_jira_agent.py update-status PZ-12345 "In Progress"
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_issue(issue: Dict[str, Any]):
    """Print issue details."""
    print(f"\n{'='*80}")
    print(f"Key: {issue['key']}")
    print(f"Summary: {issue['summary']}")
    print(f"Status: {issue['status']}")
    print(f"Priority: {issue['priority'] or 'N/A'}")
    print(f"Issue Type: {issue['issue_type']}")
    print(f"Assignee: {issue['assignee'] or 'Unassigned'}")
    print(f"Labels: {', '.join(issue['labels']) if issue['labels'] else 'None'}")
    print(f"URL: {issue['url']}")
    print(f"{'='*80}\n")


def print_issues(issues: List[Dict[str, Any]]):
    """Print list of issues."""
    if not issues:
        print("\n❌ No issues found.")
        return
    
    print(f"\n✅ Found {len(issues)} issue(s):\n")
    for issue in issues:
        print(f"  {issue['key']}: {issue['summary']} ({issue['status']})")
    print()


def main():
    """Main function for Cursor Jira Agent."""
    parser = argparse.ArgumentParser(
        description='Cursor Jira Agent - Interactive Jira operations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a bug
  python cursor_jira_agent.py create-bug "API endpoint returns 500" "The /channels endpoint fails"
  
  # Create a task
  python cursor_jira_agent.py create-task "New task" "Task description"
  
  # Search issues
  python cursor_jira_agent.py search "project = PZ AND status != Done"
  
  # Get issue
  python cursor_jira_agent.py get PZ-12345
  
  # Update status
  python cursor_jira_agent.py update-status PZ-12345 "In Progress"
  
  # Get open issues
  python cursor_jira_agent.py open-issues
  
  # Get my open issues
  python cursor_jira_agent.py my-issues
  
  # Get bugs
  python cursor_jira_agent.py bugs
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Create bug command
    create_bug_parser = subparsers.add_parser('create-bug', help='Create a bug ticket')
    create_bug_parser.add_argument('summary', help='Bug summary')
    create_bug_parser.add_argument('description', nargs='?', help='Bug description')
    create_bug_parser.add_argument('--priority', default='High', help='Priority (default: High)')
    create_bug_parser.add_argument('--labels', help='Comma-separated labels')
    create_bug_parser.add_argument('--assignee', help='Assignee username')
    
    # Create task command
    create_task_parser = subparsers.add_parser('create-task', help='Create a task ticket')
    create_task_parser.add_argument('summary', help='Task summary')
    create_task_parser.add_argument('description', nargs='?', help='Task description')
    create_task_parser.add_argument('--priority', default='Medium', help='Priority (default: Medium)')
    create_task_parser.add_argument('--labels', help='Comma-separated labels')
    create_task_parser.add_argument('--assignee', help='Assignee username')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search issues using JQL')
    search_parser.add_argument('jql', help='JQL query string')
    search_parser.add_argument('--max', type=int, help='Maximum results')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get issue by key')
    get_parser.add_argument('issue_key', help='Issue key (e.g., PZ-12345)')
    
    # Update status command
    update_status_parser = subparsers.add_parser('update-status', help='Update issue status')
    update_status_parser.add_argument('issue_key', help='Issue key')
    update_status_parser.add_argument('status', help='New status')
    
    # Update priority command
    update_priority_parser = subparsers.add_parser('update-priority', help='Update issue priority')
    update_priority_parser.add_argument('issue_key', help='Issue key')
    update_priority_parser.add_argument('priority', help='New priority')
    
    # Add comment command
    add_comment_parser = subparsers.add_parser('add-comment', help='Add comment to issue')
    add_comment_parser.add_argument('issue_key', help='Issue key')
    add_comment_parser.add_argument('comment', help='Comment text')
    
    # Get open issues command
    subparsers.add_parser('open-issues', help='Get all open issues in project')
    
    # Get my open issues command
    subparsers.add_parser('my-issues', help='Get all open issues assigned to me')
    
    # Get bugs command
    subparsers.add_parser('bugs', help='Get all open bugs in project')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Initialize agent
        agent = JiraAgent()
        
        # Execute command
        if args.command == 'create-bug':
            labels = None
            if args.labels:
                labels = [l.strip() for l in args.labels.split(',')]
            
            issue = agent.create_bug(
                summary=args.summary,
                description=args.description,
                priority=args.priority,
                labels=labels,
                assignee=args.assignee
            )
            print("\n✅ Bug created successfully!")
            print_issue(issue)
            
        elif args.command == 'create-task':
            labels = None
            if args.labels:
                labels = [l.strip() for l in args.labels.split(',')]
            
            issue = agent.create_task(
                summary=args.summary,
                description=args.description,
                priority=args.priority,
                labels=labels,
                assignee=args.assignee
            )
            print("\n✅ Task created successfully!")
            print_issue(issue)
            
        elif args.command == 'search':
            issues = agent.search(args.jql, max_results=args.max)
            print_issues(issues)
            
        elif args.command == 'get':
            issue = agent.get_issue(args.issue_key)
            print_issue(issue)
            
        elif args.command == 'update-status':
            agent.update_status(args.issue_key, args.status)
            print(f"\n✅ Issue {args.issue_key} updated to status: {args.status}")
            issue = agent.get_issue(args.issue_key)
            print_issue(issue)
            
        elif args.command == 'update-priority':
            agent.update_priority(args.issue_key, args.priority)
            print(f"\n✅ Issue {args.issue_key} updated to priority: {args.priority}")
            issue = agent.get_issue(args.issue_key)
            print_issue(issue)
            
        elif args.command == 'add-comment':
            comment = agent.add_comment(args.issue_key, args.comment)
            print(f"\n✅ Comment added to {args.issue_key}")
            print(f"   Author: {comment['author']}")
            print(f"   Comment: {comment['body']}")
            
        elif args.command == 'open-issues':
            issues = agent.get_open_issues()
            print_issues(issues)
            
        elif args.command == 'my-issues':
            issues = agent.get_my_open_issues()
            print_issues(issues)
            
        elif args.command == 'bugs':
            issues = agent.get_bugs()
            print_issues(issues)
        
        return 0
        
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

