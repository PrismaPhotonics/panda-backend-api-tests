# Focus Server Complete E2E Testing - Full Stories & Sub-tasks
## Ready-to-Import Complete Jira Structure

**Created:** 2025-11-04  
**Status:** Ready for Jira Import  
**Total Stories:** 5  
**Total Sub-tasks:** 20  
**Total Story Points:** 42

---

## 📋 How to Use This Document

1. **Create Epic** using the Epic section below
2. **Create Stories** for each Story section (5 stories)
3. **Create Sub-tasks** for each Sub-task section (20 sub-tasks)
4. **Link** all tickets to Epic
5. **Assign** to Sprints according to roadmap

---

## 🎯 Main Epic

**Type:** Epic  
**Title:** Focus Server Complete E2E Testing  
**Priority:** High  
**Story Points:** 42  
**Labels:** `backend`, `e2e`, `automation`, `focus-server`, `lifecycle`, `high-priority`  
**Sprint:** Sprint 73-80

**Description:**
```
## 🎯 Epic Summary

Complete E2E testing framework for Focus Server as a complete component, including:
- Full lifecycle E2E tests (Startup → Config → Process → Stream → Cleanup)
- Multi-component E2E tests (MongoDB + RabbitMQ + K8s + Focus Server + gRPC)
- Error recovery E2E tests
- Performance E2E tests
- Data flow E2E tests
- Panda UI integration E2E tests

## 📊 Business Value

- Test Focus Server as a complete component, not just API
- Verify end-to-end workflows from user to data display
- Ensure all components work together correctly
- Validate error handling and recovery end-to-end
- Verify performance under load end-to-end
- Ensure data quality maintained throughout the flow

## 🎯 Epic Goals

1. **Complete Lifecycle Coverage**
   - Test entire lifecycle: Startup → Configuration → Processing → Streaming → Cleanup
   - Verify all phases work correctly together

2. **Multi-Component Integration**
   - Test all components together: MongoDB + RabbitMQ + Kubernetes + Focus Server + gRPC
   - Verify integration between components

3. **Error Handling & Recovery**
   - Test error scenarios end-to-end
   - Verify recovery mechanisms work correctly

4. **Performance Validation**
   - Test performance under load end-to-end
   - Verify capacity limits and latency requirements

5. **Data Flow Validation**
   - Test complete data flow: MongoDB → Focus Server → gRPC → Client → Display
   - Verify data consistency and quality

## 📊 Epic Breakdown

**Total Story Points:** 42

**Stories:**
1. Complete Lifecycle E2E Tests (8 SP)
2. Multi-Component E2E Tests (6 SP)
3. Error Recovery E2E Tests (6 SP)
4. Performance E2E Tests (8 SP)
5. Data Flow E2E Tests (6 SP)
6. Panda UI Integration E2E Tests (8 SP)

## 📅 Estimated Timeline

- **Duration:** 8 weeks (4 sprints)
- **Team Size:** 3 members
- **Estimated Velocity:** 10-12 Story Points per sprint
- **Start Sprint:** Sprint 73
- **End Sprint:** Sprint 80

## ✅ Epic Acceptance Criteria

- [ ] All lifecycle E2E tests implemented and passing
- [ ] All multi-component E2E tests implemented and passing
- [ ] All error recovery E2E tests implemented and passing
- [ ] All performance E2E tests implemented and passing
- [ ] All data flow E2E tests implemented and passing
- [ ] All Panda UI integration E2E tests implemented and passing
- [ ] All tests integrated with CI/CD
- [ ] Documentation complete
- [ ] Test coverage >90% for critical paths
```

---

## 📊 Story 1: Complete Lifecycle E2E Tests

**Type:** Story  
**Parent:** [Epic]  
**Story Points:** 8  
**Priority:** High  
**Labels:** `backend`, `e2e`, `lifecycle`, `automation`, `high-priority`  
**Sprint:** Sprint 73-74

**Title:** Complete Lifecycle E2E Tests

**Description:**
```
## 🎯 Goal
E2E tests covering complete lifecycle of Focus Server as a component: 
Startup → Configuration → Processing → Streaming → Cleanup

## 📋 Context
Focus Server needs to be tested as a complete component, not just individual API endpoints. 
This story covers the entire lifecycle from startup to cleanup, ensuring all phases work 
correctly together.

## 📋 Tasks Included
- Startup & Initialization E2E Test (2 SP)
- Configuration to Processing E2E Test (2 SP)
- Processing to Streaming E2E Test (2 SP)
- Cleanup & Resource Management E2E Test (2 SP)

## ✅ Acceptance Criteria
- [ ] All 4 lifecycle tests implemented
- [ ] All tests passing consistently
- [ ] Complete lifecycle verified end-to-end
- [ ] All phases work correctly together
- [ ] Documentation complete
- [ ] Tests integrated with CI/CD

## 🔗 Dependencies
- Requires: Focus Server API client ready
- Requires: Kubernetes client ready
- Requires: MongoDB client ready
- Requires: RabbitMQ client ready
```

---

### Sub-task 1.1: Startup & Initialization E2E Test

**Type:** Sub-task  
**Parent:** Story 1  
**Story Points:** 2  
**Priority:** High  
**Labels:** `backend`, `e2e`, `lifecycle`, `startup`, `high-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 3 hours

**Title:** Startup & Initialization E2E Test

**Description:**
```
## 🎯 Goal
E2E test of Focus Server startup and initialization as a complete component.

## 📝 Steps
1. Verify K8s pod starts successfully
   - Check pod status
   - Verify pod is running
   - Verify pod health checks pass
2. Verify MongoDB connection established
   - Check MongoDB connectivity
   - Verify connection is stable
   - Verify connection can query data
3. Verify RabbitMQ connection established
   - Check RabbitMQ connectivity
   - Verify connection is stable
   - Verify connection can send/receive messages
4. Verify Focus Server API is ready
   - Check API health endpoint
   - Verify API responds correctly
   - Verify API is ready to accept requests
5. Verify health check endpoint responds
   - Call /health endpoint
   - Verify response is 200 OK
   - Verify health status is healthy
6. Verify all services are healthy
   - Check all service statuses
   - Verify no errors in logs
   - Verify system is ready for use

## ✅ Acceptance Criteria
- [ ] K8s pod starts successfully within timeout
- [ ] MongoDB connection established and stable
- [ ] RabbitMQ connection established and stable
- [ ] Focus Server API ready and responding
- [ ] Health check endpoint returns 200 OK
- [ ] All services report healthy status
- [ ] No errors in startup logs
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Requires: Kubernetes cluster accessible
- Requires: MongoDB accessible
- Requires: RabbitMQ accessible

## 📎 Related Files
- `tests/integration/e2e/test_complete_lifecycle_startup.py`

## ⏱️ Estimate
3 hours
```

---

### Sub-task 1.2: Configuration to Processing E2E Test

**Type:** Sub-task  
**Parent:** Story 1  
**Story Points:** 2  
**Priority:** High  
**Labels:** `backend`, `e2e`, `lifecycle`, `configuration`, `high-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 4 hours

**Title:** Configuration to Processing E2E Test

**Description:**
```
## 🎯 Goal
E2E test of Configuration → Processing flow, verifying the entire flow from user 
configuration to data processing.

## 📝 Steps
1. User configures job via Panda UI (or API directly)
   - Set up configuration parameters
   - Set channels, frequency range, NFFT
   - Set view type and time range
2. Panda UI sends request to Focus Server API
   - POST /configure request
   - Include all configuration parameters
   - Verify request is sent correctly
3. Focus Server validates configuration
   - Verify configuration validation logic
   - Verify invalid configs are rejected
   - Verify valid configs are accepted
4. Focus Server creates job in K8s
   - Verify K8s job is created
   - Verify job has correct parameters
   - Verify job is scheduled correctly
5. Focus Server queries MongoDB for data
   - Verify MongoDB query is executed
   - Verify data is retrieved correctly
   - Verify data matches configuration
6. Focus Server starts processing
   - Verify processing starts
   - Verify processing is running
   - Verify processing progress
7. Verify job is running
   - Check job status
   - Verify job is active
   - Verify job is processing data
8. Verify data is being processed
   - Check processing metrics
   - Verify data is being transformed
   - Verify processing is making progress

## ✅ Acceptance Criteria
- [ ] Configuration accepted and validated correctly
- [ ] Job created successfully in K8s
- [ ] MongoDB queried correctly with right parameters
- [ ] Processing started successfully
- [ ] Job running correctly and actively processing
- [ ] Data processing progress verified
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Sub-task 1.1 (Startup & Initialization E2E Test)

## 📎 Related Files
- `tests/integration/e2e/test_complete_lifecycle_config_to_processing.py`

## ⏱️ Estimate
4 hours
```

---

### Sub-task 1.3: Processing to Streaming E2E Test

**Type:** Sub-task  
**Parent:** Story 1  
**Story Points:** 2  
**Priority:** High  
**Labels:** `backend`, `e2e`, `lifecycle`, `streaming`, `grpc`, `high-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 4 hours

**Title:** Processing to Streaming E2E Test

**Description:**
```
## 🎯 Goal
E2E test of Processing → Streaming flow, verifying data flows from processing 
to gRPC stream correctly.

## 📝 Steps
1. Job is processing data
   - Verify job is in processing state
   - Verify data is being processed
   - Verify processing is making progress
2. Focus Server prepares gRPC stream
   - Verify gRPC stream endpoint is prepared
   - Verify stream port is allocated
   - Verify stream URL is available
3. gRPC stream starts
   - Connect to gRPC stream endpoint
   - Verify connection is established
   - Verify stream is active
4. Data flows from Focus Server to client
   - Verify data is being streamed
   - Verify data packets are received
   - Verify data flow is continuous
5. Verify stream is active
   - Check stream status
   - Verify stream is not interrupted
   - Verify stream continues flowing
6. Verify data is streaming correctly
   - Verify data format is correct
   - Verify data content is valid
   - Verify data matches processed data
7. Verify stream quality
   - Check stream latency
   - Verify stream throughput
   - Verify no data loss

## ✅ Acceptance Criteria
- [ ] Processing completes successfully
- [ ] gRPC stream starts correctly
- [ ] Data flows correctly from server to client
- [ ] Stream is active and continuous
- [ ] Data quality maintained during streaming
- [ ] Stream quality meets requirements
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Sub-task 1.2 (Configuration to Processing E2E Test)
- Requires: gRPC client ready (from PZ-13949)

## 📎 Related Files
- `tests/integration/e2e/test_complete_lifecycle_processing_to_streaming.py`

## ⏱️ Estimate
4 hours
```

---

### Sub-task 1.4: Cleanup & Resource Management E2E Test

**Type:** Sub-task  
**Parent:** Story 1  
**Story Points:** 2  
**Priority:** High  
**Labels:** `backend`, `e2e`, `lifecycle`, `cleanup`, `resources`, `high-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 3 hours

**Title:** Cleanup & Resource Management E2E Test

**Description:**
```
## 🎯 Goal
E2E test of Cleanup and Resource Management, verifying resources are properly 
released after job completion or cancellation.

## 📝 Steps
1. Job completes or is cancelled
   - Complete job normally or cancel it
   - Verify job termination is requested
   - Verify termination is acknowledged
2. Focus Server stops streaming
   - Verify gRPC stream is stopped
   - Verify stream connection is closed
   - Verify no data continues flowing
3. Focus Server cleans up resources
   - Verify processing resources are released
   - Verify memory is freed
   - Verify temporary files are deleted
4. K8s job is terminated
   - Verify K8s job is terminated
   - Verify pod is stopped
   - Verify pod is removed
5. Resources are released
   - Verify CPU resources released
   - Verify memory resources released
   - Verify network resources released
6. Verify no resource leaks
   - Check for resource leaks
   - Verify no orphaned resources
   - Verify system returns to clean state
7. Verify cleanup is complete
   - Verify all cleanup steps completed
   - Verify system is ready for next job
   - Verify no errors in cleanup logs

## ✅ Acceptance Criteria
- [ ] Job cleanup successful (both completion and cancellation scenarios)
- [ ] All resources released correctly
- [ ] No resource leaks detected
- [ ] K8s job terminated and pod removed
- [ ] Cleanup complete and system ready for next job
- [ ] No errors in cleanup process
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Sub-task 1.3 (Processing to Streaming E2E Test)

## 📎 Related Files
- `tests/integration/e2e/test_complete_lifecycle_cleanup.py`

## ⏱️ Estimate
3 hours
```

---

## 📊 Story 2: Multi-Component E2E Tests

**Type:** Story  
**Parent:** [Epic]  
**Story Points:** 6  
**Priority:** High  
**Labels:** `backend`, `e2e`, `multi-component`, `integration`, `high-priority`  
**Sprint:** Sprint 73-74

**Title:** Multi-Component E2E Tests

**Description:**
```
## 🎯 Goal
E2E tests covering all components together: MongoDB + RabbitMQ + Kubernetes + 
Focus Server + gRPC, verifying integration between all components.

## 📋 Context
Focus Server operates as part of a larger system with multiple components. This story 
ensures all components work together correctly and integration points function as expected.

## 📋 Tasks Included
- MongoDB Integration E2E Test (2 SP)
- RabbitMQ Integration E2E Test (2 SP)
- Kubernetes Integration E2E Test (2 SP)

## ✅ Acceptance Criteria
- [ ] All 3 multi-component tests implemented
- [ ] All tests passing consistently
- [ ] All components integrated correctly
- [ ] Integration points verified
- [ ] Documentation complete
- [ ] Tests integrated with CI/CD

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
```

---

### Sub-task 2.1: MongoDB Integration E2E Test

**Type:** Sub-task  
**Parent:** Story 2  
**Story Points:** 2  
**Priority:** High  
**Labels:** `backend`, `e2e`, `mongodb`, `integration`, `high-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 3 hours

**Title:** MongoDB Integration E2E Test

**Description:**
```
## 🎯 Goal
E2E test of MongoDB integration, verifying Focus Server correctly interacts with 
MongoDB throughout the workflow.

## 📝 Steps
1. Verify MongoDB connection
   - Check MongoDB connectivity
   - Verify connection is stable
   - Verify connection can query data
2. Query MongoDB for historic data
   - Execute query for historic recordings
   - Verify query parameters are correct
   - Verify query returns expected data
3. Verify data retrieval
   - Verify data is retrieved correctly
   - Verify data format is correct
   - Verify data matches expected schema
4. Verify data quality
   - Verify data completeness
   - Verify data consistency
   - Verify data integrity
5. Verify MongoDB performance
   - Check query performance
   - Verify query latency is acceptable
   - Verify no performance degradation
6. Verify error handling
   - Test MongoDB connection failure
   - Verify error is handled gracefully
   - Verify error message is clear

## ✅ Acceptance Criteria
- [ ] MongoDB connection works correctly
- [ ] Data retrieval successful and correct
- [ ] Data quality verified (completeness, consistency, integrity)
- [ ] Performance acceptable (query latency <1s)
- [ ] Error handling works correctly
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_multicomponent_mongodb.py`

## ⏱️ Estimate
3 hours
```

---

### Sub-task 2.2: RabbitMQ Integration E2E Test

**Type:** Sub-task  
**Parent:** Story 2  
**Story Points:** 2  
**Priority:** High  
**Labels:** `backend`, `e2e`, `rabbitmq`, `integration`, `roi`, `high-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 3 hours

**Title:** RabbitMQ Integration E2E Test

**Description:**
```
## 🎯 Goal
E2E test of RabbitMQ integration, verifying Focus Server correctly sends and 
receives messages via RabbitMQ (e.g., ROI adjustment commands).

## 📝 Steps
1. Verify RabbitMQ connection
   - Check RabbitMQ connectivity
   - Verify connection is stable
   - Verify connection can send/receive messages
2. Send ROI adjustment command
   - Send ROI adjustment command via RabbitMQ
   - Verify command format is correct
   - Verify command is sent successfully
3. Verify command received
   - Verify Focus Server receives command
   - Verify command is parsed correctly
   - Verify command parameters are correct
4. Verify command processed
   - Verify command is processed correctly
   - Verify ROI adjustment is applied
   - Verify system responds to command
5. Verify response sent
   - Verify response is sent back
   - Verify response format is correct
   - Verify response indicates success/failure
6. Verify error handling
   - Test RabbitMQ connection failure
   - Verify error is handled gracefully
   - Verify error message is clear

## ✅ Acceptance Criteria
- [ ] RabbitMQ connection works correctly
- [ ] Commands sent successfully
- [ ] Commands received and parsed correctly
- [ ] Commands processed correctly
- [ ] Responses sent correctly
- [ ] Error handling works correctly
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_multicomponent_rabbitmq.py`

## ⏱️ Estimate
3 hours
```

---

### Sub-task 2.3: Kubernetes Integration E2E Test

**Type:** Sub-task  
**Parent:** Story 2  
**Story Points:** 2  
**Priority:** High  
**Labels:** `backend`, `e2e`, `kubernetes`, `integration`, `high-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 4 hours

**Title:** Kubernetes Integration E2E Test

**Description:**
```
## 🎯 Goal
E2E test of Kubernetes integration, verifying Focus Server correctly manages 
K8s jobs and pods throughout the workflow.

## 📝 Steps
1. Verify K8s job creation
   - Create job via Focus Server API
   - Verify job is created in K8s
   - Verify job has correct parameters
2. Verify pod lifecycle
   - Verify pod is created
   - Verify pod starts successfully
   - Verify pod runs correctly
   - Verify pod terminates correctly
3. Verify resource allocation
   - Verify CPU resources allocated
   - Verify memory resources allocated
   - Verify resources match requirements
4. Verify port exposure
   - Verify gRPC port is exposed
   - Verify port is accessible
   - Verify port mapping is correct
5. Verify job termination
   - Terminate job via API
   - Verify job is terminated in K8s
   - Verify pod is stopped
6. Verify cleanup
   - Verify pod is removed
   - Verify resources are released
   - Verify no orphaned resources

## ✅ Acceptance Criteria
- [ ] K8s job created successfully with correct parameters
- [ ] Pod lifecycle managed correctly (create → run → terminate)
- [ ] Resources allocated correctly (CPU, memory)
- [ ] Ports exposed correctly and accessible
- [ ] Job terminated correctly
- [ ] Cleanup complete (no orphaned resources)
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_multicomponent_kubernetes.py`

## ⏱️ Estimate
4 hours
```

---

## 📊 Story 3: Error Recovery E2E Tests

**Type:** Story  
**Parent:** [Epic]  
**Story Points:** 6  
**Priority:** High  
**Labels:** `backend`, `e2e`, `error-handling`, `recovery`, `high-priority`  
**Sprint:** Sprint 75-76

**Title:** Error Recovery E2E Tests

**Description:**
```
## 🎯 Goal
E2E tests for error scenarios and recovery, verifying the system handles errors 
gracefully and recovers correctly.

## 📋 Context
Focus Server must handle errors gracefully and recover correctly. This story ensures 
error scenarios are tested end-to-end and recovery mechanisms work as expected.

## 📋 Tasks Included
- MongoDB Failure Recovery E2E Test (2 SP)
- RabbitMQ Failure Recovery E2E Test (2 SP)
- Kubernetes Pod Failure Recovery E2E Test (2 SP)

## ✅ Acceptance Criteria
- [ ] All 3 error recovery tests implemented
- [ ] All tests passing consistently
- [ ] Error scenarios covered end-to-end
- [ ] Recovery scenarios verified
- [ ] Error messages are clear and actionable
- [ ] Documentation complete
- [ ] Tests integrated with CI/CD

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)
```

---

### Sub-task 3.1: MongoDB Failure Recovery E2E Test

**Type:** Sub-task  
**Parent:** Story 3  
**Story Points:** 2  
**Priority:** High  
**Labels:** `backend`, `e2e`, `error-handling`, `mongodb`, `recovery`, `high-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 4 hours

**Title:** MongoDB Failure Recovery E2E Test

**Description:**
```
## 🎯 Goal
E2E test of MongoDB failure and recovery, verifying the system handles MongoDB 
failures gracefully and recovers correctly.

## 📝 Steps
1. Start job successfully
   - Configure and start a job
   - Verify job is running
   - Verify data is being processed
2. Stop MongoDB during job
   - Simulate MongoDB failure (stop service or network issue)
   - Verify failure is detected
   - Verify job behavior during failure
3. Verify error handling
   - Verify error is detected correctly
   - Verify error is logged properly
   - Verify error doesn't crash the system
4. Verify error message displayed
   - Check if error message is shown (via API or logs)
   - Verify error message is clear
   - Verify error message is actionable
5. Restart MongoDB
   - Restart MongoDB service
   - Verify MongoDB is accessible again
   - Verify connection is re-established
6. Verify recovery
   - Verify system detects MongoDB recovery
   - Verify system attempts to reconnect
   - Verify connection is re-established
7. Verify job can continue or retry
   - Verify job can retry after recovery
   - Verify data is not lost
   - Verify job can complete successfully

## ✅ Acceptance Criteria
- [ ] Error detected correctly when MongoDB fails
- [ ] Error message displayed and is clear/actionable
- [ ] System handles failure gracefully (no crashes)
- [ ] Recovery works correctly when MongoDB restarts
- [ ] Job can retry after recovery
- [ ] No data loss during failure/recovery
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_error_recovery_mongodb.py`

## ⏱️ Estimate
4 hours
```

---

### Sub-task 3.2: RabbitMQ Failure Recovery E2E Test

**Type:** Sub-task  
**Parent:** Story 3  
**Story Points:** 2  
**Priority:** High  
**Labels:** `backend`, `e2e`, `error-handling`, `rabbitmq`, `recovery`, `high-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 3 hours

**Title:** RabbitMQ Failure Recovery E2E Test

**Description:**
```
## 🎯 Goal
E2E test of RabbitMQ failure and recovery, verifying the system handles RabbitMQ 
failures gracefully and recovers correctly.

## 📝 Steps
1. Start job successfully
   - Configure and start a job
   - Verify job is running
   - Verify RabbitMQ connection is active
2. Stop RabbitMQ during job
   - Simulate RabbitMQ failure (stop service or network issue)
   - Verify failure is detected
   - Verify job behavior during failure
3. Verify error handling
   - Verify error is detected correctly
   - Verify error is logged properly
   - Verify error doesn't crash the system
4. Verify error message displayed
   - Check if error message is shown (via API or logs)
   - Verify error message is clear
   - Verify error message is actionable
5. Restart RabbitMQ
   - Restart RabbitMQ service
   - Verify RabbitMQ is accessible again
   - Verify connection is re-established
6. Verify recovery
   - Verify system detects RabbitMQ recovery
   - Verify system attempts to reconnect
   - Verify connection is re-established
7. Verify commands work again
   - Send test command via RabbitMQ
   - Verify command is received
   - Verify command is processed correctly

## ✅ Acceptance Criteria
- [ ] Error detected correctly when RabbitMQ fails
- [ ] Error message displayed and is clear/actionable
- [ ] System handles failure gracefully (no crashes)
- [ ] Recovery works correctly when RabbitMQ restarts
- [ ] Commands work again after recovery
- [ ] No data loss during failure/recovery
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_error_recovery_rabbitmq.py`

## ⏱️ Estimate
3 hours
```

---

### Sub-task 3.3: Kubernetes Pod Failure Recovery E2E Test

**Type:** Sub-task  
**Parent:** Story 3  
**Story Points:** 2  
**Priority:** High  
**Labels:** `backend`, `e2e`, `error-handling`, `kubernetes`, `recovery`, `high-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 4 hours

**Title:** Kubernetes Pod Failure Recovery E2E Test

**Description:**
```
## 🎯 Goal
E2E test of Kubernetes pod failure and recovery, verifying the system handles pod 
failures gracefully and recovers correctly.

## 📝 Steps
1. Start job successfully
   - Configure and start a job
   - Verify job is running
   - Verify pod is active
2. Kill K8s pod during job
   - Simulate pod failure (kill pod or node failure)
   - Verify failure is detected
   - Verify job behavior during failure
3. Verify error handling
   - Verify error is detected correctly
   - Verify error is logged properly
   - Verify error doesn't crash the system
4. Verify error message displayed
   - Check if error message is shown (via API or logs)
   - Verify error message is clear
   - Verify error message is actionable
5. Verify pod restarts
   - Verify K8s restarts the pod (if restart policy allows)
   - Verify pod comes back online
   - Verify pod is healthy
6. Verify recovery
   - Verify system detects pod recovery
   - Verify system reconnects to pod
   - Verify job can continue
7. Verify job can continue or retry
   - Verify job can retry after recovery
   - Verify data is not lost
   - Verify job can complete successfully

## ✅ Acceptance Criteria
- [ ] Error detected correctly when pod fails
- [ ] Error message displayed and is clear/actionable
- [ ] System handles failure gracefully (no crashes)
- [ ] Pod restarts correctly (if restart policy allows)
- [ ] Recovery works correctly when pod recovers
- [ ] Job can retry after recovery
- [ ] No data loss during failure/recovery
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_error_recovery_kubernetes.py`

## ⏱️ Estimate
4 hours
```

---

## 📊 Story 4: Performance E2E Tests

**Type:** Story  
**Parent:** [Epic]  
**Story Points:** 8  
**Priority:** Medium  
**Labels:** `backend`, `e2e`, `performance`, `load`, `automation`, `medium-priority`  
**Sprint:** Sprint 79-80

**Title:** Performance E2E Tests

**Description:**
```
## 🎯 Goal
E2E tests for performance under load, verifying the system meets performance 
requirements end-to-end.

## 📋 Context
Focus Server must handle expected load (200 concurrent jobs) and meet latency 
requirements. This story ensures performance is validated end-to-end.

## 📋 Tasks Included
- Concurrent Jobs Performance E2E Test (3 SP)
- Latency Measurement E2E Test (2 SP)
- Capacity & Stress E2E Test (3 SP)

## ✅ Acceptance Criteria
- [ ] All 3 performance tests implemented
- [ ] All tests passing consistently
- [ ] Performance requirements met (<5s latency, 200 concurrent jobs)
- [ ] Capacity validated
- [ ] Performance metrics collected
- [ ] Documentation complete
- [ ] Tests integrated with CI/CD

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)
```

---

### Sub-task 4.1: Concurrent Jobs Performance E2E Test

**Type:** Sub-task  
**Parent:** Story 4  
**Story Points:** 3  
**Priority:** Medium  
**Labels:** `backend`, `e2e`, `performance`, `load`, `concurrent`, `medium-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 5 hours

**Title:** Concurrent Jobs Performance E2E Test

**Description:**
```
## 🎯 Goal
E2E test of performance with 200 concurrent jobs, verifying the system can handle 
expected load end-to-end.

## 📝 Steps
1. Start 200 concurrent jobs
   - Configure 200 different jobs
   - Start all jobs simultaneously
   - Verify all jobs are started
2. Monitor system performance
   - Monitor CPU usage
   - Monitor memory usage
   - Monitor network usage
   - Monitor response times
3. Verify all jobs start successfully
   - Verify all jobs are accepted
   - Verify all jobs are created in K8s
   - Verify all jobs start processing
4. Verify data quality maintained
   - Sample data from multiple jobs
   - Verify data quality is maintained
   - Verify no data corruption
5. Verify no performance degradation
   - Monitor performance metrics
   - Verify performance doesn't degrade
   - Verify system remains responsive
6. Verify all jobs complete successfully
   - Wait for all jobs to complete
   - Verify all jobs complete successfully
   - Verify no jobs fail due to load
7. Verify resource usage acceptable
   - Check resource usage during load
   - Verify resource usage is acceptable
   - Verify no resource exhaustion

## ✅ Acceptance Criteria
- [ ] All 200 jobs start successfully
- [ ] Performance maintained under load
- [ ] Data quality maintained (no degradation)
- [ ] No performance degradation detected
- [ ] All jobs complete successfully
- [ ] Resource usage acceptable (no exhaustion)
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_performance_concurrent_jobs.py`

## ⏱️ Estimate
5 hours
```

---

### Sub-task 4.2: Latency Measurement E2E Test

**Type:** Sub-task  
**Parent:** Story 4  
**Story Points:** 2  
**Priority:** Medium  
**Labels:** `backend`, `e2e`, `performance`, `latency`, `medium-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 3 hours

**Title:** Latency Measurement E2E Test

**Description:**
```
## 🎯 Goal
E2E test of latency end-to-end, verifying latency meets requirements (<5s) 
for all operations.

## 📝 Steps
1. Measure latency: User Action → Data Display
   - Start timer when user action occurs
   - Stop timer when data is displayed
   - Record latency measurement
2. Measure latency: Configuration → Job Start
   - Start timer when configuration is sent
   - Stop timer when job starts processing
   - Record latency measurement
3. Measure latency: Data Processing → Stream Start
   - Start timer when processing starts
   - Stop timer when stream starts
   - Record latency measurement
4. Measure latency: Stream Start → Data Display
   - Start timer when stream starts
   - Stop timer when data is displayed
   - Record latency measurement
5. Verify latency meets requirements (<5s)
   - Check all latency measurements
   - Verify all are <5s
   - Verify P95 latency is acceptable
6. Verify latency is consistent
   - Run multiple measurements
   - Verify latency is consistent
   - Verify no outliers

## ✅ Acceptance Criteria
- [ ] Latency measured correctly for all operations
- [ ] All latency measurements <5s
- [ ] P95 latency acceptable
- [ ] Latency consistent across runs
- [ ] Performance requirements met
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_performance_latency.py`

## ⏱️ Estimate
3 hours
```

---

### Sub-task 4.3: Capacity & Stress E2E Test

**Type:** Sub-task  
**Parent:** Story 4  
**Story Points:** 3  
**Priority:** Medium  
**Labels:** `backend`, `e2e`, `performance`, `capacity`, `stress`, `medium-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 4 hours

**Title:** Capacity & Stress E2E Test

**Description:**
```
## 🎯 Goal
E2E test of capacity and stress, verifying the system handles capacity limits 
and stress scenarios correctly.

## 📝 Steps
1. Start jobs up to capacity limit
   - Start jobs gradually up to capacity (200 jobs)
   - Verify system handles capacity
   - Verify all jobs are accepted
2. Verify system handles capacity
   - Monitor system behavior at capacity
   - Verify system remains stable
   - Verify performance is maintained
3. Try to exceed capacity
   - Attempt to start more jobs than capacity
   - Verify system rejects excess jobs
   - Verify error handling works
4. Verify error handling
   - Verify error message is clear
   - Verify error is returned correctly
   - Verify system doesn't crash
5. Verify system recovers
   - Complete some jobs to free capacity
   - Verify system accepts new jobs
   - Verify system recovers correctly
6. Verify no data loss
   - Verify data is not lost during stress
   - Verify data quality maintained
   - Verify no corruption
7. Verify performance maintained
   - Monitor performance during stress
   - Verify performance doesn't degrade
   - Verify system remains responsive

## ✅ Acceptance Criteria
- [ ] Capacity limit respected (200 jobs)
- [ ] Error handling works when exceeding capacity
- [ ] System recovers correctly after stress
- [ ] No data loss during stress scenarios
- [ ] Performance maintained under stress
- [ ] System remains stable
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_performance_capacity.py`

## ⏱️ Estimate
4 hours
```

---

## 📊 Story 5: Data Flow E2E Tests

**Type:** Story  
**Parent:** [Epic]  
**Story Points:** 6  
**Priority:** High  
**Labels:** `backend`, `e2e`, `data-flow`, `data-quality`, `high-priority`  
**Sprint:** Sprint 75-76

**Title:** Data Flow E2E Tests

**Description:**
```
## 🎯 Goal
E2E tests covering complete data flow: MongoDB → Focus Server → gRPC → Client → 
Display, verifying data consistency and quality throughout the flow.

## 📋 Context
Data must flow correctly through all components without loss or corruption. This story 
ensures data consistency and quality are maintained end-to-end.

## 📋 Tasks Included
- Historic Data Flow E2E Test (2 SP)
- Live Data Flow E2E Test (2 SP)
- Data Consistency E2E Test (2 SP)

## ✅ Acceptance Criteria
- [ ] All 3 data flow tests implemented
- [ ] All tests passing consistently
- [ ] Data consistency verified end-to-end
- [ ] Data quality maintained throughout flow
- [ ] No data loss or corruption
- [ ] Documentation complete
- [ ] Tests integrated with CI/CD

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)
```

---

### Sub-task 5.1: Historic Data Flow E2E Test

**Type:** Sub-task  
**Parent:** Story 5  
**Story Points:** 2  
**Priority:** High  
**Labels:** `backend`, `e2e`, `data-flow`, `historic`, `high-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 4 hours

**Title:** Historic Data Flow E2E Test

**Description:**
```
## 🎯 Goal
E2E test of historic data flow, verifying data flows correctly from MongoDB 
through Focus Server to client display.

## 📝 Steps
1. Data exists in MongoDB (historic recording)
   - Verify historic recording exists
   - Verify recording has data
   - Verify recording metadata is correct
2. User requests historic playback (Panda UI or API)
   - Configure historic playback
   - Set time range matching recording
   - Start playback
3. Focus Server queries MongoDB
   - Verify query is executed
   - Verify query parameters are correct
   - Verify data is retrieved
4. Focus Server processes data
   - Verify data is processed
   - Verify processing is correct
   - Verify data format is correct
5. Focus Server streams via gRPC
   - Verify stream starts
   - Verify data is streamed
   - Verify stream format is correct
6. Client receives data
   - Verify data is received
   - Verify data format is correct
   - Verify data is complete
7. Data displayed correctly (Panda UI)
   - Verify data is displayed
   - Verify display is correct
   - Verify user sees expected data
8. Verify data matches MongoDB source
   - Compare displayed data with source
   - Verify data matches exactly
   - Verify no data loss or corruption
9. Verify data quality maintained
   - Verify data completeness
   - Verify data consistency
   - Verify data integrity

## ✅ Acceptance Criteria
- [ ] Data retrieved from MongoDB correctly
- [ ] Data processed correctly by Focus Server
- [ ] Data streamed via gRPC correctly
- [ ] Data displayed correctly in client
- [ ] Data matches MongoDB source (no loss/corruption)
- [ ] Data quality maintained throughout flow
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_data_flow_historic.py`

## ⏱️ Estimate
4 hours
```

---

### Sub-task 5.2: Live Data Flow E2E Test

**Type:** Sub-task  
**Parent:** Story 5  
**Story Points:** 2  
**Priority:** High  
**Labels:** `backend`, `e2e`, `data-flow`, `live`, `high-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 4 hours

**Title:** Live Data Flow E2E Test

**Description:**
```
## 🎯 Goal
E2E test of live data flow, verifying live data flows correctly from sensors 
through Focus Server to client display.

## 📝 Steps
1. User starts live monitoring (Panda UI or API)
   - Configure live monitoring
   - Set up live parameters
   - Start live monitoring
2. Focus Server connects to live sensors
   - Verify sensor connection
   - Verify sensors are active
   - Verify data is available
3. Focus Server processes live data
   - Verify data is processed
   - Verify processing is real-time
   - Verify data format is correct
4. Focus Server streams via gRPC
   - Verify stream starts
   - Verify data is streamed continuously
   - Verify stream format is correct
5. Client receives live data
   - Verify data is received continuously
   - Verify data format is correct
   - Verify data is current
6. Data displayed correctly (Panda UI)
   - Verify data is displayed
   - Verify display updates continuously
   - Verify user sees live data
7. Verify data is live and current
   - Verify data timestamps are current
   - Verify data is not stale
   - Verify data updates continuously
8. Verify data quality maintained
   - Verify data completeness
   - Verify data consistency
   - Verify data integrity

## ✅ Acceptance Criteria
- [ ] Live sensors connected correctly
- [ ] Live data processed correctly by Focus Server
- [ ] Live data streamed via gRPC correctly
- [ ] Live data displayed correctly in client
- [ ] Data is live and current (not stale)
- [ ] Data quality maintained throughout flow
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_data_flow_live.py`

## ⏱️ Estimate
4 hours
```

---

### Sub-task 5.3: Data Consistency E2E Test

**Type:** Sub-task  
**Parent:** Story 5  
**Story Points:** 2  
**Priority:** High  
**Labels:** `backend`, `e2e`, `data-flow`, `consistency`, `high-priority`  
**Assignee:** [Team Lead - Backend Automation]  
**Estimate:** 3 hours

**Title:** Data Consistency E2E Test

**Description:**
```
## 🎯 Goal
E2E test of data consistency, verifying data remains consistent across all 
components throughout the flow.

## 📝 Steps
1. Start job with specific configuration
   - Configure job with known parameters
   - Start job
   - Verify job is running
2. Verify data consistency across all components
   - Check data in MongoDB
   - Check data in Focus Server
   - Check data in gRPC stream
   - Check data in client display
3. Verify MongoDB data matches streamed data
   - Compare MongoDB data with streamed data
   - Verify data matches exactly
   - Verify no data loss or corruption
4. Verify displayed data matches streamed data
   - Compare streamed data with displayed data
   - Verify data matches exactly
   - Verify no data loss or corruption
5. Verify no data corruption
   - Check data integrity at each step
   - Verify no corruption detected
   - Verify data is valid
6. Verify data integrity maintained
   - Verify data completeness
   - Verify data consistency
   - Verify data integrity

## ✅ Acceptance Criteria
- [ ] Data consistent across all components
- [ ] MongoDB data matches streamed data exactly
- [ ] Displayed data matches streamed data exactly
- [ ] No data corruption detected
- [ ] Data integrity maintained throughout flow
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_data_flow_consistency.py`

## ⏱️ Estimate
3 hours
```

---

## 📊 Story 6: Panda UI Integration E2E Tests

**Type:** Story  
**Parent:** [Epic]  
**Story Points:** 8  
**Priority:** High  
**Labels:** `frontend`, `e2e`, `panda-ui`, `integration`, `high-priority`  
**Sprint:** Sprint 77-78

**Title:** Panda UI Integration E2E Tests

**Description:**
```
## 🎯 Goal
Complete E2E tests with Panda UI covering full flow from user action to data display, 
ensuring all components work together correctly.

## 📋 Context
Panda UI is the client interface for Focus Server. This story ensures the complete 
flow from user action in Panda UI through Focus Server to data display works correctly.

## 📋 Tasks Included
- Live Mode Full Flow E2E Test (2 SP)
- Historic Mode Full Flow E2E Test (2 SP)
- Error Handling Full Flow E2E Test (2 SP)
- View Switching Full Flow E2E Test (2 SP)

## ✅ Acceptance Criteria
- [ ] All 4 Panda UI integration tests implemented
- [ ] All tests passing consistently
- [ ] Full flow verified end-to-end
- [ ] User experience validated
- [ ] All components integrated correctly
- [ ] Documentation complete
- [ ] Tests integrated with CI/CD

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)
- Requires: Playwright E2E Framework Setup (PZ-XXXX)
- Requires: Page Objects implemented
```

---

### Sub-task 6.1: Live Mode Full Flow E2E Test

**Type:** Sub-task  
**Parent:** Story 6  
**Story Points:** 2  
**Priority:** High  
**Labels:** `frontend`, `e2e`, `panda-ui`, `live-mode`, `high-priority`  
**Assignee:** [Ron - Frontend & UI Automation]  
**Estimate:** 4 hours

**Title:** Live Mode Full Flow E2E Test

**Description:**
```
## 🎯 Goal
Complete E2E test of Live Mode with Panda UI, verifying the full flow from user 
action to data display.

## 📝 Steps
1. User opens Panda UI
   - Navigate to Panda UI
   - Verify UI loads correctly
   - Verify UI is ready
2. User configures live mode
   - Fill configuration form
   - Set channels, frequency range, NFFT
   - Set view type to Live
3. User clicks "Start Streaming"
   - Click start button
   - Verify request is sent
4. Panda UI → Focus Server API
   - Verify API request is sent
   - Verify request parameters are correct
   - Verify request is received
5. Focus Server → MongoDB → Processing → gRPC
   - Verify Focus Server processes request
   - Verify MongoDB is queried
   - Verify processing starts
   - Verify gRPC stream starts
6. gRPC → Panda UI → Display
   - Verify data is received in Panda UI
   - Verify data is displayed
   - Verify display updates continuously
7. User sees live spectrogram
   - Verify spectrogram is displayed
   - Verify spectrogram updates
   - Verify user sees expected data
8. Verify all components work together
   - Verify Panda UI works correctly
   - Verify Focus Server API works
   - Verify MongoDB integration works
   - Verify gRPC streaming works
9. Verify data flow is correct
   - Verify data flows correctly
   - Verify data quality maintained
   - Verify no data loss

## ✅ Acceptance Criteria
- [ ] Panda UI works correctly
- [ ] Focus Server API works correctly
- [ ] MongoDB integration works correctly
- [ ] gRPC streaming works correctly
- [ ] Data displayed correctly in Panda UI
- [ ] All components integrated correctly
- [ ] Data flow is correct end-to-end
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)
- Requires: Playwright E2E Framework Setup
- Requires: Page Objects implemented
- Related: PZ-13951 (Live Mode E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_panda_ui_live_mode_full_flow.py`
- `tests/e2e/page_objects/panda_app_page.py`

## ⏱️ Estimate
4 hours
```

---

### Sub-task 6.2: Historic Mode Full Flow E2E Test

**Type:** Sub-task  
**Parent:** Story 6  
**Story Points:** 2  
**Priority:** High  
**Labels:** `frontend`, `e2e`, `panda-ui`, `historic-mode`, `high-priority`  
**Assignee:** [Ron - Frontend & UI Automation]  
**Estimate:** 4 hours

**Title:** Historic Mode Full Flow E2E Test

**Description:**
```
## 🎯 Goal
Complete E2E test of Historic Mode with Panda UI, verifying the full flow from 
user action to data display.

## 📝 Steps
1. User opens Panda UI
   - Navigate to Panda UI
   - Verify UI loads correctly
   - Verify UI is ready
2. User configures historic mode
   - Fill configuration form
   - Set channels, frequency range, NFFT
   - Set view type to Historic
   - Select time range
3. User clicks "Start Playback"
   - Click start button
   - Verify request is sent
4. Panda UI → Focus Server API
   - Verify API request is sent
   - Verify request parameters are correct
   - Verify request is received
5. Focus Server → MongoDB → Processing → gRPC
   - Verify Focus Server processes request
   - Verify MongoDB is queried for historic data
   - Verify processing starts
   - Verify gRPC stream starts
6. gRPC → Panda UI → Display
   - Verify data is received in Panda UI
   - Verify data is displayed
   - Verify playback controls work
7. User sees historic spectrogram
   - Verify spectrogram is displayed
   - Verify playback controls work
   - Verify user sees expected data
8. Verify playback controls work
   - Test pause/resume
   - Test seek functionality
   - Test playback speed (if available)
9. Verify all components work together
   - Verify Panda UI works correctly
   - Verify Focus Server API works
   - Verify MongoDB integration works
   - Verify gRPC streaming works

## ✅ Acceptance Criteria
- [ ] Panda UI works correctly
- [ ] Focus Server API works correctly
- [ ] MongoDB integration works correctly
- [ ] gRPC streaming works correctly
- [ ] Playback controls work correctly
- [ ] Data displayed correctly in Panda UI
- [ ] All components integrated correctly
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)
- Requires: Playwright E2E Framework Setup
- Requires: Page Objects implemented
- Related: PZ-13952 (Historic Mode E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_panda_ui_historic_mode_full_flow.py`
- `tests/e2e/page_objects/panda_app_page.py`

## ⏱️ Estimate
4 hours
```

---

### Sub-task 6.3: Error Handling Full Flow E2E Test

**Type:** Sub-task  
**Parent:** Story 6  
**Story Points:** 2  
**Priority:** High  
**Labels:** `frontend`, `e2e`, `panda-ui`, `error-handling`, `high-priority`  
**Assignee:** [Ron - Frontend & UI Automation]  
**Estimate:** 4 hours

**Title:** Error Handling Full Flow E2E Test

**Description:**
```
## 🎯 Goal
Complete E2E test of Error Handling with Panda UI, verifying error scenarios 
are handled correctly end-to-end.

## 📝 Steps
1. User starts job via Panda UI
   - Configure and start job
   - Verify job starts
2. Simulate error (MongoDB down, etc.)
   - Stop MongoDB or simulate other error
   - Verify error occurs
3. Verify error detected
   - Verify error is detected by Focus Server
   - Verify error is logged
4. Verify error message displayed in Panda UI
   - Verify error message appears in UI
   - Verify error message is clear
   - Verify error message is actionable
5. Verify user can retry
   - Verify retry button is available
   - Verify retry functionality works
6. Verify recovery works
   - Restart MongoDB or fix error
   - Verify system recovers
7. Verify job succeeds after retry
   - Retry job
   - Verify job succeeds
   - Verify data is displayed correctly

## ✅ Acceptance Criteria
- [ ] Errors detected correctly
- [ ] Error messages displayed correctly in Panda UI
- [ ] Error messages are clear and actionable
- [ ] User can retry after error
- [ ] Recovery works correctly
- [ ] Job succeeds after retry
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)
- Story 3 (Error Recovery E2E Tests)
- Requires: Playwright E2E Framework Setup
- Requires: Page Objects implemented
- Related: PZ-13953 (Error Handling E2E Tests)

## 📎 Related Files
- `tests/integration/e2e/test_panda_ui_error_handling_full_flow.py`
- `tests/e2e/page_objects/panda_app_page.py`

## ⏱️ Estimate
4 hours
```

---

### Sub-task 6.4: View Switching Full Flow E2E Test

**Type:** Sub-task  
**Parent:** Story 6  
**Story Points:** 2  
**Priority:** High  
**Labels:** `frontend`, `e2e`, `panda-ui`, `view-switching`, `high-priority`  
**Assignee:** [Ron - Frontend & UI Automation]  
**Estimate:** 3 hours

**Title:** View Switching Full Flow E2E Test

**Description:**
```
## 🎯 Goal
Complete E2E test of View Switching with Panda UI, verifying view switching 
works correctly during streaming.

## 📝 Steps
1. User starts job with MultiChannel view
   - Configure job with MultiChannel view
   - Start job
   - Verify MultiChannel view displays
2. User switches to SingleChannel view
   - Switch to SingleChannel view
   - Verify view switches
   - Verify SingleChannel view displays
3. User switches to Waterfall view
   - Switch to Waterfall view
   - Verify view switches
   - Verify Waterfall view displays
4. Verify each view displays correctly
   - Verify MultiChannel view is correct
   - Verify SingleChannel view is correct
   - Verify Waterfall view is correct
5. Verify data continues streaming
   - Verify data continues during switches
   - Verify no interruption
   - Verify data quality maintained
6. Verify no data loss during switches
   - Verify no data is lost
   - Verify data consistency maintained
   - Verify no corruption

## ✅ Acceptance Criteria
- [ ] View switching works correctly
- [ ] Each view displays correctly
- [ ] Data continues streaming during switches
- [ ] No data loss during switches
- [ ] Performance maintained
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
- Story 1 (Complete Lifecycle E2E Tests)
- Story 2 (Multi-Component E2E Tests)
- Requires: Playwright E2E Framework Setup
- Requires: Page Objects implemented

## 📎 Related Files
- `tests/integration/e2e/test_panda_ui_view_switching_full_flow.py`
- `tests/e2e/page_objects/panda_app_page.py`

## ⏱️ Estimate
3 hours
```

---

## 📊 Summary Table

| Story | Sub-tasks | Story Points | Priority | Sprint |
|------|-----------|--------------|----------|--------|
| **1. Complete Lifecycle E2E** | 4 | 8 | High | 73-74 |
| **2. Multi-Component E2E** | 3 | 6 | High | 73-74 |
| **3. Error Recovery E2E** | 3 | 6 | High | 75-76 |
| **4. Performance E2E** | 3 | 8 | Medium | 79-80 |
| **5. Data Flow E2E** | 3 | 6 | High | 75-76 |
| **6. Panda UI Integration E2E** | 4 | 8 | High | 77-78 |
| **Total** | **20** | **42** | | |

---

## 📅 Sprint Planning

### Sprint 73-74 (Weeks 1-2)
- Story 1: Complete Lifecycle E2E Tests (8 SP)
- Story 2: Multi-Component E2E Tests (6 SP)
- **Total:** 14 SP

### Sprint 75-76 (Weeks 3-4)
- Story 3: Error Recovery E2E Tests (6 SP)
- Story 5: Data Flow E2E Tests (6 SP)
- **Total:** 12 SP

### Sprint 77-78 (Weeks 5-6)
- Story 6: Panda UI Integration E2E Tests (8 SP)
- **Total:** 8 SP

### Sprint 79-80 (Weeks 7-8)
- Story 4: Performance E2E Tests (8 SP)
- **Total:** 8 SP

---

## ✅ Epic Checklist

- [ ] Epic created in Jira
- [ ] 6 Stories created and linked
- [ ] 20 Sub-tasks created and linked
- [ ] Dependencies mapped
- [ ] Sprint planning completed
- [ ] Team assigned
- [ ] Progress tracking setup
- [ ] All tickets have proper labels
- [ ] All tickets have Story Points

---

**Last Updated:** 2025-11-04  
**Created by:** QA Team Lead  
**Status:** Ready for Jira Import

