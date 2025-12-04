# 🚀 Gradual Live Job Load Test

## Overview

The Gradual Load Test is a **step-up load testing** strategy that validates system behavior under increasing load:

```
Step 1:   5 jobs → Health Check ✓
Step 2:  10 jobs → Health Check ✓
Step 3:  15 jobs → Health Check ✓
...
Step 10: 50 jobs → Health Check ✓
...
Step 15: 75 jobs → Health Check ✓
...
Step 20: 100 jobs → Final Health Check → Cleanup
```

## Test Flow

1. **Start**: Creates 5 concurrent live jobs
2. **Step Up**: Every 10 seconds, adds 5 more jobs
3. **Health Check**: At each step, validates system health:
   - API responsiveness
   - Job success rate
   - System stability
4. **Maximum Load**: Reaches 100 concurrent jobs (Yonatan's requirement)
5. **Final Check**: Performs comprehensive health validation
6. **Cleanup**: Stops all jobs and cleans up resources

## What It Tests

- ✅ System handles incremental load increases
- ✅ Performance remains acceptable as load grows
- ✅ System detects breaking point (if any)
- ✅ Proper cleanup after high load
- ✅ API remains responsive under stress

## Running the Tests

### Quick Test (2 → 10 jobs)

```bash
# Fast test for CI/CD pipelines (~1 minute)
pytest be_focus_server_tests/load/test_gradual_live_load.py::TestGradualLiveLoad::test_quick_gradual_load -v -s
```

### Full Test (5 → 100 jobs)

```bash
# Complete gradual load test (~5-8 minutes)
pytest be_focus_server_tests/load/test_gradual_live_load.py::TestGradualLiveLoad::test_full_gradual_load_5_to_100 -v -s
```

### Stability Test (5 → 25 jobs)

```bash
# Focus on stability rather than maximum load
pytest be_focus_server_tests/load/test_gradual_live_load.py::TestGradualLiveLoad::test_gradual_load_stability -v -s
```

### All Gradual Load Tests

```bash
# Run all gradual load tests
pytest be_focus_server_tests/load/test_gradual_live_load.py -v -s -m gradual_load
```

### With Environment Specification

```bash
# Run on staging environment
pytest be_focus_server_tests/load/test_gradual_live_load.py -v -s --env staging

# Run on production environment
pytest be_focus_server_tests/load/test_gradual_live_load.py -v -s --env production
```

## Test Configuration

### Default Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `INITIAL_JOBS` | 5 | Starting number of jobs |
| `STEP_INCREMENT` | 5 | Jobs added each step |
| `MAX_JOBS` | 100 | Maximum concurrent jobs (20 steps) |
| `STEP_INTERVAL_SEC` | 10 | Seconds between steps |

### SLA Thresholds

| Metric | Staging | Production |
|--------|---------|------------|
| Min Success Rate | 70% | 85% |
| Max API Response | 30s | 15s |
| Max Error Rate at Max | 30% | 20% |

## Test Results

### Example Output

```
================================================================================
🚀 GRADUAL LIVE JOB LOAD TEST - Starting
================================================================================
   Test: Full Gradual Load (5→100)
   Pattern: 5 → 100 jobs (+5 every 10s)
================================================================================

📊 STEP 1: Creating 5 jobs to reach 5 total
   Created 5/5 jobs
   🏥 Checking system health...

============================================================
✅ STEP 1: 5 Jobs
============================================================
   📊 Jobs: 5 active (5 ok, 0 failed)
   ⏱️  Avg Creation: 1250ms
   📈 Success Rate: 100.0%
   🏥 Health: PASS
   🔍 API Response: 45ms
============================================================

⏳ Waiting 10s before next step...

... (continues for each step) ...

🎯 MAXIMUM REACHED: 100 jobs

🏥 FINAL HEALTH CHECK at maximum load...
   System Healthy: True
   API Response: 150ms

🧹 CLEANUP: Stopping all jobs...
   Cleaned up 100 jobs

================================================================================
🚀 GRADUAL LIVE JOB LOAD TEST - RESULTS
================================================================================

📊 Overall Status: ✅ PASSED
   • Duration: 105.3 seconds
   • Total Steps: 20
   • Successful Steps: 18

📈 Job Statistics:
   • Max Concurrent Jobs: 100
   • Total Jobs Created: 100
   • Successful: 94
   • Failed: 6

🧹 Cleanup:
   • Status: ✅ Successful
   • Jobs Cleaned: 100

================================================================================
```

### Breaking Point Detection

If the system starts failing at a certain load level, the test will report:

```
⚠️  Breaking Point: 35 jobs
```

This indicates where the system started experiencing issues.

## GitHub Actions Workflow

The test can be run via GitHub Actions:

1. **Manual Trigger**: Go to Actions → "🚀 Gradual Load Test" → Run workflow
2. **Scheduled**: Runs daily at 3:00 AM UTC
3. **Custom Parameters**: Specify custom job counts and intervals

### Workflow Inputs

| Input | Options | Default |
|-------|---------|---------|
| `test_type` | full, quick, stability, custom | quick |
| `environment` | staging, production | staging |
| `initial_jobs` | Any number | 5 |
| `max_jobs` | Any number | 100 |
| `step_interval_sec` | Any number | 10 |

## Test Markers

```python
@pytest.mark.gradual_load  # Gradual load tests
@pytest.mark.load          # Load tests
@pytest.mark.live          # Live job tests
@pytest.mark.slow          # Long-running tests
```

## Files

- `test_gradual_live_load.py` - Main test file
- `GRADUAL_LOAD_TEST.md` - This documentation
- `.github/workflows/gradual-load-test.yml` - GitHub Actions workflow

## Architecture

```
GradualLiveLoadTester
├── Configuration
│   ├── initial_jobs (5)
│   ├── step_increment (5)
│   ├── max_jobs (100)
│   └── step_interval_sec (10)
│
├── Job Management
│   ├── _create_single_job()
│   ├── _create_jobs_batch()
│   └── _cleanup_all_jobs()
│
├── Health Checking
│   └── _check_system_health()
│
├── Step Execution
│   └── _execute_step()
│
└── Test Runner
    └── run_test()
```

## Best Practices

1. **Run Quick Test First**: Always run the quick test before the full test
2. **Monitor Resources**: Watch CPU/memory during load tests
3. **Check Logs**: Review detailed logs for error patterns
4. **Cleanup Verification**: Ensure all jobs are cleaned up after test
5. **Breaking Point Analysis**: Investigate any breaking point detected

## Troubleshooting

### Jobs Not Cleaning Up

If jobs aren't being cleaned up properly:
1. Check Focus Server logs
2. Verify API connectivity
3. Run manual cleanup via API

### Low Success Rate

If success rate is below SLA:
1. Check network connectivity
2. Verify Focus Server health
3. Check for resource exhaustion

### Test Timeout

If test times out:
1. Reduce `MAX_JOBS`
2. Increase `step_interval_sec`
3. Check system resources

