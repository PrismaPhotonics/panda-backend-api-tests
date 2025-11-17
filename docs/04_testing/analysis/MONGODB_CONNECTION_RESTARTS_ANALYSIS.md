# 🔍 ניתוח Restarts - בעיית חיבור ל-MongoDB

**תאריך:** 2025-11-08 13:25  
**Pod:** `panda-panda-focus-server-78dbcfd9d9-kjj77`  
**Restarts:** 4 ב-28 שעות

---

## 📋 סיכום הבעיה

ה-pod נכשל ב-startup בגלל בעיית חיבור ל-MongoDB. השגיאה הייתה:
```
pymongo.errors.ServerSelectionTimeoutError: mongodb:27017: [Errno -3] Temporary failure in name resolution
```

---

## 🔍 ניתוח השגיאה

### השגיאה המלאה:

```
pymongo.errors.ServerSelectionTimeoutError: mongodb:27017: [Errno -3] Temporary failure in name resolution 
(configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), 
Timeout: 30s, Topology Description: <TopologyDescription id: 690dacafa411911c09db4a57, 
topology_type: Unknown, servers: [<ServerDescription ('mongodb', 27017) server_type: Unknown, 
rtt: None, error=AutoReconnect('mongodb:27017: [Errno -3] Temporary failure in name resolution 
(configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
```

### מה קרה:

1. **ה-pod התחיל לרוץ**
   - Kubernetes start את ה-pod
   - ה-pod ניסה לרוץ את `focus_server`

2. **FocusManager ניסה להתחיל**
   - `FocusManager.__init__()` נקרא
   - הוא ניסה ליצור `RecordingMongoMapper(self.storage_path)`
   - זה ניסה להתחבר ל-MongoDB דרך `mongodb:27017`

3. **בעיית DNS/Networking**
   - ה-pod לא יכול לפתור את השם `mongodb` ל-IP address
   - `[Errno -3] Temporary failure in name resolution`
   - זה אומר שה-DNS של Kubernetes לא יכול לפתור את השם

4. **ה-pod נכשל**
   - ה-pod נכשל ב-startup
   - Kubernetes restart את ה-pod
   - זה חזר על עצמו עד שהחיבור ל-MongoDB חזר לעבוד

---

## 🔍 סיבות אפשריות

### 1. בעיית DNS ב-Kubernetes

**מה זה:**
- ה-service `mongodb` לא היה זמין ב-DNS של Kubernetes
- או שה-DNS של Kubernetes לא עבד תקין

**איך לבדוק:**
```bash
# בדוק אם ה-service קיים
kubectl get svc -n panda | grep mongodb

# בדוק את ה-DNS
kubectl get svc mongodb -n panda -o yaml

# נסה לפתור את השם מתוך pod אחר
kubectl run -it --rm debug --image=busybox --restart=Never -n panda -- nslookup mongodb.panda
```

### 2. בעיית Networking ב-Kubernetes

**מה זה:**
- בעיית networking בין ה-pods
- או בעיית CNI (Container Network Interface)

**איך לבדוק:**
```bash
# בדוק את ה-network policies
kubectl get networkpolicies -n panda

# בדוק את ה-pods
kubectl get pods -n panda -o wide
```

### 3. ה-MongoDB Service לא היה מוכן

**מה זה:**
- ה-MongoDB service לא היה מוכן בזמן שה-pod התחיל
- או שה-MongoDB pod לא היה רץ

**איך לבדוק:**
```bash
# בדוק את ה-MongoDB pods
kubectl get pods -n panda | grep mongodb

# בדוק את ה-MongoDB service
kubectl get svc -n panda | grep mongodb

# בדוק את ה-endpoints
kubectl get endpoints mongodb -n panda
```

### 4. בעיית Timing

**מה זה:**
- ה-pod התחיל לפני שה-MongoDB service היה מוכן
- זה יכול לקרות אם אין `initContainers` או `readinessProbe`

**איך לבדוק:**
```bash
# בדוק את ה-deployment
kubectl get deployment panda-panda-focus-server -n panda -o yaml

# בדוק אם יש initContainers או readinessProbe
kubectl describe deployment panda-panda-focus-server -n panda
```

---

## 🔧 פתרונות

### פתרון 1: הוסף Init Container (מומלץ)

**קובץ:** `deployment.yaml` או Helm chart

```yaml
spec:
  template:
    spec:
      initContainers:
      - name: wait-for-mongodb
        image: busybox
        command: ['sh', '-c', 'until nslookup mongodb.panda; do echo waiting for mongodb; sleep 2; done']
```

**יתרונות:**
- ה-pod לא יתחיל עד שה-MongoDB service זמין
- מונע restarts בגלל בעיות timing

---

### פתרון 2: הוסף Readiness Probe

**קובץ:** `deployment.yaml` או Helm chart

```yaml
spec:
  template:
    spec:
      containers:
      - name: focus-server
        readinessProbe:
          exec:
            command:
            - python
            - -c
            - "import pymongo; pymongo.MongoClient('mongodb://mongodb.panda:27017').admin.command('ping')"
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
```

**יתרונות:**
- ה-pod לא יקבל traffic עד שהוא מוכן
- מונע requests ל-pod שלא מוכן

---

### פתרון 3: הוסף Retry Logic בקוד

**קובץ:** `pz/microservices/focus_server/focus_manager.py`

```python
import time
from pymongo.errors import ServerSelectionTimeoutError

def __init__(self, prr=2000, storage_path=r"Z:\segy"):
    # ... existing code ...
    
    # Retry MongoDB connection
    max_retries = 5
    retry_delay = 5
    for attempt in range(max_retries):
        try:
            self.mongo_mapper = RecordingMongoMapper(self.storage_path)
            break
        except ServerSelectionTimeoutError as e:
            if attempt < max_retries - 1:
                logger.warning(f"MongoDB connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(retry_delay)
            else:
                logger.error(f"MongoDB connection failed after {max_retries} attempts: {e}")
                raise
```

**יתרונות:**
- ה-pod ינסה להתחבר מספר פעמים
- מונע restarts בגלל בעיות זמניות

---

### פתרון 4: בדוק את ה-DNS Configuration

**פעולה:**
```bash
# בדוק את ה-CoreDNS
kubectl get pods -n kube-system | grep coredns

# בדוק את ה-logs של CoreDNS
kubectl logs -n kube-system <coredns-pod-name>

# בדוק את ה-config של CoreDNS
kubectl get configmap coredns -n kube-system -o yaml
```

---

## 📊 מצב נוכחי

### Pod Status:

```
panda-panda-focus-server-78dbcfd9d9-kjj77    1/1     Running   4 (28h ago)   46h
```

**ניתוח:**
- ✅ Pod רץ תקין (1/1 Running)
- ✅ Resource usage תקין: CPU 3m, Memory 394Mi
- ✅ Pod רץ כבר 46 שעות (מאז ה-restart האחרון)
- ⚠️ היו 4 restarts ב-28 שעות (אבל עכשיו זה עובד)

### MongoDB Connection:

**נראה שהחיבור ל-MongoDB עובד עכשיו** - ה-pod רץ כבר 46 שעות ללא restarts.

---

## ✅ Checklist

### בדיקות:
- [x] בדוק את ה-logs לפני ה-restarts ✅ **בוצע**
- [x] זהה את השגיאה ✅ **בוצע - MongoDB connection**
- [x] בדוק את ה-resource usage ✅ **בוצע - תקין**
- [ ] בדוק את ה-MongoDB service
- [ ] בדוק את ה-DNS configuration
- [ ] בדוק את ה-networking

### פתרונות:
- [ ] הוסף Init Container ל-deployment
- [ ] הוסף Readiness Probe ל-deployment
- [ ] הוסף Retry Logic בקוד
- [ ] בדוק את ה-DNS configuration

---

## 🎯 מסקנות

### מה גילינו:

1. ✅ **סיבת ה-restarts זוהתה** - בעיית חיבור ל-MongoDB
2. ✅ **הבעיה נפתרה** - ה-pod רץ כבר 46 שעות ללא restarts
3. ⚠️ **צריך למנוע את זה בעתיד** - הוסף init containers או retry logic

### מה לעשות:

1. ✅ **הבעיה נפתרה** - ה-pod רץ תקין עכשיו
2. 📝 **הוסף פתרונות** - init containers או retry logic למניעת בעיות עתידיות
3. 🔍 **בדוק את ה-infrastructure** - ודא שה-MongoDB service זמין תמיד

---

**עודכן לאחרונה:** 2025-11-08 13:25  
**סטטוס:** ✅ בעיה זוהתה ונפתרה - ה-pod רץ תקין  
**פעולה נדרשת:** הוסף פתרונות למניעת בעיות עתידיות

