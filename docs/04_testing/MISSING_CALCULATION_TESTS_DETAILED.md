# רשימה מפורטת - טסטי חישובים חסרים

**תאריך:** 29 אוקטובר 2025  
**קטגוריה:** בדיקת חישובים מתמטיים במערכת  
**סטטוס:** לא ממומש

---

## 📊 סיכום

| # | שם הטסט | עדיפות | זמן משוער | Xray ID |
|---|---------|---------|------------|---------|
| 1 | Frequency Resolution Calculation | גבוהה | 2h | צריך ליצור |
| 2 | Time Resolution (lines_dt) Calculation | גבוהה | 2h | צריך ליצור |
| 3 | Frequency Bins Count Calculation | גבוהה | 1.5h | צריך ליצור |
| 4 | Output Rate from Overlap Calculation | בינונית | 2h | צריך ליצור |
| 5 | Channel Mapping Calculation (SingleChannel) | גבוהה | 2h | צריך ליצור |
| 6 | Channel Mapping Calculation (MultiChannel) | גבוהה | 2h | צריך ליצור |
| 7 | Stream Amount Calculation | בינונית | 1.5h | צריך ליצור |
| 8 | Nyquist Frequency Calculation | בינונית | 1h | צריך ליצור |
| 9 | FFT Window Size Validation | בינונית | 1.5h | צריך ליצור |
| 10 | Overlap Percentage Validation | בינונית | 1.5h | צריך ליצור |
| 11 | Time Window Duration Calculation | בינונית | 2h | צריך ליצור |
| 12 | Data Rate Calculation | נמוכה | 2h | צריך ליצור |
| 13 | Memory Usage Estimation | נמוכה | 2.5h | צריך ליצור |
| 14 | Processing Time Estimation | נמוכה | 2.5h | צריך ליצור |
| 15 | Spectrogram Dimensions Calculation | בינונית | 2h | צריך ליצור |

**סה"כ:** 15 טסטים | זמן משוער: 28.5 שעות (~4 ימי עבודה)

---

## 📝 פירוט מלא של כל טסט

### 1️⃣ Frequency Resolution Calculation

**שם הטסט:**
```python
test_frequency_resolution_calculation_from_nfft()
```

**תיאור:**
בדיקה שהמערכת מחשבת נכון את רזולוציית התדר מתוך NFFT ו-PRR.

**נוסחה:**
```
frequency_resolution = PRR / NFFT

כאשר:
- PRR = Pulse Repetition Rate (samples/second)
- NFFT = Number of FFT points
```

**תרחישי בדיקה:**

| PRR | NFFT | Frequency Resolution צפוי |
|-----|------|---------------------------|
| 1000 Hz | 256 | 3.906 Hz |
| 1000 Hz | 512 | 1.953 Hz |
| 1000 Hz | 1024 | 0.977 Hz |
| 1000 Hz | 2048 | 0.488 Hz |
| 2000 Hz | 512 | 3.906 Hz |
| 500 Hz | 256 | 1.953 Hz |

**מה לבדוק:**
```python
def test_frequency_resolution_calculation_from_nfft():
    """
    Test: Frequency Resolution = PRR / NFFT
    
    Validates that the system correctly calculates frequency resolution
    from the PRR and NFFT parameters.
    
    Steps:
    1. Get PRR from system (/sensors or /metadata)
    2. Configure with specific NFFT
    3. Get metadata response
    4. Extract frequency_resolution (if returned)
    5. Calculate expected: PRR / NFFT
    6. Assert: calculated == expected (with tolerance 0.001 Hz)
    
    Example:
        PRR = 1000 Hz
        NFFT = 512
        Expected: 1000/512 = 1.953 Hz
    """
    # Test implementation
    prr = 1000  # From sensors
    nfft = 512
    
    config = create_config(nfft=nfft)
    response = api.configure(config)
    metadata = api.get_metadata(response.job_id)
    
    expected_freq_res = prr / nfft
    
    # If system returns frequency_resolution
    if hasattr(metadata, 'frequency_resolution'):
        assert abs(metadata.frequency_resolution - expected_freq_res) < 0.001
    
    # Alternative: calculate from frequency bins
    # freq_res = (max_freq - min_freq) / number_of_bins
```

**קריטריוני הצלחה:**
- ✅ חישוב נכון בדיוק של 0.001 Hz
- ✅ עובד עם כל ערכי NFFT התקפים (256, 512, 1024, 2048)
- ✅ עובד עם PRR שונים

**עדיפות:** גבוהה  
**זמן משוער:** 2 שעות

---

### 2️⃣ Time Resolution (lines_dt) Calculation

**שם הטסט:**
```python
test_time_resolution_lines_dt_calculation()
```

**תיאור:**
בדיקה שהמערכת מחשבת נכון את רזולוציית הזמן (הזמן בין שתי שורות ב-spectrogram).

**נוסחה:**
```
lines_dt = (NFFT - Overlap) / PRR

כאשר:
- NFFT = Number of FFT points
- Overlap = Number of overlapping samples
- PRR = Pulse Repetition Rate (samples/second)
```

**תרחישי בדיקה:**

| NFFT | Overlap | PRR | lines_dt צפוי |
|------|---------|-----|---------------|
| 512 | 256 | 1000 | 0.256 sec |
| 512 | 384 | 1000 | 0.128 sec |
| 1024 | 512 | 1000 | 0.512 sec |
| 1024 | 768 | 1000 | 0.256 sec |
| 512 | 0 | 1000 | 0.512 sec |
| 2048 | 1024 | 2000 | 0.512 sec |

**מה לבדוק:**
```python
def test_time_resolution_lines_dt_calculation():
    """
    Test: lines_dt = (NFFT - Overlap) / PRR
    
    Validates time resolution calculation, which represents
    the time between consecutive lines in the spectrogram.
    
    Steps:
    1. Configure with specific NFFT and Overlap
    2. Get metadata response
    3. Extract lines_dt from response
    4. Calculate expected: (NFFT - Overlap) / PRR
    5. Assert: lines_dt == expected (tolerance 0.001 sec)
    
    Example:
        NFFT = 512
        Overlap = 256
        PRR = 1000 Hz
        Expected: (512-256)/1000 = 0.256 seconds
    """
    prr = 1000
    nfft = 512
    overlap = 256
    
    config = create_config(nfft=nfft, overlap=overlap)
    response = api.configure(config)
    metadata = api.get_metadata(response.job_id)
    
    expected_lines_dt = (nfft - overlap) / prr
    actual_lines_dt = metadata.lines_dt
    
    assert abs(actual_lines_dt - expected_lines_dt) < 0.001, \
        f"lines_dt mismatch: expected {expected_lines_dt}, got {actual_lines_dt}"
```

**קריטריוני הצלחה:**
- ✅ חישוב נכון בדיוק של 0.001 שניות
- ✅ עובד עם Overlap שונים (0, 25%, 50%, 75%)
- ✅ מטפל נכון ב-Overlap=0 (no overlap)

**עדיפות:** גבוהה  
**זמן משוער:** 2 שעות

---

### 3️⃣ Frequency Bins Count Calculation

**שם הטסט:**
```python
test_frequency_bins_count_calculation()
```

**תיאור:**
בדיקה שמספר הבינים התדריים מחושב נכון מתוך NFFT.

**נוסחה:**
```
frequencies_amount = NFFT / 2 + 1

(רק חצי מה-FFT מכיל מידע שימושי בגלל סימטריה)
```

**תרחישי בדיקה:**

| NFFT | frequencies_amount צפוי |
|------|-------------------------|
| 256 | 129 |
| 512 | 257 |
| 1024 | 513 |
| 2048 | 1025 |

**מה לבדוק:**
```python
def test_frequency_bins_count_calculation():
    """
    Test: frequencies_amount = NFFT / 2 + 1
    
    Validates that the number of frequency bins is calculated
    correctly from NFFT.
    
    Explanation:
    FFT produces NFFT frequency bins, but only NFFT/2+1 are unique
    due to symmetry of real-valued signals.
    
    Steps:
    1. Configure with specific NFFT
    2. Get metadata response
    3. Extract frequencies_amount
    4. Calculate expected: NFFT / 2 + 1
    5. Assert: frequencies_amount == expected
    
    Example:
        NFFT = 512
        Expected: 512/2 + 1 = 257 bins
    """
    test_cases = [
        {"nfft": 256, "expected": 129},
        {"nfft": 512, "expected": 257},
        {"nfft": 1024, "expected": 513},
        {"nfft": 2048, "expected": 1025},
    ]
    
    for case in test_cases:
        config = create_config(nfft=case["nfft"])
        response = api.configure(config)
        metadata = api.get_metadata(response.job_id)
        
        assert metadata.frequencies_amount == case["expected"], \
            f"NFFT={case['nfft']}: expected {case['expected']}, got {metadata.frequencies_amount}"
```

**קריטריוני הצלחה:**
- ✅ חישוב מדויק (integer, לא float)
- ✅ עובד עם כל ערכי NFFT התקפים

**עדיפות:** גבוהה  
**זמן משוער:** 1.5 שעות

---

### 4️⃣ Output Rate from Overlap Calculation

**שם הטסט:**
```python
test_output_rate_from_overlap_calculation()
```

**תיאור:**
בדיקה שקצב הפלט (כמה spectrogram lines לשנייה) מחושב נכון.

**נוסחה:**
```
output_rate = PRR / (NFFT - Overlap)

או:
output_rate = 1 / lines_dt
```

**תרחישי בדיקה:**

| NFFT | Overlap | PRR | Output Rate צפוי |
|------|---------|-----|------------------|
| 512 | 256 | 1000 | 3.906 lines/sec |
| 512 | 384 | 1000 | 7.813 lines/sec |
| 1024 | 512 | 1000 | 1.953 lines/sec |
| 1024 | 768 | 1000 | 3.906 lines/sec |
| 512 | 0 | 1000 | 1.953 lines/sec |

**מה לבדוק:**
```python
def test_output_rate_from_overlap_calculation():
    """
    Test: output_rate = PRR / (NFFT - Overlap)
    
    Validates calculation of how many spectrogram lines
    are produced per second.
    
    Higher overlap → more output lines per second
    Lower overlap → fewer output lines per second
    
    Steps:
    1. Configure with varying Overlap values
    2. Calculate expected output_rate = PRR / (NFFT - Overlap)
    3. Validate against system calculation
    4. Verify: Higher overlap → Higher output rate
    
    Example:
        NFFT = 512, Overlap = 256, PRR = 1000
        output_rate = 1000 / (512-256) = 3.906 lines/sec
    """
    prr = 1000
    nfft = 512
    
    test_cases = [
        {"overlap": 0, "expected_rate": 1000/512},
        {"overlap": 128, "expected_rate": 1000/384},
        {"overlap": 256, "expected_rate": 1000/256},
        {"overlap": 384, "expected_rate": 1000/128},
    ]
    
    for case in test_cases:
        config = create_config(nfft=nfft, overlap=case["overlap"])
        response = api.configure(config)
        metadata = api.get_metadata(response.job_id)
        
        actual_rate = 1 / metadata.lines_dt
        expected_rate = case["expected_rate"]
        
        assert abs(actual_rate - expected_rate) < 0.01, \
            f"Output rate mismatch: expected {expected_rate}, got {actual_rate}"
```

**קריטריוני הצלחה:**
- ✅ חישוב נכון בדיוק של 0.01 lines/sec
- ✅ יחס הפוך נכון: יותר overlap = יותר lines/sec

**עדיפות:** בינונית  
**זמן משוער:** 2 שעות

---

### 5️⃣ Channel Mapping Calculation (SingleChannel)

**שם הטסט:**
```python
test_channel_mapping_calculation_singlechannel()
```

**תיאור:**
בדיקה ש-Channel mapping נכון ב-SingleChannel mode.

**לוגיקה:**
```
SingleChannel: min == max

Request: channels = {min: 7, max: 7}

Expected Response:
- channel_amount = 1
- stream_amount = 1
- channel_to_stream_index = {7: 0}
```

**תרחישי בדיקה:**

| Channel Request | channel_amount | stream_amount | Mapping |
|----------------|----------------|---------------|---------|
| {min: 1, max: 1} | 1 | 1 | {1: 0} |
| {min: 5, max: 5} | 1 | 1 | {5: 0} |
| {min: 10, max: 10} | 1 | 1 | {10: 0} |
| {min: 100, max: 100} | 1 | 1 | {100: 0} |

**מה לבדוק:**
```python
def test_channel_mapping_calculation_singlechannel():
    """
    Test: SingleChannel mapping validation
    
    In SingleChannel mode (min == max), validates:
    1. channel_amount = 1
    2. stream_amount = 1
    3. channel_to_stream_index = {requested_channel: 0}
    
    Steps:
    1. Configure SingleChannel (min == max)
    2. Get metadata
    3. Validate channel_amount == 1
    4. Validate stream_amount == 1
    5. Validate mapping: {channel: 0}
    
    Example:
        Request: channels = {min: 7, max: 7}
        Expected:
        - channel_amount = 1
        - stream_amount = 1
        - channel_to_stream_index = {"7": 0}
    """
    test_channels = [1, 5, 10, 50, 100]
    
    for channel in test_channels:
        config = create_config(
            channels={"min": channel, "max": channel}
        )
        response = api.configure(config)
        metadata = api.get_metadata(response.job_id)
        
        # Validate counts
        assert metadata.channel_amount == 1, \
            f"SingleChannel: expected channel_amount=1, got {metadata.channel_amount}"
        
        assert metadata.stream_amount == 1, \
            f"SingleChannel: expected stream_amount=1, got {metadata.stream_amount}"
        
        # Validate mapping
        assert str(channel) in metadata.channel_to_stream_index, \
            f"Channel {channel} not in mapping"
        
        assert metadata.channel_to_stream_index[str(channel)] == 0, \
            f"Expected mapping {channel}→0, got {metadata.channel_to_stream_index[str(channel)]}"
```

**קריטריוני הצלחה:**
- ✅ תמיד channel_amount = 1
- ✅ תמיד stream_amount = 1
- ✅ mapping נכון לכל channel

**עדיפות:** גבוהה  
**זמן משוער:** 2 שעות

---

### 6️⃣ Channel Mapping Calculation (MultiChannel)

**שם הטסט:**
```python
test_channel_mapping_calculation_multichannel()
```

**תיאור:**
בדיקה ש-Channel mapping נכון ב-MultiChannel mode.

**לוגיקה:**
```
MultiChannel: min < max

Request: channels = {min: 5, max: 10}

Expected Response:
- channel_amount = 6  (10 - 5 + 1)
- stream_amount = 6
- channel_to_stream_index = {
    "5": 0,
    "6": 1,
    "7": 2,
    "8": 3,
    "9": 4,
    "10": 5
  }
```

**תרחישי בדיקה:**

| Min | Max | channel_amount | Mapping |
|-----|-----|----------------|---------|
| 1 | 8 | 8 | {1:0, 2:1, ..., 8:7} |
| 5 | 10 | 6 | {5:0, 6:1, ..., 10:5} |
| 10 | 15 | 6 | {10:0, 11:1, ..., 15:5} |
| 1 | 100 | 100 | {1:0, 2:1, ..., 100:99} |

**מה לבדוק:**
```python
def test_channel_mapping_calculation_multichannel():
    """
    Test: MultiChannel mapping validation
    
    Validates:
    1. channel_amount = max - min + 1
    2. stream_amount = channel_amount
    3. Correct sequential mapping
    
    Steps:
    1. Configure MultiChannel (min < max)
    2. Get metadata
    3. Calculate expected_amount = max - min + 1
    4. Validate channel_amount == expected
    5. Validate stream_amount == expected
    6. Validate each channel maps correctly:
       channel[i] → stream_index[i]
    
    Example:
        Request: channels = {min: 5, max: 10}
        Expected:
        - channel_amount = 6
        - stream_amount = 6
        - Mapping: 5→0, 6→1, 7→2, 8→3, 9→4, 10→5
    """
    test_cases = [
        {"min": 1, "max": 8},
        {"min": 5, "max": 10},
        {"min": 10, "max": 15},
        {"min": 1, "max": 100},
    ]
    
    for case in test_cases:
        min_ch = case["min"]
        max_ch = case["max"]
        expected_amount = max_ch - min_ch + 1
        
        config = create_config(
            channels={"min": min_ch, "max": max_ch}
        )
        response = api.configure(config)
        metadata = api.get_metadata(response.job_id)
        
        # Validate counts
        assert metadata.channel_amount == expected_amount, \
            f"Expected {expected_amount}, got {metadata.channel_amount}"
        
        assert metadata.stream_amount == expected_amount, \
            f"Expected stream_amount={expected_amount}, got {metadata.stream_amount}"
        
        # Validate mapping
        for i, channel in enumerate(range(min_ch, max_ch + 1)):
            assert str(channel) in metadata.channel_to_stream_index, \
                f"Channel {channel} missing from mapping"
            
            actual_index = metadata.channel_to_stream_index[str(channel)]
            assert actual_index == i, \
                f"Channel {channel}: expected stream_index={i}, got {actual_index}"
```

**קריטריוני הצלחה:**
- ✅ channel_amount = max - min + 1
- ✅ mapping רציף וסדר נכון
- ✅ עובד עם טווחים שונים

**עדיפות:** גבוהה  
**זמן משוער:** 2 שעות

---

### 7️⃣ Stream Amount Calculation

**שם הטסט:**
```python
test_stream_amount_calculation()
```

**תיאור:**
בדיקה ש-stream_amount תואם ל-channel_amount.

**לוגיקה:**
```
stream_amount == channel_amount

מדוע?
כל channel מקבל stream נפרד
```

**תרחישי בדיקה:**

| View Type | Channels | stream_amount צפוי |
|-----------|----------|-------------------|
| MultiChannel | {1, 8} | 8 |
| SingleChannel | {7, 7} | 1 |
| MultiChannel | {5, 10} | 6 |
| Waterfall | {1, 100} | 100 |

**מה לבדוק:**
```python
def test_stream_amount_calculation():
    """
    Test: stream_amount == channel_amount
    
    Validates that the number of streams equals
    the number of channels in all view types.
    
    Steps:
    1. Configure with various channel ranges
    2. Get metadata
    3. Assert: stream_amount == channel_amount
    
    This should hold for:
    - SingleChannel (1 channel → 1 stream)
    - MultiChannel (N channels → N streams)
    - Waterfall (N channels → N streams)
    """
    test_cases = [
        {"min": 1, "max": 1, "expected": 1},  # SingleChannel
        {"min": 1, "max": 8, "expected": 8},  # MultiChannel
        {"min": 5, "max": 10, "expected": 6},
        {"min": 1, "max": 100, "expected": 100},
    ]
    
    for case in test_cases:
        config = create_config(
            channels={"min": case["min"], "max": case["max"]}
        )
        response = api.configure(config)
        metadata = api.get_metadata(response.job_id)
        
        assert metadata.stream_amount == case["expected"], \
            f"Expected stream_amount={case['expected']}, got {metadata.stream_amount}"
        
        assert metadata.stream_amount == metadata.channel_amount, \
            f"stream_amount ({metadata.stream_amount}) != channel_amount ({metadata.channel_amount})"
```

**קריטריוני הצלחה:**
- ✅ תמיד stream_amount == channel_amount
- ✅ עובד בכל view types

**עדיפות:** בינונית  
**זמן משוער:** 1.5 שעות

---

### 8️⃣ Nyquist Frequency Calculation

**שם הטסט:**
```python
test_nyquist_frequency_calculation()
```

**תיאור:**
בדיקה שהמערכת מחשבת נכון את תדר Nyquist ודוחה תדרים מעליו.

**נוסחה:**
```
Nyquist_Frequency = PRR / 2

תדרים מעל Nyquist → Aliasing → לא תקף
```

**תרחישי בדיקה:**

| PRR | Nyquist | תדר מבוקש | תוצאה צפויה |
|-----|---------|-----------|-------------|
| 1000 Hz | 500 Hz | 400 Hz | ✅ מקובל |
| 1000 Hz | 500 Hz | 500 Hz | ✅ מקובל (גבול) |
| 1000 Hz | 500 Hz | 501 Hz | ❌ נדחה |
| 2000 Hz | 1000 Hz | 999 Hz | ✅ מקובל |
| 500 Hz | 250 Hz | 300 Hz | ❌ נדחה |

**מה לבדוק:**
```python
def test_nyquist_frequency_calculation():
    """
    Test: Nyquist = PRR / 2, reject frequencies above Nyquist
    
    Validates:
    1. System calculates Nyquist correctly
    2. Frequencies <= Nyquist are accepted
    3. Frequencies > Nyquist are rejected (400 Bad Request)
    
    Steps:
    1. Get PRR from system
    2. Calculate Nyquist = PRR / 2
    3. Test frequencies below Nyquist → should succeed
    4. Test frequencies above Nyquist → should fail with 400
    5. Test frequency == Nyquist → should succeed (edge case)
    
    Example:
        PRR = 1000 Hz
        Nyquist = 500 Hz
        
        Test freq=400 → ✅ Accept
        Test freq=500 → ✅ Accept (boundary)
        Test freq=501 → ❌ Reject (400 Bad Request)
    """
    prr = get_prr_from_system()  # e.g., 1000
    nyquist = prr / 2
    
    # Test below Nyquist - should succeed
    config_below = create_config(
        frequency_range={"min": 0, "max": nyquist - 100}
    )
    response = api.configure(config_below)
    assert response.status_code == 200, "Frequency below Nyquist should be accepted"
    
    # Test at Nyquist - should succeed
    config_at = create_config(
        frequency_range={"min": 0, "max": nyquist}
    )
    response = api.configure(config_at)
    assert response.status_code == 200, "Frequency at Nyquist should be accepted"
    
    # Test above Nyquist - should fail
    config_above = create_config(
        frequency_range={"min": 0, "max": nyquist + 1}
    )
    with pytest.raises(APIError) as exc:
        api.configure(config_above)
    assert exc.value.status_code == 400, "Frequency above Nyquist should be rejected"
    assert "Nyquist" in str(exc.value), "Error should mention Nyquist limit"
```

**קריטריוני הצלחה:**
- ✅ Nyquist מחושב נכון: PRR/2
- ✅ דחייה נכונה של תדרים גבוהים
- ✅ קבלה נכונה של תדרים תקפים

**עדיפות:** בינונית  
**זמן משוער:** 1 שעה

---

### 9️⃣ FFT Window Size Validation

**שם הטסט:**
```python
test_fft_window_size_validation()
```

**תיאור:**
בדיקה ש-NFFT הוא power of 2 (אופטימלי ל-FFT).

**לוגיקה:**
```
NFFT צריך להיות: 2^n

תקף: 256, 512, 1024, 2048
לא תקף: 100, 300, 500, 1000
```

**תרחישי בדיקה:**

| NFFT | Power of 2? | תוצאה צפויה |
|------|-------------|-------------|
| 256 | ✅ (2^8) | מקובל |
| 512 | ✅ (2^9) | מקובל |
| 1024 | ✅ (2^10) | מקובל |
| 2048 | ✅ (2^11) | מקובל |
| 1000 | ❌ | נדחה |
| 500 | ❌ | נדחה |
| 300 | ❌ | נדחה |

**מה לבדוק:**
```python
def test_fft_window_size_validation():
    """
    Test: NFFT must be power of 2
    
    FFT algorithms are most efficient when N is a power of 2.
    System should only accept: 256, 512, 1024, 2048
    
    Steps:
    1. Test valid NFFT values (powers of 2) → should succeed
    2. Test invalid NFFT values (not powers of 2) → should fail
    3. Verify error message mentions "power of 2"
    
    Valid: 256, 512, 1024, 2048
    Invalid: 100, 300, 500, 1000, 1500
    """
    # Test valid values
    valid_nfft = [256, 512, 1024, 2048]
    for nfft in valid_nfft:
        config = create_config(nfft=nfft)
        response = api.configure(config)
        assert response.status_code == 200, \
            f"NFFT={nfft} (power of 2) should be accepted"
    
    # Test invalid values
    invalid_nfft = [100, 300, 500, 1000, 1500, 200, 400]
    for nfft in invalid_nfft:
        config = create_config(nfft=nfft)
        with pytest.raises(APIError) as exc:
            api.configure(config)
        
        assert exc.value.status_code == 400, \
            f"NFFT={nfft} (not power of 2) should be rejected"
        
        error_msg = str(exc.value).lower()
        assert "power" in error_msg or "nfft" in error_msg, \
            "Error should mention NFFT or power of 2"
```

**קריטריוני הצלחה:**
- ✅ כל power of 2 מתקבל
- ✅ כל non-power of 2 נדחה
- ✅ הודעת שגיאה ברורה

**עדיפות:** בינונית  
**זמן משוער:** 1.5 שעות

---

### 🔟 Overlap Percentage Validation

**שם הטסט:**
```python
test_overlap_percentage_validation()
```

**תיאור:**
בדיקה ש-Overlap הוא אחוז תקף מ-NFFT.

**לוגיקה:**
```
Overlap צריך להיות: 0 <= Overlap < NFFT

אחוזים נפוצים:
- 0% (Overlap = 0)
- 25% (Overlap = NFFT * 0.25)
- 50% (Overlap = NFFT * 0.5)
- 75% (Overlap = NFFT * 0.75)
```

**תרחישי בדיקה:**

| NFFT | Overlap | אחוז | תוצאה צפויה |
|------|---------|------|-------------|
| 512 | 0 | 0% | ✅ תקף |
| 512 | 128 | 25% | ✅ תקף |
| 512 | 256 | 50% | ✅ תקף |
| 512 | 384 | 75% | ✅ תקף |
| 512 | 511 | ~99% | ✅ תקף |
| 512 | 512 | 100% | ❌ לא תקף |
| 512 | 600 | >100% | ❌ לא תקף |
| 512 | -50 | שלילי | ❌ לא תקף |

**מה לבדוק:**
```python
def test_overlap_percentage_validation():
    """
    Test: 0 <= Overlap < NFFT
    
    Overlap must be between 0 and NFFT-1.
    100% overlap (Overlap == NFFT) is invalid.
    
    Steps:
    1. Test valid overlaps (0% to 99%) → should succeed
    2. Test Overlap == NFFT (100%) → should fail
    3. Test Overlap > NFFT → should fail
    4. Test negative Overlap → should fail
    
    Common valid percentages:
    - 0% (no overlap)
    - 25% (NFFT * 0.25)
    - 50% (NFFT * 0.5)
    - 75% (NFFT * 0.75)
    """
    nfft = 512
    
    # Test valid overlaps
    valid_overlaps = [
        0,          # 0%
        128,        # 25%
        256,        # 50%
        384,        # 75%
        500,        # ~97%
        511,        # ~99%
    ]
    
    for overlap in valid_overlaps:
        config = create_config(nfft=nfft, overlap=overlap)
        response = api.configure(config)
        assert response.status_code == 200, \
            f"Overlap={overlap} ({overlap/nfft*100:.0f}%) should be accepted"
    
    # Test invalid overlaps
    invalid_overlaps = [
        -50,        # Negative
        512,        # 100% (equals NFFT)
        600,        # > NFFT
        1000,       # >> NFFT
    ]
    
    for overlap in invalid_overlaps:
        config = create_config(nfft=nfft, overlap=overlap)
        with pytest.raises(APIError) as exc:
            api.configure(config)
        
        assert exc.value.status_code == 400, \
            f"Overlap={overlap} should be rejected"
```

**קריטריוני הצלחה:**
- ✅ כל overlap תקף (0 עד NFFT-1) מתקבל
- ✅ overlap >= NFFT נדחה
- ✅ overlap שלילי נדחה

**עדיפות:** בינונית  
**זמן משוער:** 1.5 שעות

---

### 1️⃣1️⃣ Time Window Duration Calculation

**שם הטסט:**
```python
test_time_window_duration_calculation()
```

**תיאור:**
בדיקה שמשך חלון הזמן מחושב נכון.

**נוסחה:**
```
time_window_duration = NFFT / PRR

(זמן שלוקח לאסוף NFFT דגימות)
```

**תרחישי בדיקה:**

| NFFT | PRR | Duration צפוי |
|------|-----|---------------|
| 512 | 1000 | 0.512 sec |
| 1024 | 1000 | 1.024 sec |
| 2048 | 1000 | 2.048 sec |
| 512 | 2000 | 0.256 sec |
| 1024 | 500 | 2.048 sec |

**מה לבדוק:**
```python
def test_time_window_duration_calculation():
    """
    Test: time_window = NFFT / PRR
    
    Calculates the duration of each FFT window in seconds.
    
    Steps:
    1. Configure with different NFFT values
    2. Calculate expected duration = NFFT / PRR
    3. Validate against metadata (if provided)
    
    Example:
        NFFT = 512
        PRR = 1000 Hz
        Expected: 512/1000 = 0.512 seconds
    """
    prr = 1000
    
    test_cases = [
        {"nfft": 256, "expected": 0.256},
        {"nfft": 512, "expected": 0.512},
        {"nfft": 1024, "expected": 1.024},
        {"nfft": 2048, "expected": 2.048},
    ]
    
    for case in test_cases:
        config = create_config(nfft=case["nfft"])
        response = api.configure(config)
        
        expected_duration = case["nfft"] / prr
        
        # If system returns time_window_duration
        metadata = api.get_metadata(response.job_id)
        if hasattr(metadata, 'time_window_duration'):
            assert abs(metadata.time_window_duration - expected_duration) < 0.001, \
                f"Expected {expected_duration}, got {metadata.time_window_duration}"
        
        # Alternative validation
        assert abs(expected_duration - case["expected"]) < 0.001
```

**קריטריוני הצלחה:**
- ✅ חישוב נכון בדיוק של 0.001 שניות
- ✅ עובד עם כל ערכי NFFT

**עדיפות:** בינונית  
**זמן משוער:** 2 שעות

---

### 1️⃣2️⃣ Data Rate Calculation

**שם הטסט:**
```python
test_data_rate_calculation()
```

**תיאור:**
בדיקה של קצב הנתונים (bytes/second או samples/second).

**נוסחה:**
```
data_rate = channel_amount * frequencies_amount * output_rate * bytes_per_sample

כאשר:
- bytes_per_sample = 4 (float32) או 8 (float64)
```

**תרחישי בדיקה:**

| Channels | Freq Bins | Output Rate | Data Rate צפוי |
|----------|-----------|-------------|-----------------|
| 8 | 257 | 3.906 | ~32 KB/sec |
| 1 | 257 | 3.906 | ~4 KB/sec |
| 100 | 513 | 1.953 | ~400 KB/sec |

**מה לבדוק:**
```python
def test_data_rate_calculation():
    """
    Test: data_rate = channels * freq_bins * output_rate * bytes_per_sample
    
    Estimates the data throughput in bytes/second.
    
    Useful for:
    - Network bandwidth planning
    - Storage capacity planning
    - Performance estimation
    
    Steps:
    1. Configure job
    2. Calculate:
       - freq_bins = NFFT/2 + 1
       - output_rate = PRR / (NFFT - Overlap)
       - data_rate = channels * freq_bins * output_rate * 4
    3. Validate calculation is reasonable
    
    Example:
        8 channels, 512 NFFT, 256 Overlap, PRR=1000
        - freq_bins = 257
        - output_rate = 1000/256 = 3.906 lines/sec
        - data_rate = 8 * 257 * 3.906 * 4 = ~32,170 bytes/sec (~31 KB/sec)
    """
    prr = 1000
    nfft = 512
    overlap = 256
    bytes_per_sample = 4  # float32
    
    test_cases = [
        {"channels": {"min": 1, "max": 8}},
        {"channels": {"min": 1, "max": 1}},  # SingleChannel
        {"channels": {"min": 1, "max": 100}},
    ]
    
    for case in test_cases:
        config = create_config(
            nfft=nfft,
            overlap=overlap,
            channels=case["channels"]
        )
        response = api.configure(config)
        metadata = api.get_metadata(response.job_id)
        
        # Calculate expected data rate
        freq_bins = nfft // 2 + 1
        output_rate = prr / (nfft - overlap)
        channel_count = metadata.channel_amount
        
        expected_rate = channel_count * freq_bins * output_rate * bytes_per_sample
        
        # Log for analysis
        logger.info(f"Channels: {channel_count}")
        logger.info(f"Expected data rate: {expected_rate:.0f} bytes/sec ({expected_rate/1024:.1f} KB/sec)")
        
        # Validate calculation is reasonable
        assert expected_rate > 0, "Data rate must be positive"
        assert expected_rate < 100_000_000, "Data rate seems unreasonably high"
```

**קריטריוני הצלחה:**
- ✅ חישוב הגיוני
- ✅ עולה עם מספר channels
- ✅ עולה עם NFFT

**עדיפות:** נמוכה  
**זמן משוער:** 2 שעות

---

### 1️⃣3️⃣ Memory Usage Estimation

**שם הטסט:**
```python
test_memory_usage_estimation()
```

**תיאור:**
בדיקה של אומדן צריכת הזיכרון.

**נוסחה:**
```
memory_per_frame = channels * freq_bins * bytes_per_sample
total_memory = memory_per_frame * frames_in_buffer

כאשר frames_in_buffer תלוי ב-buffer size
```

**תרחישי בדיקה:**

| NFFT | Channels | Memory per Frame |
|------|----------|------------------|
| 512 | 8 | ~8 KB |
| 1024 | 8 | ~16 KB |
| 2048 | 8 | ~32 KB |
| 512 | 100 | ~100 KB |

**מה לבדוק:**
```python
def test_memory_usage_estimation():
    """
    Test: memory = channels * (NFFT/2+1) * 4 bytes
    
    Estimates memory usage per spectrogram frame.
    
    Useful for:
    - Resource allocation
    - System capacity planning
    - Performance tuning
    
    Steps:
    1. Configure with varying parameters
    2. Calculate expected memory per frame
    3. Verify calculation is reasonable
    4. Verify: Larger NFFT → More memory
    5. Verify: More channels → More memory
    
    Example:
        NFFT = 512 (257 freq bins)
        Channels = 8
        Memory = 8 * 257 * 4 = 8,224 bytes (~8 KB per frame)
    """
    bytes_per_sample = 4  # float32
    
    test_cases = [
        {"nfft": 512, "channels": 8, "expected_kb": 8},
        {"nfft": 1024, "channels": 8, "expected_kb": 16},
        {"nfft": 2048, "channels": 8, "expected_kb": 32},
        {"nfft": 512, "channels": 100, "expected_kb": 100},
    ]
    
    for case in test_cases:
        freq_bins = case["nfft"] // 2 + 1
        memory_bytes = case["channels"] * freq_bins * bytes_per_sample
        memory_kb = memory_bytes / 1024
        
        assert abs(memory_kb - case["expected_kb"]) < 1, \
            f"Expected ~{case['expected_kb']} KB, got {memory_kb:.1f} KB"
        
        logger.info(f"NFFT={case['nfft']}, Channels={case['channels']}: {memory_kb:.1f} KB per frame")
    
    # Verify relationships
    # Doubling NFFT should double memory (approximately)
    mem_512 = (512//2+1) * 8 * 4
    mem_1024 = (1024//2+1) * 8 * 4
    assert mem_1024 / mem_512 > 1.9, "Doubling NFFT should approximately double memory"
```

**קריטריוני הצלחה:**
- ✅ חישוב הגיוני
- ✅ זיכרון עולה עם NFFT
- ✅ זיכרון עולה עם Channels

**עדיפות:** נמוכה  
**זמן משוער:** 2.5 שעות

---

### 1️⃣4️⃣ Processing Time Estimation

**שם הטסט:**
```python
test_processing_time_estimation()
```

**תיאור:**
בדיקה של אומדן זמן עיבוד.

**לוגיקה:**
```
Factors affecting processing time:
- NFFT size (larger = slower FFT)
- Number of channels (more = more FFTs)
- Overlap (more overlap = more frames to process)
```

**מה לבדוק:**
```python
def test_processing_time_estimation():
    """
    Test: Processing time relationships
    
    While we can't predict exact processing time,
    we can verify the relationships:
    
    1. Larger NFFT → Longer processing time
    2. More channels → Longer processing time  
    3. More overlap → More frames → Longer time
    
    Steps:
    1. Configure jobs with varying parameters
    2. Measure actual processing time (if possible)
    3. Verify relationships hold
    
    Note: This is empirical, not a strict calculation test
    """
    # This test would require actual job execution
    # and timing measurements
    pass
```

**קריטריוני הצלחה:**
- ✅ יחסים נכונים (יותר NFFT = יותר זמן)
- ✅ מדידה אמפירית

**עדיפות:** נמוכה  
**זמן משוער:** 2.5 שעות

---

### 1️⃣5️⃣ Spectrogram Dimensions Calculation

**שם הטסט:**
```python
test_spectrogram_dimensions_calculation()
```

**תיאור:**
בדיקה שממדי ה-spectrogram מחושבים נכון.

**נוסחה:**
```
Width (time axis) = (duration / lines_dt)
Height (frequency axis) = frequencies_amount

כאשר:
- duration = end_time - start_time (למצב historic)
- lines_dt = (NFFT - Overlap) / PRR
```

**תרחישי בדיקה:**

| Duration | lines_dt | NFFT | Width | Height |
|----------|----------|------|-------|--------|
| 60 sec | 0.256 sec | 512 | ~234 lines | 257 |
| 120 sec | 0.512 sec | 1024 | ~234 lines | 513 |
| 300 sec | 0.256 sec | 512 | ~1172 lines | 257 |

**מה לבדוק:**
```python
def test_spectrogram_dimensions_calculation():
    """
    Test: Spectrogram dimensions calculation
    
    For historic mode:
    Width = (end_time - start_time) / lines_dt
    Height = NFFT / 2 + 1
    
    Steps:
    1. Configure historic job with known time range
    2. Calculate expected dimensions
    3. Validate against system (if available)
    
    Example:
        Duration = 60 seconds
        NFFT = 512, Overlap = 256, PRR = 1000
        lines_dt = 256/1000 = 0.256 sec
        
        Width = 60 / 0.256 = 234.375 lines
        Height = 512/2 + 1 = 257 frequency bins
    """
    prr = 1000
    nfft = 512
    overlap = 256
    
    # Historic time range
    duration_seconds = 60
    start_time = int(datetime.now().timestamp())
    end_time = start_time + duration_seconds
    
    config = create_historic_config(
        nfft=nfft,
        overlap=overlap,
        start_time=start_time,
        end_time=end_time
    )
    
    response = api.configure(config)
    metadata = api.get_metadata(response.job_id)
    
    # Calculate expected dimensions
    lines_dt = (nfft - overlap) / prr
    expected_width = duration_seconds / lines_dt
    expected_height = nfft // 2 + 1
    
    logger.info(f"Expected spectrogram dimensions: {expected_width:.0f} x {expected_height}")
    
    # Validate height (should always be in metadata)
    assert metadata.frequencies_amount == expected_height, \
        f"Height mismatch: expected {expected_height}, got {metadata.frequencies_amount}"
    
    # Width validation (if system provides it)
    if hasattr(metadata, 'spectrogram_width'):
        assert abs(metadata.spectrogram_width - expected_width) < 1, \
            f"Width mismatch: expected {expected_width:.0f}, got {metadata.spectrogram_width}"
```

**קריטריוני הצלחה:**
- ✅ Height מחושב נכון
- ✅ Width מחושב נכון (אם זמין)
- ✅ עובד עם duration שונים

**עדיפות:** בינונית  
**זמן משוער:** 2 שעות

---

## 📊 סיכום וסדר עדיפויות

### 🔴 עדיפות גבוהה (7 טסטים - 13.5 שעות)
1. ✅ Frequency Resolution Calculation
2. ✅ Time Resolution (lines_dt) Calculation
3. ✅ Frequency Bins Count Calculation
5. ✅ Channel Mapping (SingleChannel)
6. ✅ Channel Mapping (MultiChannel)

### 🟡 עדיפות בינונית (6 טסטים - 11 שעות)
4. ⏺ Output Rate from Overlap
7. ⏺ Stream Amount Calculation
8. ⏺ Nyquist Frequency Calculation
9. ⏺ FFT Window Size Validation
10. ⏺ Overlap Percentage Validation
11. ⏺ Time Window Duration
15. ⏺ Spectrogram Dimensions

### 🟢 עדיפות נמוכה (2 טסטים - 4.5 שעות)
12. ⏺ Data Rate Calculation
13. ⏺ Memory Usage Estimation
14. ⏺ Processing Time Estimation

---

## 🎯 תוכנית יישום מוצעת

### שבוע 1 (עדיפות גבוהה)
- ימים 1-2: טסטים 1-3 (חישובי תדר ו-NFFT)
- ימים 3-4: טסטים 5-6 (Channel Mapping)

### שבוע 2 (עדיפות בינונית)
- ימים 1-3: טסטים 4, 7-10 (Overlap, Stream, Validation)
- ימים 4-5: טסטים 11, 15 (Time Window, Dimensions)

### שבוע 3 (עדיפות נמוכה + Review)
- ימים 1-2: טסטים 12-14 (Data Rate, Memory, Processing)
- ימים 3-5: Review, תיקונים, תיעוד

**סה"כ זמן:** ~3 שבועות

---

**מסמך זה מוכן ליישום מיידי. כל טסט כולל:**
- ✅ שם מדויק
- ✅ נוסחאות מתמטיות
- ✅ תרחישי בדיקה
- ✅ קוד לדוגמה
- ✅ קריטריוני הצלחה
- ✅ אומדן זמן

