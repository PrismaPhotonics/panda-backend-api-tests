# Alert Automation Summary - Quick Reference

**Date:** November 13, 2025  
**Purpose:** Quick reference guide for automating alert sending to Panda system

---

## 🎯 Quick Overview

**Process Flow:**
1. Authenticate → Get `access-token` cookie
2. Create Alert object → With required fields
3. Send Alert → Via `POST /prisma-210-1000/api/push-to-rabbit`
4. Process in RabbitMQ → Exchange `prisma`
5. Receive in Panda App → Display on map/journal

---

## 📡 API Details

### Base URL
```
https://10.10.10.100/prisma/api/
```

### Authentication Endpoint
```
POST /auth/login
Body: {"username": "prisma", "password": "prisma"}
Response: access-token cookie
```

### Alert Endpoint
```
POST /prisma-210-1000/api/push-to-rabbit
Headers: Cookie: access-token=...
Body: {
  "alertsAmount": 1,
  "dofM": 4163,
  "classId": 104,
  "severity": 3,
  "alertIds": ["test-123.4567"]
}
```

---

## 📦 Alert Payload Structure

### Required Fields:
- `alertsAmount` (int) - Number of alerts
- `dofM` (int) - Distance on fiber in meters (200-8700)
- `classId` (int) - Alert type: 103=SC, 104=SD
- `severity` (int) - Severity level: 1, 2, or 3
- `alertIds` (array[str]) - List of alert IDs

### Alert Types:
- **103** = SC (Single Channel)
- **104** = SD (Spatial Distribution)

### Severity Levels:
- **1** = Low (white)
- **2** = Medium (yellow/orange)
- **3** = High (red)

---

## 💻 Quick Code Example

```python
import requests
from blocksAndRepo.panda.entities.Alert import Alert
from tests.panda.testHelpers.ApiHelper import login_session, push_alert

# 1. Authenticate
BASE_URL = "https://10.10.10.100/prisma/api/"
session = login_session(BASE_URL, "prisma", "prisma", verify_ssl=False)

# 2. Create Alert
alert = Alert(
    alert_id="test-123.4567",
    classId=104,        # SD
    severity=3,         # High severity
    dof_m=4163,        # 4163 meters
    alerts_amount=1
)

# 3. Send Alert
result = push_alert(session, BASE_URL, {
    "alertsAmount": alert.alerts_amount,
    "dofM": alert.dof_m,
    "classId": alert.classId,
    "severity": alert.severity,
    "alertIds": [alert.alert_id]
})
```

---

## 🔧 Key Files

### Frontend Tests:
- `fe_panda_tests/blocksAndRepo/panda/alerts/AlertsBlocks.py` - Alert blocks
- `fe_panda_tests/blocksAndRepo/panda/entities/Alert.py` - Alert model
- `fe_panda_tests/tests/panda/testHelpers/ApiHelper.py` - API helpers
- `fe_panda_tests/config/project.properties` - Configuration

### Backend Tests:
- `be_focus_server_tests/infrastructure/test_rabbitmq_connectivity.py` - RabbitMQ tests

---

## ⚠️ Important Notes

1. **Authentication Required** - Must have `access-token` cookie
2. **Unique Alert ID** - Use `gen_alert_id_no_all_zeros()`
3. **Wait Time** - Wait 2-5 seconds between alerts
4. **Refresh View** - Navigate between tabs to refresh
5. **Site ID** - `prisma-210-1000` (from config)
6. **Alert End Time** - Alerts auto-close after 170 seconds

---

## 📚 Full Documentation

For complete documentation in Hebrew, see:
- `docs/02_user_guides/ALERT_AUTOMATION_GUIDE_HE.md`

---

**Version:** 1.0.0  
**Last Updated:** November 13, 2025

