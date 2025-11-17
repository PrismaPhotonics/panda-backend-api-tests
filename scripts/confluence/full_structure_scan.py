"""
Full Structure Scan - Find all pages and their relationships
============================================================
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

# Documents we moved
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

print("="*80)
print("FULL STRUCTURE SCAN")
print("="*80)

# Get all pages
print("\nGetting all pages...")
all_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)

# Check each document we moved
print("\nChecking documents we moved...\n")

structure_report = {
    'in_main_folder': [],
    'in_subfolders': [],
    'not_found': [],
    'in_wrong_location': []
}

for page_id, page_title in documents_we_moved.items():
    try:
        page = confluence.get_page_by_id(page_id, expand='ancestors,space')
        ancestors = page.get('ancestors', [])
        
        print(f"Document: {page_title[:60]}...")
        print(f"  ID: {page_id}")
        
        if not ancestors:
            print(f"  Location: ROOT (no parent)")
            structure_report['in_wrong_location'].append({
                'id': page_id,
                'title': page_title,
                'location': 'ROOT'
            })
        else:
            parent = ancestors[-1]
            parent_title = parent.get('title', 'Unknown')
            parent_id = parent.get('id')
            
            print(f"  Location: {parent_title} (ID: {parent_id})")
            
            if parent_id == main_folder_id:
                structure_report['in_main_folder'].append({
                    'id': page_id,
                    'title': page_title,
                    'parent': parent_title
                })
            elif parent_title.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_')):
                structure_report['in_subfolders'].append({
                    'id': page_id,
                    'title': page_title,
                    'parent': parent_title,
                    'parent_id': parent_id
                })
            else:
                structure_report['in_wrong_location'].append({
                    'id': page_id,
                    'title': page_title,
                    'location': parent_title,
                    'parent_id': parent_id
                })
        
        print()
        
    except Exception as e:
        print(f"  [ERROR] Failed to get page {page_id}: {e}\n")
        structure_report['not_found'].append({
            'id': page_id,
            'title': page_title,
            'error': str(e)
        })

# Check main folder children
print("\nChecking main folder direct children...")
try:
    children = confluence.get_page_child_by_type(main_folder_id, type='page', start=0, limit=1000)
    print(f"Main folder has {len(children)} direct children:")
    for child in children:
        print(f"  - {child.get('title', 'Unknown')} (ID: {child.get('id')})")
except Exception as e:
    print(f"Error getting children: {e}")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Documents in main folder: {len(structure_report['in_main_folder'])}")
print(f"Documents in subfolders: {len(structure_report['in_subfolders'])}")
print(f"Documents in wrong location: {len(structure_report['in_wrong_location'])}")
print(f"Documents not found: {len(structure_report['not_found'])}")

# Save report
output_file = project_root / 'docs' / '06_project_management' / 'FULL_STRUCTURE_SCAN_REPORT.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# Full Structure Scan Report\n\n")
    f.write(f"**Date:** 2025-11-05\n")
    f.write(f"**Main Folder ID:** {main_folder_id}\n\n")
    f.write("---\n\n")
    
    f.write("## Summary\n\n")
    f.write(f"- **Documents in main folder:** {len(structure_report['in_main_folder'])}\n")
    f.write(f"- **Documents in subfolders:** {len(structure_report['in_subfolders'])}\n")
    f.write(f"- **Documents in wrong location:** {len(structure_report['in_wrong_location'])}\n")
    f.write(f"- **Documents not found:** {len(structure_report['not_found'])}\n\n")
    
    if structure_report['in_subfolders']:
        f.write("## Documents in Subfolders\n\n")
        for doc in structure_report['in_subfolders']:
            f.write(f"- **{doc['title']}**\n")
            f.write(f"  - ID: {doc['id']}\n")
            f.write(f"  - Parent: {doc['parent']} (ID: {doc['parent_id']})\n\n")
    
    if structure_report['in_wrong_location']:
        f.write("## Documents in Wrong Location\n\n")
        for doc in structure_report['in_wrong_location']:
            f.write(f"- **{doc['title']}**\n")
            f.write(f"  - ID: {doc['id']}\n")
            f.write(f"  - Current location: {doc.get('location', 'Unknown')}\n\n")

print(f"\nReport saved to: {output_file}")
print("="*80)

