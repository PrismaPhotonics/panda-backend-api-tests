"""
Jira Client - Production-Grade Jira API Integration
====================================================

This module provides a comprehensive Jira API client for the Focus Server Automation framework.
It uses the official Jira Python library (jira) to interact with Jira Cloud, Server, and Data Center.

Main Features:
- Create, read, update, and delete issues
- Search issues using JQL (Jira Query Language)
- Manage issue transitions and workflows
- Template-based issue creation
- Comprehensive error handling and logging

Author: QA Automation Architect
Date: 2025-11-04
Version: 1.0.0
"""

import logging
import os
import sys
import importlib.util
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# Check if jira library is installed (not the scripts/jira directory)
# We need to ensure we're importing from the installed package, not scripts/jira/
try:
    # First, check if scripts/jira/ is in sys.modules and remove it
    if 'jira' in sys.modules:
        jira_module = sys.modules['jira']
        if hasattr(jira_module, '__file__') and jira_module.__file__:
            jira_path = Path(jira_module.__file__).resolve()
            # Check if it's from scripts/jira/ directory
            if 'scripts' in str(jira_path) and 'jira' in str(jira_path):
                # Clear the wrong import
                del sys.modules['jira']
                # Also clear any submodules
                modules_to_remove = [k for k in sys.modules.keys() if k.startswith('jira.')]
                for k in modules_to_remove:
                    del sys.modules[k]
    
    # Now try to import from the installed package
    from jira import JIRA
    from jira.exceptions import JIRAError
except ImportError as e:
    # Check if the error is because we're trying to import from scripts/jira/
    error_str = str(e).lower()
    if 'scripts' in error_str or 'cannot import' in error_str:
        # Try to find and import from site-packages directly
        try:
            import site
            import importlib
            # Get site-packages paths
            site_packages = site.getsitepackages()
            for sp_path in site_packages:
                jira_path = Path(sp_path) / 'jira'
                if jira_path.exists() and jira_path.is_dir():
                    # Add to sys.path temporarily
                    sys.path.insert(0, str(sp_path))
                    try:
                        from jira import JIRA
                        from jira.exceptions import JIRAError
                        break
                    finally:
                        # Remove from sys.path
                        if str(sp_path) in sys.path:
                            sys.path.remove(str(sp_path))
            else:
                raise ImportError(
                    "Jira library not installed. Please install it using: pip install jira"
                )
        except Exception:
            raise ImportError(
                "Jira library not installed. Please install it using: pip install jira\n"
                f"Original error: {e}"
            )
    else:
        raise ImportError(
            "Jira library not installed. Please install it using: pip install jira\n"
            f"Original error: {e}"
        )

try:
    import yaml
except ImportError:
    raise ImportError(
        "PyYAML not installed. Please install it using: pip install pyyaml"
    )

logger = logging.getLogger(__name__)


class JiraClient:
    """
    Production-grade Jira API client for Focus Server Automation.
    
    This class provides a comprehensive interface for interacting with Jira,
    supporting both Jira Cloud and Jira Server/Data Center.
    
    Features:
    - Automatic configuration loading from YAML
    - Support for API token and username/password authentication
    - Template-based issue creation
    - Comprehensive error handling
    - Connection pooling and resource management
    
    Example:
        ```python
        from external.jira import JiraClient
        
        # Initialize client with default config
        client = JiraClient()
        
        # Create an issue
        issue = client.create_issue(
            summary="Bug in API endpoint",
            description="The /channels endpoint returns 500 error",
            issue_type="Bug",
            priority="High",
            labels=["bug", "api", "critical"]
        )
        
        # Search for issues
        issues = client.search_issues("project = PZ AND status != Done")
        
        # Update issue
        client.update_issue("PZ-12345", priority="Highest")
        
        # Close connection
        client.close()
        ```
    
    Attributes:
        jira: JIRA client instance
        config: Configuration dictionary
        project_key: Default project key
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
        verify_ssl: Optional[bool] = None,
        timeout: Optional[int] = None
    ):
        """
        Initialize Jira Client.
        
        Args:
            config_path: Path to jira_config.yaml file (default: config/jira_config.yaml)
            base_url: Jira base URL (overrides config)
            api_token: API token for authentication (overrides config)
            email: Email for API token auth (overrides config, required for Cloud)
            username: Username for basic auth (overrides config, for Server/Data Center)
            password: Password for basic auth (overrides config, for Server/Data Center)
            project_key: Default project key (overrides config)
            verify_ssl: Whether to verify SSL certificates (overrides config)
            timeout: Request timeout in seconds (overrides config)
        
        Raises:
            FileNotFoundError: If config file not found
            ValueError: If required configuration is missing
            ConnectionError: If connection to Jira fails
            JIRAError: If Jira API returns an error
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Override config with provided parameters
        if base_url:
            self.config['jira']['base_url'] = base_url
        if api_token:
            self.config['jira']['api_token'] = api_token
        if email:
            self.config['jira']['email'] = email
        if username:
            self.config['jira']['username'] = username
        if password:
            self.config['jira']['password'] = password
        if project_key:
            self.config['jira']['project_key'] = project_key
        if verify_ssl is not None:
            self.config['jira']['verify_ssl'] = verify_ssl
        if timeout:
            self.config['jira']['timeout'] = timeout
        
        # Extract configuration
        jira_config = self.config.get('jira', {})
        self.base_url = jira_config.get('base_url')
        self.api_token = jira_config.get('api_token')
        self.email = jira_config.get('email')
        self.username = jira_config.get('username')
        self.password = jira_config.get('password')
        self.project_key = jira_config.get('project_key', 'PZ')
        self.verify_ssl = jira_config.get('verify_ssl', True)
        self.timeout = jira_config.get('timeout', 30)
        self.max_results = jira_config.get('max_results', 100)
        
        # Validate required configuration
        if not self.base_url:
            raise ValueError("Jira base_url is required")
        
        # Initialize JIRA client
        self.jira = self._create_jira_client()
        
        # Verify connection
        try:
            # Test connection by getting current user
            current_user = self.jira.current_user()
            logger.info(f"Successfully connected to Jira as user: {current_user}")
        except JIRAError as e:
            logger.error(f"Failed to connect to Jira: {e}")
            raise ConnectionError(f"Failed to connect to Jira: {e}")
        
        logger.info(f"JiraClient initialized successfully for project: {self.project_key}")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to config file (optional)
        
        Returns:
            Configuration dictionary
        
        Raises:
            FileNotFoundError: If config file not found
        """
        if config_path is None:
            # Default config path
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'jira_config.yaml'
            )
        
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Jira config file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if config is None:
            config = {}
        
        logger.debug(f"Loaded Jira configuration from: {config_path}")
        return config
    
    def _create_jira_client(self) -> JIRA:
        """
        Create JIRA client instance with appropriate authentication.
        
        Returns:
            JIRA client instance
        
        Raises:
            ValueError: If authentication credentials are invalid
        """
        # Determine authentication method
        auth_options = {}
        
        if self.api_token:
            # API token authentication (preferred for Cloud)
            if self.email:
                # Jira Cloud: use email + API token
                auth_options = {
                    'basic_auth': (self.email, self.api_token)
                }
            else:
                # Jira Server/Data Center: use username + API token
                if not self.username:
                    raise ValueError(
                        "Username is required when using API token without email "
                        "(for Jira Server/Data Center)"
                    )
                auth_options = {
                    'basic_auth': (self.username, self.api_token)
                }
        elif self.username and self.password:
            # Username/password authentication (for Server/Data Center)
            auth_options = {
                'basic_auth': (self.username, self.password)
            }
        else:
            raise ValueError(
                "Authentication credentials required. "
                "Provide either (api_token + email) or (username + password)"
            )
        
        # Create JIRA client
        options = {
            'server': self.base_url,
            'verify': self.verify_ssl,
            'timeout': self.timeout
        }
        
        try:
            jira_client = JIRA(options=options, **auth_options)
            logger.info(f"Created JIRA client for: {self.base_url}")
            return jira_client
        except JIRAError as e:
            logger.error(f"Failed to create JIRA client: {e}")
            raise
    
    # ============================================================================
    # Issue Creation Methods
    # ============================================================================
    
    def create_issue(
        self,
        summary: str,
        description: Optional[str] = None,
        issue_type: str = "Task",
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None,
        components: Optional[List[str]] = None,
        project_key: Optional[str] = None,
        parent_key: Optional[str] = None,
        reporter: Optional[str] = None,
        custom_fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Jira issue.
        
        Args:
            summary: Issue summary/title (required)
            description: Issue description (optional)
            issue_type: Issue type (Task, Bug, Story, Epic, Sub-task, etc.)
            priority: Priority (Lowest, Low, Medium, High, Highest)
            labels: List of labels
            assignee: Assignee username or account ID
            components: List of component names
            project_key: Project key (defaults to config)
            parent_key: Parent issue key (required for Sub-task)
            reporter: Reporter username or account ID
            custom_fields: Dictionary of custom field IDs to values
        
        Returns:
            Dictionary with issue details:
            - key: Issue key (e.g., "PZ-12345")
            - url: Issue URL
            - summary: Issue summary
            - status: Issue status
            - priority: Issue priority
            - assignee: Assignee
            - labels: List of labels
            - created: Creation timestamp
            - updated: Last update timestamp
        
        Raises:
            ValueError: If required parameters are missing
            JIRAError: If issue creation fails
        
        Example:
            ```python
            issue = client.create_issue(
                summary="Bug in API endpoint",
                description="The /channels endpoint returns 500 error",
                issue_type="Bug",
                priority="High",
                labels=["bug", "api", "critical"],
                assignee="john.doe"
            )
            print(f"Created issue: {issue['key']}")
            ```
        """
        if not summary:
            raise ValueError("Issue summary is required")
        
        # Use project key from parameter or default
        project = project_key or self.project_key
        
        if not project:
            raise ValueError("Project key is required")
        
        # Build issue fields
        fields = {
            'project': {'key': project},
            'summary': summary,
            'issuetype': {'name': issue_type}
        }
        
        # Add description if provided
        if description:
            fields['description'] = description
        
        # Add priority if provided
        if priority:
            fields['priority'] = {'name': priority}
        
        # Add labels if provided
        if labels:
            fields['labels'] = labels
        
        # Add assignee if provided
        if assignee:
            fields['assignee'] = {'name': assignee}
        
        # Add reporter if provided
        if reporter:
            fields['reporter'] = {'name': reporter}
        
        # Add components if provided
        if components:
            # Get component IDs from names
            component_ids = []
            try:
                project_obj = self.jira.project(project)
                for component_name in components:
                    for comp in project_obj.components:
                        if comp.name == component_name:
                            component_ids.append({'id': comp.id})
                            break
                if component_ids:
                    fields['components'] = component_ids
            except Exception as e:
                logger.warning(f"Failed to resolve components: {e}")
        
        # Add parent for Sub-task
        if issue_type == 'Sub-task':
            if not parent_key:
                raise ValueError("Parent issue key is required for Sub-task")
            fields['parent'] = {'key': parent_key}
        
        # Add custom fields if provided
        if custom_fields:
            fields.update(custom_fields)
        
        try:
            # Create issue
            new_issue = self.jira.create_issue(fields=fields)
            
            # Get full issue details
            issue_dict = self._issue_to_dict(new_issue)
            
            logger.info(f"Created issue: {issue_dict['key']} - {summary}")
            return issue_dict
        
        except JIRAError as e:
            logger.error(f"Failed to create issue: {e}")
            raise
    
    def create_issue_from_template(
        self,
        template_name: str,
        summary: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None,
        components: Optional[List[str]] = None,
        project_key: Optional[str] = None,
        parent_key: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create an issue using a predefined template.
        
        Args:
            template_name: Template name (bug, task, story, epic, sub_task)
            summary: Issue summary/title
            description: Issue description
            priority: Priority (overrides template default)
            labels: Additional labels (merged with template labels)
            assignee: Assignee username or account ID
            components: List of component names
            project_key: Project key (defaults to config)
            parent_key: Parent issue key (for Sub-task)
            **kwargs: Additional fields to pass to create_issue
        
        Returns:
            Dictionary with issue details
        
        Raises:
            ValueError: If template not found
            JIRAError: If issue creation fails
        
        Example:
            ```python
            issue = client.create_issue_from_template(
                template_name="bug",
                summary="API endpoint returns 500",
                description="The /channels endpoint fails",
                priority="Highest"  # Overrides template default
            )
            ```
        """
        # Get template from config
        templates = self.config.get('templates', {})
        template = templates.get(template_name)
        
        if not template:
            available_templates = ', '.join(templates.keys())
            raise ValueError(
                f"Template '{template_name}' not found. "
                f"Available templates: {available_templates}"
            )
        
        # Merge template values with provided parameters
        issue_type = template.get('issue_type', 'Task')
        template_priority = template.get('priority')
        template_labels = template.get('labels', [])
        
        # Use provided priority or template default
        final_priority = priority or template_priority
        
        # Merge labels
        final_labels = template_labels.copy()
        if labels:
            final_labels.extend(labels)
        # Remove duplicates while preserving order
        final_labels = list(dict.fromkeys(final_labels))
        
        # Create issue with merged values
        return self.create_issue(
            summary=summary,
            description=description,
            issue_type=issue_type,
            priority=final_priority,
            labels=final_labels if final_labels else None,
            assignee=assignee,
            components=components,
            project_key=project_key,
            parent_key=parent_key,
            **kwargs
        )
    
    # ============================================================================
    # Issue Retrieval Methods
    # ============================================================================
    
    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Get issue details by key.
        
        Args:
            issue_key: Issue key (e.g., "PZ-12345")
        
        Returns:
            Dictionary with issue details
        
        Raises:
            JIRAError: If issue not found or API error occurs
        
        Example:
            ```python
            issue = client.get_issue("PZ-12345")
            print(f"Status: {issue['status']}")
            print(f"Priority: {issue['priority']}")
            ```
        """
        try:
            issue = self.jira.issue(issue_key)
            issue_dict = self._issue_to_dict(issue)
            logger.debug(f"Retrieved issue: {issue_key}")
            return issue_dict
        except JIRAError as e:
            logger.error(f"Failed to get issue {issue_key}: {e}")
            raise
    
    def get_issues_by_keys(self, issue_keys: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple issues by their keys.
        
        Args:
            issue_keys: List of issue keys
        
        Returns:
            List of issue dictionaries
        
        Raises:
            JIRAError: If any issue retrieval fails
        """
        issues = []
        for key in issue_keys:
            try:
                issue = self.get_issue(key)
                issues.append(issue)
            except JIRAError as e:
                logger.warning(f"Failed to get issue {key}: {e}")
                # Continue with other issues
        
        return issues
    
    def search_issues(
        self,
        jql: str,
        max_results: Optional[int] = None,
        start_at: int = 0,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for issues using JQL (Jira Query Language).
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results (defaults to config)
            start_at: Starting index for pagination
            fields: List of fields to include (None = all fields)
        
        Returns:
            List of issue dictionaries
        
        Raises:
            ValueError: If JQL is invalid
            JIRAError: If search fails
        
        Example:
            ```python
            # Search for open bugs
            issues = client.search_issues(
                "project = PZ AND type = Bug AND status != Done"
            )
            
            # Search with pagination
            issues = client.search_issues(
                "project = PZ",
                max_results=50,
                start_at=0
            )
            ```
        """
        if not jql:
            raise ValueError("JQL query is required")
        
        max_results = max_results or self.max_results
        
        try:
            issues = self.jira.search_issues(
                jql_str=jql,
                maxResults=max_results,
                startAt=start_at,
                fields=fields
            )
            
            issue_list = [self._issue_to_dict(issue) for issue in issues]
            logger.info(f"Found {len(issue_list)} issue(s) with JQL: {jql}")
            return issue_list
        
        except JIRAError as e:
            logger.error(f"JQL search failed: {e}")
            raise
    
    def get_project_open_issues(
        self,
        project_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all open issues in a project.
        
        Args:
            project_key: Project key (defaults to config)
        
        Returns:
            List of open issue dictionaries
        
        Example:
            ```python
            issues = client.get_project_open_issues("PZ")
            print(f"Found {len(issues)} open issues")
            ```
        """
        project = project_key or self.project_key
        jql = f"project = {project} AND status != Done"
        return self.search_issues(jql)
    
    def get_my_open_issues(
        self,
        project_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all open issues assigned to current user.
        
        Args:
            project_key: Project key (defaults to config)
        
        Returns:
            List of issue dictionaries
        
        Example:
            ```python
            my_issues = client.get_my_open_issues("PZ")
            print(f"You have {len(my_issues)} open issues")
            ```
        """
        project = project_key or self.project_key
        jql = f"project = {project} AND assignee = currentUser() AND status != Done"
        return self.search_issues(jql)
    
    def get_project_bugs(
        self,
        project_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all open bugs in a project.
        
        Args:
            project_key: Project key (defaults to config)
        
        Returns:
            List of bug issue dictionaries
        
        Example:
            ```python
            bugs = client.get_project_bugs("PZ")
            print(f"Found {len(bugs)} open bugs")
            ```
        """
        project = project_key or self.project_key
        jql = f"project = {project} AND issuetype = Bug AND status != Done"
        return self.search_issues(jql)
    
    def search_issues_by_filter(
        self,
        filter_name: str,
        project_key: Optional[str] = None,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search issues using a predefined filter from config.
        
        Args:
            filter_name: Filter name from config
            project_key: Project key (defaults to config)
            max_results: Maximum number of results
        
        Returns:
            List of issue dictionaries
        
        Raises:
            ValueError: If filter not found
        
        Example:
            ```python
            issues = client.search_issues_by_filter("my_open", project_key="PZ")
            ```
        """
        # Get filters from config
        filters = self.config.get('filters', {})
        filter_jql = filters.get(filter_name)
        
        if not filter_jql:
            available_filters = ', '.join(filters.keys())
            raise ValueError(
                f"Filter '{filter_name}' not found. "
                f"Available filters: {available_filters}"
            )
        
        # Replace project_key placeholder
        project = project_key or self.project_key
        jql = filter_jql.replace('{project_key}', project)
        
        return self.search_issues(jql, max_results=max_results)
    
    # ============================================================================
    # Issue Update Methods
    # ============================================================================
    
    def update_issue(
        self,
        issue_key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None,
        components: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update issue fields.
        
        Args:
            issue_key: Issue key (e.g., "PZ-12345")
            summary: New summary
            description: New description
            priority: New priority
            labels: New labels (replaces existing)
            assignee: New assignee
            components: New components
            custom_fields: Dictionary of custom field IDs to values
        
        Returns:
            Updated issue dictionary
        
        Raises:
            JIRAError: If update fails
        
        Example:
            ```python
            # Update priority
            issue = client.update_issue("PZ-12345", priority="Highest")
            
            # Update multiple fields
            issue = client.update_issue(
                "PZ-12345",
                priority="High",
                labels=["bug", "critical", "fixed"],
                assignee="john.doe"
            )
            ```
        """
        try:
            issue = self.jira.issue(issue_key)
            fields = {}
            
            if summary:
                fields['summary'] = summary
            if description:
                fields['description'] = description
            if priority:
                fields['priority'] = {'name': priority}
            if labels is not None:
                fields['labels'] = labels
            if assignee:
                fields['assignee'] = {'name': assignee}
            if components:
                # Get component IDs from names
                component_ids = []
                try:
                    project_obj = self.jira.project(issue.fields.project.key)
                    for component_name in components:
                        for comp in project_obj.components:
                            if comp.name == component_name:
                                component_ids.append({'id': comp.id})
                                break
                    if component_ids:
                        fields['components'] = component_ids
                except Exception as e:
                    logger.warning(f"Failed to resolve components: {e}")
            if custom_fields:
                fields.update(custom_fields)
            
            if fields:
                issue.update(fields=fields)
                logger.info(f"Updated issue: {issue_key}")
            
            # Get updated issue
            updated_issue = self.get_issue(issue_key)
            return updated_issue
        
        except JIRAError as e:
            logger.error(f"Failed to update issue {issue_key}: {e}")
            raise
    
    def transition_issue(
        self,
        issue_key: str,
        status: str
    ) -> bool:
        """
        Transition issue to a new status.
        
        Args:
            issue_key: Issue key (e.g., "PZ-12345")
            status: Target status name (e.g., "In Progress", "Done")
        
        Returns:
            True if successful
        
        Raises:
            JIRAError: If transition fails
        
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
            
            # Find transition ID for target status
            transition_id = None
            for transition in transitions:
                if transition['name'].lower() == status.lower():
                    transition_id = transition['id']
                    break
            
            if transition_id is None:
                # Try to find transition by "to" status
                for transition in transitions:
                    to_status = transition.get('to', {}).get('name', '')
                    if to_status.lower() == status.lower():
                        transition_id = transition['id']
                        break
            
            if transition_id is None:
                available_transitions = [t['name'] for t in transitions]
                raise ValueError(
                    f"Transition to '{status}' not available. "
                    f"Available transitions: {available_transitions}"
                )
            
            # Perform transition
            self.jira.transition_issue(issue, transition_id)
            logger.info(f"Transitioned issue {issue_key} to: {status}")
            return True
        
        except JIRAError as e:
            logger.error(f"Failed to transition issue {issue_key}: {e}")
            raise
    
    def add_comment(
        self,
        issue_key: str,
        comment: str,
        visibility: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Add a comment to an issue.
        
        Args:
            issue_key: Issue key (e.g., "PZ-12345")
            comment: Comment text
            visibility: Comment visibility (optional)
                Example: {'type': 'role', 'value': 'Administrators'}
        
        Returns:
            Comment dictionary with id, body, author, created, etc.
        
        Raises:
            JIRAError: If comment addition fails
        
        Example:
            ```python
            comment = client.add_comment(
                "PZ-12345",
                "This issue is fixed in commit abc123"
            )
            print(f"Comment ID: {comment['id']}")
            ```
        """
        try:
            issue = self.jira.issue(issue_key)
            new_comment = self.jira.add_comment(issue, comment, visibility=visibility)
            
            comment_dict = {
                'id': new_comment.id,
                'body': new_comment.body,
                'author': new_comment.author.displayName,
                'created': str(new_comment.created),
                'updated': str(new_comment.updated) if hasattr(new_comment, 'updated') else None
            }
            
            logger.info(f"Added comment to issue: {issue_key}")
            return comment_dict
        
        except JIRAError as e:
            logger.error(f"Failed to add comment to issue {issue_key}: {e}")
            raise
    
    # ============================================================================
    # Utility Methods
    # ============================================================================
    
    def _issue_to_dict(self, issue: Any) -> Dict[str, Any]:
        """
        Convert Jira issue object to dictionary.
        
        Args:
            issue: Jira issue object
        
        Returns:
            Dictionary with issue details
        """
        try:
            issue_dict = {
                'key': issue.key,
                'url': f"{self.base_url}/browse/{issue.key}",
                'summary': issue.fields.summary,
                'status': issue.fields.status.name,
                'priority': issue.fields.priority.name if issue.fields.priority else None,
                'issue_type': issue.fields.issuetype.name,
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
                'reporter': issue.fields.reporter.displayName if issue.fields.reporter else None,
                'labels': list(issue.fields.labels) if issue.fields.labels else [],
                'created': str(issue.fields.created),
                'updated': str(issue.fields.updated),
                'description': issue.fields.description or '',
                'project': issue.fields.project.key,
                'components': [comp.name for comp in (issue.fields.components or [])],
                'resolution': issue.fields.resolution.name if issue.fields.resolution else None
            }
            
            # Add additional fields if available
            if hasattr(issue.fields, 'customfield_10016'):  # Story Points example
                issue_dict['story_points'] = issue.fields.customfield_10016
            
            return issue_dict
        
        except Exception as e:
            logger.warning(f"Error converting issue to dict: {e}")
            # Return minimal dict if conversion fails
            return {
                'key': issue.key,
                'url': f"{self.base_url}/browse/{issue.key}",
                'summary': getattr(issue.fields, 'summary', 'N/A'),
                'status': 'Unknown',
                'priority': None,
                'issue_type': 'Unknown',
                'assignee': None,
                'reporter': None,
                'labels': [],
                'created': None,
                'updated': None,
                'description': '',
                'project': 'Unknown',
                'components': [],
                'resolution': None
            }
    
    def close(self):
        """
        Close Jira client connection and release resources.
        
        This method should be called when done with the client to properly
        clean up connections and resources.
        
        Example:
            ```python
            client = JiraClient()
            # ... use client ...
            client.close()
            ```
        """
        if hasattr(self, 'jira') and self.jira:
            try:
                # JIRA library doesn't have explicit close, but we can log
                logger.info("Closing Jira client connection")
                # The connection will be closed when the object is garbage collected
            except Exception as e:
                logger.warning(f"Error closing Jira client: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - closes connection."""
        self.close()
        return False

