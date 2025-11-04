#!/usr/bin/env python3
"""Count Xray mapping coverage"""

import re
from pathlib import Path

# Count all test functions
all_tests = 0
tests_with_xray = 0

# Exclude conftest files from the "real" test count
excluded_files = ['conftest.py', 'conftest_xray.py', '__init__.py']

for test_file in Path('tests').rglob('*.py'):
    if any(excluded in str(test_file) for excluded in excluded_files):
        continue
    
    content = test_file.read_text(encoding='utf-8')
    
    # Count test functions
    test_functions = re.findall(r'^\s*def\s+test_', content, re.MULTILINE)
    all_tests += len(test_functions)
    
    # Count tests with Xray markers
    for match in test_functions:
        # Find the function definition
        func_name = match.strip().split('test_')[1].split('(')[0]
        
        # Look for xray marker before this function
        func_pattern = rf'{re.escape(match)}.*?def test_{re.escape(func_name)}'
        func_match = re.search(func_pattern, content, re.DOTALL)
        
        if func_match:
            func_block = func_match.group(0)
            if '@pytest.mark.xray' in func_block:
                tests_with_xray += 1

print(f"Total test functions: {all_tests}")
print(f"Tests with Xray markers: {tests_with_xray}")
print(f"Tests without Xray markers: {all_tests - tests_with_xray}")
print(f"Coverage: {tests_with_xray / all_tests * 100:.1f}%")

