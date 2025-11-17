# Kubernetes Quick Commands - Cheat Sheet
=========================================

**תאריך:** 2025-11-09  
**מטרה:** פקודות מהירות לשימוש יומיומי ב-Kubernetes

---

## ⚡ פקודת ניקוי מהירה (הכי חשובה!)

### מחיקת כל ה-gRPC jobs ו-cleanup jobs:

```bash
kubectl get jobs -n panda -o name | grep -E "(grpc-job|cleanup-job)" | xargs -I {} kubectl delete {} -n panda
```

**מתי להשתמש:**
- כשצריך לנקות את כל ה-jobs בבת אחת
- כש-pods חוזרים אחרי מחיקה (כי הם נוצרים על ידי Jobs)
- לניקוי מהיר לפני טסטים

**איך להריץ:**
```bash
# התחבר לשרת
ssh root@10.10.10.10
ssh prisma@10.10.10.150

# הרץ את הפקודה
kubectl get jobs -n panda -o name | grep -E "(grpc-job|cleanup-job)" | xargs -I {} kubectl delete {} -n panda
```

---

## 📋 פקודות נוספות שימושיות

### בדיקת jobs:
```bash
# כל ה-jobs
kubectl get jobs -n panda

# רק gRPC jobs
kubectl get jobs -n panda | grep grpc-job

# רק cleanup jobs
kubectl get jobs -n panda | grep cleanup-job

# ספירה
kubectl get jobs -n panda | grep -E "(grpc-job|cleanup-job)" | wc -l
```

### בדיקת pods:
```bash
# כל ה-pods
kubectl get pods -n panda

# רק gRPC job pods
kubectl get pods -n panda | grep grpc-job

# רק Pending pods
kubectl get pods -n panda --field-selector=status.phase=Pending

# ספירה
kubectl get pods -n panda | grep grpc-job | wc -l
```

### מחיקת pods (אבל הם יחזרו אם יש Jobs!):
```bash
# מחיקת Pending pods
kubectl delete pods -n panda --field-selector=status.phase=Pending

# מחיקת gRPC job pods לפי pattern
kubectl get pods -n panda | grep grpc-job | awk '{print $1}' | xargs kubectl delete pod -n panda
```

---

## 🔧 פקודות ניהול

### לוגים:
```bash
# לוגים של pod
kubectl logs -n panda <pod-name>

# לוגים עם follow
kubectl logs -n panda <pod-name> -f

# לוגים של job
kubectl logs -n panda -l job-name=<job-name>
```

### תיאור resource:
```bash
# תיאור pod
kubectl describe pod -n panda <pod-name>

# תיאור job
kubectl describe job -n panda <job-name>
```

### YAML export:
```bash
# Export job ל-YAML
kubectl get job -n panda <job-name> -o yaml

# Export pod ל-YAML
kubectl get pod -n panda <pod-name> -o yaml
```

---

## 🚀 שימוש ב-K8s Agent

```bash
# הפעלה
python scripts/k8s_agent.py --env staging

# פקודות שימושיות:
# 18 - מחיקת כל ה-gRPC jobs (מומלץ!)
# 13 - מחיקת pods לפי status
# 9  - מחיקת כל ה-gRPC job pods
```

---

## 💡 טיפים

1. **תמיד בדוק לפני מחיקה:**
   ```bash
   kubectl get jobs -n panda | grep grpc-job
   ```

2. **אם jobs תקועים:**
   ```bash
   kubectl delete job <job-name> -n panda --grace-period=0 --force
   ```

3. **לניקוי מהיר, השתמש בסקריפט:**
   ```bash
   ./scripts/k8s_cleanup_quick.sh
   ```

---

**עדכון אחרון:** 2025-11-09

