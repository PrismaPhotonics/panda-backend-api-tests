# Pre-Launch Validations Tests

**Created:** 27 October 2025  
**Related:** PZ-13756 (Meeting decision - Pre-launch validations in scope)

---

## Purpose

These tests validate Focus Server API pre-launch checks performed BEFORE job creation.

## Tests Included

### Port Validation (1 test)
1. **test_port_availability_before_job_creation()**
   - Validates: Port conflict detection
   - Expected: Reject if port in use

### Data Availability (2 tests)
2. **test_data_availability_live_mode()**
   - Validates: Live data stream available
   
3. **test_data_availability_historic_mode()**
   - Validates: Historic data exists in time range

### Time Range Validation (2 tests)
4. **test_time_range_validation_future_timestamps()**
   - Validates: Reject future timestamps
   
5. **test_time_range_validation_reversed_range()**
   - Validates: Reject end_time < start_time

### Configuration Validation (4 tests)
6. **test_config_validation_channels_out_of_range()**
   - Validates: Channels within system limits
   
7. **test_config_validation_frequency_exceeds_nyquist()**
   - Validates: Frequency <= PRR/2
   
8. **test_config_validation_invalid_nfft()**
   - Validates: NFFT > 0 and power of 2
   
9. **test_config_validation_invalid_view_type()**
   - Validates: View type is supported

### Error Messages (1 test)
10. **test_prelaunch_validation_error_messages_clarity()**
    - Validates: Error messages are clear and actionable

## Running Tests

```bash
# All pre-launch validation tests
pytest tests/integration/api/test_prelaunch_validations.py -v

# Specific category
pytest tests/integration/api/test_prelaunch_validations.py -v -k "data_availability"
pytest tests/integration/api/test_prelaunch_validations.py -v -k "time_range"
pytest tests/integration/api/test_prelaunch_validations.py -v -k "config_validation"

# With markers
pytest -m "prelaunch" -v
pytest -m "prelaunch and critical" -v
```

## Expected Duration

- All 10 tests: ~3-5 minutes
- Individual test: ~10-30 seconds

## Success Criteria

- Invalid requests are rejected with clear errors
- Error messages indicate what failed
- No 500 errors for validation failures
- System remains stable after validation failures

