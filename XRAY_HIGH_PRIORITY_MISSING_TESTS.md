# 🔴 Xray High Priority Tests - Missing in Automation Code
## רק טסטים עם Priority: High (בלבד)

**תאריך:** 2025-10-21  
**מקור:** `docs/xray_tests_21_10_25.csv`  
**סינון:** Priority = High בלבד  

---

## 📊 סיכום מנהלים

| סטטוס | מספר טסטים |
|-------|-----------|
| **סה"כ High Priority ב-Xray** | ~25 טסטים |
| **חסרים בקוד לגמרי** | ~18 טסטים |
| **קיימים חלקית** | ~3 טסטים |
| **קיימים מלא** | ~4 טסטים |
| **אחוז כיסוי** | ~16% בלבד! |

---

## 🔴 טסטים High Priority חסרים בקוד

### 1. Configuration Validation (High Priority)

| Test ID | Test Name | Status | הערות |
|---------|-----------|--------|-------|
| **PZ-13879** | Integration – Missing Required Fields | ❌ **חסר לגמרי** | בודק שהAPI דוחה config ללא שדות חובה |
| **PZ-13878** | Integration – Invalid View Type - Out of Range | ❌ **חסר לגמרי** | בודק view_type לא חוקי (לא 0/1) |
| **PZ-13877** | Integration – Invalid Frequency Range - Min > Max | ⚠️ **חלקי** | יש test_config_with_invalid_frequency_range |
| **PZ-13876** | Integration – Invalid Channel Range - Min > Max | ⚠️ **חלקי** | יש test_config_with_invalid_sensor_range |
| **PZ-13875** | Integration – Invalid NFFT - Negative Value | ✅ **קיים** | test_negative_nfft |
| **PZ-13874** | Integration – Invalid NFFT - Zero Value | ✅ **קיים** | test_zero_nfft |
| **PZ-13873** | Integration - Valid Configuration - All Parameters | ❌ **חסר** | בדיקת happy path מלא |

---

### 2. Historic Playback (High Priority)

| Test ID | Test Name | Status | הערות |
|---------|-----------|--------|-------|
| **PZ-13872** | Historic Playback Complete End-to-End Flow | ⚠️ **חלקי** | יש flow אבל לא מלא כמו ב-Xray |
| **PZ-13871** | Historic Playback - Timestamp Ordering Validation | ❌ **חסר לגמרי** | בדיקת סדר timestamps |
| **PZ-13868** | Historic Playback - Status 208 Completion | ❌ **חסר** | בדיקה ספציפית ל-208 |
| **PZ-13863** | Historic Playback - Standard 5-Minute Range | ❌ **חסר** | בדיקת 5 דקות ספציפי |

---

### 3. SingleChannel (High Priority)

| Test ID | Test Name | Status | הערות |
|---------|-----------|--------|-------|
| **PZ-13853** | SingleChannel Data Consistency Check | ❌ **חסר לגמרי** | בדיקת עקביות נתונים |
| **PZ-13852** | SingleChannel Invalid Channel ID | ❌ **חסר לגמרי** | בדיקת channel_id לא חוקי |

---

### 4. Infrastructure & Resilience (High Priority)

| Test ID | Test Name | Status | הערות |
|---------|-----------|--------|-------|
| **PZ-13687** | MongoDB Recovery – Recordings Indexed After Outage | ✅ **קיים** | test_mongodb_outage_* |
| **PZ-13686** | MongoDB Indexes Validation | ✅ **קיים** | test_mongodb_indexes_exist_and_optimal |
| **PZ-13685** | Recordings Metadata Completeness | ❌ **חסר** | בדיקת שדות חובה ב-metadata |

---

### 5. API Endpoints (High Priority)

| Test ID | Test Name | Status | הערות |
|---------|-----------|--------|-------|
| **PZ-13419** | GET /channels - Enabled Channels | ❌ **חסר לגמרי** | אין טסט ל-endpoint הזה כלל! |
| **PZ-13547** | POST /config - Live Mode Configuration | ⚠️ **חלקי** | יש אבל endpoint שונה |
| **PZ-13548** | POST /config - Historical Configuration | ⚠️ **חלקי** | יש אבל endpoint שונה |

---

### 6. Performance & Load (High Priority)

| Test ID | Test Name | Status | הערות |
|---------|-----------|--------|-------|
| **PZ-13770** | Performance – /config Latency P95 | ❌ **חסר לגמרי** | אין שום performance testing |
| **PZ-13771** | Performance – Concurrent Task Limit | ❌ **חסר לגמרי** | אין בדיקת מקסימום tasks |

---

### 7. ROI Dynamic Adjustment (High Priority)

| Test ID | Test Name | Status | הערות |
|---------|-----------|--------|-------|
| **PZ-13830** | ROI – Dynamic Adjustment Limits | ❌ **חסר** | בדיקת גבולות שינוי ROI |
| **PZ-13831** | ROI – Rapid Changes Stability | ❌ **חסר** | בדיקת שינויים מהירים |

---

## 📝 פירוט מלא - טסטים High Priority חסרים

### 🔴 קריטי ביותר - לממש מיידית (השבוע)

#### 1. PZ-13879: Missing Required Fields
```python
def test_missing_required_fields(focus_server_api):
    """
    Test PZ-13879: Integration – Missing Required Fields
    Priority: HIGH
    
    Validates rejection of incomplete configurations.
    """
    # Test 1: Missing channels
    config_no_channels = {
        "nfftSelection": 1024,
        "frequencyRange": {"min": 0, "max": 500}
        # Missing "channels" - should fail
    }
    
    # Test 2: Missing frequencyRange
    config_no_freq = {
        "nfftSelection": 1024,
        "channels": {"min": 0, "max": 50}
        # Missing "frequencyRange" - should fail
    }
    
    # Test 3: Missing nfftSelection
    config_no_nfft = {
        "channels": {"min": 0, "max": 50},
        "frequencyRange": {"min": 0, "max": 500}
        # Missing "nfftSelection" - should fail
    }
    
    # All should return 400 Bad Request
```

**חשיבות:** קריטי - בלי זה לא יודעים אם validation בסיסי עובד

---

#### 2. PZ-13878: Invalid View Type
```python
def test_invalid_view_type_out_of_range(focus_server_api):
    """
    Test PZ-13878: Integration – Invalid View Type - Out of Range
    Priority: HIGH
    
    Valid values: 0 (MULTICHANNEL) or 1 (SINGLECHANNEL)
    Invalid values: -1, 2, 3, 999, etc.
    """
    config = {
        "channels": {"min": 0, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "nfftSelection": 1024,
        "view_type": 99  # Invalid!
    }
    
    # Should return 400 Bad Request
```

**חשיבות:** קריטי - enum validation הכרחי

---

#### 3. PZ-13873: Valid Configuration - All Parameters
```python
def test_valid_configuration_all_parameters(focus_server_api):
    """
    Test PZ-13873: Integration - Valid Configuration - All Parameters
    Priority: HIGH
    
    Happy path with ALL parameters set correctly.
    """
    config = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 0, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": None,
        "end_time": None,
        "view_type": 0
    }
    
    # Should succeed with 200/201
    # Verify all parameters were applied correctly
```

**חשיבות:** קריטי - הבסיס לכל שאר הטסטים

---

#### 4. PZ-13419: GET /channels
```python
def test_get_channels_endpoint(focus_server_api):
    """
    Test PZ-13419: GET /channels - Enabled Channels
    Priority: HIGH
    
    Smoke test for channels endpoint.
    """
    response = focus_server_api.get_channels()
    
    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert len(response.data) > 0
    
    # Verify channel structure
    for channel in response.data:
        assert "id" in channel or "channel_id" in channel
        assert "enabled" in channel or "status" in channel
```

**חשיבות:** קריטי - endpoint חסר לגמרי בבדיקות!

---

#### 5. PZ-13868: Historic Status 208
```python
def test_historic_playback_status_208_completion(focus_server_api):
    """
    Test PZ-13868: Historic Playback - Status 208 Completion
    Priority: HIGH
    
    Verify 208 "Already Reported" semantics for historic completion.
    """
    # Configure historic task
    task_id = configure_historic_task(start_time, end_time)
    
    # Poll until 208
    status_code = poll_until_status(task_id, target_status=208)
    
    assert status_code == 208
    # Verify no more data available
    # Verify task marked as complete
```

**חשיבות:** גבוה - צריך להבין מתי playback הסתיים

---

#### 6. PZ-13871: Timestamp Ordering
```python
def test_historic_timestamp_ordering_validation(focus_server_api):
    """
    Test PZ-13871: Historic Playback - Timestamp Ordering Validation
    Priority: HIGH
    
    Verify timestamps are monotonically increasing.
    """
    # Configure and poll historic data
    waterfall_data = get_historic_waterfall(task_id)
    
    # Extract all timestamps
    timestamps = extract_timestamps(waterfall_data)
    
    # Verify ordering
    for i in range(len(timestamps) - 1):
        assert timestamps[i] < timestamps[i+1], \
            f"Timestamps not ordered: {timestamps[i]} >= {timestamps[i+1]}"
```

**חשיבות:** גבוה - integrity של נתונים

---

#### 7. PZ-13853: SingleChannel Data Consistency
```python
def test_singlechannel_data_consistency_check(focus_server_api):
    """
    Test PZ-13853: SingleChannel Data Consistency Check
    Priority: HIGH
    
    Verify data consistency between requests.
    """
    channel_id = 7
    
    # Request 1
    data1 = get_singlechannel_data(channel_id)
    
    # Request 2 (same time range)
    data2 = get_singlechannel_data(channel_id)
    
    # Should be identical
    assert data1 == data2
```

**חשיבות:** גבוה - determinism critical

---

#### 8. PZ-13852: SingleChannel Invalid Channel
```python
def test_singlechannel_invalid_channel_id(focus_server_api):
    """
    Test PZ-13852: SingleChannel Invalid Channel ID
    Priority: HIGH
    
    Test with non-existent channel ID.
    """
    invalid_channel_id = 9999
    
    config = create_singlechannel_config(channel_id=invalid_channel_id)
    
    response = focus_server_api.config_task(task_id, config)
    
    # Should reject: 400 or 404
    assert response.status_code in [400, 404]
```

**חשיבות:** גבוה - error handling

---

#### 9. PZ-13770: Performance P95 Latency
```python
@pytest.mark.performance
def test_config_endpoint_latency_p95(focus_server_api):
    """
    Test PZ-13770: Performance – /config Latency P95
    Priority: HIGH
    
    Measure P95 and P99 latency for config endpoint.
    """
    latencies = []
    
    for i in range(100):
        start_time = time.time()
        response = focus_server_api.config_task(f"task_{i}", config)
        end_time = time.time()
        
        latencies.append((end_time - start_time) * 1000)  # ms
    
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)
    
    # Need specs from meeting!
    assert p95 < THRESHOLD_P95_MS  # e.g., < 500ms
    assert p99 < THRESHOLD_P99_MS  # e.g., < 1000ms
```

**חשיבות:** קריטי - אין שום performance testing!

---

#### 10. PZ-13771: Concurrent Task Limit
```python
@pytest.mark.performance
def test_concurrent_task_limit(focus_server_api):
    """
    Test PZ-13771: Performance – Concurrent Task Limit
    Priority: HIGH
    
    Find maximum concurrent tasks supported.
    """
    import concurrent.futures
    
    max_tasks = 100  # Try up to 100
    successful_tasks = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_tasks) as executor:
        futures = []
        for i in range(max_tasks):
            future = executor.submit(
                focus_server_api.config_task,
                f"concurrent_task_{i}",
                config
            )
            futures.append(future)
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result.status_code == 200:
                    successful_tasks += 1
            except:
                pass
    
    # Need specs from meeting!
    assert successful_tasks >= MIN_CONCURRENT_TASKS  # e.g., >= 10
```

**חשיבות:** קריטי - לא יודעים capacity!

---

## 📊 סיכום פעולות נדרשות

### טסטים High Priority לממש השבוע:
1. ✅ **PZ-13879** - Missing Required Fields (קריטי)
2. ✅ **PZ-13878** - Invalid View Type (קריטי)
3. ✅ **PZ-13873** - Valid Configuration All Parameters (קריטי)
4. ✅ **PZ-13419** - GET /channels endpoint (קריטי)
5. ✅ **PZ-13868** - Historic Status 208 (גבוה)
6. ✅ **PZ-13871** - Timestamp Ordering (גבוה)
7. ✅ **PZ-13853** - SingleChannel Consistency (גבוה)
8. ✅ **PZ-13852** - SingleChannel Invalid ID (גבוה)
9. ✅ **PZ-13770** - Performance P95 (קריטי)
10. ✅ **PZ-13771** - Concurrent Tasks (קריטי)

**סה"כ:** 10 טסטים High Priority דחופים

### זמן משוער:
- Configuration validation (3 tests) - 1 יום
- Historic tests (3 tests) - 1 יום
- SingleChannel tests (2 tests) - 1 יום
- Performance tests (2 tests) - 2 ימים (כולל infrastructure)
- **סה"כ:** ~1 שבוע עבודה

---

## 🎯 Acceptance Criteria

לאחר יישום כל 10 הטסטים:
- ✅ כל טסט רץ ועובר
- ✅ כל טסט מתועד ב-Jira Xray
- ✅ יש assertions ברורים עם thresholds (אחרי פגישת specs)
- ✅ יש logging מתאים
- ✅ טסטים עם markers נכונים (`@pytest.mark.integration`, etc.)

---

**עדיפות:** 🔴 CRITICAL - התחל מחר!  
**Owner:** QA Automation Team  
**תאריך יעד:** סוף השבוע
