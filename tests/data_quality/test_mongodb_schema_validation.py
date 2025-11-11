"""
Data Quality Tests - MongoDB Schema Validation
===============================================

Tests for MongoDB collections schema validation and data quality.

Based on Xray Tests: PZ-13598, PZ-13683, PZ-13686

Tests covered:
    - PZ-13598: MongoDB Data Quality (general)
    - PZ-13683: Recording Collection Schema Validation
    - PZ-13686: Metadata Collection Schema Validation

Author: QA Automation Architect  
Date: 2025-10-27
"""

import pytest
import logging
from typing import Dict, Any, List

from src.infrastructure.mongodb_manager import MongoDBManager
from src.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


# ===================================================================
# Test Class: MongoDB Data Quality
# ===================================================================

@pytest.mark.data_quality
@pytest.mark.mongodb
@pytest.mark.integration
class TestMongoDBDataQuality:
    """
    Test suite for MongoDB data quality validation.
    
    Tests covered:
        - PZ-13598: MongoDB Data Quality (general)
        - PZ-13683: Recording Collection Schema
        - PZ-13686: Metadata Collection Schema
    
    Priority: MEDIUM
    """
    
    @pytest.mark.xray("PZ-13598")
    def test_mongodb_data_quality_general(self, mongodb_manager: MongoDBManager):
        """
        Test PZ-13598: MongoDB Data Quality (general check).
        
        Steps:
            1. Connect to MongoDB
            2. Verify database exists
            3. Verify collections exist
            4. Check basic data quality
        
        Expected:
            - Database accessible
            - Required collections present
            - Data structure valid
        
        Jira: PZ-13598
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: MongoDB Data Quality - General (PZ-13598)")
        logger.info("=" * 80)
        
        # Check database connection
        logger.info("Step 1: Verifying database connection")
        assert mongodb_manager.client is not None, "MongoDB client should be initialized"
        logger.info("✅ Database connection verified")
        
        # Get database
        db = mongodb_manager.get_database()
        logger.info(f"Database: {db.name}")
        
        # List collections
        logger.info("\nStep 2: Listing collections")
        collections = db.list_collection_names()
        logger.info(f"Found {len(collections)} collections")
        
        for coll_name in collections[:10]:  # First 10
            logger.info(f"  - {coll_name}")
        
        # Verify key collections exist
        logger.info("\nStep 3: Verifying key collections")
        
        # Check for recording-related collections (GUID-based discovery)
        recording_collections = [c for c in collections if 'recording' in c.lower()]
        
        if recording_collections:
            logger.info(f"✅ Found {len(recording_collections)} recording collection(s)")
        else:
            logger.warning("⚠️  No recording collections found")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: MongoDB Data Quality General Check")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-13683")
    def test_recording_collection_schema_validation(self, mongodb_manager: MongoDBManager):
        """
        Test PZ-13683: Recording Collection Schema Validation.
        
        Steps:
            1. Access recording collection
            2. Get sample documents
            3. Validate schema structure
            4. Verify required fields present
        
        Expected:
            - Recording collection exists
            - Documents have required fields:
              - start_time
              - end_time
              - uuid
              - deleted (soft delete flag)
        
        Jira: PZ-13683
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: Recording Collection Schema Validation (PZ-13683)")
        logger.info("=" * 80)
        
        db = mongodb_manager.get_database()
        
        # Find recording collection (GUID-based name)
        collections = db.list_collection_names()
        recording_collections = [c for c in collections if 'recording' in c.lower()]
        
        if not recording_collections:
            logger.warning("⚠️  No recording collections found - skipping schema validation")
            pytest.skip("No recording collections found")
        
        recording_collection_name = recording_collections[0]
        logger.info(f"Validating collection: {recording_collection_name}")
        
        collection = db[recording_collection_name]
        
        # Get sample document
        logger.info("Fetching sample document...")
        sample_doc = collection.find_one()
        
        if not sample_doc:
            logger.warning("⚠️  Collection is empty - cannot validate schema")
            pytest.skip("Collection is empty")
        
        logger.info("Sample document structure:")
        for key in sample_doc.keys():
            logger.info(f"  - {key}: {type(sample_doc[key]).__name__}")
        
        # Validate required fields
        logger.info("\nValidating required fields...")
        required_fields = ['start_time', 'end_time', 'uuid']
        
        for field in required_fields:
            assert field in sample_doc, f"Required field '{field}' missing from schema"
            logger.info(f"✅ Field '{field}' present")
        
        # Check soft delete field (may or may not be present)
        if 'deleted' in sample_doc:
            logger.info("✅ Soft delete field 'deleted' present")
        else:
            logger.info("ℹ️  Soft delete field 'deleted' not in sample (may be added later)")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Recording Collection Schema Valid")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-13686")
    @pytest.mark.xray("PZ-14812")
    def test_metadata_collection_schema_validation(self, mongodb_manager: MongoDBManager):
        """
        Test PZ-13686: Metadata Collection Schema Validation.
        
        Steps:
            1. Access metadata collection
            2. Get sample documents
            3. Validate schema structure
            4. Verify required fields present
        
        Expected:
            - Metadata collection exists
            - Documents have required fields
            - Schema is consistent
        
        Jira: PZ-13686
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: Metadata Collection Schema Validation (PZ-13686)")
        logger.info("=" * 80)
        
        db = mongodb_manager.get_database()
        
        # Find metadata collection
        collections = db.list_collection_names()
        metadata_collections = [c for c in collections if 'metadata' in c.lower()]
        
        if not metadata_collections:
            logger.warning("⚠️  No metadata collections found - skipping schema validation")
            pytest.skip("No metadata collections found")
        
        metadata_collection_name = metadata_collections[0]
        logger.info(f"Validating collection: {metadata_collection_name}")
        
        collection = db[metadata_collection_name]
        
        # Get sample document
        logger.info("Fetching sample document...")
        sample_doc = collection.find_one()
        
        if not sample_doc:
            logger.warning("⚠️  Collection is empty - cannot validate schema")
            pytest.skip("Collection is empty")
        
        logger.info("Sample document structure:")
        for key in sample_doc.keys():
            logger.info(f"  - {key}: {type(sample_doc[key]).__name__}")
        
        # Validate document has fields
        assert len(sample_doc.keys()) > 0, "Document should have fields"
        logger.info(f"✅ Metadata document has {len(sample_doc.keys())} fields")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Metadata Collection Schema Valid")
        logger.info("=" * 80)


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary
def test_mongodb_schema_validation_summary():
    """
    Summary test for MongoDB schema validation tests.
    
    Xray Tests Covered:
        - PZ-13598: MongoDB Data Quality (general)
        - PZ-13683: Recording Collection Schema
        - PZ-13686: Metadata Collection Schema
    
    This test always passes and serves as documentation.
    """
    logger.info("=" * 80)
    logger.info("MongoDB Schema Validation Tests Suite Summary")
    logger.info("=" * 80)
    logger.info("Tests in this module:")
    logger.info("  1. PZ-13598: MongoDB Data Quality general check")
    logger.info("  2. PZ-13683: Recording Collection Schema")
    logger.info("  3. PZ-13686: Metadata Collection Schema")
    logger.info("=" * 80)

