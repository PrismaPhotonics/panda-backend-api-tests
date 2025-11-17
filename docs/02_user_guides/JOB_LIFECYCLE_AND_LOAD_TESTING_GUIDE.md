# 🔄 מדריך מלא: תהליך Job ובדיקות עומס

**תאריך:** 26 אוקטובר 2025  
**מטרה:** הבנה מעמיקה של תהליך ה-Job במערכת Focus Server ובדיקת מגבלות המערכת

---

## 📖 **חלק 1: מהו Job במערכת Focus Server?**

### **הגדרה:**
**Job** (או **Task**) הוא תהליך עבודה שמגדיר את הפרמטרים לקבלת נתונים ממערכת ה-DAS (Distributed Acoustic Sensing) ועיבודם לתצוגה בממשק המשתמש.

### **סוגי Jobs:**

1. **Live Streaming Job** - הזרמת נתונים בזמן אמת מהסיב האופטי
2. **Historic Playback Job** - השמעה חוזרת של נתונים מוקלטים מהעבר

---

## 🔄 **חלק 2: מחזור חיים מלא של Job (Job Lifecycle)**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Job Lifecycle - תהליך מלא                    │
└─────────────────────────────────────────────────────────────────┘

1️⃣  CLIENT REQUEST (בקשת משתמש)
    └──> Panda App שולח POST /configure
         עם פרמטרים: channels, frequency, view_type, etc.

2️⃣  VALIDATION (אימות פרמטרים)
    └──> Focus Server בודק:
         ✓ Channels בטווח חוקי (1-2222)
         ✓ Frequency בטווח חוקי (0-1000 Hz)
         ✓ NFFT חוקי (128, 256, 512, 1024, 2048...)
         ✓ View Type תקין (0=MultiChannel, 1=SingleChannel, 2=Waterfall)

3️⃣  JOB CREATION (יצירת Job)
    └──> Focus Server:
         ✓ מייצר job_id ייחודי (UUID)
         ✓ שומר קונפיגורציה ב-MongoDB
         ✓ מקצה port ל-gRPC stream (50051, 50052, 50053...)
         ✓ מחשב תדירויות (frequencies_list)

4️⃣  BABY ANALYZER INITIALIZATION (אתחול מעבד)
    └──> Focus Server מתחיל Baby Analyzer process:
         ✓ קורא נתונים מ-Smart Recorder
         ✓ מבצע FFT (Fast Fourier Transform)
         ✓ מחשב spectrogram
         ✓ שולח תוצאות ל-RabbitMQ

5️⃣  DATA STREAMING (הזרמת נתונים)
    └──> gRPC Server מתחיל stream:
         ✓ Client מתחבר ל-stream_url:stream_port
         ✓ נתונים זורמים דרך gRPC (binary format)
         ✓ Client מציג בממשק (Spectrogram/Waterfall)

6️⃣  JOB MONITORING (מעקב)
    └──> Client יכול:
         ✓ GET /metadata/{job_id} - לקבל מידע על ה-job
         ✓ לבדוק שה-stream פעיל
         ✓ לעקוב אחר תקינות הנתונים

7️⃣  JOB TERMINATION (סיום Job)
    └──> אופציות:
         ✓ Client מתנתק → Job נסגר אוטומטית
         ✓ DELETE /job/{job_id} → ביטול ידני (אם נתמך)
         ✓ Timeout → Job נסגר אחרי 180 שניות ללא פעילות
         ✓ Historic job ends → Job נסגר כשהנתונים נגמרים

8️⃣  CLEANUP (ניקוי משאבים)
    └──> Focus Server:
         ✓ סוגר gRPC stream
         ✓ עוצר Baby Analyzer process
         ✓ משחרר port
         ✓ מעדכן MongoDB (status = "completed" / "cancelled")
```

---

## 🔧 **חלק 3: רכיבי המערכת המעורבים**

### **תרשים ארכיטקטורה:**

```
┌──────────────┐
│  Panda App   │ ◄─── 1. User interface (Frontend)
│  (Client)    │
└──────┬───────┘
       │ HTTP/REST
       ▼
┌──────────────┐
│ Focus Server │ ◄─── 2. API Gateway + Orchestrator
│  (Backend)   │
└──┬───────┬───┘
   │       │
   │       └─────────────┐
   │                     │
   ▼                     ▼
┌─────────┐        ┌──────────────┐
│ MongoDB │        │ Baby Analyzer│ ◄─── 3. Signal processor
└─────────┘        └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │Smart Recorder│ ◄─── 4. Data source (DAS system)
                   └──────┬───────┘
                          │ AMQP (RabbitMQ)
                          ▼
                   ┌──────────────┐
                   │  RabbitMQ    │ ◄─── 5. Message Queue
                   └──────────────┘
```

### **תפקיד כל רכיב:**

| רכיב | תפקיד בתהליך ה-Job | משאבים שנצרכים |
|------|-------------------|----------------|
| **Focus Server** | מנהל lifecycle, בודק validation, מתאם רכיבים | CPU (קל), RAM (בינוני), Connections |
| **Baby Analyzer** | מעבד FFT, מחשב spectrogram | CPU (כבד), RAM (כבד) |
| **MongoDB** | שומר metadata, configuration, status | Disk I/O, Connections |
| **RabbitMQ** | מעביר הודעות בין רכיבים | RAM (תורים), Network |
| **Smart Recorder** | מספק נתונים גולמיים מהסיב | Disk I/O (קריאה), Network |
| **gRPC Stream** | מזרים נתונים מעובדים ל-client | Network Bandwidth, Connections |

---

## ⚙️ **חלק 4: פרמטרים המשפיעים על עומס המערכת**

### **פרמטרים קריטיים לביצועים:**

```python
# 1. מספר ערוצים (Channels)
channels = {"min": 1, "max": 2222}
# השפעה: ככל שיותר ערוצים → יותר נתונים לעבד
# עומס: Linear (x2 channels = x2 CPU)

# 2. טווח תדירות (Frequency Range)
frequency_range = {"min": 0, "max": 1000}
# השפעה: טווח רחב יותר → יותר תדירויות לחשב
# עומס: Linear

# 3. NFFT (FFT Resolution)
nfft = 1024  # Options: 128, 256, 512, 1024, 2048, 4096...
# השפעה: NFFT גבוה יותר → רזולוציה טובה יותר אבל עומס גבוה יותר
# עומס: O(N log N) - אקספוננציאלי

# 4. View Type
view_type = 0  # 0=MultiChannel, 1=SingleChannel, 2=Waterfall
# השפעה: MultiChannel עם הרבה ערוצים = העומס הכבד ביותר

# 5. Live vs Historic
start_time = None  # None = Live (real-time)
# השפעה: Live מחייב latency נמוכה, Historic יכול להיות אסינכרוני
```

### **נוסחה לחישוב עומס:**

```python
# Load Score (ציון עומס משוער)
load_score = (
    (max_channel - min_channel + 1)  # מספר ערוצים
    * (frequency_max - frequency_min)  # טווח תדירות
    * log2(nfft)  # מורכבות FFT
    * view_multiplier  # 1.0 for Single, 1.5 for Multi, 2.0 for Waterfall
)

# דוגמה:
channels = 100
frequency_range = 1000
nfft = 1024
view_multiplier = 1.5

load_score = 100 * 1000 * 10 * 1.5 = 1,500,000

# ככל שה-load_score גבוה יותר, העומס על המערכת יותר גבוה
```

---

## 🚦 **חלק 5: מגבלות המערכת (System Limits)**

### **מגבלות ידועות:**

| מגבלה | ערך | מקור | השפעה |
|-------|-----|------|-------|
| **Max Channels** | 2222 | Client Config | בקשה עם יותר ערוצים תיכשל |
| **Max Frequency** | 1000 Hz | Client Config + PRR/2 | בקשה עם תדירות גבוהה יותר תיכשל |
| **Max NFFT (Multi)** | 2048 | Client Config | NFFT גבוה יותר לא נתמך |
| **Max NFFT (Single)** | 65536 | Client Config | NFFT גבוה מדי יגרום לזיכרון מלא |
| **Max Windows** | 30 | Client Config | לא ניתן לפתוח יותר מ-30 חלונות |
| **gRPC Timeout** | 180s | Server Config | אחרי 3 דקות ללא פעילות - ניתוק |
| **Stream Timeout** | 600s | Server Config | אחרי 10 דקות - סגירת stream |

### **מגבלות לא ידועות (צריך לבדוק!):**

| מגבלה | סטטוס | צריך לבדוק |
|-------|-------|-----------|
| **Max Concurrent Jobs** | ❓ לא ידוע | כמה jobs בו-זמנית המערכת יכולה לטפל? |
| **Max Total Throughput** | ❓ לא ידוע | כמה GB/s המערכת יכולה להזרים? |
| **Max Connections** | ❓ לא ידוע | כמה clients יכולים להתחבר בו-זמנית? |
| **CPU Threshold** | ❓ לא ידוע | מתי המערכת מתחילה לדחות בקשות? |
| **Memory Threshold** | ❓ לא ידוע | מתי המערכת נתקעת בגלל זיכרון? |

---

## 🎯 **חלק 6: תרחישי כשל אפשריים**

### **1. Too Many Concurrent Jobs (יותר מדי jobs בו-זמנית)**

```
סימפטום:
- בקשות חדשות נכשלות עם timeout
- שרת מחזיר 500 Internal Server Error
- CPU usage מגיע ל-100%

סיבה:
- כל job צורך Baby Analyzer process
- Baby Analyzer צורך הרבה CPU + RAM
- יותר מדי processes → מערכת תקועה

פתרון:
- להגביל מספר jobs concurrent (queue system)
- לסגור jobs ישנים אוטומטית
- לשדרג חומרה (יותר CPU cores)
```

### **2. Memory Exhaustion (גלישת זיכרון)**

```
סימפטום:
- שרת קורס לפתע
- Out of Memory errors בלוגים
- Jobs נכשלים באמצע

סיבה:
- NFFT גבוה מדי עם הרבה channels
- חישוב: channels * nfft * 8 bytes ≈ RAM נדרש
- דוגמה: 2000 channels * 65536 NFFT * 8 = 1GB per job!

פתרון:
- להגביל NFFT לפי מספר channels
- לנטר RAM usage
- להוסיף swap memory
```

### **3. Network Bandwidth Saturation (רוחב פס מוצף)**

```
סימפטום:
- Clients מקבלים נתונים לאט
- gRPC streams מתנתקים
- Latency גבוהה

סיבה:
- יותר מדי streams בו-זמנית
- כל stream שולח MB/s
- Network card saturated

פתרון:
- להגביל bandwidth per stream
- לצמצם resolution (פחות תדירויות)
- לשדרג network infrastructure
```

### **4. Port Exhaustion (אזילת ports)**

```
סימפטום:
- שרת מחזיר: "Failed to bind to port"
- Jobs חדשים לא יכולים להתחיל

סיבה:
- כל job צורך port (50051, 50052, ...)
- יש מגבלה של ~1000 ports זמינים
- Ports ישנים לא משוחררים

פתרון:
- לנקות ports של jobs סגורים
- להגדיל port range
- להשתמש ב-port multiplexing
```

---

## 🧪 **חלק 7: אסטרטגיית בדיקה (Testing Strategy)**

### **רמות בדיקה:**

```
1. Baseline Test (בסיס)
   └─> 1 Job בלבד
   └─> מדוד: CPU, RAM, Network, Latency
   └─> זהו ה-reference point

2. Linear Load Test (עומס ליניארי)
   └─> 5, 10, 15, 20, 25, 30 jobs
   └─> מדוד success rate בכל רמה
   └─> מצא את הנקודה שבה success rate < 90%

3. Stress Test (מתח)
   └─> המשך להוסיף jobs עד שהמערכת קורסת
   └─> זהה את הסימנים המוקדמים של כשל
   └─> בדוק איך המערכת מתאוששת

4. Soak Test (עומס ממושך)
   └─> הרץ 10 jobs במשך 24 שעות
   └─> בדוק אם יש memory leaks
   └─> בדוק אם יש resource leaks

5. Spike Test (עומס פתאומי)
   └─> מ-0 ל-50 jobs בבת אחת
   └─> בדוק איך המערכת מגיבה
   └─> בדוק recovery time
```

---

## 📊 **חלק 8: מטריקות למדידה**

### **מטריקות קריטיות:**

```yaml
Performance Metrics:
  - API Response Time:
      - p50 (median): < 200ms
      - p95: < 500ms
      - p99: < 1000ms
  
  - Job Creation Success Rate:
      - Target: > 95%
      - Warning: < 90%
      - Critical: < 80%
  
  - Stream Latency:
      - Target: < 100ms
      - Warning: < 200ms
      - Critical: > 500ms

System Metrics:
  - CPU Usage:
      - Normal: < 70%
      - Warning: 70-85%
      - Critical: > 85%
  
  - Memory Usage:
      - Normal: < 75%
      - Warning: 75-90%
      - Critical: > 90%
  
  - Network Throughput:
      - Measure: MB/s per stream
      - Monitor: total bandwidth usage
  
  - Open Connections:
      - Track: active TCP connections
      - Monitor: connection pool size

Quality Metrics:
  - Data Loss Rate:
      - Target: 0%
      - Acceptable: < 0.1%
  
  - Stream Drops:
      - Target: 0 per hour
      - Acceptable: < 1 per hour
```

---

## 🔍 **חלק 9: איך לזהות Bottlenecks (צווארי בקבוק)**

### **Bottleneck Identification Matrix:**

| תסמין | Bottleneck אפשרי | כיצד לאמת | פתרון |
|-------|------------------|-----------|--------|
| CPU 100%, jobs fail | CPU bound | `top`, `htop` | Scale horizontally, optimize code |
| High memory, OOM kills | Memory bound | `free -h`, `vmstat` | Add RAM, reduce NFFT |
| Network latency high | Network bound | `iftop`, `nethogs` | Upgrade network, compress data |
| Disk I/O wait high | Storage bound | `iostat`, `iotop` | Use SSD, add cache |
| Many TIME_WAIT sockets | Connection pool | `netstat -ant` | Increase pool, reduce timeout |
| RabbitMQ queue growing | Message broker | RabbitMQ admin | Add consumers, scale broker |
| MongoDB slow queries | Database | MongoDB profiler | Add indexes, optimize queries |

---

## 🛠️ **חלק 10: המלצות Implementation**

### **Best Practices:**

```python
# 1. Job Queue System
# במקום לאפשר unlimited jobs, השתמש ב-queue:
MAX_CONCURRENT_JOBS = 50  # To be determined by tests

job_semaphore = asyncio.Semaphore(MAX_CONCURRENT_JOBS)

async def create_job(config):
    async with job_semaphore:
        # רק MAX_CONCURRENT_JOBS יכולים לרוץ בו-זמנית
        return await _create_job_internal(config)


# 2. Resource-Based Admission Control
# דחה jobs אם המערכת עמוסה מדי:
def should_accept_job():
    cpu_usage = psutil.cpu_percent()
    mem_usage = psutil.virtual_memory().percent
    
    if cpu_usage > 85 or mem_usage > 90:
        return False, "System at capacity"
    
    return True, "OK"


# 3. Automatic Cleanup
# נקה jobs ישנים אוטומטית:
async def cleanup_stale_jobs():
    cutoff_time = datetime.now() - timedelta(minutes=30)
    
    stale_jobs = await db.jobs.find({
        "status": "running",
        "updated_at": {"$lt": cutoff_time}
    })
    
    for job in stale_jobs:
        await terminate_job(job["job_id"])


# 4. Circuit Breaker Pattern
# הפסק לקבל requests אם המערכת לא בריאה:
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = None
    
    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e
```

---

## 📋 **סיכום**

### **מה למדנו:**
1. ✅ Job = תהליך עבודה שמקבל נתונים ומעבד אותם לתצוגה
2. ✅ Lifecycle: Request → Validation → Creation → Processing → Streaming → Cleanup
3. ✅ רכיבים מעורבים: Focus Server, Baby Analyzer, MongoDB, RabbitMQ, Smart Recorder
4. ✅ פרמטרים משפיעים: Channels, Frequency, NFFT, View Type
5. ✅ מגבלות ידועות: 2222 channels, 1000 Hz, 2048 NFFT (multi), 30 windows
6. ✅ מגבלות לא ידועות: Max concurrent jobs, throughput, connections

### **מה צריך לבדוק:**
1. ❓ כמה jobs concurrent המערכת יכולה לטפל?
2. ❓ מהו ה-bottleneck העיקרי? (CPU / RAM / Network)
3. ❓ איך המערכת מגיבה לעומס יתר?
4. ❓ מהו זמן ההתאוששות אחרי עומס?

### **הצעדים הבאים:**
1. 🧪 להריץ את הסקריפטים שאני כותב עכשיו
2. 📊 לנתח את התוצאות
3. 📝 לתעד את המגבלות שמצאנו
4. 🛠️ להטמיע הגנות במערכת (queue, circuit breaker, cleanup)

---

**נוצר על ידי:** AI Assistant  
**תאריך:** 26 אוקטובר 2025

