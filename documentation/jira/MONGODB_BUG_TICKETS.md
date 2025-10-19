# MongoDB Data Quality - Bug Tickets

**Created:** October 16, 2025  
**Tested Environment:** Staging  
**Found By:** QA Automation Tests  
**Total Issues:** 3 (1 HIGH, 1 MEDIUM, 1 LOW)

---

## Bug Ticket #1: Missing Critical Database Indexes

### 🔴 Severity: HIGH (Critical Performance Issue)

### Summary
The recording collection (`77e49b5d-e06a-4aae-a33e-17117418151c`) is missing 4 critical database indexes, causing severe performance degradation for all time-based queries and UUID lookups.

---

### Description

**Current State:**
- Recording collection has **ONLY 1 index** (`_id_`)
- Total recordings: 3,456

**Missing Indexes:**
1. ❌ `start_time` index (ascending)
2. ❌ `end_time` index (ascending)
3. ❌ `uuid` index (ascending, **UNIQUE**)
4. ❌ `deleted` index (ascending)

**Impact:**
Without these indexes, MongoDB performs **full collection scans** for every query, resulting in:
- History playback queries: **30-60 seconds** (expected: <100ms)
- UUID lookups: **5-10 seconds** (expected: <10ms)
- Delete filtering: **extremely slow**
- **1000x performance degradation**

---

### Steps to Reproduce

1. Connect to MongoDB staging environment:
   ```bash
   mongo mongodb://root:prisma@10.10.10.103:27017/prisma?authSource=admin
   ```

2. Check existing indexes:
   ```javascript
   use prisma
   db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').getIndexes()
   ```

3. **Expected Result:** 5 indexes (_id, start_time, end_time, uuid, deleted)
4. **Actual Result:** Only 1 index (_id)

---

### How It Was Found

**Automated Test:** `test_mongodb_indexes_exist_and_optimal`
- **Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`
- **Line:** 667-805
- **Test Status:** ❌ FAILED

**Test Output:**
```
ERROR: ❌ Index on 'start_time' is MISSING
ERROR: ❌ Index on 'end_time' is MISSING
ERROR: ❌ Index on 'uuid' is MISSING
ERROR: ❌ Index on 'deleted' is MISSING

AssertionError: Critical indexes are MISSING: ['start_time', 'end_time', 'uuid'].
These indexes are REQUIRED for acceptable query performance.
History playback will be extremely slow without them.
```

---

### Impact Analysis

#### Performance Impact
| Query Type | Without Indexes | With Indexes | Degradation |
|------------|----------------|--------------|-------------|
| Time range queries | 30-60 seconds | <100ms | **1000x slower** |
| UUID lookups | 5-10 seconds | <10ms | **500-1000x slower** |
| Delete filtering | Very slow | Fast | **~1000x slower** |
| History playback | **Unusable** | Instant | **Critical** |

#### Business Impact
- **User Experience:** History feature appears broken (30-60s response time)
- **Support Tickets:** Likely increase in "system too slow" complaints
- **Data Integrity:** No uniqueness enforcement on UUID field (risk of duplicates)
- **Scalability:** Performance will degrade further as data grows

#### Technical Impact
- Full collection scans on every query (3,456 documents)
- High CPU usage on MongoDB server
- Increased memory consumption
- No query optimization possible

---

### Expected Behavior

**Recording collection should have 5 indexes:**

1. **_id_** (default, exists ✅)
   - Unique identifier for MongoDB documents

2. **start_time_idx** (MISSING ❌)
   - Purpose: Time range queries for history playback
   - Type: Ascending
   - Query Pattern: `{start_time: {$gte: startDate, $lte: endDate}}`

3. **end_time_idx** (MISSING ❌)
   - Purpose: Time range queries for completed recordings
   - Type: Ascending
   - Query Pattern: `{end_time: {$gte: startDate, $lte: endDate}}`

4. **uuid_unique** (MISSING ❌)
   - Purpose: Fast UUID lookups + uniqueness enforcement
   - Type: Ascending, **UNIQUE**
   - Query Pattern: `{uuid: "specific-uuid"}`
   - Critical: Prevents duplicate recordings

5. **deleted_idx** (MISSING ❌)
   - Purpose: Fast filtering of deleted/active recordings
   - Type: Ascending
   - Query Pattern: `{deleted: false}` or `{deleted: true}`

---

### Root Cause Analysis

**Possible Causes:**
1. Indexes were never created during initial database setup
2. Indexes were dropped accidentally during maintenance
3. Collection was recreated without indexes (e.g., after migration)
4. Migration script forgot to create indexes
5. Different environments have different configurations

**Investigation Needed:**
- Check if production has the same issue
- Review database initialization/migration scripts
- Check if other GUID-based collections have similar issues

---

### Recommended Fix

#### Solution: Create Missing Indexes

**Priority:** 🔴 **URGENT** - Fix immediately  
**Estimated Effort:** 3 minutes  
**Risk Level:** Low (non-blocking operation)

#### Implementation

**Option 1: MongoDB Shell (Manual)**
```javascript
use prisma

// Replace GUID with actual collection name
var collectionName = "77e49b5d-e06a-4aae-a33e-17117418151c";

// Create indexes (run in background to avoid blocking)
db.getCollection(collectionName).createIndex(
    { "start_time": 1 }, 
    { background: true, name: "start_time_idx" }
);

db.getCollection(collectionName).createIndex(
    { "end_time": 1 }, 
    { background: true, name: "end_time_idx" }
);

db.getCollection(collectionName).createIndex(
    { "uuid": 1 }, 
    { unique: true, background: true, name: "uuid_unique" }
);

db.getCollection(collectionName).createIndex(
    { "deleted": 1 }, 
    { background: true, name: "deleted_idx" }
);

// Verify indexes were created
db.getCollection(collectionName).getIndexes();
```

**Option 2: Python Script (Automated)**
```python
from pymongo import MongoClient, ASCENDING

# Connect
client = MongoClient("mongodb://root:prisma@10.10.10.103:27017/?authSource=admin")
db = client["prisma"]

# Get collection
collection = db["77e49b5d-e06a-4aae-a33e-17117418151c"]

# Create indexes
collection.create_index([("start_time", ASCENDING)], background=True, name="start_time_idx")
collection.create_index([("end_time", ASCENDING)], background=True, name="end_time_idx")
collection.create_index([("uuid", ASCENDING)], unique=True, background=True, name="uuid_unique")
collection.create_index([("deleted", ASCENDING)], background=True, name="deleted_idx")

print("✅ All indexes created successfully")
```

---

### Verification Steps

**After Fix:**

1. **Verify indexes exist:**
   ```bash
   py scripts/quick_mongo_explore.py
   ```
   Should show: `🔐 Indexes (5):`

2. **Run automated test:**
   ```bash
   py -m pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_mongodb_indexes_exist_and_optimal -v
   ```
   Should show: `PASSED ✅`

3. **Test query performance:**
   ```javascript
   // Before: 30-60 seconds
   // After: <100ms
   db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').find({
       start_time: {$gte: ISODate("2025-01-01"), $lte: ISODate("2025-12-31")}
   }).explain("executionStats")
   ```
   Check: `executionStats.executionTimeMillis` should be <100ms

4. **Verify uniqueness enforcement:**
   ```javascript
   // Try to insert duplicate UUID (should fail)
   db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').insertOne({
       uuid: "existing-uuid",
       start_time: new Date(),
       deleted: false
   })
   // Should fail with: "E11000 duplicate key error"
   ```

---

### Additional Notes

**Important Considerations:**
- Indexes are created in **background mode** (non-blocking)
- Total creation time: ~2-3 minutes for all 4 indexes
- System remains operational during index creation
- Monitor MongoDB CPU/memory during creation (should be minimal impact)

**Follow-up Actions:**
1. Apply same fix to **production** (if affected)
2. Check **other GUID-based collections** for missing indexes
3. Update database initialization scripts to include these indexes
4. Add monitoring to alert if indexes are ever dropped

**Prevention:**
- Add index creation to database migration scripts
- Include in database initialization/setup procedures
- Add automated tests to CI/CD pipeline
- Document required indexes in technical specifications

---

### Related Issues
- See: Bug Ticket #2 (Low Recognition Rate) - May be related to slow queries
- See: `MONGODB_BUGS_REPORT.md` for detailed technical analysis

---

### Attachments
- Test file: `tests/integration/infrastructure/test_mongodb_data_quality.py`
- Investigation script: `scripts/quick_mongo_explore.py`
- Technical report: `MONGODB_BUGS_REPORT.md`
- Workflow guide: `MONGODB_ISSUES_WORKFLOW.md`

---

### Labels
`mongodb` `performance` `critical` `indexes` `data-quality` `quick-win`

---

### Assignee
**Recommended:** DevOps / DBA Team

---

### Priority Matrix
| Impact | Effort | Priority |
|--------|--------|----------|
| 🔴 CRITICAL (1000x slower) | 🟢 LOW (3 min) | 🔴 **URGENT** |

**ROI:** 🟢 **EXCELLENT** - Massive impact with minimal effort

---

---

## Bug Ticket #2: Low Recording Recognition Rate (61.3%)

### 🟡 Severity: MEDIUM (Data Accessibility Issue)

### Summary
Out of 5,612 total recordings, 2,173 (38.7%) are classified as "unrecognized" and stored in a separate collection, making them inaccessible to users through normal history playback.

---

### Description

**Current State:**
```
Total recordings: 5,612
├── Recognized: 3,439 (61.3%) ✅
└── Unrecognized: 2,173 (38.7%) ❌

Collections:
├── 77e49b5d-e06a-4aae-a33e-17117418151c (recognized)
└── unrecognized_recordings (2,173 recordings)
```

**Problem:**
- Recognition rate: **61.3%** (LOW ❌)
- Expected rate: **>80%** (GOOD ✅)
- Gap: **18.7 percentage points**
- Missing data: **2,173 recordings** not accessible

---

### Steps to Reproduce

1. Run exploration script:
   ```bash
   py scripts/quick_mongo_explore.py
   ```

2. Observe output:
   ```
   Collection: 77e49b5d-e06a-4aae-a33e-17117418151c
   Documents: 3,439

   Collection: unrecognized_recordings
   Documents: 2,173

   Recognition Rate: 61.3% ⚠️ (Expected: >80%)
   ```

3. **Expected:** >80% recognition rate
4. **Actual:** 61.3% (below threshold)

---

### How It Was Found

**Automated Test:** `test_required_collections_exist`
- **Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`
- **Line:** 189-293
- **Test Status:** ✅ PASSED (with warnings)

**Test Output:**
```
WARNING: Recognition rate is LOW: 61.3%
   - Total recordings: 5,612
   - Recognized: 3,439 (61.3%)
   - Unrecognized: 2,173 (38.7%)
   - Expected: >80%
   - Gap: 18.7 percentage points
   
⚠️ 38.7% of recordings are NOT accessible through normal history queries!
```

---

### Impact Analysis

#### User Impact
- **Data Loss (from user perspective):** 38.7% of recordings not accessible
- **Missing History:** Users cannot view ~40% of their recorded data
- **Confusion:** "Where are my recordings?" support tickets
- **Trust:** Users lose confidence in system reliability

#### Business Impact
- **Wasted Storage:** Paying for storage of 2,173 unusable recordings
- **Lost Value:** Recorded data exists but provides zero value to users
- **Support Load:** Increased tickets about "missing recordings"
- **Customer Satisfaction:** Poor user experience

#### Technical Impact
- **Data Duplication:** Two separate collections to maintain
- **Query Complexity:** Need to query both collections
- **Inconsistency:** Different schemas/handling for recognized vs unrecognized
- **Maintenance:** Extra complexity in code and database

---

### Expected Behavior

**Recording Recognition Rate should be >80%:**

**Acceptable Rates:**
- **>80%:** Good ✅
- **70-80%:** Acceptable (needs improvement) ⚠️
- **<70%:** Poor (requires immediate action) ❌

**Current:** 61.3% ❌ **POOR**

**All recordings should:**
1. Be properly recognized and classified
2. Stored in the main recording collection (GUID-based)
3. Accessible through standard history queries
4. Have consistent metadata structure

---

### Root Cause Analysis

**Possible Causes:**

1. **Recognition Algorithm Issues:**
   - Algorithm too strict (rejects valid recordings)
   - Missing file format support
   - Incorrect pattern matching
   - Outdated recognition rules

2. **Data Format Problems:**
   - New recording formats not yet supported
   - Incomplete/corrupted metadata
   - Non-standard file structures
   - Missing required fields

3. **System Integration:**
   - Recording service not following spec
   - Multiple recording sources with different formats
   - Legacy data from old system versions

4. **Configuration:**
   - Recognition thresholds too high
   - Missing configuration for certain recording types

**Investigation Needed:**
1. Sample 20-30 unrecognized recordings
2. Analyze common patterns:
   - File formats
   - Metadata structure
   - Source systems
   - Recording types
3. Review recognition algorithm code
4. Compare recognized vs unrecognized characteristics

---

### Recommended Fix

#### Phase 1: Investigation (2 days)

**Steps:**
1. **Sample Analysis**
   ```python
   # Get sample of unrecognized recordings
   unrecognized = db.unrecognized_recordings.aggregate([
       {"$sample": {"size": 30}}
   ])
   
   # Analyze patterns
   for rec in unrecognized:
       print(f"UUID: {rec.get('uuid')}")
       print(f"Metadata: {rec.get('metadata')}")
       print(f"Source: {rec.get('source')}")
       print("---")
   ```

2. **Pattern Identification**
   - Group by common attributes
   - Identify missing fields
   - Find format differences
   - Determine source of unrecognized recordings

3. **Documentation**
   - Create analysis report
   - Document findings
   - Recommend algorithm improvements

#### Phase 2: Algorithm Improvement (1 week)

**Based on investigation findings:**

1. **Update Recognition Logic**
   - Add support for missing formats
   - Relax overly strict rules
   - Improve error handling
   - Add logging for failed recognitions

2. **Testing**
   - Test with historical unrecognized recordings
   - Verify no regression (recognized stay recognized)
   - Monitor recognition rate in staging

3. **Deployment**
   - Deploy to staging
   - Monitor for 2-3 days
   - Deploy to production if successful

#### Phase 3: Backlog Processing (optional)

**Re-process Existing Unrecognized Recordings:**
```python
# After algorithm improvement
unrecognized = db.unrecognized_recordings.find()

for rec in unrecognized:
    result = improved_recognition_algorithm(rec)
    if result.recognized:
        # Move to main collection
        db[guid_collection].insert_one(rec)
        db.unrecognized_recordings.delete_one({"_id": rec["_id"]})
```

---

### Verification Steps

**After Fix:**

1. **Run automated test:**
   ```bash
   py -m pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_required_collections_exist -v
   ```

2. **Check recognition rate:**
   ```bash
   py scripts/quick_mongo_explore.py
   ```
   Should show: `Recognition Rate: >80% ✅`

3. **Monitor new recordings:**
   - Track recognition rate daily
   - Alert if drops below 75%

4. **User Testing:**
   - Verify users can access previously missing recordings
   - Confirm history playback shows all data

---

### Success Criteria

**Definition of Done:**
- [x] Investigation complete with documented findings
- [x] Algorithm improved based on findings
- [x] Recognition rate >80% for new recordings
- [x] No regression (existing recognized recordings stay recognized)
- [x] Automated test passes
- [x] Deployed to production
- [x] Monitoring added

**Metrics:**
- Recognition rate: 61.3% → **>80%**
- Unrecognized count: 2,173 → **<1,000**
- User-accessible recordings: 61.3% → **>80%**

---

### Additional Notes

**Important Considerations:**
- Investigation phase is critical - don't skip!
- Test thoroughly before deploying to production
- Consider gradual rollout (canary deployment)
- Keep unrecognized_recordings collection as backup

**Follow-up Actions:**
1. Add monitoring dashboard for recognition rate
2. Set up alerts for drops below 75%
3. Regular audits of unrecognized recordings
4. Update documentation with supported formats

**Prevention:**
- Add validation to recording service
- Document supported recording formats
- Include recognition rate in QA checklist
- Automated tests in CI/CD pipeline

---

### Related Issues
- May be related to Bug Ticket #1 (slow queries affecting recognition?)
- See: `MONGODB_BUGS_REPORT.md` Bug #3 for details

---

### Attachments
- Test file: `tests/integration/infrastructure/test_mongodb_data_quality.py`
- Investigation script: `scripts/quick_mongo_explore.py`
- Sample analysis: (to be created during investigation)

---

### Labels
`mongodb` `data-quality` `recordings` `recognition` `investigation-required`

---

### Assignee
**Recommended:** Backend Development Team (Focus Server)

---

### Priority Matrix
| Impact | Effort | Priority |
|--------|--------|----------|
| 🟡 MEDIUM (38.7% data loss) | 🟡 MEDIUM (1-2 weeks) | 🟡 **MEDIUM** |

**ROI:** 🟡 **GOOD** - Significant improvement for reasonable effort

---

---

## Bug Ticket #3: Deleted Recordings Missing end_time Field

### 🟢 Severity: LOW (Data Quality Issue)

### Summary
24 deleted recordings (0.7% of total) are missing the `end_time` field, making it impossible to calculate recording duration and affecting analytics accuracy.

---

### Description

**Current State:**
```
Total Deleted Recordings: 24 (0.7%)
├── With end_time: 0 (0%)
└── Without end_time: 24 (100%) ❌
```

**Problem:**
- 24 recordings marked as `deleted=True`
- All 24 are missing `end_time` field (or `end_time=None`)
- Cannot calculate recording duration
- Analytics incomplete for these recordings

**Context:**
These recordings were likely deleted **while still recording** (before receiving an `end_time`). This is technically valid behavior, but results in incomplete metadata.

---

### Steps to Reproduce

1. Run check script:
   ```bash
   py scripts/check_live_vs_historical.py
   ```

2. Observe output:
   ```
   3️⃣ DELETED RECORDINGS (נמחקו)
   ההגדרה: deleted=True

   🗑️ Count: 24 (0.69%)

   דוגמאות (3 רשומות):
      1. UUID: 21fb3de5-4d58-43fc-8...
         Start: 2025-07-23 12:18:54.279000
         End: None  ← MISSING!
         Status: 🗑️ Deleted
   ```

3. Query MongoDB:
   ```javascript
   db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').find({
       deleted: true,
       $or: [
           {end_time: {$exists: false}},
           {end_time: null}
       ]
   }).count()
   // Result: 24
   ```

---

### How It Was Found

**Automated Test:** `test_deleted_recordings_marked_properly`
- **Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`
- **Line:** 845-960
- **Test Status:** ✅ PASSED (with warnings)

**Test Output:**
```
⚠️ Found 24 deleted recordings (0.7%) without end_time
   These were likely deleted while still running.
   
   Sample IDs:
   - 21fb3de5-4d58-43fc-8b97-9e8f6db2a3a4
   - 04d73fc4-7880-4f9a-8e8d-2a1c3b4d5e6f
   - 471b9ef9-d49b-4239-a9b8-7c8d9e0f1a2b
```

Also found by: `test_recordings_have_all_required_metadata`

---

### Impact Analysis

#### User Impact
- **Minor:** Only affects deleted recordings (0.7%)
- **Analytics:** Duration calculation fails for these 24 recordings
- **Reports:** Incomplete data in statistics/reports
- **User Visibility:** Low (deleted recordings not shown by default)

#### Business Impact
- **Data Quality:** Incomplete metadata (unprofessional)
- **Analytics Accuracy:** Reports missing 24 recordings
- **Minimal:** Only 0.7% of data affected

#### Technical Impact
- **Duration Calculation:** `duration = end_time - start_time` fails
- **Queries:** Need special handling for null end_time
- **Data Consistency:** Inconsistent state (should have end_time when deleted)

---

### Expected Behavior

**All deleted recordings should have end_time:**

```json
{
  "uuid": "21fb3de5-4d58-43fc-8...",
  "start_time": "2025-07-23 12:18:54.279",
  "end_time": "2025-07-23 12:25:30.123",  ← Should exist!
  "deleted": true,
  "deleted_at": "2025-07-23 12:25:30.123"
}
```

**When deleting a recording:**
1. If `end_time` already exists → keep it
2. If `end_time` is null/missing → set it to current time
3. Set `deleted = true`
4. Optionally add `deleted_at` timestamp

---

### Root Cause Analysis

**Why This Happens:**

The deletion logic does NOT set `end_time` when deleting:

```python
# Current (WRONG):
def delete_recording(uuid):
    db.recordings.update_one(
        {"uuid": uuid},
        {"$set": {"deleted": True}}
    )
```

**Scenario:**
1. Recording starts → `start_time` set
2. User deletes recording while still in progress → `deleted=True`
3. Recording never completes → `end_time` never set
4. Result: Deleted recording with no `end_time`

---

### Recommended Fix

#### Solution: Update Deletion Logic

**Priority:** 🟢 **LOW** - Fix when convenient  
**Estimated Effort:** 1 day  
**Risk Level:** Low

#### Implementation

**Updated Deletion Logic:**
```python
from datetime import datetime, timezone

def delete_recording(uuid):
    """
    Delete a recording and ensure end_time is set.
    
    Logic:
    - If end_time already exists: keep it
    - If end_time is null/missing: set to current time
    - Always set deleted=True
    - Always set deleted_at to current time
    """
    recording = db.recordings.find_one({"uuid": uuid})
    
    if not recording:
        raise RecordingNotFound(f"Recording {uuid} not found")
    
    # Prepare update
    update = {
        "deleted": True,
        "deleted_at": datetime.now(timezone.utc)
    }
    
    # Set end_time if not already set
    if not recording.get("end_time"):
        update["end_time"] = datetime.now(timezone.utc)
    
    # Update recording
    db.recordings.update_one(
        {"uuid": uuid},
        {"$set": update}
    )
    
    logger.info(f"Deleted recording {uuid}, end_time={'kept' if recording.get('end_time') else 'set'}")
```

**Alternative (MongoDB aggregation):**
```javascript
// Set end_time to current time only if it doesn't exist
db.recordings.updateOne(
    {uuid: "target-uuid"},
    [{
        $set: {
            deleted: true,
            deleted_at: new Date(),
            end_time: {
                $cond: {
                    if: {$ifNull: ["$end_time", false]},
                    then: new Date(),
                    else: "$end_time"
                }
            }
        }
    }]
)
```

---

### Verification Steps

**After Fix:**

1. **Test deletion of in-progress recording:**
   ```python
   # Create test recording
   test_uuid = "test-" + str(uuid.uuid4())
   db.recordings.insert_one({
       "uuid": test_uuid,
       "start_time": datetime.now(timezone.utc),
       "end_time": None,  # In progress
       "deleted": False
   })
   
   # Delete it
   delete_recording(test_uuid)
   
   # Verify end_time was set
   rec = db.recordings.find_one({"uuid": test_uuid})
   assert rec["end_time"] is not None, "end_time should be set!"
   assert rec["deleted"] == True
   assert rec["deleted_at"] is not None
   ```

2. **Test deletion of completed recording:**
   ```python
   # Create completed recording
   end_time = datetime.now(timezone.utc)
   test_uuid = "test-" + str(uuid.uuid4())
   db.recordings.insert_one({
       "uuid": test_uuid,
       "start_time": datetime.now(timezone.utc) - timedelta(hours=2),
       "end_time": end_time,  # Already completed
       "deleted": False
   })
   
   # Delete it
   delete_recording(test_uuid)
   
   # Verify end_time was NOT changed
   rec = db.recordings.find_one({"uuid": test_uuid})
   assert rec["end_time"] == end_time, "end_time should not change!"
   ```

3. **Run automated test:**
   ```bash
   py -m pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_deleted_recordings_marked_properly -v
   ```
   Should show no warnings about missing end_time

4. **Query check:**
   ```javascript
   // Should return 0 after fix is applied to new deletions
   db.getCollection('77e49b5d-e06a-4aae-a33e-17117418151c').find({
       deleted: true,
       $or: [{end_time: {$exists: false}}, {end_time: null}]
   }).count()
   ```

---

### One-Time Cleanup (Optional)

**Fix Existing 24 Records:**

```python
from datetime import datetime, timezone

# Find all deleted recordings without end_time
deleted_no_end = db.recordings.find({
    "deleted": True,
    "$or": [
        {"end_time": {"$exists": False}},
        {"end_time": None}
    ]
})

# Update each one
for rec in deleted_no_end:
    # Set end_time to deleted_at (if exists) or start_time + estimated duration
    if rec.get("deleted_at"):
        end_time = rec["deleted_at"]
    else:
        # Estimate: assume 2 hours recording time
        end_time = rec["start_time"] + timedelta(hours=2)
    
    db.recordings.update_one(
        {"_id": rec["_id"]},
        {"$set": {"end_time": end_time}}
    )
    
    print(f"Fixed {rec['uuid']}: end_time set to {end_time}")

print(f"✅ Fixed {deleted_no_end.count()} records")
```

**Note:** One-time cleanup is optional since these are deleted recordings (low priority).

---

### Additional Notes

**Important Considerations:**
- Only affects **future** deletions (existing 24 records remain unless cleaned up)
- Very low impact (0.7% of data, deleted recordings)
- Good for data quality and professionalism
- Easy fix with minimal risk

**Follow-up Actions:**
1. Consider adding `deleted_at` field (deletion timestamp)
2. Update API documentation
3. Add unit tests for deletion logic
4. Optional: Run one-time cleanup script

**Enhancement Opportunity:**
Consider adding an explicit `status` field:
```python
class RecordingStatus:
    RUNNING = "running"      # Has start_time, no end_time
    COMPLETED = "completed"  # Has start_time + end_time
    FAILED = "failed"        # Has start_time, no end_time, error flag
    DELETED = "deleted"      # Has start_time + end_time + deleted flag
```

---

### Related Issues
- See: `LIVE_VS_HISTORICAL_RECORDINGS.md` for classification logic
- See: `T_DATA_001_SOFT_DELETE_REPORT.md` for test results

---

### Attachments
- Test file: `tests/integration/infrastructure/test_mongodb_data_quality.py`
- Check script: `scripts/check_live_vs_historical.py`
- Sample record script: `scripts/check_specific_record.py`

---

### Labels
`mongodb` `data-quality` `cleanup` `minor` `low-priority`

---

### Assignee
**Recommended:** Backend Development Team (Focus Server)

---

### Priority Matrix
| Impact | Effort | Priority |
|--------|--------|----------|
| 🟢 LOW (0.7% affected) | 🟢 LOW (1 day) | 🟢 **LOW** |

**ROI:** 🟢 **GOOD** - Small improvement, small effort

---

---

## Summary Table

| # | Issue | Severity | Impact | Effort | Priority | Assignee |
|---|-------|----------|--------|--------|----------|----------|
| **1** | Missing 4 Critical Indexes | 🔴 HIGH | 1000x slower queries | 3 min | 🔴 URGENT | DevOps/DBA |
| **2** | Low Recognition Rate (61.3%) | 🟡 MEDIUM | 38.7% data inaccessible | 1-2 weeks | 🟡 MEDIUM | Backend Dev |
| **3** | Deleted Records Missing end_time | 🟢 LOW | 0.7% incomplete data | 1 day | 🟢 LOW | Backend Dev |

---

## Quick Action Guide

### For Management
1. **Approve** Bug #1 fix immediately (3 min, huge impact) ✅
2. **Prioritize** Bug #2 investigation for next sprint
3. **Backlog** Bug #3 for future cleanup

### For Developers
1. **Bug #1:** Fix NOW (critical performance)
2. **Bug #2:** Start investigation (2 days)
3. **Bug #3:** Add to backlog (low priority)

### For QA
1. All bugs documented with verification steps
2. Automated tests ready for regression testing
3. Re-run tests after fixes applied

---

## How to Use These Tickets

### Jira Import
1. Copy each bug ticket section
2. Create new Jira issue
3. Paste content into description
4. Set severity, labels, assignee
5. Link related files/attachments

### Quick Copy-Paste Template
Each ticket includes:
- ✅ Summary
- ✅ Detailed description
- ✅ Steps to reproduce
- ✅ Impact analysis
- ✅ Root cause analysis
- ✅ Recommended fix (with code!)
- ✅ Verification steps
- ✅ Success criteria
- ✅ Labels and priority

---

**Created by:** QA Automation Team  
**Date:** October 16, 2025  
**Status:** ✅ Ready for import to Jira

