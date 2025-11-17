# 🔍 מדריך חקירה מלא - לוגי Alerts ב-Kubernetes

**תאריך:** 13 בנובמבר 2025  
**מטרה:** חקירה מקיפה של איפה ואיך לראות לוגים של alerts בטסטים אוטומטיים

---

## 🎯 מטרת החקירה

למצוא:
1. איפה ה-alerts מטופלים (איזה pods)
2. איך לראות את הלוגים בזמן אמת
3. איך לזהות alerts בלוגים
4. איך לבדוק שהתהליך עובד

---

## 📋 שלב 1: רשימת Pods

### פקודה:
```bash
kubectl get pods -n panda
```

### מה לחפש:
- `panda-panda-focus-server-*` - מטפל ב-API
- `rabbitmq-panda-0` - RabbitMQ
- `grpc-job-*` - Baby Analyzer
- `mongodb-*` - MongoDB

---

## 📋 שלב 2: בדיקת Focus Server Logs

### פקודה בסיסית:
```bash
# כל הלוגים האחרונים
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=500

# חיפוש מילות מפתח
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=500 | grep -i "push-to-rabbit\|alert\|api\|post"
```

### מה לחפש:
- `POST /prisma-210-1000/api/push-to-rabbit` - בקשות API
- `push-to-rabbit` - endpoint של alerts
- `alert` - כל מה שקשור ל-alerts
- `rabbit` - חיבור ל-RabbitMQ

### Follow בזמן אמת:
```bash
# Terminal 1: Follow logs
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -f

# Terminal 2: שלח alert דרך API
# ואז תראה את הלוגים ב-Terminal 1
```

---

## 📋 שלב 3: בדיקת RabbitMQ Logs

### פקודה בסיסית:
```bash
# כל הלוגים האחרונים
kubectl logs -n panda rabbitmq-panda-0 --tail=500

# חיפוש מילות מפתח
kubectl logs -n panda rabbitmq-panda-0 --tail=500 | grep -i "publish\|consume\|exchange\|routing\|prisma"
```

### מה לחפש:
- `publish` - כשמפרסמים message
- `consume` - כשצורכים message
- `exchange.*prisma` - פעילות ב-exchange
- `routing_key` - routing של messages

### בדיקת Queues/Exchanges:
```bash
# רשימת exchanges
kubectl exec -n panda rabbitmq-panda-0 -- rabbitmqctl list_exchanges name type

# רשימת queues
kubectl exec -n panda rabbitmq-panda-0 -- rabbitmqctl list_queues name messages

# רשימת bindings
kubectl exec -n panda rabbitmq-panda-0 -- rabbitmqctl list_bindings exchange_name routing_key queue_name
```

---

## 📋 שלב 4: שליחת Test Alert

### דרך 1: דרך Python Script

```python
import requests
import time

# 1. Authentication
BASE_URL = "https://10.10.10.100/prisma/api/"
session = requests.Session()
session.verify = False

login_resp = session.post(
    f"{BASE_URL}auth/login",
    json={"username": "prisma", "password": "prisma"}
)
login_resp.raise_for_status()

# 2. Send Alert
alert_id = f"test-investigation-{int(time.time())}"
alert_payload = {
    "alertsAmount": 1,
    "dofM": 4163,
    "classId": 104,
    "severity": 3,
    "alertIds": [alert_id]
}

alert_resp = session.post(
    f"{BASE_URL}prisma-210-1000/api/push-to-rabbit",
    json=alert_payload
)
print(f"Alert sent: {alert_id}")
print(f"Response: {alert_resp.text}")
```

### דרך 2: דרך curl

```bash
# 1. Login
curl -k -X POST https://10.10.10.100/prisma/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "prisma", "password": "prisma"}' \
  -c cookies.txt

# 2. Send Alert
curl -k -X POST https://10.10.10.100/prisma/api/prisma-210-1000/api/push-to-rabbit \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "alertsAmount": 1,
    "dofM": 4163,
    "classId": 104,
    "severity": 3,
    "alertIds": ["test-investigation-123"]
  }'
```

---

## 📋 שלב 5: Monitoring בזמן אמת

### תהליך מומלץ:

**Terminal 1 - Focus Server:**
```bash
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -f | grep -i "push-to-rabbit\|alert"
```

**Terminal 2 - RabbitMQ:**
```bash
kubectl logs -n panda rabbitmq-panda-0 -f | grep -i "publish\|exchange\|prisma"
```

**Terminal 3 - Send Alert:**
```bash
# שלח alert דרך API (Python או curl)
```

**תוצאה:** תראה את הלוגים ב-Terminal 1 ו-2 בזמן אמת!

---

## 📋 שלב 6: בדיקת RabbitMQ Management UI

### גישה:
```bash
# פתח בדפדפן:
http://10.10.10.100:15672
# או
http://10.10.10.150:15672

# Credentials:
# Username: prisma (או user)
# Password: prisma (או password מה-config)
```

### מה לבדוק:

1. **Exchanges:**
   - חפש `prisma` exchange
   - בדוק את ה-type (צריך להיות `topic`)
   - בדוק את ה-durable (צריך להיות `true`)

2. **Queues:**
   - חפש queues עם `prisma-210-1000` או `alert`
   - בדוק את מספר ה-messages
   - בדוק את ה-consumers

3. **Bindings:**
   - בדוק bindings בין `prisma` exchange ל-queues
   - בדוק את ה-routing keys

4. **Messages:**
   - בדוק אם יש messages ב-queues
   - בדוק את ה-message content
   - בדוק את ה-timestamps

---

## 📋 שלב 7: בדיקת MongoDB

### דרך kubectl exec:
```bash
# התחבר ל-MongoDB pod
kubectl exec -it -n panda mongodb-7cb5d67cc5-wb7qz -- mongosh mongodb://prisma:prisma@localhost:27017/prisma

# חפש alerts
db.alerts.find({"alert_id": "test-investigation-123"})

# כל ה-alerts האחרונים
db.alerts.find().sort({created_at: -1}).limit(10)
```

### דרך MongoDB Compass או client אחר:
```
Connection String: mongodb://prisma:prisma@10.10.10.100:27017/prisma
Database: prisma
Collection: alerts
```

---

## 🔍 מילות מפתח ספציפיות

### Focus Server:
- `POST /prisma-210-1000/api/push-to-rabbit` - בקשה ל-alert endpoint
- `push-to-rabbit` - כל מה שקשור ל-endpoint
- `alert.*received` - כשמקבל alert
- `alert.*published` - כש-alert נשלח ל-RabbitMQ
- `rabbitmq` - חיבור ל-RabbitMQ

### RabbitMQ:
- `exchange.*prisma` - פעילות ב-exchange
- `routing_key.*Algorithm.AlertReport` - routing של alerts
- `message.*published` - כש-message נשלח
- `message.*consumed` - כש-message נצרך
- `queue.*prisma-210-1000` - queue של site

### gRPC Job (Baby Analyzer):
- `alert.*detected` - כש-alert מזוהה
- `Algorithm.AlertReport` - כשמפרסם alert report
- `MLGroundAlertReport` - alerts של ground
- `PulseAlertReport` - alerts של pulse

---

## 📊 דוגמאות לוגים צפויות

### Focus Server (מקבל alert):
```
[INFO] POST /prisma-210-1000/api/push-to-rabbit
[INFO] Received alert payload: {"alertsAmount": 1, "dofM": 4163, "classId": 104, "severity": 3, "alertIds": ["test-123"]}
[INFO] Publishing alert to RabbitMQ exchange 'prisma'
[INFO] Alert published successfully: test-123
```

### RabbitMQ (מעביר alert):
```
[INFO] Message published to exchange 'prisma' with routing_key 'Algorithm.AlertReport.MLGround'
[INFO] Message routed to queue 'prisma-210-1000-alerts'
[INFO] Message consumed from queue 'prisma-210-1000-alerts'
```

---

## ✅ Checklist לחקירה

- [ ] רשימתי את כל ה-pods
- [ ] בדקתי את Focus Server logs
- [ ] בדקתי את RabbitMQ logs
- [ ] בדקתי את RabbitMQ queues/exchanges
- [ ] שלחתי test alert
- [ ] בדקתי את הלוגים אחרי השליחה
- [ ] בדקתי את RabbitMQ Management UI
- [ ] בדקתי את MongoDB (אם רלוונטי)
- [ ] יצרתי תהליך monitoring בזמן אמת

---

## 🎯 מסקנות והמלצות

### איפה לראות לוגים:

1. **Focus Server Pod** - לוגים של API requests
   ```bash
   kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -f | grep -i "push-to-rabbit"
   ```

2. **RabbitMQ Pod** - לוגים של message publishing/consuming
   ```bash
   kubectl logs -n panda rabbitmq-panda-0 -f | grep -i "publish\|exchange"
   ```

3. **RabbitMQ Management UI** - ויזואליזציה של queues/exchanges
   ```
   http://10.10.10.100:15672
   ```

### תהליך מומלץ לטסטים:

1. **לפני הבדיקה:**
   - פתח 2 terminals עם `kubectl logs -f`
   - אחד ל-Focus Server, אחד ל-RabbitMQ

2. **בזמן הבדיקה:**
   - שלח alert דרך API
   - צפה בלוגים בזמן אמת

3. **אחרי הבדיקה:**
   - בדוק את RabbitMQ Management UI
   - בדוק את MongoDB (אם רלוונטי)

---

**תאריך עדכון:** 13 בנובמבר 2025  
**גרסה:** 1.0.0

