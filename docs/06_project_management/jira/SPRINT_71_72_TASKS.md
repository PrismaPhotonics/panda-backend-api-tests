# Sprint 71 & 72 Tasks
## Jira Tickets for gRPC and Historic Mode E2E

**Created:** 2025-11-04  
**Based on:** PZ-13949, PZ-13952  
**Sprint 71:** gRPC Stream Validation Framework (Start) + Historic Mode E2E (Continue)  
**Sprint 72:** gRPC Stream Validation Framework (Complete)

---

## 📊 Summary

| Ticket | Title | Story Points | Sprint | Priority |
|--------|-------|--------------|--------|----------|
| **PZ-13949** | gRPC Stream Validation Framework | 6 | 71-72 | Medium |
| **PZ-13952** | Historic Mode E2E Tests | 2 | 71 | Medium |
| **Total** | | **8** | | |

---

## 🎯 Sprint 71 Tasks

### PZ-13949: gRPC Stream Validation Framework (Part 1)

**Sprint:** Sprint 71  
**Story Points:** 2  
**Priority:** Medium  
**Labels:** `backend`, `grpc`, `automation`, `integration`, `medium-priority`

#### Task 1.1: Setup gRPC Testing Infrastructure

**Type:** Task  
**Estimate:** 2 hours  
**Assignee:** [Team Lead - Backend Automation]

**Description:**

Setup gRPC testing infrastructure for stream validation tests.

**Steps:**
1. Create `tests/integration/grpc/` directory structure
2. Add gRPC dependencies to `requirements.txt`:
   - `grpcio==1.60.0`
   - `grpcio-tools==1.60.0`
3. Create `tests/integration/grpc/conftest.py` with gRPC fixtures
4. Add basic connection fixture for gRPC server at `10.10.100.100:50051`

**Acceptance Criteria:**
- [ ] Directory `tests/integration/grpc/` exists
- [ ] `requirements.txt` updated with gRPC packages
- [ ] `conftest.py` created with basic fixtures
- [ ] Fixtures can connect to gRPC server
- [ ] All dependencies installed successfully

**Dependencies:** None

---

#### Task 1.2: Implement GrpcStreamClient Wrapper

**Type:** Task  
**Estimate:** 4 hours  
**Assignee:** [Team Lead - Backend Automation]

**Description:**

Create a reusable gRPC client wrapper for stream operations.

**Steps:**
1. Create `tests/integration/grpc/helpers/grpc_client.py`
2. Implement `GrpcStreamClient` class with:
   - `connect()` method
   - `disconnect()` method
   - `stream_spectrogram(job_id)` method
3. Add error handling and retry logic
4. Write docstrings and type hints for all methods
5. Add logging for debugging

**Acceptance Criteria:**
- [ ] `GrpcStreamClient` class implemented
- [ ] Can connect to gRPC server at `10.10.100.100:50051`
- [ ] Can stream data with valid job_id
- [ ] Proper error handling for connection failures
- [ ] Type hints and docstrings complete
- [ ] Unit tests for client wrapper (if applicable)

**Dependencies:** Task 1.1 (Setup gRPC Testing Infrastructure)

---

### PZ-13952: Historic Mode E2E Tests (Continue from Sprint 70)

**Sprint:** Sprint 71  
**Story Points:** 2  
**Priority:** Medium  
**Labels:** `frontend`, `e2e`, `automation`, `ui`, `medium-priority`

**Status:** Working (from Sprint 70)  
**Note:** Complete remaining tasks from Sprint 70

#### Task 4.1: Test Historic Mode Without Data

**Type:** Task  
**Estimate:** 2 hours  
**Assignee:** [Ron - Frontend & UI Automation]

**Description:**

Implement test for historic mode when no data is available.

**Steps:**
1. Implement `test_user_configures_historic_playback_no_data`:
   - Select Historic mode in UI
   - Choose time range with no recordings
   - Click "Start Playback"
   - Verify clear error message displayed
   - Verify UI doesn't crash or hang

**Acceptance Criteria:**
- [ ] Test handles no-data scenario correctly
- [ ] Error message is clear and actionable
- [ ] UI remains stable (no crashes or hangs)
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

**Dependencies:** None

---

#### Task 4.2: Test Historic Mode With Data

**Type:** Task  
**Estimate:** 3 hours  
**Assignee:** [Ron - Frontend & UI Automation]

**Description:**

Implement test for historic mode with available data.

**Steps:**
1. Implement `test_user_sees_historic_playback_with_data`:
   - Setup test recording in MongoDB
   - Select Historic mode with data time range
   - Start playback
   - Verify playback controls work
   - Verify playback displays correctly

**Acceptance Criteria:**
- [ ] Test data setup script created
- [ ] Playback starts successfully
- [ ] Playback controls functional
- [ ] Test data properly cleaned up
- [ ] Test passes consistently

**Dependencies:** Task 4.1 (Test Historic Mode Without Data)

---

#### Task 4.3: Test Playback Controls

**Type:** Task  
**Estimate:** 2 hours  
**Assignee:** [Ron - Frontend & UI Automation]

**Description:**

Test playback functionality and controls.

**Steps:**
1. Test pause/resume playback
2. Test seek to different time
3. Test playback speed control (if available)
4. Verify all controls work correctly

**Acceptance Criteria:**
- [ ] Pause/resume works correctly
- [ ] Seek functionality works
- [ ] Playback speed control works (if available)
- [ ] All controls tested and functional
- [ ] Test passes consistently

**Dependencies:** Task 4.2 (Test Historic Mode With Data)

---

## 🎯 Sprint 72 Tasks

### PZ-13949: gRPC Stream Validation Framework (Part 2)

**Sprint:** Sprint 72  
**Story Points:** 4  
**Priority:** Medium  
**Labels:** `backend`, `grpc`, `automation`, `integration`, `medium-priority`

#### Task 1.3: Write Stream Connectivity Tests

**Type:** Task  
**Estimate:** 3 hours  
**Assignee:** [Team Lead - Backend Automation]

**Description:**

Write tests for gRPC stream connectivity.

**Steps:**
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

**Acceptance Criteria:**
- [ ] All 4 connectivity tests implemented
- [ ] Tests pass consistently
- [ ] Tests properly cleanup connections
- [ ] Tests handle timeouts correctly
- [ ] Error scenarios properly tested

**Dependencies:** Task 1.2 (Implement GrpcStreamClient Wrapper)

---

#### Task 1.4: Write Data Validity Tests

**Type:** Task  
**Estimate:** 4 hours  
**Assignee:** [Team Lead - Backend Automation]

**Description:**

Write tests for validating gRPC stream data.

**Steps:**
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

**Acceptance Criteria:**
- [ ] All 4 data validity tests implemented
- [ ] Tests validate frame structure correctly
- [ ] Tests validate data content correctly
- [ ] Tests handle edge cases
- [ ] Tests pass consistently

**Dependencies:** Task 1.3 (Write Stream Connectivity Tests)

---

#### Task 1.5: Write Performance Tests

**Type:** Task  
**Estimate:** 3 hours  
**Assignee:** [Team Lead - Backend Automation]

**Description:**

Write performance tests for gRPC streams.

**Steps:**
1. Implement `test_grpc_stream_continuous_delivery`:
   - Verify stream delivers multiple frames
   - Verify frames arrive continuously
   - Verify no gaps in delivery
2. Implement `test_grpc_stream_performance_metrics`:
   - Measure frame rate (>10 fps)
   - Measure latency between frames
   - Verify performance meets thresholds

**Acceptance Criteria:**
- [ ] Performance tests implemented
- [ ] Frame rate measurement working
- [ ] Tests verify minimum performance thresholds
- [ ] Performance metrics logged
- [ ] Tests pass consistently

**Dependencies:** Task 1.4 (Write Data Validity Tests)

---

#### Task 1.6: Documentation for gRPC Tests

**Type:** Task  
**Estimate:** 2 hours  
**Assignee:** [Team Lead - Backend Automation]

**Description:**

Create documentation for gRPC tests.

**Steps:**
1. Create `tests/integration/grpc/README.md`
2. Document `GrpcStreamClient` usage with examples
3. Add troubleshooting section to documentation
4. Document common issues and solutions
5. Add examples for each test type

**Acceptance Criteria:**
- [ ] README.md created with clear examples
- [ ] Usage patterns documented
- [ ] Common issues and solutions documented
- [ ] Examples included for all test types
- [ ] Documentation is clear and helpful

**Dependencies:** Task 1.5 (Write Performance Tests)

---

## 📅 Sprint Timeline

### Sprint 71 (2 weeks)

**Week 1:**
- Task 1.1: Setup gRPC Testing Infrastructure
- Task 1.2: Implement GrpcStreamClient Wrapper
- Task 4.1: Test Historic Mode Without Data

**Week 2:**
- Task 4.2: Test Historic Mode With Data
- Task 4.3: Test Playback Controls

**Total Story Points:** 4

---

### Sprint 72 (2 weeks)

**Week 1:**
- Task 1.3: Write Stream Connectivity Tests
- Task 1.4: Write Data Validity Tests

**Week 2:**
- Task 1.5: Write Performance Tests
- Task 1.6: Documentation for gRPC Tests

**Total Story Points:** 4

---

## 📊 Summary Table

| Sprint | Ticket | Tasks | Story Points | Priority |
|--------|--------|-------|--------------|----------|
| **71** | PZ-13949 (Part 1) | 2 | 2 | Medium |
| **71** | PZ-13952 | 3 | 2 | Medium |
| **72** | PZ-13949 (Part 2) | 4 | 4 | Medium |
| **Total** | | **9** | **8** | |

---

## 🎯 Ready for Jira Import

All tasks are ready to be created in Jira. Use the following format:

1. **Create Epic/Story** for each ticket (PZ-13949, PZ-13952)
2. **Create Sub-tasks** for each task listed above
3. **Set Sprint** to Sprint 71 or Sprint 72 as indicated
4. **Set Story Points** as shown
5. **Set Labels** as shown
6. **Set Dependencies** as shown

---

**Last Updated:** 2025-11-04  
**Created by:** QA Team Lead  
**Status:** Ready for Sprint Planning

