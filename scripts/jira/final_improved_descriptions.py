"""
Create final improved descriptions with actual values from code.
Then update all Jira test cases using Rovo MCP.
"""

import re
from pathlib import Path

project_root = Path(__file__).parent.parent.parent

# Read improved descriptions and fix paths
desc_file = project_root / 'scripts/jira/improved_test_descriptions.txt'
content = desc_file.read_text(encoding='utf-8')

# Fix backslashes in paths
content = content.replace('\\', '/')

# Parse descriptions
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

print(f"Parsed {len(descriptions)} descriptions")
print("Ready to update Jira")

# Save fixed descriptions
output_file = project_root / 'scripts/jira/final_improved_descriptions.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    for test_id, desc in sorted(descriptions.items()):
        f.write(f"\n{'='*80}\n")
        f.write(f"TEST: {test_id}\n")
        f.write(f"{'='*80}\n\n")
        f.write(desc)
        f.write("\n\n")

print(f"Saved fixed descriptions to {output_file}")

