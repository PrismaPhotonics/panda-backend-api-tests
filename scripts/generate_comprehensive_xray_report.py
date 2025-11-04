#!/usr/bin/env python3
"""
Generate comprehensive Xray to Automation mapping report.
"""
import csv
import os
import re
from pathlib import Path
from collections import defaultdict

def extract_xray_ids_from_code():
    """Extract all Xray IDs from test code."""
    xray_markers = defaultdict(list)
    
    tests_dir = Path('tests')
    for test_file in tests_dir.rglob('*.py'):
        if test_file.name.startswith('test_') or test_file.name == 'conftest.py':
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find all @pytest.mark.xray markers
                pattern = r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\s*(?:,\s*["\']([^"\']+)["\']\s*)*\)'
                for match in re.finditer(pattern, content):
                    xray_ids = [match.group(1)]
                    # Check for additional IDs
                    additional = re.findall(r',\s*["\']([^"\']+)["\']', match.group(0))
                    xray_ids.extend(additional)
                    
                    for xray_id in xray_ids:
                        xray_markers[xray_id].append(str(test_file))
                
            except Exception as e:
                print(f"Error reading {test_file}: {e}")
    
    return xray_markers

def parse_xray_csv(csv_path):
    """Parse Xray CSV to get all test definitions."""
    tests = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                issue_key = row.get('Issue key', '').strip()
                summary = row.get('Summary', '').strip()
                priority = row.get('Priority', '').strip()
                status = row.get('Status', '').strip()
                
                if issue_key and summary:
                    tests.append({
                        'key': issue_key,
                        'summary': summary,
                        'priority': priority,
                        'status': status
                    })
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    return tests

def generate_report():
    """Generate comprehensive mapping report."""
    print("="*80)
    print("COMPREHENSIVE XRAY TO AUTOMATION MAPPING REPORT")
    print("="*80)
    print()
    
    # Step 1: Extract Xray IDs from code
    print("Step 1: Scanning automation code for Xray markers...")
    xray_in_code = extract_xray_ids_from_code()
    print(f"   Found {len(xray_in_code)} unique Xray IDs in automation code")
    print()
    
    # Step 2: Parse Xray CSV
    print("Step 2: Loading Xray test definitions from CSV...")
    csv_path = Path("c:/Users/roy.avrahami/Downloads/Test plan (PZ-13756) by Roy Avrahami (Jira).csv")
    
    if not csv_path.exists():
        print(f"   ERROR: CSV not found at {csv_path}")
        xray_tests = []
    else:
        xray_tests = parse_xray_csv(csv_path)
        print(f"   Found {len(xray_tests)} tests in Xray CSV")
    print()
    
    # Step 3: Create mapping
    print("Step 3: Creating mapping...")
    print()
    
    # Create markdown report
    report_lines = []
    report_lines.append("# 📊 דוח מיפוי מפורט - Xray לאוטומציה")
    report_lines.append("")
    report_lines.append("**תאריך:** 27 באוקטובר 2025")
    report_lines.append("**סטטוס:** מעודכן")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Summary statistics
    report_lines.append("## 📈 סטטיסטיקה")
    report_lines.append("")
    report_lines.append(f"| מדד | ערך |")
    report_lines.append(f"|------|------|")
    report_lines.append(f"| **טסטים ב-Xray CSV** | {len(xray_tests)} |")
    report_lines.append(f"| **Xray IDs באוטומציה** | {len(xray_in_code)} |")
    
    # Count mapped tests
    mapped_count = sum(1 for test in xray_tests if test['key'] in xray_in_code)
    unmapped_count = len(xray_tests) - mapped_count
    
    report_lines.append(f"| **טסטים ממומשים** | {mapped_count} |")
    report_lines.append(f"| **טסטים לא ממומשים** | {unmapped_count} |")
    if len(xray_tests) > 0:
        coverage = (mapped_count / len(xray_tests)) * 100
        report_lines.append(f"| **אחוז כיסוי** | {coverage:.1f}% |")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Section 1: Implemented tests
    report_lines.append("## ✅ טסטים ממומשים באוטומציה")
    report_lines.append("")
    report_lines.append("| # | Xray ID | Summary | קובץ באוטומציה | מספר קבצים |")
    report_lines.append("|---|---------|---------|----------------|------------|")
    
    implemented = []
    for test in xray_tests:
        if test['key'] in xray_in_code:
            files = xray_in_code[test['key']]
            implemented.append({
                'key': test['key'],
                'summary': test['summary'],
                'files': files,
                'priority': test['priority']
            })
    
    # Sort by Xray ID
    implemented.sort(key=lambda x: x['key'])
    
    for i, test in enumerate(implemented, 1):
        files_str = files[0].replace('tests\\', '').replace('tests/', '') if len(files) == 1 else f"{len(files)} files"
        report_lines.append(f"| {i} | {test['key']} | {test['summary'][:60]}... | `{files_str}` | {len(test['files'])} |")
    
    report_lines.append("")
    report_lines.append(f"**סה\"כ: {len(implemented)} טסטים ממומשים**")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Section 2: Not implemented tests
    report_lines.append("## ❌ טסטים שעדיין לא ממומשים")
    report_lines.append("")
    report_lines.append("| # | Xray ID | Summary | Priority | Status |")
    report_lines.append("|---|---------|---------|----------|--------|")
    
    not_implemented = []
    for test in xray_tests:
        if test['key'] not in xray_in_code:
            not_implemented.append(test)
    
    not_implemented.sort(key=lambda x: x['key'])
    
    for i, test in enumerate(not_implemented, 1):
        report_lines.append(f"| {i} | {test['key']} | {test['summary'][:70]}... | {test['priority']} | {test['status']} |")
    
    report_lines.append("")
    report_lines.append(f"**סה\"כ: {len(not_implemented)} טסטים לא ממומשים**")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Section 3: Detailed mapping
    report_lines.append("## 📋 מיפוי מפורט - כל טסט")
    report_lines.append("")
    
    for test in sorted(xray_tests, key=lambda x: x['key']):
        report_lines.append(f"### {test['key']}: {test['summary']}")
        report_lines.append("")
        report_lines.append(f"**Priority:** {test['priority']}")
        report_lines.append(f"**Status:** {test['status']}")
        report_lines.append("")
        
        if test['key'] in xray_in_code:
            report_lines.append("**✅ ממומש באוטומציה:**")
            for file_path in xray_in_code[test['key']]:
                clean_path = file_path.replace('tests\\', '').replace('tests/', '')
                report_lines.append(f"- `{clean_path}`")
        else:
            report_lines.append("**❌ לא ממומש באוטומציה**")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
    
    # Save report
    output_path = Path('COMPREHENSIVE_XRAY_AUTOMATION_MAPPING.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"✅ Report saved to: {output_path}")
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Xray Tests:     {len(xray_tests)}")
    print(f"Implemented:          {mapped_count}")
    print(f"Not Implemented:      {unmapped_count}")
    if len(xray_tests) > 0:
        print(f"Coverage:             {coverage:.1f}%")
    print("="*80)
    
    return implemented, not_implemented

if __name__ == '__main__':
    implemented, not_implemented = generate_report()

