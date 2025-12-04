#!/usr/bin/env python3
"""
Automation Run Sentinel - Main Entry Point
===========================================

Run the Sentinel service as a standalone application.
"""

import sys
import os
import logging
import signal
import yaml
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.sentinel.main.sentinel_service import SentinelService
from src.sentinel.api.app import SentinelAPI


def setup_logging(level=logging.INFO):
    """Setup logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def load_sentinel_config(config_path: str = None) -> dict:
    """
    Load Sentinel configuration from YAML file.
    
    Supports loading from:
    1. Environment variable SENTINEL_CONFIG_PATH
    2. Kubernetes ConfigMap mount (/app/config/sentinel_config.yaml)
    3. Default location (config/sentinel_config.yaml)
    
    Args:
        config_path: Path to config file (default: auto-detect)
        
    Returns:
        Configuration dictionary
    """
    # Try environment variable first (for Kubernetes)
    if config_path is None:
        config_path = os.getenv("SENTINEL_CONFIG_PATH")
    
    # Try Kubernetes ConfigMap mount location
    if config_path is None:
        k8s_config_path = "/app/config/sentinel_config.yaml"
        if os.path.exists(k8s_config_path):
            config_path = k8s_config_path
    
    # Fall back to default location
    if config_path is None:
        config_path = project_root / "config" / "sentinel_config.yaml"
    
    if not os.path.exists(config_path):
        logging.warning(f"Config file not found: {config_path}, using defaults")
        return {}
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        # Substitute environment variables in config
        config = _substitute_env_vars(config)
        
        return config or {}
    except Exception as e:
        logging.error(f"Error loading config: {e}", exc_info=True)
        return {}


def _substitute_env_vars(obj):
    """
    Recursively substitute environment variables in config values.
    
    Supports ${VAR_NAME} syntax.
    """
    if isinstance(obj, dict):
        return {k: _substitute_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_substitute_env_vars(item) for item in obj]
    elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
        var_name = obj[2:-1]
        return os.getenv(var_name, obj)  # Return original if not found
    else:
        return obj


# Global shutdown handler
_shutdown_requested = False
_sentinel_service = None
_api = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global _shutdown_requested, _sentinel_service, _api
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    _shutdown_requested = True
    
    if _sentinel_service:
        _sentinel_service.stop()


def main():
    """Main entry point."""
    global _sentinel_service, _api
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("=" * 80)
    logger.info("Automation Run Sentinel - Starting")
    logger.info("=" * 80)
    
    # Load configuration
    config = load_sentinel_config()
    
    # Initialize ConfigManager
    env = config.get("environment", "staging")
    config_manager = ConfigManager(env=env)
    
    # Create Sentinel service
    try:
        _sentinel_service = SentinelService(config_manager, config)
        _sentinel_service.start()
        
        logger.info("Sentinel service started successfully")
        
        # Create and start API if enabled
        api_config = config.get("api", {})
        if api_config.get("enabled", True):
            _api = SentinelAPI(_sentinel_service)
            if _api.app:
                logger.info(f"Starting API server on {api_config.get('host', '0.0.0.0')}:{api_config.get('port', 5000)}")
                
                # Run API in a separate thread or as main process
                # For now, we'll run it in the main thread
                try:
                    _api.run(
                        host=api_config.get("host", "0.0.0.0"),
                        port=api_config.get("port", 5000),
                        debug=api_config.get("debug", False),
                        threaded=True  # Run in threaded mode for better shutdown handling
                    )
                except Exception as e:
                    if not _shutdown_requested:
                        raise
                    logger.info("API server stopped due to shutdown request")
            else:
                logger.warning("API not available (Flask not installed)")
                # Keep service running until shutdown signal
                while not _shutdown_requested:
                    signal.pause()  # Wait for interrupt
        else:
            logger.info("API disabled, running in monitoring-only mode")
            # Keep service running until shutdown signal
            while not _shutdown_requested:
                signal.pause()  # Wait for interrupt
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        if not _shutdown_requested:
            logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)
    finally:
        logger.info("Shutting down Sentinel service...")
        if _sentinel_service:
            _sentinel_service.stop()
        logger.info("Sentinel service stopped")


if __name__ == "__main__":
    main()




