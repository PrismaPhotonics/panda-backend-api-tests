# 🔍 מדריך לבדיקת לוגי Pods של Alerts

**תאריך:** 13 בנובמבר 2025  
**מטרה:** איך לבדוק בלוגים של pods שדר alerts נשלחו ועובדו בהצלחה

---

## 📋 תוכן עניינים

1. [Pods שמטפלים ב-Alerts](#pods-שמטפלים-ב-alerts)
2. [בדיקת לוגים דרך kubectl](#בדיקת-לוגים-דרך-kubectl)
3. [בדיקת לוגים דרך Python](#בדיקת-לוגים-דרך-python)
4. [מילות מפתח לחיפוש](#מילות-מפתח-לחיפוש)
5. [דוגמאות שימוש](#דוגמאות-שימוש)

---

## 🎯 Pods שמטפלים ב-Alerts

### 0. **Ingress Controller Pod** ⭐ (המקום הראשי לבדיקת לוגי push-to-rabbit!)
- **שם Pod:** `ingress-nginx-controller-*` (לדוגמה: `ingress-nginx-controller-55694fd6ff-rqgp9`)
- **Namespace:** `kube-system`
- **תפקיד:** Entry point לכל ה-HTTP requests, כולל `push-to-rabbit` endpoint
- **לוגים רלוונטיים:**
  - `POST /prisma/api/prisma-210-1000/api/push-to-rabbit` - בקשות ל-alert endpoint
  - `push-to-rabbit` - כל הבקשות ל-endpoint
  - `201` - Status code של הצלחה
  - `alert_sound.mp3` - בקשות ל-alert sound (מעיד שהתהליך עובד!)
- **למה חשוב:** כל ה-HTTP requests עוברים דרך Ingress Controller, אז הלוגים שלו מראים את כל הבקשות!
- **פקודה לבדיקה:**
  ```bash
  kubectl logs -n kube-system ingress-nginx-controller-55694fd6ff-rqgp9 --tail=1000 | grep -i "push-to-rabbit"
  ```

### 1. **Focus Server Pod** (מטפל ב-API של alerts)
- **שם Pod:** `panda-panda-focus-server-*` (לדוגמה: `panda-panda-focus-server-78dbcfd9d9-4ld4s`)
- **תפקיד:** מטפל ב-API requests, כולל Prisma Web App API
- **לוגים רלוונטיים:**
  - `push-to-rabbit` - כשמקבל alert דרך API endpoint
  - `POST.*push-to-rabbit` - HTTP requests ל-alert endpoint
  - `alert.*received` - כשמקבל alert
  - `alert.*published` - כש-alert נשלח ל-RabbitMQ
- **הערה:** הלוגים של `push-to-rabbit` לא תמיד מופיעים כאן - לבדוק ב-Ingress Controller!

### 2. **RabbitMQ Pod** (מעביר alerts)
- **שם Pod:** `rabbitmq-panda-0` (StatefulSet)
- **תפקיד:** מעביר alerts בין components דרך exchange `prisma`
- **לוגים רלוונטיים:**
  - `message.*published` - כש-message נשלח
  - `message.*consumed` - כש-message נצרך
  - `exchange.*prisma` - פעילות ב-exchange
  - `routing_key.*Algorithm.AlertReport` - routing של alerts

### 3. **gRPC Job Pods** (Baby Analyzer - מעבד נתונים)
- **שם Pod:** `grpc-job-*` (לדוגמה: `grpc-job-1-3-rm5ms`)
- **תפקיד:** מעבד chunks של נתונים, מזהה alerts
- **לוגים רלוונטיים:**
  - `alert.*detected` - כש-alert מזוהה
  - `alert.*published` - כש-alert נשלח ל-RabbitMQ
  - `Algorithm.AlertReport` - כשמפרסם alert report
  - `MLGroundAlertReport` - alerts של ground

### 4. **MongoDB Pod** (שומר alerts)
- **שם Pod:** `mongodb-*` (לדוגמה: `mongodb-7cb5d67cc5-wb7qz`)
- **תפקיד:** שומר alerts ב-database
- **הערה:** בדרך כלל לא בודקים לוגים של MongoDB ישירות, אלא דרך ה-application logs

### 5. **SEGY Recorder Pod** (יכול לעבד alerts)
- **שם Pod:** `panda-panda-segy-recorder-*`
- **תפקיד:** יכול לעבד alerts הקשורים ל-recordings

---

## 🔧 בדיקת לוגים דרך kubectl

### 0. מציאת Ingress Controller Pod (מומלץ להתחיל כאן!):

```bash
# Ingress Controller pods (kube-system namespace)
kubectl get pods -n kube-system | grep ingress

# בדיקת לוגי push-to-rabbit ב-Ingress Controller
kubectl logs -n kube-system ingress-nginx-controller-55694fd6ff-rqgp9 --tail=1000 | grep -i "push-to-rabbit"
```

### 1. מציאת Pods:

```bash
# כל ה-pods ב-namespace panda
kubectl get pods -n panda

# Focus Server pods (מטפל ב-API)
kubectl get pods -n panda | grep focus-server

# RabbitMQ pods
kubectl get pods -n panda | grep rabbitmq

# gRPC Job pods (Baby Analyzer)
kubectl get pods -n panda | grep grpc-job

# MongoDB pods
kubectl get pods -n panda | grep mongodb
```

### 2. צפייה בלוגים:

```bash
# לוגים של Ingress Controller (מומלץ להתחיל כאן!) ⭐
kubectl logs -n kube-system ingress-nginx-controller-55694fd6ff-rqgp9 --tail=1000 | grep -i "push-to-rabbit"

# לוגים של Focus Server (מטפל ב-API של alerts)
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=100

# לוגים של RabbitMQ
kubectl logs -n panda rabbitmq-panda-0 --tail=100

# לוגים של gRPC Job (Baby Analyzer) - בחר pod ספציפי
kubectl logs -n panda grpc-job-1-3-rm5ms --tail=100

# לוגים של MongoDB
kubectl logs -n panda mongodb-7cb5d67cc5-wb7qz --tail=100
```

### 3. צפייה בלוגים בזמן אמת (follow):

```bash
# Follow logs של Ingress Controller (מומלץ!) ⭐
kubectl logs -n kube-system ingress-nginx-controller-55694fd6ff-rqgp9 --tail=1000 -f | grep -i "push-to-rabbit\|prisma"

# Follow logs של Focus Server (מטפל ב-API)
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -f

# Follow logs של RabbitMQ
kubectl logs -n panda rabbitmq-panda-0 -f

# Follow logs של gRPC Job (Baby Analyzer)
kubectl logs -n panda grpc-job-1-3-rm5ms -f
```

### 4. חיפוש מילות מפתח:

```bash
# חיפוש "alert" בלוגים
kubectl logs -n panda <pod-name> --tail=1000 | grep -i alert

# חיפוש "push-to-rabbit"
kubectl logs -n panda <pod-name> --tail=1000 | grep -i "push-to-rabbit"

# חיפוש "Algorithm.AlertReport"
kubectl logs -n panda <pod-name> --tail=1000 | grep -i "Algorithm.AlertReport"

# חיפוש alert ID ספציפי
kubectl logs -n panda <pod-name> --tail=1000 | grep "test-sd-123"
```

---

## 🐍 בדיקת לוגים דרך Python

### שימוש ב-KubernetesManager:

```python
from src.infrastructure.kubernetes_manager import KubernetesManager
from config.config_manager import ConfigManager

# יצירת manager
config_manager = ConfigManager()
k8s_manager = KubernetesManager(config_manager)

# קבלת לוגים של pod
pod_name = "panda-panda-prisma-web-app-xxx"
logs = k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=100)

# חיפוש מילות מפתח
alert_logs = [line for line in logs.split('\n') if 'alert' in line.lower()]
print('\n'.join(alert_logs))
```

### שימוש ב-SSH Manager:

```python
from src.infrastructure.ssh_manager import SSHManager
from config.config_manager import ConfigManager

# יצירת SSH manager
config_manager = ConfigManager()
ssh_manager = SSHManager(config_manager)
ssh_manager.connect()

# הרצת kubectl דרך SSH
pod_name = "panda-panda-prisma-web-app-xxx"
command = f"kubectl logs -n panda {pod_name} --tail=100 | grep -i alert"
result = ssh_manager.execute_command(command)

print(result['stdout'])
```

---

## 🔎 מילות מפתח לחיפוש

### Ingress Controller (מומלץ להתחיל כאן!): ⭐
- `POST /prisma/api/prisma-210-1000/api/push-to-rabbit` - בקשות ל-alert endpoint
- `push-to-rabbit` - כל הבקשות ל-endpoint
- `201` - Status code של הצלחה
- `alert_sound.mp3` - בקשות ל-alert sound (מעיד שהתהליך עובד!)
- `python-requests` - User Agent של הטסטים שלנו

### Focus Server:
- `push-to-rabbit` - כשמקבל alert דרך API
- `POST.*push-to-rabbit` - HTTP requests ל-alert endpoint
- `alert.*received` - כשמקבל alert
- `alert.*published` - כש-alert נשלח ל-RabbitMQ
- `prisma-210-1000/api/push-to-rabbit` - endpoint

### gRPC Job (Baby Analyzer):
- `alert.*detected` - כש-alert מזוהה
- `alert.*published` - כש-alert נשלח ל-RabbitMQ
- `Algorithm.AlertReport` - כשמפרסם alert report
- `MLGroundAlertReport` - alerts של ground
- `PulseAlertReport` - alerts של pulse

### RabbitMQ:
- `exchange.*prisma` - פעילות ב-exchange
- `routing_key.*Algorithm.AlertReport` - routing של alerts
- `message.*published` - כש-message נשלח
- `message.*consumed` - כש-message נצרך

---

## 📝 דוגמאות שימוש

### דוגמה 1: בדיקת לוגים אחרי שליחת Alert

```python
import time
from src.infrastructure.kubernetes_manager import KubernetesManager
from config.config_manager import ConfigManager

# שליחת alert (קוד קודם)
alert_id = "test-sd-123"
# ... send alert ...

# המתנה לעיבוד
time.sleep(5)

# בדיקת לוגים
config_manager = ConfigManager()
k8s_manager = KubernetesManager(config_manager)

# מציאת Focus Server pod
pods = k8s_manager.get_pods(namespace="panda", label_selector="app.kubernetes.io/name=panda-panda-focus-server")
if pods:
    pod_name = pods[0]['metadata']['name']
    logs = k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=200)
    
    # חיפוש alert ID
    if alert_id in logs:
        print(f"✅ Alert {alert_id} found in logs!")
    else:
        print(f"❌ Alert {alert_id} not found in logs")
        
# בדיקת RabbitMQ pod
rabbitmq_pods = k8s_manager.get_pods(namespace="panda", label_selector="app.kubernetes.io/instance=rabbitmq-panda")
if rabbitmq_pods:
    rabbitmq_pod = rabbitmq_pods[0]['metadata']['name']
    rabbitmq_logs = k8s_manager.get_pod_logs(rabbitmq_pod, namespace="panda", tail_lines=200)
    if alert_id in rabbitmq_logs or "Algorithm.AlertReport" in rabbitmq_logs:
        print(f"✅ Alert found in RabbitMQ logs!")
```

### דוגמה 2: Monitoring בזמן אמת

```python
from src.utils.realtime_pod_monitor import PodLogMonitor
from config.config_manager import ConfigManager

# יצירת monitor
config_manager = ConfigManager()
monitor = PodLogMonitor(config_manager)

# התחלת monitoring של Focus Server
monitor.start_monitoring_service(
    service_name="focus-server",
    pod_selector="app.kubernetes.io/name=panda-panda-focus-server"
)

# המתנה ל-alerts
time.sleep(30)

# עצירת monitoring
monitor.stop_monitoring()

# קבלת לוגים
logs = monitor.get_logs("focus-server")
alert_logs = [line for line in logs if 'alert' in line.lower() or 'push-to-rabbit' in line.lower()]
print('\n'.join(alert_logs))
```

### דוגמה 3: בדיקת לוגים דרך kubectl command

```python
from src.infrastructure.ssh_manager import SSHManager
from config.config_manager import ConfigManager
import json

# יצירת SSH manager
config_manager = ConfigManager()
ssh_manager = SSHManager(config_manager)
ssh_manager.connect()

# מציאת Focus Server pod
command = "kubectl get pods -n panda -l app.kubernetes.io/name=panda-panda-focus-server -o jsonpath='{.items[0].metadata.name}'"
result = ssh_manager.execute_command(command)
pod_name = result['stdout'].strip()

# קבלת לוגים עם חיפוש alerts
command = f"kubectl logs -n panda {pod_name} --tail=500 | grep -i alert"
result = ssh_manager.execute_command(command)

print("Alert logs:")
print(result['stdout'])
```

---

## 🎯 סדר בדיקה מומלץ

### אחרי שליחת Alert:

0. **Ingress Controller** ⭐ - בדוק שהבקשה הגיעה והתקבלה (מומלץ להתחיל כאן!)
   ```bash
   kubectl logs -n kube-system ingress-nginx-controller-55694fd6ff-rqgp9 --tail=1000 | grep -i "push-to-rabbit"
   ```
   **מה לחפש:**
   - `POST /prisma/api/prisma-210-1000/api/push-to-rabbit` - הבקשה
   - `201` - Status code של הצלחה
   - `alert_sound.mp3` - בקשות ל-alert sound (מעיד שהתהליך עובד!)

1. **Focus Server** - בדוק שהתקבל דרך API
   ```bash
   kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=100 | grep "push-to-rabbit\|alert"
   ```
   **הערה:** הלוגים של `push-to-rabbit` לא תמיד מופיעים כאן - לבדוק ב-Ingress Controller!

2. **RabbitMQ** - בדוק שה-message נשלח
   ```bash
   kubectl logs -n panda rabbitmq-panda-0 --tail=100 | grep "Algorithm.AlertReport\|exchange.*prisma"
   ```

3. **gRPC Job** - בדוק שה-alert עובד (אם נשלח מה-BE)
   ```bash
   kubectl logs -n panda grpc-job-1-3-rm5ms --tail=100 | grep "alert\|Algorithm.AlertReport"
   ```

4. **MongoDB** - בדוק שנשמר (דרך application logs או ישירות)
   ```bash
   # דרך Focus Server logs
   kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=100 | grep "alert.*saved\|alert.*stored"
   ```

---

## 📊 דוגמאות לוגים

### Ingress Controller (המקום הראשי לבדיקת push-to-rabbit!): ⭐
```
10.42.0.0 - - [13/Nov/2025:12:08:41 +0000] "POST /prisma/api/prisma-210-1000/api/push-to-rabbit HTTP/1.1" 201 450 "-" "python-requests/2.32.5" 902 0.106 [webapp-webapp-pz-web-webapp-ui-80] [] 10.42.1.9:80 450 0.106 201 80e1da9a6d866cc1ede71922a8232394
```
**פירוש:**
- `POST /prisma/api/prisma-210-1000/api/push-to-rabbit` - הבקשה
- `201` - Status code (Created - הצלחה!)
- `450` - גודל התגובה (bytes)
- `python-requests/2.32.5` - User Agent (הטסטים שלנו)
- `[webapp-webapp-pz-web-webapp-ui-80]` - Backend service שמטפל בבקשה

**סימן שהתהליך עובד:**
אחרי `push-to-rabbit` request, רואים בקשות ל-`alert_sound.mp3`:
```
10.42.0.0 - - [13/Nov/2025:12:08:42 +0000] "GET /assets/sounds/alert_sound.mp3 HTTP/2.0" 206 25214 ...
```
זה אומר שה-Frontend קיבל את ה-alert ומנגן את צליל ההתראה! 🎉

### Focus Server (מקבל alert דרך API):
```
[INFO] POST /prisma-210-1000/api/push-to-rabbit
[INFO] Received alert: {"alertId": "test-sd-123", "classId": 104, "severity": 3}
[INFO] Publishing alert to RabbitMQ: test-sd-123
[INFO] Alert published successfully
```
**הערה:** הלוגים האלה לא תמיד מופיעים ב-Focus Server - לבדוק ב-Ingress Controller!

### gRPC Job / Baby Analyzer (מזהה alert):
```
[INFO] Alert detected: class_id=104, severity=3, distance_m=4163
[INFO] Publishing alert to RabbitMQ: Algorithm.AlertReport.MLGround
[INFO] Alert published successfully: test-sd-123
```

### RabbitMQ (מעביר alert):
```
[INFO] Message published to exchange 'prisma' with routing_key 'Algorithm.AlertReport.MLGround'
[INFO] Message consumed from queue 'prisma-210-1000-alerts'
```

---

## ✅ Checklist לבדיקה

- [ ] **Ingress Controller** ⭐ - בדקתי שהבקשה הגיעה והתקבלה (מומלץ להתחיל כאן!)
  - [ ] מצאתי את ה-pod: `ingress-nginx-controller-55694fd6ff-rqgp9`
  - [ ] בדקתי את הלוגים עם `--tail=1000`
  - [ ] חיפשתי `push-to-rabbit` בלוגים
  - [ ] אימתתי ש-status code הוא `201` (הצלחה!)
  - [ ] בדקתי שיש בקשות ל-`alert_sound.mp3` (מעיד שהתהליך עובד!)
- [ ] מצאתי את ה-pod הנכון (Focus Server / RabbitMQ / gRPC Job)
- [ ] בדקתי את הלוגים עם `--tail=100` או יותר
- [ ] חיפשתי את ה-alert ID בלוגים
- [ ] בדקתי שהתקבל ב-Focus Server דרך API (או ב-Ingress Controller)
- [ ] בדקתי שה-message נשלח ל-RabbitMQ
- [ ] בדקתי שה-message נצרך מ-RabbitMQ
- [ ] בדקתי שנשמר ב-MongoDB (אם רלוונטי)

---

**תאריך עדכון:** 13 בנובמבר 2025  
**גרסה:** 1.0.0

