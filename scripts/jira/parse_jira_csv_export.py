"""Parse Jira CSV export and extract all test IDs"""
import sys
import csv
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Parsing Jira CSV Export")
print("="*80)
print()

# CSV file path
csv_file = Path(r"c:\Users\roy.avrahami\Downloads\Jira (28).csv")

if not csv_file.exists():
    print(f"[ERROR] File not found: {csv_file}")
    sys.exit(1)

print(f"Reading CSV file: {csv_file}")
print()

# Read CSV file
all_tests = []
test_ids = set()

try:
    # Try different encodings
    encodings = ['utf-8-sig', 'utf-8', 'utf-16', 'latin-1']
    reader = None
    
    for encoding in encodings:
        try:
            with open(csv_file, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                # Try to read first row to verify encoding works
                next(reader)
                f.seek(0)  # Reset to beginning
                reader = csv.DictReader(f)
                print(f"Using encoding: {encoding}")
                break
        except Exception as e:
            continue
    
    if reader is None:
        raise Exception("Could not read CSV with any encoding")
    
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # Get headers
        headers = reader.fieldnames
        print(f"CSV Headers ({len(headers)} columns):")
        for i, header in enumerate(headers[:20], 1):
            try:
                print(f"  {i:2}. {header}")
            except:
                print(f"  {i:2}. [Header {i}]")
        if len(headers) > 20:
            print(f"  ... and {len(headers) - 20} more columns")
        print()
        
        # Read all rows
        row_count = 0
        for row in reader:
            row_count += 1
            
            # Extract test information
            test_key = row.get('Issue key', '')
            summary = row.get('Summary', '')
            status = row.get('Status', '')
            issue_type = row.get('Issue Type', '')
            test_plan = row.get('Custom field (Test plan)', '')
            
            # Only process Test issues
            if issue_type == 'Test' and test_key:
                test_info = {
                    'key': test_key,
                    'summary': summary,
                    'status': status,
                    'test_plan': test_plan,
                    'description': row.get('Description', ''),
                    'test_type': row.get('Custom field (Test Type)', ''),
                    'priority': row.get('Priority', ''),
                    'labels': row.get('Labels', ''),
                    'created': row.get('Created', ''),
                    'updated': row.get('Updated', ''),
                }
                
                all_tests.append(test_info)
                test_ids.add(test_key)
        
        print(f"Total rows in CSV: {row_count}")
        print(f"Total Test issues found: {len(all_tests)}")
        print(f"Unique Test IDs: {len(test_ids)}")
        print()

except Exception as e:
    print(f"[ERROR] Failed to read CSV: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Filter tests by Test Plan PZ-14024
test_plan_key = "PZ-14024"
tests_in_plan = []
tests_not_in_plan = []

for test in all_tests:
    if test_plan_key in test['test_plan'] or test_plan_key in test['summary'] or test_plan_key in test['description']:
        tests_in_plan.append(test)
    else:
        tests_not_in_plan.append(test)

print("="*80)
print("FILTERING BY TEST PLAN PZ-14024")
print("="*80)
print(f"Tests in Test Plan PZ-14024: {len(tests_in_plan)}")
print(f"Tests NOT in Test Plan PZ-14024: {len(tests_not_in_plan)}")
print()

# Sort tests by key
tests_in_plan_sorted = sorted(tests_in_plan, key=lambda x: x['key'])

print("="*80)
print("ALL TEST IDs IN TEST PLAN PZ-14024 (sorted):")
print("="*80)
for i, test in enumerate(tests_in_plan_sorted, 1):
    try:
        summary = test['summary'][:60].encode('ascii', 'ignore').decode('ascii')
        print(f"{i:3}. {test['key']}: {summary}")
    except:
        print(f"{i:3}. {test['key']}: [Summary]")

print()
print(f"Total: {len(tests_in_plan_sorted)} tests")
print()

# Save to file
output_dir = Path("docs/04_testing/xray_mapping")
output_dir.mkdir(parents=True, exist_ok=True)

# Save test IDs
output_file_ids = output_dir / "TEST_PLAN_PZ14024_ALL_TEST_IDS.txt"
with open(output_file_ids, 'w', encoding='utf-8') as f:
    f.write(f"Test Plan: PZ-14024\n")
    f.write(f"Total Tests: {len(tests_in_plan_sorted)}\n")
    f.write(f"Source: Jira CSV Export\n")
    f.write(f"\n")
    f.write(f"All Test IDs:\n")
    for test in tests_in_plan_sorted:
        f.write(f"{test['key']}\n")

print(f"Test IDs saved to: {output_file_ids}")

# Save detailed report
output_file_details = output_dir / "TEST_PLAN_PZ14024_DETAILED_REPORT.md"
with open(output_file_details, 'w', encoding='utf-8') as f:
    f.write(f"# Test Plan: PZ-14024 - Complete Test List\n\n")
    f.write(f"**Source:** Jira CSV Export\n")
    f.write(f"**Total Tests:** {len(tests_in_plan_sorted)}\n")
    f.write(f"**Generated:** {Path(__file__).stat().st_mtime}\n\n")
    f.write(f"---\n\n")
    f.write(f"## Test Cases\n\n")
    f.write(f"| # | Test ID | Summary | Status | Test Type | Priority |\n")
    f.write(f"|---|---------|---------|--------|-----------|----------|\n")
    
    for i, test in enumerate(tests_in_plan_sorted, 1):
        test_id = test['key']
        summary = test['summary'].replace('|', '\\|')[:80]
        status = test['status']
        test_type = test.get('test_type', 'N/A')
        priority = test.get('priority', 'N/A')
        
        f.write(f"| {i} | {test_id} | {summary} | {status} | {test_type} | {priority} |\n")
    
    f.write(f"\n")
    f.write(f"## Summary\n\n")
    f.write(f"- **Total Tests:** {len(tests_in_plan_sorted)}\n")
    f.write(f"- **Tests in CSV:** {len(all_tests)}\n")
    f.write(f"- **Tests in Test Plan:** {len(tests_in_plan_sorted)}\n")
    f.write(f"- **Tests NOT in Test Plan:** {len(tests_not_in_plan)}\n")

print(f"Detailed report saved to: {output_file_details}")

# Statistics
print()
print("="*80)
print("STATISTICS")
print("="*80)
print(f"Total tests in CSV: {len(all_tests)}")
print(f"Tests in Test Plan PZ-14024: {len(tests_in_plan_sorted)}")
print(f"Tests NOT in Test Plan: {len(tests_not_in_plan)}")
print()

# Status breakdown
status_counts = {}
for test in tests_in_plan_sorted:
    status = test['status']
    status_counts[status] = status_counts.get(status, 0) + 1

print("Status breakdown:")
for status, count in sorted(status_counts.items()):
    print(f"  {status}: {count}")

print()
print("[SUCCESS] CSV parsing complete!")

