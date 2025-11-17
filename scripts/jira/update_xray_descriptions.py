#!/usr/bin/env python3
"""
Update Xray Test Descriptions with Proper Jira Markup Format
============================================================

This script updates all 30 Xray tests (PZ-14715 to PZ-14744) with proper
Jira markup formatted descriptions.

Usage:
    python scripts/jira/update_xray_descriptions.py
    python scripts/jira/update_xray_descriptions.py --dry-run
    python scripts/jira/update_xray_descriptions.py --test-ids PZ-14715,PZ-14716
"""

import argparse
import sys
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

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


def convert_markdown_to_jira_markup(text: str) -> str:
    """
    Convert Markdown format to Jira markup format.
    
    Args:
        text: Markdown formatted text
        
    Returns:
        Jira markup formatted text
    """
    # Convert ## headers to h2.
    text = re.sub(r'^##\s+(.+)$', r'h2. \1', text, flags=re.MULTILINE)
    
    # Convert ### headers to h3.
    text = re.sub(r'^###\s+(.+)$', r'h3. \1', text, flags=re.MULTILINE)
    
    # Convert **bold** to *bold*
    text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)
    
    # Convert `code` to {code}code{code}
    text = re.sub(r'`([^`]+)`', r'{code}\1{code}', text)
    
    # Convert ```bash blocks to {code} blocks
    text = re.sub(r'```bash\n(.+?)\n```', r'{code}\n\1\n{code}', text, flags=re.DOTALL)
    text = re.sub(r'```\n(.+?)\n```', r'{code}\n\1\n{code}', text, flags=re.DOTALL)
    
    return text


def build_proper_description(test_id: str, test_data: Dict[str, Any]) -> str:
    """
    Build proper Xray description in Jira markup format.
    
    Args:
        test_id: Test ID (e.g., PZ-14715)
        test_data: Test data dictionary with all sections
        
    Returns:
        Formatted description string in Jira markup
    """
    parts = []
    
    # Objective
    parts.append("h2. Objective")
    objective = test_data.get('objective', '')
    if objective:
        parts.append(objective)
    else:
        parts.append(f"Test objective for {test_id}")
    parts.append("")
    
    # Pre-Conditions
    pre_conditions = test_data.get('pre_conditions', [])
    if pre_conditions:
        parts.append("h2. Pre-Conditions")
        for condition in pre_conditions:
            parts.append(f"* {condition}")
        parts.append("")
    
    # Test Data
    test_data_items = test_data.get('test_data', [])
    if test_data_items:
        parts.append("h2. Test Data")
        for item in test_data_items:
            parts.append(f"* {item}")
        parts.append("")
    
    # Test Steps (as table)
    test_steps = test_data.get('test_steps', [])
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
    expected_result = test_data.get('expected_result', '')
    if expected_result:
        parts.append("h2. Expected Result")
        if isinstance(expected_result, list):
            for item in expected_result:
                parts.append(f"* {item}")
        else:
            parts.append(expected_result)
        parts.append("")
    
    # Assertions
    assertions = test_data.get('assertions', [])
    if assertions:
        parts.append("h2. Assertions")
        for assertion in assertions:
            parts.append(f"* {assertion}")
        parts.append("")
    
    # Post-Conditions
    post_conditions = test_data.get('post_conditions', [])
    if post_conditions:
        parts.append("h2. Post-Conditions")
        for condition in post_conditions:
            parts.append(f"* {condition}")
        parts.append("")
    
    # Automation Status
    parts.append("h2. Automation Status")
    parts.append("*Automated* with Pytest")
    parts.append("")
    
    automation_info = test_data.get('automation_info', {})
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


# Test data mapping - extracted from test code
TEST_DATA_MAP = {
    "PZ-14715": {
        "objective": "Validate that when MongoDB pod is deleted, Kubernetes automatically recreates it and the system recovers. This ensures high availability and resilience of the database layer, preventing data loss and service interruptions.",
        "pre_conditions": [
            "Kubernetes cluster is accessible",
            "MongoDB deployment exists in namespace 'panda'",
            "MongoDB is accessible and functioning"
        ],
        "test_data": [
            "Namespace: panda",
            "Deployment: mongodb",
            "Label selector: app=mongodb"
        ],
        "test_steps": [
            {"action": "Get current MongoDB pod name", "data": "namespace: panda, label: app=mongodb", "expected": "Pod name retrieved"},
            {"action": "Verify MongoDB is accessible", "data": "MongoDB connection test", "expected": "MongoDB connection successful"},
            {"action": "Delete MongoDB pod", "data": "kubectl delete pod <pod_name>", "expected": "Pod deletion initiated"},
            {"action": "Wait for pod deletion", "data": "Timeout: 30 seconds", "expected": "Pod deleted successfully"},
            {"action": "Wait for new pod to be created", "data": "Timeout: 60 seconds", "expected": "New pod created automatically"},
            {"action": "Wait for new pod to be ready", "data": "Timeout: 120 seconds", "expected": "Pod status: Running, Ready: True"},
            {"action": "Verify MongoDB connection restored", "data": "MongoDB connection test", "expected": "MongoDB connection successful"},
            {"action": "Verify system functionality restored", "data": "Create test job via API", "expected": "Job created successfully"}
        ],
        "expected_result": [
            "Pod deleted successfully",
            "New pod created automatically within 60 seconds",
            "New pod becomes ready within 120 seconds",
            "MongoDB connection restored",
            "System functionality restored"
        ],
        "assertions": [
            "Pod deleted successfully",
            "New pod created automatically within 60 seconds",
            "New pod becomes ready within 120 seconds",
            "MongoDB connection restored",
            "System functionality restored"
        ],
        "post_conditions": [
            "MongoDB pod is running",
            "MongoDB connection is restored",
            "System functionality is verified"
        ],
        "automation_info": {
            "test_function": "test_mongodb_pod_deletion_recreation",
            "test_file": "tests/infrastructure/resilience/test_mongodb_pod_resilience.py",
            "test_class": "TestMongoDBPodResilience",
            "execution_command": "pytest tests/infrastructure/resilience/test_mongodb_pod_resilience.py::TestMongoDBPodResilience::test_mongodb_pod_deletion_recreation -v"
        }
    }
    # Add more test data as needed...
}


def update_test_description(
    client: JiraClient,
    test_key: str,
    description: str,
    dry_run: bool = False
) -> bool:
    """
    Update test issue description.
    
    Args:
        client: JiraClient instance
        test_key: Test issue key
        description: New description in Jira markup
        dry_run: If True, only preview changes
        
    Returns:
        True if successful
    """
    try:
        if dry_run:
            logger.info(f"[DRY RUN] Would update description for: {test_key}")
            issue = client.jira.issue(test_key)
            current_desc = issue.fields.description or ""
            logger.info(f"  Current description length: {len(current_desc)} chars")
            logger.info(f"  New description length: {len(description)} chars")
            logger.info(f"  Preview (first 200 chars): {description[:200]}...")
            return True
        
        issue = client.jira.issue(test_key)
        issue.update(fields={'description': description})
        logger.info(f"Updated description for: {test_key}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update description for {test_key}: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Update Xray test descriptions with proper Jira markup format'
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
        logger.info(f"{'[DRY RUN] ' if args.dry_run else ''}Updating {len(test_ids)} Xray Test Descriptions")
        logger.info(f"{'='*80}\n")
        
        updated = 0
        failed = 0
        
        for test_id in test_ids:
            try:
                # Get current issue
                issue = client.jira.issue(test_id)
                current_desc = issue.fields.description or ""
                
                if not current_desc:
                    logger.warning(f"No description found for {test_id}, skipping...")
                    continue
                
                # Convert Markdown to Jira markup
                description = convert_markdown_to_jira_markup(current_desc)
                
                # Update description
                success = update_test_description(
                    client=client,
                    test_key=test_id,
                    description=description,
                    dry_run=args.dry_run
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
            logger.info("DRY RUN MODE - No changes made")
            logger.info("Run without --dry-run to update descriptions")
        
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

