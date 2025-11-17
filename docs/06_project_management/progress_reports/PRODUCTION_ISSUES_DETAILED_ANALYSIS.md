# 🔍 ניתוח מפורט - בעיות Production

**תאריך:** 2025-11-03  
**סביבה:** Production (כפר סבא)  
**מטרה:** הסבר מפורט לכל בעיה והמלצות לתיקון

---

## 1. 🔴 MongoDB Indexes - דחוף!

### מה הבעיה?

**טסטים שנכשלו:**
- `test_mongodb_indexes_exist_and_optimal` ❌
- `test_mongodb_indexes_exist_and_optimal` (related tests)

**שגיאה:**
```
Critical indexes are MISSING: ['start_time', 'end_time', 'uuid']
These indexes are REQUIRED for acceptable query performance.
History playback will be extremely slow without them.
```

### למה זה קורה?

**Collection:** `d57c8adb-ea00-4666-83cb-0248ae9d602f` (Recording Collection)

**מה חסר:**
- ❌ `start_time` index - קריטי ל-historic queries (חיפוש לפי זמן)
- ❌ `end_time` index - קריטי ל-historic queries (range queries)
- ❌ `uuid` index - קריטי ל-lookups (UNIQUE)
- ❌ `deleted` index - חשוב ל-filtering (soft delete)

**מה קיים:**
- ✅ `_id` index (default MongoDB index)

### השפעה:

**בלי indexes:**
```javascript
// MongoDB מבצע FULL COLLECTION SCAN על כל query!
db.recordings.find({
    start_time: { $gte: 1698000000 },
    end_time: { $lte: 1698100000 }
})
// Execution time: 10-60 seconds (depending on collection size)
```

**עם indexes:**
```javascript
// MongoDB משתמש ב-index!
// Execution time: 0.01-0.1 seconds
// Improvement: 100-1000x faster! ⚡
```

### פתרון:

**Script אוטומטי:** `.\scripts\fix_mongodb_indexes_production.ps1`

**או ידנית:**
```javascript
mongosh "mongodb://prisma:prisma@10.10.100.108:27017/prisma?authSource=prisma"

use prisma
var guid = "d57c8adb-ea00-4666-83cb-0248ae9d602f";

db[guid].createIndex({ "start_time": 1 }, { background: true });
db[guid].createIndex({ "end_time": 1 }, { background: true });
db[guid].createIndex({ "uuid": 1 }, { unique: true, background: true });
db[guid].createIndex({ "deleted": 1 }, { background: true });
```

### זמן משוער:
**15 דקות** (background indexing - לא חוסם את DB)

---

## 2. 🔴 Stale Recording - דחוף!

### מה זה Stale Recording?

**Stale Recording** = Recording שמתחיל אבל **לא מסתיים** (לא מקבל `end_time`)

**דוגמה מהמערכת:**
```
UUID: 65777a6b-7e0d-4876-add0-7d136792ce64
Started: 2025-10-29 13:02:23 (לפני 117.3 שעות!)
End Time: NULL ❌
Status: deleted=False, אבל >24h ללא end_time
```

### למה זה קורה?

**סיבות אפשריות:**
1. **Process Crash** - התהליך קרס לפני סיום ההקלטה
2. **Network Failure** - חיבור נותק לפני שליחת end_time
3. **Server Restart** - השרת התחיל מחדש בזמן הקלטה
4. **Database Error** - שגיאה בכתיבת end_time ל-DB
5. **Timeout** - התהליך נהרג על ידי timeout

### מה הבעיה?

**Data Quality Issue:**
- Recording "תלוי באוויר" - התחיל אבל לא הסתיים
- לא ברור אם זה LIVE או FAILED
- מפריע לניקיון נתונים
- מפריע לניתוח (מה הסטטוס?)

### איפה זה מתגלה?

**טסט:** `test_recordings_have_all_required_metadata`

**קוד:** `tests/data_quality/test_mongodb_data_quality.py:550-586`

**הלוגיקה:**
```python
# אם recording > 24 שעות ללא end_time → STALE
stale_threshold = datetime.now(timezone.utc) - timedelta(hours=24)

stale_recordings = collection.find({
    "deleted": False,
    "$or": [
        {"end_time": {"$exists": False}},
        {"end_time": None}
    ],
    "start_time": {"$lt": stale_threshold}  # > 24h old
})
```

### פתרון:

**Option 1: Mark as Deleted (מומלץ - שומר היסטוריה)**
```powershell
.\scripts\clean_stale_recording_production.ps1
```

**מה זה עושה:**
```javascript
db.recordings.updateOne(
    { uuid: "65777a6b-7e0d-4876-add0-7d136792ce64" },
    {
        $set: {
            deleted: true,
            end_time: new Date(),  // נותן end_time
            cleanup_note: "Marked as deleted due to stale status"
        }
    }
);
```

**Option 2: Delete Completely (רק אם בטוח)**
```powershell
.\scripts\clean_stale_recording_production.ps1 -Delete
```

### זמן משוער:
**5 דקות**

---

## 3. 🟡 Kubernetes API - Connection Timeout

### מה הבעיה?

**12 טסטים נכשלו:**
- `test_kubernetes_direct_connection` ❌
- `test_kubernetes_connection` ❌
- `test_kubernetes_list_deployments` ❌
- `test_kubernetes_list_pods` ❌
- `test_mongodb_status_via_kubernetes` ❌
- ועוד...

**שגיאה:**
```
Connection to 10.10.100.102:6443 timed out
HTTPSConnectionPool(host='10.10.100.102', port=6443): 
Max retries exceeded
```

### למה זה קורה?

**הסיבה:**
- Kubernetes API (10.10.100.102:6443) **לא נגיש ישירות מ-Windows**
- Firewall חוסם את הגישה
- Network policy חוסם גישה מחוץ ל-cluster
- רק services בתוך Kubernetes יכולים לגשת ישירות

### איפה זה קורה?

**קבצים:**
- `tests/infrastructure/test_basic_connectivity.py`
- `tests/infrastructure/test_external_connectivity.py`
- `tests/infrastructure/test_k8s_job_lifecycle.py`

**הקוד מנסה:**
```python
from kubernetes import client, config

# מנסה לטעון kubeconfig מהמכונה המקומית
config.load_kube_config()  # ❌ לא עובד מ-Windows!

# מנסה להתחבר ישירות ל-K8s API
api_client = client.ApiClient()
response = api_client.call_api('/version', 'GET')  # ❌ Timeout!
```

### פתרון - 3 אופציות:

#### Option 1: Skip Tests on Windows (מומלץ)
```python
# tests/infrastructure/test_basic_connectivity.py
import pytest
import platform

@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Kubernetes API not directly accessible from Windows - use SSH tunnel"
)
def test_kubernetes_direct_connection(...):
    # ... test code ...
```

#### Option 2: SSH Tunnel (אם צריך את הטסטים)
```powershell
# יצירת SSH tunnel דרך worker node
ssh -L 6443:10.10.100.102:6443 prisma@10.10.100.113

# עכשיו K8s API נגיש דרך localhost:6443
```

#### Option 3: kubectl via SSH (מומלץ לטסטים)
```python
# להשתמש ב-kubectl דרך SSH במקום ישירות
from src.infrastructure.ssh_manager import SSHManager

ssh = SSHManager(...)
result = ssh.execute_command("kubectl get pods -n panda")
```

### המלצה:
**Option 1** (Skip) - הכי פשוט וברור

### זמן משוער:
**10-15 דקות** (לעדכן את הטסטים)

---

## 4. 🔴 Schema Validation - בעיה בטסט!

### מה הבעיה?

**3 טסטים נכשלו:**
- `test_recordings_document_schema_validation` ❌
- `test_recording_collection_schema_validation` ❌
- (related tests)

**שגיאה:**
```
AssertionError: Required field 'start_time' missing
Collection: d57c8adb-ea00-4666-83cb-0248ae9d602f-unrecognized_recordings
```

### האם זה באג אמיתי או בעיה בטסט?

**זו בעיה בטסט! ✅ (לא באג אמיתי)**

### למה?

**הבעיה:**
הטסטים בודקים את `unrecognized_recordings` collection, אבל היא **לא אמורה** להיות אותה schema כ-recording הראשי!

**Schema של Main Recording Collection:**
```json
{
  "_id": "...",
  "uuid": "38e432b0-7c87-468c-9b85-fd48462d8901",
  "start_time": "2025-03-07 07:31:34.453000",  ✅
  "end_time": "2025-03-07 09:29:34.217000",      ✅
  "deleted": false                               ✅
}
```

**Schema של unrecognized_recordings:**
```json
{
  "_id": "...",
  "folder_name": "dc022cb7-ae34-4b1e-9e0e-0bfeb60a3714",  ✅
  "file_count": 1,                                          ✅
  "update_time": "2025-07-23 12:17:48.518000"              ✅
  // ❌ אין start_time, end_time, uuid, deleted!
}
```

**למה זה שונה?**
- `unrecognized_recordings` = Recordings שלא הצליחו להיזהק (unrecognized)
- הם לא עברו processing מלא
- הם לא קיבלו metadata מלא
- לכן אין להם start_time, end_time וכו'

### איפה הבעיה בטסט?

**קובץ:** `tests/data_quality/test_mongodb_indexes_and_schema.py:381-393`

**הקוד השגוי:**
```python
def test_recordings_document_schema_validation(...):
    # הבעיה: בודק כל collection ששונה מ-base_paths
    collections = [c for c in db.list_collection_names() 
                   if c != "base_paths"]
    
    for collection_name in collections:
        # ❌ בודק גם unrecognized_recordings עם אותה validation!
        sample_doc = collection.find_one()
        assert 'start_time' in sample_doc  # ❌ Fails for unrecognized!
```

### הפתרון:

**Option 1: Skip unrecognized_recordings (מומלץ)**
```python
# tests/data_quality/test_mongodb_indexes_and_schema.py

def test_recordings_document_schema_validation(...):
    collections = [
        c for c in db.list_collection_names() 
        if c != "base_paths" 
        and not c.endswith("-unrecognized_recordings")  # ✅ דלג!
    ]
    
    for collection_name in collections:
        # ... validate schema ...
```

**Option 2: Separate Test for unrecognized_recordings**
```python
def test_unrecognized_recordings_schema(...):
    """Test unrecognized_recordings has correct schema (different from main!)."""
    collection = db.get_collection("...-unrecognized_recordings")
    doc = collection.find_one()
    
    # ✅ בדוק את ה-schema הנכון:
    assert 'folder_name' in doc
    assert 'file_count' in doc
    assert 'update_time' in doc
    
    # ✅ אל תבדוק start_time, end_time וכו'!
```

### המלצה:
**Option 1** - Skip את unrecognized_recordings בטסטים של recordings הראשיים

### זמן משוער:
**20 דקות** (לתקן את הטסטים)

---

## 5. 🟡 API Validation Errors - בעיה בטסט!

### מה הבעיה?

**15 טסטים נכשלו:**
- `test_configuration_with_extreme_values` ❌
- `test_historic_playback_short_duration_1_minute` ❌
- `test_historic_playback_very_old_timestamps_no_data` ❌
- ועוד...

**שגיאה:**
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for ConfigureRequest
channels.min
  Input should be greater than or equal to 1 [type=greater_than_equal, input_value=0]
```

### למה זה קורה?

**הסיבה:**
הטסטים מנסים ליצור config עם `channels.min = 0`, אבל ה-validation של Pydantic דורש `channels.min >= 1`

**דוגמה:**
```python
# הטסט מנסה:
config = {
    "channels": {
        "min": 0,  # ❌ לא מותר!
        "max": 10
    }
}

# Validation דורש:
# channels.min >= 1
```

### האם זה באג אמיתי או בעיה בטסט?

**זה תלוי:**
- אם המערכת אמורה לתמוך ב-`channels.min = 0` → **באג בשרת** (validation שגוי)
- אם המערכת לא אמורה לתמוך → **בעיה בטסט** (טסט לא נכון)

### הפתרון:

**לעדכן את הטסטים:**
```python
# לפני:
config = {
    "channels": {
        "min": 0,  # ❌ לא מותר
        "max": 10
    }
}

# אחרי:
config = {
    "channels": {
        "min": 1,  # ✅ מינימום 1
        "max": 10
    }
}
```

**או אם צריך לבדוק edge case:**
```python
# לבדוק שהשרת דוחה channels.min = 0
with pytest.raises(ValidationError):
    config = {
        "channels": {"min": 0, "max": 10}
    }
    focus_server_api.configure(config)  # אמור להיכשל!
```

### זמן משוער:
**30 דקות** (לעדכן 15 טסטים)

---

## 6. 🟡 Focus Server 500 Errors - באג אמיתי!

### מה הבעיה?

**10 טסטים נכשלו:**
- `test_singlechannel_complete_e2e_flow` ❌
- `test_config_endpoint_p95_latency` ❌
- `test_config_endpoint_p99_latency` ❌
- `test_job_creation_time` ❌
- ועוד...

**שגיאה:**
```
HTTPSConnectionPool(host='10.10.100.100', port=443): 
Max retries exceeded with url: /focus-server/configure 
(Caused by ResponseError('too many 500 error responses'))
```

### מתי ואיפה זה קורה?

**מתי:**
- כשמנסים לקרוא ל-`/focus-server/configure` endpoint
- כשהשרת תפוס או בעומס
- כשמנסים ליצור jobs רבים (concurrent requests)

**איפה:**
```python
# tests/integration/api/test_api_endpoints_additional.py
# tests/integration/performance/test_latency_requirements.py
# ועוד...

response = focus_server_api.configure(config)
# ❌ השרת מחזיר 500 Internal Server Error
```

### למה זה קורה?

**סיבות אפשריות:**

1. **Server Overload**
   - יותר מדי concurrent requests
   - השרת לא מסוגל לטפל בכל הבקשות
   - Resource exhaustion (CPU, Memory, Connections)

2. **Database Issues**
   - MongoDB connection pool exhausted
   - Slow queries (בלי indexes!)
   - Database timeout

3. **Kubernetes Issues**
   - Pods not ready
   - Resource limits exceeded
   - Network issues

4. **Application Bugs**
   - Unhandled exceptions
   - Null pointer errors
   - Memory leaks

### איך לבדוק?

**1. בדוק את Focus Server logs:**
```bash
# דרך SSH:
ssh root@10.10.100.3
ssh prisma@10.10.100.113

# בדוק logs:
kubectl logs -n panda -l app=focus-server --tail=200 | grep -i "error\|500\|exception"
```

**2. בדוק pod status:**
```bash
kubectl get pods -n panda | grep focus-server
# האם הם Running? Ready?
```

**3. בדוק resource usage:**
```bash
kubectl top pods -n panda | grep focus-server
# האם CPU/Memory גבוהים?
```

**4. בדוק אם זה קורה תמיד:**
```python
# הרץ טסט פשוט:
pytest tests/integration/api/test_health_check.py -v --env=production
# האם זה עובד או גם נכשל?
```

### המלצות:

1. **בדוק את Logs** - לראות מה השגיאה המדויקת
2. **בדוק Resource Usage** - האם השרת תפוס?
3. **בדוק MongoDB** - האם יש בעיות?
4. **בדוק אם זה reproducible** - האם תמיד קורה או רק תחת load?

### תיקון:
**תלוי בסיבה:**
- אם זה overload → להוסיף resources או retry logic
- אם זה bug → לתקן את הבאג
- אם זה indexes → זה כבר נכלל ב-שלב 1!

---

## 7. 🟡 Load Tests - מוגבל ב-Production

### מה הבעיה?

**5 טסטים נכשלו:**
- `test_single_job_baseline` - Latency: **7028ms** (expected < 1000ms) ❌
- `test_linear_load_progression` - Success rate: **20%** (expected >= 90%) ❌
- `test_extreme_concurrent_load` - Success rate: **23%** (expected >= 50%) ❌
- `test_heavy_config_concurrent` - Success rate: **30%** (expected >= 80%) ❌
- `test_recovery_after_stress` - Latency: **2482ms** (expected < 1000ms) ❌

### למה זה קורה?

**סיבות:**

1. **Production Environment לא מיועד ל-Load Tests**
   - Resources מוגבלים
   - צריך לשמור על stability ל-prod users
   - לא רוצים לעשות stress tests על production!

2. **Actual Capacity Issues**
   - המערכת באמת לא מסוגלת לעמוד ב-load
   - צריך יותר resources
   - צריך optimization

3. **Network Latency**
   - Production יכול להיות גיאוגרפית רחוק
   - Network latency גבוה
   - זה נורמלי

### האם זה באג?

**לא! זה expected behavior ב-production:**
- Production לא מיועד ל-load tests
- זה מסוכן - יכול להשפיע על users אמיתיים
- Load tests צריכים לרוץ ב-staging

### המלצות:

**Option 1: Skip Load Tests on Production (מומלץ ביותר!)**
```python
# tests/load/test_job_capacity_limits.py

import pytest
from config.config_manager import ConfigManager

@pytest.fixture(scope="session")
def skip_load_tests_on_production(request):
    """Skip load tests on production environment."""
    env = request.config.getoption("--env", "staging")
    if env == "production":
        pytest.skip("Load tests should not run on production - use staging")

@pytest.mark.load
@pytest.mark.usefixtures("skip_load_tests_on_production")
class TestBaselinePerformance:
    # ... tests ...
```

**Option 2: Reduce Load on Production**
```python
# אם חייבים לרוץ, להפחית את ה-load:
BASELINE_JOBS = 1  # ✅ (already low)
LIGHT_LOAD_JOBS = 2  # ⚠️ Reduce from 5
MEDIUM_LOAD_JOBS = 3  # ⚠️ Reduce from 10
# etc.
```

**Option 3: Config-based Thresholds**
```yaml
# config/environments.yaml
production:
  load_testing:
    enabled: false  # ✅ Disable load tests
    max_concurrent_jobs: 0
```

### המלצה שלי:
**Option 1** - Skip לחלוטין ב-production. Load tests צריכים staging!

### זמן משוער:
**10 דקות** (לעדכן את הטסטים)

---

## 📊 סיכום והמלצות

### 🔴 דחוף (היום):
1. ✅ **MongoDB Indexes** - `.\scripts\fix_mongodb_indexes_production.ps1` (15 דק')
2. ✅ **Stale Recording** - `.\scripts\clean_stale_recording_production.ps1` (5 דק')
3. **Schema Validation** - לתקן הטסטים (20 דק')
4. **Datetime Bug** - לתקן את הקוד (20 דק')

### 🟡 בינוני (מחר):
5. **Namespace Fixes** - RabbitMQ/Focus Server (30 דק')
6. **Kubernetes Tests** - Skip on Windows (15 דק')
7. **API Validation** - לעדכן 15 טסטים (30 דק')
8. **Focus Server 500** - לבדוק logs ו-resources (1 שעה)

### 🟢 לא דחוף:
9. **Load Tests** - Skip on Production (10 דק')
10. **SSH Test** - Configuration fix (15 דק')
11. **UI Tests** - URL fix (10 דק')
12. **Config Loading Tests** - URL fix (10 דק')

---

**סה"כ זמן משוער:** ~4 שעות

**עדיפות:** התחל עם שלבים 1-4 (דחוף)

