# 🚀 פקודה להרצת Read-Only Tests (מתוקן)

**תאריך:** 2025-11-08  
**מצב:** ⚠️ המערכת במצב "waiting for fiber"

---

## ✅ פקודה אחת להרצת כל הטסטים (מתוקן)

### PowerShell:

```powershell
# Activate virtual environment (if needed)
if (Test-Path .venv\Scripts\Activate.ps1) { . .venv\Scripts\Activate.ps1 }

# Run all read-only tests
.venv\Scripts\python.exe -m pytest -v -s --tb=short --skip-health-check -k "not configure" `
    tests/integration/api/test_health_check.py `
    tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint `
    tests/integration/api/test_api_endpoints_additional.py::test_get_sensors_endpoint `
    tests/integration/api/test_api_endpoints_additional.py::test_get_live_metadata_available `
    tests/infrastructure/ `
    tests/data_quality/ `
    tests/unit/
```

### Bash/Linux:

```bash
# Activate virtual environment (if needed)
source .venv/bin/activate

# Run all read-only tests
python -m pytest -v -s --tb=short --skip-health-check -k "not configure" \
    tests/integration/api/test_health_check.py \
    tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint \
    tests/integration/api/test_api_endpoints_additional.py::test_get_sensors_endpoint \
    tests/integration/api/test_api_endpoints_additional.py::test_get_live_metadata_available \
    tests/infrastructure/ \
    tests/data_quality/ \
    tests/unit/
```

---

## 📋 מה הטסטים בודקים

| # | Test | מה בודק |
|---|------|---------|
| 1 | `test_health_check.py` | כל טסטי health check |
| 2 | `TestChannelsEndpoint` | בדיקת channels endpoint (יחזיר 2337 channels) |
| 3 | `test_get_sensors_endpoint` | בדיקת sensors endpoint |
| 4 | `test_get_live_metadata_available` | בדיקת live metadata endpoint (יחזיר prr=0.0) |
| 5 | `tests/infrastructure/` | כל טסטי infrastructure (ללא configure) |
| 6 | `tests/data_quality/` | כל טסטי data quality (ללא configure) |
| 7 | `tests/unit/` | כל טסטי unit |

---

## 🔧 אפשרויות נוספות

### עם דוח HTML:

```powershell
.venv\Scripts\python.exe -m pytest -v -s --tb=short --skip-health-check -k "not configure" `
    tests/integration/api/test_health_check.py `
    tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint `
    tests/integration/api/test_api_endpoints_additional.py::test_get_sensors_endpoint `
    tests/integration/api/test_api_endpoints_additional.py::test_get_live_metadata_available `
    tests/infrastructure/ `
    tests/data_quality/ `
    tests/unit/ `
    --html=reports/readonly_tests_report.html --self-contained-html
```

---

**עודכן לאחרונה:** 2025-11-08

