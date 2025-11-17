"""
Create Alert Tests via Atlassian Rovo API
==========================================

This script creates all alert test cases in Jira using Atlassian Rovo MCP API
and then organizes them into Xray folders.

Usage:
    python scripts/create_alerts_tests_via_rovo.py
"""

import sys
import os
from pathlib import Path
import logging
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.create_alert_test_tickets import TEST_CASES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cloud ID for Prisma Jira
CLOUD_ID = "a8cc7b3d-f5fd-41a1-a7ca-b9fc4ddfe0b4"
PROJECT_KEY = "PZ"
ISSUE_TYPE = "Test"

# Base folder ID
BASE_FOLDER_ID = "68d91b9f681e183ea2e83e16"

# Category to folder mapping
CATEGORY_FOLDERS = {
    "Positive": "Positive Tests",
    "Negative": "Negative Tests",
    "Edge Case": "Edge Cases",
    "Load": "Load Tests",
    "Performance": "Performance Tests",
    "Investigation": "Investigation",
}


def create_test_via_rovo(test_case):
    """
    Create a test case via Atlassian Rovo API.
    This function should be called from a context where MCP tools are available.
    """
    from mcp_atlassian_rovo import createJiraIssue
    
    test_id = test_case["test_id"]
    summary = test_case["summary"]
    description = test_case["description"]
    category = test_case["category"]
    
    # Skip if marked as skip
    if test_case.get("skip"):
        logger.info(f"⏭️  SKIPPING {test_id}: {summary} (test is invalid)")
        return None
    
    try:
        # Create issue via Rovo API
        result = createJiraIssue(
            cloudId=CLOUD_ID,
            projectKey=PROJECT_KEY,
            issueTypeName=ISSUE_TYPE,
            summary=f"{test_id}: {summary}",
            description=description,
            additional_fields={
                "labels": [
                    "alert",
                    "integration-test",
                    category.lower().replace(" ", "-")
                ]
            }
        )
        
        created_key = result.get("key")
        logger.info(f"✅ CREATED {test_id}: {created_key} - {summary}")
        return created_key
        
    except Exception as e:
        logger.error(f"❌ FAILED {test_id}: {e}")
        return None


def main():
    """Main function - creates all tests."""
    logger.info("=" * 80)
    logger.info("Creating Alert Test Cases via Atlassian Rovo API")
    logger.info("=" * 80)
    
    created_tests = []
    skipped_tests = []
    failed_tests = []
    
    for test_case in TEST_CASES:
        test_id = test_case["test_id"]
        
        if test_case.get("skip"):
            skipped_tests.append(test_id)
            continue
        
        # Create test
        created_key = create_test_via_rovo(test_case)
        
        if created_key:
            created_tests.append({
                "test_id": test_id,
                "key": created_key,
                "category": test_case["category"]
            })
        else:
            failed_tests.append(test_id)
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total test cases: {len(TEST_CASES)}")
    logger.info(f"✅ Created: {len(created_tests)}")
    logger.info(f"⏭️  Skipped: {len(skipped_tests)}")
    logger.info(f"❌ Failed: {len(failed_tests)}")
    
    if created_tests:
        logger.info("\nCreated tests:")
        for test in created_tests:
            logger.info(f"  {test['test_id']}: {test['key']} ({test['category']})")
    
    logger.info("\n" + "=" * 80)
    logger.info("Next step: Organize tests into Xray folders")
    logger.info("=" * 80)
    
    return created_tests


if __name__ == "__main__":
    main()

