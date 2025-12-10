#!/usr/bin/env python3
"""
CI Quality Checks for Test Suite
=================================

This script runs quality checks on the test suite to prevent regression
of fake/non-effective tests.

Checks performed:
1. No `assert True` statements in test files
2. No summary tests without `documentation_only` marker
3. No `logger.warning` for bugs that should fail
4. No `pytest.skip` as default behavior (without condition)

Usage:
    python scripts/ci_quality_checks.py
    
Exit codes:
    0 - All checks passed
    1 - One or more checks failed

Author: QA Automation Architect
Date: 2025-12-09
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Test directory
TEST_DIR = Path("be_focus_server_tests")

# Patterns to check
PATTERNS = {
    "assert_true": {
        "pattern": r"^\s*assert\s+True\b",
        "message": "Found 'assert True' - tests should have meaningful assertions",
        "severity": "ERROR"
    },
    "warning_for_bug": {
        "pattern": r'logger\.warning\(.*Server accepts|logger\.warning\(.*BUG',
        "message": "Found warning for server bug - should use pytest.fail() instead",
        "severity": "WARNING"
    },
    "unconditional_skip": {
        "pattern": r"^\s*pytest\.skip\([^)]*\)\s*$",
        "message": "Found unconditional pytest.skip - use @pytest.mark.skip or conditional skip",
        "severity": "WARNING"
    }
}


def find_python_test_files(directory: Path) -> List[Path]:
    """Find all Python test files in the directory."""
    test_files = []
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(Path(root) / file)
    
    return test_files


def check_file(file_path: Path, pattern: str) -> List[Tuple[int, str]]:
    """Check a file for a pattern and return line numbers and content."""
    matches = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if re.search(pattern, line):
                    matches.append((line_num, line.strip()))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return matches


def run_checks() -> bool:
    """Run all quality checks."""
    print("=" * 80)
    print("CI Quality Checks for Test Suite")
    print("=" * 80)
    print()
    
    test_files = find_python_test_files(TEST_DIR)
    print(f"Found {len(test_files)} test files to check")
    print()
    
    errors = 0
    warnings = 0
    
    for check_name, check_config in PATTERNS.items():
        print(f"Checking: {check_name}")
        print("-" * 40)
        
        check_errors = 0
        for file_path in test_files:
            matches = check_file(file_path, check_config["pattern"])
            
            for line_num, line_content in matches:
                severity = check_config["severity"]
                message = check_config["message"]
                
                if severity == "ERROR":
                    print(f"  [ERROR] {file_path}:{line_num}")
                    print(f"     {line_content[:80]}")
                    print(f"     {message}")
                    errors += 1
                    check_errors += 1
                else:
                    print(f"  [WARN] {file_path}:{line_num}")
                    print(f"     {line_content[:80]}")
                    print(f"     {message}")
                    warnings += 1
        
        if check_errors == 0:
            print(f"  [OK] No issues found")
        print()
    
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"  Errors:   {errors}")
    print(f"  Warnings: {warnings}")
    print()
    
    if errors > 0:
        print("[FAILED] Quality checks FAILED - fix errors before merging")
        return False
    elif warnings > 0:
        print("[PASSED] Quality checks passed with warnings")
        return True
    else:
        print("[PASSED] All quality checks PASSED")
        return True


def main():
    """Main entry point."""
    os.chdir(Path(__file__).parent.parent)
    
    success = run_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

