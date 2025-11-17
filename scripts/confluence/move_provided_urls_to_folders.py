"""
Move Provided URLs to Folder Structure
=====================================

Moves the pages from provided URLs to appropriate folders.
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

# Folder IDs (from documents we moved earlier - we know these exist)
folder_ids = {
    '01_Program_Overview': '2236874758',
    '02_Team_Management': '2236645383',
    '03_Testing_Strategy': '2236874759',
    '04_Automation_Framework': '2236907539',
    '05_BIT_Testing': '2238382086',
}

# Find missing folders by checking documents in them
print("Finding folder IDs...")
all_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)

# Check documents we know are in folders to find folder IDs
test_documents = {
    '2205319170': '01_Program_Overview',  # Long-Term Backend Refactor
    '2235498506': '02_Team_Management',  # QA Team Work Plan
    '2204237831': '03_Testing_Strategy',  # Test Review Checklist
    '2205319179': '04_Automation_Framework',  # GitHub Actions Workflow
    '1794179103': '05_BIT_Testing',  # BIT (re)usability for QA
}

for page_id, expected_folder in test_documents.items():
    try:
        page = confluence.get_page_by_id(page_id, expand='ancestors')
        ancestors = page.get('ancestors', [])
        if ancestors:
            parent_id = ancestors[-1].get('id')
            parent_title = ancestors[-1].get('title', 'Unknown')
            
            # Verify this matches our expected folder
            if expected_folder in folder_ids and folder_ids[expected_folder] == parent_id:
                print(f"  Verified: {expected_folder} (ID: {parent_id})")
            elif expected_folder not in folder_ids:
                folder_ids[expected_folder] = parent_id
                print(f"  Found: {expected_folder} (ID: {parent_id}) - {parent_title}")
    except:
        pass

# Try to find missing folders by searching for pages with matching parent IDs
# We need to find: 06_Focus_Server, 07_Test_Plans, 08_UI_Frontend_Testing, 09_Test_Plans_Archive, 10_Infrastructure
# Let's search for pages that might be these folders
for page in all_pages:
    title = page.get('title', '')
    if title.startswith('06_Focus_Server'):
        folder_ids['06_Focus_Server'] = page.get('id')
        print(f"  Found: 06_Focus_Server (ID: {page.get('id')})")
    elif title.startswith('07_Test_Plans'):
        folder_ids['07_Test_Plans'] = page.get('id')
        print(f"  Found: 07_Test_Plans (ID: {page.get('id')})")
    elif title.startswith('08_UI_Frontend_Testing'):
        folder_ids['08_UI_Frontend_Testing'] = page.get('id')
        print(f"  Found: 08_UI_Frontend_Testing (ID: {page.get('id')})")
    elif title.startswith('09_Test_Plans_Archive'):
        folder_ids['09_Test_Plans_Archive'] = page.get('id')
        print(f"  Found: 09_Test_Plans_Archive (ID: {page.get('id')})")
    elif title.startswith('10_Infrastructure'):
        folder_ids['10_Infrastructure'] = page.get('id')
        print(f"  Found: 10_Infrastructure (ID: {page.get('id')})")

# If folders not found, we'll need to create them or use alternative IDs
for folder_name in ['06_Focus_Server', '07_Test_Plans', '08_UI_Frontend_Testing', '09_Test_Plans_Archive', '10_Infrastructure']:
    if folder_name not in folder_ids:
        folder_ids[folder_name] = None
        print(f"  NOT FOUND: {folder_name}")

# Documents to move (page_id -> target_folder)
documents_to_move = {
    # 03_Testing_Strategy
    '2180448265': '03_Testing_Strategy',  # Live vs Historic Mode - Complete Analysis
    '2180808717': '03_Testing_Strategy',  # Live vs Historic Mode Testing - Implementation Summary
    '2222653443': '03_Testing_Strategy',  # Jira Ticket Template
    
    # 06_Focus_Server
    '2112094219': '06_Focus_Server',  # FOCUS SERVER – Full Test Plan (Drop 3)
    
    # 07_Test_Plans
    '2223079425': '07_Test_Plans',  # Kubernetes Tests Roadmap
    '2112552979': '07_Test_Plans',  # SMART RECORDER – Full Test Plan (Drop 3)
    '2111930403': '07_Test_Plans',  # STORAGE MANAGER – Full Test Plan (Drop 3)
    
    # 09_Test_Plans_Archive (Drop 3 plans are historical)
    # '2079817729': '09_Test_Plans_Archive',  # Drop 3 – Backend Test Plans - This is the parent, might need special handling
}

# Document titles
document_titles = {
    '2180448265': 'Live vs Historic Mode - Complete Analysis',
    '2180808717': 'Live vs Historic Mode Testing - Implementation Summary',
    '2222653443': 'Jira Ticket Template',
    '2112094219': 'FOCUS SERVER – Full Test Plan (Drop 3)',
    '2223079425': 'Kubernetes Tests Roadmap',
    '2112552979': 'SMART RECORDER – Full Test Plan (Drop 3)',
    '2111930403': 'STORAGE MANAGER – Full Test Plan (Drop 3, Interim until service exists)',
    '2079817729': 'Drop 3 – Backend Test Plans (Recorder, Focus Server, Storage Manager)',
}

print("="*80)
print("MOVING PROVIDED URLS TO FOLDER STRUCTURE")
print("="*80)

# Setup REST API authentication
auth = base64.b64encode(f"{email}:{api_token}".encode()).decode()
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {auth}'
}

# Move documents
print("\nStep 1: Moving documents...\n")
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
print(f"Documents to move: {len(documents_to_move)}")
print(f"Documents moved successfully: {moved_count}")
print(f"Documents failed: {failed_count}")

if failed_count > 0:
    print("\n[WARNING] Some documents failed to move. Check errors above.")
else:
    print("\n[SUCCESS] All documents moved successfully!")

print("\n" + "="*80)

