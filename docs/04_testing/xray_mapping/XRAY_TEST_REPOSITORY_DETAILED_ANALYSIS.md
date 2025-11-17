# Xray Test Repository - Detailed Analysis

**Generated:** 2025-11-05  
**Source:** Xray Test Repository - Project PZ  
**Total Tests Analyzed:** 100

---

## 📊 Executive Summary

### Overall Statistics

- **Total Tests:** 100
- **Status Distribution:** 100% TO DO (all tests are in TO DO status)
- **Priority Distribution:** 99% Medium, 1% High
- **Assignee Distribution:** 98% Roy Avrahami, 1% Tomer Schwartz, 1% Unassigned
- **Components:** 0% of tests have components (all tests missing components)
- **Labels:** 98% have labels, 2% without labels

### Automation Status

- **Automated Tests:** 0 (0.0%)
- **Manual Tests:** 0 (0.0%)
- **Unknown Status:** 100 (100.0%)

**Note:** Automation status detection is based on labels. Tests might need manual verification or additional custom fields to properly identify automation status.

---

## 📈 Test Distribution Analysis

### By Category (Based on Labels)

| Category | Count | Percentage | Test Keys |
|----------|-------|------------|-----------|
| **Integration Tests** | 59 | 59% | PZ-13814 to PZ-14101 |
| **API Tests** | 19 | 19% | PZ-13814 to PZ-13832, PZ-14026 to PZ-14033 |
| **Performance Tests** | 8 | 8% | PZ-13896, PZ-14078 to PZ-14092 |
| **Data Quality Tests** | 5 | 5% | PZ-13809 to PZ-13812, PZ-13867 |
| **Infrastructure Tests** | 3 | 3% | PZ-13898 to PZ-13900 |
| **Load Tests** | 1 | 1% | PZ-14088 |
| **Stress Tests** | 1 | 1% | PZ-13880 |
| **Validation Tests** | 5 | 5% | PZ-13873 to PZ-13879, PZ-14072 to PZ-14073 |
| **Orchestration Tests** | 2 | 2% | PZ-14018, PZ-14019 |
| **Historic Playback Tests** | 1 | 1% | PZ-13863 to PZ-13872 |
| **Calculation Tests** | 8 | 8% | PZ-14060 to PZ-14071 |
| **Other** | 3 | 3% | PZ-14202, PZ-14204, PZ-14080 |

### By Test Type (Based on Summaries)

| Test Type | Count | Examples |
|-----------|-------|----------|
| **SingleChannel Tests** | 25+ | Channel validation, mapping, edge cases |
| **Historic Playback Tests** | 12 | Time range validation, data integrity |
| **Configuration Validation Tests** | 15+ | NFFT, frequency range, channel range validation |
| **API Endpoint Tests** | 19 | Health check, channels, sensors endpoints |
| **Performance Tests** | 8 | Latency, capacity, load tests |
| **Data Quality Tests** | 5 | MongoDB schema, indexes, metadata |
| **Infrastructure Tests** | 3 | MongoDB, Kubernetes, SSH connectivity |
| **Calculation Tests** | 8 | Frequency resolution, time resolution, mapping |
| **Other Tests** | 5+ | Alerts, smart querying, orchestration |

---

## 🔍 Detailed Test Analysis

### 1. SingleChannel Tests (25+ tests)

**Category:** Integration & API Tests  
**Priority:** Medium  
**Status:** All TO DO

**Test Coverage:**
- ✅ Channel boundary tests (min, max, middle)
- ✅ Invalid channel tests (negative, out of range, zero)
- ✅ Channel range validation (min > max)
- ✅ Frequency range validation
- ✅ Canvas height validation
- ✅ NFFT validation
- ✅ Data consistency checks
- ✅ Metadata consistency
- ✅ Stream mapping verification
- ✅ Complete E2E flows

**Test Keys:**
- PZ-13814 to PZ-13862 (SingleChannel specific tests)
- PZ-13832 to PZ-13861 (Integration SingleChannel tests)

**Automation Status:** Unknown (need to check automation code)

---

### 2. Historic Playback Tests (12 tests)

**Category:** Integration Tests  
**Priority:** Medium  
**Status:** All TO DO

**Test Coverage:**
- ✅ Standard 5-minute range
- ✅ Short duration (1 minute)
- ✅ Very old timestamps (no data)
- ✅ Data integrity validation
- ✅ Status 208 completion
- ✅ Invalid time range (end before start)
- ✅ Future timestamps
- ✅ Timestamp ordering validation
- ✅ Complete E2E flow
- ✅ Missing start_time field
- ✅ Missing end_time field
- ✅ Short duration (rapid window)

**Test Keys:**
- PZ-13548, PZ-13863 to PZ-13872, PZ-13907, PZ-13909, PZ-14101

**Automation Status:** Unknown (need to check automation code)

---

### 3. Configuration Validation Tests (15+ tests)

**Category:** Integration & Validation Tests  
**Priority:** Medium  
**Status:** All TO DO

**Test Coverage:**
- ✅ Valid configuration (all parameters)
- ✅ Invalid NFFT (zero, negative)
- ✅ Invalid channel range (min > max)
- ✅ Invalid frequency range (min > max)
- ✅ Invalid view type (out of range, string value)
- ✅ Missing required fields
- ✅ Extreme values (stress test)
- ✅ FFT window size validation (power of 2)
- ✅ Overlap percentage validation
- ✅ Display time axis duration validation
- ✅ Frequency range within Nyquist limit

**Test Keys:**
- PZ-13873 to PZ-13879, PZ-13880, PZ-13901, PZ-13903 to PZ-13906, PZ-14072 to PZ-14073, PZ-14093 to PZ-14099, PZ-14100

**Automation Status:** Unknown (need to check automation code)

---

### 4. API Endpoint Tests (19 tests)

**Category:** API Tests  
**Priority:** Medium  
**Status:** All TO DO

**Test Coverage:**
- ✅ GET /channels - Enabled channels list
- ✅ GET /sensors - Available sensors list
- ✅ Health check endpoint:
  - Valid response (200 OK)
  - Invalid HTTP methods rejection
  - Concurrent requests handling
  - Various headers
  - Security headers validation
  - Response structure validation
  - SSL/TLS support
  - Load testing

**Test Keys:**
- PZ-13762, PZ-13895, PZ-13897, PZ-14026 to PZ-14033

**Automation Status:** Unknown (need to check automation code)

---

### 5. Performance Tests (8 tests)

**Category:** Performance & Load Tests  
**Priority:** Medium (mostly), 1 High  
**Status:** All TO DO

**Test Coverage:**
- ✅ Concurrent task limit
- ✅ High throughput configuration stress test
- ✅ Data rate calculation (informational)
- ✅ Memory usage estimation (informational)
- ✅ Job creation time (< 2 seconds)
- ✅ Configuration endpoint P99 latency
- ✅ Configuration endpoint P95 latency
- ✅ Load - 200 jobs capacity stress test

**Test Keys:**
- PZ-13896, PZ-13905, PZ-14078 to PZ-14092, PZ-14088

**Automation Status:** Unknown (need to check automation code)

---

### 6. Data Quality Tests (5 tests)

**Category:** Data Quality Tests  
**Priority:** Medium  
**Status:** All TO DO

**Test Coverage:**
- ✅ Verify required MongoDB collections exist
- ✅ Verify critical MongoDB indexes exist
- ✅ Validate recordings document schema
- ✅ Verify recordings have complete metadata
- ✅ Historic playback data integrity validation

**Test Keys:**
- PZ-13809 to PZ-13812, PZ-13867

**Automation Status:** Unknown (need to check automation code)

---

### 7. Infrastructure Tests (3 tests)

**Category:** Infrastructure Tests  
**Priority:** Medium  
**Status:** All TO DO

**Test Coverage:**
- ✅ MongoDB direct connection and health check
- ✅ Kubernetes cluster connection and pod health check
- ✅ SSH access to production servers

**Test Keys:**
- PZ-13898 to PZ-13900

**Automation Status:** Unknown (need to check automation code)

---

### 8. Calculation Tests (8 tests)

**Category:** Integration Tests  
**Priority:** Medium  
**Status:** All TO DO

**Test Coverage:**
- ✅ Frequency resolution calculation
- ✅ Frequency bins count calculation
- ✅ Nyquist frequency limit calculation
- ✅ Time resolution (line rate) calculation
- ✅ Output rate calculation
- ✅ Time window duration calculation
- ✅ Channel count calculation
- ✅ MultiChannel mapping calculation
- ✅ Stream amount calculation

**Test Keys:**
- PZ-14060 to PZ-14071

**Automation Status:** Unknown (need to check automation code)

---

### 9. Other Tests (5+ tests)

**Category:** Various  
**Priority:** Medium  
**Status:** All TO DO

**Test Coverage:**
- ✅ Invalid configuration does not launch orchestration
- ✅ History with empty time window returns 400
- ✅ Historic spectrogram dimensions calculation
- ✅ Smart Querying
- ✅ Alerts limitation

**Test Keys:**
- PZ-14018, PZ-14019, PZ-14080, PZ-14202, PZ-14204

**Automation Status:** Unknown (need to check automation code)

---

## ⚠️ Issues Identified

### 1. Missing Components

**Issue:** 100% of tests (100/100) are missing components  
**Impact:** High - Makes it difficult to categorize and filter tests  
**Recommendation:** Add components to all tests:
- `api` for API tests
- `integration` for integration tests
- `performance` for performance tests
- `data-quality` for data quality tests
- `infrastructure` for infrastructure tests

---

### 2. Automation Status Unknown

**Issue:** 100% of tests (100/100) have unknown automation status  
**Impact:** High - Cannot determine which tests are automated vs manual  
**Recommendation:** 
- Add automation labels: `automation`, `automated`, `manual`, `manual-test`
- Or use Xray custom fields for automation status
- Cross-reference with automation code to identify automated tests

---

### 3. All Tests in TO DO Status

**Issue:** 100% of tests (100/100) are in TO DO status  
**Impact:** Medium - Cannot track test execution status  
**Recommendation:** 
- Update test status after execution
- Use Xray test execution workflow
- Link tests to test executions

---

### 4. Missing Assignee

**Issue:** 1 test (PZ-14204) is missing assignee  
**Impact:** Low - Minor issue  
**Recommendation:** Assign test to appropriate team member

---

### 5. Missing Labels

**Issue:** 2 tests (PZ-14202, PZ-14204) are missing labels  
**Impact:** Low - Minor issue  
**Recommendation:** Add appropriate labels to these tests

---

## 📊 Test Coverage Analysis

### Coverage by Domain

| Domain | Test Count | Percentage | Coverage Status |
|--------|------------|------------|-----------------|
| **Integration Tests** | 59 | 59% | ✅ Good |
| **API Tests** | 19 | 19% | ✅ Good |
| **Performance Tests** | 8 | 8% | ⚠️ Partial |
| **Data Quality Tests** | 5 | 5% | ⚠️ Partial |
| **Infrastructure Tests** | 3 | 3% | ⚠️ Partial |
| **Load Tests** | 1 | 1% | ⚠️ Low |
| **Stress Tests** | 1 | 1% | ⚠️ Low |
| **Calculation Tests** | 8 | 8% | ✅ Good |
| **Other Tests** | 5 | 5% | ✅ Good |

### Coverage Gaps

**Missing Coverage:**
- ❌ Security Tests (0 tests)
- ❌ UI Tests (0 tests)
- ❌ E2E Tests (limited coverage)
- ❌ Contract Tests (0 tests)
- ❌ Resilience Tests (limited coverage)
- ❌ Recovery Tests (limited coverage)

**Recommendations:**
- Add security tests for input validation, authentication, authorization
- Add UI tests for Panda UI workflows
- Add comprehensive E2E tests for critical flows
- Add contract tests for API validation
- Add resilience tests for outage scenarios
- Add recovery tests for system recovery

---

## 🎯 Recommendations

### Immediate Actions (High Priority)

1. **Add Components to All Tests**
   - Add appropriate components to all 100 tests
   - Use standard component names: `api`, `integration`, `performance`, `data-quality`, `infrastructure`

2. **Identify Automation Status**
   - Cross-reference tests with automation code
   - Add automation labels to all tests
   - Update test status based on automation implementation

3. **Update Test Status**
   - Move executed tests from TO DO to appropriate status
   - Link tests to test executions
   - Track test execution history

### Short-Term Actions (Medium Priority)

4. **Expand Test Coverage**
   - Add security tests
   - Add UI tests
   - Add contract tests
   - Add resilience tests

5. **Improve Test Organization**
   - Organize tests by folders in Xray
   - Use consistent naming conventions
   - Add test descriptions and steps

6. **Enhance Test Metadata**
   - Add test descriptions
   - Add test steps
   - Add expected results
   - Add test data requirements

### Long-Term Actions (Low Priority)

7. **Establish Test Execution Workflow**
   - Set up automated test execution
   - Link tests to test executions
   - Track test execution results
   - Generate test execution reports

8. **Implement Test Metrics**
   - Track test pass rate
   - Track test execution time
   - Track test coverage
   - Track test quality metrics

---

## 📋 Test Repository Structure

### Test Distribution by Labels

| Label | Count | Percentage |
|-------|-------|------------|
| `TS_Focus_Server_PZ-14024` | 98 | 98% |
| `Integration_test_panda` | 59 | 59% |
| `api_test_panda` | 19 | 19% |
| `performance_test_panda` | 8 | 8% |
| `validation` | 5 | 5% |
| `data_quality_test_panda` | 5 | 5% |
| `infrastructure_test_panda` | 3 | 3% |
| `orchestration` | 2 | 2% |
| `Load_test_panda` | 1 | 1% |
| `historic-playback` | 1 | 1% |
| `stress_test_panda` | 1 | 1% |

### Test Distribution by Assignee

| Assignee | Count | Percentage |
|----------|-------|------------|
| Roy Avrahami | 98 | 98% |
| Tomer Schwartz | 1 | 1% |
| Unassigned | 1 | 1% |

---

## 📝 Test List (Complete)

### All 100 Tests

| # | Test Key | Summary | Status | Priority | Category |
|---|----------|---------|--------|----------|----------|
| 1 | PZ-13809 | Data Quality – Verify Required MongoDB Collections Exist | TO DO | Medium | Data Quality |
| 2 | PZ-13810 | Data Quality – Verify Critical MongoDB Indexes Exist | TO DO | Medium | Data Quality |
| 3 | PZ-13811 | Data Quality – Validate Recordings Document Schema | TO DO | Medium | Data Quality |
| 4 | PZ-13812 | Data Quality – Verify Recordings Have Complete Metadata | TO DO | Medium | Data Quality |
| 5 | PZ-13814 | API – SingleChannel View for Channel 1 (First Channel) | TO DO | Medium | API |
| 6 | PZ-13815 | API – SingleChannel View for Channel 100 (Upper Boundary Test) | TO DO | Medium | API |
| 7 | PZ-13816 | API – Different SingleChannels Return Different Mappings | TO DO | Medium | API |
| 8 | PZ-13817 | API – Same SingleChannel Returns Consistent Mapping Across Multiple Requests | TO DO | Medium | API |
| 9 | PZ-13818 | API – Compare SingleChannel vs MultiChannel View Types | TO DO | Medium | API |
| 10 | PZ-13819 | API – SingleChannel View with Various Frequency Ranges | TO DO | Medium | API |
| 11 | PZ-13820 | API – SingleChannel Rejects Invalid Frequency Range | TO DO | Medium | API |
| 12 | PZ-13821 | API – SingleChannel Rejects Invalid Display Height | TO DO | Medium | API |
| 13 | PZ-13822 | API – SingleChannel Rejects Invalid NFFT Value | TO DO | Medium | API |
| 14 | PZ-13823 | API – SingleChannel Rejects When min ≠ max | TO DO | Medium | API |
| 15 | PZ-13824 | API – SingleChannel Rejects Channel Zero | TO DO | Medium | API |
| 16 | PZ-13832 | Integration - SingleChannel Edge Case - Minimum Channel (Channel 1) | TO DO | Medium | Integration |
| 17 | PZ-13833 | Integration - SingleChannel Edge Case - Maximum Channel (Last Channel) | TO DO | Medium | Integration |
| 18 | PZ-13834 | Integration - SingleChannel Edge Case - Middle Channel | TO DO | Medium | Integration |
| 19 | PZ-13835 | Integration - SingleChannel with Invalid Channel (Out of Range) | TO DO | Medium | Integration |
| 20 | PZ-13836 | Integration - SingleChannel with Invalid Channel (Negative) | TO DO | Medium | Integration |
| 21 | PZ-13837 | Integration - SingleChannel with Invalid Channel (Zero) | TO DO | Medium | Integration |
| 22 | PZ-13852 | Integration - SingleChannel with Min > Max (Validation Error Expected) | TO DO | Medium | Integration |
| 23 | PZ-13853 | Integration - SingleChannel Data Consistency Check | TO DO | Medium | Integration |
| 24 | PZ-13854 | Integration - SingleChannel Frequency Range Validation | TO DO | Medium | Integration |
| 25 | PZ-13855 | Integration - SingleChannel Canvas Height Validation | TO DO | Medium | Integration |
| 26 | PZ-13857 | Integration - SingleChannel NFFT Validation | TO DO | Medium | Integration |
| 27 | PZ-13858 | Integration - SingleChannel Rapid Reconfiguration | TO DO | Medium | Integration |
| 28 | PZ-13859 | Integration - SingleChannel Polling Stability | TO DO | Medium | Integration |
| 29 | PZ-13860 | Integration - SingleChannel Metadata Consistency | TO DO | Medium | Integration |
| 30 | PZ-13861 | Integration - SingleChannel Stream Mapping Verification | TO DO | Medium | Integration |
| 31 | PZ-13862 | Integration - SingleChannel Complete Flow End-to-End | TO DO | Medium | Integration |
| 32 | PZ-13863 | Integration – Historic Playback - Standard 5-Minute Range | TO DO | Medium | Integration |
| 33 | PZ-13865 | Integration – Historic Playback - Short Duration (1 Minute) | TO DO | Medium | Integration |
| 34 | PZ-13866 | Integration – Historic Playback - Very Old Timestamps (No Data Available) | TO DO | Medium | Integration |
| 35 | PZ-13867 | Data Quality – Historic Playback - Data Integrity Validation | TO DO | Medium | Data Quality |
| 36 | PZ-13868 | Integration – Historic Playback - Status 208 Completion | TO DO | Medium | Integration |
| 37 | PZ-13869 | Integration – Historic Playback - Invalid Time Range (End Before Start) | TO DO | Medium | Integration |
| 38 | PZ-13870 | Integration – Historic Playback - Future Timestamps | TO DO | Medium | Integration |
| 39 | PZ-13871 | Integration – Historic Playback - Timestamp Ordering Validation | TO DO | Medium | Integration |
| 40 | PZ-13872 | Integration – Historic Playback Complete End-to-End Flow | TO DO | Medium | Integration |
| 41 | PZ-13873 | Integration - Valid Configuration - All Parameters | TO DO | Medium | Integration |
| 42 | PZ-13874 | Integration – Invalid NFFT - Zero Value | TO DO | Medium | Integration |
| 43 | PZ-13875 | Integration – Invalid NFFT - Negative Value | TO DO | Medium | Integration |
| 44 | PZ-13876 | Integration – Invalid Channel Range - Min > Max | TO DO | Medium | Integration |
| 45 | PZ-13877 | Integration – Invalid Frequency Range - Min > Max | TO DO | Medium | Integration |
| 46 | PZ-13878 | Integration – Invalid View Type - Out of Range | TO DO | Medium | Integration |
| 47 | PZ-13879 | Integration – Missing Required Fields | TO DO | Medium | Integration |
| 48 | PZ-13880 | Stress - Configuration with Extreme Values | TO DO | Medium | Stress |
| 49 | PZ-13895 | Integration – GET /channels - Enabled Channels List | TO DO | Medium | Integration |
| 50 | PZ-13896 | Performance – Concurrent Task Limit | TO DO | Medium | Performance |
| 51 | PZ-13897 | Integration - GET /sensors - Retrieve Available Sensors List | TO DO | Medium | Integration |
| 52 | PZ-13898 | Infrastructure - MongoDB Direct Connection and Health Check | TO DO | Medium | Infrastructure |
| 53 | PZ-13899 | Infrastructure - Kubernetes Cluster Connection and Pod Health Check | TO DO | Medium | Infrastructure |
| 54 | PZ-13900 | Infrastructure - SSH Access to Production Servers | TO DO | Medium | Infrastructure |
| 55 | PZ-13901 | Integration - NFFT Values Validation - All Supported Values | TO DO | Medium | Integration |
| 56 | PZ-13903 | Integration - Frequency Range Nyquist Limit Enforcement | TO DO | Medium | Integration |
| 57 | PZ-13904 | Integration - Configuration Resource Usage Estimation | TO DO | Medium | Integration |
| 58 | PZ-13905 | Performance - High Throughput Configuration Stress Test | TO DO | Medium | Performance |
| 59 | PZ-13906 | Integration - Low Throughput Configuration Edge Case | TO DO | Medium | Integration |
| 60 | PZ-13907 | Integration - Historic Configuration Missing start_time Field | TO DO | Medium | Integration |
| 61 | PZ-13909 | Integration - Historic Configuration Missing end_time Field | TO DO | Medium | Integration |
| 62 | PZ-14018 | Invalid Configuration Does Not Launch Orchestration | TO DO | High | Orchestration |
| 63 | PZ-14019 | History with Empty Time Window Returns 400 | TO DO | Medium | Orchestration |
| 64 | PZ-14026 | API - Health Check Returns Valid Response (200 OK) | TO DO | Medium | API |
| 65 | PZ-14027 | API - Health Check Rejects Invalid HTTP Methods | TO DO | Medium | API |
| 66 | PZ-14028 | API - Health Check Handles Concurrent Requests | TO DO | Medium | API |
| 67 | PZ-14029 | API - Health Check with Various Headers | TO DO | Medium | API |
| 68 | PZ-14030 | API - Health Check Security Headers Validation | TO DO | Medium | API |
| 69 | PZ-14031 | API - Health Check Response Structure Validation | TO DO | Medium | API |
| 70 | PZ-14032 | API - Health Check with SSL/TLS | TO DO | Medium | API |
| 71 | PZ-14033 | API - Health Check Load Testing | TO DO | Medium | API |
| 72 | PZ-14060 | Integration – Calculation Validation – Frequency Resolution Calculation | TO DO | Medium | Integration |
| 73 | PZ-14061 | Integration – Calculation Validation – Frequency Bins Count Calculation | TO DO | Medium | Integration |
| 74 | PZ-14062 | Integration – Calculation Validation – Nyquist Frequency Limit Calculation | TO DO | Medium | Integration |
| 75 | PZ-14066 | Integration – Calculation Validation – Time Resolution (line rate) Calculation | TO DO | Medium | Integration |
| 76 | PZ-14067 | Integration – Calculation Validation – Output Rate Calculation | TO DO | Medium | Integration |
| 77 | PZ-14068 | Integration – Calculation Validation – Time Window Duration Calculation | TO DO | Medium | Integration |
| 78 | PZ-14069 | Integration – Calculation Validation – Channel Count Calculation | TO DO | Medium | Integration |
| 79 | PZ-14070 | Integration – Calculation Validation – MultiChannel Mapping Calculation | TO DO | Medium | Integration |
| 80 | PZ-14071 | Integration – Calculation Validation – Stream Amount Calculation | TO DO | Medium | Integration |
| 81 | PZ-14072 | Integration – Validation – FFT Window Size (Power of 2) Validation | TO DO | Medium | Integration |
| 82 | PZ-14073 | Integration – Validation – Overlap Percentage Validation | TO DO | Medium | Integration |
| 83 | PZ-14078 | Performance – Data Rate Calculation (Informational) | TO DO | Medium | Performance |
| 84 | PZ-14079 | Performance – Memory Usage Estimation (Informational) | TO DO | Medium | Performance |
| 85 | PZ-14080 | Historic – Spectrogram Dimensions Calculation | TO DO | Medium | Historic |
| 86 | PZ-14088 | Load - 200 Jobs Capacity Stress Test | TO DO | Medium | Load |
| 87 | PZ-14089 | Integration - Time Range Validation - Future Timestamps Rejected | TO DO | Medium | Integration |
| 88 | PZ-14090 | Performance - Job Creation Time < 2 Seconds | TO DO | Medium | Performance |
| 89 | PZ-14091 | Performance - Configuration Endpoint P99 Latency | TO DO | Medium | Performance |
| 90 | PZ-14092 | Performance - Configuration Endpoint P95 Latency | TO DO | Medium | Performance |
| 91 | PZ-14093 | Integration - Invalid View Type - Out of Range | TO DO | Medium | Integration |
| 92 | PZ-14094 | Integration - Invalid View Type - String Value | TO DO | Medium | Integration |
| 93 | PZ-14095 | Integration - Configuration Missing displayTimeAxisDuration Field | TO DO | Medium | Integration |
| 94 | PZ-14097 | Integration - Configuration Missing nfftSelection Field | TO DO | Medium | Integration |
| 95 | PZ-14098 | Integration - Configuration Missing frequencyRange Field | TO DO | Medium | Integration |
| 96 | PZ-14099 | Integration - Configuration Missing channels Field | TO DO | Medium | Integration |
| 97 | PZ-14100 | Integration - Frequency Range Within Nyquist Limit | TO DO | Medium | Integration |
| 98 | PZ-14101 | Integration - Historic Playback - Short Duration (Rapid Window) | TO DO | Medium | Integration |
| 99 | PZ-14202 | Smart Querying | TO DO | Medium | Other |
| 100 | PZ-14204 | Alerts limitation | TO DO | Medium | Other |

---

## 🔗 Links

- **Xray Test Repository:** https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin%3Acom.xpandit.plugins.xray__testing-board
- **Test Folder:** https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin%3Acom.xpandit.plugins.xray__testing-board&atlOrigin=eyJpIjoiYWNhOWFhYjQyNmRjNDY2OGJhZTQ0MGZiZTA2NWIzYjkiLCJwIjoiaiJ9#!page=test-repository&selectedFolder=674f109d682e8700850e3111

---

**Last Updated:** 2025-11-05  
**Generated By:** Automated Analysis Script  
**Script:** `scripts/jira/analyze_xray_test_repository.py`

