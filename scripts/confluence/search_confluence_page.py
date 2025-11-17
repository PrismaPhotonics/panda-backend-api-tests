"""
Search Confluence Page by Title
================================

Search for Confluence page by title across all spaces or in specific space.

Author: QA Automation Architect
Date: 2025-11-05
"""

import sys
import os
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
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


def get_all_spaces(confluence: Confluence) -> List[Dict[str, Any]]:
    """Get all Confluence spaces."""
    try:
        spaces = confluence.get_all_spaces(start=0, limit=1000, expand='space')
        return spaces.get('results', [])
    except Exception as e:
        logger.error(f"Failed to get spaces: {e}")
        return []


def search_page_by_title(confluence: Confluence, title: str, space_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search for page by title."""
    results = []
    
    if space_key:
        # Search in specific space
        try:
            pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)
            for page in pages:
                if title.lower() in page.get('title', '').lower():
                    results.append(page)
        except Exception as e:
            logger.error(f"Failed to search in space {space_key}: {e}")
    else:
        # Search in all spaces
        spaces = get_all_spaces(confluence)
        logger.info(f"Searching in {len(spaces)} spaces...")
        
        for space in spaces:
            space_key = space.get('key')
            try:
                pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)
                for page in pages:
                    if title.lower() in page.get('title', '').lower():
                        results.append(page)
            except Exception as e:
                logger.debug(f"Failed to search in space {space_key}: {e}")
                continue
    
    return results


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Search Confluence page by title')
    parser.add_argument('title', help='Page title (or partial title)')
    parser.add_argument('--space', help='Space key (optional, searches all spaces if not provided)')
    parser.add_argument('--list-spaces', action='store_true', help='List all spaces')
    
    args = parser.parse_args()
    
    config = load_config()
    
    base_url = config.get('base_url', 'https://prismaphotonics.atlassian.net')
    email = config.get('email', 'roy.avrahami@prismaphotonics.com')
    api_token = config.get('api_token')
    
    if not api_token:
        logger.error("API token not found in config")
        return 1
    
    confluence = Confluence(
        url=f"{base_url}/wiki",
        username=email,
        password=api_token
    )
    
    if args.list_spaces:
        spaces = get_all_spaces(confluence)
        print(f"\nFound {len(spaces)} spaces:")
        for space in spaces:
            print(f"  - {space.get('key')}: {space.get('name')}")
        return 0
    
    # Search for page
    results = search_page_by_title(confluence, args.title, args.space)
    
    if not results:
        print(f"\n❌ No pages found with title containing: '{args.title}'")
        if not args.space:
            print("💡 Try specifying a space with --space KEY")
            print("💡 Or list all spaces with --list-spaces")
        return 1
    
    print(f"\n✅ Found {len(results)} page(s):")
    for page in results:
        print(f"\n  Title: {page.get('title')}")
        print(f"  Space: {page.get('space', {}).get('key')}")
        print(f"  Page ID: {page.get('id')}")
        print(f"  Version: {page.get('version', {}).get('number')}")
        print(f"  URL: {page.get('_links', {}).get('webui')}")
        print(f"  Full URL: https://prismaphotonics.atlassian.net/wiki/spaces/{page.get('space', {}).get('key')}/pages/{page.get('id')}/{page.get('title').replace(' ', '+')}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

