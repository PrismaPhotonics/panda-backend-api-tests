# 📡 Focus Server API Endpoints - Current Server

**תאריך:** 23 אוקטובר 2025  
**שרת:** pzlinux:10.7.122 (https://10.10.100.100/focus-server)  
**סטטוס:** ✅ פעיל

---

## 📋 **סיכום Endpoints**

| # | Method | Path | שימוש | סטטוס |
|---|--------|------|-------|-------|
| 1️⃣ | POST | `/configure` | Configure streaming job | ✅ בשימוש |
| 2️⃣ | GET | `/ack` | Health check | ✅ זמין |
| 3️⃣ | GET | `/channels` | Get channel range | ✅ זמין |
| 4️⃣ | GET | `/live_metadata` | Get live metadata | ✅ זמין |
| 5️⃣ | GET | `/metadata/{job_id}` | Get job metadata | ✅ זמין |
| 6️⃣ | POST | `/recordings_in_time_range` | Query recordings | ✅ זמין |

**סה"כ:** 6 endpoints

---

## 1️⃣ **POST /configure** ✅

### **תיאור:**
Configure a streaming job for live or historic data playback.

### **Request:**
```json
{
  "displayTimeAxisDuration": 10,      // Optional[int]
  "nfftSelection": 1024,              // Optional[int]
  "displayInfo": {
    "height": 1000                    // Required, int
  },
  "channels": {
    "min": 1,                         // Required, int
    "max": 50                         // Required, int
  },
  "frequencyRange": {                 // Optional
    "min": 0,
    "max": 500
  },
  "start_time": null,                 // Optional[int], epoch
  "end_time": null,                   // Optional[int], epoch
  "view_type": 0                      // Required, ViewType enum
}
```

### **Response:**
```json
{
  "status": "",
  "frequencies_list": [0.0, 1.0, ...],
  "lines_dt": 123.0,
  "channel_to_stream_index": {"1": 0, "2": 1, ...},
  "stream_amount": 2,
  "job_id": "abc123",
  "frequencies_amount": 500,
  "channel_amount": 50,
  "stream_port": 50051,
  "stream_url": "10.10.100.100",
  "view_type": 0,
  "metadata": {}
}
```

### **View Types:**
```
0 = MULTICHANNEL
1 = SINGLECHANNEL
2 = WATERFALL
3 = UNKNOWN (not documented)
```

### **Modes:**
- **Live Mode:** `start_time: null`, `end_time: null`
- **Historic Mode:** `start_time: epoch`, `end_time: epoch`

---

## 2️⃣ **GET /ack**

### **תיאור:**
Health check endpoint - verify server is alive.

### **Response:**
```json
{}
```

**שימוש:**
```python
response = requests.get("https://10.10.100.100/focus-server/ack", verify=False)
# 200 OK = server is alive
```

---

## 3️⃣ **GET /channels**

### **תיאור:**
Get the available channel range from the system.

### **Response:**
```json
{
  "lowest_channel": 1,
  "highest_channel": 2500
}
```

**שימוש:**
```python
response = requests.get("https://10.10.100.100/focus-server/channels", verify=False)
data = response.json()
print(f"Available channels: {data['lowest_channel']} - {data['highest_channel']}")
```

**📝 Note:** This could be used for dynamic channel validation!

---

## 4️⃣ **GET /live_metadata**

### **תיאור:**
Get metadata for live streaming.

### **Response:**
```json
{
  "dx": 1.0213698148727417,
  "prr": 2000.0,
  "fiber_start_meters": 0,
  "fiber_length_meters": 5000,
  "sw_version": "1.0.0",
  "number_of_channels": 2500,
  "fiber_description": "Main fiber"
}
```

**שדות:**
- `dx`: Distance between consecutive channels
- `prr`: Pulse Repetition Rate (samples/second)
- `fiber_start_meters`: Start position on fiber
- `fiber_length_meters`: Total fiber length
- `sw_version`: Software version
- `number_of_channels`: Total channels available
- `fiber_description`: Fiber description

**📝 Note:** This is where we can get PRR for Nyquist calculation!

---

## 5️⃣ **GET /metadata/{job_id}**

### **תיאור:**
Get metadata for a specific job.

### **Parameters:**
- `job_id` (path, required): The job ID returned from `/configure`

### **Response:**
```json
{
  "status": "running",
  "frequencies_list": [...],
  "job_id": "abc123",
  "stream_port": 50051,
  "stream_url": "10.10.100.100",
  "view_type": 0,
  "metadata": {
    "dx": 1.02,
    "prr": 2000,
    ...
  }
}
```

**שימוש:**
```python
# First, configure a job
config_response = api.configure_streaming_job(payload)
job_id = config_response.job_id

# Then, get its metadata
metadata = api.get_job_metadata(job_id)
```

---

## 6️⃣ **POST /recordings_in_time_range**

### **תיאור:**
Query available recordings in a specific time range.

### **Request:**
```json
{
  "start_time": 1698000000,  // Required, epoch timestamp
  "end_time": 1698100000     // Required, epoch timestamp
}
```

### **Response:**
```json
{
  "recordings": [
    [1698000000, 1698050000],  // [start, end]
    [1698050000, 1698100000],
    [1698100000, -1]           // -1 means recording still ongoing
  ]
}
```

**שימוש:**
```python
request = {
    "start_time": 1698000000,
    "end_time": 1698100000
}
response = requests.post(
    "https://10.10.100.100/focus-server/recordings_in_time_range",
    json=request,
    verify=False
)
recordings = response.json()["recordings"]
```

**📝 Note:** Useful for validating historic mode time ranges!

---

## ❌ **Endpoints שלא קיימים**

### **GET /waterfall/{task_id}/{row_count}** ❌

**סטטוס:** לא מיושם ב-backend!

**תיאור:**
- Endpoint זה מתוכנן אבל עדיין לא מיושם
- הטסטים מסומנים כ-`@pytest.mark.skip` עם הסיבה: *"Future API structure - GET /waterfall/{task_id}/{row_count} endpoint not yet deployed to staging"*

**השפעה:**
- כל הטסטים שמשתמשים ב-waterfall endpoint נכשלים (404)
- לא ניתן לבדוק negative amplitude values
- לא ניתן לבדוק data integrity ו-consistency
- לא ניתן לבדוק performance של waterfall endpoint

**פתרון:**
1. המתין ל-implementation של ה-endpoint ב-backend
2. סמן את כל הטסטים כ-SKIP עד שה-endpoint יהיה זמין
3. לאחר שה-endpoint ייושם, הסר את ה-skip והרץ את כל הטסטים

**קבצים שצריכים skip:**
- `be_focus_server_tests/integration/data_quality/test_negative_amplitude_values.py`
- `be_focus_server_tests/integration/data_quality/test_consumer_creation_debug.py`
- `be_focus_server_tests/integration/data_quality/test_data_consistency.py`
- `be_focus_server_tests/integration/data_quality/test_data_integrity.py`
- `be_focus_server_tests/integration/performance/test_network_latency.py`
- `be_focus_server_tests/integration/performance/test_response_time.py`

---

### **POST /config/{task_id}** ❌

**סטטוס:** לא קיים בשרת הנוכחי!

**השפעה:**
- ~190 טסטים לא עובדים
- Performance tests משתמשים בזה
- Integration tests משתמשים בזה

**פתרון:**
1. עדכן את השרת לגרסה חדשה (מומלץ)
2. שנה טסטים ל-`/configure` (זמני)

---

## 📊 **השוואה: Old API vs New API**

| Feature | Old API (`/configure`) | New API (`/config/{task_id}`) |
|---------|----------------------|------------------------------|
| **Status** | ✅ קיים | ❌ לא קיים |
| **Method** | POST | POST |
| **Task ID** | Generated by server | Provided by client |
| **Request Model** | ConfigureRequest | ConfigTaskRequest |
| **Response Model** | ConfigureResponse | ConfigTaskResponse |
| **Fields** | displayInfo, channels | canvasInfo, sensors |

---

## 🎯 **המלצות**

### **1. Dynamic Validation:**

השתמש ב-`/live_metadata` לקבל את ה-PRR:

```python
# Get PRR from server
metadata = api.get_live_metadata()
prr = metadata.prr  # e.g., 2000 Hz
nyquist = prr / 2   # 1000 Hz

# Validate frequency
if frequency > nyquist:
    raise ValueError(f"Frequency {frequency} exceeds Nyquist {nyquist}")
```

### **2. Channel Range Validation:**

השתמש ב-`/channels` לוולידציה דינמית:

```python
# Get available channels
channels = api.get_channels()
min_channel = channels.lowest_channel
max_channel = channels.highest_channel

# Validate request
if request.channels.max > max_channel:
    raise ValueError(f"Channel {request.channels.max} exceeds max {max_channel}")
```

### **3. Historic Mode Validation:**

השתמש ב-`/recordings_in_time_range`:

```python
# Check if recordings exist for this time range
recordings = api.get_recordings_in_time_range(start_time, end_time)

if not recordings.recordings:
    return "404 No recordings found in time range"
else:
    # Proceed with configuration
    config = api.configure_streaming_job(payload)
```

---

## 📋 **טסטים לעדכון**

### **קבצים שצריכים תיקון:**

```
❌ tests/performance/test_performance_high_priority.py
   - Uses: config_task() → Change to: configure_streaming_job()

❌ tests/performance/test_performance_benchmark.py
   - Uses: config_task() → Change to: configure_streaming_job()

❌ tests/integration/test_task_lifecycle.py
   - Uses: config_task() → Change to: configure_streaming_job()

❌ tests/integration/test_waterfall.py
   - Uses: /config/{task_id} endpoint
   - Action: DELETE OR FIX

❌ tests/integration/test_sensors.py
   - Uses: config_task() → Change to: configure_streaming_job()

❌ tests/api/test_metadata.py
   - Uses: config_task() → Change to: configure_streaming_job()
```

### **טסטים שעובדים:**

```
✅ tests/integration/api/test_config_validation_high_priority.py
   - Uses: configure_streaming_job() ← כבר מתוקן!

✅ tests/infrastructure/test_basic_connectivity.py
   - לא משתמש ב-API

✅ tests/infrastructure/test_mongodb_data_quality.py
   - לא משתמש ב-API
```

---

## 🔗 **קישורים שימושיים**

- **OpenAPI Spec:** https://10.10.100.100/focus-server/openapi.json
- **Swagger UI:** https://10.10.100.100/focus-server/docs (אם זמין)
- **Health Check:** https://10.10.100.100/focus-server/ack

---

**נוצר:** 23 אוקטובר 2025  
**מקור:** `api_spec.json` (8425 bytes)  
**סטטוס:** ✅ מסמך מלא!

