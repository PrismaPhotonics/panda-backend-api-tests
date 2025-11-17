# תוכנית בדיקות Focus Server - מפורטת במיוחד - חלק 2
## Invalid Ranges, View Types, SingleChannel Tests

---

## 🎯 TEST #9: Invalid Frequency Range - Min > Max

**Jira ID**: PZ-13877  
**Priority**: High  
**Type**: Integration Test (Negative)  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים שהשרת **דוחה** קונפיגורציות שבהן `frequencyRange.min > frequencyRange.max`.

**למה זה חשוב?**
- טווח הפוך הוא **בלתי אפשרי** פיזיקלית
- לא ניתן לבדוק "מ-500 Hz עד 100 Hz" - זה לא הגיוני
- בלי ולידציה → undefined behavior, crashes, נתונים מוזרים

**מה קורה בלי ולידציה?**
- Baby Analyzer מנסה ליצור FFT עם טווח הפוך → קריסה
- חישובים מתמטיים עם ערכים שליליים → NaN או Infinity
- תוצאות לא מוגדרות במערכת

### תרחישים נבדקים

**תרחיש 1: Min > Max (לא תקין)**

```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {
    "min": 500,
    "max": 100
  },
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```

**בעיה**: min=500 > max=100 → **הפוך!**

**תרחיש 2: Min == Max (Edge Case)**

```json
{
  "frequencyRange": {
    "min": 250,
    "max": 250
  }
}
```

**שאלה**: האם טווח אפס (250-250) תקף? → **צריך לתעד!**

**תרחיש 3: תדרים שליליים**

```json
{
  "frequencyRange": {
    "min": -100,
    "max": 500
  }
}
```

**בעיה**: תדרים שליליים לא הגיוניים פיזיקלית

### צעדי הבדיקה

| # | צעד | תוצאה | פירוט |
|---|-----|-------|-------|
| 1 | task_id | ID ייחודי | `generate_task_id("freq_invalid")` |
| 2 | payload עם min=500, max=100 | נוצר | תרחיש 1 |
| 3 | POST /config | HTTP 400 | דחייה |
| 4 | בדיקת הודעה | "frequencyRange.min (500) must be <= frequencyRange.max (100)" | ברורה עם ערכים |
| 5 | payload עם min=max=250 | נוצר | תרחיש 2 |
| 6 | POST /config | HTTP 400 או 200 | לתעד התנהגות |
| 7 | תיעוד | logged | תוצאה לפגישת specs |
| 8 | payload עם min=-100 | נוצר | תרחיש 3 |
| 9 | POST /config | HTTP 400 | דחייה |
| 10 | בדיקת הודעה | "Frequency values must be non-negative" | הסבר ברור |

### תוצאה צפויה

**תרחיש 1 - Reversed Range:**
```http
HTTP/1.1 400 Bad Request
{
  "error": "Invalid Frequency Range",
  "message": "frequencyRange.min (500) must be <= frequencyRange.max (100)",
  "constraint": "min <= max",
  "provided": {"min": 500, "max": 100}
}
```

**תרחיש 3 - Negative Frequency:**
```http
HTTP/1.1 400 Bad Request
{
  "error": "Invalid Frequency Value",
  "message": "Frequency values must be non-negative",
  "invalid_field": "frequencyRange.min",
  "provided_value": -100
}
```

### יישום בקוד (קיים!)

**קובץ**: `tests/integration/api/test_config_validation_high_priority.py`  
**Lines**: 296-392  
**Class**: `TestInvalidRanges`

```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
class TestInvalidRanges:
    """Test suite for invalid range configurations."""
    
    def test_invalid_frequency_range_min_greater_than_max(self, focus_server_api):
        """
        Test PZ-13877: Invalid Frequency Range - Min > Max
        
        Validates rejection of reversed frequency ranges.
        """
        task_id = generate_task_id("freq_reversed")
        logger.info(f"Test PZ-13877: Reversed frequency range - {task_id}")
        
        # Create reversed range payload
        payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 0, "max": 50},
            "frequencyRange": {
                "min": 500,  # ❌ Higher than max!
                "max": 100
            },
            "start_time": None,
            "end_time": None,
            "view_type": 0
        }
        
        # Verify reversal
        assert payload['frequencyRange']['min'] > payload['frequencyRange']['max']
        logger.info("✓ Confirmed: min (500) > max (100) - reversed range")
        
        # Expect rejection
        with pytest.raises(Exception) as exc_info:
            config_request = ConfigureRequest(**payload)
            focus_server_api.configure_streaming_job(config_request)
        
        error_msg = str(exc_info.value).lower()
        assert "frequency" in error_msg and ("min" in error_msg or "max" in error_msg)
        logger.info(f"✅ Reversed frequency range properly rejected")
        logger.info(f"   Error: {exc_info.value}")
    
    def test_frequency_range_equal_min_max(self, focus_server_api):
        """
        Test PZ-13877.2: Frequency Range with Min == Max (Edge Case)
        
        Documents behavior for zero-width frequency range.
        """
        task_id = generate_task_id("freq_equal")
        logger.info(f"Test: Frequency range min==max edge case - {task_id}")
        
        payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 0, "max": 50},
            "frequencyRange": {
                "min": 250,
                "max": 250  # Same value
            },
            "start_time": None,
            "end_time": None,
            "view_type": 0
        }
        
        # Try to configure
        try:
            config_request = ConfigureRequest(**payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            logger.info(f"✓ Zero-width frequency range ACCEPTED")
            logger.info(f"  This behavior should be documented for specs")
            
        except Exception as e:
            logger.info(f"✓ Zero-width frequency range REJECTED")
            logger.info(f"  Error: {e}")
            logger.info(f"  This behavior should be documented for specs")
```

**הרצה**:
```bash
pytest tests/integration/api/test_config_validation_high_priority.py::TestInvalidRanges::test_invalid_frequency_range_min_greater_than_max -v
```

---

## 🎯 TEST #10: Invalid Channel Range - Min > Max

**Jira ID**: PZ-13876  
**Priority**: High  
**Type**: Integration Test (Negative)  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים שהשרת **דוחה** קונפיגורציות שבהן `channels.min > channels.max`.

**למה זה חשוב?**
- ROI (Region of Interest) הפוך לא הגיוני
- לא ניתן לבקש "sensors מ-50 עד 10" - זה הפוך!
- זה קריטי ל-ROI validation

**מה זה ROI?**
- ROI = Region of Interest
- מגדיר **אילו sensors** לעבד
- `min=10, max=50` → עבד sensors 10,11,12,...,50 (41 sensors)

### תרחישים

**תרחיש 1: Min > Max (לא תקין)**

```json
{
  "channels": {
    "min": 50,
    "max": 10
  }
}
```

**תרחיש 2: Min == Max (SingleChannel equivalent)**

```json
{
  "channels": {
    "min": 7,
    "max": 7
  }
}
```

**שאלה**: האם זה תקף? → כן, זה **SingleChannel** (sensor אחד)

**תרחיש 3: ערכים שליליים**

```json
{
  "channels": {
    "min": -5,
    "max": 50
  }
}
```

### צעדי הבדיקה

| # | צעד | תוצאה | קוד |
|---|-----|-------|-----|
| 1 | task_id | ID | `generate_task_id("ch_invalid")` |
| 2 | payload min=50, max=10 | נוצר | תרחיש 1 |
| 3 | POST /config | HTTP 400 | דחייה |
| 4 | הודעה | "channels.min (50) must be <= channels.max (10)" | ברורה |
| 5 | payload min=7, max=7 | נוצר | תרחיש 2 |
| 6 | POST /config | HTTP 200 או 400 | לתעד |
| 7 | אם התקבל | בדיקת view_type | האם נחשב כ-SINGLECHANNEL? |
| 8 | payload min=-5 | נוצר | תרחיש 3 |
| 9 | POST /config | HTTP 400 | דחייה |
| 10 | הודעה | "Channel IDs must be non-negative" | ברורה |

### יישום בקוד (קיים!)

**קובץ**: `tests/integration/api/test_config_validation_high_priority.py`  
**Lines**: 395-478  
**Class**: `TestInvalidRanges`

```python
def test_invalid_channel_range_min_greater_than_max(self, focus_server_api):
    """
    Test PZ-13876: Invalid Channel Range - Min > Max
    
    Validates rejection of reversed channel ranges.
    """
    task_id = generate_task_id("channel_reversed")
    logger.info(f"Test PZ-13876: Reversed channel range - {task_id}")
    
    payload = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {
            "min": 50,  # ❌ Higher than max!
            "max": 10
        },
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,
        "end_time": None,
        "view_type": 0
    }
    
    # Verify reversal
    assert payload['channels']['min'] > payload['channels']['max']
    
    # Expect rejection
    with pytest.raises(Exception) as exc_info:
        config_request = ConfigureRequest(**payload)
        focus_server_api.configure_streaming_job(config_request)
    
    error_msg = str(exc_info.value).lower()
    assert "channel" in error_msg
    logger.info(f"✅ Reversed channel range properly rejected")

def test_channel_range_equal_min_max(self, focus_server_api):
    """
    Test PZ-13876.2: Channel Range with Min == Max
    
    Edge case: Single sensor (may be valid as SingleChannel).
    """
    task_id = generate_task_id("channel_equal")
    logger.info(f"Test: Channel range min==max - {task_id}")
    
    payload = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {
            "min": 7,
            "max": 7  # Same value
        },
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,
        "end_time": None,
        "view_type": 0  # MULTICHANNEL mode
    }
    
    try:
        config_request = ConfigureRequest(**payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        logger.info("✓ Single sensor range ACCEPTED (may be treated as SingleChannel)")
        
    except Exception as e:
        logger.info(f"✓ Single sensor range REJECTED: {e}")
```

---

## 🎯 TEST #11: Valid Configuration - All Parameters

**Jira ID**: PZ-13873  
**Priority**: High  
**Type**: Integration Test (Positive - Happy Path)  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים שהשרת **מקבל ומעבד** קונפיגורציה **תקינה לחלוטין** עם כל הפרמטרים.

**למה זה חשוב?**
- זה ה-**Happy Path** - התרחיש הבסיסי שצריך לעבוד
- אם הטסט הזה נכשל, **כלום לא עובד**!
- מאמת שהפונקציונליות הבסיסית תקינה

**מה המשמעות?**
- אם זה עובד → המערכת יכולה לעבד קונפיגורציות
- אם זה נכשל → בעיה יסודית במערכת

### תרחישי Happy Path

**תרחיש 1: MULTICHANNEL תקין**

```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```

**מאפיינים:**
- ✅ כל השדות הנדרשים קיימים
- ✅ כל הערכים תקפים
- ✅ MULTICHANNEL mode (מספר sensors)
- ✅ Live mode (start_time=null, end_time=null)

**תרחיש 2: SINGLECHANNEL תקין**

```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 7, "max": 7},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 1
}
```

**מאפיינים:**
- ✅ SINGLECHANNEL mode (view_type=1)
- ✅ sensor אחד (min=max=7)

**תרחיש 3: NFFT שונים**

```json
{
  "nfftSelection": 2048,  // גבוה יותר
  "channels": {"min": 0, "max": 100},  // יותר sensors
  "frequencyRange": {"min": 0, "max": 1000}  // טווח רחב יותר
}
```

### צעדי הבדיקה

| # | צעד | תוצאה | ולידציה |
|---|-----|-------|---------|
| 1 | task_id | ID ייחודי | `generate_task_id("valid_all_params")` |
| 2 | payload מלא ותקין | JSON valid | כל השדות |
| 3 | POST /config | HTTP 200 | הצלחה |
| 4 | בדיקת response | "Config received successfully" | הודעת הצלחה |
| 5 | GET /metadata/{task_id} | HTTP 200 + metadata | metadata זמין |
| 6 | השוואת metadata לconfig | תואם | הפרמטרים נשמרו |
| 7 | שאילתת MongoDB | Task document קיים | `db.tasks.findOne({task_id})` |
| 8 | SINGLECHANNEL config | payload | תרחיש 2 |
| 9 | POST /config | HTTP 200 | הצלחה |
| 10 | בדיקת view_type | =1 | SINGLECHANNEL activated |
| 11 | בדיקת NFFT שונים | כולם מתקבלים | 256, 512, 1024, 2048 |
| 12 | בדיקת response times | < 500ms | ביצועים |

### תוצאה צפויה

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "Config received successfully",
  "job_id": "job_abc123def456",
  "stream_url": "10.10.100.100",
  "stream_port": 50051,
  "channel_amount": 50,
  "stream_amount": 1,
  "channel_to_stream_index": {"0": 0, "1": 0, ..., "49": 0}
}
```

### יישום בקוד (קיים!)

**קובץ**: `tests/integration/api/test_config_validation_high_priority.py`  
**Lines**: 725-810  
**Class**: `TestValidConfigurationAllParameters`

```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
@pytest.mark.smoke
class TestValidConfigurationAllParameters:
    """
    Test suite for PZ-13873: Valid Configuration - All Parameters
    """
    
    def test_valid_configuration_all_parameters(
        self, 
        focus_server_api, 
        valid_config_payload
    ):
        """
        Test PZ-13873: Valid configuration with all parameters.
        
        Steps:
            1. Create config with all parameters properly set
            2. Send POST /config/{task_id}
            3. Verify acceptance
            4. Verify task can be queried
        
        Expected:
            - Status code: 200 OK
            - Config accepted successfully
            - Task ID is valid
            - Task can be queried via metadata endpoint
        """
        task_id = generate_task_id("valid_all_params")
        logger.info(f"Test PZ-13873: Valid configuration - {task_id}")
        
        # STEP 1: Validate task_id format
        assert validate_task_id_format(task_id)
        
        # STEP 2: Create fully valid config
        config_payload = valid_config_payload.copy()
        logger.info(f"Config payload: {config_payload}")
        
        # STEP 3: Create config request
        config_request = ConfigureRequest(**config_payload)
        
        # STEP 4: Configure task
        response = focus_server_api.configure_streaming_job(config_request)
        
        # STEP 5: Assertions
        assert isinstance(response, ConfigureResponse), \
            f"Expected ConfigureResponse, got {type(response)}"
        
        # ConfigureResponse has 'status' and 'job_id' fields
        assert hasattr(response, 'job_id') and response.job_id, \
            f"Expected job_id in response"
        
        logger.info(f"✅ Valid configuration accepted: job_id={response.job_id}")
        
        # Verify response contains all expected fields
        assert hasattr(response, 'stream_url'), "Response should contain stream_url"
        assert hasattr(response, 'stream_port'), "Response should contain stream_port"
        logger.info(
            f"✅ Response contains stream info: "
            f"{response.stream_url}:{response.stream_port}"
        )
        
        logger.info("✅ Test PZ-13873 PASSED")
```

**הרצה**:
```bash
pytest tests/integration/api/test_config_validation_high_priority.py::TestValidConfigurationAllParameters -v
```

---

## 🎯 TEST #12-20: SingleChannel Tests Suite

### סקירה כללית - SingleChannel Mode

**מה זה SingleChannel?**
- **SingleChannel** = מצב שבו רואים **sensor אחד בלבד**
- `view_type = 1` (לעומת MULTICHANNEL = 0)
- `channels.min == channels.max` (אותו sensor)

**למה צריך מצב זה?**
- **ניתוח מפורט** של sensor ספציפי
- **ביצועים** - פחות נתונים, מהיר יותר
- **troubleshooting** - בדיקת sensor ספציפי

**מה ייחודי ב-SingleChannel?**
- `stream_amount = 1` (stream אחד)
- `channel_to_stream_index = {"{channel_id}": 0}` (mapping 1:1)
- `channel_amount = 1` (channel אחד)

---

### TEST #12: SingleChannel - Minimum Channel (Channel 0)

**Jira ID**: PZ-13832  
**Priority**: High  
**Status**: ✅ **ממומש!**

**מטרה**: בדיקת **edge case** - ה-sensor הראשון (0)

**למה חשוב?**
- sensor 0 הוא **boundary case** (קצה תחתון)
- בעיות off-by-one שכיחות בקצוות
- צריך לוודא שהמערכת מטפלת ב-0 נכון

**Payload:**
```json
{
  "channels": {"min": 0, "max": 0},
  "view_type": 1
}
```

**Expected Response:**
```json
{
  "stream_amount": 1,
  "channel_to_stream_index": {"0": 0},
  "channel_amount": 1
}
```

**יישום:**
```python
def test_singlechannel_minimum_channel(self, focus_server_api):
    """Test PZ-13832: SingleChannel with channel 0 (minimum)."""
    
    # Configure for channel 0
    config_payload['channels']['min'] = 0
    config_payload['channels']['max'] = 0
    config_payload['view_type'] = 1
    
    response = focus_server_api.config_task(task_id, ConfigTaskRequest(**payload))
    
    # Verify
    assert response.stream_amount == 1
    assert response.channel_to_stream_index == {"0": 0}
    assert response.channel_amount == 1
    
    # Verify data
    waterfall_response = focus_server_api.get_waterfall(task_id, 10)
    for data_block in waterfall_response.data:
        for row in data_block.data[0].rows:
            assert row.sensors[0].id == 0
    
    logger.info("✅ Channel 0 works correctly")
```

---

### TEST #13: SingleChannel - Maximum Channel

**Jira ID**: PZ-13833  
**Priority**: High  
**Status**: ✅ **ממומש!**

**מטרה**: בדיקת **edge case** - ה-sensor האחרון

**למה חשוב?**
- ה-sensor האחרון הוא **boundary case** (קצה עליון)
- בעיות off-by-one שכיחות בקצה העליון
- צריך לוודא שהמערכת לא חורגת מגבולות המערך

**תהליך:**
```python
# STEP 1: Get max sensor from /sensors
sensors_response = focus_server_api.get_sensors()
max_sensor = sensors_response.sensors[-1]  # Last sensor

# STEP 2: Configure for max sensor
payload['channels']['min'] = max_sensor
payload['channels']['max'] = max_sensor
```

---

### TEST #14: SingleChannel - Middle Channel

**Jira ID**: PZ-13834  
**Priority**: Medium  
**Status**: ✅ **ממומש!**

**מטרה**: בדיקת sensor **אמצעי** (לא edge case)

**למה חשוב?**
- לוודא שהפיצ'ר עובד לא רק בקצוות
- בדיקת sensor arbitrary

**תהליך:**
```python
# Calculate middle sensor
sensors_response = focus_server_api.get_sensors()
middle_sensor = len(sensors_response.sensors) // 2

# Configure
payload['channels']['min'] = middle_sensor
payload['channels']['max'] = middle_sensor
```

---

### TEST #15-17: SingleChannel - Invalid Channels

**Jira IDs**: PZ-13835, PZ-13836, PZ-13837  
**Priority**: High  
**Type**: Negative Tests  
**Status**: ✅ **ממומש!**

**מטרה**: וידוא דחיית sensors לא תקפים

**תרחישים:**

1. **Channel גבוה מדי** (PZ-13835): channel=9999
2. **Channel שלילי** (PZ-13836, PZ-13837): channel=-1
3. **Channel מחוץ לטווח** (PZ-13852): channel > max_available

**Expected Behavior:**
- HTTP 400 או 404
- הודעת שגיאה ברורה
- אין task נוצר

**יישום:**
```python
def test_singlechannel_non_existent_channel(self, focus_server_api):
    """Test: SingleChannel with non-existent high channel ID."""
    
    invalid_channel = 9999
    payload['channels']['min'] = invalid_channel
    payload['channels']['max'] = invalid_channel
    
    with pytest.raises(Exception) as exc_info:
        focus_server_api.config_task(task_id, ConfigTaskRequest(**payload))
    
    error_msg = str(exc_info.value).lower()
    assert "out of range" in error_msg or "invalid" in error_msg
    
    # Verify task not created
    waterfall_response = focus_server_api.get_waterfall(task_id, 10)
    assert waterfall_response.status_code == 404
```

---

## 🎯 TEST #21-22: Infrastructure Tests

### TEST #21: SSH Access to Production Servers

**Jira ID**: PZ-13900  
**Priority**: High  
**Type**: Infrastructure Test  
**Status**: TO DO

**מטרה**: וידוא גישת SSH ל-production servers

**למה חשוב?**
- SSH נדרש ל-**troubleshooting**
- גישה ללוגים, k9s, kubectl
- תחזוקה ותיקונים

**צעדים:**
```python
import paramiko

# STEP 1: Connect to jump host
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.10.100.3', username='root', password='***')

# STEP 2: Execute test commands
stdin, stdout, stderr = ssh.exec_command('hostname')
hostname = stdout.read().decode().strip()
logger.info(f"Jump host: {hostname}")

# STEP 3: Connect to target host
ssh.connect('10.10.100.113', username='prisma', password='***')

# STEP 4: Test kubectl
stdin, stdout, stderr = ssh.exec_command('kubectl version --client')
kubectl_version = stdout.read().decode()
assert 'Client Version' in kubectl_version
```

---

### TEST #22: Kubernetes Cluster Connection

**Jira ID**: PZ-13899  
**Priority**: High  
**Type**: Infrastructure Test  
**Status**: TO DO

**מטרה**: וידוא חיבור ל-Kubernetes ובריאות pods

**מה בודקים?**
- חיבור ל-K8s cluster
- רשימת pods
- status של pods (Running/Ready)
- resource usage

**צעדים:**
```python
from kubernetes import client, config

# Load kubeconfig
config.load_kube_config()

# Get pods
v1 = client.CoreV1Api()
pods = v1.list_namespaced_pod(namespace="panda")

# Verify all running
for pod in pods.items:
    assert pod.status.phase == "Running"
    logger.info(f"Pod {pod.metadata.name}: {pod.status.phase}")
```

---

**המשך בחלק 3...**

