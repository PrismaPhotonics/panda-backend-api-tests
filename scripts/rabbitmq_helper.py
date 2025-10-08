"""
RabbitMQ Helper Script
======================

Helper script for testing and debugging RabbitMQ connections.
Provides utilities for connection testing, queue inspection, and message monitoring.

Author: QA Automation Architect
Date: 2025-10-08
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient
from src.models.baby_analyzer_models import ColorMap

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection(env="staging"):
    """
    Test RabbitMQ connection.
    
    Args:
        env: Environment name (default: staging)
    """
    logger.info(f"Testing RabbitMQ connection for environment: {env}")
    
    try:
        # Load config
        config = ConfigManager(env)
        rabbitmq_config = config.get("rabbitmq", {})
        
        logger.info(f"Connecting to: {rabbitmq_config.get('host')}:{rabbitmq_config.get('port')}")
        
        # Create client
        client = BabyAnalyzerMQClient(
            host=rabbitmq_config.get("host", "localhost"),
            port=rabbitmq_config.get("port", 5672),
            username=rabbitmq_config.get("username", "guest"),
            password=rabbitmq_config.get("password", "guest"),
            virtual_host=rabbitmq_config.get("vhost", "/")
        )
        
        # Try to connect
        client.connect()
        logger.info("✅ Connection successful!")
        
        # Get connection info
        info = client.get_connection_info()
        logger.info(f"Connection info: {info}")
        
        # Disconnect
        client.disconnect()
        logger.info("✅ Disconnected successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return False


def send_test_commands(env="staging"):
    """
    Send test commands to RabbitMQ.
    
    Args:
        env: Environment name
    """
    logger.info("Sending test commands to RabbitMQ...")
    
    try:
        config = ConfigManager(env)
        rabbitmq_config = config.get("rabbitmq", {})
        
        with BabyAnalyzerMQClient(
            host=rabbitmq_config.get("host"),
            port=rabbitmq_config.get("port", 5672),
            username=rabbitmq_config.get("username"),
            password=rabbitmq_config.get("password")
        ) as client:
            
            logger.info("Connected!")
            
            # Test 1: Send keepalive
            logger.info("Sending keepalive...")
            client.send_keepalive(source="test_script")
            logger.info("✅ Keepalive sent")
            
            # Test 2: Send colormap change
            logger.info("Sending colormap change...")
            client.send_colormap_change(ColorMap.JET)
            logger.info("✅ Colormap command sent")
            
            # Test 3: Send ROI change
            logger.info("Sending ROI change...")
            client.send_roi_change(start=50, end=150)
            logger.info("✅ ROI command sent")
            
            # Test 4: Send caxis adjustment
            logger.info("Sending caxis adjustment...")
            client.send_caxis_adjust(min_value=-10.0, max_value=10.0)
            logger.info("✅ Caxis command sent")
            
            logger.info("✅ All test commands sent successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to send commands: {e}")
        return False


def inspect_queues_via_management_api(env="staging"):
    """
    Inspect RabbitMQ queues via Management API.
    
    Args:
        env: Environment name
    """
    import requests
    
    logger.info("Inspecting RabbitMQ queues...")
    
    try:
        config = ConfigManager(env)
        rabbitmq_config = config.get("rabbitmq", {})
        
        host = rabbitmq_config.get("host", "localhost")
        mgmt_port = rabbitmq_config.get("management_port", 15672)
        username = rabbitmq_config.get("username", "guest")
        password = rabbitmq_config.get("password", "guest")
        
        base_url = f"http://{host}:{mgmt_port}/api"
        
        # Get overview
        logger.info(f"Fetching overview from {base_url}/overview")
        response = requests.get(f"{base_url}/overview", auth=(username, password))
        response.raise_for_status()
        
        overview = response.json()
        logger.info(f"✅ RabbitMQ Version: {overview.get('rabbitmq_version')}")
        logger.info(f"✅ Management Version: {overview.get('management_version')}")
        
        # Get queues
        logger.info(f"Fetching queues from {base_url}/queues")
        response = requests.get(f"{base_url}/queues", auth=(username, password))
        response.raise_for_status()
        
        queues = response.json()
        logger.info(f"✅ Found {len(queues)} queues:")
        
        for queue in queues:
            name = queue.get('name')
            messages = queue.get('messages', 0)
            consumers = queue.get('consumers', 0)
            logger.info(f"  - {name}: {messages} messages, {consumers} consumers")
        
        # Get exchanges
        logger.info(f"Fetching exchanges from {base_url}/exchanges")
        response = requests.get(f"{base_url}/exchanges", auth=(username, password))
        response.raise_for_status()
        
        exchanges = response.json()
        logger.info(f"✅ Found {len(exchanges)} exchanges")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to inspect queues: {e}")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="RabbitMQ Helper Script")
    parser.add_argument("--env", default="staging", help="Environment name")
    parser.add_argument("--test-connection", action="store_true", help="Test RabbitMQ connection")
    parser.add_argument("--send-commands", action="store_true", help="Send test commands")
    parser.add_argument("--inspect-queues", action="store_true", help="Inspect queues via Management API")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    if args.all:
        logger.info("=" * 60)
        logger.info("Running all RabbitMQ tests...")
        logger.info("=" * 60)
        
        test_connection(args.env)
        print()
        
        send_test_commands(args.env)
        print()
        
        inspect_queues_via_management_api(args.env)
        
    else:
        if args.test_connection:
            test_connection(args.env)
        
        if args.send_commands:
            send_test_commands(args.env)
        
        if args.inspect_queues:
            inspect_queues_via_management_api(args.env)
        
        if not any([args.test_connection, args.send_commands, args.inspect_queues]):
            parser.print_help()


if __name__ == "__main__":
    main()

