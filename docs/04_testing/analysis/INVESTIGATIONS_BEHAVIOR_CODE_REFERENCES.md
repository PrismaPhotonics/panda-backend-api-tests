# הפניות לקוד: התנהגות חקירות באוטומציה
# Code References: Investigations Automation Behavior

**תאריך:** 2025-01-27  
**מטרה:** להסביר מאיפה הגעתי לכל מסקנה, עם הפניות לקוד הספציפי

---

## 📋 סיכום המסקנות והמקורות

### 1. Jobs נשארים פתוחים ~50 שניות אחרי ניתוק

**מקור:** תיעוד טכני + שיחה עם צוות Backend

**קבצים:**
- `docs/07_infrastructure/JOB_DELETION_TIMELINE.md` (שורות 21-53)
- `docs/07_infrastructure/GRPC_JOB_LIFECYCLE.md` (שורות 114-117)

**קוד רלוונטי:**
```yaml
# מתוך GRPC_JOB_LIFECYCLE.md
Environment Variables:
  CPU_USAGE_THRESHOLD: 4        # 4 millicores
  ENABLE_CPU_USAGE_CHECK: true
  MAX_CPU_USAGE_COUNT: 5        # 5 consecutive checks
```

**הסבר:**
- `cleanup-job-$JOB_ID` בודק את ה-CPU כל **10 שניות**
- אם CPU ≤ 4m (millicores) במשך **5 בדיקות רצופות** → מתחיל cleanup
- זמן כולל: **5 × 10s = 50 שניות**

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

**הערה:** זה לא קוד Python שלנו, אלא מנגנון Kubernetes/Backend. התיעוד מבוסס על שיחה עם צוות Backend.

---

### 2. Delay בין חקירות בטסטים

#### 2.1. 277 Investigations Test - Delay של 5 שניות

**מקור:** קוד Python בפרויקט

**קובץ:** `scripts/run_277_investigations_test.py`

**שורה 66:** הגדרת הפרמטר
```python
def __init__(self, environment: str = "staging", max_frames: int = 500, delay_between_investigations: int = 5):
    self.delay_between_investigations = delay_between_investigations
```

**שורה 610:** הודעת Log שמסבירה את ה-delay
```python
logger.info(f"Delay between investigations: {self.delay_between_investigations} seconds")
logger.info("⚠️  NOTE: Each investigation creates a Kubernetes job that stays open for ~50 seconds")
logger.info("   after disconnection. With 277 investigations, this can create significant load.")
logger.info("   Consider increasing --delay-between-investigations if you see performance issues.")
```

**שורה 657-665:** הקוד שמבצע את ה-delay
```python
# Jobs are automatically deleted after ~50 seconds of inactivity
# Using configurable delay to reduce concurrent job load
logger.debug(f"Waiting {self.delay_between_investigations} seconds before next investigation...")

# Sleep in small increments to allow interruption
for _ in range(self.delay_between_investigations):
    if self.interrupted:
        break
    time.sleep(1)
```

**שורה 912-917:** הגדרת הפרמטר ב-argparse
```python
parser.add_argument(
    "--delay-between-investigations",
    type=int,
    default=5,
    help="Delay in seconds between investigations (default: 5). "
         "Jobs are automatically deleted after ~50 seconds of inactivity. "
         "Increase this value if you see too many concurrent jobs."
)
```

**ברירת מחדל:** 5 שניות

---

#### 2.2. 30 Investigations Test - Delay של 2 שניות

**מקור:** קוד Python בפרויקט

**קובץ:** `scripts/run_30_investigations_test.py`

**שורה 247-249:** הקוד שמבצע את ה-delay
```python
# Small delay between investigations
if investigation_num < 30:
    time.sleep(2)
```

**ברירת מחדל:** 2 שניות

---

#### 2.3. Stress Test Loop - Delay של 1 שנייה

**מקור:** קוד Python בפרויקט

**קובץ:** `be_focus_server_tests/stress/test_investigation_stress_loop.py`

**שורה 352-353:** הקוד שמבצע את ה-delay
```python
# Small delay between iterations
time.sleep(1)
```

**ברירת מחדל:** 1 שנייה

---

### 3. חישוב מספר Jobs במקביל

**מקור:** חישוב מתמטי מבוסס על:
- זמן לכל חקירה: ~20 שניות (מתוך `docs/04_testing/analysis/277_INVESTIGATIONS_LOAD_ANALYSIS.md`)
- זמן ניקוי: ~50 שניות (מתוך `docs/07_infrastructure/JOB_DELETION_TIMELINE.md`)
- Delay בין חקירות: תלוי בטסט

**קובץ:** `docs/04_testing/analysis/277_INVESTIGATIONS_LOAD_ANALYSIS.md` (שורות 71-105)

**חישוב:**
```
אם כל חקירה לוקחת 20 שניות, ו-Job נשאר פתוח 50 שניות:
מספר Jobs במקביל = 50 / 20 = ~2.5 Jobs בממוצע

אבל בפועל:
- חקירה 1: Job נשאר פתוח 50 שניות (מ-0 עד 50)
- חקירה 2: Job נשאר פתוח 50 שניות (מ-20 עד 70)
- חקירה 3: Job נשאר פתוח 50 שניות (מ-40 עד 90)
- ...

בזמן t=50:
- Job 1: עדיין פתוח (עד פתוח (עד 50)
- Job 2: עדיין פתוח (עד 70)
- Job 3: עדיין פתוח (עד 90)
- Job 4: עדיין פתוח (עד 110)
- Job 5: עדיין פתוח (עד 130)

מספר Jobs במקביל = 50 / 20 = 2.5 בממוצע
```

**עם delay של 5 שניות:**
- זמן בין חקירות: 20 + 5 = 25 שניות
- מספר Jobs במקביל: 50 / 25 = **~2 Jobs**

**עם delay של 1 שנייה:**
- זמן בין חקירות: 20 + 1 = 21 שניות
- מספר Jobs במקביל: 50 / 21 = **~2.4 Jobs**

**אבל בפועל עם 277 חקירות:**
- יכול להיות עד **~13 Jobs במקביל** בזמן שיא (אם delay קצר מאוד)

---

### 4. זמן לכל חקירה

**מקור:** ניתוח מבוסס על:
- תיעוד טכני
- מדידות בפועל (אם קיימות)
- הערכות מבוססות על התנהגות המערכת

**קובץ:** `docs/04_testing/analysis/277_INVESTIGATIONS_LOAD_ANALYSIS.md` (שורות 11-33)

**פירוט:**
```
1. יצירת Job:        ~0.3 שניות
   - POST /configure → יוצר Kubernetes Job
   
2. חיבור ל-gRPC:     ~12 שניות
   - המתנה ל-job להיות ready
   - חיבור ל-gRPC server
   - בעיית ביצועים שזוהתה
   
3. בדיקת 500 Frames: ~6-7 שניות
   - קבלת נתונים מ-gRPC stream
   - בדיקת ערכי amplitude שליליים
   
4. ניתוק:            ~0.1 שניות
   - client.disconnect() → סוגר את ה-gRPC connection
   
5. Delay:            תלוי בטסט (1-5 שניות)
   - time.sleep() → ממתין לפני החקירה הבאה
   
─────────────────────────────
סה"כ:             ~20 שניות לחקירה
```

**הערה:** הזמנים האלה מבוססים על הערכות ותיעוד. לא מצאתי קוד שמדוד את זה בפועל.

---

### 5. מנגנון ניקוי אוטומטי

**מקור:** תיעוד טכני של Kubernetes Job Template

**קבצים:**
- `docs/07_infrastructure/GRPC_JOB_LIFECYCLE.md` (שורות 68-96)
- `docs/07_infrastructure/JOB_DELETION_TIMELINE.md` (שורות 27-38)

**קוד רלוונטי (מתוך התיעוד):**
```yaml
# Cleanup Job Configuration
apiVersion: batch/v1
kind: Job
metadata:
  name: cleanup-job-$JOB_ID
spec:
  backoffLimit: 0
  ttlSecondsAfterFinished: 10        # Auto-delete 10 seconds after completion

Environment Variables:
  CPU_USAGE_THRESHOLD: 4        # 4 millicores
  ENABLE_CPU_USAGE_CHECK: true
  MAX_CPU_USAGE_COUNT: 5        # 5 consecutive checks
```

**הערה:** זה לא קוד Python שלנו, אלא קונפיגורציה של Kubernetes Job. הקוד של ה-cleanup job נמצא ב-Backend (לא בפרויקט הזה).

---

## 🔍 מה לא מצאתי בקוד

### 1. קוד של cleanup-job

**למה:** ה-cleanup job הוא חלק מה-Backend, לא מהפרויקט הזה. הפרויקט שלנו רק משתמש ב-API של Focus Server.

**איפה זה אמור להיות:** ב-repository של Backend (לא בפרויקט הזה).

---

### 2. מדידות זמן בפועל

**למה:** לא מצאתי קוד שמדוד את הזמנים בפועל. הזמנים מבוססים על:
- הערכות מהתיעוד
- שיחה עם צוות Backend
- ניתוח התנהגות המערכת

**איפה זה יכול להיות:** יכול להיות ב-logs או ב-metrics של Kubernetes, אבל לא בקוד Python שלנו.

---

### 3. קוד שמחשב מספר Jobs במקביל

**למה:** זה חישוב מתמטי פשוט, לא צריך קוד מיוחד.

**איפה זה מופיע:** רק בתיעוד (`docs/04_testing/analysis/277_INVESTIGATIONS_LOAD_ANALYSIS.md`).

---

## ✅ מה כן מצאתי בקוד

### 1. Delay בין חקירות

✅ **מצאתי בקוד:**
- `scripts/run_277_investigations_test.py` - שורה 66, 610, 657-665, 912-917
- `scripts/run_30_investigations_test.py` - שורה 247-249
- `be_focus_server_tests/stress/test_investigation_stress_loop.py` - שורה 352-353

---

### 2. הערות על Jobs שנשארים פתוחים

✅ **מצאתי בקוד:**
- `scripts/run_277_investigations_test.py` - שורה 613-615:
```python
logger.info("⚠️  NOTE: Each investigation creates a Kubernetes job that stays open for ~50 seconds")
logger.info("   after disconnection. With 277 investigations, this can create significant load.")
logger.info("   Consider increasing --delay-between-investigations if you see performance issues.")
```

---

### 3. תיעוד של מנגנון הניקוי

✅ **מצאתי בתיעוד:**
- `docs/07_infrastructure/JOB_DELETION_TIMELINE.md` - תיעוד מפורט של מנגנון הניקוי
- `docs/07_infrastructure/GRPC_JOB_LIFECYCLE.md` - תיעוד של מחזור החיים של Jobs

---

## 📚 קבצים רלוונטיים

### קבצי קוד Python:
1. `scripts/run_277_investigations_test.py` - טסט של 277 חקירות
2. `scripts/run_30_investigations_test.py` - טסט של 30 חקירות
3. `be_focus_server_tests/stress/test_investigation_stress_loop.py` - Stress test loop

### קבצי תיעוד:
1. `docs/07_infrastructure/JOB_DELETION_TIMELINE.md` - תיעוד של מנגנון מחיקת Jobs
2. `docs/07_infrastructure/GRPC_JOB_LIFECYCLE.md` - תיעוד של מחזור החיים של gRPC Jobs
3. `docs/04_testing/analysis/277_INVESTIGATIONS_LOAD_ANALYSIS.md` - ניתוח עומס של 277 חקירות
4. `docs/02_user_guides/WHY_INVALID_JOB_ID.md` - הסבר על למה Jobs נמחקים

---

## 🎯 מסקנות

1. **Delay בין חקירות:** ✅ מצאתי בקוד Python - ברור ומוגדר היטב
2. **Jobs נשארים פתוחים 50 שניות:** ✅ מצאתי בתיעוד - מבוסס על שיחה עם צוות Backend
3. **מנגנון ניקוי אוטומטי:** ✅ מצאתי בתיעוד - מבוסס על Kubernetes Job Template
4. **זמן לכל חקירה:** ⚠️ מבוסס על הערכות ותיעוד, לא על מדידות בפועל
5. **מספר Jobs במקביל:** ⚠️ חישוב מתמטי מבוסס על הזמנים המתועדים

---

## 💡 המלצות

1. **להוסיף מדידות זמן בפועל** - לבדוק כמה זמן באמת לוקח כל שלב
2. **להוסיף ניטור של מספר Jobs פתוחים** - לבדוק כמה Jobs באמת פתוחים במקביל
3. **להוסיף logging מפורט** - לראות בדיוק מה קורה בכל שלב

---

**תאריך:** 2025-01-27  
**מחבר:** Automation Framework Analysis

