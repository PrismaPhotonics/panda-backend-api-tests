# 🔗 Xray Test Links - Direct Access

**Date:** October 27, 2025  
**Mapping Status:** ✅ 9 automation tests mapped to 11 Xray tests

---

## 📊 Summary

I added Xray markers to **9 automation test functions**, covering **11 Xray test keys**.

---

## 🔗 Direct Links to Xray Tests

### Bug Tests (Priority 1)

1. **PZ-13984** - Future Timestamp Validation Gap
   - 🔗 Jira: `https://prismaphotonics.atlassian.net/browse/PZ-13984`
   - 📁 File: `tests/integration/api/test_prelaunch_validations.py`
   - 🧪 Test: `test_time_range_validation_future_timestamps`
   - 📍 Line: 347

2. **PZ-13985** - LiveMetadata Missing Required Fields
   - 🔗 Jira: `https://prismaphotonics.atlassian.net/browse/PZ-13985`
   - 📁 File: `tests/conftest.py`
   - 🧪 Test: `live_metadata` (fixture)
   - 📍 Line: 641

3. **PZ-13986** - 200 Jobs Capacity Issue
   - 🔗 Jira: `https://prismaphotonics.atlassian.net/browse/PZ-13986`
   - 📁 File: `tests/load/test_job_capacity_limits.py`
   - 🧪 Test: `test_200_concurrent_jobs_target_capacity`
   - 📍 Line: 799

---

### Time Range Validation Tests

4. **PZ-13869** - Historic Playback - Invalid Time Range
   - 🔗 Jira: `https://prismaphotonics.atlassian.net/browse/PZ-13869`
   - 📁 File: `tests/integration/api/test_prelaunch_validations.py`
   - 🧪 Test: `test_time_range_validation_reversed_range`
   - 📍 Line: 425

---

### Configuration Validation Tests

5. **PZ-13876** - Invalid Channel Range - Min > Max
   - 🔗 Jira: `https://prismaphotonics.atlassian.net/browse/PZ-13876`
   - 📁 File: `tests/integration/api/test_prelaunch_validations.py`
   - 🧪 Test: `test_config_validation_channels_out_of_range`
   - 📍 Line: 508

6. **PZ-13877** - Invalid Frequency Range - Min > Max
   - 🔗 Jira: `https://prismaphotonics.atlassian.net/browse/PZ-13877`
   - 📁 File: `tests/integration/api/test_prelaunch_validations.py`
   - 🧪 Test: `test_config_validation_frequency_exceeds_nyquist` (multi-key)
   - 📍 Line: 575

7. **PZ-13903** - Frequency Range Nyquist Limit Enforcement
   - 🔗 Jira: `https://prismaphotonics.atlassian.net/browse/PZ-13903`
   - 📁 File: `tests/integration/api/test_prelaunch_validations.py`
   - 🧪 Test: `test_config_validation_frequency_exceeds_nyquist` (multi-key)
   - 📍 Line: 575

---

### NFFT Validation Tests

8. **PZ-13874** - Invalid NFFT - Zero Value
   - 🔗 Jira: `https://prismaphotonics.atlassian.net/browse/PZ-13874`
   - 📁 File: `tests/integration/api/test_config_validation_nfft_frequency.py`
   - 🧪 Test: `test_zero_nfft`
   - 📍 Line: 316

9. **PZ-13875** - Invalid NFFT - Negative Value
   - 🔗 Jira: `https://prismaphotonics.atlassian.net/browse/PZ-13875`
   - 📁 File: `tests/integration/api/test_config_validation_nfft_frequency.py`
   - 🧪 Test: `test_negative_nfft`
   - 📍 Line: 329

---

### API Endpoint Tests

10. **PZ-13895** - GET /channels - Enabled Channels List
    - 🔗 Jira: `https://prismaphotonics.atlassian.net/browse/PZ-13895`
    - 📁 File: `tests/integration/api/test_api_endpoints_high_priority.py`
    - 🧪 Test: `test_get_channels_endpoint_success` (multi-key)
    - 📍 Line: 40

11. **PZ-13762** - GET /channels - System Channel Bounds
    - 🔗 Jira: `https://prismaphotonics.atlassian.net/browse/PZ-13762`
    - 📁 File: `tests/integration/api/test_api_endpoints_high_priority.py`
    - 🧪 Test: `test_get_channels_endpoint_success` (multi-key)
    - 📍 Line: 40

---

## 📋 Quick Reference Table

| # | Xray Key | Jira Link | Test Function | File | Line |
|---|----------|-----------|---------------|------|------|
| 1 | PZ-13984 | [Link](https://prismaphotonics.atlassian.net/browse/PZ-13984) | test_time_range_validation_future_timestamps | test_prelaunch_validations.py | 347 |
| 2 | PZ-13985 | [Link](https://prismaphotonics.atlassian.net/browse/PZ-13985) | live_metadata | conftest.py | 641 |
| 3 | PZ-13986 | [Link](https://prismaphotonics.atlassian.net/browse/PZ-13986) | test_200_concurrent_jobs_target_capacity | test_job_capacity_limits.py | 799 |
| 4 | PZ-13869 | [Link](https://prismaphotonics.atlassian.net/browse/PZ-13869) | test_time_range_validation_reversed_range | test_prelaunch_validations.py | 425 |
| 5 | PZ-13876 | [Link](https://prismaphotonics.atlassian.net/browse/PZ-13876) | test_config_validation_channels_out_of_range | test_prelaunch_validations.py | 508 |
| 6 | PZ-13877 | [Link](https://prismaphotonics.atlassian.net/browse/PZ-13877) | test_config_validation_frequency_exceeds_nyquist | test_prelaunch_validations.py | 575 |
| 7 | PZ-13903 | [Link](https://prismaphotonics.atlassian.net/browse/PZ-13903) | test_config_validation_frequency_exceeds_nyquist | test_prelaunch_validations.py | 575 |
| 8 | PZ-13874 | [Link](https://prismaphotonics.atlassian.net/browse/PZ-13874) | test_zero_nfft | test_config_validation_nfft_frequency.py | 316 |
| 9 | PZ-13875 | [Link](https://prismaphotonics.atlassian.net/browse/PZ-13875) | test_negative_nfft | test_config_validation_nfft_frequency.py | 329 |
| 10 | PZ-13895 | [Link](https://prismaphotonics.atlassian.net/browse/PZ-13895) | test_get_channels_endpoint_success | test_api_endpoints_high_priority.py | 40 |
| 11 | PZ-13762 | [Link](https://prismaphotonics.atlassian.net/browse/PZ-13762) | test_get_channels_endpoint_success | test_api_endpoints_high_priority.py | 40 |

---

## 🎯 Many-to-One Mappings

### Test with 2 Xray Keys:
**File:** `test_prelaunch_validations.py:575`
```python
@pytest.mark.xray("PZ-13877", "PZ-13903")
def test_config_validation_frequency_exceeds_nyquist():
```
- Covers: PZ-13877 + PZ-13903 ✅

### Test with 2 Xray Keys:
**File:** `test_api_endpoints_high_priority.py:40`
```python
@pytest.mark.xray("PZ-13895", "PZ-13762")
def test_get_channels_endpoint_success():
```
- Covers: PZ-13895 + PZ-13762 ✅

---

## ✅ Complete List

**Total:** 9 automation test functions  
**Covering:** 11 Xray test keys  
**Many-to-One:** 2 tests cover multiple Xray keys  
**Ready:** All markers added ✅

---

**All links are ready to use! ✅**

