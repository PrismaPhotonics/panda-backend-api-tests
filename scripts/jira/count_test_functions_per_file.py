"""Count test functions per test file"""
import sys
import re
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Counting Test Functions Per File")
print("="*80)
print()

tests_dir = project_root / "tests"

# Pattern to find test functions
test_func_pattern = re.compile(r'def\s+(test_\w+)')

# Count test functions per file
test_files = list(tests_dir.rglob('test_*.py'))
file_test_counts = []

for test_file in test_files:
    try:
        content = test_file.read_text(encoding='utf-8')
        rel_path = str(test_file.relative_to(project_root))
        
        # Find all test functions
        test_funcs = test_func_pattern.findall(content)
        
        file_test_counts.append((rel_path, len(test_funcs)))
    
    except Exception as e:
        print(f"[WARNING] Could not read {test_file}: {e}")

# Sort by count
file_test_counts.sort(key=lambda x: x[1], reverse=True)

print("="*80)
print("Test Functions Per File (sorted by count)")
print("="*80)
print()

print("| # | File | Test Functions Count |")
print("|---|------|---------------------|")

for i, (file_path, count) in enumerate(file_test_counts, 1):
    print(f"| {i} | `{file_path}` | {count} |")

print()
print("="*80)
print("Statistics")
print("="*80)
print()

total_test_functions = sum(count for _, count in file_test_counts)
total_files = len(file_test_counts)

print(f"Total test files: {total_files}")
print(f"Total test functions: {total_test_functions}")
print(f"Average test functions per file: {total_test_functions / total_files:.1f}")
print()

# Distribution
count_distribution = defaultdict(int)
for _, count in file_test_counts:
    count_distribution[count] += 1

print("Distribution:")
print("| Functions per file | Number of files |")
print("|-------------------|-----------------|")
for count in sorted(count_distribution.keys()):
    files = count_distribution[count]
    print(f"| {count} | {files} |")

print()
print("Files with most test functions:")
print("| # | File | Count |")
print("|---|------|-------|")
for i, (file_path, count) in enumerate(file_test_counts[:20], 1):
    print(f"| {i} | `{file_path}` | {count} |")

print()
print("Files with fewest test functions:")
print("| # | File | Count |")
print("|---|------|-------|")
for i, (file_path, count) in enumerate(file_test_counts[-20:], 1):
    print(f"| {i} | `{file_path}` | {count} |")

