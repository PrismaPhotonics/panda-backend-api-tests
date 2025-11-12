"""
MongoDB Monitoring Agent
========================

Professional MongoDB monitoring agent for continuous environment monitoring,
data retrieval, and health checks.

Features:
- Automatic connection management with retry logic
- Data retrieval (databases, collections, documents)
- Health monitoring (connection status, server info, performance metrics)
- Alerting system for monitoring issues
- Comprehensive logging
- Continuous monitoring capabilities
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from threading import Thread, Event
import json

import pymongo
from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    OperationFailure,
    PyMongoError
)

from src.core.exceptions import DatabaseError, InfrastructureError


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MonitoringMetrics:
    """MongoDB monitoring metrics."""
    timestamp: datetime = field(default_factory=datetime.now)
    connection_status: bool = False
    ping_time_ms: float = 0.0
    server_version: Optional[str] = None
    uptime_seconds: Optional[int] = None
    databases_count: int = 0
    collections_count: int = 0
    total_documents: int = 0
    active_connections: Optional[int] = None
    memory_usage_mb: Optional[float] = None
    disk_usage_mb: Optional[float] = None
    operations_per_second: Optional[float] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class Alert:
    """Monitoring alert."""
    level: AlertLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


class MongoDBMonitoringAgent:
    """
    Professional MongoDB monitoring agent.
    
    Provides comprehensive monitoring, data retrieval, and alerting capabilities
    for MongoDB environments.
    
    Example:
        ```python
        agent = MongoDBMonitoringAgent(
            connection_string="mongodb://prisma:prisma@10.10.10.108:27017/?authSource=prisma"  # Staging
            # For production: mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma
        )
        
        # Connect
        if agent.connect():
            # Get health status
            health = agent.get_health_status()
            print(f"Health: {health}")
            
            # Retrieve data
            databases = agent.list_databases()
            collections = agent.list_collections("prisma")
            
            # Start continuous monitoring
            agent.start_monitoring(interval_seconds=60)
        ```
    """
    
    def __init__(
        self,
        connection_string: str,
        database_name: Optional[str] = None,
        connection_timeout_ms: int = 5000,
        server_selection_timeout_ms: int = 5000,
        socket_timeout_ms: int = 5000,
        max_retries: int = 3,
        retry_delay_seconds: float = 2.0,
        enable_auto_reconnect: bool = True,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize MongoDB monitoring agent.
        
        Args:
            connection_string: MongoDB connection string
            database_name: Default database name (optional)
            connection_timeout_ms: Connection timeout in milliseconds
            server_selection_timeout_ms: Server selection timeout in milliseconds
            socket_timeout_ms: Socket timeout in milliseconds
            max_retries: Maximum number of connection retries
            retry_delay_seconds: Delay between retries in seconds
            enable_auto_reconnect: Enable automatic reconnection on failure
            logger: Custom logger instance (optional)
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.connection_timeout_ms = connection_timeout_ms
        self.server_selection_timeout_ms = server_selection_timeout_ms
        self.socket_timeout_ms = socket_timeout_ms
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.enable_auto_reconnect = enable_auto_reconnect
        
        # Logger setup
        self.logger = logger or logging.getLogger(__name__)
        
        # MongoDB client
        self.client: Optional[MongoClient] = None
        self.database: Optional[pymongo.database.Database] = None
        
        # Monitoring state
        self.is_monitoring: bool = False
        self.monitoring_thread: Optional[Thread] = None
        self.monitoring_stop_event: Event = Event()
        self.monitoring_interval_seconds: int = 60
        
        # Metrics and alerts
        self.current_metrics: Optional[MonitoringMetrics] = None
        self.metrics_history: List[MonitoringMetrics] = []
        self.alerts: List[Alert] = []
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        # Connection state
        self.last_connection_attempt: Optional[datetime] = None
        self.last_successful_connection: Optional[datetime] = None
        self.connection_failures: int = 0
        
        self.logger.info("MongoDB Monitoring Agent initialized")
    
    def connect(self, retry: bool = True) -> bool:
        """
        Connect to MongoDB with retry logic.
        
        Args:
            retry: Enable retry on failure
            
        Returns:
            True if connection successful, False otherwise
        """
        self.last_connection_attempt = datetime.now()
        
        for attempt in range(self.max_retries if retry else 1):
            try:
                self.logger.debug(f"Connecting to MongoDB (attempt {attempt + 1}/{self.max_retries if retry else 1})...")
                
                # Create MongoDB client
                self.client = MongoClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=self.server_selection_timeout_ms,
                    connectTimeoutMS=self.connection_timeout_ms,
                    socketTimeoutMS=self.socket_timeout_ms,
                    retryWrites=True,
                    retryReads=True
                )
                
                # Test connection with ping
                start_time = time.time()
                self.client.admin.command('ping')
                ping_time = (time.time() - start_time) * 1000
                
                # Get database if specified
                if self.database_name:
                    self.database = self.client[self.database_name]
                
                # Update connection state
                self.last_successful_connection = datetime.now()
                self.connection_failures = 0
                
                self.logger.info(
                    f"Successfully connected to MongoDB "
                    f"(ping: {ping_time:.2f}ms)"
                )
                
                return True
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                self.connection_failures += 1
                self.logger.warning(
                    f"MongoDB connection failed (attempt {attempt + 1}): {e}"
                )
                
                if retry and attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay_seconds)
                    continue
                else:
                    self._create_alert(
                        AlertLevel.ERROR,
                        f"MongoDB connection failed after {self.max_retries} attempts",
                        {"error": str(e), "attempts": self.max_retries}
                    )
                    return False
                    
            except OperationFailure as e:
                self.logger.error(f"MongoDB authentication failed: {e}")
                self._create_alert(
                    AlertLevel.CRITICAL,
                    "MongoDB authentication failed",
                    {"error": str(e)}
                )
                return False
                
            except Exception as e:
                self.logger.error(f"Unexpected error during MongoDB connection: {e}")
                self._create_alert(
                    AlertLevel.ERROR,
                    "Unexpected MongoDB connection error",
                    {"error": str(e)}
                )
                return False
        
        return False
    
    def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            try:
                self.client.close()
                self.logger.info("Disconnected from MongoDB")
            except Exception as e:
                self.logger.warning(f"Error during disconnect: {e}")
            finally:
                self.client = None
                self.database = None
    
    def _ensure_connected(self):
        """Ensure MongoDB connection is active."""
        if not self.client:
            if not self.connect():
                raise DatabaseError(
                    "MongoDB client not connected",
                    operation="connection_check"
                )
        
        # Test connection
        try:
            self.client.admin.command('ping')
        except Exception as e:
            if self.enable_auto_reconnect:
                self.logger.warning("Connection lost, attempting reconnect...")
                if not self.connect():
                    raise DatabaseError(
                        f"MongoDB connection lost and reconnect failed: {e}",
                        operation="connection_check"
                    )
            else:
                raise DatabaseError(
                    f"MongoDB connection lost: {e}",
                    operation="connection_check"
                )
    
    # ========================================================================
    # DATA RETRIEVAL METHODS
    # ========================================================================
    
    def list_databases(self) -> List[str]:
        """
        List all databases.
        
        Returns:
            List of database names
        """
        self._ensure_connected()
        
        try:
            databases = self.client.list_database_names()
            self.logger.debug(f"Found {len(databases)} databases")
            return databases
        except Exception as e:
            self.logger.error(f"Error listing databases: {e}")
            raise DatabaseError(f"Failed to list databases: {e}", operation="list_databases")
    
    def list_collections(self, database_name: Optional[str] = None) -> List[str]:
        """
        List all collections in a database.
        
        Args:
            database_name: Database name (defaults to configured database)
            
        Returns:
            List of collection names
        """
        self._ensure_connected()
        
        try:
            db_name = database_name or self.database_name
            if not db_name:
                raise DatabaseError("Database name not specified", operation="list_collections")
            
            db = self.client[db_name]
            collections = db.list_collection_names()
            self.logger.debug(f"Found {len(collections)} collections in database '{db_name}'")
            return collections
        except Exception as e:
            self.logger.error(f"Error listing collections: {e}")
            raise DatabaseError(f"Failed to list collections: {e}", operation="list_collections")
    
    def get_collection_stats(self, collection_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Args:
            collection_name: Collection name
            database_name: Database name (defaults to configured database)
            
        Returns:
            Collection statistics dictionary
        """
        self._ensure_connected()
        
        try:
            db_name = database_name or self.database_name
            if not db_name:
                raise DatabaseError("Database name not specified", operation="get_collection_stats")
            
            db = self.client[db_name]
            collection = db[collection_name]
            
            stats = db.command("collStats", collection_name)
            self.logger.debug(f"Retrieved stats for collection '{collection_name}'")
            return stats
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {e}")
            raise DatabaseError(
                f"Failed to get collection stats: {e}",
                operation="get_collection_stats",
                database=db_name
            )
    
    def count_documents(self, collection_name: str, filter: Optional[Dict[str, Any]] = None,
                       database_name: Optional[str] = None) -> int:
        """
        Count documents in a collection.
        
        Args:
            collection_name: Collection name
            filter: Optional filter query
            database_name: Database name (defaults to configured database)
            
        Returns:
            Document count
        """
        self._ensure_connected()
        
        try:
            db_name = database_name or self.database_name
            if not db_name:
                raise DatabaseError("Database name not specified", operation="count_documents")
            
            db = self.client[db_name]
            collection = db[collection_name]
            
            count = collection.count_documents(filter or {})
            self.logger.debug(f"Collection '{collection_name}' has {count} documents")
            return count
        except Exception as e:
            self.logger.error(f"Error counting documents: {e}")
            raise DatabaseError(
                f"Failed to count documents: {e}",
                operation="count_documents",
                database=db_name
            )
    
    def find_documents(
        self,
        collection_name: str,
        filter: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        sort: Optional[List[tuple]] = None,
        database_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find documents in a collection.
        
        Args:
            collection_name: Collection name
            filter: Optional filter query
            projection: Optional projection (fields to include/exclude)
            limit: Optional limit on number of documents
            sort: Optional sort specification [(field, direction), ...]
            database_name: Database name (defaults to configured database)
            
        Returns:
            List of documents
        """
        self._ensure_connected()
        
        try:
            db_name = database_name or self.database_name
            if not db_name:
                raise DatabaseError("Database name not specified", operation="find_documents")
            
            db = self.client[db_name]
            collection = db[collection_name]
            
            query = collection.find(filter or {})
            
            if projection:
                query = query.projection(projection)
            
            if sort:
                query = query.sort(sort)
            
            if limit:
                query = query.limit(limit)
            
            documents = list(query)
            self.logger.debug(f"Retrieved {len(documents)} documents from '{collection_name}'")
            return documents
        except Exception as e:
            self.logger.error(f"Error finding documents: {e}")
            raise DatabaseError(
                f"Failed to find documents: {e}",
                operation="find_documents",
                database=db_name
            )
    
    def get_database_info(self, database_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get database information.
        
        Args:
            database_name: Database name (defaults to configured database)
            
        Returns:
            Database information dictionary
        """
        self._ensure_connected()
        
        try:
            db_name = database_name or self.database_name
            if not db_name:
                raise DatabaseError("Database name not specified", operation="get_database_info")
            
            db = self.client[db_name]
            stats = db.command("dbStats")
            
            info = {
                "database": db_name,
                "collections": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "indexes": stats.get("indexes", 0),
                "index_size": stats.get("indexSize", 0),
                "objects": stats.get("objects", 0)
            }
            
            self.logger.debug(f"Retrieved info for database '{db_name}'")
            return info
        except Exception as e:
            self.logger.error(f"Error getting database info: {e}")
            raise DatabaseError(
                f"Failed to get database info: {e}",
                operation="get_database_info",
                database=db_name
            )
    
    # ========================================================================
    # MONITORING METHODS
    # ========================================================================
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get MongoDB health status.
        
        Returns:
            Health status dictionary
        """
        health = {
            "status": "unknown",
            "connected": False,
            "timestamp": datetime.now().isoformat(),
            "ping_time_ms": None,
            "server_info": None,
            "errors": []
        }
        
        try:
            if not self.client:
                health["status"] = "disconnected"
                health["errors"].append("Client not initialized")
                return health
            
            # Test connection
            start_time = time.time()
            self.client.admin.command('ping')
            ping_time = (time.time() - start_time) * 1000
            
            # Get server info
            server_info = self.client.server_info()
            
            health.update({
                "status": "healthy",
                "connected": True,
                "ping_time_ms": ping_time,
                "server_info": {
                    "version": server_info.get("version"),
                    "gitVersion": server_info.get("gitVersion"),
                    "platform": server_info.get("platform")
                }
            })
            
        except Exception as e:
            health.update({
                "status": "unhealthy",
                "errors": [str(e)]
            })
            self.logger.warning(f"Health check failed: {e}")
        
        return health
    
    def collect_metrics(self) -> MonitoringMetrics:
        """
        Collect comprehensive monitoring metrics.
        
        Returns:
            MonitoringMetrics object
        """
        metrics = MonitoringMetrics()
        
        try:
            self._ensure_connected()
            
            # Connection status and ping
            start_time = time.time()
            self.client.admin.command('ping')
            metrics.ping_time_ms = (time.time() - start_time) * 1000
            metrics.connection_status = True
            
            # Server info
            server_info = self.client.server_info()
            metrics.server_version = server_info.get("version")
            metrics.uptime_seconds = server_info.get("uptime")
            
            # Database and collection counts
            databases = self.list_databases()
            metrics.databases_count = len(databases)
            
            if self.database_name:
                collections = self.list_collections(self.database_name)
                metrics.collections_count = len(collections)
                
                # Count total documents (sample from each collection)
                total_docs = 0
                for collection_name in collections[:10]:  # Limit to first 10 collections for performance
                    try:
                        count = self.count_documents(collection_name, database_name=self.database_name)
                        total_docs += count
                    except Exception as e:
                        metrics.warnings.append(f"Failed to count documents in '{collection_name}': {e}")
                
                metrics.total_documents = total_docs
            
            # Server status (if available)
            try:
                server_status = self.client.admin.command("serverStatus")
                
                # Active connections
                connections = server_status.get("connections", {})
                metrics.active_connections = connections.get("current")
                
                # Memory usage
                memory = server_status.get("mem", {})
                metrics.memory_usage_mb = memory.get("resident") if memory.get("resident") else None
                
                # Operations per second
                opcounters = server_status.get("opcounters", {})
                total_ops = sum([
                    opcounters.get("insert", 0),
                    opcounters.get("query", 0),
                    opcounters.get("update", 0),
                    opcounters.get("delete", 0)
                ])
                # Note: This is cumulative, not per-second. For real ops/sec, need time-based calculation
                metrics.operations_per_second = total_ops
                
            except Exception as e:
                metrics.warnings.append(f"Failed to get server status: {e}")
            
        except Exception as e:
            metrics.connection_status = False
            metrics.errors.append(str(e))
            self.logger.error(f"Error collecting metrics: {e}")
        
        self.current_metrics = metrics
        self.metrics_history.append(metrics)
        
        # Keep only last 1000 metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
    
    def get_metrics_summary(self, last_n: int = 10) -> Dict[str, Any]:
        """
        Get summary of recent metrics.
        
        Args:
            last_n: Number of recent metrics to include
            
        Returns:
            Metrics summary dictionary
        """
        if not self.metrics_history:
            return {"message": "No metrics collected yet"}
        
        recent_metrics = self.metrics_history[-last_n:]
        
        summary = {
            "total_samples": len(self.metrics_history),
            "recent_samples": len(recent_metrics),
            "average_ping_time_ms": sum(m.ping_time_ms for m in recent_metrics) / len(recent_metrics),
            "connection_success_rate": sum(1 for m in recent_metrics if m.connection_status) / len(recent_metrics),
            "latest_metrics": {
                "timestamp": recent_metrics[-1].timestamp.isoformat(),
                "connection_status": recent_metrics[-1].connection_status,
                "ping_time_ms": recent_metrics[-1].ping_time_ms,
                "databases_count": recent_metrics[-1].databases_count,
                "collections_count": recent_metrics[-1].collections_count
            }
        }
        
        return summary
    
    # ========================================================================
    # ALERTING SYSTEM
    # ========================================================================
    
    def _create_alert(self, level: AlertLevel, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Create and process an alert.
        
        Args:
            level: Alert level
            message: Alert message
            details: Optional alert details
        """
        alert = Alert(
            level=level,
            message=message,
            timestamp=datetime.now(),
            details=details or {}
        )
        
        self.alerts.append(alert)
        
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        # Log alert
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }.get(level, logging.INFO)
        
        self.logger.log(log_level, f"[{level.value.upper()}] {message}")
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
    
    def register_alert_callback(self, callback: Callable[[Alert], None]):
        """
        Register a callback function for alerts.
        
        Args:
            callback: Function that receives Alert objects
        """
        self.alert_callbacks.append(callback)
    
    def get_recent_alerts(self, level: Optional[AlertLevel] = None, limit: int = 100) -> List[Alert]:
        """
        Get recent alerts.
        
        Args:
            level: Filter by alert level (optional)
            limit: Maximum number of alerts to return
            
        Returns:
            List of alerts
        """
        alerts = self.alerts[-limit:] if limit else self.alerts
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        return alerts
    
    # ========================================================================
    # CONTINUOUS MONITORING
    # ========================================================================
    
    def start_monitoring(self, interval_seconds: int = 60):
        """
        Start continuous monitoring in background thread.
        
        Args:
            interval_seconds: Monitoring interval in seconds
        """
        if self.is_monitoring:
            self.logger.warning("Monitoring already running")
            return
        
        self.monitoring_interval_seconds = interval_seconds
        self.is_monitoring = True
        self.monitoring_stop_event.clear()
        
        self.monitoring_thread = Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="MongoDBMonitoringThread"
        )
        self.monitoring_thread.start()
        
        self.logger.info(f"Started continuous monitoring (interval: {interval_seconds}s)")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self.monitoring_stop_event.set()
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        
        self.logger.info("Stopped continuous monitoring")
    
    def _monitoring_loop(self):
        """Background monitoring loop."""
        self.logger.info("Monitoring loop started")
        
        while self.is_monitoring and not self.monitoring_stop_event.is_set():
            try:
                # Collect metrics
                metrics = self.collect_metrics()
                
                # Check for issues and create alerts
                if not metrics.connection_status:
                    self._create_alert(
                        AlertLevel.CRITICAL,
                        "MongoDB connection lost",
                        {"timestamp": metrics.timestamp.isoformat()}
                    )
                elif metrics.ping_time_ms > 1000:
                    self._create_alert(
                        AlertLevel.WARNING,
                        f"High MongoDB ping time: {metrics.ping_time_ms:.2f}ms",
                        {"ping_time_ms": metrics.ping_time_ms}
                    )
                
                if metrics.errors:
                    self._create_alert(
                        AlertLevel.ERROR,
                        f"MongoDB monitoring errors: {len(metrics.errors)}",
                        {"errors": metrics.errors}
                    )
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                self._create_alert(
                    AlertLevel.ERROR,
                    "Monitoring loop error",
                    {"error": str(e)}
                )
            
            # Wait for next interval
            self.monitoring_stop_event.wait(self.monitoring_interval_seconds)
        
        self.logger.info("Monitoring loop stopped")
    
    # ========================================================================
    # CONTEXT MANAGER
    # ========================================================================
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_monitoring()
        self.disconnect()
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.stop_monitoring()
            self.disconnect()
        except Exception:
            pass

