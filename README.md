# Focus Server Automation Framework

**Production-grade test automation framework for Prisma Photonics Focus Server**

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Pytest](https://img.shields.io/badge/pytest-8.x-green.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Testing](#testing)
- [Development](#development)
- [Contributing](#contributing)

---

## 🎯 Overview

This project provides comprehensive test automation for the Focus Server system, including:

- ✅ **Unit Tests** - Core functionality validation
- ✅ **Integration Tests** - System component interaction
- ✅ **API Tests** - REST API contract testing
- ✅ **Load Tests** - Performance and scalability testing with Locust
- ✅ **UI Tests** - End-to-end user interface testing with Playwright
- ✅ **Infrastructure Monitoring** - K8s pods, MongoDB, RabbitMQ health checks
- ✅ **Automated Reporting** - Jira/Xray integration for test management

---

## 📁 Project Structure

```
focus_server_automation/
│
├── 📂 src/                          # Source code for automation framework
│   ├── api/                         # API client implementations
│   ├── database/                    # MongoDB helpers and queries
│   ├── messaging/                   # RabbitMQ message handlers
│   ├── kubernetes/                  # K8s pod management utilities
│   └── utils/                       # Common utilities and helpers
│
├── 📂 tests/                        # All test suites
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   │   ├── api/                     # API integration tests
│   │   ├── database/                # MongoDB integration tests
│   │   └── infrastructure/          # Infrastructure tests
│   └── ui/                          # Playwright UI tests
│
├── 📂 focus_server_api_load_tests/  # Locust load testing
│   ├── focus_api_tests/             # API contract tests
│   ├── load_tests/                  # Load test scenarios
│   └── reports/                     # Generated load test reports
│
├── 📂 config/                       # Configuration files
│   ├── environments.yaml            # Environment configurations
│   ├── settings.yaml                # Framework settings
│   └── *.json                       # Various config files
│
├── 📂 scripts/                      # Utility scripts
│   ├── setup/                       # Setup and installation scripts
│   ├── deployment/                  # Deployment helpers
│   └── utilities/                   # Misc automation scripts
│
├── 📂 documentation/                # All documentation (organized)
│   ├── guides/                      # User guides and how-tos
│   ├── setup/                       # Installation and setup instructions
│   ├── infrastructure/              # Infrastructure documentation
│   ├── testing/                     # Testing documentation
│   ├── jira/                        # Jira/Xray integration docs
│   └── archive/                     # Archived/legacy documentation
│
├── 📂 docs/                         # Original docs folder (reference)
│   ├── API docs (PDFs)
│   ├── Technical specs
│   └── Legacy documentation
│
├── 📂 pz/                           # PZ codebase (from Bitbucket)
│   └── Latest production code from prismaphotonics/pz
│
├── 📂 external/                     # External integrations
│   └── pz_integration.py            # PZ system integration
│
├── 📂 reports/                      # Test execution reports
│   ├── pytest-reports/
│   ├── locust-reports/
│   └── playwright-reports/
│
├── 📄 README.md                     # This file
├── 📄 requirements.txt              # Python dependencies
├── 📄 pytest.ini                    # Pytest configuration
├── 📄 setup.py                      # Package setup
└── 📄 .gitignore                    # Git ignore rules
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Git**
- **Access to Kubernetes cluster** (panda namespace)
- **MongoDB connection** (10.10.100.108:27017)
- **RabbitMQ access** (10.10.100.107:5672)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd focus_server_automation

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
. .\set_production_env.ps1  # PowerShell
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/unit/ -v                      # Unit tests
pytest tests/integration/ -v               # Integration tests
pytest focus_server_api_load_tests/ -v     # API contract tests

# Run load tests
cd focus_server_api_load_tests/load_tests
locust -f locust_focus_server.py
# Open http://localhost:8089
```

### Monitoring (K9s)

```bash
# Connect to K8s cluster
ssh root@10.10.100.3
ssh prisma@10.10.100.113
k9s -n panda

# Or use the helper script
.\connect_k9s.ps1 -Mode quick
```

---

## 📚 Documentation

All documentation is organized in the `documentation/` folder:

### 🔧 Guides (`documentation/guides/`)

Quick-reference guides for common tasks:

- **[K9S Connection Guide](documentation/guides/K9S_CONNECTION_GUIDE.md)** - Connect to Kubernetes pods
- **[Monitoring Logs Guide](documentation/guides/MONITORING_LOGS_GUIDE.md)** - Comprehensive log monitoring
- **[Quick Start - New Production](documentation/guides/QUICK_START_NEW_PRODUCTION.md)** - Get started in 2 minutes
- **[Update PZ Code](documentation/guides/UPDATE_PZ_CODE_FROM_BITBUCKET.md)** - Update PZ codebase from Bitbucket

### ⚙️ Setup (`documentation/setup/`)

Installation and configuration instructions:

- **[PandaApp Installation Guide](documentation/setup/PANDA_APP_INSTALLATION_GUIDE_HE.md)** (Hebrew)
- **[Automated Installation Guide](documentation/setup/AUTOMATED_INSTALLATION_GUIDE_HE.md)** (Hebrew)
- **[.NET 9 Installation](documentation/setup/INSTALL_DOTNET9_GUIDE_HE.md)** (Hebrew)
- **[New Environment Setup](documentation/setup/NEW_STAGING_ENVIRONMENT_GUIDE_HE.md)** (Hebrew)

### 🏗️ Infrastructure (`documentation/infrastructure/`)

Infrastructure and environment documentation:

- **[Complete Infrastructure Summary](documentation/infrastructure/COMPLETE_INFRASTRUCTURE_SUMMARY.md)**
- **[New Environment Master Document](documentation/infrastructure/NEW_ENVIRONMENT_MASTER_DOCUMENT.md)**
- **[Test Configuration Summary](documentation/infrastructure/TEST_CONFIGURATION_SUMMARY.md)**
- **[Automation Config Summary](documentation/infrastructure/AUTOMATION_CONFIG_SUMMARY_HE.md)** (Hebrew)

### 🧪 Testing (`documentation/testing/`)

Testing guides and documentation:

- **[Test Suite Inventory](documentation/testing/TEST_SUITE_INVENTORY.md)** - Complete test catalog
- **[API Healing Implementation](documentation/testing/API_HEALING_IMPLEMENTATION_SUMMARY.md)**
- **[Playwright AI Guide](documentation/testing/PLAYWRIGHT_AI_IMPLEMENTATION_SUMMARY.md)**
- **[SingleChannel View Tests](documentation/testing/SINGLECHANNEL_VIEW_TEST_QUICKSTART.md)**
- **[Integration Tests Analysis](documentation/testing/INTEGRATION_TESTS_ANALYSIS.md)**

### 📊 Jira/Xray (`documentation/jira/`)

Issue tracking and test management:

- **[Jira Tickets Overview](documentation/jira/JIRA_TICKETS_FOCUS_SERVER_AUTOMATION.md)**
- **[Xray Import Guide](documentation/jira/XRAY_IMPORT_GUIDE.md)**
- **[Bug Reports](documentation/jira/BUG_TICKETS_README.md)**
- **[Test Data Reports](documentation/jira/T_DATA_002_INDEX.md)**

### 📦 Archive (`documentation/archive/`)

Legacy and archived documentation for reference.

---

## 🔴 Known Issues & Important Notes

### MongoDB Collections - CRITICAL

**Issue discovered:** Jira Xray tests reference MongoDB collections as `node2` and `node4`, but the actual system uses **GUID-based dynamic collection names**.

- ✅ **Automation code is CORRECT** - discovers collection names dynamically from `base_paths`
- ❌ **Jira documentation is OUTDATED** - needs updates to reflect reality
- 📄 **Full explanation:** `MONGODB_COLLECTIONS_CLARIFICATION.md` (detailed technical document)
- 📋 **Quick reference:** `MONGODB_NODE2_NODE4_ISSUE_SUMMARY.md` (executive summary)

**Affected Jira tickets:** PZ-13598, PZ-13684, PZ-13685, PZ-13686, PZ-13687, PZ-13705

**Example:**
```python
# Jira says (WRONG):
collections = ["base_paths", "node2", "node4"]

# Reality (CORRECT):
collections = [
    "base_paths",                              # Fixed name
    "77e49b5d-e06a-4aae-a33e-17117418151c",   # GUID (dynamic!)
    "77e49b5d-e06a-4aae-a33e-17117418151c-unrecognized_recordings"
]
```

---

## 🧪 Testing

### Test Suites

| Suite | Location | Description | Command |
|-------|----------|-------------|---------|
| **Unit Tests** | `tests/unit/` | Core functionality | `pytest tests/unit/ -v` |
| **Integration Tests** | `tests/integration/` | Component interaction | `pytest tests/integration/ -v` |
| **API Contract Tests** | `focus_server_api_load_tests/focus_api_tests/` | API validation | `pytest focus_server_api_load_tests/focus_api_tests/ -v` |
| **Load Tests** | `focus_server_api_load_tests/load_tests/` | Performance testing | `locust -f locust_focus_server.py` |
| **UI Tests** | `tests/ui/` | End-to-end UI | `pytest tests/ui/ -v` |

### Test Environments

Configured in `config/environments.yaml`:

- **local**: Local development (via port-forward)
- **staging**: Staging environment (10.10.10.150)
- **new_production**: Production environment (panda namespace)
  - Backend: `https://10.10.100.100/focus-server/`
  - MongoDB: `mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma`
  - RabbitMQ: `10.10.100.107:5672`
  - K8s: `https://10.10.100.102:6443` (namespace: `panda`)

### Running Tests Against Specific Environment

```bash
# Set environment
. .\set_production_env.ps1

# Verify configuration
echo $env:FOCUS_BASE_URL
echo $env:MONGODB_URI

# Run tests
pytest tests/ -v
```

---

## 🔧 Development

### Project Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install in editable mode
pip install -e .

# Install dev dependencies
pip install -r requirements-dev.txt  # If exists
```

### Code Structure

- **src/**: Framework source code
  - Follow PEP 8 style guide
  - Type hints required
  - Docstrings for all public methods
  
- **tests/**: Test code
  - Use pytest fixtures
  - Keep tests isolated
  - Mock external dependencies

### Adding New Tests

1. Identify test category (unit/integration/load/ui)
2. Create test file in appropriate directory
3. Follow naming convention: `test_*.py`
4. Use fixtures from `conftest.py`
5. Document test purpose and expected behavior

### Configuration

- **environments.yaml**: Add new environments
- **settings.yaml**: Framework-level settings
- Environment variables: Use `.env` or `set_production_env.ps1`

---

## 🤝 Contributing

### Guidelines

1. **Branching**: Use feature branches (`feature/your-feature-name`)
2. **Commits**: Write clear, descriptive commit messages
3. **Testing**: Ensure all tests pass before committing
4. **Documentation**: Update relevant docs with code changes
5. **Code Review**: Submit PRs for review before merging

### Pull Request Process

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Update documentation
6. Submit PR with description

---

## 📞 Support & Contact

- **Documentation**: See `documentation/` folder
- **Issues**: Check `documentation/jira/` for known issues
- **Questions**: Refer to guides in `documentation/guides/`

---

## 📜 License

Proprietary - Prisma Photonics Ltd.

---

## 🎯 Key Features

### 🔄 CI/CD Integration
- Automated test execution
- Jira/Xray reporting
- Performance metrics tracking

### 📊 Monitoring & Observability
- K9s integration for pod monitoring
- MongoDB health checks
- RabbitMQ message queue monitoring
- Prometheus metrics (if configured)

### 🛠️ Utilities
- Automated environment setup
- Configuration management
- Log collection and analysis
- Test data generation

### 🔐 Security
- Secure credential management
- SSH tunneling for remote access
- SSL/TLS support
- Authentication handling

---

## 📈 Project Status

**Current Version**: 1.0.0  
**Last Updated**: October 2025  
**Status**: ✅ Active Development

---

## 🗺️ Roadmap

- [ ] Expand UI test coverage
- [ ] Add more load test scenarios
- [ ] Integrate with CI/CD pipeline
- [ ] Enhance reporting dashboard
- [ ] Add more MongoDB test utilities

---

**Made with ❤️ by Prisma Photonics QA Team**
