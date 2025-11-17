"""
Pytest Integration for Test Report Generation
=============================================

This module provides pytest hooks for automatic test report generation
with Jira bug mapping.

Features:
- Capture test failures automatically
- Map failures to existing Jira bugs
- Generate reports after test execution
- Save reports to files

Author: QA Automation Architect
Date: 2025-11-08
Version: 1.0.0
"""

import logging
import pytest
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from src.reporting.test_report_generator import TestReportGenerator

logger = logging.getLogger(__name__)

# Global report generator instance
_report_generator: Optional[TestReportGenerator] = None


def pytest_configure(config):
    """Initialize report generator when pytest starts."""
    global _report_generator
    
    # Check if report generation is enabled
    if not config.getoption("--generate-jira-report", default=False):
        logger.debug("Jira report generation disabled")
        return
    
    try:
        _report_generator = TestReportGenerator()
        _report_generator.start_time = datetime.now()
        logger.info("Test report generator initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize report generator: {e}")
        _report_generator = None


def pytest_addoption(parser):
    """Add command-line options for report generation."""
    parser.addoption(
        "--generate-jira-report",
        action="store_true",
        default=False,
        help="Generate test report with Jira bug mapping"
    )
    parser.addoption(
        "--jira-report-path",
        action="store",
        default="reports/test_report.json",
        help="Path to save Jira report (default: reports/test_report.json)"
    )
    parser.addoption(
        "--jira-report-format",
        action="store",
        default="json",
        choices=["json", "markdown"],
        help="Report format: json or markdown (default: json)"
    )


def pytest_runtest_setup(item):
    """Called before each test runs."""
    pass


def pytest_runtest_teardown(item, nextitem):
    """Called after each test runs."""
    pass


def pytest_runtest_makereport(item, call):
    """
    Called after each test execution to capture results.
    
    This hook captures test failures and adds them to the report generator.
    """
    global _report_generator
    
    if _report_generator is None:
        return
    
    # Only process test calls (not setup/teardown)
    if call.when != "call":
        return
    
    test_name = item.nodeid
    
    try:
        # Record test result
        if call.excinfo is None:
            # Test passed
            _report_generator.add_passed(test_name)
        elif call.excinfo.typename == "Skipped":
            # Test skipped
            _report_generator.add_skipped(test_name)
        else:
            # Test failed
            error_type = call.excinfo.typename
            error_message = str(call.excinfo.value) if call.excinfo.value else ""
            traceback = None
            
            if call.excinfo.traceback:
                # Get last traceback entry
                try:
                    tb_entry = call.excinfo.traceback[-1]
                    traceback = f"{tb_entry.path}:{tb_entry.lineno}: {tb_entry.message}"
                except Exception:
                    # If traceback extraction fails, use error message
                    traceback = error_message
            
            duration = call.duration if hasattr(call, 'duration') else None
            
            _report_generator.add_failure(
                test_name=test_name,
                error_message=error_message,
                error_type=error_type,
                traceback=traceback,
                duration=duration
            )
            
            logger.debug(f"Captured failure: {test_name} - {error_type}")
    except Exception as e:
        logger.warning(f"Failed to capture test result: {e}")


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    global _report_generator
    
    if _report_generator is None:
        return
    
    _report_generator.start_time = datetime.now()
    logger.info("Test session started - report generation enabled")


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before returning exit status.
    
    This is where we:
    1. Map failures to existing Jira bugs
    2. Generate the report
    3. Save the report to file
    """
    global _report_generator
    
    if _report_generator is None:
        return
    
    try:
        _report_generator.end_time = datetime.now()
        
        # Get total test count
        total_tests = session.config.option.numtests if hasattr(session.config.option, 'numtests') else None
        if total_tests is None:
            # Count from collected items
            total_tests = len(session.items) if hasattr(session, 'items') else 0
        
        _report_generator.set_execution_info(
            total_tests=total_tests,
            start_time=_report_generator.start_time,
            end_time=_report_generator.end_time
        )
        
        # Map failures to existing bugs
        logger.info("Mapping test failures to existing Jira bugs...")
        _report_generator.map_failures_to_bugs()
        
        # Generate and save report
        report_path = session.config.option.jira_report_path
        report_format = session.config.option.jira_report_format
        
        logger.info(f"Generating {report_format} report: {report_path}")
        _report_generator.save_report(report_path, format=report_format)
        
        # Also generate markdown if JSON was requested (for readability)
        if report_format == "json":
            md_path = Path(report_path).with_suffix('.md')
            _report_generator.save_report(str(md_path), format="markdown")
            logger.info(f"Also generated Markdown report: {md_path}")
        
        # Print summary
        summary = _report_generator.generate_report()['summary']
        logger.info("=" * 80)
        logger.info("JIRA BUG MAPPING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Failures: {summary['total_failures']}")
        logger.info(f"Mapped to Existing Bugs: ✅ {summary['mapped_to_existing_bugs']}")
        logger.info(f"New Bugs Needed: ⚠️ {summary['bugs_to_create']}")
        logger.info("=" * 80)
        
        # Print mapped bugs
        if _report_generator.mapped_bugs:
            logger.info("\nMapped Bugs:")
            for test_name, bug_info in _report_generator.mapped_bugs.items():
                logger.info(
                    f"  ✅ {test_name} → {bug_info['bug_key']} "
                    f"({bug_info['bug_status']}, similarity: {bug_info['similarity_score']:.2f})"
                )
        
        # Print new bugs needed
        if _report_generator.new_bugs_needed:
            logger.info("\nNew Bugs Needed:")
            for failure in _report_generator.new_bugs_needed:
                logger.info(f"  ⚠️ {failure.test_name}")
        
        # Cleanup
        _report_generator.close()
        
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
    finally:
        _report_generator = None

