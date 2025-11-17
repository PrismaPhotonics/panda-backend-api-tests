# Sanity Check - סיכום יישום

**תאריך:** 2025-11-06  
**סטטוס:** ✅ הושלם בהצלחה

---

## מה נוצר?

### 1. מודול Sanity Checker
**קובץ:** `src/utils/sanity_checker.py`

מודול שמבצע בדיקות מהירות של כל הקומפוננטות התשתיתיות לפני הרצת טסטים.

**קומפוננטות שנבדקות:**
- ✅ **Focus Server API** - בדיקת חיבור ו-health check
- ✅ **MongoDB** - בדיקת חיבור ו-ping
- ✅ **Kubernetes** - בדיקת חיבור ל-cluster
- ✅ **SSH** - בדיקת חיבור ל-jump host
- ✅ **RabbitMQ** - בדיקה אופציונלית (לא חובה)

### 2. אינטגרציה עם pytest
**קובץ:** `tests/conftest.py`

ה-sanity check רץ אוטומטית לפני כל הרצת טסטים דרך `pytest_sessionstart` hook.

### 3. מדריך שימוש
**קובץ:** `docs/02_user_guides/SANITY_CHECK_GUIDE.md`

מדריך מפורט בעברית לשימוש ב-sanity check.

---

## איך זה עובד?

### הרצה רגילה (עם Sanity Check)

```powershell
# Sanity check ירוץ אוטומטית לפני הטסטים
pytest tests/integration/api/test_api_endpoints_high_priority.py -v
```

**מה קורה:**
1. Sanity check מתחיל אוטומטית
2. בודק את כל הקומפוננטות (Focus Server, MongoDB, Kubernetes, SSH)
3. מדפיס סיכום
4. אם הכל עבר - ממשיך להרצת הטסטים
5. אם משהו נכשל - מדפיס אזהרה וממשיך (או עוצר אם תרצה)

### דוגמה לפלט:

```
====================================================================================================
SANITY CHECK: Verifying infrastructure components...
====================================================================================================
Environment: staging

Checking Focus Server API...
  ✅ PASS: Focus Server is responding and accessible (44.2ms)
Checking MongoDB...
  ✅ PASS: MongoDB is reachable and responding (400.6ms)
Checking Kubernetes...
  ✅ PASS: Kubernetes cluster is reachable (2 nodes) (85347.1ms)
Checking SSH...
  ✅ PASS: SSH connection successful (662.7ms)
Checking RabbitMQ...
  ✅ PASS: RabbitMQ manager available (connection check skipped - optional) (1.4ms)

====================================================================================================
SANITY CHECK SUMMARY
====================================================================================================
Total checks: 5
✅ Passed: 5
❌ Failed: 0
⏱️  Total duration: 86461.8ms

====================================================================================================

✅ All sanity checks passed - infrastructure is ready for testing
```

---

## אפשרויות

### 1. דילוג על Sanity Check

```powershell
pytest tests/ -v --skip-sanity-check
```

**הערה:** לא מומלץ - הטסטים עלולים להיכשל בגלל בעיות תשתית.

### 2. עצירה מיידית אם Sanity Check נכשל

אם תרצה שהטסטים יעצרו אם sanity check נכשל, אפשר לשנות ב-`tests/conftest.py`:

```python
# Option 1: Fail immediately (uncomment to enable)
import sys
logger.error("Stopping test execution due to sanity check failures")
sys.exit(1)
```

**כרגע:** ברירת המחדל היא להמשיך עם אזהרה.

### 3. הרצה בסביבת Local

```powershell
# בסביבת local, sanity check לא ירוץ אוטומטית
pytest tests/ -v --env local
```

---

## יתרונות

1. ✅ **חיסכון זמן** - מזהה בעיות תשתית לפני הרצת כל הטסטים
2. ✅ **דוח ברור** - רואה בדיוק איזה קומפוננטה לא עובדת
3. ✅ **אוטומטי** - רץ לפני כל הרצת טסטים ללא צורך בפעולה נוספת
4. ✅ **מהיר** - בדיקות קצרות (כמה שניות)
5. ✅ **גמיש** - אפשר לדלג או לשנות התנהגות

---

## קבצים שנוצרו/עודכנו

1. ✅ `src/utils/sanity_checker.py` - מודול sanity check (חדש)
2. ✅ `tests/conftest.py` - אינטגרציה עם pytest hooks (עודכן)
3. ✅ `docs/02_user_guides/SANITY_CHECK_GUIDE.md` - מדריך שימוש (חדש)

---

## בדיקה

✅ **Sanity check נבדק ועובד!**

כל 5 הקומפוננטות נבדקות בהצלחה:
- Focus Server API ✅
- MongoDB ✅
- Kubernetes ✅
- SSH ✅
- RabbitMQ ✅

---

## שימוש עתידי

**לפני כל הרצת טסטים:**
```powershell
# Sanity check ירוץ אוטומטית
pytest tests/integration/api/test_api_endpoints_high_priority.py -v
```

**אם יש בעיות תשתית:**
- Sanity check יזהה אותן מיד
- תקבל דוח ברור על מה לא עובד
- תוכל לתקן את הבעיות לפני הרצת הטסטים

---
*יישום הושלם: 2025-11-06*

