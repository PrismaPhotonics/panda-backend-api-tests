"""
Unit tests for configuration loading and basic framework functionality.

These tests verify that the automation framework can load configurations
and initialize properly without requiring external dependencies.
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.core.exceptions import ConfigurationError


class TestConfigLoading:
    """Test configuration loading functionality."""
    
    def test_load_new_production_config(self):
        """Test loading new production environment configuration."""
        config_manager = ConfigManager("new_production")
        
        # Test basic configuration loading
        assert config_manager.environment == "new_production"
        assert config_manager.get("focus_server.base_url") == "https://10.10.100.100/focus-server/"
        assert config_manager.get("mongodb.host") == "10.10.100.108"
        assert config_manager.get("mongodb.port") == 27017
        assert config_manager.get("rabbitmq.host") == "10.10.100.107"
        
    def test_load_staging_config(self):
        """Test loading staging environment configuration."""
        config_manager = ConfigManager("staging")
        
        # Test basic configuration loading
        assert config_manager.environment == "staging"
        # Port changed from 8500 to 5000 to match actual K8s service
        assert "5000" in config_manager.get("focus_server.base_url")
        assert config_manager.get("mongodb.host") == "10.10.10.103"
        assert config_manager.get("mongodb.port") == 27017
        assert config_manager.get("rabbitmq.host") == "10.10.10.150"
        
    def test_load_local_config(self):
        """Test loading local environment configuration."""
        # Reset singleton to test local environment
        ConfigManager._instance = None
        ConfigManager._current_env = None
        config_manager = ConfigManager("local")
        
        assert config_manager.environment == "local"
        # Port changed from 8500 to 5000 to match actual K8s service
        assert config_manager.get("focus_server.base_url") == "http://localhost:5000"
        assert config_manager.get("mongodb.host") == "localhost"
        assert config_manager.get("mongodb.port") == 27017
        
    def test_invalid_environment(self):
        """Test handling of invalid environment."""
        # Reset singleton to test invalid environment
        ConfigManager._instance = None
        ConfigManager._current_env = None
        
        with pytest.raises(ConfigurationError):
            ConfigManager("invalid_environment")
            
    def test_get_nested_config(self):
        """Test getting nested configuration values."""
        config_manager = ConfigManager("staging")
        
        # Test nested access
        focus_server_config = config_manager.get("focus_server")
        assert isinstance(focus_server_config, dict)
        # Port changed from 8500 to 5000 to match actual K8s service
        assert "5000" in focus_server_config["base_url"]
        
        # Test port-forward config
        port_forward_config = config_manager.get("focus_server.port_forward")
        assert isinstance(port_forward_config, dict)
        assert port_forward_config["enabled"] is True
        assert port_forward_config["service"] == "focus-server-service"
        
    def test_get_with_default(self):
        """Test getting configuration with default values."""
        config_manager = ConfigManager("staging")
        
        # Test with existing value
        url = config_manager.get("focus_server.base_url", "default_url")
        # Port changed from 8500 to 5000 to match actual K8s service
        assert "5000" in url
        
        # Test with non-existing value
        non_existing = config_manager.get("non_existing.key", "default_value")
        assert non_existing == "default_value"
        
    def test_environment_validation(self):
        """Test environment validation methods."""
        # Test staging environment
        ConfigManager._instance = None
        ConfigManager._current_env = None
        staging_config = ConfigManager("staging")
        assert staging_config.is_staging() is True
        assert staging_config.is_production() is False
        
        # Test local environment
        ConfigManager._instance = None
        ConfigManager._current_env = None
        local_config = ConfigManager("local")
        assert local_config.is_staging() is False
        assert local_config.is_production() is False
        
        # Test production environment
        ConfigManager._instance = None
        ConfigManager._current_env = None
        prod_config = ConfigManager("production")
        assert prod_config.is_staging() is False
        assert prod_config.is_production() is True


class TestFrameworkImports:
    """Test that all framework components can be imported."""
    
    def test_import_core_exceptions(self):
        """Test importing core exceptions."""
        from src.core.exceptions import (
            AutomationException,
            ConfigurationError,
            APIError,
            InfrastructureError,
            TestDataError,
            ValidationError
        )
        
        # Test that exceptions can be instantiated
        assert AutomationException("test") is not None
        assert ConfigurationError("test") is not None
        assert APIError("test") is not None
        assert InfrastructureError("test") is not None
        assert TestDataError("test") is not None
        assert ValidationError("test") is not None
        
    def test_import_api_client(self):
        """Test importing API client base class."""
        from src.core.api_client import BaseAPIClient
        
        # Test that base class can be imported
        assert BaseAPIClient is not None
        
    def test_import_models(self):
        """Test importing Pydantic models."""
        from src.models.focus_server_models import (
            ConfigureRequest,
            ConfigureResponse
        )
        
        # Test that models can be imported
        assert ConfigureRequest is not None
        assert ConfigureResponse is not None
        
    def test_import_infrastructure_managers(self):
        """Test importing infrastructure managers."""
        from src.infrastructure.mongodb_manager import MongoDBManager
        from src.infrastructure.kubernetes_manager import KubernetesManager
        from src.infrastructure.ssh_manager import SSHManager
        
        # Test that managers can be imported
        assert MongoDBManager is not None
        assert KubernetesManager is not None
        assert SSHManager is not None


class TestFrameworkStructure:
    """Test framework structure and organization."""
    
    def test_project_structure(self):
        """Test that project has correct structure."""
        project_root = Path(__file__).parent.parent.parent
        
        # Check main directories exist
        assert (project_root / "config").exists()
        assert (project_root / "src").exists()
        assert (project_root / "tests").exists()
        assert (project_root / "scripts").exists()
        assert (project_root / "reports").exists()
        
        # Check main files exist
        assert (project_root / "requirements.txt").exists()
        assert (project_root / "README.md").exists()
        assert (project_root / "setup.py").exists()
        
        # Check config files
        assert (project_root / "config" / "settings.yaml").exists()
        assert (project_root / "config" / "environments.yaml").exists()
        assert (project_root / "config" / "config_manager.py").exists()
        
        # Check source structure
        assert (project_root / "src" / "core").exists()
        assert (project_root / "src" / "apis").exists()
        assert (project_root / "src" / "models").exists()
        assert (project_root / "src" / "infrastructure").exists()
        assert (project_root / "src" / "utils").exists()
        
        # Check test structure
        assert (project_root / "tests" / "conftest.py").exists()
        assert (project_root / "tests" / "integration").exists()
        assert (project_root / "tests" / "unit").exists()
        
    def test_python_package_structure(self):
        """Test that Python packages are properly structured."""
        project_root = Path(__file__).parent.parent.parent
        
        # Check __init__.py files exist
        init_files = [
            project_root / "src" / "__init__.py",
            project_root / "src" / "core" / "__init__.py",
            project_root / "src" / "apis" / "__init__.py",
            project_root / "src" / "models" / "__init__.py",
            project_root / "src" / "infrastructure" / "__init__.py",
            project_root / "src" / "utils" / "__init__.py",
            project_root / "config" / "__init__.py"
        ]
        
        for init_file in init_files:
            assert init_file.exists(), f"Missing __init__.py: {init_file}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])