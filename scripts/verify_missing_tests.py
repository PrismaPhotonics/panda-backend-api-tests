"""
Verify which tests are truly missing from automation
"""
import re
from pathlib import Path

# Load Xray list
print("Loading xray_tests_list.txt...")
xray_tests = {}
with open('xray_tests_list.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            parts = line.strip().split(',', 1)
            test_id = parts[0].strip()
            if test_id.startswith('PZ-'):
                description = parts[1].strip() if len(parts) > 1 else "No description"
                xray_tests[test_id] = description

print(f"Found {len(xray_tests)} tests in xray_tests_list.txt")

# The supposedly "missing" tests
missing_tests = [
    "PZ-13903", "PZ-13873", "PZ-13865", "PZ-13863", "PZ-13857",
    "PZ-13855", "PZ-13854", "PZ-13852", "PZ-13837", "PZ-13836",
    "PZ-13833", "PZ-13832", "PZ-13822", "PZ-13769", "PZ-13766",
    "PZ-13762", "PZ-13685", "PZ-13684", "PZ-13604", "PZ-13603",
    "PZ-13601", "PZ-13600", "PZ-13562", "PZ-13561", "PZ-13560",
    "PZ-13555", "PZ-13554", "PZ-13552"
]

print(f"\nChecking {len(missing_tests)} supposedly missing tests...")

# Find all markers in automation
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

# Check each missing test
truly_missing = []
covered_by_other = []

for test_id in missing_tests:
    if test_id in automation_test_ids:
        covered_by_other.append((test_id, xray_tests.get(test_id, "Unknown")))
    else:
        truly_missing.append((test_id, xray_tests.get(test_id, "Unknown")))

print("=" * 80)
print("RESULTS")
print("=" * 80)
print(f"\n[OK] Tests that ARE covered ({len(covered_by_other)}):")
for test_id, desc in covered_by_other:
    print(f"  [OK] {test_id}: {desc}")

print(f"\n[MISSING] Tests truly missing ({len(truly_missing)}):")
for test_id, desc in truly_missing:
    print(f"  [MISSING] {test_id}: {desc}")

