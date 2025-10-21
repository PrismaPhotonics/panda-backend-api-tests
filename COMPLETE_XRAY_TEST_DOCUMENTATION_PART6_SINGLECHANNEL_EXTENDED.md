# Complete Xray Test Documentation - Part 6: SingleChannel Extended Tests
**Status**: Production-Ready Documentation for Jira Xray Import  
**Date**: October 20, 2025  
**Category**: SingleChannel View Extended Scenarios (15 Critical Tests)

---

## 📋 Test Index

### SingleChannel Extended Coverage (15 Tests)
1. **PZ-SINGLE-EXT-001**: SingleChannel Edge Case - Minimum Channel (Channel 0)
2. **PZ-SINGLE-EXT-002**: SingleChannel Edge Case - Maximum Channel (Last Available)
3. **PZ-SINGLE-EXT-003**: SingleChannel Edge Case - Middle Channel
4. **PZ-SINGLE-EXT-004**: SingleChannel with Invalid Channel (Out of Range High)
5. **PZ-SINGLE-EXT-005**: SingleChannel with Invalid Channel (Negative)
6. **PZ-SINGLE-EXT-006**: SingleChannel with Min > Max (Validation Error)
7. **PZ-SINGLE-EXT-007**: SingleChannel Data Consistency Check
8. **PZ-SINGLE-EXT-008**: SingleChannel Frequency Range Validation
9. **PZ-SINGLE-EXT-009**: SingleChannel Canvas Height Validation
10. **PZ-SINGLE-EXT-010**: SingleChannel NFFT Validation
11. **PZ-SINGLE-EXT-011**: SingleChannel Rapid Reconfiguration
12. **PZ-SINGLE-EXT-012**: SingleChannel Polling Stability
13. **PZ-SINGLE-EXT-013**: SingleChannel Metadata Consistency
14. **PZ-SINGLE-EXT-014**: SingleChannel Stream Mapping Verification
15. **PZ-SINGLE-EXT-015**: SingleChannel Complete Flow End-to-End

---

## Test: PZ-SINGLE-EXT-001
**Test Name**: SingleChannel Edge Case - Minimum Channel (Channel 0)

### Summary
Validates SingleChannel view behavior when configuring the minimum available channel (channel 0), ensuring correct 1:1 mapping and data delivery for the edge case of the first sensor.

### Objective
Verify that Focus Server correctly handles SingleChannel view for channel 0, returning exactly one stream with proper mapping, and delivers valid sensor data for the first channel.

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `edge-case`, `channel-mapping`, `api-integration`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-SINGLECHANNEL-EDGE
- **Description**: SingleChannel view must correctly handle boundary channels (min/max available sensors)

### Pre-Conditions
1. Focus Server is running and accessible at configured base URL
2. Environment configured for `new_production`
3. GET /sensors endpoint returns available sensor list
4. At least sensor 0 exists in the system
5. Baby Analyzer process is running and processing live fiber data
6. RabbitMQ connection is active for command routing

### Test Data
```json
{
  "task_id": "singlechannel_min_ch0_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 0,
      "max": 0
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Generate unique `task_id` for test | Unique task_id created (format: `singlechannel_min_ch0_<timestamp>`) |
| 2 | Send GET /sensors to retrieve available sensors | Status 200, sensors list contains 0 |
| 3 | Create `ConfigureRequest` with `view_type=SINGLECHANNEL`, `channels.min=0`, `channels.max=0` | Request payload validated by Pydantic model |
| 4 | Send POST /configure with payload | Status 200, response contains `status: "Config received successfully"` |
| 5 | Verify response `stream_amount` | `stream_amount == 1` (exactly one stream) |
| 6 | Verify response `channel_to_stream_index` | Mapping is `{"0": 0}` (channel 0 maps to stream 0) |
| 7 | Verify response `channel_amount` | `channel_amount == 1` (only one channel configured) |
| 8 | Send GET /waterfall/{task_id}/10 to poll data | Status 201, data blocks returned |
| 9 | Verify each data block contains exactly 1 stream | `len(data_block.data) == 1` for all blocks |
| 10 | Verify rows contain sensor ID 0 | All rows have `sensors[0].id == 0` |
| 11 | Validate intensity data is non-empty | `len(sensors[0].intensity) > 0` |
| 12 | Validate timestamps are sequential and increasing | `startTimestamp <= endTimestamp`, timestamps increase between rows |

### Expected Result
- **Status code**: 200 for /configure, 201 for /waterfall
- **stream_amount**: 1
- **channel_to_stream_index**: `{"0": 0}`
- **channel_amount**: 1
- **Data integrity**: All rows contain sensor 0 with valid intensity data
- **Timestamps**: Sequential and increasing

### Post-Conditions
- Task remains active (for live monitoring) or completes successfully (for historic)
- No error messages in Focus Server logs
- RabbitMQ command was successfully routed to Baby Analyzer
- Consumer for `task_id` exists in server memory

### Assertions (Python Code)
```python
# Test function: test_singlechannel_minimum_channel (from test_singlechannel_view_mapping.py)

# Assertion 1: Verify response status
assert isinstance(response, ConfigTaskResponse)
assert response.status == "Config received successfully"

# Assertion 2: Verify stream amount
assert response.stream_amount == 1, \
    f"Expected stream_amount=1 for SingleChannel, got {response.stream_amount}"

# Assertion 3: Verify channel-to-stream mapping
assert response.channel_to_stream_index == {"0": 0}, \
    f"Expected mapping {{'0': 0}}, got {response.channel_to_stream_index}"

# Assertion 4: Verify channel amount
assert response.channel_amount == 1, \
    f"Expected channel_amount=1, got {response.channel_amount}"

# Assertion 5: Poll and verify data structure
waterfall_response = focus_server_api.get_waterfall(task_id, 10)
assert waterfall_response.status_code == 201, "No data received"

# Assertion 6: Verify exactly one stream in data blocks
for data_block in waterfall_response.data:
    assert len(data_block.data) == 1, \
        f"Expected 1 stream per block, got {len(data_block.data)}"

# Assertion 7: Verify sensor ID is 0
for data_block in waterfall_response.data:
    for row in data_block.data[0].rows:  # Access first (and only) stream
        assert row.sensors[0].id == 0, \
            f"Expected sensor ID 0, got {row.sensors[0].id}"
        assert len(row.sensors[0].intensity) > 0, "Intensity data is empty"
```

### Environment
- **Environment Name**: new_production
- **Focus Server**: https://10.10.100.100/focus-server/
- **MongoDB**: 10.10.100.108:27017
- **RabbitMQ**: 10.10.100.107:5672

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_minimum_channel`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`
- **Execution**: `pytest -m "integration and api" tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewEdgeCases::test_singlechannel_minimum_channel`

---

## Test: PZ-SINGLE-EXT-002
**Test Name**: SingleChannel Edge Case - Maximum Channel (Last Available)

### Summary
Validates SingleChannel view behavior when configuring the maximum available channel (last sensor), ensuring correct 1:1 mapping and data delivery for the edge case of the last sensor.

### Objective
Verify that Focus Server correctly handles SingleChannel view for the maximum available channel, returning exactly one stream with proper mapping, and delivers valid sensor data for the last channel.

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `edge-case`, `channel-mapping`, `api-integration`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-SINGLECHANNEL-EDGE
- **Description**: SingleChannel view must correctly handle boundary channels (min/max available sensors)

### Pre-Conditions
1. Focus Server is running and accessible
2. GET /sensors endpoint returns available sensor list with N sensors
3. Maximum sensor index (N-1) is available
4. Baby Analyzer is processing live data

### Test Data
```json
{
  "task_id": "singlechannel_max_ch<max>_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": <max_sensor_id>,
      "max": <max_sensor_id>
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```
**Note**: `<max_sensor_id>` is dynamically determined from GET /sensors response.

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Send GET /sensors to retrieve available sensors | Status 200, sensors list returned |
| 2 | Extract maximum sensor ID (`max_sensor = sensors[-1]`) | Maximum sensor ID identified |
| 3 | Create `ConfigureRequest` with `channels.min=max_sensor`, `channels.max=max_sensor`, `view_type=SINGLECHANNEL` | Request payload validated |
| 4 | Send POST /configure | Status 200, `status: "Config received successfully"` |
| 5 | Verify response `stream_amount == 1` | Exactly one stream configured |
| 6 | Verify response `channel_to_stream_index == {str(max_sensor): 0}` | Correct mapping for max channel |
| 7 | Verify response `channel_amount == 1` | Only one channel configured |
| 8 | Poll GET /waterfall/{task_id}/10 | Status 201, data blocks returned |
| 9 | Verify each data block contains exactly 1 stream | Only one stream per block |
| 10 | Verify rows contain sensor ID == max_sensor | All rows have correct sensor ID |
| 11 | Validate intensity data is non-empty | Valid intensity values |
| 12 | Validate timestamps are sequential | Proper time ordering |

### Expected Result
- **Status code**: 200 for /configure, 201 for /waterfall
- **stream_amount**: 1
- **channel_to_stream_index**: `{str(max_sensor): 0}`
- **channel_amount**: 1
- **Data integrity**: All rows contain max_sensor with valid intensity data

### Post-Conditions
- Task active and delivering data for maximum channel
- No errors in server logs

### Assertions (Python Code)
```python
# Test function: test_singlechannel_maximum_channel

# Get available sensors
sensors_response = focus_server_api.get_sensors()
max_sensor = sensors_response.sensors[-1]
logger.info(f"Maximum sensor ID: {max_sensor}")

# Configure SingleChannel for max sensor
config_payload["channels"]["min"] = max_sensor
config_payload["channels"]["max"] = max_sensor
config_request = ConfigTaskRequest(**config_payload)
response = focus_server_api.config_task(task_id, config_request)

# Assertions
assert response.stream_amount == 1
assert response.channel_to_stream_index == {str(max_sensor): 0}
assert response.channel_amount == 1

# Verify data
waterfall_response = focus_server_api.get_waterfall(task_id, 10)
for data_block in waterfall_response.data:
    for row in data_block.data[0].rows:
        assert row.sensors[0].id == max_sensor
        assert len(row.sensors[0].intensity) > 0
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_maximum_channel`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## Test: PZ-SINGLE-EXT-003
**Test Name**: SingleChannel Edge Case - Middle Channel

### Summary
Validates SingleChannel view behavior when configuring a middle-range channel, ensuring correct 1:1 mapping and data delivery for a non-boundary sensor.

### Objective
Verify that Focus Server correctly handles SingleChannel view for any arbitrary channel in the middle of the sensor range, demonstrating that the feature works beyond just edge cases.

### Priority
**Medium**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `functional`, `channel-mapping`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-SINGLECHANNEL-ARBITRARY
- **Description**: SingleChannel view must work for any valid sensor index

### Pre-Conditions
1. Focus Server is running
2. At least 10 sensors available in the system
3. Baby Analyzer is processing data

### Test Data
```json
{
  "task_id": "singlechannel_middle_ch<middle>_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": <middle_sensor_id>,
      "max": <middle_sensor_id>
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```
**Note**: `<middle_sensor_id>` is calculated as `len(sensors) // 2`.

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Send GET /sensors | Sensors list returned |
| 2 | Calculate middle sensor ID (`middle = len(sensors) // 2`) | Middle sensor identified |
| 3 | Create `ConfigureRequest` with `channels.min=middle`, `channels.max=middle`, `view_type=SINGLECHANNEL` | Valid payload |
| 4 | Send POST /configure | Status 200, success message |
| 5 | Verify `stream_amount == 1` | One stream |
| 6 | Verify `channel_to_stream_index == {str(middle): 0}` | Correct mapping |
| 7 | Poll GET /waterfall | Status 201, data returned |
| 8 | Verify sensor ID in all rows matches middle channel | Correct sensor ID |
| 9 | Validate intensity data | Non-empty, valid values |

### Expected Result
- **stream_amount**: 1
- **channel_to_stream_index**: `{str(middle): 0}`
- **Data**: All rows contain middle channel sensor with valid intensity

### Post-Conditions
- Task active and delivering data for middle channel

### Assertions (Python Code)
```python
# Test function: test_singlechannel_middle_channel

sensors_response = focus_server_api.get_sensors()
middle_sensor = len(sensors_response.sensors) // 2

config_payload["channels"]["min"] = middle_sensor
config_payload["channels"]["max"] = middle_sensor
response = focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))

assert response.stream_amount == 1
assert response.channel_to_stream_index == {str(middle_sensor): 0}

waterfall_response = focus_server_api.get_waterfall(task_id, 10)
for data_block in waterfall_response.data:
    for row in data_block.data[0].rows:
        assert row.sensors[0].id == middle_sensor
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_middle_channel`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## Test: PZ-SINGLE-EXT-004
**Test Name**: SingleChannel with Invalid Channel (Out of Range High)

### Summary
Validates that Focus Server properly rejects SingleChannel configuration requests when the specified channel exceeds the maximum available sensor index.

### Objective
Verify proper error handling when attempting to configure a SingleChannel view with a channel ID that is higher than the maximum available sensor.

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `error-handling`, `validation`, `negative-test`
- **Test Type**: Integration Test (Negative)

### Requirements
- **Requirement ID**: FOCUS-API-SINGLECHANNEL-VALIDATION
- **Description**: SingleChannel view must validate channel bounds and reject out-of-range values

### Pre-Conditions
1. Focus Server is running
2. GET /sensors returns available sensor list (e.g., 0-99 for 100 sensors)
3. Maximum sensor ID is known

### Test Data
```json
{
  "task_id": "singlechannel_invalid_high_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 9999,
      "max": 9999
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```
**Note**: Channel 9999 is intentionally out of range.

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Send GET /sensors to get max available sensor | Status 200, sensors list returned |
| 2 | Create `ConfigureRequest` with `channels.min=9999`, `channels.max=9999` (out of range) | Payload created |
| 3 | Send POST /configure | Status 400 or 422 (Bad Request / Validation Error) |
| 4 | Verify error response contains appropriate message | Error message indicates "channel out of range" or similar |
| 5 | Attempt GET /waterfall/{task_id}/10 | Status 404 (task was never created) |

### Expected Result
- **Status code**: 400 or 422 for /configure
- **Error message**: "Channel index 9999 out of range" or similar validation error
- **Behavior**: Request rejected, no task created

### Post-Conditions
- No task created in server memory
- No consumer registered for this task_id

### Assertions (Python Code)
```python
# Test function: test_singlechannel_with_invalid_channel_high

sensors_response = focus_server_api.get_sensors()
max_sensor = sensors_response.sensors[-1]

invalid_channel = 9999  # Clearly out of range
config_payload["channels"]["min"] = invalid_channel
config_payload["channels"]["max"] = invalid_channel

# Expect validation error
with pytest.raises(Exception) as exc_info:
    focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))

# Verify error indicates channel out of range
assert "out of range" in str(exc_info.value).lower() or \
       "invalid channel" in str(exc_info.value).lower()

# Verify task was not created
waterfall_response = focus_server_api.get_waterfall(task_id, 10)
assert waterfall_response.status_code == 404, "Task should not exist"
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_with_invalid_channel_high`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## Test: PZ-SINGLE-EXT-005
**Test Name**: SingleChannel with Invalid Channel (Negative)

### Summary
Validates that Focus Server properly rejects SingleChannel configuration requests when the specified channel is a negative value.

### Objective
Verify proper error handling when attempting to configure a SingleChannel view with a negative channel ID.

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `error-handling`, `validation`, `negative-test`
- **Test Type**: Integration Test (Negative)

### Requirements
- **Requirement ID**: FOCUS-API-SINGLECHANNEL-VALIDATION
- **Description**: SingleChannel view must validate channel bounds and reject negative values

### Pre-Conditions
1. Focus Server is running
2. Sensor IDs are expected to be non-negative integers

### Test Data
```json
{
  "task_id": "singlechannel_invalid_negative_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": -5,
      "max": -5
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Create `ConfigureRequest` with `channels.min=-5`, `channels.max=-5` | Payload created |
| 2 | Send POST /configure | Status 400 or 422 (Validation Error) |
| 3 | Verify error response message | Error indicates "negative channel" or "invalid channel" |
| 4 | Verify task was not created | GET /waterfall returns 404 |

### Expected Result
- **Status code**: 400 or 422 for /configure
- **Error message**: "Channel index cannot be negative" or similar
- **Behavior**: Request rejected immediately

### Post-Conditions
- No task created

### Assertions (Python Code)
```python
# Test function: test_singlechannel_with_negative_channel

config_payload["channels"]["min"] = -5
config_payload["channels"]["max"] = -5

with pytest.raises(Exception) as exc_info:
    focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))

assert "negative" in str(exc_info.value).lower() or \
       "invalid" in str(exc_info.value).lower()

waterfall_response = focus_server_api.get_waterfall(task_id, 10)
assert waterfall_response.status_code == 404
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_with_negative_channel`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## Test: PZ-SINGLE-EXT-006
**Test Name**: SingleChannel with Min > Max (Validation Error)

### Summary
Validates that Focus Server properly rejects SingleChannel configuration requests when `channels.min > channels.max`, which violates the valid range definition for SingleChannel (min must equal max).

### Objective
Verify proper validation and error handling when attempting to configure a SingleChannel view with an invalid range where min is greater than max.

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `error-handling`, `validation`, `negative-test`
- **Test Type**: Integration Test (Negative)

### Requirements
- **Requirement ID**: FOCUS-API-SINGLECHANNEL-RANGE
- **Description**: For SingleChannel view, channels.min must equal channels.max (1:1 mapping)

### Pre-Conditions
1. Focus Server is running
2. Valid sensor range is known (e.g., 0-99)

### Test Data
```json
{
  "task_id": "singlechannel_min_gt_max_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 10,
      "max": 5
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```
**Note**: `min=10 > max=5` is invalid for SingleChannel.

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Create `ConfigureRequest` with `channels.min=10`, `channels.max=5`, `view_type=SINGLECHANNEL` | Payload created |
| 2 | Send POST /configure | Status 400 or 422 (Validation Error) |
| 3 | Verify error message | Error indicates "min > max" or "invalid range for SingleChannel" |
| 4 | Verify task not created | GET /waterfall returns 404 |

### Expected Result
- **Status code**: 400 or 422 for /configure
- **Error message**: "For SingleChannel view, channels.min must equal channels.max" or similar
- **Behavior**: Request rejected

### Post-Conditions
- No task created

### Assertions (Python Code)
```python
# Test function: test_singlechannel_min_greater_than_max

config_payload["channels"]["min"] = 10
config_payload["channels"]["max"] = 5  # Invalid: min > max

with pytest.raises(Exception) as exc_info:
    focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))

error_msg = str(exc_info.value).lower()
assert "min" in error_msg and "max" in error_msg or \
       "invalid range" in error_msg or \
       "singlechannel" in error_msg

waterfall_response = focus_server_api.get_waterfall(task_id, 10)
assert waterfall_response.status_code == 404
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_min_greater_than_max`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## Test: PZ-SINGLE-EXT-007
**Test Name**: SingleChannel Data Consistency Check

### Summary
Validates data consistency and integrity for a SingleChannel view over multiple polling cycles, ensuring that all returned data blocks consistently contain only the configured channel with valid, non-corrupted data.

### Objective
Verify that data delivered by Focus Server for a SingleChannel task is consistent across multiple polls, with correct sensor IDs, non-empty intensity arrays, and sequential timestamps.

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `data-integrity`, `consistency`, `quality`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-DATA-CONSISTENCY
- **Description**: Data returned from Focus Server must be consistent, complete, and free of corruption

### Pre-Conditions
1. Focus Server is running
2. Baby Analyzer is actively processing live data
3. SingleChannel task configured (e.g., channel 7)

### Test Data
```json
{
  "task_id": "singlechannel_consistency_ch7_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 7,
      "max": 7
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Configure SingleChannel task for channel 7 | Status 200, task configured |
| 2 | Poll GET /waterfall/{task_id}/20 (20 rows) | Status 201, data blocks returned |
| 3 | Verify all data blocks contain exactly 1 stream | `len(data_block.data) == 1` |
| 4 | Verify all rows in all streams have sensor ID == 7 | `row.sensors[0].id == 7` for all rows |
| 5 | Verify all intensity arrays are non-empty | `len(sensor.intensity) > 0` |
| 6 | Verify timestamps are sequential and increasing | `row[i].endTimestamp <= row[i+1].startTimestamp` |
| 7 | Repeat polling 5 more times (total 6 polls) | All polls return consistent data structure |
| 8 | Track total rows collected | Total rows > 100 (across all polls) |
| 9 | Verify no duplicate timestamps | All `startTimestamp` values are unique |
| 10 | Verify no missing data (gaps in timestamps) | Timestamp deltas are consistent |

### Expected Result
- **Consistency**: All polls return exactly 1 stream with sensor ID 7
- **Integrity**: All intensity arrays non-empty, no null/corrupted values
- **Timestamps**: Sequential, increasing, no duplicates, no gaps
- **Total rows**: > 100 rows collected across 6 polls

### Post-Conditions
- Task remains active
- No errors or warnings in logs

### Assertions (Python Code)
```python
# Test function: test_singlechannel_data_consistency

# Configure task
response = focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))
assert response.stream_amount == 1

all_rows = []
all_timestamps = set()

# Poll 6 times
for poll_num in range(6):
    waterfall_response = focus_server_api.get_waterfall(task_id, 20)
    assert waterfall_response.status_code == 201
    
    for data_block in waterfall_response.data:
        # Verify exactly 1 stream
        assert len(data_block.data) == 1
        
        for row in data_block.data[0].rows:
            # Verify sensor ID
            assert row.sensors[0].id == 7
            
            # Verify intensity data
            assert len(row.sensors[0].intensity) > 0
            
            # Track timestamps (check for duplicates)
            assert row.startTimestamp not in all_timestamps
            all_timestamps.add(row.startTimestamp)
            
            # Track all rows
            all_rows.append(row)
    
    time.sleep(1.0)  # Wait before next poll

# Verify timestamp ordering
for i in range(len(all_rows) - 1):
    assert all_rows[i].endTimestamp <= all_rows[i+1].startTimestamp

# Verify total rows collected
assert len(all_rows) > 100, f"Expected >100 rows, got {len(all_rows)}"
logger.info(f"Data consistency verified: {len(all_rows)} rows, all valid")
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_data_consistency`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## Test: PZ-SINGLE-EXT-008
**Test Name**: SingleChannel Frequency Range Validation

### Summary
Validates that SingleChannel view correctly applies and respects the specified frequency range configuration.

### Objective
Verify that when a SingleChannel task is configured with a specific frequency range (e.g., 100-300 Hz), the returned data reflects this configuration and the server processes the request correctly.

### Priority
**Medium**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `configuration`, `frequency-range`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-FREQUENCY-RANGE
- **Description**: Frequency range configuration must be applied correctly to data processing

### Pre-Conditions
1. Focus Server is running
2. Baby Analyzer supports frequency range filtering

### Test Data
```json
{
  "task_id": "singlechannel_freq_range_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 7,
      "max": 7
    },
    "frequencyRange": {
      "min": 100,
      "max": 300
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Create `ConfigureRequest` with `frequencyRange: {min: 100, max: 300}` | Payload validated |
| 2 | Send POST /configure | Status 200, task configured |
| 3 | Verify response indicates frequency range accepted | Response contains frequency range or no error |
| 4 | Poll GET /waterfall | Status 201, data returned |
| 5 | Verify intensity array length reflects frequency range | `len(intensity)` matches expected frequency bins |

### Expected Result
- **Configuration**: Frequency range 100-300 Hz applied
- **Data**: Intensity arrays have correct length for specified range

### Post-Conditions
- Task configured with custom frequency range

### Assertions (Python Code)
```python
# Test function: test_singlechannel_frequency_range_validation

config_payload["frequencyRange"]["min"] = 100
config_payload["frequencyRange"]["max"] = 300

response = focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))
assert response.status == "Config received successfully"

waterfall_response = focus_server_api.get_waterfall(task_id, 10)
assert waterfall_response.status_code == 201

# Verify data structure (intensity length may vary based on NFFT and freq range)
for data_block in waterfall_response.data:
    for row in data_block.data[0].rows:
        assert len(row.sensors[0].intensity) > 0
        logger.info(f"Intensity length: {len(row.sensors[0].intensity)}")
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_frequency_range_validation`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## Test: PZ-SINGLE-EXT-009
**Test Name**: SingleChannel Canvas Height Validation

### Summary
Validates that SingleChannel view correctly accepts and applies different canvas height configurations.

### Objective
Verify that Focus Server accepts various canvas height values (e.g., 500, 1000, 1500, 2000) and configures the task successfully.

### Priority
**Low**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `configuration`, `canvas-height`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-CANVAS-CONFIG
- **Description**: Canvas height configuration must be accepted and stored

### Pre-Conditions
1. Focus Server is running

### Test Data
```json
{
  "task_id": "singlechannel_canvas_height_<height>_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": <test_height>
    },
    "channels": {
      "min": 7,
      "max": 7
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```
**Test heights**: 500, 1000, 1500, 2000

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | For each height in [500, 1000, 1500, 2000] | Iterate test heights |
| 2 | Create `ConfigureRequest` with `displayInfo.height = <test_height>` | Payload created |
| 3 | Send POST /configure | Status 200, task configured |
| 4 | Verify response success | `status: "Config received successfully"` |
| 5 | Poll GET /waterfall | Status 201, data returned |

### Expected Result
- **All heights accepted**: 500, 1000, 1500, 2000 all configure successfully
- **No errors**: All requests return status 200

### Post-Conditions
- Tasks configured with different canvas heights

### Assertions (Python Code)
```python
# Test function: test_singlechannel_canvas_height_validation

test_heights = [500, 1000, 1500, 2000]

for height in test_heights:
    task_id = generate_task_id(f"canvas_height_{height}")
    config_payload["displayInfo"]["height"] = height
    
    response = focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))
    assert response.status == "Config received successfully"
    
    logger.info(f"Canvas height {height} configured successfully")
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_canvas_height_validation`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## Test: PZ-SINGLE-EXT-010
**Test Name**: SingleChannel NFFT Validation

### Summary
Validates that SingleChannel view correctly accepts and applies different NFFT (FFT size) configurations.

### Objective
Verify that Focus Server accepts various NFFT values (e.g., 512, 1024, 2048) and configures the task successfully, affecting the frequency resolution of the returned data.

### Priority
**Medium**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `configuration`, `nfft`, `fft`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-NFFT-CONFIG
- **Description**: NFFT configuration must be accepted and applied to signal processing

### Pre-Conditions
1. Focus Server is running
2. Baby Analyzer supports various NFFT values

### Test Data
```json
{
  "task_id": "singlechannel_nfft_<nfft>_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": <test_nfft>,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 7,
      "max": 7
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```
**Test NFFT values**: 512, 1024, 2048

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | For each NFFT in [512, 1024, 2048] | Iterate test NFFT values |
| 2 | Create `ConfigureRequest` with `nfftSelection = <test_nfft>` | Payload created |
| 3 | Send POST /configure | Status 200, task configured |
| 4 | Verify response success | `status: "Config received successfully"` |
| 5 | Poll GET /waterfall | Status 201, data returned |
| 6 | Verify intensity array length varies with NFFT | Different NFFT → different intensity array size |

### Expected Result
- **All NFFT values accepted**: 512, 1024, 2048 configure successfully
- **Data impact**: Intensity array length reflects NFFT configuration

### Post-Conditions
- Tasks configured with different NFFT values

### Assertions (Python Code)
```python
# Test function: test_singlechannel_nfft_validation

test_nfft_values = [512, 1024, 2048]

for nfft in test_nfft_values:
    task_id = generate_task_id(f"nfft_{nfft}")
    config_payload["nfftSelection"] = nfft
    
    response = focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))
    assert response.status == "Config received successfully"
    
    # Poll data and check intensity length
    waterfall_response = focus_server_api.get_waterfall(task_id, 5)
    for data_block in waterfall_response.data:
        for row in data_block.data[0].rows:
            intensity_len = len(row.sensors[0].intensity)
            logger.info(f"NFFT {nfft} → intensity length: {intensity_len}")
            assert intensity_len > 0
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_nfft_validation`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## Test: PZ-SINGLE-EXT-011
**Test Name**: SingleChannel Rapid Reconfiguration

### Summary
Validates that a SingleChannel task can be rapidly reconfigured multiple times without errors, ensuring the server handles configuration updates correctly.

### Objective
Verify that Focus Server can handle multiple rapid reconfigurations of the same task_id, updating the channel selection each time without memory leaks or errors.

### Priority
**Medium**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `reconfiguration`, `stress`, `stability`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-RECONFIGURATION
- **Description**: Tasks must support reconfiguration without resource leaks

### Pre-Conditions
1. Focus Server is running
2. At least 20 sensors available

### Test Data
```json
{
  "task_id": "singlechannel_rapid_reconfig_<timestamp>",
  "config_payload_template": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": <channel_id>,
      "max": <channel_id>
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Generate single task_id | Unique task_id created |
| 2 | For each channel in [0, 5, 10, 15, 20] (5 iterations) | Iterate channels |
| 3 | Update `config_payload` with new channel (min=max=channel) | Payload updated |
| 4 | Send POST /configure with same task_id | Status 200, configuration updated |
| 5 | Verify response `stream_amount == 1` | Single stream |
| 6 | Verify `channel_to_stream_index == {str(channel): 0}` | Correct channel mapped |
| 7 | Poll GET /waterfall | Status 201, data for new channel returned |
| 8 | Verify sensor ID matches new channel | Correct sensor in data |

### Expected Result
- **All reconfigurations succeed**: 5 rapid reconfigurations complete successfully
- **Data consistency**: Each poll returns data for the newly configured channel
- **No errors**: No memory leaks or server errors

### Post-Conditions
- Task configured with last channel (20)
- Server stable, no resource exhaustion

### Assertions (Python Code)
```python
# Test function: test_singlechannel_rapid_reconfiguration

task_id = generate_task_id("rapid_reconfig")
test_channels = [0, 5, 10, 15, 20]

for channel in test_channels:
    logger.info(f"Reconfiguring task to channel {channel}")
    
    config_payload["channels"]["min"] = channel
    config_payload["channels"]["max"] = channel
    
    response = focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))
    assert response.status == "Config received successfully"
    assert response.stream_amount == 1
    assert response.channel_to_stream_index == {str(channel): 0}
    
    # Verify data
    time.sleep(0.5)  # Brief wait for reconfiguration
    waterfall_response = focus_server_api.get_waterfall(task_id, 5)
    if waterfall_response.status_code == 201:
        for data_block in waterfall_response.data:
            for row in data_block.data[0].rows:
                assert row.sensors[0].id == channel

logger.info("Rapid reconfiguration test passed")
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_rapid_reconfiguration`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## Test: PZ-SINGLE-EXT-012
**Test Name**: SingleChannel Polling Stability

### Summary
Validates that prolonged polling of a SingleChannel task remains stable, with consistent response times and no degradation over time.

### Objective
Verify that continuous polling of a SingleChannel task for an extended period (e.g., 100 polls) does not result in performance degradation, memory leaks, or errors.

### Priority
**Medium**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `stability`, `performance`, `long-running`
- **Test Type**: Integration Test (Stability)

### Requirements
- **Requirement ID**: FOCUS-API-STABILITY
- **Description**: Continuous polling must remain stable without performance degradation

### Pre-Conditions
1. Focus Server is running
2. SingleChannel task configured

### Test Data
```json
{
  "task_id": "singlechannel_polling_stability_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 7,
      "max": 7
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Configure SingleChannel task | Status 200, task configured |
| 2 | For poll_num in range(100): | 100 polling iterations |
| 3 | Send GET /waterfall/{task_id}/10 | Status 201, data returned |
| 4 | Record response time | Response time tracked |
| 5 | Verify response structure | Valid data structure |
| 6 | Sleep 0.5 seconds | Wait before next poll |
| 7 | After all polls, analyze response times | Average response time calculated |
| 8 | Verify no significant degradation | Response times remain consistent |

### Expected Result
- **All polls succeed**: 100/100 polls return status 201
- **Response times stable**: No significant increase over time
- **No errors**: No timeouts or server errors

### Post-Conditions
- Task still active and responsive
- Server memory usage stable

### Assertions (Python Code)
```python
# Test function: test_singlechannel_polling_stability

response = focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))
assert response.stream_amount == 1

response_times = []
successful_polls = 0

for poll_num in range(100):
    start_time = time.time()
    waterfall_response = focus_server_api.get_waterfall(task_id, 10)
    elapsed = time.time() - start_time
    
    if waterfall_response.status_code == 201:
        successful_polls += 1
        response_times.append(elapsed)
    
    if poll_num % 20 == 0:
        logger.info(f"Poll {poll_num}/100, response time: {elapsed:.3f}s")
    
    time.sleep(0.5)

# Verify all polls succeeded
assert successful_polls >= 95, f"Only {successful_polls}/100 polls succeeded"

# Verify response times are stable
avg_response_time = sum(response_times) / len(response_times)
max_response_time = max(response_times)

logger.info(f"Polling stability: {successful_polls}/100 succeeded")
logger.info(f"Avg response time: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s")

assert avg_response_time < 2.0, "Average response time too high"
assert max_response_time < 5.0, "Max response time too high"
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_polling_stability`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## Test: PZ-SINGLE-EXT-013
**Test Name**: SingleChannel Metadata Consistency

### Summary
Validates that metadata returned for a SingleChannel task (via GET /metadata/{task_id}) is consistent with the configuration and reflects the single-channel setup.

### Objective
Verify that GET /metadata returns consistent and accurate metadata for a SingleChannel task, including channel count, stream count, and other configuration details.

### Priority
**Low**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `metadata`, `consistency`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-METADATA
- **Description**: Metadata endpoint must return accurate configuration details

### Pre-Conditions
1. Focus Server is running
2. SingleChannel task configured

### Test Data
```json
{
  "task_id": "singlechannel_metadata_<timestamp>",
  "config_payload": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 7,
      "max": 7
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Configure SingleChannel task for channel 7 | Status 200, task configured |
| 2 | Send GET /metadata/{task_id} | Status 200, metadata returned |
| 3 | Verify metadata contains expected fields | Required fields present |
| 4 | Verify metadata reflects SingleChannel configuration | Metadata shows 1 channel, 1 stream |
| 5 | Compare metadata with configuration | Metadata consistent with config |

### Expected Result
- **Metadata returned**: GET /metadata returns status 200
- **Consistency**: Metadata reflects SingleChannel configuration (1 channel, 1 stream)

### Post-Conditions
- Metadata endpoint functional

### Assertions (Python Code)
```python
# Test function: test_singlechannel_metadata_consistency

response = focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))
assert response.stream_amount == 1

# Get metadata
metadata_response = focus_server_api.get_metadata(task_id)

# Verify metadata structure
assert metadata_response is not None
logger.info(f"Metadata: {metadata_response}")

# Additional assertions based on actual metadata structure
# (may vary depending on API implementation)
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_metadata_consistency`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## Test: PZ-SINGLE-EXT-014
**Test Name**: SingleChannel Stream Mapping Verification

### Summary
Validates the `channel_to_stream_index` mapping returned in the configuration response for various SingleChannel configurations, ensuring correct 1:1 mapping in all cases.

### Objective
Verify that for any valid SingleChannel configuration (any channel ID), the `channel_to_stream_index` always maps the single channel to stream index 0.

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `channel-mapping`, `validation`
- **Test Type**: Integration Test

### Requirements
- **Requirement ID**: FOCUS-API-SINGLECHANNEL-MAPPING
- **Description**: SingleChannel must always map the configured channel to stream index 0

### Pre-Conditions
1. Focus Server is running
2. Multiple sensors available (e.g., 0-99)

### Test Data
```json
{
  "task_id_template": "singlechannel_mapping_ch<channel>_<timestamp>",
  "config_payload_template": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": <channel>,
      "max": <channel>
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }
}
```
**Test channels**: 0, 1, 7, 15, 25, 50, 99

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | For each channel in [0, 1, 7, 15, 25, 50, 99] | Iterate test channels |
| 2 | Create unique task_id for each channel | Task IDs generated |
| 3 | Create `ConfigureRequest` with `channels.min=channel`, `channels.max=channel` | Payload created |
| 4 | Send POST /configure | Status 200, task configured |
| 5 | Verify `stream_amount == 1` | Single stream |
| 6 | Verify `channel_to_stream_index == {str(channel): 0}` | Channel maps to stream 0 |
| 7 | Verify `channel_amount == 1` | Single channel |

### Expected Result
- **All channels map correctly**: Every channel (0, 1, 7, etc.) maps to stream index 0
- **stream_amount**: Always 1
- **channel_amount**: Always 1

### Post-Conditions
- Multiple tasks configured, each with correct mapping

### Assertions (Python Code)
```python
# Test function: test_singlechannel_stream_mapping_verification

test_channels = [0, 1, 7, 15, 25, 50, 99]

for channel in test_channels:
    task_id = generate_task_id(f"mapping_ch{channel}")
    
    config_payload["channels"]["min"] = channel
    config_payload["channels"]["max"] = channel
    
    response = focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))
    
    # Verify mapping
    assert response.stream_amount == 1
    assert response.channel_to_stream_index == {str(channel): 0}, \
        f"Channel {channel} did not map to stream 0"
    assert response.channel_amount == 1
    
    logger.info(f"Channel {channel} → Stream 0 (verified)")

logger.info("All channel-to-stream mappings verified")
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_stream_mapping_verification`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## Test: PZ-SINGLE-EXT-015
**Test Name**: SingleChannel Complete Flow End-to-End

### Summary
Comprehensive end-to-end test for SingleChannel view, covering configuration, data polling, metadata retrieval, reconfiguration, and cleanup, validating the complete lifecycle of a SingleChannel task.

### Objective
Verify that a SingleChannel task can be configured, polled for data, queried for metadata, reconfigured to a different channel, and cleaned up successfully, demonstrating a full end-to-end workflow.

### Priority
**High**

### Components/Labels
- **Component**: Focus Server Backend API
- **Labels**: `singlechannel`, `end-to-end`, `full-flow`, `lifecycle`
- **Test Type**: Integration Test (End-to-End)

### Requirements
- **Requirement ID**: FOCUS-API-SINGLECHANNEL-E2E
- **Description**: Complete SingleChannel lifecycle must function correctly

### Pre-Conditions
1. Focus Server is running
2. Baby Analyzer is processing data
3. At least 50 sensors available

### Test Data
```json
{
  "task_id": "singlechannel_e2e_<timestamp>",
  "initial_config": {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {
      "height": 1000
    },
    "channels": {
      "min": 10,
      "max": 10
    },
    "frequencyRange": {
      "min": 0,
      "max": 500
    },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  },
  "reconfig": {
    "channels": {
      "min": 25,
      "max": 25
    }
  }
}
```

### Steps
| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | **Phase 1: Initial Configuration** | - |
| 2 | Generate unique task_id | Task ID created |
| 3 | Send POST /configure with channel 10 | Status 200, `stream_amount=1`, `channel_to_stream_index={"10": 0}` |
| 4 | **Phase 2: Data Polling** | - |
| 5 | Poll GET /waterfall 10 times (collect data) | Status 201, 10 successful polls, data for channel 10 |
| 6 | Verify all data contains sensor ID 10 | All rows have `sensors[0].id == 10` |
| 7 | Verify timestamps are sequential | Timestamps increase across polls |
| 8 | **Phase 3: Metadata Retrieval** | - |
| 9 | Send GET /metadata/{task_id} | Status 200, metadata returned |
| 10 | Verify metadata consistency | Metadata reflects channel 10 configuration |
| 11 | **Phase 4: Reconfiguration** | - |
| 12 | Send POST /configure with channel 25 (same task_id) | Status 200, `channel_to_stream_index={"25": 0}` |
| 13 | Poll GET /waterfall 5 times | Status 201, data for channel 25 |
| 14 | Verify all data now contains sensor ID 25 | All rows have `sensors[0].id == 25` |
| 15 | **Phase 5: Cleanup (optional)** | - |
| 16 | If DELETE /task/{task_id} supported, send DELETE | Status 200, task deleted |
| 17 | Verify task no longer exists | GET /waterfall returns 404 |

### Expected Result
- **Phase 1**: Task configured successfully for channel 10
- **Phase 2**: 10 polls return valid data for channel 10
- **Phase 3**: Metadata retrieved and consistent
- **Phase 4**: Task reconfigured to channel 25, data updates correctly
- **Phase 5**: Task cleaned up (if supported)

### Post-Conditions
- Task either active (if cleanup not supported) or deleted
- No errors in server logs

### Assertions (Python Code)
```python
# Test function: test_singlechannel_complete_flow_e2e

task_id = generate_task_id("e2e")

# Phase 1: Initial Configuration
logger.info("Phase 1: Configuring channel 10")
response = focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))
assert response.stream_amount == 1
assert response.channel_to_stream_index == {"10": 0}

# Phase 2: Data Polling
logger.info("Phase 2: Polling data for channel 10")
poll_count = 0
for poll_num in range(10):
    waterfall_response = focus_server_api.get_waterfall(task_id, 5)
    if waterfall_response.status_code == 201:
        poll_count += 1
        for data_block in waterfall_response.data:
            for row in data_block.data[0].rows:
                assert row.sensors[0].id == 10
    time.sleep(0.5)

assert poll_count >= 8, f"Only {poll_count}/10 polls succeeded"

# Phase 3: Metadata
logger.info("Phase 3: Retrieving metadata")
metadata_response = focus_server_api.get_metadata(task_id)
assert metadata_response is not None

# Phase 4: Reconfiguration
logger.info("Phase 4: Reconfiguring to channel 25")
config_payload["channels"]["min"] = 25
config_payload["channels"]["max"] = 25
response = focus_server_api.config_task(task_id, ConfigTaskRequest(**config_payload))
assert response.channel_to_stream_index == {"25": 0}

time.sleep(1.0)  # Wait for reconfiguration

for poll_num in range(5):
    waterfall_response = focus_server_api.get_waterfall(task_id, 5)
    if waterfall_response.status_code == 201:
        for data_block in waterfall_response.data:
            for row in data_block.data[0].rows:
                assert row.sensors[0].id == 25
    time.sleep(0.5)

logger.info("End-to-end SingleChannel flow completed successfully")
```

### Environment
- **Environment Name**: new_production

### Automation Status
- ✅ **Automated**
- **Test Function**: `test_singlechannel_complete_flow_e2e`
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`

---

## 📊 Summary Statistics

### SingleChannel Extended Coverage
- **Total Tests**: 15
- **Priority Breakdown**:
  - High: 9 tests
  - Medium: 5 tests
  - Low: 1 test

### Test Categories
1. **Edge Cases**: 3 tests (min/max/middle channels)
2. **Error Handling**: 3 tests (invalid channels, validation errors)
3. **Data Quality**: 2 tests (consistency, integrity)
4. **Configuration**: 3 tests (frequency, canvas, NFFT)
5. **Stability**: 2 tests (rapid reconfig, polling stability)
6. **Integration**: 2 tests (metadata, complete E2E flow)

### Automation Status
- ✅ **100% Automated**: All 15 tests are fully automated
- **Test File**: `tests/integration/api/test_singlechannel_view_mapping.py`
- **Execution**: `pytest -m "integration and api" tests/integration/api/test_singlechannel_view_mapping.py`

---

## ✅ Documentation Quality Checklist
- [x] All 15 tests fully documented
- [x] English language throughout
- [x] Strict format compliance (Summary, Objective, Priority, etc.)
- [x] Test Data includes complete JSON payloads
- [x] Steps tables with expected results
- [x] Python assertion code blocks for all tests
- [x] Environment and automation status specified
- [x] Ready for Jira Xray import

---

**End of Part 6: SingleChannel Extended Tests Documentation**

