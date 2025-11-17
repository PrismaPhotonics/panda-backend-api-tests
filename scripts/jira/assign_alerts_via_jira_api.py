#!/usr/bin/env python3
"""
Assign Alert Tests to Xray Folders via Jira API
Attempts to use Jira API directly to assign tests to folders
"""

import requests
import yaml
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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


def load_jira_config() -> Dict[str, Any]:
    """Load Jira configuration from config file."""
    config_path = project_root / "config" / "jira_config.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Jira config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def try_xray_api_endpoints(
    jira_base_url: str,
    auth: tuple,
    project_key: str = "PZ"
) -> Optional[Dict[str, Any]]:
    """
    Try multiple Xray API endpoints to find folders.
    
    Returns:
        Dictionary with folder structure if found, None otherwise
    """
    endpoints = [
        f"{jira_base_url}/rest/raven/1.0/api/testrepository/{project_key}/folders",
        f"{jira_base_url}/rest/raven/2.0/api/testrepository/{project_key}/folders",
        f"{jira_base_url}/rest/api/3/project/{project_key}/testrepository/folders",
        f"{jira_base_url}/rest/api/2/project/{project_key}/testrepository/folders",
    ]
    
    for endpoint in endpoints:
        try:
            logger.debug(f"Trying endpoint: {endpoint}")
            response = requests.get(
                endpoint,
                auth=auth,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Found folders via {endpoint}")
                return data
            elif response.status_code == 401:
                logger.warning(f"Authentication failed for {endpoint}")
            elif response.status_code == 403:
                logger.warning(f"Permission denied for {endpoint}")
            elif response.status_code == 404:
                logger.debug(f"Endpoint not found: {endpoint}")
            else:
                logger.debug(f"Failed: {endpoint} - {response.status_code}")
                
        except Exception as e:
            logger.debug(f"Error trying {endpoint}: {e}")
            continue
    
    return None


def assign_test_to_folder_via_xray_api(
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
    
    # Try multiple API endpoints
    endpoints = [
        f"{jira_base_url}/rest/raven/1.0/api/testrepository/{project_key}/folders/{folder_id}/tests/{test_key}",
        f"{jira_base_url}/rest/raven/2.0/api/testrepository/{project_key}/folders/{folder_id}/tests/{test_key}",
    ]
    
    for api_url in endpoints:
        try:
            logger.debug(f"Assigning {test_key} to folder {folder_id} via {api_url}...")
            
            # PUT request to assign test to folder
            response = requests.put(
                api_url,
                auth=auth,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Successfully assigned {test_key} to folder {folder_id}")
                return True
            elif response.status_code == 401:
                logger.error(f"Authentication failed for {test_key}")
                continue
            elif response.status_code == 403:
                logger.error(f"Permission denied for {test_key}")
                continue
            elif response.status_code == 404:
                logger.debug(f"Endpoint not found: {api_url}")
                continue
            else:
                logger.debug(f"Failed: {api_url} - {response.status_code}")
                continue
                
        except Exception as e:
            logger.debug(f"Error trying {api_url}: {e}")
            continue
    
    logger.warning(f"Could not assign {test_key} to folder {folder_id} via any API endpoint")
    return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Assign alert tests to Xray folders via Jira API'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Only preview changes without making them'
    )
    
    parser.add_argument(
        '--folder-ids',
        type=str,
        help='Comma-separated folder IDs: Positive,Negative,EdgeCase,Load,Performance,Investigation'
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
            return 1
        
        # For Jira Cloud, use email + API token
        auth = (jira_email, jira_api_token)
        
        logger.info("=" * 80)
        logger.info("ASSIGNING ALERT TESTS TO XRAY FOLDERS VIA JIRA API")
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
            logger.info("Attempting to find folders via API...")
            folders_data = try_xray_api_endpoints(jira_base_url, auth)
            
            if folders_data:
                logger.info("Found folders via API, but folder ID extraction not implemented")
                logger.info("Please provide folder IDs manually using --folder-ids")
                logger.info("Example: --folder-ids id1,id2,id3,id4,id5,id6")
                return 1
            else:
                logger.warning("Could not retrieve folders via API")
                logger.info("Please provide folder IDs manually using --folder-ids")
                logger.info("Example: --folder-ids id1,id2,id3,id4,id5,id6")
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
                logger.warning(f"No folder ID for category: {category}")
                continue
            
            logger.info(f"\nCategory: {category} -> Folder ID: {folder_id}")
            logger.info(f"Tests: {len(test_keys)}")
            
            category_success = 0
            category_fail = 0
            
            for test_key in test_keys:
                success = assign_test_to_folder_via_xray_api(
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
            
            logger.info(f"Success: {category_success}, Failed: {category_fail}")
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        total_tests = sum(len(tests) for tests in ALERT_TESTS_BY_CATEGORY.values())
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Assigned: {total_success}")
        logger.info(f"Failed: {total_fail}")
        
        if args.dry_run:
            logger.info("\n[DRY RUN] No changes were made")
        else:
            logger.info("\nAssignment completed!")
        
        logger.info("=" * 80)
        
        return 0 if total_fail == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

