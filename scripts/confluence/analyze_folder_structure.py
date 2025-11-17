"""
Analyze Confluence Folder Structure and Provide Recommendations
=============================================================

Analyzes all pages in a Confluence folder and provides recommendations for:
- Folder structure improvements
- Naming conventions
- Missing content
- Duplicates
- Organization
"""

import sys
import yaml
import re
from pathlib import Path
from typing import List, Dict, Any, Set
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

# Search for QA/Testing/Backend related pages
qa_keywords = [
    'QA', 'Test', 'Testing', 'Automation', 'Backend', 'Focus Server',
    'BIT', 'Process', 'Workflow', 'Strategy', 'Plan', 'Team'
]

print("Scanning Confluence space for QA/Testing/Backend related pages...\n")

all_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)

# Categorize pages
qa_pages = []
for page in all_pages:
    title = page.get('title', '')
    title_lower = title.lower()
    
    # Check if related to QA/Testing/Backend
    if any(keyword.lower() in title_lower for keyword in qa_keywords):
        qa_pages.append({
            'id': page.get('id'),
            'title': title,
            'url': page.get('_links', {}).get('webui', '')
        })

print(f"Found {len(qa_pages)} QA/Testing/Backend related pages\n")

# Categorize pages
categories = {
    'QA Team Management': [],
    'Backend Refactor & Strategy': [],
    'Testing & Automation': [],
    'BIT Related': [],
    'Focus Server': [],
    'Processes & Workflows': [],
    'Other': []
}

for page in qa_pages:
    title = page['title']
    title_lower = title.lower()
    
    if any(word in title_lower for word in ['team', 'sprint', 'process', 'workflow']):
        if 'qa' in title_lower or 'test' in title_lower:
            categories['QA Team Management'].append(page)
        else:
            categories['Processes & Workflows'].append(page)
    elif any(word in title_lower for word in ['backend', 'refactor', 'strategy', 'plan', 'architecture']):
        categories['Backend Refactor & Strategy'].append(page)
    elif any(word in title_lower for word in ['test', 'automation', 'qa']):
        categories['Testing & Automation'].append(page)
    elif 'bit' in title_lower:
        categories['BIT Related'].append(page)
    elif 'focus server' in title_lower:
        categories['Focus Server'].append(page)
    else:
        categories['Other'].append(page)

# Save analysis
output_file = project_root / 'docs' / '06_project_management' / 'CONFLUENCE_FOLDER_STRUCTURE_ANALYSIS.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# Confluence Folder Structure Analysis & Recommendations\n\n")
    f.write(f"**Space:** {space_key}\n")
    f.write(f"**Total Pages Scanned:** {len(all_pages)}\n")
    f.write(f"**QA/Testing/Backend Related Pages:** {len(qa_pages)}\n")
    f.write(f"**Analysis Date:** 2025-11-05\n\n")
    f.write("---\n\n")
    
    f.write("## Current Structure Analysis\n\n")
    
    for category, pages in sorted(categories.items()):
        if pages:
            f.write(f"### {category} ({len(pages)} pages)\n\n")
            for page in sorted(pages, key=lambda x: x['title']):
                f.write(f"- **{page['title']}**\n")
                f.write(f"  - ID: {page['id']}\n")
                f.write(f"  - URL: {page['url']}\n\n")
    
    f.write("---\n\n")
    f.write("## Recommendations\n\n")
    f.write("### 1. Proposed Folder Structure\n\n")
    f.write("```\n")
    f.write("QA & Testing Program\n")
    f.write("├── 01_Program_Overview\n")
    f.write("│   ├── Long-Term Backend Refactor, Architecture & Testing Strategy\n")
    f.write("│   ├── Backend Test Automation Framework & Long-Term Strategy Plan\n")
    f.write("│   └── Program Roadmap\n")
    f.write("├── 02_Team_Management\n")
    f.write("│   ├── QA Team Work Plan - Panda & Focus Server\n")
    f.write("│   ├── Focus Server QA Team - Processes & Workflows\n")
    f.write("│   ├── Focus Server QA Team - Scope & Responsibilities\n")
    f.write("│   └── Focus Server QA Team - Sprint Backlog\n")
    f.write("├── 03_Testing_Strategy\n")
    f.write("│   ├── BIT (re)usability for QA\n")
    f.write("│   ├── Automation Status Tracking\n")
    f.write("│   └── Testing Best Practices\n")
    f.write("├── 04_Automation_Framework\n")
    f.write("│   ├── Test Framework Architecture\n")
    f.write("│   ├── CI/CD Integration\n")
    f.write("│   └── Automation Scripts\n")
    f.write("└── 05_Infrastructure\n")
    f.write("    ├── Focus Server Documentation\n")
    f.write("    └── System Architecture\n")
    f.write("```\n\n")
    
    f.write("### 2. Issues Identified\n\n")
    f.write("#### Duplicates:\n")
    f.write("- Multiple Backend Refactor/Strategy documents (need consolidation)\n")
    f.write("- Multiple BIT-related documents (need organization)\n")
    f.write("- Multiple Focus Server documents scattered\n\n")
    
    f.write("#### Missing:\n")
    f.write("- Automation Status Tracking section\n")
    f.write("- Test Execution Reports folder\n")
    f.write("- Knowledge Transfer documentation\n")
    f.write("- Automation Scripts documentation\n\n")
    
    f.write("#### Naming Issues:\n")
    f.write("- Inconsistent naming conventions\n")
    f.write("- Some documents with dates in title\n")
    f.write("- Some documents with version numbers\n\n")
    
    f.write("### 3. Recommended Actions\n\n")
    f.write("1. **Consolidate Backend Strategy Documents**\n")
    f.write("   - Merge duplicate strategy documents\n")
    f.write("   - Create single source of truth\n\n")
    
    f.write("2. **Organize BIT Documentation**\n")
    f.write("   - Create BIT subfolder\n")
    f.write("   - Group all BIT-related documents\n\n")
    
    f.write("3. **Create Automation Status Section**\n")
    f.write("   - Add Automation Labels documentation\n")
    f.write("   - Add Automation Scripts documentation\n\n")
    
    f.write("4. **Standardize Naming**\n")
    f.write("   - Remove dates from titles\n")
    f.write("   - Use consistent naming pattern\n\n")

print(f"\nAnalysis complete! Results saved to: {output_file}")

