# SingleChannel View Mapping Test Guide

## 📋 Overview

This document describes the comprehensive test suite for the **SingleChannel view type** (view_type=1) in Focus Server.

### Test Objective
Validate that `view_type=SINGLECHANNEL` returns:
- ✅ **Exactly one stream** (`stream_amount=1`)
- ✅ **Single channel mapping** entry in `channel_to_stream_index`
- ✅ **Correct 1:1 mapping** (requested channel → stream index 0)
- ✅ **No extra channels** or stray mappings

### Requirements
- **Requirement ID**: FOCUS-API-VIEWTYPE
- **Component**: focus-server, api, view-type, singlechannel
- **Priority**: Medium

---

## 🎯 Test Coverage

### 1. Happy Path Tests (`TestSingleChannelViewHappyPath`)

| Test Name | Description | Expected Behavior |
|-----------|-------------|-------------------|
| `test_configure_singlechannel_mapping` | Primary test for channel 7 mapping | `stream_amount=1`, `channel_to_stream_index={"7": 0}` |
| `test_configure_singlechannel_channel_1` | First channel (boundary test) | `stream_amount=1`, `channel_to_stream_index={"1": 0}` |
| `test_configure_singlechannel_channel_100` | High channel number test | `stream_amount=1`, `channel_to_stream_index={"100": 0}` |
| `test_singlechannel_vs_multichannel_comparison` | Compare SINGLECHANNEL vs MULTICHANNEL | SINGLECHANNEL always returns 1 stream |

### 2. Edge Cases Tests (`TestSingleChannelViewEdgeCases`)

| Test Name | Description | Expected Behavior |
|-----------|-------------|-------------------|
| `test_singlechannel_with_min_not_equal_max_should_fail` | Test with `min != max` | ValidationError or stream_amount still = 1 |
| `test_singlechannel_with_zero_channel` | Channel 0 boundary test | ValidationError or correct mapping |
| `test_singlechannel_with_different_frequency_ranges` | Various frequency ranges | stream_amount=1 regardless of freq range |

### 3. Error Handling Tests (`TestSingleChannelViewErrorHandling`)

| Test Name | Description | Expected Behavior |
|-----------|-------------|-------------------|
| `test_singlechannel_with_invalid_nfft` | Invalid NFFT (0) | ValidationError raised |
| `test_singlechannel_with_invalid_height` | Invalid height (0) | ValidationError raised |
| `test_singlechannel_with_invalid_frequency_range` | Invalid freq range (min > max) | ValidationError raised |

### 4. Backend Consistency Tests (`TestSingleChannelBackendConsistency`) ⭐

As suggested by the developer: **"check in the BE if it's the same channel process"**

| Test Name | Description | Expected Behavior |
|-----------|-------------|-------------------|
| `test_same_channel_multiple_requests_consistent_mapping` | Same channel in multiple requests | Consistent mapping across requests |
| `test_different_channels_different_mappings` | Different channels processed independently | Each channel maps to stream 0 in its own job |

---

## 🚀 Running the Tests

### Run All SingleChannel Tests
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py -v
```

### Run Specific Test Class
```bash
# Happy path tests only
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewHappyPath -v

# Edge cases only
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewEdgeCases -v

# Error handling only
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewErrorHandling -v

# Backend consistency tests only
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelBackendConsistency -v
```

### Run Specific Test
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewHappyPath::test_configure_singlechannel_mapping -v
```

### Run with Detailed Logging
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py -v -s --log-cli-level=INFO
```

### Run with Allure Reporting
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py --alluredir=reports/allure-results
allure serve reports/allure-results
```

---

## 📊 Test Data

### Primary Test Payload (Channel 7)
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

### Expected Response Structure
```json
{
  "status": "success",
  "stream_amount": 1,
  "channel_to_stream_index": { "7": 0 },
  "channel_amount": 1,
  "frequencies_list": [...],
  "lines_dt": 0.1,
  "job_id": "...",
  "frequencies_amount": ...,
  "stream_port": 50051,
  "stream_url": "...",
  "view_type": 1
}
```

---

## 🔍 Key Assertions

Each test validates the following critical assertions:

### 1. Stream Amount
```python
assert response.stream_amount == 1, (
    f"Expected stream_amount=1 for SINGLECHANNEL, got {response.stream_amount}"
)
```

### 2. Mapping Count
```python
assert len(response.channel_to_stream_index) == 1, (
    f"Expected exactly 1 channel mapping, got {len(response.channel_to_stream_index)}"
)
```

### 3. Channel Presence
```python
assert "7" in response.channel_to_stream_index, (
    f"Expected channel '7' in mapping, got keys: {list(response.channel_to_stream_index.keys())}"
)
```

### 4. Stream Index
```python
assert response.channel_to_stream_index["7"] == 0, (
    f"Expected channel '7' to map to stream 0, got {response.channel_to_stream_index['7']}"
)
```

### 5. Channel Amount
```python
assert response.channel_amount == 1, (
    f"Expected channel_amount=1 for single channel, got {response.channel_amount}"
)
```

---

## 🐛 Bug Ticket Template

If a test fails, use this template to create a bug ticket:

### Bug Title
`[FOCUS-XXX] SingleChannel view mapping failure - {specific_issue}`

### Description
**Test Case**: `test_configure_singlechannel_mapping`

**Environment**: {Dev/Staging/Production}

**Expected Behavior**:
- `stream_amount` should be `1`
- `channel_to_stream_index` should contain exactly one entry
- Channel mapping should be 1:1 (channel N → stream 0)

**Actual Behavior**:
- `stream_amount`: {actual_value}
- `channel_to_stream_index`: {actual_mapping}
- {specific_failure_description}

**Steps to Reproduce**:
1. Send POST request to `/configure`
2. Payload:
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
3. Observe response

**Impact**:
- Priority: Medium
- Component: focus-server, api, view-type

**Suggested Fix**:
{developer_suggestion}

**Automated Test**:
`tests/integration/api/test_singlechannel_view_mapping.py::{test_name}`

---

## 📈 Performance Benchmarks

| Test | Expected Duration |
|------|------------------|
| Single test | < 2 seconds |
| Happy path suite | < 10 seconds |
| All edge cases | < 15 seconds |
| Full test suite | < 30 seconds |

---

## 🔧 Troubleshooting

### Test Fails: "Expected stream_amount=1, got 2"
**Cause**: Backend is treating SINGLECHANNEL as MULTICHANNEL

**Solution**: Check view_type enum value in request/response

### Test Fails: "Channel '7' not in mapping"
**Cause**: Backend is not including requested channel in response

**Solution**: Verify channel selection logic in backend

### Test Fails: "Expected stream index 0, got 1"
**Cause**: Backend is using 1-based indexing instead of 0-based

**Solution**: Standardize on 0-based stream indexing

---

## 🔗 Related Documentation

- [Focus Server API Documentation](./API_HEALING_GUIDE.md)
- [View Type Specification](./TECHNICAL_SPECIFICATIONS_CLARIFICATIONS.md)
- [Integration Test Guide](./COMPLETE_RABBITMQ_JOURNEY.md)

---

## ✅ Success Criteria

The test suite is considered successful when:

1. ✅ All happy path tests pass
2. ✅ Edge cases are handled gracefully
3. ✅ Error validation is enforced
4. ✅ Backend consistency is maintained across multiple requests
5. ✅ No regressions in existing functionality

---

## 📞 Contact

For questions about this test suite, contact:
- **QA Team**: qa@example.com
- **Developer**: {developer_name}
- **Test Owner**: QA Automation Architect

---

**Last Updated**: 2025-10-12  
**Version**: 1.0  
**Status**: ✅ Production Ready

