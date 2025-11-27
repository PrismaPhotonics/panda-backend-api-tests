# ניתוח: GRPC Job Template ConfigMap

**תאריך:** 2025-01-27  
**מקור:** הקובץ שהמשתמש שלח

---

## 🔍 סתירות בין הקובץ לתיעוד

### 1. CPU_USAGE_THRESHOLD

| מקור | ערך | השפעה |
|------|-----|--------|
| **תיעוד שלנו** | `1` millicore | Job נסגר רק אם CPU ≤ 1m |
| **קובץ בפועל** | `4` millicores | Job נסגר אם CPU ≤ 4m |

**השלכה:**
- עם threshold=4, ה-job נסגר מהר יותר (פחות רגיש)
- זה אומר שה-job יכול להיות יותר פעיל ועדיין להיסגר
- זמן כולל עדיין 50 שניות (5 בדיקות × 10 שניות)

---

## ⚠️ שגיאה בקוד

### שגיאה ב-RabbitMQ Cleanup

**שורה בעייתית:**
```bash
queue_name = $(curl -u prisma:prismapanda http://rabbitmq-panda:15672/api/queues | grep -o "\"name\":\"grpc-job-$JOB_ID-[^\"]*\"" | sed 's/"name":"//;s/"//')
```

**הבעיה:** יש רווח לפני ה-`=` - זה יגרום לשגיאה ב-shell script!

**צריך להיות:**
```bash
queue_name=$(curl -u prisma:prismapanda http://rabbitmq-panda:15672/api/queues | grep -o "\"name\":\"grpc-job-$JOB_ID-[^\"]*\"" | sed 's/"name":"//;s/"//')
```

**השפעה:**
- ה-RabbitMQ queue לא יימחק
- זה יכול לגרום לזליגת memory ב-RabbitMQ
- זה יכול לגרום לבעיות ביצועים

---

## 📊 מה הקובץ מראה לנו

### 1. מבנה ה-Jobs

✅ **grpc-job-$JOB_ID:**
- `ttlSecondsAfterFinished: 120` (2 דקות)
- Resource limits: GPU, CPU, Memory
- Port: 5000

✅ **grpc-service-$JOB_ID:**
- NodePort service
- Exposes gRPC server externally

✅ **cleanup-job-$JOB_ID:**
- `ttlSecondsAfterFinished: 10` (10 שניות)
- Monitors CPU usage
- Cleans up resources

### 2. מנגנון Cleanup

**Environment Variables:**
- `CPU_USAGE_THRESHOLD: "4"` ← **שונה מהתיעוד!**
- `ENABLE_CPU_USAGE_CHECK: "true"`
- `MAX_CPU_USAGE_COUNT: "5"`

**תהליך:**
1. בודק כל 10 שניות
2. אם CPU ≤ 4m במשך 5 בדיקות רצופות → cleanup
3. זמן כולל: 5 × 10s = **50 שניות**

### 3. מה ה-Cleanup עושה

1. **מחיקת Service:** `kubectl delete service grpc-service-$JOB_ID`
2. **מחיקת Job:** `kubectl delete job grpc-job-$JOB_ID --grace-period=0 --force`
3. **מחיקת Cleanup Job:** `kubectl delete job cleanup-job-$JOB_ID --grace-period=0 --force`
4. **מחיקת RabbitMQ Queue:** `curl -X DELETE ...` ← **יש שגיאה כאן!**

---

## 🎯 המלצות

### 1. לעדכן את התיעוד

**לעדכן:**
- `docs/07_infrastructure/JOB_DELETION_TIMELINE.md`
- `docs/07_infrastructure/GRPC_JOB_LIFECYCLE.md`
- כל מקום שמזכיר `CPU_USAGE_THRESHOLD: 1`

**לשנות ל:**
- `CPU_USAGE_THRESHOLD: 4` (millicores)

### 2. לתקן את השגיאה ב-RabbitMQ Cleanup

**להעביר לצוות Backend:**
- יש שגיאה בקוד ה-cleanup
- צריך לתקן את הרווח לפני ה-`=`
- זה יכול לגרום לזליגת memory ב-RabbitMQ

### 3. לעדכן את ה-Cleanup Fixtures

**אם צריך:**
- לבדוק אם threshold=4 משפיע על הזמנים
- אבל הזמן הכולל עדיין 50 שניות (5 × 10s)
- אז זה לא צריך להשפיע על ה-fixtures שלנו

---

## ✅ סיכום

1. **CPU_USAGE_THRESHOLD הוא 4, לא 1** - צריך לעדכן תיעוד
2. **יש שגיאה ב-RabbitMQ cleanup** - צריך לתקן
3. **הזמנים עדיין נכונים** - 50 שניות (5 × 10s)
4. **ה-cleanup שלנו תקין** - לא צריך לשנות

---

**נוצר:** 2025-01-27  
**עודכן:** 2025-01-27 - תיעוד עודכן ל-CPU_USAGE_THRESHOLD: 4  
**סטטוס:** ✅ **תיעוד עודכן, דורש תיקון ב-Backend**

