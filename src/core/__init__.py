"""
Core Framework Components
=========================

Core components for the Focus Server automation framework.
"""

from .exceptions import (
    AutomationException,
    ConfigurationError,
    APIError,
    InfrastructureError,
    TestDataError,
    ValidationError,
)
from .api_client import BaseAPIClient

__all__ = [
    "AutomationException",
    "ConfigurationError", 
    "APIError",
    "InfrastructureError",
    "TestDataError",
    "ValidationError",
    "BaseAPIClient",
]