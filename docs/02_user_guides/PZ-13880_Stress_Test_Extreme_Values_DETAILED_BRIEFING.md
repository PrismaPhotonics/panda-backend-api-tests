# מסמך הכנה מקיף לפגישה: PZ-13880 - Stress Test - Configuration with Extreme Values

## 📋 פרטי הטסט

| פרמטר | ערך |
|-------|-----|
| **מזהה Jira** | PZ-13880 |
| **שם הטסט** | Stress - Configuration with Extreme Values |
| **סטטוס** | TO DO (לא מומש עדיין) |
| **עדיפות** | Medium |
| **תוויות** | `stress_test_panda`, `config-validation`, `stress-test`, `extreme-values`, `robustness` |
| **קטגוריה** | Integration Test (Stress) |
| **API נבדק** | POST /configure (Old API) |

---

## 🎯 PART 1: מה המטרה של הטסט?

### מטרה ראשית
**לבדוק את החוסן (Robustness) והיציבות של Focus Server כאשר הוא מקבל ערכי קונפיגורציה קיצוניים אך טכנית תקינים.**

### מטרות משניות (Sub-goals)

#### 1.1 וידוא יציבות המערכת תחת עומס חישובי
- **למה זה חשוב?** כאשר מבקשים NFFT גבוה מאוד (8192) או טווח ערוצים רחב (0-200), השרת צריך לבצע חישובים כבדים מאוד.
- **מה רוצים לוודא?** שהשרת לא יקרוס (crash), לא יקפיא (freeze), ולא יכשל באופן לא מבוקר.
- **התנהגות נכונה:**
  - **אופציה A**: השרת מקבל את הבקשה ומעבד אותה (אף שזה עלול לקחת זמן)
  - **אופציה B**: השרת דוחה את הבקשה עם הודעה ברורה: "Configuration exceeds system limits"

#### 1.2 בדיקת ניהול זיכרון (Memory Management)
- **למה זה חשוב?** ערכים קיצוניים כמו:
  - `height=5000` (גובה canvas גבוה מאוד)
  - `channels: 0-200` (200 ערוצים)
  - `nfft=8192` (חלונות FFT גדולים מאוד)
  
  כל אלה יוצרים מטריצות נתונים ענקיות בזיכרון.

- **מה רוצים לוודא?** 
  - השרת לא סובל מ-Memory Leak
  - השרת לא נכנס ל-Out of Memory (OOM)
  - השרת לא גורם למערכת ההפעלה להתקע
  - אם הזיכרון אוזל - השרת מתנהג בצורה מבוקרת (graceful degradation)

#### 1.3 בדיקת Response Time תחת עומס
- **למה זה חשוב?** גם אם המערכת לא קורסת, זמני תגובה ארוכים מדי יפגעו בחוויית המשתמש.
- **מה רוצים לוודא?**
  - השרת מגיב בזמן סביר (אפילו אם זה 10-20 שניות)
  - השרת לא "תקוע" ללא סוף (infinite hang)
  - המערכת מחזירה מענה (אפילו שגיאה) ולא משאירה את הלקוח ללא תשובה

#### 1.4 בדיקת Error Handling נכון
- **למה זה חשוב?** אם השרת לא יכול לטפל בבקשה, הוא צריך להגיד זאת בצורה ברורה.
- **מה רוצים לוודא?**
  - אם השרת דוחה את הבקשה → HTTP 400 Bad Request עם הודעה מפורשת
  - אם השרת מקבל את הבקשה → HTTP 200 OK + job_id
  - **לא** HTTP 500 Internal Server Error (שמעיד על קריסה לא מבוקרת)

---

## 🔬 PART 2: מה אני רוצה לבדוק? (What Am I Testing?)

### 2.1 התנהגות המערכת עם ערכים קיצוניים

הטסט בודק את ההתנהגות של Focus Server כאשר מקבל קונפיגורציה עם הפרמטרים הבאים:

```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 8192,        ← קיצוני: NFFT גבוה מאוד
  "displayInfo": {
    "height": 5000              ← קיצוני: גובה canvas גדול מאוד
  },
  "channels": {
    "min": 0,
    "max": 200                  ← קיצוני: 200 ערוצים
  },
  "frequencyRange": {
    "min": 0,
    "max": 2000                 ← קיצוני: טווח תדרים רחב מאוד
  },
  "start_time": null,
  "end_time": null,
  "view_type": 0                ← MULTICHANNEL
}
```

### 2.2 למה הערכים האלה קיצוניים?

#### NFFT = 8192
- **ערך נורמלי**: 256, 512, 1024, 2048
- **ערך בטסט**: 8192 (פי 4 מהמקסימום המומלץ!)
- **השפעה**:
  - חישובי FFT ארוכים מאוד (computational complexity = O(N log N))
  - צריכת זיכרון אדירה (כל חלון FFT = 8192 samples × 8 bytes = 64KB)
  - אם יש 200 ערוצים → 200 × 64KB = 12.8MB **לכל מסגרת זמן בודדת**

#### Height = 5000
- **ערך נורמלי**: 800-1500 pixels
- **ערך בטסט**: 5000 pixels
- **השפעה**:
  - מטריצת pixels ענקית (5000 rows × frequency bins)
  - אם frequency bins = 4096 → 5000 × 4096 × 4 bytes = ~82MB למסך אחד!
  - עומס על GPU/rendering engine

#### Channels: 0-200
- **ערך נורמלי**: 1-50 ערוצים
- **ערך בטסט**: 200 ערוצים
- **השפעה**:
  - 200 ערוצים × NFFT 8192 × 4 bytes = 6.5MB **לכל מסגרת**
  - עיבוד מקבילי של 200 signals
  - עומס רב על CPU cores

#### Frequency Range: 0-2000 Hz
- **ערך נורמלי**: 0-500 Hz
- **ערך בטסט**: 0-2000 Hz (פי 4!)
- **השפעה**:
  - resolution bins גבוה יותר
  - יותר נתונים לעבד ולהחזיר
  - עומס על network bandwidth

### 2.3 מה הטסט בודק בפועל? (Test Flow)

```
┌─────────────────────────────────────────────────────┐
│  STEP 1: Create Configuration with Extreme Values  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  STEP 2: Send POST /configure                      │
│  → Measure: Does Pydantic validation pass?         │
└─────────────────────────────────────────────────────┘
                        ↓
          ┌─────────────┴──────────────┐
          ↓                            ↓
  ┌───────────────┐          ┌─────────────────┐
  │  Server ACCEPTS│          │ Server REJECTS  │
  │  (Status 200)  │          │ (Status 400)    │
  └───────────────┘          └─────────────────┘
          ↓                            ↓
┌─────────────────────────────────────────────────────┐
│  STEP 3: If Accepted → Poll GET /waterfall         │
│  → Measure: Response time, server stability         │
└─────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────┐
│  STEP 4: Check for Server Errors/Crashes           │
│  → Measure: Server logs, process health             │
└─────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────┐
│  STEP 5: Verify Response Validity                  │
│  → Either: Data returned OR graceful error          │
└─────────────────────────────────────────────────────┘
```

### 2.4 Assertions (מה מאמתים?)

הטסט מאמת את הדברים הבאים:

#### ✅ Assertion 1: Pydantic Validation
```python
# Verify that ConfigTaskRequest can be created with extreme values
config_request = ConfigTaskRequest(**config_payload)
# → Should NOT raise ValidationError (values are valid, just extreme)
```

#### ✅ Assertion 2: Server Response
```python
response = focus_server_api.config_task(task_id, config_request)

# Option A: Server accepts the configuration
assert response.status == "Config received successfully"
# OR
# Option B: Server rejects with clear reason
assert "limit" in error_message.lower() or "exceed" in error_message.lower()
```

#### ✅ Assertion 3: Server Stability
```python
# Try to poll data after configuration
waterfall_response = focus_server_api.get_waterfall(task_id, 5)
assert waterfall_response.status_code in [200, 201, 208], \
    "Server should return valid status code"
# → Server should NOT crash or hang indefinitely
```

#### ✅ Assertion 4: No Uncontrolled Errors
```python
# If server fails, it should fail gracefully
# NOT: HTTP 500 Internal Server Error
# NOT: Connection timeout
# NOT: Process crash
```

---

## 🛡️ PART 3: מה הנחיצות של הטסט? (Why Is This Critical?)

### 3.1 מניעת קריסות בייצור (Production Crashes)

**תרחיש אמיתי:**
- משתמש מבקש לצפות ב-150 ערוצים בו-זמנית
- משתמש מגדיר גובה מסך של 4000 pixels (מסך 4K)
- משתמש מגדיר NFFT=8192 לקבלת רזולוציה גבוהה

**מה קורה אם הטסט לא קיים?**
- השרת עלול לקרוס באמצע עבודה
- כל המשתמשים האחרים מושפעים
- אובדן נתונים (data loss)
- downtime של כל המערכת

**מה הטסט מונע?**
- זיהוי מוקדם של בעיות בניהול משאבים
- הבנה של גבולות המערכת (system limits)
- אפשרות להוסיף validations מניעתיות

### 3.2 שיפור חוויית משתמש (UX)

**ללא הטסט:**
- משתמש מבקש קונפיגורציה קיצונית
- השרת מקבל אבל לא מגיב
- משתמש מחכה 5 דקות...10 דקות...
- לבסוף: timeout או קריסה

**עם הטסט:**
- השרת יודע מראש מה הגבולות שלו
- אם קונפיגורציה חורגת → דחייה מיידית עם הסבר
- משתמש מקבל feedback ברור: "Requested configuration exceeds maximum of X channels"
- משתמש יכול להתאים את הבקשה

### 3.3 אבטחה (Security)

**תרחיש תקיפה:**
- תוקף יכול לנסות לגרום ל-Denial of Service (DoS)
- תוקף שולח בקשות עם ערכים קיצוניים:
  ```json
  {
    "channels": {"min": 0, "max": 10000},
    "nfftSelection": 32768,
    "displayInfo": {"height": 50000}
  }
  ```
- מטרה: לגרום לשרת לצרוך את כל הזיכרון/CPU ולקרוס

**מה הטסט מונע?**
- זיהוי של פרצות אבטחה לפני שתוקפים מנצלים אותן
- הוספת rate limiting ו-validation rules
- הגנה על זמינות המערכת (availability)

### 3.4 תכנון קיבולת (Capacity Planning)

**השאלות שהטסט עונה עליהן:**
1. **מה המקסימום שהשרת יכול לטפל?**
   - כמה ערוצים בו-זמנית?
   - איזה NFFT מקסימלי?
   - איזה resolution מסך?

2. **מתי צריך scale-up?**
   - אם יש 10 משתמשים עם קונפיגורציות קיצוניות → צריך עוד RAM?
   - האם צריך לשדרג את השרת?

3. **האם צריך להוסיף limits?**
   - האם לקבוע מקסימום של 100 ערוצים?
   - האם לקבוע מקסימום NFFT של 4096?

### 3.5 ציות לדרישות (Requirement Compliance)

**דרישה מהמפרט:**
> "Focus Server must handle configuration requests with extreme (but technically valid) parameter values without crashes or errors, demonstrating robustness under stress conditions."

**למה זה חשוב?**
- חלק מדרישות הפרויקט
- נדרש לעמוד בתקני איכות
- חשוב לאישור לקוח (acceptance criteria)

---

## 💻 PART 4: איך ממשים את הטסט בקוד? (Implementation Strategy)

### 4.1 ארכיטקטורת הטסט

הטסט יממש בתבנית הבאה:

```
tests/integration/api/test_config_validation_stress.py
├── TestClass: TestStressConfigurationExtremeValues
│   ├── test_extreme_nfft_8192
│   ├── test_extreme_canvas_height_5000
│   ├── test_extreme_channel_count_200
│   ├── test_extreme_frequency_range_2000
│   └── test_combined_extreme_values (זה הטסט PZ-13880)
```

### 4.2 מבנה הטסט (Test Structure)

```python
@pytest.mark.integration
@pytest.mark.stress
@pytest.mark.medium_priority
class TestStressConfigurationExtremeValues:
    """
    Stress tests for configuration with extreme values.
    
    Objective:
        Verify that Focus Server can handle extreme (but valid) 
        configuration values without crashes or uncontrolled errors.
    
    Jira: PZ-13880
    """
    
    def test_configuration_with_extreme_values(
        self, 
        focus_server_api,
        logger
    ):
        """
        Test PZ-13880: Configuration with all extreme values.
        """
        pass  # Implementation below
```

### 4.3 שלבי המימוש (Implementation Steps)

#### שלב 1: הכנת Configuration Payload

```python
# Generate unique task ID
task_id = generate_task_id("extreme_values")
logger.info(f"Testing extreme values configuration: {task_id}")

# Create configuration with extreme values
config_payload = {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 8192,              # ← Extreme
    "displayInfo": {"height": 5000},    # ← Extreme
    "channels": {"min": 0, "max": 200}, # ← Extreme
    "frequencyRange": {"min": 0, "max": 2000},  # ← Extreme
    "start_time": None,
    "end_time": None,
    "view_type": ViewType.MULTICHANNEL
}
```

**למה ככה?**
- `generate_task_id()` יוצר מזהה ייחודי לכל ריצה (למנוע collisions)
- הערכים הקיצוניים מוגדרים מפורשות (לא משתנים randomly)
- `logger.info()` מתעד את הריצה ל-debugging

#### שלב 2: ניסיון ליצור ConfigTaskRequest

```python
try:
    # Attempt to create Pydantic model
    config_request = ConfigTaskRequest(**config_payload)
    logger.info("✅ Pydantic validation passed for extreme values")
    
except ValidationError as e:
    # If Pydantic rejects, test should fail
    logger.error(f"❌ Pydantic rejected extreme values: {e}")
    pytest.fail("Extreme values should be technically valid")
```

**למה ככה?**
- Pydantic validation צריכה לעבור (הערכים תקינים, רק קיצוניים)
- אם Pydantic דוחה → זו בעיה בהגדרת המודל
- אם Pydantic מקבל → ממשיכים לשרת

#### שלב 3: שליחת הבקשה לשרת

```python
# Send configuration to server
response = focus_server_api.config_task(task_id, config_request)
```

**מה קורה כאן?**
- `focus_server_api.config_task()` שולח POST /config/{task_id}
- פנימית: מבצע JSON serialization ושולח HTTP request
- מחזיר `ConfigTaskResponse` אם הצלחה, או זורק `APIError` אם כשלון

#### שלב 4: טיפול בתשובות אפשריות

```python
# Scenario A: Server accepts the configuration
if hasattr(response, 'status') and response.status:
    assert response.status == "Config received successfully"
    logger.info("✅ Server accepted extreme values configuration")
    
    # Wait for processing to start
    time.sleep(2.0)
    
    # Try to poll data
    waterfall_response = focus_server_api.get_waterfall(task_id, 5)
    
    # Verify server stability
    assert waterfall_response.status_code in [200, 201, 208], \
        f"Server returned unexpected status: {waterfall_response.status_code}"
    
    logger.info("✅ Server stable after accepting extreme values")
```

**למה ככה?**
- בודקים אם השרת הצליח לקבל את הקונפיגורציה
- ממתינים 2 שניות (זמן סביר להתחלת עיבוד)
- מנסים לקבל נתונים (polling)
- מוודאים שהשרת לא קרס (status codes תקינים)

#### שלב 5: טיפול בדחייה מבוקרת

```python
except APIError as e:
    # Scenario B: Server rejects with validation error
    error_message = str(e).lower()
    
    if any(keyword in error_message for keyword in 
           ["limit", "exceed", "too large", "maximum"]):
        logger.info(f"✅ Server rejected extreme values with clear reason: {e}")
        # This is acceptable behavior
        
    else:
        # Server failed for wrong reason
        logger.error(f"❌ Server failed with unexpected error: {e}")
        raise
```

**למה ככה?**
- אם השרת דוחה, צריך לבדוק **למה** הוא דוחה
- דחייה עם הסבר ברור (limit/exceed) → OK ✅
- דחייה עם שגיאה לא ברורה (500 Internal Error) → NOT OK ❌

#### שלב 6: טיפול בשגיאות לא צפויות

```python
except Exception as e:
    # Unexpected error (crash, timeout, etc.)
    logger.error(f"❌ Unexpected error during extreme values test: {e}")
    logger.error(f"Error type: {type(e).__name__}")
    raise
```

**למה ככה?**
- כל exception אחר = בעיה חמורה
- יכול להיות: Timeout, ConnectionError, MemoryError
- צריך לתעד ולזרוק מחדש (raise) כדי שהטסט ייכשל

### 4.4 Monitoring ו-Metrics

בנוסף לטסט הבסיסי, כדאי לאסוף מטריקות:

```python
import time
import psutil  # for system monitoring

# Measure response time
start_time = time.time()
response = focus_server_api.config_task(task_id, config_request)
response_time = time.time() - start_time

logger.info(f"⏱️  Server response time: {response_time:.2f} seconds")

# Check if response time is reasonable
if response_time > 30:
    logger.warning(f"⚠️  Response time is very high: {response_time:.2f}s")

# Monitor system resources (optional, advanced)
memory_usage = psutil.virtual_memory().percent
cpu_usage = psutil.cpu_percent(interval=1)

logger.info(f"📊 System resources: CPU={cpu_usage}%, Memory={memory_usage}%")
```

### 4.5 Cleanup (ניקיון)

```python
# Cleanup: Cancel job if it was created
if hasattr(response, 'job_id') and response.job_id:
    try:
        focus_server_api.cancel_job(response.job_id)
        logger.info(f"🧹 Cleaned up job: {response.job_id}")
    except Exception as cleanup_error:
        logger.warning(f"Failed to cleanup job: {cleanup_error}")
```

**למה ככה?**
- אם נוצר job, צריך למחוק אותו (לא להשאיר "זבל" במערכת)
- אם cleanup נכשל → רק warning, לא להפיל את הטסט

---

## 🎓 PART 5: שאלות ותשובות נפוצות לפגישה

### Q1: למה הטסט הזה בעדיפות Medium ולא High?

**תשובה:**
- High Priority = פונקציונליות בסיסית שבלעדיה המערכת לא עובדת
- Medium Priority = בדיקות robustness שחשובות אבל לא קריטיות ליום-יום
- הטסט הזה בודק edge cases קיצוניים, לא פונקציונליות יום-יומית
- אבל עדיין חשוב מאוד למניעת קריסות בייצור

### Q2: מה אם השרת דוחה את הקונפיגורציה?

**תשובה:**
- **זו התנהגות תקינה!**
- השרת יכול להחליט שהערכים חורגים מהגבולות שלו
- החשוב: שהדחייה תהיה **מבוקרת** (HTTP 400) ולא **קריסה** (HTTP 500)
- החשוב: שתהיה **הודעת שגיאה ברורה** ("Exceeds maximum 100 channels")

### Q3: האם צריך לבדוק כל ערך קיצוני בנפרד?

**תשובה:**
- **כן!** בנוסף לטסט המשולב (PZ-13880), צריך טסטים נפרדים:
  - `test_extreme_nfft_only` - רק NFFT=8192, שאר הערכים נורמליים
  - `test_extreme_channels_only` - רק 200 ערוצים, שאר הערכים נורמליים
  - `test_extreme_height_only` - רק height=5000, שאר הערכים נורמליים
  
- למה? כדי **לבודד** את הבעיה: אם הטסט המשולב נכשל, קשה לדעת איזה פרמטר גרם לכשלון

### Q4: מה קורה אם הטסט נכשל?

**תשובה - תרחישים אפשריים:**

| תרחיש | סיבה אפשרית | פתרון |
|-------|------------|-------|
| Server returns 500 | קריסה פנימית | צריך לתקן error handling בשרת |
| Timeout | עיבוד אינסופי | צריך להוסיף timeout mechanisms |
| MemoryError | זיכרון אזל | צריך להוסיף memory limits או validation |
| Connection reset | שרת קרס | בעיה קריטית, צריך לחקור logs |
| Pydantic ValidationError | מודל לא מאפשר ערכים אלה | צריך לעדכן את המודל |

### Q5: האם הטסט הזה מוריד את השרת?

**תשובה:**
- **לא צריך!** זו בדיוק המטרה של הטסט - לוודא שהשרת **לא** קורס
- אם הטסט כן מוריד את השרת → זו **בעיה קריטית** שצריך לתקן
- הטסט רץ בסביבת test/staging, לא בייצור

### Q6: כמה זמן הטסט אמור לקחת?

**תשובה:**
- **תרחיש אידיאלי**: 5-10 שניות
  - 1-2 שניות: שליחת הבקשה
  - 2-3 שניות: עיבוד ראשוני
  - 2-5 שניות: polling לבדיקת stability
  
- **תרחיש slow**: 20-30 שניות (עדיין OK)
- **תרחיש בעייתי**: > 60 שניות או timeout

### Q7: מה ההבדל בין הטסט הזה לבין Performance Tests?

**תשובה:**

| Stress Test (PZ-13880) | Performance Test |
|----------------------|------------------|
| בודק **stability** תחת ערכים קיצוניים | בודק **speed** תחת עומס רגיל |
| מטרה: לא לקרוס | מטרה: מהירות |
| ריצה אחת עם ערכים קיצוניים | ריצות מרובות עם ערכים רגילים |
| מחפש: crashes, memory leaks | מחפש: bottlenecks, slow queries |

---

## 📊 PART 6: מטריקות הצלחה (Success Criteria)

הטסט נחשב **מוצלח** אם מתקיימים התנאים הבאים:

### ✅ Criterion 1: No Uncontrolled Failures
```
✓ Server does NOT return HTTP 500 Internal Server Error
✓ Server does NOT crash/exit unexpectedly
✓ No MemoryError or SystemError exceptions
✓ No infinite hangs (timeout protection works)
```

### ✅ Criterion 2: Clear Response
```
✓ EITHER: Configuration accepted (HTTP 200 + job_id)
✓ OR: Configuration rejected with clear reason (HTTP 400 + error message)
```

### ✅ Criterion 3: System Stability
```
✓ Server remains responsive after request
✓ Other concurrent requests are not affected
✓ System resources return to normal after test
```

### ✅ Criterion 4: Proper Logging
```
✓ Server logs show clear processing steps
✓ Any errors are properly logged with context
✓ No silent failures (failures with no logs)
```

---

## 🚀 PART 7: תוכנית מימוש (Implementation Plan)

### שלב 1: כתיבת הטסט (1-2 שעות)
- [ ] יצירת קובץ `test_config_validation_stress.py`
- [ ] כתיבת test class + test function
- [ ] הוספת logging מפורט
- [ ] הוספת assertions

### שלב 2: ריצה ראשונית (30 דקות)
- [ ] הרצת הטסט בסביבת dev
- [ ] בדיקת התנהגות השרת
- [ ] תיעוד התוצאות

### שלב 3: Debug (אם נדרש) (1-3 שעות)
- [ ] אם הטסט נכשל → ניתוח הבעיה
- [ ] בדיקת server logs
- [ ] תיאום עם Backend team לתיקון

### שלב 4: Documentation (30 דקות)
- [ ] עדכון README
- [ ] הוספת הטסט ל-Test Plan
- [ ] קישור ל-Jira PZ-13880

### שלב 5: Integration ל-CI/CD (1 שעה)
- [ ] הוספת הטסט ל-test suite
- [ ] הגדרת timeout (max 60 seconds)
- [ ] הוספה ל-stress test category

---

## 📝 PART 8: סיכום ונקודות מפתח לפגישה

### הנקודות החשובות ביותר להדגיש:

1. **מטרת הטסט**: לוודא שהשרת לא קורס עם ערכים קיצוניים
2. **הנחיצות**: מניעת קריסות בייצור + הגנה מפני DoS
3. **התוצאה המצופה**: דחייה מבוקרת או קבלה יציבה
4. **הסיכון אם לא נבדק**: קריסות בייצור, אובדן נתונים, חוויית משתמש גרועה
5. **המימוש**: טסט integration פשוט עם ערכים מוגדרים מראש

### משפט המפתח:
> "PZ-13880 בודק את החוסן של Focus Server על ידי שליחת קונפיגורציה עם ערכים קיצוניים אך טכנית תקינים (NFFT=8192, 200 ערוצים, height=5000), וודאי שהשרת לא קורס אלא מגיב בצורה מבוקרת - או מקבל את הבקשה ומעבד בהצלחה, או דוחה עם הודעת שגיאה ברורה."

---

## 🔗 PART 9: קישורים ומסמכים רלוונטיים

- **Jira**: PZ-13880
- **Test Plan**: PZ-13756
- **Related Tests**: 
  - PZ-13873: Valid Configuration
  - PZ-13878: Invalid Canvas Info
  - PZ-13877: Invalid Frequency Range
  - PZ-13876: Invalid Channel Range
- **API Documentation**: `documentation/specs/REST_API_Documentation.md`
- **Configuration Model**: `src/models/focus_server_models.py`

---

**מסמך זה הוכן על ידי: QA Automation Architect**  
**תאריך**: 27 אוקטובר 2025  
**גרסה**: 1.0 - Comprehensive Briefing for Meeting  
**סטטוס**: ✅ מוכן לפגישה

