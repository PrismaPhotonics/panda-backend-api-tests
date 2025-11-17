# איך להריץ את הטסט של 200 Jobs

## 🎯 הטסט:
`Test200ConcurrentJobsCapacity.test_200_concurrent_jobs_target_capacity`

## 🚀 הפקודות:

### פקודה בסיסית:
```powershell
pytest tests/load/test_job_capacity_limits.py::Test200ConcurrentJobsCapacity::test_200_concurrent_jobs_target_capacity -v
```

### פקודה עם markers:
```powershell
pytest tests/load/test_job_capacity_limits.py -m "capacity and critical" -v
```

### פקודה עם סביבה ספציפית:
```powershell
# הרץ על staging
pytest tests/load/test_job_capacity_limits.py::Test200ConcurrentJobsCapacity::test_200_concurrent_jobs_target_capacity -v --env=staging

# הרץ על new_production (אם קיים)
pytest tests/load/test_job_capacity_limits.py::Test200ConcurrentJobsCapacity::test_200_concurrent_jobs_target_capacity -v --env=new_production
```

### פקודה עם output מפורט:
```powershell
pytest tests/load/test_job_capacity_limits.py::Test200ConcurrentJobsCapacity::test_200_concurrent_jobs_target_capacity -v -s --tb=short
```

### פקודה עם log level:
```powershell
pytest tests/load/test_job_capacity_limits.py::Test200ConcurrentJobsCapacity::test_200_concurrent_jobs_target_capacity -v --log-cli-level=INFO
```

## 📝 הסבר:

- **הטסט בודק:** יכולת המערכת להתמודד עם 200 concurrent jobs
- **הבאג:** PZ-13986 - 200 Jobs Capacity Issue
- **התוצאה הצפויה:** כנראה רק 40/200 jobs יצליחו (20% success rate)

## ⚠️ לפני ההרצה:

1. **נקה grpc-services ישנים:**
```bash
# מהשרת worker-node:
kubectl get svc -n panda | grep grpc-service | awk '{print $1}' | xargs kubectl delete svc -n panda
kubectl get jobs -n panda | grep grpc-job | awk '{print $1}' | xargs kubectl delete job -n panda
```

2. **וודא שהסביבה נכונה:**
```powershell
# בדוק את הסביבה בקונפיג
Get-Content config/environments.yaml | Select-String -Pattern "base_url"
```

## 🔍 אחרי ההרצה:

הטסט ייצור דוח Infrastructure Gap אם יש בעיית קיבולת.

---

**הפקודה הכי פשוטה:**
```powershell
pytest tests/load/test_job_capacity_limits.py::Test200ConcurrentJobsCapacity -v -s
```
