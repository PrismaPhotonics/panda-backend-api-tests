# שימוש בסקריפט בדיקת בריאות המערכת

## הרצה ידנית לפני טסטים

```powershell
# הפעלת הסקריפט ישירות
python scripts/pre_test_health_check.py

# עם environment ספציפי
python scripts/pre_test_health_check.py --env=staging

# עם יצירת דוח
python scripts/pre_test_health_check.py --env=staging --report=health_report.md
```

## הרצה אוטומטית לפני pytest

### אפשרות 1: עם flag מפורש

```powershell
# הפעלת בדיקות בריאות לפני הטסטים
pytest --run-health-check tests/

# דילוג על בדיקות בריאות
pytest --skip-health-check tests/
```

### אפשרות 2: עם environment variable

```powershell
# הגדרת environment variable להפעלה אוטומטית
$env:AUTO_HEALTH_CHECK="true"
pytest tests/

# או ב-PowerShell
$env:AUTO_HEALTH_CHECK="true"; pytest tests/
```

## מה הסקריפט בודק?

1. **Focus Server API**
   - חיבור ל-API
   - Health check endpoint (`/ack`)
   - Channels endpoint (`/channels`)

2. **MongoDB**
   - חיבור למסד הנתונים
   - Authentication
   - סטטוס דרך Kubernetes (אם זמין)

3. **Kubernetes**
   - חיבור ל-Kubernetes API (ישיר או SSH fallback)
   - מידע על הקלסטר
   - סטטוס deployments (בעיקר Focus Server)
   - סטטוס pods (running, pending)
   - כמות gRPC jobs פעילים

4. **RabbitMQ**
   - חיבור ל-RabbitMQ
   - זמינות service

5. **SSH**
   - חיבור ל-jump host
   - ביצוע פקודות דרך SSH

## Exit Codes

- **0** - כל הקומפוננטות תקינות ✅
- **1** - יש בעיות בקומפוננטות ❌

## דוגמת פלט

```
================================================================================
Pre-Test System Health Check - STAGING
================================================================================

Running health checks...

✅ Focus Server API: OK
   Base URL: https://10.10.10.100/focus-server/
   Health Check: OK
   Status Code: 200
   Channels Endpoint: OK
   Channel Range: 0-100

✅ MongoDB: OK
   Connection: OK
   Status Check: OK
   Connected: True
   Ready Replicas: 1
   Total Replicas: 1

✅ Kubernetes: OK
   Connection Method: SSH Fallback
   Cluster Version: v1.28.0
   Node Count: 2
   Deployments: 5
   Focus Server Deployment: Found
   Focus Server Ready: 1
   Focus Server Total: 1
   Total Pods: 15
   Running Pods: 12
   Pending Pods: 0
   gRPC Jobs: 3

✅ RabbitMQ: OK
   Connection: OK
   Host: 10.10.100.107
   Port: 5672

✅ SSH: OK
   Connection: OK
   Command Execution: OK
   Hostname: k8s-host

================================================================================
Summary
================================================================================

Total Checks: 5
Passed: 5
Failed: 0

✅ All components are healthy! Ready to run tests.
```

## שילוב ב-CI/CD

```yaml
# GitHub Actions example
- name: Pre-test Health Check
  run: |
    python scripts/pre_test_health_check.py --env=staging
    if [ $? -ne 0 ]; then
      echo "Health checks failed!"
      exit 1
    fi

- name: Run Tests
  run: pytest tests/
```

## הערות

- הסקריפט משתמש ב-`ConfigManager` כדי לקבל את ההגדרות
- אם יש בעיה בקומפוננטה, הסקריפט יציג פרטים על הבעיה
- ניתן לדלג על הבדיקות עם `--skip-health-check` אם צריך
- הסקריפט תומך ב-colorama לצבעים, אבל יעבוד גם בלי זה

