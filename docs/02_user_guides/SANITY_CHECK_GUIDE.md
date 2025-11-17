# מדריך שימוש ב-Sanity Check

## מה זה Sanity Check?

Sanity Check הוא בדיקה אוטומטית שמתבצעת **לפני** כל הרצת טסטים כדי לוודא שכל הקומפוננטות התשתיתיות פעילות ומתחברות.

## קומפוננטות שנבדקות

1. **Focus Server API** - בדיקת חיבור ו-health check
2. **MongoDB** - בדיקת חיבור ו-ping
3. **Kubernetes** - בדיקת חיבור ל-cluster
4. **SSH** - בדיקת חיבור ל-jump host
5. **RabbitMQ** - בדיקה אופציונלית (לא חובה)

## שימוש

### הרצה רגילה (עם Sanity Check)

```powershell
# Sanity check ירוץ אוטומטית לפני הטסטים
pytest tests/integration/api/test_api_endpoints_high_priority.py -v
```

### דילוג על Sanity Check (לא מומלץ)

```powershell
# אם אתה רוצה לדלג על sanity check
pytest tests/integration/api/test_api_endpoints_high_priority.py -v --skip-sanity-check
```

### הרצה בסביבת Local

```powershell
# בסביבת local, sanity check לא ירוץ אוטומטית
pytest tests/ -v --env local
```

## מה קורה אם Sanity Check נכשל?

**ברירת מחדל (נוכחי):**
- Sanity check מדפיס אזהרה
- הטסטים ממשיכים לרוץ
- טסטים שדורשים קומפוננטות שלא עובדות יכשלו

**אפשרות להפעיל עצירה מיידית:**
אם תרצה שהטסטים יעצרו אם sanity check נכשל, אפשר לשנות ב-`tests/conftest.py`:

```python
# Option 1: Fail immediately (uncomment to enable)
import sys
logger.error("Stopping test execution due to sanity check failures")
sys.exit(1)
```

## דוגמה לפלט

```
====================================================================================================
SANITY CHECK: Verifying infrastructure components...
====================================================================================================
Environment: staging

Checking Focus Server API...
  ✅ PASS: Focus Server is responding (got channels response) (245.3ms)
Checking MongoDB...
  ✅ PASS: MongoDB is reachable and responding (12.5ms)
Checking Kubernetes...
  ✅ PASS: Kubernetes cluster is reachable (2 nodes) (1234.5ms)
Checking SSH...
  ✅ PASS: SSH connection successful (567.8ms)
Checking RabbitMQ...
  ✅ PASS: RabbitMQ manager available (connection check skipped - optional) (0.1ms)

====================================================================================================
SANITY CHECK SUMMARY
====================================================================================================
Total checks: 5
✅ Passed: 5
❌ Failed: 0
⏱️  Total duration: 2050.2ms

====================================================================================================

✅ All sanity checks passed - infrastructure is ready for testing
```

## קבצים רלוונטיים

- `src/utils/sanity_checker.py` - מודול ה-sanity check
- `tests/conftest.py` - אינטגרציה עם pytest hooks
- `tests/infrastructure/test_external_connectivity.py` - טסטי connectivity מפורטים

## הערות

- Sanity check מתבצע פעם אחת לפני כל הטסטים (לא לפני כל טסט)
- Sanity check מהיר יחסית (כמה שניות)
- אם sanity check נכשל, זה לא אומר שכל הטסטים יכשלו - רק טסטים שדורשים את הקומפוננטה שנכשלה

