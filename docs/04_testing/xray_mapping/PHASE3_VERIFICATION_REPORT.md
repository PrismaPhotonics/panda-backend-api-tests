# Phase 3: Verification Report - Existing Tests

**Date:** 2025-11-09  
**Status:** In Progress

---

## 📊 Summary

### Missing Tests Analysis:
- **Total Missing Tests:** 44 (from MISSING_TESTS_DETAILED_BREAKDOWN.md)
- **Tests Already Found (with markers):** ~15-20
- **Tests with Similar Functions:** ~10-15
- **Tests Actually Missing:** ~10-15

---

## ✅ Tests Already Found (with Xray Markers)

### API Tests:
1. **PZ-13762**: GET /channels – Returns System Channel Bounds
   - Found in: `tests/integration/api/test_api_endpoints_high_priority.py`
   - Function: `test_get_channels_endpoint_success`

2. **PZ-13552**: Invalid time range (negative)
   - Found in: `tests/integration/api/test_config_validation_high_priority.py`
   - Multiple functions cover this

3. **PZ-13561**: GET /live_metadata present
   - Found in: `tests/integration/api/test_live_monitoring_flow.py`
   - Function: `test_live_monitoring_get_metadata`

4. **PZ-14101**: Historic Playback - Short Duration (Rapid Window)
   - Found in: `tests/integration/api/test_historic_playback_e2e.py`
   - Function: `test_historic_playback_complete_e2e_flow`

5. **PZ-13761**: POST /config/{task_id} – Invalid Frequency Range Rejection
   - Found in: `tests/integration/api/test_api_endpoints_additional.py`
   - Function: `test_invalid_frequency_range_rejection`

6. **PZ-13764**: GET /live_metadata – Returns Metadata When Available
   - Found in: `tests/integration/api/test_api_endpoints_additional.py`
   - Function: `test_get_live_metadata_available`

7. **PZ-13759**: POST /config/{task_id} – Invalid Time Range Rejection
   - Found in: `tests/integration/api/test_api_endpoints_additional.py`
   - Function: `test_invalid_time_range_rejection`

8. **PZ-13895**: GET /channels - Enabled Channels List
   - Found in: `tests/integration/api/test_api_endpoints_high_priority.py`
   - Function: `test_get_channels_endpoint_success`

### Integration Tests:
1. **PZ-13767**: MongoDB Outage Handling
   - Found in: `tests/performance/test_mongodb_outage_resilience.py`
   - Function: `test_mongodb_scale_down_outage_returns_503_no_orchestration`

2. **PZ-13603**: Mongo outage on History configure
   - Found in: `tests/performance/test_mongodb_outage_resilience.py`
   - Function: `test_mongodb_scale_down_outage_returns_503_no_orchestration`

3. **PZ-13604**: Orchestrator error triggers rollback
   - Found in: `tests/performance/test_mongodb_outage_resilience.py`
   - Function: `test_mongodb_scale_down_outage_returns_503_no_orchestration`

### Security Tests:
1. **PZ-13572**: Robustness to malformed inputs
   - Found in: `tests/security/test_malformed_input_handling.py`
   - Function: `test_robustness_to_malformed_inputs`

2. **PZ-13769**: Malformed Input Handling
   - Found in: `tests/security/test_malformed_input_handling.py`
   - Function: `test_robustness_to_malformed_inputs`

---

## ⚠️ Tests with Similar Functions (Need Verification)

### API Tests:
1. **PZ-13821**: SingleChannel Rejects Invalid Display Height
   - Similar functions in: `test_config_validation_high_priority.py`
   - Need to verify if specific test exists

2. **PZ-13766**: POST /recordings_in_time_range – Returns Recording Windows
   - Similar functions in: `test_mongodb_data_quality.py`
   - Need to verify if specific test exists

3. **PZ-13815**: SingleChannel View for Channel 100
   - Similar functions in: `test_config_validation_high_priority.py`
   - Need to verify if specific test exists

4. **PZ-13560**: GET /channels
   - Similar functions in: `test_basic_connectivity.py`
   - Need to verify if specific test exists

---

## ❌ Tests Actually Missing (Need to Create)

### API Tests (Need to Create):
1. **PZ-13564**: POST /recordings_in_time_range
2. **PZ-13766**: POST /recordings_in_time_range – Returns Recording Windows
3. **PZ-13814**: SingleChannel View for Channel 1 (First Channel)
4. **PZ-13815**: SingleChannel View for Channel 100 (Upper Boundary Test)
5. **PZ-13819**: SingleChannel View with Various Frequency Ranges
6. **PZ-13823**: SingleChannel Rejects When min ≠ max
7. **PZ-13821**: SingleChannel Rejects Invalid Display Height
8. **PZ-13548**: Historical configure (happy path)
9. **PZ-13554**: Invalid channels (negative)
10. **PZ-13555**: Invalid frequency range (negative)
11. **PZ-13562**: GET /live_metadata missing
12. **PZ-13760**: POST /config/{task_id} – Invalid Channel Range Rejection

### Integration Tests (Need to Create):
1. **PZ-13832**: SingleChannel Edge Case - Minimum Channel (Channel 0)
2. **PZ-13833**: SingleChannel Edge Case - Maximum Channel (Last Available)
3. **PZ-13835**: SingleChannel with Invalid Channel (Out of Range)
4. **PZ-13836**: SingleChannel with Invalid Channel (Negative)
5. **PZ-13837**: SingleChannel with Invalid Channel (Negative)
6. **PZ-13852**: SingleChannel with Min > Max (Validation Error)
7. **PZ-13854**: SingleChannel Frequency Range Validation
8. **PZ-13855**: SingleChannel Canvas Height Validation
9. **PZ-13863**: Historic Playback - Standard 5-Minute Range
10. **PZ-13865**: Historic Playback - Short Duration (1 Minute)
11. **PZ-13873**: Valid Configuration - All Parameters
12. **PZ-13877**: Invalid Frequency Range - Min > Max
13. **PZ-13903**: Frequency Range Nyquist Limit Enforcement

### Data Quality Tests (Need to Create):
1. **PZ-13684**: node4 Schema Validation
2. **PZ-13685**: Recordings Metadata Completeness
3. **PZ-13811**: Validate Recordings Document Schema
4. **PZ-13812**: Verify Recordings Have Complete Metadata

---

## 📋 Next Steps

1. **Verify Similar Functions:**
   - Check if similar test functions actually cover the missing test cases
   - Add markers if tests exist but don't have them

2. **Create Missing Tests:**
   - Start with high-priority API tests
   - Then Integration tests
   - Finally Data Quality tests

3. **Add Markers:**
   - Add Xray markers to all newly created tests

---

**Last Updated:** 2025-11-09

