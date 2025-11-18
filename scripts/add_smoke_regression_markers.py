#!/usr/bin/env python3
"""
Script to add smoke and regression markers to all test files.

This script:
1. Identifies smoke tests (critical, fast tests)
2. Adds @pytest.mark.regression to all tests (except unit tests)
3. Adds @pytest.mark.smoke to critical smoke tests
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict

# Base directory
BASE_DIR = Path("be_focus_server_tests")

# Files/directories to skip
SKIP_PATTERNS = [
    "__pycache__",
    "unit",  # Unit tests don't need regression markers
    ".pyc",
]

# Smoke test patterns - files/classes that should be smoke tests
SMOKE_TEST_PATTERNS = [
    # Health check
    ("test_health_check.py", True),  # All tests in this file
    
    # Basic connectivity
    ("test_basic_connectivity.py", True),  # All tests
    ("test_external_connectivity.py", ["test_mongodb", "test_kubernetes", "test_ssh"]),  # Specific tests
    
    # Critical API endpoints
    ("test_api_endpoints_high_priority.py", True),  # All tests
    ("test_configure_endpoint.py", ["test_valid_configuration"]),  # Basic config test
    ("test_prelaunch_validations.py", ["test_port_availability"]),  # Port check
    
    # Infrastructure basic
    ("test_rabbitmq_connectivity.py", ["test_rabbitmq"]),  # Basic connectivity
]

# Files that should NOT have regression markers
NO_REGRESSION_PATTERNS = [
    "unit/",
]


def is_smoke_test(file_path: str, test_name: str) -> bool:
    """Check if a test should be marked as smoke test."""
    file_name = os.path.basename(file_path)
    
    for pattern, tests in SMOKE_TEST_PATTERNS:
        if pattern in file_name:
            if tests is True:
                return True
            elif isinstance(tests, list):
                for test_pattern in tests:
                    if test_pattern in test_name:
                        return True
    
    # Check for critical markers
    return False


def should_have_regression(file_path: str) -> bool:
    """Check if file should have regression markers."""
    for pattern in NO_REGRESSION_PATTERNS:
        if pattern in file_path:
            return False
    return True


def add_markers_to_file(file_path: Path) -> Tuple[int, int]:
    """Add smoke and regression markers to a test file."""
    smoke_added = 0
    regression_added = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Find all test functions
        test_pattern = r'(\s*)(@pytest\.mark\.[^\n]*\n)*(\s*)(def\s+test_\w+)'
        
        def add_markers(match):
            indent = match.group(1)
            existing_markers = match.group(2) or ""
            func_indent = match.group(3)
            func_def = match.group(4)
            test_name = re.search(r'test_\w+', func_def).group()
            
            markers_to_add = []
            
            # Check if should add regression
            if should_have_regression(str(file_path)):
                if "@pytest.mark.regression" not in existing_markers:
                    markers_to_add.append("@pytest.mark.regression")
                    nonlocal regression_added
                    regression_added += 1
            
            # Check if should add smoke
            if is_smoke_test(str(file_path), test_name):
                if "@pytest.mark.smoke" not in existing_markers:
                    markers_to_add.append("@pytest.mark.smoke")
                    nonlocal smoke_added
                    smoke_added += 1
            
            if markers_to_add:
                new_markers = "\n".join([f"{indent}{marker}" for marker in markers_to_add])
                if existing_markers:
                    return f"{indent}{existing_markers.rstrip()}\n{new_markers}\n{func_indent}{func_def}"
                else:
                    return f"{new_markers}\n{func_indent}{func_def}"
            
            return match.group(0)
        
        content = re.sub(test_pattern, add_markers, content, flags=re.MULTILINE)
        
        # Also check for test classes
        class_pattern = r'(\s*)(@pytest\.mark\.[^\n]*\n)*(\s*)(class\s+Test\w+)'
        
        def add_class_markers(match):
            indent = match.group(1)
            existing_markers = match.group(2) or ""
            class_indent = match.group(3)
            class_def = match.group(4)
            
            markers_to_add = []
            
            # Check if should add regression
            if should_have_regression(str(file_path)):
                if "@pytest.mark.regression" not in existing_markers:
                    markers_to_add.append("@pytest.mark.regression")
            
            if markers_to_add:
                new_markers = "\n".join([f"{indent}{marker}" for marker in markers_to_add])
                if existing_markers:
                    return f"{indent}{existing_markers.rstrip()}\n{new_markers}\n{class_indent}{class_def}"
                else:
                    return f"{new_markers}\n{class_indent}{class_def}"
            
            return match.group(0)
        
        content = re.sub(class_pattern, add_class_markers, content, flags=re.MULTILINE)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return smoke_added, regression_added
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0, 0


def main():
    """Main function."""
    total_smoke = 0
    total_regression = 0
    files_processed = 0
    
    # Find all test files
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip directories
        dirs[:] = [d for d in dirs if not any(pattern in d for pattern in SKIP_PATTERNS)]
        
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                file_path = Path(root) / file
                
                # Skip unit tests
                if "unit" in str(file_path):
                    continue
                
                smoke, regression = add_markers_to_file(file_path)
                total_smoke += smoke
                total_regression += regression
                files_processed += 1
                
                if smoke > 0 or regression > 0:
                    print(f"Processed {file_path}: +{smoke} smoke, +{regression} regression")
    
    print(f"\nSummary:")
    print(f"Files processed: {files_processed}")
    print(f"Smoke markers added: {total_smoke}")
    print(f"Regression markers added: {total_regression}")


if __name__ == "__main__":
    main()

