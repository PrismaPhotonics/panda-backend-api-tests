"""
Update Jira Issue Script
========================

Command-line script for updating Jira issues.

Usage:
    python scripts/jira/update_jira_issue.py PZ-12345 --priority High --status "In Progress"
    python scripts/jira/update_jira_issue.py PZ-12345 --assignee john.doe --labels critical,urgent
    python scripts/jira/update_jira_issue.py PZ-12345 --summary "Updated Summary" --description "Updated description"
"""

import argparse
import sys
import logging
from pathlib import Path

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


def main():
    """Main function for updating Jira issues."""
    parser = argparse.ArgumentParser(
        description='Update a Jira issue',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update priority and status
  python update_jira_issue.py PZ-12345 --priority High --status "In Progress"
  
  # Update assignee and labels
  python update_jira_issue.py PZ-12345 --assignee john.doe --labels critical,urgent
  
  # Update summary and description
  python update_jira_issue.py PZ-12345 --summary "Updated Summary" --description "Updated description"
  
  # Change status only
  python update_jira_issue.py PZ-12345 --status Done
        """
    )
    
    # Required arguments
    parser.add_argument(
        'issue_key',
        help='Issue key to update (e.g., PZ-12345)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--summary',
        help='New summary'
    )
    
    parser.add_argument(
        '--description',
        help='New description'
    )
    
    parser.add_argument(
        '--priority',
        help='New priority (Lowest, Low, Medium, High, Highest)'
    )
    
    parser.add_argument(
        '--status',
        help='New status (e.g., "In Progress", "Done")'
    )
    
    parser.add_argument(
        '--assignee',
        help='New assignee username or account ID'
    )
    
    parser.add_argument(
        '--labels',
        help='Comma-separated list of labels (replaces existing)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to jira_config.yaml (optional)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize Jira client
        client = JiraClient(config_path=args.config)
        
        # Parse labels if provided
        labels = None
        if args.labels:
            labels = [label.strip() for label in args.labels.split(',')]
        
        # Check if any update fields provided
        has_updates = any([
            args.summary,
            args.description,
            args.priority,
            args.assignee,
            args.labels,
            args.status
        ])
        
        if not has_updates:
            print("❌ No update fields provided. Use --help for usage.")
            return 1
        
        # Update issue
        logger.info(f"Updating issue: {args.issue_key}")
        updated_issue = client.update_issue(
            issue_key=args.issue_key,
            summary=args.summary,
            description=args.description,
            priority=args.priority,
            assignee=args.assignee,
            labels=labels,
            status=args.status
        )
        
        # Print results
        print("\n✅ Issue updated successfully!")
        print(f"   Key: {updated_issue['key']}")
        print(f"   URL: {updated_issue['url']}")
        print(f"   Summary: {updated_issue['summary']}")
        print(f"   Status: {updated_issue['status']}")
        print(f"   Priority: {updated_issue['priority'] or 'N/A'}")
        print(f"   Assignee: {updated_issue['assignee'] or 'Unassigned'}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to update issue: {e}")
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

