# FE Automation, BE Automation & GitHub Actions - Overview
## For Ronen - Tools, Workflows, Infrastructure & Test Scope

**Created:** 2025-11-09  
**Purpose:** Clear overview of FE automation (Ron), BE automation, tools, infrastructure, workflows, and test scope

---

## 📋 Quick Summary

| Project | Owner | Type | Purpose |
|---------|-------|------|---------|
| **FE Automation** | Ron | Frontend E2E | Automates Panda Desktop App (Windows GUI) |
| **BE Automation** | Roy | Backend API | Automates Focus Server Backend (REST API, Infrastructure) |
| **GitHub Actions** | Both | CI/CD | Automated test execution and reporting |

---

## 🎨 FE Automation Project (Ron)

### What Is Tested

**Panda Desktop Application** (Windows GUI):
- ✅ Alerts (create, edit, delete, filter)
- ✅ Login flows
- ✅ Map interactions
- ✅ Investigations
- ✅ Analysis templates
- ✅ Frequency filters
- ✅ Smoke tests
- ✅ Regression tests

### Tools

| Tool | Purpose |
|------|---------|
| **Appium** | Windows Desktop automation |
| **Selenium** | WebView2 automation |
| **pytest** | Test framework |
| **requests** | HTTP client for API calls |
| **FFmpeg** | Video recording |
| **psutil** | System resource monitoring |

### Infrastructure

**Local:**
- Appium Server (`localhost:4723`)
- WebView2 Debugging (`localhost:9222`)
- Panda Desktop App (`C:\Program Files\Prisma\PandaApp\PandaApp-1.2.44.exe`)

**External:**
- API Backend: `https://10.10.100.100/prisma/api/`
- RabbitMQ: `10.10.10.102` (via API)
- Focus Server: `https://10.10.100.100/focus-server/`

### Workflow

**Development:**
1. Create Page Objects → Building Blocks → Tests
2. Run locally: `pytest tests/`
3. Create PR

**Execution:**
- Auto-starts Appium Server
- Launches Panda App with WebView2 debugging
- Records video (kept if test fails)
- Monitors system resources

### Test Scope

**Current:**
- ~10 test files
- 8 sanity test suites
- 2 smoke/regression suites
- ~10 Page Objects

**Future:**
- Additional UI features as they are developed
- More regression coverage
- Performance testing

---

## ⚙️ BE Automation Project (Roy)

### What Is Tested

**Focus Server Backend:**
- ✅ REST API endpoints (configure, channels, metadata, waterfall, etc.)
- ✅ Infrastructure (Kubernetes pods, MongoDB, RabbitMQ)
- ✅ Performance & load testing
- ✅ Resilience testing (pod failures, outages)
- ✅ Data quality (MongoDB schema, indexes, data consistency)
- ✅ Security (authentication, input validation, HTTPS)
- ✅ Error handling (HTTP errors, network errors, invalid payloads)

### Tools

| Tool | Purpose |
|------|---------|
| **pytest** | Test framework |
| **requests** | REST API calls |
| **kubernetes** | K8s cluster management |
| **pymongo** | MongoDB operations |
| **pika** | RabbitMQ operations |
| **paramiko** | SSH connections |
| **pydantic** | Data validation |
| **jira** | Bug tracking |
| **psutil** | System monitoring |

### Infrastructure

**Focus Server:**
- Staging: `https://10.10.10.100/focus-server/`
- Production: `https://10.10.100.100/focus-server/`

**MongoDB:**
- Staging: `10.10.10.108:27017`
- Production: `10.10.100.108:27017`

**RabbitMQ:**
- Host: `10.10.100.107:5672`
- Management: `10.10.100.107:15672`

**Kubernetes:**
- API: `https://10.10.100.102:6443`
- Namespace: `panda`
- SSH Access: Jump host → Worker node

**External Services:**
- Xray: `https://xray.cloud.getxray.app/api/v2`
- Jira: `https://prismaphotonics.atlassian.net`

### Workflow

**Development:**
1. Create test file in appropriate directory
2. Use `FocusServerAPI` client for API calls
3. Use infrastructure managers for infrastructure ops
4. Add Xray marker: `@pytest.mark.xray(test_key="PZ-XXXXX")`
5. Run locally: `pytest tests/ --monitor-pods`
6. Create PR

**Execution:**
- Loads configuration (`config/environments.yaml`)
- Connects to infrastructure (K8s, MongoDB, RabbitMQ)
- Runs tests with optional pod monitoring
- Uploads results to Xray
- Attaches evidence (logs, screenshots)

### Test Scope

**Current:**
- 42+ test files
- 230+ test functions
- 101/113 tests mapped to Xray (89.4%)
- Categories:
  - ✅ API endpoints (16+ files)
  - ✅ Infrastructure (7+ files)
  - ✅ Performance (8+ files)
  - ✅ Load (6+ files)
  - ✅ Security (7+ files)
  - ✅ Data Quality (5+ files)
  - ✅ Resilience (6+ files)
  - ✅ E2E (1+ files)

**Future (Planned):**
- ⏳ Additional security tests (10 tests planned)
- ⏳ Additional error handling tests (8 tests planned)
- ⏳ Additional performance tests (expanding coverage)
- ⏳ Additional load tests (expanding scenarios)
- ⏳ Additional data quality tests (5 tests planned)
- ⏳ Future API structure tests (15 tests - waiting for deployment)

**Pending Implementation:**
- 37 tests in Jira but not yet automated
- 204 test functions need Xray markers added

---

## 🔄 GitHub Actions (CI/CD)

### Workflows

| Workflow | Purpose | Triggers |
|---------|---------|----------|
| **xray_full_integration.yml** | Full test execution with Xray | Push, PR, Scheduled, Manual |
| **ci.yml** | Basic CI pipeline | Push, PR, Scheduled |
| **xray_upload.yml** | Upload test results | Manual |
| **focus-contract-tests.yml** | Contract validation | Push, PR |
| **readme-check.yml** | Documentation check | Push, PR |

### Main Workflow: Xray Full Integration

**Process:**
```
1. Authenticate with Xray
2. Fetch tests from Test Plan (PZ-14024)
3. Run tests (filtered by Test Plan)
4. Generate reports (JUnit XML, HTML)
5. Upload results to Xray
6. Create Test Execution
7. Attach evidence (logs, screenshots)
8. Comment PR with results
```

**Configuration:**
- Test Plan: PZ-14024 (default)
- Environment: Auto-detected (Staging/Production)
- Secrets: `XRAY_CLIENT_ID`, `XRAY_CLIENT_SECRET`

**Triggers:**
- Push to `main`/`develop`
- Pull Requests
- Scheduled (nightly at 2 AM)
- Manual trigger

---

## 🛠️ Tools Summary

### FE Automation Tools
- Appium, Selenium, pytest, requests, FFmpeg, psutil

### BE Automation Tools
- pytest, requests, kubernetes, pymongo, pika, paramiko, pydantic, jira, psutil

### Common Tools
- pytest, requests, psutil

---

## 🏗️ Infrastructure Summary

### Shared Infrastructure
- Focus Server Backend (Staging/Production)
- RabbitMQ (FE via API, BE directly)

### FE-Specific
- Appium Server (local)
- WebView2 Debugging (local)
- Panda Desktop App (local)

### BE-Specific
- MongoDB (Staging/Production)
- Kubernetes (API + SSH access)
- Xray Cloud
- Jira

---

## 📊 Test Scope Summary

### FE Automation
- **Current:** ~10 test files, 8 sanity suites, 2 smoke/regression suites
- **Future:** Additional UI features, more regression coverage, performance testing

### BE Automation
- **Current:** 42+ test files, 230+ test functions, 89.4% Xray mapping
- **Future:** 
  - 37 tests in Jira to be automated
  - 10 security tests planned
  - 8 error handling tests planned
  - 5 data quality tests planned
  - 15 future API structure tests (waiting for deployment)
  - 204 test functions need Xray markers

---

## 🔄 Development Workflows

### FE Automation
1. Create Page Objects → Building Blocks → Tests
2. Run locally
3. Create PR
4. Code review
5. Merge

### BE Automation
1. Create test file
2. Implement with Xray marker
3. Run locally with pod monitoring
4. Create PR
5. GitHub Actions runs automatically
6. Results uploaded to Xray
7. Code review
8. Merge

### Common PR Process
1. Create PR with description
2. Link Jira ticket
3. Tests run automatically (GitHub Actions)
4. Code review
5. All checks pass
6. Merge to main

---

**Last Updated:** 2025-11-09  
**Created for:** Ronen  
**Maintained by:** QA Automation Team
