# Team Responses - Required Test Updates & Action Items

**Date:** October 9, 2025  
**Source:** Development Team (via Roy)  
**Purpose:** Quick reference for required test updates based on technical clarifications

---

## 🎯 Quick Summary - What Changed?

Received 4 critical technical clarifications that impact test implementation:

1. **RabbitMQ:** Only `prisma` exchange, variable queues, Focus Server has NO queue
2. **SLA:** 180s for gRPC streams, "fast" for metadata (no specific value)
3. **Smart Recorder:** AMQP only (NOT gRPC Tap)
4. **Partial Results:** Fail-fast if no data, return with gaps if partial data

---

## 1️⃣ RabbitMQ: One Exchange, Variable Queues

### What We Learned:
- **Exchange:** Only `prisma` (and nothing else!)
- **Queues:** Depends on component:
  - Recorder: Has specific queue
  - Jobs: Dynamic pattern `{job_id}_{suffix}`
  - **Focus Server: NO queue at all!** (publisher only)

### Required Test Fixes:
```python
# ❌ BEFORE - Wrong assumptions
exchange = "baby_analyzer_commands"  # Wrong!
queue = "focus_server_queue"  # Doesn't exist!

# ✅ AFTER - Correct
exchange = "prisma"  # Only this!
# Focus Server has no queue, only publishes messages
```

### New Test Required:
```python
def test_rabbitmq_only_prisma_exchange_exists():
    """Verify only 'prisma' exchange exists."""
    exchanges = rabbitmq_manager.list_exchanges()
    custom = [e for e in exchanges if not e.startswith("amq.")]
    assert custom == ["prisma"], f"Unauthorized exchanges found: {custom}"
```

---

## 2️⃣ SLA: 180 Seconds for Streams, "Fast" for Metadata

### What We Learned:
- **gRPC timeout:** 180 seconds (3 minutes) - both live and history
- **Metadata:** Should be "fast" (no exact value provided)
- **Retry:** Handled by Noga (Frontend), not Backend

### Required New Tests:

**Test #1: gRPC Stream Timeout**
```python
def test_grpc_stream_respects_180_second_timeout():
    """Verify gRPC streams don't exceed 180 seconds."""
    start = time.time()
    
    with pytest.raises(grpc.RpcError):
        stream = focus_server_api.open_grpc_stream(task_id)
        for data in stream:
            if time.time() - start > 180:
                break
    
    elapsed = time.time() - start
    assert elapsed <= 180, f"Stream exceeded timeout: {elapsed}s"
```

**Test #2: Fast Metadata Collection**
```python
def test_metadata_collection_is_fast():
    """Verify metadata collection is fast (< 1 second)."""
    start = time.time()
    metadata = focus_server_api.get_live_metadata()
    elapsed = time.time() - start
    
    assert elapsed < 1.0, f"Metadata too slow: {elapsed}s"
```

---

## 3️⃣ Smart Recorder: AMQP Only, Not gRPC!

### What We Learned:
- Smart Recorder connects to **Interrogator** via **AMQP only**
- Does **NOT** use gRPC Tap
- All communication through RabbitMQ

### Required Changes:
```python
# ❌ DELETE - Smart Recorder doesn't use gRPC
def test_smart_recorder_grpc_tap():
    pass  # Delete this test!

# ✅ ADD - Test AMQP instead
def test_smart_recorder_sends_amqp_messages():
    """Verify Smart Recorder sends data via AMQP."""
    messages = rabbitmq_client.consume(
        exchange="prisma",
        routing_key="recorder.data.*"
    )
    assert len(messages) > 0
```

---

## 4️⃣ Partial Results in History: Fail-Fast or Holes

### What We Learned:
**NO "Strict" vs "Best-Effort" modes!** Only 2 scenarios:

| Scenario | Behavior | HTTP Status |
|----------|----------|-------------|
| **No recordings at all** | Fail-fast → error | 400 Bad Request |
| **Recordings with gaps** | Return data + holes | 200/201 |

### Required New Tests:

**Test #1: No Data → 400 Error**
```python
def test_history_no_recordings_returns_400():
    """No recordings at all → should return 400."""
    start_time = "250101000000"  # Year 2501 - no data
    end_time = "250101010000"
    
    with pytest.raises(APIError) as exc:
        focus_server_api.config_task(task_id, payload)
    
    assert "400" in str(exc.value)
    assert "no recordings" in str(exc.value).lower()
```

**Test #2: Gaps → Return Partial Data**
```python
def test_history_partial_coverage_returns_data_with_gaps():
    """Has recordings with gaps → return available data."""
    # Scenario:
    # Recording 1: 10:00 - 10:05
    # Gap:         10:05 - 10:10 (5 minutes missing)
    # Recording 2: 10:10 - 10:15
    
    response = focus_server_api.config_task(task_id, payload)
    assert response.status == "Config received successfully"
    
    # Collect all data
    all_rows = collect_all_waterfall_rows(task_id)
    
    # Verify we got data
    assert len(all_rows) > 0
    
    # Verify gap exists (expected behavior!)
    gaps = find_temporal_gaps([row.startTimestamp for row in all_rows])
    assert len(gaps) > 0, "Expected to find gap"
    
    logger.info(f"✅ Found expected gap: {gaps[0]['duration_readable']}")
```

**Helper Function:**
```python
def find_temporal_gaps(timestamps: List[int], threshold_ms: int = 60000):
    """Find gaps in timestamp sequence."""
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

## 📋 TODO List - Priority Actions

### 🔴 High Priority (Today/Tomorrow)

- [ ] **Fix RabbitMQ configuration in all tests**
  - Change exchange to `prisma`
  - Remove Focus Server queue assumptions

- [ ] **Create 3 new Partial Results tests:**
  - Test #1: No data → 400
  - Test #2: Has gaps → return with holes
  - Test #3: Edge case (data at start only)

- [ ] **Add gRPC timeout test (180 seconds)**

### 🟠 Medium Priority (This Week)

- [ ] **Add Metadata collection time test**
  - Propose threshold: < 1 second
  - Document actual measurements

- [ ] **Update Smart Recorder tests**
  - Delete gRPC tap tests
  - Add AMQP message flow tests

### 🟡 Low Priority (Future)

- [ ] **Document Frontend retry logic**
- [ ] **Add performance benchmarks**

---

## 📄 Documents Created

1. **`docs/TECHNICAL_SPECIFICATIONS_CLARIFICATIONS.md`** - Full technical specification
   - All team clarifications
   - Complete code examples for every test
   - Architecture and SLA details

2. **`TEAM_RESPONSES_ACTION_ITEMS.md`** - This document
   - Quick summary of changes
   - TODO list for test development

---

## 💡 Development Tips

### Tip #1: Remember the mnemonic
> "There is no exchange except prisma, and different queues serve it"

### Tip #2: Focus Server has NO queue
If you're writing a Focus Server test and see a queue - it's wrong!

### Tip #3: Partial Results = Best-Effort
This is the default. No parameter needed.

### Tip #4: gRPC = 180 seconds
If test exceeds 3 minutes, something is wrong.

---

**Created By:** QA Automation Architect  
**Based On:** Responses from Roy and Development Team  
**Status:** Ready for implementation

