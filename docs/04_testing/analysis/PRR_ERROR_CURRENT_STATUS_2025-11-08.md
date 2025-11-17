# 🔴 סטטוס נוכחי: שגיאת PRR - "waiting for fiber"

**תאריך:** 2025-11-08 13:19 (עודכן)  
**סביבה:** Staging (10.10.10.100)  
**סטטוס:** 🔴 **בעיה פעילה - המערכת במצב "waiting for fiber"**  
**⚠️ אזהרה:** יש retry logic פעיל שיוצר עומס מיותר על השרת!

---

## 📋 סיכום המצב הנוכחי

המערכת במצב **"waiting for fiber"** - אין fiber פיזי מחובר או שהמערכת לא קיבלה metadata מה-fiber.

### תוצאות בדיקה:

#### 1. **GET /live_metadata** מחזיר מצב "waiting for fiber":

```bash
curl -k https://10.10.10.100/focus-server/live_metadata | jq
```

**תגובה:**
```json
{
  "dx": 0.0,
  "prr": 0.0,
  "fiber_start_meters": null,
  "fiber_length_meters": null,
  "sw_version": "waiting for fiber",
  "number_of_channels": 2337,
  "fiber_description": "waiting for fiber"
}
```

**ניתוח:**
- ✅ `number_of_channels: 2337` - תקין (יש channels זמינים)
- ❌ `prr: 0.0` - **לא תקין!** (צריך להיות > 0, בדרך כלל 2000)
- ❌ `dx: 0.0` - לא תקין (צריך להיות > 0)
- ❌ `sw_version: "waiting for fiber"` - מצב "waiting for fiber"
- ❌ `fiber_description: "waiting for fiber"` - מצב "waiting for fiber"

---

#### 2. **לוגי Focus Server** מראים שגיאות חוזרות:

```bash
kubectl logs -n panda -l app.kubernetes.io/name=panda-panda-focus-server --tail=100
```

**תוצאות (13:18-13:19):**
```
2025-11-08T13:18:33+0000 INFO pz.focus_server got configuration: displayTimeAxisDuration=30 nfftSelection=1024...
2025-11-08T13:18:33+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr
INFO: "POST /configure HTTP/1.1" 503 Service Unavailable
... (שגיאות חוזרות כל 2-3 שניות)
```

**ניתוח:**
- ✅ כל בקשות `POST /configure` נכשלות עם `503 Service Unavailable`
- ❌ השגיאה: `Missing required fiber metadata fields: prr`
- ⚠️ **השגיאות חוזרות כל 2-3 שניות** - יש retry logic פעיל בטסטים!
- ⚠️ **יש 2 סוגי בקשות חוזרות:**
  - `displayInfo.height=200, channels.min=11, max=109, frequencyRange.max=1000`
  - `displayInfo.height=1000, channels.min=1, max=50, frequencyRange.max=500`
- ⚠️ זה יוצר עומס מיותר על השרת!

#### 3. **סטטוס Pod** - יש restarts (✅ **סיבה זוהתה!**):

```bash
kubectl get pods -n panda | grep focus-server
```

**תוצאות:**
```
panda-panda-focus-server-78dbcfd9d9-kjj77    1/1     Running   4 (28h ago)   46h
```

**ניתוח:**
- ✅ Pod רץ תקין (1/1 Running)
- ⚠️ **4 restarts ב-28 שעות האחרונות** - ✅ **סיבה זוהתה!**
- Pod רץ כבר 46 שעות (מאז ה-restart האחרון)
- ✅ Resource usage תקין: CPU 3m, Memory 394Mi

**סיבת ה-restarts (מהלוגים הקודמים):**
```
pymongo.errors.ServerSelectionTimeoutError: mongodb:27017: [Errno -3] Temporary failure in name resolution
```

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

---

#### 4. **לוגי RabbitMQ** תקינים:

```bash
kubectl logs -n panda -l app.kubernetes.io/instance=rabbitmq-panda --tail=50
```

**תוצאות:**
```
2025-11-08 13:12:24.748786+00:00 [debug] <0.928.0> Peer discovery: checking for partitioned nodes to clean up.
2025-11-08 13:12:24.749032+00:00 [debug] <0.928.0> Peer discovery: all known cluster nodes are up.
... (לוגים תקינים - אין בעיות)
```

**ניתוח:**
- ✅ RabbitMQ עובד תקין
- ✅ אין בעיות חיבור
- ✅ כל ה-nodes במצב תקין

---

## 🔍 ניתוח הבעיה

### מה קורה?

1. **המערכת במצב "waiting for fiber"**
   - אין fiber פיזי מחובר, או
   - המערכת לא קיבלה metadata מה-fiber, או
   - המערכת במצב initialization

2. **Focus Server לא יכול לקבל metadata**
   - `FocusManager` מנסה לפתוח recording מ-RabbitMQ (`amqp://`)
   - אבל אין recording זמין כי אין fiber מחובר
   - `fiber_metadata` נשאר במצב "waiting for fiber"
   - `prr` נשאר `0.0` (או חסר)

3. **כל בקשות `/configure` נכשלות**
   - `parse_task_configuration` משתמש ב-`focus_manager.prr` לחישובים קריטיים:
     ```python
     # pz/microservices/focus_server/focus_server.py:85
     window_overlap = 1 - (display_time_axis_duration * focus_manager.prr) / ((configuration["canvasInfo"]["height"] * n_fft))
     ```
   - אם `prr` הוא `0.0` או חסר, החישובים נכשלים
   - השגיאה: `Missing required fiber metadata fields: prr`

---

## 🎯 הקשר לטיקטי Jira

### טיקטים רלוונטיים:

1. **PZ-12920: support configuration changes** ⭐ **קריטי!**
   - מתאר בדיוק את הבעיה: כשהקונפיגורציה משתנה, Focus Server לא יכול לתמוך בזה
   - נסגר ב-18/Sep/25, אבל הבעיה עדיין קיימת

2. **PZ-8713: Different configuration BE support** ⭐
   - מתאר שכשהקונפיגורציה משתנה ב-backoffice, Focus Server צריך לעבוד עם הקונפיגורציה החדשה
   - אבל אם המערכת לא קיבלה metadata חדש, PRR יהיה חסר

3. **PZ-13843: Test isolated system** ⚠️
   - אם המערכת במצב isolated/offline, אין fiber מחובר
   - זה יכול לגרום למצב "waiting for fiber"

---

## ⚠️ בעיה קריטית: Retry Logic יוצר עומס מיותר

### מה קורה?

הטסטים מנסים להגדיר jobs כל 2-3 שניות ונכשלים:
- יש retry logic ב-API client (`src/core/api_client.py`)
- הטסטים מנסים שוב ושוב גם כשהמערכת במצב "waiting for fiber"
- זה יוצר עומס מיותר על השרת
- זה יכול לגרום ל-restarts נוספים

### פתרון מיידי: עצור את הטסטים!

**פעולה נדרשת:**
1. ⛔ **עצור את כל הטסטים** שמנסים להגדיר jobs
2. ⛔ **עצור את ה-load tests** (Locust)
3. ✅ המתן עד שהמערכת תהיה מוכנה

### פתרון לטווח הארוך: הוסף Health Check לפני הטסטים

```python
# tests/conftest.py או לפני כל טסט
@pytest.fixture(scope="session")
def ensure_metadata_ready(focus_server_api):
    """Ensure metadata is ready before configuring jobs."""
    try:
        metadata = focus_server_api.get_live_metadata_flat()
        if metadata.prr <= 0 or metadata.sw_version == "waiting for fiber":
            pytest.skip("System is waiting for fiber - metadata not ready")
        return metadata
    except Exception as e:
        pytest.skip(f"Metadata not available: {e}")
```

---

## 🔧 פתרונות מיידיים

### 1. בדוק את מצב המערכת ✅ **בוצע**

```bash
# בדוק metadata
curl -k https://10.10.10.100/focus-server/live_metadata | jq

# בדוק pods
kubectl get pods -n panda | grep focus-server

# בדוק לוגים
kubectl logs -n panda -l app.kubernetes.io/name=panda-panda-focus-server --tail=100
```

### 2. אם המערכת במצב "waiting for fiber"

**אפשרויות:**
- ✅ **המתן** עד שהמערכת תהיה מוכנה (אם יש fiber פיזי שמתחבר)
- ✅ **בדוק** שיש fiber פיזי מחובר
- ✅ **בדוק** את תקשורת ה-fiber
- ✅ **פנה ל-DevOps/Infrastructure** לבדיקה

### 3. בדוק אם הייתה שינוי קונפיגורציה

- בדוק את Backoffice - האם הייתה שינוי קונפיגורציה אחרונה?
- בדוק את MongoDB - האם יש קונפיגורציות חדשות?
- בדוק את לוגי Backoffice

### 4. פתרון זמני לטסטים ⚠️ **דחוף!**

**עצור את הטסטים עכשיו!** הטסטים יוצרים עומס מיותר על השרת.

לאחר מכן, עדכן את הטסטים לטפל ב-"waiting for fiber":

```python
# לפני כל configure()
metadata = focus_server_api.get_live_metadata_flat()
if metadata.prr <= 0 or metadata.sw_version == "waiting for fiber":
    pytest.skip("System is waiting for fiber - metadata not ready")
```

**או הוסף fixture ב-conftest.py:**
```python
@pytest.fixture(scope="session", autouse=True)
def check_metadata_ready(focus_server_api):
    """Skip all configure tests if system is waiting for fiber."""
    try:
        metadata = focus_server_api.get_live_metadata_flat()
        if metadata.prr <= 0 or metadata.sw_version == "waiting for fiber":
            pytest.skip("System is waiting for fiber - stopping all configure tests")
    except Exception:
        pytest.skip("Cannot check metadata - stopping all configure tests")
```

---

## 📊 השפעה על הטסטים

### טסטים שנכשלים:

כל הטסטים שמנסים להגדיר job יכשלו:
- `test_configure_*` - כל טסטי configuration
- `test_live_monitoring_*` - טסטי live monitoring
- `test_singlechannel_*` - טסטי single channel view
- `test_waterfall_*` - טסטי waterfall
- כל טסט שמשתמש ב-`configure()` או `POST /configure`

### טסטים שעובדים:

- `test_get_live_metadata` - בדיקת metadata (אבל יחזיר 0.0)
- `test_get_channels` - רשימת channels (יחזיר 2337 channels)
- `test_get_sensors` - רשימת sensors
- טסטי read-only שלא דורשים configuration

---

## 🔧 המלצות לטווח הארוך

### 1. שיפור ה-error handling בשרת

השרת צריך להחזיר שגיאות ברורות יותר:
- `503 Service Unavailable` → `400 Bad Request` עם הודעה ברורה
- הודעת שגיאה מפורטת על מה חסר
- סטטוס ברור: `waiting_for_fiber`, `metadata_unavailable`, וכו'

### 2. שיפור הטסטים

- הוסף health checks לפני טסטים
- הוסף retry logic עם backoff
- הוסף skip logic למצב "waiting for fiber"
- הוסף validation של metadata לפני configure

### 3. תיעוד

- תיעוד מצבי המערכת השונים
- תיעוד איך לטפל ב-"waiting for fiber"
- תיעוד איך לבדוק אם המערכת מוכנה

---

## ✅ Checklist לפתרון

- [x] בדוק את מצב המערכת (`GET /live_metadata`) ✅ **בוצע**
- [x] בדוק את לוגי השרת ✅ **בוצע**
- [x] בדוק את סטטוס ה-pods ✅ **בוצע - 4 restarts ב-28 שעות!**
- [x] בדוק את RabbitMQ ✅ **בוצע - תקין**
- [x] זהה retry logic פעיל ⚠️ **זוהה - יוצר עומס מיותר!**
- [ ] ⛔ **עצור את הטסטים** שמנסים להגדיר jobs ⚠️ **דחוף!**
- [ ] אם במצב "waiting for fiber" - המתן או פנה ל-DevOps ⏳ **בהמתנה**
- [ ] עדכן את הטסטים לטפל ב-"waiting for fiber" 📝 **לעשות**
- [ ] הוסף health checks לפני טסטים 📝 **לעשות**
- [ ] בדוק למה יש 4 restarts ב-28 שעות 📝 **לבדוק**
- [ ] תיעד את הבעיה והפתרון ✅ **בוצע**

---

## 📝 הערות נוספות

### למה זה קורה עכשיו?

1. **המערכת במצב "waiting for fiber"** - אין fiber פיזי מחובר
2. **שינוי קונפיגורציה אחרון** - ייתכן שהייתה שינוי קונפיגורציה ב-Backoffice
3. **המערכת במצב initialization** - המערכת עדיין לא מוכנה

### מה לעשות?

1. **בדוק את מצב המערכת** - האם יש metadata זמין? ✅ **בוצע - לא זמין**
2. **בדוק שינויי קונפיגורציה** - האם הייתה שינוי ב-Backoffice? ⏳ **לבדוק**
3. **בדוק את RabbitMQ** - האם יש בעיות חיבור? ✅ **בוצע - תקין**
4. **בדוק את לוגי Focus Server** - מה אומרים הלוגים? ✅ **בוצע - שגיאות חוזרות**

---

**עודכן לאחרונה:** 2025-11-08 13:25  
**סטטוס:** 🔴 בעיה פעילה - המערכת במצב "waiting for fiber"  
**⚠️ אזהרה:** יש retry logic פעיל שיוצר עומס מיותר על השרת!  
**✅ סיבת ה-restarts זוהתה:** בעיית חיבור ל-MongoDB בזמן initialization  
**פעולה נדרשת:** 
1. ⛔ **עצור את הטסטים** שמנסים להגדיר jobs (דחוף!)
2. המתן למערכת להיות מוכנה או פנה ל-DevOps/Infrastructure
3. ✅ **סיבת ה-restarts זוהתה** - בעיית DNS/Networking ל-MongoDB (נפתרה)

