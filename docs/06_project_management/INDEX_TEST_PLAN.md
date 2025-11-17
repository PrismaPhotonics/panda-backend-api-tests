# 📚 אינדקס מרכזי - תוכנית בדיקות Focus Server
## PZ-13756 - מדריך מלא לתיעוד

---

## 🎯 סקירה מהירה

נוצרה תוכנית בדיקות **מקיפה** ל-Focus Server עם **93 טסטים**.

**סטטוס אוטומציה**: 77/93 (83%) ✅

**מסמכים**: 8 מסמכים מפורטים

---

## 📋 מסמכים - Quick Links

### 🔴 מסמך מאסטר (התחל כאן!)

**📄 [TEST_PLAN_MASTER_DOCUMENT.md](./TEST_PLAN_MASTER_DOCUMENT.md)**

זה המסמך המרכזי שכולל:
- סיכום כללי
- סטטיסטיקות
- נקודות להצגה
- שאלות ותשובות
- Checklist לפגישה

**🕐 זמן קריאה**: 10 דקות  
**📌 מומלץ**: קרא קודם כל!

---

### 📘 מסמכים מפורטים (לפי נושא)

#### Part 1: Integration Tests - Historic & Validation
**📄 [COMPLETE_TEST_PLAN_DETAILED_PART1.md](./COMPLETE_TEST_PLAN_DETAILED_PART1.md)**

**תוכן:**
- TEST #1: Historic Missing end_time (PZ-13909)
- TEST #2: Historic Missing start_time (PZ-13907)
- TEST #3: Low Throughput (PZ-13906)
- TEST #4: Resource Estimation (PZ-13904)
- TEST #5: **Nyquist Limit** (PZ-13903) ← קריטי!
- TEST #6: NFFT Variations (PZ-13901)
- TEST #7: GET /sensors (PZ-13897)
- TEST #8: Missing Required Fields (PZ-13879)

**🕐 זמן קריאה**: 20 דקות  
**📌 חשיבות**: גבוהה - כולל טסטים קריטיים

---

#### Part 2: Invalid Ranges & SingleChannel
**📄 [COMPLETE_TEST_PLAN_DETAILED_PART2.md](./COMPLETE_TEST_PLAN_DETAILED_PART2.md)**

**תוכן:**
- TEST #9: Invalid Frequency Range (PZ-13877)
- TEST #10: Invalid Channel Range (PZ-13876)
- TEST #11: Valid Configuration (PZ-13873)
- TEST #12-20: SingleChannel Suite
  - Minimum Channel (0)
  - Maximum Channel
  - Middle Channel
  - Invalid Channels (negative, out of range)

**🕐 זמן קריאה**: 15 דקות  
**📌 חשיבות**: בינונית-גבוהה

---

#### Part 3: Historic Playback & Dynamic ROI
**📄 [COMPLETE_TEST_PLAN_DETAILED_PART3.md](./COMPLETE_TEST_PLAN_DETAILED_PART3.md)**

**תוכן:**
- Historic Playback Tests
  - 5-Minute Standard Range (PZ-13863)
  - Status 208 Completion (PZ-13868)
  - Invalid Time Ranges (PZ-13869)
  - Timestamp Ordering (PZ-13871)
- Dynamic ROI Tests (13 tests)
  - ROI Commands via RabbitMQ
  - Safety Validation
  - Edge Cases
- E2E Tests

**🕐 זמן קריאה**: 25 דקות  
**📌 חשיבות**: גבוהה

---

#### Part 4: Infrastructure, Security & Summary
**📄 [COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md)**

**תוכן:**
- Infrastructure Tests
  - SSH Access (PZ-13900)
  - Kubernetes Health (PZ-13899)
  - MongoDB Connection (PZ-13898)
- Security Tests
  - Malformed Inputs (PZ-13572)
- מילון מושגים מקיף
- סיכום סופי

**🕐 זמן קריאה**: 20 דקות  
**📌 חשיבות**: בינונית

---

### 📗 מסמכים משלימים

#### אסטרטגיה ותכנון
**📄 [Test_Plan_Analysis_and_Automation_Strategy.md](./Test_Plan_Analysis_and_Automation_Strategy.md)**

תוכן:
- ניתוח תוכנית הבדיקות
- סיכום קטגוריות
- מטרות הבדיקות
- תוכנית עבודה לאוטומציה
- מילון מושגים בסיסי

**🕐 זמן קריאה**: 15 דקות  
**📌 שימוש**: תכנון אסטרטגי

---

#### תהליך יצירת Jobs
**📄 [TEST_JOB_CREATION_STEP_BY_STEP.md](../TEST_JOB_CREATION_STEP_BY_STEP.md)**

תוכן:
- תהליך יצירת Job צעד-אחר-צעד
- דוגמאות קוד מלאות
- תרשימי זרימה
- מה קורה בצד השרת

**🕐 זמן קריאה**: 10 דקות  
**📌 שימוש**: הבנה טכנית

---

#### איך נוצרים Jobs בקוד
**📄 [how_jobs_are_created.md](../how_jobs_are_created.md)**

תוכן:
- הסבר טכני על יצירת Jobs
- פונקציות מרכזיות
- דוגמאות מהקוד
- תהליכים פנימיים

**🕐 זמן קריאה**: 8 דקות  
**📌 שימוש**: deep dive טכני

---

## 🗺️ מפת קריאה מומלצת

### תרחיש 1: הכנה לפגישה (30 דקות)

```
1. קרא: TEST_PLAN_MASTER_DOCUMENT.md (10 min)
   ↓
2. קרא: COMPLETE_TEST_PLAN_DETAILED_PART1.md - רק Critical tests (10 min)
   ↓
3. קרא: TEST_PLAN_MASTER_DOCUMENT.md - "נקודות להצגה" (5 min)
   ↓
4. עבור על: "שאלות צפויות ותשובות" (5 min)
   ↓
✅ מוכן לפגישה!
```

---

### תרחיש 2: הבנה מעמיקה (2 שעות)

```
1. TEST_PLAN_MASTER_DOCUMENT.md (קריאה מלאה)
   ↓
2. COMPLETE_TEST_PLAN_DETAILED_PART1.md (קריאה מלאה)
   ↓
3. COMPLETE_TEST_PLAN_DETAILED_PART2.md (קריאה מלאה)
   ↓
4. COMPLETE_TEST_PLAN_DETAILED_PART3.md (קריאה מלאה)
   ↓
5. COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md (מילון מושגים)
   ↓
6. TEST_JOB_CREATION_STEP_BY_STEP.md (תהליכים)
   ↓
✅ הבנה מלאה!
```

---

### תרחיש 3: יישום טסט חדש (45 דקות)

```
1. TEST_PLAN_MASTER_DOCUMENT.md - סעיף "Work Plan"
   ↓
2. COMPLETE_TEST_PLAN_DETAILED_PART1.md - מצא טסט דומה
   ↓
3. how_jobs_are_created.md - הבן איך ליצור job
   ↓
4. העתק קוד מטסט דומה
   ↓
5. התאם לצרכים
   ↓
✅ טסט חדש מוכן!
```

---

## 📊 סטטיסטיקות מהירות

### לפי קטגוריה

```
Integration Tests:    44 tests (80% done)   ████████████████
SingleChannel Tests:  15 tests (100% done)  ████████████████████
Dynamic ROI Tests:    13 tests (100% done)  ████████████████████
Infrastructure:        6 tests (50% done)   ██████████
Performance Tests:     5 tests (60% done)   ████████████
Security Tests:        2 tests (40% done)   ████████
E2E Tests:             3 tests (67% done)   █████████████
Data Quality Tests:    5 tests (100% done)  ████████████████████

TOTAL:                93 tests (83% done)   ████████████████
```

### לפי priority

```
Critical:  4 tests  (100% done) ████████████████████ ✅
High:     35 tests  (85% done)  █████████████████
Medium:   40 tests  (80% done)  ████████████████
Low:      14 tests  (70% done)  ██████████████
```

### לפי status

```
✅ Implemented:  77 tests (83%)
⏳ TODO:         16 tests (17%)
```

---

## 🔍 חיפוש מהיר

### לפי Test ID

| טסט ID | מסמך | עמוד/סעיף |
|--------|------|-----------|
| PZ-13909 | Part 1 | TEST #1 |
| PZ-13907 | Part 1 | TEST #2 |
| PZ-13906 | Part 1 | TEST #3 |
| PZ-13904 | Part 1 | TEST #4 |
| **PZ-13903** | **Part 1** | **TEST #5** (קריטי!) |
| PZ-13901 | Part 1 | TEST #6 |
| PZ-13897 | Part 1 | TEST #7 |
| PZ-13879 | Part 1 | TEST #8 |
| PZ-13877 | Part 2 | TEST #9 |
| PZ-13876 | Part 2 | TEST #10 |
| PZ-13873 | Part 2 | TEST #11 |
| PZ-13832-62 | Part 2 | TEST #12-20 (SingleChannel) |
| PZ-13863-72 | Part 3 | Historic Playback |
| PZ-13784-805 | Part 3 | Dynamic ROI |
| PZ-13900-98 | Part 4 | Infrastructure |
| PZ-13572 | Part 4 | Security |

---

### לפי נושא

| נושא | איפה למצוא |
|------|-----------|
| **Nyquist Validation** | Part 1, TEST #5 |
| **NFFT Values** | Part 1, TEST #6 |
| **Missing Fields** | Part 1, TEST #8 |
| **Invalid Ranges** | Part 2, TEST #9-10 |
| **Valid Configuration** | Part 2, TEST #11 |
| **SingleChannel** | Part 2, TEST #12-20 |
| **Historic Playback** | Part 3, Historic section |
| **Dynamic ROI** | Part 3, ROI section |
| **Infrastructure** | Part 4, Infrastructure section |
| **Security** | Part 4, Security section |
| **מילון מושגים** | Part 4, Glossary |

---

### לפי קוד

| Function/File | מסמך | תיאור |
|---------------|------|-------|
| `generate_task_id()` | how_jobs_are_created.md | יצירת ID |
| `configure_streaming_job()` | TEST_JOB_CREATION | שליחת config |
| `validate_roi_change_safety()` | Part 3 | ROI validation |
| `validate_configuration_compatibility()` | Part 1, TEST #4 | Resource estimation |
| `test_frequency_range_within_nyquist` | Part 1, TEST #5 | Nyquist test |
| `test_nfft_variations` | Part 1, TEST #6 | NFFT test |

---

## 💡 טיפים לשימוש

### עבור פגישת Kickoff
→ קרא: **TEST_PLAN_MASTER_DOCUMENT.md**

### עבור סקירת טסט ספציפי
→ חפש ב-INDEX לפי Test ID → קפוץ למסמך המתאים

### עבור הבנת תהליכים
→ קרא: **TEST_JOB_CREATION_STEP_BY_STEP.md**

### עבור יישום טסט חדש
→ קרא: **how_jobs_are_created.md** + דוגמה מ-Part 1-3

### עבור הסבר מונח טכני
→ Part 4: **מילון מושגים**

---

## 🎬 Getting Started

### קריאה ראשונית (15 דקות)

1. פתח: `TEST_PLAN_MASTER_DOCUMENT.md`
2. קרא: "סיכום מבנה התוכנית"
3. קרא: "טסטים לפי עדיפות" → Critical tests
4. קרא: "נקודות להצגה בפגישה"

### העמקה (1 שעה)

1. קרא: Part 1 (Integration & Historic)
2. התמקד ב-TEST #5 (Nyquist) - הכי חשוב!
3. דלג על Part 2-3
4. קרא: Part 4 - מילון מושגים

### מומחיות מלאה (4 שעות)

1. קרא את כל 4 החלקים לפי הסדר
2. קרא את המסמכים המשלימים
3. עבור על דוגמאות הקוד
4. הרץ טסטים (hands-on)

---

## 📖 מילון קיצורים

| קיצור | משמעות | הסבר |
|-------|---------|------|
| **NFFT** | Number of FFT Points | גודל ה-FFT |
| **PRR** | Pulse Repetition Rate | קצב דגימה |
| **ROI** | Region of Interest | טווח sensors |
| **CAxis** | Color Axis | טווח colormap |
| **E2E** | End-to-End | מקצה לקצה |
| **API** | Application Programming Interface | ממשק תכנות |
| **SSH** | Secure Shell | גישה מרחוק |
| **K8s** | Kubernetes | אורכיסטרציה |
| **MQ** | Message Queue | תור הודעות |
| **DB** | Database | מסד נתונים |

---

## 🎯 מטרות לפי מסמך

| מסמך | מטרה |
|------|------|
| **Master** | סקירה כוללת + הצגה |
| **Part 1** | טסטים קריטיים + integration |
| **Part 2** | validation + SingleChannel |
| **Part 3** | Historic + ROI בפירוט |
| **Part 4** | Infrastructure + מילון |
| **Strategy** | תכנון ואסטרטגיה |
| **Job Creation** | הבנה טכנית |

---

## ✅ Checklist שימושי

### הכנה לפגישה

- [x] קרא Master Document
- [x] הבן טסטים קריטיים
- [x] הכן דוגמאות
- [ ] הרץ טסטים (demo)
- [ ] הכן slides (אופציונלי)

### יישום טסט חדש

- [ ] קרא טסט דומה במסמכים
- [ ] הבן את המטרה
- [ ] העתק template
- [ ] התאם לצרכים
- [ ] כתוב assertions
- [ ] הרץ ובדוק
- [ ] תעד

### Code Review

- [ ] קוד עומד בstandards
- [ ] Docstrings מלאים
- [ ] Assertions ספציפיות
- [ ] Logging מקיף
- [ ] Error handling
- [ ] Cleanup

---

## 📞 איך להשתמש במסמכים?

### אני רוצה...

**...להבין את התוכנית הכוללת**
→ `TEST_PLAN_MASTER_DOCUMENT.md`

**...לקרוא על טסט ספציפי**
→ חפש את ה-Test ID באינדקס → קפוץ למסמך

**...להבין איך נוצר Job**
→ `TEST_JOB_CREATION_STEP_BY_STEP.md`

**...להבין מונח טכני**
→ `COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md` - מילון

**...לדעת מה TODO**
→ `TEST_PLAN_MASTER_DOCUMENT.md` - Work Plan

**...לראות דוגמת קוד**
→ כל המסמכים המפורטים (Part 1-3) כוללים קוד

**...להבין למה חילקתי ככה**
→ `TEST_PLAN_MASTER_DOCUMENT.md` - "למה חילקתי בצורה הזו"

---

## 🚀 Quick Commands

### הרצת טסטים

```bash
# הכל
pytest tests/ -v

# רק Critical
pytest -m critical -v

# רק Integration
pytest tests/integration/ -v

# טסט ספציפי
pytest tests/integration/api/test_spectrogram_pipeline.py::TestFrequencyConfiguration::test_frequency_range_within_nyquist -v
```

---

## 📈 Progress Tracking

### Implemented (77/93)

```
✅ Integration:      35/44  (80%)
✅ SingleChannel:    15/15 (100%)
✅ Dynamic ROI:      13/13 (100%)
✅ Data Quality:      5/5  (100%)
⚠️  Infrastructure:   3/6   (50%)
⚠️  Performance:      3/5   (60%)
⚠️  Security:         1/2   (50%)
⚠️  E2E:              2/3   (67%)
```

### TODO (16/93)

**Phase 1 (High Priority):**
- PZ-13909: Historic Missing end_time
- PZ-13907: Historic Missing start_time

**Phase 2 (Infrastructure):**
- PZ-13900: SSH Access
- PZ-13899: Kubernetes Health
- PZ-13898: MongoDB Connection

**Phase 3 (Others):**
- Performance baselines
- Security hardening
- gRPC E2E

---

## 🎓 מושגי מפתח (חייבים לדעת!)

| מושג | הגדרה קצרה | חשיבות |
|------|-----------|---------|
| **NFFT** | גודל FFT (128-4096) | ⭐⭐⭐ |
| **Nyquist** | PRR/2 - גבול תדר | ⭐⭐⭐ קריטי! |
| **PRR** | קצב דגימה (samples/sec) | ⭐⭐⭐ |
| **ROI** | טווח sensors | ⭐⭐⭐ |
| **Throughput** | תפוקת נתונים (Mbps) | ⭐⭐ |
| **View Type** | 0=MULTI, 1=SINGLE | ⭐⭐ |
| **Status 208** | Historic complete | ⭐⭐⭐ |
| **yymmddHHMMSS** | פורמט זמן | ⭐⭐ |

---

## 📞 Contact & Support

**מחבר**: Roy Avrahami  
**Jira Epic**: PZ-13756  
**Repository**: `C:\Projects\focus_server_automation`

**קבצי קוד מרכזיים:**
- `tests/integration/api/test_config_validation_high_priority.py`
- `tests/integration/api/test_spectrogram_pipeline.py`
- `tests/integration/api/test_historic_high_priority.py`
- `src/apis/focus_server_api.py`
- `src/utils/helpers.py`

---

## 🎉 סיכום

**יצרת:**
- 📚 8 מסמכי תיעוד מקיפים
- 💻 83% אוטומציה (77/93 tests)
- 🎯 100% Critical tests
- 📊 ניתוח מפורט של כל טסט

**אתה מוכן:**
- ✅ להציג בפגישה
- ✅ לענות על שאלות
- ✅ להסביר את החלוקה
- ✅ להדגים קוד

---

*מסמך זה הוא ה-Gateway לכל התיעוד*

**עדכון אחרון**: 27 אוקטובר 2025  
**גרסה**: 1.0

