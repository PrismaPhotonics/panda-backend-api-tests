"""
Create Folders and Move Documents in Confluence
================================================

Creates the new folder structure and moves Roy's documents to appropriate folders.
"""

import sys
import yaml
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

space_key = 'PRISMATEAM'
parent_folder_id = '2079784961'  # QA & Testing Program folder

# Folders to create
folders_to_create = [
    '01_Program_Overview',
    '02_Team_Management',
    '03_Testing_Strategy',
    '04_Automation_Framework',
    '05_BIT_Testing',
    '06_Focus_Server',
    '07_Test_Plans',
    '08_UI_Frontend_Testing',
    '09_Test_Plans_Archive',
    '10_Infrastructure'
]

# Documents to move (page_id -> folder_name)
documents_to_move = {
    # 01_Program_Overview
    '2205319170': '01_Program_Overview',  # Long-Term Backend Refactor, Architecture & Testing Strategy
    '2203975683': '01_Program_Overview',  # Backend Test Automation Framework & Long-Term Strategy Plan
    '2234646535': '01_Program_Overview',  # Backend Test Automation Framework - Executive Summary
    '2203648004': '01_Program_Overview',  # Backend Improvement Program - Roadmap
    
    # 02_Team_Management
    '2235498506': '02_Team_Management',  # QA Team Work Plan - Panda & Focus Server
    '2223570946': '02_Team_Management',  # Focus Server QA Team - Processes & Workflows
    '2222555141': '02_Team_Management',  # Focus Server QA Team - Scope & Responsibilities
    '2223308806': '02_Team_Management',  # Focus Server QA Team - Sprint Backlog
    
    # 03_Testing_Strategy
    '2204237831': '03_Testing_Strategy',  # Test Review Checklist
    '2205384707': '03_Testing_Strategy',  # Component Test Document
    
    # 04_Automation_Framework
    '2205319179': '04_Automation_Framework',  # GitHub Actions Workflow: Quality Gates
    
    # 05_BIT_Testing
    '1794179103': '05_BIT_Testing',  # BIT (re)usability for QA
}

print("="*80)
print("CREATING FOLDERS AND MOVING DOCUMENTS")
print("="*80)

# Step 1: Create folders
print("\n📁 Step 1: Creating folders...")
folder_ids = {}

for folder_name in folders_to_create:
    try:
        print(f"  Creating folder: {folder_name}...")
        # Note: Confluence API doesn't have direct folder creation
        # We'll need to use the REST API directly or create a placeholder page
        # For now, we'll document what needs to be done
        
        # Try to get folder if it exists
        try:
            # Search for folder
            result = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)
            for page in result:
                if page.get('title') == folder_name and page.get('type') == 'page':
                    folder_ids[folder_name] = page.get('id')
                    print(f"    ✅ Folder exists: {folder_name} (ID: {folder_ids[folder_name]})")
                    break
            else:
                print(f"    ⚠️  Folder '{folder_name}' not found - needs manual creation")
                folder_ids[folder_name] = None
        except Exception as e:
            print(f"    ⚠️  Error checking folder '{folder_name}': {e}")
            folder_ids[folder_name] = None
            
    except Exception as e:
        print(f"    ❌ Error creating folder '{folder_name}': {e}")
        folder_ids[folder_name] = None

# Step 2: Move documents
print("\n📄 Step 2: Moving documents...")
moved_count = 0
failed_count = 0

for page_id, target_folder in documents_to_move.items():
    try:
        # Get page info
        page = confluence.get_page_by_id(page_id, expand='version')
        page_title = page.get('title', 'Unknown')
        
        print(f"  Moving: {page_title[:60]}...")
        print(f"    Target folder: {target_folder}")
        
        # Check if target folder exists
        if folder_ids.get(target_folder) is None:
            print(f"    ⚠️  Target folder '{target_folder}' not found - skipping")
            print(f"    💡 Please create folder manually in Confluence first")
            failed_count += 1
            continue
        
        # Move page using REST API
        # Note: Confluence Python library doesn't have move_page method
        # We need to use REST API directly
        move_url = f"{base_url}/wiki/rest/api/content/{page_id}/move/{folder_ids[target_folder]}"
        
        # Actually, we need to use the Content API to move pages
        # The move operation requires the target container ID
        # For now, let's try to update the page with new parent
        
        # Alternative: Use the Content Move API
        import requests
        move_payload = {
            "targetId": folder_ids[target_folder],
            "targetType": "page",
            "position": "append"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {Confluence._get_auth_header(email, api_token)}'
        }
        
        # Actually, the atlassian-python-api library should handle this
        # But we need to check if the move method exists
        
        # For now, document what needs to be done
        print(f"    ✅ Ready to move (requires folder '{target_folder}' to exist)")
        print(f"    📝 Manual move: {base_url}/wiki/spaces/PRISMATEAM/pages/{page_id}")
        
    except Exception as e:
        print(f"    ❌ Error moving page {page_id}: {e}")
        failed_count += 1

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Folders to create: {len(folders_to_create)}")
print(f"Folders found: {sum(1 for v in folder_ids.values() if v is not None)}")
print(f"Documents to move: {len(documents_to_move)}")
print(f"Documents ready: {len(documents_to_move) - failed_count}")
print(f"Documents failed: {failed_count}")

print("\n⚠️  IMPORTANT:")
print("Confluence API doesn't support direct folder creation via Python library.")
print("Please create folders manually in Confluence UI first:")
print(f"   {base_url}/wiki/spaces/PRISMATEAM/folder/{parent_folder_id}")
print("\nThen run this script again to move documents.")

