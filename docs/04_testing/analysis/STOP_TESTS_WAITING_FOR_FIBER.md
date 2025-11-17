# ⛔ עצירת טסטים - המערכת במצב "waiting for fiber"

**תאריך:** 2025-11-08 13:19  
**עדיפות:** 🔴 **דחוף!**

---

## 📋 סיכום הבעיה

המערכת במצב **"waiting for fiber"** - אין fiber פיזי מחובר, ולכן כל בקשות `/configure` נכשלות.

**הבעיה הנוספת:** הטסטים ממשיכים לנסות להגדיר jobs כל 2-3 שניות, מה שיוצר עומס מיותר על השרת.

---

## ⚠️ מה קורה עכשיו?

### 1. המערכת במצב "waiting for fiber"

```bash
curl -k https://10.10.10.100/focus-server/live_metadata | jq
```

**תגובה:**
```json
{
  "dx": 0.0,
  "prr": 0.0,
  "sw_version": "waiting for fiber",
  "number_of_channels": 2337,
  "fiber_description": "waiting for fiber"
}
```

### 2. כל בקשות `/configure` נכשלות

```
ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr
INFO: "POST /configure HTTP/1.1" 503 Service Unavailable
```

### 3. הטסטים ממשיכים לנסות (retry logic)

הלוגים מראים בקשות חוזרות כל 2-3 שניות:
- `displayInfo.height=200, channels.min=11, max=109`
- `displayInfo.height=1000, channels.min=1, max=50`

זה יוצר עומס מיותר על השרת!

### 4. יש 4 restarts ב-28 שעות

```bash
kubectl get pods -n panda | grep focus-server
```

```
panda-panda-focus-server-78dbcfd9d9-kjj77    1/1     Running   4 (28h ago)   46h
```

זה יכול להיות קשור לעומס המיותר!

---

## ⛔ פעולות מיידיות נדרשות

### 1. עצור את כל הטסטים שמנסים להגדיר jobs

**טסטים שצריך לעצור:**
- כל טסטי `test_configure_*`
- כל טסטי `test_live_monitoring_*`
- כל טסטי `test_singlechannel_*`
- כל טסטי `test_waterfall_*`
- כל טסטי performance/load שמנסים להגדיר jobs
- כל ה-load tests (Locust)

**איך לעצור:**
```bash
# מצא את כל ה-processes שרצים טסטים
ps aux | grep pytest
ps aux | grep locust

# עצור אותם
kill <PID>
```

### 2. בדוק אם יש CI/CD שרץ טסטים

אם יש CI/CD pipeline שרץ טסטים:
- עצור את ה-pipeline
- או עדכן את ה-pipeline לדלג על טסטי configure

---

## 🔧 פתרונות לטווח הארוך

### 1. הוסף Health Check לפני הטסטים

**קובץ:** `tests/conftest.py`

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

### 2. עדכן את ה-API Client לטפל ב-"waiting for fiber"

**קובץ:** `src/apis/focus_server_api.py`

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

### 3. עדכן את ה-Retry Logic

**קובץ:** `src/core/api_client.py`

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

---

## 📊 השפעה על הטסטים

### טסטים שנכשלים (צריך לעצור):

- `test_configure_*` - כל טסטי configuration
- `test_live_monitoring_*` - טסטי live monitoring
- `test_singlechannel_*` - טסטי single channel view
- `test_waterfall_*` - טסטי waterfall
- `test_performance_*` - טסטי performance שמנסים להגדיר jobs
- `test_load_*` - טסטי load שמנסים להגדיר jobs
- כל טסט שמשתמש ב-`configure()` או `POST /configure`

### טסטים שעובדים (יכולים להמשיך):

- `test_get_live_metadata` - בדיקת metadata (יחזיר 0.0)
- `test_get_channels` - רשימת channels (יחזיר 2337 channels)
- `test_get_sensors` - רשימת sensors
- טסטי read-only שלא דורשים configuration

---

## ✅ Checklist

- [ ] ⛔ **עצור את כל הטסטים** שמנסים להגדיר jobs
- [ ] ⛔ **עצור את ה-load tests** (Locust)
- [ ] ⛔ **עצור את ה-CI/CD pipelines** שרצים טסטים
- [ ] בדוק את מצב המערכת (`GET /live_metadata`)
- [ ] בדוק את לוגי השרת
- [ ] בדוק למה יש 4 restarts ב-28 שעות
- [ ] המתן עד שהמערכת תהיה מוכנה
- [ ] הוסף health checks לפני הטסטים
- [ ] עדכן את ה-retry logic

---

**עודכן לאחרונה:** 2025-11-08 13:19  
**סטטוס:** 🔴 דחוף - עצור את הטסטים עכשיו!

