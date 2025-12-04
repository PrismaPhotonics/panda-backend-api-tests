# 🔴 Issue: Focus Server Cannot Find Recordings in MongoDB

**Date:** 2025-12-01  
**Environment:** Staging  
**Severity:** Critical - Historic Playback not working

---

## 📋 Problem Summary

Focus Server returns error `"No recording found in given time range"` when trying to create Historic Playback jobs, despite having **41,244 completed recordings** in MongoDB.

---

## 🔍 What We Found

### 1. MongoDB Structure - base_paths

There are **two** base_paths in MongoDB:

| base_path | GUID | Recordings | Notes |
|-----------|------|------------|-------|
| `/prisma/root/recordings` | `25b4875f-5785-4b24-8895-121039474bcd` | **41,244 completed** | ✅ This is the relevant one |
| `/prisma/root/recordings/segy` | `873ea296-a3a3-4c22-a880-608766f004cd` | ? | ❌ Not relevant |

### 2. Our Automation Works Correctly ✅

Our automation:
1. Searches `base_paths` for document with `base_path = "/prisma/root/recordings"`
2. Extracts GUID: `25b4875f-5785-4b24-8895-121039474bcd`
3. Accesses collection with that name
4. Finds all recordings successfully

**Result:** Our automation successfully finds all recordings.

### 3. Focus Server Cannot Find Them ❌

When trying to create Historic Playback job via Focus Server API:

```bash
POST /focus-server/configure
{
  "start_time": 1764593789,
  "end_time": 1764593829,
  ...
}
```

**Response:**
```json
{
  "error": "No recording found in given time range"
}
```

**HTTP Status:** 404

---

## 🎯 Root Cause Analysis

Focus Server is likely searching `base_paths` for a document matching `storage_mount_path` from configuration.

### Current Configuration:

```python
# default_config.py (from ConfigMap: prisma-config)
class Focus:
    storage_mount_path = '/prisma/root/recordings/segy'  # ❌ This is wrong!
```

### What Focus Server Probably Does:

1. Takes `storage_mount_path = '/prisma/root/recordings/segy'`
2. Searches `base_paths` for document with `base_path = '/prisma/root/recordings/segy'`
3. Finds GUID: `873ea296-a3a3-4c22-a880-608766f004cd`
4. Searches for recordings in that collection (which is likely empty or not relevant)

### What Focus Server Should Do:

1. **DO NOT use `storage_mount_path` to find GUID!**
2. Search `base_paths` for document with `base_path = '/prisma/root/recordings'`
3. Extract GUID: `25b4875f-5785-4b24-8895-121039474bcd`
4. Search for recordings in that collection

---

## ✅ Solution

### Option 1: Fix Focus Server Logic (Recommended)

Focus Server should change `RecordingMongoMapper` logic to:

1. **NOT use `storage_mount_path` to find GUID**
2. Search `base_paths` for document with `base_path = '/prisma/root/recordings'` (or another configured base_path)
3. Use that GUID to access recordings

**Example Code (Python):**
```python
# Instead of:
base_path_doc = base_paths.find_one({"base_path": storage_mount_path})

# Should be:
base_path_doc = base_paths.find_one({
    "base_path": "/prisma/root/recordings",
    "is_archive": False
})
```

### Option 2: Fix Configuration (Temporary)

If `storage_mount_path` is actually used for something else (not for finding GUID), then Focus Server logic needs to be fixed.

But if `storage_mount_path` should be `/prisma/root/recordings` (not `/prisma/root/recordings/segy`), then update the ConfigMap:

```yaml
# ConfigMap: prisma-config
data:
  default_config.py: |
    class Focus:
      storage_mount_path = '/prisma/root/recordings'  # ✅ Fix
```

---

## 🧪 How to Verify the Fix Works

### 1. Manual Check via MongoDB:

```python
import pymongo

client = pymongo.MongoClient("mongodb://prisma:prisma@10.10.10.108:27017/?authSource=prisma")
db = client["prisma"]

# Check base_paths
base_paths = db["base_paths"]
for doc in base_paths.find():
    print(f"base_path: {doc['base_path']}, guid: {doc['guid']}")

# Check recordings in correct GUID
guid = "25b4875f-5785-4b24-8895-121039474bcd"
collection = db[guid]
count = collection.count_documents({"deleted": False, "end_time": {"$ne": None}})
print(f"Completed recordings: {count}")
```

### 2. Check via Focus Server API:

```bash
# Get time range from MongoDB
start_time=1764593789
end_time=1764593829

# Try to create Historic job
curl -X POST https://10.10.10.100/focus-server/configure \
  -H "Content-Type: application/json" \
  -d '{
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "channels": {"min": 1, "max": 17},
    "start_time": '$start_time',
    "end_time": '$end_time'
  }'
```

**Expected Result:** Job ID instead of "No recording found" error.

### 3. Check via Automation:

```bash
# Run Historic Playback tests
pytest be_focus_server_tests/integration/api/test_historic_playback_e2e.py -v
```

**Expected Result:** All tests pass ✅

---

## 📊 Additional Data

### MongoDB Collections:

- **Database:** `prisma`
- **base_paths collection:** Contains 2 documents
- **Recording collection (GUID):** `25b4875f-5785-4b24-8895-121039474bcd`
- **Total recordings:** 41,244 completed (not deleted, with end_time)

### Focus Server:

- **Pod:** `panda-panda-focus-server` (namespace: `panda`)
- **ConfigMap:** `prisma-config`
- **Config path:** `/home/prisma/.local/lib/python3.10/site-packages/pzpy/focus_server/default_config.py`

---

## 📝 Important Notes

1. **`storage_mount_path` is NOT relevant for finding GUID!**
   - It's just a disk path, not related to MongoDB collections
   - Focus Server should use `base_path` from `base_paths` to find GUID

2. **There are two base_paths in MongoDB:**
   - `/prisma/root/recordings` - This is the relevant one (41K recordings)
   - `/prisma/root/recordings/segy` - Not relevant

3. **Our automation already works correctly:**
   - Uses the correct GUID
   - Finds all recordings
   - The issue is only in Focus Server itself

---

## 🔗 Relevant Files

### In Our Code:
- `be_focus_server_tests/fixtures/recording_fixtures.py` - Logic for finding GUID
- `be_focus_server_tests/data_quality/test_mongodb_data_quality.py` - Using GUID
- `scripts/test_focus_api_direct.py` - Focus Server API check

### In Focus Server (Needs Fix):
- `RecordingMongoMapper` - Logic for finding GUID from base_paths
- `default_config.py` - Configuration (ConfigMap)

---

## ✅ Summary

**Problem:** Focus Server searches for recordings in the wrong collection due to incorrect use of `storage_mount_path`.

**Solution:** Focus Server should change logic to search `base_paths` for `base_path = '/prisma/root/recordings'` and use that GUID, **regardless of `storage_mount_path`**.

**Important:** `storage_mount_path` is just a disk path, not related to MongoDB collections!

---

**Written by:** QA Automation Team  
**Date:** 2025-12-01
