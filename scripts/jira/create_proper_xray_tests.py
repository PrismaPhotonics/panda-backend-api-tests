"""
Create Proper Xray Tests - With Correct Structure
==================================================

This script creates/updates Xray tests with proper structure:
1. Proper description format (Jira markup: h2., *, ||, {code})
2. Test Steps table
3. All required sections

Usage:
    python scripts/jira/create_proper_xray_tests.py --update-existing
    python scripts/jira/create_proper_xray_tests.py --test-id PZ-14715
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
import ast
import inspect

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

# Test mapping: Test ID -> Test file and function
TEST_MAPPING = {
    "PZ-14715": {
        "file": "tests/infrastructure/resilience/test_mongodb_pod_resilience.py",
        "class": "TestMongoDBPodResilience",
        "function": "test_mongodb_pod_deletion_recreation"
    },
    "PZ-14716": {
        "file": "tests/infrastructure/resilience/test_mongodb_pod_resilience.py",
        "class": "TestMongoDBPodResilience",
        "function": "test_mongodb_scale_down_to_zero"
    },
    # Add more as needed
}


def extract_test_info_from_code(test_file: str, test_class: str, test_function: str) -> Dict[str, Any]:
    """
    Extract test information from test code.
    
    Args:
        test_file: Path to test file
        test_class: Test class name
        test_function: Test function name
        
    Returns:
        Dictionary with test information
    """
    test_path = project_root / test_file
    
    if not test_path.exists():
        logger.warning(f"Test file not found: {test_file}")
        return {}
    
    try:
        with open(test_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST
        tree = ast.parse(content)
        
        test_info = {
            'objective': '',
            'pre_conditions': [],
            'test_data': [],
            'test_steps': [],
            'expected_result': '',
            'assertions': [],
            'post_conditions': []
        }
        
        # Find the test class
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == test_class:
                # Find the test function
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == test_function:
                        # Extract docstring
                        docstring = ast.get_docstring(item)
                        if docstring:
                            # Parse docstring for test info
                            lines = docstring.split('\n')
                            current_section = None
                            
                            for line in lines:
                                line = line.strip()
                                if not line:
                                    continue
                                
                                # Detect sections
                                if 'Test:' in line or 'Validates' in line:
                                    test_info['objective'] += line + ' '
                                elif 'Steps:' in line:
                                    current_section = 'steps'
                                elif 'Expected:' in line:
                                    current_section = 'expected'
                                elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                                    if current_section == 'steps':
                                        step_text = line.split('.', 1)[1].strip() if '.' in line else line
                                        test_info['test_steps'].append({
                                            'action': step_text,
                                            'data': '',
                                            'expected': ''
                                        })
                                elif line.startswith('-'):
                                    if current_section == 'expected':
                                        test_info['expected_result'] += line[1:].strip() + ' '
                        
                        break
        
        return test_info
        
    except Exception as e:
        logger.error(f"Failed to extract test info: {e}")
        return {}


def build_proper_description(test_id: str, test_info: Dict[str, Any]) -> str:
    """
    Build proper Xray description in Jira markup format.
    
    Args:
        test_id: Test ID
        test_info: Test information dictionary
        
    Returns:
        Formatted description string
    """
    parts = []
    
    # Objective
    parts.append("h2. Objective")
    objective = test_info.get('objective', f'Test objective for {test_id}')
    if not objective.strip():
        objective = f"Validate system behavior for {test_id}"
    parts.append(objective.strip())
    parts.append("")
    
    # Pre-Conditions
    pre_conditions = test_info.get('pre_conditions', [
        "Kubernetes cluster is accessible",
        "System components are running",
        "Test environment is configured"
    ])
    if pre_conditions:
        parts.append("h2. Pre-Conditions")
        for condition in pre_conditions:
            parts.append(f"* {condition}")
        parts.append("")
    
    # Test Data
    test_data = test_info.get('test_data', [])
    if test_data:
        parts.append("h2. Test Data")
        for item in test_data:
            parts.append(f"* {item}")
        parts.append("")
    
    # Test Steps
    test_steps = test_info.get('test_steps', [])
    if test_steps:
        parts.append("h2. Test Steps")
        parts.append("")
        parts.append("|| # || Action || Data || Expected Result ||")
        for i, step in enumerate(test_steps, 1):
            action = step.get('action', '')
            data = step.get('data', 'N/A')
            expected = step.get('expected', 'Success')
            parts.append(f"| {i} | {action} | {data} | {expected} |")
        parts.append("")
    
    # Expected Result
    expected_result = test_info.get('expected_result', 'Test completes successfully')
    if expected_result:
        parts.append("h2. Expected Result")
        parts.append(expected_result.strip())
        parts.append("")
    
    # Assertions
    assertions = test_info.get('assertions', [])
    if assertions:
        parts.append("h2. Assertions")
        for assertion in assertions:
            parts.append(f"* {assertion}")
        parts.append("")
    
    # Post-Conditions
    post_conditions = test_info.get('post_conditions', [
        "System is restored to initial state",
        "No resources left running"
    ])
    if post_conditions:
        parts.append("h2. Post-Conditions")
        for condition in post_conditions:
            parts.append(f"* {condition}")
        parts.append("")
    
    # Automation Status
    test_mapping = TEST_MAPPING.get(test_id, {})
    if test_mapping:
        parts.append("h2. Automation Status")
        parts.append("✅ *Automated* with Pytest")
        parts.append("")
        
        if test_mapping.get('test_function'):
            parts.append(f"*Test Function:* {{code}}{test_mapping['test_function']}{{code}}")
        if test_mapping.get('test_file'):
            parts.append(f"*Test File:* {{code}}{test_mapping['test_file']}{{code}}")
        if test_mapping.get('test_class'):
            parts.append(f"*Test Class:* {{code}}{test_mapping['test_class']}{{code}}")
        
        # Execution command
        if test_mapping.get('test_file') and test_mapping.get('test_class') and test_mapping.get('test_function'):
            exec_cmd = f"pytest {test_mapping['test_file']}::{test_mapping['test_class']}::{test_mapping['test_function']} -v"
            parts.append("")
            parts.append("*Execution Command:*")
            parts.append(f"{{code}}{exec_cmd}{{code}}")
    
    return "\n".join(parts)


def update_test_description(
    client: JiraClient,
    test_key: str,
    description: str
) -> bool:
    """
    Update test description.
    
    Args:
        client: JiraClient instance
        test_key: Test issue key
        description: New description
        
    Returns:
        True if successful
    """
    try:
        issue = client.jira.issue(test_key)
        issue.update(fields={'description': description})
        logger.info(f"✅ Updated description for: {test_key}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to update {test_key}: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Create/update Xray tests with proper structure'
    )
    
    parser.add_argument(
        '--update-existing',
        action='store_true',
        help='Update existing tests (PZ-14715 to PZ-14744)'
    )
    
    parser.add_argument(
        '--test-id',
        help='Update specific test ID'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without updating'
    )
    
    args = parser.parse_args()
    
    try:
        client = JiraClient()
        
        # Determine which tests to update
        if args.test_id:
            test_ids = [args.test_id]
        elif args.update_existing:
            test_ids = [f"PZ-{14715 + i}" for i in range(30)]
        else:
            logger.error("Specify --update-existing or --test-id")
            return 1
        
        logger.info(f"\n{'='*80}")
        logger.info(f"{'[DRY RUN] ' if args.dry_run else ''}Updating {len(test_ids)} tests")
        logger.info(f"{'='*80}\n")
        
        updated = 0
        failed = 0
        
        for test_id in test_ids:
            try:
                # Get test mapping
                test_mapping = TEST_MAPPING.get(test_id, {})
                
                # Extract test info from code
                test_info = {}
                if test_mapping:
                    test_info = extract_test_info_from_code(
                        test_mapping.get('file', ''),
                        test_mapping.get('class', ''),
                        test_mapping.get('function', '')
                    )
                
                # Build description
                description = build_proper_description(test_id, test_info)
                
                if args.dry_run:
                    logger.info(f"[DRY RUN] Would update: {test_id}")
                    logger.info(f"  Description length: {len(description)} chars")
                    logger.info(f"  Preview: {description[:200]}...")
                else:
                    success = update_test_description(client, test_id, description)
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
        
        return 0 if failed == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

