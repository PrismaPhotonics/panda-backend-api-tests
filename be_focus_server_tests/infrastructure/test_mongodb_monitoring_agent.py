"""
Unit Tests for MongoDB Monitoring Agent
========================================

Comprehensive test suite for MongoDBMonitoringAgent class.
"""

import pytest
import time
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch, call
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure

from src.infrastructure.mongodb_monitoring_agent import (
    MongoDBMonitoringAgent,
    AlertLevel,
    MonitoringMetrics,
    Alert
)
from src.core.exceptions import DatabaseError


class TestMongoDBMonitoringAgent:
    """Test suite for MongoDBMonitoringAgent."""
    
    @pytest.fixture
    def connection_string(self, config_manager):
        """MongoDB connection string fixture - uses config from current environment."""
        mongo_config = config_manager.get_database_config()
        return mongo_config.get("connection_string") or \
               f"mongodb://{mongo_config['username']}:{mongo_config['password']}@{mongo_config['host']}:{mongo_config['port']}/?authSource={mongo_config.get('auth_source', 'prisma')}"
    
    @pytest.fixture
    def agent(self, connection_string):
        """MongoDBMonitoringAgent instance fixture."""
        return MongoDBMonitoringAgent(
            connection_string=connection_string,
            database_name="prisma",
            max_retries=2,
            retry_delay_seconds=0.1
        )
    
    @pytest.fixture
    @pytest.mark.xray("PZ-13898")
    def mock_client(self):
        """Mock MongoDB client fixture."""
        client = MagicMock()
        client.admin.command.return_value = {"ok": 1}
        client.list_database_names.return_value = ["prisma", "admin", "config"]
        client.server_info.return_value = {
            "version": "6.0.0",
            "gitVersion": "abc123",
            "platform": "linux",
            "uptime": 3600
        }
        return client
    
    # ========================================================================
    # CONNECTION TESTS
    # ========================================================================
    
    def test_init(self, connection_string):
        """Test agent initialization."""
        agent = MongoDBMonitoringAgent(connection_string=connection_string)
        
        assert agent.connection_string == connection_string
        assert agent.client is None
        assert agent.database is None
        assert agent.is_monitoring is False
        assert len(agent.alerts) == 0
        assert len(agent.metrics_history) == 0
    
    @patch('src.infrastructure.mongodb_monitoring_agent.MongoClient')
    @pytest.mark.xray("PZ-13807")
    def test_connect_success(self, mock_mongo_client, agent, mock_client):
        """Test successful connection."""
        mock_mongo_client.return_value = mock_client
        
        result = agent.connect()
        
        assert result is True
        assert agent.client == mock_client
        assert agent.last_successful_connection is not None
        assert agent.connection_failures == 0
        mock_client.admin.command.assert_called_once_with('ping')
    
    @patch('src.infrastructure.mongodb_monitoring_agent.MongoClient')
    def test_connect_failure_retry(self, mock_mongo_client, agent):
        """Test connection failure with retry."""
        # First attempt fails, second succeeds
        mock_client = MagicMock()
        mock_client.admin.command.side_effect = [
            ConnectionFailure("Connection failed"),
            {"ok": 1}
        ]
        mock_mongo_client.return_value = mock_client
        
        result = agent.connect(retry=True)
        
        assert result is True
        assert agent.connection_failures == 0
        assert mock_client.admin.command.call_count == 2
    
    @patch('src.infrastructure.mongodb_monitoring_agent.MongoClient')
    @pytest.mark.xray("PZ-13807")
    def test_connect_failure_max_retries(self, mock_mongo_client, agent):
        """Test connection failure after max retries."""
        mock_client = MagicMock()
        mock_client.admin.command.side_effect = ConnectionFailure("Connection failed")
        mock_mongo_client.return_value = mock_client
        
        result = agent.connect(retry=True)
        
        assert result is False
        assert agent.connection_failures == agent.max_retries
        assert len(agent.alerts) > 0
        assert agent.alerts[-1].level == AlertLevel.ERROR
    
    @patch('src.infrastructure.mongodb_monitoring_agent.MongoClient')
    @pytest.mark.xray("PZ-13807")
    @pytest.mark.xray("PZ-13807")
    @pytest.mark.xray("PZ-13807")
    def test_connect_authentication_failure(self, mock_mongo_client, agent):
        """Test authentication failure."""
        mock_client = MagicMock()
        mock_client.admin.command.side_effect = OperationFailure("Authentication failed", code=18)
        mock_mongo_client.return_value = mock_client
        
        result = agent.connect()
        
        assert result is False
        assert len(agent.alerts) > 0
        assert agent.alerts[-1].level == AlertLevel.CRITICAL
    
    def test_disconnect(self, agent, mock_client):
        """Test disconnection."""
        agent.client = mock_client
        
        agent.disconnect()
        
        mock_client.close.assert_called_once()
        assert agent.client is None
        assert agent.database is None
    
    def test_ensure_connected_success(self, agent, mock_client):
        """Test ensure_connected when already connected."""
        agent.client = mock_client
        
        agent._ensure_connected()
        
        mock_client.admin.command.assert_called_once_with('ping')
    
    @patch('src.infrastructure.mongodb_monitoring_agent.MongoClient')
    @pytest.mark.xray("PZ-13807")
    @pytest.mark.xray("PZ-13809")
    @pytest.mark.xray("PZ-13807")
    @pytest.mark.xray("PZ-13809")
    @pytest.mark.xray("PZ-13810")
    @pytest.mark.xray("PZ-13810")
    @pytest.mark.xray("PZ-13810")
    @pytest.mark.xray("PZ-13898")
    @pytest.mark.xray("PZ-13898")
    @pytest.mark.xray("PZ-13807")
    def test_ensure_connected_auto_reconnect(self, mock_mongo_client, agent, mock_client):
        """Test ensure_connected with auto-reconnect."""
        agent.client = mock_client
        agent.enable_auto_reconnect = True
        
        # First ping fails, reconnect succeeds
        mock_client.admin.command.side_effect = [
            ConnectionFailure("Connection lost"),
            {"ok": 1}  # Reconnect success
        ]
        mock_mongo_client.return_value = mock_client
        
        agent._ensure_connected()
        
        assert mock_client.admin.command.call_count >= 2
    
    # ========================================================================
    # DATA RETRIEVAL TESTS
    # ========================================================================
    
    def test_list_databases(self, agent, mock_client):
        """Test listing databases."""
        agent.client = mock_client
        
        databases = agent.list_databases()
        
        assert databases == ["prisma", "admin", "config"]
        mock_client.list_database_names.assert_called_once()
    
    def test_list_databases_not_connected(self, agent):
        """Test listing databases when not connected."""
        # Disable auto-reconnect to test error handling
        agent.enable_auto_reconnect = False
        agent.client = None
        
        # Mock connect to fail
        with patch.object(agent, 'connect', return_value=False):
            with pytest.raises(DatabaseError):
                agent.list_databases()
    
    def test_list_collections(self, agent, mock_client):
        """Test listing collections."""
        agent.client = mock_client
        agent.database_name = "prisma"
        
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["collection1", "collection2"]
        mock_client.__getitem__.return_value = mock_db
        
        collections = agent.list_collections("prisma")
        
        assert collections == ["collection1", "collection2"]
        mock_client.__getitem__.assert_called_once_with("prisma")
    
    def test_get_collection_stats(self, agent, mock_client):
        """Test getting collection statistics."""
        agent.client = mock_client
        agent.database_name = "prisma"
        
        mock_db = MagicMock()
        mock_db.command.return_value = {
            "count": 100,
            "size": 1024,
            "storageSize": 2048,
            "nindexes": 2
        }
        mock_client.__getitem__.return_value = mock_db
        
        stats = agent.get_collection_stats("test_collection", "prisma")
        
        assert stats["count"] == 100
        assert stats["size"] == 1024
        mock_db.command.assert_called_once_with("collStats", "test_collection")
    
    def test_count_documents(self, agent, mock_client):
        """Test counting documents."""
        agent.client = mock_client
        agent.database_name = "prisma"
        
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count_documents.return_value = 50
        mock_db.__getitem__.return_value = mock_collection
        mock_client.__getitem__.return_value = mock_db
        
        count = agent.count_documents("test_collection", database_name="prisma")
        
        assert count == 50
        mock_collection.count_documents.assert_called_once_with({})
    
    def test_find_documents(self, agent, mock_client):
        """Test finding documents."""
        agent.client = mock_client
        agent.database_name = "prisma"
        
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        # Create a proper mock cursor that supports iteration and chaining
        mock_documents = [{"_id": 1, "name": "test"}]
        
        class MockCursor:
            """Mock cursor that supports MongoDB query chaining."""
            def __init__(self, docs):
                self.docs = docs
                self._projection = None
                self._sort = None
                self._limit = None
            
            def __iter__(self):
                return iter(self.docs)
            
            def projection(self, proj):
                self._projection = proj
                return self
            
            def sort(self, sort_list):
                self._sort = sort_list
                return self
            
            def limit(self, lim):
                self._limit = lim
                return self
        
        mock_collection.find.return_value = MockCursor(mock_documents)
        mock_db.__getitem__.return_value = mock_collection
        mock_client.__getitem__.return_value = mock_db
        
        documents = agent.find_documents(
            "test_collection",
            filter={"status": "active"},
            limit=10,
            database_name="prisma"
        )
        
        assert len(documents) == 1
        assert documents[0]["name"] == "test"
        mock_collection.find.assert_called_once_with({"status": "active"})
    
    # ========================================================================
    # MONITORING TESTS
    # ========================================================================
    
    def test_get_health_status_healthy(self, agent, mock_client):
        """Test health status when healthy."""
        agent.client = mock_client
        
        health = agent.get_health_status()
        
        assert health["status"] == "healthy"
        assert health["connected"] is True
        assert health["ping_time_ms"] is not None
        assert health["server_info"] is not None
    
    def test_get_health_status_unhealthy(self, agent, mock_client):
        """Test health status when unhealthy."""
        agent.client = mock_client
        mock_client.admin.command.side_effect = ConnectionFailure("Connection failed")
        
        health = agent.get_health_status()
        
        assert health["status"] == "unhealthy"
        assert health["connected"] is False
        assert len(health["errors"]) > 0
    
    @patch('src.infrastructure.mongodb_monitoring_agent.MongoDBMonitoringAgent.list_databases')
    @patch('src.infrastructure.mongodb_monitoring_agent.MongoDBMonitoringAgent.list_collections')
    @patch('src.infrastructure.mongodb_monitoring_agent.MongoDBMonitoringAgent.count_documents')
    @pytest.mark.xray("PZ-13810")
    @pytest.mark.xray("PZ-13810")
    @pytest.mark.xray("PZ-13810")
    @pytest.mark.xray("PZ-13810")
    @pytest.mark.xray("PZ-13810")
    def test_collect_metrics(self, mock_count, mock_list_collections, mock_list_databases, agent, mock_client):
        """Test collecting metrics."""
        agent.client = mock_client
        agent.database_name = "prisma"
        
        mock_list_databases.return_value = ["prisma", "admin"]
        mock_list_collections.return_value = ["collection1", "collection2"]
        mock_count.return_value = 100
        
        # Setup admin.command to handle both ping and serverStatus calls
        call_count = [0]
        def admin_command_side_effect(cmd):
            call_count[0] += 1
            if cmd == 'ping':
                return {"ok": 1}
            elif cmd == "serverStatus":
                return {
                    "connections": {"current": 10},
                    "mem": {"resident": 512},
                    "opcounters": {"insert": 100, "query": 200, "update": 50, "delete": 10}
                }
            return {"ok": 1}
        
        mock_client.admin.command.side_effect = admin_command_side_effect
        
        metrics = agent.collect_metrics()
        
        assert metrics.connection_status is True
        assert metrics.ping_time_ms > 0
        assert metrics.server_version == "6.0.0"
        assert metrics.databases_count == 2
        assert metrics.collections_count == 2
        assert metrics.active_connections == 10
    
    def test_get_metrics_summary(self, agent):
        """Test getting metrics summary."""
        # Add some mock metrics
        for i in range(5):
            metrics = MonitoringMetrics(
                connection_status=True,
                ping_time_ms=10.0 + i,
                databases_count=3,
                collections_count=5
            )
            agent.metrics_history.append(metrics)
        
        summary = agent.get_metrics_summary(last_n=5)
        
        assert summary["total_samples"] == 5
        assert summary["average_ping_time_ms"] == 12.0  # (10+11+12+13+14)/5
        assert summary["connection_success_rate"] == 1.0
    
    # ========================================================================
    # ALERTING TESTS
    # ========================================================================
    
    def test_create_alert(self, agent):
        """Test creating an alert."""
        initial_count = len(agent.alerts)
        
        agent._create_alert(AlertLevel.WARNING, "Test warning", {"key": "value"})
        
        assert len(agent.alerts) == initial_count + 1
        assert agent.alerts[-1].level == AlertLevel.WARNING
        assert agent.alerts[-1].message == "Test warning"
        assert agent.alerts[-1].details == {"key": "value"}
    
    def test_register_alert_callback(self, agent):
        """Test registering alert callback."""
        callback = Mock()
        
        agent.register_alert_callback(callback)
        
        agent._create_alert(AlertLevel.INFO, "Test alert")
        
        callback.assert_called_once()
        assert isinstance(callback.call_args[0][0], Alert)
    
    def test_get_recent_alerts(self, agent):
        """Test getting recent alerts."""
        # Create some alerts
        for level in [AlertLevel.INFO, AlertLevel.WARNING, AlertLevel.ERROR]:
            agent._create_alert(level, f"{level.value} alert")
        
        # Get all alerts
        all_alerts = agent.get_recent_alerts()
        assert len(all_alerts) == 3
        
        # Get filtered alerts
        error_alerts = agent.get_recent_alerts(level=AlertLevel.ERROR)
        assert len(error_alerts) == 1
        assert error_alerts[0].level == AlertLevel.ERROR
    
    # ========================================================================
    # CONTINUOUS MONITORING TESTS
    # ========================================================================
    
    @patch('src.infrastructure.mongodb_monitoring_agent.MongoDBMonitoringAgent.collect_metrics')
    @pytest.mark.xray("PZ-13810")
    def test_start_monitoring(self, mock_collect, agent, mock_client):
        """Test starting continuous monitoring."""
        agent.client = mock_client
        
        agent.start_monitoring(interval_seconds=1)
        
        assert agent.is_monitoring is True
        assert agent.monitoring_thread is not None
        assert agent.monitoring_thread.is_alive()
        
        # Wait a bit for monitoring loop to run
        time.sleep(1.5)
        
        # Stop monitoring
        agent.stop_monitoring()
        
        assert agent.is_monitoring is False
    
    def test_stop_monitoring(self, agent):
        """Test stopping continuous monitoring."""
        agent.is_monitoring = True
        agent.monitoring_stop_event = Mock()
        
        agent.stop_monitoring()
        
        assert agent.is_monitoring is False
        agent.monitoring_stop_event.set.assert_called_once()
    
    # ========================================================================
    # CONTEXT MANAGER TESTS
    # ========================================================================
    
    @patch('src.infrastructure.mongodb_monitoring_agent.MongoClient')
    @pytest.mark.xray("PZ-13807")
    @pytest.mark.xray("PZ-13810")
    @pytest.mark.xray("PZ-13810")
    @pytest.mark.xray("PZ-13810")
    @pytest.mark.xray("PZ-13810")
    @pytest.mark.xray("PZ-13810")
    def test_context_manager(self, mock_mongo_client, connection_string, mock_client):
        """Test context manager usage."""
        mock_mongo_client.return_value = mock_client
        
        with MongoDBMonitoringAgent(connection_string=connection_string) as agent:
            assert agent.client == mock_client
        
        # Should disconnect on exit
        mock_client.close.assert_called_once()


class TestMonitoringMetrics:
    """Test suite for MonitoringMetrics dataclass."""
    
    def test_monitoring_metrics_defaults(self):
        """Test MonitoringMetrics default values."""
        metrics = MonitoringMetrics()
        
        assert metrics.connection_status is False
        assert metrics.ping_time_ms == 0.0
        assert metrics.server_version is None
        assert len(metrics.errors) == 0
        assert len(metrics.warnings) == 0


class TestAlert:
    """Test suite for Alert dataclass."""
    
    def test_alert_creation(self):
        """Test creating an alert."""
        alert = Alert(
            level=AlertLevel.WARNING,
            message="Test alert",
            details={"key": "value"}
        )
        
        assert alert.level == AlertLevel.WARNING
        assert alert.message == "Test alert"
        assert alert.details == {"key": "value"}
        assert isinstance(alert.timestamp, datetime)


class TestAlertLevel:
    """Test suite for AlertLevel enum."""
    
    def test_alert_level_values(self):
        """Test AlertLevel enum values."""
        assert AlertLevel.INFO.value == "info"
        assert AlertLevel.WARNING.value == "warning"
        assert AlertLevel.ERROR.value == "error"
        assert AlertLevel.CRITICAL.value == "critical"

