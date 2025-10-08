"""
Custom Exceptions
================

Custom exception classes for the Focus Server automation framework.
"""

from typing import Optional


class AutomationException(Exception):
    """
    Base exception for the automation framework.
    
    All framework-specific exceptions should inherit from this class.
    """
    
    def __init__(self, message: str, details: Optional[dict] = None):
        """
        Initialize automation exception.
        
        Args:
            message: Error message
            details: Optional additional details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        """String representation of the exception."""
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(AutomationException):
    """
    Raised when there's an issue with test configuration.
    
    This includes missing configuration files, invalid settings,
    or environment-specific configuration problems.
    """
    pass


class APIError(AutomationException):
    """
    Raised when an API call fails unexpectedly.
    
    This includes HTTP errors, connection timeouts, and
    API-specific error responses.
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 response_body: Optional[str] = None, details: Optional[dict] = None):
        """
        Initialize API error.
        
        Args:
            message: Error message
            status_code: HTTP status code (if applicable)
            response_body: Response body (if applicable)
            details: Optional additional details
        """
        super().__init__(message, details)
        self.status_code = status_code
        self.response_body = response_body


class InfrastructureError(AutomationException):
    """
    Raised when there's an issue with infrastructure components.
    
    This includes Kubernetes operations, MongoDB connections,
    SSH operations, and other infrastructure-related failures.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None, 
                 resource: Optional[str] = None, details: Optional[dict] = None):
        """
        Initialize infrastructure error.
        
        Args:
            message: Error message
            operation: The operation that failed
            resource: The resource involved in the operation
            details: Optional additional details
        """
        super().__init__(message, details)
        self.operation = operation
        self.resource = resource


class TestDataError(AutomationException):
    """
    Raised when there's an issue with test data.
    
    This includes missing test data files, invalid data formats,
    or data validation failures.
    """
    pass


class ValidationError(AutomationException):
    """
    Raised when data validation fails.
    
    This includes API response validation, configuration validation,
    and test result validation failures.
    """
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 expected: Optional[str] = None, actual: Optional[str] = None,
                 details: Optional[dict] = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: The field that failed validation
            expected: Expected value
            actual: Actual value
            details: Optional additional details
        """
        super().__init__(message, details)
        self.field = field
        self.expected = expected
        self.actual = actual


class TimeoutError(AutomationException):
    """
    Raised when an operation times out.
    
    This includes API call timeouts, infrastructure operation timeouts,
    and test execution timeouts.
    """
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None,
                 details: Optional[dict] = None):
        """
        Initialize timeout error.
        
        Args:
            message: Error message
            timeout_seconds: Timeout duration in seconds
            details: Optional additional details
        """
        super().__init__(message, details)
        self.timeout_seconds = timeout_seconds


class DatabaseError(AutomationException):
    """
    Raised when there's a database-related error.
    
    This includes connection failures, query errors, and
    database operation timeouts.
    """
    
    def __init__(self, message: str, database: Optional[str] = None,
                 operation: Optional[str] = None, details: Optional[dict] = None):
        """
        Initialize database error.
        
        Args:
            message: Error message
            database: Database name
            operation: Database operation that failed
            details: Optional additional details
        """
        super().__init__(message, details)
        self.database = database
        self.operation = operation


class NetworkError(AutomationException):
    """
    Raised when there's a network-related error.
    
    This includes connection failures, DNS resolution errors,
    and network timeouts.
    """
    
    def __init__(self, message: str, host: Optional[str] = None,
                 port: Optional[int] = None, details: Optional[dict] = None):
        """
        Initialize network error.
        
        Args:
            message: Error message
            host: Target host
            port: Target port
            details: Optional additional details
        """
        super().__init__(message, details)
        self.host = host
        self.port = port