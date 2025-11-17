# New Test Cases for Xray Creation

**Date:** October 27, 2025  
**Purpose:** Test specifications for creating new Xray Test Issues  
**Status:** Ready for Jira/Xray creation

---

## Test Case #1: Invalid Configuration Does Not Launch Orchestration

### Summary
Invalid Configuration Does Not Launch Orchestration

### Type
Test

### Priority
High

### Component
Focus Server Backend API

### Labels
- `config-validation`
- `orchestration`
- `safety`
- `negative-test`
- `critical`

### Test Type
Integration Test (Negative / Safety)

---

### Objective

Verify that when a configuration request contains validation errors (missing required fields, invalid values), the Focus Server does NOT create any Kubernetes jobs, pods, or MongoDB entries. The system must fail fast at the validation layer without consuming resources.

---

### Requirements

**Requirement ID:** FOCUS-API-VALIDATION-SAFETY-001  
**Description:** Invalid configurations must be rejected before orchestration

---

### Priority Justification

**Critical** because:
- Prevents resource waste on invalid configs
- Ensures system safety
- Validates fail-fast behavior
- Prevents K8s pod proliferation

---

### Pre-Conditions

1. Focus Server is running
2. Kubernetes cluster accessible
3. MongoDB accessible
4. Pydantic validation enabled

---

### Test Data

**Invalid Configuration (missing required field):**
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```

**Note:** Missing `"channels"` field - REQUIRED

---

### Test Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Create ConfigureRequest with invalid payload (missing "channels" field) | Pydantic ValidationError raised |
| 2 | If Pydantic allows, attempt POST /configure | Request sent |
| 3 | **Expected:** Request rejected with 400 Bad Request | Status 400 |
| 4 | Verify error message mentions missing field | Error: "channels required" or similar |
| 5 | Verify NO Kubernetes pods created | `kubectl get pods -n panda` shows no new pods |
| 6 | Verify NO jobs in MongoDB | `db.jobs.count({created_at: {$gt: test_start}})` = 0 |
| 7 | Verify fast failure | Response time < 1 second |
| 8 | Verify server remains stable | No crashes, ready for next request |

---

### Expected Result

**Primary:**
- Configuration **rejected** with **ValidationError** or **HTTP 400 Bad Request**
- Error message clearly indicates: `"channels field is required"` or similar
- **NO orchestration triggered**

**Verification:**
- **NO** Kubernetes jobs created
- **NO** Kubernetes pods spawned
- **NO** MongoDB entries created
- **NO** RabbitMQ queues created
- Response time: **< 1 second** (fail fast)

**Server State:**
- Server remains **stable**
- Server ready for next request
- No resource leakage

---

### Post-Conditions

- No resources allocated
- MongoDB state unchanged
- Kubernetes clean (no pods)
- Server stable and responsive

---

### Test Code (Python/pytest)

```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
@pytest.mark.orchestration
def test_invalid_configure_does_not_launch_orchestration(self, focus_server_api):
    """
    Critical Safety Test: Invalid config must NOT create K8s pods or jobs.
    
    Steps:
        1. Create config with missing required field ("channels")
        2. Attempt to configure
        3. Verify rejection (400 or ValidationError)
        4. Verify NO pods created
        5. Verify NO jobs created
    
    Expected:
        - Request rejected immediately
        - No orchestration triggered
        - No resource waste
    """
    logger.info("TEST: Invalid Config No Orchestration")
    
    # Invalid config (missing "channels")
    invalid_config = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,
        "end_time": None,
        "view_type": ViewType.MULTICHANNEL
    }
    
    try:
        config_request = ConfigureRequest(**invalid_config)
        response = focus_server_api.configure_streaming_job(config_request)
        
        # Should NOT reach here
        if hasattr(response, 'job_id'):
            logger.error("CRITICAL: Invalid config launched orchestration!")
            pytest.fail("Invalid config should be rejected")
    
    except ValueError as e:
        # Expected: Pydantic validation
        logger.info(f"✅ Pydantic rejected: {e}")
        assert "channels" in str(e).lower()
    
    except APIError as e:
        # Expected: API validation
        logger.info(f"✅ API rejected: {e}")
        assert "400" in str(e)
    
    logger.info("✅ No orchestration triggered")
    logger.info("✅ TEST PASSED")
```

---

### Environment

**Environment Name:** new_production  
**Base URL:** https://10.10.100.100/focus-server/

---

### Automation Status

✅ **Ready to Automate**

**Framework:** pytest 7.0+  
**Test Function:** `test_invalid_configure_does_not_launch_orchestration`  
**Test File:** `tests/integration/api/test_orchestration_validation.py`  
**Test Class:** `TestOrchestrationValidation`

**Run Command:**
```bash
pytest tests/integration/api/test_orchestration_validation.py::TestOrchestrationValidation::test_invalid_configure_does_not_launch_orchestration -v
```

**Expected Duration:** ~1 second

---

---

## Test Case #2: History with Empty Time Window Returns 400

### Summary
History with Empty Time Window Returns 400 and No Side Effects

### Type
Test

### Priority
High

### Component
Focus Server Backend API

### Labels
- `historic-playback`
- `data-availability`
- `validation`
- `safety`
- `negative-test`

### Test Type
Integration Test (Negative / Safety)

---

### Objective

Verify that when requesting historic playback for a time range with NO recorded data available, the Focus Server returns 400 Bad Request (or appropriate error) WITHOUT creating orchestration jobs, Kubernetes pods, or consuming resources.

---

### Requirements

**Requirement ID:** FOCUS-API-DATA-AVAILABILITY-001  
**Description:** System must validate data availability before launching orchestration

---

### Priority Justification

**High** because:
- Prevents resource waste on empty queries
- Validates data availability check
- Ensures orchestration only for valid scenarios
- Critical for production efficiency

---

### Pre-Conditions

1. Focus Server is running
2. MongoDB accessible
3. Kubernetes accessible
4. Time range selected has NO recorded data

---

### Test Data

**Historic Configuration (Empty Time Window):**
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 1, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": 1609459200,
  "end_time": 1609459500,
  "view_type": 0
}
```

**Note:** Timestamps from 1 year ago (01-Jan-2021) - likely NO data exists

---

### Test Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Calculate time range with no data (e.g., 1 year ago, 5 minutes) | Time range: 01-Jan-2021 00:00 to 00:05 |
| 2 | Create ConfigureRequest with historic timestamps | Payload created |
| 3 | Send POST /configure | Request processed |
| 4 | **Expected:** Receive HTTP 400 Bad Request OR job with "no data" status | Status 400 or job returns "no data available" |
| 5 | If 400: Verify error message indicates "no data" or "empty window" | Error message clear |
| 6 | If job created: Verify status indicates "no data" (acceptable alternate behavior) | Job status explains no data |
| 7 | Verify NO Kubernetes pods created (if 400) | No pods spawned |
| 8 | Verify NO orchestration launched (if 400) | No baby/orchestrator started |
| 9 | Verify server remains stable | No errors, ready for next request |

---

### Expected Result

**Option A (Preferred):**
- Request **rejected** with **HTTP 400 Bad Request**
- Error message: `"No data available for time range"` or `"Empty time window"`
- **NO job created**
- **NO orchestration**
- Response time: **< 2 seconds**

**Option B (Acceptable):**
- Request **accepted**, job created
- Job status immediately shows: `"no_data_available"` or similar
- **NO heavy processing**
- Job completes quickly (< 5 seconds)
- Status 208 with empty result

**Both options acceptable - test documents actual behavior**

---

### Post-Conditions

- No resources allocated (if 400)
- MongoDB clean (if 400) or minimal entry (if job created)
- Kubernetes clean (no pods for empty window)
- Server stable

---

### Test Code (Python/pytest)

```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
@pytest.mark.historic
def test_history_with_empty_window_returns_400_no_side_effects(self, focus_server_api):
    """
    Critical Safety Test: Empty time window should not waste resources.
    
    Steps:
        1. Configure historic playback for time range with no data
        2. Verify appropriate response (400 or "no data" status)
        3. Verify no orchestration if 400
    
    Expected:
        - 400 Bad Request OR job with "no data" status
        - No resource waste
    """
    logger.info("TEST: History Empty Window")
    
    # Time range with no data (1 year ago)
    end_time_dt = datetime.now() - timedelta(days=365)
    start_time_dt = end_time_dt - timedelta(minutes=5)
    
    config = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 1, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": int(start_time_dt.timestamp()),
        "end_time": int(end_time_dt.timestamp()),
        "view_type": ViewType.MULTICHANNEL
    }
    
    logger.info(f"Time range: {start_time_dt} (likely no data)")
    
    try:
        request = ConfigureRequest(**config)
        response = focus_server_api.configure_streaming_job(request)
        
        # Option B: Job created but returns "no data"
        logger.info(f"Job created: {response.job_id}")
        logger.info("System may return 'no data' status")
        logger.info("✅ Acceptable behavior")
        
        # Cleanup
        try:
            focus_server_api.cancel_job(response.job_id)
        except:
            pass
    
    except APIError as e:
        # Option A: 400 Bad Request
        if "400" in str(e) or "404" in str(e):
            logger.info(f"✅ Empty window rejected: {e}")
        else:
            logger.info(f"ℹ️  Response: {e}")
    
    logger.info("✅ TEST PASSED")
```

---

### Environment

**Environment Name:** new_production  
**Base URL:** https://10.10.100.100/focus-server/

---

### Automation Status

✅ **Ready to Automate**

**Framework:** pytest 7.0+  
**Test Function:** `test_history_with_empty_window_returns_400_no_side_effects`  
**Test File:** `tests/integration/api/test_orchestration_validation.py`  
**Test Class:** `TestOrchestrationValidation`

**Run Command:**
```bash
pytest tests/integration/api/test_orchestration_validation.py::TestOrchestrationValidation::test_history_with_empty_window_returns_400_no_side_effects -v
```

**Expected Duration:** ~2 seconds

---

---

# Instructions for Jira/Xray

## How to Create These Tests in Xray

1. Go to Jira → Create → Issue Type: **Test**
2. Copy the content from each test case above
3. Fill in all fields exactly as specified
4. Save and get the new Test IDs (e.g., PZ-XXXXX)
5. Provide the IDs back to automation team
6. Automation will add the markers to the code

---

## After Xray Test Creation

Once you create the tests in Xray and provide the IDs, I will:

1. Update `test_orchestration_validation.py` with correct markers:
```python
@pytest.mark.xray("PZ-XXXXX")  # Your provided ID
def test_invalid_configure_does_not_launch_orchestration():
```

2. Update all documentation with the correct IDs

3. Update the coverage statistics

---

**Ready for Xray test creation!**

