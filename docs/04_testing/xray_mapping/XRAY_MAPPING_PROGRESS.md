# 🔗 Xray Mapping - Progress Report

**Date:** October 27, 2025  
**Status:** In Progress

---

## ✅ Tests Already Mapped

### High Priority (Bugs Found):
1. **PZ-13984** → `test_time_range_validation_future_timestamps` ✅
2. **PZ-13985** → `live_metadata` fixture ✅
3. **PZ-13986** → `test_200_concurrent_jobs_target_capacity` ✅

### Time Range Validation:
4. **PZ-13869** → `test_time_range_validation_reversed_range` ✅
5. **PZ-13870** → Future timestamps (needs mapping)

### Configuration Validation:
6. **PZ-13876** → `test_config_validation_channels_out_of_range` ✅
7. **PZ-13877** → `test_config_validation_frequency_exceeds_nyquist` ✅
8. **PZ-13874** → `test_zero_nfft` ✅
9. **PZ-13875** → `test_negative_nfft` ✅

### API Endpoints:
10. **PZ-13895** → `test_get_channels_endpoint_success` ✅
11. **PZ-13762** → `test_get_channels_endpoint_success` ✅

---

## 📋 Tests Still Need Mapping

### From CSV:
- PZ-13909 - Historic Configuration Missing end_time
- PZ-13907 - Historic Configuration Missing start_time
- PZ-13906 - Low Throughput Configuration
- PZ-13905 - High Throughput Performance
- PZ-13904 - Resource Usage Estimation
- PZ-13903 - Frequency Range Nyquist (partially mapped)
- PZ-13901 - NFFT Values Validation
- PZ-13900 - SSH Access
- PZ-13899 - Kubernetes Connection
- PZ-13898 - MongoDB Connection
- PZ-13897 - GET /sensors
- PZ-13896 - Concurrent Task Limit
- PZ-13880 - Extreme Values
- PZ-13879 - Missing Required Fields
- PZ-13878 - Invalid View Type
- ... and ~40 more tests

---

## 🎯 Next Steps

1. Continue mapping based on keywords
2. Add markers to matching test functions
3. Create final mapping document
4. Test Xray upload

**Current Status:** 11/50+ tests mapped

