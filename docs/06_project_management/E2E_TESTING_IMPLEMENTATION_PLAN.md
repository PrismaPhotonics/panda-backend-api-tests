# Focus Server E2E Testing - Complete Implementation Plan
## תוכנית מפורטת להוספת בדיקות E2E מלאות של Focus Server כקומפוננטה

**Created:** 2025-11-04  
**Requested by:** עודד  
**Status:** Implementation Plan Ready

---

## 🎯 Executive Summary

תוכנית זו מפרטת את כל הבדיקות E2E המלאות שצריך להוסיף כדי לבדוק את Focus Server כקומפוננטה שלמה, כולל:
- בדיקות E2E מלאות עם Panda UI
- בדיקות E2E של Lifecycle מלא
- בדיקות E2E של Error Scenarios & Recovery
- בדיקות E2E של Performance
- בדיקות E2E של Data Flow מלא

**Total Story Points:** ~45 SP  
**Estimated Duration:** 3-4 sprints (6-8 weeks)  
**Priority:** High

---

## 📊 Overview

### Current State
- ✅ API-Level E2E Tests (מוגבלות)
- ✅ Integration Tests (לא כולל קליינט)
- ✅ תכנון לבדיקות Panda UI E2E (בתהליך)

### Target State
- ✅ Full E2E Tests עם Panda UI
- ✅ Complete Lifecycle E2E Tests
- ✅ Error Recovery E2E Tests
- ✅ Performance E2E Tests
- ✅ Data Flow E2E Tests

---

## 🎯 Phase 1: Full Lifecycle E2E Tests

### Story 1.1: Complete Lifecycle E2E Tests

**Story Points:** 8  
**Priority:** High  
**Labels:** `backend`, `e2e`, `lifecycle`, `automation`, `high-priority`

**Goal:** בדיקות E2E שמכסות את כל ה-lifecycle של Focus Server: Startup → Configuration → Processing → Streaming → Cleanup

#### Task 1.1.1: Startup & Initialization E2E Test

**Story Points:** 2  
**Estimate:** 3 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של startup ו-initialization של Focus Server כקומפוננטה.

## 📝 Steps
1. Verify K8s pod starts successfully
2. Verify MongoDB connection established
3. Verify RabbitMQ connection established
4. Verify Focus Server API is ready
5. Verify health check endpoint responds
6. Verify all services are healthy

## ✅ Acceptance Criteria
- [ ] K8s pod starts successfully
- [ ] MongoDB connection established
- [ ] RabbitMQ connection established
- [ ] Focus Server API ready
- [ ] Health check passes
- [ ] All services healthy
```

**Test File:** `tests/integration/e2e/test_complete_lifecycle_startup.py`

---

#### Task 1.1.2: Configuration to Processing E2E Test

**Story Points:** 2  
**Estimate:** 4 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של Configuration → Processing flow.

## 📝 Steps
1. User configures job via Panda UI
2. Panda UI sends request to Focus Server API
3. Focus Server validates configuration
4. Focus Server creates job in K8s
5. Focus Server queries MongoDB for data
6. Focus Server starts processing
7. Verify job is running
8. Verify data is being processed

## ✅ Acceptance Criteria
- [ ] Configuration accepted
- [ ] Job created successfully
- [ ] MongoDB queried correctly
- [ ] Processing started
- [ ] Job running correctly
```

**Test File:** `tests/integration/e2e/test_complete_lifecycle_config_to_processing.py`

---

#### Task 1.1.3: Processing to Streaming E2E Test

**Story Points:** 2  
**Estimate:** 4 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של Processing → Streaming flow.

## 📝 Steps
1. Job is processing data
2. Focus Server prepares gRPC stream
3. gRPC stream starts
4. Data flows from Focus Server to client
5. Verify stream is active
6. Verify data is streaming correctly
7. Verify stream quality

## ✅ Acceptance Criteria
- [ ] Processing completes
- [ ] gRPC stream starts
- [ ] Data flows correctly
- [ ] Stream is active
- [ ] Data quality maintained
```

**Test File:** `tests/integration/e2e/test_complete_lifecycle_processing_to_streaming.py`

---

#### Task 1.1.4: Cleanup & Resource Management E2E Test

**Story Points:** 2  
**Estimate:** 3 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של Cleanup ו-Resource Management.

## 📝 Steps
1. Job completes or is cancelled
2. Focus Server stops streaming
3. Focus Server cleans up resources
4. K8s job is terminated
5. Resources are released
6. Verify no resource leaks
7. Verify cleanup is complete

## ✅ Acceptance Criteria
- [ ] Job cleanup successful
- [ ] Resources released
- [ ] No resource leaks
- [ ] K8s job terminated
- [ ] Cleanup complete
```

**Test File:** `tests/integration/e2e/test_complete_lifecycle_cleanup.py`

---

### Story 1.2: Multi-Component E2E Tests

**Story Points:** 6  
**Priority:** High  
**Labels:** `backend`, `e2e`, `multi-component`, `automation`, `high-priority`

**Goal:** בדיקות E2E שמכסות את כל ה-components יחד: MongoDB + RabbitMQ + Kubernetes + Focus Server + gRPC

#### Task 1.2.1: MongoDB Integration E2E Test

**Story Points:** 2  
**Estimate:** 3 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של אינטגרציה עם MongoDB.

## 📝 Steps
1. Verify MongoDB connection
2. Query MongoDB for historic data
3. Verify data retrieval
4. Verify data quality
5. Verify MongoDB performance
6. Verify error handling

## ✅ Acceptance Criteria
- [ ] MongoDB connection works
- [ ] Data retrieval successful
- [ ] Data quality verified
- [ ] Performance acceptable
- [ ] Error handling works
```

**Test File:** `tests/integration/e2e/test_multicomponent_mongodb.py`

---

#### Task 1.2.2: RabbitMQ Integration E2E Test

**Story Points:** 2  
**Estimate:** 3 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של אינטגרציה עם RabbitMQ.

## 📝 Steps
1. Verify RabbitMQ connection
2. Send ROI adjustment command
3. Verify command received
4. Verify command processed
5. Verify response sent
6. Verify error handling

## ✅ Acceptance Criteria
- [ ] RabbitMQ connection works
- [ ] Commands sent successfully
- [ ] Commands processed correctly
- [ ] Responses received
- [ ] Error handling works
```

**Test File:** `tests/integration/e2e/test_multicomponent_rabbitmq.py`

---

#### Task 1.2.3: Kubernetes Integration E2E Test

**Story Points:** 2  
**Estimate:** 4 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של אינטגרציה עם Kubernetes.

## 📝 Steps
1. Verify K8s job creation
2. Verify pod lifecycle
3. Verify resource allocation
4. Verify port exposure
5. Verify job termination
6. Verify cleanup

## ✅ Acceptance Criteria
- [ ] K8s job created successfully
- [ ] Pod lifecycle managed correctly
- [ ] Resources allocated correctly
- [ ] Ports exposed correctly
- [ ] Job terminated correctly
- [ ] Cleanup complete
```

**Test File:** `tests/integration/e2e/test_multicomponent_kubernetes.py`

---

## 🎯 Phase 2: Error Recovery E2E Tests

### Story 2.1: Error Scenarios E2E Tests

**Story Points:** 6  
**Priority:** High  
**Labels:** `backend`, `e2e`, `error-handling`, `automation`, `high-priority`

**Goal:** בדיקות E2E של error scenarios ו-recovery

#### Task 2.1.1: MongoDB Failure Recovery E2E Test

**Story Points:** 2  
**Estimate:** 4 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של MongoDB failure ו-recovery.

## 📝 Steps
1. Start job successfully
2. Stop MongoDB during job
3. Verify error handling
4. Verify error message displayed
5. Restart MongoDB
5. Verify recovery
6. Verify job can continue or retry

## ✅ Acceptance Criteria
- [ ] Error detected correctly
- [ ] Error message displayed
- [ ] Recovery works
- [ ] Job can retry
- [ ] No data loss
```

**Test File:** `tests/integration/e2e/test_error_recovery_mongodb.py`

---

#### Task 2.1.2: RabbitMQ Failure Recovery E2E Test

**Story Points:** 2  
**Estimate:** 3 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של RabbitMQ failure ו-recovery.

## 📝 Steps
1. Start job successfully
2. Stop RabbitMQ during job
3. Verify error handling
4. Verify error message displayed
5. Restart RabbitMQ
6. Verify recovery
7. Verify commands work again

## ✅ Acceptance Criteria
- [ ] Error detected correctly
- [ ] Error message displayed
- [ ] Recovery works
- [ ] Commands work again
- [ ] No data loss
```

**Test File:** `tests/integration/e2e/test_error_recovery_rabbitmq.py`

---

#### Task 2.1.3: Kubernetes Pod Failure Recovery E2E Test

**Story Points:** 2  
**Estimate:** 4 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של K8s pod failure ו-recovery.

## 📝 Steps
1. Start job successfully
2. Kill K8s pod during job
3. Verify error handling
4. Verify error message displayed
5. Verify pod restarts
6. Verify recovery
7. Verify job can continue or retry

## ✅ Acceptance Criteria
- [ ] Error detected correctly
- [ ] Error message displayed
- [ ] Pod restarts correctly
- [ ] Recovery works
- [ ] Job can retry
```

**Test File:** `tests/integration/e2e/test_error_recovery_kubernetes.py`

---

## 🎯 Phase 3: Performance E2E Tests

### Story 3.1: Performance & Load E2E Tests

**Story Points:** 8  
**Priority:** Medium  
**Labels:** `backend`, `e2e`, `performance`, `automation`, `medium-priority`

**Goal:** בדיקות E2E של performance תחת עומס

#### Task 3.1.1: Concurrent Jobs Performance E2E Test

**Story Points:** 3  
**Estimate:** 5 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של performance עם 200 concurrent jobs.

## 📝 Steps
1. Start 200 concurrent jobs
2. Monitor system performance
3. Verify all jobs start successfully
4. Verify data quality maintained
5. Verify no performance degradation
6. Verify all jobs complete successfully
7. Verify resource usage acceptable

## ✅ Acceptance Criteria
- [ ] All 200 jobs start successfully
- [ ] Performance maintained
- [ ] Data quality maintained
- [ ] No degradation
- [ ] All jobs complete
- [ ] Resource usage acceptable
```

**Test File:** `tests/integration/e2e/test_performance_concurrent_jobs.py`

---

#### Task 3.1.2: Latency Measurement E2E Test

**Story Points:** 2  
**Estimate:** 3 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של latency end-to-end.

## 📝 Steps
1. Measure latency: User Action → Data Display
2. Measure latency: Configuration → Job Start
3. Measure latency: Data Processing → Stream Start
4. Measure latency: Stream Start → Data Display
5. Verify latency meets requirements (<5s)
6. Verify latency is consistent

## ✅ Acceptance Criteria
- [ ] Latency measured correctly
- [ ] Latency <5s for all operations
- [ ] Latency consistent
- [ ] Performance acceptable
```

**Test File:** `tests/integration/e2e/test_performance_latency.py`

---

#### Task 3.1.3: Capacity & Stress E2E Test

**Story Points:** 3  
**Estimate:** 4 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של capacity ו-stress.

## 📝 Steps
1. Start jobs up to capacity limit
2. Verify system handles capacity
3. Try to exceed capacity
4. Verify error handling
5. Verify system recovers
6. Verify no data loss
7. Verify performance maintained

## ✅ Acceptance Criteria
- [ ] Capacity limit respected
- [ ] Error handling works
- [ ] System recovers
- [ ] No data loss
- [ ] Performance maintained
```

**Test File:** `tests/integration/e2e/test_performance_capacity.py`

---

## 🎯 Phase 4: Data Flow E2E Tests

### Story 4.1: Complete Data Flow E2E Tests

**Story Points:** 6  
**Priority:** High  
**Labels:** `backend`, `e2e`, `data-flow`, `automation`, `high-priority`

**Goal:** בדיקות E2E שמכסות את כל ה-data flow: MongoDB → Focus Server → gRPC → Client → Display

#### Task 4.1.1: Historic Data Flow E2E Test

**Story Points:** 2  
**Estimate:** 4 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של historic data flow מלא.

## 📝 Steps
1. Data exists in MongoDB (historic recording)
2. User requests historic playback (Panda UI)
3. Focus Server queries MongoDB
4. Focus Server processes data
5. Focus Server streams via gRPC
6. Client receives data
7. Data displayed correctly (Panda UI)
8. Verify data matches MongoDB source
9. Verify data quality maintained

## ✅ Acceptance Criteria
- [ ] Data retrieved from MongoDB
- [ ] Data processed correctly
- [ ] Data streamed via gRPC
- [ ] Data displayed correctly
- [ ] Data matches source
- [ ] Data quality maintained
```

**Test File:** `tests/integration/e2e/test_data_flow_historic.py`

---

#### Task 4.1.2: Live Data Flow E2E Test

**Story Points:** 2  
**Estimate:** 4 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של live data flow מלא.

## 📝 Steps
1. User starts live monitoring (Panda UI)
2. Focus Server connects to live sensors
3. Focus Server processes live data
4. Focus Server streams via gRPC
5. Client receives live data
6. Data displayed correctly (Panda UI)
7. Verify data is live and current
8. Verify data quality maintained

## ✅ Acceptance Criteria
- [ ] Live sensors connected
- [ ] Live data processed
- [ ] Live data streamed
- [ ] Live data displayed
- [ ] Data is current
- [ ] Data quality maintained
```

**Test File:** `tests/integration/e2e/test_data_flow_live.py`

---

#### Task 4.1.3: Data Consistency E2E Test

**Story Points:** 2  
**Estimate:** 3 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E של data consistency end-to-end.

## 📝 Steps
1. Start job with specific configuration
2. Verify data consistency across all components
3. Verify MongoDB data matches streamed data
4. Verify displayed data matches streamed data
5. Verify no data corruption
6. Verify data integrity maintained

## ✅ Acceptance Criteria
- [ ] Data consistent across components
- [ ] MongoDB data matches streamed data
- [ ] Displayed data matches streamed data
- [ ] No data corruption
- [ ] Data integrity maintained
```

**Test File:** `tests/integration/e2e/test_data_flow_consistency.py`

---

## 🎯 Phase 5: Panda UI Integration E2E Tests

### Story 5.1: Panda UI Full Integration E2E Tests

**Story Points:** 8  
**Priority:** High  
**Labels:** `frontend`, `e2e`, `panda-ui`, `automation`, `high-priority`

**Goal:** בדיקות E2E מלאות עם Panda UI שכוללות את כל ה-flow

**Note:** חלק מהבדיקות כבר בתכנון (PZ-13951, PZ-13952, PZ-13953), אבל צריך להוסיף בדיקות שמכסות את כל ה-lifecycle

#### Task 5.1.1: Live Mode Full Flow E2E Test

**Story Points:** 2  
**Estimate:** 4 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E מלאה של Live Mode עם Panda UI.

## 📝 Steps
1. User opens Panda UI
2. User configures live mode
3. User clicks "Start Streaming"
4. Panda UI → Focus Server API
5. Focus Server → MongoDB → Processing → gRPC
6. gRPC → Panda UI → Display
7. User sees live spectrogram
8. Verify all components work together
9. Verify data flow is correct

## ✅ Acceptance Criteria
- [ ] Panda UI works correctly
- [ ] Focus Server API works
- [ ] MongoDB integration works
- [ ] gRPC streaming works
- [ ] Data displayed correctly
- [ ] All components integrated
```

**Test File:** `tests/integration/e2e/test_panda_ui_live_mode_full_flow.py`

**Related:** PZ-13951 (Live Mode E2E Tests)

---

#### Task 5.1.2: Historic Mode Full Flow E2E Test

**Story Points:** 2  
**Estimate:** 4 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E מלאה של Historic Mode עם Panda UI.

## 📝 Steps
1. User opens Panda UI
2. User configures historic mode
3. User selects time range
4. User clicks "Start Playback"
5. Panda UI → Focus Server API
6. Focus Server → MongoDB → Processing → gRPC
7. gRPC → Panda UI → Display
8. User sees historic spectrogram
9. Verify playback controls work
10. Verify all components work together

## ✅ Acceptance Criteria
- [ ] Panda UI works correctly
- [ ] Focus Server API works
- [ ] MongoDB integration works
- [ ] gRPC streaming works
- [ ] Playback controls work
- [ ] Data displayed correctly
```

**Test File:** `tests/integration/e2e/test_panda_ui_historic_mode_full_flow.py`

**Related:** PZ-13952 (Historic Mode E2E Tests)

---

#### Task 5.1.3: Error Handling Full Flow E2E Test

**Story Points:** 2  
**Estimate:** 4 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E מלאה של Error Handling עם Panda UI.

## 📝 Steps
1. User starts job via Panda UI
2. Simulate error (MongoDB down, etc.)
3. Verify error detected
4. Verify error message displayed in Panda UI
5. Verify user can retry
6. Verify recovery works
7. Verify job succeeds after retry

## ✅ Acceptance Criteria
- [ ] Errors detected correctly
- [ ] Error messages displayed
- [ ] User can retry
- [ ] Recovery works
- [ ] Job succeeds after retry
```

**Test File:** `tests/integration/e2e/test_panda_ui_error_handling_full_flow.py`

**Related:** PZ-13953 (Error Handling E2E Tests)

---

#### Task 5.1.4: View Switching Full Flow E2E Test

**Story Points:** 2  
**Estimate:** 3 hours

**Description:**
```
## 🎯 Goal
בדיקת E2E מלאה של View Switching עם Panda UI.

## 📝 Steps
1. User starts job with MultiChannel view
2. User switches to SingleChannel view
3. User switches to Waterfall view
4. Verify each view displays correctly
5. Verify data continues streaming
6. Verify no data loss during switches

## ✅ Acceptance Criteria
- [ ] View switching works
- [ ] Each view displays correctly
- [ ] Data continues streaming
- [ ] No data loss
- [ ] Performance maintained
```

**Test File:** `tests/integration/e2e/test_panda_ui_view_switching_full_flow.py`

---

## 📊 Summary Table

| Phase | Story | Tasks | Story Points | Priority | Duration |
|-------|-------|-------|--------------|----------|----------|
| **1** | Complete Lifecycle E2E | 4 | 8 | High | 2 weeks |
| **1** | Multi-Component E2E | 3 | 6 | High | 1.5 weeks |
| **2** | Error Recovery E2E | 3 | 6 | High | 1.5 weeks |
| **3** | Performance E2E | 3 | 8 | Medium | 2 weeks |
| **4** | Data Flow E2E | 3 | 6 | High | 1.5 weeks |
| **5** | Panda UI Integration E2E | 4 | 8 | High | 2 weeks |
| **Total** | | **20** | **42** | | **10.5 weeks** |

---

## 📅 Implementation Roadmap

### Sprint 73-74 (Weeks 1-2)
- Phase 1: Complete Lifecycle E2E Tests (8 SP)
- Phase 1: Multi-Component E2E Tests (6 SP)
- **Total:** 14 SP

### Sprint 75-76 (Weeks 3-4)
- Phase 2: Error Recovery E2E Tests (6 SP)
- Phase 4: Data Flow E2E Tests (6 SP)
- **Total:** 12 SP

### Sprint 77-78 (Weeks 5-6)
- Phase 5: Panda UI Integration E2E Tests (8 SP)
- **Total:** 8 SP

### Sprint 79-80 (Weeks 7-8)
- Phase 3: Performance E2E Tests (8 SP)
- **Total:** 8 SP

**Total Duration:** 8 weeks (4 sprints)

---

## 📋 Test Files Structure

```
tests/integration/e2e/
├── test_complete_lifecycle_startup.py
├── test_complete_lifecycle_config_to_processing.py
├── test_complete_lifecycle_processing_to_streaming.py
├── test_complete_lifecycle_cleanup.py
├── test_multicomponent_mongodb.py
├── test_multicomponent_rabbitmq.py
├── test_multicomponent_kubernetes.py
├── test_error_recovery_mongodb.py
├── test_error_recovery_rabbitmq.py
├── test_error_recovery_kubernetes.py
├── test_performance_concurrent_jobs.py
├── test_performance_latency.py
├── test_performance_capacity.py
├── test_data_flow_historic.py
├── test_data_flow_live.py
├── test_data_flow_consistency.py
├── test_panda_ui_live_mode_full_flow.py
├── test_panda_ui_historic_mode_full_flow.py
├── test_panda_ui_error_handling_full_flow.py
└── test_panda_ui_view_switching_full_flow.py
```

---

## ✅ Success Criteria

### Phase 1: Complete Lifecycle E2E
- [ ] All lifecycle tests implemented
- [ ] All multi-component tests implemented
- [ ] All tests passing
- [ ] Documentation complete

### Phase 2: Error Recovery E2E
- [ ] All error recovery tests implemented
- [ ] All tests passing
- [ ] Error scenarios covered
- [ ] Recovery scenarios verified

### Phase 3: Performance E2E
- [ ] All performance tests implemented
- [ ] All tests passing
- [ ] Performance requirements met
- [ ] Capacity validated

### Phase 4: Data Flow E2E
- [ ] All data flow tests implemented
- [ ] All tests passing
- [ ] Data consistency verified
- [ ] Data quality maintained

### Phase 5: Panda UI Integration E2E
- [ ] All Panda UI integration tests implemented
- [ ] All tests passing
- [ ] Full flow verified
- [ ] User experience validated

---

## 🔗 Dependencies

### Required Infrastructure
- ✅ Playwright E2E Framework Setup (PZ-XXXX)
- ✅ Page Objects implemented
- ✅ Helpers implemented
- ✅ Focus Server API client ready
- ✅ MongoDB client ready
- ✅ RabbitMQ client ready
- ✅ Kubernetes client ready

### Related Tickets
- PZ-13951: Live Mode E2E Tests
- PZ-13952: Historic Mode E2E Tests
- PZ-13953: Error Handling E2E Tests
- PZ-13949: gRPC Stream Validation Framework

---

## 📝 Next Steps

1. **Create Epic** for Complete E2E Testing
2. **Create Stories** for each Phase
3. **Create Tasks** for each test
4. **Assign to Sprints** according to roadmap
5. **Start Implementation** with Phase 1

---

**Last Updated:** 2025-11-04  
**Created by:** QA Team Lead  
**Status:** Implementation Plan Ready

