# 🔍 השוואת דופליקציות: Sustained Load Tests

**תאריך:** 2025-01-27  
**מטרה:** להשוות בין שני טסטים דומים ולקבוע איזה למחוק

---

## 📋 סיכום מהיר

| קריטריון | `test_api_sustained_load_1_hour` | `test_sustained_load_1_hour` |
|----------|----------------------------------|------------------------------|
| **מיקום** | `integration/load/test_sustained_load.py` | `load/test_job_capacity_limits.py` |
| **Xray Markers** | ✅ PZ-14801, PZ-14800 | ❌ אין |
| **מטרה** | API sustained load | Memory leak detection (soak test) |
| **גישה** | Sequential requests | Batch concurrent jobs |
| **משך זמן** | 5 דקות (CI) / שעה (manual) | שעה מלאה |
| **סטטוס** | ✅ פעיל | ⚠️ Skipped (manual only) |
| **המלצה** | ✅ **לשמור** | ❌ **למחוק** |

---

## 🔬 ניתוח מפורט

### 1. `test_api_sustained_load_1_hour` (לשמור)

**מיקום:** `be_focus_server_tests/integration/load/test_sustained_load.py`

**מאפיינים:**
- ✅ **יש Xray markers:** PZ-14801, PZ-14800
- ✅ **מטרה ברורה:** לבדוק שהמערכת יכולה להתמודד עם עומס מתמשך על ה-API
- ✅ **גישה:** שולח requests רציפים כל 10 שניות
- ✅ **בודק:** Success rate, response times
- ✅ **מבצע cleanup:** מבטל את כל ה-jobs שנוצרו
- ✅ **פעיל:** רץ ב-CI (5 דקות) או manual (שעה)

**קוד:**
```python
@pytest.mark.xray("PZ-14801")
@pytest.mark.xray("PZ-14800")
def test_api_sustained_load_1_hour(self, focus_server_api: FocusServerAPI):
    """
    Test PZ-14801: Load - Sustained Load - 1 Hour.
    
    Objective:
        Verify that API can handle sustained load over an extended period
        (1 hour) without degradation or failures.
    """
    test_duration = 300  # 5 minutes for CI (3600 seconds = 1 hour for manual)
    request_interval = 10  # 10 seconds between requests
    
    # Sends sequential requests every 10 seconds
    while time.time() < end_time:
        response = focus_server_api.configure_streaming_job(config_request)
        # ... track results ...
    
    # Cleanup all jobs
    for job_id in job_ids:
        focus_server_api.cancel_job(job_id)
    
    assert success_rate >= 0.9
```

**יתרונות:**
- ✅ מקושר ל-Xray (PZ-14801, PZ-14800)
- ✅ בודק API performance באופן ישיר
- ✅ רץ ב-CI (5 דקות) וגם manual (שעה)
- ✅ מבצע cleanup אוטומטי
- ✅ ממוקד ב-API behavior

---

### 2. `test_sustained_load_1_hour` (למחוק)

**מיקום:** `be_focus_server_tests/load/test_job_capacity_limits.py`

**מאפיינים:**
- ❌ **אין Xray markers**
- ⚠️ **מטרה:** לבדוק memory leaks (soak test)
- ⚠️ **גישה:** יוצר 10 jobs כל 60 שניות במשך שעה
- ⚠️ **בודק:** Success rate, CPU, memory trends
- ⚠️ **מסומן כ-skip:** `@pytest.mark.skip(reason="Very long test - run manually")`
- ⚠️ **לא רץ ב-CI:** רק manual

**קוד:**
```python
@pytest.mark.slow
@pytest.mark.skip(reason="Very long test - run manually")
class TestSustainedLoad:
    """Sustained load test - soak test."""
    
    def test_sustained_load_1_hour(self, focus_server_api, standard_config_payload):
        """
        Sustained load test: 10 jobs for 1 hour.
        
        Goal: Detect memory leaks or resource leaks.
        """
        duration_seconds = 3600  # 1 hour
        num_jobs = MEDIUM_LOAD_JOBS  # 10 jobs
        interval_seconds = 60  # Create jobs every 60 seconds
        
        while (datetime.now() - start_time).total_seconds() < duration_seconds:
            job_metrics, system_metrics = create_concurrent_jobs(
                focus_server_api,
                standard_config_payload,
                num_jobs=num_jobs,
                max_workers=10
            )
            # ... track memory/CPU trends ...
            time.sleep(interval_seconds)
        
        # Check for memory leak
        memory_increase = memory_trend[-1] - memory_trend[0]
        if memory_increase > 10:
            logger.warning(f"⚠️ Possible memory leak detected")
        
        assert statistics.mean(success_trend) >= SUCCESS_RATE_GOOD
```

**חסרונות:**
- ❌ אין Xray markers
- ❌ מסומן כ-skip (לא רץ אוטומטית)
- ❌ מטרה דומה לטסט הראשון (sustained load)
- ❌ לא מבצע cleanup אוטומטי של jobs
- ⚠️ בודק memory leaks אבל יש טסטים אחרים שעושים את זה טוב יותר

---

## 🔄 השוואה בין הטסטים

| מאפיין | `test_api_sustained_load_1_hour` | `test_sustained_load_1_hour` |
|--------|----------------------------------|------------------------------|
| **Xray Integration** | ✅ PZ-14801, PZ-14800 | ❌ אין |
| **מטרה** | API sustained load | Memory leak detection |
| **גישה** | Sequential API requests | Batch concurrent jobs |
| **משך זמן** | 5 דקות (CI) / שעה (manual) | שעה מלאה |
| **Request Pattern** | כל 10 שניות | כל 60 שניות (10 jobs) |
| **בודק** | Success rate, response times | Success rate, CPU, memory |
| **Cleanup** | ✅ אוטומטי | ❌ לא |
| **CI Integration** | ✅ רץ ב-CI (5 דקות) | ❌ Skipped |
| **Manual Run** | ✅ שעה מלאה | ✅ שעה מלאה |
| **סטטוס** | ✅ פעיל | ⚠️ Skipped |

---

## 🎯 האם הם דופליקציות?

### ❌ **לא בדיוק דופליקציות - אבל יש חפיפה**

**הבדלים עיקריים:**
1. **מטרה שונה:**
   - `test_api_sustained_load_1_hour`: בודק API performance
   - `test_sustained_load_1_hour`: בודק memory leaks

2. **גישה שונה:**
   - `test_api_sustained_load_1_hour`: Sequential requests (כל 10 שניות)
   - `test_sustained_load_1_hour`: Batch concurrent jobs (10 jobs כל 60 שניות)

3. **בודק דברים שונים:**
   - `test_api_sustained_load_1_hour`: Response times, success rate
   - `test_sustained_load_1_hour`: Memory trends, CPU trends

**אבל:**
- ✅ שניהם בודקים sustained load
- ✅ שניהם רצים במשך שעה
- ✅ שניהם בודקים success rate
- ⚠️ יש חפיפה במטרה הכללית

---

## ✅ המלצה סופית

### 🗑️ **למחוק את `test_sustained_load_1_hour`**

**סיבות:**
1. ❌ **אין Xray markers** - לא מקושר ל-test case ב-Jira
2. ⚠️ **מסומן כ-skip** - לא רץ אוטומטית ב-CI
3. ⚠️ **מטרה דומה** - יש טסט אחר שעושה את זה טוב יותר (`test_api_sustained_load_1_hour`)
4. ⚠️ **לא מבצע cleanup** - עלול להשאיר jobs פעילים
5. ⚠️ **Memory leak detection** - יש טסטים אחרים שעושים את זה טוב יותר

**אם צריך לבדוק memory leaks:**
- יש טסטים אחרים ב-`test_job_capacity_limits.py` שעושים את זה
- אפשר להוסיף memory leak checks לטסט הקיים (`test_api_sustained_load_1_hour`)

---

## 📝 פעולות מומלצות

### 1. למחוק את `test_sustained_load_1_hour`
```python
# למחוק מ-be_focus_server_tests/load/test_job_capacity_limits.py
# שורות 726-805
```

### 2. לשמור את `test_api_sustained_load_1_hour`
```python
# לשמור ב-be_focus_server_tests/integration/load/test_sustained_load.py
# זה הטסט המקושר ל-Xray (PZ-14801, PZ-14800)
```

### 3. אופציונלי: להוסיף memory leak checks לטסט הקיים
אם רוצים לבדוק memory leaks, אפשר להוסיף את זה ל-`test_api_sustained_load_1_hour`:
```python
# Add memory monitoring to test_api_sustained_load_1_hour
import psutil
process = psutil.Process()
memory_start = process.memory_info().rss / 1024 / 1024  # MB
# ... after test ...
memory_end = process.memory_info().rss / 1024 / 1024  # MB
memory_increase = memory_end - memory_start
if memory_increase > 100:  # 100 MB threshold
    logger.warning(f"⚠️ Possible memory leak: +{memory_increase:.1f} MB")
```

---

## 📊 סיכום

| טסט | Xray | סטטוס | המלצה |
|-----|------|-------|-------|
| `test_api_sustained_load_1_hour` | ✅ PZ-14801, PZ-14800 | ✅ פעיל | ✅ **לשמור** |
| `test_sustained_load_1_hour` | ❌ אין | ⚠️ Skipped | ❌ **למחוק** |

**סה"כ:** למחוק את `test_sustained_load_1_hour` מ-`be_focus_server_tests/load/test_job_capacity_limits.py`

---

**תאריך:** 2025-01-27  
**גרסה:** 1.0

