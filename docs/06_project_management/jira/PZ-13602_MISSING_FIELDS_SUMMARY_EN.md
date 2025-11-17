# PZ-13602 Missing Fields Analysis

## Summary
Your Jira ticket **PZ-13602** (RabbitMQ Outage - Live Configure) is missing **15 critical fields** compared to the project's standard test ticket structure.

---

## ✅ What You Have (Good!)

- Test ID: PZ-13602
- Summary: Integration – RabbitMQ outage on Live configure
- Description: Clear context
- Priority: Medium
- Components: focus-server, integration, live, rabbit, resilience
- Requirements: FOCUS-API-CONFIGURE
- Pre-Conditions: PC-030
- Acceptance Criteria: Well defined
- Expected Outcomes: 3 actions with results

---

## ❌ Missing Fields (15)

### 🔴 Critical (Must Add)

**1. Test Type**
```
Test Type: Integration Test
```

**2. Objective**
```
Objective:
  Validate graceful RabbitMQ failure handling during Live configuration.
  System must fail fast without launching K8s resources (Jobs/Services)
  and return proper 5xx error with clear message.

Business Impact:
  - Prevents resource leaks
  - Provides clear error messages
  - Ensures system stability during outages
```

**3. Test Steps** (Detailed)
```
| # | Action | Expected Result |
|---|--------|-----------------|
| 1 | Block RabbitMQ network | RabbitMQ unreachable |
| 2 | POST /configure with live payload | 503/502 error received |
| 3 | Verify no job_id in response | No job_id present |
| 4 | Check K8s Jobs | No grpc-job-* created |
| 5 | Check K8s Services | No grpc-service-* created |
| 6 | Check Focus Server logs | "RabbitMQ unavailable" logged |
| 7 | Verify no crash | No stacktrace in logs |
| 8 | Restore RabbitMQ | Connection restored |
| 9 | Retry POST /configure | 200 OK with job_id |
```

**4. Assertions**
```python
Critical Assertions:
  1. assert response.status_code in [502, 503]
  2. assert "job_id" not in response.json()
  3. assert "rabbitmq" in error_message.lower()
  4. assert len(new_k8s_jobs) == 0
  5. assert len(new_k8s_services) == 0
  6. assert "unavailable" in focus_server_logs
  7. assert "panic" not in focus_server_logs
  8. assert "traceback" not in focus_server_logs
```

---

### 🟡 Important (Should Add)

**5. Test Data**
```json
{
  "displayInfo": {"height": 1000},
  "channels": {"min": 1, "max": 10},
  "frequencyRange": {"min": 0, "max": 500},
  "nfftSelection": 1024,
  "displayTimeAxisDuration": 10,
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```

**6. Automation Status**
```
Status: TO BE AUTOMATED
Test Function: test_rabbitmq_outage_live_configure
Test File: tests/integration/resilience/test_rabbitmq_outage.py
```

**7. Execution Command**
```bash
pytest tests/integration/resilience/test_rabbitmq_outage.py::test_rabbitmq_outage_live_configure -v
```

**8. Post-Conditions**
```
- PC-CLEANUP-001: RabbitMQ network restored
- PC-CLEANUP-002: No orphaned K8s resources
- PC-CLEANUP-003: Focus Server operational
```

**9. Test Results**
```
Last Execution: NOT YET EXECUTED
Expected: PASS after implementation
```

**10. Test Configuration**
```
Environment: new_production
Namespace: panda
Focus Server: https://10.10.100.100/focus-server/
RabbitMQ: 10.10.100.107:5672
```

**11. Recovery Validation**
```
After RabbitMQ restored:
  - POST /configure → 200 OK
  - job_id returned
  - System normal
```

---

### 🟢 Optional (Nice to Have)

**12. Related Issues**
- Link to PZ-13603 (Historic mode)
- Link to FOCUS-RESILIENCE epic

**13. Attachments**
- Screenshot: 502/503 error response
- Screenshot: RabbitMQ status
- Log file: Focus Server logs during failure

**14. Architectural Context**
```
Flow:
  Frontend → Focus Server → RabbitMQ (FAILS)
  Focus Server → Should NOT create K8s Job
  Focus Server → Returns 5xx to Frontend
```

**15. Monitoring Requirements**
- Alert on RabbitMQ connection failures
- Log 5xx errors
- Track failed /configure requests

---

## 📊 Priority Summary

| Priority | Count | Fields |
|----------|-------|--------|
| 🔴 Critical | 4 | Test Type, Objective, Test Steps, Assertions |
| 🟡 Important | 7 | Test Data, Automation, Execution, Post-Conditions, Results, Config, Recovery |
| 🟢 Optional | 4 | Related Issues, Attachments, Architecture, Monitoring |
| **Total Missing** | **15** | |

---

## ✅ Quick Checklist

To complete the ticket, add:

```
□ Test Type = Integration Test
□ Objective (2-3 paragraphs)
□ Test Steps (15 detailed steps)
□ Test Data (full JSON)
□ Automation Status
□ Execution Command
□ Post-Conditions
□ Assertions (8 items)
□ Related Issues
□ Attachments (3 files)
□ Test Results
□ Test Configuration
□ Architectural Context
□ Recovery Validation
□ Monitoring Requirements
```

---

## 📚 Reference Examples

See complete examples in the project:
- `documentation/jira/JIRA_XRAY_NEW_TESTS.md` - 8 complete tickets
- `documentation/jira/XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md` - Detailed example

---

## 💡 Next Step

Would you like me to create a **complete template** for PZ-13602 with all 15 missing fields filled in?

---

**Full analysis:** `documentation/jira/PZ-13602_MISSING_FIELDS_ANALYSIS.md`

