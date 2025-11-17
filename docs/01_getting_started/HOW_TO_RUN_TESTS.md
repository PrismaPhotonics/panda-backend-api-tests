# 🚀 מדריך הרצת טסטים - Focus Server Automation

## 📋 תוכןudo
1. [הרצת כל הטסטים](#הרצת-כל-הטסטים)
2. [הרצת טסטים ספציפיים](#הרצת-טסטים-ספציפיים)
3. [הרצה לפי קטגוריות](#הרצה-לפי-קטגוריות)
4. [הרצה לפי Markers](#הרצה-לפי-markers)
5. [אופציות מתקדמות](#אופציות-מתקדמות)

---

## ✅ הרצת כל הטסטים

### פקודה בסיסית (המלצה)
```bash
# הרצת כל הטסטים עם פירוט מלא
pytest tests/ -v

# או פשוט (pytest יזהה אוטומטית את תיקיית tests/)
pytest -v
```

### עם פלט מפורט יותר
```bash
# עם פלט מפורט + לוגים
pytest tests/ -v -s

# עם פלט מפורט + לוגים + תוצאות מРувим
pytest tests/ -v -s --tb=short
```

### עם דוח HTML
```bash
# יצירת דוח HTML
pytest tests/ -v --html=reports/test_report.html --self-contained-html
```

---

## 🎯 הרצת טסטים ספציפיים

### טסט ספציפי
```bash
# טסט אחד בלבד
pytest tests/integration/api/test_health_check.py::test_health_check_valid_response -v

# כל הטסטים בקובץ מסויים
pytest tests/integration/api/test_health_check.py -v
```

### טסטים שעות בודקות (PZ-13857, PZ-13822)
```bash
# PZ-13857 - SingleChannel NFFT Validation
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelErrorHandling::test_singlechannel_with_invalid_nfft -v

# PZ-13822 - SingleChannel Rejects Invalid NFFT Value
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelErrorHandling::test_singlechannel_rejects_invalid_nfft_value -v

# כל טסטי Error Handling של SingleChannel
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelErrorHandling -v
```

---

## 📁 הרצה לפי קטגוריות

### Integration Tests
```bash
# כל טסטי Integration
pytest tests/integration/ -v

# רק טסטי API
pytest tests/integration/api/ -v

# טסטי Performance
pytest tests/integration/performance/ -v

# טסטי E2E
pytest tests/integration/e2e/ -v
```

### Infrastructure Tests
```bash
pytest tests/infrastructure/ -v
```

### Data Quality Tests
```bash
pytest tests/data_quality/ -v
```

### Unit Tests
```bash
pytest tests/unit/ -v
```

### Security Tests
```bash
pytest tests/security/ -v
```

### Stress Tests
```bash
pytest tests/stress/ -v
```

### Performance Tests
```bash
pytest tests/performance/ -v
```

---

## 🏷️ הרצה לפי Markers

### לפי קטגוריה (Xray markers)
```bash
# Integration tests
pytest -m integration -v

# API tests
pytest -m api -v

# Infrastructure tests
pytest -m infrastructure -v

# Data quality tests
pytest -m data_quality -v

# Performance tests
pytest -m performance -v

# Security tests
pytest -m security -v
```

### לפי חומרה
```bash
# Critical tests only
pytest -m critical -v

# Smoke tests
pytest -m smoke -v

# Slow tests
pytest -m slow -v
```

### מספר markers יחד
```bash
# Integration + Critical
pytest -m "integration and critical" -v

# API אבל לא slow
pytest -m "api and not slow" -v
```

---

## 🔍 הרצה לפי Xray Test ID

### טסט ספציפי לפי ID
```bash
# הרצת טסט לפי Xray ID (PZ-XXXXX)
pytest -k "PZ-13857" -v
pytest -k "PZ-13822" -v
```

### מספר טסטים לפי IDs
```bash
# מספר טסטים (OR)
pytest -k "PZ-13857 or PZ-13822" -v
```

---

## ⚙️ אופציות מתקדמות

### עם Coverage
```bash
# עם דוח כיסוי
pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# דוח כיסוי ב-HTML
pytest tests/ -v --cov=src --cov-report=html
# פתח: htmlcov/index.html
```

### עם Filter
```bash
# רק טסטים שעברו בפעם הקודמת
pytest tests/ -v --lf

# רק טסטים שנכשלו בפעם הקודמת
pytest tests/ -v --ff
```

### עם Parallel Execution
```bash
# הרצה במקביל (דורש pytest-xdist)
pytest tests/ -v -n auto

# מספר workers ספציפי
pytest tests/ -v -n 4
```

### עם Timeout
```bash
# timeout לכל טסט (דורש pytest-timeout)
pytest tests/ -v --timeout=300
```

### Stop on First Failure
```bash
# עצירה בכשל הראשון
pytest tests/ -v -x

# עצירה לאחר N כשלים
pytest tests/ -v --maxfail=3
```

### עם Verbose Output
```bash
# פלט מפורט מאוד
pytest tests/ -vv

# פלט מפורט ביותר
pytest tests/ -vvv
```

### עם Logging
```bash
# הצגת לוגים במהלך הרצה
pytest tests/ -v -s --log-cli-level=INFO

# שמירת לוגים לקובץ
pytest tests/ -v -- 자: logs/test_run.log
```

---

## 📊 דוגמאות שימושיות

### בדיקה מהירה (Smoke Test)
```bash
# רק טסטים critical
pytest -m "critical or smoke" -v
```

### בדיקה מקיפה לפני Commit
```bash
# כל הטסטים עם coverage
pytest tests/ -v --cov=src --cov-report=term-missing -x
```

### בדיקת טסטים חדשים
```bash
# רק הטסטים שעודכנו לאחרונה (git)
pytest tests/ -v --lf

# או טסטים ספציפיים
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelErrorHandling -v
```

### בדיקת תקינות מהירה
```bash
# איסוף של כל הטסטים (לא להריץ, רק לראות כמה יש)
pytest tests/ --collect-only

# רשימת כל הטסטים עם Xray markers
pytest tests/ --collect-only | grep -i "PZ-"
```

---

## 🎯 המלצות

### עבור בדיקה ראשונית (Quick Check)
```bash
pytest tests/ -v -x --tb=short
```

### עבור בדיקה מקיפה (Full Suite)
```bash
pytest tests/ -v --html=reports/test_report.html --self-contained-html --cov=src --cov-report=html
```

### עבור בדיקת טסטים חדשים בלבד
```bash
# הרצת רק הטסטים של PZ-13857 ו-PZ-13822
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelErrorHandling::test_singlechannel_with_invalid_nfft tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelErrorHandling::test_singlechannel_rejects_invalid_nfft_value -v
```

---

## 📝 הערות חשובות

1. **Environment**: ודא שהסביבה מוגדרת נכון (`config/environments.yaml`)
2. **Dependencies**: ודא שכל התלויות מותקנות (`pip install -r requirements.txt`)
3. **Network**: הטסטים דורשים גישה לשרתים (MongoDB, RabbitMQ, K8s)
4. **Credentials**: ודא שה-credentials מוגדרים נכון ב-config

---

## 🆘 פתרון בעיות

### אם הטסטים לא רצים:
```bash
# בדוק ש-pytest מותקן
pytest --version

# בדוק את ההגדרות
pytest --collect-only

# הרץ עם פלט מפורט
pytest tests/ -vv -s
```

### אם יש שגיאת Import:
```bash
# ודא שה-PYTHONPATH נכון
export PYTHONPATH=.

# או הרץ מהתיקייה הראשית
cd c:\Projects\focus_server_automation
pytest tests/ -v
```

---

**לעדכונים:** עיין ב-`pytest.ini` וב-`tests/README.md`
