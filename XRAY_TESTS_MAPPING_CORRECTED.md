# 🔄 Xray Tests Mapping - Corrected Analysis

**Date:** 2025-10-19  
**Purpose:** Accurate mapping between Jira Xray tests and existing automation

---

## ✅ **Tests ALREADY in Xray (from CSV):**

### **Confirmed Xray Tests:**

| Jira ID | Test Name | Status in Automation |
|---------|-----------|----------------------|
| PZ-13547 | Live configure (happy path) ✅ | ⚠️ Partial - `test_configure_live_task_success` exists but different endpoint |
| PZ-13548 | Historical configure (happy path) | ⚠️ Partial - `test_configure_historic_task_success` exists |
| PZ-13552 | Invalid time range (negative) | ❌ Missing |
| PZ-13554 | Invalid channels (negative) | ❌ Missing |
| PZ-13555 | Invalid frequency range (negative) | ❌ Missing |
| PZ-13556 | SingleChannel view mapping | ✅ Implemented - `test_configure_singlechannel_mapping` |
| PZ-13557 | Waterfall view handling | ❌ Missing |
| PZ-13558 | Overlap/NFFT Escalation Edge Case | ❌ Missing |
| PZ-13560 | GET /channels | ❌ Missing |
| PZ-13561 | GET /live_metadata present | ❌ Missing |
| PZ-13562 | GET /live_metadata missing | ❌ Missing |
| PZ-13563 | GET /metadata/{job_id} | ⚠️ Partial - `test_metadata_for_invalid_task_id` exists |
| PZ-13564 | POST /recordings_in_time_range | ❌ Missing |
| PZ-13565 | Focus Manager Local Mode | ❌ Missing |
| PZ-13566 | FocusManager K8s Mode | ❌ Missing |
| PZ-13568 | GRPCLauncher K8s | ❌ Missing |
| PZ-13569 | Orchestrator YAML flow | ❌ Missing |
| PZ-13570 | E2E Configure → gRPC | ❌ Missing |
| PZ-13571 | Performance latency p95 | ❌ Missing |
| PZ-13572 | Security malformed inputs | ❌ Missing |
| PZ-13597 | MongoDB collections and schema (duplicate) | ✅ Partial |
| PZ-13598 | MongoDB collections and schema | ✅ Partial - `test_mongodb_data_quality.py` |
| PZ-13599 | Postgres connectivity | ❌ Missing |
| PZ-13600 | Invalid configure no orchestration | ❌ Missing |
| PZ-13601 | History empty window | ❌ Missing |
| PZ-13602 | RabbitMQ outage | ❌ Missing |
| PZ-13603 | MongoDB outage | ❌ Missing |
| PZ-13604 | Orchestrator error triggers rollback | ❌ Missing |
| PZ-13683 | MongoDB Collections Exist | ✅ Implemented |
| PZ-13684 | node4 Schema Validation | ✅ Implemented |
| PZ-13685 | Recordings Metadata Completeness | ✅ Implemented |
| PZ-13686 | MongoDB Indexes Validation | ✅ Implemented |
| PZ-13687 | MongoDB Recovery After Outage | ✅ Implemented |
| PZ-13705 | Historical vs Live Recordings | ✅ Implemented |

---

## 🔍 **Key Findings:**

### **1. Implementation Gaps:**

#### **Tests that EXIST but DON'T MATCH Xray exactly:**

**PZ-13547 (Live Configure):**
- **Xray expects:** POST `/configure` endpoint
- **We have:** POST `/config/{task_id}` endpoint
- **Action needed:** Either update Xray or create new test for `/configure`

**PZ-13548 (Historical Configure):**
- **Xray expects:** POST `/configure` with time range
- **We have:** POST `/config/{task_id}` with historical data
- **Action needed:** Align endpoint usage

**PZ-13563 (Metadata):**
- **Xray expects:** GET `/metadata/{job_id}`
- **We have:** GET `/metadata/{task_id}` for invalid case only
- **Action needed:** Add valid case test

---

## 📝 **What Actually Needs to be Created:**

### **Priority 1: Critical Missing API Tests**
1. ❌ POST `/configure` (live) - correct endpoint
2. ❌ POST `/configure` (historical) - correct endpoint
3. ❌ POST `/configure` with invalid time range
4. ❌ POST `/configure` with invalid channels
5. ❌ POST `/configure` with invalid frequency
6. ❌ GET `/channels`
7. ❌ GET `/live_metadata` (both cases)
8. ❌ GET `/metadata/{job_id}` (valid case)
9. ❌ POST `/recordings_in_time_range`

### **Priority 2: Resilience Tests**
1. ❌ MongoDB outage handling
2. ❌ RabbitMQ outage handling
3. ❌ Invalid configure validation
4. ❌ Empty history window

### **Priority 3: Service & Integration**
1. ❌ Focus Manager (Local & K8s modes)
2. ❌ GRPCLauncher
3. ❌ Orchestrator YAML
4. ❌ E2E flow
5. ❌ Waterfall view

### **Priority 4: Non-Functional**
1. ❌ Performance tests
2. ❌ Security tests
3. ❌ Postgres connectivity

---

## 🎯 **Corrected Action Plan:**

### **Immediate Actions:**

1. **Update existing tests to match Xray:**
   - Modify `test_configure_live_task_success` to use `/configure` endpoint
   - Modify `test_configure_historic_task_success` to use `/configure` endpoint
   - Add valid case for metadata endpoint

2. **Create missing critical tests:**
   - All validation tests (time, channels, frequency)
   - Info endpoints (`/channels`, `/live_metadata`)
   - History endpoint (`/recordings_in_time_range`)

3. **Document tests that exist but aren't in Xray:**
   - All tests in `test_spectrogram_pipeline.py`
   - All tests in `test_dynamic_roi_adjustment.py`
   - All tests in `test_pz_integration.py`
   - All tests in `test_external_connectivity.py`
   - All UI tests

---

## 📊 **Revised Statistics:**

### **Xray Tests (26 unique):**
- ✅ **Fully Implemented:** 8 (31%)
- ⚠️ **Partially Implemented:** 3 (11%)
- ❌ **Not Implemented:** 15 (58%)

### **Automation Tests not in Xray:**
- 12+ tests that need Xray tickets

### **Critical Gaps:**
- Main `/configure` endpoint not tested correctly
- No resilience testing
- No performance testing
- No security testing

---

## 🔧 **Technical Notes:**

### **Endpoint Discrepancies:**
Our automation uses:
- `/config/{task_id}` instead of `/configure`
- `/metadata/{task_id}` instead of `/metadata/{job_id}`
- Different response schemas

**This suggests either:**
1. The API has changed since Xray tests were written
2. We're testing a different version/variant of the API
3. There are multiple APIs that need testing

**Recommendation:** 
- Verify with development team which endpoints are correct
- Update either Xray or automation to match current API
- Consider versioning in test names
