# 📚 אינדקס מסודר: מסמכי Specs חסרים

**תאריך יצירה:** 22 אוקטובר 2025  
**מטרה:** נקודת כניסה מרכזית לכל המידע על specs חסרים

---

## 🎯 לאן לפנות לפי צורך

### 🚀 קריאה מהירה (5 דקות)
**קובץ:** `סיכום_מהיר_SPECS_חסרים.md`  
**תוכן:**
- סיכום במספרים
- Top 5 בעיות קריטיות
- מה צריך לעשות עכשיו
- מדדי הצלחה

**מתאים ל:** מנהלים, Product Owners, כל מי שצריך overview מהיר

---

### 📊 דוח מקיף מלא (30 דקות)
**קובץ:** `MISSING_SPECS_COMPREHENSIVE_REPORT.md`  
**תוכן:**
- 20 קטגוריות מפורטות
- מיקומים מדויקים בקוד (קובץ + שורה)
- קישורים למסמכי תיעוד
- דוגמאות קוד
- טבלה מרכזית
- TOP 5 issues מפורטים
- המלצות לפעולה

**מתאים ל:** Developers, QA Engineers, Technical Leads

---

### 📁 טבלת Excel (עבודה עם הנתונים)
**קובץ:** `MISSING_SPECS_TABLE.csv`  
**תוכן:**
- 20 שורות (specs)
- 9 עמודות (מידע)
- ניתן לסינון, מיון, filtering ב-Excel
- ניתן להוספת עמודות (Status, Assigned To, וכו')

**מתאים ל:** ניהול פרויקט, מעקב אחר תיקונים

**איך לפתוח:**
```bash
# Windows
start excel MISSING_SPECS_TABLE.csv

# Mac
open MISSING_SPECS_TABLE.csv

# Linux
libreoffice MISSING_SPECS_TABLE.csv
```

---

### 🎤 מצגת לפגישה (90 דקות)
**קובץ:** `CONFLUENCE_SPECS_MEETING.md`  
**תוכן:**
- Top 7 Critical Issues
- דוגמאות קוד מפורטות
- שאלות לדיון
- סדר יום לפגישה

**מתאים ל:** פגישת specs עם הצוות

---

## 📂 מבנה הקבצים

```
C:\Projects\focus_server_automation\
│
├── 📄 MISSING_SPECS_INDEX.md ........................... ← מסמך זה (נקודת כניסה)
├── 📄 MISSING_SPECS_COMPREHENSIVE_REPORT.md ............ ← דוח מקיף מלא
├── 📄 MISSING_SPECS_TABLE.csv .......................... ← טבלת Excel
├── 📄 סיכום_מהיר_SPECS_חסרים.md ....................... ← קריאה מהירה בעברית
│
├── 📄 CONFLUENCE_SPECS_MEETING.md ...................... ← מסמך לפגישה
├── 📄 CONFLUENCE_SPECS_MEETING_WITH_MACROS.confluence .. ← Confluence format
│
└── documentation/
    └── specs/
        ├── CRITICAL_MISSING_SPECS_LIST.md .............. ← רשימה מלאה (200+ specs)
        ├── CODE_EVIDENCE_MISSING_SPECS.md .............. ← 10 דוגמאות קוד
        ├── TOP_CODE_LINKS_FOR_SPECS.md ................. ← Top 3 critical links
        └── SPECS_REQUIREMENTS_FOR_MEETING.md ........... ← דרישות לפגישה
```

---

## 🔍 חיפוש מהיר לפי נושא

### Performance Issues:
- **דוח מקיף:** סעיף #1 (שורות 51-139)
- **קוד:** `tests/integration/performance/test_performance_high_priority.py:146-170`
- **מסמך:** `CONFLUENCE_SPECS_MEETING.md:46-85`

### ROI Issues:
- **דוח מקיף:** סעיף #2 (שורות 141-207)
- **קוד:** `src/utils/validators.py:395`
- **מסמך:** `CONFLUENCE_SPECS_MEETING.md:87-118`

### NFFT Issues:
- **דוח מקיף:** סעיף #3 (שורות 209-271)
- **קוד:** `src/utils/validators.py:194-227`
- **מסמך:** `CONFLUENCE_SPECS_MEETING.md:125-159`

### MongoDB Outage:
- **דוח מקיף:** סעיף #4 (שורות 273-323)
- **קוד:** `tests/integration/infrastructure/test_mongodb_connectivity.py`
- **מסמך:** `CODE_EVIDENCE_MISSING_SPECS.md:296-313`

### SingleChannel API:
- **דוח מקיף:** סעיף #5 (שורות 325-389)
- **קוד:** `tests/integration/api/test_singlechannel_view_mapping.py`
- **מסמך:** `documentation/testing/SINGLECHANNEL_TEST_RESULTS.md:48-80`

### Frequency Range:
- **דוח מקיף:** סעיף #6 (שורות 393-397)
- **קוד:** `src/models/focus_server_models.py:46-57`
- **מסמך:** `CONFLUENCE_SPECS_MEETING.md:161-197`

### Sensor Range:
- **דוח מקיף:** סעיף #7 (שורות 399-403)
- **קוד:** `src/utils/validators.py:116-151`
- **מסמך:** `CONFLUENCE_SPECS_MEETING.md:199-237`

### RabbitMQ Commands:
- **דוח מקיף:** סעיף #8 (שורות 405-409)
- **קוד:** `src/external/rabbitmq/`
- **מסמך:** `docs/RABBITMQ_AUTOMATION_GUIDE.md`

---

## 🎯 תרחישי שימוש

### תרחיש 1: "אני מנהל ורוצה להבין את המצב"
👉 **קרא:** `סיכום_מהיר_SPECS_חסרים.md`  
⏱️ **זמן:** 5 דקות  
✅ **תקבל:** תמונת מצב כוללת, Top 5 בעיות, המלצות

---

### תרחיש 2: "אני developer וצריך לתקן בעיה ספציפית"
👉 **קרא:** `MISSING_SPECS_COMPREHENSIVE_REPORT.md` - מצא את הבעיה הספציפית  
👉 **עבור ל:** מיקום הקוד המדויק  
👉 **קרא:** המסמך המתאים  
⏱️ **זמן:** 10-15 דקות  
✅ **תקבל:** מיקום מדויק, מה חסר, מה לתקן

---

### תרחיש 3: "אני QA Lead ורוצה לעקוב אחר כל התיקונים"
👉 **פתח:** `MISSING_SPECS_TABLE.csv` ב-Excel  
👉 **הוסף עמודות:** Status, Assigned To, Target Date  
👉 **עדכן:** סטטוס לאחר כל תיקון  
⏱️ **זמן:** עבודה רציפה  
✅ **תקבל:** מעקב מסודר, reporting לניהול

---

### תרחיש 4: "אנחנו מארגנים פגישת specs"
👉 **שלח מראש:** `CONFLUENCE_SPECS_MEETING.md`  
👉 **הצג בפגישה:** דוגמאות קוד מהמסמך  
👉 **רשום החלטות:** תוך כדי הפגישה  
👉 **אחרי פגישה:** צור `SPECS_DECISIONS.md`  
⏱️ **זמן:** 2-3 שעות  
✅ **תקבל:** החלטות מתועדות, action items

---

### תרחיש 5: "אני צריך להציג למנהל שלי"
👉 **הכן:** PowerPoint עם slides מ-`CONFLUENCE_SPECS_MEETING.md`  
👉 **הצג:** הטבלה המרכזית מ-`MISSING_SPECS_COMPREHENSIVE_REPORT.md`  
👉 **סיכום:** מספרים מ-`סיכום_מהיר_SPECS_חסרים.md`  
⏱️ **זמן:** 15 דקות  
✅ **תקבל:** מצגת מקצועית, buy-in מהניהול

---

## 📋 Checklist לפעולה

### לפני פגישת Specs:
- [ ] קרא `CONFLUENCE_SPECS_MEETING.md`
- [ ] סקור Top 5 Critical Issues
- [ ] הכן שאלות לדיון
- [ ] שלח מסמך למשתתפים 2 ימים מראש

### בזמן הפגישה:
- [ ] עבור על Issues #1-3 (60 דקות)
- [ ] עבור על Issues #4-5 (45 דקות)
- [ ] עבור על Issues #6-10 (30 דקות)
- [ ] רשום כל החלטה ב-`SPECS_DECISIONS.md`

### אחרי הפגישה:
- [ ] עדכן `config/settings.yaml` עם ערכים חדשים
- [ ] עדכן `src/utils/validators.py`
- [ ] הפעל assertions ב-`tests/integration/performance/`
- [ ] הרץ 82+ טסטים מושפעים
- [ ] עדכן Jira Xray
- [ ] שלח summary לצוות

---

## 🔗 קישורים לקבצי קוד מרכזיים

### Validators:
```
src/utils/validators.py
├── Line 395  → ROI 50% hardcoded
├── Line 194  → NFFT validation permissive
├── Line 116  → Sensor range no limits
└── Line 153  → Frequency validation
```

### Models:
```
src/models/focus_server_models.py
├── Line 46   → FrequencyRange (no max)
├── Line 33   → Channels model
└── Line 99   → Time validation
```

### Performance Tests:
```
tests/integration/performance/test_performance_high_priority.py
├── Line 146  → Thresholds (TODO)
├── Line 157  → Assertions disabled
└── Line 246  → More TODOs
```

### Config Validation Tests:
```
tests/integration/api/test_config_validation_high_priority.py
├── Line 481  → Edge case no assertion
└── Line 517  → Another edge case
```

---

## 📞 איש קשר

**QA Automation Team**  
**Location:** `C:\Projects\focus_server_automation\`  
**Last Update:** 22 October 2025

---

## 🔄 גרסאות המסמך

| תאריך | גרסה | שינויים |
|-------|------|---------|
| 22/10/2025 | 1.0 | יצירה ראשונית - 20 קטגוריות, 82+ טסטים מושפעים |

---

**✅ המסמך מעודכן ומוכן לשימוש!**

