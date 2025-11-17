# ✅ Xray Mapping - Complete!

**Date:** October 27, 2025  
**Status:** ✅ **MARKERS ADDED** - Ready to Upload

---

## 🎯 What Was Done

Added Xray markers (`@pytest.mark.xray`) to the 3 bug tests:

---

## ✅ Tests Mapped

### 1. PZ-13984 - Future Timestamp Validation

**File:** `tests/integration/api/test_prelaunch_validations.py`  
**Line:** 347  
**Test:** `test_time_range_validation_future_timestamps`

```python
@pytest.mark.xray("PZ-13984")
def test_time_range_validation_future_timestamps(
    self,
    focus_server_api: FocusServerAPI
):
    """
    Test: Time Range Validation - Future Timestamps
    
    PZ-13984: Future Timestamp Validation Gap
    
    Validates rejection of future timestamps in historic mode.
    Found bug: Backend accepts future timestamps (tomorrow/week ahead).
    """
```

---

### 2. PZ-13985 - LiveMetadata Missing Required Fields

**File:** `tests/conftest.py`  
**Line:** 641  
**Fixture:** `live_metadata`

```python
@pytest.fixture(scope="session")
@pytest.mark.xray("PZ-13985")  # LiveMetadata Missing Required Fields
def live_metadata(focus_server_api):
    """
    PZ-13985: LiveMetadata Missing Required Fields
    
    This fixture tests GET /metadata endpoint and may fail if backend
    doesn't return required fields (num_samples_per_trace, dtype).
    """
    return focus_server_api.get_live_metadata_flat()
```

---

### 3. PZ-13986 - 200 Jobs Capacity Issue

**File:** `tests/load/test_job_capacity_limits.py`  
**Line:** 784 + 799  
**Test:** `test_200_concurrent_jobs_target_capacity`

```python
@pytest.mark.load
@pytest.mark.capacity
@pytest.mark.critical
@pytest.mark.xray("PZ-13986")
class Test200ConcurrentJobsCapacity:
    """
    PZ-13986: 200 Jobs Capacity Issue (Infrastructure Gap)
    
    Found bug: System handles only 40/200 concurrent jobs (20% success rate).
    """
    
    @pytest.mark.xray("PZ-13986")
    def test_200_concurrent_jobs_target_capacity(
        self, 
        focus_server_api, 
        lightweight_config_payload,
        config_manager
    ):
        """
        PZ-13986: 200 Jobs Capacity Issue
        
        Found bug: Only 40/200 jobs succeed (80% failure rate).
        This is an infrastructure capacity gap requiring DevOps attention.
        """
```

---

## 🚀 Next Steps

### 1. Run Tests to Generate Xray JSON

```bash
# Run with Xray markers
pytest tests/ --xray -v

# This will generate:
# - reports/xray-exec.json
# - reports/junit.xml
```

### 2. Upload to Xray Cloud

```bash
# Set credentials
export XRAY_CLIENT_ID="..."
export XRAY_CLIENT_SECRET="..."

# Upload
python scripts/xray_upload.py
```

### 3. View Results in Jira

Go to Xray → Test Execution → See the 3 tests with results!

---

## 📊 Summary

| JIRA | Test Location | Type | Status |
|------|---------------|------|--------|
| PZ-13984 | `test_prelaunch_validations.py:347` | Test method | ✅ Mapped |
| PZ-13985 | `conftest.py:641` | Fixture | ✅ Mapped |
| PZ-13986 | `test_job_capacity_limits.py:799` | Test method | ✅ Mapped |

---

## ✅ All Done!

**Files Modified:**
1. ✅ `tests/integration/api/test_prelaunch_validations.py`
2. ✅ `tests/conftest.py`
3. ✅ `tests/load/test_job_capacity_limits.py`

**Ready to:**
- ✅ Run tests: `pytest tests/ --xray`
- ✅ Upload to Xray: `python scripts/xray_upload.py`
- ✅ View results in Jira!

---

**Next:** Run the tests! 🚀

