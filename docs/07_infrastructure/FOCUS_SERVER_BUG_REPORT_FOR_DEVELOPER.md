# 🐛 Bug Report: Focus Server Cannot Find Recordings in MongoDB

**Date:** 2025-12-01  
**Environment:** Staging (Panda)  
**Severity:** Critical - Historic Playback completely broken  
**Component:** Focus Server - RecordingMongoMapper  
**Reporter:** QA Automation Team

---

## 📋 Executive Summary

Focus Server returns **404 "No recording found in given time range"** when trying to create Historic Playback jobs, despite having **25,753+ completed recordings** in MongoDB that match the requested time range.

**Impact:** Historic Playback feature is completely non-functional.

---

## 🔍 Problem Description

### What Happens:

1. **Our automation** queries MongoDB directly and successfully finds recordings:
   - Collection: `25b4875f-5785-4b24-8895-121039474bcd`
   - Found: **25,753 recordings** matching criteria (duration 5-10 seconds, last 2 weeks, `deleted: false`)
   - Example recording: `start_time: 2025-12-01 19:13:29`, `end_time: 2025-12-01 19:13:39`

2. **We send request to Focus Server:**
   ```json
   POST /focus-server/configure
   {
     "start_time": 1764609209,  // Unix timestamp
     "end_time": 1764609219,    // Unix timestamp
     "displayTimeAxisDuration": 10,
     "nfftSelection": 1024,
     "channels": {"min": 1, "max": 50},
     "frequencyRange": {"min": 0, "max": 500},
     "view_type": "0"
   }
   ```

3. **Focus Server responds:**
   ```json
   {
     "error": "No recording found in given time range"
   }
   ```
   **HTTP Status:** 404

### Expected Behavior:

Focus Server should find the recording and return a job ID.

---

## 🔬 Root Cause Analysis

### MongoDB Structure:

**Database:** `prisma`

**Collection: `base_paths`** (contains 2 documents):
```json
[
  {
    "base_path": "/prisma/root/recordings",
    "guid": "25b4875f-5785-4b24-8895-121039474bcd",
    "is_archive": false
  },
  {
    "base_path": "/prisma/root/recordings/segy",
    "guid": "873ea296-a3a3-4c22-a880-608766f004cd",
    "is_archive": false
  }
]
```

**Recording Collection:** `25b4875f-5785-4b24-8895-121039474bcd`
- Contains **25,753+ completed recordings**
- All have `deleted: false`
- All have `start_time` and `end_time` fields
- Time range: Last 2 weeks

### Our Automation (Works Correctly ✅):

```python
# Step 1: Query base_paths for correct base_path
base_path_doc = base_paths.find_one({
    "base_path": "/prisma/root/recordings",
    "is_archive": False
})

# Step 2: Extract GUID
guid = base_path_doc["guid"]  # "25b4875f-5785-4b24-8895-121039474bcd"

# Step 3: Query recordings collection
recordings_collection = db[guid]
recordings = recordings_collection.find({
    "start_time": {"$gte": start_time, "$lte": end_time},
    "deleted": False
})
# ✅ Successfully finds 25,753 recordings
```

### Focus Server (Broken ❌):

**Hypothesis:** Focus Server's `RecordingMongoMapper` is likely:

1. **Using `storage_mount_path` to find GUID** (WRONG):
   ```python
   # Current (incorrect) logic:
   base_path_doc = base_paths.find_one({
       "base_path": Config.Focus.storage_mount_path  # '/prisma/root/recordings/segy'?
   })
   ```

2. **Or not querying the correct collection** after finding GUID

3. **Or not filtering by `deleted: false`**

---

## ✅ Configuration Status

### ConfigMap: `prisma-config` (namespace: `panda`)

**Current Configuration:**
```python
class Focus:
    storage_mount_path = '/prisma/root/recordings'  # ✅ Correct
    k8s_mode = True
    focus_view_url = 'http://10.10.10.150'
    # ... other config ...
```

**Status:** ✅ ConfigMap is correctly configured  
**Pod Restart:** ✅ Pod was restarted after ConfigMap update  
**Verification:** ✅ ConfigMap contains correct `storage_mount_path`

---

## 🧪 Test Case That Fails

**Test File:** `be_focus_server_tests/integration/api/test_historic_playback_e2e.py`  
**Test Method:** `test_historic_playback_complete_e2e_flow`

**Steps:**
1. Query MongoDB directly for recordings (✅ Works - finds 25,753 recordings)
2. Extract time range from first recording: `start_time: 1764609209, end_time: 1764609219`
3. Send `POST /focus-server/configure` with this time range
4. **Expected:** Job ID returned  
   **Actual:** 404 "No recording found in given time range"

**Error Log:**
```
2025-12-01 21:25:58 [    INFO] be_focus_server_tests.fixtures.recording_fixtures: 📊 MongoDB query found 25753 recordings matching:
2025-12-01 21:25:58 [    INFO] be_focus_server_tests.fixtures.recording_fixtures:    - Collection: 25b4875f-5785-4b24-8895-121039474bcd
2025-12-01 21:25:58 [    INFO] be_focus_server_tests.fixtures.recording_fixtures:    - Time range: 2025-11-17 21:25:58 to 2025-12-01 21:25:58
2025-12-01 21:25:58 [    INFO] be_focus_server_tests.fixtures.recording_fixtures:    - deleted: false

2025-12-01 21:25:58 [    INFO] src.apis.focus_server_api: >> POST https://10.10.10.100/focus-server/configure
2025-12-01 21:25:58 [    INFO] src.apis.focus_server_api:     "start_time": 1764609209,
2025-12-01 21:25:58 [    INFO] src.apis.focus_server_api:     "end_time": 1764609219,

2025-12-01 21:22:27 [   ERROR] src.apis.focus_server_api: << 404 Not Found (5715.82ms)
2025-12-01 21:22:27 [   ERROR] src.apis.focus_server_api:     "error": "No recording found in given time range"
```

---

## 🔧 What Needs to Be Fixed

### Option 1: Fix RecordingMongoMapper Logic (Recommended)

**File:** `pzpy/focus_server/recording_mongo_mapper.py` (or equivalent)

**Current Logic (Hypothesis - needs verification):**
```python
# WRONG: Using storage_mount_path to find GUID
base_path_doc = base_paths.find_one({
    "base_path": Config.Focus.storage_mount_path
})
```

**Should Be:**
```python
# CORRECT: Use fixed base_path, not storage_mount_path
base_path_doc = base_paths.find_one({
    "base_path": "/prisma/root/recordings",
    "is_archive": False
})

# OR: Make it configurable via a separate config field
base_path_doc = base_paths.find_one({
    "base_path": Config.Focus.recording_base_path or "/prisma/root/recordings",
    "is_archive": False
})
```

**Key Points:**
1. **`storage_mount_path` is NOT related to MongoDB collections!**
   - It's just a disk path for file storage
   - Should NOT be used to find GUID in `base_paths`

2. **Always use `base_path = "/prisma/root/recordings"`** (not `/prisma/root/recordings/segy`)

3. **Always filter by `deleted: false`** when querying recordings

4. **Always filter by `is_archive: false`** when querying `base_paths`

### Option 2: Add Configuration Field

If `storage_mount_path` is used for something else, add a new config field:

```python
class Focus:
    storage_mount_path = '/prisma/root/recordings'  # For file storage
    recording_base_path = '/prisma/root/recordings'  # For MongoDB base_paths lookup
```

---

## 📊 Evidence & Data

### MongoDB Query (Our Automation - Works):

```python
# Connection
mongo_client = MongoClient("mongodb://prisma:prisma@10.10.10.108:27017/?authSource=prisma")
db = mongo_client["prisma"]

# Get GUID
base_paths = db["base_paths"]
base_path_doc = base_paths.find_one({
    "base_path": "/prisma/root/recordings",
    "is_archive": False
})
guid = base_path_doc["guid"]  # "25b4875f-5785-4b24-8895-121039474bcd"

# Query recordings
recordings_collection = db[guid]
count = recordings_collection.count_documents({
    "start_time": {
        "$gte": datetime(2025, 11, 17),
        "$lte": datetime(2025, 12, 1)
    },
    "deleted": False
})
# Result: 25,753 recordings ✅
```

### Example Recording (Found in MongoDB):

```json
{
  "_id": {"$oid": "692dcd664db0a43e1c3f4129"},
  "uuid": "894b93f0-9085-4815-97ff-33da7ff64eff",
  "start_time": {"$date": "2025-12-01T17:13:29.760Z"},
  "end_time": {"$date": "2025-12-01T17:13:39.759Z"},
  "deleted": false,
  "fiber_metadata": {
    "layer_type": "smart_recorder",
    "version": "TLV-1.3",
    "num_traces": 10000
  }
}
```

**Time Range Sent to Focus Server:**
- `start_time`: 1764609209 (Unix timestamp = 2025-12-01 17:13:29 UTC)
- `end_time`: 1764609219 (Unix timestamp = 2025-12-01 17:13:39 UTC)

**This recording EXISTS in MongoDB but Focus Server cannot find it!**

---

## 🔍 Debugging Steps for Developer

### 1. Check RecordingMongoMapper Logic

**Location:** `pzpy/focus_server/recording_mongo_mapper.py`

**Questions to Answer:**
- How does it find the GUID from `base_paths`?
- Does it use `storage_mount_path`? (Should NOT!)
- Does it filter by `is_archive: false`?
- Does it filter recordings by `deleted: false`?

### 2. Add Debug Logging

Add logging to see what Focus Server is doing:

```python
logger.info(f"Looking for base_path: {base_path_to_search}")
logger.info(f"Found base_path_doc: {base_path_doc}")
logger.info(f"Using GUID: {guid}")
logger.info(f"Querying collection: {collection_name}")
logger.info(f"Query filter: {query_filter}")
logger.info(f"Found {count} recordings matching query")
```

### 3. Test with Direct MongoDB Query

Run this query inside Focus Server pod to verify it can access MongoDB:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://prisma:prisma@mongodb:27017/?authSource=prisma")
db = client["prisma"]

# Check base_paths
base_paths = db["base_paths"]
for doc in base_paths.find():
    print(f"base_path: {doc['base_path']}, guid: {doc['guid']}")

# Check recordings
guid = "25b4875f-5785-4b24-8895-121039474bcd"
collection = db[guid]
count = collection.count_documents({
    "start_time": {"$gte": datetime(2025, 12, 1, 17, 13, 29), "$lte": datetime(2025, 12, 1, 17, 13, 39)},
    "deleted": False
})
print(f"Found {count} recordings")
```

---

## 📝 Files to Check

### Focus Server Code:
- `pzpy/focus_server/recording_mongo_mapper.py` - Main logic for finding recordings
- `pzpy/focus_server/default_config.py` - Configuration (from ConfigMap)
- `pzpy/focus_server/api/configure.py` - Configure endpoint handler

### Our Automation Code (Reference - Works Correctly):
- `be_focus_server_tests/fixtures/recording_fixtures.py` - Lines 709-756 (MongoDB query logic)
- `be_focus_server_tests/integration/api/test_historic_playback_e2e.py` - Test that fails

---

## ✅ Acceptance Criteria

The fix is correct when:

1. ✅ Focus Server can find recordings that exist in MongoDB
2. ✅ `POST /focus-server/configure` returns job ID (not 404)
3. ✅ Historic Playback jobs can be created successfully
4. ✅ Test `test_historic_playback_complete_e2e_flow` passes

---

## 📞 Contact & Additional Information

**Environment Details:**
- **Kubernetes Namespace:** `panda`
- **Focus Server Pod:** `panda-panda-focus-server-*`
- **MongoDB:** `10.10.10.108:27017` (via SSH tunnel)
- **Focus Server API:** `https://10.10.10.100/focus-server`

**Test Logs:**
- Full test logs: `logs/test_runs/2025-12-01_21-27-08_integration_tests.log`
- Error logs: `logs/errors/2025-12-01_21-27-08_integration_tests_ERRORS.log`

**Reproduction:**
```bash
# Run the failing test
pytest be_focus_server_tests/integration/api/test_historic_playback_e2e.py::TestHistoricPlaybackCompleteE2E::test_historic_playback_complete_e2e_flow -v
```

---

## 🎯 Summary

**Problem:** Focus Server cannot find recordings that exist in MongoDB.

**Root Cause:** Likely incorrect logic in `RecordingMongoMapper` - using `storage_mount_path` to find GUID instead of using fixed `base_path = "/prisma/root/recordings"`.

**Solution:** Fix `RecordingMongoMapper` to:
1. Query `base_paths` with `base_path = "/prisma/root/recordings"` (NOT using `storage_mount_path`)
2. Use GUID `25b4875f-5785-4b24-8895-121039474bcd` to access recordings collection
3. Filter by `deleted: false` when querying recordings
4. Filter by `is_archive: false` when querying `base_paths`

**Critical:** `storage_mount_path` is a disk path, NOT related to MongoDB collections!

---

**Reported by:** QA Automation Team  
**Date:** 2025-12-01  
**Priority:** Critical - Blocks Historic Playback feature

