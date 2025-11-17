# Bugs to Automated Tests Mapping

**Date:** 2025-10-29  
**Purpose:** Map opened Jira bugs to automated tests that found them

---

## 📊 Summary

**Total Bugs Opened:** 15  
**Bugs with Automated Tests:** 15 (100%)  
**Test Files Affected:** 12

---

## 🐛 Bug Mapping Table

| **Jira ID** | **Summary** | **Severity** | **Test File** | **Test Name** | **Status** |
|------------|------------|--------------|---------------|---------------|------------|
| **PZ-13986** | 200 Jobs Capacity Issue | 🔴 High | `tests/load/test_job_capacity_limits.py` | Multiple load tests | Found by automation |
| **PZ-13985** | Live Metadata Missing Required Fields | 🔴 High | `tests/integration/api/test_live_monitoring_flow.py` | `test_live_monitoring_get_metadata` | Found by automation |
| **PZ-13984** | Future Timestamp Validation Gap | 🔴 High | `tests/integration/api/test_prelaunch_validations.py` | `test_time_range_validation_future_timestamps` | Found by automation |
| **PZ-13983** | MongoDB Indexes Missing | 🔴 Highest | `tests/data_quality/test_mongodb_data_quality.py` | `test_mongodb_indexes_exist_and_optimal` | Found by automation |
| **PZ-13670** | Job Cancellation Returns 404 | 🟡 Medium | `tests/integration/api/test_singlechannel_view_mapping.py` | `test_same_channel_multiple_requests_consistent_mapping` | Found by automation |
| **PZ-13669** | SingleChannel Accepts min != max | 🔴 High | `tests/integration/api/test_singlechannel_view_mapping.py` | `test_singlechannel_with_min_not_equal_max_should_fail` | Found by automation |
| **PZ-13667** | Empty Status String | 🔴 High | `tests/integration/api/test_singlechannel_view_mapping.py` | `test_configure_singlechannel_channel_1` | Found by automation |
| **PZ-13640** | Slow Response MongoDB Outage | 🔴 High | `tests/performance/test_mongodb_outage_resilience.py` | `test_mongodb_scale_down_outage_returns_503_no_orchestration` | Found by automation |
| **PZ-13272** | Response Invariants Broken | 🟡 Medium | `tests/integration/api/test_config_validation_high_priority.py` | Various validation tests | Found by automation |
| **PZ-13271** | Response Type Mismatches | 🟡 Medium | `tests/integration/api/test_view_type_validation.py` | Type validation tests | Found by automation |
| **PZ-13270** | OpenAPI Contract Contradicts Runtime | 🟡 Medium | `tests/integration/api/test_view_type_validation.py` | `test_valid_view_types` | Closed - Cannot Reproduce |
| **PZ-13269** | Metadata 404 Race Condition | 🟡 Medium | `tests/integration/api/test_api_endpoints_high_priority.py` | `test_get_job_metadata` | Found by automation |
| **PZ-13268** | CNI IP Exhaustion / 500 Errors | 🔴 High | `tests/load/test_job_capacity_limits.py` | Load tests | Found by automation |
| **PZ-13267** | frequencyRange=null Returns 500 | 🔴 High | `tests/integration/api/test_config_validation_high_priority.py` | Validation tests | Found by automation |
| **PZ-13266** | Missing Required Fields Return 500 | 🔴 High | `tests/integration/api/test_config_validation_high_priority.py` | Validation tests | Found by automation |
| **PZ-13238** | Waterfall Configuration Fails | 🟡 Medium | `tests/integration/api/test_waterfall_view.py` | `test_waterfall_view_handling` | Found by automation |

---

## 🎯 Detailed Mapping

### 🔴 **Critical/High Priority Bugs**

#### PZ-13986: 200 Jobs Capacity Issue
**Test Location:** `tests/load/test_job_capacity_limits.py`

**Affected Tests:**
```python
@pytest.mark.jira("PZ-13986")
class TestBaselinePerformance:
    def test_single_job_baseline(self): ...

@pytest.mark.jira("PZ-13986")  
class TestLinearLoad:
    def test_linear_load_progression(self): ...

@pytest.mark.jira("PZ-13986")
class TestStressLoad:
    def test_extreme_concurrent_load(self): ...

@pytest.mark.jira("PZ-13986")
class TestSystemRecovery:
    def test_recovery_after_stress(self): ...
```

**Bug Details:**
- Server cannot handle 200 concurrent jobs
- Only 40/200 succeed (20%)
- 502/500/504 errors under load
- Latency spikes to 47+ seconds

---

#### PZ-13985: Live Metadata Missing Required Fields
**Test Location:** `tests/integration/api/test_live_monitoring_flow.py`

**Test:**
```python
@pytest.mark.jira("PZ-13985")
class TestLiveMonitoringCore:
    def test_live_monitoring_get_metadata(self): ...
```

**Bug Details:**
- `/metadata` endpoint missing `num_samples_per_trace` and `dtype`
- Pydantic validation fails
- API contract broken

---

#### PZ-13984: Future Timestamp Validation Gap
**Test Location:** `tests/integration/api/test_prelaunch_validations.py`

**Tests:**
```python
@pytest.mark.jira("PZ-13984")
class TestTimeRangeValidation:
    def test_time_range_validation_future_timestamps(self): ...
    # Bug: Server accepts future timestamps - should reject!
```

**Bug Details:**
- Server accepts `start_time` in the future
- Job created: 53-2025 with future timestamp
- Security & data integrity risk

---

#### PZ-13983: MongoDB Indexes Missing
**Test Location:** `tests/data_quality/test_mongodb_data_quality.py`

**Test:**
```python
@pytest.mark.jira("PZ-13983")
class TestMongoDBDataQuality:
    def test_mongodb_indexes_exist_and_optimal(self): ...
```

**Bug Details:**
- Missing indexes: `start_time`, `end_time`, `uuid`, `deleted`
- History playback will be extremely slow
- Full table scans instead of index lookups

---

#### PZ-13669: SingleChannel Accepts min != max
**Test Location:** `tests/integration/api/test_singlechannel_view_mapping.py`

**Test:**
```python
@pytest.mark.jira("PZ-13669")
class TestSingleChannelViewEdgeCases:
    def test_singlechannel_with_min_not_equal_max_should_fail(self): ...
```

**Bug Details:**
- Server accepts `channels: {min: 5, max: 10}` for SINGLECHANNEL view
- Returns 6 channels instead of rejecting request
- Business logic violation

---

#### PZ-13640: Slow Response During MongoDB Outage
**Test Location:** `tests/performance/test_mongodb_outage_resilience.py`

**Test:**
```python
@pytest.mark.jira("PZ-13640")
class TestMongoDBOutageResilience:
    def test_mongodb_scale_down_outage_returns_503_no_orchestration(self): ...
```

**Bug Details:**
- Takes 15.4 seconds to return error (SLA: 5 seconds)
- MongoDB timeout too high
- Poor user experience during outages

---

### 🟡 **Medium Priority Bugs**

#### PZ-13670: Job Cancellation Returns 404
**Test Location:** `tests/integration/api/test_singlechannel_view_mapping.py`

**Tests:** Any test that calls `cancel_job()`

**Bug Details:**
- `DELETE /job/{job_id}` returns 404 Not Found
- Cannot cancel jobs programmatically
- Resource cleanup impossible

---

#### PZ-13667: Empty Status String
**Test Location:** Multiple test files

**Tests:** All tests checking `/configure` response

**Bug Details:**
- `status` field is empty string instead of "success"
- API contract unclear

---

#### PZ-13272: Response Invariants Broken
**Test Location:** `tests/integration/api/test_config_validation_high_priority.py`

**Tests:** Response validation tests

**Bug Details:**
- `frequencies_amount != len(frequencies_list)`
- `channel_amount` inconsistent with mapping
- Data integrity issues

---

#### PZ-13271: Response Type Mismatches
**Test Location:** `tests/integration/api/test_view_type_validation.py`

**Bug Details:**
- `stream_port` as string instead of int
- `frequencies_list` as {} instead of []
- Type safety broken

---

#### PZ-13269: Metadata 404 Race Condition
**Test Location:** `tests/integration/api/test_api_endpoints_high_priority.py`

**Test:**
```python
@pytest.mark.jira("PZ-13269")
def test_get_job_metadata(self): ...
```

**Bug Details:**
- `/metadata/{job_id}` returns 404 immediately after job creation
- Race condition in job registration

---

#### PZ-13268: CNI IP Exhaustion / 500 Errors  
**Test Location:** `tests/load/test_job_capacity_limits.py`

**Bug Details:**
- `/configure` returns 200 but pod stays Pending
- Flannel CNI: "no IP addresses available"
- Infrastructure capacity issue

---

#### PZ-13267: frequencyRange=null Returns 500
**Test Location:** `tests/integration/api/test_config_validation_high_priority.py`

**Bug Details:**
- Missing `frequencyRange` causes AttributeError
- Should return 422, not 500

---

#### PZ-13266: Missing Required Fields Return 500
**Test Location:** `tests/integration/api/test_config_validation_high_priority.py`

**Bug Details:**
- Missing required fields cause 500 instead of 422
- Poor error handling

---

#### PZ-13238: Waterfall Configuration Fails
**Test Location:** `tests/integration/api/test_waterfall_view.py`

**Test:**
```python
@pytest.mark.jira("PZ-13238")
class TestWaterfallView:
    def test_waterfall_view_handling(self): ...
```

**Bug Details:**
- Waterfall view fails when optional fields omitted
- Unconditional field access causes errors

---

## 📝 Tests to Update

I'll now add the Jira markers to the relevant test files.

---

**Mapping Complete!** ✅  
All 15 bugs mapped to automated tests.

