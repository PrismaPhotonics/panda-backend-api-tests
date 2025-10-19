# מדריך ייבוא T-DATA-002 ל-Jira Xray

**תאריך:** 15 אוקטובר 2025  
**בדיקה:** T-DATA-002 - Historical vs Live Recordings Classification

---

## 🚀 שיטות ייבוא

יש **3 שיטות** לייבוא הבדיקה ל-Xray. בחר את השיטה המתאימה לך:

---

## שיטה 1: ייבוא ידני (Manual Copy-Paste) ⭐ מומלץ

### יתרונות
- ✅ פשוט וישיר
- ✅ אין צורך בהרשאות מיוחדות
- ✅ מלא שליטה על כל שדה

### צעדים

#### שלב 1: פתיחת Jira
1. פתח דפדפן וגש ל-Jira
2. עבור ל-**Project PZ** → **Test Repository**
3. לחץ על **"Create Test"** או **"+"**

#### שלב 2: פתיחת המפרט
1. פתח את הקובץ: **`XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md`**
2. זה המפרט המלא לבדיקה (30 צעדים מפורטים)

#### שלב 3: מילוי שדות בסיסיים

| שדה ב-Jira | ערך להעתקה |
|-----------|------------|
| **Test ID** | `T-DATA-002` (או `NEW-006`) |
| **Summary** | `Data Lifecycle – Historical vs Live Recordings Classification` |
| **Test Type** | `Integration Test` |
| **Priority** | `High` |

#### שלב 4: הוספת Components/Labels

לחץ על **Components** והוסף:
- `focus-server`
- `mongodb`
- `data-lifecycle`
- `data-quality`
- `data-integrity`
- `recordings`
- `cleanup`

#### שלב 5: קישור Requirements

בשדה **Requirements**, קשר ל:
- **PZ-13598** (Data Quality – Mongo collections and schema)
- **FOCUS-DATA-LIFECYCLE** (Recording lifecycle management)
- **FOCUS-CLEANUP-SERVICE** (Data cleanup and retention)

#### שלב 6: מילוי Objective

העתק מהמפרט את החלק תחת **"## Objective"**:

```
Validate that MongoDB correctly distinguishes between Historical (completed), 
Live (in-progress), and Deleted (cleanup) recordings. Verify that the recording 
lifecycle is properly managed and that cleanup services are functioning correctly.

Business Impact:
- Historical recordings must be indexed for history playback
- Live recordings must be distinguished from stale/crashed recordings
- Deleted recordings must be properly marked for cleanup
```

#### שלב 7: הוספת Pre-Conditions

העתק את ה-Pre-Conditions מהמפרט:

```
- PC-010: MongoDB is reachable and accessible
- PC-013: Recording collection exists with data
- PC-021: Recording collection is dynamically named (GUID-based)
- PC-022: base_paths collection contains GUID
- PC-023: System has active or historical recordings
```

#### שלב 8: הוספת Test Steps

**אפשרות A: העתקת הטבלה (מהירה)**
העתק את הטבלה מתוך המפרט (שורות 723-758):

```
| # | Action | Expected Result |
|---|--------|-----------------|
| 1 | Connect to MongoDB | Success |
| 2 | Get recording collection GUID from base_paths | GUID retrieved |
...
```

**אפשרות B: העתקה מפורטת (מומלצת)**
פתח את המפרט המלא (`XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md`, שורות 44-80) והעתק את ה-30 צעדים המפורטים.

#### שלב 9: הוספת Expected Result

העתק מהמפרט את החלק תחת **"Expected Result (overall)"**:

```
Classification Results:
- Historical: ~99% (completed recordings)
- Live: <1% (recent, <24h)
- Deleted: <1% (cleanup)
- Invalid: 0 ✅
- Stale: 0 ✅

Data Integrity:
- ✅ All recordings have start_time
- ✅ Classification totals match
- ✅ Historical are majority (>50%)
```

#### שלב 10: הוספת Assertions

העתק את ה-Assertions מהמפרט:

```python
Critical (Test FAILS if violated):
1. invalid_count == 0 (all have start_time)
2. historical + live + deleted == total (integrity)
3. historical / total > 0.50 (majority)

Warning (Test WARNS but PASSES):
4. Stale recordings detected (>24h without end_time)
5. Deleted recordings missing end_time
```

#### שלב 11: מילוי Automation Details

| שדה | ערך |
|-----|-----|
| **Automation Status** | `Automated ✅` |
| **Test Function** | `test_historical_vs_live_recordings` |
| **Test File** | `tests/integration/infrastructure/test_mongodb_data_quality.py` |
| **Test Class** | `TestMongoDBDataQuality` |

#### שלב 12: הוספת Execution Command

```bash
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_historical_vs_live_recordings -v
```

#### שלב 13: קישור Related Issues

בשדה **Related Issues**, קשר ל:
- **T-DATA-001** (Soft Delete - Related test)
- **BUG-CLEANUP-001** (Missing end_time - Discovered by this test)

#### שלב 14: הוספת Test Results

העתק את התוצאות האחרונות מהמפרט:

```
Date: 2025-10-15
Status: ✅ PASSED

Classification:
   Historical: 3,414 (99.3%) ✅
   Live: 1 (0.03%) ✅
   Deleted: 24 (0.7%) ⚠️
   Invalid: 0 (0%) ✅

✅ All assertions passed
⚠️  24 deleted recordings missing end_time
```

#### שלב 15: שמירה
1. לחץ **Save** או **Create**
2. ודא שהבדיקה נוצרה בהצלחה
3. רשום את מספר הבדיקה ב-Jira (למשל: `PZ-14523`)

---

## שיטה 2: ייבוא CSV (Bulk Import) 📊

### יתרונות
- ✅ מהיר לייבוא מרובה
- ✅ טוב לעדכון קבוצתי

### צעדים

#### שלב 1: הורדת קובץ CSV
השתמש בקובץ: **`XRAY_IMPORT_T_DATA_002.csv`**

#### שלב 2: פתיחת Jira Importer
1. גש ל-Jira → **System** → **Import & Export**
2. בחר **Import from CSV**

#### שלב 3: העלאת הקובץ
1. לחץ **Choose File**
2. בחר את `XRAY_IMPORT_T_DATA_002.csv`
3. לחץ **Next**

#### שלב 4: מיפוי שדות
מפה את העמודות:
- `Test ID` → `Issue Key`
- `Summary` → `Summary`
- `Test Type` → `Test Type`
- `Priority` → `Priority`
- וכו'...

#### שלב 5: אימות וייבוא
1. בדוק את המיפוי
2. לחץ **Begin Import**
3. המתן להשלמה
4. בדוק שהבדיקה נוצרה

**הערה:** שיטה זו מייבאת רק מידע בסיסי. יש להשלים ידנית:
- צעדים מפורטים (Test Steps)
- Assertions
- תוצאות בדיקה אחרונות

---

## שיטה 3: Xray REST API (Automated) 🤖

### יתרונות
- ✅ אוטומציה מלאה
- ✅ אינטגרציה עם CI/CD
- ✅ ייבוא מרובה

### דרישות מוקדמות
- Token/API Key של Xray
- הרשאות ליצירת בדיקות
- כלי API (Postman/curl/Python)

### צעדים

#### שלב 1: קבלת Credentials
1. גש ל-Jira → **Settings** → **Apps**
2. בחר **Xray API Keys**
3. צור API Key חדש
4. שמור את ה-Client ID ו-Client Secret

#### שלב 2: קבלת Token
```bash
curl -X POST https://xray.cloud.getxray.app/api/v1/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
  }'
```

התשובה תכיל `token` - שמור אותו.

#### שלב 3: הכנת JSON
צור קובץ `t_data_002.json`:

```json
{
  "fields": {
    "project": {
      "key": "PZ"
    },
    "summary": "Data Lifecycle – Historical vs Live Recordings Classification",
    "issuetype": {
      "name": "Test"
    },
    "priority": {
      "name": "High"
    },
    "components": [
      {"name": "focus-server"},
      {"name": "mongodb"},
      {"name": "data-lifecycle"}
    ],
    "customfield_XXXXX": "Integration Test",
    "description": "Full description from XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md"
  }
}
```

**הערה:** `customfield_XXXXX` הוא שדה מותאם אישית ל-Test Type. יש למצוא את המזהה הנכון ב-Jira שלך.

#### שלב 4: ייבוא ה-Test
```bash
curl -X POST https://your-jira-instance/rest/api/2/issue \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @t_data_002.json
```

#### שלב 5: הוספת Test Steps (Xray API)
```bash
curl -X POST https://xray.cloud.getxray.app/api/v1/test/PZ-XXXXX/step \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "steps": [
      {
        "action": "Connect to MongoDB",
        "data": "Database name from config",
        "result": "Success"
      },
      ...
    ]
  }'
```

---

## 🔍 אימות לאחר ייבוא

לאחר הייבוא, ודא:

### 1. שדות בסיסיים
- [x] Test ID נקבע (T-DATA-002 או מספר אחר)
- [x] Summary נכון
- [x] Priority = High
- [x] Test Type = Integration Test

### 2. תוכן
- [x] Objective מפורט
- [x] Pre-Conditions (5 תנאים)
- [x] Test Steps (27 צעדים)
- [x] Expected Results מוגדרים
- [x] Assertions רשומים (5 אסרשנים)

### 3. קישורים
- [x] Requirements מקושרים (PZ-13598)
- [x] Related Issues מקושרים (T-DATA-001)
- [x] Components מוגדרים (7 components)

### 4. אוטומציה
- [x] Automation Status = Automated
- [x] Test Function מצוין
- [x] Test File מצוין
- [x] Execution Command מצוין

### 5. תוצאות
- [x] Test Results אחרונים מתועדים
- [x] Date: 2025-10-15
- [x] Status: PASSED
- [x] תוצאות מפורטות

---

## 📋 Checklist מלא לייבוא

```
✅ 1. פתיחת Jira והכנת Test Repository
✅ 2. יצירת Test Case חדש (T-DATA-002)
✅ 3. מילוי Summary וMetadata
✅ 4. הוספת Components/Labels (7)
✅ 5. קישור Requirements (3)
✅ 6. מילוי Objective + Business Impact
✅ 7. הוספת Pre-Conditions (5)
✅ 8. הוספת Architectural Context
✅ 9. הכנת Test Data
✅ 10. העתקת Test Steps (27 צעדים)
✅ 11. הוספת Expected Results
✅ 12. מילוי Post-Conditions
✅ 13. הוספת Assertions (5)
✅ 14. מילוי Automation Details
✅ 15. הוספת Execution Command
✅ 16. קישור Related Issues
✅ 17. הוספת Test Results אחרונים
✅ 18. הוספת Recommendations
✅ 19. הוספת Questions לצוות
✅ 20. הוספת Related Documentation
✅ 21. שמירה ואימות
✅ 22. עדכון JIRA_XRAY_NEW_TESTS.md
```

---

## 🎯 קבצים לשימוש

| קובץ | תיאור | שימוש |
|------|--------|-------|
| **XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md** | מפרט מלא ומפורט | ייבוא ידני - מקור ראשי |
| **T_DATA_002_XRAY_SUMMARY_HEBREW.md** | סיכום בעברית | הבנה מהירה |
| **XRAY_IMPORT_T_DATA_002.csv** | ייבוא CSV | ייבוא המוני |
| **JIRA_XRAY_NEW_TESTS.md** | רשימת כל הבדיקות | הקשר ומעקב |
| **T_DATA_002_HISTORICAL_VS_LIVE_REPORT.md** | דוח ביצוע מלא | תוצאות ואנליזה |
| **LIVE_VS_HISTORICAL_RECORDINGS.md** | הסבר טכני מעמיק | רקע ארכיטקטוני |

---

## 💡 טיפים

### טיפ 1: התחל מהמפרט המלא
**תמיד** התחל מ-`XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md` - זה המסמך הכי מפורט.

### טיפ 2: העתק בקטעים
אל תנסה להעתיק את הכל בבת אחת. חלק לשדות והעתק אחד אחד.

### טיפ 3: שמור גרסאות ביניים
שמור את הבדיקה ב-Jira אחרי כל כמה שדות. ככה לא תאבד מידע.

### טיפ 4: בדוק formatting
Jira עשוי לפרמט טקסט בצורה שונה. בדוק שקוד Python נשאר בפורמט נכון.

### טיפ 5: צלם screenshots
צלם screenshots של התוצאות האחרונות מה-terminal והוסף ל-Jira.

---

## 🆘 פתרון בעיות

### בעיה: לא יכול ליצור Test ב-Jira
**פתרון:** ודא שיש לך הרשאות "Create Test" בפרויקט PZ.

### בעיה: Components לא קיימים
**פתרון:** צור את ה-Components החסרים תחילה ב-Project Settings.

### בעיה: Xray API לא עובד
**פתרון:** ודא שה-Token תקף וש-Xray מותקן על הפרויקט.

### בעיה: CSV Import נכשל
**פתרון:** בדוק encoding (UTF-8) ומיפוי שדות נכון.

### בעיה: Test Steps ארוכים מדי
**פתרון:** חלק ל-2 Tests או סכם צעדים דומים.

---

## 📞 עזרה נוספת

אם נתקלת בבעיות:
1. בדוק את התיעוד הרשמי של Xray
2. פנה למנהל הפרויקט
3. שאל את רועי אברהמי (מחבר הבדיקה)

---

**✅ בהצלחה עם הייבוא!**

