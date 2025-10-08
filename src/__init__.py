"""
Focus Server Automation Framework
=================================

Professional test automation framework for Focus Server testing.
"""

__version__ = "1.0.0"
__author__ = "Senior QA Automation Architect"
__email__ = "qa-architect@prisma-photonics.com"

# Core framework imports
from .core import AutomationException
from .models import ConfigureRequest, ConfigureResponse

__all__ = [
    "AutomationException", 
    "ConfigureRequest",
    "ConfigureResponse",
]