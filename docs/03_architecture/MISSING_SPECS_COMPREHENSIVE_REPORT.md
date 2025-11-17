# 📋 דוח מקיף: ספציפיקציות חסרות במערכת Focus Server
## Missing Specifications Comprehensive Report

**תאריך:** 22 אוקטובר 2025  
**סטטוס:** 🔴 **CRITICAL - חוסם 82+ טסטים אוטומטיים**  
**גרסה:** 1.0

---

## 🎯 סיכום מנהלים

### המצב הנוכחי:
- **190+ טסטים אוטומטיים** קיימים בפרויקט
- **82+ טסטים** מושפעים ישירות מחוסר specs
- **28 טסטי performance** עם assertions מושבתים
- **50+ ערכים hardcoded** שמעולם לא אושרו
- **11 TODO comments** בקוד המחכים ל-specs

### ההשפעה:
❌ טסטים רצים אבל **לא יכולים להיכשל** כשצריך  
❌ לא ניתן לזהות **ירידה בביצועים**  
❌ לא ניתן לאכוף **כללי איכות נתונים**  
❌ False positives מבזבזים זמן חקירה  
❌ False negatives מפספסים באגים אמיתיים

---

## 📊 טבלה מרכזית: כל ה-Specs החסרים

| # | קטגוריה | תיאור הבעיה | מיקום בקוד | מיקום במסמכים | מה חסר | טסטים מושפעים | עדיפות |
|---|---------|-------------|-----------|---------------|---------|---------------|--------|
| 1 | **Performance** | Performance assertions מושבתים | `tests/integration/performance/test_performance_high_priority.py:146-170` | `CONFLUENCE_SPECS_MEETING.md:46-85` | P95/P99 thresholds, Max error rate | 28 טסטים | 🔴 Critical |
| 2 | **ROI** | ROI change limit 50% hardcoded | `src/utils/validators.py:395` | `CONFLUENCE_SPECS_MEETING.md:87-118` | אישור ל-50%, cooldown period | 6 טסטים | 🔴 Critical |
| 3 | **NFFT** | NFFT validation מקבל כל ערך | `src/utils/validators.py:194-227` | `CONFLUENCE_SPECS_MEETING.md:125-159` | רשימת ערכים תקינים, maximum | 6 טסטים | 🔴 Critical |
| 4 | **Frequency** | אין absolute maximum/minimum | `src/models/focus_server_models.py:46-57` | `CONFLUENCE_SPECS_MEETING.md:161-197` | Max freq, Min freq, Min span | 16 טסטים | 🟠 High |
| 5 | **Sensors** | אין min/max ROI size | `src/utils/validators.py:116-151` | `CONFLUENCE_SPECS_MEETING.md:199-237` | Min ROI size, Max ROI size | 15 טסטים | 🟠 High |
| 6 | **API Timeouts** | Timeout thresholds שרירותיים | `tests/integration/api/test_api_endpoints_high_priority.py:135-147` | `CONFLUENCE_SPECS_MEETING.md:239-273` | SLA לכל endpoint | 3 טסטים | 🟡 Medium |
| 7 | **Config Edge Cases** | אין assertions ל-edge cases | `tests/integration/api/test_config_validation_high_priority.py:475-520` | `CONFLUENCE_SPECS_MEETING.md:275-310` | התנהגות צפויה ל-min==max | 8 טסטים | 🟡 Medium |
| 8 | **MongoDB Outage** | התנהגות לא מוגדרת | Test failures | `documentation/infrastructure/MONGODB_ISSUES_WORKFLOW.md` | HTTP status, recovery time | 5 טסטים | 🔴 Critical |
| 9 | **RabbitMQ Commands** | אין timeouts | `src/external/rabbitmq/` | `docs/RABBITMQ_AUTOMATION_GUIDE.md` | Command timeouts, retries | 8 טסטים | 🟠 High |
| 10 | **SingleChannel API** | Endpoint מחזיר 422 | `tests/integration/api/test_singlechannel_view_mapping.py` | `documentation/testing/SINGLECHANNEL_TEST_RESULTS.md:48-80` | האם endpoint תקין? payload format? | 11 טסטים | 🔴 Critical |
| 11 | **Live/Historical Threshold** | 1 שעה hardcoded | `src/utils/helpers.py:200-220` | `CRITICAL_MISSING_SPECS_LIST.md:195-206` | אישור ל-1 שעה או ערך אחר | - | 🟠 High |
| 12 | **Polling** | Timeouts hardcoded | `src/utils/helpers.py:474-504` | `CODE_EVIDENCE_MISSING_SPECS.md:231-259` | Timeout לכל סוג פעולה | Multiple | 🟡 Medium |
| 13 | **Default Values** | Mismatch code vs config | `src/utils/helpers.py:507-532` | `CODE_EVIDENCE_MISSING_SPECS.md:262-293` | יישור defaults בין code ל-config | Multiple | 🟡 Medium |
| 14 | **Waterfall Polling** | אין timeout logic | Multiple test files | `CRITICAL_MISSING_SPECS_LIST.md:44-55` | Max wait time, retry strategy | Multiple | 🟠 High |
| 15 | **Data Quality** | אין validation limits | `src/utils/validators.py:229-324` | `CRITICAL_MISSING_SPECS_LIST.md:70-90` | Amplitude range, missing data % | Multiple | 🟠 High |
| 16 | **Error Handling** | HTTP status semantics לא ברור | Multiple API files | `CRITICAL_MISSING_SPECS_LIST.md:246-273` | 200 no data, 208 meaning | Multiple | 🟠 High |
| 17 | **Time Validation** | Future/past time limits | `src/models/focus_server_models.py:99-105` | `CRITICAL_MISSING_SPECS_LIST.md:288-305` | Max future/past allowed | Multiple | 🟡 Medium |
| 18 | **Task Lifecycle** | אין cleanup/timeout | Backend (לא בקוד automation) | `CRITICAL_MISSING_SPECS_LIST.md:307-320` | Auto cleanup time, max concurrent | - | 🟡 Medium |
| 19 | **K8s Resource Limits** | לא מוגדר | K8s manifests | `CRITICAL_MISSING_SPECS_LIST.md:388-407` | CPU/Memory limits | - | 🟢 Low |
| 20 | **Security** | אין authentication | Backend | `CRITICAL_MISSING_SPECS_LIST.md:471-502` | Auth method, rate limiting | - | 🟢 Low |

**סה"כ:** 20 קטגוריות של specs חסרים

---

## 🔴 TOP 5 CRITICAL ISSUES (דורש תשומת לב מיידית)

### 1️⃣ **Performance Assertions Disabled**

#### 📍 **מיקום בקוד:**
```
File: tests/integration/performance/test_performance_high_priority.py
Lines: 146-170
Function: test_p95_p99_latency_post_config()
```

#### 📄 **מיקום במסמכים:**
- `CONFLUENCE_SPECS_MEETING.md` - Issue #1 (שורות 46-85)
- `CODE_EVIDENCE_MISSING_SPECS.md` - Example #2 (שורות 48-78)
- `CRITICAL_MISSING_SPECS_LIST.md` - Section 1 (שורות 10-66)

#### ❌ **הבעיה:**
```python
# TODO: Update thresholds after specs meeting
THRESHOLD_P95_MS = 500   # ❌ ערך שרירותי - לא מבוסס על דרישה
THRESHOLD_P99_MS = 1000  # ❌ ערך שרירותי - לא מבוסס על דרישה
MAX_ERROR_RATE = 0.05    # ❌ ערך שרירותי - לא מבוסס על דרישה

# TODO: Uncomment after specs meeting
# assert p95 < THRESHOLD_P95_MS   ❌ מושבת!
# assert p99 < THRESHOLD_P99_MS   ❌ מושבת!

# For now, just log warning
if p95 >= THRESHOLD_P95_MS:
    logger.warning(f"⚠️ P95 {p95}ms exceeds {THRESHOLD_P95_MS}ms")
```

#### 🎯 **מה חסר בדיוק:**

| Endpoint | Metric | Current Value | צריך החלטה |
|----------|--------|---------------|-----------|
| POST /config/{task_id} | P95 latency | 500ms (guess) | ? ms |
| POST /config/{task_id} | P99 latency | 1000ms (guess) | ? ms |
| POST /config/{task_id} | Error rate | 5% (guess) | ? % |
| GET /waterfall | P95 latency | - | ? ms |
| GET /waterfall | P99 latency | - | ? ms |
| GET /metadata | P95 latency | - | ? ms |
| GET /channels | Response time | 1000ms (guess) | ? ms |

#### 📊 **השפעה:**
- **28 טסטי performance** אוספים מטריקות אבל לא יכולים להיכשל
- לא ניתן לזהות ירידה בביצועים
- לא ניתן לאכוף SLAs
- False positives/negatives

#### ✅ **פתרון נדרש:**
1. קביעת P95/P99 thresholds לכל endpoint
2. קביעת max error rate
3. קביעת measurement window (כמה samples)
4. שונות בין live mode ל-historic mode?

---

### 2️⃣ **ROI Change Limit - 50% Hardcoded**

#### 📍 **מיקום בקוד:**
```
File: src/utils/validators.py
Line: 395
Function: validate_roi_change_safety()
```

#### 📄 **מיקום במסמכים:**
- `CONFLUENCE_SPECS_MEETING.md` - Issue #2 (שורות 87-118)
- `CODE_EVIDENCE_MISSING_SPECS.md` - Example #1 (שורות 22-45)
- `CRITICAL_MISSING_SPECS_LIST.md` - Section 3 (שורות 142-171)

#### ❌ **הבעיה:**
```python
def validate_roi_change_safety(
    current_min: int,
    current_max: int,
    new_min: int,
    new_max: int,
    max_change_percent: float = 50.0  # ❌ HARDCODED - מעולם לא אושר!
) -> Dict[str, Any]:
    """
    Validate ROI change is safe (not too drastic).
    Large ROI changes can cause processing disruptions.
    """
    current_range = current_max - current_min
    new_range = new_max - new_min
    range_change_percent = abs(new_range - current_range) / current_range * 100
    
    if range_change_percent > max_change_percent:
        validation_result["warnings"].append(
            f"Large ROI range change: {range_change_percent:.1f}% "
            f"(threshold: {max_change_percent}%)"
        )
```

#### 🎯 **מה חסר בדיוק:**

| שאלה | Status | השפעה |
|------|--------|-------|
| האם 50% נכון? | ❓ לא ידוע | 6 טסטים תלויים בזה |
| צריך להיות 30%? 70%? | ❓ לא ידוע | עשוי לחסום שימושים לגיטימיים |
| האם יש cooldown period? | ❓ לא מוגדר | אין הגנה מפני שינויים רצופים |
| שונה ל-live vs historic? | ❓ לא מוגדר | אולי צריך limits שונים |
| מה קורה כשעוברים? reject? warn? throttle? | ❓ לא מוגדר | לא ברור התנהגות המערכת |

#### 📊 **השפעה:**
- **6 ROI tests** תלויים בערך הזה:
  - `test_dynamic_roi_adjustment.py` - 4 טסטים
  - `test_config_validation_high_priority.py` - 2 טסטים
- עשוי לחסום שימושים לגיטימיים של משתמשים
- עשוי לאפשר שינויים מסוכנים

#### ✅ **פתרון נדרש:**
1. אישור או תיקון של 50%
2. הגדרת cooldown period (אם נדרש)
3. הגדרת limits שונים ל-live/historic (אם נדרש)
4. הגדרת התנהגות כשעוברים limit

---

### 3️⃣ **NFFT Validation - Accepts Anything**

#### 📍 **מיקום בקוד:**
```
File: src/utils/validators.py
Lines: 194-227
Function: validate_nfft_value()
```

#### 📄 **מיקום במסמכים:**
- `CONFLUENCE_SPECS_MEETING.md` - Issue #3 (שורות 125-159)
- `CODE_EVIDENCE_MISSING_SPECS.md` - Example #3 (שורות 82-114)
- `CRITICAL_MISSING_SPECS_LIST.md` - Section 2 (שורות 122-130)

#### ❌ **הבעיה:**
```python
def validate_nfft_value(nfft: int) -> bool:
    """Validate NFFT value (should be power of 2 for efficiency)."""
    
    if not isinstance(nfft, int):
        raise ValidationError("NFFT must be an integer")
    
    if nfft <= 0:
        raise ValidationError("NFFT must be positive")
    
    # Check if power of 2
    is_power_of_2 = (nfft & (nfft - 1)) == 0
    
    if not is_power_of_2:
        warnings.warn(f"NFFT={nfft} not power of 2")  # ⚠️ רק מזהיר!
    
    return True  # ✅ תמיד מחזיר True!
```

**אבל בקובץ Config:**
```yaml
# config/settings.yaml
nfft:
  valid_values: [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
```

**הקוד לא אוכף את הרשימה הזו!**

#### 🎯 **מה חסר בדיוק:**

| שאלה | Status |
|------|--------|
| האם לאכוף את הרשימה מה-config? | ❓ לא ברור |
| או להשאיר warning בלבד? | ❓ לא ברור |
| מהו ה-maximum NFFT? | ❓ לא מוגדר |
| האם משתמש יכול לעקוף עם ערכים custom? | ❓ לא מוגדר |

#### 📊 **השפעה:**
- **6 NFFT tests** לא יכולים לאכוף כללים:
  - `test_validators.py` - NFFT unit tests
  - `test_models_validation.py` - NFFT model tests
  - `test_config_validation_high_priority.py` - NFFT config tests
- ערכי NFFT לא תקינים עלולים לפגוע בביצועים/זיכרון

#### ✅ **פתרון נדרש:**
1. החלטה: האם לאכוף רשימה או להשאיר warning
2. הגדרת absolute maximum
3. הגדרת מדיניות לערכים custom

---

### 4️⃣ **MongoDB Outage - Unknown Behavior**

#### 📍 **מיקום בקוד:**
```
File: tests/integration/infrastructure/test_mongodb_connectivity.py
Lines: Multiple test failures
```

#### 📄 **מיקום במסמכים:**
- `CODE_EVIDENCE_MISSING_SPECS.md` - Example #10 (שורות 296-313)
- `CRITICAL_MISSING_SPECS_LIST.md` - Section 4 (שורות 174-193)
- `documentation/infrastructure/MONGODB_ISSUES_WORKFLOW.md`

#### ❌ **הבעיה:**
```
Test: test_mongodb_scale_down_outage_returns_503
Result: FAILED
Error: AssertionError: Response time 15.423s exceeds maximum 5.0s

Test: test_mongodb_connection_loss_during_live_streaming
Result: FAILED
Error: Expected 503, got 500
```

#### 🎯 **מה חסר בדיוק:**

| שאלה | Status | השפעה |
|------|--------|-------|
| איזה HTTP status כש-MongoDB down? | ❓ לא ידוע | טסט מצפה ל-503, מקבל 500 |
| מה max response time בזמן outage? | ❓ לא ידוע | טסט מצפה ל-5s, מקבל 15s |
| האם live data ממשיך? | ❓ לא ידוע | לא ברור התנהגות |
| האם צריך cache? | ❓ לא ידוע | אין caching כרגע |
| מה recovery time? | ❓ לא ידוע | אין SLA |
| האם יש failover automatic? | ❓ לא ידוע | לא ברור |

#### 📊 **השפעה:**
- **5 MongoDB infrastructure tests** נכשלים
- לא ברור מה ההתנהגות הצפויה במצב של outage
- לא ניתן לבדוק resilience של המערכת

#### ✅ **פתרון נדרש:**
1. הגדרת HTTP status צפוי במצב outage
2. הגדרת max response time
3. הגדרת התנהגות: להמשיך live? לשמור cache?
4. הגדרת recovery SLA

---

### 5️⃣ **SingleChannel View - API Returns 422**

#### 📍 **מיקום בקוד:**
```
File: tests/integration/api/test_singlechannel_view_mapping.py
Lines: 11/13 tests fail
Endpoint: POST /configure
```

#### 📄 **מיקום במסמכים:**
- `documentation/testing/SINGLECHANNEL_TEST_RESULTS.md` (שורות 41-103)
- `BUG_TICKET_SINGLECHANNEL_VIEW_TEMPLATE.md`

#### ❌ **הבעיה:**
```python
def test_singlechannel_basic_happy_path():
    """Test PZ-13732: SingleChannel view basic functionality"""
    
    payload = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 7, "max": 7},  # SingleChannel: min == max
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": null,
        "end_time": null,
        "view_type": 1  # SINGLECHANNEL
    }
    
    response = client.post("/configure", json=payload)
    # Result: HTTP 422 (Unprocessable Entity) ❌
    # Expected: HTTP 200 with ConfigureResponse ✅
```

#### 🎯 **מה חסר בדיוק:**

| שאלה | Status |
|------|--------|
| האם `/configure` endpoint עדיין פעיל? | ❓ לא ידוע |
| אם כן, מה גורם ל-422? | ❓ לא ידוע |
| אם deprecated, מה ה-replacement? | ❓ לא ידוע |
| האם צריך להשתמש ב-`/config/{task_id}`? | ❓ לא ידוע |
| מהו ה-payload format הנכון? | ❓ לא ידוע |

#### 📊 **השפעה:**
- **11/13 SingleChannel tests** נכשלים
- לא ניתן לבדוק SingleChannel view type
- API client method `configure_streaming_job()` לא שמיש

#### ✅ **פתרון נדרש:**
1. בירור סטטוס endpoint
2. תיקון או החלפת endpoint
3. עדכון payload format (אם נדרש)
4. עדכון תיעוד API

---

## 🟠 HIGH PRIORITY ISSUES (חשוב אבל לא חוסם)

### 6️⃣ **Frequency Range - No Absolute Limits**
- **קוד:** `src/models/focus_server_models.py:46-57`
- **מסמכים:** `CONFLUENCE_SPECS_MEETING.md:161-197`
- **חסר:** Max frequency, Min frequency, Min span
- **טסטים:** 16 טסטים

### 7️⃣ **Sensor Range - No Min/Max ROI Size**
- **קוד:** `src/utils/validators.py:116-151`
- **מסמכים:** `CONFLUENCE_SPECS_MEETING.md:199-237`
- **חסר:** Min ROI size, Max ROI size
- **טסטים:** 15 טסטים

### 8️⃣ **RabbitMQ Commands - No Timeouts**
- **קוד:** `src/external/rabbitmq/`
- **מסמכים:** `docs/RABBITMQ_AUTOMATION_GUIDE.md`
- **חסר:** Command timeouts, retry logic
- **טסטים:** 8 טסטים

### 9️⃣ **Waterfall Polling - No Timeout Logic**
- **קוד:** Multiple test files
- **מסמכים:** `CRITICAL_MISSING_SPECS_LIST.md:44-55`
- **חסר:** Max wait time, retry strategy
- **טסטים:** Multiple

### 🔟 **Data Quality Validation - No Limits**
- **קוד:** `src/utils/validators.py:229-324`
- **מסמכים:** `CRITICAL_MISSING_SPECS_LIST.md:70-90`
- **חסר:** Amplitude range, missing data percentage
- **טסטים:** Multiple

---

## 🟡 MEDIUM PRIORITY ISSUES (כדאי לטפל)

### 1️⃣1️⃣ **API Timeouts - Arbitrary Thresholds**
- **קוד:** `tests/integration/api/test_api_endpoints_high_priority.py:135-147`
- **מסמכים:** `CONFLUENCE_SPECS_MEETING.md:239-273`
- **חסר:** SLA לכל endpoint
- **טסטים:** 3 טסטים

### 1️⃣2️⃣ **Config Edge Cases - No Assertions**
- **קוד:** `tests/integration/api/test_config_validation_high_priority.py:475-520`
- **מסמכים:** `CONFLUENCE_SPECS_MEETING.md:275-310`
- **חסר:** התנהגות צפויה כאשר min==max
- **טסטים:** 8 טסטים

### 1️⃣3️⃣ **Live/Historical Threshold - 1 Hour Hardcoded**
- **קוד:** `src/utils/helpers.py:200-220`
- **מסמכים:** `CRITICAL_MISSING_SPECS_LIST.md:195-206`
- **חסר:** אישור ל-1 שעה או ערך אחר
- **טסטים:** -

### 1️⃣4️⃣ **Polling Timeouts - Hardcoded 60s**
- **קוד:** `src/utils/helpers.py:474-504`
- **מסמכים:** `CODE_EVIDENCE_MISSING_SPECS.md:231-259`
- **חסר:** Timeout לכל סוג פעולה
- **טסטים:** Multiple

### 1️⃣5️⃣ **Default Values Mismatch**
- **קוד:** `src/utils/helpers.py:507-532`
- **מסמכים:** `CODE_EVIDENCE_MISSING_SPECS.md:262-293`
- **חסר:** יישור defaults בין code ל-config
- **טסטים:** Multiple

---

## 📝 TODO Comments בקוד

### רשימת כל ה-TODO Comments:

```bash
$ grep -rn "TODO.*spec\|TODO.*threshold\|TODO.*meeting" tests/ src/

tests/integration/api/test_config_validation_high_priority.py:481:
    # TODO: Update assertion after specs meeting

tests/integration/api/test_config_validation_high_priority.py:517:
    # TODO: Update assertion after specs meeting

tests/integration/api/test_api_endpoints_high_priority.py:140:
    # TODO: Update threshold after specs meeting

tests/integration/api/test_api_endpoints_high_priority.py:256:
    # TODO: Update max value after specs meeting

tests/integration/performance/test_performance_high_priority.py:146:
    # TODO: Update thresholds after specs meeting

tests/integration/performance/test_performance_high_priority.py:157:
    # TODO: Uncomment after specs meeting

tests/integration/performance/test_performance_high_priority.py:246:
    # TODO: Update thresholds after specs meeting

tests/integration/performance/test_performance_high_priority.py:370:
    # TODO: Update threshold after specs meeting

tests/integration/performance/test_performance_high_priority.py:529:
    # TODO: Update minimum after specs meeting
```

**סה"כ:** 9 TODO comments מחכים ל-specs

---

## 🔍 איך זוהו החסרים

### מקורות זיהוי:

1. **Grep searches:**
   - TODO comments בקוד
   - Hardcoded values
   - Disabled assertions

2. **Test failures:**
   - MongoDB outage tests
   - SingleChannel view tests
   - Config validation edge cases

3. **Code review:**
   - Validators without limits
   - Models without max values
   - Mismatch between code and config

4. **Documentation review:**
   - API endpoint issues
   - Performance requirements
   - Infrastructure behavior

---

## 📂 מבנה קבצים - היכן למצוא מה

### קבצי קוד מרכזיים עם specs חסרים:

```
src/
├── utils/
│   ├── validators.py .................. ROI 50%, NFFT, Frequency, Sensors
│   └── helpers.py ..................... Polling, Defaults mismatch
├── models/
│   └── focus_server_models.py ......... Frequency max, Time validation
└── apis/
    └── focus_server_api.py ............ API timeouts

tests/
├── integration/
│   ├── performance/
│   │   └── test_performance_high_priority.py ... Performance assertions disabled
│   ├── api/
│   │   ├── test_config_validation_high_priority.py ... Edge cases no assertions
│   │   ├── test_api_endpoints_high_priority.py ..... API timeouts arbitrary
│   │   └── test_singlechannel_view_mapping.py ...... API 422 errors
│   └── infrastructure/
│       └── test_mongodb_connectivity.py ............ MongoDB outage behavior
```

### מסמכי תיעוד:

```
documentation/
├── specs/
│   ├── CRITICAL_MISSING_SPECS_LIST.md ............... רשימה מלאה (200+ specs)
│   ├── CODE_EVIDENCE_MISSING_SPECS.md ............... 10 דוגמאות קוד
│   └── TOP_CODE_LINKS_FOR_SPECS.md .................. Top 3 critical

├── testing/
│   ├── SINGLECHANNEL_TEST_RESULTS.md ................ API endpoint issues
│   └── T_DATA_002_HISTORICAL_VS_LIVE_REPORT.md ...... Live/Historical threshold

├── infrastructure/
│   └── MONGODB_ISSUES_WORKFLOW.md ................... MongoDB behavior

└── CONFLUENCE_SPECS_MEETING.md ...................... מסמך לפגישה (Top 7)
```

---

## 🎯 המלצות לפעולה

### שלב 1: פגישת Specs (2-3 שעות)
**משתתפים:** Dev Lead, Site Manager, Product Owner, QA Lead

**סדר יום:**
1. **חלק א' (60 דקות):** Issues #1-3 (Critical)
   - Performance thresholds
   - ROI 50% confirmation
   - NFFT validation

2. **חלק ב' (45 דקות):** Issues #4-5 (Critical)
   - MongoDB outage behavior
   - SingleChannel API endpoint

3. **חלק ג' (30 דקות):** Issues #6-10 (High)
   - Frequency/Sensor ranges
   - RabbitMQ timeouts
   - Data quality limits

4. **חלק ד' (15 דקות):** תיעדוף והחלטות
   - מה לתקן קודם
   - מה לדחות
   - מה N/A

### שלב 2: תיעוד ההחלטות
- עדכון `config/settings.yaml` עם כל הערכים
- יצירת `SPECS_DECISIONS.md` עם כל ההחלטות
- עדכון Confluence

### שלב 3: עדכון קוד (1-2 שבועות)
**קבצים לעדכן:**

1. **Validators:**
   ```python
   src/utils/validators.py
   - שורה 395: ROI 50% → מ-settings
   - שורה 194-227: NFFT → אכיפת רשימה
   - שורה 116-151: Sensors → min/max ROI
   - שורה 153-191: Frequency → absolute limits
   ```

2. **Performance Tests:**
   ```python
   tests/integration/performance/test_performance_high_priority.py
   - שורה 157: הסרת # מה-assertions
   - שורה 146: עדכון thresholds מ-settings
   ```

3. **Config Validation Tests:**
   ```python
   tests/integration/api/test_config_validation_high_priority.py
   - שורה 481, 517: הוספת assertions
   ```

4. **Settings:**
   ```yaml
   config/settings.yaml
   - הוספת כל הערכים החדשים
   ```

### שלב 4: בדיקה והרצה
- הרצת כל 82+ הטסטים המושפעים
- וידוא שהטסטים עוברים/נכשלים כנדרש
- עדכון Jira Xray

---

## 📊 מדדי הצלחה

### לפני תיקון:
- ❌ 82+ טסטים מושפעים
- ❌ 28 performance tests ללא assertions
- ❌ 9 TODO comments
- ❌ 50+ ערכים hardcoded

### אחרי תיקון:
- ✅ כל הטסטים עם pass/fail criteria ברורים
- ✅ כל ה-performance assertions מופעלים
- ✅ כל ה-TODO comments resolved
- ✅ כל הערכים ב-settings.yaml
- ✅ תיעוד מלא ב-Jira Xray

---

## 📞 איש קשר

**QA Automation Team**  
**מיקום מסמך:** `C:\Projects\focus_server_automation\MISSING_SPECS_COMPREHENSIVE_REPORT.md`  
**תאריך עדכון אחרון:** 22 אוקטובר 2025  

---

**🎯 מוכן לפגישת Specs!**

