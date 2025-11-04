#!/usr/bin/env python3
"""
Analyze Xray CSV File
======================

Analyze the CSV export from Jira Xray and identify test patterns.
"""

import csv
import sys
from pathlib import Path
from typing import List, Dict

def analyze_csv(file_path: str):
    """Analyze the CSV file and extract test information."""
    
    print("=" * 80)
    print("ANALYZING XRAY CSV FILE")
    print("=" * 80)
    print()
    
    tests = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if row['Issue Type'] == 'Test':
                tests.append({
                    'key': row['Issue key'],
                    'summary': row['Summary'],
                    'status': row['Status'],
                    'priority': row.get('Priority', 'N/A'),
                    'labels': row.get('Labels', ''),
                    'description': row.get('Description', '')[:200]
                })
    
    print(f"Total tests found: {len(tests)}")
    print()
    
    # Group by status
    status_count = {}
    for test in tests:
        status = test['status']
        status_count[status] = status_count.get(status, 0) + 1
    
    print("Tests by Status:")
    for status, count in sorted(status_count.items()):
        print(f"  {status}: {count}")
    print()
    
    # Show first 10 tests
    print("First 10 Tests:")
    print("-" * 80)
    for i, test in enumerate(tests[:10], 1):
        print(f"{i}. {test['key']} - {test['summary'][:60]}...")
        print(f"   Status: {test['status']}, Priority: {test['priority']}")
        print()
    
    # Count by category (from labels or description)
    categories = {}
    for test in tests:
        # Try to infer category from labels or description
        labels = test['labels'].lower() if test['labels'] else ''
        summary = test['summary'].lower()
        
        if 'integration' in labels or 'integration' in summary:
            categories['Integration'] = categories.get('Integration', 0) + 1
        elif 'api' in labels or 'api' in summary:
            categories['API'] = categories.get('API', 0) + 1
        elif 'data_quality' in labels or 'data quality' in summary or 'mongodb' in labels:
            categories['Data Quality'] = categories.get('Data Quality', 0) + 1
        elif 'performance' in labels or 'performance' in summary:
            categories['Performance'] = categories.get('Performance', 0) + 1
        elif 'infrastructure' in labels or 'infrastructure' in summary:
            categories['Infrastructure'] = categories.get('Infrastructure', 0) + 1
        elif 'security' in labels or 'security' in summary:
            categories['Security'] = categories.get('Security', 0) + 1
        elif 'stress' in labels or 'stress' in summary:
            categories['Stress'] = categories.get('Stress', 0) + 1
        else:
            categories['Other'] = categories.get('Other', 0) + 1
    
    print("Tests by Category (estimated):")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count}")
    print()
    
    # Find specific test keys we're looking for
    print("Looking for specific test keys:")
    target_keys = ['PZ-13984', 'PZ-13985', 'PZ-13986', 'PZ-13909', 'PZ-13907']
    
    found = {}
    for test in tests:
        if test['key'] in target_keys:
            found[test['key']] = test
    
    if found:
        print("Found target tests:")
        for key in target_keys:
            if key in found:
                print(f"  ✅ {key}: {found[key]['summary']}")
            else:
                print(f"  ❌ {key}: NOT FOUND")
    else:
        print("  ❌ None of the target test keys found")
    
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    file_path = r"c:\Users\roy.avrahami\Downloads\Test plan (PZ-13756) by Roy Avrahami (Jira).csv"
    
    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    analyze_csv(file_path)

