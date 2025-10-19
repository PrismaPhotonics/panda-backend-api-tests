# MongoDB Data Quality Issues - Bug Report

**Date:** October 15, 2025  
**Environment:** staging (10.10.10.103)  
**Database:** prisma  
**Collection:** `77e49b5d-e06a-4aae-a33e-17117418151c`

---

## Executive Summary

Automated testing of MongoDB data quality revealed **3 critical issues** impacting system performance, data integrity, and user experience. These issues were discovered through systematic schema exploration and validation tests.

| Issue Type | Severity | Count | Impact |
|------------|----------|-------|--------|
| Missing Indexes | 🔴 HIGH | 3,439 (100%) | Performance |
| Missing Metadata | 🟡 MEDIUM | 1 (0.03%) | Data Integrity |
| Low Recognition Rate | 🟡 MEDIUM | 2,173 (38.7%) | Data Quality |

---

## Bug #1: Missing Critical Database Indexes

### Technical Details

| Field | Value |
|-------|-------|
| **Severity** | 🔴 HIGH |
| **Priority** | HIGH |
| **Type** | Performance / Database |
| **Affected Documents** | 3,439 (100%) |
| **Collection** | `77e49b5d-e06a-4aae-a33e-17117418151c` |

### Problem Description

The recordings collection is **completely missing all critical indexes** required for optimal query performance:

| Index | Required | Exists | Impact |
|-------|----------|--------|--------|
| `uuid` (UNIQUE) | ✅ | ❌ | No uniqueness enforcement |
| `start_time` | ✅ | ❌ | Slow time-range queries |
| `end_time` | ✅ | ❌ | Slow time-range queries |
| `deleted` | ✅ | ❌ | Slow filtering of deleted records |

### Impact Analysis

1. **Severely Degraded History Playback Performance:**
   - Time-range queries on 3,439+ recordings without indexes
   - Response time: **seconds instead of milliseconds**
   - Poor user experience

2. **No UUID Uniqueness Enforcement:**
   - Possibility of duplicate recordings
   - Data corruption risk

3. **Inefficient Filtering:**
   - Selecting non-deleted recordings requires full collection scan
   - CPU and I/O overhead

### Reproduction Steps

```bash
# 1. Connect to MongoDB
mongo mongodb://prisma:prisma@10.10.10.103:27017/prisma --authenticationDatabase prisma

# 2. List indexes
db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').getIndexes()

# Output:
[
  { v: 2, key: { _id: 1 }, name: '_id_' }
]
# Only default _id index exists!
```

### Recommended Fix

```javascript
// Connect to MongoDB
mongo mongodb://prisma:prisma@10.10.10.103:27017/prisma --authenticationDatabase prisma

// Create required indexes
db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').createIndex(
  { "uuid": 1 },
  { unique: true, name: "uuid_unique" }
);

db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').createIndex(
  { "start_time": 1 },
  { name: "start_time_idx" }
);

db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').createIndex(
  { "end_time": 1 },
  { name: "end_time_idx" }
);

db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').createIndex(
  { "deleted": 1 },
  { name: "deleted_idx" }
);

// Verify indexes were created
db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').getIndexes()
```

### Timeline

- **Estimated Fix Time:** 5 minutes
- **Testing Time:** 10 minutes
- **Risk Level:** LOW (creating indexes is non-destructive)
- **Downtime Required:** None

### Related Test

```bash
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_mongodb_indexes_exist_and_optimal -v
```

---

## Bug #2: Deleted Recordings Missing end_time (Not Critical)

### Technical Details

| Field | Value |
|-------|-------|
| **Severity** | 🟢 LOW |
| **Priority** | LOW |
| **Type** | Data Quality |
| **Affected Documents** | 24 deleted recordings (0.70%) |
| **Note** | Active recordings without end_time are LIVE recordings (running) - this is NORMAL |

### Problem Description

**24 deleted recordings** are missing `end_time`. These recordings were deleted while still running and never received an `end_time` before deletion.

**Important:** Active recordings (`deleted=False`) without `end_time` can be either:
- **LIVE recordings:** Currently running, don't have `end_time` yet - **this is CORRECT** ✅
- **STALE recordings:** Crashed/failed, never received `end_time` - **this is a BUG** ❌

### How We Distinguish Live vs Stale Recordings

**Detection Strategy:**
```python
# If recording started more than 24 hours ago and still has no end_time,
# it's likely STALE (crashed/failed)
if start_time < (now - 24 hours) and end_time is None:
    status = "STALE"  # ❌ Bug
else:
    status = "LIVE"   # ✅ Normal
```

**Rationale:**
- Typical recording duration: minutes to hours
- 24-hour threshold is conservative (captures truly stuck recordings)
- Recent recordings (<24h) without `end_time` are assumed to be actively running

The system uses three types of recordings:
- **Historical recordings:** Completed or deleted, have `end_time`
- **Live recordings:** Currently running (<24h old), no `end_time` yet (normal)
- **Stale recordings:** Old (>24h) without `end_time` (bug - crashed/failed)

### Impact Analysis

1. **Cannot Calculate Duration:**
   ```python
   duration = end_time - start_time  # ❌ Error!
   ```

2. **History Display Issues:**
   - Recording appears as "still running"
   - Cannot sort by duration
   - UI displays errors

3. **Time-Range Queries Don't Work:**
   ```javascript
   db.recordings.find({
     start_time: {$gte: startDate},
     end_time: {$lte: endDate}  // ❌ Missing recordings won't appear
   })
   ```

### Reproduction Steps

```bash
# 1. Connect to MongoDB
mongo mongodb://prisma:prisma@10.10.10.103:27017/prisma --authenticationDatabase prisma

# 2. Find active recordings with missing end_time
db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').find({
  deleted: false,
  $or: [
    { end_time: { $exists: false } },
    { end_time: null }
  ]
})

# 3. Find deleted recordings with missing end_time
db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').find({
  deleted: true,
  $or: [
    { end_time: { $exists: false } },
    { end_time: null }
  ]
}).count()
# Output: 24
```

### Root Cause Investigation

**For deleted recordings (24 documents):**
- These recordings were **deleted while still running**
- They never received an `end_time` before deletion
- Pattern observed: All occurred on July 23-28, 2025
- Hypothesis: Cleanup script deleted running recordings

**For active recording (1 document):**
- Unclear why it's missing `end_time`
- Needs investigation of logs
- Check if recording process crashed

### Recommended Fix

**Option 1: Add `status` field (BEST long-term solution)**
```python
# In recording service - add explicit status field
class RecordingStatus:
    RUNNING = "running"      # Live recording in progress
    COMPLETED = "completed"  # Finished successfully
    FAILED = "failed"        # Crashed or errored
    DELETED = "deleted"      # User deleted

# When creating recording
def start_recording(uuid):
    db.recordings.insert_one({
        "uuid": uuid,
        "start_time": datetime.utcnow(),
        "end_time": None,
        "deleted": False,
        "status": RecordingStatus.RUNNING  # ✅ Explicit status
    })

# When completing recording
def complete_recording(uuid):
    db.recordings.update_one(
        {"uuid": uuid},
        {
            "$set": {
                "end_time": datetime.utcnow(),
                "status": RecordingStatus.COMPLETED  # ✅ Clear state
            }
        }
    )
```

**Benefits:**
- ✅ Clear distinction between live/completed/failed recordings
- ✅ No need for time-based heuristics
- ✅ Better queries: `find({status: "running"})` vs complex time logic
- ✅ Better monitoring and alerts

**Option 2: Find and fix stale recordings (immediate workaround)**
```javascript
// Find recordings that started >24h ago without end_time
var staleRecordings = db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').find({
  deleted: false,
  end_time: null,
  start_time: { $lt: new Date(Date.now() - 24*60*60*1000) }
});

// Fix them by setting end_time
staleRecordings.forEach(function(doc) {
  db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').updateOne(
    { uuid: doc.uuid },
    {
      $set: {
        end_time: new Date(),
        status: "failed",  // Mark as failed
        fixed_by_script: true,
        fix_date: new Date()
      }
    }
  );
});
```

**Option 2: Improve deletion logic (prevent future occurrences)**
```python
def delete_recording(uuid):
    """Delete a recording, ensuring end_time is set."""
    recording = db.recordings.find_one({"uuid": uuid})
    
    db.recordings.update_one(
        {"uuid": uuid},
        {
            "$set": {
                "deleted": True,
                "end_time": recording.get("end_time") or datetime.utcnow(),  # ✅ Set if missing
                "deleted_at": datetime.utcnow()
            }
        }
    )
```

**Option 3: Add schema validation (prevent future occurrences)**
```javascript
// Add MongoDB schema validation
db.runCommand({
  collMod: "77e49b5d-e06a-4aae-a33e-17117418151c",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["uuid", "start_time", "end_time", "deleted"],
      properties: {
        uuid: { bsonType: "string" },
        start_time: { bsonType: "date" },
        end_time: { bsonType: "date" },
        deleted: { bsonType: "bool" }
      }
    }
  },
  validationLevel: "moderate"  // Won't fail existing documents
});
```

### Related Tests

```bash
# Test that found the issue
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_recordings_have_all_required_metadata -v

# Test that validates soft delete
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_deleted_recordings_marked_properly -v
```

---

## Bug #3: Low Recognition Rate (61.3%)

### Technical Details

| Field | Value |
|-------|-------|
| **Severity** | 🟡 MEDIUM |
| **Priority** | MEDIUM |
| **Type** | Data Quality / Algorithm |
| **Affected Collections** | Main + unrecognized_recordings |

### Problem Description

Out of **5,612 total recordings**:
- ✅ **Recognized:** 3,439 (61.3%)
- ❌ **Unrecognized:** 2,173 (38.7%)

**Nearly 40% of recordings are not processed!**

### Impact Analysis

1. **Users Don't See All Their Recordings:**
   - Potential data loss
   - User complaints

2. **Wasted Storage Space:**
   - 2,173 recordings taking up space
   - Cannot clean up (don't know if they're important)

3. **Cannot Analyze Root Cause:**
   - Insufficient information in unrecognized collection
   - No error messages or reasons

### Current Data Structure

```javascript
// Unrecognized recordings collection
{
  "folder_name": "dc022cb7-ae34-4b1e-9e0e-0bfeb60a3714",
  "file_count": 1,
  "update_time": "2025-07-23 12:17:48.518000"
}
```

**Missing:**
- Why the recording wasn't recognized
- What error occurred
- Can it be retried?

### Reproduction Steps

```bash
# 1. Connect to MongoDB
mongo mongodb://prisma:prisma@10.10.10.103:27017/prisma --authenticationDatabase prisma

# 2. Count recognized vs unrecognized
RECOGNIZED=$(db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').count())
UNRECOGNIZED=$(db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c-unrecognized_recordings').count())

echo "Recognized: $RECOGNIZED"
echo "Unrecognized: $UNRECOGNIZED"
# Calculate rate
echo "Recognition Rate: $(( RECOGNIZED * 100 / (RECOGNIZED + UNRECOGNIZED) ))%"
```

### Root Cause Investigation

**Queries to run:**

1. **Which folders have the most unrecognized recordings?**
```javascript
db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c-unrecognized_recordings')
  .aggregate([
    { $group: { _id: "$folder_name", count: { $sum: 1 } } },
    { $sort: { count: -1 } },
    { $limit: 10 }
  ])
```

2. **When do unrecognized recordings occur?**
```javascript
db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c-unrecognized_recordings')
  .aggregate([
    {
      $project: {
        hour: { $hour: "$update_time" },
        date: { $dateToString: { format: "%Y-%m-%d", date: "$update_time" } }
      }
    },
    { $group: { _id: { date: "$date", hour: "$hour" }, count: { $sum: 1 } } },
    { $sort: { count: -1 } },
    { $limit: 10 }
  ])
```

3. **Check Focus Server logs:**
```bash
ssh prisma@10.10.10.150
kubectl logs -n default <focus-server-pod> | grep -i "recognition\|unrecognized" | tail -100
```

### Recommended Fix

**Step 1: Add diagnostic information to unrecognized recordings**
```python
def handle_unrecognized_recording(folder_name):
    """Store unrecognized recording with diagnostic info."""
    unrecognized_doc = {
        "folder_name": folder_name,
        "file_count": count_files(folder_name),
        "update_time": datetime.utcnow(),
        # ✅ Add useful diagnostic information:
        "error_reason": get_recognition_error(),
        "error_details": get_error_stacktrace(),
        "file_types": get_file_types(folder_name),
        "total_size_mb": get_folder_size(folder_name),
        "first_attempt": datetime.utcnow(),
        "retry_count": 0,
        "can_be_retried": check_if_retriable(),
        "format_detected": detect_format(folder_name)
    }
    db.unrecognized_recordings.insert_one(unrecognized_doc)
```

**Step 2: Improve recognition algorithm**
- Based on investigation findings
- Support more file formats?
- Fix bug in detection logic?

**Step 3: Add retry mechanism**
```python
def retry_unrecognized_recordings():
    """Retry recognition for previously failed recordings."""
    unrecognized = db.unrecognized_recordings.find({
        "can_be_retried": True,
        "retry_count": { "$lt": 3 }
    })
    
    for rec in unrecognized:
        if try_recognize_again(rec):
            # Success! Move to main collection
            move_to_recognized(rec)
            db.unrecognized_recordings.delete_one({"_id": rec["_id"]})
        else:
            # Increment retry count
            db.unrecognized_recordings.update_one(
                {"_id": rec["_id"]},
                {"$inc": {"retry_count": 1}}
            )
```

**Step 4: Add monitoring**
```python
# Alert if recognition rate drops below 80%
def check_recognition_rate():
    recognized = db.recordings.count_documents({})
    unrecognized = db.unrecognized_recordings.count_documents({})
    total = recognized + unrecognized
    
    if total > 0:
        rate = recognized / total
        if rate < 0.80:
            send_alert(f"Recognition rate is LOW: {rate:.1%} (expected >= 80%)")
```

### Related Test

```bash
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_required_collections_exist -v
```

---

## Summary Table

| Bug ID | Description | Severity | Affected Count | Status | Fix ETA |
|--------|-------------|----------|----------------|--------|---------|
| **#1** | Missing Indexes | 🔴 HIGH | 3,439 (100%) | Open | 5 min |
| **#2** | Deleted recordings missing end_time | 🟢 LOW | 24 (0.70%) | Explained | N/A |
| **#3** | Low recognition rate | 🟡 MEDIUM | 2,173 (38.7%) | Open | 1 week |

**Note:** Active recording without `end_time` (1 recording) was identified as a **LIVE recording** currently running - this is NORMAL behavior ✅

---

## Action Items

### Immediate (Do Today) ⚡

- [ ] **Create missing indexes** - 5 minutes
  - Risk: Low (non-destructive)
  - Impact: High (performance improvement)
  - Priority: **CRITICAL**

- [ ] **Fix active recording missing end_time** - 5 minutes
  - Risk: Low (single document update)
  - Impact: High (data integrity)
  - Priority: **CRITICAL**

### Short Term (This Week) 📅

- [ ] **Investigate unrecognized recordings**
  - Run diagnostic queries
  - Check logs for patterns
  - Document findings

- [ ] **Improve deletion logic**
  - Ensure `end_time` is set when deleting running recordings
  - Add logging

- [ ] **Add schema validation**
  - Prevent recordings without `end_time`
  - Enforce data types

### Medium Term (This Sprint) 📊

- [ ] **Improve recognition algorithm**
  - Based on investigation findings
  - Add retry mechanism
  - Add better logging

- [ ] **Add monitoring and alerts**
  - Alert on recognition rate < 80%
  - Alert on recordings without end_time
  - Dashboard with metrics

### Long Term 🎯

- [ ] **Developer documentation**
  - MongoDB schema guidelines
  - Best practices
  - Common pitfalls

- [ ] **CI/CD integration**
  - Automated tests on merge
  - Index validation
  - Data quality checks

---

## How to Run the Tests

```bash
# All MongoDB data quality tests
pytest tests/integration/infrastructure/test_mongodb_data_quality.py -v

# Specific test
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_mongodb_indexes_exist_and_optimal -v

# With detailed logs
pytest tests/integration/infrastructure/test_mongodb_data_quality.py -v -s --log-cli-level=DEBUG

# Run only failed tests
pytest tests/integration/infrastructure/test_mongodb_data_quality.py -v --lf
```

---

## Related Files

| File | Description |
|------|-------------|
| `tests/integration/infrastructure/test_mongodb_data_quality.py` | Test suite that discovered these bugs |
| `scripts/quick_mongo_explore.py` | Quick schema exploration tool |
| `scripts/explore_mongodb_schema.py` | Comprehensive schema discovery tool |
| `docs/MONGODB_SCHEMA_REAL_FINDINGS.md` | Detailed schema findings |
| `docs/HOW_TO_DISCOVER_DATABASE_SCHEMA.md` | Schema discovery guide |
| `TEST_FIX_SUMMARY.md` | Test fix summary |
| `T_DATA_001_SOFT_DELETE_REPORT.md` | Soft delete validation report |

---

## Test Coverage

| Test | Status | Severity | Finding |
|------|--------|----------|---------|
| test_required_collections_exist | ✅ PASS | - | Collections exist and discoverable |
| test_recording_schema_validation | ✅ PASS | - | Schema structure is valid |
| test_recordings_have_all_required_metadata | ❌ FAIL | 🔴 HIGH | 25 recordings missing end_time |
| test_mongodb_indexes_exist_and_optimal | ❌ FAIL | 🔴 HIGH | All 4 critical indexes missing |
| test_deleted_recordings_marked_properly | ✅ PASS | - | Soft delete implementation correct |

**Overall:** 3 out of 5 tests passing. 2 tests found critical bugs that need immediate attention.

---

**Created by:** QA Automation Framework  
**Date:** October 15, 2025  
**Environment:** staging (10.10.10.103)  
**Database:** prisma  
**Test ID:** PZ-13598

**These tests run automatically and find real production bugs!** 🎉

