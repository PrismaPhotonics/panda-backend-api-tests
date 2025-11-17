# 📊 דוגמה: יצירת ריפורט עם מיפוי באגים

**תאריך:** 2025-11-08

---

## 🚀 שימוש

### הרצת טסטים עם יצירת ריפורט:

```bash
# JSON report (default)
pytest --generate-jira-report

# Markdown report
pytest --generate-jira-report --jira-report-format=markdown

# Custom path
pytest --generate-jira-report --jira-report-path=reports/my_report.json
```

---

## 📝 דוגמה מלאה

### 1. הרצת טסטים

```bash
pytest tests/integration/api/ --generate-jira-report --jira-report-path=reports/test_report.json
```

### 2. התוצאה

המנגנון:
1. ✅ אוסף את כל הכשלונות
2. ✅ מחפש באגים דומים ב-Jira
3. ✅ ממפה כשלונות לבאגים קיימים
4. ✅ מזהה באגים חדשים שצריך ליצור
5. ✅ יוצר ריפורט ב-`reports/test_report.json` ו-`reports/test_report.md`

### 3. הריפורט

**JSON Report (`reports/test_report.json`):**
```json
{
  "execution_info": {
    "total_tests": 193,
    "passed": 163,
    "failed": 12,
    "skipped": 18,
    "duration_seconds": 1158.59
  },
  "mapped_bugs": [
    {
      "bug_key": "PZ-14712",
      "bug_url": "https://prismaphotonics.atlassian.net/browse/PZ-14712",
      "bug_summary": "MongoDB connection failure",
      "bug_status": "Open",
      "similarity_score": 0.85,
      "test_name": "test_mongodb_connection",
      "error_message": "Connection failed: timeout"
    }
  ],
  "new_bugs_needed": [
    {
      "test_name": "test_new_issue",
      "error_type": "AssertionError",
      "error_message": "Test assertion failed",
      "suggested_summary": "New issue found in test_new_issue",
      "keywords": ["new", "issue", "test"]
    }
  ]
}
```

**Markdown Report (`reports/test_report.md`):**
```markdown
# 📊 Test Execution Report

**Generated:** 2025-11-08 16:40:00

## 📈 Execution Summary

- **Total Tests:** 193
- **Passed:** ✅ 163
- **Failed:** ❌ 12
- **Skipped:** ⏭️ 18
- **Duration:** 1158.59 seconds

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
- **Error:** `Connection failed: timeout`

## ⚠️ New Bugs Needed

### test_new_issue
- **Error Type:** `AssertionError`
- **Error Message:** `Test assertion failed`
- **Suggested Summary:** New issue found in test_new_issue
- **Keywords:** new, issue, test
```

---

## 🎯 מה הריפורט כולל?

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
- Error message

### 3. New Bugs Needed
- Test name
- Error type and message
- Suggested summary
- Keywords

### 4. All Failures
- Full failure details
- Error type and message
- Traceback (if available)
- Duration

---

## 🔧 שימוש Programmatic

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

---

**עודכן:** 2025-11-08

