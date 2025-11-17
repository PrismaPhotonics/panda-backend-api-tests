"""
MongoDB Monitoring Agent - Example Usage
==========================================

Example script demonstrating how to use the MongoDB Monitoring Agent
for environment monitoring and data retrieval.
"""

import sys
import logging
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.mongodb_monitoring_agent import (
    MongoDBMonitoringAgent,
    AlertLevel
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def alert_callback(alert):
    """Example alert callback function."""
    print(f"\n[ALERT] {alert.level.value.upper()}: {alert.message}")
    if alert.details:
        print(f"  Details: {alert.details}")


def example_basic_usage():
    """Example: Basic usage - connect and retrieve data."""
    print("\n" + "=" * 80)
    print("Example 1: Basic Usage - Connect and Retrieve Data")
    print("=" * 80)
    
    # Initialize agent
    agent = MongoDBMonitoringAgent(
        connection_string="mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma",
        database_name="prisma"
    )
    
    try:
        # Connect
        if agent.connect():
            print("✅ Connected to MongoDB")
            
            # Get health status
            health = agent.get_health_status()
            print(f"\nHealth Status:")
            print(f"  Status: {health['status']}")
            print(f"  Ping Time: {health.get('ping_time_ms', 'N/A')}ms")
            if health.get('server_info'):
                print(f"  Server Version: {health['server_info'].get('version', 'N/A')}")
            
            # List databases
            databases = agent.list_databases()
            print(f"\nDatabases ({len(databases)}):")
            for db in databases[:10]:  # Show first 10
                print(f"  - {db}")
            
            # List collections
            collections = agent.list_collections("prisma")
            print(f"\nCollections in 'prisma' database ({len(collections)}):")
            for collection in collections[:10]:  # Show first 10
                print(f"  - {collection}")
            
            # Get database info
            db_info = agent.get_database_info("prisma")
            print(f"\nDatabase 'prisma' Info:")
            print(f"  Collections: {db_info.get('collections', 0)}")
            print(f"  Data Size: {db_info.get('data_size', 0) / 1024 / 1024:.2f} MB")
            print(f"  Storage Size: {db_info.get('storage_size', 0) / 1024 / 1024:.2f} MB")
            print(f"  Documents: {db_info.get('objects', 0)}")
            
        else:
            print("❌ Failed to connect to MongoDB")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        agent.disconnect()


def example_data_retrieval():
    """Example: Retrieve specific data from collections."""
    print("\n" + "=" * 80)
    print("Example 2: Data Retrieval")
    print("=" * 80)
    
    agent = MongoDBMonitoringAgent(
        connection_string="mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma",
        database_name="prisma"
    )
    
    try:
        if agent.connect():
            # Get collection stats
            collections = agent.list_collections("prisma")
            if collections:
                collection_name = collections[0]
                print(f"\nCollection Stats for '{collection_name}':")
                
                try:
                    stats = agent.get_collection_stats(collection_name, "prisma")
                    print(f"  Documents: {stats.get('count', 0)}")
                    print(f"  Size: {stats.get('size', 0) / 1024:.2f} KB")
                    print(f"  Storage Size: {stats.get('storageSize', 0) / 1024:.2f} KB")
                    print(f"  Indexes: {stats.get('nindexes', 0)}")
                except Exception as e:
                    print(f"  Error getting stats: {e}")
                
                # Count documents
                try:
                    count = agent.count_documents(collection_name, database_name="prisma")
                    print(f"\n  Total Documents: {count}")
                except Exception as e:
                    print(f"  Error counting documents: {e}")
                
                # Find sample documents
                try:
                    documents = agent.find_documents(
                        collection_name,
                        limit=5,
                        database_name="prisma"
                    )
                    print(f"\n  Sample Documents ({len(documents)}):")
                    for i, doc in enumerate(documents[:3], 1):
                        print(f"    Document {i}: {str(doc)[:100]}...")
                except Exception as e:
                    print(f"  Error finding documents: {e}")
                    
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        agent.disconnect()


def example_monitoring():
    """Example: Collect monitoring metrics."""
    print("\n" + "=" * 80)
    print("Example 3: Monitoring Metrics")
    print("=" * 80)
    
    agent = MongoDBMonitoringAgent(
        connection_string="mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma",
        database_name="prisma"
    )
    
    try:
        if agent.connect():
            # Collect metrics
            print("\nCollecting metrics...")
            metrics = agent.collect_metrics()
            
            print(f"\nMonitoring Metrics:")
            print(f"  Timestamp: {metrics.timestamp}")
            print(f"  Connection Status: {'✅ Connected' if metrics.connection_status else '❌ Disconnected'}")
            print(f"  Ping Time: {metrics.ping_time_ms:.2f}ms")
            print(f"  Server Version: {metrics.server_version or 'N/A'}")
            print(f"  Uptime: {metrics.uptime_seconds or 'N/A'} seconds")
            print(f"  Databases: {metrics.databases_count}")
            print(f"  Collections: {metrics.collections_count}")
            print(f"  Total Documents: {metrics.total_documents}")
            print(f"  Active Connections: {metrics.active_connections or 'N/A'}")
            
            if metrics.errors:
                print(f"\n  Errors: {metrics.errors}")
            if metrics.warnings:
                print(f"\n  Warnings: {metrics.warnings}")
            
            # Get metrics summary
            summary = agent.get_metrics_summary(last_n=5)
            print(f"\nMetrics Summary:")
            print(f"  Total Samples: {summary.get('total_samples', 0)}")
            print(f"  Average Ping Time: {summary.get('average_ping_time_ms', 0):.2f}ms")
            print(f"  Connection Success Rate: {summary.get('connection_success_rate', 0) * 100:.1f}%")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        agent.disconnect()


def example_continuous_monitoring():
    """Example: Continuous monitoring with alerts."""
    print("\n" + "=" * 80)
    print("Example 4: Continuous Monitoring")
    print("=" * 80)
    
    agent = MongoDBMonitoringAgent(
        connection_string="mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma",
        database_name="prisma"
    )
    
    # Register alert callback
    agent.register_alert_callback(alert_callback)
    
    try:
        if agent.connect():
            print("Starting continuous monitoring (30 seconds)...")
            
            # Start monitoring (every 10 seconds)
            agent.start_monitoring(interval_seconds=10)
            
            # Let it run for 30 seconds
            time.sleep(30)
            
            # Stop monitoring
            agent.stop_monitoring()
            
            # Get recent alerts
            alerts = agent.get_recent_alerts(limit=10)
            print(f"\nRecent Alerts ({len(alerts)}):")
            for alert in alerts:
                print(f"  [{alert.level.value.upper()}] {alert.message}")
                print(f"    Time: {alert.timestamp}")
            
            # Get metrics summary
            summary = agent.get_metrics_summary()
            print(f"\nFinal Metrics Summary:")
            print(f"  Total Samples: {summary.get('total_samples', 0)}")
            print(f"  Average Ping Time: {summary.get('average_ping_time_ms', 0):.2f}ms")
            
        else:
            print("❌ Failed to connect to MongoDB")
            
    except KeyboardInterrupt:
        print("\n\nMonitoring interrupted by user")
        agent.stop_monitoring()
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        agent.stop_monitoring()
        agent.disconnect()


def example_context_manager():
    """Example: Using context manager."""
    print("\n" + "=" * 80)
    print("Example 5: Context Manager Usage")
    print("=" * 80)
    
    with MongoDBMonitoringAgent(
        connection_string="mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma",
        database_name="prisma"
    ) as agent:
        if agent.client:
            print("✅ Connected via context manager")
            
            # Get health status
            health = agent.get_health_status()
            print(f"Health: {health['status']}")
            
            # List databases
            databases = agent.list_databases()
            print(f"Found {len(databases)} databases")
        else:
            print("❌ Failed to connect")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("MongoDB Monitoring Agent - Usage Examples")
    print("=" * 80)
    
    try:
        # Example 1: Basic usage
        example_basic_usage()
        
        # Example 2: Data retrieval
        example_data_retrieval()
        
        # Example 3: Monitoring
        example_monitoring()
        
        # Example 4: Continuous monitoring (optional - uncomment to run)
        # example_continuous_monitoring()
        
        # Example 5: Context manager
        example_context_manager()
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)


if __name__ == "__main__":
    main()

