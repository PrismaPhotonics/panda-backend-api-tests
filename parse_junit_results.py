#!/usr/bin/env python3
"""Parse JUnit XML files and create GitHub Actions summary."""
import xml.etree.ElementTree as ET
import glob
import os
import sys

def parse_junit_xml():
    """Parse all JUnit XML files and create summary."""
    xml_files = glob.glob('test-results/*.xml')
    
    if not xml_files:
        print("No JUnit XML files found in test-results/")
        return
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    total_time = 0.0
    failed_tests = []
    passed_tests = []
    skipped_tests = []
    
    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Handle both testsuites and testsuite elements
            suites = root.findall('.//testsuite') if root.tag != 'testsuite' else [root]
            if not suites:
                suites = [root]
            
            for suite in suites:
                total_tests += int(suite.get('tests', 0))
                total_failures += int(suite.get('failures', 0))
                total_errors += int(suite.get('errors', 0))
                total_skipped += int(suite.get('skipped', 0))
                total_time += float(suite.get('time', 0))
                
                # Process all test cases
                for testcase in suite.findall('.//testcase'):
                    test_name = f"{testcase.get('classname', '')}::{testcase.get('name', 'unknown')}"
                    failure = testcase.find('failure')
                    error = testcase.find('error')
                    skipped = testcase.find('skipped')
                    
                    if failure is not None or error is not None:
                        message = (failure or error).text or ''
                        failed_tests.append({
                            'name': test_name,
                            'status': 'failed' if failure else 'error',
                            'message': message[:200] if message else ''
                        })
                    elif skipped is not None:
                        skipped_tests.append({
                            'name': test_name,
                            'message': skipped.text or '' if skipped.text else ''
                        })
                    else:
                        passed_tests.append({
                            'name': test_name
                        })
        except Exception as e:
            print(f"Error parsing {xml_file}: {e}", file=sys.stderr)
    
    # Write to GitHub step summary
    summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
    if not summary_path:
        print("GITHUB_STEP_SUMMARY not set")
        return
    
    passed = total_tests - total_failures - total_errors - total_skipped
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write('## 📊 Test Results Summary\n\n')
        f.write(f'**Total Tests**: {total_tests}  \n')
        f.write(f'**✅ Passed**: {passed}  \n')
        f.write(f'**❌ Failed**: {total_failures}  \n')
        f.write(f'**⚠️ Errors**: {total_errors}  \n')
        f.write(f'**⏭️ Skipped**: {total_skipped}  \n')
        f.write(f'**⏱️ Duration**: {total_time:.2f}s  \n\n')
        
        f.write('### 📋 View Results\n\n')
        repo = os.environ.get('GITHUB_REPOSITORY', '')
        run_id = os.environ.get('GITHUB_RUN_ID', '')
        check_run_id = os.environ.get('CHECK_RUN_ID', '')
        
        if repo and run_id:
            f.write(f'**Workflow Run ID**: `{run_id}`  \n')
            if check_run_id:
                f.write(f'**Check Run ID**: `{check_run_id}`  \n')
            f.write(f'**Repository**: `{repo}`  \n')
            f.write('  \n')
            
            if check_run_id:
                # We have the check run ID - create the proper link
                f.write(f'- [📊 View Pytest Results Check](https://github.com/{repo}/runs/{check_run_id}) - Opens in right panel  \n\n')
            else:
                # Fallback - show instructions to find it
                f.write('**Check Run URL** (from test-reporter logs):  \n')
                f.write(f'Look for "Check run HTML" in the "Publish Test Results" step logs  \n')
                f.write(f'Format: `https://github.com/{repo}/runs/{{CHECK_RUN_ID}}`  \n\n')
                f.write('**To find the Check Run ID**:  \n')
                f.write('1. Check the "Publish Test Results" step logs  \n')
                f.write('2. Look for the line: `Check run HTML: https://github.com/.../runs/{{ID}}`  \n')
                f.write('3. The ID in that URL is the check run ID  \n\n')
        
        # Show passed tests summary (grouped by file/class)
        if passed_tests:
            f.write(f'### ✅ Passed Tests ({len(passed_tests)})\n\n')
            # Group by classname for better readability
            tests_by_class = {}
            for test in passed_tests:
                classname = test['name'].split('::')[0] if '::' in test['name'] else 'Other'
                if classname not in tests_by_class:
                    tests_by_class[classname] = []
                tests_by_class[classname].append(test['name'].split('::')[-1] if '::' in test['name'] else test['name'])
            
            # Show summary by class (limit to top 20 classes for better visibility)
            for classname, test_names in list(tests_by_class.items())[:20]:
                f.write(f'**{classname}** ({len(test_names)} tests)  \n')
                for test_name in test_names[:10]:  # Show first 10 tests per class (increased from 5)
                    f.write(f'  - ✅ {test_name}  \n')
                if len(test_names) > 10:
                    f.write(f'  - ... and {len(test_names) - 10} more  \n')
                f.write('  \n')
            
            if len(tests_by_class) > 20:
                remaining = sum(len(tests) for tests in list(tests_by_class.values())[20:])
                f.write(f'*... and {remaining} more tests in {len(tests_by_class) - 20} more classes*  \n\n')
        
        # Show skipped tests
        if skipped_tests:
            f.write(f'### ⏭️ Skipped Tests ({len(skipped_tests)})\n\n')
            for test in skipped_tests[:10]:  # Limit to 10
                f.write(f'- **{test["name"]}**  \n')
            if len(skipped_tests) > 10:
                f.write(f'\n*... and {len(skipped_tests) - 10} more skipped tests*  \n')
            f.write('  \n')
        
        # Show failed tests
        if failed_tests or total_failures > 0 or total_errors > 0:
            f.write(f'### ❌ Failed Tests ({len(failed_tests)} total, {total_failures} failures, {total_errors} errors)\n\n')
            # Show all failed tests (increased limit from 20 to 50)
            for test in failed_tests[:50]:
                f.write(f'- **{test["name"]}** ({test["status"]})  \n')
                if test['message']:
                    message = test['message']
                    truncated_message = message[:200]  # Increased from 150 to 200 chars
                    ellipsis = '...' if len(message) > 200 else ''
                    f.write(f'  ```\n  {truncated_message}{ellipsis}\n  ```  \n\n')
            if len(failed_tests) > 50:
                f.write(f'\n*... and {len(failed_tests) - 50} more failed tests*  \n')
            f.write('\n')
        elif not failed_tests:
            f.write('### ✅ All Tests Passed!\n\n')

if __name__ == '__main__':
    parse_junit_xml()

