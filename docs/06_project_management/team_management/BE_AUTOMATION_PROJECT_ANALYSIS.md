# BE Automation Project Analysis - Focus Server Automation Framework
## Complete Structure, Tools & Infrastructure

**Date:** 2025-11-09  
**Project:** Focus Server Automation Framework  
**Location:** `C:\Projects\focus_server_automation\`

---

## 📁 Directory Structure

### Complete Project Structure:

```
focus_server_automation/
├── config/                          # Configuration files
│   ├── environments.yaml            # Environment settings (staging, production, local)
│   ├── settings.yaml                # General test settings
│   ├── config_manager.py            # Central configuration manager
│   └── usersettings.new_production_client.json  # Client configuration
│
├── src/                             # Source code
│   ├── apis/                        # API clients
│   │   ├── __init__.py
│   │   ├── focus_server_api.py      # REST API client for Focus Server
│   │   ├── baby_analyzer_mq_client.py  # RabbitMQ client for Baby Analyzer
│   │   └── base_api_client.py       # Base API client (shared)
│   │
│   ├── core/                        # Core utilities
│   │   ├── __init__.py
│   │   ├── api_client.py            # Base API client with retry logic
│   │   ├── base_test.py             # Base test class for all tests
│   │   ├── circuit_breaker.py       # Circuit breaker pattern
│   │   └── exceptions.py            # Custom exceptions
│   │
│   ├── infrastructure/              # Infrastructure managers
│   │   ├── __init__.py
│   │   ├── kubernetes_manager.py   # Kubernetes management (pods, jobs, services)
│   │   ├── kubernetes_manager_fixed.py  # Fixed version
│   │   ├── mongodb_manager.py       # MongoDB management (connections, outages)
│   │   ├── mongodb_monitoring_agent.py  # MongoDB monitoring agent
│   │   ├── rabbitmq_manager.py      # RabbitMQ management (connections, queues)
│   │   ├── ssh_manager.py           # SSH management (remote commands, tunnels)
│   │   └── focus_server_manager.py  # Focus Server management
│   │
│   ├── models/                     # Data models (Pydantic)
│   │   ├── __init__.py
│   │   ├── focus_server_models.py  # Models for Focus Server API
│   │   └── baby_analyzer_models.py  # Models for Baby Analyzer
│   │
│   ├── reporting/                  # Reporting and monitoring
│   │   ├── __init__.py
│   │   ├── pytest_integration.py   # Integration with pytest
│   │   └── test_report_generator.py  # Test report generation
│   │
│   └── utils/                      # Utility tools
│       ├── __init__.py
│       ├── helpers.py              # General helper functions
│       ├── pod_logs_collector.py   # Pod log collection
│       ├── realtime_pod_monitor.py # Real-time log monitoring
│       ├── sanity_checker.py       # Pre-execution sanity checks
│       ├── token_manager.py        # Token management
│       └── validators.py           # Validations
│
├── tests/                          # Test files
│   ├── conftest.py                 # Pytest fixtures and global setup
│   ├── conftest_xray.py            # Xray integration fixtures
│   ├── pytest_logging_plugin.py   # Logging plugin
│   ├── README.md                   # Test documentation
│   │
│   ├── unit/                       # Unit tests
│   │   ├── __init__.py
│   │   ├── test_basic_functionality.py
│   │   ├── test_config_loading.py
│   │   ├── test_models_validation.py
│   │   └── test_validators.py
│   │
│   ├── integration/                # Integration tests
│   │   ├── __init__.py
│   │   ├── README.md
│   │   │
│   │   ├── api/                    # API tests
│   │   │   ├── __init__.py
│   │   │   ├── README.md
│   │   │   ├── test_api_endpoints_additional.py
│   │   │   ├── test_api_endpoints_high_priority.py
│   │   │   ├── test_config_task_endpoint.py
│   │   │   ├── test_config_validation_high_priority.py
│   │   │   ├── test_config_validation_nfft_frequency.py
│   │   │   ├── test_configure_endpoint.py
│   │   │   ├── test_dynamic_roi_adjustment.py
│   │   │   ├── test_health_check.py
│   │   │   ├── test_historic_playback_additional.py
│   │   │   ├── test_historic_playback_e2e.py
│   │   │   ├── test_live_monitoring_flow.py
│   │   │   ├── test_live_streaming_stability.py
│   │   │   ├── test_nfft_overlap_edge_case.py
│   │   │   ├── test_orchestration_validation.py
│   │   │   ├── test_prelaunch_validations.py
│   │   │   ├── test_singlechannel_view_mapping.py
│   │   │   ├── test_task_metadata_endpoint.py
│   │   │   ├── test_view_type_validation.py
│   │   │   ├── test_waterfall_endpoint.py
│   │   │   └── test_waterfall_view.py
│   │   │
│   │   ├── calculations/           # Calculation tests
│   │   │   ├── __init__.py
│   │   │   ├── README.md
│   │   │   └── test_system_calculations.py
│   │   │
│   │   ├── data_quality/          # Data quality tests
│   │   │   ├── __init__.py
│   │   │   ├── test_data_completeness.py
│   │   │   ├── test_data_consistency.py
│   │   │   └── test_data_integrity.py
│   │   │
│   │   ├── e2e/                   # End-to-End tests
│   │   │   ├── __pycache__/
│   │   │   └── test_configure_metadata_grpc_flow.py
│   │   │
│   │   ├── error_handling/        # Error handling tests
│   │   │   ├── __init__.py
│   │   │   ├── test_http_error_codes.py
│   │   │   ├── test_invalid_payloads.py
│   │   │   └── test_network_errors.py
│   │   │
│   │   ├── load/                  # Load tests
│   │   │   └── [6 test files]
│   │   │
│   │   ├── performance/           # Performance tests
│   │   │   ├── [8 test files + README.md]
│   │   │
│   │   └── security/              # Security tests
│   │       └── [7 test files]
│   │
│   ├── infrastructure/            # Infrastructure tests
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── test_basic_connectivity.py
│   │   ├── test_external_connectivity.py
│   │   ├── test_k8s_job_lifecycle.py
│   │   ├── test_mongodb_monitoring_agent.py
│   │   ├── test_pz_integration.py
│   │   ├── test_rabbitmq_connectivity.py
│   │   ├── test_rabbitmq_outage_handling.py
│   │   ├── test_system_behavior.py
│   │   └── resilience/            # Resilience tests
│   │       ├── __init__.py
│   │       ├── test_focus_server_pod_resilience.py
│   │       ├── test_mongodb_pod_resilience.py
│   │       ├── test_multiple_pods_resilience.py
│   │       ├── test_pod_recovery_scenarios.py
│   │       ├── test_rabbitmq_pod_resilience.py
│   │       └── test_segy_recorder_pod_resilience.py
│   │
│   ├── data_quality/             # Data quality tests (top level)
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── test_mongodb_data_quality.py
│   │   ├── test_mongodb_indexes_and_schema.py
│   │   ├── test_mongodb_recovery.py
│   │   ├── test_mongodb_schema_validation.py
│   │   └── test_recordings_classification.py
│   │
│   ├── load/                     # Load tests (top level)
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── README.md
│   │   └── test_job_capacity_limits.py
│   │
│   ├── performance/              # Performance tests (top level)
│   │   ├── __init__.py
│   │   ├── README.md
│   │   └── test_mongodb_outage_resilience.py
│   │
│   ├── security/                 # Security tests (top level)
│   │   ├── __init__.py
│   │   ├── README.md
│   │   └── test_malformed_input_handling.py
│   │
│   ├── stress/                   # Stress tests
│   │   ├── __init__.py
│   │   ├── README.md
│   │   └── test_extreme_configurations.py
│   │
│   ├── ui/                       # UI tests (Playwright)
│   │   ├── __init__.py
│   │   └── generated/            # Auto-generated tests
│   │       ├── __init__.py
│   │       ├── test_button_interactions.py
│   │       └── test_form_validation.py
│   │
│   ├── fixtures/                 # Shared fixtures
│   │   └── __init__.py
│   │
│   └── helpers/                  # Test helpers
│       └── __init__.py
│
├── scripts/                       # Utility scripts
│   ├── xray/                      # Xray scripts
│   │   ├── attach_evidence.py    # Attach evidence to Test Execution
│   │   └── get_test_plan_tests.py  # Fetch tests from Test Plan
│   │
│   ├── jira/                     # Jira scripts
│   │   └── [Jira integration files]
│   │
│   ├── api/                      # API scripts
│   │   └── [API test files]
│   │
│   ├── xray_upload.py            # Upload results to Xray
│   ├── quick_job_capacity_check.py  # Check job capacity
│   └── [200+ additional scripts]
│
├── external/                     # External integrations
│   ├── __init__.py
│   ├── pz/                       # PZ Development Repository (Git Submodule)
│   │   ├── microservices/        # PZ microservices
│   │   ├── bin/                  # Development tools
│   │   ├── CI-CD/                # CI/CD files
│   │   └── [Full PZ repo structure]
│   │
│   ├── jira/                     # Jira integration
│   │   ├── __init__.py
│   │   ├── jira_agent.py         # Jira API client
│   │   ├── jira_client.py        # Client wrapper
│   │   ├── bug_creator.py        # Bug creation
│   │   ├── bug_deduplication.py  # Bug deduplication
│   │   └── exceptions.py         # Custom exceptions
│   │
│   └── pz_integration.py         # Integration with PZ repository
│
├── docs/                         # Organized documentation
│   ├── 01_getting_started/      # Quick start
│   ├── 02_user_guides/          # User guides
│   ├── 03_architecture/         # Architecture
│   ├── 04_testing/              # Test documentation
│   ├── 05_development/          # Development guides
│   ├── 06_project_management/   # Project management
│   ├── 07_infrastructure/       # Infrastructure
│   └── 08_archive/              # Archive
│
├── .github/                      # GitHub Actions workflows
│   └── workflows/
│       ├── ci.yml                # Basic CI pipeline
│       ├── xray_full_integration.yml  # Full Xray integration
│       ├── xray_upload.yml       # Upload results to Xray
│       ├── focus-contract-tests.yml  # Contract tests
│       └── readme-check.yml      # README check
│
├── logs/                         # Generated logs
│   └── pod_logs/                 # Pod logs
│       ├── test_logs/            # Test-specific logs
│       ├── *_realtime.log        # Real-time logs
│       └── *_errors.log          # Error logs
│
├── reports/                      # Test reports
│   └── [Generated reports]
│
├── pytest.ini                    # pytest settings
├── requirements.txt              # Python dependencies
└── README.md                     # Main documentation
```

---

## 🛠️ Tools - What's Actually Used in Automation

### 📊 Tools Usage Summary

| Category | Tool | In Use? | Primary Usage |
|---------|-----|---------|-------------|
| **Testing** | pytest | ✅ Yes | Main test framework |
| **Testing** | playwright | ✅ Yes | UI tests (limited) |
| **HTTP** | requests | ✅ Yes | REST API calls (Focus Server, Xray) |
| **HTTP** | httpx | ❌ No | Not found in use |
| **HTTP** | beautifulsoup4 | ❌ No | Not found in use |
| **Infrastructure** | kubernetes | ✅ Yes | K8s cluster management |
| **Infrastructure** | pymongo | ✅ Yes | MongoDB connection |
| **Infrastructure** | pika | ✅ Yes | RabbitMQ connection |
| **Infrastructure** | paramiko | ✅ Yes | SSH connections |
| **Data** | pydantic | ✅ Yes | Data models and validation |
| **Data** | orjson | ❌ No | Not found in use |
| **Data** | pyyaml | ✅ Yes | Configuration reading |
| **Logging** | structlog | ❌ No | Not found in use |
| **Logging** | colorlog | ❌ No | Not found in use |
| **Monitoring** | psutil | ✅ Yes | System resource monitoring |
| **Integration** | jira | ✅ Yes | Jira integration |
| **Integration** | pytest-xray | ⚠️ Partial | Test mapping + direct requests |
| **Reporting** | allure-pytest | ❌ No | Not found in use |
| **Reporting** | jinja2 | ❌ No | Not found in use |

### ✅ Main Tools in Active Use:

1. **pytest** - Main test framework
2. **requests** - HTTP client for API calls
3. **kubernetes** - Kubernetes management
4. **pymongo** - MongoDB client
5. **paramiko** - SSH connections
6. **pydantic** - Data validation
7. **pyyaml** - Configuration parsing
8. **pika** - RabbitMQ client
9. **jira** - Jira integration
10. **psutil** - System monitoring
11. **playwright** - UI testing (limited)

### ❌ Tools Not Found in Use:

- httpx, beautifulsoup4, orjson, structlog, colorlog, allure-pytest, jinja2

---

> **Important Note:** This list includes only tools that are actually used in the code, as found in file inspection.

### 1. Testing Tools ✅ In Use

#### **pytest** ✅ **Actively Used**
- **Purpose:** Test execution framework
- **Version:** >=7.4.0
- **Actual Usage:**
  - All test files use `import pytest`
  - `tests/conftest.py` - Global fixtures definition
  - `src/core/base_test.py` - Base test class
- **Plugins in Use:**
  - `pytest-asyncio` - Async tests support
  - `pytest-timeout` - Test timeouts
  - `pytest-mock` - Mocking
  - `pytest-html` - HTML reports
  - `pytest-cov` - Code coverage
  - `pytest-json-report` - JSON reports
  - `pytest-xdist` - Parallel execution
- **Configuration:** `pytest.ini`
- **Markers:** 50+ markers defined (integration, api, infrastructure, etc.)

#### **Playwright** ✅ **Actively Used (Limited)**
- **Purpose:** UI automation (browser)
- **Version:** >=1.40.0
- **Actual Usage:**
  - `tests/ui/generated/test_button_interactions.py` - `from playwright.sync_api import Page, expect`
  - `tests/ui/generated/test_form_validation.py` - `from playwright.sync_api import Page, expect`
- **Note:** Used only in limited UI tests (generated tests)

### 2. API & HTTP Tools ✅ In Use

#### **requests** ✅ **Actively Used**
- **Purpose:** HTTP client for REST API calls
- **Version:** >=2.31.0
- **Actual Usage:**
  - `src/core/api_client.py` - `import requests` (Base API client)
  - `src/utils/token_manager.py` - `import requests` (Token management)
  - `scripts/xray_upload.py` - `import requests` (Xray API calls)
- **Usage:** All REST API calls to Focus Server and Xray

#### **httpx** ❌ **Not in Actual Use**
- **Note:** Appears in requirements.txt but no usage found in code

#### **beautifulsoup4** ❌ **Not in Actual Use**
- **Note:** Appears in requirements.txt but no usage found in code

### 3. Infrastructure Tools ✅ In Use

#### **kubernetes (Python Client)** ✅ **Actively Used**
- **Purpose:** Kubernetes cluster management
- **Version:** >=28.1.0
- **Actual Usage:**
  - `src/infrastructure/kubernetes_manager.py` - `from kubernetes import client, config`
  - `src/infrastructure/mongodb_manager.py` - `from kubernetes import client, config`
  - `tests/infrastructure/test_basic_connectivity.py` - `from kubernetes import client, config`
- **Usage:**
  - Pod management
  - Job lifecycle
  - Service discovery
  - Log retrieval
  - Deployment management

#### **pymongo** ✅ **Actively Used**
- **Purpose:** MongoDB client
- **Version:** >=4.6.0
- **Actual Usage:**
  - `src/infrastructure/mongodb_manager.py` - `import pymongo`
  - `src/infrastructure/mongodb_monitoring_agent.py` - `import pymongo`
  - `tests/infrastructure/test_basic_connectivity.py` - `import pymongo`
  - `tests/data_quality/test_mongodb_data_quality.py` - `import pymongo`
- **Usage:**
  - MongoDB connection
  - Queries
  - Monitoring
  - Outage simulation

#### **pika** ✅ **Actively Used**
- **Purpose:** RabbitMQ client
- **Version:** >=1.3.0
- **Actual Usage:**
  - `src/apis/baby_analyzer_mq_client.py` - `import pika`
  - `tests/infrastructure/test_rabbitmq_connectivity.py` - `import pika`
- **Usage:**
  - RabbitMQ connection
  - Publishing/Consuming messages
  - Queue management

#### **paramiko** ✅ **Actively Used**
- **Purpose:** SSH client
- **Version:** >=3.3.1
- **Actual Usage:**
  - `src/infrastructure/ssh_manager.py` - `import paramiko`
  - `src/infrastructure/rabbitmq_manager.py` - `import paramiko` (try/except)
  - `src/utils/realtime_pod_monitor.py` - `import paramiko`
  - `src/utils/pod_logs_collector.py` - `import paramiko`
  - `tests/infrastructure/test_basic_connectivity.py` - `import paramiko`
- **Usage:**
  - SSH connection to worker nodes
  - Running kubectl commands
  - Port forwarding
  - Tunnel management
  - Pod log collection

### 4. Data Processing Tools ✅ In Use

#### **pydantic** ✅ **Actively Used**
- **Purpose:** Data validation and serialization
- **Version:** >=2.4.0
- **Actual Usage:**
  - `src/models/focus_server_models.py` - `from pydantic import BaseModel, Field, field_validator`
  - `src/models/baby_analyzer_models.py` - Uses Pydantic models
- **Usage:**
  - Data models for API requests/responses
  - Payload validation
  - Type safety

#### **orjson** ❌ **Not in Actual Use**
- **Note:** Appears in requirements.txt but no usage found in code (using built-in json)

#### **pyyaml** ✅ **Actively Used**
- **Purpose:** YAML file parsing
- **Version:** >=6.0.1
- **Actual Usage:**
  - `config/config_manager.py` - `import yaml` (reading environments.yaml and settings.yaml)
- **Usage:** Reading all configuration files

### 5. Monitoring & Logging Tools

#### **structlog** ❌ **Not in Actual Use**
- **Note:** Appears in requirements.txt but no usage found in code (using built-in logging)

#### **colorlog** ❌ **Not in Actual Use**
- **Note:** Appears in requirements.txt but no usage found in code

#### **psutil** ✅ **Actively Used**
- **Purpose:** System monitoring
- **Version:** >=5.9.6
- **Actual Usage:**
  - `tests/infrastructure/test_system_behavior.py` - `import psutil`
  - `tests/load/test_job_capacity_limits.py` - `import psutil`
- **Usage:** System resource monitoring (CPU, memory)

### 6. Development Tools

#### **black**
- **Purpose:** Code formatter
- **Version:** >=23.7.0

#### **flake8**
- **Purpose:** Linter
- **Version:** >=6.0.0

#### **mypy**
- **Purpose:** Type checker
- **Version:** >=1.5.0

#### **isort**
- **Purpose:** Import sorter
- **Version:** >=5.12.0

### 7. Security Tools

#### **cryptography**
- **Purpose:** Cryptographic operations
- **Version:** >=41.0.7

#### **bandit**
- **Purpose:** Security linter
- **Version:** >=1.7.5

### 8. Integration Tools ✅ In Use

#### **jira (Python Client)** ✅ **Actively Used**
- **Purpose:** Jira API client
- **Version:** >=3.5.0
- **Actual Usage:**
  - `external/jira/jira_agent.py` - JiraAgent class
  - `external/jira/jira_client.py` - JiraClient wrapper
  - `src/reporting/test_report_generator.py` - Uses Jira integration
- **Usage:**
  - Creating/updating tickets
  - Searching tickets
  - Bug management
  - Bug deduplication

#### **pytest-xray** ⚠️ **Partially Used**
- **Purpose:** Xray integration
- **Version:** >=3.0.0
- **Actual Usage:**
  - `tests/conftest_xray.py` - Xray fixtures
  - Markers: `@pytest.mark.xray(test_key="PZ-XXXXX")`
- **Note:** Also using `requests` directly to Xray API (`scripts/xray_upload.py`)

### 9. Reporting Tools

#### **allure-pytest** ❌ **Not in Actual Use**
- **Note:** Appears in requirements.txt but no usage found in code

#### **jinja2** ❌ **Not in Actual Use**
- **Note:** Appears in requirements.txt but no usage found in code

---

## 🏗️ Infrastructure

### 1. Focus Server Backend

#### **Staging Environment:**
- **URL:** `https://10.10.10.100/focus-server/`
- **Frontend:** `https://10.10.10.100/liveView`
- **API:** `https://10.10.10.100/prisma/api/internal/sites/prisma-210-1000`
- **Site ID:** `prisma-210-1000`

#### **Production Environment:**
- **URL:** `https://10.10.100.100/focus-server/`
- **Frontend:** `https://10.10.100.100/liveView`
- **API:** `https://10.10.100.100/prisma/api/internal/sites/prisma-210-1000`
- **Site ID:** `prisma-210-1000`

#### **Endpoints:**
- `POST /configure` - Configure streaming job
- `GET /channels` - Get channel list
- `GET /metadata` - Get metadata
- `GET /ack` - Health check
- `GET /waterfall` - Get waterfall data
- `GET /task/{task_id}/metadata` - Task metadata

### 2. MongoDB

#### **Staging:**
- **Host:** `10.10.10.108`
- **Port:** `27017`
- **Database:** `prisma`
- **Username:** `prisma`
- **Password:** `prisma`
- **Connection String:** `mongodb://prisma:prisma@10.10.10.108:27017/?authSource=prisma`

#### **Production:**
- **Host:** `10.10.100.108`
- **Port:** `27017`
- **Database:** `prisma`
- **Username:** `prisma`
- **Password:** `prisma`
- **Connection String:** `mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma`

#### **Usage:**
- Storing job metadata
- Storing recordings
- Storing configurations

### 3. RabbitMQ

#### **Staging:**
- **Host:** `10.10.100.107`
- **AMQP Port:** `5672`
- **Management Port:** `15672`
- **Username:** `prisma`
- **Password:** `prismapanda`
- **VHost:** `/`
- **Exchange:** `prisma`

#### **Production:**
- **Host:** `10.10.100.107`
- **AMQP Port:** `5672`
- **Management Port:** `15672`
- **Username:** `prisma`
- **Password:** `prismapanda`
- **VHost:** `/`
- **Exchange:** `prisma`

#### **Usage:**
- Message queue between Focus Server and Baby Analyzer
- Event streaming
- Job orchestration

### 4. Kubernetes Cluster

#### **Staging Cluster:**
- **API Server:** `https://10.10.100.102:6443`
- **Dashboard:** `https://10.10.100.102/`
- **Context:** `panda-cluster`
- **Namespace:** `panda`

#### **Production Cluster:**
- **API Server:** `https://10.10.100.102:6443`
- **Dashboard:** `https://10.10.100.102/`
- **Context:** `panda-cluster`
- **Namespace:** `panda`

#### **SSH Access:**
**Staging:**
- Jump Host: `10.10.10.10` (root@10.10.10.10)
- Target Host: `10.10.10.150` (prisma@10.10.10.150)

**Production:**
- Jump Host: `10.10.100.3` (root@10.10.100.3)
- Target Host: `10.10.100.113` (prisma@10.10.100.113)

#### **Services:**
- `panda-panda-focus-server` - Focus Server backend (ClusterIP)
- `mongodb` - MongoDB database (LoadBalancer)
- `rabbitmq-panda` - RabbitMQ message queue (LoadBalancer)
- `grpc-service-*` - gRPC processing services (NodePort)

#### **Tools:**
- **kubectl** - Kubernetes CLI
- **k9s** - Terminal UI for Kubernetes

### 5. PZ Development Repository

#### **Location:**
- **Path:** `external/pz/`
- **Type:** Git Submodule
- **Usage:** Access to PZ microservices and development tools

#### **Content:**
- `microservices/` - Microservices
- `bin/` - Development tools
- `CI-CD/` - CI/CD files
- `dotnet/` - .NET code
- `focus-ui/` - Frontend code

### 6. GitHub Actions (CI/CD)

#### **Workflows:**
- **ci.yml** - Basic CI pipeline
- **xray_full_integration.yml** - Full Xray integration
- **xray_upload.yml** - Upload results to Xray
- **focus-contract-tests.yml** - Contract tests
- **readme-check.yml** - README check

#### **Triggers:**
- Push to `main`/`develop`
- Pull Requests
- Scheduled (nightly)
- Manual trigger

### 7. Xray Test Management

#### **API:**
- **URL:** `https://xray.cloud.getxray.app/api/v2`
- **Authentication:** Client ID + Secret
- **Project Key:** `PZ`

#### **Usage:**
- Mapping tests to Test Cases
- Uploading test results
- Creating Test Executions
- Attaching Evidence

---

## 📋 Configuration Files

### 1. `config/environments.yaml`

**Content:**
- Environment settings (staging, production, local)
- Focus Server endpoints
- MongoDB connection strings
- RabbitMQ connection details
- Kubernetes cluster access
- SSH tunnel configuration
- System constraints (frequency, channels, windows)
- NFFT configuration
- Display defaults

### 2. `config/settings.yaml`

**Content:**
- General test settings
- Timeouts
- Retry policies
- Logging configuration

### 3. `pytest.ini`

**Content:**
- Test discovery patterns
- Markers (50+ markers)
- Logging configuration
- Coverage settings
- Test paths

### 4. `requirements.txt`

**Content:**
- All Python dependencies
- Minimum versions
- Categories: Testing, HTTP, Infrastructure, Data Processing, etc.

---

## 🔄 Workflows

### 1. Test Execution Process

```
1. Session Setup (conftest.py)
   ├── Load configuration (ConfigManager)
   ├── Initialize infrastructure managers
   ├── Connect to Kubernetes (if needed)
   ├── Connect to MongoDB (if needed)
   ├── Connect to RabbitMQ (if needed)
   └── Start pod monitoring (if --monitor-pods)

2. Test Setup (conftest.py fixtures)
   ├── Create API client (FocusServerAPI)
   ├── Initialize test data
   ├── Pre-test health checks (if enabled)
   └── Start test-specific monitoring

3. Test Execution
   ├── Use API client for API calls
   ├── Use infrastructure managers for infrastructure ops
   ├── Verify responses
   └── Assert results

4. Test Teardown
   ├── Collect pod logs (if enabled)
   ├── Cleanup test data
   ├── Close connections
   └── Save evidence (if failed)

5. Session Teardown
   ├── Stop pod monitoring
   ├── Close infrastructure connections
   └── Generate reports
```

### 2. Pod Monitoring Process

```
1. Enable monitoring (--monitor-pods flag)
   ├── Connect to SSH (worker node)
   ├── Start monitoring threads
   └── Monitor multiple services

2. During Test Execution
   ├── Associate logs with current test
   ├── Detect errors in logs
   └── Save test-specific logs

3. After Test
   ├── Save test logs to file
   ├── Generate error summary
   └── Attach to Xray (if enabled)
```

### 3. Xray Integration Process

```
1. Test Mapping
   ├── Mark test with @pytest.mark.xray(test_key="PZ-XXXXX")
   └── Link to Test Plan (PZ-14024)

2. Test Execution
   ├── Run tests
   └── Generate JUnit XML report

3. Upload Results
   ├── Authenticate with Xray
   ├── Upload JUnit XML
   ├── Create Test Execution
   └── Attach evidence (logs, screenshots)

4. PR Integration
   ├── Comment PR with results
   └── Link to Test Execution
```

---

## 📊 Project Statistics

### Test Files:
- **Unit Tests:** 4 files
- **Integration Tests:** 20+ files
  - API Tests: 16+ files
  - Performance Tests: 8+ files
  - Security Tests: 7+ files
  - Load Tests: 6+ files
- **Infrastructure Tests:** 7+ files
- **Data Quality Tests:** 5+ files
- **E2E Tests:** 1+ files
- **Total:** 42+ test files

### Test Functions:
- **~230+ test functions** (basic coverage)
- **101/113 tests** mapped to Xray (89.4% mapping)

### Source Code:
- **~8,000+ lines** of test code
- **API Clients:** 3 files
- **Infrastructure Managers:** 7 files
- **Models:** 2 files
- **Utils:** 6+ files

### Scripts:
- **200+ utility scripts**
- **Xray scripts:** 2+ files
- **Jira scripts:** 5+ files
- **API scripts:** Additional files

### Documentation:
- **314+ documentation files**
- **Organized structure:** 8 main categories

---

## 🔧 External Dependencies

### 1. Kubernetes Cluster
- **Requirement:** Access to Kubernetes cluster
- **Access:** Direct API or SSH tunnel
- **Tools:** kubectl, k9s

### 2. MongoDB
- **Requirement:** Accessible MongoDB instance
- **Access:** Direct connection

### 3. RabbitMQ
- **Requirement:** Accessible RabbitMQ instance
- **Access:** AMQP connection

### 4. SSH Access
- **Requirement:** SSH access to worker nodes
- **Usage:** kubectl commands, port forwarding

### 5. Xray Cloud
- **Requirement:** Xray Cloud account
- **Credentials:** Client ID + Secret
- **Usage:** Test management, reporting

### 6. Jira
- **Requirement:** Jira instance
- **Usage:** Bug tracking, ticket management

---

## 🌐 Network Connections

### External Connections:
- **Focus Server:** `https://10.10.10.100/focus-server/` (staging)
- **Focus Server:** `https://10.10.100.100/focus-server/` (production)
- **MongoDB:** `10.10.10.108:27017` (staging) / `10.10.100.108:27017` (production)
- **RabbitMQ:** `10.10.100.107:5672`
- **Kubernetes API:** `https://10.10.100.102:6443`
- **Xray API:** `https://xray.cloud.getxray.app/api/v2`
- **Jira API:** `https://prismaphotonics.atlassian.net`

### SSH Connections:
- **Staging:** `10.10.10.10` → `10.10.10.150`
- **Production:** `10.10.100.3` → `10.10.100.113`

---

## 📝 Important Notes

### 1. Infrastructure Managers Architecture:
Each Infrastructure Manager supports:
- Direct API access (if available)
- SSH fallback (if Direct API unavailable)
- Error handling and retry logic

### 2. Real-time Pod Monitoring:
The project supports real-time log monitoring from pods during test execution, with:
- Association of logs to specific tests
- Automatic error detection
- Log file saving

### 3. Configuration Management:
Centralized configuration system with:
- Singleton pattern
- Environment-specific configurations
- Validation and error handling

### 4. Xray Integration:
Full Xray integration includes:
- Automatic test mapping
- Result upload
- Test Execution creation
- Evidence attachment

### 5. PZ Repository Integration:
Integration with PZ Development Repository via Git Submodule, with access to microservices and development tools.

---

**Last Updated:** 2025-11-09  
**Created by:** QA Automation Team
