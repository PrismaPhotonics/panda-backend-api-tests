#!/usr/bin/env python3
"""Check specific MongoDB record by _id"""

import sys
import io
import yaml
from pathlib import Path
from pymongo import MongoClient
from bson.objectid import ObjectId

# Fix Windows emoji encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def load_config(environment="staging"):
    config_path = Path(__file__).parent.parent / "config" / "environments.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config['environments'].get(environment)


def connect_to_mongodb(config):
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


# Connect
environment = "staging"
config = load_config(environment)
client, db = connect_to_mongodb(config)
collection, collection_name = get_recording_collection(db)

# Find the specific record
record_id = "689b41f9112a85ad3bec2c40"
doc = collection.find_one({"_id": ObjectId(record_id)})

if doc:
    print("=" * 80)
    print(f"Record ID: {record_id}")
    print("=" * 80)
    print()
    print(f"UUID: {doc.get('uuid', 'MISSING')}")
    print(f"start_time: {doc.get('start_time', 'MISSING')}")
    print(f"end_time: {doc.get('end_time', 'MISSING')}")
    print(f"deleted: {doc.get('deleted', 'MISSING (field not present)')}")
    print()
    
    # Determine classification
    has_end_time = 'end_time' in doc and doc['end_time'] is not None
    is_deleted = doc.get('deleted', False) == True
    has_deleted_field = 'deleted' in doc
    
    print("Classification:")
    if not has_deleted_field:
        print("  ⚠️  WARNING: 'deleted' field is MISSING from document!")
        print("      This is a schema violation - all documents should have 'deleted' field")
    
    if is_deleted:
        print("  📁 Type: DELETED")
        if not has_end_time:
            print("  🐛 BUG: Deleted record missing end_time")
    elif has_end_time:
        print("  ✅ Type: HISTORICAL (completed)")
    else:
        print("  🟢 Type: LIVE (in progress)")
        print("      This is VALID - Live recordings don't need end_time")
    
    print()
    print("Full document:")
    print(doc)
else:
    print(f"Record {record_id} not found!")

client.close()

