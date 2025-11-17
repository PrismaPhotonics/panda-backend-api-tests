# מדריך מיפוי טסטים ידניים לטסטים אוטומטיים
## Manual Tests to Automation Tests Mapping Guide

**תאריך יצירה:** 2025-11-09  
**סטטוס:** ✅ מוכן לשימוש

---

## 🎯 מטרה

לשייך כל טסט ידני ב-Jira לטסט אוטומטי בקוד, וליצור קונפיגורציה שתאפשר להריץ את הטסטים ישירות מ-Jira.

---

## 📋 סקירה כללית

המערכת כוללת שני סקריפטים עיקריים:

1. **`map_manual_tests_to_automation.py`** - ממופה טסטים ידניים לטסטים אוטומטיים
2. **`run_tests_from_jira.py`** - מריץ טסטים מ-Jira לפי הקונפיגורציה

---

## 🚀 שימוש מהיר

### שלב 1: מיפוי טסטים ידניים

```bash
# ממופה כל הטסטים הידניים בפרויקט "Automation"
python scripts/jira/map_manual_tests_to_automation.py --project Automation

# ממופה טסט ספציפי
python scripts/jira/map_manual_tests_to_automation.py --test-id PZ-12345

# Dry run (תצוגה מקדימה בלבד)
python scripts/jira/map_manual_tests_to_automation.py --project Automation --dry-run

# מיפוי + שיוך אוטומטי + יצירת קונפיגורציה
python scripts/jira/map_manual_tests_to_automation.py --project Automation --auto-link --generate-config
```

### שלב 2: הרצת טסטים מ-Jira

```bash
# הרצת טסט ספציפי
python scripts/jira/run_tests_from_jira.py --test-id PZ-12345

# הרצת כל הטסטים במיפוי
python scripts/jira/run_tests_from_jira.py --all

# הרצת טסט פלאן
python scripts/jira/run_tests_from_jira.py --test-plan PZ-14024

# הרצה עם אופציות pytest נוספות
python scripts/jira/run_tests_from_jira.py --test-id PZ-12345 --pytest-args "-v --tb=short -x"
```

---

## 📖 הסבר מפורט

### 1. מיפוי טסטים ידניים (`map_manual_tests_to_automation.py`)

#### מה הסקריפט עושה:

1. **מחפש טסטים ידניים ב-Jira:**
   - מחפש טסטים עם `Test Type = "Manual Test"` או ללא Test Type
   - יכול לחפש בפרויקט ספציפי או בכל הפרויקטים

2. **מחפש טסטים אוטומטיים מתאימים:**
   - מחפש לפי Xray marker (`@pytest.mark.xray("PZ-12345")`)
   - מחפש לפי מילות מפתח בשם/תיאור הטסט
   - מחשב ציון התאמה (match score)

3. **משייך טסטים:**
   - מעדכן את הטסט הידני ב-Jira עם קישור לטסט האוטומטי
   - מוסיף מידע על קובץ הטסט, פונקציה, ופקודת הרצה

4. **יוצר קונפיגורציה:**
   - יוצר קובץ JSON עם כל המיפויים
   - הקובץ משמש להרצת הטסטים

#### אופציות:

```bash
--project PROJECT_KEY      # מחפש בפרויקט ספציפי (למשל: "Automation", "PZ")
--test-id TEST_ID          # ממופה טסט ספציפי (למשל: "PZ-12345")
--dry-run                  # תצוגה מקדימה בלבד, לא מעדכן Jira
--auto-link                # משייך אוטומטית טסטים ידניים לטסטים אוטומטיים
--generate-config          # יוצר קובץ קונפיגורציה
--output FILE              # שם קובץ הקונפיגורציה (ברירת מחדל: jira_test_config.json)
```

#### דוגמת פלט:

```
================================================================================
Finding Manual Tests in Jira
================================================================================
JQL Query: project = Automation AND issuetype = Test AND "customfield_10951" = "Manual Test" OR "customfield_10951" is EMPTY
Found 15 potential manual tests
Extracted 15 manual tests

Processing: PZ-12345 - Test API Endpoint Validation
  ✅ Found automation test:
     File: tests/integration/api/test_api_endpoints_high_priority.py
     Function: test_get_channels_endpoint_success
     Match Score: 0.85
  ✅ Successfully linked PZ-12345 to automation test

================================================================================
SUMMARY
================================================================================
Manual tests found: 15
Automation tests found: 12
Tests linked: 12
================================================================================
```

---

### 2. הרצת טסטים מ-Jira (`run_tests_from_jira.py`)

#### מה הסקריפט עושה:

1. **קורא קונפיגורציה:**
   - טוען את קובץ ה-JSON שנוצר בשלב המיפוי
   - מכיל את כל המיפויים בין טסטים ידניים לאוטומטיים

2. **מריץ טסטים:**
   - בונה פקודת pytest לפי המיפוי
   - מריץ את הטסטים
   - מדווח על תוצאות

3. **מדווח תוצאות:**
   - מציג סיכום של כל הטסטים
   - מציג כמה עברו, נכשלו, או דולגו

#### אופציות:

```bash
--config FILE              # קובץ קונפיגורציה (ברירת מחדל: jira_test_config.json)
--test-id TEST_ID          # הרצת טסט ספציפי
--test-plan TEST_PLAN_ID   # הרצת כל הטסטים בטסט פלאן
--all                      # הרצת כל הטסטים במיפוי
--pytest-args ARGS         # אופציות נוספות ל-pytest (למשל: "-v --tb=short")
```

#### דוגמת פלט:

```
================================================================================
Running Test: PZ-12345
================================================================================
Command: pytest tests/integration/api/test_api_endpoints_high_priority.py::test_get_channels_endpoint_success -v

test_api_endpoints_high_priority.py::test_get_channels_endpoint_success PASSED

✅ Test PZ-12345 PASSED
```

---

## 📁 מבנה קובץ הקונפיגורציה

קובץ `jira_test_config.json` שנוצר נראה כך:

```json
{
  "version": "1.0",
  "generated_at": "2025-11-09T15:30:00",
  "mappings": [
    {
      "manual_test": {
        "key": "PZ-12345",
        "summary": "Test API Endpoint Validation",
        "description": "Test that API endpoint returns correct data",
        "test_type": "Manual Test",
        "status": "To Do",
        "project": "PZ",
        "url": "https://prismaphotonics.atlassian.net/browse/PZ-12345"
      },
      "automation_test": {
        "file": "tests/integration/api/test_api_endpoints_high_priority.py",
        "file_path": "C:\\Projects\\focus_server_automation\\tests\\integration\\api\\test_api_endpoints_high_priority.py",
        "test_function": "test_get_channels_endpoint_success",
        "match_score": 0.85,
        "match_method": "xray_marker"
      },
      "mapped_at": "2025-11-09T15:30:00"
    }
  ],
  "test_execution": {
    "default_command": "pytest",
    "default_flags": ["-v", "--tb=short"],
    "test_plan_format": "jira_test_plan_{test_plan_id}.json"
  }
}
```

---

## 🔍 איך הסקריפט מוצא טסטים אוטומטיים?

הסקריפט משתמש בכמה אסטרטגיות:

### 1. חיפוש לפי Xray Marker (הכי מדויק)
```python
@pytest.mark.xray("PZ-12345")
def test_something():
    ...
```

### 2. חיפוש לפי מילות מפתח
- מחלץ מילות מפתח משם/תיאור הטסט הידני
- מחפש בקובצי הטסטים
- מחשב ציון התאמה

### 3. חיפוש לפי שם פונקציה
- מחפש פונקציות שמתחילות ב-`test_`
- בודק התאמה לשם הטסט

---

## ⚙️ הגדרות מתקדמות

### עדכון Test Type ב-Jira

אם הטסטים הידניים לא מסומנים כ-"Manual Test", אפשר לעדכן אותם:

```python
from external.jira import JiraClient

client = JiraClient()
issue = client.get_issue("PZ-12345")
issue.update(fields={'customfield_10951': {'value': 'Manual Test'}})
```

### שימוש ב-Custom Field לשיוך

אם יש custom field מיוחד לשיוך טסטים אוטומטיים, אפשר לעדכן את הסקריפט:

```python
# ב-map_manual_tests_to_automation.py
AUTOMATION_TEST_ID_FIELD = "customfield_XXXXX"  # עדכן לפי ה-ID שלך
```

---

## 📊 דוגמת Workflow מלא

```bash
# 1. ממופה כל הטסטים הידניים בפרויקט Automation
python scripts/jira/map_manual_tests_to_automation.py \
    --project Automation \
    --auto-link \
    --generate-config

# 2. בודק את הקונפיגורציה שנוצרה
cat jira_test_config.json | python -m json.tool

# 3. מריץ טסט ספציפי
python scripts/jira/run_tests_from_jira.py --test-id PZ-12345

# 4. מריץ את כל הטסטים במיפוי
python scripts/jira/run_tests_from_jira.py --all

# 5. מריץ טסט פלאן
python scripts/jira/run_tests_from_jira.py --test-plan PZ-14024
```

---

## 🐛 פתרון בעיות

### בעיה: "No manual tests found"

**פתרון:**
- בדוק שהפרויקט קיים: `--project Automation`
- בדוק שה-Test Type field נכון
- נסה לחפש ללא פילטר: `--project PZ`

### בעיה: "No automation test found"

**פתרון:**
- ודא שיש Xray marker בטסט האוטומטי
- בדוק שהשם/תיאור הטסט הידני תואם לטסט האוטומטי
- נסה לשפר את התיאור ב-Jira

### בעיה: "Configuration file not found"

**פתרון:**
- הרץ קודם את `map_manual_tests_to_automation.py` עם `--generate-config`
- או ציין קובץ קונפיגורציה אחר: `--config my_config.json`

---

## 📝 הערות חשובות

1. **Xray Markers:** הסקריפט עובד הכי טוב כשיש Xray markers בטסטים האוטומטיים
2. **Test Type Field:** ודא שה-Test Type field מוגדר נכון ב-Jira
3. **קונפיגורציה:** הקובץ `jira_test_config.json` נשמר בפרויקט root
4. **Dry Run:** תמיד מומלץ להריץ קודם עם `--dry-run` לראות מה יקרה

---

## 🔗 קישורים רלוונטיים

- [Xray Mapping Documentation](../04_testing/xray_mapping/README.md)
- [Jira Integration Guide](./JIRA_INTEGRATION_GUIDE.md)
- [Test Execution Guide](../04_testing/test_execution/README.md)

---

**עודכן:** 2025-11-09  
**מחבר:** QA Automation Team

