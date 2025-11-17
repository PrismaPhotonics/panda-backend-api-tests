"""
Create Missing Folders and Move Documents
==========================================

Creates missing folders and moves all documents to appropriate folders.
"""

import sys
import yaml
import requests
import base64
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

# Known folder IDs (from previous analysis)
known_folder_ids = {
    '01_Program_Overview': '2236874758',
    '02_Team_Management': '2236645383',
    '03_Testing_Strategy': '2236874759',
    '04_Automation_Framework': '2236907539',
    '05_BIT_Testing': '2238382086',
}

# Folders to create
folders_to_create = {
    '06_Focus_Server': None,
    '07_Test_Plans': None,
    '08_UI_Frontend_Testing': None,
    '09_Test_Plans_Archive': None,
    '10_Infrastructure': None,
}

# Documents to move
documents_to_move = {
    # 06_Focus_Server
    '2112094219': '06_Focus_Server',  # FOCUS SERVER – Full Test Plan (Drop 3)
    
    # 07_Test_Plans
    '2223079425': '07_Test_Plans',  # Kubernetes Tests Roadmap
    '2112552979': '07_Test_Plans',  # SMART RECORDER – Full Test Plan (Drop 3)
    '2111930403': '07_Test_Plans',  # STORAGE MANAGER – Full Test Plan (Drop 3)
}

document_titles = {
    '2112094219': 'FOCUS SERVER – Full Test Plan (Drop 3)',
    '2223079425': 'Kubernetes Tests Roadmap',
    '2112552979': 'SMART RECORDER – Full Test Plan (Drop 3)',
    '2111930403': 'STORAGE MANAGER – Full Test Plan (Drop 3, Interim until service exists)',
}

print("="*80)
print("CREATE MISSING FOLDERS AND MOVE DOCUMENTS")
print("="*80)

# Setup REST API authentication
auth = base64.b64encode(f"{email}:{api_token}".encode()).decode()
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {auth}'
}

# Step 1: Check if folders exist, create if missing
print("\nStep 1: Checking/Creating folders...\n")

all_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)
folder_ids = known_folder_ids.copy()

for folder_name in folders_to_create.keys():
    # Check if folder exists
    found = False
    for page in all_pages:
        if page.get('title') == folder_name:
            folder_id = page.get('id')
            folder_ids[folder_name] = folder_id
            print(f"[OK] Folder exists: {folder_name} (ID: {folder_id})")
            found = True
            break
    
    if not found:
        # Create folder
        print(f"[CREATE] Creating folder: {folder_name}...")
        create_url = f"{base_url}/wiki/rest/api/content"
        create_data = {
            "type": "page",
            "title": folder_name,
            "space": {"key": space_key},
            "ancestors": [{"id": main_folder_id}],
            "body": {
                "storage": {
                    "value": f"<p>Folder: {folder_name}</p>",
                    "representation": "storage"
                }
            }
        }
        
        try:
            response = requests.post(create_url, json=create_data, headers=headers)
            if response.status_code == 200:
                folder_id = response.json().get('id')
                folder_ids[folder_name] = folder_id
                print(f"[OK] Created folder: {folder_name} (ID: {folder_id})")
            else:
                print(f"[ERROR] Failed to create folder '{folder_name}': {response.status_code} - {response.text[:200]}")
                folder_ids[folder_name] = None
        except Exception as e:
            print(f"[ERROR] Error creating folder '{folder_name}': {e}")
            folder_ids[folder_name] = None

# Step 2: Move documents
print("\nStep 2: Moving documents...\n")
moved_count = 0
failed_count = 0

for page_id, target_folder in documents_to_move.items():
    try:
        page_title = document_titles.get(page_id, f"Page {page_id}")
        target_folder_id = folder_ids.get(target_folder)
        
        if target_folder_id is None:
            print(f"[SKIP] {page_title[:50]}... - Target folder '{target_folder}' not found")
            failed_count += 1
            continue
        
        print(f"[MOVE] Moving: {page_title[:60]}...")
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
            print(f"[OK] Moved successfully")
            moved_count += 1
        else:
            print(f"[ERROR] Failed to move: {response.status_code} - {response.text[:200]}")
            failed_count += 1
            
    except Exception as e:
        print(f"[ERROR] Error moving page {page_id}: {e}")
        failed_count += 1

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Folders checked/created: {len(folders_to_create)}")
print(f"Folders available: {sum(1 for v in folder_ids.values() if v is not None)}")
print(f"Documents to move: {len(documents_to_move)}")
print(f"Documents moved successfully: {moved_count}")
print(f"Documents failed: {failed_count}")

if failed_count > 0:
    print("\n[WARNING] Some documents failed to move. Check errors above.")
else:
    print("\n[SUCCESS] All documents moved successfully!")

print("\n" + "="*80)
print("FOLDER IDs:")
for folder_name, folder_id in sorted(folder_ids.items()):
    if folder_id:
        print(f"  {folder_name}: {folder_id}")
    else:
        print(f"  {folder_name}: NOT FOUND")
print("="*80)



