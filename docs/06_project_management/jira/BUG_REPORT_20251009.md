# 🐛 Bug Report - Test Failures Analysis
**Date:** October 9, 2025  
**Environment:** Windows 10 (10.0.26100), Python 3.12+  
**Test Suite:** Focus Server Automation Framework  
**Total Failures:** 20 failed, 9 errors out of 159 tests

---

## Executive Summary

This report identifies **4 major issues** discovered during integration test execution:

1. **Validation Logic Error** - Incorrect validation order in ROI commands
2. **Kubernetes API Misuse** - Wrong API method used for version retrieval  
3. **MongoDB Outage Resilience Issues** - Slow failover and insufficient isolation
4. **Infrastructure Connectivity** - Focus Server unavailable (env issue, not code bug)

---

## 🔴 BUG #1: ROI Validation - Incorrect Error Message for Negative Values

### Issue Description
When sending a `RegionOfInterestCommand` with a negative `end` value, the validation raises the wrong error message.

**Expected Behavior:**
```
ValidationError: "Sensor indices must be non-negative"
```

**Actual Behavior:**
```
ValidationError: "end sensor must be > start sensor"
```

### Root Cause
In `src/apis/baby_analyzer_mq_client.py` (lines 346-350), validation checks are in the wrong order:

```python
# Current (WRONG ORDER)
if end <= start:
    raise ValidationError("end sensor must be > start sensor")

if start < 0 or end < 0:
    raise ValidationError("Sensor indices must be non-negative")
```

When calling `send_roi_change(start=0, end=-10)`, the first check catches it (`-10 <= 0`) and returns the wrong message.

### Impact
- **Severity:** Medium
- **User Impact:** Misleading error messages confuse API consumers
- **Test Impact:** `test_roi_with_negative_end` fails

### Recommended Fix
Reorder validation checks - validate non-negative values first:

```python
# Correct order
if start < 0 or end < 0:
    raise ValidationError("Sensor indices must be non-negative")

if end <= start:
    raise ValidationError("end sensor must be > start sensor")
```

### Affected Files
- `src/apis/baby_analyzer_mq_client.py` (lines 346-350)
- `tests/integration/api/test_dynamic_roi_adjustment.py` (test_roi_with_negative_end)

### Automated Test Case
A regression test should be added to verify this specific scenario:

```python
def test_roi_negative_values_validation_order():
    """Verify that negative value validation takes precedence."""
    client = BabyAnalyzerMQClient(...)
    
    with pytest.raises(ValidationError) as exc:
        client.send_roi_change(start=0, end=-10)
    
    # Should mention 'negative' or 'non-negative'
    assert 'negative' in str(exc.value).lower()
```

---

## 🔴 BUG #2: Kubernetes Version API Misuse

### Issue Description
Test `test_kubernetes_direct_connection` fails with:
```
'CoreV1Api' object has no attribute 'get_code'
```

### Root Cause
In `tests/integration/infrastructure/test_basic_connectivity.py` (line 152), the wrong API class is used:

```python
# Current (WRONG)
core_v1 = client.CoreV1Api()
version = core_v1.get_code()  # ❌ CoreV1Api doesn't have get_code()
```

`CoreV1Api` does not provide a `get_code()` method. The correct approach is to use `VersionApi`.

### Impact
- **Severity:** High
- **User Impact:** Kubernetes connectivity tests fail completely
- **Test Impact:** `test_kubernetes_direct_connection` always fails

### Recommended Fix
Use `VersionApi` as shown in `src/infrastructure/kubernetes_manager.py` (lines 406-408):

```python
# Correct implementation
from kubernetes.client import VersionApi

version_api = VersionApi()
version = version_api.get_code()
logger.info(f"Kubernetes Version: {version.git_version}")
```

### Affected Files
- `tests/integration/infrastructure/test_basic_connectivity.py` (line 152)

### Automated Test Case
The existing test will pass once fixed. No additional test needed.

---

## 🔴 BUG #3: MongoDB Outage Resilience - Slow Failover & Insufficient Isolation

### Issue 3.1: Excessive Response Time During Outage

**Issue Description:**
When MongoDB is unavailable, Focus Server takes **15.4 seconds** to return a 503 error, exceeding the acceptable **5-second** threshold.

```
AssertionError: Response time 15.423874139785767s exceeds maximum 5.0s
```

**Root Cause:**
- MongoDB connection timeout is likely set too high (default: 30s)
- No circuit breaker pattern implemented
- Synchronous calls block request processing

**Impact:**
- **Severity:** High (Production Critical)
- **User Impact:** Poor UX during database outages
- **SLA Impact:** Violates 5s response time SLA

**Recommended Fix:**

1. **Reduce MongoDB Connection Timeout:**
   ```python
   # In src/infrastructure/mongodb_manager.py
   self.client = pymongo.MongoClient(
       serverSelectionTimeoutMS=2000,  # 2s instead of 5s
       connectTimeoutMS=2000,
       socketTimeoutMS=2000
   )
   ```

2. **Implement Circuit Breaker:**
   Use `pybreaker` library to fail fast after detecting MongoDB unavailability:
   ```python
   from pybreaker import CircuitBreaker
   
   db_breaker = CircuitBreaker(fail_max=3, timeout_duration=30)
   
   @db_breaker
   def query_mongodb():
       # Database operations
   ```

3. **Add Health Check Caching:**
   Cache MongoDB health status for 5 seconds to avoid repeated timeout checks.

**Affected Files:**
- `src/infrastructure/mongodb_manager.py` (connection configuration)
- `src/apis/focus_server_api.py` (add circuit breaker)

---

### Issue 3.2: MongoDB Pod Remains Reachable After Deletion

**Issue Description:**
After deleting MongoDB pod, the test asserts MongoDB is unreachable, but it remains accessible:

```
AssertionError: MongoDB is still reachable after pod deletion
assert not True
```

**Root Cause:**
Kubernetes **automatically recreates** the pod due to ReplicaSet/Deployment configuration:
- The pod is deleted
- Kubernetes scheduler immediately creates a new pod
- By the time the test checks connectivity (after 5s wait), the new pod is already running

**Impact:**
- **Severity:** Low (Test Design Issue, not Production Bug)
- **User Impact:** None (this is expected Kubernetes behavior)
- **Test Impact:** Test needs redesign to account for Kubernetes self-healing

**Recommended Fix:**

Option 1: **Scale deployment to 0 instead of deleting pod**
```python
def test_mongodb_pod_deletion_outage():
    # Instead of delete_mongodb_pod()
    mongodb_manager.scale_down_mongodb(replicas=0)
    time.sleep(10)  # Wait for scale-down
    
    assert not mongodb_manager.connect(), "MongoDB should be unreachable"
```

Option 2: **Disable auto-restart temporarily**
Set deployment replicas to 0 before deleting pod to prevent recreation.

Option 3: **Accept pod recreation and test different scenario**
Test should verify graceful handling during pod restart (brief outage), not full outage.

**Affected Files:**
- `tests/integration/infrastructure/test_mongodb_outage_resilience.py` (test_mongodb_pod_deletion_outage_returns_503_no_orchestration)
- `src/infrastructure/mongodb_manager.py` (delete_mongodb_pod method)

---

## 🟡 INFRASTRUCTURE ISSUE: Focus Server Connection Refused

### Issue Description
19 tests fail with:
```
Connection failed: HTTPConnectionPool(host='10.10.10.150', port=5000): 
Max retries exceeded... [WinError 10061] No connection could be made 
because the target machine actively refused it
```

### Root Cause
**This is NOT a code bug** - it's an infrastructure/environment issue:
- Focus Server is not running on `10.10.10.150:5000`
- Kubernetes service may not be exposed
- Port-forwarding may be required

### Impact
- **Severity:** Blocker for Integration Tests
- **User Impact:** None (local test environment only)
- **Test Impact:** 19 integration tests cannot run

### Recommended Actions

1. **Verify Focus Server is Running:**
   ```bash
   kubectl get pods -n panda-system | grep focus-server
   kubectl get svc -n panda-system | grep focus-server
   ```

2. **Setup Port Forwarding:**
   ```bash
   kubectl port-forward -n panda-system svc/focus-server 5000:5000
   ```

3. **Update Configuration:**
   If Focus Server runs on a different host/port, update `config/environments.yaml`:
   ```yaml
   focus_server:
     host: "localhost"  # or correct IP
     port: 5000
   ```

4. **Add Pre-Test Connectivity Check:**
   Add a health check before running integration tests:
   ```python
   @pytest.fixture(scope="session", autouse=True)
   def verify_focus_server_available(config_manager):
       host = config_manager.get("focus_server.host")
       port = config_manager.get("focus_server.port")
       
       if not is_port_open(host, port):
           pytest.exit(f"Focus Server not available at {host}:{port}")
   ```

### Affected Tests (19 failures)
All tests in:
- `tests/integration/api/test_historic_playback_flow.py`
- `tests/integration/api/test_live_monitoring_flow.py`
- `tests/integration/api/test_spectrogram_pipeline.py`
- `tests/integration/api/test_dynamic_roi_adjustment.py` (partial)

---

## Priority & Action Items

| Priority | Issue | Action | Owner | ETA |
|----------|-------|--------|-------|-----|
| 🔴 **P0** | BUG #2 - Kubernetes API | Fix `get_code()` usage | Dev Team | 1 day |
| 🔴 **P0** | Infrastructure - Focus Server | Setup port-forward / verify service | DevOps | 1 day |
| 🟠 **P1** | BUG #1 - ROI Validation | Reorder validation checks | Dev Team | 2 days |
| 🟠 **P1** | BUG #3.1 - Slow Failover | Implement circuit breaker | Dev Team | 1 week |
| 🟡 **P2** | BUG #3.2 - Pod Deletion Test | Redesign test or accept behavior | QA Team | 3 days |

---

## Test Coverage Recommendations

1. **Add Unit Tests for Validation Logic:**
   - Test all validation edge cases independently
   - Verify validation order is correct

2. **Add Chaos Engineering Tests:**
   - Random MongoDB outages during load
   - Network latency simulation
   - Gradual degradation scenarios

3. **Add Performance Benchmarks:**
   - Response time under normal conditions
   - Response time during partial outage
   - Recovery time after outage

---

## Appendix: Full Test Results Summary

```
Total Tests:     159
Passed:          137 (86%)
Failed:          20  (13%)
Skipped:         2   (1%)
Errors:          9   (6%)
Duration:        846.04s (14:06)
```

### Failed Tests Breakdown:
- **ROI Validation:** 1 failure
- **Kubernetes API:** 1 failure  
- **MongoDB Outage:** 2 failures
- **Connection Refused:** 16 failures

### Errors Breakdown:
- **Connection Refused:** 9 errors (same root cause as failures)

---

**Report Generated:** October 9, 2025  
**Generated By:** QA Automation Architect  
**Classification:** Internal - Development Team Only

