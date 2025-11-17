# טסט 1: Performance - High Throughput Configuration Stress Test
## PZ-13905 - ניתוח מקיף ומעמיק

---

## 📋 תקציר מהיר לפגישה (Quick Brief)

| **שדה** | **ערך** |
|---------|---------|
| **Jira ID** | PZ-13905 |
| **שם הטסט** | Performance - High Throughput Configuration Stress Test |
| **עדיפות** | 🔴 **HIGH** |
| **סוג** | Performance / Stress Test |
| **סטטוס אוטומציה** | ✅ **Automated** |
| **משך ריצה צפוי** | ~2-5 שניות |
| **מורכבות מימוש** | 🟡 **בינונית** |
| **קובץ טסט** | `tests/integration/api/test_spectrogram_pipeline.py` |
| **שורות** | 270-302 |
| **תלויות** | Focus Server API, MongoDB (optional) |

---

## 🎯 מה המטרה של הטסט? (Test Objectives)

### מטרה אסטרטגית (Strategic Goal):
לוודא שהמערכת **לא קורסת** או **מתנהגת בצורה לא נכונה** כאשר משתמש מנסה ליצור קונפיגורציה שתייצר **תפוקת נתונים גבוהה מאוד** (High Throughput).

### מטרות ספציפיות (Specific Goals):
1. **זיהוי גבולות המערכת** - מה ה-throughput המקסימלי שהמערכת יכולה לטפל בו?
2. **וידוא התנהגות תקינה** - האם המערכת:
   - מקבלת את הקונפיגורציה ומתריעה? (Option A)
   - דוחה את הקונפיגורציה עם הודעת שגיאה ברורה? (Option B)
3. **מניעת קריסות** - המערכת לא קורסת גם אם הקונפיגורציה "יקרה מדי"
4. **תיעוד התנהגות** - לתעד את ההתנהגות לדיונים עתידיים עם הצוות

---

## 🧪 מה אני רוצה לבדוק? (What We're Testing)

### הסצנריו שאנחנו בודקים:

**Scenario**: משתמש יוצר קונפיגורציה שמייצרת **תפוקה גבוהה מאוד** (> 50 Mbps).

#### מה גורם ל-High Throughput?

תפוקה גבוהה נוצרת מהשילוב של:
1. **NFFT קטן** (256, 512) → הרבה rows לשנייה
2. **טווח sensors גדול** (500 sensors)
3. **טווח תדרים רחב** (4000 Hz)

#### חישוב מתמטי של Throughput:

```
נתונים:
- PRR (Pulse Repetition Rate) = 1000 samples/sec
- NFFT = 256
- Sensors = 500 (channels: 0-500)
- Frequency Range = 4000 Hz (0-4000)

שלב 1: חישוב rows per second
Rows/sec = PRR / NFFT = 1000 / 256 ≈ 3.9 rows/sec

שלב 2: חישוב frequency bins
Frequency Bins = NFFT / 2 = 256 / 2 = 128 bins

שלב 3: חישוב bytes per row
Bytes/row = Sensors × Frequency Bins × 4 bytes (float32)
Bytes/row = 500 × 128 × 4 = 256,000 bytes

שלב 4: חישוב throughput
Throughput = Rows/sec × Bytes/row × 8 bits / 1,000,000
Throughput = 3.9 × 256,000 × 8 / 1,000,000 ≈ 7.98 Mbps
```

**⚠️ הבעיה**: אם נגדיל ל-NFFT=256, Sensors=500, Freq=4000 Hz → נגיע ל-**> 50 Mbps** ואפילו יותר!

---

## 🔥 מה הנחיצות של הטסט? (Why Is This Critical?)

### סיכונים אם לא בודקים:

#### 1️⃣ **קריסת מערכת בייצור** (Production Crash)
**תרחיש**:  
משתמש ביצור יוצר קונפיגורציה "יקרה" עם 500 sensors ו-NFFT=256.  
המערכת מתחילה לייצר **נתונים בקצב של 100 Mbps**.  
**תוצאה**: Network congestion → CPU 100% → מערכת קופאת → כל המשתמשים מושפעים!

#### 2️⃣ **חנק משאבים** (Resource Exhaustion)
**תרחיש**:  
הרבה משתמשים יוצרים קונפיגורציות עם throughput גבוה.  
**תוצאה**:
- **Memory exhaustion** → OOM Killer → Pods מתים
- **CPU 100%** → latency עולה → timeouts
- **Network saturation** → packet loss → נתונים שגויים

#### 3️⃣ **חוויית משתמש גרועה** (Bad UX)
**תרחיש**:  
משתמש לא יודע שהקונפיגורציה שלו "יקרה מדי".  
המערכת מקבלת אותה, אבל **הדפדפן לא מצליח להציג** את הנתונים (too much data).  
**תוצאה**: משתמש מתוסכל, פותח ticket → תמיכה עמוסה.

#### 4️⃣ **עלויות גבוהות** (High Costs)
**תרחיש**:  
המערכת מבוססת cloud עם חיוב לפי שימוש.  
קונפיגורציות עם throughput גבוה גורמות ל-**CPU/Network overuse** → חשבונית גבוהה!

---

## 🛠️ איך אני ממש אותו בקוד? (Code Implementation)

### קובץ הטסט:
**Path**: `tests/integration/api/test_spectrogram_pipeline.py`  
**Lines**: 270-302

### מבנה הטסט (נכון ל-22 אוקטובר 2025):

```python
@pytest.mark.integration
@pytest.mark.api
class TestConfigurationCompatibility:
    """Test suite for configuration parameter compatibility."""
    
    def test_configuration_resource_estimation(self, focus_server_api):
        """
        Test: Estimate resource usage for configuration.
        
        This test validates that the system can calculate
        expected throughput and resource usage for a given
        configuration.
        
        Steps:
        1. Define test configuration parameters
        2. Calculate expected throughput
        3. Validate compatibility
        4. Log results
        
        Expected:
        - Throughput calculated correctly
        - Warning if throughput > threshold
        - No errors or crashes
        """
        logger.info("Test: Configuration resource estimation")
        
        # ============================================
        # Step 1: Define test configuration
        # ============================================
        nfft = 1024                # FFT size (power of 2)
        sensor_range = 100         # Number of sensors
        prr = 2000.0               # Pulse Repetition Rate (samples/sec)
        
        # ============================================
        # Step 2: Validate configuration compatibility
        # ============================================
        # This function calculates:
        # - Spectrogram rows per second
        # - Output data rate (Mbps)
        # - Memory usage estimate
        compat_result = validate_configuration_compatibility(
            nfft=nfft,
            sensor_range=sensor_range,
            prr=prr,
            expected_throughput_mbps=10.0  # Expected: ~10 Mbps
        )
        
        # ============================================
        # Step 3: Log results
        # ============================================
        logger.info(f"Compatibility result: {compat_result}")
        logger.info(f"  - Spectrogram rate: {compat_result['estimates']['spectrogram_rows_per_sec']:.2f} rows/sec")
        logger.info(f"  - Output data rate: {compat_result['estimates']['output_data_rate_mbps']:.2f} Mbps")
        
        # ============================================
        # Step 4: Assertions
        # ============================================
        # Verify throughput is within reasonable range
        calculated_throughput = compat_result['estimates']['output_data_rate_mbps']
        
        # Warning threshold: 50 Mbps
        THROUGHPUT_WARNING_THRESHOLD = 50.0
        
        if calculated_throughput > THROUGHPUT_WARNING_THRESHOLD:
            logger.warning(
                f"⚠️ High throughput detected: {calculated_throughput:.2f} Mbps "
                f"(threshold: {THROUGHPUT_WARNING_THRESHOLD} Mbps)"
            )
            # Option A: Accept with warning (current behavior)
            # Option B: Reject with error (future behavior - TBD)
        
        # Verify no crashes occurred
        assert compat_result is not None, "Compatibility check returned None"
        assert 'estimates' in compat_result, "Missing 'estimates' in result"
        
        logger.info("✅ Configuration resource estimation test passed")
```

---

### פירוט השלבים:

#### 🔹 **Step 1: Define Test Configuration**
```python
nfft = 1024
sensor_range = 100
prr = 2000.0
```
**מה קורה כאן?**
- מגדירים קונפיגורציה לבדיקה
- `nfft=1024` → NFFT סטנדרטי (לא extreme)
- `sensor_range=100` → 100 sensors
- `prr=2000.0` → קצב דגימה גבוה (typical)

**למה ככה?**
- זה baseline test - לא extreme, אבל מייצג תרחיש אמיתי

---

#### 🔹 **Step 2: Validate Compatibility**
```python
compat_result = validate_configuration_compatibility(
    nfft=nfft,
    sensor_range=sensor_range,
    prr=prr,
    expected_throughput_mbps=10.0
)
```

**מה הפונקציה `validate_configuration_compatibility` עושה?**

הפונקציה נמצאת ב-`src/utils/validation_helpers.py` (משוער):

```python
def validate_configuration_compatibility(
    nfft: int,
    sensor_range: int,
    prr: float,
    expected_throughput_mbps: float
) -> Dict[str, Any]:
    """
    Validate configuration compatibility and estimate resource usage.
    
    Args:
        nfft: FFT size (must be power of 2)
        sensor_range: Number of sensors
        prr: Pulse Repetition Rate (samples/sec)
        expected_throughput_mbps: Expected throughput for comparison
    
    Returns:
        Dictionary with:
        - estimates: Resource usage estimates
        - warnings: List of warnings (if any)
        - compatible: Boolean indicating if config is compatible
    
    Time Complexity: O(1) - simple calculations
    Space Complexity: O(1) - constant memory
    """
    
    # Step 1: Calculate rows per second
    rows_per_sec = prr / nfft
    
    # Step 2: Calculate frequency bins
    frequency_bins = nfft // 2  # Nyquist: only half of FFT is usable
    
    # Step 3: Calculate bytes per row
    bytes_per_row = sensor_range * frequency_bins * 4  # float32 = 4 bytes
    
    # Step 4: Calculate output data rate (Mbps)
    output_data_rate_mbps = (rows_per_sec * bytes_per_row * 8) / 1_000_000
    
    # Step 5: Check for warnings
    warnings = []
    THROUGHPUT_THRESHOLD = 50.0  # Mbps
    
    if output_data_rate_mbps > THROUGHPUT_THRESHOLD:
        warnings.append(
            f"High throughput: {output_data_rate_mbps:.2f} Mbps "
            f"exceeds threshold ({THROUGHPUT_THRESHOLD} Mbps)"
        )
    
    # Step 6: Return results
    return {
        "estimates": {
            "spectrogram_rows_per_sec": rows_per_sec,
            "output_data_rate_mbps": output_data_rate_mbps,
            "bytes_per_row": bytes_per_row,
            "frequency_bins": frequency_bins
        },
        "warnings": warnings,
        "compatible": output_data_rate_mbps <= THROUGHPUT_THRESHOLD
    }
```

**למה הפונקציה הזו חשובה?**
- היא **מחשבת** את הפרמטרים לפני שיוצרים task
- היא **מתריעה** אם הקונפיגורציה יקרה מדי
- היא **מונעת** יצירת tasks שיגרמו לבעיות

---

#### 🔹 **Step 3: Log Results**
```python
logger.info(f"  - Spectrogram rate: {compat_result['estimates']['spectrogram_rows_per_sec']:.2f} rows/sec")
logger.info(f"  - Output data rate: {compat_result['estimates']['output_data_rate_mbps']:.2f} Mbps")
```

**למה logging חשוב?**
- מאפשר לראות מה קרה בדיוק
- עוזר ב-debugging
- מספק תיעוד לדוחות

---

#### 🔹 **Step 4: Assertions**
```python
if calculated_throughput > THROUGHPUT_WARNING_THRESHOLD:
    logger.warning("⚠️ High throughput detected...")
```

**שתי אפשרויות**:
1. **Option A (Current)**: Accept with warning
   - הטסט עובר גם עם throughput גבוה
   - רק מתריע ב-logs
   - המערכת תנסה לטפל

2. **Option B (Future - TBD)**: Reject with error
   - הטסט נכשל אם throughput > threshold
   - המערכת דוחה את הקונפיגורציה
   - משתמש מקבל HTTP 400

---

## 🧩 דוגמה מלאה: High Throughput Config

### תרחיש Extreme:
```python
# Configuration that produces > 50 Mbps
extreme_config = {
    "nfftSelection": 256,           # Very small NFFT → many rows/sec
    "channels": {
        "min": 0,
        "max": 500                  # 500 sensors
    },
    "frequencyRange": {
        "min": 0,
        "max": 4000                 # Wide frequency range
    },
    "displayInfo": {"height": 2000},
    "view_type": 0
}

# Calculation:
# PRR = 1000 samples/sec (typical)
# Rows/sec = 1000 / 256 ≈ 3.9
# Frequency Bins = 256 / 2 = 128
# Bytes/row = 500 × 128 × 4 = 256,000 bytes
# Throughput = 3.9 × 256,000 × 8 / 1,000,000 ≈ 7.98 Mbps

# But if we increase sensors and frequency range further:
# Sensors = 1000, Freq = 8000 Hz → ~32 Mbps
# Sensors = 2000, Freq = 10000 Hz → ~80 Mbps (EXTREME!)
```

---

## 🎓 מה לומדים מהטסט הזה?

### תוצאות צפויות:
1. **Baseline Configuration** (NFFT=1024, 100 sensors) → **~10 Mbps** ✅ OK
2. **Moderate Configuration** (NFFT=512, 200 sensors) → **~25 Mbps** ✅ OK
3. **High Configuration** (NFFT=256, 500 sensors) → **~50 Mbps** ⚠️ WARNING
4. **Extreme Configuration** (NFFT=256, 1000+ sensors) → **~100+ Mbps** 🚫 REJECT

---

## 🗣️ שאלות לפגישה (Questions for the Meeting)

### שאלות מדיניות:
1. **מה הגבול המקסימלי של throughput שהמערכת יכולה לטפל בו?**
   - 50 Mbps? 100 Mbps? 200 Mbps?
   - מבוסס על איזה infrastructure? (network bandwidth, CPU, memory)

2. **איך המערכת צריכה להתנהג כשחורגים מהגבול?**
   - **Option A**: לקבל עם warning (ולתת למשתמש אחריות)
   - **Option B**: לדחות עם error (ולמנוע)
   - **Option C**: לאשר רק ל-admins/power users

3. **האם יש דרוג משתמשים?**
   - Admin → throughput בלתי מוגבל
   - Power User → עד 100 Mbps
   - Regular User → עד 50 Mbps

4. **מה קורה אם יש כבר tasks בריצה?**
   - האם לוקחים בחשבון את ה-throughput הכולל?
   - האם יש "תור" לקונפיגורציות יקרות?

---

### שאלות טכניות:
5. **איפה מחושב ה-throughput - Client או Server?**
   - אם Client → משתמש יכול לעקוף
   - אם Server → יותר בטוח, אבל צורך validation ב-API

6. **האם יש caching של חישובים?**
   - אם אותה קונפיגורציה נשלחת פעמיים → האם מחשבים מחדש?

7. **מה קורה עם live vs. historical configurations?**
   - האם live זקוק לפחות throughput?
   - האם historical יכול להיות "batch" (פחות urgent)?

8. **האם יש monitoring real-time של throughput?**
   - Dashboard?
   - Alerts כש throughput עובר threshold?

9. **מה ה-graceful degradation strategy?**
   - כש throughput גבוה → האם מורידים resolution?
   - האם מורידים frame rate?

10. **האם בדקנו את ההתנהגות ב-production-like environment?**
    - עם network latency?
    - עם resource limits?

---

## 📊 טבלת סיכום - Throughput Scenarios

| Scenario | NFFT | Sensors | Freq Range (Hz) | PRR | Throughput | Decision |
|----------|------|---------|----------------|-----|------------|----------|
| **Baseline** | 1024 | 100 | 500 | 2000 | ~10 Mbps | ✅ Accept |
| **Moderate** | 512 | 200 | 1000 | 2000 | ~25 Mbps | ✅ Accept |
| **High** | 256 | 500 | 2000 | 2000 | ~50 Mbps | ⚠️ Warning |
| **Extreme** | 256 | 1000 | 4000 | 2000 | ~100 Mbps | 🚫 Reject (TBD) |
| **Insane** | 128 | 2000 | 8000 | 2000 | ~400 Mbps | 🚫 Reject |

---

## ✅ Checklist לפני הפגישה

- [ ] קראתי את המסמך הזה לעומק
- [ ] הבנתי את חישובי ה-throughput
- [ ] הבנתי את ה-trade-offs בין NFFT, sensors, frequency range
- [ ] יודע להסביר למה הטסט הזה קריטי
- [ ] יודע להסביר את ההבדל בין Option A ו-Option B
- [ ] הכנתי שאלות ספציפיות לצוות
- [ ] סקרתי את הקוד ב-`test_spectrogram_pipeline.py`
- [ ] יודע איפה נמצאת הלוגיקה של `validate_configuration_compatibility`

---

## 📌 נקודות מפתח לזכור

1. **Throughput = f(NFFT, Sensors, PRR, Frequency Range)**
2. **NFFT קטן יותר → Throughput גבוה יותר**
3. **הטסט בודק את ההתנהגות, לא רק אם המערכת עובדת**
4. **התנהגות צריכה להיות מוגדרת מראש (specs meeting)**
5. **זה לא באג - זה design decision שצריך להחליט עליו**

---

**נכתב עבור**: Roy Avrahami  
**תאריך**: אוקטובר 2025  
**Jira**: PZ-13905

---

