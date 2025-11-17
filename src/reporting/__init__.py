"""
Test Reporting Module
=====================

This module provides test report generation with Jira bug mapping.

Main Components:
- TestReportGenerator: Generate test execution reports
- pytest_integration: Pytest hooks for automatic report generation

Usage:
    # Run tests with Jira report generation
    pytest --generate-jira-report --jira-report-path=reports/test_report.json
    
    # Or use programmatically
    from src.reporting.test_report_generator import TestReportGenerator
    
    generator = TestReportGenerator()
    generator.add_failure(...)
    generator.map_failures_to_bugs()
    generator.save_report("report.json")
"""

from src.reporting.test_report_generator import TestReportGenerator, TestFailure

__all__ = ["TestReportGenerator", "TestFailure"]

__version__ = "1.0.0"

