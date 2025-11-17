"""
Execute Folder Restructure - Create Folders and Move Documents
===============================================================

Creates folders and moves documents to new structure in Confluence.
"""

import sys
import yaml
import requests
import base64
from pathlib import Path
from typing import Dict, Any, Optional
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

space_key = 'PRISMATEAM'
parent_folder_id = '2079784961'  # QA & Testing Program folder

# Initialize Confluence client
confluence = Confluence(
    url=f"{base_url}/wiki",
    username=email,
    password=api_token
)

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
    '2205319170': '01_Program_Overview',  # Long-Term Backend Refactor
    '2203975683': '01_Program_Overview',  # Backend Test Automation Framework
    '2234646535': '01_Program_Overview',  # Executive Summary
    '2203648004': '01_Program_Overview',  # Backend Improvement Program - Roadmap
    '2235498506': '02_Team_Management',  # QA Team Work Plan
    '2223570946': '02_Team_Management',  # Processes & Workflows
    '2222555141': '02_Team_Management',  # Scope & Responsibilities
    '2223308806': '02_Team_Management',  # Sprint Backlog
    '2204237831': '03_Testing_Strategy',  # Test Review Checklist
    '2205384707': '03_Testing_Strategy',  # Component Test Document
    '2205319179': '04_Automation_Framework',  # GitHub Actions Workflow
    '1794179103': '05_BIT_Testing',  # BIT (re)usability for QA
}

# Document titles for reference
document_titles = {
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

print("="*80)
print("CONFLUENCE FOLDER RESTRUCTURE - EXECUTION")
print("="*80)

# Setup REST API authentication
auth = base64.b64encode(f"{email}:{api_token}".encode()).decode()
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {auth}'
}

# Step 1: Create folders (as pages in parent folder)
print("\nStep 1: Creating folders...")
folder_ids = {}

for folder_name in folders_to_create:
    try:
        # Check if folder already exists
        existing_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)
        folder_exists = False
        for page in existing_pages:
            if page.get('title') == folder_name:
                folder_ids[folder_name] = page.get('id')
                print(f"  [OK] Folder exists: {folder_name} (ID: {folder_ids[folder_name]})")
                folder_exists = True
                break
        
        if not folder_exists:
            # Create folder as a page
            print(f"  [CREATE] Creating folder: {folder_name}...")
            
            # Create page in parent folder
            create_url = f"{base_url}/wiki/rest/api/content"
            create_data = {
                "type": "page",
                "title": folder_name,
                "space": {"key": space_key},
                "ancestors": [{"id": parent_folder_id}],
                "body": {
                    "storage": {
                        "value": f"<p>Folder: {folder_name}</p>",
                        "representation": "storage"
                    }
                }
            }
            
            response = requests.post(create_url, json=create_data, headers=headers)
            if response.status_code == 200:
                folder_id = response.json().get('id')
                folder_ids[folder_name] = folder_id
                print(f"  [OK] Created folder: {folder_name} (ID: {folder_id})")
            else:
                print(f"  [ERROR] Failed to create folder '{folder_name}': {response.status_code} - {response.text}")
                folder_ids[folder_name] = None
                
    except Exception as e:
        print(f"  [ERROR] Error creating folder '{folder_name}': {e}")
        folder_ids[folder_name] = None

# Step 2: Move documents
print("\nStep 2: Moving documents...")
moved_count = 0
failed_count = 0

for page_id, target_folder in documents_to_move.items():
    try:
        page_title = document_titles.get(page_id, f"Page {page_id}")
        target_folder_id = folder_ids.get(target_folder)
        
        if target_folder_id is None:
            print(f"  [SKIP] {page_title[:50]}... - Target folder '{target_folder}' not found")
            failed_count += 1
            continue
        
        print(f"  [MOVE] Moving: {page_title[:60]}...")
        print(f"         Target: {target_folder} (ID: {target_folder_id})")
        
        # Get current page to preserve content
        current_page = confluence.get_page_by_id(page_id, expand='body.storage,version')
        current_version = current_page.get('version', {}).get('number', 1)
        
        # Update page with new ancestor (parent)
        update_url = f"{base_url}/wiki/rest/api/content/{page_id}"
        update_data = {
            "id": page_id,
            "type": "page",
            "title": current_page.get('title'),
            "space": {"key": space_key},
            "ancestors": [{"id": target_folder_id}],
            "body": current_page.get('body', {}),
            "version": {"number": current_version + 1}
        }
        
        response = requests.put(update_url, json=update_data, headers=headers)
        
        if response.status_code in [200, 201]:
            print(f"  [OK] Moved successfully")
            moved_count += 1
        else:
            print(f"  [ERROR] Failed to move: {response.status_code} - {response.text}")
            failed_count += 1
            
    except Exception as e:
        print(f"  [ERROR] Error moving page {page_id}: {e}")
        failed_count += 1

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Folders to create: {len(folders_to_create)}")
print(f"Folders created/found: {sum(1 for v in folder_ids.values() if v is not None)}")
print(f"Documents to move: {len(documents_to_move)}")
print(f"Documents moved successfully: {moved_count}")
print(f"Documents failed: {failed_count}")

if failed_count > 0:
    print("\n[WARNING] Some documents failed to move. Check errors above.")
else:
    print("\n[SUCCESS] All documents moved successfully!")

print("\n" + "="*80)

