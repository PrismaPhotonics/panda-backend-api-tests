# Integration Tests

Integration tests for Focus Server system components.

## Test Categories

### API Tests (`tests/integration/api/`)
Integration tests for Focus Server REST API endpoints.

**Test Files:** 5  
**Test Functions:** 66

- Dynamic ROI adjustment
- Historic playback flow
- Live monitoring flow
- Spectrogram pipeline configuration
- Single channel view mapping

## Run Tests

```powershell
# Run all integration tests
pytest tests/integration/ -v

# Run only API tests
pytest tests/integration/api/ -v
```

## Test Structure

```
tests/integration/
└── api/
    ├── test_dynamic_roi_adjustment.py
    ├── test_historic_playback_flow.py
    ├── test_live_monitoring_flow.py
    ├── test_spectrogram_pipeline.py
    └── test_singlechannel_view_mapping.py
```
