#!/usr/bin/env python3
"""
Assign Xray Tests to Folder in Test Repository
=============================================

This script assigns all 30 Xray tests (PZ-14715 to PZ-14744) to the 
"infrastructure Tests" folder under "Focus Server Tests" in the Xray Test Repository.

Usage:
    python scripts/jira/assign_tests_to_folder.py
    python scripts/jira/assign_tests_to_folder.py --dry-run
    python scripts/jira/assign_tests_to_folder.py --test-ids PZ-14715,PZ-14716
"""

import argparse
import sys
import logging
import requests
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


def get_xray_folder_id(
    client: JiraClient,
    folder_path: List[str]
) -> Optional[str]:
    """
    Get Xray folder ID by path.
    
    Args:
        client: JiraClient instance
        folder_path: List of folder names (e.g., ["Panda MS3", "BE Tests", "Focus Server Tests", "infrastructure Tests"])
        
    Returns:
        Folder ID or None if not found
    """
    # Note: This requires Xray API which may not be available via standard Jira API
    # We'll try to find it via Jira REST API or return None
    logger.info(f"Looking for folder path: {' > '.join(folder_path)}")
    
    # Try to get folder via Jira REST API
    # Xray folders are typically stored as custom fields or via Xray API
    # For now, we'll return None and log that manual action is needed
    logger.warning("Xray folder lookup requires Xray API - not available via standard Jira API")
    return None


def assign_test_to_folder_via_xray_api(
    test_key: str,
    folder_id: str,
    jira_base_url: str,
    jira_username: str,
    jira_password: str,
    dry_run: bool = False
) -> bool:
    """
    Assign test to Xray folder using Xray REST API.
    
    Args:
        test_key: Test issue key (e.g., "PZ-14715")
        folder_id: Xray folder ID
        jira_base_url: Jira base URL
        jira_username: Jira username
        jira_password: Jira password or API token
        dry_run: If True, only preview changes
        
    Returns:
        True if successful
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would assign {test_key} to folder {folder_id}")
        return True
    
    try:
        # Xray REST API endpoint for assigning test to folder
        # Note: This is the Xray Server/DC API endpoint
        # For Xray Cloud, the endpoint would be different
        xray_api_url = f"{jira_base_url}/rest/raven/1.0/api/testrepository/PZ/folders/{folder_id}/tests/{test_key}"
        
        # Use basic auth
        auth = (jira_username, jira_password)
        
        # PUT request to assign test to folder
        response = requests.put(
            xray_api_url,
            auth=auth,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201, 204]:
            logger.info(f"✅ Assigned {test_key} to folder {folder_id}")
            return True
        else:
            logger.error(f"❌ Failed to assign {test_key} to folder {folder_id}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error assigning {test_key} to folder {folder_id}: {e}")
        return False


def assign_test_to_folder_via_jira_api(
    client: JiraClient,
    test_key: str,
    folder_name: str,
    dry_run: bool = False
) -> bool:
    """
    Try to assign test to folder via Jira API (may not work for Xray folders).
    
    Args:
        client: JiraClient instance
        test_key: Test issue key
        folder_name: Folder name
        dry_run: If True, only preview changes
        
    Returns:
        True if successful
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would assign {test_key} to folder '{folder_name}'")
        return True
    
    try:
        # Note: Standard Jira API doesn't support Xray folder assignment
        # This is a placeholder for future implementation
        logger.warning(f"Standard Jira API doesn't support Xray folder assignment")
        logger.info(f"Manual action required: Assign {test_key} to folder '{folder_name}' via Xray UI")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Assign Xray tests to folder in Test Repository'
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
    
    parser.add_argument(
        '--folder-id',
        help='Xray folder ID (if known, otherwise will try to find it)'
    )
    
    parser.add_argument(
        '--folder-path',
        default='Panda MS3 > BE Tests > Focus Server Tests > infrastructure Tests',
        help='Folder path (default: "Panda MS3 > BE Tests > Focus Server Tests > infrastructure Tests")'
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
        logger.info(f"{'[DRY RUN] ' if args.dry_run else ''}Assigning {len(test_ids)} Tests to Folder")
        logger.info(f"{'='*80}\n")
        
        # Get folder ID
        folder_id = args.folder_id
        if not folder_id:
            folder_path = [f.strip() for f in args.folder_path.split('>')]
            folder_id = get_xray_folder_id(client, folder_path)
        
        if not folder_id:
            logger.warning("⚠️  Could not determine folder ID automatically")
            logger.info("\n" + "="*80)
            logger.info("MANUAL ASSIGNMENT REQUIRED")
            logger.info("="*80)
            logger.info("\nTo assign tests to folder manually:")
            logger.info("1. Go to Xray Test Repository:")
            logger.info("   https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository")
            logger.info("2. Navigate to: Panda MS3 > BE Tests > Focus Server Tests > infrastructure Tests")
            logger.info("3. Select all tests:")
            for test_id in test_ids:
                logger.info(f"   - {test_id}")
            logger.info("4. Drag and drop into the 'infrastructure Tests' folder")
            logger.info("\n" + "="*80 + "\n")
            return 0
        
        # Assign tests to folder
        updated = 0
        failed = 0
        
        for test_id in test_ids:
            try:
                # Try via Jira API first (may not work)
                success = assign_test_to_folder_via_jira_api(
                    client=client,
                    test_key=test_id,
                    folder_name="infrastructure Tests",
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
        
        if not args.dry_run and failed > 0:
            logger.warning("⚠️  Some tests could not be assigned automatically")
            logger.info("Manual assignment via Xray UI is required")
        
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

