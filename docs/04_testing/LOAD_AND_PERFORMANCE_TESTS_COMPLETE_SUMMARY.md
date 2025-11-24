# Load and Performance Tests - סיכום מלא 📊

**תאריך:** 23 בנובמבר 2025  
**Workflow:** `.github/workflows/load-performance.yml`  
**Markers:** `@pytest.mark.load` או `@pytest.mark.performance`

---

## 🎯 סקירה כללית

הטסטים האלה רצים באופן אוטומטי **כל לילה בשעה 02:00 UTC** או באופן ידני דרך GitHub Actions.

**קריטריון בחירה:**
```bash
pytest be_focus_server_tests/ -m "load or performance"
```

---

## 📁 קטגוריות טסטים

### **1. Alert Generation - Load Tests** 🚨
**קובץ:** `be_focus_server_tests/integration/alerts/test_alert_generation_load.py`

#### **PZ-14953: High Volume Load**
- **מטרה:** בדיקת יכולת המערכת לטפל בנפח גבוה של alerts
- **פרמטרים:**
  - 1000 alerts
  - זמן מקסימלי: 5 דקות
  - Success rate מינימלי: 99%
- **טכניקות מיוחדות:**
  - Smart backoff: אחרי 5 שגיאות 429 רצופות → הפסקה של 10 שניות
  - Retry logic: 5 ניסיונות עם exponential backoff (0.5s, 1s, 2s, 4s, 8s)
  - Delay: 100ms כל 10 alerts
- **מדידות:**
  - זמן עיבוד כולל
  - Success rate
  - Failure count

#### **PZ-14954: Sustained Load**
- **מטרה:** וידוא שהמערכת יכולה לעמוד בעומס מתמשך לאורך זמן
- **פרמטרים:**
  - משך: 10 דקות
  - קצב: 10 alerts לשנייה
  - Success rate מינימלי: 90%
- **טכניקות מיוחדות:**
  - Smart backoff: אחרי 5 שגיאות 429 רצופות → הפסקה של 10 שניות
  - 50ms delay בין requests בודדים
  - 0.5s delay בין batches
- **מדידות:**
  - זמן ריצה כולל
  - מספר alerts שנשלחו
  - Rate בפועל (alerts/sec)

#### **PZ-14955: Burst Load**
- **מטרה:** בדיקת יכולת המערכת לטפל בפרצי עומס פתאומיים
- **פרמטרים:**
  - 3 bursts של 100 alerts כל אחד
  - Success rate מינימלי: 95%
- **מדידות:**
  - זמן עיבוד לכל burst
  - Success rate לכל burst

#### **PZ-14956: Mixed Alert Types Load**
- **מטרה:** בדיקת טיפול בסוגים שונים של alerts במקביל
- **פרמטרים:**
  - 500 alerts מסוגים שונים (SC/SD)
  - סוגי severity שונים (1, 2, 3)
  - טווחי distance שונים
- **מדידות:**
  - Success rate לכל סוג alert
  - זמן עיבוד ממוצע לכל סוג

#### **PZ-14957: RabbitMQ Queue Capacity**
- **מטרה:** בדיקת יכולת התור של RabbitMQ לטפל בנפח גבוה
- **פרמטרים:**
  - 1000 messages ישירות ל-RabbitMQ
  - Success rate מינימלי: 95%
- **דורש:** `pika` library
- **מדידות:**
  - מספר messages שפורסמו בהצלחה
  - זמן עיבוד כולל

---

### **2. Alert Generation - Performance Tests** ⚡
**קובץ:** `be_focus_server_tests/integration/alerts/test_alert_generation_performance.py`

#### **PZ-14958: Response Time**
- **מטרה:** מדידת זמני תגובה של API
- **פרמטרים:**
  - 100 requests
  - Target: < 200ms ממוצע
  - P95: < 300ms
  - P99: < 500ms
- **מדידות:**
  - Min, Max, Avg, P50, P95, P99 response times

#### **PZ-14959: Throughput**
- **מטרה:** מדידת throughput מקסימלי
- **פרמטרים:**
  - משך: 5 דקות
  - Target: 10 alerts/sec
- **מדידות:**
  - Actual throughput
  - Success rate
  - Average response time

#### **PZ-14960: Latency**
- **מטרה:** מדידת latency end-to-end
- **פרמטרים:**
  - 50 alerts
  - מדידה מ-API call עד קבלת אישור
- **מדידות:**
  - Average latency
  - P95 latency
  - P99 latency

#### **PZ-14961: Resource Usage**
- **מטרה:** מוניטור על שימוש במשאבים
- **פרמטרים:**
  - משך: 3 דקות
  - מדידה של CPU, Memory, Network
- **דורש:** `psutil` library
- **מדידות:**
  - CPU usage %
  - Memory usage MB
  - Network bytes sent/received

#### **PZ-14962: End-to-End Performance**
- **מטרה:** בדיקת ביצועים מקצה לקצה
- **פרמטרים:**
  - שליחת alert → RabbitMQ → עיבוד → אחסון
  - Target: < 1 second end-to-end
- **מדידות:**
  - Time to RabbitMQ
  - Processing time
  - Total end-to-end time

#### **PZ-14963: RabbitMQ Performance**
- **מטרה:** בדיקת ביצועי RabbitMQ
- **פרמטרים:**
  - 1000 messages
  - מדידת throughput של RabbitMQ
- **דורש:** `pika` library
- **מדידות:**
  - Messages/sec
  - Average publish time
  - Queue depth

---

### **3. Focus Server API - Load Tests** 🔥
**תיקייה:** `be_focus_server_tests/integration/load/`

#### **PZ-14800: Concurrent Job Creation Load**
**קובץ:** `test_concurrent_load.py`
- **מטרה:** בדיקת יצירת jobs מקבילית
- **פרמטרים:**
  - 20 concurrent jobs
  - Max response time: 10 seconds
  - Success rate מינימלי: 80%
- **טכניקה:** ThreadPoolExecutor
- **מדידות:**
  - Success rate
  - Average response time
  - Max response time
  - Cleanup time

#### **PZ-14801: Sustained Load - 1 Hour**
**קובץ:** `test_sustained_load.py`
- **מטרה:** בדיקת עומס מתמשך למשך שעה (בCI: 5 דקות)
- **פרמטרים:**
  - משך: 5 דקות (CI) / 60 דקות (manual)
  - מרווח: 10 שניות בין requests
  - Success rate מינימלי: 90%
- **מדידות:**
  - Total requests
  - Success rate
  - Average response time
  - Max response time

#### **PZ-14802: Peak Load - High RPS**
**קובץ:** `test_peak_load.py`
- **מטרה:** בדיקת RPS גבוה
- **פרמטרים:**
  - משך: 60 שניות
  - Target RPS: 10
  - Total requests: 600
  - Success rate מינימלי: 85%
- **טכניקה:** ThreadPoolExecutor
- **מדידות:**
  - Actual RPS
  - Success rate
  - Average response time
  - Max response time

#### **PZ-14803: Ramp-Up Load Profile**
**קובץ:** `test_load_profiles.py`
- **מטרה:** בדיקת עלייה הדרגתית בעומס
- **פרמטרים:**
  - משך: 2 דקות
  - RPS התחלתי: 1
  - RPS מקסימלי: 10
  - Steps: 10
  - Success rate מינימלי: 85%
- **מדידות:**
  - Success rate לכל step
  - Response times לכל step

#### **PZ-14804: Spike Load Profile**
**קובץ:** `test_load_profiles.py`
- **מטרה:** בדיקת spike פתאומי בעומס
- **פרמטרים:**
  - Normal load: 2 RPS למשך 30 שניות
  - Spike load: 20 RPS למשך 10 שניות
  - Success rate מינימלי: 80%
- **טכניקה:** Sequential → ThreadPoolExecutor (spike)
- **מדידות:**
  - Success rate בכל phase
  - Response times בכל phase

#### **PZ-14805: Steady-State Load Profile**
**קובץ:** `test_load_profiles.py`
- **מטרה:** בדיקת עומס קבוע לאורך זמן
- **פרמטרים:**
  - RPS: 5
  - משך: 3 דקות
  - Success rate מינימלי: 90%
- **מדידות:**
  - Total requests
  - Success rate
  - Average response time

#### **PZ-14806: Recovery After Load**
**קובץ:** `test_recovery_and_exhaustion.py`
- **מטרה:** בדיקת התאוששות המערכת אחרי עומס גבוה
- **פרמטרים:**
  - Phase 1: High load (15 RPS למשך דקה)
  - Phase 2: Recovery (30 שניות המתנה)
  - Phase 3: Normal load (2 RPS למשך 30 שניות)
  - Recovery success rate מינימלי: 90%
  - Recovery avg time: < 5 seconds
- **מדידות:**
  - High load success rate
  - Recovery success rate
  - Recovery response times

#### **PZ-14807: Resource Exhaustion Under Load**
**קובץ:** `test_recovery_and_exhaustion.py`
- **מטרה:** בדיקת טיפול במצב של מיצוי משאבים
- **פרמטרים:**
  - Extreme load: 50 RPS למשך 30 שניות
  - זיהוי resource errors (503, 429, timeout)
- **מדידות:**
  - Total requests
  - Resource errors count
  - Cleanup time (< 60 seconds)
  - System health after recovery

---

### **4. Focus Server API - Performance Tests** 🎯
**קובץ:** `be_focus_server_tests/integration/performance/test_performance_high_priority.py`

#### **PZ-13770: /config Latency P95/P99**
- **מטרה:** מדידת latency של endpoint `/configure`
- **פרמטרים:**
  - 100 requests
  - P95 target: < 300ms
  - P99 target: < 500ms
  - Max error rate: 5%
- **מדידות:**
  - Min, P50, Avg, P95, P99, Max latency
  - Error rate

#### **PZ-13771: Concurrent Task Limit**

**Test 1: Concurrent Task Creation**
- **מטרה:** יצירת tasks מקבילית
- **פרמטרים:**
  - 20 concurrent tasks
  - 10 workers
  - Success rate מינימלי: 90%
- **מדידות:**
  - Success rate
  - Average latency
  - Max latency

**Test 2: Concurrent Task Polling**
- **מטרה:** polling של tasks מקבילי
- **פרמטרים:**
  - 10 tasks
  - Success rate מינימלי: 80%
- **מדידות:**
  - Tasks created successfully

**Test 3: Maximum Concurrent Task Limit**
- **מטרה:** מציאת הגבול המקסימלי של tasks מקבילים
- **פרמטרים:**
  - Test counts: [10, 20, 30, 40, 50]
  - Minimum: 10 concurrent tasks
  - Stop when success rate < 80%
- **מדידות:**
  - Success rate לכל count
  - Maximum reliable count

---

## 🔧 טכניקות ושיפורים

### **Smart Backoff (חדש!)**
```python
consecutive_429_errors = 0
max_consecutive_429 = 5

if consecutive_429_errors >= 5:
    logger.warning("Rate limited! Pausing for 10s...")
    time.sleep(10)
    consecutive_429_errors = 0
```

### **Retry Logic with Exponential Backoff**
```python
max_retries = 5
retry_delay = 0.5  # Initial delay

# Exponential backoff: 0.5s → 1s → 2s → 4s → 8s
wait_time = retry_delay * (2 ** attempt)
```

### **Rate Limiting**
```python
# Delay between individual requests
time.sleep(0.05)  # 50ms

# Delay every N alerts
if (i + 1) % 10 == 0:
    time.sleep(0.1)  # 100ms pause every 10 alerts
```

---

## 📊 סיכום סטטיסטי

### **מספר טסטים לפי קטגוריה:**
- **Alert Load:** 5 טסטים (PZ-14953 עד PZ-14957)
- **Alert Performance:** 6 טסטים (PZ-14958 עד PZ-14963)
- **API Load:** 8 טסטים (PZ-14800 עד PZ-14807)
- **API Performance:** 4 טסטים (PZ-13770, PZ-13771)

**סה"כ:** **23 טסטים**

### **משך ריצה משוער:**
- **Alert Tests:** ~30 דקות
- **Load Tests:** ~20 דקות
- **Performance Tests:** ~15 דקות

**סה"כ:** ~**65 דקות** (בתנאים אידיאליים)

---

## ⚙️ הגדרות Workflow

```yaml
# .github/workflows/load-performance.yml

# Run schedule
schedule:
  - cron: '0 2 * * *'  # כל לילה 02:00 UTC

# Environment
ENVIRONMENT: new_production
FOCUS_SERVER_HOST: 10.10.10.100
VERIFY_SSL: false

# Markers
pytest -m "load or performance"

# Exclusions
--ignore=be_focus_server_tests/ui  # UI tests דורשים playwright
```

---

## 📈 Thresholds ודרישות

### **Success Rates:**
- High volume/sustained: **99%**
- Burst/mixed: **95%**
- Concurrent/peak: **85-90%**
- Recovery: **90%**
- Spike: **80%**

### **Response Times:**
- Average: **< 300ms**
- P95: **< 300ms**
- P99: **< 500ms**

### **Throughput:**
- Target: **10 alerts/second**
- Minimum: **8 alerts/second** (80% of target)

---

## 🚀 הרצת הטסטים

### **Local:**
```bash
# All load tests
pytest be_focus_server_tests/ -m load -v

# All performance tests
pytest be_focus_server_tests/ -m performance -v

# Both
pytest be_focus_server_tests/ -m "load or performance" -v

# Specific test
pytest be_focus_server_tests/integration/alerts/test_alert_generation_load.py::TestAlertGenerationLoad::test_high_volume_load -v
```

### **GitHub Actions:**
1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר: "Load and Performance Tests"
3. לחץ: "Run workflow"
4. בחר branch: `chore/add-roy-tests`
5. לחץ: "Run workflow" ✅

---

## 📝 דרישות

### **Python Packages:**
- `pytest` >= 9.0.1
- `requests` >= 2.32.5
- `pika` (optional - for RabbitMQ tests)
- `psutil` (optional - for resource monitoring)

### **Infrastructure:**
- Access to Focus Server API
- Access to RabbitMQ (for queue tests)
- SSH access (for cleanup)
- Kubernetes access (for pod monitoring)

---

## 🎯 מטרות ו-KPIs

### **Reliability:**
- ✅ No system crashes under load
- ✅ Graceful degradation when overloaded
- ✅ Fast recovery after high load

### **Performance:**
- ✅ Meet response time SLAs
- ✅ Support required throughput
- ✅ Maintain performance under sustained load

### **Scalability:**
- ✅ Support concurrent operations
- ✅ Handle burst traffic
- ✅ Efficient resource usage

---

## 🔍 Troubleshooting

### **429 Errors:**
- ✅ **Fixed:** Smart backoff מזהה ועוצר אוטומטית
- ✅ **Fixed:** Retry logic עם exponential backoff
- ✅ **Fixed:** Rate limiting בין requests

### **Timeouts:**
- Check network connectivity
- Verify server is not overloaded
- Increase timeout values if needed

### **Resource Exhaustion:**
- Monitor pod resources
- Check cleanup is working
- Verify job cancellation

---

## 📧 Contact & Support

**Owner:** QA Automation Architect  
**Created:** 2025-11-13  
**Last Updated:** 2025-11-23  
**Status:** ✅ Active & Maintained

---

**זה המדריך המלא! 🎉**

