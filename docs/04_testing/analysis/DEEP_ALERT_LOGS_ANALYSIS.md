# 🔍 ניתוח מעמיק: לוגי Alerts - תוצאות החקירה

**תאריך:** 13 בנובמבר 2025  
**בדיקה:** `test_alert_logs_investigation.py`  
**תוצאה:** ✅ PASSED  
**זמן ביצוע:** ~62 שניות

---

## 📊 סיכום התוצאות

### ✅ מה עבד:

1. **שליחת Alert דרך API** - הצליחה ✅
   - Alert ID: `investigation-test-1763035405`
   - Response: 200 OK
   - Response Body: התקבל alert object עם כל הפרטים

2. **RabbitMQ Exchange** - נמצא ✅
   - Exchange `prisma` קיים
   - Type: `topic`
   - פעילות: נמצאו 291 שורות לוגים עם המילה "prisma"

3. **RabbitMQ Queues** - נמצאו ✅
   - נמצאו 17 queues של grpc-job
   - כל queue מכיל 1 message
   - Queue `focus_metadata`: 0 messages
   - Queue `smart_recorder`: 0 messages

4. **RabbitMQ Authentication** - פעיל ✅
   - נמצאו 5 שורות לוגים של authentication בזמן השליחה
   - User 'prisma' authenticated successfully

### ⚠️ מה לא נמצא:

1. **Focus Server Logs** - Alert לא נמצא ❌
   - חיפשו: `push-to-rabbit`, `alert`, `investigation-test-1763035405`
   - לא נמצאו שורות רלוונטיות
   - נמצאו: `rabbit` (52 שורות), `queue` (48 שורות), `POST` (23 שורות)
   - אבל לא נמצאו שורות ספציפיות ל-alert

2. **RabbitMQ Logs** - לא נמצאו מילות מפתח ספציפיות ⚠️
   - חיפשו: `publish`, `consume`, `exchange`, `routing`, `Algorithm.AlertReport`
   - לא נמצאו שורות רלוונטיות
   - נמצאו רק: `prisma` (291 שורות - authentication)

---

## 🔍 ניתוח מעמיק

### 1. למה Alert לא נמצא ב-Focus Server Logs?

**השערות:**

1. **הלוגים לא מפורטים מספיק**
   - Focus Server אולי לא מלוג את כל ה-HTTP requests
   - או שהלוגים נמצאים ב-level אחר (DEBUG במקום INFO)

2. **הלוגים נמצאים ב-Pod אחר**
   - אולי יש Pod נפרד ל-Prisma Web App API
   - או שהלוגים נמצאים ב-container אחר

3. **הלוגים נמחקו/רוטייטו**
   - הלוגים האחרונים הם מ-12:03 (לפני הבדיקה)
   - אולי הלוגים החדשים עדיין לא הגיעו

**המלצות:**

```bash
# בדיקה עם יותר שורות
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=1000 | grep -i "push-to-rabbit"

# בדיקה בזמן אמת
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -f | grep -i "push-to-rabbit"

# בדיקה של כל ה-containers
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --all-containers=true --tail=500
```

### 2. למה RabbitMQ לא מראה publish/consume?

**השערות:**

1. **RabbitMQ logs הם low-level**
   - RabbitMQ לא מלוג כל publish/consume ב-default
   - צריך להפעיל tracing mode

2. **הלוגים נמצאים ב-Management UI**
   - RabbitMQ Management UI מראה את המידע
   - אבל לא בלוגים של ה-pod

**המלצות:**

```bash
# בדיקה דרך Management UI
# URL: http://10.10.10.100:15672
# Exchanges → prisma → Check message stats

# הפעלת tracing (אם צריך)
kubectl exec -n panda rabbitmq-panda-0 -- rabbitmqctl trace_on

# בדיקת bindings
kubectl exec -n panda rabbitmq-panda-0 -- rabbitmqctl list_bindings
```

### 3. מה קורה עם ה-Alert אחרי השליחה?

**תהליך צפוי:**

1. ✅ **API Request** → Prisma Web App API (`/prisma-210-1000/api/push-to-rabbit`)
2. ✅ **Authentication** → RabbitMQ (נמצא בלוגים)
3. ❓ **Publish to RabbitMQ** → Exchange `prisma`, Routing Key `Algorithm.AlertReport.MLGround`
4. ❓ **Consume from RabbitMQ** → gRPC Job או Focus Server
5. ❓ **Process Alert** → שמירה ב-MongoDB או עיבוד

**מה צריך לבדוק:**

- ✅ RabbitMQ Exchange - נמצא
- ❓ RabbitMQ Queues - צריך לבדוק איזה queue קיבל את ה-message
- ❓ gRPC Job Logs - צריך לבדוק אם הם מעבדים את ה-alert
- ❓ MongoDB - צריך לבדוק אם ה-alert נשמר

---

## 🎯 המלצות לחקירה נוספת

### 1. בדיקת gRPC Job Logs

```bash
# בדיקה של gRPC Job pods
for pod in $(kubectl get pods -n panda -l app=grpc-job -o name); do
  echo "=== $pod ==="
  kubectl logs -n panda $pod --tail=100 | grep -i "alert\|Algorithm.AlertReport"
done
```

### 2. בדיקת MongoDB

```python
from src.infrastructure.mongodb_manager import MongoDBManager

mongodb_manager = MongoDBManager(config_manager)
mongodb_manager.connect()
db = mongodb_manager.get_database("prisma")
alerts_collection = db.get_collection("alerts")

# חיפוש alert
alert = alerts_collection.find_one({"ext_id": "investigation-test-1763035405"})
print(alert)
```

### 3. בדיקת RabbitMQ Management API

```python
import requests

rabbitmq_host = "10.10.10.150"
auth = ("user", "password")

# בדיקת exchanges
response = requests.get(f"http://{rabbitmq_host}:15672/api/exchanges", auth=auth)
exchanges = response.json()
prisma_exchange = [e for e in exchanges if e['name'] == 'prisma'][0]
print(f"Messages published: {prisma_exchange.get('message_stats', {}).get('publish', 0)}")

# בדיקת queues
response = requests.get(f"http://{rabbitmq_host}:15672/api/queues", auth=auth)
queues = response.json()
for queue in queues:
    if queue.get('messages', 0) > 0:
        print(f"{queue['name']}: {queue['messages']} messages")
```

### 4. בדיקה בזמן אמת

```bash
# Terminal 1: Follow Focus Server
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -f

# Terminal 2: Follow RabbitMQ
kubectl logs -n panda rabbitmq-panda-0 -f

# Terminal 3: Send alert
# (run test or use curl)

# Terminal 4: Follow gRPC Job
kubectl logs -n panda grpc-job-1-3-rm5ms -f
```

---

## 📋 מסקנות

### מה אנחנו יודעים:

1. ✅ Alert נשלח בהצלחה דרך API
2. ✅ RabbitMQ Exchange `prisma` קיים ופעיל
3. ✅ RabbitMQ Authentication עובד
4. ✅ יש 17 queues של grpc-job עם messages

### מה אנחנו לא יודעים:

1. ❓ איפה הלוגים של `push-to-rabbit` endpoint?
2. ❓ איזה queue קיבל את ה-alert message?
3. ❓ האם ה-alert נשמר ב-MongoDB?
4. ❓ האם gRPC Jobs מעבדים את ה-alert?

### מה צריך לעשות:

1. **להריץ את הבדיקה המעמיקה החדשה** (`test_deep_alert_logs_investigation.py`)
   - בודקת MongoDB
   - בודקת RabbitMQ Management API
   - בודקת gRPC Job logs
   - בודקת את כל הרכיבים אחרי שליחת alert

2. **לבדוק בזמן אמת**
   - Follow logs בזמן שליחת alert
   - לבדוק את RabbitMQ Management UI
   - לבדוק את MongoDB ישירות

3. **לבדוק את הקוד**
   - איפה ה-`push-to-rabbit` endpoint מלוג?
   - איזה level של logging הוא משתמש?
   - האם יש Pod נפרד ל-Prisma Web App API?

---

## 🔧 שיפורים לבדיקה

### בדיקה מעמיקה חדשה (`test_deep_alert_logs_investigation.py`):

1. ✅ בודקת MongoDB ישירות
2. ✅ בודקת RabbitMQ Management API
3. ✅ בודקת gRPC Job logs (sample)
4. ✅ מחפשת את ה-alert בכל הרכיבים
5. ✅ יוצרת דוח מפורט

### שיפורים נוספים אפשריים:

1. **בדיקת Prisma Web App API logs** (אם Pod נפרד)
2. **בדיקת RabbitMQ bindings** (איזה queue קשור ל-exchange)
3. **בדיקת RabbitMQ message tracing** (אם מופעל)
4. **בדיקת כל ה-gRPC Job pods** (לא רק sample)
5. **בדיקת Focus Server logs עם יותר שורות** (1000+)

---

**תאריך ניתוח:** 13 בנובמבר 2025  
**גרסה:** 1.0.0

