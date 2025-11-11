# 🧪 Focus Server Test Suite

**Xray-Aligned Test Organization**  
**Last Updated:** 2025-11-04  
**Repository:** https://github.com/PrismaPhotonics/panda-backend-api-tests

---

## ⚠️ SCOPE REFINEMENT (27 Oct 2025)

Following meeting decision (PZ-13756), test scope has been refined:

### ✅ **IN SCOPE:**
- **K8s/Orchestration:** Job lifecycle, resource allocation, port exposure, observability
- **Focus Server API:** Pre-launch validations (port, data, time-range, config)
- **System Behavior:** Clean startup, stability, predictable errors, rollback/cleanup
- **Capacity:** Support for 200 concurrent jobs
- **Resilience:** Pod outage recovery, infrastructure resilience
- **Data Quality:** MongoDB schema validation, data integrity, consistency
- **Error Handling:** HTTP error codes, invalid payloads, network errors
- **Load Testing:** Concurrent load, peak load, sustained load, recovery
- **Performance:** Response time, latency, resource usage, database performance
- **Security:** Authentication, input validation, CSRF protection, rate limiting

### ❌ **OUT OF SCOPE:**
- Internal Job processing ("Baby")
- Algorithm/data correctness
- Spectrogram content validation
- Full gRPC stream content checks

### 🔄 **MODIFIED SCOPE:**
- **gRPC:** Transport readiness only (port/handshake), no stream content validation

---

## 📊 Test Structure Overview

This test suite is **aligned with Jira Xray categories** for seamless integration and reporting.

```
tests/
├── 🟢 integration/          # Integration tests (workflows, E2E)
│   ├── api/                # API endpoint tests (20+ files)
│   │   ├── test_api_endpoints_high_priority.py
│   │   ├── test_api_endpoints_additional.py
│   │   ├── test_config_validation_high_priority.py
│   │   ├── test_configure_endpoint.py
│   │   ├── test_config_task_endpoint.py
│   │   ├── test_task_metadata_endpoint.py
│   │   ├── test_waterfall_endpoint.py
│   │   ├── test_health_check.py
│   │   ├── test_prelaunch_validations.py
│   │   ├── test_live_monitoring_flow.py
│   │   ├── test_historic_playback_e2e.py
│   │   ├── test_historic_playback_additional.py
│   │   ├── test_singlechannel_view_mapping.py
│   │   ├── test_waterfall_view.py
│   │   ├── test_dynamic_roi_adjustment.py
│   │   ├── test_view_type_validation.py
│   │   ├── test_orchestration_validation.py
│   │   ├── test_live_streaming_stability.py
│   │   ├── test_config_validation_nfft_frequency.py
│   │   └── test_nfft_overlap_edge_case.py
│   ├── calculations/        # System calculations validation
│   ├── data_quality/        # Data completeness, consistency, integrity
│   ├── e2e/                 # End-to-end workflows
│   ├── error_handling/      # HTTP errors, invalid payloads, network errors
│   ├── load/                # Load testing (concurrent, peak, sustained)
│   ├── performance/         # Performance tests (latency, resource usage)
│   └── security/            # Security tests (auth, validation, CSRF, rate limiting)
│
├── 🟡 data_quality/         # MongoDB data quality (root level)
│   ├── test_mongodb_data_quality.py
│   ├── test_mongodb_indexes_and_schema.py
│   ├── test_mongodb_schema_validation.py
│   ├── test_mongodb_recovery.py
│   └── test_recordings_classification.py
│
├── 🔴 performance/          # Performance tests (root level)
│   └── test_mongodb_outage_resilience.py
│
├── 🟤 infrastructure/       # Infrastructure tests
│   ├── resilience/          # Pod resilience tests (7 files)
│   │   ├── test_focus_server_pod_resilience.py
│   │   ├── test_mongodb_pod_resilience.py
│   │   ├── test_rabbitmq_pod_resilience.py
│   │   ├── test_segy_recorder_pod_resilience.py
│   │   ├── test_multiple_pods_resilience.py
│   │   └── test_pod_recovery_scenarios.py
│   ├── test_basic_connectivity.py
│   ├── test_external_connectivity.py
│   ├── test_k8s_job_lifecycle.py
│   ├── test_mongodb_monitoring_agent.py
│   ├── test_pz_integration.py
│   ├── test_rabbitmq_connectivity.py
│   ├── test_rabbitmq_outage_handling.py
│   └── test_system_behavior.py
│
├── 🔐 security/             # Security tests (root level)
│   └── test_malformed_input_handling.py
│
├── ⚡ stress/               # Stress tests
│   └── test_extreme_configurations.py
│
├── 📈 load/                 # Load tests (root level)
│   └── test_job_capacity_limits.py
│
├── 🔬 unit/                 # Unit tests (NOT in Xray)
│   ├── test_basic_functionality.py
│   ├── test_config_loading.py
│   ├── test_models_validation.py
│   └── test_validators.py
│
└── 🎨 ui/                   # UI tests (placeholder)
    └── generated/
        ├── test_button_interactions.py
        └── test_form_validation.py
```

---

## 📚 Category Documentation

### Core Test Categories (Xray-Aligned)

| Category | Path | Status | Tests | README |
|----------|------|--------|-------|--------|
| **🟢 Integration** | `integration/` | ✅ Active | 100+ | [README](integration/README.md) |
| **🟢 Integration/API** | `integration/api/` | ✅ Active | 20+ files | [README](integration/api/README.md) |
| **🟢 Integration/Data Quality** | `integration/data_quality/` | ✅ Active | 3 files | - |
| **🟢 Integration/Error Handling** | `integration/error_handling/` | ✅ Active | 3 files | - |
| **🟢 Integration/Load** | `integration/load/` | ✅ Active | 6 files | - |
| **🟢 Integration/Performance** | `integration/performance/` | ✅ Active | 8 files | - |
| **🟢 Integration/Security** | `integration/security/` | ✅ Active | 7 files | - |
| **🟡 Data Quality** | `data_quality/` | ✅ Active | 5 files | [README](data_quality/README.md) |
| **🔴 Performance** | `performance/` | ✅ Active | 1 file | [README](performance/README.md) |
| **🟤 Infrastructure** | `infrastructure/` | ✅ Active | 20+ files | [README](infrastructure/README.md) |
| **🟤 Infrastructure/Resilience** | `infrastructure/resilience/` | ✅ Active | 7 files | - |
| **🔐 Security** | `security/` | ✅ Active | 1 file | [README](security/README.md) |
| **⚡ Stress** | `stress/` | ✅ Active | 1 file | [README](stress/README.md) |
| **📈 Load** | `load/` | ✅ Active | 1 file | [README](load/README.md) |

### Additional Categories

| Category | Path | Status | Tests | Notes |
|----------|------|--------|-------|-------|
| **🔬 Unit** | `unit/` | ✅ Active | 4 files | Not tracked in Xray |
| **🎨 UI** | `ui/` | ✅ Partial | 2 files | Placeholder tests |

---

## 🚀 Quick Start

### Run All Tests
```bash
pytest tests/ -v
```

### Run by Category
```bash
# Xray categories
pytest tests/integration/ -v
pytest tests/integration/api/ -v
pytest tests/data_quality/ -v
pytest tests/performance/ -v
pytest tests/infrastructure/ -v
pytest tests/infrastructure/resilience/ -v
pytest tests/security/ -v
pytest tests/stress/ -v
pytest tests/load/ -v

# Additional
pytest tests/unit/ -v
pytest tests/ui/ -v
```

### Run by Marker
```bash
pytest -m integration -v
pytest -m api -v
pytest -m data_quality -v
pytest -m performance -v
pytest -m infrastructure -v
pytest -m resilience -v
pytest -m security -v
pytest -m load -v
pytest -m critical -v
pytest -m smoke -v
```

### Run Specific Tests
```bash
# Integration subcategories
pytest tests/integration/api/ -v
pytest tests/integration/data_quality/ -v
pytest tests/integration/error_handling/ -v
pytest tests/integration/load/ -v
pytest tests/integration/performance/ -v
pytest tests/integration/security/ -v

# Infrastructure
pytest tests/infrastructure/resilience/ -v
pytest tests/infrastructure/test_basic_connectivity.py -v

# Data quality
pytest tests/data_quality/test_mongodb_data_quality.py -v

# Load and performance
pytest tests/load/test_job_capacity_limits.py -v
pytest tests/performance/test_mongodb_outage_resilience.py -v
```

---

## 📊 Test Coverage by Category

### ✅ Implemented (Active)

| Category | Tests | Coverage | Priority |
|----------|-------|----------|----------|
| **Integration/API** | 20+ files | 🟢 High | Critical |
| ↳ API Endpoints | 20+ | 🟢 Complete | High |
| ↳ Config Validation | 3 | 🟢 Complete | High |
| ↳ Live Monitoring | 2 | 🟢 Complete | High |
| ↳ Historic Playback | 2 | 🟢 Complete | High |
| ↳ SingleChannel | 1 | 🟢 Complete | Medium |
| ↳ Waterfall | 2 | 🟢 Complete | Medium |
| **Integration/Data Quality** | 3 files | 🟢 Complete | High |
| **Integration/Error Handling** | 3 files | 🟢 Complete | High |
| **Integration/Load** | 6 files | 🟢 Complete | High |
| **Integration/Performance** | 8 files | 🟢 Complete | High |
| **Integration/Security** | 7 files | 🟢 Complete | High |
| **Data Quality** | 5 files | 🟢 Complete | High |
| **Infrastructure** | 13+ files | 🟢 Complete | High |
| **Infrastructure/Resilience** | 7 files | 🟢 Complete | High |
| **Performance** | 1 file | 🟢 Complete | High |
| **Security** | 1 file | 🟢 Complete | High |
| **Load** | 1 file | 🟢 Complete | High |
| **Stress** | 1 file | 🟢 Complete | Medium |
| **Unit Tests** | 4 files | 🟢 Complete | Low |

### 📈 Test Statistics

- **Total Test Files:** 70+ files
- **Total Test Functions:** 300+ tests
- **Xray Integration:** ✅ All tests marked with `@pytest.mark.xray()`
- **Jira Integration:** ✅ 15 bugs integrated with automated tests

---

## 🎯 Test Priority Matrix

### 🔴 Critical (Must Have)
- ✅ Integration tests (API, Live, Historic, ROI, SingleChannel, Waterfall)
- ✅ Data Quality (MongoDB validation, schema, indexes)
- ✅ Infrastructure (Connectivity, outage resilience, pod recovery)
- ✅ Error Handling (HTTP errors, invalid payloads, network errors)
- ✅ Load Testing (Concurrent, peak, sustained load)
- ✅ Performance (Response time, latency, resource usage)
- ✅ Security (Authentication, validation, CSRF, rate limiting)

### 🟡 High Priority
- ✅ Stress tests (extreme values, boundaries)
- ✅ Resilience tests (pod outage recovery)
- ✅ Additional API coverage

### 🟢 Medium Priority
- ✅ Unit tests (framework validation)
- ⏳ UI tests (end-to-end workflows)
- ✅ Extended integration scenarios

---

## 📝 Test Markers

Tests are marked for easy filtering:

```python
# Xray categories
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.data_quality
@pytest.mark.performance
@pytest.mark.infrastructure
@pytest.mark.resilience
@pytest.mark.security
@pytest.mark.stress
@pytest.mark.load
@pytest.mark.error_handling

# Severity
@pytest.mark.critical
@pytest.mark.high
@pytest.mark.medium
@pytest.mark.low

# Type
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.e2e

# Component
@pytest.mark.mongodb
@pytest.mark.kubernetes
@pytest.mark.rabbitmq
@pytest.mark.roi
@pytest.mark.singlechannel
@pytest.mark.waterfall

# Jira Integration
@pytest.mark.xray("PZ-XXXXX")
@pytest.mark.jira("PZ-XXXXX")
```

---

## 🔍 Finding Tests

### By Functionality
- **MongoDB:** `tests/data_quality/` + `tests/infrastructure/test_mongodb_*.py` + `tests/integration/data_quality/`
- **API Endpoints:** `tests/integration/api/`
- **ROI:** `tests/integration/api/test_dynamic_roi_adjustment.py`
- **SingleChannel:** `tests/integration/api/test_singlechannel_view_mapping.py`
- **Waterfall:** `tests/integration/api/test_waterfall_*.py`
- **Historic:** `tests/integration/api/test_historic_playback_*.py`
- **Live:** `tests/integration/api/test_live_monitoring_flow.py`
- **Connectivity:** `tests/infrastructure/test_*_connectivity.py`
- **Resilience:** `tests/infrastructure/resilience/`
- **Error Handling:** `tests/integration/error_handling/`
- **Load:** `tests/integration/load/` + `tests/load/`
- **Performance:** `tests/integration/performance/` + `tests/performance/`
- **Security:** `tests/integration/security/` + `tests/security/`

### By Jira Ticket
All tests are marked with `@pytest.mark.xray()` for Jira integration. See individual test files for ticket mappings.

**Key Jira Tickets:**
- PZ-13986 (200 Jobs Capacity) → `tests/load/test_job_capacity_limits.py`
- PZ-13985 (Live Metadata Missing Fields) → `tests/integration/api/test_live_monitoring_flow.py`
- PZ-13984 (Future Timestamps Accepted) → `tests/integration/api/test_prelaunch_validations.py`
- PZ-13983 (MongoDB Indexes Missing) → `tests/data_quality/test_mongodb_indexes_and_schema.py`
- PZ-13669 (SingleChannel min!=max) → `tests/integration/api/test_singlechannel_view_mapping.py`
- PZ-13640 (Slow MongoDB Outage Response) → `tests/performance/test_mongodb_outage_resilience.py`
- PZ-13238 (Waterfall Fails) → `tests/integration/api/test_waterfall_view.py`

---

## 🛠️ Configuration

Tests use configuration from:
- `config/environments.yaml` - Environment settings
- `config/settings.yaml` - Framework settings
- `tests/conftest.py` - Pytest configuration and fixtures
- `tests/conftest_xray.py` - Xray integration configuration
- `tests/pytest_logging_plugin.py` - Automatic test logging

---

## 📚 Related Documentation

- **Main README:** `../README.md`
- **User Guides:** `../docs/02_user_guides/`
- **Test Results:** `../docs/04_testing/test_results/`
- **Xray Mapping:** `../docs/04_testing/xray_mapping/`
- **Jira Integration:** `../docs/06_project_management/jira/`

---

## 🎓 Writing New Tests

### 1. Choose the Right Category

**Ask yourself:**
- Testing an API endpoint? → `integration/api/`
- Testing E2E workflow? → `integration/e2e/`
- Testing MongoDB data? → `data_quality/` or `integration/data_quality/`
- Testing latency/load? → `performance/` or `integration/performance/`
- Testing connectivity? → `infrastructure/`
- Testing pod resilience? → `infrastructure/resilience/`
- Testing malformed input? → `security/` or `integration/security/`
- Testing extreme values? → `stress/`
- Testing error handling? → `integration/error_handling/`
- Testing load capacity? → `load/` or `integration/load/`

### 2. Use the Category Template

Each category README has:
- Purpose and scope
- Test structure guidelines
- Examples
- Related Jira tickets

### 3. Add Appropriate Markers

```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
@pytest.mark.xray("PZ-XXXXX")
def test_api_endpoint():
    """Test API endpoint functionality"""
    ...
```

### 4. Update Documentation

After adding tests:
- Update category README
- Update test count in this README
- Link to Jira tickets if applicable

---

## 📞 Support

- **Questions?** Contact QA Automation Team
- **Bug in test?** Create Jira ticket
- **New test needed?** Check category README for guidelines

---

## 📈 Progress Tracking

| Milestone | Status | Date |
|-----------|--------|------|
| Test structure reorganized | ✅ Complete | 2025-10-21 |
| Integration tests | ✅ Complete | 2025-10-20 |
| Data Quality tests | ✅ Complete | 2025-10-15 |
| Infrastructure tests | ✅ Complete | 2025-10-18 |
| Resilience tests | ✅ Complete | 2025-11-04 |
| API tests | ✅ Complete | 2025-11-04 |
| Performance tests | ✅ Complete | 2025-11-04 |
| Security tests | ✅ Complete | 2025-11-04 |
| Load tests | ✅ Complete | 2025-11-04 |
| Error handling tests | ✅ Complete | 2025-11-04 |
| Jira integration | ✅ Complete | 2025-11-04 |

---

## 🔗 Repository Information

- **GitHub Repository:** https://github.com/PrismaPhotonics/panda-backend-api-tests
- **Branch:** `chore/add-roy-tests`
- **Last Code Update:** 2025-11-04
- **Total Files Uploaded:** 71 test files

---

**Last Updated:** 2025-11-04  
**Maintained by:** QA Automation Team  
**Version:** 3.0 (Complete test suite with all categories implemented)
