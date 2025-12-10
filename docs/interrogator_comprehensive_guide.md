# מדריך מקיף: כל החלקים של האינטגרטור (Interrogator)

## תוכן עניינים
1. [סקירה כללית](#סקירה-כללית)
2. [ארכיטקטורה ברמה גבוהה (Macro View)](#ארכיטקטורה-ברמה-גבוהה)
3. [רכיבי הליבה של האינטגרטור (Micro View)](#רכיבי-הליבה)
4. [תהליכי עבודה וזרימות נתונים](#תהליכי-עבודה)
5. [אינטגרציות חיצוניות](#אינטגרציות-חיצוניות)
6. [ניהול ותפעול](#ניהול-ותפעול)

---

## סקירה כללית

### מהו האינטגרטור?

האינטגרטור (Interrogator) הוא רכיב מרכזי במערכת Prisma Edge System האחראי על:
- **עיבוד אותות** - עיבוד בסיסי של אותות אופטיים
- **הקלטת נתונים** - הקלטת נתוני PRP (Prisma Recording Protocol)
- **ניהול חומרה** - שליטה על יחידת האופטיקה והדיגיטייזר
- **תקשורת** - תקשורת עם רכיבי המערכת האחרים (Analyzer, UI, Storage)

### מיקום במערכת הכללית

```
┌─────────────────────────────────────────────────────────┐
│              Prisma Edge System Architecture             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐ │
│  │ Optical Unit │───▶│ Interrogator │───▶│ Analyzer │ │
│  │   (Beacon)   │    │              │    │          │ │
│  └──────────────┘    └──────────────┘    └──────────┘ │
│                              │                  │        │
│                              ▼                  ▼        │
│                       ┌──────────────┐   ┌──────────┐  │
│                       │ NAS/Storage  │   │ UI Host  │  │
│                       └──────────────┘   └──────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## ארכיטקטורה ברמה גבוהה

### סוגי פריסה (Deployment Types)

| סוג פריסה | תצורה | שימוש |
|-----------|-------|------|
| **Fort** | Interrogator + Analyzer + NAS + UIHost (4 מכונות) | Eagle, Dove - אבטחת היקף |
| **All-In-One** | מכונה אחת עם תפקידי Interrogator & Analyzer | Power, Flow, Shaked |
| **Cloud/Online** | גישה מרחוק מופעלת, CC/UI בענן | פריסה סטנדרטית |
| **On-Prem** | ללא גישה מרחוק, UI Host ייעודי באתר | התקנות מאובטחות |

### ורטיקלים (Algorithm Types)

| ורטיקל | סוג פריסה | תיאור |
|--------|-----------|-------|
| **Eagle** | Fort | אבטחת היקף |
| **Dove** | Fort | אבטחת היקף |
| **Flow** | All-In-One | ניטור צינורות |
| **Power** | All-In-One | ניטור קווי חשמל |
| **Shaked/Watch** | All-In-One + מכונת מחקר | מחקר/פתרונות |

---

## רכיבי הליבה

### 1. Supervisor - מנהל התהליכים הראשי

**תפקיד:** מנהל ומתאם את כל השירותים והתהליכים במערכת

**תכונות עיקריות:**
- הפעלה ועצירה של שירותים
- ניהול מחזור חיים של תהליכים
- מעקב אחר תקלות והתאוששות
- ניהול תלויות בין שירותים

**קבצים מרכזיים:**
- `supervisor.yaml` - קונפיגורציה של כל השירותים
- `supervisor.log` - לוגים של מנהל התהליכים

---

### 2. Preprocessor - מעבד האותות

**תפקיד:** עיבוד בסיסי של אותות אופטיים מהדיגיטייזר

**תהליכי עבודה:**
- קבלת נתונים מהדיגיטייזר
- עיבוד אותות (FFT, פילטרים)
- שליחה לרכיבים הבאים:
  - `ml_algo` - אלגוריתמי ML
  - `smart_recorder` - הקלטת PRP
  - `baby_analyzer` - עיבוד ביניים

**תכונות:**
- עיבוד בזמן אמת
- ניהול buffers
- בדיקות תקינות נתונים

**תורים (Queues):**
- `Algo_ml` → ml_algo
- `baby` → baby_analyzer
- `smart_recorder` → smart_recorder
- `smart_recorder.heatMaps` → heatmap recorders

---

### 3. Peripherals - ממשק חומרה

**תפקיד:** שליטה על רכיבי החומרה

**רכיבים נשלטים:**
- **Optical Unit (Beacon)** - יחידת האופטיקה
  - לייזר
  - חומרה מוטמעת
- **Digitizer** - דיגיטייזר
  - Ultra vs Fort
  - הקלטת אותות אנלוגיים

**תכונות:**
- ניהול חיבורים
- בקרת כוח
- ניטור מצב חומרה

---

### 4. Smart Recorder - הקלטת PRP

**תפקיד:** הקלטת נתוני PRP (Prisma Recording Protocol) לאחסון

**תכונות:**
- הקלטה רציפה
- ניהול אחסון (FIFO rollover)
- בדיקות תקינות קבצים
- תמיכה ב-Limited Recovery ו-Machine Failure Recovery

**תורים:**
- `smart_recorder` - Limited Recovery
- `smart_recorder.heatMaps` - Machine Failure Recovery

**פורמטים:**
- PRP files
- Heatmap recordings (סוגים שונים)

---

### 5. Heatmap Recorders - הקלטת Heatmaps

**תפקיד:** הקלטת נתוני Heatmaps לסוגים שונים

**סוגי Heatmaps:**
- `DefaultChannel` - ערוץ ברירת מחדל
- `FreqSpan` - טווח תדרים
- `Poles` - קטבים
- `ExtendedAnomalyInfoBatch` - מידע אנומליות מורחב
- `MeanBatchData` - ממוצע נתונים
- `StdValuePerPixel` - סטיית תקן לכל פיקסל
- `TransientInfo` - מידע חולף
- `WindChnlFftFeatures` - תכונות FFT לערוץ רוח
- `WindFeaturesAndSpectraAgg` - תכונות רוח וספקטרה מצטברת
- `AccumPerAngle` - מצטבר לפי זווית

---

### 6. Baby Analyzer - עיבוד ביניים

**תפקיד:** עיבוד ביניים של אותות

**תהליכים:**
- Decimation - דגימה מחדש
- Unwrap - פתיחת פאזה
- עיבוד נוסף לפני האלגוריתמים

**תור:**
- `baby` ← preprocessor

---

### 7. Fiber Inspector - ניטור בריאות סיב

**תפקיד:** ניטור בריאות הסיב האופטי

**ערוצים:**
- **OTDRX** - Optical Time Domain Reflectometry (X)
- **OTDRY** - Optical Time Domain Reflectometry (Y)

**תכונות:**
- זיהוי חתכים בסיב
- זיהוי חיבורים
- ניטור איכות סיב
- Baseline management
- ניקוי התראות היסטוריות

**תורים:**
- `fiber_inspector.OTDRX`
- `fiber_inspector.OTDRY`

---

### 8. Data Manager - ניהול דיסק

**תפקיד:** ניהול אחסון וקיבולת דיסק

**תכונות:**
- **FIFO Rollover** - מחיקה אוטומטית של קבצים ישנים
- ניהול קיבולת
- הגנה על אחסון
- ניטור מקום פנוי

**ניטור:**
- PRP paths
- Heatmap paths
- C-drive growth

---

### 9. BIT (Built-In Test) - בדיקות מובנות

**תפקיד:** בדיקות תקינות מערכת מובנות

**סוגי בדיקות:**
- **Status Tests** - בדיקות סטטוס
- **System Tests** - בדיקות מערכת
- **Operational Tests** - בדיקות תפעוליות

**קבצי לוג:**
- `pz.bit_status.log` - לוגי סטטוס
- `pz.bit_test.log` - לוגי בדיקות
- `pz.bit_system.log` - לוגי מערכת

**תכונות:**
- בדיקות מחזוריות
- דיווח על תקלות
- ולידציה של רכיבים

---

### 10. Telegraf - איסוף מטריקות

**תפקיד:** איסוף ומשלוח מטריקות למערכת ניטור

**תכונות:**
- איסוף מטריקות מהמערכת
- שליחה ל-Analyzer דרך RabbitMQ
- אינטגרציה עם Prometheus/Grafana

**תורים:**
- `prisma-metrics` - מטריקות Interrogator
- `prisma-metrics-forward` - העברה ל-Analyzer

---

### 11. RabbitMQ - Message Broker

**תפקיד:** תיווך הודעות בין כל הרכיבים

**תורים מרכזיים:**

| תור | סוג | מקור → יעד | תיאור |
|-----|-----|------------|-------|
| `Algo_ml` | Service | preprocessor → ml_algo | נתונים לאלגוריתמי ML |
| `baby` | Service | preprocessor → baby_analyzer | נתונים לעיבוד ביניים |
| `smart_recorder` | Limited Recovery | preprocessor → smart_recorder | הקלטת PRP |
| `smart_recorder.heatMaps` | Machine Failure Recovery | preprocessor → heatmap recorders | הקלטת Heatmaps |
| `prisma-metrics` | Durable | BIT → telegraf | מטריקות |
| `prisma-metrics-forward` | Durable | interrogator-telegraf → analyzer-telegraf | העברת מטריקות |
| `fiber_inspector.OTDRX/Y` | Service | preprocessor → fiber_inspector | נתוני Fiber Inspector |

**סוגי הודעות:**
- `KeepAlive` - הודעות חיים
- `Heartbeat` - דופק
- `EndOfJob` - סיום עבודה
- `ProcessCrash` - קריסת תהליך
- `Prpcast.Info` - מידע PRP
- `Prpcast.Chunk` - נתוני PRP

---

### 12. MongoDB - מסד נתונים

**תפקיד:** אחסון נתונים מובנים

**Collections מרכזיות:**
- **Alerts** - התראות
- **Recordings** - הקלטות (metadata)
- **System Info** - מידע מערכת

**שימושים:**
- אחסון התראות
- metadata של הקלטות
- מידע מערכת

---

## תהליכי עבודה

### זרימת נתונים בסיסית

```
┌─────────────┐
│  Digitizer  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Preprocessor │
└──────┬──────┘
       │
       ├───▶ ml_algo ───▶ Alerts ───▶ MongoDB
       │
       ├───▶ baby_analyzer ───▶ Heatmaps
       │
       ├───▶ smart_recorder ───▶ PRP Files ───▶ NAS/Storage
       │
       └───▶ fiber_inspector ───▶ OTDR Data
```

### תהליך אינטגרציה של גרסה

1. **הכנה**
   - הגדרת scope של גרסה
   - הגדרת מטריצת בדיקות
   - הכנת תצורות

2. **פיתוח**
   - פיתוח תכונות
   - בדיקות יחידה
   - אינטגרציה קטנה

3. **אינטגרציה**
   - מיזוג קוד
   - בדיקות אינטגרציה
   - בדיקות יציבות

4. **בדיקות יציבות (48 שעות)**
   - הרצה רציפה
   - ניטור משאבים
   - בדיקות תקינות

5. **שחרור**
   - תיעוד
   - שחרור ללקוחות
   - תמיכה

---

## אינטגרציות חיצוניות

### 1. Focus Server Integration

**תפקיד:** אינטגרציה עם Focus Server לזרימת נתונים

**Endpoints:**
- `POST /configure` - הגדרת עבודה
- `GET /channels` - רשימת ערוצים זמינים
- `GET /live_metadata` - metadata בזמן אמת
- `GET /metadata/{job_id}` - metadata לפי job ID
- `POST /recordings_in_time_range` - בדיקת הקלטות בטווח זמן

**זרימות:**
- **Live Mode** - נתונים בזמן אמת דרך RabbitMQ
- **Historic Mode** - נתונים היסטוריים מ-Storage

---

### 2. Control Centre (CC)

**תפקיד:** ניהול מרכזי של מערכות

**תכונות:**
- ניטור מערכות מרוחקות
- ניהול תצורות
- עדכוני גרסאות
- גישה מרחוק

**דרישות:**
- חיבור VPN תמידי
- DNS תקין
- תקשורת יציבה

---

### 3. UI Applications

**תפקידים:**
- **Panda App** - ממשק משתמש חדש
- **Control Centre UI** - ממשק ניהול
- **Grafana** - דשבורד ניטור
- **Prometheus** - איסוף מטריקות

---

### 4. External Integrations

**תכונות:**
- **MARS Integration** - אינטגרציה עם MARS
- **Wind Integration** - אינטגרציה עם מערכות רוח
- **Back Office** - מערכת ניהול פנימית
- **Data Engineering API** - API לניהול נתונים

---

## ניהול ותפעול

### כלי ניהול

| כלי | תיאור | שימוש |
|-----|-------|------|
| **TI Tool** | כלי תצורה | תצורת מערכות |
| **ATP Script** | סקריפט בדיקות | בדיקות אוטומטיות |
| **Calibration GUI** | ממשק כיול | ניהול כיולים |
| **YeudiApp** | כלי צפייה | צפייה ב-waterfall |
| **PZ Waterfall** | כלי ויזואליזציה | יצירת גרפים |

### ניטור ו-Health Checks

**מטריקות מנוטרות:**
- CPU usage
- Memory usage
- Disk space
- GPU utilization
- Network traffic
- Queue depths
- Service health

**Health Checks:**
- Service status
- Queue health
- Heartbeat validation
- Keep-alive checks
- Database connectivity

### בדיקות אוטומציה (InterrogatorQA)

**סוגי בדיקות:**
- **Smoke** - בדיקות מהירות (~10-15 דקות)
- **Long-term** - בדיקות ארוכות טווח (שעות)
- **Reliability** - בדיקות אמינות
- **Recoverability** - בדיקות התאוששות

**אזורים נבדקים:**
- Bring-up & Health
- Message Bus Health
- Resource Usage
- Alerts & HeatMaps
- PRP Recording
- Stability
- Database Integrity
- BIT Tests

---

## סיכום

האינטגרטור הוא רכיב מורכב המורכב מ:

1. **12 שירותי ליבה** המנוהלים על ידי Supervisor
2. **תשתית תקשורת** מבוססת RabbitMQ
3. **מערכת אחסון** מבוססת NAS/Storage
4. **אינטגרציות חיצוניות** מרובות
5. **מערכת ניטור** מקיפה

כל רכיב תורם לתפקוד הכללי של המערכת, וניהול נכון של כל החלקים קריטי להצלחת המערכת.

---

## מקורות

- Interrogator Team - QA & Automation Perspective: Macro & Micro Analysis
- Interrogator integration and stability testing process
- Interrogator developer onboarding plan
- Focus Server – Integrations Map
- InterrogatorQA - Product level overview

---

*מסמך זה עודכן לאחרונה: 2025-01-XX*

