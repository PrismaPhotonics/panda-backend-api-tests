#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick MongoDB Explorer - Get Started in 30 Seconds!

Usage:
    python scripts/quick_mongo_explore.py
"""

import sys
import yaml
from pathlib import Path
from pymongo import MongoClient
import json

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def quick_explore():
    """Quick and dirty MongoDB exploration."""
    
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "environments.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Use default environment from config, or fallback to 'staging'
    default_env = config.get("default_environment", "staging")
    mongo_config = config["environments"][default_env]["mongodb"]
    
    print(f"🌍 Using environment: {default_env}")
    
    # Connect
    connection_params = {
        "host": mongo_config["host"],
        "port": mongo_config["port"]
    }
    
    # Add authentication if provided
    if mongo_config.get("username"):
        connection_params["username"] = mongo_config["username"]
        connection_params["password"] = mongo_config.get("password")
        connection_params["authSource"] = mongo_config.get("auth_source", "admin")
    
    print(f"Connecting to MongoDB: {mongo_config['host']}:{mongo_config['port']}")
    print(f"Database: {mongo_config['database']}")
    print(f"Auth Source: {connection_params.get('authSource', 'N/A')}")
    
    try:
        client = MongoClient(**connection_params, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        print("✅ Connected successfully!\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if MongoDB is accessible from your network")
        print("2. Verify username/password in config/environments.yaml")
        print("3. Try: ssh -L 27017:10.10.10.103:27017 prisma@10.10.10.150")
        return
    
    db = client[mongo_config["database"]]
    
    print("\n" + "="*60)
    print("🔍 QUICK MONGODB EXPLORATION")
    print("="*60)
    
    # List collections
    collections = db.list_collection_names()
    print(f"\n📦 Collections ({len(collections)}):")
    for col in collections:
        count = db[col].count_documents({})
        print(f"   - {col}: {count} documents")
    
    # For each collection, show sample
    for col_name in collections:
        print(f"\n{'='*60}")
        print(f"Collection: {col_name}")
        print('='*60)
        
        collection = db[col_name]
        
        # Get one sample document
        sample = collection.find_one()
        if sample:
            # Convert ObjectId to string for JSON
            sample['_id'] = str(sample['_id'])
            
            print("\n📄 Sample Document:")
            print(json.dumps(sample, indent=2, default=str))
            
            # List all fields
            fields = list(sample.keys())
            print(f"\n🔑 Fields ({len(fields)}):")
            for field in fields:
                value = sample[field]
                type_name = type(value).__name__
                print(f"   - {field}: {type_name}")
            
            # Show indexes
            indexes = list(collection.list_indexes())
            print(f"\n🔐 Indexes ({len(indexes)}):")
            for idx in indexes:
                unique = "UNIQUE" if idx.get('unique') else "NON-UNIQUE"
                print(f"   - {idx['name']}: {idx['key']} ({unique})")
        else:
            print("   ⚠️  Collection is empty!")
    
    print("\n✅ Exploration complete!")
    print("\nNext steps:")
    print("1. Look at the sample documents above")
    print("2. Identify which fields are critical for your tests")
    print("3. Write validation tests for those fields")


if __name__ == "__main__":
    quick_explore()

