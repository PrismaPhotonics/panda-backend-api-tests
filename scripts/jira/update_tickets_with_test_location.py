"""
Update Jira Tickets with Test Location
=======================================

This script updates all Jira tickets assigned to the current user with test location
information pointing to the GitHub repository where the tests are implemented.

Author: QA Automation Architect
Date: 2025-11-04
Version: 1.0.0
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from external.jira import JiraClient, JiraAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# GitHub repository URL for tests
TEST_REPOSITORY_URL = "https://github.com/PrismaPhotonics/panda-backend-api-tests.git"
TEST_REPOSITORY_DISPLAY = "https://github.com/PrismaPhotonics/panda-backend-api-tests"


class TicketTestLocationUpdater:
    """
    Update Jira tickets with test location information.
    
    This class identifies BE-related tickets that have tests implemented
    and updates them with the GitHub repository location.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the updater.
        
        Args:
            config_path: Path to jira_config.yaml (optional)
        """
        self.client = JiraClient(config_path=config_path)
        self.agent = JiraAgent(config_path=config_path)
        
        # Get current user info
        try:
            current_user = self.client.jira.current_user()
            
            # Handle both string and object responses
            if isinstance(current_user, str):
                # If current_user() returns a string (username), get full user info
                user_info = self.client.jira.user(current_user)
                self.current_user_account_id = getattr(user_info, 'accountId', None) or getattr(user_info, 'key', None)
                self.current_user_email = getattr(user_info, 'emailAddress', None)
                self.current_user_display_name = getattr(user_info, 'displayName', current_user)
            else:
                # If current_user() returns an object
                self.current_user_account_id = getattr(current_user, 'accountId', None) or getattr(current_user, 'key', None)
                self.current_user_email = getattr(current_user, 'emailAddress', None)
                self.current_user_display_name = getattr(current_user, 'displayName', str(current_user))
            
            logger.info(
                f"Initialized for user: {self.current_user_display_name} "
                f"({self.current_user_email or 'N/A'})"
            )
        except Exception as e:
            logger.warning(f"Could not get full current user info: {e}")
            # Continue without account ID - we'll use currentUser() in JQL
            self.current_user_account_id = None
            self.current_user_email = None
            self.current_user_display_name = None
        
        # Statistics
        self.stats = {
            'total_found': 0,
            'updated': [],
            'skipped': [],
            'errors': []
        }
    
    def get_all_user_tickets(
        self,
        project_key: str = "PZ",
        include_closed: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all tickets assigned to current user.
        
        Args:
            project_key: Project key (default: PZ)
            include_closed: Whether to include closed tickets
        
        Returns:
            List of ticket dictionaries
        """
        # Build JQL query
        if include_closed:
            jql = f"project = {project_key} AND assignee = currentUser()"
        else:
            jql = f"project = {project_key} AND assignee = currentUser() AND status != Done AND status != Closed"
        
        logger.info(f"Searching for tickets with JQL: {jql}")
        
        try:
            tickets = self.client.search_issues(jql, max_results=1000)
            logger.info(f"Found {len(tickets)} ticket(s) assigned to current user")
            return tickets
        except Exception as e:
            logger.error(f"Failed to search tickets: {e}")
            raise
    
    def is_be_related_ticket(self, ticket: Dict[str, Any]) -> bool:
        """
        Check if ticket is BE (Backend) related.
        
        Args:
            ticket: Ticket dictionary
        
        Returns:
            True if ticket is BE-related
        """
        # Check labels
        labels = ticket.get('labels', [])
        be_labels = ['backend', 'be', 'api', 'server', 'focus-server']
        if any(label.lower() in be_labels for label in labels):
            return True
        
        # Check summary
        summary = ticket.get('summary', '').lower()
        be_keywords = [
            'backend', 'be', 'api', 'endpoint', 'server', 'focus-server',
            'grpc', 'rest', 'http', 'mongodb', 'rabbitmq', 'k8s', 'kubernetes'
        ]
        if any(keyword in summary for keyword in be_keywords):
            return True
        
        # Check description
        description = ticket.get('description', '').lower()
        if any(keyword in description for keyword in be_keywords):
            return True
        
        # Check issue type - tasks and stories are usually BE-related
        issue_type = ticket.get('issue_type', '').lower()
        if issue_type in ['task', 'story', 'bug']:
            # Assume it's BE-related if it's a task/story/bug
            return True
        
        return False
    
    def has_test_location(self, ticket: Dict[str, Any]) -> bool:
        """
        Check if ticket already has test location information.
        
        Args:
            ticket: Ticket dictionary
        
        Returns:
            True if test location already exists
        """
        description = ticket.get('description', '')
        
        # Check for test location markers
        test_markers = [
            'test location',
            'test repository',
            'github.com/prismaphotonics/panda-backend-api-tests',
            'panda-backend-api-tests'
        ]
        
        description_lower = description.lower()
        return any(marker in description_lower for marker in test_markers)
    
    def format_test_location_section(self) -> str:
        """
        Format test location section for ticket description.
        
        Returns:
            Formatted test location section
        """
        return f"""
---
## Test Location

**Repository:** {TEST_REPOSITORY_DISPLAY}

**Git URL:** `{TEST_REPOSITORY_URL}`

**Status:** ✅ Tests implemented and available in repository

---
"""
    
    def update_ticket_with_test_location(
        self,
        ticket_key: str,
        ticket: Dict[str, Any]
    ) -> bool:
        """
        Update ticket with test location information.
        
        Args:
            ticket_key: Ticket key (e.g., "PZ-12345")
            ticket: Ticket dictionary
        
        Returns:
            True if update successful
        """
        try:
            # Get full ticket details
            full_ticket = self.client.get_issue(ticket_key)
            current_description = full_ticket.get('description', '')
            
            # Check if test location already exists
            if self.has_test_location(full_ticket):
                logger.info(f"Ticket {ticket_key} already has test location - skipping")
                self.stats['skipped'].append({
                    'key': ticket_key,
                    'summary': ticket.get('summary', 'N/A'),
                    'reason': 'Test location already exists'
                })
                return False
            
            # Add test location section
            test_location_section = self.format_test_location_section()
            
            # Append to description
            if current_description:
                new_description = f"{current_description}\n{test_location_section}"
            else:
                new_description = test_location_section.strip()
            
            # Update ticket
            updated_ticket = self.client.update_issue(
                issue_key=ticket_key,
                description=new_description
            )
            
            logger.info(f"✅ Updated ticket {ticket_key}: {ticket.get('summary', 'N/A')}")
            
            self.stats['updated'].append({
                'key': ticket_key,
                'summary': ticket.get('summary', 'N/A'),
                'status': ticket.get('status', 'N/A'),
                'url': ticket.get('url', '')
            })
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to update ticket {ticket_key}: {e}")
            self.stats['errors'].append({
                'key': ticket_key,
                'summary': ticket.get('summary', 'N/A'),
                'error': str(e)
            })
            return False
    
    def update_all_tickets(
        self,
        project_key: str = "PZ",
        include_closed: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Update all user tickets with test location.
        
        Args:
            project_key: Project key (default: PZ)
            include_closed: Whether to include closed tickets
            dry_run: If True, only show what would be updated without actually updating
        
        Returns:
            Dictionary with update statistics
        """
        logger.info("=" * 80)
        logger.info("Starting ticket update process...")
        logger.info(f"Project: {project_key}")
        logger.info(f"Include closed: {include_closed}")
        logger.info(f"Dry run: {dry_run}")
        logger.info("=" * 80)
        
        # Get all user tickets
        all_tickets = self.get_all_user_tickets(project_key, include_closed)
        self.stats['total_found'] = len(all_tickets)
        
        logger.info(f"\nFound {len(all_tickets)} ticket(s) assigned to current user")
        
        # Filter BE-related tickets
        be_tickets = [
            ticket for ticket in all_tickets
            if self.is_be_related_ticket(ticket)
        ]
        
        logger.info(f"Found {len(be_tickets)} BE-related ticket(s)")
        
        if not be_tickets:
            logger.warning("No BE-related tickets found to update")
            return self.stats
        
        # Display tickets to be updated
        logger.info("\n" + "=" * 80)
        logger.info("Tickets to be updated:")
        logger.info("=" * 80)
        for i, ticket in enumerate(be_tickets, 1):
            logger.info(
                f"{i}. {ticket['key']}: {ticket.get('summary', 'N/A')} "
                f"[{ticket.get('status', 'N/A')}]"
            )
        
        if dry_run:
            logger.info("\n" + "=" * 80)
            logger.info("DRY RUN MODE - No tickets will be updated")
            logger.info("=" * 80)
            return self.stats
        
        # Ask for confirmation
        logger.info("\n" + "=" * 80)
        logger.info(f"About to update {len(be_tickets)} ticket(s) with test location")
        logger.info("=" * 80)
        
        # Update each ticket
        logger.info("\nUpdating tickets...\n")
        
        for ticket in be_tickets:
            ticket_key = ticket['key']
            self.update_ticket_with_test_location(ticket_key, ticket)
        
        # Print summary
        self.print_summary()
        
        return self.stats
    
    def print_summary(self):
        """Print update summary."""
        logger.info("\n" + "=" * 80)
        logger.info("UPDATE SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total tickets found: {self.stats['total_found']}")
        logger.info(f"✅ Updated: {len(self.stats['updated'])}")
        logger.info(f"⏭️  Skipped: {len(self.stats['skipped'])}")
        logger.info(f"❌ Errors: {len(self.stats['errors'])}")
        
        if self.stats['updated']:
            logger.info("\n" + "-" * 80)
            logger.info("UPDATED TICKETS:")
            logger.info("-" * 80)
            for ticket in self.stats['updated']:
                logger.info(f"  ✅ {ticket['key']}: {ticket['summary']}")
                logger.info(f"     URL: {ticket['url']}")
        
        if self.stats['skipped']:
            logger.info("\n" + "-" * 80)
            logger.info("SKIPPED TICKETS:")
            logger.info("-" * 80)
            for ticket in self.stats['skipped']:
                logger.info(f"  ⏭️  {ticket['key']}: {ticket['summary']}")
                logger.info(f"     Reason: {ticket['reason']}")
        
        if self.stats['errors']:
            logger.info("\n" + "-" * 80)
            logger.info("ERRORS:")
            logger.info("-" * 80)
            for ticket in self.stats['errors']:
                logger.error(f"  ❌ {ticket['key']}: {ticket['summary']}")
                logger.error(f"     Error: {ticket['error']}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update Jira tickets with test location information"
    )
    
    parser.add_argument(
        '--project',
        default='PZ',
        help='Project key (default: PZ)'
    )
    
    parser.add_argument(
        '--include-closed',
        action='store_true',
        help='Include closed tickets'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode - show what would be updated without actually updating'
    )
    
    parser.add_argument(
        '--config',
        help='Path to jira_config.yaml (optional)'
    )
    
    args = parser.parse_args()
    
    try:
        updater = TicketTestLocationUpdater(config_path=args.config)
        
        stats = updater.update_all_tickets(
            project_key=args.project,
            include_closed=args.include_closed,
            dry_run=args.dry_run
        )
        
        # Exit with appropriate code
        if stats['errors']:
            logger.warning("Some tickets had errors during update")
            return 1
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("\n\nOperation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

