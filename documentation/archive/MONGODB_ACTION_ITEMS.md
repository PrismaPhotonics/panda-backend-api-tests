# MongoDB Data Quality - Action Items

**Date Created:** October 16, 2025  
**Priority Order:** HIGH → MEDIUM → LOW  
**Status:** Ready for Assignment

---

## 🎯 Action Items Summary

| ID | Action | Owner | Priority | Effort | Status |
|-----|--------|-------|----------|--------|--------|
| **AI-1** | Create 4 Missing Indexes | DevOps/DBA | 🔴 HIGH | 3 min | ⏳ Pending |
| **AI-2** | Investigate Low Recognition Rate | Backend Dev | 🟡 MEDIUM | 2 days | ⏳ Pending |
| **AI-3** | Improve Recognition Algorithm | Backend Dev | 🟡 MEDIUM | 1 week | ⏳ Pending |
| **AI-4** | Fix Deletion Logic | Backend Dev | 🟢 LOW | 1 day | ⏳ Pending |
| **AI-5** | Add Monitoring for Indexes | DevOps | 🟡 MEDIUM | 4 hours | ⏳ Pending |
| **AI-6** | Add Monitoring for Recognition Rate | DevOps | 🟡 MEDIUM | 2 hours | ⏳ Pending |

---

## 🔴 HIGH Priority

### AI-1: Create 4 Missing Database Indexes

**Issue:** Missing critical indexes causing 1000x performance degradation

**Owner:** DevOps / DBA  
**Estimated Effort:** 3 minutes  
**Risk Level:** Low

#### Task Description
Create 4 indexes on the recording collection (GUID-based name):
1. `start_time` (ascending)
2. `end_time` (ascending)
3. `uuid` (ascending, **UNIQUE**)
4. `deleted` (ascending)

#### Acceptance Criteria
- [ ] Index on `start_time` exists
- [ ] Index on `end_time` exists
- [ ] Index on `uuid` exists **and is marked as UNIQUE**
- [ ] Index on `deleted` exists
- [ ] Test `test_mongodb_indexes_exist_and_optimal` **PASSES**
- [ ] Time range queries complete in <100ms (verified manually)

#### How to Verify
```bash
# Run automated test
py -m pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_mongodb_indexes_exist_and_optimal -v

# Expected result: PASSED ✅
```

#### Expected Performance Improvement
- Time range queries: 30-60s → <100ms (↓ 99.8%)
- UUID lookups: 5-10s → <10ms (↓ 99.9%)
- Delete filtering: Slow → Fast (↓ 99%)

#### Notes
- Indexes will be created in **background** (non-blocking)
- Total creation time: ~2-3 minutes
- System remains operational during creation
- See `MONGODB_BUGS_REPORT.md` Bug #1 for technical details

#### Jira Ticket
- **Title:** [BUG] MongoDB Recording Collection Missing Critical Indexes
- **Component:** MongoDB, Performance
- **Labels:** `mongodb`, `performance`, `data-quality`, `quick-win`

---

## 🟡 MEDIUM Priority

### AI-2: Investigate Low Recognition Rate

**Issue:** 38.7% of recordings are unrecognized

**Owner:** Backend Developer (Focus Server team)  
**Estimated Effort:** 2 days investigation  
**Risk Level:** Low (investigation only)

#### Task Description
Investigate why 2,173 out of 5,612 recordings (38.7%) are classified as "unrecognized" and stored in a separate collection.

#### Investigation Steps
1. [ ] Sample 20-30 unrecognized recordings
2. [ ] Identify common patterns:
   - File formats
   - Naming conventions
   - Metadata structure
   - Source systems
3. [ ] Review recognition algorithm code
4. [ ] Identify gaps or bugs in current logic
5. [ ] Document findings in technical report

#### Acceptance Criteria
- [ ] Root cause(s) identified
- [ ] Technical report documenting findings
- [ ] Recommendations for improvement
- [ ] Estimated effort for fix

#### How to Verify
```bash
# Check current recognition rate
py scripts/quick_mongo_explore.py

# Look for:
# - Total in main collection: ~3,439
# - Total in unrecognized_recordings: ~2,173
# - Calculate rate: (3439 / (3439 + 2173)) * 100 = 61.3%
```

#### Expected Outcome
- Clear understanding of why recordings fail recognition
- Action plan for improving algorithm
- Go/no-go decision for AI-3

#### Notes
- Current rate: 61.3% (LOW ❌)
- Target rate: >80% (GOOD ✅)
- See `MONGODB_BUGS_REPORT.md` Bug #3 for details

#### Jira Ticket
- **Title:** [INVESTIGATION] Why 38.7% of Recordings Are Unrecognized
- **Component:** Focus Server, Data Processing
- **Labels:** `mongodb`, `data-quality`, `recordings`, `investigation`

---

### AI-3: Improve Recording Recognition Algorithm

**Issue:** Recognition rate too low (61.3%)

**Owner:** Backend Developer (Focus Server team)  
**Estimated Effort:** 1 week (after AI-2 completes)  
**Risk Level:** Medium

**Depends On:** AI-2 (investigation must complete first)

#### Task Description
Based on findings from AI-2, update the recognition algorithm to improve the recognition rate from 61.3% to >80%.

#### Implementation Steps
1. [ ] Update recognition logic based on AI-2 findings
2. [ ] Add support for missing file formats/patterns
3. [ ] Improve error handling
4. [ ] Add logging for failed recognitions
5. [ ] Test with historical unrecognized recordings
6. [ ] Deploy to staging
7. [ ] Monitor recognition rate

#### Acceptance Criteria
- [ ] Recognition rate >80% for new recordings
- [ ] Previously unrecognized recordings can be re-processed
- [ ] Test `test_required_collections_exist` shows >80% rate
- [ ] No regression (recognized recordings stay recognized)
- [ ] Logging added for debugging

#### How to Verify
```bash
# Check recognition rate after fix
py -m pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_required_collections_exist -v

# Should show:
# Recognition rate: >80.0% ✅
```

#### Expected Outcome
- Recognition rate increases from 61.3% → >80%
- 1,000-1,500 more recordings accessible to users
- Reduced unrecognized_recordings backlog

#### Notes
- May require schema changes
- Test thoroughly before production
- Consider batch re-processing of old unrecognized recordings

#### Jira Ticket
- **Title:** [FEATURE] Improve Recording Recognition Algorithm
- **Component:** Focus Server, Data Processing
- **Labels:** `mongodb`, `data-quality`, `recordings`, `enhancement`

---

### AI-5: Add Monitoring for Database Indexes

**Issue:** No alerting if indexes are accidentally dropped

**Owner:** DevOps / SRE  
**Estimated Effort:** 4 hours  
**Risk Level:** Low

#### Task Description
Implement monitoring and alerting to detect if critical indexes are missing from MongoDB.

#### Implementation Steps
1. [ ] Create monitoring script/check
2. [ ] Verify all 4 required indexes exist
3. [ ] Alert if any index is missing
4. [ ] Run check daily (or on deployment)
5. [ ] Integrate with alerting system (Prometheus/Grafana/etc)

#### Acceptance Criteria
- [ ] Automated check runs daily
- [ ] Alert triggered if index missing
- [ ] Alert includes which index(es) missing
- [ ] Documentation for fixing alerts

#### Monitoring Script Example
```bash
# Can use existing test
py -m pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_mongodb_indexes_exist_and_optimal -v

# Or create lightweight check
py scripts/check_mongodb_indexes.py  # (new script to create)
```

#### Expected Outcome
- Proactive detection of index issues
- Prevent performance degradation
- Faster incident response

#### Jira Ticket
- **Title:** [MONITORING] Add Alerts for Missing MongoDB Indexes
- **Component:** DevOps, Monitoring
- **Labels:** `mongodb`, `monitoring`, `devops`, `prevention`

---

### AI-6: Add Monitoring for Recognition Rate

**Issue:** No visibility into recognition rate trends

**Owner:** DevOps / SRE  
**Estimated Effort:** 2 hours  
**Risk Level:** Low

#### Task Description
Implement monitoring to track recording recognition rate over time.

#### Implementation Steps
1. [ ] Add metric: `recording_recognition_rate`
2. [ ] Calculate daily: (recognized / total) * 100
3. [ ] Alert if rate drops below 75%
4. [ ] Create dashboard showing trend

#### Acceptance Criteria
- [ ] Metric collected daily
- [ ] Dashboard shows recognition rate trend
- [ ] Alert triggers at <75%
- [ ] Alert includes example unrecognized recordings

#### Expected Outcome
- Visibility into data quality
- Early detection of regression
- Trend analysis

#### Jira Ticket
- **Title:** [MONITORING] Track Recording Recognition Rate
- **Component:** DevOps, Monitoring
- **Labels:** `mongodb`, `data-quality`, `monitoring`, `metrics`

---

## 🟢 LOW Priority

### AI-4: Fix Deletion Logic to Set end_time

**Issue:** 24 deleted recordings missing `end_time`

**Owner:** Backend Developer (Focus Server team)  
**Estimated Effort:** 1 day  
**Risk Level:** Low

#### Task Description
Update the recording deletion logic to always set `end_time` when marking a recording as deleted.

#### Implementation Steps
1. [ ] Find deletion code (likely in recording service)
2. [ ] Update to set `end_time` on deletion:
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
3. [ ] Add unit tests
4. [ ] Test in staging
5. [ ] Deploy to production

#### Acceptance Criteria
- [ ] All newly deleted recordings have `end_time`
- [ ] Test `test_recordings_have_all_required_metadata` shows 0 deleted without end_time
- [ ] Duration can be calculated for all recordings
- [ ] No regression (existing behavior maintained)

#### How to Verify
```bash
# Run test
py -m pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_recordings_have_all_required_metadata -v

# Should show:
# Deleted recordings without end_time: 0 ✅
```

#### Optional Enhancement
Consider adding an explicit `status` field:
```python
class RecordingStatus:
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"
```

#### Expected Outcome
- Complete metadata for all recordings
- Better analytics accuracy
- Future-proof data model

#### Notes
- Only affects new deletions (old 24 records remain)
- Consider one-time cleanup script for existing 24 records

#### Jira Ticket
- **Title:** [MINOR] Set end_time When Deleting Recordings
- **Component:** Focus Server, Recording Service
- **Labels:** `mongodb`, `data-quality`, `cleanup`, `minor`

---

## 📊 Progress Tracking

### Week 1
- [ ] AI-1: Create indexes (3 min) ← **Quick Win!**
- [ ] AI-2: Investigation starts (2 days)

### Week 2
- [ ] AI-2: Investigation completes
- [ ] AI-3: Implementation starts (1 week)
- [ ] AI-5: Monitoring for indexes (4 hours)

### Week 3
- [ ] AI-3: Implementation continues
- [ ] AI-6: Monitoring for recognition rate (2 hours)

### Week 4
- [ ] AI-3: Testing and deployment
- [ ] AI-4: Fix deletion logic (1 day)

---

## ✅ Verification Checklist

After all fixes:

### Performance
- [ ] Time range queries: <100ms
- [ ] UUID lookups: <10ms
- [ ] History playback: Fast and responsive

### Data Quality
- [ ] Recognition rate: >80%
- [ ] Deleted recordings: All have end_time
- [ ] All indexes present

### Monitoring
- [ ] Index monitoring active
- [ ] Recognition rate tracking active
- [ ] Alerts configured

### Tests
- [ ] All MongoDB tests PASS
- [ ] No regressions detected
- [ ] Performance benchmarks met

---

## 📞 Escalation

**If blocked or questions:**
1. **Technical questions:** Review `MONGODB_BUGS_REPORT.md`
2. **Priority questions:** Review `EXECUTIVE_SUMMARY_MONGODB_ISSUES.md`
3. **QA verification:** Contact Roy Avrahami (QA Lead)
4. **Implementation help:** Check existing test code for examples

---

**Last Updated:** October 16, 2025  
**Next Review:** After AI-1 completion  
**Status:** ✅ Ready for assignment

