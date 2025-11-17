"""
Jira Exceptions
===============

Custom exceptions for Jira integration.
"""


class JiraException(Exception):
    """Base exception for Jira operations."""
    pass


class JiraConnectionError(JiraException):
    """Raised when connection to Jira fails."""
    pass


class JiraAuthenticationError(JiraException):
    """Raised when authentication fails."""
    pass


class JiraValidationError(JiraException):
    """Raised when validation fails."""
    pass

