# 🚀 פקודות מעודכנות להרצת טסטים - Focus Server Automation

**תאריך עדכון:** 2025-01-27  
**גרסה:** 2.0  
**מבוסס על:** מבנה הפרויקט המאומת

---

## 📋 תוכן עניינים

1. [הרצה כללית](#הרצה-כללית)
2. [הרצה לפי קטגוריות](#הרצה-לפי-קטגוריות)
3. [הרצה לפי Markers](#הרצה-לפי-markers)
4. [הרצה של קבצים ספציפיים](#הרצה-של-קבצים-ספציפיים)
5. [הרצה לפי סביבה](#הרצה-לפי-סביבה)
6. [הרצה עם אפשרויות מתקדמות](#הרצה-עם-אפשרויות-מתקדמות)
7. [סקריפטים מוכנים](#סקריפטים-מוכנים)

---

## 🎯 הרצה כללית

### הרצת כל הבדיקות

```powershell
# דרך הסקריפט (מומלץ)
.\scripts\run_all_tests.ps1

# ישירות עם pytest
pytest be_focus_server_tests/ -v

# עם דוח HTML
pytest be_focus_server_tests/ -v --html=reports/report.html --self-contained-html

# עם סביבת Production
pytest be_focus_server_tests/ -v --env=new_production
```

### הרצה מהירה (ללא בדיקות איטיות)

```powershell
# דרך הסקריפט
.\scripts\run_all_tests.ps1 -TestSuite quick

# ישירות
pytest be_focus_server_tests/ -v -m "not slow"
```

---

## 📁 הרצה לפי קטגוריות

### 🟢 Integration Tests

```powershell
# כל בדיקות ה-Integration
pytest be_focus_server_tests/integration/ -v

# API Tests (20 קבצים)
pytest be_focus_server_tests/integration/api/ -v

# Alerts Tests (8 קבצים)
pytest be_focus_server_tests/integration/alerts/ -v

# Calculations Tests (1 קובץ)
pytest be_focus_server_tests/integration/calculations/ -v

# Data Quality Tests (תת-קטגוריה) (6 קבצים)
pytest be_focus_server_tests/integration/data_quality/ -v

# E2E Tests (1 קובץ)
pytest be_focus_server_tests/integration/e2e/ -v

# Error Handling Tests (3 קבצים)
pytest be_focus_server_tests/integration/error_handling/ -v

# Load Tests (תת-קטגוריה) (5 קבצים)
pytest be_focus_server_tests/integration/load/ -v

# Performance Tests (תת-קטגוריה) (8 קבצים)
pytest be_focus_server_tests/integration/performance/ -v

# Security Tests (תת-קטגוריה) (6 קבצים)
pytest be_focus_server_tests/integration/security/ -v
```

### 🟡 Data Quality Tests (רמה ראשית)

```powershell
# כל בדיקות Data Quality (רמה ראשית) (5 קבצים)
pytest be_focus_server_tests/data_quality/ -v

# בדיקת איכות נתונים ב-MongoDB
pytest be_focus_server_tests/data_quality/test_mongodb_data_quality.py -v

# בדיקת אינדקסים וסכמה
pytest be_focus_server_tests/data_quality/test_mongodb_indexes_and_schema.py -v

# בדיקת שחזור MongoDB
pytest be_focus_server_tests/data_quality/test_mongodb_recovery.py -v

# בדיקת אימות סכמה
pytest be_focus_server_tests/data_quality/test_mongodb_schema_validation.py -v

# סיווג הקלטות
pytest be_focus_server_tests/data_quality/test_recordings_classification.py -v
```

### 🟤 Infrastructure Tests

```powershell
# כל בדיקות Infrastructure (13+ קבצים)
pytest be_focus_server_tests/infrastructure/ -v

# בדיקות חיבור בסיסיות
pytest be_focus_server_tests/infrastructure/test_basic_connectivity.py -v

# בדיקות חיבור חיצוני
pytest be_focus_server_tests/infrastructure/test_external_connectivity.py -v

# בדיקות K8s Job Lifecycle
pytest be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py -v
# או דרך הסקריפט:
.\scripts\run_k8s_job_lifecycle_tests.ps1

# בדיקות MongoDB Monitoring
pytest be_focus_server_tests/infrastructure/test_mongodb_monitoring_agent.py -v

# בדיקות אינטגרציה עם PZ
pytest be_focus_server_tests/infrastructure/test_pz_integration.py -v

# בדיקות RabbitMQ
pytest be_focus_server_tests/infrastructure/test_rabbitmq_connectivity.py -v
pytest be_focus_server_tests/infrastructure/test_rabbitmq_outage_handling.py -v

# בדיקות התנהגות מערכת
pytest be_focus_server_tests/infrastructure/test_system_behavior.py -v
```

### 🔴 Resilience Tests

```powershell
# כל בדיקות Resilience (6 קבצים)
pytest be_focus_server_tests/infrastructure/resilience/ -v

# Resilience של Focus Server Pod
pytest be_focus_server_tests/infrastructure/resilience/test_focus_server_pod_resilience.py -v

# Resilience של MongoDB Pod
pytest be_focus_server_tests/infrastructure/resilience/test_mongodb_pod_resilience.py -v

# Resilience של RabbitMQ Pod
pytest be_focus_server_tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py -v

# Resilience של SEGY Recorder Pod
pytest be_focus_server_tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py -v

# Resilience של מספר Pods
pytest be_focus_server_tests/infrastructure/resilience/test_multiple_pods_resilience.py -v

# תרחישי שחזור Pods
pytest be_focus_server_tests/infrastructure/resilience/test_pod_recovery_scenarios.py -v
```

### 🔐 Security Tests

```powershell
# כל בדיקות Security (רמה ראשית + תת-קטגוריה)
pytest be_focus_server_tests/security/ -v
pytest be_focus_server_tests/integration/security/ -v

# טיפול בקלט לא תקין (רמה ראשית)
pytest be_focus_server_tests/security/test_malformed_input_handling.py -v

# אימות API (תת-קטגוריה)
pytest be_focus_server_tests/integration/security/test_api_authentication.py -v

# הגנת CSRF
pytest be_focus_server_tests/integration/security/test_csrf_protection.py -v

# חשיפת נתונים
pytest be_focus_server_tests/integration/security/test_data_exposure.py -v

# אכיפת HTTPS
pytest be_focus_server_tests/integration/security/test_https_enforcement.py -v

# אימות קלט
pytest be_focus_server_tests/integration/security/test_input_validation.py -v

# הגבלת קצב
pytest be_focus_server_tests/integration/security/test_rate_limiting.py -v
```

### ⚡ Stress Tests

```powershell
# בדיקות Stress (1 קובץ)
pytest be_focus_server_tests/stress/ -v

# תצורות קיצוניות
pytest be_focus_server_tests/stress/test_extreme_configurations.py -v
```

### 📈 Load Tests

```powershell
# בדיקות Load (רמה ראשית) (1 קובץ)
pytest be_focus_server_tests/load/ -v

# בדיקות קיבולת Jobs
pytest be_focus_server_tests/load/test_job_capacity_limits.py -v

# בדיקות Load (תת-קטגוריה) (5 קבצים)
pytest be_focus_server_tests/integration/load/ -v

# עומס מקבילי
pytest be_focus_server_tests/integration/load/test_concurrent_load.py -v

# פרופילי עומס
pytest be_focus_server_tests/integration/load/test_load_profiles.py -v

# עומס שיא
pytest be_focus_server_tests/integration/load/test_peak_load.py -v

# שחזור ועייפות
pytest be_focus_server_tests/integration/load/test_recovery_and_exhaustion.py -v

# עומס מתמשך
pytest be_focus_server_tests/integration/load/test_sustained_load.py -v
```

### 🔴 Performance Tests

```powershell
# בדיקות Performance (רמה ראשית) (1 קובץ)
pytest be_focus_server_tests/performance/ -v

# Resilience של MongoDB Outage
pytest be_focus_server_tests/performance/test_mongodb_outage_resilience.py -v

# בדיקות Performance (תת-קטגוריה) (8 קבצים)
pytest be_focus_server_tests/integration/performance/ -v

# ביצועים מקביליים
pytest be_focus_server_tests/integration/performance/test_concurrent_performance.py -v

# ביצועי מסד נתונים
pytest be_focus_server_tests/integration/performance/test_database_performance.py -v

# דרישות זמן תגובה
pytest be_focus_server_tests/integration/performance/test_latency_requirements.py -v

# זמן תגובה ברשת
pytest be_focus_server_tests/integration/performance/test_network_latency.py -v

# ביצועים בעדיפות גבוהה
pytest be_focus_server_tests/integration/performance/test_performance_high_priority.py -v

# שימוש במשאבים
pytest be_focus_server_tests/integration/performance/test_resource_usage.py -v

# זמן תגובה
pytest be_focus_server_tests/integration/performance/test_response_time.py -v
```

### 🔬 Unit Tests

```powershell
# כל בדיקות Unit (4 קבצים)
pytest be_focus_server_tests/unit/ -v

# פונקציונליות בסיסית
pytest be_focus_server_tests/unit/test_basic_functionality.py -v

# טעינת קונפיגורציה
pytest be_focus_server_tests/unit/test_config_loading.py -v

# אימות מודלים
pytest be_focus_server_tests/unit/test_models_validation.py -v

# אימותים
pytest be_focus_server_tests/unit/test_validators.py -v
```

### 🎨 UI Tests

```powershell
# כל בדיקות UI (2 קבצים)
pytest be_focus_server_tests/ui/ -v

# אינטראקציות כפתורים
pytest be_focus_server_tests/ui/generated/test_button_interactions.py -v

# אימות טפסים
pytest be_focus_server_tests/ui/generated/test_form_validation.py -v
```

---

## 🏷️ הרצה לפי Markers

### Markers לפי קטגוריה

```powershell
# Integration
pytest -m integration -v

# API
pytest -m api -v

# Infrastructure
pytest -m infrastructure -v

# Resilience
pytest -m resilience -v

# Data Quality
pytest -m data_quality -v

# Performance
pytest -m performance -v

# Security
pytest -m security -v

# Load
pytest -m load -v

# Stress
pytest -m stress -v

# Unit
pytest -m unit -v

# UI
pytest -m ui -v

# Alerts
pytest -m alerts -v

# Error Handling
pytest -m error_handling -v

# E2E
pytest -m e2e -v
```

### Markers לפי רכיב

```powershell
# MongoDB
pytest -m mongodb -v

# Kubernetes
pytest -m kubernetes -v

# RabbitMQ
pytest -m rabbitmq -v

# ROI
pytest -m roi -v

# SingleChannel
pytest -m singlechannel -v

# Waterfall
pytest -m waterfall -v

# Live
pytest -m live -v

# Historic
pytest -m historic -v

# gRPC
pytest -m grpc -v
```

### Markers לפי סוג

```powershell
# Critical
pytest -m critical -v

# Smoke
pytest -m smoke -v

# Slow
pytest -m "not slow" -v

# Positive
pytest -m positive -v

# Negative
pytest -m negative -v

# Edge Cases
pytest -m edge_case -v
```

### שילוב Markers

```powershell
# Integration + API + Critical
pytest -m "integration and api and critical" -v

# Infrastructure + MongoDB
pytest -m "infrastructure and mongodb" -v

# Performance + not slow
pytest -m "performance and not slow" -v

# Alerts + Positive
pytest -m "alerts and positive" -v

# Data Quality + MongoDB
pytest -m "data_quality and mongodb" -v
```

---

## 📄 הרצה של קבצים ספציפיים

### API Endpoints (20 קבצים)

```powershell
# בדיקות API בעדיפות גבוהה
pytest be_focus_server_tests/integration/api/test_api_endpoints_high_priority.py -v

# בדיקות API נוספות
pytest be_focus_server_tests/integration/api/test_api_endpoints_additional.py -v

# אימות קונפיגורציה בעדיפות גבוהה
pytest be_focus_server_tests/integration/api/test_config_validation_high_priority.py -v

# אימות NFFT ותדירות
pytest be_focus_server_tests/integration/api/test_config_validation_nfft_frequency.py -v

# Endpoint Configure
pytest be_focus_server_tests/integration/api/test_configure_endpoint.py -v

# Endpoint Config Task
pytest be_focus_server_tests/integration/api/test_config_task_endpoint.py -v

# Endpoint Task Metadata
pytest be_focus_server_tests/integration/api/test_task_metadata_endpoint.py -v

# Endpoint Waterfall
pytest be_focus_server_tests/integration/api/test_waterfall_endpoint.py -v

# Health Check
pytest be_focus_server_tests/integration/api/test_health_check.py -v

# אימותים לפני הפעלה
pytest be_focus_server_tests/integration/api/test_prelaunch_validations.py -v

# זרימת ניטור Live
pytest be_focus_server_tests/integration/api/test_live_monitoring_flow.py -v

# יציבות Live Streaming
pytest be_focus_server_tests/integration/api/test_live_streaming_stability.py -v

# Playback היסטורי E2E
pytest be_focus_server_tests/integration/api/test_historic_playback_e2e.py -v

# Playback היסטורי נוסף
pytest be_focus_server_tests/integration/api/test_historic_playback_additional.py -v

# מיפוי SingleChannel View
pytest be_focus_server_tests/integration/api/test_singlechannel_view_mapping.py -v

# Waterfall View
pytest be_focus_server_tests/integration/api/test_waterfall_view.py -v

# התאמת ROI דינמית
pytest be_focus_server_tests/integration/api/test_dynamic_roi_adjustment.py -v

# אימות סוג View
pytest be_focus_server_tests/integration/api/test_view_type_validation.py -v

# אימות Orchestration
pytest be_focus_server_tests/integration/api/test_orchestration_validation.py -v

# מקרה קצה של NFFT Overlap
pytest be_focus_server_tests/integration/api/test_nfft_overlap_edge_case.py -v
```

### Alerts Tests (8 קבצים)

```powershell
# תרחישים חיוביים
pytest be_focus_server_tests/integration/alerts/test_alert_generation_positive.py -v

# תרחישים שליליים
pytest be_focus_server_tests/integration/alerts/test_alert_generation_negative.py -v

# מקרי קצה
pytest be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py -v

# תרחישי עומס
pytest be_focus_server_tests/integration/alerts/test_alert_generation_load.py -v

# תרחישי ביצועים
pytest be_focus_server_tests/integration/alerts/test_alert_generation_performance.py -v

# חקירת לוגים
pytest be_focus_server_tests/integration/alerts/test_alert_logs_investigation.py -v -s

# חקירה מעמיקה של לוגים
pytest be_focus_server_tests/integration/alerts/test_deep_alert_logs_investigation.py -v -s
```

### Data Quality Tests (תת-קטגוריה) (6 קבצים)

```powershell
# בדיקת יצירת Consumer (Debug)
pytest be_focus_server_tests/integration/data_quality/test_consumer_creation_debug.py -v

# בדיקת שלמות נתונים
pytest be_focus_server_tests/integration/data_quality/test_data_completeness.py -v

# בדיקת עקביות נתונים
pytest be_focus_server_tests/integration/data_quality/test_data_consistency.py -v

# בדיקת שלמות נתונים
pytest be_focus_server_tests/integration/data_quality/test_data_integrity.py -v

# חקירת יצירת Consumer
pytest be_focus_server_tests/integration/data_quality/test_investigate_consumer_creation.py -v

# ערכי אמפליטודה שליליים
pytest be_focus_server_tests/integration/data_quality/test_negative_amplitude_values.py -v
```

### Error Handling Tests (3 קבצים)

```powershell
# קודי שגיאת HTTP
pytest be_focus_server_tests/integration/error_handling/test_http_error_codes.py -v

# Payloads לא תקינים
pytest be_focus_server_tests/integration/error_handling/test_invalid_payloads.py -v

# שגיאות רשת
pytest be_focus_server_tests/integration/error_handling/test_network_errors.py -v
```

### Load Tests (תת-קטגוריה) (5 קבצים)

```powershell
# עומס מקבילי
pytest be_focus_server_tests/integration/load/test_concurrent_load.py -v

# פרופילי עומס
pytest be_focus_server_tests/integration/load/test_load_profiles.py -v

# עומס שיא
pytest be_focus_server_tests/integration/load/test_peak_load.py -v

# שחזור ועייפות
pytest be_focus_server_tests/integration/load/test_recovery_and_exhaustion.py -v

# עומס מתמשך
pytest be_focus_server_tests/integration/load/test_sustained_load.py -v
```

### Performance Tests (תת-קטגוריה) (8 קבצים)

```powershell
# ביצועים מקביליים
pytest be_focus_server_tests/integration/performance/test_concurrent_performance.py -v

# ביצועי מסד נתונים
pytest be_focus_server_tests/integration/performance/test_database_performance.py -v

# דרישות זמן תגובה
pytest be_focus_server_tests/integration/performance/test_latency_requirements.py -v

# זמן תגובה ברשת
pytest be_focus_server_tests/integration/performance/test_network_latency.py -v

# ביצועים בעדיפות גבוהה
pytest be_focus_server_tests/integration/performance/test_performance_high_priority.py -v

# שימוש במשאבים
pytest be_focus_server_tests/integration/performance/test_resource_usage.py -v

# זמן תגובה
pytest be_focus_server_tests/integration/performance/test_response_time.py -v
```

### Security Tests (תת-קטגוריה) (6 קבצים)

```powershell
# אימות API
pytest be_focus_server_tests/integration/security/test_api_authentication.py -v

# הגנת CSRF
pytest be_focus_server_tests/integration/security/test_csrf_protection.py -v

# חשיפת נתונים
pytest be_focus_server_tests/integration/security/test_data_exposure.py -v

# אכיפת HTTPS
pytest be_focus_server_tests/integration/security/test_https_enforcement.py -v

# אימות קלט
pytest be_focus_server_tests/integration/security/test_input_validation.py -v

# הגבלת קצב
pytest be_focus_server_tests/integration/security/test_rate_limiting.py -v
```

### בדיקות ספציפיות לפי פונקציה

```powershell
# פונקציה ספציפית
pytest be_focus_server_tests/integration/api/test_health_check.py::test_health_check_endpoint -v

# מחלקה ספציפית
pytest be_focus_server_tests/integration/api/test_api_endpoints_high_priority.py::TestHealthCheck -v

# מספר פונקציות
pytest be_focus_server_tests/integration/api/test_health_check.py::test_health_check_endpoint be_focus_server_tests/integration/api/test_health_check.py::test_health_check_response_time -v
```

---

## 🌍 הרצה לפי סביבה

### בחירת סביבה

```powershell
# דרך הסקריפט
.\scripts\select_environment.ps1

# או ישירות עם pytest
pytest be_focus_server_tests/ -v --env=new_production
pytest be_focus_server_tests/ -v --env=staging
pytest be_focus_server_tests/ -v --env=development
```

### הגדרת סביבת Production

```powershell
# דרך הסקריפט
.\scripts\set_production_env.ps1

# או
.\scripts\setup\set_production_env.ps1
```

---

## ⚙️ הרצה עם אפשרויות מתקדמות

### עם Coverage

```powershell
# דרך הסקריפט
.\scripts\run_all_tests.ps1 -WithCoverage

# ישירות
pytest be_focus_server_tests/ -v --cov=src --cov-report=html --cov-report=term
```

### הרצה מקבילית

```powershell
# דרך הסקריפט
.\scripts\run_all_tests.ps1 -Parallel

# ישירות (דורש pytest-xdist)
pytest be_focus_server_tests/ -v -n auto
pytest be_focus_server_tests/ -v -n 4  # 4 workers
```

### עם דוחות

```powershell
# דוח HTML
pytest be_focus_server_tests/ -v --html=reports/report.html --self-contained-html

# דוח JUnit XML
pytest be_focus_server_tests/ -v --junitxml=reports/junit.xml

# דוח JSON
pytest be_focus_server_tests/ -v --json-report --json-report-file=reports/report.json
```

### עם לוגים מפורטים

```powershell
# לוגים ברמת DEBUG
pytest be_focus_server_tests/ -v -s --log-cli-level=DEBUG

# לוגים ברמת INFO
pytest be_focus_server_tests/ -v -s --log-cli-level=INFO

# לוגים לקובץ
pytest be_focus_server_tests/ -v --log-file=logs/test.log --log-file-level=DEBUG
```

### עם Xray Integration

```powershell
# הרצה עם העלאה ל-Xray
pytest be_focus_server_tests/ -v --xray

# הרצה עם Test Plan ספציפי
pytest be_focus_server_tests/ -v --xray --xray-test-plan=PZ-14024
```

### עם Stop on First Failure

```powershell
# עצירה בכשל הראשון
pytest be_focus_server_tests/ -v -x

# עצירה אחרי N כשלים
pytest be_focus_server_tests/ -v --maxfail=3
```

### עם Filter לפי שם

```powershell
# בדיקות שמכילות "health" בשם
pytest be_focus_server_tests/ -v -k "health"

# בדיקות שמכילות "api" אבל לא "load"
pytest be_focus_server_tests/ -v -k "api and not load"

# בדיקות שמכילות "mongodb" או "rabbitmq"
pytest be_focus_server_tests/ -v -k "mongodb or rabbitmq"
```

---

## 📜 סקריפטים מוכנים

### סקריפטים להרצה

```powershell
# הרצת כל הבדיקות
.\scripts\run_all_tests.ps1

# הרצת בדיקות Unit בלבד
.\scripts\run_all_tests.ps1 -TestSuite unit

# הרצת בדיקות Integration בלבד
.\scripts\run_all_tests.ps1 -TestSuite integration

# הרצת בדיקות API בלבד
.\scripts\run_all_tests.ps1 -TestSuite api

# הרצה מהירה
.\scripts\run_all_tests.ps1 -TestSuite quick

# עם Coverage
.\scripts\run_all_tests.ps1 -WithCoverage

# עם הרצה מקבילית
.\scripts\run_all_tests.ps1 -Parallel

# ללא הגדרת סביבה
.\scripts\run_all_tests.ps1 -SkipEnvSetup
```

### בדיקות Read-Only

```powershell
# בדיקות Read-Only (בטוחות למצב "waiting for fiber")
.\scripts\run_readonly_tests.ps1

# או ישירות
python scripts/run_readonly_tests.py
```

### בדיקות K8s Job Lifecycle

```powershell
# דרך הסקריפט
.\scripts\run_k8s_job_lifecycle_tests.ps1

# עם אפשרויות
.\scripts\run_k8s_job_lifecycle_tests.ps1 -SkipHealthCheck -Verbose -LogLevel DEBUG
```

### בדיקות עם לוגים משופרים

```powershell
.\scripts\test_with_enhanced_logging.ps1
```

### בדיקות Production Light

```powershell
.\scripts\run_production_light.ps1
```

---

## 📊 דוגמאות שימוש נפוצות

### הרצה יומית מהירה

```powershell
# בדיקות Smoke + Critical
pytest be_focus_server_tests/ -v -m "smoke or critical" --tb=short
```

### הרצה לפני Release

```powershell
# כל הבדיקות בעדיפות גבוהה
pytest be_focus_server_tests/ -v -m "critical or high" --html=reports/pre_release.html --self-contained-html
```

### הרצה אחרי שינוי ב-API

```powershell
# רק בדיקות API
pytest be_focus_server_tests/integration/api/ -v --tb=short -x
```

### הרצה אחרי שינוי ב-Infrastructure

```powershell
# בדיקות Infrastructure + Resilience
pytest be_focus_server_tests/infrastructure/ -v -m "infrastructure or resilience"
```

### הרצה לבדיקת Data Quality

```powershell
# כל בדיקות Data Quality (רמה ראשית + תת-קטגוריה)
pytest be_focus_server_tests/data_quality/ be_focus_server_tests/integration/data_quality/ -v
```

### הרצה לבדיקת Alerts

```powershell
# כל בדיקות Alerts
pytest be_focus_server_tests/integration/alerts/ -v

# רק תרחישים חיוביים
pytest be_focus_server_tests/integration/alerts/ -m positive -v
```

---

## 🎯 טיפים וטריקים

### הרצה מהירה יותר

```powershell
# דילוג על בדיקות איטיות
pytest be_focus_server_tests/ -v -m "not slow"

# הרצה מקבילית
pytest be_focus_server_tests/ -v -n auto

# דילוג על בדיקות שכבר עברו
pytest be_focus_server_tests/ -v --lf  # last failed
pytest be_focus_server_tests/ -v --ff  # failed first
```

### דיבוג

```powershell
# עם PDB (Python Debugger)
pytest be_focus_server_tests/integration/api/test_health_check.py -v -s --pdb

# עם print statements
pytest be_focus_server_tests/integration/api/test_health_check.py -v -s

# עם traceback מלא
pytest be_focus_server_tests/integration/api/test_health_check.py -v --tb=long
```

### הרצה עם משתני סביבה

```powershell
# Windows PowerShell
$env:PYTEST_ENV="new_production"; pytest be_focus_server_tests/ -v

# או דרך הסקריפט
.\scripts\set_production_env.ps1
pytest be_focus_server_tests/ -v
```

---

## 📝 הערות חשובות

1. **סביבת עבודה**: ודא שהסביבה מוגדרת נכון לפני הרצת בדיקות
2. **Virtual Environment**: הפעל את ה-venv לפני הרצת בדיקות
3. **תלויות**: ודא שכל התלויות מותקנות (`pip install -r requirements.txt`)
4. **קונפיגורציה**: בדוק את `config/environments.yaml` לפני הרצה
5. **לוגים**: הלוגים נשמרים ב-`logs/test_runs/` עם חותמת זמן

---

## 🔗 קישורים נוספים

- [README הראשי](../be_focus_server_tests/README.md)
- [מדריך Integration Tests](../be_focus_server_tests/integration/README.md)
- [מדריך Infrastructure Tests](../be_focus_server_tests/infrastructure/README.md)
- [מדריך Alerts Tests](../be_focus_server_tests/integration/alerts/README.md)
- [דוח אימות מבנה](../TEST_STRUCTURE_VERIFICATION_REPORT.md)

---

**תאריך עדכון:** 2025-01-27  
**מבוסס על:** מבנה הפרויקט המאומת  
**גרסה:** 2.0

