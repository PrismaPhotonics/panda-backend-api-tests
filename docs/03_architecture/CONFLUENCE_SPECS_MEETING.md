# Specs Meeting: Missing Test Specifications

**Meeting Type:** Technical Specs Review  
**Duration:** 2-3 hours  
**Required Attendees:** Dev Lead, Site Manager, Product Owner, QA Lead  
**Date:** TBD  
**Status:** **URGENT - Blocking 82+ automated tests**

---

## Meeting Objective

**Goal:** Define missing specifications that are currently blocking test automation quality gates.

**What we need:** Clear pass/fail criteria for automated tests that currently have:
- Hardcoded values without confirmation
- Disabled assertions waiting for specs
- TODO comments blocking test completion
- Undefined behavior for edge cases

**Expected Outcome:** Document agreed-upon values and behaviors that will be implemented in test code within 1-2 weeks.

---

## The Problem

### Current Situation:
- **190+ automated tests** exist in the framework
- **82+ tests** are directly affected by missing specs
- **28 performance tests** have assertions disabled/commented out
- **50+ hardcoded values** were never confirmed with the team

### Impact:
- Tests run but **can't fail** when they should  
- Can't detect **performance degradation**  
- Can't enforce **data quality** rules  
- False positives waste investigation time  
- False negatives miss real bugs  

---

## Top 7 Critical Issues (Prioritized)

---

### **Issue #1: Performance Assertions Disabled**

**Source Code File:** `src/utils/validators.py` (validation logic)

**Test Files Affected:**
- `tests/integration/performance/test_performance_high_priority.py:146-170` (28 performance tests)
- `tests/integration/api/test_api_endpoints_high_priority.py` (API endpoint tests)

**The Problem:**
```python
# TODO: Uncomment after specs meeting
# assert p95 < THRESHOLD_P95_MS   # DISABLED!
# assert p99 < THRESHOLD_P99_MS   # DISABLED!

# For now, just log warning
if p95 >= THRESHOLD_P95_MS:
    logger.warning(f"WARNING: P95 {p95}ms exceeds {THRESHOLD_P95_MS}ms")
```

**Impact:** 
- **28 performance tests** collect metrics but can't fail
- Can't detect performance regressions
- Can't enforce SLAs

**What We Need:**

| Endpoint | Metric | Current Guess | Need Decision |
|----------|--------|---------------|---------------|
| POST /config | P95 latency | 500ms | ? ms |
| POST /config | P99 latency | 1000ms | ? ms |
| POST /config | Error rate | 5% | ? % |
| GET /metadata | P95 latency | - | ? ms |
| GET /channels | Response time | 1000ms | ? ms |

**Questions:**
1. What are acceptable P95/P99 thresholds for each endpoint?
2. What's the maximum error rate before we fail the test?
3. What's the measurement window/sample size?

---

### **Issue #2: ROI Change Limit - Hardcoded 50%**

**Source Code File:** `src/utils/validators.py:390-460` (validation logic)

**Test Files Affected:**
- `tests/unit/test_validators.py` (ROI validation unit tests)
- `tests/integration/api/test_dynamic_roi_adjustment.py` (6 ROI change tests)
- `tests/integration/api/test_config_validation_high_priority.py` (ROI config validation)

**The Problem:**
```python
def validate_roi_change_safety(
    old_roi: ROIConfig,
    new_roi: ROIConfig,
    max_change_percent: float = 50.0  # NEVER CONFIRMED!
):
    """Validates ROI changes aren't too drastic."""
    ...
```

**Impact:**
- **6 ROI validation tests** depend on this unconfirmed value
- Could be blocking legitimate user changes
- Could be allowing dangerous changes
- No one knows if 50% is correct

**What We Need:**
1. Confirm: Is 50% the correct maximum change?
2. Or should it be: 30%? 70%? Different value?
3. Is there a cooldown period between consecutive changes?
4. What happens when exceeded - reject? warn? throttle?

**Current Code Behavior:**
- If ROI change > 50% → Returns validation error
- Used in: sensor range, frequency range, channel range adjustments

---

### **Issue #3: NFFT Validation Too Permissive**

**Source Code File:** `src/utils/validators.py:194-227` (validation logic)

**Test Files Affected:**
- `tests/unit/test_validators.py` (NFFT validation unit tests)
- `tests/unit/test_models_validation.py` (6 NFFT model validation tests)
- `tests/integration/api/test_config_validation_high_priority.py` (NFFT config validation)
- `tests/integration/api/test_spectrogram_pipeline.py` (NFFT in pipeline tests)

**The Problem:**
```python
def validate_nfft_value(nfft: int) -> bool:
    """Validate NFFT value."""
    if not is_power_of_2(nfft):
        warnings.warn(f"NFFT={nfft} not power of 2")  # Only warns!
    return True  # Always passes!
```

**Code vs Config Mismatch:**
- **Config file** (`config/settings.yaml`): Says valid values = [256, 512, 1024, 2048]
- **Validation code**: Accepts ANY positive integer, only warns if not power of 2
- **Tests**: Can't assert behavior because it's undefined

**Impact:**
- **6 NFFT tests** can't enforce rules
- Invalid NFFT values could harm performance/memory
- Inconsistency between config and code

**What We Need:**
1. Should code **enforce** the list in config? (reject invalid values)
2. Or keep **warning-only** behavior? (accept but warn)
3. What's the absolute maximum NFFT? (currently unlimited)
4. Can user override with custom values?

---

### **Issue #4: Frequency Range - No Absolute Limits**

**Source Code File:** `src/models/focus_server_models.py:46-57` (model definition)

**Test Files Affected:**
- `tests/unit/test_validators.py` (frequency validation unit tests)
- `tests/unit/test_models_validation.py` (16 frequency range model tests)
- `tests/integration/api/test_config_validation_high_priority.py` (frequency edge cases)
- `tests/integration/api/test_spectrogram_pipeline.py` (frequency in pipeline)
- `tests/integration/api/test_singlechannel_view_mapping.py` (frequency mapping)
- `tests/integration/api/test_live_monitoring_flow.py` (live frequency tests)

**The Problem:**
```python
class FrequencyRange(BaseModel):
    min_freq: float = Field(gt=0)  # Only: must be > 0
    max_freq: float = Field(gt=0)  # Only: must be > 0
    # No absolute maximum!
    # No minimum span required!
```

**Impact:**
- **16 frequency tests** have no upper bounds
- Could accept extreme values (e.g., 999999999 Hz)
- Can't test realistic ranges

**What We Need:**
1. Absolute maximum frequency? (e.g., 48000 Hz? 96000 Hz?)
2. Absolute minimum frequency? (e.g., 20 Hz?)
3. Minimum span required? (e.g., max - min >= 100 Hz?)
4. Edge case: Is min_freq == max_freq valid? (single frequency)

**Current Test Issues:**
- `test_frequency_range_equal_min_max` - Can't assert if this is valid or error
- `test_frequency_range_extreme_values` - Don't know what's "extreme"

---

### **Issue #5: Sensor Range - No Min/Max ROI Size**

**Source Code File:** `src/utils/validators.py:116-151` (validation logic)

**Test Files Affected:**
- `tests/unit/test_validators.py` (15 sensor validation unit tests)
- `tests/unit/test_models_validation.py` (sensor range model tests)
- `tests/integration/api/test_live_monitoring_flow.py` (sensor range in live mode)
- `tests/integration/api/test_dynamic_roi_adjustment.py` (sensor ROI adjustment)

**The Problem:**
```python
def validate_sensor_range(sensor_range: SensorRange) -> bool:
    # Validates that min <= max
    # But doesn't check if ROI is too small or too large!
    if sensor_range.min_sensor < 1:
        return False
    if sensor_range.max_sensor > 2222:  # Total sensors
        return False
    return True
```

**Current Gaps:**
- Could allow ROI with **just 1 sensor** (min=max=1) - is this valid?
- Could allow ROI with **all 2222 sensors** (min=1, max=2222) - practical?
- No minimum ROI size constraint
- No maximum ROI size constraint

**Impact:**
- **15 sensor validation tests** lack boundaries
- Could allow impractical configurations

**What We Need:**
1. Minimum ROI size? (e.g., at least 10 sensors? 50?)
2. Maximum ROI size? (e.g., at most 500 sensors? 1000?)
3. Is single-sensor ROI valid? (min == max)
4. Practical recommendations for typical use cases?

---

### **Issue #6: API Response Time - Arbitrary Timeout**

**Source Code File:** `src/apis/focus_server_api.py` (API implementation)

**Test Files Affected:**
- `tests/integration/api/test_api_endpoints_high_priority.py:135-147` (3 API timeout tests)
- `tests/integration/performance/test_performance_high_priority.py` (API performance tests)

**The Problem:**
```python
def test_get_channels_endpoint_response_time():
    start = time.time()
    response = client.get("/channels")
    duration = time.time() - start
    
    # Arbitrary 1000ms - no official SLA
    assert duration < 1.0, f"GET /channels took {duration}s"
```

**Impact:**
- **3 API timeout tests** use arbitrary values
- Could be too strict (false failures) or too lenient (miss issues)
- No official SLA documented

**What We Need:**
Response time SLA for each endpoint:

| Endpoint | Current | Need |
|----------|---------|------|
| GET /channels | 1000ms | ? |
| GET /metadata | - | ? |
| POST /config | - | ? |

---

### **Issue #7: Config Validation - No Assertions**

**Source Code File:** `src/utils/validators.py` (validation logic)

**Test Files Affected:**
- `tests/integration/api/test_config_validation_high_priority.py:475-520` (8 edge case tests with TODOs)
- `tests/unit/test_validators.py` (edge case validation unit tests)
- `tests/unit/test_models_validation.py` (edge case model validation tests)

**The Problem:**
```python
def test_frequency_range_equal_min_max():
    """Test behavior when min_freq == max_freq."""
    payload = {
        "frequency_range": {"min_freq": 1000, "max_freq": 1000}
    }
    response = client.post("/config", json=payload)
    
    # TODO: Should this be 200 (valid) or 400 (error)?
    # assert response.status_code == ???  # Can't assert!
```

**Impact:**
- **8 edge case tests** have TODO/no assertions
- Behavior undefined for boundary conditions

**What We Need:**
For these edge cases, define expected behavior:

| Test Case | Current | Need Decision |
|-----------|---------|---------------|
| min_freq == max_freq | Unknown | 200 OK or 400 Error? |
| min_channel == max_channel | Unknown | 200 OK or 400 Error? |
| ROI size = 1 sensor | Unknown | Valid or invalid? |
| NFFT not in config list | Warning | Reject or accept? |

---

## Summary Table

| # | Issue | Tests Blocked | Priority | Code Location |
|---|-------|---------------|----------|---------------|
| 1 | Performance assertions disabled | 28 | Critical | `test_performance_high_priority.py:146` |
| 2 | ROI change limit (50%) | 6 | Critical | `validators.py:395` |
| 3 | NFFT validation permissive | 6 | Critical | `validators.py:194` |
| 4 | Frequency range no limits | 16 | High | `focus_server_models.py:46` |
| 5 | Sensor range no min/max | 15 | High | `validators.py:116` |
| 6 | API response time arbitrary | 3 | Medium | `test_api_endpoints.py:135` |
| 7 | Config edge cases undefined | 8 | Medium | `test_config_validation.py:475` |

**Total: 82+ tests affected**

---

## Meeting Agenda

### Part 1: Context (15 min)
- Review this document
- Show code examples
- Explain impact on test quality

### Part 2: Issue #1-3 - Critical (60 min)
- Performance SLAs
- ROI change limit
- NFFT validation
- **Document decisions**

### Part 3: Issue #4-7 - High/Medium (45 min)
- Frequency/sensor ranges
- API timeouts
- Edge cases
- **Document decisions**

### Part 4: Implementation Plan (20 min)
- Timeline for code updates
- Testing approach
- Documentation requirements

### Part 5: Follow-up (10 min)
- Schedule review meeting
- Assign action items

---

## Desired Outcomes

After this meeting, we should have:

- **Documented decisions** for all 7 issues  
- **Specific numeric values** (thresholds, limits, timeouts)  
- **Defined behaviors** for edge cases  
- **Implementation plan** with timeline  
- **Test updates** scheduled within 1-2 weeks  

---

## Supporting Materials

### Code Files to Review:
1. `src/utils/validators.py` - Validation functions
2. `tests/integration/performance/test_performance_high_priority.py` - Performance tests
3. `tests/integration/api/test_config_validation_high_priority.py` - Config tests
4. `config/settings.yaml` - Configuration file

### Documentation Available:
- Full code evidence: `documentation/specs/CODE_EVIDENCE_MISSING_SPECS.md`
- Critical specs list: `documentation/specs/CRITICAL_MISSING_SPECS_LIST.md`
- 135 questions checklist: `documentation/specs/specs_checklist_for_meeting.csv`

---

## Next Steps (After Meeting)

1. **Document Decisions** - Update specs document with agreed values
2. **Update Code** - Modify validators and test assertions
3. **Enable Assertions** - Uncomment performance test assertions
4. **Run Tests** - Verify all affected tests pass/fail correctly
5. **Update Xray** - Document specs in Jira test cases
6. **Schedule Review** - Follow-up meeting to verify implementation

---

## Questions Before Meeting?

Contact: QA Automation Team

**Preparation:** Please review code examples in Issues #1-3 before the meeting.

---

**Document Version:** 1.0  
**Last Updated:** October 22, 2025  
**Status:** Ready for Meeting

