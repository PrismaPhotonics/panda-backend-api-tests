"""
Configuration Manager
=====================

Centralized configuration management for the Focus Server automation framework.
"""

import yaml
import os
from pathlib import Path
from typing import Any, Dict, Optional
from src.core.exceptions import ConfigurationError


class ConfigManager:
    """
    Manages configuration loading and access for the automation framework.
    
    This class provides a centralized way to access configuration values
    from YAML files with support for environment-specific configurations.
    """
    
    _instance = None
    _config_data: Dict[str, Any] = {}
    _current_env: Optional[str] = None
    
    def __new__(cls, env: Optional[str] = None):
        """
        Singleton pattern implementation.
        
        Args:
            env: Environment name (staging, production, etc.)
            
        Returns:
            ConfigManager instance
        """
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_configs()
        
        if env and cls._current_env != env:
            cls._current_env = env
            cls._instance._load_configs()  # Reload if environment changes
        
        return cls._instance
    
    def __init__(self, env: Optional[str] = None):
        """
        Initialize ConfigManager.
        
        Args:
            env: Environment name (staging, production, etc.)
        """
        if not hasattr(self, 'environment'):
            self.environment = env or self._current_env or "staging"
    
    def _load_configs(self):
        """Load configuration from YAML files."""
        try:
            config_dir = Path(__file__).parent
            
            # Load global settings
            settings_path = config_dir / "settings.yaml"
            if not settings_path.exists():
                raise ConfigurationError(f"Settings file not found: {settings_path}")
            
            with open(settings_path, 'r', encoding='utf-8') as f:
                self._config_data = yaml.safe_load(f) or {}
            
            # Load environment-specific configuration
            environments_path = config_dir / "environments.yaml"
            if not environments_path.exists():
                raise ConfigurationError(f"Environments file not found: {environments_path}")
            
            with open(environments_path, 'r', encoding='utf-8') as f:
                env_data = yaml.safe_load(f) or {}
            
            # Set current environment
            if not self._current_env:
                self._current_env = env_data.get("default_environment", "staging")
            
            # Load environment-specific settings
            environments = env_data.get("environments", {})
            if self._current_env not in environments:
                available_envs = list(environments.keys())
                raise ConfigurationError(
                    f"Environment '{self._current_env}' not found in environments.yaml. "
                    f"Available environments: {available_envs}"
                )
            
            # Merge environment-specific settings
            env_config = environments[self._current_env]
            self._config_data.update(env_config)
            
            # Load test configurations
            test_configs = env_data.get("test_configurations", {}).get(self._current_env, {})
            self._config_data["test_configurations"] = test_configs
            
            # Load environment variables
            self._load_environment_variables()
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}") from e
    
    def _load_environment_variables(self):
        """Load configuration from environment variables."""
        # Load environment variables that start with FOCUS_
        for key, value in os.environ.items():
            if key.startswith("FOCUS_"):
                # Convert FOCUS_CONFIG_KEY to config.key
                config_key = key[6:].lower().replace("_", ".")
                self._set_nested_value(config_key, value)
    
    def _set_nested_value(self, key_path: str, value: Any):
        """
        Set a nested configuration value using dot notation.
        
        Args:
            key_path: Dot-separated key path (e.g., 'database.host')
            value: Value to set
        """
        keys = key_path.split('.')
        current = self._config_data
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Examples:
            >>> config.get('database.host')
            >>> config.get('api.timeout', 30)
            >>> config.get('non_existent.key', 'default_value')
        """
        try:
            parts = key.split('.')
            current_value = self._config_data
            
            for part in parts:
                if isinstance(current_value, dict) and part in current_value:
                    current_value = current_value[part]
                else:
                    return default
            
            return current_value
            
        except Exception as e:
            raise ConfigurationError(f"Error accessing configuration key '{key}': {e}")
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.
        
        Args:
            section: Section name (e.g., 'database', 'api')
            
        Returns:
            Dictionary containing the section configuration
        """
        section_config = self.get(section, {})
        if not isinstance(section_config, dict):
            raise ConfigurationError(f"Configuration section '{section}' is not a dictionary")
        
        return section_config
    
    def get_environment_config(self) -> Dict[str, Any]:
        """
        Get configuration for the current environment.
        
        Returns:
            Dictionary containing environment-specific configuration
        """
        return self.get("environments", {}).get(self._current_env, {})
    
    def get_test_config(self, test_type: str) -> Dict[str, Any]:
        """
        Get test configuration for the current environment.
        
        Args:
            test_type: Type of test (e.g., 'mongodb_outage', 'performance')
            
        Returns:
            Dictionary containing test-specific configuration
        """
        test_configs = self.get("test_configurations", {})
        return test_configs.get(test_type, {})
    
    def is_production(self) -> bool:
        """
        Check if current environment is production.
        
        Returns:
            True if current environment is production
        """
        return self.environment == "production"
    
    def is_staging(self) -> bool:
        """
        Check if current environment is staging.
        
        Returns:
            True if current environment is staging
        """
        return self.environment == "staging"
    
    def get_current_environment(self) -> str:
        """
        Get the current environment name.
        
        Returns:
            Current environment name
        """
        return self._current_env or "unknown"
    
    def validate_required_keys(self, required_keys: list):
        """
        Validate that required configuration keys are present.
        
        Args:
            required_keys: List of required configuration keys
            
        Raises:
            ConfigurationError: If any required keys are missing
        """
        missing_keys = []
        
        for key in required_keys:
            if self.get(key) is None:
                missing_keys.append(key)
        
        if missing_keys:
            raise ConfigurationError(
                f"Missing required configuration keys: {missing_keys}"
            )
    
    def get_database_config(self) -> Dict[str, Any]:
        """
        Get database configuration for the current environment.
        
        Returns:
            Database configuration dictionary
        """
        return self.get_section("mongodb")
    
    def get_api_config(self) -> Dict[str, Any]:
        """
        Get API configuration for the current environment.
        
        Returns:
            API configuration dictionary
        """
        return self.get_section("focus_server")
    
    def get_kubernetes_config(self) -> Dict[str, Any]:
        """
        Get Kubernetes configuration for the current environment.
        
        Returns:
            Kubernetes configuration dictionary
        """
        return self.get_section("kubernetes")
    
    def get_ssh_config(self) -> Dict[str, Any]:
        """
        Get SSH configuration for the current environment.
        
        Returns:
            SSH configuration dictionary
        """
        return self.get_section("ssh")
    
    def reload(self):
        """Reload configuration from files."""
        self._config_data.clear()
        self._load_configs()
    
    def __repr__(self) -> str:
        """String representation of the configuration manager."""
        return f"ConfigManager(environment='{self._current_env}')"