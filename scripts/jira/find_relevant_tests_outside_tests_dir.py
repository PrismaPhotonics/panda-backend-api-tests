"""Find RELEVANT test files outside tests/ directory - Only Focus Server tests"""
import sys
import re
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Finding RELEVANT Test Files Outside tests/ Directory")
print("(Only Focus Server tests, excluding utility scripts)")
print("="*80)
print()

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')
test_func_pattern = re.compile(r'def\s+(test_\w+)')

# Exclude directories
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
    'pz',  # PZ project (not Focus Server)
    'external/pz',  # PZ project (not Focus Server)
}

# Exclude utility scripts (not Focus Server tests)
exclude_files = {
    'scripts/test_jira_integration.py',  # Jira utility test
    'scripts/test_jira_report_generation.py',  # Jira utility test
    'scripts/test_jira_report_generation.py',  # Jira utility test
    'src/reporting/test_report_generator.py',  # Reporting utility (not a test file)
}

# Find all test_*.py files
test_files_outside = []

for test_file in project_root.rglob('test_*.py'):
    # Skip excluded directories
    if any(excluded in test_file.parts for excluded in exclude_dirs):
        continue
    
    # Skip if in tests/ directory
    if 'tests' in test_file.parts:
        continue
    
    # Skip excluded files
    rel_path = str(test_file.relative_to(project_root))
    if rel_path in exclude_files:
        continue
    
    # Check if it's a Focus Server test by reading content
    try:
        content = test_file.read_text(encoding='utf-8')
        
        # Check if it mentions Focus Server, API, or relevant keywords
        focus_keywords = [
            'focus',
            'focus-server',
            'focus_server',
            'focusserver',
            '/configure',
            '/channels',
            '/live_metadata',
            '/recordings',
            'waterfall',
            'singlechannel',
            'spectrogram',
            'mongodb',
            'rabbitmq',
            'kubernetes',
            'k8s',
            'panda',
            'prisma',
        ]
        
        content_lower = content.lower()
        has_focus_keywords = any(keyword in content_lower for keyword in focus_keywords)
        
        # Exclude if it's clearly a utility script
        utility_keywords = [
            'jira integration',
            'jira report',
            'test utility',
            'utility test',
        ]
        
        is_utility = any(keyword in content_lower for keyword in utility_keywords)
        
        if has_focus_keywords and not is_utility:
            test_files_outside.append(test_file)
    except Exception as e:
        print(f"[WARNING] Could not read {test_file}: {e}")

print(f"Found {len(test_files_outside)} RELEVANT test files outside tests/ directory")
print()

# Analyze test files
print("="*80)
print("Analyzing RELEVANT Test Files Outside tests/ Directory")
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
print("SUMMARY - RELEVANT TESTS ONLY")
print("="*80)
print()
print(f"Total RELEVANT test files outside tests/: {len(test_files_outside)}")
print(f"  - With markers: {len(test_files_with_markers)}")
print(f"  - Without markers: {len(test_files_without_markers)}")
print(f"Total test functions: {sum(test_functions_count.values())}")
print(f"Total test IDs found: {len(test_ids_found)}")
print()

# Generate report file
output_dir = Path("docs/04_testing/xray_mapping")
output_dir.mkdir(parents=True, exist_ok=True)
report_file = output_dir / "RELEVANT_TESTS_OUTSIDE_TESTS_DIR.md"

with open(report_file, 'w', encoding='utf-8') as f:
    f.write("# RELEVANT Test Files Outside tests/ Directory\n\n")
    f.write("**Date:** 2025-11-09\n")
    f.write("**Note:** Only Focus Server tests, excluding utility scripts\n")
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
    f.write(f"- Total RELEVANT test files outside tests/: {len(test_files_outside)}\n")
    f.write(f"  - With markers: {len(test_files_with_markers)}\n")
    f.write(f"  - Without markers: {len(test_files_without_markers)}\n")
    f.write(f"- Total test functions: {sum(test_functions_count.values())}\n")
    f.write(f"- Total test IDs found: {len(test_ids_found)}\n")
    
    f.write("\n## Excluded Files (Not Focus Server Tests)\n\n")
    f.write("- `scripts/test_jira_integration.py` - Jira utility test\n")
    f.write("- `scripts/test_jira_report_generation.py` - Jira utility test\n")
    f.write("- `src/reporting/test_report_generator.py` - Reporting utility (not a test file)\n")
    f.write("- All files in `pz/` and `external/pz/` - PZ project (not Focus Server)\n")

print(f"Report saved to: {report_file}")

