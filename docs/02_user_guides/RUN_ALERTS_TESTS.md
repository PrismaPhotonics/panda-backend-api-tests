# 🚀 פקודות להרצת טסטי Alerts

**תאריך עדכון:** 2025-11-13  
**מיקום:** `be_focus_server_tests/integration/alerts/`

---

## 📋 פקודות בסיסיות

### הרצת כל טסטי Alerts:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -v --skip-health-check
```

### הרצה עם לוגים מפורטים:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -v --skip-health-check --log-cli-level=INFO
```

### הרצה עם output מלא (ללא capture):
```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -v --skip-health-check -s
```

---

## 🎯 הרצה לפי קטגוריה

### Positive Tests (5 טסטים):
```powershell
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_positive.py -v --skip-health-check
```

### Negative Tests (7 טסטים, 1 מודלג):
```powershell
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_negative.py -v --skip-health-check
```

### Edge Cases (8 טסטים):
```powershell
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py -v --skip-health-check
```

### Load Tests (5 טסטים, 1 מודלג):
```powershell
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_load.py -v --skip-health-check
```

### Performance Tests (6 טסטים, 1 מודלג):
```powershell
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_performance.py -v --skip-health-check
```

### Investigation Tests:
```powershell
# Basic investigation
py -m pytest be_focus_server_tests/integration/alerts/test_alert_logs_investigation.py -v -s --skip-health-check

# Deep investigation
py -m pytest be_focus_server_tests/integration/alerts/test_deep_alert_logs_investigation.py -v -s --skip-health-check
```

---

## 🏷️ הרצה לפי Markers

### Positive tests only:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -m positive -v --skip-health-check
```

### Negative tests only:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -m negative -v --skip-health-check
```

### Edge cases only:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -m edge_case -v --skip-health-check
```

### Load tests only:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -m load -v --skip-health-check
```

### Performance tests only:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -m performance -v --skip-health-check
```

### Investigation tests only:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -m investigation -v -s --skip-health-check
```

---

## 🎯 הרצת טסט ספציפי

### דוגמה: SD Alert Test:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_positive.py::TestAlertGenerationPositive::test_successful_sd_alert_generation -v --skip-health-check
```

### דוגמה: Invalid Class ID Test:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_negative.py::TestAlertGenerationNegative::test_invalid_class_id -v --skip-health-check
```

### דוגמה: Boundary DOF Test:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py::TestAlertGenerationEdgeCases::test_boundary_dof_values -v --skip-health-check
```

---

## 📊 הרצה עם דוחות

### HTML Report:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -v --skip-health-check --html=reports/alerts_tests_report.html --self-contained-html
```

### JSON Report:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -v --skip-health-check --json-report --json-report-file=reports/alerts_tests_report.json
```

### JUnit XML Report:
```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -v --skip-health-check --junitxml=reports/alerts_tests_junit.xml
```

---

## ⚡ הרצה מהירה (רק טסטים מהירים, ללא load/performance):

```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -v --skip-health-check -m "not slow"
```

או:

```powershell
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_positive.py be_focus_server_tests/integration/alerts/test_alert_generation_negative.py be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py -v --skip-health-check
```

---

## 🔍 הרצה עם stop on first failure:

```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -v --skip-health-check -x
```

---

## 📝 הרצה עם parallel execution (אם מותקן pytest-xdist):

```powershell
py -m pytest be_focus_server_tests/integration/alerts/ -v --skip-health-check -n auto
```

---

## 🎯 פקודה מומלצת להרצה ראשונית:

```powershell
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_positive.py be_focus_server_tests/integration/alerts/test_alert_generation_negative.py be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py -v --skip-health-check --log-cli-level=INFO
```

פקודה זו מריצה:
- ✅ כל הטסטים החיוביים (5)
- ✅ כל הטסטים השליליים (7)
- ✅ כל ה-edge cases (8)
- **סה"כ:** 20 טסטים (מהירים יחסית)

---

## 📋 רשימת כל הטסטים:

### Positive (5):
- `test_successful_sd_alert_generation` (PZ-15000)
- `test_successful_sc_alert_generation` (PZ-15001)
- `test_multiple_alerts_generation` (PZ-15002)
- `test_different_severity_levels` (PZ-15003)
- `test_alert_processing_via_rabbitmq` (PZ-15004)

### Negative (7 + 1 skipped):
- `test_invalid_class_id` (PZ-15010)
- `test_invalid_severity` (PZ-15011)
- `test_invalid_dof_range` (PZ-15012)
- `test_missing_required_fields` (PZ-15013)
- `test_rabbitmq_connection_failure` (PZ-15014)
- `test_mongodb_connection_failure` (PZ-15015) - SKIPPED
- `test_invalid_alert_id_format` (PZ-15016)
- `test_duplicate_alert_ids` (PZ-15017)

### Edge Cases (8):
- `test_boundary_dof_values` (PZ-15020)
- `test_min_max_severity` (PZ-15021)
- `test_zero_alerts_amount` (PZ-15022)
- `test_very_large_alert_id` (PZ-15023)
- `test_concurrent_alerts_same_dof` (PZ-15024)
- `test_rapid_sequential_alerts` (PZ-15025)
- `test_alert_maximum_fields` (PZ-15026)
- `test_alert_minimum_fields` (PZ-15027)

### Load (5 + 1 skipped):
- `test_high_volume_load` (PZ-15030)
- `test_sustained_load` (PZ-15031)
- `test_burst_load` (PZ-15032)
- `test_mixed_alert_types_load` (PZ-15033)
- `test_rabbitmq_queue_capacity` (PZ-15034)
- `test_mongodb_write_load` (PZ-15035) - SKIPPED

### Performance (6 + 1 skipped):
- `test_alert_response_time` (PZ-15040)
- `test_alert_throughput` (PZ-15041)
- `test_alert_latency` (PZ-15042)
- `test_resource_usage` (PZ-15043)
- `test_end_to_end_performance` (PZ-15044)
- `test_rabbitmq_performance` (PZ-15045)
- `test_mongodb_performance` (PZ-15046) - SKIPPED

---

**סה"כ:** 36 טסטים (33 פעילים, 3 מודלגים)

