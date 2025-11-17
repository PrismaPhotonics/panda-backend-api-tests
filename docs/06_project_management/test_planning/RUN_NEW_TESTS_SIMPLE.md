# פקודה להרצת הטסטים החדשים בלבד

## פקודה בסיסית (41 טסטים)

```bash
pytest tests/integration/security/ tests/integration/error_handling/ tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py tests/integration/load/ tests/integration/data_quality/ -v --tb=short --skip-health-check
```

## פקודה עם דוח HTML

```bash
pytest tests/integration/security/ tests/integration/error_handling/ tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py tests/integration/load/ tests/integration/data_quality/ -v --tb=short --skip-health-check --html=reports/new_tests_report.html --self-contained-html
```

## פקודה עם עצירה אחרי 3 כשלונות

```bash
pytest tests/integration/security/ tests/integration/error_handling/ tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py tests/integration/load/ tests/integration/data_quality/ -v --tb=short --skip-health-check --maxfail=3
```

## הרצה לפי קטגוריה

### Security Tests (10 טסטים)
```bash
pytest tests/integration/security/ -v --tb=short --skip-health-check
```

### Error Handling Tests (8 טסטים)
```bash
pytest tests/integration/error_handling/ -v --tb=short --skip-health-check
```

### Performance Tests (10 טסטים)
```bash
pytest tests/integration/performance/test_response_time.py tests/integration/performance/test_concurrent_performance.py tests/integration/performance/test_resource_usage.py tests/integration/performance/test_database_performance.py tests/integration/performance/test_network_latency.py -v --tb=short --skip-health-check
```

### Load Tests (8 טסטים)
```bash
pytest tests/integration/load/ -v --tb=short --skip-health-check
```

### Data Quality Tests (5 טסטים)
```bash
pytest tests/integration/data_quality/ -v --tb=short --skip-health-check
```

## הרצה עם סקריפט PowerShell

```powershell
.\run_new_tests.ps1
```

או עם ארגומנטים:
```powershell
.\run_new_tests.ps1 --html --junit
```

