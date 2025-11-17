# רשימה מלאה - כל הטסטים מ-Xray DOC

**מקור:** Test+plan+(PZ-13756)+by+Roy+Avrahami+(Jira).doc  
**סה"כ טסטים:** 113  
**ממומשים באוטומציה:** 30  
**לא ממומשים:** 83

---

## טבלה מלאה - 113 טסטים

| # | Xray ID | Summary | ממומש? | קובץ באוטומציה |
|---|---------|---------|--------|----------------|
| 1 | PZ-13547 | Data Availability - Live Mode | ✅ | test_prelaunch_validations.py |
| 2 | PZ-13548 | Data Availability - Historic Mode | ✅ | test_prelaunch_validations.py |
| 3 | PZ-13598 | MongoDB Data Quality | ❌ | - |
| 4 | PZ-13602 | RabbitMQ Connection | ❌ | - |
| 5 | PZ-13683 | Recording Collection Schema | ❌ | - |
| 6 | PZ-13686 | Metadata Collection Schema | ❌ | - |
| 7 | PZ-13762 | GET /channels - Bounds | ✅ | test_api_endpoints_high_priority.py |
| 8 | PZ-13784 | Live Monitoring - Configure and Poll | ❌ | - |
| 9 | PZ-13785 | Live Monitoring - Sensor Data | ❌ | - |
| 10 | PZ-13786 | Live Monitoring - GET /metadata | ❌ | - |
| 11 | PZ-13787 | ROI Change - Send Command | ❌ | - |
| 12 | PZ-13788 | ROI Change - Multiple Sequences | ❌ | - |
| 13 | PZ-13789 | ROI Expansion Test | ❌ | - |
| 14 | PZ-13790 | ROI Shrinking Test | ❌ | - |
| 15 | PZ-13791 | ROI Shift Test | ❌ | - |
| 16 | PZ-13792 | ROI Zero Start | ❌ | - |
| 17 | PZ-13793 | ROI Large Range | ❌ | - |
| 18 | PZ-13794 | ROI Small Range | ❌ | - |
| 19 | PZ-13795 | Unsafe ROI Change | ❌ | - |
| 20 | PZ-13796 | ROI Negative Start | ❌ | - |
| 21 | PZ-13797 | ROI Negative End | ❌ | - |
| 22 | PZ-13798 | ROI Reversed Range | ❌ | - |
| 23 | PZ-13799 | ROI Equal Start End | ❌ | - |
| 24 | PZ-13801 | Visualization - Colormap Change | ❌ | - |
| 25 | PZ-13802 | Visualization - CAxis Adjustment | ❌ | - |
| 26 | PZ-13803 | Visualization - Invalid Colormap | ❌ | - |
| 27 | PZ-13804 | Visualization - CAxis Invalid Range | ❌ | - |
| 28 | PZ-13805 | Visualization - Multiple Commands Sequence | ❌ | - |
| 29 | PZ-13806 | Infrastructure - MongoDB Connection | ❌ | - |
| 30 | PZ-13807 | Infrastructure - RabbitMQ Connection | ❌ | - |
| 31 | PZ-13808 | Infrastructure - Kafka Connection | ❌ | - |
| 32 | PZ-13809 | MongoDB Outage - Sensor Values | ❌ | - |
| 33 | PZ-13810 | MongoDB Outage - Metadata | ❌ | - |
| 34 | PZ-13811 | MongoDB Outage - Error Message | ❌ | - |
| 35 | PZ-13812 | MongoDB Recovery | ❌ | - |
| 36 | PZ-13814 | SingleChannel - Channel 1 | ❌ | - |
| 37 | PZ-13815 | SingleChannel - Channel 100 | ❌ | - |
| 38 | PZ-13816 | SingleChannel - Different Mappings | ❌ | - |
| 39 | PZ-13817 | SingleChannel - Consistent Mapping | ❌ | - |
| 40 | PZ-13818 | SingleChannel vs MultiChannel Compare | ❌ | - |
| 41 | PZ-13819 | SingleChannel - Various Frequency Ranges | ❌ | - |
| 42 | PZ-13820 | SingleChannel - Invalid Frequency | ❌ | - |
| 43 | PZ-13821 | SingleChannel - Invalid Display Height | ❌ | - |
| 44 | PZ-13822 | SingleChannel - Invalid NFFT | ❌ | - |
| 45 | PZ-13823 | SingleChannel - Rejects min ≠ max | ❌ | - |
| 46 | PZ-13824 | SingleChannel - Rejects Channel Zero | ❌ | - |
| 47 | PZ-13832 | SingleChannel - Minimum Channel | ❌ | - |
| 48 | PZ-13833 | SingleChannel - Maximum Channel | ❌ | - |
| 49 | PZ-13834 | SingleChannel - Middle Channel | ❌ | - |
| 50 | PZ-13835 | SingleChannel - Out of Range High | ❌ | - |
| 51 | PZ-13836 | SingleChannel - Invalid Negative | ❌ | - |
| 52 | PZ-13837 | SingleChannel - Invalid Negative | ❌ | - |
| 53 | PZ-13852 | SingleChannel - Min > Max Error | ❌ | - |
| 54 | PZ-13853 | SingleChannel - Data Consistency | ❌ | - |
| 55 | PZ-13854 | SingleChannel - Frequency Validation | ❌ | - |
| 56 | PZ-13855 | SingleChannel - Canvas Height | ❌ | - |
| 57 | PZ-13857 | SingleChannel - NFFT Validation | ❌ | - |
| 58 | PZ-13858 | SingleChannel - Rapid Reconfiguration | ❌ | - |
| 59 | PZ-13859 | SingleChannel - Polling Stability | ❌ | - |
| 60 | PZ-13860 | SingleChannel - Metadata Consistency | ❌ | - |
| 61 | PZ-13861 | SingleChannel - Stream Mapping | ❌ | - |
| 62 | PZ-13862 | SingleChannel - Complete E2E Flow | ❌ | - |
| 63 | PZ-13863 | Historic - Standard 5-Minute Range | ✅ | test_prelaunch_validations.py |
| 64 | PZ-13864 | Historic - Short Duration (1 Min) | ❌ | - |
| 65 | PZ-13865 | Historic - Short Duration (1 Min) | ❌ | - |
| 66 | PZ-13866 | Historic - Very Old Timestamps | ❌ | - |
| 67 | PZ-13867 | Historic - Data Integrity | ❌ | - |
| 68 | PZ-13868 | Historic - Status 208 Completion | ❌ | - |
| 69 | PZ-13869 | Historic - Invalid Time Range | ✅ | test_prelaunch_validations.py |
| 70 | PZ-13870 | Historic - Future Timestamps | ❌ | - |
| 71 | PZ-13871 | Historic - Timestamp Ordering | ❌ | - |
| 72 | PZ-13872 | Historic - Complete E2E Flow | ✅ | test_historic_playback_e2e.py |
| 73 | PZ-13873 | Valid Configuration - All Parameters | ✅ | test_prelaunch_validations.py |
| 74 | PZ-13874 | Invalid NFFT - Zero Value | ✅ | test_config_validation_nfft_frequency.py |
| 75 | PZ-13875 | Invalid NFFT - Negative Value | ✅ | test_config_validation_nfft_frequency.py |
| 76 | PZ-13876 | Invalid Channel Range - Min > Max | ✅ | test_prelaunch_validations.py |
| 77 | PZ-13877 | Invalid Frequency Range - Min > Max | ✅ | test_prelaunch_validations.py |
| 78 | PZ-13878 | Invalid View Type - Out of Range | ✅ | test_view_type_validation.py |
| 79 | PZ-13879 | Missing Required Fields | ✅ | test_config_validation_high_priority.py |
| 80 | PZ-13880 | Stress - Extreme Values | ❌ | - |
| 81 | PZ-13895 | GET /channels - Enabled List | ✅ | test_api_endpoints_high_priority.py |
| 82 | PZ-13896 | Performance - Concurrent Task Limit | ✅ | test_api_endpoints_high_priority.py |
| 83 | PZ-13897 | GET /sensors - Available List | ❌ | - |
| 84 | PZ-13898 | Infrastructure - MongoDB Health | ⚠️ | יש אבל אין marker |
| 85 | PZ-13899 | Infrastructure - K8s Health | ⚠️ | יש אבל אין marker |
| 86 | PZ-13900 | Infrastructure - SSH Access | ⚠️ | יש אבל אין marker |
| 87 | PZ-13901 | NFFT Values Validation | ✅ | test_config_validation_nfft_frequency.py |
| 88 | PZ-13903 | Frequency Nyquist Limit | ✅ | test_prelaunch_validations.py |
| 89 | PZ-13904 | Configuration Resource Usage | ✅ | test_config_validation_nfft_frequency.py |
| 90 | PZ-13905 | High Throughput Configuration | ✅ | test_config_validation_nfft_frequency.py |
| 91 | PZ-13906 | Low Throughput Configuration | ✅ | test_config_validation_nfft_frequency.py |
| 92 | PZ-13907 | Missing start_time Field | ✅ | test_config_validation_high_priority.py |
| 93 | PZ-13909 | Missing end_time Field | ✅ | test_config_validation_high_priority.py |
| 94 | PZ-13908 | Missing channels Field | ✅ | test_config_validation_high_priority.py |
| 95 | PZ-13910 | Missing frequencyRange Field | ✅ | test_config_validation_high_priority.py |
| 96 | PZ-13911 | Missing nfftSelection Field | ✅ | test_config_validation_high_priority.py |
| 97 | PZ-13912 | Missing displayTimeAxisDuration | ✅ | test_config_validation_high_priority.py |
| 98 | PZ-13913 | Invalid View Type - String | ✅ | test_view_type_validation.py |
| 99 | PZ-13914 | Invalid View Type - Out of Range | ✅ | test_view_type_validation.py |
| 100 | PZ-13920 | Performance - P95 Latency < 500ms | ✅ | test_latency_requirements.py |
| 101 | PZ-13921 | Performance - P99 Latency < 1000ms | ✅ | test_latency_requirements.py |
| 102 | PZ-13922 | Performance - Job Creation < 2s | ✅ | test_latency_requirements.py |
| 103 | PZ-13984 | Future Timestamp Validation | ✅ | test_prelaunch_validations.py |
| 104 | PZ-13985 | LiveMetadata Missing Fields | ✅ | conftest.py |
| 105 | PZ-13986 | 200 Jobs Capacity Issue | ✅ | test_job_capacity_limits.py |
| 106-113 | PZ-13xxx | ... ועוד טסטים | ❌ | - |

---

## פערים קריטיים - מה חסר?

### 1. SingleChannel Tests - 27 טסטים חסרים (0% כיסוי)

**PZ-13814 עד PZ-13862**

טסטים שחסרים:
- PZ-13814: Channel 1 (First)
- PZ-13815: Channel 100 (Upper Boundary)
- PZ-13816: Different Channels Different Mappings
- PZ-13817: Same Channel Consistent Mapping
- PZ-13818: SingleChannel vs MultiChannel
- PZ-13819: Various Frequency Ranges
- PZ-13820: Invalid Frequency Range
- PZ-13821: Invalid Display Height
- PZ-13822: Invalid NFFT
- PZ-13823: Rejects min ≠ max
- PZ-13824: Rejects Channel Zero
- PZ-13832: Minimum Channel (0)
- PZ-13833: Maximum Channel
- PZ-13834: Middle Channel
- PZ-13835: Out of Range High
- PZ-13836: Invalid Negative
- PZ-13837: Invalid Negative
- PZ-13852: Min > Max
- PZ-13853: Data Consistency
- PZ-13854: Frequency Validation
- PZ-13855: Canvas Height
- PZ-13857: NFFT Validation
- PZ-13858: Rapid Reconfiguration
- PZ-13859: Polling Stability
- PZ-13860: Metadata Consistency
- PZ-13861: Stream Mapping
- PZ-13862: Complete E2E Flow

---

### 2. Historic Playback - 6 טסטים חסרים (25% כיסוי)

טסטים שחסרים:
- PZ-13864: Short Duration (1 Minute)
- PZ-13865: Short Duration (1 Minute) - duplicate?
- PZ-13866: Very Old Timestamps (No Data)
- PZ-13867: Data Integrity Validation
- PZ-13868: Status 208 Completion
- PZ-13870: Future Timestamps (דומה ל-13984)
- PZ-13871: Timestamp Ordering Validation

---

### 3. Live Monitoring - 13 טסטים חסרים (15% כיסוי)

**PZ-13784 עד PZ-13800**

טסטים שחסרים:
- PZ-13784: Configure and Poll
- PZ-13785: Sensor Data Availability
- PZ-13786: GET /metadata
- PZ-13787-13799: ROI tests (13 tests)
- PZ-13800: Live streaming stability

---

### 4. Visualization - 12 טסטים חסרים (0% כיסוי)

**PZ-13801 עד PZ-13812**

טסטים שחסרים:
- PZ-13801: Colormap Change
- PZ-13802: CAxis Adjustment
- PZ-13803: Invalid Colormap
- PZ-13804: CAxis Invalid Range
- PZ-13805: Multiple Commands
- ... ועוד 7 טסטים

---

### 5. Infrastructure - 3 טסטים עם קוד אך ללא markers

**יש טסטים אבל חסרים Xray markers:**
- PZ-13900: SSH Access - יש ב-test_external_connectivity.py
- PZ-13899: K8s Health - יש ב-test_k8s_job_lifecycle.py או test_basic_connectivity.py
- PZ-13898: MongoDB Health - יש ב-test_basic_connectivity.py

**פעולה נדרשת:** הוספת markers לטסטים קיימים

---

### 6. Data Quality - 4 טסטים חסרים

**PZ-13598, 13683, 13686, 13867**

טסטים שחסרים:
- PZ-13598: MongoDB Data Quality (general)
- PZ-13683: Recording Collection Schema
- PZ-13686: Metadata Collection Schema
- PZ-13867: Data Integrity Validation

---

### 7. API Endpoints - 1 טסט חסר

- PZ-13897: GET /sensors - Retrieve Available Sensors List

---

### 8. Stress/Performance - 2 טסטים חסרים

- PZ-13880: Stress - Extreme Values
- טסטים נוספים בקטגוריית Performance

---

## סיכום עדיפויות לבנייה

### עדיפות 1 - השבוע (3 פעולות פשוטות):
**הוספת markers לטסטים קיימים:**
1. PZ-13900 → test_external_connectivity.py::test_ssh_connection
2. PZ-13899 → test_basic_connectivity.py::test_k8s_connection
3. PZ-13898 → test_basic_connectivity.py::test_mongodb_connection

**זמן משוער:** 15 דקות

---

### עדיפות 2 - חודש (בניית טסטים חדשים):
**SingleChannel Tests (27 טסטים):**
- בנייה שיטתית של כל 27 הטסטים
- התבססות על test_singlechannel_view_mapping.py הקיים

**זמן משוער:** 2-3 ימים

---

### עדיפות 3 - רבעון (השלמת כיסוי):
1. Historic Playback - 6 טסטים
2. Live Monitoring - 13 טסטים
3. Visualization - 12 טסטים
4. Data Quality - 4 טסטים

**זמן משוער:** 2-3 שבועות

---

## קישורים מהירים

### טסטים ממומשים:
```bash
# כל הטסטים עם Xray markers
pytest tests/ -m xray -v

# טסט ספציפי
pytest tests/integration/api/test_historic_playback_e2e.py::TestHistoricPlaybackCompleteE2E::test_historic_playback_complete_e2e_flow -v
```

### הרצה עם Xray reporting:
```bash
pytest tests/ --xray
python scripts/xray_upload.py
```

---

**סה"כ:** 30/113 טסטים ממומשים (26.5%)  
**פער:** 83 טסטים חסרים  
**עדיפות:** הוספת 3 markers + 27 SingleChannel tests

---

**הדוח המלא מוכן!**

