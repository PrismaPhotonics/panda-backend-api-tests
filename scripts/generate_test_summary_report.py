#!/usr/bin/env python3
"""
Comprehensive Test Summary Report Generator for GitHub Actions

Parses JUnit XML files from both backend and frontend tests,
and generates a clear, comprehensive summary report.
"""

import xml.etree.ElementTree as ET
import glob
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class TestSummaryReport:
    """Generate comprehensive test summary reports."""
    
    def __init__(self):
        self.backend_stats = {
            'total': 0, 'passed': 0, 'failed': 0, 'errors': 0, 
            'skipped': 0, 'time': 0.0, 'failed_tests': []
        }
        self.frontend_stats = {
            'total': 0, 'passed': 0, 'failed': 0, 'errors': 0, 
            'skipped': 0, 'time': 0.0, 'failed_tests': []
        }
    
    def parse_junit_xml(self, xml_file: str, test_type: str) -> None:
        """Parse a JUnit XML file and update statistics."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Handle both testsuites and testsuite elements
            suites = root.findall('.//testsuite') if root.tag != 'testsuite' else [root]
            if not suites:
                suites = [root]
            
            stats = self.backend_stats if test_type == 'backend' else self.frontend_stats
            
            for suite in suites:
                stats['total'] += int(suite.get('tests', 0))
                stats['failed'] += int(suite.get('failures', 0))
                stats['errors'] += int(suite.get('errors', 0))
                stats['skipped'] += int(suite.get('skipped', 0))
                stats['time'] += float(suite.get('time', 0))
                
                # Find failed/errored tests
                for testcase in suite.findall('.//testcase'):
                    failure = testcase.find('failure')
                    error = testcase.find('error')
                    
                    if failure is not None or error is not None:
                        test_name = f"{testcase.get('classname', '')}::{testcase.get('name', 'unknown')}"
                        message = (failure or error).text or ''
                        stats['failed_tests'].append({
                            'name': test_name,
                            'status': 'failed' if failure else 'error',
                            'message': message[:300] if message else '',
                            'file': xml_file
                        })
        except Exception as e:
            print(f"⚠️ Error parsing {xml_file}: {e}", file=sys.stderr)
    
    def find_junit_files(self) -> Tuple[List[str], List[str]]:
        """Find all JUnit XML files."""
        backend_files = []
        frontend_files = []
        
        # Check common locations
        patterns = [
            'reports/junit-backend.xml',
            'reports/junit.xml',
            '**/junit-backend.xml',
            '**/junit-frontend.xml',
            '**/junit.xml'
        ]
        
        for pattern in patterns:
            files = glob.glob(pattern, recursive=True)
            for f in files:
                if 'frontend' in f.lower() or 'fe_' in f.lower():
                    if f not in frontend_files:
                        frontend_files.append(f)
                elif 'backend' in f.lower() or 'be_' in f.lower() or 'focus_server' in f.lower():
                    if f not in backend_files:
                        backend_files.append(f)
                elif 'junit.xml' in f and f not in backend_files:
                    # Default to backend if unclear
                    backend_files.append(f)
        
        return backend_files, frontend_files
    
    def generate_summary(self) -> str:
        """Generate the summary report."""
        # Parse all files
        backend_files, frontend_files = self.find_junit_files()
        
        for f in backend_files:
            self.parse_junit_xml(f, 'backend')
        
        for f in frontend_files:
            self.parse_junit_xml(f, 'frontend')
        
        # Calculate passed tests
        self.backend_stats['passed'] = (
            self.backend_stats['total'] - 
            self.backend_stats['failed'] - 
            self.backend_stats['errors'] - 
            self.backend_stats['skipped']
        )
        self.frontend_stats['passed'] = (
            self.frontend_stats['total'] - 
            self.frontend_stats['failed'] - 
            self.frontend_stats['errors'] - 
            self.frontend_stats['skipped']
        )
        
        # Generate report
        return self._format_report()
    
    def _format_report(self) -> str:
        """Format the report as markdown."""
        total_tests = self.backend_stats['total'] + self.frontend_stats['total']
        total_passed = self.backend_stats['passed'] + self.frontend_stats['passed']
        total_failed = self.backend_stats['failed'] + self.frontend_stats['failed']
        total_errors = self.backend_stats['errors'] + self.frontend_stats['errors']
        total_skipped = self.backend_stats['skipped'] + self.frontend_stats['skipped']
        total_time = self.backend_stats['time'] + self.frontend_stats['time']
        
        # Overall status
        if total_failed == 0 and total_errors == 0:
            status_emoji = "✅"
            status_text = "All Tests Passed"
        elif total_failed > 0 or total_errors > 0:
            status_emoji = "❌"
            status_text = "Some Tests Failed"
        else:
            status_emoji = "⚠️"
            status_text = "Tests Completed with Warnings"
        
        report = f"""# {status_emoji} Test Execution Summary

**Status:** {status_text}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## 📊 Overall Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Tests** | {total_tests} | 100% |
| **✅ Passed** | {total_passed} | {(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}% |
| **❌ Failed** | {total_failed} | {(total_failed/total_tests*100) if total_tests > 0 else 0:.1f}% |
| **⚠️ Errors** | {total_errors} | {(total_errors/total_tests*100) if total_tests > 0 else 0:.1f}% |
| **⏭️ Skipped** | {total_skipped} | {(total_skipped/total_tests*100) if total_tests > 0 else 0:.1f}% |
| **⏱️ Duration** | {total_time:.2f}s | - |

---

## 🔧 Backend Tests

| Metric | Count |
|--------|-------|
| **Total** | {self.backend_stats['total']} |
| **✅ Passed** | {self.backend_stats['passed']} |
| **❌ Failed** | {self.backend_stats['failed']} |
| **⚠️ Errors** | {self.backend_stats['errors']} |
| **⏭️ Skipped** | {self.backend_stats['skipped']} |
| **⏱️ Duration** | {self.backend_stats['time']:.2f}s |

"""
        
        # Frontend section
        if self.frontend_stats['total'] > 0:
            report += f"""## 🎨 Frontend Tests

| Metric | Count |
|--------|-------|
| **Total** | {self.frontend_stats['total']} |
| **✅ Passed** | {self.frontend_stats['passed']} |
| **❌ Failed** | {self.frontend_stats['failed']} |
| **⚠️ Errors** | {self.frontend_stats['errors']} |
| **⏭️ Skipped** | {self.frontend_stats['skipped']} |
| **⏱️ Duration** | {self.frontend_stats['time']:.2f}s |

"""
        else:
            report += """## 🎨 Frontend Tests

⚠️ No frontend test results found. Frontend tests may have been skipped or not executed.

"""
        
        # Failed tests section
        all_failed = self.backend_stats['failed_tests'] + self.frontend_stats['failed_tests']
        if all_failed:
            report += f"""## ❌ Failed Tests ({len(all_failed)})

"""
            # Show backend failures
            if self.backend_stats['failed_tests']:
                report += "### Backend Failures\n\n"
                for i, test in enumerate(self.backend_stats['failed_tests'][:10], 1):
                    report += f"{i}. **{test['name']}** ({test['status']})\n"
                    if test['message']:
                        report += f"   ```\n   {test['message'][:200]}...\n   ```\n\n"
                if len(self.backend_stats['failed_tests']) > 10:
                    report += f"*... and {len(self.backend_stats['failed_tests']) - 10} more backend failures*\n\n"
            
            # Show frontend failures
            if self.frontend_stats['failed_tests']:
                report += "### Frontend Failures\n\n"
                for i, test in enumerate(self.frontend_stats['failed_tests'][:10], 1):
                    report += f"{i}. **{test['name']}** ({test['status']})\n"
                    if test['message']:
                        report += f"   ```\n   {test['message'][:200]}...\n   ```\n\n"
                if len(self.frontend_stats['failed_tests']) > 10:
                    report += f"*... and {len(self.frontend_stats['failed_tests']) - 10} more frontend failures*\n\n"
        else:
            report += """## ✅ All Tests Passed!

🎉 Congratulations! All tests passed successfully.

"""
        
        # Links section
        repo = os.environ.get('GITHUB_REPOSITORY', '')
        run_id = os.environ.get('GITHUB_RUN_ID', '')
        
        if repo and run_id:
            report += f"""## 📎 Additional Resources

- 📊 [View Workflow Run](https://github.com/{repo}/actions/runs/{run_id})
- 📦 [Download Test Artifacts](https://github.com/{repo}/actions/runs/{run_id})

"""
        
        return report


def main():
    """Main entry point."""
    reporter = TestSummaryReport()
    summary = reporter.generate_summary()
    
    # Write to GitHub step summary
    summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_path:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print("✅ Test summary written to GitHub Actions step summary")
    else:
        # Also print to stdout
        print(summary)
        print("\n⚠️ GITHUB_STEP_SUMMARY not set - printed to stdout instead")
    
    # Exit with error code if tests failed
    total_failed = (
        reporter.backend_stats['failed'] + reporter.backend_stats['errors'] +
        reporter.frontend_stats['failed'] + reporter.frontend_stats['errors']
    )
    
    if total_failed > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()

