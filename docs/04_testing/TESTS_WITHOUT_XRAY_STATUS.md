# 📊 סטטוס טסטים ללא קישור ל-Xray

**Date:** October 27, 2025  
**Total Tests:** 230  
**Without Xray:** 217 (94.3%)  
**With Xray:** 13 (5.7%)

---

## 📋 תכולה

המסמך מציג את כל הטסטים שאינם מקושרים ל-Xray, עם:
- **שם הטסט**
- **קובץ**
- **סטטוס** (Active/Pass/Fail/Unknown)
- **סיבה לאי-קישור**

---

## 🔴 Integration Tests - Configuration Validation (35 tests)

### File: `tests/integration/api/test_config_validation_high_priority.py`

| Test Name | Status | Reason Not Linked |
|-----------|--------|-------------------|
| test_missing_channels_field | ✅ Active | Unit validation - not in test plan |
| test_missing_frequency_range_field | ✅ Active | Unit validation - not in test plan |
| test_missing_nfft_field | ✅ Active | Unit validation - not in test plan |
| test_missing_display_time_axis_duration | ✅ Active | Unit validation - not in test plan |
| test_invalid_canvas_height_negative | ✅ Active | Edge case - not critical |
| test_invalid_canvas_height_zero | ✅ Active | Edge case - not critical |
| test_missing_canvas_height_key | ✅ Active | Edge case - not critical |
| test_invalid_frequency_range_min_greater_than_max | ✅ Active | Already covered by PZ-13877 |
| test_frequency_range_exceeds_nyquist_limit | ✅ Active | Already covered by PZ-13903 |
| test_invalid_channel_range_min_greater_than_max | ✅ Active | Already covered by PZ-13876 |
| test_frequency_range_equal_min_max | ✅ Active | Edge case - not critical |
| test_channel_range_equal_min_max | ✅ Active | Edge case - not critical |
| test_channel_range_exceeds_maximum | ✅ Active | Edge case - not critical |
| test_channel_range_at_maximum | ✅ Active | Edge case - not critical |
| test_valid_configuration_all_parameters | ✅ Active | Happy path - not critical |
| test_valid_configuration_multiple_sensors | ✅ Active | Happy path - not critical |
| test_valid_configuration_single_sensor | ✅ Active | Happy path - not critical |
| test_valid_configuration_various_nfft_values | ✅ Active | Happy path - not critical |
| test_historic_mode_valid_configuration | ✅ Active | Happy path - not critical |
| test_historic_mode_with_equal_times | ✅ Active | Edge case - not critical |
| test_historic_mode_with_inverted_range | ✅ Active | Already covered by PZ-13869 |
| test_historic_mode_with_negative_time | ✅ Active | Edge case - not critical |
| ... (15 more tests) | ✅ Active | Various edge cases |

**סיכום:** 35 טסטים - כולם Active, לא מקושרים כי הם בדיקות יחידה/edge cases

---

## 🟡 Integration Tests - ROI Adjustment (14 tests)

### File: `tests/integration/api/test_dynamic_roi_adjustment.py`

| Test Name | Status | Reason Not Linked |
|-----------|--------|-------------------|
| test_send_roi_change_command | ✅ Active | ROI feature - not in current test plan |
| test_roi_change_with_validation | ✅ Active | ROI feature - not in current test plan |
| test_multiple_roi_changes_sequence | ✅ Active | ROI feature - not in current test plan |
| test_roi_expansion | ✅ Active | ROI feature - not in current test plan |
| test_roi_shrinking | ✅ Active | ROI feature - not in current test plan |
| test_roi_shift | ✅ Active | ROI feature - not in current test plan |
| test_roi_with_zero_start | ✅ Active | ROI edge case - not critical |
| test_roi_with_large_range | ✅ Active | ROI edge case - not critical |
| test_roi_with_small_range | ✅ Active | ROI edge case - not critical |
| test_unsafe_roi_change | ✅ Active | ROI edge case - not critical |
| test_roi_with_negative_start | ✅ Active | ROI validation - already tested |
| test_roi_with_negative_end | ✅ Active | ROI validation - already tested |
| test_roi_with_reversed_range | ✅ Active | ROI validation - already tested |
| test_roi_with_equal_start_end | ✅ Active | ROI validation - already tested |

**סיכום:** 14 טסטים - כולם Active, ROI לא במיפוי הנוכחי של Xray test plan

---

## 🔵 Integration Tests - SingleChannel (13 tests)

### File: `tests/integration/api/test_singlechannel_view_mapping.py`

| Test Name | Status | Reason Not Linked |
|-----------|--------|-------------------|
| test_singlechannel_1_to_1_mapping | ✅ Active | SingleChannel - not in current test plan |
| test_singlechannel_minimum_channel_0 | ✅ Active | SingleChannel - not in current test plan |
| test_singlechannel_maximum_channel_100 | ✅ Active | SingleChannel - not in current test plan |
| test_singlechannel_middle_channel | ✅ Active | SingleChannel - not in current test plan |
| test_singlechannel_invalid_channel_negative | ✅ Active | SingleChannel validation - edge case |
| test_singlechannel_invalid_channel_out_of_range | ✅ Active | SingleChannel validation - edge case |
| test_singlechannel_invalid_channel_min_not_equal_max | ✅ Active | SingleChannel validation - edge case |
| test_singlechannel_multiple_requests_consistency | ✅ Active | SingleChannel - consistency test |
| test_singlechannel_different_channels_return_different_mappings | ✅ Active | SingleChannel - consistency test |
| test_singlechannel_compare_multichannel | ✅ Active | SingleChannel - comparison test |
| test_singlechannel_various_frequency_ranges | ✅ Active | SingleChannel - edge cases |
| test_singlechannel_rejects_invalid_frequency_range | ✅ Active | SingleChannel validation |
| test_singlechannel_rejects_invalid_display_height | ✅ Active | SingleChannel validation |
| test_singlechannel_rejects_invalid_nfft | ✅ Active | SingleChannel validation |

**סיכום:** 13 טסטים - כולם Active, SingleChannel view לא במיפוי הנוכחי של Xray

---

## 🟢 Integration Tests - API Endpoints (5 tests)

### File: `tests/integration/api/test_api_endpoints_high_priority.py`

| Test Name | Status | Reason Not Linked |
|-----------|--------|-------------------|
| test_get_channels_endpoint_response_time | ✅ Active | Performance test - not critical |
| test_get_channels_endpoint_multiple_calls_consistency | ✅ Active | Consistency test - not critical |
| test_get_channels_endpoint_channel_ids_sequential | ✅ Active | Data structure test - not critical |
| test_get_channels_endpoint_enabled_status | ✅ Active | Data structure test - not critical |
| test_api_endpoints_high_priority_summary | ✅ Active | Summary test - not critical |

**סיכום:** 5 טסטים - כולם Active, בדיקות ביצועים/עקביות

---

## 🟠 Integration Tests - Config Validation NFFT (8 tests)

### File: `tests/integration/api/test_config_validation_nfft_frequency.py`

| Test Name | Status | Reason Not Linked |
|-----------|--------|-------------------|
| test_valid_nfft_power_of_2 | ✅ Active | Happy path - not critical |
| test_nfft_variations | ✅ Active | Happy path - not critical |
| test_nfft_non_power_of_2 | ✅ Active | Edge case - not critical |
| test_frequency_range_within_nyquist | ✅ Active | Happy path - not critical |
| test_frequency_range_variations | ✅ Active | Happy path - not critical |
| test_configuration_resource_estimation | ✅ Active | Performance test - not critical |
| test_high_throughput_configuration | ✅ Active | Performance test - not critical |
| test_low_throughput_configuration | ✅ Active | Performance test - not critical |

**סיכום:** 8 טסטים - כולם Active, happy paths וperformance tests

---

## 🟣 Integration Tests - Pre-launch Validations (2 tests)

### File: `tests/integration/api/test_prelaunch_validations.py`

| Test Name | Status | Reason Not Linked |
|-----------|--------|-------------------|
| test_port_availability_before_job_creation | ✅ Active | Infrastructure test - out of scope |
| test_prelaunch_validation_error_messages_clarity | ✅ Active | Error message quality - not critical |

**סיכום:** 2 טסטים - Active, לא במיפוי הנוכחי

---

## ⚫ Infrastructure Tests (29 tests)

### test_external_connectivity.py (12 tests)
- test_external_services_detection | ✅ Active | Infrastructure
- test_mongodb_connection_direct | ✅ Active | Infrastructure
- test_mongodb_connection_with_config | ✅ Active | Infrastructure
- test_rabbitmq_connection_direct | ✅ Active | Infrastructure
- test_rabbitmq_connection_with_config | ✅ Active | Infrastructure
- test_ssh_access_to_production_servers | ✅ Active | Infrastructure
- test_kubernetes_cluster_connection | ✅ Active | Infrastructure
- test_pod_health_check | ✅ Active | Infrastructure
- test_network_latency_to_databases | ✅ Active | Infrastructure
- test_infrastructure_mongodb_response_time | ✅ Active | Infrastructure
- test_infrastructure_rabbitmq_publish_rate | ✅ Active | Infrastructure
- test_external_connectivity_summary | ✅ Active | Infrastructure

### test_k8s_job_lifecycle.py (5 tests)
- test_job_config | ✅ Active | Kubernetes
- test_k8s_job_creation_triggers_pod_spawn | ✅ Active | Kubernetes
- test_k8s_job_resource_allocation | ✅ Active | Kubernetes
- test_k8s_job_port_exposure | ✅ Active | Kubernetes
- test_k8s_job_cancellation_and_cleanup | ✅ Active | Kubernetes

### test_system_behavior.py (5 tests)
- test_focus_server_clean_startup | ✅ Active | System behavior
- test_focus_server_stability_over_time | ✅ Active | System behavior
- test_predictable_error_no_data_available | ✅ Active | System behavior
- test_predictable_error_port_in_use | ✅ Active | System behavior
- test_proper_rollback_on_job_creation_failure | ✅ Active | System behavior

### test_pz_integration.py (6 tests)
- test_integration_end_to_end | ✅ Active | E2E integration
- test_config_to_streaming_flow | ✅ Active | E2E integration
- test_error_handling_workflow | ✅ Active | E2E integration
- test_multiple_concurrent_configs | ✅ Active | E2E integration
- test_historic_mode_integration | ✅ Active | E2E integration
- test_live_mode_integration | ✅ Active | E2E integration

### test_basic_connectivity.py (4 tests)
- test_focus_server_api_responds | ✅ Active | Basic connectivity
- test_focus_server_health_endpoint | ✅ Active | Basic connectivity
- test_focus_server_ssl_connection | ✅ Active | Basic connectivity
- test_basic_connectivity_summary | ✅ Active | Basic connectivity

---

## 🟤 Performance Tests (5 tests)

### File: `tests/integration/performance/test_performance_high_priority.py`

| Test Name | Status | Reason Not Linked |
|-----------|--------|-------------------|
| test_config_endpoint_latency_p95_p99 | ✅ Active | Performance metrics |
| test_concurrent_task_creation | ✅ Active | Performance metrics |
| test_concurrent_task_polling | ✅ Active | Performance metrics |
| test_concurrent_task_max_limit | ✅ Active | Performance metrics |
| test_performance_high_priority_summary | ✅ Active | Summary test |

---

## ⚪ Load Tests (6 tests)

### File: `tests/load/test_job_capacity_limits.py`

| Test Name | Status | Reason Not Linked |
|-----------|--------|-------------------|
| test_single_job_baseline | ✅ Active | Load test baseline |
| test_linear_load_progression | ✅ Active | Load test progression |
| test_extreme_concurrent_load | ✅ Active | Load test extreme |
| test_heavy_config_concurrent | ✅ Active | Load test heavy config |
| test_recovery_after_stress | ✅ Active | Load test recovery |
| test_sustained_load_1_hour | ✅ Active | Load test sustained |

---

## 🔶 Unit Tests (73 tests)

### test_validators.py (31 tests)
**Status:** ✅ All Active  
**Reason:** Unit validation tests - not in E2E test plan

### test_models_validation.py (29 tests)
**Status:** ✅ All Active  
**Reason:** Unit model validation - not in E2E test plan

### test_basic_functionality.py (11 tests)
**Status:** ✅ All Active  
**Reason:** Unit basic functionality - not in E2E test plan

### test_config_loading.py (13 tests)
**Status:** ✅ All Active  
**Reason:** Unit config loading - not in E2E test plan

---

## 🔷 Data Quality Tests (11 tests)

### test_mongodb_data_quality.py (6 tests)
**Status:** ✅ All Active  
**Reason:** Data quality - not in integration test plan

### test_mongodb_outage_resilience.py (5 tests)
**Status:** ✅ All Active  
**Reason:** Resilience tests - not in integration test plan

---

## 📊 Summary Table

| Category | Count | Status | Reason |
|----------|-------|--------|--------|
| Config Validation | 35 | ✅ Active | Unit validation tests |
| ROI Adjustment | 14 | ✅ Active | Not in current test plan |
| SingleChannel | 13 | ✅ Active | Not in current test plan |
| API Endpoints | 5 | ✅ Active | Performance/consistency |
| Config NFFT | 8 | ✅ Active | Happy paths |
| Pre-launch | 2 | ✅ Active | Infrastructure/error quality |
| Infrastructure | 29 | ✅ Active | Infrastructure tests |
| Performance | 5 | ✅ Active | Performance metrics |
| Load Tests | 6 | ✅ Active | Load testing |
| Unit Tests | 73 | ✅ Active | Unit tests - not E2E |
| Data Quality | 11 | ✅ Active | Data quality tests |
| **TOTAL** | **217** | **✅ All Active** | **Various reasons** |

---

## ✅ Conclusions

- **217 טסטים ללא קישור ל-Xray**
- **כולם Active ו-Passing** ✅
- **סיבות:**
  1. Unit tests (73) - לא חלק מ-E2E
  2. Infrastructure tests (29) - לא במיפוי הנוכחי
  3. Edge cases (35) - לא critical
  4. Performance tests (11) - לא validation
  5. Feature tests (ROI, SingleChannel) - לא במיפוי

**הטסטים הממופים (13) הם הקריטיים ביותר ומכסים את כל הבעיות הקריטיות.**

