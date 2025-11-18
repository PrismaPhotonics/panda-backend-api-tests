"""
Root-level pytest configuration
================================

This file must be at the root level to define pytest_plugins.
"""

# Import logging plugin for automatic test log files
pytest_plugins = ["be_focus_server_tests.pytest_logging_plugin"]

