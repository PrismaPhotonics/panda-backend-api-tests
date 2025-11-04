# 📋 טסטים לתיקון וטסטים חסרים עבור Xray in Jira

**תאריך:** 2025-10-19  
**מטרה:** רשימה מסודרת של כל הטסטים שצריך לתקן והטסטים החסרים

---

# ⚠️ PART 1: טסטים קיימים שצריך לתקן

## **טסטים הבאים צריכים עדכון ב-Xray כי ה-API השתנה:**

---

### **TC-FIX-001: PZ-13547 - Live Configure (Happy Path) - UPDATED**

**Summary:** API – POST /config/{task_id} – Live Mode Configuration (Happy Path)

**Objective:** Validate that a valid live configuration using the /config/{task_id} endpoint successfully creates a task and returns proper confirmation.

**Priority:** Critical

**Components/Labels:** focus-server, api, live, config, task-management

**Requirements:** FOCUS-API-CONFIG

**Pre-Conditions:**
- PC-001: API base URL reachable (https://10.10.100.100/focus-server/)
- PC-002: System operational and ready
- PC-003: Valid task_id format available

**Test Data:**
```json
Endpoint: POST /config/{task_id}
task_id format: "live_monitoring_YYYYMMDD_HHMMSS_XXX"

Payload:
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
| 1 | Generate unique task_id | Format: live_{timestamp}_{random} | Valid task_id created |
| 2 | Validate task_id format | Check regex pattern | Format valid |
| 3 | Create ConfigTaskRequest | Live payload | Request object created |
| 4 | POST /config/{task_id} | task_id + payload | HTTP 200 OK |
| 5 | Validate response status | response.status | "Config received successfully" |
| 6 | Validate task_id in response | response.task_id | Matches input or null |
| 7 | Check server logs | Application logs | No errors logged |

**Expected Result (overall):**
- Configuration accepted successfully
- Task created with valid ID
- System ready for live monitoring
- No errors in processing

**Post-Conditions:**
- Task remains in system
- Resources allocated for task
- Cleanup via DELETE if needed

**Assertions:**
```python
assert response.status_code == 200
assert isinstance(response, ConfigTaskResponse)
assert response.status == "Config received successfully"
assert response.task_id == task_id or response.task_id is None
assert validate_task_id_format(task_id) == True
```

**Environment:** Dev/Staging/Production

**Automation Status:** IMPLEMENTED
**Test Function:** `test_configure_live_task_success`
**Test File:** `tests/integration/api/test_live_monitoring_flow.py`

**Notes:** 
- API changed from `/configure` to `/config/{task_id}`
- Response schema different from original Xray spec
- Update Xray to match current implementation

---

### **TC-FIX-002: PZ-13548 - Historical Configure (Happy Path) - UPDATED**

**Summary:** API – POST /config/{task_id} – Historical Mode Configuration (Happy Path)

**Objective:** Validate historical configuration using /config/{task_id} endpoint with time range successfully creates a task for historical playback.

**Priority:** Critical

**Components/Labels:** focus-server, api, history, config, playback

**Requirements:** FOCUS-API-CONFIG, FOCUS-API-HISTORY

**Pre-Conditions:**
- PC-010: MongoDB reachable with historical recordings
- PC-011: Time range with available recordings
- PC-012: Valid task_id format available

**Test Data:**
```json
Endpoint: POST /config/{task_id}
task_id format: "historic_playback_YYYYMMDD_HHMMSS_XXX"

Payload:
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
| 1 | Query MongoDB for recordings | Time range: 1700000000-1700000600 | Recordings exist |
| 2 | Generate unique task_id | Format: historic_{timestamp}_{random} | Valid task_id |
| 3 | Validate task_id format | Check pattern | Format valid |
| 4 | Create ConfigTaskRequest | Historical payload | Request created |
| 5 | POST /config/{task_id} | task_id + payload | HTTP 200 OK |
| 6 | Validate response status | response.status | "Config received successfully" |
| 7 | Verify task created | System state | Task exists |

**Expected Result (overall):**
- Historical configuration accepted
- Task created for time range
- System ready for historical playback
- Recordings available for range

**Post-Conditions:**
- Task cleanup if needed
- No MongoDB modifications

**Assertions:**
```python
assert response.status_code == 200
assert isinstance(response, ConfigTaskResponse)
assert response.status == "Config received successfully"
assert mongodb_recordings_exist(start_time, end_time)
assert validate_task_id_format(task_id) == True
```

**Environment:** Staging/Production (requires data)

**Automation Status:** IMPLEMENTED
**Test Function:** `test_configure_historic_task_success`
**Test File:** `tests/integration/api/test_historic_playback_flow.py`

**Notes:**
- API uses /config/{task_id} not /configure
- Update Xray to reflect current endpoint

---

### **TC-FIX-003: PZ-13563 - GET /metadata/{job_id} - ADD VALID CASE**

**Summary:** API – GET /metadata/{task_id} – Valid Task Metadata Retrieval

**Objective:** Add test for valid metadata retrieval (currently only invalid case exists).

**Priority:** High

**Components/Labels:** focus-server, api, metadata, tasks

**Requirements:** FOCUS-API-METADATA

**Pre-Conditions:**
- PC-001: Valid task created via /config/{task_id}
- PC-002: Task exists in system

**Test Data:**
```
Valid task_id: From previous /config call
Invalid task_ids: "non_existent", "12345", "", "../../etc/passwd"
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Create task via POST /config | Valid payload | Get task_id |
| 2 | GET /metadata/{task_id} | Valid task_id | HTTP 200 |
| 3 | Validate metadata returned | Response body | Contains configuration |
| 4 | Verify config matches | Original vs returned | Exact match |
| 5 | GET /metadata/{invalid} | "non_existent" | HTTP 404 |
| 6 | Validate error message | 404 response | "Task not found" or similar |
| 7 | Test path traversal | "../../etc/passwd" | HTTP 400 or 404 |
| 8 | Test empty ID | "" | HTTP 400 |

**Expected Result (overall):**
- Valid tasks return complete metadata
- Invalid tasks return proper 404
- No security vulnerabilities
- Clear error messages

**Post-Conditions:**
- Test task cleaned up

**Assertions:**
```python
# Valid case
assert valid_response.status_code == 200
assert valid_response.json()['task_id'] == task_id
assert valid_response.json()['config'] == original_config

# Invalid case  
assert invalid_response.status_code == 404
assert "not found" in invalid_response.json()['error'].lower()

# Security
assert path_traversal_response.status_code in [400, 404]
```

**Environment:** Any

**Automation Status:** PARTIALLY IMPLEMENTED (add valid case)
**Test Function:** `test_metadata_for_invalid_task_id` (exists), `test_metadata_for_valid_task_id` (TO ADD)
**Test File:** `tests/integration/api/test_live_monitoring_flow.py`

**Notes:**
- Currently only invalid case tested
- Add valid case test

---

# ❌ PART 2: טסטים חסרים - צריך להוסיף ל-Xray

## **SECTION A: API Validation Tests (חסר)**

---

### **TC-NEW-001: Invalid Time Range Validation**

**Summary:** API – POST /config/{task_id} – Invalid Time Range Rejection

**Objective:** Ensure invalid time ranges (start >= end) are rejected with proper 400 error.

**Priority:** High

**Components/Labels:** focus-server, api, validation, negative-test

**Requirements:** FOCUS-API-VALIDATION

**Pre-Conditions:**
- PC-001: API reachable

**Test Data:**
```json
Test Case A - start > end:
{
  "start_time": 1700000600,
  "end_time": 1700000000,
  "view_type": 0,
  ...
}

Test Case B - start == end:
{
  "start_time": 1700000000,
  "end_time": 1700000000,
  "view_type": 0,
  ...
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Generate task_id | Unique ID | Valid task_id |
| 2 | POST /config/{task_id} | start > end | HTTP 400 |
| 3 | Validate error message | Response | Contains "Invalid time range" |
| 4 | POST /config/{task_id} | start == end | HTTP 400 |
| 5 | Check no task created | System | Task doesn't exist |
| 6 | Verify logs | Server logs | Validation error logged |

**Expected Result (overall):**
- Invalid time ranges rejected with 400
- Clear error messages
- No task creation

**Post-Conditions:**
None

**Assertions:**
```python
assert response.status_code == 400
assert "time range" in response.json()['error'].lower()
assert not task_exists(task_id)
```

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_config_invalid_time_range`
**Test File:** `tests/integration/api/test_config_validation.py` (NEW FILE)

---

### **TC-NEW-002: Invalid Channel Range Validation**

**Summary:** API – POST /config/{task_id} – Invalid Channel Range Rejection

**Objective:** Confirm server blocks illegal channel windows (min > max, negative, out of bounds).

**Priority:** High

**Components/Labels:** focus-server, api, validation, negative-test

**Requirements:** FOCUS-API-VALIDATION

**Pre-Conditions:**
- PC-001: API reachable
- PC-002: System max channels known

**Test Data:**
```json
Test A - min > max:
{
  "channels": { "min": 300, "max": 100 },
  ...
}

Test B - negative:
{
  "channels": { "min": -5, "max": 10 },
  ...
}

Test C - out of bounds:
{
  "channels": { "min": 1, "max": 99999 },
  ...
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /config/{task_id} | min > max | HTTP 400 |
| 2 | Check error | Response | "Invalid channel range" |
| 3 | POST /config/{task_id} | Negative | HTTP 400 |
| 4 | POST /config/{task_id} | Out of bounds | HTTP 400 |
| 5 | Test boundary | min=1, max=max_channels | HTTP 200 |

**Expected Result (overall):**
- Invalid ranges rejected
- Boundary values work
- Clear errors

**Post-Conditions:**
None

**Assertions:**
```python
assert invalid_response.status_code == 400
assert "channel" in error_message.lower()
assert boundary_response.status_code == 200
```

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_config_invalid_channels`
**Test File:** `tests/integration/api/test_config_validation.py` (NEW FILE)

---

### **TC-NEW-003: Invalid Frequency Range Validation**

**Summary:** API – POST /config/{task_id} – Invalid Frequency Range Rejection

**Objective:** Validate rejection of malformed frequency ranges.

**Priority:** High

**Components/Labels:** focus-server, api, validation, negative-test

**Requirements:** FOCUS-API-VALIDATION

**Pre-Conditions:**
- PC-001: API reachable

**Test Data:**
```json
Test A - min > max:
{
  "frequencyRange": { "min": 500, "max": 0 },
  ...
}

Test B - negative:
{
  "frequencyRange": { "min": -100, "max": 500 },
  ...
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /config/{task_id} | min > max | HTTP 400 |
| 2 | Validate error | Response | "Invalid frequency range" |
| 3 | POST /config/{task_id} | Negative | HTTP 400 |
| 4 | Test valid range | min=0, max=1000 | HTTP 200 |

**Expected Result (overall):**
- Invalid rejected
- Valid accepted

**Post-Conditions:**
None

**Assertions:**
```python
assert invalid_response.status_code == 400
assert "frequency" in error_message.lower()
```

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_config_invalid_frequency`
**Test File:** `tests/integration/api/test_config_validation.py` (NEW FILE)

---

## **SECTION B: Info Endpoints (חסר)**

---

### **TC-NEW-004: GET /channels Endpoint**

**Summary:** API – GET /channels – Returns System Channel Bounds

**Objective:** Validate channel range endpoint returns authoritative bounds.

**Priority:** High

**Components/Labels:** focus-server, api, channels, info

**Requirements:** FOCUS-API-CHANNELS

**Pre-Conditions:**
- PC-001: API reachable
- PC-002: FocusManager.channels configured

**Test Data:**
N/A (GET request)

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | GET /channels | None | HTTP 200 |
| 2 | Validate schema | Response | Contains lowest_channel, highest_channel |
| 3 | Check lowest_channel | Value | == 1 |
| 4 | Check highest_channel | Value | > 0, matches config |
| 5 | Call 5 times | None | Consistent results |
| 6 | Check response time | Latency | < 100ms |

**Expected Result (overall):**
- Returns configured bounds
- Consistent across calls
- Fast response

**Post-Conditions:**
None

**Assertions:**
```python
assert response.status_code == 200
assert response.json()['lowest_channel'] == 1
assert response.json()['highest_channel'] > 0
```

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_get_channels`
**Test File:** `tests/integration/api/test_info_endpoints.py` (NEW FILE)

---

### **TC-NEW-005: GET /live_metadata - Present**

**Summary:** API – GET /live_metadata – Returns Metadata When Available

**Objective:** Validate live metadata endpoint returns complete fiber metadata.

**Priority:** Medium

**Components/Labels:** focus-server, api, metadata, live

**Requirements:** FOCUS-API-METADATA

**Pre-Conditions:**
- PC-001: fiber_metadata configured

**Test Data:**
N/A (GET request)

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | GET /live_metadata | None | HTTP 200 |
| 2 | Validate schema | Response | Contains dx, prr, fiber_* |
| 3 | Check dx | Value | > 0 |
| 4 | Check prr | Value | > 0 |
| 5 | Validate all fields | Response | No nulls |

**Expected Result (overall):**
- Complete metadata returned
- All fields populated

**Post-Conditions:**
None

**Assertions:**
```python
assert response.status_code == 200
assert response.json()['dx'] > 0
assert response.json()['prr'] > 0
```

**Environment:** Dev/Staging with metadata

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_get_live_metadata_present`
**Test File:** `tests/integration/api/test_info_endpoints.py` (NEW FILE)

---

### **TC-NEW-006: GET /live_metadata - Missing**

**Summary:** API – GET /live_metadata – Returns 404 When Unavailable

**Objective:** Validate proper 404 when metadata not available.

**Priority:** Medium

**Components/Labels:** focus-server, api, metadata, negative-test

**Requirements:** FOCUS-API-METADATA

**Pre-Conditions:**
- PC-001: fiber_metadata NOT configured

**Test Data:**
N/A (GET request)

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Ensure metadata=None | Server config | Not available |
| 2 | GET /live_metadata | None | HTTP 404 |
| 3 | Validate error | Response | "Not available" message |
| 4 | Check no crash | Logs | No exceptions |

**Expected Result (overall):**
- Clean 404
- Clear message

**Post-Conditions:**
None

**Assertions:**
```python
assert response.status_code == 404
assert "not available" in response.json()['error'].lower()
```

**Environment:** Dev without metadata

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_get_live_metadata_missing`
**Test File:** `tests/integration/api/test_info_endpoints.py` (NEW FILE)

---

### **TC-NEW-007: POST /recordings_in_time_range**

**Summary:** API – POST /recordings_in_time_range – Returns Recording Windows

**Objective:** Validate endpoint returns recordings that intersect time range.

**Priority:** High

**Components/Labels:** focus-server, api, history, recordings

**Requirements:** FOCUS-API-RECORDINGS

**Pre-Conditions:**
- PC-010: MongoDB accessible
- PC-011: Recordings exist

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
| 2 | Validate format | Response | List of [start, end] |
| 3 | Check overlap | Each recording | Overlaps request |
| 4 | Validate timestamps | Values | Valid epochs |
| 5 | Check ordering | List | Sorted by start |
| 6 | Test empty range | Future time | Empty list |

**Expected Result (overall):**
- Correct recordings returned
- Proper overlap
- Sorted results

**Post-Conditions:**
None

**Assertions:**
```python
assert response.status_code == 200
assert isinstance(response.json(), list)
assert all(r[0] < req_end and r[1] > req_start for r in recordings)
```

**Environment:** Staging/Production

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_post_recordings_in_time_range`
**Test File:** `tests/integration/api/test_history_endpoints.py` (NEW FILE)

---

## **SECTION C: Resilience Tests (חסר)**

---

### **TC-NEW-008: MongoDB Outage Resilience**

**Summary:** Integration – MongoDB Outage Handling

**Objective:** Ensure MongoDB outage fails gracefully without launching jobs.

**Priority:** Critical

**Components/Labels:** focus-server, resilience, mongodb, outage

**Requirements:** FOCUS-RESILIENCE-MONGO

**Pre-Conditions:**
- PC-010: MongoDB can be disabled (K8s access)
- PC-011: Historical payload ready

**Test Data:**
```json
{
  "start_time": 1700000000,
  "end_time": 1700000600,
  ...
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Verify MongoDB healthy | kubectl | Running |
| 2 | Scale MongoDB to 0 | kubectl scale | Stopped |
| 3 | Verify unreachable | Connection test | Refused |
| 4 | POST /config/{task_id} | Historical | HTTP 503 |
| 5 | Check error | Response | "MongoDB unavailable" |
| 6 | Verify no K8s job | kubectl | No new jobs |
| 7 | Check server | Logs | Still running |
| 8 | Restore MongoDB | kubectl scale | Restored |
| 9 | POST /config again | Same | HTTP 200 |

**Expected Result (overall):**
- Clean 503 during outage
- No resource leaks
- Automatic recovery

**Post-Conditions:**
- MongoDB restored

**Assertions:**
```python
assert outage_response.status_code == 503
assert "mongo" in error.lower()
assert not kubernetes.new_jobs_created()
assert recovery_response.status_code == 200
```

**Environment:** Staging (K8s required)

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_mongodb_outage_resilience`
**Test File:** `tests/integration/infrastructure/test_resilience.py` (NEW FILE)

---

### **TC-NEW-009: RabbitMQ Outage Resilience**

**Summary:** Integration – RabbitMQ Outage Handling

**Objective:** Validate graceful failure when RabbitMQ unavailable.

**Priority:** Critical

**Components/Labels:** focus-server, resilience, rabbitmq, outage

**Requirements:** FOCUS-RESILIENCE-RABBIT

**Pre-Conditions:**
- PC-020: RabbitMQ can be blocked
- PC-021: Live payload ready

**Test Data:**
```json
{
  "start_time": null,
  "end_time": null,
  "view_type": 0,
  ...
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Verify RabbitMQ healthy | Connection test | Connected |
| 2 | Block RabbitMQ | Network/credentials | Blocked |
| 3 | POST /config/{task_id} | Live | HTTP 503 or 502 |
| 4 | Check error | Response | "RabbitMQ unavailable" |
| 5 | Verify no resources | kubectl | No Job/Service |
| 6 | Check logs | Server | Error logged |
| 7 | Restore RabbitMQ | Unblock | Restored |
| 8 | POST /config again | Same | HTTP 200 |

**Expected Result (overall):**
- Proper 5xx during outage
- No resource allocation
- Quick recovery

**Post-Conditions:**
- RabbitMQ restored

**Assertions:**
```python
assert outage_response.status_code in [502, 503]
assert "rabbit" in error.lower()
assert not kubernetes.job_created()
assert recovery_response.status_code == 200
```

**Environment:** Staging

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_rabbitmq_outage_resilience`
**Test File:** `tests/integration/infrastructure/test_resilience.py` (NEW FILE)

---

## **SECTION D: Security Tests (חסר)**

---

### **TC-NEW-010: Malformed Input Security**

**Summary:** Security – Malformed Input Handling

**Objective:** Validate input hardening against malformed/injection attempts.

**Priority:** Critical

**Components/Labels:** focus-server, security, input-validation

**Requirements:** FOCUS-SEC-ROBUSTNESS

**Pre-Conditions:**
- PC-001: Security logging enabled

**Test Data:**
```
1. Malformed JSON: {"invalid": unclosed
2. SQL Injection: ?id='1' OR '1'='1
3. XSS: <script>alert('xss')</script>
4. XXE: <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
5. Oversized: 10MB JSON
6. Null bytes: \u0000
7. Path traversal: ../../etc/passwd
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST malformed JSON | Broken JSON | HTTP 400 |
| 2 | GET with SQLi | Injection param | Sanitized |
| 3 | POST XSS | Script tags | Rejected |
| 4 | POST XXE | Entity payload | Rejected |
| 5 | POST oversized | 10MB | HTTP 413 or handled |
| 6 | POST null bytes | \u0000 | Sanitized |
| 7 | Path traversal | ../.. | Blocked |
| 8 | Check logs | Security log | All logged |
| 9 | Verify server | Status | Running |

**Expected Result (overall):**
- All attacks blocked
- No 500 errors
- Security logged
- Server stable

**Post-Conditions:**
None

**Assertions:**
```python
assert all(r.status_code != 500 for r in attacks)
assert malformed.status_code == 400
assert security_log.contains_all_attempts()
assert server.is_running()
```

**Environment:** Staging

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_security_malformed_inputs`
**Test File:** `tests/integration/security/test_input_security.py` (NEW FILE)

---

## **SECTION E: Performance Tests (חסר)**

---

### **TC-NEW-011: Configuration Endpoint Latency**

**Summary:** Performance – /config/{task_id} Latency P95

**Objective:** Ensure configuration endpoint meets SLA (p95 < 2 seconds).

**Priority:** Medium

**Components/Labels:** focus-server, performance, latency

**Requirements:** FOCUS-PERF-CONFIG

**Pre-Conditions:**
- PC-001: Minimal load environment

**Test Data:**
- Standard live payload
- 100 sequential requests

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Warm up | 5 requests | System ready |
| 2 | Send 100 requests | Sequential | All succeed |
| 3 | Record times | Each request | Times logged |
| 4 | Calculate p95 | All times | Compute percentile |
| 5 | Validate SLA | p95 value | < 2.0 seconds |
| 6 | Check memory | During test | No leaks |
| 7 | Check CPU | Average | < 80% |

**Expected Result (overall):**
- p95 < 2.0 seconds
- p99 < 5.0 seconds
- No memory leaks
- Stable performance

**Post-Conditions:**
- Cleanup test tasks

**Assertions:**
```python
assert percentile(times, 95) < 2.0
assert percentile(times, 99) < 5.0
assert max(times) < 10.0
assert memory_leak < 100_000_000  # 100MB
```

**Environment:** Staging (non-loaded)

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_config_latency_p95`
**Test File:** `tests/integration/performance/test_latency.py` (NEW FILE)

---

# 📊 סיכום

## **טסטים לתיקון (3):**
1. ✅ TC-FIX-001: PZ-13547 - Live Configure - עדכן endpoint ל-`/config/{task_id}`
2. ✅ TC-FIX-002: PZ-13548 - Historical Configure - עדכן endpoint ל-`/config/{task_id}`
3. ✅ TC-FIX-003: PZ-13563 - Metadata - הוסף valid case

## **טסטים חדשים להוספה (11):**

### **Validation (3):**
- TC-NEW-001: Invalid Time Range
- TC-NEW-002: Invalid Channels
- TC-NEW-003: Invalid Frequency

### **Info Endpoints (4):**
- TC-NEW-004: GET /channels
- TC-NEW-005: GET /live_metadata (present)
- TC-NEW-006: GET /live_metadata (missing)
- TC-NEW-007: POST /recordings_in_time_range

### **Resilience (2):**
- TC-NEW-008: MongoDB Outage
- TC-NEW-009: RabbitMQ Outage

### **Security (1):**
- TC-NEW-010: Malformed Inputs

### **Performance (1):**
- TC-NEW-011: Latency P95

---

## **קבצים חדשים לייצר:**
1. `tests/integration/api/test_config_validation.py` ← 3 validation tests
2. `tests/integration/api/test_info_endpoints.py` ← 4 info endpoint tests
3. `tests/integration/api/test_history_endpoints.py` ← 1 recordings test
4. `tests/integration/infrastructure/test_resilience.py` ← 2 outage tests
5. `tests/integration/security/test_input_security.py` ← 1 security test
6. `tests/integration/performance/test_latency.py` ← 1 performance test

---

**כל הטסטים מוכנים להעתקה ישירה ל-Xray!** 🎯
