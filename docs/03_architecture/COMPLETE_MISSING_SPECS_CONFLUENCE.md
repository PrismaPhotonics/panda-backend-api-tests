# Missing Specifications - Complete Report

**Document Type:** Technical Specification Gap Analysis  
**Date:** October 22, 2025  
**Scope:** Backend Testing & Automation Framework  
**Status:** 🔴 **URGENT - Blocking 82+ tests**

---

## Executive Summary

This document catalogs **19 critical specification gaps** affecting the Focus Server automation framework. These gaps prevent proper test validation, allowing bugs to reach production and creating false confidence in test results.

**Impact Overview:**
- **82+ automated tests** cannot properly validate quality
- **50+ hardcoded values** never confirmed by product team
- **28 performance tests** have disabled assertions
- **Multiple critical endpoints** lack defined behavior

**Risk:** Without these specifications, our test suite provides false confidence - tests pass but don't catch real issues.

---

## 🔴 Critical Priority Issues (Immediate Action Required)

---

### 🔴 Issue #1: Performance Assertions Disabled

**Category:** Performance Testing  
**Tests Affected:** 28 tests  
**Code Location:** `tests/integration/performance/test_performance_high_priority.py:146-170`

#### The Problem

Performance tests measure P95/P99 latency and error rates, but **all assertions are disabled**. Tests collect metrics but never fail, even if performance is terrible.

**Current Code Behavior:**
```python
# TODO: Uncomment after specs meeting
# assert p95 < THRESHOLD_P95_MS   # ❌ DISABLED!
# assert p99 < THRESHOLD_P99_MS   # ❌ DISABLED!

# Only logs warning instead of failing
if p95 >= THRESHOLD_P95_MS:
    logger.warning(f"Would fail: P95={p95}ms")
```

#### What's Missing

| Endpoint | Metric | Current Guess | Need Decision |
|----------|--------|---------------|---------------|
| POST /config | P95 latency | 500ms | ? |
| POST /config | P99 latency | 1000ms | ? |
| POST /config | Error rate | 5% | ? |
| GET /metadata | P95 latency | - | ? |
| GET /channels | Response time | 1000ms | ? |

#### Business Impact

- ✅ **Tests run:** Yes
- ❌ **Tests fail on issues:** No
- ❌ **Can detect performance degradation:** No
- ❌ **Can enforce SLAs:** No

**Real Scenario:**
```
Developer adds N+1 query bug:
├─ Before: P95 = 150ms ✅
├─ After: P95 = 1200ms ❌
└─ Test Result: PASS ✅ (assertions disabled!)
   → Bug goes to production
```

#### Questions to Answer

1. What are acceptable P95/P99 latency thresholds for each endpoint?
2. What's the maximum error rate before we should fail?
3. What's the measurement window/sample size?

**Documentation:** See `CONFLUENCE_SPECS_MEETING.md:46-85`

---

### 🔴 Issue #2: ROI Change Limit - Hardcoded 50%

**Category:** Data Validation  
**Tests Affected:** 6 tests  
**Code Location:** `src/utils/validators.py:395`

#### The Problem

Code has hardcoded `max_change_percent = 50.0` that was **never confirmed** by product team. This value determines whether user's ROI change requests are accepted or rejected.

**Current Code:**
```python
def validate_roi_change_safety(
    old_roi: ROIConfig,
    new_roi: ROIConfig,
    max_change_percent: float = 50.0  # ❌ NEVER CONFIRMED!
):
    """Rejects if ROI change > 50%"""
```

#### What's Missing

1. **Confirmation:** Is 50% correct? Or should it be 30%? 70%? Different value?
2. **Cooldown period:** Is there a time delay between consecutive changes?
3. **On-exceed behavior:** What happens - reject? warn? throttle?

#### Business Impact

**Scenario A - Too Restrictive:**
```
User wants: 100 → 160 sensors (60% change)
System: REJECTED ❌
Impact: User frustration, legitimate use blocked
```

**Scenario B - Too Permissive:**
```
User does: 2000 → 1020 sensors (49% change)
System: ACCEPTED ✅
Impact: Data discontinuity, quality issues
```

**No one knows which scenario is correct!**

#### Affected Tests

- `test_roi_sensor_change_within_limit`
- `test_roi_sensor_change_exceeds_limit`
- `test_roi_frequency_change_validation`
- `test_roi_channel_change_validation`
- `test_roi_combined_changes`
- `test_roi_change_cooldown_period`

**Documentation:** See `CONFLUENCE_SPECS_MEETING.md:87-118`

---

### 🔴 Issue #3: NFFT Validation Accepts Any Value

**Category:** Data Validation  
**Tests Affected:** 6 tests  
**Code Location:** `src/utils/validators.py:194-227`

#### The Problem

**Config file says:** Valid NFFT = [256, 512, 1024, 2048]  
**Code does:** Accepts ANY positive integer, only warns

**Code vs Config Mismatch:**
```python
def validate_nfft_value(nfft: int) -> bool:
    if not is_power_of_2(nfft):
        warnings.warn(f"NFFT={nfft} not power of 2")  # ⚠️ Only warns
    return True  # ✅ Always passes!
```

#### What's Missing

1. Should code **enforce** the config list? (reject invalid values)
2. Or keep **warning-only** behavior? (accept but warn)
3. What's the absolute maximum NFFT? (currently unlimited)
4. Can users override with custom values?

#### Real Examples

**Case 1: NFFT=3000 (not power of 2)**
- Validation: PASS ✅
- Result: FFT runs 5-10x slower
- Impact: Performance degradation not caught

**Case 2: NFFT=16384 (huge, but power of 2)**
- Validation: PASS ✅
- Memory: ~64MB per request
- Impact: 100 requests = 6.4GB → OOM crash

#### Business Impact

Invalid NFFT values can cause:
- Performance degradation (non-power-of-2 values)
- Memory exhaustion (very large values)
- System crashes

**Documentation:** See `CONFLUENCE_SPECS_MEETING.md:125-159`

---

### 🔴 Issue #8: MongoDB Outage Behavior Undefined

**Category:** Reliability & Error Handling  
**Tests Affected:** 5 tests  
**Code Location:** Test failures in integration suite

#### The Problem

Tests fail because **expected behavior during MongoDB outage is not specified**:

**Test Failures:**
```
Expected: HTTP 503 (Service Unavailable)
Actual:   HTTP 500 (Internal Server Error)

Expected: Recovery in 5 seconds
Actual:   Recovery takes 15 seconds
```

#### What's Missing

1. **HTTP status code:** Should system return 503 or 500 during DB outage?
2. **Recovery time:** Maximum time to recover after DB comes back?
3. **Caching policy:** Should system cache data during outage?
4. **User message:** What error message to show?

#### Business Impact

**Without spec:**
- Tests can't verify correct behavior
- Production incidents have unclear expectations
- SLA for recovery time undefined

**With spec:**
- Clear behavior definition
- Tests can validate properly
- Operations knows expected recovery time

**Documentation:** See `documentation/infrastructure/MONGODB_ISSUES_WORKFLOW.md`

---

### 🔴 Issue #10: SingleChannel API Returns 422 for All Requests

**Category:** API Contract  
**Tests Affected:** 11 out of 13 tests (85% failure rate)  
**Code Location:** `tests/integration/api/test_singlechannel_view_mapping.py`

#### The Problem

**POST /configure endpoint returns 422 (Unprocessable Entity) for ALL requests.** Not clear if:
- Endpoint is not implemented yet
- Payload format is wrong
- Feature is disabled

**Test Results:**
```
13 total tests:
├─ 11 FAIL (422 status code)
├─ 2 PASS (basic checks)
└─ Failure rate: 85%
```

#### What's Missing

1. **Is endpoint valid?** Should it exist or is it deprecated?
2. **Payload format:** What's the correct request structure?
3. **Feature status:** Is SingleChannel view implemented?
4. **Expected behavior:** What should a valid request return?

#### Business Impact

**Current State:**
- Can't test SingleChannel functionality
- Don't know if it's a bug or unimplemented feature
- 85% test failure rate creates noise

**Need Clarity:**
- If implemented → need correct payload format
- If not implemented → need to skip/remove tests
- If deprecated → need to update documentation

**Documentation:** See `documentation/testing/SINGLECHANNEL_TEST_RESULTS.md:48-80`

---

## 🟠 High Priority Issues (Next Sprint)

---

### 🟠 Issue #4: Frequency Range - No Absolute Limits

**Category:** Data Validation  
**Tests Affected:** 16 tests  
**Code Location:** `src/models/focus_server_models.py:46-57`

#### The Problem

```python
class FrequencyRange(BaseModel):
    min_freq: float = Field(gt=0)  # Only: must be > 0
    max_freq: float = Field(gt=0)  # Only: must be > 0
    # ❌ No absolute maximum!
    # ❌ No minimum span!
```

**Accepts extreme values:**
- min_freq = 0.0001 Hz ✅ (too low, impractical)
- max_freq = 999999999 Hz ✅ (999 MHz, impossible)
- min_freq = max_freq ✅ (single frequency - valid?)

#### What's Missing

1. Absolute maximum frequency? (e.g., 48000 Hz for audio?)
2. Absolute minimum frequency? (e.g., 1 Hz?)
3. Minimum span required? (e.g., max - min >= 10 Hz?)
4. Is single frequency (min == max) valid?

#### Affected Tests

16 tests including:
- `test_frequency_range_within_bounds`
- `test_frequency_range_exceeds_max`
- `test_frequency_range_equal_min_max`
- `test_frequency_range_extreme_values`
- +12 more

**Documentation:** See `CONFLUENCE_SPECS_MEETING.md:161-197`

---

### 🟠 Issue #5: Sensor Range - No Min/Max ROI Size

**Category:** Data Validation  
**Tests Affected:** 15 tests  
**Code Location:** `src/utils/validators.py:116-151`

#### The Problem

System has 2222 total sensors, but validation only checks:
- ✅ min_sensor >= 1
- ✅ max_sensor <= 2222
- ✅ min <= max

**What it DOESN'T check:**
- ❌ ROI size too small (e.g., single sensor)
- ❌ ROI size too large (e.g., all 2222 sensors)

#### Edge Cases Without Specs

**Case 1: Single Sensor ROI**
```python
min_sensor = 500, max_sensor = 500
Validation: PASS ✅
Question: Is this a valid use case?
```

**Case 2: Entire Cable**
```python
min_sensor = 1, max_sensor = 2222
Validation: PASS ✅
Impact: Enormous data rate, high CPU/memory
Question: Should this be limited?
```

#### What's Missing

1. Minimum ROI size? (e.g., at least 10 sensors?)
2. Maximum ROI size? (e.g., at most 500 sensors?)
3. Is single-sensor ROI valid?
4. Practical recommendations?

**Documentation:** See `CONFLUENCE_SPECS_MEETING.md:199-237`

---

### 🟠 Issue #9: RabbitMQ Commands - No Timeouts

**Category:** External Integration  
**Tests Affected:** 8 tests  
**Code Location:** `src/external/rabbitmq/`

#### The Problem

RabbitMQ command execution has **no timeout or retry logic**.

**Current Behavior:**
```python
def execute_rabbitmq_command(cmd):
    result = subprocess.run(cmd, shell=True)  # ❌ No timeout!
    return result
    # If RabbitMQ hangs → test hangs forever
```

#### What's Missing

1. **Command timeouts:** How long to wait before giving up?
2. **Retry logic:** Should we retry failed commands?
3. **Exponential backoff:** Wait between retries?
4. **Circuit breaker:** Stop trying after N failures?

#### Business Impact

**Without timeouts:**
- Tests can hang indefinitely
- CI/CD pipeline stalls
- Manual intervention needed

**With timeouts:**
- Tests fail fast
- Clear error messages
- Predictable behavior

**Documentation:** See `docs/RABBITMQ_AUTOMATION_GUIDE.md`

---

### 🟠 Issue #11: Live/Historical Threshold - 1 Hour Hardcoded

**Category:** Business Logic  
**Tests Affected:** Not directly tested  
**Code Location:** `src/utils/helpers.py:200-220`

#### The Problem

Code has hardcoded `LIVE_HISTORICAL_THRESHOLD = 3600` (1 hour) that determines whether to use "live" or "historical" mode.

```python
def get_data_mode(timestamp):
    if time.time() - timestamp < 3600:  # ❌ Hardcoded 1 hour
        return "live"
    return "historical"
```

#### What's Missing

1. Confirmation: Is 1 hour correct?
2. Or should it be: 30 min? 2 hours? Configurable?
3. Does this affect performance/resource usage?

#### Business Impact

This threshold affects:
- Which data retrieval path is used
- Performance characteristics
- Resource allocation

**Need confirmation this value is intentional and correct.**

**Documentation:** See `CRITICAL_MISSING_SPECS_LIST.md:195-206`

---

### 🟠 Issue #15: Data Quality - No Validation Limits

**Category:** Data Quality  
**Tests Affected:** Multiple  
**Code Location:** `src/utils/validators.py:229-324`

#### The Problem

No validation for data quality metrics:
- No amplitude range limits (too high/low values accepted)
- No missing data percentage threshold
- No signal-to-noise ratio requirements

#### What's Missing

1. **Amplitude limits:** Min/max acceptable values?
2. **Missing data:** Maximum percentage of missing samples?
3. **SNR requirements:** Minimum signal quality?
4. **Outlier detection:** When to reject anomalous data?

#### Business Impact

Without data quality validation:
- Bad data passes validation
- Analysis results unreliable
- Can't enforce quality standards

**Documentation:** See `CRITICAL_MISSING_SPECS_LIST.md:70-90`

---

### 🟠 Issue #16: Error Handling - HTTP Status Semantics Unclear

**Category:** API Contract  
**Tests Affected:** Multiple  
**Code Location:** Multiple API files

#### The Problem

Not clear when to use each HTTP status code:

| Status | Current Usage | Question |
|--------|---------------|----------|
| 200 OK | Data available | What if data exists but empty? |
| 208 Already Reported | ??? | When to use this? |
| 400 Bad Request | Validation failed | Clear ✅ |
| 422 Unprocessable | ??? | vs 400? |
| 500 Internal Error | System error | Clear ✅ |
| 503 Service Unavailable | ??? | When to use vs 500? |

#### What's Missing

1. **200 with empty data:** Is this valid or should it be 204 (No Content)?
2. **208 meaning:** When should this be returned?
3. **422 vs 400:** What's the distinction?
4. **503 vs 500:** When DB is down, which one?

#### Business Impact

**Without clear semantics:**
- Inconsistent API behavior
- Tests can't validate correctly
- Client code has undefined behavior

**Documentation:** See `CRITICAL_MISSING_SPECS_LIST.md:246-273`

---

## 🟡 Medium Priority Issues (Future Consideration)

---

### 🟡 Issue #6: API Timeouts - Thresholds Arbitrary

**Category:** Performance  
**Tests Affected:** 3 tests  
**Code Location:** `tests/integration/api/test_api_endpoints_high_priority.py:135-147`

#### The Problem

API timeout tests use **arbitrary** thresholds like 1000ms with no official SLA.

```python
assert duration < 1.0  # ❌ "Reasonable" guess, no SLA
```

#### What's Missing

Response time SLA for each endpoint:

| Endpoint | Current | Need |
|----------|---------|------|
| GET /channels | 1000ms | ? |
| GET /metadata | - | ? |
| POST /config | - | ? |

**Documentation:** See `CONFLUENCE_SPECS_MEETING.md:239-273`

---

### 🟡 Issue #7: Config Validation - Edge Cases Have No Assertions

**Category:** API Contract  
**Tests Affected:** 8 tests  
**Code Location:** `tests/integration/api/test_config_validation_high_priority.py:475-520`

#### The Problem

Tests exist for edge cases but have **no assertions** because behavior is undefined.

**Examples:**
```python
def test_frequency_range_equal_min_max():
    # min_freq == max_freq
    # TODO: Should this be 200 OK or 400 Error?
    # assert ???
```

#### Edge Cases Without Specs

| Case | Current | Need Decision |
|------|---------|---------------|
| min_freq == max_freq | Unknown | 200 or 400? |
| min_channel == max_channel | Unknown | 200 or 400? |
| ROI size = 1 sensor | Unknown | Valid? |
| NFFT not in config list | Warning | Reject or accept? |

**Documentation:** See `CONFLUENCE_SPECS_MEETING.md:275-310`

---

### 🟡 Issue #12: Polling Helper - Hardcoded Timeouts

**Category:** Test Infrastructure  
**Tests Affected:** Multiple  
**Code Location:** `src/utils/helpers.py:474-504`

#### The Problem

Generic polling function uses hardcoded 60s timeout and 1s interval:

```python
def poll_until(condition, timeout=60, interval=1):
    # ❌ Same timeout for all operations
```

#### What's Missing

Different timeouts for different operations:
- Quick operations (e.g., status check): 5s?
- Data availability: 30s?
- Processing completion: 120s?

**Documentation:** See `CODE_EVIDENCE_MISSING_SPECS.md:231-259`

---

### 🟡 Issue #13: Default Values - Code vs Config Mismatch

**Category:** Configuration  
**Tests Affected:** Multiple  
**Code Location:** `src/utils/helpers.py:507-532`

#### The Problem

Default values differ between code and config files:

| Parameter | Code | Config | Issue |
|-----------|------|--------|-------|
| sensors_max | 100 | 109 | Mismatch |
| nfft | 1024 | 1024 | ✅ Match |
| frequency_max | 5000 | 10000 | Mismatch |

#### What's Missing

Need to align defaults between:
- `src/utils/helpers.py`
- `config/settings.yaml`
- `config/environments.yaml`

**Documentation:** See `CODE_EVIDENCE_MISSING_SPECS.md:262-293`

---

### 🟡 Issue #17: Time Validation - No Future/Past Limits

**Category:** Data Validation  
**Tests Affected:** Multiple  
**Code Location:** `src/models/focus_server_models.py:99-105`

#### The Problem

System accepts **any** timestamp, including:
- Far future: year 2999 ✅ accepted
- Distant past: year 1900 ✅ accepted

```python
class TimeRange(BaseModel):
    start_time: datetime  # No past limit
    end_time: datetime    # No future limit
```

#### What's Missing

1. **Maximum future:** How far ahead can users request? (e.g., +24 hours?)
2. **Maximum past:** How far back is data available? (e.g., -30 days?)
3. **Validation logic:** Reject out-of-range times or warn?

**Documentation:** See `CRITICAL_MISSING_SPECS_LIST.md:288-305`

---

### 🟡 Issue #18: Task Lifecycle - No Cleanup/Timeout

**Category:** Resource Management  
**Tests Affected:** Not tested  
**Code Location:** Backend (not in automation code)

#### The Problem

Tasks are created but **never cleaned up or expire**.

#### What's Missing

1. **Auto-cleanup time:** When to delete old tasks? (e.g., after 24 hours?)
2. **Maximum concurrent:** How many tasks can run simultaneously?
3. **Timeout:** Maximum task execution time?

**Documentation:** See `CRITICAL_MISSING_SPECS_LIST.md:307-320`

---

## 🔵 Low Priority Issues (Documentation Only)

---

### 🔵 Issue #19: Kubernetes Resource Limits Not Defined

**Category:** Infrastructure  
**Code Location:** K8s manifests

#### The Problem

No CPU/memory limits set in Kubernetes manifests. Pods can consume unlimited resources.

#### What's Missing

Resource limits for each service:
- CPU: request + limit
- Memory: request + limit
- Storage: PVC sizes

**Documentation:** See `CRITICAL_MISSING_SPECS_LIST.md:388-407`

---

### 🔵 Issue #20: Security - No Authentication

**Category:** Security  
**Code Location:** Backend

#### The Problem

System currently has:
- ❌ No authentication
- ❌ No authorization
- ❌ No rate limiting

#### What's Missing

1. **Auth method:** API keys? OAuth? JWT?
2. **Rate limiting:** Requests per minute/hour?
3. **Access control:** Role-based? User-based?

**Documentation:** See `CRITICAL_MISSING_SPECS_LIST.md:471-502`

---

## 📊 Summary Statistics

### By Priority

| Priority | Count | Tests Affected |
|----------|-------|----------------|
| 🔴 Critical | 5 | 56+ |
| 🟠 High | 8 | 39+ |
| 🟡 Medium | 4 | 15+ |
| 🔵 Low | 2 | - |
| **Total** | **19** | **110+** |

### By Category

| Category | Issues | Tests Affected |
|----------|--------|----------------|
| Data Validation | 7 | 48 |
| Performance | 3 | 31 |
| API Contract | 3 | 22 |
| Configuration | 2 | 8+ |
| External Integration | 2 | 13 |
| Infrastructure | 1 | - |
| Security | 1 | - |

### Top 5 Most Impactful

1. **Performance Assertions Disabled** - 28 tests can't validate
2. **Frequency Range No Limits** - 16 tests blocked
3. **Sensor Range No Limits** - 15 tests blocked
4. **SingleChannel API Fails** - 11 tests failing (85%)
5. **RabbitMQ No Timeouts** - 8 tests can hang

---

## 📋 Recommended Action Plan

### Phase 1: Critical Issues (Week 1)

**Meeting Agenda (2-3 hours):**
1. Performance thresholds (Issue #1) - 30 min
2. ROI change limit (Issue #2) - 20 min
3. NFFT validation (Issue #3) - 20 min
4. MongoDB behavior (Issue #8) - 15 min
5. SingleChannel endpoint (Issue #10) - 15 min

**Deliverables:**
- ✅ Documented decisions for all 5 issues
- ✅ Numeric values for thresholds
- ✅ Clear behavior definitions

### Phase 2: Implementation (Week 2-3)

1. Update `src/utils/validators.py`
2. Update `config/settings.yaml`
3. Enable assertions in performance tests
4. Add missing validations
5. Run full test suite

### Phase 3: High Priority (Week 4)

Address remaining high priority issues:
- Frequency/sensor ranges (Issues #4, #5)
- RabbitMQ timeouts (Issue #9)
- Live/historical threshold (Issue #11)

### Phase 4: Medium Priority (Following Month)

- API timeouts and edge cases (Issues #6, #7)
- Polling and defaults (Issues #12, #13)
- Data quality validation (Issue #15)

---

## 📎 Supporting Documentation

### Key Documents

1. **Confluence Specs Meeting Doc:** `CONFLUENCE_SPECS_MEETING.md`
   - Detailed breakdown of top 7 critical issues
   - Questions to answer in specs meeting
   
2. **Critical Specs List:** `CRITICAL_MISSING_SPECS_LIST.md`
   - Complete catalog of 200+ missing specs
   - YAML format with all details

3. **Code Evidence:** `CODE_EVIDENCE_MISSING_SPECS.md`
   - Direct code examples
   - Line-by-line analysis

4. **Test Results:** `documentation/testing/`
   - SingleChannel test results
   - MongoDB issues documentation

### Code Files to Review

Primary files needing updates:
- `src/utils/validators.py` - validation functions
- `src/models/focus_server_models.py` - data models
- `config/settings.yaml` - configuration
- `tests/integration/performance/` - performance tests
- `tests/integration/api/` - API tests

---

## ❓ Pre-Meeting Preparation

### For Product Team

Please review:
1. **Performance expectations** - What are acceptable response times?
2. **Business rules** - ROI change limits, data quality standards
3. **Feature status** - Is SingleChannel implemented?

### For Development Team

Please prepare:
1. **Technical constraints** - What's feasible? (e.g., NFFT limits)
2. **Current behavior** - How does system behave now?
3. **Implementation effort** - Time estimates for each fix

### For QA Team

Please provide:
1. **Test coverage** - Which tests are affected?
2. **False positive/negative** - Current pain points
3. **Priority feedback** - Which specs are most blocking?

---

## 🎯 Success Criteria

**Meeting is successful when:**
- ✅ All critical issues (1-5, 8, 10) have documented decisions
- ✅ Numeric values assigned for all thresholds
- ✅ Clear yes/no for all edge cases (min==max, etc.)
- ✅ Action items assigned with owners

**Implementation is complete when:**
- ✅ All affected tests can pass/fail correctly
- ✅ No TODO comments waiting for specs
- ✅ Documentation updated in Xray/Jira
- ✅ Test suite provides reliable quality gate

---

**Document Version:** 1.0  
**Last Updated:** October 22, 2025  
**Contact:** QA Automation Team  
**Status:** Ready for Specs Meeting

