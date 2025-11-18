# Alert Tests - Xray IDs

**Date:** 2025-01-27  
**Status:** ✅ Updated

---

## 📊 Summary

**Xray IDs:** PZ-14933 to PZ-14963 (31 tests)  
**Status:** ✅ All tests exist and updated with correct Xray IDs

---

## ✅ Tests Location

### 📍 Location
All tests are located in: `be_focus_server_tests/integration/alerts/`

### 📁 Files:
1. `test_alert_generation_positive.py` - Positive tests (5 tests)
2. `test_alert_generation_negative.py` - Negative tests (7 tests)
3. `test_alert_generation_edge_cases.py` - Edge cases (8 tests)
4. `test_alert_generation_load.py` - Load tests (5 tests)
5. `test_alert_generation_performance.py` - Performance tests (6 tests)

---

## 📋 Xray IDs List

### Positive Tests (5 tests)

| Xray ID | Test Name | File |
|---------|-----------|------|
| **PZ-14933** | Alert Generation - Successful SD Alert | `test_alert_generation_positive.py` |
| **PZ-14934** | Alert Generation - Successful SC Alert | `test_alert_generation_positive.py` |
| **PZ-14935** | Alert Generation - Multiple Alerts | `test_alert_generation_positive.py` |
| **PZ-14936** | Alert Generation - Different Severity Levels | `test_alert_generation_positive.py` |
| **PZ-14937** | Alert Generation - Alert Processing via RabbitMQ | `test_alert_generation_positive.py` |

### Negative Tests (7 tests)

| Xray ID | Test Name | File |
|---------|-----------|------|
| **PZ-14938** | Alert Generation - Invalid Class ID | `test_alert_generation_negative.py` |
| **PZ-14939** | Alert Generation - Invalid Severity | `test_alert_generation_negative.py` |
| **PZ-14940** | Alert Generation - Invalid DOF Range | `test_alert_generation_negative.py` |
| **PZ-14941** | Alert Generation - Missing Required Fields | `test_alert_generation_negative.py` |
| **PZ-14942** | Alert Generation - RabbitMQ Connection Failure | `test_alert_generation_negative.py` |
| **PZ-14943** | Alert Generation - Invalid Alert ID Format | `test_alert_generation_negative.py` |
| **PZ-14944** | Alert Generation - Duplicate Alert IDs | `test_alert_generation_negative.py` |

### Edge Cases (8 tests)

| Xray ID | Test Name | File |
|---------|-----------|------|
| **PZ-14945** | Alert Generation - Boundary DOF Values | `test_alert_generation_edge_cases.py` |
| **PZ-14946** | Alert Generation - Minimum/Maximum Severity | `test_alert_generation_edge_cases.py` |
| **PZ-14947** | Alert Generation - Zero Alerts Amount | `test_alert_generation_edge_cases.py` |
| **PZ-14948** | Alert Generation - Very Large Alert ID | `test_alert_generation_edge_cases.py` |
| **PZ-14949** | Alert Generation - Concurrent Alerts with Same DOF | `test_alert_generation_edge_cases.py` |
| **PZ-14950** | Alert Generation - Rapid Sequential Alerts | `test_alert_generation_edge_cases.py` |
| **PZ-14951** | Alert Generation - Alert with Maximum Fields | `test_alert_generation_edge_cases.py` |
| **PZ-14952** | Alert Generation - Alert with Minimum Fields | `test_alert_generation_edge_cases.py` |

### Load Tests (5 tests)

| Xray ID | Test Name | File |
|---------|-----------|------|
| **PZ-14953** | Alert Generation - High Volume Load | `test_alert_generation_load.py` |
| **PZ-14954** | Alert Generation - Sustained Load | `test_alert_generation_load.py` |
| **PZ-14955** | Alert Generation - Burst Load | `test_alert_generation_load.py` |
| **PZ-14956** | Alert Generation - Mixed Alert Types Load | `test_alert_generation_load.py` |
| **PZ-14957** | Alert Generation - RabbitMQ Queue Capacity | `test_alert_generation_load.py` |

### Performance Tests (6 tests)

| Xray ID | Test Name | File |
|---------|-----------|------|
| **PZ-14958** | Alert Generation - Response Time | `test_alert_generation_performance.py` |
| **PZ-14959** | Alert Generation - Throughput | `test_alert_generation_performance.py` |
| **PZ-14960** | Alert Generation - Latency | `test_alert_generation_performance.py` |
| **PZ-14961** | Alert Generation - Resource Usage | `test_alert_generation_performance.py` |
| **PZ-14962** | Alert Generation - End-to-End Performance | `test_alert_generation_performance.py` |
| **PZ-14963** | Alert Generation - RabbitMQ Performance | `test_alert_generation_performance.py` |

---

## 📊 Statistics

| Category | Tests | Xray IDs |
|----------|-------|----------|
| **Positive Tests** | 5 | PZ-14933 to PZ-14937 |
| **Negative Tests** | 7 | PZ-14938 to PZ-14944 |
| **Edge Cases** | 8 | PZ-14945 to PZ-14952 |
| **Load Tests** | 5 | PZ-14953 to PZ-14957 |
| **Performance Tests** | 6 | PZ-14958 to PZ-14963 |
| **Total** | **31** | **PZ-14933 to PZ-14963** |

---

## ✅ Conclusion

**All tests exist and are correctly mapped to Xray IDs!**

- ✅ **31 tests** with correct Xray IDs (PZ-14933 to PZ-14963)
- ✅ All tests located in `be_focus_server_tests/integration/alerts/`
- ✅ All Xray markers updated in test files

---

## 📍 File Locations

```
be_focus_server_tests/integration/alerts/
├── test_alert_generation_positive.py      (5 tests: PZ-14933 to PZ-14937)
├── test_alert_generation_negative.py       (7 tests: PZ-14938 to PZ-14944)
├── test_alert_generation_edge_cases.py     (8 tests: PZ-14945 to PZ-14952)
├── test_alert_generation_load.py          (5 tests: PZ-14953 to PZ-14957)
└── test_alert_generation_performance.py   (6 tests: PZ-14958 to PZ-14963)
```

---

**Date:** 2025-01-27  
**Version:** 2.0  
**Status:** ✅ All Xray IDs updated

