"""
Check Xray coverage for all tests in xray_tests_list.txt
"""
import re
from pathlib import Path
from collections import defaultdict

print("Loading Xray list...")

# Load all test IDs from xray_tests_list.txt
xray_tests = set()
with open('xray_tests_list.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            parts = line.strip().split(',', 1)
            test_id = parts[0].strip()
            if test_id.startswith('PZ-'):
                xray_tests.add(test_id)

print(f"Found {len(xray_tests)} tests in xray_tests_list.txt")

# Scan automation for Xray markers
print("\nScanning automation tests...")
automation_tests = {}

# Find all Python test files
for test_file in Path('tests').rglob('*.py'):
    try:
        content = test_file.read_text(encoding='utf-8')
        
        # Find all @pytest.mark.xray("PZ-XXXXX") patterns
        matches = re.findall(r'@pytest\.mark\.xray\(["\'](PZ-\d+)["\']\)', content)
        
        for match in matches:
            automation_tests[match] = str(test_file.name)
    except Exception as e:
        pass  # Skip files that can't be read

print(f"Found {len(automation_tests)} Xray markers in automation")

# Find missing and covered
missing = xray_tests - set(automation_tests.keys())
covered = xray_tests & set(automation_tests.keys())

# Generate report
report = []
report.append("# Xray Test Coverage Report\n")
report.append(f"**Generated:** {Path(__file__).stat().st_mtime}\n\n")
report.append("## Summary\n\n")
report.append(f"- Total tests in xray_tests_list.txt: **{len(xray_tests)}**\n")
report.append(f"- Tests with automation: **{len(automation_tests)}**\n")
report.append(f"- Tests without automation: **{len(missing)}**\n")
report.append(f"- Coverage: **{len(automation_tests)/len(xray_tests)*100:.1f}%**\n\n")

if missing:
    report.append(f"## ⚠️ Missing Automation Coverage ({len(missing)} tests)\n\n")
    report.append("These tests are in xray_tests_list.txt but do NOT have automation:\n\n")
    report.append("| Test ID | Status |\n")
    report.append("|---------|--------|\n")
    for test_id in sorted(missing):
        report.append(f"| {test_id} | ⚠️ Missing |\n")
    report.append("\n")
else:
    report.append("## ✅ All Tests Have Automation Coverage!\n\n")

# Save report
with open('XRAY_COVERAGE_FULL_REPORT.md', 'w', encoding='utf-8') as f:
    f.writelines(report)

# Print summary
print("\n" + "="*80)
print("COVERAGE ANALYSIS")
print("="*80)
print()
print(f"Total in Xray List:    {len(xray_tests)}")
print(f"With Automation:       {len(automation_tests)}")
print(f"Without Automation:    {len(missing)}")
print()
print(f"Coverage: {len(automation_tests)/len(xray_tests)*100:.1f}%")
print()

if missing:
    print("⚠️  MISSING TESTS:")
    for test_id in sorted(missing):
        print(f"  - {test_id}")
else:
    print("✅ ALL TESTS COVERED!")

print("\nReport saved to: XRAY_COVERAGE_FULL_REPORT.md")

