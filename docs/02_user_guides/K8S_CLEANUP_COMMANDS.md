# Kubernetes Cleanup Commands - Quick Reference
==============================================

**תאריך:** 2025-11-09  
**מטרה:** פקודות מהירות לניקוי gRPC jobs ו-pods

---

## ⚡ פקודת ניקוי מהירה (מומלץ!)

**מחיקת כל ה-gRPC jobs ו-cleanup jobs:**

```bash
kubectl get jobs -n panda -o name | grep -E "(grpc-job|cleanup-job)" | xargs -I {} kubectl delete {} -n panda
```

**פקודה זו:**
- ✅ מוצאת את כל ה-jobs (grpc-job-* ו-cleanup-job-*)
- ✅ מוחקת אותם (וגם את ה-pods שלהם)
- ✅ מונעת מה-pods להיווצר מחדש
- ✅ עובדת גם אם אין labels

**שימוש:**
```bash
# התחבר לשרת
ssh root@10.10.10.10
ssh prisma@10.10.10.150

# הרץ את הפקודה
kubectl get jobs -n panda -o name | grep -E "(grpc-job|cleanup-job)" | xargs -I {} kubectl delete {} -n panda
```

---

## ⚠️ בעיה נפוצה: Pods חוזרים אחרי מחיקה

**למה זה קורה?**  
ה-pods נוצרים על ידי Kubernetes Jobs. כשמוחקים pod, ה-Job יוצר pod חדש אוטומטית.

**הפתרון:** למחוק את ה-Jobs עצמם, לא רק את ה-pods!

---

## 🚀 דרך 1: K8s Agent (המומלץ)

```bash
python scripts/k8s_agent.py --env staging

# בתפריט:
# בחר 18 (Delete all gRPC jobs)
# בחר 2 (Delete gRPC + cleanup jobs)
```

---

## 🔧 דרך 2: kubectl ישירות (SSH לשרת)

### התחברות:

```bash
# Staging:
ssh root@10.10.10.10
ssh prisma@10.10.10.150

# Production:
ssh root@10.10.100.3
ssh prisma@10.10.100.113
```

### פקודות לניקוי:

#### 1. רשימת כל ה-jobs:
```bash
kubectl get jobs -n panda
```

#### 2. רשימת gRPC jobs בלבד:
```bash
kubectl get jobs -n panda | grep grpc-job
```

#### 3. רשימת cleanup jobs:
```bash
kubectl get jobs -n panda | grep cleanup-job
```

#### 4. מחיקת כל ה-gRPC jobs + cleanup jobs (הפתרון המומלץ!):
```bash
# ⭐ הפקודה המומלצת - מחיקה של כל ה-jobs בבת אחת
kubectl get jobs -n panda -o name | grep -E "(grpc-job|cleanup-job)" | xargs -I {} kubectl delete {} -n panda
```

#### 5. מחיקת רק gRPC jobs:
```bash
kubectl get jobs -n panda -o name | grep grpc-job | xargs -I {} kubectl delete {} -n panda
```

#### 6. מחיקת רק cleanup jobs:
```bash
kubectl get jobs -n panda -o name | grep cleanup-job | xargs -I {} kubectl delete {} -n panda
```

#### 7. דרכים חלופיות (אם xargs לא עובד):
```bash
# דרך 1: עם awk
kubectl get jobs -n panda | grep -E "(grpc-job|cleanup-job)" | awk '{print $1}' | xargs kubectl delete job -n panda

# דרך 2: עם while loop
kubectl get jobs -n panda -o name | grep -E "(grpc-job|cleanup-job)" | while read job; do kubectl delete $job -n panda; done

# דרך 3: עם jq (אם מותקן)
kubectl get jobs -n panda -o json | jq -r '.items[] | select(.metadata.name | startswith("grpc-job-") or startswith("cleanup-job-")) | .metadata.name' | xargs kubectl delete job -n panda
```

#### 7. מחיקה עם force (אם תקועים):
```bash
kubectl get jobs -n panda -o name | grep grpc-job | xargs -I {} kubectl delete {} -n panda --grace-period=0 --force
```

---

## 📋 פקודות נוספות שימושיות

### בדיקת pods לפני מחיקה:
```bash
# כל ה-pods
kubectl get pods -n panda

# רק gRPC job pods
kubectl get pods -n panda | grep grpc-job

# רק Pending pods
kubectl get pods -n panda --field-selector=status.phase=Pending
```

### מחיקת pods (אם צריך, אבל הם יחזרו!):
```bash
# מחיקת כל ה-Pending pods
kubectl delete pods -n panda --field-selector=status.phase=Pending

# מחיקת gRPC job pods לפי label (אם יש)
kubectl delete pods -n panda -l app=grpc-service
```

---

## 🎯 סקריפטים מהירים לניקוי

### סקריפט Bash (Linux/Mac):

הקובץ `scripts/k8s_cleanup_quick.sh` כולל את הפקודה המומלצת:

```bash
# הרצה ישירה
chmod +x scripts/k8s_cleanup_quick.sh
./scripts/k8s_cleanup_quick.sh

# או עם namespace אחר
./scripts/k8s_cleanup_quick.sh my-namespace
```

### סקריפט PowerShell (Windows):

הקובץ `scripts/k8s_cleanup_quick.ps1` להרצה מ-Windows:

```powershell
.\scripts\k8s_cleanup_quick.ps1
```

### סקריפט מותאם אישית:

צור קובץ `cleanup_grpc_jobs.sh`:

```bash
#!/bin/bash
# Cleanup all gRPC and cleanup jobs in panda namespace

NAMESPACE="panda"

echo "🔍 Finding gRPC jobs..."
GRPC_JOBS=$(kubectl get jobs -n $NAMESPACE -o name | grep grpc-job)
if [ -z "$GRPC_JOBS" ]; then
    echo "   No gRPC jobs found"
else
    echo "   Found $(echo "$GRPC_JOBS" | wc -l) gRPC job(s)"
fi

echo "🔍 Finding cleanup jobs..."
CLEANUP_JOBS=$(kubectl get jobs -n $NAMESPACE -o name | grep cleanup-job)
if [ -z "$CLEANUP_JOBS" ]; then
    echo "   No cleanup jobs found"
else
    echo "   Found $(echo "$CLEANUP_JOBS" | wc -l) cleanup job(s)"
fi

if [ -z "$GRPC_JOBS" ] && [ -z "$CLEANUP_JOBS" ]; then
    echo "✅ No jobs to delete"
    exit 0
fi

echo ""
read -p "⚠️  Delete all jobs? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 0
fi

echo ""
echo "🗑️  Deleting jobs..."

if [ ! -z "$GRPC_JOBS" ]; then
    echo "$GRPC_JOBS" | xargs -I {} kubectl delete {} -n $NAMESPACE
fi

if [ ! -z "$CLEANUP_JOBS" ]; then
    echo "$CLEANUP_JOBS" | xargs -I {} kubectl delete {} -n $NAMESPACE
fi

echo "✅ Done!"
```

הרצה:
```bash
chmod +x cleanup_grpc_jobs.sh
./cleanup_grpc_jobs.sh
```

---

## 💡 טיפים

1. **תמיד בדוק לפני מחיקה:**
   ```bash
   kubectl get jobs -n panda | grep grpc-job
   ```

2. **אם jobs תקועים ב-Terminating:**
   ```bash
   kubectl delete job <job-name> -n panda --grace-period=0 --force
   ```

3. **לבדוק pods אחרי מחיקת jobs:**
   ```bash
   kubectl get pods -n panda | grep grpc-job
   ```

4. **לניקוי אוטומטי, השתמש ב-K8s Agent:**
   ```bash
   python scripts/k8s_agent.py --env staging
   # בחר 18
   ```

---

## ⚠️ אזהרות

- **מחיקת jobs תעצור את העבודה** - ודא שזה מה שאתה רוצה!
- **בסביבת production** - היזהר במיוחד!
- **תמיד בדוק את הסביבה** לפני מחיקה
- **Jobs שנמחקו לא יכולים להיות משוחזרים**

---

**עדכון אחרון:** 2025-11-09

