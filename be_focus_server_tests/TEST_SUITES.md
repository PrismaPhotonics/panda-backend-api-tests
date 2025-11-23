# Test Suites Guide

**תאריך עדכון:** 2025-11-19  
**גרסה:** 1.0

---

## 📋 סקירה כללית

פרויקט `be_focus_server_tests` מאורגן לפי קטגוריות בדיקות שונות. מסמך זה מסביר את השימוש ב-test suites השונים.

---

## 🏷️ מרקרים (Markers)

### מרקרי Test Suites

#### `@pytest.mark.smoke`
**מטרה:** בדיקות מהירות וקריטיות  
**זמן ריצה:** < 5 דקות  
**תדירות:** כל commit/PR  
**שימוש:**
```python
@pytest.mark.smoke
@pytest.mark.critical
def test_health_check():
    """Smoke test - health check endpoint"""
    pass
```

**קריטריונים:**
- ✅ בדיקות מהירות (< 30 שניות)
- ✅ בדיקות קריטיות (health checks, connectivity)
- ✅ בדיקות בסיסיות ללא תלויות מורכבות
- ✅ בדיקות שמוודאות שהמערכת עובדת

**דוגמאות:**
- Health check endpoints
- Basic connectivity (MongoDB, Kubernetes, SSH)
- Critical API endpoints (GET /channels, GET /ack)

---

#### `@pytest.mark.regression`
**מטרה:** בדיקות אינטגרציה מלאות  
**זמן ריצה:** ~20-30 דקות  
**תדירות:** לפני merge ל-main  
**שימוש:**
```python
@pytest.mark.regression
@pytest.mark.integration
def test_api_endpoint():
    """Regression test - API endpoint"""
    pass
```

**קריטריונים:**
- ✅ כל הבדיקות עם `@pytest.mark.regression`
- ✅ בדיקות שכבר עברו בעבר
- ✅ בדיקות שמוודאות שלא נשבר דבר
- ✅ בדיקות אינטגרציה מלאות

**דוגמאות:**
- כל בדיקות ה-API
- בדיקות אינטגרציה
- בדיקות תשתית

---

#### `@pytest.mark.nightly`
**מטרה:** כל הבדיקות כולל slow/load/stress  
**זמן ריצה:** ~60-120 דקות  
**תדירות:** פעם ביום (2 AM UTC)  
**שימוש:**
```python
@pytest.mark.nightly
@pytest.mark.slow
def test_load_capacity():
    """Nightly test - load capacity"""
    pass
```

**קריטריונים:**
- ✅ כל הבדיקות (smoke + regression)
- ✅ בדיקות איטיות (`@pytest.mark.slow`)
- ✅ בדיקות עומס (`@pytest.mark.load`)
- ✅ בדיקות לחץ (`@pytest.mark.stress`)

**דוגמאות:**
- Load tests
- Stress tests
- Long-running stability tests
- Performance tests

---

### מרקרי Priority

#### `@pytest.mark.critical`
**מטרה:** בדיקות קריטיות (חייבות לעבור)  
**שימוש:**
```python
@pytest.mark.critical
@pytest.mark.smoke
def test_critical_functionality():
    """Critical test - must pass"""
    pass
```

#### `@pytest.mark.high`
**מטרה:** בדיקות בעדיפות גבוהה  
**שימוש:**
```python
@pytest.mark.high
@pytest.mark.regression
def test_important_feature():
    """High priority test"""
    pass
```

#### `@pytest.mark.medium`
**מטרה:** בדיקות בעדיפות בינונית  
**שימוש:**
```python
@pytest.mark.medium
@pytest.mark.regression
def test_standard_feature():
    """Medium priority test"""
    pass
```

#### `@pytest.mark.low`
**מטרה:** בדיקות בעדיפות נמוכה  
**שימוש:**
```python
@pytest.mark.low
@pytest.mark.regression
def test_optional_feature():
    """Low priority test"""
    pass
```

---

## 🚀 הרצת Test Suites

### Smoke Tests
```bash
# הרצת כל ה-smoke tests
pytest -m smoke -v

# הרצת smoke tests קריטיים בלבד
pytest -m "smoke and critical" -v

# הרצת smoke tests עם max failures
pytest -m smoke -v --maxfail=5
```

### Regression Tests
```bash
# הרצת כל ה-regression tests
pytest -m regression -v

# הרצת regression tests בעדיפות גבוהה
pytest -m "regression and (critical or high)" -v

# הרצת regression tests ללא slow tests
pytest -m "regression and not slow" -v
```

### Nightly Tests
```bash
# הרצת כל ה-nightly tests
pytest -m nightly -v

# הרצת כל הבדיקות (smoke + regression + nightly)
pytest -m "smoke or regression or nightly" -v

# הרצת nightly tests כולל slow/load/stress
pytest -m "nightly or slow or load or stress" -v
```

### Priority-based Selection
```bash
# הרצת בדיקות קריטיות בלבד
pytest -m critical -v

# הרצת בדיקות בעדיפות גבוהה ובינונית
pytest -m "high or medium" -v

# הרצת בדיקות בעדיפות נמוכה
pytest -m low -v
```

### Combinations
```bash
# Smoke tests קריטיים בעדיפות גבוהה
pytest -m "smoke and critical and high" -v

# Regression tests בעדיפות בינונית ונמוכה
pytest -m "regression and (medium or low)" -v

# Nightly tests ללא slow tests
pytest -m "nightly and not slow" -v
```

---

## 📊 Test Suite Statistics

### Smoke Tests
- **מספר בדיקות:** ~50 בדיקות
- **זמן ריצה:** < 5 דקות
- **תדירות:** כל commit/PR

### Regression Tests
- **מספר בדיקות:** ~200+ בדיקות
- **זמן ריצה:** ~20-30 דקות
- **תדירות:** לפני merge ל-main

### Nightly Tests
- **מספר בדיקות:** כל הבדיקות (~300+)
- **זמן ריצה:** ~60-120 דקות
- **תדירות:** פעם ביום (2 AM UTC)

---

## 🔧 תצורת CI/CD

### Smoke Tests Workflow
```yaml
name: Smoke Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run smoke tests
        run: pytest -m smoke -v --maxfail=5
```

### Regression Tests Workflow
```yaml
name: Regression Tests
on:
  push:
    branches: [main]

jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run regression tests
        run: pytest -m regression -v
```

### Nightly Tests Workflow
```yaml
name: Nightly Full Suite
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
  workflow_dispatch:

jobs:
  nightly:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run nightly tests
        run: pytest -m "smoke or regression or nightly" -v
```

---

## 📝 הנחיות לכתיבת בדיקות

### מתי להשתמש ב-`@pytest.mark.smoke`?
- ✅ בדיקות מהירות (< 30 שניות)
- ✅ בדיקות קריטיות (health checks, connectivity)
- ✅ בדיקות בסיסיות ללא תלויות מורכבות

### מתי להשתמש ב-`@pytest.mark.regression`?
- ✅ כל בדיקות האינטגרציה
- ✅ בדיקות שכבר עברו בעבר
- ✅ בדיקות שמוודאות שלא נשבר דבר

### מתי להשתמש ב-`@pytest.mark.nightly`?
- ✅ בדיקות איטיות (`@pytest.mark.slow`)
- ✅ בדיקות עומס (`@pytest.mark.load`)
- ✅ בדיקות לחץ (`@pytest.mark.stress`)
- ✅ בדיקות יציבות ארוכות טווח

### מתי להשתמש במרקרי Priority?
- ✅ `@pytest.mark.critical` - בדיקות חיוניות (חייבות לעבור)
- ✅ `@pytest.mark.high` - בדיקות חשובות
- ✅ `@pytest.mark.medium` - בדיקות סטנדרטיות
- ✅ `@pytest.mark.low` - בדיקות אופציונליות

---

## ✅ Best Practices

1. **תמיד להוסיף לפחות מרקר אחד** - `smoke`, `regression`, או `nightly`
2. **להוסיף מרקר priority** - `critical`, `high`, `medium`, או `low`
3. **לשלב מרקרים** - לדוגמה: `@pytest.mark.smoke` + `@pytest.mark.critical`
4. **לתעד בדיקות** - להוסיף docstring מפורט לכל בדיקה
5. **לבדוק לפני commit** - להריץ את הבדיקות הרלוונטיות לפני commit

---

## 📚 קישורים נוספים

- [README.md](./README.md) - תיעוד כללי של הפרויקט
- [conftest.py](./conftest.py) - הגדרת fixtures ומרקרים
- [pytest.ini](../pytest.ini) - תצורת pytest

---

**עודכן לאחרונה:** 2025-11-19  
**מתחזק:** QA Automation Team

