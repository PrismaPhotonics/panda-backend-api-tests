#!/usr/bin/env python3
"""
Generate GitHub Actions summary from JUnit XML.
"""
import xml.etree.ElementTree as ET
import os
import sys

def generate_summary(xml_file, summary_path, artifact_url=''):
    """Generate GitHub Actions summary from JUnit XML."""
    if not summary_path:
        print('GITHUB_STEP_SUMMARY not set')
        sys.exit(0)

    if not os.path.exists(xml_file):
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write('## Warning: No test results found\n\n')
            f.write('Test execution may have failed before generating reports.\n')
        return

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
        time_rounded = round(time, 2)
        status = '[OK]' if failures == 0 and errors == 0 else '[FAIL]'
        test_type = os.path.basename(xml_file).replace('junit-', '').replace('.xml', '').title()
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f'## {test_type} Results {status}\n\n')
            f.write('| Metric | Value |\n')
            f.write('|--------|-------|\n')
            f.write(f'| **Total Tests** | {total} |\n')
            f.write(f'| **Passed** | {passed} |\n')
            f.write(f'| **Failed** | {failures} |\n')
            f.write(f'| **Errors** | {errors} |\n')
            f.write(f'| **Skipped** | {skipped} |\n')
            f.write(f'| **Duration** | {time_rounded}s |\n\n')
            f.write('### Test Reports\n\n')
            
            if artifact_url:
                f.write(f'- [Download All Reports]({artifact_url}) - Download ZIP with HTML, JSON, and JUnit XML reports\n\n')
            else:
                repo = os.environ.get('GITHUB_REPOSITORY', '')
                run_id = os.environ.get('GITHUB_RUN_ID', '')
                server_url = os.environ.get('GITHUB_SERVER_URL', '')
                if repo and run_id and server_url:
                    run_url = f'{server_url}/{repo}/actions/runs/{run_id}'
                    artifact_name = f'{test_type.lower().replace(" ", "-")}-test-reports'
                    f.write(f'- [Download Reports]({run_url}) - Go to workflow run page and download `{artifact_name}` artifact\n\n')
                else:
                    f.write('- Download Reports - Check artifacts section in workflow run\n\n')
            
            if failures > 0 or errors > 0:
                f.write('### Failed Tests\n\n')
                failed_tests = root.findall('.//testcase[failure or error]')
                count = 0
                for test in failed_tests[:10]:
                    name = test.get('name', 'unknown')
                    classname = test.get('classname', 'unknown')
                    failure = test.find('failure')
                    error = test.find('error')
                    msg = ''
                    if failure is not None:
                        msg = failure.get('message', '') or (failure.text or '')[:200]
                    elif error is not None:
                        msg = error.get('message', '') or (error.text or '')[:200]
                    msg = msg.replace('`', "'")[:200]
                    f.write(f'- **{classname}::{name}**\n')
                    f.write(f'  ```{msg}```\n\n')
                    count += 1
                if len(failed_tests) > 10:
                    f.write(f'*... and {len(failed_tests) - 10} more failures*\n\n')
        
        print('[OK] GitHub Actions summary generated')
    except Exception as e:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f'## Error parsing test results\n\nError: {e}\n')
        print(f'Error: {e}')

if __name__ == '__main__':
    xml_file = sys.argv[1] if len(sys.argv) > 1 else ''
    summary_path = os.environ.get('GITHUB_STEP_SUMMARY', '')
    artifact_url = os.environ.get('ARTIFACT_DOWNLOAD_URL', '')
    
    if not xml_file:
        xml_file = os.environ.get('JUNIT_XML_FILE', '')
    
    if xml_file:
        generate_summary(xml_file, summary_path, artifact_url)
    else:
        print('Usage: generate_github_summary.py <xml_file>')
        sys.exit(1)

