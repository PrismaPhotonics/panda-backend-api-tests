# אבחון: למה Smoke Tests תקועים?

**תאריך:** 2025-11-29  
**Workflow:** Smoke Tests #204  
**סטטוס:** תקוע אחרי Kubernetes health check

---

## 🔍 מה קורה?

הלוגים מראים שהתהליך תקוע אחרי:
```
[3/5] Checking Kubernetes... ✅ OK
   ✓ Focus Server deployment found (ready: 1/1)
```

אבל לא ממשיך ל:
- `[4/5] Checking MongoDB...`
- `[5/5] Checking RabbitMQ...`

---

## 🎯 סיבות אפשריות (לפי סדר סבירות)

### 1. **MongoDB Check תקוע** (הכי סביר)

**מה קורה:**
- Health check מנסה להריץ `check_mongodb()`
- זה קורא ל-`mongodb_manager.get_mongodb_status()`
- `get_mongodb_status()` קורא ל-`kubernetes_manager.get_deployments()`
- `get_deployments()` משתמש ב-SSH fallback עם timeout של 30 שניות
- **אבל:** אם ה-SSH connection עצמו תקוע, ה-timeout לא יעזור

**איך לבדוק:**
```powershell
# בדוק אם MongoDB check תקוע (שימוש בסקריפט מיוחד)
python scripts/test_health_check_individual.py --check=mongodb --timeout=60

# או ישירות:
python -c "
from scripts.pre_test_health_check import PreTestHealthChecker
import time

checker = PreTestHealthChecker('staging')
print('Starting MongoDB check...')
start = time.time()
try:
    result = checker.check_mongodb()
    elapsed = time.time() - start
    print(f'MongoDB check completed in {elapsed:.2f}s: {result.status}')
except Exception as e:
    elapsed = time.time() - start
    print(f'MongoDB check failed after {elapsed:.2f}s: {e}')
"
```

**פתרון:**
- אם זה תקוע יותר מ-60 שניות, זה כנראה תקוע
- נסה לעצור את ה-process ולהריץ health check בנפרד

---

### 2. **RabbitMQ Check תקוע ב-Port-Forward** (סביר)

**מה קורה:**
- Health check מנסה להריץ `check_rabbitmq()`
- זה קורא ל-`rabbitmq_manager.setup()`
- `setup()` קורא ל-`start_port_forward()`
- `start_port_forward()` מחכה עד 15 שניות שהפורט יהיה פתוח
- **אבל:** אם ה-`_check_port_open()` תקוע, זה יכול להיתקע

**איך לבדוק:**
```powershell
# בדוק אם יש port-forward process רץ
Get-Process | Where-Object {$_.ProcessName -like "*kubectl*"}

# בדוק אם הפורט פתוח
Test-NetConnection -ComputerName 10.10.10.150 -Port 5672 -InformationLevel Detailed
```

**פתרון:**
- אם יש kubectl process רץ, זה יכול להיות port-forward תקוע
- נסה לעצור את ה-process: `Stop-Process -Name kubectl -Force`

---

### 3. **SSH Connection תקוע** (פחות סביר)

**מה קורה:**
- אחרי Kubernetes check, MongoDB check צריך SSH connection
- אם ה-SSH connection תקוע, זה יכול להיתקע

**איך לבדוק:**
```powershell
# בדוק אם SSH עובד
ssh -o ConnectTimeout=10 prisma@10.10.10.150 "hostname"

# בדוק אם יש SSH processes רץ
Get-Process | Where-Object {$_.ProcessName -like "*ssh*"}
```

---

## ✅ פתרונות מהירים

### פתרון 1: הרץ Health Check בנפרד עם Timeout

```powershell
# הרץ health check ישירות כדי לראות איפה זה תקוע
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

### פתרון 3: בדוק כל Check בנפרד

```powershell
# Focus Server (1/5)
python -c "from scripts.pre_test_health_check import PreTestHealthChecker; checker = PreTestHealthChecker('staging'); result = checker.check_focus_server(); print(f'[1/5] Focus Server: {result.status}')"

# SSH (2/5)
python -c "from scripts.pre_test_health_check import PreTestHealthChecker; checker = PreTestHealthChecker('staging'); result = checker.check_ssh(); print(f'[2/5] SSH: {result.status}')"

# Kubernetes (3/5)
python -c "from scripts.pre_test_health_check import PreTestHealthChecker; checker = PreTestHealthChecker('staging'); result = checker.check_kubernetes(); print(f'[3/5] Kubernetes: {result.status}')"

# MongoDB (4/5) - זה יכול להיתקע!
python -c "from scripts.pre_test_health_check import PreTestHealthChecker; import time; checker = PreTestHealthChecker('staging'); start = time.time(); result = checker.check_mongodb(); elapsed = time.time() - start; print(f'[4/5] MongoDB: {result.status} (took {elapsed:.2f}s)')"

# RabbitMQ (5/5) - זה יכול להיתקע!
python -c "from scripts.pre_test_health_check import PreTestHealthChecker; import time; checker = PreTestHealthChecker('staging'); start = time.time(); result = checker.check_rabbitmq(); elapsed = time.time() - start; print(f'[5/5] RabbitMQ: {result.status} (took {elapsed:.2f}s)')"
```

---

## 🔧 תיקון ארוך טווח

### הוסף Timeout Wrapper לכל Check

ה-health check צריך לכלול timeout לכל check כדי למנוע היתקעות:

```python
# scripts/pre_test_health_check.py
import threading
from queue import Queue

def run_check_with_timeout(check_func, timeout_seconds=60):
    """Run health check function with timeout."""
    result_queue = Queue()
    exception_queue = Queue()
    
    def target():
        try:
            result = check_func()
            result_queue.put(result)
        except Exception as e:
            exception_queue.put(e)
    
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout=timeout_seconds)
    
    if thread.is_alive():
        # Thread still running - timeout!
        return HealthCheckResult(
            name="Timeout",
            status=False,
            details={},
            error=f"Health check timed out after {timeout_seconds} seconds"
        )
    
    if not exception_queue.empty():
        raise exception_queue.get()
    
    if not result_queue.empty():
        return result_queue.get()
    
    raise RuntimeError("Health check did not return a result")

# שימוש:
result = run_check_with_timeout(lambda: self.check_mongodb(), timeout_seconds=60)
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
1. MongoDB check תקוע ב-`get_mongodb_status()` - Kubernetes API call דרך SSH
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

## 📝 מה לעשות עכשיו?

1. **עצור את ה-Workflow התקוע:**
   - לך ל-GitHub Actions
   - לחץ על "Cancel workflow"

2. **הרץ Health Check בנפרד:**
   ```powershell
   python scripts/pre_test_health_check.py --env=staging
   ```
   - אם זה תקוע יותר מ-2 דקות, זה כנראה תקוע

3. **אם זה תקוע, נסה לבדוק כל check בנפרד:**
   ```powershell
   # השתמש בסקריפט המיוחד לבדיקת checks בנפרד
   python scripts/test_health_check_individual.py --check=mongodb --timeout=60
   python scripts/test_health_check_individual.py --check=rabbitmq --timeout=60
   
   # או הרץ את כל ה-checks:
   python scripts/test_health_check_individual.py --check=all --timeout=60
   ```
   זה יעזור לך לזהות איזה check תקוע

4. **דווח על התוצאות:**
   - איזה check תקוע?
   - כמה זמן זה לקח?
   - מה ה-error message?

---

**עודכן:** 2025-11-29

