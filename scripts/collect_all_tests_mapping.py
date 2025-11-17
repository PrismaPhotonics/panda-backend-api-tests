#!/usr/bin/env python3
"""
Collect All Tests with Xray/Jira Markers Mapping
=================================================

This script scans all test files and extracts:
1. Test name
2. Test file location
3. Xray markers (PZ-XXXXX)
4. Jira markers (PZ-XXXXX)
5. Test class (if any)

Author: QA Automation Team
Date: 2025-10-30
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Any
import ast

# Configure UTF-8 output for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def extract_markers_from_decorator(decorator_node) -> Dict[str, List[str]]:
    """
    Extract Xray and Jira markers from a decorator node.
    
    Args:
        decorator_node: AST decorator node
        
    Returns:
        Dict with 'xray' and 'jira' lists of IDs
    """
    markers = {'xray': [], 'jira': []}
    
    try:
        # Check if it's pytest.mark.xray or pytest.mark.jira
        if isinstance(decorator_node, ast.Call):
            if isinstance(decorator_node.func, ast.Attribute):
                marker_name = decorator_node.func.attr
                
                if marker_name in ['xray', 'jira']:
                    # Extract all PZ-XXXXX arguments
                    for arg in decorator_node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            if arg.value.startswith('PZ-'):
                                markers[marker_name].append(arg.value)
    except:
        pass
    
    return markers


def extract_tests_from_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Extract all tests from a Python test file.
    
    Args:
        file_path: Path to test file
        
    Returns:
        List of test dictionaries with metadata
    """
    tests = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(file_path))
        
        # Get relative path from project root
        rel_path = file_path.relative_to(Path.cwd())
        
        # Extract tests from the AST
        for node in ast.walk(tree):
            # Check for test classes
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                class_markers = {'xray': [], 'jira': []}
                
                # Extract class-level markers
                for decorator in node.decorator_list:
                    markers = extract_markers_from_decorator(decorator)
                    class_markers['xray'].extend(markers['xray'])
                    class_markers['jira'].extend(markers['jira'])
                
                # Extract test methods in class
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                        method_markers = {'xray': [], 'jira': []}
                        
                        # Extract method-level markers
                        for decorator in item.decorator_list:
                            markers = extract_markers_from_decorator(decorator)
                            method_markers['xray'].extend(markers['xray'])
                            method_markers['jira'].extend(markers['jira'])
                        
                        # Combine class and method markers
                        all_xray = list(set(class_markers['xray'] + method_markers['xray']))
                        all_jira = list(set(class_markers['jira'] + method_markers['jira']))
                        
                        if all_xray or all_jira:  # Only include if has markers
                            tests.append({
                                'file': str(rel_path),
                                'class': class_name,
                                'method': item.name,
                                'full_name': f"{class_name}::{item.name}",
                                'xray_markers': sorted(all_xray),
                                'jira_markers': sorted(all_jira),
                                'line': item.lineno
                            })
            
            # Check for standalone test functions (not in a class)
            elif isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                # Check if it's at module level (not inside a class)
                is_module_level = True
                for parent in ast.walk(tree):
                    if isinstance(parent, ast.ClassDef):
                        if node in parent.body:
                            is_module_level = False
                            break
                
                if is_module_level:
                    function_markers = {'xray': [], 'jira': []}
                    
                    # Extract function-level markers
                    for decorator in node.decorator_list:
                        markers = extract_markers_from_decorator(decorator)
                        function_markers['xray'].extend(markers['xray'])
                        function_markers['jira'].extend(markers['jira'])
                    
                    if function_markers['xray'] or function_markers['jira']:  # Only include if has markers
                        tests.append({
                            'file': str(rel_path),
                            'class': None,
                            'method': node.name,
                            'full_name': node.name,
                            'xray_markers': sorted(function_markers['xray']),
                            'jira_markers': sorted(function_markers['jira']),
                            'line': node.lineno
                        })
    
    except Exception as e:
        print(f"⚠️  Error parsing {file_path}: {e}", file=sys.stderr)
    
    return tests


def find_all_test_files() -> List[Path]:
    """
    Find all test files in the tests directory.
    
    Returns:
        List of test file paths
    """
    test_files = []
    tests_dir = Path('tests')
    
    if tests_dir.exists():
        for file_path in tests_dir.rglob('test_*.py'):
            test_files.append(file_path)
    
    return sorted(test_files)


def generate_markdown_report(all_tests: List[Dict[str, Any]]) -> str:
    """
    Generate a comprehensive Markdown report.
    
    Args:
        all_tests: List of all tests with metadata
        
    Returns:
        Markdown formatted report
    """
    report = []
    
    report.append("# 📋 רשימה מלאה של טסטים עם Xray/Jira IDs")
    report.append("")
    report.append(f"**תאריך:** 2025-10-30")
    report.append(f"**סך הכל טסטים:** {len(all_tests)}")
    report.append("")
    
    # Count markers
    total_xray = sum(len(t['xray_markers']) for t in all_tests)
    total_jira = sum(len(t['jira_markers']) for t in all_tests)
    
    report.append(f"**סך הכל Xray IDs:** {total_xray}")
    report.append(f"**סך הכל Jira IDs:** {total_jira}")
    report.append("")
    report.append("---")
    report.append("")
    
    # Group by file
    tests_by_file = {}
    for test in all_tests:
        file_path = test['file']
        if file_path not in tests_by_file:
            tests_by_file[file_path] = []
        tests_by_file[file_path].append(test)
    
    # Generate report for each file
    for file_path in sorted(tests_by_file.keys()):
        tests_in_file = tests_by_file[file_path]
        
        report.append(f"## 📂 {file_path}")
        report.append("")
        report.append(f"**מספר טסטים:** {len(tests_in_file)}")
        report.append("")
        
        for test in tests_in_file:
            # Test header
            if test['class']:
                report.append(f"### ✅ {test['class']}::{test['method']}")
            else:
                report.append(f"### ✅ {test['method']}")
            
            report.append("")
            report.append(f"**קובץ:** `{test['file']}:{test['line']}`")
            report.append("")
            
            # Xray markers
            if test['xray_markers']:
                report.append(f"**Xray IDs:** {', '.join([f'`{m}`' for m in test['xray_markers']])}")
                report.append("")
            
            # Jira markers
            if test['jira_markers']:
                report.append(f"**Jira IDs:** {', '.join([f'`{m}`' for m in test['jira_markers']])}")
                report.append("")
            
            report.append("---")
            report.append("")
    
    return '\n'.join(report)


def generate_csv_report(all_tests: List[Dict[str, Any]]) -> str:
    """
    Generate a CSV report for easy import to Excel/Jira.
    
    Args:
        all_tests: List of all tests with metadata
        
    Returns:
        CSV formatted report
    """
    lines = []
    
    # Header
    lines.append("File,Class,Method,Xray IDs,Jira IDs,Line Number")
    
    # Data rows
    for test in all_tests:
        file_path = test['file']
        class_name = test['class'] or ''
        method_name = test['method']
        xray_ids = '; '.join(test['xray_markers'])
        jira_ids = '; '.join(test['jira_markers'])
        line_num = test['line']
        
        lines.append(f'"{file_path}","{class_name}","{method_name}","{xray_ids}","{jira_ids}",{line_num}')
    
    return '\n'.join(lines)


def generate_summary_statistics(all_tests: List[Dict[str, Any]]) -> str:
    """
    Generate summary statistics.
    
    Args:
        all_tests: List of all tests with metadata
        
    Returns:
        Summary text
    """
    summary = []
    
    summary.append("\n" + "="*80)
    summary.append("📊 סיכום סטטיסטי")
    summary.append("="*80)
    
    # Total tests
    summary.append(f"\n✅ סך הכל טסטים: {len(all_tests)}")
    
    # Tests with Xray markers
    tests_with_xray = [t for t in all_tests if t['xray_markers']]
    summary.append(f"📝 טסטים עם Xray markers: {len(tests_with_xray)}")
    
    # Tests with Jira markers
    tests_with_jira = [t for t in all_tests if t['jira_markers']]
    summary.append(f"🐛 טסטים עם Jira markers: {len(tests_with_jira)}")
    
    # Total Xray IDs
    all_xray_ids = set()
    for test in all_tests:
        all_xray_ids.update(test['xray_markers'])
    summary.append(f"\n🆔 ייחודיים Xray IDs: {len(all_xray_ids)}")
    
    # Total Jira IDs
    all_jira_ids = set()
    for test in all_tests:
        all_jira_ids.update(test['jira_markers'])
    summary.append(f"🆔 ייחודיים Jira IDs: {len(all_jira_ids)}")
    
    # Tests by category (integration, performance, etc.)
    by_category = {}
    for test in all_tests:
        file_path = test['file']
        category = file_path.split(os.sep)[1] if len(file_path.split(os.sep)) > 1 else 'other'
        by_category[category] = by_category.get(category, 0) + 1
    
    summary.append("\n📂 טסטים לפי קטגוריה:")
    for category, count in sorted(by_category.items()):
        summary.append(f"   {category}: {count}")
    
    summary.append("\n" + "="*80 + "\n")
    
    return '\n'.join(summary)


def main():
    """Main execution function."""
    print("\n" + "="*80)
    print("🔍 אוסף את כל הטסטים עם Xray/Jira Markers...")
    print("="*80 + "\n")
    
    # Find all test files
    test_files = find_all_test_files()
    print(f"✅ נמצאו {len(test_files)} קבצי טסט")
    
    # Extract tests from all files
    all_tests = []
    for test_file in test_files:
        tests = extract_tests_from_file(test_file)
        all_tests.extend(tests)
    
    print(f"✅ נמצאו {len(all_tests)} טסטים עם markers\n")
    
    # Generate reports
    print("📝 יוצר דוחות...\n")
    
    # 1. Markdown report
    markdown_report = generate_markdown_report(all_tests)
    with open('ALL_TESTS_WITH_MARKERS.md', 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    print("✅ נוצר: ALL_TESTS_WITH_MARKERS.md")
    
    # 2. CSV report
    csv_report = generate_csv_report(all_tests)
    with open('ALL_TESTS_WITH_MARKERS.csv', 'w', encoding='utf-8') as f:
        f.write(csv_report)
    print("✅ נוצר: ALL_TESTS_WITH_MARKERS.csv")
    
    # 3. Print summary
    summary = generate_summary_statistics(all_tests)
    print(summary)
    
    # 4. List all unique Xray IDs
    all_xray_ids = set()
    for test in all_tests:
        all_xray_ids.update(test['xray_markers'])
    
    print("\n" + "="*80)
    print(f"📋 כל ה-Xray IDs הייחודיים ({len(all_xray_ids)}):")
    print("="*80)
    for xray_id in sorted(all_xray_ids):
        # Count how many tests use this ID
        count = sum(1 for t in all_tests if xray_id in t['xray_markers'])
        print(f"  {xray_id} (משויך ל-{count} טסטים)")
    
    print("\n✅ הושלם בהצלחה!")


if __name__ == "__main__":
    main()

