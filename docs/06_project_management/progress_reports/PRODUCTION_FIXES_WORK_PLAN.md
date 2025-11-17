# 🔧 תוכנית עבודה - תיקון בעיות Production

**תאריך יצירה:** 2025-11-03  
**סביבה:** Production (כפר סבא)  
**עדיפות:** HIGH  
**זמן משוער:** 2-3 שעות

---

## 📋 סיכום הבעיות

| # | בעיה | חומרה | זמן משוער |
|---|------|--------|-----------|
| 1 | Missing MongoDB indexes | 🔴 HIGH | 15 דקות |
| 2 | Stale recording | 🟡 MEDIUM | 5 דקות |
| 3 | Namespace שגוי (RabbitMQ/Focus Server) | 🔴 HIGH | 30 דקות |
| 4 | Datetime comparison bug | 🟡 MEDIUM | 20 דקות |
| 5 | Kubernetes API timeout | 🟢 LOW | 10 דקות |
| 6 | SSH test configuration | 🟡 MEDIUM | 15 דקות |
| 7 | Schema validation mismatch | 🟡 MEDIUM | 20 דקות |

**סה"כ:** ~2 שעות

---

## 🎯 שלב 1: תיקון MongoDB Indexes (דחוף!)

### בעיה:
```
Collection: d57c8adb-ea00-4666-83cb-0248ae9d602f
Missing indexes:
  - start_time ❌
  - end_time ❌
  - uuid ❌
  - deleted ❌
```

### פתרון:

#### אופציה A: דרך Script (מומלץ)
```powershell
.\scripts\fix_mongodb_indexes_production.ps1
```

#### אופציה B: ידנית דרך MongoDB Shell
```bash
# 1. התחבר ל-MongoDB
mongosh "mongodb://prisma:prisma@10.10.100.108:27017/prisma?authSource=prisma"

# 2. צור indexes
use prisma

# הגדר GUID
var guid = "d57c8adb-ea00-4666-83cb-0248ae9d602f";

# Index #1: start_time (קריטי לhistoric queries)
db[guid].createIndex(
  { "start_time": 1 }, 
  { background: true, name: "start_time_1" }
);

# Index #2: end_time (קריטי לhistoric queries)
db[guid].createIndex(
  { "end_time": 1 }, 
  { background: true, name: "end_time_1" }
);

# Index #3: uuid (קריטי, UNIQUE)
db[guid].createIndex(
  { "uuid": 1 }, 
  { unique: true, background: true, name: "uuid_1" }
);

# Index #4: deleted (לסינון recordings שנמחקו)
db[guid].createIndex(
  { "deleted": 1 }, 
  { background: true, name: "deleted_1" }
);

# 3. אמת שכל ה-indexes נוצרו
db[guid].getIndexes();
```

### אימות:
```powershell
pytest tests/data_quality/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_mongodb_indexes_exist_and_optimal -v --env=production
```

---

## 🎯 שלב 2: ניקוי Stale Recording

### בעיה:
```
UUID: 65777a6b-7e0d-4876-add0-7d136792ce64
Started: 2025-10-29 13:02:23 (117.3 hours ago)
Status: No end_time (crashed/failed recording)
```

### פתרון:

#### דרך Script:
```powershell
.\scripts\clean_stale_recording_production.ps1
```

#### ידנית:
```javascript
// התחבר ל-MongoDB
mongosh "mongodb://prisma:prisma@10.10.100.108:27017/prisma?authSource=prisma"

use prisma

var guid = "d57c8adb-ea00-4666-83cb-0248ae9d602f";
var staleUUID = "65777a6b-7e0d-4876-add0-7d136792ce64";

// אפשרות 1: סמן כנמחק (מומלץ - שומר היסטוריה)
db[guid].updateOne(
  { uuid: staleUUID },
  { 
    $set: { 
      deleted: true, 
      end_time: new Date(),
      cleanup_note: "Marked as deleted due to stale status (117 hours old)"
    } 
  }
);

// אפשרות 2: מחק לגמרי (רק אם בטוח)
// db[guid].deleteOne({ uuid: staleUUID });

// אמת שהרשומה עודכנה
db[guid].findOne({ uuid: staleUUID });
```

### אימות:
```powershell
pytest tests/data_quality/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_recordings_have_all_required_metadata -v --env=production
```

---

## 🎯 שלב 3: תיקון Namespace (RabbitMQ/Focus Server)

### בעיה:
```python
# Code checks 'default' namespace, but services are in 'panda' namespace
namespace: str = "default"  # ❌ שגוי!
```

### פתרון:

#### 3.1 תיקון RabbitMQ Manager
**קובץ:** `src/infrastructure/rabbitmq_manager.py`

**שינוי:**
```python
# שורה 69: שנה default namespace
namespace: str = "panda",  # ✅ תיקן מ-"default" ל-"panda"
```

**בדוק גם:**
- שורה 496: האם יש עוד מקום עם `default`?

#### 3.2 תיקון Focus Server Manager
**קובץ:** `src/infrastructure/focus_server_manager.py`

**שינוי:**
```python
# שורה 40: שנה default namespace
namespace: str = "panda",  # ✅ תיקן מ-"default" ל-"panda"
```

#### 3.3 עדכון Config (אופציונלי)
**קובץ:** `config/environments.yaml`

אם יש הגדרת namespace ב-production section, עדכן שם גם כן.

### אימות:
```powershell
# הרץ טסטים שצריכים RabbitMQ/Focus Server
pytest tests/infrastructure/test_rabbitmq_connectivity.py -v --env=production
```

---

## 🎯 שלב 4: תיקון Datetime Comparison Bug

### בעיה:
```python
# Error: can't subtract offset-naive and offset-aware datetimes
```

**קובץ:** `tests/data_quality/test_mongodb_data_quality.py`

**שורה:** ~282-283 (בתוך `test_historical_vs_live_recordings`)

### פתרון:

```python
# לפני (שגוי):
current_time = datetime.now()  # offset-naive
if recording_start < current_time - timedelta(hours=24):  # ❌ Error!

# אחרי (תיקן):
from datetime import datetime, timezone, timedelta

current_time = datetime.now(timezone.utc)  # offset-aware (UTC)
if recording_start < current_time - timedelta(hours=24):  # ✅ עובד!
```

**או אם recording_start הוא offset-naive:**
```python
# אפשרות 1: המר ל-aware
if recording_start.tzinfo is None:
    recording_start = recording_start.replace(tzinfo=timezone.utc)

# אפשרות 2: המר current_time ל-naive (אם recording_start הוא naive)
if recording_start.tzinfo is None:
    current_time = datetime.now()  # naive
```

### אימות:
```powershell
pytest tests/data_quality/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_historical_vs_live_recordings -v --env=production
```

---

## 🎯 שלב 5: תיקון Kubernetes API Timeout

### בעיה:
```
Connection to 10.10.100.102:6443 timed out
```

### פתרון:

#### אופציה A: לעדכן את הטסט - לא נגיש מ-Windows (OK)
**קובץ:** `tests/infrastructure/test_basic_connectivity.py`

**שינוי:**
```python
@pytest.mark.skipif(
    os.environ.get("CI") or not os.path.exists("/usr/bin/kubectl"),
    reason="Kubernetes API not directly accessible from Windows - use SSH tunnel"
)
def test_kubernetes_direct_connection(...):
    # ... existing code ...
```

#### אופציה B: יצירת SSH Tunnel (אם צריך)
```powershell
# דרך SSH tunnel:
ssh -L 6443:10.10.100.102:6443 prisma@10.10.100.113
```

### המלצה:
לסמן את הטסט כ-skip אם הוא רץ מ-Windows, כי K8s API לא נגיש ישירות.

---

## 🎯 שלב 6: תיקון SSH Test Configuration

### בעיה:
```
Error: 'host' key not found
```

**קובץ:** `tests/infrastructure/test_basic_connectivity.py`

**שורה:** ~662-665

### פתרון:

בדוק מה הטסט מצפה לראות ב-config. כנראה צריך:
```python
def test_ssh_direct_connection(config_manager):
    """Test SSH connectivity to worker node."""
    ssh_config = config_manager.get_ssh_config()
    
    # בדוק שיש host
    assert "target_host" in ssh_config, "SSH target_host not found in config"
    assert "host" in ssh_config["target_host"], "SSH host not found"
    
    host = ssh_config["target_host"]["host"]
    # ... rest of test ...
```

---

## 🎯 שלב 7: תיקון Schema Validation

### בעיה:
```
Collection: d57c8adb-ea00-4666-83cb-0248ae9d602f-unrecognized_recordings
Document fields: _id, folder_name, file_count, update_time
Validation failed: Missing required fields
```

### פתרון:

הטסט בודק `unrecognized_recordings` collection, אבל היא לא אמורה להיות אותה schema כ-recordings הראשיים!

**קובץ:** `tests/data_quality/test_mongodb_indexes_and_schema.py`

**שינוי:**
```python
def test_recordings_document_schema_validation(...):
    # לפני: בדוק כל recording collection
    # אחרי: בדוק רק את הראשי (לא unrecognized)
    
    recording_collections = [
        c for c in collections 
        if not c.endswith('-unrecognized_recordings')  # ✅ דלג על unrecognized
    ]
    
    for collection_name in recording_collections:
        # ... validate schema ...
```

---

## 📝 סדר ביצוע מומלץ

### יום 1 (דחוף):
1. ✅ **שלב 1:** MongoDB Indexes (15 דקות)
2. ✅ **שלב 2:** Stale Recording (5 דקות)
3. ✅ **שלב 3:** Namespace fixes (30 דקות)
4. ✅ **אימות:** הרץ את הטסטים שמתוקנים

### יום 2 (לא דחוף):
5. ✅ **שלב 4:** Datetime bug (20 דקות)
6. ✅ **שלב 5:** Kubernetes test (10 דקות)
7. ✅ **שלב 6:** SSH test (15 דקות)
8. ✅ **שלב 7:** Schema validation (20 דקות)
9. ✅ **אימות מלא:** הרץ את כל הטסטים שוב

---

## ✅ Checklist סיום

- [ ] MongoDB indexes נוצרו
- [ ] Stale recording נוקה
- [ ] Namespace תוקן (RabbitMQ/Focus Server)
- [ ] Datetime bug תוקן
- [ ] Kubernetes test תוקן/מסומן skip
- [ ] SSH test תוקן
- [ ] Schema validation תוקן
- [ ] כל הטסטים עוברים
- [ ] תיעוד עודכן

---

## 🔗 קישורים חשובים

- **Scripts:** `scripts/fix_mongodb_indexes_production.ps1`
- **Config:** `config/environments.yaml`
- **Test Results:** `docs/04_testing/test_results/PRODUCTION_RUN_SUMMARY_2025-11-03.md`
- **Documentation:** `docs/02_user_guides/MONGODB_INDEXES_FIX_GUIDE.md`

---

**תאריך עדכון:** 2025-11-03  
**סטטוס:** Ready to start

