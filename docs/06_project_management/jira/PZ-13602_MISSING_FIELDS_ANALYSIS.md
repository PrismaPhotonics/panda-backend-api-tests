# 🔍 ניתוח שדות חסרים - PZ-13602 (RabbitMQ Outage)

## סיכום

השוויתי את הטיקט שלך ל-**PZ-13602** מול המבנה הסטנדרטי של טיקטי טסט בפרויקט.

---

## ✅ שדות שיש לך (מצוין!)

### 1. שדות בסיסיים
- ✅ **Test ID**: PZ-13602
- ✅ **Summary**: Integration – RabbitMQ outage on Live configure
- ✅ **Priority**: Medium
- ✅ **Components/Labels**: focus-server, integration, live, rabbit, resilience
- ✅ **Description**: מפורט וברור

### 2. קישורים
- ✅ **Requirements**: FOCUS-API-CONFIGURE
- ✅ **Pre-Conditions**: PC-030 (RabbitMQ blocked)
- ✅ **Test Data**: Valid live payload

### 3. קריטריונים
- ✅ **Acceptance Criteria**: ברורים ומפורטים
- ✅ **Expected Outcomes**: 3 actions with expected results

### 4. Metadata
- ✅ **Created**: October 5, 2025
- ✅ **Updated**: 4 days ago
- ✅ **Reporter**: Roy Avrahami

---

## ❌ שדות חסרים (נדרש להוסיף!)

### 1. **Test Type** ⚠️ חסר!
**מה צריך:**
```
Test Type: Integration Test
```

**הסבר:** זה שדה קריטי ב-Xray. צריך להגדיר את סוג הבדיקה.

**איפה להוסיף:** Jira → Edit → Test Type → `Integration Test`

---

### 2. **Objective** ⚠️ חסר!
**מה צריך:**
```yaml
Objective:
  Validate that the Focus Server handles RabbitMQ outages gracefully during 
  Live mode configuration. The system must fail fast without launching 
  downstream resources (K8s Jobs, Services) and return a proper 5xx error 
  with a clear message.

Business Impact:
  - Prevents resource leaks (orphaned Jobs/Services)
  - Provides clear error messages to frontend
  - Ensures system stability during infrastructure failures
  - Enables proper monitoring and alerting
```

**הסבר:** זה נותן הקשר עסקי ו technical למה הבדיקה חשובה.

**איפה להוסיף:** Jira → Edit → Description (מעל ה-Summary הנוכחי)

---

### 3. **Test Steps (פירוט מלא)** ⚠️ חסר!
**מה צריך:**

טבלה מפורטת עם צעדים:

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | **Setup: Block RabbitMQ** | Network rule: DROP packets to 10.10.100.107:5672 | RabbitMQ unreachable from Focus Server |
| 2 | **Verify RabbitMQ status** | `telnet 10.10.100.107 5672` | Connection timeout/refused |
| 3 | **Prepare payload** | Valid live configuration (see Test Data) | Payload ready |
| 4 | **Send POST /configure** | `POST https://10.10.100.100/focus-server/configure` | Request sent |
| 5 | **Capture response** | Response status + body | Response captured |
| 6 | **Verify status code** | Response.status_code | 503 or 502 |
| 7 | **Verify error message** | Response.body | Clear message mentioning RabbitMQ |
| 8 | **Verify no job_id** | Response.body | No job_id field present |
| 9 | **Check K8s Jobs** | `kubectl get jobs -n panda` | No new grpc-job-* created |
| 10 | **Check K8s Services** | `kubectl get services -n panda` | No new grpc-service-* created |
| 11 | **Check Focus Server logs** | `kubectl logs -n panda panda-panda-focus-server-*` | "RabbitMQ unavailable" or similar |
| 12 | **Verify no crash** | Focus Server logs | No stacktrace or panic |
| 13 | **Verify no exception** | Focus Server logs | No unhandled exceptions |
| 14 | **Cleanup: Restore RabbitMQ** | Remove network block | RabbitMQ reachable |
| 15 | **Verify recovery** | POST /configure with same payload | 200 OK, job_id returned |

**איפה להוסיף:** Jira → Test Steps → Add steps

---

### 4. **Test Data (מפורט)** ⚠️ חסר!
**מה צריך:**

```json
Valid Live Payload:
{
  "displayInfo": {
    "height": 1000
  },
  "channels": {
    "min": 1,
    "max": 10
  },
  "frequencyRange": {
    "min": 0,
    "max": 500
  },
  "nfftSelection": 1024,
  "displayTimeAxisDuration": 10,
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```

**איפה להוסיף:** Jira → Test Data → הוסף JSON

---

### 5. **Automation Status** ⚠️ חסר!
**מה צריך:**
```yaml
Automation Status: TO BE AUTOMATED
Test Function: test_rabbitmq_outage_live_configure
Test File: tests/integration/resilience/test_rabbitmq_outage.py
Test Class: TestRabbitMQResilience
```

**הסבר:** חשוב לציין אם הטסט אוטומטי או לא.

**איפה להוסיף:** Jira → Automation → Status

---

### 6. **Execution Command** ⚠️ חסר!
**מה צריך:**
```bash
pytest tests/integration/resilience/test_rabbitmq_outage.py::TestRabbitMQResilience::test_rabbitmq_outage_live_configure -v
```

**איפה להוסיף:** Jira → Automation → Execution Command

---

### 7. **Post-Conditions** ⚠️ חסר!
**מה צריך:**
```yaml
Post-Conditions:
  - PC-CLEANUP-001: RabbitMQ network block removed
  - PC-CLEANUP-002: Focus Server back to normal operation
  - PC-CLEANUP-003: No orphaned K8s resources (Jobs/Services)
```

**איפה להוסיף:** Jira → Post-Conditions

---

### 8. **Assertions** ⚠️ חסר!
**מה צריך:**

```python
Critical Assertions (Test FAILS if violated):
  1. assert response.status_code in [502, 503]
  2. assert "job_id" not in response.json()
  3. assert "rabbitmq" in response.json()["error"].lower() or "upstream" in response.json()["error"].lower()
  4. assert len(new_jobs) == 0  # No K8s Jobs created
  5. assert len(new_services) == 0  # No K8s Services created
  6. assert "unavailable" in focus_server_logs or "connection refused" in focus_server_logs
  7. assert "panic" not in focus_server_logs
  8. assert "traceback" not in focus_server_logs
```

**איפה להוסיף:** Jira → Description → Assertions section

---

### 9. **Related Issues** ⚠️ חסר!
**מה צריך:**

קישור לטיקטים קשורים:
- **PZ-13603**: RabbitMQ outage on Historic configure
- **PZ-13604**: MongoDB outage resilience
- **FOCUS-RESILIENCE**: Infrastructure resilience epic

**איפה להוסיף:** Jira → Related Issues → Link

---

### 10. **Attachments** ⚠️ חסר!
**מה צריך:**

1. **Screenshot: Error Response**
   - תמונה של ה-502/503 error body

2. **Screenshot: RabbitMQ Health**
   - `kubectl get pods -n panda | grep rabbitmq`
   - או: `curl http://10.10.100.107:15672/api/overview` (blocked)

3. **Log File: Focus Server Logs**
   - קובץ טקסט עם הלוגים של Focus Server בזמן ה-failure

**איפה להוסיף:** Jira → Attachments → Upload

---

### 11. **Test Results (אחרונים)** ⚠️ חסר!
**מה צריך:**

```yaml
Last Execution:
  Date: NOT YET EXECUTED
  Status: TO BE AUTOMATED
  Environment: new_production
  Result: N/A
  
Expected After Implementation:
  Date: [TBD]
  Status: PASS
  Execution Time: ~15 seconds
  Failures: 0
  Warnings: 0
```

**איפה להוסיף:** Jira → Test Executions → Add Execution

---

### 12. **Test Configuration** ⚠️ חסר!
**מה צריך:**

```yaml
Environment: new_production
Kubernetes Namespace: panda
Focus Server: https://10.10.100.100/focus-server/
RabbitMQ Host: 10.10.100.107
RabbitMQ Port: 5672
```

**איפה להוסיף:** Jira → Environment → Configuration

---

### 13. **Architectural Context** ⚠️ חסר!
**מה צריך:**

```yaml
System Flow:
  1. Frontend → POST /configure → Focus Server
  2. Focus Server → Validates payload
  3. Focus Server → Connects to RabbitMQ (FAILS HERE)
  4. Focus Server → Should NOT create K8s Job
  5. Focus Server → Returns 5xx error to Frontend
  
Failure Point:
  - Focus Server attempts RabbitMQ connection
  - Connection timeout or refused
  - Should fail gracefully WITHOUT downstream actions
```

**איפה להוסיף:** Jira → Description → Architecture section

---

### 14. **Recovery Validation** ⚠️ חסר!
**מה צריך:**

```yaml
Recovery Test (after RabbitMQ restored):
  Action: POST /configure with same payload
  Expected: 
    - Status: 200 OK
    - Response contains job_id
    - K8s Job created successfully
    - System back to normal
```

**איפה להוסיף:** Jira → Test Steps → Add recovery steps

---

### 15. **Monitoring/Alerting** ⚠️ חסר!
**מה צריך:**

```yaml
Monitoring Requirements:
  - Alert when RabbitMQ connection fails
  - Log 5xx errors to monitoring system
  - Track failed /configure requests
  - No silent failures
```

**איפה להוסיף:** Jira → Requirements → Monitoring

---

## 📊 סיכום השדות החסרים

| # | שדה | חשיבות | סטטוס |
|---|-----|--------|-------|
| 1 | Test Type | 🔴 קריטי | ❌ חסר |
| 2 | Objective | 🔴 קריטי | ❌ חסר |
| 3 | Test Steps (מפורט) | 🔴 קריטי | ❌ חסר |
| 4 | Test Data (JSON מלא) | 🟡 חשוב | ❌ חסר |
| 5 | Automation Status | 🟡 חשוב | ❌ חסר |
| 6 | Execution Command | 🟡 חשוב | ❌ חסר |
| 7 | Post-Conditions | 🟡 חשוב | ❌ חסר |
| 8 | Assertions | 🔴 קריטי | ❌ חסר |
| 9 | Related Issues | 🟢 רצוי | ❌ חסר |
| 10 | Attachments | 🟢 רצוי | ❌ חסר |
| 11 | Test Results | 🟡 חשוב | ❌ חסר |
| 12 | Test Configuration | 🟡 חשוב | ❌ חסר |
| 13 | Architectural Context | 🟢 רצוי | ❌ חסר |
| 14 | Recovery Validation | 🟡 חשוב | ❌ חסר |
| 15 | Monitoring Requirements | 🟢 רצוי | ❌ חסר |

**סה"כ חסרים:** 15 שדות

---

## 🎯 עדיפויות תיקון

### 🔴 קריטי (תקן מיד!)
1. **Test Type** - בלעדיו Xray לא יזהה כטסט
2. **Objective** - חובה להבנת המטרה
3. **Test Steps (מפורט)** - לא אפשר להריץ בלי זה
4. **Assertions** - איך יודעים שהטסט עבר?

### 🟡 חשוב (תקן בהקדם)
5. **Test Data** - צריך payload מדויק
6. **Automation Status** - מעקב אחרי סטטוס
7. **Execution Command** - איך להריץ
8. **Post-Conditions** - ניקיון אחרי טסט
9. **Test Results** - תיעוד ביצוע
10. **Test Configuration** - הגדרות סביבה
11. **Recovery Validation** - וידוא החזרה לתקינות

### 🟢 רצוי (תקן כשיש זמן)
12. **Related Issues** - הקשר
13. **Attachments** - תיעוד ויזואלי
14. **Architectural Context** - הבנה מעמיקה
15. **Monitoring Requirements** - לעתיד

---

## 📋 Checklist מהיר

כדי להשלים את הטיקט, תוסיף:

```
✅ 1. Test Type = Integration Test
✅ 2. Objective (3 פסקאות: מטרה + Business Impact)
✅ 3. Test Steps (15 צעדים מפורטים)
✅ 4. Test Data (JSON payload מלא)
✅ 5. Automation Status = TO BE AUTOMATED
✅ 6. Execution Command
✅ 7. Post-Conditions (3 תנאים)
✅ 8. Assertions (8 assertions)
✅ 9. Related Issues (קשר ל-3 טיקטים)
✅ 10. Attachments (3 screenshots/logs)
✅ 11. Test Results = NOT YET EXECUTED
✅ 12. Test Configuration (5 פרמטרים)
✅ 13. Architectural Context (תרשים זרימה)
✅ 14. Recovery Validation (4 צעדים)
✅ 15. Monitoring Requirements (4 דרישות)
```

---

## 🔗 קבצים לדוגמה בפרויקט

אם אתה רוצה לראות דוגמה מלאה, תסתכל על:

1. **`documentation/jira/JIRA_XRAY_NEW_TESTS.md`** - 8 טיקטים מלאים עם כל השדות
2. **`documentation/jira/XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md`** - דוגמה מפורטת ביותר
3. **`documentation/jira/XRAY_IMPORT_GUIDE.md`** - מדריך ייבוא לXray

---

## 💡 טיפ מהיר

אם אתה רוצה, אני יכול ליצור לך **template מלא ומוכן** עבור PZ-13602 עם כל 15 השדות החסרים ממולאים. רק תגיד!

---

**סיכום:** יש לך בסיס טוב, אבל חסרים 15 שדות חשובים (4 מהם קריטיים) כדי שהטיקט יהיה מלא ומקצועי כמו השאר בפרויקט.

