# Xray Markers Update - New Test IDs Mapping
**Date:** 2025-10-30  
**Action:** Update automation markers with new Jira test IDs

---

## Mapping Table: Old → New Test IDs

| Old ID (Code) | New ID (Jira) | Test Name | File Location |
|---------------|---------------|-----------|---------------|
| PZ-13864 | **PZ-14101** | Historic Playback - Short Duration | `test_historic_playback_additional.py` |
| PZ-13902 | **PZ-14100** | Frequency Range Within Nyquist | `test_config_validation_nfft_frequency.py` |
| PZ-13908 | **PZ-14099** | Missing channels Field | `test_config_validation_high_priority.py` |
| PZ-13910 | **PZ-14098** | Missing frequencyRange Field | `test_config_validation_high_priority.py` |
| PZ-13911 | **PZ-14097** | Missing nfftSelection Field | `test_config_validation_high_priority.py` |
| PZ-13912 | **PZ-14095** | Missing displayTimeAxisDuration | `test_config_validation_high_priority.py` |
| PZ-13913 | **PZ-14094** | Invalid View Type - String | `test_view_type_validation.py` |
| PZ-13914 | **PZ-14093** | Invalid View Type - Out of Range | `test_view_type_validation.py` |
| PZ-13920 | **PZ-14092** | P95 Latency | `test_latency_requirements.py` |
| PZ-13921 | **PZ-14091** | P99 Latency | `test_latency_requirements.py` |
| PZ-13922 | **PZ-14090** | Job Creation Time | `test_latency_requirements.py` |
| PZ-13984 | **PZ-14089** | Future Timestamps Rejection | `test_prelaunch_validations.py` |
| PZ-13986 | **PZ-14088** | 200 Jobs Capacity | `test_job_capacity_limits.py` |

---

## Files to Update (6 files):

1. ✅ `tests/integration/api/test_historic_playback_additional.py` (1 marker)
2. ✅ `tests/integration/api/test_config_validation_nfft_frequency.py` (1 marker)
3. ✅ `tests/integration/api/test_config_validation_high_priority.py` (4 markers)
4. ✅ `tests/integration/api/test_view_type_validation.py` (2 markers)
5. ✅ `tests/integration/performance/test_latency_requirements.py` (3 markers)
6. ✅ `tests/integration/api/test_prelaunch_validations.py` (1 marker)
7. ✅ `tests/load/test_job_capacity_limits.py` (1 marker)

---

## Update Strategy

**Option A: ADD new markers (keep old ones for backward compatibility)**
```python
# Before:
@pytest.mark.xray("PZ-13920")

# After:
@pytest.mark.xray("PZ-13920", "PZ-14092")  # Keep both
```

**Option B: REPLACE markers (clean approach)**
```python
# Before:
@pytest.mark.xray("PZ-13920")

# After:
@pytest.mark.xray("PZ-14092")  # Replace with new ID
```

**Recommendation:** Option A (ADD) - maintain traceability and backward compatibility.

---

## Summary

- **Total markers to update:** 13
- **Files affected:** 7
- **All tests already implemented and passing**
- **Action required:** Update `@pytest.mark.xray()` decorators

