#!/usr/bin/env python3
"""
Assign API Endpoint Tests to Xray Folder
=========================================

This script assigns all API endpoint tests (PZ-14750 to PZ-14764) 
to the correct folder in Xray Test Repository using Xray REST API.

Usage:
    python scripts/jira/assign_api_tests_to_xray_folder.py
    python scripts/jira/assign_api_tests_to_xray_folder.py --dry-run
    python scripts/jira/assign_api_tests_to_xray_folder.py --folder-id <folder_id>
"""

import argparse
import sys
import logging
import requests
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient
import yaml

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

# Target folder path
TARGET_FOLDER_PATH = ["Panda MS3", "BE Tests", "Focus Server Tests", "API Tests"]


def load_jira_config() -> Dict[str, Any]:
    """Load Jira configuration from config file."""
    config_path = project_root / "config" / "jira_config.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Jira config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_xray_folder_id(
    jira_base_url: str,
    auth: tuple,
    folder_path: List[str],
    project_key: str = "PZ"
) -> Optional[str]:
    """
    Get Xray folder ID by folder path.
    
    Tries multiple Xray API endpoints:
    1. /rest/raven/1.0/api/testrepository/{project}/folders (Server/DC)
    2. /rest/raven/2.0/api/testrepository/{project}/folders (Server/DC v2)
    3. /rest/api/2/project/{project}/testrepository/folders (Alternative)
    
    Args:
        jira_base_url: Jira base URL
        auth: Authentication tuple (username, password/token)
        folder_path: List of folder names (e.g., ["Panda MS3", "BE Tests", "API Tests"])
        project_key: Jira project key (default: "PZ")
        
    Returns:
        Folder ID if found, None otherwise
    """
    # Try multiple API endpoints
    api_endpoints = [
        f"{jira_base_url}/rest/raven/1.0/api/testrepository/{project_key}/folders",
        f"{jira_base_url}/rest/raven/2.0/api/testrepository/{project_key}/folders",
        f"{jira_base_url}/rest/api/2/project/{project_key}/testrepository/folders",
    ]
    
    for api_url in api_endpoints:
        try:
            logger.info(f"Trying endpoint: {api_url}")
            response = requests.get(
                api_url,
                auth=auth,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                folders = response.json()
                logger.info(f"Found {len(folders)} root folders")
                
                # Handle different response formats
                if isinstance(folders, dict) and 'data' in folders:
                    folders = folders['data']
                elif isinstance(folders, dict) and 'folders' in folders:
                    folders = folders['folders']
                
                # Recursively search for folder
                def find_folder(folders_list: List[Dict], path: List[str], current_path: List[str] = None) -> Optional[str]:
                    if current_path is None:
                        current_path = []
                    
                    if not path:
                        return None
                    
                    target_name = path[0]
                    remaining_path = path[1:]
                    
                    for folder in folders_list:
                        folder_name = folder.get('name', '') or folder.get('title', '')
                        folder_id = folder.get('id', '') or folder.get('folderId', '')
                        
                        if folder_name == target_name:
                            new_path = current_path + [folder_name]
                            
                            if not remaining_path:
                                # Found the target folder
                                logger.info(f"Found folder: {' -> '.join(new_path)} (ID: {folder_id})")
                                return folder_id
                            
                            # Check subfolders
                            subfolders = folder.get('folders', []) or folder.get('children', [])
                            if subfolders:
                                result = find_folder(subfolders, remaining_path, new_path)
                                if result:
                                    return result
                    
                    return None
                
                folder_id = find_folder(folders, folder_path)
                if folder_id:
                    return folder_id
                    
            elif response.status_code == 401:
                logger.warning(f"Authentication failed for {api_url}")
                continue
            elif response.status_code == 403:
                logger.warning(f"Permission denied for {api_url}")
                continue
            elif response.status_code == 404:
                logger.debug(f"Endpoint not found: {api_url}")
                continue
            else:
                logger.debug(f"Failed to get folders from {api_url}: {response.status_code}")
                continue
                
        except Exception as e:
            logger.debug(f"Error trying {api_url}: {e}")
            continue
    
    logger.warning("Could not find folder via any API endpoint")
    return None


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
        test_key: Test issue key (e.g., "PZ-14750")
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
        # Format: PUT /rest/raven/1.0/api/testrepository/{project}/folders/{folderId}/tests/{testKey}
        api_url = f"{jira_base_url}/rest/raven/1.0/api/testrepository/{project_key}/folders/{folder_id}/tests/{test_key}"
        
        logger.info(f"Assigning {test_key} to folder {folder_id}...")
        
        # PUT request to assign test to folder
        response = requests.put(
            api_url,
            auth=auth,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code in [200, 201, 204]:
            logger.info(f"[OK] Assigned {test_key} to folder {folder_id}")
            return True
        elif response.status_code == 401:
            logger.error(f"[FAIL] Authentication failed for {test_key}")
            return False
        elif response.status_code == 403:
            logger.error(f"[FAIL] Permission denied for {test_key}")
            return False
        elif response.status_code == 404:
            logger.warning(f"[WARN] Folder or test not found: {test_key} (folder: {folder_id})")
            return False
        else:
            logger.error(f"[FAIL] Failed to assign {test_key} to folder {folder_id}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"[FAIL] Error assigning {test_key} to folder {folder_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_jql_query(test_keys: List[str]) -> str:
    """
    Generate JQL query for finding tests in the correct format.
    
    Args:
        test_keys: List of test issue keys
        
    Returns:
        JQL query string in format: project = PZ AND key IN (...) ORDER BY key ASC
    """
    # Format: project = PZ AND key IN (PZ-14750, PZ-14751, ...) ORDER BY key ASC
    keys_str = ", ".join(test_keys)
    jql = f"project = PZ AND key IN ({keys_str}) ORDER BY key ASC"
    return jql


def generate_jql_query_formatted(test_keys: List[str]) -> str:
    """
    Generate formatted JQL query for display (multi-line).
    
    Args:
        test_keys: List of test issue keys
        
    Returns:
        Formatted JQL query string
    """
    # Format with line breaks for readability
    lines = []
    lines.append("project = PZ AND key IN (")
    
    # Group keys in lines of 5
    for i in range(0, len(test_keys), 5):
        group = test_keys[i:i+5]
        # Add comma after each key except the very last one in the entire list
        formatted_group = []
        for j, key in enumerate(group):
            global_index = i + j
            if global_index < len(test_keys) - 1:
                formatted_group.append(key + ",")
            else:
                formatted_group.append(key)
        lines.append("  " + " ".join(formatted_group))
    
    lines.append(") ORDER BY key ASC")
    return "\n".join(lines)


def verify_tests_exist(client: JiraClient, test_keys: List[str]) -> Dict[str, Any]:
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
            logger.info(f"[OK] Found: {test_key} - {issue.fields.summary}")
        except Exception as e:
            missing.append(test_key)
            logger.warning(f"[WARN] Not found: {test_key} - {e}")
    
    return {
        'existing': existing,
        'missing': missing
    }


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Assign API endpoint tests to Xray folder using Xray REST API'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Only preview changes without making them'
    )
    
    parser.add_argument(
        '--folder-id',
        type=str,
        help='Xray folder ID (if known, skips folder lookup)'
    )
    
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify tests exist, do not assign'
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
            logger.error("Jira credentials not found in config file")
            logger.error("Need: email and api_token in config/jira_config.yaml")
            return 1
        
        # For Jira Cloud, use email + API token
        auth = (jira_email, jira_api_token)
        
        # Initialize Jira client for verification
        client = JiraClient()
        
        # Verify tests exist
        logger.info("=" * 80)
        logger.info("VERIFICATION")
        logger.info("=" * 80)
        result = verify_tests_exist(client, API_ENDPOINT_TESTS)
        
        print("\n" + "=" * 80)
        print("VERIFICATION RESULTS")
        print("=" * 80)
        print(f"[OK] Found: {len(result['existing'])} tests")
        print(f"[FAIL] Missing: {len(result['missing'])} tests")
        
        if result['missing']:
            print(f"\n[WARNING] Missing tests: {', '.join(result['missing'])}")
            print("Cannot proceed with missing tests.")
            return 1
        
        if args.verify_only:
            # Print JQL query
            print("\n" + "=" * 80)
            print("JQL QUERY FOR MANUAL ASSIGNMENT")
            print("=" * 80)
            print("\nCopy this JQL query to search for tests in Xray:")
            print("-" * 80)
            print(generate_jql_query_formatted(API_ENDPOINT_TESTS))
            print("-" * 80)
            logger.info("Verification only - exiting")
            return 0
        
        # Get folder ID
        if args.folder_id:
            folder_id = args.folder_id
            logger.info(f"Using provided folder ID: {folder_id}")
        else:
            logger.info("=" * 80)
            logger.info("FOLDER LOOKUP")
            logger.info("=" * 80)
            logger.info(f"Looking for folder: {' -> '.join(TARGET_FOLDER_PATH)}")
            
            folder_id = get_xray_folder_id(
                jira_base_url,
                auth,
                TARGET_FOLDER_PATH
            )
            
            if not folder_id:
                logger.error("=" * 80)
                logger.error("COULD NOT FIND FOLDER AUTOMATICALLY")
                logger.error("=" * 80)
                logger.error("\nTo find folder ID manually:")
                logger.error("1. Open Xray Test Repository:")
                logger.error("   https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository")
                logger.error("\n2. Navigate to folder:")
                logger.error(f"   {' -> '.join(TARGET_FOLDER_PATH)}")
                logger.error("\n3. Open browser DevTools (F12)")
                logger.error("4. Go to Network tab")
                logger.error("5. Click on the folder")
                logger.error("6. Look for API calls containing 'folder' or 'testrepository'")
                logger.error("7. Find the folder ID in the response or URL")
                logger.error("\nThen run:")
                logger.error(f"   python scripts/jira/assign_api_tests_to_xray_folder.py --folder-id <FOLDER_ID>")
                logger.error("=" * 80)
                return 1
        
        # Assign tests to folder
        logger.info("=" * 80)
        logger.info("ASSIGNMENT")
        logger.info("=" * 80)
        
        if args.dry_run:
            logger.info("[DRY RUN MODE] - No changes will be made")
        
        success_count = 0
        fail_count = 0
        
        for test_key in API_ENDPOINT_TESTS:
            success = assign_test_to_folder(
                test_key,
                folder_id,
                jira_base_url,
                auth,
                dry_run=args.dry_run
            )
            
            if success:
                success_count += 1
            else:
                fail_count += 1
        
        # Summary
        print("\n" + "=" * 80)
        print("ASSIGNMENT SUMMARY")
        print("=" * 80)
        print(f"Total tests: {len(API_ENDPOINT_TESTS)}")
        print(f"[OK] Assigned: {success_count}")
        print(f"[FAIL] Failed: {fail_count}")
        
        if args.dry_run:
            print("\n[DRY RUN] No changes were made")
        else:
            print(f"\nFolder ID used: {folder_id}")
            print(f"Folder path: {' -> '.join(TARGET_FOLDER_PATH)}")
        
        # Print JQL query for reference
        print("\n" + "=" * 80)
        print("JQL QUERY FOR REFERENCE")
        print("=" * 80)
        print("\nTo find these tests in Jira, use this JQL query:")
        print("-" * 80)
        print(generate_jql_query_formatted(API_ENDPOINT_TESTS))
        print("-" * 80)
        
        client.close()
        
        return 0 if fail_count == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

