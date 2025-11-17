# 🔗 TOP Code Links - Critical for Automation Specs
## Most Important Code Locations Blocking Clear Automation

**Priority:** Highest Impact → Lowest Impact  
**Purpose:** Quick reference for specs meeting  

---

## 🥇 **#1 MOST CRITICAL: Performance Assertions Disabled**

### 📍 **Location:**
```
tests/integration/performance/test_performance_high_priority.py
Lines: 146-170
```

### 💻 **Code:**
```python
# TODO: Update thresholds after specs meeting
THRESHOLD_P95_MS = 500   # ❌ Arbitrary
THRESHOLD_P99_MS = 1000  # ❌ Arbitrary

# TODO: Uncomment after specs meeting
# assert p95 < THRESHOLD_P95_MS   ❌ DISABLED!
# assert p99 < THRESHOLD_P99_MS   ❌ DISABLED!
```

### ❌ **Impact:**
- **28 performance tests** have no thresholds
- **Cannot detect degradation**
- Tests run but don't fail on poor performance

### ✅ **What We Need:**
- P95 latency threshold for `POST /config`
- P99 latency threshold for `POST /config`
- Max error rate percentage
- Thresholds for other API endpoints

---

## 🥈 **#2 CRITICAL: ROI Change 50% Hardcoded**

### 📍 **Location:**
```
src/utils/validators.py
Line: 395
```

### 💻 **Code:**
```python
def validate_roi_change_safety(
    current_min: int,
    current_max: int,
    new_min: int,
    new_max: int,
    max_change_percent: float = 50.0  # ❌ NEVER CONFIRMED!
) -> Dict[str, Any]:
```

### ❌ **Impact:**
- **6 ROI tests** depend on this unconfirmed value
- Could be blocking legitimate use cases
- Could be allowing dangerous changes

### ✅ **What We Need:**
- Confirmed max ROI change % (is 50% correct?)
- Cooldown period between changes?
- Different limits for live vs historic?

---

## 🥉 **#3 HIGH: NFFT Validation Too Permissive**

### 📍 **Location:**
```
src/utils/validators.py
Lines: 194-227
```

### 💻 **Code:**
```python
def validate_nfft_value(nfft: int) -> bool:
    if nfft <= 0:
        raise ValidationError("NFFT must be positive")
    
    is_power_of_2 = (nfft & (nfft - 1)) == 0
    if not is_power_of_2:
        warnings.warn(f"NFFT={nfft} not power of 2")  # ❌ Only warns!
    
    return True  # ✅ Always passes!
```

**vs Config File:**
```yaml
# config/environments.yaml:31-41
nfft:
  valid_values: [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
```

### ❌ **Impact:**
- Code accepts **any positive integer**
- Config defines valid list but **code ignores it**
- Could allow invalid NFFT values in production

### ✅ **What We Need:**
- Confirm valid NFFT values list
- Should code enforce the list (reject invalid)?
- Or just warn (current behavior)?

---

## 🔴 **#4 HIGH: Frequency Range No Maximum**

### 📍 **Location:**
```
src/models/focus_server_models.py
Lines: 46-57
```

### 💻 **Code:**
```python
class FrequencyRange(BaseModel):
    min: int = Field(..., ge=0)  # ✅ >= 0
    max: int = Field(..., ge=0)  # ✅ >= 0
    # ❌ NO UPPER LIMIT!
    
    @field_validator('max')
    def validate_frequency_range(cls, v: int, info):
        if info.data.get('min') and v < info.data['min']:
            raise ValueError('max frequency must be >= min frequency')
        return v
        # ❌ NO ABSOLUTE MAX CHECK!
```

### ❌ **Impact:**
- Accepts: `{"min": 0, "max": 999999}` ✅ Passes!
- Accepts: `{"min": 0, "max": 1}` ✅ Passes! (too narrow?)
- No protection against unreasonable values

### ✅ **What We Need:**
- Absolute max frequency (Hz)
- Absolute min frequency (Hz)
- Minimum range span (e.g., at least 10 Hz difference?)

**From Config:**
```yaml
# config/environments.yaml:17-20
constraints:
  frequency:
    max_hz: 1000
    min_hz: 0
    min_range_hz: 1
```
**But code doesn't enforce these!**

---

## 🟠 **#5 HIGH: Sensor Range No Min/Max ROI Size**

### 📍 **Location:**
```
src/utils/validators.py
Lines: 116-151
```

### 💻 **Code:**
```python
def validate_sensor_range(min_sensor: int, max_sensor: int, total_sensors: int):
    if min_sensor < 0 or max_sensor < 0:
        raise ValidationError("Non-negative")
    
    if max_sensor <= min_sensor:
        raise ValidationError("max > min")
    
    if max_sensor >= total_sensors:
        raise ValidationError("Exceeds total")
    
    # ❌ NO MINIMUM ROI SIZE CHECK!
    # Accepts: {"min": 0, "max": 1} - just 1 sensor!
    
    # ❌ NO MAXIMUM ROI SIZE CHECK!
    # Accepts: {"min": 0, "max": 2000} - all sensors!
    
    return True
```

### ❌ **Impact:**
- Could allow ROI with **1 sensor** (too small?)
- Could allow ROI with **all sensors** (performance impact?)
- No guidance on reasonable ROI sizes

### ✅ **What We Need:**
- Minimum ROI size (e.g., at least 10 sensors?)
- Maximum ROI size (e.g., max 1000 sensors?)

**From Config:**
```yaml
# config/environments.yaml:24-26
constraints:
  sensors:
    total_range: 2222
    # ❌ No min_roi_size
    # ❌ No max_roi_size
```

---

## 🟡 **#6 MEDIUM: API Response Time Arbitrary**

### 📍 **Location:**
```
tests/integration/api/test_api_endpoints_high_priority.py
Lines: 140-147
```

### 💻 **Code:**
```python
def test_get_channels_endpoint_response_time(self, focus_server_api):
    start_time = time.time()
    channels = focus_server_api.get_channels()
    end_time = time.time()
    
    response_time_ms = (end_time - start_time) * 1000
    
    # TODO: Update threshold after specs meeting
    MAX_RESPONSE_TIME_MS = 1000  # ❌ "Reasonable" guess!
    
    assert response_time_ms < MAX_RESPONSE_TIME_MS
```

### ❌ **Impact:**
- Using 1000ms as **arbitrary threshold**
- No SLA basis
- Could be too strict or too lenient

### ✅ **What We Need:**
- Max response time for `GET /channels`
- Max response time for `GET /metadata`
- Max response time for `GET /waterfall`
- Different thresholds for live vs historic?

---

## 🟡 **#7 MEDIUM: Config Validation Tests - No Assertions**

### 📍 **Location:**
```
tests/integration/api/test_config_validation_high_priority.py
Lines: 475-520
```

### 💻 **Code:**
```python
def test_frequency_range_equal_min_max(self):
    config_payload["frequencyRange"] = {"min": 100, "max": 100}
    response = focus_server_api.config_task(task_id, config_request)
    
    # TODO: Update assertion after specs meeting
    # For now, just log  ❌ NO ASSERTION!
    logger.info(f"Status: {response.status_code}")

def test_channel_range_equal_min_max(self):
    config_payload["channels"] = {"min": 7, "max": 7}
    
    # TODO: Update assertion after specs meeting  ❌ NO ASSERTION!
```

### ❌ **Impact:**
- Tests **exist and run**
- But **don't check anything**!
- No spec if `min==max` is valid

### ✅ **What We Need:**
- Is `frequency.min == frequency.max` valid? (Accept? Reject?)
- Is `channels.min == channels.max` valid? (SingleChannel mode?)
- Expected HTTP status for each case

---

## 📋 **BONUS: Default Values Mismatch**

### 📍 **Location:**
```
src/utils/helpers.py
Lines: 508-513
```

### 💻 **Code:**
```python
def generate_config_payload(
    sensors_min: int = 0,          # ❌ Config says: 11
    sensors_max: int = 100,        # ❌ Config says: 109
    freq_max: int = 500,           # ❌ Config says: 1000
    canvas_height: int = 1000,     # ❌ No spec!
):
```

**vs Config:**
```yaml
# config/environments.yaml
constraints:
  sensors:
    default_start: 11      # ≠ Code: 0
    default_end: 109       # ≠ Code: 100
  frequency:
    end_hz: 1000           # ≠ Code: 500
```

### ❌ **Impact:**
- **Code and config disagree!**
- Which is correct?

### ✅ **What We Need:**
- Confirm correct default values
- Update code to match config (or vice versa)

---

## 📊 **Summary Table: Priority & Impact**

| Priority | Issue | File | Lines | Tests Affected | Specs Needed |
|----------|-------|------|-------|----------------|--------------|
| 🥇 **#1** | Performance assertions disabled | `test_performance_high_priority.py` | 146-170 | 28 tests | P95/P99/Error rate thresholds |
| 🥈 **#2** | ROI 50% hardcoded | `validators.py` | 395 | 6 tests | Max ROI change %, cooldown |
| 🥉 **#3** | NFFT too permissive | `validators.py` | 194-227 | 6 tests | Valid NFFT list enforcement |
| 🔴 **#4** | Frequency no max | `focus_server_models.py` | 46-57 | 16 tests | Max/min freq, min range |
| 🟠 **#5** | Sensor range no limits | `validators.py` | 116-151 | 15 tests | Min/max ROI size |
| 🟡 **#6** | API time arbitrary | `test_api_endpoints_high_priority.py` | 140-147 | 3 tests | Response time SLAs |
| 🟡 **#7** | Config validation no assertions | `test_config_validation_high_priority.py` | 475-520 | 8 tests | Edge case behaviors |

**Total:** **82+ tests affected** by these 7 issues

---

## 🎯 **For Quick Meeting Reference**

### Open Files in IDE:
```bash
# In VSCode/IDE, open these files:
1. tests/integration/performance/test_performance_high_priority.py:146
2. src/utils/validators.py:395
3. src/utils/validators.py:194
4. src/models/focus_server_models.py:46
5. src/utils/validators.py:116
```

### Show This in Meeting:
**"We have 82+ tests blocked by 7 missing specs"**

Then show each file live, highlighting:
- Line 146-170: TODO comments + disabled assertions
- Line 395: Hardcoded 50%
- Line 194-227: NFFT warning only
- Line 46-57: No frequency max
- Line 116-151: No ROI size limits

---

## ✅ **After Meeting: Action Items**

### 1. Update Settings File:
```python
# config/settings.py (create if doesn't exist)

# Performance SLA (from meeting)
API_P95_THRESHOLD_MS = ???  # Get from team
API_P99_THRESHOLD_MS = ???  # Get from team
API_MAX_ERROR_RATE = ???    # Get from team

# ROI Constraints (from meeting)
ROI_MAX_CHANGE_PERCENT = ???  # Confirm 50% or different?
ROI_COOLDOWN_SECONDS = ???    # Get from team

# NFFT (from meeting)
VALID_NFFT_VALUES = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]

# Frequency (from meeting)
FREQUENCY_MAX_HZ = ???        # Get from team
FREQUENCY_MIN_HZ = ???        # Get from team
FREQUENCY_MIN_RANGE_HZ = ???  # Get from team

# Sensor Range (from meeting)
SENSOR_MIN_ROI_SIZE = ???     # Get from team
SENSOR_MAX_ROI_SIZE = ???     # Get from team
```

### 2. Enable Assertions:
```python
# tests/integration/performance/test_performance_high_priority.py:157
# BEFORE:
# assert p95 < THRESHOLD_P95_MS

# AFTER:
assert p95 < settings.API_P95_THRESHOLD_MS  # ✅ Enabled!
```

### 3. Enforce NFFT List:
```python
# src/utils/validators.py:213
# BEFORE:
if not is_power_of_2:
    warnings.warn(...)

# AFTER:
if nfft not in settings.VALID_NFFT_VALUES:
    raise ValidationError(f"NFFT must be one of {settings.VALID_NFFT_VALUES}")
```

---

## 📌 **Quick Commands**

### Count TODO comments:
```bash
grep -r "TODO.*spec" tests/ | wc -l
# Result: 11 matches

grep -r "TODO.*threshold" tests/ | wc -l
# Result: 8 matches
```

### Find disabled assertions:
```bash
grep -r "# assert" tests/ | grep -i "todo"
# Shows all commented-out assertions
```

### Check hardcoded values:
```bash
grep -r "= [0-9]\+\s*#.*hardcoded" src/
# Shows hardcoded numeric values
```

---

**This document provides direct file paths and line numbers for the most critical spec gaps!** 🎯

