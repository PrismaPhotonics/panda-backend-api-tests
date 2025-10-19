# 🎯 New Test Cases for Jira Xray Test Repository
**Created:** 2025-10-15  
**Author:** Roy Avrahami (QA Automation Architect)  
**Status:** Ready for import to Jira Xray

---

## 📋 Test Cases Summary

| Test ID | Summary | Component | Priority | Status |
|---------|---------|-----------|----------|--------|
| **PZ-13556** | ⭐ API – SingleChannel View Mapping (COMPLETED & PASSED!) | api, view-type, singlechannel | Medium | ✅ Automated & Tested |
| **NEW-001** | Data Quality – MongoDB Collections Exist | mongodb, data-quality | High | ✅ Automated & Updated |
| **NEW-002** | Data Quality – node4 Schema Validation | mongodb, data-quality | High | ✅ Automated & Updated |
| **NEW-003** | Data Quality – Recordings Metadata Completeness | mongodb, data-quality | Critical | ✅ Automated & Updated |
| **NEW-004** | Data Quality – MongoDB Indexes Validation | mongodb, data-quality, performance | High | ✅ Automated & Updated |
| **NEW-005** | MongoDB Recovery – Recordings Indexed After Outage | mongodb, resilience, recovery | Critical | To Implement |
| **T-DATA-001** | ⭐ Data Lifecycle – Soft Delete Implementation | mongodb, data-lifecycle, data-integrity | Medium | ✅ Automated & Tested |
| **T-DATA-002** | ⭐ Data Lifecycle – Historical vs Live Classification (NEW!) | mongodb, data-lifecycle, data-quality | High | ✅ Automated & Tested |

---

# Test Case PZ-13556

## Test Summary
Validates view_type=SINGLECHANNEL behavior: the server must return exactly one stream (stream_amount=1) and a single, correct channel mapping. Ensures the requested channel (min=max) maps 1:1 to the produced stream, with no extra channels or stray mappings.

## Summary
Focus Server – SingleChannel view – Exactly one stream and 1:1 mapping

## Objective
Prove SingleChannel returns exactly one stream and correct mapping.

## Priority
Medium

## Components/Labels
focus-server, api, view-type, singlechannel

## Requirements
FOCUS-API-VIEWTYPE

## Pre-Conditions
- Server reachable

## Test Data
channels {min: X, max: X}; view_type=1; otherwise valid.

## Steps

| # | Action | Data | Expected |
|---|--------|------|----------|
| 1 | POST /configure | single channel payload | 200 |
| 2 | Validate stream_amount | response | stream_amount = 1 |
| 3 | Validate mapping | response | exactly one entry; 1:1 mapping for requested channel |

## Expected Result (overall)
Correct single-stream behavior and mapping.

## Post-Conditions
None.

## Test Data (Example)
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": { "height": 1000 },
  "channels": { "min": 7, "max": 7 },
  "frequencyRange": { "min": 0, "max": 500 },
  "start_time": null,
  "end_time": null,
  "view_type": 1
}
```

## Authentication
N/A

## Assertions
- Status Code: 200
- stream_amount = 1
- channel_to_stream_index contains single entry
- Mapping is correct for the requested channel

## Environment
Any (Dev/Staging)

## Automation Status
Automated with Pytest

**Test Function:** `test_configure_singlechannel_mapping`  
**Test File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

# Test Case NEW-001

## Summary
**Data Quality – MongoDB Collections Exist**

## Test Type
Integration Test

## Priority
High

## Components/Labels
`focus-server`, `mongodb`, `data-quality`, `infrastructure`, `database`

## Requirements
- PZ-13598 (Data Quality – Mongo collections and schema)

## Objective
Validate that all required MongoDB collections exist in the database. Missing collections would cause the Focus Server to fail when trying to query or store recording metadata, leading to system failures during history playback.

## Pre-Conditions
- **PC-010:** MongoDB is reachable and accessible
- **PC-011:** Database configured in environments.yaml
- **PC-012:** Valid credentials for MongoDB access

## Test Data
- Database name: `prisma` (staging) or `focus_db` (local)
- Required collections: `base_paths`, `node2`, `node4`

## Test Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Connect to MongoDB database | Database name from config | Connection successful |
| 2 | List all collections in database | N/A | Returns list of collection names |
| 3 | Verify `base_paths` collection exists | Collection name: "base_paths" | Collection found in list |
| 4 | Verify `node2` collection exists | Collection name: "node2" | Collection found in list |
| 5 | Verify `node4` collection exists | Collection name: "node4" | Collection found in list |
| 6 | Log summary of validation | Collection names | All required collections present |

## Expected Result (overall)
All required MongoDB collections (`base_paths`, `node2`, `node4`) are present in the database. No missing collections that would break recording functionality.

## Post-Conditions
None (read-only test)

## Attachments
- MongoDB collections list screenshot
- Test execution log

## Authentication
MongoDB credentials from environments.yaml

## Assertions
- `base_paths` collection exists
- `node2` collection exists
- `node4` collection exists
- No missing critical collections

## Environment
Any (Dev/Staging/Production)

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_required_collections_exist`  
**Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`  
**Test Class:** `TestMongoDBDataQuality`

## Execution Command
```bash
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_required_collections_exist -v
```

## Related Issues
- PZ-13598 (Parent)

---

# Test Case NEW-002

## Summary
**Data Quality – node4 Schema Validation**

## Test Type
Integration Test

## Priority
High

## Components/Labels
`focus-server`, `mongodb`, `data-quality`, `schema`, `node4`

## Requirements
- PZ-13598 (Data Quality – Mongo collections and schema)

## Objective
Verify that documents in the `node4` collection (recordings metadata) have all required fields with correct data types. Incorrect or missing fields would cause the Focus Server to fail when retrieving recording metadata for history playback. Type mismatches can cause parsing errors and system crashes.

## Pre-Conditions
- **PC-010:** MongoDB is reachable
- **PC-013:** node4 collection exists and contains data
- **PC-014:** At least 1 recording document exists

## Test Data
- Collection: `node4`
- Sample size: up to 100 documents
- Required fields:
  - `uuid` (string)
  - `start_time` (int/float/datetime)
  - `end_time` (int/float/datetime)
  - `deleted` (boolean)

## Test Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Access `node4` collection | Collection name: "node4" | Collection accessible |
| 2 | Count total documents | N/A | Returns document count |
| 3 | Sample up to 100 documents | Sample size: min(100, total) | Documents retrieved |
| 4 | For each document, verify field existence | Required fields list | All fields present |
| 5 | For each document, verify field types | Field: type mapping | Types match expected |
| 6 | Check for null values in critical fields | uuid, start_time, end_time | No null values |
| 7 | Log validation summary | Errors list | Report any schema violations |

## Expected Result (overall)
All sampled documents in `node4` collection have:
- All required fields present (`uuid`, `start_time`, `end_time`, `deleted`)
- Correct data types for each field
- No null values in critical fields

## Post-Conditions
None (read-only test)

## Attachments
- Sample document structure (JSON)
- Schema validation report
- Error log (if violations found)

## Authentication
MongoDB credentials from environments.yaml

## Assertions
- Every document has `uuid` field (string)
- Every document has `start_time` field (numeric/datetime)
- Every document has `end_time` field (numeric/datetime)
- Every document has `deleted` field (boolean)
- No null values in required fields
- Field types match expected types

## Environment
Any (Dev/Staging/Production) with data

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_node4_schema_validation`  
**Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`  
**Test Class:** `TestMongoDBDataQuality`

## Execution Command
```bash
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_node4_schema_validation -v
```

## Related Issues
- PZ-13598 (Parent)

---

# Test Case NEW-003

## Summary
**Data Quality – Recordings Metadata Completeness**

## Test Type
Integration Test

## Priority
Critical

## Components/Labels
`focus-server`, `mongodb`, `data-quality`, `data-integrity`, `recordings`

## Requirements
- PZ-13598 (Data Quality – Mongo collections and schema)

## Objective
Scan ALL recordings in `node4` collection and verify that none have missing critical metadata. Missing metadata prevents the Focus Server from correctly indexing and retrieving recordings for history playback. Orphaned records (missing 2+ fields) waste storage and cause query errors.

## Pre-Conditions
- **PC-010:** MongoDB is reachable
- **PC-013:** node4 collection exists
- **PC-015:** Production or staging environment with real data

## Test Data
- Collection: `node4`
- Scan: ALL documents (not sampled)
- Critical fields: `uuid`, `start_time`, `end_time`, `deleted`

## Test Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Access `node4` collection | Collection name: "node4" | Collection accessible |
| 2 | Count total documents | N/A | Returns total recording count |
| 3 | For each required field, count missing values | Field name + null check | Count of documents with missing/null field |
| 4 | Calculate percentage of records with missing data | (missing_count / total_count) * 100 | Percentage per field |
| 5 | Identify orphaned records (missing 2+ fields) | Complex aggregation query | Count of orphaned documents |
| 6 | Log detailed report | Field: count: percentage | Summary of data quality issues |

## Expected Result (overall)
- **ZERO** recordings with missing `uuid`
- **ZERO** recordings with missing `start_time`
- **ZERO** recordings with missing `end_time`
- **ZERO** recordings with missing `deleted` flag
- **ZERO** orphaned records (missing 2+ critical fields)

## Post-Conditions
None (read-only test)

## Attachments
- Data quality report (CSV/JSON)
- List of orphaned record IDs (if found)
- Metadata completeness statistics

## Authentication
MongoDB credentials from environments.yaml

## Assertions
- No recordings have missing `uuid` field
- No recordings have missing `start_time` field
- No recordings have missing `end_time` field
- No recordings have missing `deleted` field
- No recordings have null values in critical fields
- No orphaned records detected

## Environment
Staging/Production (with real recording data)

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_recordings_have_all_required_metadata`  
**Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`  
**Test Class:** `TestMongoDBDataQuality`

## Execution Command
```bash
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_recordings_have_all_required_metadata -v
```

## Related Issues
- PZ-13598 (Parent)

## Notes
**This is a CRITICAL test** - if this fails, it indicates data corruption or incomplete recording indexing that MUST be fixed before production deployment.

---

# Test Case NEW-004

## Summary
**Data Quality – MongoDB Indexes Validation**

## Test Type
Integration Test

## Priority
High

## Components/Labels
`focus-server`, `mongodb`, `data-quality`, `performance`, `indexes`

## Requirements
- PZ-13598 (Data Quality – Mongo collections and schema)
- FOCUS-PERF-QUERY (Query performance requirements)

## Objective
Verify that MongoDB has proper indexes on `node4` collection for optimal query performance. Missing indexes cause SLOW queries, especially on large datasets. Time range queries without indexes on `start_time`/`end_time` can take **minutes instead of milliseconds**, making history playback unusable.

## Pre-Conditions
- **PC-010:** MongoDB is reachable
- **PC-013:** node4 collection exists
- **PC-016:** Database administrator access (to view indexes)

## Test Data
- Collection: `node4`
- Expected indexes:
  1. `start_time` (ascending)
  2. `end_time` (ascending)
  3. `uuid` (ascending, UNIQUE)
  4. `deleted` (ascending)

## Test Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Access `node4` collection | Collection name: "node4" | Collection accessible |
| 2 | List all indexes | list_indexes() | Returns index list |
| 3 | Parse index details | Index name, keys, unique flag | Index metadata extracted |
| 4 | Verify index on `start_time` exists | Field: "start_time", direction: 1 | Index found |
| 5 | Verify index on `end_time` exists | Field: "end_time", direction: 1 | Index found |
| 6 | Verify index on `uuid` exists (UNIQUE) | Field: "uuid", unique: true | Unique index found |
| 7 | Verify index on `deleted` exists | Field: "deleted", direction: 1 | Index found |
| 8 | Check for missing critical indexes | Compare expected vs actual | Log missing indexes |

## Expected Result (overall)
All critical indexes are present on `node4` collection:
- ✅ Index on `start_time` for time range queries
- ✅ Index on `end_time` for time range queries
- ✅ **Unique** index on `uuid` for lookups
- ✅ Index on `deleted` for filtering

**Performance:** Queries on these fields should use indexes (not full collection scans).

## Post-Conditions
None (read-only test)

## Attachments
- Index list export (JSON)
- Query explain plans (before/after)
- Performance comparison report

## Authentication
MongoDB credentials from environments.yaml

## Assertions
- Index exists on `node4.start_time`
- Index exists on `node4.end_time`
- Index exists on `node4.uuid` AND is marked as unique
- Index exists on `node4.deleted`
- All critical indexes are properly configured

## Environment
Any (Dev/Staging/Production)

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_mongodb_indexes_exist_and_optimal`  
**Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`  
**Test Class:** `TestMongoDBDataQuality`

## Execution Command
```bash
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_mongodb_indexes_exist_and_optimal -v
```

## Related Issues
- PZ-13598 (Parent)
- PZ-13571 (Performance testing)

## Performance Impact
**Without indexes:**
- Time range query on 1M recordings: ~30-60 seconds ❌
- UUID lookup: ~5-10 seconds ❌

**With indexes:**
- Time range query on 1M recordings: <100ms ✅
- UUID lookup: <10ms ✅

## Notes
If this test **fails** (missing indexes), it's not a blocker, but a **performance warning**. Recommend creating the missing indexes immediately to avoid slow queries in production.

---

# Test Case NEW-005

## Summary
**MongoDB Recovery – Recordings Indexed After Outage**

## Test Type
Integration Test (Resilience & Recovery)

## Priority
Critical

## Components/Labels
`focus-server`, `mongodb`, `resilience`, `recovery`, `indexing`, `data-sync`

## Requirements
- PZ-13604 (Integration – Orchestrator error triggers rollback)
- FOCUS-RESILIENCE-RECOVERY (System recovery requirements)

## Objective
Validate that when MongoDB experiences an outage and then recovers, any recordings that were added to storage during the outage are automatically indexed in MongoDB after recovery. This ensures no data loss and complete recording availability for history playback.

## Pre-Conditions
- **PC-010:** MongoDB is reachable and healthy
- **PC-017:** Kubernetes access available (to simulate outage)
- **PC-018:** Storage contains recordings
- **PC-019:** Focus Server has recovery/indexing mechanism
- **PC-020:** Ability to simulate new recordings during outage

## Test Data
- MongoDB namespace: `default`
- MongoDB deployment: `mongodb`
- Test recording: Simulated or real recording file
- Initial recording count: N (from MongoDB before outage)

## Test Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | **SETUP:** Verify MongoDB is healthy | Ping MongoDB | Connection successful |
| 2 | Count existing recordings in MongoDB | Query node4 collection | Returns count = N |
| 3 | **SIMULATE OUTAGE:** Scale down MongoDB to 0 replicas | Replicas: 0 | MongoDB unavailable |
| 4 | Verify MongoDB is unreachable | Connection attempt | Connection fails (expected) |
| 5 | **SIMULATE NEW RECORDING:** Add recording to storage | New recording file in storage | File created/exists |
| 6 | Attempt POST /configure (should fail) | History payload | Returns 503 Service Unavailable |
| 7 | **RECOVERY:** Restore MongoDB (scale to 1 replica) | Replicas: 1 | MongoDB restored |
| 8 | Wait for MongoDB to become ready | Timeout: 120s | MongoDB is accessible |
| 9 | **TRIGGER INDEXING:** Wait for recovery mechanism | Wait time: 60-300s | Indexing process runs |
| 10 | Verify new recording is indexed | Query node4 for new recording | Recording found in MongoDB |
| 11 | Verify recording count increased | Query node4 collection | Count = N + 1 |
| 12 | **VALIDATION:** POST /configure with recovered data | History payload including new recording | Returns 200 OK with stream details |

## Expected Result (overall)
After MongoDB recovers from outage:
1. ✅ MongoDB is accessible and healthy
2. ✅ New recordings added during outage are **automatically indexed**
3. ✅ Recording count in MongoDB reflects all recordings (including those added during outage)
4. ✅ Focus Server can successfully configure history playback with recovered data
5. ✅ No data loss - all recordings are available

## Post-Conditions
- **TEARDOWN-003:** Restore MongoDB to healthy state (if not already)
- **TEARDOWN-004:** Clean up test recording files (if created)
- **TEARDOWN-005:** Verify no lingering outage effects

## Attachments
- MongoDB logs during outage and recovery
- Focus Server logs showing recovery mechanism
- Recording indexing timeline (timestamps)
- Before/after MongoDB state comparison

## Authentication
- MongoDB credentials from environments.yaml
- Kubernetes credentials (kubeconfig)

## Assertions
- MongoDB outage is successfully simulated (connection fails)
- MongoDB recovery is successful (connection restored)
- New recording is present in storage during outage
- **New recording is indexed in MongoDB after recovery**
- Recording count increases by expected amount
- POST /configure succeeds with recovered data
- No errors in Focus Server logs during recovery

## Environment
**Staging** (requires Kubernetes access)

**WARNING:** Do NOT run on Production! This test simulates MongoDB outage.

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_mongodb_recovery_indexes_pending_recordings`  
**Test File:** `tests/integration/infrastructure/test_mongodb_outage_resilience.py`  
**Test Class:** `TestMongoDBOutageResilience`

## Execution Command
```bash
# Run this test alone (it's slow and disruptive)
pytest tests/integration/infrastructure/test_mongodb_outage_resilience.py::TestMongoDBOutageResilience::test_mongodb_recovery_indexes_pending_recordings -v -s

# With markers
pytest -m "mongodb and recovery" -v -s
```

## Related Issues
- PZ-13604 (Parent - MongoDB recovery)
- PZ-13603 (MongoDB outage handling)

## Test Duration
**Estimated:** 5-10 minutes
- Outage simulation: 30-60s
- Recovery wait: 2-3 minutes
- Indexing wait: 2-5 minutes

## Known Limitations
1. **Requires Kubernetes access** - test will skip if K8s not available
2. **Requires working recovery mechanism** - if Focus Server doesn't have automatic indexing, test will fail (this is expected and indicates missing feature)
3. **Slow test** - marked with `@pytest.mark.slow`
4. **Disruptive** - simulates MongoDB outage (use staging only!)

## Success Criteria
This test **PASSES** if the Focus Server has an automatic recovery mechanism that indexes recordings added during MongoDB downtime.

This test **FAILS** if:
- No recovery mechanism exists ❌
- Recovery mechanism exists but doesn't work ❌
- Indexing is manual (requires operator intervention) ❌

## Recovery Mechanism Detection
The test will check for these common recovery patterns:
1. **Periodic scan:** Focus Server periodically scans storage and indexes missing recordings
2. **Event-driven:** Focus Server watches for MongoDB recovery and triggers indexing
3. **Manual:** Operator must run indexing script (test will fail - not acceptable)

## Notes
**CRITICAL:** This test validates a KEY resilience requirement. If this test fails, it means the system is NOT resilient to MongoDB outages, and recordings can be lost or inaccessible after recovery.

**Recommendation:** If test fails, implement automatic recovery mechanism before production deployment.

---

# Test Case T-DATA-001

## Summary
**Data Lifecycle – Soft Delete Implementation**

## Test Type
Integration Test

## Priority
Medium

## Components/Labels
`focus-server`, `mongodb`, `data-lifecycle`, `data-integrity`, `soft-delete`

## Requirements
- PZ-13598 (Data Quality – Mongo collections and schema)

## Objective
Verify that the `deleted` field is correctly implemented for soft deletion and that historical queries properly filter out deleted recordings. Ensure data integrity and cleanup service functionality.

## Pre-Conditions
- **PC-010:** MongoDB is reachable
- **PC-013:** Recording collection exists with data
- **PC-024:** Some recordings are marked as deleted

## Test Steps

| # | Action | Expected Result |
|---|--------|-----------------|
| 1 | Count total recordings | Total count retrieved |
| 2 | Count deleted recordings (deleted=True) | Deleted count retrieved |
| 3 | Count active recordings (deleted=False) | Active count retrieved |
| 4 | Verify all recordings have 'deleted' field | No missing fields |
| 5 | Verify 'deleted' is boolean type | All are True/False |
| 6 | Simulate historical query (deleted=False) | Returns only active |
| 7 | Sample deleted recordings | Details logged |

## Expected Result (overall)
- All recordings have valid `deleted` flag (boolean)
- Historical queries correctly filter deleted recordings
- Soft delete implementation is working properly

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_deleted_recordings_marked_properly`  
**Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`

## Execution Command
```bash
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_deleted_recordings_marked_properly -v
```

---

# Test Case T-DATA-002

## Summary
**Data Lifecycle – Historical vs Live Recordings Classification**

## Test Type
Integration Test

## Priority
High

## Components/Labels
`focus-server`, `mongodb`, `data-lifecycle`, `data-quality`, `data-integrity`, `recordings`, `cleanup`

## Requirements
- **PZ-13598** (Data Quality – Mongo collections and schema)
- **FOCUS-DATA-LIFECYCLE** (Recording lifecycle management)
- **FOCUS-CLEANUP-SERVICE** (Data cleanup and retention)

## Objective

Validate that MongoDB correctly distinguishes between **Historical** (completed), **Live** (in-progress), and **Deleted** (cleanup) recordings. Verify that the recording lifecycle is properly managed and that cleanup services are functioning correctly.

### Business Impact
- Historical recordings must be indexed for history playback via `POST /recordings_in_time_range`
- Live recordings must be distinguished from stale/crashed recordings
- Deleted recordings must be properly marked for cleanup
- Data quality directly impacts user experience and system reliability

## Pre-Conditions

- **PC-010:** MongoDB is reachable and accessible
- **PC-013:** Recording collection exists with data
- **PC-021:** Recording collection is dynamically named (GUID-based)
- **PC-022:** `base_paths` collection contains GUID
- **PC-023:** System has active or historical recordings

## Architectural Context

**MongoDB Role:** Metadata index for recordings (NOT raw data)
- **Used by:** Focus Server & Baby Analyzer
- **Purpose:** Find raw files (PRP2/SEGY) in S3/storage for time ranges
- **API:** `POST /recordings_in_time_range` requires `start_time` and `end_time`

**Recording Types:**

| Type | Schema | Status |
|------|--------|--------|
| **Historical** | `start_time` + `end_time` + `deleted=False` | Normal ✅ |
| **Live** | `start_time` + NO `end_time` + `deleted=False` | Normal ✅ |
| **Deleted** | `deleted=True` | Cleanup ⚠️ |
| **Stale** | Old (>24h) + NO `end_time` + `deleted=False` | Bug ❌ |

## Test Data

- **Database:** `prisma` (staging)
- **Collections:** 
  - `base_paths` - GUID pointer
  - `{GUID}` - recordings (e.g., `77e49b5d-e06a-4aae-a33e-17117418151c`)
- **Fields:** `uuid`, `start_time`, `end_time`, `deleted`
- **Thresholds:** Stale = >24h without `end_time`

## Test Steps

| # | Action | Expected Result |
|---|--------|-----------------|
| **SETUP** | | |
| 1 | Connect to MongoDB | Success |
| 2 | Get recording collection GUID from base_paths | GUID retrieved |
| 3 | Access recording collection | Collection accessible |
| 4 | Count total recordings | Total > 0 |
| **CLASSIFICATION** | | |
| 5 | Count Historical recordings | Count returned |
| 6 | Count Live recordings | Count returned |
| 7 | Count Deleted recordings | Count returned |
| 8 | Count Invalid recordings (no start_time) | Should be 0 |
| 9 | Calculate percentages | Calculated |
| 10 | Log classification summary | Summary displayed |
| **VALIDATION** | | |
| 11 | Sample 5 Historical recordings | Retrieved |
| 12 | Verify complete metadata | All fields present |
| 13 | Calculate durations | Duration in hours |
| 14 | Log Historical samples | Details shown |
| **LIVE ANALYSIS** | | |
| 15 | Check Live recordings age | Age calculated |
| 16 | Identify stale recordings (>24h) | List of stale |
| 17 | If stale found, log warning | Warning displayed |
| 18 | If no stale, confirm recent | Success message |
| **CLEANUP SERVICE** | | |
| 19 | Count Deleted with end_time | Count returned |
| 20 | Count Deleted without end_time | Count returned |
| 21 | Sample 3 Deleted recordings | Retrieved |
| 22 | Calculate age of deleted | Age in days |
| 23 | Log Deleted samples | Details shown |
| **ASSERTIONS** | | |
| 24 | Assert: No invalid recordings | PASS if 0 |
| 25 | Assert: Classification integrity | PASS if totals match |
| 26 | Assert: Historical majority (>50%) | PASS if >50% |
| 27 | Log final result | Test status |

## Expected Result (overall)

### Classification Results
- **Historical:** ~99% (completed recordings)
- **Live:** <1% (recent, <24h)
- **Deleted:** <1% (cleanup)
- **Invalid:** 0 ✅
- **Stale:** 0 ✅

### Data Integrity
- ✅ All recordings have `start_time`
- ✅ Classification totals match
- ✅ Historical are majority (>50%)
- ✅ Live recordings are recent
- ⚠️ Deleted may lack `end_time`

## Post-Conditions
None (read-only test)

## Authentication
MongoDB credentials from `environments.yaml` (read-only)

## Assertions

**Critical (Test FAILS if violated):**
1. `invalid_count == 0` (all have start_time)
2. `historical + live + deleted == total` (integrity)
3. `historical / total > 0.50` (majority)

**Warning (Test WARNS but PASSES):**
4. Stale recordings detected (>24h without end_time)
5. Deleted recordings missing end_time

## Environment
Any with data: Dev/Staging/Production (read-only)  
**Recommended:** Staging

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_historical_vs_live_recordings`  
**Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`  
**Test Class:** `TestMongoDBDataQuality`

## Execution Command
```bash
# Run this test
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_historical_vs_live_recordings -v

# Run all data lifecycle tests
pytest -m data_lifecycle -v
```

## Test Results (Last Run)

**Date:** 2025-10-15  
**Status:** ✅ **PASSED**

```
📊 Recording Classification:
   Historical: 3,414 (99.3%) ✅
   Live: 1 (0.03%) ✅
   Deleted: 24 (0.7%) ⚠️
   Invalid: 0 (0%) ✅

✅ All assertions passed
⚠️  24 deleted recordings missing end_time
✅ All Live recordings recent (<24h)
✅ No stale recordings
```

## Related Issues
- **PZ-13598** (Parent)
- **T-DATA-001** (Soft Delete - Related)
- **BUG-CLEANUP-001** (Missing end_time - Discovered)

## Recommendations

### 🔴 High Priority: Fix Deletion Logic
```python
def delete_recording(uuid):
    db.recordings.update_one(
        {"uuid": uuid},
        {
            "$set": {
                "deleted": True,
                "end_time": end_time or datetime.utcnow(),
                "deleted_at": datetime.utcnow()
            }
        }
    )
```

### 🟡 Medium Priority: Add Status Field
```python
class RecordingStatus:
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"
```

## Questions for Development Team

1. **Which service sets `deleted=True`?**
   - Sweeper / Data Manager / Other?

2. **What triggers cleanup?**
   - Retention policy / Manual / Storage quota?

3. **Should deleted recordings have `end_time`?**
   - Yes/No/Depends?

4. **Plan to add `status` field?**
   - Yes/Maybe/No?

## Success Criteria

**Test PASSES if:**
- ✅ All recordings have `start_time`
- ✅ Classification totals match
- ✅ Historical >50%
- ✅ Live are recent (<24h)
- ✅ No stale recordings

**Test WARNS if:**
- ⚠️ Deleted missing `end_time`
- ⚠️ Live count >5%

**Test FAILS if:**
- ❌ Any missing `start_time`
- ❌ Classification mismatch
- ❌ Historical <50%
- ❌ Stale recordings found

## Notes

**CRITICAL:** This test validates data lifecycle management:
- Historical recordings for playback
- Live vs stale detection
- Cleanup service functionality

**Impact:** Failures indicate:
- Data quality issues
- Cleanup service problems
- Need for schema improvements

## Related Documentation
- `XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md` - Full Xray specification
- `T_DATA_002_HISTORICAL_VS_LIVE_REPORT.md` - Detailed test report
- `LIVE_VS_HISTORICAL_RECORDINGS.md` - Technical deep-dive

---

# 📊 Summary for Jira Import

## Test Cases Created: 8

| ID | Summary | Status | Priority | Component |
|----|---------|--------|----------|-----------|
| PZ-13556 | SingleChannel View Mapping | ✅ Automated & Tested | Medium | API |
| NEW-001 | MongoDB Collections Exist | ✅ Automated & Updated | High | Data Quality |
| NEW-002 | node4 Schema Validation | ✅ Automated & Updated | High | Data Quality |
| NEW-003 | Recordings Metadata Completeness | ✅ Automated & Updated | Critical | Data Quality |
| NEW-004 | MongoDB Indexes Validation | ✅ Automated & Updated | High | Performance |
| NEW-005 | MongoDB Recovery Indexing | 🔄 To Implement | Critical | Resilience |
| T-DATA-001 | Soft Delete Implementation | ✅ Automated & Tested | Medium | Data Lifecycle |
| T-DATA-002 | Historical vs Live Classification | ✅ Automated & Tested | High | Data Lifecycle |

## Import Instructions

### Method 1: Manual Copy-Paste to Jira
1. Open Jira → Project PZ → Test Repository
2. Click "Create Test" or "Update Test" (for PZ-13556)
3. Copy each test case above (one at a time)
4. Paste into corresponding Jira fields:
   - Summary → Summary
   - Test Type → Test Type
   - Priority → Priority
   - Components/Labels → Components + Labels
   - etc.

### Method 2: CSV Import (Bulk)
Create a CSV file with columns:
```
Summary,Test Type,Priority,Components,Steps,Expected Result,Automation Status,Test Function
```

### Method 3: Xray API Import (Automated)
Use Jira Xray REST API to import test cases programmatically.

---

**Created:** 2025-10-15  
**Last Updated:** 2025-10-15  
**Author:** Roy Avrahami  
**Total Tests:** 8  
**Automation Coverage:** 88% (7/8 automated, 1 to implement)

---

## 🔗 Links to Test Files

- **PZ-13556 (Completed):** `tests/integration/api/test_singlechannel_view_mapping.py` (13 tests, all passed)
- **NEW-001 to NEW-004 (Updated):** `tests/integration/infrastructure/test_mongodb_data_quality.py` (6 tests total, including T-DATA-001 and T-DATA-002)
- **NEW-005 (To Implement):** `tests/integration/infrastructure/test_mongodb_outage_resilience.py` (1 test)
- **T-DATA-001 (New):** `tests/integration/infrastructure/test_mongodb_data_quality.py` - Soft Delete Implementation (PASSED ✅)
- **T-DATA-002 (New):** `tests/integration/infrastructure/test_mongodb_data_quality.py` - Historical vs Live Classification (PASSED ✅)

---

## 📄 Full Test Documentation

### Detailed Reports
- **XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md** - Complete Xray specification for T-DATA-002
- **T_DATA_002_HISTORICAL_VS_LIVE_REPORT.md** - Full test execution report with results
- **T_DATA_001_SOFT_DELETE_REPORT.md** - Soft delete test report
- **LIVE_VS_HISTORICAL_RECORDINGS.md** - Technical deep-dive on recording classification

### Bug Reports
- **MONGODB_BUGS_REPORT.md** - Comprehensive bug report from data quality tests
- **BUG-CLEANUP-001** - Missing end_time on deleted recordings (discovered by T-DATA-002)

### Schema Documentation
- **MONGODB_SCHEMA_REAL_FINDINGS.md** - Actual MongoDB schema (GUID-based collections)
- **HOW_TO_DISCOVER_DATABASE_SCHEMA.md** - Guide for schema discovery

---

## ✅ Ready for Jira Xray Import!

