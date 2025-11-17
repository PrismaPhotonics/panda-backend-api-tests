"""Read Confluence page by short URL."""
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

# Search for pages with short URL
short_url_id = sys.argv[1] if len(sys.argv) > 1 else 'LoDJdw'
pages = confluence.get_all_pages_from_space('PRISMATEAM', start=0, limit=1000)

# Try to find page by searching in webui links
found_page = None
for page in pages:
    webui = page.get('_links', {}).get('webui', '')
    if short_url_id in webui or short_url_id in str(page.get('id', '')):
        found_page = page
        break

if found_page:
    page_id = found_page.get('id')
    page = confluence.get_page_by_id(page_id, expand='body.storage,version')
    
    print(f"Title: {page.get('title')}")
    print(f"Version: {page.get('version', {}).get('number')}")
    print(f"Page ID: {page_id}")
    print(f"URL: {page.get('_links', {}).get('webui')}")
    
    content = page.get('body', {}).get('storage', {}).get('value', '')
    print(f"\nContent length: {len(content)}")
    
    # Save to file
    output_file = project_root / 'docs' / '06_project_management' / 'team_management' / 'PAGE_AoBygw_CURRENT.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {page.get('title')}\n\n")
        f.write(f"**Last Updated:** {page.get('version', {}).get('when', 'Unknown')}\n")
        f.write(f"**Version:** {page.get('version', {}).get('number', 'Unknown')}\n\n")
        f.write("---\n\n")
        f.write(content)
    
    print(f"\nContent saved to: {output_file}")
else:
    print(f"Page with short URL ID '{short_url_id}' not found in PRISMATEAM space")
    print("Trying to find by title...")
    
    # Try to find by title patterns
    search_terms = ['Backend Test Automation', 'Automation Strategy', 'QA Automation']
    for term in search_terms:
        results = confluence.cql(f"space = PRISMATEAM AND title ~ '{term}'", limit=10)
        if results.get('results'):
            print(f"\nFound {len(results.get('results', []))} pages with '{term}':")
            for result in results.get('results', [])[:3]:
                print(f"  - {result.get('title')} (ID: {result.get('id')})")

