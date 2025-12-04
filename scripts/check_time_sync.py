"""Check time synchronization between MongoDB recordings and Focus Server."""
import pymongo
from datetime import datetime, timedelta
import requests
import urllib3
urllib3.disable_warnings()

# Connect to MongoDB
print("="*70)
print("MongoDB Time Analysis")
print("="*70)

client = pymongo.MongoClient(
    '10.10.100.108', 27017, 
    username='prisma', password='prisma', 
    authSource='prisma',
    serverSelectionTimeoutMS=5000
)

db = client['prisma']
bp = db['base_paths'].find_one({'is_archive': False})
guid = bp['guid']
coll = db[guid]

now = datetime.now()
print(f"Current local time: {now}")
print(f"Current UTC time: {datetime.utcnow()}")

# Get recording time range
oldest = coll.find_one(sort=[('start_time', 1)])
newest = coll.find_one(sort=[('start_time', -1)])

print(f"\nMongoDB Recordings in collection '{guid}':")
print(f"  Total: {coll.count_documents({})}")
print(f"  Oldest: {oldest.get('start_time')}")
print(f"  Newest: {newest.get('start_time')}")

# Check if newest recording is recent
newest_time = newest.get('start_time')
if newest_time:
    time_diff = now - newest_time
    print(f"  Time since newest: {time_diff}")

# Get the 5 most recent recordings
print("\nLatest 5 recordings (with epoch timestamps):")
for rec in coll.find({'end_time': {'$ne': None}}).sort('start_time', -1).limit(5):
    start = rec.get('start_time')
    end = rec.get('end_time')
    if start and end:
        start_epoch = int(start.timestamp())
        end_epoch = int(end.timestamp())
        duration = (end - start).total_seconds()
        print(f"  {start} -> {end} ({duration:.1f}s)")
        print(f"    Epoch: start={start_epoch}, end={end_epoch}")

client.close()

# Now check Focus Server
print("\n" + "="*70)
print("Focus Server Time Check")
print("="*70)

# Try to create a job with the newest recording
if newest_time:
    start_epoch = int(newest_time.timestamp())
    # Add 10 seconds for end time
    end_epoch = start_epoch + 10
    
    print(f"\nTrying to create job with:")
    print(f"  start_time: {start_epoch} ({datetime.fromtimestamp(start_epoch)})")
    print(f"  end_time: {end_epoch} ({datetime.fromtimestamp(end_epoch)})")
    
    payload = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 600},
        "channels": {"min": 1, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": start_epoch,
        "end_time": end_epoch,
        "view_type": "0"
    }
    
    try:
        resp = requests.post(
            "https://10.10.100.100/focus-server/configure",
            json=payload,
            verify=False,
            timeout=30
        )
        print(f"\nFocus Server response: {resp.status_code}")
        print(f"  Body: {resp.text[:500]}")
    except Exception as e:
        print(f"\nFocus Server error: {e}")

# Check server time via API
print("\n" + "="*70)
print("Server Time Check")
print("="*70)
try:
    resp = requests.get("https://10.10.100.100/focus-server/ack", verify=False, timeout=10)
    server_date = resp.headers.get('date', 'N/A')
    print(f"Focus Server response date header: {server_date}")
    print(f"Local time: {datetime.now()}")
except Exception as e:
    print(f"Error checking server: {e}")

