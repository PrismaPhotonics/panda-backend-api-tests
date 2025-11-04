# 🚀 Quick Start - Running Tests with Reporting

## פשוט ומהיר

הרצת טסטים עם דוחות ולוגים בזמן אמת:

```bash
python scripts/reporting/generate_report.py tests/
```

זה יריץ את כל הטסטים, יציג לוגים בזמן אמת, וייצור דוחות!

## מה תראה?

### בזמן הריצה:
```
================================================================================
Running pytest with comprehensive reporting...
Run ID: run_20251029_143022
Output Directory: reports/runs/run_20251029_143022
================================================================================

=========================== test session starts ============================
platform win32 -- Python 3.11.5, pytest-7.4.0
collected 307 items

tests/integration/api/test_health_check.py::test_health_check_valid_response PASSED
tests/integration/api/test_health_check.py::test_health_check_returns_200_ok PASSED
[INFO] src.apis.focus_server_api: Sending GET request to /health
[INFO] src.apis.focus_server_api: Response: 200 OK (45.23ms)

tests/integration/api/test_singlechannel_view_mapping.py::test_singlechannel_channel_1 PASSED
...
```

### בסוף:
```
Report generation complete!
View report at: reports/runs/run_20251029_143022/index.html

================================================================================
Report Generation Summary
================================================================================
Run ID: run_20251029_143022
Total Tests: 307
Passed: 238
Failed: 18
Skipped: 51
Pass Rate: 77.52%
Duration: 1250.45 seconds
================================================================================
```

## אופציות נוספות

### רק טסטים מסוימים:
```bash
python scripts/reporting/generate_report.py tests/integration/api/test_health_check.py
```

### עם markers:
```bash
python scripts/reporting/generate_report.py tests/ -m integration
```

### ב-parallel:
```bash
python scripts/reporting/generate_report.py tests/ --parallel
```

### שילוב:
```bash
python scripts/reporting/generate_report.py tests/integration/ -m "not slow" --parallel
```

## צפייה בדוחות

### Dashboard מרכזי:
```
reports/dashboard/index.html
```

### דוח ריצה ספציפית:
```
reports/runs/run_YYYYMMDD_HHMMSS/index.html
```

### לוג מלא:
```
reports/runs/run_YYYYMMDD_HHMMSS/test_output.log
```

## בעיות?

### לא רואה לוגים?
- ודא שיש `-s` בפקודה (מוסיף אוטומטית)
- ודא ש-`log-cli-level=INFO` מופיע (מוסיף אוטומטית)

### לא רואה תוצאות?
- בדוק את `reports/runs/run_YYYYMMDD_HHMMSS/`
- פתח את `index.html` בדפדפן

### טסטים לא רצים?
- ודא שאתה בתיקיית הפרויקט
- ודא ש-pytest מותקן: `pip install -r requirements.txt`

---

**עזרה נוספת:** ראה `scripts/reporting/README.md`

