# ניקוי Jobs/Pods על השרת (Linux)

**תאריך:** 2025-11-09  
**מיקום:** Linux Server (10.10.10.150)

---

## 🎯 ניקוי ישיר דרך kubectl

### התחברות לשרת:

```bash
ssh root@10.10.10.10
ssh prisma@10.10.10.150
```

### ⚠️ הערה חשובה:

**הסקריפטים Python (`cleanup_all_jobs.py`, `environment_cleanup.py`) נמצאים במכונה המקומית (Windows) ולא על השרת Linux.**

**על השרת Linux, השתמש ב-kubectl ישירות!**

### פקודות kubectl לניקוי:

#### 1. בדיקה לפני ניקוי:

```bash
# רשימת כל ה-pods
kubectl get pods -n panda

# רשימת gRPC job pods
kubectl get pods -n panda -l app=grpc-job

# רשימת pods לפי שם (pattern)
kubectl get pods -n panda | grep grpc-job
```

#### 2. ניקוי gRPC job pods:

```bash
# מחיקת כל ה-gRPC job pods
kubectl delete pods -n panda -l app=grpc-job

# מחיקת pods לפי pattern
kubectl get pods -n panda | grep grpc-job | awk '{print $1}' | xargs kubectl delete pod -n panda
```

#### 3. ניקוי Kubernetes Jobs:

```bash
# רשימת jobs
kubectl get jobs -n panda

# מחיקת gRPC jobs
kubectl delete jobs -n panda -l app=grpc-job

# מחיקת jobs לפי pattern
kubectl get jobs -n panda | grep grpc-job | awk '{print $1}' | xargs kubectl delete job -n panda
```

#### 4. ניקוי Services:

```bash
# רשימת services
kubectl get svc -n panda

# מחיקת gRPC services
kubectl get svc -n panda | grep grpc-service | awk '{print $1}' | xargs kubectl delete svc -n panda
```

---

## 🔧 פקודות משולבות

### ניקוי מלא (pods + jobs + services):

```bash
# ניקוי pods
kubectl delete pods -n panda -l app=grpc-job

# ניקוי jobs
kubectl delete jobs -n panda -l app=grpc-job

# ניקוי services
kubectl get svc -n panda | grep grpc-service | awk '{print $1}' | xargs kubectl delete svc -n panda
```

### ניקוי pods ישנים (יותר מ-X דקות):

```bash
# מחיקת pods ב-Error/Failed state
kubectl get pods -n panda -l app=grpc-job --field-selector=status.phase!=Running -o jsonpath='{.items[*].metadata.name}' | xargs -r kubectl delete pod -n panda
```

---

## 📝 הערות

1. **הסקריפטים Python:**
   - הסקריפטים (`cleanup_all_jobs.py`, `environment_cleanup.py`) **נמצאים במכונה המקומית (Windows)** ולא על השרת Linux
   - על השרת Linux, **השתמש ב-kubectl ישירות**
   - אם אתה מנסה להריץ `python` על השרת, זה לא יעבוד כי:
     - הסקריפטים לא נמצאים שם
     - צריך `python3` (לא `python`) על Linux
     - אבל עדיף להשתמש ב-kubectl ישירות

2. **אם אין pods לניקוי:**
   - `kubectl delete pods -n panda -l app=grpc-job` החזיר "No resources found"
   - `kubectl get pods -n panda -l app=grpc-job` החזיר "No resources found"
   - `kubectl get jobs -n panda -l app=grpc-job` החזיר "No resources found"
   - **זה אומר שאין pods/jobs לניקוי - הכל נקי! ✅**

3. **בדיקה:**
   ```bash
   # בדוק כמה pods יש
   kubectl get pods -n panda | grep grpc-job | wc -l
   
   # בדוק כמה jobs יש
   kubectl get jobs -n panda | grep grpc-job | wc -l
   
   # בדיקה מפורטת
   kubectl get pods -n panda -l app=grpc-job
   kubectl get jobs -n panda -l app=grpc-job
   ```

4. **להריץ את הסקריפטים Python:**
   - הסקריפטים צריכים לרוץ **מהמכונה המקומית (Windows)**
   - לא מהשרת Linux
   - על Windows: `python scripts/cleanup_all_jobs.py --k8s`
   - על Linux: השתמש ב-kubectl ישירות

---

## 🎯 Quick Commands

### בדיקה:
```bash
kubectl get pods -n panda -l app=grpc-job
kubectl get jobs -n panda -l app=grpc-job
```

### ניקוי:
```bash
kubectl delete pods -n panda -l app=grpc-job
kubectl delete jobs -n panda -l app=grpc-job
```

### ניקוי מלא (one-liner):
```bash
kubectl delete pods,jobs -n panda -l app=grpc-job
```

