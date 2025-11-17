# מדריך Jira Agent עבור Cursor
## Cursor Jira Agent Guide

**תאריך:** 2025-11-04  
**גרסה:** 1.0.0  
**מחבר:** QA Automation Architect

---

## 🎯 מבוא

Jira Agent הוא ממשק פשוט ונוח לעבודה עם Jira דרך Cursor. הוא מאפשר לך לבקש ממני ליצור טיקטים, לחפש טיקטים, לעדכן טיקטים וכו' - והכל יעבוד אוטומטית.

---

## 🚀 שימוש מהיר

### דרך Cursor Chat

פשוט בקש ממני:

```
"צור באג עבור API endpoint /channels שמחזיר 500"
"הראה לי את כל הבאגים הפתוחים בפרויקט PZ"
"עדכן את הטיקט PZ-12345 לסטטוס 'In Progress'"
"חפש את כל הטיקטים שהוקצו לי"
```

### דרך Python Code

```python
from external.jira import JiraAgent

# אתחול Agent
agent = JiraAgent()

# יצירת באג
issue = agent.create_bug(
    summary="API endpoint returns 500",
    description="The /channels endpoint fails with 500 error",
    priority="High",
    labels=["bug", "api", "critical"]
)

# חיפוש טיקטים
issues = agent.get_open_issues()

# עדכון סטטוס
agent.update_status("PZ-12345", "In Progress")
```

### דרך Command Line

```bash
# יצירת באג
python scripts/jira/cursor_jira_agent.py create-bug "API endpoint returns 500" "The /channels endpoint fails"

# חיפוש טיקטים
python scripts/jira/cursor_jira_agent.py search "project = PZ AND status != Done"

# קריאת טיקט
python scripts/jira/cursor_jira_agent.py get PZ-12345

# עדכון סטטוס
python scripts/jira/cursor_jira_agent.py update-status PZ-12345 "In Progress"

# קבלת כל הטיקטים הפתוחים
python scripts/jira/cursor_jira_agent.py open-issues

# קבלת הטיקטים שלי
python scripts/jira/cursor_jira_agent.py my-issues

# קבלת כל הבאגים
python scripts/jira/cursor_jira_agent.py bugs
```

---

## 📋 פקודות זמינות

### יצירת טיקטים

#### יצירת באג
```python
agent = JiraAgent()

issue = agent.create_bug(
    summary="באג באנדפוינט",
    description="האנדפוינט /channels מחזיר 500",
    priority="High",
    labels=["bug", "api"],
    assignee="john.doe"
)
```

#### יצירת Task
```python
issue = agent.create_task(
    summary="Task חדש",
    description="תיאור המשימה",
    priority="Medium",
    labels=["automation"]
)
```

#### יצירת Story
```python
issue = agent.create_story(
    summary="Story חדש",
    description="תיאור הסיפור",
    priority="Medium"
)
```

#### יצירת Sub-task
```python
issue = agent.create_subtask(
    parent_key="PZ-12345",
    summary="תת-משימה",
    description="תיאור תת-המשימה",
    priority="Medium"
)
```

### קריאת טיקטים

#### קבלת טיקט בודד
```python
issue = agent.get_issue("PZ-12345")
print(f"Status: {issue['status']}")
print(f"Priority: {issue['priority']}")
```

#### קבלת כל הטיקטים הפתוחים
```python
issues = agent.get_open_issues()
for issue in issues:
    print(f"{issue['key']}: {issue['summary']}")
```

#### קבלת הטיקטים שלי
```python
issues = agent.get_my_open_issues()
for issue in issues:
    print(f"{issue['key']}: {issue['summary']}")
```

#### קבלת כל הבאגים
```python
bugs = agent.get_bugs()
for bug in bugs:
    print(f"{bug['key']}: {bug['summary']}")
```

#### חיפוש מתקדם
```python
# חיפוש באמצעות JQL
issues = agent.search(
    "project = PZ AND type = Bug AND priority = High"
)

# חיפוש עם הגבלת תוצאות
issues = agent.search(
    "project = PZ AND status != Done",
    max_results=50
)
```

### עדכון טיקטים

#### עדכון סטטוס
```python
# מעבר לסטטוס "In Progress"
agent.update_status("PZ-12345", "In Progress")

# סגירת טיקט
agent.update_status("PZ-12345", "Done")
```

#### עדכון עדיפות
```python
agent.update_priority("PZ-12345", "High")
```

#### עדכון ממונה
```python
agent.update_assignee("PZ-12345", "john.doe")
```

#### הוספת תגיות
```python
agent.add_labels("PZ-12345", ["critical", "urgent", "api"])
```

#### הוספת הערה
```python
agent.add_comment(
    "PZ-12345",
    "הבאג תוקן ב-commit abc123. יש לבדוק שוב."
)
```

---

## 💡 דוגמאות שימוש

### יצירת באג מתוך כישלון טסט

```python
from external.jira import JiraAgent

agent = JiraAgent()

def create_bug_from_test_failure(test_name: str, error_message: str):
    """יצירת באג מתוך כישלון טסט"""
    issue = agent.create_bug(
        summary=f"Test Failure: {test_name}",
        description=f"""
## כישלון בטסט
**טסט:** `{test_name}`

## שגיאה
```
{error_message}
```

## פעולות נדרשות
1. לבדוק את הקוד הרלוונטי
2. לתקן את הבאג
3. להריץ את הטסט שוב
        """,
        priority="High",
        labels=["bug", "automation", "test-failure"]
    )
    return issue

# שימוש
create_bug_from_test_failure(
    "test_api_endpoint",
    "AssertionError: Expected 200, got 500"
)
```

### סנכרון טיקטים עם תוצאות טסטים

```python
from external.jira import JiraAgent
import pytest

agent = JiraAgent()

# לאחר הרצת טסטים
if pytest_session.failures:
    for test_name, error in pytest_session.failures.items():
        agent.create_bug(
            summary=f"Test Failure: {test_name}",
            description=f"Test failed with error: {str(error)}",
            priority="High",
            labels=["bug", "automation", "test-failure"]
        )
```

### ניתוח וסיכום טיקטים

```python
from external.jira import JiraAgent
from collections import defaultdict

agent = JiraAgent()

# קבלת כל הבאגים הפתוחים
bugs = agent.get_bugs()

# ניתוח לפי עדיפות
by_priority = defaultdict(int)
for bug in bugs:
    priority = bug['priority'] or 'Unassigned'
    by_priority[priority] += 1

print("באגים לפי עדיפות:")
for priority, count in sorted(by_priority.items()):
    print(f"  {priority}: {count}")

# ניתוח לפי ממונה
by_assignee = defaultdict(int)
for bug in bugs:
    assignee = bug['assignee'] or 'Unassigned'
    by_assignee[assignee] += 1

print("\nבאגים לפי ממונה:")
for assignee, count in sorted(by_assignee.items()):
    print(f"  {assignee}: {count}")
```

---

## 🔧 הגדרה

### קונפיגורציה

הקונפיגורציה כבר מוגדרת עם:
- **Jira URL:** `https://prismaphotonics.atlassian.net`
- **Email:** `roy.avrahami@prismaphotonics.com`
- **API Token:** כבר מוגדר בקובץ `config/jira_config.yaml`

### אימות

המערכת משתמשת ב-API Token עבור אימות. אין צורך לעדכן כלום - הכל כבר מוגדר!

---

## 📚 מסמכים נוספים

- **מדריך אינטגרציה מלא:** `docs/06_project_management/jira/JIRA_INTEGRATION_GUIDE.md`
- **JiraClient:** `external/jira/jira_client.py`
- **JiraAgent:** `external/jira/jira_agent.py`

---

## ✅ סיכום

Jira Agent מספק:

- ✅ **ממשק פשוט** - עבודה קלה עם Jira דרך Cursor
- ✅ **יצירת טיקטים** - Bugs, Tasks, Stories, Sub-tasks
- ✅ **חיפוש וקריאה** - JQL, Filters מוגדרים מראש
- ✅ **עדכון טיקטים** - סטטוס, עדיפות, ממונה, תגיות
- ✅ **Command Line** - Scripts שורת פקודה
- ✅ **Python API** - ממשק תכנותי מלא

**הפתרון מוכן לשימוש כ-Agent דרך Cursor!**

---

**תאריך עדכון:** 2025-11-04  
**גרסה:** 1.0.0

