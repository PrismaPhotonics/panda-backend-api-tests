# 🚀 איך להריץ את טסטי K8s Job Lifecycle
## How to Run K8s Job Lifecycle Tests

**תאריך:** 2025-11-13  
**סביבה:** Staging

---

## 📋 פקודות להרצה

### 1. פקודה בסיסית (PowerShell)

```powershell
cd C:\Projects\focus_server_automation
py -m pytest be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py -v --tb=short --skip-health-check --log-cli-level=INFO
```

---

### 2. פקודה עם לוגים מפורטים (PowerShell)

```powershell
cd C:\Projects\focus_server_automation
py -m pytest be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py `
    -v `
    --tb=short `
    --skip-health-check `
    --log-cli-level=INFO `
    --log-cli-format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s" `
    --log-cli-date-format="%Y-%m-%d %H:%M:%S"
```

---

### 3. שימוש בסקריפט (PowerShell)

```powershell
cd C:\Projects\focus_server_automation
.\scripts\run_k8s_job_lifecycle_tests.ps1
```

**עם אפשרויות:**
```powershell
# עם skip-health-check
.\scripts\run_k8s_job_lifecycle_tests.ps1 -SkipHealthCheck

# עם verbose mode
.\scripts\run_k8s_job_lifecycle_tests.ps1 -Verbose

# עם log level
.\scripts\run_k8s_job_lifecycle_tests.ps1 -LogLevel DEBUG
```

---

### 4. פקודה בסיסית (Bash/Linux)

```bash
cd /path/to/focus_server_automation
python -m pytest be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py -v --tb=short --skip-health-check --log-cli-level=INFO
```

---

### 5. שימוש בסקריפט (Bash/Linux)

```bash
cd /path/to/focus_server_automation
chmod +x scripts/run_k8s_job_lifecycle_tests.sh
./scripts/run_k8s_job_lifecycle_tests.sh
```

---

## 📊 מה הטסטים בודקים

### 1. `test_k8s_job_creation_triggers_pod_spawn` ✅
- Job creation
- Pod discovery (by name or app label)
- Pod labels verification
- Pod status (Running)

### 2. `test_k8s_job_resource_allocation` ✅
- Pod resource info
- Pod status and readiness

### 3. `test_k8s_job_port_exposure` ✅
- Pod discovery
- Stream port verification

### 4. `test_k8s_job_observability` ✅
- Pod logs retrieval
- Pod events retrieval
- Pod status details

### 5. `test_k8s_job_cancellation_and_cleanup` ⏭️
- Job cancellation (may be skipped if endpoint not implemented)
- Pod termination verification

---

## 🔍 איך לבדוק את התוצאות

### 1. בדיקת Exit Code

```powershell
# אם Exit Code = 0 → כל הטסטים עברו או נדחו כראוי
# אם Exit Code != 0 → יש טסטים שנכשלו
```

### 2. בדיקת לוגים

**לוגים נשמרים ב:**
- `logs/test_runs/YYYY-MM-DD_HH-MM-SS_infrastructure_tests.log` - כל הלוגים
- `logs/warnings/YYYY-MM-DD_HH-MM-SS_infrastructure_tests_WARNINGS.log` - אזהרות
- `logs/errors/YYYY-MM-DD_HH-MM-SS_infrastructure_tests_ERRORS.log` - שגיאות

**איך לבדוק:**
```powershell
# לראות את הלוגים האחרונים
Get-Content logs\test_runs\*.log -Tail 100

# לחפש שגיאות
Select-String -Path logs\test_runs\*.log -Pattern "ERROR|FAILED"

# לחפש Pods שנמצאו
Select-String -Path logs\test_runs\*.log -Pattern "Pod found"
```

---

### 3. בדיקת תוצאות ספציפיות

**לבדוק כמה טסטים עברו:**
```powershell
py -m pytest be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py -v --tb=line --skip-health-check 2>&1 | Select-String "passed|failed|skipped"
```

**לבדוק טסט ספציפי:**
```powershell
py -m pytest be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py::TestK8sJobCreation::test_k8s_job_creation_triggers_pod_spawn -v --skip-health-check
```

---

## 📝 דוגמה: פלט צפוי

```
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-8.4.2
collected 5 items

be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py::TestK8sJobCreation::test_k8s_job_creation_triggers_pod_spawn PASSED
be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py::TestK8sResourceAllocation::test_k8s_job_resource_allocation PASSED
be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py::TestK8sPortExposure::test_k8s_job_port_exposure PASSED
be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py::TestK8sJobObservability::test_k8s_job_observability PASSED
be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py::TestK8sJobCancellation::test_k8s_job_cancellation_and_cleanup SKIPPED

============= 4 passed, 1 skipped, 1 warning in 75.54s =======================
```

---

## ⚙️ אפשרויות נוספות

### הרצה עם coverage
```powershell
py -m pytest be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py -v --skip-health-check --cov=src --cov-report=html
```

### הרצה עם HTML report
```powershell
py -m pytest be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py -v --skip-health-check --html=reports/k8s_job_lifecycle_report.html --self-contained-html
```

### הרצה עם parallel execution
```powershell
py -m pytest be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py -v --skip-health-check -n auto
```

---

## 🐛 פתרון בעיות

### בעיה: "Kubernetes not available"
**פתרון:** הטסטים משתמשים ב-SSH fallback, זה אמור לעבוד אוטומטית.

### בעיה: "DELETE /job/{job_id} endpoint not implemented"
**פתרון:** זה תקין - הטסט נדחה כראוי. זה באג ב-Backend.

### בעיה: "Pod not found"
**פתרון:** בדוק שהסביבה Staging פעילה ויש Pods.

---

## 📚 קבצים קשורים

- `be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py` - הטסטים
- `scripts/run_k8s_job_lifecycle_tests.ps1` - סקריפט PowerShell
- `scripts/run_k8s_job_lifecycle_tests.sh` - סקריפט Bash
- `docs/04_testing/analysis/TESTS_FIXED_FINAL_SUMMARY.md` - סיכום תיקונים

---

**מחבר:** AI Assistant  
**תאריך:** 2025-11-13

