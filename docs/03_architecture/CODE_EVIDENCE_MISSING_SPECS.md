# 📌 Code Evidence: Missing Specifications
## Exact Code Locations Demonstrating Spec Gaps

**Date:** October 22, 2025  
**Purpose:** Evidence for specs meeting presentation  

---

## 🎯 Executive Summary

**Problem:** We have **190+ automated tests** but many lack **clear pass/fail criteria** due to missing specifications.

**Evidence:** Found **50+ locations** in code where specs are:
- Hardcoded without confirmation
- Commented out waiting for specs
- Using arbitrary "reasonable" values

---

## 🔴 TOP 10 CODE EXAMPLES

### 1️⃣ **ROI Change Limit - 50% Hardcoded**

**Location:** `src/utils/validators.py:395`

```python
def validate_roi_change_safety(
    current_min: int,
    current_max: int,
    new_min: int,
    new_max: int,
    max_change_percent: float = 50.0  # ❌ HARDCODED - NO SPEC!
) -> Dict[str, Any]:
```

**Issue:** 
- Value: `50%`
- Status: ❌ **Never confirmed by team**
- Impact: 6 tests depend on this value

**Questions:**
- Is 50% correct?
- Should it be 30%? 70%?
- Any cooldown period?

---

### 2️⃣ **Performance Assertions - Disabled**

**Location:** `tests/integration/performance/test_performance_high_priority.py:146-170`

```python
def test_p95_p99_latency_post_config(self, focus_server_api):
    """Test PZ-13770: P95/P99 latency for POST /config"""
    
    # TODO: Update thresholds after specs meeting
    THRESHOLD_P95_MS = 500   # ❌ Arbitrary value
    THRESHOLD_P99_MS = 1000  # ❌ Arbitrary value
    MAX_ERROR_RATE = 0.05    # ❌ Arbitrary value
    
    error_rate = errors / num_requests
    assert error_rate <= MAX_ERROR_RATE
    
    # TODO: Uncomment after specs meeting
    # assert p95 < THRESHOLD_P95_MS   ❌ DISABLED!
    # assert p99 < THRESHOLD_P99_MS   ❌ DISABLED!
    
    # For now, just log warning
    if p95 >= THRESHOLD_P95_MS:
        logger.warning(f"⚠️ Would fail if enforced")
```

**Issue:**
- Tests exist but **assertions are disabled**
- Only logs warnings instead of failing
- Can't detect performance degradation

**Impact:** 28 performance tests without thresholds

---

### 3️⃣ **NFFT Validation - Accepts Anything**

**Location:** `src/utils/validators.py:194-227`

```python
def validate_nfft_value(nfft: int) -> bool:
    """Validate NFFT value (should be power of 2)."""
    
    if nfft <= 0:
        raise ValidationError("NFFT must be positive")
    
    is_power_of_2 = (nfft & (nfft - 1)) == 0
    
    if not is_power_of_2:
        warnings.warn(f"NFFT={nfft} not power of 2")  # ❌ Only warns!
    
    return True  # ✅ Always returns True!
```

**Issue:**
- Accepts any positive integer
- Only **warns** if not power of 2, doesn't reject
- No maximum limit
- No list of valid values enforced

**But config says:**
```yaml
nfft:
  valid_values: [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
```

**Code doesn't enforce this list!**

---

### 4️⃣ **Frequency Range - No Maximum**

**Location:** `src/models/focus_server_models.py:46-57`

```python
class FrequencyRange(BaseModel):
    """Frequency range configuration."""
    min: int = Field(..., ge=0)  # ✅ >= 0
    max: int = Field(..., ge=0)  # ✅ >= 0
    # ❌ NO UPPER LIMIT!
```

**Issue:**
- Only checks >= 0
- No absolute maximum
- No minimum range span

**Example:** These all pass validation:
```python
{"min": 0, "max": 500}       # ✅ OK
{"min": 0, "max": 1000}      # ✅ OK  
{"min": 0, "max": 999999}    # ✅ OK - but should it be?
{"min": 0, "max": 1}         # ✅ OK - too narrow?
```

---

### 5️⃣ **API Response Time - Arbitrary Threshold**

**Location:** `tests/integration/api/test_api_endpoints_high_priority.py:140-147`

```python
def test_get_channels_endpoint_response_time(self, focus_server_api):
    """Test PZ-13419.1: GET /channels response time"""
    
    start_time = time.time()
    channels = focus_server_api.get_channels()
    end_time = time.time()
    
    response_time_ms = (end_time - start_time) * 1000
    
    # TODO: Update threshold after specs meeting
    MAX_RESPONSE_TIME_MS = 1000  # ❌ "Reasonable" but not official
    
    assert response_time_ms < MAX_RESPONSE_TIME_MS
```

**Issue:**
- Uses 1000ms as "reasonable" threshold
- Not based on any SLA or requirement
- What if team wants 200ms? Or 3000ms?

---

### 6️⃣ **Sensor Range - No Minimum ROI Size**

**Location:** `src/utils/validators.py:116-151`

```python
def validate_sensor_range(min_sensor: int, max_sensor: int, total_sensors: int):
    """Validate sensor range."""
    
    if min_sensor < 0 or max_sensor < 0:
        raise ValidationError("Non-negative")
    
    if max_sensor <= min_sensor:
        raise ValidationError("max > min")
    
    if max_sensor >= total_sensors:
        raise ValidationError("Exceeds total")
    
    # ❌ NO CHECK FOR MINIMUM ROI SIZE!
    # ❌ NO CHECK FOR MAXIMUM ROI SIZE!
    return True
```

**Issue:**
- Accepts ROI with just 1 sensor: `{"min": 0, "max": 1}`
- No minimum (e.g., at least 10 sensors)
- No maximum (e.g., max 1000 sensors)

---

### 7️⃣ **Config Validation Tests - No Assertions**

**Location:** `tests/integration/api/test_config_validation_high_priority.py:475-520`

```python
def test_frequency_range_equal_min_max(self):
    """Test PZ-13876.1: frequency where min == max."""
    
    config_payload["frequencyRange"] = {"min": 100, "max": 100}
    
    response = focus_server_api.config_task(task_id, config_request)
    logger.info(f"Status: {response.status_code}")
    
    # TODO: Update assertion after specs meeting
    # For now, just log  ❌ NO ASSERTION!

def test_channel_range_equal_min_max(self):
    """Test PZ-13876.2: channels where min == max."""
    
    config_payload["channels"] = {"min": 7, "max": 7}
    
    # TODO: Update assertion after specs meeting  ❌ NO ASSERTION!
```

**Issue:**
- Tests exist and run
- But **don't check anything**!
- No spec if `min==max` is valid or not

---

### 8️⃣ **Polling - Hardcoded Timeouts**

**Location:** `src/utils/helpers.py:474-504`

```python
def poll_until(
    condition_func,
    timeout_seconds: int = 60,      # ❌ Hardcoded
    poll_interval: float = 1.0      # ❌ Hardcoded
):
    """Poll until condition or timeout."""
    start_time = time.time()
    
    while True:
        if condition_func():
            return True
        
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Timeout after {elapsed:.2f}s")
        
        time.sleep(poll_interval)
```

**Issue:**
- Default: 60s timeout, 1s interval
- No spec for different scenarios (live vs historic)
- What if live needs 5s, historic needs 300s?

---

### 9️⃣ **Default Config Values - Don't Match Config File**

**Location:** `src/utils/helpers.py:507-532`

**In Code:**
```python
def generate_config_payload(
    sensors_min: int = 0,          # ❌ Default: 0
    sensors_max: int = 100,        # ❌ Default: 100
    freq_min: int = 0,             # ✅ Matches
    freq_max: int = 500,           # ❌ Default: 500
    nfft: int = 1024,              # ✅ Matches
    canvas_height: int = 1000,     # ❌ No spec
):
```

**In Config File:** `config/environments.yaml`
```yaml
constraints:
  sensors:
    default_start: 11     # ≠ Code uses 0
    default_end: 109      # ≠ Code uses 100
  frequency:
    end_hz: 1000          # ≠ Code uses 500

defaults:
  waterfall:
    num_lines: 200        # ❌ Code doesn't use this
```

**Issue:** Mismatch between code defaults and config file!

---

### 🔟 **MongoDB Outage - Unknown Expected Behavior**

**Location:** Test failures

**Test Result:**
```
FAILED: test_mongodb_scale_down_outage_returns_503
AssertionError: Response time 15.423s exceeds maximum 5.0s
```

**Questions without answers:**
- What HTTP status when MongoDB down? (503? 500? 200?)
- Max response time during outage? (5s? 30s?)
- Should live data continue?
- Should we cache?

**No spec in code!**

---

## 📊 **Statistics: Code Locations**

### Files with Missing Specs:

| File | Issues | Lines |
|------|--------|-------|
| `src/utils/validators.py` | 4 issues | 395, 174, 213, 140 |
| `src/utils/helpers.py` | 2 issues | 474, 508 |
| `src/models/focus_server_models.py` | 1 issue | 48-49 |
| `tests/integration/performance/*.py` | 11 TODOs | Multiple |
| `tests/integration/api/*.py` | 8 TODOs | Multiple |

### TODO Comments Count:
```bash
$ grep -r "TODO.*spec" tests/
→ 11 matches

$ grep -r "TODO.*threshold" tests/
→ 8 matches

$ grep -r "TODO.*meeting" tests/
→ 11 matches
```

---

## 🎯 **For Presentation**

### Slide 1: The Problem
**Show this code:**
```python
# tests/integration/performance/test_performance_high_priority.py:157
# TODO: Uncomment after specs meeting
# assert p95 < THRESHOLD_P95_MS   ❌ DISABLED!
# assert p99 < THRESHOLD_P99_MS   ❌ DISABLED!
```

**Message:** Tests exist but can't enforce quality!

---

### Slide 2: Hardcoded Values
**Show this code:**
```python
# src/utils/validators.py:395
max_change_percent: float = 50.0  # ❌ Never confirmed!
```

**Message:** Critical values hardcoded without validation!

---

### Slide 3: Inconsistencies
**Show this:**
```python
# Code:
sensors_max: int = 100

# Config:
default_end: 109

# ❌ Mismatch!
```

**Message:** Code and config disagree!

---

## 📋 **Quick Reference**

### Most Critical Code Locations:

1. **ROI 50%:** `src/utils/validators.py:395`
2. **Performance thresholds:** `tests/integration/performance/test_performance_high_priority.py:146-170`
3. **NFFT validation:** `src/utils/validators.py:219-224`
4. **Frequency max:** `src/models/focus_server_models.py:48-49`
5. **Sensor range:** `src/utils/validators.py:140`
6. **Polling timeouts:** `src/utils/helpers.py:474`
7. **Default values:** `src/utils/helpers.py:508-513`
8. **Config validation:** `tests/integration/api/test_config_validation_high_priority.py:481`

---

## 🔧 **What Needs to Change**

### After Getting Specs:

**File:** `src/utils/validators.py`
```python
# Line 395 - BEFORE:
max_change_percent: float = 50.0  # Hardcoded

# Line 395 - AFTER:
max_change_percent: float = settings.ROI_MAX_CHANGE_PERCENT  # From specs!
```

**File:** `tests/integration/performance/test_performance_high_priority.py`
```python
# Line 157 - BEFORE:
# assert p95 < THRESHOLD_P95_MS   # Commented out

# Line 157 - AFTER:
assert p95 < settings.API_P95_THRESHOLD_MS  # From specs, enabled!
```

**File:** `src/utils/validators.py`
```python
# Line 213 - BEFORE:
if nfft <= 0:
    raise ValidationError("Must be positive")

# Line 213 - AFTER:
if nfft not in settings.VALID_NFFT_VALUES:
    raise ValidationError(f"NFFT must be one of {settings.VALID_NFFT_VALUES}")
```

---

## ✅ **Expected Outcome**

### With Specs:
- ✅ All 11 TODO comments resolved
- ✅ All 28 performance assertions enabled
- ✅ All hardcoded values moved to settings
- ✅ Code and config aligned
- ✅ Clear pass/fail criteria


