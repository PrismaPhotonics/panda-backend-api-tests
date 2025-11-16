# GitHub Actions Workflows

## Overview

This directory contains GitHub Actions workflows for automated testing and CI/CD.

## Workflows

### `tests.yml` - Run Tests (Excluding Load Tests)

This workflow runs all tests except those that create load on the system.

#### Triggers

- **Push** to `main`, `develop`, or `master` branches
- **Pull Requests** to `main`, `develop`, or `master` branches
- **Manual trigger** via GitHub Actions UI (`workflow_dispatch`)

#### What Tests Are Run

✅ **Included Test Categories:**
- Unit tests (`be_focus_server_tests/unit/`)
- Integration tests (non-load) (`be_focus_server_tests/integration/`)
- Infrastructure tests (`be_focus_server_tests/infrastructure/`)
- Data quality tests (`be_focus_server_tests/data_quality/`)
- Security tests (`be_focus_server_tests/security/`)
- Performance tests (non-load) (`be_focus_server_tests/performance/`)
- UI tests (`be_focus_server_tests/ui/`)
- Frontend tests (`fe_panda_tests/tests/`)

❌ **Excluded Test Categories:**
- Load tests (`be_focus_server_tests/load/`)
- Stress tests (`be_focus_server_tests/stress/`)
- Integration load tests (`be_focus_server_tests/integration/load/`)
- Alert load tests (`test_alert_generation_load.py`)
- Alert performance tests (`test_alert_generation_performance.py`)
- gRPC stream tests (marked with `@pytest.mark.grpc`)
- API load tests (`focus_server_api_load_tests/`)

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
pytest be_focus_server_tests/ \
  --ignore=be_focus_server_tests/load \
  --ignore=be_focus_server_tests/stress \
  --ignore=be_focus_server_tests/integration/load \
  --ignore-glob=**/test_alert_generation_load.py \
  --ignore-glob=**/test_alert_generation_performance.py \
  -m "not load and not stress and not grpc" \
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

