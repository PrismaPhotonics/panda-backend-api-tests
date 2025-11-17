# סיכום עדכון קונפיגורציית האוטומציה - סביבת ייצור חדשה

**תאריך**: 19 אוקטובר 2025  
**סביבה**: Production (Panda Namespace)  
**מטרה**: הגדרת קונפיגורציית האוטומציה לחיבור לסביבה החדשה ולניטור לוגים

---

## 📋 מה עודכן?

### 1. **קובץ קונפיגורציה ראשי** ✅
**קובץ**: `config/environments.yaml`

**שינויים**:
- ✅ נוסף environment חדש: `new_production` (במקום `new_staging`)
- ✅ עודכן MongoDB: `10.10.100.108:27017` (LoadBalancer external IP)
  - Connection string: `mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma`
  - Internal service: `mongodb.panda:27017`
  - ClusterIP: `10.43.74.248`
- ✅ עודכן RabbitMQ: `10.10.100.107` (LoadBalancer external IP)
  - AMQP: `5672`
  - AMQP SSL: `5671`
  - Management UI: `15672`
  - Internal service: `rabbitmq-panda.panda`
  - ClusterIP: `10.43.10.166`
- ✅ עודכן Kubernetes:
  - API Server: `https://10.10.100.102:6443`
  - Dashboard: `https://10.10.100.102/`
  - Namespace: `panda`
  - Context: `panda-cluster`
- ✅ נוסף SSH gateway configuration:
  - Jump host: `10.10.100.3` (root)
  - Target host: `10.10.100.113` (prisma)
- ✅ נוסף K9s configuration:
  - פרטי כל השירותים ב-namespace `panda`
  - Pod selectors
  - ClusterIP ו-External IPs

---

### 2. **סקריפט הגדרת משתני סביבה** ✅
**קובץ**: `set_production_env.ps1`

**שינויים**:
- ✅ נוסף משתני K8s:
  ```powershell
  $env:K8S_API_SERVER = "https://10.10.100.102:6443"
  $env:K8S_NAMESPACE = "panda"
  $env:K8S_DASHBOARD = "https://10.10.100.102/"
  $env:K8S_CONTEXT = "panda-cluster"
  ```
- ✅ נוסף משתני SSH לגישה ל-K9s:
  ```powershell
  $env:SSH_JUMP_HOST = "10.10.100.3"
  $env:SSH_JUMP_USER = "root"
  $env:SSH_TARGET_HOST = "10.10.100.113"
  $env:SSH_TARGET_USER = "prisma"
  ```
- ✅ נוסף משתני Kubernetes Services:
  ```powershell
  $env:FOCUS_SERVER_K8S_SERVICE = "panda-panda-focus-server.panda"
  $env:MONGODB_K8S_SERVICE = "mongodb.panda"
  $env:RABBITMQ_K8S_SERVICE = "rabbitmq-panda.panda"
  ```
- ✅ עודכן output עם פרטי SSH

**שימוש**:
```powershell
. .\set_production_env.ps1
```

---

### 3. **סקריפט חיבור ל-K9s** 🆕
**קובץ**: `connect_k9s.ps1`

**תכונות**:
- 📋 הצגת הוראות חיבור מפורטות
- 🚀 פתיחת SSH ישירה
- ⚡ פקודות מהירות להעתקה
- 📚 K9s Quick Reference
- 📦 רשימת פודים חשובים
- 🔧 דוגמאות kubectl

**שימוש**:
```powershell
# הצג הוראות מפורטות
.\connect_k9s.ps1

# או
.\connect_k9s.ps1 -Mode instructions

# פקודות מהירות להעתקה
.\connect_k9s.ps1 -Mode quick

# פתח SSH (לא ממש עובד - השתמש ב-quick)
.\connect_k9s.ps1 -Mode connect
```

---

### 4. **מדריך ניטור לוגים** 🆕
**קובץ**: `MONITORING_LOGS_GUIDE.md`

**תכנים**:
1. **גישה לפודים**:
   - הוראות SSH מפורטות (2 hops)
   - דוגמאות פקודות
   
2. **צפייה בלוגים**:
   - לוגים של pod מסוים
   - לוגים של כל הפודים בשירות
   - שמירת לוגים לקובץ
   - לוגים בזמן אמת (`-f`)
   
3. **K9s**:
   - פקודות חשובות
   - תרחישים נפוצים
   - קיצורי מקלדת
   
4. **ניטור מרחוק דרך Automation**:
   - Python class: `K8sLogCollector`
   - Pytest fixtures לאיסוף לוגים אוטומטי
   - דוגמאות שימוש
   
5. **טיפים ושגרות עבודה**:
   - בדיקת בריאות יומית
   - ניטור בזמן ריצת טסטים
   - איתור בעיות נפוצות
   - cleanup של לוגים ישנים

---

## 🎯 איך להשתמש בקונפיגורציה החדשה?

### לפני ריצת טסטים:

#### 1. הגדר משתני סביבה
```powershell
cd C:\Projects\focus_server_automation
. .\set_production_env.ps1
```

**פלט צפוי**:
```
✅ Environment variables set for:
   Backend:        https://10.10.100.100/focus-server/
   MongoDB:        10.10.100.108:27017
   RabbitMQ:       10.10.100.107:5672 (AMQP)
   RabbitMQ UI:    10.10.100.107:15672
   Kubernetes:     https://10.10.100.102:6443
   K8s Namespace:  panda
   K8s Dashboard:  https://10.10.100.102/
   Database:       prisma

🔐 SSH Access for K9s/Logs:
   Jump Host:      10.10.100.3 (user: root)
   Target Host:    10.10.100.113 (user: prisma)
   Connect:        ssh root@10.10.100.3 → ssh prisma@10.10.100.113
```

#### 2. בדוק חיבור ל-MongoDB
```powershell
# Option 1: Python test
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma'); print('✅ Connected:', client.server_info()['version'])"

# Option 2: Mongosh (if installed)
mongosh "mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma" --eval "db.version()"
```

#### 3. בדוק חיבור ל-RabbitMQ
```powershell
# Browser - Management UI
Start-Process "http://10.10.100.107:15672"
# Username: prisma
# Password: prismapanda
```

#### 4. פתח K9s לניטור
```powershell
# הצג הוראות
.\connect_k9s.ps1 -Mode quick

# לאחר מכן, בטרמינל נפרד:
ssh root@10.10.100.3
ssh prisma@10.10.100.113
k9s -n panda
```

---

### בזמן ריצת טסטים:

#### Terminal 1: הרץ טסטים
```powershell
cd C:\Projects\focus_server_automation

# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# API tests
pytest focus_server_api_load_tests/focus_api_tests/ -v

# Load tests (Locust)
cd focus_server_api_load_tests\load_tests
locust -f locust_focus_server.py
```

#### Terminal 2 (SSH): צפה בלוגים בזמן אמת
```bash
# Connect via SSH
ssh root@10.10.100.3
ssh prisma@10.10.100.113

# Follow Focus Server logs
kubectl logs -n panda -f $(kubectl get pods -n panda -l app.kubernetes.io/name=panda-panda-focus-server -o name | head -1)

# Or use K9s
k9s -n panda
# Press: :pods
# Navigate to: panda-panda-focus-server-*
# Press: l (logs)
```

#### Terminal 3 (Optional): RabbitMQ Monitoring
```
Browser: http://10.10.100.107:15672
→ Queues tab
→ Monitor message rates during tests
```

---

## 📊 בדיקת בריאות לפני טסטים

### Checklist:
```powershell
# 1. בדוק שכל הפודים רצים
ssh root@10.10.100.3
ssh prisma@10.10.100.113
kubectl get pods -n panda
```

**פלט צפוי** (כל הפודים צריכים להיות `Running` ו-`1/1 Ready`):
```
NAME                                        READY   STATUS    RESTARTS   AGE
panda-panda-focus-server-988555979-nz9fr    1/1     Running   0          2h
mongodb-569cc5fbbb-526m9                    2/2     Running   0          4d
rabbitmq-panda-0                            1/1     Running   0          4d
panda-panda-player-d4f55f8c9-kbgds          1/1     Running   0          4d
panda-panda-segy-recorder-5d55cd467-nb4r7   1/1     Running   0          4d
grpc-job-1-4-2crtf                          1/1     Running   0          20m
```

```powershell
# 2. בדוק שאין errors בלוגים האחרונים
kubectl logs -n panda $(kubectl get pods -n panda -l app.kubernetes.io/name=panda-panda-focus-server -o name | head -1) --tail=50 | grep -i error

# 3. בדוק חיבור ל-MongoDB מהפוד
kubectl exec -n panda $(kubectl get pods -n panda -l app.kubernetes.io/name=panda-panda-focus-server -o name | sed 's/pod\///') -- curl -s http://mongodb.panda:27017 || echo "MongoDB accessible"

# 4. בדוק חיבור ל-RabbitMQ
kubectl exec -n panda rabbitmq-panda-0 -- rabbitmqctl status | grep -A 3 "Status"
```

---

## 🐛 Troubleshooting

### בעיה: טסט נכשל עם שגיאת חיבור ל-MongoDB

**פתרון**:
1. בדוק שמשתני הסביבה הוגדרו:
   ```powershell
   echo $env:MONGODB_URI
   # Expected: mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma
   ```

2. בדוק connectivity ישירות:
   ```powershell
   Test-NetConnection -ComputerName 10.10.100.108 -Port 27017
   ```

3. בדוק מתוך worker node:
   ```bash
   ssh root@10.10.100.3
   ssh prisma@10.10.100.113
   kubectl get pods -n panda | grep mongodb
   kubectl logs mongodb-569cc5fbbb-526m9 -n panda
   ```

---

### בעיה: לא מצליח להתחבר ל-K9s

**פתרון**:
1. וודא שאתה על ה-worker node הנכון:
   ```bash
   ssh root@10.10.100.3
   ssh prisma@10.10.100.113  # ← זה ה-node הנכון!
   ```

2. בדוק ש-kubectl מוגדר:
   ```bash
   kubectl version
   kubectl get nodes
   ```

3. בדוק ש-K9s מותקן:
   ```bash
   which k9s
   k9s version
   ```

4. אם K9s לא עובד, השתמש ב-kubectl:
   ```bash
   kubectl get pods -n panda
   kubectl logs <pod-name> -n panda -f
   ```

---

### בעיה: RabbitMQ Management UI לא נגיש

**פתרון**:
1. בדוק שה-port פתוח:
   ```powershell
   Test-NetConnection -ComputerName 10.10.100.107 -Port 15672
   ```

2. נסה להתחבר ישירות:
   ```powershell
   Start-Process "http://10.10.100.107:15672"
   ```

3. בדוק credentials:
   - Username: `prisma` או `user`
   - Password: `prismapanda`

4. בדוק מהפוד:
   ```bash
   kubectl exec -n panda rabbitmq-panda-0 -- rabbitmqctl status
   ```

---

## 📁 מבנה הקבצים שעודכנו

```
C:\Projects\focus_server_automation\
├── config\
│   ├── environments.yaml          ✅ עודכן - נוסף new_production environment
│   ├── NEW_PRODUCTION_ENV.yaml    ✅ קיים - מכיל MongoDB connection string
│   └── KUBERNETES_INFRASTRUCTURE.md ✅ קיים
├── set_production_env.ps1          ✅ עודכן - נוסף K8s ו-SSH vars
├── connect_k9s.ps1                 🆕 חדש - סקריפט חיבור ל-K9s
├── MONITORING_LOGS_GUIDE.md        🆕 חדש - מדריך מקיף לניטור
└── AUTOMATION_CONFIG_SUMMARY_HE.md 🆕 חדש - מסמך זה
```

---

## 📚 מסמכים נוספים לעיון

1. **`MONITORING_LOGS_GUIDE.md`** - מדריך מקיף לניטור לוגים (עברית)
2. **`config/NEW_PRODUCTION_ENV.yaml`** - קונפיגורציה מלאה של הסביבה
3. **`NEW_ENVIRONMENT_MASTER_DOCUMENT.md`** - מסמך master של כל הסביבה
4. **`COMPLETE_INFRASTRUCTURE_SUMMARY.md`** - סיכום תשתית מלא
5. **`K9S_CONNECTION_GUIDE.md`** - מדריך חיבור ל-K9s

---

## ✅ סיכום

### מה הושלם:
1. ✅ עודכן `environments.yaml` עם כל פרטי ה-K8s, MongoDB, RabbitMQ
2. ✅ עודכן `set_production_env.ps1` עם משתני סביבה חדשים
3. ✅ נוצר `connect_k9s.ps1` לגישה מהירה ל-K9s
4. ✅ נוצר `MONITORING_LOGS_GUIDE.md` - מדריך מקיף לניטור
5. ✅ עודכן Memory עם נתוני MongoDB ו-SSH

### מה צריך לעשות עכשיו:
1. 🎯 הרץ `.\set_production_env.ps1` לפני כל ריצת טסטים
2. 🎯 בדוק חיבור ל-MongoDB ו-RabbitMQ לפני טסטים
3. 🎯 פתח K9s בטרמינל נפרד לניטור בזמן אמת
4. 🎯 הרץ טסטים ועקוב אחרי הלוגים

### הטסטים מוכנים לרוץ על:
- ✅ Backend: `https://10.10.100.100/focus-server/`
- ✅ MongoDB: `mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma`
- ✅ RabbitMQ: `10.10.100.107:5672`
- ✅ K8s Namespace: `panda`
- ✅ K9s Access: `ssh root@10.10.100.3 → ssh prisma@10.10.100.113 → k9s`

---

**זמן עדכון**: ~5 דקות  
**נוצר**: 2025-10-19  
**גרסה**: 1.0  
**סטטוס**: ✅ מוכן לשימוש

