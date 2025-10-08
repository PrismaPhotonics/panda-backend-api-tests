"""
Automatic RabbitMQ Setup Script
================================

One-command setup for RabbitMQ connection including:
- Service discovery
- Credential extraction  
- Port-forward setup
- Connection testing

Usage:
    py scripts/setup_rabbitmq_auto.py
    py scripts/setup_rabbitmq_auto.py --service=rabbitmq-prisma
    py scripts/setup_rabbitmq_auto.py --test-commands

Author: QA Automation Architect
Date: 2025-10-08
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager
from config.config_manager import ConfigManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection(conn_info: dict):
    """
    Test RabbitMQ connection.
    
    Args:
        conn_info: Connection information dict
    """
    from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient
    
    logger.info("\n" + "="*70)
    logger.info("Testing RabbitMQ connection...")
    logger.info("="*70)
    
    try:
        client = BabyAnalyzerMQClient(
            host=conn_info['host'],
            port=conn_info['port'],
            username=conn_info['username'],
            password=conn_info['password']
        )
        
        client.connect()
        logger.info("✅ Connection successful!")
        
        info = client.get_connection_info()
        logger.info(f"✅ Connected to: {info}")
        
        client.disconnect()
        logger.info("✅ Disconnected successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False


def test_commands(conn_info: dict):
    """
    Test sending commands to RabbitMQ.
    
    Args:
        conn_info: Connection information dict
    """
    from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient
    from src.models.baby_analyzer_models import ColorMap
    
    logger.info("\n" + "="*70)
    logger.info("Testing RabbitMQ commands...")
    logger.info("="*70)
    
    try:
        with BabyAnalyzerMQClient(
            host=conn_info['host'],
            port=conn_info['port'],
            username=conn_info['username'],
            password=conn_info['password']
        ) as client:
            
            logger.info("\n[1/4] Sending keepalive...")
            client.send_keepalive(source="setup_script")
            logger.info("✅ Keepalive sent")
            
            logger.info("\n[2/4] Sending ROI change...")
            client.send_roi_change(start=100, end=200)
            logger.info("✅ ROI change sent")
            
            logger.info("\n[3/4] Sending colormap change...")
            client.send_colormap_change(ColorMap.JET)
            logger.info("✅ Colormap change sent")
            
            logger.info("\n[4/4] Sending caxis adjustment...")
            client.send_caxis_adjust(min_value=-10.0, max_value=10.0)
            logger.info("✅ Caxis adjustment sent")
            
            logger.info("\n✅ All commands sent successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Command test failed: {e}")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Automatic RabbitMQ Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  py scripts/setup_rabbitmq_auto.py
  py scripts/setup_rabbitmq_auto.py --service=rabbitmq-prisma
  py scripts/setup_rabbitmq_auto.py --test-commands
  py scripts/setup_rabbitmq_auto.py --keep-alive
        """
    )
    parser.add_argument(
        "--env",
        default="staging",
        help="Environment name (default: staging)"
    )
    parser.add_argument(
        "--service",
        default="rabbitmq-panda",
        help="RabbitMQ service name (default: rabbitmq-panda)"
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test connection after setup"
    )
    parser.add_argument(
        "--test-commands",
        action="store_true",
        help="Test sending commands after setup"
    )
    parser.add_argument(
        "--keep-alive",
        action="store_true",
        help="Keep port-forward alive (press Enter to exit)"
    )
    
    args = parser.parse_args()
    
    logger.info("="*70)
    logger.info("🚀 RabbitMQ Automatic Setup")
    logger.info("="*70)
    logger.info(f"Environment: {args.env}")
    logger.info(f"Service: {args.service}")
    logger.info("="*70)
    
    # Load config
    config = ConfigManager(args.env)
    k8s_config = config.get("kubernetes", {})
    ssh_config = config.get("ssh", {})
    
    k8s_host = k8s_config.get("cluster_host", "10.10.10.150")
    namespace = k8s_config.get("namespace", "default")
    ssh_user = ssh_config.get("username", "prisma")
    ssh_password = ssh_config.get("password")
    
    # Create manager with SSH credentials
    manager = RabbitMQConnectionManager(
        k8s_host=k8s_host,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        preferred_service=args.service,
        namespace=namespace
    )
    
    try:
        # Setup
        conn_info = manager.setup()
        
        logger.info("\n" + "="*70)
        logger.info("✅ RabbitMQ Setup Complete!")
        logger.info("="*70)
        logger.info(f"   Host: {conn_info['host']}:{conn_info['port']}")
        logger.info(f"   Username: {conn_info['username']}")
        logger.info(f"   Password: ***")
        logger.info(f"   Management UI: http://{conn_info['host']}:{conn_info['management_port']}")
        logger.info("="*70)
        
        # Test connection
        if args.test_connection or args.test_commands:
            if not test_connection(conn_info):
                logger.error("Connection test failed!")
                return 1
        
        # Test commands
        if args.test_commands:
            if not test_commands(conn_info):
                logger.error("Command test failed!")
                return 1
        
        # Keep alive
        if args.keep_alive:
            logger.info("\n" + "="*70)
            logger.info("Port-forward is running...")
            logger.info("Press Enter to stop and cleanup")
            logger.info("="*70)
            input()
        
        logger.info("\n✅ Setup completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}", exc_info=True)
        return 1
        
    finally:
        logger.info("\nCleaning up...")
        manager.cleanup()
        logger.info("✅ Cleanup done!")


if __name__ == "__main__":
    sys.exit(main())

