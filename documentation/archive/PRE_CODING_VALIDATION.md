# ✅ בדיקה משולשת לפני כתיבת קוד
**תאריך:** 2025-10-15  
**משימה:** MongoDB Data Quality Tests (PZ-13598)

---

## 🔍 בדיקה 1/3: אימות הבנה

### ✅ מה אני יוצר?
- **קובץ חדש:** `tests/integration/infrastructure/test_mongodb_data_quality.py`
- **מטרה:** בדיקת data quality, schema, indexes של MongoDB
- **Base class:** `InfrastructureTest` (מ-`src.core.base_test`)
- **Fixtures:** `mongodb_manager` (session scope)

### ✅ מידע נדרש:

#### MongoDB Configuration:
- **Database (staging):** `prisma`
- **Database (local):** `focus_db`
- **Host:** `10.10.10.103` (staging) או `localhost` (local)
- **Port:** 27017
- **Username:** `prisma`
- **Password:** `prisma`

#### Collections צפויות:
1. **base_paths** - paths למידע
2. **node2** - מידע רמה 2
3. **node4** - recordings מידע (הכי חשוב!)

#### node4 Schema (נדרש):
```python
{
    "uuid": str,           # Required - unique identifier
    "start_time": int/datetime,  # Required - recording start
    "end_time": int/datetime,    # Required - recording end
    "deleted": bool        # Required - soft delete flag
    # + additional fields...
}
```

#### Indexes (נדרש):
- `node4.start_time` - for time range queries
- `node4.end_time` - for time range queries
- `node4.uuid` - for unique lookups
- `node4.deleted` - for filtering active recordings
- Compound indexes? (need to check)

---

## 🔍 בדיקה 2/3: אימות דפוסים קיימים

### ✅ דפוס 1: Class Structure
```python
class TestMongoDBDataQuality(InfrastructureTest):
    """
    MongoDB Data Quality Tests.
    
    Validates MongoDB schema, indexes, and data integrity.
    
    Related Jira: PZ-13598
    """
```
- ✅ רשום מ-`InfrastructureTest`
- ✅ Docstring מפורט
- ✅ קישור ל-Jira

### ✅ דפוס 2: Fixture Setup
```python
@pytest.fixture(scope="class", autouse=True)
def setup_mongodb(self, request, mongodb_manager):
    """
    Set up MongoDB connection for the test class.
    
    Skips all tests if MongoDB is not reachable.
    """
    # Check MongoDB connectivity
    if not mongodb_manager.connect():
        pytest.skip("MongoDB is not reachable")
    
    request.cls.mongodb_manager = mongodb_manager
    self.logger.info("MongoDB manager initialized")
    
    yield
    
    # Cleanup
    mongodb_manager.disconnect()
```
- ✅ scope="class" לshared setup
- ✅ autouse=True לautomatic execution
- ✅ Skip if MongoDB not available
- ✅ Cleanup in yield

### ✅ דפוס 3: Test Method
```python
@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.mongodb
@pytest.mark.data_quality
def test_required_collections_exist(self):
    """
    Verify that all required MongoDB collections exist.
    
    Test Flow:
    1. Connect to MongoDB
    2. Get database
    3. List all collections
    4. Verify required collections are present
    
    Assertions:
    - base_paths collection exists
    - node2 collection exists
    - node4 collection exists
    
    Related: PZ-13598
    """
    self.logger.info("=" * 80)
    self.logger.info("TEST: Required Collections Exist")
    self.logger.info("=" * 80)
    
    # Step 1: ...
```
- ✅ Multiple pytest markers
- ✅ Detailed docstring
- ✅ Test Flow documented
- ✅ Assertions listed
- ✅ Logging with separators

### ✅ דפוס 4: Imports
```python
"""
MongoDB Data Quality Tests
==========================

Integration tests for MongoDB data quality, schema, and indexes.
Tests PZ-13598: Data Quality – Mongo collections and schema
"""

import pytest
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.core.base_test import InfrastructureTest
from src.core.exceptions import DatabaseError, InfrastructureError
```
- ✅ Module docstring
- ✅ Standard library imports first
- ✅ Third party imports (pytest)
- ✅ Local imports last
- ✅ Type hints

---

## 🔍 בדיקה 3/3: אימות שהקוד ירוץ

### ✅ MongoDB Access Pattern:
```python
# Access database
db = self.mongodb_manager.client[self.get_config("mongodb.database")]

# List collections
collections = db.list_collection_names()

# Access collection
node4 = db["node4"]

# Query documents
documents = node4.find().limit(10)

# Check indexes
indexes = node4.list_indexes()
```

### ✅ Error Handling:
```python
try:
    # MongoDB operations
    ...
except pymongo.errors.ConnectionFailure as e:
    self.logger.error(f"MongoDB connection failed: {e}")
    pytest.fail(f"MongoDB connection failed: {e}")
except pymongo.errors.OperationFailure as e:
    self.logger.error(f"MongoDB operation failed: {e}")
    pytest.fail(f"Operation failed: {e}")
except Exception as e:
    self.logger.error(f"Unexpected error: {e}")
    raise
```

### ✅ Logging Pattern:
```python
self.logger.info("=" * 80)
self.logger.info(f"TEST: {test_name}")
self.logger.info("=" * 80)

self.log_test_step("Step description")
self.logger.debug(f"Details: {details}")
self.logger.info(f"✅ Validation passed: {message}")
self.logger.error(f"❌ Validation failed: {error}")
```

---

## ✅ סיכום בדיקה משולשת:

| בדיקה | סטטוס | הערות |
|-------|-------|-------|
| 1. הבנת דרישות | ✅ | מבין את MongoDB structure, collections, schema |
| 2. התאמה לדפוסים | ✅ | כל הדפוסים הקיימים מזוהים ומתועדים |
| 3. יכולת הרצה | ✅ | Access patterns, error handling, logging - כולם תקינים |

**האם אני מוכן לכתוב קוד?** ✅ **כן!**

---

**נוצר על ידי:** QA Automation Architect  
**תאריך:** 2025-10-15  
**סטטוס:** ✅ Ready to code

