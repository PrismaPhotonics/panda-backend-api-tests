"""Verify the scan results - detailed check"""
import sys
import re
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("VERIFYING SCAN RESULTS - Detailed Check")
print("="*80)
print()

tests_dir = project_root / "tests"

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')
test_func_pattern = re.compile(r'def\s+(test_\w+)')

# Detailed statistics
all_markers = defaultdict(list)
all_test_functions = []
files_with_markers = set()
files_without_markers = set()
test_functions_with_markers = []
test_functions_without_markers = []

print("Scanning all test files in detail...")
print()

test_files = list(tests_dir.rglob('test_*.py'))
print(f"Total test files found: {len(test_files)}")
print()

for test_file in test_files:
    try:
        content = test_file.read_text(encoding='utf-8')
        rel_path = str(test_file.relative_to(project_root))
        
        # Find all test functions
        test_funcs = test_func_pattern.findall(content)
        
        # Find all markers
        xray_markers = []
        jira_markers = []
        
        for line_num, line in enumerate(content.splitlines(), 1):
            # Xray markers
            xray_matches = xray_pattern.findall(line)
            for match in xray_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        xray_markers.append((test_id, line_num))
                        all_markers[test_id].append((rel_path, line_num))
            
            # Jira markers
            jira_matches = jira_pattern.findall(line)
            for match in jira_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        jira_markers.append((test_id, line_num))
        
        # Check each test function
        for test_func in test_funcs:
            all_test_functions.append((rel_path, test_func))
            
            # Find the test function in the file
            func_pattern = re.compile(rf'def\s+{re.escape(test_func)}.*?(?=def\s+test_|\Z)', re.DOTALL)
            match = func_pattern.search(content)
            
            if match:
                func_content = match.group(0)
                # Check if this function has markers
                has_xray = xray_pattern.search(func_content)
                has_jira = jira_pattern.search(func_content)
                
                if has_xray or has_jira:
                    test_functions_with_markers.append((rel_path, test_func))
                    files_with_markers.add(rel_path)
                else:
                    test_functions_without_markers.append((rel_path, test_func))
                    if not xray_markers and not jira_markers:
                        files_without_markers.add(rel_path)
            else:
                # Can't find function content, assume no markers
                test_functions_without_markers.append((rel_path, test_func))
        
        if xray_markers or jira_markers:
            files_with_markers.add(rel_path)
        elif test_funcs:
            files_without_markers.add(rel_path)
    
    except Exception as e:
        print(f"[ERROR] Failed to read {test_file}: {e}")

print("="*80)
print("DETAILED STATISTICS")
print("="*80)
print()
print(f"Total test files: {len(test_files)}")
print(f"Files with markers: {len(files_with_markers)}")
print(f"Files without markers: {len(files_without_markers)}")
print()
print(f"Total test functions: {len(all_test_functions)}")
print(f"Test functions with markers: {len(test_functions_with_markers)}")
print(f"Test functions without markers: {len(test_functions_without_markers)}")
print()
print(f"Total unique test IDs found: {len(all_markers)}")
print()

# Show some examples
print("="*80)
print("SAMPLE: Test functions WITHOUT markers (first 20)")
print("="*80)
for i, (file_path, test_func) in enumerate(test_functions_without_markers[:20], 1):
    print(f"{i:3}. {file_path}::{test_func}")

if len(test_functions_without_markers) > 20:
    print(f"... and {len(test_functions_without_markers) - 20} more")
print()

print("="*80)
print("SAMPLE: Test functions WITH markers (first 20)")
print("="*80)
for i, (file_path, test_func) in enumerate(test_functions_with_markers[:20], 1):
    # Find which test IDs are in this function
    test_ids = []
    for test_id, locations in all_markers.items():
        for loc_file, loc_line in locations:
            if loc_file == file_path:
                test_ids.append(test_id)
                break
    
    unique_test_ids = list(set(test_ids))[:3]
    test_ids_str = ", ".join(unique_test_ids)
    if len(set(test_ids)) > 3:
        test_ids_str += f" ... ({len(set(test_ids))} total)"
    
    print(f"{i:3}. {file_path}::{test_func} -> {test_ids_str}")

if len(test_functions_with_markers) > 20:
    print(f"... and {len(test_functions_with_markers) - 20} more")
print()

print("="*80)
print("SAMPLE: Files WITHOUT any markers")
print("="*80)
for i, file_path in enumerate(sorted(list(files_without_markers))[:20], 1):
    # Count test functions in this file
    func_count = sum(1 for f, _ in all_test_functions if f == file_path)
    print(f"{i:3}. {file_path} ({func_count} test functions)")

if len(files_without_markers) > 20:
    print(f"... and {len(files_without_markers) - 20} more files")
print()

print("="*80)
print("VERIFICATION COMPLETE")
print("="*80)

