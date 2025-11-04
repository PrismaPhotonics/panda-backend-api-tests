#!/usr/bin/env python3
"""
Comprehensive Xray to Automation Test Mapping Analysis

This script performs deep analysis comparing all Xray test cases against
all automation tests to create a detailed mapping table.
"""
import os
import sys
import re
import json
import csv
from pathlib import Path
from collections import defaultdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def extract_test_functions(file_path):
    """Extract all test function names from a Python test file."""
    test_functions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match test function definitions
        pattern = r'^(\s*)def (test_\w+)\('
        for match in re.finditer(pattern, content, re.MULTILINE):
            test_name = match.group(2)
            test_functions.append({
                'name': test_name,
                'file': str(file_path),
                'line': content[:match.start()].count('\n') + 1
            })
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return test_functions

def extract_xray_markers(file_path):
    """Extract Xray markers from a test file."""
    markers = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            # Match @pytest.mark.xray decorators
            if '@pytest.mark.xray' in line:
                # Extract marker arguments
                marker_match = re.search(r'@pytest\.mark\.xray\(([^)]+)\)', line)
                if marker_match:
                    args = marker_match.group(1)
                    # Parse quoted strings (Xray IDs)
                    xray_ids = re.findall(r'["\']([^"\']+)["\']', args)
                    markers.extend(xray_ids)
    
    except Exception as e:
        print(f"Error extracting Xray markers from {file_path}: {e}")
    
    return markers

def parse_xray_csv(csv_path):
    """Parse Xray CSV export."""
    tests = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                issue_key = row.get('Issue key', '').strip()
                summary = row.get('Summary', '').strip()
                if issue_key and summary:
                    tests.append({
                        'issue_key': issue_key,
                        'summary': summary,
                        'description': row.get('Description', '').strip(),
                        'status': row.get('Status', '').strip(),
                        'priority': row.get('Priority', '').strip(),
                        'labels': row.get('Labels', '').strip(),
                    })
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    return tests

def scan_all_test_files():
    """Scan all test files in the tests directory."""
    test_files = []
    
    tests_dir = Path('tests')
    
    for file_path in tests_dir.rglob('*.py'):
        if file_path.name.startswith('test_') or file_path.name == 'conftest.py':
            test_files.append(file_path)
    
    return test_files

def create_mapping():
    """Create comprehensive mapping between Xray tests and automation tests."""
    
    print("=" * 80)
    print("COMPREHENSIVE XRAY TO AUTOMATION MAPPING ANALYSIS")
    print("=" * 80)
    print()
    
    # Step 1: Scan all automation test files
    print("📂 Step 1: Scanning automation test files...")
    test_files = scan_all_test_files()
    print(f"   Found {len(test_files)} test files")
    print()
    
    # Step 2: Extract all test functions
    print("🔍 Step 2: Extracting test functions...")
    all_tests = []
    xray_mappings = defaultdict(list)
    
    for test_file in test_files:
        test_functions = extract_test_functions(test_file)
        markers = extract_xray_markers(test_file)
        
        for test_func in test_functions:
            test_func['xray_markers'] = markers
            all_tests.append(test_func)
            
            # Create reverse mapping (Xray -> Tests)
            for marker in markers:
                xray_mappings[marker].append({
                    'file': test_func['file'],
                    'name': test_func['name'],
                })
    
    print(f"   Found {len(all_tests)} automation test functions")
    print(f"   Found {len(xray_mappings)} Xray IDs mapped to automation")
    print()
    
    # Step 3: Parse Xray CSV
    print("📋 Step 3: Parsing Xray CSV export...")
    csv_path = Path("c:/Users/roy.avrahami/Downloads/Test plan (PZ-13756) by Roy Avrahami (Jira).csv")
    
    if not csv_path.exists():
        print(f"   ⚠️  CSV file not found: {csv_path}")
        print("   Will create partial mapping without Xray details")
        xray_tests = []
    else:
        xray_tests = parse_xray_csv(csv_path)
        print(f"   Parsed {len(xray_tests)} Xray test cases")
    print()
    
    # Step 4: Create mapping table
    print("🔄 Step 4: Creating mapping table...")
    
    mapping_results = []
    
    # Group automation tests by Xray marker
    for xray_id, auto_tests in sorted(xray_mappings.items()):
        xray_test = next((t for t in xray_tests if t['issue_key'] == xray_id), None)
        
        for auto_test in auto_tests:
            mapping_results.append({
                'automation_test': f"{auto_test['name']}",
                'automation_file': auto_test['file'],
                'xray_id': xray_id,
                'xray_summary': xray_test['summary'] if xray_test else 'Not found in CSV',
                'xray_status': xray_test['status'] if xray_test else 'Unknown',
                'relationship': 'MAPPED',
                'coverage_level': 'FULL',
                'notes': ''
            })
    
    # Find automation tests without Xray markers
    print("🔍 Step 5: Finding unmapped automation tests...")
    unmapped_tests = []
    for test_func in all_tests:
        if not test_func['xray_markers']:
            unmapped_tests.append({
                'automation_test': f"{test_func['name']}",
                'automation_file': test_func['file'],
                'xray_id': 'NONE',
                'relationship': 'NOT_MAPPED',
                'notes': 'No Xray marker'
            })
    
    print(f"   Found {len(unmapped_tests)} unmapped tests")
    print()
    
    # Step 6: Find Xray tests without automation
    print("🔍 Step 6: Finding Xray tests without automation...")
    xray_ids_with_auto = set(xray_mappings.keys())
    unmapped_xray = []
    for xray_test in xray_tests:
        if xray_test['issue_key'] not in xray_ids_with_auto:
            unmapped_xray.append({
                'xray_id': xray_test['issue_key'],
                'xray_summary': xray_test['summary'],
                'xray_status': xray_test['status'],
                'relationship': 'NO_AUTOMATION',
                'notes': 'No automation test implemented'
            })
    
    print(f"   Found {len(unmapped_xray)} unmapped Xray tests")
    print()
    
    # Step 7: Generate report
    print("📊 Step 7: Generating comprehensive report...")
    
    report = {
        'summary': {
            'total_automation_tests': len(all_tests),
            'total_xray_tests': len(xray_tests),
            'mapped_tests': len(mapping_results),
            'unmapped_automation': len(unmapped_tests),
            'unmapped_xray': len(unmapped_xray),
            'coverage_percentage': f"{(len(mapping_results) / max(len(xray_tests), 1)) * 100:.1f}%"
        },
        'mapped': mapping_results,
        'unmapped_automation': unmapped_tests,
        'unmapped_xray': unmapped_xray
    }
    
    # Write to JSON
    output_json = Path('output/comprehensive_xray_mapping.json')
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"   Report written to: {output_json}")
    print()
    
    # Print summary
    print("=" * 80)
    print("MAPPING SUMMARY")
    print("=" * 80)
    print(f"Automation Tests:     {len(all_tests)}")
    print(f"Xray Tests:            {len(xray_tests)}")
    print(f"Mapped Tests:         {len(mapping_results)}")
    print(f"Unmapped Automation:  {len(unmapped_tests)}")
    print(f"Unmapped Xray:        {len(unmapped_xray)}")
    print(f"Coverage:             {report['summary']['coverage_percentage']}")
    print("=" * 80)
    
    return report

if __name__ == '__main__':
    create_mapping()
