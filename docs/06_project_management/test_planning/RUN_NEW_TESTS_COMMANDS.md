# Run New Tests Commands

**Date:** 2025-11-09  
**Purpose:** Commands to run only the 41 new tests created

---

## 🎯 Quick Commands

### Run All New Tests (41 tests)
```bash
pytest tests/integration/security/ tests/integration/error_handling/ tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py tests/integration/load/ tests/integration/data_quality/ -v
```

### Run by Category

#### Security Tests (10 tests)
```bash
pytest tests/integration/security/ -v -m security
```

#### Error Handling Tests (8 tests)
```bash
pytest tests/integration/error_handling/ -v -m error_handling
```

#### Performance Tests (10 tests - NEW files only)
```bash
pytest tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py -v -m performance
```

#### Load Tests (8 tests)
```bash
pytest tests/integration/load/ -v -m load
```

#### Data Quality Tests (5 tests)
```bash
pytest tests/integration/data_quality/ -v -m data_quality
```

---

## 📋 Detailed Commands

### Run All New Tests with Detailed Output
```bash
pytest tests/integration/security/ tests/integration/error_handling/ tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py tests/integration/load/ tests/integration/data_quality/ -v --tb=short
```

### Run All New Tests with HTML Report
```bash
pytest tests/integration/security/ tests/integration/error_handling/ tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py tests/integration/load/ tests/integration/data_quality/ -v --html=reports/new_tests_report.html --self-contained-html
```

### Run All New Tests with JUnit XML Report
```bash
pytest tests/integration/security/ tests/integration/error_handling/ tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py tests/integration/load/ tests/integration/data_quality/ -v --junitxml=reports/new_tests_junit.xml
```

---

## 🎯 Run by Test ID Range

### Security Tests (PZ-14771 to PZ-14788)
```bash
pytest tests/integration/security/ -v -k "PZ-14771 or PZ-14772 or PZ-14773 or PZ-14774 or PZ-14775 or PZ-14776 or PZ-14777 or PZ-14778 or PZ-14779 or PZ-14788"
```

### Error Handling Tests (PZ-14780 to PZ-14787)
```bash
pytest tests/integration/error_handling/ -v -k "PZ-14780 or PZ-14781 or PZ-14782 or PZ-14783 or PZ-14784 or PZ-14785 or PZ-14786 or PZ-14787"
```

### Performance Tests (PZ-14790 to PZ-14799)
```bash
pytest tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py -v -k "PZ-14790 or PZ-14791 or PZ-14792 or PZ-14793 or PZ-14794 or PZ-14795 or PZ-14796 or PZ-14797 or PZ-14798 or PZ-14799"
```

### Load Tests (PZ-14800 to PZ-14807)
```bash
pytest tests/integration/load/ -v -k "PZ-14800 or PZ-14801 or PZ-14802 or PZ-14803 or PZ-14804 or PZ-14805 or PZ-14806 or PZ-14807"
```

### Data Quality Tests (PZ-14808 to PZ-14812)
```bash
pytest tests/integration/data_quality/ -v -k "PZ-14808 or PZ-14809 or PZ-14810 or PZ-14811 or PZ-14812"
```

---

## 🚀 Run All New Tests (Simplified - Using Markers)

### All New Tests with Markers
```bash
pytest tests/integration/security/ tests/integration/error_handling/ tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py tests/integration/load/ tests/integration/data_quality/ -v -m "security or error_handling or performance or load or data_quality"
```

---

## 📊 Test Count Verification

### Count New Tests
```bash
pytest tests/integration/security/ tests/integration/error_handling/ tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py tests/integration/load/ tests/integration/data_quality/ --collect-only -q | findstr "test session starts"
```

---

## ⚠️ Notes

1. **Performance Tests:** Only the NEW files are included:
   - `test_response_time.py`
   - `test_concurrent_performance.py`
   - `test_resource_usage.py`
   - `test_database_performance.py`
   - `test_network_latency.py`
   
   Old files like `test_latency_requirements.py` are NOT included.

2. **Slow Tests:** Load tests are marked as `@pytest.mark.slow` and may take longer to run.

3. **Skip Health Check:** If health check fails, use `--skip-health-check`:
   ```bash
   pytest tests/integration/security/ ... --skip-health-check
   ```

4. **Environment:** Make sure you're using the correct environment (staging by default):
   ```bash
   pytest ... --env=staging
   ```

---

## 🎯 Recommended Command for First Run

```bash
pytest tests/integration/security/ tests/integration/error_handling/ tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py tests/integration/load/ tests/integration/data_quality/ -v --tb=short -x
```

**Flags:**
- `-v`: Verbose output
- `--tb=short`: Short traceback format
- `-x`: Stop on first failure

---

## 📝 Expected Test Count

- Security: 10 tests
- Error Handling: 8 tests
- Performance: 10 tests
- Load: 8 tests
- Data Quality: 5 tests
- **Total: 41 tests**

