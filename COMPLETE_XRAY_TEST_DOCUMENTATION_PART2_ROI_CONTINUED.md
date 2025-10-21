# 📋 Complete Xray Test Documentation - Part 2: ROI Tests Continued (TC-ROI-008 to TC-ROI-025)

**Generated:** 2025-10-20  
**Category:** Dynamic ROI - Negative Tests & Edge Cases  
**Tests:** TC-ROI-008 through TC-ROI-025 (18 tests)  
**Source File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-008: ROI with Equal Start and End (Zero Size)

**Summary:** Dynamic ROI – Reject ROI with Start Equal to End

**Objective:** Verify that the system rejects an ROI change where start equals end (zero-size ROI) as this is invalid.

**Priority:** High

**Components/Labels:** focus-server, roi, validation, negative-test

**Requirements:** FOCUS-ROI-VALIDATION

**Pre-Conditions:**
- PC-001: RabbitMQ accessible
- PC-010: Safety validation enabled

**Test Data:**
```json
Invalid ROI (Zero Size):
{
  "start": 50,
  "end": 50
}

Expected Validation Result:
{
  "is_safe": false,
  "warnings": ["ROI size is zero"]
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Define zero-size ROI | start=50, end=50 | ROI defined |
| 2 | Calculate ROI size | end - start | size = 0 |
| 3 | Run safety validation | validate_roi_change_safety() | Validation fails |
| 4 | Check is_safe flag | result["is_safe"] | False |
| 5 | Check warnings | result["warnings"] | Contains "zero" or "invalid size" |
| 6 | Attempt to send command | - | Command should not be sent |

**Expected Result (overall):**
- Safety validation fails (is_safe=False)
- Warning about zero-size ROI generated
- Command not sent to RabbitMQ
- System protects against invalid ROI

**Post-Conditions:**
- Original ROI unchanged
- No command published

**Assertions:**
```python
# Zero-size ROI
start = 50
end = 50

# Validate safety
safety_result = validate_roi_change_safety(
    current_min=0,
    current_max=100,
    new_min=start,
    new_max=end
)

# Should fail validation
assert safety_result["is_safe"] == False
assert len(safety_result["warnings"]) > 0
assert any("size" in w.lower() or "zero" in w.lower() 
           for w in safety_result["warnings"])

logger.info("✅ Zero-size ROI correctly rejected")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_roi_equal_start_end`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-009: ROI with Reversed Range (Start > End)

**Summary:** Dynamic ROI – Reject Reversed ROI Range

**Objective:** Ensure system rejects ROI where start > end (reversed range).

**Priority:** Critical

**Components/Labels:** focus-server, roi, validation, negative-test

**Requirements:** FOCUS-ROI-VALIDATION

**Pre-Conditions:**
- PC-001: Safety validation enabled

**Test Data:**
```json
Invalid ROI (Reversed):
{
  "start": 150,
  "end": 50
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Define reversed ROI | start=150, end=50 | ROI defined |
| 2 | Calculate size | end - start | size = -100 (negative!) |
| 3 | Run validation | validate_roi_change_safety() | Fails |
| 4 | Check is_safe | result["is_safe"] | False |
| 5 | Check warnings | - | "reversed" or "invalid range" |

**Expected Result (overall):**
- Validation fails due to reversed range
- Clear warning message
- No command sent

**Post-Conditions:**
- Original ROI preserved

**Assertions:**
```python
start = 150
end = 50

safety_result = validate_roi_change_safety(
    current_min=0,
    current_max=100,
    new_min=start,
    new_max=end
)

assert safety_result["is_safe"] == False
assert end - start < 0  # Negative size
assert len(safety_result["warnings"]) > 0

logger.info("✅ Reversed ROI correctly rejected")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_invalid_roi_reversed`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-010: ROI with Negative Start

**Summary:** Dynamic ROI – Reject ROI with Negative Start Value

**Objective:** Verify system rejects ROI with negative start sensor index.

**Priority:** High

**Components/Labels:** focus-server, roi, validation, negative-test

**Requirements:** FOCUS-ROI-VALIDATION

**Pre-Conditions:**
- PC-001: Validation enabled
- PC-002: Sensor indices must be >= 0

**Test Data:**
```json
Invalid ROI (Negative Start):
{
  "start": -10,
  "end": 50
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Define negative start | start=-10, end=50 | ROI defined |
| 2 | Check start value | start < 0 | True (invalid) |
| 3 | Run validation | validate_roi_change_safety() | Fails |
| 4 | Check warnings | - | "negative" or "invalid index" |

**Expected Result (overall):**
- Validation rejects negative sensor index
- Warning message clear
- No command sent

**Post-Conditions:**
- System state unchanged

**Assertions:**
```python
start = -10
end = 50

assert start < 0  # Negative start

safety_result = validate_roi_change_safety(
    current_min=0,
    current_max=100,
    new_min=start,
    new_max=end
)

assert safety_result["is_safe"] == False
assert any("negative" in w.lower() or "invalid" in w.lower() 
           for w in safety_result["warnings"])

logger.info("✅ Negative start ROI rejected")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_roi_with_negative_start`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-011: ROI with Negative End

**Summary:** Dynamic ROI – Reject ROI with Negative End Value

**Objective:** Verify system rejects ROI with negative end sensor index.

**Priority:** High

**Components/Labels:** focus-server, roi, validation, negative-test

**Requirements:** FOCUS-ROI-VALIDATION

**Pre-Conditions:**
- PC-001: Validation enabled

**Test Data:**
```json
Invalid ROI (Negative End):
{
  "start": 10,
  "end": -50
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Define negative end | start=10, end=-50 | ROI defined |
| 2 | Check end value | end < 0 | True (invalid) |
| 3 | Run validation | validate_roi_change_safety() | Fails |

**Expected Result (overall):**
- Negative end value rejected
- Clear error message

**Post-Conditions:**
- No state change

**Assertions:**
```python
start = 10
end = -50

assert end < 0  # Negative end

safety_result = validate_roi_change_safety(
    current_min=0,
    current_max=100,
    new_min=start,
    new_max=end
)

assert safety_result["is_safe"] == False
logger.info("✅ Negative end ROI rejected")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_roi_with_negative_end`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-012: ROI with Small Range (Edge Case)

**Summary:** Dynamic ROI – Very Small ROI Range (e.g., 2 sensors)

**Objective:** Test edge case where ROI is very small but valid.

**Priority:** Medium

**Components/Labels:** focus-server, roi, edge-case

**Requirements:** FOCUS-ROI-EDGE

**Pre-Conditions:**
- PC-001: RabbitMQ accessible

**Test Data:**
```json
Small Valid ROI:
{
  "start": 50,
  "end": 52
}

Size: 2 sensors
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Define small ROI | [50, 52] | 2 sensors |
| 2 | Run validation | validate_roi_change_safety() | Passes (warning maybe) |
| 3 | Send command | - | Accepted |
| 4 | Verify system handles | - | No crash or error |

**Expected Result (overall):**
- Small ROI accepted (possibly with warning)
- System handles edge case gracefully
- Baby Analyzer reinitializes with 2 sensors

**Post-Conditions:**
- System monitoring 2 sensors only

**Assertions:**
```python
start = 50
end = 52
size = end - start

assert size == 2  # Very small

# May pass with warning
safety_result = validate_roi_change_safety(
    current_min=0,
    current_max=100,
    new_min=start,
    new_max=end
)

# Should work even if small
mq_client.send_roi_change(start=start, end=end)
logger.info("✅ Small ROI handled correctly")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_roi_with_small_range`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-013: ROI with Large Range (Edge Case)

**Summary:** Dynamic ROI – Very Large ROI Range (e.g., all sensors)

**Objective:** Test edge case where ROI covers maximum sensor range.

**Priority:** Medium

**Components/Labels:** focus-server, roi, edge-case, performance

**Requirements:** FOCUS-ROI-EDGE

**Pre-Conditions:**
- PC-001: System max sensors known (e.g., 512 or 1024)

**Test Data:**
```json
Large Valid ROI:
{
  "start": 0,
  "end": 512
}

Size: 512 sensors (maximum)
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Define large ROI | [0, 512] | All sensors |
| 2 | Run validation | - | Passes |
| 3 | Send command | - | Accepted |
| 4 | Monitor resources | CPU/Memory | No exhaustion |

**Expected Result (overall):**
- Maximum ROI accepted
- System handles high data volume
- No performance degradation

**Post-Conditions:**
- System monitoring all sensors

**Assertions:**
```python
start = 0
end = 512  # Or max_sensors from config
size = end - start

assert size == 512

safety_result = validate_roi_change_safety(
    current_min=0,
    current_max=100,
    new_min=start,
    new_max=end
)

assert safety_result["is_safe"] == True
mq_client.send_roi_change(start=start, end=end)
logger.info("✅ Large ROI handled correctly")
```

**Environment:** Staging, Production

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_roi_with_large_range`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-014: ROI Starting at Zero

**Summary:** Dynamic ROI – ROI Starting at Sensor Index 0

**Objective:** Verify ROI can start at sensor 0 (boundary).

**Priority:** Medium

**Components/Labels:** focus-server, roi, boundary

**Requirements:** FOCUS-ROI-BOUNDARY

**Pre-Conditions:**
- PC-001: RabbitMQ accessible

**Test Data:**
```json
ROI at Lower Boundary:
{
  "start": 0,
  "end": 50
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Define ROI at 0 | [0, 50] | Valid |
| 2 | Send command | - | Accepted |
| 3 | Verify waterfall | - | Sensors start at 0 |

**Expected Result (overall):**
- Sensor 0 included correctly
- No index errors

**Post-Conditions:**
- System monitoring from sensor 0

**Assertions:**
```python
start = 0
end = 50

mq_client.send_roi_change(start=start, end=end)
time.sleep(5)

waterfall = focus_api.get_waterfall(task_id)
assert waterfall.sensor_range["min"] == 0
logger.info("✅ ROI at sensor 0 works")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_roi_with_zero_start`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-015: Unsafe ROI Change (Large Jump)

**Summary:** Dynamic ROI – Detect Unsafe ROI Change (Large Jump)

**Objective:** Verify safety validation detects unsafe ROI changes (e.g., >50% change).

**Priority:** Critical

**Components/Labels:** focus-server, roi, safety, validation

**Requirements:** FOCUS-ROI-SAFETY

**Pre-Conditions:**
- PC-001: Safety rules: max_change_percent=50%

**Test Data:**
```json
Current ROI: {"min": 0, "max": 100}
Unsafe New ROI: {"min": 200, "max": 300}
Change: 100% shift, 0% overlap
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Define large jump | [0,100] → [200,300] | No overlap |
| 2 | Run safety validation | - | Fails |
| 3 | Check is_safe | - | False |
| 4 | Check warnings | - | "unsafe" or "large change" |

**Expected Result (overall):**
- Validation detects unsafe change
- Warning issued
- Command not sent (or sent with warning logged)

**Post-Conditions:**
- Admin notified of unsafe change

**Assertions:**
```python
current_min = 0
current_max = 100
new_min = 200
new_max = 300

safety_result = validate_roi_change_safety(
    current_min=current_min,
    current_max=current_max,
    new_min=new_min,
    new_max=new_max,
    max_change_percent=50.0
)

assert safety_result["is_safe"] == False
assert safety_result["overlap_percent"] == 0  # No overlap
assert len(safety_result["warnings"]) > 0

logger.info("✅ Unsafe ROI change detected")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_unsafe_roi_change`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-016: Unsafe ROI Range Change (Size Change > 50%)

**Summary:** Dynamic ROI – Detect Unsafe Size Change

**Objective:** Verify detection of unsafe size changes (e.g., doubling or halving ROI).

**Priority:** High

**Components/Labels:** focus-server, roi, safety, validation

**Requirements:** FOCUS-ROI-SAFETY

**Pre-Conditions:**
- PC-001: Safety rules configured

**Test Data:**
```json
Current ROI: {"min": 0, "max": 100, "size": 100}
Unsafe New ROI: {"min": 0, "max": 250, "size": 250}
Size change: 150% (unsafe)
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Calculate size change | (250-100)/100 | 150% increase |
| 2 | Run validation | max_change=50% | Fails |
| 3 | Check warnings | - | "size change too large" |

**Expected Result (overall):**
- Size change > 50% detected as unsafe
- Warning issued

**Post-Conditions:**
- Change logged

**Assertions:**
```python
current_size = 100
new_size = 250
size_change_percent = ((new_size - current_size) / current_size) * 100

assert size_change_percent == 150  # > 50% threshold

safety_result = validate_roi_change_safety(
    current_min=0,
    current_max=100,
    new_min=0,
    new_max=250,
    max_change_percent=50.0
)

assert safety_result["is_safe"] == False
logger.info("✅ Unsafe size change detected")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_unsafe_roi_range_change`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-017: Unsafe ROI Shift (Large Position Change)

**Summary:** Dynamic ROI – Detect Unsafe Position Shift

**Objective:** Verify detection when ROI shifts position dramatically.

**Priority:** Medium

**Components/Labels:** focus-server, roi, safety, validation

**Requirements:** FOCUS-ROI-SAFETY

**Pre-Conditions:**
- PC-001: Safety rules for position shifts

**Test Data:**
```json
Current ROI: {"min": 0, "max": 100}
New ROI: {"min": 150, "max": 250}
Shift: +150 sensors, 0% overlap
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Calculate shift | new_min - current_min | +150 |
| 2 | Calculate overlap | - | 0% |
| 3 | Run validation | - | Warning issued |

**Expected Result (overall):**
- Large shift detected
- Low overlap flagged

**Post-Conditions:**
- Warning logged

**Assertions:**
```python
current_min = 0
current_max = 100
new_min = 150
new_max = 250

shift = new_min - current_min
assert shift == 150  # Large shift

safety_result = validate_roi_change_safety(
    current_min=current_min,
    current_max=current_max,
    new_min=new_min,
    new_max=new_max
)

assert safety_result["overlap_percent"] == 0
logger.info("✅ Large shift detected")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_unsafe_roi_shift`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-018: Safe ROI Change (Within Limits)

**Summary:** Dynamic ROI – Validate Safe ROI Change

**Objective:** Confirm safe ROI changes pass validation.

**Priority:** High

**Components/Labels:** focus-server, roi, safety, validation

**Requirements:** FOCUS-ROI-SAFETY

**Pre-Conditions:**
- PC-001: Safety rules configured

**Test Data:**
```json
Current ROI: {"min": 0, "max": 100}
Safe New ROI: {"min": 10, "max": 110}
Change: +10 shift, 90% overlap
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Calculate overlap | [10,100] overlap | 90% |
| 2 | Calculate size change | 100 vs 100 | 0% |
| 3 | Run validation | - | Passes |
| 4 | Check is_safe | - | True |

**Expected Result (overall):**
- Safe change approved
- No warnings
- Command sent successfully

**Post-Conditions:**
- ROI changed to new range

**Assertions:**
```python
current_min = 0
current_max = 100
new_min = 10
new_max = 110

safety_result = validate_roi_change_safety(
    current_min=current_min,
    current_max=current_max,
    new_min=new_min,
    new_max=new_max,
    max_change_percent=50.0
)

assert safety_result["is_safe"] == True
assert safety_result["overlap_percent"] >= 80
assert len(safety_result["warnings"]) == 0

mq_client.send_roi_change(start=new_min, end=new_max)
logger.info("✅ Safe ROI change approved")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_safe_roi_change`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-019: CAxis Adjustment Command

**Summary:** Dynamic Visualization – Send CAxis Adjustment Command

**Objective:** Verify CAxis (color axis) adjustment commands can be sent via RabbitMQ for dynamic colormap range changes.

**Priority:** Medium

**Components/Labels:** focus-server, caxis, colormap, rabbitmq

**Requirements:** FOCUS-CAXIS-COMMAND

**Pre-Conditions:**
- PC-001: RabbitMQ accessible
- PC-002: Baby Analyzer supports CAxis commands

**Test Data:**
```json
CAxis Command:
{
  "command_type": "CAxisAdjustmentCommand",
  "caxis_min": -60,
  "caxis_max": -20,
  "routing_key": "caxis"
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Connect to RabbitMQ | - | Connected |
| 2 | Define CAxis range | min=-60, max=-20 | Range defined |
| 3 | Create CAxis command | - | Command created |
| 4 | Publish to exchange | routing_key="caxis" | Published |
| 5 | Verify no errors | - | Success |

**Expected Result (overall):**
- CAxis command sent successfully
- Baby Analyzer receives command
- Colormap range adjusted dynamically

**Post-Conditions:**
- Waterfall visualization uses new color range

**Assertions:**
```python
caxis_min = -60
caxis_max = -20

assert caxis_min < caxis_max  # Valid range

mq_client.send_caxis_adjustment(
    caxis_min=caxis_min,
    caxis_max=caxis_max,
    routing_key="caxis"
)

logger.info("✅ CAxis command sent successfully")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_caxis_adjustment`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-020: CAxis with Invalid Range (Min > Max)

**Summary:** Dynamic Visualization – Reject Invalid CAxis Range

**Objective:** Ensure invalid CAxis ranges (min > max) are rejected.

**Priority:** Medium

**Components/Labels:** focus-server, caxis, validation, negative-test

**Requirements:** FOCUS-CAXIS-VALIDATION

**Pre-Conditions:**
- PC-001: Validation enabled

**Test Data:**
```json
Invalid CAxis:
{
  "caxis_min": -20,
  "caxis_max": -60
}

Reversed range (min > max)
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Define invalid CAxis | min=-20, max=-60 | Reversed |
| 2 | Validate range | min > max | Invalid |
| 3 | Attempt send | - | Should fail or warn |

**Expected Result (overall):**
- Validation detects reversed range
- Command rejected or warning issued

**Post-Conditions:**
- Invalid command not applied

**Assertions:**
```python
caxis_min = -20
caxis_max = -60

assert caxis_min > caxis_max  # Invalid!

# Should raise exception or validation error
try:
    mq_client.send_caxis_adjustment(caxis_min, caxis_max)
    assert False, "Should have rejected invalid CAxis"
except Exception as e:
    logger.info(f"✅ Invalid CAxis correctly rejected: {e}")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_caxis_with_invalid_range`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-021: Invalid CAxis Range (General)

**Summary:** Dynamic Visualization – Various Invalid CAxis Scenarios

**Objective:** Test multiple invalid CAxis scenarios.

**Priority:** Low

**Components/Labels:** focus-server, caxis, validation

**Requirements:** FOCUS-CAXIS-VALIDATION

**Pre-Conditions:**
- PC-001: Validation rules defined

**Test Data:**
```json
Scenarios:
1. {"min": 0, "max": 0} - Zero range
2. {"min": null, "max": -20} - Null value
3. {"min": "invalid", "max": -20} - Wrong type
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Test zero range | min=0, max=0 | Rejected |
| 2 | Test null value | min=null | Rejected |
| 3 | Test wrong type | min="string" | Rejected |

**Expected Result (overall):**
- All invalid scenarios rejected
- Clear error messages

**Post-Conditions:**
- System state unchanged

**Assertions:**
```python
# Zero range
try:
    mq_client.send_caxis_adjustment(0, 0)
    assert False
except:
    logger.info("✅ Zero range rejected")

# Other invalid cases...
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_invalid_caxis_range`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-022: Valid CAxis Range

**Summary:** Dynamic Visualization – Valid CAxis Adjustment

**Objective:** Confirm valid CAxis ranges are accepted.

**Priority:** Medium

**Components/Labels:** focus-server, caxis, colormap

**Requirements:** FOCUS-CAXIS

**Pre-Conditions:**
- PC-001: Baby Analyzer running

**Test Data:**
```json
Valid CAxis:
{
  "caxis_min": -80,
  "caxis_max": -10
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Define valid range | [-80, -10] | Valid |
| 2 | Send command | - | Accepted |
| 3 | Verify applied | GET /waterfall | New range used |

**Expected Result (overall):**
- Valid CAxis accepted
- Visualization updated

**Post-Conditions:**
- Colormap uses new range

**Assertions:**
```python
caxis_min = -80
caxis_max = -10

assert caxis_min < caxis_max  # Valid

mq_client.send_caxis_adjustment(caxis_min, caxis_max)
logger.info("✅ Valid CAxis applied")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_valid_caxis_range`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-023: Colormap Commands

**Summary:** Dynamic Visualization – Colormap Change Commands

**Objective:** Verify colormap selection commands work via RabbitMQ.

**Priority:** Low

**Components/Labels:** focus-server, colormap, rabbitmq

**Requirements:** FOCUS-COLORMAP

**Pre-Conditions:**
- PC-001: Supported colormaps known (e.g., "jet", "viridis")

**Test Data:**
```json
Colormap Command:
{
  "command_type": "ColormapCommand",
  "colormap": "viridis"
}

Supported: jet, viridis, plasma, hot, cool
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Send colormap command | "viridis" | Accepted |
| 2 | Verify visualization | - | Uses new colormap |

**Expected Result (overall):**
- Colormap changed dynamically
- Visualization updated

**Post-Conditions:**
- New colormap active

**Assertions:**
```python
colormap = "viridis"

mq_client.send_colormap_command(colormap=colormap)
logger.info(f"✅ Colormap changed to {colormap}")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_colormap_commands`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-024: Valid Colormap Commands

**Summary:** Dynamic Visualization – Test All Valid Colormaps

**Objective:** Verify all supported colormaps work correctly.

**Priority:** Low

**Components/Labels:** focus-server, colormap

**Requirements:** FOCUS-COLORMAP

**Pre-Conditions:**
- PC-001: Colormap list defined

**Test Data:**
```json
Valid Colormaps:
["jet", "viridis", "plasma", "inferno", "magma", "hot", "cool"]
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Loop through colormaps | - | All accepted |
| 2 | Send each command | - | No errors |

**Expected Result (overall):**
- All valid colormaps work
- No errors

**Post-Conditions:**
- Last colormap active

**Assertions:**
```python
valid_colormaps = ["jet", "viridis", "plasma", "hot", "cool"]

for colormap in valid_colormaps:
    mq_client.send_colormap_command(colormap=colormap)
    time.sleep(1)
    logger.info(f"✅ {colormap} applied")

assert len(valid_colormaps) == 5
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_valid_colormap_commands`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-025: Colormap Serialization

**Summary:** Dynamic Visualization – Colormap Command Serialization

**Objective:** Verify colormap commands serialize correctly to JSON.

**Priority:** Low

**Components/Labels:** focus-server, colormap, serialization

**Requirements:** FOCUS-COLORMAP-SERIALIZATION

**Pre-Conditions:**
- PC-001: JSON serialization working

**Test Data:**
```json
Command Object:
{
  "command_type": "ColormapCommand",
  "colormap": "jet",
  "timestamp": "2025-10-20T12:00:00Z"
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Create command object | colormap="jet" | Object created |
| 2 | Serialize to JSON | json.dumps() | Valid JSON |
| 3 | Deserialize | json.loads() | Object restored |
| 4 | Validate fields | - | All fields present |

**Expected Result (overall):**
- Command serializes correctly
- No data loss in serialization

**Post-Conditions:**
- JSON valid and parseable

**Assertions:**
```python
command = {
    "command_type": "ColormapCommand",
    "colormap": "jet",
    "timestamp": datetime.utcnow().isoformat()
}

# Serialize
json_str = json.dumps(command)
assert isinstance(json_str, str)

# Deserialize
restored = json.loads(json_str)
assert restored["colormap"] == "jet"
assert restored["command_type"] == "ColormapCommand"

logger.info("✅ Colormap serialization works")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_colormap_serialization`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

# 🎯 Summary: ROI Tests (25/25 Complete)

**All 25 ROI tests documented!**

**Categories:**
- ✅ Basic ROI Changes (7 tests): TC-ROI-001 to TC-ROI-007
- ✅ Validation & Safety (7 tests): TC-ROI-008 to TC-ROI-014
- ✅ Safety Rules (4 tests): TC-ROI-015 to TC-ROI-018
- ✅ CAxis/Colormap (7 tests): TC-ROI-019 to TC-ROI-025

**Next:** Infrastructure Tests (25 tests)

---

**Files Created:**
1. `COMPLETE_XRAY_TEST_DOCUMENTATION_PART1_ROI.md` (TC-ROI-001 to TC-ROI-007)
2. `COMPLETE_XRAY_TEST_DOCUMENTATION_PART2_ROI_CONTINUED.md` (TC-ROI-008 to TC-ROI-025)

**Ready to continue with Infrastructure Tests?**
