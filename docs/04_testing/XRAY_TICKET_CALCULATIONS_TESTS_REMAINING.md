# Remaining Test Cases PZ-CALC-003 through PZ-CALC-015
**To be appended to:** `XRAY_TICKET_CALCULATIONS_TESTS.md`  
**Starting after:** PZ-CALC-002

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
  "frequencyRange": { "min": 0 referencing="max": 500 },
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
- Frequency at Nyquist may anyway accepted (boundary case)
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

[Continuing with remaining 12 test cases...]

