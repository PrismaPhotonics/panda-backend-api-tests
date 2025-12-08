"""
Search Confluence for Focus Server and Panda Articles
=====================================================

Search for all Confluence articles related to "focus server" and "Panda" system.

Author: QA Automation Architect
Date: 2025-01-XX
"""

import sys
import os
import yaml
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure UTF-8 for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
    """Get all accessible Confluence spaces."""
    try:
        spaces = confluence.get_all_spaces(start=0, limit=1000, expand='space')
        return spaces.get('results', [])
    except Exception as e:
        logger.error(f"Failed to get spaces: {e}")
        return []


def search_page_content(confluence: Confluence, page_id: str, search_terms: List[str]) -> bool:
    """Check if page content contains any of the search terms."""
    try:
        # Get page content
        page = confluence.get_page_by_id(page_id, expand='body.storage')
        if not page:
            return False
        
        # Get body content
        body = page.get('body', {}).get('storage', {}).get('value', '')
        title = page.get('title', '')
        
        # Remove HTML tags for text search
        import re
        text_content = re.sub(r'<[^>]+>', '', body).lower()
        title_lower = title.lower()
        
        # Check if any search term appears in title or content
        for term in search_terms:
            term_lower = term.lower()
            if term_lower in title_lower or term_lower in text_content:
                return True
        
        return False
    except Exception as e:
        logger.debug(f"Error checking page {page_id}: {e}")
        return False


def search_by_text_content(confluence: Confluence, search_terms: List[str]) -> List[Dict[str, Any]]:
    """Search Confluence for pages containing specific text terms by scanning all spaces."""
    all_results = []
    seen_ids = set()
    
    # Get all spaces
    logger.info("Getting all Confluence spaces...")
    spaces = get_all_spaces(confluence)
    logger.info(f"Found {len(spaces)} accessible space(s)")
    
    # Search through each space
    for space_idx, space in enumerate(spaces, 1):
        space_key = space.get('key', 'N/A')
        space_name = space.get('name', 'N/A')
        logger.info(f"[{space_idx}/{len(spaces)}] Searching space: {space_name} ({space_key})...")
        
        try:
            # Get all pages in this space
            pages = confluence.get_all_pages_from_space(
                space_key, 
                start=0, 
                limit=1000,
                expand='space,version'
            )
            
            logger.info(f"  Found {len(pages)} page(s) in {space_key}")
            
            # Check each page
            for page in pages:
                page_id = page.get('id')
                if not page_id or page_id in seen_ids:
                    continue
                
                title = page.get('title', '')
                title_lower = title.lower()
                
                # Quick check: does title contain any search term?
                title_match = False
                for term in search_terms:
                    if term.lower() in title_lower:
                        title_match = True
                        break
                
                # If title matches or we want to check content, verify
                if title_match or True:  # Always check content for thoroughness
                    if search_page_content(confluence, page_id, search_terms):
                        seen_ids.add(page_id)
                        all_results.append(page)
                        logger.info(f"    ✓ Match found: {title}")
        
        except Exception as e:
            logger.warning(f"  Error searching space {space_key}: {e}")
            continue
    
    return all_results


def format_page_info(page: Dict[str, Any], confluence: Confluence) -> str:
    """Format page information for display."""
    title = page.get('title', 'N/A')
    space = page.get('space', {})
    space_key = space.get('key', 'N/A')
    space_name = space.get('name', 'N/A')
    page_id = page.get('id', 'N/A')
    version = page.get('version', {})
    version_num = version.get('number', 'N/A')
    links = page.get('_links', {})
    webui = links.get('webui', '')
    
    # Build full URL
    base_url = "https://prismaphotonics.atlassian.net"
    if webui:
        full_url = f"{base_url}{webui}"
    else:
        # Construct URL manually
        title_slug = title.replace(' ', '+')
        full_url = f"{base_url}/wiki/spaces/{space_key}/pages/{page_id}/{title_slug}"
    
    # Get excerpt from body if available
    excerpt = ''
    try:
        page_full = confluence.get_page_by_id(page_id, expand='body.storage')
        if page_full:
            body = page_full.get('body', {}).get('storage', {}).get('value', '')
            if body:
                # Extract first 200 characters, remove HTML tags
                import re
                text = re.sub(r'<[^>]+>', '', body)
                excerpt = text[:200].strip() + '...' if len(text) > 200 else text.strip()
    except Exception:
        pass  # Skip excerpt if we can't fetch it
    
    info = f"""
{'='*80}
Title: {title}
Space: {space_name} ({space_key})
Page ID: {page_id}
Version: {version_num}
URL: {full_url}
"""
    
    if excerpt:
        info += f"Excerpt: {excerpt}\n"
    
    return info


def main():
    """Main execution."""
    logger.info("Starting Confluence search for Focus Server and Panda articles...")
    
    config = load_config()
    
    base_url = config.get('base_url', 'https://prismaphotonics.atlassian.net')
    email = config.get('email', 'roy.avrahami@prismaphotonics.com')
    api_token = config.get('api_token')
    
    if not api_token:
        logger.error("API token not found in config. Please set ATLASSIAN_API_TOKEN environment variable.")
        logger.error("Or update config/jira_config.yaml with your API token.")
        return 1
    
    # Initialize Confluence client
    try:
        confluence = Confluence(
            url=f"{base_url}/wiki",
            username=email,
            password=api_token
        )
        logger.info(f"Connected to Confluence at {base_url}")
    except Exception as e:
        logger.error(f"Failed to connect to Confluence: {e}")
        return 1
    
    # Search terms
    search_terms = [
        "focus server",
        "Focus Server",
        "FOCUS SERVER",
        "Panda",
        "PANDA",
        "panda app",
        "Panda App",
        "focus-server",
        "focus_server"
    ]
    
    logger.info(f"Searching for articles containing: {', '.join(set([t.lower() for t in search_terms]))}")
    
    # Search for pages
    results = search_by_text_content(confluence, search_terms)
    
    if not results:
        logger.warning("No pages found matching the search criteria.")
        logger.info("Try different search terms or check your Confluence access permissions.")
        return 1
    
    logger.info(f"\n✅ Found {len(results)} article(s) related to Focus Server and Panda:\n")
    
    # Display results
    for i, page in enumerate(results, 1):
        print(f"\n[{i}/{len(results)}]")
        print(format_page_info(page, confluence))
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY: Found {len(results)} article(s) related to Focus Server and Panda")
    print(f"{'='*80}\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

