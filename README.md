# Focus Server Automation Framework

## Project Overview

Comprehensive test automation framework for the Focus Server backend system, including real-time pod monitoring, API testing, infrastructure validation, and performance testing.

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
pytest --version
```

### Running Tests

```bash
# Run all tests
pytest be_focus_server_tests/ -v

# Run with real-time pod monitoring
pytest be_focus_server_tests/ --monitor-pods -v

# Run specific test category
pytest be_focus_server_tests/integration/api/ -v
pytest be_focus_server_tests/infrastructure/ -v
```

---

## 📁 Project Structure

```
focus_server_automation/
├── config/                          # Configuration files
│   ├── environments.yaml            # Environment configuration (production only)
│   ├── settings.yaml                # Test settings
│   ├── config_manager.py            # Configuration loader
│   └── usersettings.new_production_client.json  # Client configuration
│
├── src/                             # Source code
│   ├── apis/                        # API clients
│   │   ├── focus_server_api.py      # Focus Server REST API
│   │   └── baby_analyzer_mq_client.py  # RabbitMQ client
│   ├── core/                        # Core utilities
│   │   ├── api_client.py            # Base API client
│   │   ├── base_test.py             # Base test class
│   │   └── exceptions.py            # Custom exceptions
│   ├── infrastructure/              # Infrastructure managers
│   │   ├── kubernetes_manager.py    # K8s operations
│   │   ├── mongodb_manager.py       # MongoDB operations
│   │   ├── rabbitmq_manager.py      # RabbitMQ operations
│   │   └── ssh_manager.py           # SSH operations
│   ├── models/                      # Data models
│   │   └── focus_server_models.py   # Pydantic models
│   └── utils/                       # Utilities
│       ├── realtime_pod_monitor.py  # Real-time pod log monitoring
│       ├── pod_logs_collector.py    # Pod log collection
│       └── helpers.py               # Helper functions
│
├── be_focus_server_tests/            # Test suites
│   ├── conftest.py                  # Pytest fixtures & configuration
│   ├── integration/                 # Integration tests
│   │   ├── api/                     # API tests
│   │   └── performance/             # Performance tests
│   ├── infrastructure/              # Infrastructure tests
│   └── unit/                        # Unit tests
│
├── scripts/                         # Utility scripts
│   ├── quick_job_capacity_check.py  # Check K8s job capacity
│   └── [other utilities]
│
├── docs/                            # 📚 **NEW** Organized Documentation
│   ├── 01_getting_started/          # Quick start & installation
│   ├── 02_user_guides/              # How-to guides
│   ├── 03_architecture/             # System design
│   ├── 04_testing/                  # Test docs, Xray mapping, results
│   ├── 05_development/              # Contributing & standards
│   ├── 06_project_management/       # Work plans, meetings, Jira
│   ├── 07_infrastructure/           # K8s, MongoDB, RabbitMQ
│   └── 08_archive/                  # Historical documents
│
├── documentation/                   # Legacy documentation (being migrated)
│
├── logs/                            # Generated logs
│   └── pod_logs/                    # Pod monitoring logs
│       ├── test_logs/               # Test-specific logs
│       ├── *_realtime.log           # Service logs
│       └── *_errors.log             # Service errors
│
└── reports/                         # Test reports
    └── [generated reports]
```

---

## 🎯 Key Features

### 1. Real-time Pod Monitoring
Monitor Kubernetes pod logs in real-time during test execution with automatic test association.

```bash
pytest be_focus_server_tests/ --monitor-pods -v
```

**Features:**
- Automatic detection of gRPC jobs
- Test-specific log files
- Error detection and highlighting
- Multi-service monitoring (Focus Server, MongoDB, RabbitMQ, gRPC Jobs)

**See:** `documentation/testing/REALTIME_POD_MONITORING.md`

### 2. Comprehensive API Testing
Full REST API test coverage with validation, error handling, and performance testing.

**Test Categories:**
- Configuration validation (PZ-13873 to PZ-13879)
- Live/Historic mode testing
- Error handling validation
- Performance testing

### 3. Infrastructure Testing
Kubernetes, MongoDB, RabbitMQ, and SSH connectivity tests.

### 4. Automated Configuration Management
Environment-specific configuration with validation.

---

## 🔧 Configuration

### Production Environment

The framework uses **only one environment**: `new_production`

**Critical Values:**
```yaml
Focus Server:  https://10.10.100.100/focus-server/
MongoDB:       10.10.100.108:27017
RabbitMQ:      10.10.100.107:5672
Kubernetes:    panda namespace
Worker Node:   10.10.100.113

Constraints:
  Max Frequency: 1000 Hz
  Max Channels:  2222
  Max Jobs:      30
```

**See:** `config/environments.yaml`

---

## 📊 Test Execution

### Test Categories

```bash
# API Tests
pytest be_focus_server_tests/integration/api/ -v

# Infrastructure Tests
pytest be_focus_server_tests/infrastructure/ -v

# Performance Tests
pytest be_focus_server_tests/integration/performance/ -v

# High Priority Tests
pytest be_focus_server_tests/integration/api/test_config_validation_high_priority.py -v
```

### Test Markers

```bash
# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run only infrastructure tests
pytest -m infrastructure
```

---

## 🔍 Pod Monitoring

### Usage

```bash
# Enable real-time monitoring
pytest be_focus_server_tests/ --monitor-pods -v
```

### Log Files

```
logs/pod_logs/
├── panda-panda-focus-server_realtime.log
├── mongodb_realtime.log
├── rabbitmq-panda_realtime.log
├── grpc-jobs_realtime.log
└── test_logs/
    └── test_name_TIMESTAMP.log
```

### Features

- ✅ Automatic test association
- ✅ Error detection (14 patterns)
- ✅ Dynamic gRPC job monitoring
- ✅ Test-specific log files
- ✅ Multi-threaded monitoring

**See:** `documentation/testing/REALTIME_POD_MONITORING.md`

---

## 📚 Documentation

### **→ [📖 Complete Documentation Index](docs/README.md)** ←

**Organized Documentation Structure:**
- [📘 Getting Started](docs/01_getting_started/) - Installation & Quick Start
- [📗 User Guides](docs/02_user_guides/) - How-to guides
- [📙 Architecture](docs/03_architecture/) - System design  
- [📕 Testing & Xray](docs/04_testing/) - Test docs, mapping, results
- [📔 Development](docs/05_development/) - Contributing & standards
- [📓 Project Management](docs/06_project_management/) - Work plans, meetings
- [📒 Infrastructure](docs/07_infrastructure/) - K8s, MongoDB, RabbitMQ
- [🗂️ Archive](docs/08_archive/) - Historical documents

### Quick Links to Legacy Docs

- **Testing Guide:** `documentation/testing/REALTIME_POD_MONITORING.md`
- **Infrastructure:** `documentation/infrastructure/GRPC_JOB_LIFECYCLE.md`
- **Configuration:** `documentation/configuration/`
- **API Reference:** `documentation/testing/API_MIGRATION_LOG.md`

---

## 🛠️ Development

### Adding New Tests

1. Create test file in appropriate directory:
   ```python
   # be_focus_server_tests/integration/api/test_new_feature.py
   import pytest
   from src.apis.focus_server_api import FocusServerAPI
   
   def test_new_feature(focus_server_api):
       response = focus_server_api.get_channels()
       assert response.status_code == 200
   ```

2. Run with monitoring:
   ```bash
   pytest be_focus_server_tests/integration/api/test_new_feature.py --monitor-pods -v
   ```

### Using Pod Monitoring in Tests

```python
def test_with_validation(get_test_pod_logs, assert_no_pod_errors):
    # Test code...
    response = focus_server_api.configure(payload)
    
    # Validate logs
    logs = get_test_pod_logs()
    assert "Successfully processed" in str(logs)
    
    # Assert no errors in any pod
    assert_no_pod_errors()
```

---

## ⚙️ CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests with monitoring
        run: pytest be_focus_server_tests/ --monitor-pods -v
```

---

## 🐛 Troubleshooting

### Common Issues

**1. SSH Connection Failed**
```bash
# Verify SSH configuration
ssh prisma@10.10.100.113
```

**2. MongoDB Connection Failed**
```bash
# Test MongoDB connection
mongo mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma
```

**3. Focus Server 500 Errors**
```bash
# Check Kubernetes pods
ssh prisma@10.10.100.113
kubectl get pods -n panda
```

**4. Too Many Pending gRPC Jobs**
```bash
# Delete pending jobs
kubectl delete pods -n panda --field-selector=status.phase=Pending
```

**See:** `documentation/infrastructure/GRPC_JOB_LIFECYCLE.md`

---

## 📈 System Requirements

### GPU Requirements
Each gRPC job requires:
```yaml
resources:
  limits:
    nvidia.com/gpu.shared: 1
```

### Kubernetes Resources
- **Namespace:** `panda`
- **Worker Node:** `10.10.100.113`
- **Max Concurrent Jobs:** 30 (MaxWindows)

---

## 🔐 Security

**Credentials in Config:**
- Stored in `config/environments.yaml`
- For automation purposes only
- **Do not commit sensitive data to public repos**

---


## Status

✅ **Production Ready**

**Environment:** `new_production` only  
**Pod Monitoring:** Fully implemented  
**Test Coverage:** API, Infrastructure, Performance  
**Documentation:** Complete
