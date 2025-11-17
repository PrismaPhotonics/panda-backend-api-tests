"""
Update Test Quality in Jira
===========================

Script to automatically update test quality in Jira by:
1. Finding tests with short descriptions or missing details
2. Updating them with comprehensive descriptions from automation code
3. Adding test type, steps, expected results, and automation links

Usage:
    python scripts/jira/update_test_quality_jira.py
    python scripts/jira/update_test_quality_jira.py --test-id PZ-13762
    python scripts/jira/update_test_quality_jira.py --limit 10
"""

import sys
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

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


@dataclass
class TestInfo:
    """Test information from automation code."""
    test_id: str
    file_path: str
    class_name: Optional[str]
    function_name: str
    description: str
    steps: List[str]
    expected: List[str]
    priority: str = "Medium"


def find_test_in_code(test_id: str) -> Optional[TestInfo]:
    """
    Find test function in code by Xray marker.
    
    Args:
        test_id: Jira test ID (e.g., "PZ-13762")
        
    Returns:
        TestInfo if found, None otherwise
    """
    tests_dir = project_root / "tests"
    xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
    
    for test_file in tests_dir.rglob("test_*.py"):
        try:
            content = test_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Find all test functions with this marker
            for i, line in enumerate(lines):
                marker_match = xray_pattern.search(line)
                if marker_match and test_id in marker_match.group(1).split(','):
                    # Found marker, now find the function
                    func_match = re.search(r'def\s+(test_\w+)', content[i:])
                    if func_match:
                        func_name = func_match.group(1)
                        
                        # Find class if exists
                        class_match = re.search(r'class\s+(\w+).*:', content[:i])
                        class_name = class_match.group(1) if class_match else None
                        
                        # Extract docstring
                        docstring = extract_docstring(content, i)
                        description, steps, expected = parse_docstring(docstring)
                        
                        return TestInfo(
                            test_id=test_id,
                            file_path=str(test_file.relative_to(project_root)),
                            class_name=class_name,
                            function_name=func_name,
                            description=description,
                            steps=steps,
                            expected=expected
                        )
        except Exception as e:
            logger.debug(f"Error reading {test_file}: {e}")
            continue
    
    return None


def extract_docstring(content: str, marker_line: int) -> str:
    """Extract docstring from test function."""
    lines = content.split('\n')
    docstring_lines = []
    in_docstring = False
    
    # Find function definition after marker
    for i in range(marker_line, min(marker_line + 50, len(lines))):
        line = lines[i]
        
        # Start of docstring
        if '"""' in line or "'''" in line:
            quote = '"""' if '"""' in line else "'''"
            if line.count(quote) == 2:
                # Single line docstring
                docstring = line.split(quote)[1]
                return docstring
            else:
                # Multi-line docstring
                in_docstring = True
                start_idx = line.find(quote) + 3
                docstring_lines.append(line[start_idx:])
                continue
        
        if in_docstring:
            if '"""' in line or "'''" in line:
                # End of docstring
                end_idx = line.find('"""' if '"""' in line else "'''")
                docstring_lines.append(line[:end_idx])
                break
            docstring_lines.append(line)
    
    return '\n'.join(docstring_lines)


def parse_docstring(docstring: str) -> Tuple[str, List[str], List[str]]:
    """Parse docstring to extract description, steps, and expected results."""
    if not docstring:
        return "", [], []
    
    description = ""
    steps = []
    expected = []
    
    lines = docstring.split('\n')
    current_section = "description"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect sections
        if re.match(r'^(Steps|Test Steps|Steps:)$', line, re.I):
            current_section = "steps"
            continue
        elif re.match(r'^(Expected|Expected Results|Expected:)$', line, re.I):
            current_section = "expected"
            continue
        elif re.match(r'^(Objective|Description|Summary):?$', line, re.I):
            current_section = "description"
            continue
        
        # Parse content
        if current_section == "description":
            if not description:
                description = line
            else:
                description += " " + line
        elif current_section == "steps":
            # Extract step number and content
            step_match = re.match(r'^\d+[\.\)]\s*(.+)', line)
            if step_match:
                steps.append(step_match.group(1))
            elif line.startswith('-') or line.startswith('*'):
                steps.append(line[1:].strip())
        elif current_section == "expected":
            if line.startswith('-') or line.startswith('*'):
                expected.append(line[1:].strip())
            else:
                expected.append(line)
    
    return description, steps, expected


def build_jira_description(test_info: TestInfo) -> str:
    """
    Build comprehensive Jira description from test info.
    
    Args:
        test_info: Test information from code
        
    Returns:
        Jira markup formatted description
    """
    description = f"h2. Objective\n{test_info.description or 'Test objective'}\n\n"
    
    # Pre-Conditions
    description += "h2. Pre-Conditions\n"
    description += "* Focus Server is running\n"
    description += "* Environment is accessible\n"
    description += "* Test data is available\n\n"
    
    # Test Steps
    if test_info.steps:
        description += "h2. Test Steps\n"
        description += "|| # || Action || Data || Expected Result ||\n"
        for i, step in enumerate(test_info.steps, 1):
            description += f"| {i} | {step} | - | See Expected Results |\n"
        description += "\n"
    
    # Expected Results
    if test_info.expected:
        description += "h2. Expected Results\n"
        for expected_item in test_info.expected:
            description += f"* {expected_item}\n"
        description += "\n"
    
    # Automation Status
    description += "h2. Automation Status\n"
    description += "*Automated* with Pytest\n\n"
    
    # Test Details
    description += "*Test File:* {{code}}" + test_info.file_path + "{{code}}\n"
    if test_info.class_name:
        description += f"*Test Class:* {{code}}{test_info.class_name}{{code}}\n"
    description += f"*Test Function:* {{code}}{test_info.function_name}{{code}}\n\n"
    
    # Execution Command
    test_path = test_info.file_path.replace('\\', '/').replace('.py', '')
    if test_info.class_name:
        exec_cmd = f"pytest {test_path}::{test_info.class_name}::{test_info.function_name} -v"
    else:
        exec_cmd = f"pytest {test_path}::{test_info.function_name} -v"
    description += f"*Execution Command:*\n{{code}}{exec_cmd}{{code}}\n"
    
    return description


def determine_test_type(file_path: str) -> str:
    """
    Determine test type based on file path.
    
    Args:
        file_path: Path to test file
        
    Returns:
        Test type string (e.g., "Integration Test", "Unit Test", etc.)
    """
    file_path_lower = file_path.lower()
    
    if 'unit' in file_path_lower:
        return "Unit Test"
    elif 'integration' in file_path_lower:
        return "Integration Test"
    elif 'performance' in file_path_lower:
        return "Performance Test"
    elif 'load' in file_path_lower:
        return "Load Test"
    elif 'security' in file_path_lower:
        return "Security Test"
    elif 'e2e' in file_path_lower or 'end_to_end' in file_path_lower:
        return "E2E Test"
    elif 'infrastructure' in file_path_lower:
        return "Infrastructure Test"
    elif 'data_quality' in file_path_lower:
        return "Data Quality Test"
    else:
        return "Integration Test"  # Default


def update_test_quality(client: JiraClient, test_id: str, dry_run: bool = False, force: bool = False) -> bool:
    """
    Update test quality in Jira.
    
    Args:
        client: Jira client instance
        test_id: Test ID to update
        dry_run: If True, only print what would be updated
        force: If True, update even if description is long
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get test from Jira
        issue = client.get_issue(test_id)
        current_description = issue.get('description', '')
        
        # Check if description is too short or missing, or if force update
        needs_update = force or not current_description or len(current_description) < 200
        
        # Find test in code
        test_info = find_test_in_code(test_id)
        if not test_info:
            logger.warning(f"Test {test_id} not found in automation code")
            return False
        
        # Build new description (always build to ensure automation links are present)
        new_description = build_jira_description(test_info)
        
        # Check if update is needed (only description, not Test Type)
        # Note: Test Type field in Jira only accepts "Automation", so we don't update it
        description_needs_update = needs_update or "Automation Status" not in current_description
        
        if not description_needs_update and not force:
            logger.info(f"Test {test_id} already has good quality (Description: {len(current_description)} chars)")
            return True
        
        if dry_run:
            logger.info(f"[DRY RUN] Would update {test_id}:")
            logger.info(f"  Current description length: {len(current_description)}")
            logger.info(f"  New description length: {len(new_description)}")
            logger.info(f"  File: {test_info.file_path}")
            logger.info(f"  Note: Test Type will not be updated (Jira only accepts 'Automation')")
            return True
        
        # Update issue - only update description, not Test Type
        # Jira doesn't require Test Type when updating description if it's already set
        if description_needs_update:
            # Get Jira issue object directly
            jira_issue = client.jira.issue(test_id)
            # Only update description - don't touch Test Type
            jira_issue.update(fields={'description': new_description})
            logger.info(f"Updated description for {test_id}")
        
        # Get updated issue
        updated_issue = client.get_issue(test_id)
        
        logger.info(f"[OK] Updated {test_id}: {updated_issue['summary']}")
        if description_needs_update:
            logger.info(f"   Description: {len(current_description)} -> {len(new_description)} chars")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update {test_id}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def find_tests_needing_update(client: JiraClient, limit: Optional[int] = None, from_code: bool = True) -> List[str]:
    """
    Find tests that need quality updates.
    
    Args:
        client: Jira client instance
        limit: Maximum number of tests to return
        from_code: If True, find tests from code markers instead of Jira search
        
    Returns:
        List of test IDs that need updates
    """
    if from_code:
        # Find tests from code markers
        tests_dir = project_root / "tests"
        xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
        test_ids = set()
        
        for test_file in tests_dir.rglob("test_*.py"):
            try:
                content = test_file.read_text(encoding='utf-8')
                for match in xray_pattern.finditer(content):
                    marker_content = match.group(1)
                    # Extract all test IDs from marker
                    ids = [tid.strip().strip('"\'') for tid in marker_content.split(',')]
                    test_ids.update(ids)
            except Exception as e:
                logger.debug(f"Error reading {test_file}: {e}")
                continue
        
        return list(test_ids)[:limit] if limit else list(test_ids)
    else:
        # Search for Test issues with short descriptions
        jql = 'project = PZ AND issuetype = Test AND status != Done'
        tests = client.search_issues(jql, max_results=limit or 100)
        
        tests_needing_update = []
        for test in tests:
            description = test.get('description', '')
            if not description or len(description) < 200:
                tests_needing_update.append(test['key'])
        
        return tests_needing_update


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Update test quality in Jira',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--test-id',
        help='Specific test ID to update (e.g., PZ-13762)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Maximum number of tests to update'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run - show what would be updated without making changes'
    )
    
    parser.add_argument(
        '--config',
        help='Path to jira_config.yaml (optional)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force update even if description is long'
    )
    
    parser.add_argument(
        '--from-code',
        action='store_true',
        default=True,
        help='Find tests from code markers (default: True)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize Jira client
        client = JiraClient(config_path=args.config)
        
        if args.test_id:
            # Update specific test
            logger.info(f"Updating test: {args.test_id}")
            success = update_test_quality(client, args.test_id, dry_run=args.dry_run, force=args.force)
            return 0 if success else 1
        else:
            # Find and update all tests needing updates
            logger.info("Finding tests that need quality updates...")
            test_ids = find_tests_needing_update(client, limit=args.limit, from_code=args.from_code)
            
            logger.info(f"Found {len(test_ids)} tests to check")
            
            if not test_ids:
                logger.info("No tests found")
                return 0
            
            # Update each test
            updated = 0
            failed = 0
            skipped = 0
            
            for test_id in test_ids:
                result = update_test_quality(client, test_id, dry_run=args.dry_run, force=args.force)
                if result:
                    updated += 1
                else:
                    # Check if it was skipped (already good quality)
                    try:
                        issue = client.get_issue(test_id)
                        if issue.get('description', '') and len(issue.get('description', '')) > 200:
                            skipped += 1
                        else:
                            failed += 1
                    except:
                        failed += 1
            
            logger.info(f"\n[OK] Updated: {updated}")
            logger.info(f"[SKIP] Skipped (already good): {skipped}")
            logger.info(f"[FAIL] Failed: {failed}")
            logger.info(f"[TOTAL] Total: {len(test_ids)}")
            
            return 0
            
    except Exception as e:
        logger.error(f"Failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

