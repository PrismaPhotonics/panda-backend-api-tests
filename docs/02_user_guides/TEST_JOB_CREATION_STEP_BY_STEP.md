# תהליך יצירת Job - צעד אחר צעד
## Focus Server Automation - Job Creation Flow

---

## 📋 תוכן עניינים

1. [מבוא](#מבוא)
2. [תהליך כולל - Overview](#תהליך-כולל)
3. [יצירת Job - צעד אחר צעד עם קוד](#יצירת-job-צעד-אחר-צעד-עם-קוד)
4. [דוגמת קוד מלאה](#דוגמת-קוד-מלאה)
5. [מה קורה בצד השרת?](#מה-קורה-בצד-השרת)
6. [סיכום](#סיכום)

---

## 🎯 מבוא

מסמך זה מסביר **בדיוק** איך האוטומציה יוצרת Jobs במערכת Focus Server.

**קבצים מרכזיים:**
- `src/apis/focus_server_api.py` - ה-API client
- `src/utils/helpers.py` - Helper functions
- `src/models/focus_server_models.py` - Data models
- `tests/integration/api/test_config_validation_high_priority.py` - דוגמאות

---

## 🔄 תהליך כולל - Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    THREAD 1: TEST CODE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1: Generate Task ID                                  │
│    task_id = generate_task_id("test")                      │
│    → "test_20251031123456_a1b2c3d4"                       │
│                                                             │
│  STEP 2: Create Config Payload                             │
│    payload = {                                              │
│      "nfftSelection": 1024,                                │
│      "channels": {"min": 0, "max": 50},                     │
│      "frequencyRange": {"min": 0, "max": 500},              │
│      "start_time": None,                                    │
│      "end_time": None,                                      │
│      "view_type": 0                                        │
│    }                                                        │
│                                                             │
│  STEP 3: Create Request Object                             │
│    config_request = ConfigureRequest(**payload)            │
│                                                             │
│  STEP 4: Send API Request                                   │
│    response = focus_server_api.configure_streaming_job(     │
│                  config_request)                            │
│    ↓                                                         │
│    HTTP POST https://10.10.100.100/focus-server/configure  │
│                                                             │
│  STEP 5: Process Response                                   │
│    job_id = response.job_id                                │
│    assert job_id is not None                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   THREAD 2: FOCUS SERVER                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP A: Receive Request                                    │
│    POST /configure received                                │
│    Extract JSON payload                                     │
│                                                             │
│  STEP B: Validate Configuration                             │
│    ✓ Check all required fields present                     │
│    ✓ Validate value ranges                                 │
│    ✓ Check NFFT is valid (128-4096)                         │
│    ✓ Check frequency range < Nyquist                       │
│                                                             │
│  STEP C: Generate Job ID                                    │
│    job_id = "job_" + uuid.uuid4().hex[:8]                 │
│    → "job_a1b2c3d4"                                        │
│                                                             │
│  STEP D: Create Task in MongoDB                             │
│    db.tasks.insert({                                        │
│      task_id: <generated>,                                 │
│      config: <payload>,                                    │
│      status: "configured",                                 │
│      created_at: <timestamp>                               │
│    })                                                       │
│                                                             │
│  STEP E: Start Baby Analyzer                                │
│    Create Kubernetes job                                    │
│    Start Baby Analyzer pod                                  │
│                                                             │
│  STEP F: Setup RabbitMQ                                     │
│    Create queue: grpc-job-{job_id}                        │
│    Bind consumer to queue                                  │
│                                                             │
│  STEP G: Return Response                                    │
│    {                                                        │
│      "job_id": "job_a1b2c3d4",                            │
│      "stream_url": "10.10.100.100",                       │
│      "stream_port": 50051,                                  │
│      "status": "configured"                                 │
│    }                                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 יצירת Job - צעד אחר צעד עם קוד

### שלב 1: יצירת Task ID

**מיקום בקוד**: `src/utils/helpers.py:455-472`

```python
def generate_task_id(prefix: str = "task") -> str:
    """
    Generate unique task ID.
    
    Args:
        prefix: ID prefix (default: "task")
        
    Returns:
        Unique task ID in format: {prefix}_{timestamp}_{uuid}
    """
    # יצירת timestamp בפורמט YYYYMMDDHHMMSS
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # 2025-10-31 12:34:56 → "20251031123456"
    
    # יצירת UUID וקצרה ל-8 תווים
    unique_id = uuid.uuid4().hex[:8]
    # "a1b2c3d4e5f6g7h8i9j0" → "a1b2c3d4"
    
    # חיבור לתבנית: prefix_timestamp_uuid
    return f"{prefix}_{timestamp}_{unique_id}"
    # "test_20251031123456_a1b2c3d4"
```

**במבחן** (```744:744:tests/integration/api/test_config_validation_high_priority.py```):

```python
task_id = generate_task_id("valid_all_params")
# תוצאה: "valid_all_params_20251031123456_a1b2c3d4"
logger.info(f"Test PZ-13873: Valid configuration all parameters - {task_id}")
```

---

### שלב 2: יצירת Config Payload

**מיקום בקוד**: `tests/integration/api/test_config_validation_high_priority.py:64-73`

```python
def valid_config_payload() -> Dict[str, Any]:
    """
    Generate a fully valid configuration payload for LIVE MODE.
    
    Live Mode Characteristics:
        - start_time: null (streaming from current time)
        - end_time: null (continuous streaming)
        - Data source: Real-time sensors
    """
    return {
        # זמן הצגה על הציר (10 שניות)
        "displayTimeAxisDuration": 10,
        
        # NFFT - גודל ה-FFT (קובע רזולוציית תדר)
        "nfftSelection": 1024,
        
        # גובה קנבס (בפיקסלים)
        "displayInfo": {"height": 1000},
        
        # טווח sensors לבדיקה (מינימום למקסימום)
        "channels": {"min": 1, "max": 50},
        
        # טווח תדרים לבדיקה (Hz)
        "frequencyRange": {"min": 0, "max": 500},
        
        # null = Live Mode (נתונים בזמן אמת)
        "start_time": None,
        "end_time": None,
        
        # סוג תצוגה: 0 = MultiChannel (הצגה של מספר sensors)
        "view_type": ViewType.MULTICHANNEL
    }
```

**מה כל שדה אומר?**

| שדה | תיאור | דוגמה |
|-----|-------|-------|
| `displayTimeAxisDuration` | זמן הצגה בציר X (שניות) | 10 |
| `nfftSelection` | גודל FFT (128-4096) | 1024 |
| `displayInfo.height` | גובה קנבס (px) | 1000 |
| `channels.min/max` | טווח sensors | 0-50 |
| `frequencyRange.min/max` | טווח תדרים (Hz) | 0-500 |
| `start_time/end_time` | זמן - null=LIVE | None |
| `view_type` | 0=MULTI, 1=SINGLE | 0 |

---

### שלב 3: יצירת ConfigureRequest Object

**מיקום בקוד**: `tests/integration/api/test_config_validation_high_priority.py:755`

```python
# העתקה של ה-payload
config_payload = valid_config_payload.copy()
logger.info(f"Config payload: {config_payload}")

# יצירת ConfigureRequest Object
# זה מעביר ולידציה אוטומטית
config_request = ConfigureRequest(**config_payload)
```

**מה קורה כאן?**

```python
# ConfigureRequest זה Pydantic Model שמבצע ולידציה
from src.models.focus_server_models import ConfigureRequest

# כשיוצרים את האובייקט, Pydantic:
# 1. בודק שכל השדות קיימים
# 2. בודק שהערכים בטווחים תקפים
# 3. ממיר טיפוסי נתונים (coercion)
# 4. מעלה ValidationError אם יש בעיה

config_request = ConfigureRequest(**config_payload)
# ✅ אם הכל תקין - יוצר אובייקט
# ❌ אם יש בעיה - מעלה ValidationError
```

---

### שלב 4: שליחת בקשת API

**מיקום בקוד**: `tests/integration/api/test_config_validation_high_priority.py:758`

```python
# שליחת בקשת POST /configure
response = focus_server_api.configure_streaming_job(config_request)
```

**מה זה `focus_server_api`?**

```python
# זה fixture שמתקבל מהמבחן
@pytest.fixture
def focus_server_api(config_manager):
    """Create FocusServerAPI instance."""
    return FocusServerAPI(config_manager)
```

**מה קורה בתוך `configure_streaming_job()`?**

**מיקום**: `src/apis/focus_server_api.py:52-92`

```python
def configure_streaming_job(self, payload: ConfigureRequest) -> ConfigureResponse:
    """
    Configure a streaming job.
    
    Args:
        payload: Configuration request payload
        
    Returns:
        Configuration response
    """
    self.logger.info("Configuring streaming job")
    
    try:
        # 1. בדיקת ולידציה ראשונית
        if not isinstance(payload, ConfigureRequest):
            raise ValidationError("Payload must be a ConfigureRequest instance")
        
        # 2. המרה ל-dict (ל-JSON serialization)
        payload_dict = payload.model_dump()
        # {
        #   "displayTimeAxisDuration": 10,
        #   "nfftSelection": 1024,
        #   ...
        # }
        
        # 3. שליחת HTTP request
        response = self.post("/configure", json=payload_dict)
        # POST https://10.10.100.100/focus-server/configure
        # Content-Type: application/json
        # Body: {payload_dict}
        
        # 4. קבלת response
        response_data = response.json()
        # {
        #   "job_id": "job_a1b2c3d4",
        #   "stream_url": "10.10.100.100",
        #   "stream_port": 50051,
        #   "status": "configured"
        # }
        
        # 5. יצירת ConfigureResponse object
        configure_response = ConfigureResponse(**response_data)
        
        self.logger.info(f"Streaming job configured successfully")
        return configure_response
            
    except Exception as e:
        self.logger.error(f"Failed to configure streaming job: {e}")
        raise APIError(f"Failed to configure streaming job: {e}") from e
```

**HTTP Request שהקוד שולח:**

```http
POST https://10.10.100.100/focus-server/configure HTTP/1.1
Host: 10.10.100.100
Content-Type: application/json
Content-Length: 245

{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {
    "height": 1000
  },
  "channels": {
    "min": 1,
    "max": 50
  },
  "frequencyRange": {
    "min": 0,
    "max": 500
  },
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```

---

### שלב 5: עיבוד התשובה

**מיקום בקוד**: `tests/integration/api/test_config_validation_high_priority.py:760-773`

```python
# 1. בדיקה שהתקבל ConfigureResponse
assert isinstance(response, ConfigureResponse), \
    f"Expected ConfigureResponse, got {type(response)}"

# 2. בדיקה שה-job_id קיים
assert hasattr(response, 'job_id') and response.job_id, \
    f"Expected job_id in response"

logger.info(f"✅ Valid configuration accepted: job_id={response.job_id}")

# 3. בדיקה שכל השדות קיימים
assert hasattr(response, 'stream_url'), "Response should contain stream_url"
assert hasattr(response, 'stream_port'), "Response should contain stream_port"
logger.info(f"✅ Response contains stream info: {response.stream_url}:{response.stream_port}")
```

**התשובה שהשרת מחזיר:**

```json
{
  "job_id": "job_a1b2c3d4",
  "stream_url": "10.10.100.100",
  "stream_port": 50051,
  "status": "configured",
  "created_at": "2025-10-31T12:34:56Z"
}
```

---

## 💻 דוגמת קוד מלאה

### דוגמה 1: בסיסית

```python
import logging
from src.utils.helpers import generate_task_id
from src.models.focus_server_models import ConfigureRequest, ConfigureResponse, ViewType
from src.apis.focus_server_api import FocusServerAPI

logger = logging.getLogger(__name__)

def test_create_job_basic(focus_server_api):
    """דוגמה בסיסית ליצירת job."""
    
    # ========== STEP 1: Generate Task ID ==========
    task_id = generate_task_id("basic_test")
    logger.info(f"STEP 1: Generated task_id: {task_id}")
    # Output: "basic_test_20251031123456_a1b2c3d4"
    
    # ========== STEP 2: Create Config Payload ==========
    payload = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 1, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,  # Live mode
        "end_time": None,
        "view_type": ViewType.MULTICHANNEL
    }
    logger.info(f"STEP 2: Created payload with {payload['channels']['max']} channels")
    
    # ========== STEP 3: Create Request Object ==========
    config_request = ConfigureRequest(**payload)
    logger.info("STEP 3: ConfigureRequest object created (validation passed)")
    
    # ========== STEP 4: Send API Request ==========
    response = focus_server_api.configure_streaming_job(config_request)
    logger.info("STEP 4: POST /configure request sent")
    
    # ========== STEP 5: Process Response ==========
    assert hasattr(response, 'job_id') and response.job_id
    logger.info(f"STEP 5: Job created successfully!")
    logger.info(f"  Job ID: {response.job_id}")
    logger.info(f"  Stream URL: {response.stream_url}")
    logger.info(f"  Stream Port: {response.stream_port}")
    
    return response.job_id
```

---

### דוגמה 2: עם Cleanup

```python
import pytest
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def temporary_job(focus_server_api):
    """Fixture שיוצר job ומנקה אותו בסוף."""
    
    # STEP 1-3: Create job
    payload = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 1, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,
        "end_time": None,
        "view_type": 0
    }
    
    config_request = ConfigureRequest(**payload)
    response = focus_server_api.configure_streaming_job(config_request)
    
    job_id = response.job_id
    logger.info(f"Created job: {job_id}")
    
    # Return job_id to test
    yield job_id
    
    # Cleanup - cancel job after test
    try:
        focus_server_api.cancel_job(job_id)
        logger.info(f"Cleaned up job: {job_id}")
    except Exception as e:
        logger.warning(f"Failed to cleanup job {job_id}: {e}")

def test_with_job(temporary_job):
    """Test שמשתמש ב-job שנוצר."""
    job_id = temporary_job
    logger.info(f"Running test with job: {job_id}")
    
    # Your test code here
    assert job_id is not None
```

---

### דוגמה 3: Concurrent Jobs

```python
import concurrent.futures
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def create_single_job(
    api: FocusServerAPI, 
    config_payload: Dict[str, Any], 
    job_num: int
) -> Dict[str, Any]:
    """צור job בודד ומדוד ביצועים."""
    
    result = {
        'job_num': job_num,
        'success': False,
        'latency_ms': 0,
        'job_id': None,
        'error_message': None
    }
    
    try:
        import time
        start_time = time.time()
        
        # STEP 1-3: Same as before
        config_request = ConfigureRequest(**config_payload)
        
        # STEP 4: Send request
        response = api.configure_streaming_job(config_request)
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # STEP 5: Process response
        result['success'] = True
        result['latency_ms'] = latency_ms
        result['job_id'] = response.job_id
        
        logger.debug(
            f"Job #{job_num} created: {result['job_id']} "
            f"({latency_ms:.0f}ms)"
        )
        
    except Exception as e:
        result['error_message'] = str(e)
        logger.warning(f"Job #{job_num} failed: {e}")
    
    return result

def test_concurrent_jobs(focus_server_api):
    """יצירת מספר jobs במקביל."""
    
    num_jobs = 10
    max_workers = 5
    
    # Payload משותף לכל ה-jobs
    config_payload = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 1, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,
        "end_time": None,
        "view_type": 0
    }
    
    results = []
    
    # יצירת jobs במקביל
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(create_single_job, focus_server_api, config_payload, i)
            for i in range(num_jobs)
        ]
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            
            if result['success']:
                logger.info(
                    f"✅ Job #{result['job_num']}: "
                    f"{result['job_id']} ({result['latency_ms']:.0f}ms)"
                )
    
    # ניתוח תוצאות
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    logger.info(f"Summary: {len(successful)}/{num_jobs} jobs created successfully")
    
    assert len(successful) == num_jobs, f"Expected all jobs to succeed, but {len(failed)} failed"
```

---

## 🖥️ מה קורה בצד השרת?

כשה-Server מקבל את ה-request, זה מה שקורה:

### 1. קבלת Request

```python
# Server code (pseudo)
@app.post("/configure")
async def configure(request: ConfigureRequest):
    logger.info(f"Received configure request")
    
    # Extract payload
    payload = request.model_dump()
```

### 2. ולידציה

```python
# Validate configuration
validator.validate(payload)
# ✓ Check required fields
# ✓ Check value ranges (0-4096 for NFFT)
# ✓ Check frequency range < Nyquist
# ✓ Check channel ranges
```

### 3. יצירת Job ID

```python
# Generate unique job ID
job_id = f"job_{uuid.uuid4().hex[:8]}"
# "job_a1b2c3d4"
```

### 4. יצירת Task ב-MongoDB

```python
# Insert into MongoDB
db.tasks.insert({
    "task_id": job_id,
    "config": payload,
    "status": "configured",
    "created_at": datetime.now(),
    "user": "automation"
})
```

### 5. הפעלת Baby Analyzer

```python
# Create Kubernetes job
kubectl.create_job(
    name=f"baby-analyzer-{job_id}",
    image="baby-analyzer:latest",
    config=payload
)
```

### 6. הגדרת RabbitMQ

```python
# Create queue for this job
queue_name = f"grpc-job-{job_id}"
rabbitmq.create_queue(queue_name)

# Bind consumer
consumer = BufferedRecordingConsumer(job_id)
consumer.connect(queue_name)
```

### 7. החזרת Response

```python
# Return response
return ConfigureResponse(
    job_id=job_id,
    stream_url="10.10.100.100",
    stream_port=50051,
    status="configured"
)
```

---

## 📊 תרשים זרימה

```
┌────────────────────────────────────────┐
│  TEST CODE                             │
│                                        │
│  1. generate_task_id()                 │
│     ↓                                 │
│  2. Create payload dict               │
│     ↓                                 │
│  3. ConfigureRequest(**payload)       │
│     ↓                                 │
│  4. api.configure_streaming_job()     │
└────────────┬───────────────────────────┘
             │ HTTP POST /configure
             │ JSON Body: {payload}
             ▼
┌────────────────────────────────────────┐
│  FOCUS SERVER                          │
│                                        │
│  A. Receive & Validate                │
│     ↓                                 │
│  B. Generate job_id                   │
│     ↓                                 │
│  C. MongoDB: Insert task              │
│     ↓                                 │
│  D. Kubernetes: Start Baby Analyzer   │
│     ↓                                 │
│  E. RabbitMQ: Create queue            │
│     ↓                                 │
│  F. Return ConfigureResponse          │
└────────────┬───────────────────────────┘
             │ HTTP 200 OK
             │ {job_id, stream_url, ...}
             ▼
┌────────────────────────────────────────┐
│  TEST CODE                             │
│                                        │
│  5. Process response.job_id           │
│  6. Assertions & Logging              │
└────────────────────────────────────────┘
```

---

## ✅ סיכום

### התהליך ב-6 שלבים:

1. **Generate Task ID** → `generate_task_id()`
2. **Create Payload** → Dict עם configuration
3. **Create Request** → `ConfigureRequest(**payload)`
4. **Send API** → `configure_streaming_job(request)`
5. **Get Response** → `ConfigureResponse` עם `job_id`
6. **Assert & Log** → וידוא `job_id` קיים

### הסטייק:

- **Client**: Test code → API client
- **Server**: Focus Server API → MongoDB → Kubernetes → RabbitMQ

### קבצים חשובים:

| קובץ | שורה | פונקציה |
|------|------|---------|
| `src/utils/helpers.py` | 455 | `generate_task_id()` |
| `src/utils/helpers.py` | 507 | `generate_config_payload()` |
| `src/apis/focus_server_api.py` | 52 | `configure_streaming_job()` |
| `tests/integration/api/test_config_validation_high_priority.py` | 744-773 | דוגמה |

---

*מסמך זה מספק הסבר מלא ומפורט של תהליך יצירת Jobs במערכת*

