# Example Output - Enhanced Logging

## Before (Without Enhanced Logging)
```
$ pytest tests/integration/api/test_singlechannel_view_mapping.py -v

test_configure_singlechannel_mapping PASSED    [100%]

1 passed in 2.34s
```

That's all you saw... 😞

---

## After (With Enhanced Logging)

### Example 1: Basic Test (HTTP Logging)
```bash
$ pytest tests/integration/api/test_singlechannel_view_mapping.py -v
```

**Output:**
```
================================================================================
→ POST http://10.10.10.150:5000/configure
Request Body (JSON):
  {
    "view_type": "1",
    "channels": {
      "min": 7,
      "max": 7
    },
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    }
  }
← 200 OK (342.56ms)
Response Body (JSON):
  {
    "status": "",
    "stream_amount": 1,
    "channel_to_stream_index": {
      "7": 0
    },
    "job_id": "31-3633",
    "view_type": "1",
    "channel_amount": 1,
    "frequencies_amount": 256,
    "lines_dt": 0.01,
    "stream_url": "http://10.10.10.150",
    "stream_port": "12331"
  }
================================================================================

test_configure_singlechannel_mapping PASSED    [100%]
```

✅ **You now see exactly what was sent and received!**

---

### Example 2: With Pod Logs Streaming
```bash
$ pytest tests/integration/api/test_singlechannel_view_mapping.py --collect-pod-logs -v
```

**Output:**
```
================================================================================
POD LOGS COLLECTION: Starting...
================================================================================
Found pod: focus-server-deployment-7d8f9c5b6-xkl2m for service: focus-server
✅ Started background log streaming from focus-server-deployment-7d8f9c5b6-xkl2m
Found pod: rabbitmq-panda-0 for service: rabbitmq-panda
✅ Started background log streaming from rabbitmq-panda-0
✅ Real-time log streaming active

================================================================================
→ POST http://10.10.10.150:5000/configure
Request Body (JSON):
  { "view_type": "1", "channels": {"min": 7, "max": 7}, ... }

[focus-server] 2025-10-12 15:44:43 INFO: Received POST /configure request
[focus-server] 2025-10-12 15:44:43 INFO: Validating request payload for view_type=1
[focus-server] 2025-10-12 15:44:43 INFO: Channel validation: min=7, max=7 ✓
[focus-server] 2025-10-12 15:44:43 INFO: Creating baby analyzer job...
[focus-server] 2025-10-12 15:44:43 INFO: Connecting to RabbitMQ...
[rabbitmq-panda] 2025-10-12 15:44:43 INFO: New connection from 10.10.10.150:5672
[focus-server] 2025-10-12 15:44:43 INFO: Baby analyzer command created for channel 7
[focus-server] 2025-10-12 15:44:43 INFO: Stream created: stream-0
[focus-server] 2025-10-12 15:44:43 INFO: Mapping channel 7 -> stream 0
[focus-server] 2025-10-12 15:44:43 INFO: Job 31-3633 created successfully
[focus-server] 2025-10-12 15:44:43 INFO: Returning response with stream_amount=1

← 200 OK (342.56ms)
Response Body (JSON):
  { "stream_amount": 1, "channel_to_stream_index": {"7": 0}, ... }
================================================================================

test_configure_singlechannel_mapping PASSED    [100%]
```

✅ **You now see what happens INSIDE the server during the test!**

---

### Example 3: Debugging a Failure
```bash
$ pytest tests/integration/api/test_singlechannel_view_mapping.py --collect-pod-logs --save-pod-logs -v
```

**Output:**
```
================================================================================
→ POST http://10.10.10.150:5000/configure
Request Body (JSON):
  { "view_type": "1", "channels": {"min": 5, "max": 10}, ... }

[focus-server] 2025-10-12 15:44:44 INFO: Received POST /configure request
[focus-server] 2025-10-12 15:44:44 WARNING: view_type=SINGLECHANNEL but min!=max
[focus-server] 2025-10-12 15:44:44 WARNING: Expected min==max for SINGLECHANNEL
[focus-server] 2025-10-12 15:44:44 INFO: Processing anyway (no validation)
[focus-server] 2025-10-12 15:44:44 INFO: Creating stream for channels 5-10
[focus-server] 2025-10-12 15:44:44 INFO: Mapped 6 channels to single stream
[focus-server] 2025-10-12 15:44:44 INFO: Job created with stream_amount=1

← 200 OK (423.12ms)
Response Body (JSON):
  { 
    "stream_amount": 1,
    "channel_to_stream_index": {
      "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0
    }
  }
================================================================================

test_singlechannel_with_min_not_equal_max_should_fail PASSED    [100%]

⚠️  Server accepted min != max but maintained stream_amount=1

================================================================================
POD LOGS COLLECTION: Saving logs to files...
================================================================================
✅ Saved logs to reports/logs/pod_logs/focus-server_latest.log
✅ Saved logs to reports/logs/pod_logs/rabbitmq-panda_latest.log
```

✅ **You found the bug! Server accepts min!=max for SINGLECHANNEL!**  
✅ **Logs saved for later analysis!**

---

## What You Get

| Feature | What You See | When |
|---------|-------------|------|
| **HTTP Request** | Full URL, headers, body, params | Always |
| **HTTP Response** | Status, headers, body, timing | Always |
| **Request Timing** | Milliseconds per request | Always |
| **Pretty JSON** | Formatted, readable JSON | Always |
| **Focus Server Logs** | Internal server processing | `--collect-pod-logs` |
| **RabbitMQ Logs** | Message queue activity | `--collect-pod-logs` |
| **Saved Log Files** | Persistent logs for analysis | `--save-pod-logs` |

---

## Log Files Location

When using `--save-pod-logs`:
```
reports/logs/
├── pytest_execution.log              ← Full test execution log
└── pod_logs/
    ├── focus-server_latest.log       ← Focus Server logs (last 500 lines)
    └── rabbitmq-panda_latest.log     ← RabbitMQ logs (last 500 lines)
```

---

## Manual Log Collection Example

```bash
$ python scripts/collect_pod_logs_manual.py --service focus-server --lines 100
```

**Output:**
```
================================================================================
MANUAL POD LOGS COLLECTION
================================================================================
Environment: staging
SSH Host: 10.10.10.150
Services: focus-server
Lines: 100
Mode: DISPLAY
================================================================================

================================================================================
SERVICE: focus-server
================================================================================
Found pod: focus-server-deployment-7d8f9c5b6-xkl2m

--------------------------------------------------------------------------------
Logs from focus-server:
--------------------------------------------------------------------------------
2025-10-12 15:44:00 INFO: Focus Server starting...
2025-10-12 15:44:01 INFO: Connected to RabbitMQ
2025-10-12 15:44:02 INFO: Connected to MongoDB
2025-10-12 15:44:03 INFO: Server ready on port 5000
2025-10-12 15:44:43 INFO: Received POST /configure request
2025-10-12 15:44:43 INFO: Job 31-3633 created successfully
...
--------------------------------------------------------------------------------

================================================================================
✅ COLLECTION COMPLETE
================================================================================
```

---

## Summary

### Before Enhanced Logging:
- ❌ Only saw "PASSED" or "FAILED"
- ❌ No idea what was sent/received
- ❌ No visibility into server processing
- ❌ Hard to debug failures

### After Enhanced Logging:
- ✅ See full HTTP requests/responses
- ✅ See internal server processing
- ✅ See timing for every call
- ✅ Save logs for later analysis
- ✅ Easy to debug and find issues

**You now have X-ray vision into your tests! 👀**

