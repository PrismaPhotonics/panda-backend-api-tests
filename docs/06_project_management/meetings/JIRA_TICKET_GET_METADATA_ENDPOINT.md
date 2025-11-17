# 🎫 Jira Ticket Template - GET /metadata/{job_id} Restoration

**Created:** 27 October 2025  
**Purpose:** Backlog item from meeting decision (PZ-13756)  
**Priority:** Medium  
**Type:** Bug / Missing Feature

---

## Ticket Information

**Title:**  
```
Restore/Implement GET /metadata/{job_id} endpoint
```

**Type:** Bug (if existed before) / Story (if new feature)

**Priority:** Medium

**Component:** Focus Server API

**Labels:** `api`, `endpoints`, `backlog`, `PZ-13756`

---

## Description

### Summary

The `GET /metadata/{job_id}` endpoint is currently **not available** in the Focus Server API. This endpoint is needed for querying job status and metadata after job creation.

### Background

During the meeting for PZ-13756 (Scope Refinement), it was decided to add this endpoint to the **backlog** for future implementation.

**Current Situation:**
- ✅ `POST /configure` creates jobs and returns initial metadata
- ❌ `GET /metadata/{job_id}` not available to query job status later
- ⚠️  No way to retrieve job metadata if initial response is lost
- ⚠️  No way to check if job is still running dynamically

**Impact:**
- Cannot query job status after creation
- Cannot retrieve metadata if configure response lost
- Cannot monitor job progress dynamically
- Client must store all metadata from initial response

---

## Expected Behavior

### Endpoint Specification

**Method:** `GET`  
**Path:** `/metadata/{job_id}`  
**Parameters:**
- `job_id` (path, required): The job ID returned from `/configure`

**Response (Success - HTTP 200):**
```json
{
  "status": "running",
  "job_id": "abc123",
  "stream_port": 50051,
  "stream_url": "10.10.100.100",
  "view_type": 0,
  "frequencies_list": [0.0, 1.0, ...],
  "lines_dt": 123.0,
  "channel_to_stream_index": {"1": 0, "2": 1, ...},
  "stream_amount": 2,
  "frequencies_amount": 500,
  "channel_amount": 50,
  "metadata": {
    "dx": 1.02,
    "prr": 2000,
    "fiber_start_meters": 0,
    "fiber_length_meters": 5000,
    "sw_version": "1.0.0"
  }
}
```

**Response (Not Found - HTTP 404):**
```json
{
  "detail": "Job not found: abc123"
}
```

**Response (Job Completed - HTTP 200):**
```json
{
  "status": "completed",
  "job_id": "abc123",
  ...
}
```

### Use Cases

**Use Case 1: Status Polling**
```python
# Frontend polls for job status
while True:
    metadata = api.get_job_metadata(job_id)
    if metadata.status == "completed":
        break
    time.sleep(1)
```

**Use Case 2: Metadata Recovery**
```python
# User refreshes page, needs to reconnect to job
job_id = get_from_session()
metadata = api.get_job_metadata(job_id)
reconnect_to_stream(metadata.stream_url, metadata.stream_port)
```

**Use Case 3: Job Monitoring**
```python
# Admin dashboard shows all active jobs
for job_id in active_jobs:
    metadata = api.get_job_metadata(job_id)
    display_job_status(metadata)
```

---

## Current Workaround

### What We Do Now

1. **Store metadata from POST /configure response**
   ```python
   config_response = api.configure_streaming_job(payload)
   
   # Store ALL metadata locally
   session.store('job_id', config_response.job_id)
   session.store('stream_port', config_response.stream_port)
   session.store('stream_url', config_response.stream_url)
   # ... store everything
   ```

2. **Cannot query dynamic status updates**
   - No way to check if job is still running
   - No way to detect if job failed
   - Must assume job is alive based on stream connectivity

3. **Cannot recover lost metadata**
   - If page refreshes, all metadata lost
   - User must create new job (wasteful)

### Limitations

- ❌ No job status monitoring
- ❌ No metadata recovery
- ❌ No job lifecycle tracking
- ❌ Poor user experience if connection lost

---

## Implementation Requirements

### API Endpoint

**Path:** `/metadata/{job_id}`  
**Method:** `GET`

### Backend Requirements

1. **Job Registry**
   - Store job metadata in memory/cache
   - Associate metadata with job_id
   - Implement TTL for cleanup

2. **Status Tracking**
   - Track job status (running/completed/failed)
   - Update status when job completes/fails
   - Clean up after TTL expires

3. **Error Handling**
   - Return 404 if job_id not found
   - Return 200 with status if found
   - Handle expired jobs gracefully

### Testing Requirements

1. **Happy Path**
   - Create job
   - Query metadata
   - Verify response matches original

2. **Error Cases**
   - Query non-existent job_id → 404
   - Query after TTL expiration → 404 or 410

3. **Edge Cases**
   - Query during job execution
   - Query after job completion
   - Query after job cancellation

---

## Acceptance Criteria

### Must Have:
- [ ] Endpoint returns job metadata for active jobs
- [ ] Endpoint returns 404 for unknown job_id
- [ ] Metadata includes all fields from /configure response
- [ ] Endpoint is documented in OpenAPI spec
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] API documentation updated

### Nice to Have:
- [ ] Status field indicates job lifecycle state
- [ ] TTL configurable
- [ ] Cleanup mechanism for old jobs
- [ ] Metrics for endpoint usage

---

## Test Plan

### Unit Tests

```python
def test_get_metadata_returns_correct_data():
    """Validate metadata matches job configuration."""
    pass

def test_get_metadata_returns_404_for_unknown_job():
    """Validate 404 for non-existent job_id."""
    pass
```

### Integration Tests

```python
@pytest.mark.backlog
@pytest.mark.skip(reason="Endpoint not implemented - PZ-XXXXX")
def test_get_job_metadata_endpoint():
    """
    Test: GET /metadata/{job_id}
    
    Status: ⏳ PENDING IMPLEMENTATION
    Jira: PZ-XXXXX
    
    Will be enabled once endpoint is restored/implemented.
    """
    pass
```

---

## Related Documentation

- **API Endpoints:** `documentation/testing/FOCUS_SERVER_API_ENDPOINTS.md`
- **Meeting Notes:** `documentation/meetings/SCOPE_REFINEMENT_ACTION_PLAN.md`
- **Scope Refinement:** `documentation/meetings/TEST_FILES_ANALYSIS_SCOPE_REFINEMENT.md`

---

## Estimated Effort

- **Backend Development:** 4-6 hours
- **Testing:** 2-3 hours
- **Documentation:** 1 hour
- **Total:** ~8-10 hours (1-1.5 days)

---

**Status:** ⏳ Backlog  
**Next Action:** Create Jira ticket with this template

