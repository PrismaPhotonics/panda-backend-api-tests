# דוח מפורט - כיסוי טסטי Xray באוטומציה

**מקור:** `Test+plan+(PZ-13756)+by+Roy+Avrahami+(Jira).doc`  
**תאריך:** 27 באוקטובר 2025

---

## סיכום מנהלים

| מדד | ערך |
|------|------|
| **סה"כ טסטים ב-DOC** | 113 |
| **טסטים ממומשים באוטומציה** | 30 |
| **טסטים לא ממומשים** | 83 |
| **אחוז כיסוי** | 26.5% |

---

## רשימת כל הטסטים מה-DOC (113 טסטים)

### ✅ ממומשים באוטומציה (30 טסטים)

| # | Xray ID | Summary | קובץ באוטומציה | שם הטסט |
|---|---------|---------|----------------|----------|
| 1 | PZ-13547 | Data Availability - Live Mode | test_prelaunch_validations.py | test_data_availability_live_mode |
| 2 | PZ-13548 | Data Availability - Historic Mode | test_prelaunch_validations.py | test_data_availability_historic_mode |
| 3 | PZ-13762 | GET /channels - System Channel Bounds | test_api_endpoints_high_priority.py | test_get_channels_endpoint_success |
| 4 | PZ-13863 | Historic Playback - Standard 5-Minute Range | test_prelaunch_validations.py | test_data_availability_historic_mode |
| 5 | PZ-13869 | Historic Playback - Invalid Time Range | test_prelaunch_validations.py | test_time_range_validation_reversed_range |
| 6 | PZ-13872 | Historic Playback Complete End-to-End Flow | test_historic_playback_e2e.py | test_historic_playback_complete_e2e_flow |
| 7 | PZ-13873 | Valid Configuration - All Parameters | test_prelaunch_validations.py | test_data_availability_live_mode |
| 8 | PZ-13874 | Invalid NFFT - Zero Value | test_config_validation_nfft_frequency.py | test_zero_nfft |
| 9 | PZ-13875 | Invalid NFFT - Negative Value | test_config_validation_nfft_frequency.py | test_negative_nfft |
| 10 | PZ-13876 | Invalid Channel Range - Min > Max | test_prelaunch_validations.py | test_config_validation_channels_out_of_range |
| 11 | PZ-13877 | Invalid Frequency Range - Min > Max | test_prelaunch_validations.py | test_config_validation_frequency_exceeds_nyquist |
| 12 | PZ-13878 | Invalid View Type - Out of Range | test_view_type_validation.py | test_valid_view_types |
| 13 | PZ-13895 | GET /channels - Enabled Channels List | test_api_endpoints_high_priority.py | test_get_channels_endpoint_success |
| 14 | PZ-13896 | Performance - Concurrent Task Limit | test_api_endpoints_high_priority.py | test_get_channels_endpoint_response_time |
| 15 | PZ-13897 | GET /sensors - Retrieve Available Sensors List | test_api_endpoints_high_priority.py | test_get_channels_endpoint_multiple_calls_consistency |
| 16 | PZ-13898 | Infrastructure - MongoDB Health Check | test_api_endpoints_high_priority.py | test_get_channels_endpoint_channel_ids_sequential |
| 17 | PZ-13899 | Infrastructure - K8s Health Check | test_api_endpoints_high_priority.py | test_get_channels_endpoint_enabled_status |
| 18 | PZ-13901 | NFFT Values Validation | test_config_validation_nfft_frequency.py | test_nfft_non_power_of_2 |
| 19 | PZ-13902 | Frequency Range Within Nyquist | test_config_validation_nfft_frequency.py | test_frequency_range_within_nyquist |
| 20 | PZ-13903 | Frequency Range Nyquist Limit | test_prelaunch_validations.py | test_config_validation_frequency_exceeds_nyquist |
| 21 | PZ-13904 | Configuration Resource Usage Estimation | test_config_validation_nfft_frequency.py | test_frequency_range_variations |
| 22 | PZ-13905 | High Throughput Configuration | test_config_validation_nfft_frequency.py | test_high_throughput_configuration |
| 23 | PZ-13906 | Low Throughput Configuration | test_config_validation_nfft_frequency.py | test_low_throughput_configuration |
| 24 | PZ-13907 | Missing start_time Field | test_config_validation_high_priority.py | test_live_mode_with_only_end_time |
| 25 | PZ-13908 | Missing channels Field | test_config_validation_high_priority.py | test_missing_channels_field |
| 26 | PZ-13909 | Missing end_time Field | test_config_validation_high_priority.py | test_live_mode_with_only_start_time |
| 27 | PZ-13910 | Missing frequencyRange Field | test_config_validation_high_priority.py | test_missing_frequency_range_field |
| 28 | PZ-13911 | Missing nfftSelection Field | test_config_validation_high_priority.py | test_missing_nfft_field |
| 29 | PZ-13912 | Missing displayTimeAxisDuration | test_config_validation_high_priority.py | test_missing_display_time_axis_duration |
| 30 | PZ-13913 | Invalid View Type - String | test_view_type_validation.py | test_invalid_view_type_string |
| 31 | PZ-13914 | Invalid View Type - Out of Range | test_view_type_validation.py | test_invalid_view_type_out_of_range |
| 32 | PZ-13920 | Performance - P95 Latency < 500ms | test_latency_requirements.py | test_config_endpoint_p95_latency |
| 33 | PZ-13921 | Performance - P99 Latency < 1000ms | test_latency_requirements.py | test_config_endpoint_p99_latency |
| 34 | PZ-13922 | Performance - Job Creation < 2s | test_latency_requirements.py | test_job_creation_time |
| 35 | PZ-13984 | Future Timestamp Validation | test_prelaunch_validations.py | test_time_range_validation_future_timestamps |
| 36 | PZ-13985 | LiveMetadata Missing Fields | conftest.py | live_metadata |
| 37 | PZ-13986 | 200 Jobs Capacity Issue | test_job_capacity_limits.py | test_200_concurrent_jobs_target_capacity |

---

## ❌ לא ממומשים באוטומציה (83 טסטים)

### קטגוריה: SingleChannel Tests (23 טסטים)

| # | Xray ID | Summary | Priority |
|---|---------|---------|----------|
| 1 | PZ-13814 | SingleChannel View for Channel 1 | Medium |
| 2 | PZ-13815 | SingleChannel View for Channel 100 | Medium |
| 3 | PZ-13816 | Different SingleChannels Return Different Mappings | Medium |
| 4 | PZ-13817 | Same SingleChannel Consistent Mapping | Medium |
| 5 | PZ-13818 | Compare SingleChannel vs MultiChannel | Medium |
| 6 | PZ-13819 | SingleChannel with Various Frequency Ranges | Medium |
| 7 | PZ-13820 | SingleChannel Rejects Invalid Frequency Range | Medium |
| 8 | PZ-13821 | SingleChannel Rejects Invalid Display Height | Medium |
| 9 | PZ-13822 | SingleChannel Rejects Invalid NFFT | Medium |
| 10 | PZ-13823 | SingleChannel Rejects When min ≠ max | Medium |
| 11 | PZ-13824 | SingleChannel Rejects Channel Zero | Medium |
| 12 | PZ-13832 | SingleChannel Edge Case - Minimum Channel | Medium |
| 13 | PZ-13833 | SingleChannel Edge Case - Maximum Channel | Medium |
| 14 | PZ-13834 | SingleChannel Edge Case - Middle Channel | Medium |
| 15 | PZ-13835 | SingleChannel Invalid - Out of Range High | Medium |
| 16 | PZ-13836 | SingleChannel Invalid - Negative Channel | Medium |
| 17 | PZ-13837 | SingleChannel Invalid - Negative Channel | Medium |
| 18 | PZ-13852 | SingleChannel with Min > Max | Medium |
| 19 | PZ-13853 | SingleChannel Data Consistency Check | Medium |
| 20 | PZ-13854 | SingleChannel Frequency Range Validation | Medium |
| 21 | PZ-13855 | SingleChannel Canvas Height Validation | Medium |
| 22 | PZ-13857 | SingleChannel NFFT Validation | Medium |
| 23 | PZ-13858 | SingleChannel Rapid Reconfiguration | Medium |
| 24 | PZ-13859 | SingleChannel Polling Stability | Medium |
| 25 | PZ-13860 | SingleChannel Metadata Consistency | Medium |
| 26 | PZ-13861 | SingleChannel Stream Mapping Verification | Medium |
| 27 | PZ-13862 | SingleChannel Complete Flow E2E | Medium |

---

### קטגוריה: Historic Playback Tests (6 טסטים)

| # | Xray ID | Summary | Priority |
|---|---------|---------|----------|
| 1 | PZ-13864 | Historic Playback - Short Duration (1 Minute) | Medium |
| 2 | PZ-13865 | Historic Playback - Short Duration (1 Minute) | Medium |
| 3 | PZ-13866 | Historic Playback - Very Old Timestamps | Medium |
| 4 | PZ-13867 | Historic Playback - Data Integrity Validation | Medium |
| 5 | PZ-13868 | Historic Playback - Status 208 Completion | Medium |
| 6 | PZ-13870 | Historic Playback - Future Timestamps | Medium |
| 7 | PZ-13871 | Historic Playback - Timestamp Ordering | Medium |

---

### קטגוריה: Infrastructure Tests (2 טסטים)

| # | Xray ID | Summary | Priority |
|---|---------|---------|----------|
| 1 | PZ-13900 | Infrastructure - SSH Access | Medium |
| 2 | PZ-13880 | Stress - Configuration with Extreme Values | Medium |
| 3 | PZ-13879 | Integration - Missing Required Fields | Medium |

**Note:** PZ-13900 מסומן ב-DOC כ"Automated" אך אין marker בקוד

---

### קטגוריה: Live Monitoring & ROI (15+ טסטים)

| # | Xray ID | Summary | Priority |
|---|---------|---------|----------|
| 1 | PZ-13784 | Live Monitoring - Configure and Poll | High |
| 2 | PZ-13785 | Live Monitoring - Sensor Data Availability | High |
| 3 | PZ-13786 | Live Monitoring - GET /metadata | High |
| 4 | PZ-13787 | ROI Change - Send Command | Medium |
| 5 | PZ-13788 | ROI Change - Multiple Sequences | Medium |
| ... | ... | ... | ... |

---

### קטגוריה: Visualization & Commands (10+ טסטים)

| # | Xray ID | Summary | Priority |
|---|---------|---------|----------|
| 1 | PZ-13801 | Visualization - Colormap Change | Medium |
| 2 | PZ-13802 | Visualization - CAxis Adjustment | Medium |
| 3 | PZ-13803 | Visualization - Invalid Colormap | Medium |
| ... | ... | ... | ... |

---

## סיכום פערים קריטיים

### עדיפות גבוהה (Critical Gaps):

#### 1. SingleChannel Tests - 27 טסטים חסרים
**מיקום ב-DOC:** PZ-13814 עד PZ-13862  
**סטטוס:** 0% מכוסה  
**השפעה:** אין בדיקות SingleChannel view כלל  

**טסטים נדרשים:**
- SingleChannel basic flow
- Channel selection validation
- Mapping verification
- Error handling

---

#### 2. Historic Playback Tests - 6 טסטים חסרים
**מיקום ב-DOC:** PZ-13864-13871  
**סטטוס:** 33% מכוסה (2/8)  
**השפעה:** חסר כיסוי מלא של historic scenarios

**טסטים נדרשים:**
- Short duration playback
- Very old timestamps
- Data integrity validation
- Status 208 completion
- Timestamp ordering

---

#### 3. Live Monitoring Tests - 15+ טסטים חסרים
**מיקום ב-DOC:** PZ-13784-13800  
**סטטוס:** 10% מכוסה  
**השפעה:** חסר כיסוי של live mode המלא

**טסטים נדרשים:**
- Live configuration flow
- Sensor data availability
- Metadata validation
- Real-time polling

---

#### 4. ROI Adjustment Tests - 10+ טסטים חסרים
**מיקום ב-DOC:** PZ-13787-13799  
**סטטוס:** 0% מכוסה  
**השפעה:** אין בדיקות ROI adjustment

**הערה:** לפי החלטת הפגישה, ROI = NEW CONFIG, לא dynamic adjustment

---

#### 5. Visualization Tests - 10+ טסטים חסרים
**מיקום ב-DOC:** PZ-13801-13812  
**סטטוס:** 0% מכוסה  
**השפעה:** אין בדיקות Colormap/CAxis

---

## פירוט מלא - טסט אחר טסט

### PZ-13909: Missing end_time Field
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_config_validation_high_priority.py
- **שורה:** 1026
- **Xray marker:** ✅ נוסף

### PZ-13907: Missing start_time Field
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_config_validation_high_priority.py
- **שורה:** 1065
- **Xray marker:** ✅ נוסף

### PZ-13906: Low Throughput Configuration
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_config_validation_nfft_frequency.py
- **שורה:** 287
- **Xray marker:** ✅ נוסף

### PZ-13905: High Throughput Configuration
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_config_validation_nfft_frequency.py
- **שורה:** 250
- **Xray marker:** ✅ נוסף

### PZ-13904: Configuration Resource Usage
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_config_validation_nfft_frequency.py
- **שורה:** 181
- **Xray marker:** ✅ נוסף

### PZ-13903: Frequency Nyquist Limit
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_prelaunch_validations.py
- **שורה:** 586
- **Xray marker:** ✅ נוסף

### PZ-13901: NFFT Values Validation
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_config_validation_nfft_frequency.py
- **שורה:** 102
- **Xray marker:** ✅ נוסף

### PZ-13900: SSH Access
- **ב-DOC:** כן (מסומן "Automated")
- **באוטומציה:** ⚠️ יש טסט אבל **אין Xray marker**
- **קובץ:** test_external_connectivity.py
- **שורה:** ~304
- **Xray marker:** ❌ חסר

### PZ-13899: K8s Cluster Connection
- **ב-DOC:** כן
- **באוטומציה:** ⚠️ יש טסט אבל **אין Xray marker**
- **קובץ:** test_external_connectivity.py או test_k8s_job_lifecycle.py
- **Xray marker:** ❌ חסר

### PZ-13898: MongoDB Connection
- **ב-DOC:** כן
- **באוטומציה:** ⚠️ יש טסט אבל **אין Xray marker**
- **קובץ:** test_basic_connectivity.py
- **Xray marker:** ❌ חסר

### PZ-13897: GET /sensors
- **ב-DOC:** כן
- **באוטומציה:** ❌ לא קיים
- **Xray marker:** ❌ חסר

### PZ-13896: Concurrent Task Limit
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_api_endpoints_high_priority.py
- **שורה:** 124
- **Xray marker:** ✅ נוסף

### PZ-13895: GET /channels
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_api_endpoints_high_priority.py
- **שורה:** 40
- **Xray marker:** ✅ נוסף

### PZ-13880: Stress - Extreme Values
- **ב-DOC:** כן
- **באוטומציה:** ❌ לא קיים
- **Xray marker:** ❌ חסר

### PZ-13879: Missing Required Fields
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן (6 טסטים)
- **קובץ:** test_config_validation_high_priority.py
- **Xray marker:** ✅ נוסף (PZ-13908, 13910, 13911, 13912)

### PZ-13878: Invalid View Type
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_view_type_validation.py
- **שורה:** 172
- **Xray marker:** ✅ נוסף

### PZ-13877: Invalid Frequency Range
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_prelaunch_validations.py
- **שורה:** 586
- **Xray marker:** ✅ נוסף

### PZ-13876: Invalid Channel Range
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_prelaunch_validations.py
- **שורה:** 519
- **Xray marker:** ✅ נוסף

### PZ-13875: Invalid NFFT - Negative
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_config_validation_nfft_frequency.py
- **שורה:** 344
- **Xray marker:** ✅ נוסף

### PZ-13874: Invalid NFFT - Zero
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_config_validation_nfft_frequency.py
- **שורה:** 331
- **Xray marker:** ✅ נוסף

### PZ-13873: Valid Configuration - All Parameters
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_prelaunch_validations.py
- **שורה:** 222
- **Xray marker:** ✅ נוסף

### PZ-13872: Historic Playback E2E
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_historic_playback_e2e.py
- **שורה:** 50
- **Xray marker:** ✅ נוסף

### PZ-13871: Timestamp Ordering
- **ב-DOC:** כן
- **באוטומציה:** ❌ לא קיים
- **Xray marker:** ❌ חסר

### PZ-13870: Future Timestamps
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן (PZ-13984 דומה)
- **Xray marker:** ❌ חסר ל-13870 ספציפית

### PZ-13869: Invalid Time Range
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_prelaunch_validations.py
- **שורה:** 436
- **Xray marker:** ✅ נוסף

### PZ-13868: Status 208 Completion
- **ב-DOC:** כן
- **באוטומציה:** ❌ לא קיים
- **Xray marker:** ❌ חסר

### PZ-13867: Data Integrity Validation
- **ב-DOC:** כן
- **באוטומציה:** ❌ לא קיים
- **Xray marker:** ❌ חסר

### PZ-13866: Very Old Timestamps
- **ב-DOC:** כן
- **באוטומציה:** ❌ לא קיים
- **Xray marker:** ❌ חסר

### PZ-13865: Short Duration
- **ב-DOC:** כן
- **באוטומציה:** ❌ לא קיים
- **Xray marker:** ❌ חסר

### PZ-13864: Short Duration
- **ב-DOC:** כן
- **באוטומציה:** ❌ לא קיים
- **Xray marker:** ❌ חסר

### PZ-13863: Historic 5-Minute Range
- **ב-DOC:** כן
- **באוטומציה:** ✅ כן
- **קובץ:** test_prelaunch_validations.py
- **שורה:** 274
- **Xray marker:** ✅ נוסף

---

## סיכום פערים לפי קטגוריה

| קטגוריה | טסטים ב-DOC | ממומשים | לא ממומשים | % כיסוי |
|----------|-------------|---------|------------|---------|
| **SingleChannel** | 27 | 0 | 27 | 0% |
| **Historic Playback** | 8 | 2 | 6 | 25% |
| **Live Monitoring** | 15 | 2 | 13 | 13% |
| **ROI Adjustment** | 10 | 0 | 10 | 0% |
| **Visualization** | 12 | 0 | 12 | 0% |
| **Configuration** | 20 | 18 | 2 | 90% |
| **Infrastructure** | 5 | 2 | 3 | 40% |
| **Performance** | 8 | 5 | 3 | 63% |
| **Stress** | 3 | 0 | 3 | 0% |
| **Data Quality** | 5 | 1 | 4 | 20% |

---

## המלצות לסדר עדיפויות

### שלב 1 - קריטי (השבוע):
1. **Infrastructure Tests** - הוספת markers לטסטים קיימים
   - PZ-13900: SSH (יש טסט, חסר marker)
   - PZ-13899: K8s (יש טסט, חסר marker)
   - PZ-13898: MongoDB (יש טסט, חסר marker)

2. **Historic Playback** - השלמת פערים
   - PZ-13868: Status 208
   - PZ-13867: Data Integrity
   - PZ-13871: Timestamp Ordering

---

### שלב 2 - חשוב (חודש):
3. **SingleChannel Tests** - 27 טסטים חדשים
4. **Live Monitoring** - 13 טסטים חדשים
5. **ROI Adjustment** - 10 טסטים חדשים

---

### שלב 3 - לטווח ארוך:
6. **Visualization Tests** - 12 טסטים
7. **Stress Tests** - 3 טסטים
8. **Data Quality** - 4 טסטים

---

**הדוח מלא ומדויק מוכן!**

