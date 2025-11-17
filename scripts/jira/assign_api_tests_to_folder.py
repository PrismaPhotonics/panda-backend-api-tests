#!/usr/bin/env python3
"""
Assign API Endpoint Tests to Xray Folder
==========================================

This script helps assign API endpoint tests (PZ-14750 to PZ-14764) 
to the correct folder in Xray Test Repository.

Note: Xray folder assignment typically requires Xray API access.
This script provides JQL queries and instructions for manual assignment.

Usage:
    python scripts/jira/assign_api_tests_to_folder.py
    python scripts/jira/assign_api_tests_to_folder.py --dry-run
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

# Test keys to assign
API_ENDPOINT_TESTS = [
    "PZ-14750", "PZ-14751", "PZ-14752", "PZ-14753", "PZ-14754",
    "PZ-14755", "PZ-14756", "PZ-14757", "PZ-14758", "PZ-14759",
    "PZ-14760", "PZ-14761", "PZ-14762", "PZ-14763", "PZ-14764"
]


def generate_jql_query(test_keys: list) -> str:
    """
    Generate JQL query for finding tests.
    
    Args:
        test_keys: List of test issue keys
        
    Returns:
        JQL query string
    """
    # Format: project = PZ AND key IN (PZ-14750, PZ-14751, ...) ORDER BY key ASC
    keys_str = ", ".join(test_keys)
    jql = f"project = PZ AND key IN ({keys_str}) ORDER BY key ASC"
    return jql


def generate_jql_query_range() -> str:
    """
    Generate JQL query using range.
    
    Returns:
        JQL query string
    """
    return "project = PZ AND key >= PZ-14750 AND key <= PZ-14764 ORDER BY key ASC"


def verify_tests_exist(client: JiraClient, test_keys: list) -> dict:
    """
    Verify that all test issues exist.
    
    Args:
        client: JiraClient instance
        test_keys: List of test issue keys
        
    Returns:
        Dictionary with existing and missing tests
    """
    logger.info("Verifying test issues exist...")
    
    existing = []
    missing = []
    
    for test_key in test_keys:
        try:
            issue = client.jira.issue(test_key)
            existing.append({
                'key': test_key,
                'summary': issue.fields.summary,
                'url': f"https://prismaphotonics.atlassian.net/browse/{test_key}"
            })
            logger.info(f"✅ Found: {test_key} - {issue.fields.summary}")
        except Exception as e:
            missing.append(test_key)
            logger.warning(f"⚠️  Not found: {test_key} - {e}")
    
    return {
        'existing': existing,
        'missing': missing
    }


def print_assignment_instructions(test_keys: list):
    """
    Print instructions for manual folder assignment.
    
    Args:
        test_keys: List of test issue keys
    """
    jql_query = generate_jql_query(test_keys)
    jql_range = generate_jql_query_range()
    
    print("\n" + "=" * 80)
    print("XRAY FOLDER ASSIGNMENT INSTRUCTIONS")
    print("=" * 80)
    print("\nTests to Assign: 15 tests (PZ-14750 to PZ-14764)")
    print("\nTarget Folder:")
    print("   Panda MS3 -> BE Tests -> Focus Server Tests -> API Tests")
    print("\nJQL Query (Copy this):")
    print("-" * 80)
    print(jql_query)
    print("-" * 80)
    print("\nAlternative JQL Query (Range):")
    print("-" * 80)
    print(jql_range)
    print("-" * 80)
    print("\nSteps:")
    print("1. Navigate to Xray Test Repository:")
    print("   https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository")
    print("\n2. Navigate to folder:")
    print("   Panda MS3 -> BE Tests -> Focus Server Tests -> API Tests")
    print("\n3. Use search/filter and paste JQL query above")
    print("\n4. Select all 15 tests")
    print("\n5. Drag and drop to 'API Tests' folder")
    print("\n" + "=" * 80)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Generate JQL queries and instructions for assigning API tests to Xray folder'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Only print instructions without verifying tests'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify all tests exist in Jira'
    )
    
    args = parser.parse_args()
    
    try:
        if args.verify or not args.dry_run:
            client = JiraClient()
            
            # Verify tests exist
            result = verify_tests_exist(client, API_ENDPOINT_TESTS)
            
            print("\n" + "=" * 80)
            print("VERIFICATION RESULTS")
            print("=" * 80)
            print(f"[OK] Found: {len(result['existing'])} tests")
            print(f"[FAIL] Missing: {len(result['missing'])} tests")
            
            if result['missing']:
                print(f"\n[WARNING] Missing tests: {', '.join(result['missing'])}")
            
            client.close()
        
        # Print assignment instructions
        print_assignment_instructions(API_ENDPOINT_TESTS)
        
        # Print test list
        print("\nTest List:")
        print("-" * 80)
        for i, test_key in enumerate(API_ENDPOINT_TESTS, 1):
            print(f"{i:2d}. {test_key}")
        print("-" * 80)
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

