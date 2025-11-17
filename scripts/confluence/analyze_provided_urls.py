"""
Analyze Provided URLs and Map to Folder Structure
==================================================
"""

import sys
import yaml
import re
from pathlib import Path
from typing import List, Dict, Any
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

# URLs provided
urls = [
    'https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2180448265/Live+vs+Historic+Mode+-+Complete+Analysis',
    'https://prismaphotonics.atlassian.net/wiki/x/AwB7h',
    'https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2223079425/Kubernetes+Tests+Roadmap',
    'https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/folder/2234482692',
    'https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/folder/2235727873',
    'https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2112094219/FOCUS+SERVER+Full+Test+Plan+Drop+3',
    'https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2079817729/Drop+3+Backend+Test+Plans+Recorder+Focus+Server+Storage+Manager',
    'https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2112552979/SMART+RECORDER+Full+Test+Plan+Drop+3',
    'https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2111930403/STORAGE+MANAGER+Full+Test+Plan+Drop+3+Interim+until+service+exists',
    'https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2180808717/Live+vs+Historic+Mode+Testing+-+Implementation+Summary',
    'https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2222653443/Jira+Ticket+Template',
]

print("="*80)
print("ANALYZING PROVIDED URLs")
print("="*80)

# Extract page IDs from URLs
page_ids = []
folder_ids = []

for url in urls:
    # Extract page ID
    page_match = re.search(r'/pages/(\d+)', url)
    folder_match = re.search(r'/folder/(\d+)', url)
    short_url_match = re.search(r'/x/([A-Za-z0-9]+)', url)
    
    if page_match:
        page_ids.append(page_match.group(1))
    elif folder_match:
        folder_ids.append(folder_match.group(1))
    elif short_url_match:
        short_id = short_url_match.group(1)
        # Try to resolve short URL
        try:
            # Get all pages and find by short URL
            all_pages = confluence.get_all_pages_from_space('PRISMATEAM', start=0, limit=1000)
            for page in all_pages:
                page_id = page.get('id')
                # Check if short URL matches
                # This is a simplified check - actual short URL resolution is more complex
                pass
        except:
            pass

print(f"\nFound {len(page_ids)} page IDs and {len(folder_ids)} folder IDs")

# Analyze each page
pages_info = []
for page_id in page_ids:
    try:
        page = confluence.get_page_by_id(page_id, expand='ancestors,space,version')
        page_title = page.get('title', 'Unknown')
        ancestors = page.get('ancestors', [])
        
        parent_info = None
        if ancestors:
            parent = ancestors[-1]
            parent_info = {
                'id': parent.get('id'),
                'title': parent.get('title', 'Unknown')
            }
        
        pages_info.append({
            'id': page_id,
            'title': page_title,
            'url': f"{base_url}/wiki/spaces/PRISMATEAM/pages/{page_id}",
            'parent': parent_info,
            'ancestors_count': len(ancestors)
        })
        
        print(f"\nPage: {page_title}")
        print(f"  ID: {page_id}")
        if parent_info:
            print(f"  Parent: {parent_info['title']} (ID: {parent_info['id']})")
        else:
            print(f"  Parent: ROOT (no parent)")
            
    except Exception as e:
        print(f"\nError getting page {page_id}: {e}")

# Analyze folders
folders_info = []
for folder_id in folder_ids:
    try:
        folder = confluence.get_page_by_id(folder_id, expand='ancestors,space,children.page')
        folder_title = folder.get('title', 'Unknown')
        ancestors = folder.get('ancestors', [])
        
        # Get children
        children = confluence.get_page_child_by_type(folder_id, type='page', start=0, limit=1000)
        
        parent_info = None
        if ancestors:
            parent = ancestors[-1]
            parent_info = {
                'id': parent.get('id'),
                'title': parent.get('title', 'Unknown')
            }
        
        folders_info.append({
            'id': folder_id,
            'title': folder_title,
            'url': f"{base_url}/wiki/spaces/PRISMATEAM/folder/{folder_id}",
            'parent': parent_info,
            'children_count': len(children),
            'children': [{'id': c.get('id'), 'title': c.get('title', 'Unknown')} for c in children[:10]]
        })
        
        print(f"\nFolder: {folder_title}")
        print(f"  ID: {folder_id}")
        if parent_info:
            print(f"  Parent: {parent_info['title']} (ID: {parent_info['id']})")
        else:
            print(f"  Parent: ROOT (no parent)")
        print(f"  Children: {len(children)} pages")
        if children:
            print(f"  First {min(5, len(children))} children:")
            for child in children[:5]:
                print(f"    - {child.get('title', 'Unknown')}")
                
    except Exception as e:
        print(f"\nError getting folder {folder_id}: {e}")

# Map to folder structure
print("\n" + "="*80)
print("MAPPING TO FOLDER STRUCTURE")
print("="*80)

# Expected folder IDs
expected_folders = {
    '01_Program_Overview': '2236874758',
    '02_Team_Management': '2236645383',
    '03_Testing_Strategy': '2236874759',
    '04_Automation_Framework': '2236907539',
    '05_BIT_Testing': '2238382086',
    '06_Focus_Server': '2236940298',
    '07_Test_Plans': '2238283785',
    '08_UI_Frontend_Testing': '2237759512',
    '09_Test_Plans_Archive': '2237497351',
    '10_Infrastructure': '2238316553',
}

main_folder_id = '2079784961'

# Categorize pages
mapping = {
    '07_Test_Plans': [],
    '06_Focus_Server': [],
    '09_Test_Plans_Archive': [],
    '03_Testing_Strategy': [],
    'UNMAPPED': []
}

for page in pages_info:
    title_lower = page['title'].lower()
    
    if 'drop 3' in title_lower or 'test plan' in title_lower:
        if 'focus server' in title_lower:
            mapping['06_Focus_Server'].append(page)
        elif 'recorder' in title_lower or 'storage manager' in title_lower:
            mapping['07_Test_Plans'].append(page)
        else:
            mapping['09_Test_Plans_Archive'].append(page)
    elif 'focus server' in title_lower:
        mapping['06_Focus_Server'].append(page)
    elif 'kubernetes' in title_lower:
        mapping['07_Test_Plans'].append(page)
    elif 'live vs historic' in title_lower or 'historic mode' in title_lower:
        mapping['03_Testing_Strategy'].append(page)
    elif 'jira ticket template' in title_lower:
        mapping['03_Testing_Strategy'].append(page)
    else:
        mapping['UNMAPPED'].append(page)

# Print mapping
print("\nRecommended folder mapping:\n")
for folder, pages in sorted(mapping.items()):
    if pages:
        print(f"{folder}: {len(pages)} pages")
        for page in pages:
            print(f"  - {page['title']} (ID: {page['id']})")
            if page['parent']:
                print(f"    Current parent: {page['parent']['title']}")
        print()

# Save report
output_file = project_root / 'docs' / '06_project_management' / 'PROVIDED_URLS_ANALYSIS.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# Provided URLs Analysis\n\n")
    f.write(f"**Date:** 2025-11-05\n\n")
    f.write("---\n\n")
    
    f.write("## Pages Found\n\n")
    for page in pages_info:
        f.write(f"### {page['title']}\n\n")
        f.write(f"- **ID:** {page['id']}\n")
        f.write(f"- **URL:** {page['url']}\n")
        if page['parent']:
            f.write(f"- **Current Parent:** {page['parent']['title']} (ID: {page['parent']['id']})\n")
        else:
            f.write(f"- **Current Parent:** ROOT (no parent)\n")
        f.write("\n")
    
    if folders_info:
        f.write("## Folders Found\n\n")
        for folder in folders_info:
            f.write(f"### {folder['title']}\n\n")
            f.write(f"- **ID:** {folder['id']}\n")
            f.write(f"- **URL:** {folder['url']}\n")
            if folder['parent']:
                f.write(f"- **Parent:** {folder['parent']['title']} (ID: {folder['parent']['id']})\n")
            else:
                f.write(f"- **Parent:** ROOT (no parent)\n")
            f.write(f"- **Children:** {folder['children_count']} pages\n")
            if folder['children']:
                f.write("  **Children:**\n")
                for child in folder['children']:
                    f.write(f"  - {child['title']} (ID: {child['id']})\n")
            f.write("\n")
    
    f.write("---\n\n")
    f.write("## Recommended Folder Mapping\n\n")
    for folder, pages in sorted(mapping.items()):
        if pages:
            f.write(f"### {folder} ({len(pages)} pages)\n\n")
            for page in pages:
                f.write(f"- **{page['title']}**\n")
                f.write(f"  - ID: {page['id']}\n")
                f.write(f"  - URL: {page['url']}\n")
                if page['parent']:
                    f.write(f"  - Current Parent: {page['parent']['title']}\n")
                f.write("\n")
    
    f.write("---\n\n")
    f.write("## Action Items\n\n")
    f.write("1. Move pages to appropriate folders\n")
    f.write("2. Verify folder structure\n")
    f.write("3. Update any cross-references\n\n")

print(f"\nReport saved to: {output_file}")
print("="*80)



