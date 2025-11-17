# System Behavior Tests

**Created:** 27 October 2025  
**Related:** PZ-13756 (Meeting decision - System Behavior in scope)

---

## Purpose

These tests validate Focus Server infrastructure behavior and stability.

## Tests Included

1. **test_focus_server_clean_startup()**
   - Validates: Startup sequence
   - Checks: Pod running, health check, dependencies, no errors
   
2. **test_focus_server_stability_over_time()** ⚠️ 1 HOUR
   - Validates: Extended stability
   - Checks: No memory leaks, stable CPU, no crashes
   - Duration: 1 hour (skipped by default)
   
3. **test_predictable_error_no_data_available()**
   - Validates: Clear error when no data
   - Checks: HTTP 404/503, clear message, no crash
   
4. **test_predictable_error_port_in_use()**
   - Validates: Port conflict handling
   - Checks: HTTP 409, clear message, proper cleanup
   
5. **test_proper_rollback_on_job_creation_failure()**
   - Validates: Rollback on failure
   - Checks: No partial state, pods cleaned up, system recovers

## Running Tests

```bash
# All system behavior tests (excluding slow tests)
pytest tests/infrastructure/test_system_behavior.py -v -m "not slow"

# Include 1-hour stability test
pytest tests/infrastructure/test_system_behavior.py -v

# Specific test
pytest tests/infrastructure/test_system_behavior.py::TestFocusServerCleanStartup -v

# With markers
pytest -m "infrastructure and error_handling" -v
pytest -m "infrastructure and critical" -v
```

## Expected Duration

- Quick tests (4 tests): ~2-3 minutes
- With stability test (1 hour): ~65 minutes

## Success Criteria

- Clean startup with no errors
- Stable operation over time
- Predictable error responses
- Proper cleanup on failures

