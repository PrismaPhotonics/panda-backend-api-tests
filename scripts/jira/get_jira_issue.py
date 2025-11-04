"""
Get Jira Issue Script
=====================

Command-line script for retrieving Jira issue details.

Usage:
    python scripts/jira/get_jira_issue.py PZ-12345
    python scripts/jira/get_jira_issue.py --key PZ-12345 --detailed
    python scripts/jira/get_jira_issue.py --keys PZ-12345,PZ-12346,PZ-12347
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


def print_issue_detailed(issue: Dict):
    """Print detailed issue information."""
    print(f"\n{'='*80}")
    print(f"ISSUE: {issue['key']}")
    print(f"{'='*80}")
    print(f"Summary:     {issue['summary']}")
    print(f"Status:      {issue['status']}")
    print(f"Priority:    {issue['priority'] or 'N/A'}")
    print(f"Issue Type:  {issue['issue_type']}")
    print(f"Assignee:    {issue['assignee'] or 'Unassigned'}")
    print(f"Reporter:    {issue['reporter']}")
    print(f"Resolution:  {issue['resolution'] or 'Unresolved'}")
    print(f"Labels:      {', '.join(issue['labels']) if issue['labels'] else 'None'}")
    print(f"Created:     {issue['created']}")
    print(f"Updated:     {issue['updated']}")
    print(f"\nDescription:")
    print(f"{'-'*80}")
    if issue['description']:
        print(issue['description'])
    else:
        print("(No description)")
    print(f"{'-'*80}")
    print(f"\nURL: {issue['url']}")
    print(f"{'='*80}\n")


def print_issue_summary(issue: Dict):
    """Print issue summary."""
    print(f"\n{issue['key']}: {issue['summary']}")
    print(f"  Status: {issue['status']} | Priority: {issue['priority'] or 'N/A'} | Type: {issue['issue_type']}")
    print(f"  Assignee: {issue['assignee'] or 'Unassigned'}")
    print(f"  URL: {issue['url']}")


def main():
    """Main function for getting Jira issues."""
    parser = argparse.ArgumentParser(
        description='Get Jira issue details',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get single issue
  python get_jira_issue.py PZ-12345
  
  # Get issue with detailed output
  python get_jira_issue.py --key PZ-12345 --detailed
  
  # Get multiple issues
  python get_jira_issue.py --keys PZ-12345,PZ-12346,PZ-12347
        """
    )
    
    # Issue key arguments
    issue_group = parser.add_mutually_exclusive_group(required=True)
    issue_group.add_argument(
        'key',
        nargs='?',
        help='Issue key (e.g., PZ-12345)'
    )
    issue_group.add_argument(
        '--key',
        dest='key_arg',
        help='Issue key (e.g., PZ-12345)'
    )
    issue_group.add_argument(
        '--keys',
        help='Comma-separated list of issue keys'
    )
    
    # Optional arguments
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
        
        # Determine which issues to get
        if args.keys:
            # Get multiple issues
            issue_keys = [key.strip() for key in args.keys.split(',')]
            logger.info(f"Getting {len(issue_keys)} issue(s)...")
            issues = client.get_issues_by_keys(issue_keys)
            
            # Print results
            if args.detailed:
                for issue in issues:
                    print_issue_detailed(issue)
            else:
                for issue in issues:
                    print_issue_summary(issue)
        else:
            # Get single issue
            issue_key = args.key or args.key_arg
            logger.info(f"Getting issue: {issue_key}")
            issue = client.get_issue(issue_key)
            
            # Print result
            if args.detailed:
                print_issue_detailed(issue)
            else:
                print_issue_summary(issue)
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to get issue: {e}")
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

