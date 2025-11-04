"""
Jira Client - Comprehensive Jira API Integration
===============================================

This module provides a production-grade client for interacting with Jira API.
Supports creating, reading, updating, searching, and managing Jira issues.

Author: QA Automation Architect
Date: 2025-11-04
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import yaml
from jira import JIRA
from jira.exceptions import JIRAError
from requests.exceptions import RequestException

from config.config_manager import ConfigManager


# Configure logging
logger = logging.getLogger(__name__)


class JiraClient:
    """
    Production-grade Jira API client for comprehensive issue management.
    
    This client provides a complete interface for:
    - Creating issues (Tasks, Bugs, Stories, Epics, Sub-tasks)
    - Reading and retrieving issues
    - Updating issue fields and status
    - Searching issues with JQL
    - Managing issue links and attachments
    - Working with projects, fields, and metadata
    
    Features:
    - Automatic authentication handling
    - Comprehensive error handling and logging
    - Support for custom fields
    - Template-based issue creation
    - Predefined search filters
    - Connection pooling and retry logic
    
    Example:
        ```python
        from external.jira import JiraClient
        
        # Initialize client
        client = JiraClient()
        
        # Create a bug
        issue = client.create_issue(
            summary="Bug in API endpoint",
            description="The /channels endpoint returns 500 error",
            issue_type="Bug",
            priority="High",
            labels=["bug", "api", "critical"]
        )
        
        # Search for issues
        issues = client.search_issues("project = PZ AND status != Done")
        
        # Get issue details
        issue = client.get_issue("PZ-12345")
        ```
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        base_url: Optional[str] = None,
        api_token: Optional[str] = None,
        email: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        project_key: Optional[str] = None,
        verify_ssl: Optional[bool] = None
    ):
        """
        Initialize Jira Client.
        
        Args:
            config_path: Path to jira_config.yaml (optional, uses default if not provided)
            base_url: Jira server URL (overrides config)
            api_token: Jira API token (overrides config)
            email: Email for API token auth (overrides config, required for Cloud)
            username: Username for basic auth (overrides config, for Server/Data Center)
            password: Password for basic auth (overrides config, for Server/Data Center)
            project_key: Default project key (overrides config)
            verify_ssl: Whether to verify SSL certificates (overrides config)
        
        Raises:
            ValueError: If required configuration is missing
            ConnectionError: If connection to Jira fails
        """
        # Load configuration
        self._load_config(config_path)
        
        # Override config with provided parameters
        self.base_url = base_url or self.config.get("base_url")
        self.api_token = api_token or self.config.get("api_token")
        self.email = email or self.config.get("email")
        self.username = username or self.config.get("username")
        self.password = password or self.config.get("password")
        self.project_key = project_key or self.config.get("project_key", "PZ")
        self.verify_ssl = verify_ssl if verify_ssl is not None else self.config.get("verify_ssl", True)
        self.timeout = self.config.get("timeout", 30)
        self.max_results = self.config.get("max_results", 100)
        
        # Validate required configuration
        if not self.base_url:
            raise ValueError("Jira base_url is required. Set in config or pass as parameter.")
        
        if not self.api_token and not (self.username and self.password):
            raise ValueError(
                "Authentication required: Provide either api_token (and email for Cloud) "
                "or username/password for Server/Data Center."
            )
        
        # Initialize Jira client
        self._init_client()
        
        # Load additional configuration from full config (not just jira section)
        if hasattr(self, 'full_config'):
            self.defaults = self.full_config.get("defaults", {})
            self.templates = self.full_config.get("templates", {})
            self.filters = self.full_config.get("filters", {})
            self.custom_fields = self.full_config.get("custom_fields", {})
        else:
            # Fallback to empty dicts if full_config not loaded
            self.defaults = {}
            self.templates = {}
            self.filters = {}
            self.custom_fields = {}
        
        logger.info(f"JiraClient initialized successfully for {self.base_url}")
        logger.info(f"Default project: {self.project_key}")
    
    def _load_config(self, config_path: Optional[str] = None):
        """Load Jira configuration from YAML file."""
        if config_path:
            config_file = Path(config_path)
        else:
            # Use default config location
            config_dir = Path(__file__).parent.parent.parent / "config"
            config_file = config_dir / "jira_config.yaml"
        
        if not config_file.exists():
            logger.warning(f"Jira config file not found: {config_file}. Using defaults.")
            self.config = {}
            self.full_config = {}
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
                self.full_config = config_data  # Store full config
                self.config = config_data.get("jira", {})
        except Exception as e:
            logger.error(f"Error loading Jira config: {e}")
            self.config = {}
            self.full_config = {}
    
    def _init_client(self):
        """Initialize Jira client with authentication."""
        try:
            # Determine authentication method
            if self.api_token:
                # API token authentication (recommended)
                if self.email:
                    # Jira Cloud: email + API token
                    auth = (self.email, self.api_token)
                else:
                    # Jira Server/Data Center: username + API token
                    auth = (self.username or "api_token_user", self.api_token)
            else:
                # Basic authentication (username/password)
                auth = (self.username, self.password)
            
            # Initialize JIRA client
            options = {
                'server': self.base_url,
                'verify': self.verify_ssl
            }
            
            self.jira = JIRA(
                options=options,
                basic_auth=auth,
                timeout=self.timeout,
                max_retries=3
            )
            
            # Test connection
            current_user = self.jira.current_user()
            logger.info(f"Successfully connected to Jira as: {current_user}")
            
        except JIRAError as e:
            logger.error(f"Jira connection error: {e}")
            raise ConnectionError(f"Failed to connect to Jira: {e}")
        except RequestException as e:
            logger.error(f"Network error connecting to Jira: {e}")
            raise ConnectionError(f"Network error connecting to Jira: {e}")
        except Exception as e:
            logger.error(f"Unexpected error initializing Jira client: {e}")
            raise
    
    # ============================================================================
    # Issue Creation Methods
    # ============================================================================
    
    def create_issue(
        self,
        summary: str,
        description: Optional[str] = None,
        issue_type: Optional[str] = None,
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None,
        components: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
        project_key: Optional[str] = None,
        parent_key: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new Jira issue.
        
        Args:
            summary: Issue summary/title (required)
            description: Issue description (optional)
            issue_type: Issue type (Task, Bug, Story, Epic, Sub-task) - defaults to config
            priority: Priority (Lowest, Low, Medium, High, Highest) - defaults to config
            labels: List of label strings - defaults to config
            assignee: Assignee username or account ID - defaults to config
            components: List of component names - defaults to config
            custom_fields: Dict of custom field IDs/names to values
            project_key: Project key (overrides default) - defaults to config
            parent_key: Parent issue key (for sub-tasks) - required for Sub-task
            **kwargs: Additional fields to set on issue
        
        Returns:
            Dict containing issue key, ID, and URL
        
        Raises:
            ValueError: If required fields are missing
            JIRAError: If issue creation fails
        
        Example:
            ```python
            # Create a bug
            issue = client.create_issue(
                summary="API endpoint returns 500",
                description="The /channels endpoint fails with 500 error",
                issue_type="Bug",
                priority="High",
                labels=["bug", "api", "critical"]
            )
            print(f"Created issue: {issue['key']}")
            ```
        """
        if not summary:
            raise ValueError("Summary is required for issue creation")
        
        # Use defaults from config
        project = project_key or self.project_key
        issue_type = issue_type or self.defaults.get("issue_type", "Task")
        priority = priority or self.defaults.get("priority", "Medium")
        labels = labels or self.defaults.get("labels", [])
        assignee = assignee or self.defaults.get("assignee")
        components = components or self.defaults.get("components", [])
        
        # Build issue fields
        fields = {
            'project': {'key': project},
            'summary': summary,
            'issuetype': {'name': issue_type}
        }
        
        # Add description if provided
        if description:
            fields['description'] = description
        
        # Add priority if provided (but not for Epic type)
        if priority and issue_type != "Epic":
            fields['priority'] = {'name': priority}
        
        # Add labels if provided
        if labels:
            fields['labels'] = labels
        
        # Add assignee if provided
        if assignee:
            fields['assignee'] = {'name': assignee} if '@' not in assignee else {'accountId': assignee}
        
        # Add components if provided
        if components:
            fields['components'] = [{'name': comp} for comp in components]
        
        # Add parent for sub-tasks
        if parent_key:
            fields['parent'] = {'key': parent_key}
        
        # Add custom fields
        if custom_fields:
            for field_name, field_value in custom_fields.items():
                # Resolve custom field ID if needed
                field_id = self.custom_fields.get(field_name, field_name)
                fields[field_id] = field_value
        
        # Add any additional fields from kwargs
        fields.update(kwargs)
        
        try:
            # Create issue
            new_issue = self.jira.create_issue(fields=fields)
            
            # Get issue URL
            issue_url = f"{self.base_url}/browse/{new_issue.key}"
            
            result = {
                'key': new_issue.key,
                'id': new_issue.id,
                'url': issue_url,
                'summary': new_issue.fields.summary,
                'status': new_issue.fields.status.name
            }
            
            logger.info(f"Created issue: {new_issue.key} - {summary}")
            return result
            
        except JIRAError as e:
            logger.error(f"Failed to create issue: {e}")
            raise ValueError(f"Failed to create issue: {e}")
    
    def create_issue_from_template(
        self,
        template_name: str,
        summary: str,
        description: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create an issue using a predefined template.
        
        Args:
            template_name: Template name (bug, task, story, epic, sub_task)
            summary: Issue summary
            description: Issue description
            **kwargs: Additional fields to override template defaults
        
        Returns:
            Dict containing issue key, ID, and URL
        
        Example:
            ```python
            # Create a bug using template
            issue = client.create_issue_from_template(
                template_name="bug",
                summary="Critical bug in API",
                description="Detailed description here"
            )
            ```
        """
        template = self.templates.get(template_name.lower())
        if not template:
            raise ValueError(f"Template '{template_name}' not found. Available: {list(self.templates.keys())}")
        
        # Merge template with provided kwargs
        issue_params = {
            'summary': summary,
            'description': description,
            'issue_type': template.get('issue_type'),
            'priority': template.get('priority'),
            'labels': template.get('labels', [])
        }
        issue_params.update(kwargs)
        
        return self.create_issue(**issue_params)
    
    # ============================================================================
    # Issue Retrieval Methods
    # ============================================================================
    
    def get_issue(self, issue_key: str, expand: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get issue details by key.
        
        Args:
            issue_key: Issue key (e.g., PZ-12345)
            expand: List of fields to expand (e.g., ['changelog', 'renderedFields'])
        
        Returns:
            Dict containing full issue details
        
        Raises:
            ValueError: If issue not found
        
        Example:
            ```python
            issue = client.get_issue("PZ-12345")
            print(f"Status: {issue['status']}")
            print(f"Assignee: {issue['assignee']}")
            ```
        """
        try:
            expand_str = ','.join(expand) if expand else None
            issue = self.jira.issue(issue_key, expand=expand_str)
            
            return self._issue_to_dict(issue)
            
        except JIRAError as e:
            logger.error(f"Failed to get issue {issue_key}: {e}")
            raise ValueError(f"Issue {issue_key} not found: {e}")
    
    def get_issues_by_keys(self, issue_keys: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple issues by their keys.
        
        Args:
            issue_keys: List of issue keys
        
        Returns:
            List of issue dicts
        
        Example:
            ```python
            issues = client.get_issues_by_keys(["PZ-12345", "PZ-12346", "PZ-12347"])
            ```
        """
        issues = []
        for key in issue_keys:
            try:
                issue = self.get_issue(key)
                issues.append(issue)
            except Exception as e:
                logger.warning(f"Failed to get issue {key}: {e}")
                continue
        
        return issues
    
    # ============================================================================
    # Issue Search Methods
    # ============================================================================
    
    def search_issues(
        self,
        jql: str,
        max_results: Optional[int] = None,
        fields: Optional[List[str]] = None,
        expand: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for issues using JQL (Jira Query Language).
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results (defaults to config)
            fields: List of fields to return (defaults to all)
            expand: List of fields to expand
        
        Returns:
            List of issue dicts
        
        Example:
            ```python
            # Search for open issues in project
            issues = client.search_issues("project = PZ AND status != Done")
            
            # Search for bugs assigned to me
            issues = client.search_issues(
                "project = PZ AND type = Bug AND assignee = currentUser()"
            )
            ```
        """
        try:
            max_results = max_results or self.max_results
            expand_str = ','.join(expand) if expand else None
            
            # Execute search
            # jira library expects jql as first positional argument
            issues = self.jira.search_issues(
                jql,
                maxResults=max_results,
                fields=fields,
                expand=expand_str
            )
            
            # Convert to list of dicts
            result = [self._issue_to_dict(issue) for issue in issues]
            
            logger.info(f"Found {len(result)} issues matching JQL: {jql}")
            return result
            
        except JIRAError as e:
            logger.error(f"JQL search failed: {e}")
            raise ValueError(f"JQL search failed: {e}")
    
    def search_issues_by_filter(
        self,
        filter_name: str,
        project_key: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search issues using a predefined filter.
        
        Args:
            filter_name: Filter name from config (e.g., 'my_open', 'project_open')
            project_key: Project key (defaults to config)
            **kwargs: Additional parameters to substitute in filter JQL
        
        Returns:
            List of issue dicts
        
        Example:
            ```python
            # Use predefined filter
            issues = client.search_issues_by_filter("my_open")
            issues = client.search_issues_by_filter("project_open", project_key="PZ")
            ```
        """
        filter_jql = self.filters.get(filter_name)
        if not filter_jql:
            raise ValueError(f"Filter '{filter_name}' not found. Available: {list(self.filters.keys())}")
        
        # Substitute project key
        project = project_key or self.project_key
        jql = filter_jql.format(project_key=project, **kwargs)
        
        return self.search_issues(jql)
    
    def get_my_open_issues(self, project_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all open issues assigned to current user."""
        return self.search_issues_by_filter("my_open", project_key=project_key)
    
    def get_project_open_issues(self, project_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all open issues in project."""
        return self.search_issues_by_filter("project_open", project_key=project_key)
    
    def get_project_bugs(self, project_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all open bugs in project."""
        return self.search_issues_by_filter("project_bugs", project_key=project_key)
    
    # ============================================================================
    # Issue Update Methods
    # ============================================================================
    
    def update_issue(
        self,
        issue_key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        labels: Optional[List[str]] = None,
        status: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update issue fields.
        
        Args:
            issue_key: Issue key to update
            summary: New summary
            description: New description
            priority: New priority
            assignee: New assignee
            labels: New labels (replaces existing)
            status: New status (requires transition)
            **kwargs: Additional fields to update
        
        Returns:
            Updated issue dict
        
        Example:
            ```python
            # Update issue
            client.update_issue(
                issue_key="PZ-12345",
                priority="High",
                assignee="john.doe",
                labels=["critical", "urgent"]
            )
            
            # Change status
            client.update_issue(
                issue_key="PZ-12345",
                status="In Progress"
            )
            ```
        """
        try:
            issue = self.jira.issue(issue_key)
            
            # Build update fields
            update_fields = {}
            
            if summary:
                update_fields['summary'] = summary
            if description:
                update_fields['description'] = description
            if priority:
                update_fields['priority'] = {'name': priority}
            if assignee:
                update_fields['assignee'] = {'name': assignee} if '@' not in assignee else {'accountId': assignee}
            if labels:
                update_fields['labels'] = labels
            
            # Add any additional fields
            update_fields.update(kwargs)
            
            # Update issue
            if update_fields:
                issue.update(fields=update_fields)
            
            # Handle status transition if needed
            if status and status != issue.fields.status.name:
                self.transition_issue(issue_key, status)
            
            # Get updated issue
            updated_issue = self.get_issue(issue_key)
            
            logger.info(f"Updated issue: {issue_key}")
            return updated_issue
            
        except JIRAError as e:
            logger.error(f"Failed to update issue {issue_key}: {e}")
            raise ValueError(f"Failed to update issue: {e}")
    
    def transition_issue(self, issue_key: str, status: str) -> bool:
        """
        Transition issue to new status.
        
        Args:
            issue_key: Issue key
            status: Target status name
        
        Returns:
            True if successful
        
        Example:
            ```python
            # Move issue to "In Progress"
            client.transition_issue("PZ-12345", "In Progress")
            
            # Close issue
            client.transition_issue("PZ-12345", "Done")
            ```
        """
        try:
            issue = self.jira.issue(issue_key)
            
            # Get available transitions
            transitions = self.jira.transitions(issue)
            
            # Find transition to target status
            transition_id = None
            for transition in transitions:
                if transition['to']['name'] == status:
                    transition_id = transition['id']
                    break
            
            if not transition_id:
                # Try to find by common name
                transition_map = {
                    'In Progress': 'In Progress',
                    'Done': 'Done',
                    'Closed': 'Closed',
                    'To Do': 'To Do'
                }
                status = transition_map.get(status, status)
                
                for transition in transitions:
                    if transition['to']['name'].lower() == status.lower():
                        transition_id = transition['id']
                        break
            
            if not transition_id:
                available_statuses = [t['to']['name'] for t in transitions]
                raise ValueError(
                    f"Cannot transition to '{status}'. Available: {available_statuses}"
                )
            
            # Execute transition
            self.jira.transition_issue(issue, transition_id)
            
            logger.info(f"Transitioned issue {issue_key} to '{status}'")
            return True
            
        except JIRAError as e:
            logger.error(f"Failed to transition issue {issue_key}: {e}")
            raise ValueError(f"Failed to transition issue: {e}")
    
    def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """
        Add comment to issue.
        
        Args:
            issue_key: Issue key
            comment: Comment text
        
        Returns:
            Comment dict
        
        Example:
            ```python
            client.add_comment("PZ-12345", "This issue is fixed in commit abc123")
            ```
        """
        try:
            comment_obj = self.jira.add_comment(issue_key, comment)
            logger.info(f"Added comment to issue {issue_key}")
            return {
                'id': comment_obj.id,
                'body': comment_obj.body,
                'author': comment_obj.author.displayName,
                'created': comment_obj.created
            }
        except JIRAError as e:
            logger.error(f"Failed to add comment to {issue_key}: {e}")
            raise ValueError(f"Failed to add comment: {e}")
    
    # ============================================================================
    # Project and Metadata Methods
    # ============================================================================
    
    def get_project(self, project_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get project details.
        
        Args:
            project_key: Project key (defaults to config)
        
        Returns:
            Project dict
        """
        project = project_key or self.project_key
        try:
            proj = self.jira.project(project)
            return {
                'key': proj.key,
                'name': proj.name,
                'id': proj.id,
                'description': getattr(proj, 'description', ''),
                'lead': getattr(proj, 'lead', {}).get('displayName', '') if hasattr(proj, 'lead') else ''
            }
        except JIRAError as e:
            logger.error(f"Failed to get project {project}: {e}")
            raise ValueError(f"Project {project} not found: {e}")
    
    def get_issue_types(self, project_key: Optional[str] = None) -> List[str]:
        """Get available issue types for project."""
        project = project_key or self.project_key
        try:
            proj = self.jira.project(project)
            return [it.name for it in proj.issueTypes]
        except JIRAError as e:
            logger.error(f"Failed to get issue types for {project}: {e}")
            return []
    
    def get_priorities(self) -> List[str]:
        """Get available priorities."""
        try:
            priorities = self.jira.priorities()
            return [p.name for p in priorities]
        except JIRAError as e:
            logger.error(f"Failed to get priorities: {e}")
            return []
    
    # ============================================================================
    # Helper Methods
    # ============================================================================
    
    def _issue_to_dict(self, issue) -> Dict[str, Any]:
        """Convert Jira issue object to dict."""
        return {
            'key': issue.key,
            'id': issue.id,
            'url': f"{self.base_url}/browse/{issue.key}",
            'summary': issue.fields.summary,
            'description': getattr(issue.fields, 'description', ''),
            'status': issue.fields.status.name,
            'priority': getattr(issue.fields, 'priority', None) and issue.fields.priority.name or None,
            'issue_type': issue.fields.issuetype.name,
            'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
            'reporter': issue.fields.reporter.displayName if issue.fields.reporter else None,
            'labels': getattr(issue.fields, 'labels', []),
            'created': issue.fields.created,
            'updated': issue.fields.updated,
            'resolution': issue.fields.resolution.name if hasattr(issue.fields, 'resolution') and issue.fields.resolution else None
        }
    
    def close(self):
        """Close Jira client connection."""
        if hasattr(self, 'jira'):
            self.jira.close()
            logger.info("Jira client connection closed")

