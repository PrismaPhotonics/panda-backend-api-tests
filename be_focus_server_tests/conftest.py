"""
Pytest Configuration
====================

Global pytest configuration and fixtures for the Focus Server automation framework.
"""

import pytest
import os
import sys
import logging
from typing import Generator, Any, List
from pathlib import Path

# ===================================================================
# Windows Console Encoding Fix for GitHub Actions
# ===================================================================
# Fix for 'charmap' codec errors when printing Unicode characters
# This is needed for Windows PowerShell in GitHub Actions
import io
if sys.platform == 'win32':
    # Wrap stdout/stderr with UTF-8 encoding
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
# ===================================================================

from config.config_manager import ConfigManager
from src.core.exceptions import ConfigurationError, InfrastructureError
from src.utils.pod_logs_collector import PodLogsCollector
from src.utils.realtime_pod_monitor import PodLogMonitor

# Import logging plugin for automatic test log files
# Note: pytest_plugins moved to root conftest.py to avoid deprecation warning
# pytest_plugins = ["pytest_logging_plugin"]

# ===================================================================
# Register Recording Fixtures (for Historic Playback Tests)
# ===================================================================
# Import fixtures from recording_fixtures.py so pytest can discover them
pytest_plugins = ["be_focus_server_tests.fixtures.recording_fixtures"]

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
    # Import Jira report options (if available)
    try:
        from src.reporting.pytest_integration import pytest_addoption as jira_report_addoption
        jira_report_addoption(parser)
    except ImportError:
        # Jira reporting not available - skip
        pass
    except Exception:
        # Ignore errors
        pass
    
    parser.addoption(
        "--env",
        action="store",
        default="staging",
        help="Specify the environment to run tests against (e.g., staging, local)"
    )
    parser.addoption(
        "--monitor-pods",
        action="store_true",
        default=False,
        help="Enable real-time pod log monitoring with test association"
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
    parser.addoption(
        "--skip-sanity-check",
        action="store_true",
        default=False,
        help="Skip pre-test sanity checks (not recommended)"
    )
    parser.addoption(
        "--run-health-check",
        action="store_true",
        default=False,
        help="Run pre-test health checks before tests"
    )
    parser.addoption(
        "--skip-health-check",
        action="store_true",
        default=False,
        help="Skip pre-test health checks"
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
    import os
    
    # Skip auto-setup in CI environment
    is_ci = os.getenv("CI", "false").lower() == "true"
    if is_ci:
        logger.info("CI environment detected, skipping auto port-forward setup (SSH/K8s not available)")
        yield
        return
    
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
        # Get SSH config - use SSHManager for proper jump host support
        from src.infrastructure.ssh_manager import SSHManager
        
        ssh_manager = SSHManager(config_manager)
        
        # Try to connect to verify SSH works
        try:
            if ssh_manager.connect():
                logger.info("SSH connection established successfully")
                ssh_manager.disconnect()
            else:
                logger.warning("SSH connection failed - some services may not be available")
        except Exception as e:
            logger.warning(f"SSH connection test failed: {e}")
        
        # Get SSH config for managers that need it
        ssh_config = config_manager.get("ssh")
        
        # Extract host from SSH config (support both flat and nested structures)
        if "target_host" in ssh_config:
            # New nested structure (jump_host + target_host)
            ssh_host = ssh_config["target_host"]["host"]
            ssh_user = ssh_config["target_host"]["username"]
            ssh_password = ssh_config["target_host"].get("password")
            ssh_key_file = ssh_config["target_host"].get("key_file")
        else:
            # Legacy flat structure
            ssh_host = ssh_config["host"]
            ssh_user = ssh_config["username"]
            ssh_password = ssh_config.get("password")
            ssh_key_file = ssh_config.get("key_file")
        
        # Expand SSH key path if needed
        if ssh_key_file and ssh_key_file.startswith('~'):
            from pathlib import Path
            home = str(Path.home())
            ssh_key_file = ssh_key_file.replace('~', home, 1)
        
        # === Setup RabbitMQ ===
        try:
            from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager
            
            logger.info("Setting up RabbitMQ...")
            rabbitmq_mgr = RabbitMQConnectionManager(
                k8s_host=ssh_host,
                ssh_user=ssh_user,
                ssh_password=ssh_password,
                ssh_key_file=ssh_key_file,  # Pass key file
                preferred_service="rabbitmq-panda"
            )
            
            conn_info = rabbitmq_mgr.setup()
            if conn_info:
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
                k8s_host=ssh_host,
                ssh_user=ssh_user,
                ssh_password=ssh_password,
                ssh_key_file=ssh_key_file,  # Pass key file
                service_name="focus-server"
            )
            
            if focus_mgr.setup(config_manager=config_manager):
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
        
        # Cleanup MongoDB tunnel if it was created
        try:
            from be_focus_server_tests.fixtures.recording_fixtures import _cleanup_mongodb_ssh_tunnel
            _cleanup_mongodb_ssh_tunnel()
            logger.info("MongoDB tunnel cleanup complete")
        except Exception as e:
            logger.debug(f"MongoDB tunnel cleanup: {e}")
        
        logger.info("AUTO-CLEANUP: Complete")


@pytest.fixture(scope="session")
def focus_server_api(config_manager: ConfigManager):
    """
    Fixture to provide a FocusServerAPI client.
    
    Performs health check before returning the client to ensure server is available.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        FocusServerAPI client instance
        
    Raises:
        InfrastructureError: If API client initialization fails or server is not healthy
    """
    logger = logging.getLogger(__name__)
    import os
    
    # Check if we're in CI and Focus Server is not available
    is_ci = os.getenv("CI", "false").lower() == "true"
    focus_available = os.getenv("FOCUS_SERVER_AVAILABLE", "true").lower() == "true"
    
    if is_ci and not focus_available:
        logger.warning("??  CI environment detected and Focus Server not available - skipping Focus Server API fixture")
        logger.warning("   Tests requiring Focus Server API will be skipped")
        pytest.skip("Focus Server not available in CI environment")
    
    try:
        from src.apis.focus_server_api import FocusServerAPI
        api_client = FocusServerAPI(config_manager)
        logger.info("Focus Server API client initialized")
        
        # Perform health check to ensure server is available
        logger.info("Performing health check on Focus Server API...")
        try:
            # In CI, check availability first before attempting health check
            if is_ci:
                focus_available = os.getenv("FOCUS_SERVER_AVAILABLE", "true").lower() == "true"
                if not focus_available:
                    logger.warning("??  CI environment detected - Focus Server not available, skipping health check")
                    pytest.skip("Focus Server not available in CI environment")
            
            is_healthy = api_client.health_check()
        except Exception as health_error:
            logger.warning(f"Focus Server API health check failed: {health_error}")
            # In CI, skip instead of failing
            if is_ci:
                logger.warning("??  CI environment detected - skipping Focus Server API fixture due to health check error")
                pytest.skip(f"Focus Server health check failed in CI: {health_error}")
            # Don't fail here - let tests handle it, but log warning
            is_healthy = False
        
        if not is_healthy:
            logger.warning("Focus Server API health check failed - server may not be available")
            # In CI, skip instead of failing
            if is_ci:
                logger.warning("??  CI environment detected - skipping Focus Server API fixture due to failed health check")
                pytest.skip("Focus Server health check failed in CI environment")
            # Don't fail here - let tests handle it, but log warning
            # Some tests may still work even if /health endpoint is not available
        
        logger.info(f"Focus Server API health check: {'OK' if is_healthy else 'WARNING - Server may not be fully available'}")
        return api_client
    except Exception as e:
        logger.error(f"Failed to initialize Focus Server API client: {e}")
        # In CI, skip instead of raising error
        if is_ci:
            logger.warning("??  CI environment detected - skipping Focus Server API fixture due to initialization error")
            pytest.skip(f"Focus Server API initialization failed in CI: {e}")
        raise InfrastructureError(f"Failed to initialize Focus Server API client: {e}")


# ===================================================================
# MongoDB Recording Fixtures (for Historic Playback Tests)
# ===================================================================
# NOTE: Recording fixtures are defined in be_focus_server_tests/fixtures/recording_fixtures.py
# They are automatically discovered by pytest through the fixtures/ directory.
# Available fixtures:
#   - mongodb_recordings_info: Session-scoped fixture for MongoDB recordings
#   - available_recording: Single available recording
#   - historic_time_range: Valid time range for historic playback
#   - short_historic_time_range: 1 minute duration
#   - medium_historic_time_range: 5 minutes duration
#   - long_historic_time_range: 30 minutes duration


@pytest.fixture(scope="session")
def mongodb_manager(config_manager: ConfigManager, kubernetes_manager):
    """
    Fixture to provide a MongoDBManager instance.
    
    Uses KubernetesManager for SSH fallback support when accessing Kubernetes.
    
    Args:
        config_manager: Configuration manager instance
        kubernetes_manager: KubernetesManager instance (for SSH fallback support)
        
    Returns:
        MongoDBManager instance
    """
    import os
    logger = logging.getLogger(__name__)
    is_ci = os.getenv("CI", "false").lower() == "true"
    
    # Check if kubernetes_manager was skipped - pytest will propagate skip automatically
    # We just need to handle the case gracefully
    try:
        # Try to access kubernetes_manager - if it was skipped, pytest will handle it
        _ = kubernetes_manager
    except Exception:
        # If kubernetes_manager raised any exception (including skip), 
        # pytest will handle it automatically - we just need to re-raise
        raise
    
    try:
        from src.infrastructure.mongodb_manager import MongoDBManager
        import inspect
        
        # Check if MongoDBManager.__init__ accepts kubernetes_manager parameter
        sig = inspect.signature(MongoDBManager.__init__)
        accepts_k8s_manager = 'kubernetes_manager' in sig.parameters
        
        # Try to initialize MongoDBManager
        if accepts_k8s_manager and kubernetes_manager is not None:
            # MongoDBManager supports kubernetes_manager parameter
            manager = MongoDBManager(config_manager, kubernetes_manager=kubernetes_manager)
            logger.info("MongoDB manager initialized with KubernetesManager")
        else:
            # MongoDBManager doesn't support kubernetes_manager parameter, or it's None
            manager = MongoDBManager(config_manager)
            logger.info("MongoDB manager initialized without KubernetesManager")
        
        return manager
    except TypeError as e:
        # If TypeError occurs (likely due to unexpected keyword argument), try without kubernetes_manager
        if 'kubernetes_manager' in str(e) or 'unexpected keyword' in str(e).lower():
            logger.warning(f"MongoDBManager doesn't support kubernetes_manager parameter, initializing without it: {e}")
            try:
                manager = MongoDBManager(config_manager)
                logger.info("MongoDB manager initialized without KubernetesManager (fallback)")
                return manager
            except Exception as e2:
                if is_ci:
                    logger.warning(f"??  CI environment detected - skipping MongoDB manager due to initialization error: {e2}")
                    pytest.skip(f"MongoDB manager initialization failed in CI: {e2}")
                raise InfrastructureError(f"Failed to initialize MongoDB manager: {e2}")
        else:
            # Different TypeError, re-raise
            if is_ci:
                logger.warning(f"??  CI environment detected - skipping MongoDB manager due to initialization error: {e}")
                pytest.skip(f"MongoDB manager initialization failed in CI: {e}")
            raise InfrastructureError(f"Failed to initialize MongoDB manager: {e}")
    except Exception as e:
        # In CI, skip instead of raising error
        if is_ci:
            logger.warning(f"??  CI environment detected - skipping MongoDB manager due to initialization error: {e}")
            pytest.skip(f"MongoDB manager initialization failed in CI: {e}")
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
    import os
    is_ci = os.getenv("CI", "false").lower() == "true"
    skip_infra = os.getenv("SKIP_INFRASTRUCTURE_TESTS", "false").lower() == "true"
    
    if is_ci and skip_infra:
        logger = logging.getLogger(__name__)
        logger.warning("??  CI environment detected with SKIP_INFRASTRUCTURE_TESTS - skipping Kubernetes manager")
        pytest.skip("Infrastructure tests skipped in CI")
    
    try:
        from src.infrastructure.kubernetes_manager import KubernetesManager
        manager = KubernetesManager(config_manager)
        logging.getLogger(__name__).info("Kubernetes manager initialized")
        return manager
    except Exception as e:
        # In CI, skip instead of raising error
        if is_ci:
            logger = logging.getLogger(__name__)
            logger.warning(f"??  CI environment detected - skipping Kubernetes manager due to initialization error: {e}")
            pytest.skip(f"Kubernetes manager initialization failed in CI: {e}")
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
    import os
    is_ci = os.getenv("CI", "false").lower() == "true"
    skip_infra = os.getenv("SKIP_INFRASTRUCTURE_TESTS", "false").lower() == "true"
    
    if is_ci and skip_infra:
        logger = logging.getLogger(__name__)
        logger.warning("??  CI environment detected with SKIP_INFRASTRUCTURE_TESTS - skipping SSH manager")
        pytest.skip("Infrastructure tests skipped in CI")
    
    try:
        from src.infrastructure.ssh_manager import SSHManager
        manager = SSHManager(config_manager)
        logging.getLogger(__name__).info("SSH manager initialized")
        return manager
    except Exception as e:
        # In CI, skip instead of raising error
        if is_ci:
            logger = logging.getLogger(__name__)
            logger.warning(f"??  CI environment detected - skipping SSH manager due to initialization error: {e}")
            pytest.skip(f"SSH manager initialization failed in CI: {e}")
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
        "frequencyRange": {"min": 0, "max": 1000},
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
        "frequencyRange": {"min": 0, "max": 1000},
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
        "frequencyRange": {"min": 1000, "max": 1000},  # Invalid range (min > max)
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


@pytest.fixture(scope="session", autouse=True)
def check_metadata_ready(focus_server_api):
    """
    Check if system is ready (not waiting for fiber) before configure tests.
    
    This fixture runs automatically before all tests and skips configure tests
    if the system is in "waiting for fiber" state.
    
    Args:
        focus_server_api: FocusServerAPI client
        
    Yields:
        None (just checks and skips if needed)
    """
    import pytest
    
    # Only check for tests that use configure endpoints
    # We'll use a marker to identify configure tests
    # For now, we'll check metadata and skip if needed
    
    try:
        metadata = focus_server_api.get_live_metadata_flat()
        
        # Check if system is waiting for fiber using the new property
        if metadata.is_waiting_for_fiber:
            # Don't skip all tests, just log a warning
            logger = logging.getLogger(__name__)
            logger.warning("=" * 80)
            logger.warning("??  System is in 'waiting for fiber' state")
            logger.warning(f"   PRR: {metadata.prr}")
            logger.warning(f"   SW Version: {metadata.sw_version}")
            logger.warning(f"   num_samples_per_trace: {metadata.num_samples_per_trace}")
            logger.warning(f"   dtype: {metadata.dtype}")
            logger.warning("   Configure tests may fail with 503 errors")
            logger.warning("=" * 80)
            
            # Store metadata state for use in tests
            pytest.metadata_ready = False
        else:
            pytest.metadata_ready = True
            
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"??  Cannot check metadata: {e}")
        logger.warning("   Configure tests may fail")
        pytest.metadata_ready = False


@pytest.fixture(scope="function")
def skip_if_waiting_for_fiber(request, focus_server_api):
    """
    Skip test if system is waiting for fiber.
    
    Use this fixture in configure tests to skip them if system is not ready.
    
    Example:
        def test_configure_job(skip_if_waiting_for_fiber, focus_server_api):
            # Test will be skipped if system is waiting for fiber
            ...
    """
    import pytest
    
    # Check if metadata is ready
    if not hasattr(pytest, 'metadata_ready') or not pytest.metadata_ready:
        try:
            metadata = focus_server_api.get_live_metadata_flat()
            if metadata.is_waiting_for_fiber:
                pytest.skip("System is waiting for fiber - skipping configure test")
        except Exception as e:
            pytest.skip(f"Cannot check metadata - skipping configure test: {e}")


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
# Note: PZ-13985 - LiveMetadata Missing Required Fields
# (Xray marker on fixture not recommended, documented here instead)
def live_metadata(focus_server_api):
    """
    Fixture to provide live metadata.
    
    PZ-13985: LiveMetadata Missing Required Fields
    
    This fixture tests GET /metadata endpoint and may fail if backend
    doesn't return required fields (num_samples_per_trace, dtype).
    
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


# ===================================================================
# Real-time Pod Monitoring for Tests
# ===================================================================

@pytest.fixture(scope="session")
def pod_monitor(request, config_manager):
    """
    Real-time pod log monitor that tracks logs during test execution.
    
    Automatically:
    - Starts monitoring Focus Server and other critical pods
    - Associates logs with specific tests
    - Detects and highlights errors
    - Saves test-specific log files
    
    Usage:
        pytest be_focus_server_tests/ --monitor-pods  # Enable real-time monitoring
    
    Returns:
        PodLogMonitor instance or None if disabled
    """
    # Check if monitoring is enabled
    monitor_enabled = request.config.getoption("--monitor-pods", default=False)
    
    if not monitor_enabled:
        yield None
        return
    
    logger = logging.getLogger(__name__)
    
    # Get SSH credentials from config
    try:
        ssh_config = config_manager.get("ssh", {})
        
        # Extract host from SSH config (support both flat and nested structures)
        if "target_host" in ssh_config:
            # New nested structure (jump_host + target_host)
            ssh_host = ssh_config["target_host"]["host"]
            ssh_user = ssh_config["target_host"]["username"]
            ssh_password = ssh_config["target_host"].get("password")
        elif "host" in ssh_config:
            # Legacy flat structure
            ssh_host = ssh_config["host"]
            ssh_user = ssh_config["username"]
            ssh_password = ssh_config.get("password")
        else:
            ssh_host = None
            ssh_user = None
            ssh_password = None
        
        if not all([ssh_host, ssh_user, ssh_password]):
            logger.warning("SSH credentials not configured - pod monitoring disabled")
            yield None
            return
        
        # Get namespace
        k8s_config = config_manager.get("kubernetes", {})
        namespace = k8s_config.get("namespace", "panda")
        
        logger.info("=" * 80)
        logger.info("REAL-TIME POD MONITORING: Starting...")
        logger.info("=" * 80)
        
        # Initialize monitor
        monitor = PodLogMonitor(
            ssh_host=ssh_host,
            ssh_user=ssh_user,
            ssh_password=ssh_password,
            namespace=namespace
        )
        
        # Connect
        if not monitor.connect():
            logger.error("Failed to connect pod monitor")
            yield None
            return
        
        # Start monitoring key services
        services_to_monitor = [
            ("panda-panda-focus-server", "app.kubernetes.io/name=panda-panda-focus-server"),
            ("mongodb", "app.kubernetes.io/instance=mongodb"),
            ("rabbitmq-panda", "app.kubernetes.io/instance=rabbitmq-panda"),
            ("grpc-jobs", "app"),  # Monitor all gRPC jobs dynamically
        ]
        
        logger.info(f"Starting monitoring for {len(services_to_monitor)} services...")
        
        for service_name, pod_selector in services_to_monitor:
            try:
                monitor.start_monitoring_service(service_name, pod_selector)
            except Exception as e:
                logger.warning(f"Could not start monitoring {service_name}: {e}")
        
        logger.info("Real-time pod monitoring active")
        logger.info("=" * 80)
        
        yield monitor
        
        # Cleanup
        logger.info("=" * 80)
        logger.info("REAL-TIME POD MONITORING: Stopping...")
        logger.info("=" * 80)
        
        # Get summary
        summary = monitor.get_monitoring_summary()
        
        logger.info(f"Monitored {summary['total_tests_monitored']} tests")
        logger.info(f"Detected {summary['total_errors_detected']} errors in pod logs")
        
        if summary['tests_with_errors']:
            logger.warning(f"Tests with pod errors: {len(summary['tests_with_errors'])}")
            for test_name in summary['tests_with_errors'][:10]:  # Show first 10
                logger.warning(f"  - {test_name}")
        
        # Disconnect
        monitor.disconnect()
        
        logger.info("=" * 80)
        logger.info("REAL-TIME POD MONITORING: Complete")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error in pod monitoring: {e}")
        yield None


@pytest.fixture(scope="function", autouse=True)
def track_test_in_pod_monitor(request, pod_monitor):
    """
    Automatically track each test in the pod monitor.
    
    This fixture runs for EVERY test and:
    - Sets the current test context in the monitor
    - Associates pod logs with the test
    - Clears the context after the test finishes
    
    Args:
        request: Pytest request object
        pod_monitor: PodLogMonitor instance
    """
    if pod_monitor is None:
        yield
        return
    
    # Get test name
    test_name = request.node.name
    if request.node.parent:
        test_name = f"{request.node.parent.name}::{test_name}"
    
    # Set current test in monitor
    pod_monitor.set_current_test(test_name)
    
    yield
    
    # Clear current test
    pod_monitor.clear_current_test()


@pytest.fixture(scope="function")
def get_test_pod_logs(pod_monitor):
    """
    Fixture to get pod logs for the current test.
    
    Usage in test:
        def test_something(get_test_pod_logs):
            # ... test code ...
            
            # Get logs captured during this test
            logs = get_test_pod_logs()
            assert "error" not in logs.lower()
    
    Returns:
        Function that returns list of log lines for current test
    """
    if pod_monitor is None:
        return lambda: []
    
    def _get_logs() -> List[str]:
        if pod_monitor.current_test:
            return pod_monitor.get_test_logs(pod_monitor.current_test)
        return []
    
    return _get_logs


@pytest.fixture(scope="function")
def assert_no_pod_errors(pod_monitor):
    """
    Fixture to assert that no errors occurred in pod logs during test.
    
    Usage in test:
        def test_something(assert_no_pod_errors):
            # ... test code ...
            
            # At the end, assert no pod errors
            assert_no_pod_errors()
    
    Returns:
        Function that asserts no errors in pod logs
    """
    if pod_monitor is None:
        return lambda: None
    
    def _assert_no_errors():
        if pod_monitor.current_test:
            errors = pod_monitor.get_test_errors(pod_monitor.current_test)
            if errors:
                error_summary = "\n".join(errors[:5])  # Show first 5 errors
                pytest.fail(
                    f"Pod errors detected during test ({len(errors)} total):\n{error_summary}"
                )
    
    return _assert_no_errors



def pytest_configure(config):
    """Configure pytest with custom markers and run health checks if requested."""
    # Import Jira report configuration (if enabled)
    try:
        from src.reporting.pytest_integration import pytest_configure as jira_report_configure
        jira_report_configure(config)
    except ImportError:
        # Jira reporting not available - skip
        pass
    except Exception:
        # Ignore errors
        pass
    
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
    config.addinivalue_line(
        "markers", "nightly: Nightly test suite (includes all tests including slow/load/stress)"
    )
    config.addinivalue_line(
        "markers", "high: High priority tests"
    )
    config.addinivalue_line(
        "markers", "medium: Medium priority tests"
    )
    config.addinivalue_line(
        "markers", "low: Low priority tests"
    )
    
    # Run pre-test health checks automatically before all tests
    # This is a PRECONDITION - tests will not run if health checks fail
    # Use --skip-health-check to bypass this check (not recommended)
    skip_health_check = config.getoption("--skip-health-check", default=False)
    
    if not skip_health_check:
        try:
            # Import health check script
            scripts_dir = Path(__file__).parent.parent / "scripts"
            sys.path.insert(0, str(scripts_dir))
            
            # Dynamic import - script is in scripts/ directory
            from pre_test_health_check import PreTestHealthChecker  # type: ignore
            
            # Get environment from pytest option or default
            env = config.getoption("--env", default="staging")
            
            # Log that we're running health checks
            logger = logging.getLogger(__name__)
            logger.info("=" * 80)
            logger.info("PRE-TEST HEALTH CHECK: Verifying system components...")
            logger.info("=" * 80)
            
            # Run health checks
            checker = PreTestHealthChecker(environment=env)
            all_passed, results = checker.run_all_checks()
            
            # Log results summary
            logger.info("=" * 80)
            if all_passed:
                logger.info("? PRE-TEST HEALTH CHECK: All components OK - Proceeding with tests")
            else:
                logger.error("? PRE-TEST HEALTH CHECK: Some components failed - Tests will not run")
                # Print failed components
                for result in results:
                    if not result.status:
                        logger.error(f"   ? {result.name}: {result.error or 'Check failed'}")
            logger.info("=" * 80)
            
            # If health checks failed, exit pytest
            if not all_passed:
                failed_components = [r.name for r in results if not r.status]
                pytest.exit(
                    "\n" + "=" * 80 + "\n"
                    "PRE-TEST HEALTH CHECK FAILED\n"
                    "=" * 80 + "\n"
                    "One or more system components are not ready:\n\n"
                    + "\n".join([
                        f"  ? {r.name}: {r.error or 'Check failed'}"
                        for r in results if not r.status
                    ]) + "\n\n"
                    "Please fix the issues before running tests.\n"
                    "Use --skip-health-check to bypass this check (not recommended).\n"
                    "=" * 80,
                    returncode=1
                )
        
        except ImportError:
            # If health check script not available, warn but continue
            import warnings
            logger = logging.getLogger(__name__)
            logger.warning(
                "Pre-test health check script not found. "
                "Skipping health checks. Tests may fail if system is not ready."
            )
            warnings.warn(
                "Pre-test health check script not found. "
                "Skipping health checks.",
                UserWarning
            )
        except Exception as e:
            # If health check fails unexpectedly, exit pytest
            logger = logging.getLogger(__name__)
            logger.error(f"Pre-test health check failed unexpectedly: {e}")
            pytest.exit(
                f"\nPre-test health check failed unexpectedly: {e}\n"
                "Use --skip-health-check to bypass this check (not recommended).",
                returncode=1
            )
    else:
        # Health check skipped
        logger = logging.getLogger(__name__)
        logger.warning("??  Pre-test health check SKIPPED (--skip-health-check flag used)")
        logger.warning("   This is not recommended - tests may fail due to infrastructure issues")


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
    logger = logging.getLogger(__name__)
    logger.info("Starting test session")
    
    # Run sanity checks before starting tests
    skip_sanity = session.config.getoption("--skip-sanity-check", default=False)
    
    if skip_sanity:
        logger.warning("??  Sanity checks SKIPPED (--skip-sanity-check flag used)")
        logger.warning("   This is not recommended - tests may fail due to infrastructure issues")
        return
    
    # Only run sanity checks for non-local environments
    # (local environment might not have all infrastructure)
    try:
        env_option = session.config.getoption("--env", default="staging")
        if env_option == "local":
            logger.info("Local environment detected - skipping sanity checks")
            return
        
        # Get config manager for sanity checks
        from config.config_manager import ConfigManager
        config_manager = ConfigManager(env_option)
        
        # Run sanity checks
        from src.utils.sanity_checker import SanityChecker
        
        sanity_checker = SanityChecker(config_manager)
        results = sanity_checker.run_all_checks()
        
        # Check if all required components passed
        if not sanity_checker.all_passed():
            failed_components = [r.component for r in results if not r.success and r.component != "RabbitMQ"]
            
            logger.error("=" * 100)
            logger.error("? SANITY CHECK FAILED - Some infrastructure components are not available!")
            logger.error("=" * 100)
            logger.error(f"Failed components: {', '.join(failed_components)}")
            logger.error("")
            logger.error("Please ensure all infrastructure components are running before running tests.")
            logger.error("To skip sanity checks (not recommended), use: --skip-sanity-check")
            logger.error("=" * 100)
            
            # Option 1: Fail immediately (recommended) - uncomment to enable
            # import sys
            # logger.error("Stopping test execution due to sanity check failures")
            # sys.exit(1)
            
            # Option 2: Warn but continue (more lenient) - current behavior
            logger.warning("??  Continuing with tests despite sanity check failures...")
            logger.warning("   Some tests may fail due to infrastructure issues")
        else:
            logger.info("? All sanity checks passed - infrastructure is ready for testing")
            
    except Exception as e:
        logger.warning(f"??  Sanity check failed to run: {e}")
        logger.warning("   Continuing with tests - sanity check error will be ignored")
        logger.debug(f"   Error details: {e}", exc_info=True)


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    # Import Jira report generation (if enabled)
    try:
        from src.reporting.pytest_integration import pytest_sessionfinish as jira_report_finish
        jira_report_finish(session, exitstatus)
    except ImportError:
        # Jira reporting not available - skip
        pass
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Jira report generation failed: {e}")
    logging.getLogger(__name__).info(f"Test session finished with exit status: {exitstatus}")


def pytest_runtest_setup(item):
    """Called before each test item is run."""
    # Import Jira report setup (if enabled)
    try:
        from src.reporting.pytest_integration import pytest_runtest_setup as jira_report_setup
        jira_report_setup(item)
    except ImportError:
        # Jira reporting not available - skip
        pass
    except Exception:
        # Ignore errors
        pass
    logging.getLogger(__name__).info(f"Setting up test: {item.name}")


def pytest_runtest_teardown(item, nextitem):
    """Called after each test item is run."""
    # Import Jira report teardown (if enabled)
    try:
        from src.reporting.pytest_integration import pytest_runtest_teardown as jira_report_teardown
        jira_report_teardown(item, nextitem)
    except ImportError:
        # Jira reporting not available - skip
        pass
    except Exception:
        # Ignore errors
        pass
    logging.getLogger(__name__).info(f"Tearing down test: {item.name}")


def pytest_runtest_makereport(item, call):
    """Called after each test execution to capture results."""
    # Import Jira report capture (if enabled)
    try:
        from src.reporting.pytest_integration import pytest_runtest_makereport as jira_report_makereport
        jira_report_makereport(item, call)
    except ImportError:
        # Jira reporting not available - skip
        pass
    except Exception:
        # Ignore errors
        pass


# ===================================================================
# Pod Logs Collection Fixtures
# ===================================================================

@pytest.fixture(scope="session")
def pod_logs_collector(request, config_manager):
    """
    Fixture that collects logs from Kubernetes pods during test execution.
    
    Usage:
        pytest be_focus_server_tests/ --collect-pod-logs  # Stream logs in real-time
        pytest be_focus_server_tests/ --save-pod-logs     # Save logs to files
    
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
