# 🎫 טיקטי Jira מוכנים ליצירה

**תאריך:** 2025-11-08  
**פרויקט:** PZ  
**Board:** https://prismaphotonics.atlassian.net/jira/software/c/projects/PZ/boards/21

---

## 📋 הוראות יצירה

1. היכנס ל-Jira: https://prismaphotonics.atlassian.net/jira/software/c/projects/PZ/boards/21
2. לחץ על "Create" (או הקש `C`)
3. העתק את התוכן של כל טיקט למטה
4. מלא את השדות לפי הפורמט

---

## 🐛 טיקט #1: MongoDB Connection Failure גורם ל-Pod Restarts

### שדות בסיסיים:

**Issue Type:** Bug  
**Summary:** Focus Server pod restarts due to MongoDB connection failure during initialization  
**Priority:** High  
**Component:** Focus Server / Infrastructure  
**Labels:** `infrastructure`, `mongodb`, `kubernetes`, `reliability`

### Description:

```
Focus Server pod fails during startup due to MongoDB connection failure, causing repeated restarts until connection is restored.

**Environment:**
- Kubernetes namespace: panda
- Pod: panda-panda-focus-server-78dbcfd9d9-kjj77
- MongoDB service: mongodb.panda:27017

**Steps to Reproduce:**
1. Deploy Focus Server pod
2. MongoDB service is not ready or DNS is not available
3. Pod tries to initialize FocusManager
4. FocusManager tries to connect to MongoDB (line 61 in focus_manager.py)
5. Connection fails with DNS resolution error
6. Pod crashes and restarts

**Expected Behavior:**
Pod should wait for MongoDB to be available or retry connection with backoff instead of crashing.

**Actual Behavior:**
Pod crashes and restarts repeatedly until MongoDB connection is restored.

**Error Message:**
```
pymongo.errors.ServerSelectionTimeoutError: mongodb:27017: [Errno -3] Temporary failure in name resolution
(configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), 
Timeout: 30s, Topology Description: <TopologyDescription id: 690dacafa411911c09db4a57, 
topology_type: Unknown, servers: [<ServerDescription ('mongodb', 27017) server_type: Unknown, 
rtt: None, error=AutoReconnect('mongodb:27017: [Errno -3] Temporary failure in name resolution 
(configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
```

**Impact:**
- Service downtime during pod restarts
- Repeated pod restarts (observed: 4 restarts in 28 hours)
- Increased load on Kubernetes
- Poor reliability

**Evidence:**
- Pod logs show the error clearly
- Pod status: 4 restarts in 28 hours
- Pod is now running for 46 hours (after connection was restored)

**Root Cause:**
FocusManager.__init__() tries to create RecordingMongoMapper immediately without checking if MongoDB is available. If DNS resolution fails or MongoDB service is not ready, the pod crashes.

**Suggested Solutions:**

1. **Add Init Container** (Recommended):
   ```yaml
   initContainers:
   - name: wait-for-mongodb
     image: busybox
     command: ['sh', '-c', 'until nslookup mongodb.panda; do echo waiting for mongodb; sleep 2; done']
   ```

2. **Add Retry Logic in Code**:
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

3. **Add Readiness Probe** - Pod won't receive traffic until it's ready

**Related Files:**
- `pz/microservices/focus_server/focus_manager.py:61`
- `docs/04_testing/analysis/MONGODB_CONNECTION_RESTARTS_ANALYSIS.md`

**Acceptance Criteria:**
- [ ] Pod doesn't crash when MongoDB is temporarily unavailable
- [ ] Pod waits for MongoDB or retries connection with backoff
- [ ] No repeated restarts due to MongoDB connection issues
- [ ] Readiness probe or init container implemented
```

### Additional Fields:

**Affects Version:** Current (Yoshi)  
**Fix Version:** Next Release  
**Environment:** Staging (10.10.10.100)  
**Reporter:** QA Team  
**Assignee:** (Leave empty or assign to Infrastructure/Backend team)

---

## 🐛 טיקט #2: Error Handling לא ברור ב-/configure Endpoint

### שדות בסיסיים:

**Issue Type:** Bug  
**Summary:** /configure endpoint returns unclear error when system is waiting for fiber  
**Priority:** Medium  
**Component:** Focus Server / API  
**Labels:** `api`, `error-handling`, `ux`, `configure-endpoint`

### Description:

```
When system is in "waiting for fiber" state, /configure endpoint returns 503 Service Unavailable without clear error message, making it difficult for users to understand what went wrong.

**Environment:**
- Endpoint: POST /configure
- System state: "waiting for fiber" (prr=0.0, sw_version="waiting for fiber")

**Steps to Reproduce:**
1. System is in "waiting for fiber" state (check via GET /live_metadata)
2. Send POST request to /configure endpoint
3. Receive 503 Service Unavailable response
4. Error message is not clear or user-friendly

**Expected Behavior:**
Return 400 Bad Request with structured error response explaining:
- What went wrong (missing PRR metadata)
- Why it happened (system waiting for fiber)
- What the user should do (wait for fiber connection)

**Actual Behavior:**
Returns 503 Service Unavailable with minimal error information:
```
ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr
INFO: "POST /configure HTTP/1.1" 503 Service Unavailable
```

**Current Response:**
- Status Code: 503 (Service Unavailable)
- No structured error body
- Error only in logs, not in response

**Desired Response:**
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
Status Code: 400 (Bad Request) instead of 503

**Impact:**
- Poor user experience - users don't understand what went wrong
- Difficult to diagnose issues programmatically
- Difficult to handle errors in client applications
- 503 suggests server issue, but it's actually a client/state issue

**Suggested Solution:**

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
    
    # Continue with normal configuration...
```

**Related Files:**
- `pz/microservices/focus_server/focus_server.py`
- `docs/04_testing/analysis/PRR_ERROR_CURRENT_STATUS_2025-11-08.md`

**Acceptance Criteria:**
- [ ] Returns 400 Bad Request (not 503) when metadata is missing
- [ ] Returns structured JSON error response
- [ ] Error message is clear and actionable
- [ ] Error includes relevant metadata details
- [ ] Client applications can handle the error programmatically
```

### Additional Fields:

**Affects Version:** Current (Yoshi)  
**Fix Version:** Next Release  
**Environment:** Staging (10.10.10.100)  
**Reporter:** QA Team  
**Assignee:** (Leave empty or assign to Backend team)

---

## 🐛 טיקט #3: חוסר Validation של Metadata לפני Configure

### שדות בסיסיים:

**Issue Type:** Bug  
**Summary:** /configure endpoint doesn't validate metadata availability before attempting configuration  
**Priority:** Medium  
**Component:** Focus Server / API  
**Labels:** `api`, `validation`, `metadata`, `configure-endpoint`

### Description:

```
/configure endpoint doesn't check if metadata is available before attempting to configure job, causing unnecessary errors and increased server load.

**Environment:**
- Endpoint: POST /configure
- System state: "waiting for fiber" or metadata not initialized

**Steps to Reproduce:**
1. System is in "waiting for fiber" state (prr=0.0)
2. Send POST request to /configure endpoint
3. Server attempts to configure job
4. Only then discovers metadata is not available
5. Returns error after wasting processing time

**Expected Behavior:**
Check metadata availability before attempting configuration and return clear error immediately if metadata is not available.

**Actual Behavior:**
Attempts configuration first, then returns error after discovering metadata is not available during processing.

**Impact:**
- Unnecessary errors and processing
- Increased server load
- Slower response time
- Poor user experience

**Current Flow:**
1. Request received
2. Start processing configuration
3. Try to use metadata (e.g., focus_manager.prr)
4. Discover metadata is missing/invalid
5. Return error

**Desired Flow:**
1. Request received
2. Validate metadata availability immediately
3. If metadata not available, return error immediately
4. If metadata available, continue with configuration

**Suggested Solution:**

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
            status_code=503  # Service Unavailable - system not ready
        )
    
    if focus_manager.fiber_metadata.prr <= 0:
        return ORJSONResponse(
            content={
                "error": "Cannot configure job",
                "reason": "Missing required fiber metadata fields: prr",
                "status": "waiting_for_fiber",
                "message": "System is waiting for fiber connection. Please ensure fiber is connected and metadata is available.",
                "details": {
                    "prr": focus_manager.fiber_metadata.prr,
                    "sw_version": focus_manager.fiber_metadata.sw_version
                }
            },
            status_code=400  # Bad Request - invalid state
        )
    
    # Continue with normal configuration...
    # Now we know metadata is available
```

**Benefits:**
- Faster error response (fail fast)
- Reduced server load
- Better error messages
- Clearer separation between "system not ready" (503) and "invalid request" (400)

**Related Files:**
- `pz/microservices/focus_server/focus_server.py`
- `pz/microservices/focus_server/focus_manager.py`
- `docs/04_testing/analysis/PRR_ERROR_CURRENT_STATUS_2025-11-08.md`

**Acceptance Criteria:**
- [ ] Metadata is validated before attempting configuration
- [ ] Error is returned immediately if metadata is not available
- [ ] Appropriate HTTP status codes are used (503 for system not ready, 400 for invalid state)
- [ ] Error messages are clear and actionable
- [ ] Reduced processing time for invalid requests
```

### Additional Fields:

**Affects Version:** Current (Yoshi)  
**Fix Version:** Next Release  
**Environment:** Staging (10.10.10.100)  
**Reporter:** QA Team  
**Assignee:** (Leave empty or assign to Backend team)

---

## 📋 סיכום

### טיקטים ליצירה:

| # | Summary | Priority | Component | Type |
|---|---------|----------|-----------|------|
| 1 | MongoDB Connection Failure גורם ל-Pod Restarts | High | Infrastructure | Bug |
| 2 | Error Handling לא ברור ב-/configure Endpoint | Medium | API | Bug |
| 3 | חוסר Validation של Metadata לפני Configure | Medium | API | Bug |

### קישורים רלוונטיים:

- **Board:** https://prismaphotonics.atlassian.net/jira/software/c/projects/PZ/boards/21
- **מסמך ניתוח מפורט:** `docs/04_testing/analysis/BUGS_TO_OPEN_FOR_DEVELOPMENT_TEAM.md`
- **מסמך ניתוח MongoDB:** `docs/04_testing/analysis/MONGODB_CONNECTION_RESTARTS_ANALYSIS.md`
- **מסמך ניתוח PRR:** `docs/04_testing/analysis/PRR_ERROR_CURRENT_STATUS_2025-11-08.md`

---

## ✅ Checklist לפני יצירה:

- [x] כל הפרטים מוכנים ✅
- [x] יש ראיות (לוגים, שגיאות) ✅
- [x] יש פתרונות מומלצים ✅
- [x] יש Acceptance Criteria ✅
- [ ] פתח את הטיקטים ב-Jira
- [ ] צרף את המסמכים הרלוונטיים
- [ ] עדכן את המסמכים עם מספרי הטיקטים

---

**עודכן לאחרונה:** 2025-11-08  
**סטטוס:** 📝 מוכן ליצירה ב-Jira

