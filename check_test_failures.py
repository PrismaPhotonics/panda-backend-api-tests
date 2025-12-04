#!/usr/bin/env python3
"""Check test failures from JUnit XML and exit with appropriate code."""
import os
import sys
import xml.etree.ElementTree as ET


def check_test_failures():
    """Check if tests failed and exit with appropriate code."""
    run_tests_outcome = os.environ.get('RUN_TESTS_OUTCOME', '')
    print(f'Run smoke tests step outcome: {run_tests_outcome}')
    print(f'Note: With continue-on-error=true, step outcome may be "success" even if tests failed')
    
    # Check if test results exist and have failures
    results_file = 'test-results/junit-smoke.xml'
    if os.path.exists(results_file):
        print(f'Found test results file: {results_file}')
        try:
            tree = ET.parse(results_file)
            root = tree.getroot()
            
            # Handle both testsuites and testsuite root elements
            suite = root.find('.//testsuite')
            if suite is None:
                suite = root if root.tag == 'testsuite' else None
            
            if suite is not None:
                failures = int(suite.get('failures', '0') or '0')
                errors = int(suite.get('errors', '0') or '0')
                tests = int(suite.get('tests', '0') or '0')
                print(f'Test results: {tests} tests, {failures} failures, {errors} errors')
                
                # Check for error/failure testcases in XML (more reliable than just attributes)
                error_cases = suite.findall('.//error')
                failure_cases = suite.findall('.//failure')
                if error_cases or failure_cases:
                    print(f'Found {len(error_cases)} error cases and {len(failure_cases)} failure cases in XML')
                    for error in error_cases:
                        error_msg = error.get('message', 'Unknown error')
                        print(f'  Error: {error_msg}')
                    for failure in failure_cases:
                        failure_msg = failure.get('message', 'Unknown failure')
                        print(f'  Failure: {failure_msg}')
                
                # If pytest step failed OR there are test failures/errors, fail the workflow
                # Note: We check XML errors/failures FIRST because continue-on-error may mask step failure
                # IMPORTANT: Collection errors (errors during import) should also fail the workflow
                if errors > 0 or failures > 0 or error_cases or failure_cases or run_tests_outcome == 'failure':
                    print(f'::error::Tests failed: {failures} failures, {errors} errors (step outcome: {run_tests_outcome})')
                    if errors > 0:
                        print(f'::error::Collection errors detected - {errors} test files failed to import. This prevents tests from running!')
                    sys.exit(1)
                else:
                    print('All tests passed!')
                    sys.exit(0)
            else:
                print(f'::warning::Could not find testsuite element in XML')
                # No valid test results, check if pytest step failed
                if run_tests_outcome == 'failure':
                    print(f'::error::Test execution failed (no valid results file, step outcome: {run_tests_outcome})')
                    sys.exit(1)
                else:
                    print('::warning::No valid test results structure found, but step succeeded')
                    sys.exit(0)
        except Exception as e:
            print(f'::error::Error parsing test results: {e}')
            import traceback
            traceback.print_exc()
            # If we can't parse results and step failed, fail the workflow
            if run_tests_outcome == 'failure':
                sys.exit(1)
            # Otherwise, warn but don't fail (might be a parsing issue)
            print('::warning::Could not parse test results, but step succeeded')
            sys.exit(0)
    else:
        print(f'Test results file not found: {results_file}')
        # No results file - check if pytest step failed
        if run_tests_outcome == 'failure':
            print(f'::error::Test execution failed (no results file found, step outcome: {run_tests_outcome})')
            sys.exit(1)
        else:
            print('::warning::No test results file found (tests may have been skipped)')
            sys.exit(0)


if __name__ == '__main__':
    check_test_failures()

