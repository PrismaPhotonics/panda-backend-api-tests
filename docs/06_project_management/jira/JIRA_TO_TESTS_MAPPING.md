# 🔗 JIRA Bug Tickets → Automation Tests Mapping

**תאריך:** 27 אוקטובר 2025  
**סטטוס:** ✅ **Mapping Complete**  
**מטרה:** קישור בין JIRA bugs לטסטים באוטומציה שמצאו אותם

---

## 📋 Overview

מסמך זה מקשר את 4 הבאגים שנמצאו לרגעים:

1. **PZ-13983** → MongoDB Indexes Missing
2. **PZ-13984** → Future Timestamp Validation Gap
3. **PZ-13985** → LiveMetadata Missing Required Fields
4. **PZ-13986** → 200 Jobs Capacity Issue

---

## 🗺️ Complete Mapping

### Bug #1: PZ-13983 - MongoDB Indexes Missing

**JIRA Ticket:** PZ-13983  
**Priority:** Critical  
**Status:** Open  

#### Test That Found The Bug:

**File:** `tests/data_quality/test_mongodb_data_quality.py`  
**Test Class:** `TestMongoDBDataQuality`  
**Test Method:** `test_recording_collection_indexes_present()`

#### Test Details:

```python
# tests/data_quality/test_mongodb_data_quality.py
class TestMongoDBDataQuality(InfrastructureTest):
    """
    MongoDB Data Quality Tests.
    
    Line: 31-1200
    """
    
    def test_recording_collection_indexes_present(self):
        """
        Test that validates MongoDB indexes are present.
        
        Found missing indexes:
        - start_time ❌
        - end_time ❌  
        - uuid ❌
        - deleted ❌
        """
```

#### How to Run Verification Test:

```bash
# Run the specific test that found the bug
pytest tests/data_quality/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_recording_collection_indexes_present -v -s

# Or run all MongoDB data quality tests
pytest tests/data_quality/test_mongodb_data_quality.py -v

# Expected output BEFORE fix:
# ERROR: ❌ Index on 'start_time' is MISSING
# ERROR: ❌ Index on 'end_time' is MISSING
# ERROR: ❌ Index on 'uuid' is MISSING
# ERROR: ❌ Index on 'deleted' is MISSING

# Expected output AFTER fix:
# ✅ All required indexes are present
```

#### After Fix Verification:

```bash
# 1. Run test to verify indexes are created
pytest tests/data_quality/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_recording_collection_indexes_present -v -s

# 2. Should pass with: ✅ All indexes present
```

---

### Bug #2: PZ-13984 - Future Timestamp Validation Gap

**JIRA Ticket:** PZ-13984  
**Priority:** High  
**Status:** Open  

#### Test That Found The Bug:

**File:** `tests/integration/api/test_prelaunch_validations.py`  
**Test Class:** `TestTimeRangeValidation`  
**Test Method:** `test_time_range_validation_future_timestamps()`

#### Test Details:

```python
# tests/integration/api/test_prelaunch_validations.py
class TestTimeRangeValidation:
    """
    Test Suite: Time Range Validation
    Line: 338-420
    """
    
    def test_time_range_validation_future_timestamps(self, focus_server_api: FocusServerAPI):
        """
        Test: Time Range Validation - Future Timestamps
        
        Line: 347-419
        
        Validates rejection of future timestamps in historic mode.
        
        Found: Job created with future timestamps (41-54)
        Expected: Should REJECT future timestamps
        """
```

#### How to Run Verification Test:

```bash
# Run the specific test that found the bug
pytest tests/integration/api/test_prelaunch_validations.py::TestTimeRangeValidation::test_time_range_validation_future_timestamps -v -s

# Or run all time range validation tests
pytest tests/integration/api/test_prelaunch_validations.py::TestTimeRangeValidation -v

# Expected output BEFORE fix:
# ERROR: ❌ Job created with future timestamps (41-54)
# ERROR:    This is a validation gap - future timestamps should be rejected!

# Expected output AFTER fix:
# ✅ Future timestamps rejected with error: start_time cannot be in the future
```

#### After Fix Verification:

```bash
# 1. Run test to verify backend rejects future timestamps
pytest tests/integration/api/test_prelaunch_validations.py::TestTimeRangeValidation::test_time_range_validation_future_timestamps -v -s

# 2. Should pass with: ✅ Future Timestamps Rejected
# 3. Check error message quality
```

---

### Bug #3: PZ-13985 - LiveMetadata Missing Required Fields

**JIRA Ticket:** PZ-13985  
**Priority:** High  
**Status:** Open  

#### Tests That Found The Bug:

**File 1:** `tests/integration/api/test_api_endpoints_high_priority.py`  
**Test Method:** `test_get_live_metadata()`

**File 2:** `tests/integration/api/test_api_endpoints_high_priority.py`  
**Test Method:** `test_get_live_metadata_consistency()`

#### Test Details:

```python
# tests/integration/api/test_api_endpoints_high_priority.py
# Line: Various (test methods scattered throughout file)

def test_get_live_metadata(focus_server_api):
    """
    Test that validates GET /metadata endpoint.
    
    Found missing fields:
    - num_samples_per_trace ❌
    - dtype ❌
    
    Error:
    ERROR: 2 validation errors for LiveMetadataFlat
    num_samples_per_trace
      Field required [type=missing, ...]
    dtype
      Field required [type=missing, ...]
    """
```

#### How to Run Verification Test:

```bash
# Run all tests that check LiveMetadata
pytest tests/integration/api/test_api_endpoints_high_priority.py -v -k "live_metadata" -s

# Or run specific test file
pytest tests/integration/api/test_api_endpoints_high_priority.py -v

# Expected output BEFORE fix:
# ERROR: 2 validation errors for LiveMetadataFlat
# ERROR: num_samples_per_trace - Field required
# ERROR: dtype - Field required

# Expected output AFTER fix:
# ✅ LiveMetadata response includes all required fields
# ✅ num_samples_per_trace: 1024
# ✅ dtype: float32
```

#### After Fix Verification:

```bash
# 1. Run test to verify metadata includes all fields
pytest tests/integration/api/test_api_endpoints_high_priority.py -v -k "live_metadata" -s

# 2. Should pass with all fields present
# 3. Verify response structure
```

---

### Bug #4: PZ-13986 - 200 Jobs Capacity Issue

**JIRA Ticket:** PZ-13986  
**Priority:** High (Major Infrastructure)  
**Status:** Open  

#### Test That Found The Bug:

**File:** `tests/load/test_job_capacity_limits.py`  
**Test Class:** Various test classes for different load levels  
**Target Test:** `test_target_capacity_200_concurrent_jobs()`

#### Test Details:

```python
# tests/load/test_job_capacity_limits.py
# Line: 40-1200

# Test Configuration Constants
TARGET_CAPACITY_JOBS = 200  # יעד קיבולת - דרישה מפגישה (PZ-13756)

class TestTargetCapacity:
    """
    Job Capacity Limits Tests.
    
    Test that validates system can handle 200 concurrent jobs.
    
    Found:
    - Target: 200 concurrent jobs
    - Achieved: 40 jobs (20% success)
    - Gap: 160 jobs (80% failure)
    
    Status: ⚠️ System cannot handle 200 jobs
    """
    
    def test_target_capacity_200_concurrent_jobs(self):
        """
        Test that validates 200 concurrent jobs capacity.
        
        This is the EXPECTED finding - the test is designed to discover capacity gaps!
        """
```

#### How to Run Verification Test:

```bash
# Run the target capacity test
pytest tests/load/test_job_capacity_limits.py -v -k "200" -s

# Or run all capacity tests
pytest tests/load/test_job_capacity_limits.py -v -s

# Expected output BEFORE fix (this is expected!):
# ⚠️ System capacity test FAILED
# Target: 200 jobs
# Achieved: 40 jobs (20%)
# Infrastructure Gap Report: Generated!

# Expected output AFTER infrastructure scaling:
# ✅ System capacity test PASSED
# Target: 200 jobs
# Achieved: 195 jobs (97.5% success)
```

#### Infrastructure Gap Report:

When the test fails, it automatically generates:

```json
{
    "test_name": "test_target_capacity_200_concurrent_jobs",
    "target_load": 200,
    "actual_load": 40,
    "success_rate": "20%",
    "bottlenecks": [
        "Kubernetes CPU limited",
        "Memory pressure",
        "Database connections exhausted",
        "RabbitMQ queue full"
    ],
    "recommendations": [
        "Scale up K8s nodes",
        "Increase database connection pool",
        "Add RabbitMQ consumers",
        "Optimize resource allocation"
    ]
}
```

#### After Infrastructure Fix Verification:

```bash
# 1. After DevOps scales infrastructure, run test again
pytest tests/load/test_job_capacity_limits.py -v -k "200" -s

# 2. Should achieve >90% success rate
# 3. Infrastructure Gap Report should show improvements
```

---

## 📊 Summary Table

| JIRA Ticket | Test File | Test Method | Line | Priority | Status |
|-------------|-----------|-------------|------|-----------|--------|
| **PZ-13983** | `tests/data_quality/test_mongodb_data_quality.py` | `test_recording_collection_indexes_present()` | ~300-500 | Critical | Open |
| **PZ-13984** | `tests/integration/api/test_prelaunch_validations.py` | `test_time_range_validation_future_timestamps()` | 347-419 | High | Open |
| **PZ-13985** | `tests/integration/api/test_api_endpoints_high_priority.py` | `test_get_live_metadata()` | Various | High | Open |
| **PZ-13986** | `tests/load/test_job_capacity_limits.py` | `test_target_capacity_200_concurrent_jobs()` | ~800-1100 | High (Major) | Open |

---

## 🎯 Verification Commands Summary

After bugs are fixed, run these commands to verify:

```bash
# 1. MongoDB Indexes (PZ-13983)
pytest tests/data_quality/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_recording_collection_indexes_present -v -s

# 2. Future Timestamp Validation (PZ-13984)
pytest tests/integration/api/test_prelaunch_validations.py::TestTimeRangeValidation::test_time_range_validation_future_timestamps -v -s

# 3. LiveMetadata Fields (PZ-13985)
pytest tests/integration/api/test_api_endpoints_high_priority.py -v -k "live_metadata" -s

# 4. 200 Jobs Capacity (PZ-13986)
pytest tests/load/test_job_capacity_limits.py -v -k "200" -s

# Or run all at once
pytest tests/ -v -k "mongodb_data_quality or time_range_validation or live_metadata or 200" -s
```

---

## 📝 How to Use This Document

### For QA Team:

1. **Before Bug Fix:** Know which test found the bug
2. **After Bug Fix:** Run the specific test to verify fix
3. **Report to Dev:** Share exact test location and commands

### For Backend Team:

1. **Read the Test:** Understand what the test expects
2. **Fix the Bug:** Implement the fix
3. **Verify:** Run the test command to confirm fix works

### For DevOps Team:

1. **Read Bug #4:** Infrastructure scaling requirements
2. **Review Gap Report:** Understand bottlenecks
3. **Scale Infrastructure:** Follow recommendations
4. **Verify:** Run capacity test again

---

## 🔄 Test-Driven Workflow

```
1. Test discovers bug → Reports in logs
2. Bug filed in JIRA (with this mapping)
3. Dev reads test to understand issue
4. Dev fixes bug
5. QA runs specific test to verify
6. Test passes → Bug closed
7. QA updates JIRA with test results
```

---

## 📚 Additional Resources

- **Root Cause Analysis:** `documentation/analysis/TEST_FAILURES_ROOT_CAUSE_ANALYSIS.md`
- **Test Results:** `logs/errors/2025-10-27_15-05-57_all_tests_ERRORS.log`
- **Bug Summary:** `documentation/jira/BUGS_FOUND_BY_AUTOMATION.md`

---

**Document Created By:** QA Automation Framework  
**Date:** October 27, 2025  
**Purpose:** Link JIRA tickets to automation tests that found them

---

## ✅ Checklist for Each Bug Fix

- [ ] Read the JIRA ticket description
- [ ] Locate the test using this mapping
- [ ] Run the test to reproduce the issue
- [ ] Implement the fix
- [ ] Run the test again to verify fix
- [ ] Update JIRA with test results
- [ ] Close the ticket

---

**Ready for use by QA, Backend, and DevOps teams!** 🚀

