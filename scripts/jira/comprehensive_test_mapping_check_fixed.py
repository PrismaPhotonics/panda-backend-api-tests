"""Comprehensive Test Mapping Check - FIXED VERSION with proper function-level checking"""
import sys
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any
import csv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Comprehensive Test Mapping Check - FIXED VERSION")
print("="*80)
print()

# 1. Load all tests from Jira CSV export
print("="*80)
print("STEP 1: Loading tests from Jira CSV export")
print("="*80)
print()

jira_tests = {}
csv_file = Path(r"c:\Users\roy.avrahami\Downloads\Jira (28).csv")

if csv_file.exists():
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_key = row.get('Issue key', '')
                if test_key and row.get('Issue Type', '') == 'Test':
                    jira_tests[test_key] = {
                        'key': test_key,
                        'summary': row.get('Summary', ''),
                        'status': row.get('Status', ''),
                        'test_plan': row.get('Custom field (Test plan)', ''),
                        'test_type': row.get('Custom field (Test Type)', ''),
                        'description': row.get('Description', ''),
                        'priority': row.get('Priority', ''),
                    }
        print(f"Loaded {len(jira_tests)} tests from Jira CSV")
    except Exception as e:
        print(f"[ERROR] Failed to load CSV: {e}")
        jira_tests = {}
else:
    print(f"[WARNING] CSV file not found: {csv_file}")
    print("Will use only automation code analysis")

print()

# 2. Scan automation code for Xray markers - FIXED to check each test function
print("="*80)
print("STEP 2: Scanning automation code for Xray markers (FIXED)")
print("="*80)
print()

tests_dir = project_root / "tests"
automation_markers: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
tests_without_markers: List[Tuple[str, str]] = []  # (file_path, test_func_name)
tests_with_multiple_markers: List[Tuple[str, str, List[str]]] = []  # (file_path, test_func, test_ids)

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')
test_func_pattern = re.compile(r'def\s+(test_\w+)')

# Scan all test files
test_files = list(tests_dir.rglob('test_*.py'))
print(f"Scanning {len(test_files)} test files...")

for test_file in test_files:
    try:
        content = test_file.read_text(encoding='utf-8')
        try:
            rel_path = str(test_file.relative_to(project_root))
        except ValueError:
            rel_path = str(test_file)
        
        # Find all test functions in this file
        test_funcs = test_func_pattern.findall(content)
        
        # For each test function, check if it has markers
        for test_func in test_funcs:
            # Find the test function definition and its content
            # Look for the function and everything until next function or end of file
            func_pattern = re.compile(
                rf'def\s+{re.escape(test_func)}.*?(?=def\s+test_|\Z)',
                re.DOTALL
            )
            match = func_pattern.search(content)
            
            if match:
                func_content = match.group(0)
                
                # Find all Xray markers in this function
                func_xray_markers = []
                func_jira_markers = []
                
                for line in func_content.splitlines():
                    # Xray markers
                    xray_matches = xray_pattern.findall(line)
                    for match_str in xray_matches:
                        test_ids = [tid.strip() for tid in match_str.split(',')]
                        for test_id in test_ids:
                            if test_id.startswith('PZ-'):
                                func_xray_markers.append(test_id)
                                # Find line number
                                line_num = content[:match.start()].count('\n') + 1
                                automation_markers[test_id].append((rel_path, line_num))
                    
                    # Jira markers
                    jira_matches = jira_pattern.findall(line)
                    for match_str in jira_matches:
                        test_ids = [tid.strip() for tid in match_str.split(',')]
                        for test_id in test_ids:
                            if test_id.startswith('PZ-'):
                                func_jira_markers.append(test_id)
                
                # Check if function has markers
                all_markers_in_func = func_xray_markers + func_jira_markers
                
                if not all_markers_in_func:
                    # No markers in this function
                    tests_without_markers.append((rel_path, test_func))
                elif len(set(all_markers_in_func)) > 1:
                    # Multiple different test IDs in this function
                    tests_with_multiple_markers.append((rel_path, test_func, list(set(all_markers_in_func))))
            else:
                # Couldn't find function content, assume no markers
                tests_without_markers.append((rel_path, test_func))
    
    except Exception as e:
        print(f"[WARNING] Could not read {test_file}: {e}")

print(f"Found {len(automation_markers)} unique test IDs in automation code")
print(f"Found {len(tests_without_markers)} test functions without markers")
print(f"Found {len(tests_with_multiple_markers)} test functions with multiple markers")
print()

# 3. Compare Jira tests with automation markers
print("="*80)
print("STEP 3: Comparing Jira tests with automation code")
print("="*80)
print()

if jira_tests:
    jira_test_ids = set(jira_tests.keys())
    automation_test_ids = set(automation_markers.keys())
    
    # Tests in Jira but not in automation
    missing_in_automation = jira_test_ids - automation_test_ids
    
    # Tests in automation but not in Jira
    missing_in_jira = automation_test_ids - jira_test_ids
    
    # Tests in both
    in_both = jira_test_ids & automation_test_ids
    
    print(f"Tests in Jira: {len(jira_test_ids)}")
    print(f"Tests in automation: {len(automation_test_ids)}")
    print(f"Tests in both: {len(in_both)}")
    print(f"Tests in Jira but NOT in automation: {len(missing_in_automation)}")
    print(f"Tests in automation but NOT in Jira: {len(missing_in_jira)}")
    print()
else:
    missing_in_automation = set()
    missing_in_jira = set()
    in_both = set()
    print("[WARNING] No Jira tests loaded, skipping comparison")

# 4. Generate comprehensive report
print("="*80)
print("STEP 4: Generating comprehensive report")
print("="*80)
print()

output_dir = Path("docs/04_testing/xray_mapping")
output_dir.mkdir(parents=True, exist_ok=True)

report_file = output_dir / "COMPREHENSIVE_TEST_MAPPING_REPORT_FIXED.md"

with open(report_file, 'w', encoding='utf-8') as f:
    f.write("# Comprehensive Test Mapping Report - FIXED VERSION\n\n")
    f.write("**Generated:** Automated check of automation code vs Jira tests\n")
    f.write("**Note:** This version checks each test function individually\n\n")
    f.write("---\n\n")
    
    # Summary
    f.write("## Executive Summary\n\n")
    f.write("| Metric | Count |\n")
    f.write("|--------|-------|\n")
    if jira_tests:
        f.write(f"| Total tests in Jira | {len(jira_test_ids)} |\n")
    f.write(f"| Total test IDs in automation | {len(automation_markers)} |\n")
    f.write(f"| Total test functions | {len(tests_without_markers) + len(tests_with_multiple_markers) + sum(len(v) for v in automation_markers.values())} |\n")
    f.write(f"| Test functions with markers | {len(tests_without_markers) + len(tests_with_multiple_markers)} |\n")
    f.write(f"| Test functions WITHOUT markers | {len(tests_without_markers)} |\n")
    f.write(f"| Test functions with multiple markers | {len(tests_with_multiple_markers)} |\n")
    if jira_tests:
        f.write(f"| Tests in Jira but NOT in automation | {len(missing_in_automation)} |\n")
        f.write(f"| Tests in automation but NOT in Jira | {len(missing_in_jira)} |\n")
    f.write("\n")
    
    # 1. Tests without markers
    f.write("## 1. Tests Without Xray Markers\n\n")
    if tests_without_markers:
        f.write(f"**Total: {len(tests_without_markers)} test functions without markers**\n\n")
        f.write("| # | File | Test Function |\n")
        f.write("|---|------|---------------|\n")
        
        # Group by file
        by_file = defaultdict(list)
        for file_path, test_func in tests_without_markers:
            by_file[file_path].append(test_func)
        
        row_num = 1
        for file_path, funcs in sorted(by_file.items()):
            for test_func in sorted(funcs):
                f.write(f"| {row_num} | `{file_path}` | `{test_func}` |\n")
                row_num += 1
                if row_num > 200:
                    f.write(f"| ... | ... and {len(tests_without_markers) - 200} more | ... |\n")
                    break
            if row_num > 200:
                break
    else:
        f.write("**All test functions have Xray markers!**\n")
    f.write("\n")
    
    # 2. Tests with multiple markers
    f.write("## 2. Tests With Multiple Test IDs\n\n")
    if tests_with_multiple_markers:
        f.write(f"**Total: {len(tests_with_multiple_markers)} test functions with multiple markers**\n\n")
        f.write("These tests check multiple things in one automated test:\n\n")
        f.write("| # | File | Test Function | Test IDs |\n")
        f.write("|---|------|---------------|----------|\n")
        for i, (file_path, test_func, test_ids) in enumerate(tests_with_multiple_markers, 1):
            test_ids_str = ", ".join(test_ids)
            f.write(f"| {i} | `{file_path}` | `{test_func}` | {test_ids_str} |\n")
    else:
        f.write("**No tests with multiple markers found**\n")
    f.write("\n")
    
    # 3. Tests in Jira but not in automation
    if jira_tests and missing_in_automation:
        f.write("## 3. Tests in Jira but NOT in Automation\n\n")
        f.write(f"**Total: {len(missing_in_automation)} tests need to be automated**\n\n")
        f.write("| # | Test ID | Summary | Status | Test Type |\n")
        f.write("|---|---------|---------|--------|-----------|\n")
        for i, test_id in enumerate(sorted(missing_in_automation)[:100], 1):
            test = jira_tests[test_id]
            summary = test['summary'].replace('|', '\\|')[:60]
            status = test['status']
            test_type = test.get('test_type', 'N/A')
            f.write(f"| {i} | {test_id} | {summary} | {status} | {test_type} |\n")
        if len(missing_in_automation) > 100:
            f.write(f"| ... | ... and {len(missing_in_automation) - 100} more | ... | ... | ... |\n")
        f.write("\n")
    
    # 4. Tests in automation but not in Jira
    if missing_in_jira:
        f.write("## 4. Tests in Automation but NOT in Jira\n\n")
        f.write(f"**Total: {len(missing_in_jira)} test IDs in automation not found in Jira**\n\n")
        f.write("| # | Test ID | Files |\n")
        f.write("|---|---------|-------|\n")
        for i, test_id in enumerate(sorted(missing_in_jira)[:50], 1):
            files = automation_markers[test_id]
            files_str = ", ".join([f"`{f[0]}`" for f in files[:3]])
            if len(files) > 3:
                files_str += f" ... and {len(files) - 3} more"
            f.write(f"| {i} | {test_id} | {files_str} |\n")
        if len(missing_in_jira) > 50:
            f.write(f"| ... | ... and {len(missing_in_jira) - 50} more | ... |\n")
        f.write("\n")
    
    # 5. Check test descriptions for quality
    if jira_tests:
        f.write("## 5. Test Quality Check - Jira Tests\n\n")
        f.write("Checking if tests in Jira are written clearly and accurately:\n\n")
        
        quality_issues = []
        for test_id, test in jira_tests.items():
            issues = []
            
            # Check summary
            summary = test['summary']
            if not summary or len(summary) < 10:
                issues.append("Summary too short or empty")
            
            # Check description
            description = test.get('description', '')
            if not description or len(description) < 50:
                issues.append("Description missing or too short")
            
            # Check test type
            test_type = test.get('test_type', '')
            if not test_type:
                issues.append("Test Type not specified")
            
            if issues:
                quality_issues.append((test_id, test, issues))
        
        if quality_issues:
            f.write(f"**Total: {len(quality_issues)} tests with quality issues**\n\n")
            f.write("| # | Test ID | Summary | Issues |\n")
            f.write("|---|---------|---------|--------|\n")
            for i, (test_id, test, issues) in enumerate(quality_issues[:50], 1):
                summary = test['summary'].replace('|', '\\|')[:50]
                issues_str = "; ".join(issues)
                f.write(f"| {i} | {test_id} | {summary} | {issues_str} |\n")
            if len(quality_issues) > 50:
                f.write(f"| ... | ... and {len(quality_issues) - 50} more | ... | ... |\n")
        else:
            f.write("**All tests have good quality descriptions!**\n")
        f.write("\n")

print(f"Report saved to: {report_file}")

# Print summary
print()
print("="*80)
print("SUMMARY")
print("="*80)
print(f"[OK] Tests with Xray markers: {len(automation_markers)} unique test IDs")
print(f"[WARNING] Test functions without markers: {len(tests_without_markers)}")
print(f"[INFO] Test functions with multiple markers: {len(tests_with_multiple_markers)}")
if jira_tests:
    print(f"[MISSING] Tests in Jira but NOT in automation: {len(missing_in_automation)}")
    print(f"[EXTRA] Tests in automation but NOT in Jira: {len(missing_in_jira)}")
print()
print(f"Full report: {report_file}")

