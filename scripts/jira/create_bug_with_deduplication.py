#!/usr/bin/env python3
"""
Script to create bug tickets in Jira with automatic deduplication.

This script demonstrates how to use the BugCreatorService to create bugs
from test failures while automatically checking for duplicates.

Usage:
    python scripts/jira/create_bug_with_deduplication.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira.bug_creator import BugCreatorService
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to demonstrate bug creation with deduplication."""
    
    # Initialize bug creator service
    service = BugCreatorService()
    
    try:
        # Example 1: Create bug from test failure
        logger.info("=" * 80)
        logger.info("Example 1: Creating bug from test failure")
        logger.info("=" * 80)
        
        bug1 = service.create_bug_from_test_failure(
            test_name="test_mongodb_connection_failure",
            error_message="pymongo.errors.ServerSelectionTimeoutError: mongodb:27017: [Errno -3] Temporary failure in name resolution",
            summary="Focus Server pod restarts due to MongoDB connection failure during initialization",
            description="Focus Server pod fails during startup due to MongoDB connection failure, causing repeated restarts until connection is restored.",
            priority="High",
            keywords=["mongodb", "connection", "restart", "pod", "kubernetes"],
            steps_to_reproduce=[
                "Deploy Focus Server pod",
                "MongoDB service is not ready or DNS is not available",
                "Pod tries to initialize FocusManager",
                "FocusManager tries to connect to MongoDB",
                "Connection fails with DNS resolution error",
                "Pod crashes and restarts"
            ],
            expected_result="Pod should wait for MongoDB to be available or retry connection with backoff instead of crashing.",
            actual_result="Pod crashes and restarts repeatedly until MongoDB connection is restored.",
            environment="staging"
        )
        
        if bug1:
            logger.info(f"✅ Created bug: {bug1['key']}")
            logger.info(f"   URL: {bug1['url']}")
        else:
            logger.info("⚠️  Similar bug already exists - skipping creation")
        
        # Example 2: Try to create duplicate bug (should be skipped)
        logger.info("\n" + "=" * 80)
        logger.info("Example 2: Attempting to create duplicate bug")
        logger.info("=" * 80)
        
        bug2 = service.create_bug_from_test_failure(
            test_name="test_mongodb_connection_failure_duplicate",
            error_message="pymongo.errors.ServerSelectionTimeoutError: mongodb:27017: [Errno -3] Temporary failure in name resolution",
            summary="Focus Server pod restarts due to MongoDB connection failure during initialization",
            description="Focus Server pod fails during startup due to MongoDB connection failure.",
            priority="High",
            keywords=["mongodb", "connection", "restart"]
        )
        
        if bug2:
            logger.info(f"✅ Created bug: {bug2['key']}")
        else:
            logger.info("⚠️  Similar bug already exists - skipping creation (as expected)")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    
    finally:
        service.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

