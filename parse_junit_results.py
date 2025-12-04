#!/usr/bin/env python3
"""
Parse JUnit XML files and create comprehensive GitHub Actions summary.

This script creates a clear, ordered test results summary that provides
a full picture of the system status for each test run.
"""
import xml.etree.ElementTree as ET
import glob
import os
import sys
from datetime import datetime
from collections import OrderedDict


def get_test_category(classname: str) -> str:
    """Categorize test by its module/class name."""
    if 'integration' in classname.lower():
        return '🔗 Integration Tests'
    elif 'load' in classname.lower() or 'performance' in classname.lower():
        return '📊 Load & Performance Tests'
    elif 'smoke' in classname.lower():
        return '💨 Smoke Tests'
    elif 'unit' in classname.lower():
        return '🧪 Unit Tests'
    elif 'security' in classname.lower():
        return '🔒 Security Tests'
    elif 'stress' in classname.lower():
        return '💪 Stress Tests'
    elif 'data_quality' in classname.lower():
        return '📋 Data Quality Tests'
    elif 'infrastructure' in classname.lower():
        return '🏗️ Infrastructure Tests'
    else:
        return '📁 Other Tests'


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def get_status_emoji(passed: int, failed: int, errors: int) -> str:
    """Get overall status emoji based on results."""
    if failed == 0 and errors == 0:
        return "✅"
    elif failed > 0 or errors > 0:
        return "❌"
    else:
        return "⚠️"


def parse_junit_xml():
    """Parse all JUnit XML files and create comprehensive summary."""
    xml_files = glob.glob('test-results/*.xml')
    
    if not xml_files:
        print("No JUnit XML files found in test-results/")
        # Still create a summary showing no tests were found
        write_empty_summary()
        return
    
    # Collect all test data
    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    total_time = 0.0
    
    # Organize tests by category and status
    tests_by_category = OrderedDict()
    all_tests = []
    failed_tests = []
    error_tests = []
    skipped_tests = []
    passed_tests = []
    
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
                    classname = testcase.get('classname', 'Unknown')
                    test_name = testcase.get('name', 'unknown')
                    test_time = float(testcase.get('time', 0))
                    full_name = f"{classname}::{test_name}"
                    
                    failure = testcase.find('failure')
                    error = testcase.find('error')
                    skipped_elem = testcase.find('skipped')
                    
                    # Determine status
                    if failure is not None:
                        status = 'failed'
                        message = failure.text or failure.get('message', '')
                        failed_tests.append({
                            'name': full_name,
                            'short_name': test_name,
                            'classname': classname,
                            'status': status,
                            'message': message[:500] if message else '',
                            'time': test_time
                        })
                    elif error is not None:
                        status = 'error'
                        message = error.text or error.get('message', '')
                        error_tests.append({
                            'name': full_name,
                            'short_name': test_name,
                            'classname': classname,
                            'status': status,
                            'message': message[:500] if message else '',
                            'time': test_time
                        })
                    elif skipped_elem is not None:
                        status = 'skipped'
                        message = skipped_elem.text or skipped_elem.get('message', '')
                        skipped_tests.append({
                            'name': full_name,
                            'short_name': test_name,
                            'classname': classname,
                            'status': status,
                            'message': message[:200] if message else '',
                            'time': test_time
                        })
                    else:
                        status = 'passed'
                        passed_tests.append({
                            'name': full_name,
                            'short_name': test_name,
                            'classname': classname,
                            'status': status,
                            'time': test_time
                        })
                    
                    # Categorize test
                    category = get_test_category(classname)
                    if category not in tests_by_category:
                        tests_by_category[category] = {
                            'passed': [], 'failed': [], 'error': [], 'skipped': []
                        }
                    tests_by_category[category][status].append({
                        'name': full_name,
                        'short_name': test_name,
                        'classname': classname,
                        'time': test_time,
                        'message': message if status in ['failed', 'error', 'skipped'] else ''
                    })
                    
        except Exception as e:
            print(f"Error parsing {xml_file}: {e}", file=sys.stderr)
    
    # Write comprehensive summary
    write_summary(
        total_tests, total_failures, total_errors, total_skipped, total_time,
        tests_by_category, passed_tests, failed_tests, error_tests, skipped_tests
    )


def write_empty_summary():
    """Write summary when no test results are found."""
    summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
    if not summary_path:
        print("GITHUB_STEP_SUMMARY not set")
        return
    
    environment = os.environ.get('TARGET_ENVIRONMENT', 'unknown')
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write('# ⚠️ Test Results Summary\n\n')
        f.write(f'**Environment:** {environment.upper()}\n\n')
        f.write('## No Test Results Found\n\n')
        f.write('No JUnit XML files were found in `test-results/` directory.\n\n')
        f.write('This usually means:\n')
        f.write('- Tests failed to start (check pytest logs)\n')
        f.write('- Configuration error prevented test execution\n')
        f.write('- Test collection failed\n\n')
        f.write('**Please check the workflow logs above for errors.**\n')


def write_summary(total_tests, total_failures, total_errors, total_skipped, total_time,
                  tests_by_category, passed_tests, failed_tests, error_tests, skipped_tests):
    """Write comprehensive test summary to GitHub Actions."""
    summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
    if not summary_path:
        print("GITHUB_STEP_SUMMARY not set - printing to stdout")
        summary_path = None
    
    passed = len(passed_tests)
    environment = os.environ.get('TARGET_ENVIRONMENT', 'unknown')
    repo = os.environ.get('GITHUB_REPOSITORY', '')
    run_id = os.environ.get('GITHUB_RUN_ID', '')
    sha = os.environ.get('GITHUB_SHA', '')[:7] if os.environ.get('GITHUB_SHA') else ''
    
    # Determine overall status
    status_emoji = get_status_emoji(passed, total_failures, total_errors)
    
    # Build summary content
    lines = []
    
    # ==========================================
    # HEADER SECTION
    # ==========================================
    lines.append(f'# {status_emoji} Test Results Summary\n')
    lines.append(f'**Run Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}\n\n')
    
    # ==========================================
    # ENVIRONMENT & RUN INFO
    # ==========================================
    env_emoji = '🏭' if 'prod' in environment.lower() or 'kefar' in environment.lower() else '🧪'
    lines.append('## 📌 Run Information\n\n')
    lines.append('| Property | Value |\n')
    lines.append('|----------|-------|\n')
    lines.append(f'| {env_emoji} **Environment** | `{environment.upper()}` |\n')
    if run_id:
        lines.append(f'| 🔢 **Run ID** | `{run_id}` |\n')
    if sha:
        lines.append(f'| 📝 **Commit** | `{sha}` |\n')
    if repo:
        lines.append(f'| 📦 **Repository** | `{repo}` |\n')
    lines.append(f'| ⏱️ **Duration** | `{format_duration(total_time)}` |\n')
    lines.append('\n')
    
    # ==========================================
    # OVERALL STATUS CARD
    # ==========================================
    lines.append('## 📊 Overall Results\n\n')
    
    # Status badge
    if total_failures == 0 and total_errors == 0:
        lines.append('> ### ✅ ALL TESTS PASSED\n\n')
    else:
        lines.append('> ### ❌ SOME TESTS FAILED\n\n')
    
    # Results table
    lines.append('| Metric | Count | Percentage |\n')
    lines.append('|--------|-------|------------|\n')
    
    pass_pct = (passed / total_tests * 100) if total_tests > 0 else 0
    fail_pct = (total_failures / total_tests * 100) if total_tests > 0 else 0
    err_pct = (total_errors / total_tests * 100) if total_tests > 0 else 0
    skip_pct = (total_skipped / total_tests * 100) if total_tests > 0 else 0
    
    lines.append(f'| 📋 **Total Tests** | {total_tests} | 100% |\n')
    lines.append(f'| ✅ **Passed** | {passed} | {pass_pct:.1f}% |\n')
    lines.append(f'| ❌ **Failed** | {total_failures} | {fail_pct:.1f}% |\n')
    lines.append(f'| 💥 **Errors** | {total_errors} | {err_pct:.1f}% |\n')
    lines.append(f'| ⏭️ **Skipped** | {total_skipped} | {skip_pct:.1f}% |\n')
    lines.append('\n')
    
    # Progress bar visualization
    if total_tests > 0:
        bar_length = 30
        passed_blocks = int(pass_pct / 100 * bar_length)
        failed_blocks = int(fail_pct / 100 * bar_length)
        error_blocks = int(err_pct / 100 * bar_length)
        
        bar = '🟢' * passed_blocks + '🔴' * failed_blocks + '🟠' * error_blocks
        remaining = bar_length - len(bar.replace('🟢', 'x').replace('🔴', 'x').replace('🟠', 'x'))
        bar += '⚪' * (remaining if remaining > 0 else 0)
        
        lines.append(f'**Progress:** {bar[:bar_length*2]}  \n\n')  # Emoji takes 2 chars
    
    # ==========================================
    # RESULTS BY CATEGORY
    # ==========================================
    if tests_by_category:
        lines.append('## 📂 Results by Category\n\n')
        
        for category, tests in tests_by_category.items():
            cat_passed = len(tests['passed'])
            cat_failed = len(tests['failed'])
            cat_errors = len(tests['error'])
            cat_skipped = len(tests['skipped'])
            cat_total = cat_passed + cat_failed + cat_errors + cat_skipped
            
            if cat_total == 0:
                continue
            
            # Category header with status
            cat_status = '✅' if cat_failed == 0 and cat_errors == 0 else '❌'
            lines.append(f'### {category} {cat_status}\n\n')
            lines.append(f'**{cat_passed}/{cat_total}** tests passed')
            if cat_failed > 0:
                lines.append(f' | **{cat_failed}** failed')
            if cat_errors > 0:
                lines.append(f' | **{cat_errors}** errors')
            if cat_skipped > 0:
                lines.append(f' | **{cat_skipped}** skipped')
            lines.append('\n\n')
            
            # Show tests in this category
            lines.append('<details>\n')
            lines.append(f'<summary>📋 View {cat_total} tests</summary>\n\n')
            
            # Group by class within category
            classes = {}
            for status_type in ['passed', 'failed', 'error', 'skipped']:
                for test in tests[status_type]:
                    cls = test['classname'].split('.')[-1] if '.' in test['classname'] else test['classname']
                    if cls not in classes:
                        classes[cls] = []
                    classes[cls].append((status_type, test))
            
            for cls_name, cls_tests in classes.items():
                lines.append(f'**{cls_name}**\n')
                for status_type, test in cls_tests:
                    emoji = {'passed': '✅', 'failed': '❌', 'error': '💥', 'skipped': '⏭️'}[status_type]
                    time_str = f" ({test['time']:.2f}s)" if test['time'] > 0.01 else ""
                    lines.append(f'- {emoji} `{test["short_name"]}`{time_str}\n')
                lines.append('\n')
            
            lines.append('</details>\n\n')
    
    # ==========================================
    # FAILED TESTS DETAIL
    # ==========================================
    if failed_tests or error_tests:
        lines.append('## ❌ Failed Tests Details\n\n')
        lines.append('> These tests need attention:\n\n')
        
        all_failures = failed_tests + error_tests
        for i, test in enumerate(all_failures[:30], 1):
            status_emoji = '❌' if test['status'] == 'failed' else '💥'
            lines.append(f'### {i}. {status_emoji} {test["short_name"]}\n\n')
            lines.append(f'**Class:** `{test["classname"]}`  \n')
            lines.append(f'**Status:** {test["status"].upper()}  \n')
            lines.append(f'**Duration:** {test["time"]:.2f}s  \n\n')
            
            if test['message']:
                lines.append('**Error Message:**\n')
                lines.append('```\n')
                # Clean up the message
                msg = test['message'].strip()
                # Limit lines
                msg_lines = msg.split('\n')[:15]
                lines.append('\n'.join(msg_lines))
                if len(msg.split('\n')) > 15:
                    lines.append('\n... (truncated)')
                lines.append('\n```\n\n')
            
            lines.append('---\n\n')
        
        if len(all_failures) > 30:
            lines.append(f'\n*... and {len(all_failures) - 30} more failed tests*\n\n')
    
    # ==========================================
    # SKIPPED TESTS
    # ==========================================
    if skipped_tests:
        lines.append('## ⏭️ Skipped Tests\n\n')
        lines.append('<details>\n')
        lines.append(f'<summary>View {len(skipped_tests)} skipped tests</summary>\n\n')
        
        for test in skipped_tests[:20]:
            reason = f" - {test['message'][:100]}" if test.get('message') else ""
            lines.append(f'- `{test["short_name"]}`{reason}\n')
        
        if len(skipped_tests) > 20:
            lines.append(f'\n*... and {len(skipped_tests) - 20} more*\n')
        
        lines.append('\n</details>\n\n')
    
    # ==========================================
    # QUICK LINKS
    # ==========================================
    if repo and run_id:
        lines.append('## 🔗 Quick Links\n\n')
        lines.append(f'- [📋 View Full Workflow Run](https://github.com/{repo}/actions/runs/{run_id})\n')
        lines.append(f'- [📊 View Test Artifacts](https://github.com/{repo}/actions/runs/{run_id}#artifacts)\n')
        check_run_id = os.environ.get('CHECK_RUN_ID', '')
        if check_run_id:
            lines.append(f'- [🧪 View Detailed Test Report](https://github.com/{repo}/runs/{check_run_id})\n')
        lines.append('\n')
    
    # ==========================================
    # FOOTER
    # ==========================================
    lines.append('---\n')
    lines.append(f'*Generated by `parse_junit_results.py` at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*\n')
    
    # Write to file or stdout
    content = ''.join(lines)
    
    if summary_path:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Summary written to {summary_path}")
    else:
        print(content)
    
    # Also print a compact summary to the console
    print("\n" + "=" * 60)
    print(f"TEST RESULTS SUMMARY - {environment.upper()}")
    print("=" * 60)
    print(f"Total: {total_tests} | Passed: {passed} | Failed: {total_failures} | Errors: {total_errors} | Skipped: {total_skipped}")
    print(f"Duration: {format_duration(total_time)}")
    print(f"Pass Rate: {pass_pct:.1f}%")
    print("=" * 60)
    
    if failed_tests or error_tests:
        print("\n❌ FAILED TESTS:")
        for test in (failed_tests + error_tests)[:10]:
            print(f"  - {test['short_name']} ({test['status']})")
        if len(failed_tests) + len(error_tests) > 10:
            print(f"  ... and {len(failed_tests) + len(error_tests) - 10} more")
    else:
        print("\n✅ All tests passed!")
    print()


if __name__ == '__main__':
    parse_junit_xml()
