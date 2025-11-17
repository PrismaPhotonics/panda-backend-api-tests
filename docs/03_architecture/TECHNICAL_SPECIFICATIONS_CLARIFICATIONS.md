# Technical Specifications Clarifications - Focus Server & Infrastructure

**Date:** October 9, 2025  
**Source:** Development Team (via Roy)  
**Purpose:** Clarify technical requirements for Live/History test development

---

## 🎯 Overview

This document contains official clarifications from the development team regarding:
- RabbitMQ topology and queue naming conventions
- SLA requirements for production
- Smart Recorder integration patterns
- Partial results handling in history playback

**These specifications must be reflected in all integration tests.**

---

## 1️⃣ RabbitMQ Configuration & Topology

### Exchange Configuration

**Official Answer:**
> "There is only ONE exchange named `prisma`"  
> Mnemonic: *"There is no exchange except prisma, and different queues serve it"*

**Implications for Tests:**
- ✅ All RabbitMQ messages MUST be published to `prisma` exchange
- ❌ Do NOT create or expect other exchanges
- 🧪 Tests should validate exchange name is `prisma`

**Implementation:**
```python
# In baby_analyzer_mq_client.py and all MQ clients
EXCHANGE_NAME = "prisma"  # Only valid exchange

self.channel.exchange_declare(
    exchange="prisma",  # Hard-coded, never change
    exchange_type='topic',
    durable=True
)
```

---

### Queue Configuration

**Official Answer (Context-Dependent):**

| Component | Queue Behavior | Example |
|-----------|---------------|---------|
| **Recorder** | Specific named queue | `recorder_input` |
| **Jobs** | Dynamic pattern: `{job_id}_{suffix}` | `job_abc123_results` |
| **Focus Server** | No queue (publisher only) | N/A |

**Implications for Tests:**

1. **Recorder Tests:**
   ```python
   # Expect specific queue name
   queue_name = "recorder_input"
   ```

2. **Job Tests:**
   ```python
   # Dynamic queue based on job_id
   job_id = "test_job_12345"
   queue_name = f"{job_id}_results"  # or other suffix pattern
   ```

3. **Focus Server Tests:**
   ```python
   # Focus Server does NOT consume from queues
   # It only publishes to exchange with routing keys
   focus_server_api.publish_command(
       exchange="prisma",
       routing_key="baby_analyzer.commands.roi"
   )
   ```

**Test Validation:**
```python
def test_rabbitmq_topology():
    """Validate RabbitMQ topology matches specification."""
    # 1. Verify exchange exists and is named "prisma"
    assert rabbitmq_manager.exchange_exists("prisma")
    
    # 2. Verify no other exchanges exist (except defaults)
    exchanges = rabbitmq_manager.list_exchanges()
    custom_exchanges = [e for e in exchanges if not e.startswith("amq.")]
    assert custom_exchanges == ["prisma"], "Only 'prisma' exchange allowed"
    
    # 3. Focus Server should not have dedicated queue
    assert not rabbitmq_manager.queue_exists("focus_server_queue")
```

---

## 2️⃣ SLA Requirements & Timeouts

### gRPC Stream Timeout

**Official Answer:**
> "On backend we have gRPC timeout for live and history of **180 seconds**"

**Specification:**
- **Live Streams:** 180 seconds (3 minutes) max connection time
- **History Streams:** 180 seconds (3 minutes) max connection time
- **Note:** Noga (frontend) has retry timeouts for resending requests

**Implications for Tests:**

```python
# Test configuration
GRPC_TIMEOUT_SECONDS = 180

def test_grpc_stream_timeout_compliance():
    """Verify gRPC streams respect 180-second timeout."""
    start_time = time.time()
    
    with pytest.raises(grpc.RpcError) as exc:
        # Start stream and wait for timeout
        stream = focus_server_api.open_grpc_stream(task_id)
        for data in stream:
            if time.time() - start_time > 180:
                break
    
    elapsed = time.time() - start_time
    assert elapsed <= 180, f"Stream exceeded 180s timeout: {elapsed}s"
```

**Test Categories:**

1. **Normal Operation (< 180s):**
   ```python
   def test_grpc_stream_within_timeout():
       """Verify stream completes normally within timeout."""
       # Should complete successfully
   ```

2. **Long-Running Stream (approaching 180s):**
   ```python
   def test_grpc_stream_near_timeout():
       """Verify stream behavior near 180s boundary."""
       # Test graceful handling near timeout
   ```

3. **Timeout Exceeded:**
   ```python
   def test_grpc_stream_timeout_exceeded():
       """Verify proper error handling when timeout exceeded."""
       # Should raise timeout error
   ```

---

### Metadata Collection Time

**Official Answer:**
> "Metadata collect time is supposed to be **quick**" (no specific value given)

**Recommendation:**
Since no specific SLA was provided, propose reasonable thresholds based on best practices:

| Operation | Proposed SLA | Justification |
|-----------|--------------|---------------|
| GET `/live_metadata` | < 1 second | Simple metadata retrieval |
| GET `/metadata/{task_id}` | < 2 seconds | May require task lookup |
| GET `/sensors` | < 1 second | Static configuration data |

**Test Implementation:**
```python
@pytest.mark.performance
def test_metadata_collection_performance():
    """Verify metadata collection is 'quick' (< 1s)."""
    start_time = time.time()
    
    metadata = focus_server_api.get_live_metadata()
    
    elapsed = time.time() - start_time
    assert elapsed < 1.0, f"Metadata collection too slow: {elapsed}s"
    
    # Log performance for monitoring
    logger.info(f"Metadata collection time: {elapsed:.3f}s")
```

---

### Reconnect/Retry Timeouts

**Official Answer:**
> "Noga has some timeouts for resending requests" (frontend responsibility)

**Implications:**
- Backend (Focus Server) does NOT implement retry logic
- Frontend (Noga UI) handles reconnection and retries
- Tests should focus on backend idempotency, not retry behavior

**Test Focus:**
```python
def test_configure_endpoint_idempotency():
    """Verify POST /configure is idempotent for retries."""
    task_id = "idempotent_test_123"
    payload = {...}
    
    # Send same request twice
    response1 = focus_server_api.config_task(task_id, payload)
    response2 = focus_server_api.config_task(task_id, payload)
    
    # Should get same result (idempotent)
    assert response1.status == response2.status
```

---

## 3️⃣ Smart Recorder Integration

### Connection Protocol

**Official Answer:**
> "AMQP. It connects to the interrogator - all communication is AMQP"

**Architecture:**
```
[Fiber/DAS] → [Interrogator] ←--AMQP--→ [Smart Recorder] ←--AMQP--→ [RabbitMQ (prisma exchange)]
```

**Key Points:**
- Smart Recorder does NOT use gRPC Tap
- All data flow is through AMQP/RabbitMQ
- Interrogator is the data source (connected to fiber)

**Implications for Tests:**

1. **Do NOT test gRPC Tap for Smart Recorder:**
   ```python
   # ❌ WRONG - Smart Recorder doesn't use gRPC
   def test_smart_recorder_grpc_tap():
       pass  # Don't create this test
   ```

2. **Test AMQP integration instead:**
   ```python
   # ✅ CORRECT - Test AMQP message flow
   def test_smart_recorder_amqp_messages():
       """Verify Smart Recorder sends data via AMQP."""
       # Subscribe to recorder messages on 'prisma' exchange
       messages = rabbitmq_client.consume_messages(
           exchange="prisma",
           routing_key="recorder.data.*"
       )
       
       assert len(messages) > 0, "No AMQP messages from recorder"
   ```

3. **Test Interrogator connectivity (if accessible):**
   ```python
   def test_interrogator_connection():
       """Verify Interrogator is accessible via AMQP."""
       # Check if interrogator queue exists
       assert rabbitmq_manager.queue_exists("interrogator_input")
   ```

---

## 4️⃣ Partial Results in History Playback

### Current Behavior (Actual Implementation)

**Official Answer:**
> 1. **No recordings in time range → Fail-fast**  
>    Returns error immediately if no recordings exist
>
> 2. **Recordings with gaps → Partial results with holes**  
>    Returns available data with gaps in the middle

**Detailed Specification:**

| Scenario | Behavior | HTTP Status | Response |
|----------|----------|-------------|----------|
| No recordings in range | Fail-fast | 400 Bad Request | Error message |
| Complete coverage | Full results | 200/201 | All data |
| Partial coverage (gaps) | Partial results | 200/201 | Data with temporal holes |

**There is NO "Strict" vs "Best-Effort" mode** - only the behavior above.

---

### Test Scenarios

#### Scenario 1: No Recordings → Fail-Fast

```python
@pytest.mark.integration
@pytest.mark.history
def test_history_no_recordings_fails_fast():
    """
    Verify fail-fast when no recordings exist in time range.
    
    Expected: 400 Bad Request with clear error message
    """
    # Request time range with no recordings
    start_time = "250101000000"  # Year 2501 - no data
    end_time = "250101010000"
    
    payload = ConfigTaskRequest(
        start_time=start_time,
        end_time=end_time,
        ...
    )
    
    with pytest.raises(APIError) as exc:
        focus_server_api.config_task(task_id, payload)
    
    # Should return 400 (bad request - no data available)
    assert "400" in str(exc.value)
    assert "no recordings" in str(exc.value).lower()
```

---

#### Scenario 2: Complete Coverage → Full Results

```python
@pytest.mark.integration
@pytest.mark.history
def test_history_complete_coverage_full_results():
    """
    Verify full results when recordings cover entire time range.
    
    Expected: 200/201 with complete data stream
    """
    # Request time range with full coverage
    recordings = storage_manager.get_recordings()
    start_time = recordings[0].start_time
    end_time = recordings[0].end_time
    
    response = focus_server_api.config_task(task_id, payload)
    
    assert response.status == "Config received successfully"
    
    # Verify waterfall data is continuous
    waterfall_data = focus_server_api.get_waterfall(task_id, row_count=100)
    assert waterfall_data.status_code == 201
    assert len(waterfall_data.data) > 0
    
    # Verify no temporal gaps
    timestamps = [row.startTimestamp for block in waterfall_data.data 
                  for row in block.rows]
    gaps = find_temporal_gaps(timestamps, threshold_ms=2000)
    assert len(gaps) == 0, f"Unexpected gaps in continuous recording: {gaps}"
```

---

#### Scenario 3: Partial Coverage → Data with Holes

```python
@pytest.mark.integration
@pytest.mark.history
def test_history_partial_coverage_returns_data_with_holes():
    """
    Verify partial results with holes when recordings have gaps.
    
    Expected: 200/201 with data + temporal gaps
    """
    # Create test scenario with known gap
    # Recording 1: 10:00:00 - 10:05:00
    # GAP:        10:05:00 - 10:10:00 (5 minutes missing)
    # Recording 2: 10:10:00 - 10:15:00
    
    start_time = "251009100000"  # 10:00:00
    end_time = "251009101500"    # 10:15:00
    
    payload = ConfigTaskRequest(
        start_time=start_time,
        end_time=end_time,
        ...
    )
    
    response = focus_server_api.config_task(task_id, payload)
    
    # Should succeed despite gap
    assert response.status == "Config received successfully"
    
    # Collect all waterfall data
    all_rows = []
    for _ in range(10):
        data = focus_server_api.get_waterfall(task_id, row_count=50)
        if data.status_code == 201 and data.data:
            for block in data.data:
                all_rows.extend(block.rows)
        elif data.status_code == 208:  # End of stream
            break
        time.sleep(1)
    
    # Verify we got data from both recordings
    assert len(all_rows) > 0, "No data received"
    
    # Verify temporal gap exists (expected behavior)
    timestamps = [row.startTimestamp for row in all_rows]
    timestamps.sort()
    
    gaps = find_temporal_gaps(timestamps, threshold_ms=60000)  # 1 minute threshold
    assert len(gaps) > 0, "Expected temporal gap not found"
    
    logger.info(f"✅ Found expected temporal gap: {gaps[0]}")
```

**Helper Function:**
```python
def find_temporal_gaps(timestamps: List[int], threshold_ms: int = 5000) -> List[Dict]:
    """
    Find temporal gaps in timestamp sequence.
    
    Args:
        timestamps: List of epoch millisecond timestamps
        threshold_ms: Gap threshold in milliseconds
        
    Returns:
        List of gaps: [{"start": ts1, "end": ts2, "duration_ms": delta}, ...]
    """
    if len(timestamps) < 2:
        return []
    
    gaps = []
    sorted_ts = sorted(timestamps)
    
    for i in range(len(sorted_ts) - 1):
        delta = sorted_ts[i + 1] - sorted_ts[i]
        if delta > threshold_ms:
            gaps.append({
                "start": sorted_ts[i],
                "end": sorted_ts[i + 1],
                "duration_ms": delta,
                "duration_readable": f"{delta / 1000:.1f}s"
            })
    
    return gaps
```

---

#### Scenario 4: Edge Case - Single Recording at Start

```python
@pytest.mark.integration
@pytest.mark.history
def test_history_partial_at_start_only():
    """
    Test scenario where only start of time range has recordings.
    
    Timeline:
    - Recording: 10:00 - 10:05
    - Requested: 10:00 - 10:30
    - Expected: Data until 10:05, then no more data (EOS)
    """
    # Implementation similar to scenario 3
```

---

#### Scenario 5: Edge Case - Single Recording in Middle

```python
@pytest.mark.integration
@pytest.mark.history
def test_history_partial_in_middle_only():
    """
    Test scenario where only middle of time range has recordings.
    
    Timeline:
    - Requested: 10:00 - 10:30
    - Recording: 10:10 - 10:15 (middle only)
    - Expected: Data from 10:10-10:15, then EOS
    """
    # Implementation similar to scenario 3
```

---

### Decision on "Strict" vs "Best-Effort"

**Official Answer:**
> No explicit "Strict" or "Best-Effort" modes exist.

**Current Behavior is "Best-Effort" by Default:**
- Returns whatever data is available
- Does not fail if gaps exist
- Only fails if NO data exists at all

**Recommendation:**
Document this as the official behavior and add parameter for future:

```python
class ConfigTaskRequest(BaseModel):
    # Existing fields...
    
    # Future enhancement (not implemented yet):
    partial_results_mode: Optional[Literal["best_effort", "strict"]] = Field(
        default="best_effort",
        description=(
            "How to handle missing recordings:\n"
            "- best_effort: Return partial results with gaps (default)\n"
            "- strict: Fail if any gaps detected (not implemented)"
        )
    )
```

---

## 📋 Summary of Required Test Updates

### High Priority (Implement Immediately)

1. ✅ **Update RabbitMQ Configuration Tests**
   - Verify exchange name is "prisma" (only)
   - Update queue name patterns for jobs
   - Remove Focus Server queue expectations

2. ✅ **Add gRPC Timeout Tests**
   - Test 180-second timeout compliance
   - Test behavior near timeout boundary
   - Test timeout error handling

3. ✅ **Add Partial Results Tests**
   - Test fail-fast when no recordings
   - Test partial results with gaps
   - Test edge cases (start-only, middle-only)

### Medium Priority (Next Sprint)

4. 🔄 **Add Performance Tests**
   - Metadata collection time (< 1s target)
   - Document actual measurements
   - Set up performance monitoring

5. 🔄 **Update Smart Recorder Tests**
   - Remove any gRPC tap tests (not applicable)
   - Add AMQP message flow tests
   - Test interrogator connectivity

### Low Priority (Future Enhancement)

6. 📝 **Document Frontend Retry Logic**
   - Clarify Noga's retry timeouts
   - Document expected retry behavior
   - Ensure backend idempotency

---

## 🔗 References

- **RabbitMQ Documentation:** `docs/COMPLETE_RABBITMQ_JOURNEY.md`
- **gRPC Stream Spec:** (To be created)
- **Storage Manager API:** (To be documented)
- **Test Suite:** `tests/integration/api/`

---

## 📝 Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-09 | Initial specifications from dev team | QA Architect |
| 2025-10-09 | Added test scenarios and examples | QA Architect |

---

**Document Owner:** QA Automation Architect  
**Reviewers:** Roy (Dev Team), Focus Server Team  
**Status:** Draft - Pending Review  
**Next Review:** After implementation of priority 1 tests

