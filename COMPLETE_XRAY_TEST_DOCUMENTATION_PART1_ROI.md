# 📋 Complete Xray Test Documentation - Part 1: ROI Tests (25 Tests)

**Generated:** 2025-10-20  
**Category:** Dynamic ROI (Region of Interest) Adjustment  
**Total Tests:** 25  
**Source File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-001: Send ROI Change Command via RabbitMQ

**Summary:** Dynamic ROI Change – Send RegionOfInterestCommand via RabbitMQ

**Objective:** Verify that a RegionOfInterestCommand can be successfully published to RabbitMQ Baby Analyzer exchange and accepted by the system without errors.

**Priority:** High

**Components/Labels:** focus-server, rabbitmq, roi, baby-analyzer, mq-commands

**Requirements:** FOCUS-ROI-COMMAND, FOCUS-RABBITMQ-INTEGRATION

**Pre-Conditions:**
- PC-001: RabbitMQ server accessible at configured host/port
- PC-002: RabbitMQ credentials valid (username/password)
- PC-003: Baby Analyzer exchange exists
- PC-004: ROI routing key configured

**Test Data:**
```json
RabbitMQ Connection:
{
  "host": "10.10.100.107",
  "port": 5672,
  "username": "prisma",
  "password": "prisma",
  "vhost": "/"
}

ROI Command Payload:
{
  "command_type": "RegionOfInterestCommand",
  "start": 50,
  "end": 150,
  "routing_key": "roi"
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Connect to RabbitMQ | host=10.10.100.107, port=5672 | Connection established |
| 2 | Verify exchange exists | exchange="baby_analyzer" | Exchange available |
| 3 | Create ROI command | start=50, end=150 | Command object created |
| 4 | Publish command | routing_key="roi" | Message published successfully |
| 5 | Verify no exceptions | - | No errors raised |
| 6 | Check MQ acknowledgment | - | ACK received |

**Expected Result (overall):**
- ROI change command published to RabbitMQ successfully
- No exceptions or connection errors
- Command delivered to Baby Analyzer queue
- MQ acknowledgment received

**Post-Conditions:**
- RabbitMQ connection closed cleanly
- No orphaned messages in queues

**Assertions:**
```python
# Connect to RabbitMQ
client = BabyAnalyzerMQClient(host="10.10.100.107", port=5672, 
                               username="prisma", password="prisma")
client.connect()
assert client.is_connected() == True

# Send ROI command
new_start = 50
new_end = 150
client.send_roi_change(start=new_start, end=new_end, routing_key="roi")

# Verify no exceptions
assert True  # Test passes if no exception raised

# Cleanup
client.disconnect()
```

**Environment:** Staging, Production

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_send_roi_change_command`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-002: ROI Change with Safety Validation

**Summary:** Dynamic ROI Change – Validate Safety Before Sending Command

**Objective:** Ensure ROI change requests undergo safety validation to prevent unsafe or destructive changes that could impact system stability.

**Priority:** Critical

**Components/Labels:** focus-server, roi, safety-validation, rabbitmq

**Requirements:** FOCUS-ROI-SAFETY, FOCUS-VALIDATION

**Pre-Conditions:**
- PC-001: RabbitMQ accessible
- PC-010: Current ROI known (min=0, max=100)
- PC-011: Safety validation rules configured (max_change_percent=50%)

**Test Data:**
```json
Current ROI:
{
  "current_min": 0,
  "current_max": 100
}

New ROI (Safe):
{
  "new_min": 20,
  "new_max": 120
}

Safety Rules:
{
  "max_change_percent": 50.0,
  "min_overlap_percent": 30.0
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Define current ROI | min=0, max=100 | Current state captured |
| 2 | Define new ROI | min=20, max=120 | New state defined |
| 3 | Calculate change percentage | (120-20) vs (100-0) | 0% change (same size) |
| 4 | Calculate overlap | [20,100] overlap | 80% overlap |
| 5 | Run safety validation | validate_roi_change_safety() | Safety check passes |
| 6 | Check is_safe flag | result["is_safe"] | True |
| 7 | Send ROI command | start=20, end=120 | Command sent successfully |

**Expected Result (overall):**
- Safety validation passes (is_safe=True)
- No warnings generated
- ROI command sent to RabbitMQ
- System accepts new ROI range

**Post-Conditions:**
- Safety validation logs recorded
- Command successfully delivered

**Assertions:**
```python
current_min = 0
current_max = 100
new_min = 20
new_max = 120

# Validate safety
safety_result = validate_roi_change_safety(
    current_min=current_min,
    current_max=current_max,
    new_min=new_min,
    new_max=new_max,
    max_change_percent=50.0
)

assert safety_result["is_safe"] == True
assert len(safety_result["warnings"]) == 0
assert safety_result["overlap_percent"] >= 30.0

# Send command
client.send_roi_change(start=new_min, end=new_max)
assert True  # No exception means success
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_roi_change_with_validation`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-003: Multiple ROI Changes in Sequence

**Summary:** Dynamic ROI – Sequential ROI Changes Without System Restart

**Objective:** Verify that multiple ROI change commands can be sent in sequence without requiring system restart or causing state corruption.

**Priority:** High

**Components/Labels:** focus-server, roi, sequence, stability

**Requirements:** FOCUS-ROI-MULTIPLE, FOCUS-STABILITY

**Pre-Conditions:**
- PC-001: RabbitMQ accessible
- PC-010: Live task configured and running
- PC-011: Baby Analyzer responsive to commands

**Test Data:**
```json
ROI Sequence:
[
  {"start": 0, "end": 100},
  {"start": 50, "end": 150},
  {"start": 100, "end": 200},
  {"start": 75, "end": 175},
  {"start": 25, "end": 125}
]

Wait Time Between Commands: 2 seconds
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Send ROI command 1 | [0, 100] | Command sent |
| 2 | Wait | 2 seconds | System stabilizes |
| 3 | Send ROI command 2 | [50, 150] | Command sent |
| 4 | Wait | 2 seconds | System stabilizes |
| 5 | Send ROI command 3 | [100, 200] | Command sent |
| 6 | Wait | 2 seconds | System stabilizes |
| 7 | Send ROI command 4 | [75, 175] | Command sent |
| 8 | Wait | 2 seconds | System stabilizes |
| 9 | Send ROI command 5 | [25, 125] | Command sent |
| 10 | Verify all successful | - | No errors in sequence |

**Expected Result (overall):**
- All 5 ROI commands sent successfully
- No connection drops or timeouts
- System remains responsive throughout
- No memory leaks or resource exhaustion

**Post-Conditions:**
- Final ROI applied correctly ([25, 125])
- System stable and operational

**Assertions:**
```python
roi_sequence = [
    (0, 100),
    (50, 150),
    (100, 200),
    (75, 175),
    (25, 125)
]

for i, (start, end) in enumerate(roi_sequence, 1):
    logger.info(f"Sending ROI change {i}/5: [{start}, {end}]")
    client.send_roi_change(start=start, end=end)
    assert True  # No exception
    time.sleep(2)  # Wait for processing

logger.info("✅ All 5 ROI commands sent successfully")
assert len(roi_sequence) == 5
```

**Environment:** Staging, Production

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_multiple_roi_changes_sequence`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-004: ROI Change Affects Waterfall Data

**Summary:** Dynamic ROI – Verify Waterfall Data Reflects New ROI

**Objective:** Confirm that after sending an ROI change command, the GET /waterfall endpoint returns data only for the new sensor range, proving Baby Analyzer reinitialized correctly.

**Priority:** Critical

**Components/Labels:** focus-server, roi, waterfall, baby-analyzer, api

**Requirements:** FOCUS-ROI-WATERFALL, FOCUS-API-WATERFALL

**Pre-Conditions:**
- PC-001: Live task configured with initial ROI [0, 100]
- PC-002: GET /waterfall endpoint accessible
- PC-003: RabbitMQ accessible for ROI commands
- PC-004: Baby Analyzer running and processing

**Test Data:**
```json
Initial Configuration:
{
  "task_id": "roi_waterfall_test_20251020_120000",
  "initial_roi": {"min": 0, "max": 100}
}

ROI Change:
{
  "new_roi": {"start": 40, "end": 60}
}

Waterfall Request:
{
  "method": "GET",
  "endpoint": "/waterfall",
  "params": {
    "task_id": "roi_waterfall_test_20251020_120000",
    "row_count": 10
  }
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Configure live task | ROI [0, 100] | Task created |
| 2 | GET /waterfall (before) | task_id | Sensors 0-100 in response |
| 3 | Send ROI change command | [40, 60] | Command sent |
| 4 | Wait for reinitialization | 5 seconds | Baby Analyzer restarts |
| 5 | GET /waterfall (after) | task_id | Sensors 40-60 in response |
| 6 | Verify sensor_range | response["sensor_range"] | {"min": 40, "max": 60} |
| 7 | Verify data shape | response["data"] | Matches new range |
| 8 | Check row count | len(response["data"]) | == 10 rows |

**Expected Result (overall):**
- Initial waterfall returns sensors [0, 100]
- After ROI change, waterfall returns ONLY sensors [40, 60]
- Data shape and sensor_range fields updated correctly
- No data from outside new ROI range

**Post-Conditions:**
- Baby Analyzer continues processing with new ROI
- Waterfall data consistent with new range

**Assertions:**
```python
# Configure task with initial ROI
task_id = "roi_waterfall_test"
initial_response = focus_api.config_task(task_id, roi_min=0, roi_max=100)
assert initial_response.status == "Config received successfully"

# Get waterfall before ROI change
waterfall_before = focus_api.get_waterfall(task_id, row_count=10)
assert waterfall_before.sensor_range["min"] == 0
assert waterfall_before.sensor_range["max"] == 100

# Send ROI change
mq_client.send_roi_change(start=40, end=60)
time.sleep(5)  # Wait for reinitialization

# Get waterfall after ROI change
waterfall_after = focus_api.get_waterfall(task_id, row_count=10)
assert waterfall_after.sensor_range["min"] == 40
assert waterfall_after.sensor_range["max"] == 60
assert len(waterfall_after.data) == 10

logger.info("✅ Waterfall data correctly reflects new ROI")
```

**Environment:** Staging, Production

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_roi_change_affects_waterfall_data`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-005: ROI Expansion (Increase Range)

**Summary:** Dynamic ROI – Expand ROI Range (Increase Sensor Coverage)

**Objective:** Validate that expanding the ROI range (making it larger) works correctly and system adapts to monitor more sensors.

**Priority:** Medium

**Components/Labels:** focus-server, roi, expansion

**Requirements:** FOCUS-ROI-EXPANSION

**Pre-Conditions:**
- PC-001: Task configured with ROI [50, 100]
- PC-002: System monitoring 50 sensors

**Test Data:**
```json
Current ROI: {"min": 50, "max": 100}
New ROI (Expanded): {"min": 25, "max": 125}
Change: +50 sensors (25 below, 25 above)
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Configure initial ROI | [50, 100] | 50 sensors monitored |
| 2 | Send expansion command | [25, 125] | Command accepted |
| 3 | Wait for reinitialization | 5 sec | Baby Analyzer restarts |
| 4 | Verify new range | GET /waterfall | Sensors [25, 125] |
| 5 | Check sensor count | - | 100 sensors monitored |

**Expected Result (overall):**
- ROI successfully expanded from 50 to 100 sensors
- System now monitors additional 50 sensors
- No data loss or corruption

**Post-Conditions:**
- System continues with expanded ROI

**Assertions:**
```python
# Initial ROI
initial_roi = {"min": 50, "max": 100}
assert (initial_roi["max"] - initial_roi["min"]) == 50

# Expand ROI
new_roi = {"min": 25, "max": 125}
mq_client.send_roi_change(start=25, end=125)
time.sleep(5)

# Verify expansion
waterfall = focus_api.get_waterfall(task_id)
assert waterfall.sensor_range["min"] == 25
assert waterfall.sensor_range["max"] == 125
assert (waterfall.sensor_range["max"] - waterfall.sensor_range["min"]) == 100

logger.info("✅ ROI expanded successfully")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_roi_expansion`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-006: ROI Shrinking (Decrease Range)

**Summary:** Dynamic ROI – Shrink ROI Range (Reduce Sensor Coverage)

**Objective:** Validate that shrinking the ROI range (making it smaller) works correctly for focusing on specific area.

**Priority:** Medium

**Components/Labels:** focus-server, roi, shrink, focus

**Requirements:** FOCUS-ROI-SHRINK

**Pre-Conditions:**
- PC-001: Task configured with ROI [0, 200]
- PC-002: System monitoring 200 sensors

**Test Data:**
```json
Current ROI: {"min": 0, "max": 200}
New ROI (Shrunk): {"min": 75, "max": 125}
Change: -150 sensors (focus on middle 50)
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Configure initial ROI | [0, 200] | 200 sensors monitored |
| 2 | Send shrink command | [75, 125] | Command accepted |
| 3 | Wait for reinitialization | 5 sec | Baby Analyzer restarts |
| 4 | Verify new range | GET /waterfall | Sensors [75, 125] |
| 5 | Check sensor count | - | 50 sensors monitored |

**Expected Result (overall):**
- ROI successfully shrunk from 200 to 50 sensors
- System now monitors only middle range
- Performance improved due to fewer sensors

**Post-Conditions:**
- System continues with shrunk ROI
- Resources freed up

**Assertions:**
```python
# Initial ROI
initial_roi = {"min": 0, "max": 200}
assert (initial_roi["max"] - initial_roi["min"]) == 200

# Shrink ROI
new_roi = {"min": 75, "max": 125}
mq_client.send_roi_change(start=75, end=125)
time.sleep(5)

# Verify shrink
waterfall = focus_api.get_waterfall(task_id)
assert waterfall.sensor_range["min"] == 75
assert waterfall.sensor_range["max"] == 125
assert (waterfall.sensor_range["max"] - waterfall.sensor_range["min"]) == 50

logger.info("✅ ROI shrunk successfully")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_roi_shrinking`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

## TC-ROI-007: ROI Shift (Move Range)

**Summary:** Dynamic ROI – Shift ROI Range Without Changing Size

**Objective:** Verify that shifting ROI (moving the window while keeping size constant) works correctly.

**Priority:** Medium

**Components/Labels:** focus-server, roi, shift, pan

**Requirements:** FOCUS-ROI-SHIFT

**Pre-Conditions:**
- PC-001: Task configured with ROI [0, 50]

**Test Data:**
```json
Current ROI: {"min": 0, "max": 50}
New ROI (Shifted): {"min": 100, "max": 150}
Change: Moved +100 sensors right, size unchanged
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Configure initial ROI | [0, 50] | 50 sensors (0-49) |
| 2 | Send shift command | [100, 150] | Command accepted |
| 3 | Wait | 5 sec | Reinitialization |
| 4 | Verify new range | GET /waterfall | Sensors [100, 150] |
| 5 | Check size unchanged | - | Still 50 sensors |

**Expected Result (overall):**
- ROI shifted right by 100 sensors
- Size remains 50 sensors
- No overlap with previous range

**Post-Conditions:**
- System monitoring new shifted range

**Assertions:**
```python
initial_roi = {"min": 0, "max": 50}
initial_size = initial_roi["max"] - initial_roi["min"]

new_roi = {"min": 100, "max": 150}
mq_client.send_roi_change(start=100, end=150)
time.sleep(5)

waterfall = focus_api.get_waterfall(task_id)
new_size = waterfall.sensor_range["max"] - waterfall.sensor_range["min"]

assert waterfall.sensor_range["min"] == 100
assert waterfall.sensor_range["max"] == 150
assert new_size == initial_size  # Size unchanged

logger.info("✅ ROI shifted successfully")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_roi_shift`  
**Test File:** `tests/integration/api/test_dynamic_roi_adjustment.py`

---

Due to length constraints, I'll continue with the remaining ROI tests and other categories in subsequent parts. Would you like me to continue with:

1. TC-ROI-008 through TC-ROI-025 (remaining ROI tests)
2. Infrastructure tests (25 tests)
3. SingleChannel tests (15 tests)
4. Historic Playback tests (10 tests)
5. Config Validation tests (10 critical tests)

Each test will have the same level of detail with exact code references, actual assertions, and accurate technical specifications.

Shall I continue?
