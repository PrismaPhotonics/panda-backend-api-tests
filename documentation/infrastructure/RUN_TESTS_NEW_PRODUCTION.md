# 🧪 Running Tests on New Production Environment

**Date:** October 16, 2025  
**Environment:** New Production (10.10.100.100)

---

## ✅ YES, Configuration Changes Are Required!

The tests need to know about the new environment. Here's how to configure everything:

---

## 🚀 Quick Start (3 Steps)

### Step 1: Set Environment Variables

```powershell
# Run the setup script (dot-source it)
. .\set_production_env.ps1
```

This sets all required environment variables:
- ✅ Focus Server: `https://10.10.100.100/focus-server/`
- ✅ MongoDB: `mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma`
- ✅ SSL verification: disabled (self-signed certs)

### Step 2: Verify Connection

```powershell
# Test MongoDB
py -c "from pymongo import MongoClient; MongoClient('mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma').admin.command('ping'); print('✅ MongoDB OK')"

# Test Focus Server
Test-NetConnection -ComputerName 10.10.100.100 -Port 443
```

### Step 3: Run Tests

```powershell
# Run all tests
pytest tests/ -v

# Or specific categories
pytest tests/unit/ -v
pytest tests/integration/ -v
```

---

## 📝 Detailed Configuration

### Environment Variables Set by Script

| Variable | Value | Purpose |
|----------|-------|---------|
| `FOCUS_ENV` | `new_production` | Environment selector |
| `FOCUS_SERVER_HOST` | `10.10.100.100` | Backend host |
| `FOCUS_BASE_URL` | `https://10.10.100.100/focus-server/` | Full backend URL |
| `FOCUS_API_PREFIX` | `/focus-server` | API path prefix |
| `FOCUS_SITE_ID` | `prisma-210-1000` | Site identifier |
| `MONGODB_URI` | `mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma` | Full connection string |
| `MONGODB_HOST` | `10.10.100.108` | MongoDB host |
| `MONGODB_DATABASE` | `prisma` | Database name |
| `VERIFY_SSL` | `false` | Disable SSL verification |

---

## 🧪 Running Different Test Categories

### 1. Unit Tests (No configuration needed)

```powershell
pytest tests/unit/ -v
```

**Tests:**
- Configuration loading
- Model validation
- Basic functionality
- Validators

---

### 2. MongoDB Tests

**Set environment first:**
```powershell
. .\set_production_env.ps1
```

**Run comprehensive data quality tests:**
```powershell
pytest tests/integration/infrastructure/test_mongodb_data_quality.py -v --html=reports/mongodb_quality.html
```

**Run specific MongoDB tests:**
```powershell
# Soft delete validation
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::test_soft_delete_validation -v

# Historical vs Live data
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::test_historical_vs_live_data -v

# Data quality checks
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::test_data_quality_checks -v
```

**Expected Output:**
```
✅ MongoDB connection: mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma
✅ Database: prisma
✅ Collections found: 3
```

---

### 3. API Contract Tests

**Set environment:**
```powershell
. .\set_production_env.ps1
```

**Run API tests:**
```powershell
cd focus_server_api_load_tests\focus_api_tests
pytest test_api_contract.py -v
```

**Tests include:**
- ✅ GET /channels
- ✅ GET /live_metadata
- ✅ POST /configure
- ✅ GET /metadata/{job_id}
- ✅ POST /recordings_in_time_range
- ✅ GET /get_recordings_timeline

**Expected:**
- Most tests should pass
- Some may skip if endpoints not available
- 422 validation tests verify error handling

---

### 4. Integration API Tests

**Set environment:**
```powershell
. .\set_production_env.ps1
```

**Run integration tests:**
```powershell
pytest tests/integration/api/ -v
```

**Tests:**
- Single channel view mapping
- Spectrogram pipeline
- Live monitoring flow
- Historic playback flow
- Dynamic ROI adjustment

---

### 5. Load Tests (Locust)

**Set environment:**
```powershell
. .\set_production_env.ps1
```

**Quick smoke test (10 users, 5 minutes):**
```powershell
cd focus_server_api_load_tests\load_tests

locust -f locust_focus_server.py --headless `
  -u 10 -r 2 -t 5m `
  --host https://10.10.100.100 `
  --csv results/smoke --html results/smoke.html
```

**Ramp profile (20 users, 3-minute ramp):**
```powershell
$env:LOAD_SHAPE = "ramp"
$env:RAMP_USERS = 20
$env:RAMP_SPAWN_RATE = 2
$env:RAMP_STAGE_SECS = 60

locust -f locust_focus_server.py --headless --run-time 3m `
  --host https://10.10.100.100 `
  --csv results/ramp --html results/ramp.html
```

**Spike test (5→50→5 users):**
```powershell
$env:LOAD_SHAPE = "spike"
$env:SPIKE_BASE = 5
$env:SPIKE_PEAK = 50
$env:SPIKE_RISE_SECS = 10
$env:SPIKE_HOLD_SECS = 20

locust -f locust_focus_server.py --headless --run-time 1m `
  --host https://10.10.100.100 `
  --csv results/spike --html results/spike.html
```

---

## 📊 Alternative: Manual Environment Setup

If you prefer not to use the script, set variables manually:

```powershell
# MongoDB
$env:MONGODB_URI = "mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma"
$env:MONGODB_HOST = "10.10.100.108"
$env:MONGODB_DATABASE = "prisma"

# Focus Server
$env:FOCUS_BASE_URL = "https://10.10.100.100/focus-server/"
$env:FOCUS_API_PREFIX = "/focus-server"
$env:VERIFY_SSL = "false"

# Run tests
pytest tests/integration/ -v
```

---

## 🔍 Verify Configuration

### Check Environment Variables

```powershell
Write-Host "Focus Server: $env:FOCUS_BASE_URL"
Write-Host "MongoDB: $env:MONGODB_URI"
Write-Host "SSL Verify: $env:VERIFY_SSL"
```

**Expected:**
```
Focus Server: https://10.10.100.100/focus-server/
MongoDB: mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma
SSL Verify: false
```

### Test Connectivity

```powershell
# Backend
Test-NetConnection 10.10.100.100 -Port 443

# MongoDB
Test-NetConnection 10.10.100.108 -Port 27017

# MongoDB connection
py -c "from pymongo import MongoClient; MongoClient('mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma').admin.command('ping'); print('OK')"
```

---

## 🎯 Test Execution Examples

### Complete Test Suite

```powershell
# Set environment
. .\set_production_env.ps1

# Run all tests with HTML report
pytest tests/ -v --html=reports/all_tests_report.html --self-contained-html

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html
```

### MongoDB Data Quality (Comprehensive)

```powershell
. .\set_production_env.ps1

pytest tests/integration/infrastructure/test_mongodb_data_quality.py `
  -v `
  --html=reports/mongodb_quality_report.html `
  --self-contained-html `
  -m data_quality
```

### API Tests Only

```powershell
. .\set_production_env.ps1

pytest -v -m api --html=reports/api_tests.html
```

### Load Test with Reports

```powershell
. .\set_production_env.ps1

cd focus_server_api_load_tests\load_tests

locust -f locust_focus_server.py --headless `
  -u 20 -r 5 -t 10m `
  --host https://10.10.100.100 `
  --csv results/load_test `
  --html results/load_test_report.html
```

---

## 📂 Test Reports Location

After running tests, reports will be in:

```
C:\Projects\focus_server_automation\
├── reports\
│   ├── mongodb_quality_report.html
│   ├── api_tests.html
│   └── all_tests_report.html
│
└── focus_server_api_load_tests\load_tests\results\
    ├── load_test_report.html
    ├── load_test_stats.csv
    ├── load_test_failures.csv
    └── jobs_created.json
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: Tests fail with "Connection Refused"

**Problem:** Environment variables not set or wrong values

**Solution:**
```powershell
# Re-run the setup script
. .\set_production_env.ps1

# Verify
Write-Host $env:FOCUS_BASE_URL
Write-Host $env:MONGODB_URI
```

### Issue 2: MongoDB Authentication Failed

**Problem:** Wrong auth source or credentials

**Solution:**
```powershell
# Ensure auth source is "prisma" (not "admin")
$env:MONGODB_URI = "mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma"
```

### Issue 3: SSL Certificate Errors

**Problem:** SSL verification enabled

**Solution:**
```powershell
$env:VERIFY_SSL = "false"
```

### Issue 4: API Tests Return 404

**Problem:** Wrong API prefix

**Solution:**
```powershell
$env:FOCUS_API_PREFIX = "/focus-server"
# Not "/prisma/api" or other paths
```

---

## 📊 CI/CD Integration

### GitHub Actions / GitLab CI

```yaml
test_new_production:
  script:
    # Set environment
    - export MONGODB_URI="mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma"
    - export FOCUS_BASE_URL="https://10.10.100.100/focus-server/"
    - export VERIFY_SSL="false"
    
    # Run tests
    - pytest tests/integration/ -v --junitxml=junit-integration.xml
    
    # Run load tests
    - cd focus_server_api_load_tests/load_tests
    - locust -f locust_focus_server.py --headless -u 10 -r 2 -t 5m 
        --host https://10.10.100.100 
        --csv results/ci_load --html results/ci_load.html
  
  artifacts:
    paths:
      - reports/
      - focus_server_api_load_tests/load_tests/results/
    when: always
```

---

## ✅ Quick Checklist

Before running tests, verify:

- [ ] Environment script executed: `. .\set_production_env.ps1`
- [ ] MongoDB connection works: Test with quick Python command
- [ ] Focus Server accessible: `Test-NetConnection 10.10.100.100 -Port 443`
- [ ] `VERIFY_SSL` is `false`
- [ ] Current directory is project root: `C:\Projects\focus_server_automation\`

---

## 📚 Related Documentation

- `NEW_ENVIRONMENT_MASTER_DOCUMENT.md` - Complete environment documentation
- `TEST_SUITE_INVENTORY.md` - All test files and locations
- `config/NEW_PRODUCTION_ENV.yaml` - Environment configuration
- `config/NEW_PRODUCTION_SUMMARY.md` - Quick reference

---

## 🎯 Summary

**Yes, configuration IS required:**

1. ✅ **Run:** `. .\set_production_env.ps1` (sets all environment variables)
2. ✅ **Verify:** Test MongoDB and Focus Server connectivity
3. ✅ **Execute:** Run tests with `pytest` or `locust`

**Without configuration:**
- Tests will try to connect to old environment (10.10.10.150 or localhost)
- MongoDB connection will fail
- API tests will fail with 404/timeout

**With configuration:**
- ✅ Tests connect to new production: 10.10.100.100
- ✅ MongoDB works: 10.10.100.108
- ✅ All endpoints configured correctly

---

**Quick Command:**
```powershell
. .\set_production_env.ps1 && pytest tests/integration/ -v
```

**That's it!** 🚀

