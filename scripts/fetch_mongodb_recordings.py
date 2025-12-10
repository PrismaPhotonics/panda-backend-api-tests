#!/usr/bin/env python3
"""
Fetch MongoDB Recordings Collection Data
=========================================

Script to fetch and analyze all recordings from MongoDB collection.
Supports SSH tunnel connection and exports data to JSON/CSV.

Usage:
    python scripts/fetch_mongodb_recordings.py [--output json|csv] [--weeks-back 4] [--limit 1000]
"""

import sys
import os
import json
import csv
import argparse
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymongo
from config.config_manager import ConfigManager
from be_focus_server_tests.fixtures.recording_fixtures import MongoDBTunnelManager


def format_datetime(dt: Any) -> str:
    """Format datetime for display."""
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    return str(dt)


def calculate_duration(start: Any, end: Any) -> float:
    """Calculate duration in seconds."""
    if not start or not end:
        return 0.0
    
    if isinstance(start, datetime) and isinstance(end, datetime):
        delta = end - start
        return delta.total_seconds()
    return 0.0


def fetch_recordings(
    config_manager: ConfigManager,
    weeks_back: int = 4,
    limit: Optional[int] = None,
    use_tunnel: bool = True
) -> List[Dict[str, Any]]:
    """
    Fetch all recordings from MongoDB collection.
    
    Args:
        config_manager: ConfigManager instance
        weeks_back: Number of weeks back to search (default: 4)
        limit: Maximum number of recordings to fetch (None = all)
        use_tunnel: Whether to use SSH tunnel (default: True)
        
    Returns:
        List of recording documents
    """
    print("=" * 80)
    print("Fetching MongoDB Recordings")
    print("=" * 80)
    
    tunnel_manager = None
    client = None
    
    try:
        # Setup SSH tunnel if requested
        if use_tunnel:
            print("\n[1/5] Setting up SSH tunnel...")
            tunnel_manager = MongoDBTunnelManager(config_manager)
            if tunnel_manager.setup():
                print("✅ SSH tunnel established")
            else:
                print("⚠️  SSH tunnel setup failed, using direct connection")
                use_tunnel = False
        
        # Get MongoDB config
        mongo_config = config_manager.get_database_config()
        
        # Determine connection host and port
        if use_tunnel and tunnel_manager:
            mongo_host = tunnel_manager.get_connection_host()
            mongo_port = mongo_config.get("port", 27017)
            print(f"   Connecting via tunnel: {mongo_host}:{mongo_port}")
        else:
            mongo_host = mongo_config["host"]
            mongo_port = mongo_config["port"]
            print(f"   Connecting directly: {mongo_host}:{mongo_port}")
        
        # Connect to MongoDB
        print("\n[2/5] Connecting to MongoDB...")
        client = pymongo.MongoClient(
            host=mongo_host,
            port=mongo_port,
            username=mongo_config["username"],
            password=mongo_config["password"],
            authSource=mongo_config.get("auth_source", "prisma"),
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=30000
        )
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        # Get database
        db_name = mongo_config.get("database", "prisma")
        db = client[db_name]
        print(f"   Database: {db_name}")
        
        # Get GUIDs ONLY for current environment
        print("\n[3/5] Finding recordings collections for current environment...")
        
        current_env = config_manager.get_current_environment()
        print(f"   Current environment: {current_env}")
        
        base_paths = db["base_paths"]
        
        # Map environment to base_path patterns
        env_base_paths = {
            "staging": ["/prisma/root/recordings"],
            "kefar_saba": ["/prisma/root/recordings/segy"],
            "production": ["/prisma/root/recordings/segy"],
        }
        
        # Get base_path patterns for current environment
        target_base_paths = env_base_paths.get(current_env, [])
        
        if not target_base_paths:
            print(f"⚠️  Unknown environment '{current_env}', trying all base_paths")
            target_base_paths = ["/prisma/root/recordings", "/prisma/root/recordings/segy"]
        
        print(f"   Looking for base_paths: {target_base_paths}")
        
        # Find base_paths documents for current environment ONLY
        env_base_path_docs = []
        for base_path_pattern in target_base_paths:
            docs = list(base_paths.find({
                "base_path": base_path_pattern,
                "is_archive": False
            }))
            env_base_path_docs.extend(docs)
        
        if not env_base_path_docs:
            all_docs = list(base_paths.find({"is_archive": False}))
            available_paths = [d.get('base_path', 'N/A') for d in all_docs]
            print(f"❌ No base_paths documents found for environment '{current_env}'. Available paths: {available_paths}")
            return []
        
        # Extract GUIDs ONLY from current environment's base_paths
        guids = []
        for doc in env_base_path_docs:
            guid = doc.get("guid")
            if not guid:
                guid = doc.get("_id")
                if isinstance(guid, dict):
                    guid = str(guid)
            
            if guid:
                guid_str = str(guid)
                # Only add GUIDs that look like valid UUIDs
                if len(guid_str) == 36 and guid_str.count('-') == 4:
                    guids.append(guid_str)
                    base_path_val = doc.get('base_path', 'N/A')
                    print(f"✅ Found GUID for '{current_env}' from base_path '{base_path_val}': {guid_str}")
        
        if not guids:
            print(f"❌ No valid GUIDs found for environment '{current_env}'")
            return []
        
        print(f"\n   Found {len(guids)} GUID collections for environment '{current_env}': {guids}")
        
        # Query recordings collections for current environment ONLY
        print(f"\n[4/5] Querying recordings from collections for environment '{current_env}'...")
        
        # Calculate time range
        now = datetime.now()
        weeks_ago = now - timedelta(weeks=weeks_back)
        
        print(f"   Time range: {weeks_ago.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')} ({weeks_back} weeks)")
        
        # Query: Find all recordings that overlap with time range
        query = {
            "$or": [
                # Started within range
                {
                    "start_time": {
                        "$gte": weeks_ago,
                        "$lte": now
                    }
                },
                # Ended within range
                {
                    "end_time": {
                        "$gte": weeks_ago,
                        "$lte": now
                    }
                },
                # Spans entire range
                {
                    "start_time": {"$lt": weeks_ago},
                    "end_time": {"$gt": now}
                }
            ]
        }
        
        recordings = []
        total_count_all = 0
        
        print("\n[5/5] Fetching recording data from all collections...")
        
        for guid in guids:
            collection_name = str(guid)
            
            # Check if collection exists
            if collection_name not in db.list_collection_names():
                print(f"   ⚠️  Collection {collection_name} does not exist, skipping")
                continue
            
            try:
                recordings_collection = db[collection_name]
                
                # Count total matching recordings in this collection
                total_count = recordings_collection.count_documents(query)
                total_count_all += total_count
                print(f"   Collection '{collection_name}': {total_count} recordings")
                
                # Fetch recordings from this collection
                cursor = recordings_collection.find(query).sort([("start_time", -1)])
                
                if limit:
                    # Distribute limit across collections
                    per_collection_limit = max(limit // len(guids), 100)
                    cursor = cursor.limit(per_collection_limit)
                
                collection_recordings = []
                for i, doc in enumerate(cursor, 1):
                    # Stop if we have enough recordings overall
                    if limit and len(recordings) >= limit:
                        break
                    
                    # Extract key fields
                    recording = {
                        "uuid": doc.get("uuid"),
                        "start_time": doc.get("start_time"),
                        "end_time": doc.get("end_time"),
                        "deleted": doc.get("deleted", False),
                        "duration_seconds": calculate_duration(doc.get("start_time"), doc.get("end_time")),
                        "fiber_metadata": doc.get("fiber_metadata"),
                        "collection_name": collection_name,  # Track which collection this came from
                        "raw_document": doc  # Include full document
                    }
                    
                    recordings.append(recording)
                    collection_recordings.append(recording)
                
                print(f"      Fetched {len(collection_recordings)} recordings from '{collection_name}'")
                
                # Stop if we have enough recordings overall
                if limit and len(recordings) >= limit:
                    print(f"   Reached limit of {limit} recordings, stopping")
                    break
            
            except Exception as e:
                print(f"   ⚠️  Error querying collection '{collection_name}': {e}")
                continue
        
        print(f"\n✅ Fetched {len(recordings)} recordings from {len(guids)} collections for environment '{current_env}'")
        print(f"   Total matching recordings across all collections: {total_count_all}")
        
        return recordings
        
    except Exception as e:
        print(f"\n❌ Error fetching recordings: {e}")
        import traceback
        traceback.print_exc()
        return []
        
    finally:
        # Cleanup
        if client:
            client.close()
        if tunnel_manager:
            tunnel_manager.cleanup()


def print_statistics(recordings: List[Dict[str, Any]]):
    """Print statistics about the recordings."""
    if not recordings:
        print("\n❌ No recordings to analyze")
        return
    
    print("\n" + "=" * 80)
    print("Statistics")
    print("=" * 80)
    
    # Basic counts
    total = len(recordings)
    deleted = sum(1 for r in recordings if r.get("deleted", False))
    non_deleted = total - deleted
    
    print(f"\nTotal recordings: {total}")
    print(f"  - Non-deleted: {non_deleted}")
    print(f"  - Deleted: {deleted}")
    
    # Duration statistics
    durations = [r.get("duration_seconds", 0) for r in recordings if r.get("duration_seconds")]
    if durations:
        durations.sort()
        print(f"\nDuration statistics (seconds):")
        print(f"  - Min: {min(durations):.1f}s")
        print(f"  - Max: {max(durations):.1f}s")
        print(f"  - Average: {sum(durations)/len(durations):.1f}s")
        print(f"  - Median: {durations[len(durations)//2]:.1f}s")
        
        # Duration ranges
        short = sum(1 for d in durations if d < 10)
        medium = sum(1 for d in durations if 10 <= d < 60)
        long_rec = sum(1 for d in durations if 60 <= d < 300)
        very_long = sum(1 for d in durations if d >= 300)
        
        print(f"\nDuration distribution:")
        print(f"  - < 10s: {short}")
        print(f"  - 10-60s: {medium}")
        print(f"  - 60-300s: {long_rec}")
        print(f"  - >= 300s: {very_long}")
    
    # Time range
    start_times = [r.get("start_time") for r in recordings if r.get("start_time")]
    end_times = [r.get("end_time") for r in recordings if r.get("end_time")]
    
    if start_times and end_times:
        earliest_start = min(start_times)
        latest_end = max(end_times)
        print(f"\nTime range:")
        print(f"  - Earliest start: {format_datetime(earliest_start)}")
        print(f"  - Latest end: {format_datetime(latest_end)}")
    
    # Sample recordings
    print(f"\nSample recordings (first 5):")
    for i, rec in enumerate(recordings[:5], 1):
        start = rec.get("start_time")
        end = rec.get("end_time")
        duration = rec.get("duration_seconds", 0)
        deleted = rec.get("deleted", False)
        
        print(f"  {i}. {format_datetime(start)} to {format_datetime(end)} "
              f"({duration:.1f}s) {'[DELETED]' if deleted else ''}")


def export_to_json(recordings: List[Dict[str, Any]], filename: str):
    """Export recordings to JSON file."""
    # Convert datetime objects to strings for JSON serialization
    json_data = []
    for rec in recordings:
        json_rec = {
            "uuid": rec.get("uuid"),
            "start_time": format_datetime(rec.get("start_time")) if rec.get("start_time") else None,
            "end_time": format_datetime(rec.get("end_time")) if rec.get("end_time") else None,
            "deleted": rec.get("deleted", False),
            "duration_seconds": rec.get("duration_seconds", 0),
            "fiber_metadata": rec.get("fiber_metadata")
        }
        json_data.append(json_rec)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Exported {len(json_data)} recordings to {filename}")


def export_to_csv(recordings: List[Dict[str, Any]], filename: str):
    """Export recordings to CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            "uuid", "start_time", "end_time", "duration_seconds", 
            "deleted", "fiber_metadata"
        ])
        
        # Data
        for rec in recordings:
            writer.writerow([
                rec.get("uuid"),
                format_datetime(rec.get("start_time")) if rec.get("start_time") else "",
                format_datetime(rec.get("end_time")) if rec.get("end_time") else "",
                rec.get("duration_seconds", 0),
                rec.get("deleted", False),
                str(rec.get("fiber_metadata", ""))
            ])
    
    print(f"\n✅ Exported {len(recordings)} recordings to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch recordings from MongoDB collection"
    )
    parser.add_argument(
        "--output", "-o",
        choices=["json", "csv"],
        help="Export format (json or csv)"
    )
    parser.add_argument(
        "--weeks-back", "-w",
        type=int,
        default=4,
        help="Number of weeks back to search (default: 4)"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        help="Maximum number of recordings to fetch (default: all)"
    )
    parser.add_argument(
        "--no-tunnel",
        action="store_true",
        help="Don't use SSH tunnel (direct connection)"
    )
    parser.add_argument(
        "--output-file",
        help="Output filename (default: recordings_<timestamp>.json/csv)"
    )
    parser.add_argument(
        "--environment", "-e",
        choices=["staging", "kefar_saba", "production"],
        help="Environment to use (default: from config or staging)"
    )
    
    args = parser.parse_args()
    
    # Load config with specified environment
    config_manager = ConfigManager(env=args.environment) if args.environment else ConfigManager()
    
    # Fetch recordings
    recordings = fetch_recordings(
        config_manager=config_manager,
        weeks_back=args.weeks_back,
        limit=args.limit,
        use_tunnel=not args.no_tunnel
    )
    
    # Print statistics
    print_statistics(recordings)
    
    # Export if requested
    if args.output:
        if not args.output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output_file = f"recordings_{timestamp}.{args.output}"
        
        if args.output == "json":
            export_to_json(recordings, args.output_file)
        elif args.output == "csv":
            export_to_csv(recordings, args.output_file)
    
    print("\n" + "=" * 80)
    print("Done!")
    print("=" * 80)


if __name__ == "__main__":
    main()

