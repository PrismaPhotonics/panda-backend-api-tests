#!/usr/bin/env python3
"""
Parse JUnit XML and print summary to console.
"""
import xml.etree.ElementTree as ET
import sys

def parse_junit_xml(xml_file):
    """Parse JUnit XML file and print summary."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        if root.tag == 'testsuites':
            suites = root.findall('.//testsuite')
            total = sum(int(s.get('tests', 0)) for s in suites)
            failures = sum(int(s.get('failures', 0)) for s in suites)
            errors = sum(int(s.get('errors', 0)) for s in suites)
            skipped = sum(int(s.get('skipped', 0)) for s in suites)
            time = sum(float(s.get('time', 0)) for s in suites)
        elif root.tag == 'testsuite':
            total = int(root.get('tests', 0))
            failures = int(root.get('failures', 0))
            errors = int(root.get('errors', 0))
            skipped = int(root.get('skipped', 0))
            time = float(root.get('time', 0))
        else:
            testcases = root.findall('.//testcase')
            total = len(testcases)
            failures = len(root.findall('.//failure'))
            errors = len(root.findall('.//error'))
            skipped = len(root.findall('.//skipped'))
            time = 0.0
        
        passed = total - failures - errors - skipped
        print(f'Total Tests: {total}')
        print(f'Passed: {passed}')
        print(f'Failed: {failures}')
        print(f'Errors: {errors}')
        print(f'Skipped: {skipped}')
        print(f'Duration: {time:.2f}s')
    except Exception as e:
        print(f'Error parsing XML: {e}')
        sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: parse_junit_xml.py <xml_file>')
        sys.exit(1)
    parse_junit_xml(sys.argv[1])

