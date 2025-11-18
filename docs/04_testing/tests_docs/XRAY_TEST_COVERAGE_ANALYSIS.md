# 📊 ניתוח כיסוי Xray - Focus Server Automation

**תאריך:** 2025-01-27  
**מטרה:** לבדוק כמה טסטים מקושרים ל-Xray

---

## 📈 סיכום

| מדד | מספר |
|-----|------|
| **סה"כ Xray markers** | **431** |
| **Unique Xray Test IDs** | **255** |
| **קבצים עם Xray markers** | **76** |
| **טסטים עם Xray markers (בלי unit)** | **329** |
| **סה"כ טסטים (בלי unit)** | **426** |
| **אחוז כיסוי Xray** | **77.23%** |

---

## 🔍 פירוט לפי קטגוריה

### Integration/API Tests

| קובץ | Xray Markers |
|------|--------------|
| `test_dynamic_roi_adjustment.py` | 26 |
| `test_config_validation_high_priority.py` | 18 |
| `test_singlechannel_view_mapping.py` | 26 |
| `test_health_check.py` | 8 |
| `test_prelaunch_validations.py` | 13 |
| `test_api_endpoints_high_priority.py` | 9 |
| `test_api_endpoints_additional.py` | 14 |
| `test_configure_endpoint.py` | 13 |
| `test_config_task_endpoint.py` | 8 |
| `test_task_metadata_endpoint.py` | 8 |
| `test_waterfall_endpoint.py` | 10 |
| `test_historic_playback_additional.py` | 8 |
| `test_config_validation_nfft_frequency.py` | 9 |
| `test_waterfall_view.py` | 2 |
| `test_orchestration_validation.py` | 3 |
| `test_nfft_overlap_edge_case.py` | 2 |
| `test_view_type_validation.py` | 4 |
| `test_live_streaming_stability.py` | 2 |
| `test_historic_playback_e2e.py` | 2 |
| `test_live_monitoring_flow.py` | 6 |

### Integration/Alerts Tests

| קובץ | Xray Markers |
|------|--------------|
| `test_alert_generation_positive.py` | 5 |
| `test_alert_generation_negative.py` | 8 |
| `test_alert_generation_edge_cases.py` | 8 |
| `test_alert_generation_load.py` | 6 |
| `test_alert_generation_performance.py` | 7 |
| `test_deep_alert_logs_investigation.py` | 1 |

### Infrastructure Tests

| קובץ | Xray Markers |
|------|--------------|
| `test_mongodb_monitoring_agent.py` | 28 |
| `test_k8s_job_lifecycle.py` | 6 |
| `test_system_behavior.py` | 5 |
| `test_pz_integration.py` | 5 |
| `test_external_connectivity.py` | 12 |
| `test_basic_connectivity.py` | 3 |
| `test_rabbitmq_connectivity.py` | 1 |

### Infrastructure/Resilience Tests

| קובץ | Xray Markers |
|------|--------------|
| `test_focus_server_pod_resilience.py` | 6 |
| `test_mongodb_pod_resilience.py` | 6 |
| `test_rabbitmq_pod_resilience.py` | 6 |
| `test_segy_recorder_pod_resilience.py` | 5 |
| `test_multiple_pods_resilience.py` | 4 |
| `test_pod_recovery_scenarios.py` | 3 |

### Data Quality Tests

| קובץ | Xray Markers |
|------|--------------|
| `test_mongodb_data_quality.py` | 7 |
| `test_mongodb_indexes_and_schema.py` | 9 |
| `test_mongodb_schema_validation.py` | 4 |
| `test_mongodb_recovery.py` | 2 |
| `test_recordings_classification.py` | 1 |
| `test_data_completeness.py` | 2 |
| `test_data_consistency.py` | 2 |
| `test_data_integrity.py` | 1 |

### Performance Tests

| קובץ | Xray Markers |
|------|--------------|
| `test_mongodb_outage_resilience.py` | 12 |
| `test_performance_high_priority.py` | 5 |
| `test_response_time.py` | 3 |
| `test_network_latency.py` | 3 |
| `test_resource_usage.py` | 3 |
| `test_database_performance.py` | 1 |
| `test_concurrent_performance.py` | 1 |
| `test_latency_requirements.py` | 3 |

### Load Tests

| קובץ | Xray Markers |
|------|--------------|
| `test_job_capacity_limits.py` | 13 |
| `test_load_profiles.py` | 4 |
| `test_peak_load.py` | 2 |
| `test_recovery_and_exhaustion.py` | 2 |
| `test_concurrent_load.py` | 1 |
| `test_sustained_load.py` | 2 |

### Security Tests

| קובץ | Xray Markers |
|------|--------------|
| `test_api_authentication.py` | 3 |
| `test_csrf_protection.py` | 1 |
| `test_data_exposure.py` | 2 |
| `test_https_enforcement.py` | 2 |
| `test_input_validation.py` | 3 |
| `test_rate_limiting.py` | 1 |
| `test_malformed_input_handling.py` | 2 |

### Error Handling Tests

| קובץ | Xray Markers |
|------|--------------|
| `test_http_error_codes.py` | 3 |
| `test_invalid_payloads.py` | 3 |
| `test_network_errors.py` | 2 |

### Calculations Tests

| קובץ | Xray Markers |
|------|--------------|
| `test_system_calculations.py` | 15 |

### E2E Tests

| קובץ | Xray Markers |
|------|--------------|
| `test_configure_metadata_grpc_flow.py` | 2 |

### Other Tests

| קובץ | Xray Markers |
|------|--------------|
| `test_extreme_configurations.py` | 1 |
| `test_rabbitmq_outage_handling.py` | 1 |

---

## 📊 סטטיסטיקות

### סה"כ Xray Markers: 431

### Unique Xray Test IDs: 255

**הערה:** מספר ה-markers גדול ממספר ה-IDs כי:
- טסט אחד יכול להיות מקושר למספר test IDs
- יש טסטים עם מספר markers (למשל: `@pytest.mark.xray("PZ-13787")` ו-`@pytest.mark.xray("PZ-13784")` באותו טסט)

---

## 🔍 דוגמאות לטסטים עם מספר Xray IDs

### דוגמה 1: טסט עם מספר markers
```python
@pytest.mark.xray("PZ-13787")
@pytest.mark.xray("PZ-13784")
@pytest.mark.xray("PZ-13785")
def test_send_roi_change_command(self, baby_analyzer_mq_client):
    # טסט אחד עם 3 Xray IDs
```

### דוגמה 2: טסט עם מספר IDs ב-marker אחד
```python
@pytest.mark.xray("PZ-13547", "PZ-13873", "PZ-13561")
def test_something():
    # טסט אחד עם 3 Xray IDs ב-marker אחד
```

---

## ✅ מסקנות

1. ✅ **431 Xray markers** נמצאו בקבצי הטסטים
2. ✅ **255 Unique Xray Test IDs** - כלומר יש 255 test cases שונים ב-Xray
3. ✅ **76 קבצים** מכילים Xray markers
4. ✅ **329 טסטים** (מתוך 426, בלי unit) מקושרים ל-Xray
5. ✅ **77.23% כיסוי Xray** - רוב הטסטים מקושרים ל-Xray

---

## 📊 פירוט כיסוי Xray

### טסטים עם Xray markers
- **329 טסטים** מתוך **426** (בלי unit tests)
- **אחוז כיסוי:** **77.23%**

### טסטים בלי Xray markers
- **97 טסטים** (426 - 329 = 97)
- **אחוז:** **22.77%**

**הסבר:**
- חלק מהטסטים בלי markers הם:
  - Helper functions
  - Summary functions
  - טסטים שעדיין לא מקושרים ל-Xray

---

## 📝 הערות

- **מספר ה-markers גדול ממספר ה-IDs** כי טסטים יכולים להיות מקושרים למספר test IDs
- **מספר ה-markers גדול ממספר הטסטים** כי:
  - טסט אחד יכול להיות מקושר למספר test IDs
  - יש טסטים עם מספר markers (למשל: `@pytest.mark.xray("PZ-13787")` ו-`@pytest.mark.xray("PZ-13784")` באותו טסט)
- **טסטים בלי Xray markers** - כנראה unit tests, helper functions, או טסטים שעדיין לא מקושרים ל-Xray

---

**תאריך:** 2025-01-27  
**גרסה:** 1.0

