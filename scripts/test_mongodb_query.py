#!/usr/bin/env python3
"""
Test MongoDB Direct Query for Recordings
=========================================

Quick test script to verify MongoDB connection and recording query.
"""

import pymongo
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_manager import ConfigManager

def main():
    print("=" * 60)
    print("Testing MongoDB Direct Query for Recordings")
    print("=" * 60)
    
    # Load config
    cm = ConfigManager()
    mongo_config = cm.get_database_config()
    print(f"MongoDB: {mongo_config['host']}:{mongo_config['port']}")
    
    # Connect
    client = pymongo.MongoClient(
        host=mongo_config['host'],
        port=mongo_config['port'],
        username=mongo_config['username'],
        password=mongo_config['password'],
        authSource=mongo_config.get('auth_source', 'prisma'),
        serverSelectionTimeoutMS=10000
    )
    
    db = client['prisma']
    print(f"Connected to: {db.name}")
    
    # List collections
    colls = db.list_collection_names()
    print(f"\nCollections ({len(colls)}):")
    for c in colls[:15]:
        print(f"  - {c}")
    if len(colls) > 15:
        print(f"  ... and {len(colls) - 15} more")
    
    # Query base_paths
    print("\n" + "=" * 60)
    print("Querying base_paths collection...")
    base_paths = db['base_paths']
    doc = base_paths.find_one()
    
    if doc:
        print(f"base_paths keys: {list(doc.keys())}")
        guid = doc.get('guid')
        print(f"GUID: {guid}")
        
        # Query the recordings collection
        if guid:
            print(f"\n" + "=" * 60)
            print(f"Querying recordings collection: {guid}")
            rec_coll = db[str(guid)]
            count = rec_coll.count_documents({'deleted': False})
            print(f"Non-deleted recordings: {count}")
            
            # Get latest 5 recordings
            print("\nLatest recordings:")
            cursor = rec_coll.find({'deleted': False}, sort=[('start_time', -1)]).limit(5)
            
            for i, rec in enumerate(cursor, 1):
                start = rec.get('start_time')
                end = rec.get('end_time')
                duration = (end - start).total_seconds() if start and end else 0
                print(f"  {i}. {start} to {end} ({duration:.1f}s)")
                
            print("\n✅ MongoDB query successful!")
    else:
        print("❌ No base_paths doc found")
    
    client.close()
    print("\nDone!")


if __name__ == "__main__":
    main()

