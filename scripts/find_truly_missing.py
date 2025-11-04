"""
Find tests that are truly missing from automation
"""
import re
from pathlib import Path

# Load all test IDs from xray_tests_list.txt
print("Loading xray_tests_list.txt...")
xray_test_ids = []
with open('xray_tests_list.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            parts = line.strip().split(',', 1)
            test_id = parts[0].strip()
            if test_id.startswith('PZ-'):
                xray_test_ids.append((test_id, parts[1].strip() if len(parts) > 1 else ""))

print(f"Found {len(xray_test_ids)} tests in xray_tests_list.txt\n")

# Load all markers from automation
automation_test_ids = set()
for test_file in Path('tests').rglob('*.py'):
    try:
        content = test_file.read_text(encoding='utf-8')
        # Find all PZ-XXXXX patterns in xray markers
        matches = re.findall(r'@pytest\.mark\.xray\(["\'](PZ-\d+)["\']', content)
        automation_test_ids.update(matches)
    except Exception:
        pass

print(f"Found {len(automation_test_ids)} unique test IDs in automation\n")

# Find missing tests
missing = []
for test_id, description in xray_test_ids:
    if test_id not in automation_test_ids:
        missing.append((test_id, description))

print("=" * 80)
print(f"TRULY MISSING TESTS: {len(missing)}")
print("=" * 80)

for test_id, description in missing:
    print(f"{test_id}: {description}")

print(f"\nTotal missing: {len(missing)}")

