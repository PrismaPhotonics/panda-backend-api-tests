# Gradual Historic Load Testing

## 📋 סקירה כללית

טסטי העומס של Historic Playback עם אינטרוולים **זהים** לטסטי ה-Live:

- **Initial Jobs**: 5 jobs
- **Step Increment**: +5 jobs כל step
- **Step Interval**: 10 שניות בין steps
- **Max Jobs**: 100 jobs

זה מאפשר השוואה ישירה בין ביצועי Live ו-Historic תחת עומס דומה.

## 🎯 מטרת הטסטים

טסטי העומס הגרדואליים בודקים את יכולת המערכת להתמודד עם עומס הולך וגדל:

1. **Step-by-Step Load Increase**: העמסה הדרגתית במקום burst
2. **Health Monitoring**: בדיקת בריאות המערכת בכל step
3. **Breaking Point Detection**: זיהוי נקודת השבירה של המערכת
4. **Cleanup Verification**: וידוא ניקוי תקין אחרי הטסט

## 📊 מבנה הטסטים

### Gradual Load Pattern

```
Step 1:  5 jobs → Health Check → Wait 10s
Step 2: 10 jobs → Health Check → Wait 10s
Step 3: 15 jobs → Health Check → Wait 10s
...
Step 20: 100 jobs → Final Health Check → Cleanup
```

### Health Status

בכל step נבדקים:
- **API Health**: האם ה-API מגיב
- **Job Connectivity**: כמה jobs מחוברים בהצלחה
- **Success Rate**: אחוז ה-jobs שנוצרו בהצלחה

התוצאות:
- ✅ **HEALTHY**: מעל 50% jobs מחוברים
- ⚠️ **DEGRADED**: 30-50% jobs מחוברים
- ❌ **UNHEALTHY**: פחות מ-30% jobs מחוברים

## 🔧 שימוש ב-MongoDB base_paths

הטסטים משתמשים ישירות בקולקציית `base_paths` ב-MongoDB כדי למצוא recordings:

1. **Query base_paths**: מציאת GUID של הקולקציה
2. **Load Recordings**: טעינת recordings מהקולקציה על שם GUID
3. **Round-Robin Selection**: כל job מקבל recording אחר (הפצת עומס)
4. **Time Range**: שימוש ב-`start_time` ו-`end_time` מהמסד

### תצורת MongoDB

```python
MIN_DURATION_SECONDS: float = 5.0      # מינימום משך recording
MAX_DURATION_SECONDS: float = 10.0     # מקסימום משך recording
WEEKS_BACK: int = 2                     # כמה שבועות אחורה לחפש
MAX_RECORDINGS_TO_LOAD: int = 200       # מקסימום recordings לטעון
```

## 🚀 הרצת הטסטים

### טסט בסיסי (5 → 100 jobs)

```bash
pytest be_focus_server_tests/load/test_gradual_historic_load.py::TestGradualHistoricJobLoad::test_gradual_load_to_100_jobs -v -s
```

### טסט מהיר (2 → 10 jobs) - ל-CI

```bash
pytest be_focus_server_tests/load/test_gradual_historic_load.py::TestGradualHistoricJobLoad::test_quick_gradual_load -v
```

### טסט עם תצורה מותאמת אישית

```bash
pytest be_focus_server_tests/load/test_gradual_historic_load.py::TestGradualHistoricLoadCustomConfig::test_high_concurrency_gradual -v -s
```

## 📈 תוצאות הטסט

הטסט מחזיר `GradualHistoricLoadTestResult` עם:

- **Job Statistics**: כמה jobs נוצרו, נכשלו, נוקו
- **Health Metrics**: כמה steps היו healthy/degraded/unhealthy
- **Performance Metrics**: זמני יצירה ממוצעים, זמני חיבור gRPC
- **Step-by-Step Metrics**: מפורט לכל step

### דוגמה ללוג

```
================================================================================
📼 GRADUAL HISTORIC JOB LOAD TEST - RESULTS
================================================================================

📊 Test Summary:
   • Test Name: Gradual Load to 100 Jobs
   • Duration: 1250.50 seconds
   • Max Jobs Reached: 100

📦 Job Statistics:
   • Total Created: 95
   • Total Failed: 5
   • Total Cleaned: 95

🏥 Health Status:
   • Final Status: healthy
   • Healthy Steps: 18
   • Degraded Steps: 2
   • Unhealthy Steps: 0

⏱️  Performance:
   • Avg Creation Time: 2500ms
   • Avg gRPC Connect Time: 3000ms

📈 Step-by-Step Progress:
   Step  1:  5 jobs | 100% success | ✅ healthy
   Step  2: 10 jobs | 100% success | ✅ healthy
   Step  3: 15 jobs | 100% success | ✅ healthy
   ...
   Step 20: 100 jobs | 95% success | ✅ healthy
================================================================================
```

## 🔄 השוואה ל-Live Tests

| פרמטר | Live | Historic |
|--------|------|----------|
| Initial Jobs | 5 | 5 |
| Step Increment | 5 | 5 |
| Step Interval | 10s | 10s |
| Max Jobs | 100 | 100 |
| **Source** | Live Stream | MongoDB Recordings |

**האינטרוולים זהים** - זה מאפשר השוואה ישירה בין ביצועי Live ו-Historic.

## ⚙️ תצורה מותאמת אישית

ניתן להתאים את הפרמטרים:

```python
tester = create_gradual_historic_load_tester(
    config_manager=config_manager,
    initial_jobs=10,      # התחלה עם 10 jobs
    step_increment=10,    # הוספת 10 בכל step
    max_jobs=100,         # מקסימום 100 jobs
    step_interval=8       # 8 שניות בין steps
)

result = tester.run_gradual_load_test(
    test_name="Custom Gradual Load"
)
```

## 📝 Markers

- `@pytest.mark.gradual_load` - Gradual load tests
- `@pytest.mark.load` - Load tests
- `@pytest.mark.historic` - Historic job tests
- `@pytest.mark.slow` - Slow tests (may take 20+ minutes)

## 🎯 Assertions

הטסטים בודקים:

1. **Cleanup Success**: לפחות 90% מה-jobs נוקו
2. **Health Rate**: לפחות 70% מה-steps היו healthy
3. **Max Load**: הגעה לפחות ל-80 concurrent jobs
4. **Step Count**: לפחות 5 steps הושלמו

## 🔍 Troubleshooting

### No Recordings Found

אם הטסט מדלג כי אין recordings:
- בדוק שיש recordings בקולקציית `base_paths`
- בדוק את ה-`WEEKS_BACK` (אולי צריך להגדיל)
- בדוק את ה-`MIN_DURATION_SECONDS` (אולי צריך להקטין)

### High Failure Rate

אם יש הרבה failures:
- בדוק את זמינות ה-MongoDB
- בדוק את זמינות ה-Focus Server
- בדוק את ה-gRPC connectivity
- בדוק את ה-MaxWindows limit

### Slow Execution

אם הטסט איטי מדי:
- השתמש ב-`quick_gradual_historic_tester` (2→10 jobs)
- הגדל את ה-`STEP_INTERVAL_SECONDS`
- הקטן את ה-`MAX_JOBS`

## 📚 קבצים קשורים

- `be_focus_server_tests/load/test_gradual_historic_load.py` - הטסטים
- `be_focus_server_tests/load/test_gradual_live_load.py` - טסטי Live (להשוואה)
- `be_focus_server_tests/load/job_load_tester.py` - Base tester עם MongoDB support
- `docs/04_testing/load_tests/HISTORIC_LOAD_TESTING_WITH_BASE_PATHS.md` - תיעוד MongoDB

