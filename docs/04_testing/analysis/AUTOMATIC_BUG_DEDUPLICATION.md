# 🐛 מנגנון אוטומטי למניעת כפילות באגים ב-Jira

**תאריך:** 2025-11-08  
**גרסה:** 1.0.0

---

## 📋 סקירה כללית

מנגנון אוטומטי שמונע יצירת באגים כפולים ב-Jira על ידי:
1. **חיפוש באגים קיימים** - לפני יצירת באג חדש, מחפש באגים דומים
2. **השוואת דמיון** - משווה בין הבעיה החדשה לבאגים קיימים
3. **מניעת כפילות** - יוצר באג חדש רק אם לא נמצא באג דומה

---

## 🏗️ ארכיטקטורה

### רכיבים עיקריים:

1. **`BugDeduplicationService`** - שירות לחיפוש והשוואת באגים
2. **`BugCreatorService`** - שירות ליצירת באגים עם בדיקת כפילות
3. **`JiraClient`** - לקוח Jira API (קיים)

---

## 📦 שימוש

### דוגמה בסיסית:

```python
from external.jira.bug_creator import BugCreatorService

# Initialize service
service = BugCreatorService()

# Create bug from test failure
bug = service.create_bug_from_test_failure(
    test_name="test_mongodb_connection_failure",
    error_message="Connection failed: timeout",
    summary="MongoDB connection timeout",
    description="Test failed due to MongoDB connection timeout",
    priority="High",
    keywords=["mongodb", "connection", "timeout"]
)

if bug:
    print(f"Created bug: {bug['key']}")
else:
    print("Similar bug already exists - skipping creation")
```

---

## 🔍 איך זה עובד?

### 1. חיפוש באגים קיימים

השירות מחפש באגים קיימים באמצעות מספר שאילתות JQL:

- **חיפוש לפי Summary** - מחפש מילות מפתח מתוך ה-summary
- **חיפוש לפי Keywords** - מחפש לפי keywords שסופקו
- **חיפוש לפי Error Message** - מחפש מילות מפתח מתוך ה-error message
- **חיפוש לפי Test Name** - מחפש לפי שם הטסט
- **חיפוש באגים אחרונים** - מחפש באגים שנוצרו ב-30 יום האחרונים עם "Found by = QA Cycle"

### 2. חישוב דמיון

השירות מחשב ציון דמיון (0.0-1.0) בין הבעיה החדשה לבאגים קיימים:

- **Summary Similarity** (40% משקל) - השוואת summaries
- **Description Similarity** (30% משקל) - השוואת descriptions
- **Keywords Match** (20% משקל) - התאמת keywords
- **Error Message Match** (10% משקל) - התאמת error messages

### 3. החלטה

אם ציון הדמיון גבוה מ-**0.7** (ברירת מחדל), הבאג נחשב דומה והשירות מדלג על יצירת באג חדש.

---

## ⚙️ הגדרות

### BugDeduplicationService

```python
service = BugDeduplicationService(
    jira_client=None,  # JiraClient instance (creates new if not provided)
    project_key=None,  # Project key (defaults to client config)
    similarity_threshold=0.7,  # Minimum similarity score (0.0-1.0)
    cache_duration_hours=24  # How long to cache existing bugs
)
```

### BugCreatorService

```python
service = BugCreatorService(
    jira_client=None,  # JiraClient instance
    deduplication_service=None,  # BugDeduplicationService instance
    project_key=None,  # Project key
    default_reporter=None  # Default reporter email/username
)
```

---

## 📝 פרמטרים

### create_bug_from_test_failure()

```python
bug = service.create_bug_from_test_failure(
    test_name="test_name",  # Required: Name of the test
    error_message="error",  # Required: Error message
    summary="Summary",  # Required: Bug summary
    description="Description",  # Required: Bug description
    priority="High",  # Optional: Priority (default: "High")
    labels=["label1"],  # Optional: Additional labels
    keywords=["keyword1"],  # Optional: Keywords for deduplication
    steps_to_reproduce=["step1"],  # Optional: Steps to reproduce
    expected_result="Expected",  # Optional: Expected result
    actual_result="Actual",  # Optional: Actual result
    environment="staging",  # Optional: Environment
    skip_duplicate_check=False  # Optional: Skip duplicate check (not recommended)
)
```

---

## 🎯 דוגמאות שימוש

### דוגמה 1: יצירת באג מכשלון טסט

```python
from external.jira.bug_creator import BugCreatorService

service = BugCreatorService()

bug = service.create_bug_from_test_failure(
    test_name="test_mongodb_indexes_missing",
    error_message="Critical indexes are MISSING: ['start_time', 'end_time', 'uuid']",
    summary="MongoDB indexes missing - slow query performance",
    description="MongoDB recording collection is missing critical indexes, causing slow query performance.",
    priority="High",
    keywords=["mongodb", "index", "performance", "query"],
    steps_to_reproduce=[
        "Run test_mongodb_indexes_exist_and_optimal",
        "Check indexes on recording collection",
        "Verify required indexes exist"
    ],
    expected_result="All required indexes should exist",
    actual_result="Indexes are missing: start_time, end_time, uuid, deleted"
)

if bug:
    print(f"Created: {bug['key']}")
else:
    print("Similar bug exists")
```

### דוגמה 2: בדיקת כפילות ידנית

```python
from external.jira.bug_deduplication import BugDeduplicationService

service = BugDeduplicationService()

existing_bug = service.find_similar_bug(
    summary="MongoDB connection failure",
    description="Pod restarts due to MongoDB connection error",
    keywords=["mongodb", "connection", "restart"],
    error_message="pymongo.errors.ServerSelectionTimeoutError",
    test_name="test_mongodb_connection"
)

if existing_bug:
    print(f"Found similar bug: {existing_bug['key']}")
    print(f"  Summary: {existing_bug['summary']}")
    print(f"  Status: {existing_bug['status']}")
    print(f"  URL: {existing_bug['url']}")
else:
    print("No similar bugs found")
```

---

## 🔧 Cache

השירות משתמש ב-cache כדי לשפר ביצועים:

- **Cache Duration**: 24 שעות (ברירת מחדל)
- **Cache Key**: JQL query + max_results
- **Clear Cache**: `service.clear_cache()`

---

## 📊 Metrics

השירות מדווח על:

- מספר שאילתות JQL שבוצעו
- מספר באגים שנמצאו
- ציון הדמיון הגבוה ביותר
- האם באג חדש נוצר או נדלג

---

## ⚠️ הערות חשובות

1. **Similarity Threshold**: ברירת מחדל 0.7 - ניתן לשנות לפי הצורך
2. **Cache**: Cache נשמר למשך 24 שעות - ניתן לנקות ידנית
3. **Performance**: חיפוש יכול לקחת זמן - השירות משתמש ב-cache כדי לשפר ביצועים
4. **JQL Queries**: השירות מבצע מספר שאילתות JQL - ייתכן שייקח זמן

---

## 🚀 שילוב עם Automation

### שילוב עם pytest:

```python
import pytest
from external.jira.bug_creator import BugCreatorService

@pytest.fixture(scope="session")
def bug_creator():
    """Fixture for bug creator service."""
    service = BugCreatorService()
    yield service
    service.close()

def test_example(bug_creator):
    """Example test that creates bug on failure."""
    try:
        # Test code
        assert False, "Test failed"
    except AssertionError as e:
        # Create bug from failure
        bug = bug_creator.create_bug_from_test_failure(
            test_name="test_example",
            error_message=str(e),
            summary="Test example failed",
            description="Test failed with assertion error",
            priority="Medium"
        )
        raise
```

---

## 📚 קבצים

- `external/jira/bug_deduplication.py` - שירות למניעת כפילות
- `external/jira/bug_creator.py` - שירות ליצירת באגים
- `scripts/jira/create_bug_with_deduplication.py` - דוגמת שימוש

---

## 🔄 עדכונים עתידיים

- [ ] תמיכה ב-custom fields נוספים
- [ ] תמיכה ב-attachments
- [ ] תמיכה ב-linking bugs
- [ ] תמיכה ב-comments אוטומטיים
- [ ] תמיכה ב-workflow transitions

---

**עודכן לאחרונה:** 2025-11-08  
**גרסה:** 1.0.0

