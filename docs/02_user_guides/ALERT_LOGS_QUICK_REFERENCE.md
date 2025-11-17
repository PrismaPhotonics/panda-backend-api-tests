# 🔍 Quick Reference - Alert Logs Location

**תאריך:** 13 בנובמבר 2025

---

## 📍 איפה לראות לוגים של Alerts

### 1. Focus Server Pod
**Pod Name:** `panda-panda-focus-server-78dbcfd9d9-4ld4s`

**פקודות:**
```bash
# כל הלוגים
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=500

# חיפוש alerts
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=500 | grep -i "push-to-rabbit\|alert"

# Follow בזמן אמת
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -f
```

**מה לחפש:**
- `POST /prisma-210-1000/api/push-to-rabbit`
- `push-to-rabbit`
- `alert`

---

### 2. RabbitMQ Pod
**Pod Name:** `rabbitmq-panda-0`

**פקודות:**
```bash
# כל הלוגים
kubectl logs -n panda rabbitmq-panda-0 --tail=500

# חיפוש alerts
kubectl logs -n panda rabbitmq-panda-0 --tail=500 | grep -i "publish\|exchange\|prisma"

# Follow בזמן אמת
kubectl logs -n panda rabbitmq-panda-0 -f

# בדיקת queues/exchanges
kubectl exec -n panda rabbitmq-panda-0 -- rabbitmqctl list_queues
kubectl exec -n panda rabbitmq-panda-0 -- rabbitmqctl list_exchanges
```

**מה לחפש:**
- `publish`
- `exchange.*prisma`
- `routing_key.*Algorithm.AlertReport`

---

### 3. RabbitMQ Management UI
**URL:** `http://10.10.10.100:15672`

**מה לבדוק:**
- Exchanges → `prisma`
- Queues → חפש queues עם `prisma-210-1000` או `alert`
- Messages → בדוק אם יש messages

---

## 🧪 הרצת בדיקת חקירה

```bash
# הרצת בדיקת חקירה (מפורט)
pytest be_focus_server_tests/integration/alerts/test_alert_logs_investigation.py -v -s

# או דרך Python script
python scripts/investigate_alert_logs.py
```

---

## 📊 תהליך מומלץ לטסטים

### לפני הבדיקה:
```bash
# Terminal 1: Follow Focus Server
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -f | grep -i "push-to-rabbit"

# Terminal 2: Follow RabbitMQ
kubectl logs -n panda rabbitmq-panda-0 -f | grep -i "publish\|exchange"
```

### בזמן הבדיקה:
- שלח alert דרך API
- צפה בלוגים ב-Terminal 1 ו-2

### אחרי הבדיקה:
- בדוק RabbitMQ Management UI
- בדוק MongoDB (אם רלוונטי)

---

**גרסה:** 1.0.0

