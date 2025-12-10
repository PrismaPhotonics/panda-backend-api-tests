# Focus Server Automation - Sprint 5 & 6 Plan
## Cleaned & Relevant Implementation Roadmap

**Author:** QA Automation Team  
**Date:** 2025-12-09  
**Context:** Solo QA Engineer, 2-week sprints  

---

## ⚠️ CLARIFICATIONS FROM ORIGINAL PLAN

### What Was REMOVED (Not Relevant to Focus Server):

| Item | Why Removed |
|------|-------------|
| SQL Injection Tests | Focus Server uses **MongoDB**, not SQL. Already covered in `test_input_validation.py` |
| XSS Tests | Focus Server is a **backend GRPC/REST API** - no HTML rendering, no browser context |
| "NFFT = Non-Functional Tests" | **WRONG!** NFFT = Number of FFT (Fast Fourier Transform) points - signal processing param (128, 256, 512, 1024, etc.) |
| Selenium/Playwright | Not needed - no web UI to test |
| /login, /search endpoints | Don't exist in Focus Server |
| JMeter for web load testing | Use existing pytest load framework |

### What's ALREADY IMPLEMENTED:

| Feature | Location | Status |
|---------|----------|--------|
| MongoDB Outage Resilience | `performance/test_mongodb_outage_resilience.py` | ✅ Complete |
| MongoDB Pod Resilience | `infrastructure/resilience/test_mongodb_pod_resilience.py` | ✅ Complete |
| Input Validation Security | `integration/security/test_input_validation.py` | ✅ Complete |
| Malformed Input Handling | `security/test_malformed_input_handling.py` | ✅ Complete |
| RabbitMQ Outage Handling | `infrastructure/test_rabbitmq_outage_handling.py` | ✅ Complete |
| Performance Tests | `integration/performance/` (8 files) | ✅ Complete |
| Load Tests | `load/` + `integration/load/` | ✅ Complete |
| **Parallel Investigations (Single Thread)** | `integration/load/test_parallel_investigations_single_thread.py` | ✅ Complete |

---

## 📋 Sprint 5 (2 weeks) - Test Quality & Coverage Gaps

### Epic: Fix Misleading Tests & Enhance Coverage

**Objective:** Improve test reliability by identifying and fixing flaky tests, removing false-positive mocks, and enhancing coverage for critical paths.

---

### Story 5.1: Identify & Fix Flaky Tests

**Jira ID:** (Create as needed)  
**Priority:** HIGH

**Description:**  
Identify tests that pass/fail inconsistently and fix root causes (timing issues, state leaks, environment dependencies).

**Target Files to Audit:**
```
be_focus_server_tests/integration/api/test_live_streaming_stability.py
be_focus_server_tests/integration/load/test_concurrent_load.py
be_focus_server_tests/integration/performance/test_network_latency.py
```

**Tasks:**
1. Run full test suite 5 times, log any tests that fail intermittently
2. For each flaky test:
   - Add proper wait conditions / retry logic
   - Fix state isolation (ensure test cleanup)
   - Add explicit timeouts where missing
3. Add `@pytest.mark.flaky(reruns=3)` temporarily for known flaky tests while fixing

**Acceptance Criteria:**
- [ ] Full suite runs 5 times consecutively with 0 failures
- [ ] No tests using `time.sleep()` without justification
- [ ] All async operations have proper await/timeout handling

---

### Story 5.2: Remove Over-Mocking in Unit Tests

**Jira ID:** (Create as needed)  
**Priority:** MEDIUM

**Description:**  
Audit unit tests that mock too heavily, potentially hiding real bugs. Replace with integration tests where appropriate.

**Target Files:**
```
be_focus_server_tests/unit/test_models_validation.py
be_focus_server_tests/unit/test_validators.py
```

**Tasks:**
1. Review mocks that always return success - add failure path mocking
2. For tests that mock the database:
   - Consider using real MongoDB test instance
   - Or ensure mock properly simulates failure scenarios
3. Add integration test coverage for scenarios that were only unit tested

**Example - Bad Mock (to fix):**
```python
# BAD: Always returns success
@patch('src.apis.focus_server_api.requests.post')
def test_configure_job(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"job_id": "123"}
    # This test can never fail!
```

```python
# GOOD: Test both success and failure paths
def test_configure_job_success(focus_server_api):
    """Integration test with real API"""
    response = focus_server_api.configure_streaming_job(valid_config)
    assert response.job_id is not None

def test_configure_job_invalid_config(focus_server_api):
    """Test failure path"""
    with pytest.raises(ValidationError):
        focus_server_api.configure_streaming_job(invalid_config)
```

**Acceptance Criteria:**
- [ ] No unit tests that can only pass (always-success mocks removed)
- [ ] Each critical path has both success AND failure test coverage
- [ ] Integration tests cover scenarios previously only unit tested

---

### Story 5.3: NFFT Configuration Validation Enhancement

**Jira ID:** (Create as needed)  
**Priority:** HIGH

**Description:**  
Enhance NFFT (Fast Fourier Transform) configuration tests to cover all valid values and edge cases.

**Context:**  
NFFT Options: `128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536`  
Default NFFT: `1024`

**Target Files:**
```
be_focus_server_tests/integration/api/test_config_validation_nfft_frequency.py
be_focus_server_tests/integration/api/test_nfft_overlap_edge_case.py
```

**Tasks:**
1. Add parametrized tests for ALL valid NFFT values
2. Test invalid NFFT values (e.g., 100, 500, 99999)
3. Test NFFT with different channel counts
4. Test NFFT with different frequency ranges
5. Verify NFFT validation messages are clear

**Test Cases to Add:**
```python
@pytest.mark.parametrize("nfft", [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536])
def test_valid_nfft_values(focus_server_api, nfft):
    """Test all valid NFFT values are accepted"""
    config = ConfigureRequest(
        nfftSelection=nfft,
        channels={"min": 11, "max": 109},
        frequencyRange={"min": 0, "max": 1000},
        # ... other fields
    )
    response = focus_server_api.configure_streaming_job(config)
    assert response.job_id is not None

@pytest.mark.parametrize("invalid_nfft", [100, 500, 1000, 99999, -1, 0])
def test_invalid_nfft_values_rejected(focus_server_api, invalid_nfft):
    """Test invalid NFFT values are rejected with clear error"""
    config = ConfigureRequest(nfftSelection=invalid_nfft, ...)
    with pytest.raises(ValidationError) as exc:
        focus_server_api.configure_streaming_job(config)
    assert "nfft" in str(exc.value).lower()
```

**Acceptance Criteria:**
- [ ] All 10 valid NFFT values tested
- [ ] Invalid NFFT values properly rejected
- [ ] NFFT combined with channel/frequency edge cases tested
- [ ] Tests linked to Xray

---

## 📋 Sprint 6 (2 weeks) - Infrastructure & Performance

### Epic: Enhance CI Resilience & Performance Monitoring

**Objective:** Improve CI pipeline reliability, add infrastructure chaos testing, and establish performance baselines.

---

### Story 6.1: Extend MongoDB Resilience Testing (Network Partition)

**Jira ID:** (Create as needed)  
**Priority:** HIGH

**Description:**  
Extend existing MongoDB resilience tests with network partition simulation (in addition to existing scale-down tests).

**NOTE:** Basic MongoDB outage tests already exist. This story adds:
- Network partition simulation (iptables)
- Partial outage scenarios
- Concurrent operations during outage

**Existing Tests (Reference):**
```
be_focus_server_tests/performance/test_mongodb_outage_resilience.py
be_focus_server_tests/infrastructure/resilience/test_mongodb_pod_resilience.py
```

**New Tests to Add:**
```python
# In: be_focus_server_tests/infrastructure/resilience/test_mongodb_network_partition.py

@pytest.mark.nightly
@pytest.mark.infrastructure
class TestMongoDBNetworkPartition:
    
    def test_mongodb_slow_network(self):
        """Simulate slow MongoDB responses (100ms+ latency)"""
        # Use tc (traffic control) to add latency
        pass
    
    def test_mongodb_packet_loss(self):
        """Simulate 10% packet loss to MongoDB"""
        pass
    
    def test_concurrent_requests_during_recovery(self):
        """Multiple concurrent requests while MongoDB is recovering"""
        pass
```

**Acceptance Criteria:**
- [ ] Network partition test implemented and working
- [ ] Tests run in nightly pipeline (not on every commit)
- [ ] Recovery time measured and logged
- [ ] No orphaned K8s jobs after recovery

---

### Story 6.2: CI Pipeline Stability (Iterative Test Runs)

**Jira ID:** (Create as needed)  
**Priority:** MEDIUM

**Description:**  
Add CI job that runs the test suite multiple times to catch intermittent failures before they reach main branch.

**Implementation:**
```yaml
# In: .github/workflows/test-stability.yml
name: Test Stability Check
on:
  schedule:
    - cron: '0 2 * * *'  # Nightly at 2 AM
  workflow_dispatch:

jobs:
  stability-check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        iteration: [1, 2, 3, 4, 5]
    steps:
      - uses: actions/checkout@v4
      - name: Run tests iteration ${{ matrix.iteration }}
        run: |
          pytest be_focus_server_tests/ \
            --env kefar_saba \
            -v \
            --tb=short \
            --junit-xml=results-${{ matrix.iteration }}.xml
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.iteration }}
          path: results-${{ matrix.iteration }}.xml
```

**Acceptance Criteria:**
- [ ] Nightly stability job runs 5 iterations
- [ ] Results aggregated and compared
- [ ] Flaky test report generated
- [ ] Alert if any iteration fails

---

### Story 6.3: Performance Baseline & Trend Tracking

**Jira ID:** (Create as needed)  
**Priority:** MEDIUM

**Description:**  
Establish performance baselines for critical operations and track trends over time.

**Target Metrics:**
| Operation | Baseline Target | SLA |
|-----------|-----------------|-----|
| POST /configure (Live) | < 500ms | < 1s |
| POST /configure (Historic) | < 2s | < 5s |
| MongoDB query latency | < 50ms | < 100ms |
| gRPC stream setup | < 1s | < 3s |
| Job cancellation | < 500ms | < 1s |

**Implementation:**

1. **Create baseline collection script:**
```python
# scripts/collect_performance_baseline.py
import json
import time
from datetime import datetime
from statistics import mean, stdev

def collect_baseline(api, iterations=100):
    results = {
        "timestamp": datetime.now().isoformat(),
        "configure_live": [],
        "configure_historic": [],
        "cancel_job": [],
    }
    
    for i in range(iterations):
        # Measure configure (live)
        start = time.time()
        response = api.configure_streaming_job(live_config)
        results["configure_live"].append(time.time() - start)
        
        # Measure cancel
        start = time.time()
        api.cancel_job(response.job_id)
        results["cancel_job"].append(time.time() - start)
    
    # Calculate stats
    return {
        "configure_live": {
            "mean": mean(results["configure_live"]),
            "p95": sorted(results["configure_live"])[int(0.95 * iterations)],
            "stdev": stdev(results["configure_live"]),
        },
        # ...
    }
```

2. **Add performance regression test:**
```python
# be_focus_server_tests/performance/test_performance_regression.py

@pytest.mark.performance
class TestPerformanceRegression:
    
    BASELINE = {
        "configure_live_p95": 0.5,  # 500ms
        "configure_historic_p95": 2.0,  # 2s
    }
    TOLERANCE = 0.2  # 20% tolerance
    
    def test_configure_live_performance(self, focus_server_api):
        """Verify live configure latency within baseline"""
        times = []
        for _ in range(50):
            start = time.time()
            response = focus_server_api.configure_streaming_job(live_config)
            times.append(time.time() - start)
            focus_server_api.cancel_job(response.job_id)
        
        p95 = sorted(times)[int(0.95 * len(times))]
        max_allowed = self.BASELINE["configure_live_p95"] * (1 + self.TOLERANCE)
        
        assert p95 <= max_allowed, \
            f"P95 latency {p95:.3f}s exceeds baseline {max_allowed:.3f}s"
```

3. **Add trend storage:**
```python
# Store results in JSON file or database
# results/performance_history.json
{
    "2025-12-09": {"configure_live_p95": 0.45, ...},
    "2025-12-10": {"configure_live_p95": 0.48, ...},
}
```

**Acceptance Criteria:**
- [ ] Baseline established for all critical operations
- [ ] Performance test runs in CI (weekly or nightly)
- [ ] Trend data stored and accessible
- [ ] Alert if performance degrades > 20% from baseline
- [ ] Simple trend visualization (even CSV/chart is fine)

---

### Story 6.4: Parallel Investigations Load Testing ✅ IMPLEMENTED

**Jira ID:** (Create as needed)  
**Priority:** HIGH  
**Status:** ✅ COMPLETE (2025-12-09)

**Description:**  
Test suite for parallel investigation creation using single-thread asyncio to verify concurrent job handling, timing verification, and component stability under load.

**Location:**
```
be_focus_server_tests/integration/load/test_parallel_investigations_single_thread.py
```

**Test Cases Implemented:**

| Test | Description | Status |
|------|-------------|--------|
| `test_parallel_creation_with_full_verification` | 5 parallel jobs with component health checks (pre/post) | ✅ PASSED |
| `test_parallel_creation_timestamp_verification` | 10 parallel jobs with detailed timing analysis | ✅ PASSED |
| `test_mixed_job_types_parallel` | 3 Live + 3 Historic jobs in parallel | ✅ PASSED |
| `test_component_stability_under_parallel_load` | 15 parallel jobs with pre/mid/post health checks | ✅ PASSED |

**Key Features:**
- **Single-thread concurrency:** Uses `asyncio` + `aiohttp` for true parallel execution without OS threads
- **Parallel verification:** Confirms all requests sent within <100ms window
- **Job metadata inspection:** Verifies job type (Live/Historic), configuration, creation timestamps
- **Component health checks:** Focus Server health validation before/during/after load
- **Automatic cleanup:** All created jobs are cancelled after tests

**Test Results (Staging - 2025-12-09):**
```
================================================================================
PARALLEL EXECUTION VERIFICATION
================================================================================
  Request Start Spread: 5.2ms  (threshold: 100ms)
  ✅ PARALLEL EXECUTION CONFIRMED!
  All 10 requests started within 5.2ms of each other

PERFORMANCE:
  Theoretical Sequential Time: 8530.2ms
  Actual Parallel Time: 1645.3ms
  Speedup: 5.18x 🚀

COMPONENT STABILITY:
  Pre-Load:  ✅ HEALTHY
  Mid-Load:  ✅ HEALTHY
  Post-Load: ✅ HEALTHY
================================================================================
4 passed in 97.75s (0:01:37)
```

**Run Command:**
```bash
pytest be_focus_server_tests/integration/load/test_parallel_investigations_single_thread.py::TestParallelCreationVerification -v --env staging
```

**Markers:**
```python
@pytest.mark.asyncio
@pytest.mark.load
@pytest.mark.parallel
@pytest.mark.integration
```

**Acceptance Criteria:**
- [x] Parallel job creation verified (requests within <100ms spread)
- [x] Job configuration/metadata inspection implemented
- [x] Live and Historic job types tested
- [x] Component stability checks (Focus Server health)
- [x] Automatic cleanup of all created jobs
- [x] Tests passing on staging environment
- [ ] Tests linked to Xray (PZ-TBD)

**Known Findings:**
1. **Historic jobs take longer:** 15-30 seconds vs 200-700ms for Live jobs
2. **Cleanup 404 is normal:** Focus Server auto-cleans jobs before test cleanup runs

---

### Story 6.5: Extended Load Testing (Future)

**Jira ID:** (Create as needed)  
**Priority:** MEDIUM  
**Status:** 🔲 TODO

**Description:**  
Extend parallel investigation tests with additional load scenarios.

**Proposed Test Cases:**
```python
# Future additions to test_parallel_investigations_single_thread.py

@pytest.mark.load
@pytest.mark.slow
class TestExtendedParallelLoad:
    
    async def test_30_parallel_investigations(self):
        """Test system behavior at MaxWindows limit (30)"""
        pass
    
    async def test_gradual_load_increase(self):
        """Gradually increase from 5 to 30 parallel jobs"""
        pass
    
    async def test_sustained_parallel_load(self):
        """Create/destroy jobs continuously for 5 minutes"""
        pass
    
    async def test_parallel_with_network_latency(self):
        """Parallel job creation with simulated network delays"""
        pass
```

**Target Metrics:**
| Scenario | Expected | SLA |
|----------|----------|-----|
| 5 parallel Live jobs | < 1s total | < 2s |
| 10 parallel Live jobs | < 2s total | < 5s |
| 15 parallel Live jobs | < 7s total | < 10s |
| 30 parallel Live jobs | < 15s total | < 30s |
| Mixed Live+Historic (6 jobs) | < 35s total | < 60s |

---

## 📊 Sprint Summary Checklist

### Sprint 5 Exit Criteria:
- [ ] Zero flaky tests in 5 consecutive full runs
- [ ] Over-mocked unit tests refactored
- [ ] NFFT validation tests complete (all 10 values)
- [ ] CI pipeline green
- [ ] All stories linked to Xray

### Sprint 6 Exit Criteria:
- [ ] Network partition test implemented
- [ ] Stability check job running nightly
- [ ] Performance baseline established
- [ ] Trend tracking in place
- [x] **Parallel investigations load tests implemented** ✅
- [ ] All stories completed with green CI

---

## 🔗 Related Documentation

- Test Suite README: `be_focus_server_tests/README.md`
- Performance Tests: `be_focus_server_tests/integration/performance/`
- Infrastructure Resilience: `be_focus_server_tests/infrastructure/resilience/`
- **Parallel Load Tests:** `be_focus_server_tests/integration/load/test_parallel_investigations_single_thread.py`
- Xray Integration: `be_focus_server_tests/conftest_xray.py`

---

## 📝 Notes

1. **Environment:** All tests must run on `kefar_saba` environment (`--env kefar_saba`)
2. **NFFT Values:** 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536
3. **Max Channels:** 2222 (not 2500!)
4. **Max Frequency:** 1000 Hz (not 15000!)

---

*Last Updated: 2025-12-09*

