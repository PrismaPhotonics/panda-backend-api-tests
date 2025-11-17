# תוכנית בדיקות Focus Server - מפורטת במיוחד - חלק 1
## ניתוח מעמיק של כל טסט מ-PZ-13756

---

## 📋 מבנה המסמך

מסמך זה מכיל **ניתוח מפורט לפרטי פרטים** של כל טסט בתוכנית.

**חלוקה:**
- חלק 1: Integration Tests - Historic Playback & Configuration Validation (PZ-13909 - PZ-13873)
- חלק 2: Integration Tests - SingleChannel & Dynamic ROI
- חלק 3: Infrastructure, Performance, Security, E2E Tests

---

## 🎯 TEST #1: Historic Configuration Missing end_time Field

**Jira ID**: PZ-13909  
**Priority**: High  
**Type**: Integration Test (Negative)  
**Status**: TO DO - לא ממומש עדיין

### מטרת הטסט

**מה בודקים?**
בודקים שהשרת **דוחה** קונפיגורציה היסטורית שחסר בה שדה `end_time`.

**למה זה חשוב?**
- Historic Playback דורש **שני** שדות זמן: `start_time` ו-`end_time`
- בלי `end_time`, המערכת לא יודעת מתי לעצור
- חסר ולידציה → crashes, undefined behavior, data corruption

**מה קורה אם לא בודקים?**
אם השרת מקבל קונפיגורציה ללא `end_time`:
- Baby Analyzer לא יודע מתי לעצור
- יכול להמשיך לקרוא נתונים ללא סוף → memory leak
- MongoDB query יהיה לא מוגדר
- הלקוח לא יקבל התראה שיש בעיה

### נתוני הבדיקה

**Payload לא תקין** (חסר `end_time`):

```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": "251021120000",
  "view_type": 0
}
```

**שימו לב**: יש `start_time` אבל **חסר** `end_time` - זו הבעיה!

### צעדי הבדיקה (Step-by-Step)

| # | צעד | תוצאה צפויה | הסבר |
|---|-----|-------------|------|
| 1 | יצירת task_id ייחודי | task_id תקף | `generate_task_id("historic_missing_end")` |
| 2 | יצירת payload ללא `end_time` | dict נוצר | בניית ה-payload עם `start_time` בלבד |
| 3 | וידוא `start_time` קיים ו-`end_time` חסר | end_time is None | `assert payload.get("end_time") is None` |
| 4 | שליחת POST לשרת | request נשלח | `POST /focus-server/config/{task_id}` |
| 5 | **קבלת HTTP 400** | Status 400 | השרת צריך לדחות! |
| 6 | בדיקת הודעת שגיאה | "end_time" במסר | השגיאה צריכה להזכיר את השדה החסר |
| 7 | בדיקת הודעה ברורה | תיאור מפורש | "Historic playback requires end_time field" |
| 8 | וידוא אי-יצירת task | לא נמצא ב-DB | `db.tasks.find({task_id})` → empty |
| 9 | בדיקת לוגים | שגיאת ולידציה | הלוגים צריכים להראות דחייה |
| 10 | בדיקת יציבות | לא קרס | השרת ממשיך לעבוד אחרי דחייה |

### תוצאה צפויה

**HTTP Response**:
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Validation Error",
  "message": "Historic playback requires end_time field",
  "missing_field": "end_time",
  "details": "Both start_time and end_time are required for historic mode"
}
```

**MongoDB State**: אין task חדש  
**Server Logs**: `[ERROR] Configuration rejected: missing end_time for historic playback`  
**Server Status**: יציב, ללא קריסות

### יישום בקוד (מתוכנן)

**קובץ**: `tests/integration/api/test_historic_playback_flow.py`  
**Class**: `TestHistoricPlaybackValidation`  
**Function**: `test_config_with_missing_end_time`

```python
import pytest
import logging
from src.utils.helpers import generate_task_id
from src.models.focus_server_models import ConfigTaskRequest
from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError

logger = logging.getLogger(__name__)

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.historic
@pytest.mark.negative
class TestHistoricPlaybackValidation:
    """Historic playback validation tests."""
    
    def test_config_with_missing_end_time(self, focus_server_api):
        """
        Test PZ-13909: Historic Configuration Missing end_time Field
        
        Validates that server rejects historic config without end_time.
        
        Expected:
            - HTTP 400 Bad Request
            - Error message mentions "end_time"
            - No task created
            - Server stable
        """
        # STEP 1: Generate task_id
        task_id = generate_task_id("historic_missing_end")
        logger.info(f"Test PZ-13909: Missing end_time - {task_id}")
        
        # STEP 2: Create payload WITHOUT end_time
        payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 0, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": "251021120000",  # ✅ Has start_time
            # end_time: MISSING!              # ❌ No end_time
            "view_type": 0
        }
        
        # STEP 3: Verify end_time is missing
        assert "end_time" not in payload or payload.get("end_time") is None
        logger.info("✓ Verified: end_time is missing from payload")
        
        # STEP 4 & 5: Send request and expect HTTP 400
        with pytest.raises(APIError) as exc_info:
            config_request = ConfigTaskRequest(**payload)
            focus_server_api.config_task(task_id, config_request)
        
        # STEP 6: Verify error message contains "end_time"
        error_msg = str(exc_info.value).lower()
        assert "end_time" in error_msg, \
            f"Error message should mention 'end_time', got: {error_msg}"
        logger.info(f"✓ Error message mentions 'end_time': {exc_info.value}")
        
        # STEP 7: Verify error is descriptive
        assert "historic" in error_msg or "required" in error_msg, \
            "Error should explain that end_time is required for historic playback"
        
        # STEP 8: Verify no task created
        waterfall_response = focus_server_api.get_waterfall(task_id, 10)
        assert waterfall_response.status_code == 404, \
            "Task should NOT have been created (waterfall should return 404)"
        logger.info("✓ No task created in MongoDB")
        
        # STEP 9 & 10: Server should be stable
        # Try a valid request to verify server is still working
        channels_response = focus_server_api.get_channels()
        assert channels_response is not None
        logger.info("✓ Server remains stable after validation rejection")
        
        logger.info("✅ Test PZ-13909 PASSED: Missing end_time properly rejected")
```

**הרצה**:
```bash
pytest tests/integration/api/test_historic_playback_flow.py::TestHistoricPlaybackValidation::test_config_with_missing_end_time -v
```

**זמן צפוי**: ~1 שנייה

---

## 🎯 TEST #2: Historic Configuration Missing start_time Field

**Jira ID**: PZ-13907  
**Priority**: High  
**Type**: Integration Test (Negative)  
**Status**: TO DO - לא ממומש עדיין

### מטרת הטסט

**מה בודקים?**
בודקים שהשרת **דוחה** קונפיגורציה היסטורית שחסר בה שדה `start_time`.

**למה זה חשוב?**
- Historic Playback צריך לדעת **מתי להתחיל**
- `start_time` מגדיר את ה-window הראשון לקריאה
- בלי `start_time`, MongoDB query לא יכול להתבצע
- זה הזוג של TEST #1 - שניהם צריכים להיות

**מה קורה אם לא בודקים?**
- Baby Analyzer לא יודע מאיזה recording להתחיל
- MongoDB query יחזיר כל הנתונים (אין WHERE clause)
- עלולה להיגרם קריסה או timeout
- ניסיון לטעון את כל ההיסטוריה → OOM (Out Of Memory)

### נתוני הבדיקה

**Payload לא תקין** (חסר `start_time`):

```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "end_time": "251021120000",
  "view_type": 0
}
```

**שימו לב**: יש `end_time` אבל **חסר** `start_time` - זו הבעיה!

### צעדי הבדיקה

| # | צעד | תוצאה צפויה | יישום בקוד |
|---|-----|-------------|------------|
| 1 | יצירת task_id | ID ייחודי | `task_id = generate_task_id("historic_missing_start")` |
| 2 | בניית payload ללא `start_time` | Dict נוצר | `payload = {..., "end_time": "251021120000"}` |
| 3 | וידוא שדות | start_time חסר, end_time קיים | `assert "start_time" not in payload` |
| 4 | שליחת POST | Request נשלח | `api.config_task(task_id, request)` |
| 5 | קבלת 400 | HTTP 400 | `with pytest.raises(APIError)` |
| 6 | בדיקת הודעה | "start_time" בהודעה | `assert "start_time" in error_msg` |
| 7 | בדיקת פירוט | הודעה ברורה | הסבר שזה נדרש ל-historic mode |
| 8 | וידוא DB | אין task | `waterfall → 404` |
| 9 | בדיקת logs | שגיאה מתועדת | אחרי הריצה צריך לבדוק logs |
| 10 | בדיקת stability | Server עובד | ניסיון request תקין אחר כך |

### יישום בקוד (מתוכנן)

```python
def test_config_with_missing_start_time(self, focus_server_api):
    """
    Test PZ-13907: Historic Configuration Missing start_time Field
    
    Validates that server rejects historic config without start_time.
    """
    task_id = generate_task_id("historic_missing_start")
    logger.info(f"Test PZ-13907: Missing start_time - {task_id}")
    
    # Payload with end_time but NO start_time
    payload = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 0, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        # start_time: MISSING!
        "end_time": "251021120000",  # ✅ Has end_time
        "view_type": 0
    }
    
    # Verify start_time is missing
    assert "start_time" not in payload or payload.get("start_time") is None
    
    # Expect rejection
    with pytest.raises(APIError) as exc_info:
        config_request = ConfigTaskRequest(**payload)
        focus_server_api.config_task(task_id, config_request)
    
    # Verify error mentions start_time
    error_msg = str(exc_info.value).lower()
    assert "start_time" in error_msg
    assert "historic" in error_msg or "required" in error_msg
    
    # Verify no task created
    waterfall_response = focus_server_api.get_waterfall(task_id, 10)
    assert waterfall_response.status_code == 404
    
    logger.info("✅ Test PZ-13907 PASSED")
```

---

## 🎯 TEST #3: Low Throughput Configuration Edge Case

**Jira ID**: PZ-13906  
**Priority**: Medium-High  
**Type**: Integration Test (Edge Case)  
**Status**: TO DO - לא ממומש (אך דומה קיים)

### מטרת הטסט

**מה בודקים?**
בודקים שהמערכת מתנהגת נכון כאשר הקונפיגורציה מייצרת **תפוקת נתונים נמוכה מאוד** (< 1 Mbps).

**מה זה Low Throughput?**
- NFFT גדול (4096) → פחות rows לשנייה
- מעט sensors (5) → פחות bytes per row
- טווח תדרים צר (100 Hz) → פחות frequency bins

**למה זה חשוב?**
- צריך לוודא שהמערכת **לא דוחה** קונפיגורציות איטיות (אלא אם יש minimum)
- לזהות אם יש threshold מינימלי
- לוודא שהמערכת לא תקפוא או תתנהג לא צפוי עם update rate נמוך

**שאלות לפגישת specs**:
1. האם יש minimum rows/sec? (למשל 0.1 rows/sec)
2. האם יש minimum data rate? (למשל 0.01 Mbps)
3. האם המערכת צריכה להתריע או לדחות?

### חישובים

**נוסחאות:**
```
PRR = 1000 samples/sec (מהמטאדטה)
Rows/sec = PRR / NFFT
Bytes/row = sensors × (NFFT/2) × 4 bytes
Data rate (Mbps) = (Rows/sec × Bytes/row × 8) / 1,000,000
```

**חישוב לדוגמה**:
```
NFFT = 4096
Sensors = 5
Frequency bins = NFFT/2 = 2048

Rows/sec = 1000 / 4096 ≈ 0.24 rows/sec  ← מאוד איטי!
Bytes/row = 5 × 2048 × 4 = 40,960 bytes
Data rate = 0.24 × 40,960 × 8 / 1,000,000 ≈ 0.08 Mbps  ← מאוד נמוך!
```

### נתוני הבדיקה

```json
{
  "nfftSelection": 4096,
  "displayInfo": {"height": 500},
  "channels": {
    "min": 5,
    "max": 10
  },
  "frequencyRange": {
    "min": 100,
    "max": 200
  },
  "view_type": 0
}
```

### צעדי הבדיקה

| # | צעד | תוצאה צפויה | יישום |
|---|-----|-------------|-------|
| 1 | שליחת GET /live_metadata | קבלת PRR | `metadata = api.get_live_metadata()` |
| 2 | יצירת low-throughput config | payload נוצר | payload עם NFFT=4096, sensors=5 |
| 3 | חישוב throughput צפוי | < 1 Mbps | שימוש ב-`validate_configuration_compatibility()` |
| 4 | וידוא rows/sec < 1 | 0.24 rows/sec | `assert estimates['rows_per_sec'] < 1` |
| 5 | יצירת task_id | ID תקף | `generate_task_id("low_throughput")` |
| 6 | שליחת POST /config | Response התקבל | `api.config_task(task_id, request)` |
| 7 | בדיקת תשובה | **HTTP 200** (likely) | הקונפיגורציה **מתקבלת** |
| 8 | בדיקת warnings | אזהרה אופציונלית | "Low spectrogram rate: 0.24 rows/sec" |
| 9 | וידוא יצירת task | Task נוצר | `waterfall → 200/201` |
| 10 | תיעוד התנהגות | Logged | האם יש minimum threshold? |

### תוצאה צפויה

**אופציה A: מקובל עם אזהרה**
```http
HTTP/1.1 200 OK
{
  "status": "Config received successfully",
  "warning": "Low update rate: 0.24 rows/sec - display may be slow"
}
```

**אופציה B: דחייה (אם יש minimum)**
```http
HTTP/1.1 400 Bad Request
{
  "error": "Configuration below minimum threshold",
  "message": "Rows/sec (0.24) is below minimum (0.5)",
  "suggestion": "Reduce NFFT or increase sensor range"
}
```

### יישום בקוד (קיים!)

**קובץ**: `tests/integration/api/test_spectrogram_pipeline.py`  
**Lines**: 304-343  
**Function**: `test_low_throughput_configuration`

```python
def test_low_throughput_configuration(self, focus_server_api):
    """Test: Configuration with low throughput."""
    logger.info(f"Test: Low throughput configuration")
    
    # Check compatibility
    compat_result = validate_configuration_compatibility(
        nfft=4096,       # Large NFFT
        sensor_range=5,  # Few sensors
        prr=1000.0
    )
    
    logger.info(
        f"Expected output rate: "
        f"{compat_result['estimates']['output_data_rate_mbps']:.2f} Mbps"
    )
    logger.info(
        f"Rows per second: "
        f"{compat_result['estimates']['rows_per_sec']:.2f}"
    )
    
    if len(compat_result["warnings"]) > 0:
        logger.warning(f"Configuration warnings: {compat_result['warnings']}")
    
    # Low throughput config
    payload = {
        "displayTimeAxisDuration": 30,
        "nfftSelection": 4096,  # Large NFFT = low update rate
        "displayInfo": {"height": 1000},
        "channels": {"min": 5, "max": 10},  # Small sensor range
        "frequencyRange": {"min": 100, "max": 200},  # Narrow freq range
        "start_time": None,
        "end_time": None,
        "view_type": ViewType.MULTICHANNEL
    }
    
    config_request = ConfigureRequest(**payload)
    response = focus_server_api.configure_streaming_job(config_request)
    
    # Verify acceptance
    assert hasattr(response, 'job_id') and response.job_id
    logger.info("✅ Low throughput configuration accepted")
```

**הרצה**:
```bash
pytest tests/integration/api/test_spectrogram_pipeline.py::test_low_throughput_configuration -v
```

**סטטוס**: ✅ **כבר ממומש!**

---

## 🎯 TEST #4: Configuration Resource Usage Estimation

**Jira ID**: PZ-13904  
**Priority**: High  
**Type**: Integration Test (Performance)  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
מחשבים ומאמתים את **הערכת השימוש במשאבים** (CPU, Memory, Network Bandwidth) **לפני** יצירת ה-task.

**למה זה חשוב?**
- **Capacity Planning** - לדעת מה צורכת הקונפיגורציה
- **מניעת overload** - למנוע קונפיגורציות שיקרסו את השרת
- **תכנון משאבים** - להבין איזה configuration יקרה ומה זולה
- **אזהרות מוקדמות** - להתריע לפני שמקצים משאבים

### חישובים (מפורטים!)

**תהליך החישוב:**

```
┌─────────────────────────────────────────────────────┐
│ INPUT: Configuration Parameters                    │
├─────────────────────────────────────────────────────┤
│ • NFFT = 1024                                       │
│ • Sensor Range = 50 (0-49)                          │
│ • Frequency Range = 0-500 Hz                        │
│ • PRR = 1000 samples/sec (from live_metadata)       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ STEP 1: Calculate Frequency Bins                   │
├─────────────────────────────────────────────────────┤
│ Frequency Bins = NFFT / 2                          │
│ Frequency Bins = 1024 / 2 = 512 bins              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ STEP 2: Calculate Spectrogram Update Rate          │
├─────────────────────────────────────────────────────┤
│ Rows/sec = PRR / NFFT                               │
│ Rows/sec = 1000 / 1024 ≈ 0.98 rows/sec            │
│                                                     │
│ מה זה אומר?                                        │
│ המערכת תייצר ספקטוגרמה חדשה כל 1.02 שניות        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ STEP 3: Calculate Bytes per Row                    │
├─────────────────────────────────────────────────────┤
│ Bytes/row = Sensors × Freq_bins × 4 bytes          │
│ Bytes/row = 50 × 512 × 4 = 102,400 bytes          │
│                                                     │
│ למה 4 bytes?                                        │
│ כל ערך intensity הוא float32 (4 bytes)             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ STEP 4: Calculate Output Data Rate                 │
├─────────────────────────────────────────────────────┤
│ Data rate = Rows/sec × Bytes/row × 8 bits/byte     │
│ Data rate = 0.98 × 102,400 × 8                     │
│ Data rate = 802,816 bits/sec                       │
│ Data rate = 0.80 Mbps                              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ STEP 5: Validate Reasonability                     │
├─────────────────────────────────────────────────────┤
│ Is 0.1 < rate < 100 Mbps?                          │
│ 0.1 < 0.80 < 100 → ✅ YES                          │
│                                                     │
│ Need Warning?                                       │
│ rate > 50 Mbps? → 0.80 < 50 → ❌ NO WARNING       │
└─────────────────────────────────────────────────────┘
```

### נתוני הבדיקה

```json
{
  "nfftSelection": 1024,
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "displayInfo": {"height": 1000}
}
```

### צעדי הבדיקה

| # | צעד | תוצאה | קוד |
|---|-----|-------|-----|
| 1 | קבלת PRR מ-metadata | PRR value | `metadata = api.get_live_metadata()` |
| 2 | הגדרת config | payload | payload dict |
| 3 | חישוב NFFT | 1024 | `nfft = payload['nfftSelection']` |
| 4 | חישוב sensor range | 50 | `range = max - min` |
| 5 | חישוב rows/sec | ~0.98 | `rows_sec = prr / nfft` |
| 6 | חישוב frequency bins | 512 | `bins = nfft / 2` |
| 7 | חישוב bytes/row | 102,400 | `bytes = sensors × bins × 4` |
| 8 | חישוב data rate | ~0.8 Mbps | `rate = rows × bytes × 8 / 1e6` |
| 9 | בדיקת סבירות | בטווח תקין | `0.1 < rate < 100` |
| 10 | בדיקת warnings | אין | `rate < 50 → no warning` |
| 11 | וידוא compatibility | Compatible | `validate_configuration_compatibility()` |
| 12 | תיעוד | Logged | לוגים |

### יישום בקוד (קיים!)

**קובץ**: `tests/integration/api/test_spectrogram_pipeline.py`  
**Lines**: 246-268  
**Function**: `test_configuration_resource_estimation`

```python
def test_configuration_resource_estimation(self, focus_server_api):
    """
    Test PZ-13904: Configuration Resource Usage Estimation
    
    Validates resource usage estimation for configurations.
    """
    logger.info("Test: Configuration resource usage estimation")
    
    # Configuration to test
    nfft = 1024
    sensor_range = 50
    freq_min = 0
    freq_max = 500
    
    # Get PRR from metadata
    metadata = focus_server_api.get_live_metadata()
    prr = metadata.prr if hasattr(metadata, 'prr') else 1000.0
    logger.info(f"PRR from metadata: {prr} samples/sec")
    
    # Calculate estimates
    compat_result = validate_configuration_compatibility(
        nfft=nfft,
        sensor_range=sensor_range,
        prr=prr
    )
    
    estimates = compat_result['estimates']
    
    # Log all estimates
    logger.info(f"Resource Estimates:")
    logger.info(f"  Rows/sec: {estimates['rows_per_sec']:.2f}")
    logger.info(f"  Bytes/row: {estimates['bytes_per_row']:,}")
    logger.info(f"  Output rate: {estimates['output_data_rate_mbps']:.2f} Mbps")
    logger.info(f"  Frequency bins: {estimates['frequency_bins']}")
    
    # Validate reasonability
    assert 0.1 < estimates['output_data_rate_mbps'] < 100, \
        f"Data rate {estimates['output_data_rate_mbps']} Mbps is unreasonable"
    
    # Check for warnings
    if estimates['output_data_rate_mbps'] > 50:
        assert len(compat_result['warnings']) > 0, \
            "Should warn for high throughput (>50 Mbps)"
    
    # Verify compatibility
    assert compat_result['is_compatible'] == True
    
    logger.info("✅ Configuration compatible")
```

**פונקציית העזר** (`src/utils/validators.py`):

```python
def validate_configuration_compatibility(
    nfft: int,
    sensor_range: int,
    prr: float,
    max_throughput_mbps: float = 100.0
) -> Dict[str, Any]:
    """
    Validate configuration compatibility and estimate resources.
    
    Args:
        nfft: NFFT value
        sensor_range: Number of sensors
        prr: Pulse Repetition Rate (samples/sec)
        max_throughput_mbps: Maximum allowed throughput
        
    Returns:
        Dict with:
            - is_compatible: bool
            - estimates: dict of calculations
            - warnings: list of warning messages
    """
    # Calculate frequency bins
    freq_bins = nfft // 2
    
    # Calculate spectrogram rows per second
    rows_per_sec = prr / nfft
    
    # Calculate bytes per row (4 bytes per float32)
    bytes_per_row = sensor_range * freq_bins * 4
    
    # Calculate output data rate (Mbps)
    output_data_rate_mbps = (rows_per_sec * bytes_per_row * 8) / 1_000_000
    
    # Collect estimates
    estimates = {
        'frequency_bins': freq_bins,
        'rows_per_sec': rows_per_sec,
        'bytes_per_row': bytes_per_row,
        'output_data_rate_mbps': output_data_rate_mbps
    }
    
    # Check compatibility
    warnings = []
    is_compatible = True
    
    if output_data_rate_mbps > max_throughput_mbps:
        warnings.append(
            f"Data rate ({output_data_rate_mbps:.1f} Mbps) exceeds "
            f"maximum ({max_throughput_mbps} Mbps)"
        )
        is_compatible = False
    
    if output_data_rate_mbps > 50:
        warnings.append(f"High throughput: {output_data_rate_mbps:.1f} Mbps")
    
    if rows_per_sec < 0.1:
        warnings.append(f"Very low update rate: {rows_per_sec:.2f} rows/sec")
    
    if rows_per_sec > 1000:
        warnings.append(f"Very high update rate: {rows_per_sec:.0f} rows/sec")
    
    return {
        'is_compatible': is_compatible,
        'estimates': estimates,
        'warnings': warnings
    }
```

**הרצה**:
```bash
pytest tests/integration/api/test_spectrogram_pipeline.py::test_configuration_resource_estimation -v
```

---

## 🎯 TEST #5: Frequency Range Nyquist Limit Enforcement

**Jira ID**: PZ-13903  
**Priority**: **CRITICAL** 🔴  
**Type**: Integration Test (Data Quality - Critical)  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים שהשרת **אוכף** את משפט Nyquist-Shannon ו**דוחה** תדרים שחורגים מגבול Nyquist.

**מה זה משפט Nyquist-Shannon?**
```
משפט פיזיקלי בעיבוד אותות:
כדי לדגום אות נכון, תדר הדגימה (PRR) חייב להיות
לפחות כפול מהתדר המקסימלי שרוצים לבדוק.

נוסחה:
Nyquist Frequency = PRR / 2

דוגמה:
אם PRR = 1000 samples/sec
אז Nyquist = 500 Hz
כלומר: אפשר לבדוק תדרים עד 500 Hz בלבד!
```

**למה זה קריטי?**
- זה לא רק באג תוכנה - **זה פיזיקה!**
- חריגה מ-Nyquist גורמת ל-**Aliasing** (עיוות נתונים)
- תדרים גבוהים "מתחפשים" לתדרים נמוכים → **נתונים שגויים לחלוטין**
- הנתונים המעוותים יובילו ל**מסקנות שגויות** → סכנה!

**דוגמה ל-Aliasing:**
```
PRR = 1000 samples/sec
Nyquist = 500 Hz

אם מבקשים freq_max = 600 Hz:
❌ תדר של 600 Hz ייראה כמו 400 Hz (שגוי!)
❌ תדר של 700 Hz ייראה כמו 300 Hz (שגוי!)

התוצאה: נתונים מזויפים!
```

### נתוני הבדיקה

**תרחיש 1: תקין (מתחת ל-Nyquist)**

```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {
    "min": 0,
    "max": 400
  },
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```
**הערה**: אם PRR=1000, Nyquist=500, max=400 < 500 → ✅ **תקין!**

**תרחיש 2: לא תקין (מעל Nyquist)**

```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {
    "min": 0,
    "max": 600
  },
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```
**הערה**: אם PRR=1000, Nyquist=500, max=600 > 500 → ❌ **לא תקין - Aliasing!**

**תרחיש 3: Edge Case (בדיוק ב-Nyquist)**

```json
{
  "frequencyRange": {
    "min": 0,
    "max": 500
  }
}
```
**הערה**: max=500 == Nyquist → צריך לתעד את ההתנהגות (לקבל או לדחות?)

### צעדי הבדיקה (מפורט!)

| # | צעד | תוצאה | קוד | הסבר מפורט |
|---|-----|-------|-----|------------|
| 1 | GET /live_metadata | HTTP 200 + data | `metadata = api.get_live_metadata()` | שליפת מטאדטה חיה |
| 2 | חילוץ PRR | PRR value (e.g., 1000) | `prr = metadata.prr` | ערך הדגימה לשנייה |
| 3 | חישוב Nyquist | Nyquist = PRR/2 | `nyquist = prr / 2.0` | חישוב גבול פיזיקלי |
| 4 | תיעוד Nyquist | Logged | `logger.info(f"Nyquist: {nyquist} Hz")` | לתיעוד ולדוחות |
| 5 | task_id לטסט 1 | ID ייחודי | `generate_task_id("nyquist_valid")` | לקונפיגורציה תקינה |
| 6 | config עם 80% Nyquist | payload | `freq_max = nyquist * 0.8` | תדר בטוח (400 Hz) |
| 7 | POST /config | **HTTP 200** | `api.config_task(...)` | **צריך להתקבל!** |
| 8 | וידוא אין warnings | לא שגיאות | בדיקת response | התדר תקין |
| 9 | task_id לטסט 2 | ID ייחודי | `generate_task_id("nyquist_invalid")` | לקונפיגורציה לא תקינה |
| 10 | config עם 120% Nyquist | payload | `freq_max = nyquist * 1.2` | תדר מופרז (600 Hz) |
| 11 | POST /config | **HTTP 400** | `with pytest.raises(APIError)` | **צריך להידחות!** |
| 12 | בדיקת הודעה | הסבר ברור | error מכיל "Nyquist" | הסבר פיזיקלי |
| 13 | Edge case: בדיוק Nyquist | לתעד | `freq_max = nyquist` | תיעוד התנהגות |
| 14 | בדיקת stability | לא קרס | request נוסף עובד | השרת יציב |

### תוצאה צפויה - תרחיש תקין

```http
HTTP/1.1 200 OK
{
  "status": "Config received successfully",
  "job_id": "job_xyz123"
}
```

### תוצאה צפויה - תרחיש לא תקין

```http
HTTP/1.1 400 Bad Request
{
  "error": "Nyquist Frequency Violation",
  "message": "frequencyRange.max (600 Hz) exceeds Nyquist frequency (500 Hz)",
  "details": {
    "requested_max_freq": 600,
    "nyquist_limit": 500,
    "prr": 1000,
    "explanation": "Frequencies above Nyquist will cause aliasing (data corruption)"
  },
  "suggestion": "Reduce max frequency to 500 Hz or lower"
}
```

### יישום בקוד (קיים!)

**קובץ**: `tests/integration/api/test_spectrogram_pipeline.py`  
**Lines**: 127-157  
**Function**: `test_frequency_range_within_nyquist`

```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
class TestFrequencyConfiguration:
    """Test suite for frequency range configuration and Nyquist validation."""
    
    def test_frequency_range_within_nyquist(self, focus_server_api, live_metadata):
        """
        Test PZ-13903: Frequency Range Nyquist Limit Enforcement
        
        CRITICAL TEST - Prevents aliasing and data corruption!
        
        Validates that:
        1. PRR is extracted from live_metadata
        2. Nyquist calculated correctly (PRR/2)
        3. Frequencies below Nyquist are ACCEPTED
        4. Frequencies above Nyquist are REJECTED
        """
        logger.info("Test PZ-13903: Nyquist Limit Enforcement")
        
        # STEP 1-3: Get PRR and calculate Nyquist
        prr = live_metadata.prr if hasattr(live_metadata, 'prr') else 1000.0
        nyquist_frequency = prr / 2.0
        logger.info(f"PRR: {prr} samples/sec")
        logger.info(f"Nyquist Frequency: {nyquist_frequency} Hz")
        
        # STEP 4-8: Test VALID configuration (below Nyquist)
        safe_freq_max = int(nyquist_frequency * 0.8)  # 80% of Nyquist
        logger.info(f"Testing safe frequency: {safe_freq_max} Hz (80% of Nyquist)")
        
        valid_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 0, "max": 50},
            "frequencyRange": {"min": 0, "max": safe_freq_max},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request = ConfigureRequest(**valid_payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        # Should be accepted
        assert hasattr(response, 'job_id') and response.job_id
        logger.info(f"✅ Frequency below Nyquist ({safe_freq_max} Hz) ACCEPTED")
        
        # STEP 9-12: Test INVALID configuration (above Nyquist)
        excessive_freq_max = int(nyquist_frequency * 1.2)  # 120% of Nyquist
        logger.info(f"Testing excessive frequency: {excessive_freq_max} Hz (120% of Nyquist)")
        
        invalid_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 0, "max": 50},
            "frequencyRange": {"min": 0, "max": excessive_freq_max},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        # Should be rejected
        with pytest.raises(APIError) as exc_info:
            config_request = ConfigureRequest(**invalid_payload)
            focus_server_api.configure_streaming_job(config_request)
        
        error_msg = str(exc_info.value).lower()
        assert "nyquist" in error_msg or "frequency" in error_msg or "exceeds" in error_msg
        logger.info(f"✅ Frequency above Nyquist ({excessive_freq_max} Hz) REJECTED")
        logger.info(f"   Error: {exc_info.value}")
        
        # STEP 13: Edge case - exactly at Nyquist
        logger.info(f"Edge case: Testing frequency at Nyquist ({nyquist_frequency} Hz)")
        # Document behavior - may accept or reject
        
        logger.info("✅ Test PZ-13903 PASSED: Nyquist limit properly enforced")
```

**הרצה**:
```bash
pytest tests/integration/api/test_spectrogram_pipeline.py::TestFrequencyConfiguration::test_frequency_range_within_nyquist -v
```

**זמן ריצה**: 2-3 שניות

---

## 🎯 TEST #6: NFFT Values Validation - All Supported Values

**Jira ID**: PZ-13901  
**Priority**: High  
**Type**: Integration Test (Functional)  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים שהשרת **תומך ומקבל** את **כל** ערכי NFFT התקפים: 128, 256, 512, 1024, 2048, 4096.

**מה זה NFFT?**
- NFFT = Number of FFT points (מספר נקודות ה-FFT)
- קובע את **רזולוציית התדר** בניתוח ספקטרלי
- ערכים תקפים: **חזקות של 2** בטווח 128-4096

**למה זה חשוב?**
- כל NFFT נותן **trade-off** שונה בין רזולוציית תדר לרזולוציית זמן
- משתמשים שונים צריכים ערכים שונים לפי הצרכים שלהם
- צריך לוודא שהמערכת **לא מגבילה** את המשתמש

### Trade-offs של NFFT

| NFFT | רזולוציית תדר | קצב עדכון (rows/sec) | עומס CPU | שימוש |
|------|---------------|---------------------|----------|-------|
| **128** | נמוכה (64 bins) | מאוד גבוה (~7.8) | נמוך | מעקב מהיר אחר שינויים |
| **256** | נמוכה (128 bins) | גבוה (~3.9) | נמוך-בינוני | real-time monitoring |
| **512** | בינונית (256 bins) | בינוני (~2.0) | בינוני | balanced |
| **1024** | טובה (512 bins) | בינוני (~0.98) | בינוני-גבוה | **הכי נפוץ** |
| **2048** | גבוהה (1024 bins) | נמוך (~0.49) | גבוה | ניתוח מפורט |
| **4096** | מאוד גבוהה (2048 bins) | מאוד נמוך (~0.24) | מאוד גבוה | ניתוח אקוסטי מדויק |

**הסבר:**
- NFFT קטן (128) → עדכונים מהירים אבל פחות פרטים בתדר
- NFFT גדול (4096) → הרבה פרטים בתדר אבל עדכונים איטיים

### נתוני הבדיקה

**Template** (עבור כל NFFT):

```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": <NFFT_VALUE>,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```

**ערכי NFFT לבדיקה**: `[128, 256, 512, 1024, 2048, 4096]`

### צעדי הבדיקה

| # | צעד | תוצאה | פירוט |
|---|-----|-------|-------|
| 1 | לולאה על כל NFFT | iterate | `for nfft in [128, 256, 512, 1024, 2048, 4096]:` |
| 2 | יצירת task_id ייחודי | ID לכל NFFT | `task_id = f"nfft_test_{nfft}_{timestamp}"` |
| 3 | יצירת config עם NFFT | payload | `payload['nfftSelection'] = nfft` |
| 4 | וידוא NFFT הוא חזקה של 2 | True | `nfft & (nfft-1) == 0` |
| 5 | POST /config | HTTP 200 | השרת מקבל |
| 6 | בדיקת response | "Config received" | הודעת הצלחה |
| 7 | שאילתת metadata (אופציונלי) | NFFT הוחל | בדיקה שה-NFFT התקבל |
| 8 | מדידת זמן | < 5 שניות | ביצועים סבירים |
| 9 | תיעוד הצלחה | Logged | רישום ללוג |
| 10 | המשך ללולאה | repeat | NFFT הבא |
| 11 | בדיקת 100% הצלחה | כולם עברו | כל 6 הערכים התקבלו |

### תוצאה צפויה

**כל NFFT צריך להתקבל:**

```
✅ NFFT=128  → HTTP 200 OK
✅ NFFT=256  → HTTP 200 OK
✅ NFFT=512  → HTTP 200 OK
✅ NFFT=1024 → HTTP 200 OK (הכי נפוץ)
✅ NFFT=2048 → HTTP 200 OK
✅ NFFT=4096 → HTTP 200 OK
```

**Success Rate**: 6/6 (100%)

### יישום בקוד (קיים!)

**קובץ**: `tests/integration/api/test_spectrogram_pipeline.py`  
**Lines**: 80-97  
**Class**: `TestNFFTConfiguration`  
**Function**: `test_nfft_variations`

```python
@pytest.mark.integration
@pytest.mark.api
class TestNFFTConfiguration:
    """Test suite for NFFT configuration validation."""
    
    def test_nfft_variations(self, focus_server_api):
        """
        Test PZ-13901: NFFT Values Validation - All Supported Values
        
        Validates that all standard NFFT values are accepted.
        
        NFFT values: 128, 256, 512, 1024, 2048, 4096
        """
        logger.info("Test PZ-13901: NFFT Variations")
        
        # All supported NFFT values
        nfft_values = [128, 256, 512, 1024, 2048, 4096]
        results = []
        
        for nfft in nfft_values:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing NFFT = {nfft}")
            logger.info(f"{'='*60}")
            
            # Verify NFFT is power of 2
            is_power_of_2 = (nfft & (nfft - 1)) == 0
            assert is_power_of_2, f"NFFT {nfft} is not a power of 2"
            logger.info(f"✓ NFFT {nfft} is a power of 2")
            
            # Create configuration
            payload = {
                "displayTimeAxisDuration": 10,
                "nfftSelection": nfft,
                "displayInfo": {"height": 1000},
                "channels": {"min": 0, "max": 50},
                "frequencyRange": {"min": 0, "max": 500},
                "start_time": None,
                "end_time": None,
                "view_type": ViewType.MULTICHANNEL
            }
            
            # Configure
            import time
            start_time = time.time()
            
            config_request = ConfigureRequest(**payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            elapsed = time.time() - start_time
            
            # Verify acceptance
            assert hasattr(response, 'job_id') and response.job_id
            
            results.append({
                'nfft': nfft,
                'success': True,
                'job_id': response.job_id,
                'config_time': elapsed
            })
            
            logger.info(f"✅ NFFT={nfft} accepted ({elapsed:.2f}s)")
            logger.info(f"   Job ID: {response.job_id}")
        
        # Verify all succeeded
        success_count = sum(1 for r in results if r['success'])
        logger.info(f"\n{'='*60}")
        logger.info(f"NFFT Validation Summary:")
        logger.info(f"  Success: {success_count}/{len(nfft_values)}")
        logger.info(f"{'='*60}")
        
        assert success_count == len(nfft_values), \
            f"Expected all NFFT values to be accepted, but only {success_count}/6 succeeded"
        
        logger.info("✅ Test PZ-13901 PASSED: All NFFT values accepted")
```

**הרצה**:
```bash
pytest tests/integration/api/test_spectrogram_pipeline.py::TestNFFTConfiguration::test_nfft_variations -v
```

**זמן ריצה**: 5-10 שניות (6 configurations)

---

## 🎯 TEST #7: GET /sensors - Retrieve Available Sensors List

**Jira ID**: PZ-13897  
**Priority**: High  
**Type**: Integration Test (Smoke)  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים שה-endpoint `GET /sensors` מחזיר רשימה **מלאה ונכונה** של כל ה-sensors הזמינים במערכת.

**למה זה חשוב?**
- זה **prerequisite** לכל קונפיגורציה
- הלקוח **חייב** לדעת אילו sensors קיימים לפני שהוא בוחר ROI
- בלי הרשימה, הלקוח לא יכול לבחור channels תקינים
- זה **smoke test** - אחת הבדיקות הראשונות שצריכות לעבוד

**תרחישי שימוש:**
1. משתמש פותח את האפליקציה → קורא GET /sensors → רואה sensors זמינים
2. משתמש בוחר ROI → צריך לוודא ש-min ו-max בטווח sensors
3. מפתח בודק מה זמין במערכת

### נתוני הבדיקה

**Request**:
```http
GET https://10.10.100.100/focus-server/sensors HTTP/1.1
Accept: application/json
```

**אין body** - זה GET request פשוט.

**Expected Response Structure** (אפשרות 1):
```json
{
  "sensors": [0, 1, 2, 3, 4, ..., 199]
}
```

**Expected Response Structure** (אפשרות 2):
```json
{
  "sensor_count": 200,
  "sensor_list": [0, 1, 2, 3, ..., 199]
}
```

### צעדי הבדיקה

| # | צעד | תוצאה | ולידציה |
|---|-----|-------|---------|
| 1 | GET /sensors | HTTP 200 | `response.status_code == 200` |
| 2 | בדיקת Content-Type | application/json | `'application/json' in response.headers['Content-Type']` |
| 3 | Parse JSON | Valid JSON | `data = response.json()` |
| 4 | חילוץ רשימת sensors | Array of ints | `sensors = data['sensors']` או `data['sensor_list']` |
| 5 | בדיקת לא ריק | length > 0 | `assert len(sensors) > 0` |
| 6 | בדיקת טיפוס | כולם integers | `assert all(isinstance(s, int) for s in sensors)` |
| 7 | בדיקת non-negative | כולם >= 0 | `assert all(s >= 0 for s in sensors)` |
| 8 | בדיקת התחלה מ-0 | ראשון = 0 | `assert sensors[0] == 0` |
| 9 | בדיקת רציפות | אין gaps | `assert sensors == list(range(len(sensors)))` |
| 10 | בדיקת סבירות | < 10,000 | `assert len(sensors) < 10000` |
| 11 | מדידת זמן | < 500ms | response time |
| 12 | שליחה שוב | רשימה זהה | consistency check |
| 13 | השוואה ל-MongoDB | תואם | אם יש גישה ל-DB |

### תוצאה צפויה

**Response מוצלח:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "sensors": [0, 1, 2, 3, 4, 5, ..., 199]
}
```

**מאפיינים:**
- ✅ רשימה לא ריקה (לפחות sensor אחד)
- ✅ כולם integers non-negative
- ✅ רציפים מ-0 (לא gaps)
- ✅ עקביים בין קריאות
- ✅ response time < 500ms

### יישום בקוד (קיים!)

**קובץ**: `tests/integration/api/test_live_monitoring_flow.py`  
**Lines**: 129-156  
**Class**: `TestLiveMonitoringHappyPath`  
**Function**: `test_get_sensors_list`

```python
def test_get_sensors_list(self, focus_server_api):
    """
    Test PZ-13897: GET /sensors - Retrieve Available Sensors List
    
    Validates that /sensors endpoint returns complete sensors list.
    """
    logger.info("Test PZ-13897: GET /sensors")
    
    # STEP 1-3: Send request and parse
    sensors_response = focus_server_api.get_sensors()
    
    # STEP 4: Extract sensors list
    assert hasattr(sensors_response, 'sensors')
    sensors = sensors_response.sensors
    logger.info(f"Received {len(sensors)} sensors")
    
    # STEP 5: Verify non-empty
    assert len(sensors) > 0, "Sensors list should not be empty"
    logger.info(f"✓ Sensors list is non-empty: {len(sensors)} sensors")
    
    # STEP 6: Verify all are integers
    assert all(isinstance(s, int) for s in sensors), \
        "All sensors should be integers"
    logger.info("✓ All sensors are integers")
    
    # STEP 7: Verify all non-negative
    assert all(s >= 0 for s in sensors), \
        "All sensors should be non-negative"
    logger.info("✓ All sensors are non-negative")
    
    # STEP 8: Verify starts at 0
    assert sensors[0] == 0, "Sensors should start at 0"
    logger.info("✓ Sensors start at 0")
    
    # STEP 9: Verify sequential (no gaps)
    expected_sensors = list(range(len(sensors)))
    assert sensors == expected_sensors, \
        f"Sensors should be sequential [0...{len(sensors)-1}]"
    logger.info(f"✓ Sensors are sequential: 0...{sensors[-1]}")
    
    # STEP 10: Verify reasonable count
    assert len(sensors) < 10000, \
        f"Sensor count ({len(sensors)}) exceeds reasonable limit"
    logger.info(f"✓ Sensor count is reasonable: {len(sensors)}")
    
    # STEP 12: Call again for consistency
    sensors_response_2 = focus_server_api.get_sensors()
    sensors_2 = sensors_response_2.sensors
    
    assert sensors == sensors_2, \
        "Sensors list should be consistent across calls"
    logger.info("✓ Sensors list is consistent across multiple calls")
    
    logger.info(f"✅ Test PZ-13897 PASSED: {len(sensors)} sensors validated")
```

**הרצה**:
```bash
pytest tests/integration/api/test_live_monitoring_flow.py::TestLiveMonitoringHappyPath::test_get_sensors_list -v
```

**זמן ריצה**: 1-2 שניות

---

## 🎯 TEST #8: Missing Required Fields

**Jira ID**: PZ-13879  
**Priority**: High  
**Type**: Integration Test (Negative)  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים שהשרת **דוחה** קונפיגורציות שחסרים בהן **שדות חובה**: `channels`, `frequencyRange`, או `nfftSelection`.

**למה זה חשוב?**
- שדות אלה **הכרחיים** ליצירת ספקטוגרמה
- בלי `channels` - לא יודעים אילו sensors לעבד
- בלי `frequencyRange` - לא יודעים איזה תדרים להציג
- בלי `nfftSelection` - לא יכולים לעשות FFT!

**מה קורה בלי ולידציה?**
- Baby Analyzer יקבל parameters חסרים → יקרוס
- ניסיון FFT בלי NFFT → segmentation fault
- ניסיון גישה ל-sensors ללא ROI → undefined behavior

### תרחישים נבדקים

**תרחיש 1: חסר `channels`**

```json
{
  "nfftSelection": 1024,
  "frequencyRange": {"min": 0, "max": 500},
  "displayInfo": {"height": 1000},
  "view_type": 0
  // channels: MISSING!
}
```

**תרחיש 2: חסר `frequencyRange`**

```json
{
  "nfftSelection": 1024,
  "channels": {"min": 0, "max": 50},
  "displayInfo": {"height": 1000},
  "view_type": 0
  // frequencyRange: MISSING!
}
```

**תרחיש 3: חסר `nfftSelection`**

```json
{
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "displayInfo": {"height": 1000},
  "view_type": 0
  // nfftSelection: MISSING!
}
```

### צעדי הבדיקה (לכל תרחיש)

| # | צעד | תרחיש 1 | תרחיש 2 | תרחיש 3 |
|---|-----|---------|---------|---------|
| 1 | יצירת task_id | missing_channels | missing_freq | missing_nfft |
| 2 | יצירת payload | ללא channels | ללא frequencyRange | ללא nfftSelection |
| 3 | POST /config | → | → | → |
| 4 | קבלת 400 | HTTP 400 | HTTP 400 | HTTP 400 |
| 5 | בדיקת הודעה | "channels" | "frequencyRange" או "frequency" | "nfft" |
| 6 | וידוא אין task | 404 | 404 | 404 |

### תוצאה צפויה

**תשובה לתרחיש 1 (חסר channels):**
```http
HTTP/1.1 400 Bad Request
{
  "error": "Missing Required Field",
  "field": "channels",
  "message": "Field 'channels' is required for configuration"
}
```

**תשובה לתרחיש 2 (חסר frequencyRange):**
```http
HTTP/1.1 400 Bad Request
{
  "error": "Missing Required Field",
  "field": "frequencyRange",
  "message": "Field 'frequencyRange' is required for spectral analysis"
}
```

**תשובה לתרחיש 3 (חסר nfftSelection):**
```http
HTTP/1.1 400 Bad Request
{
  "error": "Missing Required Field",
  "field": "nfftSelection",
  "message": "Field 'nfftSelection' is required for FFT processing"
}
```

### יישום בקוד (קיים!)

**קובץ**: `tests/integration/api/test_config_validation_high_priority.py`  
**Class**: `TestMissingRequiredFields`  
**Function**: `test_pz_13879_missing_required_fields`

```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
class TestMissingRequiredFields:
    """Test suite for PZ-13879: Missing Required Fields validation."""
    
    def test_missing_channels_field(self, focus_server_api):
        """Test: Configuration missing 'channels' field."""
        task_id = generate_task_id("missing_channels")
        logger.info(f"Test: Missing channels field - {task_id}")
        
        # Payload WITHOUT channels
        payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "frequencyRange": {"min": 0, "max": 500},
            "displayInfo": {"height": 1000},
            "start_time": None,
            "end_time": None,
            "view_type": 0
            # channels: MISSING!
        }
        
        # Expect validation error
        with pytest.raises(Exception) as exc_info:
            config_request = ConfigureRequest(**payload)
            focus_server_api.configure_streaming_job(config_request)
        
        error_msg = str(exc_info.value).lower()
        assert "channel" in error_msg or "required" in error_msg
        logger.info(f"✅ Missing 'channels' properly rejected: {exc_info.value}")
    
    def test_missing_frequency_range_field(self, focus_server_api):
        """Test: Configuration missing 'frequencyRange' field."""
        task_id = generate_task_id("missing_freq")
        logger.info(f"Test: Missing frequencyRange field - {task_id}")
        
        payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "channels": {"min": 0, "max": 50},
            "displayInfo": {"height": 1000},
            "start_time": None,
            "end_time": None,
            "view_type": 0
            # frequencyRange: MISSING!
        }
        
        with pytest.raises(Exception) as exc_info:
            config_request = ConfigureRequest(**payload)
            focus_server_api.configure_streaming_job(config_request)
        
        error_msg = str(exc_info.value).lower()
        assert "frequency" in error_msg or "required" in error_msg
        logger.info(f"✅ Missing 'frequencyRange' properly rejected")
    
    def test_missing_nfft_field(self, focus_server_api):
        """Test: Configuration missing 'nfftSelection' field."""
        task_id = generate_task_id("missing_nfft")
        logger.info(f"Test: Missing nfftSelection field - {task_id}")
        
        payload = {
            "displayTimeAxisDuration": 10,
            "channels": {"min": 0, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "displayInfo": {"height": 1000},
            "start_time": None,
            "end_time": None,
            "view_type": 0
            # nfftSelection: MISSING!
        }
        
        with pytest.raises(Exception) as exc_info:
            config_request = ConfigureRequest(**payload)
            focus_server_api.configure_streaming_job(config_request)
        
        error_msg = str(exc_info.value).lower()
        assert "nfft" in error_msg or "required" in error_msg
        logger.info(f"✅ Missing 'nfftSelection' properly rejected")
```

**הרצה**:
```bash
pytest tests/integration/api/test_config_validation_high_priority.py::TestMissingRequiredFields -v
```

---

**המשך בחלק 2...**

