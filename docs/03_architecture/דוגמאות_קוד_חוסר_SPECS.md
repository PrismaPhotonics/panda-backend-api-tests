# 📌 דוגמאות קוד - חוסר Specs במערכת
## קישורים מדויקים לקוד שמראים את הבעיות

**תאריך:** 22 אוקטובר 2025  
**מטרה:** דוגמאות ממשיות מהקוד להצגה בפגישה  

---

## 🔴 **1. ROI Change Limit - 50% Hardcoded**

### 📍 **מיקום:** `src/utils/validators.py:390-460`

```python
def validate_roi_change_safety(
    current_min: int,
    current_max: int,
    new_min: int,
    new_max: int,
    max_change_percent: float = 50.0  # ❌ HARDCODED - אין specs!
) -> Dict[str, Any]:
    """
    Validate ROI change is safe (not too drastic).
    
    Large ROI changes can cause processing disruptions.
    """
```

**הבעיה:**
- ✅ הקוד: `max_change_percent: float = 50.0`
- ❓ **אף אחד לא אישר שזה נכון!**
- ❓ מה אם צריך 30%? או 70%?

**השפעה:**
- 6 טסטים מסתמכים על הערך הזה
- אין אישור מהצוות שזה הערך הנכון

**קישור לקוד:**
```
src/utils/validators.py
Line 395: max_change_percent: float = 50.0
```

---

## 🔴 **2. Performance Thresholds - TODO Comments**

### 📍 **מיקום:** `tests/integration/performance/test_performance_high_priority.py:140-170`

```python
def test_p95_p99_latency_post_config(self, focus_server_api):
    """Test PZ-13770: P95/P99 latency for POST /config"""
    
    # ... test code ...
    
    # TODO: Update thresholds after specs meeting
    # For now, use reasonable defaults for high-performance API
    THRESHOLD_P95_MS = 500   # 500ms for P95  ❌ אין specs!
    THRESHOLD_P99_MS = 1000  # 1000ms for P99  ❌ אין specs!
    MAX_ERROR_RATE = 0.05    # 5% error rate     ❌ אין specs!
    
    # Assertions
    error_rate = errors / num_requests
    assert error_rate <= MAX_ERROR_RATE
    
    # TODO: Uncomment after specs meeting
    # assert p95 < THRESHOLD_P95_MS   ❌ מושבת!
    # assert p99 < THRESHOLD_P99_MS   ❌ מושבת!
    
    # For now, just log warning if exceeds reasonable thresholds
    if p95 >= THRESHOLD_P95_MS:
        logger.warning(f"⚠️ P95 latency {p95:.2f}ms >= {THRESHOLD_P95_MS}ms (would fail if enforced)")
```

**הבעיה:**
- ✅ הטסט קיים
- ❌ ה-assertions **מושבתות** כי אין specs!
- ❌ רק מזהירים במקום לכשל

**השפעה:**
- 28 performance tests ללא thresholds
- אי אפשר לזהות degradation

**קישורים לקוד:**
```
tests/integration/performance/test_performance_high_priority.py
Line 146: # TODO: Update thresholds after specs meeting
Line 148: THRESHOLD_P95_MS = 500   # ❌ No official spec
Line 149: THRESHOLD_P99_MS = 1000  # ❌ No official spec
Line 157: # TODO: Uncomment after specs meeting
Line 158-162: assertions commented out!
```

---

## 🔴 **3. API Response Time - TODO Comments**

### 📍 **מיקום:** `tests/integration/api/test_api_endpoints_high_priority.py:135-147`

```python
def test_get_channels_endpoint_response_time(self, focus_server_api):
    """Test PZ-13419.1: GET /channels response time"""
    
    start_time = time.time()
    channels = focus_server_api.get_channels()
    end_time = time.time()
    
    response_time_ms = (end_time - start_time) * 1000
    
    logger.info(f"Response time: {response_time_ms:.2f}ms")
    
    # TODO: Update threshold after specs meeting
    # For now, use 1000ms as reasonable threshold
    MAX_RESPONSE_TIME_MS = 1000  # ❌ אין specs!
    
    assert response_time_ms < MAX_RESPONSE_TIME_MS
```

**הבעיה:**
- ערך "סביר" (`1000ms`) אבל לא מבוסס spec
- מה אם הצוות רוצה 200ms? או 3000ms?

**קישור לקוד:**
```
tests/integration/api/test_api_endpoints_high_priority.py
Line 140: # TODO: Update threshold after specs meeting
Line 142: MAX_RESPONSE_TIME_MS = 1000  # ❌ Arbitrary value
```

---

## 🔴 **4. Frequency Range - מקבל ערכים שליליים!**

### 📍 **מיקום:** `src/utils/validators.py:153-191`

```python
def validate_frequency_range(min_freq: int, max_freq: int, prr: float) -> bool:
    """Validate frequency range against pulse repetition rate."""
    
    if not isinstance(min_freq, int) or not isinstance(max_freq, int):
        raise ValidationError("Frequency values must be integers")
    
    if min_freq < 0 or max_freq < 0:
        raise ValidationError("Frequency values must be non-negative")
    
    # ✅ יש check שזה לא שלילי
    # ❌ אבל אין check למקסימום!
    # ❌ אין check לטווח מינימלי!
```

**אבל בפועל בmodels:**
```python
# src/models/focus_server_models.py:46-57
class FrequencyRange(BaseModel):
    """Frequency range configuration."""
    min: int = Field(..., description="Minimum frequency required", ge=0)  # ✅ >= 0
    max: int = Field(..., description="Maximum frequency required", ge=0)  # ✅ >= 0
    
    @field_validator('max')
    @classmethod
    def validate_frequency_range(cls, v: int, info: ValidationInfo) -> int:
        if info.data.get('min') and v < info.data['min']:
            raise ValueError('max frequency must be >= min frequency')
        return v
    
    # ❌ אין בדיקה למקסימום אבסולוטי!
    # ❌ אין בדיקה לטווח מינימלי!
```

**הבעיה:**
- אין מקסימום frequency מוגדר
- אין טווח מינימלי מוגדר
- מה אם מישהו שולח `{"min": 0, "max": 999999}`?

**קישורים לקוד:**
```
src/utils/validators.py
Line 174: if min_freq < 0 or max_freq < 0  # Check for negative
Line 177-180: if max_freq <= min_freq       # Check order
Line 182-189: Nyquist check                 # Check PRR
❌ No absolute max check!
❌ No minimum range check!

src/models/focus_server_models.py
Line 48: min: int = Field(..., ge=0)  # Only >= 0
Line 49: max: int = Field(..., ge=0)  # Only >= 0
❌ No upper limit!
```

---

## 🔴 **5. NFFT - מקבל כל ערך!**

### 📍 **מיקום:** `src/utils/validators.py:194-227`

```python
def validate_nfft_value(nfft: int) -> bool:
    """Validate NFFT value (should be power of 2 for efficiency)."""
    
    if not isinstance(nfft, int):
        raise ValidationError("NFFT must be an integer")
    
    if nfft <= 0:
        raise ValidationError("NFFT must be positive")
    
    # Check if power of 2 (for efficiency)
    is_power_of_2 = (nfft & (nfft - 1)) == 0
    
    if not is_power_of_2:
        import warnings
        warnings.warn(
            f"NFFT={nfft} is not a power of 2. Performance may be suboptimal."
        )  # ❌ רק אזהרה! לא דוחה!
    
    return True  # ✅ תמיד מחזיר True!
```

**הבעיה:**
- ✅ בודק שזה חיובי
- ⚠️ מזהיר אם לא power of 2
- ❌ **לא דוחה** ערכים לא חוקיים!
- ❌ אין מקסימום!
- ❌ אין רשימה של ערכים חוקיים!

**דוגמה:**
```python
validate_nfft_value(1000)     # ⚠️ Warning, אבל עובר!
validate_nfft_value(999999)   # ⚠️ Warning, אבל עובר!
validate_nfft_value(-100)     # ❌ נדחה (שלילי)
```

**אבל בconfig המערכת:**
```yaml
# config/environments.yaml (new_production)
nfft:
  default: 1024
  valid_values:
    - 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536
```

**הבעיה:** הקוד לא אוכף את הרשימה!

**קישורים לקוד:**
```
src/utils/validators.py
Line 213: if nfft <= 0  # Only checks positive
Line 217: is_power_of_2 = ...  # Soft check
Line 219-224: warnings.warn()  # ❌ Just warns, doesn't reject!

config/environments.yaml
Line 31-41: valid_values list exists
❌ But code doesn't use it!
```

---

## 🔴 **6. Sensor Range - אין גבול מקסימלי!**

### 📍 **מיקום:** `src/utils/validators.py:116-151`

```python
def validate_sensor_range(min_sensor: int, max_sensor: int, total_sensors: int) -> bool:
    """Validate sensor range against total available sensors."""
    
    if min_sensor < 0 or max_sensor < 0:
        raise ValidationError("Sensor indices must be non-negative")
    
    if max_sensor <= min_sensor:
        raise ValidationError(
            f"max_sensor ({max_sensor}) must be > min_sensor ({min_sensor})"
        )
    
    if max_sensor >= total_sensors:
        raise ValidationError(
            f"max_sensor ({max_sensor}) exceeds total sensors ({total_sensors})"
        )
    
    # ❌ אין בדיקה לטווח מינימלי!
    # ❌ מה אם sensors_min=0, sensors_max=1? (רק סנסור אחד!)
    
    return True
```

**הבעיה:**
- אין טווח מינימלי (למשל: לפחות 10 sensors)
- אין טווח מקסימלי (למשל: מקסימום 1000 sensors)

**בconfig המערכת:**
```yaml
# config/environments.yaml (new_production)
constraints:
  sensors:
    total_range: 2222           # מקסימום מוחלט
    default_start: 11           # ברירת מחדל
    default_end: 109            # ברירת מחדל
    # ❌ אין min_roi_size
    # ❌ אין max_roi_size
```

**קישורים לקוד:**
```
src/utils/validators.py
Line 137: if min_sensor < 0  # Check non-negative
Line 140-143: if max_sensor <= min_sensor  # Check order
Line 145-148: if max_sensor >= total_sensors  # Check total
❌ No minimum ROI size check!
❌ No maximum ROI size check!

config/environments.yaml
Line 24: total_range: 2222
❌ No min_roi_size defined
❌ No max_roi_size defined
```

---

## 🔴 **7. Configuration Validation - TODO Comments**

### 📍 **מיקום:** `tests/integration/api/test_config_validation_high_priority.py:475-520`

```python
def test_frequency_range_equal_min_max(self, focus_server_api, valid_config_payload):
    """Test PZ-13876.1: frequency range where min == max."""
    
    task_id = generate_task_id("freq_range_equal")
    logger.info(f"Test PZ-13876.1: frequency min == max - {task_id}")
    
    # Set frequency range with min == max
    config_payload = valid_config_payload.copy()
    config_payload["frequencyRange"] = {"min": 100, "max": 100}  # Edge case
    
    try:
        config_request = ConfigTaskRequest(**config_payload)
        response = focus_server_api.config_task(task_id, config_request)
        
        # Behavior depends on specs - document what happens
        logger.info(f"Frequency range min==max: status_code={response.status_code}")
        
        # TODO: Update assertion after specs meeting
        # For now, just log the behavior  ❌ אין assertion!
        
    except ValueError as e:
        logger.info(f"Validation rejects min==max: {e}")
```

**הבעיה:**
- הטסט רץ אבל **לא בודק כלום**!
- אין spec האם `min==max` זה חוקי או לא

**עוד דוגמה מאותו קובץ:**
```python
# Line 506-520
def test_channel_range_equal_min_max(self, focus_server_api, valid_config_payload):
    """Test PZ-13876.2: channels where min == max."""
    
    config_payload["channels"] = {"min": 7, "max": 7}  # Edge case
    
    # TODO: Update assertion after specs meeting  ❌ אין assertion!
```

**קישורים לקוד:**
```
tests/integration/api/test_config_validation_high_priority.py
Line 481: # TODO: Update assertion after specs meeting
Line 517: # TODO: Update assertion after specs meeting
❌ Tests exist but no assertions!
```

---

## 🔴 **8. Polling - אין timeout מוגדר!**

### 📍 **מיקום:** `src/utils/helpers.py:474-504`

```python
def poll_until(
    condition_func,
    timeout_seconds: int = 60,      # ❌ Hardcoded default
    poll_interval: float = 1.0      # ❌ Hardcoded default
):
    """
    Poll a condition until it returns True or timeout occurs.
    """
    start_time = time.time()
    
    while True:
        if condition_func():
            return True
        
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Condition not met after {elapsed:.2f}s")
        
        time.sleep(poll_interval)
```

**הבעיה:**
- `timeout_seconds = 60` - hardcoded, אין spec!
- `poll_interval = 1.0` - hardcoded, אין spec!
- מה אם צריך polling אחר לlive vs historic?

**קישור לקוד:**
```
src/utils/helpers.py
Line 474: timeout_seconds: int = 60  # ❌ Hardcoded
Line 474: poll_interval: float = 1.0  # ❌ Hardcoded
❌ No separate specs for live vs historic
```

---

## 🔴 **9. Default Config Values - אין specs!**

### 📍 **מיקום:** `src/utils/helpers.py:507-532`

```python
def generate_config_payload(
    sensors_min: int = 0,          # ❌ אין spec!
    sensors_max: int = 100,        # ❌ אין spec!
    freq_min: int = 0,             # ❌ אין spec!
    freq_max: int = 500,           # ❌ אין spec!
    nfft: int = 1024,              # ✅ יש בconfig
    canvas_height: int = 1000,     # ❌ אין spec!
    live: bool = True,
    # ... more params ...
) -> Dict[str, Any]:
    """Generate test configuration payload with defaults."""
```

**השוואה לconfig המערכת:**
```yaml
# config/environments.yaml (new_production)
constraints:
  sensors:
    default_start: 11     # ❌ הקוד משתמש ב-0!
    default_end: 109      # ❌ הקוד משתמש ב-100!
  frequency:
    start_hz: 0           # ✅ תואם
    end_hz: 1000          # ❌ הקוד משתמש ב-500!

nfft:
  default: 1024           # ✅ תואם

defaults:
  waterfall:
    num_lines: 200        # ❌ הקוד לא משתמש בזה!
```

**הבעיה:**
- אי התאמה בין defaults בקוד לconfig
- חלק מהdefaults לא מגיעים מspecs

**קישורים לקוד:**
```
src/utils/helpers.py
Line 508: sensors_min: int = 0        # ≠ config (11)
Line 509: sensors_max: int = 100      # ≠ config (109)
Line 511: freq_max: int = 500         # ≠ config (1000)
Line 513: canvas_height: int = 1000   # ❌ No spec

config/environments.yaml
Line 25: default_start: 11
Line 26: default_end: 109
Line 19: end_hz: 1000
❌ Code doesn't use config values!
```

---

## 🔴 **10. MongoDB Outage - אין spec מה צפוי!**

### 📍 **מיקום:** הטסטים נכשלים כי אין spec

**מהתוצאות:**
```
FAILED tests/integration/performance/test_mongodb_outage_resilience.py::
TestMongoDBOutageResilience::test_mongodb_scale_down_outage_returns_503

AssertionError: Response time 15.423s exceeds maximum 5.0s
```

**שאלות ללא תשובה:**
- מה הסטטוס HTTP שצריך לחזור כשMongoDB down?
- כמה זמן מקסימלי המערכת יכולה להיות לא responsive?
- האם צריך להמשיך לקבל live data?
- האם צריך caching?

**אין spec בקוד!**

---

## 📊 **סיכום: מיקומי הבעיות בקוד**

### קבצי Core שחסרים בהם Specs:

| קובץ | בעיות | שורות |
|------|-------|-------|
| `src/utils/validators.py` | ROI 50%, Frequency max, NFFT list, Sensor range | 395, 174, 213, 140 |
| `src/utils/helpers.py` | Polling timeouts, Default values | 474, 508-513 |
| `src/models/focus_server_models.py` | No max limits in validation | 48-49 |
| `tests/integration/performance/*.py` | 11 TODO comments | Multiple |
| `tests/integration/api/*.py` | Assertions disabled/missing | Multiple |

---

## 🎯 **איך להשתמש במסמך הזה בפגישה**

### בslide/מצגת:
1. **הראה את הקוד** - העתק את הדוגמאות עם הcomments האדומים
2. **הראה את ה-TODO** - 11 מקומות עם "TODO: Update after specs meeting"
3. **הראה את הassertions המושבתות** - Line 157-162 בperformance tests
4. **הראה את האי-התאמה** - Code defaults ≠ Config values

### בדיון:
- **לכל spec חסר** - הראה את השורה המדויקת בקוד
- **הדגש** - זה לא theoretical, זה בקוד **ממש עכשיו**!
- **הסבר** - למה זה blocking את האוטומציה

---

## 📋 **Quick Reference: מיקומים מדויקים**

### 1️⃣ ROI 50%:
```
src/utils/validators.py:395
max_change_percent: float = 50.0
```

### 2️⃣ Performance thresholds:
```
tests/integration/performance/test_performance_high_priority.py:146-170
THRESHOLD_P95_MS = 500
THRESHOLD_P99_MS = 1000
# Assertions commented out!
```

### 3️⃣ NFFT validation:
```
src/utils/validators.py:219-224
warnings.warn() # Only warns, doesn't reject!
```

### 4️⃣ TODO comments:
```
grep -r "TODO.*spec" tests/
→ 11 matches!
```

### 5️⃣ Frequency max:
```
src/models/focus_server_models.py:48-49
min: int = Field(..., ge=0)  # No max!
max: int = Field(..., ge=0)  # No max!
```

---

