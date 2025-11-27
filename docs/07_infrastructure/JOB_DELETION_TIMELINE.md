# Job Deletion Timeline - מתי Job נמחק?
# Job Deletion Timeline - When is a Job Deleted?

**תאריך עדכון:** 19 בנובמבר 2025  
**מקור:** שיחה עם צוות Backend + תיעוד טכני

---

## 📊 סיכום מהיר - Job Deletion Timeline

| תרחיש | זמן עד מחיקה | מנגנון |
|-------|-------------|--------|
| **Job לא פותחים אותו** (לא מתחברים) | **~50 שניות** | Cleanup job מזהה CPU נמוך |
| **Job מסתיים** (Complete/Failed) | **2 דקות** | TTL (ttlSecondsAfterFinished: 120) |
| **Stream ללא פעילות** | **3 דקות** | gRPC Timeout (180s) |

---

## 🔍 פירוט מפורט

### תרחיש 1: Job לא פותחים אותו (~50 שניות)

**מה קורה:**
- Job נוצר (`POST /configure`) אבל הלקוח לא מתחבר ל-gRPC stream
- ה-Job רץ אבל לא מזרים נתונים (CPU נמוך)

**מנגנון:**
- `cleanup-job-$JOB_ID` בודק את ה-CPU של `grpc-job-$JOB_ID` כל **10 שניות**
- אם CPU ≤ 4m (millicores) במשך **5 בדיקות רצופות** → מתחיל cleanup
- זמן כולל: **5 × 10s = 50 שניות**

**קוד רלוונטי:**
```yaml
Environment Variables:
  CPU_USAGE_THRESHOLD: 4        # 4 millicores
  ENABLE_CPU_USAGE_CHECK: true
  MAX_CPU_USAGE_COUNT: 5        # 5 consecutive checks
```

**תהליך:**
```
Job Created → Cleanup Job Starts Monitoring
    ↓
Check 1 (0s): CPU ≤ 4m → count = 1
Check 2 (10s): CPU ≤ 4m → count = 2
Check 3 (20s): CPU ≤ 4m → count = 3
Check 4 (30s): CPU ≤ 4m → count = 4
Check 5 (40s): CPU ≤ 4m → count = 5 → CLEANUP TRIGGERED
    ↓
Cleanup Process (~10s)
    ↓
Job Deleted (~50 seconds total)
```

---

### תרחיש 2: Job מסתיים (2 דקות)

**מה קורה:**
- Kubernetes Job מסתיים בהצלחה (`Complete`) או נכשל (`Failed`)
- ה-Job כבר לא רץ, אבל ה-Kubernetes Job object עדיין קיים

**מנגנון:**
- Kubernetes `ttlSecondsAfterFinished: 120` → Job נמחק אוטומטית אחרי **2 דקות**

**קוד רלוונטי:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: grpc-job-$JOB_ID
spec:
  ttlSecondsAfterFinished: 120  # Auto-delete after 2 minutes
```

**תהליך:**
```
Job Completes/Fails → Kubernetes marks as finished
    ↓
Wait 120 seconds (2 minutes)
    ↓
Kubernetes automatically deletes Job object
```

---

### תרחיש 3: Stream ללא פעילות (3 דקות)

**מה קורה:**
- הלקוח התחבר ל-gRPC stream אבל אין פעילות
- ה-stream פתוח אבל לא מזרים נתונים

**מנגנון:**
- gRPC Timeout של **180 שניות (3 דקות)**
- אחרי 3 דקות ללא פעילות → Job נסגר אוטומטית

**תהליך:**
```
Client Connects → gRPC Stream Opens
    ↓
No Activity for 180 seconds (3 minutes)
    ↓
gRPC Timeout Triggered
    ↓
Job Closed Automatically
```

---

## 🔄 השוואה בין התרחישים

| קריטריון | Job לא פותחים | Job מסתיים | Stream ללא פעילות |
|----------|---------------|------------|-------------------|
| **זמן** | ~50 שניות | 2 דקות | 3 דקות |
| **מנגנון** | CPU monitoring | TTL | gRPC Timeout |
| **מי מפעיל** | Cleanup Job | Kubernetes | gRPC Server |
| **תדירות בדיקה** | כל 10 שניות | חד-פעמי | רציף |
| **תנאי** | CPU ≤ 4m × 5 | Job Complete/Failed | No activity 180s |

---

## 📝 הערות חשובות

### 1. Job Cancellation Endpoint
- `DELETE /job/{job_id}` → **כרגע לא מיושם** (מחזיר 404)
- נדון בשיחה עם צוות Backend (לא החלטה רשמית)
- אם ייושם, צריך הגנות אבטחה (מניעת ביטול Jobs של instance אחר)

### 2. GRPC Disconnection
- אם הלקוח מתנתק מה-stream → Job נסגר מיד (לא צריך לחכות ל-timeout)
- זה לא תרחיש נפרד אלא חלק מ-"Stream ללא פעילות"

### 3. Historic Jobs
- Historic jobs נסגרים כשהנתונים נגמרים (לא לפי זמן)
- זה תרחיש נפרד שלא מופיע בטבלה

---

## 🔗 קישורים רלוונטיים

- [gRPC Job Lifecycle](./GRPC_JOB_LIFECYCLE.md)
- [Job Lifecycle Guide](../02_user_guides/JOB_LIFECYCLE_AND_LOAD_TESTING_GUIDE.md)
- [Job Cancellation Discussion](../06_project_management/meetings/JOB_CANCELLATION_ENDPOINT_DISCUSSION_2025-11-19.md)

---

**תאריך עדכון:** 19 בנובמבר 2025  
**מחבר:** Automation Framework (based on team discussion and technical documentation)

