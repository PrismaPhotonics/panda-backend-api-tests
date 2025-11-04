#!/usr/bin/env python3
"""
Analyze Xray CSV to identify high-priority tests without automation.
"""
import csv
import re
from pathlib import Path

# Known mapped Xray IDs (already have automation)
MAPPED_XRAY_IDS = {
    "PZ-13984", "PZ-13869", "PZ-13876", "PZ-13877", "PZ-13903",
    "PZ-13874", "PZ-13875", "PZ-13895", "PZ-13762", "PZ-13985",
    "PZ-13986", "PZ-13547", "PZ-13548", "PZ-13863", "PZ-13878",
    "PZ-13901", "PZ-13896", "PZ-13897", "PZ-13898", "PZ-13899",
    "PZ-13902", "PZ-13904", "PZ-13905", "PZ-13906", "PZ-13907",
    "PZ-13908", "PZ-13909", "PZ-13910", "PZ-13911", "PZ-13912"
}

def parse_xray_csv():
    """Parse Xray CSV and categorize tests."""
    csv_path = Path("c:/Users/roy.avrahami/Downloads/Test plan (PZ-13756) by Roy Avrahami (Jira).csv")
    
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        return []
    
    tests = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            issue_key = row.get('Issue key', '').strip()
            summary = row.get('Summary', '').strip()
            priority = row.get('Priority', '').strip()
            status = row.get('Status', '').strip()
            description = row.get('Description', '').strip()
            
            if issue_key and summary:
                has_automation = issue_key in MAPPED_XRAY_IDS
                
                tests.append({
                    'key': issue_key,
                    'summary': summary,
                    'priority': priority,
                    'status': status,
                    'has_automation': has_automation,
                    'description': description[:500]  # First 500 chars
                })
    
    return tests

def categorize_tests(tests):
    """Categorize tests by type."""
    categories = {
        'Config Validation': [],
        'API Endpoints': [],
        'Performance': [],
        'Infrastructure': [],
        'Data Quality': [],
        'Security': [],
        'Other': []
    }
    
    for test in tests:
        summary_lower = test['summary'].lower()
        
        if 'config' in summary_lower or 'validation' in summary_lower:
            categories['Config Validation'].append(test)
        elif 'api' in summary_lower or 'endpoint' in summary_lower or 'get /' in summary_lower:
            categories['API Endpoints'].append(test)
        elif 'performance' in summary_lower or 'latency' in summary_lower or 'throughput' in summary_lower:
            categories['Performance'].append(test)
        elif 'k8s' in summary_lower or 'kubernetes' in summary_lower or 'infrastructure' in summary_lower:
            categories['Infrastructure'].append(test)
        elif 'mongodb' in summary_lower or 'data quality' in summary_lower:
            categories['Data Quality'].append(test)
        elif 'security' in summary_lower:
            categories['Security'].append(test)
        else:
            categories['Other'].append(test)
    
    return categories

def print_analysis():
    """Print analysis of missing tests."""
    tests = parse_xray_csv()
    
    print("=" * 80)
    print("XRAY TESTS ANALYSIS")
    print("=" * 80)
    print()
    
    print(f"Total Xray Tests: {len(tests)}")
    mapped = [t for t in tests if t['has_automation']]
    unmapped = [t for t in tests if not t['has_automation']]
    print(f"With Automation: {len(mapped)}")
    print(f"Without Automation: {len(unmapped)}")
    print()
    
    # Categorize unmapped tests
    categories = categorize_tests(unmapped)
    
    print("UNMAPPED TESTS BY CATEGORY:")
    print("-" * 80)
    for category, tests_list in categories.items():
        if tests_list:
            print(f"\n{category}: {len(tests_list)} tests")
            # Show top 5 by priority
            high_priority = [t for t in tests_list if t['priority'] in ['High', 'Highest', 'Medium']]
            for i, test in enumerate(high_priority[:5], 1):
                print(f"  {i}. {test['key']}: {test['summary'][:70]}")
    
    print()
    print("=" * 80)
    print("TOP 10 HIGH-PRIORITY TESTS TO IMPLEMENT:")
    print("=" * 80)
    
    high_pri_unmapped = [t for t in unmapped if t['priority'] in ['High', 'Highest']]
    for i, test in enumerate(high_pri_unmapped[:10], 1):
        print(f"{i}. {test['key']} - {test['summary']}")
        print(f"   Priority: {test['priority']}, Status: {test['status']}")
    
    return unmapped, categories

if __name__ == '__main__':
    unmapped, categories = print_analysis()

