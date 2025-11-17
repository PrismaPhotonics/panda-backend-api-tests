"""Comprehensive Test Mapping Check - Compare Jira tests with automation code"""
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
print("Comprehensive Test Mapping Check")
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

# 2. Scan automation code for Xray markers
print("="*80)
print("STEP 2: Scanning automation code for Xray markers")
print("="*80)
print()

tests_dir = project_root / "tests"
automation_markers: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
tests_without_markers: List[Tuple[str, int, str]] = []
tests_with_multiple_markers: List[Tuple[str, List[str]]] = []

# Pattern to find Xray markers
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')

# Scan all test files
test_files = list(tests_dir.rglob('test_*.py'))
print(f"Scanning {len(test_files)} test files...")

for test_file in test_files:
    try:
        content = test_file.read_text(encoding='utf-8')
        lines = content.splitlines()
        
        # Find all Xray markers in this file
        file_xray_markers = []
        file_jira_markers = []
        
        for line_num, line in enumerate(lines, 1):
            # Check for Xray markers
            xray_matches = xray_pattern.findall(line)
            for match in xray_matches:
                # Handle multiple test IDs in one marker
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        file_xray_markers.append(test_id)
                        try:
                            rel_path = str(test_file.relative_to(project_root))
                        except ValueError:
                            rel_path = str(test_file)
                        automation_markers[test_id].append((rel_path, line_num))
            
            # Check for Jira markers
            jira_matches = jira_pattern.findall(line)
            for match in jira_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        file_jira_markers.append(test_id)
        
        # Check if file has test functions but no markers
        has_test_function = re.search(r'def\s+test_', content)
        if has_test_function and not file_xray_markers and not file_jira_markers:
            try:
                rel_path = str(test_file.relative_to(project_root))
            except ValueError:
                rel_path = str(test_file)
            # Find test function names
            test_funcs = re.findall(r'def\s+(test_\w+)', content)
            for test_func in test_funcs:
                tests_without_markers.append((rel_path, 0, test_func))
        
        # Check for multiple markers in same test function
        # Find test functions with multiple markers
        test_func_pattern = re.compile(r'def\s+(test_\w+).*?(?=def\s+test_|\Z)', re.DOTALL)
        for match in test_func_pattern.finditer(content):
            test_func = match.group(1)
            func_content = match.group(0)
            markers_in_func = xray_pattern.findall(func_content)
            if len(markers_in_func) > 1:
                all_test_ids = []
                for marker_match in markers_in_func:
                    test_ids = [tid.strip() for tid in marker_match.split(',')]
                    all_test_ids.extend(test_ids)
                if len(all_test_ids) > 1:
                    try:
                        rel_path = str(test_file.relative_to(project_root))
                    except ValueError:
                        rel_path = str(test_file)
                    tests_with_multiple_markers.append((rel_path, test_func, all_test_ids))
    
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

report_file = output_dir / "COMPREHENSIVE_TEST_MAPPING_REPORT.md"

with open(report_file, 'w', encoding='utf-8') as f:
    f.write("# Comprehensive Test Mapping Report\n\n")
    f.write("**Generated:** Automated check of automation code vs Jira tests\n\n")
    f.write("---\n\n")
    
    # Summary
    f.write("## 📊 Executive Summary\n\n")
    f.write("| Metric | Count |\n")
    f.write("|--------|-------|\n")
    if jira_tests:
        f.write(f"| Total tests in Jira | {len(jira_test_ids)} |\n")
    f.write(f"| Total test IDs in automation | {len(automation_markers)} |\n")
    f.write(f"| Tests with markers | {len(automation_markers)} |\n")
    f.write(f"| Tests without markers | {len(tests_without_markers)} |\n")
    f.write(f"| Tests with multiple markers | {len(tests_with_multiple_markers)} |\n")
    if jira_tests:
        f.write(f"| Tests in Jira but NOT in automation | {len(missing_in_automation)} |\n")
        f.write(f"| Tests in automation but NOT in Jira | {len(missing_in_jira)} |\n")
    f.write("\n")
    
    # 1. Tests without markers
    f.write("## 1. ⚠️ Tests Without Xray Markers\n\n")
    if tests_without_markers:
        f.write(f"**Total: {len(tests_without_markers)} test functions without markers**\n\n")
        f.write("| # | File | Test Function |\n")
        f.write("|---|------|---------------|\n")
        for i, (file_path, line_num, test_func) in enumerate(tests_without_markers[:100], 1):
            f.write(f"| {i} | `{file_path}` | `{test_func}` |\n")
        if len(tests_without_markers) > 100:
            f.write(f"| ... | ... and {len(tests_without_markers) - 100} more | ... |\n")
    else:
        f.write("✅ **All test functions have Xray markers!**\n")
    f.write("\n")
    
    # 2. Tests with multiple markers
    f.write("## 2. 🔄 Tests With Multiple Test IDs\n\n")
    if tests_with_multiple_markers:
        f.write(f"**Total: {len(tests_with_multiple_markers)} test functions with multiple markers**\n\n")
        f.write("These tests check multiple things in one automated test:\n\n")
        f.write("| # | File | Test Function | Test IDs |\n")
        f.write("|---|------|---------------|----------|\n")
        for i, (file_path, test_func, test_ids) in enumerate(tests_with_multiple_markers, 1):
            test_ids_str = ", ".join(test_ids)
            f.write(f"| {i} | `{file_path}` | `{test_func}` | {test_ids_str} |\n")
    else:
        f.write("✅ **No tests with multiple markers found**\n")
    f.write("\n")
    
    # 3. Tests in Jira but not in automation
    if jira_tests and missing_in_automation:
        f.write("## 3. ❌ Tests in Jira but NOT in Automation\n\n")
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
        f.write("## 4. ⚠️ Tests in Automation but NOT in Jira\n\n")
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
        f.write("## 5. 📝 Test Quality Check - Jira Tests\n\n")
        f.write("Checking if tests in Jira are written clearly and accurately:\n\n")
        
        quality_issues = []
        for test_id, test in jira_tests.items():
            issues = []
            
            # Check summary
            summary = test['summary']
            if not summary or len(summary) < 10:
                issues.append("Summary too short or empty")
            if 'test' in summary.lower() and 'test' in summary.lower()[:5]:
                issues.append("Summary starts with 'test' (redundant)")
            
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
            f.write("✅ **All tests have good quality descriptions!**\n")
        f.write("\n")
    
    # 6. All automation markers
    f.write("## 6. ✅ All Automation Markers\n\n")
    f.write(f"**Total: {len(automation_markers)} unique test IDs in automation**\n\n")
    f.write("| # | Test ID | Files |\n")
    f.write("|---|---------|-------|\n")
    for i, (test_id, files) in enumerate(sorted(automation_markers.items())[:100], 1):
        files_str = ", ".join([f"`{f[0]}:{f[1]}`" for f in files[:2]])
        if len(files) > 2:
            files_str += f" ... and {len(files) - 2} more"
        f.write(f"| {i} | {test_id} | {files_str} |\n")
    if len(automation_markers) > 100:
        f.write(f"| ... | ... and {len(automation_markers) - 100} more | ... |\n")
    f.write("\n")

print(f"Report saved to: {report_file}")

# Print summary
print()
print("="*80)
print("SUMMARY")
print("="*80)
print(f"[OK] Tests with Xray markers: {len(automation_markers)}")
print(f"[WARNING] Tests without markers: {len(tests_without_markers)}")
print(f"[INFO] Tests with multiple markers: {len(tests_with_multiple_markers)}")
if jira_tests:
    print(f"[MISSING] Tests in Jira but NOT in automation: {len(missing_in_automation)}")
    print(f"[EXTRA] Tests in automation but NOT in Jira: {len(missing_in_jira)}")
print()
print(f"Full report: {report_file}")

