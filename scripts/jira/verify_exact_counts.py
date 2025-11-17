"""Verify exact counts - Triple check"""
import sys
import re
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("TRIPLE CHECK: Verifying Exact Counts")
print("="*80)
print()

tests_dir = project_root / "tests"

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')
test_func_pattern = re.compile(r'def\s+(test_\w+)')

# Check 1: Count unique test IDs
print("="*80)
print("CHECK 1: Counting unique test IDs in automation")
print("="*80)
print()

automation_test_ids = set()
test_files = list(tests_dir.rglob('test_*.py'))

for test_file in test_files:
    try:
        content = test_file.read_text(encoding='utf-8')
        for line in content.splitlines():
            # Xray markers
            xray_matches = xray_pattern.findall(line)
            for match in xray_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        automation_test_ids.add(test_id)
            
            # Jira markers
            jira_matches = jira_pattern.findall(line)
            for match in jira_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        automation_test_ids.add(test_id)
    except Exception as e:
        print(f"[WARNING] Could not read {test_file}: {e}")

print(f"CHECK 1 RESULT: {len(automation_test_ids)} unique test IDs in automation")
print(f"Sample IDs: {sorted(list(automation_test_ids))[:10]}")
print()

# Check 2: Count test functions without markers
print("="*80)
print("CHECK 2: Counting test functions without markers")
print("="*80)
print()

tests_without_markers = []
tests_with_markers = []

for test_file in test_files:
    try:
        content = test_file.read_text(encoding='utf-8')
        rel_path = str(test_file.relative_to(project_root))
        
        # Find all test functions
        test_funcs = test_func_pattern.findall(content)
        
        for test_func in test_funcs:
            # Find the function content
            func_pattern = re.compile(
                rf'def\s+{re.escape(test_func)}.*?(?=def\s+test_|\Z)',
                re.DOTALL
            )
            match = func_pattern.search(content)
            
            if match:
                func_content = match.group(0)
                
                # Check for markers in this function
                has_xray = xray_pattern.search(func_content)
                has_jira = jira_pattern.search(func_content)
                
                if not has_xray and not has_jira:
                    tests_without_markers.append((rel_path, test_func))
                else:
                    tests_with_markers.append((rel_path, test_func))
    except Exception as e:
        print(f"[WARNING] Could not read {test_file}: {e}")

print(f"CHECK 2 RESULT: {len(tests_without_markers)} test functions WITHOUT markers")
print(f"CHECK 2 RESULT: {len(tests_with_markers)} test functions WITH markers")
print(f"Total test functions: {len(tests_without_markers) + len(tests_with_markers)}")
print()

# Check 3: Categorize tests without markers
print("="*80)
print("CHECK 3: Categorizing tests without markers")
print("="*80)
print()

# Exclude unit tests and helper functions
real_tests_without_markers = []
unit_tests = []
helper_functions = []

for file_path, test_func in tests_without_markers:
    # Check if unit test
    if 'unit' in file_path.lower():
        unit_tests.append((file_path, test_func))
    # Check if helper function
    elif any(keyword in test_func.lower() for keyword in ['summary', 'helper', 'util', 'fixture']):
        helper_functions.append((file_path, test_func))
    else:
        real_tests_without_markers.append((file_path, test_func))

print(f"CHECK 3 RESULT:")
print(f"  Unit tests (excluded): {len(unit_tests)}")
print(f"  Helper functions (excluded): {len(helper_functions)}")
print(f"  Real test functions WITHOUT markers: {len(real_tests_without_markers)}")
print()

# Categorize by type
by_category = defaultdict(list)
for file_path, test_func in real_tests_without_markers:
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
    else:
        category = 'Other'
    
    by_category[category].append((file_path, test_func))

print("Breakdown by category:")
for category, tests in sorted(by_category.items()):
    print(f"  {category}: {len(tests)} functions")
print()

# Final summary
print("="*80)
print("FINAL VERIFIED SUMMARY")
print("="*80)
print()
print(f"1. Unique test IDs in automation: {len(automation_test_ids)}")
print(f"2. Test functions WITHOUT markers: {len(tests_without_markers)}")
print(f"   - Unit tests (excluded): {len(unit_tests)}")
print(f"   - Helper functions (excluded): {len(helper_functions)}")
print(f"   - Real test functions (NEED markers): {len(real_tests_without_markers)}")
print(f"3. Test functions WITH markers: {len(tests_with_markers)}")
print(f"4. Total test functions: {len(tests_without_markers) + len(tests_with_markers)}")
print()

