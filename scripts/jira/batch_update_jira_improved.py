"""
Batch update all Jira test cases with improved descriptions using Rovo MCP.
Reads improved descriptions and updates Jira in batches.
"""

import re
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
desc_file = project_root / 'scripts/jira/improved_test_descriptions.txt'

def parse_improved_descriptions():
    """Parse improved descriptions file and fix paths."""
    content = desc_file.read_text(encoding='utf-8')
    
    descriptions = {}
    current_test = None
    current_desc = []
    
    for line in content.split('\n'):
        if line.startswith('TEST: PZ-'):
            if current_test:
                desc_text = '\n'.join(current_desc).strip()
                # Fix backslashes in paths
                desc_text = desc_text.replace('\\', '/')
                descriptions[current_test] = desc_text
            current_test = line.replace('TEST: ', '').strip()
            current_desc = []
        elif line.startswith('=' * 80):
            continue
        elif current_test:
            current_desc.append(line)
    
    if current_test:
        desc_text = '\n'.join(current_desc).strip()
        desc_text = desc_text.replace('\\', '/')
        descriptions[current_test] = desc_text
    
    return descriptions

def main():
    """Print all descriptions for manual review."""
    descriptions = parse_improved_descriptions()
    
    print(f"Parsed {len(descriptions)} improved descriptions")
    print("\nReady to update Jira using Rovo MCP tools")
    print("\nTest IDs:")
    for test_id in sorted(descriptions.keys()):
        print(f"  - {test_id}")

if __name__ == "__main__":
    main()

