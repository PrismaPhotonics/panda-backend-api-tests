# מקורות: התנהגות Jobs בקוד ובמסמכים של הפיתוח
# Sources: Jobs Behavior in Development Code and Documentation

**תאריך:** 2025-01-27  
**מטרה:** לתעד איפה בקוד ובמסמכים של הפיתוח מופיע מה ההתנהגות של Jobs

---

## 📚 מסמכים עיקריים

### 1. `docs/07_infrastructure/GRPC_JOB_LIFECYCLE.md`

**זה המסמך המרכזי** שמסביר את מחזור החיים המלא של Jobs.

**מקור:** מבוסס על Kubernetes job template שנמצא ב-`debug-codebase/pz/config/panda/templates/job-template.yml`

**מה כתוב שם:**

#### מבנה Job:
- **grpc-job-$JOB_ID** - Job ראשי שרץ gRPC server
- **cleanup-job-$JOB_ID** - Job שמנקה משאבים
- **grpc-service-$JOB_ID** - Kubernetes Service

#### מנגנוני סיום Job:
| תרחיש | זמן עד מחיקה | מנגנון |
|-------|-------------|--------|
| **Job לא פותחים אותו** | **~50 שניות** | Cleanup job מזהה CPU נמוך (5 checks × 10s) |
| **Job מסתיים** | **2 דקות** | TTL (`ttlSecondsAfterFinished: 120`) |
| **Stream ללא פעילות** | **3 דקות** | gRPC Timeout (180s) |

#### Environment Variables של cleanup-job:
```yaml
CPU_USAGE_THRESHOLD: 4        # 4 millicores
ENABLE_CPU_USAGE_CHECK: true
MAX_CPU_USAGE_COUNT: 5        # 5 consecutive checks
```

#### Cleanup Triggers:
1. Job Completion
2. Job Failure
3. Low CPU Usage (5 consecutive checks)

**שורות רלוונטיות:**
- שורות 68-96: מבנה cleanup-job
- שורות 102-130: מנגנוני סיום Job
- שורות 159-170: ניטור cleanup
- שורות 172-192: תהליך cleanup
- שורות 260-291: Cleanup Triggers

---

### 2. `docs/07_infrastructure/JOB_DELETION_TIMELINE.md`

**מסמך מפורט** על מתי Jobs נמחקים.

**מקור:** שיחה עם צוות Backend + תיעוד טכני

**מה כתוב שם:**

#### תרחיש 1: Job לא פותחים אותו (~50 שניות)
- `cleanup-job-$JOB_ID` בודק CPU כל **10 שניות**
- אם CPU ≤ 4m (millicores) במשך **5 בדיקות רצופות** → מתחיל cleanup
- זמן כולל: **5 × 10s = 50 שניות**

**קוד רלוונטי:**
```yaml
Environment Variables:
  CPU_USAGE_THRESHOLD: 4        # 4 millicores
  ENABLE_CPU_USAGE_CHECK: true
  MAX_CPU_USAGE_COUNT: 5        # 5 consecutive checks
```

**שורות רלוונטיות:**
- שורות 21-53: תרחיש 1 (Job לא פותחים)
- שורות 27-38: מנגנון + קוד רלוונטי
- שורות 40-53: תהליך מפורט

#### תרחיש 2: Job מסתיים (2 דקות)
- Kubernetes `ttlSecondsAfterFinished: 120` → Job נמחק אוטומטית אחרי **2 דקות**

**קוד רלוונטי:**
```yaml
apiVersion: batch/v1
kind: Job
spec:
  ttlSecondsAfterFinished: 120  # Auto-delete after 2 minutes
```

**שורות רלוונטיות:**
- שורות 57-83: תרחיש 2 (Job מסתיים)

#### תרחיש 3: Stream ללא פעילות (3 דקות)
- gRPC Timeout של **180 שניות (3 דקות)**

**שורות רלוונטיות:**
- שורות 87-106: תרחיש 3 (Stream ללא פעילות)

---

### 3. `docs/02_user_guides/JOB_LIFECYLE_AND_LOAD_TESTING_GUIDE.md`

**מדריך מלא** על תהליך Job ובדיקות עומס.

**מה כתוב שם:**

#### מחזור חיים מלא של Job:
1. CLIENT REQUEST
2. VALIDATION
3. JOB CREATION
4. BABY ANALYZER INITIALIZATION
5. DATA STREAMING
6. JOB MONITORING
7. JOB TERMINATION
8. CLEANUP

#### מנגנוני סיום Job (שורות 64-81):
| תרחיש | זמן עד מחיקה | מנגנון |
|-------|-------------|--------|
| **Job לא פותחים אותו** | **~50 שניות** | Cleanup job מזהה CPU נמוך |
| **Job מסתיים** | **2 דקות** | TTL (ttlSecondsAfterFinished: 120) |
| **Stream ללא פעילות** | **3 דקות** | gRPC Timeout (180s) |

**שורות רלוונטיות:**
- שורות 20-89: מחזור חיים מלא
- שורות 64-81: מנגנוני סיום Job

---

### 4. `docs/06_project_management/jira/HOW_JOBS_ARE_CREATED.md`

**מסמך** שמסביר איך Jobs נוצרים.

**מה כתוב שם:**

#### תהליך יצירת Job:
1. ולידציה
2. בדיקת משאבים
3. יצירת job_id
4. יצירת Kubernetes Jobs:
   - `grpc-job-$JOB_ID`
   - `cleanup-job-$JOB_ID`
5. יצירת Kubernetes Service:
   - `grpc-service-$JOB_ID`
6. יצירת Task ב-MongoDB
7. הגדרת RabbitMQ Queues
8. החזרת Response

**שורות רלוונטיות:**
- שורות 91-105: תהליך יצירת Job בצד השרת

---

## 🔍 מה לא נמצא בפרויקט הזה

### 1. קוד של Focus Server

**למה:** Focus Server הוא חלק מה-Backend, לא מהפרויקט הזה.

**איפה זה אמור להיות:** ב-repository של Backend (לא בפרויקט הזה).

**מה יש לנו:** רק API client (`src/apis/focus_server_api.py`) שמתקשר עם Focus Server.

---

### 2. קוד של cleanup-job

**למה:** cleanup-job הוא Docker image (`cleanup-grpc:1.1`) שרץ ב-Kubernetes, לא קוד Python בפרויקט הזה.

**איפה זה אמור להיות:** ב-repository של Backend או ב-repository נפרד של cleanup service.

**מה יש לנו:** רק תיעוד של ההתנהגות (Environment Variables, מנגנון).

---

### 3. Kubernetes Job Template

**למה:** ה-template נמצא ב-`debug-codebase/pz/config/panda/templates/job-template.yml`, לא בפרויקט הזה.

**מה יש לנו:** התיעוד מתייחס ל-template הזה, אבל לא יש לנו את הקובץ עצמו.

**התיעוד מתייחס ל:**
- שורה 5 ב-`GRPC_JOB_LIFECYCLE.md`: "Based on the Kubernetes job template found in `debug-codebase/pz/config/panda/templates/job-template.yml`"
- שורה 506 ב-`GRPC_JOB_LIFECYCLE.md`: "Job Template: `debug-codebase/pz/config/panda/templates/job-template.yml`"

---

## ✅ מה כן יש לנו

### 1. תיעוד מפורט של התנהגות Jobs

✅ **יש לנו:**
- `docs/07_infrastructure/GRPC_JOB_LIFECYCLE.md` - מחזור חיים מלא
- `docs/07_infrastructure/JOB_DELETION_TIMELINE.md` - מתי Jobs נמחקים
- `docs/02_user_guides/JOB_LIFECYCLE_AND_LOAD_TESTING_GUIDE.md` - מדריך מלא

---

### 2. API Client

✅ **יש לנו:**
- `src/apis/focus_server_api.py` - API client שמתקשר עם Focus Server
- `src/models/focus_server_models.py` - Models של Requests/Responses

**מה זה עושה:**
- שולח `POST /configure` ל-Focus Server
- מקבל `job_id` בתשובה
- לא יוצר Jobs ישירות, רק מתקשר עם API

---

### 3. תיעוד מבוסס על שיחות עם צוות Backend

✅ **יש לנו:**
- תיעוד שמבוסס על שיחות עם צוות Backend
- תיעוד שמבוסס על Kubernetes Job Template
- תיעוד שמבוסס על ניסיון בפועל

---

## 📋 סיכום - איפה מופיע מה

| נושא | איפה מופיע | מקור |
|------|-----------|------|
| **מבנה Job** | `docs/07_infrastructure/GRPC_JOB_LIFECYCLE.md` (שורות 9-96) | Kubernetes Job Template |
| **מנגנון ניקוי (50 שניות)** | `docs/07_infrastructure/JOB_DELETION_TIMELINE.md` (שורות 21-53) | שיחה עם צוות Backend |
| **מנגנון ניקוי (50 שניות)** | `docs/07_infrastructure/GRPC_JOB_LIFECYCLE.md` (שורות 114-117) | Kubernetes Job Template |
| **TTL (2 דקות)** | `docs/07_infrastructure/JOB_DELETION_TIMELINE.md` (שורות 57-83) | Kubernetes Config |
| **gRPC Timeout (3 דקות)** | `docs/07_infrastructure/JOB_DELETION_TIMELINE.md` (שורות 87-106) | gRPC Server Config |
| **מחזור חיים מלא** | `docs/02_user_guides/JOB_LIFECYCLE_AND_LOAD_TESTING_GUIDE.md` (שורות 20-89) | תיעוד טכני |
| **יצירת Jobs** | `docs/06_project_management/jira/HOW_JOBS_ARE_CREATED.md` (שורות 91-105) | תיעוד טכני |
| **קוד של Focus Server** | ❌ לא בפרויקט הזה | ב-repository של Backend |
| **קוד של cleanup-job** | ❌ לא בפרויקט הזה | ב-repository של Backend |
| **Kubernetes Job Template** | ❌ לא בפרויקט הזה | ב-`debug-codebase/pz/config/panda/templates/job-template.yml` |

---

## 🎯 מסקנות

1. **התיעוד מבוסס על:**
   - Kubernetes Job Template (לא בפרויקט הזה)
   - שיחות עם צוות Backend
   - ניסיון בפועל

2. **הקוד של הפיתוח לא נמצא בפרויקט הזה:**
   - Focus Server code → ב-repository של Backend
   - cleanup-job code → ב-repository של Backend
   - Kubernetes Job Template → ב-`debug-codebase/pz/config/panda/templates/job-template.yml`

3. **מה כן יש לנו:**
   - תיעוד מפורט של התנהגות Jobs
   - API client שמתקשר עם Focus Server
   - תיעוד מבוסס על שיחות עם צוות Backend

---

## 💡 המלצות

1. **לבדוק את הקוד של Backend** - אם יש גישה ל-repository של Backend, לבדוק שם את הקוד של:
   - Focus Server (יצירת Jobs)
   - cleanup-job (מנגנון הניקוי)

2. **לבדוק את Kubernetes Job Template** - אם יש גישה ל-`debug-codebase/pz/config/panda/templates/job-template.yml`, לבדוק שם את הקונפיגורציה

3. **לעדכן את התיעוד** - אם מוצאים משהו שונה בקוד, לעדכן את המסמכים

---

**תאריך:** 2025-01-27  
**מחבר:** Automation Framework Analysis

