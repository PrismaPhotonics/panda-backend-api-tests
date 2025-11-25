# Running Tests (CI-Compatible)

## Command to Run All Tests (Excluding Load/Stress)

```bash
pytest be_focus_server_tests/ \
  --env=local \
  --skip-health-check \
  --skip-sanity-check \
  --ignore=be_focus_server_tests/load \
  --ignore=be_focus_server_tests/stress \
  --ignore-glob=**/integration/load \
  --ignore-glob=**/test_alert_generation_load.py \
  --ignore-glob=**/test_alert_generation_performance.py \
  -m "not load and not stress and not grpc" \
  -v \
  --tb=short \
  --junitxml=reports/junit-backend.xml \
  --html=reports/backend-report.html \
  --self-contained-html \
  --maxfail=10 \
  --continue-on-collection-errors
```

## Environment Variables (Optional)

If you want to test with Focus Server connection:

```bash
export CI=true
export FOCUS_BASE_URL="https://10.10.10.100"
export FOCUS_API_PREFIX="/focus-server"
export VERIFY_SSL="false"
export FOCUS_SERVER_AVAILABLE="true"  # Set to "false" to skip Focus Server tests
```

## For Windows PowerShell

```powershell
$env:CI="true"
$env:FOCUS_BASE_URL="https://10.10.10.100"
$env:FOCUS_API_PREFIX="/focus-server"
$env:VERIFY_SSL="false"
$env:FOCUS_SERVER_AVAILABLE="false"  # Skip Focus Server tests in CI

pytest be_focus_server_tests/ `
  --env=local `
  --skip-health-check `
  --skip-sanity-check `
  --ignore=be_focus_server_tests/load `
  --ignore=be_focus_server_tests/stress `
  --ignore-glob=**/integration/load `
  --ignore-glob=**/test_alert_generation_load.py `
  --ignore-glob=**/test_alert_generation_performance.py `
  -m "not load and not stress and not grpc" `
  -v `
  --tb=short `
  --junitxml=reports/junit-backend.xml `
  --html=reports/backend-report.html `
  --self-contained-html `
  --maxfail=10 `
  --continue-on-collection-errors
```

## Quick Test Run (Minimal Output)

```bash
pytest be_focus_server_tests/ \
  --env=local \
  --skip-health-check \
  --skip-sanity-check \
  --ignore=be_focus_server_tests/load \
  --ignore=be_focus_server_tests/stress \
  -m "not load and not stress and not grpc" \
  -q
```

## Notes

- `--env=local` - Uses local environment config (skips auto infrastructure setup)
- `--skip-health-check` - Skips pre-test health checks
- `--skip-sanity-check` - Skips sanity checks
- `-m "not load and not stress and not grpc"` - Excludes load, stress, and gRPC tests
- `--continue-on-collection-errors` - Continues even if some tests fail to collect
- Tests requiring infrastructure (MongoDB, RabbitMQ, Kubernetes, SSH) will be skipped automatically in CI environment

