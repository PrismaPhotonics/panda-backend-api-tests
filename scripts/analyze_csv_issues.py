import csv
import re
from collections import defaultdict

# Read the CSV file
csv_file = r'c:\Users\roy.avrahami\Downloads\Jira (20).csv'
xray_list = r'C:\Projects\focus_server_automation\xray_tests_list.txt'

# Load Xray list
xray_tests = {}
with open(xray_list, 'r', encoding='utf-8') as f:
    for line in f:
        if ',' in line:
            parts = line.strip().split(',', 1)
            if len(parts) == 2:
                test_id = parts[0].strip()
                summary = parts[1].strip()
                xray_tests[test_id] = summary

# Read CSV
issues = []
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        issue_key = row.get('Issue key', '')
        summary = row.get('Summary', '')
        status = row.get('Status', '')
        
        if issue_key and summary:
            issues.append({
                'key': issue_key,
                'summary': summary,
                'status': status
            })

# Categorize issues
duplicates = defaultdict(list)
not_in_xray = []
visualization = []
roi_dynamic = []
singlechannel_duplicates = []
identical_descriptions = defaultdict(list)

for issue in issues:
    key = issue['key']
    summary = issue['summary'].lower()
    
    # Check if in Xray list
    if key not in xray_tests:
        not_in_xray.append(issue)
    
    # Find visualization tests (CAxis, Colormap, ROI related)
    if any(word in summary for word in ['caxis', 'colormap', 'roi']):
        visualization.append(issue)
    
    # SingleChannel duplicates check
    if 'singlechannel' in summary:
        # Extract channel number or specific test
        if 'channel zero' in summary or 'rejects' in summary:
            singlechannel_duplicates.append(issue)
    
    # Find identical summaries
    summary_normalized = re.sub(r'[^\w\s]', '', summary).lower().strip()
    identical_descriptions[summary_normalized].append(issue)

# Generate report
report = []
report.append("# CSV Analysis Report")
report.append("=" * 80)
report.append(f"\nTotal issues in CSV: {len(issues)}")
report.append(f"Issues in xray_tests_list.txt: {len(xray_tests)}")
report.append(f"Issues NOT in xray list: {len(not_in_xray)}")
report.append(f"Visualization tests: {len(visualization)}")
report.append(f"SingleChannel duplicates: {len(singlechannel_duplicates)}")
report.append("")

# Detailed analysis
if not_in_xray:
    report.append("\n## Issues NOT in Xray List")
    report.append("-" * 80)
    for issue in not_in_xray[:20]:  # Show first 20
        report.append(f"  {issue['key']}: {issue['summary']}")
    if len(not_in_xray) > 20:
        report.append(f"  ... and {len(not_in_xray) - 20} more")

if visualization:
    report.append("\n## Visualization Tests (ROI, CAxis, Colormap)")
    report.append("-" * 80)
    for issue in visualization[:30]:
        report.append(f"  {issue['key']}: {issue['summary']}")

if singlechannel_duplicates:
    report.append("\n## SingleChannel Tests (Potential Duplicates)")
    report.append("-" * 80)
    for issue in singlechannel_duplicates:
        report.append(f"  {issue['key']}: {issue['summary']}")

# Identical descriptions
identical_found = {k: v for k, v in identical_descriptions.items() if len(v) > 1}
if identical_found:
    report.append("\n## Identical Descriptions (True Duplicates)")
    report.append("-" * 80)
    for summary, items in list(identical_found.items())[:10]:
        report.append(f"\n  Summary: {items[0]['summary']}")
        for item in items:
            report.append(f"    {item['key']} ({item['status']})")

print("\n".join(report))

# Save report
with open('CSV_ANALYSIS_REPORT.md', 'w', encoding='utf-8') as f:
    f.write("\n".join(report))

print(f"\n✅ Report saved to CSV_ANALYSIS_REPORT.md")
