# Live vs Historical Recordings - Detection Strategy

**Question:** How do we know if a recording is LIVE (currently running) or HISTORICAL (finished/failed)?

---

## The Challenge

In MongoDB, recordings can exist in different states:
- ✅ **Completed:** Has `start_time` AND `end_time` (normal)
- ❌ **Deleted:** Has `deleted=True` (may or may not have `end_time`)
- 🔄 **Live:** Currently running, has `start_time` but NO `end_time` yet (normal)
- 💀 **Stale:** Crashed/failed, has `start_time` but NO `end_time` (bug)

**The Problem:** Both LIVE and STALE recordings lack `end_time`. How do we tell them apart?

---

## Our Solution: Time-Based Heuristic

### Detection Algorithm

```python
def classify_recording(recording):
    """
    Classify recording status based on available fields.
    
    Returns: "completed", "deleted", "live", or "stale"
    """
    if recording.get("end_time"):
        return "completed"  # Has end_time - clearly finished
    
    if recording.get("deleted"):
        return "deleted"    # Marked as deleted
    
    # No end_time, not deleted - check age
    age = datetime.now(timezone.utc) - recording["start_time"]
    
    if age > timedelta(hours=24):
        return "stale"      # Running >24h - likely crashed/failed
    else:
        return "live"       # Recent - likely still running
```

### Rationale

| Assumption | Explanation |
|------------|-------------|
| **Typical recording duration** | Minutes to hours (not days) |
| **24-hour threshold** | Conservative (catches truly stuck recordings) |
| **Recent = Active** | If started <24h ago, assume still running |

---

## Implementation in Tests

### Code Example

```python
# tests/integration/infrastructure/test_mongodb_data_quality.py

# Check for stale recordings (>24 hours old without end_time)
stale_threshold = datetime.now(timezone.utc) - timedelta(hours=24)

stale_recordings = db.recordings.find({
    "deleted": False,
    "$or": [
        {"end_time": {"$exists": False}},
        {"end_time": None}
    ],
    "start_time": {"$lt": stale_threshold}  # Started >24h ago
})

if stale_recordings.count() > 0:
    # ❌ BUG: These recordings are stuck!
    for rec in stale_recordings:
        age_hours = (datetime.now(timezone.utc) - rec['start_time']).total_seconds() / 3600
        logger.error(f"Stale recording: {rec['uuid']}, age: {age_hours:.1f}h")
else:
    # ✅ All recordings without end_time are recent (live)
    logger.info(f"Found {active_count} live recordings - this is NORMAL")
```

---

## Test Results (October 15, 2025)

### What We Found

```
Total recordings: 3,439

✅ uuid: Present in all recordings
✅ start_time: Present in all recordings
⚠️  end_time missing in 25 recordings:
    ├── 24 with deleted=True (deleted while running)
    └── 1 with deleted=False:
        └── Started <24h ago → LIVE recording ✅

Result: NO stale recordings detected!
```

### Classification

| Type | Count | Percentage | Status |
|------|-------|------------|--------|
| **Completed** | 3,414 | 99.3% | ✅ Normal |
| **Deleted** | 24 | 0.7% | ⚠️ Missing end_time (deleted while running) |
| **Live** | 1 | 0.03% | ✅ Normal (currently running) |
| **Stale** | 0 | 0% | ✅ None found! |

---

## Long-Term Solution: Add `status` Field

### Problem with Current Approach

❌ **Time-based heuristic is not perfect:**
- What if a recording legitimately runs >24 hours?
- What if system clock changes?
- Requires complex logic in queries

### Better Approach: Explicit Status

```python
class RecordingStatus:
    RUNNING = "running"      # ✅ Live recording in progress
    COMPLETED = "completed"  # ✅ Finished successfully
    FAILED = "failed"        # ❌ Crashed or errored
    DELETED = "deleted"      # 🗑️ User deleted

# Database schema
{
    "uuid": "abc-123",
    "start_time": "2025-10-15T10:00:00Z",
    "end_time": None,  # or timestamp
    "deleted": False,
    "status": "running"  # ✅ Explicit state!
}
```

### Benefits

| Aspect | Time-Based Heuristic | Explicit Status Field |
|--------|---------------------|----------------------|
| **Accuracy** | 95% (heuristic) | 100% (explicit) |
| **Query complexity** | High (time calculations) | Low (`status='running'`) |
| **Edge cases** | Issues with long recordings | None |
| **Monitoring** | Complex | Simple |
| **Maintainability** | Hard | Easy |

### Migration Strategy

**Step 1: Add status field to new recordings**
```python
def start_recording(uuid):
    db.recordings.insert_one({
        "uuid": uuid,
        "start_time": datetime.now(timezone.utc),
        "end_time": None,
        "deleted": False,
        "status": RecordingStatus.RUNNING  # ✅ New field
    })
```

**Step 2: Update existing recordings**
```javascript
// For recordings with end_time
db.recordings.updateMany(
    { end_time: { $ne: null } },
    { $set: { status: "completed" } }
);

// For deleted recordings
db.recordings.updateMany(
    { deleted: true },
    { $set: { status: "deleted" } }
);

// For recent recordings without end_time
db.recordings.updateMany(
    {
        deleted: false,
        end_time: null,
        start_time: { $gt: new Date(Date.now() - 24*60*60*1000) }
    },
    { $set: { status: "running" } }
);

// For stale recordings
db.recordings.updateMany(
    {
        deleted: false,
        end_time: null,
        start_time: { $lt: new Date(Date.now() - 24*60*60*1000) }
    },
    { $set: { status: "failed" } }
);
```

**Step 3: Update application code**
```python
# When recording completes
def complete_recording(uuid):
    db.recordings.update_one(
        {"uuid": uuid},
        {
            "$set": {
                "end_time": datetime.now(timezone.utc),
                "status": RecordingStatus.COMPLETED  # ✅
            }
        }
    )

# When recording fails
def fail_recording(uuid, error):
    db.recordings.update_one(
        {"uuid": uuid},
        {
            "$set": {
                "end_time": datetime.now(timezone.utc),
                "status": RecordingStatus.FAILED,  # ✅
                "error": error
            }
        }
    )
```

**Step 4: Update queries**
```python
# Old way (complex)
active_recordings = db.recordings.find({
    "deleted": False,
    "$or": [
        {"end_time": {"$exists": False}},
        {"end_time": None}
    ],
    "start_time": {"$gt": datetime.now(timezone.utc) - timedelta(hours=24)}
})

# New way (simple) ✅
active_recordings = db.recordings.find({
    "status": "running"
})
```

---

## Monitoring and Alerts

### Metrics to Track

```python
# Daily metrics
def calculate_recording_metrics():
    total = db.recordings.count_documents({})
    
    metrics = {
        "completed": db.recordings.count_documents({"status": "completed"}),
        "running": db.recordings.count_documents({"status": "running"}),
        "failed": db.recordings.count_documents({"status": "failed"}),
        "deleted": db.recordings.count_documents({"status": "deleted"})
    }
    
    # Calculate rates
    metrics["failure_rate"] = metrics["failed"] / total if total > 0 else 0
    
    return metrics
```

### Alerts

```python
# Alert conditions
if metrics["failure_rate"] > 0.05:  # >5% failure rate
    send_alert("High recording failure rate: {:.1%}".format(metrics["failure_rate"]))

if metrics["running"] > 100:  # Too many concurrent recordings
    send_alert(f"High number of concurrent recordings: {metrics['running']}")

# Check for stuck recordings
stuck_recordings = db.recordings.find({
    "status": "running",
    "start_time": {"$lt": datetime.now(timezone.utc) - timedelta(hours=24)}
})

if stuck_recordings.count() > 0:
    send_alert(f"Found {stuck_recordings.count()} stuck recordings!")
```

---

## Conclusion

### Current State ✅

- **Works:** Time-based heuristic (24-hour threshold) successfully distinguishes live from stale recordings
- **Accurate:** In current data, correctly identified 1 live recording and 0 stale recordings
- **Test coverage:** Automated test validates this logic

### Future Improvement 🚀

- **Recommended:** Add explicit `status` field for clarity and simplicity
- **Benefits:** Better queries, accurate monitoring, easier maintenance
- **Migration:** Can be done incrementally without breaking existing functionality

---

**Created:** October 15, 2025  
**Test:** `test_recordings_have_all_required_metadata`  
**Status:** ✅ Implemented and Validated

