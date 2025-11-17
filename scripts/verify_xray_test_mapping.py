"""
Verify Xray Test Mapping - Comprehensive Check
==============================================

This script verifies that all automation tests are properly linked to Xray tests in Jira.

It checks:
1. All Xray markers in code exist in Jira
2. All Jira Xray tests have corresponding automation tests
3. All Jira bug markers are properly linked
4. Generates comprehensive report

Usage:
    python scripts/verify_xray_test_mapping.py
    python scripts/verify_xray_test_mapping.py --jira-check  # Requires Jira credentials
"""

import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List, Tuple
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def find_all_xray_markers() -> Dict[str, List[Tuple[str, int]]]:
    """
    Find all Xray markers in automation code.
    
    Returns:
        Dict mapping Xray ID -> List of (file_path, line_number) tuples
    """
    markers = defaultdict(list)
    test_files = []
    
    # Find all Python test files
    for test_file in Path('tests').rglob('*.py'):
        if test_file.name.startswith('test_') or 'conftest' in test_file.name:
            test_files.append(test_file)
    
    print(f"Scanning {len(test_files)} test files for Xray markers...")
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Find all @pytest.mark.xray("PZ-XXXXX") patterns
            for line_num, line in enumerate(lines, 1):
                # Match single or multiple IDs: @pytest.mark.xray("PZ-12345") or @pytest.mark.xray("PZ-12345", "PZ-67890")
                xray_matches = re.findall(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)', line)
                for match in xray_matches:
                    # Handle multiple IDs separated by commas
                    test_ids = [tid.strip() for tid in match.split(',')]
                    for test_id in test_ids:
                        if test_id.startswith('PZ-'):
                            try:
                                rel_path = str(test_file.relative_to(project_root))
                            except ValueError:
                                rel_path = str(test_file)
                            markers[test_id].append((rel_path, line_num))
            
        except Exception as e:
            print(f"Warning: Could not read {test_file}: {e}")
            continue
    
    return dict(markers)


def find_all_jira_markers() -> Dict[str, List[Tuple[str, int]]]:
    """
    Find all Jira bug markers in automation code.
    
    Returns:
        Dict mapping Jira ID -> List of (file_path, line_number) tuples
    """
    markers = defaultdict(list)
    test_files = []
    
    # Find all Python test files
    for test_file in Path('tests').rglob('*.py'):
        if test_file.name.startswith('test_') or 'conftest' in test_file.name:
            test_files.append(test_file)
    
    print(f"Scanning {len(test_files)} test files for Jira bug markers...")
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Find all @pytest.mark.jira("PZ-XXXXX") patterns
            for line_num, line in enumerate(lines, 1):
                jira_matches = re.findall(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)', line)
                for match in jira_matches:
                    # Handle multiple IDs separated by commas
                    test_ids = [tid.strip() for tid in match.split(',')]
                    for test_id in test_ids:
                        if test_id.startswith('PZ-'):
                            try:
                                rel_path = str(test_file.relative_to(project_root))
                            except ValueError:
                                rel_path = str(test_file)
                            markers[test_id].append((rel_path, line_num))
            
        except Exception as e:
            print(f"Warning: Could not read {test_file}: {e}")
            continue
    
    return dict(markers)


def load_xray_list_from_file() -> Set[str]:
    """
    Load Xray test IDs from documentation files.
    
    Returns:
        Set of Xray test IDs
    """
    xray_tests = set()
    
    # Try to load from xray_tests_list_FINAL.txt
    xray_list_file = project_root / 'docs' / '04_testing' / 'xray_mapping' / 'xray_tests_list_FINAL.txt'
    if xray_list_file.exists():
        print(f"Loading Xray list from {xray_list_file}...")
        try:
            content = xray_list_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if line.strip() and not line.strip().startswith('#'):
                    # Extract PZ-XXXXX from line
                    match = re.search(r'(PZ-\d+)', line)
                    if match:
                        xray_tests.add(match.group(1))
        except Exception as e:
            print(f"Warning: Could not read {xray_list_file}: {e}")
    
    return xray_tests


def get_jira_tests(jira_client=None) -> Set[str]:
    """
    Get all Xray test IDs from Jira.
    
    Args:
        jira_client: Optional JiraClient instance
        
    Returns:
        Set of Xray test IDs
    """
    if jira_client is None:
        try:
            from external.jira import JiraClient
            jira_client = JiraClient()
        except Exception as e:
            print(f"Warning: Could not connect to Jira: {e}")
            return set()
    
    try:
        print("Fetching all Xray tests from Jira...")
        all_tests = jira_client.search_issues(
            jql='project = PZ AND issuetype = Test',
            max_results=None
        )
        test_keys = {test['key'] for test in all_tests if test.get('key')}
        print(f"Found {len(test_keys)} Xray tests in Jira")
        return test_keys
    except Exception as e:
        print(f"Warning: Could not fetch tests from Jira: {e}")
        return set()


def generate_report(
    xray_markers: Dict[str, List[Tuple[str, int]]],
    jira_markers: Dict[str, List[Tuple[str, int]]],
    xray_list: Set[str],
    jira_tests: Set[str]
) -> str:
    """
    Generate comprehensive report.
    
    Returns:
        Report as string
    """
    report_lines = []
    report_lines.append("# 📊 Xray Test Mapping Verification Report\n")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Summary
    report_lines.append("## 📈 Summary\n\n")
    report_lines.append(f"- **Xray markers in code:** {len(xray_markers)}\n")
    report_lines.append(f"- **Jira bug markers in code:** {len(jira_markers)}\n")
    report_lines.append(f"- **Xray tests in documentation:** {len(xray_list)}\n")
    report_lines.append(f"- **Xray tests in Jira:** {len(jira_tests)}\n\n")
    
    # Xray markers analysis
    report_lines.append("## 🔍 Xray Markers Analysis\n\n")
    
    if xray_list:
        xray_markers_set = set(xray_markers.keys())
        covered_in_docs = xray_markers_set & xray_list
        not_in_docs = xray_markers_set - xray_list
        docs_not_covered = xray_list - xray_markers_set
        
        report_lines.append(f"- **Markers covered in docs:** {len(covered_in_docs)}\n")
        report_lines.append(f"- **Markers NOT in docs:** {len(not_in_docs)}\n")
        report_lines.append(f"- **Docs tests NOT covered:** {len(docs_not_covered)}\n\n")
        
        if not_in_docs:
            report_lines.append("### ⚠️ Xray Markers NOT in Documentation\n\n")
            report_lines.append("| Xray ID | File | Line |\n")
            report_lines.append("|---------|------|------|\n")
            for test_id in sorted(not_in_docs):
                for file_path, line_num in xray_markers[test_id]:
                    report_lines.append(f"| {test_id} | {file_path} | {line_num} |\n")
            report_lines.append("\n")
        
        if docs_not_covered:
            report_lines.append(f"### ⚠️ Documentation Tests NOT Covered ({len(docs_not_covered)} tests)\n\n")
            report_lines.append("| Xray ID | Status |\n")
            report_lines.append("|---------|--------|\n")
            for test_id in sorted(list(docs_not_covered))[:50]:  # Limit to 50
                report_lines.append(f"| {test_id} | ❌ Missing |\n")
            if len(docs_not_covered) > 50:
                report_lines.append(f"| ... | ... and {len(docs_not_covered) - 50} more |\n")
            report_lines.append("\n")
    
    # Jira verification
    if jira_tests:
        xray_markers_set = set(xray_markers.keys())
        jira_markers_set = set(jira_markers.keys())
        all_markers = xray_markers_set | jira_markers_set
        
        markers_with_jira_test = all_markers & jira_tests
        markers_without_jira_test = all_markers - jira_tests
        jira_tests_without_markers = jira_tests - all_markers
        
        report_lines.append("## 🔗 Jira Verification\n\n")
        report_lines.append(f"- **Markers with Jira test:** {len(markers_with_jira_test)}\n")
        report_lines.append(f"- **Markers without Jira test:** {len(markers_without_jira_test)}\n")
        report_lines.append(f"- **Jira tests without markers:** {len(jira_tests_without_markers)}\n\n")
        
        if markers_without_jira_test:
            report_lines.append("### ⚠️ Markers WITHOUT Jira Test\n\n")
            report_lines.append("| Test ID | Type | File | Line |\n")
            report_lines.append("|---------|------|------|------|\n")
            for test_id in sorted(markers_without_jira_test):
                marker_type = "Xray" if test_id in xray_markers else "Jira Bug"
                locations = xray_markers.get(test_id, []) + jira_markers.get(test_id, [])
                for file_path, line_num in locations:
                    report_lines.append(f"| {test_id} | {marker_type} | {file_path} | {line_num} |\n")
            report_lines.append("\n")
        
        if jira_tests_without_markers:
            report_lines.append(f"### ⚠️ Jira Tests WITHOUT Markers ({len(jira_tests_without_markers)} tests)\n\n")
            report_lines.append("| Test ID | Status |\n")
            report_lines.append("|---------|--------|\n")
            for test_id in sorted(list(jira_tests_without_markers))[:50]:  # Limit to 50
                report_lines.append(f"| {test_id} | ❌ Missing |\n")
            if len(jira_tests_without_markers) > 50:
                report_lines.append(f"| ... | ... and {len(jira_tests_without_markers) - 50} more |\n")
            report_lines.append("\n")
    
    # Detailed marker listing
    report_lines.append("## 📋 All Xray Markers in Code\n\n")
    report_lines.append("| Xray ID | Files | Total Locations |\n")
    report_lines.append("|---------|-------|-----------------|\n")
    for test_id in sorted(xray_markers.keys()):
        locations = xray_markers[test_id]
        files = set(f for f, _ in locations)
        report_lines.append(f"| {test_id} | {len(files)} | {len(locations)} |\n")
    report_lines.append("\n")
    
    # Jira bug markers
    report_lines.append("## 🐛 Jira Bug Markers\n\n")
    report_lines.append("| Jira ID | Files | Total Locations |\n")
    report_lines.append("|---------|-------|-----------------|\n")
    for test_id in sorted(jira_markers.keys()):
        locations = jira_markers[test_id]
        files = set(f for f, _ in locations)
        report_lines.append(f"| {test_id} | {len(files)} | {len(locations)} |\n")
    report_lines.append("\n")
    
    # Coverage statistics
    report_lines.append("## 📊 Coverage Statistics\n\n")
    
    if xray_list:
        coverage_pct = (len(set(xray_markers.keys()) & xray_list) / len(xray_list) * 100) if xray_list else 0
        report_lines.append(f"- **Documentation coverage:** {coverage_pct:.1f}%\n")
    
    if jira_tests:
        all_markers = set(xray_markers.keys()) | set(jira_markers.keys())
        coverage_pct = (len(all_markers & jira_tests) / len(jira_tests) * 100) if jira_tests else 0
        report_lines.append(f"- **Jira tests coverage:** {coverage_pct:.1f}%\n")
    
    report_lines.append("\n")
    
    # Conclusion
    report_lines.append("## ✅ Conclusion\n\n")
    
    all_issues = []
    if xray_list:
        xray_markers_set = set(xray_markers.keys())
        if xray_markers_set - xray_list:
            all_issues.append(f"{len(xray_markers_set - xray_list)} Xray markers not in documentation")
        if xray_list - xray_markers_set:
            all_issues.append(f"{len(xray_list - xray_markers_set)} documentation tests without markers")
    
    if jira_tests:
        all_markers = set(xray_markers.keys()) | set(jira_markers.keys())
        if all_markers - jira_tests:
            all_issues.append(f"{len(all_markers - jira_tests)} markers without Jira tests")
        if jira_tests - all_markers:
            all_issues.append(f"{len(jira_tests - all_markers)} Jira tests without markers")
    
    if not all_issues:
        report_lines.append("**✅ All tests are properly linked!**\n\n")
    else:
        report_lines.append("**⚠️ Issues found:**\n\n")
        for issue in all_issues:
            report_lines.append(f"- {issue}\n")
        report_lines.append("\n")
    
    return ''.join(report_lines)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Verify Xray test mapping')
    parser.add_argument('--jira-check', action='store_true', help='Check against Jira (requires credentials)')
    parser.add_argument('--output', type=str, help='Output file path', default='docs/04_testing/xray_mapping/XRAY_MAPPING_VERIFICATION.md')
    args = parser.parse_args()
    
    print("="*80)
    print("Xray Test Mapping Verification")
    print("="*80)
    print()
    
    # Find all markers
    print("Step 1: Finding Xray markers in code...")
    xray_markers = find_all_xray_markers()
    print(f"   Found {len(xray_markers)} unique Xray IDs")
    
    print("\nStep 2: Finding Jira bug markers in code...")
    jira_markers = find_all_jira_markers()
    print(f"   Found {len(jira_markers)} unique Jira bug IDs")
    
    # Load Xray list from documentation
    print("\nStep 3: Loading Xray list from documentation...")
    xray_list = load_xray_list_from_file()
    print(f"   Found {len(xray_list)} tests in documentation")
    
    # Get Jira tests if requested
    jira_tests = set()
    if args.jira_check:
        print("\nStep 4: Fetching tests from Jira...")
        jira_tests = get_jira_tests()
        print(f"   Found {len(jira_tests)} tests in Jira")
    else:
        print("\nStep 4: Skipping Jira check (use --jira-check to enable)")
    
    # Generate report
    print("\nStep 5: Generating report...")
    report = generate_report(xray_markers, jira_markers, xray_list, jira_tests)
    
    # Save report
    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report, encoding='utf-8')
    print(f"   Report saved to: {output_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Xray markers in code: {len(xray_markers)}")
    print(f"Jira bug markers in code: {len(jira_markers)}")
    print(f"Xray tests in documentation: {len(xray_list)}")
    if jira_tests:
        print(f"Xray tests in Jira: {len(jira_tests)}")
        all_markers = set(xray_markers.keys()) | set(jira_markers.keys())
        coverage = (len(all_markers & jira_tests) / len(jira_tests) * 100) if jira_tests else 0
        print(f"Coverage: {coverage:.1f}%")
    print("="*80)
    print(f"\nFull report: {output_file}")


if __name__ == '__main__':
    main()

