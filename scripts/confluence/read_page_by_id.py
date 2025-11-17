"""Read Confluence page by page ID."""
import sys
import yaml
from pathlib import Path
from atlassian import Confluence

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

config_path = project_root / 'config' / 'jira_config.yaml'
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

confluence_config = config.get('confluence', {})
if not confluence_config:
    jira_config = config.get('jira', {})
    confluence_config = jira_config

base_url = confluence_config.get('base_url', 'https://prismaphotonics.atlassian.net')
email = confluence_config.get('email', 'roy.avrahami@prismaphotonics.com')
api_token = confluence_config.get('api_token')

confluence = Confluence(
    url=f"{base_url}/wiki",
    username=email,
    password=api_token
)

# Read page by ID
page_id = sys.argv[1] if len(sys.argv) > 1 else '2009694254'
space = sys.argv[2] if len(sys.argv) > 2 else 'PRISMA'

print(f"Reading page ID: {page_id} from space: {space}")

try:
    # Try to get page by ID
    page = confluence.get_page_by_id(page_id, expand='body.storage,version,space')
    
    print(f"\n{'='*80}")
    print(f"Title: {page.get('title')}")
    print(f"Space: {page.get('space', {}).get('key', 'Unknown')}")
    print(f"Version: {page.get('version', {}).get('number', 'Unknown')}")
    print(f"Last Updated: {page.get('version', {}).get('when', 'Unknown')}")
    print(f"Page ID: {page_id}")
    print(f"URL: {page.get('_links', {}).get('webui', 'N/A')}")
    print(f"{'='*80}\n")
    
    content = page.get('body', {}).get('storage', {}).get('value', '')
    print(f"Content length: {len(content)} characters\n")
    
    # Print first 2000 characters of content
    print("Content preview (first 2000 chars):")
    print("-" * 80)
    print(content[:2000])
    if len(content) > 2000:
        print(f"\n... ({len(content) - 2000} more characters)")
    print("-" * 80)
    
    # Save to file
    output_dir = project_root / 'docs' / '03_architecture' / 'api'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean title for filename
    title = page.get('title', 'Unknown')
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title.replace(' ', '_')
    
    output_file = output_dir / f'YOSHI_REST_API_DOCUMENTATION.md'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {page.get('title')}\n\n")
        f.write(f"**Source:** [Confluence Page]({page.get('_links', {}).get('webui', '')})\n")
        f.write(f"**Page ID:** {page_id}\n")
        f.write(f"**Space:** {page.get('space', {}).get('key', 'Unknown')}\n")
        f.write(f"**Last Updated:** {page.get('version', {}).get('when', 'Unknown')}\n")
        f.write(f"**Version:** {page.get('version', {}).get('number', 'Unknown')}\n\n")
        f.write("---\n\n")
        f.write(content)
    
    print(f"\n✅ Content saved to: {output_file}")
    
except Exception as e:
    print(f"❌ Error reading page: {e}")
    import traceback
    traceback.print_exc()
    
    # Try to search for the page
    print(f"\nTrying to search for page in space '{space}'...")
    try:
        pages = confluence.get_all_pages_from_space(space, start=0, limit=100)
        print(f"Found {len(pages)} pages in space '{space}'")
        
        # Search for pages with "Yoshi" or "REST API" in title
        for page in pages:
            title = page.get('title', '')
            if 'yoshi' in title.lower() or 'rest' in title.lower() or 'api' in title.lower():
                print(f"  - {title} (ID: {page.get('id')})")
    except Exception as e2:
        print(f"Error searching space: {e2}")

