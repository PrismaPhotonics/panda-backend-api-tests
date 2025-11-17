# JIRA Tickets - Focus Server Automation Findings
**Project**: FOCUS  
**Component**: Focus Server API  
**Found By**: Automated Integration Tests  
**Test Date**: 2025-10-12  

---

## Ticket 1: Empty Status String in Configure Response

### JIRA Format
```
Project: FOCUS
Issue Type: Bug
Component: Focus Server
Priority: Medium
Severity: Low
Labels: api, configure-endpoint, status-field, automated-test
Affects Version: Current

Summary:
Configure endpoint returns empty status string instead of "success"

Description:
The Focus Server /configure endpoint returns HTTP 200 with an empty string in the 'status' field instead of a meaningful status value like "success", "error", or "pending".

Steps to Reproduce:
1. Send POST request to /configure with valid SINGLECHANNEL payload
2. Receive HTTP 200 response
3. Observe status field is empty string ""

Expected Result:
status field should contain "success" for successful configuration

Actual Result:
status field contains empty string ""

Impact:
- Clients cannot validate operation success programmatically
- API contract is unclear
- Monitoring and logging are less effective

Evidence:
Test: tests/integration/api/test_singlechannel_view_mapping.py::test_configure_singlechannel_mapping
Log output:
  ⚠️ Server returned empty status - needs backend clarification
  ⚠️ Expected: status='success', Got: status=''

Request:
POST /configure
{
  "view_type": "1",
  "channels": {"min": 7, "max": 7},
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "frequencyRange": {"min": 0, "max": 500}
}

Response (HTTP 200):
{
  "status": "",  ← Empty!
  "stream_amount": 1,
  "channel_to_stream_index": {"7": 0},
  "job_id": "31-3633"
}

Recommendation:
Set status to "success" for HTTP 200 responses:
response["status"] = "success" if successful else "error"

Environment:
Staging: http://10.10.10.150:5000

Reproducibility: Always (100%)

Assignee: [Backend Team]
Reporter: QA Automation
```

---

## Ticket 2: SingleChannel View Accepts Multiple Channels (min != max)

### JIRA Format
```
Project: FOCUS
Issue Type: Bug
Component: Focus Server, View Type Logic
Priority: High
Severity: Major
Labels: api, singlechannel, validation, contract-violation, automated-test
Affects Version: Current

Summary:
SINGLECHANNEL view accepts min != max, returns multiple channels in mapping

Description:
The Focus Server /configure endpoint accepts view_type=SINGLECHANNEL requests where channels.min != channels.max, violating the SingleChannel contract. This results in multiple channels being mapped to a single stream, creating inconsistent and confusing behavior.

SingleChannel Definition:
"SingleChannel view should return exactly one stream for exactly one channel"

Current Behavior (WRONG):
- Request: view_type=SINGLECHANNEL, channels={min:5, max:10}
- Server accepts (HTTP 200) ❌
- Returns stream_amount=1 ✓
- Returns 6 channels in mapping: {"5":0, "6":0, "7":0, "8":0, "9":0, "10":0} ❌
- Returns channel_amount=1 (inconsistent with 6 channels) ❌

Expected Behavior (CORRECT):
Server should REJECT with HTTP 400/422:
{
  "status": "error",
  "message": "For SINGLECHANNEL view, channels.min must equal channels.max",
  "provided": {"min": 5, "max": 10}
}

Steps to Reproduce:
1. Send POST /configure with view_type="1" (SINGLECHANNEL)
2. Set channels.min=5, channels.max=10 (6 channels)
3. Server accepts request (should reject)
4. Response contains 6 channels in channel_to_stream_index

Impact:
HIGH - Business Logic Violation
- Violates SingleChannel view definition
- Creates data inconsistency (channel_amount=1 but 6 channels mapped)
- Confuses clients expecting single channel
- Frontend may render incorrectly
- Downstream systems receive unexpected multi-channel data

Evidence:
Test: tests/integration/api/test_singlechannel_view_mapping.py::test_singlechannel_with_min_not_equal_max_should_fail

Log output:
2025-10-12 15:44:44 [INFO] Server accepted request with min != max
2025-10-12 15:44:44 [INFO] Stream amount: 1
2025-10-12 15:44:44 [INFO] Channel mapping: {'5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0}
2025-10-12 15:44:44 [INFO] ⚠️  Server accepted min != max but maintained stream_amount=1

Request:
POST /configure
{
  "view_type": "1",
  "channels": {"min": 5, "max": 10},  ← Should be rejected!
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "frequencyRange": {"min": 0, "max": 500}
}

Actual Response (HTTP 200):
{
  "status": "",
  "stream_amount": 1,
  "channel_to_stream_index": {
    "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0  ← 6 channels!
  },
  "channel_amount": 1,  ← Inconsistent!
  "job_id": "..."
}

Root Cause:
Missing validation: Server does not check min==max for SINGLECHANNEL view

Recommendation:
Add validation in request handler:
```python
if view_type == ViewType.SINGLECHANNEL:
    if channels.min != channels.max:
        raise ValidationError(
            "For SINGLECHANNEL view, channels.min must equal channels.max"
        )
```

Return HTTP 400 with clear error message.

Breaking Change Warning:
⚠️ This fix may break existing clients if they rely on current behavior.
Recommended: Audit production usage before deploying fix.

Environment:
Staging: http://10.10.10.150:5000

Reproducibility: Always (100%)

Assignee: [Backend Team]
Reporter: QA Automation
```

---

## Ticket 3: Job Cancellation Endpoint Returns 404

### JIRA Format
```
Project: FOCUS
Issue Type: Bug / Task (Clarification Needed)
Component: Focus Server, Job Management
Priority: Medium
Severity: Medium
Labels: api, job-management, cancellation, endpoint-missing, automated-test
Affects Version: Current

Summary:
DELETE /job/{job_id} returns 404 - Job cancellation not working

Description:
Attempting to cancel a Focus Server job using DELETE /job/{job_id} returns HTTP 404 Not Found, even for valid, active jobs that were just created. This prevents clients from canceling jobs programmatically.

Unclear if this is:
a) A bug (endpoint exists but broken)
b) Not implemented (endpoint doesn't exist)
c) Wrong endpoint path (should be different URL)

Current Behavior:
1. Create job: POST /configure → job_id="41-3643"
2. Cancel job: DELETE /job/41-3643 → HTTP 404 {"detail": "Not Found"}

Expected Behavior:
Either:
a) HTTP 200 - Job cancelled successfully
b) HTTP 501 - Cancellation not implemented (with explanation)
c) HTTP 409 - Job already completed (cannot cancel)

Steps to Reproduce:
1. POST /configure with valid payload
2. Extract job_id from response (e.g., "41-3643")
3. DELETE /job/41-3643
4. Observe: HTTP 404 Not Found

Impact:
MEDIUM - Resource Management Issue
- Cannot cancel jobs programmatically
- Jobs continue consuming resources even when not needed
- Cannot recover from jobs started by mistake
- Tests cannot clean up created jobs
- Unclear job lifecycle and cleanup mechanism

Evidence:
Test: tests/integration/api/test_singlechannel_view_mapping.py::test_same_channel_multiple_requests_consistent_mapping

Log output:
2025-10-12 15:44:46 [INFO] src.apis.focus_server_api: Cancelling job: 41-3643
2025-10-12 15:44:46 [ERROR] Full error response: {'detail': 'Not Found'}
2025-10-12 15:44:46 [ERROR] HTTP 404 error for http://10.10.10.150:5000/job/41-3643
2025-10-12 15:44:46 [INFO] ⚠️  Job cancellation not supported or failed

Request:
DELETE /job/41-3643

Response:
HTTP 404 Not Found
{"detail": "Not Found"}

Questions for Backend Team:
1. Is job cancellation supposed to be supported?
2. If yes, what is the correct endpoint and HTTP method?
   - DELETE /job/{job_id}?
   - POST /job/{job_id}/cancel?
   - DELETE /cancel/{job_id}?
   - Other?
3. If no, what is the recommended way to stop unwanted jobs?
4. Do jobs auto-expire? What is the timeout?
5. Is there an alternative cleanup mechanism?

Possible Solutions:

Option 1 - Implement Cancellation:
Implement DELETE /job/{job_id} endpoint:
```python
@app.delete("/job/{job_id}")
def cancel_job(job_id: str):
    job_manager.cancel_job(job_id)
    return {"status": "success", "job_id": job_id}
```

Option 2 - Return 501 (Not Implemented):
If cancellation is not supported:
```python
@app.delete("/job/{job_id}")
def cancel_job(job_id: str):
    return JSONResponse(
        status_code=501,
        content={
            "message": "Job cancellation not supported",
            "alternative": "Jobs auto-expire after 5 minutes"
        }
    )
```

Option 3 - Document Alternative:
If different endpoint exists, update API documentation and client code.

Environment:
Staging: http://10.10.10.150:5000

Reproducibility: Always (100%)

Assignee: [Backend Team]
Reporter: QA Automation
```

---

## Summary Dashboard

| Ticket | Priority | Severity | Type | Status | Estimated Effort |
|--------|----------|----------|------|--------|------------------|
| FOCUS-001 | Medium | Low | Bug | Open | 1-2 hours (simple fix) |
| FOCUS-002 | **High** | **Major** | Bug | Open | 4-8 hours (validation + testing) |
| FOCUS-003 | Medium | Medium | Clarification | Open | TBD (depends on answer) |

---

## Recommended Action Order

### Week 1 (Immediate)
1. **FOCUS-002** (High Priority) - Add validation for SINGLECHANNEL
   - Impact: HIGH - Violates API contract
   - Effort: Medium (4-8 hours)
   - Risk: May break existing clients

### Week 2
2. **FOCUS-003** (Medium Priority) - Clarify job cancellation
   - Impact: MEDIUM - Resource management
   - Effort: Unknown (depends on investigation)
   - Risk: Low

3. **FOCUS-001** (Low Priority) - Fix empty status
   - Impact: LOW - Cosmetic
   - Effort: Low (1-2 hours)
   - Risk: Very low

---

## Testing Checklist

After fixes are deployed, run:
```bash
# Run full test suite
pytest tests/integration/api/test_singlechannel_view_mapping.py -v

# Specific tests for each bug:
pytest tests/integration/api/test_singlechannel_view_mapping.py::test_configure_singlechannel_mapping -v  # FOCUS-001
pytest tests/integration/api/test_singlechannel_view_mapping.py::test_singlechannel_with_min_not_equal_max_should_fail -v  # FOCUS-002
pytest tests/integration/api/test_singlechannel_view_mapping.py::test_same_channel_multiple_requests_consistent_mapping -v  # FOCUS-003
```

---

## Contact
**Reporter**: QA Automation Team  
**Test Framework**: focus_server_automation  
**Test Suite**: SingleChannel View Mapping Integration Tests  
**Report Date**: 2025-10-12

