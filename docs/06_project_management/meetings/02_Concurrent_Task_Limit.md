# טסט 2: Performance – Concurrent Task Limit
## PZ-13896 - ניתוח מקיף ומעמיק

---

## 📋 תקציר מהיר לפגישה (Quick Brief)

| **שדה** | **ערך** |
|---------|---------|
| **Jira ID** | PZ-13896 |
| **שם הטסט** | Performance – Concurrent Task Limit |
| **עדיפות** | 🔴 **HIGH** |
| **סוג** | Performance / Load Test / Stress Test |
| **סטטוס אוטומציה** | ✅ **Automated** |
| **משך ריצה צפוי** | ~2-5 דקות |
| **מורכבות מימוש** | 🟠 **גבוהה** |
| **קובץ טסט** | `tests/integration/performance/test_performance_high_priority.py` |
| **Test Class** | `TestConcurrentTaskLimit` |
| **שורות** | 198-421 |
| **תלויות** | Focus Server API, MongoDB, RabbitMQ, ThreadPoolExecutor |

---

## 🎯 מה המטרה של הטסט? (Test Objectives)

### מטרה אסטרטגית (Strategic Goal):
לקבוע **כמה משימות (tasks) במקביל** המערכת יכולה לטפל באופן אמין **מבלי להתדרדר, לקרוס או לתת שגיאות**.

### מטרות ספציפיות (Specific Goals):
1. **קביעת קיבולת מקסימלית** (Capacity Planning)
   - כמה concurrent tasks המערכת תומכת בהצלחה של 90%+?
   - כמה concurrent tasks המערכת תומכת בהצלחה של 80%+?
   - מה נקודת השבירה (breaking point)?

2. **וידוא התנהגות graceful degradation**
   - כשחוצים את הגבול → המערכת לא קורסת
   - שגיאות ברורות: "System at capacity"
   - לא exhaustion של משאבים

3. **זיהוי bottlenecks**
   - מה המשאב המגביל: CPU? Memory? MongoDB connections? RabbitMQ queues?

4. **תיעוד לתכנון קיבולת**
   - כמה משתמשים יכולים לעבוד במקביל?
   - האם צריך scaling?

---

## 🧪 מה אני רוצה לבדוק? (What We're Testing)

### הסצנריו שאנחנו בודקים:

**Scenario 1**: מספר משתמשים יוצרים tasks **בו-זמנית** (concurrently).

#### מה זה Concurrent Tasks?

**דוגמה פשוטה**:
```
Time: 10:00:00 - User A creates Task 1
Time: 10:00:00 - User B creates Task 2 (same second!)
Time: 10:00:01 - User C creates Task 3
Time: 10:00:01 - User D creates Task 4
Time: 10:00:01 - User E creates Task 5 (all at the same second!)

Total: 5 concurrent tasks within 1-2 seconds
```

**למה זה קורה בייצור?**
- 10 אנשים פותחים את האפליקציה **בו-זמנית** (morning rush)
- Automated scripts שרצים בלולאה
- Load balancer שמפזר בקשות ממשתמשים רבים

---

### תרחישי הבדיקה:

הטסט בודק **5 רמות** של concurrency:

| Level | Concurrent Tasks | Goal | Expected Success Rate |
|-------|-----------------|------|---------------------|
| **Level 1** | 10 tasks | Baseline capacity | ≥ 90% |
| **Level 2** | 20 tasks | Normal load | ≥ 90% |
| **Level 3** | 30 tasks | High load | ≥ 80% |
| **Level 4** | 40 tasks | Near breaking point | ≥ 70% (optional) |
| **Level 5** | 50 tasks | Stress test | Find breaking point |

**אם success rate < 80% → עצרנו (למדנו את הגבול!)**

---

## 🔥 מה הנחיצות של הטסט? (Why Is This Critical?)

### סיכונים אם לא בודקים:

#### 1️⃣ **קריסה מסיבית בייצור** (Production Outage)
**תרחיש**:  
50 משתמשים נכנסים בו-זמנית (09:00 AM - start of workday).  
המערכת לא מוכנה ל-50 concurrent tasks → **קריסה מוחלטת**!

**השפעה**:
- כל המשתמשים רואים errors
- המערכת לא מגיבה
- Pods ב-Kubernetes מתים ו-restarts
- אובדן אמון של המשתמשים

---

#### 2️⃣ **Resource Exhaustion** (ממ exhaustion של משאבים)
**תרחיש**:  
כל task פותח:
- 1 MongoDB connection
- 1 RabbitMQ channel
- X MB memory
- Y% CPU

אם 100 tasks במקביל → **MongoDB connection pool מתמלא** → בקשות חדשות נכשלות!

**תוצאה**:
- "Too many connections" errors
- Database lockups
- Memory leaks
- System becomes unresponsive

---

#### 3️⃣ **Uneven Load Distribution** (חלוקת עומס לא שווה)
**תרחיש**:  
המערכת מטפלת ב-5 concurrent tasks בקלות, אבל ב-11 tasks → failure.

**למה?**  
כי יש **connection pool limit** של 10 connections!

**תוצאה**: לא ידענו על הגבול → surprise בייצור!

---

#### 4️⃣ **Cascading Failures** (כשלים מתפשטים)
**תרחיש**:  
20 concurrent tasks → MongoDB עמוס → slow queries → RabbitMQ timeouts → Redis cache misses → **אפקט דומינו**!

**תוצאה**: כל המערכת קורסת, לא רק ה-API.

---

## 🛠️ איך אני ממש אותו בקוד? (Code Implementation)

### קובץ הטסט:
**Path**: `tests/integration/performance/test_performance_high_priority.py`  
**Test Class**: `TestConcurrentTaskLimit`  
**Lines**: 198-421

---

### מבנה המחלקה:

```python
@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.critical
@pytest.mark.slow
class TestConcurrentTaskLimit:
    """
    Test suite for PZ-13896: Performance – Concurrent Task Limit
    Priority: HIGH
    
    Validates system behavior under concurrent task load and determines
    maximum supported concurrent tasks.
    
    This class contains 3 test methods:
    1. test_concurrent_task_creation - Create tasks concurrently
    2. test_concurrent_task_polling - Poll tasks concurrently
    3. test_concurrent_task_max_limit - Find maximum capacity
    """
```

---

### טסט 1: `test_concurrent_task_creation`

**מטרה**: ליצור 20 tasks במקביל ולוודא success rate ≥ 90%.

#### קוד מלא עם הסברים:

```python
def test_concurrent_task_creation(self, focus_server_api, performance_config_payload):
    """
    Test PZ-13896.1: Create multiple concurrent tasks.
    
    Steps:
        1. Create 20 tasks concurrently using ThreadPoolExecutor
        2. Measure success rate
        3. Verify system stability
    
    Expected:
        - At least 90% success rate
        - System remains stable
        - No crashes or errors
    
    Jira: PZ-13896
    Priority: HIGH
    """
    logger.info("Test PZ-13896.1: Concurrent task creation")
    
    # =====================================================
    # Configuration
    # =====================================================
    num_concurrent = 20        # How many concurrent tasks to create
    max_workers = 10           # Thread pool size (parallel workers)
    
    logger.info(f"Creating {num_concurrent} tasks with {max_workers} workers...")
    
    # =====================================================
    # Define worker function
    # =====================================================
    def create_task(task_num: int) -> Dict[str, Any]:
        """
        Create a single task and return result.
        
        Args:
            task_num: Task number (for logging)
        
        Returns:
            Dictionary with:
            - job_id: Created job ID (or None if failed)
            - task_num: Task number
            - success: Boolean indicating success
            - latency_ms: Request latency in milliseconds
            - error: Error message (or None)
        
        Time Complexity: O(1) - single HTTP request
        Space Complexity: O(1) - constant memory
        """
        try:
            # Measure request start time
            start_time = time.perf_counter()
            
            # Create configuration request
            config_request = ConfigureRequest(**performance_config_payload)
            
            # Send POST /configure request to Focus Server
            response = focus_server_api.configure_streaming_job(config_request)
            
            # Measure request end time
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            # Check if request succeeded
            success = hasattr(response, 'job_id') and response.job_id is not None
            job_id = response.job_id if hasattr(response, 'job_id') else None
            
            return {
                'job_id': job_id,
                'task_num': task_num,
                'success': success,
                'latency_ms': latency_ms,
                'error': None
            }
            
        except Exception as e:
            # Request failed - log error
            logger.error(f"Task {task_num} failed: {e}")
            return {
                'job_id': None,
                'task_num': task_num,
                'success': False,
                'latency_ms': None,
                'error': str(e)
            }
    
    # =====================================================
    # Execute concurrent task creation
    # =====================================================
    results = []
    
    # ThreadPoolExecutor - runs tasks in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks to thread pool
        futures = [executor.submit(create_task, i) for i in range(num_concurrent)]
        
        # Wait for all tasks to complete (as_completed yields futures as they finish)
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            # Log each result
            if result['success']:
                logger.info(f"✅ Task {result['task_num']}: {result['latency_ms']:.2f}ms")
            else:
                logger.warning(f"❌ Task {result['task_num']}: Failed")
    
    # =====================================================
    # Analyze results
    # =====================================================
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    success_rate = len(successful) / num_concurrent
    
    logger.info("=" * 60)
    logger.info(f"Concurrent Task Creation Results:")
    logger.info(f"  Total tasks:      {num_concurrent}")
    logger.info(f"  Successful:       {len(successful)}")
    logger.info(f"  Failed:           {len(failed)}")
    logger.info(f"  Success rate:     {success_rate:.1%}")
    
    if successful:
        latencies = [r['latency_ms'] for r in successful]
        avg_latency = statistics.mean(latencies)
        max_latency = max(latencies)
        logger.info(f"  Avg latency:      {avg_latency:.2f}ms")
        logger.info(f"  Max latency:      {max_latency:.2f}ms")
    
    logger.info("=" * 60)
    
    # =====================================================
    # Assertions
    # =====================================================
    MIN_SUCCESS_RATE = 0.90  # 90% success rate required
    
    assert success_rate >= MIN_SUCCESS_RATE, \
        f"Success rate {success_rate:.1%} < threshold {MIN_SUCCESS_RATE:.1%}"
    
    logger.info(f"✅ Concurrent task creation: {success_rate:.1%} success rate")
```

---

### מה קורה פה? (Step-by-Step Explanation)

#### **שלב 1: הגדרת Configuration**
```python
num_concurrent = 20
max_workers = 10
```
- **num_concurrent**: כמה tasks ליצור (20)
- **max_workers**: כמה threads לרוץ במקביל (10)

**למה 10 workers ו-20 tasks?**
- 10 workers → 10 requests מקבילים ממש
- 20 tasks → כל worker יריץ 2 tasks
- זה מדמה **realistic concurrency** (לא extreme)

---

#### **שלב 2: פונקציה ליצירת Task בודד**
```python
def create_task(task_num: int) -> Dict[str, Any]:
```

הפונקציה הזו:
1. שולחת `POST /configure` ל-Focus Server
2. מודדת latency
3. מחזירה success/failure

**למה בצורה הזו?**
- כל thread מריץ את הפונקציה הזו
- ThreadPoolExecutor מנהל את ה-parallelism
- אנחנו רק מגדירים מה כל task עושה

---

#### **שלב 3: ThreadPoolExecutor**
```python
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(create_task, i) for i in range(num_concurrent)]
```

**מה זה `ThreadPoolExecutor`?**
- Python module מ-`concurrent.futures`
- מריץ פונקציות ב-**threads מקבילים**
- מספר threads = `max_workers`

**מה זה `futures`?**
- `future` = obje`ct שמייצג תוצאה עתידית
- כשה-thread מסיים → ה-future מתמלא בתוצאה

**למה `executor.submit`?**
- `submit(function, args)` → מוסיף task לתור
- ThreadPoolExecutor מריץ כל task כשיש worker פנוי

---

#### **שלב 4: המתנה לתוצאות**
```python
for future in as_completed(futures):
    result = future.result()
    results.append(result)
```

**מה זה `as_completed`?**
- Generator שמחזיר futures **כשהם מסיימים**
- לא מחכה לכולם → מחזיר בסדר שמסיימים
- יעיל יותר מאשר לחכות לסוף

**למה `future.result()`?**
- מחזיר את הערך שהפונקציה החזירה
- אם הייתה exception → זורק אותה

---

#### **שלב 5: ניתוח תוצאות**
```python
successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]
success_rate = len(successful) / num_concurrent
```

**מה מחשבים?**
- כמה tasks הצליחו
- כמה נכשלו
- מה ה-success rate (%)

**למה success rate חשוב?**
- 100% → מושלם, אבל לא realistic
- 90% → מצוין
- 80% → מקובל
- < 70% → בעיה!

---

### טסט 2: `test_concurrent_task_polling`

**מטרה**: ליצור 10 tasks ואז **לבדוק אותם במקביל** (polling).

#### למה זה חשוב?
- יצירת task ≠ שאילתת task
- אולי יצירה עובדת, אבל polling נכשל תחת עומס?

```python
def test_concurrent_task_polling(self, focus_server_api, performance_config_payload):
    """
    Test PZ-13896.2: Poll multiple tasks concurrently.
    
    Steps:
        1. Create 10 tasks
        2. Poll all tasks concurrently
        3. Verify all tasks can be polled
    
    Expected:
        - All tasks can be polled concurrently
        - No interference between tasks
    
    Jira: PZ-13896
    Priority: HIGH
    """
    logger.info("Test PZ-13896.2: Concurrent task polling")
    
    num_tasks = 10
    
    # =====================================================
    # Step 1: Create tasks first
    # =====================================================
    job_ids = []
    logger.info(f"Creating {num_tasks} tasks...")
    
    for i in range(num_tasks):
        config_request = ConfigureRequest(**performance_config_payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        if hasattr(response, 'job_id') and response.job_id:
            job_ids.append(response.job_id)
    
    # Verify we created enough tasks
    assert len(job_ids) >= num_tasks * 0.8, \
        f"Only {len(job_ids)}/{num_tasks} tasks created successfully"
    
    logger.info(f"{len(job_ids)} tasks created successfully")
    
    # =====================================================
    # Step 2: Test passes - tasks were created concurrently
    # =====================================================
    logger.info("=" * 60)
    logger.info(f"Concurrent Task Polling Test Results:")
    logger.info(f"  Tasks Created: {len(job_ids)}/{num_tasks}")
    logger.info("=" * 60)
    logger.info(f"✅ Concurrent task polling completed")
```

**הערה**: הטסט הזה כרגע **לא polling** בפועל (TODO: implement polling).  
הוא רק יוצר tasks ומוודא שהיצירה הצליחה.

---

### טסט 3: `test_concurrent_task_max_limit` (הכי חשוב!)

**מטרה**: למצוא את **נקודת השבירה** (breaking point).

```python
def test_concurrent_task_max_limit(self, focus_server_api, performance_config_payload):
    """
    Test PZ-13896.3: Find maximum concurrent task limit.
    
    Steps:
        1. Gradually increase concurrent task count (10, 20, 30, 40, 50)
        2. Find the point where tasks start failing
        3. Document maximum supported concurrent tasks
    
    Expected:
        - System supports at least [MIN] concurrent tasks
        - Graceful degradation when limit exceeded
    
    Jira: PZ-13896
    Priority: HIGH
    """
    logger.info("Test PZ-13896.3: Maximum concurrent task limit")
    
    # =====================================================
    # Test different concurrency levels
    # =====================================================
    test_counts = [10, 20, 30, 40, 50]
    results_by_count = {}
    
    for count in test_counts:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing {count} concurrent tasks...")
        logger.info(f"{'='*60}")
        
        # Define worker function
        def create_task(task_num: int) -> bool:
            try:
                config_request = ConfigureRequest(**performance_config_payload)
                response = focus_server_api.configure_streaming_job(config_request)
                return hasattr(response, 'job_id') and response.job_id is not None
            except:
                return False
        
        # Execute concurrent task creation
        with ThreadPoolExecutor(max_workers=min(count, 20)) as executor:
            futures = [executor.submit(create_task, i) for i in range(count)]
            outcomes = [f.result() for f in as_completed(futures)]
        
        # Calculate success rate
        success_count = sum(outcomes)
        success_rate = success_count / count
        
        results_by_count[count] = {
            'success_count': success_count,
            'success_rate': success_rate
        }
        
        logger.info(f"Result: {success_count}/{count} succeeded ({success_rate:.1%})")
        
        # =====================================================
        # Stop if success rate drops below 80%
        # =====================================================
        if success_rate < 0.80:
            logger.info(f"⚠️ Success rate dropped below 80% at {count} tasks")
            break
        
        # Small delay between test rounds
        time.sleep(2)
    
    # =====================================================
    # Report findings
    # =====================================================
    logger.info("\n" + "=" * 60)
    logger.info("Maximum Concurrent Task Limit - Summary:")
    logger.info("=" * 60)
    
    for count, result in results_by_count.items():
        logger.info(f"  {count:3d} tasks: {result['success_count']:3d} succeeded ({result['success_rate']:.1%})")
    
    logger.info("=" * 60)
    
    # =====================================================
    # Assertions
    # =====================================================
    MIN_CONCURRENT_TASKS = 10
    
    # Find highest count with >= 90% success rate
    max_with_90_percent = max(
        [count for count, result in results_by_count.items() if result['success_rate'] >= 0.90],
        default=0
    )
    
    assert max_with_90_percent >= MIN_CONCURRENT_TASKS, \
        f"System only supports {max_with_90_percent} concurrent tasks (minimum: {MIN_CONCURRENT_TASKS})"
    
    logger.info(f"✅ System supports at least {max_with_90_percent} concurrent tasks with 90%+ success")
```

---

### מה קורה בטסט הזה? (Detailed Walkthrough)

#### **שלב 1: מערך רמות Concurrency**
```python
test_counts = [10, 20, 30, 40, 50]
```
- מתחילים ב-10 (קל)
- מגדילים ל-20, 30, 40, 50 (הדרגתי)
- כל רמה בודקת יכולת גבוהה יותר

---

#### **שלב 2: לולאה על כל רמה**
```python
for count in test_counts:
```
- מריצים את הטסט עם `count` tasks במקביל
- מודדים success rate
- עוצרים אם success rate < 80%

---

#### **שלב 3: Worker Function פשוטה**
```python
def create_task(task_num: int) -> bool:
    try:
        # ... create task ...
        return True
    except:
        return False
```
- מחזירה רק `True/False` (לא dict מפורט)
- יותר פשוט ומהיר לניתוח

---

#### **שלב 4: ריצה עם ThreadPoolExecutor**
```python
with ThreadPoolExecutor(max_workers=min(count, 20)) as executor:
```
**למה `min(count, 20)`?**
- אם `count=10` → 10 workers
- אם `count=50` → 20 workers (לא 50!)
- למה? כדי לא ליצור **יותר מדי threads** (overhead)

---

#### **שלב 5: עצירה אם success rate נמוך**
```python
if success_rate < 0.80:
    logger.info(f"⚠️ Success rate dropped below 80% at {count} tasks")
    break
```
**למה 80%?**
- 80% = threshold למצב "לא מקובל"
- אם הגענו ל-80% → מצאנו את נקודת השבירה!
- אין טעם להמשיך (כבר ידוע שזה לא עובד טוב)

---

#### **שלב 6: דיווח ממצאים**
```python
logger.info("Maximum Concurrent Task Limit - Summary:")
for count, result in results_by_count.items():
    logger.info(f"  {count:3d} tasks: {result['success_count']:3d} succeeded ({result['success_rate']:.1%})")
```

**דוגמה לפלט**:
```
Maximum Concurrent Task Limit - Summary:
=============================================================
  10 tasks:  10 succeeded (100.0%)
  20 tasks:  19 succeeded (95.0%)
  30 tasks:  27 succeeded (90.0%)
  40 tasks:  32 succeeded (80.0%)
  50 tasks:  35 succeeded (70.0%) ⚠️ Stopped here
=============================================================
✅ System supports at least 30 concurrent tasks with 90%+ success
```

---

## 🎓 מה לומדים מהטסט הזה?

### תוצאות צפויות:
1. **10 concurrent tasks** → 100% success ✅ (baseline)
2. **20 concurrent tasks** → 95% success ✅ (good)
3. **30 concurrent tasks** → 90% success ✅ (acceptable)
4. **40 concurrent tasks** → 80% success ⚠️ (marginal)
5. **50 concurrent tasks** → 70% success 🚫 (breaking point)

**המסקנה**: המערכת תומכת ב-**30 concurrent tasks באופן אמין**.

---

### למה tasks נכשלים?

| Cause | Description | Solution |
|-------|-------------|----------|
| **MongoDB Connection Pool** | Max 10 connections → 11th task fails | Increase pool size |
| **RabbitMQ Channels** | Max 20 channels → 21st task fails | Increase channel limit |
| **CPU Saturation** | 100% CPU → slow responses → timeouts | Scale horizontally |
| **Memory Exhaustion** | OOM Killer → pods die | Increase memory limits |
| **Network Bandwidth** | Saturated → packet loss | Upgrade network |

---

## 🗣️ שאלות לפגישה (Questions for the Meeting)

### שאלות מדיניות:
1. **כמה משתמשים צפויים בייצור?**
   - 10? 50? 100? 1000?
   - מה תרחיש ה-peak usage?

2. **מה ה-SLA לקבלת concurrent requests?**
   - 90% success rate? 95%? 99%?

3. **מה קורה כשחורגים מהגבול?**
   - Error message: "System at capacity"?
   - Queueing?
   - Throttling?

4. **האם יש תכנון ל-scaling?**
   - Horizontal scaling (more pods)?
   - Vertical scaling (bigger pods)?

5. **מה timeout ל-tasks?**
   - 30 seconds? 60 seconds?
   - מה קורה לtasks שתקועים?

---

### שאלות טכניות:
6. **מה גודל connection pool של MongoDB?**
   - Default: 10? 50? 100?
   - מה קורה כשהוא מתמלא?

7. **מה גודל channel pool של RabbitMQ?**
   - כמה channels פתוחים במקביל?

8. **מה ה-resource limits ב-Kubernetes?**
   - CPU: מקסימום כמה cores?
   - Memory: מקסימום כמה GB?

9. **האם יש rate limiting ב-API?**
   - כמה requests ל-second?
   - כמה requests ל-minute?

10. **איך מבצעים load balancing?**
    - Round-robin?
    - Least connections?
    - IP hash?

---

## 📊 טבלת סיכום - Concurrent Task Scenarios

| Scenario | Concurrent Tasks | Expected Success Rate | System State |
|----------|-----------------|---------------------|--------------|
| **Low Load** | 10 | 100% | ✅ Normal |
| **Normal Load** | 20 | 95% | ✅ Good |
| **High Load** | 30 | 90% | ✅ Acceptable |
| **Near Capacity** | 40 | 80% | ⚠️ Warning |
| **Over Capacity** | 50+ | < 80% | 🚫 Degraded |

---

## ✅ Checklist לפני הפגישה

- [ ] קראתי את המסמך הזה לעומק
- [ ] הבנתי מה זה concurrent tasks ואיך זה שונה מ-sequential
- [ ] הבנתי איך ThreadPoolExecutor עובד
- [ ] יודע להסביר את ההבדל בין 3 הטסטים
- [ ] יודע מה ה-bottlenecks הצפויים
- [ ] הכנתי שאלות ספציפיות על connection pools
- [ ] סקרתי את הקוד ב-`test_performance_high_priority.py`
- [ ] יודע מה success rate נחשב מקובל

---

## 📌 נקודות מפתח לזכור

1. **Concurrency ≠ Parallelism** (אבל קרוב!)
2. **ThreadPoolExecutor** מנהל threads בצורה יעילה
3. **Success rate 90% = מצוין, 80% = מקובל, < 70% = בעיה**
4. **Breaking point = נקודה שבה success rate יורד מתחת ל-80%**
5. **הטסט הזה מגלה bottlenecks לפני שהם קורים בייצור!**

---

**נכתב עבור**: Roy Avrahami  
**תאריך**: אוקטובר 2025  
**Jira**: PZ-13896

---

