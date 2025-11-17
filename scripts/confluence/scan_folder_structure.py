"""
Scan Confluence Folder Structure
=================================

Scan all pages and subfolders in a Confluence folder and analyze the structure.
"""

import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
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

# Folder ID from URL: spaces/PRISMATEAM/folder/2079784961
folder_id = '2079784961'
space_key = 'PRISMATEAM'

print(f"Scanning folder: {folder_id} in space: {space_key}\n")

# Get all pages in the space
all_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)

print(f"Total pages in space: {len(all_pages)}\n")

# Analyze pages
pages_by_title = {}
pages_by_category = defaultdict(list)

for page in all_pages:
    title = page.get('title', '')
    page_id = page.get('id')
    url = page.get('_links', {}).get('webui', '')
    
    pages_by_title[title] = {
        'id': page_id,
        'title': title,
        'url': url
    }
    
    # Try to categorize by title keywords
    title_lower = title.lower()
    if any(word in title_lower for word in ['automation', 'test', 'qa', 'testing']):
        if 'strategy' in title_lower or 'plan' in title_lower:
            pages_by_category['Strategy & Planning'].append(title)
        elif 'process' in title_lower or 'workflow' in title_lower:
            pages_by_category['Processes & Workflows'].append(title)
        elif 'bit' in title_lower:
            pages_by_category['BIT Related'].append(title)
        else:
            pages_by_category['Testing & Automation'].append(title)
    elif 'work' in title_lower or 'sprint' in title_lower:
        pages_by_category['Team Management'].append(title)
    elif 'focus' in title_lower or 'server' in title_lower:
        pages_by_category['Focus Server'].append(title)
    else:
        pages_by_category['Other'].append(title)

print("="*80)
print("PAGES BY CATEGORY")
print("="*80)

for category, pages in sorted(pages_by_category.items()):
    print(f"\n{category} ({len(pages)} pages):")
    for page in sorted(pages):
        # Replace problematic characters
        try:
            safe_page = page.encode('ascii', 'ignore').decode('ascii')
            print(f"  - {safe_page}")
        except:
            print(f"  - {page[:50]}...")

print("\n" + "="*80)
print("ALL PAGES (sorted by title)")
print("="*80)

for title in sorted(pages_by_title.keys()):
    page_info = pages_by_title[title]
    # Replace problematic characters
    safe_title = title.encode('ascii', 'ignore').decode('ascii')
    print(f"  - {safe_title} (ID: {page_info['id']})")

# Save to file
output_file = project_root / 'docs' / '06_project_management' / 'CONFLUENCE_FOLDER_ANALYSIS.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# Confluence Folder Analysis\n\n")
    f.write(f"**Folder ID:** {folder_id}\n")
    f.write(f"**Space:** {space_key}\n")
    f.write(f"**Total Pages:** {len(all_pages)}\n\n")
    f.write("---\n\n")
    
    f.write("## Pages by Category\n\n")
    for category, pages in sorted(pages_by_category.items()):
        f.write(f"### {category} ({len(pages)} pages)\n\n")
        for page in sorted(pages):
            f.write(f"- {page}\n")
        f.write("\n")
    
    f.write("---\n\n")
    f.write("## All Pages (sorted by title)\n\n")
    for title in sorted(pages_by_title.keys()):
        page_info = pages_by_title[title]
        f.write(f"- **{title}**\n")
        f.write(f"  - ID: {page_info['id']}\n")
        f.write(f"  - URL: {page_info['url']}\n\n")

print(f"\n\nAnalysis saved to: {output_file}")

