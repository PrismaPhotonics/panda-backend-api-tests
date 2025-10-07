# Focus Server Automation Framework

## 🎯 Overview

**Professional Test Automation Framework** for Focus Server testing with comprehensive capabilities for API, infrastructure, and integration scenarios.

### 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Automation Framework                │
├─────────────────────────────────────────────────────────────┤
│  Test Suites                                                │
│  ├── Unit Tests          ├── Integration Tests             │
│  ├── API Tests           ├── Infrastructure Tests          │
│  └── Performance Tests   └── Regression Tests              │
├─────────────────────────────────────────────────────────────┤
│  Core Framework                                            │
│  ├── Base Test Classes   ├── API Clients                   │
│  ├── Infrastructure Mgmt ├── Configuration Management      │
│  └── Utilities & Helpers └── Exception Handling            │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                      │
│  ├── Kubernetes Manager  ├── MongoDB Manager               │
│  ├── RabbitMQ Manager    ├── SSH Manager                   │
│  └── Monitoring Manager  └── Environment Management        │
├─────────────────────────────────────────────────────────────┤
│  Target System                                            │
│  ├── Focus Server API    ├── MongoDB Database             │
│  ├── RabbitMQ Message    ├── Kubernetes Cluster           │
│  └── Infrastructure      └── Monitoring Systems           │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **kubectl** access to target cluster
- **Docker** (optional, for containerized execution)
- **SSH** access to infrastructure nodes

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd focus_server_automation_framework
```

2. **Initialize PZ development repository (submodule):**
```bash
# Clone PZ repository for latest production code access
git submodule update --init --recursive
```

3. **Create virtual environment:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Configure environment:**
```bash
# Set environment (staging/production/local)
export FOCUS_TEST_ENVIRONMENT=staging

# Or edit config/environments.yaml
```

6. **Validate setup:**
```bash
# Run unit tests
python scripts/run_tests.py --test-type unit --dry-run

# Verify PZ integration
pytest -m pz -v
```

### Running Tests

#### 🧪 Basic Test Execution

```bash
# Run all integration tests
python scripts/run_tests.py --test-type integration

# Run infrastructure tests with resilience markers
python scripts/run_tests.py --test-type infrastructure --markers resilience

# Run specific test file
python scripts/run_tests.py --test-paths tests/integration/infrastructure/test_mongodb_outage_resilience.py

# Run tests in parallel
python scripts/run_tests.py --test-type integration --parallel
```

#### 🎯 Targeted Test Execution

```bash
# MongoDB outage resilience tests
python scripts/run_tests.py --test-type infrastructure --markers "mongodb_outage and resilience"

# API validation tests
python scripts/run_tests.py --test-type api --markers "validation and critical"

# Performance tests
python scripts/run_tests.py --test-type integration --markers performance
```

## 📁 Project Structure

```
focus_server_automation_framework/
│
├── config/                     # Configuration Management
│   ├── settings.yaml          # Global framework settings
│   ├── environments.yaml      # Environment-specific configs
│   └── config_manager.py      # Configuration manager
│
├── external/                   # External Dependencies
│   ├── pz_integration.py      # PZ repository integration
│   └── pz/                    # PZ development repo (submodule)
│       └── microservices/     # 40+ PZ microservices
│
├── src/                        # Framework Source Code
│   ├── core/                  # Core framework components
│   │   ├── base_test.py       # Base test class
│   │   ├── api_client.py      # HTTP client base
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── utils/             # Utilities and helpers
│   │
│   ├── apis/                  # API Layer
│   │   ├── focus_server_api.py # Focus Server client
│   │   ├── mongodb_api.py     # MongoDB operations
│   │   └── rabbitmq_api.py    # RabbitMQ operations
│   │
│   ├── infrastructure/        # Infrastructure Management
│   │   ├── kubernetes_manager.py # K8s operations
│   │   ├── mongodb_manager.py    # MongoDB management
│   │   └── ssh_manager.py        # SSH operations
│   │
│   └── models/                # Data Models
│       └── focus_server_models.py # API data models
│
├── tests/                      # Test Suites
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   │   ├── api/              # API integration tests
│   │   ├── infrastructure/   # Infrastructure tests
│   │   └── end_to_end/       # E2E tests
│   ├── performance/           # Performance tests
│   └── regression/            # Regression tests
│
├── scripts/                   # Utility Scripts
│   ├── run_tests.py          # Professional test runner
│   └── sync_pz_code.py       # PZ repository sync utility
│
├── reports/                   # Test Reports
│   ├── html-reports/         # HTML test reports
│   ├── allure-results/       # Allure reports
│   └── logs/                 # Test execution logs
│
└── docs/                      # Documentation
    ├── API_DOCUMENTATION.md  # API documentation
    ├── TESTING_GUIDE.md      # Testing guide
    ├── INFRASTRUCTURE_GUIDE.md # Infrastructure guide
    └── PZ_INTEGRATION_GUIDE.md # PZ integration guide
```

## 🎯 Key Test Scenarios

### MongoDB Outage Resilience (PZ-13604)

**Objective**: Ensure dependency outage fails fast and clean without launching processing.

```python
def test_mongodb_scale_down_outage_returns_503_no_orchestration(self):
    """Test MongoDB scale-down outage returns 503 with no orchestration."""
    
    # 1. Scale down MongoDB deployment to 0 replicas
    self.mongodb_manager.create_outage_scale_down()
    
    # 2. Send POST /configure request with history payload
    with pytest.raises(APIClientException) as exc_info:
        self.api.configure_streaming_job(valid_history_request)
    
    # 3. Verify 503 response with no side effects
    assert exc_info.value.status_code == 503
    assert response_time < 5.0  # Fail fast
```

**Test Coverage**:
- ✅ Scale-down outage simulation
- ✅ Pod deletion outage simulation  
- ✅ Network blocking outage simulation
- ✅ Response time validation (<5s)
- ✅ Side effects verification (no K8s jobs/RabbitMQ queues)
- ✅ Service recovery testing
- ✅ Health monitoring validation

### PZ Development Repository Integration

**Objective**: Enable automated tests to run against the latest production code from PZ development team.

```python
def test_using_pz_code(pz_integration):
    """Test using latest PZ production code."""
    
    # Access PZ microservices
    focus_server_path = pz_integration.get_microservice_path('focus_server')
    
    # List all available microservices
    services = pz_integration.list_microservices()  # 40+ services
    
    # Get version info
    version = pz_integration.get_version_info()
    logger.info(f"Testing against PZ commit: {version['commit']}")
```

**Key Features**:
- 🔄 Git Submodule integration with PZ repository
- 📦 Access to 40+ PZ microservices
- 🔄 Automatic synchronization with development
- 📊 Version tracking and reporting
- 🧪 Pytest integration with automatic PYTHONPATH setup

**Quick Commands**:
```bash
# Sync PZ to latest version
python scripts/sync_pz_code.py --sync

# Check PZ status
python scripts/sync_pz_code.py --status

# Run PZ integration tests
pytest -m pz -v
```

📖 **Full Documentation**: [PZ Integration Guide](docs/PZ_INTEGRATION_GUIDE.md)

## 📊 Reporting

### HTML Reports
- **Location**: `reports/html-reports/`
- **Features**: Detailed test results with screenshots and logs
- **Access**: Open `test_report.html` in browser

### Allure Reports
- **Location**: `reports/allure-results/`
- **Features**: Rich reporting with trends and analytics
- **Access**: `allure serve reports/allure-results/`

### JUnit XML
- **Location**: `reports/junit-results.xml`
- **Features**: CI/CD integration format
- **Usage**: Jenkins, GitLab CI, GitHub Actions

## 🔒 Security & Safety

### Production Safety
- **Read-only operations** in production environment
- **Outage tests disabled** by default in production
- **Credential management** via environment variables
- **Audit logging** for all infrastructure operations

### Staging Safety
- **Automatic cleanup** after test execution
- **Resource restoration** on test failure
- **Rollback procedures** for failed operations
- **Health checks** before and after tests

## 🚀 CI/CD Integration

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Setup') {
            steps {
                sh 'python scripts/run_tests.py --test-type unit'
            }
        }
        stage('Integration Tests') {
            steps {
                sh 'python scripts/run_tests.py --test-type integration --environment staging'
            }
        }
        stage('Infrastructure Tests') {
            when {
                branch 'develop'
            }
            steps {
                sh 'python scripts/run_tests.py --test-type infrastructure --markers resilience'
            }
        }
    }
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports/html-reports',
                reportFiles: 'test_report.html',
                reportName: 'Test Report'
            ])
        }
    }
}
```

## 📈 Performance Metrics

### Response Time Thresholds
- **API calls**: < 5 seconds
- **Infrastructure operations**: < 30 seconds
- **Test execution**: < 30 minutes

### Test Coverage Requirements
- **Unit tests**: > 80% coverage
- **Integration tests**: > 70% coverage
- **Critical paths**: 100% coverage

## 🛠️ Development

### Adding New Tests

1. **Create test file** in appropriate directory:
```bash
touch tests/integration/api/test_new_feature.py
```

2. **Implement test class**:
```python
class TestNewFeature(BaseTest):
    @pytest.mark.integration
    @pytest.mark.api
    def test_new_feature_scenario(self, focus_server_api):
        # Test implementation
        pass
```

3. **Add markers** to `pytest.ini`:
```ini
markers =
    new_feature: New feature tests
```

## 📚 Documentation

- **[API Documentation](docs/API_DOCUMENTATION.md)**: Complete API reference
- **[Testing Guide](docs/TESTING_GUIDE.md)**: How to write and run tests
- **[Infrastructure Guide](docs/INFRASTRUCTURE_GUIDE.md)**: Infrastructure setup and management
- **[PZ Integration Guide](docs/PZ_INTEGRATION_GUIDE.md)**: PZ development repository integration
- **[Contributing Guide](docs/CONTRIBUTING.md)**: How to contribute to the framework

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Write tests** for your changes
4. **Run test suite**: `python scripts/run_tests.py --test-type all`
5. **Submit pull request** with detailed description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Senior QA Automation Architect**: Framework design and implementation
- **QA Engineers**: Test development and maintenance
- **DevOps Engineers**: Infrastructure and CI/CD integration

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-05  
**Status**: Production Ready ✅