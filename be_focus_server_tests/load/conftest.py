"""
Pytest Configuration for Quick Load Tests
==========================================

Minimal fixtures for fast load testing.
No cleanup waits, no K8s integration - just pure API performance testing.
"""

import pytest
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", 
        "quick_load: Mark test as quick load test (runs in < 2 min)"
    )


@pytest.fixture(scope="session")
def quick_load_mode() -> bool:
    """Check if running in quick load mode."""
    return os.getenv("QUICK_LOAD_MODE", "false").lower() == "true"


@pytest.fixture(scope="session") 
def load_test_config() -> Dict[str, Any]:
    """
    Load test configuration from environment.
    
    Environment Variables:
        LOAD_TEST_CONCURRENT_REQUESTS: Number of concurrent requests (default: 50)
        LOAD_TEST_DURATION_SECONDS: Test duration in seconds (default: 60)
        QUICK_LOAD_MODE: Enable quick mode with reduced timeouts (default: false)
    """
    return {
        "concurrent_requests": int(os.getenv("LOAD_TEST_CONCURRENT_REQUESTS", "50")),
        "duration_seconds": int(os.getenv("LOAD_TEST_DURATION_SECONDS", "60")),
        "quick_mode": os.getenv("QUICK_LOAD_MODE", "false").lower() == "true",
        "request_timeout": 10,  # 10 seconds max per request
        "warmup_requests": 5,
    }


@pytest.fixture(scope="function", autouse=False)
def skip_cleanup():
    """
    Fixture to skip cleanup for quick load tests.
    
    Quick load tests don't create jobs, so no cleanup is needed.
    This is a no-op fixture that can be used to explicitly mark
    tests that should skip the auto cleanup.
    """
    yield
    # No cleanup needed for quick load tests
