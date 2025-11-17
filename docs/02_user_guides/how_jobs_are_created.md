# איך נוצרים Jobs במערכת האוטומציה

## 📋 תהליך יצירת Job - סקירה כללית

כאשר רוצים ליצור job חדש במערכת האוטומציה, מתבצע התהליך הבא:

### 1️⃣ **יצירת Task ID**

```python
from src.utils.helpers import generate_task_id

# פונקציה זו מייצרת ID ייחודי לפורמט: {prefix}_{timestamp}_{uuid}
task_id = generate_task_id(prefix="test")
# דוגמה: "test_20251031123456_a1b2c3d4"
```

**קוד הפונקציה** (```455:472:src/utils/helpers.py```):
```python
def generate_task_id(prefix: str = "task") -> str:
    """
    Generate unique task ID.
    
    Args:
        prefix: ID prefix (default: "task")
        
    Returns:
        Unique task ID in format: {prefix}_{timestamp}_{uuid}
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{unique_id}"
```

---

### 2️⃣ **יצירת Configuration Payload**

יש שתי דרכים ליצור payload:

#### א. **Live Mode** (נתונים בזמן אמת)

```python
payload = {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {"height": 1000},
    "channels": {"min": 0, "max": 50},
    "frequencyRange": {"min": 0, "max": 500},
    "start_time": None,      # ✅ Live Mode
    "end_time": None,        # ✅ Live Mode
    "view_type": ViewType.MULTICHANNEL
}
```

#### ב. **Historic Mode** (נתונים מהתיעוד)

```python
payload = {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {"height": 1000},
    "channels": {"min": 0, "max": 50},
    "frequencyRange": {"min": 0, "max": 500},
    "start_time": "251021120000",  # ✅ Historic Mode
    "end_time": "251021120600",    # ✅ Historic Mode
    "view_type": ViewType.MULTICHANNEL
}
```

---

### 3️⃣ **יצירת ConfigureRequest Object**

```python
from src.models.focus_server_models import ConfigureRequest, ConfigureResponse

# יוצרים אובייקט ConfigureRequest מהמודל
config_request = ConfigureRequest(**payload)
```

**המודל** (```22:40:tests/integration/api/test_config_validation_high_priority.py```) כולל את כל השדות עם ולידציה.

---

### 4️⃣ **שליחת בקשת POST /configure**

```python
from src.apis.focus_server_api import FocusServerAPI

# מקבלים API instance (עם fixture)
response = focus_server_api.configure_streaming_job(config_request)
```

**מה קורה בתוך הפונקציה** (```52:92:src/apis/focus_server_api.py```):

```python
def configure_streaming_job(self, payload: ConfigureRequest) -> ConfigureResponse:
    """
    Configure a streaming job.
    
    Args:
        payload: Configuration request payload
        
    Returns:
        Configuration response
    """
    # Convert to dict for JSON serialization
    payload_dict = payload.model_dump()
    
    # Send request
    response = self.post("/configure", json=payload_dict)
    
    # Parse response
    response_data = response.json()
    configure_response = ConfigureResponse(**response_data)
    
    return configure_response
```

**HTTP Call**: `POST https://10.10.100.100/focus-server/configure`

---

### 5️⃣ **עיבוד התשובה**

```python
# ConfigureResponse מכיל:
# - job_id: מזהה ה-job שנוצר
# - status: מצב ה-configuration
# - stream_url: כתובת הסטרימינג
# - stream_port: פורט הסטרימינג

assert hasattr(response, 'job_id') and response.job_id
logger.info(f"✅ Job created: {response.job_id}")
```

---

## 📝 דוגמאות מהקוד

### דוגמה 1: Single Job Creation

**מקור**: ```250:285:tests/load/test_job_capacity_limits.py```

```python
def create_single_job(api: FocusServerAPI, config_payload: Dict[str, Any], 
                     job_num: int) -> Dict[str, Any]:
    """צור job בודד ומדוד ביצועים."""
    result = {
        'job_num': job_num,
        'success': False,
        'latency_ms': 0,
        'job_id': None,
        'error_message': None
    }
    
    try:
        start_time = time.time()
        
        # 1. יצירת ConfigureRequest
        config_request = ConfigureRequest(**config_payload)
        
        # 2. שליחת בקשת POST /configure
        response = api.configure_streaming_job(config_request)
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # 3. עיבוד התשובה
        result['success'] = True
        result['latency_ms'] = latency_ms
        result['job_id'] = response.job_id
        
    except Exception as e:
        result['error_message'] = str(e)
    
    return result
```

---

### דוגמה 2: Concurrent Jobs Creation

**מקור**: ```288:340:tests/load/test_job_capacity_limits.py```

```python
def create_concurrent_jobs(api: FocusServerAPI, config_payload: Dict[str, Any],
                          num_jobs: int, max_workers: int = 20):
    """צור jobs concurrent ומדוד ביצועים."""
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # יוצר num_jobs jobs במקביל
        futures = [
            executor.submit(create_single_job, api, config_payload, i)
            for i in range(num_jobs)
        ]
        
        # אוסף תוצאות
        for future in as_completed(futures):
            result = future.result()
            job_metrics.add_result(result)
```

---

### דוגמה 3: Integration Test

**מקור**: ```725:774:tests/integration/api/test_config_validation_high_priority.py```

```python
def test_valid_configuration_all_parameters(self, focus_server_api, valid_config_payload):
    """Test PZ-13873: Valid configuration with all parameters."""
    
    # 1. יצירת task_id
    task_id = generate_task_id("valid_all_params")
    
    # 2. יצירת payload
    config_payload = valid_config_payload.copy()
    
    # 3. יצירת ConfigureRequest
    config_request = ConfigureRequest(**config_payload)
    
    # 4. שליחת request
    response = focus_server_api.configure_streaming_job(config_request)
    
    # 5. Assertions
    assert hasattr(response, 'job_id') and response.job_id
    logger.info(f"✅ Valid configuration accepted: job_id={response.job_id}")
```

---

## 🔄 תהליך המלא - Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Test Code                                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. generate_task_id("test")                                    │
│    → "test_20251031123456_a1b2c3d4"                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. config_payload = {                                           │
│      "nfftSelection": 1024,                                    │
│      "channels": {"min": 0, "max": 50},                         │
│      "frequencyRange": {"min": 0, "max": 500},                  │
│      "start_time": None,                                        │
│      "end_time": None,                                          │
│      "view_type": ViewType.MULTICHANNEL                         │
│    }                                                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. config_request = ConfigureRequest(**config_payload)         │
│    → Creates validated request object                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. response = focus_server_api.configure_streaming_job(         │
│                     config_request)                             │
│    ↓                                                            │
│    POST /configure                                              │
│    Content-Type: application/json                              │
│    Body: {config_payload}                                       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Focus Server Processing:                                     │
│    ├─ Validates configuration                                  │
│    ├─ Checks resource availability                             │
│    ├─ Creates task in MongoDB                                  │
│    ├─ Starts Baby Analyzer via Kubernetes                      │
│    ├─ Sets up RabbitMQ queues                                  │
│    └─ Prepares streaming endpoint                               │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. ConfigureResponse:                                          │
│    {                                                            │
│      "job_id": "job_abc123",                                    │
│      "stream_url": "10.10.100.100",                            │
│      "stream_port": 50051,                                      │
│      "status": "configured"                                      │
│    }                                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Helper Functions

### generate_task_id()

**מקור**: ```455:472:src/utils/helpers.py```

```python
def generate_task_id(prefix: str = "task") -> str:
    """
    Generate unique task ID.
    
    Args:
        prefix: ID prefix (default: "task")
        
    Returns:
        Unique task ID in format: {prefix}_{timestamp}_{uuid}
    
    Example:
        >>> generate_task_id("test")
        'test_20251007143045_a1b2c3d4'
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{unique_id}"
```

---

### generate_config_payload()

**מקור**: ```507:549:src/utils/helpers.py```

```python
def generate_config_payload(
    sensors_min: int = 0,
    sensors_max: int = 100,
    freq_min: int = 0,
    freq_max: int = 500,
    nfft: int = 1024,
    canvas_height: int = 1000,
    live: bool = True,
    duration_minutes: int = 10
) -> Dict[str, Any]:
    """
    Generate configuration task payload for testing.
    
    Args:
        sensors_min: Minimum sensor index
        sensors_max: Maximum sensor index
        freq_min: Minimum frequency Hz
        freq_max: Maximum frequency Hz
        nfft: NFFT selection
        canvas_height: Canvas height pixels
        live: Live mode flag
        duration_minutes: Duration for historic mode
        
    Returns:
        Configuration payload dictionary
    """
    payload = {
        "displayTimeAxisDuration": 10.0,
        "nfftSelection": nfft,
        "canvasInfo": {"height": canvas_height},
        "sensors": {"min": sensors_min, "max": sensors_max},
        "frequencyRange": {"min": freq_min, "max": freq_max}
    }
    
    if live:
        payload["start_time"] = None
        payload["end_time"] = None
    else:
        start_str, end_str = generate_time_range(duration_minutes=duration_minutes)
        payload["start_time"] = start_str
        payload["end_time"] = end_str
    
    return payload
```

---

## 📊 סיכום - איך נוצרים Jobs

| שלב | פונקציה/פעולה | מיקום בקוד |
|-----|---------------|-------------|
| **1. יצירת ID** | `generate_task_id(prefix)` | `src/utils/helpers.py:455` |
| **2. יצירת Payload** | `generate_config_payload()` או dict ידנית | `src/utils/helpers.py:507` |
| **3. יצירת Request Object** | `ConfigureRequest(**payload)` | `src/models/focus_server_models.py` |
| **4. שליחת Request** | `focus_server_api.configure_streaming_job()` | `src/apis/focus_server_api.py:52` |
| **5. HTTP Call** | `POST /configure` | Inside `configure_streaming_job()` |
| **6. עיבוד Response** | `ConfigureResponse(**response_data)` | `src/apis/focus_server_api.py:82` |

---

## 🎯 דפוסי שימוש נפוצים

### Pattern 1: Basic Job Creation

```python
def test_basic_job_creation(focus_server_api):
    # 1. Payload
    payload = {
        "nfftSelection": 1024,
        "channels": {"min": 0, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,
        "end_time": None,
        "view_type": 0
    }
    
    # 2. Request
    config_request = ConfigureRequest(**payload)
    
    # 3. Send
    response = focus_server_api.configure_streaming_job(config_request)
    
    # 4. Assert
    assert response.job_id
    logger.info(f"Job created: {response.job_id}")
```

---

### Pattern 2: Fixture-based Job Creation

```python
@pytest.fixture
def configured_job(focus_server_api):
    """Configure a job for testing."""
    payload = {
        "nfftSelection": 1024,
        "channels": {"min": 1, "max": 100},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,
        "end_time": None,
        "view_type": ViewType.MULTICHANNEL
    }
    
    config_request = ConfigureRequest(**payload)
    response = focus_server_api.configure_streaming_job(config_request)
    
    yield response.job_id
    
    # Cleanup
    focus_server_api.cancel_job(response.job_id)

# Usage
def test_something(configured_job):
    job_id = configured_job
    # Use job_id in test
```

---

### Pattern 3: Concurrent Jobs

```python
def test_concurrent_jobs(focus_server_api):
    """Create multiple jobs concurrently."""
    payload = {...}  # Configuration
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(
                lambda: focus_server_api.configure_streaming_job(
                    ConfigureRequest(**payload)
                )
            )
            for _ in range(10)
        ]
        
        results = [future.result() for future in as_completed(futures)]
        
        # All jobs created successfully
        assert all(r.job_id for r in results)
```

---

## 🔧 נקודות חשובות

1. **Task ID לא צריך להיות מזכה** - ה-Focus Server מייצר את ה-job_id ועם החזרה ב-ConfigureResponse
2. **צריך fixture** (`focus_server_api`) לקבלת API client
3. **Model validation** - ConfigureRequest בודק את ה-payload
4. **Error handling** - exceptions מטופלות אוטומטית
5. **Cleanup מומלץ** - לנקות jobs אחרי הטסט

---

*מסמך זה מסכם את תהליך יצירת Jobs במערכת האוטומציה*

