"""
Find Folder IDs - Search for folders by name
============================================
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

# Folder names to find
folder_names = [
    '01_Program_Overview',
    '02_Team_Management',
    '03_Testing_Strategy',
    '04_Automation_Framework',
    '05_BIT_Testing',
    '06_Focus_Server',
    '07_Test_Plans',
    '08_UI_Frontend_Testing',
    '09_Test_Plans_Archive',
    '10_Infrastructure',
]

print("="*80)
print("FINDING FOLDER IDs")
print("="*80)

# Get all pages
print("\nSearching for folders...\n")
all_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)

folder_ids = {}
for folder_name in folder_names:
    found = False
    for page in all_pages:
        if page.get('title') == folder_name:
            folder_id = page.get('id')
            folder_ids[folder_name] = folder_id
            
            # Check parent
            try:
                full_page = confluence.get_page_by_id(folder_id, expand='ancestors')
                ancestors = full_page.get('ancestors', [])
                
                print(f"Folder: {folder_name}")
                print(f"  ID: {folder_id}")
                if ancestors:
                    parent = ancestors[-1]
                    print(f"  Parent: {parent.get('title', 'Unknown')} (ID: {parent.get('id')})")
                else:
                    print(f"  Parent: ROOT (no parent)")
                print()
                
                found = True
                break
            except Exception as e:
                print(f"  Error checking folder {folder_name}: {e}\n")
    
    if not found:
        print(f"Folder NOT FOUND: {folder_name}\n")
        folder_ids[folder_name] = None

# Save folder IDs
print("="*80)
print("FOLDER IDs SUMMARY")
print("="*80)
for folder_name, folder_id in sorted(folder_ids.items()):
    if folder_id:
        print(f"{folder_name}: {folder_id}")
    else:
        print(f"{folder_name}: NOT FOUND")



