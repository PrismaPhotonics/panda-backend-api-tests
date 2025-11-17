#!/usr/bin/env python3
"""
Assign Alert Tests to Xray Folders
===================================

This script assigns all alert tests to the correct folders in Xray Test Repository
using Xray REST API.

Usage:
    python scripts/jira/assign_alerts_tests_to_xray_folders.py
    python scripts/jira/assign_alerts_tests_to_xray_folders.py --dry-run
    python scripts/jira/assign_alerts_tests_to_xray_folders.py --base-folder-id <folder_id>
"""

import argparse
import sys
import logging
import requests
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Alert tests organized by category
ALERT_TESTS_BY_CATEGORY = {
    "Positive": [
        "PZ-14933", "PZ-14934", "PZ-14935", "PZ-14936", "PZ-14937"
    ],
    "Negative": [
        "PZ-14938", "PZ-14939", "PZ-14940", "PZ-14941", "PZ-14942", 
        "PZ-14943", "PZ-14944"
    ],
    "Edge Case": [
        "PZ-14945", "PZ-14946", "PZ-14947", "PZ-14948", "PZ-14949",
        "PZ-14950", "PZ-14951", "PZ-14952"
    ],
    "Load": [
        "PZ-14953", "PZ-14954", "PZ-14955", "PZ-14956", "PZ-14957"
    ],
    "Performance": [
        "PZ-14958", "PZ-14959", "PZ-14960", "PZ-14961", "PZ-14962", "PZ-14963"
    ],
    "Investigation": [
        "PZ-14964"
    ]
}

# Base folder ID
BASE_FOLDER_ID = "68d91b9f681e183ea2e83e16"

# Category to folder name mapping
CATEGORY_FOLDER_NAMES = {
    "Positive": "Positive Tests",
    "Negative": "Negative Tests",
    "Edge Case": "Edge Cases",
    "Load": "Load Tests",
    "Performance": "Performance Tests",
    "Investigation": "Investigation"
}


def load_jira_config() -> Dict[str, Any]:
    """Load Jira configuration from config file."""
    config_path = project_root / "config" / "jira_config.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Jira config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_xray_folders(
    jira_base_url: str,
    auth: tuple,
    project_key: str = "PZ"
) -> Optional[List[Dict[str, Any]]]:
    """
    Get all Xray folders for a project.
    
    Args:
        jira_base_url: Jira base URL
        auth: Authentication tuple (username, password/token)
        project_key: Jira project key (default: "PZ")
        
    Returns:
        List of folders or None if failed
    """
    api_endpoints = [
        f"{jira_base_url}/rest/raven/1.0/api/testrepository/{project_key}/folders",
        f"{jira_base_url}/rest/raven/2.0/api/testrepository/{project_key}/folders",
    ]
    
    for api_url in api_endpoints:
        try:
            logger.debug(f"Trying endpoint: {api_url}")
            response = requests.get(
                api_url,
                auth=auth,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                folders = response.json()
                
                # Handle different response formats
                if isinstance(folders, dict) and 'data' in folders:
                    folders = folders['data']
                elif isinstance(folders, dict) and 'folders' in folders:
                    folders = folders['folders']
                
                logger.info(f"Found {len(folders)} root folders")
                return folders
                
        except Exception as e:
            logger.debug(f"Error trying {api_url}: {e}")
            continue
    
    return None


def find_folder_by_name(
    folders: List[Dict[str, Any]],
    folder_name: str,
    parent_id: Optional[str] = None
) -> Optional[str]:
    """
    Recursively find folder by name.
    
    Args:
        folders: List of folder dictionaries
        folder_name: Name of folder to find
        parent_id: Optional parent folder ID to search within
        
    Returns:
        Folder ID if found, None otherwise
    """
    def search_recursive(folder_list: List[Dict], name: str, parent: Optional[str] = None) -> Optional[str]:
        for folder in folder_list:
            current_name = folder.get('name', '') or folder.get('title', '')
            current_id = folder.get('id', '') or folder.get('folderId', '')
            
            # Check if this folder matches
            if current_name == name:
                # If parent_id specified, check if this folder is under that parent
                if parent_id is None or folder.get('parentId') == parent_id:
                    logger.info(f"Found folder '{name}' with ID: {current_id}")
                    return current_id
            
            # Search subfolders
            subfolders = folder.get('folders', []) or folder.get('children', [])
            if subfolders:
                result = search_recursive(subfolders, name, parent)
                if result:
                    return result
        
        return None
    
    return search_recursive(folders, folder_name, parent_id)


def assign_test_to_folder(
    test_key: str,
    folder_id: str,
    jira_base_url: str,
    auth: tuple,
    project_key: str = "PZ",
    dry_run: bool = False
) -> bool:
    """
    Assign test to Xray folder using Xray REST API.
    
    Args:
        test_key: Test issue key (e.g., "PZ-14933")
        folder_id: Xray folder ID
        jira_base_url: Jira base URL
        auth: Authentication tuple (username, password/token)
        project_key: Jira project key (default: "PZ")
        dry_run: If True, only preview changes
        
    Returns:
        True if successful
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would assign {test_key} to folder {folder_id}")
        return True
    
    try:
        # Xray REST API endpoint for assigning test to folder
        api_url = f"{jira_base_url}/rest/raven/1.0/api/testrepository/{project_key}/folders/{folder_id}/tests/{test_key}"
        
        logger.debug(f"Assigning {test_key} to folder {folder_id}...")
        
        # PUT request to assign test to folder
        response = requests.put(
            api_url,
            auth=auth,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code in [200, 201, 204]:
            logger.info(f"✅ Assigned {test_key} to folder {folder_id}")
            return True
        elif response.status_code == 401:
            logger.error(f"❌ Authentication failed for {test_key}")
            return False
        elif response.status_code == 403:
            logger.error(f"❌ Permission denied for {test_key}")
            return False
        elif response.status_code == 404:
            logger.warning(f"⚠️  Folder or test not found: {test_key} (folder: {folder_id})")
            return False
        else:
            logger.error(f"❌ Failed to assign {test_key} to folder {folder_id}: {response.status_code} - {response.text[:200]}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error assigning {test_key} to folder {folder_id}: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Assign alert tests to Xray folders using Xray REST API'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Only preview changes without making them'
    )
    
    parser.add_argument(
        '--base-folder-id',
        type=str,
        default=BASE_FOLDER_ID,
        help=f'Base folder ID (default: {BASE_FOLDER_ID})'
    )
    
    parser.add_argument(
        '--folder-ids',
        type=str,
        help='Comma-separated folder IDs in order: Positive,Negative,EdgeCase,Load,Performance,Investigation'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_jira_config()
        jira_config = config.get('jira', {})
        
        jira_base_url = jira_config.get('base_url', 'https://prismaphotonics.atlassian.net')
        jira_email = jira_config.get('email')
        jira_api_token = jira_config.get('api_token')
        
        if not jira_email or not jira_api_token:
            logger.error("❌ Jira credentials not found in config file")
            logger.error("Need: email and api_token in config/jira_config.yaml")
            return 1
        
        # For Jira Cloud, use email + API token
        auth = (jira_email, jira_api_token)
        
        logger.info("=" * 80)
        logger.info("ASSIGNING ALERT TESTS TO XRAY FOLDERS")
        logger.info("=" * 80)
        
        # Get folder IDs
        folder_ids = {}
        
        if args.folder_ids:
            # Use provided folder IDs
            provided_ids = args.folder_ids.split(',')
            categories = ["Positive", "Negative", "Edge Case", "Load", "Performance", "Investigation"]
            if len(provided_ids) == len(categories):
                folder_ids = dict(zip(categories, provided_ids))
                logger.info("Using provided folder IDs")
            else:
                logger.error(f"Expected {len(categories)} folder IDs, got {len(provided_ids)}")
                return 1
        else:
            # Try to find folders via API
            logger.info("Looking up folders via API...")
            folders = get_xray_folders(jira_base_url, auth)
            
            if folders:
                # Try to find each category folder
                for category, folder_name in CATEGORY_FOLDER_NAMES.items():
                    folder_id = find_folder_by_name(folders, folder_name, args.base_folder_id)
                    if folder_id:
                        folder_ids[category] = folder_id
                    else:
                        logger.warning(f"⚠️  Could not find folder: {folder_name}")
            else:
                logger.warning("⚠️  Could not retrieve folders via API")
        
        # If we don't have all folder IDs, provide instructions
        if len(folder_ids) < len(CATEGORY_FOLDER_NAMES):
            logger.error("=" * 80)
            logger.error("COULD NOT FIND ALL FOLDERS AUTOMATICALLY")
            logger.error("=" * 80)
            logger.error("\nTo find folder IDs manually:")
            logger.error("1. Open Xray Test Repository:")
            logger.error(f"   https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository&selectedFolder={args.base_folder_id}")
            logger.error("\n2. For each category folder:")
            for category, folder_name in CATEGORY_FOLDER_NAMES.items():
                logger.error(f"   - {category}: {folder_name}")
            logger.error("\n3. Open browser DevTools (F12) > Network tab")
            logger.error("4. Click on each folder")
            logger.error("5. Find folder ID in API response or URL")
            logger.error("\nThen run:")
            logger.error("   python scripts/jira/assign_alerts_tests_to_xray_folders.py --folder-ids <positive_id>,<negative_id>,<edge_case_id>,<load_id>,<performance_id>,<investigation_id>")
            logger.error("=" * 80)
            return 1
        
        # Assign tests to folders
        logger.info("\n" + "=" * 80)
        logger.info("ASSIGNING TESTS")
        logger.info("=" * 80)
        
        if args.dry_run:
            logger.info("[DRY RUN MODE] - No changes will be made\n")
        
        total_success = 0
        total_fail = 0
        
        for category, test_keys in ALERT_TESTS_BY_CATEGORY.items():
            folder_id = folder_ids.get(category)
            if not folder_id:
                logger.warning(f"⚠️  No folder ID for category: {category}")
                continue
            
            folder_name = CATEGORY_FOLDER_NAMES[category]
            logger.info(f"\n📁 Category: {category} -> {folder_name} (ID: {folder_id})")
            logger.info(f"   Tests: {len(test_keys)}")
            
            category_success = 0
            category_fail = 0
            
            for test_key in test_keys:
                success = assign_test_to_folder(
                    test_key,
                    folder_id,
                    jira_base_url,
                    auth,
                    dry_run=args.dry_run
                )
                
                if success:
                    category_success += 1
                    total_success += 1
                else:
                    category_fail += 1
                    total_fail += 1
                
                # Small delay to avoid rate limiting
                if not args.dry_run:
                    time.sleep(0.3)
            
            logger.info(f"   ✅ Success: {category_success}, ❌ Failed: {category_fail}")
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        total_tests = sum(len(tests) for tests in ALERT_TESTS_BY_CATEGORY.values())
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"✅ Assigned: {total_success}")
        logger.info(f"❌ Failed: {total_fail}")
        
        if args.dry_run:
            logger.info("\n[DRY RUN] No changes were made")
        else:
            logger.info("\n✅ Assignment completed!")
        
        logger.info("=" * 80)
        
        return 0 if total_fail == 0 else 1
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

