# Work Plan: Fix Test Mapping Issues

**Date:** 2025-11-09  
**Status:** Planning  
**Priority:** High

---

## 📊 Current Status Summary

### Issues Found (VERIFIED - Triple Checked + Outside tests/):
1. **37 tests in Jira but NOT in automation** ✅ - Need to be automated (237 - 200 = 37)
2. **204 real test functions without Xray markers** ✅ - Need markers added (181 in tests/ + 23 outside tests/ = 204)
3. **1 test function with multiple markers** - Need review
4. **1 test ID in automation but NOT in Jira** - Need investigation
5. **Test quality issues in Jira** - Need updates

### Statistics (VERIFIED - Triple Checked):
- Total tests in Jira: 237
- Total test IDs in automation: **200** ✅
- Total test functions: 463
- Test functions with markers: **163** ✅
- Test functions without markers: 300
  - Unit tests (don't need markers): 81 ✅
  - Helper functions (don't need markers): 38 ✅
  - **Real test functions (NEED markers): 181** ✅
- **Real test functions outside tests/ (NEED markers): 23** ✅
  - UI tests: 7
  - API Load tests: 10
  - Infrastructure tests: 6 (K8s: 1, MongoDB: 1, SSH: 4)
- **Total real test functions WITHOUT markers: 204** ✅ (181 + 23)
- Tests in Jira but NOT in automation: **37** ✅ (237 - 200 = 37)

---

## 🎯 Work Plan

### Phase 1: Analysis & Prioritization (1-2 hours)

#### 1.1 Categorize Missing Tests in Jira
- [ ] Group **37 missing tests** by category (VERIFIED: 237 - 200 = 37):
  - API tests
  - Integration tests
  - Infrastructure tests
  - Data Quality tests
  - Performance tests
  - Security tests
- [ ] Prioritize by:
  - Test Type (Automation priority)
  - Priority field in Jira
  - Dependencies
- [ ] Create implementation order

#### 1.2 Categorize Test Functions Without Markers
- [x] Group **204 test functions** by (VERIFIED):
  - Integration tests (101) - HIGH PRIORITY ✅
  - Infrastructure tests (56 in tests/ + 6 outside = 62) - HIGH PRIORITY ✅
  - Data Quality tests (11) - MEDIUM PRIORITY ✅
  - Load tests (4) - MEDIUM PRIORITY ✅
  - Performance tests (5) - MEDIUM PRIORITY ✅
  - Security tests (1) - MEDIUM PRIORITY ✅
  - UI tests (7 outside tests/) - MEDIUM PRIORITY ✅
  - API Load tests (10 outside tests/) - HIGH PRIORITY ✅
  - Other tests (3) - LOW PRIORITY ✅
- [ ] Check if they have corresponding Jira tests
- [ ] Identify which need new Jira tests created

#### 1.3 Review Multiple Markers Case
- [ ] Review `test_sustained_load_1_hour` with PZ-14088 (duplicate)
- [ ] Decide if it should be split or keep as is

#### 1.4 Investigate Extra Test ID
- [ ] Check PZ-13768 in automation but not in Jira
- [ ] Decide: Create Jira test or remove marker

---

### Phase 2: Add Missing Markers (4-6 hours)

#### 2.1 Integration Tests Without Markers (101 functions) ✅ VERIFIED
**Priority: HIGH**

- [ ] Check each test function against Jira tests
- [ ] Add `@pytest.mark.xray()` markers where Jira test exists
- [ ] Create Jira tests where missing
- [ ] Update test documentation

**Files to process:**
- `tests/integration/api/` - Multiple files
- `tests/integration/calculations/` - Multiple files
- `tests/integration/data_quality/` - Multiple files
- `tests/integration/error_handling/` - Multiple files
- `tests/integration/load/` - Multiple files
- `tests/integration/performance/` - Multiple files
- `tests/integration/security/` - Multiple files

#### 2.2 Infrastructure Tests Without Markers (62 functions) ✅ VERIFIED
- In tests/ directory: 56 functions
- Outside tests/ directory: 6 functions (K8s: 1, MongoDB: 1, SSH: 4)
**Priority: HIGH**

- [ ] Check each test function against Jira tests
- [ ] Add `@pytest.mark.xray()` markers where Jira test exists
- [ ] Create Jira tests where missing
- [ ] Update test documentation

**Files to process:**
- `tests/infrastructure/test_basic_connectivity.py` - 4 functions
- `tests/infrastructure/test_external_connectivity.py` - 12 functions
- `tests/infrastructure/test_k8s_job_lifecycle.py` - 6 functions
- `tests/infrastructure/test_mongodb_monitoring_agent.py` - 27 functions
- `tests/infrastructure/test_pz_integration.py` - 6 functions
- `tests/infrastructure/test_system_behavior.py` - 5 functions
- `tests/infrastructure/resilience/` - Multiple files
- `tests/infrastructure/test_rabbitmq_connectivity.py` - 2 functions
- `tests/infrastructure/test_rabbitmq_outage_handling.py` - 2 functions

#### 2.3 Data Quality Tests Without Markers (11 functions) ✅ VERIFIED
**Priority: MEDIUM**

- [ ] Check each test function against Jira tests
- [ ] Add `@pytest.mark.xray()` markers where Jira test exists
- [ ] Create Jira tests where missing

**Files to process:**
- `tests/data_quality/test_mongodb_data_quality.py` - 5 functions
- `tests/data_quality/test_mongodb_indexes_and_schema.py` - 4 functions
- `tests/data_quality/test_mongodb_recovery.py` - 2 functions
- `tests/data_quality/test_mongodb_schema_validation.py` - 2 functions
- `tests/data_quality/test_recordings_classification.py` - 2 functions

#### 2.4 Load/Performance/Security/UI Tests Without Markers (27 functions) ✅ VERIFIED
  - Load tests: 4 functions (in tests/)
  - Performance tests: 5 functions (in tests/)
  - Security tests: 1 function (in tests/)
  - UI tests: 7 functions (outside tests/) ✅ NEW
  - API Load tests: 10 functions (outside tests/) ✅ NEW
**Priority: MEDIUM**

- [ ] Check each test function against Jira tests
- [ ] Add `@pytest.mark.xray()` markers where Jira test exists
- [ ] Create Jira tests where missing

**Files to process:**
- `tests/load/test_job_capacity_limits.py` - 4 functions
- `tests/performance/test_mongodb_outage_resilience.py` - 5 functions
- `tests/security/test_malformed_input_handling.py` - 2 functions

---

### Phase 3: Create Missing Tests in Automation (8-12 hours)

#### 3.1 API Tests Missing (Priority: HIGH)
**Estimated: 15-20 tests** ✅ (VERIFIED: 22 from breakdown, but some may already exist)

- [ ] PZ-13548: API – Historical configure (happy path)
- [ ] PZ-13552: API – Invalid time range (negative)
- [ ] PZ-13554: API – Invalid channels (negative)
- [ ] PZ-13555: API – Invalid frequency range (negative)
- [ ] PZ-13560: API – GET /channels
- [ ] PZ-13561: API – GET /live_metadata present
- [ ] PZ-13562: API – GET /live_metadata missing
- [ ] PZ-13564: API – POST /recordings_in_time_range
- [ ] PZ-13759-PZ-13766: Multiple API validation tests
- [ ] PZ-13814-PZ-13824: SingleChannel API tests
- [ ] PZ-13895: GET /channels - Enabled Channels List
- [ ] PZ-13903: Frequency Range Nyquist Limit Enforcement

#### 3.2 Integration Tests Missing (Priority: HIGH)
**Estimated: 10-15 tests** ✅ (VERIFIED: 16 from breakdown)

- [ ] PZ-13603: Integration – Mongo outage on History configure
- [ ] PZ-13604: Integration – Orchestrator error triggers rollback
- [ ] PZ-13767: Integration – MongoDB Outage Handling
- [ ] PZ-13832-PZ-13837: SingleChannel edge cases
- [ ] PZ-13852-PZ-13855: SingleChannel validation tests
- [ ] PZ-13863-PZ-13865: Historic Playback tests
- [ ] PZ-13873: Valid Configuration - All Parameters
- [ ] PZ-13877: Invalid Frequency Range - Min > Max
- [ ] PZ-14101: Historic Playback - Short Duration (Rapid Window)

#### 3.3 Data Quality Tests Missing (Priority: MEDIUM)
**Estimated: 5-8 tests**

- [ ] PZ-13684: Data Quality – node4 Schema Validation
- [ ] PZ-13685: Data Quality – Recordings Metadata Completeness
- [ ] PZ-13811: Data Quality – Validate Recordings Document Schema
- [ ] PZ-13812: Data Quality – Verify Recordings Have Complete Metadata

#### 3.4 Infrastructure Tests Missing (Priority: MEDIUM)
**Estimated: 10-15 tests**

- [ ] PZ-13806-PZ-13812: Infrastructure connectivity tests
- [ ] Various infrastructure resilience tests

#### 3.5 Security Tests Missing (Priority: MEDIUM)
**Estimated: 2-3 tests**

- [ ] PZ-13572: Security – Robustness to malformed inputs
- [ ] PZ-13769: Security – Malformed Input Handling

---

### Phase 4: Fix Issues (2-3 hours)

#### 4.1 Fix Multiple Markers
- [ ] Review `test_sustained_load_1_hour` with PZ-14088 (duplicate)
- [ ] Decide: Split test or keep single marker
- [ ] Update code accordingly

#### 4.2 Fix Extra Test ID
- [ ] Investigate PZ-13768
- [ ] Option A: Create Jira test for it
- [ ] Option B: Remove marker if not needed
- [ ] Update code accordingly

#### 4.3 Update Jira Test Quality
- [ ] Review tests with quality issues
- [ ] Update descriptions in Jira
- [ ] Add missing test types
- [ ] Improve summaries

---

### Phase 5: Verification & Documentation (2-3 hours)

#### 5.1 Re-run Comprehensive Check
- [ ] Run `comprehensive_test_mapping_check_fixed.py`
- [ ] Verify all issues are resolved
- [ ] Generate final report

#### 5.2 Update Documentation
- [ ] Update test mapping documentation
- [ ] Create coverage report
- [ ] Document any decisions made

#### 5.3 Create Summary Report
- [ ] Summary of work done
- [ ] Statistics before/after
- [ ] Remaining issues (if any)
- [ ] Recommendations

---

## 📋 Detailed Task List

### Task 1: Analysis & Categorization
**Estimated Time: 1-2 hours**

1. Create detailed breakdown of 91 missing tests
2. Create detailed breakdown of 262 test functions without markers
3. Map test functions to Jira tests (where possible)
4. Identify gaps

**Output:**
- `MISSING_TESTS_BREAKDOWN.md`
- `TEST_FUNCTIONS_WITHOUT_MARKERS_BREAKDOWN.md`
- `MAPPING_GAPS_ANALYSIS.md`

### Task 2: Add Markers to Existing Tests
**Estimated Time: 4-6 hours**

**Priority Order:**
1. Integration tests (122 functions) - Start with API tests
2. Infrastructure tests (67 functions) - Start with connectivity tests
3. Data Quality tests (15 functions)
4. Load/Performance/Security tests (11 functions)

**Approach:**
- For each test function, check if corresponding Jira test exists
- If exists: Add `@pytest.mark.xray("PZ-XXXXX")` marker
- If not exists: Note for Task 3 (create Jira test or create automation test)

**Output:**
- Updated test files with markers
- List of tests that need Jira tests created

### Task 3: Create Missing Automation Tests
**Estimated Time: 8-12 hours**

**Priority Order:**
1. API tests (20-25 tests) - Most critical
2. Integration tests (15-20 tests) - High priority
3. Data Quality tests (5-8 tests) - Medium priority
4. Infrastructure tests (10-15 tests) - Medium priority
5. Security tests (2-3 tests) - Medium priority

**Approach:**
- For each missing Jira test:
  - Review Jira test description
  - Create automation test
  - Add `@pytest.mark.xray("PZ-XXXXX")` marker
  - Test the implementation

**Output:**
- New test files or updated existing files
- All tests with proper markers

### Task 4: Fix Special Cases
**Estimated Time: 1 hour**

1. Fix `test_sustained_load_1_hour` with duplicate PZ-14088
2. Investigate and fix PZ-13768
3. Review and fix any other special cases

**Output:**
- Fixed test files
- Documentation of decisions

### Task 5: Update Jira Tests Quality
**Estimated Time: 1-2 hours**

1. Review tests with quality issues
2. Update descriptions in Jira
3. Add missing information

**Output:**
- Updated Jira tests
- Quality report

### Task 6: Final Verification
**Estimated Time: 1 hour**

1. Re-run comprehensive check
2. Verify all markers are correct
3. Verify all tests are mapped
4. Generate final report

**Output:**
- Final comprehensive report
- Coverage statistics
- Summary document

---

## ⏱️ Time Estimates

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Analysis | Categorization & Prioritization | 1-2 hours |
| Phase 2: Add Markers | 262 test functions | 4-6 hours |
| Phase 3: Create Tests | 91 missing tests | 8-12 hours |
| Phase 4: Fix Issues | Special cases | 2-3 hours |
| Phase 5: Verification | Final check & docs | 2-3 hours |
| **TOTAL** | | **17-26 hours** |

---

## 🎯 Success Criteria

### Must Have:
- ✅ All integration tests have Xray markers
- ✅ All infrastructure tests have Xray markers
- ✅ All data quality tests have Xray markers
- ✅ All load/performance/security tests have Xray markers
- ✅ All **37 missing Jira tests** are automated OR marked as not needed ✅ VERIFIED
- ✅ All **204 real test functions** have Xray markers (181 in tests/ + 23 outside tests/) ✅ VERIFIED
- ✅ No test functions with multiple markers (unless intentional)
- ✅ All test IDs in automation exist in Jira

### Nice to Have:
- ✅ All Jira tests have good quality descriptions
- ✅ 100% coverage of Jira tests in automation
- ✅ All test functions documented

---

## 📝 Notes

1. **Unit tests (81)** - These typically don't need Xray markers as they test code, not requirements
2. **Helper functions (38)** - These don't need markers as they're utilities
3. **Priority**: Focus on Integration and Infrastructure tests first (189 functions)
4. **Approach**: Batch process by category for efficiency
5. **Verification**: Run comprehensive check after each phase

---

## 🚀 Next Steps

1. Review and approve this work plan
2. Start with Phase 1: Analysis & Categorization
3. Create detailed breakdowns
4. Begin Phase 2: Add Markers (starting with highest priority)

---

**Created:** 2025-11-09  
**Last Updated:** 2025-11-09

