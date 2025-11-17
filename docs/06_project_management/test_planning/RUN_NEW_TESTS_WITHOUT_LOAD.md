# הרצת הטסטים החדשים ללא Load Tests

**תאריך:** 2025-11-09  
**סיבה:** Load Tests יוצרים יותר מדי jobs (700+ jobs)

---

## 🎯 פקודה להרצה ללא Load Tests

### פקודה בסיסית (33 טסטים - ללא Load Tests):

```bash
pytest tests/integration/security/ tests/integration/error_handling/ tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py tests/integration/data_quality/ -v --tb=short --skip-health-check -m "not load"
```

### פקודה עם דוח HTML:

```bash
pytest tests/integration/security/ tests/integration/error_handling/ tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py tests/integration/data_quality/ -v --tb=short --skip-health-check -m "not load" --html=reports/new_tests_no_load_report.html --self-contained-html
```

---

## 📊 טסטים שיורצו:

- ✅ **Security Tests:** 10 טסטים
- ✅ **Error Handling Tests:** 8 טסטים
- ✅ **Performance Tests:** 10 טסטים
- ✅ **Data Quality Tests:** 5 טסטים
- ❌ **Load Tests:** 8 טסטים (דילוג)

**סה"כ: 33 טסטים (במקום 41)**

---

## ⚠️ הערות:

1. **Load Tests יוצרים הרבה jobs:**
   - Peak Load: 600 requests
   - Sustained Load: 30+ jobs
   - Concurrent Load: 20 jobs
   - **סה"כ: ~700+ jobs**

2. **להרצת Load Tests בנפרד:**
   ```bash
   pytest tests/integration/load/ -v --tb=short --skip-health-check -m load
   ```

3. **לאחר תיקון ה-cleanup:**
   - ניתן להריץ את כל הטסטים יחד
   - Cleanup אוטומטי ינקה את כל ה-jobs

---

## 🔧 פתרון זמני:

להרצת הטסטים החדשים ללא Load Tests כדי למנוע יצירת יותר מדי jobs.

**לאחר תיקון ה-cleanup, ניתן להריץ את כל הטסטים יחד.**

