"""Read Confluence page content."""
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

page_id = '2223570946'
page = confluence.get_page_by_id(page_id, expand='body.storage,version')

print(f"Title: {page.get('title')}")
print(f"Version: {page.get('version', {}).get('number')}")

content = page.get('body', {}).get('storage', {}).get('value', '')
print(f"\nContent length: {len(content)}")

# Save to file
output_file = project_root / 'docs' / '06_project_management' / 'team_management' / 'PROCESSES_WORKFLOWS_CURRENT.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"# {page.get('title')}\n\n")
    f.write(f"**Last Updated:** {page.get('version', {}).get('when', 'Unknown')}\n")
    f.write(f"**Version:** {page.get('version', {}).get('number', 'Unknown')}\n\n")
    f.write("---\n\n")
    f.write(content)

print(f"\nContent saved to: {output_file}")

