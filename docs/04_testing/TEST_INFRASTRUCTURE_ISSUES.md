# Test Infrastructure Issues Analysis

> **Author:** QA Automation Architect  
> **Date:** December 2025  
> **Status:** Active Documentation

## Overview

This document provides a comprehensive analysis of test failures, categorizing them into:
1. **Test Infrastructure Issues** - Problems in the test framework, not system bugs
2. **Potential System Bugs** - Issues requiring verification before opening bugs
3. **Confirmed System Bugs** - Actual bugs in the Focus Server system

---

## 1. Test Infrastructure Issues (NOT System Bugs)

These are failures caused by the test framework, not by Focus Server.

### 1.1 K8s Manager SSH Fallback (6 failures)

**Symptom:** `k8s_apps_v1 is None`

**Root Cause:**  
The `KubernetesManager` wasn't properly handling SSH fallback mode. When SSH fallback was used, direct K8s API clients (`k8s_apps_v1`, `k8s_core_v1`) remained `None`, but tests checked them directly instead of using the proper availability check.

**Fix Applied:**
- Added `is_k8s_available()` method to `KubernetesManager` and `MongoDBManager`
- Updated `_ensure_k8s_available()` to check both SSH fallback and direct API
- Updated tests to use `is_k8s_available()` instead of checking `k8s_apps_v1 is None`

**Files Modified:**
- `src/infrastructure/kubernetes_manager.py`
- `src/infrastructure/mongodb_manager.py`
- `be_focus_server_tests/performance/test_mongodb_outage_resilience.py`

---

### 1.2 Pydantic Validation Errors (3 failures)

**Symptom:** `displayTimeAxisDuration not applicable for waterfall`

**Root Cause:**  
Tests were sending `displayTimeAxisDuration` and `frequencyRange` for waterfall view type, which is explicitly forbidden by the Pydantic model validation.

**Solution:**
- Use `build_configure_request()` factory function for creating requests
- Waterfall views do NOT support:
  - `displayTimeAxisDuration`
  - `frequencyRange`
  - `nfftSelection` must be `1`

**Correct Usage:**

```python
from src.models.focus_server_models import build_configure_request, ViewType

# Waterfall request (automatically omits unsupported fields)
req = build_configure_request(ViewType.WATERFALL)

# Multichannel/Singlechannel request (supports all parameters)
req = build_configure_request(ViewType.MULTICHANNEL)
```

---

### 1.3 Config Loading Failures (6 failures)

**Symptom:** `test_load_staging_config failed` - Environment not found

**Root Cause:**  
Missing `local` environment in `environments.yaml`. Tests referenced this environment but it wasn't defined.

**Fix Applied:**
- Added `local` environment configuration
- Verified `kefar_saba` environment is the production-like environment
- Updated test configurations for all environments
- Added singleton reset fixture for config tests

**Files Modified:**
- `config/environments.yaml`
- `be_focus_server_tests/unit/test_config_loading.py`

---

### 1.4 Rate Limiting (429 Too Many Requests)

**Symptom:** Tests fail with 429 status code when making many API calls

**Root Cause:**  
Tests didn't implement proper rate limiting handling. The system correctly implements rate limiting, but tests need to respect it.

**Fix Applied:**
Created new utilities in `src/utils/helpers.py`:

1. **`retry_with_backoff` decorator:**
   - Exponential backoff
   - Respects `Retry-After` headers
   - Configurable retry parameters
   - Jitter to prevent thundering herd

2. **`RateLimiter` class:**
   - Token bucket algorithm
   - Thread-safe
   - Configurable rate and burst limits

**Usage Example:**

```python
from src.utils.helpers import retry_with_backoff, RateLimiter

# Decorator approach
@retry_with_backoff(max_retries=5, initial_delay=1.0)
def make_api_call():
    response = api.configure(config)
    return response

# Rate limiter approach
limiter = RateLimiter(rate=10, per=1.0)  # 10 requests/second

for config in configs:
    limiter.wait()  # Blocks if rate limit exceeded
    api.configure(config)
```

---

### 1.5 RabbitMQ Connection Reset

**Symptom:** `ConnectionResetError` during tests

**Status:** ⚠️ Requires Investigation

**Possible Causes:**
1. Network/infrastructure issues in test environment
2. RabbitMQ broker restarting
3. Connection pool exhaustion

**Actions Required:**
- Check RabbitMQ logs during test execution
- Check Focus Server logs for connection errors
- Verify network stability

---

## 2. Issues Requiring Verification

These issues need confirmation before opening system bugs.

### 2.1 MongoDB Schema - Missing `start_time` Field

**Symptom:** `Required field 'start_time' missing from schemaDocument`

**Questions to Verify:**
- Is this document from `recordings` collection or `unrecognized_recordings`?
- What is the document type (recording vs system doc)?

**Action:** Verify with development team which collection/doctype is expected.

---

### 2.2 Missing MongoDB Indexes

**Symptom:** Test reports missing indexes `['start_time', 'end_time', 'uuid']`

**Possible Causes:**
1. Indexes not deployed to staging
2. Test looking at wrong collection/database
3. DB migration not run

**Action:** Verify with DBA/DevOps team.

---

### 2.3 Metadata - Missing `dy` Field

**Symptom:** `hasattr(LiveMetadataFlat(...), 'dy') = False`

**Question:** Is `dy` a required field or optional?

**Action:** Check with algorithms team if `dy` is mandatory.

---

### 2.4 Calculation Discrepancies

**Symptom:**
- Frequency resolution: Expected 1.953 Hz, Actual 3.891 Hz
- Frequency bins: Expected 129, Actual 64

**Possible Causes:**
1. Algorithm change not updated in tests
2. Decimation/optimization changes
3. FFT parameter changes

**Action:** Review with algorithms team.

---

### 2.5 ROI Data Size Inconsistency

**Symptom:** Different ROIs produce different data sizes

**Question:** Is this expected behavior?

**Action:** Verify with API documentation/product team.

---

## 3. Confirmed System Bugs

### 3.1 Job Cleanup Failure (Issue #26)

**Severity:** HIGH  
**Status:** Open Bug

**Symptom:** 25 jobs required aggressive cleanup after cancel/failure

**Impact:**
- Resource leak
- State corruption
- Increased cluster load

**Recommendation:** Keep Issue #26 open, document scenarios.

---

### 3.2 Alert Validation Gap (Issue #29)

**Severity:** MEDIUM-HIGH  
**Status:** Needs Spec Clarification

**Symptoms:**
- Invalid class IDs not rejected
- Invalid DOF values not rejected
- Missing required fields not validated

**Recommendation:** 
- Verify validation requirements with product team
- If validation is required, keep as bug
- If validation is optional, update tests

---

## 4. Summary Table

| Issue | Category | Priority | Status |
|-------|----------|----------|--------|
| K8s Manager SSH Fallback | Infrastructure | Fixed | ✅ |
| Pydantic Validation | Infrastructure | Documented | ✅ |
| Config Loading | Infrastructure | Fixed | ✅ |
| Rate Limiting | Infrastructure | Fixed | ✅ |
| RabbitMQ Connection | Infrastructure | Investigation | 🔄 |
| MongoDB Schema | Needs Verification | - | ❓ |
| Missing Indexes | Needs Verification | - | ❓ |
| Metadata dy Field | Needs Verification | - | ❓ |
| Calculation Discrepancies | Needs Verification | - | ❓ |
| ROI Data Size | Needs Verification | - | ❓ |
| Job Cleanup | System Bug | HIGH | 🔴 |
| Alert Validation | System Bug | MEDIUM | 🟡 |

---

## 5. Recommended Actions

### 5.1 For Test Infrastructure Issues

1. **Issue #27 (K8s Manager)**: ✅ Fixed - now supports SSH fallback properly
2. **Issue #28 (Config Loading)**: ✅ Fixed - added missing environments

### 5.2 For Verification Items

Create investigation tickets for:
- MongoDB schema verification
- Index verification with DBA
- Algorithm parameter validation

### 5.3 For System Bugs

- **Issue #26 (Job Cleanup)**: Keep open, add test scenarios
- **Issue #29 (Alert Validation)**: Mark as "Needs Spec Clarification"

---

## 6. Test Framework Hardening Epic

Create an Epic/Story for "Focus Server Test Framework Hardening":

### Tasks:
- [x] Fix Kubernetes manager SSH fallback initialization
- [x] Align Pydantic models with API schema
- [x] Fix config loading for all environments
- [x] Add rate limiting handling (retry/backoff)
- [ ] Add RabbitMQ connection resilience
- [ ] Create comprehensive test fixtures
- [ ] Add automatic environment validation

---

## Appendix: Code Examples

### A. Using retry_with_backoff

```python
from src.utils.helpers import retry_with_backoff

@retry_with_backoff(
    max_retries=5,
    initial_delay=1.0,
    max_delay=60.0,
    backoff_factor=2.0
)
def configure_job(api, config):
    """Configure a job with automatic retry on rate limiting."""
    response = api.configure_streaming_job(config)
    return response
```

### B. Using RateLimiter

```python
from src.utils.helpers import RateLimiter

# Create a limiter: 10 requests per second
limiter = RateLimiter(rate=10, per=1.0)

def bulk_configure(api, configs):
    """Configure multiple jobs with rate limiting."""
    results = []
    for config in configs:
        limiter.wait()  # Wait if rate limit exceeded
        results.append(api.configure_streaming_job(config))
    return results
```

### C. Checking K8s Availability

```python
from src.infrastructure.kubernetes_manager import KubernetesManager

def test_k8s_operation(kubernetes_manager):
    # Proper way to check K8s availability
    if not kubernetes_manager.is_k8s_available():
        pytest.skip("K8s not available")
    
    # Now safe to use K8s operations
    pods = kubernetes_manager.get_pods()
```

---

*Document maintained by QA Automation Team*
