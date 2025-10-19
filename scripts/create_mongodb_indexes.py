#!/usr/bin/env python3
"""
Create MongoDB Indexes for Focus Server Automation
===================================================

This script creates the required indexes on the MongoDB database
for optimal query performance.

Critical indexes:
- start_time: For time-range queries on recordings
- end_time: For time-range queries on recordings  
- uuid: For unique recording identification

Usage:
    python scripts/create_mongodb_indexes.py
    
Environment Variables:
    MONGODB_URI: Full MongoDB connection string (optional, defaults to new_production)
"""

import os
import sys
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure

# Default MongoDB connection for new_production environment
DEFAULT_MONGODB_URI = "mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma"
DEFAULT_DATABASE = "prisma"


def create_indexes(mongodb_uri: str = None, database_name: str = None):
    """
    Create required MongoDB indexes.
    
    Args:
        mongodb_uri: MongoDB connection string
        database_name: Database name to create indexes in
        
    Returns:
        bool: True if all indexes created successfully
    """
    # Use provided values or defaults
    uri = mongodb_uri or os.getenv("MONGODB_URI", DEFAULT_MONGODB_URI)
    db_name = database_name or os.getenv("MONGODB_DATABASE", DEFAULT_DATABASE)
    
    print(f"\n{'='*80}")
    print("  MongoDB Index Creation")
    print(f"{'='*80}\n")
    
    try:
        # Connect to MongoDB
        print(f"Connecting to MongoDB...")
        print(f"  URI: {uri.split('@')[0]}@***")  # Hide credentials in output
        print(f"  Database: {db_name}")
        
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("[OK] Connected successfully\n")
        
        # Get database
        db = client[db_name]
        
        # Collections to index
        collections_to_index = {
            "recordings": [
                ("start_time", ASCENDING, False, "Recording start time for range queries"),
                ("end_time", ASCENDING, False, "Recording end time for range queries"),
                ("uuid", ASCENDING, True, "Unique recording identifier"),
            ],
            # Add more collections if needed
        }
        
        success = True
        total_created = 0
        total_existing = 0
        
        # Create indexes for each collection
        for collection_name, indexes in collections_to_index.items():
            print(f"Collection: {collection_name}")
            collection = db[collection_name]
            
            # Get existing indexes
            existing_indexes = collection.index_information()
            existing_index_keys = [
                info.get('key')[0][0] if info.get('key') else None
                for info in existing_indexes.values()
            ]
            
            for field_name, direction, unique, description in indexes:
                try:
                    # Check if index already exists
                    if field_name in existing_index_keys:
                        print(f"  [OK] {field_name}: Already exists")
                        total_existing += 1
                        continue
                    
                    # Create index
                    index_name = collection.create_index(
                        [(field_name, direction)],
                        unique=unique,
                        background=True  # Don't block operations
                    )
                    
                    print(f"  [OK] {field_name}: Created ({description})")
                    total_created += 1
                    
                except OperationFailure as e:
                    print(f"  [FAIL] {field_name}: Failed - {e}")
                    success = False
                    
            print()
        
        # Summary
        print(f"{'='*80}")
        print("Summary:")
        print(f"  Indexes created: {total_created}")
        print(f"  Indexes already existing: {total_existing}")
        print(f"  Status: {'[SUCCESS]' if success else '[PARTIAL FAILURE]'}")
        print(f"{'='*80}\n")
        
        # Close connection
        client.close()
        
        return success
        
    except ConnectionFailure as e:
        print(f"[FAIL] Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check that MongoDB is accessible at the specified host/port")
        print("  2. Verify credentials are correct")
        print("  3. Ensure network connectivity to MongoDB server")
        return False
        
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def verify_indexes(mongodb_uri: str = None, database_name: str = None):
    """
    Verify that all required indexes exist.
    
    Args:
        mongodb_uri: MongoDB connection string
        database_name: Database name
        
    Returns:
        bool: True if all required indexes exist
    """
    uri = mongodb_uri or os.getenv("MONGODB_URI", DEFAULT_MONGODB_URI)
    db_name = database_name or os.getenv("MONGODB_DATABASE", DEFAULT_DATABASE)
    
    print(f"\n{'='*80}")
    print("  Verifying MongoDB Indexes")
    print(f"{'='*80}\n")
    
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        db = client[db_name]
        collection = db["recordings"]
        
        # Required indexes
        required_indexes = ['start_time', 'end_time', 'uuid']
        
        # Get existing indexes
        existing_indexes = collection.index_information()
        existing_index_keys = [
            info.get('key')[0][0] if info.get('key') else None
            for info in existing_indexes.values()
        ]
        
        print("Required Indexes:")
        all_exist = True
        for index_name in required_indexes:
            exists = index_name in existing_index_keys
            status = "[OK] EXISTS" if exists else "[MISSING]"
            print(f"  {index_name}: {status}")
            if not exists:
                all_exist = False
        
        print(f"\nStatus: {'[OK] ALL INDEXES EXIST' if all_exist else '[WARN] SOME INDEXES MISSING'}\n")
        
        client.close()
        return all_exist
        
    except Exception as e:
        print(f"[FAIL] Verification failed: {e}\n")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create MongoDB indexes for Focus Server Automation"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify indexes, don't create them"
    )
    parser.add_argument(
        "--uri",
        help="MongoDB connection URI (overrides env var and default)"
    )
    parser.add_argument(
        "--database",
        help="Database name (overrides env var and default)"
    )
    
    args = parser.parse_args()
    
    if args.verify_only:
        # Verify only
        success = verify_indexes(args.uri, args.database)
    else:
        # Create indexes
        success = create_indexes(args.uri, args.database)
        
        # Verify after creation
        if success:
            print("\nVerifying created indexes...")
            success = verify_indexes(args.uri, args.database)
    
    sys.exit(0 if success else 1)

