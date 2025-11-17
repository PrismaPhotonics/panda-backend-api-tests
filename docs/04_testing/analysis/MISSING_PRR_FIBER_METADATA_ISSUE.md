# 🔴 בעיה קריטית: Missing Required Fiber Metadata Fields - PRR

**תאריך:** 2025-11-08  
**סטטוס:** 🔴 **בעיה פעילה**  
**עדיפות:** גבוהה מאוד

---

## 📋 סיכום הבעיה

השרת מחזיר שגיאה חוזרת על כל בקשות `/configure`:

```
ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr
INFO: "POST /configure HTTP/1.1" 503 Service Unavailable
```

**השפעה:**
- ❌ כל הטסטים שמנסים להגדיר job נכשלים
- ❌ המערכת לא יכולה להגדיר jobs חדשים
- ❌ כל בקשות `/configure` מחזירות `503 Service Unavailable`

---

## 🔍 ניתוח הבעיה

### מה זה PRR?

**PRR = Pulse Repetition Rate** (קצב חזרת הדופק)

- זהו שדה קריטי ב-fiber metadata
- מייצג את מספר הדגימות לשנייה
- נדרש לחישוב Nyquist frequency (`Nyquist = PRR / 2`)
- נדרש לוולידציה של frequency ranges

### איפה PRR אמור להיות?

PRR אמור להיות ב-**fiber metadata** שמגיע מ-`GET /live_metadata`:

```python
# src/models/focus_server_models.py:467
class LiveMetadataFlat(BaseModel):
    prr: float = Field(..., description="Pulse repetition rate", gt=0)  # ← REQUIRED!
    num_samples_per_trace: int = Field(..., description="Samples per trace", gt=0)
    dtype: str = Field(..., description="Data type")
    # ... other fields
```

### למה זה קורה?

השרת מנסה להגדיר job אבל **אין fiber metadata זמין**. זה יכול לקרות כי:

1. **המערכת במצב "waiting for fiber"** - אין fiber פיזי מחובר
2. **המערכת לא קיבלה metadata מה-fiber** - בעיה בתקשורת
3. **המערכת לא הוגדרה כראוי** - חסר configuration
4. **המערכת במצב initialization** - עדיין לא מוכנה

---

## 🔍 איך לבדוק את המצב

### 1. בדוק אם יש live metadata זמין

```bash
curl -k https://10.10.10.100/focus-server/live_metadata
```

**תגובה תקינה:**
```json
{
  "prr": 2000.0,
  "num_samples_per_trace": 1024,
  "dtype": "float32",
  "dx": 0.5,
  "number_of_channels": 2337,
  "fiber_description": "...",
  "sw_version": "..."
}
```

**תגובה בעייתית (מצב "waiting for fiber") - ✅ זוהה ב-2025-11-08 13:15:**
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

**מצב נוכחי:**
- המערכת במצב **"waiting for fiber"** - אין fiber פיזי מחובר
- כל בקשות `/configure` נכשלות עם שגיאה: `Missing required fiber metadata fields: prr`
- לוגי Focus Server מראים שגיאות חוזרות כל 2-3 שניות
- RabbitMQ תקין - אין בעיות חיבור

**ראה מסמך מפורט:** `docs/04_testing/analysis/PRR_ERROR_CURRENT_STATUS_2025-11-08.md`

### 2. בדוק את לוגי השרת

```bash
# דרך k9s
k9s -n panda
# לחץ על pod של focus-server
# לחץ 'l' ללוגים
```

או דרך kubectl:
```bash
kubectl logs -n panda -l app.kubernetes.io/name=panda-panda-focus-server --tail=100
```

### 3. בדוק את סטטוס ה-pods

```bash
kubectl get pods -n panda
kubectl describe pod <focus-server-pod> -n panda
```

---

## 🛠️ פתרונות אפשריים

### פתרון 1: המתן למערכת להיות מוכנה (מומלץ)

אם המערכת במצב "waiting for fiber", צריך:

1. **להמתין** עד שהמערכת תקבל fiber metadata
2. **לוודא** שיש fiber פיזי מחובר
3. **לבדוק** שהמערכת קיבלה metadata מה-fiber

**בטסטים:**
```python
# בדוק אם metadata זמין לפני הגדרת job
metadata = focus_server_api.get_live_metadata_flat()
if metadata.prr <= 0:
    pytest.skip("System is waiting for fiber - metadata not ready yet")
```

### פתרון 2: עדכון הטסטים לטפל ב-"waiting for fiber"

הטסטים צריכים לבדוק אם metadata זמין לפני שהם מנסים להגדיר job:

```python
@pytest.fixture
def ensure_metadata_ready(focus_server_api):
    """Ensure metadata is ready before configuring jobs."""
    try:
        metadata = focus_server_api.get_live_metadata_flat()
        if metadata.prr <= 0:
            pytest.skip("System is waiting for fiber - metadata not ready")
        return metadata
    except Exception as e:
        pytest.skip(f"Metadata not available: {e}")
```

### פתרון 3: בדיקת health check לפני טסטים

להוסיף health check שמאמת שיש metadata זמין:

```python
def check_metadata_health(focus_server_api) -> bool:
    """Check if metadata is ready."""
    try:
        metadata = focus_server_api.get_live_metadata_flat()
        return metadata.prr > 0
    except:
        return False
```

### פתרון 4: טיפול טוב יותר בשגיאות בשרת

השרת צריך להחזיר שגיאה ברורה יותר:

**כרגע:**
```
503 Service Unavailable
```

**מומלץ:**
```json
{
  "error": "Cannot configure job",
  "reason": "Missing required fiber metadata fields: prr",
  "status": "waiting_for_fiber",
  "message": "System is waiting for fiber connection. Please ensure fiber is connected and metadata is available."
}
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
- `test_get_channels` - רשימת channels
- `test_get_sensors` - רשימת sensors
- טסטי read-only שלא דורשים configuration

---

## 🔧 פעולות מיידיות

### 1. בדוק את מצב המערכת

```bash
# בדוק metadata
curl -k https://10.10.10.100/focus-server/live_metadata | jq

# בדוק pods
kubectl get pods -n panda

# בדוק לוגים
kubectl logs -n panda -l app.kubernetes.io/name=panda-panda-focus-server --tail=50
```

### 2. אם המערכת במצב "waiting for fiber"

**אפשרויות:**
- המתן עד שהמערכת תהיה מוכנה
- בדוק שיש fiber פיזי מחובר
- בדוק את תקשורת ה-fiber
- פנה ל-DevOps/Infrastructure לבדיקה

### 3. עדכן את הטסטים

להוסיף validation לפני הגדרת jobs:

```python
# לפני כל configure()
metadata = focus_server_api.get_live_metadata_flat()
if metadata.prr <= 0:
    pytest.skip("System is waiting for fiber - metadata not ready")
```

---

## 📝 המלצות לטווח הארוך

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

## 🔗 קישורים רלוונטיים

- **PZ-14592**: LiveMetadata Missing Required Fields
- **PZ-13985**: LiveMetadata Missing Required Fields (bug)
- **קובץ מודל**: `src/models/focus_server_models.py:461` (LiveMetadataFlat)
- **API Client**: `src/apis/focus_server_api.py:440` (get_live_metadata_flat)

---

## ✅ Checklist לפתרון

- [ ] בדוק את מצב המערכת (`GET /live_metadata`)
- [ ] בדוק את לוגי השרת
- [ ] בדוק את סטטוס ה-pods
- [ ] אם במצב "waiting for fiber" - המתן או פנה ל-DevOps
- [ ] עדכן את הטסטים לטפל ב-"waiting for fiber"
- [ ] הוסף health checks לפני טסטים
- [ ] תיעד את הבעיה והפתרון

---

**עודכן לאחרונה:** 2025-11-08  
**סטטוס:** 🔴 בעיה פעילה - דורש טיפול מיידי

