# Enhanced Logging Guide
**Advanced logging capabilities for debugging and monitoring tests**

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [HTTP Request/Response Logging](#http-requestresponse-logging)
3. [Pod Logs Collection](#pod-logs-collection)
4. [Usage Examples](#usage-examples)
5. [Configuration](#configuration)
6. [Best Practices](#best-practices)

---

<a name="overview"></a>
## 🎯 Overview

The framework now includes **enhanced logging capabilities** to help you see exactly what happens during tests:

### What's New?
✅ **Detailed HTTP Logging** - See every request and response  
✅ **Pod Logs Streaming** - Monitor Kubernetes pods in real-time  
✅ **Pretty JSON Formatting** - Easy-to-read request/response bodies  
✅ **Request Timing** - Know how long each call takes  
✅ **Background Log Collection** - Non-intrusive monitoring  
✅ **Save Logs to Files** - Keep logs for later analysis  

---

<a name="http-requestresponse-logging"></a>
## 🌐 HTTP Request/Response Logging

### Features

The `BaseAPIClient` now logs **every HTTP request and response** with full details:

- **Request**: Method, URL, Headers, Body, Parameters
- **Response**: Status Code, Headers, Body, Timing
- **Pretty JSON**: Automatically formats JSON for readability
- **Error Details**: Full error responses for debugging

### Example Output

```
================================================================================
→ POST http://10.10.10.150:5000/configure
Request Body (JSON):
  {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 7,
      "max": 7
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": "1"
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
```

### Control Logging Level

```python
# In pytest.ini or command line:
-log-cli-level=DEBUG  # Show headers and all details
-log-cli-level=INFO   # Show requests/responses (default)
-log-cli-level=WARNING # Only show errors
```

---

<a name="pod-logs-collection"></a>
## 📦 Pod Logs Collection

### Overview

Collect and monitor logs from Kubernetes pods (Focus Server, RabbitMQ, etc.) during test execution.

### Two Modes

1. **Real-time Streaming** - See logs as tests run
2. **Save to Files** - Collect logs for later analysis

---

### Mode 1: Real-Time Streaming

Stream logs from services while tests are running:

```bash
# Enable real-time log streaming
pytest tests/integration/api/test_singlechannel_view_mapping.py --collect-pod-logs -v
```

**Output:**
```
================================================================================
POD LOGS COLLECTION: Starting...
================================================================================
Starting real-time log streaming from services...
Found pod: focus-server-deployment-7d8f9c5b6-xkl2m for service: focus-server
✅ Started background log streaming from focus-server-deployment-7d8f9c5b6-xkl2m
Found pod: rabbitmq-panda-0 for service: rabbitmq-panda
✅ Started background log streaming from rabbitmq-panda-0
✅ Real-time log streaming active

# During tests, you'll see logs like:
[focus-server] 2025-10-12 15:44:43 INFO: Received configure request for view_type=1
[focus-server] 2025-10-12 15:44:43 INFO: Creating baby analyzer job for channel 7
[focus-server] 2025-10-12 15:44:43 INFO: Job 31-3633 created successfully
[rabbitmq-panda] 2025-10-12 15:44:43 INFO: New connection from 10.10.10.150
```

---

### Mode 2: Save to Files

Save pod logs to files after test execution:

```bash
# Save logs to files
pytest tests/integration/api/test_singlechannel_view_mapping.py --save-pod-logs -v
```

**Output:**
```
================================================================================
POD LOGS COLLECTION: Saving logs to files...
================================================================================
Collecting logs from pod: focus-server-deployment-7d8f9c5b6-xkl2m
✅ Saved logs to reports/logs/pod_logs/focus-server_latest.log
Collecting logs from pod: rabbitmq-panda-0
✅ Saved logs to reports/logs/pod_logs/rabbitmq-panda_latest.log
✅ Logs saved to reports/logs/pod_logs
```

**Log files are saved to:**
```
reports/logs/pod_logs/
├── focus-server_latest.log
└── rabbitmq-panda_latest.log
```

---

### Mode 3: Both (Recommended for Debugging)

```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py --collect-pod-logs --save-pod-logs -v
```

---

<a name="usage-examples"></a>
## 💡 Usage Examples

### Example 1: Debug a Failing Test with Full Logs

```bash
# Run test with all logging enabled
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewHappyPath::test_configure_singlechannel_mapping \
    --collect-pod-logs \
    --save-pod-logs \
    -v \
    -s  # Show print statements
```

**What you get:**
- ✅ HTTP request/response details
- ✅ Real-time Focus Server logs
- ✅ Real-time RabbitMQ logs
- ✅ Log files saved for later analysis

---

### Example 2: Monitor Multiple Services

```python
# In your test file:
def test_something(pod_logs_collector):
    """Test with pod logs collection."""
    # Logs are automatically collected from:
    # - focus-server
    # - rabbitmq-panda
    
    # Your test code here
    response = focus_server_api.configure_streaming_job(request)
    
    # Logs from Focus Server will show what happened internally
```

---

### Example 3: Manually Collect Logs

```python
from src.utils.pod_logs_collector import PodLogsCollector

# In your test or debug script:
collector = PodLogsCollector(
    ssh_host="10.10.10.150",
    ssh_user="prisma",
    ssh_password="PASSW0RD"
)

collector.connect()

# Get last 100 lines from Focus Server
logs = collector.collect_logs_for_service("focus-server", lines=100)
print(logs)

# Save to file
collector.save_logs_to_file(
    service_name="focus-server",
    output_file="debug_logs.txt",
    lines=500
)

collector.disconnect()
```

---

### Example 4: Stream Logs from Multiple Services

```python
from src.utils.pod_logs_collector import stream_service_logs_during_test

# Start streaming before your test
collector = stream_service_logs_during_test(
    ssh_host="10.10.10.150",
    ssh_user="prisma",
    ssh_password="PASSW0RD",
    services=["focus-server", "rabbitmq-panda", "baby-analyzer"],
    lines=50
)

# Run your test
# ... test code ...

# Stop streaming
collector.disconnect()
```

---

<a name="configuration"></a>
## ⚙️ Configuration

### pytest.ini

```ini
[pytest]
# Logging configuration
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(name)s: %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S

# File logging
log_file = reports/logs/pytest_execution.log
log_file_level = DEBUG
log_file_format = %(asctime)s [%(levelname)8s] %(name)s: %(message)s
```

### environments.yaml

Ensure Kubernetes SSH credentials are configured:

```yaml
staging:
  kubernetes:
    ssh_host: "10.10.10.150"
    ssh_user: "prisma"
    ssh_password: "PASSW0RD"  # Or use environment variable
    namespace: "default"
```

---

### Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--collect-pod-logs` | Stream logs in real-time | `pytest --collect-pod-logs` |
| `--save-pod-logs` | Save logs to files | `pytest --save-pod-logs` |
| `-v` | Verbose test output | `pytest -v` |
| `-s` | Show print statements | `pytest -s` |
| `-log-cli-level=DEBUG` | Show all log details | `pytest -log-cli-level=DEBUG` |

---

<a name="best-practices"></a>
## 🎓 Best Practices

### 1. Use Appropriate Log Levels

```python
# For development/debugging
pytest --collect-pod-logs -log-cli-level=DEBUG

# For CI/CD
pytest --save-pod-logs -log-cli-level=INFO

# For production
pytest -log-cli-level=WARNING
```

---

### 2. Filter Pod Logs

```python
# Only show errors from Focus Server
def error_filter(line: str) -> bool:
    return "ERROR" in line or "CRITICAL" in line

collector.stream_logs_to_logger(
    pod_name="focus-server-xxx",
    filter_func=error_filter
)
```

---

### 3. Collect Logs for Failed Tests Only

```python
# In conftest.py
@pytest.fixture(scope="function", autouse=True)
def collect_logs_on_failure(request, pod_logs_collector):
    """Collect logs only if test fails."""
    yield
    
    if request.node.rep_call.failed:
        if pod_logs_collector:
            # Save logs for failed test
            test_name = request.node.name
            pod_logs_collector.save_logs_to_file(
                service_name="focus-server",
                output_file=f"reports/logs/failures/{test_name}_focus_server.log",
                lines=200
            )
```

---

### 4. Monitor Specific Containers

If a pod has multiple containers:

```python
collector.tail_logs(
    pod_name="focus-server-xxx",
    container="focus-server-container",  # Specific container
    lines=100
)
```

---

### 5. Save Logs with Timestamps

```python
import time

timestamp = time.strftime("%Y%m%d_%H%M%S")
collector.save_logs_to_file(
    service_name="focus-server",
    output_file=f"reports/logs/focus_server_{timestamp}.log",
    lines=1000
)
```

---

## 🔧 Troubleshooting

### Issue: No logs collected

**Solution:**
1. Check SSH credentials in `config/environments.yaml`
2. Verify pod is running: `kubectl get pods -n default`
3. Check if service name is correct: `kubectl get svc -n default`

### Issue: "SSH connection refused"

**Solution:**
```bash
# Test SSH connection manually
ssh prisma@10.10.10.150

# Check if kubectl works
ssh prisma@10.10.10.150 kubectl get pods
```

### Issue: Too many logs, performance impact

**Solution:**
```python
# Reduce initial lines
collector.collect_logs_for_service("focus-server", lines=10, stream=True)

# Use filtering
def important_only(line):
    return "ERROR" in line or "WARNING" in line or "job" in line.lower()

collector.stream_logs_to_logger(..., filter_func=important_only)
```

---

## 📊 Example: Full Debug Session

```bash
# 1. Run test with all logging
pytest tests/integration/api/test_singlechannel_view_mapping.py \
    --collect-pod-logs \
    --save-pod-logs \
    -v \
    -s \
    -log-cli-level=DEBUG \
    > full_debug_output.txt 2>&1

# 2. Check saved logs
cat reports/logs/pod_logs/focus-server_latest.log

# 3. Search for errors
grep -i "error\|exception\|fail" reports/logs/pod_logs/focus-server_latest.log

# 4. Check HTTP logs
grep "→ POST\|← 200\|← 4\|← 5" reports/logs/pytest_execution.log
```

---

## 🚀 Advanced: Custom Log Collector

```python
class CustomLogCollector(PodLogsCollector):
    """Custom log collector with additional features."""
    
    def collect_and_analyze(self, service_name: str):
        """Collect logs and perform analysis."""
        logs = self.collect_logs_for_service(service_name, lines=500)
        
        # Analyze logs
        errors = [line for line in logs.split('\n') if 'ERROR' in line]
        warnings = [line for line in logs.split('\n') if 'WARNING' in line]
        
        # Log summary
        self.logger.info(f"Analysis for {service_name}:")
        self.logger.info(f"  Errors: {len(errors)}")
        self.logger.info(f"  Warnings: {len(warnings)}")
        
        return {
            "service": service_name,
            "errors": errors,
            "warnings": warnings,
            "total_lines": len(logs.split('\n'))
        }
```

---

## 📚 Related Documentation

- [API Healing Guide](API_HEALING_GUIDE.md)
- [Quick Start Guide](../QUICK_START_PZ.md)
- [RabbitMQ Automation](RABBITMQ_AUTOMATION_GUIDE.md)

---

**Created**: 2025-10-12  
**Last Updated**: 2025-10-12  
**Version**: 1.0.0

