"""
Add Automation Labels from CSV Tests
=====================================

Script to add automation labels to tests from CSV files based on automation code coverage.
"""

import re
import sys
import csv
import logging
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_all_markers():
    """Find all Xray/Jira markers in automation code."""
    markers = set()
    markers_with_functions = set()
    
    # Find all Python test files
    for test_file in Path('tests').rglob('*.py'):
        if test_file.name.startswith('test_') or 'conftest' in test_file.name:
            try:
                content = test_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                # Find all @pytest.mark.xray("PZ-XXXXX") patterns
                for i, line in enumerate(lines):
                    if '@pytest.mark.xray' in line or '@pytest.mark.jira' in line:
                        # Extract test IDs
                        xray_ids = re.findall(r'["\'](PZ-\d+)["\']', line)
                        jira_ids = re.findall(r'["\'](PZ-\d+)["\']', line)
                        all_ids = xray_ids + jira_ids
                        
                        # Check if there's a test function after this marker
                        has_function = False
                        for j in range(i+1, min(i+10, len(lines))):
                            next_line = lines[j].strip()
                            if not next_line or next_line.startswith('#'):
                                continue
                            if re.match(r'^\s*def\s+test_\w+', next_line):
                                has_function = True
                                break
                        
                        for test_id in all_ids:
                            markers.add(test_id)
                            if has_function:
                                markers_with_functions.add(test_id)
                                
            except Exception as e:
                logger.warning(f"Failed to read {test_file}: {e}")
                continue
    
    return markers, markers_with_functions


def read_csv_tests(csv_files: List[Path]) -> Dict[str, Dict]:
    """Read all tests from CSV files."""
    all_tests = {}
    
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = row.get('Issue key', '').strip()
                    if key and key.startswith('PZ-'):
                        all_tests[key] = row
        except Exception as e:
            logger.error(f"Failed to read {csv_file}: {e}")
    
    return all_tests


def update_test_labels(client: JiraClient, test_key: str, labels_to_add: List[str]) -> bool:
    """Update test labels in Jira."""
    try:
        issue = client.jira.issue(test_key)
        current_labels = list(issue.fields.labels) if issue.fields.labels else []
        new_labels = list(set(current_labels + labels_to_add))
        
        if set(current_labels) == set(new_labels):
            return True
        
        client.update_issue(issue_key=test_key, labels=new_labels)
        logger.info(f"Updated {test_key}: added {labels_to_add}")
        return True
    except Exception as e:
        logger.error(f"Failed to update {test_key}: {e}")
        return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Add automation labels from CSV tests')
    parser.add_argument('--csv-files', required=True, help='Comma-separated CSV file paths')
    parser.add_argument('--update', action='store_true', help='Actually update Jira')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    if not args.update and not args.dry_run:
        print("Must specify either --update or --dry-run")
        return 1
    
    # Find all markers
    print("Scanning automation code for markers...")
    all_markers, markers_with_functions = find_all_markers()
    print(f"Found {len(all_markers)} unique test IDs with markers")
    print(f"Found {len(markers_with_functions)} with test functions\n")
    
    # Read CSV files
    csv_paths = [Path(f.strip()) for f in args.csv_files.split(',')]
    print(f"Reading {len(csv_paths)} CSV files...")
    csv_tests = read_csv_tests(csv_paths)
    print(f"Found {len(csv_tests)} tests in CSV files\n")
    
    # Find tests from CSV that have markers
    tests_to_update = {}
    for test_key in csv_tests:
        if test_key in all_markers:
            if test_key in markers_with_functions:
                tests_to_update[test_key] = ['Automated']
            else:
                tests_to_update[test_key] = ['For_Automation']
    
    print(f"Found {len(tests_to_update)} tests from CSV with automation markers")
    print(f"  - For_Automation: {len([t for t in tests_to_update.values() if 'For_Automation' in t])}")
    print(f"  - Automated: {len([t for t in tests_to_update.values() if 'Automated' in t])}")
    print()
    
    if args.dry_run:
        print("DRY RUN - Would update:")
        for test_key, labels in sorted(tests_to_update.items()):
            print(f"  {test_key}: {', '.join(labels)}")
        return 0
    
    # Update Jira
    client = JiraClient()
    updated = 0
    failed = 0
    
    for test_key, labels in tests_to_update.items():
        if update_test_labels(client, test_key, labels):
            updated += 1
        else:
            failed += 1
    
    print(f"\nUpdated: {updated}, Failed: {failed}")
    client.close()
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

