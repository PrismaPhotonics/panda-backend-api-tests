# 🔍 ניתוח קשר בין טיקטי Jira לשגיאת PRR

**תאריך:** 2025-11-08  
**שגיאה:** `Missing required fiber metadata fields: prr`  
**סטטוס:** 🔴 **בעיה פעילה**

---

## 📋 סיכום השגיאה

```
ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr
INFO: "POST /configure HTTP/1.1" 503 Service Unavailable
```

**השפעה:**
- כל בקשות `/configure` נכשלות
- המערכת לא יכולה להגדיר jobs חדשים
- הטסטים נכשלים

---

## 🔗 טיקטים רלוונטיים מהקבצים

### 1. **PZ-12920: support configuration changes** ⭐ **קריטי!**

**סטטוס:** CLOSED (18/Sep/25)  
**Parent:** PZ-12109 (Focus Lite MS 90 - Yoshi)  
**תיאור:**
> "when configuration changes, the historical and live researches cant support it and will crush, need to eliminate such behavior by blocking this behavior."
>
> **relevant components:**
> - mongomapper
> - recorder
> - **focus server** ⭐
> - baby

**קשר לשגיאה:**
- ✅ **קשר ישיר!** הטיקט מתאר בדיוק את הבעיה
- כשהקונפיגורציה משתנה, Focus Server לא יכול לתמוך בזה
- זה יכול לגרום לכך ש-fiber metadata לא זמין (כולל PRR)
- הפתרון שהוצע: "blocking this behavior" - אבל נראה שזה לא עובד כראוי

**ניתוח:**
- הטיקט נסגר ב-18/Sep/25, אבל הבעיה עדיין קיימת
- ייתכן שהפתרון לא כיסה את כל המקרים
- ייתכן שיש edge case שלא טופל

---

### 2. **PZ-12366: Focus server API implementation** ⭐

**סטטוס:** CLOSED (24/Aug/25)  
**Parent:** PZ-12109 (Focus Lite MS 90 - Yoshi)  
**תיאור:**
> "Goals:
> * implement all API in focus server according to design
>
> DOD:
> * after deployment system is running with 3 working points 
> * **working points and fiberlegth can be updated via backoffice** ⭐
> * live and historical data is working via noga app"

**קשר לשגיאה:**
- ✅ **קשר ישיר!** הטיקט מתאר ש-working points ו-fiber length יכולים להשתנות דרך backoffice
- כשזה קורה, Focus Server צריך לקבל metadata חדש
- אם המערכת לא מוכנה או לא קיבלה metadata, PRR יהיה חסר

**ניתוח:**
- הטיקט נסגר, אבל ייתכן שיש בעיה ב-handling של שינויים דינמיים
- המערכת צריכה לטפל ב-"waiting for fiber" state כשהקונפיגורציה משתנה

---

### 3. **PZ-12112: historical data access rely on configuration** ⭐

**סטטוס:** CLOSED (21/Oct/25)  
**Parent:** PZ-12109 (Focus Lite MS 90 - Yoshi)  
**תיאור:**
> "block historical data from more then 1 configuration"

**קשר לשגיאה:**
- ✅ **קשר עקיף** - הטיקט מתאר שהמערכת תלויה בקונפיגורציה
- אם הקונפיגורציה משתנה, המערכת חוסמת גישה
- זה יכול לגרום לכך ש-metadata לא זמין

---

### 4. **PZ-12110: backoffice integration** ⭐

**סטטוס:** CLOSED (21/Oct/25)  
**Parent:** PZ-12109 (Focus Lite MS 90 - Yoshi)  
**תיאור:**
> "* integrate backoffice into the interrogator roll.
> * configuration masking (TBD)
> * **create configuration**"

**קשר לשגיאה:**
- ✅ **קשר עקיף** - Backoffice יכול ליצור/לשנות קונפיגורציות
- כשקונפיגורציה חדשה נוצרת, Focus Server צריך metadata
- אם המערכת לא מוכנה, PRR יהיה חסר

---

### 5. **PZ-8713: Different configuration BE support** ⭐

**סטטוס:** CLOSED (21/Oct/25)  
**Parent:** PZ-12109 (Focus Lite MS 90 - Yoshi)  
**תיאור:**
> "goal - Support different configurations.
>
> DOD - after configuration have changed in the backoffice... **the focus server and baby should work and be configured and show data corresponding to the new configurations.**
>
> steps -
> # If confiuration has changed in the backoffice see that focus manager and baby are processing the data in correspondence of the new working point"

**קשר לשגיאה:**
- ✅✅ **קשר חזק מאוד!** הטיקט מתאר בדיוק את הבעיה
- כשהקונפיגורציה משתנה ב-backoffice, Focus Server צריך לעבוד עם הקונפיגורציה החדשה
- אבל אם המערכת לא קיבלה metadata חדש, PRR יהיה חסר
- זה בדיוק מה שקורה עכשיו!

**ניתוח:**
- הטיקט נסגר, אבל ייתכן שהפתרון לא מטפל בכל המקרים
- ייתכן שיש race condition בין שינוי קונפיגורציה לקבלת metadata

---

### 6. **PZ-14172: Support Focus connection to rabbit crash** ⚠️

**סטטוס:** QA Testing (06/Nov/25)  
**Parent:** PZ-12109 (Focus Lite MS 90 - Yoshi)  
**תיאור:**
> "Support Focus connection to rabbit crash"

**קשר לשגיאה:**
- ⚠️ **קשר אפשרי** - אם יש בעיה בחיבור ל-RabbitMQ, זה יכול להשפיע על קבלת metadata
- Focus Server צריך RabbitMQ כדי לקבל metadata מה-fiber
- אם החיבור נכשל, metadata לא יגיע

**ניתוח:**
- הטיקט עדיין ב-QA Testing - ייתכן שזה קשור לבעיה הנוכחית
- צריך לבדוק אם יש בעיות RabbitMQ

---

### 7. **PZ-13843: Test isolated system for delivery to field test** ⚠️

**סטטוס:** Working (28/Oct/25)  
**Parent:** PZ-12109 (Focus Lite MS 90 - Yoshi)  
**תיאור:**
> "Goal:
> * Disconnect interrogator 1045 and Linux analyzer and test all features
>
> Requirements:
> Test offline system for full features"

**קשר לשגיאה:**
- ⚠️ **קשר אפשרי** - אם המערכת במצב isolated/offline, אין fiber מחובר
- זה יכול לגרום למצב "waiting for fiber"
- במצב הזה, PRR יהיה חסר

---

### 8. **PZ-14644: VMs autostart** ⚠️

**סטטוס:** TO DO (05/Nov/25)  
**Parent:** PZ-12109 (Focus Lite MS 90 - Yoshi)  
**תיאור:**
> "We need to understand why VMs don't autostart and fix it, to avoid having to manually start them"

**קשר לשגיאה:**
- ⚠️ **קשר אפשרי** - אם VMs לא מתחילות אוטומטית, המערכת עלולה להיות במצב לא מוכן
- זה יכול לגרום לכך ש-metadata לא זמין

---

### 9. **PZ-14636: iscsi issues after reboot** ⚠️

**סטטוס:** TO DO (05/Nov/25)  
**Parent:** PZ-12109 (Focus Lite MS 90 - Yoshi)  
**תיאור:**
> "In the Yoshi systems, we encountered a problem in which the iscsi didn't log in automatically
> We need to understand how to make sure it loads up and logs in"

**קשר לשגיאה:**
- ⚠️ **קשר אפשרי** - אם iSCSI לא מתחבר, זה יכול להשפיע על גישה ל-storage/data
- זה יכול לגרום לכך ש-metadata לא זמין

---

## 🔍 ניתוח הקוד - איך Focus Server מקבל PRR

### FocusManager Initialization

```python
# pz/microservices/focus_server/focus_manager.py:22-38
def __init__(self, prr=2000, storage_path=r"Z:\segy"):
    self.prr = prr  # Default: 2000
    # ...
    logger.info("Opening a recording to init metadata")
    # Extracting metadata from recording, will block until get data.
    temp_rec = Recording.open_recording('amqp://')
    self.fiber_metadata = temp_rec.metadata  # ← מקבל metadata מ-RabbitMQ
    self.sensors = self.fiber_metadata.num_samples_per_trace
    temp_rec.end_recording()
    logger.info("Done metadata init fiber metadata")
```

**מה קורה:**
1. FocusManager מנסה לפתוח recording מ-RabbitMQ (`amqp://`)
2. הוא מחכה לקבל metadata (blocking)
3. הוא שומר את ה-metadata ב-`self.fiber_metadata`
4. הוא משתמש ב-`self.fiber_metadata.num_samples_per_trace` לקבלת sensors

**הבעיה:**
- אם אין recording זמין ב-RabbitMQ, זה יכול להיכשל
- אם המערכת במצב "waiting for fiber", metadata לא יהיה זמין
- אם הקונפיגורציה השתנתה, metadata ישן לא יהיה תקף

---

## 🎯 הקשר בין הטיקטים לשגיאה

### תרחיש אפשרי:

1. **שינוי קונפיגורציה ב-Backoffice** (PZ-8713, PZ-12110)
   - Backoffice משנה את הקונפיגורציה
   - Focus Server צריך metadata חדש

2. **Focus Server לא מקבל metadata** (PZ-12920)
   - כשהקונפיגורציה משתנה, Focus Server לא יכול לתמוך בזה
   - Metadata לא מתעדכן
   - PRR נשאר חסר

3. **בקשות /configure נכשלות** (השגיאה הנוכחית)
   - כל בקשה ל-`/configure` דורשת PRR
   - PRR חסר → שגיאה 503

### תרחיש נוסף:

1. **המערכת במצב "waiting for fiber"** (PZ-13843)
   - אין fiber פיזי מחובר
   - או המערכת במצב isolated/offline

2. **Focus Server לא יכול לקבל metadata**
   - אין recording ב-RabbitMQ
   - Metadata לא זמין

3. **בקשות /configure נכשלות**
   - PRR חסר → שגיאה 503

---

## 🔧 המלצות לפתרון

### 1. בדוק את מצב המערכת

```bash
# בדוק אם יש metadata זמין
curl -k https://10.10.10.100/focus-server/live_metadata | jq

# בדוק את לוגי Focus Server
kubectl logs -n panda -l app.kubernetes.io/name=panda-panda-focus-server --tail=100 | grep -i "metadata\|prr\|fiber"
```

### 2. בדוק אם יש שינויי קונפיגורציה אחרונים

- בדוק את Backoffice - האם הייתה שינוי קונפיגורציה?
- בדוק את לוגי Backoffice
- בדוק את MongoDB - האם יש קונפיגורציות חדשות?

### 3. בדוק את חיבור RabbitMQ

```bash
# בדוק את סטטוס RabbitMQ
kubectl get pods -n panda | grep rabbitmq

# בדוק את לוגי RabbitMQ
kubectl logs -n panda -l app.kubernetes.io/instance=rabbitmq-panda --tail=50
```

### 4. פתרון מיידי

אם המערכת במצב "waiting for fiber":
- המתן עד שהמערכת תהיה מוכנה
- או פנה ל-DevOps/Infrastructure לבדיקה

אם יש שינוי קונפיגורציה:
- בדוק אם Focus Server צריך restart
- בדוק אם metadata מתעדכן כראוי

---

## 📊 סיכום הקשרים

| טיקט | קשר | רמת רלוונטיות | סטטוס |
|------|-----|---------------|-------|
| **PZ-12920** | ישיר - "configuration changes cause crashes" | ⭐⭐⭐ | CLOSED |
| **PZ-8713** | ישיר - "Different configuration BE support" | ⭐⭐⭐ | CLOSED |
| **PZ-12366** | ישיר - "working points can be updated" | ⭐⭐ | CLOSED |
| **PZ-12112** | עקיף - "rely on configuration" | ⭐⭐ | CLOSED |
| **PZ-12110** | עקיף - "backoffice integration" | ⭐⭐ | CLOSED |
| **PZ-14172** | אפשרי - "RabbitMQ crash" | ⭐ | QA Testing |
| **PZ-13843** | אפשרי - "isolated system" | ⭐ | Working |
| **PZ-14644** | אפשרי - "VMs autostart" | ⭐ | TO DO |
| **PZ-14636** | אפשרי - "iscsi issues" | ⭐ | TO DO |

---

## 🎯 מסקנות

### הקשר העיקרי:

**PZ-12920** ו-**PZ-8713** מתארים בדיוק את הבעיה:
- כשהקונפיגורציה משתנה, Focus Server לא יכול לתמוך בזה
- זה גורם לכך ש-metadata (כולל PRR) לא זמין
- בקשות `/configure` נכשלות

### למה זה קורה עכשיו?

1. **שינוי קונפיגורציה אחרון** - ייתכן שהייתה שינוי קונפיגורציה ב-Backoffice
2. **המערכת במצב "waiting for fiber"** - אין fiber פיזי מחובר
3. **בעיית RabbitMQ** - ייתכן שיש בעיה בחיבור ל-RabbitMQ (PZ-14172)
4. **המערכת במצב initialization** - המערכת עדיין לא מוכנה

### מה לעשות?

1. **בדוק את מצב המערכת** - האם יש metadata זמין?
2. **בדוק שינויי קונפיגורציה** - האם הייתה שינוי ב-Backoffice?
3. **בדוק את RabbitMQ** - האם יש בעיות חיבור?
4. **בדוק את לוגי Focus Server** - מה אומרים הלוגים?

---

## 🔍 ניתוח הקוד - איך Focus Server משתמש ב-PRR

### FocusManager Initialization

```python
# pz/microservices/focus_server/focus_manager.py:22-38
def __init__(self, prr=2000, storage_path=r"Z:\segy"):
    self.prr = prr  # Default: 2000
    # ...
    logger.info("Opening a recording to init metadata")
    # Extracting metadata from recording, will block until get data.
    temp_rec = Recording.open_recording('amqp://')
    self.fiber_metadata = temp_rec.metadata  # ← מקבל metadata מ-RabbitMQ
    self.sensors = self.fiber_metadata.num_samples_per_trace
    temp_rec.end_recording()
    logger.info("Done metadata init fiber metadata")
```

**מה קורה:**
1. FocusManager מנסה לפתוח recording מ-RabbitMQ (`amqp://`)
2. הוא מחכה לקבל metadata (blocking)
3. הוא שומר את ה-metadata ב-`self.fiber_metadata`
4. הוא משתמש ב-`self.fiber_metadata.num_samples_per_trace` לקבלת sensors

**הבעיה:**
- אם אין recording זמין ב-RabbitMQ, זה יכול להיכשל
- אם המערכת במצב "waiting for fiber", metadata לא יהיה זמין
- אם הקונפיגורציה השתנתה, metadata ישן לא יהיה תקף

### שימוש ב-PRR ב-parse_task_configuration

```python
# pz/microservices/focus_server/focus_server.py:85
window_overlap = 1 - (display_time_axis_duration * focus_manager.prr) / ((configuration["canvasInfo"]["height"] * n_fft))

# שורה 66
rows_per_second = (focus_manager.prr / ((1 - window_overlap) * n_fft))
```

**מה קורה:**
- `focus_manager.prr` משמש בחישובים קריטיים
- אם PRR חסר או 0, החישובים יכשלו
- זה יכול לגרום לשגיאת validation

---

## 🎯 מסקנות סופיות

### הקשר העיקרי בין הטיקטים לשגיאה:

1. **PZ-12920** ו-**PZ-8713** מתארים בדיוק את הבעיה:
   - כשהקונפיגורציה משתנה, Focus Server לא יכול לתמוך בזה
   - זה גורם לכך ש-metadata (כולל PRR) לא זמין
   - בקשות `/configure` נכשלות

2. **הקוד מראה:**
   - FocusManager מקבל metadata ב-init מ-RabbitMQ
   - אם אין recording זמין, metadata לא יהיה זמין
   - PRR משמש בחישובים קריטיים - אם חסר, הכל נכשל

3. **התרחיש הסביר:**
   - שינוי קונפיגורציה ב-Backoffice (PZ-8713, PZ-12110)
   - Focus Server לא מקבל metadata חדש (PZ-12920)
   - PRR נשאר חסר או 0
   - כל בקשות `/configure` נכשלות

---

## 🔧 פעולות מיידיות מומלצות

### 1. בדוק את מצב המערכת ✅ **בוצע - 2025-11-08 13:15**

```bash
# בדוק metadata
curl -k https://10.10.10.100/focus-server/live_metadata | jq
```

**תוצאות:**
```json
{
  "dx": 0.0,
  "prr": 0.0,
  "sw_version": "waiting for fiber",
  "number_of_channels": 2337,
  "fiber_description": "waiting for fiber"
}
```

**מסקנה:** המערכת במצב **"waiting for fiber"** - אין fiber פיזי מחובר.

```bash
# בדוק את לוגי Focus Server
kubectl logs -n panda -l app.kubernetes.io/name=panda-panda-focus-server --tail=100 | grep -i "metadata\|prr\|fiber\|recording"
```

**תוצאות:** שגיאות חוזרות כל 2-3 שניות:
```
ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr
```

```bash
# בדוק את RabbitMQ
kubectl logs -n panda -l app.kubernetes.io/instance=rabbitmq-panda --tail=50
```

**תוצאות:** ✅ **תקין** - אין בעיות חיבור

### 2. בדוק אם הייתה שינוי קונפיגורציה ⏳ **לבדוק**

- בדוק את Backoffice - האם הייתה שינוי קונפיגורציה אחרונה?
- בדוק את MongoDB - האם יש קונפיגורציות חדשות?
- בדוק את לוגי Backoffice

### 3. פתרון מיידי ✅ **זוהה - המערכת במצב "waiting for fiber"**

**מצב נוכחי (2025-11-08 13:15):**
- המערכת במצב **"waiting for fiber"**
- `prr: 0.0` (לא תקין)
- `sw_version: "waiting for fiber"`
- כל בקשות `/configure` נכשלות

**פעולות נדרשות:**
1. ✅ **זוהה** - המערכת במצב "waiting for fiber"
2. ⏳ **להמתין** עד שהמערכת תהיה מוכנה (אם יש fiber פיזי שמתחבר)
3. ⏳ **לבדוק** שיש fiber פיזי מחובר
4. ⏳ **לפנות ל-DevOps/Infrastructure** לבדיקה

**ראה מסמך מפורט:** `docs/04_testing/analysis/PRR_ERROR_CURRENT_STATUS_2025-11-08.md`

---

**עודכן לאחרונה:** 2025-11-08  
**סטטוס:** 🔴 בעיה פעילה - דורש טיפול מיידי

