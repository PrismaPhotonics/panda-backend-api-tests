"""
Check and Revert Bug Tickets
============================

This script checks which tickets were updated and reverts any bug tickets
back to their original status.

Author: QA Automation Architect
Date: 2025-11-04
"""

import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Remove scripts directory from path to avoid conflicts with jira package
scripts_dir = str(project_root / "scripts")
if scripts_dir in sys.path:
    sys.path.remove(scripts_dir)

# Import JiraAgent directly
from external.jira.jira_agent import JiraAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    # Tickets that were updated in the previous run
    updated_tickets = [
        'PZ-14110',  # The frequency filter validation alert is wrong
        'PZ-13974',  # Test the support large number of alerts
        'PZ-13967',  # Test Alert Grouping Feature - Rule setup
        'PZ-13965',  # Create Test Plan to Alert Grouping feature
        'PZ-13922',  # There's no option to login the Panda app with the new wep ip address
        'PZ-13482',  # [Panda] Associate new alert with a specific group (Part 3)
        'PZ-13481',  # [Panda] Associate new alert with a specific group (Part 2)
        'PZ-13444',  # After electricity failure there's no option to run live analysis
    ]
    
    # Original statuses (need to check from Jira)
    original_statuses = {
        'PZ-14110': 'TO DO',
        'PZ-13974': 'TO DO',
        'PZ-13967': 'TO DO',
        'PZ-13965': 'Working',
        'PZ-13922': 'TO DO',
        'PZ-13482': 'CLOSED',
        'PZ-13481': 'CLOSED',
        'PZ-13444': 'TO DO',
    }
    
    # Initialize Jira agent
    agent = JiraAgent()
    
    logger.info("=" * 80)
    logger.info("Checking and Reverting Bug Tickets")
    logger.info("=" * 80)
    
    bugs_to_revert = []
    other_tickets = []
    
    for ticket_key in updated_tickets:
        try:
            # Get issue details
            issue = agent.get_issue(ticket_key)
            issue_type = issue.get('issue_type', '').lower()
            current_status = issue.get('status', '')
            summary = issue.get('summary', '')
            
            logger.info(f"\nChecking {ticket_key}: {summary}")
            logger.info(f"  Issue Type: {issue_type}")
            logger.info(f"  Current Status: {current_status}")
            
            # Check if it's a bug
            if issue_type == 'bug':
                bugs_to_revert.append({
                    'key': ticket_key,
                    'summary': summary,
                    'current_status': current_status,
                    'original_status': original_statuses.get(ticket_key, 'TO DO')
                })
                logger.warning(f"  ⚠️  BUG FOUND - Needs to be reverted!")
            else:
                other_tickets.append({
                    'key': ticket_key,
                    'summary': summary,
                    'issue_type': issue_type,
                    'current_status': current_status
                })
                logger.info(f"  ✅ Not a bug - OK to keep updated")
        
        except Exception as e:
            logger.error(f"Failed to check {ticket_key}: {e}")
    
    # Revert bug tickets
    if bugs_to_revert:
        logger.info("\n" + "=" * 80)
        logger.info("Reverting Bug Tickets")
        logger.info("=" * 80)
        
        for bug in bugs_to_revert:
            key = bug['key']
            current_status = bug['current_status']
            original_status = bug['original_status']
            
            logger.info(f"\nReverting {key}: {bug['summary']}")
            logger.info(f"  From: {current_status} → To: {original_status}")
            
            try:
                # Revert to original status
                agent.update_status(key, original_status)
                
                # Add comment explaining the revert
                comment = (
                    f"⚠️ Status reverted - This is a bug ticket.\n"
                    f"Bug tickets should not be automatically updated by automation scripts.\n"
                    f"Reverted from '{current_status}' back to '{original_status}'.\n"
                    f"Please handle bug tickets manually."
                )
                agent.add_comment(key, comment)
                
                logger.info(f"  ✅ Successfully reverted {key}")
            
            except Exception as e:
                logger.error(f"  ❌ Failed to revert {key}: {e}")
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("Summary")
    logger.info("=" * 80)
    logger.info(f"Bug tickets found: {len(bugs_to_revert)}")
    logger.info(f"Other tickets (OK): {len(other_tickets)}")
    
    if bugs_to_revert:
        logger.info("\nBug tickets that were reverted:")
        for bug in bugs_to_revert:
            logger.info(f"  - {bug['key']}: {bug['summary']}")
    
    if other_tickets:
        logger.info("\nOther tickets (kept updated):")
        for ticket in other_tickets:
            logger.info(f"  - {ticket['key']}: {ticket['summary']} ({ticket['issue_type']})")


if __name__ == "__main__":
    main()


