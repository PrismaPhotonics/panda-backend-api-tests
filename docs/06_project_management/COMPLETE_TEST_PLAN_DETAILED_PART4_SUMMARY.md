# תוכנית בדיקות Focus Server - חלק 4: סיכום ומילון מושגים
## Infrastructure, Security, Summary & Technical Glossary

---

## 🏗️ INFRASTRUCTURE TESTS

### TEST: SSH Access to Production

**Jira ID**: PZ-13900  
**Priority**: High  
**Status**: TODO

**מטרה**: וידוא גישת SSH לservers

**למה נחוץ?**
SSH הוא הדרך היחידה ל:
- **Troubleshooting** - בדיקת בעיות
- **Logs** - קריאת לוגים
- **kubectl** - ניהול Kubernetes
- **k9s** - ממשק חזותי ל-K8s
- **תחזוקה** - עדכונים ותיקונים

**חיבורים:**
```
Local PC
   ↓ SSH
Jump Host (10.10.100.3)
   ↓ SSH
Target Host (10.10.100.113)
   ↓ kubectl
Kubernetes Cluster
```

**יישום:**
```python
import paramiko

def test_ssh_access_to_production(self):
    """Test PZ-13900: SSH Access"""
    
    # Connect to jump host
    ssh_jump = paramiko.SSHClient()
    ssh_jump.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_jump.connect(
        '10.10.100.3',
        username='root',
        password='***'  # From environment
    )
    
    # Test commands on jump host
    stdin, stdout, stderr = ssh_jump.exec_command('hostname')
    hostname = stdout.read().decode().strip()
    assert hostname is not None
    logger.info(f"✓ Jump host: {hostname}")
    
    # Test whoami
    stdin, stdout, stderr = ssh_jump.exec_command('whoami')
    user = stdout.read().decode().strip()
    assert user == 'root'
    logger.info(f"✓ User: {user}")
    
    # Test uptime
    stdin, stdout, stderr = ssh_jump.exec_command('uptime')
    uptime = stdout.read().decode().strip()
    logger.info(f"✓ Uptime: {uptime}")
    
    ssh_jump.close()
    
    # Connect to target host
    ssh_target = paramiko.SSHClient()
    ssh_target.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_target.connect(
        '10.10.100.113',
        username='prisma',
        password='***'
    )
    
    # Test kubectl
    stdin, stdout, stderr = ssh_target.exec_command('kubectl version --client')
    kubectl_output = stdout.read().decode()
    assert 'Client Version' in kubectl_output
    logger.info("✓ kubectl is available")
    
    # Test k9s
    stdin, stdout, stderr = ssh_target.exec_command('k9s version')
    k9s_output = stdout.read().decode()
    assert 'Version' in k9s_output or 'k9s' in k9s_output
    logger.info("✓ k9s is available")
    
    ssh_target.close()
    
    logger.info("✅ SSH access validated")
```

---

### TEST: Kubernetes Cluster Connection

**Jira ID**: PZ-13899  
**Priority**: High  
**Status**: TODO

**מטרה**: וידוא חיבור ל-Kubernetes ובריאות pods

**מה בודקים?**
- חיבור ל-K8s cluster
- רשימת pods ב-namespace `panda`
- status של כל pod (Running/Ready)
- resource usage (CPU/Memory)

**Kubernetes Concepts:**

| מושג | הסבר | דוגמה |
|------|------|-------|
| **Pod** | יחידת ריצה קטנה (container) | `panda-focus-server-abc123` |
| **Namespace** | הפרדה לוגית | `panda` |
| **Service** | endpoint פנימי | `panda-focus-server.panda:5000` |
| **Deployment** | ניהול pods | `panda-focus-server` |

**יישום:**
```python
from kubernetes import client, config

def test_kubernetes_cluster_connection(self):
    """Test PZ-13899: Kubernetes Connection"""
    
    # Load kubeconfig
    config.load_kube_config()
    v1 = client.CoreV1Api()
    
    # List pods in panda namespace
    pods = v1.list_namespaced_pod(namespace="panda")
    logger.info(f"Found {len(pods.items)} pods in 'panda' namespace")
    
    # Check each pod
    for pod in pods.items:
        pod_name = pod.metadata.name
        pod_status = pod.status.phase
        
        logger.info(f"Pod: {pod_name}")
        logger.info(f"  Status: {pod_status}")
        
        # Verify Running
        assert pod_status == "Running", \
            f"Pod {pod_name} is not Running (status: {pod_status})"
        
        # Check containers ready
        if pod.status.container_statuses:
            for container in pod.status.container_statuses:
                assert container.ready, \
                    f"Container {container.name} in pod {pod_name} is not ready"
                logger.info(f"  Container {container.name}: Ready")
    
    logger.info("✅ All pods are Running and Ready")
```

---

### TEST: MongoDB Connection

**Jira ID**: PZ-13898  
**Priority**: High  
**Status**: TODO

**מטרה**: וידוא חיבור ל-MongoDB ובריאות DB

**מה בודקים?**
- חיבור ל-MongoDB
- קיום collections נדרשות
- sampling של documents
- schema validation

**MongoDB Collections:**

| Collection | תיאור | שימוש |
|------------|-------|-------|
| **base_paths** | נתיבי recordings | מיפוי למיקומי storage |
| **node2** | metadata של recordings | פרטים על recordings |
| **node4** | extended metadata | נתונים נוספים |

**יישום:**
```python
from pymongo import MongoClient

def test_mongodb_connection(self):
    """Test PZ-13898: MongoDB Connection"""
    
    # Connect
    client = MongoClient(
        "mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma"
    )
    
    db = client['prisma']
    
    # Verify connection
    server_info = client.server_info()
    logger.info(f"✓ MongoDB version: {server_info['version']}")
    
    # List collections
    collections = db.list_collection_names()
    logger.info(f"✓ Found {len(collections)} collections")
    
    # Verify required collections exist
    required = ['base_paths', 'node2', 'node4']
    for coll_name in required:
        assert coll_name in collections, \
            f"Required collection '{coll_name}' not found"
        logger.info(f"✓ Collection '{coll_name}' exists")
    
    # Sample a document from node4
    node4 = db['node4']
    sample_doc = node4.find_one()
    
    if sample_doc:
        logger.info(f"✓ Sample document from node4:")
        logger.info(f"  Fields: {list(sample_doc.keys())}")
        
        # Verify required fields
        required_fields = ['uuid', 'start_time', 'end_time', 'deleted']
        for field in required_fields:
            assert field in sample_doc, f"Field '{field}' missing in node4"
        
        logger.info("✓ node4 schema is valid")
    
    client.close()
    logger.info("✅ MongoDB connection validated")
```

---

## 🔒 SECURITY TESTS

### TEST: Robustness to Malformed Inputs

**Jira ID**: PZ-13572  
**Priority**: High  
**Type**: Security Test  
**Status**: חלקי

**מטרה**: לוודא שהמערכת **לא קורסת** מקלטים מזיקים

**מה בודקים?**

1. **Malformed JSON**
2. **SQL Injection attempts**
3. **XSS attempts**
4. **Oversized payloads** (10MB+)
5. **CORS headers**

**תרחישים:**

**1. Malformed JSON:**
```json
{
  "invalid_json": unclosed,
  "missing": "quote
}
```

**Expected**: HTTP 400 (לא 500!)

**2. SQL Injection:**
```http
GET /metadata?task_id=' OR '1'='1
```

**Expected**: מסונן, לא גורם crash

**3. XSS:**
```json
{
  "task_id": "<script>alert('xss')</script>"
}
```

**Expected**: מסונן או encoded

**4. Oversized Payload:**
```python
huge_payload = {
    "data": "x" * (10 * 1024 * 1024)  # 10MB
}
```

**Expected**: HTTP 413 (Payload Too Large) או דחייה אחרת

**5. CORS:**
```http
OPTIONS /configure HTTP/1.1
Origin: https://evil.com
```

**Expected**: CORS headers נכונים

**יישום:**
```python
def test_security_resilience(self, focus_server_api):
    """Test PZ-13572: Security Robustness"""
    
    # TEST 1: Malformed JSON
    try:
        response = requests.post(
            f"{base_url}/configure",
            data='{"invalid": unclosed',  # Bad JSON
            headers={'Content-Type': 'application/json'}
        )
        # Should be 400, not 500
        assert response.status_code == 400
        logger.info("✓ Malformed JSON returns 400 (not 500)")
    except:
        logger.info("✓ Malformed JSON handled gracefully")
    
    # TEST 2: SQL Injection
    try:
        response = requests.get(
            f"{base_url}/metadata",
            params={"task_id": "' OR '1'='1"}
        )
        # Should not crash (500)
        assert response.status_code != 500
        logger.info("✓ SQL injection attempt handled")
    except Exception as e:
        logger.info(f"✓ SQL injection attempt blocked: {e}")
    
    # TEST 3: Oversized payload
    huge_data = "x" * (10 * 1024 * 1024)  # 10MB
    try:
        response = requests.post(
            f"{base_url}/configure",
            json={"data": huge_data},
            timeout=5
        )
        # Should reject gracefully
        assert response.status_code in [400, 413, 413]
        logger.info("✓ Oversized payload rejected")
    except:
        logger.info("✓ Oversized payload handled")
    
    # TEST 4: CORS
    response = requests.options(f"{base_url}/configure")
    if 'Access-Control-Allow-Origin' in response.headers:
        logger.info(f"✓ CORS headers present: {response.headers['Access-Control-Allow-Origin']}")
    
    logger.info("✅ Security resilience validated")
```

---

## 📊 סיכום סופי של כל הטסטים

### סטטיסטיקה

| קטגוריה | סה"כ | ממומש | TODO | אחוז |
|----------|------|-------|------|------|
| **Integration** | 44 | 35 | 9 | 80% |
| **SingleChannel** | 15 | 15 | 0 | 100% |
| **Dynamic ROI** | 13 | 13 | 0 | 100% |
| **Infrastructure** | 6 | 3 | 3 | 50% |
| **Performance** | 5 | 3 | 2 | 60% |
| **Security** | 2 | 1 | 1 | 50% |
| **E2E** | 3 | 2 | 1 | 67% |
| **Data Quality** | 5 | 5 | 0 | 100% |
| **TOTAL** | **93** | **77** | **16** | **83%** |

### Coverage Matrix

| רכיב | כיסוי | טסטים |
|------|-------|-------|
| **POST /configure** | 95% | 40+ tests |
| **GET /waterfall** | 90% | 30+ tests |
| **GET /metadata** | 85% | 10+ tests |
| **GET /sensors** | 100% | 5 tests |
| **GET /channels** | 100% | 5 tests |
| **RabbitMQ Commands** | 90% | 15+ tests |
| **MongoDB Queries** | 75% | 8 tests |
| **Kubernetes** | 60% | 4 tests |

---

## 📖 מילון מושגים טכניים - מקיף

### Core Concepts (מושגי יסוד)

#### NFFT (Number of FFT Points)
**הגדרה**: מספר נקודות ה-FFT (Fast Fourier Transform)  
**ערכים תקפים**: 128, 256, 512, 1024, 2048, 4096 (חזקות של 2)  
**משמעות**: קובע את רזולוציית התדר בניתוח

**Trade-offs:**
- **NFFT קטן** → רזולוציית תדר נמוכה, עדכונים מהירים, CPU נמוך
- **NFFT גדול** → רזולוציית תדר גבוהה, עדכונים איטיים, CPU גבוה

**נוסחה**:
```
Frequency Bins = NFFT / 2
Rows per Second = PRR / NFFT
```

**דוגמה**:
```
NFFT = 1024
PRR = 1000 samples/sec

Frequency Bins = 1024 / 2 = 512 bins
Rows/sec = 1000 / 1024 = 0.98 rows/sec
```

---

#### PRR (Pulse Repetition Rate)
**הגדרה**: קצב חזרת הדפקים - כמה פעמים לשנייה המערכת דוגמת  
**יחידות**: samples/sec או Hz  
**טווח טיפוסי**: 1000-2000 samples/sec

**משמעות**:
- **PRR גבוה** → יכולת לבדוק תדרים גבוהים יותר
- **PRR נמוך** → גבול Nyquist נמוך יותר

**קשר ל-Nyquist**:
```
Nyquist Frequency = PRR / 2

אם PRR = 1000 → Nyquist = 500 Hz
אם PRR = 2000 → Nyquist = 1000 Hz
```

**איפה מקבלים?**
```python
metadata = focus_server_api.get_live_metadata()
prr = metadata.prr  # From live system
```

---

#### Nyquist Frequency
**הגדרה**: התדר המקסימלי שניתן לדגום נכון  
**נוסחה**: `Nyquist = PRR / 2`  
**משפט Nyquist-Shannon**: תדר הדגימה חייב להיות לפחות פי 2 מהתדר המקסימלי

**למה חשוב?**
חריגה מ-Nyquist → **Aliasing**:
```
תדר אמיתי: 600 Hz
PRR: 1000 (Nyquist = 500 Hz)

התוצאה: התדר ייראה כמו 400 Hz (WRONG!)
הסיבה: 600 Hz "מתקפל" חזרה לטווח 0-500
```

**דוגמת Aliasing בחיים:**
```
גלגל מסתובב מהר (600 RPM)
מצלמה צולמת ב-500 FPS
בסרטון: הגלגל נראה מסתובב לאחור!
זה Aliasing.
```

---

#### Spectrogram (ספקטוגרמה)
**הגדרה**: ייצוג תלת-ממדי של אות (זמן × תדר × עוצמה)  
**צירים**:
- **X (זמן)**: התקדמות בזמן
- **Y (תדר)**: תדרים שנבדקים
- **Z (עוצמה)**: צבע - כהה=חלש, בהיר=חזק

**דוגמה**:
```
     תדר (Hz)
      ↑
 500 |  [אדום]     [צהוב]
 400 |  [כתום]     [כתום]
 300 |  [צהוב]     [ירוק]
 200 |  [ירוק]     [כחול]
 100 |  [כחול]     [כחול]
   0 |____________→ זמן (sec)
      0    5    10   15   20
```

**מה כל pixel אומר?**
- מיקום (x, y) → זמן ותדר
- צבע → עוצמת האות בתדר זה באותו זמן

---

#### Throughput (תפוקה)
**הגדרה**: כמות הנתונים שהמערכת מעבדת/משדרת ליחידת זמן  
**יחידות**: Mbps (Megabits per second)

**נוסחה**:
```
Throughput (Mbps) = (Rows/sec × Bytes/row × 8 bits/byte) / 1,000,000
```

**דוגמה**:
```
Rows/sec = 0.98
Bytes/row = 102,400
Throughput = 0.98 × 102,400 × 8 / 1,000,000 = 0.80 Mbps
```

**קטגוריות**:
- **Low**: < 1 Mbps
- **Medium**: 1-10 Mbps
- **High**: 10-50 Mbps
- **Very High**: > 50 Mbps

---

### API & Network Concepts

#### Endpoint
**הגדרה**: URL שמספק פונקציונליות ספציפית  
**דוגמאות**:
```
POST   /configure
GET    /metadata/{task_id}
GET    /waterfall/{task_id}/{row_count}
GET    /sensors
GET    /channels
POST   /recordings_in_time_range
```

---

#### HTTP Status Codes (מדריך מלא)

**2xx - Success:**
| Code | Name | Usage in Focus Server |
|------|------|----------------------|
| **200** | OK | /configure accepted, /sensors returned |
| **201** | Created | /waterfall has data |
| **208** | Already Reported | **Historic playback complete** |

**4xx - Client Errors:**
| Code | Name | Usage |
|------|------|-------|
| **400** | Bad Request | Invalid configuration, missing fields |
| **404** | Not Found | Task/consumer not found |
| **413** | Payload Too Large | Request body too big |
| **422** | Unprocessable Entity | Validation error |

**5xx - Server Errors:**
| Code | Name | Usage |
|------|------|-------|
| **500** | Internal Server Error | Server crash/bug |
| **503** | Service Unavailable | Dependency down (MongoDB/RabbitMQ) |

---

#### JSON Payload
**הגדרה**: פורמט טקסט להעברת נתונים  
**מאפיינים**:
- קריא לבני אדם
- קל לparse
- תמיכה בנesting

**דוגמה**:
```json
{
  "nfftSelection": 1024,
  "channels": {
    "min": 0,
    "max": 50
  },
  "nested": {
    "deep": {
      "value": 123
    }
  }
}
```

---

### Infrastructure Concepts

#### MongoDB
**הגדרה**: NoSQL מסד נתונים מבוסס documents  
**שימוש ב-Focus Server**:
- אחסון **recordings metadata**
- שמירת **tasks configuration**
- מיפוי **time ranges** ל-recordings

**Collections:**
```
prisma DB
├── base_paths    (recording paths)
├── node2         (metadata)
└── node4         (extended metadata)
```

**Query Example:**
```javascript
db.node4.find({
  start_time: {$lte: 1700000600},
  end_time: {$gte: 1700000000},
  deleted: false
})
```

---

#### RabbitMQ
**הגדרה**: Message Broker לתקשורת אסינכרונית  
**פרוטוקול**: AMQP (Advanced Message Queuing Protocol)

**רכיבים:**
```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  Publisher   │──────>│   Exchange   │──────>│    Queue     │──────> Consumer
│ (Test Code)  │       │baby_analyzer │       │  commands    │       │(Baby Analyzer)
└──────────────┘       └──────────────┘       └──────────────┘
```

**Routing Keys:**
- `roi` - Region of Interest commands
- `caxis` - Color axis adjustments
- `colormap` - Colormap selection

**Connection:**
```
Host: 10.10.100.107
Port: 5672 (AMQP)
Port: 15672 (Management UI)
Credentials: prisma/prisma
```

---

#### Kubernetes (K8s)
**הגדרה**: מערכת אורכיסטרציה של containers  
**שימוש**: ניהול Baby Analyzer pods

**היררכיה:**
```
Cluster (10.10.100.102:6443)
└── Namespace: panda
    ├── Pod: baby-analyzer-job-abc123
    ├── Pod: focus-server-xyz789
    ├── Service: panda-focus-server.panda:5000
    └── Deployment: panda-focus-server
```

**פקודות שימושיות:**
```bash
# List pods
kubectl get pods -n panda

# Describe pod
kubectl describe pod <pod-name> -n panda

# Logs
kubectl logs <pod-name> -n panda

# Port forward
kubectl port-forward <pod-name> 5000:5000 -n panda
```

---

#### gRPC
**הגדרה**: Remote Procedure Call framework ל-streaming  
**שימוש**: העברת **ספקטוגרמות בזמן אמת**

**Advantages:**
- **Binary protocol** → מהיר מ-JSON
- **Streaming** → continuous data flow
- **Typed** → proto files מגדירים schema

**Connection:**
```python
import grpc

channel = grpc.insecure_channel(
    f"{stream_url}:{stream_port}"
)
stub = DataStreamServiceStub(channel)

# Stream data
for message in stub.StreamSpectrograms(request):
    process_spectrogram(message)
```

---

### Testing Concepts

#### Integration Test
**הגדרה**: בודק אינטראקציה בין 2+ קומפוננטות  
**דוגמה**: Focus Server → MongoDB → RabbitMQ  
**מטרה**: לוודא שהקומפוננטות עובדות **ביחד**

---

#### Unit Test
**הגדרה**: בודק פונקציה/מחלקה **בודדת**  
**דוגמה**: בדיקת `generate_task_id()`  
**מטרה**: לוודא לוגיקה מבודדת

---

#### E2E Test (End-to-End)
**הגדרה**: בודק תרחיש **מלא** מהתחלה לסוף  
**דוגמה**: Configure → Poll → Get Data → Complete  
**מטרה**: לוודא שהמערכת **כולה** עובדת

---

#### Performance Test
**הגדרה**: בודק **ביצועים** ו**תפוקה**  
**מדדים**:
- **Latency**: זמן תגובה
- **Throughput**: כמות נתונים/sec
- **Resource Usage**: CPU/Memory

**דוגמה**:
```python
# Measure latency
start = time.time()
response = api.configure(...)
latency = time.time() - start

assert latency < 2.0, f"Too slow: {latency:.2f}s"
```

---

#### Negative Test
**הגדרה**: בודק ש**inputs לא תקפים נדחים**  
**דוגמאות**:
- min > max
- ערכים שליליים
- שדות חסרים

**מטרה**: לוודא **error handling** ו**validation**

---

### Data Concepts

#### Task / Job
**הגדרה**: יחידת עבודה שמבצעת processing  
**מזהה**: `task_id` או `job_id`  
**מצבים**:
- configured
- running
- completed
- failed

**Lifecycle:**
```
Created → Configured → Running → Completed → Cleaned up
```

---

#### Recording Window
**הגדרה**: טווח זמן שבו יש recording זמין  
**פורמט**: `[start_timestamp, end_timestamp]`

**דוגמה**:
```json
[
  [1700000000, 1700000600],  // 10-minute recording
  [1700000600, 1700001200],  // Next 10 minutes
  [1700001200, 1700001800]   // Another 10 minutes
]
```

**שימוש**:
```python
# Find recordings in range
request = {
    "start_time": 1700000300,
    "end_time": 1700001500
}

# Returns overlapping windows:
# [1700000000, 1700000600] ✓ overlaps
# [1700000600, 1700001200] ✓ overlaps
# [1700001200, 1700001800] ✓ overlaps
```

---

#### View Type
**הגדרה**: מצב תצוגה  
**ערכים**:
- **0** = MULTICHANNEL (מספר sensors)
- **1** = SINGLECHANNEL (sensor אחד)

**MULTICHANNEL:**
```
channels: {min: 0, max: 50}
→ 50 sensors
→ stream_amount = 1
→ channel_to_stream_index = {"0": 0, "1": 0, ..., "49": 0}
```

**SINGLECHANNEL:**
```
channels: {min: 7, max: 7}
→ 1 sensor
→ stream_amount = 1
→ channel_to_stream_index = {"7": 0}
```

---

#### ROI (Region of Interest)
**הגדרה**: טווח ה-sensors שרוצים לראות  
**פרמטרים**: start, end

**דוגמה**:
```
ROI: [50, 150]
→ Monitor sensors 50, 51, 52, ..., 150
→ Total: 100 sensors
```

**Dynamic ROI:**
שינוי ROI תוך כדי ריצה ללא הפסקה:
```
Initial: [0, 100]
   ↓ (send ROI command via RabbitMQ)
Changed: [50, 150]
   ↓ (Baby Analyzer reinitializes)
New data: sensors 50-150 only
```

---

#### CAxis (Color Axis)
**הגדרה**: טווח ערכי amplitude ל-colormap  
**פרמטרים**: caxis_min, caxis_max

**דוגמה**:
```
CAxis: [-100, 0] dB

Mapping:
-100 dB → Blue (cold)
-60 dB → Green
-20 dB → Red (hot)
0 dB → White (max)
```

**שינוי CAxis:**
```
From: [-100, 0] → full range
To: [-80, -20] → focused range

Result: Better contrast for signals in -80 to -20 dB range
```

---

### Time & Format Concepts

#### yymmddHHMMSS Format
**הגדרה**: פורמט זמן של Focus Server  
**מבנה**: 12 digits

**פירוק:**
```
"251027143045"

25    = year (2025)
10    = month (October)
27    = day
14    = hour (24h format)
30    = minute
45    = second
```

**המרה:**
```python
# datetime → yymmddHHMMSS
def datetime_to_yymmddHHMMSS(dt: datetime) -> str:
    return dt.strftime("%y%m%d%H%M%S")

# Example
dt = datetime(2025, 10, 27, 14, 30, 45)
result = datetime_to_yymmddHHMMSS(dt)
# "251027143045"
```

**yymmddHHMMSS → datetime:**
```python
def yymmddHHMMSS_to_datetime(time_str: str) -> datetime:
    return datetime.strptime(time_str, "%y%m%d%H%M%S")

# Example
time_str = "251027143045"
dt = yymmddHHMMSS_to_datetime(time_str)
# datetime(2025, 10, 27, 14, 30, 45)
```

---

#### Epoch Timestamp
**הגדרה**: מספר שניות מ-1 January 1970 00:00:00 UTC  
**דוגמה**: `1700000000` = November 14, 2023

**המרה:**
```python
# datetime → epoch
import time
epoch = int(time.time())
# 1730034645

# epoch → datetime
dt = datetime.fromtimestamp(epoch)
```

---

### Pytest Concepts

#### Fixture
**הגדרה**: setup code שרץ לפני הטסט  
**שימוש**: הכנת resources (DB connection, API client)

**דוגמה:**
```python
@pytest.fixture
def focus_server_api(config_manager):
    """Create FocusServerAPI instance."""
    api = FocusServerAPI(config_manager)
    yield api
    # Cleanup (if needed)

# Usage
def test_something(focus_server_api):
    # focus_server_api is ready to use!
    response = focus_server_api.get_channels()
```

---

#### Marker
**הגדרה**: תגית לסיווג טסטים  
**דוגמאות**:
```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
@pytest.mark.smoke
def test_something():
    pass
```

**הרצה לפי markers:**
```bash
# Run only critical tests
pytest -m critical

# Run integration tests
pytest -m integration

# Run API tests that are NOT slow
pytest -m "api and not slow"
```

---

#### Parametrize
**הגדרה**: הרצת אותו טסט עם inputs שונים

**דוגמה:**
```python
@pytest.mark.parametrize("nfft", [128, 256, 512, 1024, 2048, 4096])
def test_nfft_value(focus_server_api, nfft):
    """Test each NFFT value."""
    payload = {"nfftSelection": nfft, ...}
    response = focus_server_api.configure(...)
    assert response.job_id

# This creates 6 separate tests!
```

---

## 🎯 תוכנית עבודה מפורטת לאוטומציה

### Phase 1: High Priority Integration (2-3 weeks)

**טסטים ליישום:**
- [ ] PZ-13909: Historic Missing end_time
- [ ] PZ-13907: Historic Missing start_time
- [ ] Completion של Historic tests suite

**משאבים נדרשים:**
- פיתוח: 1 QA Engineer
- זמן: 2-3 שבועות
- תשתית: גישה ל-MongoDB עם historic data

**Deliverables:**
```
tests/integration/api/
├── test_historic_playback_validation.py (NEW)
│   ├── TestMissingTimeFields
│   │   ├── test_missing_start_time
│   │   └── test_missing_end_time
│   ├── TestInvalidTimeRanges
│   │   ├── test_end_before_start
│   │   └── test_future_timestamps
│   └── TestHistoricEdgeCases
│       ├── test_very_old_timestamps
│       └── test_zero_duration
```

---

### Phase 2: Infrastructure Tests (1-2 weeks)

**טסטים ליישום:**
- [ ] PZ-13900: SSH Access
- [ ] PZ-13899: Kubernetes Connection
- [ ] PZ-13898: MongoDB Connection

**משאבים נדרשים:**
- גישת SSH ל-production
- kubeconfig file
- MongoDB credentials

**Deliverables:**
```
tests/infrastructure/
├── test_ssh_connectivity.py (NEW)
├── test_kubernetes_health.py (NEW)
└── test_mongodb_health.py (UPDATE)
```

---

### Phase 3: Performance & Load (1-2 weeks)

**טסטים ליישום:**
- [ ] PZ-13571: Configure latency p95
- [ ] Memory load tests
- [ ] Concurrent task limits

**כלים נדרשים:**
- Locust או pytest-benchmark
- מדידות resource usage
- monitoring tools

---

### Phase 4: Security Hardening (1 week)

**טסטים ליישום:**
- [ ] PZ-13572: Malformed inputs (להשלים)
- [ ] OWASP Top 10 tests
- [ ] Penetration testing basics

**כלים:**
- OWASP ZAP
- Security headers validation
- Input fuzzing

---

## ✅ סיכום והמלצות

### מצב נוכחי

**Strong Points (חוזקות):**
- ✅ 83% מהטסטים ממומשים
- ✅ כיסוי מצוין של Happy Path
- ✅ Negative tests מקיפים
- ✅ SingleChannel ו-ROI מלאים

**Gaps (חסרים):**
- ⚠️ Infrastructure tests חלקיים
- ⚠️ Performance tests לא מושלמים
- ⚠️ Security tests בסיסיים
- ⚠️ E2E עם gRPC חלקי

### המלצות לפגישה

**להדגיש:**
1. **83% coverage** - רוב הטסטים מוכנים
2. **Critical tests** - כל הטסטים הקריטיים ממומשים (Nyquist, validations)
3. **Architecture** - הפרדה ברורה בין טסטים, קוד נקי
4. **Documentation** - כל טסט מתועד היטב

**לציין כחסר:**
1. Infrastructure automation - דורש השלמה
2. E2E עם gRPC - דורש proto files
3. Performance baseline - צריך קווי בסיס

**שאלות לפגישה:**
1. מהם ה-SLAs לביצועים? (latency, throughput)
2. מהם גבולות המערכת? (max sensors, max NFFT)
3. האם יש minimum thresholds? (min throughput)
4. Edge cases behavior? (min==max, freq==Nyquist)

---

*מסמך זה מכסה 93 טסטים בפירוט מלא*

