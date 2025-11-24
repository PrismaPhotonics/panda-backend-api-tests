# 🔥 Load & Capacity Tests - בדיקות עומס וקיבולת

**תאריך:** 27 אוקטובר 2025 (Updated - PZ-13756)  
**מטרה:** בדיקת מגבלות המערכת מבחינת מספר jobs concurrent

---

## ⚠️ CRITICAL UPDATE (November 2025)

**דרישה מעודכנת (Graduated Load Testing):**
- ✅ המערכת חייבת לתמוך ב-**40 concurrent jobs** (מינימום חובה)
- 🎯 יעד אופטימלי: **50 concurrent jobs**
- ✅ טסט מדורג חכם: `test_graduated_load_capacity()`
- ✅ פרוגרסיה: **5→10→20→25→30→31-40→41-49→50**
- ✅ אם סביבה לא עומדת ביעד → **Infrastructure Gap Report** אוטומטי

**Target Environments (חובה לעמוד במינימום 40 jobs):**
- DEV (minimum: 40 jobs, target: 50 jobs at 95%+ success rate)
- Staging (minimum: 40 jobs, target: 50 jobs at 95%+ success rate)

**Non-Target Environments (דיווח בלבד):**
- Production (informational only)
- Local (informational only)

---

---

## 📚 **מה נמצא כאן?**

1. **מסמך הסבר מלא** - `documentation/testing/JOB_LIFECYCLE_AND_LOAD_TESTING_GUIDE.md`
   - הסבר מפורט על תהליך ה-Job
   - רכיבי המערכת
   - מגבלות ידועות
   - תרחישי כשל אפשריים
   - אסטרטגיית בדיקה

2. **סקריפט בדיקות pytest** - `tests/load/test_job_capacity_limits.py`
   - בדיקות מקיפות עם pytest
   - 6 סוגי בדיקות שונים
   - דוחות מפורטים

3. **סקריפט מהיר** - `scripts/quick_job_capacity_check.py`
   - בדיקה מהירה ללא pytest
   - ריצה ישירה מהטרמינל
   - פלט ויזואלי

---

## 🚀 **התחלה מהירה**

### **אופציה 1: בדיקה מהירה (מומלץ למתחילים)**

```bash
# בדיקה מהירה - 5, 10, 20 jobs (~1 דקה)
python scripts/quick_job_capacity_check.py --environment staging --quick

# בדיקה סטנדרטית - עד 30 jobs (~2-3 דקות)
python scripts/quick_job_capacity_check.py --environment production

# בדיקה מקיפה - עד 50 jobs מדורג (~5-10 דקות)
python scripts/quick_job_capacity_check.py --environment staging --comprehensive
```

### **אופציה 2: בדיקות pytest מלאות**

```bash
# הרץ את כל בדיקות העומס
pytest tests/load/test_job_capacity_limits.py -v -m load

# הרץ רק baseline test
pytest tests/load/test_job_capacity_limits.py -v -m baseline

# הרץ רק linear load test
pytest tests/load/test_job_capacity_limits.py -v -m linear

# הרץ stress tests
pytest tests/load/test_job_capacity_limits.py -v -m stress
```

---

## 📊 **סוגי הבדיקות**

### **1. Baseline Performance (ביצועי בסיס)**
מטרה: למדוד ביצועים של job בודד - קו הבסיס

```bash
pytest tests/load/test_job_capacity_limits.py::TestBaselinePerformance -v
```

**מה זה בודק:**
- ✓ Latency ליצירת job בודד
- ✓ צריכת משאבים (CPU, RAM)
- ✓ תקינות ה-job

**משך זמן משוער:** ~10 שניות

---

### **2. Linear Load Test (עומס הדרגתי)**
מטרה: למצוא את נקודת השבירה

```bash
pytest tests/load/test_job_capacity_limits.py::TestLinearLoad::test_linear_load_progression -v
```

**מה זה בודק:**
- ✓ 5 jobs concurrent
- ✓ 10 jobs concurrent
- ✓ 20 jobs concurrent
- ✓ 50 jobs concurrent (אם הקודמים הצליחו)

**קריטריון עצירה:** כש-success rate יורד מתחת ל-90%

**משך זמן משוער:** ~3-5 דקות

**תוצאה צפויה:**
```
Jobs     Success Rate    Latency (ms)    CPU %    Memory %
--------------------------------------------------------------
5        100.0%          250             45.2     62.1
10       100.0%          320             68.5     71.3
20       95.0%           580             82.1     79.8
50       75.0%           1250            95.3     88.2  ← נקודת שבירה
```

---

### **3. Stress Test (בדיקת לחץ)**
מטרה: לדחוף את המערכת לגבול

```bash
pytest tests/load/test_job_capacity_limits.py::TestStressLoad -v
```

**מה זה בודק:**
- ⚠️ 40 jobs concurrent בבת אחת
- ⚠️ איך המערכת מגיבה לעומס יתר
- ⚠️ האם המערכת קורסת או שורדת

**משך זמן משוער:** ~5-10 דקות

**אזהרה:** ⚠️ הבדיקה הזו עלולה להעמיס על המערכת!

---

### **4. Graduated Load Test (בדיקה מדורגת חכמה)** 🆕
מטרה: למצוא את הקיבולת המקסימלית בצורה אופטימלית

```bash
pytest tests/load/test_job_capacity_limits.py::TestGraduatedLoadCapacity -v
```

**מה זה בודק:**
- 🚀 **Phase 1 (Quick Ramp):** 5 → 10 → 20 → 25 → 30 (קפיצות גדולות)
- 🎯 **Phase 2 (Fine-Tuning):** 31 → 32 → ... → 40 (job אחד אחד)
- 📈 **Phase 3 (Extended):** 41 → 42 → ... → 50 (job אחד אחד)

**התנהגות חכמה:**
- 🛑 **עצירה מיידית** ברגע שמזהה כשל או degradation
- 📊 **תיעוד מדויק** של נקודת השבירה (breaking point)
- ✅ לא ממשיך לנסות אחרי כשל - חוסך זמן
- 🔍 מזהה 3 סוגי בעיות:
  - כשל מלא (0% success)
  - הידרדרות (partial success)
  - Exception של המערכת

**יתרונות:**
- ✅ חוסך זמן באזור העומס הנמוך (קפיצות גדולות)
- ✅ מדייק בזיהוי נקודת השבירה (צעדים קטנים ליד הגבול)
- ✅ עוצר מיד כשמוצא בעיה - לא מעמיס על המערכת
- ✅ בודק עד 50 jobs למציאת מקסימום ריאליסטי
- ✅ מתעד בדיוק איפה המערכת נכשלת ולמה

**משך זמן משוער:** 
- אם מגיע ל-50 ללא בעיות: ~8-12 דקות
- אם מוצא נקודת שבירה מוקדם: ~2-5 דקות

**Target:**
- מינימום: 40 jobs (חובה)
- אופטימלי: 50 jobs (יעד)

**דוגמת פלט:**
```
✅ All 30 job(s) succeeded - moving to next step
✅ All 31 job(s) succeeded - moving to next step
⚠️ PARTIAL SUCCESS (85.0%) - DEGRADATION DETECTED!
   Last full capacity: 31 jobs (100% success)
   Degradation at: 32 jobs (85.0% success)

🔴 CAPACITY LIMIT IDENTIFIED
Maximum Stable Capacity: 31 jobs (100% success)
Degradation Point:      32 jobs (85.0% success)
```

**משך זמן משוער:** ~5-10 דקות

**אזהרה:** ⚠️ הבדיקה הזו עלולה להעמיס על המערכת!

---

### **4. Heavy Configuration Stress**
מטרה: לבדוק עומס עם קונפיגורציה כבדה

```bash
pytest tests/load/test_job_capacity_limits.py::TestHeavyConfigurationStress -v
```

**מה זה בודק:**
- ⚠️ 200 ערוצים (במקום 50)
- ⚠️ NFFT 2048 (במקום 1024)
- ⚠️ טווח תדירות מלא (0-1000 Hz)

**משך זמן משוער:** ~3-5 דקות

**זהו הבדיקה הכבדה ביותר!**

---

### **5. Recovery Test (התאוששות)**
מטרה: לבדוק שהמערכת מתאוששת אחרי עומס

```bash
pytest tests/load/test_job_capacity_limits.py::TestSystemRecovery -v
```

**תהליך:**
1. יצירת עומס כבד (20 jobs)
2. המתנה 30 שניות
3. בדיקת job בודד
4. אימות שהמערכת חזרה לתקינות

**משך זמן משוער:** ~2 דקות

---

### **6. Soak Test (עומס ממושך)**
מטרה: לזהות memory leaks

```bash
pytest tests/load/test_job_capacity_limits.py::TestSustainedLoad -v
```

**מה זה בודק:**
- 🕐 10 jobs כל דקה במשך שעה
- 🔍 מעקב אחר זליגת זיכרון
- 🔍 מעקב אחר ביצועים לאורך זמן

**משך זמן:** ⏰ **שעה שלמה!**

**הערה:** מסומן כ-`skip` כברירת מחדל. להריץ ידנית.

---

## 🎯 **דוגמאות שימוש**

### **דוגמה 1: בדיקה מהירה לפני דפלוי**

```bash
# בדיקה מהירה של staging לפני production deployment
python scripts/quick_job_capacity_check.py \
    --environment staging \
    --quick \
    --output staging_capacity_check.json

# אם הכל עבר בהצלחה:
python scripts/quick_job_capacity_check.py \
    --environment production \
    --quick
```

### **דוגמה 2: חקירת בעיית ביצועים**

```bash
# הרץ baseline לראות מה המצב הנוכחי
pytest tests/load/test_job_capacity_limits.py::TestBaselinePerformance -v -s

# הרץ linear load למצוא איפה הבעיה מתחילה
pytest tests/load/test_job_capacity_limits.py::TestLinearLoad -v -s

# אם נראה memory leak - הרץ recovery test
pytest tests/load/test_job_capacity_limits.py::TestSystemRecovery -v -s
```

### **דוגמה 3: תיעוד קיבולת המערכת**

```bash
# הרץ בדיקה מקיפה ושמור תוצאות
python scripts/quick_job_capacity_check.py \
    --environment production \
    --comprehensive \
    --output production_capacity_$(date +%Y%m%d).json

# הרץ גם pytest לתיעוד מלא
pytest tests/load/test_job_capacity_limits.py \
    -v \
    -m "load and not soak" \
    --html=reports/capacity_test_$(date +%Y%m%d).html
```

### **דוגמה 4: בדיקה מותאמת אישית**

```bash
# בדוק עד 25 jobs (אם אתה יודע שזה הגבול שלך)
python scripts/quick_job_capacity_check.py \
    --environment production \
    --max-jobs 25 \
    --output custom_check.json
```

---

## 🔴 **הבנת נקודות שבירה (Breaking Points)**

הטסט המדורג זוהה **שלושה סוגים** של נקודות שבירה:

### **1. כשל מלא (Complete Failure)**
```
❌ ALL 35 job(s) FAILED - BREAKING POINT DETECTED!
   Last successful capacity: 34 jobs
   Breaking point: 35 jobs (0% success)
```

**משמעות:** המערכת קרסה לחלוטין ב-35 jobs. אף job לא הצליח.

**פעולה:** 
- הגבל מיידית ל-34 jobs מקסימום
- חקור logs לזהות את הגורם לקריסה
- בדוק resource exhaustion (CPU, Memory, Network)

---

### **2. הידרדרות (Degradation)**
```
⚠️ PARTIAL SUCCESS (75.0%) - DEGRADATION DETECTED!
   Last full capacity: 32 jobs (100% success)
   Degradation at: 33 jobs (75.0% success)
```

**משמעות:** המערכת עדיין עובדת אבל מתחילה להיכשל חלקית. 25% מה-jobs נכשלו.

**פעולה:**
- הגבל ל-32 jobs לשימוש production
- ניתן לשקול 33 jobs בשעות low-traffic (עם ניטור)
- חקור למה יש degradation: timeout? resource contention?

---

### **3. Exception**
```
💥 SYSTEM EXCEPTION DETECTED
   Maximum Working Capacity: 28 jobs (100% success)
   Exception at:            29 jobs
   Error:                   ConnectionTimeout: Unable to reach backend service
```

**משמעות:** המערכת זרקה exception במקום להחזיר תגובה תקינה.

**פעולה:**
- הגבל ל-28 jobs מקסימום
- **קריטי:** תקן את ה-bug שגורם ל-exception
- בדוק: connection pools, timeouts, network issues
- זו בעיה קוד שצריכה תיקון

---

## 📊 **פירוש תוצאות**

### **Success Rate (אחוז הצלחה)**

| Success Rate | משמעות | פעולה נדרשת |
|-------------|--------|-------------|
| **95-100%** | ✅ מצוין | המערכת מטפלת בקלות |
| **90-95%** | ✅ טוב | בגבול הבטוח |
| **80-90%** | ⚠️ מקובל | להיזהר, קרוב לגבול |
| **50-80%** | ❌ גרוע | חריגת קיבולת |
| **< 50%** | ❌ כשל | המערכת תקועה |

### **Latency (זמן תגובה)**

| Latency | משמעות | פעולה נדרשת |
|---------|--------|-------------|
| **< 200ms** | ✅ מצוין | ביצועים מעולים |
| **200-500ms** | ✅ טוב | תקין |
| **500ms-1s** | ⚠️ מקובל | להתחיל לחקור |
| **1s-5s** | ❌ איטי | בעיית ביצועים |
| **> 5s** | ❌ קריטי | המערכת תקועה |

### **CPU Usage (צריכת CPU)**

| CPU | משמעות | פעולה נדרשת |
|-----|--------|-------------|
| **< 70%** | ✅ תקין | המערכת בריאה |
| **70-85%** | ⚠️ אזהרה | להתחיל לנטר |
| **85-95%** | ❌ קריטי | להפסיק לקבל jobs חדשים |
| **> 95%** | ❌ תקוע | המערכת על סף קריסה |

### **Memory Usage (צריכת זיכרון)**

| Memory | משמעות | פעולה נדרשת |
|--------|--------|-------------|
| **< 75%** | ✅ תקין | המערכת בריאה |
| **75-90%** | ⚠️ אזהרה | לנטר memory leaks |
| **> 90%** | ❌ קריטי | סכנה ל-OOM kill |

---

## 🔍 **ניתוח תוצאות**

### **מצב תקין (Good Capacity)**

```
📊 Maximum Capacity (90%+ success): 30 concurrent jobs
✅ No breaking point found in tested range
```

**משמעות:** המערכת יכולה לטפל ב-30 jobs בו-זמנית בבטחה.

**המלצה:**
- להגדיר `MAX_CONCURRENT_JOBS = 25` (עם מרווח ביטחון)
- לנטר משאבים
- להוסיף queue system

---

### **מצב בעייתי (Capacity Issues)**

```
📊 Maximum Capacity (90%+ success): 10 concurrent jobs
⚠️ Breaking Point (< 80% success): 20 concurrent jobs
```

**משמעות:** המערכת מתקשה מעל 10 jobs ונשברת ב-20.

**פעולות נדרשות:**
1. **טווח קצר:**
   - הגבל ל-10 jobs concurrent
   - הוסף queue למנוע עומס יתר
   
2. **טווח בינוני:**
   - חקור bottleneck (CPU/RAM/Network)
   - אופטימיזציה של Baby Analyzer
   
3. **טווח ארוך:**
   - שדרוג חומרה
   - Horizontal scaling

---

### **מצב קריטי (System Overload)**

```
📊 Maximum Capacity (90%+ success): 5 concurrent jobs
❌ Success rate dropped below 50% at 10 jobs. System breaking point reached!
```

**משמעות:** המערכת כבר עמוסה עם 5 jobs!

**פעולות דחופות:**
1. בדוק אם יש בעיה קיימת (high load, memory leak)
2. הגבל מיידית ל-3-5 jobs
3. חקור ופתור הבעיה לפני המשך שימוש

---

## 🛠️ **Troubleshooting**

### **בעיה: הסקריפט נכשל עם Connection Error**

```
❌ Failed to connect to Focus Server!
```

**פתרון:**
1. בדוק ש-Focus Server רץ:
   ```bash
   curl https://10.10.100.100/focus-server/ack -k
   ```

2. בדוק את ה-environment config:
   ```bash
   cat config/environments.yaml
   ```

3. בדוק SSH tunneling (אם רלוונטי)

---

### **בעיה: כל ה-jobs נכשלים**

```
Success Rate: 0.0%
```

**פתרון:**
1. הרץ job בודד ידנית:
   ```bash
   pytest tests/unit/test_basic_functionality.py -v
   ```

2. בדוק לוגים:
   ```bash
   tail -f logs/errors/*.log
   ```

3. בדוק שהפרמטרים חוקיים (channels, frequency, etc.)

---

### **בעיה: System כבר עמוס לפני הבדיקה**

```
CPU warning: 85.3%
Memory warning: 82.1%
```

**פתרון:**
1. חכה עד שהמערכת תירגע
2. נקה jobs ישנים:
   ```python
   # TODO: add cleanup script
   ```
3. הפעל מחדש את השירותים

---

## 📝 **המלצות שימוש**

### **🟢 עשה (DO):**

✅ הרץ בדיקות בשעות פעילות נמוכות  
✅ תעד את התוצאות לאורך זמן  
✅ הגדר alerts על בסיס התוצאות  
✅ בדוק אחרי כל שינוי משמעותי (deployment, config change)  
✅ השתמש ב-`--quick` לבדיקות תכופות  

### **🔴 אל תעשה (DON'T):**

❌ אל תריץ stress tests על production בשעות פיק  
❌ אל תריץ comprehensive test ללא אישור  
❌ אל תתעלם מאזהרות (< 90% success rate)  
❌ אל תריץ soak test ללא סיבה (זה שעה!)  
❌ אל תשכח לנקות jobs אחרי בדיקות  

---

## 📊 **דיווח תוצאות**

### **תבנית דיווח:**

```markdown
# Capacity Test Report - [תאריך]

## Environment
- **Server:** [staging/production]
- **Date:** [YYYY-MM-DD HH:MM]
- **Duration:** [XX minutes]

## Results
- **Maximum Capacity:** XX concurrent jobs
- **Breaking Point:** YY concurrent jobs
- **Success Rate at Max:** XX.X%
- **Avg Latency at Max:** XXXms

## System Metrics
- **CPU Max:** XX.X%
- **Memory Max:** XX.X%
- **Network:** [OK/Warning/Critical]

## Recommendations
1. [המלצה 1]
2. [המלצה 2]
3. [המלצה 3]

## Action Items
- [ ] [פעולה 1]
- [ ] [פעולה 2]
```

---

## 🔗 **קישורים נוספים**

- **מדריך מלא:** `documentation/testing/JOB_LIFECYCLE_AND_LOAD_TESTING_GUIDE.md`
- **API Documentation:** `documentation/testing/FOCUS_SERVER_API_ENDPOINTS.md`
- **Performance Tests:** `tests/integration/performance/test_performance_high_priority.py`
- **Xray Tests:** `documentation/xray/XRAY_HIGH_PRIORITY_TESTS_DOCUMENTATION.md`

---

## 👥 **תמיכה**

אם יש שאלות או בעיות:
1. בדוק את הלוגים ב-`logs/`
2. קרא את המדריך המלא
3. פתח issue/ticket

---

**נוצר על ידי:** QA Automation Team  
**תאריך:** 26 אוקטובר 2025  
**גרסה:** 1.0

