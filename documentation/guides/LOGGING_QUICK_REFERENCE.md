# 🔍 Enhanced Logging - Quick Reference Card

## Quick Commands

```bash
# Basic test run (no extra logs)
pytest tests/integration/api/test_singlechannel_view_mapping.py -v

# With HTTP request/response details
pytest tests/integration/api/test_singlechannel_view_mapping.py -v -s

# With real-time pod logs
pytest tests/integration/api/test_singlechannel_view_mapping.py --collect-pod-logs -v

# With saved pod logs
pytest tests/integration/api/test_singlechannel_view_mapping.py --save-pod-logs -v

# Full debug mode (everything!)
pytest tests/integration/api/test_singlechannel_view_mapping.py --collect-pod-logs --save-pod-logs -v -s -log-cli-level=DEBUG
```

---

## What You Get

| Feature | What It Shows | Command Flag |
|---------|---------------|--------------|
| **HTTP Logs** | Full request/response with timing | Always on (use `-v`) |
| **Pod Logs (Real-time)** | Live logs from Focus Server, RabbitMQ | `--collect-pod-logs` |
| **Pod Logs (Files)** | Saved logs in `reports/logs/pod_logs/` | `--save-pod-logs` |
| **Debug Level** | Headers, full details | `-log-cli-level=DEBUG` |
| **Print Statements** | Your debug prints | `-s` |

---

## HTTP Logging Example

```
================================================================================
→ POST http://10.10.10.150:5000/configure
Request Body (JSON):
  {
    "view_type": "1",
    "channels": {"min": 7, "max": 7},
    ...
  }
← 200 OK (342.56ms)
Response Body (JSON):
  {
    "status": "",
    "stream_amount": 1,
    "channel_to_stream_index": {"7": 0},
    ...
  }
================================================================================
```

---

## Pod Logs Example

```
[focus-server] 2025-10-12 15:44:43 INFO: Received configure request
[focus-server] 2025-10-12 15:44:43 INFO: Job 31-3633 created successfully
[rabbitmq-panda] 2025-10-12 15:44:43 INFO: New connection established
```

---

## Log Locations

```
reports/logs/
├── pytest_execution.log          ← Full test logs
├── pod_logs/
│   ├── focus-server_latest.log   ← Focus Server logs
│   └── rabbitmq-panda_latest.log ← RabbitMQ logs
└── failures/                     ← Logs from failed tests
```

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| No pod logs | Check `config/environments.yaml` for SSH credentials |
| Too much output | Use `-log-cli-level=WARNING` |
| Need only errors | `grep "ERROR" reports/logs/pytest_execution.log` |
| Save specific test logs | Use `--save-pod-logs` |

---

## Configuration (Optional)

Edit `config/environments.yaml`:

```yaml
staging:
  kubernetes:
    ssh_host: "10.10.10.150"
    ssh_user: "prisma"
    ssh_password: "PASSW0RD"
```

---

## Manual Log Collection (Python)

```python
from src.utils.pod_logs_collector import PodLogsCollector

collector = PodLogsCollector("10.10.10.150", "prisma", "PASSW0RD")
collector.connect()

# Get logs
logs = collector.collect_logs_for_service("focus-server", lines=100)
print(logs)

# Save to file
collector.save_logs_to_file("focus-server", "debug.log", lines=500)

collector.disconnect()
```

---

## 🚀 Recommended Usage

### For Daily Development
```bash
pytest tests/ -v
```

### For Debugging Failures
```bash
pytest tests/test_failing.py --collect-pod-logs --save-pod-logs -v -s
```

### For CI/CD
```bash
pytest tests/ --save-pod-logs -v -log-cli-level=INFO
```

### For Deep Debugging
```bash
pytest tests/test_failing.py --collect-pod-logs --save-pod-logs -v -s -log-cli-level=DEBUG > full_output.txt 2>&1
```

---

**Full Documentation**: [Enhanced Logging Guide](docs/ENHANCED_LOGGING_GUIDE.md)

