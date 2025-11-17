# 📊 Xray Coverage Statistics

**Date:** October 27, 2025  
**Analysis:** Focus Server Automation Test Suite

---

## 📈 Summary

Based on my analysis of the test files:

### Total Tests:
- **~230 test functions** in the automation suite
- **Excluding:** conftest files, README files, __init__ files

### Tests with Xray Markers:
- **12 test functions** have `@pytest.mark.xray()` markers
- **1 fixture** has Xray marker (live_metadata)

### Tests WITHOUT Xray Markers:
- **~218 test functions** without Xray markers

---

## ✅ Detailed Breakdown

### Tests WITH Xray Markers (12 + 1 fixture):

| File | Test Functions with Markers |
|------|---------------------------|
| `test_prelaunch_validations.py` | 8 tests |
| `test_config_validation_nfft_frequency.py` | 2 tests |
| `test_api_endpoints_high_priority.py` | 1 test |
| `test_job_capacity_limits.py` | 1 test |
| `conftest.py` | 1 fixture |
| **TOTAL** | **12 tests + 1 fixture** |

### Tests WITHOUT Xray Markers (Examples):

- `test_unit/` - All 60+ unit tests
- `test_infrastructure/` - 20+ infrastructure tests
- `test_integration/api/test_config_validation_high_priority.py` - 35 tests
- `test_integration/api/test_dynamic_roi_adjustment.py` - 14 tests
- `test_infrastructure/test_pz_integration.py` - 6 tests
- `test_performance/` - 5 performance tests
- `test_data_quality/` - 6 data quality tests
- `test_integration/api/test_singlechannel_view_mapping.py` - 13 tests
- And many more...

---

## 📊 Coverage Breakdown

```
Total Tests:        ~230
With Xray Markers:    12 (5.2%)
Without Markers:     ~218 (94.8%)
```

---

## 🎯 Focused Coverage

The 12 tests with Xray markers are **high-priority tests** that:
1. Found critical bugs (PZ-13984, PZ-13985, PZ-13986)
2. Cover key integration points
3. Map to specific Xray test requirements
4. Are part of the core test plan

---

## 📝 What This Means

### Current State:
- ✅ **12 critical tests** are mapped to Xray
- ❌ **218 other tests** are not mapped (yet)

### Strategy:
- **Priority approach:** Mapped the most critical tests first
- **Many-to-one mapping:** Some automation tests cover multiple Xray tests
- **Coverage**: 22 Xray test keys covered by 12 automation tests

---

## 🚀 Next Steps (Optional)

If you want to increase coverage:

1. **Map more integration tests**
   - SingleChannel view mapping (13 tests)
   - ROI adjustment tests (14 tests)
   - Performance tests (5 tests)

2. **Map infrastructure tests**
   - External connectivity (12 tests)
   - Basic connectivity (4 tests)
   - K8s lifecycle (6 tests)

3. **Map data quality tests**
   - MongoDB quality (6 tests)
   - MongoDB outage resilience (5 tests)

---

## ✅ Answer to Your Question

**Question:** לכמה טסטים באוטומציה יש קישור לטסטים בXRAY וכמה הם לא ?

**Answer:**
- **יש קישור ל-Xray:** 12 טסטים + 1 fixture (5.2%)
- **אין קישור ל-Xray:** ~218 טסטים (94.8%)
- **סה"כ טסטים:** ~230 טסטים

**הטסטים עם קישור הם הטסטים החשובים ביותר! ✅**

