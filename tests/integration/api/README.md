# API Integration Tests

Integration tests for Focus Server API endpoints.

## Test Files

- `test_dynamic_roi_adjustment.py` - ROI adjustment tests (15 tests)
- `test_historic_playback_flow.py` - Historic playback tests (10 tests)
- `test_live_monitoring_flow.py` - Live monitoring tests (15 tests)
- `test_spectrogram_pipeline.py` - Spectrogram configuration tests (13 tests)
- `test_singlechannel_view_mapping.py` - Single channel view tests (13 tests)

## Total: 66 API Integration Tests

## Run Tests

```powershell
# Run all API integration tests
pytest tests/integration/api/ -v

# Run specific test file
pytest tests/integration/api/test_dynamic_roi_adjustment.py -v
```

