"""
Investigate Main Folder Structure in Confluence
===============================================

Scans the main QA & Testing Program folder and shows its current structure.
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

space_key = 'PRISMATEAM'
main_folder_id = '2079784961'  # QA & Testing Program folder

print("="*80)
print("INVESTIGATING MAIN FOLDER STRUCTURE")
print("="*80)
print(f"Folder ID: {main_folder_id}")
print(f"Space: {space_key}")
print(f"URL: {base_url}/wiki/spaces/{space_key}/folder/{main_folder_id}")
print("="*80)

# Get main folder info
try:
    main_folder = confluence.get_page_by_id(main_folder_id, expand='space,version')
    print(f"\nMain Folder Title: {main_folder.get('title', 'Unknown')}")
    print(f"Main Folder ID: {main_folder_id}")
except Exception as e:
    print(f"\nError getting main folder: {e}")

# Get all pages in space
print("\nScanning all pages in space...")
all_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)

# Find pages that are direct children of main folder
print("\nFinding pages in main folder...")
main_folder_pages = []
subfolders = []
other_pages = []

for page in all_pages:
    try:
        page_id = page.get('id')
        page_title = page.get('title', 'Unknown')
        
        # Get full page with ancestors
        full_page = confluence.get_page_by_id(page_id, expand='ancestors')
        ancestors = full_page.get('ancestors', [])
        
        # Check if this page is a direct child of main folder
        if ancestors:
            parent_id = ancestors[-1].get('id')
            if parent_id == main_folder_id:
                # This is a direct child
                if page_title.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_')):
                    subfolders.append({
                        'id': page_id,
                        'title': page_title,
                        'type': 'subfolder'
                    })
                else:
                    main_folder_pages.append({
                        'id': page_id,
                        'title': page_title,
                        'type': 'document'
                    })
        else:
            # Page has no parent - might be in root
            if page_id != main_folder_id:
                other_pages.append({
                    'id': page_id,
                    'title': page_title
                })
    except Exception as e:
        print(f"  Error processing page {page.get('id', 'unknown')}: {e}")

# Sort subfolders by name
subfolders.sort(key=lambda x: x['title'])
main_folder_pages.sort(key=lambda x: x['title'])

print("\n" + "="*80)
print("FOLDER STRUCTURE ANALYSIS")
print("="*80)

print(f"\nSUBFOLDERS (direct children of main folder): {len(subfolders)}")
for folder in subfolders:
    print(f"  - {folder['title']} (ID: {folder['id']})")
    
    # Find pages in this subfolder
    pages_in_folder = []
    for page in all_pages:
        try:
            full_page = confluence.get_page_by_id(page.get('id'), expand='ancestors')
            ancestors = full_page.get('ancestors', [])
            if ancestors and ancestors[-1].get('id') == folder['id']:
                pages_in_folder.append({
                    'id': page.get('id'),
                    'title': page.get('title', 'Unknown')
                })
        except:
            pass
    
    if pages_in_folder:
        print(f"    Contains {len(pages_in_folder)} pages:")
        for doc in sorted(pages_in_folder, key=lambda x: x['title']):
            print(f"      • {doc['title']}")

print(f"\nDOCUMENTS (direct children of main folder): {len(main_folder_pages)}")
for doc in main_folder_pages:
    print(f"  - {doc['title']} (ID: {doc['id']})")

print(f"\nOTHER PAGES (not in main folder): {len(other_pages)}")
if other_pages:
    print("  (Pages that might need to be moved)")

# Save report
output_file = project_root / 'docs' / '06_project_management' / 'MAIN_FOLDER_STRUCTURE_REPORT.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# Main Folder Structure Report\n\n")
    f.write(f"**Folder ID:** {main_folder_id}\n")
    f.write(f"**Space:** {space_key}\n")
    f.write(f"**URL:** {base_url}/wiki/spaces/{space_key}/folder/{main_folder_id}\n")
    f.write(f"**Report Date:** 2025-11-05\n\n")
    f.write("---\n\n")
    
    f.write("## Folder Structure\n\n")
    f.write(f"### Subfolders ({len(subfolders)})\n\n")
    for folder in subfolders:
        f.write(f"#### {folder['title']}\n\n")
        f.write(f"- **ID:** {folder['id']}\n")
        f.write(f"- **Type:** Subfolder\n\n")
        
        # Find pages in this subfolder
        pages_in_folder = []
        for page in all_pages:
            try:
                full_page = confluence.get_page_by_id(page.get('id'), expand='ancestors')
                ancestors = full_page.get('ancestors', [])
                if ancestors and ancestors[-1].get('id') == folder['id']:
                    pages_in_folder.append({
                        'id': page.get('id'),
                        'title': page.get('title', 'Unknown')
                    })
            except:
                pass
        
        if pages_in_folder:
            f.write(f"**Pages in folder ({len(pages_in_folder)}):**\n\n")
            for doc in sorted(pages_in_folder, key=lambda x: x['title']):
                f.write(f"- **{doc['title']}**\n")
                f.write(f"  - ID: {doc['id']}\n")
                f.write(f"  - URL: {base_url}/wiki/spaces/{space_key}/pages/{doc['id']}\n\n")
        else:
            f.write("**No pages in this folder.**\n\n")
    
    f.write("---\n\n")
    f.write("### Documents in Main Folder Root\n\n")
    if main_folder_pages:
        f.write(f"**Total:** {len(main_folder_pages)} documents\n\n")
        for doc in main_folder_pages:
            f.write(f"- **{doc['title']}**\n")
            f.write(f"  - ID: {doc['id']}\n")
            f.write(f"  - URL: {base_url}/wiki/spaces/{space_key}/pages/{doc['id']}\n\n")
    else:
        f.write("**No documents in main folder root.**\n\n")

print(f"\n\nReport saved to: {output_file}")
print("="*80)

