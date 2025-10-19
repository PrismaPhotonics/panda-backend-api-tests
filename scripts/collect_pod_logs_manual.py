"""
Manual Pod Logs Collection Script
==================================

Manually collect logs from Kubernetes pods for debugging.

Usage:
    python scripts/collect_pod_logs_manual.py                    # Interactive mode
    python scripts/collect_pod_logs_manual.py --service focus-server --lines 200
    python scripts/collect_pod_logs_manual.py --service focus-server --stream
    python scripts/collect_pod_logs_manual.py --all-services --save
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.pod_logs_collector import PodLogsCollector
from config.config_manager import ConfigManager


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Manually collect logs from Kubernetes pods'
    )
    
    # Service options
    parser.add_argument(
        '--service',
        type=str,
        help='Service name to collect logs from (e.g., focus-server)'
    )
    parser.add_argument(
        '--all-services',
        action='store_true',
        help='Collect logs from all known services'
    )
    
    # Collection options
    parser.add_argument(
        '--lines',
        type=int,
        default=100,
        help='Number of log lines to retrieve (default: 100)'
    )
    parser.add_argument(
        '--stream',
        action='store_true',
        help='Stream logs in real-time (press Ctrl+C to stop)'
    )
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save logs to file'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='reports/logs/manual_collection',
        help='Output directory for saved logs'
    )
    
    # Environment options
    parser.add_argument(
        '--env',
        type=str,
        default='staging',
        help='Environment to use (default: staging)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Load configuration
    try:
        config = ConfigManager(environment=args.env)
        k8s_config = config.get('kubernetes', {})
        
        ssh_host = k8s_config.get('ssh_host')
        ssh_user = k8s_config.get('ssh_user')
        ssh_password = k8s_config.get('ssh_password')
        
        if not all([ssh_host, ssh_user, ssh_password]):
            logger.error("SSH credentials not configured in config/environments.yaml")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Determine services to collect
    services = []
    if args.service:
        services = [args.service]
    elif args.all_services:
        services = [
            'focus-server',
            'rabbitmq-panda',
            'baby-analyzer',
            'data-manager',
            'collector',
        ]
    else:
        # Interactive mode
        logger.info("Available services:")
        logger.info("  1. focus-server")
        logger.info("  2. rabbitmq-panda")
        logger.info("  3. baby-analyzer")
        logger.info("  4. All services")
        
        choice = input("\nSelect service (1-4): ").strip()
        
        if choice == '1':
            services = ['focus-server']
        elif choice == '2':
            services = ['rabbitmq-panda']
        elif choice == '3':
            services = ['baby-analyzer']
        elif choice == '4':
            services = ['focus-server', 'rabbitmq-panda', 'baby-analyzer']
        else:
            logger.error("Invalid choice")
            sys.exit(1)
    
    # Create collector
    logger.info("=" * 80)
    logger.info("MANUAL POD LOGS COLLECTION")
    logger.info("=" * 80)
    logger.info(f"Environment: {args.env}")
    logger.info(f"SSH Host: {ssh_host}")
    logger.info(f"Services: {', '.join(services)}")
    logger.info(f"Lines: {args.lines}")
    if args.stream:
        logger.info("Mode: STREAMING (press Ctrl+C to stop)")
    elif args.save:
        logger.info(f"Mode: SAVE TO {args.output_dir}")
    else:
        logger.info("Mode: DISPLAY")
    logger.info("=" * 80)
    
    try:
        collector = PodLogsCollector(ssh_host, ssh_user, ssh_password)
        collector.connect()
        
        # Collect logs from each service
        for service in services:
            logger.info("")
            logger.info(f"{'='*80}")
            logger.info(f"SERVICE: {service}")
            logger.info(f"{'='*80}")
            
            if args.stream:
                # Stream mode
                logger.info("Starting log stream... (press Ctrl+C to stop)")
                collector.stream_logs_to_logger(
                    pod_name=collector.get_pod_name(service),
                    log_prefix=service,
                    lines=args.lines
                )
                
                # Wait for Ctrl+C
                try:
                    import time
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("\nStopping log stream...")
                    collector.stop_streaming()
                    break
            
            elif args.save:
                # Save mode
                output_dir = Path(args.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                import time
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_file = output_dir / f"{service}_{timestamp}.log"
                
                collector.save_logs_to_file(
                    service_name=service,
                    output_file=str(output_file),
                    lines=args.lines
                )
                
                logger.info(f"✅ Saved to: {output_file}")
            
            else:
                # Display mode
                logs = collector.collect_logs_for_service(
                    service_name=service,
                    lines=args.lines
                )
                
                if logs:
                    print(f"\n{'-'*80}")
                    print(f"Logs from {service}:")
                    print(f"{'-'*80}")
                    print(logs)
                    print(f"{'-'*80}\n")
                else:
                    logger.warning(f"No logs found for {service}")
        
        collector.disconnect()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ COLLECTION COMPLETE")
        logger.info("=" * 80)
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error collecting logs: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

