# איך לבדוק למה Health Checks תקועים?

**תאריך:** 2025-11-29  
**בעיה:** Health checks תקועים אחרי Kubernetes check

---

## 🔍 זיהוי הבעיה

### מה קורה?

הלוגים מראים שהתהליך תקוע אחרי:
```
[3/5] Checking Kubernetes... ✅ OK
   ✓ Focus Server deployment found (ready: 1/1)
```

אבל לא ממשיך ל:
- `[4/5] Checking MongoDB...`
- `[5/5] Checking RabbitMQ...`

---

## 🎯 סיבות אפשריות

### 1. **MongoDB Check תקוע**

**מה קורה:**
- `check_mongodb()` קורא ל-`get_mongodb_status()`
- `get_mongodb_status()` משתמש ב-Kubernetes API (דרך SSH fallback)
- אם ה-Kubernetes API call לא מחזיר תשובה, זה יכול להיתקע

**איך לבדוק:**
```powershell
# הרץ MongoDB check בנפרד עם timeout
$job = Start-Job {
    python scripts/pre_test_health_check.py --env=staging
}
Wait-Job $job -Timeout 60  # 60 שניות
if ($job.State -eq "Running") {
    Stop-Job $job
    Write-Host "MongoDB check תקוע!"
} else {
    Receive-Job $job
}
```

**פתרון:**
- ה-health check כבר מטפל ב-timeout של MongoDB status check
- אבל אם ה-connection עצמו תקוע, זה יכול להיתקע

---

### 2. **RabbitMQ Check תקוע ב-Port-Forward**

**מה קורה:**
- `check_rabbitmq()` קורא ל-`rabbitmq_manager.setup()`
- `setup()` קורא ל-`start_port_forward()`
- `start_port_forward()` מחכה עד 15 שניות שהפורט יהיה פתוח
- אבל אם ה-`_check_port_open()` תקוע, זה יכול להיתקע

**איך לבדוק:**
```powershell
# בדוק אם יש port-forward process רץ
Get-Process | Where-Object {$_.ProcessName -like "*kubectl*"}

# בדוק אם הפורט פתוח
Test-NetConnection -ComputerName 10.10.10.150 -Port 5672
```

**פתרון:**
- ה-`_check_port_open()` כבר יש לו timeout של 5 שניות
- אבל אם ה-SSH connection עצמו תקוע, זה יכול להיתקע

---

### 3. **Kubernetes API Call תקוע**

**מה קורה:**
- אחרי Kubernetes check, MongoDB check מנסה להשתמש ב-Kubernetes API
- אם ה-API call לא מחזיר תשובה, זה יכול להיתקע

**איך לבדוק:**
```powershell
# בדוק אם kubectl עובד
kubectl get pods -n panda --timeout=10s

# בדוק אם SSH עובד
ssh -o ConnectTimeout=10 prisma@10.10.10.150 "hostname"
```

---

## ✅ פתרונות מהירים

### פתרון 1: הרץ Health Check בנפרד עם Timeout

```powershell
# הרץ health check ישירות כדי לראות איפה זה תקוע
$ErrorActionPreference = 'Continue'
$job = Start-Job {
    $env:PYTHONUNBUFFERED=1
    python scripts/pre_test_health_check.py --env=staging
}
Wait-Job $job -Timeout 120  # 2 דקות
if ($job.State -eq "Running") {
    Write-Host "Health check תקוע! עוצר..."
    Stop-Job $job
    Remove-Job $job
} else {
    Receive-Job $job
    Remove-Job $job
}
```

---

### פתרון 2: דלג על Health Check (רק לבדיקה)

```powershell
# הרץ tests בלי health check (רק לבדיקה!)
py -m pytest be_focus_server_tests/ `
  -m "smoke" `
  --skip-health-check `
  -v `
  --maxfail=10 `
  --junitxml=test-results/junit-smoke.xml
```

**⚠️ אזהרה:** זה רק לבדיקה - לא מומלץ לייצור!

---

### פתרון 3: הרץ כל Check בנפרד

```powershell
# בדוק Focus Server
python -c "from scripts.pre_test_health_check import PreTestHealthChecker; from config.config_manager import ConfigManager; cm = ConfigManager('staging'); checker = PreTestHealthChecker(cm, 'staging'); result = checker.check_focus_server(); print(f'Focus Server: {result.status}')"

# בדוק SSH
python -c "from scripts.pre_test_health_check import PreTestHealthChecker; from config.config_manager import ConfigManager; cm = ConfigManager('staging'); checker = PreTestHealthChecker(cm, 'staging'); result = checker.check_ssh(); print(f'SSH: {result.status}')"

# בדוק Kubernetes
python -c "from scripts.pre_test_health_check import PreTestHealthChecker; from config.config_manager import ConfigManager; cm = ConfigManager('staging'); checker = PreTestHealthChecker(cm, 'staging'); result = checker.check_kubernetes(); print(f'Kubernetes: {result.status}')"

# בדוק MongoDB (זה יכול להיתקע!)
python -c "from scripts.pre_test_health_check import PreTestHealthChecker; from config.config_manager import ConfigManager; cm = ConfigManager('staging'); checker = PreTestHealthChecker(cm, 'staging'); result = checker.check_mongodb(); print(f'MongoDB: {result.status}')"

# בדוק RabbitMQ (זה יכול להיתקע!)
python -c "from scripts.pre_test_health_check import PreTestHealthChecker; from config.config_manager import ConfigManager; cm = ConfigManager('staging'); checker = PreTestHealthChecker(cm, 'staging'); result = checker.check_rabbitmq(); print(f'RabbitMQ: {result.status}')"
```

---

## 🔧 תיקון ארוך טווח

### הוסף Timeout לכל Check

ה-health check צריך לכלול timeout לכל check כדי למנוע היתקעות:

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout_context(seconds):
    """Context manager for function timeout."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# שימוש:
try:
    with timeout_context(30):  # 30 שניות timeout
        result = check_func()
except TimeoutError as e:
    result = HealthCheckResult(name, False, {}, str(e))
```

**⚠️ הערה:** `signal.SIGALRM` לא עובד ב-Windows! צריך פתרון אחר.

---

### פתרון ל-Windows: Threading עם Timeout

```python
import threading
from queue import Queue

def run_with_timeout(func, timeout_seconds):
    """Run function with timeout using threading."""
    result_queue = Queue()
    exception_queue = Queue()
    
    def target():
        try:
            result = func()
            result_queue.put(result)
        except Exception as e:
            exception_queue.put(e)
    
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout=timeout_seconds)
    
    if thread.is_alive():
        # Thread still running - timeout!
        return None, TimeoutError(f"Function timed out after {timeout_seconds} seconds")
    
    if not exception_queue.empty():
        return None, exception_queue.get()
    
    if not result_queue.empty():
        return result_queue.get(), None
    
    return None, RuntimeError("Function did not return a result")
```

---

## 📋 Checklist לבדיקה

1. **בדוק אם ה-process עדיין רץ:**
   ```powershell
   Get-Process python | Where-Object {$_.CPU -gt 0}
   ```

2. **בדוק את ה-Logs המלאים:**
   ```powershell
   $env:PYTHONUNBUFFERED=1
   python scripts/pre_test_health_check.py --env=staging 2>&1 | Tee-Object -FilePath health_check.log
   ```

3. **בדוק אם יש port-forward processes:**
   ```powershell
   Get-Process | Where-Object {$_.ProcessName -like "*kubectl*"}
   ```

4. **בדוק אם SSH עובד:**
   ```powershell
   ssh -o ConnectTimeout=10 prisma@10.10.10.150 "hostname"
   ```

5. **בדוק אם Kubernetes API עובד:**
   ```powershell
   kubectl get pods -n panda --timeout=10s
   ```

---

## 💡 המלצה

**הבעיה העיקרית היא כנראה:**
1. MongoDB check תקוע ב-`get_mongodb_status()` - Kubernetes API call
2. או RabbitMQ check תקוע ב-`start_port_forward()` - Port-forward setup

**פתרון מיידי:**
1. הרץ health check בנפרד עם timeout כדי לראות איפה זה תקוע
2. אם זה תקוע, דלג על health check (רק לבדיקה)
3. תיקן את ה-timeout handling ב-health check

**פתרון ארוך טווח:**
1. הוסף timeout לכל check function
2. הוסף better logging כדי לראות איפה בדיוק זה תקוע
3. שקול להריץ checks במקביל במקום ברצף

---

**עודכן:** 2025-11-29

