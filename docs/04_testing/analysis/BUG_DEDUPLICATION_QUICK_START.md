# 🚀 Quick Start: Bug Deduplication

**תאריך:** 2025-11-08

---

## 📋 מה זה?

מנגנון אוטומטי שמונע יצירת באגים כפולים ב-Jira על ידי חיפוש באגים דומים לפני יצירת באג חדש.

---

## 🎯 שימוש מהיר

### 1. יצירת באג מכשלון טסט

```python
from external.jira.bug_creator import BugCreatorService

# Initialize service
service = BugCreatorService()

# Create bug from test failure
bug = service.create_bug_from_test_failure(
    test_name="test_mongodb_connection",
    error_message="Connection failed: timeout",
    summary="MongoDB connection timeout",
    description="Test failed due to MongoDB connection timeout",
    priority="High"
)

if bug:
    print(f"✅ Created: {bug['key']}")
else:
    print("⚠️  Similar bug already exists")
```

### 2. בדיקת כפילות ידנית

```python
from external.jira.bug_deduplication import BugDeduplicationService

service = BugDeduplicationService()

existing_bug = service.find_similar_bug(
    summary="MongoDB connection failure",
    description="Pod restarts due to MongoDB connection error",
    keywords=["mongodb", "connection", "restart"]
)

if existing_bug:
    print(f"Found: {existing_bug['key']} - {existing_bug['summary']}")
```

---

## 🔧 הגדרות

### שינוי Similarity Threshold

```python
service = BugDeduplicationService(
    similarity_threshold=0.8  # Default: 0.7
)
```

### Cache Duration

```python
service = BugDeduplicationService(
    cache_duration_hours=12  # Default: 24
)
```

---

## 📝 דוגמה מלאה

```python
from external.jira.bug_creator import BugCreatorService

service = BugCreatorService()

bug = service.create_bug_from_test_failure(
    test_name="test_mongodb_indexes_missing",
    error_message="Critical indexes are MISSING: ['start_time', 'end_time', 'uuid']",
    summary="MongoDB indexes missing - slow query performance",
    description="MongoDB recording collection is missing critical indexes.",
    priority="High",
    keywords=["mongodb", "index", "performance"],
    steps_to_reproduce=[
        "Run test_mongodb_indexes_exist_and_optimal",
        "Check indexes on recording collection"
    ],
    expected_result="All required indexes should exist",
    actual_result="Indexes are missing: start_time, end_time, uuid"
)

if bug:
    print(f"Created: {bug['key']} - {bug['url']}")
else:
    print("Similar bug already exists - check Jira")
```

---

## ⚠️ הערות

1. **Similarity Threshold**: ברירת מחדל 0.7 - ניתן לשנות
2. **Cache**: Cache נשמר למשך 24 שעות
3. **Performance**: חיפוש יכול לקחת זמן - השירות משתמש ב-cache

---

**עודכן:** 2025-11-08

