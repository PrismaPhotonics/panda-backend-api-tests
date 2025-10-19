# T-DATA-002: Historical vs Live Recordings - Index

**תאריך:** 15 אוקטובר 2025  
**סטטוס:** ✅ מוכן לייבוא ל-Xray  
**בדיקה:** PASSED ✅

---

## 📚 תיעוד מלא - כל הקבצים

### 1️⃣ מפרט Xray מלא (MAIN)
**📄 `XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md`** (מפורט ביותר)
- **תוכן:** מפרט Xray מלא ל-T-DATA-002
- **צעדים:** 30 צעדים מפורטים
- **שורות:** 450+ שורות
- **שימוש:** **מקור ראשי** לייבוא ידני ל-Jira
- **כולל:**
  - Objective מפורט
  - Architectural Context
  - 30 Test Steps מפורטים
  - Expected Results
  - 5 Assertions קריטיים
  - Test Results אחרונים (PASSED)
  - Recommendations
  - Questions לצוות פיתוח
  - Related Documentation

### 2️⃣ סיכום בעברית
**📄 `T_DATA_002_XRAY_SUMMARY_HEBREW.md`**
- **תוכן:** סיכום מקיף בעברית
- **שורות:** 250+ שורות
- **שימוש:** הבנה מהירה, הצגה לצוות
- **כולל:**
  - הסבר בעברית על מטרת הבדיקה
  - תרשימי זרימה
  - תוצאות בעברית
  - המלצות ושאלות בעברית
  - Checklist לייבוא

### 3️⃣ דוח ביצוע מפורט (באנגלית)
**📄 `T_DATA_002_HISTORICAL_VS_LIVE_REPORT.md`**
- **תוכן:** דוח ביצוע טכני מלא
- **שורות:** 300+ שורות
- **שימוש:** אנליזה טכנית, דיווח לניהול
- **כולל:**
  - Executive Summary
  - Test Architecture
  - Test Execution Flow (6 שלבים)
  - Sample Data מהבדיקה
  - Cleanup Service Analysis
  - Recommendations מפורטות
  - Questions לצוות
  - Test Code Location

### 4️⃣ הסבר טכני מעמיק
**📄 `LIVE_VS_HISTORICAL_RECORDINGS.md`**
- **תוכן:** הסבר ארכיטקטוני מעמיק
- **שורות:** 313 שורות
- **שימוש:** הבנה טכנית עמוקה
- **כולל:**
  - הסבר The Challenge
  - Detection Algorithm (קוד Python)
  - Rationale
  - Implementation בבדיקות
  - Test Results
  - Long-Term Solution (שדה `status`)
  - Migration Strategy
  - Monitoring and Alerts
  - Code Examples מפורטים

### 5️⃣ מדריך ייבוא ל-Xray
**📄 `XRAY_IMPORT_GUIDE.md`**
- **תוכן:** מדריך שלב-אחר-שלב לייבוא
- **שורות:** 450+ שורות
- **שימוש:** **מדריך ייבוא** - עקוב צעד אחרי צעד
- **כולל:**
  - 3 שיטות ייבוא (Manual, CSV, API)
  - 15 שלבים מפורטים לייבוא ידני
  - Checklist מלא (22 פריטים)
  - טיפים ופתרון בעיות
  - קבצים לשימוש
  - עזרה נוספת

### 6️⃣ קובץ CSV לייבוא המוני
**📄 `XRAY_IMPORT_T_DATA_002.csv`**
- **תוכן:** שורה אחת עם כל הפרטים
- **שימוש:** ייבוא CSV ל-Jira
- **שדות:** 14 עמודות
- **הערה:** מייבא מידע בסיסי בלבד

### 7️⃣ קובץ אינדקס (זה)
**📄 `T_DATA_002_INDEX.md`**
- **תוכן:** אינדקס של כל הקבצים
- **שימוש:** ניווט מהיר לתיעוד

### 8️⃣ רשימת בדיקות Xray מעודכנת
**📄 `JIRA_XRAY_NEW_TESTS.md`** (עודכן)
- **תוכן:** רשימת כל הבדיקות לXray
- **שימוש:** מעקב על כל הבדיקות
- **כולל:**
  - סיכום 8 בדיקות
  - T-DATA-002 נוסף לרשימה
  - קישורים לקבצים

---

## 🎯 מהיכן להתחיל?

### אם אתה רוצה לייבא ל-Xray 👉
**התחל כאן:** `XRAY_IMPORT_GUIDE.md`
- בחר שיטת ייבוא (Manual מומלץ)
- עקוב אחרי הצעדים
- השתמש ב-`XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md` כמקור

### אם אתה רוצה להבין את הבדיקה 👉
**התחל כאן:** `T_DATA_002_XRAY_SUMMARY_HEBREW.md`
- קרא את הסיכום בעברית
- הבן את מטרת הבדיקה
- עבור ל-`LIVE_VS_HISTORICAL_RECORDINGS.md` לפרטים טכניים

### אם אתה רוצה דוח לניהול 👉
**התחל כאן:** `T_DATA_002_HISTORICAL_VS_LIVE_REPORT.md`
- קרא את ה-Executive Summary
- בדוק את התוצאות
- העבר את ה-Recommendations

### אם אתה רוצה לרוץ את הבדיקה 👉
**התחל כאן:** פקודת הרצה:
```bash
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_historical_vs_live_recordings -v
```

---

## 📊 סטטיסטיקות תיעוד

| מדד | ערך |
|-----|-----|
| **סה"כ קבצים שנוצרו** | 8 קבצים |
| **סה"כ שורות תיעוד** | ~2,000 שורות |
| **שפות** | עברית ואנגלית |
| **פורמטים** | Markdown, CSV |
| **צעדי בדיקה** | 30 צעדים מפורטים |
| **Assertions** | 5 קריטיים |
| **Recommendations** | 2 (High + Medium) |
| **Questions לצוות** | 4 שאלות |

---

## 🔗 תלות בין קבצים

```
T_DATA_002_INDEX.md (זה)
    │
    ├─── XRAY_IMPORT_GUIDE.md (מדריך ייבוא)
    │       │
    │       ├─── XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md (מפרט מלא - MAIN)
    │       ├─── XRAY_IMPORT_T_DATA_002.csv (CSV)
    │       └─── T_DATA_002_XRAY_SUMMARY_HEBREW.md (סיכום)
    │
    ├─── T_DATA_002_HISTORICAL_VS_LIVE_REPORT.md (דוח ביצוע)
    │
    ├─── LIVE_VS_HISTORICAL_RECORDINGS.md (הסבר טכני)
    │
    └─── JIRA_XRAY_NEW_TESTS.md (רשימת בדיקות - עודכן)
```

---

## 🎨 מפת ניווט לפי תפקיד

### QA Engineer / Tester
1. 📖 קרא: `T_DATA_002_XRAY_SUMMARY_HEBREW.md`
2. 🔄 הבן: `LIVE_VS_HISTORICAL_RECORDINGS.md`
3. ▶️ הרץ: `pytest ...test_historical_vs_live_recordings... -v`
4. 📋 ייבא: עקוב אחרי `XRAY_IMPORT_GUIDE.md`

### Developer / DevOps
1. 📖 קרא: `LIVE_VS_HISTORICAL_RECORDINGS.md`
2. 🐛 סקור: `T_DATA_002_HISTORICAL_VS_LIVE_REPORT.md` → Recommendations
3. 💡 תקן: השתמש בקוד לדוגמא מהמסמכים
4. ✅ אמת: הרץ את הבדיקה מחדש

### Project Manager / Team Lead
1. 📊 קרא: `T_DATA_002_HISTORICAL_VS_LIVE_REPORT.md` → Executive Summary
2. 📋 סקור: Questions for Development Team
3. 🎯 החלט: סדר עדיפויות לתיקונים
4. 📍 עקוב: ייבא ל-Jira Xray לניהול

### Architect / Technical Lead
1. 🏗️ קרא: `LIVE_VS_HISTORICAL_RECORDINGS.md` → Architectural Context
2. 🔍 נתח: `T_DATA_002_HISTORICAL_VS_LIVE_REPORT.md` → Recommendations
3. 📐 תכנן: Long-Term Solution (שדה `status`)
4. 📚 תעד: עדכן ארכיטקטורה בהתאם

---

## ✅ Checklist מהיר

לפני ייבוא ל-Xray, ודא:

- [x] קראתי את `XRAY_IMPORT_GUIDE.md`
- [x] בחרתי שיטת ייבוא (Manual/CSV/API)
- [x] פתחתי את `XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md`
- [x] יש לי גישה ל-Jira Project PZ
- [x] יש לי הרשאות ליצירת Tests
- [x] הבנתי את מטרת הבדיקה

בזמן ייבוא:

- [ ] מילאתי Summary וMetadata
- [ ] הוספתי 7 Components
- [ ] קישרתי Requirements (PZ-13598)
- [ ] העתקתי 30 Test Steps
- [ ] הוספתי Expected Results
- [ ] העתקתי 5 Assertions
- [ ] מילאתי Automation Details
- [ ] הוספתי Test Results אחרונים
- [ ] קישרתי Related Issues
- [ ] שמרתי ואימתתי

לאחר ייבוא:

- [ ] ודאתי שהבדיקה נוצרה נכון
- [ ] רשמתי את מספר הבדיקה ב-Jira
- [ ] שיתפתי עם הצוות
- [ ] עדכנתי תיעוד פנימי

---

## 📞 תמיכה

**מחבר הבדיקה:** רועי אברהמי  
**תאריך יצירה:** 15 אוקטובר 2025  
**סטטוס:** ✅ מוכן לייבוא

**שאלות?**
- בדוק את `XRAY_IMPORT_GUIDE.md` → פתרון בעיות
- סקור את התיעוד המפורט
- פנה למחבר הבדיקה

---

## 🎉 סיכום

נוצר **תיעוד מקיף** לבדיקה T-DATA-002:

✅ **8 קבצים** מפורטים  
✅ **~2,000 שורות** תיעוד  
✅ **עברית + אנגלית**  
✅ **מדריכים שלב-אחר-שלב**  
✅ **קוד לדוגמא**  
✅ **Recommendations**  
✅ **Checklist מלא**

**הכל מוכן לייבוא ל-Jira Xray! 🚀**

---

**📁 קובץ זה נוצר אוטומטית ע"י Roy Avrahami - QA Automation Architect**

