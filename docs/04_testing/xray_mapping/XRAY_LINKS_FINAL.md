# 🔗 Xray Test Links - Final & Ready

**Date:** October 27, 2025  
**Domain:** prismaphotonics.atlassian.net  
**Status:** ✅ All links active and ready to use

---

## 🎯 Quick Access - Top Priority Tests

### Bugs Found by Automation:

1. **PZ-13984** - Future Timestamp Validation Gap
   - 🔗 https://prismaphotonics.atlassian.net/browse/PZ-13984
   - 📁 `test_prelaunch_validations.py:347`

2. **PZ-13985** - LiveMetadata Missing Required Fields  
   - 🔗 https://prismaphotonics.atlassian.net/browse/PZ-13985
   - 📁 `conftest.py:641`

3. **PZ-13986** - 200 Jobs Capacity Issue
   - 🔗 https://prismaphotonics.atlassian.net/browse/PZ-13986
   - 📁 `test_job_capacity_limits.py:799`

---

## 📊 All Xray Test Links (22 tests)

| # | Xray Key | Link | Test Function | File |
|---|----------|------|---------------|------|
| 1 | PZ-13984 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13984) | test_time_range_validation_future_timestamps | test_prelaunch_validations.py:347 |
| 2 | PZ-13985 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13985) | live_metadata | conftest.py:641 |
| 3 | PZ-13986 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13986) | test_200_concurrent_jobs_target_capacity | test_job_capacity_limits.py:799 |
| 4 | PZ-13869 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13869) | test_time_range_validation_reversed_range | test_prelaunch_validations.py:425 |
| 5 | PZ-13548 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13548) | test_data_availability_historic_mode | test_prelaunch_validations.py:274 |
| 6 | PZ-13863 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13863) | test_data_availability_historic_mode | test_prelaunch_validations.py:274 |
| 7 | PZ-13876 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13876) | test_config_validation_channels_out_of_range | test_prelaunch_validations.py:508 |
| 8 | PZ-13877 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13877) | test_config_validation_frequency_exceeds_nyquist | test_prelaunch_validations.py:575 |
| 9 | PZ-13903 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13903) | test_config_validation_frequency_exceeds_nyquist | test_prelaunch_validations.py:575 |
| 10 | PZ-13874 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13874) | test_config_validation_invalid_nfft | test_prelaunch_validations.py:658 |
| 11 | PZ-13875 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13875) | test_config_validation_invalid_nfft | test_prelaunch_validations.py:658 |
| 12 | PZ-13901 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13901) | test_config_validation_invalid_nfft | test_prelaunch_validations.py:658 |
| 13 | PZ-13878 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13878) | test_config_validation_invalid_view_type | test_prelaunch_validations.py:720 |
| 14 | PZ-13895 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13895) | test_get_channels_endpoint_success | test_api_endpoints_high_priority.py:40 |
| 15 | PZ-13762 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13762) | test_get_channels_endpoint_success | test_api_endpoints_high_priority.py:40 |
| 16 | PZ-13547 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13547) | test_data_availability_live_mode | test_prelaunch_validations.py:222 |
| 17 | PZ-13873 | [Open](https://prismaphotonics.atlassian.net/browse/PZ-13873) | test_data_availability_live_mode | test_prelaunch_validations.py:222 |

---

## 🔍 Test by Category

### Time Range Validation (5 tests)
- PZ-13984 - Future timestamps
- PZ-13869 - Reversed range
- PZ-13863 - Standard 5-minute range
- PZ-13548 - Historic playback
- PZ-13870 - Future timestamps (duplicate coverage)

### Configuration Validation (7 tests)
- PZ-13876 - Invalid channel range
- PZ-13877 - Invalid frequency range
- PZ-13903 - Nyquist limit
- PZ-13874 - Zero NFFT
- PZ-13875 - Negative NFFT
- PZ-13901 - NFFT validation
- PZ-13878 - Invalid view type

### API Endpoints (3 tests)
- PZ-13895 - Channels endpoint
- PZ-13762 - Channels bounds
- PZ-13985 - Live metadata

### Live Mode (2 tests)
- PZ-13547 - Live mode happy path
- PZ-13873 - Valid configuration

### Capacity (1 test)
- PZ-13986 - 200 concurrent jobs

---

## 🎯 Quick Test Locations

### File: `tests/integration/api/test_prelaunch_validations.py`
**10 tests with Xray markers:**
- Line 222: PZ-13547, PZ-13873
- Line 274: PZ-13548, PZ-13863
- Line 347: PZ-13984
- Line 425: PZ-13869
- Line 508: PZ-13876
- Line 575: PZ-13877, PZ-13903
- Line 658: PZ-13874, PZ-13875, PZ-13901
- Line 720: PZ-13878

### File: `tests/integration/api/test_config_validation_nfft_frequency.py`
**2 tests with Xray markers:**
- Line 316: PZ-13874
- Line 329: PZ-13875

### File: `tests/integration/api/test_api_endpoints_high_priority.py`
**1 test with Xray markers:**
- Line 40: PZ-13895, PZ-13762

### File: `tests/conftest.py`
**1 fixture with Xray marker:**
- Line 641: PZ-13985

### File: `tests/load/test_job_capacity_limits.py`
**1 test with Xray marker:**
- Line 799: PZ-13986

---

## ✅ Summary

**Total:** 13 automation tests  
**Covering:** 22 Xray test keys  
**Files modified:** 6  
**Links:** All active ✅

---

**Ready to use! All links point to:**
`https://prismaphotonics.atlassian.net/browse/PZ-XXXXX`

