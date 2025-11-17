# 📚 תיק הכנה מקיף לפגישת סקירת טסטים - PZ-13756

---

## 🎯 סקירה כללית

תיקייה זו מכילה **מסמכי הכנה מקיפים** לפגישת סקירת 5 טסטי ביצועים ותשתית קריטיים עבור Focus Server.

כל מסמך בנוי **לפרטי פרטים** ומכסה:
✅ מטרה ונחיצות הטסט  
✅ מה בודקים בדיוק  
✅ מימוש מעשי בקוד עם הסברים  
✅ שאלות מפורטות לפגישה  
✅ טבלאות השוואה ודוגמאות

---

## 📂 מבנה התיקייה

### 📋 מסמכים במערך:

| # | קובץ | תיאור | זמן קריאה |
|---|------|---------|-----------|
| 0 | `00_Meeting_Preparation_Index.md` | **מסמך אינדקס ראשי** - מפת דרכים, סקירה כללית, שאלות כלליות | 10 דק' |
| 1 | `01_High_Throughput_Test.md` | **PZ-13905**: High Throughput Configuration Stress Test | 15 דק' |
| 2 | `02_Concurrent_Task_Limit.md` | **PZ-13896**: Concurrent Task Limit (קיבולת מקבילית) | 15 דק' |
| 3 | `03_Config_Latency_P95.md` | **PZ-13770**: /config Latency P95/P99 | 12 דק' |
| 4 | `04_MongoDB_Recovery.md` | **PZ-13687**: MongoDB Recovery – Recordings Indexed After Outage | 10 דק' |
| 5 | `05_Configure_Latency_P95.md` | **PZ-13571**: /configure latency p95 (Smoke Test) | 8 דק' |

**סה"כ זמן קריאה**: ~70 דקות (קריאה מלאה)

---

## 🚀 איך להשתמש במסמכים הללו?

### תרחיש 1: יש לך שעה לפני הפגישה
1. קרא את **`00_Meeting_Preparation_Index.md`** (10 דק')
2. קרא **3 מסמכים** בעדיפות גבוהה (1, 2, 3) לעומק (42 דק')
3. עיין ב-**תקציר מהיר** של מסמכים 4 ו-5 (8 דק')

### תרחיש 2: יש לך חצי שעה בלבד
1. קרא את **הסעיף "תקציר מהיר לפגישה"** בכל מסמך (5×2 = 10 דק')
2. קרא את **"שאלות לפגישה"** בכל מסמך (5×2 = 10 דק')
3. עיין ב-**טבלאות השוואה** ב-`00_Meeting_Preparation_Index.md` (10 דק')

### תרחיש 3: יש לך רק 10 דקות
1. קרא את **`00_Meeting_Preparation_Index.md`** בלבד
2. תסמן את **השאלות הכי חשובות** בכל מסמך (skim)

---

## 🎯 מה מקבלים מהמסמכים?

### 📖 בכל מסמך יש:

1. **תקציר מהיר** (Quick Brief)
   - טבלה עם כל הפרטים החשובים במבט אחד

2. **מטרות הטסט** (Test Objectives)
   - למה הטסט קיים?
   - מה הוא בודק?
   - למה הוא קריטי?

3. **תרחישי הבדיקה** (Test Scenarios)
   - מה בדיוק קורה בטסט?
   - איזה נתונים משתמשים?
   - מה התוצאות הצפויות?

4. **נחיצות** (Why Critical)
   - מה קורה אם לא בודקים?
   - איזה סיכונים?
   - דוגמאות מהחיים

5. **מימוש בקוד** (Code Implementation)
   - קוד מלא עם הסברים **שורה אחר שורה**
   - מה כל פונקציה עושה
   - למה בחרו בגישה הזו

6. **שאלות לפגישה** (Questions for Meeting)
   - שאלות מדיניות
   - שאלות טכניות
   - שאלות להבהרה

7. **טבלאות וסיכומים** (Tables & Summaries)
   - השוואות
   - תרחישים
   - benchmarks

8. **Checklist** לפני הפגישה
   - וידוא שהכנת הכל

---

## 🔑 נקודות מפתח לזכור

### הטסטים בקצרה:

| טסט | מה בודק | למה קריטי |
|-----|---------|-----------|
| **PZ-13905** | תפוקה גבוהה (>50 Mbps) | מניעת קריסת מערכת בעומס |
| **PZ-13896** | מקביליות (10-50 tasks) | מניעת failures עם משתמשים רבים |
| **PZ-13770** | זמני תגובה (P95 < 300ms) | חוויית משתמש טובה |
| **PZ-13687** | התאוששות MongoDB | מניעת איבוד נתונים |
| **PZ-13571** | smoke test מהיר | Sanity check בסיסי |

---

## 📊 רמת חשיבות

### לפי עדיפות:

1. **🔴 קריטי (Critical)**:
   - PZ-13687 (MongoDB Recovery)
   - PZ-13896 (Concurrent Tasks)
   - PZ-13770 (Latency P95)

2. **🟡 גבוה (High)**:
   - PZ-13905 (High Throughput)

3. **🟢 בינוני (Medium)**:
   - PZ-13571 (Smoke Test)

---

## 💡 טיפים לפגישה

### ✅ DO:
- **הדגש את הערך העסקי** של כל טסט (לא רק הטכניקה)
- **הצג מספרים קונקרטיים** (thresholds, benchmarks)
- **שאל שאלות להבהרת דרישות** (SLA, capacity planning)
- **הצע שיפורים** אם יש לך רעיונות

### ❌ DON'T:
- **אל תניח הנחות** - אם לא ברור, שאל
- **אל תתמקד רק בקוד** - דבר על הערך
- **אל תדלג על הטיפוסים שנראים "קלים"** - גם smoke test חשוב
- **אל תשכח לתעד החלטות** מהפגישה

---

## 📝 הערות חשובות

### ⚠️ שים לב:
1. **Thresholds** - חלק מה-thresholds **טרם הוגדרו סופית** ("need specs meeting")
2. **MongoDB Recovery Test** - דורש **Kubernetes** ולא יכול לרוץ locally
3. **Smoke Test** - ה-threshold של 2s **lenient מאוד** (10× מ-latency test)

### 🔄 מה חסר (Known Gaps):
- **Memory load tests** (הוזכר ב-PZ-13571)
- **Historical config smoke test** (אין)
- **Waterfall endpoint tests** (אין פירוט)
- **Real load tests** עם concurrent users (רק sequential)

---

## 🎓 מושגים שכדאי לדעת

| מושג | הסבר קצר | איפה להרחיב |
|------|----------|-------------|
| **Throughput** | כמות נתונים לשנייה (Mbps) | 01_High_Throughput_Test.md |
| **P95/P99** | Percentiles (95%/99% requests) | 03_Config_Latency_P95.md |
| **NFFT** | FFT size (128-4096) | 00_Meeting_Preparation_Index.md |
| **Concurrent Tasks** | Tasks running at same time | 02_Concurrent_Task_Limit.md |
| **Recovery Mechanism** | Auto-indexing after outage | 04_MongoDB_Recovery.md |

---

## 🚀 מה הלאה?

### אחרי הפגישה:
1. **תעד החלטות** שהתקבלו
2. **עדכן thresholds** במסמכים ובקוד
3. **צור tasks** ל-missing tests
4. **שתף את המסמכים** עם הצוות

### מסמכים נוספים שכדאי ליצור:
- [ ] **Test Execution Report Template** (דוח ריצה)
- [ ] **Performance Baseline Document** (baseline metrics)
- [ ] **SLA Definition Document** (הגדרות רשמיות)
- [ ] **Runbook for Test Failures** (מה לעשות כשטסט נכשל)

---

## 📞 יצירת קשר

**נוצר עבור**: Roy Avrahami  
**פרויקט**: Focus Server Automation (PZ-13756)  
**תאריך**: אוקטובר 2025

---

## ✨ בהצלחה בפגישה!

**אתה מוכן. המסמכים כאן לתמיכה שלך. תצליח!** 🚀

---

*"The best preparation is to know the material inside and out."*

---

