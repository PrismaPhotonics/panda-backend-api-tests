"""
Update all Jira test cases with improved descriptions using Rovo MCP.
"""

import re
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
desc_file = project_root / 'scripts/jira/improved_test_descriptions.txt'

def parse_improved_descriptions():
    """Parse improved descriptions file."""
    content = desc_file.read_text(encoding='utf-8')
    
    descriptions = {}
    current_test = None
    current_desc = []
    
    for line in content.split('\n'):
        if line.startswith('TEST: PZ-'):
            if current_test:
                descriptions[current_test] = '\n'.join(current_desc).strip()
            current_test = line.replace('TEST: ', '').strip()
            current_desc = []
        elif line.startswith('=' * 80):
            continue
        elif current_test:
            current_desc.append(line)
    
    if current_test:
        descriptions[current_test] = '\n'.join(current_desc).strip()
    
    return descriptions

def main():
    """Print instructions for updating Jira."""
    descriptions = parse_improved_descriptions()
    
    print(f"Found {len(descriptions)} improved descriptions")
    print("\nUse the following MCP calls to update each test:")
    print("\nExample format:")
    print("-" * 80)
    print("mcp_atlassian-rovo_editJiraIssue")
    print("  cloudId='a8cc7b3d-f5fd-41a1-a7ca-b9fc4ddfe0b4'")
    print("  issueIdOrKey='PZ-14933'")
    print("  fields={'description': '<description_text>'}")

if __name__ == "__main__":
    main()

