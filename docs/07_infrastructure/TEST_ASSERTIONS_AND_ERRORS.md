# Test Assertions and Errors - Historic Playback E2E Test

**Test:** `be_focus_server_tests/integration/api/test_historic_playback_e2e.py::TestHistoricPlaybackCompleteE2E::test_historic_playback_complete_e2e_flow`  
**Run Date:** 2025-12-01 21:34:11  
**Status:** FAILED  
**Duration:** 56.71s

---

## 📋 Test Assertion That Failed

### Assertion Error:

```
AssertionError: Focus Server cannot find recording that exists in MongoDB. 
Time range: 2025-12-01 19:29:09 to 2025-12-01 19:29:19. 
Error: API call failed: No recording found in given time range
```

### Location in Code:

**File:** `be_focus_server_tests/integration/api/test_historic_playback_e2e.py`  
**Lines:** 193-196

```python
raise AssertionError(
    f"Focus Server cannot find recording that exists in MongoDB. "
    f"Time range: {start_time_dt} to {end_time_dt}. "
    f"Error: {e}"
)
```

---

## 🔍 What Happened - Step by Step

### Step 1: MongoDB Query (✅ SUCCESS)

**Query Details:**
- **Collection:** `25b4875f-5785-4b24-8895-121039474bcd`
- **Time Range:** 2025-11-17 21:27:52 to 2025-12-01 21:27:52 (last 2 weeks)
- **Filter:** `deleted: false`
- **Duration Filter:** 5.0-10.0 seconds

**Results:**
- ✅ Found **25,751 recordings** matching criteria
- ✅ Selected first recording:
  - **Start Time:** 2025-12-01 19:29:09 UTC
  - **End Time:** 2025-12-01 19:29:19 UTC
  - **Duration:** 10.0 seconds
  - **UUID:** `6f665eb5-482a-4069-bbff-3227a1d1fb04`
  - **Status:** `deleted: false`

**MongoDB Query Log:**
```
2025-12-01 21:27:52 [    INFO] MongoDB query found 25751 recordings matching:
   - Collection: 25b4875f-5785-4b24-8895-121039474bcd
   - Time range: 2025-11-17 21:27:52.862871 to 2025-12-01 21:27:52.862871
   - deleted: false
```

**Selected Recording:**
```
Recording 1: 2025-12-01 19:29:09 to 2025-12-01 19:29:19 (10.0s)
```

---

### Step 2: Convert to Unix Timestamps

**Conversion:**
- `start_time_dt`: 2025-12-01 19:29:09 UTC
- `end_time_dt`: 2025-12-01 19:29:19 UTC
- `start_time` (Unix): **1764610149**
- `end_time` (Unix): **1764610159**

---

### Step 3: Send Request to Focus Server (❌ FAILED)

**Request:**
```http
POST https://10.10.10.100/focus-server/configure
Content-Type: application/json
```

**Request Body:**
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {
    "height": 1000
  },
  "channels": {
    "min": 1,
    "max": 50
  },
  "frequencyRange": {
    "min": 0,
    "max": 500
  },
  "start_time": 1764610149,
  "end_time": 1764610159,
  "view_type": "0"
}
```

**Request Log:**
```
2025-12-01 21:34:11 [    INFO] >> POST https://10.10.10.100/focus-server/configure
2025-12-01 21:34:11 [    INFO] Request Body (JSON):
2025-12-01 21:34:11 [    INFO]   {
2025-12-01 21:34:11 [    INFO]     "start_time": 1764610149,
2025-12-01 21:34:11 [    INFO]     "end_time": 1764610159,
2025-12-01 21:34:11 [    INFO]     "view_type": "0"
2025-12-01 21:34:11 [    INFO]   }
```

---

### Step 4: Focus Server Response (❌ 404 ERROR)

**Response:**
```http
HTTP/1.1 404 Not Found
Content-Type: application/json
Content-Length: 50
Date: Mon, 01 Dec 2025 19:35:13 GMT
```

**Response Body:**
```json
{
  "error": "No recording found in given time range"
}
```

**Response Time:** 6102.91ms (6.1 seconds)

**Response Log:**
```
2025-12-01 21:34:11 [    INFO] << 404 Not Found (6102.91ms)
2025-12-01 21:34:11 [    INFO] Response Body (JSON):
2025-12-01 21:34:11 [    INFO]   {
2025-12-01 21:34:11 [    INFO]     "error": "No recording found in given time range"
2025-12-01 21:34:11 [    INFO]   }
```

---

### Step 5: Error Handling and Assertion

**Error Log:**
```
2025-12-01 21:34:11 [   ERROR] Full error response: {'error': 'No recording found in given time range'}
2025-12-01 21:34:11 [   ERROR] HTTP 404 error for https://10.10.10.100/focus-server/configure: No recording found in given time range
2025-12-01 21:34:11 [   ERROR] Failed to configure streaming job: API call failed: No recording found in given time range
2025-12-01 21:34:11 [   ERROR] ❌ Focus Server returned 404 'No recording found' for time range 2025-12-01 19:29:09 to 2025-12-01 19:29:19. Recording exists in MongoDB (collection: 25b4875f-5785-4b24-8895-121039474bcd) but Focus Server cannot access it. This indicates a Focus Server configuration issue - check storage_mount_path and base_paths mapping.
```

**Assertion Raised:**
```python
AssertionError: Focus Server cannot find recording that exists in MongoDB. 
Time range: 2025-12-01 19:29:09 to 2025-12-01 19:29:19. 
Error: API call failed: No recording found in given time range
```

---

## 📊 Evidence Summary

### ✅ What Works (Our Automation):

1. **MongoDB Connection:** ✅ Successfully connects via SSH tunnel
2. **base_paths Query:** ✅ Finds correct GUID: `25b4875f-5785-4b24-8895-121039474bcd`
3. **Recordings Query:** ✅ Finds 25,751 recordings matching criteria
4. **Recording Selection:** ✅ Successfully selects valid recording with:
   - `start_time`: 2025-12-01 19:29:09 UTC
   - `end_time`: 2025-12-01 19:29:19 UTC
   - `deleted`: false
   - Duration: 10.0 seconds

### ❌ What Fails (Focus Server):

1. **Recording Lookup:** ❌ Cannot find recording that exists in MongoDB
2. **HTTP Response:** ❌ Returns 404 "No recording found in given time range"
3. **Job Creation:** ❌ Cannot create Historic Playback job

---

## 🔬 Detailed MongoDB Evidence

### Recording Document (Found in MongoDB):

```json
{
  "_id": {"$oid": "692dec2e1433d78ebfd47537"},
  "uuid": "6f665eb5-482a-4069-bbff-3227a1d1fb04",
  "start_time": {"$date": "2025-12-01T19:29:09.020Z"},
  "end_time": {"$date": "2025-12-01T19:29:19.019Z"},
  "deleted": false,
  "fiber_metadata": {
    "layer_type": "smart_recorder",
    "uuid": "6f665eb5-482a-4069-bbff-3227a1d1fb04",
    "version": "TLV-1.3",
    "num_traces": 10000
  }
}
```

### MongoDB Query Used:

```python
# Step 1: Get GUID from base_paths
base_path_doc = base_paths.find_one({
    "base_path": "/prisma/root/recordings",
    "is_archive": False
})
guid = base_path_doc["guid"]  # "25b4875f-5785-4b24-8895-121039474bcd"

# Step 2: Query recordings collection
recordings_collection = db[guid]
query = {
    "start_time": {
        "$gte": datetime(2025, 11, 17, 21, 27, 52),
        "$lte": datetime(2025, 12, 1, 21, 27, 52)
    },
    "deleted": False
}
recordings = recordings_collection.find(query).sort("start_time", -1).limit(500)
# ✅ Found 25,751 recordings
```

---

## 🎯 Key Assertions

### Assertion 1: MongoDB Query Success ✅

**Expected:** MongoDB query should find recordings  
**Actual:** ✅ Found 25,751 recordings  
**Status:** PASS

### Assertion 2: Recording Selection ✅

**Expected:** Should select a valid recording with duration 5-10 seconds  
**Actual:** ✅ Selected recording: 2025-12-01 19:29:09 to 2025-12-01 19:29:19 (10.0s)  
**Status:** PASS

### Assertion 3: Focus Server Configuration ❌

**Expected:** Focus Server should accept configuration and return job ID  
**Actual:** ❌ Focus Server returns 404 "No recording found in given time range"  
**Status:** FAIL

**Assertion Error:**
```
AssertionError: Focus Server cannot find recording that exists in MongoDB. 
Time range: 2025-12-01 19:29:09 to 2025-12-01 19:29:19. 
Error: API call failed: No recording found in given time range
```

---

## 📝 Test Flow Summary

```
1. [✅] Query MongoDB for recordings
   └─> Found 25,751 recordings in collection 25b4875f-5785-4b24-8895-121039474bcd

2. [✅] Select first recording
   └─> Recording: 2025-12-01 19:29:09 to 2025-12-01 19:29:19 (10.0s)

3. [✅] Convert to Unix timestamps
   └─> start_time: 1764610149, end_time: 1764610159

4. [✅] Send POST /focus-server/configure
   └─> Request sent successfully

5. [❌] Focus Server response
   └─> 404 "No recording found in given time range"

6. [❌] Assertion fails
   └─> AssertionError: Focus Server cannot find recording that exists in MongoDB
```

---

## 🔍 Root Cause Analysis

### The Problem:

Focus Server's `RecordingMongoMapper` cannot find recordings that:
1. ✅ Exist in MongoDB
2. ✅ Match the requested time range
3. ✅ Have `deleted: false`
4. ✅ Are in the correct collection (`25b4875f-5785-4b24-8895-121039474bcd`)

### Likely Cause:

Focus Server is likely:
1. Querying the wrong MongoDB collection (wrong GUID)
2. Using incorrect `base_path` to find GUID
3. Not filtering by `deleted: false`
4. Using `storage_mount_path` incorrectly to find GUID

### Evidence:

- **Our automation works correctly** - finds recordings using:
  - `base_path = "/prisma/root/recordings"`
  - GUID: `25b4875f-5785-4b24-8895-121039474bcd`
  - Filter: `deleted: false`

- **Focus Server fails** - cannot find the same recordings

---

## 📋 Complete Test Output

### Short Test Summary:

```
FAILED be_focus_server_tests/integration/api/test_historic_playback_e2e.py::TestHistoricPlaybackCompleteE2E::test_historic_playback_complete_e2e_flow - AssertionError: Focus Server cannot find recording that exists in MongoDB. Time range: 2025-12-01 19:29:09 to 2025-12-01 19:29:19. Error: API call failed: No recording found in given time range
```

### Full Error Trace:

```
ERROR    src.apis.focus_server_api:api_client.py:275 Full error response: {'error': 'No recording found in given time range'}
ERROR    src.apis.focus_server_api:api_client.py:280 HTTP 404 error for https://10.10.10.100/focus-server/configure: No recording found in given time range
ERROR    src.apis.focus_server_api:focus_server_api.py:88 Failed to configure streaming job: API call failed: No recording found in given time range
ERROR    integration.api.test_historic_playback_e2e:test_historic_playback_e2e.py:184 ❌ Focus Server returned 404 'No recording found' for time range 2025-12-01 19:29:09 to 2025-12-01 19:29:19. Recording exists in MongoDB (collection: 25b4875f-5785-4b24-8895-121039474bcd) but Focus Server cannot access it. This indicates a Focus Server configuration issue - check storage_mount_path and base_paths mapping.
```

---

## 📁 Related Files

### Test File:
- `be_focus_server_tests/integration/api/test_historic_playback_e2e.py` (lines 178-196)

### Log Files:
- Main log: `logs/test_runs/2025-12-01_21-34-11_integration_tests.log`
- Error log: `logs/errors/2025-12-01_21-34-11_integration_tests_ERRORS.log`
- Warning log: `logs/warnings/2025-12-01_21-34-11_integration_tests_WARNINGS.log`

### MongoDB Query Code:
- `be_focus_server_tests/fixtures/recording_fixtures.py` (lines 709-756)

---

## ✅ Expected vs Actual

| Step | Expected | Actual | Status |
|------|----------|--------|--------|
| MongoDB Query | Find recordings | ✅ Found 25,751 recordings | ✅ PASS |
| Recording Selection | Select valid recording | ✅ Selected: 2025-12-01 19:29:09-19:29:19 | ✅ PASS |
| Focus Server Configure | Return job ID | ❌ 404 "No recording found" | ❌ FAIL |
| Assertion | Test passes | ❌ AssertionError raised | ❌ FAIL |

---

**Generated:** 2025-12-01  
**Test Run:** 2025-12-01 21:34:11  
**Status:** FAILED


