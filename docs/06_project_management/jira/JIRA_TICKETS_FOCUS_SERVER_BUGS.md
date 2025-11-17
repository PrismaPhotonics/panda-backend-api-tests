# 🎫 JIRA Bug Tickets - Focus Server Issues
**Generated:** October 9, 2025  
**Source:** Integration Test Suite Failures  
**Priority Classification:** P0 (Critical) → P3 (Minor)

---

## 🔴 TICKET #1: Focus Server - Slow Response During MongoDB Outage (SLA Violation)

### Priority: **P0 - Critical** 🚨

### Component
- **Service:** Focus Server
- **Module:** Database Connection / Error Handling
- **API Endpoint:** POST `/configure`

### Summary
Focus Server returns 503 error after **15.4 seconds** when MongoDB is unavailable, violating the **5-second response time SLA** for error scenarios.

### Environment
- **Test Environment:** Staging (10.10.10.150)
- **Kubernetes Cluster:** panda-system namespace
- **MongoDB:** Scaled down to 0 replicas

### Description

**Expected Behavior:**
When MongoDB is unavailable, Focus Server should detect the failure and return a 503 Service Unavailable error within **5 seconds maximum**.

**Actual Behavior:**
Focus Server takes **15.423 seconds** to return an error response when MongoDB is down.

**Impact:**
- Poor user experience during database outages
- Cascading timeout failures in upstream services
- SLA violation (5-second requirement)
- Resource exhaustion (blocked threads/connections)

### Steps to Reproduce

1. Scale down MongoDB deployment to 0 replicas:
   ```bash
   kubectl scale deployment mongodb --replicas=0 -n panda-system
   ```

2. Wait for MongoDB pods to terminate (5 seconds)

3. Send POST request to Focus Server `/configure` endpoint:
   ```bash
   curl -X POST http://10.10.10.150:5000/config/test_task \
     -H "Content-Type: application/json" \
     -d '{
       "displayTimeAxisDuration": 10,
       "nfftSelection": 1024,
       "canvasInfo": {"height": 1000},
       "sensors": {"min": 1, "max": 3},
       "frequencyRange": {"min": 0, "max": 500},
       "start_time": "250101000000",
       "end_time": "250101001000"
     }'
   ```

4. Measure response time

**Expected:** Response within 5 seconds  
**Actual:** Response after 15.4 seconds

### Root Cause Analysis

**Hypothesis:**
- MongoDB client connection timeout is set too high (likely 30 seconds default)
- No circuit breaker pattern implemented
- Synchronous database calls block request processing
- No health check caching mechanism

**Evidence:**
```
Test: test_mongodb_scale_down_outage_returns_503_no_orchestration
Result: AssertionError: Response time 15.423874139785767s exceeds maximum 5.0s
```

### Recommended Solution

**Option 1: Reduce MongoDB Connection Timeout** ⭐ (Quickest)
```python
# In Focus Server MongoDB client configuration
mongo_client = MongoClient(
    serverSelectionTimeoutMS=2000,  # 2 seconds
    connectTimeoutMS=2000,
    socketTimeoutMS=2000
)
```

**Option 2: Implement Circuit Breaker Pattern** (Best Long-term)
```python
from pybreaker import CircuitBreaker

db_breaker = CircuitBreaker(
    fail_max=3,              # Open circuit after 3 failures
    timeout_duration=30,     # Keep circuit open for 30 seconds
    expected_exception=DatabaseError
)

@db_breaker
def query_mongodb():
    return mongo_client.query(...)
```

**Option 3: Add Health Check Caching**
- Cache MongoDB health status for 5 seconds
- Fail fast if cached status shows MongoDB down
- Async health check in background

### Acceptance Criteria

- [ ] Focus Server returns error response within 5 seconds when MongoDB is unavailable
- [ ] No increase in memory usage during outage
- [ ] Error message clearly indicates database unavailability
- [ ] Response includes proper HTTP status code (503)
- [ ] Automated test `test_mongodb_scale_down_outage_returns_503_no_orchestration` passes

### Test Case for Verification

```python
def test_focus_server_fast_failover():
    """Verify Focus Server fails fast during MongoDB outage."""
    # Scale down MongoDB
    mongodb_manager.scale_down_mongodb(replicas=0)
    time.sleep(5)
    
    # Send configure request
    start_time = time.time()
    with pytest.raises(APIError) as exc:
        focus_server_api.configure_streaming_job(payload)
    
    response_time = time.time() - start_time
    
    # MUST respond within 5 seconds
    assert response_time <= 5.0, f"Response time {response_time}s exceeds 5s SLA"
    assert "503" in str(exc.value), "Should return 503 Service Unavailable"
```

### Related Issues
- None

### Labels
`p0-critical`, `focus-server`, `mongodb`, `performance`, `sla-violation`, `resilience`

---

## 🟠 TICKET #2: MongoDB Pod Deletion - Kubernetes Auto-Recovery Prevents Outage Testing

### Priority: **P2 - Normal**

### Component
- **Service:** MongoDB / Kubernetes Infrastructure
- **Module:** StatefulSet / ReplicaSet Auto-Recovery
- **Test Suite:** MongoDB Outage Resilience Tests

### Summary
When deleting MongoDB pod to simulate failure, Kubernetes **immediately recreates** the pod, making it impossible to test true outage scenarios using pod deletion.

### Environment
- **Kubernetes Version:** 1.28+
- **MongoDB Deployment:** StatefulSet with 1 replica
- **Test:** `test_mongodb_pod_deletion_outage_returns_503_no_orchestration`

### Description

**Expected Behavior:**
After deleting MongoDB pod, the database should be unreachable for a period, allowing outage testing.

**Actual Behavior:**
Kubernetes ReplicaSet controller **immediately schedules a new pod**, and MongoDB becomes available again within 10-15 seconds (pod startup time).

**Impact:**
- Cannot properly test Focus Server behavior during MongoDB outages using pod deletion
- False negatives in resilience testing
- Test suite reports failures that are actually expected Kubernetes behavior

### Steps to Reproduce

1. Get MongoDB pod name:
   ```bash
   kubectl get pods -n panda-system | grep mongodb
   # Output: mongodb-7b8f6d5c9-xk4m2
   ```

2. Delete the pod:
   ```bash
   kubectl delete pod mongodb-7b8f6d5c9-xk4m2 -n panda-system
   ```

3. Check pod status after 5 seconds:
   ```bash
   kubectl get pods -n panda-system | grep mongodb
   # Output: mongodb-7b8f6d5c9-pl9x7  1/1  Running  0  8s
   ```

4. Try to connect to MongoDB:
   ```bash
   mongosh mongodb://10.10.10.150:27017
   # Connected successfully! ✅
   ```

**Expected:** Connection refused (pod deleted)  
**Actual:** Connection successful (new pod created)

### Root Cause Analysis

**Cause:**
This is **expected Kubernetes behavior**, not a bug. The ReplicaSet controller ensures the desired number of replicas (1) is always running. When a pod is deleted, it immediately creates a replacement.

**Current Test Code:**
```python
def test_mongodb_pod_deletion_outage():
    mongodb_manager.delete_mongodb_pod()
    time.sleep(5)
    
    # This assertion FAILS because K8s recreated the pod
    assert not mongodb_manager.connect(), "MongoDB should be unreachable"
```

### Recommended Solution

**Option 1: Scale Deployment to 0 Before Deleting Pod** ⭐ (Simplest)
```python
def test_mongodb_pod_deletion_outage():
    # Prevent pod recreation
    mongodb_manager.scale_down_mongodb(replicas=0)
    time.sleep(10)  # Wait for scale-down
    
    assert not mongodb_manager.connect(), "MongoDB should be unreachable"
```

**Option 2: Test Brief Outage During Pod Restart** (More Realistic)
```python
def test_mongodb_pod_restart_resilience():
    """Test Focus Server handles brief MongoDB outage during pod restart."""
    # Delete pod (will be recreated)
    mongodb_manager.delete_mongodb_pod()
    
    # During recreation window, requests should gracefully fail
    for attempt in range(5):
        try:
            focus_server_api.configure_streaming_job(payload)
            # If successful, pod has restarted
            break
        except APIError as e:
            # Expected during pod recreation
            assert "503" in str(e) or "500" in str(e)
            time.sleep(2)
```

**Option 3: Use Network Policies to Block MongoDB** (Most Complex)
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-mongodb-ingress
spec:
  podSelector:
    matchLabels:
      app: mongodb
  policyTypes:
  - Ingress
  ingress: []  # Deny all ingress
```

### Acceptance Criteria

- [ ] Test suite can successfully simulate MongoDB outages
- [ ] No false test failures due to Kubernetes auto-recovery
- [ ] Test execution time remains reasonable (<2 minutes)
- [ ] Test cleanup properly restores MongoDB

### Decision Needed

**Question for Product/Architecture Team:**

Should we test:
- **A) Complete MongoDB outage** (scale to 0) - tests disaster recovery
- **B) Brief outage during pod restart** (pod deletion) - tests resilience to transient failures

Both scenarios are valuable. Option A is currently implemented but fails due to K8s behavior.

### Related Issues
- Related to TICKET #1 (outage response time)

### Labels
`p2-normal`, `mongodb`, `kubernetes`, `test-infrastructure`, `resilience`, `needs-decision`

---

## 📝 Summary Table

| Ticket | Priority | Component | Type | ETA |
|--------|----------|-----------|------|-----|
| #1 - Slow MongoDB Failover | 🔴 P0 | Focus Server | Performance/SLA | 3 days |
| #2 - Pod Deletion Auto-Recovery | 🟠 P2 | Test Infrastructure | Test Design | 2 days |

---

## Tickets NOT Created (Not System Bugs)

### ✅ Fixed in Code
- **ROI Validation Order** - Fixed in `baby_analyzer_mq_client.py`
- **Kubernetes API Misuse** - Fixed in `test_basic_connectivity.py`

### 🔧 Infrastructure Issues (Not Bugs)
- **Focus Server Connection Refused** - Environment setup issue, not a code bug
  - Action: Setup port-forwarding or verify service availability
  - Not a JIRA ticket - DevOps checklist item

---

**Created By:** QA Automation Architect  
**Date:** October 9, 2025  
**Total Tickets:** 2 (1 Critical, 1 Normal)

