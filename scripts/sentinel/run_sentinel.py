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
    
    Args:
        config_path: Path to config file (default: config/sentinel_config.yaml)
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = project_root / "config" / "sentinel_config.yaml"
    
    if not os.path.exists(config_path):
        logging.warning(f"Config file not found: {config_path}, using defaults")
        return {}
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config or {}
    except Exception as e:
        logging.error(f"Error loading config: {e}", exc_info=True)
        return {}


def main():
    """Main entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
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
        sentinel_service = SentinelService(config_manager, config)
        sentinel_service.start()
        
        logger.info("Sentinel service started successfully")
        
        # Create and start API if enabled
        api_config = config.get("api", {})
        if api_config.get("enabled", True):
            api = SentinelAPI(sentinel_service)
            if api.app:
                logger.info(f"Starting API server on {api_config.get('host', '0.0.0.0')}:{api_config.get('port', 5000)}")
                
                # Run API in a separate thread or as main process
                # For now, we'll run it in the main thread
                api.run(
                    host=api_config.get("host", "0.0.0.0"),
                    port=api_config.get("port", 5000),
                    debug=api_config.get("debug", False)
                )
            else:
                logger.warning("API not available (Flask not installed)")
                # Keep service running
                try:
                    signal.pause()  # Wait for interrupt
                except KeyboardInterrupt:
                    logger.info("Received interrupt signal")
        else:
            logger.info("API disabled, running in monitoring-only mode")
            # Keep service running
            try:
                signal.pause()  # Wait for interrupt
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Shutting down Sentinel service...")
        if 'sentinel_service' in locals():
            sentinel_service.stop()
        logger.info("Sentinel service stopped")


if __name__ == "__main__":
    main()




