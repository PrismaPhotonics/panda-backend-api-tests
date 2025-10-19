# הרצת טסטים - SingleChannel View

## 🚀 הגדרת סביבת הטסטים

### שלב 1: ודא שהסביבה מותקנת
```powershell
# בדוק אם Python מותקן
python --version

# אם לא, התקן Python 3.11+
# https://www.python.org/downloads/
```

### שלב 2: התקן dependencies
```powershell
# מהתיקייה הראשית של הפרויקט
pip install -r requirements.txt
```

### שלב 3: ודא שה-environment מוגדר
```powershell
# בדוק את קובץ הקונפיגורציה
python scripts/debug_config.py

# או
python -c "from config.config_manager import ConfigManager; print(ConfigManager('staging').get('focus_server.base_url'))"
```

---

## ✅ הרצת הטסטים

### הרצה בסיסית
```powershell
# כל הטסטים בקובץ
pytest tests/integration/api/test_singlechannel_view_mapping.py -v

# הטסט הראשי בלבד
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewHappyPath::test_configure_singlechannel_mapping -v -s

# כל ה-Happy Path tests
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewHappyPath -v
```

### הרצה עם logging מפורט
```powershell
pytest tests/integration/api/test_singlechannel_view_mapping.py -v -s --log-cli-level=INFO
```

### הרצה עם environment ספציפי
```powershell
pytest tests/integration/api/test_singlechannel_view_mapping.py --env=staging -v

pytest tests/integration/api/test_singlechannel_view_mapping.py --env=production -v
```

### הרצה עם Allure reporting
```powershell
# צור דו"ח
pytest tests/integration/api/test_singlechannel_view_mapping.py --alluredir=reports/allure-results

# הצג דו"ח
allure serve reports/allure-results
```

---

## 🔍 בדיקת הקוד בלי הרצה

### בדיקת syntax
```powershell
python -m py_compile tests/integration/api/test_singlechannel_view_mapping.py
```

### בדיקת imports
```powershell
python -c "import tests.integration.api.test_singlechannel_view_mapping"
```

### רשימת הטסטים (ללא הרצה)
```powershell
pytest tests/integration/api/test_singlechannel_view_mapping.py --collect-only
```

---

## 🐛 פתרון בעיות נפוצות

### שגיאה: "pytest not found"
```powershell
# התקן pytest
pip install pytest

# או
pip install -r requirements.txt
```

### שגיאה: "ModuleNotFoundError: No module named 'src'"
```powershell
# ודא שאתה בתיקייה הנכונה
cd c:\Projects\focus_server_automation

# או הוסף את התיקייה ל-PYTHONPATH
$env:PYTHONPATH = "c:\Projects\focus_server_automation"
```

### שגיאה: "ConfigurationError"
```powershell
# בדוק את config/environments.yaml
# ודא ש-focus_server.base_url מוגדר
```

### שגיאה: "Connection refused"
```powershell
# ודא ש-Focus Server פועל
# או שה-port-forward מוגדר (אם רץ ב-K8s)

# בדוק connectivity
curl http://localhost:5000/health
```

---

## 📊 תוצאות מצופות

### הצלחה
```
tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewHappyPath::test_configure_singlechannel_mapping PASSED [100%]

========================= 1 passed in 2.34s =========================
```

### כישלון
```
tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewHappyPath::test_configure_singlechannel_mapping FAILED

AssertionError: Expected stream_amount=1 for SINGLECHANNEL, got 2
```

**במקרה של כישלון**: השתמש ב-[Bug Ticket Template](BUG_TICKET_SINGLECHANNEL_VIEW_TEMPLATE.md)

---

## 🔄 הרצה אוטומטית (CI/CD)

### GitHub Actions
צור קובץ: `.github/workflows/singlechannel-tests.yml`

```yaml
name: SingleChannel View Tests

on:
  push:
    paths:
      - 'tests/integration/api/test_singlechannel_view_mapping.py'
      - 'src/apis/focus_server_api.py'
      - 'src/models/focus_server_models.py'
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run SingleChannel tests
        run: |
          pytest tests/integration/api/test_singlechannel_view_mapping.py -v --tb=short
        env:
          FOCUS_SERVER_URL: ${{ secrets.FOCUS_SERVER_URL }}
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: reports/
```

---

## 📝 רישום תוצאות

### יצירת HTML report
```powershell
pytest tests/integration/api/test_singlechannel_view_mapping.py --html=reports/singlechannel-report.html --self-contained-html
```

### יצירת JSON report
```powershell
pytest tests/integration/api/test_singlechannel_view_mapping.py --json-report --json-report-file=reports/singlechannel-report.json
```

### יצירת Coverage report
```powershell
pytest tests/integration/api/test_singlechannel_view_mapping.py --cov=src.apis.focus_server_api --cov-report=html:reports/coverage
```

---

## ✅ Checklist לפני הרצה

- [ ] Python 3.11+ מותקן
- [ ] Dependencies מותקנים (`pip install -r requirements.txt`)
- [ ] Focus Server זמין ופועל
- [ ] Port-forward מוגדר (אם רלוונטי)
- [ ] Configuration תקינה (`config/environments.yaml`)
- [ ] PYTHONPATH מוגדר נכון

---

## 📞 עזרה נוספת

**קבצי תיעוד**:
- 🚀 [Quick Start (Hebrew)](SINGLECHANNEL_VIEW_TEST_QUICKSTART.md)
- 📖 [Full Guide (English)](docs/SINGLECHANNEL_VIEW_TEST_GUIDE.md)
- 🐛 [Bug Templates](BUG_TICKET_SINGLECHANNEL_VIEW_TEMPLATE.md)
- 📊 [Executive Summary](SINGLECHANNEL_VIEW_TEST_SUMMARY.md)

**קוד מקור**:
- 💻 [Test Code](tests/integration/api/test_singlechannel_view_mapping.py)

---

**נוצר ב**: 2025-10-12  
**גרסה**: 1.0  
**סטטוס**: ✅ מוכן להרצה

