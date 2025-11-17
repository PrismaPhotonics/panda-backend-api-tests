# ⚡ Stress Tests

**Category:** Stress (Xray-aligned)  
**Purpose:** Extreme conditions and edge case testing

---

## 📋 What Belongs Here?

Tests that validate behavior under extreme conditions:
- ✅ Very large values (huge NFFT, massive time ranges)
- ✅ Very small values (zero, negative)
- ✅ Boundary conditions (min/max limits)
- ✅ Resource exhaustion scenarios
- ✅ Rapid repeated requests
- ✅ Extreme concurrency
- ✅ Memory limits
- ✅ Time limits and timeouts

---

## 🧪 Test Categories

### Extreme Values
- Zero values (NFFT=0, PRR=0, height=0)
- Negative values (negative frequencies, sensors)
- Maximum values (very large NFFT, very long durations)
- Reversed ranges (start > end)

### Resource Stress
- Very large datasets
- Very long time ranges (years)
- High channel counts
- Rapid polling (stress polling endpoint)

### Edge Cases
- Empty inputs
- Minimal inputs (single channel, single sample)
- Boundary conditions (exactly at limits)

### Rapid Operations
- Rapid configuration changes
- Rapid ROI adjustments
- Rapid polling
- Race conditions

---

## 🚀 Running Tests

```bash
# All stress tests
pytest tests/stress/ -v

# With markers
pytest -m stress -v
pytest -m extreme_values -v
pytest -m boundary -v
pytest -m rapid -v
```

---

## 📊 Current Status

| Test Type | Status | Notes |
|-----------|--------|-------|
| **Extreme Values** | ⏳ Planned | Need validation boundary tests |
| **Resource Stress** | ⏳ Planned | Large datasets, long durations |
| **Edge Cases** | ⏳ Planned | Min/max boundaries |
| **Rapid Operations** | ⏳ Planned | ROI, polling stress |

---

## 🎯 Planned Test Examples

### Extreme NFFT Tests
```python
test_nfft_zero()              # NFFT = 0 → expect 422
test_nfft_negative()          # NFFT = -1 → expect 422
test_nfft_non_power_of_2()    # NFFT = 100 → expect 422
test_nfft_very_large()        # NFFT = 2^20 → resource limit
```

### Extreme Time Ranges
```python
test_very_long_duration()     # 1 year time range
test_very_old_timestamps()    # Timestamps from years ago
test_future_timestamps()      # Future timestamps → 404/400
test_reversed_time_range()    # start > end → 422
```

### Extreme Channel Values
```python
test_sensor_range_exceeds_total()    # channel > max
test_negative_sensor_index()         # channel < 0
test_zero_channel()                  # channel = 0
test_very_large_sensor_range()       # 1000s of channels
```

### Rapid Operations
```python
test_rapid_roi_changes()      # 100 ROI changes in 1 second
test_rapid_configuration()    # Reconfigure repeatedly
```

---

## 💥 Expected Behaviors

### Graceful Degradation:
- Invalid input → **422 Unprocessable Entity** (not 500)
- Resource exhaustion → **503 Service Unavailable** (not crash)
- Timeout → **408 Request Timeout** (not hang)

### Boundary Handling:
```python
# Example expectations
NFFT = 0           → 422 (invalid)
NFFT = 2^10        → 200 (valid, common)
NFFT = 2^20        → 422 or 503 (too large)
NFFT = not_power_2 → 422 (invalid)
```

---

## 📈 Stress Test Metrics

| Metric | Monitor |
|--------|---------|
| Response time | Should not hang indefinitely |
| Memory usage | Should not exceed limits |
| Error rate | Should return proper errors, not crash |
| Recovery time | Should recover after stress |

---

## 🚨 Critical Cases to Test

From Xray analysis, these are **MUST HAVE**:

1. Zero/negative values in all numeric fields
2. Reversed ranges (start > end)
3. Very large values (resource limits)
4. Rapid repeated operations
5. Boundary conditions at limits

---

## 📚 Related Tests

Some stress tests might overlap with:
- **Security** (`tests/security/`) - Malformed input
- **Performance** (`tests/performance/`) - Load testing
- **Integration** (`tests/integration/`) - Edge cases

**Guideline:** If it's about **malicious/malformed input** → Security  
If it's about **extreme but valid values** → Stress  
If it's about **sustained load** → Performance

---

**Last Updated:** 2025-10-21  
**Status:** ⏳ Placeholder - Stress tests to be implemented  
**Priority:** 🟡 Medium (after security and performance)  
**Maintained by:** QA Automation Team

