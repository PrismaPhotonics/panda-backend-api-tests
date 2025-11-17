# Focus Server API Testing Report

**Test Suite:** Configuration Validation (High Priority)  
**Date:** October 23, 2025  
**API Endpoint:** `POST https://10.10.100.100/focus-server/configure`  
**API Model:** `ConfigureRequest` / `ConfigureResponse`  
**Server Version:** pzlinux:10.7.122  
**Total Tests:** 26 (21 current behavior + 5 requirement tests)  
**Passed:** 21 ✅  
**XFailed (Expected):** 5 🔴  

---

## ⚠️ IMPORTANT NOTICE

This test suite contains **TWO types of tests**:

### 1. 📋 Current Behavior Tests (21 tests)
- **Marker:** `@pytest.mark.documents_current_behavior`
- **Purpose:** Document how the server CURRENTLY behaves
- **Result:** ✅ All PASS (even when server accepts invalid inputs)
- **Note:** Some tests document BUGS/missing validation

### 2. ✅ Requirement Tests (5 tests)
- **Marker:** `@pytest.mark.requirement + @pytest.mark.xfail`
- **Purpose:** Document how the server SHOULD behave per requirements
- **Result:** 🔴 All XFAIL (expected to fail until server validation is implemented)
- **Note:** These show the CORRECT expected behavior for backend developers

---

## Executive Summary

### Test Results
- **21/21 Current Behavior Tests:** ✅ PASS
- **5/5 Requirement Tests:** 🔴 XFAIL (expected)

### Critical Findings

**❌ Server Validation is NOT Implemented**

The tests reveal that the Focus Server **accepts invalid configurations** without rejection:

1. **displayInfo.height**: Accepts negative values and zero
2. **nfftSelection**: Accepts non-power-of-2 values and values > 2048
3. **frequencyRange**: No Nyquist limit enforcement
4. **channels**: Accepts > 2500 channels (spec limit)

**Current Server Behavior:**
- Returns `200 OK` with `job_id` for invalid configurations
- May internally adjust/correct values (e.g., NFFT=1000 → nearest valid)
- No clear error messages to clients

**Expected Server Behavior (per requirements):**
- Return `400 Bad Request` for invalid inputs
- Include clear error messages explaining what validation failed
- Reject configurations that exceed technical limits

---

## Test Results by Category

### 1. Missing Required Fields (PZ-13879) - 4 Tests

| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| Missing `channels` | No channels field | Validation error | ✅ Pydantic caught | PASS |
| Missing `frequencyRange` | No frequencyRange field | Server may accept (Optional) | ⚠️ Optional field | PASS |
| Missing `nfftSelection` | No nfftSelection field | Server may accept (Optional) | ⚠️ Optional field | PASS |
| Missing `displayTimeAxisDuration` | No displayTimeAxisDuration | Server may accept (Optional) | ⚠️ Optional field | PASS |

**Note:** Fields marked Optional in ConfigureRequest may cause server errors (500) when missing.

---

### 2. Invalid Display Info (PZ-13878) - 3 Tests + 2 Requirement Tests

#### Current Behavior Tests (documents what IS)

| Test | Input | Server Response | Status |
|------|-------|-----------------|--------|
| Negative height | `displayInfo: {height: -100}` | ⚠️ 200 OK, job_id returned | PASS |
| Zero height | `displayInfo: {height: 0}` | ⚠️ 200 OK, job_id returned | PASS |
| Missing height key | `displayInfo: {}` | ✅ Pydantic validation error | PASS |

#### Requirement Tests (documents what SHOULD BE)

| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| Negative height MUST reject | `displayInfo: {height: -100}` | ❌ 400 Bad Request | ⚠️ 200 OK | 🔴 XFAIL |
| Zero height MUST reject | `displayInfo: {height: 0}` | ❌ 400 Bad Request | ⚠️ 200 OK | 🔴 XFAIL |

**Finding:** Server accepts invalid height values. Client-side Pydantic validation catches some cases but server should validate too.

**For Backend Developers:**
```python
# Required Server-Side Validation:
if displayInfo.height <= 0:
    return 400, "displayInfo.height must be positive (> 0)"
```

---

### 3. Invalid Frequency Range (PZ-13877) - 3 Tests + 1 Requirement Test

#### Current Behavior Tests

| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| min > max | `{min: 500, max: 100}` | Rejection | ✅ Pydantic caught | PASS |
| Exceeds Nyquist | `{min: 0, max: 600}` (>500 Hz) | Dynamic validation | ⚠️ Server accepts | PASS |
| min == max | `{min: 250, max: 250}` | May accept/reject | ⚠️ Server accepts | PASS |

#### Requirement Tests

| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| Frequency > Nyquist MUST reject | `{min: 0, max: 600}` (PRR=1000) | ❌ 400 Bad Request | ⚠️ 200 OK | 🔴 XFAIL |

**Finding:** No dynamic Nyquist limit validation implemented.

**For Backend Developers:**
```python
# Required Server-Side Validation:
# 1. Get PRR from dataset metadata
prr = get_dataset_prr()  
nyquist_limit = prr / 2

# 2. Validate frequency range
if frequencyRange.max > nyquist_limit:
    return 400, f"Frequency {frequencyRange.max} Hz exceeds Nyquist limit ({nyquist_limit} Hz) for this dataset"
```

**Decision (Specs Meeting 22-Oct-2025):** Dynamic validation per dataset metadata required.

---

### 4. Invalid Channel Range (PZ-13876) - 4 Tests

| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| min > max | `{min: 50, max: 10}` | Rejection | ✅ Pydantic caught | PASS |
| min == max | `{min: 7, max: 7}` | Valid for SINGLECHANNEL | ✅ Accepted (view_type=1) | PASS |
| Exceeds 2500 | `{min: 1, max: 2501}` | Rejection | ⚠️ Server accepts 2501 channels | PASS |
| Exactly 2500 | `{min: 1, max: 2500}` | Accepted | ✅ Accepted | PASS |

**Finding:** Server does not enforce 2500 channel limit.

**Decision (Specs Meeting 22-Oct-2025):** Maximum 2500 channels per tab required.

**For Backend Developers:**
```python
# Required Server-Side Validation:
channel_count = channels.max - channels.min + 1
if channel_count > 2500:
    return 400, f"Channel count ({channel_count}) exceeds maximum (2500)"
```

---

### 5. Valid Configurations (PZ-13873) - 6 Tests + 2 Requirement Tests

#### Current Behavior Tests

| Test | Configuration | Result | Status |
|------|---------------|--------|--------|
| All parameters valid | Standard config | ✅ job_id returned | PASS |
| Multiple channels | 50 channels | ✅ job_id returned | PASS |
| Narrow channel range | 2 channels | ✅ job_id returned | PASS |
| NFFT values | 256, 512, 1024, 2048 | ✅ All accepted | PASS |
| NFFT exceeds max | NFFT=4096 (>2048) | ⚠️ Server accepts (no limit) | PASS |
| NFFT not power of 2 | NFFT=1000 | ⚠️ Server accepts (adjusts internally) | PASS |

#### Requirement Tests

| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| NFFT not power of 2 MUST reject | NFFT=1000 | ❌ 400 Bad Request | ⚠️ 200 OK | 🔴 XFAIL |
| NFFT > 2048 MUST reject | NFFT=4096 | ❌ 400 Bad Request | ⚠️ 200 OK | 🔴 XFAIL |

**Decision (Specs Meeting 22-Oct-2025):**
- NFFT must be power of 2 (256, 512, 1024, 2048)
- NFFT max = 2048
- **Absolute rejection** - NO automatic correction

**For Backend Developers:**
```python
# Required Server-Side Validation:
# 1. Check power of 2
valid_nfft = [256, 512, 1024, 2048]
if nfftSelection not in valid_nfft:
    return 400, f"nfftSelection must be power of 2 (256, 512, 1024, 2048), got {nfftSelection}"

# 2. Check maximum
if nfftSelection > 2048:
    return 400, f"nfftSelection {nfftSelection} exceeds maximum (2048)"
```

---

## API Call Examples

### ✅ Valid Configuration (Accepted)

**Request:**
```json
POST /configure
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 1, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": "0"
}
```

**Response (200 OK):**
```json
{
  "status": "",
  "frequencies_list": [0.0, 7.797, 15.594, ...],
  "lines_dt": 0.01,
  "channel_to_stream_index": {"1": 0, "2": 0, ...},
  "stream_amount": 3,
  "job_id": "23-68",
  "frequencies_amount": 64,
  "channel_amount": 50,
  "stream_port": "12323",
  "stream_url": "http://10.10.100.113",
  "view_type": 0
}
```

---

### ⚠️ Invalid Configuration (Currently Accepted - BUG)

#### Example 1: Negative Height

**Current Behavior:**
```json
POST /configure
{
  "displayInfo": {"height": -100},
  ...
}
```

**Response (200 OK):**
```json
{
  "job_id": "31-77",
  ...
}
```

**Expected Behavior (Requirement):**
```json
HTTP 400 Bad Request
{
  "error": "Validation failed",
  "details": "displayInfo.height must be positive (> 0), got -100"
}
```

---

#### Example 2: NFFT Not Power of 2

**Current Behavior:**
```json
POST /configure
{
  "nfftSelection": 1000,  // Not power of 2
  ...
}
```

**Response (200 OK):**
```json
{
  "job_id": "31-76",
  // Server internally adjusts to nearest valid NFFT
  ...
}
```

**Expected Behavior (Requirement):**
```json
HTTP 400 Bad Request
{
  "error": "Validation failed",
  "details": "nfftSelection must be power of 2 (256, 512, 1024, 2048), got 1000"
}
```

**Decision:** NO automatic correction - absolute rejection per specs meeting 22-Oct-2025.

---

#### Example 3: Frequency Exceeds Nyquist

**Current Behavior:**
```json
POST /configure
{
  "frequencyRange": {"min": 0, "max": 600},  // PRR=1000 → Nyquist=500
  ...
}
```

**Response (200 OK):**
```json
{
  "job_id": "31-78",
  ...
}
```

**Expected Behavior (Requirement):**
```json
HTTP 400 Bad Request
{
  "error": "Validation failed",
  "details": "Frequency 600 Hz exceeds Nyquist limit (500 Hz) for this dataset (PRR=1000 Hz)"
}
```

---

## Server Validation Summary

| Parameter | Client Validation | Server Validation | Required Action |
|-----------|-------------------|-------------------|-----------------|
| `displayTimeAxisDuration` | Optional field | Weak | ⚠️ Make required OR handle defaults |
| `nfftSelection` | Optional, gt=0 | **None** | ❌ Add power-of-2 + max=2048 validation |
| `displayInfo.height` | Required, gt=0 | **None** | ❌ Add server-side validation (> 0) |
| `channels.min` | Required, ge=1 | Basic | ✅ Working |
| `channels.max` | Required, ge=1 | **No limit** | ❌ Add max=2500 validation |
| `channels` range | max ≥ min | Basic | ✅ Working (Pydantic) |
| `frequencyRange.min` | Required, ge=0 | Basic | ✅ Working |
| `frequencyRange.max` | Required, ge=0 | **No Nyquist** | ❌ Add dynamic Nyquist validation |
| `frequencyRange` range | max ≥ min | Basic | ✅ Working (Pydantic) |
| `view_type` | Required enum | Strong | ✅ Working |

**Legend:**
- ✅ Working - validation implemented and functional
- ⚠️ Weak - partial validation, needs improvement
- ❌ None - validation missing, MUST be implemented

---

## Recommendations for Backend Developers

### 🔴 Critical Priority (Must Implement)

1. **displayInfo.height Validation**
   ```python
   if displayInfo.height <= 0:
       raise ValidationError("displayInfo.height must be positive (> 0)")
   ```

2. **NFFT Validation**
   ```python
   VALID_NFFT = [256, 512, 1024, 2048]
   if nfftSelection not in VALID_NFFT:
       raise ValidationError(f"nfftSelection must be power of 2 (256, 512, 1024, 2048), got {nfftSelection}")
   ```

3. **Channel Count Limit**
   ```python
   channel_count = channels.max - channels.min + 1
   if channel_count > 2500:
       raise ValidationError(f"Channel count ({channel_count}) exceeds maximum (2500)")
   ```

4. **Dynamic Nyquist Validation**
   ```python
   prr = get_dataset_prr()  # From metadata
   nyquist_limit = prr / 2
   if frequencyRange.max > nyquist_limit:
       raise ValidationError(
           f"Frequency {frequencyRange.max} Hz exceeds Nyquist limit "
           f"({nyquist_limit} Hz) for this dataset (PRR={prr} Hz)"
       )
   ```

### ⚠️ Medium Priority

5. **Standardize Error Responses**
   - Return consistent 400 Bad Request for validation errors
   - Include structured error messages with details
   - Document error formats in API schema

6. **Required Fields**
   - Decide which Optional fields are truly optional
   - Handle missing optional fields gracefully (no 500 errors)
   - Provide sensible defaults where appropriate

### ✅ Low Priority

7. **Update API Documentation**
   - Update OpenAPI/Swagger schema
   - Document validation rules
   - Provide examples of valid/invalid inputs

8. **Enhanced Client Validation**
   - Update Pydantic models to match server validation
   - Add custom validators for complex rules

---

## How to Run Tests

### Run All Tests
```bash
pytest tests/integration/api/test_config_validation_high_priority.py -v
```

### Run Current Behavior Tests Only
```bash
pytest tests/integration/api/test_config_validation_high_priority.py -m "documents_current_behavior" -v
```

### Run Requirement Tests (show what validation is needed)
```bash
pytest tests/integration/api/test_config_validation_high_priority.py -m "requirement" -v
```

### Force Requirement Tests to Run (ignore xfail)
```bash
pytest tests/integration/api/test_config_validation_high_priority.py -m "requirement" --runxfail -v
```

---

## Test Environment

- **Server:** `https://10.10.100.100/focus-server/`
- **Pod:** `focus-server-58f8b65dc9-bdpbx`
- **Image:** `pzlinux:10.7.122` (Old API)
- **Pod Age:** 27 days
- **Service:** `ClusterIP 10.43.7.249:5000`
- **Response Time:** Average 200-500ms per request
- **Test Duration:** ~17 seconds

---

## Conclusion

### Test Status
✅ **All 21 current behavior tests PASS** - Server is functionally operational  
🔴 **All 5 requirement tests XFAIL** - Server validation needs implementation

### Server Assessment

**Functionality:** ✅ GOOD  
- API endpoints working correctly
- Returns valid responses for successful configs
- No crashes or unexpected errors

**Validation:** ❌ MISSING  
- Server accepts invalid configurations
- No clear error messages for validation failures
- Missing critical validation per specs (height, NFFT, Nyquist, channel limits)

**Production Readiness:** ⚠️ MEDIUM  
- ✅ API is functional and stable
- ❌ Missing server-side validation may lead to:
  - Unexpected behavior for end users
  - Difficult debugging (invalid configs silently accepted)
  - Security/stability risks (no input sanitization)
- ❌ No clear error messages for invalid configs

### Next Steps

1. **For Backend Developers:**
   - Review requirement tests in `tests/integration/api/test_config_validation_high_priority.py`
   - Implement server-side validation per recommendations above
   - Run requirement tests with `--runxfail` to verify implementation

2. **For QA:**
   - Re-run all tests after backend validation is implemented
   - Requirement tests should PASS instead of XFAIL
   - Update this report with new findings

3. **For Product:**
   - Review and approve validation requirements
   - Decide on error message formats for end users
   - Update user documentation

---

**Report Generated:** October 23, 2025  
**Test Framework:** pytest 8.4.2  
**Python Version:** 3.13.7  
**Test File:** `tests/integration/api/test_config_validation_high_priority.py`  
**Test Strategy:** Dual approach - document current behavior + define requirements
