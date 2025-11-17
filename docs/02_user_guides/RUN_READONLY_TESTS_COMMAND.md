# 🚀 פקודה להרצת Read-Only Tests

**תאריך:** 2025-11-08  
**מצב:** ⚠️ המערכת במצב "waiting for fiber"

---

## ✅ פקודה אחת להרצת כל הטסטים

### PowerShell:

```powershell
# Activate virtual environment (if needed)
if (Test-Path .venv\Scripts\Activate.ps1) { . .venv\Scripts\Activate.ps1 }

# Run all read-only tests
pytest -v -s --tb=short -k "not configure" `
    tests/integration/api/test_api_endpoints_high_priority.py::TestHealthCheck `
    tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint `
    tests/integration/api/test_api_endpoints_high_priority.py::TestSensorsEndpoint `
    tests/integration/api/test_api_endpoints_high_priority.py::TestLiveMetadataEndpoint `
    tests/infrastructure/ `
    tests/data_quality/ `
    tests/unit/
```

### Bash/Linux:

```bash
# Activate virtual environment (if needed)
source .venv/bin/activate

# Run all read-only tests
pytest -v -s --tb=short -k "not configure" \
    tests/integration/api/test_api_endpoints_high_priority.py::TestHealthCheck \
    tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint \
    tests/integration/api/test_api_endpoints_high_priority.py::TestSensorsEndpoint \
    tests/integration/api/test_api_endpoints_high_priority.py::TestLiveMetadataEndpoint \
    tests/infrastructure/ \
    tests/data_quality/ \
    tests/unit/
```

### Python Script:

```bash
# Run the script
python scripts/run_readonly_tests.py

# Or with virtual environment
.venv\Scripts\python.exe scripts/run_readonly_tests.py
```

---

## 📋 מה הטסטים בודקים

| # | Test | מה בודק |
|---|------|---------|
| 1 | `TestHealthCheck` | בדיקת health endpoint |
| 2 | `TestChannelsEndpoint` | בדיקת channels endpoint (יחזיר 2337 channels) |
| 3 | `TestSensorsEndpoint` | בדיקת sensors endpoint |
| 4 | `TestLiveMetadataEndpoint` | בדיקת live metadata endpoint (יחזיר prr=0.0) |
| 5 | `tests/infrastructure/` | כל טסטי infrastructure (ללא configure) |
| 6 | `tests/data_quality/` | כל טסטי data quality (ללא configure) |
| 7 | `tests/unit/` | כל טסטי unit |

---

## 🔧 אפשרויות נוספות

### עם דוח HTML:

```powershell
pytest -v -s --tb=short -k "not configure" `
    tests/integration/api/test_api_endpoints_high_priority.py::TestHealthCheck `
    tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint `
    tests/integration/api/test_api_endpoints_high_priority.py::TestSensorsEndpoint `
    tests/integration/api/test_api_endpoints_high_priority.py::TestLiveMetadataEndpoint `
    tests/infrastructure/ `
    tests/data_quality/ `
    tests/unit/ `
    --html=reports/readonly_tests_report.html --self-contained-html
```

### עם coverage:

```powershell
pytest -v -s --tb=short -k "not configure" `
    tests/integration/api/test_api_endpoints_high_priority.py::TestHealthCheck `
    tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint `
    tests/integration/api/test_api_endpoints_high_priority.py::TestSensorsEndpoint `
    tests/integration/api/test_api_endpoints_high_priority.py::TestLiveMetadataEndpoint `
    tests/infrastructure/ `
    tests/data_quality/ `
    tests/unit/ `
    --cov=src --cov-report=html --cov-report=term
```

---

## ⚠️ הערות

1. **הפקודה מסננת טסטי configure** - `-k "not configure"` מבטיח שלא ירוצו טסטים שמנסים להגדיר jobs
2. **הטסטים בטוחים** - כל הטסטים האלה הם read-only ולא דורשים configuration
3. **אם יש health check שגורם לבעיה** - אפשר לדלג עליו עם `--skip-health-check` (לא מומלץ)

---

**עודכן לאחרונה:** 2025-11-08

