# ניתוח מפורט לפרטי פרטים - כל הטסטים מ-Jira

## מטרת המסמך
מסמך זה מכין אותך לפגישה ומכסה כל שאלה אפשרית לגבי כל טסט:
- **מה המטרה** של כל טסט
- **מה בודקים** בדיוק
- **למה זה חיוני** (הנחיצות)
- **איך ממשים** זאת בקוד
- **שאלות צפויות** ותשובות מוכנות

---

## 📊 סיכום כללי

### סטטיסטיקה
- **סה"כ טסטים**: 13
- **קטגוריה עיקרית**: Data Quality & Integrity
- **פוקוס**: MongoDB, PostgreSQL, Historic Playback
- **Priority Distribution**:
  - Critical: 2 טסטים
  - High: 4 טסטים  
  - Medium: 7 טסטים

### חלוקה לפי קטגוריות

#### 1. **MongoDB Infrastructure Tests** (5 טסטים)
- `PZ-13809`: Verify Required Collections Exist
- `PZ-13810`: Verify Critical Indexes Exist
- `PZ-13811`: Validate Recordings Document Schema
- `PZ-13812`: Verify Recordings Have Complete Metadata
- `PZ-13598`: Mongo Collections and Schema (Parent)

#### 2. **MongoDB Data Quality Tests** (3 טסטים)
- `PZ-13683`: MongoDB Collections Exist
- `PZ-13684`: node4 Schema Validation
- `PZ-13685`: Recordings Metadata Completeness
- `PZ-13686`: MongoDB Indexes Validation

#### 3. **Data Lifecycle & Classification** (1 טסט)
- `PZ-13705`: Historical vs Live Recordings Classification

#### 4. **Historic Playback & Integrity** (1 טסט)
- `PZ-13867`: Historic Playback - Data Integrity Validation

#### 5. **PostgreSQL Tests** (1 טסט)
- `PZ-13599`: Postgres Connectivity and Catalogs

---

# 🔬 ניתוח מפורט של כל טסט

---

## טסט #1: PZ-13867 - Historic Playback Data Integrity

### 🎯 מה המטרה של הטסט?
**המטרה המרכזית**: לוודא שכל הנתונים שחוזרים מ-Historic Playback תקינים, מסודרים כרונולוגית, ושלמים - ללא נתונים פגומים או חסרים.

### 📋 מה בדיוק בודקים?

#### 1. **Timestamp Integrity (שלמות חותמות זמן)**
```python
# בודקים שלושה דברים:
assert row.startTimestamp <= row.endTimestamp  # זמן התחלה לא אחרי זמן סיום
assert row.startTimestamp >= last_timestamp    # סדר כרונולוגי נשמר
assert no_duplicate_timestamps                 # אין כפילויות
```

**למה זה קריטי?**
- אם זמן התחלה > זמן סיום → הנתונים פגומים
- אם הסדר לא כרונולוגי → הצגה לא נכונה ב-UI
- כפילויות → נתונים מיותרים, בזבוז משאבים

#### 2. **Sensor Data Completeness (שלמות נתוני חיישנים)**
```python
assert len(row.sensors) > 0           # יש לפחות חיישן אחד
assert sensor.id >= 0                 # ID של חיישן תקין
assert len(sensor.intensity) > 0     # יש נתוני אינטנסיביות
```

**למה זה קריטי?**
- ללא חיישנים → אין מה להציג ב-waterfall
- ID שלילי → שגיאה לוגית, נתון פגום
- intensity ריק → אין נתוני גרף בפועל

#### 3. **Data Volume Validation (וולידציה של כמות נתונים)**
```python
assert len(all_rows) > 0              # קיבלנו נתונים בכלל
assert waterfall_response.status_code == 208  # Playback הושלם תקין
```

### 🔴 למה הטסט הזה נחיץ?

#### תרחישי כשל ללא הטסט:
1. **UI Crash**: אם יש נתונים פגומים, ה-UI יתרסק בניסיון להציג waterfall
2. **Wrong Timeline**: סדר לא נכון → המשתמש רואה אירועים בסדר שגוי
3. **Data Loss Detection**: מזהה חורים בנתונים לפני שהמשתמש מגלה
4. **Performance Issues**: נתונים כפולים גורמים לעומס מיותר

#### Business Impact:
- **אמינות**: לקוחות סומכים שההיסטוריה מדויקת
- **Forensics**: ניתוח אירועים דורש נתונים מושלמים
- **Compliance**: ברגולציה, נדרשת שלמות מוחלטת

### 💻 איך ממשים את זה בקוד?

#### **ארכיטקטורה**:
```
tests/integration/api/test_historic_playback_flow.py
    │
    ├─> FocusServerAPI.config_task()        # שלב 1: הגדרת task
    ├─> Loop: FocusServerAPI.get_waterfall() # שלב 2: איסוף נתונים
    └─> Validation Logic                     # שלב 3: בדיקות integrity
```

#### **קוד מלא**:
```python
import pytest
import time
from datetime import datetime
from typing import List

class TestHistoricPlaybackDataIntegrity:
    """
    Test Suite: Historic Playback Data Integrity
    Purpose: Ensure all data returned from historic playback is valid
    """
    
    @pytest.fixture
    def historic_time_range(self):
        """
        Generate a 5-minute time range for testing.
        Returns: (start_time, end_time) in yymmddHHMMSS format
        """
        # Use known good recording time range
        return ("250101120000", "250101120500")  # 5 minutes
    
    @pytest.fixture
    def historic_config(self, historic_time_range):
        """
        Build config payload for historic playback task.
        """
        start_time, end_time = historic_time_range
        return {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 0, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": start_time,
            "end_time": end_time,
            "view_type": 0  # Historic playback mode
        }
    
    def test_historic_playback_data_integrity(
        self,
        focus_server_api,
        historic_config,
        logger
    ):
        """
        Test: Historic Playback Data Integrity Validation
        
        Steps:
        1. Configure historic task (5-minute range)
        2. Poll GET /waterfall until completion (status 208)
        3. Validate EVERY row for:
           - Timestamp ordering (start <= end)
           - Sequential timestamps (no gaps/overlaps)
           - Sensor data presence (len > 0)
           - Valid sensor IDs (>= 0)
           - Non-empty intensity arrays
        4. Track statistics and report
        
        Expected: ALL integrity checks pass, no corrupted data
        """
        task_id = f"integrity_test_{int(time.time())}"
        
        # ============================================
        # STEP 1: Configure Historic Task
        # ============================================
        logger.info(f"Configuring historic task: {task_id}")
        response = focus_server_api.config_task(
            task_id=task_id,
            config_payload=historic_config
        )
        
        assert response.status == "Config received successfully", \
            f"Failed to configure task: {response.status}"
        
        # ============================================
        # STEP 2: Collect All Data Blocks
        # ============================================
        all_rows = []
        last_timestamp = 0
        timestamp_set = set()  # Track duplicates
        
        max_attempts = 100  # Prevent infinite loop
        
        for attempt in range(1, max_attempts + 1):
            logger.debug(f"Polling waterfall (attempt {attempt})...")
            
            waterfall_response = focus_server_api.get_waterfall(
                task_id=task_id,
                max_rows=20
            )
            
            # ============================================
            # HANDLE RESPONSE STATUS
            # ============================================
            if waterfall_response.status_code == 201:
                # Data available
                if not waterfall_response.data:
                    time.sleep(2.0)
                    continue
                
                # Process each block
                for block in waterfall_response.data:
                    for row in block.rows:
                        all_rows.append(row)
                        
                        # ============================================
                        # VALIDATION 1: Timestamp Ordering
                        # ============================================
                        assert row.startTimestamp <= row.endTimestamp, \
                            f"ROW {len(all_rows)}: start > end " \
                            f"({row.startTimestamp} > {row.endTimestamp})"
                        
                        # ============================================
                        # VALIDATION 2: Sequential Order
                        # ============================================
                        assert row.startTimestamp >= last_timestamp, \
                            f"ROW {len(all_rows)}: timestamps not sequential " \
                            f"(last={last_timestamp}, current={row.startTimestamp})"
                        
                        # ============================================
                        # VALIDATION 3: No Duplicates
                        # ============================================
                        timestamp_key = (row.startTimestamp, row.endTimestamp)
                        assert timestamp_key not in timestamp_set, \
                            f"ROW {len(all_rows)}: duplicate timestamp detected " \
                            f"({timestamp_key})"
                        timestamp_set.add(timestamp_key)
                        
                        # Update tracker
                        last_timestamp = row.endTimestamp
                        
                        # ============================================
                        # VALIDATION 4: Sensor Data Presence
                        # ============================================
                        assert len(row.sensors) > 0, \
                            f"ROW {len(all_rows)}: no sensor data found"
                        
                        # ============================================
                        # VALIDATION 5: Sensor Validity
                        # ============================================
                        for sensor_idx, sensor in enumerate(row.sensors):
                            # Check sensor ID
                            assert sensor.id >= 0, \
                                f"ROW {len(all_rows)}, SENSOR {sensor_idx}: " \
                                f"invalid sensor ID ({sensor.id})"
                            
                            # Check intensity data
                            assert len(sensor.intensity) > 0, \
                                f"ROW {len(all_rows)}, SENSOR {sensor_idx}: " \
                                f"empty intensity array"
                        
                        # Log progress every 50 rows
                        if len(all_rows) % 50 == 0:
                            logger.info(f"Validated {len(all_rows)} rows...")
            
            elif waterfall_response.status_code == 208:
                # Playback complete
                logger.info("Historic playback completed (status 208)")
                break
            
            elif waterfall_response.status_code == 206:
                # Processing, wait
                time.sleep(2.0)
            
            else:
                pytest.fail(
                    f"Unexpected status code: {waterfall_response.status_code}"
                )
        
        # ============================================
        # STEP 3: Final Assertions
        # ============================================
        assert len(all_rows) > 0, \
            "No rows collected during playback! Check if recording exists."
        
        # ============================================
        # STEP 4: Statistics & Report
        # ============================================
        total_sensors = sum(len(row.sensors) for row in all_rows)
        avg_sensors_per_row = total_sensors / len(all_rows)
        
        time_range = (
            all_rows[-1].endTimestamp - all_rows[0].startTimestamp
        ) / 1_000_000  # Convert microseconds to seconds
        
        logger.info("=" * 60)
        logger.info("HISTORIC PLAYBACK DATA INTEGRITY TEST: PASSED ✅")
        logger.info("=" * 60)
        logger.info(f"Total rows validated: {len(all_rows)}")
        logger.info(f"Total sensors processed: {total_sensors}")
        logger.info(f"Avg sensors per row: {avg_sensors_per_row:.1f}")
        logger.info(f"Time range covered: {time_range:.1f} seconds")
        logger.info(f"No corrupted data detected")
        logger.info("=" * 60)
```

### 🔍 שאלות צפויות והתשובות

#### **שאלה 1: "למה לא מספיק לבדוק רק את הסטטוס קוד?"**
**תשובה**: 
```
סטטוס קוד 208 אומר ש-playback הסתיים, אבל לא מבטיח שהנתונים תקינים.
דוגמה: אפשר לקבל status 208 אבל עם:
- נתונים לא מסודרים כרונולוגית
- חיישנים עם intensity ריק
- timestamps כפולים

הטסט שלנו עושה DEEP VALIDATION על כל row.
```

#### **שאלה 2: "מה קורה אם הטסט נכשל?"**
**תשובה**:
```
1. מזהה בדיוק איפה הבעיה (row number, sensor index)
2. מספק assertion message מפורט
3. מאפשר debug מהיר
4. מונע deployment של version פגומה

דוגמת שגיאה:
"ROW 47, SENSOR 3: empty intensity array"
→ מיד יודעים לחפש בעיה בחיישן 3, row 47
```

#### **שאלה 3: "כמה זמן הטסט לוקח?"**
**תשובה**:
```
- Playback של 5 דקות: ~30-60 שניות
- Validation של כל row: ~1ms per row
- סה"כ זמן ריצה: 1-2 דקות

זה אופטימלי כי:
1. רק 5 דקות היסטוריה (לא שעות)
2. Validation במקביל לאיסוף
3. Early exit אם יש שגיאה
```

#### **שאלה 4: "איך בוחרים את טווח הזמן לטסט?"**
**תשובה**:
```python
# אסטרטגיית בחירה:
def choose_test_time_range():
    # Option 1: Known good recording (הכי מומלץ)
    return query_last_successful_recording()
    
    # Option 2: Recent recording
    return get_recordings_from_last_hour()
    
    # Option 3: Fixed test data
    return ("250101120000", "250101120500")

# למה 5 דקות?
# - מספיק נתונים לוולידציה (100+ rows)
# - לא ארוך מדי (מהיר לרוץ)
# - מכסה כמה channels
```

#### **שאלה 5: "מה עושים אם יש gaps בנתונים?"**
**תשובה**:
```
הטסט מזהה gaps דרך:
1. Sequential timestamp check
2. Expected vs actual row count

אם יש gap → הטסט יזהה שהזמן קפץ יותר מדי.

אבל: gaps לגיטימיים אם:
- היה הפסקה בהקלטה
- חיישן היה offline

לכן בודקים:
✅ Timestamps מסודרים (אפילו עם gaps)
❌ Timestamps לא מסודרים (בעיה!)
```

---

## טסט #2: PZ-13812 - Verify Recordings Have Complete Metadata

### 🎯 מה המטרה של הטסט?
**המטרה**: לוודא שכל ההקלטות ב-MongoDB מכילות את כל שדות ה-metadata הנדרשים - ללא שדות חסרים, null, או ריקים.

### 📋 מה בדיוק בודקים?

#### 1. **Required Fields Presence**
```python
required_fields = ["uuid", "start_time", "end_time", "path", "node"]

for recording in sample:
    for field in required_fields:
        assert field in recording        # השדה קיים
        assert recording[field] is not None  # לא null
        assert recording[field] != ""    # לא ריק
```

**למה כל שדה קריטי?**

| Field | Purpose | What Happens If Missing |
|-------|---------|-------------------------|
| `uuid` | Unique identifier | Cannot reference recording |
| `start_time` | Recording start timestamp | Cannot query by time |
| `end_time` | Recording end timestamp | Cannot calculate duration |
| `path` | File location | Cannot load raw data |
| `node` | Recording node ID | Cannot filter by source |

#### 2. **Value Validation**
```python
# Time fields must be positive
assert recording["start_time"] > 0
assert recording["end_time"] > 0

# String fields must be non-empty
assert len(recording["uuid"]) > 0
assert len(recording["path"]) > 0
```

#### 3. **Sample Size Validation**
```python
sample = list(recordings.find().sort("start_time", -1).limit(10))
assert len(sample) >= 10, "Not enough recordings for testing"
```

**למה 10 recordings?**
- מספיק גדול לזהות patterns
- לא מדגום את כל ה-DB (יעיל)
- Statistical confidence

### 🔴 למה הטסט הזה נחיץ?

#### תרחישי כשל:
1. **POST /recordings_in_time_range fails**
   ```python
   # אם חסר start_time או end_time:
   query = {"start_time": {"$gte": start, "$lte": end}}
   # → Query returns nothing or crashes
   ```

2. **Cannot Load Raw Data**
   ```python
   # אם חסר path:
   file_path = recording["path"]  # KeyError!
   data = load_prp2_file(file_path)  # Cannot proceed
   ```

3. **UUID Collision**
   ```python
   # אם uuid ריק או null → כפילויות
   recordings = {"": recording1, "": recording2}
   # → Data corruption
   ```

### 💻 איך ממשים את זה בקוד?

#### **File Location**:
```
tests/integration/infrastructure/test_mongodb_data_quality.py
```

#### **Full Implementation**:
```python
import pytest
from pymongo import MongoClient
from typing import List, Dict, Any

class TestMongoDBDataQuality:
    """
    Test Suite: MongoDB Data Quality
    Focus: Metadata completeness and integrity
    """
    
    @pytest.fixture
    def mongo_client(self, config_manager):
        """
        Establish MongoDB connection.
        Yields: Connected MongoClient instance
        """
        mongo_config = config_manager.get_mongodb_config()
        
        client = MongoClient(
            host=mongo_config["host"],
            port=mongo_config["port"],
            username=mongo_config["username"],
            password=mongo_config["password"],
            serverSelectionTimeoutMS=5000  # 5 sec timeout
        )
        
        # Test connection
        client.admin.command('ping')
        
        yield client
        
        # Cleanup
        client.close()
    
    @pytest.fixture
    def recordings_collection(self, mongo_client, config_manager):
        """
        Get recordings collection.
        Returns: MongoDB collection object
        """
        db_name = config_manager.get("mongodb.database_name")
        db = mongo_client[db_name]
        return db["recordings"]
    
    def test_recordings_have_all_required_metadata(
        self,
        recordings_collection,
        logger
    ):
        """
        Test: Verify Recordings Have Complete Metadata
        
        Purpose:
        Ensure all recordings in MongoDB contain all required metadata
        fields populated (not null/empty).
        
        Business Impact:
        - Missing metadata breaks history playback
        - Empty UUIDs cause data corruption
        - Missing paths prevent raw data loading
        
        Steps:
        1. Sample 10 recent recordings
        2. Verify all required fields exist
        3. Verify no null or empty values
        4. Verify time values are positive
        
        Expected: All recordings have complete, valid metadata
        """
        
        # ============================================
        # STEP 1: Get Sample Recordings
        # ============================================
        SAMPLE_SIZE = 10
        
        logger.info(f"Fetching {SAMPLE_SIZE} recent recordings...")
        
        sample = list(
            recordings_collection.find()
            .sort("start_time", -1)  # Most recent first
            .limit(SAMPLE_SIZE)
        )
        
        assert len(sample) >= SAMPLE_SIZE, \
            f"Insufficient recordings: found {len(sample)}, " \
            f"expected {SAMPLE_SIZE}. Database may be empty."
        
        logger.info(f"✓ Retrieved {len(sample)} recordings for validation")
        
        # ============================================
        # STEP 2: Define Required Fields
        # ============================================
        required_fields = {
            # Field name: (expected_type, validation_function)
            "uuid": (str, lambda v: len(v) > 0),
            "start_time": ((int, float), lambda v: v > 0),
            "end_time": ((int, float), lambda v: v > 0),
            "path": (str, lambda v: len(v) > 0),
            "node": (str, lambda v: len(v) > 0)
        }
        
        # ============================================
        # STEP 3: Validate Each Recording
        # ============================================
        validation_errors = []
        
        for idx, recording in enumerate(sample, 1):
            logger.info(f"\nValidating recording {idx}/{len(sample)}:")
            logger.info(f"  UUID: {recording.get('uuid', 'MISSING')}")
            
            # Check each required field
            for field_name, (expected_type, validator) in required_fields.items():
                
                # ----------------------------------------
                # Check 1: Field Exists
                # ----------------------------------------
                if field_name not in recording:
                    error = f"Recording {idx}: Missing field '{field_name}'"
                    validation_errors.append(error)
                    logger.error(f"  ❌ {error}")
                    continue
                
                value = recording[field_name]
                
                # ----------------------------------------
                # Check 2: Not None
                # ----------------------------------------
                if value is None:
                    error = f"Recording {idx}: Field '{field_name}' is None"
                    validation_errors.append(error)
                    logger.error(f"  ❌ {error}")
                    continue
                
                # ----------------------------------------
                # Check 3: Not Empty (strings)
                # ----------------------------------------
                if isinstance(expected_type, type) and expected_type == str:
                    if value == "":
                        error = f"Recording {idx}: Field '{field_name}' is empty"
                        validation_errors.append(error)
                        logger.error(f"  ❌ {error}")
                        continue
                
                # ----------------------------------------
                # Check 4: Correct Type
                # ----------------------------------------
                if isinstance(expected_type, tuple):
                    type_ok = isinstance(value, expected_type)
                else:
                    type_ok = isinstance(value, expected_type)
                
                if not type_ok:
                    error = (
                        f"Recording {idx}: Field '{field_name}' has wrong type "
                        f"(got {type(value).__name__}, expected {expected_type})"
                    )
                    validation_errors.append(error)
                    logger.error(f"  ❌ {error}")
                    continue
                
                # ----------------------------------------
                # Check 5: Custom Validation
                # ----------------------------------------
                try:
                    is_valid = validator(value)
                    if not is_valid:
                        error = (
                            f"Recording {idx}: Field '{field_name}' "
                            f"failed validation (value={value})"
                        )
                        validation_errors.append(error)
                        logger.error(f"  ❌ {error}")
                        continue
                except Exception as e:
                    error = (
                        f"Recording {idx}: Field '{field_name}' "
                        f"validation error: {e}"
                    )
                    validation_errors.append(error)
                    logger.error(f"  ❌ {error}")
                    continue
                
                # Success
                logger.info(f"  ✓ Field '{field_name}': OK")
            
            # ----------------------------------------
            # Additional Logic Checks
            # ----------------------------------------
            if "start_time" in recording and "end_time" in recording:
                if recording["start_time"] >= recording["end_time"]:
                    error = (
                        f"Recording {idx}: start_time >= end_time "
                        f"({recording['start_time']} >= {recording['end_time']})"
                    )
                    validation_errors.append(error)
                    logger.error(f"  ❌ {error}")
        
        # ============================================
        # STEP 4: Final Assertions
        # ============================================
        if validation_errors:
            error_summary = "\n".join(f"  - {err}" for err in validation_errors)
            pytest.fail(
                f"\n\nMetadata validation FAILED! "
                f"Found {len(validation_errors)} errors:\n{error_summary}"
            )
        
        # ============================================
        # STEP 5: Success Report
        # ============================================
        logger.info("\n" + "=" * 60)
        logger.info("METADATA COMPLETENESS TEST: PASSED ✅")
        logger.info("=" * 60)
        logger.info(f"Validated {len(sample)} recordings")
        logger.info(f"All recordings have complete metadata")
        logger.info(f"Required fields checked: {', '.join(required_fields.keys())}")
        logger.info("=" * 60)
```

### 🔍 שאלות צפויות והתשובות

#### **שאלה 1: "למה לבדוק רק 10 recordings ולא את כולם?"**
**תשובה**:
```
Sampling Strategy:
1. יעילות: בדיקת כל ה-DB (1000+ recordings) תיקח דקות
2. מייצג: 10 recordings אחרונים מייצגים את המצב הנוכחי
3. Early Detection: אם יש בעיה, ככל הנראה נגלה אותה ב-10 הראשונים

אבל: אפשר להוסיף flag לבדיקה מלאה בCI/CD:
```python
@pytest.mark.full_scan
def test_all_recordings_metadata():
    # Scan entire collection
    sample = recordings_collection.find()
```

#### **שאלה 2: "מה אם יש recording לגיטימי בלי end_time?"**
**תשובה**:
```python
# Recordings חיים (Live) יכולים להיות בלי end_time
# הטסט צריך להתחשב בזה:

if "deleted" in recording and recording["deleted"] == False:
    if "end_time" not in recording or recording["end_time"] is None:
        # This might be a LIVE recording - check age
        age_hours = (now - recording["start_time"]) / 3600
        if age_hours > 24:
            # Stale recording - probably crashed
            logger.warning(f"Stale recording: {recording['uuid']}")
        else:
            # Live recording - OK
            continue
```

#### **שאלה 3: "איך מטפלים ב-recordings שנמחקו?"**
**תשובה**:
```python
# Option 1: Skip deleted recordings
sample = recordings_collection.find({"deleted": False})

# Option 2: Test deleted recordings separately
@pytest.mark.parametrize("deleted_status", [True, False])
def test_metadata_by_deletion_status(deleted_status):
    sample = recordings_collection.find({"deleted": deleted_status})
    # Validate...

# המלצה: בדוק רק non-deleted כי deleted יכולים להיות חלקיים
```

---

## טסט #3: PZ-13811 - Validate Recordings Document Schema

### 🎯 מה המטרה?
**לוודא שכל document ב-`recordings` collection יש את כל השדות הנדרשים עם הטיפוסים הנכונים**.

### 📋 מה בדיוק בודקים?

#### **Schema Definition**
```python
EXPECTED_SCHEMA = {
    "uuid": str,
    "start_time": (int, float),   # Unix epoch
    "end_time": (int, float),     # Unix epoch  
    "path": str,                  # File path
    "node": str,                  # Node identifier
    "sensor_min": (int, float),   # Optional
    "sensor_max": (int, float)    # Optional
}
```

#### **Type Validation**
```python
recording = recordings.find_one(sort=[("start_time", -1)])

# Check each field type
assert isinstance(recording["uuid"], str)
assert isinstance(recording["start_time"], (int, float))
assert isinstance(recording["end_time"], (int, float))
```

#### **Logical Validation**
```python
# Time logic
assert recording["start_time"] < recording["end_time"]

# Path format
assert recording["path"].endswith(".prp2") or \
       recording["path"].endswith(".segy")

# Sensor range
if "sensor_min" in recording and "sensor_max" in recording:
    assert recording["sensor_min"] <= recording["sensor_max"]
```

### 🔴 למה נחיץ?

#### **Type Mismatch = Runtime Errors**
```python
# אם start_time הוא string במקום number:
start_time = recording["start_time"]  # "2025-01-01"
if start_time > threshold:            # TypeError!
```

#### **Schema Drift Detection**
```
זמן → מישהו משנה את הקוד
     → מתחיל לכתוב שדה חדש בפורמט שונה
     → הטסט קולט את זה מייד
```

### 💻 Implementation

```python
def test_recording_schema_validation(
    self,
    recordings_collection,
    logger
):
    """
    Test: Validate Recordings Document Schema
    
    Purpose: Verify document structure and field types
    """
    
    # Get one recent recording
    recording = recordings_collection.find_one(
        sort=[("start_time", -1)]
    )
    
    assert recording is not None, "No recordings found in database"
    
    logger.info(f"Validating schema for recording: {recording.get('uuid')}")
    
    # ============================================
    # Required Fields Check
    # ============================================
    required_fields = ["uuid", "start_time", "end_time", "path"]
    
    for field in required_fields:
        assert field in recording, f"Missing required field: {field}"
        logger.info(f"✓ Field '{field}' present")
    
    # ============================================
    # Type Validation
    # ============================================
    assert isinstance(recording["uuid"], str), \
        f"uuid must be string, got {type(recording['uuid'])}"
    
    assert isinstance(recording["start_time"], (int, float)), \
        f"start_time must be number, got {type(recording['start_time'])}"
    
    assert isinstance(recording["end_time"], (int, float)), \
        f"end_time must be number, got {type(recording['end_time'])}"
    
    assert isinstance(recording["path"], str), \
        f"path must be string, got {type(recording['path'])}"
    
    logger.info("✓ All field types correct")
    
    # ============================================
    # Logical Validation
    # ============================================
    assert recording["start_time"] < recording["end_time"], \
        f"Invalid time range: {recording['start_time']} >= {recording['end_time']}"
    
    logger.info("✓ Time range logic valid")
    
    # ============================================
    # Optional Fields
    # ============================================
    if "sensor_min" in recording:
        assert isinstance(recording["sensor_min"], (int, float))
        logger.info(f"✓ Optional field 'sensor_min' valid: {recording['sensor_min']}")
    
    if "sensor_max" in recording:
        assert isinstance(recording["sensor_max"], (int, float))
        logger.info(f"✓ Optional field 'sensor_max' valid: {recording['sensor_max']}")
    
    if "sensor_min" in recording and "sensor_max" in recording:
        assert recording["sensor_min"] <= recording["sensor_max"], \
            "sensor_min > sensor_max"
        logger.info("✓ Sensor range logic valid")
    
    logger.info("\n" + "=" * 60)
    logger.info("RECORDING SCHEMA VALIDATION: PASSED ✅")
    logger.info("=" * 60)
```

### 🔍 שאלות והתשובות

#### **שאלה: "מה ההבדל בין הטסט הזה ל-PZ-13812?"**
**תשובה**:
```
PZ-13811 (Schema Validation):
- בודק STRUCTURE (אילו שדות קיימים)
- בודק TYPES (האם המספרים באמת מספרים)
- דוגמה 1 recording

PZ-13812 (Metadata Completeness):
- בודק VALUES (האם יש ערכים או null)
- בודק EMPTINESS (האם strings ריקים)
- דוגמה 10 recordings

שניהם משלימים:
✅ Schema → "יש שדה start_time מטיפוס number"
✅ Completeness → "start_time לא null ולא 0"
```

---

## טסט #4: PZ-13810 - Verify Critical MongoDB Indexes Exist

### 🎯 מה המטרה?
**לוודא שכל האינדקסים הקריטיים קיימים על `recordings` collection - כדי להבטיח ביצועים מהירים**.

### 📋 מה בדיוק בודקים?

#### **Required Indexes**
```python
REQUIRED_INDEXES = [
    "start_time_1",    # For time-based queries
    "end_time_1",      # For range queries
    "uuid_1",          # For lookups by ID
    "_id_"             # Default MongoDB index
]
```

#### **Why Each Index Matters**

| Index | Query Type | Without Index Performance |
|-------|------------|---------------------------|
| `start_time_1` | `find({"start_time": {$gte: X}})` | O(n) - Full collection scan |
| `end_time_1` | `find({"end_time": {$lte: Y}})` | O(n) - Slow |
| `uuid_1` | `find({"uuid": "abc123"})` | O(n) - Very slow |

**With Indexes**: O(log n) - Fast!

### 🔴 למה נחיץ?

#### **Performance Crisis Without Indexes**
```python
# Scenario: Query recordings in time range
# Collection size: 10,000 recordings

# WITHOUT index on start_time:
query_time = 5000ms  # Scans all 10k docs
# → POST /recordings_in_time_range is SLOW
# → Users wait 5+ seconds
# → Bad UX

# WITH index on start_time:
query_time = 50ms    # Uses index
# → Users get results instantly
```

#### **Real-World Impact**
```
אם אין indexes:
1. History playback ייקח דקות במקום שניות
2. MongoDB CPU spike → server overload
3. Concurrent users → timeout errors
4. Production incident

הטסט מונע את זה!
```

### 💻 Implementation

```python
def test_mongodb_indexes_exist_and_optimal(
    self,
    recordings_collection,
    logger
):
    """
    Test: Verify Critical MongoDB Indexes Exist
    
    Purpose: Ensure performance-critical indexes exist
    
    Impact: Missing indexes cause:
    - Slow queries (O(n) instead of O(log n))
    - High CPU usage on MongoDB
    - Timeout errors for users
    - Poor production performance
    """
    
    # ============================================
    # STEP 1: Get All Indexes
    # ============================================
    indexes = list(recordings_collection.list_indexes())
    index_names = [idx['name'] for idx in indexes]
    
    logger.info(f"Found {len(indexes)} indexes on 'recordings' collection:")
    for idx in indexes:
        logger.info(f"  - {idx['name']}: {idx['key']}")
    
    # ============================================
    # STEP 2: Define Required Indexes
    # ============================================
    required_indexes = {
        "start_time_1": {
            "field": "start_time",
            "type": "ascending",
            "reason": "Time-based queries (POST /recordings_in_time_range)"
        },
        "end_time_1": {
            "field": "end_time",
            "type": "ascending",
            "reason": "Range queries for playback"
        },
        "uuid_1": {
            "field": "uuid",
            "type": "ascending",
            "reason": "Unique recording lookups"
        }
    }
    
    # ============================================
    # STEP 3: Verify Each Required Index
    # ============================================
    missing_indexes = []
    
    for idx_name, idx_info in required_indexes.items():
        if idx_name in index_names:
            logger.info(f"✓ Index '{idx_name}' exists")
            logger.info(f"  Purpose: {idx_info['reason']}")
        else:
            missing_indexes.append({
                "name": idx_name,
                "field": idx_info["field"],
                "reason": idx_info["reason"]
            })
            logger.error(f"❌ Missing index: {idx_name}")
            logger.error(f"   Field: {idx_info['field']}")
            logger.error(f"   Impact: {idx_info['reason']} will be SLOW")
    
    # ============================================
    # STEP 4: Assert No Missing Indexes
    # ============================================
    if missing_indexes:
        error_msg = "\n\nCRITICAL: Missing MongoDB indexes detected!\n\n"
        error_msg += "Missing indexes will cause severe performance degradation.\n"
        error_msg += "Users will experience slow queries and timeouts.\n\n"
        error_msg += "Missing indexes:\n"
        
        for idx in missing_indexes:
            error_msg += f"  - {idx['name']} on field '{idx['field']}'\n"
            error_msg += f"    Impact: {idx['reason']}\n"
        
        error_msg += "\nTo fix, run:\n"
        for idx in missing_indexes:
            error_msg += (
                f"  db.recordings.createIndex("
                f"{{\"{idx['field']}\": 1}}, "
                f"{{name: \"{idx['name']}\"}})\n"
            )
        
        pytest.fail(error_msg)
    
    # ============================================
    # STEP 5: Optional - Check Index Statistics
    # ============================================
    logger.info("\n" + "=" * 60)
    logger.info("Checking index usage statistics...")
    
    # Get collection stats
    stats = recordings_collection.database.command("collStats", "recordings")
    
    if "indexSizes" in stats:
        logger.info("\nIndex sizes:")
        for idx_name, size_bytes in stats["indexSizes"].items():
            size_mb = size_bytes / (1024 * 1024)
            logger.info(f"  {idx_name}: {size_mb:.2f} MB")
    
    # ============================================
    # SUCCESS
    # ============================================
    logger.info("\n" + "=" * 60)
    logger.info("MONGODB INDEXES VALIDATION: PASSED ✅")
    logger.info("=" * 60)
    logger.info(f"All {len(required_indexes)} required indexes exist")
    logger.info("Query performance is optimal")
    logger.info("=" * 60)
```

### 🔍 שאלות והתשובות

#### **שאלה: "איך יוצרים את ה-indexes אם הם חסרים?"**
**תשובה**:
```python
# Method 1: MongoDB Shell
db.recordings.createIndex({"start_time": 1}, {name: "start_time_1"})
db.recordings.createIndex({"end_time": 1}, {name: "end_time_1"})
db.recordings.createIndex({"uuid": 1}, {name: "uuid_1", unique: true})

# Method 2: Python (automated setup)
from pymongo import ASCENDING, IndexModel

def setup_indexes(collection):
    indexes = [
        IndexModel([("start_time", ASCENDING)], name="start_time_1"),
        IndexModel([("end_time", ASCENDING)], name="end_time_1"),
        IndexModel([("uuid", ASCENDING)], name="uuid_1", unique=True)
    ]
    collection.create_indexes(indexes)
    logger.info("Indexes created successfully")

# Method 3: CI/CD Pipeline
# → בonboarding של סביבה חדשה, רץ script שיוצר indexes
```

#### **שאלה: "מה ה-overhead של indexes?"**
**תשובה**:
```
Trade-offs:
✅ Pros:
- Queries פי 100-1000 יותר מהירות
- פחות CPU usage
- יותר concurrent users

❌ Cons:
- תופס מקום (כל index ~1-5% מגודל ה-collection)
- Inserts מעט יותר איטיים (צריך לעדכן גם את ה-index)

Bottom Line:
הבenefits גדולים בהרבה מה-cost.
בלי indexes → production unusable.
```

#### **שאלה: "אילו indexes נוספים כדאי לשקול?"**
**תשובה**:
```python
# Compound indexes for common queries
db.recordings.createIndex(
    {"start_time": 1, "end_time": 1},
    {name: "time_range_compound"}
)
# → מהיר יותר לrangeקשתים

# Index on deleted flag
db.recordings.createIndex(
    {"deleted": 1},
    {name: "deleted_1"}
)
# → מהיר לסנן recordings שלא נמחקו

# Partial index (only for non-deleted)
db.recordings.createIndex(
    {"start_time": 1},
    {
        name: "start_time_active",
        partialFilterExpression: {"deleted": false}
    }
)
# → חוסך מקום, רלוונטי רק ל-active recordings
```

---

## טסט #5: PZ-13809 - Verify Required MongoDB Collections Exist

### 🎯 מה המטרה?
**לוודא שכל ה-collections הנדרשים קיימים ב-MongoDB database - בדיקת תשתית בסיסית**.

### 📋 מה בדיוק בודקים?

#### **Required Collections**
```python
REQUIRED_COLLECTIONS = [
    "recordings",   # Main metadata storage
    "node4",        # Node-specific data
    "tasks",        # Task management
    "jobs"          # Job queue
]
```

#### **What Each Collection Does**

| Collection | Purpose | What Breaks If Missing |
|------------|---------|------------------------|
| `recordings` | Stores recording metadata | Cannot query history, playback fails |
| `node4` | Node-specific recording info | Cannot identify recording source |
| `tasks` | Active task tracking | Cannot manage waterfall tasks |
| `jobs` | Job processing queue | Cannot process async jobs |

### 🔴 למה נחיץ?

#### **תרחישי כשל**
```python
# Scenario: Deployment to new environment
# אם לא רץ setup script → collections חסרים

# User tries: POST /recordings_in_time_range
db = client["prisma"]
recordings = db["recordings"]  # Collection doesn't exist!
results = recordings.find(...)  # Returns nothing

# Error: "No recordings found"
# → User thinks system is broken
```

#### **Early Detection**
```
הטסט רץ FIRST בtest suite:
1. אם collections חסרים → טסט נכשל מיד
2. לא מבזבזים זמן על טסטים נוספים
3. ברור מה לתקן
```

### 💻 Implementation

```python
def test_required_collections_exist(
    self,
    mongo_client,
    config_manager,
    logger
):
    """
    Test: Verify Required MongoDB Collections Exist
    
    Purpose: Validate database setup and infrastructure
    
    Priority: CRITICAL
    This test runs FIRST - if it fails, other tests will also fail
    """
    
    # ============================================
    # STEP 1: Connect to Database
    # ============================================
    db_name = config_manager.get("mongodb.database_name")
    db = mongo_client[db_name]
    
    logger.info(f"Connected to database: {db_name}")
    
    # ============================================
    # STEP 2: List All Collections
    # ============================================
    existing_collections = db.list_collection_names()
    
    logger.info(f"Found {len(existing_collections)} collections:")
    for col in existing_collections:
        logger.info(f"  - {col}")
    
    # ============================================
    # STEP 3: Define Required Collections
    # ============================================
    required_collections = {
        "recordings": "Main recording metadata storage",
        "node4": "Node-specific recording information",
        "tasks": "Active task management",
        "jobs": "Asynchronous job processing queue"
    }
    
    # ============================================
    # STEP 4: Check Each Required Collection
    # ============================================
    missing_collections = []
    
    for col_name, purpose in required_collections.items():
        if col_name in existing_collections:
            # Collection exists - verify accessible
            collection = db[col_name]
            
            try:
                count = collection.count_documents({})
                logger.info(f"✓ Collection '{col_name}' exists ({count} documents)")
                logger.info(f"  Purpose: {purpose}")
            except Exception as e:
                logger.error(f"❌ Collection '{col_name}' exists but not accessible: {e}")
                missing_collections.append({
                    "name": col_name,
                    "reason": f"Access error: {e}"
                })
        else:
            logger.error(f"❌ Collection '{col_name}' MISSING")
            logger.error(f"   Purpose: {purpose}")
            missing_collections.append({
                "name": col_name,
                "reason": "Collection does not exist"
            })
    
    # ============================================
    # STEP 5: Assert No Missing Collections
    # ============================================
    if missing_collections:
        error_msg = "\n\nCRITICAL: Required MongoDB collections are missing!\n\n"
        error_msg += "This indicates incomplete database setup.\n"
        error_msg += "Focus Server will NOT function correctly.\n\n"
        error_msg += "Missing collections:\n"
        
        for col in missing_collections:
            error_msg += f"  - {col['name']}: {col['reason']}\n"
        
        error_msg += "\nTo fix:\n"
        error_msg += "1. Run database setup script:\n"
        error_msg += "   python scripts/setup_mongodb.py\n"
        error_msg += "2. Or create collections manually:\n"
        for col in missing_collections:
            error_msg += f"   db.createCollection('{col['name']}')\n"
        
        pytest.fail(error_msg)
    
    # ============================================
    # SUCCESS
    # ============================================
    logger.info("\n" + "=" * 60)
    logger.info("MONGODB COLLECTIONS VALIDATION: PASSED ✅")
    logger.info("=" * 60)
    logger.info(f"All {len(required_collections)} required collections exist")
    logger.info("Database infrastructure is ready")
    logger.info("=" * 60)
```

### 🔍 שאלות והתשובות

#### **שאלה: "האם MongoDB יוצר collections אוטומטית?"**
**תשובה**:
```python
# כן, אבל זה לא רצוי לproduction!

# Auto-creation (implicit):
db = client["prisma"]
recordings = db["recordings"]  # Collection created NOW
recordings.insert_one({"uuid": "test"})  # First insert creates it

# Problem:
# - No schema validation
# - No indexes
# - Wrong settings

# Best Practice (explicit):
db.create_collection(
    "recordings",
    validator={  # Schema validation
        "$jsonSchema": {
            "required": ["uuid", "start_time", "end_time"],
            "properties": {
                "uuid": {"bsonType": "string"},
                "start_time": {"bsonType": ["int", "double"]},
                "end_time": {"bsonType": ["int", "double"]}
            }
        }
    }
)

# Then create indexes:
db.recordings.create_index("start_time")
```

---

## טסט #6: PZ-13705 - Historical vs Live Recordings Classification

### 🎯 מה המטרה?
**לסווג את כל ההקלטות ב-MongoDB לפי lifecycle stage ולזהות בעיות בניהול מחזור חיי הנתונים**.

### 📋 מה בדיוק בודקים?

#### **Recording States**

| State | Criteria | Expected % | What It Means |
|-------|----------|------------|---------------|
| **Historical** | `start_time` exists AND `end_time` exists AND `deleted=False` | ~99% | Completed, available recordings |
| **Live** | `start_time` exists AND `end_time=None` AND `deleted=False` | <1% | Currently recording (recent only) |
| **Deleted** | `deleted=True` | <1% | Marked for cleanup |
| **Stale** | Age >24h AND `end_time=None` AND `deleted=False` | 0% | Crashed recordings (BUG!) |
| **Invalid** | `start_time` missing | 0% | Corrupted data (BUG!) |

#### **Validation Logic**
```python
# Historical
historical = db.recordings.count_documents({
    "start_time": {"$exists": True},
    "end_time": {"$ne": None},
    "deleted": False
})

# Live  
live = db.recordings.count_documents({
    "start_time": {"$exists": True},
    "end_time": None,
    "deleted": False
})

# Deleted
deleted = db.recordings.count_documents({
    "deleted": True
})

# Invalid (should be 0!)
invalid = db.recordings.count_documents({
    "start_time": {"$exists": False}
})

# Stale Detection (should be 0!)
now = time.time()
stale_threshold = now - (24 * 3600)  # 24 hours ago

stale = db.recordings.count_documents({
    "start_time": {"$lt": stale_threshold},
    "end_time": None,
    "deleted": False
})
```

### 🔴 למה נחיץ?

#### **תרחיש 1: Stale Recordings**
```python
# בעיה: recording התחיל לפני 3 ימים, אין end_time, לא deleted

# סיבות אפשריות:
1. Focus Server crashed mid-recording
2. Recording process hung
3. end_time לא נכתב לDB

# השפעה:
- Looks like "Live" but actually dead
- Wastes storage
- Confuses users
- Indicates reliability issue

# הטסט מזהה:
if stale_count > 0:
    logger.warning(f"Found {stale_count} stale recordings!")
    # → אנחנו יודעים שיש בעיה
```

#### **תרחיש 2: Missing Metadata**
```python
# אם יש recordings בלי start_time:

# זה אומר:
- Data corruption
- Bug in recording creation
- Database integrity issue

# הטסט כושל:
assert invalid_count == 0, f"Found {invalid_count} invalid recordings!"
# → חוסם deployment
```

#### **תרחיש 3: Cleanup Service Validation**
```python
# בודקים שCleanup Service עובד:

deleted_with_endtime = db.recordings.count_documents({
    "deleted": True,
    "end_time": {"$ne": None}
})

deleted_without_endtime = db.recordings.count_documents({
    "deleted": True,
    "end_time": None
})

# אם deleted_without_endtime גבוה:
# → Recordings נמחקו בזמן הקלטה (לפני שהסתיימו)
# → זה OK, אבל מעניין לדעת
```

### 💻 Implementation (מקוצר - הקוד מאוד ארוך)

```python
def test_historical_vs_live_recordings(
    self,
    mongo_client,
    config_manager,
    logger
):
    """
    Test: Historical vs Live Recordings Classification
    
    Purpose:
    - Validate recording lifecycle management
    - Detect stale/crashed recordings
    - Verify cleanup service functionality
    - Ensure data integrity
    
    Business Impact:
    - Stale recordings indicate system reliability issues
    - Invalid metadata breaks history playback
    - Proper classification required for data retention policies
    """
    
    db_name = config_manager.get("mongodb.database_name")
    db = mongo_client[db_name]
    recordings = db["recordings"]
    
    # ============================================
    # STEP 1: Count Total Recordings
    # ============================================
    total = recordings.count_documents({})
    logger.info(f"Total recordings in DB: {total}")
    
    assert total > 0, "No recordings found! Database may be empty."
    
    # ============================================
    # STEP 2: Classify by State
    # ============================================
    
    # Historical (completed)
    historical = recordings.count_documents({
        "start_time": {"$exists": True},
        "end_time": {"$ne": None},
        "deleted": False
    })
    
    # Live (in-progress)
    live = recordings.count_documents({
        "start_time": {"$exists": True},
        "end_time": None,
        "deleted": False
    })
    
    # Deleted
    deleted = recordings.count_documents({"deleted": True})
    
    # Invalid (missing start_time)
    invalid = recordings.count_documents({
        "start_time": {"$exists": False}
    })
    
    # ============================================
    # STEP 3: Detect Stale Recordings
    # ============================================
    now = time.time()
    stale_threshold = now - (24 * 3600)
    
    stale = recordings.count_documents({
        "start_time": {"$lt": stale_threshold},
        "end_time": None,
        "deleted": False
    })
    
    # ============================================
    # STEP 4: Calculate Percentages
    # ============================================
    percentages = {
        "historical": (historical / total) * 100,
        "live": (live / total) * 100,
        "deleted": (deleted / total) * 100,
        "invalid": (invalid / total) * 100,
        "stale": (stale / total) * 100
    }
    
    # ============================================
    # STEP 5: Log Classification
    # ============================================
    logger.info("\n" + "=" * 60)
    logger.info("RECORDING CLASSIFICATION RESULTS")
    logger.info("=" * 60)
    logger.info(f"Historical (completed):  {historical:>6} ({percentages['historical']:>5.1f}%)")
    logger.info(f"Live (in-progress):      {live:>6} ({percentages['live']:>5.1f}%)")
    logger.info(f"Deleted (cleanup):       {deleted:>6} ({percentages['deleted']:>5.1f}%)")
    logger.info(f"Invalid (missing data):  {invalid:>6} ({percentages['invalid']:>5.1f}%)")
    logger.info(f"Stale (crashed):         {stale:>6} ({percentages['stale']:>5.1f}%)")
    logger.info("=" * 60)
    
    # ============================================
    # STEP 6: CRITICAL Assertions
    # ============================================
    
    # No invalid recordings allowed
    assert invalid == 0, \
        f"Found {invalid} recordings without start_time! Data corruption detected."
    
    # Classification integrity
    classified_total = historical + live + deleted
    assert classified_total == total, \
        f"Classification mismatch: {classified_total} vs {total}"
    
    # Historical should be majority
    assert percentages["historical"] > 50.0, \
        f"Historical recordings only {percentages['historical']:.1f}% " \
        f"(expected >50%). Indicates cleanup or data loss issues."
    
    # ============================================
    # STEP 7: WARNING Assertions
    # ============================================
    
    if stale > 0:
        logger.warning(
            f"\n⚠️  WARNING: Found {stale} stale recordings!\n"
            f"   These are recordings >24h old without end_time.\n"
            f"   Possible causes:\n"
            f"   - Focus Server crashed during recording\n"
            f"   - Recording process hung\n"
            f"   - Bug in end_time writing logic\n"
        )
        
        # Log samples
        stale_samples = list(recordings.find({
            "start_time": {"$lt": stale_threshold},
            "end_time": None,
            "deleted": False
        }).limit(3))
        
        for rec in stale_samples:
            age_hours = (now - rec["start_time"]) / 3600
            logger.warning(
                f"   Stale: {rec['uuid']} (age: {age_hours:.1f} hours)"
            )
    
    # ============================================
    # STEP 8: Success
    # ============================================
    logger.info("\n" + "=" * 60)
    logger.info("RECORDING LIFECYCLE VALIDATION: PASSED ✅")
    logger.info("=" * 60)
    logger.info(f"✓ No invalid recordings")
    logger.info(f"✓ Classification integrity verified")
    logger.info(f"✓ Historical recordings are majority")
    if stale == 0:
        logger.info(f"✓ No stale recordings detected")
    logger.info("=" * 60)
```

### 🔍 שאלות והתשובות

#### **שאלה: "מה עושים אם מוצאים Stale recordings?"**
**תשובה**:
```python
# Option 1: Mark as deleted
def cleanup_stale_recordings(db, stale_threshold):
    result = db.recordings.update_many(
        {
            "start_time": {"$lt": stale_threshold},
            "end_time": None,
            "deleted": False
        },
        {
            "$set": {"deleted": True, "deletion_reason": "stale"}
        }
    )
    logger.info(f"Marked {result.modified_count} stale recordings as deleted")

# Option 2: Fix end_time (if we can infer it)
def fix_stale_recordings(db):
    stale_recs = db.recordings.find({
        "start_time": {"$exists": True},
        "end_time": None,
        "deleted": False
    })
    
    for rec in stale_recs:
        # Try to infer end_time from file system
        file_path = rec.get("path")
        if file_path and os.path.exists(file_path):
            file_mtime = os.path.getmtime(file_path)
            db.recordings.update_one(
                {"_id": rec["_id"]},
                {"$set": {"end_time": file_mtime}}
            )

# Option 3: Investigate root cause
# → Check Focus Server logs
# → Find crash time
# → Fix underlying bug
```

#### **שאלה: "למה 24 שעות זה ה-threshold ל-Stale?"**
**תשובה**:
```
הגדרת 24 שעות היא heuristic:

- Recordings רגילים: 1-2 שעות
- Long recordings: עד 12 שעות
- אם recording עדיין "Live" אחרי 24h → כנראה crashed

אבל: אפשר להתאים לפי use case:
```python
# For short recordings (minutes)
STALE_THRESHOLD_HOURS = 1

# For long-term monitoring (days)
STALE_THRESHOLD_HOURS = 48

# הטסט צריך להיות configurable:
stale_threshold_hours = config_manager.get(
    "data_quality.stale_threshold_hours",
    default=24
)
```

#### **שאלה: "איך הטסט מטפל ב-deleted recordings בלי end_time?"**
**תשובה**:
```python
# תרחיש: recording נמחק בזמן שעדיין היה Live

# זה LEGITIMATE behavior:
# 1. User starts recording
# 2. Realizes it's wrong
# 3. Deletes it immediately
# 4. Recording never got end_time → OK!

# הטסט לא נכשל על זה:
deleted_without_endtime = db.recordings.count_documents({
    "deleted": True,
    "end_time": None
})

if deleted_without_endtime > 0:
    logger.info(
        f"ℹ️  {deleted_without_endtime} deleted recordings missing end_time.\n"
        f"   This is OK - they were deleted while still recording."
    )
    # → רק INFO, לא WARNING או ERROR
```

---

## טסט #7: PZ-13686 - MongoDB Indexes Validation

### 🎯 מה המטרה?
**לוודא שיש indexes אופטימליים על `node4` collection למניעת performance degradation**.

### 📋 מה בדיוק בודקים?

#### **Expected Indexes on node4**
```python
EXPECTED_INDEXES_NODE4 = {
    "start_time_1": {
        "field": "start_time",
        "type": "ascending",
        "critical": True
    },
    "end_time_1": {
        "field": "end_time", 
        "type": "ascending",
        "critical": True
    },
    "uuid_1": {
        "field": "uuid",
        "type": "ascending",
        "unique": True,
        "critical": True
    },
    "deleted_1": {
        "field": "deleted",
        "type": "ascending",
        "critical": False  # Nice to have
    }
}
```

### 🔴 למה נחיץ?

#### **Performance Impact Without Indexes**
```python
# Query: Find all recordings in time range
recordings = node4.find({
    "start_time": {"$gte": start},
    "end_time": {"$lte": end},
    "deleted": False
})

# WITHOUT indexes:
# - Full collection scan: O(n)
# - For 10,000 recordings: ~5000ms
# - MongoDB CPU: 80%+
# - Multiple concurrent users: timeout

# WITH indexes:
# - Index scan: O(log n)
# - For 10,000 recordings: ~50ms
# - MongoDB CPU: <5%
# - Scales to 100+ concurrent users
```

### 💻 Implementation

```python
def test_mongodb_indexes_exist_and_optimal(
    self,
    mongo_client,
    config_manager,
    logger
):
    """
    Test: MongoDB Indexes Validation on node4
    
    Purpose: Ensure critical indexes exist for efficient queries
    
    Critical Queries That Need Indexes:
    1. Time-based lookups (history playback)
    2. UUID lookups (recording retrieval)
    3. Deleted flag filtering (active recordings only)
    """
    
    db_name = config_manager.get("mongodb.database_name")
    db = mongo_client[db_name]
    node4 = db["node4"]
    
    # ============================================
    # STEP 1: List Current Indexes
    # ============================================
    indexes = list(node4.list_indexes())
    index_details = {}
    
    for idx in indexes:
        index_details[idx['name']] = {
            "key": idx['key'],
            "unique": idx.get('unique', False)
        }
    
    logger.info(f"Found {len(indexes)} indexes on node4:")
    for name, details in index_details.items():
        unique_marker = " [UNIQUE]" if details['unique'] else ""
        logger.info(f"  - {name}: {details['key']}{unique_marker}")
    
    # ============================================
    # STEP 2: Verify Required Indexes
    # ============================================
    required_indexes = ["start_time_1", "end_time_1", "uuid_1"]
    missing = []
    
    for idx_name in required_indexes:
        if idx_name not in index_details:
            missing.append(idx_name)
            logger.error(f"❌ Missing critical index: {idx_name}")
        else:
            logger.info(f"✓ Index {idx_name} exists")
    
    # ============================================
    # STEP 3: Verify UUID is Unique
    # ============================================
    if "uuid_1" in index_details:
        if index_details["uuid_1"]["unique"]:
            logger.info("✓ UUID index is UNIQUE (prevents duplicates)")
        else:
            logger.warning("⚠️  UUID index exists but is NOT unique!")
            logger.warning("   Recommendation: Recreate as unique index")
    
    # ============================================
    # STEP 4: Performance Analysis (Optional)
    # ============================================
    logger.info("\nPerformance Analysis:")
    
    # Estimate index efficiency
    total_docs = node4.count_documents({})
    logger.info(f"Total documents in node4: {total_docs}")
    
    if total_docs > 1000:
        # Large collection - indexes are CRITICAL
        if missing:
            logger.error(
                f"🚨 CRITICAL: {len(missing)} indexes missing on "
                f"large collection ({total_docs} docs)!"
            )
            logger.error("   Queries will be VERY slow!")
    
    # ============================================
    # ASSERTIONS
    # ============================================
    assert not missing, \
        f"Missing critical indexes on node4: {', '.join(missing)}\n" \
        f"This will cause severe performance degradation.\n" \
        f"Create indexes with:\n" + \
        "\n".join(f"  db.node4.createIndex({{\"{idx.replace('_1', '')}\": 1}})" 
                  for idx in missing)
    
    logger.info("\n" + "=" * 60)
    logger.info("NODE4 INDEXES VALIDATION: PASSED ✅")
    logger.info("=" * 60)
```

### 🔍 שאלות והתשובות

#### **שאלה: "מה ההבדל בין index על `recordings` ו-`node4`?"**
**תשובה**:
```
שני collections, אותם indexes:

recordings collection:
- Main metadata store
- Used by API: POST /recordings_in_time_range
- Needs: start_time, end_time, uuid indexes

node4 collection:
- Node-specific recording data
- Used by: Baby Analyzer, recording lookup by node
- Needs: same indexes + node-specific fields

למה שני collections?
- Separation of concerns
- Different access patterns
- node4 might have additional node-specific fields
```

#### **שאלה: "איך מודדים את ה-performance impact של indexes?"**
**תשובה**:
```python
# Test WITHOUT index (controlled test only!)
import time

# Measure query time
start = time.time()
results = collection.find({"start_time": {"$gte": threshold}})
list(results)  # Force execution
duration_no_index = time.time() - start

# Create index
collection.create_index("start_time")

# Measure again
start = time.time()
results = collection.find({"start_time": {"$gte": threshold}})
list(results)
duration_with_index = time.time() - start

speedup = duration_no_index / duration_with_index
logger.info(f"Speedup with index: {speedup}x faster")

# Typical results:
# - Small collection (100 docs): 2-5x faster
# - Medium collection (1000 docs): 10-50x faster
# - Large collection (10000+ docs): 100-1000x faster
```

---

## טסט #8: PZ-13685 - Recordings Metadata Completeness

### 🎯 מה המטרה?
**לוודא שכל recording ב-`node4` יש metadata מלא - בדיקה מקבילה ל-PZ-13812 אבל על `node4`**.

### 📋 מה בדיוק בודקים?

```python
# Sample recordings from node4
sample = list(node4.find().limit(100))

for recording in sample:
    # Required fields
    assert "uuid" in recording and recording["uuid"]
    assert "start_time" in recording and recording["start_time"] > 0
    assert "end_time" in recording and recording["end_time"] > 0
    assert "deleted" in recording and isinstance(recording["deleted"], bool)
    
    # Logical validation
    assert recording["start_time"] < recording["end_time"]
```

### 🔴 למה נחיץ?
**זהה ל-PZ-13812 אבל על `node4` collection**. אם יש בעיות metadata ב-node4:
- Baby Analyzer לא יוכל למצוא recordings
- Node-specific queries יכשלו
- Recording attribution (איזה node הקליט) תיעלם

### 💻 Implementation

```python
def test_recordings_have_all_required_metadata(
    self,
    mongo_client,
    config_manager,
    logger
):
    """
    Test: Recordings Metadata Completeness on node4
    
    Similar to PZ-13812 but validates node4 collection
    """
    
    db_name = config_manager.get("mongodb.database_name")
    db = mongo_client[db_name]
    node4 = db["node4"]
    
    SAMPLE_SIZE = 100
    sample = list(node4.find().limit(SAMPLE_SIZE))
    
    assert len(sample) >= 10, \
        f"Insufficient data in node4: {len(sample)} documents"
    
    logger.info(f"Validating {len(sample)} recordings from node4...")
    
    required_fields = ["uuid", "start_time", "end_time", "deleted"]
    missing_metadata_count = 0
    
    for idx, rec in enumerate(sample, 1):
        for field in required_fields:
            if field not in rec or rec[field] is None:
                missing_metadata_count += 1
                logger.error(
                    f"Recording {idx}: Missing or null field '{field}'"
                )
        
        # Time validation
        if "start_time" in rec and "end_time" in rec:
            if rec["start_time"] >= rec["end_time"]:
                missing_metadata_count += 1
                logger.error(
                    f"Recording {idx}: Invalid time range "
                    f"(start >= end)"
                )
    
    assert missing_metadata_count == 0, \
        f"Found {missing_metadata_count} metadata issues in node4"
    
    logger.info("✅ All recordings in node4 have complete metadata")
```

---

## טסט #9: PZ-13684 - node4 Schema Validation

### 🎯 מה המטרה?
**לוודא שה-schema של documents ב-`node4` תקין - parallel ל-PZ-13811**.

### 📋 מה בודקים?

```python
EXPECTED_SCHEMA_NODE4 = {
    "uuid": str,
    "start_time": (int, float),
    "end_time": (int, float),
    "deleted": bool,
    "path": str,  # Optional
    "node": str   # Optional - node identifier
}
```

### 💻 Implementation

```python
def test_node4_schema_validation(
    self,
    mongo_client,
    config_manager,
    logger
):
    """
    Test: node4 Schema Validation
    
    Validates document structure and field types in node4 collection
    """
    
    db_name = config_manager.get("mongodb.database_name")
    db = mongo_client[db_name]
    node4 = db["node4"]
    
    # Sample documents
    sample_size = min(100, node4.count_documents({}))
    sample = list(node4.find().limit(sample_size))
    
    assert len(sample) > 0, "node4 collection is empty"
    
    logger.info(f"Validating schema for {len(sample)} documents...")
    
    schema_errors = []
    
    for idx, doc in enumerate(sample, 1):
        # uuid
        if "uuid" not in doc:
            schema_errors.append(f"Doc {idx}: Missing 'uuid'")
        elif not isinstance(doc["uuid"], str):
            schema_errors.append(
                f"Doc {idx}: 'uuid' is {type(doc['uuid'])}, expected str"
            )
        
        # start_time
        if "start_time" in doc:
            if not isinstance(doc["start_time"], (int, float)):
                schema_errors.append(
                    f"Doc {idx}: 'start_time' is {type(doc['start_time'])}"
                )
        
        # end_time
        if "end_time" in doc:
            if not isinstance(doc["end_time"], (int, float)):
                schema_errors.append(
                    f"Doc {idx}: 'end_time' is {type(doc['end_time'])}"
                )
        
        # deleted
        if "deleted" in doc:
            if not isinstance(doc["deleted"], bool):
                schema_errors.append(
                    f"Doc {idx}: 'deleted' should be bool, "
                    f"got {type(doc['deleted'])}"
                )
    
    if schema_errors:
        error_msg = "\n".join(schema_errors)
        pytest.fail(f"Schema validation failed:\n{error_msg}")
    
    logger.info("✅ node4 schema validation passed")
```

---

## טסט #10: PZ-13683 - MongoDB Collections Exist

### 🎯 מה המטרה?
**בדיקת תשתית - לוודא ש-collections בסיסיים קיימים (זהה ל-PZ-13809 אבל עם רשימה אחרת)**.

### 📋 מה בודקים?

```python
REQUIRED_COLLECTIONS = [
    "base_paths",   # GUID mapping
    "node2",        # Node 2 data
    "node4"         # Node 4 data (main)
]
```

### 💻 Implementation

```python
def test_required_collections_exist(
    self,
    mongo_client,
    config_manager,
    logger
):
    """
    Test: MongoDB Collections Exist (base_paths, node2, node4)
    """
    
    db_name = config_manager.get("mongodb.database_name")
    db = mongo_client[db_name]
    
    existing = db.list_collection_names()
    
    required = ["base_paths", "node2", "node4"]
    missing = [col for col in required if col not in existing]
    
    if missing:
        pytest.fail(
            f"Missing collections: {', '.join(missing)}\n"
            f"Database setup incomplete!"
        )
    
    logger.info(f"✅ All required collections exist: {', '.join(required)}")
```

---

## טסט #11: PZ-13599 - Postgres Connectivity and Catalogs

### 🎯 מה המטרה?
**לוודא שאפשר להתחבר ל-PostgreSQL ושכל system catalogs נגישים**.

### 📋 מה בודקים?

#### **1. Basic Connectivity**
```python
import psycopg2

# Test connection
conn = psycopg2.connect(
    host=config["postgres"]["host"],
    port=config["postgres"]["port"],
    dbname=config["postgres"]["database"],
    user=config["postgres"]["username"],
    password=config["postgres"]["password"]
)

# Test simple query
cursor = conn.cursor()
cursor.execute("SELECT 1")
result = cursor.fetchone()
assert result == (1,), "Basic query failed"
```

#### **2. System Catalogs Accessibility**
```python
# Required system tables/views for monitoring
REQUIRED_CATALOGS = [
    "pg_stat_activity",    # Active connections monitoring
    "pg_database",         # Database list
    "pg_namespace",        # Schema list
    "pg_tables"            # Table list
]

for catalog in REQUIRED_CATALOGS:
    cursor.execute(f"SELECT COUNT(*) FROM {catalog}")
    count = cursor.fetchone()[0]
    logger.info(f"✓ Catalog '{catalog}' accessible ({count} rows)")
```

### 🔴 למה נחיץ?

#### **תרחיש: PostgreSQL Monitoring**
```python
# בלי גישה ל-pg_stat_activity:
# → Cannot monitor active connections
# → Cannot detect long-running queries
# → Cannot kill problematic queries

# בלי גישה ל-pg_database:
# → Cannot list databases
# → Cannot check DB sizes
# → Cannot validate DB exists before connecting
```

### 💻 Implementation

```python
import pytest
import psycopg2

class TestPostgresConnectivity:
    """
    Test Suite: PostgreSQL Infrastructure
    """
    
    @pytest.fixture
    def postgres_connection(self, config_manager):
        """
        Establish PostgreSQL connection.
        """
        pg_config = config_manager.get_postgres_config()
        
        conn = psycopg2.connect(
            host=pg_config["host"],
            port=pg_config["port"],
            dbname=pg_config["database"],
            user=pg_config["username"],
            password=pg_config["password"],
            connect_timeout=5
        )
        
        yield conn
        
        conn.close()
    
    def test_postgres_connectivity_and_catalogs(
        self,
        postgres_connection,
        logger
    ):
        """
        Test: Postgres Connectivity and Catalogs
        
        Purpose: Validate DB connectivity and system catalog accessibility
        
        Steps:
        1. Test basic connectivity (SELECT 1)
        2. Verify access to pg_stat_activity
        3. Verify access to pg_database
        4. Verify access to pg_namespace
        
        Expected: All checks pass, no permission errors
        """
        
        cursor = postgres_connection.cursor()
        
        # ============================================
        # STEP 1: Basic Connectivity
        # ============================================
        logger.info("Testing basic PostgreSQL connectivity...")
        
        cursor.execute("SELECT 1 AS test")
        result = cursor.fetchone()
        
        assert result == (1,), \
            f"Basic query failed: expected (1,), got {result}"
        
        logger.info("✓ Basic connectivity OK")
        
        # ============================================
        # STEP 2: Test System Catalogs
        # ============================================
        required_catalogs = {
            "pg_stat_activity": "Monitor active connections",
            "pg_database": "List databases",
            "pg_namespace": "List schemas",
            "pg_tables": "List tables"
        }
        
        logger.info("\nVerifying system catalog access:")
        
        for catalog, purpose in required_catalogs.items():
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {catalog}")
                count = cursor.fetchone()[0]
                
                logger.info(f"✓ {catalog}: {count} rows ({purpose})")
            
            except psycopg2.Error as e:
                pytest.fail(
                    f"Cannot access system catalog '{catalog}'\n"
                    f"Purpose: {purpose}\n"
                    f"Error: {e}\n"
                    f"This indicates insufficient permissions."
                )
        
        # ============================================
        # STEP 3: Database Version Check
        # ============================================
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        logger.info(f"\nPostgreSQL version: {version}")
        
        # ============================================
        # STEP 4: Active Connections Check
        # ============================================
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pg_stat_activity 
            WHERE state = 'active'
        """)
        active_conns = cursor.fetchone()[0]
        logger.info(f"Active connections: {active_conns}")
        
        # ============================================
        # SUCCESS
        # ============================================
        logger.info("\n" + "=" * 60)
        logger.info("POSTGRES CONNECTIVITY TEST: PASSED ✅")
        logger.info("=" * 60)
        logger.info("✓ Database connectivity verified")
        logger.info("✓ All system catalogs accessible")
        logger.info("✓ Permissions sufficient for monitoring")
        logger.info("=" * 60)
```

### 🔍 שאלות והתשובות

#### **שאלה: "למה צריך PostgreSQL בכלל? לא רק MongoDB?"**
**תשובה**:
```
ארכיטקטורת Focus Server:

MongoDB:
- Recording metadata (fast queries)
- Time-series indexing
- Document storage

PostgreSQL:
- Relational data (users, settings, configs)
- Transactions (ACID compliance)
- Complex queries with JOINs
- Reports and analytics

שניהם משלימים:
- MongoDB → fast reads, simple queries
- PostgreSQL → complex logic, consistency
```

#### **שאלה: "מה אם אין הרשאות ל-pg_stat_activity?"**
**תשובה**:
```sql
-- הבעיה: User doesn't have permissions

-- Fix 1: Grant permissions
GRANT SELECT ON pg_stat_activity TO focus_user;

-- Fix 2: Use restricted view
CREATE VIEW focus_stat_activity AS
SELECT pid, usename, application_name, state, query
FROM pg_stat_activity
WHERE usename = current_user;

GRANT SELECT ON focus_stat_activity TO focus_user;

-- הטסט צריך להתאים:
try:
    cursor.execute("SELECT COUNT(*) FROM pg_stat_activity")
except psycopg2.ProgrammingError:
    # Try restricted view
    cursor.execute("SELECT COUNT(*) FROM focus_stat_activity")
```

---

## טסט #12: PZ-13598 - Mongo Collections and Schema (Parent Test)

### 🎯 מה המטרה?
**טסט-על (parent) שמריץ מספר sub-tests לוולידציה מקיפה של MongoDB**.

### 📋 מה בודקים?

```python
# This is a TEST SUITE, not a single test
class TestMongoDBDataQuality:
    """
    Parent Test Suite: MongoDB Data Quality
    
    Sub-tests:
    1. Collections exist
    2. Schema validation (node4)
    3. Metadata completeness
    4. Indexes validation
    5. Soft delete implementation
    """
    
    def test_required_collections_exist(self):
        # PZ-13809
        pass
    
    def test_node4_schema_validation(self):
        # PZ-13811
        pass
    
    def test_recordings_have_all_required_metadata(self):
        # PZ-13812
        pass
    
    def test_mongodb_indexes_exist_and_optimal(self):
        # PZ-13810
        pass
```

### 🔴 למה נחיץ?
**זה ה-umbrella test שמאגד את כל בדיקות ה-MongoDB quality**.

### 💻 Implementation

```python
import pytest

@pytest.mark.mongodb
@pytest.mark.data_quality
class TestMongoDBDataQuality:
    """
    Test Suite: MongoDB Data Quality (PZ-13598)
    
    Purpose: Comprehensive MongoDB validation covering:
    - Infrastructure (collections, indexes)
    - Schema integrity (field types, structure)
    - Data quality (completeness, validity)
    - Soft delete implementation
    
    This is the parent test that groups all MongoDB quality tests.
    
    Run all MongoDB tests:
        pytest -m mongodb -v
    
    Run only this suite:
        pytest tests/integration/infrastructure/test_mongodb_data_quality.py -v
    """
    
    def test_mongodb_connection(self, mongo_client, logger):
        """
        Prerequisite: Verify MongoDB is accessible
        """
        # Test connection
        mongo_client.admin.command('ping')
        logger.info("✅ MongoDB connection successful")
    
    def test_required_collections_exist(self, ...):
        """Sub-test: PZ-13809"""
        # Implementation from PZ-13809
        pass
    
    def test_node4_schema_validation(self, ...):
        """Sub-test: PZ-13811"""
        # Implementation from PZ-13811
        pass
    
    def test_recordings_have_all_required_metadata(self, ...):
        """Sub-test: PZ-13812"""
        # Implementation from PZ-13812
        pass
    
    def test_mongodb_indexes_exist_and_optimal(self, ...):
        """Sub-test: PZ-13810"""
        # Implementation from PZ-13810
        pass
    
    def test_soft_delete_implementation(self, ...):
        """
        Additional Test: Soft Delete Logic
        
        Verify:
        - Deleted flag exists and is boolean
        - Deleted recordings are excluded from queries
        - Cleanup service marks recordings correctly
        """
        # Implementation...
        pass
    
    def test_detect_illegal_inserts(self, ...):
        """
        Additional Test: Schema Enforcement
        
        Try to insert invalid data and verify it's rejected
        """
        # Implementation...
        pass
```

### 🔍 שאלות והתשובות

#### **שאלה: "למה צריך parent test? למה לא רק individual tests?"**
**תשובה**:
```
ארגון היררכי:

PZ-13598 (Parent)
  ├─ PZ-13809: Collections Exist
  ├─ PZ-13810: Indexes Exist
  ├─ PZ-13811: Schema Validation
  └─ PZ-13812: Metadata Completeness

יתרונות:
1. ריצה מאורגנת: pytest -m mongodb
2. תיעוד ברור: כל הבדיקות במקום אחד
3. Shared fixtures: כולם משתמשים באותו mongo_client
4. Progress tracking: "5/5 MongoDB tests passed"
```

#### **שאלה: "איך מריצים רק קבוצה אחת של טסטים?"**
**תשובה**:
```bash
# Run all MongoDB tests
pytest -m mongodb -v

# Run only infrastructure tests (collections, indexes)
pytest -m "mongodb and infrastructure" -v

# Run only data quality tests (schema, metadata)
pytest -m "mongodb and data_quality" -v

# Run specific test file
pytest tests/integration/infrastructure/test_mongodb_data_quality.py -v

# Run specific test
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_node4_schema_validation -v

# Run with detailed output
pytest -m mongodb -v -s --log-cli-level=INFO
```

---

## טסט #13: Data Quality - Additional Tests Summary

הטסטים שלא פורטו בפירוט מלא (כי הם דומים מאוד לקודמים):

### PZ-13684: node4 Schema Validation
- **זהה ל-PZ-13811** אבל על `node4` במקום `recordings`
- בודק שכל document יש שדות נכונים מהטיפוס הנכון

### PZ-13685: Recordings Metadata Completeness  
- **זהה ל-PZ-13812** אבל על `node4`
- בודק שאין null או ערכים ריקים

### PZ-13686: MongoDB Indexes Validation
- **זהה ל-PZ-13810** אבל מתמקד ב-`node4` indexes
- בודק start_time, end_time, uuid indexes

### PZ-13683: MongoDB Collections Exist
- **variant של PZ-13809** עם רשימת collections אחרת
- בודק: base_paths, node2, node4

---

## 📚 סיכום והמלצות לפגישה

### טיפים לפגישה

#### 1. **הכנה מנטלית**
```
לפני הפגישה:
✅ קרא את התקציר של כל טסט (3-4 משפטים)
✅ הבן את הקטגוריות (MongoDB infra, Data quality, etc.)
✅ תדע להסביר "למה" כל טסט חשוב
```

#### 2. **שאלות נפוצות שיישאלו**
```
Q: "איזה טסטים הכי קריטיים?"
A: "PZ-13809 (Collections Exist) ו-PZ-13867 (Data Integrity) 
    כי בלעדיהם כלום לא יעבוד."

Q: "כמה זמן לרוץ את כל הטסטים?"
A: "5-7 דקות total. MongoDB tests מהירים (seconds),
    Historic playback tests יותר ארוכים (1-2 min כל אחד)."

Q: "מה אם טסט נכשל בproduction?"
A: "יש severity levels:
    - CRITICAL = block deployment
    - WARNING = alert team, don't block
    - INFO = log for analysis"
```

#### 3. **הצג ערך עסקי**
```
כל טסט ענה על:
1. מה זה מונע? (bugs, downtime, data loss)
2. מה זה חוסך? (debug time, support tickets)
3. מה זה משפר? (reliability, user trust)
```

---

## 📊 טבלת סיכום מהיר - כל הטסטים

| # | Jira ID | שם הטסט | קטגוריה | Priority | זמן ריצה | Automation Status |
|---|---------|---------|----------|----------|----------|-------------------|
| 1 | PZ-13867 | Historic Playback Data Integrity | Data Quality | High | ~2 min | ✅ Automated |
| 2 | PZ-13812 | Recordings Complete Metadata | MongoDB | Medium | ~10 sec | ✅ Automated |
| 3 | PZ-13811 | Recordings Schema Validation | MongoDB | High | ~5 sec | ✅ Automated |
| 4 | PZ-13810 | Critical Indexes Exist | MongoDB | Medium | ~3 sec | ✅ Automated |
| 5 | PZ-13809 | Required Collections Exist | MongoDB | Medium | ~2 sec | ✅ Automated |
| 6 | PZ-13705 | Historical vs Live Classification | Data Lifecycle | Medium | ~15 sec | ✅ Automated |
| 7 | PZ-13686 | node4 Indexes Validation | MongoDB | Medium | ~3 sec | ✅ Automated |
| 8 | PZ-13685 | node4 Metadata Completeness | MongoDB | Medium | ~10 sec | ✅ Automated |
| 9 | PZ-13684 | node4 Schema Validation | MongoDB | Medium | ~5 sec | ✅ Automated |
| 10 | PZ-13683 | Collections Exist (base_paths/nodes) | MongoDB | Medium | ~2 sec | ✅ Automated |
| 11 | PZ-13599 | Postgres Connectivity | PostgreSQL | Medium | ~5 sec | ✅ Automated |
| 12 | PZ-13598 | Mongo Collections and Schema (Parent) | MongoDB | Medium | ~30 sec | ✅ Automated |
| 13 | - | Additional Tests Summary | Various | - | - | - |

**סה"כ זמן ריצה**: ~5-7 דקות  
**סה"כ טסטים אוטומטיים**: 12 (100%)

---

## 🎯 מפת דרכים - איך להציג בפגישה

### **פתיחה (2 דקות)**
```
"יש לנו 13 טסטים שמכסים את כל מחזור החיים של הנתונים:
- Infrastructure (collections, indexes, connectivity)
- Data Quality (schema, metadata, integrity)
- Lifecycle Management (historical, live, deleted)

כל הטסטים אוטומטיים ורצים ב-CI/CD."
```

### **חלוקה לפי קטגוריות (הצג כך)**

#### **קטגוריה 1: MongoDB Infrastructure (קריטי!)**
```
טסטים שבלעדיהם המערכת לא תעבוד:

✅ PZ-13809/13683: Collections Exist
   → בודק ש-recordings, node4, tasks, jobs קיימים
   → אם חסרים → Focus Server crashes

✅ PZ-13810/13686: Indexes Exist
   → בודק indexes על start_time, end_time, uuid
   → אם חסרים → Queries slow (5 sec → timeout)
   → ביצועים פי 100-1000 יותר טובים עם indexes

✅ PZ-13598: Parent Test
   → מריץ את כל בדיקות ה-infrastructure ביחד
```

#### **קטגוריה 2: Schema & Type Safety**
```
טסטים שמונעים runtime errors:

✅ PZ-13811/13684: Schema Validation
   → בודק שכל field הוא מהטיפוס הנכון
   → אם start_time הוא string → TypeError!
   → מונע schema drift

✅ PZ-13812/13685: Metadata Completeness
   → בודק שאין null או ערכים ריקים
   → אם uuid ריק → data corruption
   → אם path חסר → cannot load recording
```

#### **קטגוריה 3: Data Integrity & Quality**
```
טסטים שמבטיחים נתונים תקינים:

✅ PZ-13867: Historic Playback Data Integrity
   → בודק שכל row בplayback תקין:
     - Timestamps מסודרים כרונולוגית
     - אין נתונים חסרים
     - sensor data complete
   → אם נכשל → UI crashes, wrong timeline

✅ PZ-13705: Historical vs Live Classification
   → מסווג recordings: Historical, Live, Deleted, Stale
   → מזהה crashed recordings (>24h without end_time)
   → מוודא cleanup service עובד
```

#### **קטגוריה 4: PostgreSQL Infrastructure**
```
✅ PZ-13599: Postgres Connectivity
   → בודק connection + system catalogs
   → נדרש למעקב אחר connections
   → נדרש לניהול transactions
```

---

## 💡 תשובות מוכנות לשאלות קשות

### **שאלה: "למה יש כפילויות? PZ-13810 ו-PZ-13686 שניהם בודקים indexes!"**
**תשובה מצוינת**:
```
נכון! יש דמיון אבל על collections שונים:

PZ-13810: Indexes on recordings collection
- מיועד ל-API calls (POST /recordings_in_time_range)
- משמש את ה-UI וה-REST API

PZ-13686: Indexes on node4 collection
- מיועד ל-Baby Analyzer queries
- משמש לזיהוי recordings לפי node

למה שני collections?
- Separation of concerns
- Different access patterns
- node4 יכול להכיל metadata נוסף specific לnode

אפשר לאחד? כן, אבל זה architectural decision.
```

### **שאלה: "איך אתה בוחר מה priority - High vs Medium?"**
**תשובה מצוינת**:
```
יש לי methodology:

CRITICAL (block production):
- Cannot function without (Collections, Indexes)
- Data corruption risk (Schema validation)

HIGH:
- User-facing impact (Historic playback integrity)
- Performance degradation (Missing indexes)

MEDIUM:
- Operational concerns (Metadata completeness)
- Monitoring & observability (Postgres connectivity)

LOW:
- Nice to have
- Optional features

בפועל, אני מריץ את כולם בCI/CD,
אבל priority קובע:
- CRITICAL → FAIL build
- HIGH → WARN + require approval
- MEDIUM → LOG + continue
```

### **שאלה: "מה תעשה אם יש לך 100 טסטים? איך תנהל?"**
**תשובה מצוינת**:
```
ארגון היררכי עם pytest marks:

@pytest.mark.critical
@pytest.mark.mongodb
@pytest.mark.infrastructure
def test_collections_exist():
    ...

ריצה חכמה:
# Before deployment
pytest -m critical -v  # Only critical tests (fast)

# Nightly CI/CD
pytest -m "mongodb or postgres" -v  # All DB tests

# Full regression
pytest -v  # Everything

# Specific category
pytest -m "data_quality and high" -v

פרלול:
pytest -n 8  # Run 8 tests in parallel (pytest-xdist)

אסטרטגיה:
- Critical tests: <30 seconds total
- Full suite: <10 minutes total
- If > 10 min → optimize or parallelize
```

### **שאלה: "מה אם טסט נכשל בproduction?"**
**תשובה מצוינת**:
```
יש לי action plan:

STEP 1: Severity Assessment
- CRITICAL failure → rollback deployment
- HIGH failure → investigate immediately
- MEDIUM failure → log + monitor

STEP 2: Root Cause Analysis
# הטסט כתוב כך שהוא נותן context:
AssertionError: Missing index 'start_time_1' on node4
  Impact: Queries will be slow (O(n) instead of O(log n))
  Fix: db.node4.createIndex({"start_time": 1})

→ ברור מה הבעיה ומה הפתרון!

STEP 3: Hotfix
- אם אפשר לתקן במהירות (missing index) → fix
- אם bug בקוד → rollback + fix in dev

STEP 4: Prevent Recurrence
- הוסף טסט לCI/CD אם חסר
- Document the issue
- Add to monitoring/alerts
```

---

## 📋 Checklist לפגישה

### **לפני הפגישה**
- [ ] קרא את הסיכום של כל 13 טסטים (עמוד הראשון)
- [ ] הכן 3 דוגמאות קוד (1 MongoDB, 1 Data Integrity, 1 Postgres)
- [ ] תרגל הסבר אחד בקול רם (בחר PZ-13867 או PZ-13705)
- [ ] הכן laptop עם הקוד פתוח (להראות implementation אם יבקשו)

### **במהלך הפגישה**
- [ ] התחל עם overview (2 דקות)
- [ ] הצג טבלת סיכום (visual)
- [ ] צלול לדוגמה מפורטת אחת (5 דקות)
- [ ] ענה על שאלות עם קוד + הסבר (לא רק תיאוריה)
- [ ] תמיד קשר ל-business value (למה זה חשוב ללקוח?)

### **אחרי הפגישה**
- [ ] שלח את המסמך הזה כסיכום
- [ ] רשום שאלות שלא ידעת לענות עליהן
- [ ] עדכן את המסמך לפי feedback
- [ ] הוסף טסטים נוספים אם הציעו

---

## 🎓 Key Takeaways - מסרים מרכזיים

### **1. Coverage (כיסוי מקיף)**
```
✅ Infrastructure: Collections, Indexes, Connectivity
✅ Schema: Field types, Document structure
✅ Data Quality: Completeness, Integrity
✅ Lifecycle: Historical, Live, Deleted classification
✅ Performance: Index validation, Query optimization
```

### **2. Automation (אוטומציה מלאה)**
```
✅ 100% automated tests
✅ Integrated in CI/CD pipeline
✅ Fast execution (5-7 minutes total)
✅ Clear error messages with fix suggestions
✅ Pytest markers for selective execution
```

### **3. Business Value (ערך עסקי)**
```
✅ Prevents production incidents (data corruption, crashes)
✅ Ensures performance (indexes = 100x faster queries)
✅ Enables forensics (historical data integrity)
✅ Reduces debug time (clear assertions + logging)
✅ Builds customer trust (reliable system)
```

### **4. Best Practices (שיטות עבודה מומלצות)**
```
✅ Production-grade code (PEP8, type hints, docstrings)
✅ Comprehensive assertions (not just status codes)
✅ Detailed logging (context for debugging)
✅ Fixtures for reusability (DRY principle)
✅ Clear test naming (descriptive, purposeful)
```

---

## 📞 איש קשר ומשאבים

### **קבצים רלוונטיים**
```
tests/integration/api/test_historic_playback_flow.py
tests/integration/infrastructure/test_mongodb_data_quality.py
tests/integration/infrastructure/test_postgres_connectivity.py
config/environments.yaml
```

### **פקודות שימושיות**
```bash
# Run all tests
pytest -v

# Run MongoDB tests only
pytest -m mongodb -v

# Run critical tests only
pytest -m critical -v

# Run specific test
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_required_collections_exist -v

# Run with detailed logging
pytest -v -s --log-cli-level=INFO

# Generate HTML report
pytest --html=report.html --self-contained-html
```

### **Monitoring & Alerts**
```python
# אם טסט נכשל בCI/CD:
1. Check pytest output for exact error
2. Look at assertion message (contains fix suggestion)
3. Check logs in artifacts
4. If infrastructure issue → check MongoDB/Postgres status
5. If data issue → check recent deployments/migrations
```

---

## 🏆 סיכום סופי

**אתה מכוסה לחלוטין לפגישה!**

יש לך:
- ✅ **ניתוח מפורט** של כל 13 טסטים
- ✅ **תשובות מוכנות** לכל שאלה אפשרית
- ✅ **קוד לדוגמה** ליישום
- ✅ **הסברים עסקיים** למה כל טסט נחיץ
- ✅ **אסטרטגיות** לניהול טסטים
- ✅ **Troubleshooting guides** לכשלים

**המפתח להצלחה**:
1. **הבן את ה-"למה"** - לא רק ה-"מה"
2. **דבר בשפה עסקית** - לא רק טכנית
3. **הראה קוד** - אל תסתפק בהסברים
4. **תן דוגמאות** - מתרחישים אמיתיים
5. **היה ביטחון** - אתה מכיר את החומר!

---

**בהצלחה בפגישה! 🚀**

*המסמך הזה נוצר במיוחד עבורך ומכסה כל פרט קטן.*  
*אם יש שאלות נוספות לפני הפגישה - תגיד!*


