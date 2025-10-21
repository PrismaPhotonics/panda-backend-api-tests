# 📋 Specifications Requirements for Automation Testing
## רשימת דרישות לפגישה עם ראש צוות הפיתוח ומנהל האתר

**תאריך:** 2025-10-21  
**מטרה:** הגדרת קריטריונים ברורים להצלחה/כישלון בבדיקות אוטומציה  
**משתתפים נדרשים:** ראש צוות פיתוח, מנהל אתר, QA Lead  

---

## 🎯 **1. Performance & SLA Requirements**

### 1.1 Response Time Thresholds
**❓ שאלות שצריכות תשובה:**

- [ ] **API Response Times:**
  - `POST /config/{task_id}` - מה ה-P95/P99 latency המקסימלי המקובל?
    - Currently: No threshold defined
    - Need: Specific values (e.g., P95 < 500ms, P99 < 1000ms)
  
  - `GET /waterfall/{task_id}/{row_count}` - מה זמן תגובה מקסימלי?
    - Live mode: ?
    - Historic mode: ?
  
  - `GET /metadata/{task_id}` - מה זמן תגובה מקסימלי?
    - Currently: No threshold defined
    - Need: Specific value
  
  - `GET /channels` - מה זמן תגובה מקסימלי?
    - Currently: No threshold defined
  
  - `GET /live_metadata` - מה זמן תגובה מקסימלי?
    - Currently: No threshold defined

- [ ] **End-to-End Flow Timings:**
  - מתחילת קונפיגורציה עד קבלת נתונים ראשונים - מה הזמן המקסימלי?
    - Live flow: ?
    - Historic flow: ?

- [ ] **Polling Intervals:**
  - מהו polling interval אופטימלי ל-waterfall?
  - מהו timeout מקסימלי להמתנה לנתונים?
  - כמה retries מותר לפני שנחשב failure?

### 1.2 Throughput & Capacity
**❓ שאלות שצריכות תשובה:**

- [ ] **Data Rates:**
  - מהו data rate מקסימלי צפוי (MB/sec)?
  - כמה rows per second אמורים להגיע במצב live?
  - מהו הגודל המקסימלי של waterfall response בודד?

- [ ] **Concurrent Users/Tasks:**
  - כמה tasks בו-זמניים המערכת צריכה לתמוך?
  - כמה users concurrent יכולים לעבוד במערכת?
  - מהו ה-limit על מספר baby analyzers פעילים?

- [ ] **Resource Limits:**
  - מהו CPU utilization מקסימלי מקובל? (e.g., < 80%)
  - מהו Memory utilization מקסימלי מקובל? (e.g., < 85%)
  - מהו Disk I/O threshold מקסימלי?

---

## 📊 **2. Data Quality & Accuracy Specs**

### 2.1 Waterfall Data Validation
**❓ שאלות שצריכות תשובה:**

- [ ] **Amplitude Ranges:**
  - מהו ה-range הצפוי של `current_min_amp` / `current_max_amp`?
  - מהם ערכי outliers שצריך להתריע עליהם?
  - מהו noise floor מקובל?

- [ ] **Data Completeness:**
  - כמה אחוז missing data מותר? (e.g., < 5%)
  - מהו gap מקסימלי מקובל בין rows (timestamps)?
  - כמה sensors ריקים מותר בשורה אחת?

- [ ] **Data Consistency:**
  - מהו acceptable drift בין timestamps?
  - האם צפויים duplicates? אם כן - כמה מותר?
  - מהו ה-tolerance לסטיות בין metadata למידע בפועל?

### 2.2 Sensor & Frequency Configuration
**❓ שאלות שצריכות תשובה:**

- [ ] **Sensor Ranges (ROI):**
  - מהו מספר sensors מקסימלי במערכת?
  - מהו sensor range מינימלי חוקי? (e.g., min 10 sensors)
  - מהו sensor range מקסימלי חוקי? (e.g., max 1000 sensors)
  - מהו acceptable overlap בין ROI שונים?

- [ ] **Frequency Ranges:**
  - מהו frequency range מינימלי חוקי?
  - מהו frequency range מקסימלי חוקי?
  - מהו PRR (Pulse Repetition Rate) min/max?
  - מהו Nyquist frequency enforcement? (צריך hard limit או warning?)

- [ ] **NFFT Values:**
  - אילו ערכי NFFT חוקיים? (e.g., 256, 512, 1024, 2048)
  - האם חובה power of 2? או רק recommended?
  - מהו NFFT מקסימלי מקובל?

- [ ] **Canvas & Display:**
  - מהו canvas_height min/max?
  - מהו resolution מינימלי/מקסימלי?

### 2.3 ROI Dynamic Adjustment
**❓ שאלות שצריכות תשובה:**

- [ ] **ROI Change Limits:**
  - מהו % שינוי מקסימלי מותר ב-ROI בפעולה אחת?
    - Currently: 50% (hardcoded in validator)
    - Need confirmation: Is this correct?
  
  - מהו shift מקסימלי מותר (במספר sensors)?
  
  - כמה שינויי ROI מותרים בדקה?
  
  - האם יש cooldown period בין שינויי ROI?

- [ ] **ROI Validation:**
  - מתי שינוי ROI נחשב "unsafe"?
  - האם צריך להתריע או לחסום שינויים גדולים?
  - מהי ההשפעה על live monitoring כשמשנים ROI?

---

## 🔌 **3. Infrastructure & Integration Specs**

### 3.1 MongoDB
**❓ שאלות שצריכות תשובה:**

- [ ] **Connection & Availability:**
  - מהו timeout מקסימלי לחיבור MongoDB?
  - כמה retries מותרים?
  - מהו recovery time מקסימלי אחרי outage?
  - האם צריך failover automatic?

- [ ] **Query Performance:**
  - מהו query latency מקסימלי מקובל?
  - מהו acceptable index scan ratio?
  - כמה documents מקסימלי בתוצאה אחת?

- [ ] **Data Lifecycle:**
  - מתי recording נחשב "live" vs "historical"?
    - Currently: 1 hour threshold (is this correct?)
  
  - מה הזמן המקסימלי שrecording יכול להיות "orphaned"?
  
  - מהו retention policy לrecordings?

### 3.2 RabbitMQ
**❓ שאלות שצריכות תשובה:**

- [ ] **Message Delivery:**
  - מהו timeout מקסימלי לשליחת command?
  - כמה retries אם ההודעה נכשלת?
  - האם צריך acknowledgment חובה?
  - מהו TTL (Time To Live) להודעות?

- [ ] **Queue Management:**
  - מהו max queue size מקובל?
  - מה קורה כש-queue מתמלא?
  - האם צריך Dead Letter Queue?

- [ ] **Commands:**
  - מהו timeout מקסימלי לביצוע `RegionOfInterestCommand`?
  - מהו timeout לביצוע `PauseCommand` / `ResumeCommand`?
  - האם יש priority levels בין commands?

### 3.3 Kubernetes & Orchestration
**❓ שאלות שצריכות תשובה:**

- [ ] **Pod Health:**
  - מהם הקריטריונים ל-healthy pod?
  - מהו acceptable restart count?
  - מהו grace period לפני שמחליפים pod?

- [ ] **Service Availability:**
  - מהו uptime SLA? (e.g., 99.9%)
  - מהו acceptable downtime לעדכונים?
  - מהי אסטרטגיית rollback?

- [ ] **Resource Limits:**
  - מהם ה-requests/limits המומלצים לכל pod?
  - מהו threshold ל-OOM (Out of Memory)?
  - מתי צריך scaling אוטומטי?

---

## 🚨 **4. Error Handling & Edge Cases**

### 4.1 HTTP Status Codes
**❓ שאלות שצריכות תשובה:**

- [ ] **Status Code Semantics:**
  - `200` - No data yet: מה הזמן המקסימלי שמותר לקבל 200 לפני timeout?
  - `201` - Data available: האם תמיד חייב להיות data?
  - `208` - Already reported (historic complete): האם זה success או warning?
  - `400` - Bad request: מה הפורמט של error messages?
  - `404` - Not found: מתי task_id נחשב "not found"?
  - `503` - Service unavailable: מהו recovery time צפוי?

### 4.2 Invalid Configurations
**❓ שאלות שצריכות תשובה:**

- [ ] **Input Validation:**
  - האם API צריך לדחות invalid configs או לתקן אוטומטית?
  - מה קורה עם out-of-range values? (reject או clamp?)
  - האם צריך detailed validation errors או generic message?

- [ ] **Time Range Issues:**
  - מה קורה אם start_time > end_time?
  - מה קורה אם הזמן בעתיד?
  - מה קורה אם הזמן רחוק מדי בעבר (data expired)?
  - מהו time range מקסימלי מותר לhistoric playback?

- [ ] **Task Lifecycle:**
  - האם task_id חייב להיות unique?
  - מה קורה אם שולחים config פעמיים לאותו task_id?
  - מהו timeout לtask לפני שהוא נמחק?
  - האם יש cleanup אוטומטי לtasks ישנים?

### 4.3 Network & Infrastructure Failures
**❓ שאלות שצריכות תשובה:**

- [ ] **MongoDB Outage:**
  - מה הסטטוס הצפוי של API כשMongoDB down?
  - האם צריך להמשיך לקבל live data?
  - האם צריך caching זמני?

- [ ] **RabbitMQ Outage:**
  - מה קורה לcommands שנשלחו כשRabbitMQ down?
  - האם צריך queue local?
  - מה ה-fallback strategy?

- [ ] **Baby Analyzer Crashes:**
  - מהו expected behavior כשBaby Analyzer קורס?
  - מהו recovery time מקסימלי?
  - האם צריך להתריע למשתמש?

---

## 📦 **5. SingleChannel View Specs**

**❓ שאלות שצריכות תשובה:**

- [ ] **Channel Mapping:**
  - מהו channel range חוקי?
  - האם channel_id חייב להיות בתוך sensor range?
  - מה קורה אם channel לא קיים?

- [ ] **Display Mapping:**
  - מהם הערכים החוקיים של `display_sensor_id`?
  - מהו acceptable offset?
  - האם יכולים להיות כמה channels על אותו display sensor?

---

## 🧪 **6. Test Execution Criteria**

### 6.1 Load Testing
**❓ שאלות שצריכות תשובה:**

- [ ] **Load Profiles:**
  - מהו steady state load? (concurrent users)
  - מהו peak load? (spike scenario)
  - מהו ramp-up rate מקובל?
  - מהו acceptable degradation under load?

- [ ] **Stress Testing:**
  - מהו breaking point צפוי?
  - האם יש graceful degradation?
  - מהם הסימנים להתראה מוקדמת?

### 6.2 Soak Testing
**❓ שאלות שצריכות תשובה:**

- [ ] **Long-Running Stability:**
  - כמה זמן task צריך לרוץ ללא בעיות? (e.g., 24 hours)
  - מהו acceptable memory leak? (e.g., < 1% per hour)
  - מהו acceptable CPU drift?

### 6.3 Security Testing
**❓ שאלות שצריכות תשובה:**

- [ ] **Authentication & Authorization:**
  - האם יש authentication נדרש?
  - מהם ה-roles השונים?
  - מהן ההרשאות לכל endpoint?

- [ ] **Input Sanitization:**
  - אילו injection attacks צריך לבדוק?
  - מהו max input size מקובל?
  - האם צריך rate limiting?

---

## 📝 **7. Logging & Monitoring Requirements**

**❓ שאלות שצריכות תשובה:**

- [ ] **Log Levels:**
  - מתי צריך ERROR vs WARNING?
  - מה צריך להופיע ב-INFO?
  - מה הפורמט של log messages?

- [ ] **Metrics Collection:**
  - אילו metrics חיוניים לצורך monitoring?
  - מהו sampling rate?
  - מהו retention period ל-metrics?

- [ ] **Alerting:**
  - מהם הthresholds להתראות?
  - למי שולחים alerts?
  - מהו escalation policy?

---

## 🎬 **8. Business Logic & Domain Rules**

**❓ שאלות שצריכות תשובה:**

- [ ] **Fiber Optics:**
  - מהו fiber_length_meters מינימלי/מקסימלי חוקי?
  - מהו dx (spatial resolution) מינימלי/מקסימלי?
  - מהו fiber_start_meters חוקי?
  - מהם הקריטריונים לvalid fiber geometry?

- [ ] **Recording Metadata:**
  - אילו שדות חובה ב-metadata?
  - מהם ערכי default מקובלים?
  - מהי ה-validation logic לכל שדה?

- [ ] **Data Processing:**
  - מהי decimation strategy?
  - מהי compression strategy?
  - האם יש data transformation rules?

---

## 📋 **9. Acceptance Criteria - Summary**

### 9.1 Performance
- [ ] All API endpoints respond within defined SLA
- [ ] System handles defined concurrent load
- [ ] No memory leaks over 24 hours
- [ ] Resource utilization within limits

### 9.2 Functionality
- [ ] All happy path flows complete successfully
- [ ] Invalid inputs rejected with proper errors
- [ ] Edge cases handled gracefully
- [ ] Data integrity maintained

### 9.3 Reliability
- [ ] MongoDB outage handled correctly
- [ ] RabbitMQ outage handled correctly
- [ ] Baby Analyzer crashes recover automatically
- [ ] No data loss under failure scenarios

### 9.4 Security
- [ ] Authentication enforced
- [ ] Authorization checked
- [ ] Input sanitization works
- [ ] No sensitive data in logs

---

## 📞 **10. Action Items for Meeting**

### Before Meeting:
- [ ] Send this document to all participants
- [ ] Prepare current test results
- [ ] Gather existing monitoring data
- [ ] Document current "gut feeling" thresholds

### During Meeting:
- [ ] Go through each section systematically
- [ ] Document answers in this file
- [ ] Identify items that need research
- [ ] Assign owners for follow-up

### After Meeting:
- [ ] Update automation framework with new specs
- [ ] Create Jira tickets for missing tests
- [ ] Update test assertions with thresholds
- [ ] Schedule follow-up review in 2 weeks

---

## 📎 **Appendix: Current Gaps Summary**

### Critical Gaps:
1. **No performance SLA defined** - All response times are untested
2. **No data quality thresholds** - Can't distinguish good vs bad data
3. **No resource limits** - Don't know when to scale
4. **No error handling specs** - Each failure is ad-hoc
5. **No load testing criteria** - Don't know system capacity

### High Priority:
- API response time thresholds
- Data validation ranges (amplitude, sensors, frequency)
- MongoDB/RabbitMQ outage behavior
- ROI change limits
- Task lifecycle rules

### Medium Priority:
- Security requirements
- Logging standards
- Monitoring metrics
- Load testing profiles

### Low Priority:
- Soak testing duration
- UI/UX preferences
- Documentation standards

---

**📌 Next Steps:**
1. Schedule meeting with all stakeholders
2. Send this document 48 hours before meeting
3. During meeting: Fill in all "?" marks with actual values
4. After meeting: Update automation framework accordingly
5. Re-run all tests with new thresholds
6. Document pass/fail criteria in Xray

---

**Document Owner:** QA Lead  
**Last Updated:** 2025-10-21  
**Status:** Draft - Pending Review


