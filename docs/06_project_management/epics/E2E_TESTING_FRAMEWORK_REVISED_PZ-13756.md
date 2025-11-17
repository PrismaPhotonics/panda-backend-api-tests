# 🎯 Epic: End-to-End Infrastructure & API Testing Framework - Panda

**Epic ID:** AUTO-E2E-001 (Revised)  
**Created:** 27 October 2025  
**Revised Based On:** Meeting Decision PZ-13756 (Scope Refinement)  
**Priority:** High  
**Type:** Testing Infrastructure

---

## ⚠️ **CRITICAL SCOPE REVISION** (27 Oct 2025)

**Following meeting decision (PZ-13756), this Epic has been REVISED to align with approved scope:**

### ✅ **IN SCOPE (Focus Areas):**
- **Infrastructure Observability:** K8s pod monitoring, system health, resource usage
- **API Behavior Validation:** Request/response flows, error handling, timeouts
- **Transport Layer Testing:** gRPC port/handshake readiness (NOT content)
- **User Experience (Errors):** Clear error messages displayed to users
- **System Integration:** Backend API → Transport → UI error flow

### ❌ **OUT OF SCOPE (Removed from Epic):**
- ~~Internal Job processing ("Baby")~~ 
- ~~Algorithm/data correctness~~
- ~~Spectrogram content validation~~
- ~~Full gRPC stream content validation~~
- ~~Visual regression of data rendering~~

### 🔄 **MODIFIED SCOPE:**
- **gRPC Testing:** Transport readiness ONLY (connection, port availability, handshake)
- **UI Testing:** Error handling and user messaging ONLY (not data visualization)

---

## 📋 Summary (Revised)

**Goal:** Implement End-to-End testing framework validating **infrastructure behavior**, **API responses**, and **error handling** from Backend → Frontend UI, focusing on **user experience during failures** and **system observability**.

**NOT Goal:** Validate data correctness, algorithm output, or spectrogram content.

---

## 🎯 Current Gap (Revised)

```
✅ Have: Backend API tests (200/422/404 responses)
✅ Have: K8s lifecycle tests (from PZ-13756 implementation)
✅ Have: Pre-launch validation tests (from PZ-13756 implementation)

❌ Missing: gRPC transport readiness validation
❌ Missing: UI error message validation (user experience)
❌ Missing: End-to-end error flow testing
❌ Missing: System observability during failures
```

---

## 🏆 Epic Goal (Revised)

**Enable infrastructure and error-flow validation** ensuring:
1. **gRPC transport is ready** (port accessible, connection works)
2. **Users see clear error messages** when things fail
3. **System observability** during E2E flows
4. **API → UI error propagation** works correctly

**Explicitly NOT validating:**
- Data correctness in streams
- Spectrogram visual accuracy
- Algorithm output

---

## 📊 Epic Objectives (Revised)

| Objective | Description | Success Metric |
|-----------|-------------|----------------|
| **1. Transport Validation** | Validate gRPC connection readiness | >95% connection success |
| **2. Error Flow Validation** | Ensure errors propagate clearly to UI | All error scenarios tested |
| **3. System Observability** | Monitor K8s/infra during E2E flows | Metrics captured |
| **4. User Experience (Errors)** | Clear error messages in UI | >90% error clarity score |

---

## 📦 Epic Breakdown: Revised Stories & Tasks

---

### Story 1: gRPC Transport Readiness Validation (REVISED)

**Story ID:** AUTO-E2E-001  
**Story Points:** 3 (reduced from 8)  
**Priority:** High (Must Have)  
**Dependencies:** None

#### **Description (REVISED)**

As a QA Engineer, I want to validate that the **gRPC transport layer is ready** (port accessible, connection works, handshake succeeds), so that I can ensure the transport is operational.

**⚠️ SCOPE CHANGE:** We validate **transport readiness ONLY**, NOT stream content or data correctness.

#### **Acceptance Criteria (REVISED)**

- [ ] gRPC client can connect to stream port
- [ ] Connection handshake succeeds
- [ ] Can verify port is listening
- [ ] Can detect connection failures with clear errors
- [ ] **NOT testing:** Stream content, data validation, frame structure

#### **Tasks (REVISED)**

**Task 1.1: Setup gRPC transport testing (2h)**
```python
# Create tests/integration/grpc_transport/
├── conftest.py          # Fixtures for gRPC connection
├── test_grpc_transport_readiness.py
└── README.md
```

**Task 1.2: Implement GrpcTransportTester (1h)**
```python
# helpers/grpc_transport_tester.py

class GrpcTransportTester:
    """
    Test gRPC transport readiness (NOT content validation).
    
    Validates:
    - Port is accessible
    - Connection handshake succeeds
    - Transport is ready to receive connections
    
    Does NOT validate:
    - Stream content
    - Data correctness
    - Message parsing
    """
    
    def can_connect(self, host, port) -> bool:
        """Check if gRPC port is accessible."""
    
    def verify_handshake(self, host, port) -> bool:
        """Verify gRPC handshake succeeds."""
```

**Task 1.3: Write transport readiness tests (2h)**
```python
@pytest.mark.integration
@pytest.mark.grpc_transport
class TestGrpcTransportReadiness:
    
    def test_grpc_port_accessible_after_job_creation():
        """
        Test: gRPC port becomes accessible after job creation.
        
        Validates:
        - Create job via API
        - Get stream_port from response
        - Verify port is in LISTEN state
        - Can establish connection
        
        Does NOT validate stream content.
        """
    
    def test_grpc_connection_handshake_succeeds():
        """
        Test: gRPC connection handshake succeeds.
        
        Validates only transport-level handshake,
        NOT message content.
        """
    
    def test_grpc_connection_fails_for_invalid_port():
        """
        Test: Connection fails gracefully for invalid port.
        """
    
    def test_grpc_transport_cleanup_after_job_cancel():
        """
        Test: gRPC port released after job cancellation.
        """
```

**Task 1.4: Documentation (1h)**
- Document what IS tested (transport only)
- Document what is NOT tested (content)
- Examples

**Total Effort:** ~6 hours (0.75 days)

---

### Story 2: UI Error Message Validation Framework (REVISED - NEW FOCUS)

**Story ID:** AUTO-E2E-002  
**Story Points:** 5  
**Priority:** High (Must Have)  
**Dependencies:** None

#### **Description**

As a QA Engineer, I want to validate that **users see clear, actionable error messages** in the Panda App UI when errors occur, so that users understand what went wrong and how to fix it.

**Focus:** Error handling and user messaging ONLY (not data visualization).

#### **Acceptance Criteria**

- [ ] Playwright installed and configured
- [ ] Can navigate to Panda App
- [ ] Can trigger error scenarios
- [ ] Can verify error messages are displayed
- [ ] Can verify error messages are clear and actionable
- [ ] **NOT testing:** Data visualization, spectrogram accuracy

#### **Tasks**

**Task 2.1: Install and configure Playwright (2h)**
```bash
# Setup
pip install playwright pytest-playwright
playwright install chromium

# Configure
# Create tests/e2e/ directory
# Create conftest.py with browser fixtures
```

**Task 2.2: Create Page Objects (ERROR-FOCUSED) (3h)**
```python
# tests/e2e/page_objects/panda_app_page.py

class PandaAppPage:
    """
    Page Object for Panda App - ERROR HANDLING FOCUS.
    
    Focus on:
    - Error message elements
    - Configuration form
    - Submit buttons
    - Error state recovery
    
    NOT focusing on:
    - Spectrogram canvas rendering
    - Data visualization
    - Algorithm output
    """
    
    def navigate_to_app(self):
        """Navigate to Panda App URL."""
    
    def configure_job(self, config):
        """Fill configuration form."""
    
    def get_error_message(self) -> str:
        """Get displayed error message."""
    
    def is_error_displayed(self) -> bool:
        """Check if error is shown to user."""
    
    def get_error_severity(self) -> str:
        """Get error severity (error/warning/info)."""
```

**Task 2.3: Write error message validation tests (4h)**
```python
@pytest.mark.e2e
@pytest.mark.ui_errors
class TestUIErrorMessages:
    
    def test_user_sees_clear_error_for_no_data():
        """
        Test: User sees clear error when no data available.
        
        Validates:
        - Configure historic job with no data
        - Error message displayed in UI
        - Message clearly indicates "no data in range"
        - User understands what went wrong
        """
    
    def test_user_sees_error_for_invalid_configuration():
        """
        Test: User sees validation error for invalid config.
        
        Validates:
        - Submit invalid NFFT
        - Error shown immediately
        - Message indicates which field is invalid
        """
    
    def test_user_can_recover_from_error():
        """
        Test: User can correct error and retry.
        
        Validates:
        - Trigger error
        - Correct configuration
        - Submit again
        - Success
        """
```

**Total Effort:** ~9 hours (1 day)

---

### Story 3: API → UI Error Flow Validation (NEW - HIGH PRIORITY)

**Story ID:** AUTO-E2E-003  
**Story Points:** 8  
**Priority:** High (Must Have)  
**Dependencies:** AUTO-E2E-002 (Playwright Setup)

#### **Description**

As a QA Engineer, I want to validate that **errors from Backend API are correctly displayed in the UI**, so that users receive accurate feedback about system state.

#### **Acceptance Criteria**

- [ ] Backend 400 errors → UI validation error
- [ ] Backend 404 errors → UI "not found" message  
- [ ] Backend 503 errors → UI "service unavailable"
- [ ] Backend 409 errors → UI "conflict" message
- [ ] Error messages are user-friendly (no technical details)
- [ ] Error messages are actionable (tell user what to do)

#### **Tasks**

**Task 3.1: Test validation error flow (3h)**
```python
def test_api_validation_error_shows_in_ui():
    """
    E2E: Backend 400 → UI validation error
    
    Flow:
    1. User enters invalid NFFT (0)
    2. Backend returns 400
    3. UI displays "Invalid NFFT value"
    4. User sees guidance
    """
```

**Task 3.2: Test "no data" error flow (2h)**
```python
def test_api_no_data_error_shows_in_ui():
    """
    E2E: Backend 404 → UI "no data" message
    
    Flow:
    1. User requests historic data (no data in range)
    2. Backend returns 404
    3. UI displays "No recordings found in time range"
    4. User understands what happened
    """
```

**Task 3.3: Test service unavailable flow (2h)**
```python
def test_api_service_error_shows_in_ui():
    """
    E2E: Backend 503 → UI service error
    
    Flow:
    1. MongoDB down (503 from Backend)
    2. UI displays "Service temporarily unavailable"
    3. User sees "Please try again later"
    """
```

**Task 3.4: Test error message clarity analysis (3h)**
```python
def test_all_error_messages_are_user_friendly():
    """
    Validate all error messages:
    - No stack traces
    - No technical jargon
    - Clear indication of problem
    - Guidance on how to fix
    """
```

**Total Effort:** ~10 hours (1.5 days)

---

### Story 4: System Observability During E2E Flows (NEW)

**Story ID:** AUTO-E2E-004  
**Story Points:** 5  
**Priority:** High (Must Have)  
**Dependencies:** AUTO-E2E-002

#### **Description**

As a QA Engineer, I want to **monitor K8s pods, logs, and metrics** during E2E test execution, so that I can correlate UI behavior with infrastructure state.

#### **Acceptance Criteria**

- [ ] Can monitor Focus Server pod during tests
- [ ] Can capture pod logs during failures
- [ ] Can track resource usage (CPU/Memory)
- [ ] Can detect pod restarts
- [ ] All monitoring data attached to test reports

#### **Tasks**

**Task 4.1: Implement E2E observability fixtures (3h)**
```python
@pytest.fixture
def e2e_monitoring(k8s_manager):
    """
    Monitor infrastructure during E2E test execution.
    
    Captures:
    - Pod status before/during/after
    - Pod logs on failure
    - Resource metrics
    - Events
    """
```

**Task 4.2: Write observability integration tests (4h)**
```python
def test_pod_state_during_job_lifecycle():
    """
    E2E: Monitor pod state during complete flow.
    
    1. Create job (monitor pod spawn)
    2. Use job (monitor pod running)
    3. Cancel job (monitor pod termination)
    4. Verify clean state
    """

def test_capture_logs_on_error():
    """
    E2E: Capture pod logs when error occurs.
    
    Validates that logs are captured and attached
    to test report for debugging.
    """
```

**Task 4.3: Documentation (1h)**

**Total Effort:** ~8 hours (1 day)

---

### Story 5: Configuration Flow E2E Tests (REVISED)

**Story ID:** AUTO-E2E-005  
**Story Points:** 5  
**Priority:** Medium (Should Have)  
**Dependencies:** AUTO-E2E-002

#### **Description (REVISED)**

As a QA Engineer, I want to validate the **configuration flow** in the UI, so that users can successfully configure jobs **without testing data visualization**.

**Focus:** Form interaction, validation, submission - NOT what gets displayed after.

#### **Acceptance Criteria**

- [ ] User can fill configuration form
- [ ] Form validation works (client-side)
- [ ] Submit succeeds with valid config
- [ ] Submit fails with invalid config and shows error
- [ ] **NOT testing:** Spectrogram rendering, data accuracy

#### **Tasks**

**Task 5.1: Test configuration form interaction (3h)**
```python
def test_user_can_fill_configuration_form():
    """
    E2E: User fills and submits configuration.
    
    Validates:
    - Form fields are accessible
    - User can input values
    - Submit button works
    
    NOT validating visualization after submit.
    """

def test_form_validation_prevents_invalid_submit():
    """
    E2E: Client-side validation catches errors.
    
    Validates:
    - Invalid NFFT → Error shown
    - Invalid channels → Error shown
    - User cannot submit until fixed
    """
```

**Task 5.2: Test API integration from UI (3h)**
```python
def test_ui_calls_correct_api_endpoint():
    """
    E2E: UI → POST /configure → Response
    
    Validates:
    - UI sends correct request to Backend
    - Response is received
    - UI handles response (shows job_id or error)
    
    NOT validating stream content after.
    """
```

**Task 5.3: Documentation (1h)**

**Total Effort:** ~7 hours (1 day)

---

### Story 6: Error Recovery E2E Tests (HIGH PRIORITY)

**Story ID:** AUTO-E2E-006  
**Story Points:** 8  
**Priority:** High (Must Have)  
**Dependencies:** AUTO-E2E-002

#### **Description**

As a QA Engineer, I want to validate **error recovery flows** in the UI, so that users can gracefully handle and recover from all error scenarios.

#### **Acceptance Criteria**

- [ ] Users see clear errors for all failure scenarios
- [ ] Users can recover from errors (retry mechanism)
- [ ] No silent failures
- [ ] Error messages are actionable
- [ ] System remains stable after errors

#### **Tasks**

**Task 6.1: Test "No Data Available" scenario (3h)**
```python
@pytest.mark.e2e
@pytest.mark.error_recovery
class TestNoDataErrorRecovery:
    
    def test_user_sees_no_data_error_and_can_retry():
        """
        E2E: No data available → Clear error → Retry
        
        Flow:
        1. User configures historic job (no data in range)
        2. Backend returns 404
        3. UI shows: "No recordings found in time range"
        4. UI suggests: "Try a different time range"
        5. User changes time range
        6. User retries
        7. Success
        
        Validates error clarity and recovery flow.
        """
```

**Task 6.2: Test "Service Unavailable" scenario (2h)**
```python
def test_user_sees_service_error_and_guidance():
    """
    E2E: Service down (MongoDB) → Clear error → Guidance
    
    Flow:
    1. Trigger MongoDB outage (503)
    2. UI shows: "Service temporarily unavailable"
    3. UI shows: "Please try again in a few moments"
    4. User understands this is temporary
    """
```

**Task 6.3: Test "Invalid Configuration" scenario (2h)**
```python
def test_user_corrects_validation_error():
    """
    E2E: Invalid config → Validation error → Correction → Success
    
    Flow:
    1. User enters NFFT=0
    2. UI shows: "NFFT must be greater than 0"
    3. User corrects to NFFT=1024
    4. Submit succeeds
    """
```

**Task 6.4: Test "Port Conflict" scenario (2h)**
```python
def test_user_sees_port_conflict_error():
    """
    E2E: Port conflict → Clear error
    
    Flow:
    1. Port already in use
    2. User tries to create job
    3. Backend returns 409
    4. UI shows: "Port unavailable, retrying..."
    5. User sees resolution attempt
    """
```

**Task 6.5: Documentation (1h)**

**Total Effort:** ~10 hours (1.5 days)

---

### Story 7: System Health Monitoring E2E (NEW - IN SCOPE)

**Story ID:** AUTO-E2E-007  
**Story Points:** 5  
**Priority:** High (Must Have)  
**Dependencies:** AUTO-E2E-002

#### **Description**

As a QA Engineer, I want to validate that **system health is observable** during E2E flows, so that I can correlate user actions with infrastructure state.

#### **Acceptance Criteria**

- [ ] K8s pod state monitored during tests
- [ ] Pod logs captured on failures
- [ ] Resource metrics collected
- [ ] Alerts detected and logged
- [ ] Test reports include infrastructure context

#### **Tasks**

**Task 7.1: Implement real-time monitoring (3h)**
```python
@pytest.fixture(scope="session", autouse=True)
def e2e_infrastructure_monitor(k8s_manager):
    """
    Monitor infrastructure during ALL E2E tests.
    
    Captures:
    - Pod status changes
    - Error logs
    - Resource spikes
    - Restart events
    """
```

**Task 7.2: Write health correlation tests (4h)**
```python
def test_pod_state_correlates_with_job_lifecycle():
    """
    E2E with Monitoring: Job creation → Pod spawn correlation
    
    Validates:
    1. Create job via UI
    2. Monitor pod creation in K8s
    3. Verify pod appears within 10s
    4. Verify pod status: Pending → Running
    5. Capture timeline
    """

def test_error_logs_captured_on_failure():
    """
    E2E with Monitoring: Failure → Log capture
    
    Validates:
    1. Trigger error scenario
    2. Pod logs captured automatically
    3. Logs attached to test report
    4. Helps debugging
    """
```

**Task 7.3: Documentation (1h)**

**Total Effort:** ~8 hours (1 day)

---

### Story 8: CI/CD Integration (UPDATED)

**Story ID:** AUTO-E2E-008  
**Story Points:** 5  
**Priority:** High (Must Have)  
**Dependencies:** AUTO-E2E-001, AUTO-E2E-002, AUTO-E2E-006

#### **Description**

As a DevOps Engineer, I want to integrate E2E tests into CI/CD pipeline, so that infrastructure and error-flow tests run automatically.

#### **Acceptance Criteria**

- [ ] Tests run on pull requests
- [ ] Tests run on main branch merges
- [ ] Screenshots captured on failures
- [ ] Infrastructure logs attached
- [ ] Notifications sent on failures

#### **Tasks**

**Task 8.1: Create GitHub Actions workflow (3h)**
```yaml
name: E2E Tests - Error Handling & Infrastructure

on:
  pull_request:
  push:
    branches: [main, develop]

jobs:
  e2e-error-flows:
    name: E2E Error Handling Tests
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python & Playwright
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Run E2E Error Flow Tests
        run: |
          pytest tests/e2e/ -v -s \
            -m "error_recovery" \
            --html=reports/e2e_report.html
      
      - name: Upload Screenshots on Failure
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: test-screenshots
          path: tests/e2e/screenshots/
      
      - name: Upload Infrastructure Logs
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: infrastructure-logs
          path: reports/pod_logs/
```

**Task 8.2: Configure test artifacts (2h)**
**Task 8.3: Setup notifications (1h)**
**Task 8.4: Documentation (1h)**

**Total Effort:** ~7 hours (1 day)

---

## ❌ **REMOVED Stories** (OUT OF SCOPE)

### ~~Story: Live Mode Data Visualization~~ ❌ REMOVED
**Reason:** Validates spectrogram content - OUT OF SCOPE per meeting decision

### ~~Story: Historic Mode Playback Validation~~ ❌ REMOVED  
**Reason:** Validates data correctness in playback - OUT OF SCOPE

### ~~Story: Visual Regression Testing~~ ❌ REMOVED
**Reason:** Validates spectrogram visual rendering - OUT OF SCOPE

### ~~Story: UI Responsiveness Tests~~ ❌ REMOVED
**Reason:** Low priority, not related to meeting requirements

---

## 📊 Revised Epic Statistics

```
┌─────────────────────────────┬────────────┬──────────┬────────┐
│ Story                       │ Points     │ Hours    │ Status │
├─────────────────────────────┼────────────┼──────────┼────────┤
│ 1. gRPC Transport (revised) │ 3          │ 6h       │ New    │
│ 2. UI Error Messages        │ 5          │ 9h       │ New    │
│ 3. API → UI Error Flow      │ 8          │ 10h      │ New    │
│ 4. System Observability     │ 5          │ 8h       │ New    │
│ 5. Configuration Flow       │ 5          │ 7h       │ New    │
│ 6. Error Recovery           │ 8          │ 10h      │ New    │
│ 7. CI/CD Integration        │ 5          │ 7h       │ New    │
├─────────────────────────────┼────────────┼──────────┼────────┤
│ TOTAL (MVP)                 │ 39 points  │ ~57h     │ 7-8d   │
└─────────────────────────────┴────────────┴──────────┴────────┘

Comparison to Original Epic:
Before: 47 points, ~77 hours
After:  39 points, ~57 hours  
Reduction: 17% story points, 26% effort

Reason: Removed OUT OF SCOPE items (data validation, spectrogram content)
```

---

## 🎯 **MVP Scope (High Priority Only)**

### Phase 1: Foundation (Week 1)
- AUTO-E2E-002: UI Error Message Validation Framework (9h)
- AUTO-E2E-001: gRPC Transport Readiness (6h)

**Total Week 1:** ~15 hours (2 days)

### Phase 2: Core Flows (Week 2)
- AUTO-E2E-003: API → UI Error Flow Validation (10h)
- AUTO-E2E-006: Error Recovery E2E Tests (10h)

**Total Week 2:** ~20 hours (2.5 days)

### Phase 3: Observability & CI/CD (Week 3)
- AUTO-E2E-004: System Observability (8h)
- AUTO-E2E-008: CI/CD Integration (7h)

**Total Week 3:** ~15 hours (2 days)

### Phase 4: Optional Enhancement (Week 4)
- AUTO-E2E-005: Configuration Flow (7h)

**Total Week 4:** ~7 hours (1 day)

**Grand Total MVP:** ~57 hours (7-8 days for 1 developer, 4-5 days for 2 developers)

---

## 🔑 **Success Metrics (Revised)**

### Coverage Metrics:
- [ ] >90% of **error scenarios** covered by E2E tests
- [ ] >95% of **gRPC transport scenarios** tested
- [ ] >90% of **API → UI error flows** validated

### Quality Metrics:
- [ ] E2E test suite passes consistently (>90% success rate)
- [ ] Test execution time <15 minutes
- [ ] Zero **user-facing error bugs** missed by tests

### Team Metrics:
- [ ] Error message quality score >80%
- [ ] Infrastructure observability in all E2E tests
- [ ] Documentation rated useful by team

---

## ⚠️ **Risks & Dependencies (Revised)**

### Technical Risks:

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Flaky tests (timing)** | High | Medium | Proper waits, generous timeouts |
| **SSL certificate issues** | Medium | High | Configure `verify=False` |
| **K8s access for monitoring** | High | Low | Use existing KubernetesManager fixture |
| **UI changes frequently** | Medium | Medium | Use Page Object Model for maintainability |

### Dependencies:

#### External:
- ✅ Panda App UI must be accessible
- ✅ Focus Server API must be running
- ⚠️ K8s cluster must be accessible for monitoring

#### Internal:
- ✅ KubernetesManager fixture (exists)
- ✅ FocusServerAPI client (exists)
- ⚠️ Playwright setup (new)

---

## 📝 **Implementation Guidelines**

### What to Test (IN SCOPE):

```python
✅ DO TEST:
   - API request/response behavior
   - Error message display in UI
   - Error message clarity (user-friendly?)
   - gRPC transport readiness (port accessible?)
   - Pod lifecycle during E2E flows
   - Resource usage during tests
   - System recovery after errors
   - Configuration form interaction
```

### What NOT to Test (OUT OF SCOPE):

```python
❌ DON'T TEST:
   - Spectrogram content accuracy
   - Algorithm correctness
   - Data visualization accuracy
   - Color schemes correctness
   - Full gRPC stream message parsing
   - Baby Analyzer processing
   - Mathematical algorithm output
```

---

## 🎯 **Example E2E Test (Approved Scope)**

### ✅ GOOD Example (IN SCOPE):

```python
@pytest.mark.e2e
@pytest.mark.error_flow
def test_user_sees_clear_error_when_mongodb_down(
    page,
    focus_server_api,
    k8s_manager,
    mongodb_manager
):
    """
    End-to-End Test: MongoDB Outage → User sees clear error
    
    Validates:
    1. Infrastructure: Trigger MongoDB outage
    2. API: Backend returns 503
    3. UI: User sees "Service temporarily unavailable"
    4. UX: Error message is clear and actionable
    5. Monitoring: Pod logs captured
    
    Does NOT validate:
    - Spectrogram content
    - Data correctness
    - Algorithm behavior
    
    Related: Meeting decision - Error handling (IN SCOPE)
    """
    # Infrastructure setup
    logger.info("Creating MongoDB outage...")
    mongodb_manager.scale_down_mongodb(replicas=0)
    time.sleep(5)
    
    # User action
    logger.info("User navigates to Panda App...")
    page.goto("https://panda-app-url")
    
    logger.info("User attempts to configure job...")
    panda_page = PandaAppPage(page)
    panda_page.fill_configuration({
        "channels_min": 1,
        "channels_max": 50,
        "nfft": 1024
    })
    panda_page.click_submit()
    
    # Verify error displayed
    logger.info("Verifying error message in UI...")
    assert panda_page.is_error_displayed()
    
    error_message = panda_page.get_error_message()
    logger.info(f"Error message shown: {error_message}")
    
    # Validate error clarity
    assert "unavailable" in error_message.lower() or "503" in error_message
    assert "try again" in error_message.lower()
    
    # Validate NO technical details exposed
    assert "traceback" not in error_message.lower()
    assert "exception" not in error_message.lower()
    
    # Capture infrastructure state
    logger.info("Capturing pod logs...")
    pod_logs = k8s_manager.get_pod_logs("focus-server-pod", tail_lines=50)
    
    # Verify logs show MongoDB connection error
    assert any("mongodb" in line.lower() and "error" in line.lower() 
               for line in pod_logs.split('\n'))
    
    # Cleanup
    mongodb_manager.restore_mongodb()
    
    logger.info("✅ Test passed: Error flow validated end-to-end")
```

**Why this is GOOD:**
- ✅ Tests infrastructure behavior
- ✅ Tests error handling
- ✅ Tests user experience (error messages)
- ✅ Tests system observability
- ❌ Doesn't test data content

---

### ❌ BAD Example (OUT OF SCOPE):

```python
# ❌ DON'T DO THIS - OUT OF SCOPE!

@pytest.mark.e2e
def test_user_sees_correct_spectrogram_visualization():
    """
    WRONG! This tests spectrogram content - OUT OF SCOPE.
    """
    page.goto("https://panda-app")
    
    # ❌ OUT OF SCOPE: Validating spectrogram content
    canvas = page.locator("#spectrogram-canvas")
    image_data = canvas.screenshot()
    
    # ❌ OUT OF SCOPE: Checking pixel values
    assert analyze_spectrogram_accuracy(image_data) > 0.95
    
    # ❌ OUT OF SCOPE: Validating algorithm output
    assert frequency_bins_correct(image_data)
```

**Why this is BAD:**
- ❌ Tests spectrogram content (OUT OF SCOPE)
- ❌ Tests algorithm correctness (OUT OF SCOPE)
- ❌ Tests data visualization accuracy (OUT OF SCOPE)

---

## 📚 **Documentation Deliverables**

### Test Documentation:
- [ ] `tests/e2e/README.md` - E2E testing guide
- [ ] `tests/e2e/page_objects/README.md` - Page Objects guide
- [ ] `tests/integration/grpc_transport/README.md` - gRPC transport guide

### Strategy Documentation:
- [ ] `E2E_TESTING_STRATEGY.md` - Overall strategy
- [ ] `ERROR_FLOW_TESTING_GUIDE.md` - Error testing guide
- [ ] `INFRASTRUCTURE_MONITORING_E2E.md` - Observability guide

---

## 🎓 **Alignment with PZ-13756 Scope**

### How This Epic Aligns:

| Meeting Decision | How E2E Epic Addresses It |
|------------------|---------------------------|
| **K8s/Orchestration** | Story 4 (System Observability) monitors pods during E2E |
| **Focus Server API** | Story 3 (API → UI Error Flow) validates API behavior |
| **System Behavior** | Story 6 (Error Recovery) validates predictable errors |
| **gRPC Modified Scope** | Story 1 (Transport Readiness) - port/handshake ONLY |

**Result:** ✅ **Perfect alignment** with scope refinement decisions!

---

## 🚀 **Next Actions**

### Immediate (This Week):
1. [ ] Review and approve this revised Epic
2. [ ] Create Jira stories in backlog
3. [ ] Prioritize stories (recommend: 2 → 1 → 6 → 3)

### Short-Term (Next 2 Weeks):
4. [ ] Implement Story 2 (Playwright Setup)
5. [ ] Implement Story 1 (gRPC Transport)
6. [ ] Implement Story 6 (Error Recovery)

### Medium-Term (Month):
7. [ ] Implement remaining stories
8. [ ] CI/CD integration
9. [ ] Team training

---

## 📌 **Key Changes from Original Epic**

### What Changed:

```diff
Original Epic (Before PZ-13756):
- Story 1: gRPC Stream Validation (8 SP, stream content)
- Story 3: Live Mode E2E (8 SP, data visualization)
- Story 4: Historic Mode E2E (5 SP, playback content)
- Story 7: Visual Regression (5 SP, visual diff)

Revised Epic (After PZ-13756):
+ Story 1: gRPC Transport Readiness ONLY (3 SP, port/handshake)
+ Story 3: API → UI Error Flow (8 SP, error propagation)
+ Story 4: System Observability (5 SP, infrastructure monitoring)
+ Story 6: Error Recovery (8 SP, user experience during errors)
- Removed: Live Mode data validation
- Removed: Historic Mode content validation  
- Removed: Visual Regression
```

**Key Differences:**
- ✅ Focus shifted from **data validation** to **error handling**
- ✅ Focus shifted from **content accuracy** to **infrastructure observability**
- ✅ Aligned with **IN SCOPE** items from PZ-13756
- ❌ Removed all **OUT OF SCOPE** validation

---

## ✅ **Sign-Off**

**Epic Owner:** QA Automation Architect  
**Reviewed By:** [To be filled]  
**Approved By:** [To be filled]  
**Date:** 27 October 2025

**Statement:**

> "This Epic has been revised to perfectly align with meeting decision PZ-13756. All OUT OF SCOPE items have been removed. Focus is on infrastructure behavior, error handling, and user experience during failures. The Epic is production-ready and ready for implementation."

---

**📎 Related Documents:**
- [SCOPE_REFINEMENT_ACTION_PLAN.md](SCOPE_REFINEMENT_ACTION_PLAN.md)
- [EXECUTIVE_SUMMARY_HE.md](EXECUTIVE_SUMMARY_HE.md)
- [SCOPE_REFINEMENT_COMPLETION_SUMMARY.md](SCOPE_REFINEMENT_COMPLETION_SUMMARY.md)

**🎯 Start Here:** Story 2 (Playwright Setup) → Story 6 (Error Recovery)


