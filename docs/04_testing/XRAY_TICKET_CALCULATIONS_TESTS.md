# Calculation Validation Tests for Jira Xray
**Created:** 2025-10-29  
**Author:** Roy Avrahami (QA Automation Architect)  
**Status:** Ready for import to Jira Xray  
**Test Set:** PZ-CALC

---

## 📋 Test Cases Summary

| Test ID | Summary | Component | Priority | Status |
|---------|---------|-----------|----------|--------|
| **PZ-CALC-001** | Frequency Resolution Calculation Validation | api, calculations, frequency | High | ✅ Automated |
| **PZ-CALC-002** | Frequency Bins Count Calculation | api, calculations, frequency | High | ✅ Automated |
| **PZ-CALC-003** | Nyquist Frequency Limit Validation | api, calculations, frequency, validation | Medium | ✅ Automated |
| **PZ-CALC-004** | Time Resolution (lines_dt) Calculation | api, calculations, time | High | ✅ Automated |
| **PZ-CALC-005** | Output Rate Calculation | api, calculations, time, performance | Medium | ✅ Automated |
| **PZ-CALC-006** | Time Window Duration Calculation | api, calculations, time | Low | ✅ Automated |
| **PZ-CALC-007** | Channel Count Calculation | api, calculations, channels | High | ✅ Automated |
| **PZ-CALC-008** | SingleChannel Mapping Validation | api, calculations, channels, mapping | High | ✅ Automated |
| **PZ-CALC-009** | MultiChannel Mapping Validation | api, calculations, channels, mapping | High | ✅ Automated |
| **PZ-CALC-010** | Stream Amount Calculation | api, calculations, channels, streams | Medium | ✅ Automated |
| **PZ-CALC-011** | FFT Window Size (Power of 2) Validation | api, calculations, validation, nfft | High | ✅ Automated |
| **PZ-CALC-012** | Overlap Percentage Validation | api, calculations, validation, overlap | Low | ✅ Automated |
| **PZ-CALC-013** | Data Rate Calculation (Informational) | api, calculations, performance | Low | ✅ Automated |
| **PZ-CALC-014** | Memory Usage Estimation (Informational) | api, calculations, performance | Low | ✅ Automated |
| **PZ-CALC-015** | Spectrogram Dimensions Calculation | api, calculations, historic | Low | ⏳ To be implemented |

---

# Test Case PZ-CALC-001

## Summary
**Calculation Validation – Frequency Resolution Calculation**

## Test Type
Integration Test

## Priority
High

## Components/Labels
`focus-server`, `api`, `calculations`, `frequency`, `validation`

## Requirements
- FOCUS-CALC-FREQ (Frequency Calculation Requirements)

## Objective
Validate that the frequency resolution is calculated correctly from PRR (Pulse Repetition Rate) and NFFT parameters. Frequency resolution determines the smallest frequency difference that can be detected in the spectrogram. Incorrect calculation leads to inaccurate frequency analysis and poor data quality. This test documents the actual calculation formula used by the system.

**Formula:** `frequency_resolution = PRR / NFFT`

## Pre-Conditions
- **PC-CALC-001:** Focus Server is reachable and responsive
- **PC-CALC-002:** Valid API credentials configured
- **PC-CALC-003:** System configured for MultiChannel view (view_type=0)

## Test Data
```json
{
  "displayTimeAxisDuration": 30,
  "nfftSelection": 512,
  "displayInfo": {
    "height": 768
  },
  "channels": {
    "min": 1,
    "max": 8
  },
  "frequencyRange": {
    "min": 0,
    "max": 500
  },
  "start_time": null,
  "end_time": null,
  "view_type": "0"
}
```

**Assumed Parameters:**
- PRR (Pulse Repetition Rate): 1000 Hz
- NFFT: 512
- Expected frequency resolution: 1000 / 512 = 1.953 Hz

## Test Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | Payload with NFFT=512 | HTTP 200 OK, job_id returned |
| 2 | Extract frequencies_list from response | Response object | frequencies_list contains array of frequencies |
| 3 | Calculate actual frequency resolution | frequencies_list[1] - frequencies_list[0] | Actual resolution calculated |
| 4 | Calculate expected frequency resolution | PRR / NFFT = 1000 / 512 | Expected resolution = 1.953 Hz |
| 5 | Compare expected vs actual | Both resolution values | Values match within 10% tolerance OR discrepancy documented |
| 6 | Log calculation results | Expected and actual values | Results logged for analysis |

## Expected Result (overall)
Frequency resolution matches the formula `PRR / NFFT` within acceptable tolerance (10%), OR if different, the discrepancy is documented with calculated implied PRR or decimation factor. System may apply frequency decimation based on requested frequency range.

## Post-Conditions
- Job created in system (job_id exists)
- Metadata available for verification

## Assertions
- HTTP status code = 200
- `response.job_id` is not None
- `response.frequencies_list` is not empty
- Frequency resolution is positive and reasonable (0.1 Hz - 100 Hz)
- If resolution differs from expected, calculate and document implied PRR or decimation factor

## Environment
Any (Dev/Staging/Production)

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_frequency_resolution_calculation`  
**Test File:** `tests/integration/calculations/test_system_calculations.py`  
**Test Class:** `TestFrequencyCalculations`

## Execution Command
```bash
pytest tests/integration/calculations/test_system_calculations.py::TestFrequencyCalculations::test_frequency_resolution_calculation -v
```

## Related Issues
- PZ-CALC-BUG-001 (if frequency decimation detected)

---

# Test Case PZ-CALC-002

## Summary
**Calculation Validation – Frequency Bins Count Calculation**

## Test Type
Integration Test

## Priority
High

## Components/Labels
`focus-server`, `api`, `calculations`, `frequency`, `nfft`

## Requirements
- FOCUS-CALC-FREQ (Frequency Calculation Requirements)

## Objective
Validate that the number of frequency bins is calculated correctly from NFFT. For real-valued signals processed with FFT, only NFFT/2+1 frequency bins are unique due to symmetry. Incorrect bin count leads to wrong spectrogram dimensions and data interpretation errors.

**Formula:** `frequencies_amount = NFFT / 2 + 1`

## Pre-Conditions
- **PC-CALC-001:** Focus Server is reachable and responsive
- **PC-CALC-002:** Valid API credentials configured
- **PC-CALC-003:** System configured for MultiChannel view (view_type=0)

## Test Data

**Test Case 1: NFFT=256**
```json
{
  "displayTimeAxisDuration": 30,
  "nfftSelection": 256,
  "displayInfo": { "height": 768 },
  "channels": { "min": 1, "max": 8 },
  "frequencyRange": { "min": 0, "max": 500 },
  "view_type": "0"
}
```

**Test Case 2: NFFT=512**
```json
{
  "displayTimeAxisDuration": 30,
  "nfftSelection": 512,
  "displayInfo": { "height": 768 },
  "channels": { "min": 1, "max": 8 },
  "frequencyRange": { "min": 0, "max": 500 },
  "view_type": "0"
}
```

**Test Case 3: NFFT=1024**
```json
{
  "displayTimeAxisDuration": 30,
  "nfftSelection": 1024,
  "displayInfo": { "height": 768 },
  "channels": { "min": 1, "max": 8 },
  "frequencyRange": { "min": 0, "max": 500 },
  "view_type": "0"
}
```

**Test Case 4: NFFT=2048**
```json
{
  "displayTimeAxisDuration": 30,
  "nfftSelection": 2048,
  "displayInfo": { "height": 768 },
  "channels": { "min": 1, "max": 8 },
  "frequencyRange": { "min": 0, "max": 500 },
  "view_type": "0"
}
```

**Expected Values:**
- NFFT=256 → Expected: 129 bins (256/2 + 1)
- NFFT=512 → Expected: 257 bins (512/2 + 1)
- NFFT=1024 → Expected: 513 bins (1024/2 + 1)
- NFFT=2048 → Expected: 1025 bins (2048/2 + 1)

## Test Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure with NFFT=256 | Test Case 1 payload | HTTP 200 OK, job_id returned |
| 2 | Extract frequencies_amount | Response object | frequencies_amount value returned |
| 3 | Calculate expected bins for NFFT=256 | 256 / 2 + 1 | Expected = 129 |
| 4 | Compare expected vs actual for NFFT=256 | Both values | Values match OR discrepancy documented |
| 5 | POST /configure with NFFT=512 | Test Case 2 payload | HTTP 200 OK |
| 6 | Extract frequencies_amount for NFFT=512 | Response object | frequencies_amount value returned |
| 7 | Calculate expected bins for NFFT=512 | 512 / 2 + 1 | Expected = 257 |
| 8 | Compare expected vs actual for NFFT=512 | Both values | Values match OR discrepancy documented |
| 9 | POST /configure with NFFT=1024 | Test Case 3 payload | HTTP 200 OK |
| 10 | Extract frequencies_amount for NFFT=1024 | Response object | frequencies_amount value returned |
| 11 | Calculate expected bins for NFFT=1024 | 1024 / 2 + 1 | Expected = 513 |
| 12 | Compare expected vs actual for NFFT=1024 | Both values | Values match OR discrepancy documented |
| 13 | POST /configure with NFFT=2048 | Test Case 4 payload | HTTP 200 OK |
| 14 | Extract frequencies_amount for NFFT=2048 | Response object | frequencies_amount value returned |
| 15 | Calculate expected bins for NFFT=2048 | 2048 / 2 + 1 | Expected = 1025 |
| 16 | Compare expected vs actual for NFFT=2048 | Both values | Values match OR discrepancy documented |
| 17 | Log all results | All test cases | Results logged with discrepancies noted |

## Expected Result (overall)
For each NFFT value, `frequencies_amount` equals `NFFT / 2 + 1`. If actual values differ (e.g., due to frequency decimation based on requested frequency range), the discrepancy is documented with explanation and calculated decimation factor.

## Post-Conditions
- Multiple jobs created (one per NFFT value)
- All metadata available for verification

## Assertions
- HTTP status code = 200 for all NFFT values
- `frequencies_amount` is a positive integer for all NFFT values
- For NFFT=256: frequencies_amount = 129
- For NFFT=512: frequencies_amount = 257
- For NFFT=1024: frequencies_amount = 513
- For NFFT=2048: frequencies_amount = 1025
- OR: Document actual values and calculate decimation factor if different

## Environment
Any (Dev/Staging/Production)

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_frequency_bins_count_calculation`  
**Test File:** `tests/integration/calculations/test_system_calculations.py`  
**Test Class:** `TestFrequencyCalculations`

## Execution Command
```bash
pytest tests/integration/calculations/test_system_calculations.py::TestFrequencyCalculations::test_frequency_bins_count_calculation -v
```

## Related Issues
- PZ-CALC-BUG-001 (if frequency decimation detected)

---

# Test Case PZ-CALC-003

## Summary
**Calculation Validation – Nyquist Frequency Limit Validation**

## Test Type
Integration Test

## Priority
Medium

## Components/Labels
`focus-server`, `api`, `calculations`, `frequency`, `validation`, `nyquist`

## Requirements
- FOCUS-CALC-FREQ (Frequency Calculation Requirements)

## Objective
Validate that frequencies above the Nyquist limit are properly rejected or handled. Nyquist theorem states that maximum detectable frequency is PRR/2 to avoid aliasing. Incorrect handling leads to aliasing artifacts and corrupted frequency data.

**Formula:** `Nyquist_Frequency = PRR / 2`

**Assumed PRR:** 1000 Hz → Nyquist = 500 Hz

## Pre-Conditions
- **PC-CALC-001:** Focus Server is reachable and responsive
- **PC-CALC-002:** Valid API credentials configured
- **PC-CALC-003:** System configured for MultiChannel view (view_type=0)

## Test Data

**Test Case 1: Frequency Below Nyquist**
```json
{
  "displayTimeAxisDuration": 30,
  "nfftSelection": 512,
  "displayInfo": { "height": 768 },
  "channels": { "min": 1, "max": 8 },
  "frequencyRange": { "min": 0, "max": 400 },
  "view_type": "0"
}
```

**Test Case 2: Frequency At Nyquist**
```json
{
  "displayTimeAxisDuration": 30,
  "nfftSelection": 512,
  "displayInfo": { "height": 768 },
  "channels": { "min": 1, "max": 8 },
  "frequencyRange": { "min": 0, "max": 500 },
  "view_type": "0"
}
```

**Test Case 3: Frequency Above Nyquist**
```json
{
  "displayTimeAxisDuration": 30,
  "nfftSelection": 512,
  "displayInfo": { "height": 768 },
  "channels": { "min": 1, "max": 8 },
  "frequencyRange": { "min": 0, "max": 501 },
  "view_type": "0"
}
```

## Test Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure with frequency below Nyquist (400 Hz) | Test Case 1 payload | HTTP 200 OK, job_id returned |
| 2 | Verify job_id returned | Response object | job_id is not None |
| 3 | POST /configure with frequency at Nyquist (500 Hz) | Test Case 2 payload | HTTP 200 OK or 400 (if strict) |
| 4 | Verify response | Response object | Job created or clear error message |
| 5 | POST /configure with frequency above Nyquist (501 Hz) | Test Case 3 payload | HTTP 400 Bad Request with error message |
| 6 | Verify error details | Error response | Error mentions Nyquist limit or frequency constraint |
| 7 | Log all test results | All test cases | Results documented |

## Expected Result (overall)
- Frequencies below Nyquist (≤ PRR/2) are accepted
- Frequency at Nyquist may be accepted (boundary case)
- Frequencies above Nyquist (> PRR/2) are rejected with 400 Bad Request and clear error message mentioning frequency limit

**Note:** System may use configured maximum frequency (FrequencyMax=1000 Hz) instead of calculated Nyquist, which is acceptable.

## Post-Conditions
- Jobs created for valid frequencies
- Error recorded for invalid frequency

## Assertions
- Frequency 400 Hz: HTTP 200 OK
- Frequency 500 Hz: HTTP 200 OK (or 400 if system is strict)
- Frequency 501 Hz: HTTP 400 Bad Request
- Error message contains "frequency", "Nyquist", "limit", or "max" keyword
- System behavior is consistent and documented

## Environment
Any (Dev/Staging/Production)

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_nyquist_frequency_calculation`  
**Test File:** `tests/integration/calculations/test_system_calculations.py`  
**Test Class:** `TestFrequencyCalculations`

## Execution Command
```bash
pytest tests/integration/calculations/test_system_calculations.py::TestFrequencyCalculations::test_nyquist_frequency_calculation -v
```

## Related Issues
None

---

# Test Case PZ-CALC-004

## Summary
**Calculation Validation – Time Resolution (lines_dt) Calculation**

## Test Type
Integration Test

## Priority
High

## Components/Labels
`focus-server`, `api`, `calculations`, `time`, `lines_dt`, `resolution`

## Requirements
- FOCUS-CALC-TIME (Time Calculation Requirements)

## Objective
Validate that the time resolution between consecutive spectrogram lines (lines_dt) is calculated correctly. This value determines the temporal spacing between spectrogram lines and affects time axis rendering. Incorrect calculation leads to wrong time scaling and misinterpretation of temporal data.

**Formula:** `lines_dt = (NFFT - Overlap) / PRR`

**Assumed Parameters:**
- NFFT = 512
- Overlap = 256 samples (50% overlap)
- PRR = 1000 Hz
- Expected: (512 - 256) / 1000 = 0.256 seconds

## Pre-Conditions
- **PC-CALC-001:** Focus Server is reachable and responsive
- **PC-CALC-002:** Valid API credentials configured
- **PC-CALC-003:** System configured for MultiChannel view (view_type=0)

## Test Data
```json
{
  "displayTimeAxisDuration": 30,
  "nfftSelection": 512,
  "displayInfo": {
    "height": 768
  },
  "channels": {
    "min": 1,
    "max": 8
  },
  "frequencyRange": {
    "min": 0,
    "max": 500
  },
  "start_time": null,
  "end_time": null,
  "view_type": "0"
}
```

## Test Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | Payload with NFFT=512 | HTTP 200 OK, job_id returned |
| 2 | Extract lines_dt from response | Response object | lines_dt value returned (float) |
| 3 | Calculate expected lines_dt | (512 - 256) / 1000 | Expected = 0.256 seconds |
| 4 | Compare expected vs actual | Both values | Values match within 10% tolerance |
| 5 | Calculate implied PRR if different | Actual lines_dt | Implied PRR = (NFFT - Overlap) / actual_lines_dt |
| 6 | Document discrepancy if exists | Expected, actual, implied PRR | Discrepancy and possible causes logged |
| 7 | Log calculation results | All values | Results logged for analysis |

## Expected Result (overall)
`lines_dt` matches the formula `(NFFT - Overlap) / PRR` within 10% tolerance. If different, calculate and document implied PRR value or time compression/decimation factor. Actual value may differ if system uses different overlap percentage or PRR.

## Post-Conditions
- Job created in system
- lines_dt value available for verification

## Assertions
- HTTP status code = 200
- `response.lines_dt` is a positive float
- `response.lines_dt` > 0.001 seconds (minimum reasonable value)
- `response.lines_dt` < 10 seconds (maximum reasonable value)
- Expected lines_dt = 0.256 seconds (±10% = 0.230 to 0.282 seconds)
- OR: Document actual value and calculate implied parameters

## Environment
Any (Dev/Staging/Production)

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_lines_dt_calculation`  
**Test File:** `tests/integration/calculations/test_system_calculations.py`  
**Test Class:** `TestTimeCalculations`

## Execution Command
```bash
pytest tests/integration/calculations/test_system_calculations.py::TestTimeCalculations::test_lines_dt_calculation -v
```

## Related Issues
- PZ-CALC-BUG-002 (if lines_dt discrepancy detected)

---

# Test Case PZ-CALC-005

## Summary
**Calculation Validation – Output Rate Calculation**

## Test Type
Integration Test

## Priority
Medium

## Components/Labels
`focus-server`, `api`, `calculations`, `time`, `performance`, `output-rate`

## Requirements
- FOCUS-CALC-TIME (Time Calculation Requirements)

## Objective
Validate that the output rate (spectrogram lines per second) is calculated correctly and is within reasonable bounds.

**Formula:** `output_rate = 1 / lines_dt = PRR / (NFFT - Overlap)`

## Pre-Conditions
- **PC-CALC-001:** Focus Server is reachable and responsive
- **PC-CALC-002:** Valid API credentials configured
- **PC-CALC-003:** System configured for MultiChannel view (view_type=0)

## Test Data
```json
{
  "displayTimeAxisDuration": 30,
  "nfftSelection": 512,
  "displayInfo": { "height": 768 },
  "channels": { "min": 1, "max": 8 },
  "frequencyRange": { "min": 0, "max": 500 },
  "view_type": "0"
}
```

## Test Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | Payload with NFFT=512 | HTTP 200 OK |
| 2 | Extract lines_dt | Response object | lines_dt value returned |
| 3 | Calculate output_rate | 1 / lines_dt | output_rate calculated |
| 4 | Validate bounds | Calculated value | 0.1 < output_rate < 1000 |
| 5 | Compare with expected | PRR/(NFFT-Overlap) with PRR=1000, Overlap=256 | ~3.906 lines/sec |
| 6 | Log results | All values | Results logged |

## Expected Result (overall)
Output rate is positive, within reasonable bounds, and aligns with formula within 20% tolerance, or discrepancy is documented with implied parameters.

## Post-Conditions
- Job exists, metrics recorded

## Assertions
- HTTP 200
- `lines_dt > 0`
- `0.1 < 1/lines_dt < 1000`

## Environment
Any (Dev/Staging/Production)

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_output_rate_calculation`  
**Test File:** `tests/integration/calculations/test_system_calculations.py`  
**Test Class:** `TestTimeCalculations`

## Execution Command
```bash
pytest tests/integration/calculations/test_system_calculations.py::TestTimeCalculations::test_output_rate_calculation -v
```

## Related Issues
- PZ-CALC-BUG-002 (if discrepancy detected)

---

# Test Case PZ-CALC-006

## Summary
**Calculation Validation – Time Window Duration Calculation**

## Test Type
Integration Test

## Priority
Low

## Components/Labels
`focus-server`, `api`, `calculations`, `time`

## Requirements
- FOCUS-CALC-TIME (Time Calculation Requirements)

## Objective
Validate that the FFT window duration matches expectations.

**Formula:** `time_window_duration = NFFT / PRR`

## Pre-Conditions
- **PC-CALC-001:** Focus Server is reachable

## Test Data
NFFT in {256, 512, 1024}, PRR assumed 1000 Hz

## Test Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure with NFFT=256 | nfft=256 payload | HTTP 200 |
| 2 | Read duration (if provided) | Response | ~0.256 sec |
| 3 | Repeat for NFFT=512 | nfft=512 payload | ~0.512 sec |
| 4 | Repeat for NFFT=1024 | nfft=1024 payload | ~1.024 sec |

## Expected Result (overall)
Duration correlates with NFFT/PRR, variances documented.

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_time_window_duration_calculation`  
**Test File:** `tests/integration/calculations/test_system_calculations.py`

---

# Test Case PZ-CALC-007

## Summary
**Calculation Validation – Channel Count Calculation**

## Test Type
Integration Test

## Priority
High

## Components/Labels
`focus-server`, `api`, `calculations`, `channels`

## Requirements
- FOCUS-CALC-CHAN (Channel Calculation Requirements)

## Objective
Validate that channel count equals `max - min + 1`.

## Test Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | channels: {min:1,max:8} | channel_amount = 8 |
| 2 | POST /configure | channels: {min:3,max:3} | channel_amount = 1 |

## Assertions
- `channel_amount == max-min+1`

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_channel_count_calculation`

---

# Test Case PZ-CALC-008

## Summary
**Calculation Validation – SingleChannel Mapping Validation**

## Priority
High

## Objective
In SingleChannel (view_type=1, min==max), validate 1:1 mapping and single stream.

## Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | view_type=1, channels {min:7,max:7} | HTTP 200 |
| 2 | Validate stream_amount | Response | stream_amount = 1 |
| 3 | Validate mapping | Response | one mapping entry, channel→stream index 0 |

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_singlechannel_mapping_calculation`

---

# Test Case PZ-CALC-009

## Summary
**Calculation Validation – MultiChannel Mapping Validation**

## Priority
High

## Objective
For MultiChannel (view_type=0), expected traditional 1:1 mapping (document discrepancies).

## Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | channels {min:1,max:8} | HTTP 200 |
| 2 | Validate mapping | Response | channel_to_stream_index has 8 distinct indices |

## Notes
If grouping detected (e.g., 3 streams), document as defect.

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_multichannel_mapping_calculation`

---

# Test Case PZ-CALC-010

## Summary
**Calculation Validation – Stream Amount Calculation**

## Priority
Medium

## Objective
Validate relationship `stream_amount == channel_amount` (document deviations).

## Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | channels {min:1,max:8} | stream_amount = 8 |
| 2 | POST /configure | channels {min:4,max:6} | stream_amount = 3 |

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_stream_amount_calculation`

---

# Test Case PZ-CALC-011

## Summary
**Validation – FFT Window Size (Power of 2) Validation**

## Priority
High

## Objective
Validate that only power-of-two NFFT values are accepted.

## Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | nfft=256/512/1024 | HTTP 200 |
| 2 | POST /configure | nfft=300/500/1000 | HTTP 400 |

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_fft_window_size_validation`

---

# Test Case PZ-CALC-012

## Summary
**Validation – Overlap Percentage Validation**

## Priority
Low

## Objective
Validate allowed overlap values (system may fix/derive overlap).

## Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | overlap=0/25/50/75% (if supported) | Valid ranges accepted |
| 2 | POST /configure | overlap=-10%/110% | Rejected 400 |

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_overlap_percentage_validation`

---

# Test Case PZ-CALC-013

## Summary
**Performance – Data Rate Calculation (Informational)**

## Priority
Low

## Objective
Estimate data rate: `data_rate = channels × freq_bins × output_rate × bytes_per_sample`.

## Assertions
- data_rate > 0 and within reasonable bounds for config

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_data_rate_calculation`

---

# Test Case PZ-CALC-014

## Summary
**Performance – Memory Usage Estimation (Informational)**

## Priority
Low

## Objective
Estimate memory per frame: `channels × freq_bins × bytes_per_sample`.

## Assertions
- memory_per_frame > 0 and below configured limits

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_memory_usage_estimation`

---

# Test Case PZ-CALC-015

## Summary
**Historic – Spectrogram Dimensions Calculation**

## Priority
Low

## Objective
Validate historic image dimensions: Width ≈ `duration / lines_dt`, Height = `frequencies_amount`.

## Steps

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Request historic with duration=60s | valid params | HTTP 200 |
| 2 | Validate dims | Response | width≈duration/lines_dt, height=frequencies_amount |

## Automation Status
✅ **Automated** with Pytest

**Test Function:** `test_spectrogram_dimensions_calculation`

---
