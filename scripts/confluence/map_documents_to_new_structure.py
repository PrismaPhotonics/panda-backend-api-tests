"""
Map Documents to New Folder Structure
=====================================

Identifies documents created by Roy and maps them to the new folder structure.
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
folder_id = '2079784961'

print("Scanning documents in QA & Testing Program folder...\n")

# Get all pages in the space
all_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)

# Filter pages created by Roy or related to QA/Testing/Backend
roy_documents = []
qa_documents = []

for page in all_pages:
    title = page.get('title', '')
    page_id = page.get('id')
    creator = page.get('version', {}).get('by', {}).get('displayName', '')
    url = page.get('_links', {}).get('webui', '')
    
    # Check if created by Roy
    if 'roy' in creator.lower() or 'avrahami' in creator.lower():
        roy_documents.append({
            'id': page_id,
            'title': title,
            'creator': creator,
            'url': url
        })
    
    # Check if QA/Testing/Backend related
    title_lower = title.lower()
    qa_keywords = [
        'qa', 'test', 'testing', 'automation', 'backend', 'focus server',
        'bit', 'process', 'workflow', 'strategy', 'plan', 'team'
    ]
    if any(keyword in title_lower for keyword in qa_keywords):
        qa_documents.append({
            'id': page_id,
            'title': title,
            'creator': creator,
            'url': url
        })

# Define mapping to new folders
folder_mapping = {
    '01_Program_Overview': [
        'Long-Term Backend Refactor, Architecture & Testing Strategy',
        'Backend Test Automation Framework & Long-Term Strategy Plan',
        'Backend Test Automation Framework & Long-Term Strategy Plan - Executive Summary',
        'Backend Improvement Program - Roadmap',
        'Long term design',
        'Backend Refactor'
    ],
    '02_Team_Management': [
        'QA Team Work Plan - Panda & Focus Server',
        'Focus Server QA Team - Processes & Workflows',
        'Focus Server QA Team - Scope & Responsibilities',
        'Focus Server QA Team - Sprint Backlog',
        'QA Team',
        'Team Management'
    ],
    '03_Testing_Strategy': [
        'Test Strategy',
        'Test Planning',
        'Test Review Checklist',
        'Component Test Document',
        'Testing Best Practices'
    ],
    '04_Automation_Framework': [
        'Automation Status Tracking',
        'Automation Labels',
        'Automation Scripts',
        'CI/CD Integration',
        'GitHub Actions Workflow: Quality Gates',
        'Pytest Integrations',
        'QA Framework Docs'
    ],
    '05_BIT_Testing': [
        'BIT (re)usability for QA',
        'BIT tests low level design',
        'Bit Tests Table',
        'Updated BIT tests guide',
        'BIT related guides',
        'BIT troubeshooting',
        'BIT External Integrations'
    ],
    '06_Focus_Server': [
        'Focus Server',
        'Focus Server - Integrations Map',
        'Focus Server – E2E Scenarios',
        'FOCUS SERVER – Full Test Plan',
        'Focus Server – Parameterized Testing Plan',
        'System Architecture - RabbitMQ Focus'
    ],
    '07_Test_Plans': [
        'Drop 3 – Backend Test Plans',
        'FOCUS SERVER – Full Test Plan',
        'SMART RECORDER – Full Test Plan',
        'STORAGE MANAGER – Full Test Plan',
        'Focus Server – E2E Scenarios',
        'Test Plan',
        'Test Plans'
    ],
    '08_UI_Frontend_Testing': [
        'UI Cloud Automation',
        'Web App Test Plans',
        'InterrogatorQA',
        'Test Strategy Summary - WebApp',
        'UI Testing',
        'Frontend Testing'
    ],
    '09_Test_Plans_Archive': [
        # Historical test plans - will be identified separately
    ],
    '10_Infrastructure': [
        'Test Environments',
        'Infrastructure',
        'System Architecture'
    ]
}

# Map documents to folders
mapped_documents = defaultdict(list)

for doc in roy_documents + qa_documents:
    title = doc['title']
    matched = False
    
    for folder, keywords in folder_mapping.items():
        for keyword in keywords:
            if keyword.lower() in title.lower():
                mapped_documents[folder].append(doc)
                matched = True
                break
        if matched:
            break
    
    if not matched:
        mapped_documents['UNMAPPED'].append(doc)

# Save mapping report
output_file = project_root / 'docs' / '06_project_management' / 'DOCUMENTS_MAPPING_TO_FOLDERS.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# Documents Mapping to New Folder Structure\n\n")
    f.write(f"**Analysis Date:** 2025-11-05\n")
    f.write(f"**Total Documents Scanned:** {len(all_pages)}\n")
    f.write(f"**Roy's Documents:** {len(roy_documents)}\n")
    f.write(f"**QA/Testing Related:** {len(qa_documents)}\n\n")
    f.write("---\n\n")
    
    f.write("## Documents Mapping\n\n")
    
    for folder, docs in sorted(mapped_documents.items()):
        if docs:
            f.write(f"### {folder} ({len(docs)} documents)\n\n")
            for doc in sorted(docs, key=lambda x: x['title']):
                f.write(f"- **{doc['title']}**\n")
                f.write(f"  - ID: {doc['id']}\n")
                f.write(f"  - Creator: {doc.get('creator', 'Unknown')}\n")
                f.write(f"  - URL: {doc['url']}\n\n")
    
    f.write("---\n\n")
    f.write("## Implementation Plan\n\n")
    f.write("### Step 1: Create New Folders\n")
    f.write("1. Create folder structure in Confluence\n")
    f.write("2. Verify folder creation\n\n")
    f.write("### Step 2: Move Documents\n")
    f.write("1. Move documents to appropriate folders\n")
    f.write("2. Update document references\n")
    f.write("3. Verify document locations\n\n")

print(f"\nMapping complete!")
print(f"Documents mapped to {len([k for k in mapped_documents.keys() if k != 'UNMAPPED'])} folders")
print(f"Unmapped documents: {len(mapped_documents.get('UNMAPPED', []))}")
print(f"\nReport saved to: {output_file}")

