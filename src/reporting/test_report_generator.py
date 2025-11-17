"""
Test Report Generator
====================

This module provides automatic test report generation with Jira bug mapping.

Features:
- Generate test execution reports
- Map test failures to existing Jira bugs
- Identify new bugs that need to be created
- Generate comprehensive reports with bug links

Author: QA Automation Architect
Date: 2025-11-08
Version: 1.0.0
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from external.jira.bug_deduplication import BugDeduplicationService
from external.jira.bug_creator import BugCreatorService

logger = logging.getLogger(__name__)


class TestFailure:
    """Represents a test failure."""
    
    def __init__(
        self,
        test_name: str,
        error_message: str,
        error_type: str,
        traceback: Optional[str] = None,
        duration: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ):
        self.test_name = test_name
        self.error_message = error_message
        self.error_type = error_type
        self.traceback = traceback
        self.duration = duration
        self.timestamp = timestamp or datetime.now()
        
        # Will be populated by bug mapping
        self.existing_bug: Optional[Dict[str, Any]] = None
        self.similarity_score: Optional[float] = None
        self.should_create_bug: bool = True


class TestReportGenerator:
    """
    Generate test execution reports with Jira bug mapping.
    
    This class:
    1. Analyzes test failures
    2. Maps failures to existing Jira bugs
    3. Identifies new bugs that need to be created
    4. Generates comprehensive reports
    
    Example:
        ```python
        from src.reporting.test_report_generator import TestReportGenerator
        
        generator = TestReportGenerator()
        
        # Add test failures
        generator.add_failure(
            test_name="test_mongodb_connection",
            error_message="Connection failed: timeout",
            error_type="ConnectionError"
        )
        
        # Map to existing bugs
        generator.map_failures_to_bugs()
        
        # Generate report
        report = generator.generate_report()
        generator.save_report("test_report.json")
        ```
    """
    
    def __init__(
        self,
        jira_client=None,
        deduplication_service: Optional[BugDeduplicationService] = None,
        project_key: Optional[str] = None
    ):
        """
        Initialize Test Report Generator.
        
        Args:
            jira_client: JiraClient instance (creates new if not provided)
            deduplication_service: BugDeduplicationService instance
            project_key: Project key for Jira
        """
        self.deduplication_service = deduplication_service or BugDeduplicationService(
            jira_client=jira_client,
            project_key=project_key
        )
        self.project_key = project_key or self.deduplication_service.project_key
        
        # Test execution data
        self.failures: List[TestFailure] = []
        self.passed: List[str] = []
        self.skipped: List[str] = []
        self.total_tests: int = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Bug mapping results
        self.mapped_bugs: Dict[str, Dict[str, Any]] = {}  # test_name -> bug info
        self.new_bugs_needed: List[TestFailure] = []
        
        logger.info(f"TestReportGenerator initialized for project: {self.project_key}")
    
    def add_failure(
        self,
        test_name: str,
        error_message: str,
        error_type: str,
        traceback: Optional[str] = None,
        duration: Optional[float] = None
    ):
        """
        Add a test failure to the report.
        
        Args:
            test_name: Name of the test that failed
            error_message: Error message
            error_type: Type of error (e.g., "AssertionError", "ConnectionError")
            traceback: Full traceback (optional)
            duration: Test duration in seconds (optional)
        """
        failure = TestFailure(
            test_name=test_name,
            error_message=error_message,
            error_type=error_type,
            traceback=traceback,
            duration=duration
        )
        self.failures.append(failure)
        logger.debug(f"Added failure: {test_name}")
    
    def add_passed(self, test_name: str):
        """Add a passed test to the report."""
        self.passed.append(test_name)
    
    def add_skipped(self, test_name: str):
        """Add a skipped test to the report."""
        self.skipped.append(test_name)
    
    def set_execution_info(
        self,
        total_tests: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ):
        """
        Set test execution information.
        
        Args:
            total_tests: Total number of tests
            start_time: Test execution start time
            end_time: Test execution end time
        """
        self.total_tests = total_tests
        self.start_time = start_time or datetime.now()
        self.end_time = end_time or datetime.now()
    
    def map_failures_to_bugs(self, similarity_threshold: float = 0.7):
        """
        Map test failures to existing Jira bugs.
        
        Args:
            similarity_threshold: Minimum similarity score to consider bugs similar
        """
        logger.info(f"Mapping {len(self.failures)} failures to existing bugs...")
        
        self.mapped_bugs = {}
        self.new_bugs_needed = []
        
        for failure in self.failures:
            logger.info(f"Checking failure: {failure.test_name}")
            
            # Extract keywords from error message and test name
            keywords = self._extract_keywords(failure)
            
            # Search for similar bugs
            existing_bug = self.deduplication_service.find_similar_bug(
                summary=self._generate_summary(failure),
                description=self._generate_description(failure),
                keywords=keywords,
                error_message=failure.error_message,
                test_name=failure.test_name
            )
            
            if existing_bug:
                # Calculate similarity score
                similarity = self._calculate_similarity_for_failure(failure, existing_bug)
                
                failure.existing_bug = existing_bug
                failure.similarity_score = similarity
                failure.should_create_bug = False
                
                self.mapped_bugs[failure.test_name] = {
                    'bug_key': existing_bug['key'],
                    'bug_url': existing_bug['url'],
                    'bug_summary': existing_bug['summary'],
                    'bug_status': existing_bug['status'],
                    'similarity_score': similarity,
                    'test_name': failure.test_name,
                    'error_message': failure.error_message[:200]  # Truncate
                }
                
                logger.info(
                    f"✅ Mapped to existing bug: {existing_bug['key']} "
                    f"(similarity: {similarity:.2f})"
                )
            else:
                failure.should_create_bug = True
                self.new_bugs_needed.append(failure)
                
                logger.info(f"⚠️  No similar bug found - new bug needed")
        
        logger.info(
            f"Mapped {len(self.mapped_bugs)} failures to existing bugs, "
            f"{len(self.new_bugs_needed)} new bugs needed"
        )
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive test execution report.
        
        Returns:
            Dictionary with report data
        """
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        report = {
            'execution_info': {
                'total_tests': self.total_tests,
                'passed': len(self.passed),
                'failed': len(self.failures),
                'skipped': len(self.skipped),
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'duration_seconds': duration
            },
            'failures': [],
            'mapped_bugs': list(self.mapped_bugs.values()),
            'new_bugs_needed': [],
            'summary': {
                'total_failures': len(self.failures),
                'mapped_to_existing_bugs': len(self.mapped_bugs),
                'new_bugs_needed': len(self.new_bugs_needed),
                'bugs_already_exist': len(self.mapped_bugs),
                'bugs_to_create': len(self.new_bugs_needed)
            }
        }
        
        # Add failure details
        for failure in self.failures:
            failure_data = {
                'test_name': failure.test_name,
                'error_type': failure.error_type,
                'error_message': failure.error_message[:500],  # Truncate
                'duration': failure.duration,
                'timestamp': failure.timestamp.isoformat(),
                'existing_bug': None,
                'similarity_score': None,
                'should_create_bug': failure.should_create_bug
            }
            
            if failure.existing_bug:
                failure_data['existing_bug'] = {
                    'key': failure.existing_bug['key'],
                    'url': failure.existing_bug['url'],
                    'summary': failure.existing_bug['summary'],
                    'status': failure.existing_bug['status']
                }
                failure_data['similarity_score'] = failure.similarity_score
            
            report['failures'].append(failure_data)
        
        # Add new bugs needed
        for failure in self.new_bugs_needed:
            report['new_bugs_needed'].append({
                'test_name': failure.test_name,
                'error_type': failure.error_type,
                'error_message': failure.error_message[:500],
                'suggested_summary': self._generate_summary(failure),
                'suggested_description': self._generate_description(failure),
                'keywords': self._extract_keywords(failure)
            })
        
        return report
    
    def generate_markdown_report(self) -> str:
        """
        Generate markdown-formatted test report.
        
        Returns:
            Markdown string
        """
        report = self.generate_report()
        
        lines = []
        lines.append("# 📊 Test Execution Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Execution Summary
        exec_info = report['execution_info']
        lines.append("## 📈 Execution Summary")
        lines.append("")
        lines.append(f"- **Total Tests:** {exec_info['total_tests']}")
        lines.append(f"- **Passed:** ✅ {exec_info['passed']}")
        lines.append(f"- **Failed:** ❌ {exec_info['failed']}")
        lines.append(f"- **Skipped:** ⏭️ {exec_info['skipped']}")
        if exec_info['duration_seconds']:
            lines.append(f"- **Duration:** {exec_info['duration_seconds']:.2f} seconds")
        lines.append("")
        
        # Summary
        summary = report['summary']
        lines.append("## 🐛 Bug Mapping Summary")
        lines.append("")
        lines.append(f"- **Total Failures:** {summary['total_failures']}")
        lines.append(f"- **Mapped to Existing Bugs:** ✅ {summary['mapped_to_existing_bugs']}")
        lines.append(f"- **New Bugs Needed:** ⚠️ {summary['bugs_to_create']}")
        lines.append("")
        
        # Mapped Bugs
        if report['mapped_bugs']:
            lines.append("## ✅ Failures Mapped to Existing Bugs")
            lines.append("")
            for bug_info in report['mapped_bugs']:
                lines.append(f"### {bug_info['test_name']}")
                lines.append("")
                lines.append(f"- **Bug:** [{bug_info['bug_key']}]({bug_info['bug_url']})")
                lines.append(f"- **Summary:** {bug_info['bug_summary']}")
                lines.append(f"- **Status:** {bug_info['bug_status']}")
                lines.append(f"- **Similarity Score:** {bug_info['similarity_score']:.2f}")
                lines.append(f"- **Error:** `{bug_info['error_message']}`")
                lines.append("")
        
        # New Bugs Needed
        if report['new_bugs_needed']:
            lines.append("## ⚠️ New Bugs Needed")
            lines.append("")
            for bug_info in report['new_bugs_needed']:
                lines.append(f"### {bug_info['test_name']}")
                lines.append("")
                lines.append(f"- **Error Type:** `{bug_info['error_type']}`")
                lines.append(f"- **Error Message:** `{bug_info['error_message']}`")
                lines.append(f"- **Suggested Summary:** {bug_info['suggested_summary']}")
                lines.append(f"- **Keywords:** {', '.join(bug_info['keywords'])}")
                lines.append("")
        
        # All Failures
        if report['failures']:
            lines.append("## ❌ All Failures")
            lines.append("")
            for failure in report['failures']:
                lines.append(f"### {failure['test_name']}")
                lines.append("")
                lines.append(f"- **Error Type:** `{failure['error_type']}`")
                lines.append(f"- **Error Message:** `{failure['error_message']}`")
                if failure['existing_bug']:
                    bug = failure['existing_bug']
                    lines.append(f"- **Existing Bug:** [{bug['key']}]({bug['url']}) ({bug['status']})")
                    lines.append(f"- **Similarity:** {failure['similarity_score']:.2f}")
                else:
                    lines.append(f"- **Status:** ⚠️ New bug needed")
                lines.append("")
        
        return "\n".join(lines)
    
    def save_report(self, output_path: str, format: str = "json"):
        """
        Save report to file.
        
        Args:
            output_path: Path to save report
            format: Report format ("json" or "markdown")
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            report = self.generate_report()
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved JSON report to: {output_path}")
        
        elif format == "markdown":
            report = self.generate_markdown_report()
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Saved Markdown report to: {output_path}")
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _extract_keywords(self, failure: TestFailure) -> List[str]:
        """Extract keywords from test failure."""
        text = f"{failure.test_name} {failure.error_message}".lower()
        
        # Common technical terms
        tech_terms = [
            'mongodb', 'connection', 'timeout', 'error', 'failure', 'restart',
            'pod', 'kubernetes', 'k8s', 'api', 'endpoint', 'configure',
            'metadata', 'fiber', 'prr', 'index', 'database', 'query',
            'assertion', 'validation', 'missing', 'slow', 'performance'
        ]
        
        keywords = []
        for term in tech_terms:
            if term in text:
                keywords.append(term)
        
        # Extract from test name
        test_parts = failure.test_name.split('_')
        for part in test_parts:
            if len(part) >= 4 and part not in ['test', 'should', 'when', 'then']:
                keywords.append(part)
        
        return list(set(keywords))[:10]  # Limit to 10 keywords
    
    def _generate_summary(self, failure: TestFailure) -> str:
        """Generate bug summary from test failure."""
        # Extract key information from error message
        error_lower = failure.error_message.lower()
        
        if 'mongodb' in error_lower and 'connection' in error_lower:
            return f"MongoDB connection failure in {failure.test_name}"
        elif 'timeout' in error_lower:
            return f"Timeout error in {failure.test_name}"
        elif 'missing' in error_lower and 'index' in error_lower:
            return f"MongoDB indexes missing - slow query performance"
        elif 'assertion' in error_lower:
            return f"Test assertion failed: {failure.test_name}"
        else:
            # Use error type and test name
            return f"{failure.error_type} in {failure.test_name}"
    
    def _generate_description(self, failure: TestFailure) -> str:
        """Generate bug description from test failure."""
        parts = []
        
        parts.append(f"Test: {failure.test_name}")
        parts.append(f"Error Type: {failure.error_type}")
        parts.append(f"Error Message: {failure.error_message}")
        
        if failure.traceback:
            parts.append(f"Traceback:\n{failure.traceback}")
        
        return "\n".join(parts)
    
    def _calculate_similarity_for_failure(
        self,
        failure: TestFailure,
        existing_bug: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between failure and existing bug."""
        return self.deduplication_service._calculate_similarity(
            summary1=self._generate_summary(failure),
            description1=self._generate_description(failure),
            keywords1=self._extract_keywords(failure),
            error1=failure.error_message,
            summary2=existing_bug['summary'],
            description2=existing_bug.get('description', ''),
            labels2=existing_bug.get('labels', [])
        )
    
    def close(self):
        """Close the service and clean up resources."""
        if hasattr(self, 'deduplication_service') and self.deduplication_service:
            self.deduplication_service.close()

