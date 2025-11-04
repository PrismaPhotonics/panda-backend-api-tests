"""
Jira Integration Module
=======================

This module provides comprehensive Jira API integration for the Focus Server Automation framework.
It supports creating, reading, updating, and searching Jira issues.

Main Components:
- JiraClient: Main client class for Jira API operations
- IssueBuilder: Helper class for building issue creation payloads
- JiraSearch: Helper class for constructing JQL queries

Usage:
    from external.jira import JiraClient
    
    # Initialize client
    client = JiraClient()
    
    # Create an issue
    issue = client.create_issue(
        summary="Test Issue",
        description="This is a test issue",
        issue_type="Task"
    )
    
    # Search for issues
    issues = client.search_issues("project = PZ AND status != Done")
    
    # Get issue by key
    issue = client.get_issue("PZ-12345")
"""

from external.jira.jira_client import JiraClient
from external.jira.jira_agent import JiraAgent, get_agent

__all__ = ["JiraClient", "JiraAgent", "get_agent"]

__version__ = "1.0.0"

