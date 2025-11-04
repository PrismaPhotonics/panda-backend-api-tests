"""
Search Jira Issues Script
=========================

Command-line script for searching Jira issues.

Usage:
    python scripts/jira/search_jira_issues.py --jql "project = PZ AND status != Done"
    python scripts/jira/search_jira_issues.py --filter my_open
    python scripts/jira/search_jira_issues.py --filter project_open --project PZ
    python scripts/jira/search_jira_issues.py --filter project_bugs --max 50
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_issue(issue: Dict):
    """Print issue details."""
    print(f"\n{'='*80}")
    print(f"Key: {issue['key']}")
    print(f"Summary: {issue['summary']}")
    print(f"Status: {issue['status']}")
    print(f"Priority: {issue['priority']}")
    print(f"Issue Type: {issue['issue_type']}")
    print(f"Assignee: {issue['assignee'] or 'Unassigned'}")
    print(f"Reporter: {issue['reporter']}")
    print(f"Labels: {', '.join(issue['labels']) if issue['labels'] else 'None'}")
    print(f"URL: {issue['url']}")
    print(f"Created: {issue['created']}")
    print(f"Updated: {issue['updated']}")


def print_issues_summary(issues: List[Dict]):
    """Print summary of issues."""
    if not issues:
        print("\n❌ No issues found.")
        return
    
    print(f"\n✅ Found {len(issues)} issue(s):\n")
    
    # Print summary table
    print(f"{'Key':<12} {'Status':<15} {'Priority':<10} {'Summary':<50}")
    print("-" * 87)
    
    for issue in issues:
        summary = issue['summary'][:47] + '...' if len(issue['summary']) > 50 else issue['summary']
        print(f"{issue['key']:<12} {issue['status']:<15} {issue['priority'] or 'N/A':<10} {summary:<50}")
    
    print(f"\n{'='*80}")


def main():
    """Main function for searching Jira issues."""
    parser = argparse.ArgumentParser(
        description='Search Jira issues',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search using JQL
  python search_jira_issues.py --jql "project = PZ AND status != Done"
  
  # Use predefined filter
  python search_jira_issues.py --filter my_open
  python search_jira_issues.py --filter project_open --project PZ
  
  # Search with limit
  python search_jira_issues.py --filter project_bugs --max 50
  
  # Detailed output
  python search_jira_issues.py --jql "project = PZ" --detailed
        """
    )
    
    # Search method (mutually exclusive)
    search_group = parser.add_mutually_exclusive_group(required=True)
    search_group.add_argument(
        '--jql',
        help='JQL query string'
    )
    search_group.add_argument(
        '--filter',
        help='Use predefined filter (my_open, project_open, project_bugs, etc.)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--project',
        '--project-key',
        dest='project_key',
        help='Project key (for filters, defaults to config)'
    )
    
    parser.add_argument(
        '--max',
        '--max-results',
        dest='max_results',
        type=int,
        help='Maximum number of results'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Print detailed issue information'
    )
    
    parser.add_argument(
        '--config',
        help='Path to jira_config.yaml (optional)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize Jira client
        client = JiraClient(config_path=args.config)
        
        # Search issues
        if args.jql:
            # Search using JQL
            logger.info(f"Searching issues with JQL: {args.jql}")
            issues = client.search_issues(
                jql=args.jql,
                max_results=args.max_results
            )
        else:
            # Use filter
            logger.info(f"Searching issues using filter: {args.filter}")
            issues = client.search_issues_by_filter(
                filter_name=args.filter,
                project_key=args.project_key
            )
        
        # Print results
        if args.detailed:
            # Print detailed information for each issue
            for issue in issues:
                print_issue(issue)
        else:
            # Print summary table
            print_issues_summary(issues)
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to search issues: {e}")
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

