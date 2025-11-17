# מדריך אינטגרציה מלא עם Jira
## Jira Integration Guide - Complete Hebrew Documentation

**תאריך:** 2025-11-04  
**גרסה:** 1.0.0  
**מחבר:** QA Automation Architect

---

## 📋 תוכן עניינים

1. [מבוא](#מבוא)
2. [התקנה והגדרה](#התקנה-והגדרה)
3. [שימוש ב-JiraClient](#שימוש-ב-jiraclient)
4. [יצירת טיקטים](#יצירת-טיקטים)
5. [חיפוש וקריאת טיקטים](#חיפוש-וקריאת-טיקטים)
6. [עדכון טיקטים](#עדכון-טיקטים)
7. [Scripts שימושיים](#scripts-שימושיים)
8. [דוגמאות מתקדמות](#דוגמאות-מתקדמות)
9. [טיפים ובטיחות](#טיפים-ובטיחות)

---

## 🎯 מבוא

המערכת מספקת אינטגרציה מלאה עם Jira API עבור יצירה, קריאה, עדכון וחיפוש של טיקטים ומשימות.

### תכונות עיקריות

- ✅ **יצירת טיקטים** - Tasks, Bugs, Stories, Epics, Sub-tasks
- ✅ **חיפוש מתקדם** - חיפוש באמצעות JQL (Jira Query Language)
- ✅ **עדכון טיקטים** - עדכון שדות, שינוי סטטוס, הוספת הערות
- ✅ **תבניות מוכנות** - יצירת טיקטים באמצעות תבניות מוגדרות מראש
- ✅ **ניהול פרויקטים** - קבלת מידע על פרויקטים, שדות, וסוגי טיקטים
- ✅ **Scripts שימושיים** - כלים שורת פקודה לעבודה מהירה

---

## 🔧 התקנה והגדרה

### 1. התקנת תלויות

```bash
pip install -r requirements.txt
```

הספרייה `jira>=3.5.0` תותקן אוטומטית.

### 2. הגדרת קונפיגורציה

ערוך את הקובץ `config/jira_config.yaml`:

```yaml
jira:
  # עדכן את ה-URL של Jira שלך
  base_url: "https://your-company.atlassian.net"
  
  # API Token (כבר מוגדר)
  api_token: "ATATT3xFfGF01lXkpLEMF151x_N8f90jc0FMf9oVwSiVV1P0XyTxgcef6UxNE8ZjfCGC7Aoy-xTVeUcorZIxYhpibV5JnkCvILpv9Rq27Hhg0dQX_I1M05mYp4ABAX6e81jYP7MuMEG11mmZj9rm-w_3RlSPdFUErttiQw8shWTEolFT6wVGW-M=22FE4F76"
  
  # Email (חובה עבור Jira Cloud)
  email: "your-email@company.com"
  
  # Project Key
  project_key: "PZ"
```

### 3. קביעת URL של Jira

**חשוב:** עדכן את `base_url` בקובץ הקונפיגורציה ל-URL של Jira שלך:

- **Jira Cloud:** `https://your-company.atlassian.net`
- **Jira Server:** `https://jira.your-company.com`
- **Jira Data Center:** `https://jira.your-company.com`

---

## 🚀 שימוש ב-JiraClient

### אתחול בסיסי

```python
from external.jira import JiraClient

# אתחול עם קונפיגורציה ברירת מחדל
client = JiraClient()

# אתחול עם פרמטרים מותאמים
client = JiraClient(
    base_url="https://your-company.atlassian.net",
    api_token="your-api-token",
    email="your-email@company.com",
    project_key="PZ"
)
```

### בדיקת חיבור

```python
from external.jira import JiraClient

client = JiraClient()
# החיבור נבדק אוטומטית בעת האתחול
# אם יש שגיאה, תתקבל חריגה ConnectionError
```

---

## 📝 יצירת טיקטים

### יצירת Task פשוט

```python
from external.jira import JiraClient

client = JiraClient()

# יצירת Task
issue = client.create_issue(
    summary="באג באנדפוינט /channels",
    description="האנדפוינט /channels מחזיר שגיאה 500",
    issue_type="Task",
    priority="High",
    labels=["bug", "api", "critical"]
)

print(f"נוצר טיקט: {issue['key']}")
print(f"URL: {issue['url']}")
```

### יצירת Bug

```python
issue = client.create_issue(
    summary="באג באנדפוינט /channels",
    description="""
    ## תיאור הבעיה
    האנדפוינט /channels מחזיר שגיאה 500 כאשר יש יותר מ-1000 ערוצים.
    
    ## שלבים לשחזור
    1. שליחת GET request ל-/channels
    2. כאשר יש יותר מ-1000 ערוצים, השרת מחזיר 500
    
    ## התנהגות צפויה
    השרת אמור להחזיר רשימת ערוצים בהצלחה.
    """,
    issue_type="Bug",
    priority="High",
    labels=["bug", "api", "critical"],
    assignee="john.doe"
)
```

### יצירת Sub-task

```python
# יצירת Sub-task תחת טיקט קיים
sub_task = client.create_issue(
    summary="תת-משימה: בדיקת תקינות API",
    description="ביצוע בדיקות תקינות עבור האנדפוינט /channels",
    issue_type="Sub-task",
    parent_key="PZ-12345",  # מפתח הטיקט ההורה
    priority="Medium",
    labels=["testing", "api"]
)
```

### יצירה באמצעות תבנית

```python
# יצירת Bug באמצעות תבנית
issue = client.create_issue_from_template(
    template_name="bug",
    summary="באג באנדפוינט",
    description="תיאור הבאג כאן",
    priority="High"  # דורס את ברירת המחדל של התבנית
)
```

---

## 🔍 חיפוש וקריאת טיקטים

### חיפוש באמצעות JQL

```python
# חיפוש כל הטיקטים הפתוחים בפרויקט
issues = client.search_issues("project = PZ AND status != Done")

# חיפוש באגים עם עדיפות גבוהה
issues = client.search_issues(
    "project = PZ AND type = Bug AND priority = High AND status != Done"
)

# חיפוש טיקטים שהוקצו לי
issues = client.search_issues(
    "project = PZ AND assignee = currentUser() AND status != Done"
)

# חיפוש טיקטים שנוצרו השבוע
issues = client.search_issues(
    "project = PZ AND created >= startOfWeek()"
)

for issue in issues:
    print(f"{issue['key']}: {issue['summary']} ({issue['status']})")
```

### חיפוש באמצעות Filters מוגדרים מראש

```python
# כל הטיקטים הפתוחים שלי
issues = client.get_my_open_issues()

# כל הטיקטים הפתוחים בפרויקט
issues = client.get_project_open_issues(project_key="PZ")

# כל הבאגים בפרויקט
issues = client.get_project_bugs(project_key="PZ")

# חיפוש באמצעות filter מותאם
issues = client.search_issues_by_filter(
    filter_name="this_week",
    project_key="PZ"
)
```

### קריאת טיקט בודד

```python
# קבלת פרטי טיקט
issue = client.get_issue("PZ-12345")

print(f"מפתח: {issue['key']}")
print(f"סיכום: {issue['summary']}")
print(f"סטטוס: {issue['status']}")
print(f"עדיפות: {issue['priority']}")
print(f"ממונה: {issue['assignee']}")
print(f"תיאור: {issue['description']}")
print(f"URL: {issue['url']}")
```

### קריאת מספר טיקטים

```python
# קבלת מספר טיקטים בבת אחת
issues = client.get_issues_by_keys([
    "PZ-12345",
    "PZ-12346",
    "PZ-12347"
])

for issue in issues:
    print(f"{issue['key']}: {issue['summary']}")
```

---

## ✏️ עדכון טיקטים

### עדכון שדות בסיסיים

```python
# עדכון עדיפות וסטטוס
updated = client.update_issue(
    issue_key="PZ-12345",
    priority="High",
    status="In Progress"
)

# עדכון ממונה ותגיות
updated = client.update_issue(
    issue_key="PZ-12345",
    assignee="john.doe",
    labels=["critical", "urgent", "api"]
)

# עדכון סיכום ותיאור
updated = client.update_issue(
    issue_key="PZ-12345",
    summary="סיכום מעודכן",
    description="תיאור מעודכן"
)
```

### שינוי סטטוס

```python
# מעבר לסטטוס "In Progress"
client.transition_issue("PZ-12345", "In Progress")

# סגירת טיקט
client.transition_issue("PZ-12345", "Done")

# מעבר לסטטוס "In Review"
client.transition_issue("PZ-12345", "In Review")
```

### הוספת הערה

```python
# הוספת הערה לטיקט
comment = client.add_comment(
    issue_key="PZ-12345",
    comment="הבאג תוקן ב-commit abc123. יש לבדוק שוב."
)

print(f"הערה נוספה: {comment['id']}")
print(f"מחבר: {comment['author']}")
```

---

## 🛠️ Scripts שימושיים

### יצירת טיקט

```bash
# יצירת Task פשוט
python scripts/jira/create_jira_issue.py --summary "Task חדש" --type Task

# יצירת Bug
python scripts/jira/create_jira_issue.py --summary "באג באנדפוינט" --type Bug --priority High --labels bug,api

# יצירה באמצעות תבנית
python scripts/jira/create_jira_issue.py --template bug --summary "באג קריטי" --description "תיאור הבאג"

# יצירת Sub-task
python scripts/jira/create_jira_issue.py --summary "תת-משימה" --type "Sub-task" --parent PZ-12345
```

### חיפוש טיקטים

```bash
# חיפוש באמצעות JQL
python scripts/jira/search_jira_issues.py --jql "project = PZ AND status != Done"

# חיפוש באמצעות filter
python scripts/jira/search_jira_issues.py --filter my_open
python scripts/jira/search_jira_issues.py --filter project_open --project PZ

# חיפוש מפורט
python scripts/jira/search_jira_issues.py --filter project_bugs --detailed
```

### קריאת טיקט

```bash
# קריאת טיקט בודד
python scripts/jira/get_jira_issue.py PZ-12345

# קריאת טיקט מפורט
python scripts/jira/get_jira_issue.py --key PZ-12345 --detailed

# קריאת מספר טיקטים
python scripts/jira/get_jira_issue.py --keys PZ-12345,PZ-12346,PZ-12347
```

### עדכון טיקט

```bash
# עדכון עדיפות וסטטוס
python scripts/jira/update_jira_issue.py PZ-12345 --priority High --status "In Progress"

# עדכון ממונה ותגיות
python scripts/jira/update_jira_issue.py PZ-12345 --assignee john.doe --labels critical,urgent

# עדכון סיכום ותיאור
python scripts/jira/update_jira_issue.py PZ-12345 --summary "סיכום מעודכן" --description "תיאור מעודכן"
```

---

## 💡 דוגמאות מתקדמות

### יצירת מספר טיקטים מתוך רשימה

```python
from external.jira import JiraClient

client = JiraClient()

tasks = [
    {"summary": "Task 1", "description": "תיאור 1", "priority": "High"},
    {"summary": "Task 2", "description": "תיאור 2", "priority": "Medium"},
    {"summary": "Task 3", "description": "תיאור 3", "priority": "Low"}
]

created_issues = []
for task in tasks:
    issue = client.create_issue(
        summary=task["summary"],
        description=task["description"],
        issue_type="Task",
        priority=task["priority"],
        labels=["automation", "qa"]
    )
    created_issues.append(issue)
    print(f"נוצר: {issue['key']}")

print(f"\nסה\"כ נוצרו {len(created_issues)} טיקטים")
```

### יצירת טיקטים מתוך קובץ

```python
import json
from external.jira import JiraClient

client = JiraClient()

# קריאת קובץ JSON עם טיקטים
with open("tasks.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

for task in tasks:
    issue = client.create_issue(
        summary=task["summary"],
        description=task.get("description", ""),
        issue_type=task.get("type", "Task"),
        priority=task.get("priority", "Medium"),
        labels=task.get("labels", [])
    )
    print(f"נוצר: {issue['key']} - {issue['summary']}")
```

### סנכרון טיקטים עם תוצאות טסטים

```python
from external.jira import JiraClient
import pytest

client = JiraClient()

# לאחר הרצת טסטים
def create_bug_from_test_failure(test_name: str, error_message: str):
    """יצירת באג מתוך כישלון טסט"""
    issue = client.create_issue_from_template(
        template_name="bug",
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
if pytest_session.failures:
    for test_name, error in pytest_session.failures.items():
        create_bug_from_test_failure(test_name, str(error))
```

### חיפוש וניתוח טיקטים

```python
from external.jira import JiraClient
from collections import defaultdict

client = JiraClient()

# חיפוש כל הבאגים הפתוחים
bugs = client.search_issues(
    "project = PZ AND type = Bug AND status != Done"
)

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

## 🔐 טיפים ובטיחות

### אבטחה

1. **אל תשמור API Token בקוד** - השתמש בקובץ קונפיגורציה או משתני סביבה
2. **השתמש ב-SSL** - ודא ש-`verify_ssl: true` מוגדר (אלא אם יש תעודת SSL עצמית)
3. **הגבל הרשאות** - השתמש ב-API Token עם הרשאות מינימליות נדרשות

### שימוש בקובץ קונפיגורציה

```python
# שימוש בקובץ קונפיגורציה מותאם
client = JiraClient(config_path="/path/to/custom/jira_config.yaml")
```

### טיפול בשגיאות

```python
from external.jira import JiraClient
from jira.exceptions import JIRAError

client = JiraClient()

try:
    issue = client.create_issue(
        summary="Test Issue",
        issue_type="Task"
    )
    print(f"נוצר: {issue['key']}")
except JIRAError as e:
    print(f"שגיאת Jira: {e}")
except ValueError as e:
    print(f"שגיאת ערך: {e}")
except Exception as e:
    print(f"שגיאה כללית: {e}")
```

### סגירת חיבור

```python
# סגירת חיבור (לא חובה, אבל מומלץ)
client = JiraClient()
# ... עבודה עם Jira ...
client.close()
```

---

## 📚 מסמכים נוספים

- **קובץ קונפיגורציה:** `config/jira_config.yaml`
- **JiraClient:** `external/jira/jira_client.py`
- **Scripts:** `scripts/jira/`

---

## ✅ סיכום

המערכת מספקת אינטגרציה מלאה עם Jira API עבור:

- ✅ יצירת טיקטים (Tasks, Bugs, Stories, Epics, Sub-tasks)
- ✅ חיפוש וקריאת טיקטים (JQL, Filters מוגדרים מראש)
- ✅ עדכון טיקטים (שדות, סטטוס, הערות)
- ✅ Scripts שורת פקודה לעבודה מהירה
- ✅ תבניות מוכנות ליצירת טיקטים
- ✅ טיפול בשגיאות ולוגים

**הפתרון נבדק ומוכן לשימוש Production!**

---

**תאריך עדכון:** 2025-11-04  
**גרסה:** 1.0.0

