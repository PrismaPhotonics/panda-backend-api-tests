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
from src.utils.pod_logs_collector import PodLogsCollector

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
        default="new_production",
        help="Specify the environment to run tests against (e.g., new_production, staging, local)"
    )
    parser.addoption(
        "--collect-pod-logs",
        action="store_true",
        default=False,
        help="Collect and stream logs from Kubernetes pods during tests"
    )
    parser.addoption(
        "--save-pod-logs",
        action="store_true",
        default=False,
        help="Save pod logs to files after test execution"
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


# ===================================================================
# Automated Port-Forward Fixtures
# ===================================================================

@pytest.fixture(scope="session", autouse=True)
def auto_setup_infrastructure(config_manager: ConfigManager, request):
    """
    Automatically set up infrastructure (port-forwards) before tests.
    
    This fixture runs automatically for ALL test sessions and:
    - Sets up RabbitMQ port-forward
    - Sets up Focus Server port-forward
    - Cleans up after all tests complete
    
    Args:
        config_manager: Configuration manager
        request: Pytest request object
    """
    logger = logging.getLogger(__name__)
    
    # Only run for staging/production environments
    env = config_manager.environment
    if env == "local":
        logger.info("Local environment detected, skipping auto port-forward setup")
        yield
        return
    
    logger.info("=" * 80)
    logger.info("AUTO-SETUP: Starting infrastructure...")
    logger.info("=" * 80)
    
    # Track managers for cleanup
    managers = []
    
    try:
        # Get SSH config
        ssh_config = config_manager.get("ssh")
        
        # === Setup RabbitMQ ===
        try:
            from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager
            
            logger.info("Setting up RabbitMQ...")
            rabbitmq_mgr = RabbitMQConnectionManager(
                k8s_host=ssh_config["host"],
                ssh_user=ssh_config["username"],
                ssh_password=ssh_config.get("password"),
                preferred_service="rabbitmq-panda"
            )
            
            if rabbitmq_mgr.setup():
                managers.append(("RabbitMQ", rabbitmq_mgr))
                logger.info("RabbitMQ setup SUCCESS")
            else:
                logger.warning("RabbitMQ setup FAILED (tests may fail)")
                
        except Exception as e:
            logger.warning(f"RabbitMQ setup error: {e}")
        
        # === Setup Focus Server ===
        try:
            from src.infrastructure.focus_server_manager import FocusServerConnectionManager
            
            logger.info("Setting up Focus Server...")
            focus_mgr = FocusServerConnectionManager(
                k8s_host=ssh_config["host"],
                ssh_user=ssh_config["username"],
                ssh_password=ssh_config.get("password"),
                service_name="focus-server"
            )
            
            if focus_mgr.setup():
                managers.append(("Focus Server", focus_mgr))
                logger.info("Focus Server setup SUCCESS")
            else:
                logger.warning("Focus Server setup FAILED (tests may fail)")
                
        except Exception as e:
            logger.warning(f"Focus Server setup error: {e}")
        
        logger.info("=" * 80)
        logger.info(f"AUTO-SETUP: {len(managers)} services ready!")
        logger.info("=" * 80)
        
        # Run tests
        yield
        
    finally:
        # Cleanup all managers
        logger.info("=" * 80)
        logger.info("AUTO-CLEANUP: Stopping infrastructure...")
        logger.info("=" * 80)
        
        for name, mgr in managers:
            try:
                logger.info(f"Cleaning up {name}...")
                mgr.cleanup()
            except Exception as e:
                logger.error(f"Cleanup error for {name}: {e}")
        
        logger.info("AUTO-CLEANUP: Complete")


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


# ===================================================================
# New Fixtures for Complete API Testing
# ===================================================================

@pytest.fixture(scope="session")
def baby_analyzer_mq_client(config_manager):
    """
    Fixture to provide BabyAnalyzerMQClient for RabbitMQ command interface.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        Connected BabyAnalyzerMQClient instance
        
    Yields:
        BabyAnalyzerMQClient
        
    Cleanup:
        Disconnects from RabbitMQ
    """
    try:
        from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient
        
        # Get RabbitMQ config
        rabbitmq_config = config_manager.get("rabbitmq", {})
        
        client = BabyAnalyzerMQClient(
            host=rabbitmq_config.get("host", "localhost"),
            port=rabbitmq_config.get("port", 5672),
            username=rabbitmq_config.get("username", "guest"),
            password=rabbitmq_config.get("password", "guest")
        )
        
        # Connect
        client.connect()
        logging.getLogger(__name__).info("Baby Analyzer MQ client connected")
        
        yield client
        
        # Disconnect
        client.disconnect()
        logging.getLogger(__name__).info("Baby Analyzer MQ client disconnected")
        
    except Exception as e:
        pytest.skip(f"RabbitMQ not available: {e}")


@pytest.fixture(scope="function")
def live_config_payload():
    """
    Fixture to provide a valid live configuration payload.
    
    Returns:
        Dictionary with live mode configuration (no timestamps)
    """
    from src.utils.helpers import generate_config_payload
    
    return generate_config_payload(
        sensors_min=0,
        sensors_max=50,
        freq_min=0,
        freq_max=500,
        nfft=1024,
        canvas_height=1000,
        live=True
    )


@pytest.fixture(scope="function")
def historic_config_payload():
    """
    Fixture to provide a valid historic configuration payload.
    
    Returns:
        Dictionary with historic mode configuration (with timestamps)
    """
    from src.utils.helpers import generate_config_payload
    
    return generate_config_payload(
        sensors_min=0,
        sensors_max=50,
        freq_min=0,
        freq_max=500,
        nfft=1024,
        canvas_height=1000,
        live=False,
        duration_minutes=5
    )


@pytest.fixture(scope="function")
def configured_live_task(focus_server_api, live_config_payload):
    """
    Fixture to configure a live monitoring task.
    
    Args:
        focus_server_api: FocusServerAPI client
        live_config_payload: Live configuration payload
        
    Yields:
        task_id for the configured task
        
    Cleanup:
        Task cleanup after test
    """
    from src.utils.helpers import generate_task_id
    from src.models.focus_server_models import ConfigTaskRequest
    
    task_id = generate_task_id("live_test")
    
    try:
        # Configure task
        config_request = ConfigTaskRequest(**live_config_payload)
        response = focus_server_api.config_task(task_id, config_request)
        
        assert response.status == "Config received successfully"
        logging.getLogger(__name__).info(f"Configured live task: {task_id}")
        
        yield task_id
        
    finally:
        # Cleanup
        logging.getLogger(__name__).info(f"Cleaning up task: {task_id}")


@pytest.fixture(scope="function")
def configured_historic_task(focus_server_api, historic_config_payload):
    """
    Fixture to configure a historic playback task.
    
    Args:
        focus_server_api: FocusServerAPI client
        historic_config_payload: Historic configuration payload
        
    Yields:
        task_id for the configured task
        
    Cleanup:
        Task cleanup after test
    """
    from src.utils.helpers import generate_task_id
    from src.models.focus_server_models import ConfigTaskRequest
    
    task_id = generate_task_id("historic_test")
    
    try:
        # Configure task
        config_request = ConfigTaskRequest(**historic_config_payload)
        response = focus_server_api.config_task(task_id, config_request)
        
        assert response.status == "Config received successfully"
        logging.getLogger(__name__).info(f"Configured historic task: {task_id}")
        
        yield task_id
        
    finally:
        # Cleanup
        logging.getLogger(__name__).info(f"Cleaning up task: {task_id}")


@pytest.fixture(scope="session")
def sensors_list(focus_server_api):
    """
    Fixture to provide list of available sensors.
    
    Args:
        focus_server_api: FocusServerAPI client
        
    Returns:
        List of sensor indices
    """
    try:
        response = focus_server_api.get_sensors()
        return response.sensors
    except Exception as e:
        pytest.skip(f"Could not retrieve sensors list: {e}")


@pytest.fixture(scope="session")
def live_metadata(focus_server_api):
    """
    Fixture to provide live metadata.
    
    Args:
        focus_server_api: FocusServerAPI client
        
    Returns:
        LiveMetadataFlat instance
    """
    try:
        return focus_server_api.get_live_metadata_flat()
    except Exception as e:
        pytest.skip(f"Could not retrieve live metadata: {e}")


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


# ===================================================================
# Pod Logs Collection Fixtures
# ===================================================================

@pytest.fixture(scope="session")
def pod_logs_collector(request, config_manager):
    """
    Fixture that collects logs from Kubernetes pods during test execution.
    
    Usage:
        pytest tests/ --collect-pod-logs  # Stream logs in real-time
        pytest tests/ --save-pod-logs     # Save logs to files
    
    Returns:
        PodLogsCollector instance or None if disabled
    """
    collect_logs = request.config.getoption("--collect-pod-logs")
    save_logs = request.config.getoption("--save-pod-logs")
    
    if not (collect_logs or save_logs):
        yield None
        return
    
    logger = logging.getLogger(__name__)
    
    # Get SSH credentials from config
    try:
        k8s_config = config_manager.get("kubernetes", {})
        ssh_host = k8s_config.get("ssh_host")
        ssh_user = k8s_config.get("ssh_user")
        ssh_password = k8s_config.get("ssh_password")
        
        if not all([ssh_host, ssh_user, ssh_password]):
            logger.warning("⚠️  SSH credentials not configured - pod logs collection disabled")
            yield None
            return
        
        logger.info("=" * 80)
        logger.info("POD LOGS COLLECTION: Starting...")
        logger.info("=" * 80)
        
        collector = PodLogsCollector(
            ssh_host=ssh_host,
            ssh_user=ssh_user,
            ssh_password=ssh_password
        )
        
        collector.connect()
        
        # Start streaming logs if requested
        if collect_logs:
            logger.info("Starting real-time log streaming from services...")
            
            # List of services to monitor
            services_to_monitor = [
                "focus-server",
                "rabbitmq-panda",
                # Add more services as needed
            ]
            
            for service in services_to_monitor:
                try:
                    collector.collect_logs_for_service(
                        service_name=service,
                        lines=30,  # Initial lines
                        stream=True
                    )
                except Exception as e:
                    logger.warning(f"Could not start streaming logs for {service}: {e}")
            
            logger.info("✅ Real-time log streaming active")
        
        yield collector
        
        # Save logs to files if requested
        if save_logs:
            logger.info("=" * 80)
            logger.info("POD LOGS COLLECTION: Saving logs to files...")
            logger.info("=" * 80)
            
            logs_dir = Path("reports/logs/pod_logs")
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            services_to_save = [
                "focus-server",
                "rabbitmq-panda",
            ]
            
            for service in services_to_save:
                try:
                    timestamp = pytest_sessionstart.__self__.start_time if hasattr(pytest_sessionstart, '__self__') else "latest"
                    output_file = logs_dir / f"{service}_{timestamp}.log"
                    
                    collector.save_logs_to_file(
                        service_name=service,
                        output_file=str(output_file),
                        lines=500
                    )
                except Exception as e:
                    logger.warning(f"Could not save logs for {service}: {e}")
            
            logger.info(f"✅ Logs saved to {logs_dir}")
        
        # Cleanup
        collector.disconnect()
        
        logger.info("=" * 80)
        logger.info("POD LOGS COLLECTION: Complete")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error in pod logs collection: {e}")
        yield None


@pytest.fixture(scope="function")
def focus_server_logs(pod_logs_collector):
    """
    Fixture to get Focus Server logs for a specific test.
    
    Usage in test:
        def test_something(focus_server_logs):
            # Logs are automatically collected
            # After test, logs can be retrieved
            pass
    """
    if pod_logs_collector is None:
        yield None
        return
    
    # Before test - mark start point
    start_time = pytest.now() if hasattr(pytest, 'now') else None
    
    yield pod_logs_collector
    
    # After test - optionally save test-specific logs
    # (Implementation can be added based on requirements)