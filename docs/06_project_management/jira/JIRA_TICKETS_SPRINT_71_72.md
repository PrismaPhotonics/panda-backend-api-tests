# Jira Tickets for Sprint 71 & 72
## Ready-to-Import Tickets

**Created:** 2025-11-04  
**Based on:** PZ-13949, PZ-13952  
**Status:** Ready for Jira Import

---

## 📋 How to Use

1. Copy each ticket section below
2. Create new Jira issue
3. Paste content into description
4. Set fields as indicated
5. Link tickets as dependencies

---

## 🎯 Sprint 71 Tickets

### PZ-13949-1: Setup gRPC Testing Infrastructure

**Type:** Sub-task  
**Parent:** PZ-13949  
**Sprint:** Sprint 71  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `backend`, `grpc`, `automation`, `integration`, `medium-priority`  
**Assignee:** [Team Lead - Backend Automation]

**Title:** Setup gRPC Testing Infrastructure

**Description:**
```
## 🎯 Goal
Setup gRPC testing infrastructure for stream validation tests.

## 📝 Steps
1. Create `tests/integration/grpc/` directory structure
2. Add gRPC dependencies to `requirements.txt`:
   - `grpcio==1.60.0`
   - `grpcio-tools==1.60.0`
3. Create `tests/integration/grpc/conftest.py` with gRPC fixtures
4. Add basic connection fixture for gRPC server at `10.10.100.100:50051`

## ✅ Acceptance Criteria
- [ ] Directory `tests/integration/grpc/` exists
- [ ] `requirements.txt` updated with gRPC packages
- [ ] `conftest.py` created with basic fixtures
- [ ] Fixtures can connect to gRPC server
- [ ] All dependencies installed successfully

## 🔗 Dependencies
None

## 📎 Related Files
- `tests/integration/grpc/`
- `requirements.txt`
- `tests/integration/grpc/conftest.py`

## ⏱️ Estimate
2 hours
```

---

### PZ-13949-2: Implement GrpcStreamClient Wrapper

**Type:** Sub-task  
**Parent:** PZ-13949  
**Sprint:** Sprint 71  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `backend`, `grpc`, `automation`, `integration`, `medium-priority`  
**Assignee:** [Team Lead - Backend Automation]

**Title:** Implement GrpcStreamClient Wrapper

**Description:**
```
## 🎯 Goal
Create a reusable gRPC client wrapper for stream operations.

## 📝 Steps
1. Create `tests/integration/grpc/helpers/grpc_client.py`
2. Implement `GrpcStreamClient` class with:
   - `connect()` method
   - `disconnect()` method
   - `stream_spectrogram(job_id)` method
3. Add error handling and retry logic
4. Write docstrings and type hints for all methods
5. Add logging for debugging

## ✅ Acceptance Criteria
- [ ] `GrpcStreamClient` class implemented
- [ ] Can connect to gRPC server at `10.10.100.100:50051`
- [ ] Can stream data with valid job_id
- [ ] Proper error handling for connection failures
- [ ] Type hints and docstrings complete
- [ ] Unit tests for client wrapper (if applicable)

## 🔗 Dependencies
- PZ-13949-1 (Setup gRPC Testing Infrastructure)

## 📎 Related Files
- `tests/integration/grpc/helpers/grpc_client.py`

## ⏱️ Estimate
4 hours
```

---

### PZ-13952-1: Test Historic Mode Without Data

**Type:** Sub-task  
**Parent:** PZ-13952  
**Sprint:** Sprint 71  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `frontend`, `e2e`, `automation`, `ui`, `medium-priority`  
**Assignee:** [Ron - Frontend & UI Automation]

**Title:** Test Historic Mode Without Data

**Description:**
```
## 🎯 Goal
Implement test for historic mode when no data is available.

## 📝 Steps
1. Implement `test_user_configures_historic_playback_no_data`:
   - Select Historic mode in UI
   - Choose time range with no recordings
   - Click "Start Playback"
   - Verify clear error message displayed
   - Verify UI doesn't crash or hang

## ✅ Acceptance Criteria
- [ ] Test handles no-data scenario correctly
- [ ] Error message is clear and actionable
- [ ] UI remains stable (no crashes or hangs)
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
None

## 📎 Related Files
- `tests/integration/e2e/test_historic_playback.py`

## ⏱️ Estimate
2 hours
```

---

### PZ-13952-2: Test Historic Mode With Data

**Type:** Sub-task  
**Parent:** PZ-13952  
**Sprint:** Sprint 71  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `frontend`, `e2e`, `automation`, `ui`, `medium-priority`  
**Assignee:** [Ron - Frontend & UI Automation]

**Title:** Test Historic Mode With Data

**Description:**
```
## 🎯 Goal
Implement test for historic mode with available data.

## 📝 Steps
1. Implement `test_user_sees_historic_playback_with_data`:
   - Setup test recording in MongoDB
   - Select Historic mode with data time range
   - Start playback
   - Verify playback controls work
   - Verify playback displays correctly

## ✅ Acceptance Criteria
- [ ] Test data setup script created
- [ ] Playback starts successfully
- [ ] Playback controls functional
- [ ] Test data properly cleaned up
- [ ] Test passes consistently

## 🔗 Dependencies
- PZ-13952-1 (Test Historic Mode Without Data)

## 📎 Related Files
- `tests/integration/e2e/test_historic_playback.py`
- `scripts/setup_test_recording.py` (if needed)

## ⏱️ Estimate
3 hours
```

---

### PZ-13952-3: Test Playback Controls

**Type:** Sub-task  
**Parent:** PZ-13952  
**Sprint:** Sprint 71  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `frontend`, `e2e`, `automation`, `ui`, `medium-priority`  
**Assignee:** [Ron - Frontend & UI Automation]

**Title:** Test Playback Controls

**Description:**
```
## 🎯 Goal
Test playback functionality and controls.

## 📝 Steps
1. Test pause/resume playback
2. Test seek to different time
3. Test playback speed control (if available)
4. Verify all controls work correctly

## ✅ Acceptance Criteria
- [ ] Pause/resume works correctly
- [ ] Seek functionality works
- [ ] Playback speed control works (if available)
- [ ] All controls tested and functional
- [ ] Test passes consistently

## 🔗 Dependencies
- PZ-13952-2 (Test Historic Mode With Data)

## 📎 Related Files
- `tests/integration/e2e/test_historic_playback.py`

## ⏱️ Estimate
2 hours
```

---

## 🎯 Sprint 72 Tickets

### PZ-13949-3: Write Stream Connectivity Tests

**Type:** Sub-task  
**Parent:** PZ-13949  
**Sprint:** Sprint 72  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `backend`, `grpc`, `automation`, `integration`, `medium-priority`  
**Assignee:** [Team Lead - Backend Automation]

**Title:** Write Stream Connectivity Tests

**Description:**
```
## 🎯 Goal
Write tests for gRPC stream connectivity.

## 📝 Steps
1. Implement `test_grpc_stream_connects_successfully`:
   - Verify connection to gRPC server
   - Verify connection is established within timeout
2. Implement `test_grpc_stream_delivers_first_frame`:
   - Verify first frame received within timeout
   - Verify frame structure is valid
3. Implement `test_grpc_stream_handles_invalid_job_id`:
   - Verify error handling for bad job_id
   - Verify appropriate error message
4. Implement `test_grpc_stream_stops_on_job_completion`:
   - Verify stream ends properly
   - Verify cleanup after stream ends

## ✅ Acceptance Criteria
- [ ] All 4 connectivity tests implemented
- [ ] Tests pass consistently
- [ ] Tests properly cleanup connections
- [ ] Tests handle timeouts correctly
- [ ] Error scenarios properly tested

## 🔗 Dependencies
- PZ-13949-2 (Implement GrpcStreamClient Wrapper)

## 📎 Related Files
- `tests/integration/grpc/test_grpc_stream_connectivity.py`

## ⏱️ Estimate
3 hours
```

---

### PZ-13949-4: Write Data Validity Tests

**Type:** Sub-task  
**Parent:** PZ-13949  
**Sprint:** Sprint 72  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `backend`, `grpc`, `automation`, `integration`, `medium-priority`  
**Assignee:** [Team Lead - Backend Automation]

**Title:** Write Data Validity Tests

**Description:**
```
## 🎯 Goal
Write tests for validating gRPC stream data.

## 📝 Steps
1. Implement `test_grpc_stream_frame_structure_valid`:
   - Verify frame has required fields (job_id, timestamp, data)
   - Verify field types are correct
2. Implement `test_grpc_stream_data_dimensions_correct`:
   - Verify data dimensions match configuration
   - Verify data shape is consistent
3. Implement `test_grpc_stream_frequency_range_correct`:
   - Verify frequency metadata is correct
   - Verify frequency range matches configuration
4. Implement `test_grpc_stream_data_not_all_zeros`:
   - Verify actual data is present (not empty)
   - Verify data contains meaningful values

## ✅ Acceptance Criteria
- [ ] All 4 data validity tests implemented
- [ ] Tests validate frame structure correctly
- [ ] Tests validate data content correctly
- [ ] Tests handle edge cases
- [ ] Tests pass consistently

## 🔗 Dependencies
- PZ-13949-3 (Write Stream Connectivity Tests)

## 📎 Related Files
- `tests/integration/grpc/test_grpc_stream_data_validity.py`

## ⏱️ Estimate
4 hours
```

---

### PZ-13949-5: Write Performance Tests

**Type:** Sub-task  
**Parent:** PZ-13949  
**Sprint:** Sprint 72  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `backend`, `grpc`, `automation`, `integration`, `performance`, `medium-priority`  
**Assignee:** [Team Lead - Backend Automation]

**Title:** Write Performance Tests

**Description:**
```
## 🎯 Goal
Write performance tests for gRPC streams.

## 📝 Steps
1. Implement `test_grpc_stream_continuous_delivery`:
   - Verify stream delivers multiple frames
   - Verify frames arrive continuously
   - Verify no gaps in delivery
2. Implement `test_grpc_stream_performance_metrics`:
   - Measure frame rate (>10 fps)
   - Measure latency between frames
   - Verify performance meets thresholds

## ✅ Acceptance Criteria
- [ ] Performance tests implemented
- [ ] Frame rate measurement working
- [ ] Tests verify minimum performance thresholds
- [ ] Performance metrics logged
- [ ] Tests pass consistently

## 🔗 Dependencies
- PZ-13949-4 (Write Data Validity Tests)

## 📎 Related Files
- `tests/integration/grpc/test_grpc_stream_performance.py`

## ⏱️ Estimate
3 hours
```

---

### PZ-13949-6: Documentation for gRPC Tests

**Type:** Sub-task  
**Parent:** PZ-13949  
**Sprint:** Sprint 72  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `backend`, `grpc`, `documentation`, `medium-priority`  
**Assignee:** [Team Lead - Backend Automation]

**Title:** Documentation for gRPC Tests

**Description:**
```
## 🎯 Goal
Create documentation for gRPC tests.

## 📝 Steps
1. Create `tests/integration/grpc/README.md`
2. Document `GrpcStreamClient` usage with examples
3. Add troubleshooting section to documentation
4. Document common issues and solutions
5. Add examples for each test type

## ✅ Acceptance Criteria
- [ ] README.md created with clear examples
- [ ] Usage patterns documented
- [ ] Common issues and solutions documented
- [ ] Examples included for all test types
- [ ] Documentation is clear and helpful

## 🔗 Dependencies
- PZ-13949-5 (Write Performance Tests)

## 📎 Related Files
- `tests/integration/grpc/README.md`

## ⏱️ Estimate
2 hours
```

---

## 📊 Summary

### Sprint 71
- **Total Tasks:** 5
- **Total Story Points:** 4
- **Tickets:** PZ-13949 (Part 1), PZ-13952

### Sprint 72
- **Total Tasks:** 4
- **Total Story Points:** 4
- **Tickets:** PZ-13949 (Part 2)

### Overall
- **Total Tasks:** 9
- **Total Story Points:** 8
- **Total Tickets:** 2

---

**Last Updated:** 2025-11-04  
**Created by:** QA Team Lead  
**Status:** Ready for Jira Import

