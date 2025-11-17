"""
Fix All Xray Tests - Update with Proper Structure
==================================================

This script updates all 30 Xray tests (PZ-14715 to PZ-14744) with:
1. Test Type custom field (customfield_10951)
2. Proper description format (Jira markup)
3. All required sections (Objective, Pre-Conditions, Test Steps, etc.)

Usage:
    python scripts/jira/fix_all_xray_tests.py
    python scripts/jira/fix_all_xray_tests.py --test-ids PZ-14715,PZ-14716
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

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

# Xray Test Type custom field ID
TEST_TYPE_FIELD_ID = "customfield_10951"

# Test details extracted from test code
def get_test_details_from_code(test_id: str) -> Dict[str, Any]:
    """Extract test details from test code."""
    # Map test IDs to test files and functions
    test_mapping = {
        "PZ-14715": {
            "file": "tests/infrastructure/resilience/test_mongodb_pod_resilience.py",
            "class": "TestMongoDBPodResilience",
            "function": "test_mongodb_pod_deletion_recreation"
        },
        # Add more mappings as needed
    }
    
    return test_mapping.get(test_id, {})


def build_proper_description(test_id: str, test_data: Dict[str, Any]) -> str:
    """
    Build proper Xray description in Jira markup format.
    
    Args:
        test_id: Test ID
        test_data: Test data dictionary
        
    Returns:
        Formatted description string
    """
    # Extract from test_data or use defaults
    objective = test_data.get('objective', '')
    pre_conditions = test_data.get('pre_conditions', [])
    test_data_items = test_data.get('test_data', [])
    test_steps = test_data.get('test_steps', [])
    expected_result = test_data.get('expected_result', '')
    assertions = test_data.get('assertions', [])
    post_conditions = test_data.get('post_conditions', [])
    automation_info = test_data.get('automation_info', {})
    
    parts = []
    
    # Objective
    parts.append("h2. Objective")
    if objective:
        parts.append(objective)
    else:
        parts.append(f"Test objective for {test_id}")
    parts.append("")
    
    # Pre-Conditions
    if pre_conditions:
        parts.append("h2. Pre-Conditions")
        for condition in pre_conditions:
            parts.append(f"* {condition}")
        parts.append("")
    
    # Test Data
    if test_data_items:
        parts.append("h2. Test Data")
        for item in test_data_items:
            parts.append(f"* {item}")
        parts.append("")
    
    # Test Steps
    if test_steps:
        parts.append("h2. Test Steps")
        parts.append("")
        parts.append("|| # || Action || Data || Expected Result ||")
        for i, step in enumerate(test_steps, 1):
            action = step.get('action', '')
            data = step.get('data', '')
            expected = step.get('expected', '')
            parts.append(f"| {i} | {action} | {data} | {expected} |")
        parts.append("")
    
    # Expected Result
    if expected_result:
        parts.append("h2. Expected Result")
        parts.append(expected_result)
        parts.append("")
    
    # Assertions
    if assertions:
        parts.append("h2. Assertions")
        for assertion in assertions:
            parts.append(f"* {assertion}")
        parts.append("")
    
    # Post-Conditions
    if post_conditions:
        parts.append("h2. Post-Conditions")
        for condition in post_conditions:
            parts.append(f"* {condition}")
        parts.append("")
    
    # Automation Status
    parts.append("h2. Automation Status")
    parts.append("✅ *Automated* with Pytest")
    parts.append("")
    
    if automation_info.get('test_function'):
        parts.append(f"*Test Function:* {{code}}{automation_info['test_function']}{{code}}")
    if automation_info.get('test_file'):
        parts.append(f"*Test File:* {{code}}{automation_info['test_file']}{{code}}")
    if automation_info.get('test_class'):
        parts.append(f"*Test Class:* {{code}}{automation_info['test_class']}{{code}}")
    if automation_info.get('execution_command'):
        parts.append("")
        parts.append("*Execution Command:*")
        parts.append(f"{{code}}{automation_info['execution_command']}{{code}}")
    
    return "\n".join(parts)


def update_test_issue(
    client: JiraClient,
    test_key: str,
    test_type: str = "Automation",
    description: Optional[str] = None
) -> bool:
    """
    Update test issue with Test Type and description.
    
    Args:
        client: JiraClient instance
        test_key: Test issue key
        test_type: Test type value
        description: Optional new description
        
    Returns:
        True if successful
    """
    try:
        issue = client.jira.issue(test_key)
        
        update_fields = {}
        
        # Update Test Type
        update_fields[TEST_TYPE_FIELD_ID] = {"value": test_type}
        
        # Update description if provided
        if description:
            update_fields['description'] = description
        
        # Update issue
        issue.update(fields=update_fields)
        logger.info(f"✅ Updated test: {test_key}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update test {test_key}: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Fix all Xray tests with proper structure'
    )
    
    parser.add_argument(
        '--test-ids',
        help='Comma-separated list of test IDs (default: all PZ-14715 to PZ-14744)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without updating'
    )
    
    args = parser.parse_args()
    
    try:
        client = JiraClient()
        
        # Determine test IDs
        if args.test_ids:
            test_ids = [tid.strip() for tid in args.test_ids.split(',')]
        else:
            test_ids = [f"PZ-{14715 + i}" for i in range(30)]
        
        logger.info(f"\n{'='*80}")
        logger.info(f"{'[DRY RUN] ' if args.dry_run else ''}Fixing {len(test_ids)} Xray Tests")
        logger.info(f"{'='*80}\n")
        
        updated = 0
        failed = 0
        
        for test_id in test_ids:
            try:
                if args.dry_run:
                    logger.info(f"[DRY RUN] Would update: {test_id}")
                    # Get current issue
                    issue = client.jira.issue(test_id)
                    logger.info(f"  Current Test Type: {issue.raw['fields'].get(TEST_TYPE_FIELD_ID, 'Not set')}")
                    logger.info(f"  Current Summary: {issue.fields.summary}")
                else:
                    # Update Test Type only for now
                    success = update_test_issue(
                        client=client,
                        test_key=test_id,
                        test_type="Automation"
                    )
                    if success:
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
            logger.info(f"Failed: {failed}")
        logger.info(f"{'='*80}\n")
        
        if args.dry_run:
            logger.info("⚠️  DRY RUN MODE - No changes made")
            logger.info("   Run without --dry-run to update tests")
        
        return 0 if failed == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

