"""
Recording Fixtures - MongoDB Recording Data Provider
=====================================================

Provides fixtures and utilities for querying available recordings from MongoDB
before running Historic playback tests.

IMPORTANT (per Yonatan's feedback):
- DO NOT manually insert data into MongoDB
- ONLY query existing recordings and use their timestamps
- If no recordings exist, skip the test

MongoDB Structure:
1. base_paths collection contains the guid
2. Collection named by guid contains recordings with:
   - start_time: datetime
   - end_time: datetime
   - deleted: boolean
   - uuid, fiber_metadata, etc.

Author: QA Automation Architect
Date: 2025-12-01
"""

import pytest
import logging
import time
import pymongo
import threading
import socket
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

# Thread-safe lock for MongoDB tunnel operations
_mongodb_tunnel_lock = threading.Lock()

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

logger = logging.getLogger(__name__)

# Global variable to track MongoDB port-forward
_mongodb_port_forward_client: Optional[paramiko.SSHClient] = None
_mongodb_port_forward_ssh_manager: Optional[Any] = None  # SSHManager instance
_mongodb_port_forward_thread: Optional[threading.Thread] = None
_mongodb_port_forward_active = False


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class Recording:
    """Represents an available recording from MongoDB."""
    start_time_ms: int  # epoch milliseconds
    end_time_ms: int    # epoch milliseconds
    
    @property
    def start_time(self) -> int:
        """Start time in seconds (for API compatibility)."""
        return self.start_time_ms // 1000
    
    @property
    def end_time(self) -> int:
        """End time in seconds (for API compatibility)."""
        return self.end_time_ms // 1000
    
    @property
    def duration_seconds(self) -> float:
        """Recording duration in seconds."""
        return (self.end_time_ms - self.start_time_ms) / 1000
    
    @property
    def start_datetime(self) -> datetime:
        """Start time as datetime object."""
        return datetime.fromtimestamp(self.start_time)
    
    @property
    def end_datetime(self) -> datetime:
        """End time as datetime object."""
        return datetime.fromtimestamp(self.end_time)
    
    def get_time_range(self, duration_seconds: int = 60) -> Tuple[int, int]:
        """
        Get a time range from this recording.
        
        Args:
            duration_seconds: Desired duration (max = recording duration)
            
        Returns:
            Tuple of (start_time_sec, end_time_sec) for API use
        """
        available_duration = int(self.duration_seconds)
        actual_duration = min(duration_seconds, available_duration)
        
        return (self.start_time, self.start_time + actual_duration)


@dataclass
class RecordingsInfo:
    """Information about available recordings in MongoDB."""
    recordings: List[Recording]
    query_time: datetime
    
    @property
    def has_recordings(self) -> bool:
        """Check if any recordings are available."""
        return len(self.recordings) > 0
    
    @property
    def count(self) -> int:
        """Number of available recordings."""
        return len(self.recordings)
    
    @property
    def total_duration_seconds(self) -> float:
        """Total duration of all recordings."""
        return sum(r.duration_seconds for r in self.recordings)
    
    def get_recording(self, min_duration_seconds: int = 10) -> Optional[Recording]:
        """
        Get a recording with at least the specified duration.
        
        Args:
            min_duration_seconds: Minimum required duration
            
        Returns:
            Recording object or None if no suitable recording found
        """
        for recording in self.recordings:
            if recording.duration_seconds >= min_duration_seconds:
                return recording
        return None
    
    def get_longest_recording(self) -> Optional[Recording]:
        """Get the longest available recording."""
        if not self.recordings:
            return None
        return max(self.recordings, key=lambda r: r.duration_seconds)


# =============================================================================
# MongoDB Tunnel Manager (Connection Pooling + Health Checks)
# =============================================================================

class MongoDBTunnelManager:
    """
    Professional MongoDB SSH Tunnel Manager with:
    - Connection pooling/reuse
    - Health checks
    - Automatic recovery
    - Thread-safe operations
    - Session-scoped lifecycle
    """
    
    def __init__(self, config_manager):
        """Initialize MongoDB Tunnel Manager."""
        self.config_manager = config_manager
        self.ssh_manager: Optional[Any] = None
        self.ssh_client: Optional[Any] = None
        self.port_forward_thread: Optional[threading.Thread] = None
        self.is_active = False
        self.last_health_check = 0
        self.health_check_interval = 30  # seconds
        self.lock = threading.Lock()
        self.k8s_host: Optional[str] = None
        self.local_port: int = 27017
        self.mongo_service: Optional[str] = None
        self.namespace: str = "panda"
        
        # Initialize config
        self._load_config()
    
    def _load_config(self):
        """Load configuration from config_manager."""
        ssh_config = self.config_manager.get_ssh_config()
        k8s_config = self.config_manager.get_kubernetes_config()
        mongo_config = self.config_manager.get_database_config()
        
        target_host_config = ssh_config.get("target_host", {})
        self.k8s_host = target_host_config.get("host")
        self.namespace = k8s_config.get("default_namespace", "panda")
        self.mongo_service = k8s_config.get("services", {}).get("mongodb", {}).get("name", "mongodb")
        self.local_port = mongo_config.get("port", 27017)
    
    def setup(self) -> bool:
        """
        Set up MongoDB SSH tunnel with connection reuse.
        
        Returns:
            True if tunnel setup successful
        """
        with self.lock:
            if self.is_active:
                # Verify tunnel is still healthy
                if self._check_health():
                    logger.debug("MongoDB tunnel already active and healthy")
                    return True
                else:
                    logger.warning("MongoDB tunnel marked active but unhealthy, reconnecting...")
                    self._cleanup_internal()
            
            return self._setup_tunnel()
    
    def _setup_tunnel(self) -> bool:
        """Internal tunnel setup (must be called with lock held)."""
        if not PARAMIKO_AVAILABLE:
            logger.warning("Paramiko not available - cannot create SSH tunnel for MongoDB")
            return False
        
        if not self.k8s_host:
            logger.warning("No Kubernetes host configured for MongoDB SSH tunnel")
            return False
        
        try:
            logger.info(f"Setting up SSH tunnel for MongoDB: {self.mongo_service} in namespace {self.namespace}")
            
            def run_port_forward():
                try:
                    # Reuse existing SSHManager connection if available
                    if not self.ssh_manager or not self.ssh_manager.connected:
                        from src.infrastructure.ssh_manager import SSHManager
                        self.ssh_manager = SSHManager(self.config_manager)
                        if not self.ssh_manager.connect():
                            logger.error("Failed to connect via SSHManager")
                            return
                    
                    client = self.ssh_manager.ssh_client
                    self.ssh_client = client
                    
                    # Get remote port from config
                    mongo_config = self.config_manager.get_database_config()
                    remote_port = mongo_config.get("port", 27017)
                    
                    pf_cmd = (
                        f"kubectl port-forward --address 0.0.0.0 -n {self.namespace} "
                        f"svc/{self.mongo_service} {self.local_port}:{remote_port}"
                    )
                    
                    logger.info(f"Starting kubectl port-forward for MongoDB: {pf_cmd}")
                    stdin, stdout, stderr = client.exec_command(pf_cmd)
                    
                    # Wait for port-forward confirmation
                    port_forward_started = False
                    confirmation_lines = []
                    
                    # Read first few lines to get confirmation
                    for _ in range(10):  # Read up to 10 lines
                        try:
                            line = stdout.readline()
                            if line:
                                line_str = line.strip()
                                confirmation_lines.append(line_str)
                                logger.debug(f"mongodb port-forward: {line_str}")
                                
                                if "Forwarding from" in line_str or "Forwarding" in line_str:
                                    port_forward_started = True
                                    logger.info(f"✅ MongoDB port-forward confirmed: {line_str}")
                                    with self.lock:
                                        self.is_active = True
                                        self.last_health_check = time.time()
                                    break
                        except Exception as e:
                            logger.debug(f"Error reading port-forward output: {e}")
                            break
                    
                    if not port_forward_started:
                        logger.warning(f"MongoDB port-forward started but no confirmation message received. Output: {confirmation_lines}")
                        # Still mark as active - port check will verify later
                        with self.lock:
                            self.is_active = True
                    
                    # Keep reading to keep connection alive
                    for line in stdout:
                        logger.debug(f"mongodb port-forward: {line.strip()}")
                        if not self.is_active:
                            break
                    
                    logger.info("MongoDB port-forward stopped")
                    with self.lock:
                        self.is_active = False
                    
                except Exception as e:
                    logger.error(f"MongoDB port-forward thread error: {e}", exc_info=True)
                    with self.lock:
                        self.is_active = False
            
            # Start port-forward in background thread
            self.port_forward_thread = threading.Thread(target=run_port_forward, daemon=True)
            self.port_forward_thread.start()
            
            # Wait for port to become available
            logger.info("Waiting for MongoDB port-forward to start...")
            max_wait = 15
            for i in range(max_wait):
                time.sleep(1)
                if self._check_port_available():
                    logger.info(f"✅ MongoDB port-forward active on {self.k8s_host}:{self.local_port}")
                    self.last_health_check = time.time()
                    return True
            
            logger.warning(f"MongoDB port-forward did not become available on {self.k8s_host}:{self.local_port} within {max_wait}s")
            self._cleanup_internal()
            return False
            
        except Exception as e:
            logger.error(f"Failed to setup MongoDB SSH tunnel: {e}", exc_info=True)
            self._cleanup_internal()
            return False
    
    def _check_port_available(self) -> bool:
        """Check if port is available on remote host."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.k8s_host, self.local_port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def _check_health(self) -> bool:
        """
        Check tunnel health (port availability + time since last check).
        
        Returns:
            True if tunnel is healthy
        """
        current_time = time.time()
        
        # Check if health check is needed
        if current_time - self.last_health_check < self.health_check_interval:
            return True  # Assume healthy if checked recently
        
        # Perform health check
        is_healthy = self._check_port_available()
        self.last_health_check = current_time
        
        if not is_healthy:
            logger.warning("MongoDB tunnel health check failed - tunnel may be down")
        
        return is_healthy
    
    def ensure_healthy(self) -> bool:
        """
        Ensure tunnel is healthy, reconnect if needed.
        
        Returns:
            True if tunnel is healthy
        """
        with self.lock:
            if not self.is_active:
                logger.info("MongoDB tunnel not active, setting up...")
                return self._setup_tunnel()
            
            if not self._check_health():
                logger.warning("MongoDB tunnel unhealthy, reconnecting...")
                self._cleanup_internal()
                return self._setup_tunnel()
            
            return True
    
    def _cleanup_internal(self):
        """Internal cleanup (must be called with lock held)."""
        if self.is_active:
            self.is_active = False
        
        if self.ssh_manager:
            try:
                # Don't disconnect - we want to reuse the connection
                # Only disconnect if we're completely cleaning up
                pass
            except Exception:
                pass
        
        if self.port_forward_thread:
            try:
                self.port_forward_thread.join(timeout=2)
            except Exception:
                pass
            self.port_forward_thread = None
    
    def cleanup(self):
        """Clean up tunnel and connections."""
        with self.lock:
            logger.info("Cleaning up MongoDB SSH tunnel...")
            self.is_active = False
            
            if self.ssh_manager:
                try:
                    self.ssh_manager.disconnect()
                except Exception:
                    pass
                self.ssh_manager = None
            
            if self.ssh_client:
                try:
                    self.ssh_client.close()
                except Exception:
                    pass
                self.ssh_client = None
            
            if self.port_forward_thread:
                try:
                    self.port_forward_thread.join(timeout=5)
                except Exception:
                    pass
                self.port_forward_thread = None
            
            logger.info("MongoDB tunnel cleanup complete")
    
    def get_connection_host(self) -> str:
        """Get the host to connect to (remote host where port-forward runs)."""
        return self.k8s_host or "localhost"


# Global MongoDB Tunnel Manager instance (singleton pattern)
_mongodb_tunnel_manager: Optional['MongoDBTunnelManager'] = None
_mongodb_tunnel_manager_lock = threading.Lock()


def _get_mongodb_tunnel_manager(config_manager) -> MongoDBTunnelManager:
    """
    Get or create MongoDB Tunnel Manager instance (singleton).
    
    Args:
        config_manager: ConfigManager instance
        
    Returns:
        MongoDBTunnelManager instance
    """
    global _mongodb_tunnel_manager
    
    with _mongodb_tunnel_manager_lock:
        if _mongodb_tunnel_manager is None:
            _mongodb_tunnel_manager = MongoDBTunnelManager(config_manager)
        
        return _mongodb_tunnel_manager


# =============================================================================
# SSH Tunnel Helper Functions (Legacy - for backward compatibility)
# =============================================================================

def _setup_mongodb_ssh_tunnel(config_manager) -> bool:
    """
    Set up SSH tunnel for MongoDB using kubectl port-forward.
    
    Uses MongoDBTunnelManager for connection pooling and health checks.
    
    Args:
        config_manager: ConfigManager instance
        
    Returns:
        True if tunnel setup successful
    """
    # Use the professional tunnel manager
    manager = _get_mongodb_tunnel_manager(config_manager)
    return manager.setup()


def _cleanup_mongodb_ssh_tunnel():
    """
    Clean up MongoDB SSH tunnel.
    
    Uses MongoDBTunnelManager for proper cleanup.
    """
    global _mongodb_tunnel_manager
    
    with _mongodb_tunnel_manager_lock:
        if _mongodb_tunnel_manager:
            _mongodb_tunnel_manager.cleanup()
            _mongodb_tunnel_manager = None


# =============================================================================
# MongoDB Direct Query Functions
# =============================================================================

def fetch_recordings_from_mongodb(
    config_manager,
    max_recordings: int = 100,
    min_duration_seconds: float = 5.0,
    max_duration_seconds: float = 300.0,  # 5 minutes - extended for flexibility
    weeks_back: int = 4  # 1 month - extended from 2 weeks for different environments
) -> RecordingsInfo:
    """
    Fetch available recordings DIRECTLY from MongoDB (not via Focus Server API).
    
    DYNAMIC TIME RANGE: Searches from current date going back.
    Works with both kefar_saba and staging environments which have different data.
    
    Collects ALL recordings in the time range without any filters:
    - Time range: From NOW to weeks_back weeks ago
    - No duration filters - collects recordings of any duration
    - No deleted status filters - collects all recordings (deleted and non-deleted)
    
    MongoDB Structure:
    1. base_paths collection → get the guid
    2. Collection named {guid} → contains recordings
    
    Args:
        config_manager: ConfigManager instance
        max_recordings: Maximum recordings to return (default: 100)
        min_duration_seconds: Ignored - kept for backward compatibility
        max_duration_seconds: Ignored - kept for backward compatibility
        weeks_back: Number of weeks back to search (default: 4 = 1 month)
        
    Returns:
        RecordingsInfo object with available recordings
    """
    logger.info(f"Querying MongoDB directly for ALL recordings in time range: last {weeks_back} weeks (no filters)...")
    
    # Setup SSH tunnel for MongoDB
    tunnel_setup = _setup_mongodb_ssh_tunnel(config_manager)
    use_tunnel = tunnel_setup
    
    # MongoDB client - will be closed in finally block
    client = None
    
    try:
        # Get MongoDB config
        mongo_config = config_manager.get_database_config()
        
        # Determine connection host and port
        if use_tunnel:
            # Use tunnel manager to ensure healthy connection
            manager = _get_mongodb_tunnel_manager(config_manager)
            if not manager.ensure_healthy():
                logger.warning("MongoDB tunnel unhealthy, falling back to direct connection")
                use_tunnel = False
                mongo_host = mongo_config["host"]
                mongo_port = mongo_config["port"]
            else:
                # Port-forward runs on remote host with --address 0.0.0.0
                # So we connect to the remote host, not localhost
                mongo_host = manager.get_connection_host()
                mongo_port = mongo_config.get("port", 27017)
                logger.info(f"Using SSH tunnel: connecting to {mongo_host}:{mongo_port} (port-forward on remote host)")
        else:
            # Direct connection (fallback)
            mongo_host = mongo_config["host"]
            mongo_port = mongo_config["port"]
            logger.info(f"Using direct connection: {mongo_host}:{mongo_port}")
        
        # Connect to MongoDB with retry logic
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"MongoDB connection attempt {attempt + 1}/{max_retries} to {mongo_host}:{mongo_port}")
                client = pymongo.MongoClient(
                    host=mongo_host,
                    port=mongo_port,
                    username=mongo_config["username"],
                    password=mongo_config["password"],
                    authSource=mongo_config.get("auth_source", "prisma"),
                    serverSelectionTimeoutMS=10000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=30000
                )
                
                # Test connection
                client.admin.command('ping')
                break  # Success
                
            except Exception as e:
                logger.warning(f"MongoDB connection attempt {attempt + 1} failed: {e}")
                if client:
                    try:
                        client.close()
                    except Exception:
                        pass
                    client = None
                
                # If tunnel was used and failed, try direct connection as fallback
                if attempt == 0 and use_tunnel:
                    logger.info("Tunnel connection failed, trying direct connection as fallback...")
                    mongo_host = mongo_config["host"]
                    mongo_port = mongo_config["port"]
                    use_tunnel = False
                elif attempt == max_retries - 1:
                    raise  # Re-raise on last attempt
        
        if not client:
            raise Exception("Failed to connect to MongoDB after all retry attempts")
        
        # Get database
        db_name = mongo_config.get("database", "prisma")
        db = client[db_name]
        
        logger.info(f"✅ Connected to MongoDB: {mongo_host}:{mongo_port}/{db_name}")
        
        # Step 1: Identify current environment and get GUIDs ONLY for that environment
        # CRITICAL: Each environment has its own GUIDs/collections:
        #   - kefar_saba: /prisma/root/recordings/segy → 24774bcb-a6f6-4e23-aa49-c100ad717bf0
        #   - staging: /prisma/root/recordings → 25b4875f-5785-4b24-8895-121039474bcd, 873ea296-a3a3-4c22-a880-608766f004cd
        # We MUST query only the GUIDs for the current environment, NOT mix data from different environments!
        
        current_env = config_manager.get_current_environment()
        logger.info(f"Current environment: {current_env}")
        
        base_paths = db["base_paths"]
        
        # Map environment to base_path patterns
        # Each environment has specific base_path patterns that identify its collections
        env_base_paths = {
            "staging": ["/prisma/root/recordings"],
            "kefar_saba": ["/prisma/root/recordings/segy"],
            "production": ["/prisma/root/recordings/segy"],  # kefar_saba is alias for production
        }
        
        # Get base_path patterns for current environment
        target_base_paths = env_base_paths.get(current_env, [])
        
        if not target_base_paths:
            logger.warning(f"Unknown environment '{current_env}', trying all base_paths")
            target_base_paths = ["/prisma/root/recordings", "/prisma/root/recordings/segy"]
        
        logger.info(f"Looking for base_paths for environment '{current_env}': {target_base_paths}")
        
        # Find base_paths documents for current environment ONLY
        env_base_path_docs = []
        for base_path_pattern in target_base_paths:
            docs = list(base_paths.find({
                "base_path": base_path_pattern,
                "is_archive": False
            }))
            env_base_path_docs.extend(docs)
        
        if not env_base_path_docs:
            # Log all available base_paths for debugging
            all_docs = list(base_paths.find({"is_archive": False}))
            available_paths = [d.get('base_path', 'N/A') for d in all_docs]
            logger.warning(f"No base_paths documents found for environment '{current_env}'. Available paths: {available_paths}")
            return RecordingsInfo(recordings=[], query_time=datetime.now())
        
        # Extract GUIDs ONLY from current environment's base_paths
        guids = []
        for doc in env_base_path_docs:
            guid = doc.get("guid")
            if not guid:
                guid = doc.get("_id")
                if isinstance(guid, dict):
                    guid = str(guid)
            
            if guid:
                guid_str = str(guid)
                # Only add GUIDs that look like valid UUIDs (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
                if len(guid_str) == 36 and guid_str.count('-') == 4:
                    guids.append(guid_str)
                    base_path_val = doc.get('base_path', 'N/A')
                    logger.info(f"Found GUID for environment '{current_env}' from base_path '{base_path_val}': {guid_str}")
        
        if not guids:
            logger.warning(f"No valid GUIDs found for environment '{current_env}'")
            return RecordingsInfo(recordings=[], query_time=datetime.now())
        
        logger.info(f"Found {len(guids)} GUID collections for environment '{current_env}': {guids}")
        
        # Calculate time range: from today to weeks_back weeks ago
        now = datetime.now()
        weeks_ago = now - timedelta(weeks=weeks_back)
        
        logger.info(f"🔍 Time range filter: {weeks_ago.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')} (last {weeks_back} weeks)")
        logger.info(f"   Collecting ALL recordings from {len(guids)} collections for environment '{current_env}' (no duration/deleted filters)")
        
        # Query by time range only - find ALL recordings that overlap with the time range:
        # - Recordings that started within the range, OR
        # - Recordings that ended within the range, OR
        # - Recordings that span the entire range (started before and ended after)
        # No filters on deleted status or duration - collect everything in the time range
        query = {
            "$or": [
                # Started within range
                {
                    "start_time": {
                        "$gte": weeks_ago,
                        "$lte": now
                    }
                },
                # Ended within range
                {
                    "end_time": {
                        "$gte": weeks_ago,
                        "$lte": now
                    }
                },
                # Spans entire range (started before and ended after)
                {
                    "start_time": {"$lt": weeks_ago},
                    "end_time": {"$gt": now}
                }
            ]
        }
        logger.debug(f"MongoDB query: {query}")
        sort = [("start_time", pymongo.DESCENDING)]
        
        # Step 3: Query ALL GUID collections and collect recordings from all of them
        recordings = []
        skipped_no_times = 0
        total_matching_all_collections = 0
        
        for guid in guids:
            collection_name = str(guid)
            
            # Check if collection exists
            if collection_name not in db.list_collection_names():
                logger.debug(f"Collection {collection_name} does not exist, skipping")
                continue
            
            try:
                recordings_collection = db[collection_name]
                
                # Count total matching recordings in this collection
                total_matching = recordings_collection.count_documents(query)
                total_matching_all_collections += total_matching
                
                logger.info(f"📊 Collection '{collection_name}': {total_matching} recordings in time range")
                
                # Fetch recordings from this collection
                # Use a higher limit per collection to ensure we get enough recordings overall
                cursor = recordings_collection.find(query).sort(sort).limit(max_recordings * 2)
                
                collection_recordings_count = 0
                for doc in cursor:
                    # Stop if we have enough recordings overall
                    if len(recordings) >= max_recordings:
                        break
                    
                    start_time = doc.get("start_time")
                    end_time = doc.get("end_time")
                    
                    # Skip recordings without valid timestamps
                    if not start_time or not end_time:
                        skipped_no_times += 1
                        logger.debug(f"Skipping recording without start_time or end_time")
                        continue
                    
                    # Convert datetime to epoch milliseconds
                    # IMPORTANT: MongoDB stores datetimes as naive UTC, but Python's timestamp()
                    # assumes local timezone. We need to treat the datetime as UTC explicitly.
                    if isinstance(start_time, datetime):
                        # Treat naive datetime as UTC (MongoDB stores UTC)
                        if start_time.tzinfo is None:
                            start_utc = start_time.replace(tzinfo=timezone.utc)
                            start_ms = int(start_utc.timestamp() * 1000)
                        else:
                            start_ms = int(start_time.timestamp() * 1000)
                    else:
                        start_ms = int(start_time)
                    
                    if isinstance(end_time, datetime):
                        # Treat naive datetime as UTC (MongoDB stores UTC)
                        if end_time.tzinfo is None:
                            end_utc = end_time.replace(tzinfo=timezone.utc)
                            end_ms = int(end_utc.timestamp() * 1000)
                        else:
                            end_ms = int(end_time.timestamp() * 1000)
                    else:
                        end_ms = int(end_time)
                    
                    # Calculate duration for logging
                    duration_seconds = (end_ms - start_ms) / 1000.0
                    
                    # Add ALL recordings found in the time range (no duration or deleted filters)
                    recordings.append(Recording(start_time_ms=start_ms, end_time_ms=end_ms))
                    collection_recordings_count += 1
                    
                    logger.debug(
                        f"  Recording from {collection_name}: {start_time} to {end_time} "
                        f"({duration_seconds:.1f}s)"
                    )
                
                logger.info(f"   Collected {collection_recordings_count} recordings from '{collection_name}'")
                
                # Stop if we have enough recordings overall
                if len(recordings) >= max_recordings:
                    logger.info(f"   Reached limit of {max_recordings} recordings, stopping collection")
                    break
            
            except Exception as e:
                logger.warning(f"Error querying collection '{collection_name}': {e}")
                continue
        
        # Sort by start_time (most recent first)
        recordings.sort(key=lambda r: r.start_time_ms, reverse=True)
        
        logger.info(f"\n✅ Found {len(recordings)} recordings from {len(guids)} MongoDB collections for environment '{current_env}'")
        logger.info(f"   - Total matching recordings across all collections: {total_matching_all_collections}")
        logger.info(f"   - Collections queried: {guids}")
        logger.info(f"   - Time range: {weeks_ago.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}")
        logger.info(f"   - No filters applied (collected all recordings in time range)")
        if skipped_no_times > 0:
            logger.info(f"   - Skipped: {skipped_no_times} recordings without valid timestamps")
        
        # Log first 5 recordings
        for i, rec in enumerate(recordings[:5]):
            logger.info(
                f"  Recording {i+1}: {rec.start_datetime} to {rec.end_datetime} "
                f"({rec.duration_seconds:.1f}s)"
            )
        
        return RecordingsInfo(
            recordings=recordings,
            query_time=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch recordings from MongoDB: {e}")
        return RecordingsInfo(recordings=[], query_time=datetime.now())
    
    finally:
        # CRITICAL: Always close MongoDB client to prevent resource leaks
        if client:
            try:
                client.close()
                logger.debug("MongoDB client closed")
            except Exception as close_error:
                logger.warning(f"Error closing MongoDB client: {close_error}")


# =============================================================================
# Focus Server API Functions (Fallback)
# =============================================================================

def fetch_available_recordings(
    focus_server_api,
    hours_back: int = 336,  # 2 weeks (14 days * 24 hours)
    max_recordings: int = 50,
    min_duration_seconds: float = 5.0,
    max_duration_seconds: float = 10.0
) -> RecordingsInfo:
    """
    Fetch available recordings from MongoDB via Focus Server API.
    
    Searches for recordings by time range only (not by deleted: false).
    Filters recordings by duration: 5-10 seconds only.
    Time range: from today to 2 weeks ago.
    
    Args:
        focus_server_api: FocusServerAPI instance
        hours_back: How many hours back to search (default: 336 = 2 weeks)
        max_recordings: Maximum recordings to return (default: 50)
        min_duration_seconds: Minimum recording duration (default: 5.0)
        max_duration_seconds: Maximum recording duration (default: 10.0)
        
    Returns:
        RecordingsInfo object with available recordings
    """
    from src.models.focus_server_models import RecordingsInTimeRangeRequest
    
    weeks_back = hours_back / (24 * 7)
    logger.info(f"Querying MongoDB for recordings in last {weeks_back:.1f} weeks ({hours_back} hours, duration: {min_duration_seconds}-{max_duration_seconds}s)...")
    
    try:
        # Query time range
        now_ms = int(time.time() * 1000)
        start_ms = now_ms - (hours_back * 60 * 60 * 1000)
        
        request = RecordingsInTimeRangeRequest(
            start_time=start_ms,
            end_time=now_ms
        )
        
        response = focus_server_api.get_recordings_in_time_range(request)
        
        # Convert to Recording objects and filter by duration
        recordings = []
        for start, end in response.root:
            duration_seconds = (end - start) / 1000.0
            
            # Filter by duration: 5-10 seconds only
            if min_duration_seconds <= duration_seconds <= max_duration_seconds:
                recordings.append(Recording(start_time_ms=start, end_time_ms=end))
                
                # Stop if we have enough recordings
                if len(recordings) >= max_recordings:
                    break
        
        # Sort by duration (longest first)
        recordings.sort(key=lambda r: r.duration_seconds, reverse=True)
        
        logger.info(f"Found {len(recordings)} recordings in MongoDB with duration {min_duration_seconds}-{max_duration_seconds}s")
        
        # Log first 5 recordings
        for i, rec in enumerate(recordings[:5]):
            logger.debug(
                f"  Recording {i+1}: {rec.start_datetime} to {rec.end_datetime} "
                f"({rec.duration_seconds:.1f}s)"
            )
        
        return RecordingsInfo(
            recordings=recordings,
            query_time=datetime.now()
        )
        
    except Exception as e:
        logger.warning(f"Failed to fetch recordings from MongoDB: {e}")
        return RecordingsInfo(recordings=[], query_time=datetime.now())


def get_historic_time_range_from_mongodb(
    config_manager,
    duration_seconds: int = 60,
    min_duration_seconds: float = 5.0,
    max_duration_seconds: float = 10.0,
    weeks_back: int = 2,
    focus_server_api=None,
    verify_with_focus_server: bool = True
) -> Optional[Tuple[int, int]]:
    """
    Get a valid time range for historic playback by querying MongoDB directly.
    
    This is the PREFERRED method (per Yonatan's feedback) - query MongoDB directly
    to get existing recordings.
    
    Searches for recordings with duration 5-10 seconds from the last two weeks.
    Optionally verifies with Focus Server API that the recording is accessible.
    
    Args:
        config_manager: ConfigManager instance
        duration_seconds: Desired duration for playback (will use full recording duration if shorter)
        min_duration_seconds: Minimum recording duration to search for (default: 5.0)
        max_duration_seconds: Maximum recording duration to search for (default: 10.0)
        weeks_back: Number of weeks back to search (default: 2)
        focus_server_api: Optional FocusServerAPI instance to verify recordings
        verify_with_focus_server: If True, verify recording exists via Focus Server API (default: True)
        
    Returns:
        Tuple of (start_time_sec, end_time_sec) or None if no recordings
    """
    info = fetch_recordings_from_mongodb(
        config_manager,
        min_duration_seconds=min_duration_seconds,
        max_duration_seconds=max_duration_seconds,
        weeks_back=weeks_back
    )
    
    if not info.has_recordings:
        logger.warning(f"No recordings available in MongoDB (duration: {min_duration_seconds}-{max_duration_seconds}s, time range: last {weeks_back} weeks)")
        return None
    
    # NOTE: Focus Server API /recordings_in_time_range returns 500 errors, so we can't verify recordings.
    # We'll use the first recording from MongoDB and let Focus Server handle validation during configure.
    
    # Get first available recording (already filtered by duration 5-10 seconds)
    recording = info.recordings[0] if info.recordings else None
    
    if recording:
        # Use the full recording duration (it's already 5-10 seconds)
        logger.info(f"Using recording from MongoDB: {recording.start_datetime} to {recording.end_datetime}")
        return (recording.start_time, recording.end_time)
    
    return None


def get_historic_time_range(
    focus_server_api,
    duration_seconds: int = 60,
    hours_back: int = 24
) -> Optional[Tuple[int, int]]:
    """
    Get a valid time range for historic playback from existing MongoDB data.
    
    FALLBACK method - uses Focus Server API. Prefer get_historic_time_range_from_mongodb().
    
    Args:
        focus_server_api: FocusServerAPI instance
        duration_seconds: Desired duration for playback
        hours_back: Hours to search back
        
    Returns:
        Tuple of (start_time_sec, end_time_sec) or None if no recordings
    """
    info = fetch_available_recordings(focus_server_api, hours_back=hours_back)
    
    if not info.has_recordings:
        logger.warning("No recordings available in MongoDB")
        return None
    
    recording = info.get_recording(min_duration_seconds=duration_seconds)
    
    if not recording:
        # Use longest available even if shorter than requested
        recording = info.get_longest_recording()
        if recording:
            logger.warning(
                f"No recording with {duration_seconds}s duration found. "
                f"Using longest: {recording.duration_seconds:.1f}s"
            )
    
    if recording:
        return recording.get_time_range(duration_seconds)
    
    return None


# =============================================================================
# Pytest Fixtures
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def mongodb_tunnel_session_cleanup(config_manager, request):
    """
    Session-scoped cleanup fixture for MongoDB SSH tunnel.
    
    Ensures MongoDB tunnel is properly cleaned up at the end of the test session.
    This fixture runs automatically for all tests that use MongoDB.
    
    Args:
        config_manager: ConfigManager instance
        request: Pytest request object
    """
    yield
    
    # Cleanup at session end
    logger.info("=" * 80)
    logger.info("MongoDB Tunnel Session Cleanup")
    logger.info("=" * 80)
    try:
        _cleanup_mongodb_ssh_tunnel()
        logger.info("✅ MongoDB tunnel cleanup complete")
    except Exception as e:
        logger.warning(f"MongoDB tunnel cleanup error: {e}")
    logger.info("=" * 80)


@pytest.fixture(scope="session")
def mongodb_recordings_info(config_manager) -> RecordingsInfo:
    """
    Session-scoped fixture that fetches available recordings DIRECTLY from MongoDB.
    
    This fixture queries MongoDB ONCE per test session and caches the results.
    Uses direct MongoDB connection (not Focus Server API).
    
    Usage:
        def test_historic_something(self, mongodb_recordings_info):
            if not mongodb_recordings_info.has_recordings:
                pytest.skip("No recordings available in MongoDB")
            
            recording = mongodb_recordings_info.get_recording(min_duration_seconds=60)
            start_time, end_time = recording.get_time_range(60)
    """
    return fetch_recordings_from_mongodb(config_manager)


@pytest.fixture
def available_recording(mongodb_recordings_info: RecordingsInfo) -> Optional[Recording]:
    """
    Fixture that provides a single available recording.
    
    Returns None if no recordings are available (test should skip).
    
    Usage:
        def test_historic_playback(self, available_recording):
            if available_recording is None:
                pytest.skip("No recordings available")
            
            start, end = available_recording.get_time_range(60)
    """
    return mongodb_recordings_info.get_recording(min_duration_seconds=10)


@pytest.fixture
def historic_time_range(config_manager) -> Optional[Tuple[int, int]]:
    """
    Fixture that provides a valid time range for historic playback.
    
    Queries MongoDB DIRECTLY (not via Focus Server API).
    
    Returns:
        Tuple of (start_time_sec, end_time_sec) or None if no recordings
        
    Usage:
        def test_historic_playback(self, historic_time_range):
            if historic_time_range is None:
                pytest.skip("No recordings available")
            
            start_time, end_time = historic_time_range
            config = {
                "start_time": start_time,
                "end_time": end_time,
                ...
            }
    """
    return get_historic_time_range_from_mongodb(config_manager, duration_seconds=60)


@pytest.fixture
def short_historic_time_range(config_manager) -> Optional[Tuple[int, int]]:
    """
    Fixture for short duration historic playback (1 minute).
    """
    return get_historic_time_range_from_mongodb(config_manager, duration_seconds=60)


@pytest.fixture
def medium_historic_time_range(config_manager) -> Optional[Tuple[int, int]]:
    """
    Fixture for medium duration historic playback (5 minutes).
    """
    return get_historic_time_range_from_mongodb(config_manager, duration_seconds=300)


@pytest.fixture
def long_historic_time_range(config_manager) -> Optional[Tuple[int, int]]:
    """
    Fixture for long duration historic playback (10 minutes).
    """
    return get_historic_time_range_from_mongodb(config_manager, duration_seconds=600)

