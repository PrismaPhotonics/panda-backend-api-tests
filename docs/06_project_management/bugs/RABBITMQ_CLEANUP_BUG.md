# 🐛 Bug: RabbitMQ Queue Cleanup Failure

**תאריך:** 2025-01-27  
**חומרה:** גבוהה  
**סטטוס:** 🔴 **דורש תיקון מיידי**

---

## 📋 סיכום

יש שגיאה בקוד ה-cleanup של gRPC jobs שגורמת לכך ש-RabbitMQ queues לא נמחקים. זה יכול לגרום לזליגת memory ולבעיות ביצועים.

---

## 🔍 תיאור הבעיה

### מיקום השגיאה

**קובץ:** `grpc-job-template` ConfigMap  
**שורה:** בשורת ה-RabbitMQ cleanup script

### הקוד השגוי

```bash
# Cleanup RabbitMQ queue associated with this job
queue_name = $(curl -u prisma:prismapanda http://rabbitmq-panda:15672/api/queues | grep -o "\"name\":\"grpc-job-$JOB_ID-[^\"]*\"" | sed 's/"name":"//;s/"//')

curl -u prisma:prismapanda -X DELETE http://rabbitmq-panda:15672/api/queues/%2F/$queue_name
```

**הבעיה:** יש רווח לפני ה-`=` בשורה הראשונה. זה גורם לשגיאה ב-shell script כי bash לא מזהה את זה כהשמה של משתנה.

---

## ⚠️ השפעה

### בעיות מיידיות:
1. **RabbitMQ queues לא נמחקים** - כל queue שנוצר עבור job נשאר ב-RabbitMQ
2. **זליגת memory** - queues מצטברים ולא נמחקים
3. **בעיות ביצועים** - ככל שיש יותר queues, RabbitMQ עובד יותר לאט

### השפעה ארוכת טווח:
- **עומס על RabbitMQ** - מאות או אלפי queues שלא נמחקים
- **בעיות זיכרון** - RabbitMQ יכול להיגמר מ-memory
- **בעיות ביצועים** - חיפוש queues לוקח יותר זמן

---

## ✅ תיקון נדרש

### הקוד המתוקן

```bash
# Cleanup RabbitMQ queue associated with this job
queue_name=$(curl -u prisma:prismapanda http://rabbitmq-panda:15672/api/queues | grep -o "\"name\":\"grpc-job-$JOB_ID-[^\"]*\"" | sed 's/"name":"//;s/"//')

curl -u prisma:prismapanda -X DELETE http://rabbitmq-panda:15672/api/queues/%2F/$queue_name
```

**השינוי:** הסרת הרווח לפני ה-`=` בשורה הראשונה.

---

## 🔧 איך לתקן

### שלב 1: מצא את הקובץ

הקובץ נמצא ב-ConfigMap:
```bash
kubectl get configmap grpc-job-template -n panda -o yaml
```

או בקובץ המקור:
```
/mnt/panda/offline_deploy/linux-infra/charts/panda/templates/grpc-job/job.yml
```

### שלב 2: תקן את השגיאה

הסר את הרווח לפני ה-`=` בשורה:
```bash
queue_name = $(curl...
```

להפוך ל:
```bash
queue_name=$(curl...
```

### שלב 3: עדכן את ה-ConfigMap

אם זה ConfigMap:
```bash
kubectl apply -f <fixed-configmap-file>.yaml
```

או אם זה Helm chart:
```bash
helm upgrade panda <chart-path>
```

---

## 📊 בדיקות

### איך לבדוק שהתיקון עובד:

1. **צור job חדש:**
   ```bash
   # Create a test job
   curl -X POST http://focus-server/configure ...
   ```

2. **בדוק ש-queue נוצר:**
   ```bash
   curl -u prisma:prismapanda http://rabbitmq-panda:15672/api/queues | grep grpc-job
   ```

3. **חכה ל-cleanup (50 שניות):**
   ```bash
   sleep 60
   ```

4. **בדוק ש-queue נמחק:**
   ```bash
   curl -u prisma:prismapanda http://rabbitmq-panda:15672/api/queues | grep grpc-job
   # Should return empty or not find the queue
   ```

---

## 🎯 עדיפות

**גבוהה** - זה יכול לגרום לבעיות ביצועים חמורות אם יש הרבה jobs.

---

## 📝 הערות

- השגיאה נמצאת ב-cleanup script של `cleanup-job-$JOB_ID`
- זה לא משפיע על מחיקת ה-Kubernetes Jobs (זה עובד)
- זה משפיע רק על RabbitMQ queues

---

## 🔗 קישורים רלוונטיים

- [GRPC Job Lifecycle](../../07_infrastructure/GRPC_JOB_LIFECYCLE.md)
- [Job Deletion Timeline](../../07_infrastructure/JOB_DELETION_TIMELINE.md)

---

**נוצר:** 2025-01-27  
**דורש תיקון:** ✅ **כן**

