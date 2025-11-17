"""
Check Tests from Jira Ticket Script
====================================

This script checks if all tests mentioned in a Jira ticket exist in the automation test suite.

Usage:
    python scripts/jira/check_tests_from_ticket.py PZ-14592
    python scripts/jira/check_tests_from_ticket.py --ticket PZ-14592 --detailed
"""

import argparse
import sys
import re
import logging
from pathlib import Path
from typing import List, Dict, Set, Optional, Any
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


def extract_test_names_from_text(text: str) -> Set[str]:
    """
    Extract test names from text.
    
    Looks for patterns like:
    - test_function_name
    - TestClassName::test_method_name
    - test_*.py file names
    - PZ-XXXXX (Xray test keys)
    
    Args:
        text: Text to search for test names
        
    Returns:
        Set of test names found
    """
    test_names = set()
    
    if not text:
        return test_names
    
    # Pattern 1: test function names (test_*)
    test_function_pattern = r'\btest_\w+\b'
    matches = re.findall(test_function_pattern, text, re.IGNORECASE)
    test_names.update(matches)
    
    # Pattern 2: Test class names (Test*)
    test_class_pattern = r'\bTest\w+\b'
    matches = re.findall(test_class_pattern, text)
    test_names.update(matches)
    
    # Pattern 3: Test file names (test_*.py)
    test_file_pattern = r'test_\w+\.py'
    matches = re.findall(test_file_pattern, text, re.IGNORECASE)
    test_names.update([m.replace('.py', '') for m in matches])
    
    # Pattern 4: Xray test keys (PZ-XXXXX)
    xray_pattern = r'PZ-\d{5,}'
    matches = re.findall(xray_pattern, text)
    test_names.update(matches)
    
    # Pattern 5: Full test paths (TestClass::test_method)
    full_test_pattern = r'\b\w+::test_\w+\b'
    matches = re.findall(full_test_pattern, text)
    test_names.update(matches)
    
    return test_names


def scan_tests_directory(tests_dir: Path) -> Dict[str, List[str]]:
    """
    Scan tests directory and extract all test functions and classes.
    
    Args:
        tests_dir: Path to tests directory
        
    Returns:
        Dictionary mapping test names to their file paths
    """
    test_map = defaultdict(list)
    
    if not tests_dir.exists():
        logger.warning(f"Tests directory not found: {tests_dir}")
        return test_map
    
    # Find all Python test files
    test_files = list(tests_dir.rglob("test_*.py"))
    logger.info(f"Found {len(test_files)} test files")
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            relative_path = test_file.relative_to(tests_dir)
            
            # Extract test functions
            test_function_pattern = r'def\s+(test_\w+)'
            functions = re.findall(test_function_pattern, content)
            for func_name in functions:
                test_map[func_name].append(str(relative_path))
            
            # Extract test classes
            test_class_pattern = r'class\s+(Test\w+)'
            classes = re.findall(test_class_pattern, content)
            for class_name in classes:
                test_map[class_name].append(str(relative_path))
            
            # Extract full test paths (Class::method)
            class_method_pattern = r'class\s+(\w+).*?def\s+(test_\w+)'
            for match in re.finditer(class_method_pattern, content, re.DOTALL):
                class_name = match.group(1)
                method_name = match.group(2)
                full_name = f"{class_name}::{method_name}"
                test_map[full_name].append(str(relative_path))
            
            # Add file name itself
            file_name = test_file.stem  # without .py extension
            test_map[file_name].append(str(relative_path))
            
        except Exception as e:
            logger.warning(f"Error reading {test_file}: {e}")
            continue
    
    return dict(test_map)


def find_xray_markers_in_tests(tests_dir: Path) -> Dict[str, List[str]]:
    """
    Find Xray test markers (PZ-XXXXX) in test files.
    
    Args:
        tests_dir: Path to tests directory
        
    Returns:
        Dictionary mapping Xray test keys to test file paths
    """
    xray_map = defaultdict(list)
    
    if not tests_dir.exists():
        return xray_map
    
    test_files = list(tests_dir.rglob("test_*.py"))
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            relative_path = test_file.relative_to(tests_dir)
            
            # Find Xray markers (@pytest.mark.xray('PZ-XXXXX') or @pytest.mark.xray("PZ-XXXXX", "PZ-YYYYY"))
            # This pattern matches single or multiple Xray keys in the marker
            xray_pattern = r"@pytest\.mark\.xray\([^)]*\)"
            xray_matches = re.findall(xray_pattern, content)
            for match in xray_matches:
                # Extract all PZ-XXXXX keys from the match
                keys = re.findall(r'(PZ-\d{5,})', match)
                for xray_key in keys:
                    xray_map[xray_key].append(str(relative_path))
            
            # Also check for Jira markers (@pytest.mark.jira('PZ-XXXXX') or multiple)
            jira_pattern = r"@pytest\.mark\.jira\([^)]*\)"
            jira_matches = re.findall(jira_pattern, content)
            for match in jira_matches:
                # Extract all PZ-XXXXX keys from the match
                keys = re.findall(r'(PZ-\d{5,})', match)
                for jira_key in keys:
                    xray_map[jira_key].append(str(relative_path))
            
        except Exception as e:
            logger.warning(f"Error reading {test_file}: {e}")
            continue
    
    return dict(xray_map)


def get_ticket_tests(client: JiraClient, ticket_key: str) -> Dict[str, Any]:
    """
    Get ticket details and extract test information.
    
    Args:
        client: JiraClient instance
        ticket_key: Jira ticket key (e.g., "PZ-14592")
        
    Returns:
        Dictionary with ticket details and extracted tests
    """
    try:
        # Get ticket with full description
        issue = client.jira.issue(ticket_key, expand='renderedFields')
        
        # Get description (both raw and rendered)
        description = getattr(issue.fields, 'description', '') or ''
        summary = issue.fields.summary
        
        # Try to get rendered description if available
        rendered_description = ''
        if hasattr(issue.renderedFields, 'description'):
            rendered_description = issue.renderedFields.description or ''
        
        # Combine all text fields
        all_text = f"{summary}\n{description}\n{rendered_description}"
        
        # Extract test names
        test_names = extract_test_names_from_text(all_text)
        
        # Extract Xray test keys
        xray_keys = set()
        xray_pattern = r'PZ-\d{5,}'
        matches = re.findall(xray_pattern, all_text)
        xray_keys.update(matches)
        
        return {
            'key': issue.key,
            'summary': summary,
            'description': description,
            'rendered_description': rendered_description,
            'test_names': test_names,
            'xray_keys': xray_keys,
            'url': f"{client.base_url}/browse/{issue.key}",
            'status': issue.fields.status.name,
            'issue_type': issue.fields.issuetype.name
        }
        
    except Exception as e:
        logger.error(f"Failed to get ticket {ticket_key}: {e}")
        raise


def check_tests_coverage(
    ticket_tests: Dict[str, Any],
    automation_tests: Dict[str, List[str]],
    xray_markers: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    Check which tests from ticket exist in automation suite.
    
    Args:
        ticket_tests: Ticket test information
        automation_tests: Dictionary of automation tests
        xray_markers: Dictionary of Xray markers in tests
        
    Returns:
        Coverage analysis results
    """
    found_tests = []
    missing_tests = []
    found_xray = []
    missing_xray = []
    
    # Check test names (exclude Xray keys - they are checked separately)
    xray_keys_set = set(ticket_tests['xray_keys'])
    
    for test_name in ticket_tests['test_names']:
        # Skip Xray keys - they are checked in the Xray keys section
        if test_name in xray_keys_set:
            continue
            
        # Check if test name exists in automation
        found = False
        locations = []
        
        # Direct match
        if test_name in automation_tests:
            found = True
            locations = automation_tests[test_name]
        else:
            # Partial match (test name contains or is contained)
            for auto_test, paths in automation_tests.items():
                if test_name.lower() in auto_test.lower() or auto_test.lower() in test_name.lower():
                    found = True
                    locations.extend(paths)
        
        if found:
            found_tests.append({
                'name': test_name,
                'locations': list(set(locations))
            })
        else:
            missing_tests.append(test_name)
    
    # Check Xray keys
    for xray_key in ticket_tests['xray_keys']:
        if xray_key in xray_markers:
            found_xray.append({
                'key': xray_key,
                'locations': xray_markers[xray_key]
            })
        else:
            missing_xray.append(xray_key)
    
    return {
        'found_tests': found_tests,
        'missing_tests': missing_tests,
        'found_xray': found_xray,
        'missing_xray': missing_xray,
        'total_tests_in_ticket': len(ticket_tests['test_names']),
        'total_xray_in_ticket': len(ticket_tests['xray_keys']),
        'found_count': len(found_tests),
        'missing_count': len(missing_tests),
        'found_xray_count': len(found_xray),
        'missing_xray_count': len(missing_xray)
    }


def print_report(
    ticket_info: Dict[str, Any],
    coverage: Dict[str, Any],
    detailed: bool = False
):
    """Print coverage report."""
    import sys
    import io
    
    # Set UTF-8 encoding for stdout to handle emojis
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("\n" + "="*100)
    print(f"TEST COVERAGE REPORT FOR TICKET: {ticket_info['key']}")
    print("="*100)
    print(f"Summary: {ticket_info['summary']}")
    print(f"Status: {ticket_info['status']}")
    print(f"Type: {ticket_info['issue_type']}")
    print(f"URL: {ticket_info['url']}")
    print("\n" + "-"*100)
    
    # Test names coverage
    print(f"\n[TEST NAMES COVERAGE]")
    print(f"   Total test names found in ticket: {coverage['total_tests_in_ticket']}")
    print(f"   [OK] Found in automation: {coverage['found_count']}")
    print(f"   [MISSING] Missing from automation: {coverage['missing_count']}")
    
    if coverage['found_tests']:
        print(f"\n   [OK] Found Tests ({len(coverage['found_tests'])}):")
        for test in coverage['found_tests']:
            print(f"      - {test['name']}")
            if detailed:
                for loc in test['locations']:
                    print(f"        -> {loc}")
    
    if coverage['missing_tests']:
        print(f"\n   [MISSING] Missing Tests ({len(coverage['missing_tests'])}):")
        for test in coverage['missing_tests']:
            print(f"      - {test}")
    
    # Xray keys coverage
    print(f"\n[XRAY TEST KEYS COVERAGE]")
    print(f"   Total Xray keys found in ticket: {coverage['total_xray_in_ticket']}")
    print(f"   [OK] Found in automation: {coverage['found_xray_count']}")
    print(f"   [MISSING] Missing from automation: {coverage['missing_xray_count']}")
    
    if coverage['found_xray']:
        print(f"\n   [OK] Found Xray Keys ({len(coverage['found_xray'])}):")
        for xray in coverage['found_xray']:
            print(f"      - {xray['key']}")
            if detailed:
                for loc in xray['locations']:
                    print(f"        -> {loc}")
    
    if coverage['missing_xray']:
        print(f"\n   [MISSING] Missing Xray Keys ({len(coverage['missing_xray'])}):")
        for xray_key in coverage['missing_xray']:
            print(f"      - {xray_key}")
    
    # Summary
    print("\n" + "="*100)
    
    # Calculate coverage - Xray keys are the most important metric
    xray_coverage_percent = 0
    if coverage['total_xray_in_ticket'] > 0:
        xray_coverage_percent = (coverage['found_xray_count'] / coverage['total_xray_in_ticket']) * 100
    
    # Overall coverage (test names + Xray keys, but Xray keys are primary)
    total_items = coverage['total_tests_in_ticket'] + coverage['total_xray_in_ticket']
    found_items = coverage['found_count'] + coverage['found_xray_count']
    
    print(f"COVERAGE SUMMARY:")
    print(f"   Xray Keys Coverage: {coverage['found_xray_count']}/{coverage['total_xray_in_ticket']} ({xray_coverage_percent:.1f}%)")
    if coverage['total_tests_in_ticket'] > 0:
        test_names_coverage_percent = (coverage['found_count'] / coverage['total_tests_in_ticket']) * 100
        print(f"   Test Names Coverage: {coverage['found_count']}/{coverage['total_tests_in_ticket']} ({test_names_coverage_percent:.1f}%)")
    
    if coverage['total_xray_in_ticket'] > 0:
        if coverage['found_xray_count'] == coverage['total_xray_in_ticket']:
            print(f"\n   [SUCCESS] All Xray test keys are implemented in automation!")
        else:
            print(f"\n   [WARNING] {coverage['missing_xray_count']} Xray test key(s) missing from automation")
    
    print("="*100 + "\n")
    
    if detailed and ticket_info['description']:
        print("\n[TICKET DESCRIPTION]")
        print("-"*100)
        print(ticket_info['description'][:1000])  # First 1000 chars
        if len(ticket_info['description']) > 1000:
            print("... (truncated)")
        print("-"*100 + "\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Check if tests from Jira ticket exist in automation suite"
    )
    parser.add_argument(
        'ticket_key',
        nargs='?',
        help='Jira ticket key (e.g., PZ-14592)'
    )
    parser.add_argument(
        '--ticket', '-t',
        dest='ticket_key_opt',
        help='Jira ticket key (alternative)'
    )
    parser.add_argument(
        '--detailed', '-d',
        action='store_true',
        help='Show detailed report with file locations'
    )
    parser.add_argument(
        '--tests-dir',
        type=Path,
        default=project_root / 'tests',
        help='Path to tests directory (default: tests/)'
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=project_root / 'config' / 'jira_config.yaml',
        help='Path to Jira config file'
    )
    
    args = parser.parse_args()
    
    # Get ticket key
    ticket_key = args.ticket_key or args.ticket_key_opt
    if not ticket_key:
        parser.error("Ticket key is required (provide as argument or --ticket)")
    
    try:
        # Initialize Jira client
        logger.info(f"Connecting to Jira...")
        client = JiraClient(config_path=args.config)
        
        # Get ticket information
        logger.info(f"Fetching ticket {ticket_key}...")
        ticket_info = get_ticket_tests(client, ticket_key)
        
        # Scan automation tests
        logger.info(f"Scanning automation tests in {args.tests_dir}...")
        automation_tests = scan_tests_directory(args.tests_dir)
        logger.info(f"Found {len(automation_tests)} unique test identifiers")
        
        # Find Xray markers
        logger.info("Scanning for Xray markers...")
        xray_markers = find_xray_markers_in_tests(args.tests_dir)
        logger.info(f"Found {len(xray_markers)} Xray test keys in automation")
        
        # Check coverage
        logger.info("Analyzing coverage...")
        coverage = check_tests_coverage(ticket_info, automation_tests, xray_markers)
        
        # Print report
        print_report(ticket_info, coverage, detailed=args.detailed)
        
        # Return exit code based on coverage
        # Xray keys are the primary metric - if all Xray keys are found, return success
        if coverage['missing_xray_count'] > 0:
            return 1  # Missing Xray keys - this is critical
        # If all Xray keys are found, return success even if some test names are missing
        # (test names are less critical than Xray keys)
        return 0  # All Xray keys found
        
    except Exception as e:
        logger.error(f"Failed to check tests: {e}")
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

