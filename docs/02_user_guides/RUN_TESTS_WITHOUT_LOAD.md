# 🚀 הרצת כל הטסטים ללא עומס

**תאריך:** 2025-11-09  
**מטרה:** הרצת כל הטסטים חוץ מהטסטים שיוצרים עומס על המערכת או יצירה לא פרופורציונלית של gRPC jobs

---

## 📋 פקודה להרצת כל הטסטים ללא עומס

### פקודה בסיסית:

```bash
pytest -m "not load and not stress and not grpc" -v
```

### פקודה מפורטת (עם דיווח):

```bash
pytest -m "not load and not stress and not grpc" -v --tb=short -s
```

### פקודה עם HTML report:

```bash
pytest -m "not load and not stress and not grpc" -v --tb=short -s --html=reports/test_report_no_load.html --self-contained-html
```

---

## 🎯 מה הפקודה מדלגת עליו:

### 1. **Load Tests** (`@pytest.mark.load`)
- כל הטסטים בתיקיית `tests/load/`
- כולל:
  - `test_job_capacity_limits.py` - יוצר 200+ jobs
  - `test_peak_load.py` - יוצר 600+ requests
  - `test_sustained_load.py` - יוצר 30+ jobs
  - `test_concurrent_load.py` - יוצר 20 concurrent jobs
  - `test_load_profiles.py` - יוצר multiple load profiles
  - `test_recovery_and_exhaustion.py` - יוצר extreme load

### 2. **Stress Tests** (`@pytest.mark.stress`)
- כל הטסטים בתיקיית `tests/stress/`
- כולל:
  - `test_extreme_configurations.py` - יוצר configurations כבדות
  - `test_job_capacity_limits.py::TestStressLoad` - יוצר 100 concurrent jobs
  - `test_job_capacity_limits.py::TestHeavyConfigurationStress` - יוצר heavy config jobs

### 3. **gRPC Tests** (`@pytest.mark.grpc`)
- כל הטסטים שמשתמשים ב-gRPC streams
- כולל:
  - `test_configure_metadata_grpc_flow.py` - יוצר gRPC jobs

---

## ✅ מה הפקודה מריצה:

### כל הטסטים הבאים **יורצו**:

1. ✅ **Integration Tests** - כל הטסטים של integration
2. ✅ **API Tests** - כל הטסטים של API endpoints
3. ✅ **Performance Tests** (חלק) - רק הטסטים שלא יוצרים concurrent jobs:
   - `test_performance_high_priority.py::TestAPILatencyP95` - מדידת latency (100 requests)
   - `test_network_latency.py` - מדידת network latency
   - `test_response_time.py` - מדידת response time
   - `test_database_performance.py` - מדידת database performance
   - `test_latency_requirements.py` - בדיקת latency requirements
4. ✅ **Security Tests** - כל הטסטים של security
5. ✅ **Error Handling Tests** - כל הטסטים של error handling
6. ✅ **Data Quality Tests** - כל הטסטים של data quality
7. ✅ **Infrastructure Tests** - כל הטסטים של infrastructure
8. ✅ **Unit Tests** - כל הטסטים של unit tests
9. ✅ **E2E Tests** - כל הטסטים של end-to-end (חוץ מ-gRPC)

---

## ⚠️ הערות חשובות:

### Performance Tests שיורצו:

**✅ יורצו:**
- `test_performance_high_priority.py::TestAPILatencyP95` - מדידת latency (100 requests sequential)
- `test_network_latency.py` - מדידת network latency
- `test_response_time.py` - מדידת response time
- `test_database_performance.py` - מדידת database performance
- `test_latency_requirements.py` - בדיקת latency requirements

**❌ לא יורצו:**
- `test_performance_high_priority.py::TestConcurrentTaskLimit` - יוצר 20 concurrent tasks
- `test_concurrent_performance.py` - יוצר 10 concurrent requests
- `test_resource_usage.py` - יוצר load למדידת resource usage

**אם אתה רוצה להדיר גם את הטסטים האלה, השתמש בפקודה:**

```bash
pytest -m "not load and not stress and not grpc and not (performance and concurrent)" -v
```

או להדיר טסטים ספציפיים:

```bash
pytest -m "not load and not stress and not grpc" -v --ignore=tests/integration/performance/test_concurrent_performance.py --ignore=tests/integration/performance/test_resource_usage.py
```

---

## 📊 דוגמאות שימוש:

### דוגמה 1: הרצה בסיסית

```bash
pytest -m "not load and not stress and not grpc" -v
```

### דוגמה 2: הרצה עם HTML report

```bash
pytest -m "not load and not stress and not grpc" -v --html=reports/test_report_no_load.html --self-contained-html
```

### דוגמה 3: הרצה של תיקייה ספציפית

```bash
pytest tests/integration/api -m "not load and not stress and not grpc" -v
```

### דוגמה 4: הרצה עם coverage

```bash
pytest -m "not load and not stress and not grpc" -v --cov=src --cov-report=html
```

### דוגמה 5: הרצה עם parallel execution

```bash
pytest -m "not load and not stress and not grpc" -v -n auto
```

---

## 🔍 איך לבדוק מה יוריץ:

### בדיקה 1: רשימת הטסטים שיורצו

```bash
pytest -m "not load and not stress and not grpc" --collect-only
```

### בדיקה 2: ספירת הטסטים

```bash
pytest -m "not load and not stress and not grpc" --collect-only -q | grep "test session starts" -A 1000 | grep "test" | wc -l
```

### בדיקה 3: רשימת הטסטים שלא יורצו

```bash
pytest -m "load or stress or grpc" --collect-only
```

---

## 📝 סיכום:

**פקודה מומלצת:**

```bash
pytest -m "not load and not stress and not grpc" -v --tb=short -s --html=reports/test_report_no_load.html --self-contained-html
```

**מה זה עושה:**
- ✅ מריץ את כל הטסטים חוץ מ-load, stress, ו-gRPC
- ✅ מציג output מפורט (`-v`)
- ✅ מציג short traceback (`--tb=short`)
- ✅ מציג print statements (`-s`)
- ✅ יוצר HTML report (`--html=...`)

---

**עודכן לאחרונה:** 2025-11-09  
**גרסה:** 1.0

