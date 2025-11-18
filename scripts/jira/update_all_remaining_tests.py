"""
Update all remaining Alert Generation Xray test cases in Jira.
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

# Already updated: PZ-14933, PZ-14934, PZ-14938
already_updated = {'PZ-14933', 'PZ-14934', 'PZ-14938'}

# Remaining tests to update
remaining_tests = sorted([tid for tid in all_descriptions.keys() if tid not in already_updated])

print(f"Total tests: {len(all_descriptions)}")
print(f"Already updated: {len(already_updated)}")
print(f"Remaining to update: {len(remaining_tests)}")
print(f"\nRemaining tests: {', '.join(remaining_tests)}")

# Print descriptions for manual update (skip emoji to avoid encoding issues)
for test_id in remaining_tests:
    desc = all_descriptions[test_id].replace('✅', '[OK]')
    print(f"\n{'='*80}")
    print(f"TEST: {test_id}")
    print(f"{'='*80}")
    print(desc)
    print()

