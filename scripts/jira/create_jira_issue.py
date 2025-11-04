"""
Create Jira Issue Script
========================

Command-line script for creating Jira issues.

Usage:
    python scripts/jira/create_jira_issue.py --summary "Bug in API" --type Bug --priority High
    python scripts/jira/create_jira_issue.py --summary "New Task" --description "Task description" --labels automation,qa
    python scripts/jira/create_jira_issue.py --template bug --summary "Critical Bug" --project PZ
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
    """Main function for creating Jira issues."""
    parser = argparse.ArgumentParser(
        description='Create a new Jira issue',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a bug
  python create_jira_issue.py --summary "Bug in API" --type Bug --priority High
  
  # Create a task using template
  python create_jira_issue.py --template task --summary "New Task" --description "Task description"
  
  # Create a sub-task
  python create_jira_issue.py --summary "Sub-task" --type "Sub-task" --parent PZ-12345
  
  # Create with labels and assignee
  python create_jira_issue.py --summary "Task" --labels automation,qa --assignee john.doe
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--summary',
        required=True,
        help='Issue summary/title'
    )
    
    # Optional arguments
    parser.add_argument(
        '--description',
        help='Issue description'
    )
    
    parser.add_argument(
        '--type',
        '--issue-type',
        dest='issue_type',
        help='Issue type (Task, Bug, Story, Epic, Sub-task)'
    )
    
    parser.add_argument(
        '--priority',
        help='Priority (Lowest, Low, Medium, High, Highest)'
    )
    
    parser.add_argument(
        '--labels',
        help='Comma-separated list of labels'
    )
    
    parser.add_argument(
        '--assignee',
        help='Assignee username or account ID'
    )
    
    parser.add_argument(
        '--project',
        '--project-key',
        dest='project_key',
        help='Project key (defaults to config)'
    )
    
    parser.add_argument(
        '--parent',
        '--parent-key',
        dest='parent_key',
        help='Parent issue key (required for Sub-task)'
    )
    
    parser.add_argument(
        '--template',
        help='Use predefined template (bug, task, story, epic, sub_task)'
    )
    
    parser.add_argument(
        '--components',
        help='Comma-separated list of component names'
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
        
        # Parse components if provided
        components = None
        if args.components:
            components = [comp.strip() for comp in args.components.split(',')]
        
        # Create issue
        if args.template:
            # Use template
            logger.info(f"Creating issue using template: {args.template}")
            issue = client.create_issue_from_template(
                template_name=args.template,
                summary=args.summary,
                description=args.description,
                priority=args.priority,
                labels=labels,
                assignee=args.assignee,
                components=components,
                project_key=args.project_key,
                parent_key=args.parent_key
            )
        else:
            # Create directly
            logger.info("Creating issue...")
            issue = client.create_issue(
                summary=args.summary,
                description=args.description,
                issue_type=args.issue_type,
                priority=args.priority,
                labels=labels,
                assignee=args.assignee,
                components=components,
                project_key=args.project_key,
                parent_key=args.parent_key
            )
        
        # Print results
        print("\n✅ Issue created successfully!")
        print(f"   Key: {issue['key']}")
        print(f"   URL: {issue['url']}")
        print(f"   Summary: {issue['summary']}")
        print(f"   Status: {issue['status']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to create issue: {e}")
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

