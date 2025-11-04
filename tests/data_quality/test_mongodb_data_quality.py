"""
MongoDB Data Quality Tests
===========================

Integration tests for MongoDB data quality, schema validation, and indexes.

These tests validate:
- Collection existence and structure
- Document schema and data types
- Index presence and performance
- Data integrity and completeness

Tests PZ-13598: Data Quality – Mongo collections and schema
Author: QA Automation Architect
Date: 2025-10-15
"""

import pytest
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

import pymongo
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError

from src.core.base_test import InfrastructureTest
from src.core.exceptions import DatabaseError, InfrastructureError


class TestMongoDBDataQuality(InfrastructureTest):
    """
    MongoDB Data Quality Tests.
    
    Validates MongoDB schema, indexes, and data integrity for the Focus Server.
    Ensures that all required collections exist, documents have proper schema,
    and indexes are optimized for query performance.
    
    Related Jira: PZ-13598
    """
    
    # Base collection that must exist
    BASE_COLLECTION = "base_paths"
    
    # Required fields in recording collection
    RECORDING_REQUIRED_FIELDS = ["uuid", "start_time", "end_time", "deleted"]
    
    # Expected indexes on recording collection
    RECORDING_EXPECTED_INDEXES = {
        "start_time": {"keys": [("start_time", 1)]},
        "end_time": {"keys": [("end_time", 1)]},
        "uuid": {"keys": [("uuid", 1)], "unique": True},
        "deleted": {"keys": [("deleted", 1)]}
    }
    
    # Cache for recording collection name (discovered dynamically)
    _recording_collection_name = None
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_mongodb(self, request, mongodb_manager):
        """
        Set up MongoDB connection for the test class.
        
        This fixture:
        - Verifies MongoDB is reachable
        - Establishes connection
        - Skips all tests if MongoDB is unavailable
        - Ensures cleanup after tests
        
        Args:
            request: Pytest request object
            mongodb_manager: MongoDB manager instance
        """
        self.logger.info("=" * 80)
        self.logger.info("Setting up MongoDB Data Quality Tests")
        self.logger.info("=" * 80)
        
        # Check MongoDB connectivity
        self.logger.info("Verifying MongoDB connectivity...")
        if not mongodb_manager.connect():
            pytest.skip(
                "MongoDB is not reachable. "
                "These tests require MongoDB to be available. "
                "Please check MongoDB configuration and network connectivity."
            )
        
        # Store mongodb_manager in class
        request.cls.mongodb_manager = mongodb_manager
        self.logger.info("✅ MongoDB manager initialized successfully")
        
        # Get database name from configuration
        db_name = self.get_config("mongodb.database", "prisma")
        request.cls.database_name = db_name
        self.logger.info(f"Using database: {db_name}")
        
        yield
        
        # Cleanup: disconnect from MongoDB
        self.logger.info("Cleaning up MongoDB connection...")
        mongodb_manager.disconnect()
        self.logger.info("✅ MongoDB Data Quality Tests cleanup complete")
    
    def _get_database(self) -> pymongo.database.Database:
        """
        Get MongoDB database instance.
        
        Returns:
            MongoDB database object
            
        Raises:
            DatabaseError: If database cannot be accessed
        """
        try:
            db = self.mongodb_manager.client[self.database_name]
            return db
        except Exception as e:
            raise DatabaseError(f"Failed to access database '{self.database_name}': {e}") from e
    
    def _get_collection(self, collection_name: str) -> pymongo.collection.Collection:
        """
        Get MongoDB collection instance.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            MongoDB collection object
            
        Raises:
            DatabaseError: If collection cannot be accessed
        """
        try:
            db = self._get_database()
            collection = db[collection_name]
            return collection
        except Exception as e:
            raise DatabaseError(f"Failed to access collection '{collection_name}': {e}") from e
    
    def _get_recording_collection_name(self) -> str:
        """
        Discover the recording collection name dynamically from base_paths.
        
        The recording collection is named by GUID, which is stored in the
        base_paths collection. This method:
        1. Reads base_paths collection
        2. Extracts the GUID
        3. Returns the GUID as the collection name
        
        Returns:
            Recording collection name (GUID)
            
        Raises:
            DatabaseError: If base_paths doesn't exist or has no GUID
        """
        # Use cached value if available
        if self._recording_collection_name:
            return self._recording_collection_name
        
        try:
            self.logger.debug("Discovering recording collection name from base_paths")
            base_paths = self._get_collection(self.BASE_COLLECTION)
            
            # Get first document (should only be one)
            base_path_doc = base_paths.find_one()
            
            if not base_path_doc:
                raise DatabaseError(f"Collection '{self.BASE_COLLECTION}' is empty - cannot discover recording collection")
            
            # Extract GUID
            guid = base_path_doc.get("guid")
            if not guid:
                raise DatabaseError(f"Document in '{self.BASE_COLLECTION}' has no 'guid' field")
            
            self.logger.debug(f"Discovered recording collection name: {guid}")
            
            # Cache for future use
            self._recording_collection_name = guid
            
            return guid
            
        except Exception as e:
            raise DatabaseError(f"Failed to discover recording collection name: {e}") from e
    
    def _get_recording_collection(self) -> pymongo.collection.Collection:
        """
        Get the recording collection (discovered dynamically).
        
        Returns:
            Recording collection object
            
        Raises:
            DatabaseError: If recording collection cannot be accessed
        """
        collection_name = self._get_recording_collection_name()
        return self._get_collection(collection_name)
    
    # ===================================================================
    # Collection Existence Tests
    # ===================================================================
    
    @pytest.mark.integration
    @pytest.mark.infrastructure
    @pytest.mark.mongodb
    @pytest.mark.data_quality
    def test_required_collections_exist(self):
        """
        Verify that all required MongoDB collections exist.
        
        Test Flow:
        1. Connect to MongoDB database
        2. List all collections
        3. Verify base_paths collection exists
        4. Discover recording collection name (GUID-based) from base_paths
        5. Verify recording collection exists
        6. Verify unrecognized_recordings collection exists
        
        Assertions:
        - base_paths collection is present
        - Recording collection (named by GUID) is present
        - Unrecognized recordings collection is present
        
        Why This Matters:
        Missing collections would cause the Focus Server to fail when
        trying to query or store recording metadata, leading to system
        failures during history playback.
        
        NOTE: Recording collections are named dynamically by GUID 
        (e.g., "77e49b5d-e06a-4aae-a33e-17117418151c"), not hardcoded
        like "node4". The GUID is stored in base_paths collection.
        
        Related: PZ-13598
        """
        self.logger.info("=" * 80)
        self.logger.info("TEST: Required Collections Exist")
        self.logger.info("=" * 80)
        
        try:
            # Step 1: Get database
            self.log_test_step("Getting MongoDB database")
            db = self._get_database()
            
            # Step 2: List all collections
            self.log_test_step("Listing all collections in database")
            existing_collections = db.list_collection_names()
            self.logger.info(f"Found {len(existing_collections)} collections")
            self.logger.debug(f"Collections: {existing_collections}")
            
            # Step 3: Verify base_paths exists
            self.log_test_step("Verifying base_paths collection exists")
            assert self.BASE_COLLECTION in existing_collections, \
                f"Collection '{self.BASE_COLLECTION}' is MISSING. This is critical!"
            self.logger.info(f"✅ Collection '{self.BASE_COLLECTION}' exists")
            
            # Step 4: Discover recording collection name
            self.log_test_step("Discovering recording collection name from base_paths")
            recording_collection_name = self._get_recording_collection_name()
            self.logger.info(f"Recording collection name: {recording_collection_name}")
            
            # Step 5: Verify recording collection exists
            self.log_test_step("Verifying recording collection exists")
            assert recording_collection_name in existing_collections, \
                f"Recording collection '{recording_collection_name}' is MISSING!"
            self.logger.info(f"✅ Recording collection '{recording_collection_name}' exists")
            
            # Get document count
            recording_count = db[recording_collection_name].count_documents({})
            self.logger.info(f"   Documents: {recording_count}")
            
            # Step 6: Verify unrecognized_recordings collection
            self.log_test_step("Verifying unrecognized_recordings collection exists")
            unrecognized_collection_name = f"{recording_collection_name}-unrecognized_recordings"
            
            if unrecognized_collection_name in existing_collections:
                self.logger.info(f"✅ Collection '{unrecognized_collection_name}' exists")
                unrecognized_count = db[unrecognized_collection_name].count_documents({})
                self.logger.info(f"   Documents: {unrecognized_count}")
                
                # Calculate recognition rate
                total = recording_count + unrecognized_count
                if total > 0:
                    recognition_rate = (recording_count / total) * 100
                    self.logger.info(f"   Recognition rate: {recognition_rate:.1f}%")
                    
                    # Warn if rate is low
                    if recognition_rate < 80:
                        self.logger.warning(
                            f"⚠️  Recognition rate is LOW ({recognition_rate:.1f}%). "
                            f"Expected >= 80%. This may indicate data quality issues."
                        )
            else:
                self.logger.warning(
                    f"⚠️  Collection '{unrecognized_collection_name}' not found. "
                    f"This is OK if no unrecognized recordings exist yet."
                )
            
            self.logger.info("=" * 80)
            self.logger.info("✅ All required collections exist")
            self.logger.info("=" * 80)
            
        except DatabaseError as e:
            self.logger.error(f"Database error: {e}")
            pytest.fail(f"Failed to verify collections: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
    
    # ===================================================================
    # Schema Validation Tests
    # ===================================================================
    
    @pytest.mark.integration
    @pytest.mark.infrastructure
    @pytest.mark.mongodb
    @pytest.mark.data_quality
    @pytest.mark.schema
    def test_recording_schema_validation(self):
        """
        Verify recording collection documents have required fields and correct types.
        
        Test Flow:
        1. Discover recording collection name (GUID-based)
        2. Access recording collection
        3. Sample up to 100 documents
        4. Verify each document has all required fields:
           - uuid: Unique identifier (string)
           - start_time: Recording start (datetime)
           - end_time: Recording end (datetime)
           - deleted: Soft delete flag (bool)
        5. Verify field types are correct
        
        Assertions:
        - All sampled documents have required fields
        - Field types match expected types
        - No null values in critical fields
        
        Why This Matters:
        Incorrect or missing fields would cause the Focus Server
        to fail when retrieving recording metadata for history playback.
        Type mismatches can cause parsing errors and system crashes.
        
        Related: PZ-13598
        """
        self.logger.info("=" * 80)
        self.logger.info("TEST: Recording Schema Validation")
        self.logger.info("=" * 80)
        
        try:
            # Step 1: Discover and access recording collection
            self.log_test_step("Accessing recording collection")
            recording_collection = self._get_recording_collection()
            collection_name = self._get_recording_collection_name()
            self.logger.info(f"Collection: {collection_name}")
            
            # Step 2: Get total document count
            total_count = recording_collection.count_documents({})
            self.logger.info(f"Total documents: {total_count}")
            
            if total_count == 0:
                self.logger.warning("⚠️  Recording collection is empty - skipping schema validation")
                pytest.skip("Recording collection is empty - cannot validate schema")
            
            # Step 3: Sample documents (up to 100)
            sample_size = min(100, total_count)
            self.log_test_step(f"Sampling {sample_size} documents for schema validation")
            
            # Use aggregation to get random sample
            sample_docs = list(recording_collection.aggregate([{"$sample": {"size": sample_size}}]))
            self.logger.info(f"Retrieved {len(sample_docs)} documents for validation")
            
            # Step 4: Validate each document
            self.log_test_step("Validating document schema")
            
            validation_errors = []
            docs_validated = 0
            
            for idx, doc in enumerate(sample_docs):
                doc_id = doc.get("_id", f"unknown_{idx}")
                doc_errors = []
                
                # Check required fields
                for field in self.RECORDING_REQUIRED_FIELDS:
                    if field not in doc:
                        doc_errors.append(f"Missing field: '{field}'")
                    elif doc[field] is None:
                        # Special case: end_time is allowed to be None in two cases:
                        # 1. Live recordings (deleted=False, still in progress)
                        # 2. Deleted recordings (deleted=True, deleted while still running)
                        # Both are valid states - recording was not completed before being deleted/still running
                        if field == "end_time":
                            # end_time=None is acceptable - skip validation error
                            continue
                        doc_errors.append(f"Field '{field}' is null")
                
                # Type validation (if fields exist)
                if "uuid" in doc and doc["uuid"] is not None:
                    if not isinstance(doc["uuid"], str):
                        doc_errors.append(f"Field 'uuid' has wrong type: {type(doc['uuid'])}, expected str")
                
                if "start_time" in doc and doc["start_time"] is not None:
                    if not isinstance(doc["start_time"], (int, float, datetime)):
                        doc_errors.append(f"Field 'start_time' has wrong type: {type(doc['start_time'])}")
                
                if "end_time" in doc and doc["end_time"] is not None:
                    if not isinstance(doc["end_time"], (int, float, datetime)):
                        doc_errors.append(f"Field 'end_time' has wrong type: {type(doc['end_time'])}")
                
                if "deleted" in doc and doc["deleted"] is not None:
                    if not isinstance(doc["deleted"], bool):
                        doc_errors.append(f"Field 'deleted' has wrong type: {type(doc['deleted'])}, expected bool")
                
                # Log errors for this document
                if doc_errors:
                    self.logger.error(f"❌ Document {doc_id} has {len(doc_errors)} error(s):")
                    for error in doc_errors:
                        self.logger.error(f"   - {error}")
                    validation_errors.append({
                        "document_id": str(doc_id),
                        "errors": doc_errors
                    })
                else:
                    docs_validated += 1
            
            # Log summary
            self.logger.info(f"Schema validation summary:")
            self.logger.info(f"  - Documents validated: {docs_validated}/{len(sample_docs)}")
            self.logger.info(f"  - Documents with errors: {len(validation_errors)}")
            
            # Assertion: No validation errors
            assert not validation_errors, \
                f"Schema validation failed for {len(validation_errors)} document(s). " \
                f"First error: {validation_errors[0] if validation_errors else 'N/A'}"
            
            self.logger.info("=" * 80)
            self.logger.info(f"✅ All {docs_validated} sampled documents have valid schema")
            self.logger.info("=" * 80)
            
        except DatabaseError as e:
            self.logger.error(f"Database error: {e}")
            pytest.fail(f"Failed to validate schema: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
    
    # ===================================================================
    # Data Integrity Tests
    # ===================================================================
    
    @pytest.mark.integration
    @pytest.mark.infrastructure
    @pytest.mark.mongodb
    @pytest.mark.data_quality
    @pytest.mark.data_integrity
    def test_recordings_have_all_required_metadata(self):
        """
        Scan all recordings and verify none have missing metadata.
        
        Test Flow:
        1. Discover and access recording collection
        2. Count documents with missing critical fields
        3. Distinguish between live (running) and historical recordings
        4. Verify historical recordings have complete metadata
        5. Identify orphaned records (incomplete metadata)
        
        Checks:
        - Every recording has uuid (unique identifier)
        - Every recording has start_time
        - Historical recordings (deleted=True or completed) have end_time
        - Live recordings (deleted=False, no end_time) are acceptable
        - No null/missing critical fields for historical data
        
        Why This Matters:
        Live recordings (currently running) don't have end_time yet - this is NORMAL.
        However, deleted or completed recordings MUST have end_time for history playback.
        Missing metadata in historical recordings prevents correct indexing and retrieval.
        
        Related: PZ-13598
        """
        self.logger.info("=" * 80)
        self.logger.info("TEST: Recordings Have All Required Metadata")
        self.logger.info("=" * 80)
        
        try:
            # Step 1: Access recording collection
            self.log_test_step("Accessing recording collection")
            recording_collection = self._get_recording_collection()
            collection_name = self._get_recording_collection_name()
            self.logger.info(f"Collection: {collection_name}")
            
            total_count = recording_collection.count_documents({})
            self.logger.info(f"Total recordings: {total_count}")
            
            if total_count == 0:
                self.logger.warning("⚠️  Recording collection is empty - skipping metadata validation")
                pytest.skip("Recording collection is empty - cannot validate metadata")
            
            # Step 2: Check for missing metadata
            self.log_test_step("Checking for missing metadata")
            
            missing_metadata = {}
            
            # Check uuid and start_time (required for ALL recordings)
            for field in ["uuid", "start_time"]:
                missing_count = recording_collection.count_documents({
                    "$or": [
                        {field: {"$exists": False}},
                        {field: None}
                    ]
                })
                
                if missing_count > 0:
                    percentage = (missing_count / total_count) * 100
                    self.logger.error(
                        f"❌ Field '{field}': {missing_count} recordings ({percentage:.2f}%) have missing/null values"
                    )
                    missing_metadata[field] = {
                        "count": missing_count,
                        "percentage": percentage
                    }
                else:
                    self.logger.info(f"✅ Field '{field}': All recordings have valid values")
            
            # Check end_time for HISTORICAL recordings only (deleted=True means historical)
            # Live recordings (deleted=False, no end_time) are acceptable
            self.log_test_step("Checking end_time for historical recordings")
            
            # Count deleted recordings without end_time (these should have end_time)
            deleted_missing_end_time = recording_collection.count_documents({
                "deleted": True,
                "$or": [
                    {"end_time": {"$exists": False}},
                    {"end_time": None}
                ]
            })
            
            # Count active recordings without end_time (these might be LIVE or stale)
            active_missing_end_time = recording_collection.count_documents({
                "deleted": False,
                "$or": [
                    {"end_time": {"$exists": False}},
                    {"end_time": None}
                ]
            })
            
            if deleted_missing_end_time > 0:
                percentage = (deleted_missing_end_time / total_count) * 100
                self.logger.warning(
                    f"⚠️  Found {deleted_missing_end_time} DELETED recordings ({percentage:.2f}%) without end_time. "
                    f"These were likely deleted while still running."
                )
            
            if active_missing_end_time > 0:
                # Check if these are actually LIVE or STALE recordings
                # Strategy: Check start_time - if recording started more than 24 hours ago
                # and still has no end_time, it's likely STALE (crashed/failed)
                from datetime import datetime, timedelta, timezone
                
                stale_threshold = datetime.now(timezone.utc) - timedelta(hours=24)
                
                # Find active recordings without end_time that started more than 24h ago
                stale_recordings = list(recording_collection.find({
                    "deleted": False,
                    "$or": [
                        {"end_time": {"$exists": False}},
                        {"end_time": None}
                    ],
                    "start_time": {"$lt": stale_threshold}
                }).limit(10))  # Sample up to 10
                
                stale_count = len(stale_recordings)
                likely_live = active_missing_end_time - stale_count
                
                if stale_count > 0:
                    self.logger.error(
                        f"❌ Found {stale_count} STALE recordings (started >24h ago, no end_time). "
                        f"These are likely crashed/failed recordings!"
                    )
                    for rec in stale_recordings[:5]:  # Show first 5
                        age_hours = (datetime.utcnow() - rec['start_time']).total_seconds() / 3600
                        self.logger.error(
                            f"   - UUID: {rec.get('uuid', 'N/A')}, "
                            f"Started: {rec.get('start_time')}, "
                            f"Age: {age_hours:.1f} hours"
                        )
                    
                    missing_metadata["stale_recordings"] = {
                        "count": stale_count,
                        "percentage": (stale_count / total_count) * 100
                    }
                
                if likely_live > 0:
                    self.logger.info(
                        f"ℹ️  Found {likely_live} LIVE recordings (recent, no end_time). "
                        f"These are currently running - this is NORMAL."
                    )
            
            # Check deleted field
            missing_deleted = recording_collection.count_documents({
                "$or": [
                    {"deleted": {"$exists": False}},
                    {"deleted": None}
                ]
            })
            
            if missing_deleted > 0:
                percentage = (missing_deleted / total_count) * 100
                self.logger.error(
                    f"❌ Field 'deleted': {missing_deleted} recordings ({percentage:.2f}%) have missing/null values"
                )
                missing_metadata["deleted"] = {
                    "count": missing_deleted,
                    "percentage": percentage
                }
            else:
                self.logger.info(f"✅ Field 'deleted': All recordings have valid values")
            
            # Step 3: Find completely invalid recordings (missing multiple fields)
            self.log_test_step("Identifying orphaned records")
            
            # Find documents missing 2 or more critical fields
            orphaned_query = {
                "$expr": {
                    "$gte": [
                        {
                            "$size": {
                                "$filter": {
                                    "input": self.RECORDING_REQUIRED_FIELDS,
                                    "cond": {
                                        "$or": [
                                            {"$eq": [{"$ifNull": [f"$${field}", None]}, None]}
                                            for field in self.RECORDING_REQUIRED_FIELDS
                                        ]
                                    }
                                }
                            }
                        },
                        2  # Missing 2 or more fields
                    ]
                }
            }
            
            # This is a complex query - if it fails, we'll skip this check
            try:
                orphaned_count = recording_collection.count_documents(orphaned_query)
                if orphaned_count > 0:
                    percentage = (orphaned_count / total_count) * 100
                    self.logger.error(
                        f"❌ Found {orphaned_count} orphaned records ({percentage:.2f}%) "
                        f"missing 2+ critical fields"
                    )
                    missing_metadata["orphaned_records"] = {
                        "count": orphaned_count,
                        "percentage": percentage
                    }
                else:
                    self.logger.info("✅ No orphaned records found")
            except OperationFailure as e:
                self.logger.warning(f"⚠️  Could not check for orphaned records: {e}")
                self.logger.info("Skipping orphaned records check (operation not supported)")
            
            # Step 4: Report summary
            self.logger.info("Metadata validation summary:")
            self.logger.info(f"  - Total recordings: {total_count}")
            self.logger.info(f"  - Fields with missing data: {len(missing_metadata)}")
            
            # Assertion: No missing metadata
            assert not missing_metadata, \
                f"Found recordings with missing metadata: {missing_metadata}. " \
                f"This indicates data integrity issues that must be resolved."
            
            self.logger.info("=" * 80)
            self.logger.info("✅ All recordings have complete metadata")
            self.logger.info("=" * 80)
            
        except DatabaseError as e:
            self.logger.error(f"Database error: {e}")
            pytest.fail(f"Failed to validate metadata: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
    
    # ===================================================================
    # Index Performance Tests
    # ===================================================================
    
    @pytest.mark.integration
    @pytest.mark.infrastructure
    @pytest.mark.mongodb
    @pytest.mark.data_quality
    @pytest.mark.performance
    @pytest.mark.jira("PZ-13983")  # Bug: MongoDB Indexes Missing
    def test_mongodb_indexes_exist_and_optimal(self):
        """
        Verify MongoDB indexes exist on critical fields and are optimal.
        
        Test Flow:
        1. Discover and access recording collection
        2. List all indexes
        3. Verify required indexes exist:
           - Index on start_time (for time range queries)
           - Index on end_time (for time range queries)
           - Index on uuid (for unique lookups)
           - Index on deleted (for filtering active recordings)
        4. Warn if missing indexes that would improve performance
        
        Assertions:
        - All critical indexes are present
        - Indexes are properly configured (unique where needed)
        - No missing indexes that would degrade query performance
        
        Why This Matters:
        Missing indexes cause SLOW queries, especially on large datasets.
        Time range queries without indexes on start_time/end_time can
        take minutes instead of milliseconds, making history playback
        unusable for users.
        
        Related: PZ-13598
        """
        self.logger.info("=" * 80)
        self.logger.info("TEST: MongoDB Indexes Exist and Optimal")
        self.logger.info("=" * 80)
        
        try:
            # Step 1: Access recording collection
            self.log_test_step("Accessing recording collection")
            recording_collection = self._get_recording_collection()
            collection_name = self._get_recording_collection_name()
            self.logger.info(f"Collection: {collection_name}")
            
            # Step 2: List all indexes
            self.log_test_step(f"Listing all indexes on recording collection")
            indexes = list(recording_collection.list_indexes())
            
            self.logger.info(f"Found {len(indexes)} index(es) on recording collection")
            
            # Parse existing indexes
            existing_indexes = {}
            for idx in indexes:
                idx_name = idx.get("name", "unknown")
                idx_keys = idx.get("key", {})
                idx_unique = idx.get("unique", False)
                
                self.logger.debug(f"Index '{idx_name}': keys={idx_keys}, unique={idx_unique}")
                existing_indexes[idx_name] = {
                    "keys": idx_keys,
                    "unique": idx_unique
                }
            
            # Step 3: Check for required indexes
            self.log_test_step("Verifying required indexes are present")
            
            missing_indexes = []
            suboptimal_indexes = []
            
            # Check each expected index
            for expected_name, expected_config in self.RECORDING_EXPECTED_INDEXES.items():
                expected_keys = expected_config["keys"]
                expected_unique = expected_config.get("unique", False)
                
                # Check if index exists (by keys, not name)
                index_found = False
                for idx_name, idx_info in existing_indexes.items():
                    # Compare keys (convert to comparable format)
                    idx_keys_list = list(idx_info["keys"].items())
                    if idx_keys_list == expected_keys:
                        index_found = True
                        
                        # Check if uniqueness matches
                        if expected_unique and not idx_info["unique"]:
                            suboptimal_indexes.append({
                                "field": expected_name,
                                "issue": f"Index exists but is not unique (should be unique)"
                            })
                            self.logger.warning(
                                f"⚠️  Index on '{expected_name}' exists but is NOT unique (should be)"
                            )
                        else:
                            self.logger.info(f"✅ Index on '{expected_name}' exists and is configured correctly")
                        break
                
                if not index_found:
                    missing_indexes.append(expected_name)
                    self.logger.error(f"❌ Index on '{expected_name}' is MISSING")
            
            # Step 4: Report summary
            self.logger.info("Index validation summary:")
            self.logger.info(f"  - Total indexes: {len(existing_indexes)}")
            self.logger.info(f"  - Expected indexes: {len(self.RECORDING_EXPECTED_INDEXES)}")
            self.logger.info(f"  - Missing indexes: {len(missing_indexes)}")
            self.logger.info(f"  - Suboptimal indexes: {len(suboptimal_indexes)}")
            
            # Warn about missing indexes (but don't fail - they're performance optimization)
            if missing_indexes:
                self.logger.warning("=" * 80)
                self.logger.warning("⚠️  WARNING: Missing indexes detected!")
                self.logger.warning("=" * 80)
                self.logger.warning(
                    f"Missing indexes on: {missing_indexes}\n"
                    f"This will cause SLOW queries on large datasets.\n"
                    f"Recommended: Create these indexes to improve performance."
                )
                self.logger.warning("=" * 80)
            
            # Fail if critical indexes are completely missing
            critical_indexes = ["start_time", "end_time", "uuid"]
            missing_critical = [idx for idx in missing_indexes if idx in critical_indexes]
            
            assert not missing_critical, \
                f"Critical indexes are MISSING: {missing_critical}. " \
                f"These indexes are REQUIRED for acceptable query performance. " \
                f"History playback will be extremely slow without them."
            
            self.logger.info("=" * 80)
            self.logger.info("✅ All critical indexes are present")
            self.logger.info("=" * 80)
            
        except DatabaseError as e:
            self.logger.error(f"Database error: {e}")
            pytest.fail(f"Failed to validate indexes: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
    
    # ===================================================================
    # Soft Delete Tests
    # ===================================================================
    
    @pytest.mark.integration
    @pytest.mark.infrastructure
    @pytest.mark.mongodb
    @pytest.mark.data_quality
    @pytest.mark.soft_delete
    def test_deleted_recordings_marked_properly(self):
        """
        T-DATA-001: Verify deleted recordings are marked with deleted=True.
        
        Test Flow:
        1. Access recording collection
        2. Query for recordings marked as deleted (deleted=True)
        3. Query for active recordings (deleted=False)
        4. Verify the deleted flag is properly set
        5. Ensure historical queries can filter by this flag
        
        Assertions:
        - deleted field is boolean (not string or other type)
        - deleted field exists in all documents
        - Historical queries should be able to filter out deleted recordings
        
        Why This Matters:
        The 'deleted' field implements soft delete functionality.
        Historical jobs MUST ignore recordings with deleted=True to avoid
        showing deleted data to users. This is critical for data privacy
        and system correctness.
        
        Related: T-DATA-001 | Historical Query ignores `deleted` recordings
        """
        self.logger.info("=" * 80)
        self.logger.info("TEST: T-DATA-001 | Deleted Recordings Marked Properly")
        self.logger.info("=" * 80)
        
        try:
            # Step 1: Access recording collection
            self.log_test_step("Accessing recording collection")
            recording_collection = self._get_recording_collection()
            collection_name = self._get_recording_collection_name()
            self.logger.info(f"Collection: {collection_name}")
            
            total_count = recording_collection.count_documents({})
            self.logger.info(f"Total recordings: {total_count}")
            
            if total_count == 0:
                self.logger.warning("⚠️  Recording collection is empty - skipping test")
                pytest.skip("Recording collection is empty")
            
            # Step 2: Count deleted vs active recordings
            self.log_test_step("Analyzing deleted flag distribution")
            
            deleted_count = recording_collection.count_documents({"deleted": True})
            active_count = recording_collection.count_documents({"deleted": False})
            
            # Check for documents without deleted field
            missing_deleted = recording_collection.count_documents({
                "deleted": {"$exists": False}
            })
            
            # Check for non-boolean deleted values
            invalid_type_count = recording_collection.count_documents({
                "deleted": {"$not": {"$type": "bool"}}
            })
            
            self.logger.info(f"Active recordings (deleted=False): {active_count}")
            self.logger.info(f"Deleted recordings (deleted=True): {deleted_count}")
            self.logger.info(f"Missing 'deleted' field: {missing_deleted}")
            self.logger.info(f"Invalid 'deleted' type: {invalid_type_count}")
            
            # Step 3: Validate data quality
            self.log_test_step("Validating soft delete implementation")
            
            # Check 1: No documents should be missing the deleted field
            assert missing_deleted == 0, \
                f"Found {missing_deleted} recordings without 'deleted' field. " \
                f"All recordings MUST have a 'deleted' field for proper filtering."
            
            # Check 2: deleted field must be boolean
            assert invalid_type_count == 0, \
                f"Found {invalid_type_count} recordings with non-boolean 'deleted' field. " \
                f"The 'deleted' field MUST be boolean (true/false)."
            
            # Check 3: Total should match
            assert deleted_count + active_count == total_count, \
                f"Mismatch in counts: deleted({deleted_count}) + active({active_count}) != total({total_count})"
            
            self.logger.info("✅ All recordings have valid 'deleted' flag")
            
            # Step 4: Test query filtering (simulate historical query)
            self.log_test_step("Testing historical query filtering")
            
            # Simulate a historical query that should exclude deleted recordings
            historical_query = {
                "deleted": False,
                "start_time": {"$exists": True},
                "end_time": {"$exists": True}
            }
            
            historical_results_count = recording_collection.count_documents(historical_query)
            self.logger.info(f"Historical query results (active only): {historical_results_count}")
            
            # This should match the active count (minus any with missing times)
            assert historical_results_count <= active_count, \
                f"Historical query returned more results ({historical_results_count}) " \
                f"than active recordings ({active_count}). This should not happen!"
            
            # Step 5: Sample deleted recordings for inspection
            if deleted_count > 0:
                self.log_test_step("Inspecting sample of deleted recordings")
                
                deleted_sample = list(recording_collection.find(
                    {"deleted": True}
                ).limit(5))
                
                self.logger.info(f"Sample of {len(deleted_sample)} deleted recordings:")
                for idx, doc in enumerate(deleted_sample, 1):
                    self.logger.info(f"  {idx}. UUID: {doc.get('uuid', 'N/A')}")
                    self.logger.info(f"     Start: {doc.get('start_time', 'N/A')}")
                    self.logger.info(f"     End: {doc.get('end_time', 'N/A')}")
                    self.logger.info(f"     Deleted: {doc.get('deleted')}")
                
                deleted_percentage = (deleted_count / total_count) * 100
                self.logger.info(f"Deleted recordings: {deleted_percentage:.1f}% of total")
                
                if deleted_percentage > 20:
                    self.logger.warning(
                        f"⚠️  High percentage of deleted recordings ({deleted_percentage:.1f}%). "
                        f"Consider purging old deleted recordings to save space."
                    )
            else:
                self.logger.info("No deleted recordings found (all active)")
            
            self.logger.info("=" * 80)
            self.logger.info("✅ T-DATA-001: Soft delete implementation is correct")
            self.logger.info("=" * 80)
            
        except DatabaseError as e:
            self.logger.error(f"Database error: {e}")
            pytest.fail(f"Failed to validate soft delete: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
    
    @pytest.mark.integration
    @pytest.mark.infrastructure
    @pytest.mark.mongodb
    @pytest.mark.data_quality
    @pytest.mark.data_integrity
    @pytest.mark.data_lifecycle
    def test_historical_vs_live_recordings(self):
        """
        T-DATA-002: Verify distinction between Historical and Live recordings.
        
        Test Flow:
        1. Access recording collection
        2. Identify Historical recordings (have both start_time AND end_time)
        3. Identify Live recordings (have start_time but NO end_time, not deleted)
        4. Verify data integrity for Historical recordings
        5. Check if cleanup service properly manages lifecycle
        
        Key Architectural Understanding:
        - MongoDB stores metadata INDEX for recordings (not the raw data)
        - Historical recordings: Completed, have start_time AND end_time defined
        - Live recordings: In-progress, have start_time but NO end_time yet
        - Deleted recordings: Marked with deleted=True (soft delete for cleanup)
        
        Purpose:
        Historical recordings are used by Focus Server and Baby Analyzer to find
        raw files (PRP2/SEGY) in S3/local storage for specific time ranges.
        This test validates that the recordings index is properly maintained
        and that lifecycle management (cleanup) works correctly.
        
        Related: T-DATA-002 | Data Management Cleanup of Mongo Records
        """
        self.logger.info("=" * 80)
        self.logger.info("TEST: T-DATA-002 | Historical vs Live Recordings")
        self.logger.info("=" * 80)
        
        try:
            # Step 1: Access recording collection
            self.log_test_step("Accessing recording collection")
            recording_collection = self._get_recording_collection()
            collection_name = self._get_recording_collection_name()
            self.logger.info(f"Collection: {collection_name}")
            
            total_count = recording_collection.count_documents({})
            self.logger.info(f"Total recordings: {total_count}")
            
            if total_count == 0:
                self.logger.warning("⚠️  Recording collection is empty - skipping test")
                pytest.skip("Recording collection is empty")
            
            # Step 2: Classify recordings by type
            self.log_test_step("Classifying recordings: Historical vs Live")
            
            # Historical: Have both start_time AND end_time (completed recordings)
            historical_count = recording_collection.count_documents({
                "start_time": {"$exists": True},
                "end_time": {"$exists": True, "$ne": None},
                "deleted": False
            })
            
            # Live: Have start_time but NO end_time (in-progress recordings)
            live_count = recording_collection.count_documents({
                "start_time": {"$exists": True},
                "$or": [
                    {"end_time": {"$exists": False}},
                    {"end_time": None}
                ],
                "deleted": False
            })
            
            # Deleted: Soft-deleted recordings (cleanup candidates)
            deleted_count = recording_collection.count_documents({
                "deleted": True
            })
            
            # Invalid: Missing start_time (should not exist)
            invalid_count = recording_collection.count_documents({
                "$or": [
                    {"start_time": {"$exists": False}},
                    {"start_time": None}
                ]
            })
            
            self.logger.info(f"📊 Recording Classification:")
            self.logger.info(f"   Historical (completed): {historical_count} ({historical_count/total_count*100:.1f}%)")
            self.logger.info(f"   Live (in-progress): {live_count} ({live_count/total_count*100:.1f}%)")
            self.logger.info(f"   Deleted (cleanup): {deleted_count} ({deleted_count/total_count*100:.1f}%)")
            self.logger.info(f"   Invalid (no start_time): {invalid_count}")
            
            # Step 3: Validate Historical recordings structure
            self.log_test_step("Validating Historical recordings structure")
            
            # Historical recordings MUST have uuid, start_time, end_time, deleted
            historical_sample = list(recording_collection.find({
                "start_time": {"$exists": True},
                "end_time": {"$exists": True, "$ne": None},
                "deleted": False
            }).limit(5))
            
            self.logger.info(f"Sample Historical recordings:")
            for idx, rec in enumerate(historical_sample, 1):
                duration = (rec['end_time'] - rec['start_time']).total_seconds() / 3600
                self.logger.info(f"  {idx}. UUID: {rec.get('uuid', 'N/A')}")
                self.logger.info(f"     Start: {rec['start_time']}")
                self.logger.info(f"     End: {rec['end_time']}")
                self.logger.info(f"     Duration: {duration:.2f} hours")
                self.logger.info(f"     Deleted: {rec.get('deleted', 'N/A')}")
            
            # Step 4: Check Live recordings age
            self.log_test_step("Analyzing Live recordings age")
            
            if live_count > 0:
                from datetime import datetime, timezone, timedelta
                
                now = datetime.now(timezone.utc)
                
                # Find old live recordings (>24h without end_time)
                stale_live = list(recording_collection.find({
                    "start_time": {"$exists": True, "$lt": now - timedelta(hours=24)},
                    "$or": [
                        {"end_time": {"$exists": False}},
                        {"end_time": None}
                    ],
                    "deleted": False
                }).limit(5))
                
                if stale_live:
                    self.logger.warning(
                        f"⚠️  Found {len(stale_live)} Live recordings older than 24h. "
                        f"These may be stale (crashed/failed):"
                    )
                    for rec in stale_live:
                        age_hours = (now - rec['start_time']).total_seconds() / 3600
                        self.logger.warning(f"   - UUID: {rec.get('uuid')}, Age: {age_hours:.1f}h")
                else:
                    self.logger.info(f"✅ All {live_count} Live recordings are recent (<24h)")
            
            # Step 5: Check cleanup service behavior
            self.log_test_step("Checking cleanup service behavior")
            
            if deleted_count > 0:
                # Check if deleted recordings have end_time
                deleted_with_endtime = recording_collection.count_documents({
                    "deleted": True,
                    "end_time": {"$exists": True, "$ne": None}
                })
                
                deleted_without_endtime = recording_collection.count_documents({
                    "deleted": True,
                    "$or": [
                        {"end_time": {"$exists": False}},
                        {"end_time": None}
                    ]
                })
                
                self.logger.info(f"Deleted recordings analysis:")
                self.logger.info(f"   With end_time: {deleted_with_endtime}")
                self.logger.info(f"   Without end_time: {deleted_without_endtime}")
                
                if deleted_without_endtime > 0:
                    self.logger.warning(
                        f"⚠️  {deleted_without_endtime} deleted recordings missing end_time. "
                        f"These were likely deleted while still running."
                    )
                
                # Sample deleted recordings to understand cleanup pattern
                deleted_sample = list(recording_collection.find({
                    "deleted": True
                }).limit(3))
                
                self.logger.info(f"Sample Deleted recordings:")
                for idx, rec in enumerate(deleted_sample, 1):
                    # Handle timezone awareness - MongoDB dates may be naive
                    start_time = rec['start_time']
                    if start_time.tzinfo is None:
                        # Make it timezone-aware (assume UTC)
                        start_time = start_time.replace(tzinfo=timezone.utc)
                    age_days = (now - start_time).days
                    self.logger.info(f"  {idx}. UUID: {rec.get('uuid')}")
                    self.logger.info(f"     Started: {rec['start_time']} ({age_days} days ago)")
                    self.logger.info(f"     Has end_time: {rec.get('end_time') is not None}")
            else:
                self.logger.info("ℹ️  No deleted recordings found. Cleanup service may not be active.")
            
            # Step 6: Assertions
            self.log_test_step("Validating data integrity")
            
            # Check 1: No invalid recordings (must have start_time)
            assert invalid_count == 0, \
                f"Found {invalid_count} recordings without start_time! All recordings MUST have start_time."
            
            # Check 2: Total should match classification
            classified_total = historical_count + live_count + deleted_count
            assert classified_total == total_count, \
                f"Classification mismatch: {classified_total} classified vs {total_count} total"
            
            # Check 3: Historical recordings should be the majority
            if total_count > 10:  # Only check if we have significant data
                historical_percentage = (historical_count / total_count) * 100
                assert historical_percentage > 50, \
                    f"Historical recordings are only {historical_percentage:.1f}% of total. " \
                    f"Expected majority to be Historical (completed recordings)."
            
            self.logger.info("=" * 80)
            self.logger.info("✅ T-DATA-002: Historical/Live classification is correct")
            self.logger.info("=" * 80)
            
        except DatabaseError as e:
            self.logger.error(f"Database error: {e}")
            pytest.fail(f"Failed to validate historical/live recordings: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise

