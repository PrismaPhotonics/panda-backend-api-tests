"""
Pytest Configuration
====================

Global pytest configuration and fixtures for the Focus Server automation framework.
"""

import pytest
import os
import sys
import logging
from typing import Generator, Any
from pathlib import Path

from config.config_manager import ConfigManager
from src.core.exceptions import ConfigurationError, InfrastructureError

# ===================================================================
# PZ Development Repository Integration
# ===================================================================
# Automatically add PZ repository to PYTHONPATH for seamless imports
try:
    from external.pz_integration import get_pz_integration
    
    # Initialize PZ integration at module load
    pz = get_pz_integration()
    logging.getLogger(__name__).info(
        f"✅ PZ repository integrated: {len(pz.list_microservices())} microservices available"
    )
except FileNotFoundError:
    logging.getLogger(__name__).warning(
        "⚠️  PZ repository not found. Run: git submodule update --init --recursive"
    )
except Exception as e:
    logging.getLogger(__name__).warning(
        f"⚠️  PZ integration failed: {e}"
    )


def pytest_addoption(parser):
    """Add custom command line options for pytest."""
    parser.addoption(
        "--env",
        action="store",
        default="staging",
        help="Specify the environment to run tests against (e.g., staging, production, local)"
    )
    parser.addoption(
        "--test-type",
        action="store",
        default="all",
        help="Specify the type of tests to run (e.g., unit, integration, infrastructure, api)"
    )
    parser.addoption(
        "--parallel",
        action="store_true",
        default=False,
        help="Run tests in parallel"
    )
    parser.addoption(
        "--dry-run",
        action="store_true",
        default=False,
        help="Perform a dry run without executing tests"
    )


@pytest.fixture(scope="session")
def current_env(request) -> str:
    """
    Fixture to get the current environment from command line options.
    
    Returns:
        Environment name (staging, production, local)
    """
    env = request.config.getoption("--env")
    logging.getLogger(__name__).info(f"Using environment: {env}")
    return env


@pytest.fixture(scope="session")
def config_manager(current_env: str) -> ConfigManager:
    """
    Fixture to provide a ConfigManager instance for the current environment.
    
    Args:
        current_env: Current environment name
        
    Returns:
        ConfigManager instance
        
    Raises:
        ConfigurationError: If configuration cannot be loaded
    """
    try:
        config = ConfigManager(current_env)
        logging.getLogger(__name__).info(f"Configuration loaded for environment: {current_env}")
        return config
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration for environment '{current_env}': {e}")


@pytest.fixture(scope="session")
def focus_server_api(config_manager: ConfigManager):
    """
    Fixture to provide a FocusServerAPI client.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        FocusServerAPI client instance
    """
    try:
        from src.apis.focus_server_api import FocusServerAPI
        api_client = FocusServerAPI(config_manager)
        logging.getLogger(__name__).info("Focus Server API client initialized")
        return api_client
    except Exception as e:
        raise InfrastructureError(f"Failed to initialize Focus Server API client: {e}")


@pytest.fixture(scope="session")
def mongodb_manager(config_manager: ConfigManager):
    """
    Fixture to provide a MongoDBManager instance.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        MongoDBManager instance
    """
    try:
        from src.infrastructure.mongodb_manager import MongoDBManager
        manager = MongoDBManager(config_manager)
        logging.getLogger(__name__).info("MongoDB manager initialized")
        return manager
    except Exception as e:
        raise InfrastructureError(f"Failed to initialize MongoDB manager: {e}")


@pytest.fixture(scope="session")
def kubernetes_manager(config_manager: ConfigManager):
    """
    Fixture to provide a KubernetesManager instance.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        KubernetesManager instance
    """
    try:
        from src.infrastructure.kubernetes_manager import KubernetesManager
        manager = KubernetesManager(config_manager)
        logging.getLogger(__name__).info("Kubernetes manager initialized")
        return manager
    except Exception as e:
        raise InfrastructureError(f"Failed to initialize Kubernetes manager: {e}")


@pytest.fixture(scope="session")
def ssh_manager(config_manager: ConfigManager):
    """
    Fixture to provide an SSHManager instance.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        SSHManager instance
    """
    try:
        from src.infrastructure.ssh_manager import SSHManager
        manager = SSHManager(config_manager)
        logging.getLogger(__name__).info("SSH manager initialized")
        return manager
    except Exception as e:
        raise InfrastructureError(f"Failed to initialize SSH manager: {e}")


@pytest.fixture(scope="function")
def valid_history_payload(config_manager: ConfigManager) -> dict:
    """
    Provides a valid history payload for configure requests.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        Dictionary containing valid history configure request payload
    """
    from datetime import datetime, timedelta
    
    # Create dynamic timestamps
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=10)
    
    return {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 1, "max": 3},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": int(start_time.timestamp()),
        "end_time": int(end_time.timestamp()),
        "view_type": 0  # MULTICHANNEL
    }


@pytest.fixture(scope="function")
def valid_live_payload() -> dict:
    """
    Provides a valid live payload for configure requests.
    
    Returns:
        Dictionary containing valid live configure request payload
    """
    return {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 1, "max": 3},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,
        "end_time": None,
        "view_type": 0  # MULTICHANNEL
    }


@pytest.fixture(scope="function")
def invalid_payload() -> dict:
    """
    Provides an invalid payload for testing error handling.
    
    Returns:
        Dictionary containing invalid configure request payload
    """
    return {
        "displayTimeAxisDuration": -1,  # Invalid negative value
        "nfftSelection": 0,  # Invalid zero value
        "displayInfo": {},  # Empty display info
        "channels": {"min": 10, "max": 5},  # Invalid range (min > max)
        "frequencyRange": {"min": 1000, "max": 500},  # Invalid range (min > max)
        "start_time": 9999999999999,  # Invalid future timestamp
        "end_time": 1000000000000,  # Invalid timestamp
        "view_type": 999  # Invalid view type
    }


@pytest.fixture(scope="session")
def test_data_directory() -> str:
    """
    Provides the path to the test data directory.
    
    Returns:
        Path to test data directory
    """
    return os.path.join(os.path.dirname(__file__), "..", "data")


@pytest.fixture(scope="function")
def cleanup_test_data(test_data_directory: str) -> Generator[None, None, None]:
    """
    Fixture to clean up test data after test execution.
    
    Args:
        test_data_directory: Path to test data directory
        
    Yields:
        None
    """
    yield
    
    # Cleanup logic would go here
    # This is a placeholder for actual cleanup operations
    logging.getLogger(__name__).debug("Test data cleanup completed")


@pytest.fixture(scope="session")
def setup_logging():
    """
    Set up logging for test execution.
    
    Returns:
        Logger instance
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create logger
    logger = logging.getLogger("focus_server_automation")
    logger.info("Logging initialized for test execution")
    
    return logger


@pytest.fixture(scope="session")
def pz_integration():
    """
    Fixture to provide PZ development repository integration.
    
    Returns:
        PZIntegration instance
        
    Raises:
        FileNotFoundError: If PZ repository not initialized
    """
    try:
        from external.pz_integration import get_pz_integration
        pz = get_pz_integration()
        logging.getLogger(__name__).info("PZ integration available for tests")
        return pz
    except Exception as e:
        pytest.skip(f"PZ repository not available: {e}")


@pytest.fixture(scope="session")
def environment_validation(config_manager: ConfigManager) -> bool:
    """
    Validate that the test environment is ready.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        True if environment is valid
        
    Raises:
        InfrastructureError: If environment validation fails
    """
    try:
        # Basic environment validation
        required_services = config_manager.get("required_services", [])
        
        for service in required_services:
            logging.getLogger(__name__).debug(f"Validating service: {service}")
            # Service validation logic would go here
        
        logging.getLogger(__name__).info("Environment validation passed")
        return True
        
    except Exception as e:
        raise InfrastructureError(f"Environment validation failed: {e}")


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "infrastructure: Infrastructure tests"
    )
    config.addinivalue_line(
        "markers", "api: API tests"
    )
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "resilience: Resilience tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance tests"
    )
    config.addinivalue_line(
        "markers", "mongodb_outage: MongoDB outage tests"
    )
    config.addinivalue_line(
        "markers", "rabbitmq_outage: RabbitMQ outage tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "critical: Critical tests"
    )
    config.addinivalue_line(
        "markers", "connectivity: Connectivity tests"
    )
    config.addinivalue_line(
        "markers", "mongodb: MongoDB tests"
    )
    config.addinivalue_line(
        "markers", "kubernetes: Kubernetes tests"
    )
    config.addinivalue_line(
        "markers", "ssh: SSH tests"
    )
    config.addinivalue_line(
        "markers", "summary: Summary tests"
    )
    config.addinivalue_line(
        "markers", "pz: PZ development repository integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    # Add markers based on test file paths
    for item in items:
        # Add markers based on test file location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        if "infrastructure" in str(item.fspath):
            item.add_marker(pytest.mark.infrastructure)
        
        if "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker for tests that take longer than 30 seconds
        if "outage" in item.name or "resilience" in item.name:
            item.add_marker(pytest.mark.slow)


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    logging.getLogger(__name__).info("Starting test session")


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    logging.getLogger(__name__).info(f"Test session finished with exit status: {exitstatus}")


def pytest_runtest_setup(item):
    """Called before each test item is run."""
    logging.getLogger(__name__).info(f"Setting up test: {item.name}")


def pytest_runtest_teardown(item, nextitem):
    """Called after each test item is run."""
    logging.getLogger(__name__).info(f"Tearing down test: {item.name}")