# Test Case T-DATA-002 (NEW-006)

**Created:** 2025-10-15  
**Author:** Roy Avrahami (QA Automation Architect)  
**Status:** ✅ Automated & Tested  
**Test Run:** PASSED ✅

---

## Summary
**Data Lifecycle – Historical vs Live Recordings Classification**

---

## Test Type
Integration Test

---

## Priority
**High**

---

## Components/Labels
`focus-server`, `mongodb`, `data-quality`, `data-lifecycle`, `data-integrity`, `recordings`, `cleanup`

---

## Requirements
- **PZ-13598** (Data Quality – Mongo collections and schema)
- **FOCUS-DATA-LIFECYCLE** (Recording lifecycle management)
- **FOCUS-CLEANUP-SERVICE** (Data cleanup and retention)

---

## Objective

Validate that MongoDB correctly distinguishes between **Historical** (completed), **Live** (in-progress), and **Deleted** (cleanup) recordings. Verify that the recording lifecycle is properly managed and that cleanup services (Sweeper/Data Manager) are functioning correctly.

**Business Impact:**
- Historical recordings must be properly indexed for history playback via `POST /recordings_in_time_range`
- Live recordings must be distinguished from stale/crashed recordings
- Deleted recordings must be properly marked for cleanup
- Missing end_time on deleted recordings indicates improper cleanup logic

---

## Pre-Conditions

- **PC-010:** MongoDB is reachable and accessible
- **PC-013:** Recording collection exists and contains data
- **PC-021:** Recording collection is dynamically named (GUID-based)
- **PC-022:** `base_paths` collection contains GUID for recording collection
- **PC-023:** System has active or historical recordings

---

## Architectural Context

### MongoDB Role in Focus/Panda System

MongoDB serves as a **metadata index** for recordings:
- **Purpose:** Store metadata for recordings (NOT raw data)
- **Used by:** Focus Server & Baby Analyzer
- **Function:** Find raw files (PRP2/SEGY) in S3/local storage for specific time ranges
- **API:** `POST /recordings_in_time_range` requires `start_time` and `end_time`

### Recording Types

| Type | Description | Schema | Status |
|------|-------------|--------|--------|
| **Historical** | Completed recordings | Has `start_time` AND `end_time`, `deleted=False` | Normal ✅ |
| **Live** | Currently recording | Has `start_time`, NO `end_time` (yet), `deleted=False` | Normal ✅ |
| **Deleted** | Soft-deleted recordings | Has `deleted=True` | Cleanup ⚠️ |
| **Stale** | Crashed/failed recordings | Old (>24h) with NO `end_time`, `deleted=False` | Bug ❌ |

---

## Test Data

- **Database name:** `prisma` (staging)
- **Collections:**
  - `base_paths` - contains GUID for recording collection
  - `{GUID}` - dynamic recording collection (e.g., `77e49b5d-e06a-4aae-a33e-17117418151c`)
  - `{GUID}-unrecognized_recordings` - failed recognition recordings

- **Expected Recording Fields:**
  - `uuid` (string, unique) - Recording identifier
  - `start_time` (datetime) - Recording start timestamp
  - `end_time` (datetime or null) - Recording end timestamp
  - `deleted` (boolean) - Soft delete flag

- **Thresholds:**
  - **Stale threshold:** 24 hours (recordings older than 24h without `end_time`)
  - **Historical majority:** >50% of recordings should be completed

---

## Test Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| **SETUP** | | | |
| 1 | Connect to MongoDB | Database name from config | Connection successful |
| 2 | Access `base_paths` collection | Collection name: "base_paths" | Collection accessible |
| 3 | Get dynamic recording collection GUID | Query base_paths for GUID | GUID retrieved |
| 4 | Access recording collection | Collection name: {GUID} | Collection accessible |
| 5 | Count total recordings | `count_documents({})` | Total count > 0 |
| **CLASSIFICATION** | | | |
| 6 | Count Historical recordings | Query: `{start_time: exists, end_time: {$ne: null}, deleted: false}` | Count returned |
| 7 | Count Live recordings | Query: `{start_time: exists, end_time: null, deleted: false}` | Count returned |
| 8 | Count Deleted recordings | Query: `{deleted: true}` | Count returned |
| 9 | Count Invalid recordings | Query: `{start_time: {$exists: false}}` | Should be 0 |
| 10 | Calculate percentages | (count / total) * 100 | Percentages calculated |
| 11 | Log classification summary | All categories | Summary displayed |
| **VALIDATION** | | | |
| 12 | Sample Historical recordings | Limit: 5, sort by start_time | Retrieve 5 records |
| 13 | Verify Historical have complete metadata | Check: uuid, start_time, end_time, deleted | All fields present |
| 14 | Calculate recording durations | (end_time - start_time) in hours | Duration calculated |
| 15 | Log Historical samples | UUID, Start, End, Duration | Details displayed |
| **LIVE ANALYSIS** | | | |
| 16 | Check Live recordings age | For each Live, calculate age from start_time | Age in hours |
| 17 | Identify stale Live recordings | Filter: age > 24 hours | Stale recordings listed |
| 18 | If stale found, log details | UUID, age, start_time | Warning displayed |
| 19 | If no stale, confirm all Live are recent | Age < 24 hours | Success message |
| **CLEANUP SERVICE** | | | |
| 20 | Count Deleted with end_time | Query: `{deleted: true, end_time: {$ne: null}}` | Count returned |
| 21 | Count Deleted without end_time | Query: `{deleted: true, end_time: null}` | Count returned |
| 22 | Calculate Deleted percentages | (count / total_deleted) * 100 | Percentages calculated |
| 23 | Sample Deleted recordings | Limit: 3 | Retrieve 3 deleted records |
| 24 | For each Deleted, calculate age | (now - start_time) in days | Age calculated |
| 25 | Log Deleted samples | UUID, Started, Age, Has end_time | Details displayed |
| 26 | If no Deleted, note cleanup status | Check if cleanup service active | Note displayed |
| **ASSERTIONS** | | | |
| 27 | Assert: No invalid recordings | `invalid_count == 0` | PASS if 0, FAIL otherwise |
| 28 | Assert: Classification integrity | `historical + live + deleted == total` | PASS if match |
| 29 | Assert: Historical majority | `(historical / total) > 0.50` | PASS if >50% |
| 30 | Log final test result | Overall status | Test result displayed |

---

## Expected Result (overall)

### Classification Results
- **Historical (completed):** ~99% of total recordings
- **Live (in-progress):** <1% of total recordings (recent, <24h old)
- **Deleted (cleanup):** <1% of total recordings
- **Invalid (no start_time):** 0 recordings ✅
- **Stale (crashed/failed):** 0 recordings ✅

### Data Integrity
- ✅ All recordings have `start_time`
- ✅ Classification totals match overall count
- ✅ Historical recordings are the majority (>50%)
- ✅ All Historical recordings have complete metadata (uuid, start_time, end_time)
- ✅ Live recordings are recent (<24 hours old)
- ⚠️ Deleted recordings may be missing `end_time` (deleted while running)

### Cleanup Service Behavior
- Cleanup service (Sweeper/Data Manager) sets `deleted=True`
- Some deleted recordings may lack `end_time` (indicates deletion during recording)
- Pattern analysis of deleted recordings shows cleanup policy (age, retention)

---

## Post-Conditions

**None** (read-only test)

**Note:** If test identifies issues (stale recordings, improper cleanup), these should be reported but do not affect test cleanup.

---

## Attachments

- Recording classification report (JSON/CSV)
- Sample Historical recordings (JSON)
- Sample Deleted recordings (JSON)
- Stale recordings list (if any found)
- Test execution log with full details

---

## Authentication

- MongoDB credentials from `environments.yaml`
- Read-only access required (no write operations)

---

## Assertions

### Critical Assertions (Test FAILS if violated)
1. **No Invalid Recordings:**
   ```python
   assert invalid_count == 0, \
       f"Found {invalid_count} recordings without start_time!"
   ```

2. **Classification Integrity:**
   ```python
   assert (historical_count + live_count + deleted_count) == total_count, \
       f"Classification mismatch: {classified} vs {total}"
   ```

3. **Historical Majority:**
   ```python
   assert (historical_count / total_count) > 0.50, \
       f"Historical recordings only {percentage:.1f}% (expected >50%)"
   ```

### Warning Assertions (Test WARNS but doesn't FAIL)
4. **Stale Recordings Detection:**
   ```python
   if stale_count > 0:
       logger.warning(f"Found {stale_count} stale recordings (>24h without end_time)")
   ```

5. **Deleted Missing end_time:**
   ```python
   if deleted_without_endtime > 0:
       logger.warning(f"{deleted_without_endtime} deleted recordings missing end_time")
   ```

---

## Environment

**Any environment with recording data:**
- ✅ **Dev** (minimal data)
- ✅ **Staging** (production-like data)
- ✅ **Production** (real data, read-only test)

**Recommended:** **Staging** for comprehensive testing with significant data volume.

---

## Automation Status

✅ **Automated** with Pytest

**Test Function:** `test_historical_vs_live_recordings`  
**Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`  
**Test Class:** `TestMongoDBDataQuality`

---

## Execution Command

```bash
# Run this test alone
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_historical_vs_live_recordings -v

# Run with detailed output
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_historical_vs_live_recordings -v -s

# Run all data lifecycle tests
pytest -m data_lifecycle -v

# Run all MongoDB data quality tests
pytest tests/integration/infrastructure/test_mongodb_data_quality.py -v
```

---

## Related Issues

- **PZ-13598** (Parent - MongoDB Data Quality)
- **T-DATA-001** (Soft Delete Implementation - Related test)
- **BUG-CLEANUP-001** (Deleted recordings missing end_time - Discovered by this test)

---

## Test Results (Last Run)

**Date:** 2025-10-15  
**Environment:** Staging  
**Status:** ✅ **PASSED**

### Results Summary
```
📊 Recording Classification:
   Historical (completed): 3,414 (99.3%) ✅
   Live (in-progress): 1 (0.03%) ✅
   Deleted (cleanup): 24 (0.7%) ⚠️
   Invalid (no start_time): 0 (0%) ✅

✅ All assertions passed
⚠️  24 deleted recordings missing end_time (non-critical)
✅ All 1 Live recording is recent (<24h)
✅ No stale recordings detected
```

### Sample Historical Recordings
| UUID | Duration | Status |
|------|----------|--------|
| 38e432b0-7c87-468c-9b85-fd48462d8901 | 1.97 hours | ✅ Valid |
| 2b58e51e-50fd-4ad8-a623-46f5d48c9e8b | 0.01 hours | ✅ Valid |
| 55c582e8-1de4-4a03-b7e2-bd803e03264f | 0.02 hours | ✅ Valid |

### Deleted Recordings Analysis
- **With end_time:** 0 (0%)
- **Without end_time:** 24 (100%)
- **Age:** 84 days (all deleted on 2025-07-23)
- **Pattern:** Bulk cleanup operation or retention policy

---

## Performance Metrics

- **Test Duration:** ~10 seconds
- **Database Queries:** 15 queries
- **Data Scanned:** 3,439 recordings
- **Memory Usage:** Low (streaming queries)

---

## Known Limitations

1. **24-hour heuristic for stale detection:**
   - Recordings older than 24h without `end_time` are flagged as stale
   - May have false positives for extremely long recordings
   - **Recommendation:** Add explicit `status` field in future

2. **Dynamic collection naming:**
   - Test depends on `base_paths` collection to find recording collection GUID
   - If `base_paths` is missing or corrupted, test will fail

3. **Cleanup service identification:**
   - Test can detect cleanup behavior but cannot identify which service performed cleanup
   - **Action required:** Manual confirmation with development team

---

## Recommendations Based on Test Results

### 🔴 High Priority

**Issue:** Deleted recordings missing `end_time` (24 recordings)

**Current Behavior:**
```python
def delete_recording(uuid):
    db.recordings.update_one(
        {"uuid": uuid},
        {"$set": {"deleted": True}}
    )
```

**Recommended Fix:**
```python
def delete_recording(uuid):
    """Delete recording, ensuring end_time is set."""
    db.recordings.update_one(
        {"uuid": uuid},
        {
            "$set": {
                "deleted": True,
                "end_time": end_time or datetime.utcnow(),
                "deleted_at": datetime.utcnow(),
                "deletion_reason": "manual"  # or "retention", "cleanup"
            }
        }
    )
```

### 🟡 Medium Priority

**Enhancement:** Add explicit `status` field

**Recommended Schema:**
```python
class RecordingStatus:
    RUNNING = "running"      # Live recording
    COMPLETED = "completed"  # Finished successfully
    FAILED = "failed"        # Crashed/errored
    DELETED = "deleted"      # Soft deleted

# Schema
{
    "uuid": "abc-123",
    "start_time": datetime,
    "end_time": datetime or None,
    "deleted": bool,
    "status": RecordingStatus.RUNNING  # ← New field
}
```

**Benefits:**
- No time-based heuristics needed
- Clear state machine
- Better monitoring and alerting
- Simpler queries

---

## Questions for Development Team

### Q1: Cleanup Service Identification
**Which service sets `deleted=True` on recordings?**
- [ ] Sweeper service
- [ ] Data Manager service
- [ ] Lifeboat service
- [ ] Manual API calls
- [ ] Other: _______________

### Q2: Cleanup Trigger
**What triggers recording cleanup/deletion?**
- [ ] Retention policy (auto-delete after X days)
- [ ] Manual user deletion
- [ ] Storage quota limit
- [ ] `clean_status_list` job completion
- [ ] Other: _______________

### Q3: Expected Behavior
**Should deleted recordings have `end_time` set?**
- [ ] Yes - Set to deletion timestamp
- [ ] Yes - Set to last known timestamp
- [ ] No - Leave as null
- [ ] Depends: _______________

### Q4: Status Field
**Is there a plan to add explicit `status` field?**
- [ ] Yes - In progress
- [ ] Maybe - Under consideration
- [ ] No - Not planned

---

## Success Criteria

### Test PASSES if:
1. ✅ All recordings have `start_time` (no invalid records)
2. ✅ Classification totals match overall count
3. ✅ Historical recordings are >50% of total
4. ✅ All Historical recordings have complete metadata
5. ✅ Live recordings are recent (<24h old)
6. ✅ No stale recordings detected

### Test WARNS if:
1. ⚠️ Deleted recordings missing `end_time`
2. ⚠️ Live recordings count is unusually high (>5%)
3. ⚠️ Recognition rate is low (<80%)

### Test FAILS if:
1. ❌ Any recordings missing `start_time`
2. ❌ Classification doesn't match total count
3. ❌ Historical recordings <50% (indicates cleanup issues)
4. ❌ Stale recordings detected (>24h without end_time, not deleted)

---

## Notes

**IMPORTANT:** This test validates a critical aspect of data lifecycle management in Focus/Panda system:

1. **Historical recordings** must be complete for history playback
2. **Live recordings** must be distinguished from crashed/stale recordings
3. **Cleanup service** must properly manage deleted recordings
4. **Missing end_time on deleted recordings** indicates suboptimal cleanup logic

**Impact:** If this test fails, it may indicate:
- Data quality issues affecting history playback
- Cleanup service not functioning properly
- Stale recordings consuming storage
- Need for explicit `status` field in schema

**Action Required:** 
- Review cleanup service logic
- Consider implementing recommendations
- Monitor for stale recordings in production

---

## Test Maintenance

**Update Required If:**
- Recording schema changes (new required fields)
- Cleanup service behavior changes
- Stale detection threshold changes (currently 24h)
- New recording states are introduced

**Review Schedule:**
- Monthly review of test results
- Quarterly review of detection thresholds
- After any schema changes

---

## Related Documentation

- `LIVE_VS_HISTORICAL_RECORDINGS.md` - Detailed explanation of recording types
- `T_DATA_002_HISTORICAL_VS_LIVE_REPORT.md` - Full test execution report
- `MONGODB_BUGS_REPORT.md` - Bug findings from data quality tests
- `MONGODB_SCHEMA_REAL_FINDINGS.md` - Actual MongoDB schema documentation

---

**Created:** 2025-10-15  
**Last Updated:** 2025-10-15  
**Test Author:** Roy Avrahami  
**Reviewed By:** Pending  
**Status:** ✅ Ready for Xray Import

---

## 🎯 Xray Import Checklist

- [x] Test ID assigned (T-DATA-002 / NEW-006)
- [x] Summary defined
- [x] Priority set (High)
- [x] Components/Labels added
- [x] Requirements linked (PZ-13598)
- [x] Test steps documented (30 steps)
- [x] Expected results defined
- [x] Assertions listed
- [x] Automation status confirmed (Automated ✅)
- [x] Test executed and results documented (PASSED ✅)
- [x] Related issues linked
- [x] Recommendations provided

✅ **Ready for import to Jira Xray!**

