# תיקון: Smoke Tests תקועים ב-Kubernetes Health Check

**תאריך:** 2025-11-29  
**בעיה:** Health check תקוע ב-`get_pods()` יותר מ-14 דקות  
**פתרון:** הוספת timeout handling ל-`get_pods()` ו-`execute_command()`

---

## 🔍 הבעיה

התהליך היה תקוע ב-Kubernetes health check אחרי שמצא את ה-deployment:
```
[3/5] Checking Kubernetes... 
   ✓ Focus Server deployment found (ready: 1/1)
```

אבל לא המשיך ל-MongoDB או RabbitMQ checks. אחרי 15 דקות ה-workflow בוטל.

---

## 🎯 סיבת השורש

1. **`get_pods()` תקוע** - ה-kubectl command דרך SSH לוקח הרבה זמן או תקוע
2. **`execute_command()` ללא timeout אמיתי** - `recv_exit_status()` יכול להיתקע לנצח
3. **אין timeout wrapper** - ה-health check לא מטפל ב-timeout של `get_pods()`

---

## ✅ התיקון

### 1. תיקון `execute_command()` ב-SSH Manager

**קובץ:** `src/infrastructure/ssh_manager.py`

**מה תוקן:**
- הוספת `socket.timeout` handling
- הוספת `channel.settimeout()` לפני `recv_exit_status()`
- הוספת error handling טוב יותר

**קוד:**
```python
# Set timeout on channel to prevent hanging
stdout.channel.settimeout(timeout)
stderr.channel.settimeout(timeout)

# Wait for command to complete with timeout
try:
    exit_code = stdout.channel.recv_exit_status()
except socket.timeout:
    raise InfrastructureError(f"Command timed out after {timeout} seconds: {command}")
```

---

### 2. תיקון `check_kubernetes()` ב-Health Check

**קובץ:** `scripts/pre_test_health_check.py`

**מה תוקן:**
- הוספת timeout wrapper ל-`get_pods()` עם threading
- אם `get_pods()` לוקח יותר מ-60 שניות, זה נכשל עם warning
- ה-health check ממשיך גם אם pods check נכשל

**קוד:**
```python
# Add timeout wrapper to prevent hanging
import threading
from queue import Queue

pods_queue = Queue()
exception_queue = Queue()

def get_pods_thread():
    try:
        pods = k8s_manager.get_pods()
        pods_queue.put(pods)
    except Exception as e:
        exception_queue.put(e)

thread = threading.Thread(target=get_pods_thread, daemon=True)
thread.start()
thread.join(timeout=60)  # 60 second timeout

if thread.is_alive():
    # Thread still running - timeout!
    details["Pods"] = "Timeout (took >60s)"
    self.logger.warning(f"{name}: get_pods() timed out after 60 seconds")
```

---

## 📋 מה השתנה?

### לפני התיקון:
- `get_pods()` יכול להיתקע לנצח
- `execute_command()` לא מטפל ב-timeout של `recv_exit_status()`
- Health check תקוע ולא ממשיך

### אחרי התיקון:
- `get_pods()` יש לו timeout של 60 שניות
- `execute_command()` מטפל ב-timeout נכון
- Health check ממשיך גם אם pods check נכשל

---

## 🧪 איך לבדוק?

### בדיקה מקומית:
```powershell
# הרץ health check
python scripts/pre_test_health_check.py --env=staging

# אם זה תקוע יותר מ-2 דקות, זה עדיין תקוע
# אבל עכשיו זה צריך להיכשל עם timeout message
```

### בדיקה ב-GitHub Actions:
1. Push את השינויים
2. בדוק את ה-workflow
3. Health check צריך להמשיך גם אם pods check נכשל

---

## 💡 המלצות נוספות

### 1. הגדל את ה-timeout של `get_pods()`
אם יש הרבה pods, אפשר להגדיל את ה-timeout:
```python
thread.join(timeout=120)  # 2 דקות במקום 60 שניות
```

### 2. הוסף timeout לכל health check
אפשר להוסיף timeout wrapper לכל check:
```python
def run_check_with_timeout(check_func, timeout_seconds=60):
    # ... timeout wrapper code ...
```

### 3. שפר את ה-logging
הוסף יותר logging כדי לראות איפה בדיוק זה תקוע:
```python
self.logger.info(f"Starting get_pods() with timeout {timeout}s...")
```

---

## 📝 קבצים ששונו

1. `src/infrastructure/ssh_manager.py`
   - הוספת timeout handling ל-`execute_command()`
   - הוספת `socket` import

2. `scripts/pre_test_health_check.py`
   - הוספת timeout wrapper ל-`get_pods()` ב-`check_kubernetes()`
   - הוספת `threading` ו-`Queue` imports

---

## ✅ סטטוס

- [x] תיקון `execute_command()` ב-SSH Manager
- [x] תיקון `check_kubernetes()` ב-Health Check
- [x] בדיקת linter errors
- [ ] בדיקה ב-GitHub Actions
- [ ] בדיקה מקומית

---

**עודכן:** 2025-11-29

