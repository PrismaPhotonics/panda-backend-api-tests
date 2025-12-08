# Interrogator Automation - Deep Investigation Report

**Source:** Confluence Page ID 2349465601  
**Extracted:** December 8, 2024  
**Status:** Critical findings for Phase 1 planning

---

## Executive Summary

| Category | Issues Found | Severity |
|----------|--------------|----------|
| **Code Bugs & Issues** | 12 | 🔴 Critical: 3, 🟡 High: 5, 🟢 Medium: 4 |
| **Missing Test Coverage** | 15 | 🔴 Critical: 5, 🟡 High: 6, 🟢 Medium: 4 |
| **Documentation Gaps** | 8 | 🟡 High: 3, 🟢 Medium: 5 |
| **Architecture Issues** | 6 | 🟡 High: 2, 🟢 Medium: 4 |
| **Maintenance/Tech Debt** | 9 | 🟡 High: 4, 🟢 Medium: 5 |

---

## 🔴 CRITICAL ISSUES

### 1. Duplicated Code in `configurator.py`

**File:** `framework/configurator.py`  
**Lines:** 225-347

```
# These methods are duplicated TWICE in the same file:
def get_broker_connection_info(self)  # Lines 225-240 AND 287-302
def get_rabbit_management_endpoint(self)  # Lines 242-250 AND 304-312
def get_rabbit_management_base_url(self)  # Lines 252-254 AND 314-316
def validate_analyzer_rabbitmq_management_endpoint(self)  # Lines 256-285 AND 318-347
```

**Impact:** Code bloat, maintenance nightmare, potential inconsistencies  
**Fix:** Remove duplicate methods (lines 287-347)

---

### 2. Duplicated SvCli Initialization in `orchestrator.py`

**File:** `framework/orchestrator.py`  
**Lines:** 292-294

```python
self.sv_cli = SvCli(poll_delay=1, broker_uri=self._detect_local_broker_uri())
# Prefer detected local broker for Supervisor RPC
self.sv_cli = SvCli(poll_delay=1, broker_uri=self._detect_local_broker_uri())  # DUPLICATE!
```

**Impact:** Unnecessary object creation, potential memory waste  
**Fix:** Remove line 294

---

### 3. Skipped Critical Tests

**Files:** `tests/test_smoke.py`

| Test | Xray ID | Reason | Impact |
|------|---------|--------|--------|
| `test_bit_test_logs` | IQ-90 | "Need min ~15m, Smoke is too short" | BIT validation not covered in smoke |
| `test_bit_status_logs` | IQ-91 | "Need min ~15m, Smoke is too short" | BIT status not validated |
| `test_compare_heatmaps` | IQ-93 | "heatmap bitwise comparison too sensitive" | Heatmap integrity not validated |

**Fix:** Create a dedicated "medium" or "extended-smoke" suite

---

## 🟡 HIGH SEVERITY ISSUES

### 4. xfail Tests (Known Failures Not Fixed)

| Test | Xray ID | Reason |
|------|---------|--------|
| `test_all_services_stopped` | IQ-84 | "shutdown processes may not be complete" |
| `test_allowed_range_validation` | IQ-488 | "used for information rather than validation" |
| `test_peak_validation` | IQ-489 | "used for information rather than validation" |

### 5. Hardcoded Test Values

**File:** `tests/test_pretest.py`

```python
def test_cyclic_check(...):
    test_time = 120  # HARDCODED!
```

### 6. README Has PLACEHOLDER Sections

```
## PLACEHOLDER
PLACEHOLDER
```

### 7. Python Version Constraint

```
**Important!**
1. Install **Python 3.8** only
```

**Impact:** Python 3.8 is approaching EOL

---

## MISSING TEST COVERAGE

### Critical Missing Tests

| Area | Missing Coverage | Priority |
|------|------------------|----------|
| **Database Recovery** | MongoDB connection failure/recovery | 🔴 Critical |
| **Network Failure** | Analyzer-Interrogator network disconnect | 🔴 Critical |
| **Disk Space** | Behavior when disk is full | 🔴 Critical |
| **NAS Failure** | Storage server disconnection | 🔴 Critical |
| **Multi-Vertical** | Tests only cover Power & Flow | 🔴 Critical |

### High Priority Missing Tests

| Area | Missing Coverage | Priority |
|------|------------------|----------|
| **Optical Unit** | Power down/recovery scenarios | 🟡 High |
| **Data Cut (Lifeboat)** | During live operation | 🟡 High |
| **Configuration Changes** | Runtime configuration changes | 🟡 High |
| **Time Synchronization** | NTP failure scenarios | 🟡 High |
| **GPU Failures** | CUDA errors, driver crashes | 🟡 High |

---

## MISSING PF CRITERIA FILES

Currently only exist:
- `smoke_power_PF_criteria.yaml`
- `smoke_flow_PF_criteria.yaml`
- `longterm_power_PF_criteria.yaml`
- `reliability_power_PF_criteria.yaml`
- `recoverability_power_PF_criteria.yaml`

### Missing Files:

| Vertical | Suites Missing |
|----------|----------------|
| **Eagle** | smoke, longterm, reliability, recoverability |
| **Dove** | smoke, longterm, reliability, recoverability |
| **Shaked/Watch** | smoke, longterm, reliability, recoverability |
| **Flow** | longterm, reliability, recoverability |

---

## TEST METRICS SUMMARY

### Current State:

| Metric | Value |
|--------|-------|
| **Total Test Files** | 4 (smoke, longterm, recoverability, pretest) |
| **Total Test Functions** | ~55 |
| **Skipped Tests** | 3 (permanently) |
| **xfail Tests** | 3 |
| **Xray Mapped Tests** | ~50 |
| **PF Criteria Files** | 5 |
| **Verticals Covered** | 2 (Power, Flow) |
| **Verticals Missing** | 3 (Eagle, Dove, Shaked) |

### Target State:

| Metric | Current | Target |
|--------|---------|--------|
| **Test Files** | 4 | 8+ |
| **Test Functions** | ~55 | ~100 |
| **Skipped Tests** | 3 | 0 |
| **xfail Tests** | 3 | 0 |
| **Verticals Covered** | 2 | 5 |
| **Documentation Pages** | 1 | 8+ |

---

## RECOMMENDED FIXES (Prioritized)

### Immediate Actions (This Week)

| # | Action | Files | Effort |
|---|--------|-------|--------|
| 1 | Remove duplicate code in configurator.py | `framework/configurator.py` | 1h |
| 2 | Remove duplicate SvCli in orchestrator.py | `framework/orchestrator.py` | 5m |
| 3 | Fix test_pretest.py Xray ID (IQ-0) | `tests/test_pretest.py` | 30m |
| 4 | Remove commented code | All test files | 2h |
| 5 | Fix logging in test_recoverability.py | `tests/test_recoverability.py` | 15m |

### Short-Term Actions (This Month)

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 1 | Create "extended-smoke" suite for BIT tests | Covers IQ-90, IQ-91 | 4h |
| 2 | Fix `test_all_services_stopped` (IQ-84) | Real validation | 8h |
| 3 | Move magic numbers to PF criteria | Maintainability | 4h |
| 4 | Complete README documentation | Usability | 8h |

---

**This investigation reveals that while InterrogatorQA is a functional framework with good core capabilities, it has significant technical debt that needs attention. The immediate focus should be on fixing the duplicated code, then expanding coverage.**
