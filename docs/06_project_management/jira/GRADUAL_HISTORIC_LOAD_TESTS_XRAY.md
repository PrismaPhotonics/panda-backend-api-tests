# Gradual Historic Load Tests - Xray/Jira Tickets

## 📋 סקירה כללית

סקריפט ליצירת טיקטים ב-Xray/Jira עבור טסטי Gradual Historic Load.

## 🎯 טסטים שנוצרים

| Test ID | Summary | Priority | Xray Marker |
|---------|---------|----------|-------------|
| LOAD-400 | Load - Historic - Gradual Load to 100 Jobs | High | PZ-LOAD-400 |
| LOAD-401 | Load - Historic - Quick Gradual Load (2→10 Jobs) | Medium | PZ-LOAD-401 |
| LOAD-402 | Load - Historic - Gradual Load Health Tracking | High | PZ-LOAD-402 |
| LOAD-403 | Load - Historic - Gradual Load Cleanup Verification | High | PZ-LOAD-403 |
| LOAD-410 | Load - Historic - High Concurrency Gradual Load | Medium | PZ-LOAD-410 |

**סה"כ: 5 טסטים**

## 🚀 שימוש

### Dry Run (תצוגה מקדימה)

```bash
python scripts/jira/create_gradual_historic_load_tests.py --dry-run
```

זה יציג את כל הטסטים שייווצרו בלי ליצור אותם בפועל.

### יצירה בפועל

```bash
python scripts/jira/create_gradual_historic_load_tests.py
```

זה יוצר את כל הטסטים ב-Jira Xray.

## 📝 דרישות

1. **JIRA_API_TOKEN**: צריך להיות מוגדר ב-environment variables
2. **Jira Client**: הסקריפט משתמש ב-`external.jira.JiraClient`
3. **Project Key**: PZ (מוגדר אוטומטית)

## 📊 פרטי הטסטים

### PZ-LOAD-400: Gradual Load to 100 Jobs

**תיאור:**
טסט מלא של gradual load מ-5 ל-100 jobs עם אותם אינטרוולים כמו טסטי Live:
- Initial: 5 jobs
- Step: +5 jobs כל 10 שניות
- Max: 100 jobs

**Labels:**
- load, historic, gradual_load, capacity, automation, job_load, mongodb

**Components:**
- focus-server, grpc, mongodb

### PZ-LOAD-401: Quick Gradual Load

**תיאור:**
גרסה מהירה ל-CI/CD:
- Initial: 2 jobs
- Step: +2 jobs כל 5 שניות
- Max: 10 jobs

**Labels:**
- load, historic, gradual_load, quick, ci, automation, job_load

**Components:**
- focus-server, grpc

### PZ-LOAD-402: Health Tracking

**תיאור:**
מעקב אחר בריאות המערכת במהלך gradual load increase.

**Labels:**
- load, historic, gradual_load, health, monitoring, automation, job_load

**Components:**
- focus-server, grpc, monitoring

### PZ-LOAD-403: Cleanup Verification

**תיאור:**
וידוא ניקוי תקין אחרי הטסט.

**Labels:**
- load, historic, gradual_load, cleanup, resource_management, automation, job_load

**Components:**
- focus-server, grpc, kubernetes

### PZ-LOAD-410: High Concurrency

**תיאור:**
Gradual load עם steps גדולים יותר:
- Initial: 10 jobs
- Step: +10 jobs כל 8 שניות
- Max: 100 jobs

**Labels:**
- load, historic, gradual_load, high_concurrency, scalability, automation, job_load

**Components:**
- focus-server, grpc

## 🔧 תצורת Test Type

כל הטסטים נוצרים עם:
- **Issue Type**: Test
- **Test Type**: Automation (customfield_10951)
- **Project**: PZ

## 📚 קישורים

- **Test File**: `be_focus_server_tests/load/test_gradual_historic_load.py`
- **Script**: `scripts/jira/create_gradual_historic_load_tests.py`
- **Documentation**: `docs/04_testing/load_tests/GRADUAL_HISTORIC_LOAD_TESTING.md`

## 🔄 עדכון טסטים

אם צריך לעדכן טסט קיים:
1. עדכן את ה-description ב-`GRADUAL_HISTORIC_LOAD_TESTS` dictionary
2. הרץ את הסקריפט שוב (הוא לא יוצר duplicates)
3. או עדכן ידנית ב-Jira

## ✅ וידוא

לאחר יצירת הטסטים:
1. בדוק ב-Jira שהטסטים נוצרו
2. וודא שה-Test Type = "Automation"
3. בדוק שה-labels וה-components נכונים
4. קשר את הטסטים ל-test plan הרלוונטי

## 📝 הערות

- הטסטים משתמשים ב-MongoDB base_paths collection
- האינטרוולים זהים לטסטי Live (להשוואה)
- כל הטסטים הם automated tests
- הטסטים מסומנים כ-slow tests (מלבד LOAD-401)

