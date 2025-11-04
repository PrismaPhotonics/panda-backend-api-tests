# 📋 All Missing Test Cases for Xray in Jira

**Generated:** 2025-10-19  
**Total Missing Tests:** 30 Test Cases  
**Purpose:** Complete documentation for creating all missing tests in Jira Xray

---

# 🔴 SECTION A: Critical API Endpoint Tests (Missing)

## **Test Case: TC-API-001**
**Summary:** API – POST /configure – Live Mode (Happy Path)

**Objective:** Validate that a valid live configuration creates a job and returns usable gRPC coordinates with correct stream/channel mapping.

**Priority:** Critical

**Components/Labels:** focus-server, api, live, grpc, configure, mapping

**Requirements:** FOCUS-API-CONFIGURE

**Pre-Conditions:**
- PC-001: API base URL reachable (https://10.10.100.100/focus-server/)
- PC-002: System PRR configured (default 2000)
- PC-003: FocusManager.channels known
- PC-004: No authentication OR valid bearer token ready

**Test Data:**
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": { "height": 1000 },
  "channels": { "min": 1, "max": 3 },
  "frequencyRange": { "min": 0, "max": 500 },
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Send POST request to /configure | Live payload above | HTTP 200 OK |
| 2 | Validate response contains job_id | response.job_id | Not null, format: "gpu-X-Y" |
| 3 | Validate stream_amount field | response.stream_amount | 1 ≤ value ≤ 3 |
| 4 | Validate channel mapping | response.channel_to_stream_index | Size matches channel_amount |
| 5 | Validate stream URL format | response.stream_url | Starts with http:// or https:// |
| 6 | Validate stream port | response.stream_port | Port > 0 and < 65535 |
| 7 | Validate frequencies list | response.frequencies_list | Length > 0, all values numeric |
| 8 | Validate view_type | response.view_type | Equals 0 (matches request) |

**Expected Result (overall):**
- Job successfully created
- All response fields populated correctly
- Stream endpoint ready for gRPC connection
- No errors in server logs

**Post-Conditions:**
- Job remains active until cleanup
- Resources allocated in K8s/local
- Stream endpoint accessible

**Assertions:**
```python
assert response.status_code == 200
assert response.json()['job_id'] is not None
assert 1 <= response.json()['stream_amount'] <= 3
assert response.json()['stream_port'] > 0
assert len(response.json()['channel_to_stream_index']) == response.json()['channel_amount']
assert response.json()['view_type'] == 0
```

**Environment:** Dev/Staging/Production

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_configure_live_happy_path`
**Test File:** `tests/integration/api/test_configure_endpoints.py`

---

## **Test Case: TC-API-002**
**Summary:** API – POST /configure – Historical Mode (Happy Path)

**Objective:** Validate historical configuration succeeds when requested time range overlaps existing recordings in MongoDB.

**Priority:** Critical

**Components/Labels:** focus-server, api, history, grpc, storage, mongo

**Requirements:** FOCUS-API-CONFIGURE, FOCUS-API-REC-RANGE

**Pre-Conditions:**
- PC-010: MongoDB reachable and accessible
- PC-011: Recordings exist in requested time window
- PC-012: Storage (S3/local) accessible
- PC-013: rec_mapper collection populated

**Test Data:**
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": { "height": 1000 },
  "channels": { "min": 1, "max": 3 },
  "frequencyRange": { "min": 0, "max": 500 },
  "start_time": 1700000000,
  "end_time": 1700000600,
  "view_type": 0
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Query MongoDB for recordings | Time range 1700000000-1700000600 | Recordings found |
| 2 | Send POST to /configure | Historical payload | HTTP 200 OK |
| 3 | Validate job_id returned | response.job_id | Not null |
| 4 | GET /metadata/{job_id} | job_id from step 3 | 200 with matching config |
| 5 | POST /recordings_in_time_range | Same time window | List of [start_ts, end_ts] tuples |
| 6 | Cross-check recordings | Returned vs requested | All overlap requested window |
| 7 | Validate source field | Internal logs/metadata | source = "storage" |
| 8 | Check no gaps in coverage | Recording windows | Continuous coverage |

**Expected Result (overall):**
- Historical job configured successfully
- Metadata matches original request
- Recordings cover requested time range
- No gaps in data coverage

**Post-Conditions:**
- Job ready for historical playback
- No modifications to MongoDB
- Storage reads initiated

**Assertions:**
```python
assert response.status_code == 200
assert recordings_response.json() != []
assert all(rec[0] <= 1700000600 and rec[1] >= 1700000000 for rec in recordings)
assert metadata_response.json()['start_time'] == 1700000000
assert metadata_response.json()['end_time'] == 1700000600
```

**Environment:** Staging/Production (requires real data)

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_configure_historical_happy_path`
**Test File:** `tests/integration/api/test_configure_endpoints.py`

---

## **Test Case: TC-API-003**
**Summary:** API – POST /configure – Invalid Time Range Validation

**Objective:** Ensure invalid time ranges (start >= end) are rejected with proper 400 error.

**Priority:** High

**Components/Labels:** focus-server, api, validation, history, negative-test

**Requirements:** FOCUS-API-VALIDATION

**Pre-Conditions:**
- API reachable
- Server validation enabled

**Test Data:**
```json
Test Case A: {
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": { "height": 1000 },
  "channels": { "min": 1, "max": 3 },
  "frequencyRange": { "min": 0, "max": 500 },
  "start_time": 1700000600,
  "end_time": 1700000000,  // start > end
  "view_type": 0
}

Test Case B: {
  "start_time": 1700000000,
  "end_time": 1700000000,  // start == end
  "view_type": 0
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | Payload A (start > end) | HTTP 400 Bad Request |
| 2 | Validate error message | Response body | Contains "Invalid time range" |
| 3 | Check no job created | Server state | No job_id generated |
| 4 | POST /configure | Payload B (start == end) | HTTP 400 Bad Request |
| 5 | Validate error structure | Response body | JSON with error details |
| 6 | GET /metadata/{random_id} | Non-existent ID | 404 (no false positives) |
| 7 | Check server logs | Log entries | Validation error logged, no crash |

**Expected Result (overall):**
- Clear 400 errors for invalid time ranges
- Descriptive error messages
- No resource allocation
- No server errors

**Post-Conditions:**
- No side effects
- Server remains stable

**Assertions:**
```python
assert response.status_code == 400
assert "Invalid time range" in response.json()['error']
assert 'job_id' not in response.json()
assert server_logs.contains("Validation failed")
assert not kubernetes.job_exists()
```

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_configure_invalid_time_range`
**Test File:** `tests/integration/api/test_configure_validation.py`

---

## **Test Case: TC-API-004**
**Summary:** API – POST /configure – Invalid Channel Range

**Objective:** Confirm server blocks illegal channel windows (min > max, negative, out of bounds).

**Priority:** High

**Components/Labels:** focus-server, api, validation, negative-test

**Requirements:** FOCUS-API-VALIDATION

**Pre-Conditions:**
- API reachable
- System max channels known (e.g., 1000)

**Test Data:**
```json
Test Case A: {
  "channels": { "min": 300, "max": 100 },  // min > max
  ...
}

Test Case B: {
  "channels": { "min": -5, "max": 10 },  // negative
  ...
}

Test Case C: {
  "channels": { "min": 1, "max": 9999 },  // out of bounds
  ...
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | min > max channels | HTTP 400 |
| 2 | Check error message | Response | "Invalid channel range" |
| 3 | POST /configure | Negative channel | HTTP 400 |
| 4 | Check error details | Response | Specifies negative value issue |
| 5 | POST /configure | Out of bounds | HTTP 400 |
| 6 | Verify no partial creation | K8s/RabbitMQ | No resources created |
| 7 | Test boundary values | min=1, max=max_channels | Should succeed (200) |

**Expected Result (overall):**
- All invalid ranges rejected with 400
- Clear, specific error messages
- No partial job creation
- Boundary values handled correctly

**Post-Conditions:**
None

**Assertions:**
```python
assert all(r.status_code == 400 for r in invalid_responses)
assert "channel" in error_message.lower()
assert boundary_test.status_code == 200
```

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_configure_invalid_channels`
**Test File:** `tests/integration/api/test_configure_validation.py`

---

## **Test Case: TC-API-005**
**Summary:** API – POST /configure – Invalid Frequency Range

**Objective:** Validate rejection of malformed frequency ranges (negative, min > max, invalid units).

**Priority:** High

**Components/Labels:** focus-server, api, validation, negative-test

**Requirements:** FOCUS-API-VALIDATION

**Pre-Conditions:**
- API reachable
- System frequency limits known

**Test Data:**
```json
Test Case A: {
  "frequencyRange": { "min": 500, "max": 0 },  // min > max
  ...
}

Test Case B: {
  "frequencyRange": { "min": -100, "max": 500 },  // negative
  ...
}

Test Case C: {
  "frequencyRange": { "min": 0, "max": 1000000 },  // exceeds system max
  ...
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | min > max frequency | HTTP 400 |
| 2 | Validate error | Response | "Invalid frequency range" |
| 3 | POST /configure | Negative frequency | HTTP 400 |
| 4 | POST /configure | Exceeds max | HTTP 400 |
| 5 | Check no orchestration | Server state | No job started |
| 6 | Test valid range | min=0, max=1000 | HTTP 200 |

**Expected Result (overall):**
- Invalid ranges rejected
- No server errors
- Valid ranges accepted

**Post-Conditions:**
None

**Assertions:**
```python
assert invalid_response.status_code == 400
assert "frequency" in error_message.lower()
assert valid_response.status_code == 200
```

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_configure_invalid_frequency_range`
**Test File:** `tests/integration/api/test_configure_validation.py`

---

## **Test Case: TC-API-006**
**Summary:** API – GET /channels – Returns System Channel Bounds

**Objective:** Validate channel range endpoint returns authoritative system bounds.

**Priority:** High

**Components/Labels:** focus-server, api, channels, info

**Requirements:** FOCUS-API-CHANNELS

**Pre-Conditions:**
- FocusManager.channels configured
- API reachable

**Test Data:**
N/A (GET request, no payload)

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Send GET /channels | None | HTTP 200 OK |
| 2 | Validate response schema | JSON response | Contains lowest_channel, highest_channel |
| 3 | Check lowest_channel | response.lowest_channel | Value == 1 |
| 4 | Check highest_channel | response.highest_channel | Value > 0, matches config |
| 5 | Call endpoint 5 times | None | Consistent results |
| 6 | Validate data types | Response fields | All integers |
| 7 | Check response time | Latency | < 100ms |

**Expected Result (overall):**
- Returns configured channel bounds
- Consistent across calls
- Fast response time

**Post-Conditions:**
None

**Assertions:**
```python
assert response.status_code == 200
assert response.json()['lowest_channel'] == 1
assert response.json()['highest_channel'] > 0
assert all(r.json() == response.json() for r in repeated_calls)
```

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_channels_endpoint`
**Test File:** `tests/integration/api/test_info_endpoints.py`

---

## **Test Case: TC-API-007**
**Summary:** API – GET /metadata/{job_id} – Valid and Invalid Cases

**Objective:** Validate metadata retrieval for existing jobs and proper 404 for non-existent.

**Priority:** High

**Components/Labels:** focus-server, api, metadata, jobs

**Requirements:** FOCUS-API-JOB-META

**Pre-Conditions:**
- At least one job created via /configure
- Valid job_id available

**Test Data:**
- Valid job_id: From previous /configure call
- Invalid job_ids: "non_existent", "12345", "", "../../etc/passwd"

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Create job via POST /configure | Valid payload | Get job_id |
| 2 | GET /metadata/{job_id} | Valid job_id | HTTP 200 |
| 3 | Validate config match | Response vs original | Exact match |
| 4 | Check all fields present | Response | All config fields included |
| 5 | GET /metadata/non_existent | Invalid ID | HTTP 404 |
| 6 | Validate error message | 404 response | "Job not found" |
| 7 | Test path traversal | "../../etc/passwd" | HTTP 400 or 404 |
| 8 | Test empty job_id | "" | HTTP 400 |

**Expected Result (overall):**
- Valid jobs return complete metadata
- Invalid jobs return 404
- No information leakage
- Path traversal blocked

**Post-Conditions:**
- Created job cleaned up

**Assertions:**
```python
assert valid_response.status_code == 200
assert valid_response.json() == original_config
assert invalid_response.status_code == 404
assert "not found" in invalid_response.json()['error'].lower()
```

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_metadata_endpoint`
**Test File:** `tests/integration/api/test_info_endpoints.py`

---

## **Test Case: TC-API-008**
**Summary:** API – GET /live_metadata – Present Case

**Objective:** Validate live metadata endpoint returns complete fiber metadata when available.

**Priority:** Medium

**Components/Labels:** focus-server, api, metadata, live

**Requirements:** FOCUS-API-METADATA

**Pre-Conditions:**
- fiber_metadata configured
- Live mode enabled

**Test Data:**
N/A (GET request)

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | GET /live_metadata | None | HTTP 200 |
| 2 | Validate schema | Response | Contains dx, prr, fiber_* fields |
| 3 | Check dx field | response.dx | Numeric value > 0 |
| 4 | Check prr field | response.prr | Integer > 0 |
| 5 | Check fiber_length | response.fiber_length | Numeric > 0 |
| 6 | Validate all required fields | Response | No null values |
| 7 | Check response format | Content-Type | application/json |

**Expected Result (overall):**
- Complete metadata returned
- All fields populated
- Valid data types

**Post-Conditions:**
None

**Assertions:**
```python
assert response.status_code == 200
assert response.json()['dx'] > 0
assert response.json()['prr'] > 0
assert all(v is not None for v in response.json().values())
```

**Environment:** Dev/Staging with fiber_metadata

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_live_metadata_present`
**Test File:** `tests/integration/api/test_info_endpoints.py`

---

## **Test Case: TC-API-009**
**Summary:** API – GET /live_metadata – Missing Case

**Objective:** Validate proper 404 when live metadata is not available.

**Priority:** Medium

**Components/Labels:** focus-server, api, metadata, live, negative-test

**Requirements:** FOCUS-API-METADATA

**Pre-Conditions:**
- fiber_metadata NOT configured or null
- Server running

**Test Data:**
N/A (GET request)

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Ensure fiber_metadata=None | Server config | Metadata not available |
| 2 | GET /live_metadata | None | HTTP 404 |
| 3 | Validate error message | Response | "Metadata not available" |
| 4 | Check response structure | Response | Valid JSON error |
| 5 | Verify no crash | Server logs | No exceptions |
| 6 | Check no empty 200 | Response | Not 200 with empty body |

**Expected Result (overall):**
- Clean 404 error
- Clear message
- No server errors

**Post-Conditions:**
None

**Assertions:**
```python
assert response.status_code == 404
assert "not available" in response.json()['error'].lower()
assert response.json() != {}
```

**Environment:** Dev/Staging without fiber_metadata

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_live_metadata_missing`
**Test File:** `tests/integration/api/test_info_endpoints.py`

---

## **Test Case: TC-API-010**
**Summary:** API – POST /recordings_in_time_range

**Objective:** Validate endpoint returns precise recording windows that intersect requested range.

**Priority:** High

**Components/Labels:** focus-server, api, history, recordings, mongo

**Requirements:** FOCUS-API-REC-RANGE

**Pre-Conditions:**
- MongoDB accessible
- Recordings exist in database
- rec_mapper populated

**Test Data:**
```json
{
  "start_time": 1700000000,
  "end_time": 1700000600
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /recordings_in_time_range | Time window | HTTP 200 |
| 2 | Validate response format | Response | List of [start, end] tuples |
| 3 | Check overlap | Each recording | Overlaps with request |
| 4 | Validate timestamps | All values | Valid epoch timestamps |
| 5 | Check ordering | Recording list | Sorted by start_time |
| 6 | Test with no recordings | Future time range | Empty list [] |
| 7 | Test ongoing recordings | Current time | end_time handled correctly |

**Expected Result (overall):**
- Correct recordings returned
- Proper overlap calculation
- Ongoing recordings handled

**Post-Conditions:**
None

**Assertions:**
```python
assert response.status_code == 200
assert isinstance(response.json(), list)
assert all(isinstance(r, list) and len(r) == 2 for r in response.json())
assert all(r[0] < request_end and r[1] > request_start for r in recordings)
```

**Environment:** Staging/Production (needs data)

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_recordings_in_time_range`
**Test File:** `tests/integration/api/test_history_endpoints.py`

---

# 🟠 SECTION B: Resilience & Integration Tests (Missing)

## **Test Case: TC-RESILIENCE-001**
**Summary:** Integration – MongoDB Outage Resilience

**Objective:** Ensure MongoDB dependency outage fails fast without launching processing jobs.

**Priority:** Critical

**Components/Labels:** focus-server, integration, resilience, mongodb, outage

**Requirements:** FOCUS-RESILIENCE-MONGO

**Pre-Conditions:**
- MongoDB can be disabled (K8s access)
- Historical payload ready
- Monitoring available

**Test Data:**
- Valid historical configuration payload
- MongoDB deployment name: "mongodb"

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Verify MongoDB healthy | kubectl get pods | MongoDB running |
| 2 | Scale MongoDB to 0 | kubectl scale --replicas=0 | MongoDB stopped |
| 3 | Verify MongoDB unreachable | Connection test | Connection refused |
| 4 | POST /configure | Historical payload | HTTP 503 Service Unavailable |
| 5 | Check error message | Response body | "MongoDB unavailable" |
| 6 | Verify no K8s job created | kubectl get jobs | No new jobs |
| 7 | Check RabbitMQ | Queue list | No new queues |
| 8 | Verify server didn't crash | Server logs | Error logged, still running |
| 9 | Scale MongoDB to 1 | kubectl scale --replicas=1 | MongoDB restored |
| 10 | POST /configure again | Same payload | HTTP 200 (recovery) |

**Expected Result (overall):**
- Clean 503 failure during outage
- No resource leaks
- Automatic recovery when MongoDB returns
- No cascading failures

**Post-Conditions:**
- MongoDB restored
- Server operational

**Assertions:**
```python
assert outage_response.status_code == 503
assert "mongo" in outage_response.json()['error'].lower()
assert not kubernetes.new_jobs_created()
assert not rabbitmq.new_queues_created()
assert recovery_response.status_code == 200
```

**Environment:** Staging (requires K8s access)

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_mongodb_outage_handling`
**Test File:** `tests/integration/infrastructure/test_resilience.py`

---

## **Test Case: TC-RESILIENCE-002**
**Summary:** Integration – RabbitMQ Outage Resilience

**Objective:** Validate graceful upstream failure (AMQP) without launching downstream resources.

**Priority:** Critical

**Components/Labels:** focus-server, integration, resilience, rabbitmq, outage

**Requirements:** FOCUS-RESILIENCE-RABBIT

**Pre-Conditions:**
- RabbitMQ can be blocked
- Live payload ready
- Network control available

**Test Data:**
- Valid live configuration payload
- RabbitMQ service: rabbitmq-panda

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Verify RabbitMQ healthy | Connection test | Connected |
| 2 | Block RabbitMQ network | iptables/credentials | Connection blocked |
| 3 | Verify RabbitMQ unreachable | AMQP connection | Connection refused |
| 4 | POST /configure | Live payload | HTTP 503 or 502 |
| 5 | Check error message | Response | "RabbitMQ unavailable" |
| 6 | Verify no K8s resources | kubectl | No Job/Service created |
| 7 | Check server logs | Logs | Upstream error logged |
| 8 | Verify no crash | Process status | Server still running |
| 9 | Restore RabbitMQ | Unblock | Connection restored |
| 10 | POST /configure again | Same payload | HTTP 200 |

**Expected Result (overall):**
- Proper 5xx error during outage
- Clear error messages
- No resource allocation
- Quick recovery

**Post-Conditions:**
- RabbitMQ restored
- Server operational

**Assertions:**
```python
assert outage_response.status_code in [502, 503]
assert "rabbit" in outage_response.json()['error'].lower()
assert not kubernetes.job_created()
assert server.is_running()
assert recovery_response.status_code == 200
```

**Environment:** Staging

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_rabbitmq_outage_handling`
**Test File:** `tests/integration/infrastructure/test_resilience.py`

---

## **Test Case: TC-INTEGRATION-001**
**Summary:** Integration – Invalid Configure Does Not Launch Orchestration

**Objective:** Prove invalid input is rejected with 400 and does not start Baby/K8s/Rabbit jobs.

**Priority:** Critical

**Components/Labels:** focus-server, integration, validation, orchestration

**Requirements:** FOCUS-API-VALIDATION

**Pre-Conditions:**
- All systems operational
- Monitoring available

**Test Data:**
```json
{
  "channels": {"min": 300, "max": 100},  // Invalid
  "frequencyRange": {"min": 1000, "max": 0},  // Invalid
  // ... rest of payload
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Record initial state | K8s jobs, RabbitMQ queues | Baseline recorded |
| 2 | POST /configure | Invalid payload | HTTP 400 |
| 3 | Check error details | Response | Structured validation errors |
| 4 | Verify no K8s activity | kubectl events | No new events |
| 5 | Check RabbitMQ | Queue list | No new queues |
| 6 | Verify MongoDB | Collections | No new documents |
| 7 | Check server logs | Logs | Validation logged, no errors |
| 8 | Compare final state | All systems | No changes from baseline |

**Expected Result (overall):**
- 400 rejection
- Zero side effects
- Clean validation

**Post-Conditions:**
None

**Assertions:**
```python
assert response.status_code == 400
assert kubernetes.state == initial_k8s_state
assert rabbitmq.queues == initial_queues
assert mongodb.document_count == initial_count
```

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_invalid_configure_no_orchestration`
**Test File:** `tests/integration/api/test_orchestration_validation.py`

---

## **Test Case: TC-INTEGRATION-002**
**Summary:** Integration – History with Empty Window Returns 400

**Objective:** Ensure "no data" short-circuits with no orchestration or storage scanning.

**Priority:** High

**Components/Labels:** focus-server, integration, history, validation

**Requirements:** FOCUS-API-CONFIGURE

**Pre-Conditions:**
- MongoDB accessible
- Time window with no recordings

**Test Data:**
```json
{
  "start_time": 2000000000,  // Far future
  "end_time": 2000000600,
  // ... rest of payload
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Verify no recordings exist | Time window query | Empty result |
| 2 | POST /configure | Empty window payload | HTTP 400 |
| 3 | Check error message | Response | "No recordings found" |
| 4 | Verify no K8s job | kubectl | No job created |
| 5 | Check storage access | Storage logs | No read attempts |
| 6 | Verify MongoDB queries | Query logs | Only lookup, no writes |
| 7 | Check quick response | Response time | < 500ms |

**Expected Result (overall):**
- Clean 400 error
- No resource usage
- Fast failure

**Post-Conditions:**
None

**Assertions:**
```python
assert response.status_code == 400
assert "no recording" in response.json()['error'].lower()
assert response.elapsed.total_seconds() < 0.5
assert not storage.access_logged()
```

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_history_empty_window`
**Test File:** `tests/integration/api/test_history_validation.py`

---

## **Test Case: TC-E2E-001**
**Summary:** E2E – Configure → Metadata → gRPC Stream (Mock)

**Objective:** Validate full integration path from configuration to streaming.

**Priority:** Critical

**Components/Labels:** focus-server, e2e, integration, grpc, streaming

**Requirements:** FOCUS-E2E-GRPC

**Pre-Conditions:**
- Mock gRPC server available
- Full system operational

**Test Data:**
- Standard live configuration payload
- Expected stream message format

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | Live payload | HTTP 200, get job_id |
| 2 | Extract stream details | Response | stream_url, stream_port |
| 3 | GET /metadata/{job_id} | job_id | HTTP 200, config matches |
| 4 | Connect to gRPC stream | stream_url:port | Connection established |
| 5 | Receive first message | Stream | Message within 1 second |
| 6 | Validate message format | Message | Contains expected fields |
| 7 | Receive 10 messages | Stream | All valid format |
| 8 | Disconnect gracefully | gRPC client | Clean disconnect |
| 9 | Stop job | DELETE /jobs/{job_id} | Job cleaned up |

**Expected Result (overall):**
- Complete flow works
- Stream delivers data
- Clean lifecycle

**Post-Conditions:**
- Job cleaned up
- Resources released

**Assertions:**
```python
assert configure_response.status_code == 200
assert metadata_response.json() == original_config
assert grpc_connection.is_connected()
assert first_message.timestamp is not None
assert all(msg.is_valid() for msg in messages[:10])
```

**Environment:** Integration environment

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_e2e_configure_to_stream`
**Test File:** `tests/integration/e2e/test_full_flow.py`

---

# 🟡 SECTION C: Security & Performance Tests (Missing)

## **Test Case: TC-SECURITY-001**
**Summary:** Security – Malformed Input Handling

**Objective:** Validate input hardening against malformed, oversized, and injection attempts.

**Priority:** Critical

**Components/Labels:** focus-server, security, input-validation, hardening

**Requirements:** FOCUS-SEC-ROBUSTNESS

**Pre-Conditions:**
- Security logging enabled
- WAF/validation active

**Test Data:**
```
1. Malformed JSON: {"invalid_json": unclosed
2. SQL Injection: ?search='1' OR '1'='1
3. XSS Attempt: <script>alert('xss')</script>
4. XXE Attack: <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
5. Oversized Payload: 10MB JSON
6. Unicode exploits: \u0000 null bytes
7. Path traversal: ../../etc/passwd
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST malformed JSON | Broken JSON | HTTP 400 |
| 2 | GET with SQL injection | SQLi in params | Sanitized, no error |
| 3 | POST with XSS | Script tags | Escaped/rejected |
| 4 | POST XXE payload | XML with entity | Rejected |
| 5 | POST oversized payload | 10MB JSON | HTTP 413 or handled |
| 6 | Send null bytes | \u0000 in strings | Sanitized |
| 7 | Path traversal attempt | ../.. in paths | Blocked |
| 8 | Check security logs | Log entries | All attempts logged |
| 9 | Verify no crashes | Server status | Still running |

**Expected Result (overall):**
- All attacks blocked
- No 500 errors
- Security events logged
- Server stable

**Post-Conditions:**
None

**Assertions:**
```python
assert all(r.status_code != 500 for r in attack_responses)
assert malformed_response.status_code == 400
assert xxe_response.status_code in [400, 422]
assert security_log.contains_all_attempts()
assert server.is_running()
```

**Environment:** Staging (preferably)

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_security_malformed_inputs`
**Test File:** `tests/integration/security/test_input_validation.py`

---

## **Test Case: TC-SECURITY-002**
**Summary:** Security – CORS Headers Validation

**Objective:** Ensure proper CORS headers are present for cross-origin requests.

**Priority:** Medium

**Components/Labels:** focus-server, security, cors, headers

**Requirements:** FOCUS-SEC-CORS

**Pre-Conditions:**
- CORS configured
- Different origins available

**Test Data:**
- Origin: https://frontend.example.com
- Methods: GET, POST, OPTIONS

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | OPTIONS /configure | Origin header | CORS headers present |
| 2 | Check Allow-Origin | Response headers | Matches or * |
| 3 | Check Allow-Methods | Response headers | Contains POST, GET |
| 4 | Check Allow-Headers | Response headers | Contains Content-Type |
| 5 | POST with Origin | Different origin | Accepted or rejected per policy |
| 6 | Check preflight cache | Max-Age header | Present and > 0 |

**Expected Result (overall):**
- CORS properly configured
- Preflight requests handled
- Policy enforced

**Post-Conditions:**
None

**Assertions:**
```python
assert 'Access-Control-Allow-Origin' in response.headers
assert 'POST' in response.headers['Access-Control-Allow-Methods']
assert options_response.status_code == 200
```

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_cors_headers`
**Test File:** `tests/integration/security/test_cors.py`

---

## **Test Case: TC-PERFORMANCE-001**
**Summary:** Performance – /configure Endpoint Latency P95

**Objective:** Ensure /configure response times meet SLA (p95 < 2 seconds).

**Priority:** Medium

**Components/Labels:** focus-server, performance, latency, sla

**Requirements:** FOCUS-PERF-CONFIGURE

**Pre-Conditions:**
- Minimal concurrent load
- Warm system (not cold start)

**Test Data:**
- Standard live configuration payload
- 100 sequential requests

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Warm up system | 5 requests | System ready |
| 2 | Send 100 sequential requests | Live payload | All succeed |
| 3 | Record response times | Each request | Times logged |
| 4 | Calculate percentiles | All times | p50, p95, p99 |
| 5 | Validate p95 | 95th percentile | < 2.0 seconds |
| 6 | Check for outliers | All times | No extreme outliers |
| 7 | Monitor memory | During test | No leaks |
| 8 | Check CPU usage | During test | < 80% average |

**Expected Result (overall):**
- p95 < 2.0 seconds
- p99 < 5.0 seconds
- No memory leaks
- Stable performance

**Post-Conditions:**
- Clean up created jobs

**Assertions:**
```python
assert percentile(response_times, 95) < 2.0
assert percentile(response_times, 99) < 5.0
assert max(response_times) < 10.0
assert memory_end - memory_start < 100_000_000  # 100MB
```

**Environment:** Staging (non-loaded)

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_configure_latency_p95`
**Test File:** `tests/integration/performance/test_latency.py`

---

## **Test Case: TC-PERFORMANCE-002**
**Summary:** Performance – Concurrent Load Handling

**Objective:** Validate system handles concurrent requests without degradation.

**Priority:** Medium

**Components/Labels:** focus-server, performance, load, concurrency

**Requirements:** FOCUS-PERF-LOAD

**Pre-Conditions:**
- Load testing tool ready
- System metrics available

**Test Data:**
- 10 concurrent users
- 100 requests total
- Mixed live/historical

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Start metrics collection | CPU, memory, network | Baseline recorded |
| 2 | Launch 10 concurrent users | Mixed payloads | All start |
| 3 | Each user sends 10 requests | Sequential | Requests sent |
| 4 | Monitor response times | All responses | Times recorded |
| 5 | Check success rate | All responses | > 95% success |
| 6 | Monitor resource usage | During test | CPU < 90% |
| 7 | Check for errors | Server logs | No critical errors |
| 8 | Validate consistency | All responses | Valid data |

**Expected Result (overall):**
- > 95% success rate
- Response times stable
- No resource exhaustion

**Post-Conditions:**
- Clean up all jobs

**Assertions:**
```python
assert success_rate > 0.95
assert max_cpu_usage < 0.9
assert no_critical_errors_in_logs()
assert response_time_variance < 2.0  # seconds
```

**Environment:** Staging

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_concurrent_load`
**Test File:** `tests/integration/performance/test_load.py`

---

# 🟢 SECTION D: Existing Tests Not in Jira (Need Documentation)

## **Test Case: TC-EXISTING-001**
**Summary:** Infrastructure – Basic Connectivity Test

**Objective:** Validate basic connectivity to all required services (MongoDB, RabbitMQ, Focus Server).

**Priority:** High

**Components/Labels:** infrastructure, connectivity, smoke-test

**Requirements:** INFRA-CONNECTIVITY

**Pre-Conditions:**
- Environment variables configured
- Network access available

**Test Data:**
- Service endpoints from configuration
- Connection timeouts: 30 seconds

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Test MongoDB connection | Connection string | Connected successfully |
| 2 | Query test collection | db.test.find() | Query executes |
| 3 | Test RabbitMQ connection | AMQP URL | Connected |
| 4 | Declare test queue | test_queue | Queue created |
| 5 | Test Focus Server health | GET /health | HTTP 200 |
| 6 | Test Frontend access | Frontend URL | Page loads |
| 7 | Measure connection times | All services | All < 5 seconds |

**Expected Result (overall):**
- All services reachable
- Connections stable
- Acceptable latency

**Post-Conditions:**
- Test queue deleted
- Connections closed

**Assertions:**
```python
assert mongodb.is_connected()
assert rabbitmq.is_connected()
assert focus_server_response.status_code == 200
assert all(time < 5.0 for time in connection_times)
```

**Environment:** Any

**Automation Status:** IMPLEMENTED
**Test Function:** `test_basic_connectivity`
**Test File:** `tests/integration/infrastructure/test_basic_connectivity.py`

---

## **Test Case: TC-EXISTING-002**
**Summary:** Processing – Spectrogram Pipeline Validation

**Objective:** Validate spectrogram data processing and transformation pipeline.

**Priority:** Medium

**Components/Labels:** processing, spectrogram, pipeline, data-transformation

**Requirements:** PROC-SPECTROGRAM

**Pre-Conditions:**
- Processing pipeline available
- Sample data ready

**Test Data:**
- Raw sensor data (1000 samples)
- Expected spectrogram dimensions

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Submit raw data | Sensor samples | Job created |
| 2 | Monitor job status | Job ID | Status: processing |
| 3 | Wait for completion | Timeout 30s | Status: completed |
| 4 | Retrieve spectrogram | Job ID | Data returned |
| 5 | Validate dimensions | Output shape | Matches expected |
| 6 | Check frequency bins | Frequency axis | Correct range |
| 7 | Validate magnitude values | Data values | Within valid range |
| 8 | Check metadata | Output metadata | Complete and accurate |

**Expected Result (overall):**
- Processing completes successfully
- Output format correct
- Data integrity maintained

**Post-Conditions:**
- Test data cleaned up

**Assertions:**
```python
assert job.status == 'completed'
assert spectrogram.shape == expected_shape
assert 0 <= spectrogram.min() <= spectrogram.max() <= 1
assert metadata['sample_rate'] == input_sample_rate
```

**Environment:** Dev/Staging

**Automation Status:** IMPLEMENTED
**Test Function:** `test_spectrogram_pipeline`
**Test File:** `tests/integration/api/test_spectrogram_pipeline.py`

---

## **Test Case: TC-EXISTING-003**
**Summary:** API – Historic Playback Flow

**Objective:** Validate complete historic playback workflow from request to data delivery.

**Priority:** High

**Components/Labels:** api, history, playback, workflow

**Requirements:** FOCUS-HISTORY-PLAYBACK

**Pre-Conditions:**
- Historical data available
- Time range with recordings

**Test Data:**
- Time range with known recordings
- Expected data characteristics

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Query available recordings | Time range | Recordings found |
| 2 | Configure historic playback | Config payload | Job created |
| 3 | Start playback | Job ID | Playback initiated |
| 4 | Receive data stream | Stream connection | Data flowing |
| 5 | Validate data sequence | Timestamps | Chronological order |
| 6 | Check data completeness | Coverage | No gaps |
| 7 | Stop playback | Stop command | Clean stop |
| 8 | Verify cleanup | Resources | All released |

**Expected Result (overall):**
- Complete playback flow works
- Data delivered in order
- Clean resource management

**Post-Conditions:**
- All resources cleaned up

**Assertions:**
```python
assert playback_job.created
assert all(data[i].timestamp <= data[i+1].timestamp for i in range(len(data)-1))
assert coverage_percentage > 95
assert resources_released()
```

**Environment:** Staging/Production

**Automation Status:** IMPLEMENTED
**Test Function:** `test_historic_playback_flow`
**Test File:** `tests/integration/api/test_historic_playback_flow.py`

---

## **Test Case: TC-EXISTING-004**
**Summary:** API – Live Monitoring Flow

**Objective:** Validate live monitoring workflow from configuration to real-time streaming.

**Priority:** High

**Components/Labels:** api, live, monitoring, streaming

**Requirements:** FOCUS-LIVE-MONITORING

**Pre-Conditions:**
- Live data source available
- System in monitoring mode

**Test Data:**
- Live configuration parameters
- Expected stream characteristics

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Configure live monitoring | Live config | Job created |
| 2 | Connect to stream | Stream endpoint | Connected |
| 3 | Receive live data | Stream | Data arriving |
| 4 | Validate real-time delivery | Timestamps | Current time |
| 5 | Monitor data rate | Messages/sec | Matches PRR |
| 6 | Check data quality | Signal metrics | Within specs |
| 7 | Test 5 minute stability | Continuous | No disconnects |
| 8 | Stop monitoring | Stop command | Clean shutdown |

**Expected Result (overall):**
- Live streaming works
- Real-time data delivery
- Stable connection

**Post-Conditions:**
- Stream closed
- Job cleaned up

**Assertions:**
```python
assert stream.is_connected()
assert abs(data.timestamp - time.now()) < 1.0  # Within 1 second
assert data_rate == expected_prr
assert connection_duration >= 300  # 5 minutes
```

**Environment:** Any

**Automation Status:** IMPLEMENTED
**Test Function:** `test_live_monitoring_flow`
**Test File:** `tests/integration/api/test_live_monitoring_flow.py`

---

## **Test Case: TC-EXISTING-005**
**Summary:** UI – Dynamic ROI Adjustment

**Objective:** Validate dynamic Region of Interest adjustment functionality.

**Priority:** Medium

**Components/Labels:** ui, roi, dynamic-adjustment, interactive

**Requirements:** UI-ROI-DYNAMIC

**Pre-Conditions:**
- UI accessible
- ROI feature enabled

**Test Data:**
- Various ROI coordinates
- Edge cases (min/max)

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Set initial ROI | x1=100, y1=100, x2=500, y2=500 | ROI displayed |
| 2 | Adjust top-left corner | Move to 50,50 | ROI updated |
| 3 | Adjust bottom-right | Move to 600,600 | ROI expanded |
| 4 | Test minimum size | 10x10 pixels | Minimum enforced |
| 5 | Test maximum size | Full canvas | Maximum enforced |
| 6 | Test aspect ratio lock | Lock 16:9 | Ratio maintained |
| 7 | Save ROI settings | Save button | Settings persisted |
| 8 | Reload and verify | Page refresh | ROI restored |

**Expected Result (overall):**
- ROI adjustments work smoothly
- Constraints enforced
- Settings persist

**Post-Conditions:**
- Reset to defaults

**Assertions:**
```python
assert roi.width >= 10 and roi.height >= 10
assert roi.width <= canvas.width
assert roi.aspect_ratio == 16/9 when locked
assert saved_roi == loaded_roi
```

**Environment:** Any

**Automation Status:** IMPLEMENTED
**Test Function:** `test_dynamic_roi_adjustment`
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## **Test Case: TC-EXISTING-006**
**Summary:** External – PZ Integration Validation

**Objective:** Validate integration with external PZ system.

**Priority:** High

**Components/Labels:** external, integration, pz-system

**Requirements:** EXT-PZ-INTEGRATION

**Pre-Conditions:**
- PZ system accessible
- Integration credentials available

**Test Data:**
- PZ API endpoints
- Test commands

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Connect to PZ system | Credentials | Authenticated |
| 2 | Send test command | PING | PONG response |
| 3 | Query PZ status | GET /status | Status returned |
| 4 | Submit PZ job | Job payload | Job accepted |
| 5 | Monitor PZ job | Job ID | Progress updates |
| 6 | Retrieve PZ results | Job ID | Results available |
| 7 | Validate data format | Results | Expected format |
| 8 | Test error handling | Invalid command | Proper error |

**Expected Result (overall):**
- PZ integration functional
- Commands processed
- Results retrievable

**Post-Conditions:**
- Test job cleaned up

**Assertions:**
```python
assert pz_client.is_authenticated()
assert pz_response.status == 'success'
assert pz_job.state == 'completed'
assert pz_results.format == expected_format
```

**Environment:** Staging/Production

**Automation Status:** IMPLEMENTED
**Test Function:** `test_pz_integration`
**Test File:** `tests/integration/infrastructure/test_pz_integration.py`

---

## **Test Case: TC-EXISTING-007**
**Summary:** Validation – Input Validators Testing

**Objective:** Validate all input validation functions work correctly.

**Priority:** Medium

**Components/Labels:** validation, input-validation, unit-test

**Requirements:** VAL-INPUT-VALIDATORS

**Pre-Conditions:**
- Validators module loaded

**Test Data:**
- Valid and invalid inputs for each validator
- Edge cases

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Test channel validator | Valid: 1-1000 | Pass |
| 2 | Test channel validator | Invalid: -1, 9999 | Fail |
| 3 | Test frequency validator | Valid: 0-100000 | Pass |
| 4 | Test frequency validator | Invalid: negative | Fail |
| 5 | Test time validator | Valid epoch | Pass |
| 6 | Test time validator | Invalid: future | Fail |
| 7 | Test view_type validator | Valid: 0,1,2 | Pass |
| 8 | Test view_type validator | Invalid: 99 | Fail |

**Expected Result (overall):**
- All validators work correctly
- Clear error messages
- Edge cases handled

**Post-Conditions:**
None

**Assertions:**
```python
assert channel_validator(1) == True
assert channel_validator(-1) == False
assert frequency_validator(1000) == True
assert time_validator(valid_epoch) == True
```

**Environment:** Any

**Automation Status:** IMPLEMENTED
**Test Function:** `test_validators`
**Test File:** `tests/unit/test_validators.py`

---

## **Test Case: TC-EXISTING-008**
**Summary:** Models – Pydantic Model Validation

**Objective:** Validate all Pydantic models enforce correct data types and constraints.

**Priority:** Medium

**Components/Labels:** models, validation, pydantic

**Requirements:** MODEL-VALIDATION

**Pre-Conditions:**
- Models module loaded

**Test Data:**
- Valid and invalid model data
- Type mismatches

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Test ConfigureRequest | Valid data | Model created |
| 2 | Test ConfigureRequest | Invalid types | ValidationError |
| 3 | Test ConfigureResponse | Valid data | Model created |
| 4 | Test required fields | Missing fields | ValidationError |
| 5 | Test optional fields | Without optional | Model created |
| 6 | Test nested models | Nested data | Proper parsing |
| 7 | Test enum fields | Valid enums | Accepted |
| 8 | Test enum fields | Invalid enums | Rejected |

**Expected Result (overall):**
- Models validate correctly
- Type enforcement works
- Clear validation errors

**Post-Conditions:**
None

**Assertions:**
```python
assert ConfigureRequest(**valid_data)
with pytest.raises(ValidationError):
    ConfigureRequest(**invalid_data)
assert model.view_type in [0, 1, 2]
```

**Environment:** Any

**Automation Status:** IMPLEMENTED
**Test Function:** `test_models_validation`
**Test File:** `tests/unit/test_models_validation.py`

---

## **Test Case: TC-EXISTING-009**
**Summary:** Configuration – Config Loading and Environment Selection

**Objective:** Validate configuration loading for different environments.

**Priority:** High

**Components/Labels:** configuration, environment, settings

**Requirements:** CONFIG-MANAGEMENT

**Pre-Conditions:**
- Config files present
- Environment variable set

**Test Data:**
- Different environment names
- Config overrides

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Load staging config | env=staging | Config loaded |
| 2 | Verify staging URLs | Config values | Staging URLs |
| 3 | Load production config | env=production | Config loaded |
| 4 | Verify production URLs | Config values | Production URLs |
| 5 | Test config override | Override values | Applied correctly |
| 6 | Test missing config | Invalid env | Default loaded |
| 7 | Validate all required keys | Config keys | All present |
| 8 | Test config refresh | Reload | Updated values |

**Expected Result (overall):**
- Configs load correctly
- Environment selection works
- Overrides applied

**Post-Conditions:**
- Reset to default

**Assertions:**
```python
assert config.environment == 'staging'
assert 'staging' in config.get('focus_server.base_url')
assert config.get('mongodb.host') is not None
assert len(config.get_all_keys()) > 20
```

**Environment:** Any

**Automation Status:** IMPLEMENTED
**Test Function:** `test_config_loading`
**Test File:** `tests/unit/test_config_loading.py`

---

## **Test Case: TC-EXISTING-010**
**Summary:** UI – Button Interactions Test

**Objective:** Validate all UI buttons respond correctly to user interactions.

**Priority:** Low

**Components/Labels:** ui, buttons, interaction, playwright

**Requirements:** UI-INTERACTIONS

**Pre-Conditions:**
- UI accessible
- Playwright configured

**Test Data:**
- Button selectors
- Expected actions

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Navigate to UI | URL | Page loaded |
| 2 | Click Configure button | Button selector | Modal opens |
| 3 | Click Submit button | Submit selector | Form submitted |
| 4 | Click Cancel button | Cancel selector | Modal closed |
| 5 | Test disabled buttons | Disabled state | Not clickable |
| 6 | Test button tooltips | Hover | Tooltip shown |
| 7 | Test keyboard navigation | Tab key | Focus moves |
| 8 | Test button animations | Click | Animation plays |

**Expected Result (overall):**
- All buttons functional
- Proper state management
- Good UX

**Post-Conditions:**
- Return to home

**Assertions:**
```python
assert modal.is_visible() after configure_click
assert form.is_submitted() after submit
assert button.is_disabled() when appropriate
assert tooltip.text == expected_text
```

**Environment:** Any

**Automation Status:** IMPLEMENTED
**Test Function:** `test_button_interactions`
**Test File:** `tests/ui/generated/test_button_interactions.py`

---

## **Test Case: TC-EXISTING-011**
**Summary:** UI – Form Validation Test

**Objective:** Validate form inputs and validation messages.

**Priority:** Low

**Components/Labels:** ui, forms, validation, playwright

**Requirements:** UI-FORM-VALIDATION

**Pre-Conditions:**
- UI accessible
- Forms available

**Test Data:**
- Valid and invalid form data
- Edge cases

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Enter valid data | All fields | No errors |
| 2 | Submit valid form | Submit button | Success |
| 3 | Enter invalid email | bad-email | Error shown |
| 4 | Leave required empty | Empty field | Required error |
| 5 | Exceed max length | Long string | Truncated/error |
| 6 | Test number fields | Non-numeric | Rejected |
| 7 | Test date fields | Invalid date | Error |
| 8 | Test form reset | Reset button | Fields cleared |

**Expected Result (overall):**
- Validation works correctly
- Clear error messages
- Good UX

**Post-Conditions:**
- Form reset

**Assertions:**
```python
assert form.is_valid() with valid_data
assert error_message.is_visible() with invalid_data
assert field.value == '' after reset
assert submit_button.is_disabled() when invalid
```

**Environment:** Any

**Automation Status:** IMPLEMENTED
**Test Function:** `test_form_validation`
**Test File:** `tests/ui/generated/test_form_validation.py`

---

## **Test Case: TC-EXISTING-012**
**Summary:** Infrastructure – External Service Connectivity

**Objective:** Validate connectivity to external third-party services.

**Priority:** Medium

**Components/Labels:** infrastructure, external, connectivity

**Requirements:** INFRA-EXTERNAL

**Pre-Conditions:**
- External services configured
- Network access available

**Test Data:**
- External service endpoints
- API keys (if required)

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Test S3 connectivity | S3 endpoint | Connected |
| 2 | List S3 buckets | Credentials | Buckets listed |
| 3 | Test external API | API endpoint | Response received |
| 4 | Validate API auth | API key | Authenticated |
| 5 | Test DNS resolution | Hostnames | Resolved |
| 6 | Check SSL certificates | HTTPS endpoints | Valid certs |
| 7 | Test proxy (if used) | Proxy settings | Working |
| 8 | Measure latencies | All services | Acceptable |

**Expected Result (overall):**
- All external services reachable
- Authentication works
- Acceptable performance

**Post-Conditions:**
None

**Assertions:**
```python
assert s3_client.list_buckets() is not None
assert external_api_response.status_code == 200
assert all(latency < 2.0 for latency in service_latencies)
assert ssl_cert.is_valid()
```

**Environment:** Any

**Automation Status:** IMPLEMENTED
**Test Function:** `test_external_connectivity`
**Test File:** `tests/integration/infrastructure/test_external_connectivity.py`

---

# 📊 Summary

## **Total Test Cases: 42**

### **Distribution:**
- **Missing API Tests:** 10
- **Missing Integration Tests:** 5
- **Missing Security Tests:** 2
- **Missing Performance Tests:** 2
- **Service/Orchestration Tests:** 4
- **Data Quality Tests:** 7 (already in Jira)
- **Existing Automation Tests:** 12

### **Priority Breakdown:**
- **Critical:** 8 tests
- **High:** 20 tests
- **Medium:** 12 tests
- **Low:** 2 tests

### **Implementation Status:**
- **To Be Automated:** 30 tests
- **Already Implemented:** 12 tests

---

## **Next Steps:**

1. **Create Jira tickets** for all TC-API-*, TC-RESILIENCE-*, TC-INTEGRATION-*, TC-SECURITY-*, TC-PERFORMANCE-* tests
2. **Create Jira tickets** for all TC-EXISTING-* tests (currently in automation but not in Jira)
3. **Implement missing tests** starting with Critical priority
4. **Add Xray markers** to all existing tests
5. **Setup CI/CD integration** with Xray reporting

---

**All test cases are now ready for import to Jira Xray!** 🎯
