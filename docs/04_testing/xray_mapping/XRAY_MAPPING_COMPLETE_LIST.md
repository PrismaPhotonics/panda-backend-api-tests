# 🔗 Xray Test Mapping - Complete List

**Date:** October 27, 2025  
**Source:** Test plan (PZ-13756) by Roy Avrahami (Jira).csv  
**Total Tests in CSV:** ~50+ tests

---

## 📋 Mapping Strategy

I will map tests based on:
1. **Summary keywords** (historic, nfft, frequency, channels, etc.)
2. **Labels** (integration_test, performance_test, etc.)
3. **Known automation test files**

---

## 🎯 Tests to Map (First 30 from CSV)

| Xray Key | Summary | Expected File |
|----------|---------|---------------|
| PZ-13909 | Integration - Historic Configuration Missing end_time Field | test_prelaunch_validations.py |
| PZ-13907 | Integration - Historic Configuration Missing start_time Field | test_prelaunch_validations.py |
| PZ-13906 | Integration - Low Throughput Configuration Edge Case | test_config_validation_nfft_frequency.py |
| PZ-13905 | Performance - High Throughput Configuration Stress Test | test_job_capacity_limits.py |
| PZ-13904 | Integration - Configuration Resource Usage Estimation | test_config_validation_nfft_frequency.py |
| PZ-13903 | Integration - Frequency Range Nyquist Limit Enforcement | test_config_validation_nfft_frequency.py |
| PZ-13901 | Integration - NFFT Values Validation - All Supported Values | test_config_validation_nfft_frequency.py |
| PZ-13900 | Infrastructure - SSH Access to Production Servers | test_external_connectivity.py |
| PZ-13899 | Infrastructure - Kubernetes Cluster Connection and Pod Health Check | test_k8s_job_lifecycle.py |
| PZ-13898 | Infrastructure - MongoDB Direct Connection and Health Check | test_mongodb_data_quality.py |
| PZ-13897 | Integration - GET /sensors - Retrieve Available Sensors List | test_api_endpoints_high_priority.py |
| PZ-13896 | Performance - Concurrent Task Limit | test_job_capacity_limits.py |
| PZ-13895 | Integration - GET /channels - Enabled Channels List | test_api_endpoints_high_priority.py |
| PZ-13880 | Stress - Configuration with Extreme Values | test_config_validation_nfft_frequency.py |
| PZ-13879 | Integration - Missing Required Fields | test_prelaunch_validations.py |
| PZ-13878 | Integration - Invalid View Type - Out of Range | test_prelaunch_validations.py |
| PZ-13877 | Integration - Invalid Frequency Range - Min > Max | test_config_validation_nfft_frequency.py |
| PZ-13876 | Integration - Invalid Channel Range - Min > Max | test_prelaunch_validations.py |
| PZ-13875 | Integration - Invalid NFFT - Negative Value | test_config_validation_nfft_frequency.py |
| PZ-13874 | Integration - Invalid NFFT - Zero Value | test_config_validation_nfft_frequency.py |

---

## 📝 Action Plan

1. **For each test in the list above:**
   - Find the matching test function in automation
   - Add `@pytest.mark.xray("KEY")` marker
   - Document the mapping

2. **Create mapping file:**
   - JSON format for easy lookup
   - Include test key, summary, automation file, and test function name

3. **Update test files:**
   - Add markers to all matching tests

---

**Status:** Ready to implement

