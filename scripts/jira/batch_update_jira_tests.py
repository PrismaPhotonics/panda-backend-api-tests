"""
Batch update all Alert Generation Xray test cases in Jira.
Reads descriptions from alert_tests_descriptions.txt and updates Jira.
"""

import re
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
desc_file = project_root / 'scripts/jira/alert_tests_descriptions.txt'

def parse_descriptions():
    """Parse descriptions file."""
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

# Parse all descriptions
all_descriptions = parse_descriptions()
print(f"Loaded {len(all_descriptions)} test descriptions")

# Now update each test in Jira
# This will be done via MCP tools

