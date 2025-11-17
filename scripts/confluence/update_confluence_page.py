"""
Update Confluence Page from Markdown Document
==============================================

Updates a Confluence page with content from a Markdown document.
Converts Markdown to Confluence Storage Format (XHTML) or Wiki Markup.

Author: QA Automation Architect
Date: 2025-11-05
"""

import sys
import os
import re
import yaml
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from atlassian import Confluence
except ImportError:
    logger.error("atlassian-python-api library not installed. Install with: pip install atlassian-python-api")
    sys.exit(1)


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load Confluence configuration from YAML file."""
    if config_path is None:
        config_path = project_root / 'config' / 'jira_config.yaml'
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def markdown_to_confluence_storage(markdown_content: str) -> str:
    """
    Convert Markdown to Confluence Storage Format (XHTML).
    This is a simplified conversion - Confluence Storage Format is XHTML-based.
    """
    # Basic Markdown to XHTML conversion
    content = markdown_content
    
    # Headers
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
    
    # Bold
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    
    # Italic
    content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
    
    # Code blocks
    content = re.sub(r'```(\w+)?\n(.*?)```', r'<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">\1</ac:parameter><ac:plain-text-body><![CDATA[\2]]></ac:plain-text-body></ac:structured-macro>', content, flags=re.DOTALL)
    
    # Inline code
    content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
    
    # Links
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
    
    # Lists
    content = re.sub(r'^- (.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    content = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', content, flags=re.DOTALL)
    
    # Paragraphs
    content = re.sub(r'^(?!<[hul])(.+)$', r'<p>\1</p>', content, flags=re.MULTILINE)
    
    # Wrap in ac:structured-macro for Confluence Storage Format
    storage_content = f'<ac:structured-macro ac:name="note"><ac:rich-text-body>{content}</ac:rich-text-body></ac:structured-macro>'
    
    return storage_content


def markdown_to_confluence_wiki(markdown_content: str) -> str:
    """
    Convert Markdown to Confluence Wiki Markup.
    This is a simplified conversion.
    """
    content = markdown_content
    
    # Headers
    content = re.sub(r'^# (.+)$', r'h1. \1', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'h2. \1', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'h3. \1', content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.+)$', r'h4. \1', content, flags=re.MULTILINE)
    
    # Bold
    content = re.sub(r'\*\*(.+?)\*\*', r'*\1*', content)
    
    # Italic
    content = re.sub(r'\*(.+?)\*', r'_\1_', content)
    
    # Code blocks
    content = re.sub(r'```(\w+)?\n(.*?)```', r'{code:\1}\n\2\n{code}', content, flags=re.DOTALL)
    
    # Inline code
    content = re.sub(r'`([^`]+)`', r'{{1}}', content)
    
    # Links
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'[\1|\2]', content)
    
    # Lists
    content = re.sub(r'^- (.+)$', r'* \1', content, flags=re.MULTILINE)
    
    # Tables (basic)
    # Convert markdown tables to Confluence tables
    lines = content.split('\n')
    in_table = False
    result_lines = []
    
    for line in lines:
        if '|' in line and not line.strip().startswith('|'):
            # Start of table
            if not in_table:
                in_table = True
            # Convert table row
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells and not all(c in ['-', ':'] for c in ''.join(cells)):
                result_lines.append('| ' + ' | '.join(cells) + ' |')
        elif in_table and '|' not in line:
            in_table = False
            result_lines.append(line)
        else:
            result_lines.append(line)
    
    content = '\n'.join(result_lines)
    
    return content


def resolve_short_url(confluence: Confluence, short_id: str) -> Optional[Dict[str, Any]]:
    """Resolve Confluence short URL to page."""
    try:
        # Try to get page by short ID using Confluence API
        # Short URLs are typically resolved by accessing the page directly
        # We'll need to search or use a different approach
        # For now, return None and require space/title
        return None
    except Exception as e:
        logger.error(f"Failed to resolve short URL: {e}")
        return None


def get_page_id_from_url(confluence: Confluence, url: str) -> Optional[str]:
    """Extract page ID from Confluence URL."""
    # Try to extract page ID from full URL
    match = re.search(r'/pages/(\d+)/', url)
    if match:
        return match.group(1)
    
    # If it's a short URL (x/AwBegw), we need space and title to find it
    if '/x/' in url:
        match = re.search(r'/x/([A-Za-z0-9]+)', url)
        if match:
            short_id = match.group(1)
            logger.info(f"Found short URL ID: {short_id}")
            logger.info("Short URLs require space and title to resolve. Please provide --space and --title")
            return None
    
    return None


def find_page_by_title(confluence: Confluence, space: str, title: str) -> Optional[Dict[str, Any]]:
    """Find page by space and title."""
    try:
        pages = confluence.get_all_pages_from_space(space, start=0, limit=1000)
        for page in pages:
            if page.get('title') == title:
                return page
        return None
    except Exception as e:
        logger.error(f"Failed to search pages: {e}")
        return None


def update_confluence_page(
    page_url: str,
    markdown_file: Path,
    space: Optional[str] = None,
    title: Optional[str] = None,
    use_storage_format: bool = True
) -> bool:
    """
    Update Confluence page with content from Markdown file.
    
    Args:
        page_url: Confluence page URL (short or full URL)
        markdown_file: Path to Markdown file
        space: Confluence space key (optional, for page lookup)
        title: Page title (optional, for page lookup)
        use_storage_format: If True, use Storage Format (XHTML), else Wiki Markup
    
    Returns:
        True if successful
    """
    # Load configuration
    config = load_config()
    
    # Try Confluence config first, fallback to Jira config
    confluence_config = config.get('confluence', {})
    if not confluence_config:
        # Fallback to Jira config (same credentials often work)
        jira_config = config.get('jira', {})
        confluence_config = jira_config
    
    base_url = confluence_config.get('base_url', 'https://prismaphotonics.atlassian.net')
    email = confluence_config.get('email', 'roy.avrahami@prismaphotonics.com')
    api_token = confluence_config.get('api_token')
    
    if not api_token:
        logger.error("API token not found in config (confluence.api_token or jira.api_token)")
        return False
    
    # Initialize Confluence client
    confluence_url = f"{base_url}/wiki"
    try:
        confluence = Confluence(
            url=confluence_url,
            username=email,
            password=api_token
        )
    except Exception as e:
        logger.error(f"Failed to initialize Confluence client: {e}")
        return False
    
    # Read Markdown file
    if not markdown_file.exists():
        logger.error(f"Markdown file not found: {markdown_file}")
        return False
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Try to get page ID from URL
    page_id = get_page_id_from_url(confluence, page_url)
    
    # If page ID not found, try to find by space and title
    if not page_id:
        if space and title:
            logger.info(f"Searching for page: space={space}, title={title}")
            page = find_page_by_title(confluence, space, title)
            if page:
                page_id = page.get('id')
                logger.info(f"Found page ID: {page_id}")
            else:
                logger.error(f"Page not found with space='{space}', title='{title}'")
                return False
        else:
            logger.error("Could not determine page ID. Please provide --space and --title, or use full page URL with page ID.")
            logger.error("Example: --url 'https://prismaphotonics.atlassian.net/wiki/spaces/SPACE/pages/123456/Title' --space SPACE --title 'Page Title'")
            return False
    
    if not page_id:
        logger.error("Could not determine page ID. Please provide space and title, or use full page URL.")
        return False
    
    # Get current page content
    try:
        current_page = confluence.get_page_by_id(page_id, expand='body.storage,version')
        current_version = current_page.get('version', {}).get('number', 1)
        logger.info(f"Current page version: {current_version}")
    except Exception as e:
        logger.error(f"Failed to get current page: {e}")
        return False
    
    # Convert Markdown to Confluence format
    if use_storage_format:
        # Use Storage Format (XHTML) - recommended for Confluence Cloud
        content = markdown_to_confluence_storage(markdown_content)
        content_format = 'storage'
    else:
        # Use Wiki Markup
        content = markdown_to_confluence_wiki(markdown_content)
        content_format = 'wiki'
    
    # Update page
    try:
        # Prepare update data
        update_data = {
            'id': page_id,
            'title': current_page.get('title'),
            'type': 'page',
            'body': {
                content_format: {
                    'value': content
                }
            },
            'version': {
                'number': current_version + 1
            }
        }
        
        # Update page using REST API
        updated_page = confluence.update_page(
            page_id=page_id,
            title=current_page.get('title'),
            body=content,
            representation=content_format
        )
        logger.info(f"Successfully updated page: {updated_page.get('_links', {}).get('webui')}")
        return True
    except Exception as e:
        logger.error(f"Failed to update page: {e}")
        logger.error(f"Error details: {type(e).__name__}: {str(e)}")
        return False


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Update Confluence page from Markdown document'
    )
    parser.add_argument(
        '--url',
        required=True,
        help='Confluence page URL (short or full URL, e.g., https://prismaphotonics.atlassian.net/wiki/x/AwBegw)'
    )
    parser.add_argument(
        '--file',
        required=True,
        type=Path,
        help='Path to Markdown file to upload'
    )
    parser.add_argument(
        '--space',
        help='Confluence space key (optional, for page lookup)'
    )
    parser.add_argument(
        '--title',
        help='Page title (optional, for page lookup)'
    )
    parser.add_argument(
        '--wiki-markup',
        action='store_true',
        help='Use Wiki Markup format instead of Storage Format'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run - show what would be updated without actually updating'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
        logger.info(f"Would update page: {args.url}")
        logger.info(f"With content from: {args.file}")
        return 0
    
    success = update_confluence_page(
        page_url=args.url,
        markdown_file=args.file,
        space=args.space,
        title=args.title,
        use_storage_format=not args.wiki_markup
    )
    
    if success:
        logger.info("✅ Page updated successfully!")
        return 0
    else:
        logger.error("❌ Failed to update page")
        return 1


if __name__ == '__main__':
    sys.exit(main())

