"""
Script to check MongoDB alert schema and find how alerts are actually stored.

This script:
1. Connects to MongoDB
2. Lists all collections
3. Checks the 'alerts' collection schema
4. Shows recent alerts and their structure
5. Tests different search patterns

Run with:
    python scripts/check_mongodb_alert_schema.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.infrastructure.mongodb_manager import MongoDBManager
import json
from datetime import datetime

def main():
    print("=" * 80)
    print("MongoDB Alert Schema Investigation")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Load config
    config_manager = ConfigManager()
    env = config_manager.get("environment", "staging")
    print(f"Environment: {env}\n")
    
    # Connect to MongoDB
    mongodb_manager = MongoDBManager(config_manager)
    try:
        mongodb_manager.connect()
        print("[OK] Connected to MongoDB\n")
        
        # List all databases
        print("=" * 80)
        print("Step 0: Listing All Databases")
        print("=" * 80)
        admin_db = mongodb_manager.client.admin
        db_list = admin_db.command("listDatabases")
        databases = [db["name"] for db in db_list["databases"]]
        print(f"Found {len(databases)} databases:")
        for db_name in sorted(databases):
            print(f"  - {db_name}")
        
        # Check each database for alerts
        print("\n" + "=" * 80)
        print("Step 1: Searching for 'alerts' Collection in All Databases")
        print("=" * 80)
        
        alerts_found = False
        for db_name in databases:
            db = mongodb_manager.client[db_name]
            collections = db.list_collection_names()
            if 'alerts' in collections:
                alerts_found = True
                print(f"\n[FOUND] 'alerts' collection in database: {db_name}")
                alerts_collection = db.get_collection("alerts")
                count = alerts_collection.count_documents({})
                print(f"  Total alerts: {count}")
                
                if count > 0:
                    # Get sample alert
                    sample = alerts_collection.find_one()
                    print(f"  Sample alert keys: {list(sample.keys())}")
        
        if not alerts_found:
            print("\n[WARNING] 'alerts' collection not found in any database!")
            print("\nChecking all collections in all databases for alert-related data:")
            for db_name in databases:
                db = mongodb_manager.client[db_name]
                collections = db.list_collection_names()
                print(f"\nDatabase: {db_name}")
                for coll in sorted(collections):
                    count = db[coll].count_documents({})
                    print(f"  - {coll}: {count} documents")
        
        # Get prisma database (main one)
        db = mongodb_manager.get_database("prisma")
        
        # List all collections in prisma
        print("\n" + "=" * 80)
        print("Step 1.5: Collections in 'prisma' Database")
        print("=" * 80)
        collections = db.list_collection_names()
        print(f"Found {len(collections)} collections:")
        for coll in sorted(collections):
            count = db[coll].count_documents({})
            print(f"  - {coll}: {count} documents")
        
        # Check if alerts might be in the main collection
        print("\n" + "=" * 80)
        print("Step 2: Checking Main Collection for Alert Data")
        print("=" * 80)
        
        main_collection_name = None
        for coll in collections:
            if coll not in ['base_paths'] and not coll.endswith('-unrecognized_recordings'):
                main_collection_name = coll
                break
        
        if main_collection_name:
            print(f"Checking main collection: {main_collection_name}")
            main_collection = db.get_collection(main_collection_name)
            
            # Sample documents to see structure
            sample_docs = list(main_collection.find().limit(5))
            if sample_docs:
                print(f"\nSample document keys:")
                for i, doc in enumerate(sample_docs[:3], 1):
                    print(f"  Doc {i}: {list(doc.keys())}")
                    
                # Check if any document has alert-related fields
                alert_fields = ['alert', 'ext_id', 'class_id', 'severity', 'dof']
                found_alert_fields = set()
                for doc in sample_docs:
                    for field in alert_fields:
                        if field in str(doc).lower():
                            found_alert_fields.add(field)
                
                if found_alert_fields:
                    print(f"\n[INFO] Found alert-related fields: {found_alert_fields}")
                else:
                    print(f"\n[INFO] No alert-related fields found in sample documents")
        
        # Check alerts collection
        print("\n" + "=" * 80)
        print("Step 3: Checking 'alerts' Collection Schema")
        print("=" * 80)
        
        if 'alerts' not in collections:
            print("[ERROR] 'alerts' collection not found!")
            print("\n[CONCLUSION] Alerts are NOT stored in MongoDB!")
            print("This explains why the tests are failing.")
            print("\nPossible reasons:")
            print("  1. Alerts are only processed through RabbitMQ, not stored")
            print("  2. Alerts are stored in a different system (not MongoDB)")
            print("  3. Alerts collection is created dynamically only when needed")
            print("  4. The alert storage feature is not implemented yet")
            return
        
        alerts_collection = db.get_collection("alerts")
        total_count = alerts_collection.count_documents({})
        print(f"Total alerts: {total_count}\n")
        
        if total_count == 0:
            print("[WARNING] No alerts found in collection!")
            return
        
        # Get recent alerts
        print("Recent alerts (last 5):")
        recent_alerts = list(alerts_collection.find().sort("_id", -1).limit(5))
        
        for i, alert in enumerate(recent_alerts, 1):
            print(f"\n--- Alert {i} ---")
            print(f"Keys: {list(alert.keys())}")
            print(f"Full document:")
            # Convert ObjectId to string for JSON serialization
            alert_dict = {}
            for key, value in alert.items():
                if hasattr(value, '__str__'):
                    alert_dict[key] = str(value)
                else:
                    alert_dict[key] = value
            print(json.dumps(alert_dict, indent=2, default=str))
        
        # Analyze schema
        print("\n" + "=" * 80)
        print("Step 3: Schema Analysis")
        print("=" * 80)
        
        # Collect all unique keys from recent alerts
        all_keys = set()
        for alert in recent_alerts:
            all_keys.update(alert.keys())
        
        print(f"\nAll unique keys found: {sorted(all_keys)}")
        
        # Check for common ID fields
        print("\nID fields found:")
        id_fields = ['ext_id', 'alert_id', '_id', 'id', 'alertIds', 'alertId']
        for field in id_fields:
            found = any(field in alert for alert in recent_alerts)
            if found:
                sample_values = [alert.get(field) for alert in recent_alerts if field in alert]
                print(f"  [OK] {field}: Found (sample: {sample_values[0] if sample_values else 'N/A'})")
            else:
                print(f"  [FAIL] {field}: Not found")
        
        # Test search patterns
        print("\n" + "=" * 80)
        print("Step 4: Testing Search Patterns")
        print("=" * 80)
        
        if recent_alerts:
            test_alert = recent_alerts[0]
            print(f"\nUsing test alert: {test_alert.get('_id')}")
            
            # Try different search patterns
            search_patterns = [
                {"_id": test_alert.get('_id')},
                {"ext_id": test_alert.get('ext_id')} if 'ext_id' in test_alert else None,
                {"alert_id": test_alert.get('alert_id')} if 'alert_id' in test_alert else None,
                {"id": test_alert.get('id')} if 'id' in test_alert else None,
            ]
            
            for pattern in search_patterns:
                if pattern:
                    result = alerts_collection.find_one(pattern)
                    if result:
                        print(f"  [OK] Found with pattern: {pattern}")
                    else:
                        print(f"  [FAIL] Not found with pattern: {pattern}")
        
        print("\n" + "=" * 80)
        print("Investigation Complete")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        mongodb_manager.disconnect()
        print("\n[OK] Disconnected from MongoDB")

if __name__ == "__main__":
    main()

