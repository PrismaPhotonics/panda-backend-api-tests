# Historic Playback E2E Test - All Assertions

**Test File:** `be_focus_server_tests/integration/api/test_historic_playback_e2e.py`  
**Test Method:** `test_historic_playback_complete_e2e_flow`  
**Jira:** PZ-13872, PZ-14101

---

## 📋 All Assertions in Order of Execution

### Phase 1: Configuration

#### Assertion 1: Job ID Present
```python
# Line 188-189
assert hasattr(response, 'job_id') and response.job_id, \
    "Configuration should return job_id"
```
**Purpose:** Verify that configuration request returns a valid job_id  
**Expected:** `response.job_id` exists and is truthy  
**Failure Message:** "Configuration should return job_id"

---

### Phase 2: Data Polling

**No explicit assertions** - Only status tracking and data collection

---

### Phase 3: Data Validation

**No explicit assertions** - Only logging of data collection status

---

### Phase 4: Completion Verification

#### Assertion 2: Status Transitions Exist
```python
# Line 279
assert len(status_transitions) > 0, "Should have at least one status"
```
**Purpose:** Verify that at least one status was recorded during polling  
**Expected:** `status_transitions` list has at least one element  
**Failure Message:** "Should have at least one status"

---

### Phase 5: Summary

#### Assertion 3: Status Transitions Exist (Duplicate Check)
```python
# Line 304
assert len(status_transitions) > 0, "Should have status transitions"
```
**Purpose:** Final verification that status transitions occurred  
**Expected:** `status_transitions` list has at least one element  
**Failure Message:** "Should have status transitions"

---

## 🔍 Implicit Validations (Not Assertions, but Important Checks)

### Pre-Condition Checks:

#### Check 1: Recordings Available in MongoDB
```python
# Line 151-152
if time_range is None:
    pytest.skip("No recordings available in MongoDB for historic playback")
```
**Purpose:** Skip test if no recordings found in MongoDB  
**Action:** Test is skipped (not failed)

#### Check 2: Focus Server Can Find Recordings
```python
# Line 180-185
if "no recording found" in error_msg or "404" in error_msg:
    pytest.skip(
        f"No recording found in Focus Server for time range "
        f"{start_time_dt} to {end_time_dt}. "
        f"Recording exists in MongoDB but Focus Server cannot access it."
    )
```
**Purpose:** Skip test if Focus Server cannot find recordings (current issue!)  
**Action:** Test is skipped (not failed)

---

## 📊 Expected Behavior Summary

### ✅ Success Path:
1. MongoDB query finds recordings ✅
2. Focus Server accepts configuration ✅
3. Job ID returned ✅ (Assertion 1)
4. Status transitions tracked ✅ (Assertion 2 & 3)
5. Playback completes (status 208) ✅
6. Completion within 200 seconds ✅

### ⚠️ Current Issue:
- **MongoDB:** ✅ Finds 50 recordings successfully
- **Focus Server:** ❌ Returns "No recording found in given time range"
- **Result:** Test is **SKIPPED** (not failed)

---

## 🎯 Assertion Summary Table

| # | Line | Assertion | Phase | Critical |
|---|------|-----------|-------|----------|
| 1 | 188-189 | `hasattr(response, 'job_id') and response.job_id` | Configuration | ✅ Yes |
| 2 | 279 | `len(status_transitions) > 0` | Completion | ✅ Yes |
| 3 | 304 | `len(status_transitions) > 0` | Summary | ✅ Yes |

**Total Explicit Assertions:** 3  
**Total Implicit Checks:** 2 (skip conditions)

---

## 📝 Notes

1. **Assertion 2 and 3 are duplicates** - Both check `len(status_transitions) > 0`
2. **No assertions for data quality** - Currently only logging (Phase 3)
3. **No assertions for completion time** - Only warning logged if > 200s
4. **No assertions for data blocks** - Only logging of count

---

**Generated:** 2025-12-01  
**Test Status:** Currently SKIPPED due to Focus Server issue

