# מדריך לניטור לוגים - סביבת ייצור חדשה (Panda)

## 📋 תוכן עניינים
1. [גישה לפודים](#גישה-לפודים)
2. [צפייה בלוגים](#צפייה-בלוגים)
3. [K9s - כלי ניטור אינטראקטיבי](#k9s---כלי-ניטור-אינטראקטיבי)
4. [ניטור מרחוק דרך Automation](#ניטור-מרחוק-דרך-automation)
5. [טיפים ושגרות עבודה](#טיפים-ושגרות-עבודה)

---

## 🔐 גישה לפודים

### שיטת גישה
הגישה לפודים היא דרך **SSH עם 2 הופים (Jump Host)**:

```bash
# Step 1: התחבר ל-Jump Host (panda2worker)
ssh root@10.10.100.3
# Password: PASSW0RD

# Step 2: התחבר ל-Worker Node (בעל kubectl/k9s)
ssh prisma@10.10.100.113
# Password: PASSW0RD

# Step 3: עכשיו אפשר להשתמש ב-kubectl או k9s
kubectl get pods -n panda
k9s -n panda
```

### סקריפט מהיר
השתמש בסקריפט המוכן:
```powershell
.\connect_k9s.ps1 -Mode quick
```

---

## 📜 צפייה בלוגים

### 1. לוגים של Pod מסוים

#### Focus Server
```bash
# מצא את שם הפוד
kubectl get pods -n panda | grep focus-server

# צפה בלוגים
kubectl logs panda-panda-focus-server-988555979-nz9fr -n panda

# עקוב אחרי לוגים בזמן אמת
kubectl logs panda-panda-focus-server-988555979-nz9fr -n panda -f

# לוגים של 100 שורות אחרונות
kubectl logs panda-panda-focus-server-988555979-nz9fr -n panda --tail=100

# לוגים מ-5 דקות אחרונות
kubectl logs panda-panda-focus-server-988555979-nz9fr -n panda --since=5m
```

#### MongoDB
```bash
kubectl get pods -n panda | grep mongodb
kubectl logs mongodb-569cc5fbbb-526m9 -n panda -c mongodb
```

#### RabbitMQ
```bash
kubectl get pods -n panda | grep rabbitmq
kubectl logs rabbitmq-panda-0 -n panda -f
```

#### gRPC Jobs
```bash
kubectl get pods -n panda | grep grpc-job
kubectl logs grpc-job-1-4-2crtf -n panda -f
```

### 2. לוגים של כל הפודים בשירות

```bash
# כל הפודים של Focus Server
kubectl logs -n panda -l app.kubernetes.io/name=panda-panda-focus-server

# כל הפודים של RabbitMQ
kubectl logs -n panda -l app.kubernetes.io/instance=rabbitmq-panda
```

### 3. שמירת לוגים לקובץ

```bash
# שמור לוגים לקובץ
kubectl logs panda-panda-focus-server-988555979-nz9fr -n panda > focus_server_logs.txt

# שמור לוגים עם חותמת זמן
kubectl logs panda-panda-focus-server-988555979-nz9fr -n panda --timestamps > focus_server_$(date +%Y%m%d_%H%M%S).log

# שמור לוגים של כל הפודים
for pod in $(kubectl get pods -n panda -o name); do
  kubectl logs $pod -n panda > "${pod//\//_}_$(date +%Y%m%d_%H%M%S).log"
done
```

---

## 🎮 K9s - כלי ניטור אינטראקטיבי

### הפעלת K9s
```bash
# מתוך worker node (10.10.100.113)
k9s

# או ישירות ל-namespace של panda
k9s -n panda
```

### פקודות חשובות ב-K9s

| פעולה | קיצור מקלדת | תיאור |
|-------|-------------|--------|
| עבור לפודים | `:pods` | הצג את כל הפודים |
| עבור לשירותים | `:svc` | הצג את כל השירותים |
| עבור ל-deployments | `:deploy` | הצג deployments |
| עבור ל-logs | `:logs` | הצג לוגים |
| צפה בלוגים | `l` (על pod מסומן) | פתח לוגים של הפוד |
| תיאור משאב | `d` | הצג describe של המשאב |
| shell לתוך pod | `s` | פתח bash/sh בתוך הפוד |
| מחק משאב | `Ctrl+d` | מחק את המשאב המסומן |
| רענן | `Ctrl+a` | רענן את התצוגה |
| סינון | `/pattern` | סנן לפי שם |
| מיון | `Shift+s` | מיין את הרשימה |
| עזרה | `?` | הצג מסך עזרה |

### תרחישים נפוצים ב-K9s

#### 1. בדיקת בריאות כל הפודים
1. הפעל: `k9s -n panda`
2. הקש: `:pods`
3. בדוק שכל הפודים ב-`Running` וב-`1/1 Ready`

#### 2. צפייה בלוגים של Focus Server בזמן אמת
1. הקש: `:pods`
2. חפש: `/focus-server`
3. סמן את הפוד עם חצים
4. הקש: `l` (ראה logs)
5. הקש: `0` להצגת לוגים בזמן אמת

#### 3. כניסה לפוד (shell)
1. הקש: `:pods`
2. סמן את הפוד הרצוי
3. הקש: `s` (shell)
4. בחר: `/bin/bash` או `/bin/sh`

#### 4. בדיקת שירותים ו-endpoints
1. הקש: `:svc`
2. סמן את השירות הרצוי
3. הקש: `d` (describe)

---

## 🤖 ניטור מרחוק דרך Automation

### Python Script לאיסוף לוגים

```python
"""
Automated log collection from Panda namespace
"""
import subprocess
import os
from datetime import datetime
from pathlib import Path

class K8sLogCollector:
    """
    Production-grade Kubernetes log collector for Focus Server automation.
    """
    
    def __init__(self, 
                 jump_host="10.10.100.3", 
                 jump_user="root",
                 target_host="10.10.100.113",
                 target_user="prisma",
                 namespace="panda"):
        """
        Initialize K8s log collector with SSH gateway configuration.
        
        Args:
            jump_host: Jump host IP
            jump_user: Jump host username
            target_host: Target K8s worker node IP
            target_user: Target node username
            namespace: Kubernetes namespace to monitor
        """
        self.jump_host = jump_host
        self.jump_user = jump_user
        self.target_host = target_host
        self.target_user = target_user
        self.namespace = namespace
        
    def get_pod_logs(self, pod_name, tail=100, follow=False):
        """
        Retrieve logs from a specific pod via SSH tunnel.
        
        Args:
            pod_name: Name of the pod
            tail: Number of lines to retrieve (default: 100)
            follow: Stream logs in real-time (default: False)
            
        Returns:
            str: Pod logs
        """
        follow_flag = "-f" if follow else ""
        
        # Build SSH command with double hop
        ssh_cmd = (
            f"ssh -o StrictHostKeyChecking=no "
            f"-J {self.jump_user}@{self.jump_host} "
            f"{self.target_user}@{self.target_host} "
            f"'kubectl logs {pod_name} -n {self.namespace} --tail={tail} {follow_flag}'"
        )
        
        try:
            result = subprocess.run(
                ssh_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_all_pods(self):
        """
        Get list of all pods in namespace.
        
        Returns:
            list: Pod names
        """
        ssh_cmd = (
            f"ssh -o StrictHostKeyChecking=no "
            f"-J {self.jump_user}@{self.jump_host} "
            f"{self.target_user}@{self.target_host} "
            f"'kubectl get pods -n {self.namespace} -o name'"
        )
        
        try:
            result = subprocess.run(
                ssh_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                pods = result.stdout.strip().split('\n')
                # Remove 'pod/' prefix
                return [p.replace('pod/', '') for p in pods if p]
            else:
                return []
                
        except Exception as e:
            print(f"Error getting pods: {e}")
            return []
    
    def collect_all_logs(self, output_dir="./logs", tail=500):
        """
        Collect logs from all pods and save to files.
        
        Args:
            output_dir: Directory to save log files
            tail: Number of lines to retrieve per pod
            
        Returns:
            dict: {pod_name: log_file_path}
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        collected_logs = {}
        
        pods = self.get_all_pods()
        print(f"[INFO] Found {len(pods)} pods in namespace '{self.namespace}'")
        
        for pod in pods:
            print(f"[INFO] Collecting logs from: {pod}")
            logs = self.get_pod_logs(pod, tail=tail)
            
            # Save to file
            log_filename = f"{pod}_{timestamp}.log"
            log_filepath = output_path / log_filename
            
            with open(log_filepath, 'w', encoding='utf-8') as f:
                f.write(logs)
            
            collected_logs[pod] = str(log_filepath)
            print(f"[SUCCESS] Saved to: {log_filepath}")
        
        return collected_logs
    
    def monitor_focus_server_health(self):
        """
        Monitor Focus Server pod health by checking recent logs for errors.
        
        Returns:
            dict: Health status and error messages
        """
        pods = self.get_all_pods()
        focus_server_pods = [p for p in pods if 'focus-server' in p]
        
        if not focus_server_pods:
            return {
                "status": "ERROR",
                "message": "No Focus Server pods found"
            }
        
        health_status = {}
        
        for pod in focus_server_pods:
            logs = self.get_pod_logs(pod, tail=50)
            
            # Check for common error patterns
            errors = []
            if "ERROR" in logs:
                errors.append("ERROR found in logs")
            if "Exception" in logs:
                errors.append("Exception found in logs")
            if "CrashLoopBackOff" in logs:
                errors.append("Pod in CrashLoopBackOff")
            
            health_status[pod] = {
                "status": "UNHEALTHY" if errors else "HEALTHY",
                "errors": errors,
                "last_logs": logs[-500:] if logs else ""
            }
        
        return health_status


# Usage Example
if __name__ == "__main__":
    collector = K8sLogCollector()
    
    # Collect logs from all pods
    print("Collecting logs from all pods...")
    logs = collector.collect_all_logs(output_dir="./reports/k8s_logs")
    
    # Monitor Focus Server health
    print("\nChecking Focus Server health...")
    health = collector.monitor_focus_server_health()
    
    for pod, status in health.items():
        print(f"\n{pod}: {status['status']}")
        if status['errors']:
            print(f"  Errors: {', '.join(status['errors'])}")
```

### שימוש ב-Pytest fixture

```python
"""
Pytest fixture for K8s log collection in tests
"""
import pytest
from pathlib import Path
from datetime import datetime

@pytest.fixture(scope="session")
def k8s_log_collector():
    """
    Provide K8s log collector instance for all tests.
    """
    from monitoring.k8s_logs import K8sLogCollector
    return K8sLogCollector()

@pytest.fixture(scope="function")
def collect_logs_on_failure(request, k8s_log_collector):
    """
    Automatically collect K8s logs when a test fails.
    """
    yield
    
    if request.node.rep_call.failed:
        # Test failed - collect logs
        test_name = request.node.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"./reports/failed_tests/{test_name}_{timestamp}"
        
        print(f"\n[COLLECTING LOGS] Test '{test_name}' failed - collecting K8s logs...")
        k8s_log_collector.collect_all_logs(output_dir=output_dir, tail=200)
        print(f"[LOGS SAVED] Logs saved to: {output_dir}")
```

---

## 💡 טיפים ושגרות עבודה

### 1. בדיקת בריאות יומית

```bash
#!/bin/bash
# daily_health_check.sh

echo "=== Daily Health Check - $(date) ==="

# 1. Check all pods are running
echo "1. Pod Status:"
kubectl get pods -n panda

# 2. Check for restarts
echo "2. Pods with restarts:"
kubectl get pods -n panda --field-selector=status.phase=Running \
  | awk 'NR>1 && $4>0 {print $1, "- Restarts:", $4}'

# 3. Check for errors in last hour
echo "3. Recent errors in Focus Server:"
POD=$(kubectl get pods -n panda -l app.kubernetes.io/name=panda-panda-focus-server -o name | head -1)
kubectl logs $POD -n panda --since=1h | grep -i "error" | tail -20

# 4. Check services
echo "4. Services status:"
kubectl get svc -n panda

# 5. Resource usage
echo "5. Resource usage:"
kubectl top pods -n panda
```

### 2. ניטור בזמן ריצת טסטים

```bash
# Terminal 1: הרץ את הטסטים
pytest tests/integration/ -v

# Terminal 2: עקוב אחרי לוגים
kubectl logs -n panda -f $(kubectl get pods -n panda -l app.kubernetes.io/name=panda-panda-focus-server -o name | head -1)

# Terminal 3: צפה ב-K9s
k9s -n panda
```

### 3. איתור בעיות נפוצות

#### בעיה: Pod במצב CrashLoopBackOff
```bash
# הצג את הלוגים
kubectl logs <pod-name> -n panda

# הצג לוגים של הנסיון הקודם
kubectl logs <pod-name> -n panda --previous

# describe לפרטים נוספים
kubectl describe pod <pod-name> -n panda
```

#### בעיה: שירות לא מגיב
```bash
# בדוק endpoints
kubectl get endpoints <service-name> -n panda

# בדוק את הפודים של השירות
kubectl get pods -n panda -l <label-selector>

# בדוק connectivity מתוך פוד אחר
kubectl exec -n panda <pod-name> -- curl http://<service>:<port>/health
```

### 4. מחיקת לוגים ישנים (cleanup)

```bash
# מחק לוגים ישנים מ-reports/k8s_logs
find ./reports/k8s_logs -name "*.log" -mtime +7 -delete

# או השתמש בסקריפט Python
python scripts/cleanup_old_logs.py --days 7
```

---

## 📊 Dashboard ו-Metrics

### Prometheus (אם זמין)
```bash
# Check if Prometheus is available
kubectl get svc -n monitoring

# Port-forward to Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Access: http://localhost:9090
```

### Grafana (אם זמין)
```bash
# Port-forward to Grafana
kubectl port-forward -n monitoring svc/grafana 3000:80

# Access: http://localhost:3000
```

### RabbitMQ Management UI
```
URL: http://10.10.100.107:15672
Username: prisma (או user)
Password: prismapanda
```

---

## 🔗 קישורים רלוונטיים

- **K9s Documentation**: https://k9scli.io/
- **kubectl Cheat Sheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- **Kubernetes Logs**: https://kubernetes.io/docs/concepts/cluster-administration/logging/

---

## 📝 רשימת ניטור לפני ריצת טסטים

- [ ] כל הפודים ב-`Running` ו-`Ready`
- [ ] אין פודים במצב `CrashLoopBackOff` או `Error`
- [ ] Focus Server מגיב ל-health checks
- [ ] MongoDB ו-RabbitMQ זמינים
- [ ] אין errors קריטיים בלוגים האחרונים (1 שעה אחרונה)
- [ ] משאבי CPU/Memory לא ב-capacity מלא

---

**נוצר**: אוקטובר 2025  
**עודכן אחרון**: 2025-10-19  
**גרסה**: 1.0

