#!/usr/bin/env python3
"""Check test failures from JUnit XML and exit with appropriate code."""
import os
import sys
import xml.etree.ElementTree as ET


def check_test_failures():
    """Check if tests failed and exit with appropriate code."""
    run_tests_outcome = os.environ.get('RUN_TESTS_OUTCOME', '')
    print(f'Run smoke tests step outcome: {run_tests_outcome}')
    
    # Check if test results exist and have failures
    results_file = 'test-results/junit-smoke.xml'
    if os.path.exists(results_file):
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
                print(f'Test results: {failures} failures, {errors} errors')
                
                # If pytest step failed or there are test failures/errors, fail the workflow
                if run_tests_outcome == 'failure' or failures > 0 or errors > 0:
                    print(f'::error::Tests failed: {failures} failures, {errors} errors (step outcome: {run_tests_outcome})')
                    sys.exit(1)
                else:
                    print('All tests passed!')
                    sys.exit(0)
            else:
                # No valid test results, check if pytest step failed
                if run_tests_outcome == 'failure':
                    print(f'::error::Test execution failed (no valid results file, step outcome: {run_tests_outcome})')
                    sys.exit(1)
        except Exception as e:
            print(f'::error::Error parsing test results: {e}')
            if run_tests_outcome == 'failure':
                sys.exit(1)
    else:
        # No results file - check if pytest step failed
        if run_tests_outcome == 'failure':
            print(f'::error::Test execution failed (no results file found, step outcome: {run_tests_outcome})')
            sys.exit(1)
        else:
            print('::warning::No test results file found (tests may have been skipped)')
            sys.exit(0)


if __name__ == '__main__':
    check_test_failures()

