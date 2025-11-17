# Pod Monitoring Configuration for gRPC Jobs

## Overview

This document explains how to configure the real-time pod monitoring system to track gRPC jobs dynamically.

---

## Current Limitation

The current monitoring configuration in `tests/conftest.py` monitors **static services**:

```python
services_to_monitor = [
    ("panda-panda-focus-server", "app.kubernetes.io/name=panda-panda-focus-server"),
    ("mongodb", "app.kubernetes.io/instance=mongodb"),
    ("rabbitmq-panda", "app.kubernetes.io/instance=rabbitmq-panda"),
]
```

**Problem:** gRPC jobs are **dynamic** - they're created on-demand with unique IDs like `grpc-job-12-70788`.

---

## Solution: Dynamic gRPC Job Monitoring

### Option 1: Monitor All gRPC Jobs (Wildcard)

Use a label selector that matches all gRPC jobs:

```python
# In tests/conftest.py, add to services_to_monitor:
services_to_monitor = [
    ("panda-panda-focus-server", "app.kubernetes.io/name=panda-panda-focus-server"),
    ("mongodb", "app.kubernetes.io/instance=mongodb"),
    ("rabbitmq-panda", "app.kubernetes.io/instance=rabbitmq-panda"),
    
    # Monitor ALL gRPC jobs (wildcard)
    ("grpc-jobs-all", "app"),  # Matches app=grpc-job-*
]
```

**How it works:**
- Monitors ALL pods with label `app` that contain "grpc-job"
- Captures logs from all active gRPC jobs
- Groups them under "grpc-jobs-all" in log files

**Pros:**
- Automatically captures all gRPC jobs
- No need to know job_id in advance
- Works for concurrent jobs

**Cons:**
- All gRPC jobs logs mixed together
- Harder to correlate specific job_id with test

### Option 2: Monitor Specific Job ID

Monitor a specific gRPC job created during a test:

```python
def test_with_grpc_monitoring(pod_monitor, focus_server_api):
    # Create gRPC job
    response = focus_server_api.configure(payload)
    job_id = response.json()["job_id"]
    
    # Start monitoring this specific job
    if pod_monitor:
        pod_monitor.start_monitoring_service(
            service_name=f"grpc-job-{job_id}",
            pod_selector=f"app=grpc-job-{job_id}"
        )
    
    # Test proceeds...
    # Logs are captured and associated with this test
```

**Pros:**
- Precise - only monitors the job created by this test
- Clear association between test and logs

**Cons:**
- Requires test code changes
- Monitoring starts after job creation (might miss initial logs)

### Option 3: Enhanced PodLogMonitor with Dynamic Detection

Update `PodLogMonitor` to automatically detect and monitor new gRPC jobs:

```python
# In src/utils/realtime_pod_monitor.py

def start_monitoring_all_grpc_jobs(self):
    """
    Automatically detect and monitor all gRPC jobs.
    Spawns a watcher thread that monitors for new jobs.
    """
    def _watch_for_grpc_jobs():
        while self.is_monitoring:
            # List all gRPC job pods
            cmd = f"kubectl get pods -n {self.namespace} -l app --no-headers | grep grpc-job"
            stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
            output = stdout.read().decode().strip()
            
            if output:
                for line in output.split('\n'):
                    parts = line.split()
                    if len(parts) > 0:
                        pod_name = parts[0]
                        
                        # Extract job_id from pod name
                        # Format: grpc-job-12-70788-xxxxx
                        if pod_name.startswith("grpc-job-"):
                            job_id = "-".join(pod_name.split("-")[2:4])  # "12-70788"
                            service_name = f"grpc-job-{job_id}"
                            
                            # Start monitoring if not already monitored
                            if service_name not in self.monitored_services:
                                self.logger.info(f"Detected new gRPC job: {service_name}")
                                self.start_monitoring_service(
                                    service_name=service_name,
                                    pod_selector=f"app=grpc-job-{job_id}"
                                )
            
            # Check every 5 seconds
            time.sleep(5)
    
    # Start watcher thread
    watcher_thread = threading.Thread(
        target=_watch_for_grpc_jobs,
        daemon=True,
        name="GrpcJobWatcher"
    )
    watcher_thread.start()
    self.logger.info("Started automatic gRPC job detection")
```

**Pros:**
- Fully automatic
- Monitors all gRPC jobs without test code changes
- Each job gets its own log file

**Cons:**
- More complex implementation
- Slight delay (5 seconds) before new jobs are detected

---

## Recommended Approach

**For most use cases: Option 1 (Monitor All gRPC Jobs)**

```python
# In tests/conftest.py, line ~758

services_to_monitor = [
    ("panda-panda-focus-server", "app.kubernetes.io/name=panda-panda-focus-server"),
    ("mongodb", "app.kubernetes.io/instance=mongodb"),
    ("rabbitmq-panda", "app.kubernetes.io/instance=rabbitmq-panda"),
    ("grpc-jobs", "app"),  # Add this line - monitors all grpc-job pods
]
```

**Log files will be:**
```
logs/pod_logs/
├── panda-panda-focus-server_realtime.log
├── mongodb_realtime.log
├── rabbitmq-panda_realtime.log
├── grpc-jobs_realtime.log              # All gRPC job logs
├── grpc-jobs_errors.log                # All gRPC job errors
└── test_logs/
    └── test_configure_live_mode_20251026_120545.log  # Includes gRPC logs
```

---

## Example: Monitoring gRPC Jobs

### Before (No gRPC Monitoring)

```bash
py -m pytest tests/integration/api/test_config_validation_high_priority.py::test_valid_live_configuration --monitor-pods -v
```

**Output:**
```
[2025-10-26 12:05:45.123] [panda-panda-focus-server] Received POST /configure request
[2025-10-26 12:05:45.234] [panda-panda-focus-server] Configuration validated successfully
[2025-10-26 12:05:45.345] [panda-panda-focus-server] Job created: job_id=12-70788
# ❌ No logs from grpc-job-12-70788 itself
```

### After (With gRPC Monitoring)

```bash
py -m pytest tests/integration/api/test_config_validation_high_priority.py::test_valid_live_configuration --monitor-pods -v
```

**Output:**
```
[2025-10-26 12:05:45.123] [panda-panda-focus-server] Received POST /configure request
[2025-10-26 12:05:45.234] [panda-panda-focus-server] Configuration validated successfully
[2025-10-26 12:05:45.345] [panda-panda-focus-server] Job created: job_id=12-70788
[2025-10-26 12:05:46.123] [grpc-jobs] Starting gRPC server on port 5000
[2025-10-26 12:05:46.234] [grpc-jobs] Connected to RabbitMQ: data-rabbitmq.prismaphotonics.net
[2025-10-26 12:05:46.345] [grpc-jobs] Streaming spectrogram data to client
[2025-10-26 12:05:47.456] [grpc-jobs] Frame sent: 1/100
[2025-10-26 12:05:47.567] [grpc-jobs] Frame sent: 2/100
# ✅ Full gRPC job logs captured!
```

---

## Implementation

### Step 1: Update `tests/conftest.py`

Find the `services_to_monitor` list (around line 758) and add:

```python
services_to_monitor = [
    ("panda-panda-focus-server", "app.kubernetes.io/name=panda-panda-focus-server"),
    ("mongodb", "app.kubernetes.io/instance=mongodb"),
    ("rabbitmq-panda", "app.kubernetes.io/instance=rabbitmq-panda"),
    ("grpc-jobs", "app"),  # ← ADD THIS LINE
]
```

### Step 2: Run Tests with Monitoring

```bash
py -m pytest tests/ --monitor-pods -v
```

### Step 3: Review Logs

```bash
# View all gRPC job logs
cat logs/pod_logs/grpc-jobs_realtime.log

# View gRPC job errors only
cat logs/pod_logs/grpc-jobs_errors.log

# View test-specific logs (includes gRPC logs)
cat logs/pod_logs/test_logs/test_valid_live_configuration_*.log
```

---

## Advanced: Filter gRPC Job Logs

If you want to monitor only specific gRPC jobs (e.g., ignore cleanup jobs):

### Update `src/utils/realtime_pod_monitor.py`

Modify the `_monitor_pod_logs` method to filter pods:

```python
def _monitor_pod_logs(self, service_name: str, pod_selector: str):
    self.is_monitoring = True
    
    try:
        # Get pod name
        cmd = f"kubectl get pods -n {self.namespace} -l {pod_selector} -o jsonpath='{{.items[0].metadata.name}}'"
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
        pod_name = stdout.read().decode().strip()
        
        # Filter: Only monitor grpc-job-*, not cleanup-job-*
        if service_name == "grpc-jobs":
            if not pod_name.startswith("grpc-job-"):
                self.logger.debug(f"Skipping non-grpc-job pod: {pod_name}")
                return
        
        # ... rest of monitoring code ...
```

---

## Troubleshooting

### Problem: No gRPC Job Logs Captured

**Possible Causes:**
1. gRPC jobs are not running (all Pending)
2. Label selector doesn't match gRPC job pods
3. SSH connection issue

**Solution:**
```bash
# Check if gRPC jobs are running
ssh prisma@10.10.100.113
kubectl get pods -n panda | grep grpc-job

# Check labels
kubectl get pods -n panda -l app | grep grpc-job

# If no results, jobs are not running (likely Pending)
```

### Problem: Too Many Logs (Performance Issue)

**Solution:** Filter out verbose messages in `realtime_pod_monitor.py`:

```python
def _process_log_line(self, service_name: str, line: str):
    # Skip debug/verbose lines
    if "DEBUG" in line or "TRACE" in line:
        return
    
    # ... rest of processing ...
```

---

## Summary

| Monitoring Approach | Pros | Cons | Best For |
|---------------------|------|------|----------|
| **Static services only** | Simple, fast | Misses gRPC job logs | Basic debugging |
| **Monitor all gRPC jobs** | Automatic, comprehensive | Mixed logs | Most use cases ✅ |
| **Monitor specific job** | Precise | Requires code changes | Detailed debugging |
| **Dynamic detection** | Fully automatic, separate logs per job | Complex | Advanced scenarios |

**Recommended:** Start with **Monitor all gRPC jobs** (Option 1), then move to dynamic detection if needed.

