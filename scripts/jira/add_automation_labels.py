"""
Add Automation Labels to Jira Tests
====================================

Script to add automation labels to Jira tests based on automation code coverage.

This script:
1. Scans automation code for Xray/Jira markers
2. Identifies tests written by Roy (Reporter/Creator/Assignee)
3. Adds labels:
   - "For_Automation" for tests with markers (covered by automation)
   - "Automated" for tests that are actually implemented (have test functions)

Usage:
    python scripts/jira/add_automation_labels.py --dry-run
    python scripts/jira/add_automation_labels.py --update
"""

import argparse
import sys
import re
import logging
from pathlib import Path
from typing import List, Dict, Set, Optional
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


def find_xray_markers_in_code() -> Dict[str, Dict[str, any]]:
    """
    Scan automation code for Xray/Jira markers.
    
    Returns:
        Dictionary mapping test keys to their marker information
    """
    logger.info("Scanning automation code for Xray/Jira markers...")
    
    markers = {}
    test_files = []
    
    # Find all Python test files
    for test_file in Path('tests').rglob('*.py'):
        if test_file.name.startswith('test_') or 'conftest' in test_file.name:
            test_files.append(test_file)
    
    logger.info(f"Scanning {len(test_files)} test files...")
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            
            # Find all @pytest.mark.xray("PZ-XXXXX") patterns
            xray_matches = re.findall(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)', content)
            for match in xray_matches:
                # Handle multiple IDs in one marker: "PZ-1234", "PZ-5678"
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        if test_id not in markers:
                            markers[test_id] = {
                                'file': str(test_file),
                                'type': 'xray',
                                'has_test_function': False
                            }
                        else:
                            # Multiple markers for same test
                            markers[test_id]['file'] += f", {test_file.name}"
            
            # Find all @pytest.mark.jira("PZ-XXXXX") patterns
            jira_matches = re.findall(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)', content)
            for match in jira_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        if test_id not in markers:
                            markers[test_id] = {
                                'file': str(test_file),
                                'type': 'jira',
                                'has_test_function': False
                            }
                        else:
                            markers[test_id]['file'] += f", {test_file.name}"
            
            # Check if markers are associated with actual test functions
            # We'll check this later when we find the test functions
            
        except Exception as e:
            logger.warning(f"Failed to read {test_file}: {e}")
            continue
    
    logger.info(f"Found {len(markers)} unique test IDs with markers")
    
    # Mark tests that have test functions (markers with actual test functions)
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Find test functions that have markers
            for i, line in enumerate(lines):
                # Check for markers on the same line or previous lines (decorators)
                if '@pytest.mark.xray' in line or '@pytest.mark.jira' in line:
                    # Look for test function in next few lines (decorator pattern)
                    for j in range(i+1, min(i+10, len(lines))):
                        next_line = lines[j].strip()
                        # Skip empty lines and comments
                        if not next_line or next_line.startswith('#'):
                            continue
                        # Check if it's a test function
                        if re.match(r'^\s*def\s+test_\w+', next_line):
                            # Extract test IDs from marker line
                            xray_ids = re.findall(r'["\'](PZ-\d+)["\']', line)
                            jira_ids = re.findall(r'["\'](PZ-\d+)["\']', line)
                            all_ids = xray_ids + jira_ids
                            for test_id in all_ids:
                                if test_id in markers:
                                    markers[test_id]['has_test_function'] = True
                            break
        except Exception as e:
            logger.warning(f"Failed to check test functions in {test_file}: {e}")
            continue
    
    return markers


def get_all_tests(client: JiraClient, project_key: str = "PZ", filter_by_roy: bool = False) -> Dict[str, Dict]:
    """
    Get all tests from project (optionally filtered by Roy).
    
    Args:
        client: JiraClient instance
        project_key: Project key
        filter_by_roy: If True, only get tests by Roy
        
    Returns:
        Dictionary mapping test keys to test information
    """
    if filter_by_roy:
        logger.info("Fetching tests written by Roy...")
        # Search for tests where Roy is reporter, creator, or assignee
        jql = (
            f'project = {project_key} AND issuetype = Test AND '
            f'(reporter = "Roy Avrahami" OR creator = "Roy Avrahami" OR assignee = "Roy Avrahami")'
        )
    else:
        logger.info("Fetching ALL tests from project...")
        jql = f'project = {project_key} AND issuetype = Test'
    
    try:
        tests = client.search_issues(jql=jql, max_results=None)
        
        # Convert to dictionary
        tests_dict = {}
        for test in tests:
            key = test.get('key')
            if key:
                tests_dict[key] = test
        
        logger.info(f"Found {len(tests_dict)} tests")
        return tests_dict
        
    except Exception as e:
        logger.error(f"Failed to fetch tests: {e}")
        raise


def update_test_labels(
    client: JiraClient,
    test_key: str,
    labels_to_add: List[str],
    dry_run: bool = False
) -> bool:
    """
    Update test labels in Jira.
    
    Args:
        client: JiraClient instance
        test_key: Test issue key
        labels_to_add: List of labels to add
        dry_run: If True, don't actually update
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get current issue
        issue = client.jira.issue(test_key)
        current_labels = list(issue.fields.labels) if issue.fields.labels else []
        
        # Add new labels (avoid duplicates)
        new_labels = list(set(current_labels + labels_to_add))
        
        if set(current_labels) == set(new_labels):
            logger.debug(f"Test {test_key} already has all labels: {current_labels}")
            return True
        
        if dry_run:
            logger.info(f"[DRY RUN] Would update {test_key}: {current_labels} -> {new_labels}")
            return True
        
        # Update issue using client's update_issue method
        client.update_issue(issue_key=test_key, labels=new_labels)
        logger.info(f"Updated {test_key}: {current_labels} -> {new_labels}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update {test_key}: {e}")
        return False


def main():
    """Main function for adding automation labels."""
    parser = argparse.ArgumentParser(
        description='Add automation labels to Jira tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (see what would be updated)
  python add_automation_labels.py --dry-run
  
  # Actually update labels
  python add_automation_labels.py --update
  
  # Update specific test
  python add_automation_labels.py --update --test PZ-12345
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (don\'t actually update Jira)'
    )
    
    parser.add_argument(
        '--update',
        action='store_true',
        help='Actually update labels in Jira'
    )
    
    parser.add_argument(
        '--test',
        help='Update specific test key only'
    )
    
    parser.add_argument(
        '--all-tests',
        action='store_true',
        help='Update all tests with markers, not just Roy\'s tests'
    )
    
    parser.add_argument(
        '--project',
        '--project-key',
        dest='project_key',
        default='PZ',
        help='Project key (default: PZ)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to jira_config.yaml (optional)'
    )
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.update:
        print("❌ Must specify either --dry-run or --update")
        return 1
    
    try:
        # Initialize Jira client
        client = JiraClient(config_path=args.config)
        
        # Find markers in code
        markers = find_xray_markers_in_code()
        
        if not markers:
            print("❌ No markers found in automation code")
            return 1
        
        logger.info(f"Found {len(markers)} unique test IDs with markers in automation code")
        
        # Get all tests (or just Roy's if filter_by_roy is True)
        all_tests = get_all_tests(
            client, 
            project_key=args.project_key, 
            filter_by_roy=not args.all_tests
        )
        
        if not all_tests:
            print("❌ No tests found")
            return 1
        
        # Filter to tests that have markers
        tests_to_update = {}
        for test_key in markers:
            if test_key in all_tests:
                tests_to_update[test_key] = {
                    'test_info': all_tests[test_key],
                    'marker_info': markers[test_key]
                }
        
        filter_msg = "Roy's" if not args.all_tests else "all"
        logger.info(f"Found {len(tests_to_update)} {filter_msg} tests with automation markers")
        
        # Determine which label to add
        # Tests with markers = "For_Automation" (covered by automation)
        # Tests with markers + test functions = "Automated" (actually implemented)
        for_automation = []
        automated = []
        
        for test_key, info in tests_to_update.items():
            marker_info = info['marker_info']
            
            if args.test and test_key != args.test:
                continue
            
            # If has test function, it's "Automated" (actually implemented)
            # Otherwise, it's "For_Automation" (covered but not fully implemented)
            if marker_info.get('has_test_function', False):
                automated.append(test_key)
            else:
                for_automation.append(test_key)
        
        # Update labels
        dry_run = args.dry_run
        updated_count = 0
        failed_count = 0
        
        print("\n" + "="*80)
        print("Automation Labels Update Summary")
        print("="*80)
        print(f"\nTests with 'For_Automation' label: {len(for_automation)}")
        print(f"Tests with 'Automated' label: {len(automated)}")
        print(f"Mode: {'DRY RUN' if dry_run else 'UPDATE'}")
        print("\n" + "="*80 + "\n")
        
        # Update "For_Automation" labels
        for test_key in for_automation:
            if update_test_labels(client, test_key, ['For_Automation'], dry_run=dry_run):
                updated_count += 1
            else:
                failed_count += 1
        
        # Update "Automated" labels
        for test_key in automated:
            if update_test_labels(client, test_key, ['Automated'], dry_run=dry_run):
                updated_count += 1
            else:
                failed_count += 1
        
        print("\n" + "="*80)
        print("Update Summary")
        print("="*80)
        print(f"Updated: {updated_count}")
        print(f"Failed: {failed_count}")
        print(f"Total: {len(for_automation) + len(automated)}")
        print("="*80)
        
        if dry_run:
            print("\nThis was a DRY RUN. Use --update to actually update labels.")
        
        return 0 if failed_count == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed to add automation labels: {e}", exc_info=True)
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    finally:
        try:
            client.close()
        except:
            pass


if __name__ == '__main__':
    sys.exit(main())

