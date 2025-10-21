# 📋 High Priority Tests - Xray Documentation
## תיעוד מלא לטסטים High Priority בפורמט Xray

**תאריך:** 2025-10-21  
**סביבה:** new_production (panda namespace)  
**סה"כ טסטים:** 10 High Priority Test Cases  

---

# TEST 1: PZ-13879

## Test ID
**PZ-13879**

## Summary
Integration – Missing Required Fields

## Objective
Validates that Focus Server properly rejects configuration requests that are missing required fields (e.g., missing `channels`, `frequencyRange`, or `nfftSelection`). This ensures proper input validation and prevents incomplete configurations from being processed.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `config-validation`, `negative-test`, `required-fields`, `input-validation`
* **Test Type**: Integration Test (Negative)

## Requirements
* **Requirement ID**: FOCUS-API-CONFIG-VALIDATION-001
* **Description**: Server must validate all required fields in configuration requests and reject incomplete requests with appropriate error messages

## Pre-Conditions
1. Focus Server is running and accessible at `https://10.10.100.100/focus-server/`
2. API endpoint `POST /config/{task_id}` is available
3. Test client has network access to Focus Server
4. MongoDB is accessible at `10.10.100.108:27017`

## Test Data

### Test Data 1: Missing 'channels' Field
```json
{
  "nfftSelection": 1024,
  "frequencyRange": {
    "min": 0,
    "max": 500
  },
  "displayInfo": {
    "height": 1000
  },
  "view_type": 0
}
```
**Note**: Missing `channels` field - should be rejected

### Test Data 2: Missing 'frequencyRange' Field
```json
{
  "nfftSelection": 1024,
  "channels": {
    "min": 0,
    "max": 50
  },
  "displayInfo": {
    "height": 1000
  },
  "view_type": 0
}
```
**Note**: Missing `frequencyRange` field - should be rejected

### Test Data 3: Missing 'nfftSelection' Field
```json
{
  "channels": {
    "min": 0,
    "max": 50
  },
  "frequencyRange": {
    "min": 0,
    "max": 500
  },
  "displayInfo": {
    "height": 1000
  },
  "view_type": 0
}
```
**Note**: Missing `nfftSelection` field - should be rejected

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Generate unique `task_id` (e.g., `missing_fields_test_<timestamp>`) | Valid task_id format (alphanumeric with underscores) |
| 2 | Create configuration payload **without** `channels` field (Test Data 1) | JSON payload created successfully |
| 3 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` with Test Data 1, headers: `Content-Type: application/json` | HTTP 400 Bad Request |
| 4 | Verify response error message contains "channels" or "required field" | Error message clearly indicates missing field |
| 5 | Create configuration payload **without** `frequencyRange` field (Test Data 2) | JSON payload created successfully |
| 6 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` with Test Data 2 | HTTP 400 Bad Request |
| 7 | Verify response error message contains "frequencyRange" or "frequency" | Error message clearly indicates missing field |
| 8 | Create configuration payload **without** `nfftSelection` field (Test Data 3) | JSON payload created successfully |
| 9 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` with Test Data 3 | HTTP 400 Bad Request |
| 10 | Verify response error message contains "nfft" or "required field" | Error message clearly indicates missing field |
| 11 | Query database to verify no orphaned tasks created: `db.tasks.find({task_id: {$in: [task_id_1, task_id_2, task_id_3]}})` | No tasks found in database |

## Expected Result
* **All** configuration requests missing required fields are **rejected** with HTTP 400 Bad Request
* Error messages clearly indicate which field is missing (e.g., "Missing required field: channels")
* No tasks are created in the system for invalid configurations
* Server remains stable and responsive
* Response time < 500ms for validation errors

## Post-Conditions
* No tasks created in MongoDB
* Server logs contain validation errors with timestamps
* System state unchanged - no side effects
* Server health check remains GREEN

## Environment

**Environment Name**: new_production (panda namespace)

**Backend (Focus Server)**:
- URL: `https://10.10.100.100/focus-server/`
- API Endpoint: `POST https://10.10.100.100/focus-server/config/{task_id}`
- Swagger: `https://10.10.100.100/api/swagger/#/`
- SSL Verification: `False` (self-signed certificate)

**Frontend (LiveView)**:
- URL: `https://10.10.10.100/liveView?siteId=prisma-210-1000`

**MongoDB**:
- Host: `10.10.100.108:27017`
- Connection: `mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma`
- Database: `prisma`
- Collections: `tasks`, `recordings`, `metadata`

**RabbitMQ**:
- AMQP: `10.10.100.107:5672`
- Management UI: `http://10.10.100.107:15672`
- Credentials: `prisma/prisma`

**Kubernetes**:
- API Server: `https://10.10.100.102:6443`
- Namespace: `panda`
- Focus Server Service: `panda-panda-focus-server.panda:5000` (ClusterIP: 10.43.103.101)

**SSH Access** (for infrastructure validation):
- Jump Host: `ssh root@10.10.100.3`
- Target Host: `ssh prisma@10.10.100.113`

## Automation Status

✅ **Automated**

**Framework**: pytest 7.0+  
**Python Version**: 3.11+  
**Test Function**: `test_missing_channels_field`, `test_missing_frequency_range_field`, `test_missing_nfft_field`, `test_missing_view_type_field`  
**Test File**: `tests/integration/api/test_config_validation_high_priority.py`  
**Test Class**: `TestMissingRequiredFields`  
**Lines**: 54-168

**Run Command**:
```bash
# Run all missing fields tests
pytest tests/integration/api/test_config_validation_high_priority.py::TestMissingRequiredFields -v

# Run specific test
pytest tests/integration/api/test_config_validation_high_priority.py::TestMissingRequiredFields::test_missing_channels_field -v

# Run with markers
pytest -m "critical" -k "missing" -v

# Generate report
pytest tests/integration/api/test_config_validation_high_priority.py::TestMissingRequiredFields \
  --junitxml=results/PZ-13879.xml \
  --html=results/PZ-13879.html
```

**Expected Test Duration**: ~2-3 seconds

---

# TEST 2: PZ-13878

## Test ID
**PZ-13878**

## Summary
Integration – Invalid View Type - Out of Range

## Objective
Validates that Focus Server properly rejects configuration requests with invalid `view_type` values (outside the defined enum range). Valid values are `0` (MULTICHANNEL) or `1` (SINGLECHANNEL). Any other value should be rejected with a clear error message.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `config-validation`, `enum-validation`, `negative-test`, `view-type`
* **Test Type**: Integration Test (Negative)

## Requirements
* **Requirement ID**: FOCUS-API-CONFIG-VALIDATION-002
* **Description**: Server must validate view_type enum and reject values outside [0, 1] range with descriptive error

## Pre-Conditions
1. Focus Server is running and accessible at `https://10.10.100.100/focus-server/`
2. API endpoint `POST /config/{task_id}` is available
3. Valid enum values documented: `0=MULTICHANNEL`, `1=SINGLECHANNEL`
4. Server enforces enum validation

## Test Data

### Test Data 1: Negative view_type
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": -1
}
```
**Note**: `view_type=-1` is invalid (must be 0 or 1)

### Test Data 2: Out-of-range view_type
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 99
}
```
**Note**: `view_type=99` is invalid (must be 0 or 1)

### Test Data 3: String view_type (type mismatch)
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": "invalid"
}
```
**Note**: `view_type="invalid"` is wrong type (must be integer 0 or 1)

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Generate unique `task_id` (e.g., `invalid_view_type_test_<timestamp>`) | Valid task_id created |
| 2 | Create configuration with `view_type=-1` (Test Data 1) | JSON payload created |
| 3 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` with Test Data 1 | HTTP 400 Bad Request |
| 4 | Verify response body contains error: `"view_type must be 0 or 1"` or similar | Error message present and descriptive |
| 5 | Generate new `task_id` for second test | Valid task_id created |
| 6 | Create configuration with `view_type=99` (Test Data 2) | JSON payload created |
| 7 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | HTTP 400 Bad Request |
| 8 | Verify error indicates out-of-range: `"view_type 99 is not valid. Must be 0 (MULTICHANNEL) or 1 (SINGLECHANNEL)"` | Descriptive error with valid values listed |
| 9 | Generate new `task_id` for third test | Valid task_id created |
| 10 | Attempt to create configuration with `view_type="invalid"` (Test Data 3) | Type validation error OR JSON parsing error |
| 11 | Send request (if payload created) or verify type validation | HTTP 400 Bad Request or type error before sending |
| 12 | Verify no tasks created: `db.tasks.find({task_id: {$regex: "invalid_view_type"}})` | Zero tasks found |

## Expected Result
* **All** invalid `view_type` values are **rejected** with HTTP 400 Bad Request
* Error messages clearly indicate:
  - Current invalid value
  - Valid values (0 or 1)
  - Semantic meaning (MULTICHANNEL / SINGLECHANNEL)
* Type validation prevents non-integer values
* Server remains stable after multiple invalid requests
* Response time < 300ms for validation errors

## Post-Conditions
* No tasks created in MongoDB
* Server logs contain validation errors with details
* System state unchanged
* No memory leaks or resource exhaustion

## Environment
**Same as PZ-13879** (new_production environment - see above for full details)

## Automation Status

✅ **Automated**

**Framework**: pytest 7.0+  
**Test Function**: `test_invalid_view_type_negative`, `test_invalid_view_type_out_of_range`, `test_invalid_view_type_string`  
**Test File**: `tests/integration/api/test_config_validation_high_priority.py`  
**Test Class**: `TestInvalidViewType`  
**Lines**: 171-293

**Run Command**:
```bash
# Run all invalid view type tests
pytest tests/integration/api/test_config_validation_high_priority.py::TestInvalidViewType -v

# Run with coverage
pytest tests/integration/api/test_config_validation_high_priority.py::TestInvalidViewType --cov=src.models --cov-report=html
```

**Expected Test Duration**: ~1-2 seconds

---

# TEST 3: PZ-13877

## Test ID
**PZ-13877**

## Summary
Integration – Invalid Frequency Range - Min > Max

## Objective
Validates that Focus Server properly rejects configuration requests where `frequencyRange.min > frequencyRange.max`, which represents an invalid/impossible frequency range. This ensures data integrity and prevents undefined behavior in frequency analysis.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `config-validation`, `range-validation`, `frequency`, `negative-test`
* **Test Type**: Integration Test (Negative)

## Requirements
* **Requirement ID**: FOCUS-API-CONFIG-VALIDATION-003
* **Description**: Server must validate that frequencyRange.min ≤ frequencyRange.max and reject invalid ranges

## Pre-Conditions
1. Focus Server is running at `https://10.10.100.100/focus-server/`
2. Frequency range validation is implemented
3. Server understands frequency range semantics

## Test Data

### Test Data 1: Min > Max (Invalid)
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {
    "min": 500,
    "max": 100
  },
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```
**Note**: `min=500 > max=100` - INVALID

### Test Data 2: Min == Max (Edge Case)
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {
    "min": 250,
    "max": 250
  },
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```
**Note**: `min == max` - Edge case (zero range) - behavior to be determined

### Test Data 3: Negative Frequencies
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {
    "min": -100,
    "max": 500
  },
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```
**Note**: `min=-100` - Negative frequency (physically meaningless)

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Generate `task_id` | Valid task_id |
| 2 | Create config with `frequencyRange.min=500, max=100` (Test Data 1) | Payload created |
| 3 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | HTTP 400 Bad Request |
| 4 | Verify error: `"frequencyRange.min (500) must be <= frequencyRange.max (100)"` | Clear error message with actual values |
| 5 | Create config with `frequencyRange.min=250, max=250` (Test Data 2) | Payload created |
| 6 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | HTTP 400 Bad Request OR 200 (if zero range allowed) |
| 7 | Document behavior for specs meeting | Behavior logged for future specification |
| 8 | Create config with negative frequency (Test Data 3) | Payload created |
| 9 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | HTTP 400 Bad Request |
| 10 | Verify error mentions non-negative requirement | Error: "Frequency values must be non-negative" |

## Expected Result
* `frequencyRange.min > frequencyRange.max` is **rejected** with HTTP 400
* Error message shows both values and explains constraint
* Negative frequencies are **rejected**
* Edge case (min == max) behavior is **documented**
* No undefined behavior in system

## Post-Conditions
* No tasks created
* Validation errors logged
* System stable

## Environment
**Same as PZ-13879** (new_production)

## Automation Status

✅ **Automated**

**Test Function**: `test_invalid_frequency_range_min_greater_than_max`, `test_frequency_range_equal_min_max`  
**Test File**: `tests/integration/api/test_config_validation_high_priority.py`  
**Test Class**: `TestInvalidRanges`  
**Lines**: 296-392

**Run Command**:
```bash
pytest tests/integration/api/test_config_validation_high_priority.py::TestInvalidRanges::test_invalid_frequency_range_min_greater_than_max -v
```

**Expected Test Duration**: ~1 second

---

# TEST 4: PZ-13876

## Test ID
**PZ-13876**

## Summary
Integration – Invalid Channel Range - Min > Max

## Objective
Validates that Focus Server properly rejects configuration requests where `channels.min > channels.max`, which represents an invalid sensor/channel range. This is critical for ROI (Region of Interest) validation.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `config-validation`, `channel-validation`, `roi`, `negative-test`
* **Test Type**: Integration Test (Negative)

## Requirements
* **Requirement ID**: FOCUS-API-CONFIG-VALIDATION-004
* **Description**: Server must validate that channels.min ≤ channels.max for valid ROI definition

## Pre-Conditions
1. Focus Server is running
2. Channel/sensor range validation implemented
3. System knows total available channels

## Test Data

### Test Data 1: Min > Max (Invalid)
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {
    "min": 50,
    "max": 10
  },
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```
**Note**: `channels: min=50 > max=10` - INVALID

### Test Data 2: Min == Max (SingleChannel Equivalent)
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {
    "min": 7,
    "max": 7
  },
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```
**Note**: `min == max` - May be valid as SingleChannel equivalent

### Test Data 3: Negative Channel IDs
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {
    "min": -5,
    "max": 50
  },
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```
**Note**: `min=-5` - Negative channel ID (invalid)

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Generate `task_id` | Valid task_id |
| 2 | Create config with `channels.min=50, max=10` (Test Data 1) | Payload created |
| 3 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | HTTP 400 Bad Request |
| 4 | Verify error: `"channels.min (50) must be <= channels.max (10)"` | Descriptive error |
| 5 | Create config with `channels.min=7, max=7` (Test Data 2) | Payload created |
| 6 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | HTTP 200 OR 400 (document behavior) |
| 7 | If accepted, verify view_type handling | Check if treated as SINGLECHANNEL |
| 8 | Create config with negative channel (Test Data 3) | Payload created |
| 9 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | HTTP 400 Bad Request |
| 10 | Verify error: `"Channel IDs must be non-negative"` | Clear error |

## Expected Result
* `channels.min > channels.max` is **rejected**
* Negative channel IDs are **rejected**
* Edge case (min == max) behavior **documented**
* Clear error messages

## Post-Conditions
* No invalid tasks created
* System stable

## Environment
**Same as PZ-13879** (new_production)

## Automation Status

✅ **Automated**

**Test Function**: `test_invalid_channel_range_min_greater_than_max`, `test_channel_range_equal_min_max`  
**Test File**: `tests/integration/api/test_config_validation_high_priority.py`  
**Test Class**: `TestInvalidRanges`  
**Lines**: 395-478

**Run Command**:
```bash
pytest tests/integration/api/test_config_validation_high_priority.py::TestInvalidRanges::test_invalid_channel_range_min_greater_than_max -v
```

**Expected Test Duration**: ~1 second

---

# TEST 5: PZ-13873

## Test ID
**PZ-13873**

## Summary
Integration - Valid Configuration - All Parameters

## Objective
Validates that Focus Server correctly **accepts** and processes a fully valid configuration request with all parameters properly set. This is the happy path test that confirms basic configuration functionality works correctly.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `config-validation`, `happy-path`, `smoke-test`, `positive-test`
* **Test Type**: Integration Test (Positive)

## Requirements
* **Requirement ID**: FOCUS-API-CONFIG-BASIC-001
* **Description**: Server must accept and process valid configuration requests successfully

## Pre-Conditions
1. Focus Server is running at `https://10.10.100.100/focus-server/`
2. All required services (MongoDB, RabbitMQ) are healthy
3. System has available resources for task creation

## Test Data

### Test Data 1: Complete Valid Configuration (MULTICHANNEL)
```json
{
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
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```
**Note**: All required fields present, valid values, MULTICHANNEL mode

### Test Data 2: Valid SINGLECHANNEL Configuration
```json
{
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
```
**Note**: SINGLECHANNEL mode with view_type=1

### Test Data 3: Valid with Various NFFT Values
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 2048,
  "displayInfo": {
    "height": 1000
  },
  "channels": {
    "min": 0,
    "max": 100
  },
  "frequencyRange": {
    "min": 0,
    "max": 1000
  },
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```
**Note**: Higher NFFT (2048), wider ranges

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Generate unique `task_id` (e.g., `valid_config_test_<timestamp>`) | Valid task_id created |
| 2 | Create complete valid configuration (Test Data 1) | JSON payload with all required fields |
| 3 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` with Test Data 1 | HTTP 200 OK |
| 4 | Verify response: `{"status": "Config received successfully"}` or similar | Success status in response body |
| 5 | Query metadata endpoint: `GET https://10.10.100.100/focus-server/metadata/{task_id}` | HTTP 200 with task metadata |
| 6 | Verify metadata matches configuration | All config parameters reflected in metadata |
| 7 | Query database: `db.tasks.findOne({task_id: "<task_id>"})` | Task document exists with correct config |
| 8 | Create SINGLECHANNEL config (Test Data 2) with new task_id | Payload created |
| 9 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | HTTP 200 OK |
| 10 | Verify SINGLECHANNEL mode activated | Metadata shows view_type=1 |
| 11 | Test various NFFT values (256, 512, 1024, 2048) | All accepted (power of 2 values) |
| 12 | Verify response times < 500ms for all requests | Performance within acceptable range |

## Expected Result
* All **valid** configurations are **accepted** with HTTP 200 OK
* Response includes success status message
* Tasks are created in MongoDB with correct configuration
* Metadata endpoint returns configuration details
* Task can be queried via `/waterfall` endpoint
* System processes configuration without errors
* All NFFT power-of-2 values accepted (256, 512, 1024, 2048)
* Both view_type 0 and 1 work correctly

## Post-Conditions
* Tasks created successfully in MongoDB
* Baby Analyzer initialized with configuration
* Task ready for data streaming
* Server logs show successful configuration
* System resources allocated appropriately

## Environment
**Same as PZ-13879** (new_production environment)

## Automation Status

✅ **Automated**

**Test Function**: `test_valid_configuration_all_parameters`, `test_valid_configuration_multichannel_explicit`, `test_valid_configuration_singlechannel_explicit`, `test_valid_configuration_various_nfft_values`  
**Test File**: `tests/integration/api/test_config_validation_high_priority.py`  
**Test Class**: `TestValidConfigurationAllParameters`  
**Lines**: 481-635

**Run Command**:
```bash
# Run all valid configuration tests
pytest tests/integration/api/test_config_validation_high_priority.py::TestValidConfigurationAllParameters -v

# Run specific test
pytest tests/integration/api/test_config_validation_high_priority.py::TestValidConfigurationAllParameters::test_valid_configuration_all_parameters -v
```

**Expected Test Duration**: ~3-5 seconds

---

# TEST 6: PZ-13419

## Test ID
**PZ-13419**

## Summary
GET /channels - Enabled Channels List

## Objective
Validates that the `GET /channels` endpoint returns a list of all enabled/available channels in the system. This is a critical smoke test that verifies basic API functionality and channel discovery mechanism. The endpoint is used by clients to determine which channels are available for configuration.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `api-endpoint`, `channels`, `smoke-test`, `get-request`, `discovery`
* **Test Type**: Integration Test (Smoke)

## Requirements
* **Requirement ID**: FOCUS-API-CHANNELS-001
* **Description**: Server must provide endpoint to query available/enabled channels

## Pre-Conditions
1. Focus Server is running at `https://10.10.100.100/focus-server/`
2. System has channels configured (fiber optic sensors)
3. At least one channel is enabled
4. Endpoint is accessible without authentication (or with valid credentials)

## Test Data

**No request body required** (GET request)

**Query Parameters**: None required

**Headers**:
```
Accept: application/json
Content-Type: application/json
```

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Send `GET https://10.10.100.100/focus-server/channels` request | HTTP 200 OK |
| 2 | Verify response Content-Type is `application/json` | Header: `Content-Type: application/json` |
| 3 | Parse response body as JSON | Valid JSON structure |
| 4 | Verify response contains list/array of channels | Response is array or object with `channels` field |
| 5 | Verify list is non-empty | `channels.length > 0` |
| 6 | For each channel in list, verify structure has `id` or `channel_id` field | All channels have identifier |
| 7 | Verify channel IDs are non-negative integers | All IDs >= 0 |
| 8 | Verify channel IDs are in reasonable range (0-10000) | All IDs < 10000 |
| 9 | Optional: Verify `enabled` or `status` field if present | If present, all should be `enabled: true` |
| 10 | Measure response time | Response time < 1000ms |
| 11 | Send request again and verify consistency | Same channels returned |
| 12 | Optional: Verify channel count matches system configuration | Count matches expected number |

## Expected Result
* Endpoint returns **HTTP 200 OK**
* Response contains **list of channels**
* List is **non-empty** (at least 1 channel)
* Each channel has:
  - **Valid ID** (non-negative integer)
  - **Reasonable range** (0-10000 or system max)
  - Optional: `enabled: true` or `status: "active"`
* Response is **consistent** across multiple calls
* Response time < 1000ms
* No errors or exceptions

## Post-Conditions
* No state changes (read-only operation)
* Server remains responsive
* Endpoint remains available

## Environment
**Same as PZ-13879** (new_production environment)

**Specific Endpoint**:
- URL: `GET https://10.10.100.100/focus-server/channels`
- Alternative: `GET https://10.10.100.100/api/channels`

## Automation Status

✅ **Automated**

**Test Function**: `test_get_channels_endpoint_success`, `test_get_channels_endpoint_response_time`, `test_get_channels_endpoint_multiple_calls_consistency`, `test_get_channels_endpoint_channel_ids_sequential`, `test_get_channels_endpoint_enabled_status`  
**Test File**: `tests/integration/api/test_api_endpoints_high_priority.py`  
**Test Class**: `TestChannelsEndpoint`  
**Lines**: 30-267

**Run Command**:
```bash
# Run all channels endpoint tests
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint -v

# Run specific test
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint::test_get_channels_endpoint_success -v

# Run with markers
pytest -m "smoke" -k "channels" -v
```

**Expected Test Duration**: ~2-3 seconds

---

# TEST 7: PZ-13868

## Test ID
**PZ-13868**

## Summary
Historic Playback - Status 208 Completion

## Objective
Validates that historic playback properly completes with HTTP status code 208 ("Already Reported") when all historical data has been delivered. This status indicates that the playback has finished and no more data is available for the requested time range. This is critical for clients to know when to stop polling.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `historic-playback`, `status-208`, `completion`, `polling`
* **Test Type**: Integration Test (Flow)

## Requirements
* **Requirement ID**: FOCUS-API-HISTORIC-COMPLETE-001
* **Description**: Server must signal playback completion with status 208

## Pre-Conditions
1. Focus Server is running
2. MongoDB contains historical recording data (at least 2+ hours old)
3. Historic playback functionality is implemented
4. Waterfall endpoint supports status 208

## Test Data

**Configuration for 1-minute historic range**:
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": "251021120000",
  "end_time": "251021120100",
  "view_type": 0
}
```
**Note**: `start_time` and `end_time` in format `yymmddHHMMSS` (1 minute duration, 2 hours ago)

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Calculate time range: 1 minute duration, 2 hours in the past | Valid time range (ensure data exists) |
| 2 | Convert times to `yymmddHHMMSS` format | Valid timestamp strings (12 digits) |
| 3 | Generate unique `task_id` | Valid task_id |
| 4 | Create config with `start_time` and `end_time` | Historic config payload |
| 5 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | HTTP 200 OK - config accepted |
| 6 | Poll `GET https://10.10.100.100/focus-server/waterfall/{task_id}/100` every 500ms | Initially: HTTP 200 (no data yet) or 201 (data available) |
| 7 | Track status codes seen: 200 → 201 → 208 | Status progression documented |
| 8 | Continue polling until status 208 received | Eventually: HTTP 208 |
| 9 | Verify status 208 has **no data** in response body | `data: null` or empty |
| 10 | Poll 5 more times after receiving 208 | All subsequent polls: 208, 404, or 400 |
| 11 | Verify **no status 201** (new data) after 208 | No new data after completion |
| 12 | Measure total time to completion | Time < 60 seconds for 1-minute range |

## Expected Result
* Historic playback **completes** with **HTTP 208**
* Status progression: `200 → 201 → 208`
* Status 208 contains **no data** (or empty data)
* After 208:
  - No new data (status 201) appears
  - Subsequent polls return 208, 404, or 400
* Completion happens within reasonable time (< 60s for 1-min range)
* Clear indication that playback is complete

## Post-Conditions
* Task marked as complete in system
* No more data available for this task
* Resources released (if applicable)
* Task may be cleaned up after timeout

## Environment
**Same as PZ-13879** (new_production environment)

## Automation Status

✅ **Automated**

**Test Function**: `test_historic_status_208_completion`, `test_historic_status_208_no_subsequent_data`  
**Test File**: `tests/integration/api/test_historic_high_priority.py`  
**Test Class**: `TestHistoricStatus208Completion`  
**Lines**: 48-199

**Run Command**:
```bash
pytest tests/integration/api/test_historic_high_priority.py::TestHistoricStatus208Completion -v
```

**Expected Test Duration**: ~30-60 seconds (includes polling)

---

# TEST 8: PZ-13871

## Test ID
**PZ-13871**

## Summary
Historic Playback - Timestamp Ordering Validation

## Objective
Validates that timestamps in historic playback data are **monotonically increasing** (each timestamp >= previous timestamp). This is critical for data integrity, ensuring that time-series data is delivered in correct chronological order. Out-of-order timestamps can cause serious issues in client applications and data analysis.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `historic-playback`, `data-integrity`, `timestamps`, `ordering`
* **Test Type**: Integration Test (Data Quality)

## Requirements
* **Requirement ID**: FOCUS-API-HISTORIC-ORDERING-001
* **Description**: Historic data timestamps must be monotonically increasing

## Pre-Conditions
1. Focus Server is running
2. MongoDB contains historical data with timestamps
3. Historic playback returns data with timestamp fields
4. Data is retrieved from actual recordings (not synthetic)

## Test Data

**Configuration for 2-minute historic range**:
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": "251021120000",
  "end_time": "251021120200",
  "view_type": 0
}
```
**Note**: 2-minute range for sufficient data points

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Calculate 2-minute time range, 2 hours ago | Valid time range |
| 2 | Generate `task_id` and configure historic task | Task configured successfully |
| 3 | Poll waterfall endpoint to collect data | Multiple data blocks received |
| 4 | Extract all timestamps from all data blocks: `block.rows[].startTimestamp` and `endTimestamp` | List of timestamps collected |
| 5 | Verify list contains at least 10 timestamps | Sufficient data for validation |
| 6 | Sort timestamps into chronological order | Timestamps ordered |
| 7 | Iterate through timestamps: for i in 0..N-1, verify `timestamp[i] < timestamp[i+1]` | All pairs satisfy: `T[i] < T[i+1]` |
| 8 | Check within each data block: verify `row.endTimestamp > row.startTimestamp` | End > Start for every row |
| 9 | Check between consecutive rows: verify `row[i].endTimestamp <= row[i+1].startTimestamp` | No overlaps or gaps violations |
| 10 | Calculate timestamp gaps: `gap[i] = timestamp[i+1] - timestamp[i]` | All gaps > 0 |
| 11 | Verify no unreasonably large gaps (> 10 seconds) | All gaps < 10s |
| 12 | Verify no unreasonably small gaps (< 0.1ms) | All gaps > 0.0001s |

## Expected Result
* **All timestamps are monotonically increasing**
* No timestamp violations: `T[i] >= T[i+1]`
* Within each row: `endTimestamp > startTimestamp`
* Between rows: no time overlaps (or overlaps are intentional/documented)
* Timestamp gaps are reasonable (0.0001s < gap < 10s)
* No duplicates (unless explicitly allowed)
* Data integrity maintained throughout playback

## Post-Conditions
* Data validated successfully
* No data corruption detected
* Client can safely process data chronologically

## Environment
**Same as PZ-13879** (new_production environment)

## Automation Status

✅ **Automated**

**Test Function**: `test_timestamp_ordering_monotonic_increasing`, `test_timestamp_ordering_within_blocks`, `test_timestamp_gap_validation`  
**Test File**: `tests/integration/api/test_historic_high_priority.py`  
**Test Class**: `TestHistoricTimestampOrdering`  
**Lines**: 202-427

**Run Command**:
```bash
pytest tests/integration/api/test_historic_high_priority.py::TestHistoricTimestampOrdering -v
```

**Expected Test Duration**: ~20-40 seconds

---

# TEST 9: PZ-13853

## Test ID
**PZ-13853**

## Summary
SingleChannel - Data Consistency Check

## Objective
Validates that SingleChannel view returns **consistent data** across multiple requests for the same channel. Data consistency is critical for ensuring that the same channel configuration produces reproducible results. This test verifies that sensor mapping, data structure, and metadata remain stable.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `singlechannel`, `data-consistency`, `reproducibility`
* **Test Type**: Integration Test (Quality)

## Requirements
* **Requirement ID**: FOCUS-API-SINGLECHANNEL-CONSISTENCY-001
* **Description**: Same channel must return consistent data structure across multiple requests

## Pre-Conditions
1. Focus Server is running
2. SingleChannel view is implemented (`view_type=1`)
3. System has live data available
4. At least one valid channel exists (e.g., channel 7)

## Test Data

**SingleChannel Configuration for Channel 7**:
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {
    "min": 7,
    "max": 7
  },
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 1
}
```
**Note**: `channels.min == channels.max` for SingleChannel, `view_type=1`

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Generate two unique task IDs: `task_1` and `task_2` | Two valid task_ids |
| 2 | Configure `task_1` with channel 7 (Test Data) | HTTP 200 - task configured |
| 3 | Configure `task_2` with same channel 7 | HTTP 200 - task configured |
| 4 | Poll waterfall for `task_1` until data received (status 201) | Data received from task_1 |
| 5 | Poll waterfall for `task_2` until data received (status 201) | Data received from task_2 |
| 6 | Compare number of data blocks: `len(data_1) == len(data_2)` | Same number of blocks |
| 7 | For each block, compare number of rows: `len(block1.rows) == len(block2.rows)` | Same row count |
| 8 | For each row, compare sensor count: `len(row1.sensors) == len(row2.sensors)` | Same sensor count (should be 1 for SingleChannel) |
| 9 | Poll `task_1` multiple times (5 times) | Multiple data batches |
| 10 | Verify sensor count is consistent across all polls | All polls return same sensor structure |
| 11 | Query metadata for both tasks: `GET /metadata/{task_id}` | Metadata retrieved |
| 12 | Compare metadata fields: channel, view_type, nfft, frequency range | All metadata matches |

## Expected Result
* **Same channel** returns **same data structure**
* Number of sensors is **consistent** (=1 for SingleChannel)
* Data structure **identical** across:
  - Different tasks with same config
  - Multiple polls of same task
* Metadata is **consistent** with configuration
* No random variations in structure
* Deterministic behavior

## Post-Conditions
* Tasks can be cleaned up
* Data consistency validated
* System proven reliable

## Environment
**Same as PZ-13879** (new_production environment)

## Automation Status

✅ **Automated**

**Test Function**: `test_singlechannel_data_consistency_same_channel`, `test_singlechannel_data_consistency_polling`, `test_singlechannel_metadata_consistency`  
**Test File**: `tests/integration/api/test_singlechannel_high_priority.py`  
**Test Class**: `TestSingleChannelDataConsistency`  
**Lines**: 50-208

**Run Command**:
```bash
pytest tests/integration/api/test_singlechannel_high_priority.py::TestSingleChannelDataConsistency -v
```

**Expected Test Duration**: ~10-20 seconds

---

# TEST 10: PZ-13852

## Test ID
**PZ-13852**

## Summary
SingleChannel - Invalid Channel ID

## Objective
Validates proper error handling when configuring SingleChannel with **invalid or non-existent channel IDs**. This includes negative channel IDs, very large channel IDs beyond system capacity, and wrong data types (strings instead of integers). Proper validation prevents undefined behavior and system crashes.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `singlechannel`, `validation`, `negative-test`, `error-handling`
* **Test Type**: Integration Test (Negative)

## Requirements
* **Requirement ID**: FOCUS-API-SINGLECHANNEL-VALIDATION-001
* **Description**: Server must validate channel IDs and reject invalid values

## Pre-Conditions
1. Focus Server is running
2. System has finite number of channels (e.g., 0-200)
3. Channel validation is implemented
4. System knows valid channel range

## Test Data

### Test Data 1: Non-existent Channel (Very High ID)
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {
    "min": 9999,
    "max": 9999
  },
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 1
}
```
**Note**: Channel 9999 likely doesn't exist

### Test Data 2: Negative Channel ID
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {
    "min": -1,
    "max": -1
  },
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 1
}
```
**Note**: Negative channel ID is invalid

### Test Data 3: String Channel ID (Type Error)
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {
    "min": "invalid",
    "max": "invalid"
  },
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 1
}
```
**Note**: String instead of integer

### Test Data 4: Out-of-Bounds Channel
First query system for max channel: `GET /channels` → extract max ID → use `max_id + 100`

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Query `GET /channels` to determine valid channel range | List of valid channels |
| 2 | Extract maximum channel ID from response | `max_channel_id` (e.g., 200) |
| 3 | Generate `task_id` for test 1 | Valid task_id |
| 4 | Create config with channel_id=9999 (Test Data 1) | Payload created |
| 5 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | HTTP 400 or 404 |
| 6 | Verify error: `"Channel 9999 does not exist"` or similar | Descriptive error |
| 7 | Create config with channel_id=-1 (Test Data 2) | Payload created |
| 8 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | HTTP 400 |
| 9 | Verify error: `"Channel ID must be non-negative"` | Clear error |
| 10 | Attempt to create config with channel_id="invalid" (Test Data 3) | Type validation error OR payload creation fails |
| 11 | If payload created, send request | HTTP 400 or type error |
| 12 | Create config with channel_id = `max_channel_id + 100` (Test Data 4) | Payload created |
| 13 | Send request | HTTP 400 or 404 |
| 14 | Verify error indicates valid range: `"Valid channels: 0-{max_channel_id}"` | Range shown in error |

## Expected Result
* **Non-existent channel ID (9999)** is **rejected** with 400/404
* **Negative channel ID (-1)** is **rejected** with 400
* **String channel ID** is caught by type validation
* **Out-of-bounds channel** is **rejected** with descriptive error
* Error messages indicate:
  - Invalid channel ID provided
  - Valid channel range
* No tasks created for invalid channels
* System remains stable (no crashes)

## Post-Conditions
* No orphaned tasks
* Server stable
* Clear error logging

## Environment
**Same as PZ-13879** (new_production environment)

## Automation Status

✅ **Automated**

**Test Function**: `test_singlechannel_non_existent_channel_id`, `test_singlechannel_negative_channel_id`, `test_singlechannel_string_channel_id`, `test_singlechannel_out_of_bounds_channel_id`  
**Test File**: `tests/integration/api/test_singlechannel_high_priority.py`  
**Test Class**: `TestSingleChannelInvalidID`  
**Lines**: 211-381

**Run Command**:
```bash
pytest tests/integration/api/test_singlechannel_high_priority.py::TestSingleChannelInvalidID -v
```

**Expected Test Duration**: ~5-10 seconds

---

# TEST 11: PZ-13770

## Test ID
**PZ-13770**

## Summary
Performance – /config Latency P95/P99

## Objective
Measures and validates **P95 and P99 latency** for the critical `POST /config/{task_id}` endpoint. This performance test ensures that the configuration endpoint responds within acceptable time limits under normal load. P95 (95th percentile) and P99 (99th percentile) metrics are industry-standard SLA indicators.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `performance`, `latency`, `p95`, `p99`, `sla`, `load-test`
* **Test Type**: Performance Test

## Requirements
* **Requirement ID**: FOCUS-API-PERFORMANCE-001
* **Description**: Configuration endpoint must meet P95/P99 latency SLAs

## Pre-Conditions
1. Focus Server is running under normal load (not stressed)
2. System resources are available (CPU < 80%, Memory < 85%)
3. MongoDB and RabbitMQ are responsive
4. No other heavy tests running concurrently

## Test Data

**Standard Configuration Payload** (repeated 100 times):
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```
**Note**: Same config used for all 100 requests (different task_ids)

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Prepare test: 100 unique task_ids | 100 task_ids generated |
| 2 | Clear any previous test data | System clean |
| 3 | For i=1 to 100: Record start time `t_start[i]` | Time recorded |
| 4 | Send `POST https://10.10.100.100/focus-server/config/{task_id[i]}` with payload | Request sent |
| 5 | Record end time `t_end[i]` | Time recorded |
| 6 | Calculate latency: `latency[i] = (t_end[i] - t_start[i]) * 1000` ms | Latency in milliseconds |
| 7 | Verify response status: 200 OK or "Config received successfully" | Success confirmed |
| 8 | Add 100ms delay every 10 requests to avoid overwhelming server | Controlled load |
| 9 | After all 100 requests, sort latencies | Latencies sorted |
| 10 | Calculate P50 (median): `latency[50]` | P50 value |
| 11 | Calculate P95: `latency[95]` | P95 value |
| 12 | Calculate P99: `latency[99]` | P99 value |
| 13 | Calculate min, max, average | Statistical summary |
| 14 | Count errors/failures | Error count |
| 15 | Verify P95 < **[THRESHOLD]** ms (need specs!) | P95 within SLA |
| 16 | Verify P99 < **[THRESHOLD]** ms (need specs!) | P99 within SLA |

## Expected Result
* **100 requests** executed successfully
* **P50 (median)** latency: < 200ms (target)
* **P95 latency**: < **[THRESHOLD]** ms (e.g., 500ms - **needs specs meeting**)
* **P99 latency**: < **[THRESHOLD]** ms (e.g., 1000ms - **needs specs meeting**)
* **Error rate**: < 5% (95% success rate minimum)
* **No timeouts** or crashes
* System remains stable throughout test

**Current Thresholds** (to be updated after specs meeting):
- P95: 500ms (reasonable default)
- P99: 1000ms (reasonable default)

## Post-Conditions
* Test tasks can be cleaned up
* Performance metrics logged
* System resources return to normal
* No degradation in subsequent requests

## Environment
**Same as PZ-13879** (new_production environment)

## Automation Status

✅ **Automated**

**Test Function**: `test_config_endpoint_latency_p95_p99`, `test_waterfall_endpoint_latency_p95`  
**Test File**: `tests/integration/performance/test_performance_high_priority.py`  
**Test Class**: `TestAPILatencyP95`  
**Lines**: 53-195

**Run Command**:
```bash
# Run performance tests (slow)
pytest tests/integration/performance/test_performance_high_priority.py::TestAPILatencyP95 -v -s

# Generate performance report
pytest tests/integration/performance/test_performance_high_priority.py::TestAPILatencyP95::test_config_endpoint_latency_p95_p99 \
  --junitxml=results/performance_p95.xml \
  --html=results/performance_p95.html
```

**Expected Test Duration**: ~60-90 seconds (100 requests with delays)

---

# TEST 12: PZ-13771

## Test ID
**PZ-13771**

## Summary
Performance – Concurrent Task Limit

## Objective
Determines the **maximum number of concurrent tasks** the system can handle reliably. This test validates system capacity under parallel load and identifies breaking points. Understanding concurrent task limits is critical for capacity planning and preventing system overload in production.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `performance`, `concurrency`, `load-test`, `capacity`, `stress-test`
* **Test Type**: Performance Test (Load/Stress)

## Requirements
* **Requirement ID**: FOCUS-API-CONCURRENCY-001
* **Description**: System must support minimum number of concurrent tasks without degradation

## Pre-Conditions
1. Focus Server is running with adequate resources
2. System is under normal load (baseline)
3. MongoDB can handle concurrent connections
4. RabbitMQ can handle concurrent messages
5. No resource limits (file descriptors, connections) hit

## Test Data

**Standard Configuration** (used for all concurrent tasks):
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```

**Test Scenarios**:
- Scenario 1: 10 concurrent tasks
- Scenario 2: 20 concurrent tasks
- Scenario 3: 30 concurrent tasks
- Scenario 4: 40 concurrent tasks
- Scenario 5: 50 concurrent tasks (if previous succeed)

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Start with 10 concurrent tasks | Test count = 10 |
| 2 | Create ThreadPoolExecutor with 10 workers | Executor ready |
| 3 | Generate 10 unique task_ids | 10 task_ids created |
| 4 | Submit 10 config requests in parallel (non-blocking) | All submitted |
| 5 | Wait for all requests to complete | All futures resolved |
| 6 | Count successes (status 200) and failures | Success count recorded |
| 7 | Calculate success rate: `successes / total * 100%` | Success rate % |
| 8 | Calculate average latency for successful requests | Avg latency recorded |
| 9 | If success rate >= 90%, proceed to 20 concurrent tasks | Move to next level |
| 10 | Repeat steps 2-8 for 20, 30, 40, 50 tasks | Test increasing loads |
| 11 | Stop when success rate drops below 80% | Breaking point identified |
| 12 | Poll all successful tasks to verify they're operational | All tasks can be queried |
| 13 | Monitor system resources (CPU, Memory) during test | Resources within limits |
| 14 | Document maximum reliable concurrent task count | Max capacity recorded |

## Expected Result
* System **successfully handles** at least **[MIN_CONCURRENT]** tasks (e.g., 10 - **needs specs meeting**)
* **Success rate >= 90%** for all tests up to capacity limit
* **Graceful degradation** when limit exceeded:
  - No crashes or hangs
  - Clear error messages (e.g., "System at capacity")
  - No resource exhaustion
* **All successful tasks** remain operational and queryable
* System **recovers** after load removed

**Findings to Document**:
- Maximum concurrent tasks with 90%+ success
- Maximum concurrent tasks with 80%+ success
- Breaking point (where failures exceed 20%)
- Resource bottleneck (CPU/Memory/Connections)

## Post-Conditions
* All test tasks cleaned up
* System resources released
* System returns to stable state
* Performance metrics logged for capacity planning

## Environment
**Same as PZ-13879** (new_production environment)

## Automation Status

✅ **Automated**

**Test Function**: `test_concurrent_task_creation`, `test_concurrent_task_polling`, `test_concurrent_task_max_limit`  
**Test File**: `tests/integration/performance/test_performance_high_priority.py`  
**Test Class**: `TestConcurrentTaskLimit`  
**Lines**: 198-421

**Run Command**:
```bash
# Run concurrency tests (can be slow and resource-intensive)
pytest tests/integration/performance/test_performance_high_priority.py::TestConcurrentTaskLimit -v -s

# Run with resource monitoring
pytest tests/integration/performance/test_performance_high_priority.py::TestConcurrentTaskLimit::test_concurrent_task_max_limit -v -s
```

**Expected Test Duration**: ~2-5 minutes (depending on capacity)

**⚠️ Warning**: This is a stress test that may temporarily impact system performance. Run during maintenance window or on test environment.

---

## 📊 Summary - All 10 High Priority Tests

| Test ID | Summary | Priority | Automation | Duration |
|---------|---------|----------|-----------|----------|
| **PZ-13879** | Missing Required Fields | High | ✅ Automated | ~2-3s |
| **PZ-13878** | Invalid View Type | High | ✅ Automated | ~1-2s |
| **PZ-13877** | Invalid Frequency Range | High | ✅ Automated | ~1s |
| **PZ-13876** | Invalid Channel Range | High | ✅ Automated | ~1s |
| **PZ-13873** | Valid Configuration | High | ✅ Automated | ~3-5s |
| **PZ-13419** | GET /channels | High | ✅ Automated | ~2-3s |
| **PZ-13868** | Historic Status 208 | High | ✅ Automated | ~30-60s |
| **PZ-13871** | Timestamp Ordering | High | ✅ Automated | ~20-40s |
| **PZ-13853** | SingleChannel Consistency | High | ✅ Automated | ~10-20s |
| **PZ-13852** | Invalid Channel ID | High | ✅ Automated | ~5-10s |
| **PZ-13770** | Performance P95/P99 | High | ✅ Automated | ~60-90s |
| **PZ-13771** | Concurrent Tasks | High | ✅ Automated | ~2-5min |

**Total Tests**: 12 test IDs (10 unique Xray stories)  
**Total Test Functions**: 42 automated tests  
**Total Estimated Duration**: ~5-10 minutes for full suite

---

## ⚠️ Important Notes - Specs Needed

The following tests have **TODO thresholds** that need confirmation from specs meeting:

1. **PZ-13770** (Performance P95/P99):
   - Current default: P95 < 500ms, P99 < 1000ms
   - **Need**: Actual SLA requirements

2. **PZ-13771** (Concurrent Tasks):
   - Current default: Minimum 10 concurrent tasks
   - **Need**: Actual capacity requirements

3. **PZ-13871** (Timestamp Gaps):
   - Current: 0.0001s < gap < 10s
   - **Need**: Actual acceptable gap ranges

4. **PZ-13419** (Channels Response Time):
   - Current: < 1000ms
   - **Need**: Actual response time SLA

---

**Document Complete** ✅  
**All 10 High Priority Xray Tests Documented**  
**Format**: Full Xray specification without embedded Python code  
**Ready for**: Import to Jira Xray

