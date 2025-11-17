# Real-time Pod Log Monitoring for Tests

This document explains the real-time pod log monitoring feature that captures and associates logs with specific tests.

## Overview

The real-time pod monitoring system:
- **Connects via SSH** to the Kubernetes worker node
- **Monitors pod logs** in real-time during test execution
- **Associates logs** with the specific test that's running
- **Detects errors** automatically using pattern matching
- **Saves test-specific logs** to files for debugging

## How It Works

### 1. Architecture

```
┌─────────────────┐
│  Pytest Suite   │
│                 │
│  Test 1 ────────┼─────► [PodLogMonitor] ────► SSH ────► Kubernetes Pod Logs
│  Test 2 ────────┤                                            (Focus Server,
│  Test 3 ────────┤                                             MongoDB, etc.)
│  ...            │
└─────────────────┘
```

### 2. Components

**`PodLogMonitor` (src/utils/realtime_pod_monitor.py)**
- Manages SSH connection to worker node
- Spawns monitoring threads for each service
- Associates logs with currently running test
- Detects errors using pattern matching
- Saves logs to test-specific files

**Pytest Fixtures (tests/conftest.py)**
- `pod_monitor`: Session-scoped fixture that starts/stops monitoring
- `track_test_in_pod_monitor`: Auto-runs for EVERY test to set context
- `get_test_pod_logs`: Get logs for current test
- `assert_no_pod_errors`: Assert no errors occurred in pods during test

### 3. Usage

#### Enable Monitoring

```bash
# Run tests with real-time pod monitoring
py -m pytest tests/ --monitor-pods -v
```

#### Automatic Test Association

Every test automatically has its logs tracked:

```python
def test_focus_server_api_call():
    # Monitor automatically knows this test is running
    # All pod logs during this test are associated with it
    response = focus_server_api.get_channels()
    assert response.status_code == 200
    # Logs saved to: logs/pod_logs/test_logs/test_focus_server_api_call_*.log
```

#### Manual Log Access

```python
def test_with_log_validation(get_test_pod_logs):
    # ... perform test actions ...
    
    # Get all pod logs captured during this test
    logs = get_test_pod_logs()
    
    # Validate logs
    assert any("Successfully processed" in line for line in logs)
```

#### Assert No Pod Errors

```python
def test_critical_operation(assert_no_pod_errors):
    # ... perform critical operation ...
    
    # At the end, verify no errors occurred in pods
    assert_no_pod_errors()
    # Will FAIL the test if any errors detected in Focus Server, MongoDB, etc.
```

## Log Files Structure

```
logs/pod_logs/
├── panda-panda-focus-server_realtime.log       # All Focus Server logs
├── panda-panda-focus-server_errors.log         # Focus Server errors only
├── mongodb_realtime.log                         # All MongoDB logs
├── mongodb_errors.log                           # MongoDB errors only
├── rabbitmq-panda_realtime.log                 # All RabbitMQ logs
├── rabbitmq-panda_errors.log                   # RabbitMQ errors only
│
└── test_logs/                                   # Test-specific logs
    ├── test_focus_server_configure_20251026_120545.log
    ├── test_focus_server_configure_20251026_120545_ERRORS.log
    ├── test_mongodb_connection_20251026_120550.log
    └── ...
```

## Error Detection

The monitor automatically detects log lines containing:
- `error`, `ERROR`
- `exception`, `Exception`, `EXCEPTION`
- `failed`, `FAILED`
- `timeout`, `TIMEOUT`
- `panic`, `PANIC`
- `fatal`, `FATAL`
- `crash`, `CRASH`
- `traceback`, `Traceback`

## Configuration

### Monitored Services

By default, the following services are monitored:

1. **panda-panda-focus-server** (Focus Server backend)
2. **mongodb** (Database)
3. **rabbitmq-panda** (Message broker)

### SSH Configuration

The monitor uses SSH configuration from `config/environments.yaml`:

```yaml
new_production:
  ssh:
    target_host:
      host: "10.10.100.113"
      username: "prisma"
      password: "PASSW0RD"
  kubernetes:
    namespace: "panda"
```

## Example Test Run

```bash
# Run tests with pod monitoring
py -m pytest tests/integration/api/ --monitor-pods -v
```

**Output:**
```
================================================================================
REAL-TIME POD MONITORING: Starting...
================================================================================
Starting monitoring for 3 services...
Monitoring pod: panda-panda-focus-server-7d8f9c5b6-x4k2p for service panda-panda-focus-server
Monitoring pod: mongodb-0 for service mongodb
Monitoring pod: rabbitmq-panda-0 for service rabbitmq-panda
Real-time pod monitoring active
================================================================================

================================================================================
TEST STARTED: test_config_validation_high_priority.py::test_valid_live_configuration
================================================================================
[2025-10-26 12:05:45.123] [panda-panda-focus-server] Received POST /configure request
[2025-10-26 12:05:45.234] [panda-panda-focus-server] Configuration validated successfully
[2025-10-26 12:05:45.345] [panda-panda-focus-server] Job created: job_id=12-70788
================================================================================
TEST FINISHED: test_config_validation_high_priority.py::test_valid_live_configuration
================================================================================
Saved logs for test: test_valid_live_configuration -> logs/pod_logs/test_logs/test_valid_live_configuration_20251026_120545.log

PASSED

================================================================================
REAL-TIME POD MONITORING: Stopping...
================================================================================
Monitored 28 tests
Detected 3 errors in pod logs
Tests with pod errors: 2
  - test_invalid_frequency_range
  - test_ambiguous_mode_detection
================================================================================
REAL-TIME POD MONITORING: Complete
================================================================================
```

## Benefits

1. **Automatic Context** - No need to manually correlate test failures with pod logs
2. **Error Detection** - Automatically highlights errors from any monitored service
3. **Test-Specific Logs** - Each test gets its own log file
4. **Debugging** - Quickly see what happened in pods during a specific test
5. **CI/CD Integration** - Can be enabled in CI pipelines to capture all logs

## Advanced Usage

### Custom Error Detection

To detect custom error patterns, modify `realtime_pod_monitor.py`:

```python
self.error_patterns = [
    "error",
    "ERROR",
    # Add custom patterns
    "connection refused",
    "no space left",
    "out of memory",
]
```

### Monitor Additional Services

To monitor more services, update `conftest.py`:

```python
services_to_monitor = [
    ("panda-panda-focus-server", "app.kubernetes.io/name=panda-panda-focus-server"),
    ("mongodb", "app.kubernetes.io/instance=mongodb"),
    ("rabbitmq-panda", "app.kubernetes.io/instance=rabbitmq-panda"),
    # Add more services
    ("grpc-service", "app=grpc-service"),
]
```

## Troubleshooting

### Monitoring Not Starting

**Problem:** `SSH credentials not configured - pod monitoring disabled`

**Solution:** Ensure SSH configuration is correct in `config/environments.yaml`

### No Logs Captured

**Problem:** Logs are empty or missing

**Solution:**
1. Check SSH connection: `ssh prisma@10.10.100.113`
2. Verify pods are running: `kubectl get pods -n panda`
3. Check pod selector labels match actual pods

### High CPU Usage

**Problem:** Monitoring consumes too much CPU

**Solution:** Reduce number of monitored services or add log filtering

## See Also

- `src/utils/realtime_pod_monitor.py` - Main implementation
- `tests/conftest.py` - Pytest fixtures
- `config/environments.yaml` - SSH configuration

