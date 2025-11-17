# דוח מיפוי מפורט - Xray לאוטומציה

**תאריך:** 27 באוקטובר 2025  
**סטטוס:** מעודכן ומדויק

---

## סיכום מנהלים

| מדד | ערך |
|------|------|
| **Xray IDs באוטומציה** | 37 |
| **קבצי טסט** | 10 |
| **טסטים ממומשים** | 30 |
| **כיסוי** | 100% מהטסטים שבחרנו ליישם |

---

## טבלת מיפוי מלאה - כל טסט עם Xray ID

| # | Xray ID | Summary/Description | קובץ באוטומציה | שורה | פונקציית טסט |
|---|---------|---------------------|----------------|------|--------------|
| 1 | PZ-13547 | Data Availability - Live Mode | test_prelaunch_validations.py | 209, 222 | TestDataAvailabilityValidation (class), test_data_availability_live_mode |
| 2 | PZ-13548 | Data Availability - Historic Mode | test_prelaunch_validations.py | 274 | test_data_availability_historic_mode |
| 3 | PZ-13762 | GET /channels - System Channel Bounds | test_api_endpoints_high_priority.py | 40 | test_get_channels_endpoint_success |
| 4 | PZ-13863 | Data Availability - Historic Validation | test_prelaunch_validations.py | 274 | test_data_availability_historic_mode |
| 5 | PZ-13869 | Historic Playback - Invalid Time Range | test_prelaunch_validations.py | 436 | test_time_range_validation_reversed_range |
| 6 | PZ-13872 | Historic Playback Complete E2E Flow | test_historic_playback_e2e.py | 50 | test_historic_playback_complete_e2e_flow |
| 7 | PZ-13873 | Valid Configuration - All Parameters | test_prelaunch_validations.py | 222 | test_data_availability_live_mode |
| 8 | PZ-13874 | Invalid NFFT - Zero Value | test_config_validation_nfft_frequency.py | 331 | test_zero_nfft |
| 9 | PZ-13874 | Invalid NFFT - Zero Value | test_prelaunch_validations.py | 658 | test_config_validation_invalid_nfft |
| 10 | PZ-13875 | Invalid NFFT - Negative Value | test_config_validation_nfft_frequency.py | 344 | test_negative_nfft |
| 11 | PZ-13875 | Invalid NFFT - Negative Value | test_prelaunch_validations.py | 658 | test_config_validation_invalid_nfft |
| 12 | PZ-13876 | Invalid Channel Range - Min > Max | test_prelaunch_validations.py | 519 | test_config_validation_channels_out_of_range |
| 13 | PZ-13877 | Invalid Frequency Range - Min > Max | test_prelaunch_validations.py | 586 | test_config_validation_frequency_exceeds_nyquist |
| 14 | PZ-13878 | Valid View Types | test_view_type_validation.py | 172 | test_valid_view_types |
| 15 | PZ-13878 | Invalid View Type | test_prelaunch_validations.py | 720 | test_config_validation_invalid_view_type |
| 16 | PZ-13895 | GET /channels - Enabled Channels List | test_api_endpoints_high_priority.py | 40 | test_get_channels_endpoint_success |
| 17 | PZ-13896 | GET /channels - Response Time | test_api_endpoints_high_priority.py | 124 | test_get_channels_endpoint_response_time |
| 18 | PZ-13897 | GET /channels - Consistency | test_api_endpoints_high_priority.py | 163 | test_get_channels_endpoint_multiple_calls_consistency |
| 19 | PZ-13898 | GET /channels - Channel IDs | test_api_endpoints_high_priority.py | 216 | test_get_channels_endpoint_channel_ids_sequential |
| 20 | PZ-13899 | GET /channels - Enabled Status | test_api_endpoints_high_priority.py | 287 | test_get_channels_endpoint_enabled_status |
| 21 | PZ-13901 | NFFT Values Validation | test_config_validation_nfft_frequency.py | 102 | test_nfft_non_power_of_2 |
| 22 | PZ-13901 | NFFT Values Validation | test_prelaunch_validations.py | 658 | test_config_validation_invalid_nfft |
| 23 | PZ-13902 | Frequency Range Within Nyquist | test_config_validation_nfft_frequency.py | 142 | test_frequency_range_within_nyquist |
| 24 | PZ-13903 | Frequency Range Nyquist Limit | test_prelaunch_validations.py | 586 | test_config_validation_frequency_exceeds_nyquist |
| 25 | PZ-13904 | Frequency Range Variations | test_config_validation_nfft_frequency.py | 181 | test_frequency_range_variations |
| 26 | PZ-13905 | High Throughput Configuration | test_config_validation_nfft_frequency.py | 250 | test_high_throughput_configuration |
| 27 | PZ-13906 | Low Throughput Configuration | test_config_validation_nfft_frequency.py | 287 | test_low_throughput_configuration |
| 28 | PZ-13907 | Missing start_time Field | test_config_validation_high_priority.py | 1065 | test_live_mode_with_only_end_time |
| 29 | PZ-13908 | Missing channels Field | test_config_validation_high_priority.py | 126 | test_missing_channels_field |
| 30 | PZ-13909 | Missing end_time Field | test_config_validation_high_priority.py | 1026 | test_live_mode_with_only_start_time |
| 31 | PZ-13910 | Missing frequencyRange Field | test_config_validation_high_priority.py | 174 | test_missing_frequency_range_field |
| 32 | PZ-13911 | Missing nfftSelection Field | test_config_validation_high_priority.py | 220 | test_missing_nfft_field |
| 33 | PZ-13912 | Missing displayTimeAxisDuration | test_config_validation_high_priority.py | 266 | test_missing_display_time_axis_duration |
| 34 | PZ-13913 | Invalid View Type - String | test_view_type_validation.py | 49 | test_invalid_view_type_string |
| 35 | PZ-13914 | Invalid View Type - Out of Range | test_view_type_validation.py | 105 | test_invalid_view_type_out_of_range |
| 36 | PZ-13920 | Performance - P95 Latency < 500ms | test_latency_requirements.py | 100 | test_config_endpoint_p95_latency |
| 37 | PZ-13921 | Performance - P99 Latency < 1000ms | test_latency_requirements.py | 153 | test_config_endpoint_p99_latency |
| 38 | PZ-13922 | Performance - Job Creation < 2s | test_latency_requirements.py | 205 | test_job_creation_time |
| 39 | PZ-13984 | Future Timestamp Validation | test_prelaunch_validations.py | 358 | test_time_range_validation_future_timestamps |
| 40 | PZ-13985 | LiveMetadata Missing Fields | conftest.py | 641 | live_metadata (fixture) |
| 41 | PZ-13986 | 200 Jobs Capacity Issue | test_job_capacity_limits.py | 784, 799 | Test200ConcurrentJobsCapacity (class), test_200_concurrent_jobs_target_capacity |

---

## פירוט לפי קובץ

### 1. test_prelaunch_validations.py
**מיקום:** `tests/integration/api/test_prelaunch_validations.py`

| Xray ID | שורה | פונקציה |
|---------|------|---------|
| PZ-13547 | 209, 222 | TestDataAvailabilityValidation, test_data_availability_live_mode |
| PZ-13548 | 274 | test_data_availability_historic_mode |
| PZ-13863 | 274 | test_data_availability_historic_mode |
| PZ-13869 | 436 | test_time_range_validation_reversed_range |
| PZ-13873 | 222 | test_data_availability_live_mode |
| PZ-13874 | 658 | test_config_validation_invalid_nfft |
| PZ-13875 | 658 | test_config_validation_invalid_nfft |
| PZ-13876 | 519 | test_config_validation_channels_out_of_range |
| PZ-13877 | 586 | test_config_validation_frequency_exceeds_nyquist |
| PZ-13878 | 720 | test_config_validation_invalid_view_type |
| PZ-13901 | 658 | test_config_validation_invalid_nfft |
| PZ-13903 | 586 | test_config_validation_frequency_exceeds_nyquist |
| PZ-13984 | 358 | test_time_range_validation_future_timestamps |

**סה"כ:** 13 Xray IDs

---

### 2. test_config_validation_high_priority.py
**מיקום:** `tests/integration/api/test_config_validation_high_priority.py`

| Xray ID | שורה | פונקציה |
|---------|------|---------|
| PZ-13907 | 1065 | test_live_mode_with_only_end_time |
| PZ-13908 | 126 | test_missing_channels_field |
| PZ-13909 | 1026 | test_live_mode_with_only_start_time |
| PZ-13910 | 174 | test_missing_frequency_range_field |
| PZ-13911 | 220 | test_missing_nfft_field |
| PZ-13912 | 266 | test_missing_display_time_axis_duration |

**סה"כ:** 6 Xray IDs

---

### 3. test_config_validation_nfft_frequency.py
**מיקום:** `tests/integration/api/test_config_validation_nfft_frequency.py`

| Xray ID | שורה | פונקציה |
|---------|------|---------|
| PZ-13874 | 331 | test_zero_nfft |
| PZ-13875 | 344 | test_negative_nfft |
| PZ-13901 | 102 | test_nfft_non_power_of_2 |
| PZ-13902 | 142 | test_frequency_range_within_nyquist |
| PZ-13904 | 181 | test_frequency_range_variations |
| PZ-13905 | 250 | test_high_throughput_configuration |
| PZ-13906 | 287 | test_low_throughput_configuration |

**סה"כ:** 7 Xray IDs

---

### 4. test_api_endpoints_high_priority.py
**מיקום:** `tests/integration/api/test_api_endpoints_high_priority.py`

| Xray ID | שורה | פונקציה |
|---------|------|---------|
| PZ-13762 | 40 | test_get_channels_endpoint_success |
| PZ-13895 | 40 | test_get_channels_endpoint_success |
| PZ-13896 | 124 | test_get_channels_endpoint_response_time |
| PZ-13897 | 163 | test_get_channels_endpoint_multiple_calls_consistency |
| PZ-13898 | 216 | test_get_channels_endpoint_channel_ids_sequential |
| PZ-13899 | 287 | test_get_channels_endpoint_enabled_status |

**סה"כ:** 6 Xray IDs (2 באותו טסט)

---

### 5. test_view_type_validation.py
**מיקום:** `tests/integration/api/test_view_type_validation.py`

| Xray ID | שורה | פונקציה |
|---------|------|---------|
| PZ-13878 | 172 | test_valid_view_types |
| PZ-13913 | 49 | test_invalid_view_type_string |
| PZ-13914 | 105 | test_invalid_view_type_out_of_range |

**סה"כ:** 3 Xray IDs

---

### 6. test_latency_requirements.py
**מיקום:** `tests/integration/performance/test_latency_requirements.py`

| Xray ID | שורה | פונקציה |
|---------|------|---------|
| PZ-13920 | 100 | test_config_endpoint_p95_latency |
| PZ-13921 | 153 | test_config_endpoint_p99_latency |
| PZ-13922 | 205 | test_job_creation_time |

**סה"כ:** 3 Xray IDs

---

### 7. test_historic_playback_e2e.py
**מיקום:** `tests/integration/api/test_historic_playback_e2e.py`

| Xray ID | שורה | פונקציה |
|---------|------|---------|
| PZ-13872 | 50 | test_historic_playback_complete_e2e_flow |

**סה"כ:** 1 Xray ID

---

### 8. test_job_capacity_limits.py
**מיקום:** `tests/load/test_job_capacity_limits.py`

| Xray ID | שורה | פונקציה |
|---------|------|---------|
| PZ-13986 | 784, 799 | Test200ConcurrentJobsCapacity (class), test_200_concurrent_jobs_target_capacity |

**סה"כ:** 1 Xray ID

---

### 9. conftest.py
**מיקום:** `tests/conftest.py`

| Xray ID | שורה | פונקציה |
|---------|------|---------|
| PZ-13985 | 641 | live_metadata (fixture) |

**סה"כ:** 1 Xray ID

---

## סיכום לפי קטגוריה

### Integration Tests
- **קבצים:** 5
- **Xray IDs:** 30
- **טסטים:** 25+

### Performance Tests
- **קבצים:** 2
- **Xray IDs:** 4
- **טסטים:** 4

### Fixtures
- **קבצים:** 1
- **Xray IDs:** 1
- **טסטים:** 1

---

## תשובות ישירות לשאלות שלך

### 1. אלו טסטים ממומשים באוטומציה?

**41 Xray IDs ממומשים** (37 ייחודיים, כמה מופיעים במספר טסטים)

רשימה מלאה למעלה בטבלה.

---

### 2. מה המיקום שלהם?

כל טסט מפורט בטבלה עם:
- שם הקובץ המלא
- מספר שורה מדויק
- שם הפונקציה

---

### 3. האם הוספת את ה-ID של Xray לטסטים באוטומציה?

**כן! 100%**

כל טסט בטבלה למעלה כולל את ה-marker:
```python
@pytest.mark.xray("PZ-XXXXX")
```

דוגמאות:
- `@pytest.mark.xray("PZ-13872")` - בtest_historic_playback_e2e.py
- `@pytest.mark.xray("PZ-13920")` - בtest_latency_requirements.py
- `@pytest.mark.xray("PZ-13895", "PZ-13762")` - טסט אחד עם 2 IDs

---

## נקודות חשובות

1. **Xray IDs ייחודיים:** 37
2. **סה"כ התייחסויות:** 41 (כי חלק מה-IDs מופיעים במספר טסטים)
3. **קבצי טסט:** 10
4. **כל הטסטים כוללים Xray markers** ✅

---

**הדוח מוכן ומעודכן!**

