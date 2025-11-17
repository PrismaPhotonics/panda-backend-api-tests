# 📍 מיקומי קוד מדויקים למצגת
## 9 דוגמאות - מוכן לפתיחה ב-IDE

**הוראות:** Ctrl+P בCursor, הדבק את השורה, Enter

---

## 🔴 **Priority 0 - קריטי**

### **1️⃣ ROI Change Limit - 50% Hardcoded**
```
src/utils/validators.py:395
```
**לפתיחה מהירה:** 
- לחץ Ctrl+P
- הדבק: `src/utils/validators.py:395`
- Enter

**מה להראות:**
```python
Line 395:
    max_change_percent: float = 50.0  # ❌ HARDCODED - NO SPEC!
```

**הודעה למשתתפים:**
"רואים שורה 395? 50% hardcoded. אף אחד לא אישר את זה!"

---

### **2️⃣ Performance Assertions Disabled (P95/P99)**
```
tests/integration/performance/test_performance_high_priority.py:146
```
**לפתיחה מהירה:** 
- Ctrl+P
- הדבק: `tests/integration/performance/test_performance_high_priority.py:146`

**מה להראות - שורה 146:**
```python
# TODO: Update thresholds after specs meeting
THRESHOLD_P95_MS = 500   # ❌ Arbitrary
THRESHOLD_P99_MS = 1000  # ❌ Arbitrary
```

**מה להראות - שורות 157-162:**
```python
# TODO: Uncomment after specs meeting
# assert p95 < THRESHOLD_P95_MS   ❌ DISABLED!
# assert p99 < THRESHOLD_P99_MS   ❌ DISABLED!
```

**הודעה למשתתפים:**
"28 performance tests עם assertions מושבתות. הם רצים אבל לא יכולים לכשל!"

---

## 🟠 **Priority 1 - גבוה**

### **3️⃣ NFFT Validation Too Permissive**
```
src/utils/validators.py:194
```
**לפתיחה:** Ctrl+P → `src/utils/validators.py:194`

**מה להראות - שורה 219:**
```python
if not is_power_of_2:
    warnings.warn(...)  # ❌ Only warns, doesn't reject!

return True  # ✅ Always returns True!
```

**הודעה:**
"הקוד רק מזהיר, אף פעם לא דוחה. מקבל כל ערך חיובי!"

---

### **4️⃣ Frequency Range - No Maximum**
```
src/models/focus_server_models.py:46
```
**לפתיחה:** Ctrl+P → `src/models/focus_server_models.py:46`

**מה להראות - שורות 48-49:**
```python
class FrequencyRange(BaseModel):
    min: int = Field(..., ge=0)  # ✅ >= 0
    max: int = Field(..., ge=0)  # ✅ >= 0
    # ❌ NO UPPER LIMIT!
```

**הודעה:**
"רואים? אין גבול עליון. יכול לשלוח 999999 - ויעבור!"

---

## 🟡 **Priority 2 - בינוני**

### **5️⃣ Sensor Range - No Min/Max ROI Size**
```
src/utils/validators.py:116
```
**לפתיחה:** Ctrl+P → `src/utils/validators.py:116`

**מה להראות - שורות 137-148:**
```python
if max_sensor <= min_sensor:
    raise ValidationError("max > min")

if max_sensor >= total_sensors:
    raise ValidationError("Exceeds total")

# ❌ NO CHECK FOR MINIMUM ROI SIZE!
# ❌ NO CHECK FOR MAXIMUM ROI SIZE!
```

**הודעה:**
"יכול להיות ROI עם סנסור אחד בלבד. או עם כל 2222 הסנסורים. אין גבולות!"

---

### **6️⃣ Polling Helper - Hardcoded Timeouts**
```
src/utils/helpers.py:474
```
**לפתיחה:** Ctrl+P → `src/utils/helpers.py:474`

**מה להראות - שורה 474:**
```python
def poll_until(
    condition_func,
    timeout_seconds: int = 60,      # ❌ Hardcoded
    poll_interval: float = 1.0      # ❌ Hardcoded
):
```

**הודעה:**
"60 שניות timeout, 1 שנייה interval. אותם ערכים ל-live וגם ל-historic!"

---

### **7️⃣ Default Payloads Mismatch Config**
```
src/utils/helpers.py:507
```
**לפתיחה:** Ctrl+P → `src/utils/helpers.py:507`

**מה להראות - שורות 508-513:**
```python
def generate_config_payload(
    sensors_min: int = 0,          # ❌ Config: 11
    sensors_max: int = 100,        # ❌ Config: 109
    freq_max: int = 500,           # ❌ Config: 1000
    canvas_height: int = 1000,     # ❌ No spec
):
```

**גם הראה את config/environments.yaml שורות 24-26:**
```yaml
constraints:
  sensors:
    default_start: 11     # ≠ Code: 0
    default_end: 109      # ≠ Code: 100
```

**הודעה:**
"קוד אומר 0-100, config אומר 11-109. מי צודק?!"

---

## ⚪ **Priority 3 - נמוך**

### **8️⃣ Config Validation Tests - No Assertions**
```
tests/integration/api/test_config_validation_high_priority.py:475
```
**לפתיחה:** Ctrl+P → `tests/integration/api/test_config_validation_high_priority.py:475`

**מה להראות - שורה 481:**
```python
# TODO: Update assertion after specs meeting
# For now, just log  ❌ NO ASSERTION!
logger.info(f"Frequency range min==max: status_code={response.status_code}")
```

**גם שורה 517:**
```python
# TODO: Update assertion after specs meeting  ❌ NO ASSERTION!
```

**הודעה:**
"הטסטים רצים, אבל לא בודקים כלום. רק כותבים ל-log!"

---

### **9️⃣ MongoDB Outage Resilience - Behavior Unclear**
```
tests/integration/performance/test_mongodb_outage_resilience.py:1
```
**לפתיחה:** Ctrl+P → `tests/integration/performance/test_mongodb_outage_resilience.py`

**מה להראות - הטסט שנכשל:**
```
FAILED: test_mongodb_scale_down_outage_returns_503
AssertionError: Response time 15.423s exceeds maximum 5.0s
```

**הודעה:**
"הטסט מצפה ל-5 שניות, בפועל לוקח 15. האם 5s נכון? 15s? אף אחד לא יודע!"

---

## 📋 **Quick Copy List - לפתיחה מהירה**

```
src/utils/validators.py:395
tests/integration/performance/test_performance_high_priority.py:146
src/utils/validators.py:194
src/models/focus_server_models.py:46
src/utils/validators.py:116
src/utils/helpers.py:474
src/utils/helpers.py:507
tests/integration/api/test_config_validation_high_priority.py:475
tests/integration/performance/test_mongodb_outage_resilience.py
```

**איך להשתמש:**
1. העתק שורה
2. Ctrl+P ב-Cursor
3. Ctrl+V להדבקה
4. Enter

---

## 🎤 **תסריט למצגת - סדר מומלץ**

### **התחלה חזקה (5 דקות):**
1. ✅ פתח #2 - Performance Assertions Disabled
   - "28 טסטים לא יכולים לכשל!"
   - הראה את ה-TODO comments
   - הראה assertions מושבתות

2. ✅ פתח #1 - ROI 50% Hardcoded
   - "50% - מאיפה זה בא?"
   - "אף אחד לא אישר"

### **המשך עם דוגמאות (5 דקות):**
3. ✅ פתח #3 - NFFT
   - "רואים? רק warning, אף פעם לא reject"

4. ✅ פתח #4 - Frequency
   - "אין מקסימום. יכול לשלוח מיליון!"

5. ✅ פתח #7 - Mismatch
   - "קוד וconfig לא מסונכרנים!"

### **סיום (2 דקות):**
6. ✅ הראה את הטבלה
   - "9 דוגמאות, 82 טסטים מושפעים"
   - "בואו נפתור את זה היום"

---

## 💡 **טיפים למצגת:**

### **לפני:**
- [ ] פתח את כל 9 הקבצים בטאבים נפרדים
- [ ] סמן את השורות הקריטיות
- [ ] תרגל את המעבר בין הטאבים

### **במהלך:**
- [ ] הגדל את הגופן (Ctrl + +)
- [ ] השתמש ב-highlight לשורות חשובות
- [ ] עבור לאט - תן למשתתפים לקרוא

### **אחרי:**
- [ ] שלח את המסמך הזה למשתתפים
- [ ] הם יכולים לפתוח את הקוד בעצמם

---

## ✅ **Ready to Present!**

**יש לך:**
- ✅ 9 מיקומים מדויקים
- ✅ מה להראות בכל אחד
- ✅ מה להגיד
- ✅ סדר מומלץ

**בהצלחה במצגת!** 🚀

