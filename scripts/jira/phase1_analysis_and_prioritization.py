"""Phase 1: Analysis & Prioritization - Comprehensive Analysis"""
import sys
import re
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Phase 1: Analysis & Prioritization")
print("="*80)
print()

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')
test_func_pattern = re.compile(r'def\s+(test_\w+)')

# 1. Load Jira tests
print("="*80)
print("STEP 1: Loading Jira tests")
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
                        'test_plan': row.get('Custom field (Test plan', ''),
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
    jira_tests = {}

print()

# 2. Load automation markers
print("="*80)
print("STEP 2: Loading automation markers")
print("="*80)
print()

tests_dir = project_root / "tests"
automation_markers = defaultdict(list)
automation_test_ids = set()

# Scan tests/ directory
test_files = list(tests_dir.rglob('test_*.py'))
for test_file in test_files:
    try:
        content = test_file.read_text(encoding='utf-8')
        rel_path = str(test_file.relative_to(project_root))
        
        for line_num, line in enumerate(content.splitlines(), 1):
            xray_matches = xray_pattern.findall(line)
            for match in xray_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        automation_test_ids.add(test_id)
                        automation_markers[test_id].append((rel_path, line_num))
            
            jira_matches = jira_pattern.findall(line)
            for match in jira_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        automation_test_ids.add(test_id)
                        automation_markers[test_id].append((rel_path, line_num))
    except Exception as e:
        print(f"[WARNING] Could not read {test_file}: {e}")

# Scan files outside tests/ directory
outside_test_files = [
    project_root / "scripts" / "ui" / "test_login_page_comprehensive.py",
    project_root / "focus_server_api_load_tests" / "focus_api_tests" / "test_api_contract.py",
    project_root / "scripts" / "test_k8s_fixed.py",
    project_root / "scripts" / "test_mongodb_connection.py",
    project_root / "scripts" / "test_ssh_connection.py",
]

for test_file in outside_test_files:
    if test_file.exists():
        try:
            content = test_file.read_text(encoding='utf-8')
            rel_path = str(test_file.relative_to(project_root))
            
            for line_num, line in enumerate(content.splitlines(), 1):
                xray_matches = xray_pattern.findall(line)
                for match in xray_matches:
                    test_ids = [tid.strip() for tid in match.split(',')]
                    for test_id in test_ids:
                        if test_id.startswith('PZ-'):
                            automation_test_ids.add(test_id)
                            automation_markers[test_id].append((rel_path, line_num))
                
                jira_matches = jira_pattern.findall(line)
                for match in jira_matches:
                    test_ids = [tid.strip() for tid in match.split(',')]
                    for test_id in test_ids:
                        if test_id.startswith('PZ-'):
                            automation_test_ids.add(test_id)
                            automation_markers[test_id].append((rel_path, line_num))
        except Exception as e:
            print(f"[WARNING] Could not read {test_file}: {e}")

print(f"Found {len(automation_test_ids)} unique test IDs in automation")
print()

# 3. Find missing tests in Jira
print("="*80)
print("STEP 3: Finding missing tests in Jira")
print("="*80)
print()

if jira_tests:
    jira_test_ids = set(jira_tests.keys())
    missing_in_automation = jira_test_ids - automation_test_ids
    
    print(f"Tests in Jira: {len(jira_test_ids)}")
    print(f"Tests in automation: {len(automation_test_ids)}")
    print(f"Tests missing in automation: {len(missing_in_automation)}")
    print()
    
    # Categorize missing tests
    missing_by_category = defaultdict(list)
    
    for test_id in missing_in_automation:
        test = jira_tests[test_id]
        summary = test['summary'].lower()
        
        if 'api' in summary or 'endpoint' in summary or '/config' in summary or '/metadata' in summary or '/waterfall' in summary or '/channels' in summary:
            category = 'API'
        elif 'integration' in summary:
            category = 'Integration'
        elif 'infrastructure' in summary or 'pod' in summary or 'mongodb' in summary or 'rabbitmq' in summary:
            category = 'Infrastructure'
        elif 'data quality' in summary or 'schema' in summary or 'metadata' in summary:
            category = 'Data Quality'
        elif 'performance' in summary or 'latency' in summary or 'load' in summary:
            category = 'Performance/Load'
        elif 'security' in summary or 'malformed' in summary:
            category = 'Security'
        elif 'calculation' in summary or 'frequency' in summary or 'nyquist' in summary:
            category = 'Calculations'
        elif 'health' in summary or 'check' in summary:
            category = 'Health Check'
        else:
            category = 'Other'
        
        missing_by_category[category].append((test_id, test))
    
    print("Missing tests by category:")
    for category, tests in sorted(missing_by_category.items()):
        print(f"  {category}: {len(tests)} tests")
    print()

# 4. Find test functions without markers
print("="*80)
print("STEP 4: Finding test functions without markers")
print("="*80)
print()

tests_without_markers = []
tests_with_markers = []
tests_with_multiple_markers = []

# Scan tests/ directory
for test_file in test_files:
    try:
        content = test_file.read_text(encoding='utf-8')
        rel_path = str(test_file.relative_to(project_root))
        
        test_funcs = test_func_pattern.findall(content)
        
        for test_func in test_funcs:
            func_pattern = re.compile(
                rf'def\s+{re.escape(test_func)}.*?(?=def\s+test_|\Z)',
                re.DOTALL
            )
            match = func_pattern.search(content)
            
            if match:
                func_content = match.group(0)
                has_xray = xray_pattern.search(func_content)
                has_jira = jira_pattern.search(func_content)
                
                if not has_xray and not has_jira:
                    # Check if it's a helper function or unit test
                    is_helper = any(keyword in test_func.lower() for keyword in ['summary', 'helper', 'util', 'fixture'])
                    is_unit = 'unit' in rel_path.lower()
                    
                    if not is_helper and not is_unit:
                        tests_without_markers.append((rel_path, test_func))
                else:
                    # Check for multiple markers
                    all_markers = xray_pattern.findall(func_content) + jira_pattern.findall(func_content)
                    marker_ids = set()
                    for match_str in all_markers:
                        test_ids = [tid.strip() for tid in match_str.split(',')]
                        marker_ids.update(test_ids)
                    
                    if len(marker_ids) > 1:
                        tests_with_multiple_markers.append((rel_path, test_func, list(marker_ids)))
                    else:
                        tests_with_markers.append((rel_path, test_func))
    except Exception as e:
        print(f"[WARNING] Could not read {test_file}: {e}")

# Scan files outside tests/
for test_file in outside_test_files:
    if test_file.exists():
        try:
            content = test_file.read_text(encoding='utf-8')
            rel_path = str(test_file.relative_to(project_root))
            
            test_funcs = test_func_pattern.findall(content)
            
            for test_func in test_funcs:
                func_pattern = re.compile(
                    rf'def\s+{re.escape(test_func)}.*?(?=def\s+test_|\Z)',
                    re.DOTALL
                )
                match = func_pattern.search(content)
                
                if match:
                    func_content = match.group(0)
                    has_xray = xray_pattern.search(func_content)
                    has_jira = jira_pattern.search(func_content)
                    
                    if not has_xray and not has_jira:
                        tests_without_markers.append((rel_path, test_func))
                    else:
                        all_markers = xray_pattern.findall(func_content) + jira_pattern.findall(func_content)
                        marker_ids = set()
                        for match_str in all_markers:
                            test_ids = [tid.strip() for tid in match_str.split(',')]
                            marker_ids.update(test_ids)
                        
                        if len(marker_ids) > 1:
                            tests_with_multiple_markers.append((rel_path, test_func, list(marker_ids)))
                        else:
                            tests_with_markers.append((rel_path, test_func))
        except Exception as e:
            print(f"[WARNING] Could not read {test_file}: {e}")

print(f"Test functions WITHOUT markers: {len(tests_without_markers)}")
print(f"Test functions WITH markers: {len(tests_with_markers)}")
print(f"Test functions with MULTIPLE markers: {len(tests_with_multiple_markers)}")
print()

# 5. Find extra test IDs
print("="*80)
print("STEP 5: Finding extra test IDs")
print("="*80)
print()

if jira_tests:
    jira_test_ids = set(jira_tests.keys())
    extra_in_automation = automation_test_ids - jira_test_ids
    
    print(f"Test IDs in automation but NOT in Jira: {len(extra_in_automation)}")
    if extra_in_automation:
        print("Extra test IDs:")
        for test_id in sorted(extra_in_automation):
            print(f"  - {test_id}")
    print()

# 6. Generate detailed report
print("="*80)
print("STEP 6: Generating detailed report")
print("="*80)
print()

output_dir = Path("docs/04_testing/xray_mapping")
output_dir.mkdir(parents=True, exist_ok=True)
report_file = output_dir / "PHASE1_ANALYSIS_REPORT.md"

with open(report_file, 'w', encoding='utf-8') as f:
    f.write("# Phase 1: Analysis & Prioritization Report\n\n")
    f.write(f"**Date:** 2025-11-09\n")
    f.write(f"**Status:** Complete ✅\n\n")
    f.write("---\n\n")
    
    # Missing tests
    if jira_tests and missing_in_automation:
        f.write("## 1. Missing Tests in Automation (37 tests)\n\n")
        f.write("### By Category:\n\n")
        for category, tests in sorted(missing_by_category.items()):
            f.write(f"### {category} Tests ({len(tests)} tests)\n\n")
            f.write("| # | Test ID | Summary | Status | Priority | Test Type |\n")
            f.write("|---|---------|---------|--------|----------|-----------|\n")
            for i, (test_id, test) in enumerate(tests, 1):
                summary = test['summary'].replace('|', '\\|')[:60]
                status = test['status']
                priority = test.get('priority', 'N/A')
                test_type = test.get('test_type', 'N/A')
                f.write(f"| {i} | {test_id} | {summary} | {status} | {priority} | {test_type} |\n")
            f.write("\n")
    
    # Test functions without markers
    f.write("## 2. Test Functions Without Markers (204 functions)\n\n")
    f.write("### Summary:\n\n")
    f.write(f"- Total test functions without markers: {len(tests_without_markers)}\n")
    f.write(f"- Total test functions with markers: {len(tests_with_markers)}\n")
    f.write(f"- Total test functions with multiple markers: {len(tests_with_multiple_markers)}\n\n")
    
    # Categorize by file location
    by_location = defaultdict(list)
    for file_path, test_func in tests_without_markers:
        if 'integration' in file_path.lower():
            category = 'Integration'
        elif 'infrastructure' in file_path.lower():
            category = 'Infrastructure'
        elif 'data_quality' in file_path.lower():
            category = 'Data Quality'
        elif 'security' in file_path.lower():
            category = 'Security'
        elif 'performance' in file_path.lower():
            category = 'Performance'
        elif 'load' in file_path.lower():
            category = 'Load'
        elif 'ui' in file_path.lower():
            category = 'UI'
        else:
            category = 'Other'
        
        by_location[category].append((file_path, test_func))
    
    f.write("### By Category:\n\n")
    for category, tests in sorted(by_location.items()):
        f.write(f"### {category} Tests ({len(tests)} functions)\n\n")
        f.write("| # | File | Test Function |\n")
        f.write("|---|------|---------------|\n")
        for i, (file_path, test_func) in enumerate(tests, 1):
            f.write(f"| {i} | `{file_path}` | `{test_func}` |\n")
        f.write("\n")
    
    # Multiple markers
    if tests_with_multiple_markers:
        f.write("## 3. Test Functions With Multiple Markers\n\n")
        f.write("| # | File | Test Function | Test IDs |\n")
        f.write("|---|------|---------------|----------|\n")
        for i, (file_path, test_func, test_ids) in enumerate(tests_with_multiple_markers, 1):
            test_ids_str = ", ".join(test_ids)
            f.write(f"| {i} | `{file_path}` | `{test_func}` | {test_ids_str} |\n")
        f.write("\n")
    
    # Extra test IDs
    if jira_tests and extra_in_automation:
        f.write("## 4. Test IDs in Automation but NOT in Jira\n\n")
        f.write(f"**Total:** {len(extra_in_automation)}\n\n")
        for test_id in sorted(extra_in_automation):
            f.write(f"- {test_id}\n")
        f.write("\n")

print(f"Report saved to: {report_file}")
print()

# Summary
print("="*80)
print("PHASE 1 SUMMARY")
print("="*80)
print()
print(f"1. Missing tests in automation: {len(missing_in_automation) if jira_tests else 'N/A'}")
print(f"2. Test functions without markers: {len(tests_without_markers)}")
print(f"3. Test functions with multiple markers: {len(tests_with_multiple_markers)}")
print(f"4. Extra test IDs in automation: {len(extra_in_automation) if jira_tests else 'N/A'}")
print()

