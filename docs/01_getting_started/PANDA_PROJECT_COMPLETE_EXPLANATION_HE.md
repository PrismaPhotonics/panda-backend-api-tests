# 🐼 הסבר מפורט: פרויקט Panda - מערכת Prisma Photonics

**תאריך:** 2025-11-04  
**מעודכן:** אחרי ניתוח מלא של המערכת

---

## 📖 **מה זה פרויקט Panda?**

**Panda** הוא פרויקט של **Prisma Photonics** - מערכת מתקדמת לעיבוד והצגת נתונים מ-**DAS (Distributed Acoustic Sensing)** - מערכת סיבים אופטיים שמשמשת למעקב ולניטור אקוסטי.

### **המטרה העיקרית:**
המערכת מקבלת נתונים גולמיים מהסיב האופטי, מעבדת אותם (FFT, Spectrogram), ומציגה אותם למשתמש בממשק גרפי אינטראקטיבי.

---

## 🏗️ **ארכיטקטורה מלאה של המערכת**

### **תרשים ארכיטקטורה:**

```
┌─────────────────────────────────────────────────────────────┐
│                    מערכת Panda - מבנה מלא                    │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   Panda App      │ ◄─── Frontend (Desktop Application)
│  (Client GUI)    │      • ממשק משתמש גרפי
│                  │      • ויזואליזציה של Spectrogram
│  Location:       │      • ניהול Jobs
│  C:\Program Files│      • Live/Historic Playback
│  \Prisma\        │
│  PandaApp\       │
└──────┬───────────┘
       │ HTTP/REST API
       │ POST /configure
       │ GET /channels
       │ GET /metadata
       │ GET /ack (health check)
       ▼
┌──────────────────┐
│  Focus Server    │ ◄─── Backend (API Gateway + Orchestrator)
│  (Backend API)   │      • מנהל lifecycle של Jobs
│                  │      • בודק validation של פרמטרים
│  IP: 10.10.      │      • מתאם בין רכיבים
│  100.100:443     │      • מקצה ports ל-gRPC streams
│                  │      • שומר configuration ב-MongoDB
│  Namespace:      │
│  panda (K8s)     │
└──┬───────────┬───┘
   │           │
   │           └───────────────────┐
   │                               │
   ▼                               ▼
┌──────────┐              ┌──────────────────┐
│ MongoDB  │              │ Baby Analyzer    │ ◄─── Signal Processor
│          │              │ (gRPC Jobs)      │      • מעבד FFT
│  IP:     │              │                  │      • מחשב Spectrogram
│  10.10.  │              │  Kubernetes Jobs │      • דורש GPU
│  100.108 │              │  Namespace: panda │      • CPU/RAM כבד
│  :27017  │              │                  │      • רץ כ-Container
│          │              │  Max: 30 Jobs    │
└──────────┘              └──────┬───────────┘
   ▲                             │
   │                             │ gRPC Stream
   │                             │ (Port: 50051+)
   │                             ▼
   │                    ┌──────────────────┐
   │                    │  gRPC Stream     │ ◄─── Data Streaming
   │                    │  Server          │      • נתונים מעובדים
   │                    │                  │      • Binary format
   │                    │  Port: Dynamic   │      • Real-time streaming
   │                    │  (50051-50080)   │
   │                    └──────────────────┘
   │
   │ Metadata/Config
   │ Status Updates
   │
   └───────────────────────────────────────┐
                                            │
                                            ▼
                                   ┌──────────────────┐
                                   │  RabbitMQ        │ ◄─── Message Queue
                                   │                  │      • מעביר הודעות
                                   │  IP: 10.10.      │      • AMQP Protocol
                                   │  100.107:5672    │      • בין Smart Recorder
                                   │                  │        ל-Baby Analyzer
                                   │  Management:     │
                                   │  15672           │
                                   └──────┬───────────┘
                                          │
                                          │ AMQP Messages
                                          ▼
                                   ┌──────────────────┐
                                   │ Smart Recorder   │ ◄─── Data Source (DAS)
                                   │                  │      • מספק נתונים גולמיים
                                   │  (DAS System)    │      • מהסיב האופטי
                                   │                  │      • שולח ל-RabbitMQ
                                   └──────────────────┘
```

---

## 🔄 **תהליך Job מלא - Step by Step**

### **1️⃣ CLIENT REQUEST (בקשת משתמש)**

**מה קורה:**
- המשתמש ב-**PandaApp** בוחר פרמטרים:
  - **Channels**: טווח ערוצים (לדוגמה: 1-100)
  - **Frequency Range**: טווח תדירות (לדוגמה: 0-500 Hz)
  - **NFFT**: רזולוציה של FFT (1024, 2048, 4096...)
  - **View Type**: MultiChannel, SingleChannel, או Waterfall
  - **Time Mode**: Live (זמן אמת) או Historic (נתונים מהעבר)

**בקשה ל-Focus Server:**
```http
POST https://10.10.100.100/focus-server/configure
Content-Type: application/json

{
  "channels": {"min": 1, "max": 100},
  "frequencyRange": {"min": 0, "max": 500},
  "nfftSelection": 1024,
  "view_type": 0,  // 0=MultiChannel
  "displayTimeAxisDuration": 30,
  "start_time": null,  // null = Live mode
  "end_time": null
}
```

---

### **2️⃣ VALIDATION (אימות פרמטרים)**

**Focus Server בודק:**
- ✅ **Channels**: בטווח חוקי (1-2222)
- ✅ **Frequency**: בטווח חוקי (0-1000 Hz) ולא חורג מ-Nyquist
- ✅ **NFFT**: ערך חוקי (128, 256, 512, 1024, 2048, 4096...)
- ✅ **View Type**: תקין (0=MultiChannel, 1=SingleChannel, 2=Waterfall)
- ✅ **Time Range**: אם Historic - לא בעתיד, לא הפוך
- ✅ **Port Availability**: פורט זמין ל-gRPC stream

**אם יש שגיאה:**
```json
{
  "error": "Invalid frequency range",
  "message": "Frequency exceeds Nyquist limit",
  "status_code": 422
}
```

---

### **3️⃣ JOB CREATION (יצירת Job)**

**Focus Server יוצר Job:**
1. **מחולל job_id ייחודי** (UUID)
2. **מקצה port** ל-gRPC stream (50051, 50052, 50053...)
3. **שומר configuration** ב-MongoDB:
   ```json
   {
     "job_id": "d57c8adb-ea00-4666-83cb-0248ae9d602f",
     "status": "created",
     "channels": {"min": 1, "max": 100},
     "frequency_range": {"min": 0, "max": 500},
     "nfft": 1024,
     "view_type": 0,
     "grpc_port": 50051,
     "created_at": "2025-11-04T10:30:00Z"
   }
   ```
4. **מחשב frequencies_list** (רשימת תדירויות לעבד)
5. **מחזיר response** למשתמש:
   ```json
   {
     "job_id": "d57c8adb-ea00-4666-83cb-0248ae9d602f",
     "status": "created",
     "stream_url": "10.10.100.100:50051",
     "estimated_time": "30s"
   }
   ```

---

### **4️⃣ BABY ANALYZER INITIALIZATION (אתחול מעבד)**

**Focus Server מתחיל Baby Analyzer process:**

1. **יוצר Kubernetes Job:**
   ```yaml
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: baby-analyzer-d57c8adb
     namespace: panda
   spec:
     template:
       spec:
         containers:
         - name: baby-analyzer
           image: baby-analyzer:latest
           resources:
             limits:
               nvidia.com/gpu.shared: 1  # דורש GPU!
           env:
           - name: JOB_ID
             value: "d57c8adb-ea00-4666-83cb-0248ae9d602f"
           - name: CHANNELS_MIN
             value: "1"
           - name: CHANNELS_MAX
             value: "100"
   ```

2. **Baby Analyzer מתחבר:**
   - ✅ **ל-RabbitMQ** - מקבל נתונים גולמיים מ-Smart Recorder
   - ✅ **קורא נתונים** מהסיב האופטי (Live או Historic)
   - ✅ **מבצע FFT** (Fast Fourier Transform) על הנתונים
   - ✅ **מחשב Spectrogram** - תמונה תלת-ממדית (Time × Frequency × Amplitude)
   - ✅ **שולח תוצאות** ל-gRPC Stream Server

---

### **5️⃣ DATA STREAMING (הזרמת נתונים)**

**gRPC Stream Server מתחיל stream:**

1. **PandaApp מתחבר:**
   ```python
   # PandaApp מתחבר ל-gRPC stream
   channel = grpc.insecure_channel('10.10.100.100:50051')
   stub = FocusServerStub(channel)
   
   # מתחיל stream
   stream = stub.GetSpectrogramStream(request)
   ```

2. **נתונים זורמים:**
   - ✅ **Binary format** - יעיל מאוד
   - ✅ **Real-time** - נתונים בזמן אמת
   - ✅ **Structured data** - Spectrogram frames
   - ✅ **High bandwidth** - יכול להגיע ל-MB/s

3. **PandaApp מציג:**
   - ✅ **Spectrogram** - תמונה תלת-ממדית
   - ✅ **Waterfall** - תצוגה דו-ממדית
   - ✅ **SingleChannel** - ערוץ בודד
   - ✅ **Live updates** - עדכונים בזמן אמת

---

### **6️⃣ JOB MONITORING (מעקב)**

**PandaApp יכול לבדוק:**

```http
GET https://10.10.100.100/focus-server/metadata/d57c8adb-ea00-4666-83cb-0248ae9d602f
```

**Response:**
```json
{
  "job_id": "d57c8adb-ea00-4666-83cb-0248ae9d602f",
  "status": "running",
  "channels": {"min": 1, "max": 100},
  "frequency_range": {"min": 0, "max": 500},
  "progress": 75,  // 75% מהנתונים עובדו
  "grpc_port": 50051,
  "started_at": "2025-11-04T10:30:00Z",
  "elapsed_time": "22.5s"
}
```

---

### **7️⃣ JOB TERMINATION (סיום Job)**

**Job נסגר כאשר:**

1. **משתמש מתנתק:**
   - PandaApp נסגר או מנתק את ה-stream
   - Focus Server מזהה את הניתוק
   - Job נסגר אוטומטית

2. **Historic job נגמר:**
   - כל הנתונים מהעבר עובדו
   - Job מסתיים אוטומטית

3. **Timeout:**
   - אחרי 180 שניות ללא פעילות
   - Job נסגר אוטומטית

4. **ביטול ידני:**
   ```http
   DELETE https://10.10.100.100/focus-server/job/d57c8adb-ea00-4666-83cb-0248ae9d602f
   ```

---

### **8️⃣ CLEANUP (ניקוי משאבים)**

**Focus Server מנקה:**

1. ✅ **סוגר gRPC stream**
2. ✅ **עוצר Baby Analyzer process** (Kubernetes Job)
3. ✅ **משחרר port** (50051 זמין שוב)
4. ✅ **מעדכן MongoDB:**
   ```json
   {
     "job_id": "d57c8adb-ea00-4666-83cb-0248ae9d602f",
     "status": "completed",
     "completed_at": "2025-11-04T10:32:15Z",
     "duration": "135s"
   }
   ```
5. ✅ **משחרר משאבים** (GPU, CPU, RAM)

---

## 🎯 **מה מטרת פרויקט האוטומציה?**

### **Focus Server Automation Framework**

פרויקט האוטומציה הזה (**Focus Server Automation**) בודק את ה-**Backend (Focus Server)**:

### **1. בדיקות API**
- ✅ **Pre-launch Validation** - בדיקת פרמטרים לפני יצירת Job
- ✅ **Health Check** - בדיקת תקינות המערכת
- ✅ **Endpoints** - בדיקת כל ה-API endpoints
- ✅ **Error Handling** - בדיקת טיפול בשגיאות

### **2. בדיקות תשתית**
- ✅ **Kubernetes** - בדיקת Job lifecycle
- ✅ **MongoDB** - בדיקת איכות נתונים
- ✅ **RabbitMQ** - בדיקת קישוריות
- ✅ **Connectivity** - בדיקת קישוריות בין רכיבים

### **3. בדיקות ביצועים**
- ✅ **Latency** - בדיקת זמן תגובה (P95)
- ✅ **Load** - בדיקת עומס (200 Jobs concurrent)
- ✅ **Capacity** - בדיקת מגבלות (30 Jobs max)
- ✅ **Outage Resilience** - בדיקת עמידות בתקלות

### **4. בדיקות אינטגרציה**
- ✅ **Live Monitoring** - בדיקת Live streaming
- ✅ **Historic Playback** - בדיקת השמעה חוזרת
- ✅ **SingleChannel** - בדיקת תצוגת ערוץ בודד
- ✅ **Dynamic ROI** - בדיקת שינוי ROI בזמן אמת

---

## 📊 **פרמטרים טכניים**

### **מגבלות המערכת:**

| פרמטר | ערך מקסימלי | הערה |
|--------|-------------|------|
| **Max Channels** | 2,222 | מספר הערוצים המקסימלי |
| **Max Frequency** | 1,000 Hz | תדירות מקסימלית |
| **Max Jobs** | 30 | מספר Jobs בו-זמנית |
| **NFFT Options** | 128-65536 | רזולוציה של FFT |
| **Port Range** | 50051-50080 | Ports ל-gRPC streams |
| **Timeout** | 180s | זמן המתנה ללא פעילות |

### **משאבים נדרשים:**

| רכיב | CPU | RAM | GPU | Network |
|------|-----|-----|-----|---------|
| **Focus Server** | קל | בינוני | ❌ | בינוני |
| **Baby Analyzer** | כבד | כבד | ✅ (1 GPU/Job) | גבוה |
| **MongoDB** | בינוני | בינוני | ❌ | נמוך |
| **RabbitMQ** | קל | בינוני | ❌ | בינוני |

---

## 🔧 **סביבת Production**

### **Infrastructure:**

```
Backend Infrastructure (10.10.100.x):
├── 10.10.100.100:443  → Focus Server (HTTPS)
├── 10.10.100.107:5672 → RabbitMQ (AMQP)
├── 10.10.100.107:15672 → RabbitMQ Management
└── 10.10.100.108:27017 → MongoDB

Frontend Infrastructure (10.10.10.x):
├── 10.10.10.100:443   → Frontend/LiveView
└── 10.10.10.150:30443 → FrontendApi

Kubernetes:
├── API Server: 10.10.100.102:6443
├── Namespace: panda
└── Worker Node: 10.10.100.113
```

### **PandaApp Configuration:**

```json
{
  "Communication": {
    "Backend": "https://10.10.100.100/focus-server/",
    "Frontend": "https://10.10.10.100/liveView",
    "SiteId": "prisma-210-1000"
  },
  "Constraints": {
    "FrequencyMax": 1000,
    "MaxWindows": 30,
    "SensorsRange": 2222
  }
}
```

**Location:** `C:\Panda\usersettings.json`

---

## 🧪 **פרויקט האוטומציה**

### **מה בודקים:**

1. ✅ **API Endpoints** - כל ה-endpoints של Focus Server
2. ✅ **Pre-launch Validation** - בדיקת פרמטרים לפני Job
3. ✅ **Job Lifecycle** - יצירה, הרצה, סיום, ניקוי
4. ✅ **Data Quality** - איכות נתונים ב-MongoDB
5. ✅ **Performance** - Latency, Load, Capacity
6. ✅ **Infrastructure** - Kubernetes, MongoDB, RabbitMQ
7. ✅ **Integration** - Live, Historic, SingleChannel, ROI

### **טכנולוגיות:**

- **Python 3.12+** - שפת התכנות
- **pytest** - Framework לבדיקות
- **Playwright** - בדיקות UI (מתוכנן)
- **Locust** - בדיקות עומס
- **Xray** - אינטגרציה עם Jira

### **קבצים:**

```
tests/
├── integration/api/        # בדיקות API
├── integration/performance/ # בדיקות ביצועים
├── infrastructure/         # בדיקות תשתית
├── data_quality/          # בדיקות איכות נתונים
└── load/                  # בדיקות עומס
```

---

## 📈 **סטטיסטיקות**

### **פרויקט האוטומציה:**

- **151 טסטים** - מיושמים בקוד
- **25 Tasks** - ב-10 Stories
- **99% Coverage** - כיסוי של כל ה-API
- **10 Stories** - ב-Epic PZ-14221

### **המערכת:**

- **Max 30 Jobs** - בו-זמנית
- **2,222 Channels** - מקסימלי
- **1,000 Hz** - תדירות מקסימלית
- **Production Ready** - ✅ מוכן לשימוש

---

## 🎓 **סיכום**

**Panda** הוא מערכת מורכבת שמעבדת נתונים מאקוסטיים מהסיב האופטי ומציגה אותם למשתמש.

**המערכת כוללת:**
1. **PandaApp** - Frontend (ממשק משתמש)
2. **Focus Server** - Backend (API + Orchestration)
3. **Baby Analyzer** - Signal Processor (FFT, Spectrogram)
4. **MongoDB** - Database (Metadata, Config)
5. **RabbitMQ** - Message Queue (תקשורת)
6. **Smart Recorder** - Data Source (DAS System)

**פרויקט האוטומציה:**
- בודק את כל ה-Backend (Focus Server)
- 151 טסטים מיושמים
- כיסוי מלא של כל הפונקציונליות
- מוכן ל-Production

---

**נכתב על ידי:** QA Automation Architect  
**תאריך:** 2025-11-04  
**פרויקט:** Focus Server Automation Framework

