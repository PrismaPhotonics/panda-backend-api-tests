"""Analyze tests without markers - understand why they don't have markers"""
import sys
import re
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Analyzing Tests Without Markers")
print("="*80)
print()

tests_dir = project_root / "tests"

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')
test_func_pattern = re.compile(r'def\s+(test_\w+)')

# Categorize tests
unit_tests = []
integration_tests = []
infrastructure_tests = []
data_quality_tests = []
security_tests = []
performance_tests = []
load_tests = []
other_tests = []

tests_without_markers_by_category = defaultdict(list)

test_files = list(tests_dir.rglob('test_*.py'))

for test_file in test_files:
    try:
        content = test_file.read_text(encoding='utf-8')
        rel_path = str(test_file.relative_to(project_root))
        
        # Determine category based on path
        if 'unit' in rel_path.lower():
            category = 'unit'
        elif 'integration' in rel_path.lower():
            category = 'integration'
        elif 'infrastructure' in rel_path.lower():
            category = 'infrastructure'
        elif 'data_quality' in rel_path.lower():
            category = 'data_quality'
        elif 'security' in rel_path.lower():
            category = 'security'
        elif 'performance' in rel_path.lower():
            category = 'performance'
        elif 'load' in rel_path.lower():
            category = 'load'
        else:
            category = 'other'
        
        # Find all test functions
        test_funcs = test_func_pattern.findall(content)
        
        # Check each test function
        for test_func in test_funcs:
            # Find the test function content
            func_pattern = re.compile(
                rf'def\s+{re.escape(test_func)}.*?(?=def\s+test_|\Z)',
                re.DOTALL
            )
            match = func_pattern.search(content)
            
            if match:
                func_content = match.group(0)
                
                # Check if function has markers
                has_xray = xray_pattern.search(func_content)
                has_jira = jira_pattern.search(func_content)
                
                if not has_xray and not has_jira:
                    # No markers - categorize
                    tests_without_markers_by_category[category].append((rel_path, test_func))
    
    except Exception as e:
        print(f"[WARNING] Could not read {test_file}: {e}")

print("="*80)
print("Tests Without Markers by Category")
print("="*80)
print()

total_without_markers = 0
for category, tests in sorted(tests_without_markers_by_category.items()):
    print(f"{category.upper()}: {len(tests)} test functions without markers")
    total_without_markers += len(tests)
    
    # Show first 5 examples
    print("  Examples:")
    for file_path, test_func in tests[:5]:
        print(f"    - {file_path}::{test_func}")
    if len(tests) > 5:
        print(f"    ... and {len(tests) - 5} more")
    print()

print(f"Total: {total_without_markers} test functions without markers")
print()

# Check if these are helper functions or real tests
print("="*80)
print("Checking if these are helper functions or real tests")
print("="*80)
print()

helper_keywords = ['summary', 'helper', 'util', 'fixture', 'setup', 'teardown']
real_test_keywords = ['test_', 'verify', 'check', 'validate', 'assert']

helper_functions = []
real_test_functions = []

for category, tests in tests_without_markers_by_category.items():
    for file_path, test_func in tests:
        # Check if it's a helper function
        is_helper = any(keyword in test_func.lower() for keyword in helper_keywords)
        
        if is_helper:
            helper_functions.append((category, file_path, test_func))
        else:
            real_test_functions.append((category, file_path, test_func))

print(f"Helper functions (probably don't need markers): {len(helper_functions)}")
print(f"Real test functions (probably need markers): {len(real_test_functions)}")
print()

print("Sample helper functions:")
for category, file_path, test_func in helper_functions[:10]:
    print(f"  {category}: {file_path}::{test_func}")

print()
print("Sample real test functions without markers:")
for category, file_path, test_func in real_test_functions[:20]:
    print(f"  {category}: {file_path}::{test_func}")

print()
print("="*80)
print("Analysis by Test Type")
print("="*80)
print()

# Check if unit tests should have markers
unit_tests_without = tests_without_markers_by_category.get('unit', [])
integration_tests_without = tests_without_markers_by_category.get('integration', [])
infrastructure_tests_without = tests_without_markers_by_category.get('infrastructure', [])

print(f"Unit tests without markers: {len(unit_tests_without)}")
print("  Note: Unit tests typically don't need Xray markers (they test code, not requirements)")
print()
print(f"Integration tests without markers: {len(integration_tests_without)}")
print("  Note: Integration tests SHOULD have Xray markers")
print()
print(f"Infrastructure tests without markers: {len(infrastructure_tests_without)}")
print("  Note: Infrastructure tests SHOULD have Xray markers")
print()

# Check specific files
print("="*80)
print("Checking specific files for context")
print("="*80)
print()

sample_files = [
    'tests/infrastructure/test_mongodb_monitoring_agent.py',
    'tests/unit/test_models_validation.py',
    'tests/infrastructure/test_basic_connectivity.py',
]

for file_path in sample_files:
    full_path = project_root / file_path
    if full_path.exists():
        print(f"File: {file_path}")
        content = full_path.read_text(encoding='utf-8')
        
        # Count test functions
        test_funcs = test_func_pattern.findall(content)
        print(f"  Total test functions: {len(test_funcs)}")
        
        # Count markers
        xray_markers = len(xray_pattern.findall(content))
        jira_markers = len(jira_pattern.findall(content))
        print(f"  Xray markers: {xray_markers}")
        print(f"  Jira markers: {jira_markers}")
        
        # Check if it's a unit test file
        if 'unit' in file_path:
            print(f"  Type: Unit test (typically don't need Xray markers)")
        elif 'infrastructure' in file_path:
            print(f"  Type: Infrastructure test (SHOULD have Xray markers)")
        else:
            print(f"  Type: Other")
        print()

