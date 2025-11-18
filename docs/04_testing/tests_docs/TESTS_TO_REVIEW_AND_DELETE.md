# 🚩 טסטים לבדיקה ומחיקה - Focus Server Automation

**תאריך:** 2025-01-27  
**מטרה:** לזהות טסטים לא רלוונטיים, כפולים, או בלי Xray markers

---

## 📊 סיכום

| קטגוריה | מספר |
|---------|------|
| **Summary tests (לא טסטים אמיתיים)** | **37** |
| **Fixtures (test_config)** | **5** |
| **Helper functions (test_results, test_init)** | **3** |
| **טסטים אמיתיים בלי Xray** | **67** |
| **סה"כ לבדיקה** | **112** |

---

## ✅ טסטים שצריך למחוק (לא טסטים אמיתיים)

### 1. Summary Tests (37 טסטים) - למחוק

**אלה לא טסטים אמיתיים - הם summary functions:**

| קובץ | טסט |
|------|-----|
| `test_mongodb_indexes_and_schema.py` | `test_mongodb_indexes_schema_summary` |
| `test_mongodb_recovery.py` | `test_mongodb_recovery_summary` |
| `test_mongodb_schema_validation.py` | `test_mongodb_schema_validation_summary` |
| `test_recordings_classification.py` | `test_recordings_classification_summary` |
| `test_basic_connectivity.py` | `test_connectivity_summary` |
| `test_external_connectivity.py` | `test_all_services_summary` |
| `test_pz_integration.py` | `test_pz_integration_summary` |
| `test_rabbitmq_connectivity.py` | `test_rabbitmq_connectivity_summary` |
| `test_rabbitmq_outage_handling.py` | `test_rabbitmq_outage_handling_summary` |
| `test_focus_server_pod_resilience.py` | `test_focus_server_pod_resilience_summary` |
| `test_mongodb_pod_resilience.py` | `test_mongodb_pod_resilience_summary` |
| `test_multiple_pods_resilience.py` | `test_multiple_pods_resilience_summary` |
| `test_pod_recovery_scenarios.py` | `test_pod_recovery_scenarios_summary` |
| `test_rabbitmq_pod_resilience.py` | `test_rabbitmq_pod_resilience_summary` |
| `test_segy_recorder_pod_resilience.py` | `test_segy_recorder_pod_resilience_summary` |
| `test_api_endpoints_additional.py` | `test_api_endpoints_additional_summary` |
| `test_api_endpoints_high_priority.py` | `test_api_endpoints_high_priority_summary` |
| `test_configure_endpoint.py` | `test_configure_endpoint_summary` |
| `test_config_task_endpoint.py` | `test_config_task_endpoint_summary` |
| `test_config_validation_high_priority.py` | `test_config_validation_high_priority_summary` |
| `test_historic_playback_additional.py` | `test_historic_playback_additional_summary` |
| `test_historic_playback_e2e.py` | `test_historic_playback_e2e_summary` |
| `test_live_monitoring_flow.py` | `test_live_monitoring_summary` |
| `test_live_streaming_stability.py` | `test_live_streaming_stability_summary` |
| `test_nfft_overlap_edge_case.py` | `test_nfft_overlap_edge_case_summary` |
| `test_orchestration_validation.py` | `test_orchestration_validation_summary` |
| `test_singlechannel_view_mapping.py` | `test_module_summary` |
| `test_task_metadata_endpoint.py` | `test_task_metadata_endpoint_summary` |
| `test_view_type_validation.py` | `test_view_type_validation_summary` |
| `test_waterfall_endpoint.py` | `test_waterfall_endpoint_summary` |
| `test_waterfall_view.py` | `test_waterfall_view_summary` |
| `test_e2e_flow_summary.py` | `test_e2e_flow_summary` |
| `test_latency_requirements.py` | `test_latency_requirements_summary` |
| `test_performance_high_priority.py` | `test_performance_high_priority_summary` |
| `test_malformed_input_handling.py` | `test_malformed_input_handling_summary` |
| `test_extreme_configurations.py` | `test_extreme_configurations_summary` |

**המלצה:** למחוק את כל ה-summary tests - הם לא טסטים אמיתיים.

---

### 2. Fixtures (5 טסטים) - לא למחוק (fixtures תקינים)

**אלה fixtures, לא טסטים - תקין:**

| קובץ | Function |
|------|----------|
| `test_focus_server_pod_resilience.py` | `test_config` (fixture) |
| `test_mongodb_pod_resilience.py` | `test_config` (fixture) |
| `test_multiple_pods_resilience.py` | `test_config` (fixture) |
| `test_pod_recovery_scenarios.py` | `test_config` (fixture) |
| `test_rabbitmq_pod_resilience.py` | `test_config` (fixture) |

**המלצה:** לא למחוק - אלה fixtures תקינים.

---

### 3. Helper Functions (3 טסטים) - לבדוק

| קובץ | Function | הערה |
|------|----------|------|
| `test_external_connectivity.py` | `test_results` | Helper function - לבדוק אם צריך |
| `test_mongodb_monitoring_agent.py` | `test_init` | טסט initialization - לבדוק אם רלוונטי |

---

## 🚩 טסטים אמיתיים בלי Xray (67 טסטים) - לבדוק

### Infrastructure Tests (30 טסטים)

#### test_k8s_job_lifecycle.py (5 טסטים)
- `test_k8s_job_creation_triggers_pod_spawn` - ⚠️ לבדוק אם יש Xray test דומה
- `test_k8s_job_resource_allocation` - ⚠️ לבדוק אם יש Xray test דומה
- `test_k8s_job_port_exposure` - ⚠️ לבדוק אם יש Xray test דומה
- `test_k8s_job_cancellation_and_cleanup` - ⚠️ לבדוק אם יש Xray test דומה
- `test_k8s_job_observability` - ⚠️ לבדוק אם יש Xray test דומה

**המלצה:** לבדוק אם יש Xray tests דומים (PZ-13899 מופיע בקובץ).

#### test_mongodb_monitoring_agent.py (27 טסטים)
- `test_init` - טסט initialization
- `test_connect_failure_retry` - ⚠️ לבדוק אם יש Xray test דומה
- `test_disconnect` - ⚠️ לבדוק אם יש Xray test דומה
- `test_ensure_connected_success` - ⚠️ לבדוק אם יש Xray test דומה
- `test_list_databases` - ⚠️ לבדוק אם יש Xray test דומה
- `test_list_databases_not_connected` - ⚠️ לבדוק אם יש Xray test דומה
- `test_list_collections` - ⚠️ לבדוק אם יש Xray test דומה
- `test_get_collection_stats` - ⚠️ לבדוק אם יש Xray test דומה
- `test_count_documents` - ⚠️ לבדוק אם יש Xray test דומה
- `test_find_documents` - ⚠️ לבדוק אם יש Xray test דומה
- `test_get_health_status_healthy` - ⚠️ לבדוק אם יש Xray test דומה
- `test_get_health_status_unhealthy` - ⚠️ לבדוק אם יש Xray test דומה
- `test_get_metrics_summary` - ⚠️ לבדוק אם יש Xray test דומה
- `test_create_alert` - ⚠️ לבדוק אם יש Xray test דומה
- `test_register_alert_callback` - ⚠️ לבדוק אם יש Xray test דומה
- `test_get_recent_alerts` - ⚠️ לבדוק אם יש Xray test דומה
- `test_stop_monitoring` - ⚠️ לבדוק אם יש Xray test דומה
- `test_monitoring_metrics_defaults` - ⚠️ לבדוק אם יש Xray test דומה
- `test_alert_creation` - ⚠️ לבדוק אם יש Xray test דומה
- `test_alert_level_values` - ⚠️ לבדוק אם יש Xray test דומה

**המלצה:** לבדוק אם יש Xray tests דומים (PZ-13807, PZ-13809, PZ-13810, PZ-13898 מופיעים בקובץ).

#### test_system_behavior.py (1 טסט)
- `test_focus_server_clean_startup` - ⚠️ לבדוק אם יש Xray test דומה

**המלצה:** לבדוק אם יש Xray test דומה (PZ-13873 מופיע בקובץ).

---

### Integration/API Tests (18 טסטים)

#### test_config_validation_high_priority.py (17 טסטים)
- `test_invalid_canvas_height_negative` - ⚠️ לבדוק אם יש Xray test דומה
- `test_invalid_canvas_height_zero` - ⚠️ לבדוק אם יש Xray test דומה
- `test_missing_canvas_height_key` - ⚠️ לבדוק אם יש Xray test דומה
- `test_invalid_frequency_range_min_greater_than_max` - ⚠️ לבדוק אם יש Xray test דומה
- `test_frequency_range_exceeds_nyquist_limit` - ⚠️ לבדוק אם יש Xray test דומה
- `test_invalid_channel_range_min_greater_than_max` - ⚠️ לבדוק אם יש Xray test דומה
- `test_frequency_range_equal_min_max` - ⚠️ לבדוק אם יש Xray test דומה
- `test_channel_range_exceeds_maximum` - ⚠️ לבדוק אם יש Xray test דומה
- `test_channel_range_at_maximum` - ⚠️ לבדוק אם יש Xray test דומה
- `test_valid_configuration_all_parameters` - ⚠️ לבדוק אם יש Xray test דומה
- `test_valid_configuration_multiple_sensors` - ⚠️ לבדוק אם יש Xray test דומה
- `test_valid_configuration_single_sensor` - ⚠️ לבדוק אם יש Xray test דומה
- `test_valid_configuration_various_nfft_values` - ⚠️ לבדוק אם יש Xray test דומה
- `test_invalid_nfft_exceeds_maximum` - ⚠️ לבדוק אם יש Xray test דומה
- `test_invalid_nfft_not_power_of_2` - ⚠️ לבדוק אם יש Xray test דומה
- `test_live_mode_valid_configuration` - ⚠️ לבדוק אם יש Xray test דומה

**המלצה:** לבדוק אם יש Xray tests דומים (PZ-13878, PZ-13879, PZ-13548, PZ-13552, PZ-13555, PZ-13907, PZ-13909, PZ-14095, PZ-14097, PZ-14098, PZ-14099 מופיעים בקובץ).

#### test_config_validation_nfft_frequency.py (2 טסטים)
- `test_nfft_variations` - ⚠️ לבדוק אם יש Xray test דומה
- `test_configuration_resource_estimation` - ⚠️ לבדוק אם יש Xray test דומה

**המלצה:** לבדוק אם יש Xray tests דומים.

#### test_dynamic_roi_adjustment.py (4 טסטים)
- `test_roi_change_with_validation` - ⚠️ לבדוק אם יש Xray test דומה
- `test_roi_change_should_not_affect_other_config_parameters` - ⚠️ **Parametrized test** - לבדוק אם יש Xray test דומה
- `test_roi_change_with_different_configs_should_not_affect_other_params` - ⚠️ **Parametrized test** - לבדוק אם יש Xray test דומה
- `test_different_rois_should_produce_same_data_size` - ⚠️ לבדוק אם יש Xray test דומה

**המלצה:** לבדוק אם יש Xray tests דומים (PZ-13784-PZ-13799 מופיעים בקובץ).

#### test_health_check.py (1 טסט)
- `test_ack_concurrent_requests` - ⚠️ לבדוק אם יש Xray test דומה

**המלצה:** לבדוק אם יש Xray test דומה (PZ-14026-PZ-14033 מופיעים בקובץ).

---

### Integration/Data Quality Tests (6 טסטים)

#### test_consumer_creation_debug.py (3 טסטים)
- `test_consumer_creation_timing` - ⚠️ לבדוק אם יש Xray test דומה
- `test_metadata_vs_waterfall_endpoints` - ⚠️ לבדוק אם יש Xray test דומה
- `test_waterfall_status_code_handling` - ⚠️ לבדוק אם יש Xray test דומה

**המלצה:** לבדוק אם יש Xray tests דומים.

#### test_investigate_consumer_creation.py (1 טסט)
- `test_investigate_consumer_creation_issue` - ⚠️ **Investigation test** - לבדוק אם צריך

**המלצה:** זה investigation test - לבדוק אם צריך לשמור.

#### test_negative_amplitude_values.py (2 טסטים)
- `test_detect_negative_amplitude_values` - ⚠️ לבדוק אם יש Xray test דומה
- `test_validate_waterfall_response_amplitude_ranges` - ⚠️ לבדוק אם יש Xray test דומה

**המלצה:** לבדוק אם יש Xray tests דומים.

---

### Integration/Alerts Tests (1 טסט)

#### test_alert_logs_investigation.py (1 טסט)
- `test_investigate_alert_logs` - ⚠️ **Investigation test** - לבדוק אם צריך

**המלצה:** זה investigation test - לבדוק אם צריך לשמור.

---

### Integration/Security Tests (1 טסט)

#### test_data_exposure.py (1 טסט)
- `test_error_message_security` - ⚠️ לבדוק אם יש Xray test דומה

**המלצה:** לבדוק אם יש Xray test דומה.

---

### Load Tests (3 טסטים)

#### test_job_capacity_limits.py (3 טסטים)
- `test_extreme_concurrent_load` - ⚠️ לבדוק אם יש Xray test דומה
- `test_heavy_config_concurrent` - ⚠️ לבדוק אם יש Xray test דומה
- `test_sustained_load_1_hour` - ⚠️ **דופליקציה!** יש גם `test_api_sustained_load_1_hour` ב-integration/load

**המלצה:** 
- לבדוק אם יש Xray tests דומים (PZ-13986, PZ-14088 מופיעים בקובץ).
- `test_sustained_load_1_hour` - יש דופליקציה עם `test_api_sustained_load_1_hour` - לבדוק איזה לשמור.

---

### UI Tests (2 טסטים)

#### test_button_interactions.py (1 טסט)
- `test_button_interactions` - ⚠️ לבדוק אם יש Xray test דומה

#### test_form_validation.py (1 טסט)
- `test_form_validation` - ⚠️ לבדוק אם יש Xray test דומה

**המלצה:** לבדוק אם יש Xray tests דומים.

---

## 🔍 טסטים כפולים/דומים שזוהו

### 1. Sustained Load Tests - דופליקציה

| קובץ | טסט | Xray |
|------|-----|------|
| `integration/load/test_sustained_load.py` | `test_api_sustained_load_1_hour` | ✅ PZ-14801, PZ-14800 |
| `load/test_job_capacity_limits.py` | `test_sustained_load_1_hour` | ❌ אין |

**המלצה:** 
- `test_sustained_load_1_hour` ב-`load/test_job_capacity_limits.py` - למחוק או להוסיף Xray marker
- `test_api_sustained_load_1_hour` - לשמור (יש Xray)

---

## 📋 סיכום המלצות

### למחוק מיד (37 טסטים):
- ✅ כל ה-summary tests (`*_summary`)

### לבדוק ולמחוק אם לא רלוונטי (67 טסטים):
- ⚠️ כל הטסטים בלי Xray markers
- ⚠️ Investigation tests (לבדוק אם צריך)
- ⚠️ Debug tests (לבדוק אם צריך)

### לבדוק דופליקציות:
- ⚠️ `test_sustained_load_1_hour` - יש דופליקציה

---

**תאריך:** 2025-01-27  
**גרסה:** 1.0

