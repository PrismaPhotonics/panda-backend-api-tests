"""
Bug Creator Service
===================

This module provides automatic bug creation from test failures with
deduplication support.

Features:
- Analyze test failures
- Check for existing bugs before creating new ones
- Create bugs only if no similar bug exists
- Link bugs to test failures

Author: QA Automation Architect
Date: 2025-11-08
Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from external.jira.jira_client import JiraClient
from external.jira.bug_deduplication import BugDeduplicationService
try:
    from jira.exceptions import JIRAError
except ImportError:
    # Fallback if jira library not available
    class JIRAError(Exception):
        pass

logger = logging.getLogger(__name__)


class BugCreatorService:
    """
    Service for creating bugs from test failures with deduplication.
    
    This service:
    1. Analyzes test failures
    2. Checks for existing similar bugs
    3. Creates new bugs only if no similar bug exists
    4. Links bugs to test failures
    
    Example:
        ```python
        from external.jira.bug_creator import BugCreatorService
        
        service = BugCreatorService()
        
        # Create bug from test failure
        bug = service.create_bug_from_test_failure(
            test_name="test_mongodb_connection",
            error_message="Connection failed: timeout",
            summary="MongoDB connection timeout",
            description="Test failed due to MongoDB connection timeout",
            priority="High"
        )
        
        if bug:
            print(f"Created bug: {bug['key']}")
        else:
            print("Similar bug already exists")
        ```
    """
    
    def __init__(
        self,
        jira_client: Optional[JiraClient] = None,
        deduplication_service: Optional[BugDeduplicationService] = None,
        project_key: Optional[str] = None,
        default_reporter: Optional[str] = None
    ):
        """
        Initialize Bug Creator Service.
        
        Args:
            jira_client: JiraClient instance (creates new if not provided)
            deduplication_service: BugDeduplicationService instance (creates new if not provided)
            project_key: Project key (defaults to client config)
            default_reporter: Default reporter email/username
        """
        self.jira_client = jira_client or JiraClient()
        self.deduplication_service = deduplication_service or BugDeduplicationService(
            jira_client=self.jira_client,
            project_key=project_key
        )
        self.project_key = project_key or self.jira_client.project_key
        self.default_reporter = default_reporter
        
        logger.info(f"BugCreatorService initialized for project: {self.project_key}")
    
    def create_bug_from_test_failure(
        self,
        test_name: str,
        error_message: str,
        summary: str,
        description: str,
        priority: str = "High",
        labels: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        steps_to_reproduce: Optional[List[str]] = None,
        expected_result: Optional[str] = None,
        actual_result: Optional[str] = None,
        environment: Optional[str] = None,
        skip_duplicate_check: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create a bug from a test failure, checking for duplicates first.
        
        Args:
            test_name: Name of the test that failed
            error_message: Error message from test failure
            summary: Bug summary/title
            description: Bug description
            priority: Bug priority (Lowest, Low, Medium, High, Highest)
            labels: Additional labels
            keywords: Keywords for deduplication
            steps_to_reproduce: Steps to reproduce the issue
            expected_result: Expected result
            actual_result: Actual result
            environment: Environment where the issue occurred
            skip_duplicate_check: Skip duplicate check (not recommended)
            
        Returns:
            Dictionary of created bug, or None if similar bug exists
        """
        logger.info(f"Creating bug from test failure: {test_name}")
        
        # Check for existing similar bugs
        if not skip_duplicate_check:
            existing_bug = self.deduplication_service.find_similar_bug(
                summary=summary,
                description=description,
                keywords=keywords or self._extract_keywords_from_text(summary + " " + description),
                error_message=error_message,
                test_name=test_name
            )
            
            if existing_bug:
                logger.warning(
                    f"Similar bug already exists: {existing_bug['key']} - {existing_bug['summary']}"
                )
                logger.info(f"  URL: {existing_bug['url']}")
                logger.info(f"  Status: {existing_bug['status']}")
                return None
        
        # Build bug description
        full_description = self._build_bug_description(
            description=description,
            test_name=test_name,
            error_message=error_message,
            steps_to_reproduce=steps_to_reproduce,
            expected_result=expected_result,
            actual_result=actual_result,
            environment=environment
        )
        
        # Build labels
        final_labels = self._build_labels(labels, test_name, error_message)
        
        # Build custom fields
        custom_fields = self._build_custom_fields(
            steps_to_reproduce=steps_to_reproduce,
            expected_result=expected_result,
            actual_result=actual_result
        )
        
        # Create bug
        try:
            bug = self.jira_client.create_issue(
                summary=summary,
                description=full_description,
                issue_type="Bug",
                priority=priority,
                labels=final_labels,
                custom_fields=custom_fields,
                project_key=self.project_key,
                reporter=self.default_reporter
            )
            
            logger.info(f"✅ Created bug: {bug['key']} - {summary}")
            logger.info(f"  URL: {bug['url']}")
            
            return bug
            
        except JIRAError as e:
            logger.error(f"Failed to create bug: {e}")
            raise
    
    def _build_bug_description(
        self,
        description: str,
        test_name: str,
        error_message: str,
        steps_to_reproduce: Optional[List[str]],
        expected_result: Optional[str],
        actual_result: Optional[str],
        environment: Optional[str]
    ) -> str:
        """Build full bug description from components."""
        parts = []
        
        # Main description
        if description:
            parts.append(f"*Description:*\n{description}\n")
        
        # Test information
        parts.append(f"*Test Name:*\n{{code}}{test_name}{{code}}\n")
        
        # Error message
        if error_message:
            parts.append(f"*Error Message:*\n{{code}}{error_message}{{code}}\n")
        
        # Steps to reproduce
        if steps_to_reproduce:
            steps_text = "\n".join([f"# {step}" for step in steps_to_reproduce])
            parts.append(f"*Steps to Reproduce:*\n{steps_text}\n")
        
        # Expected result
        if expected_result:
            parts.append(f"*Expected Result:*\n{expected_result}\n")
        
        # Actual result
        if actual_result:
            parts.append(f"*Actual Result:*\n{actual_result}\n")
        
        # Environment
        if environment:
            parts.append(f"*Environment:*\n{environment}\n")
        
        # Found by
        parts.append(f"*Found by:*\nQA Cycle (Automated Test)\n")
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        parts.append(f"*Reported:*\n{timestamp}\n")
        
        return "\n".join(parts)
    
    def _build_labels(
        self,
        labels: Optional[List[str]],
        test_name: str,
        error_message: str
    ) -> List[str]:
        """Build labels list."""
        final_labels = ["automation", "qa-cycle", "test-failure"]
        
        if labels:
            final_labels.extend(labels)
        
        # Add labels based on test name
        if "mongodb" in test_name.lower() or "mongodb" in error_message.lower():
            final_labels.append("mongodb")
        if "api" in test_name.lower() or "api" in error_message.lower():
            final_labels.append("api")
        if "kubernetes" in test_name.lower() or "k8s" in test_name.lower():
            final_labels.append("kubernetes")
        if "infrastructure" in test_name.lower():
            final_labels.append("infrastructure")
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(final_labels))
    
    def _build_custom_fields(
        self,
        steps_to_reproduce: Optional[List[str]],
        expected_result: Optional[str],
        actual_result: Optional[str]
    ) -> Dict[str, Any]:
        """Build custom fields dictionary."""
        custom_fields = {}
        
        # Found by
        custom_fields['customfield_10038'] = {"value": "QA Cycle"}
        
        # Steps to reproduce
        if steps_to_reproduce:
            steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps_to_reproduce)])
            custom_fields['customfield_10123'] = steps_text
        
        # Expected result
        if expected_result:
            custom_fields['customfield_10179'] = expected_result
        
        # Actual result
        if actual_result:
            custom_fields['customfield_10180'] = actual_result
        
        return custom_fields
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text for deduplication."""
        if not text:
            return []
        
        # Simple keyword extraction
        import re
        words = re.findall(r'\b\w{4,}\b', text.lower())
        
        # Common technical terms
        tech_terms = [
            'mongodb', 'connection', 'timeout', 'error', 'failure', 'restart',
            'pod', 'kubernetes', 'k8s', 'api', 'endpoint', 'configure',
            'metadata', 'fiber', 'prr', 'index', 'database', 'query'
        ]
        
        keywords = []
        for word in words:
            if word in tech_terms:
                keywords.append(word)
        
        return list(set(keywords))[:10]  # Limit to 10 keywords
    
    def close(self):
        """Close the service and clean up resources."""
        if hasattr(self, 'deduplication_service') and self.deduplication_service:
            self.deduplication_service.close()
        if hasattr(self, 'jira_client') and self.jira_client:
            self.jira_client.close()

