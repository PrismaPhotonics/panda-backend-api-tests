# Projects, Workflows, Tools & Infrastructure Overview
## For Ronen - Complete Guide

**Created:** 2025-11-09  
**Purpose:** Clear overview of FE automation project, BE automation project, tools, infrastructure, and development processes

---

## 📋 Table of Contents

1. [FE Automation Project - Frontend Testing](#fe-automation-project---frontend-testing)
2. [BE Automation Project - Backend Testing](#be-automation-project---backend-testing)
3. [Infrastructure & Tools](#infrastructure--tools)
4. [Development Workflows](#development-workflows)
5. [CI/CD Processes](#cicd-processes)

---

## 🎨 FE Automation Project - Frontend Testing

### Project Overview

**Project Name:** Panda Test Automation (FE Automation)  
**Repository:** `panda-test-automation` (cloned to `ron_project/`)  
**Type:** Frontend E2E Testing  
**Technology:** Playwright, Python, Appium (Windows Desktop App)  
**Maintained by:** Ron

### What It Does

Automates testing of the **Panda Desktop Application** (Windows GUI):
- **Alerts** - Create, edit, delete, filter alerts
- **Login** - Authentication flows
- **Map** - Map view interactions
- **Investigations** - Investigation workflows
- **Filters** - Alert filtering functionality
- **Analysis Templates** - Pre-defined analysis templates
- **Frequency Filter** - Frequency filtering validation
- **Smoke Tests** - Critical path validation
- **Regression Tests** - Full regression suite

### Project Structure

```
ron_project/
├── blocksAndRepo/          # Page Object Model (POM)
│   └── panda/
│       ├── alerts/         # Alert page objects
│       ├── login/           # Login page objects
│       ├── map/             # Map page objects
│       └── investigator/    # Investigation page objects
├── tests/
│   └── panda/
│       ├── sanity/         # Sanity test suites
│       ├── smoke/          # Smoke tests
│       └── regression/     # Regression tests
├── common/                 # Common utilities
│   ├── appium/            # Appium server/client
│   └── Logging.py         # Logging utilities
└── config/                # Test configuration
```

### Current Status

**Implemented Features:**
- ✅ Alerts Tests (3 sanity tests + page objects)
- ✅ Login Tests (1 sanity test + page objects)
- ✅ Map Tests (1 sanity test + page objects)
- ✅ Investigations Tests (1 sanity test + page objects)
- ✅ Filters Tests (1 sanity test)
- ✅ Analysis Templates Tests (1 sanity test)
- ✅ Frequency Filter Tests (1 sanity test)
- ✅ Analyze Alert Tests (1 sanity test)
- ✅ Smoke Tests (1 test file)
- ✅ Regression Tests (1 test file)

**Jira Integration:**
- 100+ relevant Jira tickets identified
- 8 tickets updated to reflect implementation status

### Tools Used

- **Playwright** - UI automation framework
- **Appium** - Windows desktop app automation
- **Python** - Test scripting language
- **pytest** - Test execution framework

---

## ⚙️ BE Automation Project - Backend Testing

### Project Overview

**Project Name:** Focus Server Automation Framework  
**Repository:** `focus_server_automation`  
**Type:** Backend API & Infrastructure Testing  
**Technology:** Python, pytest, REST API, gRPC

### What It Does

Comprehensive test automation for the **Focus Server Backend** system:
- **API Testing** - REST API endpoint validation
- **Infrastructure Testing** - Kubernetes, MongoDB, RabbitMQ
- **Performance Testing** - Load and stress testing
- **Integration Testing** - End-to-end workflows
- **Real-time Pod Monitoring** - Kubernetes pod log monitoring during tests

### Project Structure

```
focus_server_automation/
├── src/
│   ├── apis/              # API clients
│   │   ├── focus_server_api.py
│   │   └── baby_analyzer_mq_client.py
│   ├── infrastructure/    # Infrastructure managers
│   │   ├── kubernetes_manager.py
│   │   ├── mongodb_manager.py
│   │   ├── rabbitmq_manager.py
│   │   └── ssh_manager.py
│   ├── models/           # Data models (Pydantic)
│   └── utils/            # Utilities
│       └── realtime_pod_monitor.py
├── tests/
│   ├── integration/      # Integration tests
│   │   ├── api/          # API tests
│   │   └── performance/  # Performance tests
│   ├── infrastructure/   # Infrastructure tests
│   └── unit/             # Unit tests
├── config/
│   └── environments.yaml # Environment configuration
└── scripts/              # Utility scripts
    └── xray_upload.py    # Xray integration
```

### Current Status

**Test Coverage:**
- ✅ **42 test files** implemented
- ✅ **230+ test functions** (basic coverage)
- ✅ **101/113 tests** mapped to Xray (89.4% mapping)
- ✅ **~8,000+ lines** of test code

**Test Categories:**
- ✅ Unit Tests: 4 files, 60+ tests
- ✅ Integration Tests: 20+ files, 100+ tests
- ✅ Performance Tests: 3+ files, 6+ tests
- ✅ Security Tests: 1 file
- ✅ Infrastructure Tests: 7 files
- ✅ Data Quality Tests: 5 files

**Framework Components:**
- ✅ API Client Library (REST API client)
- ✅ Infrastructure Managers (K8s, MongoDB, RabbitMQ, SSH)
- ✅ Real-time Pod Monitoring
- ✅ Configuration Management System
- ✅ Jira/Xray Integration

### Tools Used

- **Python 3.12** - Programming language
- **pytest** - Test framework
- **requests** - HTTP client
- **pydantic** - Data validation
- **kubernetes** - K8s Python client
- **pymongo** - MongoDB client
- **pika** - RabbitMQ client

---

## 🏗️ Infrastructure & Tools

### Production Environment

**Focus Server Backend:**
- **URL:** `https://10.10.100.100/focus-server/`
- **Frontend:** `https://10.10.100.100/liveView`
- **Site ID:** `prisma-210-1000`

**Infrastructure Components:**

| Component | IP:Port | Purpose | Access Method |
|-----------|---------|---------|---------------|
| **Focus Server** | `10.10.100.100:443` | Backend API | HTTPS |
| **MongoDB** | `10.10.100.108:27017` | Database | Direct connection |
| **RabbitMQ** | `10.10.100.107:5672` | Message Queue | AMQP |
| **RabbitMQ Management** | `10.10.100.107:15672` | Management UI | HTTP |
| **Kubernetes API** | `10.10.100.102:6443` | K8s Cluster | HTTPS |

### Kubernetes Cluster

**Cluster Details:**
- **Namespace:** `panda`
- **Context:** `panda-cluster`
- **Access:** SSH tunnel via jump host

**SSH Access:**
```
Jump Host: 10.10.100.3 (root@10.10.100.3)
Target Host: 10.10.100.113 (prisma@10.10.100.113)
```

**Services Running:**
- `panda-panda-focus-server` - Focus Server backend
- `mongodb` - MongoDB database
- `rabbitmq-panda` - RabbitMQ message queue
- `grpc-service-*` - gRPC processing services

### System Constraints

**Configuration Limits:**
- **Max Frequency:** 1000 Hz
- **Max Channels:** 2222 (SensorsRange)
- **Max Concurrent Jobs:** 30 (MaxWindows)
- **Default Channels:** 11-109 (99 channels)
- **Default NFFT:** 1024

**NFFT Options:** 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536

### Configuration Management

**Environment Configuration:**
- **File:** `config/environments.yaml`
- **Environments:** `staging`, `production`, `local`
- **Default:** `staging` (November 2025)

**Key Configuration Sections:**
- Focus Server endpoints
- MongoDB connection strings
- RabbitMQ connection details
- Kubernetes cluster access
- SSH tunnel configuration
- System constraints and defaults

---

## 🔄 Development Workflows

### Code Development Process

**1. Feature Development:**
```
Developer creates feature branch
    ↓
Implements feature/tests
    ↓
Creates Pull Request
    ↓
Code Review
    ↓
Tests pass (CI/CD)
    ↓
Merge to main
```

**2. Test Development:**
```
Identify test requirement
    ↓
Create test file in appropriate directory
    ↓
Implement test with Xray marker
    ↓
Run tests locally
    ↓
Create PR with test
    ↓
Review and merge
```

### Pull Request Process

**PR Requirements:**
- ✅ Clear title: `[Type] - [Short description]`
- ✅ Description includes:
  - What was changed
  - Why it was changed
  - How to test
  - Link to Jira ticket
- ✅ All tests pass
- ✅ Code review approval
- ✅ Jira ticket linked

**Review Checklist:**
- [ ] Code works (Tests pass)
- [ ] Sufficient Test Coverage
- [ ] Documentation exists
- [ ] Error Handling exists
- [ ] Logging exists
- [ ] Clean Code principles
- [ ] Follows Best Practices
- [ ] No Hardcoded Values
- [ ] Configuration is correct
- [ ] Jira ticket linked

### Jira Ticket Management

**Ticket Types:**
- **Story** - Feature or test group
- **Task** - Technical task
- **Bug** - Found bug
- **Sub-task** - Small task part of larger Story

**Recommended Labels:**
- **Component:** `backend`, `frontend`, `infrastructure`
- **Type:** `automation`, `manual`, `bug`, `feature`
- **Technology:** `kubernetes`, `regression`, `api`, `ui`

**For Automation:**
- **Label:** `automation` - Tests that are automated
- **Label:** `for-automation` - Tests that need to be automated (Tomer's label)

**Story Points:** Fibonacci sequence (1, 2, 3, 5, 8, 13)

---

## 🚀 CI/CD Processes

### GitHub Actions Workflows

**1. Xray Full Integration** (`.github/workflows/xray_full_integration.yml`)

**Purpose:** Automated test execution with Xray integration

**Triggers:**
- Push to `main`/`develop`
- Pull Requests
- Scheduled (nightly at 2 AM)
- Manual trigger

**Process:**
```
1. Authenticate with Xray
    ↓
2. Fetch tests from Test Plan (PZ-14024)
    ↓
3. Run tests (filtered by Test Plan)
    ↓
4. Generate test reports (JUnit XML, HTML)
    ↓
5. Upload results to Xray
    ↓
6. Create Test Execution
    ↓
7. Attach evidence (logs, screenshots)
    ↓
8. Comment PR with results
```

**Configuration:**
- **Test Plan:** PZ-14024 (default, configurable)
- **Environment:** Staging/Production (auto-detected)
- **Secrets Required:**
  - `XRAY_CLIENT_ID`
  - `XRAY_CLIENT_SECRET`

**2. CI - Focus API and Load Sanity** (`.github/workflows/ci.yml`)

**Purpose:** Basic CI pipeline for API tests

**Triggers:**
- Push to any branch
- Pull Requests
- Scheduled (daily at 2 AM UTC)

**Process:**
```
1. Checkout code
    ↓
2. Setup Python 3.12
    ↓
3. Install dependencies
    ↓
4. Preflight check (Focus Server availability)
    ↓
5. Run API tests
```

### Test Execution

**Local Execution:**
```bash
# Run all tests
pytest tests/ -v

# Run with pod monitoring
pytest tests/ --monitor-pods -v

# Run specific category
pytest tests/integration/api/ -v
pytest tests/infrastructure/ -v

# Run by marker
pytest -m integration
pytest -m api
```

**CI/CD Execution:**
- Automatic on PR creation
- Automatic on push to main
- Scheduled nightly runs
- Manual trigger via GitHub Actions UI

### Xray Integration

**Test Mapping:**
- Tests marked with `@pytest.mark.xray(test_key="PZ-XXXXX")`
- 101/113 tests mapped (89.4% coverage)
- Test Execution created automatically
- Results uploaded after each run

**Test Plan:**
- Default: PZ-14024
- Tests linked to Test Plan
- Environment tracked (Staging/Production)
- Revision tracked (Git SHA)

**Evidence Attachment:**
- Test logs
- Screenshots
- HTML reports
- Error logs

---

## 📊 Project Statistics

### BE Automation Project

| Metric | Value |
|--------|-------|
| **Test Files** | 42 |
| **Test Functions** | 230+ |
| **Xray Mapping** | 101/113 (89.4%) |
| **Lines of Code** | ~8,000+ |
| **Documentation Files** | 314+ |

### FE Automation Project

| Metric | Value |
|--------|-------|
| **Test Suites** | 8 (sanity) + 2 (smoke/regression) |
| **Page Objects** | 6 modules |
| **Jira Tickets** | 100+ identified |

---

## 🔧 Key Tools Summary

### Development Tools

| Tool | Purpose | Used By |
|------|---------|---------|
| **Python 3.12** | Programming language | Both projects |
| **pytest** | Test framework | Both projects |
| **Playwright** | UI automation | FE Automation project |
| **Appium** | Desktop app automation | FE Automation project |
| **requests** | HTTP client | BE Automation project |
| **pydantic** | Data validation | BE Automation project |

### Infrastructure Tools

| Tool | Purpose | Access |
|------|---------|--------|
| **Kubernetes** | Container orchestration | SSH tunnel |
| **MongoDB** | Database | Direct connection |
| **RabbitMQ** | Message queue | AMQP connection |
| **kubectl/k9s** | K8s management | SSH to worker node |

### CI/CD Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **GitHub Actions** | CI/CD pipeline | `.github/workflows/` |
| **Xray** | Test management | Jira integration |
| **Jira** | Issue tracking | Project: PZ |

---

## 📝 Key Processes Summary

### 1. Test Development Process

**BE Automation:**
1. Identify API endpoint/feature to test
2. Create test file in `tests/integration/api/`
3. Implement test with Xray marker
4. Add to Test Plan (PZ-14024)
5. Run locally, then create PR

**FE Automation:**
1. Identify UI feature to test
2. Create page objects in `blocksAndRepo/panda/`
3. Create test in `tests/panda/sanity/`
4. Run locally, then create PR

### 2. Bug Reporting Process

**Bug Review Meeting:**
- **Frequency:** Once per sprint (before sprint ends)
- **Scope:** All FE and BE bugs
- **Purpose:** Review, prioritize, assign

**Bug Workflow:**
```
Bug found → Create Jira ticket → Assign → Fix → Test → Close
```

### 3. Sprint Planning

**Capacity Planning:**
- **Roy** - Sit with Ron about sprint capacity
- **Roy** - Sit with Tomer about sprint plans
- **Tomer** - Add labels for automation (`automation`, `for-automation`)

**Test Planning:**
- **Tomer** - Define tests to automate
- **Tomer** - Label tests with `for-automation`
- **Ron** - Automate tests labeled `for-automation`

### 4. Load & Stress Testing

**Current Status:**
- ✅ Automated tests exist for load/stress
- ⚠️ Need to coordinate with team
- ⚠️ Need to understand Tomer's test plans

**Action Items:**
- Discuss with team about existing automated tests
- Understand what tests Tomer plans to run
- Coordinate load/stress test execution

---

## 🎯 Action Items & Next Steps

### Immediate Actions

1. **Alarm Grouping Automation**
   - Need test plan for Tomer
   - Define most important tests to automate
   - Set up automation framework

2. **Load & Stress Testing**
   - Coordinate with team
   - Understand existing automated tests
   - Understand Tomer's test plans

3. **Sprint Capacity**
   - Roy sit with Ron about sprint capacity
   - Roy sit with Tomer about sprint plans

4. **Bug Review**
   - Schedule bug review meeting (once per sprint)
   - Review all FE and BE bugs

5. **Test Labels**
   - Tomer add `automation` label to automated tests
   - Tomer add `for-automation` label to tests needing automation

### Documentation Needs

- ✅ This document (Projects & Workflows overview)
- ⚠️ FE-BE-GitHub Actions workflow document (Ronen requested)
- ⚠️ Detailed infrastructure setup guide
- ⚠️ Test execution guide

---

## 📚 Additional Resources

### Documentation Locations

**Main Documentation:**
- `docs/` - Organized documentation structure
- `docs/06_project_management/` - Project management docs
- `docs/07_infrastructure/` - Infrastructure docs

**Key Documents:**
- `README.md` - Project overview
- `docs/06_project_management/jira/XRAY_INTEGRATION_SUMMARY.md` - Xray integration
- `docs/07_infrastructure/COMPLETE_INFRASTRUCTURE_SUMMARY.md` - Infrastructure details

### External Links

- **Jira:** https://prismaphotonics.atlassian.net
- **GitHub:** Repository-specific URLs
- **Xray:** Integrated with Jira

---

**Last Updated:** 2025-11-09  
**Maintained by:** QA Automation Team

