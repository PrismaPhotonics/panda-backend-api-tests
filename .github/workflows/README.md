# GitHub Actions Workflows

## Overview

This directory contains GitHub Actions workflows for automated testing and CI/CD.

## 🆕 New Workflows (Recommended)

### `backend-tests-lab.yml` - Focus Server Backend Tests (Lab Runner) 🏭

**Purpose:** Run tests on self-hosted Windows runner in the lab (with access to K8s, MongoDB, RabbitMQ)

**Runner:** `[self-hosted, Windows, panda-backend-lab]`

**Triggers:**
- Push to `main`, `develop`, `master`, `chore/add-roy-tests`
- Pull Requests to `main`
- Manual trigger (`workflow_dispatch`) with test suite selection
- Scheduled: Daily at 23:00 UTC (01:00 Israel time)

**Test Suites:**
- `smoke` - Smoke and high-priority tests
- `regression` - Regression tests (excluding slow/nightly)
- `nightly` - Full suite including slow/load/stress with pod monitoring
- `all` - All tests

**Timeout:** 120 minutes  
**Max Failures:** 5-50 (depending on suite)

**Setup Required:**
- Self-hosted Windows runner installed on lab machine
- Runner labels: `self-hosted`, `Windows`, `panda-backend-lab`
- GitHub Secrets: `FOCUS_BASE_URL`, `FOCUS_API_PREFIX`, `VERIFY_SSL`

**See:** [Setup Guide](../docs/07_infrastructure/github_actions_setup_guide.md)

---

### `backend-tests-github.yml` - Focus Server Backend Tests (GitHub Runner) ☁️

**Purpose:** Run tests on GitHub-hosted runner (for tests that don't need VPN/K8s access)

**Runner:** `ubuntu-latest`

**Triggers:**
- Push to `main`, `develop`, `master`, `chore/add-roy-tests`
- Pull Requests to `main`
- Manual trigger (`workflow_dispatch`) with test suite selection

**Test Suites:**
- `smoke` - Smoke and high-priority tests
- `regression` - Regression tests (excluding slow/nightly)

**Timeout:** 30 minutes  
**Max Failures:** 5-10 (depending on suite)

**Setup Required:**
- GitHub Secrets: `FOCUS_BASE_URL`, `FOCUS_API_PREFIX`, `VERIFY_SSL`

---

## Legacy Workflows

### `smoke-tests.yml` - Smoke Tests ⚡

Fast, critical tests that run on every commit/PR.

**Triggers:**
- Push to `main`, `develop`, or `master` branches
- Pull Requests to `main`, `develop`, or `master` branches
- Manual trigger via GitHub Actions UI (`workflow_dispatch`)

**What Tests Are Run:**
- Tests marked with `@pytest.mark.smoke`
- Fast tests (< 5 minutes)
- Critical functionality tests

**Timeout:** 10 minutes  
**Max Failures:** 5

---

### `regression-tests.yml` - Regression Tests 🔄

Full integration tests that run before merge to main.

**Triggers:**
- Push to `main` branch only
- Manual trigger via GitHub Actions UI (`workflow_dispatch`)

**What Tests Are Run:**
- Tests marked with `@pytest.mark.regression`
- Excludes slow and nightly tests
- Full integration test suite

**Timeout:** 60 minutes  
**Max Failures:** 10

---

### `nightly-tests.yml` - Nightly Full Suite 🌙

Complete test suite including slow/load/stress tests.

**Triggers:**
- Scheduled: Daily at 2:00 AM UTC
- Manual trigger via GitHub Actions UI (`workflow_dispatch`)

**What Tests Are Run:**
- Tests marked with `@pytest.mark.smoke`
- Tests marked with `@pytest.mark.regression`
- Tests marked with `@pytest.mark.nightly`
- Includes slow, load, and stress tests

**Timeout:** 120 minutes (2 hours)  
**Max Failures:** 20

---

### `backend-tests.yml` - Backend Tests (Legacy)

**Note:** This workflow is kept for backward compatibility. Consider using the new test suite workflows (`smoke-tests.yml`, `regression-tests.yml`, `nightly-tests.yml`) instead.

This workflow runs all tests except those that create load on the system.

#### Triggers

- **Push** to `main`, `develop`, or `master` branches
- **Pull Requests** to `main`, `develop`, or `master` branches
- **Manual trigger** via GitHub Actions UI (`workflow_dispatch`)

#### What Tests Are Run

✅ **Included Test Categories:**
- **Unit tests** (`be_focus_server_tests/unit/`)
- **Integration tests** (non-load) - will skip if infrastructure not available
- **Data quality tests** - will skip if MongoDB/Focus Server not available
- **Infrastructure tests** - will skip if SSH/K8s/RabbitMQ not available
- **API tests** - will skip if Focus Server not available

**Note:** The workflow attempts to run all tests except load/stress tests. Tests requiring external infrastructure (Focus Server API, MongoDB, RabbitMQ, Kubernetes, SSH) will automatically skip if the services are not available in the CI environment. This allows the workflow to run successfully even without access to internal services, while still running tests that can execute.

**Focus Server Connection:** If `FOCUS_BASE_URL` secret is configured and the server is reachable, tests requiring Focus Server will run. Otherwise, they will be skipped gracefully.

❌ **Excluded Test Categories:**
- Load tests (`be_focus_server_tests/load/`)
- Stress tests (`be_focus_server_tests/stress/`)
- Infrastructure tests (`be_focus_server_tests/infrastructure/` - require SSH/K8s/RabbitMQ access)
- Integration load tests (`be_focus_server_tests/integration/load/`)
- Alert load tests (`test_alert_generation_load.py`)
- Alert performance tests (`test_alert_generation_performance.py`)
- gRPC stream tests (marked with `@pytest.mark.grpc`)
- API load tests (`focus_server_api_load_tests/`)
- Tests requiring infrastructure (MongoDB, RabbitMQ, Kubernetes, SSH)

#### Test Execution Strategy

The workflow uses multiple exclusion methods to ensure load tests are not run:

1. **Directory exclusion**: `--ignore` flags for load/stress directories
2. **File pattern exclusion**: `--ignore-glob` for specific load test files
3. **Marker exclusion**: `-m "not load and not stress and not grpc"` to exclude tests marked with these markers

#### Outputs

- **Test Reports**: JUnit XML and HTML reports are generated and uploaded as artifacts
- **Test Summary**: A summary is displayed in the GitHub Actions UI showing which test categories were included/excluded

#### Artifacts

The following artifacts are available after workflow completion:

- `backend-test-reports`: Contains JUnit XML and HTML reports for backend tests
- `frontend-test-reports`: Contains JUnit XML and HTML reports for frontend tests

Artifacts are retained for 30 days.

#### Timeouts

- Backend tests: 60 minutes
- Frontend tests: 30 minutes

#### Failure Handling

- Tests will stop after 10 failures (`--maxfail=10`) to prevent excessive CI time
- Reports are uploaded even if tests fail (`if: always()`)

## Running Tests Locally (Without Load)

To run the same set of tests locally that the CI runs:

```bash
# Run only unit tests (same as CI)
pytest be_focus_server_tests/unit/ -m "unit" -v

# Or run all tests excluding load/stress/infrastructure (requires local infrastructure access)
pytest be_focus_server_tests/ \
  --ignore=be_focus_server_tests/load \
  --ignore=be_focus_server_tests/stress \
  --ignore=be_focus_server_tests/infrastructure \
  --ignore-glob=**/integration/load \
  --ignore-glob=**/test_alert_generation_load.py \
  --ignore-glob=**/test_alert_generation_performance.py \
  -m "not load and not stress and not grpc and not infrastructure and not mongodb and not rabbitmq and not kubernetes and not ssh" \
  -v
```

Or use the simpler marker-based approach:

```bash
pytest -m "not load and not stress and not grpc" -v
```

## Notes

- Load tests should be run manually or in a separate workflow on dedicated infrastructure
- The workflow uses Python 3.10
- All dependencies are installed from `requirements.txt`
- Frontend tests use dependencies from `fe_panda_tests/requirements.txt`

