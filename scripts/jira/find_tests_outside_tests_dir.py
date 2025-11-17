"""Find all test files outside tests/ directory"""
import sys
import re
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Finding Test Files Outside tests/ Directory")
print("="*80)
print()

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')
test_func_pattern = re.compile(r'def\s+(test_\w+)')

# Find all Python files with "test" in name
test_files_outside = []
test_files_in_tests = []

# Exclude certain directories
exclude_dirs = {
    '__pycache__',
    '.git',
    'node_modules',
    '.pytest_cache',
    'venv',
    'env',
    '.venv',
    'focus_server_automation_framework.egg-info',
    'ron_project',  # Different project
}

# Find all test_*.py files
for test_file in project_root.rglob('test_*.py'):
    # Skip excluded directories
    if any(excluded in test_file.parts for excluded in exclude_dirs):
        continue
    
    # Check if it's in tests/ directory
    if 'tests' in test_file.parts:
        # Check if it's directly in tests/ or in a subdirectory
        tests_index = test_file.parts.index('tests')
        if tests_index == len(test_file.parts) - 2:  # tests/file.py
            test_files_in_tests.append(test_file)
        elif tests_index < len(test_file.parts) - 2:  # tests/subdir/file.py
            test_files_in_tests.append(test_file)
    else:
        test_files_outside.append(test_file)

# Also find *test*.py files (but not in tests/)
for test_file in project_root.rglob('*test*.py'):
    # Skip excluded directories
    if any(excluded in test_file.parts for excluded in exclude_dirs):
        continue
    
    # Skip if already found
    if test_file in test_files_outside:
        continue
    
    # Skip if in tests/ directory
    if 'tests' in test_file.parts:
        continue
    
    # Skip if it's a script that uses "test" in a different context
    # (like test_jira_integration.py which is a test script, not a test file)
    if 'scripts' in test_file.parts and test_file.name.startswith('test_'):
        # This is a test script, include it
        test_files_outside.append(test_file)

print(f"Found {len(test_files_outside)} test files OUTSIDE tests/ directory")
print(f"Found {len(test_files_in_tests)} test files IN tests/ directory")
print()

# Analyze test files outside tests/
print("="*80)
print("Analyzing Test Files Outside tests/ Directory")
print("="*80)
print()

test_files_with_markers = []
test_files_without_markers = []
test_functions_count = defaultdict(int)
test_ids_found = set()

for test_file in test_files_outside:
    try:
        content = test_file.read_text(encoding='utf-8')
        rel_path = str(test_file.relative_to(project_root))
        
        # Find test functions
        test_funcs = test_func_pattern.findall(content)
        test_functions_count[rel_path] = len(test_funcs)
        
        # Find markers
        has_xray = xray_pattern.search(content)
        has_jira = jira_pattern.search(content)
        
        # Extract test IDs
        for line in content.splitlines():
            xray_matches = xray_pattern.findall(line)
            for match in xray_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        test_ids_found.add(test_id)
            
            jira_matches = jira_pattern.findall(line)
            for match in jira_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        test_ids_found.add(test_id)
        
        if has_xray or has_jira:
            test_files_with_markers.append((rel_path, len(test_funcs), has_xray is not None, has_jira is not None))
        else:
            test_files_without_markers.append((rel_path, len(test_funcs)))
    except Exception as e:
        print(f"[WARNING] Could not read {test_file}: {e}")

print(f"Test files WITH markers: {len(test_files_with_markers)}")
print(f"Test files WITHOUT markers: {len(test_files_without_markers)}")
print(f"Total test IDs found: {len(test_ids_found)}")
print()

if test_files_with_markers:
    print("="*80)
    print("Test Files WITH Markers (Outside tests/)")
    print("="*80)
    print()
    print("| # | File | Test Functions | Has Xray | Has Jira |")
    print("|---|------|----------------|----------|----------|")
    for i, (file_path, func_count, has_xray, has_jira) in enumerate(test_files_with_markers, 1):
        print(f"| {i} | `{file_path}` | {func_count} | {'✅' if has_xray else '❌'} | {'✅' if has_jira else '❌'} |")
    print()

if test_files_without_markers:
    print("="*80)
    print("Test Files WITHOUT Markers (Outside tests/)")
    print("="*80)
    print()
    print("| # | File | Test Functions |")
    print("|---|------|----------------|")
    for i, (file_path, func_count) in enumerate(test_files_without_markers, 1):
        print(f"| {i} | `{file_path}` | {func_count} |")
    print()

if test_ids_found:
    print("="*80)
    print(f"Test IDs Found in Files Outside tests/ ({len(test_ids_found)} total)")
    print("="*80)
    print()
    for test_id in sorted(test_ids_found):
        print(f"  - {test_id}")
    print()

# Summary
print("="*80)
print("SUMMARY")
print("="*80)
print()
print(f"Total test files outside tests/: {len(test_files_outside)}")
print(f"  - With markers: {len(test_files_with_markers)}")
print(f"  - Without markers: {len(test_files_without_markers)}")
print(f"Total test functions outside tests/: {sum(test_functions_count.values())}")
print(f"Total test IDs found: {len(test_ids_found)}")
print()

# Generate report file
output_dir = Path("docs/04_testing/xray_mapping")
output_dir.mkdir(parents=True, exist_ok=True)
report_file = output_dir / "TESTS_OUTSIDE_TESTS_DIR.md"

with open(report_file, 'w', encoding='utf-8') as f:
    f.write("# Test Files Outside tests/ Directory\n\n")
    f.write(f"**Date:** 2025-11-09\n")
    f.write(f"**Total Files Found:** {len(test_files_outside)}\n\n")
    f.write("---\n\n")
    
    if test_files_with_markers:
        f.write("## Test Files WITH Markers\n\n")
        f.write("| # | File | Test Functions | Has Xray | Has Jira |\n")
        f.write("|---|------|----------------|----------|----------|\n")
        for i, (file_path, func_count, has_xray, has_jira) in enumerate(test_files_with_markers, 1):
            f.write(f"| {i} | `{file_path}` | {func_count} | {'✅' if has_xray else '❌'} | {'✅' if has_jira else '❌'} |\n")
        f.write("\n")
    
    if test_files_without_markers:
        f.write("## Test Files WITHOUT Markers\n\n")
        f.write("| # | File | Test Functions |\n")
        f.write("|---|------|----------------|\n")
        for i, (file_path, func_count) in enumerate(test_files_without_markers, 1):
            f.write(f"| {i} | `{file_path}` | {func_count} |\n")
        f.write("\n")
    
    if test_ids_found:
        f.write(f"## Test IDs Found ({len(test_ids_found)} total)\n\n")
        for test_id in sorted(test_ids_found):
            f.write(f"- {test_id}\n")
        f.write("\n")
    
    f.write("## Summary\n\n")
    f.write(f"- Total test files outside tests/: {len(test_files_outside)}\n")
    f.write(f"  - With markers: {len(test_files_with_markers)}\n")
    f.write(f"  - Without markers: {len(test_files_without_markers)}\n")
    f.write(f"- Total test functions: {sum(test_functions_count.values())}\n")
    f.write(f"- Total test IDs found: {len(test_ids_found)}\n")

print(f"Report saved to: {report_file}")

