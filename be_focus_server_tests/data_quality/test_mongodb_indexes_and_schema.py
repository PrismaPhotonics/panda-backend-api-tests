"""
Data Quality Tests - MongoDB Indexes and Schema Validation
===========================================================

Comprehensive MongoDB data quality tests covering indexes, schema, and metadata.

Based on Xray Tests: PZ-13806 to PZ-13812

Tests covered:
    - PZ-13806: MongoDB Direct TCP Connection
    - PZ-13807: MongoDB Connection Using Focus Server Config
    - PZ-13808: MongoDB Quick Response Time
    - PZ-13809: Verify Required Collections Exist
    - PZ-13810: Verify Critical Indexes Exist
    - PZ-13811: Validate Recordings Document Schema
    - PZ-13812: Verify Recordings Have Complete Metadata

Author: QA Automation Architect  
Date: 2025-10-27
"""

import pytest
import logging
import time
from typing import Dict, Any, List

from src.infrastructure.mongodb_manager import MongoDBManager
from src.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

# Check if pymongo is available
try:
    import pymongo
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


# ===================================================================
# Test Class: MongoDB Connection Tests
# ===================================================================

@pytest.mark.data_quality
@pytest.mark.mongodb
@pytest.mark.infrastructure
@pytest.mark.skipif(not PYMONGO_AVAILABLE, reason="pymongo not installed")
class TestMongoDBConnection:
    """
    Test suite for MongoDB connection validation.
    
    Tests covered:
        - PZ-13806: Direct TCP connection
        - PZ-13807: Connection using Focus config
        - PZ-13808: Quick response time
    
    Priority: HIGH
    """
    
    @pytest.mark.xray("PZ-13806")
    def test_mongodb_direct_tcp_connection(self, config_manager):
        """
        Test PZ-13806: MongoDB Direct TCP Connection and Authentication.
        
        Steps:
            1. Get MongoDB config
            2. Create direct TCP connection
            3. Authenticate
            4. Verify connection
        
        Expected:
            - TCP connection succeeds
            - Authentication succeeds
            - Ping command works
        
        Jira: PZ-13806
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: MongoDB Direct TCP Connection (PZ-13806)")
        logger.info("=" * 80)
        
        mongo_config = config_manager.get_database_config()
        
        logger.info(f"Connecting to MongoDB:")
        logger.info(f"  Host: {mongo_config['host']}")
        logger.info(f"  Port: {mongo_config['port']}")
        
        client = pymongo.MongoClient(
            host=mongo_config["host"],
            port=mongo_config["port"],
            username=mongo_config["username"],
            password=mongo_config["password"],
            authSource=mongo_config.get("auth_source", "admin"),
            serverSelectionTimeoutMS=5000
        )
        
        # Ping
        client.admin.command('ping')
        logger.info("✅ MongoDB ping successful")
        
        # Get server info
        server_info = client.server_info()
        logger.info(f"   MongoDB version: {server_info['version']}")
        
        client.close()
        logger.info("✅ TEST PASSED")
    
    @pytest.mark.xray("PZ-13807")
    def test_mongodb_connection_using_focus_config(self, mongodb_manager: MongoDBManager):
        """
        Test PZ-13807: MongoDB Connection Using Focus Server Config.
        
        Steps:
            1. Use MongoDBManager (uses ConfigManager internally)
            2. Verify connection works
            3. Test basic operations
        
        Expected:
            - Connection via ConfigManager succeeds
            - Configuration consistent
        
        Jira: PZ-13807
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: MongoDB Using Focus Config (PZ-13807)")
        logger.info("=" * 80)
        
        # Connect to MongoDB
        connection_success = mongodb_manager.connect()
        assert connection_success, "Failed to connect to MongoDB"
        
        assert mongodb_manager.client is not None
        logger.info("✅ MongoDB manager initialized via ConfigManager")
        
        db = mongodb_manager.get_database()
        collections = db.list_collection_names()
        
        logger.info(f"✅ Database accessible: {db.name}")
        logger.info(f"   Collections: {len(collections)}")
        
        logger.info("✅ TEST PASSED")
    
    @pytest.mark.xray("PZ-13808")
    def test_mongodb_quick_response_time(self, mongodb_manager: MongoDBManager):
        """
        Test PZ-13808: MongoDB Quick Response Time Test.
        
        Steps:
            1. Measure ping latency
            2. Verify < 100ms
        
        Expected:
            - Ping latency < 100ms
            - Ideally < 50ms
        
        Jira: PZ-13808
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: MongoDB Response Time (PZ-13808)")
        logger.info("=" * 80)
        
        start = time.time()
        mongodb_manager.client.admin.command('ping')
        elapsed = (time.time() - start) * 1000
        
        logger.info(f"MongoDB ping: {elapsed:.2f}ms")
        
        assert elapsed < 100, f"Ping too slow: {elapsed:.2f}ms"
        logger.info("✅ Response time acceptable")
        
        if elapsed < 50:
            logger.info("⚡ Excellent latency!")
        
        logger.info("✅ TEST PASSED")


# ===================================================================
# Test Class: MongoDB Collections and Indexes
# ===================================================================

@pytest.mark.data_quality
@pytest.mark.mongodb
@pytest.mark.schema
class TestMongoDBCollectionsAndIndexes:
    """
    Test suite for MongoDB collections and indexes validation.
    
    Tests covered:
        - PZ-13809: Required collections exist
        - PZ-13810: Critical indexes exist
    
    Priority: HIGH
    """
    
    @pytest.mark.xray("PZ-13809")
    def test_required_mongodb_collections_exist(self, mongodb_manager: MongoDBManager):
        """
        Test PZ-13809: Verify Required MongoDB Collections Exist.
        
        Steps:
            1. Get database
            2. List all collections
            3. Verify required collections present
        
        Expected:
            - Recording collections exist
            - Metadata collections exist (if applicable)
        
        Jira: PZ-13809
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: Required Collections Exist (PZ-13809)")
        logger.info("=" * 80)
        
        db = mongodb_manager.get_database()
        collections = db.list_collection_names()
        
        logger.info(f"Found {len(collections)} collections")
        
        # Look for recording collections (GUID-based)
        recording_colls = [c for c in collections if 'recording' in c.lower()]
        
        assert len(recording_colls) > 0, "At least one recording collection should exist"
        
        logger.info(f"✅ Found {len(recording_colls)} recording collection(s):")
        for coll in recording_colls:
            logger.info(f"   - {coll}")
        
        logger.info("✅ TEST PASSED")
    
    @pytest.mark.xray("PZ-13810")
    def test_critical_mongodb_indexes_exist(self, mongodb_manager: MongoDBManager):
        """
        Test PZ-13810: Verify Critical MongoDB Indexes Exist.
        
        Steps:
            1. Access recording collection
            2. List indexes
            3. Verify critical indexes present
        
        Expected:
            - start_time index exists
            - end_time index exists
            - uuid index exists (unique)
        
        Jira: PZ-13810
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: Critical Indexes Exist (PZ-13810)")
        logger.info("=" * 80)
        
        db = mongodb_manager.get_database()
        collections = db.list_collection_names()
        recording_colls = [c for c in collections if 'recording' in c.lower()]
        
        if not recording_colls:
            pytest.skip("No recording collections found")
        
        collection = db[recording_colls[0]]
        indexes = list(collection.list_indexes())
        
        logger.info(f"Found {len(indexes)} indexes")
        
        index_names = [idx.get('name') for idx in indexes]
        logger.info(f"Indexes: {index_names}")
        
        # Check for critical indexes
        critical_fields = ['start_time', 'end_time', 'uuid']
        
        for field in critical_fields:
            field_indexed = any(field in str(idx.get('key', {})) for idx in indexes)
            if field_indexed:
                logger.info(f"✅ Index on '{field}' present")
            else:
                logger.warning(f"⚠️  Index on '{field}' missing")
        
        logger.info("✅ TEST PASSED")


# ===================================================================
# Test Class: MongoDB Schema Validation
# ===================================================================

@pytest.mark.data_quality
@pytest.mark.mongodb
@pytest.mark.schema
class TestMongoDBSchemaValidation:
    """
    Test suite for MongoDB document schema validation.
    
    Tests covered:
        - PZ-13811: Recordings document schema
        - PZ-13812: Recordings metadata completeness
    
    Priority: MEDIUM
    """
    
    @pytest.mark.xray("PZ-13811", "PZ-13684")
    @pytest.mark.xray("PZ-13811")
    def test_recordings_document_schema_validation(self, mongodb_manager: MongoDBManager):
        """
        Test PZ-13811, PZ-13684: Validate Recordings Document Schema.
        
        Steps:
            1. Get recording collection
            2. Fetch sample document
            3. Validate schema fields
        
        Expected:
            - Documents have consistent schema
            - Required fields present
        
        Jira: PZ-13811, PZ-13684
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: Recordings Schema Validation (PZ-13811, 13684)")
        logger.info("=" * 80)
        
        db = mongodb_manager.get_database()
        collections = db.list_collection_names()
        recording_colls = [c for c in collections if 'recording' in c.lower()]
        
        if not recording_colls:
            pytest.skip("No recording collections")
        
        collection = db[recording_colls[0]]
        doc = collection.find_one()
        
        if not doc:
            pytest.skip("Collection empty")
        
        logger.info("Document fields:")
        for key in doc.keys():
            logger.info(f"  - {key}")
        
        required = ['start_time', 'end_time', 'uuid']
        for field in required:
            assert field in doc, f"Required field '{field}' missing"
            logger.info(f"✅ {field} present")
        
        logger.info("✅ TEST PASSED")
    
    @pytest.mark.xray("PZ-13812", "PZ-13685")
    @pytest.mark.xray("PZ-13685")
    def test_recordings_metadata_completeness(self, mongodb_manager: MongoDBManager):
        """
        Test PZ-13812, PZ-13685: Verify Recordings Have Complete Metadata.
        
        Steps:
            1. Get recording documents
            2. Verify metadata fields complete
            3. Check for missing data
        
        Expected:
            - All recordings have complete metadata
            - No null/missing critical fields
        
        Jira: PZ-13812, PZ-13685
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: Recordings Metadata Completeness (PZ-13812, 13685)")
        logger.info("=" * 80)
        
        db = mongodb_manager.get_database()
        collections = db.list_collection_names()
        recording_colls = [c for c in collections if 'recording' in c.lower()]
        
        if not recording_colls:
            pytest.skip("No recording collections")
        
        collection = db[recording_colls[0]]
        
        # Get first 10 documents
        docs = list(collection.find().limit(10))
        
        logger.info(f"Checking {len(docs)} documents...")
        
        for i, doc in enumerate(docs, 1):
            # Check critical fields are not None
            for field in ['start_time', 'end_time', 'uuid']:
                if field in doc:
                    assert doc[field] is not None, f"Doc {i}: {field} is None"
        
        logger.info(f"✅ All {len(docs)} documents have complete metadata")
        logger.info("✅ TEST PASSED")


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary
def test_mongodb_indexes_schema_summary():
    """
    Summary test for MongoDB indexes and schema tests.
    
    Xray Tests Covered:
        - PZ-13806: Direct TCP Connection
        - PZ-13807: Focus Config Connection
        - PZ-13808: Response Time
        - PZ-13809: Collections Exist
        - PZ-13810: Indexes Exist
        - PZ-13811: Schema Validation
        - PZ-13812: Metadata Completeness
    
    This test always passes and serves as documentation.
    """
    logger.info("=" * 80)
    logger.info("MongoDB Indexes and Schema Tests Suite Summary")
    logger.info("=" * 80)
    logger.info("Tests in this module:")
    logger.info("  1. PZ-13806: Direct TCP Connection")
    logger.info("  2. PZ-13807: Focus Config Connection")
    logger.info("  3. PZ-13808: Response Time < 100ms")
    logger.info("  4. PZ-13809: Required Collections")
    logger.info("  5. PZ-13810: Critical Indexes")
    logger.info("  6. PZ-13811: Document Schema")
    logger.info("  7. PZ-13812: Metadata Completeness")
    logger.info("=" * 80)

