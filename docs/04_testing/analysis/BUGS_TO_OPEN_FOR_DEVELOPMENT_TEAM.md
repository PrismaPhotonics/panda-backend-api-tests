# 🐛 באגים לפתיחה לצוות פיתוח

**תאריך:** 2025-11-08 13:30  
**סטטוס:** 📝 **מוכן לפתיחה**

---

## 📋 סיכום

במהלך הבדיקות היום זיהינו מספר בעיות שדורשות פתיחה של באגים לצוות פיתוח:

1. ✅ **בעיית חיבור ל-MongoDB בזמן initialization** - גורם ל-restarts
2. ✅ **בעיית error handling ב-/configure endpoint** - מחזיר 503 ללא הודעה ברורה
3. ✅ **חוסר validation של metadata לפני configure** - לא בודק אם המערכת מוכנה
4. ⚠️ **בעיית retry logic בטסטים** - זה באג שלנו, לא של השרת

---

## 🐛 באג #1: MongoDB Connection Failure גורם ל-Pod Restarts

### תיאור הבעיה:

ה-pod של Focus Server נכשל ב-startup בגלל בעיית חיבור ל-MongoDB, מה שגורם ל-restarts חוזרים.

### שגיאה:

```
pymongo.errors.ServerSelectionTimeoutError: mongodb:27017: [Errno -3] Temporary failure in name resolution
```

### מה קורה:

1. ה-pod מתחיל לרוץ
2. `FocusManager.__init__()` נקרא
3. הוא ניסה ליצור `RecordingMongoMapper(self.storage_path)`
4. זה ניסה להתחבר ל-MongoDB דרך `mongodb:27017`
5. ה-pod לא יכול לפתור את השם `mongodb` ל-IP address
6. ה-pod נכשל ב-startup ונכנס ל-CrashLoopBackOff
7. Kubernetes restart את ה-pod עד שהחיבור ל-MongoDB חזר לעבוד

### ראיות:

- **4 restarts ב-28 שעות** ב-pod `panda-panda-focus-server-78dbcfd9d9-kjj77`
- הלוגים מראים את השגיאה בבירור
- ה-pod רץ כבר 46 שעות ללא restarts (אחרי שהחיבור חזר לעבוד)

### השפעה:

- Pod restarts חוזרים עד שהחיבור ל-MongoDB עובד
- זמן downtime של השירות
- עומס מיותר על Kubernetes

### פתרונות מומלצים:

1. **הוסף Init Container** שימתין ל-MongoDB:
   ```yaml
   initContainers:
   - name: wait-for-mongodb
     image: busybox
     command: ['sh', '-c', 'until nslookup mongodb.panda; do echo waiting for mongodb; sleep 2; done']
   ```

2. **הוסף Retry Logic בקוד**:
   ```python
   # pz/microservices/focus_server/focus_manager.py
   import time
   from pymongo.errors import ServerSelectionTimeoutError
   
   max_retries = 5
   retry_delay = 5
   for attempt in range(max_retries):
       try:
           self.mongo_mapper = RecordingMongoMapper(self.storage_path)
           break
       except ServerSelectionTimeoutError as e:
           if attempt < max_retries - 1:
               logger.warning(f"MongoDB connection failed (attempt {attempt + 1}/{max_retries}): {e}")
               time.sleep(retry_delay)
           else:
               logger.error(f"MongoDB connection failed after {max_retries} attempts: {e}")
               raise
   ```

3. **הוסף Readiness Probe** - ה-pod לא יקבל traffic עד שהוא מוכן

### עדיפות:

**גבוהה** - זה גורם ל-restarts חוזרים ו-downtime של השירות

### קטגוריה:

**Infrastructure / Reliability**

### קישורים רלוונטיים:

- מסמך ניתוח: `docs/04_testing/analysis/MONGODB_CONNECTION_RESTARTS_ANALYSIS.md`
- קוד רלוונטי: `pz/microservices/focus_server/focus_manager.py:61`

---

## 🐛 באג #2: Error Handling לא ברור ב-/configure Endpoint

### תיאור הבעיה:

כשהמערכת במצב "waiting for fiber", ה-`/configure` endpoint מחזיר `503 Service Unavailable` ללא הודעה ברורה למשתמש.

### מה קורה:

1. המשתמש שולח בקשה ל-`POST /configure`
2. השרת בודק את ה-metadata
3. אם `prr` חסר או 0, השרת מחזיר `503 Service Unavailable`
4. אבל ההודעה לא ברורה - המשתמש לא יודע למה זה נכשל

### שגיאה נוכחית:

```
ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr
INFO: "POST /configure HTTP/1.1" 503 Service Unavailable
```

### מה צריך להיות:

```json
{
  "error": "Cannot configure job",
  "reason": "Missing required fiber metadata fields: prr",
  "status": "waiting_for_fiber",
  "message": "System is waiting for fiber connection. Please ensure fiber is connected and metadata is available.",
  "details": {
    "prr": 0.0,
    "sw_version": "waiting for fiber",
    "fiber_description": "waiting for fiber"
  }
}
```

### השפעה:

- משתמשים לא יודעים למה הבקשה נכשלה
- קשה לזהות את הבעיה
- קשה לטפל בבעיה

### פתרון מומלץ:

```python
# pz/microservices/focus_server/focus_server.py
@app.post('/configure')
def configure(configuration: Dict):
    # Check metadata before attempting to configure
    if focus_manager.fiber_metadata.prr <= 0 or focus_manager.fiber_metadata.sw_version == "waiting for fiber":
        return ORJSONResponse(
            content={
                "error": "Cannot configure job",
                "reason": "Missing required fiber metadata fields: prr",
                "status": "waiting_for_fiber",
                "message": "System is waiting for fiber connection. Please ensure fiber is connected and metadata is available.",
                "details": {
                    "prr": focus_manager.fiber_metadata.prr,
                    "sw_version": focus_manager.fiber_metadata.sw_version,
                    "fiber_description": focus_manager.fiber_metadata.fiber_description
                }
            },
            status_code=400  # Bad Request instead of 503
        )
```

### עדיפות:

**בינונית** - זה לא גורם ל-downtime, אבל משפיע על ה-UX

### קטגוריה:

**API / Error Handling**

### קישורים רלוונטיים:

- מסמך ניתוח: `docs/04_testing/analysis/PRR_ERROR_CURRENT_STATUS_2025-11-08.md`
- קוד רלוונטי: `pz/microservices/focus_server/focus_server.py`

---

## 🐛 באג #3: חוסר Validation של Metadata לפני Configure

### תיאור הבעיה:

ה-`/configure` endpoint לא בודק אם המערכת מוכנה לפני שהוא מנסה להגדיר job. זה גורם לשגיאות מיותרות.

### מה קורה:

1. המשתמש שולח בקשה ל-`POST /configure`
2. השרת מנסה להגדיר job מיד
3. רק אחר כך הוא מגלה שה-metadata לא זמין
4. השרת מחזיר שגיאה

### מה צריך להיות:

1. המשתמש שולח בקשה ל-`POST /configure`
2. השרת בודק אם ה-metadata זמין לפני שהוא מנסה להגדיר job
3. אם ה-metadata לא זמין, השרת מחזיר שגיאה ברורה מיד

### השפעה:

- שגיאות מיותרות
- עומס מיותר על השרת
- זמן תגובה איטי יותר

### פתרון מומלץ:

```python
# pz/microservices/focus_server/focus_server.py
@app.post('/configure')
def configure(configuration: Dict):
    # Validate metadata before attempting to configure
    if not hasattr(focus_manager, 'fiber_metadata') or focus_manager.fiber_metadata is None:
        return ORJSONResponse(
            content={
                "error": "Cannot configure job",
                "reason": "Fiber metadata not available",
                "status": "metadata_unavailable",
                "message": "Fiber metadata is not available. Please wait for the system to initialize."
            },
            status_code=503
        )
    
    if focus_manager.fiber_metadata.prr <= 0:
        return ORJSONResponse(
            content={
                "error": "Cannot configure job",
                "reason": "Missing required fiber metadata fields: prr",
                "status": "waiting_for_fiber",
                "message": "System is waiting for fiber connection. Please ensure fiber is connected and metadata is available."
            },
            status_code=400
        )
    
    # Continue with configuration...
```

### עדיפות:

**בינונית** - זה לא גורם ל-downtime, אבל משפר את ה-UX

### קטגוריה:

**API / Validation**

### קישורים רלוונטיים:

- מסמך ניתוח: `docs/04_testing/analysis/PRR_ERROR_CURRENT_STATUS_2025-11-08.md`
- קוד רלוונטי: `pz/microservices/focus_server/focus_server.py`

---

## ⚠️ בעיה #4: Retry Logic בטסטים (באג שלנו, לא של השרת)

### תיאור הבעיה:

הטסטים ממשיכים לנסות להגדיר jobs גם כשהמערכת במצב "waiting for fiber", מה שיוצר עומס מיותר על השרת.

### מה קורה:

1. הטסטים מנסים להגדיר job
2. השרת מחזיר `503 Service Unavailable`
3. ה-retry logic מנסה שוב
4. זה חוזר על עצמו כל 2-3 שניות

### השפעה:

- עומס מיותר על השרת
- לוגים מיותרים
- זמן תגובה איטי יותר

### פתרון (בצד שלנו):

```python
# tests/conftest.py
@pytest.fixture(scope="session", autouse=True)
def check_metadata_ready(focus_server_api):
    """Skip all configure tests if system is waiting for fiber."""
    import pytest
    
    try:
        metadata = focus_server_api.get_live_metadata_flat()
        if metadata.prr <= 0 or metadata.sw_version == "waiting for fiber":
            pytest.skip("System is waiting for fiber - stopping all configure tests")
    except Exception as e:
        pytest.skip(f"Cannot check metadata - stopping all configure tests: {e}")
```

### עדיפות:

**נמוכה** - זה באג שלנו, לא של השרת

### קטגוריה:

**Test Infrastructure**

---

## 📊 סיכום

### באגים לפתיחה לצוות פיתוח:

| # | תיאור | עדיפות | קטגוריה | קישור למסמך |
|---|-------|--------|---------|-------------|
| 1 | MongoDB Connection Failure גורם ל-Pod Restarts | גבוהה | Infrastructure / Reliability | `MONGODB_CONNECTION_RESTARTS_ANALYSIS.md` |
| 2 | Error Handling לא ברור ב-/configure Endpoint | בינונית | API / Error Handling | `PRR_ERROR_CURRENT_STATUS_2025-11-08.md` |
| 3 | חוסר Validation של Metadata לפני Configure | בינונית | API / Validation | `PRR_ERROR_CURRENT_STATUS_2025-11-08.md` |

### בעיות שצריך לטפל בהן בעצמנו:

| # | תיאור | עדיפות | קטגוריה |
|---|-------|--------|---------|
| 4 | Retry Logic בטסטים | נמוכה | Test Infrastructure |

---

## ✅ Checklist לפתיחת באגים

### לפני פתיחת באג:

- [x] זיהינו את הבעיה בבירור ✅
- [x] יש לנו ראיות (לוגים, שגיאות) ✅
- [x] יש לנו מסמך ניתוח מפורט ✅
- [x] יש לנו פתרונות מומלצים ✅
- [ ] פתחנו באג ב-Jira
- [ ] צירפנו את המסמכים
- [ ] צירפנו את הלוגים
- [ ] צירפנו את הקוד הרלוונטי

---

## 📝 תבנית לפתיחת באג ב-Jira

### באג #1: MongoDB Connection Failure

**Title:** Focus Server pod restarts due to MongoDB connection failure during initialization

**Description:**
Focus Server pod fails during startup due to MongoDB connection failure, causing repeated restarts until connection is restored.

**Steps to Reproduce:**
1. Deploy Focus Server pod
2. MongoDB service is not ready or DNS is not available
3. Pod tries to initialize FocusManager
4. FocusManager tries to connect to MongoDB
5. Connection fails with DNS resolution error
6. Pod crashes and restarts

**Expected Behavior:**
Pod should wait for MongoDB to be available or retry connection with backoff.

**Actual Behavior:**
Pod crashes and restarts repeatedly until MongoDB connection is restored.

**Error Message:**
```
pymongo.errors.ServerSelectionTimeoutError: mongodb:27017: [Errno -3] Temporary failure in name resolution
```

**Impact:**
- Service downtime
- Repeated pod restarts
- Increased load on Kubernetes

**Priority:** High

**Category:** Infrastructure / Reliability

**Attachments:**
- `docs/04_testing/analysis/MONGODB_CONNECTION_RESTARTS_ANALYSIS.md`
- Logs from previous pod instance

**Suggested Solutions:**
1. Add init container to wait for MongoDB
2. Add retry logic in code
3. Add readiness probe

---

### באג #2: Error Handling לא ברור

**Title:** /configure endpoint returns unclear error when system is waiting for fiber

**Description:**
When system is in "waiting for fiber" state, /configure endpoint returns 503 Service Unavailable without clear error message.

**Steps to Reproduce:**
1. System is in "waiting for fiber" state (prr=0.0)
2. Send POST request to /configure
3. Receive 503 Service Unavailable
4. Error message is not clear

**Expected Behavior:**
Return 400 Bad Request with clear error message explaining the issue.

**Actual Behavior:**
Returns 503 Service Unavailable without clear error message.

**Error Message:**
```
ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr
INFO: "POST /configure HTTP/1.1" 503 Service Unavailable
```

**Impact:**
- Poor user experience
- Difficult to diagnose issues
- Difficult to handle errors programmatically

**Priority:** Medium

**Category:** API / Error Handling

**Attachments:**
- `docs/04_testing/analysis/PRR_ERROR_CURRENT_STATUS_2025-11-08.md`
- Example error response

**Suggested Solutions:**
Return structured error response with status code 400 and clear message.

---

### באג #3: חוסר Validation

**Title:** /configure endpoint doesn't validate metadata availability before attempting configuration

**Description:**
/configure endpoint doesn't check if metadata is available before attempting to configure job, causing unnecessary errors.

**Steps to Reproduce:**
1. System is in "waiting for fiber" state
2. Send POST request to /configure
3. Server attempts to configure job
4. Only then discovers metadata is not available
5. Returns error

**Expected Behavior:**
Check metadata availability before attempting configuration and return clear error immediately.

**Actual Behavior:**
Attempts configuration first, then returns error after discovering metadata is not available.

**Impact:**
- Unnecessary errors
- Increased server load
- Slower response time

**Priority:** Medium

**Category:** API / Validation

**Attachments:**
- `docs/04_testing/analysis/PRR_ERROR_CURRENT_STATUS_2025-11-08.md`

**Suggested Solutions:**
Add metadata validation before attempting configuration.

---

**עודכן לאחרונה:** 2025-11-08 16:01  
**סטטוס:** ✅ **כל 3 הטיקטים נוצרו בהצלחה ב-Jira!**

## ✅ טיקטים שנוצרו:

| # | Ticket Key | Summary | Priority | URL |
|---|------------|---------|----------|-----|
| 1 | **PZ-14712** | Focus Server pod restarts due to MongoDB connection failure during initialization | High | https://prismaphotonics.atlassian.net/browse/PZ-14712 |
| 2 | **PZ-14713** | /configure endpoint returns unclear error when system is waiting for fiber | Medium | https://prismaphotonics.atlassian.net/browse/PZ-14713 |
| 3 | **PZ-14714** | /configure endpoint doesn't validate metadata availability before attempting configuration | Medium | https://prismaphotonics.atlassian.net/browse/PZ-14714 |

**ראה מסמך מפורט:** `docs/04_testing/analysis/BUGS_CREATED_IN_JIRA_2025-11-08.md`

