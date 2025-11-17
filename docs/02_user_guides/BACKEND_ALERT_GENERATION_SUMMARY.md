# Backend Alert Generation - Complete Analysis Summary

**Date:** November 13, 2025  
**Purpose:** Complete understanding of alert generation process from Backend to Panda system

---

## 🎯 Overview

### Complete Flow:

```
Backend (pz) → RabbitMQ → Prisma Web App → Panda App (liveView)
```

---

## 📊 Architecture Components

### 1. Backend (pz)

**Components:**
- **Collector** (`pz/microservices/collector/Collector.py`) - Data collection
- **Baby Analyzer** (`pz/microservices/baby_analyzer/babyanalyzer.py`) - Data processing
- **Algo ML** (`pz/microservices/algo/DataScience/`) - Alert detection
- **Alert Reports** (`pz/microservices/algo/Reports/OfficialMlReports.py`) - Alert generation

**Process:**
1. Collector gathers fiber data
2. Baby Analyzer processes chunks
3. Algo ML detects alerts
4. AlertReport created
5. Message published to RabbitMQ

---

### 2. RabbitMQ

**Exchange:** `prisma` (single exchange in system!)

**Routing Keys:**
- `Algorithm.AlertReport.MLGround` - Ground alerts
- `Algorithm.AlertReport.Pulse` - Pulse alerts
- `Algorithm.AlertReport.FiberCut` - Fiber cut alerts
- `Algorithm.AlertReport` - General alerts

**Queue:** Dynamic based on site ID (`prisma-210-1000`)

---

### 3. Prisma Web App API

**Endpoint:** `POST /prisma-210-1000/api/push-to-rabbit`

**Base URL:** `https://10.10.10.100/prisma/api/`

**Process:**
- Receives alert from RabbitMQ
- Processes and stores in MongoDB
- Updates Panda App

---

### 4. Panda App

**WebApp URL:** `https://10.10.10.100/liveView?siteId=prisma-210-1000`

**Views:**
- **Map View** (liveView) - Live map with alerts
- **Journal** - Alerts list
- **Investigation** - Alert investigations

---

## 💻 Implementation Locations

### Frontend Tests (fe_panda_tests):

- `tests/panda/testHelpers/ApiHelper.py` - API helpers
- `blocksAndRepo/panda/alerts/AlertsBlocks.py` - Alert blocks
- `blocksAndRepo/panda/entities/Alert.py` - Alert model

**Process:**
```python
# 1. Authenticate
session = login_session(base_url, username, password)

# 2. Create Alert
alert = Alert(alert_id="test-123", classId=104, severity=3, dof_m=4163)

# 3. Send via API
push_alert(session, base_url, {
    "alertsAmount": 1,
    "dofM": 4163,
    "classId": 104,
    "severity": 3,
    "alertIds": ["test-123"]
})
```

---

### Backend (pz):

**Key Files:**
- `microservices/algo/DataScience/utils/io/alerts.py` - Alert I/O
- `microservices/algo/DataScience/utils/algo_messages/messages.py` - Messages
- `microservices/algo/Reports/OfficialMlReports.py` - Alert reports
- `microservices/algo/DataScience/core/runner/callbacks/producers.py` - Producers

**Process:**
```python
# 1. Detect alerts
alerts = algo_ml.detect_alerts(data)

# 2. Create AlertReport
alert_report = OfficialMlAlertReport(...)

# 3. Create Message
message = MessageMLGroundAlertReport(alert_report)

# 4. Publish to RabbitMQ
producer.publish(
    exchange="prisma",
    routing_key="Algorithm.AlertReport.MLGround",
    body=message.serialize()
)
```

---

## 🔄 Complete Process Flow

### From Backend:

1. **Data Collection** → Collector gathers fiber data
2. **Data Processing** → Baby Analyzer processes chunks
3. **Alert Detection** → Algo ML detects alerts
4. **Alert Report** → OfficialMlAlertReport created
5. **Message Creation** → MessageMLGroundAlertReport created
6. **RabbitMQ Publish** → Published to `prisma` exchange
7. **Web App Processing** → Prisma Web App processes message
8. **Panda Display** → Alert shown in Map/Journal

### From Test Automation:

1. **Authentication** → Get `access-token` cookie
2. **Create Alert** → Alert object with required fields
3. **Send via API** → POST to `/prisma-210-1000/api/push-to-rabbit`
4. **RabbitMQ** → Message processed
5. **Panda App** → Alert displayed

---

## 🐰 RabbitMQ Details

### Exchange:
- **Name:** `prisma`
- **Type:** `topic`
- **Durable:** `True`

### Message Format:
```json
{
  "algorun_id": "run-123",
  "alert_id": "test-123.4567",
  "class_id": 104,
  "severity": 3,
  "distance_m": 4163,
  "alert_time": "2025-11-13T11:43:41",
  "time_interval_s": 150
}
```

---

## 🌐 WebApp & liveView

### URL:
```
https://10.10.10.100/liveView?siteId=prisma-210-1000
```

### Parameters:
- **siteId:** `prisma-210-1000` (Environment Site ID)

### Features:
- Live map view with alerts
- Journal with alerts list
- Investigation from alerts

---

## ☸️ K8s Integration

### Access:
```bash
# List pods
kubectl get pods -n panda

# Check RabbitMQ
kubectl get pods -n panda | grep rabbitmq

# Check queues
kubectl exec -n panda rabbitmq-pod -- rabbitmqctl list_queues
```

### Creating Alerts:

**Method 1: Via API (Recommended)**
```python
POST /prisma-210-1000/api/push-to-rabbit
```

**Method 2: Direct RabbitMQ**
```python
channel.basic_publish(
    exchange='prisma',
    routing_key='Algorithm.AlertReport.MLGround',
    body=json.dumps(alert_payload)
)
```

---

## 📚 Key Files Reference

### Frontend Tests:
- `fe_panda_tests/tests/panda/testHelpers/ApiHelper.py`
- `fe_panda_tests/blocksAndRepo/panda/alerts/AlertsBlocks.py`
- `fe_panda_tests/blocksAndRepo/panda/entities/Alert.py`

### Backend:
- `pz/microservices/algo/DataScience/utils/io/alerts.py`
- `pz/microservices/algo/DataScience/utils/algo_messages/messages.py`
- `pz/microservices/algo/Reports/OfficialMlReports.py`
- `pz/microservices/baby_analyzer/babyanalyzer.py`

### Documentation:
- `docs/02_user_guides/BACKEND_ALERT_GENERATION_COMPLETE_GUIDE_HE.md` - Full guide (Hebrew)
- `docs/02_user_guides/ALERT_AUTOMATION_GUIDE_HE.md` - Frontend automation
- `docs/02_user_guides/K8S_AGENT_GUIDE.md` - K8s management

---

## ✅ Summary

### Backend Process:
1. Data collection → Processing → Alert detection → Report creation → RabbitMQ publish

### Test Automation Process:
1. Authentication → Alert creation → API send → RabbitMQ → Panda display

### Key Points:
- **Single Exchange:** `prisma` (only exchange in system)
- **Site ID:** `prisma-210-1000`
- **WebApp URL:** `https://10.10.10.100/liveView?siteId=prisma-210-1000`
- **API Endpoint:** `POST /prisma-210-1000/api/push-to-rabbit`

---

**Version:** 1.0.0  
**Last Updated:** November 13, 2025

