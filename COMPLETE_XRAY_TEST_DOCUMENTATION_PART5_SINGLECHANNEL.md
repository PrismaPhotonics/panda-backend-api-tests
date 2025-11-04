# 📋 Complete Xray Test Documentation - Part 5: SingleChannel Tests (15 Tests)

**Generated:** 2025-10-20  
**Category:** SingleChannel View Type (view_type=1)  
**Total Tests:** 15  
**Source File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

## TC-SINGLECHANNEL-001: SingleChannel View Mapping (Channel 7)

**Summary:** API – SingleChannel View Returns Correct 1:1 Mapping

**Objective:** Validate that view_type=SINGLECHANNEL returns exactly one stream with correct 1:1 channel-to-stream mapping for the requested channel.

**Priority:** High

**Components/Labels:** focus-server, api, view-type, singlechannel, mapping

**Requirements:** FOCUS-API-VIEWTYPE, FOCUS-SINGLECHANNEL

**Pre-Conditions:**
- PC-001: Focus Server API accessible
- PC-002: /configure endpoint available
- PC-003: view_type=1 (SINGLECHANNEL) supported

**Test Data:**
```json
POST /configure
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 7, "max": 7},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 1
}

Expected Response:
{
  "job_id": "string",
  "stream_amount": 1,
  "stream_port": "integer",
  "stream_url": "string",
  "channel_to_stream_index": {"7": 0},
  "channel_amount": 1,
  "frequencies_list": [...],
  "frequencies_amount": "integer",
  "lines_dt": "number",
  "status": "string",
  "view_type": 1
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Create ConfigureRequest | view_type=1, channels={min:7,max:7} | Request created |
| 2 | POST /configure | Request payload | HTTP 200 OK |
| 3 | Validate response schema | - | Valid ConfigureResponse |
| 4 | Check stream_amount | response.stream_amount | == 1 |
| 5 | Check channel_to_stream_index size | len(mapping) | == 1 |
| 6 | Verify mapping entry | mapping["7"] | == 0 |
| 7 | Check channel_amount | response.channel_amount | == 1 |
| 8 | Verify no extra channels | - | Only channel 7 |
| 9 | Validate view_type | response.view_type | == 1 |

**Expected Result (overall):**
- Configuration accepted (HTTP 200)
- Exactly one stream created (stream_amount=1)
- Single mapping: channel "7" → stream index 0
- No extraneous channels in mapping
- view_type returned as 1 (SINGLECHANNEL)

**Post-Conditions:**
- Job created with correct configuration
- Baby Analyzer initialized for single channel

**Assertions:**
```python
from src.models.focus_server_models import ConfigureRequest, ConfigureResponse, ViewType

# Create request
config_request = ConfigureRequest(
    displayTimeAxisDuration=10,
    nfftSelection=1024,
    displayInfo={"height": 1000},
    channels={"min": 7, "max": 7},  # Single channel
    frequencyRange={"min": 0, "max": 500},
    start_time=None,
    end_time=None,
    view_type=ViewType.SINGLECHANNEL  # view_type = 1
)

# Send request
response = focus_server_api.configure(config_request)

# Validate response
assert isinstance(response, ConfigureResponse)
assert response.stream_amount == 1, f"Expected 1 stream, got {response.stream_amount}"

# Validate mapping
channel_mapping = response.channel_to_stream_index
assert len(channel_mapping) == 1, f"Expected 1 mapping, got {len(channel_mapping)}"
assert "7" in channel_mapping, "Channel 7 not in mapping"
assert channel_mapping["7"] == 0, f"Expected stream 0, got {channel_mapping['7']}"

# Validate channel amount
assert response.channel_amount == 1, f"Expected 1 channel, got {response.channel_amount}"

# Validate view type
assert response.view_type == 1, f"Expected view_type=1, got {response.view_type}"

logger.info("✅ SingleChannel mapping correct for channel 7")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_configure_singlechannel_mapping`  
**Test File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

## TC-SINGLECHANNEL-002: SingleChannel View – Channel 1 (Lower Boundary)

**Summary:** API – SingleChannel View for Channel 1 (First Channel)

**Objective:** Verify SingleChannel view works correctly for channel 1 (lower boundary test).

**Priority:** Medium

**Components/Labels:** focus-server, singlechannel, boundary-test

**Requirements:** FOCUS-SINGLECHANNEL-BOUNDARY

**Pre-Conditions:**
- PC-001: Focus Server API accessible
- PC-002: Channel 1 valid (first channel)

**Test Data:**
```json
POST /configure
{
  "channels": {"min": 1, "max": 1},
  "view_type": 1,
  ...
}

Expected:
{
  "stream_amount": 1,
  "channel_to_stream_index": {"1": 0},
  "channel_amount": 1
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Create request | channel 1 | Request created |
| 2 | POST /configure | - | HTTP 200 |
| 3 | Validate stream_amount | - | == 1 |
| 4 | Validate mapping | - | {"1": 0} |
| 5 | Check no errors | - | Success |

**Expected Result (overall):**
- Channel 1 works as SingleChannel
- Correct mapping returned
- No boundary errors

**Post-Conditions:**
- Job created for channel 1

**Assertions:**
```python
config_request = ConfigureRequest(
    displayTimeAxisDuration=10,
    nfftSelection=1024,
    displayInfo={"height": 1000},
    channels={"min": 1, "max": 1},  # Channel 1 (lower boundary)
    frequencyRange={"min": 0, "max": 500},
    view_type=ViewType.SINGLECHANNEL
)

response = focus_server_api.configure(config_request)

assert response.stream_amount == 1
assert len(response.channel_to_stream_index) == 1
assert "1" in response.channel_to_stream_index
assert response.channel_to_stream_index["1"] == 0

logger.info("✅ SingleChannel works for channel 1 (lower boundary)")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_configure_singlechannel_channel_1`  
**Test File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

## TC-SINGLECHANNEL-003: SingleChannel View – Channel 100 (Upper Boundary)

**Summary:** API – SingleChannel View for Channel 100 (Upper Boundary Test)

**Objective:** Verify SingleChannel view works correctly for channel 100 (upper boundary or high channel number).

**Priority:** Medium

**Components/Labels:** focus-server, singlechannel, boundary-test

**Requirements:** FOCUS-SINGLECHANNEL-BOUNDARY

**Pre-Conditions:**
- PC-001: Focus Server supports channel 100
- PC-002: Max channels >= 100

**Test Data:**
```json
POST /configure
{
  "channels": {"min": 100, "max": 100},
  "view_type": 1,
  ...
}

Expected:
{
  "stream_amount": 1,
  "channel_to_stream_index": {"100": 0}
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Create request | channel 100 | Request created |
| 2 | POST /configure | - | HTTP 200 |
| 3 | Validate mapping | - | {"100": 0} |
| 4 | Verify no overflow | - | Success |

**Expected Result (overall):**
- Channel 100 works correctly
- No overflow or boundary errors
- Correct mapping

**Post-Conditions:**
- Job created for channel 100

**Assertions:**
```python
config_request = ConfigureRequest(
    displayTimeAxisDuration=10,
    nfftSelection=1024,
    displayInfo={"height": 1000},
    channels={"min": 100, "max": 100},  # Channel 100 (upper boundary)
    frequencyRange={"min": 0, "max": 500},
    view_type=ViewType.SINGLECHANNEL
)

response = focus_server_api.configure(config_request)

assert response.stream_amount == 1
assert "100" in response.channel_to_stream_index
assert response.channel_to_stream_index["100"] == 0

logger.info("✅ SingleChannel works for channel 100 (upper boundary)")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_configure_singlechannel_channel_100`  
**Test File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

## TC-SINGLECHANNEL-004: Different Channels Different Mappings

**Summary:** API – Different SingleChannels Return Different Mappings

**Objective:** Verify that requesting different single channels returns distinct channel_to_stream_index entries.

**Priority:** High

**Components/Labels:** focus-server, singlechannel, mapping-consistency

**Requirements:** FOCUS-SINGLECHANNEL-CONSISTENCY

**Pre-Conditions:**
- PC-001: Focus Server API accessible

**Test Data:**
```json
Test 1: {"channels": {"min": 5, "max": 5}}
Test 2: {"channels": {"min": 10, "max": 10}}
Test 3: {"channels": {"min": 50, "max": 50}}

Expected:
- Test 1: {"5": 0}
- Test 2: {"10": 0}
- Test 3: {"50": 0}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Configure channel 5 | min=max=5 | mapping={"5": 0} |
| 2 | Configure channel 10 | min=max=10 | mapping={"10": 0} |
| 3 | Configure channel 50 | min=max=50 | mapping={"50": 0} |
| 4 | Compare mappings | - | All different channels |
| 5 | Verify consistency | - | All map to stream 0 |

**Expected Result (overall):**
- Each channel gets correct mapping
- Channel key differs in each response
- Stream index always 0 for SingleChannel

**Post-Conditions:**
- Multiple jobs created

**Assertions:**
```python
test_channels = [5, 10, 50]
mappings = []

for channel in test_channels:
    config_request = ConfigureRequest(
        displayTimeAxisDuration=10,
        nfftSelection=1024,
        displayInfo={"height": 1000},
        channels={"min": channel, "max": channel},
        frequencyRange={"min": 0, "max": 500},
        view_type=ViewType.SINGLECHANNEL
    )
    
    response = focus_server_api.configure(config_request)
    
    assert str(channel) in response.channel_to_stream_index
    assert response.channel_to_stream_index[str(channel)] == 0
    
    mappings.append(response.channel_to_stream_index)
    logger.info(f"Channel {channel}: mapping = {response.channel_to_stream_index}")

# Verify all mappings are different (different channel keys)
assert len(set(str(m) for m in mappings)) == len(mappings)

logger.info("✅ Different channels return different mappings")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_different_channels_different_mappings`  
**Test File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

## TC-SINGLECHANNEL-005: Same Channel Consistent Mapping

**Summary:** API – Same SingleChannel Returns Consistent Mapping Across Multiple Requests

**Objective:** Verify that requesting the same single channel multiple times returns consistent mapping.

**Priority:** High

**Components/Labels:** focus-server, singlechannel, consistency, idempotency

**Requirements:** FOCUS-SINGLECHANNEL-IDEMPOTENCY

**Pre-Conditions:**
- PC-001: Focus Server API accessible

**Test Data:**
```json
Request (repeated 3 times):
{
  "channels": {"min": 25, "max": 25},
  "view_type": 1
}

Expected: All 3 responses identical mapping:
{"25": 0}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Configure channel 25 (1st) | - | mapping={"25": 0} |
| 2 | Configure channel 25 (2nd) | - | mapping={"25": 0} |
| 3 | Configure channel 25 (3rd) | - | mapping={"25": 0} |
| 4 | Compare all mappings | - | All identical |
| 5 | Verify consistency | - | Passed |

**Expected Result (overall):**
- All 3 requests return same mapping
- Consistent behavior across calls
- No randomness or drift

**Post-Conditions:**
- 3 jobs created (may be different job_ids)

**Assertions:**
```python
channel = 25
mappings = []

for i in range(3):
    config_request = ConfigureRequest(
        displayTimeAxisDuration=10,
        nfftSelection=1024,
        displayInfo={"height": 1000},
        channels={"min": channel, "max": channel},
        frequencyRange={"min": 0, "max": 500},
        view_type=ViewType.SINGLECHANNEL
    )
    
    response = focus_server_api.configure(config_request)
    mapping = response.channel_to_stream_index
    
    assert str(channel) in mapping
    assert mapping[str(channel)] == 0
    
    mappings.append(mapping)
    logger.info(f"Request {i+1}: mapping = {mapping}")

# Verify all mappings are identical
for mapping in mappings:
    assert mapping == mappings[0], "Inconsistent mappings!"

logger.info("✅ Same channel returns consistent mapping")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_same_channel_multiple_requests_consistent_mapping`  
**Test File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

## TC-SINGLECHANNEL-006: SingleChannel vs MultiChannel Comparison

**Summary:** API – Compare SingleChannel vs MultiChannel View Types

**Objective:** Verify distinct behavior between view_type=SINGLECHANNEL (1) and view_type=MULTICHANNEL (0).

**Priority:** Medium

**Components/Labels:** focus-server, view-type, comparison

**Requirements:** FOCUS-VIEWTYPE-COMPARISON

**Pre-Conditions:**
- PC-001: Both view types supported

**Test Data:**
```json
MultiChannel Request:
{
  "channels": {"min": 1, "max": 10},
  "view_type": 0
}
Expected: stream_amount > 1, multiple mappings

SingleChannel Request:
{
  "channels": {"min": 5, "max": 5},
  "view_type": 1
}
Expected: stream_amount = 1, single mapping
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Configure MultiChannel | channels 1-10 | stream_amount > 1 |
| 2 | Count mappings | - | len(mapping) = 10 |
| 3 | Configure SingleChannel | channel 5 only | stream_amount = 1 |
| 4 | Count mappings | - | len(mapping) = 1 |
| 5 | Compare results | - | Clear difference |

**Expected Result (overall):**
- MultiChannel returns multiple streams
- SingleChannel returns one stream
- Mapping counts differ
- Behavior clearly distinct

**Post-Conditions:**
- Two jobs created with different configs

**Assertions:**
```python
# MultiChannel request
multi_request = ConfigureRequest(
    displayTimeAxisDuration=10,
    nfftSelection=1024,
    displayInfo={"height": 1000},
    channels={"min": 1, "max": 10},
    frequencyRange={"min": 0, "max": 500},
    view_type=0  # MULTICHANNEL
)

multi_response = focus_server_api.configure(multi_request)

assert multi_response.stream_amount > 1
assert len(multi_response.channel_to_stream_index) == 10

logger.info(f"MultiChannel: {multi_response.stream_amount} streams, {len(multi_response.channel_to_stream_index)} mappings")

# SingleChannel request
single_request = ConfigureRequest(
    displayTimeAxisDuration=10,
    nfftSelection=1024,
    displayInfo={"height": 1000},
    channels={"min": 5, "max": 5},
    frequencyRange={"min": 0, "max": 500},
    view_type=ViewType.SINGLECHANNEL
)

single_response = focus_server_api.configure(single_request)

assert single_response.stream_amount == 1
assert len(single_response.channel_to_stream_index) == 1

logger.info(f"SingleChannel: {single_response.stream_amount} stream, {len(single_response.channel_to_stream_index)} mapping")

# Verify difference
assert multi_response.stream_amount != single_response.stream_amount
assert len(multi_response.channel_to_stream_index) != len(single_response.channel_to_stream_index)

logger.info("✅ SingleChannel vs MultiChannel behavior distinct")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_singlechannel_vs_multichannel_comparison`  
**Test File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

## TC-SINGLECHANNEL-007: SingleChannel with Different Frequency Ranges

**Summary:** API – SingleChannel View with Various Frequency Ranges

**Objective:** Verify SingleChannel works with different frequency configurations.

**Priority:** Low

**Components/Labels:** focus-server, singlechannel, frequency

**Requirements:** FOCUS-SINGLECHANNEL-FREQUENCY

**Pre-Conditions:**
- PC-001: Various frequency ranges supported

**Test Data:**
```json
Test 1: {"frequencyRange": {"min": 0, "max": 500}}
Test 2: {"frequencyRange": {"min": 100, "max": 400}}
Test 3: {"frequencyRange": {"min": 0, "max": 1000}}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Configure with freq 0-500 | - | Success, mapping correct |
| 2 | Configure with freq 100-400 | - | Success, mapping correct |
| 3 | Configure with freq 0-1000 | - | Success, mapping correct |
| 4 | Verify all work | - | All pass |

**Expected Result (overall):**
- SingleChannel works with all frequency ranges
- Mapping always correct
- Frequency doesn't affect channel mapping

**Post-Conditions:**
- Multiple jobs created

**Assertions:**
```python
frequency_ranges = [
    (0, 500),
    (100, 400),
    (0, 1000)
]

channel = 10

for freq_min, freq_max in frequency_ranges:
    config_request = ConfigureRequest(
        displayTimeAxisDuration=10,
        nfftSelection=1024,
        displayInfo={"height": 1000},
        channels={"min": channel, "max": channel},
        frequencyRange={"min": freq_min, "max": freq_max},
        view_type=ViewType.SINGLECHANNEL
    )
    
    response = focus_server_api.configure(config_request)
    
    assert response.stream_amount == 1
    assert str(channel) in response.channel_to_stream_index
    assert response.channel_to_stream_index[str(channel)] == 0
    
    logger.info(f"✓ Freq [{freq_min},{freq_max}]: mapping correct")

logger.info("✅ SingleChannel works with different frequency ranges")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_singlechannel_with_different_frequency_ranges`  
**Test File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

## TC-SINGLECHANNEL-008: SingleChannel with Invalid Frequency Range

**Summary:** API – SingleChannel Rejects Invalid Frequency Range

**Objective:** Verify SingleChannel view rejects configurations with invalid frequency ranges (min > max).

**Priority:** Medium

**Components/Labels:** focus-server, singlechannel, validation, negative-test

**Requirements:** FOCUS-SINGLECHANNEL-VALIDATION

**Pre-Conditions:**
- PC-001: Validation enabled

**Test Data:**
```json
Invalid Request:
{
  "channels": {"min": 10, "max": 10},
  "frequencyRange": {"min": 500, "max": 0},  // Invalid: min > max
  "view_type": 1
}

Expected: HTTP 400 or validation error
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Create invalid request | freq min > max | Request created |
| 2 | POST /configure | - | HTTP 400 |
| 3 | Verify error message | - | "Invalid frequency range" |

**Expected Result (overall):**
- Request rejected with 400
- Clear error message
- No job created

**Post-Conditions:**
- No job created

**Assertions:**
```python
config_request = ConfigureRequest(
    displayTimeAxisDuration=10,
    nfftSelection=1024,
    displayInfo={"height": 1000},
    channels={"min": 10, "max": 10},
    frequencyRange={"min": 500, "max": 0},  # Invalid!
    view_type=ViewType.SINGLECHANNEL
)

try:
    response = focus_server_api.configure(config_request)
    assert False, "Should have rejected invalid frequency range"
except APIError as e:
    assert e.status_code == 400
    assert "frequency" in str(e).lower() or "invalid" in str(e).lower()
    logger.info(f"✓ Invalid frequency rejected: {e}")

logger.info("✅ SingleChannel rejects invalid frequency range")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_singlechannel_with_invalid_frequency_range`  
**Test File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

## TC-SINGLECHANNEL-009: SingleChannel with Invalid Height

**Summary:** API – SingleChannel Rejects Invalid Display Height

**Objective:** Verify SingleChannel rejects invalid display height (zero or negative).

**Priority:** Medium

**Components/Labels:** focus-server, singlechannel, validation, negative-test

**Requirements:** FOCUS-SINGLECHANNEL-VALIDATION

**Pre-Conditions:**
- PC-001: Validation enabled

**Test Data:**
```json
Invalid Request:
{
  "displayInfo": {"height": 0},  // Invalid height
  "channels": {"min": 10, "max": 10},
  "view_type": 1
}

Expected: HTTP 400
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Create request with height=0 | - | Request created |
| 2 | POST /configure | - | HTTP 400 |
| 3 | Verify error | - | "Invalid height" |

**Expected Result (overall):**
- Zero height rejected
- Clear error message

**Post-Conditions:**
- No job created

**Assertions:**
```python
config_request = ConfigureRequest(
    displayTimeAxisDuration=10,
    nfftSelection=1024,
    displayInfo={"height": 0},  # Invalid!
    channels={"min": 10, "max": 10},
    frequencyRange={"min": 0, "max": 500},
    view_type=ViewType.SINGLECHANNEL
)

try:
    response = focus_server_api.configure(config_request)
    assert False, "Should have rejected zero height"
except (APIError, PydanticValidationError) as e:
    logger.info(f"✓ Zero height rejected: {e}")

logger.info("✅ SingleChannel rejects invalid height")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_singlechannel_with_invalid_height`  
**Test File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

## TC-SINGLECHANNEL-010: SingleChannel with Invalid NFFT

**Summary:** API – SingleChannel Rejects Invalid NFFT Value

**Objective:** Verify SingleChannel rejects NFFT that is not power of 2.

**Priority:** Medium

**Components/Labels:** focus-server, singlechannel, validation, nfft

**Requirements:** FOCUS-NFFT-VALIDATION

**Pre-Conditions:**
- PC-001: NFFT validation enabled

**Test Data:**
```json
Invalid Request:
{
  "nfftSelection": 1000,  // Not power of 2
  "channels": {"min": 10, "max": 10},
  "view_type": 1
}

Expected: HTTP 400
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Create request with nfft=1000 | - | Request created |
| 2 | POST /configure | - | HTTP 400 |
| 3 | Verify error | - | "NFFT must be power of 2" |

**Expected Result (overall):**
- Non-power-of-2 NFFT rejected
- Clear error message

**Post-Conditions:**
- No job created

**Assertions:**
```python
config_request = ConfigureRequest(
    displayTimeAxisDuration=10,
    nfftSelection=1000,  # Not power of 2!
    displayInfo={"height": 1000},
    channels={"min": 10, "max": 10},
    frequencyRange={"min": 0, "max": 500},
    view_type=ViewType.SINGLECHANNEL
)

try:
    response = focus_server_api.configure(config_request)
    assert False, "Should have rejected non-power-of-2 NFFT"
except (APIError, PydanticValidationError) as e:
    logger.info(f"✓ Invalid NFFT rejected: {e}")

logger.info("✅ SingleChannel rejects invalid NFFT")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_singlechannel_with_invalid_nfft`  
**Test File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

## TC-SINGLECHANNEL-011: SingleChannel with Min Not Equal Max (Should Fail)

**Summary:** API – SingleChannel Rejects When min ≠ max

**Objective:** Verify that view_type=SINGLECHANNEL requires min=max in channels, and rejects min≠max.

**Priority:** Critical

**Components/Labels:** focus-server, singlechannel, validation, negative-test

**Requirements:** FOCUS-SINGLECHANNEL-VALIDATION

**Pre-Conditions:**
- PC-001: Validation enforces min=max for SINGLECHANNEL

**Test Data:**
```json
Invalid Request (min ≠ max):
{
  "channels": {"min": 5, "max": 10},  // Invalid for SINGLECHANNEL
  "view_type": 1
}

Expected: HTTP 400 or 422
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Create request | min=5, max=10, view_type=1 | Request created |
| 2 | POST /configure | - | HTTP 400 or 422 |
| 3 | Verify error | - | "SINGLECHANNEL requires min=max" |

**Expected Result (overall):**
- Request rejected
- Clear validation error
- No job created

**Post-Conditions:**
- No job created

**Assertions:**
```python
config_request = ConfigureRequest(
    displayTimeAxisDuration=10,
    nfftSelection=1024,
    displayInfo={"height": 1000},
    channels={"min": 5, "max": 10},  # Invalid for SINGLECHANNEL!
    frequencyRange={"min": 0, "max": 500},
    view_type=ViewType.SINGLECHANNEL
)

try:
    response = focus_server_api.configure(config_request)
    assert False, "Should have rejected min≠max for SINGLECHANNEL"
except APIError as e:
    assert e.status_code in [400, 422]
    logger.info(f"✓ min≠max rejected for SINGLECHANNEL: {e}")

logger.info("✅ SINGLECHANNEL correctly requires min=max")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_singlechannel_with_min_not_equal_max_should_fail`  
**Test File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

## TC-SINGLECHANNEL-012: SingleChannel with Zero Channel

**Summary:** API – SingleChannel Rejects Channel Zero

**Objective:** Verify that channel 0 is rejected (if channels start from 1).

**Priority:** Low

**Components/Labels:** focus-server, singlechannel, validation, boundary

**Requirements:** FOCUS-CHANNEL-VALIDATION

**Pre-Conditions:**
- PC-001: Channel numbering starts from 1

**Test Data:**
```json
Invalid Request:
{
  "channels": {"min": 0, "max": 0},  // Channel 0
  "view_type": 1
}

Expected: HTTP 400 (if channels start from 1)
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Create request with channel=0 | - | Request created |
| 2 | POST /configure | - | HTTP 400 or success |
| 3 | Verify behavior | - | Depends on system |

**Expected Result (overall):**
- If channels start from 1: rejected
- If channels start from 0: accepted
- Behavior documented

**Post-Conditions:**
- Depends on system configuration

**Assertions:**
```python
config_request = ConfigureRequest(
    displayTimeAxisDuration=10,
    nfftSelection=1024,
    displayInfo={"height": 1000},
    channels={"min": 0, "max": 0},  # Channel 0
    frequencyRange={"min": 0, "max": 500},
    view_type=ViewType.SINGLECHANNEL
)

try:
    response = focus_server_api.configure(config_request)
    # If accepted, channel 0 is valid
    logger.info("Channel 0 is valid (channels start from 0)")
    assert "0" in response.channel_to_stream_index
except APIError as e:
    # If rejected, channels start from 1
    logger.info("Channel 0 rejected (channels start from 1)")
    assert e.status_code == 400

logger.info("✅ Channel 0 behavior documented")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_singlechannel_with_zero_channel`  
**Test File:** `tests/integration/api/test_singlechannel_view_mapping.py`

---

Due to length limits, I'll create the remaining 3 SingleChannel tests plus all Historic Playback tests (10) in the next file.

**Progress: 62/75 tests complete (83%)**

Shall I continue?
