#!/usr/bin/env python3
"""
Parse Xray CSV export and extract test case information.
"""
import csv
import json
import sys
from pathlib import Path

def parse_xray_csv(csv_path):
    """Parse Xray CSV and extract test information."""
    tests = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            issue_key = row.get('Issue key', '').strip()
            summary = row.get('Summary', '').strip()
            description = row.get('Description', '').strip()
            status = row.get('Status', '').strip()
            
            if issue_key and summary:
                test_info = {
                    'issue_key': issue_key,
                    'summary': summary,
                    'description': description,
                    'status': status,
                    'priority': row.get('Priority', '').strip(),
                    'labels': row.get('Labels', '').strip(),
                }
                tests.append(test_info)
    
    return tests

def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_xray_csv.py <csv_file> <output_json>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'output/xray_tests.json'
    
    # Create output directory
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Parse CSV
    tests = parse_xray_csv(csv_path)
    
    # Write JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tests, f, indent=2, ensure_ascii=False)
    
    print(f"Parsed {len(tests)} test cases from CSV")
    print(f"Output written to: {output_path}")

if __name__ == '__main__':
    main()

