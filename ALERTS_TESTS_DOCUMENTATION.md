# Complete Alert Tests Documentation

This document provides a comprehensive list of all alert tests that exist in the automation project.

---

## 📋 Table of Contents

1. [Backend Integration Tests](#backend-integration-tests)
   - [Positive Scenarios](#positive-scenarios)
   - [Negative Scenarios](#negative-scenarios)
   - [Edge Cases](#edge-cases)
   - [Load Scenarios](#load-scenarios)
   - [Performance Scenarios](#performance-scenarios)
   - [Investigation Tests](#investigation-tests)
2. [Frontend Tests](#frontend-tests)
3. [Test Helpers](#test-helpers)

---

## Backend Integration Tests

Location: `be_focus_server_tests/integration/alerts/`

### Positive Scenarios

**File:** `test_alert_generation_positive.py`

| Test ID | Test Name | Description |
|---------|-----------|-------------|
| PZ-15000 | `test_successful_sd_alert_generation` | Verify SD (Spatial Distribution) alerts can be successfully generated and processed |
| PZ-15001 | `test_successful_sc_alert_generation` | Verify SC (Single Channel) alerts can be successfully generated and processed |
| PZ-15002 | `test_multiple_alerts_generation` | Verify multiple alerts can be generated simultaneously without conflicts |
| PZ-15003 | `test_different_severity_levels` | Verify alerts with different severity levels (1, 2, 3) are correctly generated |
| PZ-15004 | `test_alert_processing_via_rabbitmq` | Verify alerts are correctly processed through RabbitMQ message queue system |

**Total:** 5 tests

---

### Negative Scenarios

**File:** `test_alert_generation_negative.py`

| Test ID | Test Name | Description |
|---------|-----------|-------------|
| PZ-15010 | `test_invalid_class_id` | Verify alerts with invalid class IDs are rejected |
| PZ-15011 | `test_invalid_severity` | Verify alerts with invalid severity levels are rejected |
| PZ-15012 | `test_invalid_dof_range` | Verify alerts with invalid DOF (Distance on Fiber) values are rejected |
| PZ-15013 | `test_missing_required_fields` | Verify alerts with missing required fields are rejected |
| PZ-15014 | `test_rabbitmq_connection_failure` | Verify system handles RabbitMQ connection failures gracefully |
| PZ-15015 | `test_mongodb_connection_failure` | **SKIPPED** - Alerts are NOT stored in MongoDB |
| PZ-15016 | `test_invalid_alert_id_format` | Verify alerts with invalid alert ID formats are rejected or handled appropriately |
| PZ-15017 | `test_duplicate_alert_ids` | Verify duplicate alert IDs are handled appropriately |

**Total:** 7 tests (1 skipped)

---

### Edge Cases

**File:** `test_alert_generation_edge_cases.py`

| Test ID | Test Name | Description |
|---------|-----------|-------------|
| PZ-15020 | `test_boundary_dof_values` | Verify alerts with boundary DOF values (0, 1, 2221, 2222) are handled correctly |
| PZ-15021 | `test_min_max_severity` | Verify alerts with minimum (1) and maximum (3) severity are handled correctly |
| PZ-15022 | `test_zero_alerts_amount` | Verify alerts with alertsAmount = 0 are handled appropriately |
| PZ-15023 | `test_very_large_alert_id` | Verify alerts with very long alert IDs (1000+ characters) are handled correctly |
| PZ-15024 | `test_concurrent_alerts_same_dof` | Verify multiple alerts with the same DOF can be processed concurrently |
| PZ-15025 | `test_rapid_sequential_alerts` | Verify rapid sequential alerts are processed correctly without loss |
| PZ-15026 | `test_alert_maximum_fields` | Verify alerts with all fields set to maximum values are processed correctly |
| PZ-15027 | `test_alert_minimum_fields` | Verify alerts with only required fields are processed correctly |

**Total:** 8 tests

---

### Load Scenarios

**File:** `test_alert_generation_load.py`

| Test ID | Test Name | Description |
|---------|-----------|-------------|
| PZ-15030 | `test_high_volume_load` | Verify system can handle high volume of alerts (1000+) without degradation |
| PZ-15031 | `test_sustained_load` | Verify system can handle sustained load over extended period (10+ minutes) |
| PZ-15032 | `test_burst_load` | Verify system can handle sudden burst of alerts (500 simultaneous) without failures |
| PZ-15033 | `test_mixed_alert_types_load` | Verify system can handle mixed alert types (SD, SC, different severities) under load |
| PZ-15034 | `test_rabbitmq_queue_capacity` | Verify RabbitMQ queues can handle high volume without overflow or message loss |
| PZ-15035 | `test_mongodb_write_load` | **SKIPPED** - Alerts are NOT stored in MongoDB |

**Total:** 5 tests (1 skipped)

---

### Performance Scenarios

**File:** `test_alert_generation_performance.py`

| Test ID | Test Name | Description | Requirements |
|---------|-----------|-------------|--------------|
| PZ-15040 | `test_alert_response_time` | Verify alert generation response time meets requirements | Mean < 100ms, P95 < 200ms, P99 < 500ms |
| PZ-15041 | `test_alert_throughput` | Verify alert generation throughput meets requirements | >= 100 alerts/second |
| PZ-15042 | `test_alert_latency` | Verify alert generation latency meets requirements | Mean < 50ms, P95 < 100ms |
| PZ-15043 | `test_resource_usage` | Verify alert generation does not cause excessive resource usage | CPU < 80%, Memory increase < 500MB |
| PZ-15044 | `test_end_to_end_performance` | Verify end-to-end performance from alert creation to storage | Mean < 200ms, P95 < 500ms |
| PZ-15045 | `test_rabbitmq_performance` | Verify RabbitMQ performance in alert processing | Publish time < 10ms, Consume time < 50ms |
| PZ-15046 | `test_mongodb_performance` | **SKIPPED** - Alerts are NOT stored in MongoDB |

**Total:** 6 tests (1 skipped)

---

### Investigation Tests

**File:** `test_alert_logs_investigation.py`

| Test Name | Description |
|-----------|-------------|
| `test_investigate_alert_logs` | Investigation test to find where alert logs appear in Kubernetes. Lists pods, checks Focus Server logs, RabbitMQ logs, sends test alert, and monitors logs |

**File:** `test_deep_alert_logs_investigation.py`

| Test ID | Test Name | Description |
|---------|-----------|-------------|
| PZ-15051 | `test_deep_investigate_alert_logs` | Comprehensive investigation of alert logs across all components: Focus Server, Prisma Web App API, RabbitMQ, gRPC Jobs, MongoDB, RabbitMQ Management API |

**Total:** 2 tests

---

## Frontend Tests

Location: `fe_panda_tests/tests/panda/sanity/alerts/`

### TestAlerts.py

| Test Name | Description |
|-----------|-------------|
| `test_alerts_sc_all_severities` | Test SC alerts with all severity levels (red/yellow/white) and verify details on sidebar |
| `test_alerts_sd_all_severities` | Test SD alerts with all severity levels (red/yellow/white) and verify details on sidebar |
| `test_alert_wait_till_finish` | Test alert wait functionality until finish |
| `test_alert_bell` | Test alert bell notification (red dot) |

**Total:** 4 tests

---

### TestAlertsFilter.py

| Test Name | Description |
|-----------|-------------|
| `test_alert_filter_basic` | Test basic alert filtering with importance, event types, status, time range, sensor range, and report line range |
| `test_alert_filter_dates_with_no_alerts` | Test alert filtering with date range that has no alerts |
| `test_alert_filter_cancel` | Test canceling alert filter |
| `test_alert_filter_cancel_with_x` | Test canceling alert filter using X button |

**Total:** 4 tests

---

### TestAlertsNotes.py

| Test Name | Description |
|-----------|-------------|
| `test_random_alert_note_heb_and_eng` | Test adding Hebrew and English notes to alerts |
| `test_alert_note_long_msg` | Test adding long message (1100 characters) as note to alert |
| `test_alert_note_many_notes` | Test adding multiple notes (30) to a specific alert |
| `test_alert_note_cancel_note` | Test canceling note addition |

**Total:** 4 tests

---

### TestAlertsGrouping.py

| Test Name | Description |
|-----------|-------------|
| `test_alerts_sd_grouping` | Test SD alert grouping functionality with time range and sensor difference |
| `test_alerts_sc_grouping` | Test SC alert grouping functionality with time range and sensor difference |

**Total:** 2 tests

---

## Test Helpers

**File:** `be_focus_server_tests/integration/alerts/alert_test_helpers.py`

### Helper Functions:

1. **`authenticate_session(base_url, username, password)`**
   - Authenticate and return a session with access-token cookie

2. **`send_alert_via_api(config_manager, alert_payload, ...)`**
   - Send an alert via the Prisma Web App API push-to-rabbit endpoint

3. **`create_alert_payload(class_id, dof_m, severity, alert_id, alerts_amount)`**
   - Create a standard alert payload dictionary

4. **`get_alerts_by_time_range(config_manager, start_time, end_time, ...)`**
   - Get alerts created within a time range

5. **`delete_alerts(config_manager, alert_ids, ...)`**
   - Delete alerts by their IDs

6. **`cleanup_test_alerts(config_manager, start_time, end_time, ...)`**
   - Cleanup all alerts created during test execution

---

## Configuration

**File:** `be_focus_server_tests/integration/alerts/conftest.py`

### Fixtures:

- **`alert_test_session_cleanup`** - Automatic cleanup fixture for alert tests (session scope)

---

## Summary Statistics

### Backend Integration Tests:
- **Positive Scenarios:** 5 tests
- **Negative Scenarios:** 7 tests (1 skipped)
- **Edge Cases:** 8 tests
- **Load Scenarios:** 5 tests (1 skipped)
- **Performance Scenarios:** 6 tests (1 skipped)
- **Investigation Tests:** 2 tests

**Backend Total:** 33 tests (4 skipped)

### Frontend Tests:
- **Basic Alert Tests:** 4 tests
- **Alert Filter Tests:** 4 tests
- **Alert Notes Tests:** 4 tests
- **Alert Grouping Tests:** 2 tests

**Frontend Total:** 14 tests

### Grand Total: 47 tests (4 skipped)

---

## Test Execution

### Run All Backend Alert Tests:
```bash
pytest be_focus_server_tests/integration/alerts/ -v
```

### Run All Frontend Alert Tests:
```bash
pytest fe_panda_tests/tests/panda/sanity/alerts/ -v
```

### Run Specific Test Categories:
```bash
# Positive scenarios
pytest be_focus_server_tests/integration/alerts/test_alert_generation_positive.py -v

# Negative scenarios
pytest be_focus_server_tests/integration/alerts/test_alert_generation_negative.py -v

# Edge cases
pytest be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py -v

# Load scenarios
pytest be_focus_server_tests/integration/alerts/test_alert_generation_load.py -v

# Performance scenarios
pytest be_focus_server_tests/integration/alerts/test_alert_generation_performance.py -v
```

### Run with Markers:
```bash
# Positive tests only
pytest be_focus_server_tests/integration/alerts/ -m positive -v

# Negative tests only
pytest be_focus_server_tests/integration/alerts/ -m negative -v

# Edge cases only
pytest be_focus_server_tests/integration/alerts/ -m edge_case -v

# Load tests only
pytest be_focus_server_tests/integration/alerts/ -m load -v

# Performance tests only
pytest be_focus_server_tests/integration/alerts/ -m performance -v
```

---

## Alert Payload Format

```json
{
  "alertsAmount": 1,
  "dofM": 4163,
  "classId": 104,
  "severity": 3,
  "alertIds": ["test-123.4567"]
}
```

### Alert Types:
- **103** = SC (Single Channel)
- **104** = SD (Spatial Distribution)

### Severity Levels:
- **1** = Low (White)
- **2** = Medium (Yellow)
- **3** = High (Red)

### DOF Range:
- **Min:** 0 meters
- **Max:** 2222 meters (SensorsRange)

---

## RabbitMQ Configuration

- **Exchange:** `prisma`
- **Routing Keys:**
  - `Algorithm.AlertReport.MLGround`
  - `Algorithm.AlertReport.Pulse`
  - `Algorithm.AlertReport.FiberCut`
  - `Algorithm.AlertReport`

---

## Notes

- Some tests require actual RabbitMQ and MongoDB connections
- Performance tests may take longer to execute
- Load tests are marked with `@pytest.mark.slow`
- Tests use `@pytest.mark.skipif` for optional dependencies (pika)
- MongoDB-related tests are skipped as alerts are NOT stored in MongoDB
- Tests use automatic cleanup fixtures to remove test alerts after execution

---

**Document Generated:** 2025-01-27  
**Total Tests Documented:** 47 tests (4 skipped)

