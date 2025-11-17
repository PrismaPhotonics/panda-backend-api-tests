# מסמך טכני לפגישת Specs - Focus Server Automation

**סוג פגישה:** סקירה טכנית - הגדרת ספציפיקציות חסרות  
**משך משוער:** 2-3 שעות  
**משתתפים נדרשים:** ראש פיתוח, מנהל אתר, Product Owner, ראש QA  
**תאריך:** לתיאום  
**סטטוס:** דחוף - חוסם 82+ בדיקות אוטומטיות

---

## מבנה המסמך

1. [מטרת הפגישה והרקע](#מטרת-הפגישה-והרקע)
2. [הבעיה המרכזית](#הבעיה-המרכזית)
3. [7 הנושאים הקריטיים](#7-הנושאים-הקריטיים)
4. [טבלת סיכום](#טבלת-סיכום)
5. [תוכנית פעולה](#תוכנית-פעולה)

---

## מטרת הפגישה והרקע

### מטרת הפגישה

**מה אנחנו רוצים להשיג:**
- קביעת ערכים ספציפיים (thresholds, limits, timeouts) לבדיקות אוטומטיות
- הגדרת התנהגות צפויה במצבי edge cases
- אישור ערכים שכבר קיימים בקוד אבל לא אושרו רשמית

**התוצאה הרצויה:**
- מסמך מוסכם עם כל הערכים והחלטות
- יישום הערכים בקוד תוך 1-2 שבועות
- 82+ בדיקות יוכלו לספק תוצאות משמעותיות (pass/fail)

---

### רקע כללי על מסגרת הבדיקות

#### מה בנינו עד כה:
- **מסגרת אוטומציה מקיפה** ל-Focus Server עם 190+ בדיקות
- **בדיקות ברמות שונות:**
  - Unit Tests - בדיקות יחידה לפונקציות בודדות
  - Integration Tests - בדיקות אינטגרציה בין מרכיבים
  - Performance Tests - בדיקות ביצועים
  - Infrastructure Tests - בדיקות תשתית (MongoDB, RabbitMQ, K8s)

#### איך הבדיקות עובדות:
```python
# דוגמה לבדיקה טיפוסית:
def test_api_performance():
    # שלב 1: הרצת הפעולה
    start_time = time.time()
    response = focus_server.post_config(payload)
    duration = time.time() - start_time
    
    # שלב 2: בדיקת תוצאה
    assert response.status_code == 200  # ✅ יש spec - 200 = הצלחה
    
    # שלב 3: בדיקת ביצועים
    THRESHOLD_MS = 500  # ❌ אין spec - מה הערך הנכון?
    assert duration < THRESHOLD_MS  # ⚠️ לא יכול לרוץ ללא spec!
```

---

## הבעיה המרכזית

### המצב הנוכחי:

**במספרים:**
- **190+ בדיקות** קיימות במסגרת
- **82+ בדיקות** מושפעות ישירות מחוסר specs
- **28 בדיקות ביצועים** עם assertions מושבתים
- **50+ ערכים hardcoded** שמעולם לא אושרו על ידי הצוות

**מה זה אומר בפועל:**
```python
# בדיקה שרצה אבל לא עושה כלום:
def test_p95_latency():
    p95 = measure_latency()  # ✅ עובד - אוספים נתונים
    
    # TODO: Uncomment after specs meeting
    # assert p95 < THRESHOLD  # ❌ מושבת! לא יודעים מה ה-threshold
    
    # במקום זה:
    logger.warning(f"P95 = {p95}ms")  # רק מדפיס, לא בודק!
```

---

### ההשפעה על איכות המוצר:

#### 1. **לא יכולים לזהות ירידה בביצועים**
```
תרחיש:
- השבוע: API עונה ב-300ms ממוצע
- בשבוע הבא: API עונה ב-5000ms ממוצע (איטי פי-16!)
- הבדיקה: עוברת! (כי אין threshold)
- התוצאה: משתמשים יראו איטיות, אבל לא תפסנו זאת בזמן
```

#### 2. **False Positives - בזבוז זמן**
```
תרחיש:
- בדיקה נכשלת: "ROI change 60% exceeds limit of 50%"
- הצוות בודק: זה שימוש לגיטימי!
- הבעיה: ה-50% הוא ניחוש, לא דרישה אמיתית
- התוצאה: בזבזנו 2 שעות על false alarm
```

#### 3. **False Negatives - מפספסים באגים**
```
תרחיש:
- משתמש מבקש frequency range: [0, 999999 Hz]
- הקוד: מקבל! (אין maximum)
- המערכת: קורסת (out of memory)
- הבדיקה: עברה! (כי לא בדקנו extreme values)
- התוצאה: באג בייצור שהיה ניתן למניעה
```

#### 4. **לא יכולים לאכוף SLA**
```
תרחיש:
- SLA מוסכם עם לקוח: "API תענה תוך 1 שנייה"
- הבדיקה שלנו: בודקת... כלום! (אין threshold)
- במציאות: API עונה ב-3 שניות
- התוצאה: הפרת SLA שלא זיהינו
```

---

### למה זה קרה?

**סיבות לגיטימיות:**
1. **פיתוח מהיר** - התמקדנו בפונקציונליות, לא בתיעוד specs
2. **שינויים בדרישות** - מה שהיה נכון לפני חצי שנה השתנה
3. **ידע מפוזר** - מי שיודע את הערכים לא תיעד אותם

**אבל עכשיו:**
- המערכת בשלה ויציבה
- יש לנו אוטומציה מקיפה
- **הגיע הזמן לתעדף נכון ולקבוע specs פורמליים**

---

## 7 הנושאים הקריטיים

---

## נושא #1: בדיקות ביצועים ללא Thresholds

### מהות הבדיקות

**מה אנחנו בודקים:**
- זמני תגובה (latency) של API endpoints
- P95 latency: 95% מהבקשות מתחת לסף מסוים
- P99 latency: 99% מהבקשות מתחת לסף מסוים
- אחוז שגיאות (error rate)

**איך הבדיקה עובדת:**
```python
def test_p95_p99_latency():
    """בודק שזמני התגובה של POST /config עומדים ב-SLA"""
    
    # שלב 1: ריצת 100 בקשות
    latencies = []
    errors = 0
    for i in range(100):
        start = time.time()
        response = api.post_config(test_payload)
        duration = (time.time() - start) * 1000  # המרה ל-ms
        
        if response.status_code != 200:
            errors += 1
        else:
            latencies.append(duration)
    
    # שלב 2: חישוב סטטיסטיקות
    p95 = numpy.percentile(latencies, 95)
    p99 = numpy.percentile(latencies, 99)
    error_rate = errors / 100
    
    # שלב 3: בדיקה מול thresholds
    # TODO: מה הערכים הנכונים? ⬇️
    THRESHOLD_P95_MS = 500   # ❌ ניחוש
    THRESHOLD_P99_MS = 1000  # ❌ ניחוש
    MAX_ERROR_RATE = 0.05    # ❌ ניחוש (5%)
    
    # ⚠️ השורות הבאות מושבתות כי לא יודעים את הערכים!
    # assert p95 < THRESHOLD_P95_MS, f"P95 {p95}ms too high"
    # assert p99 < THRESHOLD_P99_MS, f"P99 {p99}ms too high"
    assert error_rate <= MAX_ERROR_RATE, f"Error rate {error_rate} too high"
    
    # במקום assertion - רק warning:
    if p95 >= THRESHOLD_P95_MS:
        logger.warning(f"⚠️ P95 {p95}ms exceeds {THRESHOLD_P95_MS}ms")
```

---

### רקע על הפונקציה הנבדקת

**Endpoint:** `POST /config/{task_id}`

**תפקיד:**
- מקבל קונפיגורציה לעיבוד DAS (Distributed Acoustic Sensing)
- יוצר baby analyzer instance
- מאתחל pipeline עיבוד נתונים
- מחזיר אישור למשתמש

**תהליך פנימי:**
1. Parse configuration (JSON → objects)
2. Validate parameters (sensors, frequencies, NFFT, etc.)
3. Allocate resources (memory, threads)
4. Initialize RabbitMQ consumer
5. Start baby analyzer process
6. Return response to client

**קריטיות:**
- **משתמש מחכה** - זה API סינכרוני
- **חוויית משתמש** - אם איטי = משתמש מתוסכל
- **עומס** - המערכת מטפלת ב-10-50 קונפיגורציות במקביל

---

### מטרת הבדיקות

**מה אנחנו רוצים להבטיח:**

1. **חוויית משתמש טובה:**
   - API מגיב מהר (לא מחכים דקות)
   - משתמש מקבל feedback בזמן סביר

2. **יציבות תחת עומס:**
   - 100 בקשות במקביל לא "מקרסות" את המערכת
   - P95/P99 נשארים יציבים

3. **זיהוי רגרסיות:**
   - אם פיתוח חדש האט את המערכת - נגלה מיד
   - לא נגלה רק בייצור

4. **אכיפת SLA:**
   - אם יש הסכם עם לקוח - נוודא שמקיימים אותו

---

### הצורך ב-Spec ביחס לבדיקות

**מדוע אנחנו צריכים thresholds:**

#### ללא Spec:
```python
# ⚠️ המצב הנוכחי:
p95 = 834ms  # הבדיקה עוברת
p95 = 2341ms # הבדיקה עוברת
p95 = 8923ms # הבדיקה עוברת
# כל ערך "עובר" - אין משמעות לבדיקה!
```

#### עם Spec:
```python
# ✅ עם threshold מוגדר:
THRESHOLD_P95_MS = 500

p95 = 423ms  # ✅ PASS - מצוין!
p95 = 834ms  # ❌ FAIL - יש רגרסיה, צריך לחקור
p95 = 2341ms # ❌ FAIL - בעיה חמורה!
```

---

### מה אני רוצה להשיג

**מטרות קונקרטיות:**

1. **קבלת ערכים רשמיים:**
   ```
   POST /config:
   - P95 < ? ms
   - P99 < ? ms
   - Error rate < ? %
   
   GET /metadata:
   - P95 < ? ms
   
   GET /channels:
   - Response time < ? ms
   ```

2. **הפעלת Assertions:**
   ```python
   # Before:
   # assert p95 < THRESHOLD  # מושבת
   
   # After:
   assert p95 < THRESHOLD  # ✅ פעיל!
   ```

3. **28 בדיקות יספקו תוצאות משמעותיות:**
   - תפסו רגרסיות בביצועים
   - יאמתו SLA
   - ימנעו deployment של קוד איטי

---

### איך זה מקדם אותנו

**תועלות מיידיות:**

1. **איכות גבוהה יותר:**
   - לא נפרוס קוד איטי לייצור
   - נזהה בעיות בשלב פיתוח

2. **ביטחון בשינויים:**
   ```
   Developer מוסיף feature חדש
   ↓
   בדיקות ביצועים רצות אוטומטית
   ↓
   אם P95 עלה מ-400ms ל-1200ms → ❌ FAIL
   ↓
   Developer יודע מיד שיש בעיה
   ↓
   מתקן לפני merge
   ```

3. **SLA Management:**
   - אם יש הסכם: "API תענה תוך 1 שנייה"
   - הבדיקות מאמתות זאת 24/7
   - לא צריך לבדוק ידנית

4. **מדידה אובייקטיבית:**
   - "המערכת מהירה" ← סובייקטיבי
   - "P95 = 423ms, target = 500ms" ← אובייקטיבי

**תועלות ארוכות טווח:**

1. **תיעוד חי:**
   - Thresholds מתעדים את הציפיות מהמערכת
   - מפתח חדש רואה: "אה, המערכת צריכה לענות תוך 500ms"

2. **Trend Analysis:**
   - עוקבים אחר P95 לאורך זמן
   - רואים אם יש ירידה הדרגתית

3. **Capacity Planning:**
   - "האם יש לנו מספיק resources?"
   - מסתכלים על P95/P99 תחת עומס

---

### שאלות לדיון

**אנחנו צריכים להחליט:**

1. **מהו P95 threshold סביר ל-POST /config?**
   - האם 500ms סביר?
   - או צריך פחות (300ms)?
   - או יותר (1000ms)?

2. **מהו P99 threshold?**
   - פי כמה מ-P95?
   - בדרך כלל: P99 = 2-3x P95

3. **מהו אחוז שגיאות מקסימלי?**
   - 5% (1 מתוך 20 נכשל)?
   - 1% (1 מתוך 100)?
   - 0.1%?

4. **האם צריך thresholds שונים ל-live vs historic mode?**
   - Live: real-time → צריך להיות מהיר
   - Historic: playback → אפשר יותר איטי?

5. **מהי חלון המדידה?**
   - 100 בקשות?
   - 1000 בקשות?
   - 5 דקות של בקשות רציפות?

---

## נושא #2: ROI Change Limit - 50% Hardcoded

### מהות הבדיקות

**מה אנחנו בודקים:**
- שינוי ROI (Region Of Interest) דינמי במהלך streaming
- שהמערכת מונעת שינויים "קיצוניים" מדי
- שהמערכת מאפשרת שינויים "סבירים"

**איך הבדיקה עובדת:**
```python
def test_roi_change_safety():
    """בודק שאי אפשר לשנות ROI יותר מדי בבת אחת"""
    
    # מצב התחלתי
    current_roi = {
        "min_sensor": 100,
        "max_sensor": 200  # ROI גודל 100 sensors
    }
    
    # שינוי מוצע
    new_roi = {
        "min_sensor": 100,
        "max_sensor": 400  # ROI גודל 300 sensors - פי 3!
    }
    
    # חישוב שינוי באחוזים
    current_size = 200 - 100 = 100
    new_size = 400 - 100 = 300
    change_percent = (300 - 100) / 100 * 100 = 200%
    
    # בדיקה מול threshold
    MAX_CHANGE_PERCENT = 50.0  # ❌ לא אושר!
    
    result = validate_roi_change_safety(current_roi, new_roi)
    
    if change_percent > MAX_CHANGE_PERCENT:
        assert result["is_safe"] == False  # ✅ צריך לדחות
        assert "warning" in result
    else:
        assert result["is_safe"] == True  # ✅ צריך לאשר
```

---

### רקע על הפונקציה הנבדקת

**Feature:** Dynamic ROI Adjustment via RabbitMQ

**תפקיד:**
- משתמש רוצה "להגדיל זום" על אזור ספציפי במהלך streaming
- שליחת פקודה דרך RabbitMQ: `RegionOfInterestCommand`
- Baby analyzer מתאים את ROI בזמן אמת
- לא צריך לעצור ולהתחיל streaming מחדש

**למה צריך הגנה:**
- **עומס עיבוד:** ROI גדול = יותר sensors = יותר CPU/Memory
- **יציבות:** שינוי קיצוני מדי עלול לגרום ל-spike בעומס
- **חוויית משתמש:** שינוי גדול מדי = lag בתצוגה

**תהליך פנימי:**
```
1. Client שולח RegionOfInterestCommand
   ↓
2. RabbitMQ מעביר ל-Baby Analyzer
   ↓
3. Validator בודק: האם השינוי סביר?
   ↓
4. אם כן: מתאים את ROI ומחזיר data חדש
   אם לא: דוחה + שולח error
```

---

### מטרת הבדיקות

**מה אנחנו רוצים להבטיח:**

1. **מניעת overload:**
   ```
   תרחיש לא רצוי:
   - ROI נוכחי: 10 sensors
   - משתמש מבקש: 2000 sensors (כל המערך!)
   - המערכת: מתה (out of memory)
   
   עם validation:
   - השינוי נדחה: "Too large, max 50% change"
   - המערכת נשארת יציבה
   ```

2. **גמישות לשימושים לגיטימיים:**
   ```
   תרחיש רצוי:
   - ROI נוכחי: 100 sensors
   - משתמש מבקש: 130 sensors (הגדלה של 30%)
   - המערכת: מאשרת
   ```

3. **חוויית משתמש עקבית:**
   - משתמשים יודעים מה מותר ומה לא
   - לא תהיה הפתעה: "למה דחו לי את הבקשה?"

---

### הצורך ב-Spec ביחס לבדיקות

**הבעיה הנוכחית:**

```python
# src/utils/validators.py line 395
def validate_roi_change_safety(
    current_min: int,
    current_max: int,
    new_min: int,
    new_max: int,
    max_change_percent: float = 50.0  # ❌ מי קבע 50%?
):
```

**השאלות שצריך לענות עליהן:**

1. **האם 50% נכון?**
   - מאיפה הערך הזה הגיע?
   - מבוסס על מה? ניסיון? ניחוש?
   - האם נבדק בפועל?

2. **האם זה מספיק?**
   ```
   דוגמה:
   - ROI: 100 → 150 sensors (50%) = מותר
   - האם זה סביר מבחינת resources?
   - האם זה לא יגרום ל-lag?
   ```

3. **האם זה מגביל מדי?**
   ```
   דוגמה:
   - ROI: 10 → 20 sensors (100% אבל רק 10 sensors)
   - נדחה בגלל 100% > 50%
   - אבל 10 sensors זה כלום! מדוע לדחות?
   ```

4. **האם צריך גם absolute limit?**
   ```
   דוגמה:
   - ROI: 1000 → 1499 sensors (49.9% ✅)
   - מותר לפי אחוזים
   - אבל תוספת של 499 sensors זה הרבה מאוד!
   ```

---

### מה אני רוצה להשיג

**מטרות קונקרטיות:**

1. **אישור או תיקון הערך 50%:**
   ```
   אפשרות A: "כן, 50% נכון"
   → עדכון documentation
   → מסיר ❌ סימון מהקוד
   
   אפשרות B: "לא, צריך להיות 30%"
   → עדכון הקוד
   → עדכון 6 הבדיקות
   ```

2. **הוספת כללים נוספים (אם נדרש):**
   ```python
   # אפשרות מורכבת יותר:
   def validate_roi_change_safety(...):
       change_percent = calculate_change(...)
       
       # כלל 1: אחוזים
       if change_percent > 50:
           return False
       
       # כלל 2: גודל מוחלט
       absolute_change = abs(new_size - current_size)
       if absolute_change > 500:  # מקסימום 500 sensors בשינוי
           return False
       
       # כלל 3: גודל מינימלי
       if new_size < 10:  # מינימום 10 sensors
           return False
       
       return True
   ```

3. **הגדרת cooldown period (אם נדרש):**
   ```python
   # האם אפשר לשנות ROI כל שנייה?
   # או צריך להמתין X שניות בין שינויים?
   
   MIN_TIME_BETWEEN_CHANGES_SEC = 5  # ?
   ```

4. **הגדרת התנהגות:**
   ```
   כאשר עוברים limit:
   - Reject (דחייה מוחלטת)?
   - Warning (אזהרה אבל מאשר)?
   - Throttle (מאשר חלקי - מקסימום מותר)?
   ```

---

### איך זה מקדם אותנו

**תועלות מיידיות:**

1. **בטיחות מובטחת:**
   - לא יהיו crashes מ-ROI changes מופרזים
   - המערכת יציבה

2. **תיעוד ברור:**
   ```
   Documentation:
   "Dynamic ROI: Maximum change allowed: 50% per adjustment"
   
   User knows:
   - אם יש לי ROI של 100, אוכל להגדיל עד 150
   - לא אנסה להגדיל ל-300 ויתקע
   ```

3. **בדיקות משמעותיות:**
   - 6 בדיקות ROI יוכלו לאמת התנהגות נכונה
   - לא יהיו false positives/negatives

**תועלות ארוכות טווח:**

1. **שיפור Feature:**
   - אולי נגלה שהגבלה של 50% מגבילה מדי
   - נשנה ל-70% עם נימוק מבוסס

2. **Capacity Planning:**
   - יודעים מה המקסימום: 50% ROI changes
   - מחשבים resources לפי זה

3. **UX Improvements:**
   - אפשר להוסיף ב-UI: "Max increase: 50%"
   - משתמש לא מתוסכל

---

### שאלות לדיון

**אנחנו צריכים להחליט:**

1. **מהו אחוז השינוי המקסימלי?**
   - 50%? (נוכחי)
   - 30%? (יותר שמרני)
   - 70%? (יותר גמיש)
   - תלוי בגודל ROI הנוכחי?

2. **האם צריך גם limit מוחלט?**
   - "מקסימום 500 sensors בשינוי אחד"
   - או רק אחוזים?

3. **האם צריך גם minimum ROI size?**
   - "ROI לא יכול להיות קטן מ-10 sensors"

4. **האם יש cooldown period?**
   - "לא יותר מ-1 שינוי ל-5 שניות"
   - או unlimited?

5. **מה ההתנהגות כשעוברים?**
   - Reject (error message)?
   - Throttle (אשר עד מקסימום)?
   - Warning (log but allow)?

6. **האם שונה ל-live vs historic?**
   - Live: יותר שמרני? (realtime sensitive)
   - Historic: יותר גמיש? (playback)

---

## נושא #3: NFFT Validation - קבלה של כל ערך

### מהות הבדיקות

**מה אנחנו בודקים:**
- שהמערכת מקבלת רק ערכי NFFT תקינים
- שערכים לא תקינים נדחים (או מוזהרים)
- שיש עקביות בין הקוד לקובץ ה-configuration

**NFFT - רקע טכני:**
- **NFFT** = Number of FFT points
- **FFT** = Fast Fourier Transform
- משמש להמרת אות מזמן לתדר (time domain → frequency domain)
- ערך גבוה יותר = רזולוציית תדר טובה יותר, אבל עומס CPU גבוה יותר

**דרישה טכנית:**
- NFFT צריך להיות חזקה של 2 (power of 2) לביצועים אופטימליים
- דוגמאות תקינות: 256, 512, 1024, 2048, 4096
- דוגמאות לא תקינות: 300, 1000, 1500

**איך הבדיקה עובדת:**
```python
def test_nfft_validation():
    """בודק שערכי NFFT מאומתים כראוי"""
    
    # ערכים תקינים - צריכים לעבור
    valid_values = [256, 512, 1024, 2048]
    for nfft in valid_values:
        result = validate_nfft_value(nfft)
        assert result == True  # ✅
    
    # ערכים לא תקינים - מה צריך לקרות? ⬇️
    invalid_values = [300, 1000, 1500]
    for nfft in invalid_values:
        result = validate_nfft_value(nfft)
        # ❓ האם result צריך להיות False?
        # ❓ או True + warning?
        # ❓ לא יודעים!
```

---

### רקע על הפונקציה הנבדקת

**Function:** `validate_nfft_value()`

**מיקום:** `src/utils/validators.py:194-227`

**תפקיד:**
- מאמת שערך NFFT חוקי לפני יצירת configuration
- מגן מפני ערכים שיגרמו לבעיות ביצועים או קריסות

**הקוד הנוכחי:**
```python
def validate_nfft_value(nfft: int) -> bool:
    """Validate NFFT value (should be power of 2 for efficiency)."""
    
    if not isinstance(nfft, int):
        raise ValidationError("NFFT must be an integer")
    
    if nfft <= 0:
        raise ValidationError("NFFT must be positive")
    
    # בדיקה: האם חזקה של 2?
    is_power_of_2 = (nfft & (nfft - 1)) == 0
    
    if not is_power_of_2:
        warnings.warn(f"NFFT={nfft} not power of 2")  # ⚠️ רק מזהיר!
    
    return True  # ✅ תמיד מחזיר True!
```

**הבעיה:**
- הפונקציה **תמיד מחזירה True**
- רק מזהירה אם לא power of 2
- **לא דוחה** ערכים לא תקינים

**מה קורה אחר כך:**
```
1. User שולח: NFFT = 1500
   ↓
2. validate_nfft_value(1500)
   ↓
3. Warning: "NFFT=1500 not power of 2"
   ↓
4. Return: True ✅
   ↓
5. Baby Analyzer מנסה להריץ עם NFFT=1500
   ↓
6. ביצועים גרועים / התנהגות לא צפויה
```

---

### אי-עקביות: קוד vs קובץ Config

**בקובץ Config:**
```yaml
# config/settings.yaml
nfft:
  valid_values: [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
  default: 1024
  description: "NFFT for spectrogram calculation"
```

**בקוד:**
```python
# src/utils/validators.py
def validate_nfft_value(nfft: int) -> bool:
    # ❌ לא משתמש ברשימה מה-config!
    # ❌ מקבל כל integer חיובי
    # ❌ רק מזהיר אם לא power of 2
    return True
```

**התוצאה:**
- **אין אכיפה** של הרשימה מה-config
- **אי-עקביות** בין מה שמתועד למה שקורה

---

### מטרת הבדיקות

**מה אנחנו רוצים להבטיח:**

1. **ביצועים אופטימליים:**
   ```
   NFFT חזקה של 2:
   - FFT אלגוריתם מהיר (O(n log n))
   - שימוש יעיל ב-CPU cache
   
   NFFT לא חזקה של 2:
   - FFT אלגוריתם איטי יותר
   - שימוש לא יעיל ב-memory
   ```

2. **מניעת ערכים קיצוניים:**
   ```
   NFFT = 999999:
   - עומס CPU אדיר
   - out of memory
   - crash
   ```

3. **עקביות עם documentation:**
   - אם config אומר: [256, 512, 1024, 2048]
   - הקוד צריך לאכוף זאת

---

### הצורך ב-Spec ביחס לבדיקות

**השאלות שצריך לענות עליהן:**

1. **האם לאכוף את הרשימה מה-config?**
   ```python
   # אופציה A: אכיפה קשיחה
   VALID_NFFT = [256, 512, 1024, 2048]
   if nfft not in VALID_NFFT:
       raise ValidationError(f"NFFT must be one of {VALID_NFFT}")
   ```

2. **או להשאיר warning בלבד?**
   ```python
   # אופציה B: גמישות
   if not is_power_of_2(nfft):
       warnings.warn("Not power of 2, performance may be suboptimal")
   return True  # מאשר בכל מקרה
   ```

3. **מהו ה-maximum NFFT?**
   ```
   - 65536? (כמו ב-config)
   - 131072? (גבוה יותר)
   - unlimited? (לא מומלץ)
   ```

4. **מהו ה-minimum NFFT?**
   ```
   - 128? (כמו ב-config)
   - 64? (נמוך יותר)
   - any positive? (לא מומלץ)
   ```

5. **האם לאפשר ערכים custom?**
   ```
   תרחיש:
   - משתמש מתקדם רוצה NFFT = 3000
   - לא ברשימה, לא power of 2
   - אבל הוא יודע מה הוא עושה
   - האם לאפשר?
   ```

---

### מה אני רוצה להשיג

**מטרות קונקרטיות:**

1. **החלטה על מדיניות:**
   ```
   אופציה 1: "קשיח - רק מה שברשימה"
   → עדכון הקוד לאכיפה
   → 6 בדיקות יאמתו rejection של ערכים לא תקינים
   
   אופציה 2: "גמיש - כל power of 2"
   → עדכון documentation
   → 6 בדיקות יאמתו warning אבל acceptance
   
   אופציה 3: "היברידי"
   → אכיפת min/max
   → warning אם לא ברשימה אבל בטווח
   → rejection אם מחוץ לטווח
   ```

2. **יישור קוד ל-config:**
   ```python
   # אם החלטנו על אכיפה:
   from config.settings import VALID_NFFT_VALUES
   
   def validate_nfft_value(nfft: int) -> bool:
       if nfft not in VALID_NFFT_VALUES:
           raise ValidationError(f"NFFT must be one of {VALID_NFFT_VALUES}")
       return True
   ```

3. **תיעוד ברור:**
   ```
   בdocumentation:
   "NFFT Values:
   - Supported: 256, 512, 1024, 2048, 4096
   - Must be power of 2
   - Maximum: 65536
   - Recommended: 1024 (balance between resolution and performance)"
   ```

---

### איך זה מקדם אותנו

**תועלות מיידיות:**

1. **מניעת בעיות ביצועים:**
   ```
   Before: User sends NFFT=1500
   → System accepts
   → Slow performance
   → Complaints
   
   After: User sends NFFT=1500
   → System rejects: "NFFT must be power of 2"
   → User fixes to 1024 or 2048
   → Good performance
   ```

2. **בדיקות משמעותיות:**
   - 6 בדיקות NFFT יוכלו לאמת rejection נכון
   - לא יהיו false passes

3. **UX טוב יותר:**
   ```
   בUI אפשר להציג dropdown:
   "Select NFFT: [256 | 512 | 1024 | 2048]"
   
   במקום free text שמאפשר ערכים לא תקינים
   ```

**תועלות ארוכות טווח:**

1. **תיעוד מדויק:**
   - API documentation מפרט בדיוק מה מותר
   - לקוחות יודעים מה לצפות

2. **שיפור Feature:**
   - אם נגלה שצריך תמיכה ב-NFFT=8192
   - פשוט להוסיף לרשימה

3. **עקביות:**
   - קוד, config, documentation - הכל מסונכרן

---

### שאלות לדיון

**אנחנו צריכים להחליט:**

1. **מדיניות validation:**
   - אכיפה קשיחה (רק מהרשימה)?
   - גמישות (כל power of 2)?
   - היברידי?

2. **ערכים מינימום ומקסימום:**
   - Min NFFT: 128? 64? אחר?
   - Max NFFT: 65536? 131072? unlimited?

3. **custom values:**
   - האם לאפשר למשתמשים מתקדמים?
   - עם warning?
   - או חסימה מוחלטת?

4. **error handling:**
   - דחייה מוחלטת (400 Bad Request)?
   - acceptance עם warning?
   - auto-correction למקסימום מותר?

5. **performance guidelines:**
   - איזה NFFT מומלץ לרוב המקרים?
   - מתי להשתמש בערכים נמוכים/גבוהים?

---

## נושא #4: Frequency Range - אין גבולות מוחלטים

### מהות הבדיקות

**מה אנחנו בודקים:**
- שטווח התדרים (frequency range) שמשתמש מבקש הוא תקין
- שאין ערכים קיצוניים שיגרמו לבעיות
- ש-min < max
- שהתדרים בתוך גבולות פיזיקליים (Nyquist limit)

**איך הבדיקה עובדת:**
```python
def test_frequency_range_validation():
    """בודק validation של frequency range"""
    
    # תקין
    config = {
        "frequencyRange": {"min": 0, "max": 500}
    }
    assert validate_frequency_range(config) == True  # ✅
    
    # min > max - צריך להיכשל
    config = {
        "frequencyRange": {"min": 600, "max": 500}
    }
    assert validate_frequency_range(config) == False  # ✅
    
    # ערכים קיצוניים - מה צריך לקרות? ⬇️
    extreme_configs = [
        {"min": 0, "max": 999999999},  # ❓ תקין?
        {"min": -1000, "max": 500},    # ❓ שלילי מותר?
        {"min": 100, "max": 100},      # ❓ min == max?
    ]
```

---

### רקע על הפונקציה הנבדקת

**Feature:** Frequency Range Selection

**תפקיד:**
- משתמש בוחר איזה טווח תדרים רוצה לראות
- Baby Analyzer מחשב spectrogram רק לתדרים האלה
- חוסך CPU/Memory - לא מחשב תדרים שלא מעניינים

**פיזיקה - Nyquist Limit:**
```
PRR = Pulse Repetition Rate (samples per second)
Nyquist Frequency = PRR / 2

דוגמה:
PRR = 2000 Hz
Nyquist = 1000 Hz
→ אפשר לזהות תדרים עד 1000 Hz בלבד
→ בקשה ל-max_freq > 1000 Hz = לא הגיוני!
```

**הקוד הנוכחי:**
```python
# src/models/focus_server_models.py:46-57
class FrequencyRange(BaseModel):
    min: int = Field(..., ge=0)  # ✅ >= 0
    max: int = Field(..., ge=0)  # ✅ >= 0
    # ❌ אין absolute maximum!
    # ❌ אין בדיקת minimum span!
    # ❌ אין בדיקה שmin < max!
```

**מה חסר:**
```python
# מה שהיה צריך להיות:
class FrequencyRange(BaseModel):
    min: int = Field(..., ge=0, le=MAX_FREQ)  # גם maximum
    max: int = Field(..., ge=0, le=MAX_FREQ)  # גם maximum
    
    @model_validator
    def check_range(self):
        if self.max <= self.min:
            raise ValueError("max must be > min")
        if (self.max - self.min) < MIN_SPAN:
            raise ValueError("span too small")
        return self
```

---

### מטרת הבדיקות

**מה אנחנו רוצים להבטיח:**

1. **גבולות פיזיקליים:**
   ```
   תרחיש לא רצוי:
   - PRR = 2000 Hz (Nyquist = 1000 Hz)
   - User מבקש: max_freq = 5000 Hz
   - המערכת: מקבלת!
   - התוצאה: data לא תקין (aliasing)
   
   עם validation:
   - המערכת: דוחה "max_freq exceeds Nyquist limit"
   - התוצאה: data תקין
   ```

2. **מניעת ערכים קיצוניים:**
   ```
   תרחיש לא רצוי:
   - User מבקש: [0, 999999999 Hz]
   - CPU: מנסה לחשב spectrogram עם מיליארד תדרים
   - המערכת: קורסת (out of memory)
   
   עם validation:
   - המערכת: דוחה "max_freq exceeds absolute limit"
   - התוצאה: יציבות
   ```

3. **minimum span:**
   ```
   תרחיש לא שימושי:
   - User מבקש: [100, 101 Hz] (span = 1 Hz)
   - המערכת: מחשבת spectrogram לתדר אחד
   - רזולוציה: גרועה, לא רואים כלום
   
   עם validation:
   - המערכת: דוחה "span too small, minimum 10 Hz"
   - התוצאה: נתונים שימושיים
   ```

---

### הצורך ב-Spec ביחס לבדיקות

**השאלות שצריך לענות עליהן:**

1. **מהו absolute maximum frequency?**
   ```
   אופציות:
   - לפי Nyquist: PRR/2 (דינמי)
   - קבוע: 5000 Hz? 10000 Hz?
   - unlimited? (לא מומלץ)
   ```

2. **מהו absolute minimum frequency?**
   ```
   אופציות:
   - 0 Hz? (DC - תדר אפס)
   - 10 Hz? (תדרים נמוכים מאוד)
   - 20 Hz? (כמו שמיעה אנושית)
   ```

3. **מהו minimum span?**
   ```
   אופציות:
   - 1 Hz? (ספציפי מאוד)
   - 10 Hz? (סביר)
   - 100 Hz? (רחב יותר)
   - תלוי ב-NFFT?
   ```

4. **האם min == max מותר?**
   ```
   תרחיש:
   - User מבקש: [100, 100 Hz]
   - כוונה: רק תדר ספציפי אחד
   - האם זה valid use case?
   ```

---

### מה אני רוצה להשיג

**מטרות קונקרטיות:**

1. **קביעת גבולות:**
   ```yaml
   # config/settings.yaml
   frequency:
     absolute_min_hz: 0  # או 10? או 20?
     absolute_max_hz: 5000  # או dynamic לפי PRR?
     minimum_span_hz: 10  # או 100?
     allow_equal_min_max: false  # או true?
   ```

2. **עדכון Model:**
   ```python
   class FrequencyRange(BaseModel):
       min: int = Field(..., ge=FREQ_MIN, le=FREQ_MAX)
       max: int = Field(..., ge=FREQ_MIN, le=FREQ_MAX)
       
       @model_validator
       def validate_range(self):
           if self.max < self.min:
               raise ValueError("max must be >= min")
           
           span = self.max - self.min
           if span < MIN_SPAN:
               raise ValueError(f"span must be >= {MIN_SPAN} Hz")
           
           if self.max > get_nyquist_limit():
               raise ValueError("max exceeds Nyquist limit")
           
           return self
   ```

3. **16 בדיקות יוכלו לאמת:**
   - Rejection של ערכים קיצוניים
   - Rejection של span קטן מדי
   - Rejection של min >= max
   - Acceptance של ערכים תקינים

---

### איך זה מקדם אותנו

**תועלות מיידיות:**

1. **איכות נתונים:**
   - לא יהיו spectrograms עם aliasing
   - לא יהיו ranges לא שימושיים

2. **יציבות:**
   - לא יהיו crashes מ-out of memory
   - לא יהיו תלייות מחישובים מופרזים

3. **UX טוב יותר:**
   ```
   בUI:
   "Frequency Range:
   Min: [___] Hz (0 - 5000)
   Max: [___] Hz (0 - 5000)
   Minimum span: 10 Hz"
   
   User input: min=100, max=105
   → Validation: ✅ (span=5 >= 10? לא!)
   → Error: "Span must be at least 10 Hz"
   → User corrects to: max=110
   ```

---

### שאלות לדיון

1. **Absolute maximum frequency?**
2. **Absolute minimum frequency?**
3. **Minimum span?**
4. **האם min == max valid?**
5. **Dynamic validation לפי PRR/Nyquist?**

---

## נושא #5: Sensor Range - אין גבולות ROI

### מהות הבדיקות

**מה אנחנו בודקים:**
- שטווח ה-sensors (ROI) שמשתמש מבקש הוא תקין
- שיש מינימום sensors (לא 1)
- שיש מקסימום sensors (לא כל המערך)
- ש-min < max

**איך הבדיקה עובדת:**
```python
def test_sensor_range_validation():
    """בודק validation של sensor range"""
    
    # תקין
    config = {
        "sensors": {"min": 100, "max": 200}  # 100 sensors
    }
    assert validate_sensor_range(config) == True  # ✅
    
    # Edge cases - מה צריך לקרות? ⬇️
    edge_cases = [
        {"min": 1, "max": 1},      # ❓ ROI של sensor אחד?
        {"min": 1, "max": 2222},   # ❓ כל המערך?
        {"min": 100, "max": 105},  # ❓ 5 sensors - מספיק?
    ]
```

---

### רקע על הפונקציה הנבדקת

**Feature:** Sensor Range Selection (ROI)

**תפקיד:**
- משתמש בוחר איזה חלק מהמערך (2222 sensors) לעבד
- חוסך CPU/Memory - לא מעבד sensors שלא מעניינים
- מאפשר "zoom in" על אזור ספציפי

**הקוד הנוכחי:**
```python
# src/utils/validators.py:116-151
def validate_sensor_range(sensor_range: SensorRange) -> bool:
    if sensor_range.min_sensor < 1:
        return False
    
    if sensor_range.max_sensor > 2222:  # Total sensors
        return False
    
    if sensor_range.max_sensor <= sensor_range.min_sensor:
        return False
    
    # ✅ בודק גבולות מערך
    # ✅ בודק min < max
    # ❌ לא בודק minimum ROI size
    # ❌ לא בודק maximum ROI size
    
    return True
```

**מה חסר:**
```python
# מה שהיה צריך להיות:
def validate_sensor_range(sensor_range: SensorRange) -> bool:
    # ... הבדיקות הקיימות ...
    
    roi_size = sensor_range.max_sensor - sensor_range.min_sensor
    
    if roi_size < MIN_ROI_SIZE:  # ❌ חסר!
        return False, "ROI too small"
    
    if roi_size > MAX_ROI_SIZE:  # ❌ חסר!
        return False, "ROI too large"
    
    return True
```

---

### מטרת הבדיקות

**מה אנחנו רוצים להבטיח:**

1. **מינימום שימושי:**
   ```
   תרחיש לא שימושי:
   - User מבקש: ROI [100, 100] (1 sensor)
   - המערכת: מקבלת
   - התוצאה: spectrogram עם sensor אחד - לא רואים כלום
   
   עם validation:
   - המערכת: דוחה "ROI must be at least 10 sensors"
   - User מתקן: ROI [100, 110]
   - התוצאה: data שימושי
   ```

2. **מקסימום סביר:**
   ```
   תרחיש לא פרקטי:
   - User מבקש: ROI [1, 2222] (כל המערך!)
   - CPU: מעבד 2222 sensors
   - Memory: GB של data
   - התוצאה: slow/crash
   
   עם validation:
   - המערכת: דוחה "ROI too large, max 1000 sensors"
   - User מתקן: ROI [1, 500]
   - התוצאה: ביצועים טובים
   ```

3. **טווח מומלץ:**
   ```
   לרוב המקרים:
   - ROI: 50-500 sensors
   - מספיק לראות תמונה ברורה
   - לא עומס מופרז
   ```

---

### הצורך ב-Spec ביחס לבדיקות

**השאלות שצריך לענות עליהן:**

1. **מהו minimum ROI size?**
   ```
   אופציות:
   - 1 sensor? (מינימלי)
   - 10 sensors? (סביר)
   - 50 sensors? (מומלץ)
   ```

2. **מהו maximum ROI size?**
   ```
   אופציות:
   - 500 sensors? (שמרני)
   - 1000 sensors? (סביר)
   - 2222 sensors? (כל המערך)
   - unlimited?
   ```

3. **האם single-sensor ROI valid?**
   ```
   תרחיש:
   - User רוצה לעקוב אחרי sensor ספציפי אחד
   - min = max = 100
   - האם זה use case לגיטימי?
   ```

4. **recommended range?**
   ```
   לתיעוד:
   "Recommended ROI size: 50-500 sensors
   For most use cases, this provides good resolution
   without excessive load."
   ```

---

### מה אני רוצה להשיג

**מטרות קונקרטיות:**

1. **קביעת גבולות:**
   ```yaml
   # config/settings.yaml
   sensors:
     total: 2222
     roi_min_size: 10  # או 1? או 50?
     roi_max_size: 1000  # או 500? או 2222?
     recommended_min: 50
     recommended_max: 500
   ```

2. **עדכון Validation:**
   ```python
   def validate_sensor_range(sensor_range: SensorRange) -> bool:
       # ... הבדיקות הקיימות ...
       
       roi_size = sensor_range.max_sensor - sensor_range.min_sensor
       
       if roi_size < settings.ROI_MIN_SIZE:
           raise ValidationError(f"ROI must be at least {settings.ROI_MIN_SIZE} sensors")
       
       if roi_size > settings.ROI_MAX_SIZE:
           raise ValidationError(f"ROI cannot exceed {settings.ROI_MAX_SIZE} sensors")
       
       return True
   ```

3. **15 בדיקות יוכלו לאמת:**
   - Rejection של ROI קטן מדי
   - Rejection של ROI גדול מדי
   - Acceptance של ROI תקין

---

### איך זה מקדם אותנו

**תועלות:**

1. **ביצועים צפויים:**
   - יודעים מראש max load
   - capacity planning

2. **UX טוב יותר:**
   - משתמשים יודעים גבולות
   - לא מקבלים rejections מפתיעים

3. **תיעוד:**
   - "ROI: 10-1000 sensors"
   - ברור למשתמשים

---

### שאלות לדיון

1. **Minimum ROI size?**
2. **Maximum ROI size?**
3. **Single-sensor ROI valid?**
4. **Recommended range?**

---

## נושא #6: API Response Time - Timeouts שרירותיים

### מהות הבדיקות

**מה אנחנו בודקים:**
- שה-API מגיב תוך זמן סביר
- שאין timeouts ארוכים מדי
- שעומדים ב-SLA (אם קיים)

**איך הבדיקה עובדת:**
```python
def test_get_channels_response_time():
    """בודק ש-GET /channels מגיב מהר"""
    
    start = time.time()
    response = api.get_channels()
    duration = time.time() - start
    
    # ❌ ערך שרירותי - "נראה סביר"
    MAX_RESPONSE_TIME_SEC = 1.0
    
    assert duration < MAX_RESPONSE_TIME_SEC, \
           f"GET /channels took {duration}s (max: {MAX_RESPONSE_TIME_SEC}s)"
```

---

### רקע על הפונקציה הנבדקת

**Endpoints נבדקים:**
- `GET /channels` - מחזיר רשימת channels זמינים
- `GET /metadata` - מחזיר metadata של recording
- `POST /config` - יוצר configuration חדשה

**למה זה חשוב:**
- **User experience** - משתמש מחכה
- **SLA** - אם יש הסכם עם לקוח
- **Performance monitoring** - זיהוי רגרסיות

---

### הצורך ב-Spec

**השאלות:**

1. **מהו timeout סביר לכל endpoint?**
   ```
   GET /channels: ? ms
   GET /metadata: ? ms
   POST /config: ? ms
   ```

2. **האם יש SLA מוסכם?**

3. **האם שונה ל-live vs historic?**

---

### מה אני רוצה להשיג

**קביעת SLA:**
```yaml
api_timeouts:
  get_channels: 200ms
  get_metadata: 500ms
  post_config: 1000ms
```

---

### שאלות לדיון

1. **Timeout לכל endpoint?**
2. **SLA קיים?**
3. **שונה ל-live/historic?**

---

## נושא #7: Config Edge Cases - התנהגות לא מוגדרת

### מהות הבדיקות

**מה אנחנו בודקים:**
- התנהגות במקרי קצה
- מה קורה כאשר min == max
- מה קורה עם ערכים קיצוניים

**איך הבדיקה עובדת:**
```python
def test_frequency_range_equal_min_max():
    """מה קורה כאשר min_freq == max_freq?"""
    
    config = {
        "frequencyRange": {"min": 100, "max": 100}
    }
    
    response = api.post_config(config)
    
    # ❓ מה צריך לקרות?
    # אופציה 1: 200 OK (תקין - תדר יחיד)
    # אופציה 2: 400 Error (לא תקין - span=0)
    # לא יודעים! ⬇️
    # assert response.status_code == ???
```

---

### הצורך ב-Spec

**צריך להגדיר התנהגות ל:**

| Edge Case | אופציה A | אופציה B |
|-----------|-----------|----------|
| min_freq == max_freq | 200 OK | 400 Error |
| min_channel == max_channel | 200 OK | 400 Error |
| ROI size = 1 sensor | 200 OK | 400 Error |
| NFFT לא ברשימה | Warning | Reject |

---

### מה אני רוצה להשיג

**החלטה על כל edge case:**
- 8 בדיקות יקבלו assertions
- התנהגות אחידה

---

### שאלות לדיון

1. **min == max: valid או invalid?**
2. **Edge values: reject או accept?**

---

## טבלת סיכום

| # | נושא | בדיקות מושפעות | עדיפות | מהות הבעיה | מה צריך להחליט |
|---|------|----------------|---------|-------------|----------------|
| 1 | Performance Thresholds | 28 | קריטי | אין SLA מוגדר | P95/P99 לכל endpoint |
| 2 | ROI Change 50% | 6 | קריטי | ערך לא אושר | האם 50% נכון? |
| 3 | NFFT Validation | 6 | קריטי | אין אכיפה | לאכוף רשימה או לא? |
| 4 | Frequency Limits | 16 | גבוה | אין maximum | Max/Min frequency |
| 5 | Sensor Range | 15 | גבוה | אין גבולות ROI | Min/Max ROI size |
| 6 | API Timeouts | 3 | בינוני | ערכים שרירותיים | SLA לכל endpoint |
| 7 | Edge Cases | 8 | בינוני | התנהגות לא ברורה | מה קורה כש-min==max |

**סה"כ: 82+ בדיקות מחכות ל-specs**

---

## תוכנית פעולה

### בפגישה:

**חלק א' - Critical Issues (60 דקות)**
1. נושא #1: Performance (20 דקות)
   - קביעת P95/P99 לכל endpoint
   - קביעת max error rate

2. נושא #2: ROI 50% (20 דקות)
   - אישור או תיקון ערך
   - cooldown period?

3. נושא #3: NFFT (20 דקות)
   - מדיניות validation
   - min/max values

**חלק ב' - High Priority (45 דקות)**
4. נושאים #4-5: Frequency & Sensor ranges
5. דיון קצר בכל נושא

**חלק ג' - סיכום והמשך (15 דקות)**
6. תיעוד החלטות
7. action items
8. timeline ליישום

---

### אחרי הפגישה:

**שבוע 1:**
- תיעוד כל ההחלטות ב-`SPECS_DECISIONS.md`
- עדכון `config/settings.yaml` עם הערכים החדשים

**שבוע 2:**
- עדכון קוד:
  - `src/utils/validators.py`
  - `tests/integration/performance/*.py`
  - `tests/integration/api/*.py`

**שבוע 3:**
- הרצת כל 82+ הבדיקות
- תיקון בעיות
- עדכון documentation

**שבוע 4:**
- עדכון Jira Xray
- CI/CD integration
- סיכום לצוות

---

## סיכום

### למה זה חשוב:

**הבעיה:**
- 82+ בדיקות רצות אבל לא יכולות להיכשל כשצריך
- לא יכולים לאכוף SLA, לזהות רגרסיות, למנוע באגים

**הפתרון:**
- פגישה אחת של 2-3 שעות
- קבלת החלטות על 7 נושאים קריטיים
- יישום תוך 1-2 שבועות

**התוצאה:**
- ✅ 82+ בדיקות משמעותיות
- ✅ זיהוי רגרסיות אוטומטי
- ✅ אכיפת SLA
- ✅ מניעת באגים בייצור
- ✅ תיעוד מלא ומדויק

---

**מוכנים לפגישה! 🎯**

