# 🐛 Summary - Bugs Found by Automation

**Date:** October 27, 2025  
**Source:** Automated Test Suite  
**Status:** 3 bugs opened in JIRA + 1 performance finding

---

## 1. PZ-13983: MongoDB Indexes (Recommendation) ⚠️ CLOSED

**One-liner:** Backend missing `deleted` index causes slow queries when filtering deleted recordings.  
**Note:** Other indexes exist; only performance optimization, not a critical bug.  
**Test:** `tests/data_quality/test_mongodb_data_quality.py`

---

## 2. PZ-13984: Future Timestamp Validation ⚠️ HIGH

**One-liner:** Backend accepts job requests with future timestamps (tomorrow/week ahead), allowing creation of jobs for non-existent data.  
**Test:** `tests/integration/api/test_prelaunch_validations.py::test_time_range_validation_future_timestamps`

---

## 3. PZ-13985: LiveMetadata Missing Fields ⚠️ HIGH

**One-liner:** GET /metadata API response missing two required fields (`num_samples_per_trace`, `dtype`), causing Pydantic validation to fail and frontend to break.  
**Test:** `tests/integration/api/test_api_endpoints_high_priority.py::test_get_live_metadata`

---

## 4. PZ-13986: 200 Jobs Capacity Gap ⚠️ MAJOR

**One-liner:** System handles only 40 concurrent jobs instead of required 200, resulting in 80% failure rate and inability to meet production load requirements.  
**Test:** `tests/load/test_job_capacity_limits.py::test_target_capacity_200_concurrent_jobs`

---

## 📊 Quick Summary

| JIRA | One-Line Issue Description | Priority | Effort | Team | Status |
|------|---------------------------|----------|--------|------|--------|
| PZ-13983 | Missing `deleted` index causes slow queries on deleted recordings | Low (Optional) | 5 min | DBA | CLOSED |
| PZ-13984 | Backend accepts future timestamps, creating jobs for non-existent data | High | 2-4h | Backend | OPEN |
| PZ-13985 | API response missing 2 required fields causing Pydantic validation to fail | High | 1-2h | Backend | OPEN |
| PZ-13986 | System handles 40/200 concurrent jobs, 80% failure rate under load | Major | Weeks | DevOps | OPEN |

---

## ✅ **Updated Summary**

**Total:** 4 findings from automation  
**Real Bugs:** 3 (PZ-13984, PZ-13985, PZ-13986)  
**Recommendations:** 1 (PZ-13983 - Closed)  
**Quick Fixes:** 2 bugs (5min + 2-4h)  
**Infrastructure:** 1 major epic (weeks)

---

**For full details:** `documentation/jira/JIRA_TO_TESTS_MAPPING.md`

