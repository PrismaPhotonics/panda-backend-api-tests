# Commands to Run API Endpoint Tests
=====================================

## 🟢 Current Structure Tests (WORKING)

### Run All Current Structure Tests
```bash
pytest tests/integration/api/test_configure_endpoint.py -v --skip-health-check
```

### Run Specific Test
```bash
# Valid Configuration
pytest tests/integration/api/test_configure_endpoint.py::TestConfigureEndpoint::test_configure_valid_configuration -v --skip-health-check

# Missing Required Fields
pytest tests/integration/api/test_configure_endpoint.py::TestConfigureEndpoint::test_configure_missing_required_fields -v --skip-health-check

# Invalid Channel Range
pytest tests/integration/api/test_configure_endpoint.py::TestConfigureEndpoint::test_configure_invalid_channel_range -v --skip-health-check

# Invalid Frequency Range
pytest tests/integration/api/test_configure_endpoint.py::TestConfigureEndpoint::test_configure_invalid_frequency_range -v --skip-health-check

# Invalid View Type
pytest tests/integration/api/test_configure_endpoint.py::TestConfigureEndpoint::test_configure_invalid_view_type -v --skip-health-check

# Frequency Above Nyquist
pytest tests/integration/api/test_configure_endpoint.py::TestConfigureEndpoint::test_configure_frequency_above_nyquist -v --skip-health-check

# Channel Count Exceeds Maximum
pytest tests/integration/api/test_configure_endpoint.py::TestConfigureEndpoint::test_configure_channel_count_exceeds_maximum -v --skip-health-check

# Invalid NFFT Selection
pytest tests/integration/api/test_configure_endpoint.py::TestConfigureEndpoint::test_configure_invalid_nfft_selection -v --skip-health-check

# Invalid Time Range (Historic)
pytest tests/integration/api/test_configure_endpoint.py::TestConfigureEndpoint::test_configure_invalid_time_range_historic -v --skip-health-check

# Response Time Performance
pytest tests/integration/api/test_configure_endpoint.py::TestConfigureEndpoint::test_configure_response_time_performance -v --skip-health-check
```

### Run with Detailed Output
```bash
pytest tests/integration/api/test_configure_endpoint.py -v -s --skip-health-check
```

### Run with HTML Report
```bash
pytest tests/integration/api/test_configure_endpoint.py -v --skip-health-check --html=reports/api_tests_report.html --self-contained-html
```

---

## ⏸️ Future Structure Tests (SKIPPED)

These tests are currently skipped. They will show as "SKIPPED" when run:

### Run Future Structure Tests (Will Show as Skipped)
```bash
# POST /config/{task_id} tests
pytest tests/integration/api/test_config_task_endpoint.py -v --skip-health-check

# GET /waterfall/{task_id}/{row_count} tests
pytest tests/integration/api/test_waterfall_endpoint.py -v --skip-health-check

# GET /metadata/{task_id} tests
pytest tests/integration/api/test_task_metadata_endpoint.py -v --skip-health-check
```

### See Skip Reasons
```bash
pytest tests/integration/api/test_config_task_endpoint.py -v -rs --skip-health-check
```

---

## 🎯 Run All API Tests Together

### Run All API Tests (Current + Future)
```bash
pytest tests/integration/api/test_configure_endpoint.py \
        tests/integration/api/test_config_task_endpoint.py \
        tests/integration/api/test_waterfall_endpoint.py \
        tests/integration/api/test_task_metadata_endpoint.py \
        -v --skip-health-check
```

### Run Only Working Tests (Exclude Skipped)
```bash
pytest tests/integration/api/test_configure_endpoint.py -v --skip-health-check -m "not skip"
```

---

## 📊 Run with Markers

### Run by Xray Test ID
```bash
# Run specific Xray test
pytest tests/integration/api/test_configure_endpoint.py -v --skip-health-check -k "PZ-14750"

# Run multiple Xray tests
pytest tests/integration/api/test_configure_endpoint.py -v --skip-health-check -k "PZ-14750 or PZ-14751"
```

### Run by Priority
```bash
# Run only critical tests
pytest tests/integration/api/test_configure_endpoint.py -v --skip-health-check -m critical
```

---

## 🔍 Useful Options

### Show Test Output (-s)
```bash
pytest tests/integration/api/test_configure_endpoint.py -v -s --skip-health-check
```

### Stop on First Failure (-x)
```bash
pytest tests/integration/api/test_configure_endpoint.py -v -x --skip-health-check
```

### Show Local Variables on Failure (-l)
```bash
pytest tests/integration/api/test_configure_endpoint.py -v -l --skip-health-check
```

### Run in Parallel (if pytest-xdist installed)
```bash
pytest tests/integration/api/test_configure_endpoint.py -v --skip-health-check -n auto
```

---

## 📝 Example Output

### Successful Test Run
```
tests/integration/api/test_configure_endpoint.py::TestConfigureEndpoint::test_configure_valid_configuration PASSED
tests/integration/api/test_configure_endpoint.py::TestConfigureEndpoint::test_configure_missing_required_fields PASSED
...
```

### Skipped Test Run
```
tests/integration/api/test_config_task_endpoint.py::TestConfigTaskEndpoint::test_config_task_valid_configuration SKIPPED [1] Future API structure - POST /config/{task_id} endpoint not yet deployed to staging
...
```

---

## 🚀 Quick Start

**Run all working tests:**
```bash
pytest tests/integration/api/test_configure_endpoint.py -v --skip-health-check
```

**Run single test:**
```bash
pytest tests/integration/api/test_configure_endpoint.py::TestConfigureEndpoint::test_configure_valid_configuration -v --skip-health-check -s
```

