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
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


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
# MongoDB Direct Query Functions
# =============================================================================

def fetch_recordings_from_mongodb(
    config_manager,
    max_recordings: int = 50,
    min_duration_seconds: float = 5.0,
    max_duration_seconds: float = 10.0,
    weeks_back: int = 2
) -> RecordingsInfo:
    """
    Fetch available recordings DIRECTLY from MongoDB (not via Focus Server API).
    
    Filters recordings by:
    - Duration: 5-10 seconds only
    - Time range: From today to two weeks ago
    
    MongoDB Structure:
    1. base_paths collection → get the guid
    2. Collection named {guid} → contains recordings
    
    Args:
        config_manager: ConfigManager instance
        max_recordings: Maximum recordings to return
        min_duration_seconds: Minimum recording duration (default: 5.0)
        max_duration_seconds: Maximum recording duration (default: 10.0)
        weeks_back: Number of weeks back to search (default: 2)
        
    Returns:
        RecordingsInfo object with available recordings
    """
    logger.info(f"Querying MongoDB directly for recordings (duration: {min_duration_seconds}-{max_duration_seconds}s, time range: last {weeks_back} weeks)...")
    
    try:
        # Get MongoDB config
        mongo_config = config_manager.get_database_config()
        
        # Connect to MongoDB
        client = pymongo.MongoClient(
            host=mongo_config["host"],
            port=mongo_config["port"],
            username=mongo_config["username"],
            password=mongo_config["password"],
            authSource=mongo_config.get("auth_source", "prisma"),
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=30000
        )
        
        # Get database
        db_name = mongo_config.get("database", "prisma")
        db = client[db_name]
        
        logger.info(f"Connected to MongoDB: {mongo_config['host']}:{mongo_config['port']}/{db_name}")
        
        # Step 1: Get guid from base_paths collection
        # IMPORTANT: Use the GUID for /prisma/root/recordings (not /prisma/root/recordings/segy)
        # This is the correct base_path that contains the actual recordings
        base_paths = db["base_paths"]
        base_path_doc = base_paths.find_one({
            "base_path": "/prisma/root/recordings",
            "is_archive": False
        })
        
        if not base_path_doc:
            logger.warning("No base_paths document found for /prisma/root/recordings in MongoDB")
            client.close()
            return RecordingsInfo(recordings=[], query_time=datetime.now())
        
        # Get the guid (it's the collection name for recordings)
        guid = base_path_doc.get("guid")
        if not guid:
            # Try other common field names
            guid = base_path_doc.get("_id")
            if isinstance(guid, dict):
                guid = str(guid)
        
        logger.info(f"Found guid from base_paths for /prisma/root/recordings: {guid}")
        
        # Step 2: Query the collection named by guid
        recordings_collection = db[str(guid)]
        
        # Calculate time range: from today to two weeks ago
        now = datetime.now()
        two_weeks_ago = now - timedelta(weeks=weeks_back)
        
        # Query by time range only (no deleted filter)
        query = {
            "start_time": {
                "$gte": two_weeks_ago,
                "$lte": now
            }
        }
        sort = [("start_time", pymongo.DESCENDING)]
        
        # Fetch more recordings than needed to filter by duration
        cursor = recordings_collection.find(query).sort(sort).limit(max_recordings * 10)
        
        recordings = []
        for doc in cursor:
            start_time = doc.get("start_time")
            end_time = doc.get("end_time")
            
            if start_time and end_time:
                # Convert datetime to epoch milliseconds
                if isinstance(start_time, datetime):
                    start_ms = int(start_time.timestamp() * 1000)
                else:
                    start_ms = int(start_time)
                
                if isinstance(end_time, datetime):
                    end_ms = int(end_time.timestamp() * 1000)
                else:
                    end_ms = int(end_time)
                
                # Calculate duration
                duration_seconds = (end_ms - start_ms) / 1000.0
                
                # Filter by duration: 5-10 seconds only
                if min_duration_seconds <= duration_seconds <= max_duration_seconds:
                    recordings.append(Recording(start_time_ms=start_ms, end_time_ms=end_ms))
                    
                    logger.debug(
                        f"  Recording: {start_time} to {end_time} "
                        f"({duration_seconds:.1f}s)"
                    )
                    
                    # Stop if we have enough recordings
                    if len(recordings) >= max_recordings:
                        break
        
        # Close connection
        client.close()
        
        # Sort by duration (longest first)
        recordings.sort(key=lambda r: r.duration_seconds, reverse=True)
        
        logger.info(f"Found {len(recordings)} recordings in MongoDB (guid: {guid}) with duration {min_duration_seconds}-{max_duration_seconds}s")
        
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


# =============================================================================
# Focus Server API Functions (Fallback)
# =============================================================================

def fetch_available_recordings(
    focus_server_api,
    hours_back: int = 24,
    max_recordings: int = 50,
    min_duration_seconds: float = 5.0,
    max_duration_seconds: float = 10.0
) -> RecordingsInfo:
    """
    Fetch available recordings from MongoDB via Focus Server API.
    
    Filters recordings by duration: 5-10 seconds only.
    
    Args:
        focus_server_api: FocusServerAPI instance
        hours_back: How many hours back to search (default: 24)
        max_recordings: Maximum recordings to return (default: 50)
        min_duration_seconds: Minimum recording duration (default: 5.0)
        max_duration_seconds: Maximum recording duration (default: 10.0)
        
    Returns:
        RecordingsInfo object with available recordings
    """
    from src.models.focus_server_models import RecordingsInTimeRangeRequest
    
    logger.info(f"Querying MongoDB for recordings in last {hours_back} hours (duration: {min_duration_seconds}-{max_duration_seconds}s)...")
    
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
    weeks_back: int = 2
) -> Optional[Tuple[int, int]]:
    """
    Get a valid time range for historic playback by querying MongoDB directly.
    
    This is the PREFERRED method (per Yonatan's feedback) - query MongoDB directly
    to get existing recordings.
    
    Searches for recordings with duration 5-10 seconds from the last two weeks.
    
    Args:
        config_manager: ConfigManager instance
        duration_seconds: Desired duration for playback (will use full recording duration if shorter)
        min_duration_seconds: Minimum recording duration to search for (default: 5.0)
        max_duration_seconds: Maximum recording duration to search for (default: 10.0)
        weeks_back: Number of weeks back to search (default: 2)
        
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
    
    # Get first available recording (already filtered by duration 5-10 seconds)
    recording = info.recordings[0] if info.recordings else None
    
    if recording:
        # Use the full recording duration (it's already 5-10 seconds)
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

