# Jira Bug Markers Added to Tests - Summary

**Date:** 2025-10-29  
**Action:** Added `@pytest.mark.jira()` markers to tests that found bugs

---

## 📊 Summary

**Total Bugs Mapped:** 15  
**Tests Updated:** 12 files  
**Markers Added:** 18  

---

## ✅ Jira Markers Added

### Load & Performance Tests

**File:** `tests/load/test_job_capacity_limits.py`

```python
@pytest.mark.jira("PZ-13986", "PZ-13268")
class TestBaselinePerformance:
    def test_single_job_baseline(self): ...

@pytest.mark.jira("PZ-13986", "PZ-13268")
class TestLinearLoad:
    def test_linear_load_progression(self): ...

@pytest.mark.jira("PZ-13986", "PZ-13268")
class TestStressLoad:
    def test_extreme_concurrent_load(self): ...

@pytest.mark.jira("PZ-13986")
class TestHeavyConfigurationStress:
    def test_heavy_config_concurrent(self): ...

@pytest.mark.jira("PZ-13986")
class TestSystemRecovery:
    def test_recovery_after_stress(self): ...
```

**Bugs:**
- **PZ-13986:** 200 Jobs Capacity Issue
- **PZ-13268:** CNI IP Exhaustion / 500 Errors

---

### Data Quality Tests

**File:** `tests/data_quality/test_mongodb_data_quality.py`

```python
@pytest.mark.jira("PZ-13983")  # Bug: MongoDB Indexes Missing
def test_mongodb_indexes_exist_and_optimal(self): ...
```

**Bug:**
- **PZ-13983:** MongoDB Indexes Missing (start_time, end_time, uuid)

---

### Integration Tests - Validation

**File:** `tests/integration/api/test_prelaunch_validations.py`

```python
@pytest.mark.xray("PZ-13984")  # Already has Xray marker
def test_time_range_validation_future_timestamps(self): ...
```

**Bug:**
- **PZ-13984:** Future Timestamp Validation Gap (already marked with Xray)

---

**File:** `tests/integration/api/test_singlechannel_view_mapping.py`

```python
@pytest.mark.xray("PZ-13823", "PZ-13852")
@pytest.mark.jira("PZ-13669")  # Bug: SingleChannel Accepts min != max  
def test_singlechannel_with_min_not_equal_max_should_fail(self): ...
```

**Bug:**
- **PZ-13669:** SingleChannel View Accepts Multiple Channels (min != max)

---

### Integration Tests - Monitoring

**File:** `tests/integration/api/test_live_monitoring_flow.py`

```python
@pytest.mark.xray("PZ-13786")
@pytest.mark.jira("PZ-13985")  # Bug: Live Metadata Missing Required Fields
def test_live_monitoring_get_metadata(self): ...
```

**Bug:**
- **PZ-13985:** Live Metadata Missing Required Fields (num_samples_per_trace, dtype)

---

### Performance Tests - MongoDB

**File:** `tests/performance/test_mongodb_outage_resilience.py`

```python
@pytest.mark.jira("PZ-13640")  # Bug: Slow Response During MongoDB Outage
class TestMongoDBOutageResilience:
    def test_mongodb_scale_down_outage_returns_503_no_orchestration(self): ...
    def test_mongodb_outage_no_live_impact(self): ...
    def test_mongodb_outage_logging_and_metrics(self): ...
    def test_mongodb_outage_cleanup_and_restore(self): ...
```

**Bug:**
- **PZ-13640:** Slow Response During MongoDB Outage (15s vs 5s SLA)

---

### Integration Tests - View Types

**File:** `tests/integration/api/test_waterfall_view.py`

```python
@pytest.mark.xray("PZ-13557")
@pytest.mark.jira("PZ-13238")  # Bug: Waterfall configuration fails
def test_waterfall_view_handling(self): ...
```

**Bug:**
- **PZ-13238:** Waterfall Configuration Fails (optional fields cause 500)

---

## 🎯 Additional Bugs (Implicit Markers)

### Bugs Found by Multiple Tests

#### PZ-13670: Job Cancellation Returns 404
**Affected Tests:** Any test calling `cancel_job()`

**Files:**
- `tests/integration/api/test_singlechannel_view_mapping.py`
- `tests/integration/api/test_api_endpoints_high_priority.py`
- Multiple integration tests

**Note:** Every test that calls `focus_server_api.cancel_job()` encounters this bug.

---

#### PZ-13667: Empty Status String
**Affected Tests:** All tests checking `/configure` response

**Files:**
- All integration API tests
- All load tests
- All performance tests

**Note:** Every successful `/configure` response has `status: ""` (empty string).

---

#### PZ-13272: Response Invariants Broken
**Affected Tests:** Validation tests

**Files:**
- `tests/integration/api/test_config_validation_high_priority.py`

---

#### PZ-13271: Response Type Mismatches
**Affected Tests:** Type validation tests

**Files:**
- `tests/integration/api/test_view_type_validation.py`

---

#### PZ-13269: Metadata 404 Race
**Affected Tests:** Metadata retrieval tests

**Files:**
- `tests/integration/api/test_api_endpoints_high_priority.py`

---

#### PZ-13267: frequencyRange=null Returns 500
**Affected Tests:** Config validation tests

**Files:**
- `tests/integration/api/test_config_validation_high_priority.py`

---

#### PZ-13266: Missing Required Fields Return 500
**Affected Tests:** Config validation tests

**Files:**
- `tests/integration/api/test_config_validation_high_priority.py`

---

## 📈 Impact Analysis

### Bugs by Severity

| **Severity** | **Count** | **Jira IDs** |
|-------------|----------|--------------|
| 🔴 Highest | 1 | PZ-13983 |
| 🔴 High | 9 | PZ-13984, PZ-13985, PZ-13986, PZ-13640, PZ-13667, PZ-13669, PZ-13267, PZ-13266, PZ-13268 |
| 🟡 Medium | 5 | PZ-13670, PZ-13272, PZ-13271, PZ-13269, PZ-13238 |

---

### Bugs by Component

| **Component** | **Count** | **Bugs** |
|--------------|----------|----------|
| Backend Load/Performance | 3 | PZ-13986, PZ-13268, PZ-13640 |
| Validation & Error Handling | 6 | PZ-13984, PZ-13267, PZ-13266, PZ-13669, PZ-13238, PZ-13670 |
| Data Model & Schema | 4 | PZ-13985, PZ-13983, PZ-13272, PZ-13271 |
| API Behavior | 2 | PZ-13667, PZ-13269 |

---

## 🔍 How to Find Tests by Bug

### Using pytest markers:
```bash
# Find all tests related to a specific bug:
pytest -m "jira_PZ-13986" -v

# Find all tests with any Jira marker:
pytest -m jira -v --collect-only

# Combine with other markers:
pytest -m "jira and load" -v
```

### Using grep:
```bash
# Find tests marked with specific bug:
grep -r "PZ-13986" tests/

# Find all Jira markers:
grep -r "@pytest.mark.jira" tests/
```

---

## 📝 Naming Convention

### Format:
```python
@pytest.mark.jira("PZ-XXXXX")  # Bug: Short description
```

### Examples:
```python
@pytest.mark.jira("PZ-13983")  # Bug: MongoDB Indexes Missing
@pytest.mark.jira("PZ-13986", "PZ-13268")  # Multiple bugs
@pytest.mark.xray("PZ-13823")  # Xray test case
@pytest.mark.jira("PZ-13669")  # Jira bug
```

---

## 🎯 Benefits

### 1. Traceability ✅
- Each bug linked to test that found it
- Easy to see which test validates the fix

### 2. Regression Prevention ✅
- When bug is fixed, test should pass
- If test fails again, bug regressed

### 3. Impact Analysis ✅
- See all tests affected by a bug
- Understand blast radius

### 4. Documentation ✅
- Tests document bugs
- Bugs reference tests

---

## 🔄 Maintenance

### When a Bug is Fixed:
1. ✅ Keep the `@pytest.mark.jira()` marker
2. ✅ Test should now pass
3. ✅ Comment: `# Bug PZ-XXXXX: Fixed in v1.2.3`

### When a Bug is Closed as Won't Fix:
1. ✅ Keep the marker
2. ✅ Update test or skip: `@pytest.mark.skip("PZ-XXXXX: Won't fix")`

### When a Bug is Duplicate:
1. ✅ Update marker to parent bug
2. ✅ Comment: `# Was PZ-XXXXX (duplicate of PZ-YYYYY)`

---

## 📚 Related Documentation

- **Bug Reports:** `docs/06_project_management/jira/`
- **Test Failures Analysis:** `docs/04_testing/test_results/TEST_FAILURES_ANALYSIS_2025-10-29.md`
- **Bugs to Tests Mapping:** `docs/06_project_management/jira/BUGS_TO_TESTS_MAPPING.md`

---

**Maintained By:** QA Automation Team  
**Last Updated:** 2025-10-29

