"""
Parse final improved descriptions and update all Jira test cases using Rovo MCP.
"""

import re
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
desc_file = project_root / 'scripts/jira/final_improved_descriptions.txt'

def parse_descriptions():
    """Parse improved descriptions."""
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

if __name__ == "__main__":
    descriptions = parse_descriptions()
    print(f"Parsed {len(descriptions)} descriptions")
    print("\nDescriptions ready for Jira update via Rovo MCP")
    print(f"\nTest IDs: {', '.join(sorted(descriptions.keys()))}")

