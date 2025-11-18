"""
Script to update all Alert Generation Xray test cases in Jira
using the generated descriptions.

Usage:
    python scripts/jira/update_jira_alert_tests.py
    python scripts/jira/update_jira_alert_tests.py --test-ids PZ-14933,PZ-14934
"""

import sys
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def parse_descriptions_file(file_path: Path) -> dict:
    """Parse the descriptions file and return dict of test_id -> description."""
    content = file_path.read_text(encoding='utf-8')
    
    descriptions = {}
    current_test = None
    current_desc = []
    
    for line in content.split('\n'):
        if line.startswith('TEST: PZ-'):
            # Save previous test if exists
            if current_test:
                descriptions[current_test] = '\n'.join(current_desc).strip()
            
            # Start new test
            current_test = line.replace('TEST: ', '').strip()
            current_desc = []
        elif line.startswith('=' * 80):
            continue
        elif current_test:
            current_desc.append(line)
    
    # Save last test
    if current_test:
        descriptions[current_test] = '\n'.join(current_desc).strip()
    
    return descriptions


def main():
    """Update Jira test cases."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Update Alert Generation Xray test cases')
    parser.add_argument('--test-ids', help='Comma-separated list of test IDs to update')
    parser.add_argument('--dry-run', action='store_true', help='Preview without updating')
    args = parser.parse_args()
    
    # Load descriptions
    desc_file = project_root / 'scripts/jira/alert_tests_descriptions.txt'
    if not desc_file.exists():
        print(f"ERROR: Descriptions file not found: {desc_file}")
        return
    
    descriptions = parse_descriptions_file(desc_file)
    print(f"Loaded {len(descriptions)} test descriptions")
    
    # Filter test IDs if specified
    if args.test_ids:
        test_ids = [tid.strip() for tid in args.test_ids.split(',')]
        descriptions = {tid: descriptions[tid] for tid in test_ids if tid in descriptions}
    
    print("\n" + "=" * 80)
    print("Jira Update Instructions")
    print("=" * 80)
    print("\nUse the following MCP tool calls to update each test:")
    print("\nExample for PZ-14933:")
    print("-" * 80)
    
    # Show first test as example
    if descriptions:
        first_test = list(descriptions.keys())[0]
        first_desc = descriptions[first_test]
        print(f"\nTest ID: {first_test}")
        print(f"Description length: {len(first_desc)} chars")
        print(f"\nDescription preview (first 300 chars):")
        print(first_desc[:300] + "...")
    
    print("\n" + "=" * 80)
    print(f"Total tests to update: {len(descriptions)}")
    print("=" * 80)
    
    if args.dry_run:
        print("\n[DRY RUN] Would update the following tests:")
        for test_id in sorted(descriptions.keys()):
            print(f"  - {test_id}")
        print("\nRun without --dry-run to see update instructions")
    else:
        print("\nTo update tests, use MCP tool: mcp_atlassian-rovo_editJiraIssue")
        print("with cloudId='a8cc7b3d-f5fd-41a1-a7ca-b9fc4ddfe0b4'")
        print("and fields={'description': '<description_text>'}")


if __name__ == "__main__":
    main()

