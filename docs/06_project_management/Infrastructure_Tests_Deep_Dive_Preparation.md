# מדריך מפורט לטסטים - הכנה מושלמת לפגישה
## בדיקות Infrastructure - ניתוח מקיף ומדריך יישום

---

## 📋 תוכן עניינים

1. [מבוא - סקירה כללית](#מבוא)
2. [טסט 1: SSH Access to Production Servers](#test-1-ssh)
3. [טסט 2: Kubernetes Cluster Connection](#test-2-kubernetes)
4. [טסט 3: MongoDB Direct Connection](#test-3-mongodb-connection)
5. [טסט 4: MongoDB Quick Response Time](#test-4-mongodb-performance)
6. [טסט 5: MongoDB via ConfigManager](#test-5-mongodb-config)
7. [טסט 6: MongoDB Direct TCP Authentication](#test-6-mongodb-tcp)
8. [סיכום ומטריצת השוואה](#summary)
9. [שאלות צפויות ותשובות](#qa)

---

<a name="מבוא"></a>
## 🎯 מבוא - סקירה כללית

### מה הקבוצה הזאת של טסטים?
**בדיקות Infrastructure (תשתית)** - טסטים שבודקים את שכבת התשתית שעליה רץ Focus Server.

### מדוע חשובים טסטים אלה?
Focus Server **לא עובד לבד**. הוא תלוי ב:
- **MongoDB** - לאחסון recordings, metadata, tasks
- **Kubernetes** - לניהול pods ו-orchestration
- **SSH** - לגישה ל-servers לצורכי troubleshooting
- **Network connectivity** - קישוריות רשת

**אם התשתית נכשלת - גם אפליקציה מושלמת לא תעבוד!**

### מטרת הבדיקות:
1. ✅ **Availability** - תשתית זמינה ונגישה
2. ✅ **Health Check** - כל הקומפוננטות בריאות
3. ✅ **Performance** - תשתית עונה מהר מספיק
4. ✅ **Configuration** - קונפיגורציות נטענות נכון
5. ✅ **Diagnostic Readiness** - אפשר לעשות troubleshooting

---

<a name="test-1-ssh"></a>
## 🔐 טסט 1: SSH Access to Production Servers

### 📌 פרטי הטסט

| פרמטר | ערך |
|-------|-----|
| **Issue Key** | PZ-13900 |
| **Priority** | High |
| **Component** | SSH Infrastructure |
| **Status** | Automated ✅ |
| **Test File** | `tests/integration/infrastructure/test_external_connectivity.py` |
| **Test Function** | `test_ssh_connection` |
| **Lines** | 304-364 |

---

### 🎯 מטרת הטסט

**מה הטסט בודק?**
הטסט מאמת שיש **גישת SSH תקינה** לשרתי production דרך **jump host** לצורכי:
- Troubleshooting (פתרון בעיות)
- Maintenance (תחזוקה)
- Log access (גישה ללוגים)
- Manual intervention (התערבות ידנית)
- Running k9s / kubectl (ניהול Kubernetes)

**למה זה קריטי?**
כאשר מתרחשת תקלה ב-production, הדרך היחידה לאבחן ולתקן היא דרך SSH!
- בלי SSH → לא יכול לראות לוגים
- בלי SSH → לא יכול להריץ kubectl
- בלי SSH → לא יכול לעשות debugging

---

### 📊 מה בדיוק בודקים? (שלב אחר שלב)

#### **Pre-Conditions (תנאים מוקדמים):**
1. Jump host רץ ב-`10.10.100.3`
2. Target host רץ ב-`10.10.100.113`
3. SSH keys או credentials זמינים
4. Network routing מאפשר SSH connections
5. Firewall rules מאפשרים SSH traffic

#### **Test Flow (זרימת הטסט):**

```
Test Client (מחשב הבדיקה)
    ↓
    SSH → Jump Host (10.10.100.3, user: root)
    ↓
    Execute commands: hostname, whoami, uptime
    ↓
    SSH → Target Host (10.10.100.113, user: prisma)
    ↓
    Execute commands: kubectl version, k9s version
    ↓
    ✅ SUCCESS - all connections work
```

#### **צעדי הטסט (15 Steps):**

| # | Action | Expected Result |
|---|--------|----------------|
| 1 | Import paramiko | Library imported successfully |
| 2 | Create SSH client | `ssh = paramiko.SSHClient()` |
| 3 | Set host key policy | `AutoAddPolicy()` set |
| 4 | Connect to jump host | Connection to 10.10.100.3 established |
| 5 | Execute `hostname` | Hostname returned successfully |
| 6 | Read stdout | Output captured |
| 7 | Check stderr | No errors |
| 8 | Execute `whoami` | Returns `root` |
| 9 | Execute `uptime` | System uptime returned |
| 10 | Close jump connection | Connection closed cleanly |
| 11 | Connect to target host | Connection to 10.10.100.113 established |
| 12 | Execute `kubectl version` | kubectl installed and working |
| 13 | Execute `k9s version` | k9s installed |
| 14 | Optional: List pods | `kubectl get pods -n panda` works |
| 15 | Close target connection | Connection closed |

#### **Expected Results (תוצאות מצופות):**
- ✅ Jump host (10.10.100.3) נגיש דרך SSH
- ✅ Target host (10.10.100.113) נגיש דרך SSH
- ✅ Commands מתבצעות בהצלחה בשני ה-hosts
- ✅ `kubectl` זמין ב-target host
- ✅ `k9s` זמין ב-target host
- ✅ אין authentication failures
- ✅ אין network timeouts
- ✅ Connection latency < 2 seconds

---

### 🔧 איך לממש את הטסט בקוד?

#### **Architecture Approach:**

**גישה 1: Paramiko (מומלץ)**
```
Pros:
✅ Pure Python SSH client
✅ קל לשימוש
✅ תומך בכל features של SSH
✅ Exception handling טוב

Cons:
⚠️ צריך credentials או SSH keys
⚠️ צריך לטפל בהזמנות certificates
```

**גישה 2: Subprocess + ssh command**
```
Pros:
✅ משתמש ב-SSH native של OS
✅ פשוט מאוד

Cons:
⚠️ לא cross-platform
⚠️ קשה יותר לטפל בשגיאות
⚠️ תלוי ב-SSH configuration מקומית
```

**המלצה: Paramiko** - יותר reliable ו-cross-platform

---

#### **Implementation Pattern:**

```python
# File: tests/integration/infrastructure/test_external_connectivity.py

import paramiko
import pytest
from config.config_manager import ConfigManager

class TestExternalServicesConnectivity:
    """
    Test suite for external infrastructure connectivity validation.
    Validates SSH access to production servers.
    """
    
    @pytest.mark.ssh
    @pytest.mark.infrastructure
    @pytest.mark.critical
    def test_ssh_connection(self, config_manager):
        """
        Test SSH connectivity to jump host and target host.
        
        Purpose:
        - Validate SSH access for troubleshooting
        - Ensure kubectl and k9s are available
        - Verify network connectivity
        
        Steps:
        1. Connect to jump host
        2. Execute basic commands
        3. Connect to target host  
        4. Verify kubectl/k9s availability
        
        Expected:
        - All connections successful
        - Commands execute without errors
        - Latency < 2 seconds
        """
        
        # 1. Get SSH configuration
        ssh_config = config_manager.get_ssh_config()
        jump_host = ssh_config['jump_host']
        target_host = ssh_config['target_host']
        
        # 2. Test Jump Host Connection
        jump_client = self._create_ssh_client()
        try:
            # Connect with timeout
            jump_client.connect(
                hostname=jump_host['ip'],  # 10.10.100.3
                username=jump_host['username'],  # root
                password=jump_host['password'],
                timeout=5
            )
            
            # Execute test commands
            commands = ['hostname', 'whoami', 'uptime']
            for cmd in commands:
                stdin, stdout, stderr = jump_client.exec_command(cmd)
                output = stdout.read().decode().strip()
                error = stderr.read().decode().strip()
                
                assert output, f"Command '{cmd}' returned empty output"
                assert not error, f"Command '{cmd}' returned error: {error}"
                
        finally:
            jump_client.close()
        
        # 3. Test Target Host Connection
        target_client = self._create_ssh_client()
        try:
            target_client.connect(
                hostname=target_host['ip'],  # 10.10.100.113
                username=target_host['username'],  # prisma
                password=target_host['password'],
                timeout=5
            )
            
            # Verify kubectl availability
            stdin, stdout, stderr = target_client.exec_command('kubectl version --client')
            kubectl_output = stdout.read().decode()
            assert 'Client Version' in kubectl_output, "kubectl not available"
            
            # Verify k9s availability
            stdin, stdout, stderr = target_client.exec_command('k9s version')
            k9s_output = stdout.read().decode()
            assert 'Version' in k9s_output, "k9s not available"
            
        finally:
            target_client.close()
    
    def _create_ssh_client(self):
        """Helper method to create SSH client with proper settings."""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return client
```

#### **Dependencies:**
```python
# requirements.txt
paramiko>=3.0.0
pytest>=7.0.0
```

#### **Configuration (environments.yaml):**
```yaml
new_production:
  ssh:
    jump_host:
      ip: "10.10.100.3"
      username: "root"
      password: "***"  # From secrets
    target_host:
      ip: "10.10.100.113"
      username: "prisma"
      password: "***"  # From secrets
```

---

### ❓ שאלות צפויות לטסט זה + תשובות

#### **שאלה 1: למה צריך Jump Host? למה לא ישר ל-Target Host?**
**תשובה:**
```
Security best practice!
- Production servers לא חשופים ישירות לאינטרנט
- Jump host הוא bastion/gateway מאובטח
- מאפשר audit trail (לוג של מי נכנס)
- מקל על ניהול firewall rules
```

#### **שאלה 2: מה קורה אם SSH נכשל?**
**תשובה:**
```
תרחישים אפשריים:
1. Network issue → לא מגיעים ל-jump host
2. Authentication failure → credentials שגויים
3. Firewall blocking → port 22 חסום
4. Target host down → server לא רץ

Action:
- בדוק connectivity (ping)
- בדוק credentials
- בדוק firewall rules
- בדוק logs ב-jump host
```

#### **שאלה 3: איך מטפלים ב-SSH keys במקום passwords?**
**תשובה:**
```python
# Instead of password, use key_filename:
client.connect(
    hostname=host_ip,
    username=username,
    key_filename='/path/to/private_key',
    timeout=5
)

# Or use SSH agent:
import paramiko.agent
agent = paramiko.agent.Agent()
agent_keys = agent.get_keys()
```

#### **שאלה 4: מה ה-timeout אופטימלי?**
**תשובה:**
```
Recommended: 5-10 seconds
- יותר מדי קצר → false negatives (network hiccup)
- יותר מדי ארוך → טסט איטי

באוטומציה: 5 seconds
במניטורינג: 10 seconds
```

#### **שאלה 5: איך בודקים שה-SSH session לא נשאר תקוע?**
**תשובה:**
```python
# Always use try-finally or context manager:
try:
    client.connect(...)
    # Do work
finally:
    client.close()  # Always close!

# Or better - context manager:
with paramiko.SSHClient() as client:
    client.connect(...)
    # Work here
# Auto-closes
```

---

### 📈 קריטריוני הצלחה

| Metric | Threshold | סיבה |
|--------|-----------|------|
| Connection latency | < 2s | חיוני ל-troubleshooting מהיר |
| Authentication | 100% success | אי אפשר לאבד גישה |
| Command execution | 100% success | צריך לבצע פקודות |
| kubectl availability | 100% | חיוני לניהול K8s |

---

<a name="test-2-kubernetes"></a>
## ☸️ טסט 2: Kubernetes Cluster Connection and Pod Health Check

### 📌 פרטי הטסט

| פרמטר | ערך |
|-------|-----|
| **Issue Key** | PZ-13899 |
| **Priority** | High |
| **Component** | Kubernetes Infrastructure |
| **Status** | Automated ✅ |
| **Test File** | `tests/integration/infrastructure/test_external_connectivity.py` |
| **Test Function** | `test_kubernetes_connection` |
| **Lines** | 172-219 |

---

### 🎯 מטרת הטסט

**מה הטסט בודק?**
הטסט מאמת:
1. **קישוריות ל-Kubernetes cluster** API server
2. **גילוי Focus Server pods** והסטטוס שלהם
3. **בריאות (health) של pods** - Running ו-Ready
4. **זמינות services** ונכונות ה-configuration

**למה זה קריטי?**
Focus Server רץ ב-Kubernetes pods. אם:
- K8s cluster לא נגיש → לא יודע מצב המערכת
- Pods לא רצים → המערכת לא עובדת
- Pods restart הרבה → יש בעיה יציבות
- Services לא קיימים → לא יכול להגיע ל-API

**Operational Visibility** - חייבים לדעת מה קורה ב-production!

---

### 📊 מה בדיוק בודקים?

#### **Pre-Conditions:**
1. Kubernetes cluster רץ
2. API Server נגיש ב-`https://10.10.100.102:6443`
3. kubeconfig או service account credentials זמינים
4. Namespace `panda` קיים
5. Focus Server deployed ב-namespace
6. Network מאפשר חיבור ל-K8s API

#### **Test Data:**

**Cluster Details:**
```yaml
API Server: https://10.10.100.102:6443
Namespace: panda
Expected Deployment: panda-panda-focus-server
Expected Service: panda-panda-focus-server.panda:5000
```

**Expected Pods:**
```
- Pattern: panda-panda-focus-server-*
- Min count: 1
- Status: Running
- Ready: True
```

**Expected Services:**
```
Name: panda-panda-focus-server
Type: ClusterIP
ClusterIP: 10.43.103.101
Port: 5000
```

#### **צעדי הטסט (16 Steps):**

| # | Action | Expected Result |
|---|--------|----------------|
| 1 | Import kubernetes library | `from kubernetes import client, config` |
| 2 | Load kubeconfig | Config loaded successfully |
| 3 | Create API client | `v1 = client.CoreV1Api()` |
| 4 | Get cluster version | Version info (e.g., v1.25.x) |
| 5 | List namespaces | Namespace list returned |
| 6 | Verify `panda` namespace | `'panda' in namespaces` = True |
| 7 | List pods in `panda` | Pod list returned |
| 8 | Filter Focus Server pods | At least 1 pod found |
| 9 | Check pod status | Status = `Running` |
| 10 | Check pod readiness | `ready` condition = True |
| 11 | Check restart count | Restart count < 5 |
| 12 | List services | Service list returned |
| 13 | Verify service exists | `panda-panda-focus-server` found |
| 14 | Verify ClusterIP | ClusterIP = `10.43.103.101` |
| 15 | Verify port | Port = `5000` |
| 16 | Get pod logs (optional) | Last 10 lines accessible |

---

### 🔧 איך לממש את הטסט בקוד?

#### **Architecture Approach:**

**גישה 1: kubernetes-python library (מומלץ)**
```
Pros:
✅ Official K8s Python client
✅ תומך בכל K8s APIs
✅ Type-safe וטוב documented
✅ אוטומטי load kubeconfig

Cons:
⚠️ צריך kubeconfig מוכן
⚠️ קצת verbose
```

**גישה 2: kubectl subprocess**
```
Pros:
✅ פשוט מאוד
✅ משתמש ב-kubectl native

Cons:
⚠️ צריך kubectl מותקן
⚠️ קשה לפרסר output
⚠️ לא type-safe
```

**גישה 3: REST API ישיר**
```
Pros:
✅ מלא שליטה

Cons:
⚠️ צריך לטפל ב-authentication
⚠️ הרבה boilerplate
```

**המלצה: kubernetes-python** - הכי robust ו-production-ready

---

#### **Implementation Pattern:**

```python
# File: tests/integration/infrastructure/test_external_connectivity.py

from kubernetes import client, config
from kubernetes.client.rest import ApiException
import pytest

class TestExternalServicesConnectivity:
    """
    Test suite for Kubernetes cluster connectivity and pod health validation.
    """
    
    @pytest.mark.kubernetes
    @pytest.mark.infrastructure
    @pytest.mark.high_priority
    def test_kubernetes_connection(self, config_manager):
        """
        Test Kubernetes cluster connection and Focus Server pod health.
        
        Purpose:
        - Validate K8s cluster accessibility
        - Verify Focus Server pods are running
        - Check pod health and readiness
        - Verify services are configured correctly
        
        Steps:
        1. Load kubeconfig and create API client
        2. Verify cluster connection (get version)
        3. Verify namespace exists
        4. List and validate Focus Server pods
        5. Check pod status and health
        6. Verify service configuration
        
        Expected:
        - Cluster accessible
        - At least 1 Focus Server pod running
        - All pods Ready
        - Service configured correctly
        """
        
        # 1. Load Kubernetes configuration
        try:
            # Try in-cluster config first (if running in K8s)
            config.load_incluster_config()
        except:
            # Fall back to kubeconfig
            config.load_kube_config()
        
        # 2. Create API client
        v1 = client.CoreV1Api()
        
        # 3. Test cluster connection - get version
        try:
            version_info = v1.get_api_resources()
            logger.info(f"✅ K8s cluster accessible")
        except ApiException as e:
            pytest.fail(f"Cannot connect to K8s cluster: {e}")
        
        # 4. Verify namespace 'panda' exists
        namespaces = v1.list_namespace()
        namespace_names = [ns.metadata.name for ns in namespaces.items]
        assert 'panda' in namespace_names, "Namespace 'panda' not found"
        
        # 5. List pods in 'panda' namespace
        pods = v1.list_namespaced_pod(namespace='panda')
        
        # 6. Filter Focus Server pods
        focus_server_pods = [
            pod for pod in pods.items
            if 'panda-panda-focus-server' in pod.metadata.name
        ]
        
        assert len(focus_server_pods) > 0, "No Focus Server pods found"
        logger.info(f"Found {len(focus_server_pods)} Focus Server pods")
        
        # 7. Check each pod's health
        for pod in focus_server_pods:
            pod_name = pod.metadata.name
            
            # Check status
            phase = pod.status.phase
            assert phase == 'Running', f"Pod {pod_name} not Running (status: {phase})"
            
            # Check readiness
            conditions = pod.status.conditions
            ready_condition = next(
                (c for c in conditions if c.type == 'Ready'),
                None
            )
            assert ready_condition is not None, f"Pod {pod_name} has no Ready condition"
            assert ready_condition.status == 'True', f"Pod {pod_name} not Ready"
            
            # Check restart count
            restart_count = sum(
                container.restart_count
                for container in pod.status.container_statuses
            )
            assert restart_count < 5, f"Pod {pod_name} has high restart count: {restart_count}"
            
            logger.info(f"✅ Pod {pod_name}: Running, Ready, Restarts: {restart_count}")
        
        # 8. Verify service exists
        services = v1.list_namespaced_service(namespace='panda')
        service_names = [svc.metadata.name for svc in services.items]
        
        assert 'panda-panda-focus-server' in service_names, "Focus Server service not found"
        
        # 9. Get service details
        service = v1.read_namespaced_service(
            name='panda-panda-focus-server',
            namespace='panda'
        )
        
        # Verify ClusterIP
        cluster_ip = service.spec.cluster_ip
        assert cluster_ip == '10.43.103.101', f"Unexpected ClusterIP: {cluster_ip}"
        
        # Verify port
        ports = service.spec.ports
        assert len(ports) > 0, "Service has no ports"
        assert ports[0].port == 5000, f"Unexpected port: {ports[0].port}"
        
        logger.info(f"✅ Service configured correctly: {cluster_ip}:5000")
```

#### **Dependencies:**
```python
# requirements.txt
kubernetes>=28.0.0
pytest>=7.0.0
```

#### **Kubeconfig Setup:**
```bash
# Option 1: Use existing kubeconfig
export KUBECONFIG=~/.kube/config

# Option 2: Get kubeconfig from cluster
scp prisma@10.10.100.113:~/.kube/config ~/.kube/config

# Option 3: Service account (for in-cluster)
# Automatically loaded when running inside K8s
```

---

### ❓ שאלות צפויות + תשובות

#### **שאלה 1: מה זה Pod? מה זה Deployment?**
**תשובה:**
```
Pod:
- יחידת ריצה בסיסית ב-Kubernetes
- מכולה אחת או יותר (containers)
- כתובת IP משלה
- lifecycle: pending → running → succeeded/failed

Deployment:
- מנהל replicas של pods
- מגדיר כמה pods צריכים לרוץ
- מבטיח שהם רצים (self-healing)
- מאפשר rolling updates

דוגמה:
Deployment: panda-panda-focus-server (מגדיר 2 replicas)
    ↓
Pod 1: panda-panda-focus-server-abc123
Pod 2: panda-panda-focus-server-def456
```

#### **שאלה 2: מה זה Ready condition? למה זה חשוב?**
**תשובה:**
```
Ready Condition:
- סטטוס שמראה ש-pod מוכן לקבל traffic
- נקבע ע"י readiness probes

Pod יכול להיות Running אבל לא Ready!
- Running = containers רצים
- Ready = אפליקציה מוכנה לעבוד

דוגמה:
Pod Status: Running
Ready Condition: False
  ↓
המשמעות: Pod רץ אבל אפליקציה עדיין loading
Service לא ישלח traffic ל-pod הזה!
```

#### **שאלה 3: מה Restart Count סביר?**
**תשובה:**
```
Restart Count Thresholds:
0-2: ✅ מצוין (restarts ספורדיים)
3-5: ⚠️ סביר (אולי deployment issues)
6-10: ❌ בעייתי (instability)
>10: ❌ קריטי (crash loop)

סיבות ל-restarts:
- OOMKilled (out of memory)
- Application crash
- Failed liveness probe
- Node issues

Action:
kubectl logs <pod> --previous  # לראות מה קרה
```

#### **שאלה 4: מה ההבדל בין ClusterIP לבין LoadBalancer?**
**תשובה:**
```
Service Types:

ClusterIP (internal):
- כתובת IP פנימית בתוך cluster
- נגיש רק מתוך K8s
- שימוש: תקשורת פנימית בין services
- דוגמה: 10.43.103.101:5000

LoadBalancer (external):
- חושף service לעולם החיצון
- מקבל IP חיצוני
- שימוש: גישה מבחוץ
- דוגמה: 10.10.100.100:443

במקרה שלנו:
- ClusterIP: תקשורת פנימית
- LoadBalancer: גישה external ל-Focus Server
```

#### **שאלה 5: איך בודקים pod logs?**
**תשובה:**
```python
# Get last 10 lines of logs:
logs = v1.read_namespaced_pod_log(
    name=pod_name,
    namespace='panda',
    tail_lines=10
)
print(logs)

# Get logs from previous crashed container:
logs = v1.read_namespaced_pod_log(
    name=pod_name,
    namespace='panda',
    previous=True
)

# Stream logs in real-time:
from kubernetes.watch import Watch
w = Watch()
for line in w.stream(v1.read_namespaced_pod_log, 
                      name=pod_name, 
                      namespace='panda'):
    print(line)
```

---

### 📈 קריטריוני הצלחה

| Metric | Threshold | סיבה |
|--------|-----------|------|
| Cluster accessible | 100% | חובה לניהול |
| Pods running | ≥1 | חובה לשרות |
| Pods ready | 100% | חובה ל-traffic |
| Restart count | <5 | סימן יציבות |
| Service exists | 100% | חובה ל-routing |

---

<a name="test-3-mongodb-connection"></a>
## 🍃 טסט 3: MongoDB Direct Connection and Health Check

### 📌 פרטי הטסט

| פרמטר | ערך |
|-------|-----|
| **Issue Key** | PZ-13898 |
| **Priority** | High |
| **Component** | MongoDB Infrastructure |
| **Status** | Automated ✅ |
| **Test File** | `tests/integration/infrastructure/test_external_connectivity.py` |
| **Test Function** | `test_mongodb_connection` |
| **Lines** | 68-125 |

---

### 🎯 מטרת הטסט

**מה הטסט בודק?**
הטסט מאמת **קישוריות ישירה ל-MongoDB** ו**בריאות מסד הנתונים**:
1. TCP connection ל-MongoDB server
2. Authentication (אימות)
3. Ping command (בדיקת תקשורת)
4. Database existence (קיום מסד נתונים)
5. Collections existence (קיום טבלאות)
6. Basic queries (שאילתות בסיסיות)

**למה זה קריטי?**
MongoDB הוא ה**מקור האמת** (source of truth) ב-Focus Server:
- אחסון recordings metadata
- אחסון tasks ו-configurations
- Query capabilities לhistoric playback

**Isolation Test** - בודקים MongoDB לבד, מבודד מ-Focus Server.
אם MongoDB נכשל → Focus Server לא יעבוד!

---

### 📊 מה בדיוק בודקים?

#### **Pre-Conditions:**
1. MongoDB deployed ורץ
2. MongoDB LoadBalancer service חשוף ב-`10.10.100.108:27017`
3. Credentials זמינים: `username=prisma, password=prisma`
4. Database `prisma` קיים
5. Network routing מאפשר חיבור ל-MongoDB

#### **Test Data:**

**Connection String:**
```
mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma
```

**Expected Database:** `prisma`

**Expected Collections:**
- `recordings` - רשימת recordings זמינים
- `tasks` - מידע על tasks ריצה
- `metadata` - metadata של recordings
- `node4` - נתונים היסטוריים

#### **צעדי הטסט (14 Steps):**

| # | Action | Expected Result |
|---|--------|----------------|
| 1 | Import pymongo | Library imported |
| 2 | Create connection string | Connection string built |
| 3 | TCP connection | Socket connection established |
| 4 | Create MongoClient | Client object created |
| 5 | Authenticate | Authentication successful |
| 6 | Ping command | `{'ok': 1}` returned |
| 7 | List databases | Database list returned |
| 8 | Verify `prisma` DB | `'prisma' in databases` |
| 9 | Connect to DB | DB object created |
| 10 | List collections | Collection list returned |
| 11 | Verify collections | All 4 collections exist |
| 12 | Simple query | Query executes |
| 13 | Measure latency | Latency < 100ms |
| 14 | Close connection | Connection closed cleanly |

---

### 🔧 איך לממש את הטסט בקוד?

#### **Architecture Approach:**

**גישה 1: pymongo (מומלץ)**
```
Pros:
✅ Official MongoDB Python driver
✅ מלא features
✅ Connection pooling
✅ Retry logic

Cons:
⚠️ צריך credentials נכונים
```

**גישה 2: Motor (async)**
```
Pros:
✅ Async/await support
✅ טוב ל-high concurrency

Cons:
⚠️ מורכב יותר
⚠️ לא נחוץ לטסטים
```

**המלצה: pymongo** - פשוט, robust, synchronous

---

#### **Implementation Pattern:**

```python
# File: tests/integration/infrastructure/test_external_connectivity.py

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import pytest
import time

class TestExternalServicesConnectivity:
    """
    Test suite for MongoDB connectivity and health validation.
    """
    
    @pytest.mark.mongodb
    @pytest.mark.infrastructure
    @pytest.mark.high_priority
    def test_mongodb_connection(self, config_manager):
        """
        Test MongoDB direct connection and health check.
        
        Purpose:
        - Validate TCP connection to MongoDB
        - Verify authentication works
        - Check database and collections exist
        - Validate query capability
        - Measure connection latency
        
        This is an isolation test - MongoDB is tested independently
        from Focus Server to diagnose infrastructure issues.
        
        Steps:
        1. Create MongoDB client
        2. Test connection with ping
        3. Verify database exists
        4. Verify collections exist
        5. Test query execution
        6. Measure latency
        
        Expected:
        - Connection successful
        - Authentication passes
        - Database 'prisma' exists
        - All required collections exist
        - Latency < 100ms
        """
        
        # 1. Get MongoDB configuration
        mongo_config = config_manager.get_database_config()
        
        # 2. Build connection string
        connection_string = (
            f"mongodb://{mongo_config['username']}:{mongo_config['password']}"
            f"@{mongo_config['host']}:{mongo_config['port']}"
            f"/?authSource={mongo_config['auth_source']}"
        )
        
        # 3. Create MongoClient with timeouts
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=10000,  # 10 seconds
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        try:
            # 4. Test connection - ping command
            start_time = time.time()
            ping_result = client.admin.command('ping')
            latency_ms = (time.time() - start_time) * 1000
            
            assert ping_result['ok'] == 1.0, "Ping failed"
            assert latency_ms < 100, f"Ping latency too high: {latency_ms:.2f}ms"
            logger.info(f"✅ MongoDB ping: {latency_ms:.2f}ms")
            
            # 5. List all databases
            db_list = client.list_database_names()
            assert len(db_list) > 0, "No databases found"
            logger.info(f"Databases found: {db_list}")
            
            # 6. Verify 'prisma' database exists
            assert 'prisma' in db_list, "Database 'prisma' not found"
            
            # 7. Connect to prisma database
            db = client['prisma']
            
            # 8. List all collections
            collections = db.list_collection_names()
            logger.info(f"Collections found: {collections}")
            
            # 9. Verify required collections
            required_collections = ['recordings', 'tasks', 'metadata', 'node4']
            for collection_name in required_collections:
                assert collection_name in collections, \
                    f"Collection '{collection_name}' not found"
            
            logger.info(f"✅ All {len(required_collections)} required collections exist")
            
            # 10. Test simple query on 'recordings'
            recordings_collection = db['recordings']
            sample_recording = recordings_collection.find_one()
            
            # Note: sample_recording can be None if collection is empty
            # That's OK - we're just testing query capability
            logger.info(f"Query test: {'✅ Success' if sample_recording is not None else '✅ Query works (empty collection)'}")
            
            # 11. Verify collection schemas (optional deep check)
            if sample_recording:
                # Validate expected fields
                expected_fields = ['uuid', 'start_time', 'end_time']
                for field in expected_fields:
                    assert field in sample_recording, \
                        f"Field '{field}' missing in recording document"
            
        except ConnectionFailure as e:
            pytest.fail(f"MongoDB connection failed: {e}")
        except ServerSelectionTimeoutError as e:
            pytest.fail(f"MongoDB server selection timeout: {e}")
        finally:
            # 12. Always close connection
            client.close()
            logger.info("✅ MongoDB connection closed")
```

#### **Dependencies:**
```python
# requirements.txt
pymongo>=4.0.0
pytest>=7.0.0
```

#### **Configuration (environments.yaml):**
```yaml
new_production:
  mongodb:
    host: "10.10.100.108"
    port: 27017
    username: "prisma"
    password: "prisma"
    database: "prisma"
    auth_source: "prisma"
```

---

### ❓ שאלות צפויות + תשובות

#### **שאלה 1: מה זה authSource? למה צריך את זה?**
**תשובה:**
```
authSource = מסד נתונים שבו נמצאות credentials למשתמש

דוגמה:
mongodb://prisma:prisma@host:27017/?authSource=prisma
                                      ↑
                            Authentication DB

למה צריך?
- MongoDB מאחסן users ב-DB נפרד
- בדרך כלל: 'admin' (default)
- במקרה שלנו: 'prisma' (custom)

בלי authSource נכון → Authentication יכשל!
```

#### **שאלה 2: מה הכוונה ב-Ping latency < 100ms?**
**תשובה:**
```
Ping Latency = זמן שלוקח ל-ping command לחזור

Thresholds:
- <10ms: מצוין (local network)
- 10-50ms: טוב (same datacenter)
- 50-100ms: סביר (acceptable)
- >100ms: בעייתי (network issues)

במקרה שלנו:
- MongoDB ב-K8s cluster
- Test client external
- 100ms = threshold סביר

Action אם latency גבוה:
- Check network
- Check MongoDB load
- Check disk I/O
```

#### **שאלה 3: מה קורה אם Collection ריק?**
**תשובה:**
```
find_one() על collection ריק:
- Returns: None
- לא זורק exception!

זה בסדר לטסט:
✅ אנחנו בודקים שה-query עובד
✅ לא בודקים שיש data

אם רוצים להבטיח data:
assert sample_recording is not None, "Collection is empty"

אבל: ב-fresh deployment אפשר collection ריק
```

#### **שאלה 4: איך בודקים MongoDB schema?**
**תשובה:**
```python
# Sample a document and check fields:
sample = collection.find_one()

if sample:
    # Check required fields
    assert 'uuid' in sample
    assert 'start_time' in sample
    assert 'end_time' in sample
    
    # Check data types
    assert isinstance(sample['uuid'], str)
    assert isinstance(sample['start_time'], (int, float))
    
    # Check value validity
    assert sample['start_time'] < sample['end_time']

# Or use MongoDB schema validation:
db.command({
    "collMod": "recordings",
    "validator": {
        "$jsonSchema": {
            "required": ["uuid", "start_time", "end_time"]
        }
    }
})
```

#### **שאלה 5: מה ההבדל בין הטסט הזה לבין Functional Test?**
**תשובה:**
```
Infrastructure Test (הטסט הזה):
- בודק MongoDB **לבד**
- בידוד מ-Focus Server
- Diagnose: האם MongoDB בריא?
- שאלה: "האם התשתית עובדת?"

Functional Test:
- בודק Focus Server **עם** MongoDB
- אינטגרציה מלאה
- Diagnose: האם האפליקציה עובדת?
- שאלה: "האם הפיצ'ר עובד?"

Example Flow:
1. Infrastructure Test fails → בעיה ב-MongoDB
2. Infrastructure Test passes + Functional Test fails → בעיה ב-Focus Server
```

---

### 📈 קריטריוני הצלחה

| Metric | Threshold | סיבה |
|--------|-----------|------|
| Connection success | 100% | חובה לכל פעולה |
| Ping latency | <100ms | חיוני לביצועים |
| Authentication | 100% success | אבטחה וגישה |
| Collections exist | 100% | חובה ל-queries |

---

<a name="test-4-mongodb-performance"></a>
## ⚡ טסט 4: MongoDB Quick Response Time Test (Performance)

### 📌 פרטי הטסט

| פרמטר | ערך |
|-------|-----|
| **Issue Key** | PZ-13808 |
| **Priority** | Medium |
| **Component** | MongoDB Performance |
| **Status** | Implemented ✅ |
| **Test File** | `tests/integration/infrastructure/test_basic_connectivity.py` |
| **Test Function** | `test_quick_mongodb_ping` |

---

### 🎯 מטרת הטסט

**מה הטסט בודק?**
הטסט בודק **זמן תגובה (response time)** של MongoDB תחת תנאי עומס רגילים.

**למה זה קריטי?**
MongoDB איטי → Focus Server איטי → משתמשים לא מרוצים!

Performance criteria:
- **Excellent**: <50ms
- **Acceptable**: 50-100ms
- **Problem**: >100ms

**זה לא בדיקת functionality - זה בדיקת ביצועים!**

---

### 📊 מה בדיוק בודקים?

#### **Test Data:**
```json
{
  "max_response_time_ms": 100,
  "acceptable_response_time_ms": 50
}
```

#### **צעדי הטסט (7 Steps):**

| # | Action | Data | Expected |
|---|--------|------|----------|
| 1 | Connect to MongoDB | Connection string | Connected |
| 2 | Record start time | `time.time()` | Timestamp captured |
| 3 | Send ping command | `client.admin.command('ping')` | Response received |
| 4 | Record end time | `time.time()` | Timestamp captured |
| 5 | Calculate latency | `(end - start) * 1000` | Latency in ms |
| 6 | Verify threshold | `latency < 100ms` | Pass/Fail |
| 7 | Log result | Latency value | Logged |

---

### 🔧 איך לממש את הטסט בקוד?

```python
# File: tests/integration/infrastructure/test_basic_connectivity.py

import time
import pytest
from pymongo import MongoClient

class TestMongoDBPerformance:
    """
    Performance tests for MongoDB infrastructure.
    """
    
    @pytest.mark.mongodb
    @pytest.mark.performance
    @pytest.mark.infrastructure
    def test_quick_mongodb_ping(self, config_manager):
        """
        Test MongoDB ping response time under normal load.
        
        Purpose:
        - Ensure MongoDB responds quickly
        - Detect performance degradation
        - Monitor database health
        
        Performance Criteria:
        - Excellent: <50ms
        - Acceptable: 50-100ms
        - Unacceptable: >100ms
        
        Expected:
        - Ping latency < 100ms
        - Consistent performance
        """
        
        # 1. Get MongoDB config
        mongo_config = config_manager.get_database_config()
        
        # 2. Create client
        client = MongoClient(
            host=mongo_config['host'],
            port=mongo_config['port'],
            username=mongo_config['username'],
            password=mongo_config['password'],
            authSource=mongo_config.get('auth_source', 'admin')
        )
        
        try:
            # 3. Measure ping time
            start_time = time.time()
            ping_result = client.admin.command('ping')
            end_time = time.time()
            
            # 4. Calculate latency in milliseconds
            latency_ms = (end_time - start_time) * 1000
            
            # 5. Assertions
            assert ping_result['ok'] == 1.0, "Ping failed"
            assert latency_ms < 100, f"MongoDB ping too slow: {latency_ms:.2f}ms"
            
            # 6. Log performance
            logger.info(f"✅ MongoDB ping: {latency_ms:.2f}ms")
            
            # 7. Performance classification
            if latency_ms < 50:
                logger.info("⚡ Excellent latency!")
            elif latency_ms < 100:
                logger.info("✓ Acceptable latency")
            else:
                logger.warning("⚠️ High latency detected!")
                
        finally:
            client.close()
```

---

### ❓ שאלות צפויות + תשובות

#### **שאלה 1: למה בודקים ping ולא query אמיתי?**
**תשובה:**
```
Ping Command:
✅ קל מאוד (minimal overhead)
✅ בודק network + authentication + basic health
✅ consistent (לא תלוי ב-data)
✅ מהיר לרוץ

Real Query:
⚠️ תלוי ב-data size
⚠️ תלוי באינדקסים
⚠️ לא consistent
⚠️ משפיע על production

Ping = baseline performance
```

#### **שאלה 2: מה אם ה-latency משתנה הרבה בין runs?**
**תשובה:**
```
Latency Variability:
- Normal: ±10-20ms
- Problem: ±50ms+

סיבות ל-variability:
- Network congestion
- MongoDB load
- Disk I/O
- Background tasks (compaction, backups)

פתרון:
# Run multiple pings and take median:
latencies = []
for _ in range(5):
    start = time.time()
    client.admin.command('ping')
    latencies.append((time.time() - start) * 1000)

median_latency = statistics.median(latencies)
p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
```

#### **שאלה 3: איך מזהים performance degradation לאורך זמן?**
**תשובה:**
```
Monitoring Strategy:

1. Baseline Measurement:
   - Run test multiple times
   - Record median: ~15ms (example)

2. Continuous Monitoring:
   - Run every hour
   - Track trend

3. Alerting:
   - If latency > 2x baseline → Warning
   - If latency > 100ms → Critical

4. Historical Data:
   - Store in time-series DB
   - Visualize trends
   - Correlate with changes

Tools:
- Prometheus + Grafana
- CloudWatch
- Datadog
```

---

### 📈 קריטריוני הצלחה

| Latency Range | Classification | Action |
|--------------|----------------|--------|
| <50ms | ⚡ Excellent | None |
| 50-100ms | ✅ Acceptable | Monitor |
| 100-200ms | ⚠️ Warning | Investigate |
| >200ms | ❌ Critical | Immediate action |

---

<a name="test-5-mongodb-config"></a>
## ⚙️ טסט 5: MongoDB Connection Using Focus Server Config

### 📌 פרטי הטסט

| פרמטר | ערך |
|-------|-----|
| **Issue Key** | PZ-13807 |
| **Priority** | High |
| **Component** | ConfigManager, MongoDB |
| **Status** | Implemented ✅ |
| **Test File** | `tests/integration/infrastructure/test_basic_connectivity.py` |
| **Test Function** | `test_mongodb_connection` |

---

### 🎯 מטרת הטסט

**מה הטסט בודק?**
הטסט מאמת ש**ConfigManager טוען נכון את MongoDB configuration** ושהחיבור עובד.

**למה זה קריטי?**
Focus Server משתמש ב-ConfigManager לניהול כל ה-configs:
- MongoDB credentials
- API endpoints
- Timeouts
- Environments (dev, staging, production)

**אם ConfigManager לא טוען נכון → Focus Server יכשל בהתחלה!**

---

### 📊 מה בדיוק בודקים?

#### **Test Data (environments.yaml):**
```yaml
new_production:
  mongodb:
    host: "10.10.100.108"
    port: 27017
    username: "prisma"
    password: "prisma"
    database: "prisma"
    auth_source: "prisma"
```

#### **צעדי הטסט (6 Steps):**

| # | Action | Data | Expected |
|---|--------|------|----------|
| 1 | Initialize ConfigManager | `env="new_production"` | Manager created |
| 2 | Get database config | `get_database_config()` | Config dict returned |
| 3 | Verify host | `config["host"]` | `"10.10.100.108"` |
| 4 | Verify port | `config["port"]` | `27017` |
| 5 | Create MongoDB client | Using config | Client created |
| 6 | Test connection | `ping` | Success |

---

### 🔧 איך לממש את הטסט בקוד?

```python
# File: tests/integration/infrastructure/test_basic_connectivity.py

import pytest
from pymongo import MongoClient
from config.config_manager import ConfigManager

class TestConfigManagerMongoDB:
    """
    Test MongoDB connection through ConfigManager.
    Validates configuration loading and connection establishment.
    """
    
    @pytest.mark.mongodb
    @pytest.mark.config
    @pytest.mark.high_priority
    def test_mongodb_connection_via_config_manager(self):
        """
        Test MongoDB connection using Focus Server's ConfigManager.
        
        Purpose:
        - Validate ConfigManager loads MongoDB config correctly
        - Ensure all connection parameters are accurate
        - Test connection using loaded config
        
        This test validates the configuration layer that Focus Server
        uses. If this fails, Focus Server won't start properly.
        
        Steps:
        1. Initialize ConfigManager for environment
        2. Load MongoDB configuration
        3. Validate each config parameter
        4. Create MongoDB client using config
        5. Test connection with ping
        
        Expected:
        - ConfigManager loads config successfully
        - All parameters match expected values
        - Connection successful
        """
        
        # 1. Initialize ConfigManager
        config_manager = ConfigManager("new_production")
        
        # 2. Get MongoDB configuration
        mongo_config = config_manager.get_database_config()
        
        # 3. Validate configuration parameters
        assert 'host' in mongo_config, "Missing 'host' in config"
        assert 'port' in mongo_config, "Missing 'port' in config"
        assert 'username' in mongo_config, "Missing 'username' in config"
        assert 'password' in mongo_config, "Missing 'password' in config"
        assert 'database' in mongo_config, "Missing 'database' in config"
        
        # 4. Validate specific values
        assert mongo_config['host'] == "10.10.100.108", \
            f"Unexpected host: {mongo_config['host']}"
        assert mongo_config['port'] == 27017, \
            f"Unexpected port: {mongo_config['port']}"
        assert mongo_config['database'] == "prisma", \
            f"Unexpected database: {mongo_config['database']}"
        
        logger.info("✅ ConfigManager loaded MongoDB config correctly")
        logger.info(f"  Host: {mongo_config['host']}")
        logger.info(f"  Port: {mongo_config['port']}")
        logger.info(f"  Database: {mongo_config['database']}")
        
        # 5. Create MongoDB client using config
        # Option A: Manual connection string
        client = MongoClient(
            host=mongo_config['host'],
            port=mongo_config['port'],
            username=mongo_config['username'],
            password=mongo_config['password'],
            authSource=mongo_config.get('auth_source', 'admin')
        )
        
        # Option B: Using **kwargs unpacking (if config matches MongoClient params)
        # client = MongoClient(**mongo_config)
        
        try:
            # 6. Test connection with ping
            ping_result = client.admin.command('ping')
            assert ping_result['ok'] == 1.0, "Ping failed"
            
            logger.info("✅ MongoDB connection via ConfigManager successful")
            
        finally:
            client.close()
```

---

### ❓ שאלות צפויות + תשובות

#### **שאלה 1: מה זה ConfigManager? למה צריך אותו?**
**תשובה:**
```
ConfigManager = Centralized configuration management

Problem Without ConfigManager:
❌ Hard-coded values scattered in code
❌ Different configs for dev/staging/prod
❌ Difficult to change
❌ Security risk (passwords in code)

Solution With ConfigManager:
✅ Single source of truth
✅ Environment-based configs
✅ Easy to change (edit YAML)
✅ Secure (credentials from secrets)

Example:
config = ConfigManager("production")  # Auto-loads production config
mongo_config = config.get_database_config()  # Gets MongoDB config
```

#### **שאלה 2: איך ConfigManager מטפל בסביבות שונות?**
**תשובה:**
```yaml
# config/environments.yaml

development:
  mongodb:
    host: "localhost"
    port: 27017

staging:
  mongodb:
    host: "10.10.100.50"
    port: 27017

production:
  mongodb:
    host: "10.10.100.108"
    port: 27017
```

```python
# Usage:
config_dev = ConfigManager("development")
config_prod = ConfigManager("production")

# Same code, different environment!
mongo_config = config_dev.get_database_config()  # Gets dev config
mongo_config = config_prod.get_database_config()  # Gets prod config
```

#### **שאלה 3: מה קורה אם ConfigManager לא מוצא את הקובץ?**
**תשובה:**
```python
# ConfigManager should handle this gracefully:

class ConfigManager:
    def __init__(self, environment):
        config_path = Path("config/environments.yaml")
        
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )
        
        # Load YAML
        with open(config_path) as f:
            all_configs = yaml.safe_load(f)
        
        if environment not in all_configs:
            raise ValueError(
                f"Environment '{environment}' not found in config. "
                f"Available: {list(all_configs.keys())}"
            )
        
        self.config = all_configs[environment]
```

#### **שאלה 4: איך מטפלים בסודות (secrets) בצורה בטוחה?**
**תשובה:**
```
Bad Practice ❌:
mongodb:
  password: "mysecretpassword123"  # In Git!

Good Practices ✅:

Option 1: Environment Variables
mongodb:
  password: ${MONGO_PASSWORD}  # From env var

Option 2: Secret Management Service
mongodb:
  password: ${vault:secret/mongo/password}  # From Vault

Option 3: Kubernetes Secrets
# Mounted as file or env var in pod

Implementation:
import os
password = os.getenv('MONGO_PASSWORD')
if not password:
    raise ValueError("MONGO_PASSWORD env var not set")
```

---

### 📈 קריטריוני הצלחה

| Test Aspect | Requirement | סיבה |
|------------|-------------|------|
| Config loads | 100% success | חובה להתחלה |
| All params present | 100% | חובה לחיבור |
| Values correct | 100% match | חובה לאבטחה |
| Connection works | 100% | חובה לפונקציונליות |

---

<a name="test-6-mongodb-tcp"></a>
## 🔌 טסט 6: MongoDB Direct TCP Connection and Authentication

### 📌 פרטי הטסט

| פרמטר | ערך |
|-------|-----|
| **Issue Key** | PZ-13806 |
| **Priority** | Critical |
| **Component** | MongoDB TCP, Authentication |
| **Status** | Implemented ✅ |
| **Test File** | `tests/integration/infrastructure/test_basic_connectivity.py` |
| **Test Function** | `test_mongodb_direct_connection` |

---

### 🎯 מטרת הטסט

**מה הטסט בודק?**
הטסט מאמת ברמה הכי נמוכה:
1. **TCP connection** ל-MongoDB server
2. **Authentication** עם credentials
3. **Basic operations**: ping, server info, list databases

**למה זה קריטי?**
זה הטסט הכי בסיסי - **foundation layer**.

```
Layer 5: Application (Focus Server)
Layer 4: Configuration (ConfigManager)  ← Test #5
Layer 3: High-level ops (Collections)    ← Test #3
Layer 2: Performance (Ping latency)      ← Test #4
Layer 1: TCP + Auth                       ← Test #6 (THIS ONE)
```

**אם Layer 1 נכשל → הכל נכשל!**

---

### 📊 מה בדיוק בודקים?

#### **Test Data:**
```json
{
  "host": "10.10.100.108",
  "port": 27017,
  "username": "prisma",
  "password": "prisma",
  "auth_source": "prisma",
  "database": "prisma",
  "connection_timeout_ms": 10000,
  "server_selection_timeout_ms": 10000
}
```

#### **צעדי הטסט (9 Steps):**

| # | Action | Expected |
|---|--------|----------|
| 1 | Load MongoDB config | Config loaded |
| 2 | Create MongoClient | Client created |
| 3 | Establish TCP connection | Connection established |
| 4 | Authenticate | Authentication success |
| 5 | Send ping command | `{'ok': 1.0}` |
| 6 | Get server info | Version returned |
| 7 | List databases | Database list returned |
| 8 | Verify prisma DB exists | `'prisma' in db_list` |
| 9 | Close connection | Clean disconnect |

---

### 🔧 איך לממש את הטסט בקוד?

```python
# File: tests/integration/infrastructure/test_basic_connectivity.py

import pytest
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
from config.config_manager import ConfigManager

class TestMongoDBLowLevel:
    """
    Low-level MongoDB connectivity tests.
    Tests the foundational layer: TCP connection and authentication.
    """
    
    @pytest.mark.mongodb
    @pytest.mark.infrastructure
    @pytest.mark.critical
    def test_mongodb_direct_tcp_connection(self):
        """
        Test MongoDB direct TCP connection and authentication.
        
        Purpose:
        - Validate TCP connection to MongoDB server
        - Verify authentication mechanism works
        - Test basic commands (ping, server info)
        - Verify database accessibility
        
        This is the most fundamental MongoDB test - it validates
        the lowest layer of connectivity. All other MongoDB tests
        depend on this passing.
        
        Steps:
        1. Load MongoDB configuration
        2. Create MongoClient with explicit parameters
        3. Establish TCP connection
        4. Authenticate with credentials
        5. Execute ping command
        6. Get server version info
        7. List databases
        8. Verify target database exists
        9. Close connection cleanly
        
        Expected:
        - TCP connection successful
        - Authentication passes
        - Ping returns {'ok': 1.0}
        - Server version retrieved
        - Database list includes 'prisma'
        - Clean disconnect
        """
        
        # 1. Load configuration
        config_manager = ConfigManager("new_production")
        mongo_config = config_manager.get_database_config()
        
        # 2. Create MongoClient with explicit parameters and timeouts
        client = MongoClient(
            host=mongo_config['host'],  # 10.10.100.108
            port=mongo_config['port'],  # 27017
            username=mongo_config['username'],
            password=mongo_config['password'],
            authSource=mongo_config.get('auth_source', 'admin'),
            # Timeouts
            serverSelectionTimeoutMS=10000,  # 10 seconds
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            # Connection pool
            maxPoolSize=10,
            minPoolSize=1
        )
        
        try:
            # 3. Test TCP connection + Authentication with ping
            logger.info("Testing TCP connection and authentication...")
            try:
                ping_result = client.admin.command('ping')
            except ConnectionFailure as e:
                pytest.fail(f"TCP connection failed: {e}")
            except OperationFailure as e:
                pytest.fail(f"Authentication failed: {e}")
            except ServerSelectionTimeoutError as e:
                pytest.fail(f"Server selection timeout: {e}")
            
            # 4. Validate ping response
            assert ping_result.get('ok') == 1.0, \
                f"Ping failed with response: {ping_result}"
            logger.info("✅ TCP connection and authentication successful")
            
            # 5. Get server information
            logger.info("Retrieving server information...")
            server_info = client.server_info()
            
            # Validate server info structure
            assert 'version' in server_info, "Server info missing 'version'"
            version = server_info['version']
            logger.info(f"✅ MongoDB Version: {version}")
            
            # Optional: Verify version meets minimum requirement
            # major_version = int(version.split('.')[0])
            # assert major_version >= 4, f"MongoDB version too old: {version}"
            
            # 6. List all databases
            logger.info("Listing databases...")
            db_list = client.list_database_names()
            
            assert isinstance(db_list, list), "Database list not a list"
            assert len(db_list) > 0, "No databases found (empty list)"
            logger.info(f"Found {len(db_list)} databases: {db_list}")
            
            # 7. Verify target database exists
            target_db = mongo_config['database']  # 'prisma'
            assert target_db in db_list, \
                f"Database '{target_db}' not found in {db_list}"
            logger.info(f"✅ Target database '{target_db}' exists")
            
            # 8. Additional validation: Connect to database and verify access
            db = client[target_db]
            collections = db.list_collection_names()
            logger.info(f"Database '{target_db}' has {len(collections)} collections")
            
        except Exception as e:
            pytest.fail(f"MongoDB connectivity test failed: {e}")
            
        finally:
            # 9. Always close connection
            client.close()
            logger.info("✅ MongoDB connection closed cleanly")
```

---

### ❓ שאלות צפויות + תשובות

#### **שאלה 1: מה ההבדל בין ConnectionFailure ל-OperationFailure?**
**תשובה:**
```
ConnectionFailure:
- TCP connection נכשל
- Cannot reach server
- Network issue
- MongoDB down

OperationFailure:
- TCP connection OK
- Authentication failed
- Wrong username/password
- Wrong authSource
- Permissions issue

Example:
try:
    client.admin.command('ping')
except ConnectionFailure:
    # Network/server problem
    print("Cannot reach MongoDB")
except OperationFailure:
    # Auth problem
    print("Wrong credentials")
```

#### **שאלה 2: מה זה ServerSelectionTimeout? מתי זה קורה?**
**תשובה:**
```
ServerSelectionTimeout:
- MongoDB client tries to find suitable server
- Can't find one within timeout
- Common causes:
  ✗ MongoDB not running
  ✗ Network unreachable
  ✗ Wrong host/port
  ✗ Replica set misconfigured

Timeout Configuration:
serverSelectionTimeoutMS=10000  # 10 seconds

Recommendation:
- Dev/Testing: 5-10 seconds
- Production: 10-30 seconds
- CI/CD: 5 seconds (fail fast)
```

#### **שאלה 3: מה זה Connection Pool? למה צריך אותו?**
**תשובה:**
```
Connection Pool = מאגר חיבורים פתוחים

Without Pool:
Request 1 → Open connection → Use → Close
Request 2 → Open connection → Use → Close
Request 3 → Open connection → Use → Close
    ↓
Slow! Open/close connection is expensive

With Pool:
Pool: [Conn1, Conn2, Conn3, ...]
Request 1 → Get Conn1 from pool → Use → Return to pool
Request 2 → Get Conn2 from pool → Use → Return to pool
    ↓
Fast! Reuse existing connections

Configuration:
maxPoolSize=10   # Max 10 concurrent connections
minPoolSize=1    # Keep at least 1 open
```

#### **שאלה 4: איך בודקים שהסגירה של Connection תקינה?**
**תשובה:**
```python
# Always use try-finally:
client = MongoClient(...)
try:
    # Do work
    pass
finally:
    client.close()  # Always runs!

# Check connection state:
assert client.address is None, "Connection not closed"

# Check no hanging connections on MongoDB:
# On MongoDB server:
db.adminCommand({currentOp: true})
# Check 'inprog' array is empty

# In test:
# Run test
# Check MongoDB connections count
# Should be 0 after test completes
```

#### **שאלה 5: מה קורה אם יש network hiccup באמצע?**
**תשובה:**
```
pymongo Auto-Retry:
✅ Automatically retries failed operations
✅ Handles temporary network issues
✅ Transparent to application

Configuration:
retryWrites=True   # Retry write operations
retryReads=True    # Retry read operations

Example:
# Network hiccup during ping:
1. client.admin.command('ping')
2. Network drops for 100ms
3. pymongo auto-retries
4. Network back
5. Ping succeeds
   ↓
Application doesn't even know!

If exhausts retries:
→ Raises exception
```

---

### 📈 קריטריוני הצלחה

| Test Stage | Requirement | Impact if Fails |
|-----------|-------------|-----------------|
| TCP connection | 100% | Total system failure |
| Authentication | 100% | Cannot access data |
| Ping command | 100% | Basic health check fails |
| Server info | 100% | Cannot verify version |
| Database list | 100% | Cannot find databases |

---

<a name="summary"></a>
## 📋 סיכום - מטריצת השוואה בין הטסטים

### טבלת השוואה מקיפה:

| היבט | Test #1<br/>SSH | Test #2<br/>K8s | Test #3<br/>MongoDB Health | Test #4<br/>MongoDB Perf | Test #5<br/>Config | Test #6<br/>TCP Auth |
|------|----------------|----------------|---------------------------|------------------------|-------------------|---------------------|
| **Priority** | High | High | High | Medium | High | **Critical** |
| **Layer** | Infrastructure | Orchestration | Data Layer | Performance | Configuration | Foundation |
| **Purpose** | Troubleshooting access | Pod monitoring | DB health | Performance | Config validation | Basic connectivity |
| **Isolates** | SSH connectivity | K8s cluster | MongoDB operations | Response time | ConfigManager | TCP + Auth |
| **Duration** | 3-5s | 3-5s | 2-3s | <1s | 1-2s | 1-2s |
| **Dependency** | Network | Network, K8s | Network, MongoDB | MongoDB | Config files | Network, MongoDB |
| **Failure Impact** | No troubleshooting | No monitoring | No data access | Performance issues | App won't start | Total MongoDB failure |
| **Automation** | ✅ Automated | ✅ Automated | ✅ Automated | ✅ Automated | ✅ Automated | ✅ Automated |

---

### זרימה לוגית בין הטסטים:

```
1. Test #6 (TCP + Auth) - FOUNDATION
   ↓ If passes
   
2. Test #3 (MongoDB Health) - OPERATIONS
   ↓ If passes
   
3. Test #4 (Performance) - SPEED
   ↓ If passes
   
4. Test #5 (ConfigManager) - CONFIGURATION
   ↓ If passes
   
5. Test #1 (SSH) - MAINTENANCE ACCESS
   
6. Test #2 (Kubernetes) - ORCHESTRATION HEALTH
```

**כללי אבחון (Diagnosis Rules):**

| Failure Pattern | Diagnosis | Next Step |
|----------------|-----------|-----------|
| Test #6 fails | MongoDB TCP/Auth issue | Check MongoDB logs, network |
| Test #6 passes, #3 fails | MongoDB health issue | Check collections, disk space |
| Tests #3,#6 pass, #4 fails | Performance degradation | Check load, indexes |
| Tests #3,#4,#6 pass, #5 fails | Config problem | Check YAML files |
| Tests #1,#2 fail | Infrastructure down | Check SSH, K8s cluster |

---

<a name="qa"></a>
## ❓ שאלות צפויות כלליות בפגישה + תשובות

### שאלות אסטרטגיות:

#### **שאלה 1: למה צריך 6 טסטים שונים ל-MongoDB? זה לא redundant?**
**תשובה:**
```
לא! כל טסט בוחן שכבה אחרת:

Test #6: האם אני יכול להתחבר? (TCP + Auth)
Test #3: האם המבנה תקין? (Collections, Schema)
Test #4: האם זה מהיר? (Performance)
Test #5: האם Config נכון? (ConfigManager)

Analogy (דימוי):
- Test #6 = "האם יש חיבור לאינטרנט?"
- Test #3 = "האם האתר קיים?"
- Test #4 = "האם האתר מהיר?"
- Test #5 = "האם השמרתי את ה-URL נכון?"

כל שכבה יכולה לכשל בנפרד!
```

#### **שאלה 2: מה עושים אם טסט נכשל ב-CI/CD pipeline?**
**תשובה:**
```
CI/CD Failure Strategy:

1. Identify Layer:
   - Infrastructure test fails → בעיה בתשתית
   - Functional test fails → בעיה בקוד

2. Immediate Actions:
   ✅ Block deployment (don't deploy broken code)
   ✅ Notify team (Slack, email)
   ✅ Create incident ticket
   ✅ Check logs

3. Investigation:
   - Check test logs
   - Check service logs
   - Check infrastructure monitoring
   - Reproduce locally

4. Resolution:
   - Fix issue
   - Re-run tests
   - If passes → merge/deploy
   - If fails → escalate

Example Flow:
Git Push → CI runs tests → Test #3 fails → Block merge
                                          ↓
                            Team investigates → MongoDB disk full
                                          ↓
                            Clear space → Re-run → Pass → Deploy
```

#### **שאלה 3: איך מתעדפים fix של טסטים כשהרבה נכשלים?**
**תשובה:**
```
Priority Order (מהגבוה לנמוך):

1. Critical Infrastructure (Test #6, #1, #2)
   → חובה לפעולה בסיסית
   
2. High Priority Operations (Test #3, #5)
   → חיוני לפונקציונליות
   
3. Performance & Optimization (Test #4)
   → חשוב אבל לא blocking

Decision Matrix:
| Severity | Production Impact | Fix Priority |
|----------|------------------|--------------|
| Critical | System down | P0 - Immediate |
| High | Features broken | P1 - Same day |
| Medium | Degraded perf | P2 - This week |
| Low | Minor issues | P3 - Backlog |

Example:
- Test #6 fails + Test #4 fails → Fix #6 first!
- Test #1 fails + Test #5 fails → Fix #5 first (blocks app start)
```

#### **שאלה 4: איך מבטיחים שהטסטים עצמם לא broken?**
**תשובה:**
```
Test Quality Assurance:

1. Code Reviews:
   ✅ Peer review לכל test
   ✅ Senior approval

2. Test the Tests:
   ✅ Run locally before commit
   ✅ Verify against known-good state
   ✅ Test both pass and fail scenarios

3. Maintenance:
   ✅ Update when APIs change
   ✅ Refactor when brittle
   ✅ Document expected behavior

4. Monitoring:
   ✅ Track flaky tests (intermittent failures)
   ✅ Track test execution time
   ✅ Alert on unusual patterns

Flaky Test Detection:
# Run test 10 times:
for i in range(10):
    result = run_test()
    results.append(result)

# If not all pass or all fail → Flaky!
if not (all(results) or not any(results)):
    mark_as_flaky()
```

#### **שאלה 5: מה ה-ROI (Return on Investment) של האוטומציה הזאת?**
**תשובה:**
```
ROI Calculation:

Manual Testing:
- Time per test: 5 minutes
- 6 tests: 30 minutes
- Run per day: 3 times (dev, staging, prod)
- Total: 90 minutes/day
- Monthly: 90 min × 22 days = 33 hours
- Cost: 33 hours × $50/hour = $1,650/month

Automated Testing:
- Setup time: 40 hours (one-time)
- Maintenance: 2 hours/month
- Execution time: 30 seconds (vs 90 minutes)
- Cost: $0/month (runs automatically)

Break-Even:
$2,000 setup / $1,650 saved per month = 1.2 months

After 2 months: Net positive ROI!

Additional Benefits (hard to quantify):
✅ Faster feedback (seconds vs hours)
✅ Earlier bug detection
✅ Consistent execution
✅ No human error
✅ Enables CI/CD
✅ Confidence in deployments

Total ROI: ~500% within first year
```

---

### שאלות טכניות:

#### **שאלה 6: איך מטפלים בסביבות שונות (dev/staging/prod)?**
**תשובה:**
```python
# config/environments.yaml
environments:
  development:
    mongodb:
      host: "localhost"
      port: 27017
    kubernetes:
      context: "minikube"
    ssh:
      enabled: false  # No SSH in dev
  
  staging:
    mongodb:
      host: "staging-mongo.internal"
      port: 27017
    kubernetes:
      context: "staging-cluster"
    ssh:
      jump_host: "staging-jump.internal"
  
  production:
    mongodb:
      host: "10.10.100.108"
      port: 27017
    kubernetes:
      context: "prod-cluster"
    ssh:
      jump_host: "10.10.100.3"

# Test execution:
# Dev:
pytest --env=development

# Staging:
pytest --env=staging

# Prod:
pytest --env=production
```

#### **שאלה 7: איך מונעים תלות בין טסטים (test isolation)?**
**תשובה:**
```python
# Bad Practice ❌:
def test_create_user():
    user = create_user("test@example.com")
    # Doesn't clean up!

def test_login():
    # Depends on test_create_user!
    login("test@example.com")

# Good Practice ✅:
@pytest.fixture
def clean_database():
    # Setup
    db.clear()
    yield
    # Teardown
    db.clear()

def test_create_user(clean_database):
    user = create_user("test@example.com")
    # Clean database after test

def test_login(clean_database):
    # Independent - creates own data
    create_user("test@example.com")
    login("test@example.com")

Principles:
1. Each test creates its own data
2. Each test cleans up after itself
3. Tests can run in any order
4. Tests can run in parallel
```

#### **שאלה 8: איך measuring test coverage?**
**תשובה:**
```bash
# Install coverage tool:
pip install pytest-cov

# Run with coverage:
pytest --cov=src --cov-report=html tests/

# Output:
Name                  Stmts   Miss  Cover
-----------------------------------------
src/__init__.py           5      0   100%
src/mongodb.py          120     10    92%
src/ssh.py               80      5    94%
-----------------------------------------
TOTAL                   205     15    93%

# View detailed report:
open htmlcov/index.html

Coverage Goals:
✅ Critical paths: 100%
✅ Infrastructure: 95%+
✅ Utilities: 90%+
✅ Overall: 85%+
```

---

## 🎓 מונחון (Glossary) - מילון מונחים

### Infrastructure Terms:

| מונח | הסבר | דוגמה |
|------|------|-------|
| **Jump Host** | שרת ביניים מאובטח לגישה ל-production | Bastion server |
| **LoadBalancer** | מנגנון חלוקת עומסים | MongoDB exposed via LB |
| **ClusterIP** | כתובת IP פנימית ב-K8s | Service internal IP |
| **Namespace** | קבוצה לוגית של resources ב-K8s | `panda` namespace |
| **Pod** | יחידת ריצה בסיסית ב-K8s | Container group |

### Testing Terms:

| מונח | הסבר | דוגמה |
|------|------|-------|
| **Isolation Test** | טסט שבודק קומפוננט אחד בלבד | MongoDB without Focus Server |
| **Integration Test** | טסט שבודק קומפוננטות יחד | Focus Server + MongoDB |
| **Smoke Test** | טסטים בסיסיים מהירים | Can I connect? |
| **Regression Test** | בדיקה שלא נשברו דברים קיימים | After changes |

### MongoDB Terms:

| מונח | הסבר | דוגמה |
|------|------|-------|
| **authSource** | DB שבו נמצאים users | `prisma` |
| **Collection** | טבלה (כמו ב-SQL) | `recordings` |
| **Document** | שורה (כמו ב-SQL) | Single recording |
| **Connection Pool** | מאגר חיבורים פתוחים | Reuse connections |

---

## ✅ Checklist להכנה לפגישה

### הכנה טכנית:
- [ ] קראתי את כל 6 הטסטים
- [ ] הבנתי את המטרה של כל טסט
- [ ] יכול להסביר את ההבדלים ביניהם
- [ ] יודע איך לממש כל טסט (ברמה קונספטואלית)
- [ ] מכיר את ה-dependencies הנדרשים
- [ ] מבין את ה-test flow של כל טסט

### הכנה קונספטואלית:
- [ ] מבין את שכבות התשתית (TCP → Health → Performance → Config)
- [ ] יכול להסביר למה צריך כל טסט
- [ ] יודע מה קורה כשכל טסט נכשל
- [ ] מבין את הקשר בין הטסטים
- [ ] יכול לתעדף fixes לפי חומרה

### הכנה לשאלות:
- [ ] מוכן לענות על שאלות "למה"
- [ ] מוכן לענות על שאלות טכניות
- [ ] מוכן להציג alternatives/trade-offs
- [ ] מוכן להסביר ROI
- [ ] מוכן לדון ב-CI/CD integration

---

## 🎯 המלצות אחרונות לפגישה

### Do's ✅:
1. **התחל עם Big Picture** - הסבר את מטרת בדיקות Infrastructure
2. **השתמש בדוגמאות** - "זה כמו לבדוק שיש חשמל לפני שמדליקים מחשב"
3. **הדגש נחיצות** - "בלי הטסטים האלה, לא נדע שמשהו נשבר עד שלקוח יתלונן"
4. **הצג confidence** - "הטסטים האלה נותנים לנו אמון לעשות deployments"
5. **דבר על automation value** - "חוסך X שעות בשבוע"

### Don'ts ❌:
1. **אל תיכנס לפרטים קטנים מדי** - אלא אם שואלים
2. **אל תניח ידע מוקדם** - הסבר מושגים בסיסיים
3. **אל תגיד "זה פשוט"** - זה מזלזל במאמץ
4. **אל תהיה defensive** - אם יש ביקורת, תקשיב
5. **אל תבטיח מה שאתה לא יכול לעמוד בו** - היה realistic

### Key Messages להעביר:
1. 🎯 **Infrastructure tests are critical** - without them, we're blind
2. ⚡ **Automation saves time and increases confidence**
3. 🔍 **Each test isolates a specific layer** - efficient debugging
4. 📊 **Measurable ROI** - pays for itself in weeks
5. 🚀 **Enables CI/CD** - faster, safer deployments

---

## 📞 צור קשר לשאלות נוספות

אם יש שאלות נוספות או צריך הבהרות:
- 📧 Email: [your-email]
- 💬 Slack: #focus-server-qa
- 📱 Teams: QA Channel

---

**בהצלחה בפגישה! 🚀**

*מסמך זה הוכן עבור PZ-13756 - Focus Server Infrastructure Tests*
*עודכן לאחרונה: 27 אוקטובר 2025*

