# 📊 יצירת ריפורט עם מיפוי באגים ל-Jira

**תאריך:** 2025-11-08

---

## 📋 סקירה כללית

מנגנון אוטומטי שיוצר ריפורט על ריצת טסטים וממפה כשלונות טסטים לבאגים קיימים ב-Jira.

**תכונות:**
- ✅ איסוף אוטומטי של כשלונות טסטים
- ✅ מיפוי לבאגים קיימים ב-Jira
- ✅ זיהוי באגים חדשים שצריך ליצור
- ✅ יצירת ריפורט JSON ו-Markdown

---

## 🚀 שימוש מהיר

### הרצת טסטים עם יצירת ריפורט:

```bash
# JSON report
pytest --generate-jira-report --jira-report-path=reports/test_report.json

# Markdown report
pytest --generate-jira-report --jira-report-format=markdown --jira-report-path=reports/test_report.md
```

---

## 📝 דוגמה

### 1. הרצת טסטים

```bash
pytest tests/integration/api/ --generate-jira-report
```

### 2. התוצאה

המנגנון:
1. ✅ אוסף את כל הכשלונות
2. ✅ מחפש באגים דומים ב-Jira
3. ✅ ממפה כשלונות לבאגים קיימים
4. ✅ מזהה באגים חדשים שצריך ליצור
5. ✅ יוצר ריפורט ב-`reports/test_report.json` ו-`reports/test_report.md`

### 3. הריפורט

הריפורט יכלול:

**JSON Report:**
```json
{
  "execution_info": {
    "total_tests": 193,
    "passed": 163,
    "failed": 12,
    "skipped": 18
  },
  "mapped_bugs": [
    {
      "bug_key": "PZ-14712",
      "bug_url": "https://prismaphotonics.atlassian.net/browse/PZ-14712",
      "bug_summary": "MongoDB connection failure",
      "bug_status": "Open",
      "similarity_score": 0.85,
      "test_name": "test_mongodb_connection"
    }
  ],
  "new_bugs_needed": [
    {
      "test_name": "test_new_issue",
      "suggested_summary": "New issue found",
      "keywords": ["new", "issue"]
    }
  ]
}
```

**Markdown Report:**
```markdown
# 📊 Test Execution Report

## 📈 Execution Summary
- **Total Tests:** 193
- **Passed:** ✅ 163
- **Failed:** ❌ 12
- **Skipped:** ⏭️ 18

## 🐛 Bug Mapping Summary
- **Total Failures:** 12
- **Mapped to Existing Bugs:** ✅ 8
- **New Bugs Needed:** ⚠️ 4

## ✅ Failures Mapped to Existing Bugs

### test_mongodb_connection
- **Bug:** [PZ-14712](https://prismaphotonics.atlassian.net/browse/PZ-14712)
- **Summary:** MongoDB connection failure
- **Status:** Open
- **Similarity Score:** 0.85
```

---

## ⚙️ הגדרות

### Command Line Options:

```bash
# Enable Jira report generation
--generate-jira-report

# Set report path (default: reports/test_report.json)
--jira-report-path=reports/my_report.json

# Set report format (default: json)
--jira-report-format=json  # or markdown
```

### דוגמאות:

```bash
# JSON report
pytest --generate-jira-report --jira-report-path=reports/test_report.json

# Markdown report
pytest --generate-jira-report --jira-report-format=markdown

# Custom path
pytest --generate-jira-report --jira-report-path=reports/2025-11-08_report.json
```

---

## 🔧 שימוש Programmatic

### דוגמה 1: יצירת ריפורט ידנית

```python
from src.reporting.test_report_generator import TestReportGenerator

# Initialize generator
generator = TestReportGenerator()

# Add failures
generator.add_failure(
    test_name="test_mongodb_connection",
    error_message="Connection failed: timeout",
    error_type="ConnectionError"
)

# Map to existing bugs
generator.map_failures_to_bugs()

# Generate and save report
generator.save_report("reports/test_report.json", format="json")
generator.save_report("reports/test_report.md", format="markdown")
```

### דוגמה 2: קריאת ריפורט

```python
import json

# Read JSON report
with open("reports/test_report.json", "r") as f:
    report = json.load(f)

# Check mapped bugs
for bug_info in report["mapped_bugs"]:
    print(f"✅ {bug_info['test_name']} → {bug_info['bug_key']}")

# Check new bugs needed
for bug_info in report["new_bugs_needed"]:
    print(f"⚠️  {bug_info['test_name']} - needs new bug")
```

---

## 📊 מה הריפורט כולל?

### 1. Execution Info
- Total tests
- Passed/Failed/Skipped counts
- Duration
- Start/End time

### 2. Mapped Bugs
- Test name
- Bug key and URL
- Bug summary and status
- Similarity score

### 3. New Bugs Needed
- Test name
- Error message
- Suggested summary
- Keywords

### 4. All Failures
- Full failure details
- Error type and message
- Traceback (if available)
- Duration

---

## 🎯 יתרונות

1. **אוטומציה מלאה** - לא צריך לבדוק ידנית
2. **מיפוי חכם** - מוצא באגים דומים אוטומטית
3. **ריפורט מפורט** - כל המידע במקום אחד
4. **JSON + Markdown** - שני פורמטים לשימוש
5. **Integration** - עובד אוטומטית עם pytest

---

## ⚠️ הערות

1. **Jira Connection** - צריך חיבור ל-Jira (configured in `config/jira_config.yaml`)
2. **Performance** - חיפוש באגים יכול לקחת זמן (uses cache)
3. **Similarity Threshold** - ברירת מחדל 0.7 (ניתן לשנות)

---

## 📚 קבצים

- `src/reporting/test_report_generator.py` - Generator class
- `src/reporting/pytest_integration.py` - Pytest hooks
- `reports/test_report.json` - JSON report (generated)
- `reports/test_report.md` - Markdown report (generated)

---

**עודכן:** 2025-11-08

