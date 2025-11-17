"""
Move Documents to New Folder Structure in Confluence
===================================================

Identifies Roy's documents and moves them to the new folder structure.
Note: This script requires manual folder creation in Confluence first.
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

# Documents that Roy created (identified by title patterns)
roy_documents_mapping = {
    '01_Program_Overview': [
        {
            'title': 'Long-Term Backend Refactor, Architecture & Testing Strategy',
            'id': '2205319170',
            'url': '/spaces/PRISMATEAM/pages/2205319170/Long-Term+Backend+Refactor+Architecture+Testing+Strategy'
        },
        {
            'title': 'Backend Test Automation Framework & Long-Term Strategy Plan',
            'id': '2203975683',
            'url': '/spaces/PRISMATEAM/pages/2203975683/Backend+Test+Automation+Framework+Long-Term+Strategy+Plan'
        },
        {
            'title': 'Backend Test Automation Framework & Long-Term Strategy Plan - Executive Summary',
            'id': '2234646535',
            'url': '/spaces/PRISMATEAM/pages/2234646535/Backend+Test+Automation+Framework+Long-Term+Strategy+Plan+-+Executive+Summary'
        },
        {
            'title': 'Backend Improvement Program - Roadmap',
            'id': '2203648004',
            'url': '/spaces/PRISMATEAM/pages/2203648004/Backend+Improvement+Program+-+Roadmap'
        }
    ],
    '02_Team_Management': [
        {
            'title': 'QA Team Work Plan - Panda & Focus Server',
            'id': '2235498506',
            'url': '/spaces/PRISMATEAM/pages/2235498506/QA+Team+Work+Plan+-+Panda+Focus+Server'
        },
        {
            'title': 'Focus Server QA Team - Processes & Workflows',
            'id': '2223570946',
            'url': '/spaces/PRISMATEAM/pages/2223570946/Focus+Server+QA+Team+-+Processes+Workflows'
        },
        {
            'title': 'Focus Server QA Team - Scope & Responsibilities',
            'id': '2222555141',
            'url': '/spaces/PRISMATEAM/pages/2222555141/Focus+Server+QA+Team+-+Scope+Responsibilities'
        },
        {
            'title': 'Focus Server QA Team - Sprint Backlog for Sprints 71-72: Tasks and Priorities',
            'id': '2223308806',
            'url': '/spaces/PRISMATEAM/pages/2223308806/Focus+Server+QA+Team+-+Sprint+Backlog+for+Sprints+71-72+Tasks+and+Priorities'
        }
    ],
    '03_Testing_Strategy': [
        {
            'title': 'Test Review Checklist',
            'id': '2204237831',
            'url': '/spaces/PRISMATEAM/pages/2204237831/Test+Review+Checklist'
        },
        {
            'title': 'Component Test Document',
            'id': '2205384707',
            'url': '/spaces/PRISMATEAM/pages/2205384707/Component+Test+Document'
        }
    ],
    '04_Automation_Framework': [
        {
            'title': 'GitHub Actions Workflow: Quality Gates',
            'id': '2205319179',
            'url': '/spaces/PRISMATEAM/pages/2205319179/GitHub+Actions+Workflow+Quality+Gates'
        }
    ],
    '05_BIT_Testing': [
        {
            'title': 'BIT (re)usability for QA',
            'id': '1794179103',
            'url': '/spaces/PRISMATEAM/pages/1794179103/BIT+re+usability+for+QA'
        }
    ],
    '06_Focus_Server': [
        # Focus Server documents will be moved here
    ],
    '07_Test_Plans': [
        # Active test plans will be moved here
    ],
    '08_UI_Frontend_Testing': [
        # UI/Frontend documents will be moved here
    ]
}

print("Preparing document move plan for Roy's documents...\n")
print("="*80)
print("MOVEMENT PLAN")
print("="*80)

# Create movement plan document
output_file = project_root / 'docs' / '06_project_management' / 'DOCUMENTS_MOVE_PLAN.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# Documents Move Plan - Roy's Documents\n\n")
    f.write("**Date:** 2025-11-05\n")
    f.write("**Purpose:** Move Roy's documents to new folder structure\n\n")
    f.write("---\n\n")
    f.write("## Important Notes\n\n")
    f.write("⚠️ **Before moving documents:**\n")
    f.write("1. Create the new folder structure in Confluence manually\n")
    f.write("2. Verify all folders exist before running this script\n")
    f.write("3. This script will move documents to folders\n\n")
    f.write("---\n\n")
    
    for folder, docs in sorted(roy_documents_mapping.items()):
        if docs:
            f.write(f"## {folder}\n\n")
            f.write(f"**Total Documents:** {len(docs)}\n\n")
            
            for doc in docs:
                f.write(f"### {doc['title']}\n\n")
                f.write(f"- **Page ID:** {doc['id']}\n")
                f.write(f"- **URL:** {doc['url']}\n")
                f.write(f"- **Action:** Move to `{folder}`\n\n")
            
            f.write("---\n\n")
    
    f.write("## Implementation Steps\n\n")
    f.write("### Step 1: Create Folders in Confluence\n")
    f.write("1. Navigate to QA & Testing Program folder\n")
    f.write("2. Create the following folders:\n")
    for folder in sorted(roy_documents_mapping.keys()):
        f.write(f"   - `{folder}`\n")
    f.write("\n")
    f.write("### Step 2: Move Documents\n")
    f.write("1. For each document listed above:\n")
    f.write("   - Open the document\n")
    f.write("   - Click '...' menu → 'Move'\n")
    f.write("   - Select the target folder\n")
    f.write("   - Click 'Move'\n")
    f.write("\n")
    f.write("### Step 3: Verify\n")
    f.write("1. Check that all documents are in correct folders\n")
    f.write("2. Verify document links still work\n")
    f.write("3. Update any cross-references if needed\n\n")

print(f"\nMove plan created: {output_file}")
print(f"\nTotal documents to move: {sum(len(docs) for docs in roy_documents_mapping.values())}")
print("\nDocuments by folder:")
for folder, docs in sorted(roy_documents_mapping.items()):
    if docs:
        print(f"  {folder}: {len(docs)} documents")

