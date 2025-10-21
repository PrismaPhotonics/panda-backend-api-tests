# 📝 Missing Xray Test Documentation

**Generated:** 2025-10-19  
**Purpose:** Documentation for creating missing tests in Jira Xray

---

## 🔴 **CRITICAL: Missing Test Cases for Jira Xray**

### **Test Case: PZ-NEW-001**
**Summary:** API – POST /configure – Live Mode (Happy Path)

**Objective:** Validate that a valid live configuration creates a job and returns usable gRPC coordinates with correct stream/channel mapping.

**Priority:** High

**Components/Labels:** focus-server, api, live, grpc, configure, mapping

**Requirements:** FOCUS-API-CONFIGURE

**Pre-Conditions:**
- API base URL reachable
- System PRR configured (default 2000)
- FocusManager.channels known

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
| 1 | POST /configure | Live payload | 200 OK with job_id |
| 2 | Validate stream_amount | response.stream_amount | 1 ≤ value ≤ 3 |
| 3 | Validate mapping size | channel_to_stream_index | Size matches channel_amount |
| 4 | Validate stream_url/port | stream_url, stream_port | Valid URL and port > 0 |
| 5 | Validate frequencies | frequencies_list/amount | frequencies_amount == len(frequencies_list) |

**Expected Result (overall):**
Job created with coherent mapping and endpoints ready for gRPC connection.

**Post-Conditions:**
Job cleanup if needed

**Assertions:**
- Status Code: 200
- job_id is not null
- stream_port > 0
- channel_to_stream_index is valid
- view_type matches request

**Environment:** Dev/Staging/Production

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_configure_live_happy_path`
**Test File:** `tests/integration/api/test_configure_endpoints.py`

---

### **Test Case: PZ-NEW-002**
**Summary:** API – POST /configure – Historical Mode (Happy Path)

**Objective:** Validate historical configuration succeeds when requested time range overlaps existing recordings.

**Priority:** High

**Components/Labels:** focus-server, api, history, grpc, storage, mongo

**Requirements:** FOCUS-API-CONFIGURE, FOCUS-API-REC-RANGE

**Pre-Conditions:**
- MongoDB reachable with recordings in requested window
- Storage accessible

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
| 1 | POST /configure | Historical payload | 200 OK with job_id |
| 2 | GET /metadata/{job_id} | job_id | 200 with matching config |
| 3 | POST /recordings_in_time_range | Same time window | List of recordings |
| 4 | Cross-check windows | Returned vs requested | All overlap requested window |

**Expected Result (overall):**
Historical job configured with windows and metadata consistent.

**Post-Conditions:**
Job cleanup

**Assertions:**
- Status Code: 200
- Recordings found in time range
- Metadata matches configuration
- No gaps in coverage

**Environment:** Staging/Production

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_configure_historical_happy_path`
**Test File:** `tests/integration/api/test_configure_endpoints.py`

---

### **Test Case: PZ-NEW-003**
**Summary:** API – POST /configure – Invalid Time Range Validation

**Objective:** Ensure invalid time ranges are rejected with proper error messages.

**Priority:** Medium

**Components/Labels:** focus-server, api, validation, history

**Requirements:** FOCUS-API-VALIDATION

**Pre-Conditions:**
- API reachable

**Test Data:**
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": { "height": 1000 },
  "channels": { "min": 1, "max": 3 },
  "frequencyRange": { "min": 0, "max": 500 },
  "start_time": 1700000600,
  "end_time": 1700000000,
  "view_type": 0
}
```

**Steps:**
| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | start_time > end_time | 400 Bad Request |
| 2 | Check error message | Response body | "Invalid time range" |
| 3 | POST /configure | start_time == end_time | 400 Bad Request |
| 4 | Verify no job created | GET /metadata | No job exists |

**Expected Result (overall):**
Clear 400 errors with no resource allocation.

**Post-Conditions:**
None

**Assertions:**
- Status Code: 400
- Error message contains "Invalid time range"
- No job_id returned
- No side effects

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_configure_invalid_time_range`
**Test File:** `tests/integration/api/test_configure_validation.py`

---

### **Test Case: PZ-NEW-004**
**Summary:** API – POST /configure – Invalid Channel Range

**Objective:** Confirm server blocks illegal channel windows.

**Priority:** Medium

**Components/Labels:** focus-server, api, validation

**Requirements:** FOCUS-API-VALIDATION

**Pre-Conditions:**
- API reachable

**Test Data:**
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": { "height": 1000 },
  "channels": { "min": 300, "max": 100 },
  "frequencyRange": { "min": 0, "max": 500 },
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```

**Steps:**
| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | min > max channels | 400 Bad Request |
| 2 | Check error message | Response body | "Invalid channel range" |
| 3 | POST /configure | Negative channels | 400 Bad Request |
| 4 | POST /configure | Out of bounds | 400 Bad Request |

**Expected Result (overall):**
400 with clear error details, no partial job creation.

**Post-Conditions:**
None

**Assertions:**
- Status Code: 400
- Descriptive error message
- No orchestration triggered

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_configure_invalid_channels`
**Test File:** `tests/integration/api/test_configure_validation.py`

---

### **Test Case: PZ-NEW-005**
**Summary:** API – GET /channels – Returns System Channel Bounds

**Objective:** Validate channel range endpoint returns authoritative bounds.

**Priority:** High

**Components/Labels:** focus-server, api, channels

**Requirements:** FOCUS-API-CHANNELS

**Pre-Conditions:**
- FocusManager.channels configured

**Test Data:**
N/A (GET request)

**Steps:**
| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | GET /channels | None | 200 OK |
| 2 | Validate response schema | JSON response | Contains lowest_channel, highest_channel |
| 3 | Check lowest_channel | Response field | Value == 1 |
| 4 | Check highest_channel | Response field | Matches configuration |

**Expected Result (overall):**
Range reflects server configuration.

**Post-Conditions:**
None

**Assertions:**
- Status Code: 200
- lowest_channel == 1
- highest_channel > 0
- Response is stable across calls

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_channels_endpoint`
**Test File:** `tests/integration/api/test_info_endpoints.py`

---

### **Test Case: PZ-NEW-006**
**Summary:** API – GET /metadata/{job_id} – Valid and Invalid Cases

**Objective:** Validate metadata retrieval for existing jobs and 404 for non-existent.

**Priority:** High

**Components/Labels:** focus-server, api, metadata

**Requirements:** FOCUS-API-JOB-META

**Pre-Conditions:**
- At least one live configure succeeded

**Test Data:**
- Valid job_id from previous configure
- Invalid job_id: "non_existent_job"

**Steps:**
| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Create job via POST /configure | Valid payload | Get job_id |
| 2 | GET /metadata/{job_id} | Valid job_id | 200 with configuration |
| 3 | Validate config match | Response vs original | Exact match |
| 4 | GET /metadata/invalid | "non_existent" | 404 Not Found |

**Expected Result (overall):**
Correct 200/404 behavior with config integrity.

**Post-Conditions:**
Cleanup created job

**Assertions:**
- Valid job: 200 with matching config
- Invalid job: 404 with error message
- No information leakage

**Environment:** Any

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_metadata_endpoint`
**Test File:** `tests/integration/api/test_info_endpoints.py`

---

### **Test Case: PZ-NEW-007**
**Summary:** Integration – MongoDB Outage Resilience

**Objective:** Ensure dependency outage fails fast without launching processing.

**Priority:** High

**Components/Labels:** focus-server, integration, history, mongo, resilience

**Requirements:** FOCUS-API-CONFIGURE

**Pre-Conditions:**
- MongoDB can be disabled/blocked

**Test Data:**
- Valid history payload

**Steps:**
| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Disable MongoDB | Scale replicas=0 | MongoDB unreachable |
| 2 | POST /configure | History payload | 503 Service Unavailable |
| 3 | Check K8s/RabbitMQ | Events/queues | No new resources |
| 4 | Check server logs | Log entries | Dependency error logged |
| 5 | Re-enable MongoDB | Scale replicas=1 | Service restored |

**Expected Result (overall):**
Clean failure with no side effects.

**Post-Conditions:**
MongoDB restored

**Assertions:**
- Status Code: 503
- Clear error message
- No job_id returned
- No orchestration triggered
- Server doesn't crash

**Environment:** Staging (requires K8s access)

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_mongodb_outage_handling`
**Test File:** `tests/integration/infrastructure/test_resilience.py`

---

### **Test Case: PZ-NEW-008**
**Summary:** Integration – RabbitMQ Outage Resilience

**Objective:** Validate graceful upstream failure without launching downstream resources.

**Priority:** High

**Components/Labels:** focus-server, integration, live, rabbit, resilience

**Requirements:** FOCUS-API-CONFIGURE

**Pre-Conditions:**
- RabbitMQ can be blocked

**Test Data:**
- Valid live payload

**Steps:**
| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Block RabbitMQ | Network/credentials | RabbitMQ unreachable |
| 2 | POST /configure | Live payload | 503/502 |
| 3 | Check K8s | Events | No Job/Service created |
| 4 | Check logs | Server logs | Upstream unavailable logged |
| 5 | Restore RabbitMQ | Unblock | Service restored |

**Expected Result (overall):**
Proper 5xx mapping with clear message, no resource leaks.

**Post-Conditions:**
RabbitMQ restored

**Assertions:**
- Status Code: 503 or 502
- Friendly error message
- No job created
- No crash/stacktrace

**Environment:** Staging

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_rabbitmq_outage_handling`
**Test File:** `tests/integration/infrastructure/test_resilience.py`

---

### **Test Case: PZ-NEW-009**
**Summary:** Security – Malformed Input Handling

**Objective:** Validate input hardening against malformed/oversized/injection attempts.

**Priority:** High

**Components/Labels:** focus-server, security, input-validation

**Requirements:** FOCUS-SEC-ROBUSTNESS

**Pre-Conditions:**
- Logging enabled

**Test Data:**
- Malformed JSON: `{"invalid_json": unclosed`
- SQLi attempt: `?search='1' OR '1'='1`
- XSS attempt: `?id=<script>alert('xss')</script>`
- Oversized payload: 10MB JSON

**Steps:**
| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | POST /configure | Malformed JSON | 400 Bad Request |
| 2 | OPTIONS any endpoint | None | CORS headers present |
| 3 | GET with SQLi params | Injection string | No 500, sanitized |
| 4 | POST oversized payload | 10MB JSON | Rejected gracefully |

**Expected Result (overall):**
No 5xx due to malformed inputs, stable behavior.

**Post-Conditions:**
None

**Assertions:**
- No 500 errors for malformed input
- CORS headers present
- Injection attempts sanitized
- Large payloads rejected
- Security events logged

**Environment:** Any (preferably Staging)

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_security_malformed_inputs`
**Test File:** `tests/integration/security/test_input_validation.py`

---

### **Test Case: PZ-NEW-010**
**Summary:** Performance – Configure Endpoint Latency

**Objective:** Ensure /configure response times meet SLA under minimal load.

**Priority:** Low

**Components/Labels:** focus-server, performance, latency

**Requirements:** FOCUS-PERF-CONFIGURE

**Pre-Conditions:**
- Minimal concurrent load

**Test Data:**
- Standard live payload

**Steps:**
| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Send 5 sequential POST /configure | Live payload | All return 200 |
| 2 | Measure response times | Latencies | Record all times |
| 3 | Calculate p95 | Collected times | Compute percentile |
| 4 | Validate against SLA | p95 value | p95 < 2.0 seconds |

**Expected Result (overall):**
SLA met for latency.

**Post-Conditions:**
Cleanup created jobs

**Assertions:**
- All requests succeed
- p95 < 2.0 seconds
- No significant variance
- No memory leaks

**Environment:** Dev/Staging (non-loaded)

**Automation Status:** TO BE AUTOMATED
**Test Function:** `test_configure_latency_p95`
**Test File:** `tests/integration/performance/test_latency.py`

---

## 📊 **Tests Existing in Automation but NOT in Jira**

### **Test Case: AUTOMATION-001**
**Summary:** Basic Infrastructure Connectivity

**Objective:** Validate basic connectivity to all required services.

**Priority:** High

**Components/Labels:** infrastructure, connectivity, smoke

**Requirements:** INFRA-CONNECTIVITY

**Pre-Conditions:**
- Environment configured

**Test Data:**
- Service endpoints from configuration

**Steps:**
| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Test MongoDB connection | Connection string | Connected |
| 2 | Test RabbitMQ connection | AMQP URL | Connected |
| 3 | Test Focus Server health | Base URL | 200 OK |
| 4 | Test Frontend access | Frontend URL | Accessible |

**Expected Result (overall):**
All services reachable and healthy.

**Post-Conditions:**
None

**Assertions:**
- All connections successful
- Response times acceptable
- No authentication errors

**Environment:** Any

**Automation Status:** IMPLEMENTED
**Test Function:** `test_basic_connectivity`
**Test File:** `tests/integration/infrastructure/test_basic_connectivity.py`

---

### **Test Case: AUTOMATION-002**
**Summary:** Spectrogram Processing Pipeline

**Objective:** Validate spectrogram data processing and transformation.

**Priority:** Medium

**Components/Labels:** processing, spectrogram, pipeline

**Requirements:** PROC-SPECTROGRAM

**Pre-Conditions:**
- Processing pipeline available

**Test Data:**
- Sample recording data

**Steps:**
| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Submit data for processing | Raw data | Accepted |
| 2 | Monitor processing status | Job ID | Processing |
| 3 | Retrieve processed data | Job ID | Spectrogram data |
| 4 | Validate data format | Output | Correct format |

**Expected Result (overall):**
Spectrogram correctly processed and formatted.

**Post-Conditions:**
Cleanup test data

**Assertions:**
- Processing completes
- Output format correct
- Data integrity maintained
- Performance acceptable

**Environment:** Dev/Staging

**Automation Status:** IMPLEMENTED
**Test Function:** `test_spectrogram_pipeline`
**Test File:** `tests/integration/api/test_spectrogram_pipeline.py`

---

### **Test Case: AUTOMATION-003**
**Summary:** Dynamic ROI Adjustment

**Objective:** Validate dynamic Region of Interest adjustment functionality.

**Priority:** Medium

**Components/Labels:** roi, dynamic, adjustment

**Requirements:** UI-ROI-DYNAMIC

**Pre-Conditions:**
- ROI feature enabled

**Test Data:**
- Various ROI configurations

**Steps:**
| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Set initial ROI | Coordinates | ROI set |
| 2 | Trigger dynamic adjustment | New parameters | ROI adjusted |
| 3 | Validate new boundaries | Response | Correct boundaries |
| 4 | Test edge cases | Min/max values | Handled correctly |

**Expected Result (overall):**
ROI adjusts correctly to all inputs.

**Post-Conditions:**
Reset to defaults

**Assertions:**
- Adjustments accurate
- Boundaries respected
- No overflow errors
- UI updates correctly

**Environment:** Any

**Automation Status:** IMPLEMENTED
**Test Function:** `test_dynamic_roi_adjustment`
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## 🎯 **Summary**

### **Tests to Create in Jira:**
- 12 existing automation tests need Jira tickets
- Each should follow the template format above

### **Tests to Implement in Automation:**
- 18 Jira tests need implementation
- Priority: Critical (10) → High (5) → Medium (3)

### **Total Coverage After Implementation:**
- 38 total tests (26 from Jira + 12 from automation)
- Full API coverage
- Complete integration testing
- Security and performance validation
