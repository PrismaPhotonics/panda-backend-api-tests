# Pre-Test Health Check - Integration Guide
============================================

## Overview

The pre-test health check script (`scripts/pre_test_health_check.py`) is now **automatically integrated** into the pytest test execution flow as a **PRECONDITION**.

## How It Works

### Automatic Execution

The health check runs **automatically** before every test session:

1. **Before tests start**: Health check verifies all system components
2. **If all checks pass**: Tests proceed normally
3. **If any check fails**: Tests are **blocked** and pytest exits with error code 1

### Components Checked

The health check verifies:

- ✅ **Focus Server API** - Connectivity and `/ack` endpoint
- ✅ **MongoDB** - Connection and status via Kubernetes
- ✅ **Kubernetes** - API connectivity, cluster info, SSH fallback
- ✅ **RabbitMQ** - Service discovery and credential extraction
- ✅ **SSH** - Connection to target host (with jump host support)

## Usage

### Normal Execution (Health Check Enabled)

```bash
# Health check runs automatically
pytest tests/

# With specific environment
pytest tests/ --env=staging
```

### Skip Health Check (Not Recommended)

```bash
# Skip health check (use only for debugging)
pytest tests/ --skip-health-check
```

### Standalone Health Check

You can also run the health check script directly:

```bash
# Run health check standalone
python scripts/pre_test_health_check.py --env=staging
```

## Behavior

### When Health Check Passes

```
================================================================================
PRE-TEST HEALTH CHECK: Verifying system components...
================================================================================
✅ Focus Server API: OK
✅ MongoDB: OK
✅ Kubernetes: OK
✅ RabbitMQ: OK
✅ SSH: OK
================================================================================
✅ PRE-TEST HEALTH CHECK: All components OK - Proceeding with tests
================================================================================
```

### When Health Check Fails

```
================================================================================
PRE-TEST HEALTH CHECK: Verifying system components...
================================================================================
✅ Focus Server API: OK
❌ MongoDB: FAILED
   Error: MongoDB has no ready replicas
✅ Kubernetes: OK
✅ RabbitMQ: OK
✅ SSH: OK
================================================================================
❌ PRE-TEST HEALTH CHECK: Some components failed - Tests will not run
   ❌ MongoDB: MongoDB has no ready replicas
================================================================================

================================================================================
PRE-TEST HEALTH CHECK FAILED
================================================================================
One or more system components are not ready:

  ❌ MongoDB: MongoDB has no ready replicas

Please fix the issues before running tests.
Use --skip-health-check to bypass this check (not recommended).
================================================================================
```

**Result**: pytest exits with code 1, tests do not run.

## Configuration

The health check uses the same environment configuration as pytest:

- `--env=staging` (default)
- `--env=production`
- `--env=local` (health check may skip some components)

## Integration Points

### In `conftest.py`

The health check is integrated in `pytest_configure()` hook:

```python
def pytest_configure(config):
    # ... markers registration ...
    
    # Run pre-test health checks automatically before all tests
    # This is a PRECONDITION - tests will not run if health checks fail
    skip_health_check = config.getoption("--skip-health-check", default=False)
    
    if not skip_health_check:
        # Run health checks
        checker = PreTestHealthChecker(environment=env)
        all_passed, results = checker.run_all_checks()
        
        if not all_passed:
            pytest.exit("Pre-test health check failed...", returncode=1)
```

### Script Location

- **Script**: `scripts/pre_test_health_check.py`
- **Class**: `PreTestHealthChecker`
- **Integration**: `tests/conftest.py` → `pytest_configure()`

## Benefits

1. **Early Failure Detection**: Catch infrastructure issues before running tests
2. **Time Saving**: Don't waste time running tests if system is not ready
3. **Clear Error Messages**: Detailed information about what failed
4. **Consistent Behavior**: Same health check for all test runs

## Troubleshooting

### Health Check Fails Unexpectedly

1. Check the error message for specific component failure
2. Verify infrastructure is running:
   ```bash
   # Run health check standalone to see details
   python scripts/pre_test_health_check.py --env=staging
   ```
3. Check SSH connectivity and credentials
4. Verify Kubernetes cluster is accessible

### Skip Health Check (Debugging Only)

```bash
# Use only when debugging - not recommended for normal runs
pytest tests/ --skip-health-check
```

**Warning**: Skipping health checks may result in test failures due to infrastructure issues.

## Notes

- The health check script (`pre_test_health_check.py`) is **not modified** - it remains standalone and can be run independently
- Health check results are logged to pytest output
- Failed health checks prevent test execution (fail-fast approach)
- Health check respects environment configuration (`--env` flag)

