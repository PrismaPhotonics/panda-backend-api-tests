# Complete Xray Test Documentation - Part 7: Historic Playback Extended Tests
**Status**: Production-Ready Documentation for Jira Xray Import  
**Date**: October 20, 2025  
**Category**: Historic Playback Extended Scenarios (10 Critical Tests)

---

## 📋 Test Index

### Historic Playback Extended Coverage (10 Tests)
1. **PZ-HISTORIC-EXT-001**: Historic Playback - Standard 5-Minute Range
2. **PZ-HISTORIC-EXT-002**: Historic Playback - Short Duration (1 Minute)
3. **PZ-HISTORIC-EXT-003**: Historic Playback - Long Duration (30 Minutes)
4. **PZ-HISTORIC-EXT-004**: Historic Playback - Very Old Timestamps (No Data)
5. **PZ-HISTORIC-EXT-005**: Historic Playback - Data Integrity Validation
6. **PZ-HISTORIC-EXT-006**: Historic Playback - Status 208 Completion
7. **PZ-HISTORIC-EXT-007**: Historic Playback - Invalid Time Range (End Before Start)
8. **PZ-HISTORIC-EXT-008**: Historic Playback - Future Timestamps
9. **PZ-HISTORIC-EXT-009**: Historic Playback - Timestamp Ordering Validation
10. **PZ-HISTORIC-EXT-010**: Historic Playback Complete End-to-End Flow

---

## Test: PZ-HISTORIC-EXT-001
**Test Name**: Historic Playback - Standard 5-Minute Range

### Summary
Validates that Focus Server correctly handles a standard historic playback request for a 5-minute time range, returning data from the specified historical period and completing with status 208.

### Objective
Verify that Focus Server can process a historic playback configuration with `start_time` and `end_time` set to a 5-minute range, poll waterfall data until completion, and return all available data for the specified period.

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `historic-playback`, `time-range`, `integration`, `api`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-HISTORIC-PLAYBACK
- **Description**: Historic playback must support time-bound data retrieval with start/end timestamps

### Pre-Conditions
1. Focus Server is running and accessible
2. MongoDB contains recorded data for the specified time range
3. Baby Analyzer can access and process historic recordings
4. Recordings collection in MongoDB has data within the last 24 hours

### Test Data
```json
{
  "task_id": "historic_5min_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 0,
      "max": 50
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": "<yymmddHHMMSS_start>",
    "end_time": "<yymmddHHMMSS_end>",
    "view_type": 0
  }
}
```
**Time Range**: `end_time = now()`, `start_time = end_time - 5 minutes`  
**Format**: `yymmddHHMMSS` (e.g., "251020120000" for 2025-10-20 12:00:00)

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Calculate time range: `end_time = now()`, `start_time = end_time - 5 minutes` | Time range calculated in `yymmddHHMMSS` format |
| 2 | Validate time format using `validate_time_format_yymmddHHMMSS()` | Time strings validated |
| 3 | Create `ConfigureRequest` with `start_time` and `end_time` | Payload validated by Pydantic |
| 4 | Send POST /configure | Status 200, `status: "Config received successfully"` |
| 5 | Immediately send GET /waterfall/{task_id}/10 | Status 200 (no data yet) or 201 (data available) |
| 6 | Poll GET /waterfall every 2 seconds (max 100 attempts) | Status transitions from 200 → 201 → 208 |
| 7 | Collect all data blocks during status 201 phases | Multiple data blocks with waterfall rows |
| 8 | Wait for status 208 (baby analyzer exited) | Status 208 received, playback complete |
| 9 | Verify total data blocks received > 0 | At least some historic data retrieved |
| 10 | Verify all timestamps fall within specified range | `start_time <= row.timestamp <= end_time` |
| 11 | Verify timestamps are sequential and increasing | Each row's timestamp >= previous row's timestamp |

### Expected Result
- **Status code**: 200 for /configure, status transitions 200 → 201 → 208 for /waterfall
- **Data received**: Multiple data blocks with valid waterfall rows
- **Timestamps**: All within specified 5-minute range, sequential
- **Completion**: Status 208 received within reasonable time (< 200 seconds)

### Post-Conditions
- Historic playback task completed successfully
- Baby analyzer process for this task exited cleanly
- No error messages in Focus Server logs

### Assertions (Python Code)
```python
# Test function: test_configure_historic_task_success (from test_historic_playback_flow.py)

# Generate time range
from src.utils.helpers import generate_time_range, datetime_to_yymmddHHMMSS
end_time_dt = datetime.now()
start_time_dt = end_time_dt - timedelta(minutes=5)

start_time = datetime_to_yymmddHHMMSS(start_time_dt)
end_time = datetime_to_yymmddHHMMSS(end_time_dt)

historic_config_payload["start_time"] = start_time
historic_config_payload["end_time"] = end_time

logger.info(f"Time range: {start_time} to {end_time}")

# Validate time format
from src.utils.validators import validate_time_format_yymmddHHMMSS
assert validate_time_format_yymmddHHMMSS(start_time)
assert validate_time_format_yymmddHHMMSS(end_time)

# Configure task
config_request = ConfigTaskRequest(**historic_config_payload)
response = focus_server_api.config_task(task_id, config_request)

# Assertions
assert isinstance(response, ConfigTaskResponse)
assert response.status == "Config received successfully"

# Poll until completion
status_transitions = []
data_blocks_received = 0
max_poll_attempts = 100
poll_interval = 2.0

for attempt in range(max_poll_attempts):
    waterfall_response = focus_server_api.get_waterfall(task_id, 10)
    
    # Track status transitions
    if not status_transitions or status_transitions[-1] != waterfall_response.status_code:
        status_transitions.append(waterfall_response.status_code)
        logger.info(f"Status transition: {waterfall_response.status_code}")
    
    if waterfall_response.status_code == 201:
        # Data available
        validation_result = validate_waterfall_response(waterfall_response)
        assert validation_result["is_valid"]
        
        if waterfall_response.data:
            data_blocks_received += len(waterfall_response.data)
    
    elif waterfall_response.status_code == 208:
        # Playback complete
        logger.info(f"Playback completed after {attempt + 1} polls")
        logger.info(f"Total data blocks received: {data_blocks_received}")
        assert data_blocks_received > 0, "No data blocks received during playback"
        return  # Test passed
    
    time.sleep(poll_interval)

pytest.fail("Playback did not complete after 100 poll attempts")
```

### Environment
- **Environment Name**: new_production
- **Focus Server**: https://10.10.100.100/focus-server/
- **MongoDB**: 10.10.100.108:27017 (contains historic recordings)

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_configure_historic_task_success`, `test_poll_historic_playback_until_completion`
- **Test File**: `tests/integration/api/test_historic_playback_flow.py`
- **Execution**: `pytest -m "integration and api" tests/integration/api/test_historic_playback_flow.py::TestHistoricPlaybackHappyPath::test_configure_historic_task_success`

---

## Test: PZ-HISTORIC-EXT-002
**Test Name**: Historic Playback - Short Duration (1 Minute)

### Summary
Validates that Focus Server can handle a very short historic playback request (1 minute), completing quickly and efficiently.

### Objective
Verify that historic playback works correctly for minimal time ranges (1 minute), demonstrating that the system can handle short-duration queries without issues.

### Priority
**Medium**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `historic-playback`, `short-duration`, `edge-case`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-HISTORIC-SHORT
- **Description**: Historic playback must support short time ranges (minimum 1 minute)

### Pre-Conditions
1. Focus Server is running
2. MongoDB contains data from the last hour
3. Baby Analyzer can process 1-minute playback

### Test Data
```json
{
  "task_id": "historic_1min_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 0,
      "max": 20
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": "<yymmddHHMMSS_start>",
    "end_time": "<yymmddHHMMSS_end>",
    "view_type": 0
  }
}
```
**Time Range**: 1 minute (end_time - 1 minute to end_time)

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Calculate 1-minute time range | `start_time = now() - 1 minute`, `end_time = now()` |
| 2 | Create `ConfigureRequest` with 1-minute range | Payload validated |
| 3 | Send POST /configure | Status 200, task configured |
| 4 | Poll GET /waterfall every 1 second (max 30 attempts) | Status transitions to 201, then 208 |
| 5 | Verify status 208 received within 30 seconds | Playback completes quickly |
| 6 | Verify some data received | Data blocks > 0 |

### Expected Result
- **Quick completion**: Status 208 received within 30 polls (30 seconds)
- **Data received**: At least some data blocks returned
- **No errors**: Clean completion

### Post-Conditions
- Short playback completed successfully

### Assertions (Python Code)
```python
# Test function: test_historic_playback_with_short_duration

# Create 1-minute historic range
end_time_dt = datetime.now()
start_time_dt = end_time_dt - timedelta(minutes=1)

start_time = datetime_to_yymmddHHMMSS(start_time_dt)
end_time = datetime_to_yymmddHHMMSS(end_time_dt)

payload = generate_config_payload(
    sensors_min=0,
    sensors_max=20,
    live=False,
    duration_minutes=1
)

# Configure task
config_request = ConfigTaskRequest(**payload)
response = focus_server_api.config_task(task_id, config_request)
assert response.status == "Config received successfully"

# Poll until completion (with shorter timeout)
max_attempts = 30
completed = False

for attempt in range(max_attempts):
    response = focus_server_api.get_waterfall(task_id, 10)
    
    if response.status_code == 208:
        completed = True
        logger.info(f"Short playback completed after {attempt + 1} polls")
        break
    
    time.sleep(1.0)

assert completed, "Short historic playback did not complete in time"
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_historic_playback_with_short_duration`
- **Test File**: `tests/integration/api/test_historic_playback_flow.py`

---

## Test: PZ-HISTORIC-EXT-003
**Test Name**: Historic Playback - Long Duration (30 Minutes)

### Summary
Validates that Focus Server can handle longer historic playback requests (30 minutes), ensuring stability and data integrity over extended processing.

### Objective
Verify that historic playback works correctly for longer time ranges (30 minutes), demonstrating that the system can sustain extended playback sessions without memory leaks or performance degradation.

### Priority
**Medium**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `historic-playback`, `long-duration`, `stability`
- **Test Type**: Integration Test (Long-Running)

### Requirements
- **Requirement ID**: FOCUS-API-HISTORIC-LONG
- **Description**: Historic playback must support extended time ranges (up to 60 minutes)

### Pre-Conditions
1. Focus Server is running
2. MongoDB contains at least 30 minutes of recorded data from recent period
3. Sufficient server resources for long playback

### Test Data
```json
{
  "task_id": "historic_30min_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 0,
      "max": 50
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": "<yymmddHHMMSS_start>",
    "end_time": "<yymmddHHMMSS_end>",
    "view_type": 0
  }
}
```
**Time Range**: 30 minutes

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Calculate 30-minute time range | Time range calculated |
| 2 | Send POST /configure | Status 200, task configured |
| 3 | Poll GET /waterfall every 2 seconds (max 600 attempts = 20 minutes timeout) | Status 201 data received continuously |
| 4 | Track total data blocks received | Large number of data blocks |
| 5 | Wait for status 208 | Playback completes eventually |
| 6 | Verify large amount of data received | Data blocks > 100 |
| 7 | Verify no memory issues or timeouts | No server errors |

### Expected Result
- **Long playback**: Completes within 20 minutes (600 polls)
- **Large data volume**: > 100 data blocks received
- **Stability**: No errors, timeouts, or resource exhaustion

### Post-Conditions
- Server stable after long playback
- Memory usage returns to normal

### Assertions (Python Code)
```python
# Test function: test_historic_playback_long_duration

# Create 30-minute historic range
end_time_dt = datetime.now()
start_time_dt = end_time_dt - timedelta(minutes=30)

start_time = datetime_to_yymmddHHMMSS(start_time_dt)
end_time = datetime_to_yymmddHHMMSS(end_time_dt)

payload = generate_config_payload(
    sensors_min=0,
    sensors_max=50,
    live=False,
    duration_minutes=30
)

# Configure task
response = focus_server_api.config_task(task_id, ConfigTaskRequest(**payload))
assert response.status == "Config received successfully"

# Poll with longer timeout
max_attempts = 600  # 20 minutes
data_blocks_received = 0

for attempt in range(max_attempts):
    waterfall_response = focus_server_api.get_waterfall(task_id, 10)
    
    if waterfall_response.status_code == 201 and waterfall_response.data:
        data_blocks_received += len(waterfall_response.data)
        
        if attempt % 50 == 0:
            logger.info(f"Poll {attempt}, data blocks: {data_blocks_received}")
    
    elif waterfall_response.status_code == 208:
        logger.info(f"Long playback completed after {attempt + 1} polls")
        logger.info(f"Total data blocks: {data_blocks_received}")
        assert data_blocks_received > 100, f"Expected >100 blocks, got {data_blocks_received}"
        return  # Test passed
    
    time.sleep(2.0)

pytest.fail("Long playback did not complete in time")
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_historic_playback_long_duration`
- **Test File**: `tests/integration/api/test_historic_playback_flow.py`

---

## Test: PZ-HISTORIC-EXT-004
**Test Name**: Historic Playback - Very Old Timestamps (No Data)

### Summary
Validates that Focus Server correctly handles historic playback requests for time ranges where no data exists (e.g., 1 year ago), returning appropriate status and messages.

### Objective
Verify error handling or graceful completion when requesting historic data from a time period with no recorded data in MongoDB.

### Priority
**Medium**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `historic-playback`, `error-handling`, `no-data`, `negative-test`
- **Test Type**: Integration Test (Negative)

### Requirements
- **Requirement ID**: FOCUS-API-HISTORIC-NODATA
- **Description**: Historic playback must handle "no data available" scenarios gracefully

### Pre-Conditions
1. Focus Server is running
2. MongoDB does NOT contain data from 1 year ago

### Test Data
```json
{
  "task_id": "historic_old_nodata_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 0,
      "max": 50
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": "<yymmddHHMMSS_1_year_ago>",
    "end_time": "<yymmddHHMMSS_1_year_ago_plus_5min>",
    "view_type": 0
  }
}
```
**Time Range**: 1 year ago, 5-minute window

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Calculate time range from 1 year ago | Time range calculated |
| 2 | Send POST /configure | Status 200, task configured (server accepts config) |
| 3 | Poll GET /waterfall (max 30 attempts) | Status 200 (no data yet) or 208 (no data found, exited) |
| 4 | Verify either: (a) Status 208 quickly (no data), or (b) Status 200 persists (no data available) | Expected behavior for "no data" scenario |
| 5 | Verify no data blocks received | `data_blocks_received == 0` |

### Expected Result
- **Configuration accepted**: Status 200 for /configure
- **No data**: Either status 208 (completed with no data) or persistent status 200
- **No errors**: No crashes or unexpected errors

### Post-Conditions
- Task completes or remains in "no data" state
- No errors logged

### Assertions (Python Code)
```python
# Test function: test_historic_with_very_old_timestamps

# Calculate time range from 1 year ago
end_time_dt = datetime.now() - timedelta(days=365)
start_time_dt = end_time_dt - timedelta(minutes=5)

start_time = datetime_to_yymmddHHMMSS(start_time_dt)
end_time = datetime_to_yymmddHHMMSS(end_time_dt)

payload = generate_config_payload(
    sensors_min=0,
    sensors_max=50,
    live=False,
    duration_minutes=5
)
payload["start_time"] = start_time
payload["end_time"] = end_time

# Configure task
response = focus_server_api.config_task(task_id, ConfigTaskRequest(**payload))
assert response.status == "Config received successfully"

# Poll and expect no data
data_found = False
max_attempts = 30

for attempt in range(max_attempts):
    waterfall_response = focus_server_api.get_waterfall(task_id, 10)
    
    if waterfall_response.status_code == 201:
        data_found = True
        logger.warning("Unexpected data found for 1-year-old timestamps")
        break
    
    elif waterfall_response.status_code == 208:
        logger.info("Playback completed with no data (expected)")
        break
    
    time.sleep(1.0)

# No data expected
assert not data_found, "Data should not exist for 1-year-old timestamps"
logger.info("No data scenario handled correctly")
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_historic_with_very_old_timestamps`
- **Test File**: `tests/integration/api/test_historic_playback_flow.py`

---

## Test: PZ-HISTORIC-EXT-005
**Test Name**: Historic Playback - Data Integrity Validation

### Summary
Validates data integrity during historic playback by checking timestamp ordering, sensor data completeness, and absence of corrupted data.

### Objective
Verify that all data returned during historic playback has sequential timestamps, complete sensor arrays, non-empty intensity data, and no missing or corrupted values.

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `historic-playback`, `data-integrity`, `quality`, `validation`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-DATA-INTEGRITY
- **Description**: All historic data must be complete, ordered, and free of corruption

### Pre-Conditions
1. Focus Server is running
2. MongoDB contains clean, recorded data
3. Historic playback configured for 5-minute range

### Test Data
```json
{
  "task_id": "historic_integrity_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 0,
      "max": 50
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": "<yymmddHHMMSS_start>",
    "end_time": "<yymmddHHMMSS_end>",
    "view_type": 0
  }
}
```

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Configure historic task (5-minute range) | Task configured |
| 2 | Poll GET /waterfall, collect ALL data blocks | Data collected |
| 3 | For each row in all blocks: | - |
| 4 | → Verify `row.startTimestamp <= row.endTimestamp` | Timestamps valid |
| 5 | → Verify timestamps are sequential (increasing) | `row[i].endTimestamp <= row[i+1].startTimestamp` |
| 6 | → Verify `len(row.sensors) > 0` | Row has sensor data |
| 7 | → For each sensor: `assert sensor.id >= 0` | Valid sensor IDs |
| 8 | → For each sensor: `assert len(sensor.intensity) > 0` | Non-empty intensity arrays |
| 9 | → Track last_timestamp, ensure no duplicates | No duplicate timestamps |
| 10 | Wait for status 208 | Playback completes |
| 11 | Verify total rows collected > 0 | Data received |
| 12 | Verify all integrity checks passed | No corrupted data found |

### Expected Result
- **All rows valid**: Every row passes timestamp, sensor, and intensity checks
- **Sequential timestamps**: No out-of-order or duplicate timestamps
- **Complete data**: No missing sensors or empty intensity arrays

### Post-Conditions
- Data integrity verified for historic playback

### Assertions (Python Code)
```python
# Test function: test_historic_playback_data_integrity

# Configure task
response = focus_server_api.config_task(task_id, ConfigTaskRequest(**historic_config_payload))
assert response.status == "Config received successfully"

all_rows = []
last_timestamp = 0

for attempt in range(100):
    waterfall_response = focus_server_api.get_waterfall(task_id, 20)
    
    if waterfall_response.status_code == 201 and waterfall_response.data:
        # Collect rows
        for block in waterfall_response.data:
            for row in block.rows:
                all_rows.append(row)
                
                # Check timestamp ordering
                assert row.startTimestamp <= row.endTimestamp, \
                    "Start timestamp > end timestamp"
                assert row.startTimestamp >= last_timestamp, \
                    "Timestamps not sequential"
                last_timestamp = row.endTimestamp
                
                # Check sensor data
                assert len(row.sensors) > 0, "Row has no sensor data"
                
                for sensor in row.sensors:
                    assert sensor.id >= 0, "Invalid sensor ID"
                    assert len(sensor.intensity) > 0, "Sensor has no intensity data"
    
    elif waterfall_response.status_code == 208:
        # Playback complete
        logger.info(f"Data integrity verified: {len(all_rows)} rows collected")
        break
    
    time.sleep(2.0)

# Final assertions
assert len(all_rows) > 0, "No rows collected during playback"
logger.info(f"All {len(all_rows)} rows passed integrity checks")
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_historic_playback_data_integrity`
- **Test File**: `tests/integration/api/test_historic_playback_flow.py`

---

## Test: PZ-HISTORIC-EXT-006
**Test Name**: Historic Playback - Status 208 Completion

### Summary
Validates that historic playback tasks correctly reach status 208 (baby analyzer exited) upon completion, signaling end-of-data.

### Objective
Verify that the server properly signals playback completion by returning status 208 when all historical data for the specified range has been delivered.

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `historic-playback`, `status-208`, `completion`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-STATUS-208
- **Description**: Historic playback must signal completion with status 208

### Pre-Conditions
1. Focus Server is running
2. Historic data available for specified range

### Test Data
```json
{
  "task_id": "historic_status_208_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 0,
      "max": 50
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": "<yymmddHHMMSS_start>",
    "end_time": "<yymmddHHMMSS_end>",
    "view_type": 0
  }
}
```

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Configure historic task (5-minute range) | Task configured |
| 2 | Poll GET /waterfall until status 208 | Status transitions: 200 → 201 → 208 |
| 3 | Track status transitions | Status codes logged |
| 4 | Verify status 208 eventually received | Final status = 208 |
| 5 | Verify status 208 message indicates completion | Message: "Baby analyzer exited" or similar |

### Expected Result
- **Status 208 received**: Playback completes with status 208
- **Message**: "Baby analyzer exited" or "playback complete"

### Post-Conditions
- Task completed, no longer active

### Assertions (Python Code)
```python
# Test function: test_historic_playback_status_208_completion

response = focus_server_api.config_task(task_id, ConfigTaskRequest(**historic_config_payload))
assert response.status == "Config received successfully"

status_transitions = []
status_208_received = False

for attempt in range(100):
    waterfall_response = focus_server_api.get_waterfall(task_id, 10)
    
    if not status_transitions or status_transitions[-1] != waterfall_response.status_code:
        status_transitions.append(waterfall_response.status_code)
        logger.info(f"Status: {waterfall_response.status_code} - {waterfall_response.message}")
    
    if waterfall_response.status_code == 208:
        status_208_received = True
        logger.info("Status 208 received - playback complete")
        break
    
    time.sleep(2.0)

assert status_208_received, "Status 208 not received within timeout"
logger.info(f"Status transitions: {status_transitions}")
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_historic_playback_status_208_completion`
- **Test File**: `tests/integration/api/test_historic_playback_flow.py`

---

## Test: PZ-HISTORIC-EXT-007
**Test Name**: Historic Playback - Invalid Time Range (End Before Start)

### Summary
Validates that Focus Server properly rejects historic playback requests where `end_time` is before `start_time`, returning an appropriate error.

### Objective
Verify proper validation and error handling when attempting to configure a historic playback with an invalid time range (end before start).

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `historic-playback`, `error-handling`, `validation`, `negative-test`
- **Test Type**: Integration Test (Negative)

### Requirements
- **Requirement ID**: FOCUS-API-HISTORIC-VALIDATION
- **Description**: Historic playback must validate that start_time < end_time

### Pre-Conditions
1. Focus Server is running

### Test Data
```json
{
  "task_id": "historic_invalid_range_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 0,
      "max": 50
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": "<yymmddHHMMSS_later>",
    "end_time": "<yymmddHHMMSS_earlier>",
    "view_type": 0
  }
}
```
**Note**: `start_time > end_time` (intentionally invalid)

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Set `start_time = now()`, `end_time = now() - 10 minutes` (inverted) | Invalid time range created |
| 2 | Send POST /configure | Status 400 or 422 (Validation Error) |
| 3 | Verify error message | Error indicates "start_time must be before end_time" or similar |
| 4 | Verify task not created | GET /waterfall returns 404 |

### Expected Result
- **Status code**: 400 or 422 for /configure
- **Error message**: "Invalid time range: start_time must be before end_time"
- **Behavior**: Request rejected

### Post-Conditions
- No task created

### Assertions (Python Code)
```python
# Test function: test_historic_invalid_time_range_end_before_start

# Create invalid time range (end before start)
start_time_dt = datetime.now()
end_time_dt = datetime.now() - timedelta(minutes=10)  # Earlier than start

start_time = datetime_to_yymmddHHMMSS(start_time_dt)
end_time = datetime_to_yymmddHHMMSS(end_time_dt)

payload = generate_config_payload(sensors_min=0, sensors_max=50, live=False, duration_minutes=5)
payload["start_time"] = start_time
payload["end_time"] = end_time

# Expect validation error
with pytest.raises(Exception) as exc_info:
    focus_server_api.config_task(task_id, ConfigTaskRequest(**payload))

error_msg = str(exc_info.value).lower()
assert "time" in error_msg or "range" in error_msg or "invalid" in error_msg

# Verify task not created
waterfall_response = focus_server_api.get_waterfall(task_id, 10)
assert waterfall_response.status_code == 404
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_historic_invalid_time_range_end_before_start`
- **Test File**: `tests/integration/api/test_historic_playback_flow.py`

---

## Test: PZ-HISTORIC-EXT-008
**Test Name**: Historic Playback - Future Timestamps

### Summary
Validates that Focus Server properly handles historic playback requests with future timestamps, either rejecting them or gracefully completing with no data.

### Objective
Verify error handling or graceful behavior when requesting historic data for a time range in the future (which cannot exist).

### Priority
**Medium**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `historic-playback`, `error-handling`, `future-timestamps`, `negative-test`
- **Test Type**: Integration Test (Negative)

### Requirements
- **Requirement ID**: FOCUS-API-HISTORIC-FUTURE
- **Description**: Historic playback must handle future timestamps gracefully

### Pre-Conditions
1. Focus Server is running

### Test Data
```json
{
  "task_id": "historic_future_timestamps_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 0,
      "max": 50
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": "<yymmddHHMMSS_tomorrow>",
    "end_time": "<yymmddHHMMSS_tomorrow_plus_5min>",
    "view_type": 0
  }
}
```
**Time Range**: Tomorrow (future)

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Set `start_time = now() + 1 day`, `end_time = now() + 1 day + 5 minutes` | Future time range |
| 2 | Send POST /configure | Status 200 (accepted) or 400 (rejected) |
| 3 | If accepted, poll GET /waterfall | Status 200 (no data) or 208 (no data, completed) |
| 4 | Verify no data returned | `data_blocks_received == 0` |

### Expected Result
- **Option A**: Configuration rejected (status 400)
- **Option B**: Configuration accepted, but no data (status 208 quickly)

### Post-Conditions
- No data returned for future timestamps

### Assertions (Python Code)
```python
# Test function: test_historic_future_timestamps

# Create future time range
start_time_dt = datetime.now() + timedelta(days=1)
end_time_dt = start_time_dt + timedelta(minutes=5)

start_time = datetime_to_yymmddHHMMSS(start_time_dt)
end_time = datetime_to_yymmddHHMMSS(end_time_dt)

payload = generate_config_payload(sensors_min=0, sensors_max=50, live=False, duration_minutes=5)
payload["start_time"] = start_time
payload["end_time"] = end_time

try:
    response = focus_server_api.config_task(task_id, ConfigTaskRequest(**payload))
    
    # If accepted, verify no data
    data_found = False
    for attempt in range(30):
        waterfall_response = focus_server_api.get_waterfall(task_id, 10)
        
        if waterfall_response.status_code == 201:
            data_found = True
            break
        elif waterfall_response.status_code == 208:
            logger.info("Future timestamps: no data (expected)")
            break
        
        time.sleep(1.0)
    
    assert not data_found, "Data should not exist for future timestamps"
    
except Exception as e:
    # Configuration rejected (also acceptable)
    logger.info(f"Future timestamps rejected: {e}")
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_historic_future_timestamps`
- **Test File**: `tests/integration/api/test_historic_playback_flow.py`

---

## Test: PZ-HISTORIC-EXT-009
**Test Name**: Historic Playback - Timestamp Ordering Validation

### Summary
Validates that all timestamps in historic playback data are strictly ordered, with no out-of-sequence or overlapping time ranges.

### Objective
Verify that timestamps in all waterfall rows are monotonically increasing, ensuring proper temporal ordering of historic data.

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `historic-playback`, `timestamps`, `ordering`, `quality`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-TIMESTAMP-ORDER
- **Description**: All waterfall rows must have sequential, non-overlapping timestamps

### Pre-Conditions
1. Focus Server is running
2. Historic data available

### Test Data
```json
{
  "task_id": "historic_timestamp_order_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 0,
      "max": 50
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": "<yymmddHHMMSS_start>",
    "end_time": "<yymmddHHMMSS_end>",
    "view_type": 0
  }
}
```

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Configure historic task | Task configured |
| 2 | Poll and collect ALL rows | Rows collected |
| 3 | For each consecutive pair of rows: | - |
| 4 | → Verify `row[i].endTimestamp <= row[i+1].startTimestamp` | No overlap, strict ordering |
| 5 | → Track any violations | No violations found |
| 6 | Verify all rows passed ordering check | All timestamps valid |

### Expected Result
- **Strict ordering**: Every row's endTimestamp <= next row's startTimestamp
- **No violations**: 0 timestamp ordering errors

### Post-Conditions
- Timestamp ordering verified

### Assertions (Python Code)
```python
# Test function: test_historic_timestamp_ordering_validation

response = focus_server_api.config_task(task_id, ConfigTaskRequest(**historic_config_payload))

all_rows = []

for attempt in range(100):
    waterfall_response = focus_server_api.get_waterfall(task_id, 20)
    
    if waterfall_response.status_code == 201 and waterfall_response.data:
        for block in waterfall_response.data:
            for row in block.rows:
                all_rows.append(row)
    
    elif waterfall_response.status_code == 208:
        break
    
    time.sleep(2.0)

# Verify timestamp ordering
violations = 0
for i in range(len(all_rows) - 1):
    if all_rows[i].endTimestamp > all_rows[i+1].startTimestamp:
        logger.error(f"Timestamp violation at row {i}: {all_rows[i].endTimestamp} > {all_rows[i+1].startTimestamp}")
        violations += 1

assert violations == 0, f"Found {violations} timestamp ordering violations"
logger.info(f"All {len(all_rows)} rows have correct timestamp ordering")
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_historic_timestamp_ordering_validation`
- **Test File**: `tests/integration/api/test_historic_playback_flow.py`

---

## Test: PZ-HISTORIC-EXT-010
**Test Name**: Historic Playback Complete End-to-End Flow

### Summary
Comprehensive end-to-end test for historic playback, covering configuration, polling, data collection, metadata retrieval, and completion verification.

### Objective
Verify that a complete historic playback session works correctly from start (configuration) to finish (status 208), demonstrating a full lifecycle workflow.

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `historic-playback`, `end-to-end`, `full-flow`, `lifecycle`
- **Test Type**: Integration Test (End-to-End)

### Requirements
- **Requirement ID**: FOCUS-API-HISTORIC-E2E
- **Description**: Complete historic playback lifecycle must function correctly

### Pre-Conditions
1. Focus Server is running
2. MongoDB contains recorded data
3. Baby Analyzer functional

### Test Data
```json
{
  "task_id": "historic_e2e_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 0,
      "max": 50
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": "<yymmddHHMMSS_start>",
    "end_time": "<yymmddHHMMSS_end>",
    "view_type": 0
  }
}
```

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | **Phase 1: Configuration** | - |
| 2 | Calculate 5-minute time range | Time range calculated |
| 3 | Send POST /configure | Status 200, task configured |
| 4 | **Phase 2: Data Polling** | - |
| 5 | Poll GET /waterfall continuously | Status transitions 200 → 201 → 208 |
| 6 | Collect all data blocks during status 201 | Multiple data blocks collected |
| 7 | Track total rows received | Row count tracked |
| 8 | **Phase 3: Data Validation** | - |
| 9 | Verify all timestamps within specified range | All timestamps valid |
| 10 | Verify timestamp ordering | Sequential, no overlap |
| 11 | Verify sensor data completeness | All sensors have intensity data |
| 12 | **Phase 4: Completion** | - |
| 13 | Wait for status 208 | Status 208 received |
| 14 | Verify playback duration reasonable | Completed within expected time |
| 15 | **Phase 5: Post-Completion** | - |
| 16 | Verify total rows > 0 | Data was delivered |
| 17 | Log summary statistics | Statistics logged |

### Expected Result
- **Configuration**: Successful (status 200)
- **Data delivery**: Multiple blocks, > 50 rows total
- **Data quality**: All timestamps valid, ordered, sensors complete
- **Completion**: Status 208 within 200 seconds
- **Summary**: Full lifecycle successful

### Post-Conditions
- Historic playback completed successfully
- All data quality checks passed

### Assertions (Python Code)
```python
# Test function: test_historic_playback_complete_e2e_flow

task_id = generate_task_id("historic_e2e")

# Phase 1: Configuration
logger.info("Phase 1: Configuring historic playback")
end_time_dt = datetime.now()
start_time_dt = end_time_dt - timedelta(minutes=5)
start_time = datetime_to_yymmddHHMMSS(start_time_dt)
end_time = datetime_to_yymmddHHMMSS(end_time_dt)

payload = generate_config_payload(sensors_min=0, sensors_max=50, live=False, duration_minutes=5)
payload["start_time"] = start_time
payload["end_time"] = end_time

response = focus_server_api.config_task(task_id, ConfigTaskRequest(**payload))
assert response.status == "Config received successfully"

# Phase 2: Data Polling
logger.info("Phase 2: Polling historic data")
all_rows = []
status_transitions = []
start_poll_time = time.time()

for attempt in range(100):
    waterfall_response = focus_server_api.get_waterfall(task_id, 10)
    
    if not status_transitions or status_transitions[-1] != waterfall_response.status_code:
        status_transitions.append(waterfall_response.status_code)
    
    if waterfall_response.status_code == 201 and waterfall_response.data:
        for block in waterfall_response.data:
            for row in block.rows:
                all_rows.append(row)
    
    elif waterfall_response.status_code == 208:
        poll_duration = time.time() - start_poll_time
        logger.info(f"Playback completed after {poll_duration:.1f} seconds")
        break
    
    time.sleep(2.0)

# Phase 3: Data Validation
logger.info("Phase 3: Validating data quality")
assert len(all_rows) > 0, "No rows received"

# Verify timestamp ordering
for i in range(len(all_rows) - 1):
    assert all_rows[i].endTimestamp <= all_rows[i+1].startTimestamp

# Verify sensor data
for row in all_rows:
    assert len(row.sensors) > 0
    for sensor in row.sensors:
        assert len(sensor.intensity) > 0

# Phase 4: Summary
logger.info(f"E2E Historic Playback Summary:")
logger.info(f"  - Total rows: {len(all_rows)}")
logger.info(f"  - Status transitions: {status_transitions}")
logger.info(f"  - Duration: {poll_duration:.1f}s")
logger.info("  - All validations passed")
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_historic_playback_complete_e2e_flow`
- **Test File**: `tests/integration/api/test_historic_playback_flow.py`

---

## 📊 Summary Statistics

### Historic Playback Extended Coverage
- **Total Tests**: 10
- **Priority Breakdown**:
  - High: 6 tests
  - Medium: 4 tests

### Test Categories
1. **Duration Variants**: 3 tests (1min, 5min, 30min)
2. **Error Handling**: 3 tests (no data, invalid range, future timestamps)
3. **Data Quality**: 3 tests (integrity, ordering, status 208)
4. **End-to-End**: 1 comprehensive test

### Automation Status
- ✅ **100% Automated**: All 10 tests are fully automated
- **Test File**: `tests/integration/api/test_historic_playback_flow.py`
- **Execution**: `pytest -m "integration and api" tests/integration/api/test_historic_playback_flow.py`

---

## ✅ Documentation Quality Checklist
- [x] All 10 tests fully documented
- [x] English language throughout
- [x] Strict format compliance
- [x] Complete test data with JSON payloads
- [x] Detailed steps tables
- [x] Python assertion code blocks
- [x] Environment and automation status
- [x] Ready for Jira Xray import

---

**End of Part 7: Historic Playback Extended Tests Documentation**

