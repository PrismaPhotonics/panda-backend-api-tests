# How to Run Historic Playback Tests

## Quick Commands

### Run all Historic Playback tests:
```bash
pytest be_focus_server_tests/integration/api/test_historic_playback_e2e.py -v
```

### Run with staging environment:
```bash
$env:FOCUS_ENV = "staging"; pytest be_focus_server_tests/integration/api/test_historic_playback_e2e.py -v
```

### Run specific test:
```bash
pytest be_focus_server_tests/integration/api/test_historic_playback_e2e.py::TestHistoricPlaybackCompleteE2E::test_historic_playback_complete_e2e_flow -v
```

### Run with markers:
```bash
# Run only critical tests
pytest be_focus_server_tests/integration/api/test_historic_playback_e2e.py -m critical -v

# Run only regression tests
pytest be_focus_server_tests/integration/api/test_historic_playback_e2e.py -m regression -v

# Run only Xray tests
pytest be_focus_server_tests/integration/api/test_historic_playback_e2e.py -m xray -v
```

### Run with additional tests:
```bash
# Include additional historic playback tests
pytest be_focus_server_tests/integration/api/test_historic_playback_e2e.py be_focus_server_tests/integration/api/test_historic_playback_additional.py -v
```

### Run with detailed output:
```bash
pytest be_focus_server_tests/integration/api/test_historic_playback_e2e.py -v -s --tb=short
```

### Run with logging:
```bash
pytest be_focus_server_tests/integration/api/test_historic_playback_e2e.py -v --log-cli-level=INFO
```

## Test Markers

- `@pytest.mark.critical` - Critical tests
- `@pytest.mark.high` - High priority tests
- `@pytest.mark.regression` - Regression tests
- `@pytest.mark.xray("PZ-13872")` - Xray test mapping
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.nightly` - Nightly tests

## Expected Behavior

**If Focus Server is fixed:**
- ✅ Tests should pass
- ✅ Historic jobs should be created successfully
- ✅ Recordings should be found and played back

**If Focus Server still has the issue:**
- ❌ Tests will skip with message: "No recording found in Focus Server for time range"
- ❌ API will return 404: "No recording found in given time range"

## Troubleshooting

### If tests skip due to "No recording found":
1. Check MongoDB has recordings:
   ```bash
   py scripts/check_all_base_paths.py
   ```

2. Check Focus Server can access MongoDB:
   ```bash
   py scripts/test_focus_api_direct.py
   ```

3. See issue documentation:
   - `docs/07_infrastructure/FOCUS_SERVER_RECORDINGS_NOT_FOUND_ISSUE.md`

