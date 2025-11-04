# 🧪 Focus Server Test Suite

**Xray-Aligned Test Organization**  
**Last Updated:** 2025-10-27 (Scope Refined - PZ-13756)

---

## ⚠️ SCOPE REFINEMENT (27 Oct 2025)

Following meeting decision (PZ-13756), test scope has been refined:

### ✅ **IN SCOPE:**
- **K8s/Orchestration:** Job lifecycle, resource allocation, port exposure, observability
- **Focus Server API:** Pre-launch validations (port, data, time-range, config)
- **System Behavior:** Clean startup, stability, predictable errors, rollback/cleanup
- **Capacity:** Support for 200 concurrent jobs

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
│   ├── configuration/      # Config validation, NFFT, ranges
│   ├── historic_playback/  # Historic flow, status 208
│   ├── live_monitoring/    # Live flow, sensors, metadata
│   ├── roi_adjustment/     # Dynamic ROI via RabbitMQ
│   ├── singlechannel/      # SingleChannel view mapping
│   └── visualization/      # Colormap, CAxis commands
│
├── 🔵 api/                  # API endpoint tests
│   ├── endpoints/          # General API endpoints
│   └── singlechannel/      # API-specific SingleChannel
│
├── 🟡 data_quality/         # MongoDB data quality
├── 🔴 performance/          # Latency, load tests
├── 🟤 infrastructure/       # MongoDB, K8s, SSH connectivity
├── 🔐 security/             # Security validation
├── ⚡ stress/               # Extreme values, boundaries
├── 🔬 unit/                 # Unit tests (NOT in Xray)
└── 🎨 ui/                   # UI tests (placeholder)
```

---

## 📚 Category Documentation

Click on each category for detailed documentation:

### Core Test Categories (Xray-Aligned)

| Category | Path | Status | Tests | README |
|----------|------|--------|-------|--------|
| **🟢 Integration** | `integration/` | ✅ Active | 50+ | [README](integration/README.md) |
| **🔵 API** | `api/` | ⏳ Planned | 0 | [README](api/README.md) |
| **🟡 Data Quality** | `data_quality/` | ✅ Active | 6 | [README](data_quality/README.md) |
| **🔴 Performance** | `performance/` | ⏳ Planned | 0 | [README](performance/README.md) |
| **🟤 Infrastructure** | `infrastructure/` | ✅ Active | 15+ | [README](infrastructure/README.md) |
| **🔐 Security** | `security/` | ⏳ Planned | 0 | [README](security/README.md) |
| **⚡ Stress** | `stress/` | ⏳ Planned | 0 | [README](stress/README.md) |

### Additional Categories

| Category | Path | Status | Tests | Notes |
|----------|------|--------|-------|-------|
| **🔬 Unit** | `unit/` | ✅ Active | 30+ | Not tracked in Xray |
| **🎨 UI** | `ui/` | ✅ Partial | 2 | Placeholder tests |

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
pytest tests/api/ -v
pytest tests/data_quality/ -v
pytest tests/performance/ -v
pytest tests/infrastructure/ -v
pytest tests/security/ -v
pytest tests/stress/ -v

# Additional
pytest tests/unit/ -v
pytest tests/ui/ -v
```

### Run by Marker
```bash
pytest -m integration -v
pytest -m data_quality -v
pytest -m performance -v
pytest -m critical -v
pytest -m smoke -v
```

### Run Specific Tests
```bash
# Integration subcategories
pytest tests/integration/roi_adjustment/ -v
pytest tests/integration/singlechannel/ -v
pytest tests/integration/historic_playback/ -v
pytest tests/integration/live_monitoring/ -v

# Data quality
pytest tests/data_quality/test_mongodb_data_quality.py -v

# Infrastructure
pytest tests/infrastructure/test_basic_connectivity.py -v
```

---

## 📊 Test Coverage by Category

### ✅ Implemented (Active)

| Category | Tests | Coverage | Priority |
|----------|-------|----------|----------|
| **Integration** | 50+ | 🟢 High | Critical |
| ↳ ROI Adjustment | 25 | 🟢 Complete | High |
| ↳ SingleChannel | 15 | 🟢 Complete | Medium |
| ↳ Historic Playback | 10+ | 🟢 Complete | High |
| ↳ Live Monitoring | 15+ | 🟢 Complete | High |
| **Data Quality** | 6 | 🟢 Complete | High |
| **Infrastructure** | 15+ | 🟢 Complete | High |
| **Unit Tests** | 30+ | 🟢 Complete | Low |

### ⏳ Planned (To Be Implemented)

| Category | Priority | Estimated Tests | Status |
|----------|----------|----------------|--------|
| **API** | 🔴 Critical | 15+ | Planned |
| **Performance** | 🔴 Critical | 10+ | Planned |
| **Security** | 🔴 Critical | 8+ | Planned |
| **Stress** | 🟡 Medium | 20+ | Planned |

---

## 🎯 Test Priority Matrix

### 🔴 Critical (Must Have)
- ✅ Integration tests (Live, Historic, ROI, SingleChannel)
- ✅ Data Quality (MongoDB validation)
- ✅ Infrastructure (Connectivity, outage resilience)
- ⏳ **API tests** (endpoints, error handling)
- ⏳ **Performance tests** (P95 latency, load)
- ⏳ **Security tests** (malformed input, validation)

### 🟡 High Priority
- ⏳ Stress tests (extreme values, boundaries)
- ⏳ Additional API coverage
- ⏳ Extended performance scenarios

### 🟢 Medium Priority
- ✅ Unit tests (framework validation)
- ⏳ UI tests (end-to-end workflows)
- ⏳ Extended integration scenarios

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
@pytest.mark.security
@pytest.mark.stress

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
```

---

## 🔍 Finding Tests

### By Functionality
- **MongoDB:** `tests/data_quality/` + `tests/infrastructure/test_mongodb_*.py`
- **ROI:** `tests/integration/roi_adjustment/`
- **SingleChannel:** `tests/integration/singlechannel/` + `tests/api/singlechannel/`
- **Historic:** `tests/integration/historic_playback/`
- **Live:** `tests/integration/live_monitoring/`
- **Connectivity:** `tests/infrastructure/test_*_connectivity.py`

### By Jira Ticket
See individual category READMEs for Jira ticket mappings.

---

## 🛠️ Configuration

Tests use configuration from:
- `config/environments.yaml` - Environment settings
- `config/settings.yaml` - Framework settings
- `tests/conftest.py` - Pytest configuration and fixtures

---

## 📚 Related Documentation

- **Main README:** `../README.md`
- **Test Location Guide:** `TESTS_LOCATION_GUIDE_HE.md` (Hebrew)
- **Xray Documentation:** `../documentation/xray/`
- **Jira Analysis:** `../documentation/analysis/`

---

## 🎓 Writing New Tests

### 1. Choose the Right Category

**Ask yourself:**
- Testing an API endpoint? → `api/`
- Testing E2E workflow? → `integration/`
- Testing MongoDB data? → `data_quality/`
- Testing latency/load? → `performance/`
- Testing connectivity? → `infrastructure/`
- Testing malformed input? → `security/`
- Testing extreme values? → `stress/`

### 2. Use the Category Template

Each category README has:
- Purpose and scope
- Test structure guidelines
- Examples
- Related Jira tickets

### 3. Add Appropriate Markers

```python
@pytest.mark.integration
@pytest.mark.critical
@pytest.mark.roi
def test_roi_expansion():
    """Test ROI expansion via RabbitMQ command"""
    ...
```

### 4. Update Documentation

After adding tests:
- Update category README
- Update test count in this INDEX
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
| API tests | ⏳ In Progress | - |
| Performance tests | ⏳ Planned | - |
| Security tests | ⏳ Planned | - |
| Stress tests | ⏳ Planned | - |

---

**Last Updated:** 2025-10-21  
**Maintained by:** QA Automation Team  
**Version:** 2.0 (Xray-aligned structure)
