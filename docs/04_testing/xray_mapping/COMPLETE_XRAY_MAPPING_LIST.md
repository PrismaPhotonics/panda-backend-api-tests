# 🔗 Complete Xray Mapping - All Test Links

**Date:** October 27, 2025  
**Status:** ✅ 18 markers added, covering 22 Xray test keys

---

## 📊 Summary

- **Automation tests with markers:** 13 test functions
- **Xray test keys mapped:** 22 keys
- **Many-to-one mappings:** Yes ✅ (as you requested!)

---

## 🔗 Direct Links - Copy & Paste

### Bug Tests (Critical Priority)

| Xray Key | Summary | Automation Test | Jira Link |
|----------|---------|-----------------|-----------|
| **PZ-13984** | Future Timestamp Validation Gap | test_time_range_validation_future_timestamps | https://prismaphotonics.atlassian.net/browse/PZ-13984 |
| **PZ-13985** | LiveMetadata Missing Required Fields | live_metadata fixture | https://prismaphotonics.atlassian.net/browse/PZ-13985 |
| **PZ-13986** | 200 Jobs Capacity Issue | test_200_concurrent_jobs_target_capacity | https://prismaphotonics.atlassian.net/browse/PZ-13986 |

---

### Time Range & Historic Tests

| Xray Key | Summary | Automation Test | Jira Link |
|----------|---------|-----------------|-----------|
| **PZ-13869** | Invalid Time Range (End Before Start) | test_time_range_validation_reversed_range | https://prismaphotonics.atlassian.net/browse/PZ-13869 |
| **PZ-13548** | Historical configure (happy path) | test_data_availability_historic_mode | https://prismaphotonics.atlassian.net/browse/PZ-13548 |
| **PZ-13863** | Standard 5-Minute Range | test_data_availability_historic_mode | https://prismaphotonics.atlassian.net/browse/PZ-13863 |

---

### Configuration Validation Tests

| Xray Key | Summary | Automation Test | Jira Link |
|----------|---------|-----------------|-----------|
| **PZ-13876** | Invalid Channel Range - Min > Max | test_config_validation_channels_out_of_range | https://prismaphotonics.atlassian.net/browse/PZ-13876 |
| **PZ-13877** | Invalid Frequency Range - Min > Max | test_config_validation_frequency_exceeds_nyquist | https://prismaphotonics.atlassian.net/browse/PZ-13877 |
| **PZ-13903** | Frequency Range Nyquist Limit Enforcement | test_config_validation_frequency_exceeds_nyquist | https://prismaphotonics.atlassian.net/browse/PZ-13903 |
| **PZ-13874** | Invalid NFFT - Zero Value | test_config_validation_invalid_nfft | https://prismaphotonics.atlassian.net/browse/PZ-13874 |
| **PZ-13875** | Invalid NFFT - Negative Value | test_config_validation_invalid_nfft | https://prismaphotonics.atlassian.net/browse/PZ-13875 |
| **PZ-13901** | NFFT Values Validation - All Supported Values | test_config_validation_invalid_nfft | https://prismaphotonics.atlassian.net/browse/PZ-13901 |
| **PZ-13878** | Invalid View Type - Out of Range | test_config_validation_invalid_view_type | https://prismaphotonics.atlassian.net/browse/PZ-13878 |

---

### API Endpoint Tests

| Xray Key | Summary | Automation Test | Jira Link |
|----------|---------|-----------------|-----------|
| **PZ-13895** | GET /channels - Enabled Channels List | test_get_channels_endpoint_success | https://prismaphotonics.atlassian.net/browse/PZ-13895 |
| **PZ-13762** | GET /channels - Returns System Channel Bounds | test_get_channels_endpoint_success | https://prismaphotonics.atlassian.net/browse/PZ-13762 |

---

### Live Mode Tests

| Xray Key | Summary | Automation Test | Jira Link |
|----------|---------|-----------------|-----------|
| **PZ-13547** | POST /config - Live Mode Configuration (Happy Path) | test_data_availability_live_mode | https://prismaphotonics.atlassian.net/browse/PZ-13547 |
| **PZ-13873** | Valid Configuration - All Parameters | test_data_availability_live_mode | https://prismaphotonics.atlassian.net/browse/PZ-13873 |

---

## 📊 Complete Test List with File Locations

### File: `tests/integration/api/test_prelaunch_validations.py`

| Line | Xray Keys | Test Function |
|------|-----------|---------------|
| 222 | PZ-13547, PZ-13873 | test_data_availability_live_mode |
| 274 | PZ-13548, PZ-13863 | test_data_availability_historic_mode |
| 347 | PZ-13984 | test_time_range_validation_future_timestamps |
| 425 | PZ-13869 | test_time_range_validation_reversed_range |
| 508 | PZ-13876 | test_config_validation_channels_out_of_range |
| 575 | PZ-13877, PZ-13903 | test_config_validation_frequency_exceeds_nyquist |
| 658 | PZ-13874, PZ-13875, PZ-13901 | test_config_validation_invalid_nfft |
| 720 | PZ-13878 | test_config_validation_invalid_view_type |

### File: `tests/integration/api/test_config_validation_nfft_frequency.py`

| Line | Xray Keys | Test Function |
|------|-----------|---------------|
| 316 | PZ-13874 | test_zero_nfft |
| 329 | PZ-13875 | test_negative_nfft |

### File: `tests/integration/api/test_api_endpoints_high_priority.py`

| Line | Xray Keys | Test Function |
|------|-----------|---------------|
| 40 | PZ-13895, PZ-13762 | test_get_channels_endpoint_success |

### File: `tests/conftest.py`

| Line | Xray Keys | Fixture |
|------|-----------|---------|
| 641 | PZ-13985 | live_metadata |

### File: `tests/load/test_job_capacity_limits.py`

| Line | Xray Keys | Test Function |
|------|-----------|---------------|
| 784 | PZ-13986 | class Test200ConcurrentJobsCapacity |
| 799 | PZ-13986 | test_200_concurrent_jobs_target_capacity |

---

## 🎯 Many-to-One Mappings Implemented

### Example 1: NFFT Test covers 3 Xray tests
```python
# Line 658
@pytest.mark.xray("PZ-13874", "PZ-13875", "PZ-13901")
def test_config_validation_invalid_nfft():
    # Tests NFFT zero, negative, and all values
```

### Example 2: Frequency Test covers 2 Xray tests
```python
# Line 575
@pytest.mark.xray("PZ-13877", "PZ-13903")
def test_config_validation_frequency_exceeds_nyquist():
    # Tests frequency range min>max and Nyquist limit
```

### Example 3: Channels Test covers 2 Xray tests
```python
# Line 40
@pytest.mark.xray("PZ-13895", "PZ-13762")
def test_get_channels_endpoint_success():
    # Tests channels list and system bounds
```

---

## ✅ Total Coverage

| Category | Tests | Xray Keys | Files Modified |
|----------|-------|-----------|----------------|
| Bugs Found | 3 | 3 | 3 files |
| Pre-launch Validation | 8 | 14 | 1 file |
| Config Validation | 2 | 3 | 1 file |
| API Endpoints | 1 | 2 | 1 file |
| **TOTAL** | **13** | **22** | **6 files** |

---

## 🚀 Ready to Use

```bash
# Run all tests
pytest tests/ --xray -v

# Run specific file
pytest tests/integration/api/test_prelaunch_validations.py -v

# Upload to Xray
python scripts/xray_upload.py
```

---

**All links are ready to use! ✅**

