# T-DATA-002: Historical vs Live Recordings - Test Report

**Test ID:** T-DATA-002  
**Test Name:** Historical vs Live Recording Classification  
**Status:** ✅ PASSED  
**Date:** October 15, 2025  
**Execution Time:** ~10 seconds

---

## Executive Summary

This test validates that MongoDB correctly distinguishes between **Historical** (completed) and **Live** (in-progress) recordings, and verifies that the cleanup service is properly managing the recording lifecycle.

### Key Findings

| Metric | Value | Status |
|--------|-------|--------|
| **Total Recordings** | 3,439 | ✅ |
| **Historical (completed)** | 3,414 (99.3%) | ✅ Normal |
| **Live (in-progress)** | 1 (0.03%) | ✅ Normal |
| **Deleted (cleanup)** | 24 (0.7%) | ⚠️ Missing end_time |
| **Invalid (no start_time)** | 0 (0%) | ✅ Perfect |

---

## Test Architecture

### Architectural Understanding

MongoDB serves as a **metadata index** for recordings in the Focus/Panda system:

```
┌─────────────────────────────────────────────────────────────┐
│                   MongoDB Role in System                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Purpose: Index metadata for recordings                      │
│           (NOT the actual raw data)                          │
│                                                               │
│  Used by: Focus Server & Baby Analyzer                       │
│           To find raw files (PRP2/SEGY) in S3/local storage  │
│           For specific time ranges                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Recording Types

```python
# Historical Recordings (99.3%)
{
    "uuid": "38e432b0-7c87-468c-9b85-fd48462d8901",
    "start_time": "2025-03-07T07:31:34.453Z",  # ✅ Present
    "end_time": "2025-03-07T09:29:34.217Z",    # ✅ Present
    "deleted": False
}
# → Used for history playback via POST /recordings_in_time_range

# Live Recordings (0.03%)
{
    "uuid": "abc-123",
    "start_time": "2025-10-15T20:21:00.000Z",  # ✅ Present
    "end_time": None,                           # ⏳ Not yet (still recording)
    "deleted": False
}
# → Currently recording, will get end_time when complete

# Deleted Recordings (0.7%)
{
    "uuid": "21fb3de5-4d58-43fc-8685-0f45d0ed97ea",
    "start_time": "2025-07-23T12:18:54.279Z",  # ✅ Present
    "end_time": None,                           # ❌ Missing (deleted while running)
    "deleted": True                             # 🗑️ Soft delete
}
# → Deleted by cleanup service (Sweeper/Data Manager)
```

---

## Test Execution Flow

### Step 1: Classify Recordings

```
📊 Recording Classification:
   Historical (completed): 3414 (99.3%)  ✅
   Live (in-progress): 1 (0.0%)          ✅
   Deleted (cleanup): 24 (0.7%)          ⚠️
   Invalid (no start_time): 0            ✅
```

**Result:** All recordings have valid `start_time`. Classification is correct.

### Step 2: Validate Historical Recordings

**Sample Historical Recordings:**

| UUID | Duration | Status |
|------|----------|--------|
| `38e432b0-7c87-468c-9b85-fd48462d8901` | 1.97 hours | ✅ Valid |
| `2b58e51e-50fd-4ad8-a623-46f5d48c9e8b` | 0.01 hours | ✅ Valid |
| `55c582e8-1de4-4a03-b7e2-bd803e03264f` | 0.02 hours | ✅ Valid |
| `fc456e06-b599-4b4c-bace-ecef68f36414` | 2.55 hours | ✅ Valid |
| `d0bf090d-a94d-4e87-b1dd-265a8738dfd9` | 6.13 hours | ✅ Valid |

**Result:** All historical recordings have valid `start_time`, `end_time`, and `uuid`.

### Step 3: Analyze Live Recordings Age

```
✅ All 1 Live recordings are recent (<24h)
```

**Result:** No stale recordings detected. The single live recording is less than 24 hours old, indicating it's currently in progress (normal behavior).

### Step 4: Check Cleanup Service Behavior

```
Deleted recordings analysis:
   With end_time: 0        ❌
   Without end_time: 24    ⚠️
```

**Sample Deleted Recordings:**

| UUID | Started | Age | Has end_time? |
|------|---------|-----|---------------|
| `21fb3de5-4d58-43fc-8685-0f45d0ed97ea` | 2025-07-23 | 84 days | ❌ No |
| `04d73fc4-7880-4f9a-8ef0-ffe9f5578b86` | 2025-07-23 | 84 days | ❌ No |
| `471b9ef9-d49b-4239-abdc-b9eb35a41c7a` | 2025-07-23 | 84 days | ❌ No |

**Observation:** All 24 deleted recordings are missing `end_time`. They were deleted while still running (before receiving `end_time`).

---

## Test Assertions

### Assertion 1: No Invalid Recordings
```python
assert invalid_count == 0, \
    f"Found {invalid_count} recordings without start_time!"
```
**Result:** ✅ PASSED (0 invalid recordings)

### Assertion 2: Classification Integrity
```python
classified_total = historical_count + live_count + deleted_count
assert classified_total == total_count
```
**Result:** ✅ PASSED (3414 + 1 + 24 = 3439)

### Assertion 3: Historical Majority
```python
historical_percentage = (historical_count / total_count) * 100
assert historical_percentage > 50, \
    f"Historical recordings are only {historical_percentage:.1f}% of total"
```
**Result:** ✅ PASSED (99.3% are historical - expected for production database)

---

## Cleanup Service Analysis

### Current State

The system appears to have a **cleanup service** (likely **Sweeper** or **Data Manager**) that:

1. ✅ **Sets `deleted=True`** for old/unwanted recordings
2. ❌ **Does NOT set `end_time`** when deleting running recordings
3. ⚠️ **24 deleted recordings** (0.7%) were deleted while still in progress

### Observations

```
Timeline of Deleted Recordings:
- All deleted recordings: Started July 23, 2025 (84 days ago)
- All missing end_time
- All marked with deleted=True
- Pattern suggests: Bulk cleanup operation OR automated cleanup after retention period
```

### Recommendations

#### Recommendation 1: Update Deletion Logic ⭐

**Current Behavior:**
```python
def delete_recording(uuid):
    db.recordings.update_one(
        {"uuid": uuid},
        {"$set": {"deleted": True}}
    )
```

**Recommended Behavior:**
```python
def delete_recording(uuid):
    """Delete a recording, ensuring end_time is set."""
    db.recordings.update_one(
        {"uuid": uuid},
        {
            "$set": {
                "deleted": True,
                "end_time": end_time or datetime.utcnow(),  # ← Ensure end_time
                "deleted_at": datetime.utcnow(),
                "deletion_reason": "manual" # or "retention_policy", "cleanup"
            }
        }
    )
```

**Benefits:**
- Complete audit trail
- Accurate duration calculations
- No missing metadata

#### Recommendation 2: Add Explicit `status` Field ⭐⭐⭐

**Best Long-Term Solution:**
```python
class RecordingStatus:
    RUNNING = "running"      # Live recording
    COMPLETED = "completed"  # Finished successfully
    FAILED = "failed"        # Crashed/errored
    DELETED = "deleted"      # User/system deleted

# Schema
{
    "uuid": "abc-123",
    "start_time": datetime,
    "end_time": datetime or None,
    "deleted": bool,
    "status": RecordingStatus.RUNNING,  # ← Explicit state
    "deletion_reason": str or None
}
```

**Benefits:**
- Clear state machine
- No time-based heuristics
- Better monitoring
- Easier queries

#### Recommendation 3: Monitor Cleanup Service

**Metrics to Track:**
```python
# Daily metrics
cleanup_metrics = {
    "deleted_today": count,
    "deleted_with_endtime": count,
    "deleted_without_endtime": count,  # Should be 0
    "deletion_reasons": {
        "manual": count,
        "retention_policy": count,
        "cleanup": count
    }
}
```

**Alerts:**
```python
# Alert if recordings are deleted without end_time
if deleted_without_endtime > 0:
    send_alert(f"{deleted_without_endtime} recordings deleted without end_time")
```

---

## Questions for Development Team

Based on test findings, please clarify:

### 1. Cleanup Service Identification
**Q:** Which service is responsible for setting `deleted=True`?
- [ ] **Sweeper** service
- [ ] **Data Manager** service
- [ ] **Lifeboat** service
- [ ] **Manual cleanup** via API
- [ ] Other: _________________

### 2. Cleanup Trigger
**Q:** What triggers the cleanup/deletion of recordings?
- [ ] **Retention policy** (delete after X days)
- [ ] **Manual deletion** by user
- [ ] **Storage quota** reached
- [ ] **`clean_status_list`** job completion
- [ ] Other: _________________

### 3. Expected Behavior
**Q:** Is it expected that deleted recordings have no `end_time`?
- [ ] **Yes** - This is normal behavior
- [ ] **No** - This is a bug (should set `end_time` on deletion)

**Q:** Should the cleanup service set `end_time` when deleting running recordings?
- [ ] **Yes** - Set to deletion time
- [ ] **Yes** - Set to `start_time` (duration = 0)
- [ ] **No** - Leave as `None`

### 4. Status Field
**Q:** Is there a plan to add an explicit `status` field?
- [ ] **Yes** - Already in progress
- [ ] **Maybe** - Under consideration
- [ ] **No** - Not planned

---

## Test Code Location

**File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`  
**Class:** `TestMongoDBDataQuality`  
**Method:** `test_historical_vs_live_recordings()`  
**Markers:** `@pytest.mark.data_lifecycle`, `@pytest.mark.mongodb`, `@pytest.mark.data_quality`

**Run Command:**
```bash
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_historical_vs_live_recordings -v
```

---

## Related Tests

| Test ID | Name | Status |
|---------|------|--------|
| T-DATA-001 | Soft Delete Implementation | ✅ PASSED |
| T-DATA-002 | Historical vs Live Classification | ✅ PASSED |
| T-PERF-001 | MongoDB Indexes Exist | ❌ FAILED (missing indexes) |
| T-QUAL-001 | Recording Recognition Rate | ⚠️ WARNING (38.7% unrecognized) |

---

## Conclusion

### ✅ Test Passed

The test successfully validated:
1. **Historical recordings** (99.3%) have complete metadata
2. **Live recordings** (0.03%) are recent and in-progress (normal)
3. **No invalid recordings** (all have `start_time`)
4. **Classification logic** is correct

### ⚠️ Cleanup Service Issue

The cleanup service (Sweeper/Data Manager) is setting `deleted=True` but NOT setting `end_time`, resulting in:
- 24 deleted recordings (0.7%) missing `end_time`
- Incomplete metadata for deleted records
- Potential analytics issues

### 🚀 Next Steps

1. **Identify cleanup service** (Sweeper/Data Manager/Other)
2. **Update deletion logic** to set `end_time` when deleting
3. **Consider adding explicit `status` field** for clarity
4. **Monitor cleanup operations** with metrics/alerts

---

**Test Engineer:** Roy Avrahami  
**Review Status:** Pending Development Team Response  
**Priority:** MEDIUM (does not block production, but should be addressed)

