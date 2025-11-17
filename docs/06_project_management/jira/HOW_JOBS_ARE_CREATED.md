# איפה ואיך מייצרים Jobs במערכת

## 📍 מיקום יצירת Jobs בקוד

### 1. **API Client - `src/apis/focus_server_api.py`**

**פונקציה:** `configure_streaming_job()`

```python
def configure_streaming_job(self, payload: ConfigureRequest) -> ConfigureResponse:
    """
    Configure a streaming job.
    
    Args:
        payload: Configuration request payload
        
    Returns:
        Configuration response with job_id
    """
    # 1. Validate payload
    if not isinstance(payload, ConfigureRequest):
        raise ValidationError("Payload must be a ConfigureRequest instance")
    
    # 2. Convert to dict for JSON serialization
    payload_dict = payload.model_dump()
    
    # 3. Send HTTP POST request
    response = self.post("/configure", json=payload_dict)
    # POST https://10.10.10.100/focus-server/configure
    
    # 4. Parse response
    response_data = response.json()
    configure_response = ConfigureResponse(**response_data)
    
    return configure_response
```

**HTTP Request שנשלח:**
```http
POST https://10.10.10.100/focus-server/configure HTTP/1.1
Host: 10.10.10.100
Content-Type: application/json

{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```

---

## 🔄 תהליך יצירת Job - Flow מלא

### שלב 1: יצירת Request Object

```python
from src.models.focus_server_models import ConfigureRequest

payload = {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "channels": {"min": 0, "max": 50},
    "frequencyRange": {"min": 0, "max": 500},
    "start_time": None,  # Live mode
    "end_time": None,
    "view_type": ViewType.MULTICHANNEL
}

config_request = ConfigureRequest(**payload)
```

### שלב 2: שליחת Request ל-Focus Server

```python
from src.apis.focus_server_api import FocusServerAPI

# focus_server_api הוא fixture שמספק API client
response = focus_server_api.configure_streaming_job(config_request)
```

**מה קורה:**
- שולח POST request ל-`https://10.10.10.100/focus-server/configure`
- מחכה לתשובה מהשרת
- מחזיר `ConfigureResponse` עם `job_id`

### שלב 3: עיבוד בצד השרת (Focus Server)

**Focus Server מקבל את ה-request ומבצע:**

1. **ולידציה** - בודק שהקונפיגורציה תקינה
2. **בדיקת משאבים** - בודק שיש GPU זמין, לא יותר מ-30 jobs פעילים
3. **יצירת job_id** - מייצר מזהה ייחודי (למשל: `"12-70788"`)
4. **יצירת Kubernetes Jobs:**
   - `grpc-job-$JOB_ID` - ה-job הראשי שרץ את ה-gRPC server
   - `cleanup-job-$JOB_ID` - job שמנקה את המשאבים כשסיימו
5. **יצירת Kubernetes Service:**
   - `grpc-service-$JOB_ID` - NodePort service לחשיפת ה-gRPC server
6. **יצירת Task ב-MongoDB** - שומר את פרטי ה-task
7. **הגדרת RabbitMQ Queues** - יוצר queues לתקשורת
8. **החזרת Response** - מחזיר `job_id` ללקוח

### שלב 4: קבלת Response

```python
# ConfigureResponse מכיל:
response.job_id        # "12-70788"
response.stream_url    # "10.10.100.100"
response.stream_port   # 50051
response.status        # "configured"
```

---

## 🐳 מה נוצר ב-Kubernetes?

כאשר Focus Server יוצר job, הוא יוצר:

### 1. **grpc-job-$JOB_ID** (Job ראשי)

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: grpc-job-12-70788
spec:
  backoffLimit: 0
  ttlSecondsAfterFinished: 120
  template:
    spec:
      containers:
      - name: grpc-server
        image: 262399703539.dkr.ecr.eu-central-1.amazonaws.com/pzlinux:latest
        resources:
          limits:
            nvidia.com/gpu.shared: 1  # דורש GPU!
        ports:
        - containerPort: 5000
```

**תפקיד:** מריץ gRPC server ששולח spectrogram data ללקוח

### 2. **cleanup-job-$JOB_ID** (Job ניקוי)

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: cleanup-job-12-70788
spec:
  backoffLimit: 0
  ttlSecondsAfterFinished: 10
  serviceAccountName: cleanup-sa
```

**תפקיד:** מנטר את ה-gRPC job ומנקה משאבים כשהוא מסיים

### 3. **grpc-service-$JOB_ID** (Service)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: grpc-service-12-70788
spec:
  type: NodePort
  selector:
    app: grpc-job-12-70788
  ports:
  - port: 12301
    targetPort: 5000
    nodePort: 30001
```

**תפקיד:** חושף את ה-gRPC server דרך NodePort

---

## ❌ למה יש 503 Service Unavailable?

כאשר השרת מחזיר `503 Service Unavailable`, זה אומר שהשרת **לא יכול ליצור jobs כרגע**.

### סיבות אפשריות:

1. **Focus Server Pod לא רץ**
   ```bash
   kubectl get pods -n panda | grep focus-server
   # אם אין pod או שהוא CrashLoopBackOff
   ```

2. **Focus Server לא יכול להתחבר ל-Kubernetes API**
   - Focus Server צריך גישה ל-Kubernetes API כדי ליצור jobs
   - אם יש בעיית רשת או הרשאות, הוא לא יכול ליצור jobs

3. **אין GPU resources זמינים**
   - כל job דורש `nvidia.com/gpu.shared: 1`
   - אם כל ה-GPUs תפוסים, jobs חדשים לא יכולים להתחיל
   ```bash
   kubectl describe nodes | grep -A 5 "nvidia.com/gpu"
   ```

4. **יותר מדי jobs פעילים (MaxWindows=30)**
   - Focus Server מוגבל ל-30 jobs במקביל
   - אם יש כבר 30 jobs פעילים, הוא לא יכול ליצור עוד

5. **Worker Node לא זמין**
   - אם ה-worker node ב-`NotReady` state, pods לא יכולים להתזמן
   ```bash
   kubectl get nodes
   # אם worker-node הוא NotReady
   ```

6. **MongoDB לא זמין**
   - Focus Server צריך MongoDB כדי לשמור tasks
   - אם MongoDB לא זמין, הוא לא יכול ליצור jobs

---

## 🔍 איך לבדוק מה הבעיה?

### 1. בדיקת Focus Server Pod

```bash
# בדוק אם Focus Server רץ
kubectl get pods -n panda | grep focus-server

# בדוק logs של Focus Server
kubectl logs -n panda -l app=focus-server --tail=100

# בדוק describe אם יש errors
kubectl describe pod -n panda -l app=focus-server
```

### 2. בדיקת GPU Resources

```bash
# בדוק כמה GPUs זמינים
kubectl describe nodes | grep -A 5 "nvidia.com/gpu"

# בדוק כמה jobs pending
kubectl get pods -n panda --field-selector=status.phase=Pending | grep grpc-job

# בדוק כמה jobs running
kubectl get pods -n panda --field-selector=status.phase=Running | grep grpc-job
```

### 3. בדיקת Kubernetes API Access

```bash
# בדוק אם Focus Server יכול לגשת ל-Kubernetes API
kubectl exec -n panda -l app=focus-server -- kubectl get nodes

# בדוק service account permissions
kubectl get serviceaccount -n panda focus-server -o yaml
```

### 4. בדיקת MongoDB

```bash
# בדוק אם MongoDB רץ
kubectl get pods -n panda | grep mongodb

# בדוק connection
kubectl exec -n panda -l app=focus-server -- \
  mongosh mongodb://prisma:prisma@mongodb-panda:27017/prisma --eval "db.adminCommand('ping')"
```

### 5. בדיקת Node Status

```bash
# בדוק מצב ה-nodes
kubectl get nodes

# אם worker-node הוא NotReady:
kubectl describe node worker-node
```

---

## 🛠️ פתרונות אפשריים

### פתרון 1: Restart Focus Server

```bash
# Restart Focus Server pod
kubectl delete pod -n panda -l app=focus-server

# או scale down/up
kubectl scale deployment focus-server -n panda --replicas=0
kubectl scale deployment focus-server -n panda --replicas=1
```

### פתרון 2: ניקוי Jobs ישנים

```bash
# מחק כל ה-pending jobs
kubectl get pods -n panda --field-selector=status.phase=Pending | \
  grep grpc-job | \
  awk '{print $1}' | \
  xargs -I {} kubectl delete pod {} -n panda --grace-period=0 --force

# מחק כל ה-jobs הישנים
kubectl delete jobs -n panda -l app | grep grpc-job
```

### פתרון 3: תיקון Worker Node

```bash
# אם worker-node הוא NotReady:
# 1. בדוק מה הבעיה
kubectl describe node worker-node

# 2. Restart kubelet (על ה-node עצמו)
sudo systemctl restart kubelet

# 3. או uncordon את ה-node
kubectl uncordon worker-node
```

### פתרון 4: בדיקת MongoDB

```bash
# Restart MongoDB אם צריך
kubectl delete pod -n panda -l app=mongodb

# בדוק connection
kubectl exec -n panda -l app=focus-server -- \
  mongosh mongodb://prisma:prisma@mongodb-panda:27017/prisma --eval "db.adminCommand('ping')"
```

---

## 📊 סיכום - איפה ואיך מייצרים Jobs

| שלב | מיקום בקוד | פעולה |
|-----|------------|-------|
| **1. יצירת Request** | `tests/integration/api/...` | `ConfigureRequest(**payload)` |
| **2. שליחת Request** | `src/apis/focus_server_api.py:52` | `configure_streaming_job()` |
| **3. HTTP Call** | `src/apis/focus_server_api.py:77` | `POST /configure` |
| **4. עיבוד בשרת** | Focus Server (לא בקוד שלנו) | יצירת Kubernetes jobs |
| **5. קבלת Response** | `src/apis/focus_server_api.py:82` | `ConfigureResponse(**response_data)` |

**הבעיה הנוכחית:** Focus Server מחזיר `503 Service Unavailable` - צריך לבדוק למה הוא לא יכול ליצור jobs.

**הסיבות הנפוצות:**
1. Focus Server pod לא רץ או crash
2. אין GPU resources זמינים
3. יותר מדי jobs פעילים (MaxWindows=30)
4. Worker node לא זמין
5. MongoDB לא זמין

**המלצה:** לבדוק את כל הנקודות לעיל כדי לזהות את הבעיה הספציפית.

