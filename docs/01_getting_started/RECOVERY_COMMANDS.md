# 🔧 פקודות שחזור מדויקות - טסטים חסרים

**תאריך:** 22 אוקטובר 2025  
**מטרה:** שחזור קבצי טסט שנמחקו ב-reorganization

---

## ⚡ שחזור מהיר (מומלץ להתחלה)

### שחזור רק את הקובץ הכי חסר:

```bash
# Performance tests (הכי חסר!)
git checkout da81742 -- tests/integration/performance/test_performance_high_priority.py

# בדוק שהוא עובד
pytest tests/integration/performance/test_performance_high_priority.py -v --collect-only
```

**תוצאה:** תקבל בחזרה 5 performance tests (P95/P99, Concurrent)

---

## 🔄 שחזור מלא (כל 5 הקבצים)

### אופציה 1: שחזור אחד-אחד

```bash
# 1. Config validation tests (15 tests)
git checkout da81742 -- tests/integration/api/test_config_validation_high_priority.py

# 2. API endpoints tests (5 tests)
git checkout da81742 -- tests/integration/api/test_api_endpoints_high_priority.py

# 3. Historic tests (5 tests)
git checkout da81742 -- tests/integration/api/test_historic_high_priority.py

# 4. SingleChannel tests (7 tests)
git checkout da81742 -- tests/integration/api/test_singlechannel_high_priority.py

# 5. Performance tests (5 tests)
git checkout da81742 -- tests/integration/performance/test_performance_high_priority.py
```

### אופציה 2: שחזור בפקודה אחת

```bash
# כל טסטי API ביחד
git checkout da81742 -- \
  tests/integration/api/test_config_validation_high_priority.py \
  tests/integration/api/test_api_endpoints_high_priority.py \
  tests/integration/api/test_historic_high_priority.py \
  tests/integration/api/test_singlechannel_high_priority.py \
  tests/integration/performance/test_performance_high_priority.py
```

---

## 🎯 שחזור סלקטיבי (מומלץ!)

### מה כדאי לשחזר? (לפי עדיפות)

#### 1. ✅ חובה - Performance Tests
```bash
git checkout da81742 -- tests/integration/performance/test_performance_high_priority.py
```
**למה?** אין אף performance test אחר (חוץ מ-MongoDB outage)

#### 2. ✅ מומלץ - API Endpoints Tests
```bash
git checkout da81742 -- tests/integration/api/test_api_endpoints_high_priority.py
```
**למה?** GET /channels לא נבדק בשום מקום אחר

#### 3. ⚠️ אופציונלי - Config Validation Tests
```bash
git checkout da81742 -- tests/integration/api/test_config_validation_high_priority.py
```
**למה?** יש validation tests אחרים, אבל לא מכסים הכל

#### 4. ⚠️ אופציונלי - Historic Tests
```bash
git checkout da81742 -- tests/integration/api/test_historic_high_priority.py
```
**למה?** יש `test_historic_playback_flow.py` שמכסה חלק

#### 5. ❌ לא מומלץ - SingleChannel Tests
```bash
# אל תשחזר את זה!
# git checkout da81742 -- tests/integration/api/test_singlechannel_high_priority.py
```
**למה?** יש replacement טוב: `test_singlechannel_view_mapping.py`

---

## 📦 אחרי שחזור - בדיקות

### בדוק שהקבצים חזרו:
```bash
# רשימת כל הקבצים שחזרו
ls -la tests/integration/api/*_high_priority.py
ls -la tests/integration/performance/*_high_priority.py
```

### בדוק כמה טסטים יש:
```bash
# ספירה מהירה
pytest tests/integration/api/test_*_high_priority.py --collect-only | Select-String "test session starts" -Context 0,3

pytest tests/integration/performance/test_performance_high_priority.py --collect-only | Select-String "test session starts" -Context 0,3
```

### בדוק שהם עוברים (smoke test):
```bash
# הרץ רק טסט אחד מכל קובץ
pytest tests/integration/api/test_config_validation_high_priority.py::TestMissingRequiredFields::test_missing_channels_field -v

pytest tests/integration/performance/test_performance_high_priority.py::TestAPILatencyP95::test_config_endpoint_latency_p95_p99 -v -s
```

---

## 🔍 בדיקה מתקדמת - השוואת קבצים

### השווה קובץ ישן לחדש (SingleChannel example):

```bash
# 1. חלץ גרסה ישנה לקובץ זמני
git show da81742:tests/integration/api/test_singlechannel_high_priority.py > /tmp/old_singlechannel.py

# 2. פתח diff עם VS Code
code --diff /tmp/old_singlechannel.py tests/integration/api/test_singlechannel_view_mapping.py

# 3. בדוק overlaps
```

**מה לחפש:**
- ✅ יש test functions זהים?
- ✅ יש coverage זהה?
- ⚠️ יש gaps?

---

## 📝 אחרי שחזור - עדכון Imports

הקבצים הישנים עשויים לדרוש עדכון imports למבנה החדש:

### בדוק שגיאות import:
```bash
python -m pytest tests/integration/api/test_config_validation_high_priority.py --collect-only 2>&1 | Select-String "ImportError|ModuleNotFoundError"
```

### תקן imports אם נדרש:
```python
# אם יש שגיאת import, פתח את הקובץ ועדכן:

# ישן:
from src.apis.focus_server_api import FocusServerAPI
from src.models import ConfigureRequest

# חדש (אם צריך):
from src.apis.focus_server_api import FocusServerAPI
from src.models.focus_server_models import ConfigureRequest
```

---

## 🧪 הרצת טסטים אחרי שחזור

### הרצת כל performance tests:
```bash
# סביבת production
$env:TEST_ENV="new_production"
pytest tests/integration/performance/test_performance_high_priority.py -v -s

# עם logging מפורט
pytest tests/integration/performance/test_performance_high_priority.py -v -s --log-cli-level=INFO
```

### הרצת כל config validation tests:
```bash
pytest tests/integration/api/test_config_validation_high_priority.py -v
```

### הרצת רק P95 latency test:
```bash
pytest tests/integration/performance/test_performance_high_priority.py::TestAPILatencyP95::test_config_endpoint_latency_p95_p99 -v -s
```

### הרצת concurrent tasks test (זהירות - stress test!):
```bash
# זה stress test - עלול להשפיע על מערכת
pytest tests/integration/performance/test_performance_high_priority.py::TestConcurrentTaskLimit::test_concurrent_task_max_limit -v -s
```

---

## 🗂️ העברה למבנה החדש (אופציונלי)

אם אתה מעדיף לעבור למבנה החדש:

### מבנה ישן:
```
tests/integration/api/test_*_high_priority.py
tests/integration/performance/test_performance_high_priority.py
```

### מבנה חדש:
```
tests/api/endpoints/test_*_high_priority.py
tests/performance/test_performance_high_priority.py
tests/api/validation/test_config_validation_high_priority.py
```

### פקודות העברה:
```bash
# צור תיקיות חדשות
mkdir -p tests/api/endpoints
mkdir -p tests/api/validation

# העבר קבצים
mv tests/integration/api/test_api_endpoints_high_priority.py tests/api/endpoints/
mv tests/integration/api/test_config_validation_high_priority.py tests/api/validation/

# Performance נשאר במקום
# tests/integration/performance/ -> tests/performance/
```

---

## 🔙 ביטול שחזור (אם משהו השתבש)

### אם רוצה לבטל הכל:
```bash
# ביטול כל השינויים שלא committed
git restore tests/integration/api/test_*_high_priority.py
git restore tests/integration/performance/test_performance_high_priority.py

# או reset hard (זהירות!)
git reset --hard HEAD
```

---

## 📊 ספירת טסטים אחרי שחזור

```bash
# ספירה מדויקת
cd C:\Projects\focus_server_automation

Write-Host "Tests by file:"
Get-ChildItem -Path tests -Filter "*_high_priority.py" -Recurse | ForEach-Object {
    $testCount = (Select-String -Path $_.FullName -Pattern "^\s*def test_").Count
    Write-Host "  $($_.Name): $testCount tests"
}

$totalTests = (Get-ChildItem -Path tests -Filter "*_high_priority.py" -Recurse | ForEach-Object {
    (Select-String -Path $_.FullName -Pattern "^\s*def test_").Count
} | Measure-Object -Sum).Sum

Write-Host ""
Write-Host "Total high_priority tests: $totalTests"
```

**תוצאה צפויה אחרי שחזור מלא:** ~37 tests

---

## ✅ Checklist לאחר שחזור

- [ ] קבצים נשחזרו מ-git
- [ ] אין שגיאות import
- [ ] pytest --collect-only עובד
- [ ] הרצתי לפחות טסט אחד ועבר
- [ ] עדכנתי JIRA ל-"Automated"
- [ ] עדכנתי תיעוד (אם רלוונטי)
- [ ] committed ו-pushed לשרת

---

## 🚀 המלצה הסופית

### תחילה (5 דקות):
```bash
# 1. שחזר רק performance tests
git checkout da81742 -- tests/integration/performance/test_performance_high_priority.py

# 2. בדוק שהם קיימים
ls tests/integration/performance/test_performance_high_priority.py

# 3. הרץ smoke test
pytest tests/integration/performance/test_performance_high_priority.py::TestAPILatencyP95 --collect-only
```

### אם הכל עובד (10 דקות):
```bash
# 4. שחזר גם API endpoints
git checkout da81742 -- tests/integration/api/test_api_endpoints_high_priority.py

# 5. בדוק שהכל עובד
pytest tests/integration/api/test_api_endpoints_high_priority.py --collect-only

# 6. Commit!
git add tests/integration/performance/test_performance_high_priority.py
git add tests/integration/api/test_api_endpoints_high_priority.py
git commit -m "chore: restore high priority performance and API tests from backup

Restored from commit da81742:
- test_performance_high_priority.py (P95/P99 latency, concurrent tasks)
- test_api_endpoints_high_priority.py (GET /channels endpoint)

These tests cover JIRA tickets: PZ-13770, PZ-13896, PZ-13419"
```

---

**כל הפקודות מוכנות - פשוט Copy & Paste!** 🎯

**שאלות? בעיות? תגיד לי!** 💬

