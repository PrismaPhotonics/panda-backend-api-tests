# Automation Improvement Work Plan

**Date:** December 9, 2025  
**Objective:** Address coverage gaps, fix configuration misalignments, and integrate recent PZ changes into the Focus Server automation framework.

---

## 🟢 Phase 1: Immediate Fixes & Configuration Alignment (Quick Wins)
**Goal:** Fix known bugs in test logic and enable ignored test suites.

1.  **Enable Stress Test Suite**
    *   **Action:** Remove `stress` directory from `norecursedirs` in `pytest.ini`.
    *   **Reason:** Currently, stress tests are completely ignored by the test runner.

2.  **Fix Channel Range Validation Logic**
    *   **Action:** Update `be_focus_server_tests/integration/api/test_prelaunch_validations.py`.
    *   **Details:**
        *   Change default max channel assumption from `2500` to `2222` (matching `usersettings.new_production_client.json`).
        *   Change logic from `logger.warning` to `pytest.fail` or `assert` when the server accepts invalid channels.
        *   Ensure the test actually fails if the server doesn't enforce the 2222 limit.

3.  **Update Load Test Defaults**
    *   **Action:** Update `HistoricInvestigationConfig` in `be_focus_server_tests/load/test_historic_investigation_load_constraints.py` and other load tests.
    *   **Details:**
        *   Set `CHANNELS_MAX` to match production usage (e.g., range 11-109 or max 2222).
        *   Set `FREQUENCY_MAX` to `1000` Hz (was 500 Hz).
        *   Add coverage for different `NFFT` options defined in client settings.

---

## 🟡 Phase 2: Performance & API Test Modernization
**Goal:** Unblock skipped performance tests and ensure they run against the *actual* available APIs.

4.  **Refactor Performance Tests (High Priority)**
    *   **Action:** Modify `be_focus_server_tests/integration/performance/test_performance_high_priority.py`.
    *   **Details:**
        *   The tests currently depend on `POST /config/{task_id}` which returns 404.
        *   **Refactor:** Switch these tests to use the working `POST /configure` API.
        *   **Metric Enforcement:** Once working, enforce the P95/P99 latency thresholds (target: ~300ms).

5.  **Implement Backward-Compatible Metadata/Waterfall Tests**
    *   **Action:** Create new test files or update existing ones in `be_focus_server_tests/integration/api/`.
    *   **Details:**
        *   Keep the "Future API" tests skipped.
        *   Add active tests for the *current* endpoints: `GET /metadata/{job_id}` and existing waterfall endpoints.
        *   Ensure we have coverage for the API as it exists today on staging/prod.

---

## 🔵 Phase 3: PZ Integration & Regression (New)
**Goal:** Verify recent changes in the PZ repository (Heatmap revert & logic changes).

6.  **Heatmap Recorder Configuration Regression**
    *   **Action:** Add/Update tests to verify Heatmap behavior.
    *   **Details:**
        *   Recent PZ commits reverted PR 1455 and changed `heatMapSummary.json` and `autocfg` parameters.
        *   Create a regression test that verifies the Focus Server loads the updated configuration correctly without errors during startup or job initiation.
        *   Verify that `autocfg` loads successfully despite the removal of modules in `sv_modules.py`.

7.  **Data Summary & Msgbus Validation**
    *   **Action:** Update Data Quality tests.
    *   **Details:**
        *   Align validation logic with changes in `pzpy/data/data_summary.py`.
        *   Ensure tests handle the stricter `dtype` checks introduced in `fix/msgbus-check-dtype`.

---

## 🔴 Phase 4: Infrastructure Resilience (Complex)
**Goal:** Enable critical outage tests that are currently skipped.

8.  **Enable MongoDB Outage Tests**
    *   **Action:** Implement a CI-compatible network blocking mechanism.
    *   **Strategy:**
        *   Instead of relying on node-level `iptables` (which requires SSH/root), use a **Kubernetes NetworkPolicy** or a sidecar proxy approach to simulate the outage.
        *   Update `be_focus_server_tests/performance/test_mongodb_outage_resilience.py` to use this new mechanism so it can run in the automated pipeline.

---

## 📅 Execution Schedule

| Task | Priority | Estimated Time | Owner |
| :--- | :--- | :--- | :--- |
| **Phase 1: Immediate Fixes** | Critical | 1 Day | Automation Team |
| **Phase 2: Performance Modernization** | High | 2-3 Days | Automation Team |
| **Phase 3: PZ Regression** | Medium | 2 Days | Automation Team |
| **Phase 4: Resilience Infra** | Low (Long term) | 5 Days | DevOps + QA |

