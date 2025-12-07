# Statement of Work (SOW)
## Interrogator Automation Ownership Transfer & Enhancement

**Project Name:** InterrogatorQA Takeover & Modernization  
**Date:** December 06, 2025  
**Author:** Roy Avrahami, QA Team Lead  
**Version:** 1.0  
**Status:** Draft for Approval

---

## 1. Executive Summary

This Statement of Work (SOW) outlines the project for transferring ownership of the **Interrogator Automation Framework (InterrogatorQA)** from the Interrogator Team to the QA Automation Team, and more critically – **building a new layer of functional automation from scratch**.

**Key Finding:** The existing automation suite (`InterrogatorQA`) primarily covers **infrastructure health checks** (service status, resource monitoring, connectivity) but lacks **functional product testing** (data flow validation, signal-to-alert flows, configuration effects, external integrations).

As a result, critical aspects of product functionality – such as **business logic, detection accuracy, data integrity, and operational resilience** – are still tested mostly manually, increasing release risk and slowing feedback cycles.

**Examples of untested Business Logic:**
*   **Detection Accuracy:** Does the system correctly detect and classify events (intrusion, vehicle, digging, fiber cut)?
*   **Alert Generation Rules:** Given a specific signal pattern, does the system generate the correct alert type with proper severity?
*   **Zone Sensitivity:** When sensitivity thresholds are changed, does the detection behavior change accordingly?
*   **Alert Suppression/Filtering:** Are duplicate or noise alerts filtered correctly?
*   **Recording Trigger Logic:** Does the system start/stop recordings at the correct times based on configured rules?
*   **Channel Mapping:** Are events correctly mapped to their geographic location/zone?
*   **Event Correlation:** Are related events from multiple channels correlated into a single incident?
*   **Data Retention Policies:** Is old data purged according to FIFO rules when disk is full?

> **Note:** Need to verify with Interrogator team if any resilience testing (network/power/storage failures) has been performed manually or is documented.

The project aims to:
1. Stabilize and maintain the existing infrastructure automation.
2. **Build comprehensive functional automation** covering the core product logic.
3. Establish a robust CI/CD pipeline with quality gates.

The strategy involves a preliminary learning phase by the QA Team Lead, followed by the recruitment of a dedicated Automation Engineer to execute the long-term roadmap.

## 2. Project Objectives

1.  **Ownership Transfer:** Complete transfer of code ownership and maintenance responsibility to the QA Team.
2.  **Knowledge Retention:** Documenting the complex Interrogator system architecture and testing flows to reduce dependency on specific individuals.
3.  **Infrastructure Stability:** Stabilizing the existing infrastructure test suite (Smoke, Long-term) to achieve >95% pass rate.
4.  **Functional Coverage (NEW):** Building functional automation from scratch to cover:
    *   Data Pipeline validation (Signal → Alert → Recording).
    *   Configuration & State Management.
    *   External Integrations (Focus Server, Control Center).
    *   Fiber Health Monitoring.
    *   Hardware Interaction logic.
5.  **Resilience Testing:** Implementing automated tests for critical failure scenarios (service crashes, storage/network failures, power loss recovery).
6.  **CI/CD Integration:** Fully integrating the framework into the organization's CI/CD pipelines with automated quality gates.

## 3. Scope of Work

### 3.1 Phase 1: Knowledge Acquisition & Preparation (Months 1-2)
*   **Owner:** QA Team Lead (Roy)
*   **Activities:**
    *   Deep dive into the `nc_pz` repository and 12 core services (Supervisor, Preprocessor, etc.).
    *   Setup of local development environments (Python 3.8, RabbitMQ, MongoDB).
    *   Mapping of all existing manual tests vs. automated coverage.
    *   Identification of all critical technical debts (e.g., code duplication in `configurator.py`).
    *   **Recruitment:** Sourcing and interviewing candidates for the Automation Engineer position.

### 3.2 Phase 2: Functional Coverage & Stabilization (Months 3-7)

**Focus:** Building the "Real" automation – testing the product logic across all functional domains.

*   **Owner:** QA Team Lead + New Hire (Onboarding)
*   **Activities:**

    #### Core Functional Coverage (The Missing Layers)
    
    *   **Data Pipeline Validation:**
        *   Design and implement automated tests that validate the complete data flow.
        *   Known input signals → expected alarms and events.
        *   Correct metadata (timestamp, channel, severity, etc.) on generated alerts and recordings.
        *   Data persistence and retrieval (recordings, logs, events).
        *   Convert high-value manual regression scenarios into repeatable automated end-to-end flows:
            *   "Signal-in to alert-out" scenarios.
            *   Configuration changes and effect on system behavior.
            *   Typical workflows used by field and operations teams.
    
    *   **Configuration & State Management:**
        *   Validating that system configuration changes (e.g., sensitivity thresholds, frequency ranges) are applied correctly in real-time.
        *   Verifying state persistence after restarts.
    
    *   **External Integrations:**
        *   Testing the interaction and data contracts with external systems (Focus Server, Control Center, 3rd party integrations).
        *   API validation and contract testing.
    
    *   **Fiber Health Monitoring:**
        *   Simulating fiber cuts and degradations.
        *   Verifying the Fiber Inspector's detection and reporting logic.
    
    *   **Hardware Interaction:**
        *   Validating the control logic for Optical Units and Digitizers (simulation-based).
        *   Verifying that hardware commands are executed correctly.

    #### Resilience & Recovery Automation
    
    > **TBD:** Verify with Interrogator team what resilience scenarios (if any) have been tested manually and documented. Prioritize automation based on field-reported incidents.
    
    *   Implement automated tests for critical field scenarios:
        *   System behavior during component crashes (e.g., service restarts).
        *   Data integrity under storage/network failures.
        *   Automatic recovery after power loss and service restarts.
        *   Behavior during NAS disconnection/reconnection.
        *   MongoDB failover and data consistency.
    *   Define high-level pass criteria:
        *   Maximum recovery time (e.g., <60 seconds for full service restoration).
        *   No data loss or clearly defined, acceptable data-loss bounds.
        *   Alert continuity – no missed events during recovery window.

    #### Performance Under Load
    
    *   Validating system stability and alert latency under high-load scenarios.
    *   Alert Storms handling.
    *   Heavy recording duty cycles.

    #### Documentation
    
    *   Create and maintain:
        *   Architecture overview of the automation framework (layers, fixtures, utilities).
        *   How-to guides for running, debugging, and extending tests.
        *   Scenario documentation for each major functional test flow.

*   **Phase 2 Deliverables:**
    *   Stabilized existing automation suite (minimal flakes, reliable runs).
    *   Initial Functional Test Suite covering key data paths and end-to-end flows.
    *   Resilience test scenarios for at least the top-priority failure modes.
    *   Documentation set for framework usage and extension.

### 3.3 Phase 3: CI/CD & Advanced Capabilities (Months 8-9)
*   **Owner:** Automation Engineer
*   **Activities:**
    *   Integration with Jenkins/GitHub Actions.
    *   Implementation of parallel test execution (pytest-xdist).
    *   Dashboard creation for long-term stability trends.
    *   Python version migration (upgrade from 3.8 to 3.10+).

## 4. Out of Scope
*   Development of the Interrogator product code (C++/Python microservices).
*   Hardware maintenance of lab setups (responsibility of the Interrogator/DevOps team).
*   Manual testing execution for weekly releases (remains with manual QA until automation reaches maturity).

## 5. Deliverables

| ID | Deliverable | Description | Due Date (Est.) |
|----|-------------|-------------|-----------------|
| **D1** | **Knowledge Base** | Comprehensive documentation of the framework and system architecture. | Month 2 |
| **D2** | **Stabilized Infrastructure Suite** | Existing automation with minimal flakes and reliable runs. | Month 4 |
| **D3** | **Functional Test Suite** | New automation covering Data Pipeline, Configuration, External Integrations, and Fiber Health. | Month 6 |
| **D4** | **Resilience Suite** | Automated recovery tests (service crashes, storage/network failures, power loss). | Month 7 |
| **D5** | **Documentation Set** | Architecture overview, how-to guides, scenario documentation. | Month 7 |
| **D6** | **CI/CD Pipeline** | Fully automated pipeline with reporting to Xray. | Month 9 |

## 6. Roles & Responsibilities

### 6.1 QA Team (Roy & New Hire)
*   Project management and timeline tracking.
*   Code development, refactoring, and maintenance.
*   Test script creation and validation.
*   Alerting on regressions.

### 6.2 Interrogator Team (Inbar & Developers)
*   **Knowledge Transfer:** Providing deep-dive sessions on system internals.
*   **Support:** Technical support for complex debugging (Supervisor/Preprocessor issues).
*   **Hardware:** Providing stable hardware environments for testing.
*   **Review:** Code reviews for critical logic changes.

## 7. Assumptions & Dependencies

1.  **Hardware Availability:** Dedicated test setups (Windows 11 Pro machines) will be available for automation development.
2.  **Support Availability:** Interrogator team members will be available for weekly syncs and ad-hoc questions.
3.  **Recruitment:** A qualified Automation Engineer will be recruited within 2-3 months.
4.  **Access:** Full access to `nc_pz` Bitbucket repository, Jira, and Xray is granted.

## 8. Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **High Complexity** | Long learning curve, potential for delays. | Phased learning approach, extensive documentation. |
| **Recruitment Delay** | Delay in Phase 3-4 execution. | QA Lead starts Phase 1 immediately; prioritizing hiring. |
| **Hardware Instability** | Flaky tests, false negatives. | Adding health checks, retry mechanisms, and recovery tests. |
| **Knowledge Gap** | Critical knowledge held by few individuals. | Recording sessions, insisting on written documentation. |

## 9. Resource Estimates

*   **QA Team Lead:** 20% allocation (Management, Architecture, Phase 1 execution).
*   **Automation Engineer:** 100% allocation (Execution Phase 2-4).
*   **Interrogator Team Support:** ~5-10 hours/month (Consultation).

## 10. Acceptance Criteria

The project will be considered successful when:
1.  **Infrastructure automation** (existing) is stable with >95% pass rate.
2.  **Functional automation** covers key data paths: Signal → Alert → Recording flows.
3.  **Configuration changes** are validated automatically (real-time effect, persistence after restart).
4.  **External integrations** (Focus Server, Control Center) have automated contract/API tests.
5.  **Resilience tests** cover top-priority failure modes (service crashes, storage failures, power loss).
6.  Automated tests run nightly with a **pass rate >95%** (excluding genuine bugs).
7.  Documentation is sufficient for a new developer to onboard without assistance.

---

**Approvals:**

_________________________  
**Roy Avrahami**  
QA Team Lead

_________________________  
**Inbar [Last Name]**  
Interrogator Team Lead

_________________________  
**Management**

