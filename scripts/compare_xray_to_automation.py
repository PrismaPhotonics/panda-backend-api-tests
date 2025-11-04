"""
Compare xray_tests_list.txt with automation tests
Find:
1. Tests in Xray list but NOT in automation
2. Tests in automation but NOT in Xray list
"""

import re
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("Xray vs Automation Comparison")
print("=" * 80)

# 1. Load Xray list
print("\n1. Loading xray_tests_list.txt...")
xray_tests = set()
with open('xray_tests_list.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            parts = line.strip().split(',', 1)
            test_id = parts[0].strip()
            if test_id.startswith('PZ-'):
                xray_tests.add(test_id)

print(f"   Found {len(xray_tests)} tests in xray_tests_list.txt")

# 2. Load automation tests
print("\n2. Scanning automation tests...")
automation_tests = set()

# Find all Python test files
for test_file in Path('tests').rglob('*.py'):
    try:
        content = test_file.read_text(encoding='utf-8')
        
        # Find all @pytest.mark.xray("PZ-XXXXX") patterns
        # Handle both single and multiple markers: @pytest.mark.xray("PZ-123") and @pytest.mark.xray("PZ-123", "PZ-456")
        matches_single = re.findall(r'@pytest\.mark\.xray\(["\'](PZ-\d+)["\']\)', content)
        matches_multi = re.findall(r'@pytest\.mark\.xray\(["\'](PZ-\d+)["\']', content)
        matches = list(set(matches_single + matches_multi))
        
        for match in matches:
            automation_tests.add(match)
    except Exception:
        pass

print(f"   Found {len(automation_tests)} unique Xray markers in automation")

# 3. Find differences
print("\n3. Analyzing differences...")
tests_in_xray_not_in_automation = xray_tests - automation_tests
tests_in_automation_not_in_xray = automation_tests - xray_tests
tests_common = xray_tests & automation_tests

# 4. Generate report
report = []
report.append("# Xray vs Automation - Complete Analysis\n")
report.append("**Generated:** " + str(Path.cwd()) + "\n\n")
report.append("## Summary\n\n")
report.append(f"- Tests in xray_tests_list.txt: **{len(xray_tests)}**\n")
report.append(f"- Tests in automation: **{len(automation_tests)}**\n")
report.append(f"- Common tests: **{len(tests_common)}**\n")
report.append(f"- In Xray but NOT in automation: **{len(tests_in_xray_not_in_automation)}**\n")
report.append(f"- In automation but NOT in Xray: **{len(tests_in_automation_not_in_xray)}**\n\n")

# Tests in Xray but NOT in automation
if tests_in_xray_not_in_automation:
    report.append("## ⚠️ Tests in xray_tests_list.txt but NOT in Automation\n\n")
    report.append(f"**Total: {len(tests_in_xray_not_in_automation)} tests**\n\n")
    report.append("These tests need automation implementation:\n\n")
    report.append("| Test ID | Description |\n")
    report.append("|---------|-------------|\n")
    
    # Get descriptions from xray_tests_list.txt
    with open('xray_tests_list.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split(',', 1)
                test_id = parts[0].strip()
                if test_id in tests_in_xray_not_in_automation:
                    description = parts[1].strip() if len(parts) > 1 else "No description"
                    report.append(f"| {test_id} | {description} |\n")
    
    report.append("\n")

# Tests in automation but NOT in Xray
if tests_in_automation_not_in_xray:
    report.append("## ⚠️ Tests in Automation but NOT in xray_tests_list.txt\n\n")
    report.append(f"**Total: {len(tests_in_automation_not_in_xray)} tests**\n\n")
    report.append("These tests exist in automation but are missing from Xray list:\n\n")
    report.append("| Test ID | Status |\n")
    report.append("|---------|--------|\n")
    for test_id in sorted(tests_in_automation_not_in_xray):
        report.append(f"| {test_id} | ⚠️ Missing from Xray list |\n")
    
    report.append("\n")
    report.append("**Recommendation:** Add these to xray_tests_list.txt or remove from automation\n\n")

# Common tests
report.append("## ✅ Common Tests\n\n")
report.append(f"**Total: {len(tests_common)} tests that are in both**\n\n")

# Save report
with open('XRAY_VS_AUTOMATION_FULL_REPORT.md', 'w', encoding='utf-8') as f:
    f.writelines(report)

# Print summary
print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)
print()
print(f"[OK] Common tests: {len(tests_common)}")
print(f"[WARN] In Xray but NOT in automation: {len(tests_in_xray_not_in_automation)}")
print(f"[WARN] In automation but NOT in Xray: {len(tests_in_automation_not_in_xray)}")
print()

if tests_in_xray_not_in_automation:
    print("[WARN] TESTS NEEDING AUTOMATION:")
    for test_id in sorted(tests_in_xray_not_in_automation):
        print(f"  - {test_id}")
    print()

if tests_in_automation_not_in_xray:
    print("[WARN] TESTS IN AUTOMATION BUT NOT IN XRAY LIST:")
    for test_id in sorted(tests_in_automation_not_in_xray):
        print(f"  - {test_id}")
    print()

print(f"\nReport saved to: XRAY_VS_AUTOMATION_FULL_REPORT.md")

