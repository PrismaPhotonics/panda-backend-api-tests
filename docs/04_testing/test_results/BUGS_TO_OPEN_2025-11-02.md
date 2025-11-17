# באגים לפתיחה ב-Jira - 2 בנובמבר 2025

## באגים קריטיים לפתיחה מיידית

### 🔴 באג #1: Server Returns Excessive 500 Errors
**Priority:** Critical
**Component:** Focus Server API
**Environment:** Production (10.10.100.100)

**Description:**
The Focus Server API endpoint `/focus-server/configure` returns excessive HTTP 500 errors, causing multiple test failures.

**Steps to Reproduce:**
1. Send multiple configuration requests to the server
2. Observe that after a few requests, server starts returning 500 errors consistently

**Actual Result:**
- Error: `HTTPSConnectionPool(host='10.10.100.100', port=443): Max retries exceeded with url: /focus-server/configure (Caused by ResponseError('too many 500 error responses'))`
- Affects 8+ different test scenarios

**Expected Result:**
Server should handle requests properly without returning 500 errors

**Affected Tests:**
- test_fft_window_size_validation
- test_overlap_percentage_validation
- test_memory_usage_estimation
- test_e2e_configure_metadata_grpc_flow
- test_config_endpoint_p95_latency
- test_config_endpoint_p99_latency
- test_job_creation_time
- test_live_streaming_stability

**Impact:** Complete blockage of configuration functionality

---

### 🟡 באג #2: Frequency Calculation Discrepancies
**Priority:** High
**Component:** Signal Processing / Calculations
**Environment:** Production

**Description:**
Significant discrepancies in frequency-related calculations between expected and actual values.

**Issues Found:**
1. **Frequency Resolution:**
   - Expected: 1.953 Hz (based on PRR/NFFT)
   - Actual: 15.595 Hz
   - Discrepancy: ~8x difference

2. **Frequency Bins Count:**
   - Expected: 129 bins (for NFFT=256)
   - Actual: 16 bins
   - Missing: 113 bins

3. **Lines Delta Time (lines_dt):**
   - Expected: 0.256 seconds
   - Actual: 0.039 seconds
   - Ratio: 6.55x difference

**Possible Causes:**
- Frequency decimation applied but not documented
- Different PRR value used internally
- Time compression/decimation logic

**Affected Tests:**
- test_frequency_resolution_calculation
- test_frequency_bins_count_calculation
- test_lines_dt_calculation

**Impact:** Incorrect frequency analysis and display

---

### 🟡 באג #3: Channel Grouping Inconsistency
**Priority:** Medium
**Component:** Channel Management
**Environment:** Production

**Description:**
Channels are being grouped into streams in an undocumented manner, causing confusion in channel-to-stream mapping.

**Issue:**
- Input: 8 channels (1-8)
- Output: 3 streams
- Mapping: Channels 1-3 → Stream 0, Channels 4-6 → Stream 1, Channels 7-8 → Stream 2

**Expected:**
Either 1:1 channel-to-stream mapping OR documented grouping logic

**Affected Tests:**
- test_multichannel_mapping_calculation
- test_stream_amount_calculation

**Impact:** Unexpected behavior in multi-channel configurations

---

## באגים קיימים שכבר מאומתים

### ✅ PZ-13984: Future Timestamps Accepted
- **Status:** Already reported, test confirms bug exists
- **Test:** test_time_range_validation_future_timestamps
- **Finding:** System accepts future timestamps instead of rejecting them

### ✅ PZ-13985: Live Metadata Missing Fields
- **Status:** Already reported, test confirms bug exists
- **Test:** test_live_monitoring_get_metadata
- **Missing Fields:**
  - num_samples_per_trace
  - dtype

---

## סיכום לפתיחה

| באג | עדיפות | סטטוס | פעולה |
|-----|---------|--------|--------|
| Server 500 Errors | קריטי | חדש | לפתוח מיידית |
| Frequency Calculations | גבוה | חדש | לפתוח |
| Channel Grouping | בינוני | חדש | לפתוח |
| PZ-13984 | גבוה | קיים | מאומת |
| PZ-13985 | גבוה | קיים | מאומת |

## המלצות נוספות
1. לבדוק את יציבות השרת - האם יש בעיית זיכרון/משאבים?
2. לתעד את לוגיקת החישובים והגרופינג
3. להוסיף monitoring לשרת למעקב אחר 500 errors
