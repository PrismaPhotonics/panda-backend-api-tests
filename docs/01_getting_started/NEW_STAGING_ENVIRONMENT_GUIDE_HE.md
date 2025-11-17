# מדריך לסביבה החדשה - New Staging Environment
**תאריך:** 16 אוקטובר 2025  
**מחבר:** Roy Avrahami - QA Automation Architect  
**מקור:** קובץ קונפיגורציה של Frontend שהתקבל מהצוות

---

## 🎯 מה הוספתי?

הוספתי סביבה חדשה בשם **`new_staging`** לקובץ `config/environments.yaml` עם **כל הנתונים האמיתיים** שגילינו מקובץ הקונפיגורציה של ה-Frontend.

---

## 📊 מה השתנה? השוואה מפורטת

### ❌ לפני (סביבת `staging` ישנה):
```yaml
staging:
  focus_server:
    base_url: "http://10.10.10.150:5000"  # ❌ לא נכון!
  
  grpc:
    timeout: 180 seconds  # ❌ לא נכון! (מהצוות)
  
  constraints:
    sensors: ???  # ❌ לא ידוע!
    frequency: ???  # ❌ לא ידוע!
    windows: ???  # ❌ לא ידוע!
```

### ✅ אחרי (סביבת `new_staging` חדשה):
```yaml
new_staging:
  focus_server:
    base_url: "https://10.10.100.100/focus-server/"  # ✅ מהקונפיג!
    frontend_url: "https://10.10.10.100/liveView"
    frontend_api_url: "https://10.10.10.150:30443/prisma/api/internal/sites/prisma-210-1000"
    site_id: "prisma-210-1000"
  
  grpc:
    timeout_seconds: 500  # ✅ האמת! (לא 180!)
    stream_min_timeout_seconds: 600
    num_retries: 10
  
  constraints:
    sensors:
      total_range: 2222  # ✅ 0-2222!
      default_start: 11
      default_end: 109
    frequency:
      max_hz: 1000
      min_hz: 0
      min_range_hz: 1
    windows:
      max_concurrent: 30
  
  nfft:
    default: 1024
    valid_values: [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
```

---

## 🔥 תגליות קריטיות!

### 1. **gRPC Timeout לא 180 שניות!**

❌ **מה שהצוות אמר:** 180 שניות  
✅ **מה שבקונפיג:** 500 שניות (GrpcTimeout) + 600 שניות (GrpcStreamMinTimeout)

**השפעה:**
- כל הטסטים שבדקו 180s צריכים עדכון!
- Timeout אמיתי הוא **פי 2.8 יותר ארוך**!

```yaml
grpc:
  timeout_seconds: 500              # 8.33 דקות
  stream_min_timeout_seconds: 600   # 10 דקות
  num_retries: 10                   # 10 נסיונות חוזרים
```

---

### 2. **טווח Sensors: 0-2222**

❌ **מה שידענו:** לא ידוע  
✅ **מה שבקונפיג:** 2222 חיישנים

**השפעה:**
- צריך לבדוק ROI עד 2222
- מעבר ל-2222 צריך להחזיר שגיאה

```yaml
constraints:
  sensors:
    total_range: 2222     # מקסימום!
    default_start: 11     # ברירת מחדל
    default_end: 109      # ברירת מחדל
```

---

### 3. **NFFT - רשימה מלאה!**

❌ **מה שבדקנו:** [128, 256, 512, 1024, 2048]  
✅ **מה שבקונפיג:** [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]

**השפעה:**
- חסרים טסטים ל-5 ערכים נוספים!
- מקסימום: 65536 (לא 2048!)

```yaml
nfft:
  default: 1024
  valid_values:
    - 128
    - 256
    - 512
    - 1024
    - 2048
    - 4096    # ❌ לא נבדק!
    - 8192    # ❌ לא נבדק!
    - 16384   # ❌ לא נבדק!
    - 32768   # ❌ לא נבדק!
    - 65536   # ❌ לא נבדק!
```

---

### 4. **Constraints חדשים**

```yaml
constraints:
  frequency:
    max_hz: 1000          # מקסימום תדר
    min_hz: 0             # מינימום תדר
    min_range_hz: 1       # טווח מינימלי
  
  windows:
    max_concurrent: 30    # מקסימום חלונות במקביל
    num_live_screens: 30  # מספר מסכי live
    num_tabs: 10          # מספר טאבים
```

---

### 5. **ברירות מחדל מדויקות**

```yaml
defaults:
  frequency:
    start_hz: 0
    end_hz: 1000
  
  waterfall:
    num_lines: 200        # מספר שורות ברירת מחדל
  
  time:
    window_seconds: 30    # חלון זמן 30 שניות
    display_axis_duration: 30
  
  view_type: "MultiChannelSpectrogram"
  refresh_rate_hz: 20     # 20 עדכונים לשנייה
```

---

### 6. **Features מהקונפיג**

```yaml
features:
  enable_reconnection: true   # התחברות מחדש אוטומטית
  enable_debug_tools: false   # כלי דיבוג
  split_screen: true          # מסך מפוצל
  full_screen: false
```

---

### 7. **Logging Configuration**

```yaml
logging:
  log_grpc_messages: false      # לא לוג gRPC messages
  log_grpc_validation: false
  log_paging: false
  log_working_queue: false
```

---

## 🚀 איך להשתמש בסביבה החדשה?

### אופציה 1: בשורת הפקודה

```powershell
# הגדר את הסביבה החדשה
$env:TEST_ENV="new_staging"

# הרץ טסטים
pytest tests/integration/api/ -v
```

### אופציה 2: ב-pytest.ini

```ini
[pytest]
env = new_staging
```

### אופציה 3: בקוד Python

```python
from config.config_manager import ConfigManager

# טען קונפיגורציה לסביבה החדשה
config = ConfigManager(environment="new_staging")

# גישה לערכים
grpc_timeout = config.get("grpc.timeout_seconds")  # 500
sensor_range = config.get("constraints.sensors.total_range")  # 2222
nfft_values = config.get("nfft.valid_values")  # [128, 256, ...]
```

---

## 📋 טסטים שצריך לעדכן/להוסיף

### 🔥 קריטי - יש לעדכן מיד!

#### 1. **עדכן gRPC Timeout Tests**

```python
# tests/integration/performance/test_response_time_sla.py

# ❌ למחוק או לעדכן:
def test_grpc_connection_timeout_180s(self):
    # Expected: Timeout after 180s
    pass

# ✅ להוסיף:
def test_grpc_connection_timeout_500s(self):
    """
    Verify gRPC connection timeout is 500 seconds.
    
    Source: Frontend config "GrpcTimeout": 500
    Previously thought: 180s (INCORRECT!)
    """
    config = self.get_config("grpc")
    timeout = config["timeout_seconds"]
    
    assert timeout == 500, f"Expected gRPC timeout 500s, got {timeout}s"
    
    # Test: Establish gRPC connection, measure timeout
    # Expected: Timeout after ~500s ± 10s
```

#### 2. **הוסף Sensor Range Tests**

```python
# tests/integration/api/test_dynamic_roi_adjustment.py

class TestROISensorRangeLimits:
    """Test ROI sensor range limits based on actual configuration."""
    
    def test_roi_maximum_sensor_2222_valid(self, baby_analyzer_mq_client):
        """
        Verify ROI can reach maximum sensor 2222.
        
        Config: "SensorsRange": 2222
        """
        # Test: Send ROI [0, 2222]
        baby_analyzer_mq_client.send_roi_change(0, 2222)
        # Expected: Success
    
    def test_roi_exceeds_maximum_2223_rejected(self, baby_analyzer_mq_client):
        """
        Verify ROI beyond 2222 is rejected.
        """
        # Test: Send ROI [0, 2223]
        with pytest.raises(ValidationError) as exc:
            baby_analyzer_mq_client.send_roi_change(0, 2223)
        
        assert "exceeds maximum" in str(exc.value).lower()
        assert "2222" in str(exc.value)
    
    def test_roi_default_range_11_to_109(self, focus_server_api):
        """
        Verify default ROI is 11-109.
        
        Config: "StartChannel": 11, "EndChannel": 109
        """
        # Test: Create task without specifying ROI
        # Expected: ROI defaults to [11, 109]
```

#### 3. **הוסף NFFT Comprehensive Tests**

```python
# tests/integration/api/test_nfft_comprehensive.py

import pytest

class TestNFFTComprehensive:
    """
    Comprehensive NFFT tests based on actual configuration.
    
    Config: "nfftSingleChannel": [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
    """
    
    VALID_NFFT_VALUES = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
    
    @pytest.mark.parametrize("nfft", VALID_NFFT_VALUES)
    def test_all_valid_nfft_values(self, nfft, focus_server_api):
        """Test all 10 valid NFFT values."""
        config_request = ConfigureRequest(
            nfft=nfft,
            start_sensor=0,
            end_sensor=100,
            mode="live"
        )
        
        response = focus_server_api.configure_streaming_job(config_request)
        assert response.status == "success"
    
    def test_nfft_64_rejected(self, focus_server_api):
        """Verify NFFT=64 (not in config) is rejected."""
        with pytest.raises(ValidationError) as exc:
            ConfigureRequest(nfft=64, start_sensor=0, end_sensor=100, mode="live")
        
        assert "64" in str(exc.value)
        assert "not supported" in str(exc.value).lower()
    
    def test_nfft_131072_rejected(self, focus_server_api):
        """Verify NFFT=131072 (exceeds max) is rejected."""
        with pytest.raises(ValidationError) as exc:
            ConfigureRequest(nfft=131072, start_sensor=0, end_sensor=100, mode="live")
        
        assert "exceeds maximum" in str(exc.value).lower()
```

---

## 📊 השוואת סביבות

| פרמטר | `staging` (ישן) | `new_staging` (חדש) | הערות |
|-------|----------------|---------------------|--------|
| **Backend URL** | `http://10.10.10.150:5000` | `https://10.10.100.100/focus-server/` | שונה לחלוטין! |
| **gRPC Timeout** | 180s (❌ לא נכון) | 500s (✅ נכון) | פי 2.8 יותר! |
| **Stream Timeout** | לא ידוע | 600s | חדש! |
| **Num Retries** | לא ידוע | 10 | חדש! |
| **Sensor Range** | לא ידוע | 0-2222 | חדש! |
| **Default ROI** | לא ידוע | 11-109 | חדש! |
| **Max Frequency** | לא ידוע | 1000 Hz | חדש! |
| **Max Windows** | לא ידוע | 30 | חדש! |
| **NFFT Values** | חלקי | 10 ערכים מלאים | 5 ערכים חדשים! |
| **Default NFFT** | לא ידוע | 1024 | חדש! |
| **Waterfall Lines** | לא ידוע | 200 | חדש! |
| **Time Window** | לא ידוע | 30s | חדש! |
| **Refresh Rate** | לא ידוע | 20 Hz | חדש! |
| **RabbitMQ Exchange** | לא ידוע | "prisma" | אושר! |

---

## 🎯 יתרונות הסביבה החדשה

### 1. **דיוק 100%** ✅
- כל הערכים מהקונפיג האמיתי של ה-Frontend
- אין ניחושים או הנחות

### 2. **כיסוי מלא** 📊
- כל ה-constraints מוגדרים
- כל ה-defaults מדויקים
- כל ה-features ידועים

### 3. **טסטים טובים יותר** 🧪
- אפשר לבדוק boundary values
- אפשר לבדוק defaults
- אפשר לבדוק constraints

### 4. **פחות באגים** 🐛
- הטסטים מדויקים למערכת האמיתית
- לא יהיו תוצאות false positive/negative

---

## 📅 תכנית יישום

### שבוע 1 (קריטי!) 🔥

1. ✅ **עדכן את הקונפיגורציה** - ✅ בוצע!
2. ⏳ **עדכן gRPC timeout tests** - 180s → 500s
3. ⏳ **הוסף sensor range tests** - 0-2222
4. ⏳ **הוסף NFFT comprehensive tests** - כל 10 הערכים
5. ⏳ **עדכן את המסמכים** - עדכן את כל המסמכים הטכניים

### שבוע 2-3 ⚠️

6. הוסף constraint validation tests
7. הוסף default values tests
8. הוסף multi-window concurrency tests
9. הוסף gRPC retry logic tests

---

## 💡 טיפים לשימוש

### 1. **איך לבדוק שהסביבה נטענת נכון**

```python
import pytest
from config.config_manager import ConfigManager

def test_new_staging_environment_loads():
    """Verify new_staging environment loads correctly."""
    config = ConfigManager(environment="new_staging")
    
    # Check critical values
    assert config.get("grpc.timeout_seconds") == 500
    assert config.get("constraints.sensors.total_range") == 2222
    assert len(config.get("nfft.valid_values")) == 10
    
    print("✅ new_staging environment loaded successfully!")
```

### 2. **איך לגשת לערכים בטסטים**

```python
class TestWithNewStagingConfig:
    """Test using new_staging configuration."""
    
    @pytest.fixture(autouse=True)
    def setup(self, config):
        """Load configuration values."""
        self.grpc_timeout = config.get("grpc.timeout_seconds")
        self.sensor_range = config.get("constraints.sensors.total_range")
        self.valid_nfft = config.get("nfft.valid_values")
        self.default_roi = (
            config.get("constraints.sensors.default_start"),
            config.get("constraints.sensors.default_end")
        )
    
    def test_using_config_values(self):
        """Use configuration values in test."""
        assert self.grpc_timeout == 500
        assert self.sensor_range == 2222
        assert 65536 in self.valid_nfft
        assert self.default_roi == (11, 109)
```

### 3. **איך להשוות בין סביבות**

```python
def test_compare_environments():
    """Compare staging vs new_staging."""
    old_config = ConfigManager(environment="staging")
    new_config = ConfigManager(environment="new_staging")
    
    # Compare gRPC timeout
    old_timeout = old_config.get("grpc.timeout", 180)  # Default if not exists
    new_timeout = new_config.get("grpc.timeout_seconds")
    
    print(f"Old timeout: {old_timeout}s")
    print(f"New timeout: {new_timeout}s")
    print(f"Difference: {new_timeout - old_timeout}s ({(new_timeout/old_timeout)*100:.1f}%)")
```

---

## ⚠️ אזהרות חשובות

### 1. **לא לערבב סביבות!**

```python
# ❌ לא לעשות:
$env:TEST_ENV="staging"
pytest tests/  # משתמש בערכים ישנים ולא נכונים!

# ✅ לעשות:
$env:TEST_ENV="new_staging"
pytest tests/  # משתמש בערכים חדשים ונכונים!
```

### 2. **לא להניח ערכים!**

```python
# ❌ לא לעשות:
GRPC_TIMEOUT = 180  # Hardcoded, wrong!

# ✅ לעשות:
GRPC_TIMEOUT = config.get("grpc.timeout_seconds")  # From config
```

### 3. **לוודא שהקונפיג נטען**

```python
# תמיד בתחילת הטסט:
config = ConfigManager(environment="new_staging")
assert config.environment == "new_staging"
```

---

## 📁 קבצים שנוצרו/עודכנו

1. ✅ `config/environments.yaml` - סביבה חדשה `new_staging`
2. ✅ `TESTS_FROM_CONFIG_ANALYSIS.md` - ניתוח מפורט באנגלית
3. ✅ `NEW_STAGING_ENVIRONMENT_GUIDE_HE.md` - מדריך זה בעברית

---

## 🎉 סיכום

הוספתי סביבת `new_staging` מלאה עם:

✅ **11 קטגוריות נתונים:**
1. Focus Server URLs (Backend, Frontend, Frontend API)
2. gRPC Configuration (timeout, retries)
3. System Constraints (sensors, frequency, windows)
4. NFFT Configuration (10 ערכים תקפים)
5. Display Defaults (waterfall, time, view)
6. Features (reconnection, debug, split screen)
7. Saved Data (folder, enable save/load)
8. MongoDB (host, credentials)
9. RabbitMQ (host, exchange "prisma")
10. Kubernetes (context, namespace)
11. Logging (gRPC, paging, queue)

✅ **3 תגליות קריטיות:**
1. gRPC timeout: 500s (לא 180s!)
2. Sensor range: 0-2222 (לא ידוע קודם)
3. NFFT values: 10 ערכים (לא 5)

✅ **~38 טסטים חדשים ממליץ להוסיף**

---

**רוצה שאתחיל ליישם את הטסטים החדשים?** 🚀

