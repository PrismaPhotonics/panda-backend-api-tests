"""
Verify Folder Structure - Check if documents were moved correctly
=================================================================
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

# Folder IDs
folders = {
    '01_Program_Overview': '2238578692',
    '02_Team_Management': '2237759495',
    '03_Testing_Strategy': '2237562886',
    '04_Automation_Framework': '2236579844',
    '05_BIT_Testing': '2236121093',
}

# Documents to verify
documents_to_verify = {
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

print("="*80)
print("VERIFYING FOLDER STRUCTURE")
print("="*80)

# Get all pages and check their parents
all_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)

print("\nChecking document locations...\n")

errors = []
success_count = 0

for page_id, expected_folder in documents_to_verify.items():
    try:
        page = confluence.get_page_by_id(page_id, expand='ancestors')
        page_title = page.get('title', 'Unknown')
        
        # Get ancestors (parent pages)
        ancestors = page.get('ancestors', [])
        
        if not ancestors:
            print(f"[ERROR] {page_title[:60]}...")
            print(f"        Expected in: {expected_folder}")
            print(f"        Actual location: ROOT (no parent)")
            errors.append((page_id, page_title, expected_folder, "ROOT"))
        else:
            parent_id = ancestors[-1].get('id')
            parent_title = ancestors[-1].get('title', 'Unknown')
            
            expected_folder_id = folders.get(expected_folder)
            
            if parent_id == expected_folder_id:
                print(f"[OK] {page_title[:60]}... -> {expected_folder}")
                success_count += 1
            else:
                print(f"[ERROR] {page_title[:60]}...")
                print(f"        Expected in: {expected_folder} (ID: {expected_folder_id})")
                print(f"        Actual location: {parent_title} (ID: {parent_id})")
                errors.append((page_id, page_title, expected_folder, parent_title))
                
    except Exception as e:
        print(f"[ERROR] Failed to check page {page_id}: {e}")
        errors.append((page_id, "Unknown", expected_folder, f"Error: {e}"))

print("\n" + "="*80)
print("VERIFICATION SUMMARY")
print("="*80)
print(f"Documents checked: {len(documents_to_verify)}")
print(f"Documents in correct location: {success_count}")
print(f"Documents in wrong location: {len(errors)}")

if errors:
    print("\n[ERRORS FOUND]")
    print("The following documents are not in the correct folders:")
    for page_id, title, expected, actual in errors:
        print(f"  - {title[:50]}...")
        print(f"    Expected: {expected}")
        print(f"    Actual: {actual}")
else:
    print("\n[SUCCESS] All documents are in the correct folders!")

print("\n" + "="*80)

