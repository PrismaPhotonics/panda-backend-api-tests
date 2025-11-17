# 🚀 רשימת טסטי Alerts ופקודות הרצה

**מיקום:** `be_focus_server_tests/integration/alerts/`  
**תאריך עדכון:** 2025-11-13

---

## 📋 רשימת כל הטסטים

### 1. Positive Scenarios (`test_alert_generation_positive.py`)
- ✅ `test_successful_sd_alert_generation` (PZ-15000)
- ✅ `test_successful_sc_alert_generation` (PZ-15001)
- ✅ `test_multiple_alerts_generation` (PZ-15002)
- ✅ `test_different_severity_levels` (PZ-15003)
- ✅ `test_alert_processing_via_rabbitmq` (PZ-15004)

### 2. Negative Scenarios (`test_alert_generation_negative.py`)
- ❌ `test_invalid_class_id` (PZ-15010)
- ❌ `test_invalid_severity` (PZ-15011)
- ❌ `test_invalid_dof_range` (PZ-15012)
- ❌ `test_missing_required_fields` (PZ-15013)
- ❌ `test_rabbitmq_connection_failure` (PZ-15014)
- ❌ `test_mongodb_connection_failure` (PZ-15015)
- ❌ `test_invalid_alert_id_format` (PZ-15016)
- ❌ `test_duplicate_alert_ids` (PZ-15017)

### 3. Edge Cases (`test_alert_generation_edge_cases.py`)
- 🔍 `test_boundary_dof_values` (PZ-15020)
- 🔍 `test_min_max_severity` (PZ-15021)
- 🔍 `test_zero_alerts_amount` (PZ-15022)
- 🔍 `test_very_large_alert_id` (PZ-15023)
- 🔍 `test_concurrent_alerts_same_dof` (PZ-15024)
- 🔍 `test_rapid_sequential_alerts` (PZ-15025)
- 🔍 `test_maximum_minimum_fields` (PZ-15026)
- 🔍 `test_edge_case_combinations` (PZ-15027)

### 4. Load Scenarios (`test_alert_generation_load.py`)
- 📈 `test_high_volume_load` (PZ-15030)
- 📈 `test_sustained_load` (PZ-15031)
- 📈 `test_burst_load` (PZ-15032)
- 📈 `test_mixed_alert_types_load` (PZ-15033)
- 📈 `test_rabbitmq_queue_capacity` (PZ-15034)

### 5. Performance Scenarios (`test_alert_generation_performance.py`)
- ⚡ `test_response_time` (PZ-15040)
- ⚡ `test_throughput` (PZ-15041)
- ⚡ `test_latency` (PZ-15042)
- ⚡ `test_resource_usage` (PZ-15043)
- ⚡ `test_end_to_end_performance` (PZ-15044)
- ⚡ `test_rabbitmq_performance` (PZ-15045)

### 6. Investigation Tests
- 🔬 `test_investigate_alert_logs` (`test_alert_logs_investigation.py`)
- 🔬 `test_deep_investigate_alert_logs` (`test_deep_alert_logs_investigation.py`) (PZ-15051)

---

## 🚀 פקודות הרצה

### הרצת כל הטסטים:
```bash
py -m pytest be_focus_server_tests/integration/alerts/ -v --skip-health-check
```

### הרצה לפי קטגוריה:

#### Positive Tests:
```bash
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_positive.py -v --skip-health-check
```

#### Negative Tests:
```bash
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_negative.py -v --skip-health-check
```

#### Edge Cases:
```bash
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py -v --skip-health-check
```

#### Load Tests:
```bash
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_load.py -v --skip-health-check
```

#### Performance Tests:
```bash
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_performance.py -v --skip-health-check
```

#### Investigation Tests:
```bash
# Basic investigation
py -m pytest be_focus_server_tests/integration/alerts/test_alert_logs_investigation.py -v -s --skip-health-check

# Deep investigation
py -m pytest be_focus_server_tests/integration/alerts/test_deep_alert_logs_investigation.py -v -s --skip-health-check
```

---

### הרצה לפי Markers:

```bash
# Positive tests only
py -m pytest be_focus_server_tests/integration/alerts/ -m positive -v --skip-health-check

# Negative tests only
py -m pytest be_focus_server_tests/integration/alerts/ -m negative -v --skip-health-check

# Edge cases only
py -m pytest be_focus_server_tests/integration/alerts/ -m edge_cases -v --skip-health-check

# Load tests only
py -m pytest be_focus_server_tests/integration/alerts/ -m load -v --skip-health-check

# Performance tests only
py -m pytest be_focus_server_tests/integration/alerts/ -m performance -v --skip-health-check

# Investigation tests only
py -m pytest be_focus_server_tests/integration/alerts/ -m investigation -v --skip-health-check
```

---

### הרצת טסט ספציפי:

```bash
# דוגמה: טסט SD Alert
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_positive.py::TestAlertGenerationPositive::test_successful_sd_alert_generation -v --skip-health-check

# דוגמה: טסט RabbitMQ
py -m pytest be_focus_server_tests/integration/alerts/test_alert_generation_positive.py::TestAlertGenerationPositive::test_alert_processing_via_rabbitmq -v --skip-health-check
```

---

### הרצה עם לוגים מפורטים:

```bash
py -m pytest be_focus_server_tests/integration/alerts/ -v --skip-health-check --log-cli-level=INFO
```

---

### הרצה עם HTML report:

```bash
py -m pytest be_focus_server_tests/integration/alerts/ -v --skip-health-check --html=reports/alerts_tests_report.html --self-contained-html
```

---

## 📊 סיכום

**סה"כ טסטים:** ~36 טסטים

- ✅ **Positive:** 5 טסטים
- ❌ **Negative:** 8 טסטים
- 🔍 **Edge Cases:** 8 טסטים
- 📈 **Load:** 5 טסטים
- ⚡ **Performance:** 6 טסטים
- 🔬 **Investigation:** 2 טסטים

---

## 📁 מיקום הקבצים

```
be_focus_server_tests/integration/alerts/
├── __init__.py
├── README.md                                    # תיעוד מלא
├── test_alert_generation_positive.py            # Positive tests
├── test_alert_generation_negative.py            # Negative tests
├── test_alert_generation_edge_cases.py          # Edge cases
├── test_alert_generation_load.py                # Load tests
├── test_alert_generation_performance.py         # Performance tests
├── test_alert_logs_investigation.py             # Basic investigation
└── test_deep_alert_logs_investigation.py        # Deep investigation
```

---

## 📝 הערות חשובות

1. **MongoDB Storage:** Alerts לא נשמרים ב-MongoDB - הטסטים לא בודקים MongoDB storage
2. **RabbitMQ:** רוב הטסטים דורשים חיבור ל-RabbitMQ
3. **Dependencies:** חלק מהטסטים דורשים `pika` (RabbitMQ client)
4. **Slow Tests:** Load ו-Performance tests מסומנים כ-`@pytest.mark.slow`

---

**קובץ זה:** `docs/02_user_guides/ALERTS_TESTS_QUICK_REFERENCE.md`  
**README מלא:** `be_focus_server_tests/integration/alerts/README.md`

