#!/usr/bin/env python3
"""
Comprehensive Test Results Report Generator
============================================

Generates professional, detailed test reports from JUnit XML files
with full metrics, test flow breakdown, key insights, and performance data.

Usage:
    python scripts/generate_comprehensive_test_report.py [junit-xml-file] [--output report.md]
"""

import xml.etree.ElementTree as ET
import os
import sys
import json
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from statistics import mean, stdev, median
from collections import defaultdict


class TestReportGenerator:
    """Generate comprehensive test reports from JUnit XML."""
    
    def __init__(self, xml_file: str, environment: str = "staging", target: str = ""):
        self.xml_file = xml_file
        self.environment = environment
        self.target = target
        self.test_data = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'duration': 0.0,
            'test_cases': [],
            'suites': [],
            'performance_metrics': {}
        }
        
    def parse_xml(self) -> None:
        """Parse JUnit XML file and extract test data."""
        if not os.path.exists(self.xml_file):
            raise FileNotFoundError(f"JUnit XML file not found: {self.xml_file}")
        
        tree = ET.parse(self.xml_file)
        root = tree.getroot()
        
        # Handle both testsuites and testsuite elements
        suites = root.findall('.//testsuite') if root.tag != 'testsuite' else [root]
        if not suites:
            suites = [root] if root.tag == 'testsuite' else []
        
        for suite in suites:
            suite_data = {
                'name': suite.get('name', 'Unknown'),
                'tests': int(suite.get('tests', 0)),
                'failures': int(suite.get('failures', 0)),
                'errors': int(suite.get('errors', 0)),
                'skipped': int(suite.get('skipped', 0)),
                'time': float(suite.get('time', 0)),
                'test_cases': []
            }
            
            self.test_data['total'] += suite_data['tests']
            self.test_data['failed'] += suite_data['failures']
            self.test_data['errors'] += suite_data['errors']
            self.test_data['skipped'] += suite_data['skipped']
            self.test_data['duration'] += suite_data['time']
            
            # Process test cases
            for testcase in suite.findall('.//testcase'):
                test_case_data = {
                    'name': testcase.get('name', 'Unknown'),
                    'classname': testcase.get('classname', ''),
                    'time': float(testcase.get('time', 0)),
                    'status': 'passed',
                    'message': '',
                    'type': ''
                }
                
                failure = testcase.find('failure')
                error = testcase.find('error')
                skipped = testcase.find('skipped')
                
                if error is not None:
                    test_case_data['status'] = 'error'
                    test_case_data['message'] = error.get('message', '') or (error.text or '')[:200]
                    test_case_data['type'] = error.get('type', 'Error')
                elif failure is not None:
                    test_case_data['status'] = 'failed'
                    test_case_data['message'] = failure.get('message', '') or (failure.text or '')[:200]
                    test_case_data['type'] = failure.get('type', 'Failure')
                elif skipped is not None:
                    test_case_data['status'] = 'skipped'
                    test_case_data['message'] = skipped.get('message', '') or (skipped.text or '')[:200]
                
                suite_data['test_cases'].append(test_case_data)
                self.test_data['test_cases'].append(test_case_data)
            
            self.test_data['suites'].append(suite_data)
        
        self.test_data['passed'] = self.test_data['total'] - self.test_data['failed'] - self.test_data['errors'] - self.test_data['skipped']
        
        # Calculate performance metrics
        self._calculate_performance_metrics()
    
    def _calculate_performance_metrics(self) -> None:
        """Calculate performance metrics from test execution times."""
        if not self.test_data['test_cases']:
            return
        
        execution_times = [tc['time'] for tc in self.test_data['test_cases'] if tc['status'] == 'passed']
        
        if execution_times:
            self.test_data['performance_metrics'] = {
                'min_time': min(execution_times),
                'max_time': max(execution_times),
                'avg_time': mean(execution_times),
                'median_time': median(execution_times),
                'total_time': sum(execution_times),
                'std_dev': stdev(execution_times) if len(execution_times) > 1 else 0.0
            }
        
        # Group by status
        status_counts = defaultdict(int)
        for tc in self.test_data['test_cases']:
            status_counts[tc['status']] += 1
        
        self.test_data['performance_metrics']['status_distribution'] = dict(status_counts)
        
        # Group by classname for suite-level metrics
        class_metrics = defaultdict(lambda: {'count': 0, 'passed': 0, 'failed': 0, 'time': 0.0})
        for tc in self.test_data['test_cases']:
            classname = tc['classname'] or 'Unknown'
            class_metrics[classname]['count'] += 1
            class_metrics[classname]['time'] += tc['time']
            if tc['status'] == 'passed':
                class_metrics[classname]['passed'] += 1
            elif tc['status'] in ['failed', 'error']:
                class_metrics[classname]['failed'] += 1
        
        self.test_data['performance_metrics']['by_class'] = dict(class_metrics)
    
    def generate_markdown_report(self) -> str:
        """Generate comprehensive markdown report."""
        report = []
        
        # Header
        status_emoji = "✅" if self.test_data['failed'] == 0 and self.test_data['errors'] == 0 else "❌"
        report.append(f"# {status_emoji} Test Results Summary")
        report.append("")
        
        # Test Details Section
        report.append("## 📋 Test Details")
        report.append("")
        report.append(f"**Environment:** `{self.environment}`")
        if self.target:
            report.append(f"**Target:** `{self.target}`")
        report.append(f"**Time:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
        report.append(f"**Report Generated:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
        report.append("")
        
        # Overall Statistics
        report.append("## 📊 Overall Statistics")
        report.append("")
        report.append("| Metric | Value |")
        report.append("|--------|-------|")
        report.append(f"| **Total Tests** | {self.test_data['total']} |")
        report.append(f"| **✅ Passed** | {self.test_data['passed']} |")
        report.append(f"| **❌ Failed** | {self.test_data['failed']} |")
        report.append(f"| **⚠️ Errors** | {self.test_data['errors']} |")
        report.append(f"| **⏭️ Skipped** | {self.test_data['skipped']} |")
        report.append(f"| **⏱️ Duration** | {self.test_data['duration']:.2f}s |")
        
        if self.test_data['total'] > 0:
            success_rate = (self.test_data['passed'] / self.test_data['total']) * 100
            report.append(f"| **📈 Success Rate** | {success_rate:.1f}% |")
        
        report.append("")
        
        # Test Flow Section
        report.append("## 🔄 Test Flow")
        report.append("")
        report.append("This test suite validates the complete job lifecycle:")
        report.append("")
        report.append("1. **`POST /configure`** - Create job, get `job_id`, `stream_url`, `stream_port`")
        report.append("2. **`Wait + Retry`** - Wait for gRPC to be ready (with retries!)")
        report.append("3. **`gRPC Connect`** - Connect to streaming endpoint")
        report.append("4. **`Stream Data`** - Receive spectrogram frames")
        report.append("5. **`Cleanup`** - Disconnect and release resources")
        report.append("")
        
        # Key Insights Section
        report.append("## 💡 Key Insights")
        report.append("")
        
        if self.test_data['failed'] == 0 and self.test_data['errors'] == 0:
            report.append("✅ **All tests passed successfully!**")
            report.append("")
            report.append("The system demonstrated:")
            report.append(f"- ✅ {self.test_data['passed']} successful test executions")
            report.append(f"- ⏱️ Average execution time: {self.test_data['performance_metrics'].get('avg_time', 0):.2f}s")
        else:
            report.append("⚠️ **Some tests encountered issues:**")
            report.append("")
            report.append(f"- ❌ {self.test_data['failed']} test(s) failed")
            report.append(f"- ⚠️ {self.test_data['errors']} test(s) encountered errors")
            report.append("")
            report.append("**Recommendation:** Review failed tests below for details.")
        
        report.append("")
        report.append("> **Note:** Based on Yonatan's feedback, the tests include **retry logic** between job configuration (step 4) and gRPC connection (step 5). This is critical because the gRPC service may not be immediately available.")
        report.append("")
        
        # Performance Metrics Section
        if self.test_data['performance_metrics']:
            report.append("## ⚡ Performance Metrics")
            report.append("")
            
            perf = self.test_data['performance_metrics']
            if 'avg_time' in perf:
                report.append("### Execution Time Statistics")
                report.append("")
                report.append("| Metric | Value |")
                report.append("|--------|-------|")
                report.append(f"| **Min Time** | {perf['min_time']:.3f}s |")
                report.append(f"| **Max Time** | {perf['max_time']:.3f}s |")
                report.append(f"| **Average Time** | {perf['avg_time']:.3f}s |")
                report.append(f"| **Median Time** | {perf['median_time']:.3f}s |")
                report.append(f"| **Total Time** | {perf['total_time']:.2f}s |")
                if perf['std_dev'] > 0:
                    report.append(f"| **Std Deviation** | {perf['std_dev']:.3f}s |")
                report.append("")
        
        # Test Suites Breakdown
        if self.test_data['suites']:
            report.append("## 📦 Test Suites Breakdown")
            report.append("")
            
            for suite in self.test_data['suites']:
                suite_passed = suite['tests'] - suite['failures'] - suite['errors'] - suite['skipped']
                suite_status = "✅" if suite['failures'] == 0 and suite['errors'] == 0 else "❌"
                
                report.append(f"### {suite_status} {suite['name']}")
                report.append("")
                report.append("| Metric | Value |")
                report.append("|--------|-------|")
                report.append(f"| **Total Tests** | {suite['tests']} |")
                report.append(f"| **Passed** | {suite_passed} |")
                report.append(f"| **Failures** | {suite['failures']} |")
                report.append(f"| **Errors** | {suite['errors']} |")
                report.append(f"| **Duration** | {suite['time']:.2f}s |")
                report.append("")
                
                if suite['test_cases']:
                    # Show sample test cases (first 5 passed, all failed/errors)
                    passed_cases = [tc for tc in suite['test_cases'] if tc['status'] == 'passed'][:5]
                    failed_cases = [tc for tc in suite['test_cases'] if tc['status'] in ['failed', 'error']]
                    
                    if passed_cases:
                        report.append("**Sample Passed Tests:**")
                        report.append("")
                        for tc in passed_cases:
                            report.append(f"- ✅ `{tc['name']}` ({tc['time']:.3f}s)")
                        report.append("")
                    
                    if failed_cases:
                        report.append("**Failed/Error Tests:**")
                        report.append("")
                        for tc in failed_cases:
                            report.append(f"- ❌ `{tc['name']}` ({tc['type']})")
                            if tc['message']:
                                report.append(f"  ```")
                                report.append(f"  {tc['message'][:300]}")
                                report.append(f"  ```")
                        report.append("")
        
        # Failed Tests Details
        failed_tests = [tc for tc in self.test_data['test_cases'] if tc['status'] in ['failed', 'error']]
        if failed_tests:
            report.append("## ❌ Failed Tests Details")
            report.append("")
            
            for i, tc in enumerate(failed_tests, 1):
                report.append(f"### {i}. {tc['name']}")
                report.append("")
                report.append(f"**Status:** `{tc['status'].upper()}`")
                report.append(f"**Class:** `{tc['classname']}`")
                report.append(f"**Duration:** `{tc['time']:.3f}s`")
                if tc['type']:
                    report.append(f"**Type:** `{tc['type']}`")
                report.append("")
                
                if tc['message']:
                    report.append("**Error Message:**")
                    report.append("```")
                    report.append(tc['message'])
                    report.append("```")
                    report.append("")
        
        # Class-Level Metrics
        if self.test_data['performance_metrics'].get('by_class'):
            report.append("## 📊 Class-Level Metrics")
            report.append("")
            report.append("| Class | Tests | Passed | Failed | Duration |")
            report.append("|-------|-------|--------|--------|----------|")
            
            for classname, metrics in sorted(self.test_data['performance_metrics']['by_class'].items()):
                report.append(f"| `{classname}` | {metrics['count']} | {metrics['passed']} | {metrics['failed']} | {metrics['time']:.2f}s |")
            
            report.append("")
        
        # Artifacts Section
        report.append("## 📎 Artifacts")
        report.append("")
        report.append("**Produced during runtime:**")
        report.append("")
        report.append("| Name | Description |")
        report.append("|------|-------------|")
        report.append(f"| `{os.path.basename(self.xml_file)}` | JUnit XML test results |")
        
        # Look for additional artifacts
        xml_dir = os.path.dirname(self.xml_file)
        if os.path.exists(xml_dir):
            for ext in ['.json', '.html', '.csv', '.log']:
                artifacts = glob.glob(os.path.join(xml_dir, f'*{ext}'))
                for artifact in artifacts[:5]:  # Limit to 5 per type
                    artifact_name = os.path.basename(artifact)
                    artifact_desc = {
                        '.json': 'JSON metrics data',
                        '.html': 'HTML test report',
                        '.csv': 'CSV export data',
                        '.log': 'Test execution logs'
                    }.get(ext, 'Additional artifact')
                    report.append(f"| `{artifact_name}` | {artifact_desc} |")
        
        report.append("")
        report.append("> **Note:** Job summary generated at run-time")
        report.append("")
        
        return "\n".join(report)
    
    def generate_json_report(self) -> Dict[str, Any]:
        """Generate JSON report for programmatic access."""
        return {
            'metadata': {
                'environment': self.environment,
                'target': self.target,
                'generated_at': datetime.now().isoformat(),
                'xml_file': self.xml_file
            },
            'summary': {
                'total': self.test_data['total'],
                'passed': self.test_data['passed'],
                'failed': self.test_data['failed'],
                'errors': self.test_data['errors'],
                'skipped': self.test_data['skipped'],
                'duration': self.test_data['duration'],
                'success_rate': (self.test_data['passed'] / self.test_data['total'] * 100) if self.test_data['total'] > 0 else 0
            },
            'performance': self.test_data['performance_metrics'],
            'suites': self.test_data['suites'],
            'test_cases': self.test_data['test_cases']
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate comprehensive test reports from JUnit XML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate markdown report
  python scripts/generate_comprehensive_test_report.py test-results/junit-smoke.xml
  
  # Generate report with custom environment
  python scripts/generate_comprehensive_test_report.py test-results/junit-smoke.xml \\
    --environment production --target https://10.10.10.100
  
  # Generate both markdown and JSON
  python scripts/generate_comprehensive_test_report.py test-results/junit-smoke.xml \\
    --output report.md --json report.json
        """
    )
    
    parser.add_argument('xml_file', help='Path to JUnit XML file')
    parser.add_argument('--output', '-o', help='Output markdown file path (default: stdout or GITHUB_STEP_SUMMARY)')
    parser.add_argument('--json', '-j', help='Output JSON file path')
    parser.add_argument('--environment', '-e', default='staging', help='Environment name (default: staging)')
    parser.add_argument('--target', '-t', default='', help='Target server URL')
    
    args = parser.parse_args()
    
    try:
        # Generate report
        generator = TestReportGenerator(args.xml_file, args.environment, args.target)
        generator.parse_xml()
        
        # Generate markdown report
        markdown_report = generator.generate_markdown_report()
        
        # Output markdown
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(markdown_report)
            print(f"✅ Markdown report written to: {args.output}")
        else:
            # Try GitHub Actions summary, fallback to stdout
            summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
            if summary_path:
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_report)
                print(f"✅ Report written to GitHub Actions summary")
            else:
                print(markdown_report)
        
        # Generate JSON report if requested
        if args.json:
            json_report = generator.generate_json_report()
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump(json_report, f, indent=2)
            print(f"✅ JSON report written to: {args.json}")
        
        # Report generation should always succeed (even if tests failed)
        # The workflow will fail in a separate step that checks for failures
        # This allows the report to be generated even when tests fail
        if generator.test_data['failed'] > 0 or generator.test_data['errors'] > 0:
            print(f"⚠️ Report generated successfully, but tests had failures: {generator.test_data['failed']} failures, {generator.test_data['errors']} errors")
            print("Note: Workflow will fail in the 'Fail workflow if tests failed' step")
            sys.exit(0)  # Don't fail here - let the failure check step handle it
        else:
            print("✅ All tests passed!")
            sys.exit(0)
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

