"""
Basic functionality tests for the automation framework.

These tests verify that the framework can be imported and basic functionality works.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestBasicImports:
    """Test that basic framework components can be imported."""
    
    def test_import_config_manager(self):
        """Test importing ConfigManager."""
        from config.config_manager import ConfigManager
        
        # Test that ConfigManager can be imported
        assert ConfigManager is not None
        
        # Test that we can create an instance
        config = ConfigManager("staging")
        assert config is not None
        
    def test_import_exceptions(self):
        """Test importing exceptions."""
        from src.core.exceptions import (
            AutomationException,
            ConfigurationError,
            APIError,
            InfrastructureError,
            TestDataError,
            ValidationError
        )
        
        # Test that exceptions can be imported and instantiated
        assert AutomationException("test") is not None
        assert ConfigurationError("test") is not None
        assert APIError("test") is not None
        assert InfrastructureError("test") is not None
        assert TestDataError("test") is not None
        assert ValidationError("test") is not None
        
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


class TestBasicFunctionality:
    """Test basic framework functionality."""
    
    def test_config_loading(self):
        """Test that configuration can be loaded."""
        from config.config_manager import ConfigManager
        
        # Test loading new_production config (default environment)
        config = ConfigManager("new_production")
        
        # Test that we can get configuration values
        base_url = config.get("focus_server.base_url")
        assert base_url is not None
        # Verify it's a valid URL
        assert "http" in base_url
        
        # Test that we can get nested configuration
        mongodb_host = config.get("mongodb.host")
        assert mongodb_host is not None
        # Verify it's a valid IP format (don't hardcode specific IP)
        assert mongodb_host.startswith("10.10.")
        
    def test_model_creation(self):
        """Test that Pydantic models can be created."""
        from src.models.focus_server_models import ConfigureRequest, ConfigureResponse
        
        # Test creating a ConfigureRequest with all required fields
        request = ConfigureRequest(
            displayInfo={
                "height": 1080
            },
            channels={
                "min": 1,
                "max": 100
            },
            view_type=1
        )
        
        assert request.displayInfo.height == 1080
        assert request.channels.min == 1
        assert request.channels.max == 100
        assert request.view_type == 1
        
        # Test creating a ConfigureResponse with all required fields
        response = ConfigureResponse(
            status="success",
            frequencies_list=[1.0, 2.0, 3.0],
            lines_dt=0.1,
            channel_to_stream_index={"1": 0, "2": 1},
            stream_amount=2,
            job_id="test_job_123",
            frequencies_amount=3,
            channel_amount=2,
            stream_port=50051,
            stream_url="localhost:50051",
            view_type=1
        )
        
        assert response.job_id == "test_job_123"
        assert response.status == "success"
        assert response.frequencies_list == [1.0, 2.0, 3.0]
        assert response.stream_port == 50051
        
    def test_exception_handling(self):
        """Test that exceptions work correctly."""
        from src.core.exceptions import ConfigurationError, APIError
        
        # Test ConfigurationError
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Test configuration error")
            
        # Test APIError
        with pytest.raises(APIError):
            raise APIError("Test API error")


class TestProjectStructure:
    """Test that project structure is correct."""
    
    def test_main_directories_exist(self):
        """Test that main directories exist."""
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
        
    def test_config_files_exist(self):
        """Test that configuration files exist."""
        project_root = Path(__file__).parent.parent.parent
        
        # Check config files
        assert (project_root / "config" / "settings.yaml").exists()
        assert (project_root / "config" / "environments.yaml").exists()
        assert (project_root / "config" / "config_manager.py").exists()
        
    def test_source_structure_exists(self):
        """Test that source structure exists."""
        project_root = Path(__file__).parent.parent.parent
        
        # Check source structure
        assert (project_root / "src" / "core").exists()
        assert (project_root / "src" / "apis").exists()
        assert (project_root / "src" / "models").exists()
        assert (project_root / "src" / "infrastructure").exists()
        assert (project_root / "src" / "utils").exists()
        
    def test_python_packages_exist(self):
        """Test that Python packages have __init__.py files."""
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
