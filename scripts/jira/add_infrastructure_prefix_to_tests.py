#!/usr/bin/env python3
"""
Add "Infrastructure - " Prefix to Test Titles
==============================================

This script adds "Infrastructure - " prefix to the summary (title) of 
all tests specified in the JQL query.

Usage:
    python scripts/jira/add_infrastructure_prefix_to_tests.py
    python scripts/jira/add_infrastructure_prefix_to_tests.py --dry-run
    python scripts/jira/add_infrastructure_prefix_to_tests.py --test-ids PZ-14715,PZ-14716
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional

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

# Prefix to add
PREFIX = "Infrastructure - "


def update_test_summary(
    client: JiraClient,
    test_key: str,
    prefix: str = PREFIX,
    dry_run: bool = False
) -> bool:
    """
    Update test summary by adding prefix if not already present.
    
    Args:
        client: JiraClient instance
        test_key: Test issue key (e.g., "PZ-14715")
        prefix: Prefix to add to summary
        dry_run: If True, only preview changes
        
    Returns:
        True if successful
    """
    try:
        # Get current issue
        issue = client.jira.issue(test_key)
        current_summary = issue.fields.summary
        
        # Check if prefix already exists
        if current_summary.startswith(prefix):
            logger.info(f"⏭️  {test_key}: Prefix already exists - '{current_summary}'")
            return True
        
        # Add prefix
        new_summary = prefix + current_summary
        
        if dry_run:
            logger.info(f"[DRY RUN] Would update {test_key}:")
            logger.info(f"  Current: '{current_summary}'")
            logger.info(f"  New:     '{new_summary}'")
            return True
        
        # Update issue
        issue.update(fields={'summary': new_summary})
        logger.info(f"✅ Updated {test_key}: '{new_summary}'")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update {test_key}: {e}")
        return False


def get_test_ids_from_jql(jql: str, client: JiraClient) -> List[str]:
    """
    Get test IDs from JQL query.
    
    Args:
        jql: JQL query string
        client: JiraClient instance
        
    Returns:
        List of test issue keys
    """
    try:
        issues = client.jira.search_issues(jql, maxResults=1000)
        test_ids = [issue.key for issue in issues]
        logger.info(f"Found {len(test_ids)} tests from JQL query")
        return test_ids
    except Exception as e:
        logger.error(f"Failed to get test IDs from JQL: {e}")
        return []


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Add "Infrastructure - " prefix to test titles'
    )
    
    parser.add_argument(
        '--test-ids',
        help='Comma-separated list of test IDs (default: from JQL query)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without updating'
    )
    
    parser.add_argument(
        '--jql',
        default='issue in (43342,43343,43344,43461,43462,43463,45353,45354,45355,45356,45357,45358,45359,45360,45361,45362,45363,45364,45365,45366,45367,45368,45369,45370,45371,45372,45373,45374,45375,45376,45377,45378,45379,45380,45381,45382)',
        help='JQL query to find tests (default: from the provided link)'
    )
    
    args = parser.parse_args()
    
    try:
        client = JiraClient()
        
        # Determine test IDs
        if args.test_ids:
            test_ids = [tid.strip() for tid in args.test_ids.split(',')]
        else:
            # Get test IDs from JQL query
            test_ids = get_test_ids_from_jql(args.jql, client)
        
        if not test_ids:
            logger.error("❌ No test IDs found")
            return 1
        
        logger.info(f"\n{'='*80}")
        logger.info(f"{'[DRY RUN] ' if args.dry_run else ''}Updating {len(test_ids)} Test Titles")
        logger.info(f"{'='*80}\n")
        
        updated = 0
        skipped = 0
        failed = 0
        
        for test_id in test_ids:
            try:
                success = update_test_summary(
                    client=client,
                    test_key=test_id,
                    prefix=PREFIX,
                    dry_run=args.dry_run
                )
                
                if success:
                    # Check if it was skipped (prefix already exists)
                    issue = client.jira.issue(test_id)
                    if issue.fields.summary.startswith(PREFIX):
                        if not args.dry_run:
                            skipped += 1
                        updated += 1
                    else:
                        updated += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Failed to process {test_id}: {e}")
                failed += 1
        
        logger.info(f"\n{'='*80}")
        logger.info("SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Total: {len(test_ids)}")
        if not args.dry_run:
            logger.info(f"Updated: {updated}")
            logger.info(f"Skipped (already has prefix): {skipped}")
            logger.info(f"Failed: {failed}")
        logger.info(f"{'='*80}\n")
        
        if args.dry_run:
            logger.info("⚠️  DRY RUN MODE - No changes made")
            logger.info("   Run without --dry-run to update test titles")
        
        return 0 if failed == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        client.close()


if __name__ == '__main__':
    sys.exit(main())

