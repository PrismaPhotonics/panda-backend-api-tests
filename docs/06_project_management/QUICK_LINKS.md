# 🔗 קישורים מהירים - תוכנית בדיקות Focus Server
## Quick Navigation Guide

---

## 🚀 התחל כאן!

### ⭐ Top 3 מסמכים (קרא אלה קודם!)

1. **[INDEX_TEST_PLAN.md](./INDEX_TEST_PLAN.md)** ← התחל כאן!
   - מפת דרכים מלאה
   - Quick links לכל טסט
   - 5 דקות קריאה

2. **[TEST_PLAN_MASTER_DOCUMENT.md](./TEST_PLAN_MASTER_DOCUMENT.md)** ← מוכן לפגישה!
   - סיכום מלא
   - נקודות להצגה
   - שאלות ותשובות
   - 10 דקות קריאה

3. **[PRESENTATION_READY_SUMMARY.md](./PRESENTATION_READY_SUMMARY.md)** ← Slides מוכנות!
   - Bullet points
   - Talking points
   - Slides מעוצבות
   - 10 דקות קריאה

---

## 📘 מסמכים מפורטים (Deep Dive)

### חלק 1: Integration & Historic Tests
**[COMPLETE_TEST_PLAN_DETAILED_PART1.md](./COMPLETE_TEST_PLAN_DETAILED_PART1.md)**

טסטים:
- [TEST #1: Historic Missing end_time](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-1-historic-configuration-missing-end_time-field) (PZ-13909)
- [TEST #2: Historic Missing start_time](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-2-historic-configuration-missing-start_time-field) (PZ-13907)
- [TEST #3: Low Throughput](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-3-low-throughput-configuration-edge-case) (PZ-13906)
- [TEST #4: Resource Estimation](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-4-configuration-resource-usage-estimation) (PZ-13904)
- **[TEST #5: Nyquist Limit](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-5-frequency-range-nyquist-limit-enforcement)** ⭐ קריטי! (PZ-13903)
- [TEST #6: NFFT Variations](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-6-nfft-values-validation---all-supported-values) (PZ-13901)
- [TEST #7: GET /sensors](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-7-get-sensors---retrieve-available-sensors-list) (PZ-13897)
- [TEST #8: Missing Fields](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-8-missing-required-fields) (PZ-13879)

⏱️ 20 דקות קריאה

---

### חלק 2: Invalid Ranges & SingleChannel
**[COMPLETE_TEST_PLAN_DETAILED_PART2.md](./COMPLETE_TEST_PLAN_DETAILED_PART2.md)**

טסטים:
- [TEST #9: Invalid Frequency Range](./COMPLETE_TEST_PLAN_DETAILED_PART2.md#test-9-invalid-frequency-range---min--max) (PZ-13877)
- [TEST #10: Invalid Channel Range](./COMPLETE_TEST_PLAN_DETAILED_PART2.md#test-10-invalid-channel-range---min--max) (PZ-13876)
- [TEST #11: Valid Configuration](./COMPLETE_TEST_PLAN_DETAILED_PART2.md#test-11-valid-configuration---all-parameters) (PZ-13873)
- [TEST #12-20: SingleChannel Suite](./COMPLETE_TEST_PLAN_DETAILED_PART2.md#test-12-20-singlechannel-tests-suite)

⏱️ 15 דקות קריאה

---

### חלק 3: Historic Playback & Dynamic ROI
**[COMPLETE_TEST_PLAN_DETAILED_PART3.md](./COMPLETE_TEST_PLAN_DETAILED_PART3.md)**

טסטים:
- [Historic Playback Overview](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#historic-playback-tests---סקירה)
- [TEST #23: Historic 5-min Range](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#test-23-historic-playback---standard-5-minute-range) (PZ-13863)
- [TEST #24: Status 208 Completion](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#test-24-historic-playback---status-208-completion) (PZ-13868)
- [Dynamic ROI Overview](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#dynamic-roi-tests---סקירה)
- [TEST #26: ROI via RabbitMQ](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#test-26-send-roi-change-command-via-rabbitmq) (PZ-13784)
- [E2E Test](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#e2e-test-configure--metadata--grpc) (PZ-13570)

⏱️ 25 דקות קריאה

---

### חלק 4: Infrastructure & מילון
**[COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md)**

תוכן:
- [Infrastructure Tests](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#infrastructure-tests)
- [Security Tests](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#security-tests)
- [מילון מושגים מקיף](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#מילון-מושגים-טכניים---מקיף) ⭐
- [סיכום סופי](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#סיכום-סופי-של-כל-הטסטים)

⏱️ 20 דקות קריאה

---

## 🔧 מסמכים טכניים

### איך נוצרים Jobs?
**[TEST_JOB_CREATION_STEP_BY_STEP.md](../TEST_JOB_CREATION_STEP_BY_STEP.md)**
- תהליך מפורט ב-6 שלבים
- דוגמאות קוד
- תרשימי זרימה

**[how_jobs_are_created.md](../how_jobs_are_created.md)**
- הסבר טכני
- פונקציות מרכזיות

---

### ניתוח והשוואה
**[TEST_COMPARISON_AND_ANALYSIS.md](./TEST_COMPARISON_AND_ANALYSIS.md)**
- השוואות בין טסטים
- Dependencies matrix
- Gap analysis

**[Test_Plan_Analysis_and_Automation_Strategy.md](./Test_Plan_Analysis_and_Automation_Strategy.md)**
- אסטרטגיה כוללת
- תוכנית אוטומציה

---

## 📖 מדריכים

**[README_PRESENTATIONS.md](./README_PRESENTATIONS.md)**
- מדריך לשימוש במסמכים
- מסלולי קריאה
- טיפים

---

## 🎯 קישורים לפי מטרה

### אני רוצה...

**...להתכונן לפגישה** (30 דקות)
1. [INDEX_TEST_PLAN.md](./INDEX_TEST_PLAN.md)
2. [TEST_PLAN_MASTER_DOCUMENT.md](./TEST_PLAN_MASTER_DOCUMENT.md)
3. [PRESENTATION_READY_SUMMARY.md](./PRESENTATION_READY_SUMMARY.md)

---

**...להבין טסט ספציפי**
1. חפש ב-[INDEX](./INDEX_TEST_PLAN.md#חיפוש-מהיר) את ה-Test ID
2. קפוץ למסמך המתאים (PART 1-4)

---

**...להבין Nyquist** ⭐
→ [PART 1, TEST #5](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-5-frequency-range-nyquist-limit-enforcement)

---

**...להבין SingleChannel**
→ [PART 2, TEST #12-20](./COMPLETE_TEST_PLAN_DETAILED_PART2.md#test-12-20-singlechannel-tests-suite)

---

**...להבין Historic Playback**
→ [PART 3, Historic Section](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#historic-playback-tests---סקירה)

---

**...להבין Dynamic ROI**
→ [PART 3, ROI Section](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#dynamic-roi-tests---סקירה)

---

**...הסבר מונח טכני**
→ [PART 4, מילון מושגים](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#מילון-מושגים-טכניים---מקיף)

---

**...לראות איך נוצר Job**
→ [TEST_JOB_CREATION_STEP_BY_STEP.md](../TEST_JOB_CREATION_STEP_BY_STEP.md)

---

**...השוואה בין טסטים**
→ [TEST_COMPARISON_AND_ANALYSIS.md](./TEST_COMPARISON_AND_ANALYSIS.md)

---

**...תוכנית עבודה**
→ [MASTER, Work Plan](./TEST_PLAN_MASTER_DOCUMENT.md#תוכנית-עבודה-לאוטומציה)

---

## 🎤 קישורים לפגישה

### Preparation
- [Elevator Pitch](./PRESENTATION_READY_SUMMARY.md#elevator-pitch-30-שניות)
- [Key Messages](./PRESENTATION_READY_SUMMARY.md#key-messages-מסרים-מרכזיים)
- [Slides](./PRESENTATION_READY_SUMMARY.md#slides-מוכנות)

### During Presentation
- [Talking Points](./PRESENTATION_READY_SUMMARY.md#talking-points)
- [Visual Aids](./PRESENTATION_READY_SUMMARY.md#visual-aids)
- [One-Pagers](./PRESENTATION_READY_SUMMARY.md#one-pagers-דף-אחד-לכל-נושא)

### Q&A
- [Expected Questions](./TEST_PLAN_MASTER_DOCUMENT.md#שאלות-צפויות-ותשובות)
- [Technical Answers](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#מילון-מושגים-טכניים---מקיף)

---

## 📊 קישורים לסטטיסטיקות

- [Test Breakdown](./TEST_PLAN_MASTER_DOCUMENT.md#סיכום-מבנה-התוכנית)
- [Automation Status](./TEST_PLAN_MASTER_DOCUMENT.md#progress-tracking)
- [Coverage Matrix](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#coverage-matrix)
- [Dependencies](./TEST_COMPARISON_AND_ANALYSIS.md#dependencies-matrix)

---

## 🔍 חיפוש לפי Test ID

| Test ID | קישור ישיר | קטגוריה |
|---------|-----------|----------|
| **PZ-13903** | [Nyquist Limit](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-5-frequency-range-nyquist-limit-enforcement) ⭐ | Critical |
| PZ-13909 | [Missing end_time](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-1-historic-configuration-missing-end_time-field) | High |
| PZ-13907 | [Missing start_time](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-2-historic-configuration-missing-start_time-field) | High |
| PZ-13906 | [Low Throughput](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-3-low-throughput-configuration-edge-case) | Medium |
| PZ-13904 | [Resource Estimation](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-4-configuration-resource-usage-estimation) | High |
| PZ-13901 | [NFFT Variations](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-6-nfft-values-validation---all-supported-values) | High |
| PZ-13897 | [GET /sensors](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-7-get-sensors---retrieve-available-sensors-list) | High |
| PZ-13879 | [Missing Fields](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-8-missing-required-fields) | High |
| PZ-13877 | [Invalid Freq Range](./COMPLETE_TEST_PLAN_DETAILED_PART2.md#test-9-invalid-frequency-range---min--max) | High |
| PZ-13876 | [Invalid Channel Range](./COMPLETE_TEST_PLAN_DETAILED_PART2.md#test-10-invalid-channel-range---min--max) | High |
| PZ-13873 | [Valid Configuration](./COMPLETE_TEST_PLAN_DETAILED_PART2.md#test-11-valid-configuration---all-parameters) | High |
| PZ-13863 | [Historic 5-min](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#test-23-historic-playback---standard-5-minute-range) | High |
| PZ-13868 | [Status 208](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#test-24-historic-playback---status-208-completion) | High |
| PZ-13784 | [ROI Command](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#test-26-send-roi-change-command-via-rabbitmq) | High |

---

## 🔑 קישורים למושגים

### Core Concepts
- [NFFT](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#nfft-number-of-fft-points)
- [PRR](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#prr-pulse-repetition-rate)
- [Nyquist Frequency](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#nyquist-frequency)
- [Spectrogram](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#spectrogram-ספקטוגרמה)
- [Throughput](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#throughput-תפוקה)

### Infrastructure
- [MongoDB](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#mongodb)
- [RabbitMQ](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#rabbitmq)
- [Kubernetes](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#kubernetes-k8s)
- [gRPC](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#grpc)

### Testing
- [Integration Test](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#integration-test)
- [E2E Test](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#e2e-test-end-to-end)
- [Performance Test](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#performance-test)
- [Negative Test](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#negative-test)

---

## 🎯 קישורים לפי נושא

### Historic Playback
- [Overview](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#historic-playback-tests---סקירה)
- [5-Minute Range](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#test-23-historic-playback---standard-5-minute-range)
- [Status 208](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#test-24-historic-playback---status-208-completion)
- [Invalid Time Range](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#test-25-historic---invalid-time-range-end-before-start)

### SingleChannel
- [Overview](./COMPLETE_TEST_PLAN_DETAILED_PART2.md#test-12-20-singlechannel-tests-suite)
- [Minimum Channel (0)](./COMPLETE_TEST_PLAN_DETAILED_PART2.md#test-12-singlechannel---minimum-channel-channel-0)
- [Maximum Channel](./COMPLETE_TEST_PLAN_DETAILED_PART2.md#test-13-singlechannel---maximum-channel)
- [Invalid Channels](./COMPLETE_TEST_PLAN_DETAILED_PART2.md#test-15-17-singlechannel---invalid-channels)

### Dynamic ROI
- [Overview](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#dynamic-roi-tests---סקירה)
- [ROI Command](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#test-26-send-roi-change-command-via-rabbitmq)
- [Safety Validation](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#test-27-roi-change-with-safety-validation)
- [Unsafe Changes](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#test-28-unsafe-roi-change-large-jump)

### Infrastructure
- [SSH Access](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#test-ssh-access-to-production)
- [Kubernetes](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#test-kubernetes-cluster-connection)
- [MongoDB](./COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md#test-mongodb-connection)

---

## 🔧 קישורים טכניים

### Code Examples
- [Job Creation Flow](../TEST_JOB_CREATION_STEP_BY_STEP.md#דוגמת-קוד-מלאה)
- [Valid Configuration](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#יישום-בקוד-קיים)
- [Nyquist Validation](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#יישום-בקוד-קיים-1)
- [ROI Safety](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#יישום)

### Helpers & Utilities
- [generate_task_id()](../how_jobs_are_created.md#generate_task_id)
- [generate_config_payload()](../how_jobs_are_created.md#generate_config_payload)
- [configure_streaming_job()](../how_jobs_are_created.md#configure_streaming_job)
- [validate_roi_change_safety()](./COMPLETE_TEST_PLAN_DETAILED_PART3.md#חישובי-safety)

---

## 📋 Quick Actions

### לפני פגישה
- [ ] קרא [MASTER](./TEST_PLAN_MASTER_DOCUMENT.md)
- [ ] קרא [PRESENTATION_READY](./PRESENTATION_READY_SUMMARY.md)
- [ ] עבור על [Critical Test (Nyquist)](./COMPLETE_TEST_PLAN_DETAILED_PART1.md#test-5-frequency-range-nyquist-limit-enforcement)
- [ ] הכן [Slides](./PRESENTATION_READY_SUMMARY.md#slides-מוכנות)

### במהלך פגישה
- 💡 [Talking Points](./PRESENTATION_READY_SUMMARY.md#talking-points)
- 📊 [Visual Aids](./PRESENTATION_READY_SUMMARY.md#visual-aids)
- ❓ [Q&A Prep](./TEST_PLAN_MASTER_DOCUMENT.md#שאלות-צפויות-ותשובות)

### אחרי פגישה
- 📝 [Work Plan](./TEST_PLAN_MASTER_DOCUMENT.md#תוכנית-עבודה-לאוטומציה)
- ✅ [Next Steps](./PRESENTATION_READY_SUMMARY.md#next-steps)

---

## 🏠 חזרה לדף הבית

→ [INDEX_TEST_PLAN.md](./INDEX_TEST_PLAN.md) ← התחל כאן!

---

*קובץ זה מכיל את כל הקישורים המהירים למסמכים*

**עודכן**: 27 אוקטובר 2025

