#!/usr/bin/env python3
"""
Compare CSV with xray_tests_list.txt to find missing tests.
"""
import csv

# Read CSV
csv_tests = set()
csv_path = "c:/Users/roy.avrahami/Downloads/Test plan (PZ-13756) by Roy Avrahami (Jira) (1).csv"

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        issue_key = row.get('Issue key', '').strip()
        if issue_key:
            csv_tests.add(issue_key)

print(f"Tests in CSV: {len(csv_tests)}")

# Read xray_tests_list.txt
list_tests = set()
with open("xray_tests_list.txt", 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and line.startswith('PZ-'):
            test_id = line.split(',')[0].strip()
            list_tests.add(test_id)

print(f"Tests in list: {len(list_tests)}")

# Find missing
missing_in_list = csv_tests - list_tests
missing_in_csv = list_tests - csv_tests

print("\n" + "="*80)
print(f"MISSING IN xray_tests_list.txt (but in CSV): {len(missing_in_list)}")
print("="*80)

if missing_in_list:
    for test_id in sorted(missing_in_list):
        print(f"  {test_id}")

print("\n" + "="*80)
print(f"EXTRA IN xray_tests_list.txt (not in CSV): {len(missing_in_csv)}")
print("="*80)

if missing_in_csv:
    for test_id in sorted(missing_in_csv):
        print(f"  {test_id}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"CSV tests: {len(csv_tests)}")
print(f"List tests: {len(list_tests)}")
print(f"Missing in list: {len(missing_in_list)}")
print(f"Extra in list: {len(missing_in_csv)}")
print("="*80)

