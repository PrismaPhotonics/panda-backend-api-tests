# 🔍 פתרון בעיות - חיפוש לוגי Alerts

**תאריך:** 13 בנובמבר 2025  
**מטרה:** פתרון בעיות כשהלוגים לא נמצאים

---

## ❌ בעיה: לא מוצאים לוגים

אם הפקודות הבאות לא מחזירות תוצאות:
```bash
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=100 | grep "push-to-rabbit\|alert"
kubectl logs -n panda rabbitmq-panda-0 --tail=100 | grep "Algorithm.AlertReport"
```

---

## 🔧 פתרונות

### 1. בדוק את הלוגים בלי grep

ראשית, בואו נראה מה יש בלוגים:

```bash
# Focus Server - כל הלוגים האחרונים
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=200

# RabbitMQ - כל הלוגים האחרונים
kubectl logs -n panda rabbitmq-panda-0 --tail=200

# gRPC Job - כל הלוגים האחרונים
kubectl logs -n panda grpc-job-1-3-rm5ms --tail=200
```

### 2. חפש מילות מפתח אחרות

אולי הלוגים משתמשים בפורמט אחר:

```bash
# Focus Server - חיפוש רחב יותר
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=500 | grep -i "rabbit\|queue\|message\|api\|post"

# RabbitMQ - חיפוש רחב יותר
kubectl logs -n panda rabbitmq-panda-0 --tail=500 | grep -i "publish\|consume\|exchange\|routing"

# gRPC Job - חיפוש רחב יותר
kubectl logs -n panda grpc-job-1-3-rm5ms --tail=500 | grep -i "report\|algorithm\|mlground"
```

### 3. בדוק אם יש pods אחרים

אולי ה-alerts מטופלים ב-pods אחרים:

```bash
# כל ה-pods
kubectl get pods -n panda

# חפש pods עם "alert" בשם
kubectl get pods -n panda | grep -i alert

# חפש pods עם "api" בשם
kubectl get pods -n panda | grep -i api

# חפש pods עם "web" בשם
kubectl get pods -n panda | grep -i web
```

### 4. בדוק את ה-API ישירות

בדוק אם ה-API endpoint קיים ועובד:

```bash
# בדוק את ה-API endpoint
curl -k -X POST https://10.10.10.100/prisma/api/prisma-210-1000/api/push-to-rabbit \
  -H "Content-Type: application/json" \
  -d '{"alertsAmount": 1, "dofM": 4163, "classId": 104, "severity": 3, "alertIds": ["test-debug-123"]}'
```

### 5. בדוק את RabbitMQ Management UI

בדוק את RabbitMQ Management UI לראות אם יש messages:

```bash
# פתח RabbitMQ Management UI
# http://10.10.10.100:15672 (או הכתובת שלך)

# בדוק את ה-exchange "prisma"
# בדוק את ה-queues
# בדוק את ה-bindings
```

### 6. בדוק את MongoDB ישירות

בדוק אם ה-alerts נשמרו ב-MongoDB:

```bash
# התחבר ל-MongoDB
mongosh mongodb://prisma:prisma@10.10.10.100:27017/prisma

# חפש alerts
db.alerts.find({"alert_id": "test-debug-123"})

# או חפש את כל ה-alerts האחרונים
db.alerts.find().sort({created_at: -1}).limit(10)
```

---

## 🎯 מילות מפתח חלופיות לחיפוש

### Focus Server:
- `POST` - כל ה-POST requests
- `api` - כל ה-API calls
- `rabbit` - כל מה שקשור ל-RabbitMQ
- `queue` - כל מה שקשור ל-queues
- `prisma-210-1000` - site ID
- `push` - כל מה שקשור ל-push

### RabbitMQ:
- `publish` - כל ה-publish operations
- `consume` - כל ה-consume operations
- `exchange` - כל מה שקשור ל-exchanges
- `routing` - כל מה שקשור ל-routing
- `prisma` - exchange name

### gRPC Job:
- `report` - כל ה-reports
- `algorithm` - כל מה שקשור ל-algorithms
- `mlground` - ML Ground alerts
- `pulse` - Pulse alerts
- `fibercut` - Fiber Cut alerts

---

## 📊 דוגמאות פקודות מפורטות

### בדיקת Focus Server - מפורט:

```bash
# כל הלוגים האחרונים
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=500

# חיפוש POST requests
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=500 | grep "POST"

# חיפוש API calls
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=500 | grep "/api/"

# חיפוש RabbitMQ
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=500 | grep -i "rabbit"
```

### בדיקת RabbitMQ - מפורט:

```bash
# כל הלוגים האחרונים
kubectl logs -n panda rabbitmq-panda-0 --tail=500

# חיפוש publish
kubectl logs -n panda rabbitmq-panda-0 --tail=500 | grep -i "publish"

# חיפוש exchange
kubectl logs -n panda rabbitmq-panda-0 --tail=500 | grep -i "exchange"

# חיפוש routing
kubectl logs -n panda rabbitmq-panda-0 --tail=500 | grep -i "routing"
```

### בדיקת gRPC Job - מפורט:

```bash
# כל הלוגים האחרונים
kubectl logs -n panda grpc-job-1-3-rm5ms --tail=500

# חיפוש report
kubectl logs -n panda grpc-job-1-3-rm5ms --tail=500 | grep -i "report"

# חיפוש algorithm
kubectl logs -n panda grpc-job-1-3-rm5ms --tail=500 | grep -i "algorithm"

# חיפוש alert
kubectl logs -n panda grpc-job-1-3-rm5ms --tail=500 | grep -i "alert"
```

---

## 🔍 בדיקת Pods אחרים

אולי ה-alerts מטופלים ב-pods אחרים:

```bash
# בדוק את כל ה-pods
kubectl get pods -n panda -o wide

# בדוק את ה-labels של כל pod
kubectl get pods -n panda --show-labels

# חפש pods עם label מסוים
kubectl get pods -n panda -l app.kubernetes.io/name=panda-panda-focus-server

# בדוק את ה-services
kubectl get svc -n panda
```

---

## 💡 טיפים

1. **השתמש ב-`--tail` גדול יותר** - אולי הלוגים ישנים יותר
   ```bash
   kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=1000
   ```

2. **השתמש ב-`--since`** - חפש לוגים מהזמן האחרון
   ```bash
   kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --since=1h
   ```

3. **השתמש ב-`-f`** - Follow בזמן אמת בזמן שאתה שולח alert
   ```bash
   kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -f
   ```

4. **שמור את הלוגים לקובץ** - כדי לבדוק אחר כך
   ```bash
   kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=1000 > focus-server-logs.txt
   ```

---

## ✅ Checklist לפתרון בעיות

- [ ] בדקתי את הלוגים בלי grep
- [ ] בדקתי מילות מפתח אחרות
- [ ] בדקתי pods אחרים
- [ ] בדקתי את ה-API ישירות
- [ ] בדקתי את RabbitMQ Management UI
- [ ] בדקתי את MongoDB ישירות
- [ ] השתמשתי ב-`--tail` גדול יותר
- [ ] השתמשתי ב-`--since` לזמן ספציפי
- [ ] השתמשתי ב-`-f` ל-follow בזמן אמת

---

**תאריך עדכון:** 13 בנובמבר 2025  
**גרסה:** 1.0.0

