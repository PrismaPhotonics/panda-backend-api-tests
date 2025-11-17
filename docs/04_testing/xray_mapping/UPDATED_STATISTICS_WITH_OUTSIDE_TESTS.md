# Updated Statistics - Including Tests Outside tests/ Directory

**Date:** 2025-11-09  
**Status:** Updated ✅  
**Note:** This includes test files found outside the `tests/` directory

---

## ✅ Updated Counts

### Test Files Found Outside tests/ Directory
- **Total test files outside tests/:** 32 files
- **Relevant test files (excluding PZ project):** 7 files
  - `scripts/test_jira_integration.py` - 4 functions
  - `scripts/test_jira_report_generation.py` - 2 functions
  - `scripts/test_k8s_fixed.py` - 1 function
  - `scripts/test_mongodb_connection.py` - 1 function
  - `scripts/test_ssh_connection.py` - 4 functions
  - `scripts/ui/test_login_page_comprehensive.py` - 7 functions
  - `focus_server_api_load_tests/focus_api_tests/test_api_contract.py` - 10 functions

### Test Functions Outside tests/ Directory
- **Total test functions outside tests/:** 29 functions (relevant files only)
- **All WITHOUT markers:** 29 functions ✅

### Updated Total Statistics

#### Test Functions
- **Test functions in tests/ directory:** 463 ✅
- **Test functions outside tests/ directory:** 29 ✅
- **Total test functions in project:** **492** ✅ (463 + 29)

#### Test Functions Without Markers
- **In tests/ directory:** 300 functions
  - Unit tests (excluded): 81
  - Helper functions (excluded): 38
  - **Real test functions (NEED markers): 181** ✅
- **Outside tests/ directory:** 29 functions
  - **All need markers:** 29 ✅
- **Total real test functions WITHOUT markers:** **210** ✅ (181 + 29)

#### Test Functions With Markers
- **In tests/ directory:** 163 functions ✅
- **Outside tests/ directory:** 0 functions
- **Total test functions WITH markers:** **163** ✅

---

## 📊 Breakdown by Location

### Tests in tests/ Directory
- Total: 463 functions
- With markers: 163
- Without markers: 300
  - Unit tests: 81 (excluded)
  - Helper functions: 38 (excluded)
  - Real tests: 181 (NEED markers)

### Tests Outside tests/ Directory
- Total: 29 functions
- With markers: 0
- Without markers: 29
  - **All need markers:** 29 ✅

---

## 🎯 Updated Work Plan Impact

### Phase 2: Add Missing Markers
**Updated count:** 210 test functions need markers (not 181)
- Integration tests: 101 (in tests/)
- Infrastructure tests: 56 (in tests/)
- Data Quality tests: 11 (in tests/)
- Load tests: 4 (in tests/)
- Performance tests: 5 (in tests/)
- Security tests: 1 (in tests/)
- Other tests: 3 (in tests/)
- **Scripts tests: 19** (outside tests/) ✅ NEW
- **Load tests (focus_server_api_load_tests): 10** (outside tests/) ✅ NEW

### Breakdown of Tests Outside tests/
1. **Scripts tests (19 functions):**
   - `scripts/test_jira_integration.py` - 4 functions
   - `scripts/test_jira_report_generation.py` - 2 functions
   - `scripts/test_k8s_fixed.py` - 1 function
   - `scripts/test_mongodb_connection.py` - 1 function
   - `scripts/test_ssh_connection.py` - 4 functions
   - `scripts/ui/test_login_page_comprehensive.py` - 7 functions

2. **Load tests (10 functions):**
   - `focus_server_api_load_tests/focus_api_tests/test_api_contract.py` - 10 functions

---

## 📝 Notes

1. **PZ Project Files Excluded:**
   - Files in `pz/` and `external/pz/` are from a different project (PZ)
   - These are not part of Focus Server Automation project
   - Excluded from count: 25 files, 68 functions

2. **Scripts Tests:**
   - These are utility/test scripts, not production tests
   - However, they should still have markers if they test functionality
   - Consider moving to `tests/scripts/` or `tests/utilities/`

3. **Load Tests:**
   - `focus_server_api_load_tests/` is a separate project/module
   - These tests should have markers if they're part of the test suite
   - Consider if they should be in `tests/load/` instead

---

## ✅ Recommendations

1. **Move relevant tests to tests/ directory:**
   - Move `scripts/ui/test_login_page_comprehensive.py` → `tests/ui/`
   - Move `focus_server_api_load_tests/focus_api_tests/test_api_contract.py` → `tests/load/` or `tests/integration/api/`

2. **Add markers to all 29 test functions outside tests/**

3. **Update work plan to include 29 additional test functions**

---

**Last Updated:** 2025-11-09  
**Verified By:** Comprehensive scan of entire project

