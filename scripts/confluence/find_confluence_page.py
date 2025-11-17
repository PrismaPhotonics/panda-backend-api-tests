"""
Find Confluence Page Information
=================================

Helper script to find Confluence page ID, space, and title from URL or search.

Author: QA Automation Architect
Date: 2025-11-05
"""

import sys
import os
import yaml
import re
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure UTF-8 for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from atlassian import Confluence
except ImportError:
    logger.error("atlassian-python-api library not installed. Install with: pip install atlassian-python-api")
    sys.exit(1)


def load_config():
    """Load configuration."""
    config_path = project_root / 'config' / 'jira_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Try Confluence config first, fallback to Jira config
    confluence_config = config.get('confluence', {})
    if not confluence_config:
        jira_config = config.get('jira', {})
        confluence_config = jira_config
    
    return confluence_config


def find_page_by_url(url: str):
    """Find page information from URL."""
    config = load_config()
    
    base_url = config.get('base_url', 'https://prismaphotonics.atlassian.net')
    email = config.get('email', 'roy.avrahami@prismaphotonics.com')
    api_token = config.get('api_token')
    
    confluence = Confluence(
        url=f"{base_url}/wiki",
        username=email,
        password=api_token
    )
    
    # Try to extract space and page info from URL
    # Format: https://prismaphotonics.atlassian.net/wiki/spaces/SPACE/pages/PAGE_ID/Title
    match = re.search(r'/spaces/([^/]+)/pages/(\d+)/', url)
    if match:
        space = match.group(1)
        page_id = match.group(2)
        print(f"Found in URL: space={space}, page_id={page_id}")
        
        try:
            page = confluence.get_page_by_id(page_id, expand='body.storage,version,space')
            print(f"\nPage Information:")
            print(f"  Title: {page.get('title')}")
            print(f"  Space: {page.get('space', {}).get('key')}")
            print(f"  Page ID: {page.get('id')}")
            print(f"  Version: {page.get('version', {}).get('number')}")
            print(f"  URL: {page.get('_links', {}).get('webui')}")
            return page
        except Exception as e:
            print(f"Error getting page: {e}")
            return None
    
    # Short URL
    if '/x/' in url:
        short_id = re.search(r'/x/([A-Za-z0-9]+)', url).group(1)
        print(f"Short URL detected: {short_id}")
        print("Please provide space and title to find the page.")
        return None
    
    return None


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Find Confluence page information')
    parser.add_argument('url', help='Confluence page URL')
    args = parser.parse_args()
    
    find_page_by_url(args.url)


if __name__ == '__main__':
    main()

