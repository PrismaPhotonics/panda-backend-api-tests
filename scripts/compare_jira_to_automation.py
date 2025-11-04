"""
Compare Jira test cases from CSV with existing automation tests
"""
import csv
import re
from pathlib import Path
from collections import defaultdict

# Load Xray list (already mapped tests)
xray_tests = {}
with open('xray_tests_list.txt', 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split(',', 1)
        if len(parts) > 0 and parts[0].startswith('PZ-'):
            xray_tests[parts[0].strip()] = parts[1].strip() if len(parts) > 1 else ""

# Load Jira CSV
jira_tests = {}
jira_csv_path = r'c:\Users\roy.avrahami\Downloads\Jira (21).csv'

try:
    with open(jira_csv_path, 'r', encoding='utf-8') as f:
        # Skip header
        header = f.readline()
        
        # Read all lines manually to handle CSV with duplicate column names
        for line in f:
            if line.strip():
                # Parse line manually - get Issue key
                parts = line.split(',')
                if len(parts) > 1 and parts[1].startswith('PZ-'):
                    issue_key = parts[1].strip()
                    summary = parts[0].strip().replace('"', '')
                    jira_tests[issue_key] = summary
except Exception as e:
    print(f"Error reading CSV: {e}")
    # Try alternative method
    import pandas as pd
    try:
        df = pd.read_csv(jira_csv_path)
        for idx, row in df.iterrows():
            issue_key = str(row.get('Issue key', '')).strip()
            if issue_key.startswith('PZ-'):
                summary = str(row.get('Summary', '')).strip()
                jira_tests[issue_key] = summary
    except Exception as e2:
        print(f"Alternative method also failed: {e2}")

# Get all test files from automation
automation_tests = {}
test_files = []

for test_file in Path('tests').rglob('test_*.py'):
    test_files.append(str(test_file))
    
    # Try to extract test class names and functions
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract test function names
            test_funcs = re.findall(r'^def\s+(test_\w+)', content, re.MULTILINE)
            for func in test_funcs:
                automation_tests[func] = str(test_file)
    except Exception as e:
        pass

# Compare and generate report
report = []
report.append("# Jira vs Automation Comparison Report\n")
report.append(f"Generated: {Path('.').resolve()}\n\n")
report.append(f"## Statistics\n\n")
report.append(f"- Jira CSV tests: {len(jira_tests)}\n")
report.append(f"- Xray mapped tests: {len(xray_tests)}\n")
report.append(f"- Automation test files: {len(test_files)}\n")
report.append(f"- Automation test functions: {len(automation_tests)}\n\n")

# Find tests in Jira but NOT in Xray (not yet automated)
jira_not_in_xray = set(jira_tests.keys()) - set(xray_tests.keys())

if jira_not_in_xray:
    report.append("## Tests in Jira but NOT in Xray (Not Yet Automated)\n\n")
    for issue_key in sorted(jira_not_in_xray):
        summary = jira_tests[issue_key]
        report.append(f"- **{issue_key}**: {summary}\n")
    report.append("\n")

# Find tests in Xray but NOT in Jira (old/removed tests)
xray_not_in_jira = set(xray_tests.keys()) - set(jira_tests.keys())

if xray_not_in_jira:
    report.append("## Tests in Xray but NOT in Jira CSV (Old/Removed)\n\n")
    for issue_key in sorted(xray_not_in_jira):
        summary = xray_tests[issue_key]
        report.append(f"- **{issue_key}**: {summary}\n")
    report.append("\n")

# Save report
with open('JIRA_VS_AUTOMATION_COMPARISON.md', 'w', encoding='utf-8') as f:
    f.writelines(report)

print("Comparison complete. Report saved to JIRA_VS_AUTOMATION_COMPARISON.md")
print(f"\nFound {len(jira_not_in_xray)} tests in Jira not yet in Xray")
print(f"Found {len(xray_not_in_jira)} tests in Xray not in Jira CSV")

