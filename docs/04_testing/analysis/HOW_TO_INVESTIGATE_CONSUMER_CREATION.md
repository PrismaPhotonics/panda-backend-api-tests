# 🔍 מדריך לחקירת בעיות Consumer Creation
## How to Investigate Consumer Creation Issues

**תאריך:** 2025-11-13  
**מטרה:** לבדוק למה Consumer לא נוצר

---

## 🚀 הרצת הבדיקה

### דרך 1: Python Script (מומלץ)

```bash
# מהשורש של הפרויקט
python scripts/investigate_consumer_creation_issue.py --job-id 19-7 --environment staging
```

### דרך 2: דרך pytest

```bash
# מהשורש של הפרויקט
pytest be_focus_server_tests/integration/data_quality/test_investigate_consumer_creation.py -v -s
```

---

## 📋 מה הסקריפט בודק

### 1. Backend Logs ✅

**מה בודק:**
- האם Backend מקבל בקשות `GET /metadata/{job_id}`?
- מה Backend מחזיר?
- האם יש שגיאות בלוגים?

**איך בודק:**
1. מוצא את Backend pod (`panda-panda-focus-server`)
2. מביא את הלוגים האחרונים (1000 שורות)
3. מחפש את ה-job_id בלוגים
4. מציג את השורות הרלוונטיות

**מה לחפש:**
- `GET /metadata/19-7`
- `Invalid job_id`
- `job_id: 19-7`
- שגיאות הקשורות ל-job_id

---

### 2. MongoDB ✅

**מה בודק:**
- האם Job נרשם ב-MongoDB?
- האם Consumer נרשם ב-MongoDB?
- מה הנתונים שנשמרו?

**איך בודק:**
1. מתחבר ל-MongoDB (staging: `10.10.10.108:27017`)
2. מחפש Job ב-collections: `jobs`, `job`, `configurations`, `configs`
3. מחפש Consumer ב-collections: `consumers`, `consumer`, `consumer_status`
4. מציג את הנתונים שנמצאו

**מה לחפש:**
- Job עם `job_id: "19-7"`
- Consumer עם `job_id: "19-7"`
- נתונים נוספים על ה-Job/Consumer

---

### 3. Consumer Service ✅

**מה בודק:**
- האם Consumer Service רץ?
- האם יש Pods של Consumer Service?
- מה הלוגים של Consumer Service?

**איך בודק:**
1. מחפש Pods עם selectors: `app=consumer`, `app=consumer-service`, `component=consumer`
2. אם לא מוצא, מחפש Pods עם "consumer" בשם
3. מביא את הלוגים של כל Pod שנמצא
4. מחפש את ה-job_id בלוגים

**מה לחפש:**
- Pods של Consumer Service
- לוגים שמזכירים את ה-job_id
- שגיאות ב-Consumer creation

---

### 4. K8s Pods and Labels ✅

**מה בודק:**
- האם Pods נוצרו?
- מה ה-Labels של ה-Pods?
- האם יש `job_id` label?

**איך בודק:**
1. מביא את כל ה-Pods ב-namespace `panda`
2. מחפש Pods שמכילים את ה-job_id בשם
3. בודק את ה-Labels של כל Pod
4. מנתח האם יש `job_id` label

**מה לחפש:**
- Pods עם שם שמכיל `19-7` (כמו `grpc-job-19-7-xxx`)
- Labels: `job_id`, `app`, `job-name`
- האם `job_id` label קיים ותואם

---

## 📊 דוגמה: Output

```
================================================================================
INVESTIGATING CONSUMER CREATION ISSUE FOR JOB_ID: 19-7
================================================================================

================================================================================
1. CHECKING BACKEND LOGS
================================================================================
✅ Found Backend pod: panda-panda-focus-server-xxx
Fetching logs from panda-panda-focus-server-xxx...
✅ Found 15 log entries mentioning 19-7
  [2025-11-13 15:25:31] GET /metadata/19-7 → 404 Invalid job_id
  [2025-11-13 15:25:32] GET /metadata/19-7 → 404 Invalid job_id
  ...

================================================================================
2. CHECKING MONGODB
================================================================================
Connecting to MongoDB...
✅ Connected to MongoDB
Searching for job_id: 19-7...
⚠️  Job 19-7 not found in MongoDB
Searching for consumer with job_id: 19-7...
⚠️  Consumer for job 19-7 not found in MongoDB

================================================================================
3. CHECKING CONSUMER SERVICE
================================================================================
⚠️  No Consumer Service pods found
Listing all pods in namespace:
  panda-panda-focus-server-xxx | Running
  mongodb-xxx | Running
  ...

================================================================================
4. CHECKING K8S PODS AND LABELS
================================================================================
✅ Found 2 pods matching job_id 19-7

  Pod: cleanup-job-19-7-2tj8z
    Status: Running
    Ready: True
    Labels:
      app: cleanup-job-19-7
      controller-uid: xxx
      job-name: cleanup-job-19-7
    ⚠️  No job_id label found

  Pod: grpc-job-19-7-8rlgb
    Status: Running
    Ready: True
    Labels:
      app: grpc-job-19-7
      controller-uid: xxx
      job-name: grpc-job-19-7
    ⚠️  No job_id label found

  Labels Analysis:
    Pods with job_id label: 0
    Pods without job_id label: 2

================================================================================
SUMMARY
================================================================================

Job ID: 19-7
Timestamp: 2025-11-13T15:30:00

📋 Backend Logs:
  ✅ Found logs mentioning 19-7

📋 MongoDB:
  ⚠️  Job NOT found in MongoDB
  ⚠️  Consumer NOT found in MongoDB

📋 Consumer Service:
  ⚠️  No Consumer Service pods found

📋 K8s Pods:
  ✅ Found 2 pod(s) matching 19-7
    ⚠️  cleanup-job-19-7-2tj8z missing job_id label
    ⚠️  grpc-job-19-7-8rlgb missing job_id label

💡 RECOMMENDATIONS:
  1. ⚠️  Job not found in MongoDB - Backend may not have saved the job
  2. ⚠️  Consumer not found in MongoDB - Consumer Service may not have created it
  3. ⚠️  2 pod(s) missing job_id label - Backend may not find them
     → Consider adding job_id label to Pods during creation
  4. ⚠️  Consumer Service not found - may not be running or named differently
```

---

## 🔧 פתרון בעיות נפוצות

### בעיה 1: Job לא נמצא ב-MongoDB

**סיבות אפשריות:**
- Backend לא שמר את ה-Job
- Job נשמר ב-collection אחר
- Job נמחק

**פתרונות:**
1. לבדוק Backend logs - האם יש שגיאות ב-save?
2. לבדוק collections אחרים ב-MongoDB
3. לבדוק אם Job נמחק

---

### בעיה 2: Consumer לא נמצא ב-MongoDB

**סיבות אפשריות:**
- Consumer Service לא רץ
- Consumer Service לא יוצר Consumer
- Consumer נשמר ב-collection אחר

**פתרונות:**
1. לבדוק אם Consumer Service רץ
2. לבדוק את הלוגים של Consumer Service
3. לבדוק collections אחרים

---

### בעיה 3: אין `job_id` label ב-Pods

**סיבות אפשריות:**
- Backend לא מוסיף label כשהוא יוצר Pods
- Label נמחק
- Label עם שם אחר

**פתרונות:**
1. לבדוק את קוד ה-Backend - האם הוא מוסיף label?
2. לבדוק את ה-K8s Job definition
3. להוסיף label ידנית (אם צריך)

---

### בעיה 4: Consumer Service לא נמצא

**סיבות אפשריות:**
- Consumer Service לא רץ
- Consumer Service עם שם אחר
- Consumer Service ב-namespace אחר

**פתרונות:**
1. לבדוק את כל ה-Pods ב-namespace
2. לבדוק deployments/services
3. לבדוק namespaces אחרים

---

## 📝 מסקנות

הסקריפט מספק תמונה מלאה של מה קורה:
- ✅ Backend Logs - מה Backend רואה
- ✅ MongoDB - האם Job/Consumer נרשמו
- ✅ Consumer Service - האם הוא רץ
- ✅ K8s Pods - האם Pods נוצרו ומה ה-Labels שלהם

**המלצות:**
1. להריץ את הסקריפט אחרי כל כשל של Consumer creation
2. לשמור את התוצאות לניתוח
3. להשתמש בתוצאות כדי לתקן את הבעיה

---

**מחבר:** AI Assistant  
**תאריך:** 2025-11-13

