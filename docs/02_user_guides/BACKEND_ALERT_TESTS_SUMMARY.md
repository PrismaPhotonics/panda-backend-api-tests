# Backend Alert Tests - Quick Summary

**Date:** November 13, 2025  
**Purpose:** Quick reference for backend alert generation tests

---

## 📊 Test Coverage

### Total Tests: **35**

- ✅ **Positive Scenarios:** 6 tests (PZ-15000 - PZ-15005)
- ❌ **Negative Scenarios:** 8 tests (PZ-15010 - PZ-15017)
- 🔍 **Edge Cases:** 8 tests (PZ-15020 - PZ-15027)
- 📈 **Load Scenarios:** 6 tests (PZ-15030 - PZ-15035)
- ⚡ **Performance:** 7 tests (PZ-15040 - PZ-15046)

---

## 🚀 Quick Run Commands

```bash
# All alert tests
pytest be_focus_server_tests/integration/alerts/ -v

# By category
pytest be_focus_server_tests/integration/alerts/ -m positive -v
pytest be_focus_server_tests/integration/alerts/ -m negative -v
pytest be_focus_server_tests/integration/alerts/ -m edge_cases -v
pytest be_focus_server_tests/integration/alerts/ -m load -v
pytest be_focus_server_tests/integration/alerts/ -m performance -v
```

---

## 📁 Files Created

1. `be_focus_server_tests/integration/alerts/__init__.py`
2. `be_focus_server_tests/integration/alerts/test_alert_generation_positive.py`
3. `be_focus_server_tests/integration/alerts/test_alert_generation_negative.py`
4. `be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py`
5. `be_focus_server_tests/integration/alerts/test_alert_generation_load.py`
6. `be_focus_server_tests/integration/alerts/test_alert_generation_performance.py`
7. `be_focus_server_tests/integration/alerts/README.md`

---

## 📚 Documentation

- **Full Guide (Hebrew):** `docs/02_user_guides/BACKEND_ALERT_TESTS_GUIDE_HE.md`
- **Test README:** `be_focus_server_tests/integration/alerts/README.md`

---

## ⚙️ Requirements

### Dependencies:
- `pika` - RabbitMQ client
- `pymongo` - MongoDB client
- `psutil` - Resource monitoring

### Configuration:
- Uses `config/environments.yaml`
- Requires RabbitMQ and MongoDB connections

---

## ✅ Test Scenarios

### Positive:
- ✅ SD Alert generation
- ✅ SC Alert generation
- ✅ Multiple alerts
- ✅ Different severity levels
- ✅ RabbitMQ processing
- ✅ MongoDB storage

### Negative:
- ❌ Invalid class IDs
- ❌ Invalid severity
- ❌ Invalid DOF range
- ❌ Missing fields
- ❌ Connection failures
- ❌ Invalid alert ID format
- ❌ Duplicate alert IDs

### Edge Cases:
- 🔍 Boundary DOF values
- 🔍 Min/max severity
- 🔍 Zero alerts amount
- 🔍 Very large alert IDs
- 🔍 Concurrent same DOF
- 🔍 Rapid sequential alerts
- 🔍 Maximum/minimum fields

### Load:
- 📈 High volume (1000+ alerts)
- 📈 Sustained load (10+ minutes)
- 📈 Burst load (500 simultaneous)
- 📈 Mixed alert types
- 📈 RabbitMQ capacity
- 📈 MongoDB write load

### Performance:
- ⚡ Response time (< 100ms mean)
- ⚡ Throughput (>= 100 alerts/sec)
- ⚡ Latency (< 50ms mean)
- ⚡ Resource usage (CPU < 80%)
- ⚡ End-to-end (< 200ms)
- ⚡ RabbitMQ (< 10ms publish)
- ⚡ MongoDB (< 20ms write)

---

**Version:** 1.0.0  
**Last Updated:** November 13, 2025

