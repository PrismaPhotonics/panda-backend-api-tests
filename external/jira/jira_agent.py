"""
Jira Agent - Cursor Integration
================================

Agent wrapper for Jira operations that can be easily used from Cursor.
This module provides a simplified interface for common Jira operations
that can be called directly from Cursor chat or as agent commands.

Usage from Cursor:
    "Create a bug ticket for API endpoint /channels returning 500"
    "Show me all open bugs in project PZ"
    "Update ticket PZ-12345 to status 'In Progress'"
"""

import logging
from typing import Dict, List, Optional, Any
from external.jira.jira_client import JiraClient

logger = logging.getLogger(__name__)


class JiraAgent:
    """
    Jira Agent - Simplified interface for Cursor integration.
    
    This class provides a high-level interface for common Jira operations
    that can be easily called from Cursor or other agents.
    
    Example:
        ```python
        from external.jira import JiraAgent
        
        agent = JiraAgent()
        
        # Create a bug
        issue = agent.create_bug(
            summary="API endpoint returns 500",
            description="The /channels endpoint fails with 500 error"
        )
        
        # Get open issues
        issues = agent.get_open_issues()
        
        # Update issue status
        agent.update_status("PZ-12345", "In Progress")
        ```
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Jira Agent.
        
        Args:
            config_path: Path to jira_config.yaml (optional)
        """
        self.client = JiraClient(config_path=config_path)
        logger.info("JiraAgent initialized successfully")
    
    # ============================================================================
    # Issue Creation Methods (Simplified)
    # ============================================================================
    
    def create_bug(
        self,
        summary: str,
        description: Optional[str] = None,
        priority: str = "High",
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a bug ticket.
        
        Args:
            summary: Bug summary/title
            description: Bug description
            priority: Priority (Lowest, Low, Medium, High, Highest)
            labels: List of labels
            assignee: Assignee username or account ID
        
        Returns:
            Dict with issue key, URL, and details
        
        Example:
            ```python
            issue = agent.create_bug(
                summary="API endpoint returns 500",
                description="The /channels endpoint fails with 500 error",
                priority="High",
                labels=["bug", "api", "critical"]
            )
            ```
        """
        default_labels = ["bug", "automation"]
        if labels:
            default_labels.extend(labels)
        
        issue = self.client.create_issue(
            summary=summary,
            description=description,
            issue_type="Bug",
            priority=priority,
            labels=default_labels,
            assignee=assignee
        )
        
        logger.info(f"Created bug: {issue['key']}")
        return issue
    
    def create_task(
        self,
        summary: str,
        description: Optional[str] = None,
        priority: str = "Medium",
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a task ticket.
        
        Args:
            summary: Task summary/title
            description: Task description
            priority: Priority (Lowest, Low, Medium, High, Highest)
            labels: List of labels
            assignee: Assignee username or account ID
        
        Returns:
            Dict with issue key, URL, and details
        """
        default_labels = ["automation", "qa"]
        if labels:
            default_labels.extend(labels)
        
        issue = self.client.create_issue(
            summary=summary,
            description=description,
            issue_type="Task",
            priority=priority,
            labels=default_labels,
            assignee=assignee
        )
        
        logger.info(f"Created task: {issue['key']}")
        return issue
    
    def create_story(
        self,
        summary: str,
        description: Optional[str] = None,
        priority: str = "Medium",
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a story ticket.
        
        Args:
            summary: Story summary/title
            description: Story description
            priority: Priority (Lowest, Low, Medium, High, Highest)
            labels: List of labels
            assignee: Assignee username or account ID
        
        Returns:
            Dict with issue key, URL, and details
        """
        default_labels = ["automation", "feature"]
        if labels:
            default_labels.extend(labels)
        
        issue = self.client.create_issue(
            summary=summary,
            description=description,
            issue_type="Story",
            priority=priority,
            labels=default_labels,
            assignee=assignee
        )
        
        logger.info(f"Created story: {issue['key']}")
        return issue
    
    def create_subtask(
        self,
        parent_key: str,
        summary: str,
        description: Optional[str] = None,
        priority: str = "Medium",
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a sub-task ticket.
        
        Args:
            parent_key: Parent issue key (e.g., "PZ-12345")
            summary: Sub-task summary/title
            description: Sub-task description
            priority: Priority (Lowest, Low, Medium, High, Highest)
            labels: List of labels
        
        Returns:
            Dict with issue key, URL, and details
        """
        issue = self.client.create_issue(
            summary=summary,
            description=description,
            issue_type="Sub-task",
            priority=priority,
            labels=labels or ["automation", "sub-task"],
            parent_key=parent_key
        )
        
        logger.info(f"Created sub-task: {issue['key']} under {parent_key}")
        return issue
    
    # ============================================================================
    # Issue Retrieval Methods (Simplified)
    # ============================================================================
    
    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Get issue details by key.
        
        Args:
            issue_key: Issue key (e.g., "PZ-12345")
        
        Returns:
            Dict with issue details
        """
        return self.client.get_issue(issue_key)
    
    def get_open_issues(self, project_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open issues in project.
        
        Args:
            project_key: Project key (defaults to config)
        
        Returns:
            List of issue dicts
        """
        return self.client.get_project_open_issues(project_key=project_key)
    
    def get_my_open_issues(self, project_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open issues assigned to current user.
        
        Args:
            project_key: Project key (defaults to config)
        
        Returns:
            List of issue dicts
        """
        return self.client.get_my_open_issues(project_key=project_key)
    
    def get_bugs(self, project_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open bugs in project.
        
        Args:
            project_key: Project key (defaults to config)
        
        Returns:
            List of bug issue dicts
        """
        return self.client.get_project_bugs(project_key=project_key)
    
    def search(
        self,
        jql: str,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search issues using JQL.
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results
        
        Returns:
            List of issue dicts
        
        Example:
            ```python
            # Search for high priority bugs
            issues = agent.search(
                "project = PZ AND type = Bug AND priority = High"
            )
            ```
        """
        return self.client.search_issues(jql=jql, max_results=max_results)
    
    # ============================================================================
    # Issue Update Methods (Simplified)
    # ============================================================================
    
    def update_status(
        self,
        issue_key: str,
        status: str
    ) -> bool:
        """
        Update issue status.
        
        Args:
            issue_key: Issue key (e.g., "PZ-12345")
            status: New status (e.g., "In Progress", "Done")
        
        Returns:
            True if successful
        
        Example:
            ```python
            agent.update_status("PZ-12345", "In Progress")
            agent.update_status("PZ-12345", "Done")
            ```
        """
        return self.client.transition_issue(issue_key, status)
    
    def update_priority(
        self,
        issue_key: str,
        priority: str
    ) -> Dict[str, Any]:
        """
        Update issue priority.
        
        Args:
            issue_key: Issue key (e.g., "PZ-12345")
            priority: New priority (Lowest, Low, Medium, High, Highest)
        
        Returns:
            Updated issue dict
        """
        return self.client.update_issue(
            issue_key=issue_key,
            priority=priority
        )
    
    def update_assignee(
        self,
        issue_key: str,
        assignee: str
    ) -> Dict[str, Any]:
        """
        Update issue assignee.
        
        Args:
            issue_key: Issue key (e.g., "PZ-12345")
            assignee: Assignee username or account ID
        
        Returns:
            Updated issue dict
        """
        return self.client.update_issue(
            issue_key=issue_key,
            assignee=assignee
        )
    
    def add_labels(
        self,
        issue_key: str,
        labels: List[str]
    ) -> Dict[str, Any]:
        """
        Add labels to issue (replaces existing labels).
        
        Args:
            issue_key: Issue key (e.g., "PZ-12345")
            labels: List of labels to add
        
        Returns:
            Updated issue dict
        """
        # Get current labels
        issue = self.client.get_issue(issue_key)
        current_labels = issue.get('labels', [])
        
        # Merge labels (avoid duplicates)
        new_labels = list(set(current_labels + labels))
        
        return self.client.update_issue(
            issue_key=issue_key,
            labels=new_labels
        )
    
    def add_comment(
        self,
        issue_key: str,
        comment: str
    ) -> Dict[str, Any]:
        """
        Add comment to issue.
        
        Args:
            issue_key: Issue key (e.g., "PZ-12345")
            comment: Comment text
        
        Returns:
            Comment dict
        
        Example:
            ```python
            agent.add_comment("PZ-12345", "This issue is fixed in commit abc123")
            ```
        """
        return self.client.add_comment(issue_key, comment)
    
    # ============================================================================
    # Utility Methods
    # ============================================================================
    
    def format_issue_summary(self, issue: Dict[str, Any]) -> str:
        """
        Format issue as readable string.
        
        Args:
            issue: Issue dict
        
        Returns:
            Formatted string
        """
        return f"""
{issue['key']}: {issue['summary']}
Status: {issue['status']}
Priority: {issue['priority'] or 'N/A'}
Assignee: {issue['assignee'] or 'Unassigned'}
URL: {issue['url']}
        """.strip()
    
    def format_issues_list(self, issues: List[Dict[str, Any]]) -> str:
        """
        Format list of issues as readable string.
        
        Args:
            issues: List of issue dicts
        
        Returns:
            Formatted string
        """
        if not issues:
            return "No issues found."
        
        lines = [f"Found {len(issues)} issue(s):\n"]
        for issue in issues:
            lines.append(self.format_issue_summary(issue))
            lines.append("")
        
        return "\n".join(lines)
    
    def close(self):
        """Close Jira client connection."""
        self.client.close()


# Global agent instance (for easy access)
_agent_instance: Optional[JiraAgent] = None


def get_agent(config_path: Optional[str] = None) -> JiraAgent:
    """
    Get or create global Jira agent instance.
    
    Args:
        config_path: Path to jira_config.yaml (optional)
    
    Returns:
        JiraAgent instance
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = JiraAgent(config_path=config_path)
    return _agent_instance

