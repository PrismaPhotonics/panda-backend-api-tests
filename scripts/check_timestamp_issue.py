"""Debug timestamp conversion issue."""
import pymongo
from datetime import datetime, timedelta, timezone
import requests
import urllib3
urllib3.disable_warnings()

print("="*70)
print("TIMESTAMP ANALYSIS")
print("="*70)

# Connect to MongoDB
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

# Get a recent recording with end_time
rec = coll.find_one({'end_time': {'$ne': None}}, sort=[('start_time', -1)])
start_time = rec.get('start_time')
end_time = rec.get('end_time')

print(f"\nMongoDB Recording:")
print(f"  start_time (raw): {start_time}")
print(f"  end_time (raw): {end_time}")
print(f"  type: {type(start_time)}")

# Check if the datetime is timezone-aware
if start_time.tzinfo is None:
    print(f"  timezone: NAIVE (no timezone info)")
else:
    print(f"  timezone: {start_time.tzinfo}")

# Convert to epoch - THIS IS THE PROBLEM!
# If datetime is naive, timestamp() assumes LOCAL timezone
start_epoch_local = int(start_time.timestamp())
print(f"\nEpoch conversion (assuming local timezone):")
print(f"  start_epoch: {start_epoch_local}")
print(f"  back to datetime: {datetime.fromtimestamp(start_epoch_local)}")

# If MongoDB stores UTC, we should treat it as UTC
start_utc = start_time.replace(tzinfo=timezone.utc)
start_epoch_utc = int(start_utc.timestamp())
print(f"\nEpoch conversion (treating as UTC):")
print(f"  start_epoch: {start_epoch_utc}")
print(f"  back to datetime (UTC): {datetime.utcfromtimestamp(start_epoch_utc)}")
print(f"  back to datetime (local): {datetime.fromtimestamp(start_epoch_utc)}")

# The difference
diff_seconds = start_epoch_local - start_epoch_utc
print(f"\nDifference: {diff_seconds} seconds ({diff_seconds/3600:.1f} hours)")

# Test with Focus Server
print("\n" + "="*70)
print("TESTING WITH FOCUS SERVER")
print("="*70)

# Try with LOCAL timestamp (WRONG)
payload_local = {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {"height": 600},
    "channels": {"min": 1, "max": 50},
    "frequencyRange": {"min": 0, "max": 500},
    "start_time": start_epoch_local,
    "end_time": start_epoch_local + 10,
    "view_type": "0"
}

print(f"\n1. Testing with LOCAL timestamp: {start_epoch_local}")
print(f"   (represents: {datetime.fromtimestamp(start_epoch_local)})")
resp = requests.post(
    "https://10.10.100.100/focus-server/configure",
    json=payload_local,
    verify=False,
    timeout=30
)
print(f"   Response: {resp.status_code} - {resp.text[:100]}")

# Try with UTC timestamp (CORRECT?)
payload_utc = {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {"height": 600},
    "channels": {"min": 1, "max": 50},
    "frequencyRange": {"min": 0, "max": 500},
    "start_time": start_epoch_utc,
    "end_time": start_epoch_utc + 10,
    "view_type": "0"
}

print(f"\n2. Testing with UTC timestamp: {start_epoch_utc}")
print(f"   (represents: {datetime.utcfromtimestamp(start_epoch_utc)} UTC)")
resp = requests.post(
    "https://10.10.100.100/focus-server/configure",
    json=payload_utc,
    verify=False,
    timeout=30
)
print(f"   Response: {resp.status_code} - {resp.text[:100]}")

client.close()

