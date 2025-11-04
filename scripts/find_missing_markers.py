#!/usr/bin/env python3
"""
Script to find all pytest markers used in tests and compare with pytest.ini
"""
import re
import glob
from pathlib import Path

# Find all markers in test files
markers_found = set()
test_files = glob.glob("tests/**/*.py", recursive=True)

for file_path in test_files:
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
            # Find all @pytest.mark.XXXX patterns
            markers = re.findall(r'@pytest\.mark\.(\w+)', content)
            markers_found.update(markers)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

# Read markers from pytest.ini
pytest_ini_markers = set()
try:
    with open("pytest.ini", encoding='utf-8') as f:
        content = f.read()
        # Extract markers from markers = section
        marker_section = re.search(r'markers\s*=\s*((?:[^\[]|\[[^\]]*\])*)', content, re.MULTILINE)
        if marker_section:
            marker_lines = marker_section.group(1)
            # Extract marker names (before the colon)
            markers_defined = re.findall(r'^\s*(\w+):', marker_lines, re.MULTILINE)
            pytest_ini_markers.update(markers_defined)
except Exception as e:
    print(f"Error reading pytest.ini: {e}")

# Find missing markers
missing_markers = markers_found - pytest_ini_markers

print("=" * 60)
print("MARKER ANALYSIS")
print("=" * 60)
print(f"\nTotal markers found in tests: {len(markers_found)}")
print(f"Markers defined in pytest.ini: {len(pytest_ini_markers)}")
print(f"\nMissing markers (need to add to pytest.ini): {len(missing_markers)}")
print("-" * 60)

if missing_markers:
    print("\nMissing markers:")
    for marker in sorted(missing_markers):
        print(f"  - {marker}")
    print("\n" + "=" * 60)
    print("Copy these to add to pytest.ini:")
    print("=" * 60)
    for marker in sorted(missing_markers):
        print(f"    {marker}: {marker.replace('_', ' ').title()} tests")
else:
    print("\n✅ All markers are defined in pytest.ini!")

print("\n" + "=" * 60)

