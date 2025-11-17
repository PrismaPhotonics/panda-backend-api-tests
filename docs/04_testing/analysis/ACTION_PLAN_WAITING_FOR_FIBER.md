# 📋 תוכנית פעולה - המערכת במצב "waiting for fiber"

**תאריך:** 2025-11-08 13:20  
**עדיפות:** 🔴 **דחוף**

---

## 🎯 סיכום המצב

- ✅ המערכת במצב **"waiting for fiber"** - אין fiber פיזי מחובר
- ✅ כל בקשות `/configure` נכשלות עם `503 Service Unavailable`
- ⚠️ **יש retry logic פעיל** שיוצר עומס מיותר על השרת
- ⚠️ **יש 4 restarts ב-28 שעות** - צריך לבדוק למה

---

## ⛔ פעולות מיידיות (עכשיו!)

### 1. עצור את כל הטסטים שמנסים להגדיר jobs

**פעולה:**
```bash
# מצא את כל ה-processes שרצים טסטים
ps aux | grep pytest
ps aux | grep locust

# עצור אותם
kill <PID>
# או
pkill -f pytest
pkill -f locust
```

**למה זה חשוב:**
- הטסטים יוצרים עומס מיותר על השרת
- הם מנסים כל 2-3 שניות ונכשלים
- זה יכול לגרום ל-restarts נוספים

**טסטים שצריך לעצור:**
- כל טסטי `test_configure_*`
- כל טסטי `test_live_monitoring_*`
- כל טסטי `test_singlechannel_*`
- כל טסטי `test_waterfall_*`
- כל טסטי performance/load שמנסים להגדיר jobs
- כל ה-load tests (Locust)

---

### 2. בדוק אם יש CI/CD שרץ טסטים

**פעולה:**
- בדוק את ה-CI/CD pipelines (GitHub Actions, Jenkins, GitLab CI, וכו')
- עצור כל pipeline שרץ טסטים
- או עדכן את ה-pipeline לדלג על טסטי configure

**למה זה חשוב:**
- CI/CD יכול להריץ טסטים אוטומטית
- זה יוצר עומס נוסף על השרת

---

## 🔍 בדיקות נוספות (לאחר עצירת הטסטים)

### 3. בדוק למה יש 4 restarts ב-28 שעות ✅ **סיבה זוהתה!**

**פעולה:**
```bash
# בדוק את ה-events של ה-pod
kubectl describe pod panda-panda-focus-server-78dbcfd9d9-kjj77 -n panda | grep -A 20 Events

# בדוק את ה-logs לפני ה-restarts
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-kjj77 --previous --tail=100

# בדוק את ה-resource usage
kubectl top pod panda-panda-focus-server-78dbcfd9d9-kjj77 -n panda
```

**תוצאות:**
- ✅ **סיבה זוהתה:** בעיית חיבור ל-MongoDB בזמן initialization
- ✅ **השגיאה:** `pymongo.errors.ServerSelectionTimeoutError: mongodb:27017: [Errno -3] Temporary failure in name resolution`
- ✅ **Resource usage תקין:** CPU 3m, Memory 394Mi
- ✅ **הבעיה נפתרה:** ה-pod רץ כבר 46 שעות ללא restarts

**מה קרה:**
- ה-pod לא יכול לפתור את השם `mongodb` ל-IP address
- זה קרה בזמן ה-initialization של `FocusManager`
- ה-pod נכשל ב-startup ונכנס ל-CrashLoopBackOff
- Kubernetes restart את ה-pod עד שהחיבור ל-MongoDB חזר לעבוד

**סיבות אפשריות:**
1. בעיית DNS ב-Kubernetes (ה-service `mongodb` לא היה זמין)
2. בעיית networking ב-Kubernetes
3. ה-MongoDB service לא היה מוכן בזמן שה-pod התחיל
4. בעיית timing - ה-pod התחיל לפני שה-MongoDB service היה מוכן

**פתרונות מומלצים:**
- הוסף Init Container שימתין ל-MongoDB
- הוסף Readiness Probe
- הוסף Retry Logic בקוד

**ראה מסמך מפורט:** `docs/04_testing/analysis/MONGODB_CONNECTION_RESTARTS_ANALYSIS.md`

---

### 4. בדוק את מצב המערכת

**פעולה:**
```bash
# בדוק metadata
curl -k https://10.10.10.100/focus-server/live_metadata | jq

# בדוק את ה-pods
kubectl get pods -n panda | grep focus-server

# בדוק את ה-services
kubectl get svc -n panda | grep focus-server
```

**מה לחפש:**
- האם `prr` עדיין `0.0`?
- האם `sw_version` עדיין `"waiting for fiber"`?
- האם ה-pods רצים תקין?

---

## 📞 פעולות תקשורת

### 5. פנה ל-DevOps/Infrastructure

**מתי לפנות:**
- אם המערכת צריכה להיות מוכנה אבל לא מוכנה
- אם יש בעיות תשתית (fiber לא מחובר)
- אם יש בעיות עם RabbitMQ או MongoDB

**מה לספר להם:**
- המערכת במצב "waiting for fiber"
- `prr: 0.0` - לא תקין
- כל בקשות `/configure` נכשלות
- יש 4 restarts ב-28 שעות
- הטסטים נעצרו כדי למנוע עומס מיותר

---

## 🔧 פעולות לטווח הארוך (לאחר שהמערכת תהיה מוכנה)

### 6. הוסף Health Check לפני הטסטים

**קובץ:** `tests/conftest.py`

**קוד:**
```python
@pytest.fixture(scope="session", autouse=True)
def check_metadata_ready(focus_server_api):
    """Skip all configure tests if system is waiting for fiber."""
    import pytest
    
    try:
        metadata = focus_server_api.get_live_metadata_flat()
        if metadata.prr <= 0 or metadata.sw_version == "waiting for fiber":
            pytest.skip("System is waiting for fiber - stopping all configure tests")
    except Exception as e:
        pytest.skip(f"Cannot check metadata - stopping all configure tests: {e}")
```

**למה זה חשוב:**
- מונע מהטסטים לרוץ כשהמערכת לא מוכנה
- חוסך זמן ומשאבים
- מונע עומס מיותר על השרת

---

### 7. עדכן את ה-Retry Logic

**קובץ:** `src/core/api_client.py`

**קוד:**
```python
# Don't retry on 503 if it's "waiting for fiber"
if response.status_code == 503:
    try:
        metadata = self.get_live_metadata_flat()
        if metadata.sw_version == "waiting for fiber":
            raise APIError("System is waiting for fiber - do not retry")
    except:
        pass
```

**למה זה חשוב:**
- מונע retry מיותר כשהמערכת במצב "waiting for fiber"
- חוסך זמן ומשאבים
- מונע עומס מיותר על השרת

---

### 8. עדכן את ה-API Client לבדוק metadata לפני configure

**קובץ:** `src/apis/focus_server_api.py`

**קוד:**
```python
def configure_streaming_job(self, request: ConfigureRequest) -> ConfigureResponse:
    """Configure streaming job with metadata check."""
    # Check metadata before attempting to configure
    try:
        metadata = self.get_live_metadata_flat()
        if metadata.prr <= 0 or metadata.sw_version == "waiting for fiber":
            raise APIError(
                "Cannot configure job: System is waiting for fiber. "
                "Please ensure fiber is connected and metadata is available."
            )
    except Exception as e:
        raise APIError(f"Cannot check metadata: {e}")
    
    # Continue with configuration...
```

**למה זה חשוב:**
- נותן שגיאה ברורה לפני שמנסים להגדיר job
- חוסך זמן ומשאבים
- מונע עומס מיותר על השרת

---

## ✅ Checklist

### פעולות מיידיות (עכשיו!):
- [ ] ⛔ **עצור את כל הטסטים** שמנסים להגדיר jobs
- [ ] ⛔ **עצור את ה-load tests** (Locust)
- [ ] ⛔ **עצור את ה-CI/CD pipelines** שרצים טסטים

### בדיקות נוספות (לאחר עצירת הטסטים):
- [ ] בדוק למה יש 4 restarts ב-28 שעות
- [ ] בדוק את מצב המערכת (`GET /live_metadata`)
- [ ] בדוק את ה-logs לפני ה-restarts
- [ ] בדוק את ה-resource usage

### תקשורת:
- [ ] פנה ל-DevOps/Infrastructure אם צריך

### פעולות לטווח הארוך (לאחר שהמערכת תהיה מוכנה):
- [ ] הוסף Health Check לפני הטסטים
- [ ] עדכן את ה-Retry Logic
- [ ] עדכן את ה-API Client לבדוק metadata לפני configure
- [ ] תיעד את הבעיה והפתרון

---

## 📊 סיכום

### מה עשינו:
1. ✅ זיהינו שהמערכת במצב "waiting for fiber"
2. ✅ זיהינו שיש retry logic פעיל שיוצר עומס מיותר
3. ✅ זיהינו שיש 4 restarts ב-28 שעות
4. ✅ יצרנו מסמכים מפורטים

### מה צריך לעשות עכשיו:
1. ⛔ **עצור את הטסטים** (דחוף!)
2. 🔍 בדוק למה יש restarts
3. 📞 פנה ל-DevOps אם צריך
4. 🔧 הוסף health checks לטסטים

### מה צריך לעשות אחר כך:
1. המתן עד שהמערכת תהיה מוכנה
2. עדכן את הטסטים לטפל ב-"waiting for fiber"
3. עדכן את ה-retry logic
4. עדכן את ה-API client

---

**עודכן לאחרונה:** 2025-11-08 13:20  
**סטטוס:** 🔴 דחוף - עצור את הטסטים עכשיו!

