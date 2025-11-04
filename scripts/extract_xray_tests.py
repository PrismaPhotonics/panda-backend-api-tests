#!/usr/bin/env python3
"""
Extract Xray test definitions from CSV and create implementation plan.
"""
import csv
import json
from pathlib import Path

def extract_test_data(csv_path):
    """Extract test data from CSV."""
    tests = []
    
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            issue_key = row.get('Issue key', '').strip()
            summary = row.get('Summary', '').strip()
            description = row.get('Description', '').strip()
            priority = row.get('Priority', '').strip()
            status = row.get('Status', '').strip()
            
            if issue_key and summary and description:
                tests.append({
                    'key': issue_key,
                    'summary': summary,
                    'priority': priority,
                    'status': status,
                    'description': description
                })
    
    return tests

def main():
    csv_path = Path("c:/Users/roy.avrahami/Downloads/Test plan (PZ-13756) by Roy Avrahami (Jira).csv")
    
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        return
    
    print("Extracting Xray tests from CSV...")
    tests = extract_test_data(csv_path)
    
    print(f"\nFound {len(tests)} tests")
    
    # Show first 10
    print("\n" + "="*80)
    print("FIRST 10 TESTS TO IMPLEMENT:")
    print("="*80)
    
    for i, test in enumerate(tests[:10], 1):
        print(f"\n{i}. {test['key']}: {test['summary']}")
        print(f"   Priority: {test['priority']}, Status: {test['status']}")
        
        # Extract objective
        desc = test['description']
        if '## Objective' in desc:
            obj_start = desc.find('## Objective') + len('## Objective')
            obj_end = desc.find('##', obj_start)
            if obj_end == -1:
                obj_end = obj_start + 200
            objective = desc[obj_start:obj_end].strip()[:150]
            print(f"   Objective: {objective}...")
    
    # Save to JSON for processing
    output_path = Path('output/xray_tests_detailed.json')
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tests, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nSaved {len(tests)} tests to: {output_path}")
    
    return tests

if __name__ == '__main__':
    tests = main()

