# Xray Test Cases - New Tests to Add to Jira
**Date:** 2025-10-30  
**Total Tests:** 13  
**Category:** Automated Integration & Performance Tests

---

## Test 1: PZ-13986

**Test Summary:**  
Load - 200 Jobs Capacity Stress Test

**Description:**  
Validates that the Focus Server can handle 200 concurrent jobs as per system capacity requirements. This is a critical load test to ensure the infrastructure can support the target workload defined in the capacity planning meeting.

**Pre-conditions:**
- Focus Server is running and accessible
- System has sufficient resources (CPU, Memory, Network)
- Test environment is stable with no other heavy loads

**Test Steps:**
1. Generate 200 lightweight job configurations
2. Submit all 200 jobs concurrently using thread pool
3. Monitor job creation success rate
4. Wait for all jobs to be processed
5. Collect metrics: success rate, response times, resource usage

**Expected Results:**
- At least 90% of jobs (180/200) should be created successfully
- System should remain stable (no crashes or hangs)
- Average job creation time < 3 seconds
- No memory leaks observed
- Infrastructure gap documented if target not met

**Priority:** Critical  
**Type:** Load Test  
**Labels:** load, capacity, stress, infrastructure, concurrent

---

## Test 2: PZ-13984

**Test Summary:**  
Integration - Time Range Validation - Future Timestamps Rejection

**Description:**  
Validates that the Focus Server properly rejects historic playback requests with future timestamps. This prevents invalid configurations and ensures data integrity.

**Pre-conditions:**
- Focus Server API is accessible
- Test has valid authentication credentials

**Test Steps:**
1. Create a configuration with start_time = tomorrow
2. Create a configuration with end_time = next week
3. Submit POST /configure request
4. Capture the response

**Expected Results:**
- Request should be rejected with HTTP 400 Bad Request
- Error message should clearly indicate "future timestamp" or "invalid time range"
- No job should be created (no job_id returned)
- No side effects in the system

**Priority:** High  
**Type:** Integration Test  
**Labels:** validation, time-range, historic, negative-test, api

---

## Test 3: PZ-13922

**Test Summary:**  
Performance - Job Creation Time < 2 Seconds

**Description:**  
Validates that job creation completes within acceptable time limits. Measures the time from POST /configure request to receiving job_id response.

**Pre-conditions:**
- Focus Server is running with normal load
- Network latency is minimal (<50ms)

**Test Steps:**
1. Prepare a valid configuration payload
2. Start timer
3. Send POST /configure request
4. Wait for job_id response
5. Stop timer and record duration
6. Repeat 10 times to get average

**Expected Results:**
- Job creation completes within 2 seconds (per job)
- Average creation time < 1.5 seconds
- All requests return valid job_id
- No timeouts observed

**Priority:** High  
**Type:** Performance Test  
**Labels:** performance, latency, sla, job-creation, api

---

## Test 4: PZ-13921

**Test Summary:**  
Performance - Configuration Endpoint P99 Latency

**Description:**  
Validates that 99% of configuration requests complete within acceptable time threshold (< 1000ms). Measures P99 percentile latency for POST /configure endpoint under normal load.

**Pre-conditions:**
- Focus Server is running
- System is under normal operational load
- Minimum 100 samples required for statistical significance

**Test Steps:**
1. Send 100 POST /configure requests sequentially
2. Measure response time for each request
3. Calculate P99 latency (99th percentile)
4. Calculate also Mean, P95, Max latencies for comparison

**Expected Results:**
- P99 latency < 1000ms (1 second)
- P95 latency < 500ms
- Mean latency < 300ms
- All requests succeed (no errors)

**Priority:** High  
**Type:** Performance Test  
**Labels:** performance, latency, p99, sla, api

---

## Test 5: PZ-13920

**Test Summary:**  
Performance - Configuration Endpoint P95 Latency

**Description:**  
Validates that 95% of configuration requests complete within acceptable time threshold (< 500ms). Measures P95 percentile latency for POST /configure endpoint.

**Pre-conditions:**
- Focus Server is running
- System is under normal operational load
- Minimum 20 samples required for statistical significance

**Test Steps:**
1. Send 20 POST /configure requests sequentially
2. Measure response time for each request
3. Calculate P95 latency (95th percentile)
4. Calculate also Mean, Median, Max latencies

**Expected Results:**
- P95 latency < 500ms
- Mean latency < 300ms
- Median latency < 200ms
- All requests succeed

**Priority:** High  
**Type:** Performance Test  
**Labels:** performance, latency, p95, sla, api

---

## Test 6: PZ-13914

**Test Summary:**  
Integration - Invalid View Type - Out of Range

**Description:**  
Validates that the system properly rejects configuration requests with invalid view_type values that are out of the acceptable range. Valid range: 0 (MULTICHANNEL), 1 (SINGLECHANNEL), 2 (WATERFALL).

**Pre-conditions:**
- Focus Server API is accessible

**Test Steps:**
1. Create configuration with view_type = 999 (invalid)
2. Send POST /configure request
3. Capture the response
4. Verify rejection

**Expected Results:**
- Request rejected with HTTP 400 Bad Request or validation error
- Error message indicates invalid view_type value
- No job created
- Error mentions valid range: 0-2

**Priority:** High  
**Type:** Integration Test  
**Labels:** validation, view-type, negative-test, api

---

## Test 7: PZ-13913

**Test Summary:**  
Integration - Invalid View Type - String Value

**Description:**  
Validates that the system properly rejects configuration requests with view_type provided as a string instead of integer. Tests Pydantic type validation.

**Pre-conditions:**
- Focus Server API is accessible

**Test Steps:**
1. Create configuration with view_type = "multichannel" (string)
2. Attempt to create ConfigureRequest object
3. Capture validation error

**Expected Results:**
- Pydantic validation should reject the string type
- Error message indicates type mismatch (expected int, got str)
- Request never reaches the server (caught at client validation)

**Priority:** High  
**Type:** Integration Test  
**Labels:** validation, view-type, type-validation, negative-test, pydantic

---

## Test 8: PZ-13912

**Test Summary:**  
Integration - Configuration Missing displayTimeAxisDuration Field

**Description:**  
Validates that the system properly handles configuration requests missing the displayTimeAxisDuration field. Tests required field validation.

**Pre-conditions:**
- Focus Server API is accessible

**Test Steps:**
1. Create configuration payload without displayTimeAxisDuration
2. Include all other required fields (channels, frequencyRange, nfftSelection, etc.)
3. Send POST /configure request or create ConfigureRequest object
4. Capture response or validation error

**Expected Results:**
- Request rejected with validation error or HTTP 400
- Error message indicates missing displayTimeAxisDuration
- No job created
- Clear indication of required field

**Priority:** High  
**Type:** Integration Test  
**Labels:** validation, missing-field, negative-test, api

---

## Test 9: PZ-13911

**Test Summary:**  
Integration - Configuration Missing nfftSelection Field

**Description:**  
Validates that the system properly handles configuration requests missing the nfftSelection field. Tests required field validation for FFT window size.

**Pre-conditions:**
- Focus Server API is accessible

**Test Steps:**
1. Create configuration payload without nfftSelection
2. Include all other required fields
3. Send POST /configure request
4. Capture response or validation error

**Expected Results:**
- Request rejected with validation error or HTTP 400/500
- Error message indicates missing nfftSelection
- No job created
- System remains stable

**Priority:** High  
**Type:** Integration Test  
**Labels:** validation, missing-field, negative-test, nfft, api

---

## Test 10: PZ-13910

**Test Summary:**  
Integration - Configuration Missing frequencyRange Field

**Description:**  
Validates that the system properly handles configuration requests missing the frequencyRange field. Tests required field validation for frequency parameters.

**Pre-conditions:**
- Focus Server API is accessible

**Test Steps:**
1. Create configuration payload without frequencyRange
2. Include all other required fields
3. Send POST /configure request
4. Capture response or validation error

**Expected Results:**
- Request rejected with validation error or HTTP 400/500
- Error message indicates missing frequencyRange
- No job created
- System remains stable

**Priority:** High  
**Type:** Integration Test  
**Labels:** validation, missing-field, negative-test, frequency, api

---

## Test 11: PZ-13908

**Test Summary:**  
Integration - Configuration Missing channels Field

**Description:**  
Validates that the system properly handles configuration requests missing the channels field. Tests required field validation for channel selection.

**Pre-conditions:**
- Focus Server API is accessible

**Test Steps:**
1. Create configuration payload without channels
2. Include all other required fields
3. Attempt to create ConfigureRequest or send POST /configure
4. Capture validation error

**Expected Results:**
- Pydantic or server validation rejects the request
- Error message indicates missing channels field
- No job created
- Clear error message for troubleshooting

**Priority:** High  
**Type:** Integration Test  
**Labels:** validation, missing-field, negative-test, channels, api

---

## Test 12: PZ-13902

**Test Summary:**  
Integration - Frequency Range Within Nyquist Limit

**Description:**  
Validates that the system correctly accepts frequency range configurations that are within the Nyquist limit (PRR/2). This is a positive test ensuring valid configurations are accepted.

**Pre-conditions:**
- Focus Server API is accessible
- Live metadata is available with valid PRR value
- System is in Live mode

**Test Steps:**
1. Retrieve live metadata to get PRR value
2. Calculate Nyquist frequency = PRR / 2
3. Create configuration with frequencyRange.max = 80% of Nyquist
4. Send POST /configure request
5. Verify job creation succeeds

**Expected Results:**
- Configuration accepted (HTTP 200)
- Valid job_id returned
- Frequency validation passes
- Job processes successfully

**Priority:** High  
**Type:** Integration Test  
**Labels:** validation, frequency, nyquist, positive-test, api

---

## Test 13: PZ-13864

**Test Summary:**  
Integration - Historic Playback - Short Duration (Rapid Window)

**Description:**  
Validates that the system can handle historic playback requests with very short time windows (1 minute). Tests edge case for minimal duration historic jobs.

**Pre-conditions:**
- Focus Server API is accessible
- Historic data exists in the requested time range
- MongoDB is accessible and has recordings

**Test Steps:**
1. Calculate 1-minute time range (2 hours ago to ensure data exists)
2. Create historic configuration with start_time and end_time
3. Send POST /configure request
4. Poll job status until completion
5. Verify quick completion

**Expected Results:**
- Configuration accepted (HTTP 200)
- Valid job_id returned
- Job completes within 30 seconds
- Status reaches 208 (completion)
- No errors or timeouts

**Priority:** Medium  
**Type:** Integration Test  
**Labels:** historic, playback, edge-case, short-duration, api

---

## Summary

**Test Distribution:**
- Performance Tests: 3 (PZ-13920, PZ-13921, PZ-13922)
- Validation Tests (Negative): 7 (PZ-13908, 13910, 13911, 13912, 13913, 13914, 13984)
- Validation Tests (Positive): 1 (PZ-13902)
- Load Tests: 1 (PZ-13986)
- Historic Playback: 1 (PZ-13864)

**Priority Breakdown:**
- Critical: 1
- High: 11
- Medium: 1

**Implementation Status:**
- All tests are already implemented in automated test suite
- Tests have `@pytest.mark.xray()` markers
- Tests are production-ready and passing

---

## Notes for Jira Upload

1. Each test should be created as type "Test" in Jira
2. Link to automation: All tests are in `tests/` directory
3. Test execution: Can be run via pytest with marker filters
4. CI/CD: Tests are integrated in automation pipeline
5. Coverage: These tests close gaps identified in coverage analysis

**Automation Files:**
- PZ-13986: `tests/load/test_job_capacity_limits.py`
- PZ-13984: `tests/integration/api/test_prelaunch_validations.py`
- PZ-13920-13922: `tests/integration/performance/test_latency_requirements.py`
- PZ-13913-13914: `tests/integration/api/test_view_type_validation.py`
- PZ-13908-13912: `tests/integration/api/test_config_validation_high_priority.py`
- PZ-13902: `tests/integration/api/test_config_validation_nfft_frequency.py`
- PZ-13864: `tests/integration/api/test_historic_playback_additional.py`

