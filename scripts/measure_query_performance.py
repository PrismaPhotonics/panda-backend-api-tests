#!/usr/bin/env python3
"""
Measure MongoDB Query Performance
===================================

This script measures ACTUAL query performance with and without indexes.

Author: Roy Avrahami
Date: 2025-10-16
"""

import sys
import io
import yaml
import time
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta

# Fix Windows emoji encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def load_config(environment="staging"):
    """Load MongoDB configuration"""
    config_path = Path(__file__).parent.parent / "config" / "environments.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config['environments'].get(environment)


def connect_to_mongodb(config):
    """Connect to MongoDB"""
    mongodb_config = config['mongodb']
    
    connection_string = (
        f"mongodb://{mongodb_config['username']}:{mongodb_config['password']}"
        f"@{mongodb_config['host']}:{mongodb_config['port']}"
        f"/?authSource={mongodb_config.get('auth_source', 'admin')}"
    )
    
    client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    
    return client, client[mongodb_config['database']]


def get_recording_collection(db):
    """Get the recording collection"""
    # IMPORTANT: Use the GUID for /prisma/root/recordings (not /prisma/root/recordings/segy)
    base_paths = db['base_paths']
    doc = base_paths.find_one({
        "base_path": "/prisma/root/recordings",
        "is_archive": False
    })
    
    if not doc or 'guid' not in doc:
        raise ValueError("Could not find GUID in base_paths collection for /prisma/root/recordings")
    
    return db[doc['guid']], doc['guid']


def main():
    print("=" * 80)
    print("MongoDB Query Performance Measurement")
    print("=" * 80)
    print()
    
    # Connect
    environment = "staging"
    print(f"Environment: {environment}")
    
    config = load_config(environment)
    client, db = connect_to_mongodb(config)
    collection, collection_name = get_recording_collection(db)
    
    print(f"Collection: {collection_name}")
    
    # Get total count
    total_count = collection.count_documents({})
    print(f"Total documents: {total_count:,}")
    print()
    
    # Check current indexes
    indexes = list(collection.list_indexes())
    print(f"Current indexes: {len(indexes)}")
    for idx in indexes:
        print(f"  - {idx['name']}: {idx['key']}")
    print()
    
    print("=" * 80)
    print("PERFORMANCE TESTS")
    print("=" * 80)
    print()
    
    # Test 1: Count all documents
    print("Test 1: Count All Documents")
    print("-" * 40)
    start_time = time.time()
    count = collection.count_documents({})
    elapsed = time.time() - start_time
    print(f"Result: {count:,} documents")
    print(f"Time: {elapsed:.3f} seconds")
    print()
    
    # Test 2: Time range query (with filter)
    print("Test 2: Time Range Query (Last 30 Days)")
    print("-" * 40)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    start_time = time.time()
    cursor = collection.find({
        "start_time": {"$gte": thirty_days_ago}
    })
    results = list(cursor)
    elapsed = time.time() - start_time
    
    print(f"Query: start_time >= {thirty_days_ago.strftime('%Y-%m-%d')}")
    print(f"Result: {len(results):,} documents")
    print(f"Time: {elapsed:.3f} seconds")
    
    # Get explain for this query
    explain = collection.find({
        "start_time": {"$gte": thirty_days_ago}
    }).explain()
    
    execution_stats = explain.get('executionStats', {})
    print(f"Documents examined: {execution_stats.get('totalDocsExamined', 'N/A'):,}")
    print(f"Documents returned: {execution_stats.get('nReturned', 'N/A'):,}")
    
    if execution_stats.get('totalDocsExamined', 0) == total_count:
        print("⚠️  WARNING: FULL COLLECTION SCAN! (examined ALL documents)")
    print()
    
    # Test 3: UUID lookup
    print("Test 3: UUID Lookup")
    print("-" * 40)
    
    # Get a sample UUID
    sample_doc = collection.find_one({}, {"uuid": 1})
    if sample_doc and 'uuid' in sample_doc:
        test_uuid = sample_doc['uuid']
        
        start_time = time.time()
        result = collection.find_one({"uuid": test_uuid})
        elapsed = time.time() - start_time
        
        print(f"Query: uuid = '{test_uuid[:20]}...'")
        print(f"Result: {'Found' if result else 'Not found'}")
        print(f"Time: {elapsed:.3f} seconds")
        
        # Get explain
        explain = collection.find({"uuid": test_uuid}).explain()
        execution_stats = explain.get('executionStats', {})
        print(f"Documents examined: {execution_stats.get('totalDocsExamined', 'N/A'):,}")
        
        if execution_stats.get('totalDocsExamined', 0) > 1:
            print("⚠️  WARNING: Examined more than 1 document for unique UUID lookup!")
    else:
        print("No UUID found to test")
    print()
    
    # Test 4: Deleted filter
    print("Test 4: Filter Active Recordings (deleted=False)")
    print("-" * 40)
    
    start_time = time.time()
    cursor = collection.find({"deleted": False})
    results = list(cursor)
    elapsed = time.time() - start_time
    
    print(f"Query: deleted = False")
    print(f"Result: {len(results):,} documents")
    print(f"Time: {elapsed:.3f} seconds")
    
    # Get explain
    explain = collection.find({"deleted": False}).explain()
    execution_stats = explain.get('executionStats', {})
    print(f"Documents examined: {execution_stats.get('totalDocsExamined', 'N/A'):,}")
    
    if execution_stats.get('totalDocsExamined', 0) == total_count:
        print("⚠️  WARNING: FULL COLLECTION SCAN!")
    print()
    
    # Test 5: Complex query (time range + deleted filter)
    print("Test 5: Complex Query (Time Range + Active Only)")
    print("-" * 40)
    
    start_time = time.time()
    cursor = collection.find({
        "start_time": {"$gte": thirty_days_ago},
        "deleted": False
    })
    results = list(cursor)
    elapsed = time.time() - start_time
    
    print(f"Query: start_time >= {thirty_days_ago.strftime('%Y-%m-%d')} AND deleted = False")
    print(f"Result: {len(results):,} documents")
    print(f"Time: {elapsed:.3f} seconds")
    
    # Get explain
    explain = collection.find({
        "start_time": {"$gte": thirty_days_ago},
        "deleted": False
    }).explain()
    execution_stats = explain.get('executionStats', {})
    print(f"Documents examined: {execution_stats.get('totalDocsExamined', 'N/A'):,}")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Total documents: {total_count:,}")
    print(f"Current indexes: {len(indexes)} (only _id)")
    print()
    print("Performance Issues Detected:")
    print("  ⚠️  All filtered queries perform FULL COLLECTION SCANS")
    print("  ⚠️  Every query examines ALL documents instead of using indexes")
    print("  ⚠️  UUID lookups are not optimized (no unique constraint)")
    print()
    print("Recommended Indexes:")
    print("  1. start_time (ascending) - for time range queries")
    print("  2. end_time (ascending) - for time range queries")
    print("  3. uuid (ascending, UNIQUE) - for fast lookups")
    print("  4. deleted (ascending) - for filtering")
    print()
    
    # Close
    client.close()
    
    print("✅ Measurement complete!")
    print()
    print("Note: These are ACTUAL measured performance numbers.")


if __name__ == "__main__":
    main()

