# 🔗 Complete Code & Test Links
## All 9 Examples with Direct Links to Code AND Tests

---

## **[P0] #1: ROI change limit - hardcoded 50%**

### 📝 **Code (Problem):**
```
vscode://file/C:/Projects/focus_server_automation/src/utils/validators.py:395
```
- **File:** `src/utils/validators.py`
- **Line:** 395
- **Function:** `validate_roi_change_safety()`
- **Issue:** `max_change_percent: float = 50.0` - hardcoded, no spec!

### 🧪 **Test (Uses This Code):**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_dynamic_roi_adjustment.py:475
```
- **File:** `tests/integration/api/test_dynamic_roi_adjustment.py`
- **Line:** 475
- **Test:** `test_unsafe_roi_change()`
- **What it tests:** ROI changes exceeding safe limits

### 📋 **Additional Related Tests:**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_dynamic_roi_adjustment.py:150
```
- Line 150: `test_roi_change_with_validation()`

```
vscode://file/C:/Projects/focus_server_automation/tests/unit/test_validators.py:1
```
- Unit tests for `validate_roi_change_safety()`

---

## **[P0] #2: Performance assertions disabled (P95/P99)**

### 📝 **Code (Problem):**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/performance/test_performance_high_priority.py:67
```
- **File:** `tests/integration/performance/test_performance_high_priority.py`
- **Line:** 67
- **Test:** `test_config_endpoint_latency_p95_p99()`
- **Issue:** P95/P99 thresholds hardcoded, assertions disabled

### 🧪 **Test (IS the problem):**
**Same as above** - this IS the test file with disabled assertions

### 📋 **All Performance Tests with Disabled Assertions:**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/performance/test_performance_high_priority.py:67
```
- Line 67: `test_config_endpoint_latency_p95_p99()`

```
vscode://file/C:/Projects/focus_server_automation/tests/integration/performance/test_performance_high_priority.py:175
```
- Line 175: `test_waterfall_endpoint_latency_p95()`

```
vscode://file/C:/Projects/focus_server_automation/tests/integration/performance/test_performance_high_priority.py:273
```
- Line 273: `test_concurrent_task_creation()`

```
vscode://file/C:/Projects/focus_server_automation/tests/integration/performance/test_performance_high_priority.py:378
```
- Line 378: `test_concurrent_task_polling()`

```
vscode://file/C:/Projects/focus_server_automation/tests/integration/performance/test_performance_high_priority.py:461
```
- Line 461: `test_concurrent_task_max_limit()`

---

## **[P1] #3: NFFT validation too permissive**

### 📝 **Code (Problem):**
```
vscode://file/C:/Projects/focus_server_automation/src/utils/validators.py:194
```
- **File:** `src/utils/validators.py`
- **Line:** 194
- **Function:** `validate_nfft_value()`
- **Issue:** Only warns for non-power-of-2, doesn't reject

### 🧪 **Test (Uses This Code):**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_spectrogram_pipeline.py:98
```
- **File:** `tests/integration/api/test_spectrogram_pipeline.py`
- **Line:** 98
- **Test:** `test_nfft_non_power_of_2()`
- **What it tests:** Non-power-of-2 NFFT values

### 📋 **Additional NFFT Tests:**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_spectrogram_pipeline.py:64
```
- Line 64: `test_valid_nfft_power_of_2()`

```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_spectrogram_pipeline.py:80
```
- Line 80: `test_nfft_variations()`

```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_spectrogram_pipeline.py:345
```
- Line 345: `test_zero_nfft()`

```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_spectrogram_pipeline.py:356
```
- Line 356: `test_negative_nfft()`

---

## **[P1] #4: Frequency range - no absolute max/min**

### 📝 **Code (Problem):**
```
vscode://file/C:/Projects/focus_server_automation/src/models/focus_server_models.py:46
```
- **File:** `src/models/focus_server_models.py`
- **Line:** 46
- **Model:** `FrequencyRange`
- **Issue:** No upper limit (Field ge=0 but no le=...)

### 🧪 **Test (Uses This Code):**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_spectrogram_pipeline.py:159
```
- **File:** `tests/integration/api/test_spectrogram_pipeline.py`
- **Line:** 159
- **Test:** `test_frequency_range_variations()`
- **What it tests:** Various frequency ranges

### 📋 **Additional Frequency Tests:**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_spectrogram_pipeline.py:127
```
- Line 127: `test_frequency_range_within_nyquist()`

```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_config_validation_high_priority.py:1
```
- Contains edge case tests for frequency range min==max

---

## **[P2] #5: Sensor range - no min/max ROI size**

### 📝 **Code (Problem):**
```
vscode://file/C:/Projects/focus_server_automation/src/utils/validators.py:116
```
- **File:** `src/utils/validators.py`
- **Line:** 116
- **Function:** `validate_sensor_range()`
- **Issue:** No check for minimum/maximum ROI size (1 sensor or 2222 both valid!)

### 🧪 **Test (Uses This Code):**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_config_validation_high_priority.py:416
```
- **File:** `tests/integration/api/test_config_validation_high_priority.py`
- **Line:** 416
- **Test:** `test_invalid_channel_range_min_greater_than_max()`
- **What it tests:** Invalid sensor/channel ranges

### 📋 **Additional Sensor Range Tests:**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_config_validation_high_priority.py:487
```
- Line 487: `test_channel_range_equal_min_max()` - edge case (min==max)

```
vscode://file/C:/Projects/focus_server_automation/tests/unit/test_validators.py:1
```
- Unit tests for sensor range validation

```
vscode://file/C:/Projects/focus_server_automation/tests/unit/test_models_validation.py:1
```
- Model validation tests including sensor ranges

---

## **[P2] #6: Polling helper - hardcoded timeouts**

### 📝 **Code (Problem):**
```
vscode://file/C:/Projects/focus_server_automation/src/utils/helpers.py:474
```
- **File:** `src/utils/helpers.py`
- **Line:** 474
- **Function:** `poll_until()`
- **Issue:** `timeout_seconds=60`, `poll_interval=1.0` hardcoded (same for live & historic!)

### 🧪 **Test (Uses This Code):**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_live_monitoring_flow.py:184
```
- **File:** `tests/integration/api/test_live_monitoring_flow.py`
- **Line:** 184
- **Test:** `test_poll_waterfall_data_live_task()`
- **What it tests:** Polling waterfall data until available

### 📋 **Additional Polling Tests:**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_live_monitoring_flow.py:491
```
- Line 491: `test_rapid_waterfall_polling()` - rapid polling behavior

**Also used in historic playback tests:**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_historic_playback_flow.py:1
```
- Multiple tests use `poll_until()` helper

---

## **[P2] #7: Default payloads mismatch config**

### 📝 **Code (Problem):**
```
vscode://file/C:/Projects/focus_server_automation/src/utils/helpers.py:507
```
- **File:** `src/utils/helpers.py`
- **Line:** 507
- **Function:** `generate_config_payload()`
- **Issue:** Defaults (sensors_min=0, sensors_max=100) don't match config (11-109)

### 🧪 **Test (Uses This Code):**
**Used by MANY tests!** Every test that generates config payloads uses this helper.

**Primary examples:**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_live_monitoring_flow.py:1
```
- All live monitoring tests

```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_historic_playback_flow.py:1
```
- All historic playback tests

```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_dynamic_roi_adjustment.py:1
```
- All ROI adjustment tests

```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_spectrogram_pipeline.py:1
```
- All configuration tests

```
vscode://file/C:/Projects/focus_server_automation/tests/integration/performance/test_performance_high_priority.py:1
```
- All performance tests

### 📋 **Config Reference:**
```
vscode://file/C:/Projects/focus_server_automation/config/environments.yaml:24
```
- Line 24: Shows correct defaults (sensors 11-109, not 0-100)

---

## **[P3] #8: Config validation tests with TODO/no assertions**

### 📝 **Code (Problem):**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_config_validation_high_priority.py:475
```
- **File:** `tests/integration/api/test_config_validation_high_priority.py`
- **Line:** 475
- **Test:** `test_frequency_range_equal_min_max()`
- **Issue:** TODO comment, no assertion!

### 🧪 **Test (IS the problem):**
**Same as above** - this IS the test with missing assertions

### 📋 **All Tests with TODO/Missing Assertions:**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_config_validation_high_priority.py:475
```
- Line 475: `test_frequency_range_equal_min_max()` - TODO, no assertion

```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_config_validation_high_priority.py:487
```
- Line 487: `test_channel_range_equal_min_max()` - TODO, no assertion

**Other tests in this file that may need spec clarification:**
```
vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_config_validation_high_priority.py:1
```
- View entire file for context

---

## **[P3] #9: MongoDB outage resilience (behavior unclear)**

### 📝 **Code (Problem):**
```
vscode://file/C:/Projects/focus_server_automation/tests/performance/test_mongodb_outage_resilience.py:157
```
- **File:** `tests/performance/test_mongodb_outage_resilience.py`
- **Line:** 157
- **Test:** `test_mongodb_scale_down_outage_returns_503_no_orchestration()`
- **Issue:** Expected HTTP code unclear, SLA (5s) may be wrong (actual: 15s)

### 🧪 **Test (IS the problem):**
**Same as above** - this IS the test with unclear expected behavior

### 📋 **All MongoDB Outage Tests:**
```
vscode://file/C:/Projects/focus_server_automation/tests/performance/test_mongodb_outage_resilience.py:157
```
- Line 157: `test_mongodb_scale_down_outage_returns_503_no_orchestration()`

```
vscode://file/C:/Projects/focus_server_automation/tests/performance/test_mongodb_outage_resilience.py:217
```
- Line 217: `test_mongodb_network_block_outage_returns_503_no_orchestration()`

```
vscode://file/C:/Projects/focus_server_automation/tests/performance/test_mongodb_outage_resilience.py:283
```
- Line 283: `test_mongodb_outage_no_live_impact()`

```
vscode://file/C:/Projects/focus_server_automation/tests/performance/test_mongodb_outage_resilience.py:338
```
- Line 338: `test_mongodb_outage_logging_and_metrics()`

```
vscode://file/C:/Projects/focus_server_automation/tests/performance/test_mongodb_outage_resilience.py:391
```
- Line 391: `test_mongodb_outage_cleanup_and_restore()`

---

## 📊 **Summary Table - Quick Reference**

| # | Priority | Problem | Code Link | Test Link |
|---|----------|---------|-----------|-----------|
| 1 | 🔴 P0 | ROI 50% hardcoded | `validators.py:395` | `test_dynamic_roi_adjustment.py:475` |
| 2 | 🔴 P0 | Performance disabled | `test_performance_high_priority.py:67` | (same - IS test) |
| 3 | 🟠 P1 | NFFT permissive | `validators.py:194` | `test_spectrogram_pipeline.py:98` |
| 4 | 🟠 P1 | Frequency no max | `focus_server_models.py:46` | `test_spectrogram_pipeline.py:159` |
| 5 | 🟡 P2 | Sensor no limits | `validators.py:116` | `test_config_validation_high_priority.py:416` |
| 6 | 🟡 P2 | Polling hardcoded | `helpers.py:474` | `test_live_monitoring_flow.py:184` |
| 7 | 🟡 P2 | Defaults mismatch | `helpers.py:507` | (used by ALL tests) |
| 8 | ⚪ P3 | No assertions | `test_config_validation_high_priority.py:475` | (same - IS test) |
| 9 | ⚪ P3 | MongoDB unclear | `test_mongodb_outage_resilience.py:157` | (same - IS test) |

---

## 🎯 **How to Use These Links**

### **In PowerPoint Presentation:**
Each link is formatted as:
```
vscode://file/C:/Projects/focus_server_automation/<path>:<line>
```

### **To Open in Cursor:**
1. Click the link
2. Cursor opens automatically
3. Jumps to exact line
4. Ready to review/edit!

### **Manual Navigation:**
If links don't work:
1. Press `Ctrl+P` in Cursor
2. Copy file path (without vscode:// prefix)
3. Paste and press Enter
4. Press `Ctrl+G` and type line number

---

## 📝 **Copy-Paste Format for Meeting**

### **For PowerPoint (9 slides with dual links):**

**Slide 1:**
```
[P0] #1: ROI change limit - hardcoded 50%
  [view code →]   validators.py:395
  [view test →]   test_dynamic_roi_adjustment.py:475
```

**Slide 2:**
```
[P0] #2: Performance assertions disabled (P95/P99)
  [view code →]   test_performance_high_priority.py:67
  [view test →]   (same file - this IS the test)
```

**Slide 3:**
```
[P1] #3: NFFT validation too permissive
  [view code →]   validators.py:194
  [view test →]   test_spectrogram_pipeline.py:98
```

**Slide 4:**
```
[P1] #4: Frequency range - no absolute max/min
  [view code →]   focus_server_models.py:46
  [view test →]   test_spectrogram_pipeline.py:159
```

**Slide 5:**
```
[P2] #5: Sensor range - no min/max ROI size
  [view code →]   validators.py:116
  [view test →]   test_config_validation_high_priority.py:416
```

**Slide 6:**
```
[P2] #6: Polling helper - hardcoded timeouts
  [view code →]   helpers.py:474
  [view test →]   test_live_monitoring_flow.py:184
```

**Slide 7:**
```
[P2] #7: Default payloads mismatch config
  [view code →]   helpers.py:507
  [view test →]   (used by ALL config tests)
  [view config →] environments.yaml:24
```

**Slide 8:**
```
[P3] #8: Config validation tests with TODO/no assertions
  [view code →]   test_config_validation_high_priority.py:475
  [view test →]   (same - this IS the test with TODO)
```

**Slide 9:**
```
[P3] #9: MongoDB outage resilience (behavior unclear)
  [view code →]   test_mongodb_outage_resilience.py:157
  [view test →]   (same - this IS the test)
```

---

**Created:** 2025-10-22  
**Total Examples:** 9 (with code + test links for each)  
**Total Affected Tests:** 82+  
**Link Format:** Local `vscode://` URIs for Cursor IDE

