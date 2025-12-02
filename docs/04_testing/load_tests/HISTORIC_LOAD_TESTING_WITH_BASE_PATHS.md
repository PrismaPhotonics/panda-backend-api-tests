# Historic Load Testing עם MongoDB base_paths Collection

## 📋 סקירה כללית

טסטי העומס של Historic Playback משתמשים ישירות בקולקציית `base_paths` ב-MongoDB כדי למצוא recordings זמינים וליצור עליהם historic jobs. זה מאפשר יצירת עומס אמיתי על המערכת.

## 🗄️ מבנה MongoDB

### קולקציית `base_paths`

הקולקציה מכילה מסמכים שמתארים את ה-base paths של ה-recordings:

```json
{
  "_id": "ObjectId('692db0d440390e62fb9ec955')",
  "base_path": "/prisma/root/recordings",
  "guid": "25b4875f-5785-4b24-8895-121039474bcd",
  "is_archive": false
}
```

**שדות חשובים:**
- `base_path`: הנתיב הבסיסי של ה-recordings (`/prisma/root/recordings`)
- `guid`: ה-GUID שמשמש כשם הקולקציה שמכילה את ה-recordings
- `is_archive`: האם זה ארכיון (false = recordings פעילים)

### קולקציית ה-Recordings

הקולקציה נקראת על שם ה-GUID (למשל: `25b4875f-5785-4b24-8895-121039474bcd`)

כל מסמך בקולקציה:
```json
{
  "_id": "ObjectId(...)",
  "start_time": ISODate("2025-12-02T07:41:00.000Z"),
  "end_time": ISODate("2025-12-02T07:41:10.000Z"),
  "deleted": false,
  "uuid": "..."
}
```

## 🔄 תהליך השאילתה

### שלב 1: חיבור ל-MongoDB
```python
from config.config_manager import ConfigManager
from be_focus_server_tests.fixtures.recording_fixtures import fetch_recordings_from_mongodb

config_manager = ConfigManager()
```

### שלב 2: שאילתת base_paths
```python
# 1. חיבור ל-MongoDB
client = pymongo.MongoClient(...)
db = client["prisma"]

# 2. שאילתת base_paths collection
base_paths = db["base_paths"]
base_path_doc = base_paths.find_one({
    "base_path": "/prisma/root/recordings",
    "is_archive": False
})

# 3. קבלת ה-GUID
guid = base_path_doc["guid"]  # "25b4875f-5785-4b24-8895-121039474bcd"
```

### שלב 3: שאילתת Recordings
```python
# 4. שאילתת הקולקציה על שם ה-GUID
recordings_collection = db[guid]

# 5. שאילתה עם פילטרים
query = {
    "start_time": {
        "$gte": two_weeks_ago,
        "$lte": now
    },
    "deleted": False  # CRITICAL: רק recordings שלא נמחקו
}

recordings = recordings_collection.find(query).sort("start_time", -1)
```

## 🚀 שימוש ב-HistoricJobLoadTester

### יצירת Tester עם MongoDB

```python
from be_focus_server_tests.load.job_load_tester import create_historic_job_tester

# יצירת tester שמשתמש ב-MongoDB base_paths
tester = create_historic_job_tester(
    config_manager=config_manager,
    channels_min=1,
    channels_max=50,
    frequency_min=0,
    frequency_max=500,
    nfft=1024,
    recording_duration_seconds=10,
    # פרמטרים של MongoDB
    min_duration_seconds=5.0,      # מינימום משך recording
    max_duration_seconds=10.0,     # מקסימום משך recording
    weeks_back=2,                   # כמה שבועות אחורה לחפש
    max_recordings_to_load=100      # כמה recordings לטעון מהמסד
)
```

### הרצת טסט עומס

```python
# הרצת טסט עם מספר jobs
result = tester.run_load_test(
    num_jobs=10,           # סה"כ jobs
    concurrent_jobs=3,     # כמה jobs במקביל
    test_name="Historic Load Test"
)

# תוצאות
print(f"Successful: {result.successful_jobs}/{result.total_jobs}")
print(f"P95 Time: {result.p95_total_time_ms}ms")
print(f"Error Rate: {result.error_rate}%")
```

## 📊 איך זה עובד

### 1. טעינת Recordings מהמסד

כאשר יוצרים `HistoricJobLoadTester`, הוא:
1. מתחבר ל-MongoDB דרך `config_manager`
2. שואל את קולקציית `base_paths` עבור `base_path="/prisma/root/recordings"` ו-`is_archive=False`
3. מקבל את ה-GUID (`25b4875f-5785-4b24-8895-121039474bcd`)
4. שואל את הקולקציה על שם ה-GUID עבור recordings
5. מסנן לפי:
   - `deleted: false` (רק recordings פעילים)
   - טווח זמן (למשל: 2 שבועות אחורה)
   - משך זמן (למשל: 5-10 שניות)

### 2. בחירת Recording לכל Job

כאשר יוצרים job חדש:
- ה-tester בוחר recording מהרשימה בטורניר (round-robin)
- זה מבטיח פיזור עומס על recordings שונים
- כל job מקבל `start_time` ו-`end_time` מהמסד

### 3. יצירת Historic Job

```python
config = {
    "start_time": rec_start_ms,    # מ-MongoDB
    "end_time": rec_end_ms,        # מ-MongoDB
    "channels": {"min": 1, "max": 50},
    "frequencyRange": {"min": 0, "max": 500},
    ...
}

response = focus_server_api.configure_streaming_job(config)
job_id = response.job_id
```

## 🎯 דוגמאות שימוש

### טסט עומס בסיסי

```python
@pytest.mark.historic
@pytest.mark.load
def test_historic_load_basic(historic_tester):
    """טסט עומס בסיסי עם 10 jobs."""
    result = historic_tester.run_load_test(
        num_jobs=10,
        concurrent_jobs=2
    )
    
    assert result.successful_jobs >= 8, "80% success rate required"
    assert result.p95_total_time_ms < 60000, "P95 < 60s"
```

### טסט עומס כבד

```python
@pytest.mark.historic
@pytest.mark.load
@pytest.mark.heavy
def test_historic_heavy_load(heavy_historic_tester):
    """טסט עומס כבד עם 500 ערוצים."""
    result = heavy_historic_tester.run_load_test(
        num_jobs=5,
        concurrent_jobs=1
    )
    
    assert result.successful_jobs >= 3, "60% success rate for heavy load"
```

### טסט עומס ממושך

```python
@pytest.mark.historic
@pytest.mark.load
@pytest.mark.slow
def test_historic_sustained_load(historic_tester):
    """טסט עומס ממושך עם 50 jobs."""
    result = historic_tester.run_load_test(
        num_jobs=50,
        concurrent_jobs=5
    )
    
    assert result.error_rate < 25, "Error rate < 25%"
```

## ⚙️ פרמטרים חשובים

### MongoDB Query Parameters

| פרמטר | ברירת מחדל | תיאור |
|--------|------------|-------|
| `min_duration_seconds` | 5.0 | משך מינימלי של recording (שניות) |
| `max_duration_seconds` | 10.0 | משך מקסימלי של recording (שניות) |
| `weeks_back` | 2 | כמה שבועות אחורה לחפש |
| `max_recordings_to_load` | 100 | כמה recordings לטעון מהמסד |

### Job Configuration

| פרמטר | ברירת מחדל | תיאור |
|--------|------------|-------|
| `recording_duration_seconds` | 10 | משך playback שביקש (שניות) |
| `channels_min` | 1 | ערוץ מינימלי |
| `channels_max` | 50 | ערוץ מקסימלי |
| `frequency_min` | 0 | תדר מינימלי (Hz) |
| `frequency_max` | 500 | תדר מקסימלי (Hz) |
| `nfft` | 1024 | NFFT selection |

## 🔍 Debugging

### בדיקת Recordings זמינים

```python
# בדיקה ישירה של MongoDB
from be_focus_server_tests.fixtures.recording_fixtures import fetch_recordings_from_mongodb

info = fetch_recordings_from_mongodb(
    config_manager=config_manager,
    max_recordings=10,
    min_duration_seconds=5.0,
    max_duration_seconds=10.0,
    weeks_back=2
)

print(f"Found {len(info.recordings)} recordings")
for rec in info.recordings[:5]:
    print(f"  {rec.start_datetime} to {rec.end_datetime} ({rec.duration_seconds:.1f}s)")
```

### בדיקת base_paths

```python
import pymongo
from config.config_manager import ConfigManager

cm = ConfigManager()
mongo_config = cm.get_database_config()

client = pymongo.MongoClient(
    host=mongo_config['host'],
    port=mongo_config['port'],
    username=mongo_config['username'],
    password=mongo_config['password'],
    authSource=mongo_config.get('auth_source', 'prisma')
)

db = client[mongo_config.get('database', 'prisma')]
base_paths = db['base_paths']

# בדיקת כל ה-base_paths
for doc in base_paths.find():
    print(f"base_path: {doc.get('base_path')}")
    print(f"guid: {doc.get('guid')}")
    print(f"is_archive: {doc.get('is_archive')}")
    
    # בדיקת מספר recordings בקולקציה
    guid = doc.get('guid')
    if guid:
        collection = db[str(guid)]
        total = collection.count_documents({})
        active = collection.count_documents({'deleted': False})
        print(f"  Total recordings: {total}")
        print(f"  Active recordings: {active}")
    print()
```

## 📝 הערות חשובות

1. **תמיד לסנן לפי `deleted: false`** - Focus Server לא מוצא recordings שנמחקו
2. **לשתמש ב-`base_path="/prisma/root/recordings"`** - לא `/prisma/root/recordings/segy`
3. **לסנן לפי `is_archive: False`** - רק recordings פעילים
4. **Round-robin selection** - ה-tester בוחר recordings שונים לכל job כדי ליצור עומס מגוון
5. **טעינה מראש** - ה-recordings נטענים פעם אחת ונשמרים ב-cache

## 🚀 הרצת טסטים

```bash
# כל טסטי ה-historic load
pytest be_focus_server_tests/load/test_historic_load.py -v -m historic

# טסט ספציפי
pytest be_focus_server_tests/load/test_historic_load.py::TestHistoricJobLoad::test_single_historic_job -v

# עם סביבה ספציפית
$env:FOCUS_ENV = "new_production"; pytest be_focus_server_tests/load/test_historic_load.py -v -m historic
```

## 📚 קבצים קשורים

- `be_focus_server_tests/load/job_load_tester.py` - ה-tester עצמו
- `be_focus_server_tests/load/test_historic_load.py` - הטסטים
- `be_focus_server_tests/fixtures/recording_fixtures.py` - פונקציות MongoDB
- `docs/07_infrastructure/FOCUS_SERVER_RECORDINGS_NOT_FOUND_ISSUE.md` - תיעוד בעיות

