"""
Deep Investigation of Folder Structure
=====================================

Checks all pages and their relationships to find the actual structure.
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

# Expected folder IDs
expected_folders = {
    '01_Program_Overview': '2238578692',
    '02_Team_Management': '2237759495',
    '03_Testing_Strategy': '2237562886',
    '04_Automation_Framework': '2236579844',
    '05_BIT_Testing': '2236121093',
    '06_Focus_Server': '2236940298',
    '07_Test_Plans': '2238283785',
    '08_UI_Frontend_Testing': '2237759512',
    '09_Test_Plans_Archive': '2237497351',
    '10_Infrastructure': '2238316553',
}

print("="*80)
print("DEEP STRUCTURE INVESTIGATION")
print("="*80)

# Check each expected folder
print("\nChecking expected folders...\n")

for folder_name, folder_id in expected_folders.items():
    try:
        folder = confluence.get_page_by_id(folder_id, expand='ancestors,space')
        folder_title = folder.get('title', 'Unknown')
        ancestors = folder.get('ancestors', [])
        
        print(f"Folder: {folder_name}")
        print(f"  Title: {folder_title}")
        print(f"  ID: {folder_id}")
        
        if ancestors:
            print(f"  Parent: {ancestors[-1].get('title', 'Unknown')} (ID: {ancestors[-1].get('id')})")
            if ancestors[-1].get('id') == main_folder_id:
                print(f"  [OK] Parent is main folder")
            else:
                print(f"  [ERROR] Parent is NOT main folder!")
        else:
            print(f"  [ERROR] No parent (in root)")
        
        # Count children
        children = confluence.get_page_child_by_type(folder_id, type='page', start=0, limit=1000)
        print(f"  Children: {len(children)} pages")
        if children:
            for child in children[:5]:  # Show first 5
                print(f"    - {child.get('title', 'Unknown')[:60]}")
        
        print()
        
    except Exception as e:
        print(f"  [ERROR] Failed to check folder {folder_name} (ID: {folder_id}): {e}\n")

# Check main folder
print("\nChecking main folder...")
try:
    main_folder = confluence.get_page_by_id(main_folder_id, expand='children.page')
    print(f"Main folder: {main_folder.get('title', 'Unknown')}")
    print(f"Main folder ID: {main_folder_id}")
    
    # Get children
    children = confluence.get_page_child_by_type(main_folder_id, type='page', start=0, limit=1000)
    print(f"Direct children: {len(children)} pages")
    
    if children:
        print("\nDirect children of main folder:")
        for child in children:
            print(f"  - {child.get('title', 'Unknown')} (ID: {child.get('id')})")
    
except Exception as e:
    print(f"Error checking main folder: {e}")

print("\n" + "="*80)

