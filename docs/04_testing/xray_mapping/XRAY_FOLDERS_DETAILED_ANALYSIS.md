# Xray Test Repository - Detailed Folder Analysis

**Generated:** 2025-11-05  
**Source:** Xray Test Repository - Project PZ  
**Folders Analyzed:** 2

---

## 📋 Folder Information

### Folder 1
- **Folder ID:** `674c55ccbaf7e0b87d2be730`
- **URL:** https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin%3Acom.xpandit.plugins.xray__testing-board&atlOrigin=eyJpIjoiYzAyZGQyMjc3OGZjNDc2OWE2YTdhNGRhMDhhOTczYTgiLCJwIjoiaiJ9#!page=test-repository&selectedFolder=674c55ccbaf7e0b87d2be730

### Folder 2
- **Folder ID:** `67d7d7a878a0a2d1bfe6b650`
- **URL:** https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin%3Acom.xpandit.plugins.xray__testing-board&atlOrigin=eyJpIjoiNzZlZDczNjU3NGNlNDE1ZThkYTAyYzA5MDgwYjNhN2MiLCJwIjoiaiJ9#!page=test-repository&selectedFolder=67d7d7a878a0a2d1bfe6b650

---

## ⚠️ Important Note

**Limitation:** Xray folder information is not directly available via Jira REST API.  
This analysis includes all 100 tests from the project.  
To identify which tests belong to specific folders, you need to:

1. **Manual Verification:** Open each folder in Xray UI and check which tests are listed
2. **Xray REST API:** Use Xray REST API with proper authentication to access folder structure
3. **Custom Fields:** Check if Xray stores folder information in custom fields

---

## 📊 Overall Statistics (All Tests)

### Total Tests in Project: 100

| Metric | Value | Percentage |
|--------|-------|------------|
| **Total Tests** | 100 | 100% |
| **Status: TO DO** | 100 | 100% |
| **Priority: Medium** | 99 | 99% |
| **Priority: High** | 1 | 1% |
| **Assignee: Roy Avrahami** | 98 | 98% |
| **Assignee: Tomer Schwartz** | 1 | 1% |
| **Unassigned** | 1 | 1% |
| **Tests Without Components** | 100 | 100% |
| **Tests Without Labels** | 2 | 2% |

### Test Distribution by Category

| Category | Count | Percentage |
|----------|-------|------------|
| **Integration Tests** | 59 | 59% |
| **API Tests** | 19 | 19% |
| **Performance Tests** | 8 | 8% |
| **Data Quality Tests** | 5 | 5% |
| **Infrastructure Tests** | 3 | 3% |
| **Other Tests** | 5 | 5% |
| **Load Tests** | 1 | 1% |
| **Stress Tests** | 1 | 1% |

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

---

## 🔍 Detailed Test Breakdown

### Integration Tests (59 tests)

**Focus Areas:**
- SingleChannel tests (25+ tests)
- Historic Playback tests (12 tests)
- Configuration validation tests (15+ tests)
- Calculation validation tests (8 tests)
- API endpoint tests (GET /channels, GET /sensors)

**Test Keys:**
- PZ-13832 to PZ-13862 (SingleChannel tests)
- PZ-13863 to PZ-13872 (Historic Playback tests)
- PZ-13873 to PZ-13879, PZ-13901, PZ-13903 to PZ-13906, PZ-14072 to PZ-14073, PZ-14093 to PZ-14100, PZ-14101 (Configuration/Validation tests)
- PZ-13895, PZ-13897 (API endpoint tests)
- PZ-14060 to PZ-14071 (Calculation tests)

---

### API Tests (19 tests)

**Focus Areas:**
- SingleChannel API tests (11 tests)
- Health Check endpoint tests (8 tests)
- GET /channels endpoint tests
- GET /sensors endpoint tests

**Test Keys:**
- PZ-13814 to PZ-13824 (SingleChannel API tests)
- PZ-13895, PZ-13897 (GET endpoints)
- PZ-14026 to PZ-14033 (Health Check tests)

---

### Performance Tests (8 tests)

**Focus Areas:**
- Latency tests (P95, P99)
- Job creation time
- Concurrent task limit
- High throughput stress test
- Data rate calculation
- Memory usage estimation

**Test Keys:**
- PZ-13896, PZ-13905, PZ-14078 to PZ-14092

---

### Data Quality Tests (5 tests)

**Focus Areas:**
- MongoDB collections validation
- MongoDB indexes validation
- Recordings schema validation
- Metadata completeness
- Data integrity validation

**Test Keys:**
- PZ-13809 to PZ-13812, PZ-13867

---

### Infrastructure Tests (3 tests)

**Focus Areas:**
- MongoDB connection and health check
- Kubernetes cluster connection and pod health check
- SSH access to production servers

**Test Keys:**
- PZ-13898 to PZ-13900

---

### Other Tests (5 tests)

**Focus Areas:**
- Orchestration tests
- Historic spectrogram dimensions
- Smart Querying
- Alerts limitation

**Test Keys:**
- PZ-14018, PZ-14019, PZ-14080, PZ-14202, PZ-14204

---

### Load Tests (1 test)

**Focus Areas:**
- 200 jobs capacity stress test

**Test Keys:**
- PZ-14088

---

### Stress Tests (1 test)

**Focus Areas:**
- Configuration with extreme values

**Test Keys:**
- PZ-13880

---

## 📋 Complete Test List (100 Tests)

### SingleChannel Tests (25+ tests)

| Test Key | Summary | Category |
|----------|---------|----------|
| PZ-13814 | API – SingleChannel View for Channel 1 (First Channel) | API |
| PZ-13815 | API – SingleChannel View for Channel 100 (Upper Boundary Test) | API |
| PZ-13816 | API – Different SingleChannels Return Different Mappings | API |
| PZ-13817 | API – Same SingleChannel Returns Consistent Mapping Across Multiple Requests | API |
| PZ-13818 | API – Compare SingleChannel vs MultiChannel View Types | API |
| PZ-13819 | API – SingleChannel View with Various Frequency Ranges | API |
| PZ-13820 | API – SingleChannel Rejects Invalid Frequency Range | API |
| PZ-13821 | API – SingleChannel Rejects Invalid Display Height | API |
| PZ-13822 | API – SingleChannel Rejects Invalid NFFT Value | API |
| PZ-13823 | API – SingleChannel Rejects When min ≠ max | API |
| PZ-13824 | API – SingleChannel Rejects Channel Zero | API |
| PZ-13832 | Integration - SingleChannel Edge Case - Minimum Channel (Channel 1) | Integration |
| PZ-13833 | Integration - SingleChannel Edge Case - Maximum Channel (Last Channel) | Integration |
| PZ-13834 | Integration - SingleChannel Edge Case - Middle Channel | Integration |
| PZ-13835 | Integration - SingleChannel with Invalid Channel (Out of Range) | Integration |
| PZ-13836 | Integration - SingleChannel with Invalid Channel (Negative) | Integration |
| PZ-13837 | Integration - SingleChannel with Invalid Channel (Zero) | Integration |
| PZ-13852 | Integration - SingleChannel with Min > Max (Validation Error Expected) | Integration |
| PZ-13853 | Integration - SingleChannel Data Consistency Check | Integration |
| PZ-13854 | Integration - SingleChannel Frequency Range Validation | Integration |
| PZ-13855 | Integration - SingleChannel Canvas Height Validation | Integration |
| PZ-13857 | Integration - SingleChannel NFFT Validation | Integration |
| PZ-13858 | Integration - SingleChannel Rapid Reconfiguration | Integration |
| PZ-13859 | Integration - SingleChannel Polling Stability | Integration |
| PZ-13860 | Integration - SingleChannel Metadata Consistency | Integration |
| PZ-13861 | Integration - SingleChannel Stream Mapping Verification | Integration |
| PZ-13862 | Integration - SingleChannel Complete Flow End-to-End | Integration |

---

### Historic Playback Tests (12 tests)

| Test Key | Summary | Category |
|----------|---------|----------|
| PZ-13548 | Data Availability - Historic Mode | Integration |
| PZ-13863 | Integration – Historic Playback - Standard 5-Minute Range | Integration |
| PZ-13865 | Integration – Historic Playback - Short Duration (1 Minute) | Integration |
| PZ-13866 | Integration – Historic Playback - Very Old Timestamps (No Data Available) | Integration |
| PZ-13867 | Data Quality – Historic Playback - Data Integrity Validation | Data Quality |
| PZ-13868 | Integration – Historic Playback - Status 208 Completion | Integration |
| PZ-13869 | Integration – Historic Playback - Invalid Time Range (End Before Start) | Integration |
| PZ-13870 | Integration – Historic Playback - Future Timestamps | Integration |
| PZ-13871 | Integration – Historic Playback - Timestamp Ordering Validation | Integration |
| PZ-13872 | Integration – Historic Playback Complete End-to-End Flow | Integration |
| PZ-13907 | Integration - Historic Configuration Missing start_time Field | Integration |
| PZ-13909 | Integration - Historic Configuration Missing end_time Field | Integration |
| PZ-14101 | Integration - Historic Playback - Short Duration (Rapid Window) | Integration |
| PZ-14019 | History with Empty Time Window Returns 400 | Historic Playback |

---

### Configuration Validation Tests (15+ tests)

| Test Key | Summary | Category |
|----------|---------|----------|
| PZ-13873 | Integration - Valid Configuration - All Parameters | Integration |
| PZ-13874 | Integration – Invalid NFFT - Zero Value | Integration |
| PZ-13875 | Integration – Invalid NFFT - Negative Value | Integration |
| PZ-13876 | Integration – Invalid Channel Range - Min > Max | Integration |
| PZ-13877 | Integration – Invalid Frequency Range - Min > Max | Integration |
| PZ-13878 | Integration – Invalid View Type - Out of Range | Integration |
| PZ-13879 | Integration – Missing Required Fields | Integration |
| PZ-13901 | Integration - NFFT Values Validation - All Supported Values | Integration |
| PZ-13903 | Integration - Frequency Range Nyquist Limit Enforcement | Integration |
| PZ-13904 | Integration - Configuration Resource Usage Estimation | Integration |
| PZ-13906 | Integration - Low Throughput Configuration Edge Case | Integration |
| PZ-14072 | Integration – Validation – FFT Window Size (Power of 2) Validation | Integration |
| PZ-14073 | Integration – Validation – Overlap Percentage Validation | Integration |
| PZ-14093 | Integration - Invalid View Type - Out of Range | Integration |
| PZ-14094 | Integration - Invalid View Type - String Value | Integration |
| PZ-14095 | Integration - Configuration Missing displayTimeAxisDuration Field | Integration |
| PZ-14097 | Integration - Configuration Missing nfftSelection Field | Integration |
| PZ-14098 | Integration - Configuration Missing frequencyRange Field | Integration |
| PZ-14099 | Integration - Configuration Missing channels Field | Integration |
| PZ-14100 | Integration - Frequency Range Within Nyquist Limit | Integration |
| PZ-14018 | Invalid Configuration Does Not Launch Orchestration | Configuration/Validation |

---

### API Endpoint Tests (19 tests)

| Test Key | Summary | Category |
|----------|---------|----------|
| PZ-13762 | GET /channels - Bounds | API |
| PZ-13895 | Integration – GET /channels - Enabled Channels List | Integration |
| PZ-13897 | Integration - GET /sensors - Retrieve Available Sensors List | Integration |
| PZ-14026 | API - Health Check Returns Valid Response (200 OK) | API |
| PZ-14027 | API - Health Check Rejects Invalid HTTP Methods | API |
| PZ-14028 | API - Health Check Handles Concurrent Requests | API |
| PZ-14029 | API - Health Check with Various Headers | API |
| PZ-14030 | API - Health Check Security Headers Validation | API |
| PZ-14031 | API - Health Check Response Structure Validation | API |
| PZ-14032 | API - Health Check with SSL/TLS | API |
| PZ-14033 | API - Health Check Load Testing | API |
| PZ-13814 to PZ-13824 | SingleChannel API tests (11 tests) | API |

---

### Performance Tests (8 tests)

| Test Key | Summary | Category |
|----------|---------|----------|
| PZ-13896 | Performance – Concurrent Task Limit | Performance |
| PZ-13905 | Performance - High Throughput Configuration Stress Test | Performance |
| PZ-14078 | Performance – Data Rate Calculation (Informational) | Performance |
| PZ-14079 | Performance – Memory Usage Estimation (Informational) | Performance |
| PZ-14080 | Historic – Spectrogram Dimensions Calculation | Performance |
| PZ-14090 | Performance - Job Creation Time < 2 Seconds | Performance |
| PZ-14091 | Performance - Configuration Endpoint P99 Latency | Performance |
| PZ-14092 | Performance - Configuration Endpoint P95 Latency | Performance |

---

### Calculation Tests (8 tests)

| Test Key | Summary | Category |
|----------|---------|----------|
| PZ-14060 | Integration – Calculation Validation – Frequency Resolution Calculation | Integration |
| PZ-14061 | Integration – Calculation Validation – Frequency Bins Count Calculation | Integration |
| PZ-14062 | Integration – Calculation Validation – Nyquist Frequency Limit Calculation | Integration |
| PZ-14066 | Integration – Calculation Validation – Time Resolution (line rate) Calculation | Integration |
| PZ-14067 | Integration – Calculation Validation – Output Rate Calculation | Integration |
| PZ-14068 | Integration – Calculation Validation – Time Window Duration Calculation | Integration |
| PZ-14069 | Integration – Calculation Validation – Channel Count Calculation | Integration |
| PZ-14070 | Integration – Calculation Validation – MultiChannel Mapping Calculation | Integration |
| PZ-14071 | Integration – Calculation Validation – Stream Amount Calculation | Integration |

---

### Data Quality Tests (5 tests)

| Test Key | Summary | Category |
|----------|---------|----------|
| PZ-13809 | Data Quality – Verify Required MongoDB Collections Exist | Data Quality |
| PZ-13810 | Data Quality – Verify Critical MongoDB Indexes Exist | Data Quality |
| PZ-13811 | Data Quality – Validate Recordings Document Schema | Data Quality |
| PZ-13812 | Data Quality – Verify Recordings Have Complete Metadata | Data Quality |
| PZ-13867 | Data Quality – Historic Playback - Data Integrity Validation | Data Quality |

---

### Infrastructure Tests (3 tests)

| Test Key | Summary | Category |
|----------|---------|----------|
| PZ-13898 | Infrastructure - MongoDB Direct Connection and Health Check | Infrastructure |
| PZ-13899 | Infrastructure - Kubernetes Cluster Connection and Pod Health Check | Infrastructure |
| PZ-13900 | Infrastructure - SSH Access to Production Servers | Infrastructure |

---

### Load & Stress Tests (2 tests)

| Test Key | Summary | Category |
|----------|---------|----------|
| PZ-14088 | Load - 200 Jobs Capacity Stress Test | Load |
| PZ-13880 | Stress - Configuration with Extreme Values | Stress |

---

### Other Tests (3 tests)

| Test Key | Summary | Category |
|----------|---------|----------|
| PZ-14018 | Invalid Configuration Does Not Launch Orchestration | Orchestration |
| PZ-14202 | Smart Querying | Other |
| PZ-14204 | Alerts limitation | Other |

---

## 🎯 Recommendations for Folder Identification

### Method 1: Manual Verification

1. Open each folder in Xray UI:
   - Folder 1: https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin%3Acom.xpandit.plugins.xray__testing-board&atlOrigin=eyJpIjoiYzAyZGQyMjc3OGZjNDc2OWE2YTdhNGRhMDhhOTczYTgiLCJwIjoiaiJ9#!page=test-repository&selectedFolder=674c55ccbaf7e0b87d2be730
   - Folder 2: https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin%3Acom.xpandit.plugins.xray__testing-board&atlOrigin=eyJpIjoiNzZlZDczNjU3NGNlNDE1ZThkYTAyYzA5MDgwYjNhN2MiLCJwIjoiaiJ9#!page=test-repository&selectedFolder=67d7d7a878a0a2d1bfe6b650

2. List all test keys in each folder
3. Update this document with folder-specific test lists

### Method 2: Xray REST API

Use Xray REST API to access folder structure:
```
GET /rest/raven/1.0/api/testrepository/{projectKey}/folders/{folderId}
```

### Method 3: Custom Fields

Check if Xray stores folder information in custom fields:
- Look for custom fields like `folder_id`, `test_folder`, etc.
- Use Jira field API to discover custom fields

---

## 📊 Test Coverage Analysis

### Coverage by Domain

| Domain | Test Count | Coverage Status |
|--------|------------|-----------------|
| **Integration Tests** | 59 | ✅ Comprehensive |
| **API Tests** | 19 | ✅ Good |
| **Performance Tests** | 8 | ⚠️ Partial |
| **Data Quality Tests** | 5 | ⚠️ Partial |
| **Infrastructure Tests** | 3 | ⚠️ Partial |
| **Load Tests** | 1 | ⚠️ Low |
| **Stress Tests** | 1 | ⚠️ Low |
| **Calculation Tests** | 8 | ✅ Good |

### Coverage Gaps

**Missing Coverage:**
- ❌ Security Tests (0 tests)
- ❌ UI Tests (0 tests)
- ❌ Contract Tests (0 tests)
- ❌ Resilience Tests (limited)
- ❌ Recovery Tests (limited)

---

## 🔗 Links

- **Folder 1:** https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin%3Acom.xpandit.plugins.xray__testing-board&atlOrigin=eyJpIjoiYzAyZGQyMjc3OGZjNDc2OWE2YTdhNGRhMDhhOTczYTgiLCJwIjoiaiJ9#!page=test-repository&selectedFolder=674c55ccbaf7e0b87d2be730
- **Folder 2:** https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin%3Acom.xpandit.plugins.xray__testing-board&atlOrigin=eyJpIjoiNzZlZDczNjU3NGNlNDE1ZThkYTAyYzA5MDgwYjNhN2MiLCJwIjoiaiJ9#!page=test-repository&selectedFolder=67d7d7a878a0a2d1bfe6b650
- **All Tests Repository:** https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin%3Acom.xpandit.plugins.xray__testing-board

---

**Last Updated:** 2025-11-05  
**Generated By:** Automated Analysis Script  
**Script:** `scripts/jira/analyze_xray_folders.py`

