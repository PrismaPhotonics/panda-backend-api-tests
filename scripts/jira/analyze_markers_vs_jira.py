"""
Analyze Markers vs Jira Tests
==============================

Script to compare automation markers with Jira tests and identify gaps.
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient


def find_all_markers():
    """Find all Xray/Jira markers in automation code."""
    markers = set()
    test_files = []
    
    # Find all Python test files
    for test_file in Path('tests').rglob('*.py'):
        if test_file.name.startswith('test_') or 'conftest' in test_file.name:
            test_files.append(test_file)
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            
            # Find all @pytest.mark.xray("PZ-XXXXX") patterns
            xray_matches = re.findall(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)', content)
            for match in xray_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        markers.add(test_id)
            
            # Find all @pytest.mark.jira("PZ-XXXXX") patterns
            jira_matches = re.findall(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)', content)
            for match in jira_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        markers.add(test_id)
            
        except Exception as e:
            continue
    
    return markers


def main():
    """Main function."""
    print("="*80)
    print("Analyzing Markers vs Jira Tests")
    print("="*80)
    print()
    
    # Find all markers in code
    print("1. Scanning automation code for markers...")
    markers_in_code = find_all_markers()
    print(f"   Found {len(markers_in_code)} unique test IDs with markers in code")
    print()
    
    # Get all tests from Jira
    print("2. Fetching all tests from Jira...")
    client = JiraClient()
    all_tests = client.search_issues(
        jql='project = PZ AND issuetype = Test',
        max_results=None
    )
    all_test_keys = {test['key'] for test in all_tests if test.get('key')}
    print(f"   Found {len(all_test_keys)} tests in Jira")
    print()
    
    # Compare
    print("3. Comparing markers with Jira tests...")
    markers_with_jira_test = markers_in_code & all_test_keys
    markers_without_jira_test = markers_in_code - all_test_keys
    jira_tests_without_markers = all_test_keys - markers_in_code
    
    print(f"   Markers with Jira test: {len(markers_with_jira_test)}")
    print(f"   Markers without Jira test: {len(markers_without_jira_test)}")
    print(f"   Jira tests without markers: {len(jira_tests_without_markers)}")
    print()
    
    # Show markers without Jira test
    if markers_without_jira_test:
        print("="*80)
        print("Markers in Code WITHOUT Jira Test:")
        print("="*80)
        for test_id in sorted(markers_without_jira_test):
            print(f"  {test_id}")
        print()
    
    # Show sample Jira tests without markers
    if jira_tests_without_markers:
        print("="*80)
        print(f"Jira Tests WITHOUT Markers (showing first 20):")
        print("="*80)
        for test_key in sorted(list(jira_tests_without_markers))[:20]:
            # Get test info
            test_info = next((t for t in all_tests if t.get('key') == test_key), None)
            if test_info:
                summary = test_info.get('summary', '')[:60]
                # Replace problematic characters
                summary = summary.replace('≠', '!=').replace('–', '-')
                print(f"  {test_key:15} {summary}")
        if len(jira_tests_without_markers) > 20:
            print(f"  ... and {len(jira_tests_without_markers) - 20} more")
        print()
    
    print("="*80)
    print("Summary")
    print("="*80)
    print(f"Markers in code: {len(markers_in_code)}")
    print(f"Tests in Jira: {len(all_test_keys)}")
    print(f"Markers with Jira test: {len(markers_with_jira_test)}")
    print(f"Coverage: {len(markers_with_jira_test)/len(all_test_keys)*100:.1f}% of Jira tests have markers")
    print("="*80)
    
    client.close()


if __name__ == '__main__':
    main()

