# Calculation Validation Tests

## 📊 Overview

This package contains 15 automated tests that validate mathematical calculations performed by the Focus Server.

**Status:** ✅ Fully Implemented  
**Xray Test Set:** PZ-CALC  
**Total Tests:** 15

---

## 🚀 Quick Start

### Run All Tests
```bash
pytest tests/integration/calculations/test_system_calculations.py -v
```

### Run by Category
```bash
# Frequency calculations (3 tests)
pytest tests/integration/calculations/ -k "Frequency" -v

# Time calculations (3 tests)  
pytest tests/integration/calculations/ -k "Time" -v

# Channel calculations (4 tests)
pytest tests/integration/calculations/ -k "Channel" -v

# Validation tests (2 tests)
pytest tests/integration/calculations/ -k "Validation" -v

# Performance tests (3 tests)
pytest tests/integration/calculations/ -k "Performance" -v
```

---

## 📋 Test List

### Frequency Calculations
1. ✅ `test_frequency_resolution_calculation` - PRR / NFFT
2. ✅ `test_frequency_bins_count_calculation` - NFFT / 2 + 1
3. ✅ `test_nyquist_frequency_calculation` - PRR / 2

### Time Calculations
4. ✅ `test_lines_dt_calculation` - (NFFT - Overlap) / PRR
5. ✅ `test_output_rate_calculation` - 1 / lines_dt
6. ✅ `test_time_window_duration_calculation` - NFFT / PRR

### Channel Calculations
7. ✅ `test_channel_count_calculation` - max - min + 1
8. ✅ `test_singlechannel_mapping_calculation` - SingleChannel mapping
9. ✅ `test_multichannel_mapping_calculation` - MultiChannel mapping
10. ✅ `test_stream_amount_calculation` - stream vs channel count

### Validation Tests
11. ✅ `test_fft_window_size_validation` - Power of 2 check
12. ✅ `test_overlap_percentage_validation` - Overlap documentation

### Performance Tests (Informational)
13. ✅ `test_data_rate_calculation` - Data throughput estimation
14. ✅ `test_memory_usage_estimation` - Memory per frame
15. ⏳ `test_spectrogram_dimensions_calculation` - Width × Height (TBD)

---

## ⚠️ Important Notes

### These Tests Document ACTUAL Behavior

**Philosophy:**
- Tests run against production system
- Failed tests = discrepancy between expected and actual
- Failed tests → open bug tickets for investigation

**DO NOT:**
- Change tests to pass without understanding why
- Assume failures are "wrong"

**DO:**
- Document actual behavior
- Open bug tickets with test output
- Update documentation when behavior is clarified

---

## 🐛 Expected Failures

Based on verification run (Job ID: 2-5756), expect these tests to fail:

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Frequency Bins | 257 | 32 | ❌ Fail |
| lines_dt | 0.256 sec | 0.039 sec | ❌ Fail |
| Output Rate | 3.9 lines/sec | 25.6 lines/sec | ❌ Fail |
| Stream Amount | 8 | 3 | ❌ Fail |
| MultiChannel Mapping | 1:1 | Grouped | ❌ Fail |

**These failures are EXPECTED and DOCUMENTED.**  
They indicate gaps in our understanding, not bugs per se.

---

## 📝 When a Test Fails

### Step 1: Capture Details
```bash
pytest tests/integration/calculations/test_system_calculations.py::TestFrequencyCalculations::test_frequency_bins_count_calculation -v --tb=long > test_failure.log
```

### Step 2: Open Bug Ticket

**Title:** `[Calculation] [TEST_NAME] - Actual behavior differs from expected`

**Description:**
```
Test: test_frequency_bins_count_calculation
Expected: 257 frequency bins (NFFT/2 + 1)
Actual: 32 frequency bins
Difference: 225 bins (87% less)

Possible causes:
1. Frequency decimation based on requested range
2. Different calculation formula
3. Optimization/compression

Request:
- Clarify expected behavior
- Document actual calculation formula
- Update test expectations if behavior is correct
```

### Step 3: Attach Evidence
- Test output log
- Job ID
- Request payload
- Response data

---

## 🔗 Related Documentation

- **Xray Ticket:** `docs/04_testing/XRAY_TICKET_CALCULATIONS_TESTS.md`
- **Verification Results:** `docs/04_testing/CALCULATION_VERIFICATION_RESULTS.md`
- **Detailed Test Plan:** `docs/04_testing/MISSING_CALCULATION_TESTS_DETAILED.md`
- **Source Analysis:** `docs/04_testing/CALCULATION_TESTS_SOURCE_ANALYSIS.md`

---

## 🎯 Success Criteria

### Definition of Done
- ✅ All 15 tests implemented
- ✅ Tests run successfully (even if they fail assertions)
- ✅ Failed tests documented with bug tickets
- ✅ Xray test cases created and linked
- ✅ Team understands actual vs expected behavior

### NOT Success Criteria
- ❌ All tests must pass (unrealistic without specs)
- ❌ Tests must match DSP textbook formulas (system may differ)

---

## 📊 Test Execution Report

After running tests, use this template:

```markdown
## Calculation Tests - Execution Report

**Date:** [DATE]
**Environment:** production
**Job IDs:** [JOB_IDS]

### Results
- Total: 15
- Passed: X
- Failed: Y
- Skipped: Z

### Bug Tickets Created
1. [PZ-XXXXX] - Frequency bins calculation discrepancy
2. [PZ-XXXXX] - lines_dt value unexpected
3. [PZ-XXXXX] - Channel grouping not documented

### Next Steps
- [ ] Review bug tickets with Product/Dev team
- [ ] Update documentation based on clarifications
- [ ] Adjust test expectations if behavior is correct
- [ ] Re-run tests to verify
```

---

**Owner:** QA Automation Team  
**Maintainer:** [YOUR_NAME]  
**Last Updated:** 29 אוקטובר 2025

