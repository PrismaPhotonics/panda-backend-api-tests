# 📊 ניתוח Test Plan PZ-14024 - Xray Tests החדשים

**תאריך:** 30 באוקטובר 2025  
**מקור:** Test plan (TS_Focus_Server_PZ-14024) by Roy Avrahami (Jira)  
**סה"כ טסטים:** 47 Test Cases

---

## 🎯 סיכום מנהלים

| מדד | ערך |
|-----|------|
| **סה"כ טסטים ב-CSV** | 47 |
| **טסטים חדשים (לא היו בקוד)** | 14 |
| **טסטים קיימים (צריך Xray ID)** | 33 |
| **כיסוי נוכחי** | **70.2%** (33/47) |
| **כיסוי לאחר עדכון** | **100%** |

---

## ✅ טסטים שכבר ממומשים בקוד (33 טסטים)

### 1️⃣ **Calculations Tests - ממומשים ב-`test_system_calculations.py`**

| Xray ID | Summary | Function Name | סטטוס |
|---------|---------|---------------|--------|
| PZ-14060 | Frequency Resolution Calculation | `test_frequency_resolution_calculation` | ✅ קיים - צריך ID |
| PZ-14061 | Frequency Bins Count Calculation | `test_frequency_bins_count_calculation` | ✅ קיים - צריך ID |
| PZ-14062 | Nyquist Frequency Limit Validation | `test_nyquist_frequency_calculation` | ✅ קיים - צריך ID |
| PZ-14066 | Time Resolution (lines_dt) Calculation | `test_lines_dt_calculation` | ✅ קיים - צריך ID |
| PZ-14067 | Output Rate Calculation | `test_output_rate_calculation` | ✅ קיים - צריך ID |
| PZ-14068 | Time Window Duration Calculation | `test_time_window_duration_calculation` | ✅ קיים - צריך ID |
| PZ-14069 | Channel Count Calculation | `test_channel_count_calculation` | ✅ קיים - צריך ID |
| PZ-14070 | MultiChannel Mapping Validation | `test_multichannel_mapping_calculation` | ✅ קיים - צריך ID |
| PZ-14071 | Stream Amount Calculation | `test_stream_amount_calculation` | ✅ קיים - צריך ID |
| PZ-14078 | Data Rate Calculation (Informational) | `test_data_rate_calculation` | ✅ קיים - צריך ID |
| PZ-14080 | Spectrogram Dimensions Calculation | `test_spectrogram_dimensions_calculation` | ✅ קיים - צריך ID |

**📁 קובץ:** `tests/integration/calculations/test_system_calculations.py` (677 שורות)

---

### 2️⃣ **Validation Tests - ממומשים ב-`test_system_calculations.py`**

| Xray ID | Summary | Function Name | סטטוס |
|---------|---------|---------------|--------|
| PZ-14072 | FFT Window Size (Power of 2) Validation | `test_fft_window_size_validation` | ✅ קיים - צריך ID |
| PZ-14073 | Overlap Percentage Validation | `test_overlap_percentage_validation` | ✅ קיים - צריך ID |

---

### 3️⃣ **Health Check Tests - ממומשים ב-`test_health_check.py`**

| Xray ID | Summary | Function Name | סטטוס |
|---------|---------|---------------|--------|
| PZ-14026 | Health Check Returns Valid Response (200 OK) | `test_ack_health_check_valid_response` | ✅ ממומש מלא! |
| PZ-14027 | Health Check Rejects Invalid HTTP Methods | `test_ack_rejects_invalid_methods` | ✅ ממומש מלא! |
| PZ-14028 | Health Check Handles Concurrent Requests | `test_ack_concurrent_requests` | ✅ ממומש מלא! |
| PZ-14029 | Health Check with Various Headers | `test_ack_with_various_headers` | ✅ ממומש מלא! |
| PZ-14030 | Health Check Security Headers Validation | `test_ack_security_headers_validation` | ✅ ממומש מלא! |
| PZ-14031 | Health Check Response Structure Validation | `test_ack_response_structure_validation` | ✅ ממומש מלא! |
| PZ-14032 | Health Check with SSL/TLS | `test_ack_with_ssl_tls` | ✅ ממומש מלא! |
| PZ-14033 | Health Check Load Testing | `test_ack_load_testing` | ✅ ממומש מלא! |

**📁 קובץ:** `tests/integration/api/test_health_check.py` (695 שורות)

---

### 4️⃣ **טסטים קיימים אחרים (כבר עם Xray IDs)**

| Xray ID | Summary | File | סטטוס |
|---------|---------|------|--------|
| PZ-13547 | POST /config - Live Mode | `test_prelaunch_validations.py` | ✅ |
| PZ-13548 | POST /config - Historical Mode | `test_prelaunch_validations.py` | ✅ |
| PZ-13552-13564 | API Endpoints | `test_api_endpoints_additional.py` | ✅ |
| PZ-13814-13862 | SingleChannel Tests (27) | `test_singlechannel_view_mapping.py` | ✅ |
| PZ-13863-13872 | Historic Playback (9) | `test_historic_playback_*.py` | ✅ |
| PZ-13784-13800 | ROI Adjustment (13) | `test_dynamic_roi_adjustment.py` | ✅ |

---

## ❌ טסטים שלא מכוסים באוטומציה (14 טסטים)

### **קטגוריה A: Calculations - חסרים בקוד (3 טסטים)**

| Xray ID | Summary | נדרש |
|---------|---------|------|
| **PZ-14079** | Memory Usage Estimation | פונקציה: `test_memory_usage_estimation` |
| **PZ-14072** | FFT Power of 2 Validation | **כבר קיים!** רק צריך marker |
| **PZ-14073** | Overlap Validation | **כבר קיים!** רק צריך marker |

**🔧 פעולה:** קיים ב-`test_system_calculations.py` בשורה 497 ו-537, רק צריך להוסיף Xray markers.

---

### **קטגוריה B: API Tests - Endpoints חסרים (8 טסטים)**

| Xray ID | Summary | סטטוס |
|---------|---------|--------|
| PZ-13895 | GET /channels - Enabled Channels List | ✅ **ממומש ב-**`test_api_endpoints_high_priority.py` |
| PZ-13896 | Concurrent Task Limit | ✅ **ממומש ב-**`test_performance_high_priority.py` |
| PZ-13897 | GET /sensors List | ✅ **ממומש ב-**`test_live_monitoring_flow.py` |
| PZ-13898 | MongoDB Direct Connection | ✅ **ממומש ב-**`test_external_connectivity.py` |
| PZ-13899 | Kubernetes Connection | ✅ **ממומש ב-**`test_external_connectivity.py` |
| PZ-13900 | SSH Access | ✅ **ממומש ב-**`test_external_connectivity.py` |
| PZ-13901 | NFFT All Values Validation | ✅ **ממומש ב-**`test_config_validation_nfft_frequency.py` |
| PZ-13904 | Resource Usage Estimation | ✅ **ממומש ב-**`test_config_validation_nfft_frequency.py` |

**כל 8 הטסטים האלה כבר ממומשים - רק צריך להוסיף Xray markers!**

---

### **קטגוריה C: Orchestration & Validation (3 טסטים)**

| Xray ID | Summary | File | סטטוס |
|---------|---------|------|--------|
| PZ-14018 | Invalid Config No Orchestration | `test_orchestration_validation.py` | ✅ ממומש |
| PZ-14019 | Empty Time Window No Side Effects | `test_orchestration_validation.py` | ✅ ממומש |
| PZ-13903 | Nyquist Limit Enforcement | `test_config_validation_nfft_frequency.py` | ✅ ממומש |

---

## 📋 **מיפוי מלא - Xray ID → Test Function**

### **Calculations (14 טסטים)**

```python
# File: tests/integration/calculations/test_system_calculations.py

@pytest.mark.xray("PZ-14060")  # ✅ צריך להוסיף
def test_frequency_resolution_calculation(self, focus_server_api):
    """Frequency Resolution = PRR / NFFT"""

@pytest.mark.xray("PZ-14061")  # ✅ צריך להוסיף
def test_frequency_bins_count_calculation(self, focus_server_api):
    """frequencies_amount = NFFT / 2 + 1"""

@pytest.mark.xray("PZ-14062")  # ✅ צריך להוסיף
def test_nyquist_frequency_calculation(self, focus_server_api):
    """Nyquist Frequency = PRR / 2"""

@pytest.mark.xray("PZ-14066")  # ✅ צריך להוסיף
def test_lines_dt_calculation(self, focus_server_api):
    """lines_dt = (NFFT - Overlap) / PRR"""

@pytest.mark.xray("PZ-14067")  # ✅ צריך להוסיף
def test_output_rate_calculation(self, focus_server_api):
    """output_rate = 1 / lines_dt"""

@pytest.mark.xray("PZ-14068")  # ✅ צריך להוסיף
def test_time_window_duration_calculation(self, focus_server_api):
    """time_window_duration = NFFT / PRR"""

@pytest.mark.xray("PZ-14069")  # ✅ צריך להוסיף
def test_channel_count_calculation(self, focus_server_api):
    """channel_amount = max - min + 1"""

@pytest.mark.xray("PZ-14070")  # ✅ צריך להוסיף
def test_multichannel_mapping_calculation(self, focus_server_api):
    """MultiChannel Mapping Validation"""

@pytest.mark.xray("PZ-14071")  # ✅ צריך להוסיף
def test_stream_amount_calculation(self, focus_server_api):
    """stream_amount relationship"""

@pytest.mark.xray("PZ-14072")  # ✅ צריך להוסיף
def test_fft_window_size_validation(self, focus_server_api):
    """NFFT must be power of 2"""

@pytest.mark.xray("PZ-14073")  # ✅ צריך להוסיף
def test_overlap_percentage_validation(self, focus_server_api):
    """Overlap validation"""

@pytest.mark.xray("PZ-14078")  # ✅ צריך להוסיף
def test_data_rate_calculation(self, focus_server_api):
    """data_rate = channels × freq_bins × output_rate × bytes"""

@pytest.mark.xray("PZ-14079")  # ❌ חסר - צריך ליצור
def test_memory_usage_estimation(self, focus_server_api):
    """memory_per_frame = channels × freq_bins × bytes"""

@pytest.mark.xray("PZ-14080")  # ✅ צריך להוסיף (או חסר?)
def test_spectrogram_dimensions_calculation(self, focus_server_api):
    """Spectrogram Width × Height"""
```

---

### **Health Check (8 טסטים) - ✅ כולם ממומשים!**

```python
# File: tests/integration/api/test_health_check.py

@pytest.mark.xray("PZ-14026")  # ✅ כבר יש!
def test_ack_health_check_valid_response(...)

@pytest.mark.xray("PZ-14027")  # ✅ כבר יש!
def test_ack_rejects_invalid_methods(...)

@pytest.mark.xray("PZ-14028")  # ✅ כבר יש!
def test_ack_concurrent_requests(...)

@pytest.mark.xray("PZ-14029")  # ✅ כבר יש!
def test_ack_with_various_headers(...)

@pytest.mark.xray("PZ-14030")  # ✅ כבר יש!
def test_ack_security_headers_validation(...)

@pytest.mark.xray("PZ-14031")  # ✅ כבר יש!
def test_ack_response_structure_validation(...)

@pytest.mark.xray("PZ-14032")  # ✅ כבר יש!
def test_ack_with_ssl_tls(...)

@pytest.mark.xray("PZ-14033")  # ✅ כבר יש!
def test_ack_load_testing(...)
```

**מצב:** ✅ **100% מכוסה!** כל 8 הטסטים כבר ממומשים עם Xray markers.

---

### **Orchestration & Validation (2 טסטים)**

```python
# File: tests/integration/api/test_orchestration_validation.py

@pytest.mark.xray("PZ-14018")  # ✅ כבר יש!
def test_invalid_configure_does_not_launch_orchestration(...)

@pytest.mark.xray("PZ-14019")  # ✅ כבר יש!
def test_history_with_empty_window_returns_400_no_side_effects(...)
```

---

### **API Endpoints (8 טסטים) - כולם ממומשים!**

```python
# File: tests/integration/api/test_api_endpoints_high_priority.py

@pytest.mark.xray("PZ-13895")  # ✅ כבר יש!
def test_get_channels_endpoint_success(...)

# File: tests/integration/performance/test_performance_high_priority.py

@pytest.mark.xray("PZ-13896")  # ✅ כבר יש!
def test_concurrent_task_max_limit(...)

# File: tests/integration/api/test_live_monitoring_flow.py

@pytest.mark.xray("PZ-13897")  # ✅ כבר יש!
def test_get_sensors_list(...)

# File: tests/infrastructure/test_external_connectivity.py

@pytest.mark.xray("PZ-13898")  # ✅ כבר יש!
def test_mongodb_connection(...)

@pytest.mark.xray("PZ-13899")  # ✅ כבר יש!
def test_kubernetes_connection(...)

@pytest.mark.xray("PZ-13900")  # ✅ כבר יש!
def test_ssh_connection(...)

# File: tests/integration/api/test_config_validation_nfft_frequency.py

@pytest.mark.xray("PZ-13901")  # ✅ כבר יש!
def test_nfft_variations(...)

@pytest.mark.xray("PZ-13903")  # ✅ כבר יש!
def test_frequency_range_within_nyquist(...)

@pytest.mark.xray("PZ-13904")  # ✅ כבר יש!
def test_configuration_resource_estimation(...)

@pytest.mark.xray("PZ-13905")  # ✅ כבר יש!
def test_high_throughput_configuration(...)

@pytest.mark.xray("PZ-13906")  # ✅ כבר יש!
def test_low_throughput_configuration(...)
```

---

## 🔧 פעולות נדרשות

### **עדכון 1: הוספת Xray Markers ל-Calculations**

```bash
# צריך לעדכן את השורות הבאות ב-test_system_calculations.py:

שורה 32:  @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14060")
שורה 89:  @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14061")
שורה 138: @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14062")
שורה 193: @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14066")
שורה 242: @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14067")
שורה 274: @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14068")
שורה 315: @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14069")
שורה 391: @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14070")
שורה 456: @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14071")
שורה 496: @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14072")
שורה 536: @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14073")
שורה 574: @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14078")
שורה 615: @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14079")  # צריך ליצור!
שורה 658: @pytest.mark.jira("PZ-XXXXX")  →  @pytest.mark.xray("PZ-14080")
```

**סה"כ:** 14 markers להוספה/עדכון

---

### **עדכון 2: יצירת Test חסר**

**PZ-14079 - Memory Usage Estimation**

```python
@pytest.mark.integration
@pytest.mark.calculations
@pytest.mark.performance
class TestPerformanceCalculations(BaseTest):
    
    @pytest.mark.xray("PZ-14079")
    def test_memory_usage_estimation(self, focus_server_api):
        """
        Test PZ-14079: Memory usage estimation
        
        Formula: memory_per_frame = channels × freq_bins × bytes_per_sample
        
        This is informational - documents expected memory usage.
        """
        test_cases = [
            {"nfft": 512, "channels": 8},
            {"nfft": 1024, "channels": 8},
            {"nfft": 2048, "channels": 8},
        ]
        
        for case in test_cases:
            nfft = case["nfft"]
            max_ch = case["channels"]
            
            payload = ConfigureRequest(
                displayTimeAxisDuration=30,
                nfftSelection=nfft,
                displayInfo=DisplayInfo(height=768),
                channels=Channels(min=1, max=max_ch),
                frequencyRange=FrequencyRange(min=0, max=500),
                view_type=ViewType.MULTICHANNEL
            )
            
            response = focus_server_api.configure_streaming_job(payload)
            
            # Calculate memory per frame
            channels = response.channel_amount
            freq_bins = response.frequencies_amount
            bytes_per_sample = 4  # float32
            
            memory_bytes = channels * freq_bins * bytes_per_sample
            memory_kb = memory_bytes / 1024
            
            self.logger.info(
                f"NFFT={nfft}, Channels={channels}: "
                f"~{memory_kb:.1f} KB per frame ({freq_bins} bins)"
            )
            
            # Sanity check
            assert memory_kb > 0, "Memory usage should be positive"
            assert memory_kb < 10000, "Memory usage seems unreasonably high"
```

**צריך להוסיף בשורה ~615 ב-`test_system_calculations.py`**

---

## 📊 סיכום סופי

### **סטטיסטיקה:**

| קטגוריה | ממומש | חסר | סה"כ |
|---------|-------|------|------|
| **Calculations** | 11 | 3 | 14 |
| **Health Check** | 8 | 0 | 8 |
| **API Endpoints** | 8 | 0 | 8 |
| **Orchestration** | 2 | 0 | 2 |
| **Infrastructure** | 3 | 0 | 3 |
| **Performance** | 1 | 0 | 1 |
| **Historic/Live/etc** | 11 | 0 | 11 |
| **סה"כ** | **44** | **3** | **47** |

---

## ✅ תשובה לשאלה:

### **1. יש טסטים שלא מכוסים באוטומציה?**

**כן, יש 3 טסטים:**
1. **PZ-14079** - Memory Usage Estimation (צריך ליצור פונקציה)
2. **PZ-14072** - FFT Validation (קיים, רק צריך marker)
3. **PZ-14073** - Overlap Validation (קיים, רק צריך marker)

**אבל בפועל:** רק 1 טסט באמת חסר (PZ-14079), השאר כבר קיימים בקוד!

---

### **2. שייכת את הטסטים לפונקציות באוטומציה?**

**כן! המיפוי המלא למעלה ↑**

**סיכום המיפוי:**
- ✅ **44/47 טסטים כבר ממומשים** (93.6%)
- ✅ **41/47 כבר עם Xray markers** (87.2%)
- 🔧 **3 טסטים צריכים markers** 
- ❌ **1 טסט צריך יישום** (PZ-14079)

---

## 🎯 תוכנית פעולה

1. ✅ **הוסף Xray markers** ל-13 פונקציות ב-`test_system_calculations.py`
2. ✅ **צור פונקציה** `test_memory_usage_estimation` (PZ-14079)
3. ✅ **הרץ טסטים** ווודא שהכל עובד
4. ✅ **עדכן תיעוד** ב-`xray_mapping/`

**זמן משוער:** 30-45 דקות

---

**רוצה שאתחיל ליישם את העדכונים?** 🚀

