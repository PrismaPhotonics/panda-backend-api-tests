#!/usr/bin/env python3
"""
Generate comprehensive tests report with Xray/Jira markers
"""

import os
import sys
import re
from collections import defaultdict
from pathlib import Path

# Configure UTF-8 output for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def read_test_file_and_extract_tests(file_path):
    """Read a test file and extract all test functions with their markers."""
    tests = []
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
    except:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            return tests
    
    current_markers = {'xray': [], 'jira': []}
    current_class = None
    class_markers = {'xray': [], 'jira': []}
    
    for i, line in enumerate(lines, 1):
        # Check for class definition
        if line.strip().startswith('class Test'):
            match = re.match(r'class\s+(\w+)', line.strip())
            if match:
                current_class = match.group(1)
                # Scan backwards for class markers
                class_markers = {'xray': [], 'jira': []}
                for j in range(max(0, i-10), i):
                    if '@pytest.mark.xray(' in lines[j-1]:
                        xray_ids = re.findall(r'PZ-\d+', lines[j-1])
                        class_markers['xray'].extend(xray_ids)
                    if '@pytest.mark.jira(' in lines[j-1]:
                        jira_ids = re.findall(r'PZ-\d+', lines[j-1])
                        class_markers['jira'].extend(jira_ids)
        
        # Check for test function
        if line.strip().startswith('def test_'):
            match = re.match(r'def\s+(test_\w+)', line.strip())
            if match:
                test_name = match.group(1)
                
                # Scan backwards for markers
                current_markers = {'xray': [], 'jira': []}
                for j in range(max(0, i-10), i):
                    if '@pytest.mark.xray(' in lines[j-1]:
                        xray_ids = re.findall(r'PZ-\d+', lines[j-1])
                        current_markers['xray'].extend(xray_ids)
                    if '@pytest.mark.jira(' in lines[j-1]:
                        jira_ids = re.findall(r'PZ-\d+', lines[j-1])
                        current_markers['jira'].extend(jira_ids)
                
                # Combine class and method markers
                all_xray = list(set(class_markers['xray'] + current_markers['xray']))
                all_jira = list(set(class_markers['jira'] + current_markers['jira']))
                
                if all_xray or all_jira:
                    full_name = f"{current_class}::{test_name}" if current_class else test_name
                    tests.append({
                        'name': test_name,
                        'full_name': full_name,
                        'class': current_class,
                        'line': i,
                        'xray': sorted(all_xray),
                        'jira': sorted(all_jira)
                    })
    
    return tests

def main():
    print("\n" + "="*100)
    print("📋 רשימה מלאה של כל הטסטים עם Xray/Jira IDs")
    print("="*100 + "\n")
    
    # Find all test files
    tests_dir = Path('tests')
    all_test_files = list(tests_dir.rglob('test_*.py'))
    
    print(f"🔍 סורק {len(all_test_files)} קבצי טסט...\n")
    
    # Process all files
    all_tests = []
    tests_by_file = defaultdict(list)
    
    for test_file in sorted(all_test_files):
        tests = read_test_file_and_extract_tests(test_file)
        if tests:
            rel_path = str(test_file).replace(str(Path.cwd()) + os.sep, '')
            tests_by_file[rel_path] = tests
            all_tests.extend(tests)
    
    # Collect all unique IDs
    all_xray_ids = set()
    all_jira_ids = set()
    xray_to_tests = defaultdict(list)
    jira_to_tests = defaultdict(list)
    
    for test in all_tests:
        for xray_id in test['xray']:
            all_xray_ids.add(xray_id)
            xray_to_tests[xray_id].append(test['full_name'])
        for jira_id in test['jira']:
            all_jira_ids.add(jira_id)
            jira_to_tests[jira_id].append(test['full_name'])
    
    print("="*100)
    print("📊 סיכום")
    print("="*100)
    print(f"✅ סך הכל טסטים עם markers: {len(all_tests)}")
    print(f"📂 קבצים עם טסטים: {len(tests_by_file)}")
    print(f"🆔 ייחודיים Xray IDs: {len(all_xray_ids)}")
    print(f"🐛 ייחודיים Jira IDs: {len(all_jira_ids)}")
    print("="*100 + "\n")
    
    # Generate detailed report
    report_lines = []
    report_lines.append("# 📋 רשימה מלאה של טסטים עם Xray/Jira IDs\n")
    report_lines.append(f"**תאריך:** 2025-10-30\n")
    report_lines.append(f"**סך הכל טסטים:** {len(all_tests)}\n")
    report_lines.append(f"**Xray IDs:** {len(all_xray_ids)}\n")
    report_lines.append(f"**Jira IDs:** {len(all_jira_ids)}\n")
    report_lines.append("\n---\n\n")
    
    # Group by file
    for file_path in sorted(tests_by_file.keys()):
        tests = tests_by_file[file_path]
        report_lines.append(f"## 📂 {file_path}\n\n")
        report_lines.append(f"**מספר טסטים:** {len(tests)}\n\n")
        
        for test in tests:
            report_lines.append(f"### ✅ `{test['full_name']}`\n\n")
            report_lines.append(f"**קובץ:** `{file_path}:{test['line']}`\n\n")
            
            if test['xray']:
                report_lines.append(f"**Xray IDs:** {', '.join([f'`{x}`' for x in test['xray']])}\n\n")
            
            if test['jira']:
                report_lines.append(f"**Jira Bugs:** {', '.join([f'`{j}`' for j in test['jira']])}\n\n")
            
            report_lines.append("---\n\n")
    
    # Save Markdown report
    with open('ALL_TESTS_WITH_XRAY_JIRA_IDS.md', 'w', encoding='utf-8') as f:
        f.writelines(report_lines)
    
    print("✅ נוצר דוח: ALL_TESTS_WITH_XRAY_JIRA_IDS.md\n")
    
    # Generate CSV
    csv_lines = []
    csv_lines.append("File,Class,Test Name,Full Name,Xray IDs,Jira IDs,Line\n")
    
    for file_path in sorted(tests_by_file.keys()):
        for test in tests_by_file[file_path]:
            xray_str = '; '.join(test['xray'])
            jira_str = '; '.join(test['jira'])
            csv_lines.append(f'"{file_path}","{test["class"] or ""}","{test["name"]}","{test["full_name"]}","{xray_str}","{jira_str}",{test["line"]}\n')
    
    with open('ALL_TESTS_WITH_XRAY_JIRA_IDS.csv', 'w', encoding='utf-8') as f:
        f.writelines(csv_lines)
    
    print("✅ נוצר CSV: ALL_TESTS_WITH_XRAY_JIRA_IDS.csv\n")
    
    # Print Xray IDs with test count
    print("\n" + "="*100)
    print(f"📋 כל ה-Xray IDs ({len(all_xray_ids)})")
    print("="*100)
    for xray_id in sorted(all_xray_ids):
        count = len(xray_to_tests[xray_id])
        print(f"  {xray_id:10} - {count} טסט/ים")
    
    # Print Jira IDs with test count
    print("\n" + "="*100)
    print(f"🐛 כל ה-Jira Bug IDs ({len(all_jira_ids)})")
    print("="*100)
    for jira_id in sorted(all_jira_ids):
        count = len(jira_to_tests[jira_id])
        print(f"  {jira_id:10} - {count} טסט/ים")
    
    print("\n" + "="*100)
    print("✅ הושלם בהצלחה!")
    print("="*100 + "\n")

if __name__ == "__main__":
    main()

