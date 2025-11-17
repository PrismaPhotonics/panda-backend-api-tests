# 🔍 בדיקת Ingress Controller Logs

**תאריך:** 13 בנובמבר 2025  
**מטרה:** למצוא לוגים של `push-to-rabbit` endpoint ב-Ingress Controller

---

## 📋 פקודות לבדיקה

### 1. מציאת Ingress Controller Pod

```bash
kubectl get pods -n kube-system | grep ingress
```

**תוצאה:**
```
ingress-nginx-defaultbackend-75fb9c5bb9-f85nc   1/1     Running   0              25h
ingress-nginx-controller-55694fd6ff-rqgp9       1/1     Running   0              25h
```

**Pod רלוונטי:** `ingress-nginx-controller-55694fd6ff-rqgp9`

---

### 2. בדיקת לוגים של Ingress Controller

```bash
# כל הלוגים האחרונים
kubectl logs -n kube-system ingress-nginx-controller-55694fd6ff-rqgp9 --tail=1000

# חיפוש prisma
kubectl logs -n kube-system ingress-nginx-controller-55694fd6ff-rqgp9 --tail=1000 | grep -i "prisma"

# חיפוש push-to-rabbit
kubectl logs -n kube-system ingress-nginx-controller-55694fd6ff-rqgp9 --tail=1000 | grep -i "push-to-rabbit"

# Follow בזמן אמת (עם tail לראות את הלוגים האחרונים קודם)
kubectl logs -n kube-system ingress-nginx-controller-55694fd6ff-rqgp9 --tail=1000 -f | grep -i "prisma\|push-to-rabbit"
```

---

### 3. בדיקת לוגים בזמן אמת (מומלץ)

**Terminal 1:**
```bash
kubectl logs -n kube-system ingress-nginx-controller-55694fd6ff-rqgp9 --tail=1000 -f | grep -i "prisma\|push-to-rabbit\|POST"
```

**Terminal 2:**
```bash
# שלח alert דרך API
# או הרץ את הבדיקה
pytest be_focus_server_tests/integration/alerts/test_deep_alert_logs_investigation.py::TestDeepAlertLogsInvestigation::test_deep_investigate_alert_logs -v -s
```

---

### 4. בדיקת כל ה-requests ל-prisma

```bash
kubectl logs -n kube-system ingress-nginx-controller-55694fd6ff-rqgp9 --tail=5000 | grep -i "prisma-210-1000\|/prisma/api"
```

---

### 5. בדיקת POST requests

```bash
kubectl logs -n kube-system ingress-nginx-controller-55694fd6ff-rqgp9 --tail=1000 | grep -i "POST.*prisma"
```

---

## 🎯 מה לחפש בלוגים

### דוגמאות לוגים צפויות:

```
10.42.1.21 - - [13/Nov/2025:12:08:40 +0000] "POST /prisma/api/prisma-210-1000/api/push-to-rabbit HTTP/1.1" 201 1234 "-" "python-requests/2.31.0"
```

### מילות מפתח:

- `POST /prisma/api/prisma-210-1000/api/push-to-rabbit`
- `push-to-rabbit`
- `prisma-210-1000`
- `201` (status code)
- `prisma/api`

---

## 📊 ניתוח התוצאות

### ✅ אם נמצאו לוגים (כמו בדוגמה שלנו):

✅ ה-endpoint מטופל דרך Ingress Controller  
✅ הלוגים נמצאים ב-Ingress Controller Pod  
✅ אפשר לעקוב אחרי ה-requests בזמן אמת

**דוגמה לוגים שנמצאו:**
```
10.42.0.0 - - [13/Nov/2025:12:08:41 +0000] "POST /prisma/api/prisma-210-1000/api/push-to-rabbit HTTP/1.1" 201 450 "-" "python-requests/2.32.5" 902 0.106 [webapp-webapp-pz-web-webapp-ui-80] [] 10.42.1.9:80 450 0.106 201 80e1da9a6d866cc1ede71922a8232394
```

**פירוש הלוג:**
- `POST /prisma/api/prisma-210-1000/api/push-to-rabbit` - הבקשה
- `201` - Status code (Created - הצלחה!)
- `450` - גודל התגובה (bytes)
- `python-requests/2.32.5` - User Agent (הטסטים שלנו)
- `[webapp-webapp-pz-web-webapp-ui-80]` - Backend service שמטפל בבקשה
- `10.42.1.9:80` - כתובת ה-backend service

**סימנים שהתהליך עובד:**
- ✅ Status 201 = Alert נשלח בהצלחה
- ✅ Response size 450 bytes = תגובה תקינה
- ✅ Backend service `webapp-webapp-pz-web-webapp-ui-80` = ה-endpoint מטופל

**סימן נוסף שהתהליך עובד:**
אחרי `push-to-rabbit` request, רואים בקשות ל-`alert_sound.mp3`:
```
10.42.0.0 - - [13/Nov/2025:12:08:42 +0000] "GET /assets/sounds/alert_sound.mp3 HTTP/2.0" 206 25214 ...
```
זה אומר שה-Frontend קיבל את ה-alert ומנגן את צליל ההתראה! 🎉

### אם לא נמצאו לוגים:

❓ ה-endpoint לא עובר דרך Ingress Controller  
❓ ה-endpoint מטופל ישירות ב-Focus Server  
❓ יש routing אחר (Load Balancer, Service Mesh)

---

## 🔧 פתרונות נוספים

### אם לא נמצאו לוגים ב-Ingress:

1. **בדוק את Focus Server Pod ישירות:**
   ```bash
   kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --all-containers=true --tail=1000 | grep -i "push-to-rabbit"
   ```

2. **בדוק את כל ה-containers:**
   ```bash
   kubectl get pod panda-panda-focus-server-78dbcfd9d9-4ld4s -n panda -o jsonpath='{.spec.containers[*].name}'
   ```

3. **בדוק בזמן אמת:**
   ```bash
   kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -f --all-containers=true
   ```

---

**תאריך:** 13 בנובמבר 2025  
**גרסה:** 1.0.0

