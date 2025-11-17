# פקודות לניקוי Jobs/Pods

**תאריך:** 2025-11-09  
**מטרה:** ניקוי כל ה-jobs/pods שנוצרו במהלך הטסטים

---

## 🎯 ניקוי Jobs דרך API

### ניקוי Jobs ספציפיים:

```bash
python scripts/cleanup_all_jobs.py --job-ids job1 job2 job3
```

### ניקוי Jobs דרך Python:

```python
from config.config_manager import ConfigManager
from src.apis.focus_server_api import FocusServerAPI

config_manager = ConfigManager(environment="staging")
api = FocusServerAPI(config_manager)

# Cancel specific job
api.cancel_job("job_id_here")
```

---

## 🎯 ניקוי Kubernetes Pods (gRPC Jobs)

### דרך Script:

```bash
python scripts/cleanup_all_jobs.py --k8s
```

### דרך kubectl (ישירות):

```bash
# רשימת כל ה-gRPC job pods
kubectl get pods -n panda -l app=grpc-job

# מחיקת כל ה-gRPC job pods
kubectl delete pods -n panda -l app=grpc-job

# מחיקת pod ספציפי
kubectl delete pod <pod-name> -n panda
```

### דרך k9s:

1. התחבר ל-k9s:
   ```bash
   ssh root@10.10.100.3
   ssh prisma@10.10.100.113
   k9s
   ```

2. בחר namespace: `panda`
3. בחר pods
4. חפש pods עם `grpc-job` בשם
5. לחץ `Ctrl+D` למחיקה

---

## 🎯 ניקוי משולב (API + K8s)

```bash
python scripts/cleanup_all_jobs.py --job-ids job1 job2 --k8s
```

---

## 🔧 פקודות kubectl נוספות

### רשימת כל ה-pods:

```bash
kubectl get pods -n panda
```

### רשימת gRPC job pods:

```bash
kubectl get pods -n panda -l app=grpc-job
```

### מחיקת כל ה-gRPC jobs:

```bash
kubectl delete pods -n panda -l app=grpc-job
```

### מחיקת pods לפי שם (pattern):

```bash
kubectl get pods -n panda | grep grpc-job | awk '{print $1}' | xargs kubectl delete pod -n panda
```

### מחיקת pods ישנים (יותר מ-X דקות):

```bash
# מחיקת pods שנוצרו לפני יותר מ-10 דקות
kubectl get pods -n panda -l app=grpc-job --field-selector=status.phase!=Running -o jsonpath='{.items[*].metadata.name}' | xargs -r kubectl delete pod -n panda
```

---

## 📝 הערות

1. **ניקוי אוטומטי:**
   - הטסטים אמורים לנקות jobs בסוף
   - אם טסט נכשל, cleanup לא מתבצע
   - צריך לנקות ידנית

2. **gRPC Jobs:**
   - כל job יוצר pod ב-Kubernetes
   - Pods נקראים `grpc-job-*`
   - Label: `app=grpc-job`

3. **ניקוי בטוח:**
   - Jobs פעילים יסתיימו אוטומטית
   - Pods יימחקו וייווצרו מחדש אם צריך
   - אין השפעה על infrastructure pods

---

## ⚠️ אזהרות

1. **אל תמחק infrastructure pods:**
   - `panda-panda-focus-server-*`
   - `mongodb-*`
   - `rabbitmq-panda-*`

2. **בדוק לפני מחיקה:**
   ```bash
   kubectl get pods -n panda -l app=grpc-job
   ```

3. **ניקוי זהיר:**
   - Jobs פעילים יסתיימו
   - בדוק שאין jobs חשובים רצים

---

## 🎯 Quick Commands

### ניקוי מהיר (K8s pods בלבד):

```bash
kubectl delete pods -n panda -l app=grpc-job
```

### ניקוי מלא (Script):

```bash
python scripts/cleanup_all_jobs.py --k8s
```

### בדיקה לפני ניקוי:

```bash
kubectl get pods -n panda -l app=grpc-job
```

