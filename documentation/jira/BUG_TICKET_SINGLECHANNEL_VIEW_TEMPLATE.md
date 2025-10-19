# Bug Ticket Template: SingleChannel View Issues

## 📋 Bug Ticket Template

Use this template when `test_configure_singlechannel_mapping` or related tests fail.

---

## 🐛 Bug #1: Incorrect stream_amount

### Title
`[FOCUS-XXX] SingleChannel view returns incorrect stream_amount`

### Environment
- **Environment**: Staging / Production / Dev
- **Focus Server Version**: {version}
- **Date**: {date}

### Test Case
**Automated Test**: `tests/integration/api/test_singlechannel_view_mapping.py::test_configure_singlechannel_mapping`

**Test Requirement**: FOCUS-API-VIEWTYPE

### Priority & Impact
- **Priority**: Medium
- **Component**: focus-server, api, view-type, singlechannel
- **Impact**: API contract violation - affects UI rendering

### Description

**Expected Behavior**:
For `view_type=SINGLECHANNEL`, the API must return:
```json
{
  "stream_amount": 1
}
```

**Actual Behavior**:
```json
{
  "stream_amount": {actual_value}
}
```

### Steps to Reproduce

1. Send POST request to `/configure`
2. Request payload:
   ```json
   {
     "displayTimeAxisDuration": 10,
     "nfftSelection": 1024,
     "displayInfo": { "height": 1000 },
     "channels": { "min": 7, "max": 7 },
     "frequencyRange": { "min": 0, "max": 500 },
     "start_time": null,
     "end_time": null,
     "view_type": 1
   }
   ```
3. Observe response `stream_amount`
4. **Expected**: `stream_amount = 1`
5. **Actual**: `stream_amount = {actual}`

### Root Cause Analysis (Developer to fill)

**Hypothesis**:
- [ ] view_type not properly handled in backend
- [ ] Stream creation logic treats SINGLECHANNEL as MULTICHANNEL
- [ ] Configuration mismatch

**Affected Code**:
- `{path_to_backend_file}`
- `{function_or_class}`

### Suggested Fix

```python
# Pseudocode
if view_type == ViewType.SINGLECHANNEL:
    stream_amount = 1  # Force single stream
    # Create only one stream regardless of channel count
```

### Verification

After fix, run:
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py::test_configure_singlechannel_mapping -v
```

Expected: ✅ TEST PASSED

---

## 🐛 Bug #2: Incorrect channel_to_stream_index mapping

### Title
`[FOCUS-XXX] SingleChannel view has incorrect channel mapping`

### Environment
- **Environment**: {environment}
- **Focus Server Version**: {version}

### Test Case
**Automated Test**: `tests/integration/api/test_singlechannel_view_mapping.py::test_configure_singlechannel_mapping`

### Priority & Impact
- **Priority**: Medium
- **Component**: focus-server, api, channel-mapping
- **Impact**: Data routing error - wrong channel data sent to UI

### Description

**Expected Behavior**:
For `channels: {min: 7, max: 7}` with `view_type=SINGLECHANNEL`:
```json
{
  "channel_to_stream_index": {
    "7": 0
  }
}
```

**Actual Behavior**:
```json
{
  "channel_to_stream_index": {
    {actual_mapping}
  }
}
```

### Possible Issues

1. **Missing channel**: Channel "7" not in mapping
   ```json
   "channel_to_stream_index": {}  // Empty!
   ```

2. **Wrong stream index**: Channel maps to wrong stream
   ```json
   "channel_to_stream_index": {
     "7": 1  // Should be 0
   }
   ```

3. **Multiple entries**: More than one channel in mapping
   ```json
   "channel_to_stream_index": {
     "7": 0,
     "8": 0  // Unexpected!
   }
   ```

### Steps to Reproduce

1. Send POST request to `/configure` with payload above
2. Check `response.channel_to_stream_index`
3. Verify:
   - ✅ Exactly 1 entry
   - ✅ Key is "7"
   - ✅ Value is 0

### Suggested Fix

```python
# Pseudocode
if view_type == ViewType.SINGLECHANNEL:
    requested_channel = channels.min  # Should equal channels.max
    channel_to_stream_index = {
        str(requested_channel): 0  # Always map to stream 0
    }
```

### Verification

```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py::test_configure_singlechannel_mapping -v
```

---

## 🐛 Bug #3: Backend channel process inconsistency

### Title
`[FOCUS-XXX] Same channel in multiple requests produces inconsistent mappings`

### Environment
- **Environment**: {environment}

### Test Case
**Automated Test**: `tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelBackendConsistency::test_same_channel_multiple_requests_consistent_mapping`

**Developer Suggestion**: "check in the BE if it's the same channel process"

### Priority & Impact
- **Priority**: High
- **Component**: focus-server, backend, channel-processing
- **Impact**: Data inconsistency - same channel behaves differently across requests

### Description

**Expected Behavior**:
Requesting the same channel (e.g., channel 7) multiple times should produce **consistent** results:

**Request #1**:
```json
{
  "channels": { "min": 7, "max": 7 },
  "view_type": 1
}
→ Response: { "channel_to_stream_index": { "7": 0 } }
```

**Request #2** (same channel):
```json
{
  "channels": { "min": 7, "max": 7 },
  "view_type": 1
}
→ Response: { "channel_to_stream_index": { "7": 0 } }  // Same mapping!
```

**Actual Behavior**:
Request #1: `{ "7": 0 }`  
Request #2: `{ "7": 1 }` ← **Inconsistent!**

### Root Cause Analysis

**Hypothesis**:
- [ ] Backend assigns stream indices incrementally without checking channel
- [ ] No caching/reuse of channel processes
- [ ] Stream pool management issue

**Backend Check Required**:
> As suggested: "check in the BE if it's the same channel process"

Verify that:
1. Same channel → same backend process
2. Different channels → independent processes
3. Process assignment is deterministic

### Suggested Fix

```python
# Pseudocode
class ChannelProcessManager:
    def get_or_create_process(self, channel_num, view_type):
        if view_type == ViewType.SINGLECHANNEL:
            # For SINGLECHANNEL, always use stream index 0
            return StreamIndex(0)
        
        # For MULTICHANNEL, use deterministic mapping
        return self._get_channel_stream_index(channel_num)
```

### Verification

```bash
# Run consistency test
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelBackendConsistency -v
```

---

## 🐛 Bug #4: channel_amount mismatch

### Title
`[FOCUS-XXX] SingleChannel view returns incorrect channel_amount`

### Environment
- **Environment**: {environment}

### Test Case
**Automated Test**: `tests/integration/api/test_singlechannel_view_mapping.py::test_configure_singlechannel_mapping`

### Priority & Impact
- **Priority**: Low
- **Component**: focus-server, api, metadata
- **Impact**: Metadata inconsistency

### Description

**Expected Behavior**:
```json
{
  "channel_amount": 1,
  "stream_amount": 1,
  "channel_to_stream_index": { "7": 0 }
}
```

**Actual Behavior**:
```json
{
  "channel_amount": {actual_value},  // Should be 1
  "stream_amount": 1,
  "channel_to_stream_index": { "7": 0 }
}
```

### Suggested Fix

```python
if view_type == ViewType.SINGLECHANNEL:
    channel_amount = 1  # Always 1 for single channel
```

---

## 📊 Debugging Checklist

When investigating SingleChannel view issues, check:

### Backend
- [ ] `view_type` enum value correctly parsed (1 = SINGLECHANNEL)
- [ ] Stream creation logic respects `view_type`
- [ ] Channel mapping logic is 1:1 for SINGLECHANNEL
- [ ] Stream index is 0-based (not 1-based)
- [ ] No stream pooling conflicts

### Request Processing
- [ ] Request payload validation accepts min=max
- [ ] `channels.min` and `channels.max` correctly read
- [ ] No default fallback to MULTICHANNEL

### Response Generation
- [ ] `stream_amount` set to 1
- [ ] `channel_to_stream_index` has exactly 1 entry
- [ ] `channel_amount` matches `stream_amount`
- [ ] Correct stream index in mapping (0, not 1)

### Logging (for debugging)
- [ ] Log received `view_type` value
- [ ] Log channel selection (min, max)
- [ ] Log stream creation count
- [ ] Log final mapping

---

## 🧪 Manual Testing Procedure

### Test Tool: Postman / curl

```bash
# Test SingleChannel view
curl -X POST http://localhost:5000/configure \
  -H "Content-Type: application/json" \
  -d '{
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": { "height": 1000 },
    "channels": { "min": 7, "max": 7 },
    "frequencyRange": { "min": 0, "max": 500 },
    "start_time": null,
    "end_time": null,
    "view_type": 1
  }'
```

### Expected Response
```json
{
  "status": "success",
  "stream_amount": 1,              ← Must be 1
  "channel_to_stream_index": {     ← Must have 1 entry
    "7": 0                         ← Must map to 0
  },
  "channel_amount": 1,             ← Must be 1
  "job_id": "...",
  "view_type": 1
}
```

### Validation Script
```python
import requests

response = requests.post("http://localhost:5000/configure", json={
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": { "height": 1000 },
    "channels": { "min": 7, "max": 7 },
    "frequencyRange": { "min": 0, "max": 500 },
    "start_time": None,
    "end_time": None,
    "view_type": 1
})

data = response.json()

# Validate
assert data["stream_amount"] == 1, f"Expected 1, got {data['stream_amount']}"
assert len(data["channel_to_stream_index"]) == 1, "Expected 1 mapping entry"
assert "7" in data["channel_to_stream_index"], "Channel 7 missing"
assert data["channel_to_stream_index"]["7"] == 0, "Wrong stream index"

print("✅ All validations passed!")
```

---

## 📞 Escalation Path

1. **QA Team**: Validates bug with automated test
2. **Developer**: Investigates backend channel process
3. **Architect**: Reviews stream management design if needed

---

## ✅ Definition of Done

Bug is resolved when:

1. ✅ All SingleChannel tests pass
   ```bash
   pytest tests/integration/api/test_singlechannel_view_mapping.py -v
   ```

2. ✅ Manual testing confirms correct behavior

3. ✅ Code review approved

4. ✅ Regression test added (if new scenario found)

---

**Template Version**: 1.0  
**Last Updated**: 2025-10-12  
**Owner**: QA Automation Architect

