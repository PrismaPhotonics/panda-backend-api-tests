# ⚠️  Performance Tests - Status & Migration Plan

**תאריך:** 23 אוקטובר 2025  
**סטטוס:** ❌ **לא עובדים - דורשים API חדש**

---

## 🚨 **בעיה**

הטסטים האלה משתמשים ב-API חדש שלא קיים בשרת הנוכחי:

```python
# ❌ API שלא קיים:
POST /config/{task_id}

# ✅ API זמין:
POST /configure
```

**שרת נוכחי:** `pzlinux:10.7.122`  
**Endpoints זמינים:** ראה `documentation/testing/FOCUS_SERVER_API_ENDPOINTS.md`

---

## 📊 **טסטים מושפעים**

### **קבצים:**
```
tests/integration/performance/
├── test_performance_high_priority.py   ← 11 occurrences
└── (other performance tests...)
```

### **סטטיסטיקה:**
- **טסטים כושלים:** ~100+
- **סיבת כישלון:** `404 Not Found - /config/{task_id}`
- **השפעה:** Performance benchmarks לא זמינים

---

## 🔧 **אופציות תיקון**

### **אופציה 1: עדכן שרת (מומלץ!)** ⭐

**יתרונות:**
- ✅ לא צריך לשנות טסטים
- ✅ Forward compatibility
- ✅ API חדש ומשופר

**חסרונות:**
- ⏱️ דורש deployment
- 📋 צריך לתאם עם DevOps

**איך לבצע:**
```bash
# 1. בדוק איזו גרסה תומכת ב-API החדש
kubectl describe deployment focus-server -n <namespace>

# 2. עדכן image:
kubectl set image deployment/focus-server \
  focus-server=pzlinux:<newer-version> \
  -n <namespace>

# 3. המתן לrollout:
kubectl rollout status deployment/focus-server -n <namespace>

# 4. אמת:
curl -X POST https://10.10.100.100/focus-server/config/test_123 \
  -H "Content-Type: application/json" \
  -d '{"view_type": "0", ...}'
```

---

### **אופציה 2: תקן טסטים (זמני)**

**יתרונות:**
- ⚡ מהיר
- ✅ עובד עם שרת נוכחי

**חסרונות:**
- ⚠️ צריך לשנות הרבה קבצים
- ⚠️ לא יעבוד עם API חדש

**דוגמת תיקון:**

```python
# ❌ לפני:
from src.models.focus_server_models import ConfigTaskRequest, ConfigTaskResponse

def test_something(focus_server_api):
    task_id = generate_task_id("test")
    config_request = ConfigTaskRequest(...)
    response = focus_server_api.config_task(task_id, config_request)
```

```python
# ✅ אחרי:
from src.models.focus_server_models import ConfigureRequest, ConfigureResponse

def test_something(focus_server_api):
    config_request = ConfigureRequest(...)
    response = focus_server_api.configure_streaming_job(config_request)
```

**שינויים נדרשים:**
1. `ConfigTaskRequest` → `ConfigureRequest`
2. `ConfigTaskResponse` → `ConfigureResponse`
3. `config_task(task_id, payload)` → `configure_streaming_job(payload)`
4. שדות: `canvasInfo` → `displayInfo`, `sensors` → `channels`

**זמן משוער:** 3-4 שעות

---

### **אופציה 3: סמן כ-SKIP (נוכחי)** 🏷️

**יתרונות:**
- ⚡⚡ מהיר מאוד (5 דקות)
- 📋 מתעד בבירור את המצב
- ✅ לא שובר שום דבר

**חסרונות:**
- ⚠️ טסטים לא רצים

**מימוש:**
```python
# בראש הקובץ:
import pytest

pytestmark = pytest.mark.skip(
    reason="Performance tests require /config/{task_id} API not available on current server (pzlinux:10.7.122). "
           "Either update server or migrate tests to use /configure API. "
           "See: tests/integration/performance/PERFORMANCE_TESTS_STATUS.md"
)
```

---

## 📋 **המלצה**

**עכשיו:** אופציה 3 (SKIP) - מהיר ובטוח  
**טווח קצר:** אופציה 1 (עדכן שרת) - מומלץ!  
**טווח ארוך:** אופציה 2 (תקן טסטים) - אם שרת לא מתעדכן

---

## 🎯 **Action Items**

### **מיידי:**
- [x] סמן טסטים עם `@pytest.mark.skip`
- [x] הוסף README זה
- [ ] עדכן CI/CD להתעלם מטסטים אלה

### **טווח קצר:**
- [ ] תאם עם DevOps לעדכון שרת
- [ ] בדוק איזו גרסה תומכת ב-API החדש
- [ ] תכנן deployment window

### **טווח בינוני:**
- [ ] אחרי עדכון שרת - הסר את ה-skip
- [ ] הרץ טסטים ווודא שעוברים
- [ ] עדכן baselines לperformance

---

## 📚 **מסמכים קשורים**

- `documentation/testing/FOCUS_SERVER_API_ENDPOINTS.md` - כל ה-endpoints הזמינים
- `tests/integration/api/test_config_validation_high_priority.py` - דוגמה לטסטים שעובדים
- `API_TEST_REPORT.md` (archived) - ניתוח API ישן vs חדש

---

**נוצר:** 23 אוקטובר 2025  
**עודכן:** 23 אוקטובר 2025  
**סטטוס:** 🟡 **ממתין לעדכון שרת**

