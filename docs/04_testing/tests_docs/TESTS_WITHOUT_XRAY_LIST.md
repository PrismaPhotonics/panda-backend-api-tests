# 📋 רשימת טסטים בלי Xray Markers

**תאריך:** 2025-01-27  
**סה"כ טסטים בלי Xray:** 67  
**מטרה:** לבדוק אילו טסטים צריך למחוק או להוסיף להם Xray markers

---

## 🚩 דופליקציות שזוהו

### 1. Sustained Load Tests - דופליקציה

| # | קובץ | טסט | Xray | סטטוס |
|---|------|-----|------|--------|
| 1 | `integration/load/test_sustained_load.py` | `test_api_sustained_load_1_hour` | ✅ PZ-14801, PZ-14800 | ✅ לשמור |
| 2 | `load/test_job_capacity_limits.py` | `test_sustained_load_1_hour` | ❌ אין | ⚠️ לבדוק/למחוק |

**המלצה:** למחוק את `test_sustained_load_1_hour` מ-`load/test_job_capacity_limits.py` כי יש טסט דומה עם Xray.

---

## 📊 רשימת כל הטסטים בלי Xray (67 טסטים)

### Infrastructure Tests (30 טסטים)

#### test_k8s_job_lifecycle.py (5 טסטים)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_k8s_job_creation_triggers_pod_spawn` | ⚠️ לבדוק אם יש Xray test דומה (PZ-13899 מופיע בקובץ) |
| 2 | `test_k8s_job_resource_allocation` | ⚠️ לבדוק אם יש Xray test דומה |
| 3 | `test_k8s_job_port_exposure` | ⚠️ לבדוק אם יש Xray test דומה |
| 4 | `test_k8s_job_cancellation_and_cleanup` | ⚠️ לבדוק אם יש Xray test דומה |
| 5 | `test_k8s_job_observability` | ⚠️ לבדוק אם יש Xray test דומה |

#### test_mongodb_monitoring_agent.py (27 טסטים)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_init` | טסט initialization |
| 2 | `test_connect_failure_retry` | ⚠️ לבדוק אם יש Xray test דומה |
| 3 | `test_disconnect` | ⚠️ לבדוק אם יש Xray test דומה |
| 4 | `test_ensure_connected_success` | ⚠️ לבדוק אם יש Xray test דומה |
| 5 | `test_list_databases` | ⚠️ לבדוק אם יש Xray test דומה |
| 6 | `test_list_databases_not_connected` | ⚠️ לבדוק אם יש Xray test דומה |
| 7 | `test_list_collections` | ⚠️ לבדוק אם יש Xray test דומה |
| 8 | `test_get_collection_stats` | ⚠️ לבדוק אם יש Xray test דומה |
| 9 | `test_count_documents` | ⚠️ לבדוק אם יש Xray test דומה |
| 10 | `test_find_documents` | ⚠️ לבדוק אם יש Xray test דומה |
| 11 | `test_get_health_status_healthy` | ⚠️ לבדוק אם יש Xray test דומה |
| 12 | `test_get_health_status_unhealthy` | ⚠️ לבדוק אם יש Xray test דומה |
| 13 | `test_get_metrics_summary` | ⚠️ לבדוק אם יש Xray test דומה |
| 14 | `test_create_alert` | ⚠️ לבדוק אם יש Xray test דומה |
| 15 | `test_register_alert_callback` | ⚠️ לבדוק אם יש Xray test דומה |
| 16 | `test_get_recent_alerts` | ⚠️ לבדוק אם יש Xray test דומה |
| 17 | `test_stop_monitoring` | ⚠️ לבדוק אם יש Xray test דומה |
| 18 | `test_monitoring_metrics_defaults` | ⚠️ לבדוק אם יש Xray test דומה |
| 19 | `test_alert_creation` | ⚠️ לבדוק אם יש Xray test דומה |
| 20 | `test_alert_level_values` | ⚠️ לבדוק אם יש Xray test דומה |

**הערה:** בקובץ יש Xray markers (PZ-13807, PZ-13809, PZ-13810, PZ-13898) - לבדוק אם הטסטים האלה כפולים.

#### test_system_behavior.py (1 טסט)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_focus_server_clean_startup` | ⚠️ לבדוק אם יש Xray test דומה (PZ-13873 מופיע בקובץ) |

#### test_external_connectivity.py (1 טסט)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_results` | Helper function - לבדוק אם צריך |

---

### Integration/API Tests (18 טסטים)

#### test_config_validation_high_priority.py (17 טסטים)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_invalid_canvas_height_negative` | ⚠️ לבדוק אם יש Xray test דומה |
| 2 | `test_invalid_canvas_height_zero` | ⚠️ לבדוק אם יש Xray test דומה |
| 3 | `test_missing_canvas_height_key` | ⚠️ לבדוק אם יש Xray test דומה |
| 4 | `test_invalid_frequency_range_min_greater_than_max` | ⚠️ לבדוק אם יש Xray test דומה |
| 5 | `test_frequency_range_exceeds_nyquist_limit` | ⚠️ לבדוק אם יש Xray test דומה |
| 6 | `test_invalid_channel_range_min_greater_than_max` | ⚠️ לבדוק אם יש Xray test דומה |
| 7 | `test_frequency_range_equal_min_max` | ⚠️ לבדוק אם יש Xray test דומה |
| 8 | `test_channel_range_exceeds_maximum` | ⚠️ לבדוק אם יש Xray test דומה |
| 9 | `test_channel_range_at_maximum` | ⚠️ לבדוק אם יש Xray test דומה |
| 10 | `test_valid_configuration_all_parameters` | ⚠️ לבדוק אם יש Xray test דומה |
| 11 | `test_valid_configuration_multiple_sensors` | ⚠️ לבדוק אם יש Xray test דומה |
| 12 | `test_valid_configuration_single_sensor` | ⚠️ לבדוק אם יש Xray test דומה |
| 13 | `test_valid_configuration_various_nfft_values` | ⚠️ לבדוק אם יש Xray test דומה |
| 14 | `test_invalid_nfft_exceeds_maximum` | ⚠️ לבדוק אם יש Xray test דומה |
| 15 | `test_invalid_nfft_not_power_of_2` | ⚠️ לבדוק אם יש Xray test דומה |
| 16 | `test_live_mode_valid_configuration` | ⚠️ לבדוק אם יש Xray test דומה |

**הערה:** בקובץ יש הרבה Xray markers (PZ-13878, PZ-13879, PZ-13548, PZ-13552, PZ-13555, וכו') - לבדוק אם הטסטים האלה כפולים.

#### test_config_validation_nfft_frequency.py (2 טסטים)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_nfft_variations` | ⚠️ לבדוק אם יש Xray test דומה |
| 2 | `test_configuration_resource_estimation` | ⚠️ לבדוק אם יש Xray test דומה |

#### test_dynamic_roi_adjustment.py (4 טסטים)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_roi_change_with_validation` | ⚠️ לבדוק אם יש Xray test דומה |
| 2 | `test_roi_change_should_not_affect_other_config_parameters` | ⚠️ Parametrized (20 cases) - לבדוק אם יש Xray test דומה |
| 3 | `test_roi_change_with_different_configs_should_not_affect_other_params` | ⚠️ Parametrized (8 cases) - לבדוק אם יש Xray test דומה |
| 4 | `test_different_rois_should_produce_same_data_size` | ⚠️ לבדוק אם יש Xray test דומה |

**הערה:** בקובץ יש הרבה Xray markers (PZ-13784-PZ-13799) - לבדוק אם הטסטים האלה כפולים.

#### test_health_check.py (1 טסט)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_ack_concurrent_requests` | ⚠️ לבדוק אם יש Xray test דומה (PZ-14026-PZ-14033 מופיעים בקובץ) |

---

### Integration/Data Quality Tests (6 טסטים)

#### test_consumer_creation_debug.py (3 טסטים)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_consumer_creation_timing` | ⚠️ Debug test - לבדוק אם צריך |
| 2 | `test_metadata_vs_waterfall_endpoints` | ⚠️ Debug test - לבדוק אם צריך |
| 3 | `test_waterfall_status_code_handling` | ⚠️ Debug test - לבדוק אם צריך |

#### test_investigate_consumer_creation.py (1 טסט)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_investigate_consumer_creation_issue` | ⚠️ Investigation test - לבדוק אם צריך |

#### test_negative_amplitude_values.py (2 טסטים)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_detect_negative_amplitude_values` | ⚠️ לבדוק אם יש Xray test דומה |
| 2 | `test_validate_waterfall_response_amplitude_ranges` | ⚠️ לבדוק אם יש Xray test דומה |

---

### Integration/Alerts Tests (1 טסט)

#### test_alert_logs_investigation.py (1 טסט)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_investigate_alert_logs` | ⚠️ Investigation test - לבדוק אם צריך |

---

### Integration/Security Tests (1 טסט)

#### test_data_exposure.py (1 טסט)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_error_message_security` | ⚠️ לבדוק אם יש Xray test דומה |

---

### Load Tests (3 טסטים)

#### test_job_capacity_limits.py (3 טסטים)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_extreme_concurrent_load` | ⚠️ לבדוק אם יש Xray test דומה (PZ-13986, PZ-14088 מופיעים בקובץ) |
| 2 | `test_heavy_config_concurrent` | ⚠️ לבדוק אם יש Xray test דומה |
| 3 | `test_sustained_load_1_hour` | 🚩 **דופליקציה!** יש גם `test_api_sustained_load_1_hour` עם Xray |

---

### UI Tests (2 טסטים)

#### test_button_interactions.py (1 טסט)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_button_interactions` | ⚠️ לבדוק אם יש Xray test דומה |

#### test_form_validation.py (1 טסט)
| # | טסט | הערה |
|---|-----|------|
| 1 | `test_form_validation` | ⚠️ לבדוק אם יש Xray test דומה |

---

## 📊 סיכום לפי קטגוריה

| קטגוריה | מספר טסטים |
|---------|-------------|
| **Infrastructure** | 30 |
| **Integration/API** | 18 |
| **Integration/Data Quality** | 6 |
| **Integration/Alerts** | 1 |
| **Integration/Security** | 1 |
| **Load** | 3 |
| **UI** | 2 |
| **סה"כ** | **67** |

---

## 🚩 דופליקציות ודמיון שזוהו

### 1. Sustained Load - דופליקציה
- ✅ `test_api_sustained_load_1_hour` (יש Xray) - לשמור
- ❌ `test_sustained_load_1_hour` (אין Xray) - למחוק

### 2. ROI Change Tests - לבדוק דמיון
- 4 טסטים בלי Xray בקובץ שיש בו הרבה Xray markers
- לבדוק אם הם כפולים לטסטים עם Xray

### 3. Config Validation Tests - לבדוק דמיון
- 17 טסטים בלי Xray בקובץ שיש בו הרבה Xray markers
- לבדוק אם הם כפולים לטסטים עם Xray

### 4. MongoDB Monitoring Agent Tests - לבדוק דמיון
- 27 טסטים בלי Xray בקובץ שיש בו Xray markers
- לבדוק אם הם כפולים לטסטים עם Xray

### 5. K8s Job Lifecycle Tests - לבדוק דמיון
- 5 טסטים בלי Xray בקובץ שיש בו Xray marker (PZ-13899)
- לבדוק אם הם כפולים לטסטים עם Xray

---

## ✅ המלצות

1. **למחוק מיד:**
   - `test_sustained_load_1_hour` מ-`load/test_job_capacity_limits.py` (דופליקציה)

2. **לבדוק ולמחוק אם לא רלוונטי:**
   - כל הטסטים בלי Xray markers (67 טסטים)
   - Investigation tests (2 טסטים)
   - Debug tests (3 טסטים)

3. **לבדוק דופליקציות:**
   - ROI change tests (4 טסטים)
   - Config validation tests (17 טסטים)
   - MongoDB monitoring tests (27 טסטים)
   - K8s job lifecycle tests (5 טסטים)

---

**תאריך:** 2025-01-27  
**גרסה:** 1.0

