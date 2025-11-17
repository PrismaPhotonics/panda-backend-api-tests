# 🔍 ניתוח: למה לא רואים לוגים של push-to-rabbit?

**תאריך:** 13 בנובמבר 2025  
**בעיה:** לוגים של `push-to-rabbit` endpoint לא מופיעים ב-Focus Server Pod

---

## 📊 ממצאים מהחקירה

### ✅ מה עובד:

1. **Alert נשלח בהצלחה** ✅
   - Response: 201 Created
   - Alert ID: `deep-investigation-1763035715`
   - Response body מלא עם כל הפרטים

2. **RabbitMQ פעיל** ✅
   - Exchange `prisma` קיים
   - נמצאה פעילות בלוגים (authentication)

3. **Infrastructure תקין** ✅
   - Focus Server Pod: Running
   - RabbitMQ Pod: Running
   - MongoDB: Connected

### ❌ מה לא נמצא:

1. **Focus Server Logs** ❌
   - Alert לא נמצא בלוגים
   - לא נמצאו שורות עם `push-to-rabbit`
   - לא נמצאו POST requests ל-`/prisma-210-1000/api/push-to-rabbit`

2. **MongoDB** ❌
   - Alert לא נשמר ב-MongoDB
   - זה אומר שה-alert לא עבר את כל התהליך

3. **gRPC Jobs** ❌
   - לא נמצאה פעילות של alerts

---

## 🔍 ניתוח הארכיטקטורה

### מה מצאנו:

1. **Ingress Configuration:**
   ```
   Ingress: panda-panda-focus-server
   Host: *
   Path: /focus-server(/|$)(.*) -> Service: panda-panda-focus-server
   ```

2. **Focus Server Service:**
   ```
   Service: panda-panda-focus-server
   Type: ClusterIP
   Port: 5000 -> http
   ```

3. **אין Pod נפרד** ל-Prisma Web App API

### השערות:

#### השערה 1: ה-endpoint מטופל ב-Focus Server אבל לא מלוג
- ה-endpoint `/prisma-210-1000/api/push-to-rabbit` מטופל ב-Focus Server
- אבל הלוגים נמצאים ב-level אחר (DEBUG במקום INFO)
- או שהלוגים לא מופעלים עבור endpoint זה

#### השערה 2: ה-endpoint מטופל דרך Ingress אחר
- יש Ingress נוסף שלא נמצא בבדיקה
- או שה-endpoint מטופל דרך Load Balancer ישירות
- או שיש Service Mesh שמטפל ב-routing

#### השערה 3: ה-endpoint מטופל ב-container אחר
- Focus Server Pod מכיל מספר containers
- ה-endpoint מטופל ב-container אחר (לא ה-main container)
- הלוגים נמצאים ב-container הנפרד

---

## 🎯 המלצות לחקירה נוספת

### 1. בדיקת כל ה-containers ב-Focus Server Pod

```bash
# רשימת כל ה-containers
kubectl get pod panda-panda-focus-server-78dbcfd9d9-4ld4s -n panda -o jsonpath='{.spec.containers[*].name}'

# בדיקת לוגים מכל container
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --all-containers=true --tail=1000 | grep -i "push-to-rabbit"
```

### 2. בדיקת Ingress Controller Logs

```bash
# מציאת Ingress Controller Pod
kubectl get pods -n kube-system | grep ingress

# בדיקת לוגים
kubectl logs -n kube-system <ingress-controller-pod> --tail=1000 | grep -i "prisma-210-1000\|push-to-rabbit"
```

### 3. בדיקה בזמן אמת

```bash
# Terminal 1: Follow Focus Server logs
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -f --all-containers=true

# Terminal 2: Send alert
# (run test or use curl)

# Terminal 3: Follow Ingress Controller logs
kubectl logs -n kube-system <ingress-controller-pod> -f
```

### 4. בדיקת Application Logs ישירות

```bash
# התחברות ל-Pod
kubectl exec -it -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -- /bin/bash

# חיפוש קבצי לוגים
find /var/log -name "*.log" -type f 2>/dev/null
find /app -name "*.log" -type f 2>/dev/null

# בדיקת application logs
tail -f /var/log/app.log | grep -i "push-to-rabbit"
```

### 5. בדיקת Response Headers

```python
import requests

session = requests.Session()
session.verify = False

# Login
login_resp = session.post(
    "https://10.10.10.100/prisma/api/auth/login",
    json={"username": "prisma", "password": "prisma"}
)

# Send alert
alert_resp = session.post(
    "https://10.10.10.100/prisma/api/prisma-210-1000/api/push-to-rabbit",
    json={
        "alertsAmount": 1,
        "dofM": 4163,
        "classId": 104,
        "severity": 3,
        "alertIds": ["test-123"]
    }
)

# Check response headers
print("Response Headers:")
for key, value in alert_resp.headers.items():
    print(f"  {key}: {value}")

# Check if there's a server header that indicates which service handled it
print(f"\nServer: {alert_resp.headers.get('Server', 'N/A')}")
print(f"X-Powered-By: {alert_resp.headers.get('X-Powered-By', 'N/A')}")
```

---

## 💡 מסקנות

### מה אנחנו יודעים:

1. ✅ Alert נשלח בהצלחה דרך API
2. ✅ Response: 201 Created עם alert object מלא
3. ✅ RabbitMQ Exchange `prisma` קיים ופעיל
4. ❌ לוגים לא מופיעים ב-Focus Server Pod

### מה אנחנו לא יודעים:

1. ❓ איפה הלוגים של `push-to-rabbit` endpoint?
2. ❓ האם ה-endpoint מטופל ב-Focus Server או ב-service אחר?
3. ❓ למה ה-alert לא נשמר ב-MongoDB?
4. ❓ האם יש Ingress נוסף שמטפל ב-`/prisma/api`?

### מה צריך לעשות:

1. **לבדוק את כל ה-containers** ב-Focus Server Pod
2. **לבדוק את Ingress Controller logs**
3. **לבדוק בזמן אמת** - Follow logs בזמן שליחת alert
4. **לבדוק את Response Headers** - לראות איזה server מטפל ב-request
5. **לבדוק את Application Logs** ישירות ב-Pod

---

## 🔧 פתרונות אפשריים

### פתרון 1: הפעלת DEBUG Logging

אם הלוגים נמצאים ב-DEBUG level:

```python
# בדיקת configuration של Focus Server
# אולי צריך להפעיל DEBUG logging עבור endpoint זה
```

### פתרון 2: בדיקת Application Logs ישירות

```bash
# התחברות ל-Pod ובדיקת application logs
kubectl exec -it -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -- tail -f /var/log/app.log
```

### פתרון 3: בדיקת Ingress Controller

```bash
# בדיקת Ingress Controller logs
kubectl logs -n kube-system <ingress-controller-pod> --tail=1000 | grep -i "prisma"
```

---

**תאריך ניתוח:** 13 בנובמבר 2025  
**גרסה:** 1.0.0

