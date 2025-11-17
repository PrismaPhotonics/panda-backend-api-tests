"""
Find All Folders - Search for all folders that might be related
===============================================================
"""

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

space_key = 'PRISMATEAM'
main_folder_id = '2079784961'

print("="*80)
print("FINDING ALL FOLDERS")
print("="*80)

# Get all pages
print("\nSearching for all pages...\n")
all_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)

# Look for pages that might be our folders
potential_folders = []
for page in all_pages:
    title = page.get('title', '')
    page_id = page.get('id')
    
    # Check if title matches our folder pattern
    if any(title.startswith(f"{i:02d}_") for i in range(1, 11)):
        potential_folders.append({
            'id': page_id,
            'title': title
        })
    
    # Also check for pages with similar names
    title_lower = title.lower()
    if any(keyword in title_lower for keyword in ['program overview', 'team management', 'testing strategy', 'automation framework', 'bit testing', 'focus server', 'test plans', 'ui frontend', 'infrastructure']):
        potential_folders.append({
            'id': page_id,
            'title': title,
            'match': 'keyword'
        })

print(f"Found {len(potential_folders)} potential folders:\n")
for folder in potential_folders:
    print(f"  - {folder['title']} (ID: {folder['id']})")
    
    # Check parent
    try:
        full_page = confluence.get_page_by_id(folder['id'], expand='ancestors')
        ancestors = full_page.get('ancestors', [])
        if ancestors:
            parent = ancestors[-1]
            print(f"    Parent: {parent.get('title', 'Unknown')} (ID: {parent.get('id')})")
            
            # Check if parent is main folder
            if parent.get('id') == main_folder_id:
                print(f"    [OK] Parent is main folder!")
            else:
                print(f"    [WARNING] Parent is NOT main folder")
        else:
            print(f"    Parent: ROOT (no parent)")
    except Exception as e:
        print(f"    Error checking parent: {e}")
    print()

# Also check documents we moved earlier - where are they now?
print("\n" + "="*80)
print("CHECKING DOCUMENTS WE MOVED EARLIER")
print("="*80)

documents_we_moved = {
    '2205319170': 'Long-Term Backend Refactor, Architecture & Testing Strategy',
    '2203975683': 'Backend Test Automation Framework & Long-Term Strategy Plan',
    '2234646535': 'Backend Test Automation Framework & Long-Term Strategy Plan - Executive Summary',
    '2203648004': 'Backend Improvement Program - Roadmap',
    '2235498506': 'QA Team Work Plan - Panda & Focus Server',
    '2223570946': 'Focus Server QA Team - Processes & Workflows',
    '2222555141': 'Focus Server QA Team - Scope & Responsibilities',
    '2223308806': 'Focus Server QA Team - Sprint Backlog for Sprints 71-72',
    '2204237831': 'Test Review Checklist',
    '2205384707': 'Component Test Document',
    '2205319179': 'GitHub Actions Workflow: Quality Gates',
    '1794179103': 'BIT (re)usability for QA',
}

print("\nChecking where documents are now...\n")
for page_id, page_title in documents_we_moved.items():
    try:
        page = confluence.get_page_by_id(page_id, expand='ancestors')
        ancestors = page.get('ancestors', [])
        
        print(f"Document: {page_title[:60]}...")
        print(f"  ID: {page_id}")
        
        if ancestors:
            parent = ancestors[-1]
            print(f"  Parent: {parent.get('title', 'Unknown')} (ID: {parent.get('id')})")
        else:
            print(f"  Parent: ROOT (no parent)")
        print()
        
    except Exception as e:
        print(f"  Error checking document {page_id}: {e}\n")

print("="*80)



