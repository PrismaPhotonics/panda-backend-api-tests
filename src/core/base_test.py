"""
Base Test Class
===============

Base test class that provides common functionality for all test cases.
"""

import pytest
import logging
from typing import Dict, Any, Optional
from config.config_manager import ConfigManager
from .exceptions import ConfigurationError, InfrastructureError


class BaseTest:
    """
    Base class for all automation tests.
    
    Provides common fixtures, setup, and teardown functionality
    for all test classes in the framework.
    """
    
    # Class-level attributes
    config_manager: ConfigManager
    test_data: Dict[str, Any]
    logger: logging.Logger
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, request, current_env):
        """
        Sets up the configuration manager and common resources for the test class.
        
        This fixture runs once per test class and provides:
        - Configuration manager with environment-specific settings
        - Logger instance for the test class
        - Test data loading
        
        Args:
            request: Pytest request object
            current_env: Current environment name
        """
        # Initialize configuration manager
        try:
            self.config_manager = ConfigManager(current_env)
            request.cls.config_manager = self.config_manager
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize configuration manager: {e}")
        
        # Initialize logger
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        request.cls.logger = self.logger
        
        # Log test class initialization
        self.logger.info(f"Initializing test class: {self.__class__.__name__}")
        self.logger.info(f"Environment: {current_env}")
        
        # Load test data if available
        self._load_test_data()
        
        yield
        
        # Cleanup after all tests in the class
        self._cleanup_class()
    
    @pytest.fixture(scope="function", autouse=True)
    def setup_method(self, request):
        """
        Sets up resources for each individual test method.
        
        This fixture runs before each test method and provides:
        - Test method logging
        - Resource validation
        - Test-specific setup
        
        Args:
            request: Pytest request object
        """
        test_name = request.node.name
        self.logger.info(f"Starting test: {test_name}")
        
        # Validate environment before test
        self._validate_environment()
        
        yield
        
        # Cleanup after each test
        self._cleanup_method(test_name)
    
    def _load_test_data(self):
        """
        Load test data for the test class.
        
        This method can be overridden by subclasses to load
        specific test data files or generate test data.
        """
        self.test_data = {}
        self.logger.debug("No test data loaded (using default empty dict)")
    
    def _validate_environment(self):
        """
        Validate that the environment is ready for testing.
        
        This method checks:
        - Required services are available
        - Configuration is valid
        - Infrastructure is accessible
        
        Raises:
            InfrastructureError: If environment validation fails
        """
        try:
            # Basic environment validation
            if not self.config_manager:
                raise InfrastructureError("Configuration manager not initialized")
            
            # Log environment validation
            self.logger.debug("Environment validation passed")
            
        except Exception as e:
            raise InfrastructureError(f"Environment validation failed: {e}")
    
    def _cleanup_class(self):
        """
        Cleanup resources after all tests in the class complete.
        
        This method can be overridden by subclasses to perform
        class-specific cleanup operations.
        """
        self.logger.info(f"Cleaning up test class: {self.__class__.__name__}")
        # Default cleanup - can be extended by subclasses
    
    def _cleanup_method(self, test_name: str):
        """
        Cleanup resources after each test method completes.
        
        This method can be overridden by subclasses to perform
        test-specific cleanup operations.
        
        Args:
            test_name: Name of the test method that just completed
        """
        self.logger.info(f"Cleaning up test: {test_name}")
        # Default cleanup - can be extended by subclasses
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config_manager.get(key, default)
    
    def log_test_step(self, step: str, details: Optional[Dict[str, Any]] = None):
        """
        Log a test step with optional details.
        
        Args:
            step: Description of the test step
            details: Optional additional details
        """
        if details:
            self.logger.info(f"Test Step: {step} | Details: {details}")
        else:
            self.logger.info(f"Test Step: {step}")
    
    def assert_response_time(self, response_time: float, max_time: float = 5.0):
        """
        Assert that response time is within acceptable limits.
        
        Args:
            response_time: Actual response time in seconds
            max_time: Maximum acceptable response time
            
        Raises:
            AssertionError: If response time exceeds maximum
        """
        assert response_time <= max_time, \
            f"Response time {response_time}s exceeds maximum {max_time}s"
        
        self.logger.info(f"Response time validation passed: {response_time}s <= {max_time}s")
    
    def assert_no_side_effects(self, side_effects: Dict[str, Any]):
        """
        Assert that no side effects occurred during the test.
        
        Args:
            side_effects: Dictionary of side effects to check
            
        Raises:
            AssertionError: If unexpected side effects are found
        """
        for effect_type, effect_details in side_effects.items():
            assert not effect_details, \
                f"Unexpected side effect '{effect_type}': {effect_details}"
        
        self.logger.info("No side effects validation passed")
    
    def create_test_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of test results.
        
        Args:
            test_results: Dictionary of test results
            
        Returns:
            Test summary dictionary
        """
        summary = {
            "test_class": self.__class__.__name__,
            "environment": self.get_config("environment.name", "unknown"),
            "timestamp": self._get_timestamp(),
            "results": test_results,
            "status": "PASSED" if all(test_results.values()) else "FAILED"
        }
        
        self.logger.info(f"Test summary created: {summary['status']}")
        return summary
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()


class IntegrationTest(BaseTest):
    """
    Base class for integration tests.
    
    Provides additional functionality specific to integration testing
    including service validation and infrastructure setup.
    """
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_integration_environment(self, request):
        """
        Set up integration test environment.
        
        This includes:
        - Service availability checks
        - Infrastructure validation
        - Test data preparation
        """
        self.logger.info("Setting up integration test environment")
        
        # Validate required services
        self._validate_services()
        
        # Prepare test data
        self._prepare_test_data()
        
        yield
        
        # Cleanup integration environment
        self._cleanup_integration_environment()
    
    def _validate_services(self):
        """
        Validate that required services are available.
        
        Raises:
            InfrastructureError: If required services are not available
        """
        required_services = self.get_config("required_services", [])
        
        for service in required_services:
            self.logger.debug(f"Validating service: {service}")
            # Service validation logic would go here
            # This is a placeholder for actual service checks
    
    def _prepare_test_data(self):
        """
        Prepare test data for integration tests.
        
        This method can be overridden by subclasses to prepare
        specific test data for integration scenarios.
        """
        self.logger.debug("Preparing integration test data")
        # Test data preparation logic would go here
    
    def _cleanup_integration_environment(self):
        """
        Clean up integration test environment.
        
        This includes:
        - Restoring services to initial state
        - Cleaning up test data
        - Releasing resources
        """
        self.logger.info("Cleaning up integration test environment")
        # Integration cleanup logic would go here


class InfrastructureTest(BaseTest):
    """
    Base class for infrastructure tests.
    
    Provides functionality for testing infrastructure components
    including Kubernetes, databases, and message queues.
    """
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_infrastructure(self, request):
        """
        Set up infrastructure test environment.
        
        This includes:
        - Infrastructure component validation
        - Resource allocation
        - Monitoring setup
        """
        self.logger.info("Setting up infrastructure test environment")
        
        # Validate infrastructure components
        self._validate_infrastructure()
        
        yield
        
        # Cleanup infrastructure
        self._cleanup_infrastructure()
    
    def _validate_infrastructure(self):
        """
        Validate infrastructure components.
        
        Raises:
            InfrastructureError: If infrastructure validation fails
        """
        self.logger.debug("Validating infrastructure components")
        # Infrastructure validation logic would go here
    
    def _cleanup_infrastructure(self):
        """
        Clean up infrastructure test environment.
        
        This includes:
        - Restoring infrastructure to initial state
        - Cleaning up resources
        - Stopping monitoring
        """
        self.logger.info("Cleaning up infrastructure test environment")
        # Infrastructure cleanup logic would go here