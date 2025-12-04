#!/usr/bin/env python3
"""
Check MongoDB recordings to understand timestamp format.
"""

import pymongo
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_manager import ConfigManager

def main():
    cm = ConfigManager()
    mongo_config = cm.get_database_config()

    client = pymongo.MongoClient(
        host=mongo_config['host'],
        port=mongo_config['port'],
        username=mongo_config['username'],
        password=mongo_config['password'],
        authSource=mongo_config.get('auth_source', 'prisma')
    )

    db = client['prisma']
    base_paths = db['base_paths']
    doc = base_paths.find_one()
    guid = doc.get('guid')

    rec_coll = db[str(guid)]

    # Find COMPLETED recording (end_time is NOT None)
    print("=" * 60)
    print("Latest COMPLETED recordings:")
    print("=" * 60)
    
    query = {'deleted': False, 'end_time': {'$ne': None}}
    cursor = rec_coll.find(query).sort([('start_time', -1)]).limit(5)
    
    for i, rec in enumerate(cursor, 1):
        start = rec.get('start_time')
        end = rec.get('end_time')
        
        if start and end:
            duration = (end - start).total_seconds()
            start_ts = int(start.timestamp())
            end_ts = int(end.timestamp())
            
            print(f"\n{i}. Recording:")
            print(f"   MongoDB datetime: {start} to {end}")
            print(f"   Duration: {duration:.1f} seconds")
            print(f"   Unix timestamp (sec): {start_ts} to {end_ts}")
            print(f"   Verify: {datetime.fromtimestamp(start_ts)} to {datetime.fromtimestamp(end_ts)}")

    client.close()


if __name__ == "__main__":
    main()

