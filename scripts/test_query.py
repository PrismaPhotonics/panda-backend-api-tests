"""Test the exact query our code runs."""
import pymongo
from datetime import datetime, timedelta

# Connect directly to MongoDB (kefar_saba environment)
client = pymongo.MongoClient(
    '10.10.100.108', 27017, 
    username='prisma', password='prisma', 
    authSource='prisma',
    serverSelectionTimeoutMS=5000
)

db = client['prisma']

print('='*70)
print('SIMULATING EXACT QUERY FROM recording_fixtures.py')
print('='*70)

# Step 1: Find base_path document
base_paths = db["base_paths"]
# Try the path the code uses
base_path_doc = base_paths.find_one({
    "base_path": "/prisma/root/recordings/segy",
    "is_archive": False
})

if not base_path_doc:
    print("❌ No base_path found for /prisma/root/recordings/segy")
    # Try alternate path
    base_path_doc = base_paths.find_one({
        "base_path": "/prisma/root/recordings",
        "is_archive": False
    })
    if base_path_doc:
        print("✓ Found base_path for /prisma/root/recordings instead!")
    else:
        print("❌ No base_path found for either path!")
        client.close()
        exit(1)
else:
    print("✓ Found base_path for /prisma/root/recordings/segy")

guid = base_path_doc.get("guid")
print(f"  guid: {guid}")

# Step 2: Query recordings
collection_name = str(guid)
recordings_collection = db[collection_name]

# Parameters matching the test
weeks_back = 4
min_duration_seconds = 5.0
max_duration_seconds = 300.0
max_recordings = 500

now = datetime.now()
weeks_ago = now - timedelta(weeks=weeks_back)

print(f"\nQuery parameters:")
print(f"  weeks_back: {weeks_back}")
print(f"  Time range: {weeks_ago.strftime('%Y-%m-%d %H:%M')} to {now.strftime('%Y-%m-%d %H:%M')}")
print(f"  min_duration: {min_duration_seconds}s")
print(f"  max_duration: {max_duration_seconds}s")

query = {
    "start_time": {
        "$gte": weeks_ago,
        "$lte": now
    },
    "deleted": False
}

print(f"\nMongoDB query: {query}")

total_matching = recordings_collection.count_documents(query)
print(f"\n✓ Query matches: {total_matching} recordings")

if total_matching > 0:
    # Fetch and filter by duration
    cursor = recordings_collection.find(query).sort([("start_time", pymongo.DESCENDING)]).limit(max_recordings * 10)
    
    recordings = []
    skipped_duration = 0
    skipped_no_times = 0
    
    for doc in cursor:
        start_time = doc.get("start_time")
        end_time = doc.get("end_time")
        
        if not start_time or not end_time:
            skipped_no_times += 1
            continue
        
        duration = (end_time - start_time).total_seconds()
        
        if duration < min_duration_seconds or duration > max_duration_seconds:
            skipped_duration += 1
            continue
        
        # This would be a valid recording
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)
        recordings.append((start_ms, end_ms, duration))
        
        if len(recordings) >= max_recordings:
            break
    
    print(f"\nAfter duration filter ({min_duration_seconds}s - {max_duration_seconds}s):")
    print(f"  Valid recordings: {len(recordings)}")
    print(f"  Skipped (no times): {skipped_no_times}")
    print(f"  Skipped (wrong duration): {skipped_duration}")
    
    if recordings:
        print(f"\nSample valid recordings (first 5):")
        for i, (start_ms, end_ms, dur) in enumerate(recordings[:5]):
            start_dt = datetime.fromtimestamp(start_ms / 1000)
            end_dt = datetime.fromtimestamp(end_ms / 1000)
            print(f"  {i+1}. {start_dt} -> {end_dt} ({dur:.1f}s)")
            print(f"     start_ms={start_ms}, end_ms={end_ms}")
else:
    print("❌ No recordings match the query!")

client.close()

