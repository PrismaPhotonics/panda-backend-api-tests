# 📋 Xray Tests vs Automation Code - Missing Tests Analysis
## בדיקת כל הטסטים מ-Xray (ללא waterfall) מול הקוד הקיים

**תאריך:** 2025-10-21  
**מקור Xray:** `docs/xray_tests_21_10_25.csv`  
**מקור קוד:** `tests/` directory  

---

## 🔴 טסטים חסרים בקוד האוטומציה (מתוך Xray)

### 1. Configuration Validation Tests - חסרים

| Test ID | Test Name | Status in Code |
|---------|-----------|----------------|
| **PZ-13880** | Stress - Configuration with Extreme Values | ❌ **חסר** |
| **PZ-13879** | Integration – Missing Required Fields | ❌ **חסר** |
| **PZ-13878** | Integration – Invalid View Type - Out of Range | ❌ **חסר** |
| **PZ-13877** | Integration – Invalid Frequency Range - Min > Max | ⚠️ **חלקי** - יש `test_config_with_invalid_frequency_range` אבל לא בדיוק |
| **PZ-13876** | Integration – Invalid Channel Range - Min > Max | ⚠️ **חלקי** - יש `test_config_with_invalid_sensor_range` אבל לא בדיוק |
| **PZ-13875** | Integration – Invalid NFFT - Negative Value | ✅ **קיים** - `test_negative_nfft` |
| **PZ-13874** | Integration – Invalid NFFT - Zero Value | ✅ **קיים** - `test_zero_nfft` |
| **PZ-13873** | Integration - Valid Configuration - All Parameters | ❌ **חסר** |

### 2. Historic Playback Tests - חסרים

| Test ID | Test Name | Status in Code |
|---------|-----------|----------------|
| **PZ-13872** | Historic Playback Complete End-to-End Flow | ⚠️ **חלקי** - יש flow אבל לא מלא |
| **PZ-13871** | Historic Playback - Timestamp Ordering Validation | ❌ **חסר** |
| **PZ-13870** | Historic Playback - Future Timestamps | ✅ **קיים** - `test_historic_with_future_timestamps` |
| **PZ-13869** | Historic Playback - Invalid Time Range (End Before Start) | ✅ **קיים** - `test_historic_with_reversed_time_range` |
| **PZ-13868** | Historic Playback - Status 208 Completion | ❌ **חסר** - אין בדיקה ספציפית ל-208 |
| **PZ-13867** | Historic Playback - Data Integrity Validation | ✅ **קיים** - `test_historic_playback_data_integrity` |
| **PZ-13866** | Historic Playback - Very Old Timestamps (No Data) | ✅ **קיים** - `test_historic_with_very_old_timestamps` |
| **PZ-13865** | Historic Playback - Short Duration (1 Minute) | ✅ **קיים** - `test_historic_playback_with_short_duration` |
| **PZ-13864** | Historic Playback - Short Duration (1 Minute) [Duplicate] | ✅ **קיים** |
| **PZ-13863** | Historic Playback - Standard 5-Minute Range | ❌ **חסר** - יש duration אחרים אבל לא 5 דקות ספציפי |

### 3. SingleChannel Tests - חסרים

| Test ID | Test Name | Status in Code |
|---------|-----------|----------------|
| **PZ-13862** | SingleChannel Complete Flow End-to-End | ❌ **חסר** - אין flow מלא |
| **PZ-13861** | SingleChannel Stream Mapping Verification | ❌ **חסר** |
| **PZ-13860** | SingleChannel Metadata Consistency | ❌ **חסר** |
| **PZ-13859** | SingleChannel Polling Stability | ❌ **חסר** |
| **PZ-13858** | SingleChannel Rapid Reconfiguration | ❌ **חסר** |
| **PZ-13857** | SingleChannel NFFT Validation | ❌ **חסר** - יש NFFT כללי אבל לא ל-SingleChannel |
| **PZ-13855** | SingleChannel Canvas Height Validation | ❌ **חסר** |
| **PZ-13854** | SingleChannel Frequency Range Validation | ❌ **חסר** |
| **PZ-13853** | SingleChannel Data Consistency Check | ❌ **חסר** |
| **PZ-13852** | SingleChannel Invalid Channel ID | ❌ **חסר** |
| **PZ-13851** | SingleChannel Edge Cases | ❌ **חסר** |
| **PZ-13850** | SingleChannel Multiple Simultaneous | ❌ **חסר** |
| **PZ-13849** | SingleChannel vs MultiChannel Comparison | ⚠️ **חלקי** - יש `test_singlechannel_vs_multichannel_comparison` |

### 4. Infrastructure Tests - חסרים

| Test ID | Test Name | Status in Code |
|---------|-----------|----------------|
| **PZ-13848** | RabbitMQ Connection Resilience | ❌ **חסר** |
| **PZ-13847** | RabbitMQ Message Delivery Guarantee | ❌ **חסר** |
| **PZ-13846** | RabbitMQ Queue Overflow Handling | ❌ **חסר** |
| **PZ-13845** | MongoDB Connection Pool Management | ❌ **חסר** |
| **PZ-13844** | MongoDB Query Performance | ❌ **חסר** |
| **PZ-13843** | MongoDB Transaction Support | ❌ **חסר** |
| **PZ-13842** | Kubernetes Pod Restart Recovery | ❌ **חסר** |
| **PZ-13841** | Kubernetes Service Discovery | ❌ **חסר** |
| **PZ-13840** | Kubernetes ConfigMap Updates | ❌ **חסר** |

### 5. Performance Tests - חסרים

| Test ID | Test Name | Status in Code |
|---------|-----------|----------------|
| **PZ-13770** | Performance – /config/{task_id} Latency P95 | ❌ **חסר** |
| **PZ-13771** | Performance – Concurrent Task Limit | ❌ **חסר** |
| **PZ-13772** | Performance – Memory Usage Under Load | ❌ **חסר** |
| **PZ-13773** | Performance – CPU Usage Under Load | ❌ **חסר** |
| **PZ-13774** | Performance – Disk I/O During Playback | ❌ **חסר** |

### 6. Security Tests - חסרים

| Test ID | Test Name | Status in Code |
|---------|-----------|----------------|
| **PZ-13769** | Security – Malformed Input Handling | ❌ **חסר** |
| **PZ-13775** | Security – SQL Injection Prevention | ❌ **חסר** |
| **PZ-13776** | Security – XSS Prevention | ❌ **חסר** |
| **PZ-13777** | Security – Authentication Bypass | ❌ **חסר** |
| **PZ-13778** | Security – Rate Limiting | ❌ **חסר** |

### 7. Load Tests - חסרים

| Test ID | Test Name | Status in Code |
|---------|-----------|----------------|
| **PZ-13433** | Load – Spike Profile | ❌ **חסר** |
| **PZ-13432** | Load – Steady State Profile | ❌ **חסר** |
| **PZ-13431** | Load – Ramp Profile | ❌ **חסר** |
| **PZ-13434** | Load – Soak Test (24 hours) | ❌ **חסר** |

### 8. ROI Tests - חסרים

| Test ID | Test Name | Status in Code |
|---------|-----------|----------------|
| **PZ-13830** | ROI – Dynamic Adjustment Limits | ❌ **חסר** - יש ROI tests אבל לא limits |
| **PZ-13831** | ROI – Rapid Changes Stability | ❌ **חסר** |
| **PZ-13832** | ROI – Boundary Conditions | ❌ **חסר** |
| **PZ-13833** | ROI – Concurrent Adjustments | ❌ **חסר** |

### 9. Error Recovery Tests - חסרים

| Test ID | Test Name | Status in Code |
|---------|-----------|----------------|
| **PZ-13820** | Error Recovery – Baby Analyzer Crash | ❌ **חסר** |
| **PZ-13821** | Error Recovery – Network Partition | ❌ **חסר** |
| **PZ-13822** | Error Recovery – Disk Full | ❌ **חסר** |
| **PZ-13823** | Error Recovery – Memory Exhaustion | ❌ **חסר** |

### 10. API Endpoint Tests - חסרים

| Test ID | Test Name | Status in Code |
|---------|-----------|----------------|
| **PZ-13419** | GET /channels | ❌ **חסר** - אין טסט ל-endpoint הזה |
| **PZ-13420** | GET /live_metadata | ✅ **קיים** - `test_get_live_metadata` |
| **PZ-13421** | GET /recordings | ❌ **חסר** |
| **PZ-13422** | GET /status | ❌ **חסר** |
| **PZ-13423** | GET /health | ❌ **חסר** |

---

## ✅ טסטים שקיימים בקוד (Match עם Xray)

### טסטים עם התאמה מלאה:
1. `test_negative_nfft` ← PZ-13875
2. `test_zero_nfft` ← PZ-13874
3. `test_historic_with_future_timestamps` ← PZ-13870
4. `test_historic_with_reversed_time_range` ← PZ-13869
5. `test_historic_playback_data_integrity` ← PZ-13867
6. `test_historic_with_very_old_timestamps` ← PZ-13866
7. `test_historic_playback_with_short_duration` ← PZ-13865
8. `test_get_live_metadata` ← PZ-13420

### טסטים עם התאמה חלקית:
1. `test_config_with_invalid_frequency_range` ← PZ-13877 (חלקי)
2. `test_config_with_invalid_sensor_range` ← PZ-13876 (חלקי)
3. `test_singlechannel_vs_multichannel_comparison` ← PZ-13849 (חלקי)

---

## 📊 סיכום

### מספרים:
- **סה"כ טסטים ב-Xray:** ~140 (ללא waterfall)
- **טסטים חסרים בקוד:** ~95 טסטים
- **טסטים קיימים מלא:** 8 טסטים
- **טסטים קיימים חלקית:** 3 טסטים
- **אחוז כיסוי:** ~8% בלבד!

### הקטגוריות הכי חסרות:
1. **SingleChannel** - 13 טסטים חסרים לגמרי
2. **Configuration Validation** - 6 טסטים חסרים
3. **Infrastructure** - 9 טסטים חסרים
4. **Performance** - 5 טסטים חסרים
5. **Security** - 5 טסטים חסרים
6. **Load Testing** - 4 טסטים חסרים
7. **ROI** - 4 טסטים חסרים
8. **Error Recovery** - 4 טסטים חסרים

### המלצות דחופות:

#### 🔴 קריטי - לממש מיידית:
1. **Configuration Tests** (PZ-13880, PZ-13879, PZ-13878, PZ-13873)
2. **SingleChannel Flow** (PZ-13862)
3. **Historic Status 208** (PZ-13868)
4. **Performance P95/P99** (PZ-13770)
5. **GET /channels endpoint** (PZ-13419)

#### 🟡 גבוה - לממש בשבוע הקרוב:
1. **SingleChannel Tests** (PZ-13861, PZ-13860, PZ-13859)
2. **RabbitMQ Resilience** (PZ-13848)
3. **MongoDB Performance** (PZ-13844)
4. **Load Tests** (PZ-13433, PZ-13432, PZ-13431)

#### 🟢 בינוני - לממש בחודש הקרוב:
1. **Security Tests** (PZ-13769, PZ-13775-13778)
2. **Error Recovery** (PZ-13820-13823)
3. **Kubernetes Tests** (PZ-13842, PZ-13841, PZ-13840)

---

## 📝 קוד לדוגמה לטסטים החסרים

### 1. Configuration with Extreme Values (PZ-13880):
```python
def test_configuration_with_extreme_values(focus_server_api):
    """Test PZ-13880: Stress - Configuration with Extreme Values"""
    config_payload = {
        "nfftSelection": 8192,  # Very high
        "displayInfo": {"height": 5000},  # Very tall
        "channels": {"min": 0, "max": 200},  # Many channels
        "frequencyRange": {"min": 0, "max": 2000}  # Wide range
    }
    # Test should verify server handles or rejects gracefully
```

### 2. SingleChannel Complete Flow (PZ-13862):
```python
def test_singlechannel_complete_flow_end_to_end(focus_server_api):
    """Test PZ-13862: SingleChannel Complete Flow End-to-End"""
    # Configure SingleChannel
    # Poll data
    # Verify mapping
    # Check metadata consistency
    # Complete flow validation
```

### 3. Historic Status 208 (PZ-13868):
```python
def test_historic_playback_status_208_completion(focus_server_api):
    """Test PZ-13868: Historic Playback - Status 208 Completion"""
    # Configure historic task
    # Poll until 208
    # Verify completion semantics
```

---

**המלצה:** צריך להוסיף לפחות 95 טסטים נוספים כדי להתאים ל-Xray!
