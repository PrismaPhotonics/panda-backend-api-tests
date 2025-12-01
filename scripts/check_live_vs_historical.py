#!/usr/bin/env python3
"""
Check Live vs Historical Recordings
====================================

This script shows you which recordings are Live and which are Historical.

Author: Roy Avrahami
Date: 2025-10-16
"""

import sys
import io
import yaml
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
    print("Live vs Historical Recordings Checker")
    print("=" * 80)
    print()
    
    # Connect
    environment = sys.argv[1] if len(sys.argv) > 1 else "staging"
    print(f"🌍 Environment: {environment}")
    
    config = load_config(environment)
    client, db = connect_to_mongodb(config)
    collection, collection_name = get_recording_collection(db)
    
    print(f"📦 Collection: {collection_name}")
    print()
    
    # Count totals
    total = collection.count_documents({})
    print(f"📊 Total recordings: {total:,}")
    print()
    
    # ============================================
    # Historical (completed recordings)
    # ============================================
    print("=" * 80)
    print("1️⃣  HISTORICAL RECORDINGS (Completed)")
    print("=" * 80)
    print("ההגדרה: יש start_time + end_time, deleted=False")
    print()
    
    historical = collection.count_documents({
        "start_time": {"$exists": True},
        "end_time": {"$exists": True, "$ne": None},
        "deleted": False
    })
    
    print(f"📈 Count: {historical:,} ({historical/total*100:.1f}%)")
    print()
    
    # Sample
    print("דוגמאות (5 רשומות):")
    historical_sample = collection.find({
        "start_time": {"$exists": True},
        "end_time": {"$exists": True, "$ne": None},
        "deleted": False
    }).limit(5)
    
    for idx, rec in enumerate(historical_sample, 1):
        duration = (rec['end_time'] - rec['start_time']).total_seconds() / 3600
        print(f"   {idx}. UUID: {rec['uuid'][:20]}...")
        print(f"      Start: {rec['start_time']}")
        print(f"      End:   {rec['end_time']}")
        print(f"      Duration: {duration:.2f} hours")
        print(f"      Status: ✅ Historical (הסתיימה)")
        print()
    
    # ============================================
    # Live (in-progress recordings)
    # ============================================
    print("=" * 80)
    print("2️⃣  LIVE RECORDINGS (In Progress)")
    print("=" * 80)
    print("ההגדרה: יש start_time, אין end_time, deleted=False")
    print()
    
    live = collection.count_documents({
        "start_time": {"$exists": True},
        "$or": [
            {"end_time": {"$exists": False}},
            {"end_time": None}
        ],
        "deleted": False
    })
    
    print(f"🔴 Count: {live:,} ({live/total*100:.2f}%)")
    print()
    
    if live > 0:
        print("דוגמאות:")
        live_sample = collection.find({
            "start_time": {"$exists": True},
            "$or": [
                {"end_time": {"$exists": False}},
                {"end_time": None}
            ],
            "deleted": False
        }).limit(5)
        
        now = datetime.now(timezone.utc)
        
        for idx, rec in enumerate(live_sample, 1):
            start_time = rec['start_time']
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
            
            age_hours = (now - start_time).total_seconds() / 3600
            
            # Check if stale (>24h)
            if age_hours > 24:
                status_emoji = "💀"
                status_text = "STALE (תקוע > 24 שעות!)"
            else:
                status_emoji = "🟢"
                status_text = "LIVE (פעיל)"
            
            print(f"   {idx}. UUID: {rec['uuid'][:20]}...")
            print(f"      Start: {rec['start_time']}")
            print(f"      End:   None (עדיין רץ)")
            print(f"      Age: {age_hours:.1f} hours")
            print(f"      Status: {status_emoji} {status_text}")
            print()
    else:
        print("   אין הקלטות Live כרגע")
        print()
    
    # ============================================
    # Deleted recordings
    # ============================================
    print("=" * 80)
    print("3️⃣  DELETED RECORDINGS (נמחקו)")
    print("=" * 80)
    print("ההגדרה: deleted=True")
    print()
    
    deleted = collection.count_documents({"deleted": True})
    
    print(f"🗑️  Count: {deleted:,} ({deleted/total*100:.2f}%)")
    print()
    
    if deleted > 0:
        print("דוגמאות (3 רשומות):")
        deleted_sample = collection.find({"deleted": True}).limit(3)
        
        for idx, rec in enumerate(deleted_sample, 1):
            has_end = rec.get('end_time') is not None
            print(f"   {idx}. UUID: {rec['uuid'][:20]}...")
            print(f"      Start: {rec['start_time']}")
            print(f"      End:   {rec.get('end_time', 'None (נמחק תוך כדי)')}")
            print(f"      Status: 🗑️  Deleted")
            print()
    
    # ============================================
    # Summary
    # ============================================
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print()
    print(f"{'סוג':<20} {'כמות':<10} {'אחוז':<10} {'הגדרה'}")
    print("-" * 80)
    print(f"{'Historical':<20} {historical:<10,} {historical/total*100:>6.1f}%   יש start_time + end_time")
    print(f"{'Live':<20} {live:<10,} {live/total*100:>6.2f}%   יש start_time, אין end_time")
    print(f"{'Deleted':<20} {deleted:<10,} {deleted/total*100:>6.2f}%   deleted=True")
    print("-" * 80)
    print(f"{'TOTAL':<20} {total:<10,} {100.0:>6.1f}%")
    print()
    
    # Close
    client.close()
    
    print("✅ Done!")


if __name__ == "__main__":
    main()

