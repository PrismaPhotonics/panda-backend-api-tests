# 🔍 מדריך מקיף: יצירת Alerts מה-Backend למערכת Panda

**תאריך:** 13 בנובמבר 2025  
**מטרה:** הבנה מלאה של תהליך יצירת alerts מה-Backend (BE) למערכת Panda

---

## 📋 תוכן עניינים

1. [סקירה כללית - ארכיטקטורה](#סקירה-כללית)
2. [תהליך יצירת Alert מה-BE - שלב אחר שלב](#תהליך-יצירת-alert-מה-be)
3. [מימוש ב-fe_panda_tests](#מימוש-ב-fe_panda_tests)
4. [מימוש ב-pz (Backend)](#מימוש-ב-pz-backend)
5. [תהליך דרך RabbitMQ](#תהליך-דרך-rabbitmq)
6. [WebApp ו-liveView](#webapp-ו-liveview)
7. [יצירת Alerts דרך K8s/BE](#יצירת-alerts-דרך-k8sbe)
8. [דוגמאות קוד מלאות](#דוגמאות-קוד-מלאות)

---

## 🎯 סקירה כללית - ארכיטקטורה

### תזרים הנתונים המלא:

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (pz)                              │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Collector  │───▶│ Baby Analyzer│───▶│   Algo ML    │ │
│  │  (Data)      │    │  (Process)   │    │  (Alerts)    │ │
│  └──────────────┘    └──────────────┘    └──────┬───────┘ │
│                                                    │         │
│                                                    │ Publish │
│                                                    ▼         │
│                                            ┌──────────────┐ │
│                                            │  RabbitMQ    │ │
│                                            │  Exchange:   │ │
│                                            │  "prisma"    │ │
│                                            └──────┬───────┘ │
└────────────────────────────────────────────────────┼─────────┘
                                                     │
                                                     │ Message Queue
                                                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PRISMA WEB APP API                             │
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │  POST /prisma-210-1000/api/push-to-rabbit          │   │
│  │  (Alternative: Direct RabbitMQ publish)            │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    PANDA APP                                 │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Map View    │    │  Journal     │    │  WebApp      │  │
│  │  (liveView)  │    │  (Alerts)    │    │  (UI)        │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
│  URL: https://10.10.10.100/liveView?siteId=prisma-210-1000 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 תהליך יצירת Alert מה-BE - שלב אחר שלב

### שלב 1: איסוף נתונים (Collector)

**מיקום:** `pz/microservices/collector/Collector.py`

**תפקיד:**
- אוסף נתונים מהסיב (fiber)
- שולח ל-Baby Analyzer לעיבוד

**תהליך:**
```python
# Collector אוסף נתונים ומעביר ל-Baby Analyzer
collector → baby_analyzer (via RabbitMQ)
```

---

### שלב 2: עיבוד נתונים (Baby Analyzer)

**מיקום:** `pz/microservices/baby_analyzer/babyanalyzer.py`

**תפקיד:**
- מעבד chunks של נתונים
- מפעיל processors שונים
- יוצר metadata

**תהליך:**
```python
# Baby Analyzer מעבד chunks
baby_analyzer.process_chunk(chunk) → processed_data
```

---

### שלב 3: זיהוי Alerts (Algo ML)

**מיקום:** `pz/microservices/algo/DataScience/`

**קבצים רלוונטיים:**
- `utils/io/alerts.py` - טיפול ב-alerts
- `utils/algo_messages/messages.py` - הודעות alerts
- `Reports/OfficialMlReports.py` - דוחות alerts
- `core/runner/callbacks/producers.py` - producers ל-RabbitMQ

**תהליך:**
```python
# Algo ML מזהה alerts
algo_ml.detect_alert(data) → AlertReport
```

---

### שלב 4: יצירת Alert Report

**מיקום:** `pz/microservices/algo/Reports/OfficialMlReports.py`

**מבנה Alert Report:**
```python
class OfficialMlAlertReport(AlgoAlertReport):
    """
    דוח alert רשמי מה-ML
    מכיל:
    - alert_id
    - class_id (103=SC, 104=SD)
    - severity (1, 2, 3)
    - distance_m (DOF)
    - alert_time
    - ועוד...
    """
```

---

### שלב 5: פרסום ל-RabbitMQ

**מיקום:** `pz/microservices/algo/DataScience/utils/algo_messages/messages.py`

**Routing Keys:**
- `Algorithm.AlertReport.MLGround` - Ground alerts
- `Algorithm.AlertReport.Pulse` - Pulse alerts
- `Algorithm.AlertReport.FiberCut` - Fiber cut alerts
- `Algorithm.AlertReport` - General alerts

**Exchange:** `prisma` (יחיד במערכת!)

**תהליך:**
```python
# יצירת message
alert_report = OfficialMlAlertReport(...)
message = MessageMLGroundAlertReport(alert_report)

# פרסום ל-RabbitMQ
producer.publish(
    exchange="prisma",
    routing_key="Algorithm.AlertReport.MLGround",
    message=message
)
```

---

### שלב 6: קבלה ב-Prisma Web App

**מיקום:** Backend API (`/prisma/api/`)

**תהליך:**
- Prisma Web App מקבל את ה-message מ-RabbitMQ
- מעבד את ה-alert
- שומר ב-MongoDB
- מעדכן את Panda App

---

### שלב 7: תצוגה ב-Panda App

**WebApp URL:** `https://10.10.10.100/liveView?siteId=prisma-210-1000`

**תהליך:**
- Panda App מקבל את ה-alert דרך RabbitMQ
- מציג במפה (Map View)
- מציג ב-Journal
- מאפשר תחקירים

---

## 💻 מימוש ב-fe_panda_tests

### מיקום הקבצים:

**1. API Helper:**
- `fe_panda_tests/tests/panda/testHelpers/ApiHelper.py`

**2. Alerts Blocks:**
- `fe_panda_tests/blocksAndRepo/panda/alerts/AlertsBlocks.py`

**3. Alert Entity:**
- `fe_panda_tests/blocksAndRepo/panda/entities/Alert.py`

### תהליך השליחה:

```python
# 1. Authentication
session = login_session(base_url, username, password, verify_ssl=False)

# 2. יצירת Alert
alert = Alert(
    alert_id="test-123.4567",
    classId=104,        # SD
    severity=3,
    dof_m=4163,
    alerts_amount=1
)

# 3. שליחת Alert דרך API
push_alert(session, base_url, {
    "alertsAmount": alert.alerts_amount,
    "dofM": alert.dof_m,
    "classId": alert.classId,
    "severity": alert.severity,
    "alertIds": [alert.alert_id]
})
```

### Endpoint:

```
POST /prisma-210-1000/api/push-to-rabbit
Base URL: https://10.10.10.100/prisma/api/
```

---

## 🏗️ מימוש ב-pz (Backend)

### 1. יצירת Alert מה-ML

**מיקום:** `pz/microservices/algo/DataScience/utils/io/alerts.py`

**תהליך:**
```python
class AlertsLoader:
    """
    טוען alerts מ-ML וממיר לפורמט נדרש
    """
    
    @classmethod
    def load(cls, alerts_path: str):
        # טוען alerts מ-ML output
        # ממיר ל-GeoDataFrame
        # מחזיר alerts_updates_df, alerts_gdf, recordings_df
        pass
```

---

### 2. יצירת Alert Report

**מיקום:** `pz/microservices/algo/Reports/OfficialMlReports.py`

```python
class OfficialMlAlertReport(AlgoAlertReport):
    """
    דוח alert רשמי מה-ML
    יורש מ-AlgoAlertReport
    """
    def __init__(self, algorun_id: str = None):
        super().__init__(algorun_id)
```

---

### 3. המרה ל-Message

**מיקום:** `pz/microservices/algo/DataScience/utils/algo_messages/messages.py`

```python
@register_algo_msg(OfficialMlAlertReport)
class MessageOfficialMlAlertReport(MessageAlgoReportBase):
    routing_key = "Algorithm.AlertReport.MLGround"
    
    def serialize(self) -> bytes:
        # ממיר את ה-AlertReport ל-JSON
        attr_dict = self.body.get_attr_dict()
        return json.dumps(attr_dict).encode("utf_8")
```

---

### 4. פרסום ל-RabbitMQ

**מיקום:** `pz/microservices/algo/DataScience/core/runner/callbacks/producers.py`

```python
class AlertsProducer(PredictCallback):
    """
    Producer שמוציא alerts ל-RabbitMQ
    """
    
    def on_predict_step(self, x: EnrichedWaterfallContainer, runner=None, **kwargs):
        # מזהה alerts
        alerts = self.detect_alerts(x)
        
        # יוצר AlertReport
        for alert in alerts:
            alert_report = OfficialMlAlertReport(...)
            message = generate_algo_msg(alert_report)
            
            # מפרסם ל-RabbitMQ
            self.producer.publish(
                exchange="prisma",
                routing_key=message.routing_key,
                body=message.serialize()
            )
```

---

## 🐰 תהליך דרך RabbitMQ

### Exchange Configuration:

**Exchange Name:** `prisma` (יחיד במערכת!)

**Exchange Type:** `topic`

**Durable:** `True`

### Routing Keys:

| Routing Key | תיאור | Alert Type |
|-------------|-------|------------|
| `Algorithm.AlertReport.MLGround` | Ground alerts | ML Ground |
| `Algorithm.AlertReport.Pulse` | Pulse alerts | Pulse |
| `Algorithm.AlertReport.FiberCut` | Fiber cut alerts | Fiber Cut |
| `Algorithm.AlertReport` | General alerts | General |

### Queue Configuration:

**Queue Name:** דינמי לפי site ID (`prisma-210-1000`)

**Queue Creation:** אוטומטי על ידי Panda App

---

## 🌐 WebApp ו-liveView

### WebApp URL:

```
https://10.10.10.100/liveView?siteId=prisma-210-1000
```

### פרמטרים:

- **siteId:** `prisma-210-1000` (Site ID של הסביבה)

### תפקיד:

- **liveView** - תצוגת מפה חיה עם alerts
- **Journal** - רשימת alerts
- **Investigation** - תחקירים מ-alerts

### מימוש ב-fe_panda_tests:

**מיקום:** `fe_panda_tests/blocksAndRepo/panda/PandaNativeRepo.py`

```python
class PandaNativeRepo:
    # Map tab
    map_tab = [AppiumBy.XPATH, '//*[@data-testid="liveView-nav-element"]']
    
    # Journal tab
    alert_journal_tab = [AppiumBy.XPATH, '//*[@data-testid="investigations-nav-element"]']
    
    # Investigation tab
    investigate_tab = [AppiumBy.XPATH, '//*[@data-testid="analysis-nav-element"]']
```

---

## ☸️ יצירת Alerts דרך K8s/BE

### תהליך דרך Kubernetes:

#### 1. גישה ל-K8s:

**מיקום:** `docs/02_user_guides/K8S_AGENT_GUIDE.md`

**פקודות:**
```bash
# גישה ל-K8s cluster
kubectl get pods -n panda

# בדיקת RabbitMQ
kubectl get pods -n panda | grep rabbitmq

# בדיקת Algo pods
kubectl get pods -n panda | grep algo
```

#### 2. בדיקת RabbitMQ:

```bash
# בדיקת queues
kubectl exec -n panda rabbitmq-pod -- rabbitmqctl list_queues

# בדיקת exchanges
kubectl exec -n panda rabbitmq-pod -- rabbitmqctl list_exchanges

# בדיקת bindings
kubectl exec -n panda rabbitmq-pod -- rabbitmqctl list_bindings
```

#### 3. יצירת Alert דרך Pod:

**דרך 1: דרך API (מומלץ)**
```python
# שימוש ב-API endpoint
POST /prisma-210-1000/api/push-to-rabbit
```

**דרך 2: ישירות ל-RabbitMQ**
```python
# חיבור ישיר ל-RabbitMQ
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('10.10.10.100', 5672)
)
channel = connection.channel()

channel.exchange_declare(exchange='prisma', exchange_type='topic', durable=True)

# פרסום alert
channel.basic_publish(
    exchange='prisma',
    routing_key='Algorithm.AlertReport.MLGround',
    body=json.dumps(alert_payload)
)
```

---

## 📝 דוגמאות קוד מלאות

### דוגמה 1: יצירת Alert מה-BE דרך API

```python
import requests
from datetime import datetime

# 1. Authentication
BASE_URL = "https://10.10.10.100/prisma/api/"
session = requests.Session()
session.verify = False

login_resp = session.post(
    f"{BASE_URL}auth/login",
    json={"username": "prisma", "password": "prisma"}
)
login_resp.raise_for_status()

# 2. יצירת Alert Payload
alert_payload = {
    "alertsAmount": 1,
    "dofM": 4163,           # מרחק על הסיב במטרים
    "classId": 104,         # 103=SC, 104=SD
    "severity": 3,          # 1, 2, או 3
    "alertIds": ["test-123.4567"]
}

# 3. שליחת Alert
resp = session.post(
    f"{BASE_URL}prisma-210-1000/api/push-to-rabbit",
    json=alert_payload
)
resp.raise_for_status()

print(f"Alert sent: {resp.json()}")
```

---

### דוגמה 2: יצירת Alert ישירות ל-RabbitMQ

```python
import pika
import json
from datetime import datetime

# 1. חיבור ל-RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='10.10.10.100',
        port=5672,
        virtual_host='/',
        credentials=pika.PlainCredentials('guest', 'guest')
    )
)
channel = connection.channel()

# 2. הגדרת Exchange
channel.exchange_declare(
    exchange='prisma',
    exchange_type='topic',
    durable=True
)

# 3. יצירת Alert Message
alert_message = {
    "algorun_id": "test-run-123",
    "alert_id": "test-123.4567",
    "class_id": 104,        # SD
    "severity": 3,
    "distance_m": 4163,
    "alert_time": datetime.now().isoformat(),
    "time_interval_s": 150,
    "is_external": False,
    "is_dead": False,
    "is_faded": False
}

# 4. פרסום ל-RabbitMQ
channel.basic_publish(
    exchange='prisma',
    routing_key='Algorithm.AlertReport.MLGround',
    body=json.dumps(alert_message),
    properties=pika.BasicProperties(
        delivery_mode=2,  # make message persistent
        content_type='application/json'
    )
)

print(f"Alert published: {alert_message['alert_id']}")

# 5. סגירת חיבור
connection.close()
```

---

### דוגמה 3: יצירת Alert דרך K8s Pod

```python
from kubernetes import client, config
import requests

# 1. טעינת K8s config
config.load_kube_config()

# 2. חיבור ל-Pod
v1 = client.CoreV1Api()
pods = v1.list_namespaced_pod(namespace="panda", label_selector="app=prisma-api")

if pods.items:
    pod = pods.items[0]
    pod_name = pod.metadata.name
    
    # 3. ביצוע exec ב-pod
    exec_command = [
        '/bin/sh',
        '-c',
        f'curl -X POST http://localhost:8080/prisma-210-1000/api/push-to-rabbit '
        f'-H "Content-Type: application/json" '
        f'-d \'{{"alertsAmount":1,"dofM":4163,"classId":104,"severity":3,"alertIds":["test-123.4567"]}}\''
    ]
    
    resp = stream(
        v1.connect_get_namespaced_pod_exec,
        pod_name,
        'panda',
        command=exec_command,
        stderr=True, stdin=False,
        stdout=True, tty=False
    )
```

---

### דוגמה 4: בדיקת Alert ב-Panda App

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. פתיחת Panda App
driver = webdriver.Chrome()
driver.get("https://10.10.10.100/liveView?siteId=prisma-210-1000")

# 2. התחברות
username_input = driver.find_element(By.NAME, "username")
password_input = driver.find_element(By.NAME, "password")
login_button = driver.find_element(By.XPATH, "//input[@type='submit']")

username_input.send_keys("prisma")
password_input.send_keys("prisma")
login_button.click()

# 3. המתנה ל-alert
wait = WebDriverWait(driver, 30)
alert_element = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//p[contains(.,'test-123.4567')]")
    )
)

print(f"Alert found: {alert_element.text}")

# 4. בדיקת alert במפה
map_tab = driver.find_element(By.XPATH, '//*[@data-testid="liveView-nav-element"]')
map_tab.click()

# 5. בדיקת alert ב-journal
journal_tab = driver.find_element(By.XPATH, '//*[@data-testid="investigations-nav-element"]')
journal_tab.click()

alert_in_journal = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//p[contains(.,'test-123.4567')]")
    )
)

print(f"Alert in journal: {alert_in_journal.text}")
```

---

## 🔍 סיכום - תהליך מלא

### תהליך מה-BE:

1. ✅ **Collector** אוסף נתונים מהסיב
2. ✅ **Baby Analyzer** מעבד את הנתונים
3. ✅ **Algo ML** מזהה alerts
4. ✅ **AlertReport** נוצר
5. ✅ **Message** נוצר מה-Report
6. ✅ **RabbitMQ** מפרסם את ה-Message
7. ✅ **Prisma Web App** מקבל את ה-Message
8. ✅ **Panda App** מציג את ה-Alert

### תהליך מ-Test Automation:

1. ✅ **Authentication** → קבלת `access-token`
2. ✅ **יצירת Alert** → Alert object
3. ✅ **שליחת Alert** → דרך API endpoint
4. ✅ **RabbitMQ** → עיבוד ה-Message
5. ✅ **Panda App** → תצוגה במפה וב-Journal

---

## 📚 קבצים רלוונטיים

### fe_panda_tests:
- `tests/panda/testHelpers/ApiHelper.py` - API helpers
- `blocksAndRepo/panda/alerts/AlertsBlocks.py` - Alert blocks
- `blocksAndRepo/panda/entities/Alert.py` - Alert model
- `config/project.properties` - Configuration

### pz (Backend):
- `microservices/algo/DataScience/utils/io/alerts.py` - Alert I/O
- `microservices/algo/DataScience/utils/algo_messages/messages.py` - Messages
- `microservices/algo/Reports/OfficialMlReports.py` - Alert reports
- `microservices/baby_analyzer/babyanalyzer.py` - Data processor
- `microservices/collector/Collector.py` - Data collector

### Documentation:
- `docs/02_user_guides/ALERT_AUTOMATION_GUIDE_HE.md` - Frontend automation
- `docs/02_user_guides/K8S_AGENT_GUIDE.md` - K8s management

---

**תאריך עדכון:** 13 בנובמבר 2025  
**גרסה:** 1.0.0

