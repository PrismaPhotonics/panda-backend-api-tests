# Integration Tests - Alerts

**Backend Alert Generation and Processing Tests**

---

## 📋 Overview

This directory contains comprehensive tests for alert generation and processing from the Backend (BE) system.

### Test Categories:

1. **Positive Scenarios** (`test_alert_generation_positive.py`)
   - Successful alert generation
   - Different alert types (SD, SC)
   - Multiple alerts
   - Different severity levels
   - RabbitMQ processing

2. **Negative Scenarios** (`test_alert_generation_negative.py`)
   - Invalid class IDs
   - Invalid severity levels
   - Invalid DOF ranges
   - Missing required fields
   - Connection failures
   - Invalid alert ID formats
   - Duplicate alert IDs

3. **Edge Cases** (`test_alert_generation_edge_cases.py`)
   - Boundary DOF values
   - Min/max severity
   - Zero alerts amount
   - Very large alert IDs
   - Concurrent alerts with same DOF
   - Rapid sequential alerts
   - Maximum/minimum fields

4. **Load Scenarios** (`test_alert_generation_load.py`)
   - High volume load
   - Sustained load
   - Burst load
   - Mixed alert types load
   - RabbitMQ queue capacity

5. **Performance Scenarios** (`test_alert_generation_performance.py`)
   - Response time
   - Throughput
   - Latency
   - Resource usage
   - End-to-end performance
   - RabbitMQ performance

---

## 🎯 Test Coverage

### Xray Test Cases:

- **PZ-14933** - PZ-14937: Positive scenarios
- **PZ-14938** - PZ-14944: Negative scenarios
- **PZ-14945** - PZ-14952: Edge cases
- **PZ-14953** - PZ-14957: Load scenarios
- **PZ-14958** - PZ-14963: Performance scenarios

---

## 🚀 Running Tests

### Run all alert tests:
```bash
pytest be_focus_server_tests/integration/alerts/ -v
```

### Run investigation test (to find where logs are):
```bash
pytest be_focus_server_tests/integration/alerts/test_alert_logs_investigation.py -v -s
```

This test will:
1. List all pods
2. Check Focus Server logs
3. Check RabbitMQ logs
4. Send a test alert
5. Monitor logs after sending
6. Create a detailed report

### Run specific category:
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

### Run with markers:
```bash
# Positive tests only
pytest be_focus_server_tests/integration/alerts/ -m positive -v

# Negative tests only
pytest be_focus_server_tests/integration/alerts/ -m negative -v

# Edge cases only
pytest be_focus_server_tests/integration/alerts/ -m edge_cases -v

# Load tests only
pytest be_focus_server_tests/integration/alerts/ -m load -v

# Performance tests only
pytest be_focus_server_tests/integration/alerts/ -m performance -v
```

---

## 📊 Test Requirements

### Dependencies:
- `pika` - For RabbitMQ tests
- `psutil` - For resource monitoring
- `pymongo` - For MongoDB tests

### Configuration:
Tests use configuration from `config/environments.yaml`:
- RabbitMQ connection settings
- MongoDB connection settings
- Site ID (`prisma-210-1000`)

---

## 🔧 Implementation Notes

### Alert Payload Format:
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
- **1** = Low
- **2** = Medium
- **3** = High

### RabbitMQ:
- **Exchange:** `prisma`
- **Routing Keys:**
  - `Algorithm.AlertReport.MLGround`
  - `Algorithm.AlertReport.Pulse`
  - `Algorithm.AlertReport.FiberCut`
  - `Algorithm.AlertReport`

---

## 📝 Notes

- Some tests require actual RabbitMQ and MongoDB connections
- Performance tests may take longer to execute
- Load tests are marked with `@pytest.mark.slow`
- Tests use `@pytest.mark.skipif` for optional dependencies

---

**Author:** QA Automation Architect  
**Date:** 2025-11-13  
**Version:** 1.0.0

