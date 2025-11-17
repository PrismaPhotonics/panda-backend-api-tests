#!/usr/bin/env python3
"""
Assign Xray Tests to Folder via Jira REST API
============================================

This script attempts to assign all 30 Xray tests (PZ-14715 to PZ-14744) 
to the "infrastructure Tests" folder using Jira REST API directly.

Usage:
    python scripts/jira/assign_tests_to_folder_via_api.py
    python scripts/jira/assign_tests_to_folder_via_api.py --dry-run
"""

import argparse
import sys
import logging
import requests
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from base64 import b64encode

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_jira_config() -> Dict[str, Any]:
    """Load Jira configuration from config file."""
    config_path = project_root / "config" / "jira_config.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Jira config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_xray_folder_id_via_api(
    jira_base_url: str,
    auth: tuple,
    folder_path: List[str]
) -> Optional[str]:
    """
    Try to get Xray folder ID via Jira REST API.
    
    Args:
        jira_base_url: Jira base URL
        auth: Authentication tuple (username, password)
        folder_path: List of folder names
        
    Returns:
        Folder ID or None if not found
    """
    try:
        # Try Xray REST API endpoint for folder lookup
        # Note: This may not work without Xray API credentials
        api_url = f"{jira_base_url}/rest/raven/1.0/api/testrepository/PZ/folders"
        
        response = requests.get(
            api_url,
            auth=auth,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            folders = response.json()
            logger.info(f"Found {len(folders)} folders")
            # Try to find folder by path
            # This is a simplified approach - actual implementation may vary
            for folder in folders:
                if folder.get('name') == folder_path[-1]:
                    folder_id = folder.get('id')
                    logger.info(f"Found folder ID: {folder_id}")
                    return folder_id
        else:
            logger.warning(f"Failed to get folders: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.warning(f"Could not get folder ID via API: {e}")
    
    return None


def assign_test_to_folder_via_api(
    test_key: str,
    folder_id: str,
    jira_base_url: str,
    auth: tuple,
    dry_run: bool = False
) -> bool:
    """
    Assign test to Xray folder via Jira REST API.
    
    Args:
        test_key: Test issue key (e.g., "PZ-14715")
        folder_id: Xray folder ID
        jira_base_url: Jira base URL
        auth: Authentication tuple (username, password)
        dry_run: If True, only preview changes
        
    Returns:
        True if successful
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would assign {test_key} to folder {folder_id}")
        return True
    
    try:
        # Xray REST API endpoint for assigning test to folder
        api_url = f"{jira_base_url}/rest/raven/1.0/api/testrepository/PZ/folders/{folder_id}/tests/{test_key}"
        
        # PUT request to assign test to folder
        response = requests.put(
            api_url,
            auth=auth,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201, 204]:
            logger.info(f"✅ Assigned {test_key} to folder {folder_id}")
            return True
        elif response.status_code == 401:
            logger.error(f"❌ Authentication failed - check credentials")
            return False
        elif response.status_code == 403:
            logger.error(f"❌ Permission denied - check Xray API access")
            return False
        else:
            logger.error(f"❌ Failed to assign {test_key} to folder {folder_id}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error assigning {test_key} to folder {folder_id}: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Assign Xray tests to folder via Jira REST API'
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
    
    args = parser.parse_args()
    
    try:
        # Load Jira config
        config = load_jira_config()
        jira_base_url = config.get('jira', {}).get('base_url', 'https://prismaphotonics.atlassian.net')
        jira_email = config.get('jira', {}).get('email')
        jira_api_token = config.get('jira', {}).get('api_token')
        
        if not jira_email or not jira_api_token:
            logger.error("❌ Jira credentials not found in config file")
            logger.info("Please check config/jira_config.yaml")
            return 1
        
        # Setup authentication (email + API token for Jira Cloud)
        auth = (jira_email, jira_api_token)
        
        # Test IDs
        test_ids = [f"PZ-{14715 + i}" for i in range(30)]
        
        logger.info(f"\n{'='*80}")
        logger.info(f"{'[DRY RUN] ' if args.dry_run else ''}Assigning {len(test_ids)} Tests to Folder")
        logger.info(f"{'='*80}\n")
        
        # Get folder ID
        folder_id = args.folder_id
        if not folder_id:
            folder_path = ["Panda MS3", "BE Tests", "Focus Server Tests", "infrastructure Tests"]
            folder_id = get_xray_folder_id_via_api(jira_base_url, auth, folder_path)
        
        if not folder_id:
            logger.warning("⚠️  Could not determine folder ID automatically")
            logger.info("\n" + "="*80)
            logger.info("MANUAL ASSIGNMENT REQUIRED")
            logger.info("="*80)
            logger.info("\nPlease see: docs/06_project_management/test_planning/XRAY_TESTS_FOLDER_ASSIGNMENT.md")
            logger.info("for detailed manual assignment instructions.")
            logger.info("\n" + "="*80 + "\n")
            return 0
        
        # Assign tests to folder
        updated = 0
        failed = 0
        
        for test_id in test_ids:
            try:
                success = assign_test_to_folder_via_api(
                    test_key=test_id,
                    folder_id=folder_id,
                    jira_base_url=jira_base_url,
                    auth=auth,
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
            logger.info("Manual assignment via Xray UI may be required")
        
        return 0 if failed == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

