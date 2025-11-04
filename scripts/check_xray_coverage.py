"""
Check Xray Coverage - Which tests from xray_tests_list.txt have automation tests?
"""
import re
from pathlib import Path

# Load Xray list
xray_tests = set()
with open('xray_tests_list.txt', 'r') as f:
    for line in f:
        if line.strip():
            parts = line.strip().split(',', 1)
            if len(parts) > 0 and parts[0].startswith('PZ-'):
                xray_tests.add(parts[0].strip())

print(f"Loaded {len(xray_tests)} tests from xray_tests_list.txt")
print()

# Scan automation tests for Xray markers
automation_tests = set()
test_files = []

for test_file in Path('tests').rglob('test_*.py'):
    test_files.append(str(test_file))
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Find all @pytest.mark.xray("PZ-XXXX") patterns
            matches = re.findall(r'@pytest\.mark\.xray\(["\'](PZ-\d+)["\']\)', content)
            for match in matches:
                automation_tests.add(match)
                print(f"  Found {match} in {test_file.name}")
    except Exception as e:
        pass

print()
print(f"Found {len(automation_tests)} Xray tests in automation")
print()

# Find missing
missing = xray_tests - automation_tests

print("=" * 80)
print("COVERAGE ANALYSIS")
print("=" * 80)
print()
print(f"Tests in Xray List: {len(xray_tests)}")
print(f"Tests with Automation: {len(automation_tests)}")
print(f"Tests without Automation: {len(missing)}")
print()

if missing:
    print("⚠️  TESTS WITHOUT AUTOMATION:")
    print("-" * 80)
    for test_id in sorted(missing):
        print(f"  - {test_id}")
else:
    print("✅ ALL TESTS HAVE AUTOMATION!")

print()
print("=" * 80)

