# 🚩 טסטים כפולים/דומים שזוהו

**תאריך:** 2025-01-27  
**מטרה:** לזהות טסטים שבודקים את אותו הדבר

---

## 🔍 טסטים כפולים/דומים

### 1. ⚠️ Sustained Load Tests - דופליקציה

#### טסט 1: `test_api_sustained_load_1_hour`
- **מיקום:** `integration/load/test_sustained_load.py`
- **Xray:** ✅ PZ-14801, PZ-14800
- **מטרה:** API sustained load test - בודק API load
- **משך:** 5 דקות (CI) או 1 שעה (manual)

#### טסט 2: `test_sustained_load_1_hour`
- **מיקום:** `load/test_job_capacity_limits.py`
- **Xray:** ❌ אין
- **מטרה:** Job capacity sustained load - בודק job capacity limits
- **משך:** 1 שעה (soak test)

**הבדל:**
- טסט 1 בודק API load
- טסט 2 בודק job capacity limits

**המלצה:** 
- ✅ לשמור את `test_api_sustained_load_1_hour` (יש Xray)
- ⚠️ לבדוק אם `test_sustained_load_1_hour` צריך Xray marker או למחוק

---

### 2. ⚠️ ROI Change Tests - לבדוק דמיון

#### טסטים ב-`test_dynamic_roi_adjustment.py`:

1. `test_roi_change_with_validation` - ❌ אין Xray
   - בודק ROI change עם safety validation
   - **לבדוק:** האם זה דומה ל-`test_send_roi_change_command` (יש Xray)?

2. `test_roi_change_should_not_affect_other_config_parameters` - ❌ אין Xray
   - Parametrized test (20 test cases)
   - בודק ש-ROI change לא משפיע על config parameters אחרים
   - **לבדוק:** האם זה דומה לטסטים אחרים?

3. `test_roi_change_with_different_configs_should_not_affect_other_params` - ❌ אין Xray
   - Parametrized test (8 test cases)
   - בודק ש-ROI change עם configs שונים לא משפיע על parameters אחרים
   - **לבדוק:** האם זה דומה ל-`test_roi_change_should_not_affect_other_config_parameters`?

4. `test_different_rois_should_produce_same_data_size` - ❌ אין Xray
   - בודק ש-different ROIs מייצרים אותו data size
   - **לבדוק:** האם זה דומה לטסטים אחרים?

**המלצה:** לבדוק אם הטסטים האלה בודקים את אותו הדבר או דברים שונים.

---

### 3. ⚠️ Config Validation Tests - לבדוק דמיון

#### טסטים ב-`test_config_validation_high_priority.py`:

17 טסטים בלי Xray markers:
- `test_invalid_canvas_height_negative`
- `test_invalid_canvas_height_zero`
- `test_missing_canvas_height_key`
- `test_invalid_frequency_range_min_greater_than_max`
- `test_frequency_range_exceeds_nyquist_limit`
- `test_invalid_channel_range_min_greater_than_max`
- `test_frequency_range_equal_min_max`
- `test_channel_range_exceeds_maximum`
- `test_channel_range_at_maximum`
- `test_valid_configuration_all_parameters`
- `test_valid_configuration_multiple_sensors`
- `test_valid_configuration_single_sensor`
- `test_valid_configuration_various_nfft_values`
- `test_invalid_nfft_exceeds_maximum`
- `test_invalid_nfft_not_power_of_2`
- `test_live_mode_valid_configuration`

**המלצה:** לבדוק אם יש טסטים דומים עם Xray markers בקובץ הזה.

---

### 4. ⚠️ MongoDB Monitoring Agent Tests - לבדוק דמיון

27 טסטים בלי Xray markers ב-`test_mongodb_monitoring_agent.py`:
- `test_init`
- `test_connect_failure_retry`
- `test_disconnect`
- `test_ensure_connected_success`
- `test_list_databases`
- `test_list_databases_not_connected`
- `test_list_collections`
- `test_get_collection_stats`
- `test_count_documents`
- `test_find_documents`
- `test_get_health_status_healthy`
- `test_get_health_status_unhealthy`
- `test_get_metrics_summary`
- `test_create_alert`
- `test_register_alert_callback`
- `test_get_recent_alerts`
- `test_stop_monitoring`
- `test_monitoring_metrics_defaults`
- `test_alert_creation`
- `test_alert_level_values`

**המלצה:** לבדוק אם יש טסטים דומים עם Xray markers (PZ-13807, PZ-13809, PZ-13810, PZ-13898 מופיעים בקובץ).

---

### 5. ⚠️ K8s Job Lifecycle Tests - לבדוק דמיון

5 טסטים בלי Xray markers ב-`test_k8s_job_lifecycle.py`:
- `test_k8s_job_creation_triggers_pod_spawn`
- `test_k8s_job_resource_allocation`
- `test_k8s_job_port_exposure`
- `test_k8s_job_cancellation_and_cleanup`
- `test_k8s_job_observability`

**המלצה:** לבדוק אם יש טסטים דומים עם Xray markers (PZ-13899 מופיע בקובץ).

---

## 📋 סיכום

### דופליקציות ודמיון שזוהו:

1. ✅ **Sustained Load** - 2 טסטים דומים (אחד עם Xray, אחד בלי)
2. ⚠️ **ROI Change** - 4 טסטים בלי Xray (לבדוק דמיון)
3. ⚠️ **Config Validation** - 17 טסטים בלי Xray (לבדוק דמיון)
4. ⚠️ **MongoDB Monitoring** - 27 טסטים בלי Xray (לבדוק דמיון)
5. ⚠️ **K8s Job Lifecycle** - 5 טסטים בלי Xray (לבדוק דמיון)

---

## ✅ המלצות

1. **למחוק מיד:**
   - כל ה-summary tests (37 טסטים)

2. **לבדוק ולמחוק אם לא רלוונטי:**
   - כל הטסטים בלי Xray markers (67 טסטים)
   - Investigation tests (2 טסטים)
   - Debug tests (3 טסטים)

3. **לבדוק דופליקציות:**
   - `test_sustained_load_1_hour` vs `test_api_sustained_load_1_hour`
   - ROI change tests (4 טסטים)
   - Config validation tests (17 טסטים)

---

**תאריך:** 2025-01-27  
**גרסה:** 1.0

