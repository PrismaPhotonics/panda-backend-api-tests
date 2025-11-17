# Jobs Cleanup Issue - Analysis and Solution

**Date:** 2025-11-09  
**Issue:** Too many gRPC jobs created during test execution

---

## 🔍 Problem Analysis

### Root Causes:

1. **Load Tests Create Many Jobs:**
   - `test_peak_load.py`: 600 requests (10 RPS × 60 seconds)
   - `test_sustained_load.py`: 30+ jobs (1 job every 10 seconds for 5 minutes)
   - `test_concurrent_load.py`: 20 concurrent jobs
   - `test_load_profiles.py`: Multiple load profiles with many jobs
   - `test_recovery_and_exhaustion.py`: Extreme load with many jobs

2. **Cleanup Issues:**
   - Cleanup uses `Exception: pass` - silently fails
   - If test fails, cleanup doesn't run
   - No automatic cleanup fixture
   - Cleanup happens sequentially (slow)

3. **Performance Tests:**
   - `test_concurrent_performance.py`: 10 concurrent requests
   - `test_resource_usage.py`: 10 requests

4. **Total Jobs Created:**
   - Load Tests: ~700+ jobs
   - Performance Tests: ~20 jobs
   - Security/Error Handling: ~50 jobs
   - **Total: ~770+ jobs per full test run**

---

## ✅ Solutions

### Solution 1: Add Automatic Job Cleanup Fixture

Add a fixture that automatically tracks and cleans up jobs:

```python
@pytest.fixture(scope="function", autouse=True)
def auto_cleanup_jobs(focus_server_api: FocusServerAPI):
    """
    Automatically track and cleanup jobs created during test.
    """
    job_ids = []
    
    # Track job creation
    original_configure = focus_server_api.configure_streaming_job
    
    def tracked_configure(*args, **kwargs):
        response = original_configure(*args, **kwargs)
        if response and response.job_id:
            job_ids.append(response.job_id)
        return response
    
    focus_server_api.configure_streaming_job = tracked_configure
    
    yield
    
    # Cleanup all tracked jobs
    if job_ids:
        logger.info(f"Auto-cleanup: Cleaning up {len(job_ids)} jobs...")
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
            except Exception as e:
                logger.warning(f"Failed to cancel job {job_id}: {e}")
```

### Solution 2: Improve Cleanup in Load Tests

1. **Parallel Cleanup:**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor(max_workers=10) as executor:
       executor.map(focus_server_api.cancel_job, job_ids)
   ```

2. **Better Error Handling:**
   ```python
   for job_id in job_ids:
       try:
           focus_server_api.cancel_job(job_id)
           logger.debug(f"Canceled job: {job_id}")
       except APIError as e:
           logger.warning(f"API error canceling job {job_id}: {e}")
       except Exception as e:
           logger.error(f"Unexpected error canceling job {job_id}: {e}")
   ```

3. **Cleanup in finally block:**
   ```python
   try:
       # Test code
   finally:
       # Cleanup always runs
       cleanup_jobs(job_ids)
   ```

### Solution 3: Reduce Job Creation in Load Tests

1. **Use Mock/Stub for Load Tests:**
   - Don't create real jobs for load testing
   - Use mock responses

2. **Reduce Load Test Parameters:**
   - Reduce RPS in peak load test
   - Reduce duration in sustained load test
   - Reduce concurrent jobs

3. **Skip Load Tests by Default:**
   - Mark as `@pytest.mark.slow`
   - Run only with `-m load` flag

---

## 🎯 Recommended Actions

### Immediate (High Priority):

1. ✅ Add automatic cleanup fixture
2. ✅ Improve cleanup error handling
3. ✅ Add cleanup to finally blocks
4. ✅ Reduce load test parameters

### Short Term:

1. Implement parallel cleanup
2. Add job tracking mechanism
3. Add cleanup verification

### Long Term:

1. Consider mock/stub for load tests
2. Implement job pool management
3. Add cleanup monitoring

---

## 📝 Implementation Notes

### Current Cleanup Pattern:
```python
# Cleanup
for job_id in job_ids:
    try:
        focus_server_api.cancel_job(job_id)
    except Exception:
        pass  # ❌ Silently fails
```

### Improved Cleanup Pattern:
```python
# Cleanup with better error handling
def cleanup_jobs(api: FocusServerAPI, job_ids: List[str]):
    """Clean up jobs with proper error handling."""
    if not job_ids:
        return
    
    logger.info(f"Cleaning up {len(job_ids)} jobs...")
    cleaned = 0
    failed = 0
    
    for job_id in job_ids:
        try:
            api.cancel_job(job_id)
            cleaned += 1
        except APIError as e:
            logger.warning(f"API error canceling job {job_id}: {e}")
            failed += 1
        except Exception as e:
            logger.error(f"Unexpected error canceling job {job_id}: {e}")
            failed += 1
    
    logger.info(f"Cleanup complete: {cleaned} canceled, {failed} failed")
```

---

## ⚠️ Current Status

- **Issue:** Too many jobs created
- **Impact:** System overload, resource exhaustion
- **Priority:** HIGH
- **Status:** Needs immediate fix

---

## 🔧 Quick Fix Commands

### Run Tests Without Load Tests:
```bash
pytest tests/integration/security/ tests/integration/error_handling/ tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py tests/integration/data_quality/ -v --tb=short --skip-health-check -m "not load"
```

### Run Only Load Tests (with cleanup):
```bash
pytest tests/integration/load/ -v --tb=short --skip-health-check -m load
```

