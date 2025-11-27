# Job Cancellation Endpoint - Discussion Summary
# דיון על Job Cancellation Endpoint - סיכום

**תאריך:** 19 בנובמבר 2025  
**משתתפים:** Roy Avrahami, Guy Zaichik  
**נושא:** Job Cancellation Endpoint - האם צריך להיות קיים?

**⚠️ חשוב:** זהו סיכום שיחה/דיון, לא החלטה רשמית או תוכנית מחייבת.

---

## 📋 סיכום השיחה

### שאלה ראשונית
**Roy:** "Job Cancellation Endpoint זה משהו שאנחנו צריכים להיות?"

### תשובת Guy
**Guy:** 
- 💬 **כן, עדיף שיהיה** - כדי לשלוט טוב יותר על ה-state (דעה/המלצה)
- 🔒 **אבל צריך הגנה** - מפני מצב שבו instance אחד של APP מבטל Jobs של instance אחר
- ⏰ **כרגע מסתמכים על:**
  - Timeout או ניתוק GRPC כדי לדחוף את ה-Job למצב "off"

### מצב נוכחי
**Roy:** "זה המצב עכשיו, 3 דקות ל-full timeout"

---

## 💬 נקודות שהועלו בשיחה (לא החלטה)

### 1. Job Cancellation Endpoint - נדון
- **סטטוס:** נדון בשיחה - הועלה הרעיון שכדאי שיהיה קיים
- **כרגע:** לא מיושם (מחזיר 404)
- **לא:** אין החלטה רשמית או תוכנית מחייבת לייצור

### 2. מנגנון נוכחי - מתי Job נמחק

| תרחיש | זמן עד מחיקה | מנגנון |
|-------|-------------|--------|
| **Job לא פותחים אותו** (לא מתחברים) | **~50 שניות** | Cleanup job מזהה CPU נמוך (5 checks × 10s) |
| **Job מסתיים** (Complete/Failed) | **2 דקות** | TTL (`ttlSecondsAfterFinished: 120`) |
| **Stream ללא פעילות** | **3 דקות** | gRPC Timeout (180s) |

**פירוט:**
- **Job לא פותחים:** Cleanup job בודק CPU כל 10 שניות, אם CPU ≤ 4m (millicores) במשך 5 בדיקות → cleanup (~50 שניות)
- **Job מסתיים:** Kubernetes Job נמחק אוטומטית אחרי 2 דקות (TTL)
- **Stream ללא פעילות:** gRPC timeout של 3 דקות → Job נסגר
- **GRPC Disconnection:** ניתוק הלקוח → Job עובר למצב "off"

### 3. דרישות אבטחה (כשייושם)
- 🔒 **הגנה מפני cross-instance cancellation:**
  - וידוא שה-APP instance שמבטל את ה-Job הוא זה שיצר אותו
  - או: מנגנון הרשאות/authentication לזיהוי instance
  - מניעת מצב שבו instance אחד מבטל Jobs של instance אחר

---

## 📝 פעולות נדרשות

### לצוות Backend
1. ☐ להחליט אם יש צורך ב-endpoint `DELETE /job/{job_id}` (נדון בשיחה)
2. ☐ אם יחליטו ליישם - להוסיף הגנות אבטחה (cross-instance protection)
3. ☐ לעדכן את ה-API documentation אם יחליטו ליישם

### לצוות אוטומציה
1. ✅ עדכון קוד `cancel_job()` - מטפל ב-404 כ-DEBUG/WARNING
2. ✅ עדכון תיעוד - מציין שמדובר בנושא שנדון בשיחה (לא החלטה)
3. ☐ לבדוק מחדש אם הצוות Backend יחליט ליישם את ה-endpoint

---

## 🔗 קישורים רלוונטיים

- [Automation Issues Summary](../test_execution/AUTOMATION_ISSUES_AND_FIXES_SUMMARY_2025-11-19.md#בעיה-3-job-cancellation-endpoint-לא-קיים-404)
- [gRPC Job Lifecycle](../../07_infrastructure/GRPC_JOB_LIFECYCLE.md)
- [Job Lifecycle Guide](../../02_user_guides/JOB_LIFECYCLE_AND_LOAD_TESTING_GUIDE.md)

---

**תאריך עדכון:** 19 בנובמבר 2025  
**מחבר:** Automation Framework (based on team conversation)  
**⚠️ הערה:** זהו סיכום שיחה, לא החלטה רשמית או תוכנית מחייבת

