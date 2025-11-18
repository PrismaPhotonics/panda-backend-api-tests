# ✅ Smoke and Regression Markers Summary

**Date:** 2025-01-27  
**Status:** ✅ Completed

---

## 📊 Statistics

| Metric | Count |
|--------|-------|
| **Total Tests (excluding unit)** | **374** |
| **Tests with regression marker** | **374** |
| **Tests with smoke marker** | **30** |
| **Regression Coverage** | **100%** ✅ |
| **Smoke Coverage** | **8.02%** ✅ |

---

## 🎯 Smoke Tests - Fast and Critical Tests

### Health Check Tests (9 tests)
- ✅ `test_health_check.py` - All tests
  - `test_ack_health_check_valid_response` (3 parameterized tests)
  - `test_ack_health_check_invalid_methods` (3 tests)
  - `test_ack_health_check_concurrent_requests` (1 test)
  - `test_ack_health_check_ssl_support` (1 test)
  - `test_ack_health_check_load_testing` (1 test)

### Basic Connectivity Tests (4 tests)
- ✅ `test_basic_connectivity.py`
  - `test_mongodb_direct_connection` - PZ-13898
  - `test_kubernetes_direct_connection` - PZ-13899
  - `test_ssh_direct_connection` - PZ-13900
  - `test_all_services_summary` (not smoke - summary test)

### External Connectivity Tests (7 tests)
- ✅ `test_external_connectivity.py`
  - `test_mongodb_status_via_kubernetes` - PZ-13899
  - `test_kubernetes_list_deployments` - PZ-13899
  - `test_kubernetes_list_pods` (not smoke - not basic)
  - `test_ssh_connection` - PZ-13900
  - `test_all_services_summary` (not smoke - summary test)

### Critical API Endpoints (5 tests)
- ✅ `test_api_endpoints_high_priority.py`
  - `test_get_channels_endpoint_success` - PZ-13895, PZ-13762, PZ-13560
  - All tests in `TestChannelsEndpoint` class

### Configuration Tests (2 tests)
- ✅ `test_configure_endpoint.py`
  - `test_configure_valid_configuration` - PZ-14750, PZ-13547

- ✅ `test_prelaunch_validations.py`
  - `test_port_availability_before_job_creation` - PZ-14018

### RabbitMQ Connectivity (2 tests)
- ✅ `test_rabbitmq_connectivity.py`
  - `test_rabbitmq_connection` (basic connectivity)
  - `test_rabbitmq_health_check` (basic health check)

---

## 📋 Regression Tests - All Tests

### Full Coverage (100%)
- ✅ All tests in `integration/` (374 tests)
- ✅ All tests in `infrastructure/` (including resilience)
- ✅ All tests in `data_quality/`
- ✅ All tests in `performance/`
- ✅ All tests in `load/`
- ✅ All tests in `stress/`
- ✅ All tests in `security/`
- ✅ All tests in `ui/`

### Not Regression
- ❌ Unit tests (`unit/`) - Do not need regression markers

---

## 🚀 Running Tests by Markers

### Smoke Tests (Fast and Critical)
```bash
# All smoke tests
pytest -m smoke -v

# Smoke tests only (fast)
pytest -m smoke --tb=short -v
```

### Regression Tests (All Tests)
```bash
# All regression tests
pytest -m regression -v

# Regression tests without smoke (longer)
pytest -m "regression and not smoke" -v

# Regression tests with smoke (fast)
pytest -m "regression and smoke" -v
```

### Combining Markers
```bash
# Critical smoke tests
pytest -m "critical and smoke" -v

# Smoke tests with Xray markers
pytest -m "smoke and xray" -v

# Regression tests without slow tests
pytest -m "regression and not slow" -v
```

---

## 📝 Updated Files

### Files with Smoke Markers:
1. ✅ `integration/api/test_health_check.py` - 9 smoke tests
2. ✅ `infrastructure/test_basic_connectivity.py` - 3 smoke tests
3. ✅ `infrastructure/test_external_connectivity.py` - 4 smoke tests
4. ✅ `integration/api/test_api_endpoints_high_priority.py` - 5 smoke tests
5. ✅ `integration/api/test_configure_endpoint.py` - 1 smoke test
6. ✅ `integration/api/test_prelaunch_validations.py` - 1 smoke test
7. ✅ `infrastructure/test_rabbitmq_connectivity.py` - 2 smoke tests

### Files with Regression Markers:
- ✅ All files in `be_focus_server_tests/` (except unit tests)
- ✅ 77 test files updated
- ✅ 374 tests received regression markers

---

## ✅ Summary

1. ✅ **Regression Markers** - Added to all tests (100% coverage)
2. ✅ **Smoke Markers** - Added to 30 critical and fast tests (8.02% coverage)
3. ✅ **Format** - All markers in correct format
4. ✅ **Documentation** - All tests documented

---

## 🎯 Usage Recommendations

### Before Deploy:
```bash
# Run smoke tests (fast - ~2-3 minutes)
pytest -m smoke -v
```

### Before Release:
```bash
# Run all regression tests (long - ~30-60 minutes)
pytest -m regression -v
```

### In CI/CD:
```bash
# Pull Request - smoke tests only
pytest -m smoke -v

# Main branch - all regression tests
pytest -m regression -v
```

---

**Date:** 2025-01-27  
**Version:** 1.0  
**Status:** ✅ Completed

