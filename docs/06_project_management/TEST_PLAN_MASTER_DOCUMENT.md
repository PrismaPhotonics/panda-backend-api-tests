# 📋 תוכנית בדיקות Focus Server - מסמך מאסטר
## PZ-13756 - ניתוח מקיף ומפורט לפגישה

---

## 🎯 מטרת המסמך

מסמך זה מספק **סקירה מקיפה** של תוכנית הבדיקות ל-Focus Server, כולל:
- ניתוח מפורט של כל טסט
- הסבר על המטרות והנחיצות
- יישום בקוד
- תוכנית עבודה לאוטומציה

**מוכן לפגישה**: המסמך כולל את כל המידע הנדרש כדי להציג ולענות על שאלות.

---

## 🔗 קישורים מהירים

**📚 ניווט למסמכים:**
- 🏠 [INDEX - מפת דרכים מלאה](./INDEX_TEST_PLAN.md)
- 🎤 [PRESENTATION_READY - Slides מוכנות](./PRESENTATION_READY_SUMMARY.md)
- 🔗 [QUICK_LINKS - כל הקישורים](./QUICK_LINKS.md)
- 📖 [README - מדריך שימוש](./README_PRESENTATIONS.md)

**🆕 מסמך מעודכן - גרסה 2.0:**
- 📋 **[FOCUS_SERVER_TEST_PLAN_MASTER.md](./FOCUS_SERVER_TEST_PLAN_MASTER.md)** - Master Test Plan (135+ tests, Production-Ready)

---

## 📚 מבנה התיעוד

המסמך מחולק ל-4 חלקים:

| חלק | תוכן | קובץ |
|------|------|------|
| **חלק 1** | Integration Tests - Historic & Validation | [PART1](./COMPLETE_TEST_PLAN_DETAILED_PART1.md) |
| **חלק 2** | Invalid Ranges, View Types, SingleChannel | [PART2](./COMPLETE_TEST_PLAN_DETAILED_PART2.md) |
| **חלק 3** | Historic Playback, Dynamic ROI, E2E | [PART3](./COMPLETE_TEST_PLAN_DETAILED_PART3.md) |
| **חלק 4** | Infrastructure, Security, סיכום ומילון | [PART4](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md) |

**מסמכים נוספים:**
- [Test_Plan_Analysis_and_Automation_Strategy.md](./Test_Plan_Analysis_and_Automation_Strategy.md) - ניתוח אסטרטגי
- [TEST_JOB_CREATION_STEP_BY_STEP.md](../TEST_JOB_CREATION_STEP_BY_STEP.md) - תהליך יצירת Jobs
- [how_jobs_are_created.md](../how_jobs_are_created.md) - הסבר טכני
- [TEST_COMPARISON_AND_ANALYSIS.md](./TEST_COMPARISON_AND_ANALYSIS.md) - השוואות וניתוח

---

## 📊 סיכום מבנה התוכנית

### סך הכל: **~93 טסטים**

```
┌──────────────────────────────────────────────────────────┐
│                    TEST BREAKDOWN                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Integration Tests (44)                                  │
│  ├─ Config Validation (12)       ████████████ 100%     │
│  ├─ Historic Playback (10)       ██████████   80%      │
│  ├─ Frequency/NFFT (8)           ████████████ 100%     │
│  └─ API Endpoints (14)           ███████████  90%      │
│                                                          │
│  SingleChannel Tests (15)        ████████████ 100%     │
│  │                                                       │
│  ├─ Happy Path (5)                                      │
│  ├─ Edge Cases (5)                                      │
│  └─ Negative Tests (5)                                  │
│                                                          │
│  Dynamic ROI Tests (13)          ████████████ 100%     │
│  │                                                       │
│  ├─ ROI Commands (5)                                    │
│  ├─ Safety Validation (5)                               │
│  └─ Edge Cases (3)                                      │
│                                                          │
│  Infrastructure Tests (6)         ██████     50%       │
│  ├─ SSH (1)                       TODO                  │
│  ├─ Kubernetes (1)                TODO                  │
│  ├─ MongoDB (1)                   TODO                  │
│  └─ Connectivity (3)              ████████ DONE        │
│                                                          │
│  Performance Tests (5)            ████████  60%        │
│  ├─ Latency (2)                   ████ Partial          │
│  ├─ Throughput (2)                ████████ Done         │
│  └─ Load (1)                      ████████ Done         │
│                                                          │
│  Security Tests (2)               ████      40%        │
│  └─ Input Validation (2)          ████ Partial          │
│                                                          │
│  E2E Tests (3)                    ██████    67%        │
│  ├─ Configure→Metadata (1)        ████████ Done         │
│  ├─ gRPC Streaming (1)            ████ Partial          │
│  └─ Full Flow (1)                 ████████ Done         │
│                                                          │
│  Data Quality Tests (5)           ████████████ 100%    │
│  ├─ MongoDB Schema (2)            ████████ Done         │
│  ├─ Collections (1)               ████████ Done         │
│  └─ Metadata Completeness (2)    ████████ Done         │
│                                                          │
└──────────────────────────────────────────────────────────┘

TOTAL AUTOMATION: 77/93 = 83% ████████████████  83%
```

---

## 🔍 טסטים לפי עדיפות

### 🔴 CRITICAL (חייבים לעבור!)

| ID | שם | Status | קובץ | זמן |
|----|-----|--------|------|-----|
| **PZ-13903** | **Nyquist Limit** | ✅ | `test_spectrogram_pipeline.py:127` | 2-3s |
| **PZ-13873** | **Valid Configuration** | ✅ | `test_config_validation_high_priority.py:725` | 3-5s |
| **PZ-13879** | **Missing Required Fields** | ✅ | `test_config_validation_high_priority.py` | 3-5s |
| **PZ-13600** | **Invalid No Orchestration** | ✅ | (קיים) | 2s |

**למה קריטיים?**
- Nyquist → **data integrity** (נתונים מדויקים)
- Valid Config → **basic functionality** (תפקוד בסיסי)
- Missing Fields → **robustness** (חוסן)
- No Orchestration → **safety** (בטיחות)

---

### 🟡 HIGH Priority

| ID | שם | Status | תיאור קצר |
|----|-----|--------|----------|
| PZ-13909 | Historic Missing end_time | TODO | ולידציה של שדות חובה |
| PZ-13907 | Historic Missing start_time | TODO | ולידציה של שדות חובה |
| PZ-13901 | NFFT Variations | ✅ | תמיכה בכל NFFT |
| PZ-13897 | GET /sensors | ✅ | smoke test |
| PZ-13877 | Invalid Freq Range | ✅ | negative test |
| PZ-13876 | Invalid Channel Range | ✅ | negative test |
| PZ-13868 | Status 208 Completion | ✅ | historic completion |
| PZ-13863 | Standard 5-min Range | ✅ | happy path |

---

### 🟢 MEDIUM Priority

| ID | שם | Status | קטגוריה |
|----|-----|--------|----------|
| PZ-13906 | Low Throughput | ✅ | Edge case |
| PZ-13904 | Resource Estimation | ✅ | Performance |
| PZ-13895 | GET /channels | ✅ | API |
| All SingleChannel | ✅ | Functional |
| All Dynamic ROI | ✅ | Integration |

---

## 🎓 למה חילקתי את הטסטים בצורה הזו?

### עקרון החלוקה

**1. לפי Layer (שכבה)**
```
┌─────────────────────────────────────────────┐
│ E2E Tests                                   │ ← מלמעלה למטה
├─────────────────────────────────────────────┤
│ Integration Tests                           │ ← אינטגרציה בין רכיבים
├─────────────────────────────────────────────┤
│ API Tests                                   │ ← endpoints
├─────────────────────────────────────────────┤
│ Unit Tests                                  │ ← פונקציות בודדות
└─────────────────────────────────────────────┘
```

**2. לפי Test Type (סוג)**
```
Functional Tests    → מה המערכת עושה
Performance Tests   → כמה מהר
Security Tests      → כמה בטוח
Data Quality Tests  → כמה מדויק
Infrastructure Tests → האם התשתית עובדת
```

**3. לפי Feature (תכונה)**
```
Historic Playback    → 10 tests
SingleChannel        → 15 tests
Dynamic ROI          → 13 tests
Configuration        → 20 tests
```

**4. לפי Priority (עדיפות)**
```
Critical → פיצ'רים קריטיים (Nyquist, validation)
High     → פונקציונליות עיקרית
Medium   → edge cases
Low      → nice-to-have
```

### למה זה חשוב?

**ארגון לפי Layer:**
- מאפשר **בדיקה הדרגתית** (unit → integration → E2E)
- מזהה **באגים מוקדם** (unit tests ירוצו ראשון)
- **CI/CD** יעיל (לא צריך E2E לכל commit)

**ארגון לפי Feature:**
- **פיתוח מקביל** - צוותים שונים על features שונות
- **Regression testing** - אחרי שינוי ב-ROI, רץ רק ROI tests
- **Debugging** - קל למצוא איפה הבעיה

**ארגון לפי Priority:**
- **Smoke tests** ראשון (Critical)
- **Resource optimization** - לא רצים Low priority בכל build
- **Time management** - אם יש מעט זמן, רצים רק High

---

## 🚀 איך להריץ את הטסטים?

### הרצה מלאה

```bash
# כל הטסטים
pytest tests/ -v

# רק integration
pytest tests/integration/ -v

# רק API tests
pytest -m api -v

# רק critical
pytest -m critical -v
```

### הרצה לפי קטגוריה

```bash
# Historic playback tests
pytest tests/integration/api/test_historic_high_priority.py -v

# SingleChannel tests
pytest tests/integration/api/test_singlechannel_high_priority.py -v

# Dynamic ROI tests
pytest tests/integration/api/test_dynamic_roi_adjustment.py -v

# Configuration validation
pytest tests/integration/api/test_config_validation_high_priority.py -v
```

### הרצה של טסט בודד

```bash
# טסט ספציפי
pytest tests/integration/api/test_spectrogram_pipeline.py::TestFrequencyConfiguration::test_frequency_range_within_nyquist -v

# עם output
pytest tests/integration/api/test_spectrogram_pipeline.py::TestNFFTConfiguration::test_nfft_variations -v -s
```

### הרצה עם markers

```bash
# Critical tests only
pytest -m critical -v

# API tests (not slow)
pytest -m "api and not slow" -v

# Integration + high priority
pytest -m "integration and high_priority" -v

# Smoke tests
pytest -m smoke -v
```

---

## 📈 מדדי איכות

### Test Coverage

**API Endpoints:**
- ✅ POST /configure: 100%
- ✅ GET /waterfall: 95%
- ✅ GET /metadata: 90%
- ✅ GET /sensors: 100%
- ✅ GET /channels: 100%
- ⚠️ POST /recordings_in_time_range: 70%

**Features:**
- ✅ Live Mode: 95%
- ✅ Historic Mode: 90%
- ✅ SingleChannel: 100%
- ✅ Dynamic ROI: 100%
- ⚠️ gRPC Streaming: 60%

**Error Scenarios:**
- ✅ Missing Fields: 100%
- ✅ Invalid Ranges: 100%
- ✅ Invalid Values: 95%
- ⚠️ Timeout Handling: 70%
- ⚠️ Connection Errors: 75%

---

## 🎤 נקודות להצגה בפגישה

### Opening (פתיחה)

```
"יצרנו תוכנית בדיקות מקיפה ל-Focus Server עם 93 טסטים.

83% מהטסטים כבר ממומשים ופועלים.

התוכנית מכסה:
- ✅ תפקוד בסיסי (Happy Path)
- ✅ ולידציות (Negative Tests)
- ✅ ביצועים (Performance)
- ✅ יציבות (Stability)
- ✅ איכות נתונים (Data Quality)
"
```

### Structure (מבנה)

```
"חילקנו את הטסטים ל-7 קטגוריות:

1. Integration Tests (44) - אינטגרציה בין רכיבים
2. SingleChannel Tests (15) - תצוגת sensor בודד
3. Dynamic ROI Tests (13) - שינוי ROI בזמן אמת
4. Infrastructure Tests (6) - תשתית
5. Performance Tests (5) - ביצועים
6. Security Tests (2) - אבטחה
7. Data Quality Tests (5) - איכות נתונים

הארגון הזה מאפשר:
- בדיקה מדורגת (Unit → Integration → E2E)
- פיתוח מקביל (צוותים שונים על features שונות)
- CI/CD יעיל (רק הטסטים הרלוונטיים)
"
```

### Critical Tests (טסטים קריטיים)

```
"הטסט הכי חשוב: Nyquist Limit Enforcement (PZ-13903)

למה? כי זה לא רק תוכנה - זה פיזיקה!

אם לא נאכוף את גבול Nyquist:
❌ הנתונים יתעוותו (Aliasing)
❌ תדרים גבוהים יופיעו כתדרים נמוכים
❌ מדידות שגויות → החלטות מסוכנות

הטסט הזה:
✅ מוציא PRR מהמערכת
✅ מחשב Nyquist = PRR/2
✅ דוחה תדרים מעל Nyquist
✅ מגן על שלמות הנתונים

זמן ריצה: 2-3 שניות
Status: ✅ ממומש ועובד
"
```

### Automation Status (מצב אוטומציה)

```
"מתוך 93 טסטים:
✅ 77 ממומשים (83%)
⏳ 16 בתכנון (17%)

הפרדה:
- Integration: 80% ממומש
- SingleChannel: 100% ממומש ✅
- Dynamic ROI: 100% ממומש ✅
- Infrastructure: 50% ממומש
- Performance: 60% ממומש
- Security: 40% ממומש
- E2E: 67% ממומש

הטסטים הקריטיים: 100% ממומש ✅
"
```

### Implementation Details (פרטי יישום)

```
"כל טסט ממומש ב:
- Pytest 7.0+
- Python 3.11+
- Production-grade code

Structure:
tests/
├── integration/
│   ├── api/           (40+ tests)
│   └── performance/   (5 tests)
├── infrastructure/    (6 tests)
├── unit/              (10 tests)
└── data_quality/      (5 tests)

כל טסט כולל:
✅ Docstrings מפורטים
✅ Logging מקיף
✅ Error handling
✅ Assertions ברורות
✅ Cleanup אוטומטי
"
```

### Work Plan (תוכנית עבודה)

```
"תוכנית להשלמת 17% הנותרים:

Phase 1 (2-3 weeks): High Priority Integration
├─ PZ-13909: Historic Missing end_time
├─ PZ-13907: Historic Missing start_time
└─ Historic validation suite

Phase 2 (1-2 weeks): Infrastructure
├─ PZ-13900: SSH Access
├─ PZ-13899: Kubernetes Health
└─ PZ-13898: MongoDB Health

Phase 3 (1 week): Security Hardening
└─ PZ-13572: Complete security tests

Phase 4 (1 week): Performance Baseline
└─ PZ-13571: Latency benchmarks

Total Time: 5-7 weeks
Resources: 1 QA Engineer
"
```

---

## 💡 שאלות צפויות ותשובות

### Q1: "למה 83% ולא 100%?"

**A**:
```
התמקדנו ב-Critical ו-High priority ראשון.

✅ כל הטסטים הקריטיים ממומשים (100%)
✅ רוב ה-High priority ממומשים (85%)
⏳ Medium ו-Low בתכנון (50%)

הגישה: Value-driven development
→ הטסטים החשובים ביותר קודם
```

### Q2: "כמה זמן לוקח להריץ הכל?"

**A**:
```
Fast Suite (Critical + Smoke): ~5 דקות
Full Suite (כל הטסטים): ~15-20 דקות
Nightly Suite (כולל E2E ארוכים): ~60 דקות

אסטרטגיה:
- Pre-commit: Unit tests (~30s)
- PR: Fast Suite (~5m)
- Post-merge: Full Suite (~20m)
- Nightly: Everything (~60m)
```

### Q3: "מה אם טסט נכשל?"

**A**:
```
כל טסט כולל:
1. Detailed logging - לוגים מפורטים של כל צעד
2. Screenshots (אם רלוונטי)
3. Error messages ברורות
4. Stack traces
5. Environment info

דוגמה:
FAILED test_nyquist_limit
├─ Error: Frequency (600 Hz) exceeds Nyquist (500 Hz)
├─ PRR: 1000 samples/sec
├─ Nyquist calculated: 500 Hz
├─ Requested: 600 Hz
└─ Expected: Rejection with HTTP 400

זה מאפשר debug מהיר!
```

### Q4: "איך מוודאים ש-tests נכונים?"

**A**:
```
כל טסט עובר peer review:
✅ Code review
✅ Test data validation
✅ Expected results documented
✅ Manual verification (פעם ראשונה)

בנוסף:
- Self-verification: הטסט בודק את עצמו
- Negative tests: מוודאים שהשרת דוחה inputs לא תקפים
- Comparison: התוצאות משוים למסמכי דרישות
```

### Q5: "מה לגבי False Positives?"

**A**:
```
מניעת False Positives:
1. Assertions ספציפיות (לא כלליות)
2. Timeouts סבירים (לא קצרים מדי)
3. Retry logic (לbאגים ארעיים ברשת)
4. Environment validation (לפני הטסטים)
5. Cleanup בין טסטים (לא state sharing)

דוגמה:
# ❌ BAD (False Positive prone)
assert response is not None

# ✅ GOOD (Specific)
assert response.status_code == 200
assert response.job_id is not None
assert len(response.job_id) > 0
```

---

## 📖 Quick Reference - טסטים עיקריים

### Must-Know Tests (לפגישה)

| ID | שם | מטרה במשפט אחד |
|----|-----|----------------|
| **PZ-13903** | Nyquist Limit | מונע aliasing - הטסט הכי חשוב לאיכות נתונים |
| **PZ-13873** | Valid Configuration | Happy path - מוודא שהמערכת עובדת |
| **PZ-13901** | NFFT Variations | מוודא תמיכה בכל ערכי NFFT |
| **PZ-13863** | Historic 5-min | בודק historic playback סטנדרטי |
| **PZ-13868** | Status 208 | מוודא שהיסטורי נסגר נכון |
| **PZ-13879** | Missing Fields | מוודא ולידציה של שדות חובה |
| **PZ-13784** | ROI via RabbitMQ | בודק dynamic ROI commands |

---

## 🔧 כלי עבודה

### Pytest Configuration

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    integration: Integration tests
    api: API endpoint tests
    critical: Critical functionality tests
    smoke: Smoke tests
    slow: Tests that take > 10 seconds
    negative: Negative test cases

log_cli = true
log_cli_level = INFO
```

### Test Fixtures

**conftest.py:**
```python
@pytest.fixture(scope="session")
def config_manager():
    """Load configuration once per session."""
    return ConfigManager()

@pytest.fixture(scope="function")
def focus_server_api(config_manager):
    """Create API client for each test."""
    return FocusServerAPI(config_manager)

@pytest.fixture(scope="function")
def baby_analyzer_mq_client(config_manager):
    """Create RabbitMQ client for each test."""
    client = BabyAnalyzerMQClient(config_manager)
    client.connect()
    yield client
    client.disconnect()
```

---

## 📝 Checklist לפגישה

### לפני הפגישה

- [x] קרא את כל המסמכים
- [x] הבן כל טסט
- [x] הכן דוגמאות קוד
- [x] הכן תשובות לשאלות נפוצות
- [ ] הרץ את הטסטים (demo)
- [ ] הכן screenshots של תוצאות
- [ ] הכן demo של failed test
- [ ] בדוק שה-environment עובד

### במהלך הפגישה

- [ ] הצג את המבנה הכללי
- [ ] הסבר את החלוקה לקטגוריות
- [ ] הדגם טסט קריטי (Nyquist)
- [ ] הצג קוד (דוגמה)
- [ ] הסבר תוכנית עבודה
- [ ] ענה על שאלות

### אחרי הפגישה

- [ ] תעד החלטות
- [ ] עדכן priorities
- [ ] תכנן Phase הבא
- [ ] שתף סיכום עם הצוות

---

## 🎯 Key Takeaways

1. **83% Automation** - רוב הטסטים מוכנים
2. **100% Critical Coverage** - כל הקריטיים ממומשים
3. **Clean Architecture** - קוד מאורגן ונקי
4. **Production-Ready** - ברמה גבוהה
5. **Comprehensive** - מכסה כל המערכת

**Bottom Line:**
```
המערכת נבדקת היטב, הקוד איכותי, והטסטים מקיפים.
יש 17% להשלים, אבל כל החלקים הקריטיים פועלים.
```

---

## 📞 נקודות קשר

**Documentation:**
- חלק 1: Integration & Historic → `COMPLETE_TEST_PLAN_DETAILED_PART1.md`
- חלק 2: Ranges & SingleChannel → `COMPLETE_TEST_PLAN_DETAILED_PART2.md`
- חלק 3: Historic & ROI → `COMPLETE_TEST_PLAN_DETAILED_PART3.md`
- חלק 4: Infrastructure & Summary → `COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md`

**Code:**
- Tests: `tests/integration/api/`
- Models: `src/models/focus_server_models.py`
- API Client: `src/apis/focus_server_api.py`
- Utilities: `src/utils/`

---

*מסמך זה מהווה את ה-Master Document לכל תוכנית הבדיקות*

**נוצר**: 27 אוקטובר 2025  
**עודכן**: 29 אוקטובר 2025  
**גרסה**: 1.0  
**מחבר**: Roy Avrahami  
**Jira Epic**: PZ-13756

---

## 📝 הערה חשובה

**גרסה מעודכנת זמינה:**
המסמך **[FOCUS_SERVER_TEST_PLAN_MASTER.md](./FOCUS_SERVER_TEST_PLAN_MASTER.md)** מכיל עדכון מלא עם:
- ✅ **135+ טסטים** (מעודכן מ-93)
- ✅ **8 קטגוריות עיקריות** עם פירוט מלא
- ✅ **סטטוס Production-Ready** מפורט
- ✅ **באגים שגילו** (4 ממצאים קריטיים)
- ✅ **מדדי איכות** ועדכוני ביצועים

מומלץ לעיין במסמך המעודכן למידע עדכני ומקיף יותר.

